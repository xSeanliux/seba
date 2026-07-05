from typer.testing import CliRunner

from seba.cli import app

runner = CliRunner()

GOOD = "goal: g\nsubject: probability\nconcepts:\n  - id: a\n    name: A\n"
BAD = "goal: g\nsubject: probability\nconcepts:\n  - id: a\n    name: A\n    prereqs: [ghost]\n"


def test_status_empty(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBA_DATA_DIR", str(tmp_path))
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "no goals" in result.output.lower()


def test_new_goal_from_file(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBA_DATA_DIR", str(tmp_path / "data"))
    f = tmp_path / "syllabus.yaml"
    f.write_text(GOOD)
    result = runner.invoke(
        app, ["new-goal", "prob", "--subject", "probability", "--from-file", str(f)]
    )
    assert result.exit_code == 0
    assert (tmp_path / "data" / "goals" / "prob" / "syllabus.yaml").exists()


def test_new_goal_invalid_syllabus_rejected(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBA_DATA_DIR", str(tmp_path / "data"))
    f = tmp_path / "syllabus.yaml"
    f.write_text(BAD)
    result = runner.invoke(
        app, ["new-goal", "prob", "--subject", "probability", "--from-file", str(f)]
    )
    assert result.exit_code == 1
    assert "ghost" in (result.output + str(result.exception or ""))
    assert not (tmp_path / "data" / "goals" / "prob").exists()


def test_new_goal_unknown_subject(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBA_DATA_DIR", str(tmp_path / "data"))
    f = tmp_path / "syllabus.yaml"
    f.write_text(GOOD)
    result = runner.invoke(
        app, ["new-goal", "x", "--subject", "nonexistent", "--from-file", str(f)]
    )
    assert result.exit_code == 1


def test_new_goal_missing_file_rejected(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBA_DATA_DIR", str(tmp_path / "data"))
    result = runner.invoke(
        app,
        [
            "new-goal",
            "prob",
            "--subject",
            "probability",
            "--from-file",
            str(tmp_path / "nope.yaml"),
        ],
    )
    assert result.exit_code != 0  # typer rejects a nonexistent path, no traceback
    assert result.exception is None or isinstance(result.exception, SystemExit)
    assert not (tmp_path / "data" / "goals" / "prob").exists()
