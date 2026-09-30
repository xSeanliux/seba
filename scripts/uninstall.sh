#!/usr/bin/env bash
# Reverse scripts/install.sh: remove the `seba` CLI and the skill symlinks.
set -uo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

uv tool uninstall seba || true
for skill in "$repo"/skills/*/; do
  rm -f "$HOME/.claude/skills/$(basename "$skill")"
done

echo "uninstalled"
