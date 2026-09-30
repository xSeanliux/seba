import subprocess
from datetime import date, datetime, timedelta, timezone

import pytest
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


def test_start_reports_the_concept_calls_recorded_so_far(monkeypatch, tmp_path):
    seed(env(monkeypatch, tmp_path))
    out = yaml.safe_load(runner.invoke(app, ["start", "prob"]).output)
    assert out["concept_calls_so_far"] == 0
    runner.invoke(app, ["concept", "prob", "bayes", "--status", "started"])
    runner.invoke(app, ["concept", "prob", "bayes", "--note", "MISCONCEPTION: x"])
    result = runner.invoke(app, ["start", "prob"])
    out = yaml.safe_load(result.output.split("\n", 1)[1])  # skip the resuming line
    assert out["already_graded"] == [] and out["minted_so_far"] == 0
    assert out["concept_calls_so_far"] == 2


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


def test_abandon_discard_says_what_it_discarded(monkeypatch, tmp_path):
    seed(env(monkeypatch, tmp_path))
    runner.invoke(app, ["start", "prob"])
    runner.invoke(app, ["grade", "prob", "it-1", "good"])
    runner.invoke(
        app,
        ["mint", "prob", "--concept", "bayes", "--type", "recall"]
        + ["--front", "f", "--back", "b"],
    )
    runner.invoke(app, ["concept", "prob", "bayes", "--status", "started"])
    runner.invoke(app, ["concept", "prob", "bayes", "--note", "n"])
    result = runner.invoke(app, ["abandon", "prob", "--discard"])
    assert result.exit_code == 0
    assert result.output.strip() == (
        "pending session discarded (1 grades, 1 minted, 2 concept calls)"
    )


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
    # shown on one line; the quotes and the non-ASCII text survive
    one_line = 'mixed up "σ-algebra" with a topology — perché?'
    assert f'hard: [bayes] it-1, passed with help — "{one_line}".' in agenda["briefing"]
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


def test_completing_a_concept_never_started_is_refused(monkeypatch, tmp_path):
    store = seed(env(monkeypatch, tmp_path), with_item=False)  # no cards: no pass gate
    runner.invoke(app, ["start", "prob"])
    result = runner.invoke(
        app, ["concept", "prob", "bayes", "--status", "completed", "--evidence", "x"]
    )
    assert result.exit_code == 1 and "unseen -> done" in result.output
    runner.invoke(app, ["concept", "prob", "bayes", "--status", "started"])
    result = runner.invoke(
        app, ["concept", "prob", "bayes", "--status", "completed", "--evidence", "x"]
    )
    assert result.exit_code == 0, result.output
    runner.invoke(app, ["end", "prob", "--summary", "s", "--hint", "h"])
    assert _status(store) == "done"


def test_a_concept_first_carded_this_session_cannot_complete_in_it(
    monkeypatch, tmp_path
):
    seed(env(monkeypatch, tmp_path), with_item=False)
    runner.invoke(app, ["start", "prob"])
    runner.invoke(app, ["concept", "prob", "bayes", "--status", "started"])
    result = runner.invoke(
        app,
        ["mint", "prob", "--concept", "bayes", "--type", "recall"]
        + ["--front", "f", "--back", "b"],
    )
    assert result.exit_code == 0, result.output
    result = runner.invoke(
        app, ["concept", "prob", "bayes", "--status", "completed", "--evidence", "x"]
    )
    assert result.exit_code == 1 and "0 of 1" in result.output


def _goal_yaml(data):
    return yaml.safe_load((data / "goals" / "prob" / "goal.yaml").read_text())


def _commit_count(data):
    out = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"], cwd=data, capture_output=True, text=True
    )
    return int(out.stdout)


def test_tune_prints_and_writes_nothing(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    seed(data)
    before = _commit_count(data)
    result = runner.invoke(app, ["tune", "prob"])
    assert result.exit_code == 0
    shown = yaml.safe_load(result.output)
    assert shown["settings"] == {
        "desired_retention": 0.9,
        "max_interval_days": 180,
        "concepts_per_session": 1,
        "completion_passes": 1,
    }
    assert shown["emphasis"] == {}
    assert _commit_count(data) == before and "settings" not in _goal_yaml(data)


def test_tune_roundtrips_through_goal_yaml(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    store = seed(data)
    result = runner.invoke(
        app,
        ["tune", "prob", "--retention", "0.85", "--max-interval", "120"]
        + ["--concepts-per-session", "2", "--completion-passes", "2"],
    )
    assert result.exit_code == 0, result.output
    assert "desired_retention: 0.9 → 0.85" in result.output
    assert "max_interval_days: 180 → 120" in result.output
    assert _goal_yaml(data)["settings"] == {
        "desired_retention": 0.85,
        "max_interval_days": 120,
        "concepts_per_session": 2,
        "completion_passes": 2,
    }
    s = store.load_goal("prob").settings
    assert (s.desired_retention, s.max_interval_days) == (0.85, 120)
    # a later tune changes one value and keeps the rest
    runner.invoke(app, ["tune", "prob", "--retention", "0.8"])
    s = store.load_goal("prob").settings
    assert (s.desired_retention, s.max_interval_days) == (0.8, 120)


@pytest.mark.parametrize(
    "flags,bounds",
    [
        (["--retention", "0.5"], ["0.7", "0.97"]),
        (["--retention", "0.99"], ["0.7", "0.97"]),
        (["--max-interval", "0"], ["1"]),
        (["--concepts-per-session", "6"], ["1", "5"]),
        (["--completion-passes", "0"], ["1"]),
    ],
)
def test_tune_refuses_out_of_range_with_the_range(monkeypatch, tmp_path, flags, bounds):
    data = env(monkeypatch, tmp_path)
    seed(data)
    before = _commit_count(data)
    result = runner.invoke(app, ["tune", "prob", *flags])
    assert result.exit_code == 1
    assert flags[0] in result.output
    assert all(b in result.output for b in bounds)
    assert _commit_count(data) == before and "settings" not in _goal_yaml(data)


@pytest.mark.parametrize(
    "flags,said",
    [
        (["--concept", "ghost", "--emphasis", "more"], "unknown concept"),
        (["--concept", "bayes"], "--emphasis"),
        (["--emphasis", "more"], "--concept"),
        (["--concept", "bayes", "--emphasis", "lots"], "less, normal, more"),
    ],
)
def test_tune_refuses_bad_emphasis(monkeypatch, tmp_path, flags, said):
    data = env(monkeypatch, tmp_path)
    seed(data)
    result = runner.invoke(app, ["tune", "prob", *flags])
    assert result.exit_code == 1 and said in result.output
    assert "emphasis" not in _goal_yaml(data)


def test_emphasis_more_makes_the_cards_due_now(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    store = seed(data)
    gs = store.load_goal("prob")
    far = gs.items[0].model_copy(update={"fsrs": _fsrs("2099-01-01T00:00:00+00:00")})
    store.save_tuning("prob", gs.settings, gs.emphasis, [far])
    assert (
        yaml.safe_load(runner.invoke(app, ["start", "prob"]).output)["agenda"][
            "review_items"
        ]
        == []
    )
    runner.invoke(app, ["abandon", "prob", "--discard"])

    result = runner.invoke(
        app, ["tune", "prob", "--concept", "bayes", "--emphasis", "more"]
    )
    assert result.exit_code == 0, result.output
    assert "emphasis [bayes]: normal → more" in result.output
    assert "1 card due now" in result.output
    gs2 = store.load_goal("prob")
    assert gs2.emphasis == {"bayes": "more"}
    assert gs2.items[0].fsrs["due"][:10] == date.today().isoformat()
    agenda = yaml.safe_load(runner.invoke(app, ["start", "prob"]).output)["agenda"]
    assert [r["id"] for r in agenda["review_items"]] == ["it-1"]
    assert "emphasis: [bayes] more" in agenda["briefing"]


def test_emphasis_less_and_normal_leave_due_dates_alone(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    store = seed(data)
    due = store.load_goal("prob").items[0].fsrs["due"]
    runner.invoke(app, ["tune", "prob", "--concept", "bayes", "--emphasis", "less"])
    gs = store.load_goal("prob")
    assert gs.emphasis == {"bayes": "less"} and gs.items[0].fsrs["due"] == due
    result = runner.invoke(
        app, ["tune", "prob", "--concept", "bayes", "--emphasis", "normal"]
    )
    assert "emphasis [bayes]: less → normal" in result.output
    assert store.load_goal("prob").emphasis == {}
    assert _goal_yaml(data)["emphasis"] == {}


def test_tune_with_nothing_to_change_does_not_commit(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    seed(data)
    runner.invoke(app, ["tune", "prob", "--retention", "0.85"])
    before = _commit_count(data)
    result = runner.invoke(app, ["tune", "prob", "--retention", "0.85"])
    assert result.exit_code == 0 and "nothing changed" in result.output
    assert _commit_count(data) == before


def test_tune_works_during_a_session(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    store = seed(data)
    runner.invoke(app, ["start", "prob"])
    pending = data / "goals" / "prob" / "session.pending.yaml"
    before = pending.read_text()
    result = runner.invoke(app, ["tune", "prob", "--max-interval", "5"])
    assert result.exit_code == 0, result.output
    assert pending.read_text() == before
    runner.invoke(app, ["grade", "prob", "it-1", "easy"])
    result = runner.invoke(app, ["end", "prob", "--summary", "s", "--hint", "h"])
    assert result.exit_code == 0, result.output
    due = datetime.fromisoformat(store.load_goal("prob").items[0].fsrs["due"])
    assert due - datetime.now(timezone.utc) <= timedelta(days=5)  # new ceiling applied


def test_tune_on_an_unknown_goal_fails_cleanly(monkeypatch, tmp_path):
    env(monkeypatch, tmp_path)
    result = runner.invoke(app, ["tune", "nope"])
    assert result.exit_code == 1 and "no such goal" in result.output


@pytest.mark.parametrize(
    "emphasis_flags",
    [
        ["--concept", "ghost", "--emphasis", "more"],
        ["--concept", "bayes", "--emphasis", "lots"],
        ["--concept", "bayes"],
    ],
)
def test_a_valid_setting_with_a_bad_emphasis_writes_nothing(
    monkeypatch, tmp_path, emphasis_flags
):
    data = env(monkeypatch, tmp_path)
    seed(data)
    gdir = data / "goals" / "prob"
    goal_yaml, items = (
        (gdir / "goal.yaml").read_text(),
        (gdir / "items.jsonl").read_text(),
    )
    before = _commit_count(data)
    result = runner.invoke(
        app, ["tune", "prob", "--retention", "0.85", *emphasis_flags]
    )
    assert result.exit_code == 1
    assert (gdir / "goal.yaml").read_text() == goal_yaml
    assert (gdir / "items.jsonl").read_text() == items
    assert _commit_count(data) == before


def _seed_concepts(data):
    Store(data).create_goal(
        "prob",
        Syllabus(
            goal="learn probability",
            subject="probability",
            concepts=[
                Concept(id="counting", name="Counting", status=Status.DONE),
                Concept(
                    id="bayes",
                    name="Bayes' Theorem",
                    prereqs=["counting"],
                    status=Status.IN_PROGRESS,
                ),
                Concept(
                    id="martingales",
                    name="Martingales",
                    status=Status.DROPPED,
                    dropped_from=Status.UNSEEN,
                ),
                Concept(id="priors", name="Choosing Priors", prereqs=["bayes"]),
                Concept(id="sets", name="Set Algebra"),
            ],
        ),
        "probability",
    )


def test_concepts_lists_the_syllabus_in_order(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    _seed_concepts(data)
    before = _commit_count(data)
    result = runner.invoke(app, ["concepts", "prob"])
    assert result.exit_code == 0, result.output
    assert result.output == (
        "direction: learn probability\n"
        "counting     done         Counting\n"
        "bayes        in-progress  Bayes' Theorem  prereqs: counting\n"
        "martingales  dropped      Martingales  dropped from: unseen\n"
        "priors       unseen       Choosing Priors  prereqs: bayes\n"
        "sets         unseen       Set Algebra\n"
        "frontier: bayes, sets\n"
    )
    assert _commit_count(data) == before


@pytest.mark.parametrize(
    "text,ids",
    [("bayes", ["bayes"]), ("PRIOR", ["priors"]), ("algebra", ["sets"])],
)
def test_concepts_grep_matches_id_or_name_ignoring_case(
    monkeypatch, tmp_path, text, ids
):
    _seed_concepts(env(monkeypatch, tmp_path))
    result = runner.invoke(app, ["concepts", "prob", "--grep", text])
    assert result.exit_code == 0, result.output
    lines = result.output.splitlines()
    assert lines[0] == "direction: learn probability"
    assert [ln.split()[0] for ln in lines[1:-1]] == ids
    assert lines[-1] == "frontier: bayes, sets"


def test_concepts_grep_with_no_match_prints_nothing(monkeypatch, tmp_path):
    _seed_concepts(env(monkeypatch, tmp_path))
    result = runner.invoke(app, ["concepts", "prob", "--grep", "topology"])
    assert result.exit_code == 0 and result.output == ""


def test_concepts_frontier_none(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    store = seed(data, with_item=False)
    _mark_done(store)
    result = runner.invoke(app, ["concepts", "prob"])
    assert result.exit_code == 0
    assert result.output.splitlines()[-1] == "frontier: none"


def test_concepts_on_an_unknown_goal_fails_cleanly(monkeypatch, tmp_path):
    env(monkeypatch, tmp_path)
    result = runner.invoke(app, ["concepts", "nope"])
    assert result.exit_code == 1 and "no such goal" in result.output
