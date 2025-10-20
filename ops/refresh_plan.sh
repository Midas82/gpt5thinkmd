#!/usr/bin/env bash
set -euo pipefail
python ops/gen_master_plan.py
git add WORKSPACE_MASTER_PLAN.md TRINITY_MASTER_CONTROL.md || true
git commit -m "docs: refresh master plan" || true
