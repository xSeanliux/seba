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
    # A dropped concept is not done, so what needs it waits too.
    return [
        c
        for c in s.concepts
        if c.status not in ("done", "dropped") and all(p in done for p in c.prereqs)
    ]


def check_teachable(s: Syllabus, concept_id: str) -> Concept:
    """The concept, if it is in progress or on the frontier; else why not."""
    by_id = {c.id: c for c in s.concepts}
    c = by_id.get(concept_id)
    if c is None:
        raise SyllabusError(f"unknown concept: '{concept_id}'")
    if c.status == "dropped":
        raise SyllabusError(f"'{concept_id}' is dropped; restore it first")
    if c.status == "done":
        raise SyllabusError(
            f"'{concept_id}' is done; reopen it if the learner wants it taught again"
        )
    if c.status == "in-progress":
        return c
    # Hard edges are the curriculum: name every one that stands in the way.
    unmet = [p for p in c.prereqs if by_id[p].status != "done"]
    if unmet:
        raise SyllabusError(
            f"'{concept_id}' is not ready: {', '.join(unmet)} must be done first"
        )
    return c


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


def apply_status(
    s: Syllabus, concept_id: str, status: Status, *, reopen: bool = False
) -> Syllabus:
    concepts = []
    found = False
    for c in s.concepts:
        if c.id == concept_id:
            found = True
            if c.status == "dropped":
                raise SyllabusError(f"'{concept_id}' is dropped; restore it first")
            # Forward one step, or a reopen. Nothing reopens by itself: the
            # tutor proposes it and the learner agrees (docs/adr/0001), so
            # done -> in-progress needs `reopen`, and `reopen` allows only that.
            if reopen:
                legal = (c.status, status) == (Status.DONE, Status.IN_PROGRESS)
            else:
                legal = _ORDER.index(status) == _ORDER.index(c.status) + 1
            if not legal:
                raise SyllabusError(
                    f"illegal status move for '{concept_id}': {c.status} -> {status}"
                )
            c = c.model_copy(update={"status": status})
        concepts.append(c)
    if not found:
        raise SyllabusError(f"unknown concept: '{concept_id}'")
    return s.model_copy(update={"concepts": concepts})
