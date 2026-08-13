from datetime import datetime

from seba.models import GoalState, Grade, SessionRecord, Status
from seba.scheduler.items import apply_review, mint_item
from seba.syllabus.graph import SyllabusError, apply_status

_STATUS: dict[str, Status] = {"started": Status.IN_PROGRESS, "completed": Status.DONE}


def lapsing_concepts(state: GoalState, record: SessionRecord) -> set[str]:
    """Concepts with a card graded `again` in that card's last two reviews.

    Card health, not the tutor's impression: the object FSRS keeps alive is the
    card, and a concept can be `done` while all of its cards are lapsing."""
    graded = {r.id: r.grade for r in record.reviews}
    out = set()
    for i in state.items:
        recent = state.recent_by_item.get(i.id, [])
        if i.id in graded:
            recent = [*recent, graded[i.id]]
        if Grade.AGAIN in recent[-2:]:
            out.add(i.concept)
    return out


def apply_record(state: GoalState, record: SessionRecord, now: datetime) -> GoalState:
    grades = {r.id: r.grade for r in record.reviews}
    items = [
        apply_review(i, grades[i.id], now) if i.id in grades else i for i in state.items
    ]
    # Mint due-dates use the LOCAL day so a freshly minted card is due the same
    # day the scheduler filters on (start/build_agenda use date.today(), local).
    # now is UTC; now.date() would be tomorrow for evening sessions in UTC-behind
    # timezones, making the card miss the next-day agenda.
    items += [mint_item(m, now.astimezone().date()) for m in record.new_items]

    syllabus = state.syllabus
    for c in record.concepts:
        if c.status_change:
            try:
                syllabus = apply_status(syllabus, c.id, _STATUS[c.status_change])
            except SyllabusError:
                pass  # re-reported or illegal move: never corrupt state

    # A card that lapsed this session reopens its concept in the same save; a
    # `completed` recorded this session wins for this session.
    completed = {c.id for c in record.concepts if c.status_change == "completed"}
    lapsed = lapsing_concepts(state, record) - completed
    done = {c.id for c in syllabus.concepts if c.status == Status.DONE}
    for cid in sorted(lapsed & done):
        syllabus = apply_status(syllabus, cid, Status.IN_PROGRESS)
    return state.model_copy(update={"items": items, "syllabus": syllabus})
