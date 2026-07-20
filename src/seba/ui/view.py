import json
import re
from datetime import date, timedelta
from graphlib import TopologicalSorter
from importlib.resources import files

from seba.models import (
    ForecastDay,
    GoalState,
    Status,
    ViewCard,
    ViewConcept,
    ViewData,
    ViewStats,
    WatchItem,
)
from seba.store.store import parse_notes
from seba.syllabus.graph import frontier

FORECAST_DAYS = 14
SOLID_STABILITY = 14.0  # FSRS stability (days) above which a memory reads "solid"
_SESSION_MARK = re.compile(r"^\[s(\d+)\]\s*")


def _latest_note(lines: list[str]) -> tuple[str, int] | None:
    """Newest note (notes.md bullets are prepended) -> (text, session_no)."""
    if not lines:
        return None
    raw = lines[0].lstrip("- ").strip()
    m = _SESSION_MARK.match(raw)
    return _SESSION_MARK.sub("", raw), int(m.group(1)) if m else 0


def _bucket(item) -> str:
    fsrs = item.fsrs
    if str(fsrs.get("state", "")) in ("3", "State.Relearning", "Relearning"):
        return "rebuilding"
    stability = fsrs.get("stability") or 0.0
    return "solid" if stability >= SOLID_STABILITY else "fragile"


def _due_date(item) -> date | None:
    raw = str(item.fsrs.get("due", ""))[:10]
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def build_view_data(state: GoalState, today: date) -> ViewData:
    concepts = state.syllabus.concepts
    by_id = {c.id: c for c in concepts}
    order = TopologicalSorter({c.id: set(c.prereqs) for c in concepts}).static_order()
    layer: dict[str, int] = {}
    for cid in order:
        layer[cid] = 1 + max((layer[p] for p in by_id[cid].prereqs), default=-1)

    cutoff = today.isoformat()

    def is_due(i) -> bool:
        return not i.suspended and str(i.fsrs.get("due", ""))[:10] <= cutoff

    notes_map = parse_notes(state.notes)

    view_concepts = []
    watch_candidates: list[tuple[int, WatchItem]] = []
    for c in concepts:
        cards = [i for i in state.items if i.concept == c.id]
        latest = _latest_note(notes_map.get(c.id, []))
        if latest is not None:
            note, session_no = latest
            watch_candidates.append(
                (session_no, WatchItem(id=c.id, name=c.name, note=note))
            )
        due_dates = [
            d for i in cards if not i.suspended and (d := _due_date(i)) is not None
        ]
        deck = [
            ViewCard(
                type=i.type,
                front=i.front,
                back=i.back,
                due=_due_date(i),
                bucket="suspended" if i.suspended else _bucket(i),
            )
            for i in cards
        ]
        view_concepts.append(
            ViewConcept(
                id=c.id,
                name=c.name,
                status=c.status,
                layer=layer[c.id],
                prereqs=c.prereqs,
                cards=len(cards),
                due=sum(1 for i in cards if is_due(i)),
                est_sessions=c.est_sessions,
                note=latest[0] if latest else None,
                next_due=min(due_dates) if due_dates else None,
                deck=deck,
            )
        )
    watch_candidates.sort(key=lambda t: t[0], reverse=True)  # freshest session first
    watch = [w for _, w in watch_candidates[:3]]

    live = [i for i in state.items if not i.suspended]
    buckets = {"solid": 0, "fragile": 0, "rebuilding": 0}
    for i in live:
        buckets[_bucket(i)] += 1

    # 14-day due forecast; anything overdue lands in today's bucket
    per_day = {today + timedelta(days=n): 0 for n in range(FORECAST_DAYS)}
    horizon = today + timedelta(days=FORECAST_DAYS - 1)
    for i in live:
        d = _due_date(i)
        if d is None or d > horizon:
            continue
        per_day[max(d, today)] += 1
    forecast = [ForecastDay(date=d, count=n) for d, n in sorted(per_day.items())]

    stats = ViewStats(
        concepts_done=sum(c.status == Status.DONE for c in concepts),
        concepts_total=len(concepts),
        cards_total=len(state.items),
        cards_due=sum(1 for i in state.items if is_due(i)),
        frontier=[c.id for c in frontier(state.syllabus)],
        solid=buckets["solid"],
        fragile=buckets["fragile"],
        rebuilding=buckets["rebuilding"],
    )
    return ViewData(
        goal=state.name,
        subject=state.subject,
        session_number=state.session_number,
        generated=today,
        stats=stats,
        concepts=view_concepts,
        recent_grades=state.recent_grades,
        next_hint=state.last_hint,
        forecast=forecast,
        watch=watch,
    )


def render_view(data: ViewData) -> str:
    template = files("seba.ui").joinpath("view_template.html").read_text()
    # json.dumps doesn't escape "/", so a name containing "</script>" would
    # close the data <script> block early and silently blank the page.
    blob = json.dumps(data.model_dump(mode="json")).replace("</", "<\\/")
    return template.replace("__SEBA_DATA__", blob)
