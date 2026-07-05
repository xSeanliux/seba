from pathlib import Path

from pydantic import BaseModel, ValidationError

from seba.models import (Agenda, EndSession, GradeReview, MintItem,
                         SessionRecord, Syllabus, UpdateConcept)
from seba.scheduler.agenda import resolve_excerpt

MINT_CAP = 10

TOOL_MODELS: dict[str, type[BaseModel]] = {
    "grade_review": GradeReview,
    "mint_item": MintItem,
    "update_concept": UpdateConcept,
    "end_session": EndSession,
}


def anthropic_tools() -> list[dict]:
    tools = [{"name": name,
              "description": model.__doc__ or name,
              "input_schema": model.model_json_schema()}
             for name, model in TOOL_MODELS.items()]
    tools.append({"name": "fetch_source",
                  "description": "Fetch a source excerpt by ref, "
                                 "e.g. blitzstein/ch09.md#9.2",
                  "input_schema": {"type": "object",
                                   "properties": {"ref": {"type": "string"}},
                                   "required": ["ref"]}})
    return tools


class ToolHandler:
    def __init__(self, agenda: Agenda, syllabus: Syllabus, sources_dir: Path):
        self.agenda = agenda
        self.syllabus = syllabus
        self.sources_dir = sources_dir
        self.record = SessionRecord()

    def missing_grades(self) -> list[str]:
        graded = {r.id for r in self.record.reviews}
        return [r.id for r in self.agenda.review_items if r.id not in graded]

    def handle(self, name: str, args: dict) -> tuple[str, bool]:
        if name == "fetch_source":
            ex = resolve_excerpt(self.sources_dir, str(args.get("ref", "")), 16_000)
            return (ex, False) if ex is not None else (f"no such source: {args}", True)
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
        if len(self.record.new_items) >= MINT_CAP:
            return f"mint cap reached ({MINT_CAP}); no more cards this session", True
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
            return ("cannot end: ungraded review items: "
                    + ", ".join(missing)
                    + ". Grade each (or grade as 'skipped') first."), True
        self.record.summary = call.summary
        self.record.next_session_hint = call.next_session_hint
        self.record.complete = True
        return "session ended", False
