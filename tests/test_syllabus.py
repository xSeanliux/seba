from pathlib import Path
import pytest
import yaml
from seba.models import Concept, Syllabus
from seba.syllabus.graph import (
    SyllabusError,
    apply_status,
    confusables,
    frontier,
    load_syllabus,
    validate,
)


def make(concepts):
    return Syllabus(goal="g", subject="probability", concepts=concepts)


def test_cycle_detected_and_named():
    s = make(
        [
            Concept(id="a", name="A", prereqs=["b"]),
            Concept(id="b", name="B", prereqs=["a"]),
        ]
    )
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
    s = make(
        [
            Concept(id="a", name="A", status="done"),
            Concept(id="b", name="B", prereqs=["a"]),
            Concept(id="c", name="C", prereqs=["a"]),
            Concept(id="d", name="D", prereqs=["b", "c"]),
        ]
    )
    assert [c.id for c in frontier(s)] == ["b", "c"]


def test_frontier_nothing_done():
    s = make([Concept(id="a", name="A"), Concept(id="b", name="B", prereqs=["a"])])
    assert [c.id for c in frontier(s)] == ["a"]


def test_apply_status_legal_and_illegal():
    s = make([Concept(id="a", name="A")])
    s2 = apply_status(s, "a", "in-progress")
    assert s2.concepts[0].status == "in-progress"
    with pytest.raises(SyllabusError):
        apply_status(s, "a", "done")  # no skipping unseen -> done
    with pytest.raises(SyllabusError, match="nope"):
        apply_status(s, "nope", "done")


def test_done_reopens_but_other_moves_back_are_illegal():
    s = make([Concept(id="a", name="A", status="done")])
    assert apply_status(s, "a", "in-progress").concepts[0].status == "in-progress"
    with pytest.raises(SyllabusError):
        apply_status(s, "a", "unseen")
    with pytest.raises(SyllabusError):
        apply_status(s, "a", "done")  # already done: not a move
    ip = make([Concept(id="a", name="A", status="in-progress")])
    with pytest.raises(SyllabusError):
        apply_status(ip, "a", "unseen")


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


def test_soft_prereq_does_not_block_frontier():
    s = make(
        [
            Concept(id="a", name="A"),
            Concept(id="b", name="B", soft_prereqs=["a"]),
        ]
    )
    validate(s)
    assert [c.id for c in frontier(s)] == ["a", "b"]


def test_unknown_soft_prereq_rejected():
    s = make([Concept(id="a", name="A", soft_prereqs=["ghost"])])
    with pytest.raises(SyllabusError, match="unknown soft_prereqs"):
        validate(s)


def test_soft_cycle_rejected():
    s = make(
        [
            Concept(id="a", name="A", soft_prereqs=["b"]),
            Concept(id="b", name="B", prereqs=["a"]),
        ]
    )
    with pytest.raises(SyllabusError, match="cycle"):
        validate(s)


def test_confusable_with_is_not_a_dependency():
    s = make(
        [
            Concept(id="a", name="A", confusable_with=["b"]),
            Concept(id="b", name="B", confusable_with=["a"]),
        ]
    )
    validate(s)  # mutual confusables are not a cycle
    assert [c.id for c in frontier(s)] == ["a", "b"]


def test_unknown_confusable_rejected():
    s = make([Concept(id="a", name="A", confusable_with=["ghost"])])
    with pytest.raises(SyllabusError, match="unknown confusable_with"):
        validate(s)


def test_confusables_unions_both_directions():
    s = make(
        [
            Concept(id="a", name="A", confusable_with=["b"]),
            Concept(id="b", name="B"),
            Concept(id="c", name="C", confusable_with=["a"]),
        ]
    )
    assert confusables(s, "a") == ["b", "c"]
    assert confusables(s, "b") == ["a"]


def test_old_format_syllabus_still_loads(tmp_path: Path):
    p = tmp_path / "syllabus.yaml"
    p.write_text(
        "goal: g\nsubject: probability\nconcepts:\n"
        "  - id: a\n    name: A\n    prereqs: []\n    sources: []\n"
        "    status: unseen\n    est_sessions: 1\n"
    )
    c = load_syllabus(p).concepts[0]
    assert (c.soft_prereqs, c.confusable_with, c.kc_type) == ([], [], "concept")


def test_new_fields_round_trip(tmp_path: Path):
    s = make(
        [
            Concept(id="a", name="A", kc_type="fact"),
            Concept(
                id="b",
                name="B",
                soft_prereqs=["a"],
                confusable_with=["a"],
                kc_type="procedure",
            ),
        ]
    )
    p = tmp_path / "syllabus.yaml"
    p.write_text(yaml.safe_dump(s.model_dump(mode="json"), sort_keys=False))
    assert load_syllabus(p) == s
