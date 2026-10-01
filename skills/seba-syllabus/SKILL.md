---
name: seba-syllabus
description: Change what a Seba goal covers, interactively, between sessions — create a new goal, add a source (paper, chapter) and map it to concepts, drop or restore a concept, change a concept's prerequisites or name, restate the direction. Use when the learner wants to change a goal's syllabus or curriculum, create a new goal, add a paper or material, set a concept aside, or says "/seba-syllabus".
---

# Seba syllabus

Learner changes what a goal covers. You draft; learner decides. No teaching
here.

## Commands (the `seba` CLI is on PATH)

| Command | Purpose |
|---|---|
| `seba status` | list goals |
| `seba new-goal NAME --subject SUBJECT --from-file PATH` | create a goal from a syllabus YAML drafted in conversation |
| `seba concepts GOAL [--grep TEXT]` | curriculum: `direction:` line, `session: in progress` if pending, one line per concept (id, status, name, hard prereqs), `frontier:` line |
| `seba edit GOAL ID [--name TEXT] [--add-prereq ID] [--remove-prereq ID] [--add-source LOCATOR] [--status dropped\|restored]` | change one concept; prereq and source flags repeat; flags combine |
| `seba extend GOAL --from-file PATH` | add concepts from a file |
| `seba tune GOAL --direction TEXT` | restate what goal is for |

`edit`, `extend`, `tune` act at once.

Full reference: `docs/cli.md` (under the plugin if installed as one; in the repo from a checkout).


## Conversation

1. Goal from arguments or learner; unclear → `seba status`, ask.
2. `seba concepts GOAL`. **No change runs before this check:**
   `session: in progress` → stop; learner finishes it with the tutor skill,
   or `seba abandon GOAL`; then resume here. Otherwise show the part that
   matters; ask what to change. **One question per turn, then stop.**
3. Draft exact change: every command you will run, and for new concepts the
   YAML. Show it. Ask "Apply this?" **Run nothing until an explicit yes.**
   Otherwise revise.
4. Run. Refusal → say what stood in the way, propose a fix, ask. Never work
   around a refusal.
5. Show `seba concepts GOAL` so learner sees result.

## Reading sources

Shared by "Adding a source" and "Creating a new goal" below, and by the
tutor's mid-session new-source path.

- **Get it onto disk first**, under `$SEBA_DATA_DIR/sources/<GOAL>/`, named
  plainly (`smith2024.pdf`, `ch03.md`): a URL → `curl -L -o` (PDF or page); a
  local file → copy it; a web page worth keeping as text → save it as `.md`,
  so `seba start` can pre-load slices of it later the same way it does for
  any other markdown source. Skip anything over ~50MB and keep the URL as the
  locator instead — `$SEBA_DATA_DIR` is a git repo, `seba end` commits
  everything under it, and a large PDF would land in that history; accepted
  for a normal paper or chapter, not worth it past that size.
  Can't fetch it (paywall, login, interactive site) → keep the URL as the
  locator and say so to the learner; the tutor fetches the bounded slice at
  teach time, same as it already does for a URL source.
  `seba view --json` and `seba concepts` don't list files — the
  `sources/<GOAL>/` folder is the inventory; tell the learner where it is.
- One source, one subagent: read `source-reader.md` (beside the syllabus
  skill), fill the placeholders, send it as the Agent prompt with model
  `sonnet`, one agent per source or slice, in parallel. Under the plugin the
  file is inside the bundle; from a checkout it is in the repo. `{{SOURCE}}`
  is the local path on disk (not the URL) when fetched — the agent writes
  `sources:` locators relative to `$SEBA_DATA_DIR/sources/`, e.g.
  `<GOAL>/smith2024.pdf p.3-7`; a source that couldn't be fetched keeps its
  URL as `{{SOURCE}}` and as the locator. `{{EXISTING}}` is the ids and names
  from `seba concepts GOAL`, or "none" for a new goal. You never read the
  source yourself — only its draft comes back.
- Big source — a book, or anything past a few chapters — first: read its
  table of contents yourself, or with one agent. Then split it: one agent per
  chapter group, the grouping decided from the table of contents, each a
  `{{SLICE}}` of its own.
- Merge what comes back:
  - a concept is a semantic unit; one source can yield several, never "one
    paper is one concept"; one concept can draw on several sources.
  - the same idea drafted by two agents collapses into one concept, sources
    from both.
  - an agent's `assumed_background` entry becomes its own concept, a hard
    prerequisite (`prereqs`) of what needs it; `done` if the learner already
    has it (ask), otherwise a gap to teach.
  - defaults, a guide not a rule: one to three concepts per source, each
    sized to a session or two, never carved by section.
  - an agent's `notes` flags what it couldn't place: resolve before showing
    the draft, or carry the open question to the learner.
- The merged draft goes to the learner for revision and an explicit yes
  before anything is written. A source is never a concept: it goes, as
  slices, in `sources`.

## Adding a source (mapping)

1. Read it per "Reading sources" above.
2. Draft concepts with learner, reusing existing ids where the idea already
   has one.
3. On a yes: `concepts:` list in a temp file, then
   `seba extend GOAL --from-file PATH`.

   ```yaml
   concepts:
     - id: likelihood-ratio          # kebab-case, unique
       name: Likelihood ratios
       prereqs: [bayes-rule]         # HARD gate: done first
       soft_prereqs: []              # helpful, never block
       confusable_with: []
       kc_type: concept              # fact | concept | procedure | principle
       sources: ["smith2024.pdf p.3-7"]
       status: unseen                # or done
       est_sessions: 1               # 1–3
   ```
4. Existing concept the source also teaches:
   `seba edit GOAL ID --add-source LOCATOR`.
5. Gap under an existing concept: map it as a new concept; with learner's yes,
   `seba edit GOAL EXISTING --add-prereq NEW`. Gap is taught first: tell
   learner to ask for NEW at next session, so tutor steers to it
   (`seba start GOAL --concept NEW`).

## Creating a new goal

1. Ask the learner for the goal and every primary source, and where each
   lives (local markdown/text, PDF, URL). No source is fine. Seba pre-loads
   markdown under `$SEBA_DATA_DIR/sources/`; you resolve PDFs and URLs at
   read time.
2. Read each source per "Reading sources" above; merge into one candidate
   concept list. No source → draft the candidate list yourself, same shape
   (ids, names, prereqs), from general knowledge.
3. **Entry interview**, before the draft is final — short and explicit, not a
   self-rating:
   - Two or three questions: what the learner already knows coming in, what
     they want from this goal. This also gives the direction.
   - Two or three concrete probes against the draft, at different depths —
     never "how good are you at X". This is so teaching skips what they
     already hold and doesn't drop them in unfamiliar territory.
   - What they clearly hold → `status: done` on that concept. Unsure stays
     `unseen`.
4. **Draft syllabus YAML yourself** from this schema; do NOT read Seba's
   source to reverse-engineer it:

   ```yaml
   goal: Understand introductory probability     # one line
   subject: probability                           # = --subject
   concepts:
     - id: sample-spaces                          # kebab-case, unique
       name: Sample spaces and events             # human-readable
       prereqs: []                                # HARD gate: must be done first
       soft_prereqs: []                           # helpful, never block
       confusable_with: []                        # mixed up with this; symmetric, declare on either side
       kc_type: concept                           # fact | concept | procedure | principle
       sources: []                                # SMALL slices: "blitzstein/ch01.md#1.2" (pre-loaded),
                                                  # "algebra.pdf p.40-58", "https://…/ch3"; [] = from memory
       status: unseen                             # "unseen", or "done" if the interview showed they have it
       est_sessions: 1                            # 1–3
     - id: conditional-probability
       name: Conditional probability and Bayes
       prereqs: [sample-spaces]                   # may cut across chapter order
       soft_prereqs: []
       confusable_with: []
       kc_type: concept
       sources: []
       status: unseen
       est_sessions: 2
   ```

   Write out every field.
5. Get learner's explicit approval of draft — a hard gate.
6. Write it to a temp file; run `seba new-goal NAME --subject SUBJECT
   --from-file PATH`. It rejects (read stderr, fix, retry) **duplicate concept
   ids**, `prereqs`/`soft_prereqs`/`confusable_with` **naming an id not in the
   file**, or a **cycle** in `prereqs` + `soft_prereqs` together. Bundled
   subjects: `probability`, `italian`; for a new one, first copy a template
   from repo's `subjects/_templates/` into `$SEBA_DATA_DIR/subjects/<name>/`.

## Dropping and restoring

`--status dropped` stops teaching and reviewing a concept, keeping its history
and cards. `--status restored` returns it to the status it had.
- `cannot drop …` names what depends on it. Ask; on a yes drop those first, or
  `--remove-prereq` the edge if learner agrees dependency is wrong.
- `… which is dropped — restore that first` — ask about restoring that one.

## Prerequisites and names

`--add-prereq`, `--remove-prereq`: hard edges, the curriculum. Refused: unknown
id, concept on itself, cycle, dropped prerequisite, edge already there, edge
absent. Added edge on an unseen concept takes it off the frontier till the
prerequisite is done: say so. `--name`: what learner could
explain, one line.

## Direction

Learner's words, one line: `seba tune GOAL --direction TEXT`. Then walk unseen
concepts and propose drops **one at a time**, each with its reason, starting
with those nothing depends on. Map any missing material.

## By hand

No command for `soft_prereqs`, `confusable_with`, `kc_type`, `est_sessions`.
On a yes, with no `session: in progress` line, edit
`$SEBA_DATA_DIR/goals/GOAL/syllabus.yaml`, then
`seba concepts GOAL` to check it loads. No deleting a concept: drop it.
