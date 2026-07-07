from collections.abc import Sequence
from datetime import date
from pathlib import Path

from seba.models import (
    Agenda,
    GoalState,
    Grade,
    PaceHint,
    ReviewItem,
    SubjectProfile,
    TeachConcept,
)
from seba.scheduler.items import due_items
from seba.store.store import parse_notes
from seba.syllabus.graph import frontier

BRIEFING_BUDGET = 4_000
EXCERPT_BUDGET = 16_000


def resolve_excerpt(sources_dir: Path, ref: str, budget: int) -> str | None:
    rel, _, frag = ref.partition("#")
    path = sources_dir / rel
    if not path.exists():
        return None
    text = path.read_text()
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


def build_agenda(
    state: GoalState, profile: SubjectProfile, today: date, sources_dir: Path
) -> Agenda:
    due = due_items(state.items, today, profile.max_reviews_per_session)
    reviews = [
        ReviewItem(id=i.id, type=i.type, front=i.front, back=i.back) for i in due
    ]

    concepts = state.syllabus.concepts
    teach_src = next((c for c in concepts if c.status == "in-progress"), None) or next(
        iter(frontier(state.syllabus)), None
    )
    teach = None
    scope = {i.concept for i in state.items if i.id in {r.id for r in reviews}}
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
            sources=teach_src.sources,
            source_excerpts=excerpts,
            guidance=f"estimated {teach_src.est_sessions} session(s)",
        )
        scope |= {teach_src.id, *teach_src.prereqs}

    done = sum(c.status == "done" for c in concepts)
    front = ", ".join(c.id for c in frontier(state.syllabus)[:10])
    lines = [
        f"Session {state.session_number}. Concepts done: {done}/{len(concepts)}.",
        f"Frontier: {front or 'none'}.",
    ]
    if state.last_hint:
        lines.append(f"Last session's hint: {state.last_hint}")
    notes = parse_notes(state.notes)
    for cid in sorted(scope):
        for note in notes.get(cid, [])[:3]:
            lines.append(f"[{cid}] {note}")
    briefing = "\n".join(lines)
    if len(briefing) > BRIEFING_BUDGET:
        briefing = briefing[:BRIEFING_BUDGET] + "\n(older notes omitted)"

    return Agenda(
        goal=state.name,
        subject=state.subject,
        session_number=state.session_number,
        briefing=briefing,
        review_items=reviews,
        teach_concept=teach,
        practice_quota=3,
        pace_hint=_pace(state.recent_grades),
    )
