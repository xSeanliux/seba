import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def data_dir() -> Path:
    return Path(os.environ.get("SEBA_DATA_DIR", Path.home() / "seba-data"))


def model() -> str:
    return os.environ.get("SEBA_MODEL", "claude-sonnet-5")


def recovery_model() -> str:
    return os.environ.get("SEBA_RECOVERY_MODEL", "claude-haiku-4-5")


def subjects_dirs() -> list[Path]:
    return [REPO_ROOT / "subjects", data_dir() / "subjects"]
