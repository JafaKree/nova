#!/usr/bin/env bash
# One-time setup on the Jetson. Run from the cloned repo:
#   bash deploy/jetson/install.sh
set -euo pipefail

REPO_DIR=$(cd "$(dirname "$0")/../.." && pwd)
HERE="$REPO_DIR/deploy/jetson"
UNIT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"

export PATH="$HOME/.local/bin:$PATH"
if ! command -v uv >/dev/null; then
  echo "uv isn't installed. Install it with:"
  echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 1
fi

echo "Installing dependencies..."
(cd "$REPO_DIR" && uv sync --frozen)

echo "Installing the update timer..."
mkdir -p "$UNIT_DIR"
for unit in nova-update.service nova-update.timer; do
  sed "s|@REPO@|$REPO_DIR|g" "$HERE/$unit" > "$UNIT_DIR/$unit"
done

# Let user services keep running after you log out and start at boot.
loginctl enable-linger "$USER" 2>/dev/null || sudo loginctl enable-linger "$USER"

systemctl --user daemon-reload
systemctl --user enable --now nova-update.timer

echo
echo "Done. The Jetson now checks GitHub for Nova updates every 5 minutes."
echo "  Next check:   systemctl --user list-timers nova-update.timer"
echo "  Update now:   systemctl --user start nova-update.service"
echo "  View the log: journalctl --user -u nova-update.service -n 50"
