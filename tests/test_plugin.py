import json
import os
import tomllib

from seba.config import REPO_ROOT

PLUGIN = REPO_ROOT / ".claude-plugin"


def test_marketplace_entry_points_at_this_plugin():
    market = json.loads((PLUGIN / "marketplace.json").read_text())
    [entry] = market["plugins"]
    root = REPO_ROOT / entry["source"]
    assert (root / ".claude-plugin" / "plugin.json").is_file()
    assert (root / "skills" / "seba-tutor" / "SKILL.md").is_file()
    assert os.access(root / "bin" / "seba", os.X_OK)
    # plugin.json alone carries the version; a second copy here could disagree.
    assert "version" not in entry


def test_plugin_and_package_versions_agree():
    plugin = json.loads((PLUGIN / "plugin.json").read_text())
    project = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text())
    assert plugin["version"] == project["project"]["version"]
