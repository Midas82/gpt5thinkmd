import os, json, shutil, time
from pathlib import Path

HOME = Path.home()
MASTER = HOME / "refresh" / "organized" / "arch" / "geminicli" / "gpt5thinkmd"
TEMPL = MASTER / "templates"
INDEX = HOME / "refresh" / "index"
CTRL  = INDEX / "controls.json"
APPROVED = INDEX / "approved_projects.json"
WORKSPACES = HOME / "refresh" / "workspaces"

def load_json(p: Path, default):
    if p.exists():
        try:
            return json.loads(p.read_text() or json.dumps(default))
        except Exception:
            return default
    return default

def write(path: Path, content: str, dry=True):
    path.parent.mkdir(parents=True, exist_ok=True)
    if dry:
        print(f"[dry] write {path}")
        return
    path.write_text(content)

def ensure_dir(path: Path, dry=True):
    if dry:
        print(f"[dry] mkdir -p {path}")
    else:
        path.mkdir(parents=True, exist_ok=True)

def stamp():
    return time.strftime("%Y-%m-%d")

def main():
    ctrl = load_json(CTRL, {"dry_run": True})
    dry = bool(ctrl.get("dry_run", True))
    items = load_json(APPROVED, [])
    created = 0
    for p in items:
        area = p.get("area","unsorted")
        slug = p.get("id", p.get("name","project"))
        base = WORKSPACES / area / slug
        ensure_dir(base, dry)
        for sub in ["docs","src","assets","data","ops"]:
            ensure_dir(base / sub, dry)

        # Seed docs from templates
        def tmpl(name): return (TEMPL / name).read_text() if (TEMPL / name).exists() else ""
        def fill(s: str) -> str:
            return (s.replace("<project-name>", p.get("name",""))
                     .replace("<area>", area)
                     .replace("planned", p.get("status","planned"))
                     .replace("<tags>", ", ".join(p.get("tags",[])))
                     .replace("<YYYY-MM-DD>", stamp()))
        files = {
            "PROJECT.md": fill(tmpl("PROJECT.md")),
            "CONTEXT.md": tmpl("CONTEXT.md"),
            "TASKS.md": tmpl("TASKS.md"),
            "PROGRESS.md": tmpl("PROGRESS.md"),
            "STRUCTURE.yml": "folders: [docs, src, assets, data, ops]\nrules:\n  - ignore: [\"**/node_modules/**\", \".git/**\", \"**/__pycache__/**\", \"**/.cache/**\", \".DS_Store\", \"thumbs.db\"]\n"
        }
        for name, content in files.items():
            write(base / name, content, dry)

        created += 1

    print(f"[apply] approved={len(items)} created={created} dry_run={dry}")
    if dry:
        print(f"[hint] To apply, set controls.json dry_run=false and re-run.")

if __name__ == "__main__":
    main()
