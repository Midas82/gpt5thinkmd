# TRINITY PROJECT MASTER CONTROL
Generated: 2025-10-20T05:13:14-06:00
DO NOT EDIT BY HAND

## SYSTEM STATUS
- Orchestrator: GPT-5 (architect + coordinator)
- Primary Builder: Gemini CLI
- Premium Builder: Claude Code CLI (token-limited)
- Base: /home/midas/refresh/organized/arch/geminicli/gpt5thinkmd

## WORKFLOW RULES
1) GPT-5 routes all work. 2) Use Gemini for ~90% of builds. 3) Use Claude Code only when Gemini cannot.
4) Every action updates this file. 5) No role confusion.

## TOKEN MANAGEMENT
- Track Claude Code tokens here. Switch to Gemini when <20% remain.

## ACTIVE CONTEXT
- Current Project: [none]
- Last Action: Initialization at 2025-10-20T05:13:14-06:00
- Next Steps: Generate WORKSPACE_MASTER_PLAN.md and create first project.

## PROJECT REGISTRY
| ID | Name | Status | Created | Progress | Builder Used |
|----|------|--------|---------|----------|--------------|

## BRAINFLASH LOG
| Timestamp | Idea | Status |
|-----------|------|--------|

## BUILD PROTOCOL
1) GPT-5 designs → ARCHITECT.md
2) Builder implements (default: Gemini) → BUILD.md
3) GPT-5 verifies → update this file
4) Repeat
## RUNNER MATRIX
- You:
  - Export env vars, create dirs, set git remote, push.
  - Run local dev: ops/dev.sh, ops/verify.sh.
  - Use ws CLI when needed: ws new|import|eval.
- Gemini CLI (Primary Builder):
  - Generate/commit docs: ops/gen_master_plan.py, ops/refresh_plan.sh.
  - Workspace ops: scripts/gen_bootstrap.sh, scripts/gen_task_stubs.sh.
  - Deep enrichment and file changes; commit results.
- Claude Code CLI (Premium, token-limited):
  - Same as Gemini only if Gemini cannot proceed.
- Web Claude (Orchestrator):
  - Route DESIGN→GPT-5, BUILD→Builder; track status. No file writes.
- GPT-5 (Architect):
  - Produce ARCHITECT.md and design artifacts. No shell commands.
