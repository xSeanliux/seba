# Scheduling controls — notes for the implementation plan

Not a plan. These are the implementation decisions worked out while reading the
code for `2026-09-27-scheduling-controls-design.md`, written down so whoever
writes the plan starts from them. The plan itself has not been written and needs
the learner's review before any code.

Baseline on `origin/main`: `uv run pytest -q` → 105 passed. CI gate is
`make check` (ruff, ruff format, `ty check src`, pytest).

## Shapes

`models.py`:

```python
class Emphasis(StrEnum):
    LESS = "less"
    MORE = "more"          # normal is the absence of an entry


class GoalSettings(BaseModel):
    desired_retention: float = Field(0.9, ge=0.70, le=0.97)
    max_interval_days: int = Field(180, ge=1)
    concepts_per_session: int = Field(1, ge=1, le=5)
    completion_passes: int = Field(1, ge=1)
```

`GoalState` gains `settings: GoalSettings`, `emphasis: dict[str, Emphasis]`,
and three derived fields, and loses two:

| Field | Change |
|---|---|
| `passes: dict[str, int]` | replaces `delayed_pass: set[str]`. Distinct sessions, later than the one teaching started, with a `good`/`easy` review of one of the concept's cards |
| `again_runs: dict[str, int]` | replaces `recent_by_item`. Per card, the trailing run of `again`, ignoring `skipped` |
| `last_trouble: list[GradeReview]` | new. The last session's `again` and `hard` reviews, notes included |
| `last_session_errors` | kept, but `again` only |

`Agenda` keeps `teach_concept` and gains `next_concepts: list[TeachConcept] = []`
for the follow-ons when `concepts_per_session > 1`. Keeping `teach_concept`
means a pending session saved before the change still loads, and the existing
agenda tests stand.

`UpdateConcept.status_change` gains `"reopened"`.

## Where each rule lives

- **Scheduler construction** — `scheduler/items.py`. The module-level
  `_scheduler = Scheduler()` goes. `apply_review(item, grade, now, settings,
  emphasis)` builds one with `learning_steps=()`, `relearning_steps=()`,
  `maximum_interval=settings.max_interval_days`, and the target retention.
  py-fsrs clamps to `maximum_interval` after fuzzing, so a test can assert the
  ceiling exactly; interval tests otherwise need fuzz tolerance.
- **Target retention** — one small function in `scheduler/items.py`: goal
  retention, plus 0.05 for `more` or minus 0.10 for `less`, clamped to
  0.70–0.97.
- **Note required on `hard`/`again`** — `ToolHandler._grade_review`, not the
  `GradeReview` model. The model also parses old session outcomes that have no
  notes, which is the same reason `evidence` is enforced in the handler.
- **`reopened`** — `ToolHandler._update_concept` refuses it unless the concept
  is `done`. `apply_status` already permits done → in-progress.
- **Automatic reopen** — delete `lapsing_concepts` and the block at the end of
  `apply_record`.
- **Completion gate** — `ToolHandler` takes `passes` and `completion_passes`
  in place of `delayed_pass`. The no-cards bypass stays as it is.
- **Settings storage** — `goal.yaml` gains `settings:` and `emphasis:`. A
  malformed block is a `StoreError` naming the file.
- **`seba tune`** — validates by building a `GoalSettings` from the current
  values plus the changes. With no flags it prints and writes nothing. It must
  not commit when nothing changed: `Store._git` runs with `check=True` and an
  empty commit fails.
- **Emphasis `more` makes cards due now** — done by `tune`, which rewrites
  `due` on that concept's cards the way `mint_item` stamps a new card.
- **Briefing** — new lines in `scheduler/agenda.py`: `slipped:` for each
  `again` in `last_trouble` with its run length and note, `hard:` for each
  `hard` with its note, `emphasis:` for each non-normal concept.

## Tests that change

| Test | Change |
|---|---|
| `test_apply.py::test_lapsing_card_reopens_its_concept` | inverts: the concept stays done |
| `test_apply.py::test_reopen_is_idempotent_and_ignores_older_lapses` | delete |
| `test_apply.py::test_completed_this_session_beats_the_lapse` | delete; nothing to beat |
| `test_store.py::test_delayed_pass_needs_a_later_session` | asserts `passes` and `again_runs` |
| `test_store.py::test_last_session_date_and_error_sites` | add a `hard` case that leaves errors empty |
| `test_tools.py` fixture and the two delayed-pass tests | new constructor arguments and message |

No existing CLI or integration test grades `again` or `hard`, so the note
requirement breaks none of them.

## Task order

1. Remove the two stray lines from `subjects/_templates/analytic/profile.yaml`,
   with a test that every bundled and template profile parses. Own commit.
2. Settings and emphasis: models, load, save.
3. Scheduler built from settings and emphasis.
4. Notes on `hard`/`again`, `again`-only error sites, briefing lines.
5. Remove the automatic reopen; add `reopened`.
6. `completion_passes`.
7. `concepts_per_session` and `next_concepts`.
8. `seba tune`.
9. `SKILL.md`: the `hard` rubric, the new briefing lines, reopening by
   agreement, tuning, follow-on concepts.

## Inputs the spec is silent on

Each needs a test in the task that owns the code.

1. `goal.yaml` hand-edited to an out-of-range or non-numeric setting: a clean
   error naming the file, never a traceback.
2. Emphasis naming a concept that does not exist: `tune` refuses it; an entry
   already in `goal.yaml` is ignored at load.
3. A stored card in the Learning state with a step set, reviewed by a scheduler
   with no learning steps: graduates without error. Existing goals have these.
4. A stored card already due past the ceiling: left alone until its next
   review, capped from then on.
5. A note that is only whitespace: refused. A note with quotes, newlines or
   non-ASCII text: survives the round trip into the briefing.
