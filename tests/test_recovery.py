from pathlib import Path
from types import SimpleNamespace

import pytest
from seba.models import Agenda, Concept, ReviewItem, Syllabus
from seba.session.recovery import RecoveryError, recover_session


def tool_block(id, name, input):
    return SimpleNamespace(type="tool_use", id=id, name=name, input=input)


def msg(blocks, stop="end_turn"):
    return SimpleNamespace(content=blocks, stop_reason=stop)


def fixtures():
    agenda = Agenda(goal="g", subject="probability", session_number=1, briefing="",
                    review_items=[ReviewItem(id="it-1", type="recall", front="f", back="b")],
                    teach_concept=None, practice_quota=3, pace_hint="steady")
    syllabus = Syllabus(goal="g", subject="probability",
                        concepts=[Concept(id="bayes", name="Bayes")])
    return agenda, syllabus


def test_recovery_builds_record(tmp_path: Path):
    agenda, syllabus = fixtures()
    script = [
        msg([tool_block("t1", "grade_review", {"id": "it-1", "grade": "hard"}),
             tool_block("t2", "end_session",
                        {"summary": "recovered", "next_session_hint": "h"})],
            stop="tool_use"),
        msg([]),
    ]
    calls = list(script)
    record = recover_session("TUTOR: hi", agenda, syllabus, tmp_path,
                             lambda s, m: calls.pop(0))
    assert record.complete and record.reviews[0].grade == "hard"
    assert record.summary == "recovered"


def test_recovery_round_cap(tmp_path: Path):
    agenda, syllabus = fixtures()

    def looping_send(system, messages):
        return msg([tool_block("t", "update_concept", {"id": "bayes"})],
                   stop="tool_use")

    with pytest.raises(RecoveryError):
        recover_session("t", agenda, syllabus, tmp_path, looping_send)
