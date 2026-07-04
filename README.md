# seba

*seba*, from Egyptian *sbꜣ* "to teach" — the root of *sbꜣyt*, the
instruction-literature genre (Ptahhotep, Amenemope); the glyph 𓇼 also writes
"star" and "door". Package, CLI command, and repo are all `seba`.

## What it is

A long-term personal tutor, mid-relationship with each learner. It owns a
curriculum (concept graph) and longitudinal learner state (FSRS review
scheduling + per-concept notes), all stored as plain text in a git-backed data
directory. Code owns state, scheduling, and validation; Claude Code owns
dialogue and grading, recorded through validated outcome commands.

## How it works now

Sessions run inside Claude Code — your subscription, not a metered API key,
no per-token cost. The `seba` CLI owns state, scheduling, and validation; the
`seba-tutor` skill instructs Claude Code to conduct the dialogue and record
outcomes through it.

## Install

```bash
uv tool install --force ~/Desktop/Projects/seba   # global `seba` command
mkdir -p ~/.claude/skills
ln -sfn ~/Desktop/Projects/seba/skills/seba-tutor ~/.claude/skills/seba-tutor
```

Requires Python ≥3.12 and `uv`. Then from any directory: run `claude` and ask
to study, or invoke `/seba-tutor`.

## Environment variables

- `SEBA_DATA_DIR` — where learner data lives (default `~/seba-data`). It is
  its own git repo; every saved session is a commit.

`SEBA_MODEL`, `SEBA_RECOVERY_MODEL`, and `ANTHROPIC_API_KEY` no longer
exist — Claude Code supplies the model, and there is no API key to set.

## Commands

| Command | Purpose |
|---|---|
| `seba status` | list goals with due counts |
| `seba start GOAL` | begin/resume a session; prints the agenda YAML |
| `seba grade GOAL ITEM_ID GRADE [--note TEXT]` | record a review grade |
| `seba mint GOAL --concept ID --type TYPE --front TEXT --back TEXT` | create a spaced-repetition card |
| `seba concept GOAL ID [--status started\|completed] [--note TEXT]` | record concept progress or a note |
| `seba end GOAL --summary TEXT --hint TEXT` | close the session |
| `seba abandon GOAL [--discard]` | quit early: save as INCOMPLETE (or discard) |
| `seba new-goal NAME --subject SUBJECT --from-file PATH` | create a goal from a drafted syllabus YAML |

These commands are called by Claude Code, per the `seba-tutor` skill — you
don't normally run them by hand, though nothing stops you.

## Data directory layout

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

## Crash story

Every accepted outcome is written to `session.pending.yaml` the moment it's
recorded — nothing lives only in the conversation. If the session (or Claude
Code, or the machine) dies mid-session, `seba start GOAL` resumes exactly
where it left off; `seba abandon GOAL` closes it out as INCOMPLETE instead.
There is no `extract`/replay step anymore — there is nothing to reconstruct.

## Development

### Architecture

The Python half is deterministic and stateless: each `seba` subcommand is a
one-shot invocation that reads and writes plain-text state on disk, sharing a
durable `session.pending.yaml` between calls. There is no long-running
process. The pieces:

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

Claude Code is the LLM half — dialogue and grading — and reaches the
deterministic half only through the CLI, directed by the `seba-tutor` skill.

### Invariants (don't break these)

- **All schemas live in `src/seba/models.py`.** No module defines its own dict
  shapes; pass models, not loose dicts.
- **Imports run strictly downward:** `cli → session → scheduler → store`;
  `syllabus` is a sibling used by `cli`/`store`. No circular imports.
- **`ToolHandler` owns all outcome validation.** Never add a second validator
  or default silently. Grades are `again | hard | good | easy | skipped`;
  concept status moves `unseen → in-progress → done` one step forward only;
  `mint_item` is capped at 10 per session.
- **Fail loudly.** A malformed state file raises an error naming the file; a
  CLI validation failure prints the reason to stderr and exits non-zero.
  Never swallow an error or silently default.
- **The core is offline and deterministic.** No network, no API key — tests
  run with neither.

### Running and testing

```bash
uv run pytest -q          # full suite (must be green before every commit)
uv run seba --help        # exercise the CLI directly
```

Dependencies (exact): `fsrs`, `pydantic>=2`, `rich`, `pyyaml`, `typer`; dev:
`pytest`. Add nothing else without reason. Commit after every green test cycle
with a conventional-commit subject.
