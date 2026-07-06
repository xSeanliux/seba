import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def data_dir() -> Path:
    return Path(os.environ.get("SEBA_DATA_DIR", Path.home() / "seba-data"))


def subjects_dirs() -> list[Path]:
    return [REPO_ROOT / "subjects", data_dir() / "subjects"]
