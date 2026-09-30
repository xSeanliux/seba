#!/usr/bin/env bash
# Release Seba: bump the version, commit, tag, push, and create a GitHub Release.
# Usage: scripts/release.sh major|minor|patch [--dry-run]
# The release workflow runs this on every merge to main. --dry-run prints what
# it would do and changes nothing.
set -euo pipefail
part=${1:?usage: release.sh major|minor|patch [--dry-run]}
cd "$(dirname "${BASH_SOURCE[0]}")/.."

if [[ "${2:-}" == --dry-run ]]; then
  version=$(uv version --bump "$part" --dry-run --short)
  echo "would bump $(uv version --short) -> $version in pyproject.toml, uv.lock, .claude-plugin/plugin.json"
  echo "would commit 'chore: release v$version', tag v$version"
  echo "would run: git push --atomic origin HEAD:main v$version"
  echo "would run: gh release create v$version --generate-notes --title v$version"
  exit 0
fi

# uv bumps pyproject.toml and seba's entry in uv.lock; plugin.json follows,
# since it is the copy Claude Code compares to decide an update.
version=$(uv version --bump "$part" --no-sync --short)
jq --arg v "$version" '.version = $v' .claude-plugin/plugin.json > plugin.json.tmp
mv plugin.json.tmp .claude-plugin/plugin.json

git commit -am "chore: release v$version"
git tag "v$version"
# --atomic: if main moved since checkout, reject the tag too, so no tag lands
# on a commit that never reached main.
git push --atomic origin HEAD:main "v$version"
gh release create "v$version" --generate-notes --title "v$version"
