import subprocess

import pytest
import yaml
from typer.testing import CliRunner

from seba.cli import app
from seba.models import Concept, Status, Syllabus
from seba.store.store import Store, StoreError
from seba.syllabus.graph import apply_status, frontier

runner = CliRunner()


def _seed(data):
    store = Store(data)
    store.create_goal(
        "prob",
        Syllabus(
            goal="prob",
            subject="probability",
            concepts=[Concept(id="bayes", name="Bayes")],
        ),
        "probability",
    )
    return store


def _env(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBA_DATA_DIR", str(tmp_path / "data"))
    return tmp_path / "data"


def _file(tmp_path, content, name="more.yaml"):
    path = tmp_path / name
    path.write_text(content if isinstance(content, str) else yaml.safe_dump(content))
    return path


def _syllabus_bytes(data):
    return (data / "goals" / "prob" / "syllabus.yaml").read_bytes()


def _commit_count(data):
    out = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"], cwd=data, capture_output=True, text=True
    )
    return int(out.stdout)


def test_new_concept_reaches_frontier_once_its_prereq_is_done(tmp_path):
    store = _seed(tmp_path / "data")
    path = _file(
        tmp_path, {"concepts": [{"id": "odds", "name": "Odds", "prereqs": ["bayes"]}]}
    )
    assert store.extend_syllabus("prob", path) == ["odds"]
    s = store.load_goal("prob").syllabus
    assert [c.id for c in s.concepts] == ["bayes", "odds"]
    assert [c.id for c in frontier(s)] == ["bayes"]
    s = apply_status(s, "bayes", Status.IN_PROGRESS)
    s = apply_status(s, "bayes", Status.DONE)
    assert [c.id for c in frontier(s)] == ["odds"]
    assert _commit_count(store.data_dir) == 2


@pytest.mark.parametrize(
    "concepts, words",
    [
        ([{"id": "bayes", "name": "again"}], ["already", "bayes"]),
        (
            [{"id": "odds", "name": "Odds"}, {"id": "odds", "name": "Odds 2"}],
            ["repeated", "odds"],
        ),
        ([{"id": "odds", "name": "Odds", "prereqs": ["nope"]}], ["unknown", "nope"]),
        (
            [
                {"id": "x", "name": "X", "prereqs": ["bayes", "y"]},
                {"id": "y", "name": "Y", "prereqs": ["x"]},
            ],
            ["cycle", "x", "y"],
        ),
        ([{"id": "odds", "name": "Odds", "status": "in-progress"}], ["in-progress"]),
        ([{"id": "odds", "name": "Odds", "status": "dropped"}], ["dropped"]),
        (
            [{"id": "odds", "name": "Odds", "dropped_from": "unseen"}],
            ["a new concept is unseen"],
        ),
    ],
)
def test_refusal_writes_nothing(tmp_path, concepts, words):
    data = tmp_path / "data"
    store = _seed(data)
    before, commits = _syllabus_bytes(data), _commit_count(data)
    with pytest.raises(StoreError) as e:
        store.extend_syllabus("prob", _file(tmp_path, {"concepts": concepts}))
    msg = str(e.value)
    assert msg.startswith("more.yaml: ")
    assert all(w in msg for w in words), msg
    assert _syllabus_bytes(data) == before
    assert _commit_count(data) == commits


def test_status_message_is_verbatim(tmp_path):
    store = _seed(tmp_path / "data")
    path = _file(tmp_path, [{"id": "odds", "name": "Odds", "status": "in-progress"}])
    with pytest.raises(StoreError) as e:
        store.extend_syllabus("prob", path)
    assert str(e.value) == (
        "more.yaml: new concept 'odds' has status in-progress; "
        "a new concept is unseen, or done if the learner already has it"
    )


def test_done_status_is_accepted(tmp_path):
    store = _seed(tmp_path / "data")
    path = _file(tmp_path, [{"id": "odds", "name": "Odds", "status": "done"}])
    store.extend_syllabus("prob", path)
    assert store.load_goal("prob").syllabus.concepts[1].status == Status.DONE


@pytest.mark.parametrize(
    "content", ["", "concepts: [unclosed", "goal: g\nsubject: s\n", "concepts: []\n"]
)
def test_file_without_concepts_is_refused_naming_it(tmp_path, content):
    data = tmp_path / "data"
    store = _seed(data)
    before = _syllabus_bytes(data)
    with pytest.raises(StoreError) as e:
        store.extend_syllabus("prob", _file(tmp_path, content))
    assert str(e.value).startswith("more.yaml: ")
    assert _syllabus_bytes(data) == before


def test_no_concepts_says_what_is_expected(tmp_path):
    store = _seed(tmp_path / "data")
    with pytest.raises(StoreError) as e:
        store.extend_syllabus("prob", _file(tmp_path, "goal: g\nsubject: s\n"))
    assert str(e.value) == (
        "more.yaml: holds no concepts — expected a list of concepts, "
        "or a mapping with a 'concepts:' list"
    )


def test_both_file_shapes_are_accepted(tmp_path):
    store = _seed(tmp_path / "data")
    whole = {
        "goal": "ignored",
        "subject": "ignored",
        "concepts": [{"id": "odds", "name": "Odds"}],
    }
    assert store.extend_syllabus("prob", _file(tmp_path, whole)) == ["odds"]
    bare = [{"id": "lotp", "name": "LOTP"}, {"id": "cond", "name": "Cond"}]
    assert store.extend_syllabus("prob", _file(tmp_path, bare)) == ["lotp", "cond"]
    s = store.load_goal("prob").syllabus
    assert s.goal == "prob" and s.subject == "probability"
    assert [c.id for c in s.concepts] == ["bayes", "odds", "lotp", "cond"]


def test_extend_commits_only_the_syllabus(tmp_path):
    data = tmp_path / "data"
    store = _seed(data)
    (data / "goals" / "prob" / "notes.md").write_text("unsaved\n")
    store.extend_syllabus("prob", _file(tmp_path, [{"id": "odds", "name": "Odds"}]))
    log = subprocess.run(
        ["git", "log", "-1", "--name-only", "--format=%s"],
        cwd=data,
        capture_output=True,
        text=True,
    ).stdout.split()
    assert log[:3] == ["prob:", "extended", "(+1)"]
    assert log[3:] == ["goals/prob/syllabus.yaml"]


def test_old_goal_extended_round_trips(tmp_path):
    data = tmp_path / "data"
    store = _seed(data)
    path = data / "goals" / "prob" / "syllabus.yaml"
    # As written before `dropped_from` existed.
    path.write_text(
        "goal: prob\nsubject: probability\nconcepts:\n"
        "- id: bayes\n  name: Bayes\n  status: done\n"
    )
    store.extend_syllabus("prob", _file(tmp_path, [{"id": "odds", "name": "Odds"}]))
    s = store.load_goal("prob").syllabus
    assert [(c.id, c.status, c.dropped_from) for c in s.concepts] == [
        ("bayes", Status.DONE, None),
        ("odds", Status.UNSEEN, None),
    ]
    assert "dropped_from" not in path.read_text()


def test_cli_prints_added(monkeypatch, tmp_path):
    data = _env(monkeypatch, tmp_path)
    _seed(data)
    path = _file(
        tmp_path, [{"id": "odds", "name": "Odds"}, {"id": "lotp", "name": "L"}]
    )
    result = runner.invoke(app, ["extend", "prob", "--from-file", str(path)])
    assert result.exit_code == 0, result.output
    assert result.output == "added 2 concept(s): odds, lotp\n"


def test_cli_refusals_exit_1(monkeypatch, tmp_path):
    data = _env(monkeypatch, tmp_path)
    _seed(data)
    path = _file(tmp_path, [{"id": "bayes", "name": "Bayes"}])
    result = runner.invoke(app, ["extend", "prob", "--from-file", str(path)])
    assert result.exit_code == 1 and result.output.startswith("more.yaml: ")
    result = runner.invoke(app, ["extend", "nope", "--from-file", str(path)])
    assert result.exit_code == 1 and "no such goal: 'nope'" in result.output
    missing = str(tmp_path / "missing.yaml")
    result = runner.invoke(app, ["extend", "prob", "--from-file", missing])
    assert result.exit_code != 0


def test_extend_during_a_session(monkeypatch, tmp_path):
    data = _env(monkeypatch, tmp_path)
    _seed(data)
    assert runner.invoke(app, ["start", "prob"]).exit_code == 0
    pending = data / "goals" / "prob" / "session.pending.yaml"
    agenda = yaml.safe_load(pending.read_text())["agenda"]

    path = _file(tmp_path, [{"id": "odds", "name": "Odds", "prereqs": ["bayes"]}])
    result = runner.invoke(app, ["extend", "prob", "--from-file", str(path)])
    assert result.exit_code == 0, result.output
    mint = ["mint", "prob", "--concept", "odds", "--type", "recall"]
    result = runner.invoke(app, [*mint, "--front", "Odds of p?", "--back", "p/(1-p)"])
    assert result.exit_code == 0, result.output
    assert yaml.safe_load(pending.read_text())["agenda"] == agenda

    result = runner.invoke(app, ["end", "prob", "--summary", "s", "--hint", "h"])
    assert result.exit_code == 0, result.output
    state = Store(data).load_goal("prob")
    assert [c.id for c in state.syllabus.concepts] == ["bayes", "odds"]
    assert [i.concept for i in state.items] == ["odds"]


# ---- a new concept on a dropped one ----


def _seed_with(data, **status):
    """bayes and odds, with the statuses given (a dropped one from unseen)."""
    store = Store(data)
    concepts = [
        Concept(
            id=cid,
            name=cid,
            status=status.get(cid, "unseen"),
            dropped_from="unseen" if status.get(cid) == "dropped" else None,
        )
        for cid in ("bayes", "odds")
    ]
    syllabus = Syllabus(goal="prob", subject="probability", concepts=concepts)
    store.create_goal("prob", syllabus, "probability")
    return store


LOGODDS = [{"id": "logodds", "name": "Log odds", "prereqs": ["odds"]}]


def test_a_new_concept_on_a_dropped_one_is_refused(tmp_path):
    data = tmp_path / "data"
    store = _seed_with(data, bayes="dropped", odds="dropped")
    before, commits = _syllabus_bytes(data), _commit_count(data)
    both = [{"id": "x", "name": "X", "prereqs": ["bayes", "odds"]}]
    with pytest.raises(StoreError) as e:
        store.extend_syllabus("prob", _file(tmp_path, both))
    assert str(e.value) == (
        "more.yaml: new concept 'x' depends on bayes, odds, which is dropped — "
        "restore that first"
    )
    assert _syllabus_bytes(data) == before
    assert _commit_count(data) == commits


def test_a_drop_in_this_session_refuses_a_new_dependent(monkeypatch, tmp_path):
    data = _env(monkeypatch, tmp_path)
    _seed_with(data)
    assert runner.invoke(app, ["start", "prob"]).exit_code == 0
    drop = ["concept", "prob", "odds", "--status", "dropped"]
    assert runner.invoke(app, drop).exit_code == 0
    before, commits = _syllabus_bytes(data), _commit_count(data)

    path = _file(tmp_path, LOGODDS)
    result = runner.invoke(app, ["extend", "prob", "--from-file", str(path)])
    assert result.exit_code == 1
    assert result.output == (
        "more.yaml: new concept 'logodds' depends on odds, which is dropped — "
        "restore that first\n"
    )
    assert _syllabus_bytes(data) == before
    assert _commit_count(data) == commits

    result = runner.invoke(app, ["end", "prob", "--summary", "s", "--hint", "h"])
    assert result.exit_code == 0, result.output
    s = Store(data).load_goal("prob").syllabus
    assert [(c.id, c.status) for c in s.concepts] == [
        ("bayes", Status.UNSEEN),
        ("odds", Status.DROPPED),
    ]


def test_a_restore_in_this_session_allows_a_new_dependent(monkeypatch, tmp_path):
    data = _env(monkeypatch, tmp_path)
    _seed_with(data, odds="dropped")
    assert runner.invoke(app, ["start", "prob"]).exit_code == 0
    restore = ["concept", "prob", "odds", "--status", "restored"]
    assert runner.invoke(app, restore).exit_code == 0

    path = _file(tmp_path, LOGODDS)
    result = runner.invoke(app, ["extend", "prob", "--from-file", str(path)])
    assert result.exit_code == 0, result.output
    # Only the new concept is written; the restore waits for `seba end`.
    s = Store(data).load_goal("prob").syllabus
    assert [(c.id, c.status) for c in s.concepts] == [
        ("bayes", Status.UNSEEN),
        ("odds", Status.DROPPED),
        ("logodds", Status.UNSEEN),
    ]


def test_a_malformed_pending_session_is_a_clean_refusal(monkeypatch, tmp_path):
    data = _env(monkeypatch, tmp_path)
    _seed(data)
    (data / "goals" / "prob" / "session.pending.yaml").write_text("agenda: [\n")
    path = _file(tmp_path, [{"id": "odds", "name": "Odds"}])
    result = runner.invoke(app, ["extend", "prob", "--from-file", str(path)])
    assert result.exit_code == 1
    assert result.output.startswith("session.pending.yaml: ")
    assert result.exception is None or isinstance(result.exception, SystemExit)
