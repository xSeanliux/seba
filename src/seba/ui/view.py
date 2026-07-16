import json
from datetime import date
from graphlib import TopologicalSorter
from importlib.resources import files

from seba.models import GoalState, Status, ViewConcept, ViewData, ViewStats
from seba.syllabus.graph import frontier


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

    view_concepts = []
    for c in concepts:
        cards = [i for i in state.items if i.concept == c.id]
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
            )
        )

    stats = ViewStats(
        concepts_done=sum(c.status == Status.DONE for c in concepts),
        concepts_total=len(concepts),
        cards_total=len(state.items),
        cards_due=sum(1 for i in state.items if is_due(i)),
        frontier=[c.id for c in frontier(state.syllabus)],
    )
    return ViewData(
        goal=state.name,
        subject=state.subject,
        session_number=state.session_number,
        generated=today,
        stats=stats,
        concepts=view_concepts,
        recent_grades=state.recent_grades,
    )


def render_view(data: ViewData) -> str:
    template = files("seba.ui").joinpath("view_template.html").read_text()
    return template.replace("__SEBA_DATA__", json.dumps(data.model_dump(mode="json")))
