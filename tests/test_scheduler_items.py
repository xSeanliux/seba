from datetime import date, datetime, timedelta, timezone

import pytest
from fsrs import Card, Rating, Scheduler, State

from seba.models import Emphasis, GoalSettings, Item, MintItem
from seba.scheduler.items import apply_review, due_items, mint_item, target_retention

NOW = datetime(2026, 7, 3, tzinfo=timezone.utc)
DEFAULTS = GoalSettings()


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
    graded = apply_review(item, "good", now, DEFAULTS, None)
    assert graded.fsrs != item.fsrs


def test_skipped_leaves_fsrs_untouched():
    item = make_item()
    assert (
        apply_review(item, "skipped", datetime.now(timezone.utc), DEFAULTS, None)
        == item
    )


def test_again_due_within_a_day():
    now = datetime(2026, 7, 3, tzinfo=timezone.utc)
    item = mint_item(
        MintItem(concept="c", type="recall", front="f", back="b"), date(2026, 7, 3)
    )
    graded = apply_review(item, "again", now, DEFAULTS, None)
    due = datetime.fromisoformat(graded.fsrs["due"])
    assert due <= now + timedelta(days=1)


def test_thirty_day_sim_intervals_grow():
    now = datetime(2026, 7, 3, tzinfo=timezone.utc)
    item = mint_item(
        MintItem(concept="c", type="recall", front="f", back="b"), date(2026, 7, 3)
    )
    # A ceiling that never binds: under the default 180 days, fuzz near the
    # ceiling makes the last intervals wobble, and the ceiling has its own test.
    uncapped = GoalSettings(max_interval_days=36500)
    intervals = []
    for _ in range(6):
        due = datetime.fromisoformat(item.fsrs["due"])
        now = max(now, due) + timedelta(hours=1)
        item = apply_review(item, "good", now, uncapped, None)
        intervals.append((datetime.fromisoformat(item.fsrs["due"]) - now).days)
    assert intervals == sorted(intervals) and intervals[-1] > intervals[0]


def new_card():
    return mint_item(
        MintItem(concept="c", type="recall", front="f", back="b"), date(2026, 7, 3)
    )


def days(item, since):
    return (datetime.fromisoformat(item.fsrs["due"]) - since).days


@pytest.fixture
def no_fuzz(monkeypatch):
    # The midpoint of the fuzz range, so intervals are deterministic.
    monkeypatch.setattr("fsrs.scheduler.random", lambda: 0.5)


@pytest.mark.parametrize(
    "settings,emphasis,expected",
    [
        (GoalSettings(), None, 0.90),
        (GoalSettings(), Emphasis.MORE, 0.95),
        (GoalSettings(), Emphasis.LESS, 0.80),
        (GoalSettings(desired_retention=0.95), Emphasis.MORE, 0.97),
        (GoalSettings(desired_retention=0.75), Emphasis.LESS, 0.70),
    ],
)
def test_target_retention(settings, emphasis, expected):
    assert target_retention(settings, emphasis) == pytest.approx(expected)


def test_hard_on_a_new_card_yields_at_least_a_day():
    graded = apply_review(new_card(), "hard", NOW, DEFAULTS, None)
    assert days(graded, NOW) >= 1
    assert graded.fsrs["state"] == State.Review


def test_struggler_history_grows(no_fuzz):
    # The history that kept one card at zero days for five sessions.
    item, now, intervals = new_card(), NOW, []
    for grade in ["again", "hard", "hard", "hard", "hard", "good", "easy"]:
        item = apply_review(item, grade, now, DEFAULTS, None)
        intervals.append(days(item, now))
        # sessions are three days apart; a card is never reviewed before it is due
        now = max(datetime.fromisoformat(item.fsrs["due"]), now + timedelta(days=3))
    assert intervals[0] >= 1
    assert intervals == sorted(set(intervals))  # strictly growing


def test_no_interval_exceeds_the_ceiling():
    settings = GoalSettings(max_interval_days=30)
    item, now, intervals = new_card(), NOW, []
    for _ in range(8):
        item = apply_review(item, "easy", now, settings, None)
        intervals.append(days(item, now))
        now = datetime.fromisoformat(item.fsrs["due"])
    # Fuzz is on and may land a day or two under the ceiling, never over it.
    assert max(intervals) <= 30
    assert intervals[-1] >= 25  # the ceiling is what is binding by now


def test_emphasis_shifts_the_interval(no_fuzz):
    def after_three_goods(emphasis):
        item, now = new_card(), NOW
        for _ in range(3):
            item = apply_review(item, "good", now, DEFAULTS, emphasis)
            last = days(item, now)
            now = datetime.fromisoformat(item.fsrs["due"])
        return last

    more, normal, less = (
        after_three_goods(e) for e in (Emphasis.MORE, None, Emphasis.LESS)
    )
    assert more < normal < less


@pytest.mark.parametrize("grade", ["again", "hard", "good", "easy"])
def test_a_stored_learning_card_graduates(grade):
    # Existing goals hold cards in Learning with a step set, written by a
    # scheduler that had learning steps.
    card, _ = Scheduler().review_card(Card(), Rating.Hard, review_datetime=NOW)
    assert card.state == State.Learning and card.step == 0
    item = new_card().model_copy(update={"fsrs": dict(card.to_dict())})
    later = NOW + timedelta(days=3)
    graded = apply_review(item, grade, later, DEFAULTS, None)
    assert graded.fsrs["state"] == State.Review and graded.fsrs["step"] is None
    assert days(graded, later) >= 1


def test_a_card_due_past_the_ceiling_is_capped_at_its_next_review():
    due = NOW + timedelta(days=400)
    fsrs = dict(Card().to_dict())
    fsrs.update(
        state=State.Review.value,
        step=None,
        stability=400.0,
        difficulty=5.0,
        due=due.isoformat(),
        last_review=NOW.isoformat(),
    )
    item = new_card().model_copy(update={"fsrs": fsrs})
    graded = apply_review(item, "good", due, DEFAULTS, None)
    assert days(graded, due) <= 180
