import json
from datetime import date

from typer.testing import CliRunner

from seba.cli import app
from seba.models import Concept, GoalState, Item, Syllabus
from seba.ui.view import build_view_data, render_view

runner = CliRunner()

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


def test_enriched_fields_hint_notes_watch():
    from seba.models import GoalState, Syllabus

    notes = (
        "## a\n- [s003] watch X under pressure\n- [s001] older note\n\n"
        "## b\n- [s004] slips on Y\n\n## c\n- [s002] fine\n\n## d\n- [s001] old\n"
    )
    s = GoalState(
        name="prob",
        subject="probability",
        syllabus=Syllabus(
            goal="prob",
            subject="probability",
            concepts=[Concept(id=x, name=x.upper()) for x in "abcd"],
        ),
        items=[],
        notes=notes,
        last_hint="drill the prior/likelihood split",
        session_number=5,
        recent_grades=[],
    )
    v = build_view_data(s, TODAY)
    assert v.next_hint == "drill the prior/likelihood split"
    by = {c.id: c for c in v.concepts}
    assert by["a"].note == "watch X under pressure"  # newest bullet, marker stripped
    # watch = freshest 3 by session marker, newest first
    assert [(w.id, w.note) for w in v.watch][:2] == [
        ("b", "slips on Y"),
        ("a", "watch X under pressure"),
    ]
    assert len(v.watch) == 3 and v.watch[2].id == "c"


def test_buckets_forecast_next_due():
    def fsrs(due, stability=5.0, state_=2):
        return {"due": due, "stability": stability, "state": state_}

    items = [
        item("it-1", "a"),  # overdue (2020) -> today's forecast bucket; fragile
        Item(
            id="it-2",
            concept="a",
            type="recall",
            front="f",
            back="b",
            fsrs=fsrs("2026-07-18T00:00:00+00:00", stability=20.0),
            created=TODAY,
        ),
        Item(
            id="it-3",
            concept="a",
            type="recall",
            front="f",
            back="b",
            fsrs=fsrs("2026-07-18T00:00:00+00:00", state_=3),
            created=TODAY,
        ),
        Item(
            id="it-4",
            concept="a",
            type="recall",
            front="f",
            back="b",
            fsrs=fsrs("2099-01-01T00:00:00+00:00"),
            created=TODAY,
        ),  # beyond horizon
    ]
    v = build_view_data(state([Concept(id="a", name="A")], items), TODAY)
    assert (v.stats.solid, v.stats.fragile, v.stats.rebuilding) == (1, 2, 1)
    assert len(v.forecast) == 14
    assert v.forecast[0].date == TODAY and v.forecast[0].count == 1  # overdue -> today
    assert v.forecast[3].date == TODAY.replace(day=18) and v.forecast[3].count == 2
    assert sum(d.count for d in v.forecast) == 3  # 2099 card excluded
    [c] = v.concepts
    assert c.next_due == date(2020, 1, 1)  # earliest across cards


def test_deck_carries_card_contents():
    items = [
        item("it-1", "a"),  # front="f", back="b", stability absent -> fragile
        item("it-2", "a", suspended=True),
    ]
    v = build_view_data(state([Concept(id="a", name="A")], items), TODAY)
    [c] = v.concepts
    assert len(c.deck) == 2
    assert (c.deck[0].front, c.deck[0].back, c.deck[0].type) == ("f", "b", "recall")
    assert c.deck[0].bucket == "fragile" and c.deck[0].due == date(2020, 1, 1)
    assert c.deck[1].bucket == "suspended"


def test_render_view_injects_data():
    v = build_view_data(state([Concept(id="a", name="A")]), TODAY)
    html = render_view(v)
    assert "__SEBA_DATA__" not in html
    assert '"goal": "prob"' in html
    assert "<script" in html and "http" not in html.split("<script")[0].lower().replace(
        "http-equiv", ""
    )  # no external URLs before the data script (self-contained head)


def test_render_view_escapes_script_breakout():
    v = build_view_data(state([Concept(id="a", name="tricky </script> name")]), TODAY)
    html = render_view(v)
    # only the template's own closing tag may appear; the data blob must not
    # be able to terminate the <script> block early (silent blank page)
    assert html.count("</script>") == 1
    assert "tricky <\\/script> name" in html


def test_view_cli(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBA_DATA_DIR", str(tmp_path / "data"))
    from seba.models import Syllabus as _S  # local alias to build a real goal
    from seba.store.store import Store

    Store(tmp_path / "data").create_goal(
        "prob",
        _S(goal="prob", subject="probability", concepts=[Concept(id="a", name="A")]),
        "probability",
    )
    result = runner.invoke(app, ["view", "prob", "--json"])
    assert result.exit_code == 0
    blob = json.loads(result.output)
    assert blob["stats"]["concepts_total"] == 1

    result2 = runner.invoke(app, ["view", "prob"])
    assert result2.exit_code == 0
    out = tmp_path / "data" / "goals" / "prob" / "view.html"
    assert out.exists() and str(out) in result2.output
    assert '"concepts_total": 1' in out.read_text()
