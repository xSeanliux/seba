#!/usr/bin/env python3
"""Bump Seba's version everywhere it is written, and print the new one.

Usage: bump_version.py major|minor|patch [REPO_ROOT]

The version lives in .claude-plugin/plugin.json (what Claude Code compares to
decide an update), pyproject.toml (what the CLI reports) and uv.lock (seba's own
entry, so `uv lock --check` stays clean). The release workflow runs this on
every merge to main.
"""

import json
import re
import sys
from pathlib import Path


def bump(version: str, part: str) -> str:
    major, minor, patch = (int(n) for n in version.split("."))
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    if part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise SystemExit(f"unknown bump {part!r}: use major, minor or patch")


def main() -> None:
    part = sys.argv[1]
    root = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).parents[1]

    plugin = root / ".claude-plugin" / "plugin.json"
    manifest = json.loads(plugin.read_text())
    new = bump(manifest["version"], part)
    manifest["version"] = new
    plugin.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    for name, pattern in [
        ("pyproject.toml", r'(?m)^(version = ")[^"]+(")'),
        ("uv.lock", r'(name = "seba"\nversion = ")[^"]+(")'),
    ]:
        path = root / name
        text, n = re.subn(pattern, rf"\g<1>{new}\g<2>", path.read_text(), count=1)
        if n != 1:
            raise SystemExit(f"no version found in {path}")
        path.write_text(text)

    print(new)


if __name__ == "__main__":
    main()
