from datetime import date

from seba.models import Concept, GoalState, Item, Syllabus
from seba.ui.view import build_view_data

TODAY = date(2026, 7, 15)


def state(concepts, items=()):
    return GoalState(
        name="prob",
        subject="probability",
        syllabus=Syllabus(goal="prob", subject="probability", concepts=list(concepts)),
        items=list(items),
        session_number=3,
        recent_grades=["good", "again"],
    )


def item(id, concept, due="2020-01-01T00:00:00+00:00", suspended=False):
    return Item(
        id=id,
        concept=concept,
        type="recall",
        front="f",
        back="b",
        fsrs={"due": due},
        created=TODAY,
        suspended=suspended,
    )


def test_layers_and_frontier():
    s = state(
        [
            Concept(id="a", name="A", status="done"),
            Concept(id="b", name="B", prereqs=["a"]),
            Concept(id="c", name="C", prereqs=["a", "b"]),
        ]
    )
    v = build_view_data(s, TODAY)
    by = {c.id: c for c in v.concepts}
    assert (by["a"].layer, by["b"].layer, by["c"].layer) == (0, 1, 2)
    assert v.stats.frontier == ["b"]  # a done, b unlocked, c blocked by b
    assert v.stats.concepts_done == 1 and v.stats.concepts_total == 3


def test_card_counts_and_due():
    s = state(
        [Concept(id="a", name="A")],
        [
            item("it-1", "a"),  # overdue
            item("it-2", "a", due="2099-01-01T00:00:00+00:00"),  # future
            item("it-3", "a", suspended=True),  # suspended: never due
        ],
    )
    v = build_view_data(s, TODAY)
    [c] = v.concepts
    assert (c.cards, c.due) == (3, 1)
    assert (v.stats.cards_total, v.stats.cards_due) == (3, 1)
    assert v.generated == TODAY and v.recent_grades == ["good", "again"]
