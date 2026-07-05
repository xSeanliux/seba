from pathlib import Path

import pytest
from seba.syllabus.graph import SyllabusError
from seba.synthesis.synthesize import draft_syllabus, edit_until_valid

GOOD = """goal: g
subject: probability
concepts:
  - id: a
    name: A
"""
BAD = GOOD.replace("name: A", "name: A\n    prereqs: [ghost]")


def test_draft_strips_fences_and_uses_toc():
    captured = {}

    def fake(prompt):
        captured["prompt"] = prompt
        return "```yaml\n" + GOOD + "```"

    out = draft_syllabus("mygoal", "probability", "THE_TOC", fake)
    assert out.strip() == GOOD.strip()
    assert "THE_TOC" in captured["prompt"] and "mygoal" in captured["prompt"]


def test_draft_without_fences_passthrough():
    out = draft_syllabus("g", "probability", "ch1", lambda p: GOOD)
    assert out.strip() == GOOD.strip()


def test_edit_until_valid_passes_through(tmp_path: Path):
    s = edit_until_valid(GOOD, tmp_path / "s.yaml", editor=lambda p: None)
    assert s.concepts[0].id == "a"


def test_edit_until_valid_retries_with_errors(tmp_path: Path):
    calls = []

    def editor(path: Path):
        calls.append(path.read_text())
        if len(calls) == 1:
            assert "ERRORS" not in calls[0]
        else:
            path.write_text(GOOD)

    s = edit_until_valid(BAD, tmp_path / "s.yaml", editor=editor)
    assert len(calls) == 2 and "ghost" in calls[1] and "# ERRORS" in calls[1]
    assert s.concepts[0].id == "a"


def test_edit_gives_up_after_three(tmp_path: Path):
    with pytest.raises(SyllabusError):
        edit_until_valid(BAD, tmp_path / "s.yaml", editor=lambda p: None)
