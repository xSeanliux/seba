# Changing a syllabus

You propose; the learner decides. Never drop, restore, extend, or change the
direction on your own judgment.

**When a change lands.** `seba extend` and `seba tune --direction` act at once.
Dropping, restoring and `--add-source` are `seba concept` calls: they need a
session in progress and are applied at `seba end` (`seba abandon --discard`
throws them away), so they shape the next session, not this one. Once a concept
is dropped this session, `started`, `completed`, `reopened` and minting on it
are refused until it is restored, and so is `extend` with a concept that
depends on it.

## Mapping a new source

New material (a paper, a chapter, a page): work out with the learner which
concepts it teaches.
1. Skim its abstract and headings: a PDF's first page, the table of contents,
   the one page a URL names. **Never load the whole of it.**
2. Draft the concepts, naming the existing ones the source reuses
   (`seba view GOAL --json` lists them). Defaults:
   - One to three per source, each sized to a session or two and named by what
     the learner could explain without the source. Never carved by section.
   - Background the source assumes is a hard prerequisite (`prereqs`) of what
     needs it: the existing concept's id, or else a new concept, `done` if the
     learner has it. If not, it is a gap, and this is how it gets closed.
   - **A source is never a concept.** It goes, as slices, in the `sources` of
     the concepts it teaches.
3. Revise the draft with the learner. **Nothing is saved without an explicit
   yes.**
4. New concepts: write them to a temp file as a `concepts:` list in the schema
   under Creating a new goal in `SKILL.md`, each `unseen` or `done` (probe, as
   in step 2 there), and run `seba extend GOAL --from-file PATH`. They may name
   existing ids in `prereqs`, `soft_prereqs` and `confusable_with`. `extend`
   writes nothing and refuses an id already in the syllabus or repeated in the
   file, any other status, whatever `new-goal` refuses, and a concept whose
   `prereqs` name a dropped one (`… depends on P, which is dropped — restore
   that first`: ask about P).
   This session's agenda is unchanged; new concepts reach the frontier once
   their hard prerequisites are done. If the learner wants one now, on an
   ordinary day: once the current concept reaches a stopping point,
   `seba concept GOAL ID --status started` it and teach it as a follow-on.
   An existing concept the source also teaches:
   `seba concept GOAL ID --add-source LOCATOR`, one slice per call.

**A gap under an existing concept.** Background an existing concept needs and
the learner lacks: map it as a new concept and `seba extend` it. No command
makes the existing concept depend on it; tell the learner so, and teach the new
concept first, now or steered next session. Add that edge by hand in
`$SEBA_DATA_DIR/goals/GOAL/syllabus.yaml` only if the learner wants it.

## Dropping and restoring

`seba concept GOAL ID --status dropped` sets a concept aside: it is no longer
taught or reviewed; its history, notes and cards are kept. `--status restored`
returns it to the status it had.
- `cannot drop 'X': a, b depend on it — …` lists X's hard dependents, done
  ones included. That is news, not an obstacle: they may want those set aside
  too, or not know what rests on X. Ask. On a yes, drop the dependents first,
  then X. Remove the edge by hand in `$SEBA_DATA_DIR/goals/GOAL/syllabus.yaml`
  only for a dependency the learner agrees is wrong, never to get a drop
  through.
- `cannot restore 'X': it depends on P, which is dropped — restore that first`
  — ask about P.
- A card whose concept was dropped this session stays in this session's review
  list (each review item names its `concept`). Don't pose it: grade it
  `skipped`. Any other grade is refused:
  `'ITEM_ID' belongs to 'X', which is dropped — grade it skipped`.

## Steering

When the learner asks for a particular concept: `seba start GOAL --concept ID`
(ids from `seba view GOAL --json`). It must be in progress or on the frontier.
Any refusal but the last below starts no session: run `seba start GOAL` for the
usual one, and tell the learner what stood in the way.
- `'X' is not ready: a, b must be done first` — offer the first of those that
  is ready (in progress, or in `stats.frontier` of `seba view GOAL --json`), or
  ask what they want instead.
- `'X' is dropped; restore it first` or `'X' is done; reopen it if the learner
  wants it taught again` — restoring or reopening is its own decision, made in
  a session, and shows from the next.
- `a session is already in progress for 'GOAL' — end or abandon it before
  choosing a concept` — asked after `seba start`:
  - **Nothing recorded** — only when all of these hold: `already_graded` is
    empty; `minted_so_far` and `concept_calls_so_far` are both 0; and you have
    run no `seba grade`, `seba mint` or `seba concept` since. Then
    `seba abandon GOAL --discard`, then `seba start GOAL --concept ID`.
  - **Otherwise** — never discard: it throws away the recorded grades, cards
    and concept calls, a resumed session's too. Teach what the agenda holds.
    Put the request in the `--hint` at `seba end` by id ("learner asked for
    bayes-rule — steer to it"); tell the learner they can name it next start.

**Last session's hint asks for a concept.** If nothing is recorded (the test
above) and `teach_concept` is not already that concept, discard and start again
steered; otherwise don't. If that `--concept` is refused, the plain
`seba start GOAL` you run next is the session; keep it.

A steered session is ordinary, even on a day that would have been synthesis or
return-after-lapse. Its briefing lines:
- `steered: the learner asked for [concept] today.` — `teach_concept` is their
  pick. Teach it; don't argue for the usual order.
- `away: N days since the last session — …` — follows `steered:` on a day that
  would have been return-after-lapse. Acknowledge the time away once, briefly
  and without guilt, then teach what they asked for.

## When the direction changes

When the learner says the goal is now for something else, record it in one
line, a sentence or two in their words: `seba tune GOAL --direction TEXT`. Say
what changed. Then walk the unseen concepts with them (`seba view GOAL --json`)
and propose drops **one at a time**, each with its reason against the new
direction: "martingales served the old aim — set it aside?" Drop only on a yes.
Start with concepts nothing depends on: fewer refusals. If the new direction
needs material the syllabus lacks, map it (above).

## Running out

`nearly out of syllabus: 1 concept left unseen (…) — …` or `out of syllabus: no
concept left unseen — …`: carry on with the session. At a natural point, never
as the opener, ask what the learner wants after this: a new source to map, a
changed direction, or the goal is finished. On a small goal these lines can
show from the first session; ask anyway.
