# Scheduling Controls Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make py-fsrs the only thing that decides when a card comes back, and give the learner per-goal settings, per-concept emphasis and `seba tune` to steer it.

**Architecture:** Seba stops layering rules on the scheduler (no learning steps, no `hard` pull-in, no automatic reopen) and instead builds the py-fsrs `Scheduler` per review from the goal's settings and the concept's emphasis. Settings live in `goal.yaml`; everything else the tutor needs (slipped cards, `hard` notes, pass counts) is derived from the session outcome files at load, as today. The briefing carries what happened; the learner decides what changes.

**Tech Stack:** Python 3.12, py-fsrs 6.3.1, pydantic v2, typer, PyYAML, pytest, ruff, ty, uv.

**Spec:** `specs/2026-09-27-scheduling-controls-design.md`, with `specs/2026-09-27-scheduling-controls-plan-notes.md`, `docs/adr/0001-scheduler-owns-the-schedule.md` and `CONTEXT.md` (all on branch `docs/scheduling-syllabus-specs`).

## Global Constraints

- py-fsrs decides when a card comes back and Seba never changes that by itself. Do not add leech detection, damping of `easy`, automatic reopening of concepts, or automatic tuning from grades.
- The one direct override of a due date is setting a concept's emphasis to `more`, which makes its cards due now.
- Setting ranges and defaults: `desired_retention` 0.9 (0.70–0.97); `max_interval_days` 180 (≥ 1); `concepts_per_session` 1 (1–5); `completion_passes` 1 (≥ 1).
- Emphasis offsets: `more` is +0.05, `less` is −0.10, result clamped to 0.70–0.97. Normal is the absence of an entry.
- Scheduler is built with `learning_steps=()` and `relearning_steps=()`. Fuzzing stays on in production.
- Settings take effect at each card's next review. Stored due dates are not rewritten, except by emphasis `more`.
- No data migration. Session outcome files and a pending session written before this change must still load.
- Use the terms in `CONTEXT.md` exactly: goal, direction, concept, source, card, hard, mapping, emphasis, gap, dropped. `hard` is a pass.
- Python typing: never annotate as `Any` or `object`, and never add `# type: ignore` to a line that can be typed properly.
- The gate is `make check` (ruff, `ruff format --check`, `ty check src`, pytest). It must pass at the end of every task. Baseline on `origin/main`: 105 passed.
- Match the surrounding code: its comment density, naming and test style. No new dependencies.
- Commits use Conventional Commits and end with the trailer `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.

## Review Focus

Inputs the spec is silent on. Each has a test in the task that owns the code.

1. `goal.yaml` hand-edited to an out-of-range or non-numeric setting → a clean error naming the file, never a traceback (Task 2).
2. Emphasis naming a concept that does not exist → `tune` refuses it (Task 8); an entry already in `goal.yaml` is ignored at load (Task 2).
3. A stored card in the Learning state with a step set, reviewed by a scheduler with no learning steps → graduates without error (Task 3).
4. A stored card already due past the ceiling → left alone until its next review, capped from then on (Task 3).
5. A note that is only whitespace → refused; a note with quotes, newlines or non-ASCII text → survives the round trip into the briefing (Task 4).

## File Structure

| File | Responsibility after this plan |
|---|---|
| `src/seba/models.py` | `Emphasis`, `GoalSettings`, `GoalMeta`; `GoalState` derived fields; `Agenda.next_concepts`; `reopened` |
| `src/seba/scheduler/items.py` | target retention; scheduler built per review; due-now stamp |
| `src/seba/scheduler/apply.py` | applies a session record; no reopen logic |
| `src/seba/scheduler/agenda.py` | briefing lines; up to N concepts |
| `src/seba/store/store.py` | `goal.yaml` read/write; derived state from outcomes |
| `src/seba/session/tools.py` | note required; `reopened`; pass-count gate |
| `src/seba/cli.py` | `tune`; clean load errors; `--status reopened` |
| `skills/seba-tutor/SKILL.md`, `docs/development.md` | what the tutor is told |

No new source files. Tests go in the existing `tests/test_*.py` file for each module.

---

### Task 1: Remove the stray lines from the analytic template profile

**Files:**
- Modify: `subjects/_templates/analytic/profile.yaml`
- Test: `tests/test_loader.py`

**Interfaces:**
- Consumes: nothing.
- Produces: nothing later tasks rely on.

The file ends with two lines that are not YAML, `</content>` and `</invoke>`, left by a tool. They make the template unparseable.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_loader.py` (keep its existing imports and tests):

```python
from pathlib import Path

import pytest
import yaml

from seba.models import SubjectProfile

SUBJECTS = Path(__file__).parents[1] / "subjects"


@pytest.mark.parametrize(
    "path", sorted(SUBJECTS.rglob("profile.yaml")), ids=lambda p: p.parent.name
)
def test_every_shipped_profile_parses(path):
    SubjectProfile.model_validate(yaml.safe_load(path.read_text()))
```

- [ ] **Step 2: Run it and see it fail**

Run: `uv run pytest tests/test_loader.py -q`
Expected: the `analytic` case FAILS with a YAML error; the other profiles pass.

- [ ] **Step 3: Delete the two stray lines**

The file must be exactly:

```yaml
name: TEMPLATE
kind: analytic
max_reviews_per_session: 10
item_types: [recall, apply, produce]
session_shape: teach-heavy
```

- [ ] **Step 4: Run `make check`**

Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add subjects/_templates/analytic/profile.yaml tests/test_loader.py
git commit -m "fix(subjects): remove stray lines from the analytic template profile"
```

---

### Task 2: Settings and emphasis — models, load, save

**Files:**
- Modify: `src/seba/models.py`, `src/seba/store/store.py`, `src/seba/cli.py`
- Test: `tests/test_models.py`, `tests/test_store.py`, `tests/test_session_cli.py`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `seba.models.RETENTION_MIN = 0.70`, `seba.models.RETENTION_MAX = 0.97`
  - `seba.models.Emphasis` (`StrEnum`: `LESS = "less"`, `MORE = "more"`)
  - `seba.models.GoalSettings` (fields below)
  - `seba.models.GoalMeta` (the shape of `goal.yaml`)
  - `GoalState.settings: GoalSettings`, `GoalState.emphasis: dict[str, Emphasis]`
  - `Store.save_tuning(name: str, settings: GoalSettings, emphasis: dict[str, Emphasis], items: list[Item]) -> bool` — `True` if it committed
  - `seba.cli._load_goal(store: Store, goal: str) -> GoalState` — exits 1 with the message on `StoreError`

- [ ] **Step 1: Write the failing model tests**

Add to `tests/test_models.py`:

```python
import pytest
from pydantic import ValidationError

from seba.models import GoalSettings


def test_goal_settings_defaults():
    s = GoalSettings()
    assert (
        s.desired_retention,
        s.max_interval_days,
        s.concepts_per_session,
        s.completion_passes,
    ) == (0.9, 180, 1, 1)


@pytest.mark.parametrize(
    "field,value",
    [
        ("desired_retention", 0.69),
        ("desired_retention", 0.98),
        ("max_interval_days", 0),
        ("concepts_per_session", 0),
        ("concepts_per_session", 6),
        ("completion_passes", 0),
    ],
)
def test_goal_settings_refuses_out_of_range(field, value):
    with pytest.raises(ValidationError):
        GoalSettings.model_validate({field: value})
```

- [ ] **Step 2: Run them and see them fail**

Run: `uv run pytest tests/test_models.py -q`
Expected: FAIL, `cannot import name 'GoalSettings'`.

- [ ] **Step 3: Add the models**

In `src/seba/models.py`, import `ConfigDict` from pydantic, and add after `PaceHint`:

```python
RETENTION_MIN = 0.70
RETENTION_MAX = 0.97


class Emphasis(StrEnum):
    LESS = "less"
    MORE = "more"  # normal is the absence of an entry


class GoalSettings(BaseModel):
    desired_retention: float = Field(0.9, ge=RETENTION_MIN, le=RETENTION_MAX)
    max_interval_days: int = Field(180, ge=1)
    concepts_per_session: int = Field(1, ge=1, le=5)
    completion_passes: int = Field(1, ge=1)


class GoalMeta(BaseModel):
    """goal.yaml. Unknown keys are kept so a hand-edited file survives a rewrite."""

    model_config = ConfigDict(extra="allow")

    name: str
    subject: str
    settings: GoalSettings = Field(default_factory=GoalSettings)
    emphasis: dict[str, Emphasis] = Field(default_factory=dict)
```

Add to `GoalState`, after `notes`:

```python
    settings: GoalSettings = Field(default_factory=GoalSettings)
    emphasis: dict[str, Emphasis] = Field(default_factory=dict)
```

- [ ] **Step 4: Run the model tests and see them pass**

Run: `uv run pytest tests/test_models.py -q`
Expected: PASS.

- [ ] **Step 5: Write the failing store tests**

Add to `tests/test_store.py` (add `Emphasis`, `GoalSettings` to the `seba.models` import):

```python
def _goal_yaml(store):
    return store.data_dir / "goals" / "prob" / "goal.yaml"


def _commits(store):
    return subprocess.run(
        ["git", "log", "--oneline"], cwd=store.data_dir, capture_output=True, text=True
    ).stdout.splitlines()


def test_goal_without_a_settings_block_loads_defaults(store):
    store.create_goal("prob", syl(), "probability")
    gs = store.load_goal("prob")
    assert gs.settings == GoalSettings() and gs.emphasis == {}


def test_save_tuning_roundtrip(store):
    store.create_goal("prob", syl(), "probability")
    settings = GoalSettings(desired_retention=0.85, max_interval_days=120)
    assert store.save_tuning("prob", settings, {"bayes": Emphasis.MORE}, [item()])
    gs = store.load_goal("prob")
    assert gs.settings == settings
    assert gs.emphasis == {"bayes": "more"}
    assert gs.items[0].id == "it-1" and gs.subject == "probability"
    assert "prob: tuned" in _commits(store)[0]


def test_save_tuning_does_not_commit_when_nothing_changed(store):
    store.create_goal("prob", syl(), "probability")
    settings = GoalSettings(desired_retention=0.85)
    assert store.save_tuning("prob", settings, {}, [])
    before = _commits(store)
    assert store.save_tuning("prob", settings, {}, []) is False
    assert _commits(store) == before


def test_save_tuning_keeps_unknown_keys(store):
    store.create_goal("prob", syl(), "probability")
    path = _goal_yaml(store)
    path.write_text(path.read_text() + "colour: teal\n")
    store.save_tuning("prob", GoalSettings(), {}, [])
    assert yaml.safe_load(path.read_text())["colour"] == "teal"


@pytest.mark.parametrize(
    "block",
    [
        "settings:\n  desired_retention: 2.0\n",
        "settings:\n  desired_retention: banana\n",
        "settings:\n  max_interval_days: 0\n",
        "settings: nonsense\n",
        "emphasis:\n  bayes: lots\n",
    ],
)
def test_malformed_goal_yaml_names_the_file(store, block):
    store.create_goal("prob", syl(), "probability")
    path = _goal_yaml(store)
    path.write_text(path.read_text() + block)
    with pytest.raises(StoreError, match="goal.yaml"):
        store.load_goal("prob")


def test_emphasis_on_an_unknown_concept_is_ignored_at_load(store):
    store.create_goal("prob", syl(), "probability")
    path = _goal_yaml(store)
    path.write_text(path.read_text() + "emphasis:\n  ghost: more\n  bayes: less\n")
    assert store.load_goal("prob").emphasis == {"bayes": "less"}
```

- [ ] **Step 6: Run them and see them fail**

Run: `uv run pytest tests/test_store.py -q`
Expected: the new tests FAIL (`save_tuning` missing; no `StoreError` raised).

- [ ] **Step 7: Implement load and save in `src/seba/store/store.py`**

Import `Emphasis`, `GoalMeta`, `GoalSettings` from `seba.models`. Add to `Store`:

```python
    def _load_meta(self, path: Path) -> GoalMeta:
        try:
            return GoalMeta.model_validate(yaml.safe_load(path.read_text()))
        except (yaml.YAMLError, ValidationError) as e:
            raise StoreError(f"{path.name}: {e}") from e

    def _write_items(self, gdir: Path, items: list[Item]) -> None:
        tmp = gdir / "items.jsonl.tmp"
        tmp.write_text(
            "".join(json.dumps(i.model_dump(mode="json")) + "\n" for i in items)
        )
        tmp.rename(gdir / "items.jsonl")

    def save_tuning(
        self,
        name: str,
        settings: GoalSettings,
        emphasis: dict[str, Emphasis],
        items: list[Item],
    ) -> bool:
        """Write settings, emphasis and cards. Commits only if something changed:
        `_git` runs with check=True and an empty commit fails."""
        gdir = self._goal_dir(name)
        path = gdir / "goal.yaml"
        meta = self._load_meta(path).model_copy(
            update={"settings": settings, "emphasis": emphasis}
        )
        path.write_text(yaml.safe_dump(meta.model_dump(mode="json"), sort_keys=False))
        self._write_items(gdir, items)
        self._git("add", f"goals/{name}/goal.yaml", f"goals/{name}/items.jsonl")
        staged = subprocess.run(
            ["git", "diff", "--cached", "--quiet"], cwd=self.data_dir
        )
        if staged.returncode == 0:
            return False
        self._git("commit", "-m", f"{name}: tuned")
        return True
```

In `save_session`, replace the inline `items.jsonl.tmp` block with `self._write_items(gdir, updated.items)`.

In `load_goal`, replace the `yaml.safe_load` of `goal.yaml` with `meta = self._load_meta(gdir / "goal.yaml")` (keep `load_syllabus` inside the existing `try` for `SyllabusError`), use `meta.subject` where `meta["subject"]` was, and pass to `GoalState`:

```python
            settings=meta.settings,
            emphasis={
                cid: e
                for cid, e in meta.emphasis.items()
                if cid in {c.id for c in syllabus.concepts}
            },
```

- [ ] **Step 8: Run the store tests and see them pass**

Run: `uv run pytest tests/test_store.py -q`
Expected: PASS.

- [ ] **Step 9: Write the failing CLI test**

Add to `tests/test_session_cli.py`. Follow `test_malformed_pending_fails_cleanly` in the same file for how it asserts on output and exit code.

```python
def test_malformed_goal_yaml_fails_cleanly(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    seed(data)
    path = data / "goals" / "prob" / "goal.yaml"
    path.write_text(path.read_text() + "settings:\n  desired_retention: banana\n")
    for cmd in (["start", "prob"], ["view", "prob", "--json"], ["status"]):
        result = runner.invoke(app, cmd)
        assert result.exit_code == 1, cmd
        assert "goal.yaml" in result.output
        assert "Traceback" not in result.output
        assert result.exception is None or isinstance(result.exception, SystemExit)
```

- [ ] **Step 10: Run it and see it fail**

Run: `uv run pytest tests/test_session_cli.py::test_malformed_goal_yaml_fails_cleanly -q`
Expected: FAIL, the exception is a `StoreError`.

- [ ] **Step 11: Catch `StoreError` in `src/seba/cli.py`**

Import `GoalState` from `seba.models` and `StoreError` from `seba.store.store`. Add:

```python
def _load_goal(store: Store, goal: str) -> GoalState:
    """load_goal, but turn a StoreError into a clean stderr + exit 1."""
    try:
        return store.load_goal(goal)
    except StoreError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
```

Replace every `store.load_goal(goal)` in `cli.py` (`_session`, `_finish`, `start`, `view`) with `_load_goal(store, goal)`. In `status`, wrap `_store().list_goals()` in the same `try`/`except StoreError`.

- [ ] **Step 12: Run `make check`**

Expected: all pass.

- [ ] **Step 13: Commit**

```bash
git add src/seba/models.py src/seba/store/store.py src/seba/cli.py tests/
git commit -m "feat(settings): per-goal settings and per-concept emphasis in goal.yaml"
```

---

### Task 3: Scheduler built from settings and emphasis

**Files:**
- Modify: `src/seba/scheduler/items.py`, `src/seba/scheduler/apply.py`
- Test: `tests/test_scheduler_items.py`, `tests/test_apply.py`

**Interfaces:**
- Consumes: `GoalSettings`, `Emphasis`, `RETENTION_MIN`, `RETENTION_MAX`, `GoalState.settings`, `GoalState.emphasis` (Task 2).
- Produces:
  - `seba.scheduler.items.target_retention(settings: GoalSettings, emphasis: Emphasis | None) -> float`
  - `seba.scheduler.items.apply_review(item: Item, grade: Grade, now: datetime, settings: GoalSettings, emphasis: Emphasis | None) -> Item` — `settings` and `emphasis` are required, no defaults
  - `apply_record(state, record, now)` keeps its signature and reads settings and emphasis from `state`

Facts about py-fsrs 6.3.1, measured: with `learning_steps=()` a `hard` on a new card is due in 1 day and the card goes straight to the Review state; a stored card in Learning or Relearning with `step: 0` moves to Review at its next review without error; `maximum_interval` is applied after fuzzing, so the ceiling can be asserted exactly. py-fsrs does `from random import random` in `fsrs/scheduler.py`, so a test pins the fuzz by patching `fsrs.scheduler.random`, not `random.random`. With fuzz left random, the struggler history below is not strictly growing for about 1 seed in 8.

- [ ] **Step 1: Write the failing tests**

In `tests/test_scheduler_items.py`, change the imports to:

```python
from datetime import date, datetime, timedelta, timezone

import pytest
from fsrs import Card, Rating, Scheduler, State

from seba.models import Emphasis, GoalSettings, Item, MintItem
from seba.scheduler.items import apply_review, due_items, mint_item, target_retention

NOW = datetime(2026, 7, 3, tzinfo=timezone.utc)
DEFAULTS = GoalSettings()
```

Update the four existing calls to `apply_review(...)` to pass `DEFAULTS, None` as the last two arguments. Then add:

```python
def new_card():
    return mint_item(
        MintItem(concept="c", type="recall", front="f", back="b"), date(2026, 7, 3)
    )


def days(item, since):
    return (datetime.fromisoformat(item.fsrs["due"]) - since).days


@pytest.fixture
def no_fuzz(monkeypatch):
    # The midpoint of the fuzz range, so intervals are deterministic.
    monkeypatch.setattr("fsrs.scheduler.random", lambda: 0.5)


@pytest.mark.parametrize(
    "settings,emphasis,expected",
    [
        (GoalSettings(), None, 0.90),
        (GoalSettings(), Emphasis.MORE, 0.95),
        (GoalSettings(), Emphasis.LESS, 0.80),
        (GoalSettings(desired_retention=0.95), Emphasis.MORE, 0.97),
        (GoalSettings(desired_retention=0.75), Emphasis.LESS, 0.70),
    ],
)
def test_target_retention(settings, emphasis, expected):
    assert target_retention(settings, emphasis) == pytest.approx(expected)


def test_hard_on_a_new_card_yields_at_least_a_day():
    graded = apply_review(new_card(), "hard", NOW, DEFAULTS, None)
    assert days(graded, NOW) >= 1
    assert graded.fsrs["state"] == State.Review


def test_struggler_history_grows(no_fuzz):
    # The history that kept one card at zero days for five sessions.
    item, now, intervals = new_card(), NOW, []
    for grade in ["again", "hard", "hard", "hard", "hard", "good", "easy"]:
        item = apply_review(item, grade, now, DEFAULTS, None)
        intervals.append(days(item, now))
        # sessions are three days apart; a card is never reviewed before it is due
        now = max(datetime.fromisoformat(item.fsrs["due"]), now + timedelta(days=3))
    assert intervals[0] >= 1
    assert intervals == sorted(set(intervals))  # strictly growing


def test_no_interval_exceeds_the_ceiling():
    settings = GoalSettings(max_interval_days=30)
    item, now, intervals = new_card(), NOW, []
    for _ in range(8):
        item = apply_review(item, "easy", now, settings, None)
        intervals.append(days(item, now))
        now = datetime.fromisoformat(item.fsrs["due"])
    # Fuzz is on and may land a day or two under the ceiling, never over it.
    assert max(intervals) <= 30
    assert intervals[-1] >= 25  # the ceiling is what is binding by now


def test_emphasis_shifts_the_interval(no_fuzz):
    def after_three_goods(emphasis):
        item, now = new_card(), NOW
        for _ in range(3):
            item = apply_review(item, "good", now, DEFAULTS, emphasis)
            last = days(item, now)
            now = datetime.fromisoformat(item.fsrs["due"])
        return last

    more, normal, less = (
        after_three_goods(e) for e in (Emphasis.MORE, None, Emphasis.LESS)
    )
    assert more < normal < less


@pytest.mark.parametrize("grade", ["again", "hard", "good", "easy"])
def test_a_stored_learning_card_graduates(grade):
    # Existing goals hold cards in Learning with a step set, written by a
    # scheduler that had learning steps.
    card, _ = Scheduler().review_card(Card(), Rating.Hard, review_datetime=NOW)
    assert card.state == State.Learning and card.step == 0
    item = new_card().model_copy(update={"fsrs": dict(card.to_dict())})
    later = NOW + timedelta(days=3)
    graded = apply_review(item, grade, later, DEFAULTS, None)
    assert graded.fsrs["state"] == State.Review and graded.fsrs["step"] is None
    assert days(graded, later) >= 1


def test_a_card_due_past_the_ceiling_is_capped_at_its_next_review():
    due = NOW + timedelta(days=400)
    fsrs = dict(Card().to_dict())
    fsrs.update(
        state=State.Review.value,
        step=None,
        stability=400.0,
        difficulty=5.0,
        due=due.isoformat(),
        last_review=NOW.isoformat(),
    )
    item = new_card().model_copy(update={"fsrs": fsrs})
    graded = apply_review(item, "good", due, DEFAULTS, None)
    assert days(graded, due) <= 180
```

Add to `tests/test_apply.py` (add `Emphasis`, `GoalSettings` to the `seba.models` import and `from datetime import timedelta`):

```python
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
```

- [ ] **Step 2: Run them and see them fail**

Run: `uv run pytest tests/test_scheduler_items.py tests/test_apply.py -q`
Expected: FAIL, `cannot import name 'target_retention'`.

- [ ] **Step 3: Implement in `src/seba/scheduler/items.py`**

Delete the module-level `_scheduler = Scheduler()`. Import `Emphasis`, `GoalSettings`, `RETENTION_MAX`, `RETENTION_MIN` from `seba.models`. Add:

```python
_SHIFT = {Emphasis.MORE: 0.05, Emphasis.LESS: -0.10}


def target_retention(settings: GoalSettings, emphasis: Emphasis | None) -> float:
    shift = _SHIFT[emphasis] if emphasis is not None else 0.0
    return min(RETENTION_MAX, max(RETENTION_MIN, settings.desired_retention + shift))


def apply_review(
    item: Item,
    grade: Grade,
    now: datetime,
    settings: GoalSettings,
    emphasis: Emphasis | None,
) -> Item:
    if grade == "skipped":
        return item
    # No learning or relearning steps: those are minutes, for re-showing a card
    # in the same sitting, and sessions are days apart. Every grade then yields
    # at least a day and `hard` grows the interval.
    scheduler = Scheduler(
        desired_retention=target_retention(settings, emphasis),
        learning_steps=(),
        relearning_steps=(),
        maximum_interval=settings.max_interval_days,
    )
    card, _ = scheduler.review_card(
        Card.from_dict(cast(CardDict, item.fsrs)), _RATING[grade], review_datetime=now
    )
    return item.model_copy(update={"fsrs": dict(card.to_dict())})
```

- [ ] **Step 4: Pass settings and emphasis from `apply_record`**

In `src/seba/scheduler/apply.py`, the items comprehension becomes:

```python
    items = [
        apply_review(
            i, grades[i.id], now, state.settings, state.emphasis.get(i.concept)
        )
        if i.id in grades
        else i
        for i in state.items
    ]
```

- [ ] **Step 5: Run `make check`**

Expected: all pass. `test_again_due_within_a_day` still passes: `again` is now due in exactly one day.

- [ ] **Step 6: Commit**

```bash
git add src/seba/scheduler/ tests/test_scheduler_items.py tests/test_apply.py
git commit -m "feat(scheduler): build the scheduler from settings and emphasis, without learning steps"
```

---

### Task 4: Notes on `hard` and `again`, `again`-only error sites, briefing lines

**Files:**
- Modify: `src/seba/models.py`, `src/seba/store/store.py`, `src/seba/session/tools.py`, `src/seba/scheduler/agenda.py`
- Test: `tests/test_tools.py`, `tests/test_store.py`, `tests/test_agenda.py`, `tests/test_session_cli.py`

**Interfaces:**
- Consumes: `GoalState.emphasis` (Task 2).
- Produces:
  - `GoalState.again_runs: dict[str, int]` — per card id, the trailing run of `again` over its reviews, ignoring `skipped`. Cards whose run is zero are absent.
  - `GoalState.last_trouble: list[GradeReview]` — the last session's `again` and `hard` reviews, in order, notes included.
  - `GoalState.last_session_errors: set[str]` — kept, now concepts graded `again` in the last session only.
  - `GoalState.recent_by_item` is left in place. Task 5 removes it.
  - Briefing lines beginning `slipped:`, `hard:` and `emphasis:`.

- [ ] **Step 1: Write the failing handler tests**

In `tests/test_tools.py`, change `test_missing_grades` so its `again` carries a note (`{"id": "it-1", "grade": "again", "note": "blanked"}`), and add:

```python
import pytest  # already imported


@pytest.mark.parametrize("grade", ["hard", "again"])
@pytest.mark.parametrize("note", [None, "", "   ", "\n\t"])
def test_hard_and_again_need_a_note(handler, grade, note):
    text, err = handler.handle(
        "grade_review", {"id": "it-1", "grade": grade, "note": note}
    )
    assert err and "--note" in text
    assert not handler.record.reviews


@pytest.mark.parametrize("grade", ["hard", "again"])
def test_hard_and_again_record_with_a_note(handler, grade):
    _, err = handler.handle(
        "grade_review", {"id": "it-1", "grade": grade, "note": "needed the formula"}
    )
    assert not err and handler.record.reviews[0].note == "needed the formula"


@pytest.mark.parametrize("grade", ["good", "easy", "skipped"])
def test_other_grades_need_no_note(handler, grade):
    _, err = handler.handle("grade_review", {"id": "it-1", "grade": grade})
    assert not err
```

- [ ] **Step 2: Run them and see them fail**

Run: `uv run pytest tests/test_tools.py -q`
Expected: `test_hard_and_again_need_a_note` FAILS.

- [ ] **Step 3: Require the note in `ToolHandler._grade_review`**

In `src/seba/session/tools.py`, import `Grade`, and add before `self.record.reviews.append(call)`:

```python
        if call.grade in (Grade.AGAIN, Grade.HARD) and not (call.note or "").strip():
            # Enforced here, not on GradeReview: the model also parses old
            # session outcomes, which have no notes.
            what = (
                "what went wrong"
                if call.grade == Grade.AGAIN
                else "what the help was for"
            )
            return f"grading '{call.grade}' requires --note saying {what}", True
```

In `src/seba/models.py`, replace the rubric in the `GradeReview` docstring with:

```python
    """Grade a review item right after its exchange resolves.

    Rubric: wrong or no recall -> again; correct, but only with
    significant help -> hard (a pass); correct and unaided -> good;
    instant and confident -> easy; never reached this session -> skipped.
    `again` and `hard` need a note: what went wrong, or what the help was for."""
```

- [ ] **Step 4: Run the handler tests and see them pass**

Run: `uv run pytest tests/test_tools.py -q`
Expected: PASS.

- [ ] **Step 5: Write the failing store tests**

In `tests/test_store.py`, add:

```python
def _save(store, gs, *reviews):
    store.save_session(
        "prob", SessionRecord(reviews=list(reviews), complete=True), "t", gs
    )


def test_hard_is_not_an_error_site(store):
    store.create_goal("prob", syl(), "probability")
    gs = store.load_goal("prob").model_copy(update={"items": [item()]})
    _save(store, gs, GradeReview(id="it-1", grade="hard", note="needed the formula"))
    gs2 = store.load_goal("prob")
    assert gs2.last_session_errors == set()
    assert gs2.last_trouble == [
        GradeReview(id="it-1", grade="hard", note="needed the formula")
    ]
    assert gs2.again_runs == {}


def test_again_runs_count_the_trailing_run(store):
    store.create_goal("prob", syl(), "probability")
    gs = store.load_goal("prob").model_copy(update={"items": [item()]})
    _save(store, gs, GradeReview(id="it-1", grade="again", note="blanked"))
    assert store.load_goal("prob").again_runs == {"it-1": 1}
    _save(store, gs, GradeReview(id="it-1", grade="skipped"))  # ignored
    _save(store, gs, GradeReview(id="it-1", grade="again", note="blanked again"))
    gs3 = store.load_goal("prob")
    assert gs3.again_runs == {"it-1": 2}
    assert [r.note for r in gs3.last_trouble] == ["blanked again"]
    assert gs3.last_session_errors == {"bayes"}
    _save(store, gs, GradeReview(id="it-1", grade="hard", note="one hint"))
    assert store.load_goal("prob").again_runs == {}  # a pass resets it


def test_last_trouble_is_the_last_session_only(store):
    store.create_goal("prob", syl(), "probability")
    gs = store.load_goal("prob").model_copy(update={"items": [item()]})
    _save(store, gs, GradeReview(id="it-1", grade="again", note="blanked"))
    _save(store, gs, GradeReview(id="it-1", grade="good"))
    assert store.load_goal("prob").last_trouble == []


def test_old_outcomes_without_notes_still_load(store):
    store.create_goal("prob", syl(), "probability")
    gs = store.load_goal("prob").model_copy(update={"items": [item()]})
    _save(store, gs, GradeReview(id="it-1", grade="again"))  # as written before
    gs2 = store.load_goal("prob")
    assert gs2.last_trouble[0].note is None and gs2.again_runs == {"it-1": 1}
```

- [ ] **Step 6: Run them and see them fail**

Run: `uv run pytest tests/test_store.py -q`
Expected: the new tests FAIL (`again_runs` is not a field).

- [ ] **Step 7: Derive the fields in `Store.load_goal`**

In `src/seba/models.py`, change the comment on `last_session_errors` and add the two fields to `GoalState`:

```python
    # Concepts with a card graded `again` in the most recent session only —
    # Rosenshine's "review where errors were made last time". `hard` is a pass
    # and pulls nothing in.
    last_session_errors: set[str] = Field(default_factory=set)
    # Per card, how many of its most recent reviews in a row were `again`.
    again_runs: dict[str, int] = Field(default_factory=dict)
    # The last session's `again` and `hard` reviews, with their notes.
    last_trouble: list[GradeReview] = Field(default_factory=list)
```

`GradeReview` is defined above `GoalState` in the file, so no forward reference is needed.

In `load_goal`, beside the other accumulators add `again_runs: dict[str, int] = {}` and `last_trouble: list[GradeReview] = []`. In the `if last:` block also reset `last_trouble = []`. At the top of the `for r in rec.reviews:` loop add:

```python
                if r.grade == Grade.AGAIN:
                    again_runs[r.id] = again_runs.get(r.id, 0) + 1
                elif r.grade != Grade.SKIPPED:
                    again_runs.pop(r.id, None)
                if last and r.grade in (Grade.AGAIN, Grade.HARD):
                    last_trouble.append(r)
```

Change the error-site branch from `r.grade in (Grade.AGAIN, Grade.HARD)` to `r.grade == Grade.AGAIN`. Pass `again_runs=again_runs, last_trouble=last_trouble` to `GoalState`. Leave `recent_by_item` as it is.

Update `test_last_session_date_and_error_sites` only if it fails; it grades `again` and should pass unchanged.

- [ ] **Step 8: Run the store tests and see them pass**

Run: `uv run pytest tests/test_store.py -q`
Expected: PASS.

- [ ] **Step 9: Write the failing agenda tests**

In `tests/test_agenda.py`, add `Emphasis`, `GradeReview` to the `seba.models` import, and add:

```python
def trouble_state(**kw):
    return state(
        [Concept(id="a", name="A", status="done"), Concept(id="b", name="B")],
        [item("it-a", concept="a", due="2099-01-01T00:00:00+00:00")],
        **kw,
    )


def test_slipped_line_carries_the_run_and_the_note(tmp_path):
    s = trouble_state(
        last_trouble=[GradeReview(id="it-a", grade="again", note="mixed up e and x⁻¹")],
        again_runs={"it-a": 2},
    )
    briefing = build_agenda(s, profile(), TODAY, tmp_path).briefing
    assert (
        'slipped: [a] it-a, 2 sessions running — "mixed up e and x⁻¹". '
        "Propose re-teaching if the repair doesn't hold." in briefing
    )


def test_slipped_line_for_a_first_slip_without_a_note(tmp_path):
    s = trouble_state(
        last_trouble=[GradeReview(id="it-a", grade="again")], again_runs={"it-a": 1}
    )
    briefing = build_agenda(s, profile(), TODAY, tmp_path).briefing
    assert "slipped: [a] it-a, 1 session running. Propose" in briefing


def test_hard_line_carries_the_note(tmp_path):
    s = trouble_state(
        last_trouble=[GradeReview(id="it-a", grade="hard", note="needed the formula")]
    )
    a = build_agenda(s, profile(), TODAY, tmp_path)
    assert 'hard: [a] it-a, passed with help — "needed the formula".' in a.briefing
    assert "slipped:" not in a.briefing
    assert a.review_items == []  # a `hard` pulls nothing in


def test_trouble_on_a_deleted_card_is_skipped(tmp_path):
    s = trouble_state(last_trouble=[GradeReview(id="it-gone", grade="again", note="n")])
    assert "slipped:" not in build_agenda(s, profile(), TODAY, tmp_path).briefing


def test_emphasis_lines(tmp_path):
    s = trouble_state(emphasis={"b": Emphasis.MORE, "a": Emphasis.LESS})
    briefing = build_agenda(s, profile(), TODAY, tmp_path).briefing
    assert "emphasis: [a] less" in briefing and "emphasis: [b] more" in briefing
    assert "emphasis:" not in build_agenda(
        trouble_state(), profile(), TODAY, tmp_path
    ).briefing
```

- [ ] **Step 10: Run them and see them fail**

Run: `uv run pytest tests/test_agenda.py -q`
Expected: the new tests FAIL.

- [ ] **Step 11: Add the lines in `src/seba/scheduler/agenda.py`**

Import `Emphasis`. Add after `_stuck_lines`:

```python
def _trouble_lines(state: GoalState) -> list[str]:
    """What went wrong last session, in the tutor's own words. Reporting only:
    the scheduler has already decided when each of these cards comes back."""
    concept_of = {i.id: i.concept for i in state.items}
    lines = []
    for r in state.last_trouble:
        cid = concept_of.get(r.id)
        if cid is None:
            continue  # card since deleted
        note = (r.note or "").strip()
        said = f' — "{note}"' if note else ""
        if r.grade == Grade.AGAIN:
            n = state.again_runs.get(r.id, 1)
            lines.append(
                f"slipped: [{cid}] {r.id}, {n} session{'' if n == 1 else 's'} "
                f"running{said}. Propose re-teaching if the repair doesn't hold."
            )
        else:
            lines.append(
                f"hard: [{cid}] {r.id}, passed with help{said}. Touch on it in "
                "conversation; the schedule is unchanged."
            )
    return lines


def _emphasis_lines(state: GoalState) -> list[str]:
    often = {Emphasis.MORE: "more", Emphasis.LESS: "less"}
    return [
        f"emphasis: [{cid}] {e} — the learner asked to see these cards "
        f"{often[e]} often."
        for cid, e in sorted(state.emphasis.items())
    ]
```

In `build_agenda`, after `lines += _stuck_lines(state)`:

```python
    lines += _trouble_lines(state)
    lines += _emphasis_lines(state)
```

Update the docstring of `_reviews`: error sites are concepts graded `again` last session.

- [ ] **Step 12: Run the agenda tests and see them pass**

Run: `uv run pytest tests/test_agenda.py -q`
Expected: PASS.

- [ ] **Step 13: Write the CLI round-trip tests**

Add to `tests/test_session_cli.py`:

```python
AWKWARD = 'mixed up "σ-algebra"\nwith a topology — perché?'


def _finish_session(*grade_args):
    assert runner.invoke(app, ["start", "prob"]).exit_code == 0
    result = runner.invoke(app, ["grade", "prob", "it-1", *grade_args])
    assert result.exit_code == 0, result.output
    result = runner.invoke(app, ["end", "prob", "--summary", "s", "--hint", "h"])
    assert result.exit_code == 0, result.output


def _briefing():
    result = runner.invoke(app, ["start", "prob"])
    assert result.exit_code == 0, result.output
    return yaml.safe_load(result.output)["agenda"]


def test_grade_hard_without_a_note_is_refused(monkeypatch, tmp_path):
    seed(env(monkeypatch, tmp_path))
    runner.invoke(app, ["start", "prob"])
    result = runner.invoke(app, ["grade", "prob", "it-1", "hard"])
    assert result.exit_code == 1 and "--note" in result.output
    result = runner.invoke(app, ["grade", "prob", "it-1", "hard", "--note", "  "])
    assert result.exit_code == 1


def test_a_hard_note_reaches_the_next_briefing(monkeypatch, tmp_path):
    seed(env(monkeypatch, tmp_path))
    _finish_session("hard", "--note", AWKWARD)
    agenda = _briefing()
    assert f'hard: [bayes] it-1, passed with help — "{AWKWARD}".' in agenda["briefing"]
    # a `hard`-only session pulls no extra cards into the next
    assert agenda["review_items"] == []
```

- [ ] **Step 14: Run `make check`**

Expected: all pass.

- [ ] **Step 15: Commit**

```bash
git add src/seba tests
git commit -m "feat(grading): hard is a pass that says why; only again pulls cards in early"
```

---

### Task 5: Remove the automatic reopen; add `reopened`

**Files:**
- Modify: `src/seba/scheduler/apply.py`, `src/seba/models.py`, `src/seba/store/store.py`, `src/seba/session/tools.py`, `src/seba/syllabus/graph.py`, `src/seba/cli.py`
- Test: `tests/test_apply.py`, `tests/test_tools.py`, `tests/test_store.py`, `tests/test_session_cli.py`

**Interfaces:**
- Consumes: `GoalState.again_runs`, the `slipped:` briefing line (Task 4).
- Produces:
  - `UpdateConcept.status_change: Literal["started", "completed", "reopened"] | None`
  - `GoalState.recent_by_item` is removed.
  - `seba.scheduler.apply.lapsing_concepts` is removed.
  - `seba concept GOAL ID --status reopened`

- [ ] **Step 1: Change the apply tests**

In `tests/test_apply.py`:

Delete `test_reopen_is_idempotent_and_ignores_older_lapses` and `test_completed_this_session_beats_the_lapse`.

Replace `done_state` and `test_lapsing_card_reopens_its_concept` with:

```python
def done_state():
    s = state()
    s.syllabus.concepts[0] = s.syllabus.concepts[0].model_copy(
        update={"status": "done"}
    )
    return s


def test_an_again_leaves_a_done_concept_done():
    rec = SessionRecord(reviews=[GradeReview(id="it-1", grade="again", note="n")])
    out = apply_record(done_state(), rec, NOW)
    assert out.syllabus.concepts[0].status == "done"


def test_reopened_moves_done_to_in_progress():
    rec = SessionRecord(concepts=[UpdateConcept(id="bayes", status_change="reopened")])
    out = apply_record(done_state(), rec, NOW)
    assert out.syllabus.concepts[0].status == "in-progress"
```

- [ ] **Step 2: Add the handler tests**

In `tests/test_tools.py`, add `Status` to the `seba.models` import, and add:

```python
def _set_status(handler, status):
    handler.syllabus.concepts[0] = handler.syllabus.concepts[0].model_copy(
        update={"status": status}
    )


def test_reopened_needs_a_done_concept(handler):
    for status in (Status.UNSEEN, Status.IN_PROGRESS):
        _set_status(handler, status)
        text, err = handler.handle(
            "update_concept", {"id": "bayes", "status_change": "reopened"}
        )
        assert err and "only a done concept can be reopened" in text
    assert not handler.record.concepts
    _set_status(handler, Status.DONE)
    text, err = handler.handle(
        "update_concept", {"id": "bayes", "status_change": "reopened"}
    )
    assert not err and text == "recorded"


def test_started_does_not_reopen_a_done_concept(handler):
    _set_status(handler, Status.DONE)
    text, err = handler.handle(
        "update_concept", {"id": "bayes", "status_change": "started"}
    )
    assert err and "--status reopened" in text
```

- [ ] **Step 3: Run them and see them fail**

Run: `uv run pytest tests/test_apply.py tests/test_tools.py -q`
Expected: FAIL (`reopened` is not a valid `status_change`; the `again` test sees `in-progress`).

- [ ] **Step 4: Implement**

`src/seba/models.py`: `status_change: Literal["started", "completed", "reopened"] | None = None`. Delete `recent_by_item` from `GoalState`.

`src/seba/store/store.py`: delete the `by_item` accumulator, its `setdefault(...).append(...)` line, and the `recent_by_item=` argument.

`src/seba/scheduler/apply.py`: delete `lapsing_concepts` and everything in `apply_record` after the `for c in record.concepts:` loop except the `return`. Drop the now-unused `Grade` import. `_STATUS` becomes:

```python
_STATUS: dict[str, Status] = {
    "started": Status.IN_PROGRESS,
    "completed": Status.DONE,
    "reopened": Status.IN_PROGRESS,
}
```

`src/seba/syllabus/graph.py`: in `apply_status`, replace the comment above `reopen = ...` with:

```python
            # Forward one step, or a reopen. Nothing reopens by itself: the
            # tutor proposes it and the learner agrees (docs/adr/0001).
```

`src/seba/session/tools.py`: import `Status`. In `_update_concept`, after the unknown-concept check:

```python
        status = next(c.status for c in self.syllabus.concepts if c.id == call.id)
        if call.status_change == "reopened" and status != Status.DONE:
            return (
                f"'{call.id}' is {status}; only a done concept can be reopened"
            ), True
        if call.status_change == "started" and status == Status.DONE:
            return (
                f"'{call.id}' is done; reopening it is the learner's decision — "
                "if they agree, use --status reopened"
            ), True
```

`src/seba/cli.py`: the `--status` help becomes `"started|completed|reopened"`.

`tests/test_store.py`: in `test_delayed_pass_needs_a_later_session`, replace the `recent_by_item` assertion with `assert gs2.again_runs == {}`.

- [ ] **Step 5: Run them and see them pass**

Run: `uv run pytest tests/test_apply.py tests/test_tools.py tests/test_store.py -q`
Expected: PASS.

- [ ] **Step 6: Write the end-to-end test**

Add to `tests/test_session_cli.py` (it uses `_finish_session` and `_briefing` from Task 4; `Status` comes from `seba.models`):

```python
def _mark_done(store):
    gs = store.load_goal("prob")
    done = gs.syllabus.model_copy(
        update={
            "concepts": [
                gs.syllabus.concepts[0].model_copy(update={"status": Status.DONE})
            ]
        }
    )
    store.save_session(
        "prob",
        SessionRecord(complete=True, summary="s", next_session_hint="h"),
        "t",
        gs.model_copy(update={"syllabus": done}),
    )


def _status(store):
    return store.load_goal("prob").syllabus.concepts[0].status


def test_a_slipping_card_is_reported_and_nothing_reopens(monkeypatch, tmp_path):
    store = seed(env(monkeypatch, tmp_path))
    _mark_done(store)

    _finish_session("again", "--note", "confused e with x⁻¹")
    assert _status(store) == "done"
    agenda = _briefing()
    assert "slipped: [bayes] it-1, 1 session running" in agenda["briefing"]
    assert "confused e with x⁻¹" in agenda["briefing"]
    assert [r["id"] for r in agenda["review_items"]] == ["it-1"]  # pulled in early

    _finish_session("again", "--note", "same slip")
    assert _status(store) == "done"
    assert "slipped: [bayes] it-1, 2 sessions running" in _briefing()["briefing"]

    _finish_session("good")
    assert "slipped:" not in _briefing()["briefing"]


def test_reopening_is_a_command(monkeypatch, tmp_path):
    store = seed(env(monkeypatch, tmp_path))
    runner.invoke(app, ["start", "prob"])
    result = runner.invoke(app, ["concept", "prob", "bayes", "--status", "reopened"])
    assert result.exit_code == 1 and "only a done concept" in result.output
    runner.invoke(app, ["abandon", "prob", "--discard"])

    _mark_done(store)
    runner.invoke(app, ["start", "prob"])
    result = runner.invoke(app, ["concept", "prob", "bayes", "--status", "reopened"])
    assert result.exit_code == 0, result.output
    runner.invoke(app, ["grade", "prob", "it-1", "good"])
    runner.invoke(app, ["end", "prob", "--summary", "s", "--hint", "h"])
    assert _status(store) == "in-progress"
    assert _briefing()["teach_concept"]["id"] == "bayes"  # takes the teaching slot
```

`_finish_session` calls `start`, which resumes the pending session that `_briefing` opened. That is the intended flow: one `start` per session, whoever calls it.

- [ ] **Step 7: Run `make check`**

Expected: all pass.

- [ ] **Step 8: Commit**

```bash
git add src/seba tests
git commit -m "feat(concepts): nothing reopens by itself; reopen by --status reopened"
```

---

### Task 6: `completion_passes`

**Files:**
- Modify: `src/seba/models.py`, `src/seba/store/store.py`, `src/seba/session/tools.py`, `src/seba/cli.py`
- Test: `tests/test_store.py`, `tests/test_tools.py`

**Interfaces:**
- Consumes: `GoalSettings.completion_passes` (Task 2); `reopened` (Task 5).
- Produces:
  - `GoalState.passes: dict[str, int]` replaces `GoalState.delayed_pass`. Per concept that has been started or reopened: the number of distinct sessions, later than the one where teaching started, with a `good` or `easy` review of one of the concept's cards. A later `reopened` moves the starting point to the session it was recorded in.
  - `ToolHandler(agenda, syllabus, sources_dir, max_reviews_per_session, passes: dict[str, int], completion_passes: int, carded: set[str])`

A re-recorded `started` does not move the starting point; only `reopened` does. The tutor may record `started` again on a concept already in progress, and that must not wipe its passes.

- [ ] **Step 1: Change the store test**

In `tests/test_store.py`, replace `test_delayed_pass_needs_a_later_session` with:

```python
def test_passes_count_later_sessions(store):
    store.create_goal("prob", syl(), "probability")
    gs = store.load_goal("prob").model_copy(update={"items": [item()]})
    started = SessionRecord(
        reviews=[GradeReview(id="it-1", grade="good")],
        concepts=[UpdateConcept(id="bayes", status_change="started")],
        complete=True,
    )
    store.save_session("prob", started, "t", gs)
    assert store.load_goal("prob").passes == {"bayes": 0}  # same session: no

    _save(store, gs, GradeReview(id="it-1", grade="easy"))
    gs2 = store.load_goal("prob")
    assert gs2.passes == {"bayes": 1}
    assert gs2.again_runs == {}

    _save(store, gs, GradeReview(id="it-1", grade="hard", note="one hint"))
    assert store.load_goal("prob").passes == {"bayes": 1}  # a pass is good or easy

    again_started = SessionRecord(
        reviews=[GradeReview(id="it-1", grade="good")],
        concepts=[UpdateConcept(id="bayes", status_change="started")],
        complete=True,
    )
    store.save_session("prob", again_started, "t", gs)
    assert store.load_goal("prob").passes == {"bayes": 2}  # re-recorded start


def test_reopening_restarts_the_pass_count(store):
    store.create_goal("prob", syl(), "probability")
    gs = store.load_goal("prob").model_copy(update={"items": [item()]})
    store.save_session(
        "prob",
        SessionRecord(
            concepts=[UpdateConcept(id="bayes", status_change="started")],
            complete=True,
        ),
        "t",
        gs,
    )
    _save(store, gs, GradeReview(id="it-1", grade="good"))
    assert store.load_goal("prob").passes == {"bayes": 1}
    store.save_session(
        "prob",
        SessionRecord(
            reviews=[GradeReview(id="it-1", grade="good")],
            concepts=[UpdateConcept(id="bayes", status_change="reopened")],
            complete=True,
        ),
        "t",
        gs,
    )
    assert store.load_goal("prob").passes == {"bayes": 0}
    _save(store, gs, GradeReview(id="it-1", grade="good"))
    assert store.load_goal("prob").passes == {"bayes": 1}


def test_a_concept_never_started_has_no_passes(store):
    store.create_goal("prob", syl(), "probability")
    gs = store.load_goal("prob").model_copy(update={"items": [item()]})
    _save(store, gs, GradeReview(id="it-1", grade="good"))
    assert store.load_goal("prob").passes == {}
```

- [ ] **Step 2: Change the handler tests**

In `tests/test_tools.py`, the fixture's last line becomes:

```python
    return ToolHandler(agenda, syllabus, tmp_path, 6, {}, 1, {"bayes"})
```

Replace `test_completed_needs_delayed_evidence` and `test_completed_allowed_after_a_later_pass` with:

```python
COMPLETE = {"id": "bayes", "status_change": "completed", "evidence": "solved 3 unaided"}


def test_completed_needs_a_later_pass(handler):
    text, err = handler.handle("update_concept", COMPLETE)
    assert err and "0 of 1" in text and "later session" in text
    assert not handler.record.concepts
    # started is never gated
    _, err2 = handler.handle(
        "update_concept", {"id": "bayes", "status_change": "started"}
    )
    assert not err2


def test_completed_allowed_after_a_later_pass(handler):
    handler.passes = {"bayes": 1}
    text, err = handler.handle("update_concept", COMPLETE)
    assert not err and text == "recorded"


def test_completion_passes_raises_the_bar(handler):
    handler.completion_passes = 2
    handler.passes = {"bayes": 1}
    text, err = handler.handle("update_concept", COMPLETE)
    assert err and "1 of 2" in text
    handler.passes = {"bayes": 2}
    _, err2 = handler.handle("update_concept", COMPLETE)
    assert not err2
```

`test_concept_without_cards_bypasses_the_delayed_check` stays as it is.

- [ ] **Step 3: Run them and see them fail**

Run: `uv run pytest tests/test_store.py tests/test_tools.py -q`
Expected: FAIL (`passes` is not a field; `ToolHandler` takes 6 arguments).

- [ ] **Step 4: Implement**

`src/seba/models.py`: in `GoalState`, replace `delayed_pass` and its comment with:

```python
    # Per concept, the distinct sessions with a good/easy card review, strictly
    # after the one where teaching started (or where it was last reopened) —
    # the delayed, unaided check `completed` is gated on.
    passes: dict[str, int] = Field(default_factory=dict)
```

`src/seba/store/store.py`, in `load_goal`: beside `started_at` add

```python
        counted_from: dict[str, int] = {}  # started_at, moved on by `reopened`
```

The concepts loop becomes:

```python
            for c in rec.concepts:
                if c.status_change == "started":
                    started_at.setdefault(c.id, n)
                    counted_from.setdefault(c.id, n)
                elif c.status_change == "reopened":
                    counted_from[c.id] = n
```

and the `delayed_pass=` argument becomes:

```python
            passes={
                cid: len({s for s in passed_at.get(cid, []) if s > start})
                for cid, start in counted_from.items()
            },
```

`src/seba/session/tools.py`: the constructor takes `passes: dict[str, int], completion_passes: int` where `delayed_pass: set[str]` was, and stores both. The gate becomes:

```python
        have = self.passes.get(call.id, 0)
        if call.status_change == "completed" and have < self.completion_passes:
            if call.id in self.carded:
                return (
                    f"'{call.id}' has {have} of {self.completion_passes} unaided "
                    "pass(es) in a later session; each is a good/easy review of "
                    "one of its cards, in a session after the one where teaching "
                    "started or the concept was reopened"
                ), True
            # No cards means the delayed check can never be satisfied; allowing it
            # unremarked would hide that this completion rests on the tutor alone.
            note = " (no cards for this concept, so the delayed check was skipped)"
```

`src/seba/cli.py`, in `_session`: pass `state.passes, state.settings.completion_passes,` where `state.delayed_pass,` was.

- [ ] **Step 5: Run `make check`**

Expected: all pass. `grep -rn delayed_pass src tests` finds nothing.

- [ ] **Step 6: Commit**

```bash
git add src/seba tests
git commit -m "feat(completion): gate completed on a configurable number of later passes"
```

---

### Task 7: `concepts_per_session` and `next_concepts`

**Files:**
- Modify: `src/seba/models.py`, `src/seba/scheduler/agenda.py`
- Test: `tests/test_agenda.py`, `tests/test_pending.py`

**Interfaces:**
- Consumes: `GoalSettings.concepts_per_session` (Task 2).
- Produces:
  - `Agenda.next_concepts: list[TeachConcept]` — default empty; the follow-on concepts after `teach_concept`, in order.
  - A briefing line beginning `next:` when `next_concepts` is not empty.

`teach_concept` keeps its meaning and its place, so a pending session saved before this change still loads and the existing agenda tests stand. `concepts_per_session` is a ceiling: the agenda lists up to that many ready concepts and the tutor starts the next only once the current one reaches a stopping point.

- [ ] **Step 1: Write the failing tests**

In `tests/test_agenda.py`, add `GoalSettings` to the `seba.models` import, and add:

```python
def test_concepts_per_session_lists_up_to_that_many(tmp_path):
    concepts = [
        Concept(id="a", name="A", status="done"),
        Concept(id="b", name="B"),
        Concept(id="c", name="C", status="in-progress"),
        Concept(id="d", name="D", prereqs=["b"]),  # not ready: b is not done
        Concept(id="e", name="E"),
    ]
    two = build_agenda(
        state(concepts, settings=GoalSettings(concepts_per_session=2)),
        profile(),
        TODAY,
        tmp_path,
    )
    assert two.teach_concept.id == "c"  # in progress comes first
    assert [c.id for c in two.next_concepts] == ["b"]
    assert "next: b — start it only once" in two.briefing

    five = build_agenda(
        state(concepts, settings=GoalSettings(concepts_per_session=5)),
        profile(),
        TODAY,
        tmp_path,
    )
    assert [c.id for c in five.next_concepts] == ["b", "e"]  # only what is ready


def test_one_ready_concept_lists_one(tmp_path):
    s = state(
        [Concept(id="a", name="A")], settings=GoalSettings(concepts_per_session=2)
    )
    a = build_agenda(s, profile(), TODAY, tmp_path)
    assert a.teach_concept.id == "a" and a.next_concepts == []
    assert "next:" not in a.briefing


def test_the_default_is_one_concept(tmp_path):
    s = state([Concept(id="a", name="A"), Concept(id="b", name="B")])
    a = build_agenda(s, profile(), TODAY, tmp_path)
    assert a.teach_concept.id == "a" and a.next_concepts == []


def test_no_follow_ons_outside_an_ordinary_session(tmp_path):
    concepts = [
        Concept(id="a", name="A", status="done"),
        Concept(id="b", name="B", status="done"),
        Concept(id="c", name="C"),
        Concept(id="d", name="D"),
    ]
    s = state(
        concepts, session_number=5, settings=GoalSettings(concepts_per_session=2)
    )
    a = build_agenda(s, profile(), TODAY, tmp_path)
    assert a.session_type == "synthesis"
    assert a.teach_concept is None and a.next_concepts == []


def test_follow_ons_share_the_excerpt_budget(tmp_path):
    (tmp_path / "a.md").write_text("x" * 12_000)
    (tmp_path / "b.md").write_text("y" * 12_000)
    s = state(
        [
            Concept(id="a", name="A", sources=["a.md"]),
            Concept(id="b", name="B", sources=["b.md"]),
        ],
        settings=GoalSettings(concepts_per_session=2),
    )
    a = build_agenda(s, profile(), TODAY, tmp_path)
    assert len(a.teach_concept.source_excerpts[0]) == 12_000
    assert len(a.next_concepts[0].source_excerpts[0]) == 4_000
```

In `tests/test_pending.py`, add (reuse that file's existing helper for building a pending session if it has one; the point is the missing key):

```python
def test_a_pending_session_saved_before_next_concepts_still_loads(tmp_path):
    path = tmp_path / "session.pending.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "goal": "g",
                "started": "2026-09-01",
                "agenda": {
                    "goal": "g",
                    "subject": "probability",
                    "session_number": 3,
                    "briefing": "b",
                    "review_items": [],
                    "teach_concept": {"id": "a", "name": "A"},
                    "practice_quota": 3,
                    "pace_hint": "steady",
                },
                "record": {
                    "reviews": [{"id": "it-1", "grade": "hard", "note": None}],
                    "concepts": [],
                    "new_items": [],
                },
            }
        )
    )
    pending = load_pending(path)
    assert pending.agenda.teach_concept.id == "a"
    assert pending.agenda.next_concepts == []
    assert pending.record.reviews[0].grade == "hard"  # graded before notes were required
```

- [ ] **Step 2: Run them and see them fail**

Run: `uv run pytest tests/test_agenda.py tests/test_pending.py -q`
Expected: FAIL (`next_concepts` is not a field).

- [ ] **Step 3: Implement**

`src/seba/models.py`, in `Agenda`, after `teach_concept`:

```python
    # Follow-ons when the goal allows more than one concept a session. The tutor
    # starts the next only once the current one reaches a stopping point.
    next_concepts: list[TeachConcept] = Field(default_factory=list)
```

`src/seba/scheduler/agenda.py`: move the building of a `TeachConcept` out of `build_agenda` into a helper that returns what is left of the excerpt budget:

```python
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
```

In `build_agenda`, the pick becomes a list. In-progress concepts come first, then the rest of the frontier, each once, cut to the ceiling:

```python
    ready: list[Concept] = []
    if session_type == SessionType.ORDINARY:
        in_progress = [c for c in concepts if c.status == "in-progress"]
        rest = [c for c in frontier(state.syllabus) if c.status != "in-progress"]
        ready = (in_progress + rest)[: state.settings.concepts_per_session]
    teach_src = ready[0] if ready else None
```

Where the `TeachConcept` was built inline:

```python
    teach = None
    following: list[TeachConcept] = []
    scope = {i.concept for i in picked}
    unmastered: list[str] = []
    soft_unmastered: list[str] = []
    if teach_src is not None:
        teach, budget = _teach(state, teach_src, sources_dir, EXCERPT_BUDGET)
        for src in ready[1:]:
            follow, budget = _teach(state, src, sources_dir, budget)
            following.append(follow)
        scope |= {teach_src.id, *teach_src.prereqs, *(c.id for c in ready[1:])}
        unmastered = [p for p in teach_src.prereqs if by_id[p].status != "done"]
        soft_unmastered = [
            p for p in teach_src.soft_prereqs if by_id[p].status != "done"
        ]
```

After the `soft_unmastered` briefing line:

```python
    if following:
        lines.append(
            f"next: {', '.join(c.id for c in following)} — start it only once the "
            "current concept reaches a stopping point; ending the session there "
            "is always fine."
        )
```

Pass `next_concepts=following` to `Agenda(...)`.

Review selection and the prereq lines stay keyed to `teach_concept` alone: a follow-on taken from the frontier has its hard prerequisites done by definition.

- [ ] **Step 4: Run `make check`**

Expected: all pass, including every existing agenda test unchanged.

- [ ] **Step 5: Commit**

```bash
git add src/seba tests
git commit -m "feat(agenda): list up to concepts_per_session ready concepts"
```

---

### Task 8: `seba tune`

**Files:**
- Modify: `src/seba/scheduler/items.py`, `src/seba/cli.py`
- Test: `tests/test_scheduler_items.py`, `tests/test_session_cli.py`

**Interfaces:**
- Consumes: `GoalSettings`, `Emphasis`, `Store.save_tuning`, `_load_goal` (Task 2); `apply_review` (Task 3).
- Produces:
  - `seba.scheduler.items.due_now(item: Item, today: date) -> Item`
  - `seba tune GOAL [--retention F] [--max-interval N] [--concepts-per-session N] [--completion-passes N] [--concept ID --emphasis less|normal|more]`

Behaviour:

- With no flags it prints the settings and the emphasis as YAML and writes nothing.
- It validates by building a `GoalSettings` from the current values plus the changes. An out-of-range value is refused with the valid range, exit 1, nothing written.
- `--concept` and `--emphasis` go together; either alone is refused. An unknown concept is refused. `normal` removes the entry.
- `--emphasis more` also makes that concept's cards due now, the way `mint_item` stamps a new card. This is the one place Seba writes a due date itself, and it happens only because the learner asked.
- It works with or without a session in progress and never touches the pending session.
- It says which setting changed and to what. It does not commit when nothing changed.

- [ ] **Step 1: Write the failing `due_now` test**

Add to `tests/test_scheduler_items.py` (add `due_now` to the import):

```python
def test_due_now_stamps_today_like_a_new_card():
    today = date(2026, 7, 3)
    item = make_item(due="2027-01-01T00:00:00+00:00")
    stamped = due_now(item, today)
    assert stamped.fsrs["due"] == new_card().fsrs["due"]
    assert due_items([stamped], today, limit=5) == [stamped]
    assert item.fsrs["due"] == "2027-01-01T00:00:00+00:00"  # the input is untouched
```

- [ ] **Step 2: Run it and see it fail**

Run: `uv run pytest tests/test_scheduler_items.py -q`
Expected: FAIL, `cannot import name 'due_now'`.

- [ ] **Step 3: Implement `due_now`**

In `src/seba/scheduler/items.py`, pull the stamp out of `mint_item` and reuse it:

```python
def _start_of(today: date) -> str:
    return datetime.combine(today, time.min, tzinfo=timezone.utc).isoformat()


def due_now(item: Item, today: date) -> Item:
    """Make a card due today. Used only when the learner sets emphasis `more`."""
    return item.model_copy(update={"fsrs": {**item.fsrs, "due": _start_of(today)}})
```

and in `mint_item`, `fsrs["due"] = _start_of(today)`, keeping its comment.

- [ ] **Step 4: Write the failing CLI tests**

Add to `tests/test_session_cli.py`:

```python
import subprocess


def _goal_yaml(data):
    return yaml.safe_load((data / "goals" / "prob" / "goal.yaml").read_text())


def _commit_count(data):
    out = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"], cwd=data, capture_output=True, text=True
    )
    return int(out.stdout)


def test_tune_prints_and_writes_nothing(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    seed(data)
    before = _commit_count(data)
    result = runner.invoke(app, ["tune", "prob"])
    assert result.exit_code == 0
    shown = yaml.safe_load(result.output)
    assert shown["settings"] == {
        "desired_retention": 0.9,
        "max_interval_days": 180,
        "concepts_per_session": 1,
        "completion_passes": 1,
    }
    assert shown["emphasis"] == {}
    assert _commit_count(data) == before and "settings" not in _goal_yaml(data)


def test_tune_roundtrips_through_goal_yaml(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    store = seed(data)
    result = runner.invoke(
        app,
        ["tune", "prob", "--retention", "0.85", "--max-interval", "120"]
        + ["--concepts-per-session", "2", "--completion-passes", "2"],
    )
    assert result.exit_code == 0, result.output
    assert "desired_retention: 0.9 → 0.85" in result.output
    assert "max_interval_days: 180 → 120" in result.output
    assert _goal_yaml(data)["settings"] == {
        "desired_retention": 0.85,
        "max_interval_days": 120,
        "concepts_per_session": 2,
        "completion_passes": 2,
    }
    s = store.load_goal("prob").settings
    assert (s.desired_retention, s.max_interval_days) == (0.85, 120)
    # a later tune changes one value and keeps the rest
    runner.invoke(app, ["tune", "prob", "--retention", "0.8"])
    s = store.load_goal("prob").settings
    assert (s.desired_retention, s.max_interval_days) == (0.8, 120)


@pytest.mark.parametrize(
    "flags,bounds",
    [
        (["--retention", "0.5"], ["0.7", "0.97"]),
        (["--retention", "0.99"], ["0.7", "0.97"]),
        (["--max-interval", "0"], ["1"]),
        (["--concepts-per-session", "6"], ["1", "5"]),
        (["--completion-passes", "0"], ["1"]),
    ],
)
def test_tune_refuses_out_of_range_with_the_range(monkeypatch, tmp_path, flags, bounds):
    data = env(monkeypatch, tmp_path)
    seed(data)
    before = _commit_count(data)
    result = runner.invoke(app, ["tune", "prob", *flags])
    assert result.exit_code == 1
    assert flags[0] in result.output
    assert all(b in result.output for b in bounds)
    assert _commit_count(data) == before and "settings" not in _goal_yaml(data)


@pytest.mark.parametrize(
    "flags,said",
    [
        (["--concept", "ghost", "--emphasis", "more"], "unknown concept"),
        (["--concept", "bayes"], "--emphasis"),
        (["--emphasis", "more"], "--concept"),
        (["--concept", "bayes", "--emphasis", "lots"], "less, normal, more"),
    ],
)
def test_tune_refuses_bad_emphasis(monkeypatch, tmp_path, flags, said):
    data = env(monkeypatch, tmp_path)
    seed(data)
    result = runner.invoke(app, ["tune", "prob", *flags])
    assert result.exit_code == 1 and said in result.output
    assert "emphasis" not in _goal_yaml(data)


def test_emphasis_more_makes_the_cards_due_now(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    store = seed(data)
    gs = store.load_goal("prob")
    far = gs.items[0].model_copy(update={"fsrs": _fsrs("2099-01-01T00:00:00+00:00")})
    store.save_tuning("prob", gs.settings, gs.emphasis, [far])
    assert yaml.safe_load(runner.invoke(app, ["start", "prob"]).output)["agenda"][
        "review_items"
    ] == []
    runner.invoke(app, ["abandon", "prob", "--discard"])

    result = runner.invoke(
        app, ["tune", "prob", "--concept", "bayes", "--emphasis", "more"]
    )
    assert result.exit_code == 0, result.output
    assert "emphasis [bayes]: normal → more" in result.output
    assert "1 card due now" in result.output
    gs2 = store.load_goal("prob")
    assert gs2.emphasis == {"bayes": "more"}
    assert gs2.items[0].fsrs["due"][:10] == date.today().isoformat()
    agenda = yaml.safe_load(runner.invoke(app, ["start", "prob"]).output)["agenda"]
    assert [r["id"] for r in agenda["review_items"]] == ["it-1"]
    assert "emphasis: [bayes] more" in agenda["briefing"]


def test_emphasis_less_and_normal_leave_due_dates_alone(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    store = seed(data)
    due = store.load_goal("prob").items[0].fsrs["due"]
    runner.invoke(app, ["tune", "prob", "--concept", "bayes", "--emphasis", "less"])
    gs = store.load_goal("prob")
    assert gs.emphasis == {"bayes": "less"} and gs.items[0].fsrs["due"] == due
    result = runner.invoke(
        app, ["tune", "prob", "--concept", "bayes", "--emphasis", "normal"]
    )
    assert "emphasis [bayes]: less → normal" in result.output
    assert store.load_goal("prob").emphasis == {}
    assert _goal_yaml(data)["emphasis"] == {}


def test_tune_with_nothing_to_change_does_not_commit(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    seed(data)
    runner.invoke(app, ["tune", "prob", "--retention", "0.85"])
    before = _commit_count(data)
    result = runner.invoke(app, ["tune", "prob", "--retention", "0.85"])
    assert result.exit_code == 0 and "nothing changed" in result.output
    assert _commit_count(data) == before


def test_tune_works_during_a_session(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    store = seed(data)
    runner.invoke(app, ["start", "prob"])
    pending = data / "goals" / "prob" / "session.pending.yaml"
    before = pending.read_text()
    result = runner.invoke(app, ["tune", "prob", "--max-interval", "5"])
    assert result.exit_code == 0, result.output
    assert pending.read_text() == before
    runner.invoke(app, ["grade", "prob", "it-1", "easy"])
    result = runner.invoke(app, ["end", "prob", "--summary", "s", "--hint", "h"])
    assert result.exit_code == 0, result.output
    due = datetime.fromisoformat(store.load_goal("prob").items[0].fsrs["due"])
    assert due - datetime.now(timezone.utc) <= timedelta(days=5)  # new ceiling applied


def test_tune_on_an_unknown_goal_fails_cleanly(monkeypatch, tmp_path):
    env(monkeypatch, tmp_path)
    result = runner.invoke(app, ["tune", "nope"])
    assert result.exit_code == 1 and "no such goal" in result.output
```

Add `import pytest` and `from datetime import date, datetime, timedelta, timezone` to the file's imports.

- [ ] **Step 5: Run them and see them fail**

Run: `uv run pytest tests/test_session_cli.py -q -k "tune or emphasis"`
Expected: FAIL, no such command `tune`.

- [ ] **Step 6: Implement `tune` in `src/seba/cli.py`**

Import `ValidationError` from pydantic, `Emphasis`, `GoalSettings` from `seba.models`, and `due_now` from `seba.scheduler.items`.

```python
_FLAG = {
    "desired_retention": "--retention",
    "max_interval_days": "--max-interval",
    "concepts_per_session": "--concepts-per-session",
    "completion_passes": "--completion-passes",
}
_LEVELS = ("less", "normal", "more")


def _range(field: str) -> str:
    """The valid range of a setting, read off the model so it is stated once."""
    spec = GoalSettings.model_json_schema()["properties"][field]
    low, high = spec.get("minimum"), spec.get("maximum")
    return f"between {low} and {high}" if high is not None else f"at least {low}"


def _refuse(message: str) -> typer.Exit:
    typer.echo(message, err=True)
    return typer.Exit(1)


@app.command()
def tune(
    goal: str,
    retention: float | None = typer.Option(None, "--retention"),
    max_interval: int | None = typer.Option(None, "--max-interval"),
    concepts_per_session: int | None = typer.Option(None, "--concepts-per-session"),
    completion_passes: int | None = typer.Option(None, "--completion-passes"),
    concept: str | None = typer.Option(None, "--concept"),
    emphasis: str | None = typer.Option(None, "--emphasis", help="less|normal|more"),
):
    store = _store()
    state = _load_goal(store, goal)
    asked = {
        "desired_retention": retention,
        "max_interval_days": max_interval,
        "concepts_per_session": concepts_per_session,
        "completion_passes": completion_passes,
    }
    changes = {k: v for k, v in asked.items() if v is not None}
    if not changes and concept is None and emphasis is None:
        typer.echo(
            yaml.safe_dump(
                {
                    "settings": state.settings.model_dump(mode="json"),
                    "emphasis": {c: str(e) for c, e in state.emphasis.items()},
                },
                sort_keys=False,
            )
        )
        return

    try:
        settings = GoalSettings.model_validate(
            {**state.settings.model_dump(), **changes}
        )
    except ValidationError as e:
        fields = [str(err["loc"][0]) for err in e.errors()]
        raise _refuse(
            "\n".join(f"{_FLAG[f]} must be {_range(f)}" for f in fields)
        )

    said = [
        f"{k}: {getattr(state.settings, k)} → {v}"
        for k, v in changes.items()
        if getattr(state.settings, k) != v
    ]
    levels = dict(state.emphasis)
    items = state.items
    if (concept is None) != (emphasis is None):
        raise _refuse("--concept and --emphasis go together")
    if concept is not None and emphasis is not None:
        if concept not in {c.id for c in state.syllabus.concepts}:
            raise _refuse(f"unknown concept: '{concept}'")
        if emphasis not in _LEVELS:
            raise _refuse(f"--emphasis must be one of: {', '.join(_LEVELS)}")
        was = str(levels.get(concept, "normal"))
        if emphasis == "normal":
            levels.pop(concept, None)
        else:
            levels[concept] = Emphasis(emphasis)
        line = f"emphasis [{concept}]: {was} → {emphasis}"
        if emphasis == "more":
            # The one direct override of the schedule, and only because the
            # learner asked: "I keep losing functors" on Monday, functors Tuesday.
            mine = [i for i in items if i.concept == concept]
            items = [
                due_now(i, date.today()) if i.concept == concept else i for i in items
            ]
            line += f" ({len(mine)} card{'' if len(mine) == 1 else 's'} due now)"
        if was != emphasis or emphasis == "more":
            said.append(line)

    # Nothing to say means nothing to write; and save_tuning itself declines to
    # commit when the files come out identical (emphasis `more` set twice).
    if not said or not store.save_tuning(goal, settings, levels, items):
        typer.echo("nothing changed")
        return
    typer.echo("\n".join(said))
```

Order matters in one place: validate the settings and the emphasis flags before anything is written, so a refusal leaves `goal.yaml` untouched. Move the `--concept`/`--emphasis` pairing check above the settings validation if that reads better; the tests accept either.

- [ ] **Step 7: Run `make check`**

Expected: all pass.

- [ ] **Step 8: Commit**

```bash
git add src/seba tests
git commit -m "feat(cli): seba tune for settings and emphasis"
```

---

### Task 9: Tell the tutor — `SKILL.md` and the command table

**Files:**
- Modify: `skills/seba-tutor/SKILL.md`, `docs/development.md`

**Interfaces:**
- Consumes: every command, briefing line and refusal from Tasks 2–8.
- Produces: nothing in code.

No tests. Read the whole of `skills/seba-tutor/SKILL.md` first and keep its voice: terse, imperative, second person, bold lead-ins. Change only what is listed.

- [ ] **Step 1: The command tables**

In `SKILL.md`:

- `seba grade` row: `seba grade GOAL ITEM_ID GRADE [--note TEXT]` — add that `--note` is **required** on `hard` and `again`.
- `seba concept` row: `--status started\|completed\|reopened`; add that `reopened` is only for a done concept, and only once the learner has agreed.
- New row: `seba tune GOAL [--retention F] [--max-interval N] [--concepts-per-session N] [--completion-passes N] [--concept ID --emphasis less\|normal\|more]` — with no flags, prints the goal's settings and emphasis; with flags, changes them. Works during a session.
- `seba start` row: no change.

Make the same three changes to the table in `docs/development.md`.

- [ ] **Step 2: The grading rubric**

In Session flow step 3, the rubric becomes:

```markdown
   - `again` — wrong, or no recall. `--note` says what went wrong.
   - `hard` — **correct, but only with significant help** (any hint above L2).
     It is a pass: the interval still grows. `--note` says what the help was
     for. Slow but unaided is `good`, not `hard`.
   - `good` — correct and unaided
   - `easy` — instant, confident, unaided
   - `skipped` — only for items the session never reached

   `seba grade` refuses `hard` and `again` without a note. Write the note for
   the tutor who opens the next session: "confused the identity element with
   the inverse", not "struggled".
```

- [ ] **Step 3: The briefing lines**

In Session flow step 2, add to the list of briefing lines that are instructions:

```markdown
   - `slipped: [concept] card, N session(s) running — "note"` — that card came
     back `again` last session. Open there. At two or more sessions running,
     **propose re-teaching** the concept and let the learner decide.
   - `hard: [concept] card, passed with help — "note"` — touch on what the help
     was for, in conversation. Don't drill it: the schedule is unchanged.
   - `emphasis: [concept] more|less` — the learner asked for this. Don't
     second-guess it, and don't change it without them.
   - `next: a, b` — see `agenda.next_concepts` under Teach.
```

Change the existing `[concept] recent:` line's gloss from "A trailing `again` means open there, gently" to point at the `slipped:` line for the detail.

- [ ] **Step 4: Reopened concepts**

Replace the **Reopened concepts** paragraph under Session types with:

```markdown
**Nothing reopens by itself.** A done concept stays done while its cards are
failing; the scheduler brings the failing card back and the `slipped:` line
keeps it in front of you. When the repair isn't holding, say so and propose
re-teaching: "bayes has slipped twice running — want to reopen it?" Only on a
yes: `seba concept GOAL ID --status reopened`. It takes the teaching slot next
session. Pick up where the card broke, don't re-teach from zero, and don't
commiserate. Completing it again needs a fresh later-session pass.
```

- [ ] **Step 5: Follow-on concepts and session length**

In Session flow step 4, after the first sentence, add:

```markdown
   `agenda.next_concepts` lists follow-ons when the goal allows more than one
   concept a session. It is a ceiling, never a target: start the next only once
   the current concept reaches a stopping point, and stopping after one is
   always fine. `--status started` and a first card apply to each one you begin.
```

- [ ] **Step 6: Completion**

In Session flow step 5, where it says Seba refuses `completed` unless one of the concept's cards came back `good`/`easy` in a later session, say instead that it needs the goal's `completion_passes` such sessions (default one), that the refusal states how many it has, and that after a reopen the count starts again.

- [ ] **Step 7: Tuning, in the closing negotiation**

In Session flow step 9, after the "state your read and invite disagreement" sentence, add:

```markdown
   **Tuning is the learner's call.** What they say comes first, grades second.
   Nothing tunes itself. Use grades to decide what to *propose*: "functors came
   back `again` twice — want it more often?" Then act on their answer:
   - one concept → `seba tune GOAL --concept ID --emphasis more|less|normal`.
     `more` also makes its cards due now.
   - everything coming back too often, or not often enough →
     `--retention` (0.70–0.97, default 0.9; lower means longer gaps).
   - cards vanishing for months → `--max-interval DAYS` (default 180).
   - sessions too short or too long → `--concepts-per-session N` (1–5).

   **Always say which setting changed and to what**, in the same turn. Never
   change one silently, and never to make a session go smoother.
```

- [ ] **Step 8: Check and commit**

Run: `make check` (nothing should change) and `grep -n "reopens its concept\|on its own" skills/seba-tutor/SKILL.md` (expect no claim left that anything reopens automatically).

```bash
git add skills/seba-tutor/SKILL.md docs/development.md
git commit -m "docs(skill): hard rubric, new briefing lines, reopening by agreement, tuning"
```
