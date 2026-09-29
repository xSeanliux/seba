from collections.abc import Sequence
from datetime import date
from pathlib import Path

from seba.models import (
    Agenda,
    Concept,
    Emphasis,
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
from seba.syllabus.graph import check_teachable, confusables, frontier

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
    """Due ∪ prereqs-of-today ∪ last session's error sites, the concepts with a
    card graded `again` (Rosenshine's daily review: due-ness is orthogonal to
    what today's lesson needs). Due items win the cap; the rest fill what's
    left. A dropped concept's cards are left out, their due dates untouched."""
    dropped = {c.id for c in state.syllabus.concepts if c.status == "dropped"}
    items = [i for i in state.items if i.concept not in dropped]
    picked = due_items(items, today, cap)
    seen = {i.id for i in picked}
    warm = set(state.last_session_errors)
    if teach_src is not None:
        warm |= set(teach_src.prereqs) | set(teach_src.soft_prereqs)
    extra = sorted(
        (
            i
            for i in items
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


def _trouble_lines(state: GoalState) -> list[str]:
    """What went wrong last session, in the tutor's own words. Reporting only:
    the scheduler has already decided when each of these cards comes back."""
    concept_of = {i.id: i.concept for i in state.items}
    done = {c.id for c in state.syllabus.concepts if c.status == "done"}
    dropped = {c.id for c in state.syllabus.concepts if c.status == "dropped"}
    lines = []
    for r in state.last_trouble:
        cid = concept_of.get(r.id)
        if cid is None or cid in dropped:
            continue  # card since deleted, or its concept set aside
        note = " ".join((r.note or "").split())  # a newline would split the line
        said = f' — "{note}"' if note else ""
        if r.grade == Grade.AGAIN:
            n = state.again_runs.get(r.id, 1)
            # Only a done concept can be reopened; one still being taught (or
            # carded before teaching started) is repaired where it stands.
            then = (
                "Propose re-teaching if the repair doesn't hold."
                if cid in done
                else "Still in progress: repair it this session."
            )
            lines.append(
                f"slipped: [{cid}] {r.id}, {n} session{'' if n == 1 else 's'} "
                f"running{said}. {then}"
            )
        else:
            lines.append(
                f"hard: [{cid}] {r.id}, passed with help{said}. Touch on it in "
                "conversation; the schedule is unchanged."
            )
    return lines


def _emphasis_lines(state: GoalState) -> list[str]:
    often = {Emphasis.MORE: "more", Emphasis.LESS: "less"}
    # A dropped concept's cards are not reviewed, so there is nothing to expect.
    dropped = {c.id for c in state.syllabus.concepts if c.status == "dropped"}
    return [
        f"emphasis: [{cid}] {e} — the learner asked to see these cards "
        f"{often[e]} often."
        for cid, e in sorted(state.emphasis.items())
        if cid not in dropped
    ]


def _teach(
    state: GoalState, src: Concept, sources_dir: Path, budget: int
) -> tuple[TeachConcept, int]:
    excerpts = []
    for ref in src.sources:
        if budget <= 0:
            break
        ex = resolve_excerpt(sources_dir, ref, budget)
        if ex:
            excerpts.append(ex)
            budget -= len(ex)
    teach = TeachConcept(
        id=src.id,
        name=src.name,
        kc_type=src.kc_type,
        confusable_with=confusables(state.syllabus, src.id),
        sources=src.sources,
        source_excerpts=excerpts,
        guidance=f"estimated {src.est_sessions} session(s)",
    )
    return teach, budget


def build_agenda(
    state: GoalState,
    profile: SubjectProfile,
    today: date,
    sources_dir: Path,
    *,
    teach: str | None = None,
) -> Agenda:
    concepts = state.syllabus.concepts
    by_id = {c.id: c for c in concepts}
    done = sum(c.status == "done" for c in concepts)
    session_type = _session_type(state, today, done)
    lapsed = session_type == SessionType.RETURN_AFTER_LAPSE
    gap = (today - state.last_session_date).days if state.last_session_date else 0
    # The learner asked for a concept: that outranks a synthesis or
    # return-after-lapse day.
    steered = check_teachable(state.syllabus, teach) if teach is not None else None
    if steered is not None:
        session_type = SessionType.ORDINARY

    ready: list[Concept] = []
    if session_type == SessionType.ORDINARY:
        in_progress = [c for c in concepts if c.status == "in-progress"]
        rest = [c for c in frontier(state.syllabus) if c.status != "in-progress"]
        ready = in_progress + rest
        if steered is not None:
            ready = [steered] + [c for c in ready if c.id != steered.id]
        ready = ready[: state.settings.concepts_per_session]
    teach_src = ready[0] if ready else None

    picked = _reviews(state, teach_src, today, profile.max_reviews_per_session)
    reviews = [
        ReviewItem(id=i.id, type=i.type, front=i.front, back=i.back, concept=i.concept)
        for i in picked
    ]

    taught = None
    following: list[TeachConcept] = []
    scope = {i.concept for i in picked}
    unmastered: list[str] = []
    soft_unmastered: list[str] = []
    if teach_src is not None:
        taught, budget = _teach(state, teach_src, sources_dir, EXCERPT_BUDGET)
        for src in ready[1:]:
            follow, budget = _teach(state, src, sources_dir, budget)
            following.append(follow)
        scope |= {teach_src.id, *teach_src.prereqs, *(c.id for c in ready[1:])}
        unmastered = [p for p in teach_src.prereqs if by_id[p].status != "done"]
        soft_unmastered = [
            p for p in teach_src.soft_prereqs if by_id[p].status != "done"
        ]

    front = ", ".join(c.id for c in frontier(state.syllabus)[:10])
    unseen = [c.id for c in concepts if c.status == "unseen"]
    dropped = sum(c.status == "dropped" for c in concepts)
    lines = [
        *([f"Direction: {state.direction}"] if state.direction else []),
        f"Session {state.session_number}. Concepts: {done} done, "
        f"{len(concepts) - done - dropped} open"
        + (f", {dropped} dropped." if dropped else "."),
        f"Frontier: {front or 'none'}.",
    ]
    if session_type == SessionType.RETURN_AFTER_LAPSE:
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
    if steered is not None:
        lines.append(f"steered: the learner asked for [{steered.id}] today.")
        if lapsed:
            lines.append(
                f"away: {gap} days since the last session — acknowledge it "
                "briefly and without guilt, then teach what the learner asked for."
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
    if following:
        when = (
            "start it only once the current concept"
            if len(following) == 1
            else "start each only once the one before it"
        )
        lines.append(
            f"next: {', '.join(c.id for c in following)} — {when} reaches a "
            "stopping point; ending the session there is always fine."
        )
    if len(unseen) <= 1:
        left = (
            f"nearly out of syllabus: 1 concept left unseen ({unseen[0]})"
            if unseen
            else "out of syllabus: no concept left unseen"
        )
        lines.append(
            f"{left} — propose what comes next, or confirm with the learner "
            "that the goal is finished."
        )
    lines += _stuck_lines(state)
    lines += _trouble_lines(state)
    lines += _emphasis_lines(state)
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
        teach_concept=taught,
        next_concepts=following,
        practice_quota=PRACTICE_QUOTA[pace],
        pace_hint=pace,
        session_type=session_type,
    )
