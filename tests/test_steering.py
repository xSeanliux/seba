from datetime import date

import pytest
import yaml
from typer.testing import CliRunner

from seba.cli import app
from seba.models import (
    Concept,
    GoalSettings,
    GoalState,
    SubjectProfile,
    Syllabus,
)
from seba.scheduler.agenda import build_agenda
from seba.store.store import Store
from seba.syllabus.graph import SyllabusError, check_teachable

TODAY = date(2026, 7, 3)
runner = CliRunner()


def syllabus(concepts):
    return Syllabus(goal="prob", subject="probability", concepts=list(concepts))


def concepts():
    """a done; b, c on the frontier; d needs b and c; e dropped; f in progress."""
    return [
        Concept(id="a", name="A", status="done"),
        Concept(id="b", name="B", prereqs=["a"]),
        Concept(id="c", name="C", prereqs=["a"]),
        Concept(id="d", name="D", prereqs=["b", "c"]),
        Concept(id="e", name="E", status="dropped", dropped_from="unseen"),
        Concept(id="f", name="F", status="in-progress"),
    ]


# --- check_teachable ---


@pytest.mark.parametrize(
    "cid, message",
    [
        ("zz", "unknown concept: 'zz'"),
        ("e", "'e' is dropped; restore it first"),
        ("a", "'a' is done; reopen it if the learner wants it taught again"),
        ("d", "'d' is not ready: b, c must be done first"),
    ],
)
def test_check_teachable_refuses(cid, message):
    with pytest.raises(SyllabusError) as e:
        check_teachable(syllabus(concepts()), cid)
    assert str(e.value) == message


@pytest.mark.parametrize("cid", ["b", "f"])
def test_check_teachable_returns_frontier_and_in_progress(cid):
    assert check_teachable(syllabus(concepts()), cid).id == cid


# --- build_agenda ---


def profile():
    return SubjectProfile(
        name="probability",
        kind="technical",
        max_reviews_per_session=6,
        item_types=["recall"],
        session_shape="teach-heavy",
    )


def state(cs, **kw):
    return GoalState(
        name="prob",
        subject="probability",
        syllabus=syllabus(cs),
        items=[],
        session_number=kw.pop("session_number", 2),
        **kw,
    )


def test_teach_outranks_in_progress_and_frontier_order(tmp_path):
    s = state(concepts())
    assert build_agenda(s, profile(), TODAY, tmp_path).teach_concept.id == "f"
    a = build_agenda(s, profile(), TODAY, tmp_path, teach="c")
    assert a.teach_concept.id == "c" and a.next_concepts == []


def test_follow_on_is_the_usual_first_pick(tmp_path):
    s = state(concepts(), settings=GoalSettings(concepts_per_session=2))
    a = build_agenda(s, profile(), TODAY, tmp_path, teach="c")
    assert a.teach_concept.id == "c"
    assert [c.id for c in a.next_concepts] == ["f"]
    a = build_agenda(s, profile(), TODAY, tmp_path, teach="f")
    assert a.teach_concept.id == "f"
    assert [c.id for c in a.next_concepts] == ["b"]


def test_steering_makes_a_synthesis_or_lapse_day_ordinary(tmp_path):
    two_done = [*concepts(), Concept(id="g", name="G", status="done")]
    for s in (
        state(two_done, session_number=5, last_session_date=date(2026, 7, 1)),
        state(concepts(), last_session_date=date(2026, 6, 1)),
    ):
        assert build_agenda(s, profile(), TODAY, tmp_path).session_type != "ordinary"
        a = build_agenda(s, profile(), TODAY, tmp_path, teach="b")
        assert a.session_type == "ordinary" and a.teach_concept.id == "b"
        assert "Session type:" not in a.briefing


def test_the_briefing_says_steered(tmp_path):
    s = state(concepts())
    line = "steered: the learner asked for [b] today."
    assert line in build_agenda(s, profile(), TODAY, tmp_path, teach="b").briefing
    assert "steered:" not in build_agenda(s, profile(), TODAY, tmp_path).briefing


def test_build_agenda_lets_the_refusal_through(tmp_path):
    with pytest.raises(SyllabusError, match="'d' is not ready"):
        build_agenda(state(concepts()), profile(), TODAY, tmp_path, teach="d")


# --- seba start --concept ---


def seed(monkeypatch, tmp_path):
    data = tmp_path / "data"
    monkeypatch.setenv("SEBA_DATA_DIR", str(data))
    Store(data).create_goal("prob", syllabus(concepts()), "probability")
    return data / "goals" / "prob" / "session.pending.yaml"


def test_start_concept_picks_the_named_concept(monkeypatch, tmp_path):
    pending = seed(monkeypatch, tmp_path)
    result = runner.invoke(app, ["start", "prob", "--concept", "c"])
    assert result.exit_code == 0
    agenda = yaml.safe_load(result.output)["agenda"]
    assert agenda["teach_concept"]["id"] == "c"
    assert "steered: the learner asked for [c] today." in agenda["briefing"]
    assert pending.exists()


@pytest.mark.parametrize(
    "cid, message",
    [
        ("d", "'d' is not ready: b, c must be done first"),
        ("e", "'e' is dropped; restore it first"),
        ("a", "'a' is done; reopen it if the learner wants it taught again"),
        ("zz", "unknown concept: 'zz'"),
    ],
)
def test_start_concept_refusals_write_nothing(monkeypatch, tmp_path, cid, message):
    pending = seed(monkeypatch, tmp_path)
    result = runner.invoke(app, ["start", "prob", "--concept", cid])
    assert result.exit_code == 1
    assert message in result.output
    assert not pending.exists()


@pytest.mark.parametrize("cid", ["b", "zz"])
def test_start_concept_refused_while_a_session_is_pending(monkeypatch, tmp_path, cid):
    pending = seed(monkeypatch, tmp_path)
    assert runner.invoke(app, ["start", "prob"]).exit_code == 0
    before = pending.read_bytes()
    result = runner.invoke(app, ["start", "prob", "--concept", cid])
    assert result.exit_code == 1
    assert (
        "a session is already in progress for 'prob' — end or abandon it before "
        "choosing a concept"
    ) in result.output
    assert pending.read_bytes() == before
