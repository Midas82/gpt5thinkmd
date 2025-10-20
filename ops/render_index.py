import json, time
from pathlib import Path
root = Path.home()
projects = root.joinpath("refresh/index/projects.json")
index_md = root.joinpath("refresh/index/index.md")
arr = []
if projects.exists():
    arr = json.loads(projects.read_text() or "[]")
status_counts = {}
for p in arr:
    status_counts[p.get("status","unknown")] = status_counts.get(p.get("status","unknown"),0)+1
lines = ["# Global Index", "", "_Source of truth is projects.json. This file is rendered from it._", ""]
lines += [f"- Total projects: {len(arr)}"]
for k in sorted(status_counts):
    lines += [f"- {k}: {status_counts[k]}"]
lines += ["", f"_Rendered: {time.strftime('%Y-%m-%d %H:%M:%S')}_", "", "## Projects", ""]
for p in arr:
    lines += [f"- **{p.get('name','<unnamed>') }** — `{p.get('area','')}` — {p.get('status','')}"
              + (f" — next: {', '.join(p.get("next_actions",[])[:3])}" if p.get("next_actions") else "")]
index_md.write_text("\n".join(lines))