import yaml
from typer.testing import CliRunner

from seba.cli import app
from seba.store.store import Store

runner = CliRunner()

SYLLABUS = (
    "goal: prob\nsubject: probability\nconcepts:\n  - id: bayes\n    name: Bayes\n"
)


def invoke_ok(args):
    result = runner.invoke(app, args)
    assert result.exit_code == 0, f"{args} failed: {result.output} {result.exception}"
    return result


def test_session_two_reflects_session_one(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBA_DATA_DIR", str(tmp_path / "data"))
    f = tmp_path / "syllabus.yaml"
    f.write_text(SYLLABUS)
    invoke_ok(["new-goal", "prob", "--subject", "probability", "--from-file", str(f)])

    # --- Session 1: teach, note a misconception, mint a card, end.
    out1 = yaml.safe_load(invoke_ok(["start", "prob"]).output)
    assert out1["ungraded_reviews"] == []  # nothing due on day one
    assert out1["agenda"]["teach_concept"]["id"] == "bayes"
    invoke_ok(
        [
            "concept",
            "prob",
            "bayes",
            "--status",
            "started",
            "--note",
            "confuses prior with likelihood",
        ]
    )
    invoke_ok(
        [
            "mint",
            "prob",
            "--concept",
            "bayes",
            "--type",
            "recall",
            "--front",
            "State Bayes' theorem",
            "--back",
            "P(A|B)=...",
        ]
    )
    invoke_ok(
        [
            "end",
            "prob",
            "--summary",
            "Introduced Bayes.",
            "--hint",
            "drill the prior/likelihood split",
        ]
    )

    # --- Session 2: the minted card is due; briefing carries note + hint.
    out2 = yaml.safe_load(invoke_ok(["start", "prob"]).output)
    [review] = out2["agenda"]["review_items"]
    assert review["front"] == "State Bayes' theorem"
    assert "confuses prior with likelihood" in out2["agenda"]["briefing"]
    assert "drill the prior/likelihood split" in out2["agenda"]["briefing"]

    # end is gated until the review is graded
    blocked = runner.invoke(app, ["end", "prob", "--summary", "s", "--hint", "h"])
    assert blocked.exit_code == 1

    invoke_ok(["grade", "prob", review["id"], "good"])
    invoke_ok(["end", "prob", "--summary", "Drilled.", "--hint", "advance"])

    # --- Continuity assertions straight off disk.
    store = Store(tmp_path / "data")
    gs = store.load_goal("prob")
    assert gs.session_number == 3
    assert gs.recent_grades == ["good"]
    assert gs.items[0].fsrs["last_review"] is not None  # FSRS state advanced+persisted
    assert gs.syllabus.concepts[0].status == "in-progress"
