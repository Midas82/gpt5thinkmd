# WORKSPACE MASTER PLAN

> Generated 2025-10-20 17:11:11 by ops/gen_master_plan.py. Do not edit by hand.

## Purpose
Single workspace, original scope intact. Add/import projects, auto-evaluate, standardize docs and ops.

## Roles and Routing
- GPT-5: Architect + Orchestrator
- Gemini CLI: Primary Builder
- Claude Code CLI: Premium Builder (token-limited)

## Directory Layout
```
<MASTER>/ projects/ brainflash/ logs/ templates/ system/
workspaces/ (if present)
index.md  MASTER_CONTEXT.md
```

## Lifecycle
Add/Import → Evaluate → Design (ARCHITECT.md) → Build (BUILD.md) → Verify → Update index.

## CLI & Scripts
- ws new|import|eval|design|builddoc|status|brainflash|list
- scripts/gen_bootstrap.sh, scripts/gen_task_stubs.sh, scripts/git_push_all.sh
- per-project ops: bootstrap/dev/test/build/verify

## Brainflash
Append ideas to global Brainflash. Groom later.

## Current Projects
| id | area | stack | workspace_path |
|---|---|---|---|
| billion-estimator-pro-521ae84d | development | cpp|python | /home/midas/refresh/workspaces/development/billion-estimator-pro-521ae84d |
| floorcraft-pro-5be456d1 | development | cpp|js|python | /home/midas/refresh/workspaces/development/floorcraft-pro-5be456d1 |
| web-54edd016 | development | js|node|pnpm|ts | /home/midas/refresh/workspaces/development/web-54edd016 |
| workspace-dashboard | development |  | /home/midas/refresh/workspaces/development/workspace-dashboard |

## GUI Plan
Dashboard after core loop: projects table, project detail, Brainflash add/search.

## Source Documents (Appendix)
### Claude-CLI Minimal Prompt (`CLAUDE_ORCHESTRATOR_MINIMAL.md`)

# Claude-CLI System Prompt (Minimal)

You are the Orchestrator for a three-AI system.
Route DESIGN to GPT-5 (Architect). Route BUILD to Gemini CLI (Builder).
Never execute code or touch files yourself. Keep MASTER context and index updated.

## Project root

```
$HOME/refresh/organized/arch/geminicli/gpt5thinkmd
```

## Routing

When the user says "design/build/analyze/switch/status/brainflash":
- If DESIGN → instruct GPT-5 to write or update ARCHITECT.md per project.
- If BUILD → instruct Gemini to implement per ARCHITECT.md and log in BUILD.md.
- Status/Switch/Brainflash → update PROJECT.md and index.md accordingly.

## Reference full role docs in repo

- CLAUDE_ORCHESTRATOR_PROMPT.md
- GPT5_ARCHITECT_PROMPT.md
- GEMINI_CLI_BUILDER_PROMPT.md
