import subprocess
from datetime import date
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from seba.cli import app
from seba.models import Concept, GoalSettings, GoalState, Item, SubjectProfile, Syllabus
from seba.scheduler.agenda import build_agenda
from seba.store.store import Store
from seba.ui.view import build_view_data, render_view

runner = CliRunner()
TODAY = date(2026, 7, 3)
OUT = "propose what comes next, or confirm with the learner that the goal is finished."


def profile():
    return SubjectProfile(
        name="probability",
        kind="technical",
        max_reviews_per_session=6,
        item_types=["recall"],
        session_shape="teach-heavy",
    )


def state(statuses, direction="judge priors in A/B tests", items=()):
    concepts = [Concept(id=cid, name=cid.upper(), status=s) for cid, s in statuses]
    return GoalState(
        name="prob",
        subject="probability",
        direction=direction,
        syllabus=Syllabus(goal="prob", subject="probability", concepts=concepts),
        items=list(items),
        session_number=4,
    )


def briefing(statuses, **kw):
    return build_agenda(
        state(statuses, **kw), profile(), TODAY, Path("nowhere")
    ).briefing


def item(id, concept, due="2020-01-01T00:00:00+00:00"):
    return Item(
        id=id,
        concept=concept,
        type="recall",
        front="f",
        back="b",
        fsrs={"due": due},
        created=TODAY,
    )


# ---- agenda ----


def test_the_briefing_opens_with_the_direction():
    lines = briefing([("a", "unseen")]).splitlines()
    assert lines[0] == "Direction: judge priors in A/B tests"
    assert lines[1].startswith("Session 4. ")


def test_no_direction_line_when_it_is_empty():
    assert briefing([("a", "unseen")], direction="").startswith("Session 4. ")


def test_the_direction_falls_back_to_the_syllabus_goal(tmp_path):
    store = Store(tmp_path / "data")
    store.create_goal(
        "prob",
        Syllabus(
            goal="learn probability",
            subject="probability",
            concepts=[Concept(id="a", name="A")],
        ),
        "probability",
    )
    b = build_agenda(store.load_goal("prob"), profile(), TODAY, tmp_path).briefing
    assert b.splitlines()[0] == "Direction: learn probability"


def test_progress_line_without_dropped():
    b = briefing(
        [("a", "done"), ("b", "in-progress"), ("c", "unseen"), ("d", "unseen")]
    )
    assert "Session 4. Concepts: 1 done, 3 open." in b.splitlines()
    assert "Concepts done" not in b


def test_progress_line_with_dropped():
    b = briefing(
        [("a", "done"), ("b", "dropped"), ("c", "unseen"), ("d", "in-progress")]
    )
    assert "Session 4. Concepts: 1 done, 2 open, 1 dropped." in b.splitlines()


def test_nearly_out_of_syllabus_at_one_unseen():
    b = briefing([("a", "done"), ("b", "in-progress"), ("c", "unseen")])
    assert (
        f"nearly out of syllabus: 1 concept left unseen (c) — {OUT}" in b.splitlines()
    )


def test_out_of_syllabus_at_none_unseen():
    b = briefing([("a", "done"), ("b", "in-progress")])
    assert f"out of syllabus: no concept left unseen — {OUT}" in b.splitlines()


def test_no_running_out_line_at_two_unseen():
    assert "out of syllabus" not in briefing([("a", "unseen"), ("b", "unseen")])


def test_a_dropped_concept_is_not_counted_as_unseen():
    b = briefing([("a", "unseen"), ("b", "dropped")])
    assert f"nearly out of syllabus: 1 concept left unseen (a) — {OUT}" in b


# ---- store ----


def seed(data_dir):
    store = Store(data_dir)
    store.create_goal(
        "prob",
        Syllabus(
            goal="learn probability",
            subject="probability",
            concepts=[Concept(id="bayes", name="Bayes")],
        ),
        "probability",
    )
    return store


def _goal_yaml(data):
    return yaml.safe_load((data / "goals" / "prob" / "goal.yaml").read_text())


def _commits(data):
    out = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"], cwd=data, capture_output=True, text=True
    )
    return int(out.stdout)


def test_save_tuning_writes_the_direction_and_commits(tmp_path):
    store = seed(tmp_path)
    before = _commits(tmp_path)
    assert store.save_tuning("prob", GoalSettings(), {}, [], direction="read priors")
    assert _goal_yaml(tmp_path)["direction"] == "read priors"
    assert _commits(tmp_path) == before + 1


def test_save_tuning_without_a_direction_leaves_it_alone(tmp_path):
    store = seed(tmp_path)
    store.save_tuning("prob", GoalSettings(), {}, [], direction="read priors")
    store.save_tuning("prob", GoalSettings(desired_retention=0.85), {}, [])
    assert _goal_yaml(tmp_path)["direction"] == "read priors"


# ---- CLI ----


@pytest.fixture
def data(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBA_DATA_DIR", str(tmp_path / "data"))
    seed(tmp_path / "data")
    return tmp_path / "data"


def _files(data):
    gdir = data / "goals" / "prob"
    return (gdir / "goal.yaml").read_text(), (gdir / "items.jsonl").read_text()


def test_tune_direction_reaches_the_next_briefing(data):
    result = runner.invoke(app, ["tune", "prob", "--direction", "judge A/B priors"])
    assert result.exit_code == 0, result.output
    assert 'direction: "learn probability" → "judge A/B priors"' in result.output
    assert _goal_yaml(data)["direction"] == "judge A/B priors"
    out = yaml.safe_load(runner.invoke(app, ["start", "prob"]).output)
    assert out["agenda"]["briefing"].startswith("Direction: judge A/B priors\n")


@pytest.mark.parametrize(
    "flags,said",
    [
        (["--direction", "   "], "--direction needs text"),
        (["--direction", "new aim", "--retention", "0.5"], "--retention"),
        (
            ["--direction", "new aim", "--concept", "ghost", "--emphasis", "more"],
            "ghost",
        ),
    ],
)
def test_a_refused_tune_with_a_direction_writes_nothing(data, flags, said):
    files, before = _files(data), _commits(data)
    result = runner.invoke(app, ["tune", "prob", *flags])
    assert result.exit_code == 1 and said in result.output
    assert _files(data) == files and _commits(data) == before


def test_the_same_direction_twice_changes_nothing(data):
    runner.invoke(app, ["tune", "prob", "--direction", "judge A/B priors"])
    before = _commits(data)
    result = runner.invoke(app, ["tune", "prob", "--direction", "judge A/B priors"])
    assert result.exit_code == 0 and "nothing changed" in result.output
    assert _commits(data) == before


def test_direction_combines_with_a_setting(data):
    result = runner.invoke(
        app, ["tune", "prob", "--direction", "new aim", "--retention", "0.85"]
    )
    assert result.exit_code == 0, result.output
    assert "desired_retention: 0.9 → 0.85" in result.output
    assert 'direction: "learn probability" → "new aim"' in result.output


def test_a_direction_is_one_line(data):
    result = runner.invoke(
        app, ["tune", "prob", "--direction", " read\npriors \t now\nSession 99. x "]
    )
    assert result.exit_code == 0, result.output
    assert _goal_yaml(data)["direction"] == "read priors now Session 99. x"
    out = yaml.safe_load(runner.invoke(app, ["start", "prob"]).output)
    lines = out["agenda"]["briefing"].splitlines()
    assert lines[0] == "Direction: read priors now Session 99. x"
    assert lines[1].startswith("Session 1. ")


def test_a_stated_direction_equal_to_the_fallback_is_recorded(data):
    before = _commits(data)
    result = runner.invoke(app, ["tune", "prob", "--direction", "learn probability"])
    assert result.exit_code == 0, result.output
    assert "nothing changed" not in result.output
    assert "direction:" in result.output
    assert _goal_yaml(data)["direction"] == "learn probability"
    assert _commits(data) == before + 1
    result = runner.invoke(app, ["tune", "prob", "--direction", "learn probability"])
    assert result.exit_code == 0 and "nothing changed" in result.output
    assert _commits(data) == before + 1


def test_tune_with_no_flags_prints_the_direction(data):
    out = yaml.safe_load(runner.invoke(app, ["tune", "prob"]).output)
    assert out["direction"] == "learn probability"
    assert "settings" in out and "emphasis" in out


# ---- view ----


def test_view_counts_open_and_dropped():
    s = state(
        [("a", "done"), ("b", "in-progress"), ("c", "unseen"), ("d", "dropped")],
        items=[item("it-c", "c"), item("it-d", "d")],
    )
    v = build_view_data(s, TODAY)
    st = v.stats
    assert (st.concepts_done, st.concepts_open, st.concepts_dropped) == (1, 2, 1)
    assert st.concepts_total == 4
    assert (st.cards_total, st.cards_due) == (2, 1)  # d's card is not due
    by = {c.id: c for c in v.concepts}
    assert (by["d"].cards, by["d"].due) == (1, 0)
    assert (by["c"].cards, by["c"].due) == (1, 1)


def test_the_page_words_progress_and_marks_dropped():
    html = render_view(build_view_data(state([("a", "done"), ("d", "dropped")]), TODAY))
    assert '"concepts_dropped": 1' in html and '"status": "dropped"' in html
    assert "${S.concepts_done} done, ${S.concepts_open} open" in html
    assert "${S.concepts_dropped} dropped" in html
    assert '"dropped":' in html  # a colour of its own
    assert "</i>dropped" in html  # and a legend entry
    assert "/${S.concepts_total}" not in html
