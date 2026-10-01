import re
from pathlib import Path

import pytest
import typer
import yaml

from seba.cli import app

SKILLS = Path(__file__).parents[1] / "skills"
CLI_DOCS = Path(__file__).parents[1] / "docs" / "cli.md"


@pytest.mark.parametrize("name", ["seba-tutor", "seba-syllabus"])
def test_skill_has_name_and_description(name):
    text = (SKILLS / name / "SKILL.md").read_text()
    _, front, _ = text.split("---\n", 2)
    meta = yaml.safe_load(front)
    assert meta["name"] == name
    assert meta["description"].strip()


def _commands() -> dict[str, set[str]]:
    group = typer.main.get_command(app)
    return {
        name: {o for p in cmd.params for o in p.opts if o.startswith("--")}
        for name, cmd in group.commands.items()
    }


@pytest.mark.parametrize("path", sorted(SKILLS.glob("*/*.md")), ids=lambda p: p.name)
def test_every_command_a_skill_names_exists(path):
    commands = _commands()
    docs = CLI_DOCS.read_text()
    spans = re.findall(r"`(seba [^`]*)`", path.read_text())
    assert spans
    for span in spans:
        name = span.split()[1]
        assert name in commands, span
        assert f"`seba {name}`" in docs, span
        for flag in re.findall(r"--[a-z-]+", span):
            assert flag in commands[name], span
