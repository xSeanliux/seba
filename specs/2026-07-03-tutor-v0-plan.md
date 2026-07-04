# Seba v0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Name:** *seba*, Egyptian *sbꜣ* "to teach" (also "star" 𓇼 and "door"); root of *sbꜣyt*, the instruction-literature genre. Package, CLI, and repo are all `seba`. The README (Task 14) must carry a one-line etymology note.

**Repository:** implement everything in https://github.com/xSeanliux/seba — Task 1 clones it to `~/Desktop/Projects/seba` (do NOT `git init` a fresh repo); all work is committed there. Do not push unless the user asks.

**Goal:** Build the v0 milestone of Seba — a terminal LLM tutor with a scheduler-owned agenda, in-session outcome tools, FSRS review scheduling, and plain-text git-backed learner state — per the spec, committed in the repo at `specs/` (Task 1 puts it there).

**Architecture:** Code owns state, scheduling, and validation; the LLM owns dialogue and grading, recorded through four validated outcome tools (`grade_review`, `mint_item`, `update_concept`, `end_session`) with a deterministic session-end gate. Two artifacts cross the seam: Agenda (code → LLM) and SessionRecord (accumulated tool calls, LLM → code). All learner state is plain text in a git-committed data directory.

**Tech Stack:** Python ≥3.12, uv, pydantic v2, py-fsrs (`fsrs`), anthropic SDK, typer, rich, pyyaml, pytest.

## Global Constraints

- Repo: clone of https://github.com/xSeanliux/seba at `~/Desktop/Projects/seba`. All paths below relative to it. Commit locally; do not push unless the user asks.
- Python ≥3.12; deps EXACTLY: `anthropic`, `fsrs`, `pydantic>=2`, `rich`, `pyyaml`, `typer`; dev: `pytest`. No others without cause.
- All schemas live in `src/seba/models.py`. No module defines its own dict shapes.
- Imports strictly downward: `ui → session → scheduler → store`; `syllabus` and `synthesis` are siblings used by `cli`. No circular imports.
- Prompts are markdown files with `{placeholder}` `.format()` substitution, never Python string literals.
- Models: dialogue `claude-sonnet-5` (env `SEBA_MODEL`), recovery/synthesis `claude-haiku-4-5` (env `SEBA_RECOVERY_MODEL`).
- Data dir: env `SEBA_DATA_DIR`, default `~/seba-data`. It is its own git repo; one commit per saved session.
- Grades: `again | hard | good | easy | skipped`. `skipped` never touches FSRS state.
- Concept statuses: `unseen | in-progress | done`; legal moves only forward one step at a time (`unseen→in-progress→done`).
- `mint_item` cap: 10 per session. Briefing budget ~4,000 chars (~1k tokens). Source-excerpt budget ~16,000 chars (~4k tokens).
- Loud failures: malformed state files raise errors naming file (and line where possible); never silently default.
- Commit after every green test cycle. Conventional-commit style subjects.

## Orchestrator briefing (read this first if you are the PM agent)

**Task dependency DAG** (arrows = "needs merged first"):

```
T1 scaffold
 └─ T2 models.py            ← single owned artifact; nothing parallel until merged
     ├─ T3 syllabus ─── T4 store ──┐
     ├─ T5 fsrs items ─────────────┼─ T6 agenda ── T7 tools ─┬─ T9 dialogue ── T10 recovery
     ├─ T8 prompts/profiles ───────┘   (T6 imports store.parse_notes;         │
     │                                  T7 imports agenda.resolve_excerpt)     │
     ├─ T11 apply (needs T3+T5) ──────────────────────────────────────────────┼─ T13 CLI
     └─ T12 synthesis (needs T3) ─────────────────────────────────────────────┘
T14 dogfood — HUMAN-GATED, do not attempt; hand off to the user.
```

Safe parallel waves after T2: **wave 1** = T3, T5, T8, T12 · **wave 2** = T4, T11 · **wave 3** = T6 · **wave 4** = T7 · **wave 5** = T9 · **wave 6** = T10 · **wave 7** = T13, T13b. (T9 also needs T8's loader; T13b needs T4, T6, T9, T11 but not T13.)

**Known v0 spec deviation (accepted):** spec §M5 has `new-goal` auto-drafting a missing subject profile from templates; v0 instead errors with copy-the-template instructions (both launch subjects ship bundled). Auto-drafting lands with agentic synthesis in v1. Do not "fix" this during execution.

**Working model:** one repo, sequential merges. If you parallelize a wave with worktrees, tasks touch disjoint files by design — merge in task-number order and run the full `uv run pytest` after each merge; a red suite blocks the next wave.

**Worker prompt recipe:** give each worker its full task section + the Global Constraints block + nothing else. Interfaces blocks define what neighbors expect — workers must not rename anything listed there.

**Allowed deviation:** only where a task explicitly grants it (T5's py-fsrs dict-shape note; T12's test-merge note). Anything else that seems wrong → stop, report to PM, PM decides; never silently redesign.

**Failure protocol:** a worker whose Step "expect PASS" fails after 2 fix attempts stops and reports the failing output verbatim. PM reviews before re-dispatch.

---

### Task 1: Project scaffold

**Files:**
- Create: `pyproject.toml`, `src/seba/__init__.py`, `src/seba/config.py`, `tests/test_config.py`, `.gitignore`
- Already in repo: `specs/` (design spec, implementation plan, review page — committed before execution; treat `specs/2026-07-03-tutor-design.md` as the spec of record)

**Interfaces:**
- Produces: `config.data_dir() -> Path`, `config.MODEL: str`, `config.RECOVERY_MODEL: str`, `config.subjects_dirs() -> list[Path]` (bundled `subjects/` first, then `<data>/subjects/`).

- [ ] **Step 1: Clone repo and set up env**

```bash
cd ~/Desktop/Projects
git clone https://github.com/xSeanliux/seba && cd seba
uv init --package --name seba --python 3.12
uv add anthropic fsrs "pydantic>=2" rich pyyaml typer
uv add --dev pytest
mkdir -p src/seba tests subjects
```

(If `~/Desktop/Projects/seba` already exists as the clone, just `cd` in and continue.)

`.gitignore`:
```
.venv/
__pycache__/
*.egg-info/
```

- [ ] **Step 2: Write the failing test**

`tests/test_config.py`:
```python
from pathlib import Path
from seba import config


def test_data_dir_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBA_DATA_DIR", str(tmp_path / "d"))
    assert config.data_dir() == tmp_path / "d"


def test_data_dir_default(monkeypatch):
    monkeypatch.delenv("SEBA_DATA_DIR", raising=False)
    assert config.data_dir() == Path.home() / "seba-data"


def test_models_defaults(monkeypatch):
    monkeypatch.delenv("SEBA_MODEL", raising=False)
    assert config.model() == "claude-sonnet-5"
    monkeypatch.setenv("SEBA_RECOVERY_MODEL", "claude-x")
    assert config.recovery_model() == "claude-x"


def test_subjects_dirs(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBA_DATA_DIR", str(tmp_path))
    dirs = config.subjects_dirs()
    assert dirs[0].name == "subjects" and dirs[1] == tmp_path / "subjects"
```

- [ ] **Step 3: Run test to verify it fails**

Run: `uv run pytest tests/test_config.py -v` — Expected: FAIL (no module `tutor.config`).

- [ ] **Step 4: Implement**

`src/seba/config.py`:
```python
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def data_dir() -> Path:
    return Path(os.environ.get("SEBA_DATA_DIR", Path.home() / "seba-data"))


def model() -> str:
    return os.environ.get("SEBA_MODEL", "claude-sonnet-5")


def recovery_model() -> str:
    return os.environ.get("SEBA_RECOVERY_MODEL", "claude-haiku-4-5")


def subjects_dirs() -> list[Path]:
    return [REPO_ROOT / "subjects", data_dir() / "subjects"]
```

- [ ] **Step 5: Run tests, expect PASS, commit**

```bash
uv run pytest -v
git add -A && git commit -m "feat: scaffold tutor project with config"
```

---

### Task 2: models.py — all schemas

**Files:**
- Create: `src/seba/models.py`
- Test: `tests/test_models.py`

**Interfaces:**
- Produces (used by every later task):
  - `ItemType = Literal["recall","apply","cloze","produce","recognize"]`
  - `Grade = Literal["again","hard","good","easy","skipped"]`
  - `Status = Literal["unseen","in-progress","done"]`
  - `Concept(id, name, prereqs: list[str]=[], sources: list[str]=[], status: Status="unseen", est_sessions: int=1)`
  - `Syllabus(goal: str, subject: str, concepts: list[Concept])`
  - `Item(id, concept, type: ItemType, front, back, fsrs: dict, created: date, suspended: bool=False)`
  - `ReviewItem(id, type: ItemType, front, back)`
  - `TeachConcept(id, name, source_excerpts: list[str], guidance: str)`
  - `Agenda(goal, subject, session_number: int, briefing: str, review_items: list[ReviewItem], teach_concept: TeachConcept | None, practice_quota: int, pace_hint: Literal["push-harder","steady","step-back"])`
  - Tool arg models: `GradeReview(id, grade: Grade, note: str | None = None)`, `MintItem(concept, type: ItemType, front, back)`, `UpdateConcept(id, status_change: Literal["started","completed"] | None = None, note: str | None = None)`, `EndSession(summary: str, next_session_hint: str)`
  - `SessionRecord(reviews: list[GradeReview]=[], concepts: list[UpdateConcept]=[], new_items: list[MintItem]=[], summary: str | None=None, next_session_hint: str | None=None, complete: bool=False)`
  - `SubjectProfile(name, kind: str, max_reviews_per_session: int, item_types: list[ItemType], session_shape: str)`
  - `GoalState(name, subject, syllabus: Syllabus, items: list[Item], notes: str="", last_hint: str | None=None, session_number: int, recent_grades: list[Grade]=[])`
  - `GoalSummary(name, subject, session_count: int, due_count: int)`

- [ ] **Step 1: Write the failing test**

`tests/test_models.py`:
```python
from datetime import date
import pytest
from pydantic import ValidationError
from seba.models import (
    Agenda, Concept, EndSession, GoalState, GradeReview, Item, MintItem,
    ReviewItem, SessionRecord, SubjectProfile, Syllabus, UpdateConcept,
)


def test_concept_defaults():
    c = Concept(id="bayes", name="Bayes")
    assert c.status == "unseen" and c.prereqs == [] and c.est_sessions == 1


def test_grade_review_rejects_bad_grade():
    with pytest.raises(ValidationError):
        GradeReview(id="it-1", grade="great")


def test_grade_review_accepts_skipped():
    assert GradeReview(id="it-1", grade="skipped").note is None


def test_session_record_defaults_incomplete():
    r = SessionRecord()
    assert r.complete is False and r.reviews == []


def test_item_roundtrip():
    i = Item(id="it-1", concept="bayes", type="recall", front="f", back="b",
             fsrs={"due": "2026-07-03"}, created=date(2026, 7, 3))
    assert Item.model_validate(i.model_dump()) == i


def test_agenda_allows_no_teach_concept():
    a = Agenda(goal="g", subject="s", session_number=1, briefing="",
               review_items=[ReviewItem(id="it-1", type="recall", front="f", back="b")],
               teach_concept=None, practice_quota=3, pace_hint="steady")
    assert a.teach_concept is None


def test_syllabus_and_goal_state():
    s = Syllabus(goal="g", subject="probability", concepts=[Concept(id="a", name="A")])
    gs = GoalState(name="g", subject="probability", syllabus=s, items=[], session_number=1)
    assert gs.notes == "" and gs.recent_grades == []


def test_subject_profile():
    p = SubjectProfile(name="italian", kind="language", max_reviews_per_session=20,
                       item_types=["produce", "cloze"], session_shape="review-heavy")
    assert p.max_reviews_per_session == 20
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_models.py -v` — Expected: FAIL (no `tutor.models`).

- [ ] **Step 3: Implement**

`src/seba/models.py`:
```python
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

ItemType = Literal["recall", "apply", "cloze", "produce", "recognize"]
Grade = Literal["again", "hard", "good", "easy", "skipped"]
Status = Literal["unseen", "in-progress", "done"]
PaceHint = Literal["push-harder", "steady", "step-back"]


class Concept(BaseModel):
    id: str
    name: str
    prereqs: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    status: Status = "unseen"
    est_sessions: int = 1


class Syllabus(BaseModel):
    goal: str
    subject: str
    concepts: list[Concept]


class Item(BaseModel):
    id: str
    concept: str
    type: ItemType
    front: str
    back: str
    fsrs: dict  # owned by py-fsrs (Card.to_dict()); others read only "due"
    created: date
    suspended: bool = False


class ReviewItem(BaseModel):
    id: str
    type: ItemType
    front: str
    back: str


class TeachConcept(BaseModel):
    id: str
    name: str
    source_excerpts: list[str] = Field(default_factory=list)
    guidance: str = ""


class Agenda(BaseModel):
    goal: str
    subject: str
    session_number: int
    briefing: str
    review_items: list[ReviewItem]
    teach_concept: TeachConcept | None
    practice_quota: int
    pace_hint: PaceHint


class GradeReview(BaseModel):
    """Grade a review item right after its exchange resolves.

    Rubric: wrong or no recall -> again; correct with significant
    hesitation or hints -> hard; correct -> good; instant and
    confident -> easy; never reached this session -> skipped."""
    id: str
    grade: Grade
    note: str | None = None


class MintItem(BaseModel):
    """Create a spaced-repetition card. Only for facts/skills worth
    retaining a month from now — not session-local scaffolding."""
    concept: str
    type: ItemType
    front: str
    back: str


class UpdateConcept(BaseModel):
    """Record concept progress or a note (misconception, strength)."""
    id: str
    status_change: Literal["started", "completed"] | None = None
    note: str | None = None


class EndSession(BaseModel):
    """Close the session. Call exactly once, after recapping aloud."""
    summary: str
    next_session_hint: str


class SessionRecord(BaseModel):
    reviews: list[GradeReview] = Field(default_factory=list)
    concepts: list[UpdateConcept] = Field(default_factory=list)
    new_items: list[MintItem] = Field(default_factory=list)
    summary: str | None = None
    next_session_hint: str | None = None
    complete: bool = False


class SubjectProfile(BaseModel):
    name: str
    kind: str
    max_reviews_per_session: int
    item_types: list[ItemType]
    session_shape: str


class GoalState(BaseModel):
    name: str
    subject: str
    syllabus: Syllabus
    items: list[Item]
    notes: str = ""
    last_hint: str | None = None
    session_number: int
    recent_grades: list[Grade] = Field(default_factory=list)


class GoalSummary(BaseModel):
    name: str
    subject: str
    session_count: int
    due_count: int
```

- [ ] **Step 4: Run tests, expect PASS, commit**

```bash
uv run pytest tests/test_models.py -v
git add -A && git commit -m "feat: add all pydantic schemas in models.py"
```

---

### Task 3: syllabus module — DAG validation, frontier, status

**Files:**
- Create: `src/seba/syllabus/__init__.py`, `src/seba/syllabus/graph.py`
- Test: `tests/test_syllabus.py`

**Interfaces:**
- Consumes: `models.Syllabus`, `models.Concept`, `models.Status`.
- Produces:
  - `load_syllabus(path: Path) -> Syllabus` — parses YAML, validates: unique kebab-case ids, prereqs reference existing ids, DAG (cycle → `SyllabusError` naming the cycle).
  - `validate(s: Syllabus) -> None` — same checks on an in-memory syllabus.
  - `frontier(s: Syllabus) -> list[Concept]` — not-done concepts whose prereqs are all done, declaration order.
  - `apply_status(s: Syllabus, concept_id: str, status: Status) -> Syllabus` — returns new Syllabus; illegal jump (e.g. unseen→done) or unknown id → `SyllabusError`.
  - `class SyllabusError(Exception)`.

- [ ] **Step 1: Write the failing test**

`tests/test_syllabus.py`:
```python
from pathlib import Path
import pytest
from seba.models import Concept, Syllabus
from seba.syllabus.graph import SyllabusError, apply_status, frontier, load_syllabus, validate


def make(concepts):
    return Syllabus(goal="g", subject="probability", concepts=concepts)


def test_cycle_detected_and_named():
    s = make([Concept(id="a", name="A", prereqs=["b"]),
              Concept(id="b", name="B", prereqs=["a"])])
    with pytest.raises(SyllabusError, match="a"):
        validate(s)


def test_unknown_prereq_rejected():
    s = make([Concept(id="a", name="A", prereqs=["ghost"])])
    with pytest.raises(SyllabusError, match="ghost"):
        validate(s)


def test_duplicate_id_rejected():
    s = make([Concept(id="a", name="A"), Concept(id="a", name="A2")])
    with pytest.raises(SyllabusError, match="a"):
        validate(s)


def test_frontier_diamond():
    # a -> b, a -> c, {b,c} -> d ; a done => frontier is [b, c]
    s = make([Concept(id="a", name="A", status="done"),
              Concept(id="b", name="B", prereqs=["a"]),
              Concept(id="c", name="C", prereqs=["a"]),
              Concept(id="d", name="D", prereqs=["b", "c"])])
    assert [c.id for c in frontier(s)] == ["b", "c"]


def test_frontier_nothing_done():
    s = make([Concept(id="a", name="A"), Concept(id="b", name="B", prereqs=["a"])])
    assert [c.id for c in frontier(s)] == ["a"]


def test_apply_status_legal_and_illegal():
    s = make([Concept(id="a", name="A")])
    s2 = apply_status(s, "a", "in-progress")
    assert s2.concepts[0].status == "in-progress"
    with pytest.raises(SyllabusError):
        apply_status(s, "a", "done")  # unseen -> done is an illegal jump
    with pytest.raises(SyllabusError, match="nope"):
        apply_status(s, "nope", "done")


def test_load_syllabus_yaml(tmp_path: Path):
    p = tmp_path / "syllabus.yaml"
    p.write_text(
        "goal: g\nsubject: probability\nconcepts:\n"
        "  - id: a\n    name: A\n"
        "  - id: b\n    name: B\n    prereqs: [a]\n"
    )
    s = load_syllabus(p)
    assert [c.id for c in s.concepts] == ["a", "b"]


def test_load_syllabus_bad_file_names_path(tmp_path: Path):
    p = tmp_path / "syllabus.yaml"
    p.write_text("goal: g\nsubject: s\nconcepts: [{id: a, name: A, prereqs: [a]}]")
    with pytest.raises(SyllabusError, match="syllabus.yaml"):
        load_syllabus(p)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_syllabus.py -v` — Expected: FAIL (no module).

- [ ] **Step 3: Implement**

`src/seba/syllabus/__init__.py`:
```python
from seba.syllabus.graph import SyllabusError, apply_status, frontier, load_syllabus, validate

__all__ = ["SyllabusError", "apply_status", "frontier", "load_syllabus", "validate"]
```

`src/seba/syllabus/graph.py`:
```python
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
        unknown = [p for p in c.prereqs if p not in known]
        if unknown:
            raise SyllabusError(f"concept '{c.id}' has unknown prereqs: {unknown}")
    ts = TopologicalSorter({c.id: set(c.prereqs) for c in s.concepts})
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
    return [c for c in s.concepts
            if c.status != "done" and all(p in done for p in c.prereqs)]


_ORDER: list[Status] = ["unseen", "in-progress", "done"]


def apply_status(s: Syllabus, concept_id: str, status: Status) -> Syllabus:
    concepts = []
    found = False
    for c in s.concepts:
        if c.id == concept_id:
            found = True
            if _ORDER.index(status) != _ORDER.index(c.status) + 1:
                raise SyllabusError(
                    f"illegal status move for '{concept_id}': {c.status} -> {status}")
            c = c.model_copy(update={"status": status})
        concepts.append(c)
    if not found:
        raise SyllabusError(f"unknown concept: '{concept_id}'")
    return s.model_copy(update={"concepts": concepts})
```

- [ ] **Step 4: Run tests, expect PASS, commit**

```bash
uv run pytest tests/test_syllabus.py -v
git add -A && git commit -m "feat: syllabus graph with DAG validation, frontier, status moves"
```

---

### Task 4: store — persistence + git

**Files:**
- Create: `src/seba/store/__init__.py`, `src/seba/store/store.py`
- Test: `tests/test_store.py`

**Interfaces:**
- Consumes: `models.*`, `syllabus.load_syllabus`.
- Produces:
  - `class Store: __init__(self, data_dir: Path)` — creates dir + git repo if missing.
  - `Store.list_goals() -> list[GoalSummary]` (`due_count` = items with `fsrs["due"] <= today` ISO-date prefix comparison, not suspended).
  - `Store.load_goal(name: str) -> GoalState` — `StoreError` naming the file on any malformed input; `session_number` = count of `sessions/*.outcomes.yaml` + 1; `last_hint` from newest outcomes file's `next_session_hint`; `recent_grades` = review grades from up to 3 newest outcomes files.
  - `Store.save_session(name: str, record: SessionRecord, transcript: str, updated: GoalState) -> None` — writes `sessions/NNN.md` (summary body; `INCOMPLETE` marker line if `not record.complete`), `NNN.outcomes.yaml`, `NNN.transcript.md`; rewrites `items.jsonl` and `syllabus.yaml` from `updated`; appends concept notes to `notes.md` under `## <concept-id>` headings (newest first within a section); one git commit `"{name}: session {NNN}"`.
  - `Store.create_goal(name: str, syllabus: Syllabus, subject: str) -> None` — `StoreError` if goal exists.
  - `parse_notes(text: str) -> dict[str, list[str]]` — maps concept-id → list of note lines from `## <id>` sections.
  - `class StoreError(Exception)`.

- [ ] **Step 1: Write the failing test**

`tests/test_store.py`:
```python
import subprocess
from datetime import date
from pathlib import Path

import pytest
from seba.models import (Concept, GoalState, GradeReview, Item, MintItem,
                          SessionRecord, Syllabus, UpdateConcept)
from seba.store.store import Store, StoreError, parse_notes


def syl():
    return Syllabus(goal="prob", subject="probability",
                    concepts=[Concept(id="bayes", name="Bayes")])


def item(due="2026-07-01"):
    return Item(id="it-1", concept="bayes", type="recall", front="f", back="b",
                fsrs={"due": due}, created=date(2026, 6, 28))


@pytest.fixture
def store(tmp_path):
    return Store(tmp_path / "data")


def test_create_and_load_roundtrip(store):
    store.create_goal("prob", syl(), "probability")
    gs = store.load_goal("prob")
    assert gs.subject == "probability" and gs.session_number == 1
    assert gs.items == [] and gs.last_hint is None


def test_create_duplicate_rejected(store):
    store.create_goal("prob", syl(), "probability")
    with pytest.raises(StoreError):
        store.create_goal("prob", syl(), "probability")


def test_save_session_roundtrip_and_git(store):
    store.create_goal("prob", syl(), "probability")
    gs = store.load_goal("prob")
    record = SessionRecord(
        reviews=[GradeReview(id="it-1", grade="good")],
        concepts=[UpdateConcept(id="bayes", status_change="started", note="shaky on priors")],
        new_items=[MintItem(concept="bayes", type="recall", front="f", back="b")],
        summary="Taught Bayes.", next_session_hint="drill priors", complete=True)
    updated = gs.model_copy(update={
        "items": [item()],
        "syllabus": gs.syllabus.model_copy(update={
            "concepts": [gs.syllabus.concepts[0].model_copy(update={"status": "in-progress"})]})})
    store.save_session("prob", record, "transcript text", updated)

    gs2 = store.load_goal("prob")
    assert gs2.session_number == 2
    assert gs2.last_hint == "drill priors"
    assert gs2.recent_grades == ["good"]
    assert gs2.items[0].id == "it-1"
    assert gs2.syllabus.concepts[0].status == "in-progress"
    assert "shaky on priors" in gs2.notes

    gdir = store.data_dir / "goals" / "prob" / "sessions"
    assert (gdir / "001.md").exists()
    assert (gdir / "001.outcomes.yaml").exists()
    assert (gdir / "001.transcript.md").exists()
    log = subprocess.run(["git", "log", "--oneline"], cwd=store.data_dir,
                         capture_output=True, text=True).stdout
    assert "prob: session 001" in log


def test_incomplete_marker(store):
    store.create_goal("prob", syl(), "probability")
    gs = store.load_goal("prob")
    store.save_session("prob", SessionRecord(complete=False), "t", gs)
    body = (store.data_dir / "goals" / "prob" / "sessions" / "001.md").read_text()
    assert "INCOMPLETE" in body


def test_list_goals_due_count(store):
    store.create_goal("prob", syl(), "probability")
    gs = store.load_goal("prob")
    updated = gs.model_copy(update={"items": [item(due="2020-01-01")]})
    store.save_session("prob", SessionRecord(complete=True, summary="s",
                                             next_session_hint="h"), "t", updated)
    [summary] = store.list_goals()
    assert summary.due_count == 1 and summary.session_count == 1


def test_malformed_items_named(store):
    store.create_goal("prob", syl(), "probability")
    (store.data_dir / "goals" / "prob" / "items.jsonl").write_text("not json\n")
    with pytest.raises(StoreError, match="items.jsonl"):
        store.load_goal("prob")


def test_parse_notes():
    text = "## bayes\n- shaky on priors\n\n## sigma\n- fine\n"
    assert parse_notes(text) == {"bayes": ["- shaky on priors"], "sigma": ["- fine"]}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_store.py -v` — Expected: FAIL.

- [ ] **Step 3: Implement**

`src/seba/store/__init__.py`:
```python
from seba.store.store import Store, StoreError, parse_notes

__all__ = ["Store", "StoreError", "parse_notes"]
```

`src/seba/store/store.py`:
```python
import json
import subprocess
from datetime import date
from pathlib import Path

import yaml
from pydantic import ValidationError

from seba.models import GoalState, GoalSummary, Item, SessionRecord, Syllabus
from seba.syllabus.graph import SyllabusError, load_syllabus


class StoreError(Exception):
    pass


def parse_notes(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
        elif current is not None and line.strip():
            sections[current].append(line)
    return sections


class Store:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        (data_dir / "goals").mkdir(parents=True, exist_ok=True)
        (data_dir / "sources").mkdir(exist_ok=True)
        if not (data_dir / ".git").exists():
            self._git("init")

    def _git(self, *args: str) -> None:
        subprocess.run(["git", *args], cwd=self.data_dir, check=True,
                       capture_output=True)

    def _goal_dir(self, name: str) -> Path:
        return self.data_dir / "goals" / name

    def create_goal(self, name: str, syllabus: Syllabus, subject: str) -> None:
        gdir = self._goal_dir(name)
        if gdir.exists():
            raise StoreError(f"goal '{name}' already exists")
        (gdir / "sessions").mkdir(parents=True)
        (gdir / "goal.yaml").write_text(yaml.safe_dump({"name": name, "subject": subject}))
        (gdir / "syllabus.yaml").write_text(
            yaml.safe_dump(syllabus.model_dump(), sort_keys=False))
        (gdir / "items.jsonl").write_text("")
        (gdir / "notes.md").write_text("")
        self._git("add", "-A")
        self._git("commit", "-m", f"{name}: created")

    def _load_items(self, path: Path) -> list[Item]:
        items = []
        for n, line in enumerate(path.read_text().splitlines(), 1):
            if not line.strip():
                continue
            try:
                items.append(Item.model_validate(json.loads(line)))
            except (json.JSONDecodeError, ValidationError) as e:
                raise StoreError(f"{path.name}:{n}: {e}") from e
        return items

    def _outcomes_files(self, name: str) -> list[Path]:
        return sorted(self._goal_dir(name).glob("sessions/*.outcomes.yaml"))

    def load_goal(self, name: str) -> GoalState:
        gdir = self._goal_dir(name)
        if not gdir.exists():
            raise StoreError(f"no such goal: '{name}'")
        try:
            meta = yaml.safe_load((gdir / "goal.yaml").read_text())
            syllabus = load_syllabus(gdir / "syllabus.yaml")
        except (yaml.YAMLError, SyllabusError) as e:
            raise StoreError(str(e)) from e
        items = self._load_items(gdir / "items.jsonl")
        outcomes = self._outcomes_files(name)
        last_hint, recent_grades = None, []
        for path in outcomes[-3:]:
            rec = SessionRecord.model_validate(yaml.safe_load(path.read_text()))
            recent_grades.extend(r.grade for r in rec.reviews)
            last_hint = rec.next_session_hint or last_hint
        return GoalState(
            name=name, subject=meta["subject"], syllabus=syllabus, items=items,
            notes=(gdir / "notes.md").read_text(), last_hint=last_hint,
            session_number=len(outcomes) + 1, recent_grades=recent_grades)

    def save_session(self, name: str, record: SessionRecord,
                     transcript: str, updated: GoalState) -> None:
        gdir = self._goal_dir(name)
        n = f"{len(self._outcomes_files(name)) + 1:03d}"
        sdir = gdir / "sessions"
        marker = "" if record.complete else "**INCOMPLETE**\n\n"
        (sdir / f"{n}.md").write_text(
            f"# Session {n}\n\n{marker}{record.summary or '(no summary)'}\n")
        (sdir / f"{n}.outcomes.yaml").write_text(
            yaml.safe_dump(record.model_dump(), sort_keys=False))
        (sdir / f"{n}.transcript.md").write_text(transcript)

        tmp = gdir / "items.jsonl.tmp"
        tmp.write_text("".join(
            json.dumps(i.model_dump(mode="json")) + "\n" for i in updated.items))
        tmp.rename(gdir / "items.jsonl")
        (gdir / "syllabus.yaml").write_text(
            yaml.safe_dump(updated.syllabus.model_dump(), sort_keys=False))

        noted = [c for c in record.concepts if c.note]
        if noted:
            sections = parse_notes((gdir / "notes.md").read_text())
            for c in noted:
                sections.setdefault(c.id, []).insert(0, f"- [s{n}] {c.note}")
            (gdir / "notes.md").write_text("".join(
                f"## {cid}\n" + "\n".join(lines) + "\n\n"
                for cid, lines in sections.items()))

        self._git("add", "-A")
        self._git("commit", "-m", f"{name}: session {n}")

    def list_goals(self) -> list[GoalSummary]:
        out = []
        today = date.today().isoformat()
        for gdir in sorted((self.data_dir / "goals").iterdir()):
            if not gdir.is_dir():
                continue
            gs = self.load_goal(gdir.name)
            due = sum(1 for i in gs.items
                      if not i.suspended and str(i.fsrs.get("due", ""))[:10] <= today)
            out.append(GoalSummary(name=gs.name, subject=gs.subject,
                                   session_count=gs.session_number - 1, due_count=due))
        return out
```

- [ ] **Step 4: Run tests, expect PASS, commit**

```bash
uv run pytest tests/test_store.py -v
git add -A && git commit -m "feat: store with git-committed plain-text state"
```

---

### Task 5: scheduler/items.py — FSRS wrapper

**Files:**
- Create: `src/seba/scheduler/__init__.py`, `src/seba/scheduler/items.py`
- Test: `tests/test_scheduler_items.py`

**Interfaces:**
- Consumes: `models.Item`, `models.MintItem`, `models.Grade`; `fsrs` package (`Scheduler`, `Card`, `Rating`).
- Produces:
  - `due_items(items: list[Item], today: date, limit: int) -> list[Item]` — unsuspended, `due <= today`, most-overdue first, capped.
  - `apply_review(item: Item, grade: Grade, now: datetime) -> Item` — new Item with updated `fsrs`; `grade == "skipped"` returns item unchanged.
  - `mint_item(new: MintItem, today: date) -> Item` — id `"it-" + uuid4().hex[:8]`, fresh FSRS card.
- Note for implementer: py-fsrs API — `Card()` new card; `Card.to_dict()` / `Card.from_dict(d)`; `Scheduler().review_card(card, Rating.Good, review_datetime=now)` returns `(card, review_log)`. `Rating.Again/Hard/Good/Easy`. The card dict's `due` field is an ISO datetime string.

- [ ] **Step 1: Write the failing test**

`tests/test_scheduler_items.py`:
```python
from datetime import date, datetime, timedelta, timezone

from seba.models import Item, MintItem
from seba.scheduler.items import apply_review, due_items, mint_item


def make_item(id="it-1", due="2026-07-01T00:00:00+00:00", suspended=False):
    return Item(id=id, concept="c", type="recall", front="f", back="b",
                fsrs={"due": due}, created=date(2026, 6, 1), suspended=suspended)


def test_due_items_filters_sorts_caps():
    items = [make_item("a", "2026-07-02T00:00:00+00:00"),
             make_item("b", "2026-06-01T00:00:00+00:00"),
             make_item("c", "2026-08-01T00:00:00+00:00"),
             make_item("d", "2026-06-15T00:00:00+00:00", suspended=True)]
    got = due_items(items, date(2026, 7, 3), limit=2)
    assert [i.id for i in got] == ["b", "a"]  # most overdue first, c future, d suspended


def test_mint_and_review_cycle():
    now = datetime(2026, 7, 3, tzinfo=timezone.utc)
    item = mint_item(MintItem(concept="c", type="recall", front="f", back="b"),
                     date(2026, 7, 3))
    assert item.id.startswith("it-") and "due" in item.fsrs
    graded = apply_review(item, "good", now)
    assert graded.fsrs != item.fsrs


def test_skipped_leaves_fsrs_untouched():
    item = make_item()
    assert apply_review(item, "skipped", datetime.now(timezone.utc)) == item


def test_again_due_within_a_day():
    now = datetime(2026, 7, 3, tzinfo=timezone.utc)
    item = mint_item(MintItem(concept="c", type="recall", front="f", back="b"),
                     date(2026, 7, 3))
    graded = apply_review(item, "again", now)
    due = datetime.fromisoformat(graded.fsrs["due"])
    assert due <= now + timedelta(days=1)


def test_thirty_day_sim_intervals_grow():
    now = datetime(2026, 7, 3, tzinfo=timezone.utc)
    item = mint_item(MintItem(concept="c", type="recall", front="f", back="b"),
                     date(2026, 7, 3))
    intervals = []
    for _ in range(6):
        due = datetime.fromisoformat(item.fsrs["due"])
        now = max(now, due) + timedelta(hours=1)
        item = apply_review(item, "good", now)
        intervals.append((datetime.fromisoformat(item.fsrs["due"]) - now).days)
    assert intervals == sorted(intervals) and intervals[-1] > intervals[0]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_scheduler_items.py -v` — Expected: FAIL.

- [ ] **Step 3: Implement**

`src/seba/scheduler/__init__.py`: (empty file)

`src/seba/scheduler/items.py`:
```python
from datetime import date, datetime
from uuid import uuid4

from fsrs import Card, Rating, Scheduler

from seba.models import Grade, Item, MintItem

_RATING = {"again": Rating.Again, "hard": Rating.Hard,
           "good": Rating.Good, "easy": Rating.Easy}
_scheduler = Scheduler()


def due_items(items: list[Item], today: date, limit: int) -> list[Item]:
    cutoff = today.isoformat()
    due = [i for i in items
           if not i.suspended and str(i.fsrs.get("due", ""))[:10] <= cutoff]
    due.sort(key=lambda i: str(i.fsrs["due"]))
    return due[:limit]


def apply_review(item: Item, grade: Grade, now: datetime) -> Item:
    if grade == "skipped":
        return item
    card, _ = _scheduler.review_card(Card.from_dict(item.fsrs), _RATING[grade],
                                     review_datetime=now)
    return item.model_copy(update={"fsrs": card.to_dict()})


def mint_item(new: MintItem, today: date) -> Item:
    return Item(id=f"it-{uuid4().hex[:8]}", concept=new.concept, type=new.type,
                front=new.front, back=new.back, fsrs=Card().to_dict(), created=today)
```

If py-fsrs's actual `Card.to_dict()` keys differ (e.g. `due` nested), adapt the two access points (`due_items` cutoff read and tests) to the real shape — run `uv run python -c "from fsrs import Card; print(Card().to_dict())"` first and adjust; the contract is only that `fsrs` round-trips through the library and `due` is readable as an ISO string.

- [ ] **Step 4: Run tests, expect PASS, commit**

```bash
uv run pytest tests/test_scheduler_items.py -v
git add -A && git commit -m "feat: FSRS item scheduling wrapper"
```

---

### Task 6: scheduler/agenda.py — agenda builder with context budget

**Files:**
- Create: `src/seba/scheduler/agenda.py`
- Test: `tests/test_agenda.py`

**Interfaces:**
- Consumes: `models.*`, `scheduler.items.due_items`, `syllabus.frontier`, `store.parse_notes`.
- Produces:
  - `build_agenda(state: GoalState, profile: SubjectProfile, today: date, sources_dir: Path) -> Agenda`
  - `resolve_excerpt(sources_dir: Path, ref: str, budget: int) -> str | None` — ref `"blitzstein/ch09.md#9.2"` → read `sources_dir/blitzstein/ch09.md`, if `#frag` pick the markdown section whose heading contains the fragment, else whole file; truncate to `budget` chars; missing file → `None`.
- Rules (from spec §8a): reviews = `due_items(..., limit=profile.max_reviews_per_session)`; teach concept = first `in-progress` concept, else first frontier concept, else `None`; briefing ≤ 4,000 chars (truncate oldest notes first, append `"(older notes omitted)"`); notes scoped to session concepts (review items' concepts + teach concept + its direct prereqs), ≤3 newest per concept; excerpts total ≤ 16,000 chars, over-budget → keep first source only; `pace_hint` from `state.recent_grades` excluding `skipped`: success = good+easy fraction, >0.9 → `push-harder`, <0.7 → `step-back`, else/empty → `steady`; `practice_quota=3`; deterministic (pure function of args).

- [ ] **Step 1: Write the failing test**

`tests/test_agenda.py`:
```python
from datetime import date
from pathlib import Path

from seba.models import Concept, GoalState, Item, SubjectProfile, Syllabus
from seba.scheduler.agenda import build_agenda, resolve_excerpt

TODAY = date(2026, 7, 3)


def profile(max_reviews=6):
    return SubjectProfile(name="probability", kind="technical",
                          max_reviews_per_session=max_reviews,
                          item_types=["recall", "apply"], session_shape="teach-heavy")


def state(concepts, items=(), notes="", recent=()):
    return GoalState(name="prob", subject="probability",
                     syllabus=Syllabus(goal="prob", subject="probability",
                                       concepts=list(concepts)),
                     items=list(items), notes=notes, session_number=2,
                     recent_grades=list(recent))


def item(id, due="2026-07-01T00:00:00+00:00", concept="a"):
    return Item(id=id, concept=concept, type="recall", front="f", back="b",
                fsrs={"due": due}, created=TODAY)


def test_teach_prefers_in_progress(tmp_path):
    s = state([Concept(id="a", name="A", status="done"),
               Concept(id="b", name="B", status="in-progress"),
               Concept(id="c", name="C")])
    a = build_agenda(s, profile(), TODAY, tmp_path)
    assert a.teach_concept.id == "b"


def test_teach_falls_back_to_frontier_then_none(tmp_path):
    s = state([Concept(id="a", name="A")])
    assert build_agenda(s, profile(), TODAY, tmp_path).teach_concept.id == "a"
    s2 = state([Concept(id="a", name="A", status="done")])
    assert build_agenda(s2, profile(), TODAY, tmp_path).teach_concept is None


def test_reviews_capped_by_profile(tmp_path):
    items = [item(f"it-{i}") for i in range(10)]
    s = state([Concept(id="a", name="A")], items)
    a = build_agenda(s, profile(max_reviews=6), TODAY, tmp_path)
    assert len(a.review_items) == 6


def test_pace_hint(tmp_path):
    s = state([Concept(id="a", name="A")], recent=["good"] * 10)
    assert build_agenda(s, profile(), TODAY, tmp_path).pace_hint == "push-harder"
    s = state([Concept(id="a", name="A")], recent=["again"] * 10)
    assert build_agenda(s, profile(), TODAY, tmp_path).pace_hint == "step-back"
    s = state([Concept(id="a", name="A")], recent=["skipped"] * 10)
    assert build_agenda(s, profile(), TODAY, tmp_path).pace_hint == "steady"


def test_briefing_scoped_notes_and_budget(tmp_path):
    notes = ("## a\n- note-a1\n- note-a2\n- note-a3\n- note-a4\n\n"
             "## zzz\n- irrelevant\n\n")
    s = state([Concept(id="a", name="A")], notes=notes)
    a = build_agenda(s, profile(), TODAY, tmp_path)
    assert "note-a1" in a.briefing and "irrelevant" not in a.briefing
    assert "note-a4" not in a.briefing  # max 3 newest per concept

    s2 = state([Concept(id="a", name="A")], notes="## a\n- " + "x" * 9000 + "\n")
    a2 = build_agenda(s2, profile(), TODAY, tmp_path)
    assert len(a2.briefing) <= 4100 and "(older notes omitted)" in a2.briefing


def test_resolve_excerpt(tmp_path):
    src = tmp_path / "blitz"
    src.mkdir()
    (src / "ch09.md").write_text("# 9.1 Intro\nalpha\n# 9.2 CondExp\nbeta\n")
    assert resolve_excerpt(tmp_path, "blitz/ch09.md#9.2", 1000).strip() == "# 9.2 CondExp\nbeta"
    assert "alpha" in resolve_excerpt(tmp_path, "blitz/ch09.md", 1000)
    assert resolve_excerpt(tmp_path, "blitz/missing.md", 1000) is None
    assert len(resolve_excerpt(tmp_path, "blitz/ch09.md", 10)) == 10


def test_deterministic(tmp_path):
    s = state([Concept(id="a", name="A")], [item("it-1")], recent=["good"])
    a1 = build_agenda(s, profile(), TODAY, tmp_path)
    a2 = build_agenda(s, profile(), TODAY, tmp_path)
    assert a1 == a2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_agenda.py -v` — Expected: FAIL.

- [ ] **Step 3: Implement**

`src/seba/scheduler/agenda.py`:
```python
from datetime import date
from pathlib import Path

from seba.models import (Agenda, GoalState, PaceHint, ReviewItem, SubjectProfile,
                          TeachConcept)
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


def _pace(recent: list[str]) -> PaceHint:
    graded = [g for g in recent if g != "skipped"]
    if not graded:
        return "steady"
    rate = sum(g in ("good", "easy") for g in graded) / len(graded)
    if rate > 0.9:
        return "push-harder"
    if rate < 0.7:
        return "step-back"
    return "steady"


def build_agenda(state: GoalState, profile: SubjectProfile, today: date,
                 sources_dir: Path) -> Agenda:
    due = due_items(state.items, today, profile.max_reviews_per_session)
    reviews = [ReviewItem(id=i.id, type=i.type, front=i.front, back=i.back)
               for i in due]

    concepts = state.syllabus.concepts
    teach_src = (next((c for c in concepts if c.status == "in-progress"), None)
                 or next(iter(frontier(state.syllabus)), None))
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
        teach = TeachConcept(id=teach_src.id, name=teach_src.name,
                             source_excerpts=excerpts,
                             guidance=f"estimated {teach_src.est_sessions} session(s)")
        scope |= {teach_src.id, *teach_src.prereqs}

    done = sum(c.status == "done" for c in concepts)
    front = ", ".join(c.id for c in frontier(state.syllabus)[:10])
    lines = [f"Session {state.session_number}. Concepts done: {done}/{len(concepts)}.",
             f"Frontier: {front or 'none'}."]
    if state.last_hint:
        lines.append(f"Last session's hint: {state.last_hint}")
    notes = parse_notes(state.notes)
    for cid in sorted(scope):
        for note in notes.get(cid, [])[:3]:
            lines.append(f"[{cid}] {note}")
    briefing = "\n".join(lines)
    if len(briefing) > BRIEFING_BUDGET:
        briefing = briefing[:BRIEFING_BUDGET] + "\n(older notes omitted)"

    return Agenda(goal=state.name, subject=state.subject,
                  session_number=state.session_number, briefing=briefing,
                  review_items=reviews, teach_concept=teach, practice_quota=3,
                  pace_hint=_pace(state.recent_grades))
```

- [ ] **Step 4: Run tests, expect PASS, commit**

```bash
uv run pytest tests/test_agenda.py -v
git add -A && git commit -m "feat: agenda builder with context budgets and pace hint"
```

---

### Task 7: session/tools.py — outcome tools, handlers, gates

**Files:**
- Create: `src/seba/session/__init__.py`, `src/seba/session/tools.py`
- Test: `tests/test_tools.py`

**Interfaces:**
- Consumes: `models.*`.
- Produces:
  - `TOOL_MODELS = {"grade_review": GradeReview, "mint_item": MintItem, "update_concept": UpdateConcept, "end_session": EndSession}`
  - `anthropic_tools() -> list[dict]` — API tool definitions: `{"name", "description" (model docstring), "input_schema" (model_json_schema())}` for each, plus `fetch_source`: `{"name": "fetch_source", "description": "Fetch a source excerpt by ref, e.g. blitzstein/ch09.md#9.2", "input_schema": {"type": "object", "properties": {"ref": {"type": "string"}}, "required": ["ref"]}}`.
  - `class ToolHandler: __init__(self, agenda: Agenda, syllabus: Syllabus, sources_dir: Path)`; attribute `record: SessionRecord`; method `handle(name: str, args: dict) -> tuple[str, bool]` — returns `(result_text, is_error)`.
- Handler rules (spec §4.4 + gates): unknown tool → error; invalid args → pydantic error text as result, `is_error=True`; `grade_review.id` must be in agenda review items and not already graded; `mint_item` — concept must exist in syllabus, cap 10 (11th rejected: `"mint cap reached (10)"`); `update_concept.id` must exist in syllabus; **session-end gate**: `end_session` rejected with the list of ungraded review ids while any agenda review lacks a grade; accepted `end_session` sets `record.summary/next_session_hint/complete=True`; second `end_session` rejected; `fetch_source` delegates to `resolve_excerpt` (missing → error text).
  - `missing_grades(self) -> list[str]` — agenda review ids not yet graded (used by dialogue on `/done`).

- [ ] **Step 1: Write the failing test**

`tests/test_tools.py`:
```python
from pathlib import Path

import pytest
from seba.models import Agenda, Concept, ReviewItem, Syllabus
from seba.session.tools import ToolHandler, anthropic_tools


@pytest.fixture
def handler(tmp_path: Path):
    agenda = Agenda(goal="g", subject="probability", session_number=1, briefing="",
                    review_items=[ReviewItem(id="it-1", type="recall", front="f", back="b"),
                                  ReviewItem(id="it-2", type="recall", front="f", back="b")],
                    teach_concept=None, practice_quota=3, pace_hint="steady")
    syllabus = Syllabus(goal="g", subject="probability",
                        concepts=[Concept(id="bayes", name="Bayes")])
    return ToolHandler(agenda, syllabus, tmp_path)


def test_anthropic_tools_shape():
    tools = anthropic_tools()
    names = {t["name"] for t in tools}
    assert names == {"grade_review", "mint_item", "update_concept",
                     "end_session", "fetch_source"}
    assert all("input_schema" in t and t["description"] for t in tools)


def test_grade_review_ok_and_duplicate(handler):
    text, err = handler.handle("grade_review", {"id": "it-1", "grade": "good"})
    assert not err and handler.record.reviews[0].grade == "good"
    _, err2 = handler.handle("grade_review", {"id": "it-1", "grade": "easy"})
    assert err2  # already graded


def test_grade_review_unknown_id(handler):
    text, err = handler.handle("grade_review", {"id": "it-99", "grade": "good"})
    assert err and "it-99" in text


def test_grade_review_bad_args(handler):
    _, err = handler.handle("grade_review", {"id": "it-1", "grade": "great"})
    assert err


def test_mint_cap(handler):
    for i in range(10):
        _, err = handler.handle("mint_item", {"concept": "bayes", "type": "recall",
                                              "front": f"f{i}", "back": "b"})
        assert not err
    text, err = handler.handle("mint_item", {"concept": "bayes", "type": "recall",
                                             "front": "f10", "back": "b"})
    assert err and "cap" in text


def test_mint_unknown_concept(handler):
    _, err = handler.handle("mint_item", {"concept": "ghost", "type": "recall",
                                          "front": "f", "back": "b"})
    assert err


def test_end_session_gate(handler):
    text, err = handler.handle("end_session", {"summary": "s", "next_session_hint": "h"})
    assert err and "it-1" in text and "it-2" in text
    handler.handle("grade_review", {"id": "it-1", "grade": "good"})
    handler.handle("grade_review", {"id": "it-2", "grade": "skipped"})
    _, err2 = handler.handle("end_session", {"summary": "s", "next_session_hint": "h"})
    assert not err2 and handler.record.complete
    _, err3 = handler.handle("end_session", {"summary": "s2", "next_session_hint": "h"})
    assert err3  # exactly once


def test_missing_grades(handler):
    assert handler.missing_grades() == ["it-1", "it-2"]
    handler.handle("grade_review", {"id": "it-1", "grade": "again"})
    assert handler.missing_grades() == ["it-2"]


def test_fetch_source(handler, tmp_path):
    (tmp_path / "x.md").write_text("hello")
    text, err = handler.handle("fetch_source", {"ref": "x.md"})
    assert not err and text == "hello"
    _, err2 = handler.handle("fetch_source", {"ref": "missing.md"})
    assert err2


def test_unknown_tool(handler):
    _, err = handler.handle("nonsense", {})
    assert err
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_tools.py -v` — Expected: FAIL.

- [ ] **Step 3: Implement**

`src/seba/session/__init__.py`: (empty file)

`src/seba/session/tools.py`:
```python
from pathlib import Path

from pydantic import BaseModel, ValidationError

from seba.models import (Agenda, EndSession, GradeReview, MintItem,
                          SessionRecord, Syllabus, UpdateConcept)
from seba.scheduler.agenda import resolve_excerpt

MINT_CAP = 10

TOOL_MODELS: dict[str, type[BaseModel]] = {
    "grade_review": GradeReview,
    "mint_item": MintItem,
    "update_concept": UpdateConcept,
    "end_session": EndSession,
}


def anthropic_tools() -> list[dict]:
    tools = [{"name": name,
              "description": model.__doc__ or name,
              "input_schema": model.model_json_schema()}
             for name, model in TOOL_MODELS.items()]
    tools.append({"name": "fetch_source",
                  "description": "Fetch a source excerpt by ref, "
                                 "e.g. blitzstein/ch09.md#9.2",
                  "input_schema": {"type": "object",
                                   "properties": {"ref": {"type": "string"}},
                                   "required": ["ref"]}})
    return tools


class ToolHandler:
    def __init__(self, agenda: Agenda, syllabus: Syllabus, sources_dir: Path):
        self.agenda = agenda
        self.syllabus = syllabus
        self.sources_dir = sources_dir
        self.record = SessionRecord()

    def missing_grades(self) -> list[str]:
        graded = {r.id for r in self.record.reviews}
        return [r.id for r in self.agenda.review_items if r.id not in graded]

    def handle(self, name: str, args: dict) -> tuple[str, bool]:
        if name == "fetch_source":
            ex = resolve_excerpt(self.sources_dir, str(args.get("ref", "")), 16_000)
            return (ex, False) if ex is not None else (f"no such source: {args}", True)
        model = TOOL_MODELS.get(name)
        if model is None:
            return f"unknown tool: {name}", True
        try:
            call = model.model_validate(args)
        except ValidationError as e:
            return str(e), True
        return getattr(self, f"_{name}")(call)

    def _grade_review(self, call: GradeReview) -> tuple[str, bool]:
        if call.id not in {r.id for r in self.agenda.review_items}:
            return f"'{call.id}' is not in this session's review items", True
        if call.id in {r.id for r in self.record.reviews}:
            return f"'{call.id}' already graded", True
        self.record.reviews.append(call)
        return "recorded", False

    def _mint_item(self, call: MintItem) -> tuple[str, bool]:
        if len(self.record.new_items) >= MINT_CAP:
            return f"mint cap reached ({MINT_CAP}); no more cards this session", True
        if call.concept not in {c.id for c in self.syllabus.concepts}:
            return f"unknown concept: '{call.concept}'", True
        self.record.new_items.append(call)
        return "minted", False

    def _update_concept(self, call: UpdateConcept) -> tuple[str, bool]:
        if call.id not in {c.id for c in self.syllabus.concepts}:
            return f"unknown concept: '{call.id}'", True
        self.record.concepts.append(call)
        return "recorded", False

    def _end_session(self, call: EndSession) -> tuple[str, bool]:
        if self.record.complete:
            return "session already ended", True
        missing = self.missing_grades()
        if missing:
            return ("cannot end: ungraded review items: "
                    + ", ".join(missing)
                    + ". Grade each (or grade as 'skipped') first."), True
        self.record.summary = call.summary
        self.record.next_session_hint = call.next_session_hint
        self.record.complete = True
        return "session ended", False
```

- [ ] **Step 4: Run tests, expect PASS, commit**

```bash
uv run pytest tests/test_tools.py -v
git add -A && git commit -m "feat: outcome tools with validation and session-end gate"
```

---

### Task 8: prompts + bundled subject profiles

**Files:**
- Create: `src/seba/session/prompts/system_base.md`, `src/seba/session/prompts/recovery.md`, `subjects/probability/profile.yaml`, `subjects/probability/overlay.md`, `subjects/italian/profile.yaml`, `subjects/italian/overlay.md`, `subjects/_templates/technical/profile.yaml`, `subjects/_templates/technical/overlay.md`, `subjects/_templates/language/profile.yaml`, `subjects/_templates/language/overlay.md`, `src/seba/session/loader.py`
- Test: `tests/test_loader.py`

**Interfaces:**
- Consumes: `config.subjects_dirs()`, `models.SubjectProfile`.
- Produces:
  - `load_profile(subject: str) -> SubjectProfile | None` — searches `config.subjects_dirs()` in order for `<subject>/profile.yaml`.
  - `load_overlay(subject: str) -> str` — the subject's `overlay.md` text ("" if missing).
  - `system_prompt(agenda: Agenda, overlay: str) -> str` — `system_base.md` formatted with `{overlay}` and `{agenda_yaml}` (agenda serialized via `yaml.safe_dump(agenda.model_dump())`).
  - `recovery_prompt(transcript: str, agenda_yaml: str) -> str`.

- [ ] **Step 1: Write the prompt and profile files**

`src/seba/session/prompts/system_base.md`:
```markdown
You are a long-term personal tutor, mid-relationship with this learner.
The agenda below is your memory of them — reference it naturally
("last time you were shaky on…"), never robotically.

# Pedagogy policy
- New concepts: worked example first, then faded scaffolding
  (fill-in-the-blank → guided → independent practice). Target roughly
  85% learner success; honor the agenda's pace_hint.
- Ask "why?" and "convince me" follow-ups. Prompt self-explanation.
- When correcting, NAME the misconception explicitly, then fix it.
- Never dump an answer the learner could produce with one more hint.
- Tangents are welcome — follow them, and record anything durable via
  update_concept or mint_item.

# Session conduct
1. Open with one sentence of continuity from the briefing, then begin the
   review items, woven in conversationally. Get a real answer attempt
   before revealing anything. Call grade_review the moment each review
   resolves (grades: again/hard/good/easy; skipped only if never reached).
2. Reviews done → teach the agenda's teach_concept using its source
   excerpts. Practice questions as you go (about practice_quota of them).
   Record progress with update_concept; mint spaced-repetition cards with
   mint_item for anything worth retaining a month from now.
3. When the learner says they're done (or the session naturally closes):
   recap aloud in 2-3 sentences, then call end_session with a 3-6 sentence
   summary and a concrete next_session_hint. You cannot end while agenda
   review items are ungraded — grade or mark them skipped first.

# Subject style
{overlay}

# Agenda
```yaml
{agenda_yaml}
```
```

`src/seba/session/prompts/recovery.md`:
```markdown
A tutoring session ended abnormally. Below are its agenda and transcript.
Reconstruct what happened by calling the outcome tools: grade_review for
each agenda review item the transcript shows an attempt for (grade
strictly by the rubric; items never reached → grade "skipped"),
update_concept / mint_item for durable progress shown, and finally
end_session with a faithful summary and next_session_hint. Call tools
only — no prose.

# Agenda
```yaml
{agenda_yaml}
```

# Transcript
{transcript}
```

`subjects/probability/profile.yaml`:
```yaml
name: probability
kind: technical
max_reviews_per_session: 6
item_types: [recall, apply]
session_shape: teach-heavy
```

`subjects/probability/overlay.md`:
```markdown
Subject: probability theory. Use Unicode math notation inline
(σ-algebra, 𝔼[X|Y], ℙ(A|B)); LaTeX in fenced blocks only for long
derivations. Practice forms: compute, prove-sketch, find-a-counterexample.
Push for precise statements AND intuitions — a theorem the learner cannot
motivate is not mastered.
```

`subjects/italian/profile.yaml`:
```yaml
name: italian
kind: language
max_reviews_per_session: 20
item_types: [recognize, produce, cloze]
session_shape: review-heavy
```

`subjects/italian/overlay.md`:
```markdown
Subject: Italian. Conduct an increasing fraction of the session in
Italian as the learner's level (per the briefing) allows; recast into
Italian what they say in English when they could have said it in Italian.
Prefer production over recognition. Correct errors by recasting the
sentence correctly, then drill the underlying pattern once or twice.
```

`subjects/_templates/technical/profile.yaml`:
```yaml
name: TEMPLATE
kind: technical
max_reviews_per_session: 6
item_types: [recall, apply]
session_shape: teach-heavy
```

`subjects/_templates/technical/overlay.md`:
```markdown
Subject: SUBJECT_NAME. Practice forms: compute, derive, predict-the-output,
find-a-counterexample. Push for precise statements AND intuitions.
```

`subjects/_templates/language/profile.yaml`:
```yaml
name: TEMPLATE
kind: language
max_reviews_per_session: 20
item_types: [recognize, produce, cloze]
session_shape: review-heavy
```

`subjects/_templates/language/overlay.md`:
```markdown
Subject: SUBJECT_NAME. Conduct an increasing fraction of the session in
the target language as the learner's level allows. Prefer production over
recognition. Correct by recasting, then drill the pattern.
```

- [ ] **Step 2: Write the failing test**

`tests/test_loader.py`:
```python
from seba.models import Agenda
from seba.session.loader import load_overlay, load_profile, recovery_prompt, system_prompt


def agenda():
    return Agenda(goal="g", subject="probability", session_number=1,
                  briefing="Session 1.", review_items=[], teach_concept=None,
                  practice_quota=3, pace_hint="steady")


def test_load_bundled_profiles():
    p = load_profile("probability")
    assert p.max_reviews_per_session == 6 and p.kind == "technical"
    i = load_profile("italian")
    assert i.max_reviews_per_session == 20
    assert load_profile("nonexistent") is None


def test_user_profile_overrides(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBA_DATA_DIR", str(tmp_path))
    d = tmp_path / "subjects" / "astronomy"
    d.mkdir(parents=True)
    (d / "profile.yaml").write_text(
        "name: astronomy\nkind: technical\nmax_reviews_per_session: 4\n"
        "item_types: [recall]\nsession_shape: teach-heavy\n")
    assert load_profile("astronomy").max_reviews_per_session == 4


def test_overlay_and_system_prompt():
    overlay = load_overlay("probability")
    assert "σ-algebra" in overlay
    sp = system_prompt(agenda(), overlay)
    assert "Session 1." in sp and "σ-algebra" in sp and "{overlay}" not in sp


def test_recovery_prompt():
    rp = recovery_prompt("the transcript", "goal: g")
    assert "the transcript" in rp and "goal: g" in rp
```

- [ ] **Step 3: Run test to verify it fails**

Run: `uv run pytest tests/test_loader.py -v` — Expected: FAIL.

- [ ] **Step 4: Implement**

`src/seba/session/loader.py`:
```python
from pathlib import Path

import yaml

from seba import config
from seba.models import Agenda, SubjectProfile

_PROMPTS = Path(__file__).parent / "prompts"


def load_profile(subject: str) -> SubjectProfile | None:
    for base in config.subjects_dirs():
        p = base / subject / "profile.yaml"
        if p.exists():
            return SubjectProfile.model_validate(yaml.safe_load(p.read_text()))
    return None


def load_overlay(subject: str) -> str:
    for base in config.subjects_dirs():
        p = base / subject / "overlay.md"
        if p.exists():
            return p.read_text()
    return ""


def system_prompt(agenda: Agenda, overlay: str) -> str:
    template = (_PROMPTS / "system_base.md").read_text()
    return template.format(
        overlay=overlay,
        agenda_yaml=yaml.safe_dump(agenda.model_dump(), sort_keys=False))


def recovery_prompt(transcript: str, agenda_yaml: str) -> str:
    template = (_PROMPTS / "recovery.md").read_text()
    return template.format(transcript=transcript, agenda_yaml=agenda_yaml)
```

Note: `config.subjects_dirs()[0]` resolves to the repo's `subjects/` because `REPO_ROOT` in Task 1 points two levels above `src/seba/config.py`. Verify: `uv run python -c "from seba import config; print(config.subjects_dirs())"`.

- [ ] **Step 5: Run tests, expect PASS, commit**

```bash
uv run pytest tests/test_loader.py -v
git add -A && git commit -m "feat: prompts, subject profiles, and loaders"
```

---

### Task 9: session/dialogue.py — the conversation loop

**Files:**
- Create: `src/seba/session/dialogue.py`
- Test: `tests/test_dialogue.py`

**Interfaces:**
- Consumes: `session.tools.ToolHandler`, `session.tools.anthropic_tools`, `session.loader.system_prompt`, `models.*`.
- Produces:
  - `class SessionIO(Protocol): def get_input(self) -> str | None: ...` (None = EOF/Ctrl-D) `; def show_chunk(self, text: str) -> None: ...` `; def show(self, text: str) -> None: ...`
  - `Send = Callable[[str, list[dict]], "AssistantMessage"]` — takes (system_prompt, messages), returns an object with `.content` (list of blocks, each having `.type` in `{"text","tool_use"}`; tool_use blocks have `.id`, `.name`, `.input`) and `.stop_reason` (`"tool_use"` or `"end_turn"`). Production impl wraps `anthropic` client; tests pass fakes.
  - `run_session(agenda: Agenda, syllabus: Syllabus, overlay: str, sources_dir: Path, io: SessionIO, send: Send) -> tuple[SessionRecord, str]` — returns (handler.record, transcript).
  - `make_send(client, model: str) -> Send` — wraps `client.messages.stream(...)`, streaming text via a callback is handled inside `run_session`; for v0 `make_send` uses `client.messages.create` (non-streaming call, whole message shown at once) — acceptable, REPL still feels responsive; streaming upgrade is cosmetic and deferred.
- Loop semantics: seed messages with `{"role": "user", "content": "(session start — greet and begin)"}`; call `send`; for each content block: text → `io.show_chunk` + transcript; tool_use → `handler.handle(name, input)`, append tool_result (with `is_error` flag) and re-`send` until `stop_reason != "tool_use"`. Then: if `handler.record.complete` → return. Else `io.get_input()`: `None` or `/done` with no missing grades → return; `/done` with missing grades → inject user message `"(user is done; ungraded reviews: …ids…; grade or skip each, then end_session)"` and continue; otherwise append user text and continue. Transcript accumulates `"TUTOR: …"`, `"LEARNER: …"`, `"[tool] name(args) -> result"` lines.

- [ ] **Step 1: Write the failing test**

`tests/test_dialogue.py`:
```python
from pathlib import Path
from types import SimpleNamespace

from seba.models import Agenda, Concept, ReviewItem, Syllabus
from seba.session.dialogue import run_session


def text_block(t):
    return SimpleNamespace(type="text", text=t)


def tool_block(id, name, input):
    return SimpleNamespace(type="tool_use", id=id, name=name, input=input)


def msg(blocks, stop="end_turn"):
    return SimpleNamespace(content=blocks, stop_reason=stop)


class ScriptedIO:
    def __init__(self, inputs):
        self.inputs = list(inputs)
        self.shown = []

    def get_input(self):
        return self.inputs.pop(0) if self.inputs else None

    def show_chunk(self, text):
        self.shown.append(text)

    def show(self, text):
        self.shown.append(text)


def make_send(script):
    calls = list(script)

    def send(system, messages):
        return calls.pop(0)
    return send


def fixtures():
    agenda = Agenda(goal="g", subject="probability", session_number=1, briefing="b",
                    review_items=[ReviewItem(id="it-1", type="recall", front="f", back="b")],
                    teach_concept=None, practice_quota=3, pace_hint="steady")
    syllabus = Syllabus(goal="g", subject="probability",
                        concepts=[Concept(id="bayes", name="Bayes")])
    return agenda, syllabus


def test_full_session_with_tools(tmp_path: Path):
    agenda, syllabus = fixtures()
    script = [
        msg([text_block("Welcome back! State Bayes?")]),
        msg([tool_block("t1", "grade_review", {"id": "it-1", "grade": "good"}),
             text_block("Correct!")], stop="tool_use"),
        msg([text_block("Anything else?")]),
        msg([tool_block("t2", "end_session",
                        {"summary": "Reviewed Bayes.", "next_session_hint": "go on"})],
            stop="tool_use"),
        msg([text_block("Bye!")]),
    ]
    io = ScriptedIO(["P(A|B) = P(B|A)P(A)/P(B)", "/done"])
    record, transcript = run_session(agenda, syllabus, "", tmp_path, io,
                                     make_send(script))
    assert record.complete and record.reviews[0].grade == "good"
    assert "Welcome back!" in transcript and "LEARNER:" in transcript


def test_done_with_missing_grades_injects_reminder(tmp_path: Path):
    agenda, syllabus = fixtures()
    script = [
        msg([text_block("Hi!")]),
        # after /done reminder, model grades then ends
        msg([tool_block("t1", "grade_review", {"id": "it-1", "grade": "skipped"}),
             tool_block("t2", "end_session",
                        {"summary": "s", "next_session_hint": "h"})], stop="tool_use"),
        msg([text_block("Bye")]),
    ]
    io = ScriptedIO(["/done"])
    record, _ = run_session(agenda, syllabus, "", tmp_path, io, make_send(script))
    assert record.complete and record.reviews[0].grade == "skipped"


def test_eof_returns_incomplete(tmp_path: Path):
    agenda, syllabus = fixtures()
    script = [msg([text_block("Hi!")])]
    io = ScriptedIO([])  # immediate EOF
    record, transcript = run_session(agenda, syllabus, "", tmp_path, io,
                                     make_send(script))
    assert not record.complete and "Hi!" in transcript


def test_tool_error_fed_back(tmp_path: Path):
    agenda, syllabus = fixtures()
    captured = []

    def send(system, messages):
        captured.append([m for m in messages])
        if len(captured) == 1:
            return msg([tool_block("t1", "grade_review",
                                   {"id": "it-99", "grade": "good"})], stop="tool_use")
        return msg([text_block("oops, retrying")])

    io = ScriptedIO([])
    record, _ = run_session(agenda, syllabus, "", tmp_path, io, send)
    # second call's messages must include an error tool_result
    last = captured[-1][-1]
    assert last["role"] == "user"
    assert last["content"][0]["type"] == "tool_result"
    assert last["content"][0]["is_error"] is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_dialogue.py -v` — Expected: FAIL.

- [ ] **Step 3: Implement**

`src/seba/session/dialogue.py`:
```python
import json
from pathlib import Path
from typing import Callable, Protocol

from seba.models import Agenda, SessionRecord, Syllabus
from seba.session.loader import system_prompt
from seba.session.tools import ToolHandler, anthropic_tools


class SessionIO(Protocol):
    def get_input(self) -> str | None: ...
    def show_chunk(self, text: str) -> None: ...
    def show(self, text: str) -> None: ...


Send = Callable[[str, list[dict]], object]


def make_send(client, model: str) -> Send:
    tools = anthropic_tools()

    def send(system: str, messages: list[dict]):
        return client.messages.create(model=model, max_tokens=2000,
                                      system=system, messages=messages,
                                      tools=tools)
    return send


def _assistant_blocks(message) -> list[dict]:
    out = []
    for b in message.content:
        if b.type == "text":
            out.append({"type": "text", "text": b.text})
        elif b.type == "tool_use":
            out.append({"type": "tool_use", "id": b.id, "name": b.name,
                        "input": b.input})
    return out


def run_session(agenda: Agenda, syllabus: Syllabus, overlay: str,
                sources_dir: Path, io: SessionIO, send: Send
                ) -> tuple[SessionRecord, str]:
    handler = ToolHandler(agenda, syllabus, sources_dir)
    system = system_prompt(agenda, overlay)
    messages: list[dict] = [
        {"role": "user", "content": "(session start — greet and begin)"}]
    transcript: list[str] = []

    while True:
        message = send(system, messages)
        messages.append({"role": "assistant",
                         "content": _assistant_blocks(message)})
        results = []
        for block in message.content:
            if block.type == "text":
                io.show_chunk(block.text)
                transcript.append(f"TUTOR: {block.text}")
            elif block.type == "tool_use":
                result, is_error = handler.handle(block.name, dict(block.input))
                transcript.append(
                    f"[tool] {block.name}({json.dumps(dict(block.input))})"
                    f" -> {result}")
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": result, "is_error": is_error})
        if results:
            messages.append({"role": "user", "content": results})
        if message.stop_reason == "tool_use":
            continue
        if handler.record.complete:
            return handler.record, "\n".join(transcript)

        user = io.get_input()
        if user is None:
            return handler.record, "\n".join(transcript)
        if user.strip() == "/done":
            missing = handler.missing_grades()
            if not missing and handler.record.complete:
                return handler.record, "\n".join(transcript)
            user = ("(user is done; ungraded reviews: "
                    + (", ".join(missing) or "none")
                    + "; grade or skip each, then call end_session)")
        transcript.append(f"LEARNER: {user}")
        messages.append({"role": "user", "content": user})
```

- [ ] **Step 4: Run tests, expect PASS, commit**

```bash
uv run pytest tests/test_dialogue.py -v
git add -A && git commit -m "feat: session dialogue loop with tool dispatch"
```

---

### Task 10: session/recovery.py — backfill crashed sessions

**Files:**
- Create: `src/seba/session/recovery.py`
- Test: `tests/test_recovery.py`

**Interfaces:**
- Consumes: `ToolHandler`, `anthropic_tools`, `loader.recovery_prompt`, `Send` (same shape as Task 9).
- Produces: `recover_session(transcript: str, agenda: Agenda, syllabus: Syllabus, sources_dir: Path, send: Send) -> SessionRecord` — drives the same tool loop with the recovery prompt as system, a single fixed user message `"(reconstruct the session via tool calls)"`, and NO human input; loops on `stop_reason == "tool_use"` feeding tool results back; returns `handler.record` when the model stops or `end_session` is accepted; hard cap 20 send-rounds (`RecoveryError` beyond — prevents infinite loops).

- [ ] **Step 1: Write the failing test**

`tests/test_recovery.py`:
```python
from pathlib import Path
from types import SimpleNamespace

import pytest
from seba.models import Agenda, Concept, ReviewItem, Syllabus
from seba.session.recovery import RecoveryError, recover_session


def tool_block(id, name, input):
    return SimpleNamespace(type="tool_use", id=id, name=name, input=input)


def msg(blocks, stop="end_turn"):
    return SimpleNamespace(content=blocks, stop_reason=stop)


def fixtures():
    agenda = Agenda(goal="g", subject="probability", session_number=1, briefing="",
                    review_items=[ReviewItem(id="it-1", type="recall", front="f", back="b")],
                    teach_concept=None, practice_quota=3, pace_hint="steady")
    syllabus = Syllabus(goal="g", subject="probability",
                        concepts=[Concept(id="bayes", name="Bayes")])
    return agenda, syllabus


def test_recovery_builds_record(tmp_path: Path):
    agenda, syllabus = fixtures()
    script = [
        msg([tool_block("t1", "grade_review", {"id": "it-1", "grade": "hard"}),
             tool_block("t2", "end_session",
                        {"summary": "recovered", "next_session_hint": "h"})],
            stop="tool_use"),
        msg([]),
    ]
    calls = list(script)
    record = recover_session("TUTOR: hi", agenda, syllabus, tmp_path,
                             lambda s, m: calls.pop(0))
    assert record.complete and record.reviews[0].grade == "hard"
    assert record.summary == "recovered"


def test_recovery_round_cap(tmp_path: Path):
    agenda, syllabus = fixtures()

    def looping_send(system, messages):
        return msg([tool_block("t", "update_concept", {"id": "bayes"})],
                   stop="tool_use")

    with pytest.raises(RecoveryError):
        recover_session("t", agenda, syllabus, tmp_path, looping_send)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_recovery.py -v` — Expected: FAIL.

- [ ] **Step 3: Implement**

`src/seba/session/recovery.py`:
```python
import json
from pathlib import Path

import yaml

from seba.models import Agenda, SessionRecord, Syllabus
from seba.session.dialogue import Send, _assistant_blocks
from seba.session.loader import recovery_prompt
from seba.session.tools import ToolHandler

MAX_ROUNDS = 20


class RecoveryError(Exception):
    pass


def recover_session(transcript: str, agenda: Agenda, syllabus: Syllabus,
                    sources_dir: Path, send: Send) -> SessionRecord:
    handler = ToolHandler(agenda, syllabus, sources_dir)
    system = recovery_prompt(
        transcript, yaml.safe_dump(agenda.model_dump(), sort_keys=False))
    messages: list[dict] = [
        {"role": "user", "content": "(reconstruct the session via tool calls)"}]
    for _ in range(MAX_ROUNDS):
        message = send(system, messages)
        messages.append({"role": "assistant",
                         "content": _assistant_blocks(message)})
        results = []
        for block in message.content:
            if block.type == "tool_use":
                result, is_error = handler.handle(block.name, dict(block.input))
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": result, "is_error": is_error})
        if results:
            messages.append({"role": "user", "content": results})
        if message.stop_reason != "tool_use" or handler.record.complete:
            return handler.record
    raise RecoveryError(f"recovery did not converge in {MAX_ROUNDS} rounds")
```

- [ ] **Step 4: Run tests, expect PASS, commit**

```bash
uv run pytest tests/test_recovery.py -v
git add -A && git commit -m "feat: crashed-session recovery via tool replay"
```

---

### Task 11: applying a SessionRecord to state

**Files:**
- Create: `src/seba/scheduler/apply.py`
- Test: `tests/test_apply.py`

**Interfaces:**
- Consumes: `scheduler.items.apply_review/mint_item`, `syllabus.apply_status`, `models.*`.
- Produces: `apply_record(state: GoalState, record: SessionRecord, now: datetime) -> GoalState` — pure function: grades applied to matching items (`skipped` no-op; grade for an id not in `state.items` ignored — recovery may over-report); minted items appended; `status_change: "started"` → `in-progress`, `"completed"` → `done`, applied via `apply_status` with illegal moves *skipped with no error* (the tutor may re-report an existing status; state must never corrupt).

- [ ] **Step 1: Write the failing test**

`tests/test_apply.py`:
```python
from datetime import date, datetime, timezone

from seba.models import (Concept, GoalState, GradeReview, Item, MintItem,
                          SessionRecord, Syllabus, UpdateConcept)
from seba.scheduler.apply import apply_record

NOW = datetime(2026, 7, 3, tzinfo=timezone.utc)


def state():
    return GoalState(
        name="g", subject="probability",
        syllabus=Syllabus(goal="g", subject="probability",
                          concepts=[Concept(id="bayes", name="B", status="unseen")]),
        items=[Item(id="it-1", concept="bayes", type="recall", front="f", back="b",
                    fsrs={"due": "2026-07-01T00:00:00+00:00", "state": 1},
                    created=date(2026, 6, 1))],
        session_number=1)


def test_apply_grades_mints_and_statuses():
    rec = SessionRecord(
        reviews=[GradeReview(id="it-1", grade="good")],
        new_items=[MintItem(concept="bayes", type="recall", front="nf", back="nb")],
        concepts=[UpdateConcept(id="bayes", status_change="started")],
        summary="s", next_session_hint="h", complete=True)
    out = apply_record(state(), rec, NOW)
    assert len(out.items) == 2
    assert out.items[0].fsrs["due"] != "2026-07-01T00:00:00+00:00"
    assert out.syllabus.concepts[0].status == "in-progress"


def test_skipped_and_unknown_ids_are_safe():
    rec = SessionRecord(
        reviews=[GradeReview(id="it-1", grade="skipped"),
                 GradeReview(id="it-ghost", grade="good")],
        concepts=[UpdateConcept(id="bayes", status_change="completed")])  # illegal jump
    out = apply_record(state(), rec, NOW)
    assert out.items[0] == state().items[0]
    assert out.syllabus.concepts[0].status == "unseen"  # illegal move skipped, no error
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_apply.py -v` — Expected: FAIL.

- [ ] **Step 3: Implement**

`src/seba/scheduler/apply.py`:
```python
from datetime import datetime

from seba.models import GoalState, SessionRecord
from seba.scheduler.items import apply_review, mint_item
from seba.syllabus.graph import SyllabusError, apply_status

_STATUS = {"started": "in-progress", "completed": "done"}


def apply_record(state: GoalState, record: SessionRecord,
                 now: datetime) -> GoalState:
    grades = {r.id: r.grade for r in record.reviews}
    items = [apply_review(i, grades[i.id], now) if i.id in grades else i
             for i in state.items]
    items += [mint_item(m, now.date()) for m in record.new_items]

    syllabus = state.syllabus
    for c in record.concepts:
        if c.status_change:
            try:
                syllabus = apply_status(syllabus, c.id, _STATUS[c.status_change])
            except SyllabusError:
                pass  # re-reported or illegal move: never corrupt state
    return state.model_copy(update={"items": items, "syllabus": syllabus})
```

- [ ] **Step 4: Run tests, expect PASS, commit**

```bash
uv run pytest tests/test_apply.py -v
git add -A && git commit -m "feat: apply session record to goal state"
```

---

### Task 12: synthesis — new-goal drafting + $EDITOR loop

**Files:**
- Create: `src/seba/synthesis/__init__.py`, `src/seba/synthesis/synthesize.py`, `src/seba/synthesis/prompts/synthesis.md`
- Test: `tests/test_synthesis.py`

**Interfaces:**
- Consumes: `syllabus.load_syllabus`, `models.Syllabus`, anthropic client (injected as `complete: Callable[[str], str]` — takes a prompt, returns text).
- Produces:
  - `draft_syllabus(goal: str, subject: str, toc: str, complete: Callable[[str], str]) -> str` — returns raw YAML text (strips markdown fences if the model wrapped it).
  - `edit_until_valid(yaml_text: str, path: Path, editor: Callable[[Path], None]) -> Syllabus` — writes text to `path`, invokes `editor(path)` (production: `subprocess.run([$EDITOR or "nano", path])`), loads+validates; on `SyllabusError` prepends `# ERRORS:` comment lines and re-invokes editor; 3 failures → raise. `editor` injected for tests.
  - `default_editor(path: Path) -> None` — the subprocess implementation.

- [ ] **Step 1: Write the prompt file**

`src/seba/synthesis/prompts/synthesis.md`:
```markdown
You are designing a long-term study syllabus. Goal: "{goal}". Subject
preset: {subject}.

Below is the table of contents of the primary source. Produce a concept
graph as YAML: top-level keys `goal`, `subject`, `concepts`; each concept
has `id` (kebab-case), `name`, `prereqs` (list of ids), `sources` (list of
"<source-dir>/<file>#<section>" refs into the ToC where applicable),
`status: unseen`, `est_sessions` (1-3).

Rules: concepts sized to 1-3 sessions each; prereq edges may REORDER or
cut across the book's chapter order; INSERT prerequisite concepts the book
assumes but does not teach; the book guides, it does not dictate. Output
ONLY the YAML.

# Table of contents
{toc}
```

- [ ] **Step 2: Write the failing test**

`tests/test_synthesis.py`:
```python
from pathlib import Path

import pytest
from seba.syllabus.graph import SyllabusError
from seba.synthesis.synthesize import draft_syllabus, edit_until_valid

GOOD = """goal: g
subject: probability
concepts:
  - id: a
    name: A
"""
BAD = GOOD.replace("name: A", "name: A\n    prereqs: [ghost]")


def test_draft_strips_fences():
    out = draft_syllabus("g", "probability", "ch1",
                         lambda p: "```yaml\n" + GOOD + "```")
    assert out.strip() == GOOD.strip()
    assert "ch1" in_prompt_capture()  # see capture helper below


_captured = {}


def in_prompt_capture():
    return _captured.get("prompt", "")


def test_draft_prompt_contains_toc():
    def fake(prompt):
        _captured["prompt"] = prompt
        return GOOD
    draft_syllabus("mygoal", "probability", "THE_TOC", fake)
    assert "THE_TOC" in _captured["prompt"] and "mygoal" in _captured["prompt"]


def test_edit_until_valid_passes_through(tmp_path: Path):
    s = edit_until_valid(GOOD, tmp_path / "s.yaml", editor=lambda p: None)
    assert s.concepts[0].id == "a"


def test_edit_until_valid_retries_with_errors(tmp_path: Path):
    calls = []

    def editor(path: Path):
        calls.append(path.read_text())
        if len(calls) == 1:
            assert "ERRORS" not in calls[0]
        else:
            path.write_text(GOOD)  # user fixes it on round 2

    s = edit_until_valid(BAD, tmp_path / "s.yaml", editor=editor)
    assert len(calls) == 2 and "ghost" in calls[1] and "# ERRORS" in calls[1]
    assert s.concepts[0].id == "a"


def test_edit_gives_up_after_three(tmp_path: Path):
    with pytest.raises(SyllabusError):
        edit_until_valid(BAD, tmp_path / "s.yaml", editor=lambda p: None)
```

(Note: `test_draft_strips_fences` overlaps `test_draft_prompt_contains_toc`; keep the simpler assertion form — if the capture-helper indirection annoys, merge the two tests into one that asserts both fence-stripping and prompt content.)

- [ ] **Step 3: Run test to verify it fails**

Run: `uv run pytest tests/test_synthesis.py -v` — Expected: FAIL.

- [ ] **Step 4: Implement**

`src/seba/synthesis/__init__.py`: (empty file)

`src/seba/synthesis/synthesize.py`:
```python
import os
import re
import subprocess
from pathlib import Path
from typing import Callable

from seba.models import Syllabus
from seba.syllabus.graph import SyllabusError, load_syllabus

_PROMPT = Path(__file__).parent / "prompts" / "synthesis.md"


def draft_syllabus(goal: str, subject: str, toc: str,
                   complete: Callable[[str], str]) -> str:
    prompt = _PROMPT.read_text().format(goal=goal, subject=subject, toc=toc)
    out = complete(prompt)
    fenced = re.search(r"```(?:yaml)?\n(.*?)```", out, re.DOTALL)
    return fenced.group(1) if fenced else out


def default_editor(path: Path) -> None:
    subprocess.run([os.environ.get("EDITOR", "nano"), str(path)], check=True)


def edit_until_valid(yaml_text: str, path: Path,
                     editor: Callable[[Path], None]) -> Syllabus:
    path.write_text(yaml_text)
    last_error: SyllabusError | None = None
    for _ in range(3):
        editor(path)
        try:
            return load_syllabus(path)
        except SyllabusError as e:
            last_error = e
            body = "\n".join(l for l in path.read_text().splitlines()
                             if not l.startswith("# ERRORS") and not l.startswith("#   "))
            path.write_text(f"# ERRORS: fix and save again\n#   {e}\n{body}")
    raise last_error
```

- [ ] **Step 5: Run tests, expect PASS, commit**

```bash
uv run pytest tests/test_synthesis.py -v
git add -A && git commit -m "feat: syllabus synthesis with editor validation loop"
```

---

### Task 13: CLI + REPL — wiring it all

**Files:**
- Create: `src/seba/ui/__init__.py`, `src/seba/ui/repl.py`, `src/seba/cli.py`
- Modify: `pyproject.toml` (add `[project.scripts] tutor = "seba.cli:app"`)
- Test: `tests/test_cli.py` (wiring only; REPL itself is dogfood-tested)

**Interfaces:**
- Consumes: everything above.
- Produces: `seba` entry point with commands:
  - `tutor` (default) / `seba learn [GOAL]` — picker if no goal; briefing card; run session; apply record; save; receipt.
  - `seba new-goal NAME --subject SUBJECT --toc PATH` — profile check/draft, syllabus draft, editor loop, `store.create_goal`.
  - `seba status` — goals table.
  - `seba extract GOAL N` — recovery on `sessions/NNN.transcript.md`, apply + re-save.

- [ ] **Step 1: Write the failing test**

`tests/test_cli.py`:
```python
from typer.testing import CliRunner

from seba.cli import app

runner = CliRunner()


def test_status_empty(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBA_DATA_DIR", str(tmp_path))
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "no goals" in result.output.lower()


def test_new_goal_unknown_subject_without_profile_errors(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    toc = tmp_path / "toc.md"
    toc.write_text("# ch1")
    # no API key -> command must fail cleanly, not create a broken goal
    result = runner.invoke(app, ["new-goal", "prob", "--subject", "probability",
                                 "--toc", str(toc)])
    assert result.exit_code != 0
    assert not (tmp_path / "goals" / "prob").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py -v` — Expected: FAIL.

- [ ] **Step 3: Implement**

`src/seba/ui/__init__.py`: (empty file)

`src/seba/ui/repl.py`:
```python
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from seba.models import Agenda, SessionRecord

console = Console()


class TerminalIO:
    def get_input(self) -> str | None:
        try:
            text = console.input("[bold cyan]you>[/] ")
        except EOFError:
            return None
        return text or None

    def show_chunk(self, text: str) -> None:
        console.print(Markdown(text))

    def show(self, text: str) -> None:
        console.print(text)


def briefing_card(agenda: Agenda) -> None:
    teach = agenda.teach_concept.name if agenda.teach_concept else "review only"
    console.print(Panel(
        f"{agenda.goal} · session {agenda.session_number} · "
        f"{len(agenda.review_items)} due · today: {teach}\n\n{agenda.briefing}",
        title="tutor"))


def receipt(record: SessionRecord) -> None:
    graded = sum(1 for r in record.reviews if r.grade != "skipped")
    skipped = len(record.reviews) - graded
    parts = [f"{graded} reviewed"]
    if skipped:
        parts.append(f"{skipped} skipped")
    parts.append(f"{len(record.new_items)} minted")
    parts += [f"{c.id} → {c.status_change}" for c in record.concepts
              if c.status_change]
    status = "" if record.complete else "  [red]INCOMPLETE[/]"
    console.print("[dim]" + " · ".join(parts) + "[/]" + status)
```

`src/seba/cli.py`:
```python
from datetime import date, datetime, timezone
from pathlib import Path

import anthropic
import typer
import yaml

from seba import config
from seba.models import SubjectProfile
from seba.scheduler.agenda import build_agenda
from seba.scheduler.apply import apply_record
from seba.session.dialogue import make_send, run_session
from seba.session.loader import load_overlay, load_profile
from seba.session.recovery import recover_session
from seba.store.store import Store
from seba.synthesis.synthesize import default_editor, draft_syllabus, edit_until_valid
from seba.ui import repl

app = typer.Typer(no_args_is_help=False, invoke_without_command=True)


def _store() -> Store:
    return Store(config.data_dir())


def _profile(subject: str) -> SubjectProfile:
    p = load_profile(subject)
    if p is None:
        typer.echo(f"no subject profile '{subject}' — create "
                   f"{config.data_dir()}/subjects/{subject}/profile.yaml "
                   f"(copy from subjects/_templates/)", err=True)
        raise typer.Exit(1)
    return p


@app.callback()
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        learn(goal=None)


@app.command()
def learn(goal: str | None = typer.Argument(None)):
    store = _store()
    goals = store.list_goals()
    if not goals:
        typer.echo("no goals yet — run: seba new-goal NAME --subject S --toc PATH")
        raise typer.Exit(1)
    if goal is None:
        for i, g in enumerate(goals, 1):
            repl.console.print(
                f"[bold]{i}[/] {g.name} ({g.subject}) · "
                f"session {g.session_count + 1} · {g.due_count} due")
        goal = goals[int(repl.console.input("pick> ")) - 1].name

    state = store.load_goal(goal)
    profile = _profile(state.subject)
    agenda = build_agenda(state, profile, date.today(),
                          config.data_dir() / "sources")
    repl.briefing_card(agenda)

    client = anthropic.Anthropic()
    record, transcript = run_session(
        agenda, state.syllabus, load_overlay(state.subject),
        config.data_dir() / "sources", repl.TerminalIO(),
        make_send(client, config.model()))
    updated = apply_record(state, record, datetime.now(timezone.utc))
    store.save_session(goal, record, transcript, updated)
    repl.receipt(record)
    if not record.complete:
        typer.echo(f"run: seba extract {goal} {state.session_number}")


@app.command("new-goal")
def new_goal(name: str, subject: str = typer.Option(...),
             toc: Path = typer.Option(...)):
    store = _store()
    _profile(subject)  # must exist (v0: bundled or hand-copied from template)
    client = anthropic.Anthropic()

    def complete(prompt: str) -> str:
        msg = client.messages.create(model=config.recovery_model(),
                                     max_tokens=4000,
                                     messages=[{"role": "user", "content": prompt}])
        return "".join(b.text for b in msg.content if b.type == "text")

    draft = draft_syllabus(name, subject, toc.read_text(), complete)
    syllabus = edit_until_valid(draft, config.data_dir() / f"{name}-syllabus.yaml",
                                default_editor)
    store.create_goal(name, syllabus, subject)
    typer.echo(f"goal '{name}' created — start with: seba learn {name}")


@app.command()
def status():
    goals = _store().list_goals()
    if not goals:
        typer.echo("no goals yet")
        return
    for g in goals:
        done_msg = f"{g.session_count} sessions · {g.due_count} due today"
        repl.console.print(f"[bold]{g.name}[/] ({g.subject}) — {done_msg}")


@app.command()
def extract(goal: str, n: int):
    store = _store()
    state = store.load_goal(goal)
    tdir = store.data_dir / "goals" / goal / "sessions"
    transcript = (tdir / f"{n:03d}.transcript.md").read_text()
    profile = _profile(state.subject)
    agenda = build_agenda(state, profile, date.today(),
                          config.data_dir() / "sources")
    client = anthropic.Anthropic()
    record = recover_session(transcript, agenda, state.syllabus,
                             config.data_dir() / "sources",
                             make_send(client, config.recovery_model()))
    updated = apply_record(state, record, datetime.now(timezone.utc))
    store.save_session(goal, record, transcript, updated)
    repl.receipt(record)
```

Add to `pyproject.toml`:
```toml
[project.scripts]
tutor = "seba.cli:app"
```

- [ ] **Step 4: Run all tests, expect PASS, commit**

```bash
uv run pytest -v
git add -A && git commit -m "feat: CLI and REPL wiring"
```

Known v0 sharp edge (accepted): `extract` rebuilds the agenda from *current* state, which may differ from the crashed session's agenda if state moved on; acceptable because extract is meant to run immediately after a crash. Note it in README.

---

### Task 13b: End-to-end integration test — the continuity property

**Files:**
- Test: `tests/test_integration.py`

**Interfaces:**
- Consumes: `Store`, `build_agenda`, `run_session`, `apply_record`, plus the fake-message helpers pattern from `tests/test_dialogue.py`.
- Produces: nothing new — proves the whole loop: session N's outcomes shape session N+1's agenda.

- [ ] **Step 1: Write the failing test**

`tests/test_integration.py`:
```python
from datetime import date, datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from seba.models import Concept, Syllabus
from seba.scheduler.agenda import build_agenda
from seba.scheduler.apply import apply_record
from seba.session.dialogue import run_session
from seba.store.store import Store

NOW = datetime(2026, 7, 3, 12, tzinfo=timezone.utc)
TODAY = date(2026, 7, 3)


def text_block(t):
    return SimpleNamespace(type="text", text=t)


def tool_block(id, name, input):
    return SimpleNamespace(type="tool_use", id=id, name=name, input=input)


def msg(blocks, stop="end_turn"):
    return SimpleNamespace(content=blocks, stop_reason=stop)


class SilentIO:
    def get_input(self):
        return None

    def show_chunk(self, text):
        pass

    def show(self, text):
        pass


def scripted(script):
    calls = list(script)
    return lambda system, messages: calls.pop(0)


def run_one(store, profile, script, tmp_path):
    state = store.load_goal("prob")
    agenda = build_agenda(state, profile, TODAY, tmp_path / "sources")
    record, transcript = run_session(agenda, state.syllabus, "", tmp_path,
                                     SilentIO(), scripted(script))
    store.save_session("prob", record, transcript,
                       apply_record(state, record, NOW))
    return agenda, record


def test_session_two_reflects_session_one(tmp_path: Path):
    from seba.session.loader import load_profile
    store = Store(tmp_path / "data")
    store.create_goal("prob", Syllabus(goal="prob", subject="probability",
                                       concepts=[Concept(id="bayes", name="Bayes")]),
                      "probability")
    profile = load_profile("probability")

    # Session 1: teach bayes, note a misconception, mint one card, end.
    s1 = [msg([tool_block("t1", "update_concept",
                          {"id": "bayes", "status_change": "started",
                           "note": "confuses prior with likelihood"}),
               tool_block("t2", "mint_item",
                          {"concept": "bayes", "type": "recall",
                           "front": "State Bayes' theorem", "back": "..."}),
               tool_block("t3", "end_session",
                          {"summary": "Introduced Bayes.",
                           "next_session_hint": "drill the prior/likelihood split"})],
              stop="tool_use"),
          msg([text_block("Bye!")])]
    agenda1, _ = run_one(store, profile, s1, tmp_path)
    assert agenda1.review_items == []  # nothing due on day one

    # Session 2: the minted card is due (new FSRS cards are due immediately);
    # the briefing must carry the note and the hint.
    state2 = store.load_goal("prob")
    assert state2.session_number == 2
    agenda2 = build_agenda(state2, profile, TODAY, tmp_path / "sources")
    [review] = agenda2.review_items
    assert review.front == "State Bayes' theorem"
    assert "confuses prior with likelihood" in agenda2.briefing
    assert "drill the prior/likelihood split" in agenda2.briefing

    # Session 2 runs: grade it good → the card sleeps; agenda 3 has no reviews.
    s2 = [msg([tool_block("t1", "grade_review",
                          {"id": review.id, "grade": "good"}),
               tool_block("t2", "end_session",
                          {"summary": "Drilled.", "next_session_hint": "advance"})],
              stop="tool_use"),
          msg([text_block("Bye!")])]
    run_one(store, profile, s2, tmp_path)
    state3 = store.load_goal("prob")
    agenda3 = build_agenda(state3, profile, TODAY, tmp_path / "sources")
    assert agenda3.review_items == []  # graded good → due in the future
    assert state3.recent_grades == ["good"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_integration.py -v` — Expected: FAIL until T4/T6/T9/T11 all merged (this is the point — it is the wave-7 wiring check).

- [ ] **Step 3: Make it pass** — no new production code should be needed; failures here mean a wiring bug in an earlier task. Fix in the task that owns the broken piece, not with shims here.

- [ ] **Step 4: Run all tests, expect PASS, commit**

```bash
uv run pytest -v
git add -A && git commit -m "test: end-to-end continuity integration test"
```

---

### Task 14: Dogfood gate (manual)

**Files:**
- Create: `README.md` (usage: env vars, new-goal, learn, status, extract; the extract sharp edge above)

- [ ] **Step 1: Write README.md** opening with the etymology note (*seba*, Egyptian *sbꜣ* "to teach" — root of *sbꜣyt*, the instruction genre; the glyph 𓇼 also writes "star" and "door"), then install (`uv sync`), `ANTHROPIC_API_KEY` requirement, the four commands with examples, data-dir layout summary, and the extract caveat.
- [ ] **Step 2: Create both real goals** — `seba new-goal probability --subject probability --toc <real ToC file>` and `seba new-goal italian --subject italian --toc <a course outline>`. Review both syllabi in the editor for real.
- [ ] **Step 3: Run 3 real sessions per goal across ≥3 distinct days.** After each, check: `data/` git log has one commit per session; `NNN.outcomes.yaml` grades match what actually happened in the dialogue; next session's briefing surfaces the shaky concepts and due items correctly.
- [ ] **Step 4: Success criteria (spec §9.5):** session N+1's briefing correctly reflects session N — shaky concepts resurface, mastered items sleep, frontier advances. Log failures as issues; prompt fixes are file edits, no code.
- [ ] **Step 5: Commit README**

```bash
git add README.md && git commit -m "docs: usage README"
```

---

## Self-review (done at plan time)

- **Spec coverage:** models ✅(T2) · store ✅(T4) · scheduler items/agenda/context-budget ✅(T5,T6) · syllabus ✅(T3) · outcome tools + gates ✅(T7) · prompts/profiles data-driven ✅(T8) · dialogue ✅(T9) · recovery ✅(T10) · record→state ✅(T11) · synthesis+editor loop ✅(T12) · CLI/REPL/receipt ✅(T13) · dogfood ✅(T14). Save-time invariants (spec §M4 gates) are covered jointly by T7 (exactly-one `end_session`, grades map to agenda) and T11 (legal status edges, corrupt-proof apply). Deferred to v1 per spec: drill mode, agentic synthesis, `seba gc`, ladder, streaming display, TUI.
- **Type consistency:** `Send` shape shared by T9/T10; `SessionRecord` produced by T7, consumed by T4/T11/T13; `resolve_excerpt` defined T6, reused T7. Names checked.
- **Parallelization:** see the Orchestrator briefing DAG at the top — T6 depends on T4 (`store.parse_notes`) and T7 on T6 (`agenda.resolve_excerpt`), so the waves are narrower than three fully independent tracks.
