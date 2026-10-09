#!/usr/bin/env bash
#
# Install this repo's git hooks. Idempotent — safe to run any time, and you
# should run it once after every fresh clone.
#
#   ./scripts/install-hooks.sh
#
# It symlinks scripts/pre-push into .git/hooks/pre-push so edits to the tracked
# hook take effect immediately. The hook blocks pushes that contain secrets or
# personal/local data. See scripts/pre-push for details.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOK_DIR="$(git rev-parse --git-path hooks)"
mkdir -p "$HOOK_DIR"

SRC="$REPO_ROOT/scripts/pre-push"
DEST="$HOOK_DIR/pre-push"

chmod +x "$SRC"

# Prefer a relative symlink; fall back to a copy if symlinks are unavailable.
if ln -sf "../../scripts/pre-push" "$DEST" 2>/dev/null && [ -e "$DEST" ]; then
  echo "✅ Installed pre-push hook (symlink → scripts/pre-push)"
else
  cp "$SRC" "$DEST"
  chmod +x "$DEST"
  echo "✅ Installed pre-push hook (copy of scripts/pre-push)"
fi

if [ -f "$REPO_ROOT/local/hook-extra-patterns.txt" ]; then
  echo "   Loaded private markers from local/hook-extra-patterns.txt"
else
  echo "   (No local/hook-extra-patterns.txt — generic secret + local-data guard only.)"
fi
