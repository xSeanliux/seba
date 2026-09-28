---
status: accepted
---

# The scheduler owns the schedule

py-fsrs decides when a card comes back, and Seba never changes that by itself.
Seba's own rules layered on top (pulling a concept's cards in early after a
`hard`, reopening a done concept after one `again`) were the cause of cards
recurring for weeks and of concepts being completed three times over, while the
scheduler underneath was behaving correctly. So Seba now limits itself to
feeding the scheduler the right inputs and telling the tutor what happened.

The learner can still steer. They do it through the scheduler's inputs
(retention target, interval ceiling, per-concept emphasis), and the scheduler
still computes every date. The one direct override is setting a concept's
emphasis to `more`, which makes its cards due now; it happens only because the
learner asked.

## Considered options

- **Detect cards that keep failing and flag them for rewriting.** The scheduler
  has no such notion, and a failing card already comes back soon.
- **Treat an early `easy` as `good`.** Overrides a grade the scheduler was
  given. The interval ceiling and emphasis cover the case from the input side.
- **Reopen a concept automatically on repeated `again`.** Replaced by a line in
  the briefing; the tutor proposes re-teaching and the learner decides.
- **Tune the retention target from measured recall.** Grades are assigned by a
  language model reading a conversation. Inflated grades would read as high
  recall and lengthen intervals further.

## Consequences

A done concept stays done while its cards are failing, until the learner agrees
to reopen it. The briefing is what keeps that visible.
