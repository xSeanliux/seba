from pathlib import Path

from pydantic import BaseModel, ValidationError

from seba.models import (
    Agenda,
    EndSession,
    GradeReview,
    MintItem,
    SessionRecord,
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
    ):
        self.agenda = agenda
        self.syllabus = syllabus
        self.sources_dir = sources_dir
        self.max_reviews = max_reviews_per_session
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
        self.record.concepts.append(call)
        return "recorded", False

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
