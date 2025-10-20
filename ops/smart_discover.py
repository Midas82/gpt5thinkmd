import os, json, re, hashlib, time, sys
from pathlib import Path

HOME = Path.home()
INDEX = HOME / "refresh" / "index"
PROPDIR = INDEX / "proposals"
PROPDIR.mkdir(parents=True, exist_ok=True)
OUT = PROPDIR / "smart_projects_proposed.json"
AUTO = PROPDIR / "smart_autoapproved.json"
IDS  = PROPDIR / "approved_ids_from_smart.txt"

ROOTS = [
  HOME,
  HOME/"Desktop", HOME/"Documents", HOME/"Downloads", HOME/"Projects",
  HOME/"refresh", HOME/"workspaces"
]
for base in (Path("/mnt"), Path("/media"), Path("/run/media")):
    if base.exists():
        ROOTS += [p for p in base.iterdir() if p.is_dir()]

# hard skips to kill mirrors and runtimes
BIND_PREFIX = (HOME/"refresh/organized/arch/geminicli/gpt5thinkmd/.gemini/workspace/bind").as_posix()
SKIP_PREFIXES = {
  BIND_PREFIX,
  (HOME/"refresh/workspaces").as_posix(),
  (HOME/".local/share/lutris/runtime").as_posix(),
  (HOME/".local/share/Steam/steamapps/compatdata").as_posix(),
  (HOME/".steam/steam/steamapps/compatdata").as_posix(),
  (HOME/".cache").as_posix(),
  (HOME/".var/app").as_posix(),
  (HOME/"needs_transferred_to_remote_backups_drive").as_posix()
}

IGNORE_DIRS = {
  ".git","node_modules","__pycache__",".mypy_cache",".pytest_cache",".cache",
  "venv",".venv","env",".idea",".vscode","dist","build","target",".next",
  "site-packages","vendor",".gradle"
}
IGNORE_SUBSTR = {".DS_Store","thumbs.db","/runtime/","/wine/","/prefixes/"}

MARKERS = {
  "package.json","pnpm-lock.yaml","yarn.lock","requirements.txt","pyproject.toml","Pipfile",
  "setup.py","Cargo.toml","go.mod","Makefile","pom.xml","build.gradle","CMakeLists.txt",
  "README.md","README","LICENSE",".git"
}
CODE_EXT = {".py",".js",".ts",".tsx",".jsx",".rs",".go",".java",".kt",".cpp",".c",".h",".rb",".php",".sh",".swift"}

def ignored_path(p: Path) -> bool:
    s = p.as_posix()
    if any(s.startswith(pref) for pref in SKIP_PREFIXES): return True
    if set(p.parts) & IGNORE_DIRS: return True
    sl = s.lower()
    return any(x in sl for x in (y.lower() for y in IGNORE_SUBSTR))

def guess_area(p: Path, have):
    s = p.as_posix().lower()
    if any(x in have for x in ["package.json","pyproject.toml","requirements.txt","go.mod","Cargo.toml","Makefile"]):
        return "development"
    if any(k in s for k in ("/3d","/cad","/print","/stl")): return "maker"
    if any(k in s for k in ("/music","/audio","/daw")): return "media"
    if any(k in s for k in ("/photo","/image")): return "photography"
    if "/documents/" in s: return "documents"
    return "unsorted"

def sample_lines(d: Path, limit=12):
    for name in ["README.md","README","readme.md","package.json","pyproject.toml","Cargo.toml","Makefile"]:
        p = d / name
        if p.exists() and p.is_file():
            try:
                txt = p.read_text(errors="ignore")
                return [ln.rstrip()[:400] for ln in txt.splitlines()[:limit]]
            except Exception:
                pass
    for p in sorted(d.glob("*")):
        if p.is_file() and p.suffix in CODE_EXT and p.stat().st_size < 256*1024 and "site-packages" not in p.as_posix():
            try:
                return [ln.rstrip()[:400] for ln in p.read_text(errors="ignore").splitlines()[:limit]]
            except Exception:
                continue
    return []

def score_dir(d: Path, have: set, code_count: int):
    s = 0.0
    if have & MARKERS: s += min(0.4, 0.1 * len(have & MARKERS))
    if (d/"README.md").exists() or (d/"README").exists(): s += 0.2
    if (d/"LICENSE").exists(): s += 0.1
    if code_count >= 5: s += 0.2
    if any(bad in d.as_posix() for bad in ["site-packages",".pytest_cache","node_modules"]): s -= 0.5
    return max(0.0, min(1.0, s))

def slugify(t: str) -> str:
    t = re.sub(r"[^a-zA-Z0-9]+","-",t.strip().lower()).strip("-")
    return re.sub(r"-{2,}","-",t) or "project"

def short_id(path: str) -> str:
    h = hashlib.sha1(path.encode("utf-8")).hexdigest()[:8]
    name = Path(path).name
    return f"{slugify(name)}-{h}"

seen_ids = set()
seen_keys = set()  # folder name + markers
proposed = []
scanned = 0
start = time.time()

for root in ROOTS:
    if not root.exists(): continue
    for d in root.rglob("*"):
        if not d.is_dir(): continue
        if ignored_path(d): 
            continue

        have = set(); code_count = 0
        try:
            for p in d.iterdir():
                if p.is_file():
                    if p.name in MARKERS: have.add(p.name)
                    if p.suffix in CODE_EXT: code_count += 1
        except Exception:
            continue

        if not have and code_count < 5:
            scanned += 1
            if scanned % 2000 == 0:
                print(f"[scan] dirs={scanned} props={len(proposed)} elapsed={int(time.time()-start)}s", file=sys.stderr, flush=True)
            continue

        key = (d.name.lower(), tuple(sorted(list(have))[:6]))
        if key in seen_keys:
            scanned += 1
            if scanned % 2000 == 0:
                print(f"[scan] dirs={scanned} props={len(proposed)} elapsed={int(time.time()-start)}s", file=sys.stderr, flush=True)
            continue
        seen_keys.add(key)

        pid = short_id(d.as_posix())
        if pid in seen_ids:
            scanned += 1
            continue
        seen_ids.add(pid)

        conf = score_dir(d, have, code_count)
        if conf < 0.35:
            scanned += 1
            continue

        proj = {
            "id": pid,
            "name": d.name or pid,
            "area": guess_area(d, have),
            "root": d.as_posix(),
            "status": "planned",
            "percent": 0,
            "tags": sorted(list(have)),
            "confidence": round(conf, 3),
            "rationale": f"markers={sorted(list(have))}, code_files~{code_count}",
            "sample": sample_lines(d)
        }
        proposed.append(proj)

        scanned += 1
        if scanned % 2000 == 0:
            print(f"[scan] dirs={scanned} props={len(proposed)} elapsed={int(time.time()-start)}s", file=sys.stderr, flush=True)

proposed.sort(key=lambda x: (-x["confidence"], x["name"]))
OUT.write_text(json.dumps(proposed, indent=2))

auto = [p for p in proposed 
        if p["confidence"] >= 0.70 
        and all(b not in p["root"] for b in ["site-packages",".pytest_cache","node_modules"])]
AUTO.write_text(json.dumps(auto, indent=2))
IDS.write_text("\n".join(p["id"] for p in auto) + ("\n" if auto else ""))

print(f"[smart] roots={len(ROOTS)} proposed={len(proposed)} autoapproved={len(auto)} -> {OUT.name}, {AUTO.name}, {IDS.name}")
print("TOP 20:")
for p in proposed[:20]:
    print(f"{p['id'][:24]:24}  {p['confidence']:.2f}  {p['area']:11}  {p['root']}")
