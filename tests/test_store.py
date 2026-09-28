import subprocess
from datetime import date

import yaml
import pytest
from seba.models import (
    Concept,
    Emphasis,
    GoalSettings,
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


def test_passes_count_later_sessions(store):
    store.create_goal("prob", syl(), "probability")
    gs = store.load_goal("prob").model_copy(update={"items": [item()]})
    started = SessionRecord(
        reviews=[GradeReview(id="it-1", grade="good")],
        concepts=[UpdateConcept(id="bayes", status_change="started")],
        complete=True,
    )
    store.save_session("prob", started, "t", gs)
    assert store.load_goal("prob").passes == {"bayes": 0}  # same session: no

    _save(store, gs, GradeReview(id="it-1", grade="easy"))
    gs2 = store.load_goal("prob")
    assert gs2.passes == {"bayes": 1}
    assert gs2.again_runs == {}

    _save(store, gs, GradeReview(id="it-1", grade="hard", note="one hint"))
    assert store.load_goal("prob").passes == {"bayes": 1}  # a pass is good or easy

    again_started = SessionRecord(
        reviews=[GradeReview(id="it-1", grade="good")],
        concepts=[UpdateConcept(id="bayes", status_change="started")],
        complete=True,
    )
    store.save_session("prob", again_started, "t", gs)
    assert store.load_goal("prob").passes == {"bayes": 2}  # re-recorded start


def test_reopening_restarts_the_pass_count(store):
    store.create_goal("prob", syl(), "probability")
    gs = store.load_goal("prob").model_copy(update={"items": [item()]})
    store.save_session(
        "prob",
        SessionRecord(
            concepts=[UpdateConcept(id="bayes", status_change="started")],
            complete=True,
        ),
        "t",
        gs,
    )
    _save(store, gs, GradeReview(id="it-1", grade="good"))
    assert store.load_goal("prob").passes == {"bayes": 1}
    store.save_session(
        "prob",
        SessionRecord(
            reviews=[GradeReview(id="it-1", grade="good")],
            concepts=[UpdateConcept(id="bayes", status_change="reopened")],
            complete=True,
        ),
        "t",
        gs,
    )
    assert store.load_goal("prob").passes == {"bayes": 0}
    _save(store, gs, GradeReview(id="it-1", grade="good"))
    assert store.load_goal("prob").passes == {"bayes": 1}


def test_a_concept_never_started_has_no_passes(store):
    store.create_goal("prob", syl(), "probability")
    gs = store.load_goal("prob").model_copy(update={"items": [item()]})
    _save(store, gs, GradeReview(id="it-1", grade="good"))
    assert store.load_goal("prob").passes == {}


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


def test_historical_completed_without_evidence_still_loads(tmp_path):
    # `evidence` is required on new `completed` calls, but outcomes written
    # before the field existed must stay readable — enforcing it on the model
    # instead of the tool handler made every pre-existing goal unloadable.
    store = Store(tmp_path)
    syl = Syllabus(
        goal="g", subject="probability", concepts=[Concept(id="a", name="A")]
    )
    store.create_goal("g", syl, "probability")
    old = {
        "reviews": [],
        "concepts": [{"id": "a", "status_change": "completed", "note": None}],
        "new_items": [],
        "complete": True,
    }
    (tmp_path / "goals/g/sessions/001.outcomes.yaml").write_text(yaml.safe_dump(old))
    assert store.load_goal("g").session_number == 2


def _goal_yaml(store):
    return store.data_dir / "goals" / "prob" / "goal.yaml"


def _commits(store):
    return subprocess.run(
        ["git", "log", "--oneline"], cwd=store.data_dir, capture_output=True, text=True
    ).stdout.splitlines()


def test_goal_without_a_settings_block_loads_defaults(store):
    store.create_goal("prob", syl(), "probability")
    gs = store.load_goal("prob")
    assert gs.settings == GoalSettings() and gs.emphasis == {}


def test_save_tuning_roundtrip(store):
    store.create_goal("prob", syl(), "probability")
    settings = GoalSettings(desired_retention=0.85, max_interval_days=120)
    assert store.save_tuning("prob", settings, {"bayes": Emphasis.MORE}, [item()])
    gs = store.load_goal("prob")
    assert gs.settings == settings
    assert gs.emphasis == {"bayes": "more"}
    assert gs.items[0].id == "it-1" and gs.subject == "probability"
    assert "prob: tuned" in _commits(store)[0]


def test_save_tuning_does_not_commit_when_nothing_changed(store):
    store.create_goal("prob", syl(), "probability")
    settings = GoalSettings(desired_retention=0.85)
    assert store.save_tuning("prob", settings, {}, [])
    before = _commits(store)
    assert store.save_tuning("prob", settings, {}, []) is False
    assert _commits(store) == before


def test_save_tuning_keeps_unknown_keys(store):
    store.create_goal("prob", syl(), "probability")
    path = _goal_yaml(store)
    path.write_text(path.read_text() + "colour: teal\n")
    store.save_tuning("prob", GoalSettings(), {}, [])
    assert yaml.safe_load(path.read_text())["colour"] == "teal"


@pytest.mark.parametrize(
    "block",
    [
        "settings:\n  desired_retention: 2.0\n",
        "settings:\n  desired_retention: banana\n",
        "settings:\n  max_interval_days: 0\n",
        "settings: nonsense\n",
        "emphasis:\n  bayes: lots\n",
    ],
)
def test_malformed_goal_yaml_names_the_file(store, block):
    store.create_goal("prob", syl(), "probability")
    path = _goal_yaml(store)
    path.write_text(path.read_text() + block)
    with pytest.raises(StoreError, match="goal.yaml"):
        store.load_goal("prob")


def test_emphasis_on_an_unknown_concept_is_ignored_at_load(store):
    store.create_goal("prob", syl(), "probability")
    path = _goal_yaml(store)
    path.write_text(path.read_text() + "emphasis:\n  ghost: more\n  bayes: less\n")
    assert store.load_goal("prob").emphasis == {"bayes": "less"}


def _save(store, gs, *reviews):
    store.save_session(
        "prob", SessionRecord(reviews=list(reviews), complete=True), "t", gs
    )


def test_hard_is_not_an_error_site(store):
    store.create_goal("prob", syl(), "probability")
    gs = store.load_goal("prob").model_copy(update={"items": [item()]})
    _save(store, gs, GradeReview(id="it-1", grade="hard", note="needed the formula"))
    gs2 = store.load_goal("prob")
    assert gs2.last_session_errors == set()
    assert gs2.last_trouble == [
        GradeReview(id="it-1", grade="hard", note="needed the formula")
    ]
    assert gs2.again_runs == {}


def test_again_runs_count_the_trailing_run(store):
    store.create_goal("prob", syl(), "probability")
    gs = store.load_goal("prob").model_copy(update={"items": [item()]})
    _save(store, gs, GradeReview(id="it-1", grade="again", note="blanked"))
    assert store.load_goal("prob").again_runs == {"it-1": 1}
    _save(store, gs, GradeReview(id="it-1", grade="skipped"))  # ignored
    _save(store, gs, GradeReview(id="it-1", grade="again", note="blanked again"))
    gs3 = store.load_goal("prob")
    assert gs3.again_runs == {"it-1": 2}
    assert [r.note for r in gs3.last_trouble] == ["blanked again"]
    assert gs3.last_session_errors == {"bayes"}
    _save(store, gs, GradeReview(id="it-1", grade="hard", note="one hint"))
    assert store.load_goal("prob").again_runs == {}  # a pass resets it


def test_last_trouble_is_the_last_session_only(store):
    store.create_goal("prob", syl(), "probability")
    gs = store.load_goal("prob").model_copy(update={"items": [item()]})
    _save(store, gs, GradeReview(id="it-1", grade="again", note="blanked"))
    _save(store, gs, GradeReview(id="it-1", grade="good"))
    assert store.load_goal("prob").last_trouble == []


def test_old_outcomes_without_notes_still_load(store):
    store.create_goal("prob", syl(), "probability")
    gs = store.load_goal("prob").model_copy(update={"items": [item()]})
    _save(store, gs, GradeReview(id="it-1", grade="again"))  # as written before
    gs2 = store.load_goal("prob")
    assert gs2.last_trouble[0].note is None and gs2.again_runs == {"it-1": 1}
