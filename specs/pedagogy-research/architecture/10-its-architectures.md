# What worked in real tutoring systems — architectures, evidence, and what it implies for Seba

Scope: systems with measured effects on learning, read for **what they stored, how they
chose the next thing, and what their builders concluded in hindsight**. Then verdicts on
Seba's six architectural bets.

Seba, for reference (read from the repo, not assumed): `src/seba/scheduler/items.py` wraps
`py-fsrs` (`Scheduler`, `Card`, ratings again/hard/good/easy); `scheduler/agenda.py` builds
the agenda from `due_items` + the syllabus `frontier`, derives a `pace_hint` from recent
grade rate (>0.9 → push harder, <0.7 → step back) and a `practice_quota` (5/3/2); the LLM
grades every review, mints cards (cap 10/session), sets concept status, and writes
misconception notes. Mastery criterion lives in prose in `skills/seba-tutor/SKILL.md`: *"two
correct unaided applications, at least one in a context they haven't seen it in."* State is
YAML/markdown in a git repo. One generic SKILL.md + a ~35-line per-subject overlay
(`subjects/italian/overlay.md`, `subjects/probability/overlay.md`).

---

## 1. Cognitive Tutors / Carnegie Learning

**Modelled.** ACT-R production rules. Domain knowledge decomposed into *knowledge components*
(skills); a model-tracing expert system solves each problem every acceptable way, so student
input is matched step-by-step against ideal steps plus a library of buggy rules. Anderson,
Corbett, Koedinger & Pelletier, *Cognitive Tutors: Lessons Learned*, JLS 4(2):167–207, 1995 —
https://www.tandfonline.com/doi/abs/10.1207/s15327809jls0402_2 ,
http://act-r.psy.cmu.edu/?post_type=publications&p=13881

**Stored between sessions.** One Bayesian Knowledge Tracing posterior per knowledge component
per student: P(known), updated with four parameters (prior, learn, guess, slip) after every
step. Corbett & Anderson, *Knowledge tracing: modeling the acquisition of procedural
knowledge*, UMUAI 4:253–278, 1994 — https://link.springer.com/article/10.1007/BF01099821

**Next thing.** Mastery learning at the *skill* level: a section's problems keep coming until
every KC in it exceeds P(known) ≥ 0.95, then the student advances. Exposed to the learner as
the **skillometer** — a bar per skill, the first widely deployed open learner model (Corbett &
Anderson 1992/1995; VanLehn's slide 8 reproduces the Carnegie Learning skillometer:
https://educationgroup.mit.edu/HHMIEducationGroup/wp-content/uploads/2011/02/VanLehnPresentationSlides.pdf).

**Measured effect.** Lab/best-case: same proficiency as conventional instruction in **one third
of the time**, ~1 σ in the strongest early studies (Anderson et al. 1995). At scale, much
smaller. The RAND cluster-randomised trial (Pane, Griffin, McCaffrey & Karam, *Effectiveness
of Cognitive Tutor Algebra I at Scale*, EEPA 36(2):127–144, 2014;
https://eric.ed.gov/?id=EJ1024233 , https://www.rand.org/pubs/external_publications/EP50410.html):
147 schools in 7 states, matched pairs, 2 years. **Year 1: no effect. Year 2: +0.21 σ, high
schools only**, not significant in middle schools — about eight percentile points for the
median student. WWC rated it *Meets Evidence Standards without Reservations*
(https://ies.ed.gov/ncee/wwc/Study/82100). An addendum revisits the estimates:
https://www.rand.org/pubs/working_papers/WR1050.html

**Designers in retrospect.** Anderson et al. (1995) report that the *interaction style* mattered
more than the theory's elaborations: immediate feedback, short directed error messages,
learning in production-rule-sized units. Two of their eight principles were walked back in
practice (the reification of goal structure; heavy tutorial control). And a finding that should
worry any mastery-gated system — Corbett & Bhatnagar (1997): BKT predicts post-test scores when
used passively, but **once BKT is used to drive mastery learning it stops predicting post-test
scores** (Campbell's Law; discussed in Baker 2016, below).

## 2. ASSISTments

**Architecture.** Deliberately simple. Items are authored by teachers/researchers; a *skill
builder* is a pool of items tagged to one skill. Hints and scaffolds are pre-written per item.
Mastery is a **heuristic, not a model: three correct in a row** — the counterexample Baker uses
to make his point about student modelling. Heffernan & Heffernan, *The ASSISTments Ecosystem*,
IJAIED 24:470–497, 2014.

**Stored.** Item-level response logs, per-skill counters, and — the part they consider the
product — **reports to the teacher** before the next class.

**Randomised evidence.** Roschelle, Feng, Murphy & Mason, *Online Mathematics Homework Increases
Student Achievement*, AERA Open, 2016 — https://journals.sagepub.com/doi/full/10.1177/2332858416673968 .
2,769–2,850 seventh graders, 43–46 Maine schools, random assignment: **g = 0.22** on TerraNova
(p<0.001), larger for lower-prior-achievement students. IES award page:
https://ies.ed.gov/use-work/awards/efficacy-study-online-mathematics-homework-support-evaluation-assistments-formative-assessment-and .
The **replication is weaker**: North Carolina, 5,991 students, 63 schools, **0.10** as a one-year
delayed effect (https://www.assistments.org/evidence-of-impact ; long-term follow-up
https://eric.ed.gov/?id=ED659541). Independent listing: https://evidencebasedprograms.org/programs/assistments/

**Conclusion drawn.** The wins came from hundreds of small in-platform A/B tests and from
routing information to a human, not from a richer learner model.

## 3. ALEKS

**Modelled.** Knowledge Space Theory: the domain is a partial order of items; a *knowledge state*
is a feasible downward-closed set. Assessment is adaptive over states, not over a latent trait.
Matayoshi & Cosyn, *A practical perspective on knowledge space theory: ALEKS and its data*,
J. Math. Psych., 2021 — https://jmatayoshi.github.io/publications/JMP2021_KST_ALEKS_preprint.pdf

**Stored.** The student's current knowledge state (a set of mastered items), plus history for
re-assessment. **Next thing:** the *outer fringe* — items whose prerequisites are all mastered —
presented as the **pie** of "ready to learn" topics; the learner picks from that set. Periodic
**progress assessments** re-estimate the state, and can *demote* items (explicit forgetting),
which is the piece most prerequisite-graph systems omit.

**Efficacy.** Mixed and implementation-dependent; the best-known independent RCT is Craig, Hu,
Graesser et al., *The impact of a technology-based mathematics after-school program using ALEKS*,
Computers & Education 68:495–504, 2013 (positive). No WWC intervention report establishes a
general effect; ALEKS's own bibliography is at https://www.aleks.com/about_aleks/publications_kst .
Treat vendor-summarised numbers with the same suspicion as Duolingo's.

## 4. AutoTutor family

**Modelled.** No production rules and no per-skill posterior. Each question carries a **curriculum
script**: ideal answer, a list of **expectations** (anticipated correct propositions), a list of
**misconceptions** with corrections, hint/prompt families attached to each expectation, keywords
and synonyms, and a summary. Graesser et al., *AutoTutor: a tutor with dialogue in natural
language*, BRM 36:180–192, 2004 — https://link.springer.com/content/pdf/10.3758/BF03195563.pdf ;
review: *AutoTutor and Family: A Review of 17 Years of Natural Language Tutoring*, IJAIED 24, 2014
— https://link.springer.com/article/10.1007/s40593-014-0029-5

**Next thing.** Expectation-and-Misconception-Tailored (EMT) dialogue: LSA/regex semantic match
scores how much of each expectation the student's turn covers; the system pumps → hints → prompts
→ asserts until coverage crosses a threshold, and fires a correction whenever a misconception
matches. The *state* is essentially a coverage vector over the current question's expectations —
**within-question, not persisted across sessions**. AutoTutor kept far less long-term learner
state than Cognitive Tutor did.

**Effect.** ~**0.8 σ** against non-interactive control conditions, aggregated over many studies
(Graesser et al.; https://files.eric.ed.gov/fulltext/ED586836.pdf). But see §5: against a *matched-
content* text, the advantage disappears.

## 5. Andes / Why2-Atlas — and the interaction plateau

The single most consequential retrospective for Seba. Sources: VanLehn, *The Relative
Effectiveness of Human Tutoring, Intelligent Tutoring Systems, and Other Tutoring Systems*,
Educational Psychologist 46(4):197–221, 2011
(https://www.tandfonline.com/doi/abs/10.1080/00461520.2011.611369 ,
https://eric.ed.gov/?id=EJ946764) and his talk slides, which contain the full meta-analytic table
— https://educationgroup.mit.edu/HHMIEducationGroup/wp-content/uploads/2011/02/VanLehnPresentationSlides.pdf

Meta-analytic means, effect vs. *no tutoring* (slide 37):

| Tutoring type | vs. | k | mean d | % reliable |
|---|---|---|---|---|
| Answer-based (CAI) | no tutoring | 165 | **0.31** | 40% |
| Step-based (typical ITS) | no tutoring | 28 | **0.76** | 68% |
| Substep-based (ITS w/ NL dialogue) | no tutoring | 26 | **0.40** | 54% |
| Human tutoring | no tutoring | 10 | **0.79** | 80% |
| Step-based | answer-based | 2 | 0.40 | 50% |
| Substep-based | step-based | 11 | 0.16 | **0%** |
| Human | step-based | 10 | 0.21 | 30% |
| Human | substep-based | 5 | −0.12 | **0%** |

**The plateau:** assignments < answers < steps, and then *nothing*. Steps = substeps = human.
Supporting experiments, all with content held constant: Andes-Atlas vs Andes across four studies
(N=26, 21, 12) — no reliable advantage, one trend *against* dialogue (d=0.34 favouring plain
Andes); the seven WHY2 experiments (VanLehn, Graesser et al., *When Are Tutorial Dialogues More
Effective Than Reading?*, Cognitive Science 31:3–62, 2007 —
https://onlinelibrary.wiley.com/doi/abs/10.1080/03640210709336984) where human tutoring =
Why2-Atlas = Why2-AutoTutor = a **step-based tutor whose "dialogue" was rewritten as a static
monologue**, all > reading a textbook; plus Evens & Michael (2006), Reif & Scott (1999), Katz et
al. (2003).

**What VanLehn concludes is worth building.** Get to step granularity and stop. Build the step
loop (step analyser + feedback/hint generator) before the task loop (assessor + task selector).
"If you build one, use **example-tracing** first." And where the details *do* matter — his slides
53 — Min Chi's induced tell-vs-elicit policy produced **d = 0.8** from only 103 students'
data, so the payoff is in tuning micro-decisions empirically, not in adding machinery.

**Caveat he states explicitly (slide 42): the evidence base is STEM only — "not language, music,
sports."** Nothing in the plateau result licenses conclusions about Italian.

## 6. Duolingo — the language case

**Half-life regression** (Settles & Meeder, ACL 2016, pp. 1848–1858;
https://aclanthology.org/P16-1174/ , https://research.duolingo.com/papers/settles.acl16.pdf ,
code+13M traces at https://github.com/duolingo/halflife-regression). Model: p = 2^(−Δ/h),
ĥ = 2^(Θ·x), fit by regularised squared loss on both the observed recall rate *and* an algebraic
half-life target. Features: per-student-per-lexeme counters (times seen, times right, times
wrong — square-rooted) plus ~20k sparse lexeme-tag indicators. **Unit of state is the
student×lexeme-tag pair**, not the word and not the skill. Pimsleur and Leitner fall out as
special cases with hand-picked weights.

Honest numbers (their Table 2, full 12.9M instances): HLR MAE **0.128** vs Leitner 0.235
(≥45% error reduction), but **AUC 0.538 for HLR vs 0.542 for Leitner** — i.e. at *ranking* which
item to review next, the trained model was no better than a 1972 flashcard heuristic. The
operational win was calibration of the strength meters, and **+12% daily engagement** in the A/B
test — an engagement result, not a learning result.

**Birdbrain** is the other half: a per-exercise difficulty × per-learner ability model (IRT-shaped,
later deep) predicting P(correct) for lesson construction —
https://blog.duolingo.com/learning-how-to-help-you-learn-introducing-birdbrain/ . Duolingo reports
A/B improvements in learning and engagement; no independent replication exists.

**Efficacy evidence is vendor-run and weak.** Jiang, Rollinson, Plonsky & Pajak, *Evaluating the
reading and listening outcomes of beginning-level Duolingo courses*, Foreign Language Annals,
2021 — https://onlinelibrary.wiley.com/doi/full/10.1111/flan.12600 — claims parity with four
university semesters in half the time, but has no pretest, no control group, no time-on-task
control, and self-selected completers. Independent commentary is blunt about the unwarranted
claims; e.g. https://scholarspace.manoa.hawaii.edu/server/api/core/bitstreams/ea47a53e-da6e-4419-bd55-e72b458294f4/content .
Treat "34 hours ≈ one semester" as marketing.

## 7. SuperMemo / Anki / FSRS — the other lineage

FSRS is a three-variable DSR model (Difficulty, Stability, Retrievability) — ~13–21 parameters,
6 equations, fit per user by gradient descent to their own review history; now the default
scheduler in Anki. https://github.com/open-spaced-repetition/free-spaced-repetition-scheduler ,
https://github.com/open-spaced-repetition/fsrs4anki/wiki/ABC-of-FSRS ,
https://faqs.ankiweb.net/what-spaced-repetition-algorithm . Reported benefit: **20–30% fewer
reviews for the same retention** vs SM-2.

What this lineage **deliberately does not model**, and this is the point: no domain graph, no
prerequisites, no skills, no misconceptions, no notion of *understanding* — only per-item recall
probability over time, with the human responsible for what goes on the card and for grading their
own recall. It is answer-granularity by VanLehn's taxonomy (d≈0.31 territory) and it makes no
claim otherwise; its job is retention of already-learned items, not acquisition. Anything that
pairs it with a teaching loop is combining two lineages that were never validated together.

## 8. Mastery learning / Keller Plan (PSI)

Mechanics: small self-paced units, a study guide, a unit test requiring ~90% to advance,
unlimited ungraded retakes, proctors. Keller, *Good-bye, teacher…*, JABA 1(1):79–89, 1968.
Meta-analytic effect vs lecture: Kulik, Kulik & Cohen (1979), 72 studies, **+0.5 σ** on final
exams (other syntheses 0.42 and 0.49). https://files.eric.ed.gov/fulltext/EJ800986.pdf ,
https://en.wikipedia.org/wiki/Keller_Plan

Two mechanisms carry the effect and both are cheap: **a stated criterion that gates advancement**,
and **retakes that cost nothing and carry no penalty**. Seba's SKILL.md implements exactly this
pair ("two correct unaided applications… retakes cost nothing and get no commentary"). VanLehn's
slide 57 notes competency gating is rare in schools only because *schools* are time-gated — an
individual learner has no such constraint.

## 9. Retrospectives: what the builders say was wasted

**Baker, *Stupid Tutoring Systems, Intelligent Humans*, IJAIED 26:600–614, 2016** —
https://learninganalytics.upenn.edu/ryanbaker/STS-Baker-IJAIED-v15.pdf (read in full). The
argument, in his words and mine:

- The systems that reached scale are *the least like the original vision*. "The most widely used
  intelligent tutoring systems are in some ways the furthest from the initial vision."
- On student modelling specifically: "despite the decades of work on knowledge modeling, and the
  intense competition between approaches seen in published papers… **the approaches used in
  practice are largely fairly simple**. For example, many systems in wide use depend on simple
  heuristics to assess student mastery, such as whether the student gets three right in a row."
- Affect/metacognition/self-regulation detectors improved outcomes in small studies but "are not
  then integrated into the systems deployed at scale." Self-improving RL tutors: "few systems
  incorporate this capacity."
- Why automated intervention loses to informed humans: **authoring cost** (his own gaming-detector
  agent took "several months" and worked on a handful of lessons), **brittleness** ("an automated
  system can't recognize when a model is clearly wrong"), students adapting faster than the system
  ("an encouraging message may not be so encouraging the 12th time"), and drift over years.
- The Campbell's-Law trap: BKT predicts post-test until you gate on it, then it doesn't
  (Corbett & Bhatnagar 1997). **Any mastery estimate optimised against becomes a worse measure.**

**VanLehn 2011/2011-talk** — above: the elaborate substep machinery bought nothing over steps.

**Anderson et al. 1995** — the theory-derived elaborations were the parts they dropped; feedback
timing and grain size were the parts that held.

## 10. Authoring cost

- Model-tracing ITS: **~200–300 hours of expert authoring per hour of instruction** (Murray 1999,
  *Authoring intelligent tutoring systems: an analysis of the state of the art*, IJAIED 10:98–129;
  updated 2003 survey https://www.researchgate.net/publication/228328548). Most of it goes into
  the production-rule model.
- Even with CTAT and experienced teams, **50:1 to 100:1** is the reported range (Aleven et al.).
- **Example-tracing** tutors — author by demonstrating solutions instead of writing rules — measure
  at **4–8× cheaper** than the literature estimates, ~20–30:1: Aleven, McLaren, Sewall & Koedinger,
  *The Cognitive Tutor Authoring Tools (CTAT): Preliminary Evaluation of Efficiency Gains*, ITS
  2006 — https://link.springer.com/chapter/10.1007/11774303_7 ; *Example-Tracing Tutors: Intelligent
  Tutor Development for Non-Programmers*, IJAIED — https://files.eric.ed.gov/fulltext/ED618912.pdf
- Authoring-tool survey: https://link.springer.com/article/10.1007/s40593-017-0157-9

**Implication.** The authoring ratio is the *reason* the field built elaborate learner models: when
content costs 200 hours/hour, you must route each student to exactly the right pre-authored item,
so you need a precise estimate of what they know. **An LLM that authors a correct, transfer-shaped
problem in two seconds changes the economics of that argument, not the pedagogy.** With generation
free, the value of a precise selection model drops sharply — but the value of *knowing whether the
student actually got it* does not drop at all, because that is now the only remaining source of
signal.

## 11. LLM-era systems with published architecture

- **LearnLM** (Google, arXiv:2412.16429 — https://arxiv.org/abs/2412.16429 ,
  https://arxiv.org/html/2412.16429v1). Explicit three-layer split: pedagogy trained *into* the
  model (SFT+RLHF), behaviour specified by **system instructions** that "take precedence over any
  subsequent instructions", and grounding material / learner persona / scenario supplied by the
  surrounding application. Framing: **"pedagogical instruction following"** — refuse to hard-code
  one pedagogy, let the prompt name the pedagogy. Evaluation: 49 scenarios, 186 experts role-playing
  learners, 2,360 conversations, 228 experts scoring a 29-item rubric over cognitive load, active
  learning, metacognition, curiosity, adaptivity. Expert preference **+31% vs GPT-4o, +13% vs its
  own base Gemini 1.5 Pro, +11% vs Claude 3.5 Sonnet**. Their own caveat: per-application
  fine-tuning is impractical, so "**prompting will likely remain the best way for education product
  developers to specify behavior**" — i.e. a prompt-specified tutor is the recommended architecture,
  not a fallback. All of this measures *expert preference over conversations*, not learning.
- **Tutor CoPilot** (Wang, Demszky et al., 2024 — https://edworkingpapers.com/ai24-1054 ,
  https://files.eric.ed.gov/fulltext/ED661562.pdf). RCT, ~900 tutors / ~1,800 K-12 students. LLM is
  **tutor-facing only**: it suggests moves, the human decides. **+4 pp topic mastery (p<0.01),
  +9 pp for the lowest-rated tutors**, ~$20/tutor/year. Message analysis (350k messages) shows the
  mechanism: more probing questions, less generic praise. The first RCT of an LLM in live tutoring,
  and its design lesson is that the LLM's reliable contribution was *pedagogical move selection*,
  not autonomy.
- **Kestin et al. 2025** (Harvard, ~194 physics undergrads, crossover RCT). AI tutor ("PS2 Pal")
  beat an active-learning classroom by **d ≈ 0.73–1.3** in less time (median 49 vs 60 min).
  Architecturally the notable bit: hallucination was controlled by **injecting pre-written
  step-by-step solutions into the prompt** — the tutor was told the answer before it was allowed to
  grade or hint. Review + criticisms (2-week window, no retention data, selective sample):
  https://etcjournal.com/2025/11/10/review-of-kestin-et-al-s-june-2025-harvard-study-on-ai-tutoring/

**What no one has published:** an RCT isolating *where state lives* (code vs model), or evidence on
LLM-as-sole-assessor over a long horizon. That is a genuine gap, and it is where Seba's biggest
bet sits.

---

## Verdicts on Seba's design

### (a) Code owns state/scheduling/validation; LLM owns dialogue, assessment, authoring — **SUPPORTED**

Every system here separates a *step loop* from a *task loop* (VanLehn slides 44–45: student
interface + step analyser + feedback/hint generator, vs assessor + task selector). Seba's split is
that split, with the LLM as step analyser + feedback generator and code as assessor plumbing + task
selector. LearnLM's three-layer architecture is the same shape and is the only LLM-tutor
architecture paper with expert-rated evidence behind it. The strongest specific support is
mechanical: `seba end` refusing while reviews are ungraded is a **code-enforced invariant on a
process the LLM would otherwise silently skip**, which is exactly the class of thing Baker says
automated components are bad at and deterministic ones are good at. Keep it.

Caveat: VanLehn's meta-analysis says the *dialogue* half of this — the part Seba invests most in —
is where the returns plateau. Step-granularity feedback is worth d≈0.76; making it conversational
and substep-fine bought 0.16 at 0% reliability. Seba's SKILL.md already mandates working at
solution steps ("never accept or evaluate only a final answer… name *which* step broke"), which is
the load-bearing part.

### (b) LLM as sole assessor, no independent check on mastery — **UNSUPPORTED** (not contradicted; untested)

No deployed system that showed measured effects let the same component both teach and be the sole
judge of mastery with no external signal. The judge was always separable from the teacher: a
production-rule match (Cognitive Tutor), a knowledge-state re-assessment on *sequestered* items
(ALEKS progress assessments), three-right-in-a-row on fresh items (ASSISTments), a 90% unit test
written by someone else (PSI), or recall of a fixed card (Anki). PSI's effect specifically depends
on the criterion being **external to the tutoring interaction**.

Two concrete risks, both documented:
1. **Campbell's Law, empirically demonstrated in this exact setting.** BKT predicted post-test until
   it was used to gate mastery, then stopped (Corbett & Bhatnagar 1997, via Baker 2016 p.10). Seba's
   grader is also its teacher and also chooses the practice problems — the tightest possible
   optimise-against-your-own-measure loop.
2. **Grader leniency and self-consistency.** The Kestin tutor was given the worked solution before
   it was allowed to respond; Seba's SKILL.md independently arrived at the same guard ("solve before
   you pose… never derive the answer in the same turn you judge theirs"), which is the right
   instinct. But there is no published evidence on LLM grading drift over hundreds of sessions with
   the same learner, and I could not find any (search budget exhausted before that query; treat as
   an open question, not a settled one).

This is the design's largest unhedged bet. It is not wrong — nothing contradicts it — but it is the
one place where every predecessor bought insurance and Seba does not.

### (c) Concept-level mastery, no per-skill estimate / skillometer — **CONTRADICTED, with a large exception**

The evidence for grain size is unusually consistent and it points *finer* than concept:
- Cognitive Tutor's whole effect is built on per-KC tracking, and the field's most cited data-driven
  win is Koedinger et al. splitting one "compute the area of a circle" skill into two KCs after
  Learning Factors Analysis showed it was two, then **teaching the corrected decomposition and
  getting significantly faster learning** (Baker 2016 p.6).
- Duolingo's unit of memory state is the **student × lexeme-tag** pair, far below "concept."
- ALEKS operates on items with prerequisite structure, not chapters.

Seba's concept nodes are sized at 1–3 sessions (`est_sessions: 1–3` in the syllabus schema) — that
is roughly a Cognitive Tutor *section*, not a KC. A concept marked `completed` on two unaided
applications can easily contain a sub-skill that was never exercised.

**The exception, which is real:** the machinery those systems used to get finer granularity
(production rules, KC labels per item, an IRT-shaped ability estimate) is exactly what VanLehn's
"increase task-loop sophistication" branch bought least from, and what Baker says practitioners
abandoned for three-in-a-row heuristics. Seba's FSRS card layer *already is* a fine-grained
per-item memory model — arguably finer than a skillometer. What's missing isn't a per-skill
probability; it's that **concept completion and card scheduling are two disconnected state
machines**: a concept can be `completed` while its cards are all lapsing. That's the actual defect,
and it's fixable without a skillometer (rec. 2).

### (d) Content authored on the fly rather than pre-authored — **SUPPORTED**

This is Seba's best-supported choice, and it is supported by the *cost* literature rather than by
any efficacy trial. 200–300 hours of authoring per instructional hour (Murray) is the tax that
shaped every system above: it is why they needed precise selection models, why AutoTutor's coverage
was limited to scripted questions, and why example-tracing (4–8× cheaper) was considered a
breakthrough. Generation at zero marginal cost dissolves that constraint. It also unlocks something
none of them could do: SKILL.md's "practice problems should be structurally the same and
superficially different from what you taught" and "mint the **transfer** version of a problem" —
generating a *fresh transfer item per learner per session* was economically impossible in 2005.

Risk to name: on-the-fly authoring means no item ever accumulates difficulty statistics, so the
Birdbrain/IRT style of calibration is permanently unavailable. That's an acceptable trade for one
learner; it would not be at scale.

### (e) Plain-text git-backed state — **NO EVIDENCE** (and none needed)

No ITS paper evaluates its storage layer. Two indirect arguments, both favourable: Baker's whole
thesis is that the leverage is in *a human being able to see and act on the state*, and a git repo
of YAML is the maximally inspectable open learner model — the skillometer's actual function was
transparency (Corbett & Anderson 1992/Bull & Nghiem 2002 on open learner models). And git gives
free longitudinal history, which is what a one-learner-multi-year system needs and what none of
these systems' student records provided. The only thing plain text costs you is aggregate analysis,
which is meaningless at N=1. Keep it; don't build a database.

### (f) One generic prompt + short per-subject overlay across probability and Italian — **UNSUPPORTED, and the Italian side is the weak one**

- **In favour:** LearnLM's central claim is precisely that pedagogy should be *specified in system
  instructions* rather than baked in, so that different pedagogies can share one model — and it
  showed +13% expert preference over its own base model doing exactly that. Seba's structure
  (generic policy + overlay naming the subject's pedagogy) is the LearnLM pattern.
- **Against:** VanLehn's plateau result — the main evidence that a well-run step-based dialogue is
  enough — **explicitly excludes language** (slide 42: "Only STEM; not language, music, sports").
  Nothing in the ITS efficacy literature transfers to Italian. Meanwhile the two subjects want
  structurally different loops: probability wants solve-before-you-pose, step-level error attribution
  and transfer problems; Italian wants meaning-first tasks, a *correction budget per turn*, output-
  volume monitoring, and recasts — and the generic SKILL.md's core moves ("ask exactly one question
  per turn", "gate the explanation", "two consecutive non-answers means stop asking and teach") are
  written for the probability case. The Italian overlay is currently fighting the base prompt on at
  least three of them.

Verdict: the *architecture* (generic + overlay) is supported; the current *allocation* — a
probability-shaped generic layer with a language-shaped patch — is not. This is a content problem,
not a structural one.

---

## Recommendations, ordered by expected effect

**1. Add one independent mastery check that the teaching turn cannot see. — cheap.**
The single highest-value change. Before `--status completed`, have code hold back one *sequestered*
item: a card minted earlier for that concept, or a stored transfer problem the LLM wrote at
teach-time and has not seen the answer to since. Gate completion on that item being answered
unaided in a *later* session. This is ALEKS's progress assessment, PSI's unit test, and
ASSISTments' fresh-item rule, all of which are cheap heuristics rather than models — and it is the
one insurance policy every predecessor bought (§ verdict b, Corbett & Bhatnagar's Campbell's-Law
result). Implementation: a `sequestered` flag on `Item` and a completion precondition in
`scheduler/apply.py`.

**2. Make concept completion answer to the FSRS layer. — cheap.**
Refuse or flag `--status completed` for a concept whose cards are lapsing (e.g. any card for that
concept with grade `again` in the last two reviews), and surface per-concept card health in the
agenda. This closes the (c) gap — the real defect isn't a missing skillometer, it's that the two
state machines never talk. Bonus: it gives ALEKS-style *demotion*, which pure prerequisite graphs
lack.

**3. Split the base prompt: move probability-shaped policy into the analytic overlay. — cheap.**
The turn policy, hint ladder, and "two non-answers → teach" rules are STEM tutoring rules. Keep
truly universal things in SKILL.md (voice, recording discipline, don't-cave, feedback shape,
retakes are free) and push the rest down. Fixes (f) without changing the architecture.

**4. Show the learner the state — a skillometer, not a skill model. — cheap.**
`seba view` already renders the graph; add per-concept card health and time-since-review to it, and
mention it at session end (SKILL.md already does). Open learner models were the part of Cognitive
Tutor that transferred everywhere; Duolingo's strength meters exist because learners complained the
Leitner-based ones misrepresented what they knew (Settles & Meeder §3.3). Cheap, and it recruits the
one intelligent human in the loop (Baker's whole thesis).

**5. Log the tutor's own decisions so you can A/B your policy later. — cheap now, valuable later.**
Record per-turn: hint rung reached, tell-vs-elicit, whether the item was transfer or same-format.
Min Chi induced a d=0.8 policy improvement from **103 students'** data; a single learner over a year
gives you thousands of turns, enough to at least *notice* which rungs precede failures. Baker and
VanLehn independently converge on "run many small A/B tests" as the thing that actually moved
outcomes. Costs one extra field today; impossible to reconstruct retroactively.

**6. Add explicit forgetting at the concept level. — moderate.**
ALEKS re-assesses and demotes. Seba's concepts are monotonic (`unseen → started → completed`) while
only its cards decay. A concept untouched for N months with no card coverage should re-enter the
frontier as review, not stay green forever.

**7. Do NOT build a Bayesian/IRT learner model or a per-skill probability. — expensive, and the
evidence says skip it.**
Baker: systems at scale use three-right-in-a-row. Duolingo: the trained HLR model tied a 1972
Leitner heuristic on AUC. VanLehn: task-loop sophistication is the branch with the least evidence,
and the mastery estimate degrades the moment you gate on it. Rec. 1 buys the same protection for a
fraction of the work.

**8. Do NOT add substep/Socratic machinery beyond what's there. — expensive, contradicted.**
Substep vs step: d = 0.16, 0% reliable, k = 11. Human vs substep: d = −0.12. If anything, prune —
the SKILL.md's finer-grained conversational rules are in plateau territory.

### Keep, explicitly

- **Code-owned scheduler + FSRS + hard validation at `seba end`** — the deterministic invariants are
  the part LLMs are worst at and code is best at, and FSRS is a well-benchmarked component (20–30%
  fewer reviews for equal retention). Verdict (a): supported.
- **On-the-fly authoring** — verdict (d): the cost literature is unambiguous, and it enables
  per-session transfer items no pre-authored system could afford.
- **Plain-text git state** — verdict (e): maximally inspectable, free history, right call at N=1.
- **The mastery criterion as written** ("two correct unaided applications, at least one in an unseen
  context") **plus free retakes with no commentary** — this is Keller Plan mechanics (+0.5 σ,
  72 studies) and transfer-testing in one sentence. Rec. 1 hardens it; it does not replace it.
- **Solve-before-you-pose and never-judge-in-the-derivation-turn** — Kestin's team converged on the
  same guard independently and credit it for controlling hallucination in the only LLM tutor RCT
  showing d>0.7.
- **Step-level error attribution** ("name *which* step broke") — this is the d=0.76 mechanism, the
  best-evidenced single feature in the whole literature.

---

### Sources

- Anderson, Corbett, Koedinger & Pelletier (1995), *Cognitive Tutors: Lessons Learned* — https://www.tandfonline.com/doi/abs/10.1207/s15327809jls0402_2
- Corbett & Anderson (1994), *Knowledge Tracing* — https://link.springer.com/article/10.1007/BF01099821
- Pane, Griffin, McCaffrey & Karam (2014), *Effectiveness of Cognitive Tutor Algebra I at Scale* — https://eric.ed.gov/?id=EJ1024233 · WWC https://ies.ed.gov/ncee/wwc/Study/82100 · addendum https://www.rand.org/pubs/working_papers/WR1050.html
- Roschelle, Feng, Murphy & Mason (2016), ASSISTments RCT — https://journals.sagepub.com/doi/full/10.1177/2332858416673968 · https://www.assistments.org/evidence-of-impact · https://eric.ed.gov/?id=ED659541
- Matayoshi & Cosyn (2021), ALEKS/KST — https://jmatayoshi.github.io/publications/JMP2021_KST_ALEKS_preprint.pdf · https://www.aleks.com/about_aleks/publications_kst
- Graesser et al., AutoTutor — https://link.springer.com/content/pdf/10.3758/BF03195563.pdf · https://link.springer.com/article/10.1007/s40593-014-0029-5 · https://files.eric.ed.gov/fulltext/ED586836.pdf
- VanLehn (2011), Educational Psychologist 46(4) — https://www.tandfonline.com/doi/abs/10.1080/00461520.2011.611369 · slides w/ meta-analytic table https://educationgroup.mit.edu/HHMIEducationGroup/wp-content/uploads/2011/02/VanLehnPresentationSlides.pdf
- VanLehn, Graesser et al. (2007), *When Are Tutorial Dialogues More Effective Than Reading?* — https://onlinelibrary.wiley.com/doi/abs/10.1080/03640210709336984
- Settles & Meeder (2016), Half-life regression — https://aclanthology.org/P16-1174/ · https://github.com/duolingo/halflife-regression
- Duolingo Birdbrain — https://blog.duolingo.com/learning-how-to-help-you-learn-introducing-birdbrain/
- Jiang et al. (2021), Duolingo efficacy — https://onlinelibrary.wiley.com/doi/full/10.1111/flan.12600
- FSRS — https://github.com/open-spaced-repetition/free-spaced-repetition-scheduler · https://faqs.ankiweb.net/what-spaced-repetition-algorithm
- Keller Plan / PSI meta-analyses — https://files.eric.ed.gov/fulltext/EJ800986.pdf
- Baker (2016), *Stupid Tutoring Systems, Intelligent Humans* — https://learninganalytics.upenn.edu/ryanbaker/STS-Baker-IJAIED-v15.pdf
- Murray (1999/2003) authoring cost; Aleven et al., CTAT & example-tracing — https://link.springer.com/chapter/10.1007/11774303_7 · https://files.eric.ed.gov/fulltext/ED618912.pdf · https://link.springer.com/article/10.1007/s40593-017-0157-9
- LearnLM (2024) — https://arxiv.org/abs/2412.16429
- Tutor CoPilot (2024) — https://edworkingpapers.com/ai24-1054 · https://files.eric.ed.gov/fulltext/ED661562.pdf
- Kestin et al. (2025) Harvard AI tutor RCT, review — https://etcjournal.com/2025/11/10/review-of-kestin-et-al-s-june-2025-harvard-study-on-ai-tutoring/
