import argparse, json, os, re, datetime
from pathlib import Path

HOME = Path.home()
MASTER = Path(os.environ.get("MASTER", HOME/"refresh/organized/arch/geminicli/gpt5thinkmd"))
INDEX  = Path(os.environ.get("INDEX",  HOME/"refresh/index"))
WSROOT = Path(os.environ.get("WSROOT", HOME/"refresh/workspaces"))

def slug(s): return re.sub(r'[^a-zA-Z0-9]+','-',s).strip('-').lower() or "project"
def now():  return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def write(p:Path, s:str):
    p.parent.mkdir(parents=True, exist_ok=True)
    old = p.read_text() if p.exists() else None
    if old == s: return False
    p.write_text(s); return True

def sniff_stack(up:Path):
    tags=set()
    for k,v in {"package.json":"js","pnpm-lock.yaml":"pnpm","yarn.lock":"yarn","requirements.txt":"python",
                "pyproject.toml":"python","CMakeLists.txt":"cpp","go.mod":"go","Cargo.toml":"rust"}.items():
        if (up/k).exists(): tags.add(v)
    ext_map={".py":"python",".ts":"ts",".js":"js",".cpp":"cpp",".cxx":"cpp",".cc":"cpp",".go":"go",".rs":"rust"}
    try:
        for p in up.rglob("*"):
            if p.is_file(): tags.add(ext_map.get(p.suffix,""))
    except: pass
    return sorted(t for t in tags if t)

def ensure_ws(area, pid):
    w = WSROOT/area/pid
    (w/"ops").mkdir(parents=True, exist_ok=True)
    (w/"docs").mkdir(parents=True, exist_ok=True)
    (w/"src").mkdir(parents=True, exist_ok=True)
    return w

def meta_update(w:Path, **kv):
    mp=w/"ops"/"meta.json"; meta=json.loads(mp.read_text()) if mp.exists() else {}
    meta.update({k:v for k,v in kv.items() if v is not None})
    write(mp, json.dumps(meta, indent=2)); return meta

def copy_upstream_readme(up:Path, w:Path):
    for cand in ("README.md","README","Readme.md"):
        if (up/cand).exists():
            write(w/"docs"/"README.upstream.md", (up/cand).read_text(errors="ignore")); return True
    return False

def evaluate(w:Path):
    up=w/"src"/"upstream"
    meta=meta_update(w, id=w.name, area=w.parent.name, linked_upstream=up.exists(), stack=sniff_stack(up))
    txt=(w/"docs"/"README.upstream.md").read_text(errors="ignore") if (w/"docs"/"README.upstream.md").exists() else ""
    if not txt: copy_upstream_readme(up,w); txt=(w/"docs"/"README.upstream.md").read_text(errors="ignore") if (w/"docs"/"README.upstream.md").exists() else ""
    write(w/"PROJECT.md", f"# {w.name}\n\nArea: `{w.parent.name}`\nStatus: planned\n")
    write(w/"CONTEXT.md", f"# Context\n\n{txt or 'No upstream README detected.'}\n")
    if not (w/"TASKS.md").exists(): write(w/"TASKS.md","- [ ] Audit upstream and set up toolchain\n- [ ] Define first milestone\n")
    dirs=[]
    if up.exists():
        try: dirs=sorted({p.relative_to(up).parts[0] for p in up.rglob("*") if p.is_dir()})
        except: pass
    write(w/"STRUCTURE.yml","workspace:\n  dirs: [docs, src, assets, data, ops]\nupstream_top:\n  dirs: ["+", ".join(dirs)+"]\n")
    return meta

def render_status():
    rows=[]
    for m in WSROOT.rglob("ops/meta.json"):
        try:
            meta=json.loads(m.read_text()); w=m.parent.parent
            rows.append([meta.get("id","?"), meta.get("area","?"), "|".join(meta.get("stack",[])), str(w)])
        except: pass
    INDEX.mkdir(parents=True, exist_ok=True)
    (INDEX/"workspaces.tsv").write_text("id\tarea\tstack\tworkspace_path\n"+"\n".join("\t".join(r) for r in sorted(rows)))
    return len(rows)

def brainflash_add(text):
    f=INDEX/"brainflash.md"
    base="# Brainflash\n\n"
    write(f, (f.read_text() if f.exists() else base) + f"- {now()} — {text}\n")
    return f

def cmd_new(a):
    pid=a.id or slug(a.name)
    w=ensure_ws(a.area,pid); meta_update(w,id=pid,area=a.area,stack=[],linked_upstream=False)
    write(w/"PROJECT.md", f"# {pid}\n\nArea: `{a.area}`\nStatus: planned\n")
    write(w/"CONTEXT.md","# Context\n\n")
    write(w/"TASKS.md","- [ ] Audit upstream and set up toolchain\n- [ ] Define first milestone\n")
    print(f"[ok] created {w}")

def cmd_eval(a):
    w=WSROOT/a.area/a.id; meta=evaluate(w); n=render_status()
    print(f"[ok] evaluated {w} stack={','.join(meta.get('stack',[]))} workspaces={n}")

def cmd_status(_):
    n=render_status(); print(f"[ok] status updated; workspaces={n}\n{INDEX/'workspaces.tsv'}")

def cmd_brainflash(a):
    f=brainflash_add(a.text); print(f"[ok] noted -> {f}")

def cmd_list(_):
    for m in WSROOT.rglob("ops/meta.json"):
        try:
            meta=json.loads(m.read_text()); w=m.parent.parent
            print(f"{meta.get('id','?'):>28}  ::  {meta.get('area','?'):>12}  ::  {','.join(meta.get('stack',[]))}")
        except: pass

def main():
    ap=argparse.ArgumentParser(prog="ws")
    sub=ap.add_subparsers(dest="cmd", required=True)
    p=sub.add_parser("new"); p.add_argument("name"); p.add_argument("--area", default="development"); p.add_argument("--id"); p.set_defaults(func=cmd_new)
    p=sub.add_parser("eval"); p.add_argument("area"); p.add_argument("id"); p.set_defaults(func=cmd_eval)
    p=sub.add_parser("status"); p.set_defaults(func=cmd_status)
    p=sub.add_parser("brainflash"); p.add_argument("text"); p.set_defaults(func=cmd_brainflash)
    p=sub.add_parser("list"); p.set_defaults(func=cmd_list)
    args=ap.parse_args(); args.func(args)

if __name__=="__main__": main()
