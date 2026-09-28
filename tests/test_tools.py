from pathlib import Path

import pytest
from seba.models import Agenda, Concept, ReviewItem, Status, Syllabus
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
    return ToolHandler(agenda, syllabus, tmp_path, 6, {}, 1, {"bayes"})


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
    handler.handle("grade_review", {"id": "it-1", "grade": "again", "note": "blanked"})
    assert handler.missing_grades() == ["it-2"]


@pytest.mark.parametrize("grade", ["hard", "again"])
@pytest.mark.parametrize("note", [None, "", "   ", "\n\t"])
def test_hard_and_again_need_a_note(handler, grade, note):
    text, err = handler.handle(
        "grade_review", {"id": "it-1", "grade": grade, "note": note}
    )
    assert err and "--note" in text
    assert not handler.record.reviews


@pytest.mark.parametrize("grade", ["hard", "again"])
def test_hard_and_again_record_with_a_note(handler, grade):
    _, err = handler.handle(
        "grade_review", {"id": "it-1", "grade": grade, "note": "needed the formula"}
    )
    assert not err and handler.record.reviews[0].note == "needed the formula"


@pytest.mark.parametrize("grade", ["good", "easy", "skipped"])
def test_other_grades_need_no_note(handler, grade):
    _, err = handler.handle("grade_review", {"id": "it-1", "grade": grade})
    assert not err


COMPLETE = {"id": "bayes", "status_change": "completed", "evidence": "solved 3 unaided"}


def test_completed_needs_a_later_pass(handler):
    text, err = handler.handle("update_concept", COMPLETE)
    assert err and "0 of 1" in text and "later session" in text
    assert not handler.record.concepts
    # started is never gated
    _, err2 = handler.handle(
        "update_concept", {"id": "bayes", "status_change": "started"}
    )
    assert not err2


def test_completed_allowed_after_a_later_pass(handler):
    handler.passes = {"bayes": 1}
    text, err = handler.handle("update_concept", COMPLETE)
    assert not err and text == "recorded"


def test_completion_passes_raises_the_bar(handler):
    handler.completion_passes = 2
    handler.passes = {"bayes": 1}
    text, err = handler.handle("update_concept", COMPLETE)
    assert err and "1 of 2" in text
    handler.passes = {"bayes": 2}
    _, err2 = handler.handle("update_concept", COMPLETE)
    assert not err2


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


def _set_status(handler, status):
    handler.syllabus.concepts[0] = handler.syllabus.concepts[0].model_copy(
        update={"status": status}
    )


def test_reopened_needs_a_done_concept(handler):
    for status in (Status.UNSEEN, Status.IN_PROGRESS):
        _set_status(handler, status)
        text, err = handler.handle(
            "update_concept", {"id": "bayes", "status_change": "reopened"}
        )
        assert err and "only a done concept can be reopened" in text
    assert not handler.record.concepts
    _set_status(handler, Status.DONE)
    text, err = handler.handle(
        "update_concept", {"id": "bayes", "status_change": "reopened"}
    )
    assert not err and text == "recorded"


def test_started_does_not_reopen_a_done_concept(handler):
    _set_status(handler, Status.DONE)
    text, err = handler.handle(
        "update_concept", {"id": "bayes", "status_change": "started"}
    )
    assert err and "--status reopened" in text


def test_reopening_restarts_the_count_within_the_session(handler):
    _set_status(handler, Status.DONE)
    handler.passes = {"bayes": 1}
    _, err = handler.handle(
        "update_concept", {"id": "bayes", "status_change": "reopened"}
    )
    assert not err
    text, err2 = handler.handle("update_concept", COMPLETE)
    assert err2 and "0 of 1" in text
    assert [c.status_change for c in handler.record.concepts] == ["reopened"]
