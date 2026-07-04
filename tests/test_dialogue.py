from pathlib import Path
from types import SimpleNamespace

from seba.models import Agenda, Concept, ReviewItem, Syllabus
from seba.session.dialogue import run_session


def text_block(t):
    return SimpleNamespace(type="text", text=t)


def tool_block(id, name, input):
    return SimpleNamespace(type="tool_use", id=id, name=name, input=input)


def msg(blocks, stop="end_turn"):
    return SimpleNamespace(content=blocks, stop_reason=stop)


class ScriptedIO:
    def __init__(self, inputs):
        self.inputs = list(inputs)
        self.shown = []

    def get_input(self):
        return self.inputs.pop(0) if self.inputs else None

    def show_chunk(self, text):
        self.shown.append(text)

    def show(self, text):
        self.shown.append(text)


def make_send(script):
    calls = list(script)

    def send(system, messages):
        return calls.pop(0)
    return send


def fixtures():
    agenda = Agenda(goal="g", subject="probability", session_number=1, briefing="b",
                    review_items=[ReviewItem(id="it-1", type="recall", front="f", back="b")],
                    teach_concept=None, practice_quota=3, pace_hint="steady")
    syllabus = Syllabus(goal="g", subject="probability",
                        concepts=[Concept(id="bayes", name="Bayes")])
    return agenda, syllabus


def test_full_session_with_tools(tmp_path: Path):
    agenda, syllabus = fixtures()
    script = [
        msg([text_block("Welcome back! State Bayes?")]),
        msg([tool_block("t1", "grade_review", {"id": "it-1", "grade": "good"}),
             text_block("Correct!")], stop="tool_use"),
        msg([text_block("Anything else?")]),
        msg([tool_block("t2", "end_session",
                        {"summary": "Reviewed Bayes.", "next_session_hint": "go on"})],
            stop="tool_use"),
        msg([text_block("Bye!")]),
    ]
    io = ScriptedIO(["P(A|B) = P(B|A)P(A)/P(B)", "/done"])
    record, transcript = run_session(agenda, syllabus, "", tmp_path, io,
                                     make_send(script))
    assert record.complete and record.reviews[0].grade == "good"
    assert "Welcome back!" in transcript and "LEARNER:" in transcript


def test_done_with_missing_grades_injects_reminder(tmp_path: Path):
    agenda, syllabus = fixtures()
    script = [
        msg([text_block("Hi!")]),
        # after /done reminder, model grades then ends
        msg([tool_block("t1", "grade_review", {"id": "it-1", "grade": "skipped"}),
             tool_block("t2", "end_session",
                        {"summary": "s", "next_session_hint": "h"})], stop="tool_use"),
        msg([text_block("Bye")]),
    ]
    io = ScriptedIO(["/done"])
    record, _ = run_session(agenda, syllabus, "", tmp_path, io, make_send(script))
    assert record.complete and record.reviews[0].grade == "skipped"


def test_eof_returns_incomplete(tmp_path: Path):
    agenda, syllabus = fixtures()
    script = [msg([text_block("Hi!")])]
    io = ScriptedIO([])  # immediate EOF
    record, transcript = run_session(agenda, syllabus, "", tmp_path, io,
                                     make_send(script))
    assert not record.complete and "Hi!" in transcript


def test_tool_error_fed_back(tmp_path: Path):
    agenda, syllabus = fixtures()
    captured = []

    def send(system, messages):
        captured.append([m for m in messages])
        if len(captured) == 1:
            return msg([tool_block("t1", "grade_review",
                                   {"id": "it-99", "grade": "good"})], stop="tool_use")
        return msg([text_block("oops, retrying")])

    io = ScriptedIO([])
    record, _ = run_session(agenda, syllabus, "", tmp_path, io, send)
    # second call's messages must include an error tool_result
    last = captured[-1][-1]
    assert last["role"] == "user"
    assert last["content"][0]["type"] == "tool_result"
    assert last["content"][0]["is_error"] is True
