#!/usr/bin/env bash
# Reverse scripts/install.sh: remove the `seba` CLI and the skill symlink.
set -uo pipefail

uv tool uninstall seba || true
rm -f "$HOME/.claude/skills/seba-tutor"

echo "uninstalled"
