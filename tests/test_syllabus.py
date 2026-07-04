from pathlib import Path
import pytest
from seba.models import Concept, Syllabus
from seba.syllabus.graph import SyllabusError, apply_status, frontier, load_syllabus, validate


def make(concepts):
    return Syllabus(goal="g", subject="probability", concepts=concepts)


def test_cycle_detected_and_named():
    s = make([Concept(id="a", name="A", prereqs=["b"]),
              Concept(id="b", name="B", prereqs=["a"])])
    with pytest.raises(SyllabusError, match="a"):
        validate(s)


def test_unknown_prereq_rejected():
    s = make([Concept(id="a", name="A", prereqs=["ghost"])])
    with pytest.raises(SyllabusError, match="ghost"):
        validate(s)


def test_duplicate_id_rejected():
    s = make([Concept(id="a", name="A"), Concept(id="a", name="A2")])
    with pytest.raises(SyllabusError, match="a"):
        validate(s)


def test_frontier_diamond():
    s = make([Concept(id="a", name="A", status="done"),
              Concept(id="b", name="B", prereqs=["a"]),
              Concept(id="c", name="C", prereqs=["a"]),
              Concept(id="d", name="D", prereqs=["b", "c"])])
    assert [c.id for c in frontier(s)] == ["b", "c"]


def test_frontier_nothing_done():
    s = make([Concept(id="a", name="A"), Concept(id="b", name="B", prereqs=["a"])])
    assert [c.id for c in frontier(s)] == ["a"]


def test_apply_status_legal_and_illegal():
    s = make([Concept(id="a", name="A")])
    s2 = apply_status(s, "a", "in-progress")
    assert s2.concepts[0].status == "in-progress"
    with pytest.raises(SyllabusError):
        apply_status(s, "a", "done")
    with pytest.raises(SyllabusError, match="nope"):
        apply_status(s, "nope", "done")


def test_load_syllabus_yaml(tmp_path: Path):
    p = tmp_path / "syllabus.yaml"
    p.write_text(
        "goal: g\nsubject: probability\nconcepts:\n"
        "  - id: a\n    name: A\n"
        "  - id: b\n    name: B\n    prereqs: [a]\n"
    )
    s = load_syllabus(p)
    assert [c.id for c in s.concepts] == ["a", "b"]


def test_load_syllabus_bad_file_names_path(tmp_path: Path):
    p = tmp_path / "syllabus.yaml"
    p.write_text("goal: g\nsubject: s\nconcepts: [{id: a, name: A, prereqs: [a]}]")
    with pytest.raises(SyllabusError, match="syllabus.yaml"):
        load_syllabus(p)
