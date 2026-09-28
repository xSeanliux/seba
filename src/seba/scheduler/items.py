from datetime import date, datetime, time, timezone
from typing import cast
from uuid import uuid4

from fsrs import Card, Rating, Scheduler
from fsrs.card import CardDict

from seba.models import (
    RETENTION_MAX,
    RETENTION_MIN,
    Emphasis,
    GoalSettings,
    Grade,
    Item,
    MintItem,
)

_RATING = {
    "again": Rating.Again,
    "hard": Rating.Hard,
    "good": Rating.Good,
    "easy": Rating.Easy,
}
_SHIFT = {Emphasis.MORE: 0.05, Emphasis.LESS: -0.10}


def target_retention(settings: GoalSettings, emphasis: Emphasis | None) -> float:
    shift = _SHIFT[emphasis] if emphasis is not None else 0.0
    return min(RETENTION_MAX, max(RETENTION_MIN, settings.desired_retention + shift))


def due_items(items: list[Item], today: date, limit: int) -> list[Item]:
    cutoff = today.isoformat()
    due = [
        i
        for i in items
        if not i.suspended and str(i.fsrs.get("due", ""))[:10] <= cutoff
    ]
    due.sort(key=lambda i: str(i.fsrs["due"]))
    return due[:limit]


def apply_review(
    item: Item,
    grade: Grade,
    now: datetime,
    settings: GoalSettings,
    emphasis: Emphasis | None,
) -> Item:
    if grade == "skipped":
        return item
    # No learning or relearning steps: those are minutes, for re-showing a card
    # in the same sitting, and sessions are days apart. Every grade then yields
    # at least a day and `hard` grows the interval.
    scheduler = Scheduler(
        desired_retention=target_retention(settings, emphasis),
        learning_steps=(),
        relearning_steps=(),
        maximum_interval=settings.max_interval_days,
    )
    card, _ = scheduler.review_card(
        Card.from_dict(cast(CardDict, item.fsrs)), _RATING[grade], review_datetime=now
    )
    return item.model_copy(update={"fsrs": dict(card.to_dict())})


def _start_of(today: date) -> str:
    return datetime.combine(today, time.min, tzinfo=timezone.utc).isoformat()


def due_now(item: Item, today: date) -> Item:
    """Make a card due today. Used only when the learner sets emphasis `more`."""
    return item.model_copy(update={"fsrs": {**item.fsrs, "due": _start_of(today)}})


def mint_item(new: MintItem, today: date) -> Item:
    # py-fsrs stamps a new Card.due from the wall clock; override it to `today`
    # so scheduling stays deterministic in the passed date (spec §M2) and a
    # freshly minted card is due the day it is created.
    fsrs = dict(Card().to_dict())
    fsrs["due"] = _start_of(today)
    return Item(
        id=f"it-{uuid4().hex[:8]}",
        concept=new.concept,
        type=new.type,
        front=new.front,
        back=new.back,
        fsrs=fsrs,
        created=today,
    )
