from datetime import date, datetime, timedelta, timezone

from fsrs import Card

from seba.models import (
    Concept,
    Emphasis,
    GoalSettings,
    GoalState,
    GradeReview,
    Item,
    MintItem,
    SessionRecord,
    Syllabus,
    UpdateConcept,
)
from seba.scheduler.apply import apply_change, apply_record, replay

NOW = datetime(2026, 7, 3, tzinfo=timezone.utc)


def _fsrs(due="2026-07-01T00:00:00+00:00"):
    # A real, full py-fsrs card dict (Card.from_dict requires every field);
    # override only `due` so the review clearly shifts it.
    d = Card().to_dict()
    d["due"] = due
    return d


def state():
    return GoalState(
        name="g",
        subject="probability",
        syllabus=Syllabus(
            goal="g",
            subject="probability",
            concepts=[Concept(id="bayes", name="B", status="unseen")],
        ),
        items=[
            Item(
                id="it-1",
                concept="bayes",
                type="recall",
                front="f",
                back="b",
                fsrs=_fsrs(),
                created=date(2026, 6, 1),
            )
        ],
        session_number=1,
    )


def test_apply_grades_mints_and_statuses():
    rec = SessionRecord(
        reviews=[GradeReview(id="it-1", grade="good")],
        new_items=[MintItem(concept="bayes", type="recall", front="nf", back="nb")],
        concepts=[UpdateConcept(id="bayes", status_change="started")],
        summary="s",
        next_session_hint="h",
        complete=True,
    )
    out = apply_record(state(), rec, NOW)
    assert len(out.items) == 2
    assert out.items[0].fsrs["due"] != "2026-07-01T00:00:00+00:00"
    assert out.syllabus.concepts[0].status == "in-progress"


def test_skipped_and_unknown_ids_are_safe():
    s = state()  # capture once: Card() mints a fresh card_id each call
    rec = SessionRecord(
        reviews=[
            GradeReview(id="it-1", grade="skipped"),
            GradeReview(id="it-ghost", grade="good"),
        ],
        concepts=[UpdateConcept(id="bayes", status_change="completed", evidence="e")],
    )  # illegal jump
    out = apply_record(s, rec, NOW)
    assert out.items[0] == s.items[0]
    assert out.syllabus.concepts[0].status == "unseen"  # illegal move skipped, no error


def done_state():
    s = state()
    s.syllabus.concepts[0] = s.syllabus.concepts[0].model_copy(
        update={"status": "done"}
    )
    return s


def test_an_again_leaves_a_done_concept_done():
    rec = SessionRecord(reviews=[GradeReview(id="it-1", grade="again", note="n")])
    out = apply_record(done_state(), rec, NOW)
    assert out.syllabus.concepts[0].status == "done"


def test_reopened_moves_done_to_in_progress():
    rec = SessionRecord(concepts=[UpdateConcept(id="bayes", status_change="reopened")])
    out = apply_record(done_state(), rec, NOW)
    assert out.syllabus.concepts[0].status == "in-progress"


def test_started_leaves_a_done_concept_done():
    # a pending session written before `reopened` existed can still say `started`
    rec = SessionRecord(concepts=[UpdateConcept(id="bayes", status_change="started")])
    out = apply_record(done_state(), rec, NOW)
    assert out.syllabus.concepts[0].status == "done"


def test_started_after_completed_in_one_session_leaves_it_done():
    s = state()
    s.syllabus.concepts[0] = s.syllabus.concepts[0].model_copy(
        update={"status": "in-progress"}
    )
    rec = SessionRecord(
        concepts=[
            UpdateConcept(id="bayes", status_change="completed", evidence="e"),
            UpdateConcept(id="bayes", status_change="started"),
        ]
    )
    out = apply_record(s, rec, NOW)
    assert out.syllabus.concepts[0].status == "done"


def test_apply_record_uses_the_goals_settings_and_emphasis(monkeypatch):
    monkeypatch.setattr("fsrs.scheduler.random", lambda: 0.5)
    rec = SessionRecord(reviews=[GradeReview(id="it-1", grade="easy")])

    def due_after(**update):
        s = state().model_copy(update=update)
        out = apply_record(s, rec, NOW)
        return datetime.fromisoformat(out.items[0].fsrs["due"])

    normal = due_after()
    assert due_after(emphasis={"bayes": Emphasis.MORE}) < normal
    assert due_after(emphasis={"other": Emphasis.MORE}) == normal
    capped = due_after(settings=GoalSettings(max_interval_days=2))
    assert capped - NOW <= timedelta(days=2)


def test_an_unreviewed_card_keeps_its_due_date():
    # Settings take effect at a card's next review; stored dates are not rewritten.
    far = "2028-01-01T00:00:00+00:00"
    s = state()
    s.items[0] = s.items[0].model_copy(update={"fsrs": _fsrs(far)})
    out = apply_record(s, SessionRecord(), NOW)
    assert out.items[0].fsrs["due"] == far


def _syl(status="unseen"):
    return Syllabus(
        goal="g",
        subject="probability",
        concepts=[Concept(id="bayes", name="B", status=status)],
    )


def test_replay_skips_an_illegal_move_and_applies_the_rest():
    changes = [
        UpdateConcept(id="bayes", status_change="completed", evidence="e"),  # illegal
        UpdateConcept(id="bayes", status_change="started"),
        UpdateConcept(id="bayes", status_change="started"),  # a repeat: skipped
        UpdateConcept(id="bayes", status_change="completed", evidence="e"),
        UpdateConcept(id="bayes", status_change="reopened"),
        UpdateConcept(id="bayes", note="a note moves nothing"),
    ]
    assert replay(_syl(), changes).concepts[0].status == "in-progress"
    out = apply_record(state(), SessionRecord(concepts=changes), NOW)
    assert out.syllabus == replay(_syl(), changes)


def test_apply_change_without_a_move_returns_the_syllabus():
    s = _syl()
    assert apply_change(s, UpdateConcept(id="bayes", note="n")) is s
