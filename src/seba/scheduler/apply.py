from datetime import datetime

from seba.models import GoalState, SessionRecord, Status
from seba.scheduler.items import apply_review, mint_item
from seba.syllabus.graph import SyllabusError, apply_status

_STATUS: dict[str, Status] = {"started": Status.IN_PROGRESS, "completed": Status.DONE}


def apply_record(state: GoalState, record: SessionRecord, now: datetime) -> GoalState:
    grades = {r.id: r.grade for r in record.reviews}
    items = [
        apply_review(i, grades[i.id], now) if i.id in grades else i for i in state.items
    ]
    items += [mint_item(m, now.date()) for m in record.new_items]

    syllabus = state.syllabus
    for c in record.concepts:
        if c.status_change:
            try:
                syllabus = apply_status(syllabus, c.id, _STATUS[c.status_change])
            except SyllabusError:
                pass  # re-reported or illegal move: never corrupt state
    return state.model_copy(update={"items": items, "syllabus": syllabus})
