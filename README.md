# seba

*seba*, from Egyptian *sbꜣ* "to teach" — the root of *sbꜣyt*, the
instruction-literature genre (Ptahhotep, Amenemope); the glyph 𓇼 also writes
"star" and "door". Package, CLI command, and repo are all `seba`.

## What it is

A long-term personal tutor in the terminal. It owns a curriculum (concept
graph) and longitudinal learner state (FSRS review scheduling + per-concept
notes), all stored as plain text in a git-backed data directory. Code owns
state, scheduling, and validation; the LLM owns dialogue and grading, recorded
through validated outcome tools.

## Install

```bash
uv sync
```

Requires Python ≥3.12 and `uv`.

## API key

Set `ANTHROPIC_API_KEY` in the environment — the `learn`, `new-goal`, and
`extract` commands call the Anthropic API. `status` works offline.

## Environment variables

- `SEBA_DATA_DIR` — where learner data lives (default `~/seba-data`). It is
  its own git repo; every saved session is a commit.
- `SEBA_MODEL` — dialogue model (default `claude-sonnet-5`).
- `SEBA_RECOVERY_MODEL` — recovery/synthesis model (default
  `claude-haiku-4-5`).

## Commands

### `seba new-goal NAME --subject SUBJECT --toc PATH`

Draft a syllabus from a table-of-contents markdown file via the LLM, edit it
in `$EDITOR` (re-validates on save, annotating errors as YAML comments), then
create the goal.

```bash
seba new-goal probability-101 --subject probability --toc toc.md
```

Bundled subjects: `probability`, `italian`. A missing subject profile is a
friendly error pointing at `subjects/_templates/` to copy — v0 does not
auto-draft profiles; that lands in v1.

### `seba learn [GOAL]`

Also the default when you run bare `seba`. Picks a goal (or takes its name),
shows the briefing card, and converses with the tutor. During a session,
`/done` ends it — the tutor must grade or skip every review item first. On
exit it applies the session outcomes, saves, and prints a receipt.

```bash
seba learn probability-101
seba          # same, but prompts you to pick a goal
```

### `seba status`

Per-goal table: sessions completed and items due today.

```bash
seba status
```

### `seba extract GOAL N`

Recover a crashed session: replay `sessions/NNN.transcript.md` through the
recovery model to backfill the outcomes, then apply and save.

```bash
seba extract probability-101 3
```

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

## The `extract` caveat

`extract` rebuilds the agenda from the goal's *current* state, which can
differ from the crashed session's original agenda if state has since moved
on. It is meant to be run immediately after a crash, not as a general-purpose
replay tool.
