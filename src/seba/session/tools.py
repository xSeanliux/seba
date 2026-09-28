from pathlib import Path

from pydantic import BaseModel, ValidationError

from seba.models import (
    Agenda,
    EndSession,
    Grade,
    GradeReview,
    MintItem,
    SessionRecord,
    Status,
    Syllabus,
    UpdateConcept,
)


def mint_budget(max_reviews_per_session: int) -> int:
    """New cards per session, budgeted against review capacity.

    Minting faster than the session can review grows a due queue that never
    drains; once the review cap binds it becomes the scheduler and FSRS's
    intervals are silently overrun."""
    return max(2, min(5, max_reviews_per_session // 2))


TOOL_MODELS: dict[str, type[BaseModel]] = {
    "grade_review": GradeReview,
    "mint_item": MintItem,
    "update_concept": UpdateConcept,
    "end_session": EndSession,
}


class ToolHandler:
    def __init__(
        self,
        agenda: Agenda,
        syllabus: Syllabus,
        sources_dir: Path,
        max_reviews_per_session: int,
        passes: dict[str, int],
        completion_passes: int,
        carded: set[str],
    ):
        self.agenda = agenda
        self.syllabus = syllabus
        self.sources_dir = sources_dir
        self.max_reviews = max_reviews_per_session
        self.passes = passes
        self.completion_passes = completion_passes
        self.carded = carded
        self.mint_budget = mint_budget(max_reviews_per_session)
        self.record = SessionRecord()

    def missing_grades(self) -> list[str]:
        graded = {r.id for r in self.record.reviews}
        return [r.id for r in self.agenda.review_items if r.id not in graded]

    def handle(self, name: str, args: dict) -> tuple[str, bool]:
        model = TOOL_MODELS.get(name)
        if model is None:
            return f"unknown tool: {name}", True
        try:
            call = model.model_validate(args)
        except ValidationError as e:
            return str(e), True
        return getattr(self, f"_{name}")(call)

    def _grade_review(self, call: GradeReview) -> tuple[str, bool]:
        if call.id not in {r.id for r in self.agenda.review_items}:
            return f"'{call.id}' is not in this session's review items", True
        if call.id in {r.id for r in self.record.reviews}:
            return f"'{call.id}' already graded", True
        if call.grade in (Grade.AGAIN, Grade.HARD) and not (call.note or "").strip():
            # Enforced here, not on GradeReview: the model also parses old
            # session outcomes, which have no notes.
            what = (
                "what went wrong"
                if call.grade == Grade.AGAIN
                else "what the help was for"
            )
            return f"grading '{call.grade}' requires --note saying {what}", True
        self.record.reviews.append(call)
        return "recorded", False

    def _mint_item(self, call: MintItem) -> tuple[str, bool]:
        if len(self.record.new_items) >= self.mint_budget:
            return (
                f"mint budget reached ({self.mint_budget} this session); "
                f"review capacity is {self.max_reviews}/session"
            ), True
        if call.concept not in {c.id for c in self.syllabus.concepts}:
            return f"unknown concept: '{call.concept}'", True
        self.record.new_items.append(call)
        return "minted", False

    def _update_concept(self, call: UpdateConcept) -> tuple[str, bool]:
        if call.id not in {c.id for c in self.syllabus.concepts}:
            return f"unknown concept: '{call.id}'", True
        status = next(c.status for c in self.syllabus.concepts if c.id == call.id)
        if call.status_change == "reopened" and status != Status.DONE:
            return (
                f"'{call.id}' is {status}; only a done concept can be reopened"
            ), True
        if call.status_change == "started" and status == Status.DONE:
            return (
                f"'{call.id}' is done; reopening it is the learner's decision — "
                "if they agree, use --status reopened"
            ), True
        note = ""
        if call.status_change == "completed" and not (call.evidence or "").strip():
            # Naming the exchange moves the call from mastery attribution (which
            # the model does badly) toward turn correctness (which it does well).
            return (
                "completing a concept requires --evidence: name the specific "
                "exchange in this session that demonstrated the learner has it"
            ), True
        have = self.passes.get(call.id, 0)
        if call.status_change == "completed" and have < self.completion_passes:
            if call.id in self.carded:
                return (
                    f"'{call.id}' has {have} of {self.completion_passes} unaided "
                    "pass(es) in a later session; each is a good/easy review of "
                    "one of its cards, in a session after the one where teaching "
                    "started or the concept was reopened"
                ), True
            # No cards means the delayed check can never be satisfied; allowing it
            # unremarked would hide that this completion rests on the tutor alone.
            note = " (no cards for this concept, so the delayed check was skipped)"
        self.record.concepts.append(call)
        return "recorded" + note, False

    def _end_session(self, call: EndSession) -> tuple[str, bool]:
        if self.record.complete:
            return "session already ended", True
        missing = self.missing_grades()
        if missing:
            return (
                "cannot end: ungraded review items: "
                + ", ".join(missing)
                + ". Grade each (or grade as 'skipped') first."
            ), True
        self.record.summary = call.summary
        self.record.next_session_hint = call.next_session_hint
        self.record.complete = True
        return "session ended", False
