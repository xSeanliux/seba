import subprocess

import pytest
from typer.testing import CliRunner

from seba.cli import app
from seba.models import Concept, Status, Syllabus
from seba.store.store import Store
from seba.syllabus.graph import frontier

runner = CliRunner()


def _seed(monkeypatch, tmp_path):
    """bayes done; odds on bayes; lotp free; old dropped from in-progress;
    older dropped from unseen, on old."""
    data = tmp_path / "data"
    monkeypatch.setenv("SEBA_DATA_DIR", str(data))
    concepts = [
        Concept(id="bayes", name="Bayes", status="done"),
        Concept(id="odds", name="Odds", prereqs=["bayes"], sources=["a.md"]),
        Concept(id="lotp", name="LOTP"),
        Concept(id="old", name="Old", status="dropped", dropped_from="in-progress"),
        Concept(
            id="older",
            name="Older",
            prereqs=["old"],
            status="dropped",
            dropped_from="unseen",
        ),
    ]
    Store(data).create_goal(
        "prob",
        Syllabus(goal="prob", subject="probability", concepts=concepts),
        "probability",
    )
    return data


def _syllabus_bytes(data):
    return (data / "goals" / "prob" / "syllabus.yaml").read_bytes()


def _commit_count(data):
    out = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"], cwd=data, capture_output=True, text=True
    )
    return int(out.stdout)


def _concept(data, cid):
    [c] = [c for c in Store(data).load_goal("prob").syllabus.concepts if c.id == cid]
    return c


def _edit(*args):
    return runner.invoke(app, ["edit", "prob", *args])


def test_name(monkeypatch, tmp_path):
    data = _seed(monkeypatch, tmp_path)
    result = _edit("odds", "--name", "Odds  and\nodds ratios")
    assert result.exit_code == 0, result.output
    assert result.output == 'name: "Odds" → "Odds and odds ratios"\n'
    assert _concept(data, "odds").name == "Odds and odds ratios"


def test_add_prereq_moves_the_frontier(monkeypatch, tmp_path):
    data = _seed(monkeypatch, tmp_path)
    s = Store(data).load_goal("prob").syllabus
    assert [c.id for c in frontier(s)] == ["odds", "lotp"]
    result = _edit("lotp", "--add-prereq", "odds")
    assert result.exit_code == 0, result.output
    assert result.output == "prereq added: odds\n"
    s = Store(data).load_goal("prob").syllabus
    assert [c.id for c in frontier(s)] == ["odds"]


def test_remove_prereq(monkeypatch, tmp_path):
    data = _seed(monkeypatch, tmp_path)
    result = _edit("older", "--remove-prereq", "old")
    assert result.exit_code == 0, result.output
    assert result.output == "prereq removed: old\n"
    assert _concept(data, "older").prereqs == []


def test_add_source_repeatable(monkeypatch, tmp_path):
    data = _seed(monkeypatch, tmp_path)
    result = _edit("odds", "--add-source", "b.md", "--add-source", "c.pdf p.3-9")
    assert result.exit_code == 0, result.output
    assert result.output == "source added: b.md\nsource added: c.pdf p.3-9\n"
    assert _concept(data, "odds").sources == ["a.md", "b.md", "c.pdf p.3-9"]


def test_drop_then_restore_returns_the_status_it_had(monkeypatch, tmp_path):
    data = _seed(monkeypatch, tmp_path)
    result = _edit("lotp", "--status", "dropped")
    assert result.exit_code == 0, result.output
    assert result.output == "status: unseen → dropped\n"
    result = _edit("old", "--status", "restored")
    assert result.exit_code == 0, result.output
    assert result.output == "status: dropped → in-progress\n"
    c = _concept(data, "old")
    assert (c.status, c.dropped_from) == (Status.IN_PROGRESS, None)


def test_flags_combine_in_one_commit(monkeypatch, tmp_path):
    data = _seed(monkeypatch, tmp_path)
    commits = _commit_count(data)
    result = _edit(
        "older",
        "--name",
        "Older still",
        "--remove-prereq",
        "old",
        "--add-prereq",
        "bayes",
        "--add-prereq",
        "lotp",
        "--add-source",
        "x.md",
        "--status",
        "restored",
    )
    assert result.exit_code == 0, result.output
    assert result.output == (
        'name: "Older" → "Older still"\n'
        "prereq added: bayes\n"
        "prereq added: lotp\n"
        "prereq removed: old\n"
        "source added: x.md\n"
        "status: dropped → unseen\n"
    )
    c = _concept(data, "older")
    assert c.prereqs == ["bayes", "lotp"] and c.status == Status.UNSEEN
    assert _commit_count(data) == commits + 1


def test_success_commits_only_the_syllabus(monkeypatch, tmp_path):
    data = _seed(monkeypatch, tmp_path)
    (data / "goals" / "prob" / "notes.md").write_text("unsaved\n")
    assert _edit("odds", "--name", "Odds ratios").exit_code == 0
    log = subprocess.run(
        ["git", "log", "-1", "--name-only", "--format=%s"],
        cwd=data,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    assert log == ["prob: edited odds", "", "goals/prob/syllabus.yaml"]


def test_nothing_changed_writes_nothing(monkeypatch, tmp_path):
    data = _seed(monkeypatch, tmp_path)
    before, commits = _syllabus_bytes(data), _commit_count(data)
    result = _edit("odds", "--name", "Odds", "--add-source", "a.md")
    assert result.exit_code == 0, result.output
    assert result.output == "nothing changed\n"
    assert _syllabus_bytes(data) == before
    assert _commit_count(data) == commits


@pytest.mark.parametrize(
    "args, message",
    [
        (["nope", "odds", "--name", "x"], "no such goal: 'nope'"),
        (["prob", "zzz", "--name", "x"], "unknown concept: 'zzz'"),
        (
            ["prob", "odds"],
            "nothing to edit — give --name, --add-prereq, "
            "--remove-prereq, --add-source or --status",
        ),
        (["prob", "odds", "--name", "  "], "--name needs text"),
        (
            ["prob", "lotp", "--add-prereq", "nope"],
            "concept 'lotp' has unknown prereqs: ['nope']",
        ),
        (["prob", "odds", "--add-prereq", "odds"], "'odds' cannot depend on itself"),
        (["prob", "odds", "--add-prereq", "bayes"], "'odds' already depends on bayes"),
        (
            ["prob", "lotp", "--remove-prereq", "bayes"],
            "'lotp' does not depend on bayes",
        ),
        (["prob", "bayes", "--add-prereq", "odds"], "prereq cycle: "),
        (
            ["prob", "lotp", "--add-prereq", "old"],
            "concept 'lotp' depends on old, which is dropped — restore that first",
        ),
        (
            ["prob", "bayes", "--status", "dropped"],
            "cannot drop 'bayes': odds depend on it — drop them first, "
            "or remove the edge with seba edit --remove-prereq",
        ),
        (["prob", "lotp", "--status", ""], "--status must be dropped or restored"),
        (
            ["prob", "older", "--status", "restored"],
            "cannot restore 'older': it depends on old, which is dropped — "
            "restore that first",
        ),
        (["prob", "lotp", "--status", "done"], "--status must be dropped or restored"),
    ],
)
def test_refusal_writes_nothing(monkeypatch, tmp_path, args, message):
    data = _seed(monkeypatch, tmp_path)
    before, commits = _syllabus_bytes(data), _commit_count(data)
    result = runner.invoke(app, ["edit", *args])
    assert result.exit_code == 1
    assert result.output.startswith(message), result.output
    assert _syllabus_bytes(data) == before
    assert _commit_count(data) == commits


def test_refused_while_a_session_is_pending(monkeypatch, tmp_path):
    data = _seed(monkeypatch, tmp_path)
    assert runner.invoke(app, ["start", "prob"]).exit_code == 0
    pending = data / "goals" / "prob" / "session.pending.yaml"
    held = pending.read_bytes()
    before, commits = _syllabus_bytes(data), _commit_count(data)
    result = _edit("lotp", "--status", "dropped")
    assert result.exit_code == 1
    assert result.output == (
        "a session is in progress for 'prob' — end or abandon it before "
        "editing the syllabus\n"
    )
    assert pending.read_bytes() == held
    assert _syllabus_bytes(data) == before
    assert _commit_count(data) == commits
