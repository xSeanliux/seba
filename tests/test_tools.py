from pathlib import Path

import pytest
from seba.models import Agenda, Concept, ReviewItem, Syllabus
from seba.session.tools import ToolHandler, mint_budget


@pytest.fixture
def handler(tmp_path: Path):
    agenda = Agenda(
        goal="g",
        subject="probability",
        session_number=1,
        briefing="",
        review_items=[
            ReviewItem(id="it-1", type="recall", front="f", back="b"),
            ReviewItem(id="it-2", type="recall", front="f", back="b"),
        ],
        teach_concept=None,
        practice_quota=3,
        pace_hint="steady",
    )
    syllabus = Syllabus(
        goal="g", subject="probability", concepts=[Concept(id="bayes", name="Bayes")]
    )
    return ToolHandler(agenda, syllabus, tmp_path, 6, set(), {"bayes"})


def test_grade_review_ok_and_duplicate(handler):
    text, err = handler.handle("grade_review", {"id": "it-1", "grade": "good"})
    assert not err and handler.record.reviews[0].grade == "good"
    _, err2 = handler.handle("grade_review", {"id": "it-1", "grade": "easy"})
    assert err2  # already graded


def test_grade_review_unknown_id(handler):
    text, err = handler.handle("grade_review", {"id": "it-99", "grade": "good"})
    assert err and "it-99" in text


def test_grade_review_bad_args(handler):
    _, err = handler.handle("grade_review", {"id": "it-1", "grade": "great"})
    assert err


def test_mint_budget_tracks_review_capacity(handler):
    assert (mint_budget(6), mint_budget(20), mint_budget(2), mint_budget(0)) == (
        3,
        5,
        2,
        2,
    )
    for i in range(3):  # handler is built with 6 reviews/session -> budget 3
        _, err = handler.handle(
            "mint_item",
            {"concept": "bayes", "type": "recall", "front": f"f{i}", "back": "b"},
        )
        assert not err
    text, err = handler.handle(
        "mint_item", {"concept": "bayes", "type": "recall", "front": "f3", "back": "b"}
    )
    assert err and "3 this session" in text and "6/session" in text


def test_mint_unknown_concept(handler):
    _, err = handler.handle(
        "mint_item", {"concept": "ghost", "type": "recall", "front": "f", "back": "b"}
    )
    assert err


def test_end_session_gate(handler):
    text, err = handler.handle(
        "end_session", {"summary": "s", "next_session_hint": "h"}
    )
    assert err and "it-1" in text and "it-2" in text
    handler.handle("grade_review", {"id": "it-1", "grade": "good"})
    handler.handle("grade_review", {"id": "it-2", "grade": "skipped"})
    _, err2 = handler.handle("end_session", {"summary": "s", "next_session_hint": "h"})
    assert not err2 and handler.record.complete
    _, err3 = handler.handle("end_session", {"summary": "s2", "next_session_hint": "h"})
    assert err3  # exactly once


def test_missing_grades(handler):
    assert handler.missing_grades() == ["it-1", "it-2"]
    handler.handle("grade_review", {"id": "it-1", "grade": "again"})
    assert handler.missing_grades() == ["it-2"]


def test_completed_needs_delayed_evidence(handler):
    text, err = handler.handle(
        "update_concept",
        {"id": "bayes", "status_change": "completed", "evidence": "solved 3 unaided"},
    )
    assert err and "no unaided pass in a later session" in text
    assert not handler.record.concepts
    # started is never gated
    _, err2 = handler.handle(
        "update_concept", {"id": "bayes", "status_change": "started"}
    )
    assert not err2


def test_completed_allowed_after_a_later_pass(handler):
    handler.delayed_pass = {"bayes"}
    text, err = handler.handle(
        "update_concept",
        {"id": "bayes", "status_change": "completed", "evidence": "solved 3 unaided"},
    )
    assert not err and text == "recorded"


def test_completed_needs_evidence_field(handler):
    text, err = handler.handle(
        "update_concept", {"id": "bayes", "status_change": "completed"}
    )
    assert err and "evidence" in text


def test_concept_without_cards_bypasses_the_delayed_check(handler):
    handler.carded = set()
    text, err = handler.handle(
        "update_concept",
        {"id": "bayes", "status_change": "completed", "evidence": "derived it aloud"},
    )
    assert not err and "no cards" in text


def test_unknown_tool(handler):
    _, err = handler.handle("nonsense", {})
    assert err
