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
