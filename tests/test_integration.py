from datetime import date, datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from seba.models import Concept, Syllabus
from seba.scheduler.agenda import build_agenda
from seba.scheduler.apply import apply_record
from seba.session.dialogue import run_session
from seba.store.store import Store

NOW = datetime(2026, 7, 3, 12, tzinfo=timezone.utc)
TODAY = date(2026, 7, 3)


def text_block(t):
    return SimpleNamespace(type="text", text=t)


def tool_block(id, name, input):
    return SimpleNamespace(type="tool_use", id=id, name=name, input=input)


def msg(blocks, stop="end_turn"):
    return SimpleNamespace(content=blocks, stop_reason=stop)


class SilentIO:
    def get_input(self):
        return None

    def show_chunk(self, text):
        pass

    def show(self, text):
        pass


def scripted(script):
    calls = list(script)
    return lambda system, messages: calls.pop(0)


def run_one(store, profile, script, tmp_path):
    state = store.load_goal("prob")
    agenda = build_agenda(state, profile, TODAY, tmp_path / "sources")
    record, transcript = run_session(agenda, state.syllabus, "", tmp_path,
                                     SilentIO(), scripted(script))
    store.save_session("prob", record, transcript,
                       apply_record(state, record, NOW))
    return agenda, record


def test_session_two_reflects_session_one(tmp_path: Path):
    from seba.session.loader import load_profile
    store = Store(tmp_path / "data")
    store.create_goal("prob", Syllabus(goal="prob", subject="probability",
                                       concepts=[Concept(id="bayes", name="Bayes")]),
                      "probability")
    profile = load_profile("probability")

    # Session 1: teach bayes, note a misconception, mint one card, end.
    s1 = [msg([tool_block("t1", "update_concept",
                          {"id": "bayes", "status_change": "started",
                           "note": "confuses prior with likelihood"}),
               tool_block("t2", "mint_item",
                          {"concept": "bayes", "type": "recall",
                           "front": "State Bayes' theorem", "back": "..."}),
               tool_block("t3", "end_session",
                          {"summary": "Introduced Bayes.",
                           "next_session_hint": "drill the prior/likelihood split"})],
              stop="tool_use"),
          msg([text_block("Bye!")])]
    agenda1, _ = run_one(store, profile, s1, tmp_path)
    assert agenda1.review_items == []  # nothing due on day one

    # Session 2: the minted card is due (new FSRS cards are due immediately);
    # the briefing must carry the note and the hint.
    state2 = store.load_goal("prob")
    assert state2.session_number == 2
    agenda2 = build_agenda(state2, profile, TODAY, tmp_path / "sources")
    [review] = agenda2.review_items
    assert review.front == "State Bayes' theorem"
    assert "confuses prior with likelihood" in agenda2.briefing
    assert "drill the prior/likelihood split" in agenda2.briefing

    # Session 2 runs: grade it good. Under py-fsrs library defaults (spec §12) a
    # fresh card stays in *learning* after one 'good' (rescheduled minutes later,
    # so still due the same calendar day). What continuity requires is that the
    # grade was recorded and the card's FSRS state advanced and persisted — not
    # that a single good "masters" it.
    minted_fsrs = state2.items[0].fsrs
    s2 = [msg([tool_block("t1", "grade_review",
                          {"id": review.id, "grade": "good"}),
               tool_block("t2", "end_session",
                          {"summary": "Drilled.", "next_session_hint": "advance"})],
              stop="tool_use"),
          msg([text_block("Bye!")])]
    run_one(store, profile, s2, tmp_path)
    state3 = store.load_goal("prob")
    assert state3.recent_grades == ["good"]
    # the good grade advanced and persisted the card's FSRS state
    assert state3.items[0].fsrs != minted_fsrs
    assert state3.items[0].fsrs["last_review"] is not None
    # learning card is still due today (defaults reschedule it minutes out)
    agenda3 = build_agenda(state3, profile, TODAY, tmp_path / "sources")
    assert [r.id for r in agenda3.review_items] == [review.id]
