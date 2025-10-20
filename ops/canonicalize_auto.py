import os, json, re, time
from pathlib import Path

HOME = Path.home()
IDX = HOME/"refresh"/"index"
PROPDIR = IDX/"proposals"
AUTO = json.loads((PROPDIR/"smart_autoapproved.json").read_text() or "[]")
PROPOSED = json.loads((PROPDIR/"smart_projects_proposed.json").read_text() or "[]")

def base_id(pid:str):
    parts = pid.split("-")
    if parts and len(parts[-1])==8 and all(c in "0123456789abcdef" for c in parts[-1]):
        return "-".join(parts[:-1]) or pid
    return pid

def score_path(p:str, tags:set[str]):
    s = 0.0
    if p.startswith((HOME/"Projects").as_posix()): s += 5
    elif p.startswith(HOME.as_posix()): s += 4
    elif p.startswith(Path("/mnt").as_posix()) or p.startswith(Path("/media").as_posix()) or p.startswith(Path("/run/media").as_posix()): s += 2
    if "/.gemini/workspace/bind/" in p: s -= 100
    if "needs_transferred_to_remote_backups_drive" in p: s -= 50
    if ".git" in tags: s += 2
    try: s += os.stat(p).st_mtime * 1e-8
    except: pass
    s -= len(p) * 1e-3
    return s

# index proposed by path for tags/metadata
by_path = {x["root"]: x for x in PROPOSED}
groups = {}
for itm in AUTO:
    b = base_id(itm["id"])
    groups.setdefault(b, []).append(itm)

canon = []
suppressed = []
for b, items in groups.items():
    best = None; best_score = -1e9
    for it in items:
        path = it["root"]
        tags = set(by_path.get(path, it).get("tags", []))
        sc = score_path(path, tags)
        if sc > best_score:
            best = it; best_score = sc
    canon.append(best)
    for it in items:
        if it is not best:
            suppressed.append({"base": b, "kept": best["root"], "drop": it["root"]})

outdir = IDX/"canonical"
outdir.mkdir(parents=True, exist_ok=True)
(IDX/"approved_projects.json").write_text(json.dumps(canon, indent=2))
(outdir/"dupes.csv").write_text(
    "base,kept,drop\n" + "\n".join(f'{d["base"]},"{d["kept"]}","{d["drop"]}' for d in suppressed)
)
(outdir/"summary.json").write_text(json.dumps({
    "auto_in": len(AUTO),
    "bases": len(groups),
    "kept": len(canon),
    "suppressed": len(suppressed)
}, indent=2))
print(f'[canon] auto_in={len(AUTO)} bases={len(groups)} kept={len(canon)} suppressed={len(suppressed)}')
