# Scheduling controls — design

Status: **draft, awaiting review.** No code written yet.

## What the learner asked for

> Often a concept is marked as easy and just skipped, while concepts that were
> failed the first few times come up over and over for weeks on end. More
> control over thresholds (when a thing is done, spaced-repetition thresholds),
> ideally adaptive.

Success looks like: a card that was passed with hesitation stops appearing every
session; a card that was called `easy` twice does not vanish for a year; the
learner can turn the dials themselves; and the system notices when a card is
going nowhere instead of repeating it.

## What the data says

Measured on the `category-theory` goal (11 sessions, 18 cards) and reproduced
with a py-fsrs simulation (sessions 3 days apart, fuzz off).

**1. Learning steps are in minutes; sessions are days apart.** `Scheduler()`
runs on py-fsrs defaults: learning steps of 1 and 10 minutes, built for
re-showing a card inside one Anki sitting. In the Learning state `hard` does not
advance the step, so the interval stays at zero days and the card is due at
every session until it collects two `good`s. Seba's rubric makes `hard` a pass
("correct but with hesitation"), so a pass is being scheduled as a failure.

| History | Default | No learning steps |
|---|---|---|
| again, hard, hard, hard, hard, good, easy | 0, 0, 0, 0, 0, 0, 15 days | 1, 2, 4, 7, 10, 17, 35 days |

Card `it-b2c8b232` (monoids-groups) was reviewed in eight consecutive sessions:
again, hard, hard, hard, hard, good, skipped, easy.

**2. The warm-review pull feeds itself.** `last_session_errors` counts `hard` as
an error and pulls *every* card of that concept into the next session whether
due or not. Those cards get graded `hard` again, which puts the concept back in
`last_session_errors`.

**3. `easy` compounds fast.** Two `easy` grades give 8 → 66 → 397 days. Card
`it-5adb868a` has two reviews and is next due four months out. The grader is an
LLM reading a conversation, and the research notes already flag over-grading as
the likely failure (`09-review-scheduling.md` §10).

**4. One dial cannot fix both.** Raising `desired_retention` to 0.95 brings the
easy card back sooner (3 → 14 → 52 days) but makes the struggling card *more*
frequent (1, 1, 2, 3, 3, 4 days). The two complaints pull in opposite
directions, so they need separate fixes.

## Design

Four parts, smallest first. Parts A and B change defaults; C adds the dials; D
is the adaptive piece.

### A. Fix the defaults

- Build the scheduler with `learning_steps=()` and `relearning_steps=()`. Every
  grade then yields an interval of at least a day, and `hard` grows it. Cards
  currently in the Learning state graduate on their next review; py-fsrs handles
  an empty step list on a card that has a step set. No data migration.
- `last_session_errors` counts `again` only. With A in place an `again` card is
  due the next day regardless, so the pull still brings in its siblings, which
  is what Rosenshine's daily review is for.

### B. Damp early `easy`

An `easy` is recorded as `good` for scheduling until the card has passed
(`good`/`easy`) in an earlier session. The grade in the session outcome stays
`easy`; only the FSRS update is damped. First-ever `easy` then gives 2 days
rather than 8, and the 66-day jump needs two sessions of evidence.

Rejected: exposing FSRS weights (unreadable), and capping interval growth as a
multiple of the last interval (a second scheduler fighting the first).

### C. Per-goal settings

A `settings` block in `goal.yaml`, all optional, defaults shown:

```yaml
settings:
  desired_retention: 0.9     # 0.70–0.97; higher = more reviews of everything
  max_interval_days: 180     # ceiling on any card's interval
  completion_passes: 1       # later-session passes required before `completed`
```

- Per goal rather than per subject: an exam in six weeks and lifelong Italian
  want different schedules from the same subject profile.
- `max_interval_days` defaults to 180, down from py-fsrs's 36,500. This is a
  behaviour change for existing goals and only bites cards already past 180
  days.
- `completion_passes` generalises the existing delayed-pass gate. `delayed_pass:
  set[str]` on `GoalState` becomes a count per concept; the refusal message
  names how many passes are still owed.
- New settings apply at each card's next review. Due dates already stored are
  not rewritten.

One command, because the learner talks to the tutor rather than editing YAML:

```
seba tune GOAL                          # print current settings
seba tune GOAL --retention 0.85 --max-interval 120 --completion-passes 2
```

Out-of-range values are refused with the valid range. The change is committed to
the data repo like everything else.

`SKILL.md` gains a short section: when the learner says reviews are too frequent
or too sparse, say what the dial does, confirm the value, run `seba tune`.

Not exposed: `STUCK_RATE`, `STUCK_MIN_OPPORTUNITIES`, `LAPSE_DAYS`,
`SYNTHESIS_EVERY`, the pace cutoffs. Nobody has asked for them. They move into
`settings` when someone does.

### D. Adaptive: leeches, not parameter fitting

A card reviewed four or more times with no `good`/`easy` in its last four is a
**leech**. The briefing gets a line, in the style of the existing `stuck:` line:

```
leech: [it-b2c8b232] (monoids-groups) 4 reviews without a clean pass —
the card is the problem: rewrite or split it, then retire the old one.
```

`seba retire GOAL ITEM_ID` sets the existing `Item.suspended` flag, which
nothing can currently set. The tutor mints the replacement with `seba mint`.

This adapts the *material* rather than the *parameters*, which is the right
order at this scale:

- FSRS's own optimizer needs a few hundred reviews and pulls in torch. The
  largest goal has about sixty. Revisit when a goal passes ~400 reviews.
- Auto-tuning `desired_retention` from measured recall is one function, but it
  steers on LLM-assigned grades. If the grader inflates, measured recall reads
  high and the controller *lengthens* intervals, which is complaint one again.
  Deferred until grades can be trusted; see open question 3.

## Files touched

| File | Change |
|---|---|
| `models.py` | `GoalSettings`; `GoalState.settings`; `delayed_pass` becomes a count |
| `scheduler/items.py` | scheduler built from settings; `easy` damping |
| `scheduler/apply.py` | passes settings and pass history through |
| `scheduler/agenda.py` | leech lines |
| `store/store.py` | read/write `settings`; `again`-only errors; pass counts |
| `session/tools.py` | `completion_passes` in the gate |
| `cli.py` | `tune`, `retire` |
| `skills/seba-tutor/SKILL.md` | tuning section; leech line in the briefing list |

## Testing

One test per behaviour, in the existing test files:

- `hard` on a new card yields an interval of at least one day.
- The struggler history above produces strictly growing intervals.
- First `easy` schedules as `good`; `easy` after an earlier-session pass
  schedules as `easy`.
- No interval exceeds `max_interval_days`.
- `completed` is refused at one pass when `completion_passes: 2`, accepted at two.
- A `hard`-only session leaves `last_session_errors` empty.
- A four-review card with no clean pass produces a leech line; a retired card
  leaves the agenda.
- `seba tune` round-trips through `goal.yaml` and refuses out-of-range values.
- A `goal.yaml` with no `settings` block loads with defaults.

## Open questions

1. **`max_interval_days` default.** 180 is a guess. 365 is the conservative
   alternative; FSRS's 36,500 is "no ceiling".
2. **`easy` damping rule.** The proposal needs one earlier-session pass. The
   stricter version never trusts `easy` on a card's first two reviews.
3. **Retention auto-tune.** Deferred above. If wanted anyway, it should steer on
   the learner's answer in the closing negotiation ("Y shaky — fair?") rather
   than on grades.

## Unrelated, found on the way

`subjects/_templates/analytic/profile.yaml` ends with two stray lines,
`</content>` and `</invoke>`, committed in `d28ed71`. Anyone copying that
template gets a profile that fails to parse. Two-line deletion, separate commit.
