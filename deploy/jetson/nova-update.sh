#!/usr/bin/env bash
# Pulls the latest Nova from GitHub, checks it, and restarts Nova.
# nova-update.timer runs this every few minutes; it's also safe to run by hand.
#
# - Does nothing if the Jetson is already on the latest commit.
# - Runs `uv sync` and the tests on the new commit. If they fail, it rolls back
#   and skips that commit until a newer one is pushed.
# - Restarts nova.service if one is installed.
set -euo pipefail

REPO_DIR="${NOVA_REPO_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
BRANCH="${NOVA_BRANCH:-main}"
STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/nova-update"
BAD_FILE="$STATE_DIR/bad-commit"

log() { echo "[nova-update] $*"; }

mkdir -p "$STATE_DIR"
cd "$REPO_DIR"

if [[ "$(git symbolic-ref --short HEAD 2>/dev/null)" != "$BRANCH" ]]; then
  log "Not on branch $BRANCH; not updating. Run: git checkout $BRANCH"
  exit 1
fi

git fetch --quiet origin "$BRANCH"
current=$(git rev-parse HEAD)
target=$(git rev-parse "origin/$BRANCH")

if [[ "$current" == "$target" ]]; then
  exit 0
fi
if [[ -f "$BAD_FILE" && "$(cat "$BAD_FILE")" == "$target" ]]; then
  log "Skipping ${target:0:7}: it failed checks earlier. Push a fix to move past it."
  exit 0
fi
if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  log "There are local changes in $REPO_DIR; not updating. Commit or discard them first."
  exit 1
fi

log "Updating ${current:0:7} -> ${target:0:7}"
if ! git merge --ff-only --quiet "origin/$BRANCH"; then
  log "Local $BRANCH has commits GitHub doesn't; not updating."
  exit 1
fi

if uv sync --frozen && uv run pytest -q; then
  rm -f "$BAD_FILE"
  if systemctl --user cat nova.service >/dev/null 2>&1; then
    systemctl --user restart nova.service
    log "Restarted nova.service"
  fi
  log "Now on ${target:0:7}"
else
  log "Checks failed on ${target:0:7}; rolling back to ${current:0:7}"
  echo "$target" > "$BAD_FILE"
  git reset --hard --quiet "$current"
  uv sync --frozen
  exit 1
fi
