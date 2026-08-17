#!/usr/bin/env bash
# Install the `seba` CLI globally and link the seba-tutor skill into Claude Code.
# Requires: uv (https://docs.astral.sh/uv/). Reverse with scripts/uninstall.sh.
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo"

# --reinstall as well as --force: without it uv can serve a cached build of seba
# itself, leaving the CLI stale while the skill — a symlink — is already live.
# A new prompt against an old CLI calls flags that don't exist yet.
uv tool install --force --reinstall .
mkdir -p "$HOME/.claude/skills"
ln -sfn "$repo/skills/seba-tutor" "$HOME/.claude/skills/seba-tutor"

echo "installed — run 'claude' and ask to study, or /seba-tutor"
