# The Empirical Science of 1:1 Tutoring — Concrete Conversational Mechanisms

## 1. The effect size question: how good is 1:1 tutoring, really?

**Bloom, B. S. (1984). "The 2 Sigma Problem: The Search for Methods of Group Instruction as Effective as One-to-One Tutoring." *Educational Researcher* 13(6), 4–16.**
Claim: tutored + mastery-learning students outperformed conventional classroom students by ~2.0 SD (average tutee above 98th percentile of control).

**The 2σ figure does not survive scrutiny.** The critical detail is that Bloom's "tutoring" condition was *tutoring + mastery learning*: tutees were held to a 90% mastery criterion with individualized corrective loops, while controls advanced at ~80% with group-level correction. The confound is the mastery criterion, not the dialogue.

- Cohen, Kulik & Kulik (1982), meta-analysis of 65 studies: **d ≈ 0.40** (Graesser & Person 1994 cite 0.4 from 52 studies).
- **Nickow, Oreopoulos & Quan (2020/2024), "The Impressive Effects of Tutoring on PreK-12 Learning," NBER WP 27476 / *AERJ*.** 96 RCTs. Pooled **d = 0.37 SD** (~14 percentile points). Teacher/paraprofessional tutors > nonprofessional/parent tutors. Effects strongest in early grades and in reading (early) / math (later). https://www.nber.org/system/files/working_papers/w27476/w27476.pdf
- Kulik et al. (1990) on mastery learning: **d = 0.5 on experimenter-made tests vs d = 0.08 on standardized tests** — most of the effect is overfitting to the assessment.
- Nintil's systematic review (https://nintil.com/bloom-sigma/) concludes Bloom's d = 2.0 "seems due mostly to holding tutees to higher mastery standards"; also documents publication bias (published d ≈ 0.3, unpublished d ≈ 0.16) and small-sample inflation (Cheung & Slavin 2016: d = 0.38 small-N vs d = 0.11 large-N).

**Implication for an LLM tutor:** the biggest lever isn't dialogue eloquence — it's the *mastery criterion and the corrective loop*. Do not advance a topic until a demonstrated criterion is met; make the criterion explicit and enforce it. Also: be suspicious of assessing on the exact material you just taught; test transfer, not recall of the session.

---

## 2. VanLehn 2011 — the central paper

**VanLehn, K. (2011). "The Relative Effectiveness of Human Tutoring, Intelligent Tutoring Systems, and Other Tutoring Systems." *Educational Psychologist* 46(4), 197–221.** https://www.tandfonline.com/doi/abs/10.1080/00461520.2011.611369

Received wisdom before this paper: answer-based systems d ≈ 0.3, ITS d ≈ 1.0, human tutors d ≈ 2.0. VanLehn's meta-analysis (studies 1975–2010) found instead:

| Condition (vs. no tutoring) | Effect size |
|---|---|
| Answer-based computer tutoring | **d ≈ 0.31** |
| Step-based ITS | **d ≈ 0.76** |
| Substep-based ITS | **d ≈ 0.40** (no better than step-based) |
| Human tutoring | **d ≈ 0.79** |

Granularity definitions:
- **Answer-based**: student submits only the final answer; feedback/hints keyed to the answer.
- **Step-based**: student's work is decomposed into steps; the tutor gives feedback and hints *per step* (e.g. Cognitive Tutors, Andes).
- **Substep-based**: the tutor additionally engages in dialogue *within* a step, eliciting the reasoning that produces the step (e.g. Why2-Atlas, AutoTutor).

**The interaction plateau hypothesis.** Effectiveness rises sharply from answer-granularity to step-granularity and then **plateaus**. Going finer (substep dialogue, or full natural-language human tutoring) buys little or nothing more. See also VanLehn's "The Interaction Plateau: Answer-Based Tutoring < Step-Based Tutoring = Natural Tutoring" (ITS 2010 keynote).

Why the plateau? VanLehn's preferred account routes through Chi's ICAP: what matters is that the student *generates* the content of each step and gets feedback on it. Once the interaction is fine-grained enough to force step-level generation plus step-level feedback, further conversational richness adds no measurable learning.

**Implications for an LLM tutor (these are the load-bearing ones):**
1. **Operate at step granularity, not answer granularity.** Never accept or evaluate only a final answer. Decompose the problem and require/evaluate each step. This single design choice is worth ~0.45 SD in the meta-analytic record — bigger than anything else on this list.
2. **Do not assume conversational sophistication buys learning.** A chatty, dialogic tutor that operates at answer granularity is *worse* than a terse tutor that checks every step. The LLM's natural advantage (fluent dialogue) is not where the effect lives.
3. Substep dialogue is where an LLM is uniquely capable — but the evidence says it's on the plateau. Use it for *diagnosis* (finding which step is wrong and why) rather than as an end in itself.

**Corollary from VanLehn, Graesser, Jackson, Jordan, Olney & Rosé (2007), "When Are Tutorial Dialogues More Effective Than Reading?" *Cognitive Science* 31(1), 3–62.** Seven content-matched experiments in qualitative physics. Dialogue beat reading **only when the material was pitched above the student's preparation** (novices given intermediate-level content) — large effect sizes there, null when content matched the learner's level.
**Implication:** interactive tutoring earns its cost specifically when the material is *too hard to read*. If the material is well-matched to the learner, an explanation or a text plus practice is as good — and cheaper. Route effort by mismatch: escalate to dialogue when the student is over their head, drop to exposition + practice when they aren't.

---

## 3. What naturalistic tutoring actually looks like

**Graesser, A. C., Person, N. K., & Magliano, J. P. (1995). "Collaborative dialogue patterns in naturalistic one-to-one tutoring." *Applied Cognitive Psychology* 9(6), 495–522.** https://onlinelibrary.wiley.com/doi/abs/10.1002/acp.2350090604

The **5-step tutoring frame**, the dominant observed pattern:
1. Tutor asks a question (or presents a problem).
2. Student answers.
3. Tutor gives **short feedback** on answer quality.
4. Tutor and student **collaboratively improve the answer** over multiple turns.
5. Tutor **assesses** whether the student now understands.

Step 4 is where the length is: exchanges ran ~5 turns (research methods) to ~10 turns (algebra), vs ~3 turns for classroom IRE sequences. Step 5 is routinely done badly — tutors ask "Do you understand?" and take "yes" at face value.

Other findings: unskilled tutors follow a **curriculum script** (a prepared topic agenda) rather than adapting deeply; **the Socratic method was essentially absent**; 34% of feedback coded "neutral" from audio turned out to be positive or negative once video was consulted (i.e., much real feedback is nonverbal — unavailable in text).

**Graesser, A. C., & Person, N. K. (1994). "Question Asking During Tutoring." *AERJ* 31(1), 104–137.** https://gwern.net/doc/psychology/spaced-repetition/1994-graesser.pdf

Hard numbers (research methods = college; algebra = 7th grade):
- Student questions per hour: classroom ≈ **0.11 per individual student** (3.0/hr class-wide ÷ 26.7 students); tutoring ≈ **26.5 per student**. → **~240× more**.
- Tutor questions per hour: **95.2** (research methods), **112.1** (algebra) vs ~69/hr for classroom teachers — only **1.5×** higher.
- **80% of all questions in a tutoring session are asked by the tutor** (82% research methods, 78% algebra) — vs 96% in classrooms.
- Short-answer questions dominate over long-answer for both parties (.56 vs .38 overall; tutors .60/.35, students .52/.40).
- Only **~4% of teacher questions in classrooms are high-level**; most are short-answer grilling on explicit material.
- Student achievement correlated with the **quality** of student questions (after some tutoring experience), **not** with their frequency.

**Implications:**
- The 5-step frame is a good default control loop for an LLM tutor, but **step 5 must be an actual probe, not "does that make sense?"** — ask the student to apply, restate in a new context, or predict a different case.
- Question *quality* over quantity. Don't optimize for asking a lot; optimize for deep-reasoning questions (why / how / what-if / what-would-happen-if-not / how-does-this-differ-from).
- A tutoring session should *create room for student questions* — that's the 240× signal — and should **train the student to ask better ones** (model the question, then hand the form back: "what question should you be asking here?").
- **High specification**: Graesser & Person note a good tutor poses questions with high enough specification that the student can parse them. "What are the variables in the factorial design in Experiment 1?" not "What are those?" LLMs drift to vague prompts ("what do you notice?") which are low-specification and produce floundering.

**Person, Kreuz, Zwaan & Graesser (1995), "Pragmatics and pedagogy: Conversational rules and politeness strategies may inhibit effective tutoring," *Cognition and Instruction*.** Tutors' politeness norms make them reluctant to give clear negative feedback; they hedge, praise vaguely, and blur errors. This *harms* learning by destroying the feedback signal.
**Implication:** this is the single most LLM-relevant finding in the corpus. RLHF'd models are maximally polite and maximally hedging — exactly the failure mode identified in 1995. **Negative feedback must be unambiguous.** "That's not right — the sign is wrong" beats "Good thinking! Although we might want to reconsider the sign."

---

## 4. Chi: interactivity and "tutors should say less"

**Chi, M. T. H., Siler, S. A., Jeong, H., Yamauchi, T., & Hausmann, R. G. (2001). "Learning from human tutoring." *Cognitive Science* 25(4), 471–533.** https://onlinelibrary.wiley.com/doi/10.1207/s15516709cog2504_1

Three competing hypotheses: tutor-centered (learning comes from tutor explanations), student-centered (from student construction), interactive (from co-construction). Study 2 manipulated tutor behavior: tutors were **suppressed from giving explanations and feedback** and restricted to content-free prompting. Result: **students learned just as much.** Gains were attributed to more and deeper *scaffolding episodes* and to students taking control (reading more on their own).

**Chi, M. T. H. (2009). "Active-Constructive-Interactive: A Conceptual Framework for Differentiating Learning Activities." *Topics in Cognitive Science* 1(1), 73–105**; and **Chi & Wylie (2014), "The ICAP Framework," *Educational Psychologist* 49(4), 219–243.**
Predicted ordering of learning outcomes: **Interactive > Constructive > Active > Passive.**
- *Passive*: receiving (reading, listening).
- *Active*: manipulating (highlighting, copying, pausing a video).
- *Constructive*: generating output beyond what was given (self-explaining, drawing an inference, posing a question).
- *Interactive*: dialogue in which **both partners contribute substantively** and each builds on the other's contribution. Crucially, a dialogue only counts as Interactive if the student's turns are constructive — otherwise it's Active dressed as dialogue.

**Chi, Siler & Jeong (2004), "Can Tutors Monitor Students' Understanding Accurately?" *Cognition and Instruction* 22(3), 363–387.** Even adult non-peer tutors are poor at diagnosing what the tutee actually understands; their assessments correlate weakly with tutee knowledge. Tutors run on their own curriculum script, not a real student model.

**Implications:**
- **The tutor's explanation is not what teaches.** An LLM tutor that answers well is optimizing the wrong variable. Budget: student generative output should dominate the transcript.
- A concrete ICAP test to apply before every turn: *does my next turn cause the student to produce something beyond what they've been given?* If not, it's a Passive/Active turn and should be replaced or cut.
- **Assume your student model is wrong.** Chi 2004 says diagnosis is the hard part and humans fail at it. An LLM should surface and test its model explicitly ("I think you're treating X as Y — is that right?") rather than silently acting on it, and should re-diagnose after any surprising answer.
- Content-free prompting ("Can you say more about that?", "Why?", "What about the other case?") is empirically sufficient in many episodes. It's also cheap and safe — it can't inject a wrong explanation.

---

## 5. Contingency and fading

**Wood, D., Bruner, J. S., & Ross, G. (1976). "The role of tutoring in problem solving." *J. Child Psychology and Psychiatry* 17, 89–100.** (origin of "scaffolding")
**Wood, D., Wood, H., & Middleton, D. (1978). "An experimental evaluation of four face-to-face teaching strategies." *Int. J. Behavioral Development* 1(2), 131–147.** https://journals.sagepub.com/doi/10.1177/016502547800100203

**The contingency rule** — the most directly implementable rule in the whole literature:
> **If the child succeeds, when next intervening offer less help. If the child fails, when next intervening take more control.**

Five levels of help (increasing control):
1. General verbal encouragement / prompt to act.
2. Specific verbal instruction (name the relevant feature).
3. Indicate materials / narrow the search space.
4. Prepare for assembly / set up the step.
5. **Demonstrate** — do the operation for them.

Children under contingent instruction outperformed all other strategies (including consistently-high and consistently-low help) on the task and on later independent performance. Aim: *"the child will never succeed too easily or fail too often."*

**Wood, H., & Wood, D. (1999). "Help seeking, learning and contingent tutoring." *Computers & Education* 33, 153–169.** https://www.tlu.ee/~kpata/haridustehnoloogiaTLU/tutoring.pdf
Their QUADRATIC system operationalized it: help is learner-requested, at one of five levels; the level is set by the learner's recent history — after a level-3 hint followed by a success, the system next offers **level 2**; if the learner requests more help instead, it escalates to level 4. Key stated policy: **"After about three cues of increasing levels of explicitness, the tutor will provide the answer or demonstrate the next step."** Fading: on success, drop a level; but *if the learner needed a lot of help on one problem, offer a bit of unsolicited help on the next*.

Also from this paper: contingency has three components — **domain contingency** (choosing what to focus on), **temporal contingency** (intervening at the right moment), **instructional contingency** (the right amount of support). And a warning: leaving help-seeking entirely to the learner disadvantages low achievers, who are least aware they need help and most reluctant to ask. Nelson-Le Gall (1985) and others document this.

**Implications:**
- Implement a literal **hint ladder with 5 levels and a state variable per skill**. Level index goes down on success, up on request/failure. **Cap at 3 escalations, then give the answer + explanation** — floundering past that point is unproductive.
- **Never wait to be asked.** Do not rely on "let me know if you want a hint." Low-prior-knowledge learners won't ask. Offer proactively when temporal contingency says so (a stall, a repeated error, a non-answer).
- Fading is a *cross-problem* policy, not just within-problem: if the last problem needed level 4, open the next one at level 2 unsolicited; if it needed nothing, open at level 0.

---

## 6. Errors, impasses, and productive struggle

**VanLehn, K., Siler, S., Murray, C., Yamauchi, T., & Baggett, W. (2003). "Why Do Only Some Events Cause Learning During Human Tutoring?" *Cognition and Instruction* 21(3), 209–249.** https://www.tandfonline.com/doi/abs/10.1207/S1532690XCI2103_01 — ~125 hours of expert physics tutoring analyzed.
Central finding: **learning required that the student first reach an impasse.** When students were *not* at an impasse, tutorial explanations were essentially never associated with learning, no matter how good the explanation. Once at an impasse, explanations sometimes produced learning (and different explanation types mapped to different knowledge types).

**Merrill, D. C., Reiser, B. J., Ranney, M., & Trafton, J. G. (1992). "Effective Tutoring Techniques: A Comparison of Human Tutors and Intelligent Tutoring Systems." *Journal of the Learning Sciences* 2(3), 277–305.** https://www.tandfonline.com/doi/abs/10.1207/s15327809jls0203_2
Human tutors' support is **more flexible and more subtle** than model-tracing ITS. The characteristic human policy is to let students **do most of the work of error recovery while limiting the space in which they flounder** — tutors intervene to keep the student on a *productive* path rather than to prevent errors. They do not correct at the first deviation; they correct when the error would lead to unrecoverable confusion or wasted effort. Errors are treated as opportunities to elicit reasoning, not as things to be suppressed.

**Kapur, M. (2008, 2016). "Productive Failure"; Kapur & Bielaczyc; Loibl, Roll & Rummel (2017).**
Generation/invention phase *before* instruction, followed by strong consolidation, outperforms instruction-first on **conceptual understanding and transfer (d ≈ 0.36)** without hurting procedural knowledge. The consolidation phase is non-negotiable — productive failure ≠ discovery learning. https://static1.squarespace.com/static/5c5310c785ede1e27998bbb0/t/6033ebab5190b8101bcae768/1614015403798/Learning+from+Productive+Failure.pdf

**Implications:**
- **Do not explain to a student who is not at an impasse.** The single most common LLM tutor failure. Before explaining, verify the student has actually tried and hit a wall; otherwise the explanation is inert.
- **Error handling policy:** let an error run when (a) it is recoverable, (b) its consequence will be visible to the student soon, and (c) the student can plausibly detect it. Interrupt immediately when the error is a *misread of the problem statement*, a *sign/units/setup error that will silently propagate*, or when the student is about to spend a lot of effort down a path with no diagnostic payoff.
- **Generation before telling**: pose the problem before delivering the method; then consolidate explicitly ("here's the canonical solution, here's how it relates to what you tried").

---

## 7. Does Socratic tutoring actually work?

The honest answer: **there's less evidence for it than its reputation implies, and clear boundary conditions against it.**

- Graesser, Person & Magliano (1995): the Socratic method was **absent** in naturalistic tutoring — yet naturalistic tutoring still gets d ≈ 0.79. So Socratic questioning is not the mechanism behind tutoring's effect.
- **Kirschner, P. A., Sweller, J., & Clark, R. E. (2006). "Why Minimal Guidance During Instruction Does Not Work." *Educational Psychologist* 41(2), 75–86.** https://www.sfu.ca/~jcnesbit/EDUC220/ThinkPaper/KirschnerSweller2006.pdf Minimal-guidance approaches fail for learners without adequate prior knowledge: absent domain schemas in long-term memory, open questioning imposes heavy working-memory load on search rather than on schema construction. The expertise-reversal effect: guidance helps novices and hurts experts; open inquiry does the reverse.
- Chi et al. (2001) shows prompting-only works — but note it worked with students who had already *read the text*. The prompts operated on existing material.
- VanLehn et al. (2007): dialogue only beat reading when content exceeded the learner's preparation — and even there the students had baseline physics exposure.

**Synthesis:** Socratic questioning is a *retrieval and integration* tool, not an *acquisition* tool. It works when the student has the raw material in memory and needs to assemble, connect, or repair it. It fails when the student lacks the schema — then it degenerates into guessing, which costs working memory, produces frustration, and teaches nothing. Lepper's expert tutors were "Socratic" in a much weaker sense than Plato's: piquing curiosity and asking leading questions inside a heavily scaffolded environment, not withholding all content.

**Implication:** gate Socratic mode on prior knowledge. If the student cannot produce a relevant fact or definition on request, **stop questioning and teach** — give the definition, the worked example, the vocabulary — then resume questioning. Two consecutive non-answers is a schema-absence signal, not a motivation problem.

---

## 8. Expert vs. novice tutors

**Lu, X., Di Eugenio, B., Kershaw, T. C., Ohlsson, S., & Corrigan-Halpern, A. (2007). "Expert vs. Non-expert Tutoring: Dialogue Moves, Interaction Patterns and Multi-Utterance Turns." (CICLing / Springer LNCS)** https://nlp-lab.red.uic.edu/wp-content/uploads/sites/314/2018/06/Expert-vs.-Non-expert-Tutoring.pdf
Three tutors (expert 1:1 tutor, experienced lecturer, novice), letter-pattern extrapolation domain, 11 students per group + no-tutoring control. **Only the expert tutor significantly beat both other tutors and the control** on post-test.

Move distribution (% of tutor moves; Novice / Lecturer / Expert):

| Move | Novice | Lecturer | Expert |
|---|---|---|---|
| Declarative instructing (facts about the problem) | **22.6** | 6.2 | **4.0** |
| Procedural instructing (how to go about it) | 0.6 | 4.4 | **17.2** |
| Demonstrating | 6.3 | 0.0 | 11.1 |
| Specific prompting | 17.6 | **27.7** | 13.9 |
| Summarizing | 6.9 | 16.7 | 16.6 |
| Answering student questions | 10.1 | 5.4 | **1.4** |
| Support (encouragement) | 0.6 | 0.6 | **5.4** |
| Evaluating | 16.4 | 12.9 | 7.8 |

Findings that cut against the standard story:
- The expert did **less** specific prompting than the lecturer, and his students explained **less** — contradicting a naive "prompt more, talk less" rule. What he did instead was *vary* his strategies, and lead with **procedural** rather than **declarative** instruction.
- Expert turns were **significantly longer** (multi-utterance turns up to 22 utterances; lecturer max 9, novice rarely >7); **35.6%** of his specific prompts were *not* immediately followed by a student move — he chained moves within a turn.
- The expert **never answered a student question directly or immediately** (Answering = 1.4% of moves); non-experts did.
- Students with the expert had **no questions after his general prompting** — his prompts were clear enough not to need repair. Novice-tutor answering was routinely followed by student questioning (i.e. his answers created confusion).
- The expert did declarative instructing **almost exclusively after a student "reflecting" move** — i.e. only after the student explicitly expressed lack of understanding of a concept. That is a precise gate on when to just tell them.
- Expert follow-ups: after his own *support* move, almost any move type could follow — he encouraged, then pushed forward. After *diagnosing*, he did procedural instructing and support far more than non-experts.

**Implications:**
- **Prefer procedural over declarative instruction.** "Start by counting the letters in each period" beats "notice that the two Cs separate the parts." Teach the move, not the fact.
- **Gate declarative telling on an explicit student statement of not-understanding.** ("I don't really get the C thing" → now give the fact.)
- **Don't answer questions directly.** Answer with a prompt or a procedural cue; when you must answer, follow the answer immediately with a specific prompt (the expert's signature pattern: Answering → Specific Prompting).
- **Longer, structured tutor turns are not a violation of "say less."** The expert talked more per turn but told less content — he chained diagnose → procedural cue → support. "Say less" means less *declarative content*, not fewer words.
- Encouragement is a real move with real frequency (5.4% vs 0.6%), and it functions as a transition into further work.

---

## 9. Motivation and affect

**Lepper, M. R., Woolverton, M., Mumme, D. L., & Gurtner, J.-L. (1993). "Motivational techniques of expert human tutors: Lessons for the design of computer-based tutors."** In Lajoie & Derry (Eds.), *Computers as Cognitive Tools*. Also Lepper & Woolverton (2002), "The wisdom of practice." Guidelines summary: https://www.eoas.ubc.ca/research/cwsei/resources/INSPIRE-Guidelines.pdf

**INSPIRE** — traits of expert tutors:
- **I**ntelligent (deep domain knowledge)
- **N**urturant (build rapport, care about the student's state)
- **S**ocratic (elicit rather than tell; pique curiosity so students want the answer)
- **P**rogressive (sequence problems so difficulty rises with competence; challenging but not impossible)
- **I**ndirect (feedback is oblique; errors are attributed to the problem's difficulty or ambiguity, not the student's ability — "that's a tricky one, a lot of people put the sign there")
- **R**eflective (make the student articulate what they did and why, and generalize it)
- **E**ncouraging (support agency and effort attribution)

Lepper's expert tutors almost never said "wrong." They diagnosed silently, then engineered the next problem so the misconception surfaced. They also **deliberately assigned occasional problems slightly beyond the student's reach** so that struggle was normalized and success felt earned.

**D'Mello, S., & Graesser, A. C. (2012). "Dynamics of affective states during complex learning." *Learning and Instruction* 22(2), 145–157.** https://www.sciencedirect.com/science/article/abs/pii/S0959475211000806
**D'Mello, S., Lehman, B., Pekrun, R., & Graesser, A. (2014). "Confusion can be beneficial for learning." *Learning and Instruction* 29, 153–170.** https://www.sciencedirect.com/science/article/abs/pii/S0959475212000357

- The affect model: engagement/flow → (contradiction, anomaly, impasse) → **confusion** → *if resolved*, back to flow; *if unresolved*, **frustration** → *if persistent*, **boredom** and disengagement. Time-series analyses confirm confusion↔flow, confusion↔frustration, and boredom↔frustration oscillations.
- Confusion **experimentally induced** (via contradictory information from animated agents) **improved learning** — but only for learners who resolved it. This is the **zone of optimal confusion**: a minimum of constructive confusion and a maximum beyond which it becomes adverse.
- Individual differences matter (Lehman et al. 2013): confusion induction benefits learners with adequate prior knowledge and does not benefit those without.

**Implications:**
- **Confusion is a target state, not a failure state** — but only paired with a guaranteed resolution path. Never induce confusion you don't have a plan to resolve within a few turns.
- **Distinguish confusion from frustration in the transcript and respond differently.** Confusion markers: questions, hedged reasoning, "wait…", partial answers, re-reading. Frustration markers: terseness, "I don't know" repeated, self-deprecation, "just tell me," meta-complaints about the session. Confusion → hold the line, prompt. Frustration → drop a hint level immediately, or give the answer and rebuild.
- **Indirect attribution of error** is a cheap and evidence-backed move: attribute to the problem, not the person. This is *not* the same as vague hedging (Person et al. 1995) — the correction must still be unambiguous; only the blame is redirected.
- **Wait time** (Rowe, M. B., 1974, 1986, "Wait-Time: Slowing Down May Be A Way of Speeding Up," *J. Teacher Education* 37(1)): teachers wait 0.7–1.5 s; extending to **3–5 s** produces longer student responses, more student-initiated reasoning, more confidence, and more diverse teacher questions. The text analogue is *turn discipline*: do not fill the silence, do not answer your own question in the same message, do not stack a hint onto the question you just asked.

---

## 10. Concrete behavioral rules for a text-based LLM tutor

Ordered roughly by expected effect size.

1. **Never evaluate only a final answer.** Decompose every problem into steps and require the student to produce and defend each one. Answer-granularity d ≈ 0.31; step-granularity d ≈ 0.76 (VanLehn 2011). This is the highest-value rule on the list.
2. **Enforce a mastery criterion before advancing.** Define, per skill, what counts as mastered (e.g. two consecutive correct applications, one of them in a novel context). Do not move on because the conversation feels finished. Most of Bloom's 2σ was the criterion, not the dialogue.
3. **Do not explain to a student who is not at an impasse.** Before any explanation, verify the student has attempted and hit a wall. Explanations delivered pre-impasse are not associated with learning (VanLehn et al. 2003). If they haven't tried, the correct move is "what would you try first?"
4. **Run a 5-level hint ladder with per-skill state.** L1 general prompt to act → L2 name the relevant feature → L3 narrow the space / point at the operative constraint → L4 set up the step → L5 demonstrate. Track a current level per skill.
5. **Apply the contingency rule literally.** On success, next intervention is one level *lower*. On failure or a help request, one level *higher*. Carry the level across problems: if the last problem needed L4, open the next unsolicited at L2.
6. **Cap escalation at three.** After ~three increasingly explicit cues without success, give the answer and the worked reasoning, then re-pose an isomorphic problem. Floundering beyond this is frustration, not productive struggle (Wood & Wood 1999).
7. **Offer help proactively; never rely on the student asking.** Low-prior-knowledge learners are least likely to ask and most likely to need it (Nelson-Le Gall; Wood & Wood 1999). Trigger unsolicited help on: a stall, a repeated error class, a non-answer, or an "I don't know."
8. **Make negative feedback unambiguous.** State plainly that the answer is wrong and name what is wrong, before anything else. No praise sandwich, no "great thinking, though…". Politeness that obscures the error is a documented failure mode (Person et al. 1995) and is the LLM's default failure mode.
9. **Attribute the error to the problem, not the student.** "That step trips a lot of people up — the sign flips when you factor out the negative" (Lepper INSPIRE, *Indirect*). Unambiguous correction, redirected blame. These are compatible; do both.
10. **Prefer procedural instruction over declarative instruction.** Teach the *move* ("start by writing what you know in symbols") not the *fact* ("the discriminant is b²−4ac"). Expert tutors: 17.2% procedural / 4.0% declarative; novices: 0.6% / 22.6% (Lu et al. 2007).
11. **Gate declarative telling on an explicit statement of not-understanding.** Only hand over a definition or fact after the student has said, in some form, "I don't know what X is." The expert tutor did declarative instruction almost exclusively after student reflecting moves.
12. **Don't answer direct questions directly.** Convert to a prompt or a procedural cue. When you must answer (student is blocked on a fact), pair the answer immediately with a specific prompt that returns the work to them — the expert pattern Answering→Specific Prompting.
13. **One question per turn, then stop.** Do not ask a question and answer it in the same message. Do not stack a question plus a hint plus an explanation. This is the text analogue of 3–5 s wait time (Rowe 1986); the LLM's tendency to pre-empt is the direct violation.
14. **Ask deep, high-specification questions.** Deep = why / how / what-if / what-would-break / how-does-this-differ. High-specification = enough referential content that the student knows exactly what's being asked. "What happens to the variance if you double every observation?" not "What do you notice?"
15. **Never close a step with "does that make sense?"** Step 5 of the Graesser frame must be a real probe: restate in your own words, apply to a modified case, predict what changes if a premise flips. Treat any bare "yes" as unverified.
16. **Assume your student model is wrong and test it out loud.** "I think you're applying the chain rule where the product rule is needed — is that what you did?" Human tutors are poor diagnosticians (Chi, Siler & Jeong 2004); explicit hypothesis-testing beats silent inference.
17. **Apply the ICAP test to every planned turn.** Will this turn cause the student to *generate* something not already given? If no, rewrite or delete it. Aim for student generative output to dominate the transcript by volume.
18. **Escalate to dialogue only when material exceeds the student's preparation.** If the content matches their level, exposition + step-level practice is as effective and cheaper (VanLehn et al. 2007). Use dialogue where the student is genuinely over their head.
19. **Gate Socratic mode on prior knowledge; two consecutive non-answers means stop asking and teach.** Absent schemas, questioning imposes search load rather than building knowledge (Kirschner, Sweller & Clark 2006). Give vocabulary, definition, and one worked example, then resume questioning.
20. **Generation before telling, with mandatory consolidation.** Pose the problem before delivering the method; after the attempt, explicitly present the canonical solution and connect it to what the student tried. Productive failure without consolidation is just failure (Kapur 2016).
21. **Error interruption policy.** Let it run when the error is recoverable, its consequence will be visible soon, and the student could plausibly catch it. Interrupt immediately when: the student has misread the problem, the error is a silent setup/sign/units error that will propagate invisibly, or a long stretch of work with no diagnostic value lies ahead (Merrill et al. 1992).
22. **Induce confusion deliberately — but only with a resolution path.** Counterexamples, contradictions, and "why doesn't this work?" cases are legitimate and effective (D'Mello et al. 2014). Never leave one unresolved at the end of a segment.
23. **Detect and treat frustration separately from confusion.** Confusion (questions, hedging, "wait…", partial reasoning) → hold, prompt. Frustration ("just tell me," repeated "I don't know," self-deprecation, terseness) → drop a hint level or resolve outright, then rebuild with an easier win. Unresolved frustration decays to boredom and disengagement (D'Mello & Graesser 2012).
24. **Sequence progressively.** Each problem should be challenging but reachable given demonstrated competence; occasionally include one slightly beyond reach and frame the struggle as expected (Lepper INSPIRE, *Progressive*).
25. **Use encouragement as a structural move, not decoration.** Expert tutors spent 5.4% of moves on content-free support, and used it as a transition into more work — not as a substitute for feedback.
26. **Cultivate student question-asking.** Student question *quality*, not frequency, tracks achievement (Graesser & Person 1994). Periodically hand the move back: "what's the question you should be asking about this result?" Then critique the question.
27. **Longer tutor turns are fine if they're low in declarative content.** The expert chained diagnose → procedural cue → support inside a single turn. "Say less" means tell them less, not type less.
28. **Test transfer, not session recall.** Assess on problems structurally similar but surface-different from what was taught. Mastery effects that appear on experimenter-made tests largely vanish on standardized ones (Kulik et al. 1990) — the same trap applies to a session's own review questions.
29. **Track and log which step failed, not just that the problem failed.** Step-level diagnosis is what makes step-based tutoring work; without persistent per-skill state, the contingency rules in #4–7 are unimplementable.
30. **Budget the session against the interaction plateau.** Once the tutor is at step granularity with clear feedback and a contingent hint ladder, additional conversational elaboration returns nothing measurable. Spend the remaining effort on more problems, better sequencing, and spaced review instead of richer dialogue.

---

## Appendix: AutoTutor and EMT dialogue

**Graesser, A. C. et al., AutoTutor (1999–present).** Reviews: Nye, Graesser & Hu (2014), "AutoTutor and Family: A Review of 17 Years of Natural Language Tutoring," *IJAIED* 24(4), 427–469 (https://link.springer.com/article/10.1007/s40593-014-0029-5); Graesser et al., "Conversations with AutoTutor Help Students Learn," *IJAIED* (https://files.eric.ed.gov/fulltext/ED586836.pdf).

**Expectation & Misconception-Tailored (EMT) dialogue** — the mechanism AutoTutor extracted from human tutoring and the most directly portable design for an LLM tutor:

1. For each challenging question, pre-specify a list of **expectations** (the sentence-like ideas a complete answer must contain) and a list of **misconceptions** (specific wrong ideas known to be common).
2. As the student answers across turns, semantically match their contributions against both lists.
3. Give **short feedback** on the match.
4. Drive coverage of the remaining expectations with a **pump → hint → prompt → assertion** cycle:
   - **Pump**: "What else?" / "Tell me more." — content-free, maximal student generation.
   - **Hint**: point at the missing idea without naming it.
   - **Prompt**: a leading question engineered so the student must supply a *specific word or phrase*.
   - **Assertion**: state the expectation yourself. Last resort.
5. Correct any matched misconception directly.
6. **Summarize** the full answer at the end.

Note the escalation is exactly Wood's contingency ladder in dialogue form, and the terminal assertion is Wood's "demonstrate."

**Implication for an LLM tutor:** this is the concrete session data structure. Before a topic, generate (a) the expectation list and (b) the misconception list. Then the whole dialogue policy reduces to: track which expectations are covered, escalate pump→hint→prompt→assert on uncovered ones, fire a direct correction on any misconception match, summarize at close. It makes "did the student understand?" a checklist rather than a vibe — which is exactly what Chi, Siler & Jeong (2004) says humans get wrong.

---

## Key sources

- VanLehn (2011): https://www.tandfonline.com/doi/abs/10.1080/00461520.2011.611369
- Graesser & Person (1994), full text: https://gwern.net/doc/psychology/spaced-repetition/1994-graesser.pdf
- Graesser, Person & Magliano (1995): https://onlinelibrary.wiley.com/doi/abs/10.1002/acp.2350090604
- Chi et al. (2001): https://onlinelibrary.wiley.com/doi/10.1207/s15516709cog2504_1
- Chi, Siler & Jeong (2004): https://www.tandfonline.com/doi/abs/10.1207/s1532690xci2203_4
- VanLehn et al. (2003): https://www.tandfonline.com/doi/abs/10.1207/S1532690XCI2103_01
- VanLehn et al. (2007): https://onlinelibrary.wiley.com/doi/abs/10.1080/03640210709336984
- Merrill, Reiser, Ranney & Trafton (1992): https://www.tandfonline.com/doi/abs/10.1207/s15327809jls0203_2
- Wood & Wood (1999), full text: https://www.tlu.ee/~kpata/haridustehnoloogiaTLU/tutoring.pdf
- Wood, Wood & Middleton (1978): https://journals.sagepub.com/doi/10.1177/016502547800100203
- Lu, Di Eugenio, Kershaw, Ohlsson & Corrigan-Halpern (2007), full text: https://nlp-lab.red.uic.edu/wp-content/uploads/sites/314/2018/06/Expert-vs.-Non-expert-Tutoring.pdf
- Kirschner, Sweller & Clark (2006), full text: https://www.sfu.ca/~jcnesbit/EDUC220/ThinkPaper/KirschnerSweller2006.pdf
- D'Mello, Lehman, Pekrun & Graesser (2014): https://www.sciencedirect.com/science/article/abs/pii/S0959475212000357
- D'Mello & Graesser (2012): https://www.sciencedirect.com/science/article/abs/pii/S0959475211000806
- Nickow, Oreopoulos & Quan (2020): https://www.nber.org/system/files/working_papers/w27476/w27476.pdf
- Nye, Graesser & Hu (2014), AutoTutor review: https://link.springer.com/article/10.1007/s40593-014-0029-5
- Graesser et al., Conversations with AutoTutor: https://files.eric.ed.gov/fulltext/ED586836.pdf
- Lepper & Woolverton, INSPIRE guidelines: https://www.eoas.ubc.ca/research/cwsei/resources/INSPIRE-Guidelines.pdf
- Nintil, systematic review of Bloom's 2σ: https://nintil.com/bloom-sigma/
- Kapur, "Learning from Productive Failure": https://static1.squarespace.com/static/5c5310c785ede1e27998bbb0/t/6033ebab5190b8101bcae768/1614015403798/Learning+from+Productive+Failure.pdf

---

## Caveats on the evidence base

- Full text of VanLehn (2011) and Chi et al. (2001) was not directly accessible; their effect sizes and the suppressed-explanation result come from secondary summaries and abstracts. The substep d ≈ 0.40 figure in particular should be verified against the original table before being quoted.
- Lu et al. (2007) is a single expert tutor, N=11 per group, in an artificial letter-pattern domain. Its move percentages indicate mechanism, not established norms.
- Most of this literature predates LLMs and concerns spoken or typed human tutoring in math/physics. The granularity and contingency findings should transfer; the affect-detection findings relied on facial/postural sensors that a text tutor does not have.
