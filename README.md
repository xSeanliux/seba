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

Sessions run inside Claude Code — your subscription, not a metered API key, no
per-token cost. The `seba` CLI owns state, scheduling, and validation; the
`seba-tutor` skill instructs Claude Code to conduct the dialogue and record
outcomes through it. You talk to Claude Code; it drives `seba` for you.

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

## Install as a Claude Code plugin

The plugin bundles the `seba` CLI and the `seba-tutor` skill, so there's no
manual `uv tool install` or symlinking — Claude Code runs it for you. Only
prerequisite is [`uv`](https://docs.astral.sh/uv/); the plugin resolves Python
deps lazily on first use.

```bash
claude plugin marketplace add xSeanliux/seba
claude plugin install seba@seba
```

Then open `claude` and ask to study (or `/seba-tutor`) — same as the local
install, but nothing to set up. `make install` above remains the local/dev
path; the plugin is the zero-setup path for users.

## Use

From any directory, run `claude`, then ask to study — or invoke `/seba-tutor`.
Claude Code handles the dialogue and calls `seba` for you.

Learner data lives in `$SEBA_DATA_DIR` (default `~/seba-data`), its own git
repo with one commit per saved session. If a session crashes, just ask to study
again — `seba start` resumes where it left off.

## Development

Architecture, invariants, the command reference, and how to run tests live in
[`docs/development.md`](docs/development.md).
