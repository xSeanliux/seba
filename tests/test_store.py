import subprocess
from datetime import date

import pytest
from seba.models import (
    Concept,
    GradeReview,
    Item,
    MintItem,
    SessionRecord,
    Status,
    Syllabus,
    UpdateConcept,
)
from seba.store.store import Store, StoreError, parse_notes


def syl():
    return Syllabus(
        goal="prob", subject="probability", concepts=[Concept(id="bayes", name="Bayes")]
    )


def item(due="2026-07-01"):
    return Item(
        id="it-1",
        concept="bayes",
        type="recall",
        front="f",
        back="b",
        fsrs={"due": due},
        created=date(2026, 6, 28),
    )


@pytest.fixture
def store(tmp_path):
    return Store(tmp_path / "data")


def test_create_and_load_roundtrip(store):
    store.create_goal("prob", syl(), "probability")
    gs = store.load_goal("prob")
    assert gs.subject == "probability" and gs.session_number == 1
    assert gs.items == [] and gs.last_hint is None


def test_create_duplicate_rejected(store):
    store.create_goal("prob", syl(), "probability")
    with pytest.raises(StoreError):
        store.create_goal("prob", syl(), "probability")


def test_save_session_roundtrip_and_git(store):
    store.create_goal("prob", syl(), "probability")
    gs = store.load_goal("prob")
    record = SessionRecord(
        reviews=[GradeReview(id="it-1", grade="good")],
        concepts=[
            UpdateConcept(id="bayes", status_change="started", note="shaky on priors")
        ],
        new_items=[MintItem(concept="bayes", type="recall", front="f", back="b")],
        summary="Taught Bayes.",
        next_session_hint="drill priors",
        complete=True,
    )
    updated = gs.model_copy(
        update={
            "items": [item()],
            "syllabus": gs.syllabus.model_copy(
                update={
                    "concepts": [
                        gs.syllabus.concepts[0].model_copy(
                            update={"status": Status.IN_PROGRESS}
                        )
                    ]
                }
            ),
        }
    )
    store.save_session("prob", record, "transcript text", updated)

    gs2 = store.load_goal("prob")
    assert gs2.session_number == 2
    assert gs2.last_hint == "drill priors"
    assert gs2.recent_grades == ["good"]
    assert gs2.items[0].id == "it-1"
    assert gs2.syllabus.concepts[0].status == "in-progress"
    assert "shaky on priors" in gs2.notes

    gdir = store.data_dir / "goals" / "prob" / "sessions"
    assert (gdir / "001.md").exists()
    assert (gdir / "001.outcomes.yaml").exists()
    assert (gdir / "001.transcript.md").exists()
    log = subprocess.run(
        ["git", "log", "--oneline"], cwd=store.data_dir, capture_output=True, text=True
    ).stdout
    assert "prob: session 001" in log


def test_incomplete_marker(store):
    store.create_goal("prob", syl(), "probability")
    gs = store.load_goal("prob")
    store.save_session("prob", SessionRecord(complete=False), "t", gs)
    body = (store.data_dir / "goals" / "prob" / "sessions" / "001.md").read_text()
    assert "INCOMPLETE" in body


def test_list_goals_due_count(store):
    store.create_goal("prob", syl(), "probability")
    gs = store.load_goal("prob")
    updated = gs.model_copy(update={"items": [item(due="2020-01-01")]})
    store.save_session(
        "prob",
        SessionRecord(complete=True, summary="s", next_session_hint="h"),
        "t",
        updated,
    )
    [summary] = store.list_goals()
    assert summary.due_count == 1 and summary.session_count == 1


def test_malformed_items_named(store):
    store.create_goal("prob", syl(), "probability")
    (store.data_dir / "goals" / "prob" / "items.jsonl").write_text("not json\n")
    with pytest.raises(StoreError, match="items.jsonl"):
        store.load_goal("prob")


def test_recent_grades_keyed_by_concept(store):
    store.create_goal("prob", syl(), "probability")
    gs = store.load_goal("prob")
    record = SessionRecord(
        reviews=[
            GradeReview(id="it-1", grade="again"),
            GradeReview(id="it-gone", grade="good"),
        ],
        complete=True,
    )
    store.save_session("prob", record, "t", gs.model_copy(update={"items": [item()]}))
    gs2 = store.load_goal("prob")
    assert gs2.recent_by_concept == {"bayes": ["again"]}  # deleted item skipped
    assert gs2.recent_grades == ["again", "good"]  # global pool unchanged


def test_delayed_pass_needs_a_later_session(store):
    store.create_goal("prob", syl(), "probability")
    gs = store.load_goal("prob").model_copy(update={"items": [item()]})
    started = SessionRecord(
        reviews=[GradeReview(id="it-1", grade="good")],
        concepts=[UpdateConcept(id="bayes", status_change="started")],
        complete=True,
    )
    store.save_session("prob", started, "t", gs)
    assert store.load_goal("prob").delayed_pass == set()  # same session doesn't count

    store.save_session(
        "prob",
        SessionRecord(reviews=[GradeReview(id="it-1", grade="easy")], complete=True),
        "t",
        gs,
    )
    gs2 = store.load_goal("prob")
    assert gs2.delayed_pass == {"bayes"}
    assert gs2.recent_by_item == {"it-1": ["good", "easy"]}  # last two only


def test_last_session_date_and_error_sites(store):
    store.create_goal("prob", syl(), "probability")
    gs = store.load_goal("prob").model_copy(update={"items": [item()]})
    store.save_session(
        "prob",
        SessionRecord(reviews=[GradeReview(id="it-1", grade="again")], complete=True),
        "t",
        gs,
    )
    gs2 = store.load_goal("prob")
    assert gs2.last_session_date == date.today()  # stamped on save, not file mtime
    assert gs2.last_session_errors == {"bayes"}
    assert gs2.grades_by_concept == {"bayes": ["again"]}

    # errors are the LAST session's only
    store.save_session(
        "prob",
        SessionRecord(reviews=[GradeReview(id="it-1", grade="good")], complete=True),
        "t",
        gs,
    )
    gs3 = store.load_goal("prob")
    assert gs3.last_session_errors == set()
    assert gs3.grades_by_concept == {"bayes": ["again", "good"]}


def test_parse_notes():
    text = "## bayes\n- shaky on priors\n\n## sigma\n- fine\n"
    assert parse_notes(text) == {"bayes": ["- shaky on priors"], "sigma": ["- fine"]}
