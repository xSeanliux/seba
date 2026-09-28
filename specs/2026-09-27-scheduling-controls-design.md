# Scheduling controls — design

Status: **design confirmed.** Settled over five rounds of design review. No code written yet. Terms are defined in `CONTEXT.md`.

## What the learner asked for

> Often a concept is marked as easy and just skipped, while concepts that were
> failed the first few times come up over and over for weeks on end. More
> control over thresholds, ideally adaptive.

## The principle that came out of review

py-fsrs schedules cards. It knows nothing about concepts, completion, or what
gets taught; all of that is Seba's layer. Every fault found sits where Seba acts
on top of the scheduler, never inside it. So the rule for this change is:
**the scheduler decides when a card comes back, and Seba stops second-guessing
it.** Seba changes what it feeds the scheduler and what it tells the tutor.

## What the data says

Measured on the `category-theory` goal (11 sessions, 18 cards) and reproduced
with a py-fsrs simulation (sessions 3 days apart, fuzz off).

| Finding | Cause |
|---|---|
| Card `it-b2c8b232` reviewed in eight consecutive sessions | Learning steps are 1 and 10 minutes, meant for re-showing a card in the same sitting. `hard` never advances the step, so the interval stays at zero days |
| Same | A `hard` grade pulls every card of that concept into the next session, due or not. They get graded `hard` again and the pull repeats |
| `monoids-groups` completed three times | One `again` reopens the concept, and the check reads each card's last two grades whether or not it was reviewed this session, so an old `again` keeps firing |
| Card `it-5adb868a` due four months out after two reviews | Two `easy` grades give 8 → 66 → 397 days with no ceiling |

| History | Today | Learning steps removed |
|---|---|---|
| again, hard, hard, hard, hard, good, easy | 0, 0, 0, 0, 0, 0, 15 days | 1, 2, 4, 7, 10, 17, 35 days |

## Design

### 1. Feed the scheduler correctly

- Build it with no learning steps and no relearning steps. Every grade then
  yields at least a day, and `hard` grows the interval. Cards now in the
  Learning state graduate at their next review. No data migration.
- Build it with the goal's interval ceiling (default 180 days).
- `easy` is passed through as `easy`. No damping.

### 2. `hard` is a pass, and says why

`hard` means correct with significant help. The interval grows. Grading `hard`
or `again` requires a note saying what the help was for or what went wrong;
the command refuses without one. The next briefing shows that note beside the
concept.

Today grade notes are written to the session outcome and never read again.

### 3. Only `again` pulls cards in early

`hard` no longer counts as an error site. Its note reaches the tutor through the
briefing, so the tutor can touch on it in conversation without disturbing the
schedule.

### 4. Nothing reopens by itself

The automatic reopen is removed, and the stale-grade fault goes with it. A card
graded `again` comes back when the scheduler says. The briefing reports it:

```
slipped: [monoids-groups] it-0c151259, 2 sessions running — "confused the
identity element with the inverse". Propose re-teaching if the repair doesn't hold.
```

Reopening happens when the learner agrees to it: `seba concept GOAL ID --status
reopened`. A reopened concept takes a teaching slot, as an in-progress concept
does today.

### 5. Settings, per goal

```yaml
settings:
  desired_retention: 0.9       # 0.70–0.97
  max_interval_days: 180
  concepts_per_session: 1      # up to this many
  completion_passes: 1         # later-session passes before `completed`
emphasis:
  functors: more               # less | more; absent means normal
```

- `concepts_per_session` is a ceiling. The agenda lists that many ready concepts
  in order and the tutor starts the next only once the current one reaches a
  stopping point.
- `completion_passes` generalises the existing delayed-pass gate.
- Settings take effect at each card's next review. Stored due dates are not
  rewritten, with one exception below.

### 6. Emphasis, per concept

Three levels. `more` reviews that concept's cards against a higher retention
target than the goal's (+0.05, capped at 0.97); `less` against a lower one
(−0.10, floored at 0.70). Setting `more` also makes the concept's cards due now,
so a learner who says "I keep losing functors" on Monday sees functors on
Tuesday.

### 7. One command

```
seba tune GOAL                                   # print settings and emphasis
seba tune GOAL --retention 0.85 --max-interval 120
seba tune GOAL --concepts-per-session 2
seba tune GOAL --concept functors --emphasis more
```

Out-of-range values are refused with the valid range. Works with or without a
session in progress. Committed to the data repo like everything else.

### 8. Adaptive, in the sense agreed

The learner's statement comes first, grades second. Nothing tunes itself in this
version. Grades decide what the tutor *proposes* in the closing negotiation
("functors came back `again` twice — want it more often?"), and the learner's
answer is what changes a setting. The tutor always says which setting changed
and to what.

## Removed from the first draft

| Idea | Why it went |
|---|---|
| Leech detection | The scheduler has no such notion; the card continues on schedule |
| Damping `easy` | Overrides the scheduler. Its own ceiling and retention target cover the case |
| Automatic reopen | Replaced by a briefing line and the learner's decision |
| Retention auto-tuning | Would steer on grades alone |

## Files touched

| File | Change |
|---|---|
| `models.py` | `GoalSettings`, emphasis; `Agenda.teach_concepts`; pass counts replace `delayed_pass` |
| `scheduler/items.py` | scheduler built from settings and emphasis |
| `scheduler/apply.py` | automatic reopen deleted |
| `scheduler/agenda.py` | slipped and hard-note lines; up to N concepts |
| `store/store.py` | settings read/write; `again`-only errors; grade notes and pass counts loaded |
| `session/tools.py` | note required on `hard`/`again`; `reopened`; `completion_passes` |
| `cli.py` | `tune`; `--status reopened` |
| `skills/seba-tutor/SKILL.md` | rubric for `hard`; new briefing lines; tuning; session length |
| `subjects/_templates/analytic/profile.yaml` | remove two stray lines (separate commit) |

## Testing

- `hard` on a new card yields an interval of at least one day, and the struggler
  history above produces strictly growing intervals.
- No interval exceeds `max_interval_days`.
- `grade ... hard` without a note is refused; with one, the note appears in the
  next briefing.
- A `hard`-only session pulls no extra cards into the next.
- An `again` on a done concept leaves it done and produces a slipped line; the
  count rises when it happens again and resets after a pass.
- `--status reopened` moves done to in-progress and is refused from any other status.
- `concepts_per_session: 2` lists two concepts when two are ready, one when one is.
- Emphasis `more` makes the concept's cards due today and shortens the next
  interval relative to normal; `less` lengthens it.
- `completed` is refused at one pass when `completion_passes: 2`.
- `seba tune` round-trips through `goal.yaml`, refuses out-of-range values, and
  a goal with no settings block loads with defaults.
- A pending session saved before this change still loads.

## Confirmed in review

- `completion_passes` stays in, default 1.
- Emphasis offsets of +0.05 and −0.10 were proposed and not objected to.
- The scheduler principle is recorded in `docs/adr/0001-scheduler-owns-the-schedule.md`.
