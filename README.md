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
