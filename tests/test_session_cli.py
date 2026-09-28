from datetime import date

import yaml
from fsrs import Card
from typer.testing import CliRunner

from seba.cli import app
from seba.models import (
    Concept,
    Item,
    SessionRecord,
    Status,
    Syllabus,
    UpdateConcept,
)
from seba.store.store import Store

runner = CliRunner()


def _fsrs(due="2020-01-01T00:00:00+00:00"):
    d = Card().to_dict()
    d["due"] = due
    return d


def seed(data_dir, with_item=True):
    """Create goal 'prob'; optionally seed one long-overdue item."""
    store = Store(data_dir)
    store.create_goal(
        "prob",
        Syllabus(
            goal="prob",
            subject="probability",
            concepts=[Concept(id="bayes", name="Bayes")],
        ),
        "probability",
    )
    if with_item:
        gs = store.load_goal("prob")
        item = Item(
            id="it-1",
            concept="bayes",
            type="recall",
            front="State Bayes",
            back="P(A|B)=...",
            fsrs=_fsrs(),
            created=date(2026, 1, 1),
        )
        store.save_session(
            "prob",
            SessionRecord(complete=True, summary="seed", next_session_hint="seed"),
            "t",
            gs.model_copy(update={"items": [item]}),
        )
    return store


def env(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBA_DATA_DIR", str(tmp_path / "data"))
    return tmp_path / "data"


def test_start_creates_pending_and_prints_agenda(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    seed(data)
    result = runner.invoke(app, ["start", "prob"])
    assert result.exit_code == 0
    out = yaml.safe_load(result.output)
    assert out["ungraded_reviews"] == ["it-1"]
    assert out["agenda"]["review_items"][0]["front"] == "State Bayes"
    assert "σ-algebra" in out["subject_style"]
    assert (data / "goals" / "prob" / "session.pending.yaml").exists()


def test_start_resumes_existing_pending(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    seed(data)
    runner.invoke(app, ["start", "prob"])
    runner.invoke(app, ["grade", "prob", "it-1", "good"])
    result = runner.invoke(app, ["start", "prob"])
    assert result.exit_code == 0 and "resuming" in result.output
    out = yaml.safe_load(result.output.split("\n", 1)[1])  # skip the resuming line
    assert out["already_graded"] == ["it-1"] and out["ungraded_reviews"] == []


def test_malformed_pending_fails_cleanly(monkeypatch, tmp_path):
    from seba.session.pending import PendingError

    data = env(monkeypatch, tmp_path)
    seed(data)
    runner.invoke(app, ["start", "prob"])
    (data / "goals" / "prob" / "session.pending.yaml").write_text("not: [valid: yaml")
    result = runner.invoke(app, ["grade", "prob", "it-1", "good"])
    assert result.exit_code == 1
    assert not isinstance(result.exception, PendingError)  # clean exit, no traceback
    assert "session.pending.yaml" in result.output


def test_malformed_goal_yaml_fails_cleanly(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    seed(data)
    path = data / "goals" / "prob" / "goal.yaml"
    path.write_text(path.read_text() + "settings:\n  desired_retention: banana\n")
    for cmd in (["start", "prob"], ["view", "prob", "--json"], ["status"]):
        result = runner.invoke(app, cmd)
        assert result.exit_code == 1, cmd
        assert "goal.yaml" in result.output
        assert "Traceback" not in result.output
        assert result.exception is None or isinstance(result.exception, SystemExit)


def test_resume_without_subject_profile(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    seed(data)
    runner.invoke(app, ["start", "prob"])  # builds pending while profile exists
    # profile vanishes mid-session; resume must not need it
    monkeypatch.setattr("seba.config.subjects_dirs", lambda: [tmp_path / "none"])
    result = runner.invoke(app, ["start", "prob"])
    assert result.exit_code == 0 and "resuming" in result.output


def test_grade_records_and_rejects_duplicates_and_unknowns(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    seed(data)
    runner.invoke(app, ["start", "prob"])
    assert runner.invoke(app, ["grade", "prob", "it-1", "good"]).exit_code == 0
    assert runner.invoke(app, ["grade", "prob", "it-1", "easy"]).exit_code == 1
    assert runner.invoke(app, ["grade", "prob", "it-99", "good"]).exit_code == 1
    assert runner.invoke(app, ["grade", "prob", "it-1", "great"]).exit_code == 1


def test_commands_without_pending_fail_with_hint(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    seed(data)
    for args in (
        ["grade", "prob", "it-1", "good"],
        [
            "mint",
            "prob",
            "--concept",
            "bayes",
            "--type",
            "recall",
            "--front",
            "f",
            "--back",
            "b",
        ],
        ["concept", "prob", "bayes", "--note", "n"],
        ["end", "prob", "--summary", "s", "--hint", "h"],
    ):
        result = runner.invoke(app, args)
        assert result.exit_code == 1
        assert "seba start" in (result.output + str(result.exception or ""))


def test_end_gate_then_success(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    store = seed(data)
    runner.invoke(app, ["start", "prob"])
    blocked = runner.invoke(app, ["end", "prob", "--summary", "s", "--hint", "h"])
    assert blocked.exit_code == 1 and "it-1" in (
        blocked.output + str(blocked.exception or "")
    )

    runner.invoke(app, ["grade", "prob", "it-1", "good"])
    runner.invoke(
        app,
        [
            "mint",
            "prob",
            "--concept",
            "bayes",
            "--type",
            "recall",
            "--front",
            "nf",
            "--back",
            "nb",
        ],
    )
    runner.invoke(
        app,
        [
            "concept",
            "prob",
            "bayes",
            "--status",
            "started",
            "--note",
            "shaky on priors",
        ],
    )
    done = runner.invoke(
        app, ["end", "prob", "--summary", "Reviewed Bayes.", "--hint", "drill priors"]
    )
    assert done.exit_code == 0

    assert not (data / "goals" / "prob" / "session.pending.yaml").exists()
    gs = store.load_goal("prob")
    assert gs.last_hint == "drill priors"
    assert "shaky on priors" in gs.notes
    assert len(gs.items) == 2  # original + minted
    assert gs.syllabus.concepts[0].status == "in-progress"
    sessions = data / "goals" / "prob" / "sessions"
    assert (sessions / "002.md").exists()
    assert "INCOMPLETE" not in (sessions / "002.md").read_text()
    assert "Claude Code" in (sessions / "002.transcript.md").read_text()


def test_abandon_discard(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    seed(data)
    runner.invoke(app, ["start", "prob"])
    runner.invoke(app, ["grade", "prob", "it-1", "good"])
    result = runner.invoke(app, ["abandon", "prob", "--discard"])
    assert result.exit_code == 0
    assert not (data / "goals" / "prob" / "session.pending.yaml").exists()
    assert not (data / "goals" / "prob" / "sessions" / "002.md").exists()


def test_abandon_saves_incomplete(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    seed(data)
    runner.invoke(app, ["start", "prob"])
    runner.invoke(app, ["grade", "prob", "it-1", "good"])
    result = runner.invoke(app, ["abandon", "prob"])
    assert result.exit_code == 0
    assert not (data / "goals" / "prob" / "session.pending.yaml").exists()
    body = (data / "goals" / "prob" / "sessions" / "002.md").read_text()
    assert "INCOMPLETE" in body


AWKWARD = 'mixed up "σ-algebra"\nwith a topology — perché?'


def _finish_session(*grade_args):
    assert runner.invoke(app, ["start", "prob"]).exit_code == 0
    result = runner.invoke(app, ["grade", "prob", "it-1", *grade_args])
    assert result.exit_code == 0, result.output
    result = runner.invoke(app, ["end", "prob", "--summary", "s", "--hint", "h"])
    assert result.exit_code == 0, result.output


def _briefing():
    result = runner.invoke(app, ["start", "prob"])
    assert result.exit_code == 0, result.output
    return yaml.safe_load(result.output)["agenda"]


def test_grade_hard_without_a_note_is_refused(monkeypatch, tmp_path):
    seed(env(monkeypatch, tmp_path))
    runner.invoke(app, ["start", "prob"])
    result = runner.invoke(app, ["grade", "prob", "it-1", "hard"])
    assert result.exit_code == 1 and "--note" in result.output
    result = runner.invoke(app, ["grade", "prob", "it-1", "hard", "--note", "  "])
    assert result.exit_code == 1


def test_a_hard_note_reaches_the_next_briefing(monkeypatch, tmp_path):
    seed(env(monkeypatch, tmp_path))
    _finish_session("hard", "--note", AWKWARD)
    agenda = _briefing()
    assert f'hard: [bayes] it-1, passed with help — "{AWKWARD}".' in agenda["briefing"]
    # a `hard`-only session pulls no extra cards into the next
    assert agenda["review_items"] == []


def _mark_done(store):
    gs = store.load_goal("prob")
    done = gs.syllabus.model_copy(
        update={
            "concepts": [
                gs.syllabus.concepts[0].model_copy(update={"status": Status.DONE})
            ]
        }
    )
    store.save_session(
        "prob",
        SessionRecord(complete=True, summary="s", next_session_hint="h"),
        "t",
        gs.model_copy(update={"syllabus": done}),
    )


def _status(store):
    return store.load_goal("prob").syllabus.concepts[0].status


def test_a_slipping_card_is_reported_and_nothing_reopens(monkeypatch, tmp_path):
    store = seed(env(monkeypatch, tmp_path))
    _mark_done(store)

    _finish_session("again", "--note", "confused e with x⁻¹")
    assert _status(store) == "done"
    agenda = _briefing()
    assert "slipped: [bayes] it-1, 1 session running" in agenda["briefing"]
    assert "confused e with x⁻¹" in agenda["briefing"]
    assert [r["id"] for r in agenda["review_items"]] == ["it-1"]  # pulled in early

    _finish_session("again", "--note", "same slip")
    assert _status(store) == "done"
    assert "slipped: [bayes] it-1, 2 sessions running" in _briefing()["briefing"]

    _finish_session("good")
    assert "slipped:" not in _briefing()["briefing"]


def test_reopening_is_a_command(monkeypatch, tmp_path):
    store = seed(env(monkeypatch, tmp_path))
    runner.invoke(app, ["start", "prob"])
    result = runner.invoke(app, ["concept", "prob", "bayes", "--status", "reopened"])
    assert result.exit_code == 1 and "only a done concept" in result.output
    runner.invoke(app, ["abandon", "prob", "--discard"])

    _mark_done(store)
    runner.invoke(app, ["start", "prob"])
    result = runner.invoke(app, ["concept", "prob", "bayes", "--status", "reopened"])
    assert result.exit_code == 0, result.output
    runner.invoke(app, ["grade", "prob", "it-1", "good"])
    runner.invoke(app, ["end", "prob", "--summary", "s", "--hint", "h"])
    assert _status(store) == "in-progress"
    assert _briefing()["teach_concept"]["id"] == "bayes"  # takes the teaching slot


def test_a_reopened_concept_cannot_complete_in_the_same_session(monkeypatch, tmp_path):
    store = seed(env(monkeypatch, tmp_path))
    store.save_session(
        "prob",
        SessionRecord(
            concepts=[UpdateConcept(id="bayes", status_change="started")],
            complete=True,
        ),
        "t",
        store.load_goal("prob"),
    )
    _finish_session("good")
    _mark_done(store)
    assert store.load_goal("prob").passes == {"bayes": 1}

    runner.invoke(app, ["start", "prob"])
    result = runner.invoke(app, ["concept", "prob", "bayes", "--status", "reopened"])
    assert result.exit_code == 0, result.output
    result = runner.invoke(
        app, ["concept", "prob", "bayes", "--status", "completed", "--evidence", "x"]
    )
    assert result.exit_code == 1 and "0 of 1" in result.output
