#!/usr/bin/env bash
set -euo pipefail
REPO="$HOME/refresh/organized/arch/geminicli/gpt5thinkmd"
REMOTE_NAME="origin"
REMOTE_URL="git@github.com:YOURUSER/gpt5thinkmd.git"  # change me

cd "$REPO"
git remote | grep -qx "$REMOTE_NAME" || git remote add "$REMOTE_NAME" "$REMOTE_URL"
git add -A
git commit -m "chore: bootstrap generators and task stubs" || true
git push -u "$REMOTE_NAME" "$(git rev-parse --abbrev-ref HEAD)"
