from typer.testing import CliRunner

from seba.cli import app

runner = CliRunner()


def test_status_empty(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBA_DATA_DIR", str(tmp_path))
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "no goals" in result.output.lower()


def test_new_goal_unknown_subject_without_profile_errors(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    toc = tmp_path / "toc.md"
    toc.write_text("# ch1")
    # no API key -> command must fail cleanly, not create a broken goal
    result = runner.invoke(app, ["new-goal", "prob", "--subject", "probability",
                                 "--toc", str(toc)])
    assert result.exit_code != 0
    assert not (tmp_path / "goals" / "prob").exists()
