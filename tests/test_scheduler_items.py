from datetime import date, datetime, timedelta, timezone

from seba.models import Item, MintItem
from seba.scheduler.items import apply_review, due_items, mint_item


def make_item(id="it-1", due="2026-07-01T00:00:00+00:00", suspended=False):
    return Item(
        id=id,
        concept="c",
        type="recall",
        front="f",
        back="b",
        fsrs={"due": due},
        created=date(2026, 6, 1),
        suspended=suspended,
    )


def test_due_items_filters_sorts_caps():
    items = [
        make_item("a", "2026-07-02T00:00:00+00:00"),
        make_item("b", "2026-06-01T00:00:00+00:00"),
        make_item("c", "2026-08-01T00:00:00+00:00"),
        make_item("d", "2026-06-15T00:00:00+00:00", suspended=True),
    ]
    got = due_items(items, date(2026, 7, 3), limit=2)
    assert [i.id for i in got] == ["b", "a"]


def test_mint_and_review_cycle():
    now = datetime(2026, 7, 3, tzinfo=timezone.utc)
    item = mint_item(
        MintItem(concept="c", type="recall", front="f", back="b"), date(2026, 7, 3)
    )
    assert item.id.startswith("it-") and "due" in item.fsrs
    graded = apply_review(item, "good", now)
    assert graded.fsrs != item.fsrs


def test_skipped_leaves_fsrs_untouched():
    item = make_item()
    assert apply_review(item, "skipped", datetime.now(timezone.utc)) == item


def test_again_due_within_a_day():
    now = datetime(2026, 7, 3, tzinfo=timezone.utc)
    item = mint_item(
        MintItem(concept="c", type="recall", front="f", back="b"), date(2026, 7, 3)
    )
    graded = apply_review(item, "again", now)
    due = datetime.fromisoformat(graded.fsrs["due"])
    assert due <= now + timedelta(days=1)


def test_thirty_day_sim_intervals_grow():
    now = datetime(2026, 7, 3, tzinfo=timezone.utc)
    item = mint_item(
        MintItem(concept="c", type="recall", front="f", back="b"), date(2026, 7, 3)
    )
    intervals = []
    for _ in range(6):
        due = datetime.fromisoformat(item.fsrs["due"])
        now = max(now, due) + timedelta(hours=1)
        item = apply_review(item, "good", now)
        intervals.append((datetime.fromisoformat(item.fsrs["due"]) - now).days)
    assert intervals == sorted(intervals) and intervals[-1] > intervals[0]
