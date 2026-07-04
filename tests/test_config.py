from pathlib import Path

from seba import config


def test_data_dir_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBA_DATA_DIR", str(tmp_path / "d"))
    assert config.data_dir() == tmp_path / "d"


def test_data_dir_default(monkeypatch):
    monkeypatch.delenv("SEBA_DATA_DIR", raising=False)
    assert config.data_dir() == Path.home() / "seba-data"


def test_subjects_dirs(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBA_DATA_DIR", str(tmp_path))
    dirs = config.subjects_dirs()
    assert dirs[0].name == "subjects" and dirs[1] == tmp_path / "subjects"
