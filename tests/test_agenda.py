from datetime import date
from pathlib import Path

from seba.models import Concept, GoalState, Item, SubjectProfile, Syllabus
from seba.scheduler.agenda import build_agenda, resolve_excerpt

TODAY = date(2026, 7, 3)


def profile(max_reviews=6):
    return SubjectProfile(name="probability", kind="technical",
                          max_reviews_per_session=max_reviews,
                          item_types=["recall", "apply"], session_shape="teach-heavy")


def state(concepts, items=(), notes="", recent=()):
    return GoalState(name="prob", subject="probability",
                     syllabus=Syllabus(goal="prob", subject="probability",
                                       concepts=list(concepts)),
                     items=list(items), notes=notes, session_number=2,
                     recent_grades=list(recent))


def item(id, due="2026-07-01T00:00:00+00:00", concept="a"):
    return Item(id=id, concept=concept, type="recall", front="f", back="b",
                fsrs={"due": due}, created=TODAY)


def test_teach_prefers_in_progress(tmp_path):
    s = state([Concept(id="a", name="A", status="done"),
               Concept(id="b", name="B", status="in-progress"),
               Concept(id="c", name="C")])
    a = build_agenda(s, profile(), TODAY, tmp_path)
    assert a.teach_concept.id == "b"


def test_teach_falls_back_to_frontier_then_none(tmp_path):
    s = state([Concept(id="a", name="A")])
    assert build_agenda(s, profile(), TODAY, tmp_path).teach_concept.id == "a"
    s2 = state([Concept(id="a", name="A", status="done")])
    assert build_agenda(s2, profile(), TODAY, tmp_path).teach_concept is None


def test_reviews_capped_by_profile(tmp_path):
    items = [item(f"it-{i}") for i in range(10)]
    s = state([Concept(id="a", name="A")], items)
    a = build_agenda(s, profile(max_reviews=6), TODAY, tmp_path)
    assert len(a.review_items) == 6


def test_pace_hint(tmp_path):
    s = state([Concept(id="a", name="A")], recent=["good"] * 10)
    assert build_agenda(s, profile(), TODAY, tmp_path).pace_hint == "push-harder"
    s = state([Concept(id="a", name="A")], recent=["again"] * 10)
    assert build_agenda(s, profile(), TODAY, tmp_path).pace_hint == "step-back"
    s = state([Concept(id="a", name="A")], recent=["skipped"] * 10)
    assert build_agenda(s, profile(), TODAY, tmp_path).pace_hint == "steady"


def test_briefing_scoped_notes_and_budget(tmp_path):
    notes = ("## a\n- note-a1\n- note-a2\n- note-a3\n- note-a4\n\n"
             "## zzz\n- irrelevant\n\n")
    s = state([Concept(id="a", name="A")], notes=notes)
    a = build_agenda(s, profile(), TODAY, tmp_path)
    assert "note-a1" in a.briefing and "irrelevant" not in a.briefing
    assert "note-a4" not in a.briefing  # max 3 newest per concept

    s2 = state([Concept(id="a", name="A")], notes="## a\n- " + "x" * 9000 + "\n")
    a2 = build_agenda(s2, profile(), TODAY, tmp_path)
    assert len(a2.briefing) <= 4100 and "(older notes omitted)" in a2.briefing


def test_resolve_excerpt(tmp_path):
    src = tmp_path / "blitz"
    src.mkdir()
    (src / "ch09.md").write_text("# 9.1 Intro\nalpha\n# 9.2 CondExp\nbeta\n")
    assert resolve_excerpt(tmp_path, "blitz/ch09.md#9.2", 1000).strip() == "# 9.2 CondExp\nbeta"
    assert "alpha" in resolve_excerpt(tmp_path, "blitz/ch09.md", 1000)
    assert resolve_excerpt(tmp_path, "blitz/missing.md", 1000) is None
    assert len(resolve_excerpt(tmp_path, "blitz/ch09.md", 10)) == 10


def test_deterministic(tmp_path):
    s = state([Concept(id="a", name="A")], [item("it-1")], recent=["good"])
    a1 = build_agenda(s, profile(), TODAY, tmp_path)
    a2 = build_agenda(s, profile(), TODAY, tmp_path)
    assert a1 == a2
