from datetime import date, datetime
from uuid import uuid4

from fsrs import Card, Rating, Scheduler

from seba.models import Grade, Item, MintItem

_RATING = {"again": Rating.Again, "hard": Rating.Hard,
           "good": Rating.Good, "easy": Rating.Easy}
_scheduler = Scheduler()


def due_items(items: list[Item], today: date, limit: int) -> list[Item]:
    cutoff = today.isoformat()
    due = [i for i in items
           if not i.suspended and str(i.fsrs.get("due", ""))[:10] <= cutoff]
    due.sort(key=lambda i: str(i.fsrs["due"]))
    return due[:limit]


def apply_review(item: Item, grade: Grade, now: datetime) -> Item:
    if grade == "skipped":
        return item
    card, _ = _scheduler.review_card(Card.from_dict(item.fsrs), _RATING[grade],
                                     review_datetime=now)
    return item.model_copy(update={"fsrs": card.to_dict()})


def mint_item(new: MintItem, today: date) -> Item:
    return Item(id=f"it-{uuid4().hex[:8]}", concept=new.concept, type=new.type,
                front=new.front, back=new.back, fsrs=Card().to_dict(), created=today)
