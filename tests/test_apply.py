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
from seba.scheduler.apply import apply_record

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


def done_state(recent: list[str] | None = None):
    s = state()
    s.syllabus.concepts[0] = s.syllabus.concepts[0].model_copy(
        update={"status": "done"}
    )
    return s.model_copy(update={"recent_by_item": {"it-1": recent or []}})


def test_lapsing_card_reopens_its_concept():
    s = done_state(["good"])
    rec = SessionRecord(reviews=[GradeReview(id="it-1", grade="again")])
    out = apply_record(s, rec, NOW)
    assert out.syllabus.concepts[0].status == "in-progress"


def test_reopen_is_idempotent_and_ignores_older_lapses():
    # a still-lapsing concept already reopened last session: no move, no error
    s = state().model_copy(update={"recent_by_item": {"it-1": ["again"]}})
    assert apply_record(s, SessionRecord(), NOW).syllabus.concepts[0].status == "unseen"
    # an `again` older than the last two reviews no longer counts
    stale = done_state(["again", "good", "good"])
    assert (
        apply_record(stale, SessionRecord(), NOW).syllabus.concepts[0].status == "done"
    )


def test_completed_this_session_beats_the_lapse():
    s = state()
    rec = SessionRecord(
        reviews=[GradeReview(id="it-1", grade="again")],
        concepts=[
            UpdateConcept(id="bayes", status_change="started"),
            UpdateConcept(id="bayes", status_change="completed", evidence="e"),
        ],
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
