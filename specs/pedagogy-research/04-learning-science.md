# Domain-General Learning Science for a 1:1 LLM Tutor

## 1. Retrieval practice / testing effect

**Core claim.** Retrieving information from memory produces more durable retention than restudying the same material for the same time. Roediger & Karpicke (2006): repeated testing beat repeated rereading at a 1-week delay, 61% vs 40% recall — despite the restudy group rating their own learning higher immediately after study.

**Effect sizes.**
- Rowland (2014), the definitive meta-analysis: 159 studies, overall **g ≈ 0.50** for testing vs restudy. https://pubmed.ncbi.nlm.nih.gov/25150680/
- Classroom-context meta (Schwieren et al. 2017): **g = 0.61**. https://journals.sagepub.com/doi/10.1177/1475725717695149
- Transfer of test-enhanced learning (Pan & Rickard 2018, 192 effect sizes, N=10,382): **d = 0.40** relative to re-exposure controls; transfer is strongest *across test formats*, to *application/inference questions*, and to *problems* — weakest for untested-but-related facts. https://pdf.retrievalpractice.org/transfer/Pan_Rickard_2018.pdf

**Format effects (Rowland).** Free recall > cued recall > recognition. Short-answer produces larger testing effects than multiple choice. Production/generation is the active ingredient, not "being quizzed."

**The critical moderator — retrievability × feedback.** Rowland found **no testing effect at all** for lab studies with *no corrective feedback* and retrievability ≤ 50%. This is the bifurcation model: unsuccessful retrieval without feedback leaves the item worse off than restudy. Feedback rescues failed retrieval attempts and is what makes hard questions safe to ask.

> **Tutor implication.** Every session opens with production, not exposition. Prefer open-ended "explain/derive/state" prompts over multiple choice. Never ask a hard question without being prepared to supply the answer. Target ~70–90% success on review items; below ~50% success, feedback becomes mandatory rather than optional, and the item needs re-teaching not re-quizzing. Do not assume quizzing on X transfers to Y — quiz the thing you want retained, but vary the *format* across sessions.

## 2. Spacing: gaps, ratios, schedules

**Cepeda, Vul, Rohrer, Wixted & Pashler (2008), *Psychological Science* 19(11), 1095–1102.** N > 1,350; inter-study gaps up to 3.5 months; retention intervals (RI) up to 1 year. https://pubmed.ncbi.nlm.nih.gov/19076480/ · https://escholarship.org/uc/item/0kp5q19x

- Optimal gap ≈ **10–20% of the retention interval**. ~20% for RIs of a few weeks, falling to ~**5–10%** for a 1-year RI.
- Worked numbers: RI = 1 week → gap ≈ 1 day. RI = 1 month → gap ≈ 1 week. RI = 1 year → gap ≈ 3–4 weeks.
- Shape: performance rises with gap, peaks, then **declines gradually**. The penalty for overshooting the optimum is much smaller than for undershooting — massing is the expensive error. (Note: one secondary summary encountered during research glossed the ridgeline as "not flat"; the paper's own framing is a broad ridgeline with a gentle post-peak decline. Treat "err long" as the safe direction.)
- **The scheduling consequence:** the optimal gap depends on *when you need the material*. A tutor must know the horizon (exam in 6 weeks? lifelong fluency?) before it can schedule.

**Expanding vs uniform.** Karpicke & Roediger (2007), *JEP:LMC* 33(4), 704–719: expanding schedules win at 10 minutes; **equally-spaced schedules win at 2 days** — with and without feedback. The robust finding is not "expand" but **"delay the first test."** https://learninglab.psych.purdue.edu/downloads/2007/2007_Karpicke_Roediger_JEPLMC.pdf

> **Tutor implication.** Ask for the target horizon and schedule backwards at 10–20%. For open-ended long-term goals, treat the RI as "indefinite" and use a slowly expanding ladder (1d → 3d → 1w → 3w → 2mo), which approximates 10–20% of an ever-growing RI. Do not re-quiz an item within the same session after a successful retrieval — that's massing. When uncertain, schedule the next review *later* rather than sooner.

## 3. Interleaving vs blocking

**Brunmair & Richter (2019), *Psychological Bulletin*, meta-analysis:** pooled **g = 0.42** [0.34, 0.50]. https://www.psychologie.uni-wuerzburg.de/fileadmin/06020400/2019/Brunmair_Richter_in_press__2019_META-ANALYSIS_OF_INTERLEAVED_LEARNING.pdf

**Domain moderation is enormous:**

| Material | g |
|---|---|
| Paintings / artist styles | 0.67 |
| Expository texts | ~0.40 |
| Mathematics (problem types) | 0.34 |
| **Word lists** | **−0.39 (blocking wins)** |

**Boundary condition.** Interleaving helps when the learner's task is **discrimination** — knowing *which* rule/category/method applies. It helps most for *high between-category similarity* and *low within-category similarity*. It hurts when the task is building a single coherent representation from scratch (vocabulary, isolated facts) or acquiring initial procedural fluency in one skill.

> **Tutor implication.** Two-phase: block during acquisition of a genuinely new procedure (get one clean successful execution), then interleave for discrimination as soon as a second confusable procedure exists. Mixed problem sets should ask "which method?" not just "apply this method." Do **not** interleave vocabulary drilling or first exposure to a new concept.

## 4. Desirable difficulties and the fluency illusion

**Bjork & Bjork (1994; 2011).** Conditions that slow acquisition — spacing, testing, interleaving, generation, varied practice, reduced feedback — **impair performance during learning while improving long-term retention and transfer**. https://www.psychologicalscience.org/observer/desirable-difficulties

**The metacognitive trap.** Learners infer learning from *processing fluency*, which is driven by recency and repetition, not encoding durability. Consequences, replicated many times:
- Learners are systematically **overconfident** after massed practice and rereading, **underconfident** after spacing and testing.
- Learners rate the *less effective* condition as more effective, even in studies where they personally experienced both and the test data contradicted them.
- Roediger & Karpicke's restudy group predicted higher performance and scored 21 points lower.

**Kornell & Bjork on students' actual choices:** most students self-report rereading and highlighting as their primary strategies — the two techniques Dunlosky et al. (2013) rated **low utility**. https://journals.sagepub.com/doi/abs/10.1177/1529100612453266

> **Tutor implication — this is the single most important one for an LLM tutor.** A user's in-session satisfaction is an *anti-correlated* signal with learning. "That was too hard," "just show me the answer," "can we go faster" are predictable outputs of the fluency illusion, not evidence the method is wrong. The tutor must (a) not silently optimize for felt ease, (b) explain the difficulty is deliberate *once, briefly*, and (c) still respect an explicit, repeated user decision — but log it rather than quietly drift toward exposition. Design the reward signal around delayed-retrieval success, never around "did the user enjoy this turn."

## 5. Feedback

**Hattie & Timperley (2007), *Review of Educational Research* 77(1), 81–112.** https://conselhopedagogico.tecnico.ulisboa.pt/files/sites/32/hattie-and-timperley-2007.pdf

Three questions: **Feed Up** (where am I going? — goals/criteria), **Feed Back** (how am I going? — current vs criteria), **Feed Forward** (where to next? — the next action).

Four levels, in descending effectiveness for learning:
1. **Task** (FT) — correctness, accuracy. Effective but poorly generalizing.
2. **Process** (FP) — the strategy, the method, the error's cause. **Most powerful for deep learning and transfer.**
3. **Self-regulation** (FR) — how to monitor and direct one's own learning. Powerful for capable learners.
4. **Self** (FS) — "good job," "you're smart." **Least effective, most frequently used.** Diverts attention from performance, process and self-regulation.

**Kluger & DeNisi (1996), *Psychological Bulletin* 119(2), 254–284.** 607 effect sizes, 23,663 observations. Mean **d = 0.41** — but **over one-third of feedback interventions *decreased* performance.** https://mrbartonmaths.com/resourcesnew/8.%20Research/Marking%20and%20Feedback/The%20effects%20of%20feedback%20interventions.pdf

Feedback Intervention Theory's mechanism: feedback works by directing attention. Feedback that moves attention **up to the self** ("you're bad at this," and also "you're brilliant") consumes resources on self-evaluation instead of the task and is where the negative third lives. Feedback directed at task details and task-motivation processes helps.

**Feedback content — van der Kleij, Feskens & Eggen (2015), *RER*, 40 studies, 70 effect sizes:** https://journals.sagepub.com/doi/abs/10.3102/0034654314564881

| Type | d |
|---|---|
| KR (right/wrong only) | **0.05** |
| KCR (correct answer given) | 0.32 |
| **EF (elaborated: why)** | **0.49** |
| EF on *higher-order* outcomes | 0.59 |
| EF on lower-order outcomes | 0.31 |

**Timing.** Immediate feedback favors lower-order/procedural outcomes; delayed feedback favors higher-order and transfer (consistent with desirable difficulties). Overall, delayed timing reduced effect sizes in this meta-analysis, but the interaction with outcome level means there's no universal rule.

> **Tutor implication.** Feedback template: name what's right/wrong at the **task** level (one sentence), then the **process** — what in their method produced the error — then a **feed-forward** next action. Ban self-level praise ("great job!", "you're really good at this") as a default filler; it is the most-used and least-effective form and costs a turn. Never give bare "Correct/Incorrect" — always elaborate. For factual recall, feedback immediately; for problem-solving and conceptual work, let the learner finish the attempt before feeding back, and consider deferring to the end of a problem set.

## 6. Self-explanation and elaborative interrogation

**Bisra, Liu, Nesbit, Salimi & Winne (2018), *Educational Psychology Review*, "Inducing Self-Explanation: a Meta-Analysis."** 69 effect sizes, 64 studies, ~5,917 participants: **g = 0.55**. https://link.springer.com/article/10.1007/s10648-018-9434-x

- Works across subject areas and for both declarative and procedural knowledge.
- Chi et al. (1989/1994): good learners spontaneously self-explain worked examples; *prompting* self-explanation makes poor learners behave like good ones. The effect comes from generating inferences about causal/conceptual relations and from detecting one's own comprehension gaps.
- **Elaborative interrogation** ("why is this true?"): **d ≈ 0.56**, rated *moderate utility* by Dunlosky et al. (2013), narrower and easier to prompt than open self-explanation.

**Caveat worth knowing.** Barbieri et al. (2023) worked-examples meta found self-explanation prompts *attached to worked examples* moderated the effect **negatively** vs worked examples alone — plausibly a load issue when the example is already high element-interactivity. https://link.springer.com/article/10.1007/s10648-023-09745-1

> **Tutor implication.** After a correct answer, the highest-value next turn is "why?" — not a new question. Prompt self-explanation on *the learner's own* answers and errors; be more cautious about stacking explanation prompts on top of a dense worked example the learner is still parsing.

## 7. Cognitive load theory

**Sweller's three loads.** *Intrinsic* (element interactivity of the material relative to learner expertise — irreducible without changing the goal), *extraneous* (imposed by presentation — always reducible, always worth reducing), *germane* (working-memory resources devoted to handling intrinsic load; in Sweller's later formulation it is not an independent additive load but a redistribution). https://link.springer.com/article/10.1007/s10648-010-9128-5

**Element interactivity** is the unifying construct: elements that must be held in working memory *simultaneously* because they are logically related. High element interactivity = high intrinsic load = need for load-reducing design.

**Effects that follow:**
- **Worked example effect**: **g = 0.48** for mathematics (Barbieri et al. 2023, 55 studies, 181 effect sizes). Studying worked solutions beats problem-solving for novices.
- **Expertise reversal**: the same worked example that helps a novice *hurts* an expert — the explanation becomes redundant material the expert must process and reconcile against their own schema. Chen, Kalyuga & Sweller argue this is a special case of the element interactivity effect. https://link.springer.com/article/10.1007/s10648-016-9359-1
- **Completion / fading**: worked example → completion problem (some steps blanked) → full problem, as expertise grows. This is the operational answer to expertise reversal.
- **Split attention**: mutually-referring sources the learner must integrate mentally impose extraneous load — integrate them physically instead.
- **Redundancy**: presenting the same content in two forms *hurts*. Saying the same thing twice in different words is not thoroughness, it's load.
- **Coherence / seductive details**: removing interesting-but-extraneous material improves learning, **g = −0.37 to −0.41** for its presence. One of the largest multimedia effects. https://journals.sagepub.com/doi/abs/10.3102/00346543211052329
- **Segmenting**: learner-paced meaningful chunks beat continuous presentation (small-to-medium effects for retention and transfer). https://link.springer.com/article/10.1007/s10648-018-9456-4

**Overall multimedia-principles meta (2025, 181 studies, 591 effects): g = 0.37**, with a declining trend over years. https://www.sciencedirect.com/science/article/pii/S1747938X25000673

> **Tutor implication — turn length.** The coherence and redundancy effects say directly: an LLM tutor's default verbosity is *extraneous load*. Every analogy, caveat, motivational aside, and restatement is a seductive detail with a measured negative effect. Rules: one idea per turn; hard ceiling of roughly 100–150 words per teaching turn on high-element-interactivity material; never restate the same point in two phrasings; no preamble; no recap of what was just said. Segment: teach one chunk, then hand control back. On the learner's first encounter with a hard procedure, give a worked example rather than a problem; fade to completion problems; stop giving examples once they succeed unaided (expertise reversal).

## 8. Metacognition and calibration

- **Judgments of learning (JOLs)** made immediately after study are contaminated by short-term memory contents and are poorly diagnostic. **Delayed JOLs** are substantially more accurate (Rhodes & Tauber 2011 meta-analysis) — the delay forces an actual retrieval attempt, which is what the judgment should be based on. https://www.researchgate.net/publication/49740681_The_Influence_of_Delaying_Judgments_of_Learning_on_Metacognitive_Accuracy_A_Meta-Analytic_Review
- **Overconfidence is worst in the lowest performers** (Dunning–Kruger pattern), i.e. exactly the learners whose study decisions matter most.
- **Failing to retrieve reduces overconfidence** and improves calibration — a testing benefit independent of memory. https://www.sciencedirect.com/science/article/abs/pii/S1053810014001469
- **Prediction-before-answer**: asking the learner to commit to a confidence rating or a prediction before revealing the answer converts a passive exposure into (a) a retrieval attempt and (b) a calibration data point.

**Pretesting / errorful generation.** Richland, Kornell & Kao (2009), *JEP:Applied*: being asked about material *before* studying it improves later memory for that material, **even when the pretest answers are all wrong** — provided the correct answers are subsequently studied. https://learninglab.uchicago.edu/Pre-Testing_files/RichlandKornellKao.pdf
- Meta-analysis of prequestions: **g = 0.66** for prequestioned information; **g = 0.01** for other, non-prequestioned information in the same lesson — the benefit is *specific*, not general. https://link.springer.com/article/10.1007/s10648-025-10075-7
- Pan & Sana (2021): pretesting beat post-test retrieval practice by **d = 0.30**.

> **Tutor implication.** Before teaching anything new, ask about it first — a guess, a prediction, a "what do you think this would be?" Wrong answers are productive, so long as the correct answer follows. Because the prequestion benefit is item-specific, prequestion the things that matter most, not the topic in general. Before revealing any answer, get a commitment ("what's your answer, and how sure are you, 0–10?"). Ask the learner to predict their performance on the *next* session's review, then show them the actual result — this is the cheapest calibration training available.

## 9. Generation and productive failure

**Generation effect.** Bertsch, Pesta, Wiscott & McDaniel (2007), *Memory & Cognition* 35, 201–210: 445 effect sizes over 86 studies, **d = 0.40** for generating vs reading. https://mcdaniel97.github.io/Publications/Bertsch%20et%20al.%202007.pdf

**Productive failure.** Sinha & Kapur (2021), *Review of Educational Research*: 53 studies, 166 comparisons, >12,000 participants. Problem-solving *before* instruction (PS-I) beats instruction-first on conceptual understanding and transfer, **d = 0.36** [0.20, 0.51], rising to **d = 0.58** with high fidelity to PF design principles. https://journals.sagepub.com/doi/10.3102/00346543211019105

**The essential qualifier.** Unscaffolded PS-I shows **g = −0.08** [−0.34, 0.28] — i.e. nothing. Productive failure only works when (a) the problem is designed so learners generate multiple *representations and solution attempts* even if none succeed, (b) instruction *follows and explicitly builds on* the learners' generated attempts, comparing them against the canonical solution, and (c) affective support keeps the learner engaged through failure. Failure without the consolidation phase is just failure. Note also the apparent tension with the worked-example effect: worked examples win for *procedural* skill acquisition in novices; productive failure wins for *conceptual understanding and transfer* — and PF's problems are deliberately beyond current competence.

> **Tutor implication.** Ask the learner to attempt before explaining, then build the explanation out of *their specific attempt* ("you tried X — that gets you here, and breaks here; the canonical method fixes it by…"). Never let a struggle end without consolidation. Never make the learner generate what they cannot possibly produce *and* then fail to close the loop.

## 10. Deliberate practice

**Ericsson, Krampe & Tesch-Römer (1993)**: expert performance arises from prolonged, effortful, feedback-rich practice specifically targeting current weaknesses at the edge of competence, designed by a teacher — not from mere experience.

**Macnamara, Hambrick & Oswald (2014), *Psychological Science*:** deliberate practice explains **26%** of variance in games, **21%** music, **18%** sports, **4%** education, **<1%** professions; ~**12%** overall in one model. https://journals.sagepub.com/doi/abs/10.1177/0956797614535810

**Ericsson's rebuttal** (Frontiers 2019): the meta-analysis included studies whose "practice" measures don't meet the deliberate-practice definition (unstructured play, total accumulated experience), so it estimates the effect of *practice*, not *deliberate practice*. https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2019.02396/full

**What survives the fight, uncontested by either side:** practice matters a great deal; practice *quality* matters more than volume; the design features — targeting current weaknesses, immediate informative feedback, repetition with refinement, full attention, beyond-comfort difficulty — are individually supported by other literatures. What does *not* survive: "10,000 hours," "deliberate practice is sufficient," "individual differences don't matter."

> **Tutor implication.** Keep the mechanics (target the weak edge, feedback every rep, stay just past comfortable). Never claim to the user that hours are the whole story, and never quote 10,000 hours.

## 11. Mastery learning and criterion-based advancement

- **Bloom (1984), "The 2 Sigma Problem":** 1:1 tutoring + mastery learning ≈ **2 SD** over conventional classroom; group mastery learning ≈ **1 SD**. https://en.wikipedia.org/wiki/Bloom%27s_2_sigma_problem
- **Kulik, Kulik & Bangert-Drowns (1990), *RER*:** mastery learning programs (including Keller's PSI) show typical effects around **0.5 SD** on examination performance, with larger effects for weaker students. https://journals.sagepub.com/doi/10.3102/00346543060002265
- **The correction:** Nickow, Oreopoulos & Quan (2020) — 96 randomized tutoring studies, mean **0.37 SD**; **none** reached 2 sigma. Bloom's figure does not replicate and should not be quoted as a target. https://www.educationnext.org/two-sigma-tutoring-separating-science-fiction-from-science-fact/

**Keller Plan (PSI) mechanics that carry over:** self-pacing; unit mastery required before advancing; repeated alternate-form testing with no penalty for retakes; written material as primary content vehicle with the tutor's time spent on assessment and remediation.

> **Tutor implication.** Advancement is criterion-based, not time-based or curriculum-position-based: don't move to topic N+1 until N passes a stated criterion (e.g. correct, unaided, on a delayed retrieval, twice). Make the criterion explicit to the learner (this is Hattie's "feed up"). Retakes carry no penalty and no commentary. And keep expectations honest — 0.3–0.5 SD is what good tutoring buys, not 2 SD.

## 12. Transfer

- **Barnett & Ceci (2002), *Psychological Bulletin*, taxonomy for far transfer:** transfer claims are incomparable without specifying 9 dimensions (content: learned skill, performance change, memory demands; context: knowledge domain, physical, temporal, functional, social, modality). Of 14 studies reviewed, all "far transfer" demonstrations were *near* on ≥3 of 6 dimensions. https://rapunselshair.pbworks.com/f/barnett_2002.pdf
- **Why transfer fails:** knowledge is encoded bound to surface features of the training context; at test, surface dissimilarity prevents retrieval of the relevant structure. The learner often *has* the knowledge and fails to access it.
- **What improves it:**
  - **Analogical encoding — Gentner, Loewenstein & Thompson (2003), *JEP* 95(2), 393–408:** explicitly *comparing two cases* that share deep structure but differ in surface features causes schema abstraction. In the negotiation studies, students who drew an analogy across two cases were **nearly 3× more likely** to transfer the strategy than students who studied the same two cases separately. Comparison support increased transfer further. https://groups.psych.northwestern.edu/gentner/papers/GentnerLoewensteinThompson03.pdf
  - **Varied practice** across contexts, surface features, and problem framings.
  - Explicit **abstract schema articulation** — having the learner state the principle in context-free terms.
  - Retrieval practice transfers (d = 0.40) best across *formats* and to *application/inference* questions — so vary the question format deliberately.

> **Tutor implication.** Never teach a principle from one example. Present two superficially different instances *side by side* and ask "what's the same about these?" — the comparison is the mechanism, not the exposure. Then have the learner state the shared principle in their own words with the surface details stripped out. Make deliberately far-surface practice problems for anything meant to generalize, and don't claim a concept is learned on the basis of same-format success.

## 13. Motivation

**Self-determination theory (Deci & Ryan).** Autonomy, competence, relatedness are basic needs; satisfying them produces autonomous motivation and persistence, thwarting them produces controlled motivation and dropout. Meta-analysis of SDT-based educational interventions (36 studies, 137 effect sizes, N = 9,433) supports intervention effectiveness, with **competence the strongest predictor** of self-determined motivation, then autonomy, then relatedness. https://www.sciencedirect.com/science/article/abs/pii/S0023969024000572

Practical: autonomy = meaningful choice + rationale for required activities + acknowledging negative affect ("yes, this part is tedious, here's why it's on the list"); competence = optimal challenge + informational (not controlling) feedback; relatedness = the tutor being a consistent, non-judging presence.

**Achievement goals — Huang (2012) meta, 151 studies, N = 52,986:** mastery-approach **r = .10** with achievement, performance-approach **r = .07**, performance-avoidance **r = −.12**, mastery-avoidance negative. Effects are small; mastery-approach is the most adaptive framing and performance-avoidance the most maladaptive. https://www.researchgate.net/publication/232500545_Discriminant_and_Criterion-Related_Validity_of_Achievement_Goals_in_Predicting_Academic_Achievement_A_Meta-Analysis

**Mindset — be accurate here.** Sisk et al. (2018), *Psychological Science*, two meta-analyses: mindset–achievement correlation is very weak (k = 273, N = 365,915); **mindset interventions average d = 0.08** across 43 interventions, with effects concentrated in at-risk and low-SES students. https://journals.sagepub.com/doi/10.1177/0956797617739704 The National Study of Learning Mindsets (Yeager et al. 2019, *Nature*) found a real but small effect (~0.1 GPA points) in lower-achieving students only. Li & Bates (2019) failed to replicate Mueller & Dweck (1998) on praise. Yeager & Dweck (2020) contest the framing, not the numbers. Bottom line: a one-shot mindset message is a **small, conditional** effect, not a lever.

**Interest — Hidi & Renninger (2006) four-phase model:** triggered situational → maintained situational → emerging individual → well-developed individual interest. Early phases require *external* support (novelty, tasks with clear meaning, hands-on activity); later phases become self-sustaining and self-generating of questions. Interest is developed, not discovered.

> **Tutor implication.** Support competence first — it's the strongest lever. Give real choices (which topic today, which of these two problem types) with reasons for non-negotiables. Frame goals as mastery-approach ("get this method reliable") and never as social comparison or failure-avoidance. Do **not** deliver mindset homilies; the process-level feedback in §5 already delivers what mindset messaging tries to deliver, with better evidence. For a new subject, scaffold interest actively in early sessions rather than assuming intrinsic motivation exists.

## 14. Rules to implement

1. **Open with retrieval, not exposition.** First turn of any session is a question about prior material, in production format (free/cued recall), never recognition.
2. **Never ask without being ready to answer.** Elaborated feedback (why, not just what) after every attempt; bare "correct/incorrect" is worth d = 0.05 and is not acceptable output.
3. **Feedback shape: task → process → feed-forward.** One sentence on correctness, then what in their method caused it, then the next action. Zero self-level praise as filler.
4. **Prequestion before teaching.** Elicit a guess or prediction on the specific items that matter before any new exposition. Wrong guesses are fine; always follow with the correct answer.
5. **Require a commitment before every reveal**, with a confidence number where cheap. Show the learner their calibration record.
6. **Schedule reviews at 10–20% of the target retention interval.** Ask the horizon. Absent one, use an expanding ladder (1d, 3d, 1w, 3w, 2mo, 6mo). When in doubt, schedule later, not sooner. Never re-quiz an item successfully retrieved earlier in the same session.
7. **Block, then interleave.** Block until one clean unaided success on a new procedure; interleave the moment a confusable sibling exists. Mixed sets must require choosing the method. Don't interleave vocabulary or first exposure.
8. **Worked example → completion problem → full problem.** Give the example for novel high-element-interactivity procedures; fade as soon as success appears (expertise reversal is a real cost, not a nicety).
9. **Cap turn length hard.** One idea per turn, ~100–150 words on hard material, no restatement, no preamble, no recap, no seductive analogies. Coherence effect g ≈ −0.4 says the extra prose actively costs learning.
10. **After a correct answer, ask "why?" before asking anything new.** Self-explanation g = 0.55 is cheaper than a new item.
11. **Attempt before instruction on conceptual material; always consolidate.** Build the explanation out of the learner's specific attempt. Unscaffolded struggle without consolidation is worth zero.
12. **Teach principles from two contrasting cases, side by side, with an explicit "what's shared?" prompt** and a learner-stated abstract principle. Never from one example.
13. **Vary surface features and question format** across sessions for anything meant to transfer. Same-format success is not evidence of understanding.
14. **Advance on criterion, not on coverage or time.** State the criterion aloud. Retakes are unpenalized and uncommented.
15. **Treat requests for ease as expected, not as evidence.** Explain the desirable-difficulty rationale once, briefly; then honor an explicit repeated user decision while recording it. Never let session-level comfort become the optimization target.
16. **Support competence and autonomy concretely** — real choices, rationale for requirements, optimal challenge, informational feedback. No mindset sermons, no social comparison, no praise-as-motivation.
17. **Target ~70–90% retrieval success.** Below ~50% without feedback the testing effect vanishes; re-teach rather than re-quiz.
18. **Delay the first review** rather than expanding aggressively — the robust finding is first-test delay, not the expansion pattern.

## 15. Myths not to encode

- **Learning styles / VAK / the meshing hypothesis.** Pashler, McDaniel, Rohrer & Bjork (2008): ~70 studies reviewed, one gave partial support, two clearly contradicted it; "no adequate evidence base to justify incorporating learning-styles assessments into general educational practice." Never ask a user their learning style; never adapt modality to a self-reported preference. https://journals.sagepub.com/doi/10.1111/j.1539-6053.2009.01038.x
- **Bloom's 2 sigma as an achievable target.** Doesn't replicate; 0.37 SD is the modern tutoring estimate.
- **10,000 hours / deliberate practice as sufficient.** Practice quality matters; hours alone explain a modest fraction of variance.
- **Growth-mindset interventions as a major lever.** d ≈ 0.08 overall; real but small and concentrated in at-risk students. Don't build a tutor personality around it.
- **"Learners know what's working for them."** Systematically inverted judgments; the fluency illusion is one of the best-replicated findings here.
- **Praise as feedback.** Hattie's least effective level; a third of feedback interventions in Kluger & DeNisi made performance *worse*, concentrated where attention moved to the self.
- **Expanding retrieval as strictly superior.** Equal spacing wins at real retention intervals.
- **"Interleaving is always better."** g = −0.39 for word lists; it's a discrimination tool.
- **"More explanation is more helpful."** Redundancy, coherence, and expertise-reversal effects all say the opposite.
- **Right-brain/left-brain learners, the "learning pyramid" retention percentages (10% of what we read…), Dale's Cone as data, multiple-intelligences-as-modalities, digital natives.** No evidentiary basis.
- **Rereading and highlighting as study strategies.** Rated *low utility* by Dunlosky et al. (2013) and the most commonly self-reported — the tutor should actively displace them.

## Sources

- [Cepeda et al. 2008, Spacing Effects in Learning: A Temporal Ridgeline of Optimal Retention](https://pubmed.ncbi.nlm.nih.gov/19076480/) · [full text](https://escholarship.org/uc/item/0kp5q19x)
- [Karpicke & Roediger 2007, Expanding vs Equally Spaced Retrieval](https://learninglab.psych.purdue.edu/downloads/2007/2007_Karpicke_Roediger_JEPLMC.pdf)
- [Roediger & Karpicke 2006, The Power of Testing Memory](http://psychnet.wustl.edu/memory/wp-content/uploads/2018/04/Roediger-Karpicke-2006_PPS.pdf)
- [Rowland 2014, Testing vs Restudy: Meta-Analytic Review](https://pubmed.ncbi.nlm.nih.gov/25150680/) · [PDF](https://courseware.epfl.ch/assets/courseware/v1/fdde2f0aa590bf3b1324077a6bf1540c/asset-v1:EPFL+DEMO+2020+type@asset+block/Rowland2014-meta-analysis.pdf)
- [Pan & Rickard 2018, Transfer of Test-Enhanced Learning](https://pdf.retrievalpractice.org/transfer/Pan_Rickard_2018.pdf)
- [Schwieren et al. 2017, Testing Effect in the Psychology Classroom](https://journals.sagepub.com/doi/10.1177/1475725717695149)
- [Brunmair & Richter 2019, Similarity Matters: Meta-Analysis of Interleaved Learning](https://www.psychologie.uni-wuerzburg.de/fileadmin/06020400/2019/Brunmair_Richter_in_press__2019_META-ANALYSIS_OF_INTERLEAVED_LEARNING.pdf)
- [Bjork & Bjork, Desirable Difficulties (APS Observer)](https://www.psychologicalscience.org/observer/desirable-difficulties)
- [Hattie & Timperley 2007, The Power of Feedback](https://conselhopedagogico.tecnico.ulisboa.pt/files/sites/32/hattie-and-timperley-2007.pdf)
- [Kluger & DeNisi 1996, Effects of Feedback Interventions on Performance](https://mrbartonmaths.com/resourcesnew/8.%20Research/Marking%20and%20Feedback/The%20effects%20of%20feedback%20interventions.pdf)
- [van der Kleij, Feskens & Eggen 2015, Feedback in Computer-Based Learning: Meta-Analysis](https://journals.sagepub.com/doi/abs/10.3102/0034654314564881)
- [Bisra et al. 2018, Inducing Self-Explanation: a Meta-Analysis](https://link.springer.com/article/10.1007/s10648-018-9434-x)
- [Sweller 2010, Element Interactivity and Intrinsic/Extraneous/Germane Load](https://link.springer.com/article/10.1007/s10648-010-9128-5)
- [Chen, Kalyuga & Sweller 2017, Expertise Reversal as Element Interactivity](https://link.springer.com/article/10.1007/s10648-016-9359-1)
- [Barbieri et al. 2023, Meta-analysis of the Worked Examples Effect on Mathematics](https://link.springer.com/article/10.1007/s10648-023-09745-1)
- [Noetel et al. 2022, Multimedia Design for Learning: Meta-Meta-Analysis](https://journals.sagepub.com/doi/abs/10.3102/00346543211052329)
- [Meta-analysis of the Segmenting Effect 2019](https://link.springer.com/article/10.1007/s10648-018-9456-4)
- [Mayer multimedia principles meta-analysis 2025](https://www.sciencedirect.com/science/article/pii/S1747938X25000673)
- [Richland, Kornell & Kao 2009, The Pretesting Effect](https://learninglab.uchicago.edu/Pre-Testing_files/RichlandKornellKao.pdf)
- [Prequestions multilevel meta-analysis 2025](https://link.springer.com/article/10.1007/s10648-025-10075-7)
- [Pan & Sana 2021, Pretesting vs Posttesting](https://osf.io/preprints/psyarxiv/un87v_v1)
- [Rhodes & Tauber 2011, Delayed JOLs Meta-Analysis](https://www.researchgate.net/publication/49740681_The_Influence_of_Delaying_Judgments_of_Learning_on_Metacognitive_Accuracy_A_Meta-Analytic_Review)
- [Bertsch et al. 2007, The Generation Effect: A Meta-Analytic Review](https://mcdaniel97.github.io/Publications/Bertsch%20et%20al.%202007.pdf)
- [Sinha & Kapur 2021, When Problem Solving Followed by Instruction Works](https://journals.sagepub.com/doi/10.3102/00346543211019105)
- [Macnamara, Hambrick & Oswald 2014, Deliberate Practice Meta-Analysis](https://journals.sagepub.com/doi/abs/10.1177/0956797614535810) · [Ericsson 2019 rebuttal](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2019.02396/full)
- [Kulik, Kulik & Bangert-Drowns 1990, Effectiveness of Mastery Learning Programs](https://journals.sagepub.com/doi/10.3102/00346543060002265) · [Nickow, Oreopoulos & Quan on two-sigma](https://www.educationnext.org/two-sigma-tutoring-separating-science-fiction-from-science-fact/)
- [Barnett & Ceci 2002, A Taxonomy for Far Transfer](https://rapunselshair.pbworks.com/f/barnett_2002.pdf)
- [Gentner, Loewenstein & Thompson 2003, Learning and Transfer: A General Role for Analogical Encoding](https://groups.psych.northwestern.edu/gentner/papers/GentnerLoewensteinThompson03.pdf)
- [SDT interventions in education meta-analysis 2024](https://www.sciencedirect.com/science/article/abs/pii/S0023969024000572)
- [Huang 2012, Achievement Goals and Academic Achievement Meta-Analysis](https://www.researchgate.net/publication/232500545_Discriminant_and_Criterion-Related_Validity_of_Achievement_Goals_in_Predicting_Academic_Achievement_A_Meta-Analysis)
- [Sisk et al. 2018, To What Extent Are Growth Mind-Sets Important? Two Meta-Analyses](https://journals.sagepub.com/doi/10.1177/0956797617739704)
- [Pashler, McDaniel, Rohrer & Bjork 2008, Learning Styles: Concepts and Evidence](https://journals.sagepub.com/doi/10.1111/j.1539-6053.2009.01038.x)
- [Dunlosky et al. 2013, Improving Students' Learning With Effective Learning Techniques](https://journals.sagepub.com/doi/abs/10.1177/1529100612453266)
