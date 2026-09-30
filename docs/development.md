# seba — developer docs

Internals, invariants, and how to run the project. For install/use, see the
[README](../README.md).

## Architecture

The Python half is deterministic and stateless: each `seba` subcommand is a
one-shot invocation that reads and writes plain-text state on disk, sharing a
durable `session.pending.yaml` between calls. There is no long-running process.
The pieces:

- `build_agenda` — the **context firewall**: turns durable learner state into
  the single agenda the tutor sees (what's due, what to teach). It is the only
  thing that decides *what* a session covers.
- `ToolHandler` — the **one validator**: every outcome (grade, mint, concept
  update, end-gate) is validated here and nowhere else. One code path, one
  error format.
- `apply_record` — folds an accepted session record into learner state (FSRS
  scheduling + syllabus progress).
- `save_session` — writes the session files and makes one git commit in the
  data repo.
- `view` — deterministic tooling around the loop: `seba view` renders
  `GoalState` through a bundled self-contained HTML template
  (`src/seba/ui/view_template.html`) — the CLI only injects a JSON blob.

Claude Code is the LLM half — dialogue and grading — and reaches the
deterministic half only through the CLI, directed by the `seba-tutor` skill.

## Invariants (don't break these)

- **All schemas live in `src/seba/models.py`.** No module defines its own dict
  shapes; pass models, not loose dicts.
- **Imports run strictly downward:** `cli → session → scheduler → store`;
  `syllabus` is a sibling used by `cli`/`store`. No circular imports.
- **`ToolHandler` owns all outcome validation.** Never add a second validator
  or default silently. Grades are `again | hard | good | easy | skipped`, and a
  card whose concept is dropped takes only `skipped`;
  concept status moves `unseen → in-progress → done` one step forward only,
  except `reopened` (`done → in-progress`), `dropped` (from any other status, while no
  live concept has it as a hard prereq) and `restored` (back to the status it
  was dropped from, while none of its hard prereqs is dropped); `started` on an
  unseen concept needs its hard prereqs done. Every concept call is judged
  against the syllabus as this session's record leaves it, not as it was at
  `seba start`, and so is `seba extend`'s refusal of a new concept on a
  dropped one;
  `mint_item` is capped per session by `mint_budget`: 2 to 5, depending on
  the subject's review capacity. It is a count of new cards, half the
  session's review capacity, floored at 2 and capped at 5, so that new cards
  never outrun what a session can review.
- **Fail loudly.** A malformed state file raises an error naming the file; a
  CLI validation failure prints the reason to stderr and exits non-zero.
  Never swallow an error or silently default.
- **The core is offline and deterministic.** No network, no API key — tests
  run with neither.

## Running and testing

```bash
make check          # lint + format-check + type-check + tests (the CI gate)
make test           # pytest only
uv run seba --help  # exercise the CLI directly
```

Dependencies are whatever `pyproject.toml` / `uv.lock` pin — check there, not a
list here. Commit after every green `make check`, with a conventional-commit
subject.

## Command reference

These commands are **agent-facing**: Claude Code calls them during a session,
directed by the `seba-tutor` skill. You rarely run them by hand (`seba status`
is the exception).

| Command | Purpose |
|---|---|
| `seba status` | list goals with due counts |
| `seba start GOAL [--concept ID]` | begin/resume a session; prints the agenda YAML. `--concept` teaches that concept instead of the usual pick (in progress or on the frontier; refused once a session is pending) |
| `seba grade GOAL ITEM_ID GRADE [--note TEXT]` | record a review grade; `--note` is required on `hard` and `again` |
| `seba mint GOAL --concept ID --type TYPE --front TEXT --back TEXT` | create a spaced-repetition card |
| `seba concept GOAL ID [--status started\|completed\|reopened\|dropped\|restored] [--evidence TEXT] [--note TEXT] [--add-source LOCATOR]` | record concept progress, a note, or a source; `completed` requires `--evidence`; `reopened` is only for a done concept, once the learner has agreed. Drops, restores and sources are applied at `seba end` |
| `seba extend GOAL --from-file PATH` | append concepts to the goal's syllabus; validated whole, written at once, works with or without a session pending; refuses a new concept whose hard prereq is dropped |
| `seba tune GOAL [--retention F] [--max-interval N] [--concepts-per-session N] [--completion-passes N] [--concept ID --emphasis less\|normal\|more] [--direction TEXT]` | no flags: print the goal's direction, settings and emphasis; with flags: change them. `--direction` is written at once. Works during a session, but the session's review list and follow-on concepts were fixed at `seba start`: emphasis `more` and `--concepts-per-session` show from the next session. Retention, the interval ceiling and emphasis take effect at each card's next review, including cards graded later in this session. `--retention` (default 0.9, py-fsrs's own) is bounded by design to 0.70–0.97, the limits Anki puts on FSRS desired retention: below 0.70 the learner forgets most of what they review, above 0.97 the workload grows without bound for little gain in recall. `--completion-passes` (default 3) is the number of distinct sessions, later than the one where the concept was started or reopened, in which one of its cards came back `good` or `easy`, before `completed` is allowed: a pass is per session, not per card, and `good` counts as well as `easy` |
| `seba end GOAL --summary TEXT --hint TEXT` | close the session |
| `seba abandon GOAL [--discard]` | quit early: save as INCOMPLETE (or discard) |
| `seba new-goal NAME --subject SUBJECT --from-file PATH` | create a goal from a drafted syllabus YAML |
| `seba view GOAL [--json] [--open]` | render the goal's dependency graph + card status to HTML; `--json` prints the data blob instead, `--open` shows it in the browser |

## Data directory layout

`$SEBA_DATA_DIR` (default `~/seba-data`) is its own git repo — every saved
session is a commit.

```
$SEBA_DATA_DIR/
├── goals/
│   └── <name>/
│       ├── goal.yaml
│       ├── syllabus.yaml
│       ├── items.jsonl
│       ├── notes.md
│       └── sessions/
│           ├── 001.md
│           ├── 001.outcomes.yaml
│           └── 001.transcript.md
└── sources/
```

## Crash recovery

Every accepted outcome is written to `session.pending.yaml` the moment it's
recorded — nothing lives only in the conversation. If the session (or Claude
Code, or the machine) dies mid-session, `seba start GOAL` resumes exactly where
it left off; `seba abandon GOAL` closes it out as INCOMPLETE instead. There is
no replay/reconstruction step.
