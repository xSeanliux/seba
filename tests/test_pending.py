from datetime import date
from pathlib import Path

import pytest
from seba.models import Agenda, GradeReview, PendingSession, ReviewItem, SessionRecord
from seba.session.pending import (PendingError, clear_pending, load_pending,
                                  pending_path, save_pending)


def agenda():
    return Agenda(goal="prob", subject="probability", session_number=1,
                  briefing="b",
                  review_items=[ReviewItem(id="it-1", type="recall", front="f", back="b")],
                  teach_concept=None, practice_quota=3, pace_hint="steady")


def test_pending_path(tmp_path: Path):
    assert pending_path(tmp_path, "prob") == tmp_path / "goals" / "prob" / "session.pending.yaml"


def test_roundtrip(tmp_path: Path):
    p = tmp_path / "session.pending.yaml"
    ps = PendingSession(goal="prob", agenda=agenda(), started=date(2026, 7, 4))
    ps.record.reviews.append(GradeReview(id="it-1", grade="good"))
    save_pending(p, ps)
    loaded = load_pending(p)
    assert loaded == ps
    assert loaded.record.reviews[0].grade == "good"
    assert not p.with_suffix(".tmp").exists()  # atomic write cleaned up


def test_missing_returns_none(tmp_path: Path):
    assert load_pending(tmp_path / "nope.yaml") is None


def test_malformed_names_file(tmp_path: Path):
    p = tmp_path / "session.pending.yaml"
    p.write_text("not: [valid: pending")
    with pytest.raises(PendingError, match="session.pending.yaml"):
        load_pending(p)


def test_clear_is_idempotent(tmp_path: Path):
    p = tmp_path / "session.pending.yaml"
    save_pending(p, PendingSession(goal="g", agenda=agenda(), started=date(2026, 7, 4)))
    clear_pending(p)
    assert not p.exists()
    clear_pending(p)  # no error on second call
