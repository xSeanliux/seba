from collections.abc import Sequence
from datetime import date
from pathlib import Path

from seba.models import (
    Agenda,
    Concept,
    GoalState,
    Grade,
    Item,
    PaceHint,
    ReviewItem,
    SessionType,
    SubjectProfile,
    TeachConcept,
)
from seba.scheduler.items import due_items
from seba.store.store import parse_notes
from seba.syllabus.graph import confusables, frontier

BRIEFING_BUDGET = 4_000
EXCERPT_BUDGET = 16_000
PRACTICE_QUOTA = {PaceHint.PUSH_HARDER: 5, PaceHint.STEADY: 3, PaceHint.STEP_BACK: 2}
LAPSE_DAYS = 14
SYNTHESIS_EVERY = 5
STUCK_MIN_OPPORTUNITIES = 4  # below this the correctness rate is noise
STUCK_RATE = 0.5


def resolve_excerpt(sources_dir: Path, ref: str, budget: int) -> str | None:
    rel, _, frag = ref.partition("#")
    path = sources_dir / rel
    if not path.exists():
        return None
    try:
        text = path.read_text()
    except (UnicodeDecodeError, OSError):
        return None  # non-text (PDF/binary) or unreadable — skip, don't crash start
    if frag:
        sections, current = {}, None
        for line in text.splitlines():
            if line.lstrip().startswith("#"):
                current = line
                sections[current] = [line]
            elif current:
                sections[current].append(line)
        for heading, lines in sections.items():
            if frag in heading:
                text = "\n".join(lines)
                break
    return text[:budget]


def _pace(recent: Sequence[Grade]) -> PaceHint:
    graded = [g for g in recent if g != Grade.SKIPPED]
    if not graded:
        return PaceHint.STEADY
    rate = sum(g in (Grade.GOOD, Grade.EASY) for g in graded) / len(graded)
    if rate > 0.9:
        return PaceHint.PUSH_HARDER
    if rate < 0.7:
        return PaceHint.STEP_BACK
    return PaceHint.STEADY


def _session_type(state: GoalState, today: date, done: int) -> SessionType:
    last = state.last_session_date
    if last is not None and (today - last).days > LAPSE_DAYS:
        return SessionType.RETURN_AFTER_LAPSE
    if state.session_number % SYNTHESIS_EVERY == 0 and done >= 2:
        return SessionType.SYNTHESIS
    return SessionType.ORDINARY


def _reviews(
    state: GoalState, teach_src: Concept | None, today: date, cap: int
) -> list[Item]:
    """Due ∪ prereqs-of-today ∪ last session's error sites (Rosenshine's daily
    review: due-ness is orthogonal to what today's lesson needs). Due items win
    the cap; the rest fill what's left."""
    picked = due_items(state.items, today, cap)
    seen = {i.id for i in picked}
    warm = set(state.last_session_errors)
    if teach_src is not None:
        warm |= set(teach_src.prereqs) | set(teach_src.soft_prereqs)
    extra = sorted(
        (
            i
            for i in state.items
            if i.concept in warm and i.id not in seen and not i.suspended
        ),
        key=lambda i: (i.concept, i.id),
    )
    return picked + extra[: cap - len(picked)]


def _stuck_lines(state: GoalState) -> list[str]:
    """Wheel-spinning check. A single threshold on correctness after 4
    opportunities is within a few points of a random forest — no classifier."""
    lines = []
    for c in state.syllabus.concepts:
        if c.status != "in-progress":
            continue
        graded = [
            g for g in state.grades_by_concept.get(c.id, []) if g != Grade.SKIPPED
        ]
        if len(graded) < STUCK_MIN_OPPORTUNITIES:
            continue
        rate = sum(g in (Grade.GOOD, Grade.EASY) for g in graded) / len(graded)
        if rate >= STUCK_RATE:
            continue
        n = state.session_number - state.started_at.get(c.id, state.session_number)
        lines.append(
            f"stuck: [{c.id}] in progress for {n} session(s), correctness "
            f"{rate:.2f} over {len(graded)} graded — change approach: split the "
            "concept, drop to a prerequisite, or switch representation."
        )
    return lines


def build_agenda(
    state: GoalState, profile: SubjectProfile, today: date, sources_dir: Path
) -> Agenda:
    concepts = state.syllabus.concepts
    by_id = {c.id: c for c in concepts}
    done = sum(c.status == "done" for c in concepts)
    session_type = _session_type(state, today, done)

    teach_src = None
    if session_type == SessionType.ORDINARY:
        teach_src = next(
            (c for c in concepts if c.status == "in-progress"), None
        ) or next(iter(frontier(state.syllabus)), None)

    picked = _reviews(state, teach_src, today, profile.max_reviews_per_session)
    reviews = [
        ReviewItem(id=i.id, type=i.type, front=i.front, back=i.back) for i in picked
    ]

    teach = None
    scope = {i.concept for i in picked}
    unmastered: list[str] = []
    soft_unmastered: list[str] = []
    if teach_src is not None:
        excerpts, budget = [], EXCERPT_BUDGET
        for ref in teach_src.sources:
            ex = resolve_excerpt(sources_dir, ref, budget)
            if ex:
                excerpts.append(ex)
                budget -= len(ex)
                if budget <= 0:
                    break
        teach = TeachConcept(
            id=teach_src.id,
            name=teach_src.name,
            kc_type=teach_src.kc_type,
            confusable_with=confusables(state.syllabus, teach_src.id),
            sources=teach_src.sources,
            source_excerpts=excerpts,
            guidance=f"estimated {teach_src.est_sessions} session(s)",
        )
        scope |= {teach_src.id, *teach_src.prereqs}
        unmastered = [p for p in teach_src.prereqs if by_id[p].status != "done"]
        soft_unmastered = [
            p for p in teach_src.soft_prereqs if by_id[p].status != "done"
        ]

    front = ", ".join(c.id for c in frontier(state.syllabus)[:10])
    lines = [
        f"Session {state.session_number}. Concepts done: {done}/{len(concepts)}.",
        f"Frontier: {front or 'none'}.",
    ]
    if session_type == SessionType.RETURN_AFTER_LAPSE:
        gap = (today - state.last_session_date).days if state.last_session_date else 0
        lines.append(
            f"Session type: return-after-lapse — {gap} days since the last session. "
            "Triage the backlog and teach no new concept; re-orient briefly, and "
            "frame the gap without guilt."
        )
    elif session_type == SessionType.SYNTHESIS:
        lines.append(
            "Session type: synthesis — no new concept. Have the learner explain how "
            "the concepts already done connect, and push a problem that needs "
            "several of them together."
        )
    if unmastered:
        lines.append(
            f"prereqs not yet done: {', '.join(unmastered)} — offer a short review "
            "before teaching."
        )
    if soft_unmastered:
        lines.append(
            f"soft prereqs not yet done (advisory): {', '.join(soft_unmastered)} — "
            "these don't gate the concept; touch them only if the learner stumbles."
        )
    lines += _stuck_lines(state)
    if state.last_hint:
        lines.append(f"Last session's hint: {state.last_hint}")
    notes = parse_notes(state.notes)
    for cid in sorted(scope):
        grades = state.recent_by_concept.get(cid)
        if grades:
            lines.append(f"[{cid}] recent: " + ", ".join(grades))
        for note in notes.get(cid, [])[:3]:
            lines.append(f"[{cid}] {note}")
    briefing = "\n".join(lines)
    if len(briefing) > BRIEFING_BUDGET:
        briefing = briefing[:BRIEFING_BUDGET] + "\n(older notes omitted)"

    pace = _pace(state.recent_grades)
    return Agenda(
        goal=state.name,
        subject=state.subject,
        session_number=state.session_number,
        briefing=briefing,
        review_items=reviews,
        teach_concept=teach,
        practice_quota=PRACTICE_QUOTA[pace],
        pace_hint=pace,
        session_type=session_type,
    )
