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

Requires [`uv`](https://docs.astral.sh/uv/), which fetches Python ≥3.12 and
Seba's dependencies itself.

### As a Claude Code plugin

```bash
claude plugin marketplace add xSeanliux/seba
claude plugin install seba@seba
```

That is the whole install. The plugin puts a `seba` command on the PATH of
Claude Code's Bash tool (not your own shell's); its first run builds Seba's
environment, which takes a few seconds.

Every merge to `main` is a release with a new version, except pull requests
labelled `no-release`. To get it, run
`claude plugin update seba@seba`, or turn on auto-update once under
`/plugin` → Marketplaces → seba → Enable auto-update; Claude Code then updates
in the background and asks you to `/reload-plugins`. Remove with
`claude plugin uninstall seba@seba`. Your learner data is not touched.

If you installed the older way (a checkout with `make install`), run
`uv tool uninstall seba` and remove the `~/.claude/skills/seba-tutor` and
`~/.claude/skills/seba-syllabus` symlinks before installing the plugin: a
`seba` on your own PATH wins over the plugin's, so the plugin's skill would
otherwise drive the old CLI.

### Developing

```bash
git clone https://github.com/xSeanliux/seba
cd seba
uv run seba --help          # the CLI, from the checkout
claude --plugin-dir .       # loads the checkout as the plugin for one session
```

`--plugin-dir .` puts both skills and this checkout's `bin/seba` on the Bash
tool's PATH for that session only — nothing is installed. `make check` is the
gate before you push.

## Use

From any directory, run `claude`, then ask to study — or invoke
`/seba:seba-tutor`. Claude Code handles the dialogue and calls `seba` for you.

To change what a goal covers (add a paper or chapter, set a concept aside or
bring it back, change a concept's prerequisites or name, restate the
direction), ask for it outside a session, or invoke `/seba:seba-syllabus`.

`seba concepts GOAL` prints the curriculum at a glance.

`seba view GOAL --open` opens a page showing progress and the dependency graph.

Learner data lives in `$SEBA_DATA_DIR` (default `~/seba-data`), its own git
repo with one commit per saved session. If a session crashes, just ask to study
again — `seba start` resumes where it left off.

## Development

Architecture, invariants, the command reference, and how to run tests live in
[`docs/development.md`](docs/development.md).
