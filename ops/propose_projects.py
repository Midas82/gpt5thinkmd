import os, json, time, hashlib, re
from pathlib import Path

HOME = Path.home()
MASTER = HOME / "refresh" / "organized" / "arch" / "geminicli" / "gpt5thinkmd"
INDEX = HOME / "refresh" / "index"
CANDS = INDEX / "project_candidates.jsonl"
OUTDIR = INDEX / "proposals"
OUTDIR.mkdir(parents=True, exist_ok=True)
OUTFILE = OUTDIR / "projects_proposed.json"

def slugify(text: str) -> str:
    t = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return re.sub(r"-{2,}", "-", t) or "project"

def short_id(path: str) -> str:
    h = hashlib.sha1(path.encode("utf-8")).hexdigest()[:8]
    name = Path(path).name
    return f"{slugify(name)}-{h}"

def guess_area(path: str, markers: list[str]) -> str:
    p = path.lower()
    if any(m in markers for m in ["package.json","pyproject.toml","requirements.txt","cargo.toml","go.mod","makefile"]):
        return "development"
    if "/documents/" in p:
        return "documents"
    if "/downloads/" in p:
        return "downloads"
    if "/desktop/" in p:
        return "desktop"
    if any(x in p for x in ["/music","/audio","/daw","/mix","/podcast"]):
        return "media"
    if any(x in p for x in ["/photo","/image","/img","/camera"]):
        return "photography"
    if any(x in p for x in ["/3d","/cad","/print","/stl"]):
        return "maker"
    return "unsorted"

def load_candidates():
    if not CANDS.exists():
        return []
    items = []
    with CANDS.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except Exception:
                continue
    return items

def top_files(dir_path: Path, limit=12):
    try:
        names = []
        for p in sorted(dir_path.iterdir()):
            if p.is_file():
                names.append(p.name)
            if len(names) >= limit:
                break
        return names
    except Exception:
        return []

def main():
    now = time.strftime("%Y-%m-%d")
    cands = load_candidates()
    out = []
    seen_dirs = set()
    for c in cands:
        d = c.get("dir")
        if not d or d in seen_dirs:
            continue
        seen_dirs.add(d)
        markers = c.get("markers", [])
        pid = short_id(d)
        name = Path(d).name or pid
        area = guess_area(d, markers)
        proj = {
            "id": pid,
            "name": name,
            "area": area,
            "root": d,
            "status": "planned",
            "percent": 0,
            "tags": sorted(list(set(markers))),
            "created": now,
            "updated": now,
            "next_actions": [
                "review proposal",
                "confirm area",
                "approve or drop"
            ],
            "files": top_files(Path(d))
        }
        out.append(proj)

    OUTFILE.write_text(json.dumps(out, indent=2))
    print(f"[propose] candidates={len(cands)} proposed={len(out)} -> {OUTFILE}")

if __name__ == "__main__":
    main()