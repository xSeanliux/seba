from datetime import datetime

from seba.models import (
    Emphasis,
    GoalState,
    SessionRecord,
    Status,
    Syllabus,
    UpdateConcept,
)
from seba.scheduler.items import apply_review, mint_item
from seba.syllabus.graph import (
    SyllabusError,
    _find,
    _replace,
    apply_status,
    drop,
    restore,
)

_STATUS: dict[str, Status] = {
    "started": Status.IN_PROGRESS,
    "completed": Status.DONE,
    "reopened": Status.IN_PROGRESS,
}


def apply_change(syllabus: Syllabus, change: UpdateConcept) -> Syllabus:
    """Apply one concept change. Raises SyllabusError if the move is illegal."""
    if change.status_change == "dropped":
        syllabus = drop(syllabus, change.id)
    elif change.status_change == "restored":
        syllabus = restore(syllabus, change.id)
    elif change.status_change is not None:
        status = _STATUS[change.status_change]
        reopen = change.status_change == "reopened"
        # Re-reporting the status a concept already has (a repeated `started`
        # above all) is normal: no move, and a source it carries still goes in.
        if reopen or _find(syllabus, change.id).status != status:
            syllabus = apply_status(syllabus, change.id, status, reopen=reopen)
    if change.add_source:
        c = _find(syllabus, change.id)
        if change.add_source not in c.sources:
            syllabus = _replace(
                syllabus,
                c.model_copy(update={"sources": [*c.sources, change.add_source]}),
            )
    return syllabus


def replay(syllabus: Syllabus, changes: list[UpdateConcept]) -> Syllabus:
    for c in changes:
        try:
            syllabus = apply_change(syllabus, c)
        except SyllabusError:
            pass  # re-reported or illegal move: never corrupt state
    return syllabus


def apply_record(state: GoalState, record: SessionRecord, now: datetime) -> GoalState:
    grades = {r.id: r.grade for r in record.reviews}
    items = [
        apply_review(
            i,
            grades[i.id],
            now,
            state.settings,
            state.emphasis.get(i.concept, Emphasis.NORMAL),
        )
        if i.id in grades
        else i
        for i in state.items
    ]
    # Mint due-dates use the LOCAL day so a freshly minted card is due the same
    # day the scheduler filters on (start/build_agenda use date.today(), local).
    # now is UTC; now.date() would be tomorrow for evening sessions in UTC-behind
    # timezones, making the card miss the next-day agenda.
    items += [mint_item(m, now.astimezone().date()) for m in record.new_items]

    syllabus = replay(state.syllabus, record.concepts)
    return state.model_copy(update={"items": items, "syllabus": syllabus})
