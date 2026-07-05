from datetime import date

import pytest
from pydantic import ValidationError
from seba.models import (
    Agenda, Concept, EndSession, GoalState, GradeReview, Item, MintItem,
    ReviewItem, SessionRecord, SubjectProfile, Syllabus, UpdateConcept,
)


def test_concept_defaults():
    c = Concept(id="bayes", name="Bayes")
    assert c.status == "unseen" and c.prereqs == [] and c.est_sessions == 1


def test_grade_review_rejects_bad_grade():
    with pytest.raises(ValidationError):
        GradeReview(id="it-1", grade="great")


def test_grade_review_accepts_skipped():
    assert GradeReview(id="it-1", grade="skipped").note is None


def test_session_record_defaults_incomplete():
    r = SessionRecord()
    assert r.complete is False and r.reviews == []


def test_item_roundtrip():
    i = Item(id="it-1", concept="bayes", type="recall", front="f", back="b",
             fsrs={"due": "2026-07-03"}, created=date(2026, 7, 3))
    assert Item.model_validate(i.model_dump()) == i


def test_agenda_allows_no_teach_concept():
    a = Agenda(goal="g", subject="s", session_number=1, briefing="",
               review_items=[ReviewItem(id="it-1", type="recall", front="f", back="b")],
               teach_concept=None, practice_quota=3, pace_hint="steady")
    assert a.teach_concept is None


def test_syllabus_and_goal_state():
    s = Syllabus(goal="g", subject="probability", concepts=[Concept(id="a", name="A")])
    gs = GoalState(name="g", subject="probability", syllabus=s, items=[], session_number=1)
    assert gs.notes == "" and gs.recent_grades == []


def test_subject_profile():
    p = SubjectProfile(name="italian", kind="language", max_reviews_per_session=20,
                       item_types=["produce", "cloze"], session_shape="review-heavy")
    assert p.max_reviews_per_session == 20
