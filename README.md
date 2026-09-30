# seba

*seba*, from Egyptian *sbꜣ* "to teach" — the root of *sbꜣyt*, the
instruction-literature genre (Ptahhotep, Amenemope); the glyph 𓇼 also writes
"star" and "door". Package, CLI command, and repo are all `seba`.

## What it is

A long-term personal tutor, mid-relationship with each learner. It owns a
curriculum (concept graph) and longitudinal learner state (FSRS review
scheduling + per-concept notes), all stored as plain text in a git-backed data
directory. The graph is a revisable prior, not a settled plan: some edges advise
rather than gate, nothing reopens by itself (when a done concept's cards slip,
the tutor says so and proposes re-teaching it, and the learner decides), and
marking one done needs evidence from a later session, not the tutor's word on
the day. Code owns state, scheduling, and validation; Claude Code owns dialogue
and grading, recorded through validated outcome commands.

The learner steers the schedule with a retention target, an interval ceiling,
and per-concept emphasis (`seba tune`). These reach it as the scheduler's own
inputs; Seba never second-guesses the scheduler on its own. The syllabus can
change while a goal is under way: concepts added from a new source, set aside
and restored, their prerequisites rewired, the direction restated.

Sessions run inside Claude Code — your subscription, not a metered API key, no
per-token cost. The `seba` CLI owns state, scheduling, and validation; two
skills instruct Claude Code to drive it. `seba-tutor` conducts a session:
review, teaching, and recording outcomes. `seba-syllabus` changes what a goal
covers, between sessions, by conversation: it drafts each change, shows it to
you, and applies it only once you agree. You talk to Claude Code; it drives
`seba` for you.

## Install

Requires Python ≥3.12 and [`uv`](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/xSeanliux/seba
cd seba
make install          # or: ./scripts/install.sh
```

This installs the `seba` CLI (`uv tool install`) and links the `seba-tutor`
skill into `~/.claude/skills/`. Reverse with `make uninstall` (or
`./scripts/uninstall.sh`).

Not a Claude Code plugin — `/plugin` doesn't manage it. To update, `git pull`
then `make install`. The skill is a symlink and so is already live after the
pull; the CLI is a copy and needs the reinstall, which is what `make install`
is for.

## Use

From any directory, run `claude`, then ask to study — or invoke `/seba:seba-tutor`
(`/seba-tutor` from a checkout install).
Claude Code handles the dialogue and calls `seba` for you.

To change what a goal covers (add a paper or chapter, set a concept aside or
bring it back, change a concept's prerequisites or name, restate the
direction), ask for it outside a session, or invoke `/seba:seba-syllabus`
(`/seba-syllabus` from a checkout install).

`seba concepts GOAL` prints the curriculum at a glance.

`seba view GOAL --open` opens a page showing progress and the dependency graph.

Learner data lives in `$SEBA_DATA_DIR` (default `~/seba-data`), its own git
repo with one commit per saved session. If a session crashes, just ask to study
again — `seba start` resumes where it left off.

## Development

Architecture, invariants, the command reference, and how to run tests live in
[`docs/development.md`](docs/development.md).
