from datetime import date
from pathlib import Path

import pytest
import yaml
from fsrs import Card
from typer.testing import CliRunner

from seba.cli import app
from seba.models import (
    Agenda,
    Concept,
    GoalState,
    GradeReview,
    Item,
    SessionRecord,
    Status,
    SubjectProfile,
    Syllabus,
    UpdateConcept,
)
from seba.scheduler.agenda import build_agenda
from seba.scheduler.apply import apply_change
from seba.session.tools import ToolHandler
from seba.store.store import Store
from seba.syllabus.graph import SyllabusError, drop, restore

TODAY = date(2026, 7, 3)
DUE = "2026-07-01T00:00:00+00:00"
runner = CliRunner()


def syl(*concepts: Concept) -> Syllabus:
    return Syllabus(goal="g", subject="probability", concepts=list(concepts))


def status_of(s: Syllabus, cid: str) -> Status:
    return next(c for c in s.concepts if c.id == cid).status


def chain() -> Syllabus:
    """a <- b (hard), a <- c (soft), a ~ d (confusable)."""
    return syl(
        Concept(id="a", name="A", status=Status.DONE),
        Concept(id="b", name="B", prereqs=["a"]),
        Concept(id="c", name="C", soft_prereqs=["a"]),
        Concept(id="d", name="D", confusable_with=["a"]),
    )


# graph


def test_drop_records_the_status_it_had_and_restore_returns_it():
    for before in (Status.IN_PROGRESS, Status.DONE, Status.UNSEEN):
        s = syl(Concept(id="x", name="X", status=before))
        dropped = drop(s, "x")
        assert dropped.concepts[0].status == "dropped"
        assert dropped.concepts[0].dropped_from == before
        back = restore(dropped, "x")
        assert back.concepts[0].status == before
        assert back.concepts[0].dropped_from is None


def test_restore_without_dropped_from_is_unseen():
    s = syl(Concept(id="x", name="X", status=Status.DROPPED))
    assert restore(s, "x").concepts[0].status == "unseen"


def test_drop_refusals():
    with pytest.raises(SyllabusError, match="unknown concept: 'ghost'"):
        drop(chain(), "ghost")
    with pytest.raises(SyllabusError, match="'b' is already dropped"):
        drop(drop(chain(), "b"), "b")


def test_a_live_dependent_blocks_a_drop_until_it_is_dropped():
    s = syl(
        Concept(id="a", name="A"),
        Concept(id="b", name="B", prereqs=["a"], status=Status.DONE),
        Concept(id="e", name="E", prereqs=["a"]),
    )
    msg = (
        "cannot drop 'a': b, e depend on it — drop them first, "
        "or remove the edge in syllabus.yaml"
    )
    with pytest.raises(SyllabusError) as e:
        drop(s, "a")
    assert str(e.value) == msg  # a done dependent still blocks
    s = drop(drop(s, "b"), "e")
    assert status_of(drop(s, "a"), "a") == "dropped"


def test_soft_prereqs_and_confusables_never_block_a_drop():
    s = syl(
        Concept(id="a", name="A"),
        Concept(id="c", name="C", soft_prereqs=["a"]),
        Concept(id="d", name="D", confusable_with=["a"]),
    )
    assert status_of(drop(s, "a"), "a") == "dropped"


def test_restore_refusals():
    with pytest.raises(SyllabusError) as e:
        restore(chain(), "b")
    assert str(e.value) == "'b' is unseen; only a dropped concept can be restored"
    s = drop(drop(chain(), "b"), "a")
    with pytest.raises(SyllabusError) as e:
        restore(s, "b")
    assert str(e.value) == (
        "cannot restore 'b': it depends on a, which is dropped — restore that first"
    )
    with pytest.raises(SyllabusError, match="unknown concept: 'ghost'"):
        restore(s, "ghost")


def test_moves_on_a_dropped_concept_are_refused():
    s = drop(chain(), "b")
    for move in ("started", "completed", "reopened"):
        with pytest.raises(SyllabusError, match="'b' is dropped; restore it first"):
            apply_change(s, UpdateConcept(id="b", status_change=move))


# apply_change


def test_apply_change_adds_a_source_once_with_or_without_a_status():
    s = syl(Concept(id="x", name="X", sources=["p.md"]))
    s = apply_change(s, UpdateConcept(id="x", add_source="q.md"))
    s = apply_change(s, UpdateConcept(id="x", add_source="q.md"))
    assert s.concepts[0].sources == ["p.md", "q.md"]
    s = apply_change(
        s, UpdateConcept(id="x", status_change="dropped", add_source="r.md")
    )
    assert s.concepts[0].status == "dropped"
    assert s.concepts[0].sources == ["p.md", "q.md", "r.md"]


def test_a_repeated_status_is_no_move_and_still_adds_its_source():
    for status, move in ((Status.IN_PROGRESS, "started"), (Status.DONE, "completed")):
        s = syl(Concept(id="x", name="X", status=status))
        s = apply_change(
            s, UpdateConcept(id="x", status_change=move, add_source="p.md")
        )
        assert s.concepts[0].status == status
        assert s.concepts[0].sources == ["p.md"]
    s = syl(Concept(id="x", name="X", status=Status.IN_PROGRESS))
    with pytest.raises(SyllabusError, match="in-progress -> in-progress"):
        apply_change(s, UpdateConcept(id="x", status_change="reopened"))


# handler


def handler(s: Syllabus, tmp_path: Path) -> ToolHandler:
    agenda = Agenda(
        goal="g",
        subject="probability",
        session_number=1,
        briefing="",
        review_items=[],
        teach_concept=None,
        practice_quota=3,
        pace_hint="steady",
    )
    return ToolHandler(agenda, s, tmp_path, 6, {"b": 5}, 1, set())


def update(h: ToolHandler, **args: str) -> tuple[str, bool]:
    return h.handle("update_concept", {"id": "b", **args})


def test_handler_drop_then_restore_ends_where_it_began(tmp_path):
    h = handler(chain(), tmp_path)
    assert update(h, status_change="started") == ("recorded", False)
    assert update(h, status_change="dropped") == ("recorded", False)
    recorded = len(h.record.concepts)
    for move in ("started", "completed", "reopened"):
        text, err = update(h, status_change=move, evidence="x")
        assert err and text == "'b' is dropped; restore it first", move
    assert len(h.record.concepts) == recorded
    text, err = update(h, status_change="dropped")
    assert err and text == "'b' is already dropped"
    assert update(h, status_change="restored") == ("recorded", False)
    assert status_of(h.effective(), "b") == "in-progress"
    assert update(h, status_change="dropped") == ("recorded", False)
    assert status_of(h.effective(), "b") == "dropped"


def test_handler_refuses_a_drop_with_a_live_dependent(tmp_path):
    h = handler(chain(), tmp_path)
    text, err = h.handle("update_concept", {"id": "a", "status_change": "dropped"})
    assert err and "b depend on it" in text
    assert h.record.concepts == []


def test_handler_refuses_a_repeated_or_blank_source(tmp_path):
    h = handler(chain(), tmp_path)
    text, err = update(h, add_source="  ")
    assert err and text == "--add-source needs a locator"
    assert update(h, add_source="p.md#Intro") == ("recorded", False)
    text, err = update(h, add_source="p.md#Intro")
    assert err and text == "'p.md#Intro' is already a source of 'b'"


def test_a_source_with_a_repeated_status_is_kept(tmp_path):
    h = handler(chain(), tmp_path)
    update(h, status_change="started")
    assert update(h, status_change="started", add_source="p.md") == (
        "recorded",
        False,
    )
    assert next(c for c in h.effective().concepts if c.id == "b").sources == ["p.md"]
    assert [(c.status_change, c.add_source) for c in h.record.concepts] == [
        ("started", None),
        ("started", "p.md"),
    ]


def test_handler_refuses_minting_for_a_concept_dropped_this_session(tmp_path):
    h = handler(chain(), tmp_path)
    update(h, status_change="dropped")
    text, err = h.handle(
        "mint_item", {"concept": "b", "type": "recall", "front": "f", "back": "b"}
    )
    assert err and text == "'b' is dropped; restore it before minting a card for it"


# agenda and store


def profile() -> SubjectProfile:
    return SubjectProfile(
        name="probability",
        kind="technical",
        max_reviews_per_session=6,
        item_types=["recall"],
        session_shape="teach-heavy",
    )


def card(id: str, concept: str) -> Item:
    return Item(
        id=id,
        concept=concept,
        type="recall",
        front="f",
        back="b",
        fsrs={"due": DUE},
        created=TODAY,
    )


def goal_state(s: Syllabus) -> GoalState:
    return GoalState(
        name="g",
        subject="probability",
        syllabus=s,
        items=[card("it-b", "b"), card("it-a", "a")],
        notes="",
        session_number=2,
        last_session_errors=["b"],
        last_trouble=[GradeReview(id="it-b", grade="again", note="slip")],
    )


def test_a_dropped_concept_is_neither_reviewed_nor_taught(tmp_path):
    s = apply_change(chain(), UpdateConcept(id="b", status_change="started"))
    s = drop(s, "b")
    agenda = build_agenda(goal_state(s), profile(), TODAY, tmp_path)
    assert [r.id for r in agenda.review_items] == ["it-a"]
    assert agenda.teach_concept is None or agenda.teach_concept.id != "b"
    assert "slipped:" not in agenda.briefing

    agenda = build_agenda(goal_state(restore(s, "b")), profile(), TODAY, tmp_path)
    assert {r.id for r in agenda.review_items} == {"it-a", "it-b"}
    assert agenda.teach_concept is not None and agenda.teach_concept.id == "b"
    assert "slipped: [b] it-b" in agenda.briefing


def test_due_count_excludes_a_dropped_concept(tmp_path):
    store = Store(tmp_path)
    store.create_goal("g", drop(chain(), "b"), "probability")
    gs = store.load_goal("g")
    items = [
        i.model_copy(update={"fsrs": Card().to_dict() | {"due": DUE}})
        for i in goal_state(gs.syllabus).items
    ]
    store.save_session(
        "g",
        SessionRecord(complete=True, summary="s", next_session_hint="h"),
        "t",
        gs.model_copy(update={"items": items}),
    )
    assert store.list_goals()[0].due_count == 1


# CLI, one process per command


def seed(data: Path) -> Store:
    store = Store(data)
    store.create_goal(
        "prob",
        Syllabus(
            goal="prob",
            subject="probability",
            concepts=[
                Concept(id="bayes", name="Bayes", status=Status.IN_PROGRESS),
                Concept(id="other", name="Other"),
            ],
        ),
        "probability",
    )
    gs = store.load_goal("prob")
    item = card("it-1", "bayes").model_copy(
        update={"fsrs": Card().to_dict() | {"due": "2020-01-01T00:00:00+00:00"}}
    )
    store.save_session(
        "prob",
        SessionRecord(complete=True, summary="seed", next_session_hint="seed"),
        "t",
        gs.model_copy(update={"items": [item]}),
    )
    return store


def ok(*args: str) -> str:
    result = runner.invoke(app, list(args))
    assert result.exit_code == 0, result.output
    return result.output


def agenda() -> dict:
    return yaml.safe_load(ok("start", "prob"))["agenda"]


def end() -> None:
    ok("end", "prob", "--summary", "s", "--hint", "h")


def test_drop_and_restore_across_sessions(monkeypatch, tmp_path):
    data = tmp_path / "data"
    monkeypatch.setenv("SEBA_DATA_DIR", str(data))
    store = seed(data)
    due_before = store.load_goal("prob").items[0].fsrs["due"]

    assert agenda()["teach_concept"]["id"] == "bayes"
    ok("concept", "prob", "bayes", "--status", "dropped")
    ok("grade", "prob", "it-1", "skipped")
    end()

    a = agenda()
    assert a["review_items"] == [] and a["teach_concept"]["id"] == "other"
    ok("concept", "prob", "bayes", "--status", "restored")
    end()

    a = agenda()
    assert [r["id"] for r in a["review_items"]] == ["it-1"]
    assert a["teach_concept"]["id"] == "bayes"
    assert store.load_goal("prob").items[0].fsrs["due"] == due_before


def test_add_source_reaches_syllabus_and_agenda(monkeypatch, tmp_path):
    data = tmp_path / "data"
    monkeypatch.setenv("SEBA_DATA_DIR", str(data))
    seed(data)
    agenda()
    ok("concept", "prob", "bayes", "--add-source", "papers/x.md#Intro")
    ok("grade", "prob", "it-1", "skipped")
    end()
    raw = yaml.safe_load((data / "goals" / "prob" / "syllabus.yaml").read_text())
    assert raw["concepts"][0]["sources"] == ["papers/x.md#Intro"]
    assert agenda()["teach_concept"]["sources"] == ["papers/x.md#Intro"]
