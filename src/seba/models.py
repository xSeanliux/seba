from datetime import date
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, model_validator


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


class SessionType(StrEnum):
    ORDINARY = "ordinary"
    SYNTHESIS = "synthesis"
    RETURN_AFTER_LAPSE = "return-after-lapse"
    # ponytail: `checkpoint` deferred — it needs sequestered items (a pool held
    # back from FSRS selection) to sample a unit unscaffolded. Nothing mints those yet.


class PaceHint(StrEnum):
    PUSH_HARDER = "push-harder"
    STEADY = "steady"
    STEP_BACK = "step-back"


class Concept(BaseModel):
    id: str
    name: str
    prereqs: list[str] = Field(default_factory=list)
    # Advisory edges: the syllabus is LLM-drafted from a table of contents, so a
    # wrong hard edge would strand a concept forever. These never gate the frontier.
    soft_prereqs: list[str] = Field(default_factory=list)
    confusable_with: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    status: Status = Status.UNSEEN
    est_sessions: int = 1
    kc_type: Literal["fact", "concept", "procedure", "principle"] = "concept"


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
    kc_type: Literal["fact", "concept", "procedure", "principle"] = "concept"
    confusable_with: list[str] = Field(
        default_factory=list
    )  # both declared directions; what practice interleaves against
    sources: list[str] = Field(
        default_factory=list
    )  # raw locators the tutor resolves on demand
    source_excerpts: list[str] = Field(
        default_factory=list
    )  # pre-loaded text for local-text sources
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
    session_type: SessionType = SessionType.ORDINARY


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
    evidence: str | None = None

    @model_validator(mode="after")
    def _completed_needs_evidence(self) -> "UpdateConcept":
        # Naming the exchange moves the call from mastery attribution (which the
        # model does badly) toward turn correctness (which it does well).
        if self.status_change == "completed" and not (self.evidence or "").strip():
            raise ValueError(
                "completing a concept requires `evidence`: name the specific "
                "exchange in this session that demonstrated the learner has it"
            )
        return self


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
    session_date: date | None = None  # stamped on save; absent in older outcomes


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
    recent_by_concept: dict[str, list[Grade]] = Field(default_factory=dict)
    recent_by_item: dict[str, list[Grade]] = Field(default_factory=dict)
    grades_by_concept: dict[str, list[Grade]] = Field(default_factory=dict)  # all-time
    # Concepts graded `again`/`hard` in the most recent session only — Rosenshine's
    # "review where errors were made last time", which the 3-session pool blurs.
    last_session_errors: set[str] = Field(default_factory=set)
    started_at: dict[str, int] = Field(
        default_factory=dict
    )  # session first in-progress
    last_session_date: date | None = None
    # Concepts with a good/easy card review in a session strictly after the one
    # where teaching started — the delayed, unaided check `completed` is gated on.
    delayed_pass: set[str] = Field(default_factory=set)


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


class ViewConcept(BaseModel):
    id: str
    name: str
    status: Status
    layer: int  # longest prereq path from a root; drives graph column
    prereqs: list[str]
    cards: int
    due: int
    est_sessions: int


class ViewStats(BaseModel):
    concepts_done: int
    concepts_total: int
    cards_total: int
    cards_due: int
    frontier: list[str]


class ViewData(BaseModel):
    goal: str
    subject: str
    session_number: int
    generated: date
    stats: ViewStats
    concepts: list[ViewConcept]
    recent_grades: list[Grade]
