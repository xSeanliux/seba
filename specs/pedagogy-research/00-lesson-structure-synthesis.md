# Lesson-structure synthesis: within a session, and across a run of sessions

Sources: `lesson-structure/11-lesson-architecture.md`, `12-session-timing.md`,
`13-session-chaining.md`, `14-practitioner-lesson-craft.md`. Companion syntheses:
`00-synthesis.md` (how to teach a turn), `00-architecture-synthesis.md` (what the
system should model and schedule).

**Headline: structure is not the lever. Proportion and criterion are.**

Every named phase model — Gagné's nine events, Hunter's ITIP, 5E, gradual
release — is unvalidated *as a whole*. No study in any of the four sweeps tests
session phase ordering against learning outcomes. What survives scrutiny is a
different kind of fact: how session time is *divided*, what *criterion* governs
moving on, and which single moves carry measured effects. Seba's current
five-step protocol is already close to the evidence on ordering; the gaps are
that it has no success criterion, no segment-boundary retrieval, and it
generates its highest-signal assessment at the close and then throws it away.

---

## 1. What is actually load-bearing

Ranked by evidence quality across all four reports.

**1. Proportion beats order.** The single best-evidenced structural fact is a
time allocation: effective teachers spend far more of a lesson on questioning,
guided practice, checking and error correction than on exposition — 23 vs 11
minutes out of 40, and *9 questions per 40 minutes marks the least effective
teachers* (Rosenshine 2012). If exposition is the biggest block, the session has
drifted toward the empirically distinguishing feature of worse instruction.

**2. ~80% success rate.** The most actionable number in the corpus. 82% vs 73%
separated the most from least successful teachers; ~80% is the stated optimum.
Below it, errors get consolidated — which is expensive to undo. Seba currently
targets "~85%", which is close, but as a *static aspiration*, not a runtime
control loop.

**3. Retrieval at every segment boundary, not only at the end.** Szpunar et al.
2013: cumulative test **90% vs 76% (restudy) vs 68% (untested)**, mind-wandering
halved (19% vs 39%/41%), *and* lower anxiety and lower perceived load. The
restudy control rules out mere re-exposure — it must be learner retrieval, not
tutor recapitulation. Roughly every 4–6 minutes of exposition. This is the
highest-value within-session change available.

**4. The learner produces the consolidation, and the gaps feed forward.**
Converges independently from four traditions: the Japanese *matome* phase,
Webster's expert 1:1 closure sequence, Rosenshine's "ask students to explain
what they have learned", and SNAPPS/one-minute-preceptor's generalise step.

**5. Attempt-before-instruction — conditionally.** g = 0.36 (CI 0.20–0.51),
rising to 0.58 at high fidelity, and *stronger for adults and domain-specific
outcomes* — Seba's exact case. Boundary conditions are sharp and are given in §3.

**6. Stop when the material is done.** Overlearning past mastery gave **zero**
benefit at one *and* four weeks; durability flattens past ~3 correct recalls;
the same number of retrievals spread across sessions beats concentrating them.
A 25-minute session that covered its material is correct, not lazy.

**7. Open with review, selected by relevance rather than due-ness.** Rosenshine's
daily review is 5–8 minutes, and it prioritises *where errors were made last
time*. FSRS due-ness is orthogonal to what today's lesson needs.

**8. End on success.** Affective slope over an episode explains **35–46% of
variance** in remembered and forecasted pleasure up to 7 days later. This buys
adherence, not learning — which for a voluntary learner is the higher-leverage
variable.

---

## 2. Where the four reports converge

| Finding | 11 | 12 | 13 | 14 |
|---|:--:|:--:|:--:|:--:|
| Open with retrieval on prior material | ● | ● | ● | ● |
| Learner writes the consolidation, not the tutor | ● | ● | ● | ● |
| End on success; hand off a named next practice | ● | ● | ● | ● |
| Diagnose/extract an attempt before teaching | ● | ● | | ● |
| Guided practice is the largest block | ● | | | ● |
| Interleave against *confusable* siblings, not randomly | | | ● | |
| Periodic synthesis session, no new material | ● | | ● | |

Four-way agreement on the opening move, the closing move, and who writes the
summary. That is a strong signal for structure that is otherwise weakly evidenced.

---

## 3. Tensions resolved

**Attempt-first vs model-first.** *14* says the attempt-first camp (TTT, TBLT,
one-minute preceptor, SNAPPS, Lepper's expert tutors, chess) contains every 1:1
expert-observation study and both RCT-tested micro-frames; model-first (PPP,
high-dosage protocols, cognitive apprenticeship) is classroom- and
novice-oriented. But the worked-example effect is real and `SKILL.md` already
encodes "procedures → demonstrate first". *11* gives the principled boundary,
and it is the expertise-reversal line:

> **Attempt first when**: the target is conceptual, the learner has *some*
> relevant prior knowledge, and element interactivity is manageable.
> **Demonstrate first when**: the target is novel notation or vocabulary, or
> element interactivity is high.

Either way the attempt must be followed by consolidation contrasting it with the
canonical method — without that phase the effect disappears. This supersedes the
flat "concepts → attempt, procedures → demonstrate" rule now in `SKILL.md`,
which is the right instinct with the wrong discriminator: the discriminator is
*prior knowledge and element interactivity*, not concept-vs-procedure.

**A correction to `00-synthesis.md` rule 6.** I wrote "never re-quiz an item
successfully retrieved earlier in the same session." Too strong. Karpicke &
Roediger: repeated *testing* after first correct recall had a large one-week
effect where repeated *studying* had none. Correct rule: **massed re-ask is
wasted; a spaced re-touch later in the same session is cheap and mildly
positive**, with a ceiling of ~2–3 successful retrievals before the item goes to
the scheduler.

**Interleaving is discriminative, not temporal.** Carvalho & Goldstone: the
active ingredient is discriminative contrast, not spacing. So shuffling topics
across sessions buys nothing FSRS isn't already providing. Interleaving must run
against *confusable siblings* — which requires a `confusable-with` edge, not a
random mix. This sharpens the vaguer "interleave practice" item in
`00-architecture-synthesis.md` §2.2.

---

## 4. Proposed session shape

Deltas from Seba's current protocol, which is already close on ordering.

```
0  Continuity opener          1 min   — pick up the named next-practice from last time
1  Daily review               5-8 min — due items ∪ prereqs of today ∪ last session's errors
2  Bridge                     1-2 min — name the prior knowledge today builds on
3  Attempt-before-instruction 4-6 min — CONDITIONAL (see §3 boundary)
4  Intro + worked example     6-10 min— small steps, pre-warn likely errors,
                                        A QUESTION AT EVERY SEGMENT BOUNDARY
5  Guided practice           10-20 min— LARGEST BLOCK. Process questions, not answer checks.
                                        Governed to ~80% success: <75% drop a rung and re-model,
                                        >90% step up or move on early
6  Independent practice       5-10 min— same material, minimal intervention, stop at 2-3 hits
7  Matome                     3-5 min — end on a correct item, learner writes the summary,
                                        tutor compares to canonical, GAPS BECOME REVIEW ITEMS
8  Record + name next practice 1 min  — a procedure, not a quantity
```

Two constraints that matter more than the phase list: **guided practice must be
the largest block**, and **do not add phases** — the gains are in interaction
granularity, not session architecture.

### Session length
25–45 minutes of active work; hard stop around 60. The lower bound is set by
*content*, not stamina. No RCT of tutoring session duration exists; every number
here is triangulated and should be a soft default. Interaction density matters
more than duration: a 45-minute session with a question every 4 minutes is
better supported than a 20-minute monologue.

---

## 5. Proposed multi-session shape

A **unit** = one complexity level, ending when the learner can perform an
unsupported whole task at that level — **state-terminated, not count-terminated**.
Roughly 10 sessions in a **7 ordinary : 2 synthesis : 1 checkpoint** ratio.

- **Unit open**: the simplest complete version of what this unit buys you;
  introduce a running problem; full support (worked example end to end).
- **Ordinary sessions**: the shape in §4, support fading across the unit.
- **Synthesis sessions** (~every 4–5): *no new concept*. Render the concept graph
  back to the learner — "explain how these connect" — and advance the running
  problem now that the tools exist.
- **Checkpoint** (unit end): cumulative, unscaffolded, samples the whole unit
  rather than the FSRS-selected subset, explicitly low-stakes, and **writes back
  to concept statuses**. This is also the natural home for the independent
  delayed mastery check proposed in `00-architecture-synthesis.md` §1.2.
- **Support resets upward at each unit boundary** — otherwise fading for six
  sessions then raising complexity produces a failure that reads falsely as
  learner regression.

Roughly 30% of sessions teach no new material. That is the uncomfortable
implication of the review literature, and Rosenshine says it plainly: material
not adequately practised and reviewed is easily forgotten.

**Cadence.** ~25–45 min, a few times a week, at least one night between sessions
on the same new material. Bahrick 1993: **13 sessions at 56-day gaps ≈ 26
sessions at 14-day gaps** — session count trades directly against gap width.
Baddeley & Longman: the distributed group learned most efficiently and was
*least satisfied* — the fluency illusion, now at schedule level.

**Returning after a lapse should be a first-class session type**: backlog triage,
no new concept, explicit re-orientation, zero guilt framing. Lally et al.: missing
one occasion "did not materially affect the habit formation process"; Duolingo's
*more forgiving* streak raised engagement. This is precisely what a streak app
structurally cannot do and a stateful tutor can.

---

## 6. Changes to make, ordered

**Cheap, prompt-level:**
1. **Success-rate governor** on practice — a running criterion, not a fixed count.
   `<75%` drop a rung and re-model; `>90%` step up or end early.
2. **A question at every segment boundary** during exposition — learner retrieval,
   not tutor recap.
3. **Recap becomes a graded artefact.** Learner writes it, tutor compares against
   a canonical summary, and the gaps are minted as review items. Today this
   signal is generated and discarded — it is the session's highest-signal
   formative assessment.
4. **End on a success.** If the last practice item failed, insert one the learner
   can clear before closing.
5. **Split guided from independent practice**, and make guided the larger.
6. **Hand off a procedure, not a quantity.** "Read this paragraph aloud, stop at
   every word you hesitate on, write those five down" — not "20 minutes of
   Italian". Practice duration and repetition count did not predict retention;
   strategy did.
7. **Replace the flat concept/procedure rule** for attempt-vs-demonstrate with the
   prior-knowledge × element-interactivity boundary in §3.
8. **Stop when done.** Cap at 2–3 successful retrievals per item; a short session
   that covered its material is finished.
9. **Invert the feedback ratio further.** Expert studio teachers: corrective
   feedback frequent, specific, brief; praise *rare, unexpected, and large* when
   it comes. `SKILL.md` currently only bans superlatives.

**Schema / state:**
10. **Widen the review selection rule** to due ∪ prereqs-of-today ∪ last-session
    error sites. Requires errors to be locatable in the notes — currently
    freeform, so this is the one soft dependency.
11. **`confusable-with` edges**, so interleaving is discriminative rather than random.
12. **Session types** — ordinary / synthesis / checkpoint / return-after-lapse —
    with a counter since last synthesis.
13. **A per-session proximal goal**, set at the close of the previous session and
    evaluated at the close of this one.
14. **`support_level` per unit**, faded within a unit and reset up at unit open.

---

## 7. Honest limits

- **No study tests session phase ordering against outcomes.** The convergence
  across seven unrelated traditions on "diagnose first, generalise and hand off
  last" is informative, but it is convergent *convention*, not a tested variable.
  Everything in §4 is either a transplanted mechanism (retrieval, generation,
  desirable difficulties) or expert craft.
- **Named phase models are omission checklists, not blueprints.** Hunter's ITIP
  is a documented cautionary tale about template-as-compliance.
- **Do not encode**: the 10–15 minute attention span (the most-cited source
  "barely discusses student attention at all"); the 6-minute MOOC figure (it
  measured page navigation in a zero-interaction medium); primacy/recency within
  a lesson (no primary study; list recency dies after ~30s of filled delay);
  Zeigarnik-style ending mid-task (doesn't replicate, and the meta-analytic
  finding is *rumination*); prescriptive time-of-day rules (>80% of studies find
  no chronotype main effect in adults 18–45).
- **Sourcing note:** report 12 hit the session's WebSearch quota and worked
  through Europe PMC, OpenAlex, Semantic Scholar and Unpaywall instead, flagging
  the two effect sizes it could not independently verify. Report 11 could not
  retrieve one EEF headline figure. Both disclosed rather than papered over.
