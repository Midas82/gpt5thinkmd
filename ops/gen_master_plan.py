import os, csv, datetime, textwrap
from pathlib import Path

MASTER = Path(os.environ.get("MASTER", "")) or Path.cwd()
INDEX  = Path(os.environ.get("INDEX", "")) or MASTER.parent.parent/"index"
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

sources = [
 ("WORKSPACE_OVERVIEW.md","Workspace Overview"),
 ("BUILD.md","Build Guide"),
 ("README_START_HERE.md","Read Me First"),
 ("SYSTEM_OVERVIEW.md","System Overview"),
 ("QUICK_START_GUIDE.md","Quick Start"),
 ("VISUAL_WORKFLOWS.md","Visual Workflows"),
 ("CLAUDE_ORCHESTRATOR_PROMPT.md","Claude Orchestrator Prompt"),
 ("GPT5_ARCHITECT_PROMPT.md","GPT-5 Architect Prompt"),
 ("GEMINI_CLI_BUILDER_PROMPT.md","Gemini CLI Builder Prompt"),
 ("CLAUDE_ORCHESTRATOR_MINIMAL.md","Claude-CLI Minimal Prompt"),
]

def read_if(p:Path, limit=2000):
    if not p.exists(): return None
    s=p.read_text(errors="ignore").strip()
    return s[:limit]

def load_projects():
    p = Path(INDEX)/"workspaces.tsv"
    rows=[]
    if p.exists():
        with p.open() as f:
            for row in csv.DictReader(f, delimiter="\t"):
                rows.append(row)
    return rows

def section_projects():
    rows=load_projects()
    if not rows: return "No projects listed.\n"
    out=["| id | area | stack | workspace_path |"]
    out.append("|---|---|---|---|")
    for r in rows:
        out.append(f"| {r['id']} | {r['area']} | {r['stack']} | {r['workspace_path']} |")
    return "\n".join(out)+"\n"

def appendix():
    parts=[]
    for fname,title in sources:
        txt=read_if(MASTER/fname)
        if txt:
            parts.append(f"### {title} (`{fname}`)\n\n{txt}\n")
    return "\n".join(parts) if parts else "_No source docs found._\n"

doc=[]
doc.append(f"# WORKSPACE MASTER PLAN\n\n> Generated {now} by ops/gen_master_plan.py. Do not edit by hand.\n")
doc.append("## Purpose\nSingle workspace, original scope intact. Add/import projects, auto-evaluate, standardize docs and ops.\n")
doc.append("## Roles and Routing\n- GPT-5: Architect + Orchestrator\n- Gemini CLI: Primary Builder\n- Claude Code CLI: Premium Builder (token-limited)\n")
doc.append("## Directory Layout\n```\n<MASTER>/ projects/ brainflash/ logs/ templates/ system/\nworkspaces/ (if present)\nindex.md  MASTER_CONTEXT.md\n```\n")
doc.append("## Lifecycle\nAdd/Import → Evaluate → Design (ARCHITECT.md) → Build (BUILD.md) → Verify → Update index.\n")
doc.append("## CLI & Scripts\n- ws new|import|eval|design|builddoc|status|brainflash|list\n- scripts/gen_bootstrap.sh, scripts/gen_task_stubs.sh, scripts/git_push_all.sh\n- per-project ops: bootstrap/dev/test/build/verify\n")
doc.append("## Brainflash\nAppend ideas to global Brainflash. Groom later.\n")
doc.append("## Current Projects\n"+section_projects())
doc.append("## GUI Plan\nDashboard after core loop: projects table, project detail, Brainflash add/search.\n")
doc.append("## Source Documents (Appendix)\n"+appendix())

out=MASTER/"WORKSPACE_MASTER_PLAN.md"
out.write_text("\n".join(doc))
print(f"[ok] wrote {out}")