# Changing a syllabus

You propose; learner decides. Never drop, restore, extend, or change direction
on your own judgment. `extend` and `--direction` act at once; dropping,
restoring and `--add-source` apply from next session.

## Mapping a new source

1. Skim only its abstract and headings. **Never load the whole of it.**
2. Draft concepts with learner, reusing existing ids (`seba view GOAL --json`):
   - One to three per source, each a session or two, named by what learner
     could explain without the source. Never carved by section.
   - Assumed background becomes its own concept and a hard prerequisite
     (`prereqs`) of what needs it; `done` if learner has it, otherwise a gap
     to teach.
   - A source is never a concept: it goes, as slices, in `sources`.
3. **Save only after an explicit yes:** `concepts:` list (new-goal schema in
   `SKILL.md`, each `unseen` or `done`) in a temp file, then
   `seba extend GOAL --from-file PATH`.
4. Existing concept the source also teaches:
   `seba concept GOAL ID --add-source LOCATOR`, one slice per call.

Teach a new concept now, on an ordinary day: once current concept reaches a
stopping point, `--status started` it, teach, mint. Counts against
`concepts_per_session` like any follow-on.

**Gap under an existing concept:** map it as a new concept; teach it first.
Add the edge by hand in `$SEBA_DATA_DIR/goals/GOAL/syllabus.yaml` only if
learner wants it.

## Dropping and restoring

`--status dropped` stops teaching and reviewing a concept, keeping its
history; `--status restored` undoes that.
- `cannot drop …` — tell learner what depends on it, ask; on a yes, drop those
  first. Never edit an edge by hand to get a drop through.
- `… depends on P, which is dropped …` — ask about restoring P.
- Review card whose concept was dropped this session: grade it `skipped`.

## Steering

Learner asks for a concept: `seba start GOAL --concept ID`. On any refusal but
the last, run `seba start GOAL` and say what stood in the way.
- `not ready: …` — offer first ready one of those, or ask.
- `is dropped` / `is done` — restoring or reopening is a separate decision.
- `a session is already in progress …`:
  - **Nothing recorded** — only when all of these hold: `already_graded` is
    empty; `minted_so_far` and `concept_calls_so_far` are both 0; and you have
    run no `seba grade`, `seba mint` or `seba concept` since. Then
    `seba abandon GOAL --discard`, then `seba start GOAL --concept ID`.
  - **Otherwise** — never discard: it throws away the recorded grades, cards
    and concept calls, a resumed session's too. Teach what agenda holds. Put
    the request in `--hint` at `seba end` by id ("learner asked for
    bayes-rule — steer to it").

**Last session's hint asks for a concept:** if nothing is recorded and
`teach_concept` isn't that concept, discard and start steered. If `--concept`
is refused, keep the plain session.

Steered session is ordinary, whatever the day.
- `steered: …` — teach their pick; don't argue for usual order.
- `away: …` — acknowledge time away once, without guilt.

## When the direction changes

Record it in one line, in their words: `seba tune GOAL --direction TEXT`. Then
propose dropping unseen concepts **one at a time**, each with its reason,
starting with those nothing depends on. Map any missing material.

## Running out

`nearly out of syllabus` / `out of syllabus`: carry on. At a natural point,
never as opener, ask what next: new source, new direction, or done.
