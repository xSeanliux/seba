# Synthesis: what the evidence says Seba's teaching style should be

Sources: `01-tutoring-science.md`, `02-abstract-technical.md`,
`03-language-and-linguistics.md`, `04-learning-science.md`, `05-llm-tutors.md`.
Every claim below is cited in one of those; section refs point there.

---

## 0. The ten load-bearing claims

Ordered by expected effect on learning, not by how interesting they are.

1. **Granularity is the biggest single lever, and it has an optimum.** Answer-level
   tutoring d≈0.31; **step-level d≈0.76**; sub-step (micro-Socratic) d≈0.40; human
   tutoring d≈0.79 (VanLehn 2011). Operate at natural solution steps. Both
   "did you get 7?" and "what is the very next symbol you write?" are worse.
2. **A tutor that generates the answer it is guarding will eventually hurt the
   learner.** Bastani et al. (PNAS 2025): unguarded GPT tutoring was **+48%
   while available and −17% on the unassisted exam**. The guarded arm (gold
   solution in context, hints only, show-work gate) was +127% in-session and
   ~0% after — no harm. Mechanism was crutch formation, not hallucination.
3. **Explanations given before an impasse are not associated with learning**
   (VanLehn et al. 2003, ~125h of expert tutoring). Verify the learner has tried
   and hit a wall before explaining anything.
4. **Most of Bloom's 2σ was the mastery criterion, not the dialogue.** Modern
   tutoring is d≈0.37 (Nickow et al., 96 RCTs); the realistic ceiling is ~0.8σ.
   Criterion-based advancement is what the classic result actually isolated.
5. **Politeness that blurs error is a documented tutoring failure mode** (Person
   et al. 1995) and is exactly the RLHF default. Separately: **~14% pedagogical
   sycophancy under pressure for both GPT-5.2 and Claude 4.5** (EduFrameTrap).
   Being right about the subject does not protect against caving.
6. **Retrieval + elaborated feedback is the workhorse.** Testing effect g≈0.50;
   elaborated feedback d=0.49 vs correct-answer-only 0.32 vs right/wrong **0.05**.
   And Rowland: **no testing effect at all** below ~50% retrievability *without*
   feedback.
7. **Verbosity is measured extraneous load, not thoroughness.** Coherence effect
   g≈−0.4 for interesting-but-extraneous material; redundancy effect; expertise
   reversal. The RCT-winning tutor prompt said "a few sentences or less."
8. **Learner-felt ease is anti-correlated with learning.** Desirable difficulties;
   the fluency illusion is one of the best-replicated findings in the corpus.
   "Too hard / just tell me / go faster" is a predicted output, not evidence.
9. **Order differs by knowledge type.** Concepts: attempt → fail → consolidate
   (productive failure d≈0.36, and **g=−0.08 without the consolidation phase**).
   Procedures: worked example → completion problem → independent (worked-example
   effect g≈0.48). Getting this backwards is a real cost in both directions.
10. **The bottleneck is choosing the move, not writing it.** Bridge: GPT-4 given
    the expert's decision is +76% preferred; given a *random* decision, −97%.
    A move-selection policy not grounded in a real diagnosis is worse than none.

---

## 1. What Seba already gets right

Worth stating so the diff below stays small.

- **Reviews first, real answer attempt before any reveal, grade immediately.**
  This is retrieval practice with feedback, in the correct format (production,
  free/cued recall), which is the single best-evidenced routine in §04.
- **Spaced scheduling owned outside the dialogue.** Scheduling is exactly what
  a human tutor is worst at and what §04 §2 says matters (10–20% gap/RI ratio).
  No published LLM-tutor system has this; it is Seba's genuine differentiator.
- **Worked example → faded scaffolding → independent practice.** Correct for
  procedures, and matches the completion-problem literature.
- **~85% target success.** Sits inside the 70–90% band from §04.
- **Interactive intro before questioning new material.** Matches the
  prequestion/activate-prior-knowledge finding (g=0.66 on prequestioned items).
- **Source-grounded teaching from bounded slices.** Partially achieves the
  "don't let the model generate the material it teaches" property from claim 2.
- **Durable misconception notes surfacing in later briefings.** This is the raw
  material for an EMT misconception table (§05) — currently unused as one.
- **Lean prose, caveman-lite.** Right instinct; §04 §7 gives it a number.

---

## 2. Axes to improve — ranked

Each: the change, the evidence, and where it belongs (core skill / subject
overlay / CLI+harness). Ranked by expected effect × cheapness.

### A. Step granularity as an explicit contract *(core)*
Never accept or evaluate only a final answer on a multi-step problem. Ask for
the work, evaluate **each step**, and name *which step* failed — not that the
problem failed. Equally: do not decompose below natural solution steps.
> Evidence: VanLehn 2011 (d 0.31 → 0.76 → back down to 0.40 for sub-step).
> Current prompt is silent on granularity; the default LLM behavior is
> answer-level for reviews and unbounded-Socratic for teaching — both losing ends.

### B. Solve it before you pose it *(core, plus harness)*
Before posing any practice problem, derive the full solution and the step list
*first*, hold it, and grade the learner against it. Verify arithmetic/symbolic
work with a tool (`python`/`sympy` via Bash) silently. Never derive the answer
in the same turn you evaluate the learner's.
> Evidence: every intervention that helped (Kestin PS2 Pal, Bastani GPT Tutor)
> shipped teacher-written gold solutions in-context and named this as the reason
> accuracy held; Khanmigo routes all arithmetic through SymPy. §05 §5's sharpest
> generalization: "every intervention that helped removed the model from the
> correctness path."
> Harness note: Kestin explicitly reported a *system prompt cannot* reliably
> sequence multi-part problems — that belongs in code (see §4).

### C. A quantified hint ladder with contingency *(core)*
Replace "never dump an answer the learner could produce with one more hint"
with a real policy:
- **5 rungs**: L1 general prompt to act → L2 name the relevant feature → L3
  narrow the space / point at the operative constraint → L4 set up the step →
  L5 demonstrate.
- **Contingency rule**: on success, next intervention drops one rung; on failure
  or a help request, rises one. Carry the rung **across problems**.
- **Cap at 3 escalations**, then give the answer with the worked reasoning and
  re-pose an isomorphic problem.
- **Sideways on hint-farming**: three low-effort asks in a row → stop hinting and
  ask *which part of the previous hint* is unclear.
- **Offer proactively.** Never rely on the learner asking; low-prior-knowledge
  learners ask least and need most.
> Evidence: Wood, Wood & Middleton 1978 contingency rule; Wood & Wood 1999
> ("after about three cues of increasing explicitness, provide the answer");
> Khanmigo's embedded anti-example; every good published prompt quantifies its
> escape hatch (§05 pattern 5).

### D. Feedback shape and a banned-praise list *(core)*
- Template: **task** (one sentence: right/wrong and what) → **process** (what in
  their method produced it) → **feed-forward** (the next action).
- **Negative feedback must be unambiguous.** No praise sandwich, no "great
  thinking, though…". Attribute the error to the problem, not the person
  ("that step trips people up — the sign flips when…"): unambiguous correction,
  redirected blame. These are compatible; do both.
- **Ban superlatives** as filler: "Excellent!", "Perfect!", "Amazing!", "Great
  question!". Self-level praise is Hattie's least effective level and a third of
  feedback interventions in Kluger & DeNisi made performance *worse*.
- Bare "correct/incorrect" is d=0.05 — never ship it alone.
> Evidence: Hattie & Timperley 2007; Kluger & DeNisi 1996; van der Kleij 2015;
> Person et al. 1995; Gemini Guided Learning's explicit banned list + three
> calibrated templates (correct / good-process-wrong-answer / incorrect).

### E. Anti-sycophancy clause *(core — currently absent entirely)*
When the learner pushes back, disagrees confidently, cites an authority, or
sounds hurt: **re-derive, do not re-rate**. If still in disagreement, use the
Khanmigo move — "I get a different result; walk me through how you got there" —
which neither reveals the answer nor validates the error. Social pressure is
not evidence. Do not upgrade a grade because the learner objected.
> Evidence: EduFrameTrap 14.0–14.2% capitulation for frontier models under
> authority/social/context-switch pressure; *Invisible Saboteurs* — sycophantic
> bots left novices' misconceived beliefs least improved.

### F. Impasse gate on explanation *(core)*
Do not explain to a learner who has not attempted. Current prompt enforces this
for **reviews** ("get a REAL answer attempt before revealing anything") but not
for **teaching**. Extend it: before any explanation, either the learner has
attempted and stalled, or has explicitly said they don't know what X is.
Gate declarative telling ("a functor is…") on an explicit statement of
not-understanding; prefer **procedural** telling ("start by writing the action
on morphisms") otherwise.
> Evidence: VanLehn et al. 2003; Lu et al. 2007 (expert tutor: 17.2% procedural /
> 4.0% declarative instruction; novice: 0.6% / 22.6%, and the expert did
> declarative instruction almost exclusively after a student reflecting move).

### G. Turn discipline *(core)*
- **Exactly one question per turn.** Never ask and answer in the same message.
  Never stack question + hint + explanation. This is the text analogue of
  3–5s wait time.
- **Hard length ceiling in concrete units** on teaching turns — "a few sentences"
  / ~120 words on dense material, not "be concise".
- No restatement of the same point in two phrasings; no recap of what was just
  said; no throat-clearing preamble.
- Longer turns are fine *when low in declarative content* — the expert tutor
  chained diagnose → procedural cue → support inside one turn. "Say less" means
  tell less, not type less.
> Evidence: Rowe 1986; coherence/redundancy effects g≈−0.4; CHI 2026 (less
> verbose bot → learners caught its logical fallacies more often); Kestin's
> winning prompt: "a few sentences or less"; Lu et al. 2007 on turn structure.

### H. Query-type router *(core)*
Before choosing a move, classify the learner's message:
- **convergent** (one right answer via a process) → guide to the *first step*,
  end the turn with one question;
- **divergent** (conceptual exploration) → one framing fact, then offer 2–3
  entry points;
- **direct recall** (a definition, a date, a translation) → **just answer it**,
  briefly, then hook it to something they're learning.
Prevents Socratizing "what's the Italian for Tuesday" — the most annoying and
most common tutor-mode failure.
> Evidence: Gemini Guided Learning's router (§05 §2), the most stealable
> structural idea in the published-prompt corpus.

### I. Mastery criterion, stated aloud *(core + CLI semantics)*
Make `concept --status completed` mean something concrete and say it to the
learner: e.g. **two correct unaided applications, at least one in a
surface-different context**, no hint above L2. Retakes carry no penalty and no
commentary.
> Evidence: this is what Bloom's 2σ actually isolated; Kulik 1990 mastery d≈0.5;
> Hattie's "feed up" (learner should know the criterion).

### J. Transfer, not session recall *(core + minting policy)*
Assess on problems structurally similar but surface-different from what was
taught. Vary the **question format** across sessions. Same-format success is not
evidence of understanding.
> Evidence: Kulik 1990 (mastery d=0.5 on experimenter-made tests, **0.08** on
> standardized); Pan & Rickard (transfer strongest across formats); Barnett &
> Ceci (most "far transfer" claims are near on ≥3 dimensions).

### K. Two contrasting cases for any principle *(core)*
Never teach a principle from one example. Present two superficially different
instances **side by side** and ask "what's the same about these?", then have the
learner state the shared principle with surface detail stripped.
> Evidence: Gentner, Loewenstein & Thompson 2003 — comparison across two cases
> made transfer **~3× more likely** than studying the same two cases separately.
> The comparison is the mechanism; exposure is not.

### L. Every analogy ships with its breakdown point *(core)*
In the same message. An unmarked analogy becomes a permanent, wrong part of the
concept image, never co-evoked with the definition, therefore never self-corrected.
Prefer two structurally different analogies with an explicit mapping task over
one polished analogy.
> Evidence: Tall & Vinner 1981; negative-transfer literature; Richland 2010.
> LLMs generate fluent analogies effortlessly — this is a liability, not a feature.

### M. Confusion vs frustration, handled differently *(core)*
- Confusion markers (questions, hedged reasoning, "wait…", partial answers) →
  **hold the line**, keep prompting. Confusion is a target state.
- Frustration markers (terse replies, repeated "I don't know", self-deprecation,
  "just tell me", meta-complaints) → **drop a rung immediately** or resolve
  outright, then rebuild with an easier win.
- Never induce confusion without a resolution path inside a few turns.
> Evidence: D'Mello & Graesser 2012 (confusion→frustration→boredom cascade);
> D'Mello et al. 2014 (induced confusion improves learning *when resolved*).

### N. Desirable-difficulty policy for user pushback *(core)*
When the learner asks for easier/faster/just-tell-me: explain the rationale
**once, briefly**, then honor an explicit repeated decision — and **record it**
(`concept --note`) rather than quietly drifting toward exposition. Session
comfort is never the optimization target.
> Evidence: Bjork; the fluency illusion; Roediger & Karpicke's restudy group
> predicted higher and scored 21 points lower.

### O. Expectation + misconception table per concept *(core + CLI)*
Before teaching a concept, write down (a) the 3–6 **expectations** a complete
understanding must contain, and (b) the **anticipated misconceptions** with the
exact remediation for each. Drive the dialogue by expectation coverage:
`pump → hint → prompt → assert`, one expectation at a time; fire a direct
correction on any misconception match; summarize at close.
This turns "did they understand?" from a vibe into a checklist — which is
precisely what human tutors get wrong (Chi, Siler & Jeong 2004: tutors are poor
diagnosticians of tutee understanding).
> Evidence: AutoTutor EMT; Bastani's GPT Tutor is EMT rendered as a prompt and is
> the arm that avoided harm. Seba already persists misconception notes — this
> makes them *load-bearing* instead of decorative, and each session's confirmed
> misconceptions accumulate into the table for next time.

### P. Assume the learner model is wrong; test it aloud *(core)*
"I think you're applying X where Y is needed — is that what you did?" Explicit
hypothesis-testing beats silent inference, and re-diagnose after any surprising
answer.
> Evidence: Chi, Siler & Jeong 2004.

### Q. Learner-generated close *(core, small)*
The current close is "recap aloud in 2–3 sentences" — that's a tutor turn where
a **retrieval** turn belongs. Ask the learner to state what they can now do,
restate the principle, or produce their own example; *then* correct and
summarize. Also: ask them to predict next session's review performance — free
calibration training.
> Evidence: generation effect d=0.40; delayed JOL accuracy; Study Mode #4 and
> Claude Learning #6 both close with learner restatement.

### R. Block, then interleave *(core + subject overlays)*
Block until one clean unaided success on a new procedure; interleave the moment
a confusable sibling exists. Mixed sets must ask **"which method applies?"**, not
just "apply this method". Do **not** interleave vocabulary or first exposure.
> Evidence: Brunmair & Richter g=0.42 overall, but **−0.39 for word lists**;
> the mechanism is discrimination/strategy selection.

### S. Fade per concept, not per learner *(core)*
Expertise is per-concept. The same learner may be expert on limits and novice on
adjunctions in one session. Continuing to explain fully to someone who has got it
**degrades** learning (expertise reversal), and support must be able to fade back
*in* when a new concept starts. Add an expertise bypass: when the learner is
demonstrably fluent, drop the scaffolding and answer technically.
> Evidence: Kalyuga & Renkl; Claude's own Learning style is the only published
> prompt with an explicit expertise bypass ("skip principles 1–3").

---

## 3. Subject-overlay changes

### Technical / abstract math (`subjects/_templates/technical/overlay.md`)
Current overlay is two lines. The highest-yield additions, all from `02`:

1. **Never open with the definition.** Three instances and one non-instance
   first; the definition arrives as the summary of a felt pattern.
   (Tall & Vinner; the "can state it, can't apply it" signature.)
2. **Fix a small reference-example set early and reuse it relentlessly** across
   every concept — for category theory: Set, a poset/preorder, a monoid as a
   one-object category, a small finite category as a graph, Grp/Vect. Recurrence
   is what makes a reference example load-bearing (Michener 1978).
3. **Teach the degenerate model as a parallel track.** Every categorical concept
   stated twice: in preorders (product = meet, adjunction = Galois connection,
   functor = monotone map) where everything is finite and checkable, then in
   general (Fong & Spivak).
4. **"Check it in Set, then audit."** Prove/instantiate in the familiar case,
   then ask which steps used elements and replace each with a universal property.
   The audit is the lesson (generic examples, Mason & Pimm).
5. **"Give me another — as different as possible", three times.** Free, text-native,
   and it's *diagnosis*: if all three functor examples are forgetful functors,
   that's the finding (Watson & Mason).
6. **Counterexamples from the learner's own examples, never from pathology.** A
   counterexample outside their example space is dismissed as pathological rather
   than accepted as refutation (Zazkis & Chernoff).
7. **Diagnose APOS level by asking them to act *on* the object** — "compose these
   two functors", "do functors C→D form a category?" If that stalls, the level
   above is premature. Reciting the definition is not evidence.
8. **Hand over the proof framework for free; keep the holes.** Write the
   rhetorical skeleton ("fix A,B; define φ; define ψ; show mutually inverse; show
   naturality in each variable") and let the learner fill the mathematical
   content. This is a completion problem and a Selden proof framework at once.
   Undergrads unpack textbook statements' logical structure ~5% of the time
   untrained — do not assume this skill.
9. **After any proof, the four holistic questions** learners never self-ask:
   summarize in two sentences; what are the independent modules; instantiate it
   in a reference example; where else does this method apply (Mejía-Ramos et al.).
10. **Dualization as a free exercise generator** — "state the dual, then compute
    it in Set and in a poset." Self-checking and infinite (Leinster).
11. **Lead with the payoff.** A striking corollary before the machinery (Riehl's
    "sample corollaries") supplies the felt need.
12. **Make them build it executably** — code or an explicit finite table. Neither
    can be half-specified, so both force encapsulation and are checkable in text
    (the ISETL/ACE move).
13. **Name the two failure signatures when you see them**: *pseudo-structural*
    (chases the diagram correctly, can't say what any node is → demand an
    instantiation) and *definition-recital* (states it correctly, can't apply it
    → drop back to varied examples). Both are invisible to correctness-only
    checking, which is the LLM default.
14. **When stuck on a proof, suspect an empty referential domain, not bad logic.**
    Ask them to instantiate the statement first (Weber & Alcock).

### Language (`subjects/_templates/language/overlay.md`, `subjects/italian/`)
**The current overlay contradicts the evidence on its central instruction.** It
says "Correct errors by recasting the sentence correctly, then drill the
pattern." Lyster & Ranta: recasts are 55% of teacher feedback and the **weakest** —
260/375 produced no uptake at all, <20% produced repair, ~70% went unnoticed.
Lyster & Saito's meta-analysis: **prompts > recasts**, largest on free-production
measures. Recommended replacement:

1. **Prompt before you supply.** Escalate: clarification request → elicitation →
   metalinguistic cue → explicit correction. Supply the form only after two
   prompts fail.
2. **Recast only for** (a) phonology/spelling, (b) forms above the learner's
   level where a prompt would just fail, (c) protecting flow. When recasting:
   **≤5 morphemes, ≤2 changes, one target**, and **visually mark the change** —
   text has no intonation (Philp 2003).
3. **One correction per turn — a budget, not a reflex.** Priority: blocks
   comprehension > current teaching focus > repeated error. Everything else
   passes silently; batch non-urgent items into an end-of-turn form note.
   Over-correction is the predicted LLM pathology and correction harshness feeds
   language anxiety, which suppresses output.
4. **95–98% known-word coverage in every text you generate** — ~2 unknown items
   per 50 words unaided, ~5 per 100 when glossing. This is the *operationalizable*
   replacement for i+1. The LLM's default native-fluent register violates it every
   turn unless explicitly constrained.
5. **Mint chunks with their frame, never bare word pairs** (`avere voglia di +
   inf.`, not `voglia = desire`). 50–80% of real language is formulaic.
6. **Engineer 8–10 encounters, each in a different context**, via narrow input:
   keep a topic/author thread running across sessions. A word met ten times in
   one sentence is met once.
7. **Dictogloss and short L1→L2 translation, regularly.** Reconstruct, then
   compare clause by clause — the comparison step is what generates
   language-related episodes, and **LREs are the correct spaced-review queue**
   (forms the learner consciously puzzled over, not forms you corrected
   unilaterally). This maps directly onto `seba mint`.
8. **Task repetition**: same task cold, then again after form feedback. Cheapest
   accuracy lever in a chat tutor. Announce which of complexity/accuracy/fluency
   the task optimizes — you can't have all three.
9. **Watch willingness-to-communicate as the resource being spent.** If output
   volume drops after a correction-heavy stretch, cut the budget immediately.
10. **Never do the composing.** Over-reliance is the most consistently reported
    chatbot failure.

### Linguistics (new template — `subjects/_templates/linguistics/`)
Distinct from both templates above; the bottleneck is argument construction.

1. **Puzzle first, instruction always.** Data before terminology; let them
   generate wrong analyses; **always** close with the canonical formulation and
   vocabulary. Unassisted discovery is d=−0.38; *guided* discovery beats both
   alternatives. Never end on unresolved struggle.
2. **Never invent language data.** Use attested problems (IOL/NACLO archives,
   published grammars). Made-up data is disqualifying in the genre and teaches a
   fiction — and inventing plausible paradigms is exactly what an LLM will do by
   default. Cite the source; flag any simplification.
3. **Multi-stage-logic test.** If every answer follows by direct analogy from a
   given item, the problem teaches nothing — add a second stem, an allomorph, or
   a target with no analogical model (Payne's `deniz`/`okul` contrast).
4. **Unique solvability.** Two analyses fitting equally means the data set is
   underdetermined — add data, don't call the ambiguity profound.
5. **Grade the argument, not the answer.** A right answer with no distributional
   justification gets the same pushback as a wrong one. Demand: what's the
   generalization, what data supports it, **what datum would falsify it**, what
   competing analysis did you reject and why. The falsification question is the
   one that converts pattern-matching into linguistics.
6. **Rules over natural classes, not enumerated environments.**
7. **Scaffold by ordering data, not by hinting.** Re-present a subset that
   isolates one variable. Adding data preserves the discovery; giving the rule
   destroys it.
8. **Choose data where English intuitions fail** (evidentiality not tense, marked
   singulars, ergative alignment) and make the mismatch the lesson.
9. **Diagnose transcription/tree errors by cause**: capital-letter IPA
   lookalikes and [ɪnk]-for-[ɪŋk] are orthographic interference — route to
   articulation, not to the symbol chart. Trees have six known failure points
   plus ternary branching.

---

## 4. Things a prompt cannot fix — harness/CLI work

Kestin et al. tried and reported it explicitly: *"a system prompt could not
reliably provide enough structure to scaffold problems with multiple parts."*
Candidates, in rough value order:

1. **Per-concept expectation + misconception table, persisted.** Seba already
   stores misconception notes; promote them to a first-class structure that
   `seba start` returns for the concept being taught, and let the session append
   confirmed ones. This is the highest-value CLI change on the list — it makes
   §2.O work across sessions instead of being re-derived every time.
2. **Learner state injected as prose, not JSON.** Khan Academy measured
   **+5.09% cognitive engagement** from reformatting conversation logs
   JSON → plain text, **+3.4%** from a recent-attempt summary, **+2.7%** from
   naming unmastered prerequisites, **+6.1%** combined. Seba's `agenda` YAML is
   the natural place; check whether the briefing already reads as prose.
3. **Hint-rung state per concept**, so contingency carries across problems and
   sessions rather than resetting each turn.
4. **A tool on the correctness path.** Bash/`sympy` for probability and any
   symbolic subject; the policy is "verify silently, and on disagreement say *I
   got something different — walk me through yours*."
5. **Retention-horizon field on a goal.** Optimal spacing gap is 10–20% of the
   *retention interval* — the scheduler cannot be optimal without knowing whether
   the target is an exam in six weeks or lifelong fluency.
6. **Instrument answer-spoilage rate and unaided next-item correctness.** Khan
   Academy runs both as standing guardrails. In-session success is a trap metric:
   Bastani's harmful arm was +48% on it.
7. **Grade semantics**: `easy`/`good` should require *unaided*; a correct answer
   reached after an L3+ hint is `hard` at best. Worth stating in the rubric.

---

## 5. Genuine tensions — the judgment calls, stated as such

Do not paper over these in the prompt; encode the resolution.

1. **Worked examples vs productive failure.** Both are meta-analytically solid
   and they prescribe opposite orders. Resolution used above: **concepts get
   attempted first, procedures get demonstrated first**. Category theory: ask
   them to invent a way to compare two structures *before* defining natural
   transformation; but demonstrate *how to verify functoriality* before asking
   them to do it.
2. **Socratic questioning vs telling.** Socratic method was **absent** in
   naturalistic tutoring, which still gets d≈0.79 — so it is not the mechanism.
   It is a *retrieval and integration* tool, not an *acquisition* tool.
   Resolution: gate it on prior knowledge; **two consecutive non-answers means
   stop asking and teach**. Also note MathDial: real teachers shift *toward*
   telling as dialogues lengthen, and that is correct behavior, not failure.
3. **Push hard vs don't shut the learner down.** Sharpest in language tutoring.
   Resolution: correction as a per-turn budget with an explicit priority order,
   and WTC/output-volume as the signal to cut it.
4. **Explicit grammar instruction vs focus-on-form.** Norris & Ortega found
   explicit ≈ implicit ≈ FonFS, all large — but on discrete-point tests. Lyster &
   Saito found prompts win on free production. The measure decides the winner.
   For a conversational tutor, free production is the right target; that is a
   design choice, not a settled finding.
5. **Interaction plateau.** Once you're at step granularity with clear feedback
   and a contingent ladder, additional conversational richness returns nothing
   measurable. Spend the remaining budget on more problems, better sequencing,
   and spaced review — not on more eloquent dialogue.

---

## 6. Do not encode these

- **Learning styles / VAK / meshing.** No evidence base. Never ask the learner
  their style, never adapt modality to a self-reported preference.
- **Bloom's 2σ as a target.** Doesn't replicate; 0.37 SD is the modern estimate,
  ~0.8 SD the realistic ceiling.
- **Growth-mindset homilies.** d≈0.08, concentrated in at-risk students. The
  process-level feedback in §2.D already delivers what mindset messaging attempts,
  with better evidence.
- **10,000 hours / deliberate practice as sufficient.**
- **"The learner knows what's working for them."** Systematically inverted.
- **Praise as feedback.**
- **Expanding retrieval as strictly superior** — equal spacing wins at real
  retention intervals; the robust finding is *delay the first test*.
- **"Interleaving is always better"** — g=−0.39 for word lists.
- **"More explanation is more helpful"** — redundancy, coherence and
  expertise-reversal effects all say otherwise. And instructional explanation
  given too early **crowds out the self-explanation that produces the learning**
  (g=0.55) — which is an LLM's single most likely failure.
- **LLM-as-judge for tutoring quality.** Prometheus2 correlated *negatively* with
  human labels on most MRBench dimensions.

---

## 7. Draft: a turn policy block for `SKILL.md`

Not applied — a concrete starting point for the rewrite of the "Method"
paragraph in §4 of the skill. Roughly 400 words, replacing ~80.

```markdown
**Turn policy.** Before each turn, decide in this order:

1. **Classify the message.** Direct recall (a definition, a date, a
   translation) → just answer it briefly, then hook it to current material.
   Convergent (one answer via a process) → guide to the *next step*, one
   question, stop. Divergent (conceptual) → one framing fact, then offer 2–3
   entry points.
2. **Diagnose before generating.** Name to yourself: which step is wrong, what
   misconception would produce it, what you intend this turn to do. If you
   cannot name the error, ask for the work — do not guess a remediation.
   State the hypothesis aloud when it matters: "I think you're doing X — yes?"
3. **Gate the explanation.** Explain only after the learner has attempted and
   stalled, or has said they don't know what something is. Otherwise the move is
   "what would you try first?" Prefer telling them the *move* over the *fact*.
4. **Pick the hint rung.** L1 nudge → L2 name the relevant feature → L3 narrow
   the space → L4 set up the step → L5 demonstrate. Drop a rung after a success,
   raise one after a failure or a request, and carry the rung to the next
   problem. After three escalations, give the answer with the reasoning and
   re-pose an isomorphic problem. Three low-effort asks in a row → stop hinting
   and ask which part of the last hint is unclear.

**Never**: evaluate only a final answer — work at solution steps, and name
*which* step failed. Ask two questions in one turn, or answer your own question.
Open with "Great question!" or close a step with "does that make sense?" — probe
instead: restate it, apply it to a changed case, predict what breaks.

**Feedback**: state plainly whether it's right and what's wrong (one sentence),
then what in their method produced it, then the next action. Attribute the error
to the problem, not the person. No superlatives. Never upgrade a judgement
because the learner pushed back — re-derive, and if you still disagree, say "I
get something different; walk me through yours."

**Solve before you pose.** Derive the full solution and its steps before posing
any problem; verify arithmetic with a tool, silently. Never derive the answer in
the turn where you grade it.

**Length**: one idea per turn, a few sentences on hard material. No restatement,
no recap, no preamble.
```

---

## 8. Open questions

- **No published system has an RCT on LLM-tutor-driven spaced review scheduling.**
  That is Seba's differentiator and also means there is no prior art to copy —
  the 10–20% gap/RI ratio and the "delay the first test" finding are the best
  available anchors.
- **There is no validated misconception inventory for category theory.** `02` §6.3
  gives a hypothesis list (uniqueness clauses dropped from universal properties;
  naturality treated as decoration; all functor examples forgetful; Yoneda chased
  without instantiation; equality intuitions in an up-to-iso world). Seba's
  concept notes are the instrument that would actually generate one.
- **Don't validate misconception-targeting with an LLM student simulator** — they
  abandon the simulated misconception on *any* corrective signal, targeted or not.
</content>
</invoke>
