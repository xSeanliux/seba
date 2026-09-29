from graphlib import CycleError, TopologicalSorter
from pathlib import Path

import yaml
from pydantic import TypeAdapter, ValidationError

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


def load_concepts(path: Path) -> list[Concept]:
    """Concepts from a bare list, or from the `concepts:` of a mapping (a whole
    syllabus file works; its goal and subject are ignored)."""
    try:
        raw = yaml.safe_load(path.read_text())
        if isinstance(raw, dict):
            raw = raw.get("concepts")
        concepts = TypeAdapter(list[Concept]).validate_python(raw or [])
    except (OSError, UnicodeDecodeError, yaml.YAMLError, ValidationError) as e:
        raise SyllabusError(f"{path.name}: {e}") from e
    if not concepts:
        raise SyllabusError(
            f"{path.name}: holds no concepts — expected a list of concepts, "
            "or a mapping with a 'concepts:' list"
        )
    return concepts


def extend(
    s: Syllabus, new: list[Concept], *, against: Syllabus | None = None
) -> Syllabus:
    """The syllabus with `new` appended, validated whole. A new concept may not
    stand on a concept dropped in `against` (default `s`): the syllabus as a
    pending session has changed it, which is what `s` will become."""
    have = {c.id for c in s.concepts}
    taken = sorted({c.id for c in new if c.id in have})
    if taken:
        raise SyllabusError(f"concept ids already in the syllabus: {taken}")
    ids = [c.id for c in new]
    repeated = sorted({i for i in ids if ids.count(i) > 1})
    if repeated:
        raise SyllabusError(f"concept ids repeated in the file: {repeated}")
    for c in new:
        if c.status not in ("unseen", "done") or c.dropped_from is not None:
            raise SyllabusError(
                f"new concept '{c.id}' has status {c.status}; "
                "a new concept is unseen, or done if the learner already has it"
            )
    dropped = {
        c.id
        for c in (s if against is None else against).concepts
        if c.status == "dropped"
    }
    for c in new:
        gone = [p for p in c.prereqs if p in dropped]
        if gone:
            raise SyllabusError(
                f"new concept '{c.id}' depends on {', '.join(gone)}, which is "
                "dropped — restore that first"
            )
    merged = s.model_copy(update={"concepts": [*s.concepts, *new]})
    validate(merged)
    return merged


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


def _find(s: Syllabus, concept_id: str) -> Concept:
    for c in s.concepts:
        if c.id == concept_id:
            return c
    raise SyllabusError(f"unknown concept: '{concept_id}'")


def _replace(s: Syllabus, new: Concept) -> Syllabus:
    return s.model_copy(
        update={"concepts": [new if c.id == new.id else c for c in s.concepts]}
    )


def drop(s: Syllabus, concept_id: str) -> Syllabus:
    """Set a concept aside, remembering the status it had. Only hard prereq
    edges block: they are the curriculum, and a live concept cannot stand on
    one that is gone."""
    c = _find(s, concept_id)
    if c.status == "dropped":
        raise SyllabusError(f"'{concept_id}' is already dropped")
    live = [
        d.id for d in s.concepts if concept_id in d.prereqs and d.status != "dropped"
    ]
    if live:
        raise SyllabusError(
            f"cannot drop '{concept_id}': {', '.join(live)} depend on it — drop "
            "them first, or remove the edge in syllabus.yaml"
        )
    return _replace(
        s, c.model_copy(update={"status": Status.DROPPED, "dropped_from": c.status})
    )


def restore(s: Syllabus, concept_id: str) -> Syllabus:
    c = _find(s, concept_id)
    if c.status != "dropped":
        raise SyllabusError(
            f"'{concept_id}' is {c.status}; only a dropped concept can be restored"
        )
    gone = [p for p in c.prereqs if _find(s, p).status == "dropped"]
    if gone:
        raise SyllabusError(
            f"cannot restore '{concept_id}': it depends on {', '.join(gone)}, "
            "which is dropped — restore that first"
        )
    return _replace(
        s,
        c.model_copy(
            update={"status": c.dropped_from or Status.UNSEEN, "dropped_from": None}
        ),
    )
