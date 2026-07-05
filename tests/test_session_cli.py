from datetime import date

import yaml
from fsrs import Card
from typer.testing import CliRunner

from seba.cli import app
from seba.models import Concept, Item, SessionRecord, Syllabus
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
