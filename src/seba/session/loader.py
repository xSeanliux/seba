from pathlib import Path

import yaml

from seba import config
from seba.models import Agenda, SubjectProfile

_PROMPTS = Path(__file__).parent / "prompts"


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


def system_prompt(agenda: Agenda, overlay: str) -> str:
    template = (_PROMPTS / "system_base.md").read_text()
    return template.format(
        overlay=overlay,
        agenda_yaml=yaml.safe_dump(agenda.model_dump(), sort_keys=False))


def recovery_prompt(transcript: str, agenda_yaml: str) -> str:
    template = (_PROMPTS / "recovery.md").read_text()
    return template.format(transcript=transcript, agenda_yaml=agenda_yaml)
