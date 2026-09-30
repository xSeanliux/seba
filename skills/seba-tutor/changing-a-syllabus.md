# Changing a syllabus mid-session

You propose; learner decides. Never drop or steer on your own judgment. Any
other change to what goal covers (new source, restore, prerequisites, new
direction): suggest learner use the syllabus skill after the session.

## Dropping

Learner asks to set a concept aside: `seba concept GOAL ID --status dropped`.
Applies from next session; stops teaching and reviewing it, keeping its
history.
- `cannot drop …` — tell learner what depends on it, ask; on a yes, drop those
  first. Otherwise leave it for the syllabus skill.
- Review card whose concept was dropped this session: grade it `skipped`.

## Steering

Learner asks for a concept: `seba start GOAL --concept ID` (ids from
`seba concepts GOAL`). On any refusal but the last, run `seba start GOAL` and
say what stood in the way.
- `not ready: …` — offer first ready one of those (in progress, or on
  `frontier:` line of `seba concepts GOAL`), or ask.
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

## Running out

`nearly out of syllabus` / `out of syllabus`: carry on. At a natural point,
never as opener, ask what next: new source, new direction, or done. New source
or direction → suggest the syllabus skill after the session.
