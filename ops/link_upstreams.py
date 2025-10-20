#!/usr/bin/env python3
import json, shutil
from pathlib import Path

HOME = Path.home()
INDEX = HOME/"refresh"/"index"
WS = HOME/"refresh"/"workspaces"

appr = INDEX/"approved_projects.json"
if not appr.exists():
    raise SystemExit("[link] no approved_projects.json found")
APPROVED = json.loads(appr.read_text() or "[]")

def symlink_force(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        if dst.exists() or dst.is_symlink():
            dst.unlink()
    except Exception:
        pass
    try:
        dst.symlink_to(src)
        return True
    except Exception:
        return False

made = copied = meta_w = 0
for p in APPROVED:
    area = p.get("area","unsorted")
    pid = p.get("id") or p.get("name") or "project"
    root = Path(p["root"]).expanduser()
    w = WS/area/pid
    ok = symlink_force(root, w/"src"/"upstream")
    if ok:
        made += 1
    for cand in ("README.md","README","Readme.md"):
        r = root/cand
        if r.exists() and r.is_file():
            (w/"docs").mkdir(parents=True, exist_ok=True)
            shutil.copy2(r, w/"docs"/"README.upstream.md")
            copied += 1
            break
    meta = {
        "id": pid,
        "area": area,
        "root": root.as_posix(),
        "tags": p.get("tags", []),
        "confidence": p.get("confidence"),
        "linked_upstream": ok,
    }
    (w/"ops").mkdir(parents=True, exist_ok=True)
    (w/"ops"/"meta.json").write_text(json.dumps(meta, indent=2))
    meta_w += 1

print(f"[link] symlinks={made} readmes_copied={copied} metas={meta_w}")
