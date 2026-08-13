from datetime import date

from seba.models import Concept, GoalState, Item, SubjectProfile, Syllabus
from seba.scheduler.agenda import build_agenda, resolve_excerpt

TODAY = date(2026, 7, 3)


def profile(max_reviews=6):
    return SubjectProfile(
        name="probability",
        kind="technical",
        max_reviews_per_session=max_reviews,
        item_types=["recall", "apply"],
        session_shape="teach-heavy",
    )


def state(concepts, items=(), notes="", recent=(), by_concept=None, **kw):
    return GoalState(
        name="prob",
        subject="probability",
        syllabus=Syllabus(goal="prob", subject="probability", concepts=list(concepts)),
        items=list(items),
        notes=notes,
        session_number=kw.pop("session_number", 2),
        recent_grades=list(recent),
        recent_by_concept=by_concept or {},
        **kw,
    )


def item(id, due="2026-07-01T00:00:00+00:00", concept="a"):
    return Item(
        id=id,
        concept=concept,
        type="recall",
        front="f",
        back="b",
        fsrs={"due": due},
        created=TODAY,
    )


def test_teach_prefers_in_progress(tmp_path):
    s = state(
        [
            Concept(id="a", name="A", status="done"),
            Concept(id="b", name="B", status="in-progress"),
            Concept(id="c", name="C"),
        ]
    )
    a = build_agenda(s, profile(), TODAY, tmp_path)
    assert a.teach_concept.id == "b"


def test_teach_falls_back_to_frontier_then_none(tmp_path):
    s = state([Concept(id="a", name="A")])
    assert build_agenda(s, profile(), TODAY, tmp_path).teach_concept.id == "a"
    s2 = state([Concept(id="a", name="A", status="done")])
    assert build_agenda(s2, profile(), TODAY, tmp_path).teach_concept is None


def test_teach_passes_raw_source_locators_through(tmp_path):
    # A local markdown source is pre-loaded as text; a PDF and a URL locator
    # can't be pre-loaded but must still reach the tutor via teach.sources.
    (tmp_path / "blitz").mkdir()
    (tmp_path / "blitz" / "ch01.md").write_text("# 1.1\nlocal text\n")
    srcs = ["blitz/ch01.md#1.1", "algebra.pdf p.40-58", "https://ct.org/ch3"]
    s = state([Concept(id="a", name="A", sources=srcs)])
    teach = build_agenda(s, profile(), TODAY, tmp_path).teach_concept
    assert teach.sources == srcs  # all locators carried through, verbatim
    assert any("local text" in e for e in teach.source_excerpts)  # md pre-loaded
    assert len(teach.source_excerpts) == 1  # pdf + url not pre-loaded, only the md


def test_reviews_capped_by_profile(tmp_path):
    items = [item(f"it-{i}") for i in range(10)]
    s = state([Concept(id="a", name="A")], items)
    a = build_agenda(s, profile(max_reviews=6), TODAY, tmp_path)
    assert len(a.review_items) == 6


def test_pace_hint_drives_practice_quota(tmp_path):
    s = state([Concept(id="a", name="A")], recent=["good"] * 10)
    a = build_agenda(s, profile(), TODAY, tmp_path)
    assert (a.pace_hint, a.practice_quota) == ("push-harder", 5)
    s = state([Concept(id="a", name="A")], recent=["again"] * 10)
    a = build_agenda(s, profile(), TODAY, tmp_path)
    assert (a.pace_hint, a.practice_quota) == ("step-back", 2)
    s = state([Concept(id="a", name="A")], recent=["skipped"] * 10)
    a = build_agenda(s, profile(), TODAY, tmp_path)
    assert (a.pace_hint, a.practice_quota) == ("steady", 3)


def test_briefing_scoped_notes_and_budget(tmp_path):
    notes = (
        "## a\n- note-a1\n- note-a2\n- note-a3\n- note-a4\n\n## zzz\n- irrelevant\n\n"
    )
    s = state([Concept(id="a", name="A")], notes=notes)
    a = build_agenda(s, profile(), TODAY, tmp_path)
    assert "note-a1" in a.briefing and "irrelevant" not in a.briefing
    assert "note-a4" not in a.briefing  # max 3 newest per concept

    s2 = state([Concept(id="a", name="A")], notes="## a\n- " + "x" * 9000 + "\n")
    a2 = build_agenda(s2, profile(), TODAY, tmp_path)
    assert len(a2.briefing) <= 4100 and "(older notes omitted)" in a2.briefing


def test_briefing_lists_per_concept_recent_grades(tmp_path):
    s = state(
        [Concept(id="a", name="A")],
        by_concept={"a": ["again", "hard", "good"], "zzz": ["easy"]},
    )
    b = build_agenda(s, profile(), TODAY, tmp_path).briefing
    assert "[a] recent: again, hard, good" in b
    assert "zzz" not in b  # out of scope this session


def test_resolve_excerpt(tmp_path):
    src = tmp_path / "blitz"
    src.mkdir()
    (src / "ch09.md").write_text("# 9.1 Intro\nalpha\n# 9.2 CondExp\nbeta\n")
    assert (
        resolve_excerpt(tmp_path, "blitz/ch09.md#9.2", 1000).strip()
        == "# 9.2 CondExp\nbeta"
    )
    assert "alpha" in resolve_excerpt(tmp_path, "blitz/ch09.md", 1000)
    assert resolve_excerpt(tmp_path, "blitz/missing.md", 1000) is None
    assert len(resolve_excerpt(tmp_path, "blitz/ch09.md", 10)) == 10
    # a non-text file (e.g. a stray PDF) is skipped, not a crash
    (src / "book.pdf").write_bytes(b"%PDF-1.7\x00\x80\xff binary\x00")
    assert resolve_excerpt(tmp_path, "blitz/book.pdf", 1000) is None


FUTURE = "2027-01-01T00:00:00+00:00"  # not due


def test_reviews_widen_to_prereqs_and_error_sites(tmp_path):
    concepts = [
        Concept(id="a", name="A", status="done"),
        Concept(id="soft", name="S", status="done"),
        Concept(id="err", name="E", status="done"),
        Concept(id="b", name="B", prereqs=["a"], soft_prereqs=["soft"]),
    ]
    items = [
        item("it-due", concept="b"),
        item("it-a", due=FUTURE, concept="a"),
        item("it-soft", due=FUTURE, concept="soft"),
        item("it-err", due=FUTURE, concept="err"),
        item("it-none", due=FUTURE, concept="a2"),
    ]
    s = state(concepts, items, last_session_errors={"err"})
    ids = [r.id for r in build_agenda(s, profile(), TODAY, tmp_path).review_items]
    assert ids == ["it-due", "it-a", "it-err", "it-soft"]  # due first, then sorted


def test_widened_reviews_respect_cap_and_prefer_due(tmp_path):
    concepts = [
        Concept(id="a", name="A", status="done"),
        Concept(id="b", name="B", prereqs=["a"]),
    ]
    items = [item(f"it-{i}", concept="b") for i in range(3)]  # all due
    items += [item(f"it-a{i}", due=FUTURE, concept="a") for i in range(5)]
    a = build_agenda(state(concepts, items), profile(max_reviews=4), TODAY, tmp_path)
    ids = [r.id for r in a.review_items]
    assert len(ids) == 4 and len(set(ids)) == 4
    assert {"it-0", "it-1", "it-2"} <= set(ids)  # due keep priority under the cap


def test_no_duplicate_when_prereq_item_is_also_due(tmp_path):
    concepts = [
        Concept(id="a", name="A", status="done"),
        Concept(id="b", name="B", prereqs=["a"]),
    ]
    s = state(concepts, [item("it-a", concept="a")], last_session_errors={"a"})
    ids = [r.id for r in build_agenda(s, profile(), TODAY, tmp_path).review_items]
    assert ids == ["it-a"]


def test_briefing_names_unmastered_prereqs(tmp_path):
    concepts = [
        Concept(id="a", name="A", status="done"),
        Concept(id="cond", name="Cond"),
        Concept(id="indep", name="Indep"),
        Concept(id="soft", name="Soft"),
        Concept(
            id="b",
            name="B",
            status="in-progress",
            prereqs=["a", "cond", "indep"],
            soft_prereqs=["soft"],
        ),
    ]
    b = build_agenda(state(concepts), profile(), TODAY, tmp_path).briefing
    assert "prereqs not yet done: cond, indep — offer a short review" in b
    assert "soft prereqs not yet done (advisory): soft" in b
    assert "not yet done: a" not in b  # `a` is done


def test_stuck_check_threshold(tmp_path):
    concepts = [Concept(id="b", name="B", status="in-progress")]
    low = ["again", "again", "hard", "good", "skipped"]
    s = state(
        concepts, grades_by_concept={"b": low}, started_at={"b": 1}, session_number=4
    )
    b = build_agenda(s, profile(), TODAY, tmp_path).briefing
    assert (
        "stuck: [b] in progress for 3 session(s), correctness 0.25 over 4 graded" in b
    )
    assert "switch representation" in b

    # under 4 graded opportunities the signal is noise — stay silent
    s2 = state(concepts, grades_by_concept={"b": ["again", "again", "hard"]})
    assert "stuck:" not in build_agenda(s2, profile(), TODAY, tmp_path).briefing
    # and above the rate threshold, silent too
    s3 = state(concepts, grades_by_concept={"b": ["good", "good", "good", "again"]})
    assert "stuck:" not in build_agenda(s3, profile(), TODAY, tmp_path).briefing


def test_session_types(tmp_path):
    concepts = [
        Concept(id="a", name="A", status="done"),
        Concept(id="b", name="B", status="done"),
        Concept(id="c", name="C"),
    ]
    ordinary = build_agenda(state(concepts), profile(), TODAY, tmp_path)
    assert ordinary.session_type == "ordinary" and ordinary.teach_concept.id == "c"

    lapsed = build_agenda(
        state(concepts, last_session_date=date(2026, 6, 1)), profile(), TODAY, tmp_path
    )
    assert lapsed.session_type == "return-after-lapse"
    assert lapsed.teach_concept is None
    assert "return-after-lapse — 32 days since the last session" in lapsed.briefing

    synth = build_agenda(state(concepts, session_number=5), profile(), TODAY, tmp_path)
    assert synth.session_type == "synthesis" and synth.teach_concept is None
    assert "synthesis — no new concept" in synth.briefing

    # every 5th session, but fewer than 2 concepts done -> nothing to synthesise
    thin = [Concept(id="a", name="A", status="done"), Concept(id="c", name="C")]
    assert (
        build_agenda(
            state(thin, session_number=5), profile(), TODAY, tmp_path
        ).session_type
        == "ordinary"
    )


def test_deterministic(tmp_path):
    s = state([Concept(id="a", name="A")], [item("it-1")], recent=["good"])
    a1 = build_agenda(s, profile(), TODAY, tmp_path)
    a2 = build_agenda(s, profile(), TODAY, tmp_path)
    assert a1 == a2
