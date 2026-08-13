from graphlib import CycleError, TopologicalSorter
from pathlib import Path

import yaml
from pydantic import ValidationError

from seba.models import Concept, Status, Syllabus


class SyllabusError(Exception):
    pass


def validate(s: Syllabus) -> None:
    ids = [c.id for c in s.concepts]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise SyllabusError(f"duplicate concept ids: {sorted(dupes)}")
    known = set(ids)
    for c in s.concepts:
        for field in ("prereqs", "soft_prereqs", "confusable_with"):
            unknown = [i for i in getattr(c, field) if i not in known]
            if unknown:
                raise SyllabusError(f"concept '{c.id}' has unknown {field}: {unknown}")
    # confusable_with is symmetric, not a dependency — deliberately not an edge here.
    ts = TopologicalSorter(
        {c.id: set(c.prereqs) | set(c.soft_prereqs) for c in s.concepts}
    )
    try:
        ts.prepare()
    except CycleError as e:
        raise SyllabusError(f"prereq cycle: {e.args[1]}") from e


def load_syllabus(path: Path) -> Syllabus:
    try:
        raw = yaml.safe_load(path.read_text())
        s = Syllabus.model_validate(raw)
        validate(s)
    except (yaml.YAMLError, ValidationError, SyllabusError) as e:
        raise SyllabusError(f"{path.name}: {e}") from e
    return s


def frontier(s: Syllabus) -> list[Concept]:
    done = {c.id for c in s.concepts if c.status == "done"}
    return [
        c
        for c in s.concepts
        if c.status != "done" and all(p in done for p in c.prereqs)
    ]


def confusables(s: Syllabus, concept_id: str) -> list[str]:
    """Concepts confusable with this one, in both declared directions."""
    out: set[str] = set()
    for c in s.concepts:
        if c.id == concept_id:
            out |= set(c.confusable_with)
        elif concept_id in c.confusable_with:
            out.add(c.id)
    out.discard(concept_id)
    return sorted(out)


_ORDER: list[Status] = [Status.UNSEEN, Status.IN_PROGRESS, Status.DONE]


def apply_status(s: Syllabus, concept_id: str, status: Status) -> Syllabus:
    concepts = []
    found = False
    for c in s.concepts:
        if c.id == concept_id:
            found = True
            if _ORDER.index(status) != _ORDER.index(c.status) + 1:
                raise SyllabusError(
                    f"illegal status move for '{concept_id}': {c.status} -> {status}"
                )
            c = c.model_copy(update={"status": status})
        concepts.append(c)
    if not found:
        raise SyllabusError(f"unknown concept: '{concept_id}'")
    return s.model_copy(update={"concepts": concepts})
