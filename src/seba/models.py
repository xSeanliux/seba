from datetime import date
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class ItemType(StrEnum):
    RECALL = "recall"
    APPLY = "apply"
    CLOZE = "cloze"
    PRODUCE = "produce"
    RECOGNIZE = "recognize"


class Grade(StrEnum):
    AGAIN = "again"
    HARD = "hard"
    GOOD = "good"
    EASY = "easy"
    SKIPPED = "skipped"


class Status(StrEnum):
    UNSEEN = "unseen"
    IN_PROGRESS = "in-progress"
    DONE = "done"


class PaceHint(StrEnum):
    PUSH_HARDER = "push-harder"
    STEADY = "steady"
    STEP_BACK = "step-back"


class Concept(BaseModel):
    id: str
    name: str
    prereqs: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    status: Status = Status.UNSEEN
    est_sessions: int = 1


class Syllabus(BaseModel):
    goal: str
    subject: str
    concepts: list[Concept]


class Item(BaseModel):
    id: str
    concept: str
    type: ItemType
    front: str
    back: str
    fsrs: dict  # owned by py-fsrs (Card.to_dict()); others read only "due"
    created: date
    suspended: bool = False


class ReviewItem(BaseModel):
    id: str
    type: ItemType
    front: str
    back: str


class TeachConcept(BaseModel):
    id: str
    name: str
    source_excerpts: list[str] = Field(default_factory=list)
    guidance: str = ""


class Agenda(BaseModel):
    goal: str
    subject: str
    session_number: int
    briefing: str
    review_items: list[ReviewItem]
    teach_concept: TeachConcept | None
    practice_quota: int
    pace_hint: PaceHint


class GradeReview(BaseModel):
    """Grade a review item right after its exchange resolves.

    Rubric: wrong or no recall -> again; correct with significant
    hesitation or hints -> hard; correct -> good; instant and
    confident -> easy; never reached this session -> skipped."""

    id: str
    grade: Grade
    note: str | None = None


class MintItem(BaseModel):
    """Create a spaced-repetition card. Only for facts/skills worth
    retaining a month from now — not session-local scaffolding."""

    concept: str
    type: ItemType
    front: str
    back: str


class UpdateConcept(BaseModel):
    """Record concept progress or a note (misconception, strength)."""

    id: str
    status_change: Literal["started", "completed"] | None = None
    note: str | None = None


class EndSession(BaseModel):
    """Close the session. Call exactly once, after recapping aloud."""

    summary: str
    next_session_hint: str


class SessionRecord(BaseModel):
    reviews: list[GradeReview] = Field(default_factory=list)
    concepts: list[UpdateConcept] = Field(default_factory=list)
    new_items: list[MintItem] = Field(default_factory=list)
    summary: str | None = None
    next_session_hint: str | None = None
    complete: bool = False


class SubjectProfile(BaseModel):
    name: str
    kind: str
    max_reviews_per_session: int
    item_types: list[ItemType]
    session_shape: str


class GoalState(BaseModel):
    name: str
    subject: str
    syllabus: Syllabus
    items: list[Item]
    notes: str = ""
    last_hint: str | None = None
    session_number: int
    recent_grades: list[Grade] = Field(default_factory=list)


class GoalSummary(BaseModel):
    name: str
    subject: str
    session_count: int
    due_count: int


class PendingSession(BaseModel):
    goal: str
    agenda: Agenda
    record: SessionRecord = Field(default_factory=SessionRecord)
    started: date
