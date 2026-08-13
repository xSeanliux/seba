# Architecture synthesis: what to change in Seba, and what to leave alone

Sources: everything under `architecture/` — `06-curriculum-sequencing.md`,
`07-knowledge-structures.md`, `08-learner-modelling.md`,
`09-review-scheduling.md`, `10-its-architectures.md`. The companion sweep under
`teaching-style/` (synthesised in `00-synthesis.md`) covers how to teach a
*turn*; this one covers what the *system* should model, schedule, and decide.

**Headline: the skeleton survives, the joints don't.** The research was
commissioned with an explicit licence to pivot the whole product. It doesn't
justify one. Seba's three structural bets — code owns state and scheduling, the
LLM owns dialogue and authoring, state is plain text in git — come out
supported or unopposed. What comes out badly is a handful of *semantics* inside
that skeleton: what `done` means, who is allowed to declare it, how many cards
a session may create, and whether a session may touch more than one concept.

---

## 1. Where the five reports independently converge

Agreement across agents that never saw each other's work is the strongest
signal available here. Five findings cleared that bar.

### 1.1 An absorbing `done` is wrong — **all five reports**

- *06*: learning-trajectory research finds performance "does not simply increase
  monotonically. Rather students move back and forth along the trajectory";
  levels are "expected probabilities", students "advance and fall back". A
  spiral has no terminal state by construction.
- *07*: ALEKS's progress assessments **demote** items; monotone
  unseen→in-progress→done has no mechanism for forgetting or for discovering
  that `done` was premature.
- *08*: the state is absorbing *and has no duration* — `in-progress` carries no
  count of sessions held, so wheel-spinning is structurally undetectable.
- *09*: the object FSRS keeps alive (a card) is not the object the tutor
  certified (a concept). Three green cards ≠ a live concept.
- *10*: pure prerequisite graphs omit demotion; concept completion and card
  scheduling are two state machines that never talk.

Two independent literatures reach the same phrasing: **a concept's status
should be a decaying scalar, not a latch.**

### 1.2 The LLM must not be the sole, unchecked judge of mastery — three reports

This is the design's one genuinely unhedged bet.

- *08* is close to a direct test: GPT-4o judges **turn-level correctness** at
  near-human quality (0.93), but **mastery attribution** degrades to α ≈ 0.44,
  and the documented error mode is *scoring a turn correct when the student has
  said they don't understand*. So `seba grade` is fine; `--status completed` is
  the weak link.
- *10*: no system with measured effects let one component both teach and be the
  sole judge. The judge was always separable — a production-rule match, ALEKS's
  re-assessment on sequestered items, three-right-in-a-row on fresh items, a
  90% unit test someone else wrote. And there is a direct precedent for what
  goes wrong: **BKT predicted post-test scores until it was used to gate
  mastery, then stopped** (Corbett & Bhatnagar 1997 — Campbell's Law, measured).
  Seba is the tightest possible version of that loop: the same model teaches,
  chooses the practice problems, grades them, and certifies the outcome.
- *06*: PSI's meta-analytic success (+0.5σ) rests on gating by a **mastery
  test**, not by the tutor's impression.

### 1.3 One concept per session is the losing arm of a large, clean effect

*06* and *09* both land on Rohrer, Dedrick, Hartwig & Cheung (2020):
preregistered, cluster-randomised, 54 seventh-grade classes, four months,
**identical problems — only the order differed**. Unannounced test one month
later: **interleaved 61% vs blocked 38%, d = 0.83.**

Seba teaches exactly one concept per session, so every session is blocked by
construction. Note the boundary condition both reports flag: interleaving helps
for *confusable, related* skills where the question is "which applies?" — the
recommendation is not "shuffle the syllabus."

### 1.4 A hand-authored, TOC-derived, never-revised DAG is a prior, not a truth

- *07*: an LLM reading a table of contents is doing precisely what the **expert
  blind spot** literature identifies as the failure — deriving learner-facing
  sequence from the discipline's own organising structure. Nathan & Koedinger
  found expert-asserted prerequisite direction was *backwards* on a central
  algebra case. Learner approval cannot fix this: a learner new to the domain
  cannot detect an inverted edge. That is what makes it a blind spot.
- *06*: Confrey's own validated trajectories had **167 of 676 items (24%)
  revised** after empirical checking, and she frames validation as "an ongoing
  process". Every source that has built a real progression revises it.
- *07* again: **hard gating turns each authoring error into an unreachable
  concept** rather than a mildly suboptimal suggestion. Hard gates are "the
  single worst-supported choice in Seba's design *conditional on* the structure
  being LLM-authored and unrevised."

### 1.5 Do **not** build the sophisticated version — three reports, emphatically

The most useful convergence, because it closes expensive doors:

- *07*: ALEKS — a real knowledge space, 10²³ states, AUROC 0.88 state
  estimation, an item bank, Bayesian state search — achieves **Hedges' g = 0.05
  [−0.01, 0.20]** against ordinary classroom teaching. "Structural fidelity has
  a demonstrably poor conversion rate into learning gains."
- *08*: don't build BKT/PFA/DKT. Unidentifiable at n=1; deep KT's reported
  advantage largely evaporated once duplicated records (23.6% of rows) and
  scaffolding leakage were removed; dialogue-KT tops out ~0.76 AUC with a
  fine-tuned model and 21× more data than Seba will ever have.
- *10*: Baker's *Stupid Tutoring Systems, Intelligent Humans* — the systems that
  reached scale are "the furthest from the initial vision", and "the approaches
  used in practice are largely fairly simple… many systems in wide use depend on
  simple heuristics to assess student mastery, such as whether the student gets
  three right in a row."

And the calibration that governs everything: *08*'s meta-analytic table shows
ITS effect sizes shrinking as rigour rises (g ≈ 0.62 → 0.42 → **0.271**
validity-weighted), with the strongest moderators being **worked examples,
duration, outcome type, and immediacy of measurement — none of them properties
of the learner model.**

---

## 2. What the evidence says to KEEP

Stated explicitly so these don't get relitigated.

| Choice | Verdict | Why |
|---|---|---|
| Code owns state/scheduling/validation; LLM owns dialogue/assessment/authoring | **SUPPORTED** (*10*) | Every system separates a step loop from a task loop; LearnLM's three-layer architecture is the same shape and is the only LLM-tutor architecture with expert-rated evidence. `seba end` refusing while reviews are ungraded is a code-enforced invariant on exactly the kind of thing an LLM silently skips. |
| Content authored on the fly | **SUPPORTED — the best-supported choice in the system** (*10*) | Model-tracing ITS cost **200–300 authoring hours per instructional hour**; example-tracing was a breakthrough at 20–30:1. That tax is *why* older systems needed precise selection models. Generation at zero marginal cost dissolves the constraint, and enables a fresh transfer item per learner per session — economically impossible in 2005. |
| Plain-text git-backed state | **NO EVIDENCE, and none needed** (*10*) | Nothing evaluates storage layers. Indirectly favourable: maximally inspectable (Baker's whole thesis is that leverage comes from a human seeing the state), free longitudinal history, and aggregate analysis is meaningless at n=1. Don't build a database. |
| Conversational review rather than a quiz sheet | **SUPPORTED** (*09*) | QuizBot: >20% more correct answers with an *identical* scheduling algorithm, and 2.6× voluntary time on task. Do not "fix" review by making it look more like Anki. |
| Freeform prose notes as the misconception store | **SUPPORTED, ahead of the literature** (*08*) | Bug libraries lost historically — bugs migrate, libraries don't transfer, enumeration lost to generative accounts. And Khan measured JSON→prose as **+5.09%** with identical content. |
| A DAG at all | **SUPPORTED with a named ceiling** (*07*) | By Birkhoff's theorem a DAG *is* a quasi-ordinal knowledge space — exactly the `L₁` structure ALEKS's QUERY produces in Block 1, which Falmagne & Doignon call "sufficiently informative to be used in the schools and colleges." It's a principled v1, not an ad-hoc simplification. |
| Mastery criterion + free retakes (as now written in `SKILL.md`) | **SUPPORTED** (*10*) | Keller Plan mechanics, +0.5σ over 72 studies. The two load-bearing parts are a stated criterion that gates advancement and retakes that cost nothing. |
| Step-level error attribution | **SUPPORTED — best-evidenced single feature in the corpus** | d = 0.76 vs 0.31; already in `SKILL.md`. |

---

## 3. One correction to the research

*08*'s top recommendation — "inject the last session's transcript; the file
already exists at `sessions/NNN.transcript.md` and `Store.load` never opens it"
— is **wrong on the decisive detail.** `cli.py:79` writes
`NO_TRANSCRIPT = "(session conducted via Claude Code; no transcript captured)"`.
The file exists; it contains a placeholder. The dialogue lives in Claude Code's
own session log, which `seba` never sees.

So the Khan +5.09% result is not available for the price of a file read. The
options are (a) capture the transcript out of Claude Code, which is a harness
problem and not obviously in reach, or (b) have `seba end` write a longer,
structured prose recap than the current 3–6 sentence `--summary`. (b) is cheap
and captures most of the value; the evidence mildly prefers raw prose over a
summary, so the recap should be generous rather than terse.

---

## 4. Proposed changes

Ordered by expected effect ÷ cost. Nothing here has been implemented.

### Tier 0 — verified defects (cheap, code)

**0.1 — `MINT_CAP` 10 → ~3, and make it a budget against outstanding due load.**
`session/tools.py:15` caps minting at 10/session; `subjects/probability/profile.yaml`
allows 6 reviews/session. Ten cards in, six slots out — the queue diverges in
2–4 weeks and never recovers. Worse, once the review cap binds, **the cap
becomes the scheduler**: FSRS's intervals are systematically overrun, and it
then fits its DSR parameters from those corrupted reviews. Refuse to mint when
outstanding due load already exceeds review capacity. (*09*)

**0.2 — Compute the pace signal per concept, not only globally.**
`store.py:94-97` pools `recent_grades` across all concepts, so a learner acing
five concepts while grinding on a sixth reads as *push harder* — the opposite
of what's needed. Both the Khan result (+3.4% for per-item recent history) and
wheel-spinning detection operate on disaggregated evidence. Keep the global
hint; add per-concept. (*08*)

**0.3 — Drop `recognize` from the probability profile.**
Free recall > cued recall > recognition is among the most robust findings in the
retrieval literature. Recognition's only justification is transfer-appropriate
processing — when recognition *is* the criterion, which is true for
understanding heard Italian and false for probability. (*09*)

### Tier 1 — the consensus changes (schema + prompt, cheap)

**1.1 — Make `done` reversible and tie it to card health.**
Add `reopened` to the status literal; a concept whose cards are lapsing (any
card graded `again` in its last two reviews) re-enters the eligible set. This
closes the gap all five reports name, and gives ALEKS-style demotion without a
knowledge space. Cheapest continuous signal available: mean FSRS retrievability
across a concept's cards, computable from existing `Card` state with no fitting
— stated ceiling: it measures retention *of what was carded*, not transfer.

**1.2 — Require an independent, delayed check before `completed`.**
The single highest-value change. Gate completion on one item the teaching turn
cannot see: a card minted earlier for that concept, or a stored transfer problem
written at teach time, answered unaided in a **later** session. This is ALEKS's
progress assessment, PSI's unit test, and ASSISTments' fresh-item rule — all of
them cheap heuristics rather than models, and the one insurance policy every
predecessor bought. Add a required `evidence` field naming the exchange that
demonstrated it, which moves the judgement from mastery-attribution (α 0.44)
toward turn-correctness (0.93).

**1.3 — Add a stuck-check on `in-progress` concepts.**
Wheel-spinning is *the* defined failure mode of mastery-learning systems, runs
6.6–24.2% of student-skill pairs, and a **single-feature logistic regression on
correctness percentage hits 93.5% precision / 77.1% recall after 4
opportunities** — within a few points of Random Forest. Don't build a
classifier. Compute sessions-since-started plus correctness rate over that
concept's grades; on fire, put one line in the briefing and force `teach_src` to
change. Today `agenda.py:69` picks the first `in-progress` concept forever, so
the failure is silent and unbounded.

**1.4 — Soft vs hard prereq edges.**
`strength: hard | soft`, default soft; the frontier admits anything whose *hard*
prereqs are done and whose soft prereqs are done-or-waived. This removes the
mechanism by which one wrong LLM-authored edge makes a concept permanently
unreachable, and matches how KST actually treats prerequisites (thresholded
probabilities, "practical certainty", fast-tracking of uncertain items).

**1.5 — Surface *unmastered* prereqs of the teach concept in the briefing.**
Khan: **+2.7% next-item correctness across 1.36M threads**, the second-largest
measured production win, and it is pure prompt content over state Seba already
has. `agenda.py` unions `teach_src.prereqs` into `scope` but never says which of
them isn't done. One line: *"prereqs not yet done: X, Y — offer a 2-minute
review first."*

**1.6 — Hint-aware grading, as a hard input.**
Anki's manual names the one habit FSRS cannot absorb: grading *Hard* when you
actually forgot. An encouraging conversational tutor grading a learner who
needed two hints is a machine built to commit that error. The PR already
reworded the rubric ("`hard` — correct after any hint above L2"); make the hint
rung an explicit recorded input to the grade rather than a remembered one.

**1.7 — Learner picks from the frontier; system computes the frontier.**
Present 2–4 eligible concepts with one-line rationales rather than taking the
first node in topological order. This is exactly ALEKS's outer-fringe mechanism.
Achievement cost ≈ zero (learner control g = 0.05) and it buys engagement, which
for a voluntary adult learner is the binding constraint on whether sessions
happen at all. Explicitly do **not** let the learner override prereqs or declare
concepts done — those are the choices learners reliably get wrong.

**1.8 — Tag concepts with a KC type and route method off the tag.**
`kc_type: fact | concept | procedure | principle`, set at authoring time. Facts →
spaced retrieval, minimal dialogue. Procedures → worked example then fading.
Principles → self-explanation and argumentation. KLI's asymmetry claim is the
sharp bit: elaborate dialogue "may **fail to support** simple knowledge" like
constant-constant associations — i.e. Socratic dialogue is predicted to be
*actively inefficient* for Italian vocabulary and notation conventions. Seba
already owns both tools (dialogue and spaced review); it just doesn't route
between them. Note this generalises the concept-vs-procedure split already
shipped in `SKILL.md`.

**1.9 — Make the syllabus revisable, with named operations.**
Four ops the tutor may propose, surfaced to the learner in batch: insert a
missing prerequisite, split a concept, mark a concept already-known, drop a
concept as out-of-goal. Insert-missing-prerequisite is the highest-frequency
real defect in a TOC-derived DAG and should ship first. *Do not* attempt to
learn edges from Seba's own logs: because Seba always teaches in DAG order, its
logs are maximally confounded — structure discovery collapses from F1 0.46 to
**0.17** under curriculum-ordered sequences. Record explicit violation and
waiver events instead; waivers are what create the counterfactual variation.

**1.10 — Prompt the syllabus author against the expert blind spot.**
"For each edge, state whether A is required to *understand* B or is merely
conventionally taught first — mark the latter soft. Do not assume formalism
precedes application." Plus an adversarial second pass looking for inverted
edges, which is far likelier to catch them than learner approval.

### Tier 2 — moderate, worth doing after Tier 1 lands

**2.1 — Diagnose the entry point at goal creation.** The most underrated finding
in the sweep: learning *rate* is astonishingly uniform (~0.1 log-odds,
~7 opportunities per component to reach 80%), while *starting* knowledge varies
enormously (55% vs 75% between lower and upper halves). Therefore **locating the
learner dominates optimising the order.** A placement pass that marks concepts
already-known is worth more than any amount of DAG polish.

**2.2 — Focal concept + interleaved practice.** Keep one concept for new
instruction; draw practice from 2–4 related recent/due concepts, and ask "which
method applies?" rather than "apply this method". Order the review set for
concept diversity instead of oldest-due-first. (d = 0.83, and the queue-ordering
half is a scoring tweak.)

**2.3 — Concept-level free-recall review track.** "Tell me everything you
remember about conditional independence." Free recall is the strongest retrieval
format (g ≈ 0.81) and captures the relational material no card holds. This is
the natural repair for "concepts are never revisited, only their cards": put
concepts on a slow FSRS track with free recall as the item type.

**2.4 — Retention horizon → FSRS `desired_retention`.** The one hard parameter
in the spacing literature is gap ≈ 10–20% of the retention interval; FSRS
already exposes the knob and defaults to an infinite-horizon assumption.

**2.5 — A negotiation turn, and evidence in `seba view`.** Before close: *"My
read is you've got X solid, Y shaky, Z untouched. Fair?"* Negotiated learner
models are the OLM variant with the best evidence — they improve both model
accuracy and the learner's self-assessment — and it's the only mechanism that
handles recency, evidence weighting, and *absence* of evidence. It is also the
cheapest available correction for an over-confident `done`. Render the notes
behind each status so the model is scrutable rather than merely viewable.

**2.6 — Log the tutor's own decisions.** Hint rung reached, tell-vs-elicit,
transfer-vs-same-format. Min Chi induced a **d = 0.8** policy improvement from
103 students' data; a single learner over a year yields thousands of turns.
Costs one field now, impossible to reconstruct later.

### Tier 3 — explicitly do not build

Recorded so the doors close deliberately.

- **Knowledge space / state lattice.** ALEKS with the full machinery: g = 0.05.
- **BKT / PFA / deep knowledge tracing.** Unidentifiable at n=1; the reported
  advantages don't survive clean data.
- **Affect state.** Detectors are weak (F ≈ 0.63–0.68) and affect is volatile at
  minute scale. Persist the *behavioural* residue instead — skipped grades,
  abandoned sessions, repeated deferrals — and fold it into the one stuck-check
  rather than building a second subsystem.
- **More substep/Socratic machinery.** Substep vs step: **d = 0.16, 0%
  reliable, k = 11**. Human vs substep: d = −0.12. If anything, prune.
- **Smaller units justified by "microlearning".** That evidence base is a
  low-tier venue with I² ≈ 70% and no publication-bias handling. It cannot carry
  a design decision.

---

## 5. Does the README need to change?

Barely, and not in the way the licence to pivot anticipated.

The README's architectural claims — "owns a curriculum (concept graph) and
longitudinal learner state… Code owns state, scheduling, and validation; Claude
Code owns dialogue and grading" — are the parts that came out **supported**. The
one phrase that now overclaims is the implication that the concept graph is a
settled plan. After Tier 1 it is a revisable prior with soft edges and
reversible statuses, and the README should say so.

The honest summary for the top of the file: *Seba is a step-level conversational
tutor with a code-owned scheduler and a revisable concept graph.* Everything the
research contradicts is one layer below that sentence.

---

## 6. Open questions the literature does not answer

- **No RCT isolates where state lives** (code vs model), and none tests
  LLM-as-sole-assessor over a long horizon. Tier 1.2 is insurance against a risk
  that is *documented by analogy* (Campbell's Law in BKT) rather than measured
  in this setting.
- **No head-to-head on generated variants vs fixed cards** under a spaced
  schedule. The indirect case against fixed cards is strong (response
  congruency: transfer d 0.58 → 0.28 when the response form changes), but
  varying the surface breaks FSRS's per-card difficulty estimation. The
  resolution — schedule the component, render the surface — is Duolingo's
  architecture and is a real project, not a tweak.
- **The ITS evidence base is STEM-only.** VanLehn states it outright: "not
  language, music, sports." Nothing in the interaction-plateau result licenses
  any conclusion about Italian.
- **Two months of Seba's own data would settle the grader question** more
  decisively than any citation here: if true retention runs far above the
  desired-retention target, the LLM is over-grading. Instrument it.
</content>
</invoke>
