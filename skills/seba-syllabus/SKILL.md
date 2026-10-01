---
name: seba-syllabus
description: Change what a Seba goal covers, interactively, between sessions — add a source (paper, chapter) and map it to concepts, drop or restore a concept, change a concept's prerequisites or name, restate the direction. Use when the learner wants to change a goal's syllabus or curriculum, add a paper or material, set a concept aside, or says "/seba-syllabus".
---

# Seba syllabus

Learner changes what a goal covers. You draft; learner decides. No teaching
here.

## Commands (the `seba` CLI is on PATH)

| Command | Purpose |
|---|---|
| `seba status` | list goals |
| `seba concepts GOAL [--grep TEXT]` | curriculum: `direction:` line, `session: in progress` if pending, one line per concept (id, status, name, hard prereqs), `frontier:` line |
| `seba edit GOAL ID [--name TEXT] [--add-prereq ID] [--remove-prereq ID] [--add-source LOCATOR] [--status dropped\|restored]` | change one concept; prereq and source flags repeat; flags combine |
| `seba extend GOAL --from-file PATH` | add concepts from a file |
| `seba tune GOAL --direction TEXT` | restate what goal is for |

`edit`, `extend`, `tune` act at once.


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

## Adding a source (mapping)

1. Skim only its abstract and headings. **Never load the whole of it.**
2. Draft concepts with learner, reusing existing ids:
   - One to three per source, each a session or two, named by what learner
     could explain without the source. Never carved by section.
   - Assumed background becomes its own concept and a hard prerequisite
     (`prereqs`) of what needs it; `done` if learner has it (ask), otherwise a
     gap to teach.
   - A source is never a concept: it goes, as slices, in `sources`.
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
