# Learner Modelling: what to persist between sessions, how to update it, what it buys

Scope: student-model taxonomies, knowledge tracing and its critiques, open learner models, deployed-LLM-tutor evidence, affect/wheel-spinning, forgetting, lifelong models, LLM-era modelling, and the size of the adaptivity effect. Ends with verdicts on Seba and ranked recommendations.

Seba's persisted state, verified against the code at `d101dd9`:

| What | Where | Notes |
|---|---|---|
| Concept status (`unseen`/`in-progress`/`done`) | `syllabus.yaml`, `models.py:23` | Three-valued, tutor-set |
| FSRS card state per item | `items.jsonl`, `models.py:56` | `fsrs` dict is opaque; v6 `Card.to_dict()` = `{card_id, state, step, stability, difficulty, due, last_review}` — **no reps/lapses counter** |
| Per-concept freeform notes | `notes.md`, `store.py:136-144` | Markdown `## <concept_id>` sections, newest-first insert; 3 newest per in-scope concept injected (`agenda.py:99-104`) |
| `last_hint` | last session's `next_session_hint` | one sentence |
| `recent_grades` | `store.py:94-97` | **all** review grades from the last 3 outcome files, not "last N" |
| Pace hint | `agenda.py:47-56` | >0.9 good/easy → push-harder (quota 5); <0.7 → step-back (quota 2); else steady (3) |
| Transcripts | `sessions/NNN.transcript.md` (`store.py:127`) | **written but never read back** — the data exists, nothing consumes it |
| Per-review grades + notes | `sessions/NNN.outcomes.yaml` | `GradeReview.note` persisted per item; only the grade is ever re-read |

Two corrections to the framing in the task: notes *are* keyed per concept (not flat), and per-item review history *is* on disk in the outcomes YAMLs — it is simply not loaded. That materially changes the cost of several recommendations below from "expensive" to "cheap".

---

## 1. Overlay vs buggy/perturbation models

**Overlay** (Carbonell's SCHOLAR, 1970; Goldstein's genetic graph, 1979). The learner model is a subset of the expert model: for each element of domain knowledge, does the student have it or not. Goldstein's *genetic graph* extended this by linking rules with evolutionary relations (generalisation, specialisation, analogy, refinement/correction) so the model represented not just *what* is known but *how* the student's rule set could evolve into the expert's — an early argument that the topology of the domain, not just per-node flags, is part of the learner model.

**Buggy / perturbation models.** Brown & Burton's BUGGY (1978) rejected the overlay assumption that student errors are absence of knowledge. They modelled multi-digit subtraction as a procedural network and generated errors by *perturbing* subprocedures, producing a catalogue of ~100+ precisely specified "bugs" (e.g. *smaller-from-larger*: always subtract the smaller digit from the larger regardless of position). DEBUGGY did offline diagnosis, IDEBUGGY online. ([Brown & Burton 1978, Cognitive Science](https://onlinelibrary.wiley.com/doi/pdf/10.1207/s15516709cog0202_4); [Burton, *Diagnosing Bugs in a Simple Procedural Skill*](https://exquisitive.com/library/DiagnosingBugsSimpleProceduralSkill.pdf))

**What the bug library bought.**
- Genuine diagnostic power: a large fraction of systematic subtraction errors in thousands of students were reproduced by a small library of composable perturbations. Error patterns are not random noise.
- The empirical result that misconceptions are *structured and shared* across learners, which is the entire basis for later misconception-targeted instruction and for distractor design in assessment.
- A teacher-training artifact: BUGGY was used to train teachers to recognise error patterns, which is arguably its most durable contribution.

**Why the field moved away.**
1. **Bug migration / instability.** Students do not hold a bug the way a program holds a defect; they shift among bugs across problems and sessions. Brown & VanLehn's *repair theory* ([Cognitive Science 1980](https://onlinelibrary.wiley.com/doi/abs/10.1207/s15516709cog0404_3)) explained this: the student has a stable but *incomplete* procedure; on some problems that procedure reaches an **impasse**; the student then applies a local **repair** (skip the step, back up, refuse, substitute an operator); different repairs at the same impasse surface as different bugs. So a bug is a *derived, situational* observation, not a stable latent trait. Cataloguing outputs of a generative process is the wrong abstraction level.
2. **Generativity beat enumeration.** VanLehn's Sierra ([*Mind Bugs*, MIT Press 1990](https://mitpress.mit.edu/9780262512909/mind-bugs/)) learned procedures inductively from worked examples and *derived* the bug catalogue rather than storing it, reproducing more of the observed error data than case-by-case analysis. Once you can generate bugs from an impasse+repair theory, the library is a compiled artifact, not the model.
3. **Slips are indistinguishable from bugs.** DEBUGGY could not diagnose performance noise; inconsistent students produced unresolvable diagnoses. This is exactly the problem BKT later handled statistically with guess/slip parameters.
4. **Authoring cost does not amortise.** The library is per-domain, per-representation, and hand-built by cognitive scientists. Subtraction is unusually tractable (finite, procedural, unambiguous). Nobody produced a comparable library for, say, probability reasoning or L2 morphology. DEBUGGY was also limited to skills composable from its predefined subprocedures — it could not induce a genuinely new erroneous procedure from behaviour.

**Carry-forward for an LLM tutor:** the *misconception catalogue* idea survives; the *runtime diagnostic search over a bug library* does not. What is worth persisting is the observation ("this learner conflated P(A|B) with P(B|A) on 2026-07-14"), tagged and retrievable, not a claimed stable buggy procedure.

---

## 2. Knowledge tracing

### 2.1 BKT (Corbett & Anderson 1995)

Per knowledge component (KC), a two-state HMM over latent binary mastery, four parameters:

| Param | Meaning |
|---|---|
| p(L₀) | prior probability the skill is already known |
| p(T) | probability of transitioning unknown→known at each opportunity |
| p(G) | probability of a correct answer while not knowing (guess) |
| p(S) | probability of an incorrect answer while knowing (slip) |

Mastery is inferred by Bayes update after each observation; classic Cognitive Tutor mastery threshold p(Lₙ) ≥ 0.95. Notably, **standard BKT has no forgetting term** — p(known→unknown) is fixed at 0.

**Known pathologies.**
- **Identifiability**: wildly dissimilar parameter sets fit the same data equally well, with different pedagogical consequences (Beck & Chang 2007). Formally characterised in [van de Sande, *Properties of the Bayesian Knowledge Tracing Model*](https://files.eric.ed.gov/fulltext/EJ1115329.pdf).
- **Degeneracy**: fits where p(G) + p(S) > 1, i.e. a student is *more* likely correct when not knowing the skill. Usually clamped by hand (p(G) ≤ 0.3, p(S) ≤ 0.1).
- **Local minima** in EM fitting; sensitivity to initialisation.
- **Multi-KC items**: BKT is defined for single-KC observations. The usual workarounds (joint pseudo-skill, or replaying the observation once per KC) each distort the evidence. ([Xiong et al. 2016 §2](http://beardeer.github.io/wpi_public_html/papers/edm_2016_xiong_zhao.pdf))

**Variants worth knowing.**
- **Individualised BKT** — per-student p(L₀) and/or p(T) (Pardos & Heffernan 2010, [*Modeling Individualization in a Bayesian Networks Implementation of Knowledge Tracing*](https://link.springer.com/chapter/10.1007/978-3-642-13470-8_24)). Modest gains; per-student priors help more than per-student learn rates.
- **Contextual guess and slip** — Baker, Corbett & Aleven 2008, [*More Accurate Student Modeling through Contextual Estimation of Slip and Guess Probabilities*](https://link.springer.com/chapter/10.1007/978-3-540-69132-7_44): estimate p(G)/p(S) *per action* from context features (response time, help requests) rather than as skill constants. This is the important conceptual move: **whether a correct answer counts as evidence of knowing depends on how it was produced.** A fast unaided correct answer and a correct answer after three hints are not the same observation.
- **KT-IDEM** (Pardos & Heffernan 2011) — per-item difficulty inside BKT.

### 2.2 Logistic alternatives: AFM and PFA

**AFM** (Additive Factors Model; Cen, Koedinger & Junker 2006, [*Learning Factors Analysis*](https://link.springer.com/chapter/10.1007/11774303_17)): logistic regression, logit of correctness = student ability + Σ over KCs of (KC easiness + KC learning rate × opportunity count). Counts *opportunities*, not outcomes — so it is a pure practice-curve model and cannot use the fact that the student got them wrong.

**PFA** (Pavlik, Cen & Koedinger 2009, [*Performance Factors Analysis — A New Alternative to Knowledge Tracing*](https://digitalcommons.memphis.edu/facpubs/8350/)): replaces the opportunity count with separate counts of **prior successes** and **prior failures** per KC, each with its own weight, plus item difficulty. Handles multi-KC items natively (just sum the terms), has a convex objective (guaranteed global optimum, unlike BKT's EM), and drops the latent-state interpretation — it predicts correctness, not "mastery".

Head-to-head, PFA and BKT are roughly comparable in predictive power across many studies (Pavlik et al. 2009; Gong, Beck & Heffernan 2010; Baker, Gowda & Corbett 2011; Pardos et al. 2011/2012), with PFA usually ahead when items carry multiple KCs. In Xiong et al.'s clean comparison PFA beat BKT on every dataset by a wide margin (AUC .70–.73 vs .60–.64).

### 2.3 Deep Knowledge Tracing and the correction

**Piech et al. 2015** (NeurIPS, [*Deep Knowledge Tracing*](https://papers.nips.cc/paper/5654-deep-knowledge-tracing)): an LSTM over one-hot (skill × correctness) inputs, reported AUC ≈ 0.86 on ASSISTments 2009-10 vs ≈ 0.67 for BKT — a headline "+25% AUC" that drove ~a decade of deep-KT papers.

**Xiong, Zhao, Van Inwegen & Beck 2016, [*Going Deeper with Deep Knowledge Tracing*](http://beardeer.github.io/wpi_public_html/papers/edm_2016_xiong_zhao.pdf) (EDM'16)** — the correction. Reimplementing DKT in TensorFlow and re-preparing the data, they found three defects inflating the original result:

1. **Duplicated records.** "Large chunks of records are duplications" in the public ASSISTments 2009-10 skill-builder file — **123,778 of 525,535 rows (23.6%)** were duplicates, acknowledged as an error by the ASSISTments team.
2. **Scaffolding problems mixed with main problems.** 73,466 scaffolding rows that BKT/PFA exclude by convention were fed to DKT, giving it extra information.
3. **Repeated response sequences from multi-skill tagging.** Multi-KC problems were replicated once per skill tag, so an RNN sees skill B's answer immediately after skill A's answer *to the same problem* — a near-deterministic repeat. Splitting predictions confirmed it: on repeated data points DKT scored **AUC 0.97, r² 0.74**; on the leading (genuinely predictive) records, **AUC 0.77, r² 0.23**.

Cleaned results (5-fold, student-level CV):

| Dataset | Torch DKT | TF DKT | PFA | BKT |
|---|---|---|---|---|
| 09-10 (a) raw-ish | 0.79 | 0.81 | 0.70 | 0.60 |
| 09-10 (b) no scaffolding | 0.79 | 0.82 | 0.73 | 0.63 |
| 09-10 (c) joint skills, no repeats | 0.73 | 0.75 | 0.73 | 0.63 |
| ASSISTments 14-15 | 0.70 | 0.70 | 0.69 | 0.64 |
| KDD Cup 2010 | 0.79 | 0.79 | 0.71 | 0.62 |

r² on 14-15: DKT 0.10, PFA 0.09, BKT 0.06.

Read carefully: **DKT reliably beats BKT. DKT does not reliably beat PFA.** On the two cleanest datasets (09-10c and 14-15) the DKT/PFA gap is 0.00–0.02 AUC and 0.01–0.04 r². The KDD advantage the authors themselves attribute to a handicap they imposed on PFA (item difficulties had to be coarsened to skill difficulties to avoid leakage). Independent work in the same period found BKT+forgetting and well-featurised logistic models matching DKT; [KTbench](https://arxiv.org/html/2403.15304v2/) later showed leakage bugs are endemic to the deep-KT benchmarking pipeline itself. Absolute r² of 0.10–0.30 means **all** of these models explain a small minority of variance in individual responses.

**Implication for Seba:** the entire deep-KT branch is unavailable anyway (no per-student corpus of thousands of graded responses), and the evidence says the ceiling over a simple counting model is small. The defensible target is PFA-class: count successes and failures per concept, weight them, and don't pretend to a latent state.

---

## 3. Open Learner Models

The learner model is made inspectable — and sometimes editable or negotiable — by the learner. Core references: Bull & Kay's SMILI framework ([*A Framework for Designing and Analysing Open Learner Models*, IJAIED 2007](https://www.researchgate.net/publication/220049165)) which classifies OLMs by *what* is opened, *to whom*, *how*, and *why*; and Bull's retrospective [*There are Open Learner Models About!* (IEEE TLT 2020)](https://dl.acm.org/doi/abs/10.1109/TLT.2020.2978473).

**A spectrum of openness, in increasing cost and increasing evidenced benefit:**

| Level | What the learner can do | Evidence |
|---|---|---|
| Viewable | See the model | Supports planning/self-monitoring; weakest effects |
| Scrutable | Ask *why* the model says that | Kay & Kummerfeld's line; supports trust/accountability |
| Editable | Assert a correction | Risk: learners over-claim |
| **Negotiated** | Model changes only after learner and system justify positions and reach agreement | Strongest evidence |

**What the evidence supports.**
- OLMs support metacognitive activity — planning, self-monitoring, reflection — and are used for navigation/lesson sequencing. The systematic review of OLMs for SRL in higher education ([Hooshyar et al., *Computers & Education* 2020](https://www.sciencedirect.com/science/article/abs/pii/S0360131520300774)) finds OLMs mainly support **cognition**, less **metacognition** and **motivation**, and almost never **affect** — i.e. the field's own coverage is skewed toward "show a skill meter".
- **Negotiation is the part with the strongest results.** [Bull & Kay, *Negotiated learner modelling to maintain today's learner models*, RPTEL 2016](https://pmc.ncbi.nlm.nih.gov/articles/PMC6302918/): negotiation improves *model accuracy* (learners recognise wrong entries and propose fixes) **and** self-assessment accuracy — in the CALMsystem evaluation the negotiated condition showed significantly greater improvement in self-assessment accuracy than an inspection-only condition — and prompts metacognitive behaviour. Crucially for a long-lived model, negotiation is how the paper proposes handling **recency of evidence, weighting of evidence from heterogeneous sources, and absence of evidence** — the three things an automatic updater cannot resolve alone.
- **Uncertainty visualisation matters.** [Evaluating the Effect of Uncertainty Visualisation in OLMs on Students' Metacognitive Skills (AIED 2017)](https://link.springer.com/chapter/10.1007/978-3-319-61425-0_2) — showing the model's confidence, not just its point estimate, changes metacognitive behaviour. A model that shows "done" with no confidence band invites over-trust.
- **Accuracy is a precondition for trust.** [Persuading an Open Learner Model (ITS 2016)](https://link.springer.com/chapter/10.1007/978-3-319-39583-8_34) and the negotiation literature both note that a visibly wrong OLM is worse than none: it burns credibility for the whole system.

**Evaluating `seba view` against this.** It is a **viewable, non-scrutable, non-editable, non-negotiated** OLM (`src/seba/ui/view.py`, `ViewData`/`ViewConcept` in `models.py:170-197`). It shows: status per concept, DAG layer, card counts, due counts, `est_sessions`, aggregate stats, frontier, and the raw `recent_grades` string. It shows **no uncertainty**, **no evidence** (the per-concept notes that justify a status are not rendered), and offers **no path to disagree**. So Seba sits at the weakest rung of the OLM ladder — the rung the literature credits with real but small effects — while the rung with the best evidence (negotiation) is, uniquely, *nearly free* in a conversational tutor: the tutor can simply ask. That is the single largest gap between Seba's design and the OLM literature.

---

## 4. What state actually paid off in a deployed LLM tutor

**Khan Academy / Khanmigo — the strongest production evidence available.** ([How Khan Academy Is Building a Better AI Tutor, 2026](https://blog.khanacademy.org/how-khan-academy-is-building-a-better-ai-tutor-our-most-recent-learnings/); methodology: [GrowthBook writeup](https://www.growthbook.io/blog/how-khan-academy-optimizes-ai-tutoring-with-experimentation)). ~20 substantive A/B tests, >15M tutoring threads over six months, primary metric **next-item correctness** (did the student get the next problem right after tutoring), plus guardrails. Cumulative: **+6.1% next-item correctness**.

| Intervention | Metric | Effect | n (threads) |
|---|---|---|---|
| Summary of student's **recent problem-solving history** (how many attempted, which right/wrong) | next-item correctness | **+3.4%** (97.5% prob. better) | 608,000 |
| **Surfacing unmastered prerequisite skills** + offering brief review | next-item correctness | **+2.7%** (98.5% prob. better) | 1,360,000 |
| Conversation log as **plain text instead of JSON**, extended to all threads on that skill in prior 24h | cognitive engagement | **+5.09%** (99.4% prob. better) | — |
| Full in-session conversation log, **as JSON** | performance | **no measurable improvement** | — |
| Examples of problem types for the skill in the prompt | next-item correctness | **no effect** | — |
| More relevant follow-up content links | next-item correctness | **n.s.** (shipped for latency) | — |
| Faster model / concise responses / narrowed agent scope / verification pre-check | latency | −0.3s (1.35M), −3s (352k), −0.4s + 50% less answer-giving, −0.3s (1.04M); accuracy held | various |

**Four lessons that transfer directly.**
1. The two state features that worked are exactly **recent performance history** and **unmastered prerequisites**. Both are cheap prompt-context features over data the system already had.
2. **Formatting is not cosmetic.** The *same* conversation history was worth nothing as JSON and worth +5.09% engagement as prose. This is a first-class finding and the cheapest lever in the entire literature.
3. **Recency window mattered**: 24 hours of related threads, not all history.
4. Content-side enrichments (examples, links) did nothing. Effects come from *learner state*, not more domain material.

**Other measured evidence.** Deployed-LLM-tutor RCTs with learner-state manipulations are otherwise thin. Tutor CoPilot (Wang et al. 2024, human tutors with LLM assistance) reports ~+4pp mastery, +9pp for lower-rated tutors, but manipulates tutor support rather than persisted learner state. The Khan results are, as of now, the only large-scale published A/B evidence isolating *what learner state to put in an LLM tutor's context*. There is also a counterweight worth holding: [*Faster Completion, Less Learning*](https://arxiv.org/pdf/2605.21629) finds generative AI reduced study time on math problems and the knowledge built — i.e. process metrics can improve while learning does not, which is a caution about Khan's next-item-correctness proxy too (it is measured immediately, on the next item, and is partly a "did the tutor leak the method" signal).

---

## 5. Affect, motivation, and wheel-spinning

### 5.1 Affect

Sensor-free detectors of boredom, frustration, confusion and engaged concentration, built from interaction logs, are established but not strong: best F-measures around **boredom 0.632, frustration 0.677, confusion 0.667** (Baker et al., Cognitive Tutor Algebra). Key findings:

- [Baker, D'Mello, Rodrigo & Graesser, *Better to be frustrated than bored* (IJHCS 2010)](https://www.sciencedirect.com/science/article/abs/pii/S1071581909001797): **boredom is the affective state most damaging to learning** — it is persistent and it precedes gaming the system. **Brief confusion is positively associated with learning; extended confusion is negative.** Frustration is negatively but less strongly associated with outcomes.
- **Gaming the system** (Baker et al. 2004 onward): exploiting the interface (hint-spamming, systematic guessing) rather than learning. Robustly associated with poorer learning; detectable from logs; frustration is associated with it and boredom precedes it. See [Gaming the System — Affect Detectors and Student Persistence](https://www.globallearningcouncil.org/posts/gaming-the-system-affect-detectors-and-student-persistence-and-learning-in-computer-based-learning-environments/); [Carelessness and Affect in an ITS (IJAIED)](https://learninganalytics.upenn.edu/ryanbaker/AIED-D-13-00017_Revised%20v2.pdf).
- [Generalisable sensor-free frustration detection (UMUAI 2024)](https://link.springer.com/article/10.1007/s11257-024-09402-4) shows the detectors are now portable across environments, but accuracies remain modest.

**Is affect worth *persisting*?** The distinction the literature draws is between **state affect** (within-session, minutes-scale, the thing detectors target and interventions respond to *now*) and **trait-like dispositions** (persistent boredom with a topic, avoidance of a concept). Persisting a raw affect label across weeks is not supported — affect is volatile and the detectors are weak. Persisting *behavioural consequences* of affect is: repeated disengagement on a specific concept, sessions abandoned, requests to skip. In a 1:1 dialogue tutor, the detector problem is also much easier than in a click-stream ITS: the learner says "I'm lost" in words. The relevant persisted quantity is a small counter, not an emotion.

### 5.2 Wheel-spinning — the most directly applicable finding

[Beck & Gong, *Wheel-Spinning: Students Who Fail to Master a Skill* (AIED 2013)](https://link.springer.com/chapter/10.1007/978-3-642-39112-5_44): mastery learning assumes the student *can* eventually master the skill with enough practice. Wheel-spinning is the violation — a student practising a KC extensively without reaching mastery. Their operationalisation: **failing to get three correct in a row within the first 10 practice opportunities.** It is not rare, and it predicts long-run harm; [Seven-Year Longitudinal Implications of Wheel Spinning and Productive Persistence (AIED 2021)](https://link.springer.com/chapter/10.1007/978-3-030-78292-4_2) tracks the consequences downstream.

[Zhang, Huang, Wang, Lu, Fang, Stamper, Fancsali, Holstein & Aleven, *Early Detection of Wheel Spinning* (EDM 2019)](https://files.eric.ed.gov/fulltext/ED594575.pdf) — three datasets (MATHia CL1 132,551 student-KC pairs; CL2 419,832; Geometry 8,175), two operationalisations, six detectors:

- **Prevalence** is operationalisation-dependent: three-correct-in-a-row gives 6.6% / 0.56% / 10.2%; Predictive Stability++ (BKT-based when-to-stop) gives 24.2% / 2.17% / 13.2%.
- **The two criteria agree on under 50% of wheel-spinning cases** (14.1% CL1, 41.6% Geometry). Wheel-spinning is not a well-defined ground truth; pick a criterion and own it.
- **Detection is cheap and works early.** A **logistic regression on the single feature "correct response percentage"** reached **93.5% precision / 77.1% recall after just 4 practice opportunities** (PS++ criterion). Random Forest at step 4: (77.2%, 63.5%) under three-correct-in-a-row, (90.8%, 81.4%) under PS++. Features involving correctness dominate importance; response-time and assistance-score features add less.
- **Cold start is real**: below ~20% precision/recall in the first 2–3 opportunities under three-correct-in-a-row. Don't judge before ~4 attempts.

**Why this is the sharpest finding for Seba.** A concept sitting at `in-progress` across many sessions *is* the wheel-spinning signal, and Seba currently has no representation of "how long has this been in-progress", no per-concept correctness rate, and no trigger. The literature says a **single correctness-rate feature with a threshold, applied after ~4 opportunities**, is most of the achievable detection. That is a `sum()` over data already on disk.

---

## 6. Forgetting and decay in student models

- **BKT has no forgetting** (p(forget) pinned to 0). Adding a forget parameter (BKT+F) is a known and effective extension, and BKT+forgetting is one of the simple baselines that matches DKT in several replications.
- **PFA/AFM have no time term** — only counts. Both are practice-curve models, blind to the calendar.
- **DASH** (Difficulty, Ability, and Study History; Lindsey, Shroyer, Pashler & Mozer, *Improving students' long-term knowledge retention through personalized review*, Psych Science 2014) is the bridge: a logistic model with time-windowed counts of prior study and prior success, which lets one model both learning and forgetting. The classroom study (middle-school Spanish, semester-long) is one of the few demonstrations that a *personalised* review schedule beats massed and generic-spaced review on delayed retention.
- **DAS3H** ([Choffin, Popineau, Bourda & Vie, EDM 2019](https://arxiv.org/pdf/1905.06873)) adds multiple KCs and per-KC time-window features to DASH, and beats DKT-family models on several datasets — again, a logistic model with good features.
- **Half-Life Regression** ([Settles & Meeder, ACL 2016](https://research.duolingo.com/papers/settles.acl16.pdf)) — Duolingo: fit the *half-life* of a memory from past performance plus lexeme features; deployed at scale. Related: [Adaptive Forgetting Curves for Spaced Repetition](https://pmc.ncbi.nlm.nih.gov/articles/PMC7334729/), [Ebisu](https://fasiha.github.io/ebisu/).
- **FSRS** (which Seba uses) is in this family: DSR (difficulty/stability/retrievability), stability = the time to 90% retrievability, fit from grade sequences.

**Does the KT model duplicate the scheduler?** Partly, and the split is principled:

| | Question answered | Grain | Time-aware |
|---|---|---|---|
| Spaced-repetition scheduler (FSRS) | *When should I re-show this item?* | item | yes, centrally |
| Knowledge tracing | *Does the learner know this concept well enough to move on / to teach the next thing?* | KC/concept | usually not |

They overlap on "retention of an item" and diverge on "readiness to progress". A system with FSRS does **not** need a separate forgetting model for items. What FSRS does not provide is a *concept-level* readiness estimate: FSRS stability is per-card, and 6 cards on a concept with high stability is not the same claim as "understands the concept". Aggregating card-level retrievability up to concept level is a legitimate cheap proxy (and better than a hand-set flag), but it measures *retention of what was memorised*, not *transfer*. This is the real limit and it should be stated rather than papered over.

---

## 7. Long-term / lifelong learner models

Judy Kay and Bob Kummerfeld's programme ([*From data to personal user models for life-long, life-wide learners*, BJET 2019](https://bera-journals.onlinelibrary.wiley.com/doi/abs/10.1111/bjet.12878); [Lifelong Learner Modelling for Lifelong Personalized Pervasive Learning](https://www.semanticscholar.org/paper/118a7c6702d3e32ac75cfd87b52320bede9cc500); [Scrutable adaptation, AH 2006](https://dl.acm.org/doi/10.1007/11768012_2)) argues:

- **Ownership and portability.** The model should be the learner's asset, stored under their control, usable by many systems. This is a design position, not an empirical result, but it is the dominant one in the OLM community and it is unusually easy to honour in a local-first CLI.
- **Scrutability** — the learner can answer "why does the system believe this about me?" — is the mechanism that makes a long-lived model trustworthy. A long-lived model accumulates more chances to be wrong, so the older it gets the more it needs justification attached to each claim.
- **Staleness/recency.** The negotiation paper ([RPTEL 2016](https://pmc.ncbi.nlm.nih.gov/articles/PMC6302918/)) names it explicitly: data becomes outdated quickly, especially when recent activity isn't reflected in the model, and evidence from different sources deserves different weights. Their proposed resolution is human-in-the-loop (learner or teacher adjusts weights), because no automatic decay rate is defensible across sources.
- **Infrastructure gap.** The literature's own assessment is that there is *no* generic infrastructure for long-term personal learner-model storage and transfer — lifelong learner modelling is still an open problem, not a solved one ([Towards Personal infrastructure to manage long term open learner models](https://www.researchgate.net/publication/308762252)).

**How old evidence should be discounted, in practice.** Three defensible policies, none requiring a model: (a) **time-window counts**, the DASH/DAS3H approach — count successes and failures within windows (last day / week / month / all-time) and let a weight per window be fit or hand-set; (b) **cap and expire** — keep the k most recent observations per concept, which is what Seba already does for notes (3 newest) and grades (last 3 sessions); (c) **timestamp everything and let the reader discount** — for an LLM consumer this is remarkably effective, because "(4 sessions ago)" in prose is a discount signal the model can act on. (c) is nearly free and Seba does not do it: notes carry `[sNNN]` session tags in the file but the briefing injects the note text with only the concept id.

---

## 8. Natural-language / LLM-era learner modelling

The central question for Seba: **is an LLM's judgement that "the student has mastered this" calibrated?** The best evidence is [Scarlatos, Baker & Lan, *Exploring Knowledge Tracing in Tutor-Student Dialogues using LLMs* (LAK'25)](https://learninganalytics.upenn.edu/ryanbaker/Dialogue_KT_LAK_25-2.pdf), which is almost exactly Seba's setting: knowledge tracing over open-ended tutoring dialogue.

Setup: GPT-4o annotates each dialogue turn with (i) student response correctness and (ii) Common Core KC tags; KT models are then trained on the annotations. Datasets CoMTA (small, 4–5 labelled turn pairs per dialogue) and MathDial (21× larger). Human evaluation with 3 former math teachers over 30 dialogues / 166 turn pairs.

**Results (accuracy / AUC / F1):**

| Method | CoMTA AUC | MathDial AUC |
|---|---|---|
| BKT | 52.50 | 64.19 |
| DKT | 53.20 | 63.22 |
| DKVMN | 46.81 | 60.42 |
| AKT | 51.40 | 63.31 |
| SAINT | 47.81 | 60.10 |
| simpleKT | 51.25 | 63.83 |
| DKT-Sem (DKT + text embeddings) | 61.82 | 66.18 |
| **LLMKT** (fine-tuned Llama-3.1-8B) | **65.79** | **76.71** |

**What this establishes:**

1. **Classical KT collapses on dialogue.** On CoMTA every conventional KT method fails to beat the majority-class baseline (Acc 57.83, AUC 50.0). Sparse, short, semantically-loaded dialogue is not the data KT was built for.
2. **Textual content is the signal.** Merely swapping DKT's learned embeddings for sentence embeddings of the turns (DKT-Sem) beats every classical method. Fine-tuning an LLM on the KT objective beats everything.
3. **Ceiling is low.** Best dialogue-KT AUC ≈ **76%**, versus >80% for standard KT on problem-response data. The authors attribute this to short dialogues, unpredictable student behaviour, and many turns being irrelevant to any KC. **Tracing knowledge from conversation is intrinsically harder than tracing it from graded problems.**
4. **What GPT-4o is good at vs bad at** (Table 4, human eval): judging **whether a student turn was correct** — human-assigned score **0.9317/1**, 3-annotator exact overlap 0.8434; final-turn correctness accuracy **GPT-4o 75.82% vs human annotators 85.56%** — i.e. close to but below human. Judging **which KCs a turn involves** — score **3.2831/4**, overlap only **0.3494**, Krippendorff's α **0.4383**. Error analysis: GPT-4o under-assigns KCs (misses required ones), errs most on turns needing arithmetic verification, mislabels turns that should be "not applicable", and **sometimes labels a turn correct when the tutor asks whether the student knows a concept and the student says they do not** — i.e. it confuses a claim of understanding with a demonstration of it.
5. **Zero-shot LLM mastery estimation was not viable.** The authors are explicit that since LLMs are not pretrained on the KT task, "we cannot expect them to do well in this zero-shot setting" — hence fine-tuning. The mastery numbers above are from a *fine-tuned* model; nobody in this paper claims an off-the-shelf LLM's unaided mastery judgement is calibrated.
6. **Learning curves are only weakly recovered.** Of the 15 most frequent KCs, 5 trended upward in predicted mastery, 5 downward, 5 flat — a power-law-of-practice signature only partially visible.

**Reading it for Seba.** The mapping is direct and unflattering in one specific place. Seba's tutor does exactly two judgement tasks: (a) **grade a review exchange** (`GradeReview`, again/hard/good/easy) — this is turn-level correctness judgement, the task GPT-4o does at near-human level (0.93 score); and (b) **declare a concept `done`** (`UpdateConcept.status_change`) — this is a *mastery* judgement over a whole KC, which is (i) the task with poor KC-attribution agreement (α 0.44), (ii) the task that needed a fine-tuned model and still only reached 0.66–0.77 AUC, and (iii) the task where the documented failure mode is *believing a student's claim of understanding*. Seba trusts the model for both, but only (a) is supported.

Corroborating general calibration work: LLMs are broadly overconfident, with GPT-4o-class models reasonably calibrated only in the 70–100% confidence band and smaller models badly overconfident ([Mind the Confidence Gap, 2025](https://arxiv.org/html/2502.11028v1)). And Scarlatos et al. note (citing recent work) that LLMs are ineffective at anticipating, parsing and following flawed reasoning — precisely the skill misconception diagnosis requires.

**Learner memory graphs / LLM-as-tracer generally.** LLM-KT variants ([LLM-KT, 2025](https://arxiv.org/html/2502.02945v1)) and multi-agent "judger/critic" KT designs exist, but all of the credible ones either fine-tune or supply the LLM with explicit structured performance history. Nothing in this literature supports "let the model remember in prose and trust the summary". The reliable pattern is: **LLM extracts structured observations from dialogue → cheap statistical model aggregates them over time → structured state is rendered back into the prompt as prose.** Both ends are LLM work; the middle is arithmetic.

---

## 9. How much does adaptivity actually buy?

| Comparison | Effect | Source |
|---|---|---|
| ITS vs conventional/classroom instruction | **g ≈ 0.62** | [Kulik & Fletcher, RER 2016](https://journals.sagepub.com/doi/abs/10.3102/0034654315581420) |
| ITS vs teacher-led large group | **g = 0.42** | [Ma, Adesope, Nesbit & Liu, JEP 2014](https://eric.ed.gov/?id=EJ1049508) |
| ITS vs non-ITS computer-based instruction | **g = 0.57** | Ma et al. 2014 |
| ITS vs textbooks/workbooks | **g = 0.35** | Ma et al. 2014 |
| ITS vs **individualised human tutoring** | **g = −0.11 (n.s.)** | Ma et al. 2014 |
| ITS vs small-group instruction | **g = 0.05 (n.s.)** | Ma et al. 2014 |
| Human tutoring vs **step-based** ITS | **d = 0.21** | [VanLehn, *The Relative Effectiveness of Human Tutoring, ITS, and Other Tutoring Systems*, Ed. Psychologist 2011](https://www.tandfonline.com/doi/abs/10.1080/00461520.2011.611369) |
| Human tutoring vs **substep-based** ITS | **d = −0.12** | VanLehn 2011 |
| ITS in US K-12, validity-weighted | **g = 0.271** (18 studies, 77 ES, 11 systems) | [Leite et al. 2025](https://arxiv.org/pdf/2511.04997) |

**Three conclusions, in order of importance for Seba:**

1. **The "2 sigma" premise is dead.** VanLehn 2011's central result is that human tutoring is *not* d = 2.0 better than computer tutoring; it is ~d = 0.2, and substep-based systems match or slightly exceed human tutors. What separates effective from ineffective tutoring is **granularity of interaction** — whether the learner is asked to produce and gets feedback at each *step*, not whether a sophisticated learner model is behind it. Interactivity is the active ingredient.
2. **ITS effect sizes shrink as study rigor rises**: g ≈ 0.62 (broad meta-analysis) → 0.42 (vs teacher-led) → 0.271 (validity-weighted US K-12). The strongest moderators found by Leite et al.'s MetaForest are **worked-out examples, intervention duration, outcome type, and immediacy of measurement** — *none of them properties of the learner model*.
3. **The adaptivity component itself is the weakest-evidenced part.** The comparison the task asks for — adaptive vs otherwise-identical non-adaptive — is under-studied, and where it exists the delta is small. The [simulation-based-learning meta-analysis on adaptivity vs adaptability (*Educational Research Review* 2024)](https://www.sciencedirect.com/science/article/pii/S1747938X2400071X) finds adaptive scaffolding + adaptable task progression descriptively largest, but **only for high-prior-knowledge learners, not low-prior-knowledge learners**. Ma et al.'s own moderator analysis finds no reliable benefit from more sophisticated student-modelling machinery. VanLehn's ITS-vs-ITS comparisons repeatedly show step granularity dominating model sophistication.

**The blunt version:** most of the measured benefit of an ITS comes from *frequent step-level interaction with feedback and adequate practice*, which Seba already does by construction (it's a dialogue with graded exchanges plus FSRS). The marginal return on elaborate learner modelling is small and not well demonstrated. The exceptions — where modelling clearly pays — are narrow and specific: **choosing what to review when (spacing)**, **not letting a stuck learner stay stuck (wheel-spinning)**, and **surfacing unmastered prerequisites (+2.7% at Khan)**. Build those three. Do not build BKT.

---

## 10. Verdicts on Seba's design

### (a) Three-valued concept status (`unseen`/`in-progress`/`done`) as the only mastery representation — **PARTIALLY SUPPORTED, with one specific failure**

Supported: every deployed KT model is ultimately consumed as a *decision* (mastered → advance), and the meta-analytic evidence (§9) says model sophistication is not where the effect sizes live. A three-valued flag is a defensible compression, and BKT's own output is thresholded to a binary in practice. Seba's DAG + status also directly enables the highest-value Khan feature (prerequisite surfacing), and `frontier()` already computes it.

The failure is not the coarseness — it is that **the state is absorbing and has no duration**. `in-progress` carries no count of how many sessions it has been held, no per-concept correctness rate, and no path out except the tutor deciding. That makes wheel-spinning structurally undetectable (§5.2), and wheel-spinning is the single best-evidenced pathology of exactly this design (mastery learning without a stuck-check). Note also that `recent_grades` is a *global* aggregate across all concepts (`store.py:94-97`), so it cannot surface a per-concept problem: a learner acing five concepts while grinding on a sixth reads as "push harder".

### (b) Trusting the LLM tutor's unaided judgement to set `done` — **CONTRADICTED**

Scarlatos et al. (§8) is close to a direct test. GPT-4o judges *turn-level correctness* at near-human quality (0.9317/1; 75.82% vs 85.56% human on the hardest turns) — so `GradeReview` is fine. But *KC-level mastery attribution* is where it degrades: KC-labelling agreement α = 0.4383 with overlap 0.3494; a *fine-tuned* LLM was needed for mastery estimation and still topped out at 0.66–0.77 AUC; and the documented error mode is **labelling a turn correct when the student has actually said they do not know** — mistaking a claim of understanding for a demonstration. Add the general overconfidence result. A single unaided call of "completed" from the same model that just taught the concept, with no independent check and no way for the learner to dispute it, is the least-supported decision in the system. It is also the most consequential: `done` is absorbing, it removes the concept from the frontier, and nothing ever revisits it.

### (c) Freeform prose notes as the misconception store — **SUPPORTED, and better than the alternative**

This is the one place the design is ahead of the literature rather than behind it. The bug-library history (§1) is a strong argument *against* a fixed misconception taxonomy: bugs migrate, libraries don't transfer across domains, and enumeration lost to generative accounts. Khan's JSON→prose result (+5.09% engagement from *formatting alone*, with the same content worth nothing as JSON) is direct production evidence that prose is the right serialisation for an LLM consumer. Per-concept keying, newest-first, top-3, scoped to in-scope concepts (`agenda.py:99-104`) is a sensible recency policy consistent with §7.

Two gaps, both small: (i) notes are stored with `[sNNN]` tags but injected **without any recency marker**, so the tutor cannot discount a stale observation — timestamping in the injected line is nearly free and is the cheapest form of evidence-weighting (§7); (ii) notes are *only* written on `UpdateConcept`, so a misconception observed during a review exchange lands in `GradeReview.note`, which is persisted to the outcomes YAML and then **never read again** (`store.py:94-97` only extracts grades).

### (d) No wheel-spinning / stuck detection — **CONTRADICTED**

Beck & Gong 2013 defined wheel-spinning specifically as the failure mode of mastery-learning systems, which is what Seba is. Prevalence in ITS data is 6.6–24.2% of student-KC pairs depending on criterion (Zhang et al. 2019). Detection is *cheap*: a single-feature logistic regression on correct-response percentage hit **93.5% precision / 77.1% recall after 4 opportunities**; the useful features are all correctness-based. Cold start below ~4 attempts is the only caveat. There is no defensible reason for a mastery-learning system not to have a stuck-check, and Seba's absorbing `in-progress` state makes the failure silent and unbounded — the tutor will keep selecting the same concept as `teach_src` forever (`agenda.py:69`: first `in-progress` concept wins).

### (e) No affect or motivation state — **SUPPORTED for affect, UNSUPPORTED for behavioural disengagement**

Persisting affect labels across sessions is not supported: detectors are weak (F ≈ 0.63–0.68), affect is volatile at minute-scale, and the OLM/SRL review notes affect is the dimension OLMs almost never address — with no evidence that they should. Skip it.

What *is* supported is persisting the **behavioural residue** that affect detectors are proxies for: boredom is the most learning-damaging state and precedes gaming; extended (not brief) confusion is harmful. In a text dialogue these are observable in words and cheap to count — sessions abandoned, concepts repeatedly deferred, "can we skip this", repeated `again` grades on the same item. Seba persists none of it. Note this is largely the same counter as (d) from a different direction, which is an argument for building one counter, not two subsystems.

### (f) Open learner model via the rendered graph — **SUPPORTED but at the weakest evidenced level; the strongest level is nearly free and unbuilt**

`seba view` is a *viewable* OLM. That rung has real but modest support (planning, self-monitoring, navigation) and the SRL systematic review notes OLMs mostly serve cognition rather than metacognition. It is worth having, and the local-first ownership model matches the lifelong-learner-model position (§7) better than most deployed systems do.

But: it shows **no uncertainty** (contradicting the AIED 2017 uncertainty-visualisation result), **no evidence** — the per-concept notes that justify a status exist and aren't rendered, so the model is non-scrutable — and **no way to disagree**. Negotiated learner modelling is the OLM variant with the best evidence (improves both model accuracy *and* the learner's self-assessment accuracy vs. inspection-only; CALMsystem), and it is the one that resolves recency/weighting/absence-of-evidence, which no automatic rule can. In a conversational tutor, negotiation costs one prompt line. Seba has the rarest prerequisite for the best-evidenced OLM technique and doesn't use it. Given (b), it is also the cheapest available *correction* mechanism for an over-confident `done`.

### (g) `recent_grades` → coarse pace hint as the only global adaptation signal — **PARTIALLY SUPPORTED; the aggregation is wrong**

The mechanism is sound and matches evidence: correctness rate is the feature that dominates in wheel-spinning detection, the thresholds (>0.9 push, <0.7 step-back) are in the neighbourhood of the desirable-difficulty / ~85%-success zone used across adaptive systems, and mapping it to practice quota rather than to content is conservative — a coarse control on a coarse signal is exactly right given §9's message that adaptation machinery buys little.

The problem is **aggregation over the wrong unit**. `recent_grades` pools all review grades from the last 3 sessions across all concepts and items (`store.py:94-97`). Both the Khan result (+3.4% for *recent problem-solving history*, i.e. per-item detail) and the wheel-spinning result (per student-KC pair) operate on disaggregated evidence. A global pass rate cannot distinguish "broadly fine, stuck on one thing" from "uniformly struggling", and those need opposite responses. Also, since the pace hint only sets `practice_quota`, a struggling learner gets *fewer* practice items (2) — defensible as load reduction, but it is worth being deliberate that this is the intended semantics.

### Not asked, but worth flagging: transcripts are written and never read

`store.py:127` writes `NNN.transcript.md` every session; nothing loads it. Khan's single largest formatting win was **putting the conversation log in plain text and extending it to related threads from the previous 24 hours** (+5.09% cognitive engagement) — after the same log in JSON produced nothing. Seba has the log, in prose, on disk, unused. This is the highest ratio of evidenced-effect to work in the entire report.

---

## 11. Recommendations, ordered by expected effect

**1. Inject the last session's transcript (or a trimmed tail of it) into the briefing. — CHEAP (schema/plumbing)**
Khan: +5.09% cognitive engagement for exactly this, in exactly this format (plain text, recent window), after the JSON version measured zero. The file already exists at `sessions/NNN.transcript.md`; `Store.load` never opens it. Bound it by characters like `EXCERPT_BUDGET`, take the tail, and prefer transcripts touching concepts in `scope`. If a full transcript is too large, have `EndSession` write a slightly longer prose summary and inject that — but the evidence favours the raw prose over a summary.

**2. Add a stuck-check on `in-progress` concepts. — CHEAP (arithmetic over data already on disk)**
Per concept, from `sessions/*.outcomes.yaml`: sessions since `status_change: started`, plus correct-response percentage over that concept's review grades (`good`/`easy` vs `again`/`hard`). Fire after ≥4 graded opportunities (Zhang et al.'s cold-start floor). On fire, put one line in the briefing — *"`bayes-rule` has been in progress for 4 sessions at 45% success; try a different representation, a worked example, or drop to prerequisite `conditional-prob`"* — and consider forcing `teach_src` to change. Do not build a classifier: a threshold on correctness percentage was within a few points of Random Forest and MLP in the published comparison. Choose the three-correct-in-a-row-style criterion or the stability-style one deliberately; they agree on under half of cases, so document which one you mean.

**3. Require evidence, not assertion, before `done`; and make `done` reversible. — CHEAP (prompt + schema)**
`UpdateConcept.status_change: "completed"` is currently a bare assertion from the model whose judgement §8 shows is miscalibrated at exactly this granularity. Two changes, both prompt-level: (i) add a required `evidence` field naming the specific exchange(s) that demonstrated it, which converts the judgement from mastery-attribution (α 0.44) toward turn-correctness (0.93) and creates an audit trail for the OLM; (ii) gate on a floor — e.g. at least one minted item on the concept graded `good`/`easy` in a *later* session than the teaching one, which enforces retention over recognition and costs one condition. Add `"reopened"` to the literal so a `done` concept can return to `in-progress` when its cards start lapsing — with no reopen path, one over-confident call is permanent.

**4. Surface unmastered prerequisites of the teach concept explicitly in the briefing. — CHEAP (prompt)**
Khan: **+2.7% next-item correctness across 1.36M threads**, the second-largest measured win, and it is pure prompt content over state Seba already has. `agenda.py` already unions `teach_src.prereqs` into `scope`; it does not tell the tutor *which of those prereqs is not `done`*, nor offer a brief review of it. One line: *"prereqs not yet done: X, Y — offer a 2-minute review before teaching."*

**5. Give the briefing per-item recent history, not just a pooled pace hint. — CHEAP (schema)**
Khan's largest single win (**+3.4%**, 608k threads) was "how many problems attempted recently and which ones right and wrong". Seba pools everything into three enum values. Emit per-review-item outcome history for in-scope items (e.g. `[cond-prob-3] last 3: again, hard, good`) and keep the pace hint as-is. Same data, disaggregated. This also fixes (g): compute the pace rate per concept as well as globally.

**6. Timestamp injected notes and read back `GradeReview.note`. — CHEAP (two lines)**
`agenda.py:101` injects `[{cid}] {note}` while `store.py:138` stores `- [sNNN] {note}`; keep the session tag and render it as an age (*"3 sessions ago"*) so the tutor can discount stale observations — the only automatic form of evidence-weighting §7 endorses. Separately, `GradeReview.note` is persisted and never re-read; fold notes attached to `again`-graded reviews into the same per-concept note stream.

**7. Add a negotiation turn: have the tutor state its model and ask the learner to confirm or dispute. — CHEAP (prompt), highest evidence-quality of the OLM options**
Before closing: *"My read is you've got X solid, Y is shaky, Z we haven't touched. Fair?"* Negotiated learner models improve both model accuracy and learner self-assessment accuracy relative to inspection-only, and it is the only mechanism in this literature that handles recency, evidence weighting, and *absence* of evidence. It is also the practical antidote to (b): the learner is the cheapest available check on an over-confident `done`. Persist the disagreement, not just the resolution.

**8. Render evidence and confidence in `seba view`. — MODERATE (UI)**
Show, per concept: the notes behind its status, when the status was set, and how many sessions it has been in-progress (falls out of #2). This moves the OLM from *viewable* to *scrutable*, matching the uncertainty-visualisation and scrutability findings, and makes the stuck-check legible rather than a hidden heuristic. Optionally make the graph the entry point for #7 (click a concept to dispute it).

**9. Aggregate FSRS card retrievability to a per-concept retention number. — MODERATE (arithmetic, but a real modelling claim)**
Mean/min retrievability across a concept's cards at today's date is a continuous, decay-aware companion to the three-valued flag, computable from `Card` state with no new data and no fitting. It is the cheapest way to get *something* continuous, and it is what should trigger `"reopened"` in #3. State the ceiling honestly: it measures retention of what was carded, not transfer — it will report high retention for a learner who has memorised a definition without understanding it. Do not present it to the learner as "mastery".

**10. Persist a disengagement counter per concept. — CHEAP (schema)**
Count `skipped` grades, sessions abandoned mid-way (`SessionRecord.complete == False` already exists), and explicit deferrals, per concept. Boredom is the affect state most damaging to learning and it precedes gaming; in a text dialogue its behavioural signature is directly countable without any affect detector. Fold the counter into #2's trigger rather than building a separate mechanism — it is a second input to one stuck-check, not a second subsystem.

**11. Do NOT build BKT, PFA, or any deep KT model. — the expensive option, and it is not warranted**
BKT needs per-skill parameter fitting from a population Seba does not have, is unidentifiable at n = 1, and lost to PFA on every clean dataset in Xiong et al. Deep KT's reported advantage over PFA largely evaporated once duplicated records (23.6% of rows), scaffolding leakage, and repeated multi-skill sequences were removed. Dialogue-KT specifically tops out around 0.76 AUC even with a *fine-tuned* LLM and 21× more data than Seba will ever have. And §9's meta-analytic bottom line is that step-level interactivity, worked examples, and duration — not learner-model sophistication — carry ITS effect sizes (g = 0.271 in the validity-weighted K-12 analysis; ITS vs human tutoring n.s.). Items 1–7 are prompt and schema work implementing exactly the features with measured production effects. Build those, measure, and revisit only if they saturate.

---

### Sources

- [Brown & Burton, *Diagnostic Models for Procedural Bugs in Basic Mathematical Skills*, Cognitive Science 1978](https://onlinelibrary.wiley.com/doi/pdf/10.1207/s15516709cog0202_4)
- [Burton, *Diagnosing Bugs in a Simple Procedural Skill*](https://exquisitive.com/library/DiagnosingBugsSimpleProceduralSkill.pdf)
- [Brown & VanLehn, *Repair Theory: A Generative Theory of Bugs in Procedural Skills*, Cognitive Science 1980](https://onlinelibrary.wiley.com/doi/abs/10.1207/s15516709cog0404_3)
- [VanLehn, *Mind Bugs: The Origins of Procedural Misconceptions*, MIT Press 1990](https://mitpress.mit.edu/9780262512909/mind-bugs/)
- [VanLehn, Siler, Murray, Yamauchi & Baggett, *Why Do Only Some Events Cause Learning During Human Tutoring?*, Cognition & Instruction 2003](https://www.tandfonline.com/doi/abs/10.1207/S1532690XCI2103_01)
- [van de Sande, *Properties of the Bayesian Knowledge Tracing Model*](https://files.eric.ed.gov/fulltext/EJ1115329.pdf)
- [Pardos & Heffernan, *Modeling Individualization in a Bayesian Networks Implementation of Knowledge Tracing*, UMAP 2010](https://link.springer.com/chapter/10.1007/978-3-642-13470-8_24)
- [Baker, Corbett & Aleven, *More Accurate Student Modeling through Contextual Estimation of Slip and Guess Probabilities*, ITS 2008](https://link.springer.com/chapter/10.1007/978-3-540-69132-7_44)
- [Pavlik, Cen & Koedinger, *Performance Factors Analysis — A New Alternative to Knowledge Tracing*, AIED 2009](https://digitalcommons.memphis.edu/facpubs/8350/)
- [Xiong, Zhao, Van Inwegen & Beck, *Going Deeper with Deep Knowledge Tracing*, EDM 2016](http://beardeer.github.io/wpi_public_html/papers/edm_2016_xiong_zhao.pdf) ([ERIC](https://eric.ed.gov/?id=ED592679))
- [KTbench: A Data Leakage-Free Framework for Knowledge Tracing, 2024](https://arxiv.org/html/2403.15304v2/)
- [Bull & Kay, *Negotiated learner modelling to maintain today's learner models*, RPTEL 2016](https://pmc.ncbi.nlm.nih.gov/articles/PMC6302918/)
- [Bull, *There are Open Learner Models About!*, IEEE TLT 2020](https://dl.acm.org/doi/abs/10.1109/TLT.2020.2978473)
- [Open learner models in supporting SRL in higher education: A systematic literature review, Computers & Education 2020](https://www.sciencedirect.com/science/article/abs/pii/S0360131520300774)
- [Evaluating the Effect of Uncertainty Visualisation in Open Learner Models on Students' Metacognitive Skills, AIED 2017](https://link.springer.com/chapter/10.1007/978-3-319-61425-0_2)
- [Persuading an Open Learner Model in the Context of a University Course, ITS 2016](https://link.springer.com/chapter/10.1007/978-3-319-39583-8_34)
- [Kay & Kummerfeld, *From data to personal user models for life-long, life-wide learners*, BJET 2019](https://bera-journals.onlinelibrary.wiley.com/doi/abs/10.1111/bjet.12878)
- [Kay, *Lifelong Learner Modeling for Lifelong Personalized Pervasive Learning*](https://www.semanticscholar.org/paper/118a7c6702d3e32ac75cfd87b52320bede9cc500)
- [Kay & Kummerfeld, *Scrutable adaptation*, AH 2006](https://dl.acm.org/doi/10.1007/11768012_2)
- [Khan Academy, *How Khan Academy Is Building a Better AI Tutor: Our Most Recent Learnings*](https://blog.khanacademy.org/how-khan-academy-is-building-a-better-ai-tutor-our-most-recent-learnings/)
- [GrowthBook, *How Khan Academy A/B Tests Generative AI*](https://www.growthbook.io/blog/how-khan-academy-optimizes-ai-tutoring-with-experimentation)
- [Beck & Gong, *Wheel-Spinning: Students Who Fail to Master a Skill*, AIED 2013](https://link.springer.com/chapter/10.1007/978-3-642-39112-5_44)
- [Zhang et al., *Early Detection of Wheel Spinning: Comparison across Tutors, Models, Features, and Operationalizations*, EDM 2019](https://files.eric.ed.gov/fulltext/ED594575.pdf)
- [Seven-Year Longitudinal Implications of Wheel Spinning and Productive Persistence, AIED 2021](https://link.springer.com/chapter/10.1007/978-3-030-78292-4_2)
- [Baker, D'Mello, Rodrigo & Graesser, *Better to be frustrated than bored*, IJHCS 2010](https://www.sciencedirect.com/science/article/abs/pii/S1071581909001797)
- [Baker et al., *Carelessness and Affect in an Intelligent Tutoring System*, IJAIED](https://learninganalytics.upenn.edu/ryanbaker/AIED-D-13-00017_Revised%20v2.pdf)
- [Generalisable sensor-free frustration detection, UMUAI 2024](https://link.springer.com/article/10.1007/s11257-024-09402-4)
- [Settles & Meeder, *A Trainable Spaced Repetition Model for Language Learning*, ACL 2016](https://research.duolingo.com/papers/settles.acl16.pdf)
- [Choffin, Popineau, Bourda & Vie, *DAS3H: Modeling Student Learning and Forgetting for Optimally Scheduling Distributed Practice*, EDM 2019](https://arxiv.org/pdf/1905.06873)
- [Adaptive Forgetting Curves for Spaced Repetition Language Learning](https://pmc.ncbi.nlm.nih.gov/articles/PMC7334729/)
- [Scarlatos, Baker & Lan, *Exploring Knowledge Tracing in Tutor-Student Dialogues using LLMs*, LAK 2025](https://learninganalytics.upenn.edu/ryanbaker/Dialogue_KT_LAK_25-2.pdf)
- [LLM-KT: Aligning Large Language Models with Knowledge Tracing, 2025](https://arxiv.org/html/2502.02945v1)
- [Mind the Confidence Gap: Overconfidence, Calibration, and Distractor Effects in LLMs, 2025](https://arxiv.org/html/2502.11028v1)
- [Kulik & Fletcher, *Effectiveness of Intelligent Tutoring Systems: A Meta-Analytic Review*, RER 2016](https://journals.sagepub.com/doi/abs/10.3102/0034654315581420)
- [Ma, Adesope, Nesbit & Liu, *Intelligent Tutoring Systems and Learning Outcomes: A Meta-Analysis*, JEP 2014](https://eric.ed.gov/?id=EJ1049508)
- [Leite et al., *Do intelligent tutoring systems benefit K-12 students? A meta-analysis*, 2025](https://arxiv.org/pdf/2511.04997)
- [Personalization through adaptivity or adaptability? A meta-analysis on simulation-based learning, Educational Research Review 2024](https://www.sciencedirect.com/science/article/pii/S1747938X2400071X)
- [*Faster Completion, Less Learning: Generative AI Reduced Study Time on Math Problems*](https://arxiv.org/pdf/2605.21629)
