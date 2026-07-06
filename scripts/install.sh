#!/usr/bin/env bash
# Install the `seba` CLI globally and link the seba-tutor skill into Claude Code.
# Requires: uv (https://docs.astral.sh/uv/). Reverse with scripts/uninstall.sh.
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo"

uv tool install --force .
mkdir -p "$HOME/.claude/skills"
ln -sfn "$repo/skills/seba-tutor" "$HOME/.claude/skills/seba-tutor"

echo "installed — run 'claude' and ask to study, or /seba-tutor"
