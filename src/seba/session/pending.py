from pathlib import Path

import yaml
from pydantic import ValidationError

from seba.models import PendingSession


class PendingError(Exception):
    pass


def pending_path(data_dir: Path, goal: str) -> Path:
    return data_dir / "goals" / goal / "session.pending.yaml"


def load_pending(path: Path) -> PendingSession | None:
    if not path.exists():
        return None
    try:
        return PendingSession.model_validate(yaml.safe_load(path.read_text()))
    except (yaml.YAMLError, ValidationError) as e:
        raise PendingError(f"{path.name}: {e}") from e


def save_pending(path: Path, pending: PendingSession) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(
        yaml.safe_dump(
            pending.model_dump(mode="json"), sort_keys=False, allow_unicode=True
        )
    )
    tmp.rename(path)


def clear_pending(path: Path) -> None:
    path.unlink(missing_ok=True)
