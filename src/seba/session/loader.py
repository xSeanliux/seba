import yaml

from seba import config
from seba.models import SubjectProfile


def load_profile(subject: str) -> SubjectProfile | None:
    for base in config.subjects_dirs():
        p = base / subject / "profile.yaml"
        if p.exists():
            return SubjectProfile.model_validate(yaml.safe_load(p.read_text()))
    return None


def load_overlay(subject: str) -> str:
    for base in config.subjects_dirs():
        p = base / subject / "overlay.md"
        if p.exists():
            return p.read_text()
    return ""
