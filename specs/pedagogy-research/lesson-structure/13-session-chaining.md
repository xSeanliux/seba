# Session Chaining: the architecture above the lesson, below the syllabus

Scope: how a run of sessions becomes a course. Prerequisite DAGs, FSRS internals, turn-level moves and learner-modelling formalisms are treated as settled elsewhere.

**Sourcing note.** This session's web-search budget was exhausted before this round began. Findings below come from direct fetches of primary sources (Rosenshine's full AFT text, Rasch & Born, Duolingo's engineering blog), OpenAlex/Crossref metadata-and-abstract retrieval used as a search substitute, and Wikipedia for locating classic experiments. Where a number is stated from domain knowledge and could not be re-verified against the source text in this session, it is tagged **[unverified-here]**. Treat those as "check before quoting", not as fabrications — they are all well-known published figures, but I did not read them today.

---

## 1. Cumulative review and the shape of a course

### Rosenshine's principles 1 and 10 — read from the source

Barak Rosenshine, "Principles of Instruction: Research-Based Strategies That All Teachers Should Know," *American Educator* 36(1), Spring 2012, pp. 12–19, 39. https://www.aft.org/sites/default/files/Rosenshine.pdf (full text fetched and read for this report).

**Principle 1 — daily review.** Rosenshine's exact framing: "Begin a lesson with a short review of previous learning: Daily review can strengthen previous learning and can lead to fluent recall."

What it consisted of, per his text:

> "The most effective teachers in the studies of classroom instruction understood the importance of practice, and they began their lessons with a five- to eight-minute review of previously covered material. Some teachers reviewed vocabulary, formulae, events, or previously learned concepts. These teachers provided additional practice on facts and skills that were needed for recall to become automatic."

And an explicit checklist:

> - Correct homework.
> - Review the concepts and skills that were practiced as part of the homework.
> - Ask students about points where they had difficulties or made errors.
> - Review material where errors were made.
> - Review material that needs overlearning (i.e., newly acquired skills should be practiced well beyond the point of initial mastery, leading to automaticity).

**What it bought.** The cited experiment is the Missouri Mathematics Effectiveness Project (Good & Grouws, *Journal of Educational Psychology* 71(3), 1979, 355–362, https://doi.org/10.1037/0022-0663.71.3.355): "Teachers in the experiment were taught to spend eight minutes on review... As a result, students in these classrooms had higher achievement scores than did students in other classrooms." Rosenshine gives no effect size. This is a *bundled* treatment — daily review was one component of a multi-component training package — so the review-specific effect is not isolable from that study.

Rosenshine's stated mechanism is working-memory economy, and it is the strongest argument for an opening review move in a tutor: "It is important for a teacher to help students recall the concepts and vocabulary that will be relevant for the day's lesson because our working memory is very limited. If we do not review previous learning, then we will have to make a special effort to recall old material while learning new material, and this makes it difficult for us to learn the new material."

**Principle 10 — weekly and monthly review.** "Students need to be involved in extensive practice in order to develop well-connected and automatic knowledge."

The concrete schedule Rosenshine describes:

> "Many successful programs, especially in the elementary grades, provided for extensive review. One way of achieving this goal is to review the previous week's work every Monday and the previous month's work every fourth Monday. Some effective teachers also gave tests after their reviews."

And the one comparative claim with a direction attached:

> "Research has found that even at the secondary level, classes that had weekly quizzes scored better on final exams than did classes with only one or two quizzes during the term."

Source given: Kulik & Kulik, "College Teaching," in Peterson & Walberg (eds.), *Research on Teaching* (McCutchan, 1979). No effect size in Rosenshine's text.

**Implication for Seba.** Rosenshine's weekly/monthly cadence is a crude, hand-rolled spacing schedule invented before FSRS existed. Seba's FSRS layer already dominates it *for item-level recall*. What FSRS does **not** cover, and what principle 10 is actually reaching for, is the second half of his rationale: "Review also helps students develop their new knowledge into patterns... The more one rehearses and reviews information, the stronger the interconnections between the materials become." That is **structural** review — reviewing the *relationships* between concepts — and it is not a card. This is the single clearest gap the principle identifies for a system that already has good card scheduling.

Also worth lifting directly: the **80% success rate** target (principle 7). Rosenshine reports that in the classroom studies, the most successful fourth-grade math teachers ran an 82% correct rate during guided practice versus 73% for the least successful, and "the optimal success rate for fostering student achievement appears to be about 80 percent." That is a *course-level* calibration target for a tutor that controls difficulty across sessions, not just within one.

### Cumulative vs unit-terminal assessment

The direct experimental literature on cumulative-vs-terminal exams is thin and mostly quasi-experimental. The stronger and more directly transferable evidence is **successive relearning**, which is cumulative assessment operationalized.

- **Janes, Dunlosky, Rawson & Jasnow (2021), "The benefits of successive relearning on multiple learning outcomes," *Journal of Educational Psychology*, https://doi.org/10.1037/edu0000693.** Abstract, fetched: successive relearning = "repeated retrieval practice of the same information (with feedback) over multiple, spaced sessions." In an intro psych class, students did three practice sessions per week's lecture, each separated by two days, sustained over 10 weeks; within-subject alternation between relearn and restudy, **with exposure duration controlled** (a real methodological improvement over earlier work). "Recall of course material at the end of the semester was better for relearning compared to restudying." Secondary outcomes are the interesting part for a voluntary learner: "improved metacognition, increased self-reported sense of mastery, increased attentional control, and **reduced anxiety**," and "students found successive relearning to be enjoyable and valuable."
- **Higham, Zengel, Bartlett & Hadwin (2022), "Enhancing learning and retention through the distribution of practice repetitions across multiple sessions," *Memory & Cognition* 50, https://doi.org/10.3758/s13421-022-01361-8.** Same family; distributing repetitions across sessions beats concentrating them.
- **Rawson & Dunlosky's** relearning-to-criterion work is the origin: relearning to a criterion of 3 correct recalls per session across 3–4 spaced sessions produces retention on the order of months from a few minutes of total investment. **[unverified-here]**
- Rosenshine's own gloss on the tension is honest and worth keeping: "Teachers face a difficult problem when they need to cover a lot of material and don't feel they have the time for sufficient review. But the research states (and we all know from personal experience) that material that is not adequately practiced and reviewed is easily forgotten."

**Implication.** Seba's FSRS layer *is* successive relearning for atomic items. The evidence says the sense-of-mastery and anxiety-reduction benefits ride along with it, and those are retention-of-the-learner benefits, not just retention-of-the-material benefits. Making the relearning *visible* to the learner ("you have now recalled this correctly on four separate occasions across five weeks") converts a scheduling mechanism into a self-efficacy signal. Cheap.

### How mastery-based courses structure revisiting — and a caution

Mastery learning's effect sizes are genuinely contested, and the contest is instructive.

- **Kulik, Kulik & Bangert-Drowns (1990), "Effectiveness of Mastery Learning Programs: A Meta-Analysis," *Review of Educational Research* 60(2), https://doi.org/10.3102/00346543060002265** — reports substantial positive effects (commonly quoted around 0.5 SD). **[unverified-here]**
- **Slavin (1990), "Mastery Learning Re-Reconsidered," *Review of Educational Research* 60(2), 300–302, https://doi.org/10.3102/00346543060002300** (abstract fetched). Slavin's best-evidence synthesis found "in studies of at least 4 weeks' duration, mastery learning had essentially no effect on standardized achievement measures and a small effect on experimenter-made measures, which, I argued, were often biased in favor of the mastery learning treatment." Critically, he notes agreement on the key point: "Kulik et al. (1990) **agree** with what was to me the key finding of my review, that the effects of mastery learning on standardized measures are effectively zero," and that the headline Kulik numbers "are heavily influenced by" experimenter-made tests.

**Implication.** Do not sell mastery gating as a large-effect intervention. The honest reading is that mastery structures reliably improve performance on *the thing you are testing on* and do not reliably transfer to independent measures. For Seba this argues for mastery gating as an **instructional-sequencing hygiene** measure (don't teach C before B is solid — which the prerequisite DAG already handles) rather than as a motivational or achievement lever in its own right.

---

## 2. Session frequency and duration, total time held constant

This is the cleanest, oldest, and most decision-relevant evidence in the whole brief.

### The canonical total-time-constant experiment

**Baddeley & Longman (1978), "The influence of length and frequency of training session on the rate of learning to type," *Ergonomics* 21(8), 627–635, https://doi.org/10.1080/00140137808931764.** British postal workers learning a keyboard, four schedules crossing session length (1h vs 2h) with sessions per day (1 vs 2): **1×1h, 2×1h, 1×2h, 2×2h per day**, total hours equated at 60. The 1h-once-daily group learned fastest per hour of training and retained best at follow-up; the 2h-twice-daily group was worst per hour invested. The gap widened at delayed retention tests (retests at 1 and 9 months). **[unverified-here for the exact schedule grid; the direction and the total-time-constant design are confirmed via the distributed-practice literature fetched this session.]**

The wrinkle that matters enormously for a voluntary adult learner: **the group with the most efficient schedule was the least satisfied with it.** The massed groups preferred their schedule because it finished the course in fewer calendar days. Efficiency per hour and subjective preference pointed in opposite directions. This is the session-level instance of the desirable-difficulties problem, and it directly predicts that Seba's optimal cadence will feel slower to the learner than a suboptimal one.

### Retention across very long horizons

**Bahrick, Bahrick, Bahrick & Bahrick (1993), "Maintenance of foreign language vocabulary and the spacing effect," *Psychological Science* 4(5), 316–321, https://doi.org/10.1111/j.1467-9280.1993.tb00571.x.** Nine years, 50 relearning sessions of English–foreign-language vocabulary, spacing manipulated at 14/28/56 days. Fetched summary: "both the number of relearning sessions and the number of days in between each session have a major impact on retention," with recall "highest for the 56-day interval," and the headline efficiency result — **"13 sessions spaced 56 days apart yielded comparable retention to 26 sessions with a 14-day interval."** Half the sessions, equal retention, purely by widening the gap.

**Implication.** At the item level Seba already exploits this via FSRS. At the *session* level, the analogous claim is that session count can be traded against session gap without loss — which is the escape hatch when a learner's life gets busy. A tutor that quietly widens intervals and reduces frequency during a busy stretch, rather than nagging for the original cadence, has literature behind it.

### Second-language-specific evidence — weaker and more equivocal than folklore suggests

- **Kasprowicz, Marsden & Sephton (2019), "Investigating Distribution of Practice Effects for the Learning of Foreign Language Verb Morphology in the Young Learner Classroom," *Modern Language Journal* 103(3), https://doi.org/10.1111/modl.12586** (abstract fetched). Direct 7-day vs 3.5-day spacing comparison for French verb inflection with L1-English children. Result: **"minimal differences between longer (7-day) versus shorter (3.5-day) spacing... at either posttest or delayed posttest," with "minimal group-level gains and substantial within-group variation."** The authors note the field's evidence is "conflicting" — "some studies reveal advantages for spacing of 7 days or more, but others for shorter spacing."
- **Nakata & Elgort / Serrano & Muñoz** and the broader L2 distribution-of-practice literature reach similar conclusions: spacing helps, but the *optimal* L2 classroom gap is not established and interacts with the type of knowledge. **[unverified-here]**
- **Suzuki & DeKeyser** on the interaction between spacing and skill type (declarative vs proceduralized L2 knowledge) is the most relevant refinement: procedural/automatization gains favour shorter gaps and higher frequency; declarative knowledge favours longer gaps. **[unverified-here]**
- **Elgort, Beliaeva & Boers (2020), "Effects of spacing on contextual vocabulary learning," *Second Language Research* 36(4), https://doi.org/10.1177/0267658320927764** (abstract fetched). Spaced beat massed on meaning-recall and meaning–form matching posttests, but **semantic priming was equivalent** across massed and spaced. Their conclusion: "the spacing effect holds in contextual word learning for the development of **explicit** vocabulary knowledge, but massing appears to be as effective as spacing for the acquisition of **tacit** semantic knowledge."

**The honest synthesis for Seba's two subjects.** Probability theory is declarative/schematic — spacing helps, longer gaps are fine, session count can be traded for gap width. Italian is *split*: the explicit vocabulary/grammar layer behaves like probability (space it, FSRS it), but the fluency/automatization layer behaves differently and appears to benefit from **higher frequency and shorter gaps** even at the cost of session length. There is no evidence-backed single optimal cadence covering both.

**A defensible default rather than a derived optimum:** for a voluntary adult learner, sessions of **~25–45 minutes**, **3–4 per week for Italian** and **2–3 per week for probability**, with a strong preference for *never skipping two in a row* over hitting any particular count. The frequency asymmetry is theory-driven (automatization vs schema-building), not directly evidenced; the session-length range is bounded below by "enough time for review + one concept + practice + recap" and above by attention and voluntary-learner tolerance, not by a study.

**Do not** recommend long sessions on the grounds of "getting more done." Baddeley & Longman is the one place where total-time-constant evidence exists and it points the other way, and the learner's own preference will point the wrong way too.

---

## 3. What should carry across a session boundary

### The opening review move

Rosenshine's principle 1 (above) is the operational answer: 5–8 minutes, retrieval-based, covering (a) prerequisite material the day's lesson will consume, and (b) points where errors occurred last time. Note the two are different targets and both are named explicitly in his text — "review the concepts and vocabulary that will be relevant for the day's lesson" is *feedforward*; "ask students about points where they had difficulties or made errors" is *error repair*. A tutor that only does FSRS-due-items does neither reliably: due-ness is a function of the scheduler, not of what today's lesson needs or where last session broke down.

**This is the single highest-leverage structural finding in the brief for Seba.** The opening block should be a union of three sets, not one:
1. FSRS-due items (already implemented).
2. Prerequisite concepts for today's target concept, regardless of due status — retrieved, not just mentioned.
3. Last session's error sites, regardless of due status.

Sets 2 and 3 are computable from state Seba already has (concept graph edges; per-concept notes) and require no new storage.

### Advance organizers and bridging

**Ausubel (1960), "The use of advance organizers in the learning and retention of meaningful verbal material," *Journal of Educational Psychology* 51(5), 267–272, https://doi.org/10.1037/h0046669.** The original: a short abstract passage presented *before* the material, pitched at a higher level of generality, whose function is to provide "ideational scaffolding" — anchoring ideas in existing cognitive structure for the new material to subsume into.

**Luiten, Ames & Ackerson (1980), "A Meta-Analysis of the Effects of Advance Organizers on Learning and Retention," *American Educational Research Journal* 17(2), 211–218, https://doi.org/10.3102/00028312017002211.** 135 studies; mean effect on learning **~0.21 SD**, with a somewhat larger effect on delayed retention than immediate learning. **[unverified-here]** This is a *small* effect and it should be reported as small.

A more recent critical read — **Sáez & Chacón (2023), "Ausubel's meaningful learning re-visited," *Current Psychology*, https://doi.org/10.1007/s12144-023-04440-4** (abstract fetched) — argues the construct needs updating in light of memory dynamism and non-representational memory, and that "effective questioning to ascertain previous knowledge necessitates in-depth Socratic dialogue" rather than a static organizer passage. That is a notable point for a *conversational* tutor: Seba can do the interactive version of an advance organizer, which a textbook cannot, and the interactive version is what the critique says is actually needed.

A directly negative data point worth recording so as not to oversell: **Chen, Chen & Xiao (2007)**-type web-course studies find "no statistically significant AO effect" between concept-map organizers, text-outline organizers, and no organizer, with the benefit "positive but inconclusive" (abstract fetched via OpenAlex, https://doi.org/ n/a).

**Implication.** An explicit "here's where we are and how today connects to last time" opener is *cheap* and has a small-but-real evidence base (~0.2 SD), plus a mechanism argument (working memory, per Rosenshine) that is stronger than the effect size. It is not a big lever. Do it because it costs one paragraph of the briefing prose, not because it will transform outcomes.

### Should a session begin by explicitly connecting to the previous one?

Yes, but the evidence supports a *specific* form. Generic "last time we covered X" is a summary, not an organizer and not retrieval. The evidence-backed forms are:
- **Retrieval** of last session's content ("before I say anything — what stuck from Tuesday?"). Test-enhanced learning generalizes to classrooms: **McDaniel, Anderson, Derbish & Morrisette (2007), "Testing the testing effect in the classroom," *European Journal of Cognitive Psychology*, and Roediger & Karpicke's classroom-generalization work, https://doi.org/10.3758/bf03194052** (Butler & Roediger 2007, "Generalizing test-enhanced learning from the laboratory to the classroom," *Psychonomic Bulletin & Review* 14, 514–519).
- **Bridging at the level of relationships**, not facts: "last time: independence. Today: conditional probability. The link is that independence is the special case where conditioning changes nothing." This is Ausubel's subsumption plus Rosenshine's "develop new knowledge into patterns."

**Seba-specific.** The `next_session_hint` field is already the right hook and is currently underspecified. It should carry the *bridge*, not the *topic*. "Next: conditional probability" is a topic. "Next: conditional probability — open by asking her to restate the independence definition, then show it's the P(A|B)=P(A) case; she was shaky on why independence isn't the same as disjointness" is a bridge plus an error-repair target plus an opening move.

---

## 4. Unit / module architecture

### 4C/ID and task classes

**van Merriënboer & Kirschner, *Ten Steps to Complex Learning* (Routledge; 3rd ed. 2018)**, and **van Merriënboer, Clark & de Croock (2002), "Blueprints for complex learning: The 4C/ID-model," *Educational Technology Research and Development* 50(2), 39–64, https://doi.org/10.1007/BF02504993.** (4cid.org returned 403; the model is described here from the published literature. **[unverified-here]**)

Four components: **learning tasks** (whole, authentic tasks), **supportive information** (theory/mental models for non-recurrent aspects), **procedural information** (just-in-time how-to for recurrent aspects), and **part-task practice** (drilling routines to automaticity).

The concept that matters for session chaining is the **task class**: a set of learning tasks of *equivalent complexity*, sequenced simple-to-complex across classes. The two rules inside 4C/ID that are directly about multi-session structure:

1. **Within a task class, support fades.** The first task in a class is a worked example / full process worked-out; the last is a conventional task with no support. This is the **completion-problem** sequence. Then the *next* task class begins again with high support at higher complexity — a sawtooth, not a monotone ramp.
2. **Whole tasks throughout.** Every task class presents the whole skill, simplified, rather than a component in isolation. Components are drilled *in addition* (part-task practice), never *instead*.

**Implication for Seba.** This is the strongest available prescription for what a "unit" is: a **task class = a run of sessions at one complexity level, over which scaffolding fades from worked example to independent problem, ending with an unsupported whole task.** It gives a principled answer to "when does a unit end": when the learner can do a whole task of that complexity unsupported. That is a *state* criterion, not a *count* criterion — and Seba, which persists per-concept state, can evaluate it, whereas a fixed-length syllabus cannot.

The sawtooth also predicts something counterintuitive and useful: **at the start of a new unit, deliberately increase support again.** A tutor that has been fading scaffolding for six sessions and then jumps complexity without re-scaffolding will produce a failure that reads (wrongly) as learner regression.

### Elaboration Theory and the epitome

**Reigeluth (1999), "The Elaboration Theory: Guidance for scope and sequence decisions," in *Instructional-Design Theories and Models, Vol. II*, Lawrence Erlbaum**; and Reigeluth & Stein (1983). (Wikipedia article 404'd on both title guesses; described from the published literature. **[unverified-here]**)

The zoom-lens metaphor: start with a wide-angle **epitome** — not a summary or an abstract, but the *simplest complete real version* of the whole task or the whole domain, taught at an application level. Then zoom in on one part, elaborate it, and **zoom back out to the wide-angle view** to re-situate it before zooming in on the next part. Two dedicated devices carry this: **synthesizers** (show relationships among the parts just taught, and between parts and the whole) and **summarizers** (concise review of what was taught, with examples).

The periodic zoom-out is *exactly* the structural review that Rosenshine's principle 10 gestures at and FSRS does not provide. Elaboration Theory's empirical base is weak — it is a design theory with case studies rather than a body of RCTs, and it should be adopted as *structure* rather than cited as *evidence*.

**Implication.** Every N sessions, run a zoom-out: not "review these ten cards" but "here is the map of everything in this unit; explain how these three pieces relate; where does the thing we learned Tuesday sit?" Seba's concept graph *is* an epitome-shaped artifact already sitting in state. Rendering it back to the learner as a synthesis prompt is nearly free.

### Evidence for integrative/synthesis activities

Weaker than one would like. The two supporting lines:
- **Self-explanation and elaborative interrogation** (Dunlosky et al. 2013, "Improving Students' Learning With Effective Learning Techniques," *Psychological Science in the Public Interest* 14(1), https://doi.org/10.1177/1529100612453266) rate as *moderate* utility — better than summarization and rereading, worse than practice testing and distributed practice. Self-explaining how new material relates to known material is the mechanism a synthesis session would exercise. **[unverified-here for the specific utility ratings]**
- **Concept mapping / knowledge integration** effects are small and inconsistent, and the advance-organizer null results above apply.

**Honest position:** synthesis sessions are supported by *design theory* (4C/ID, Elaboration Theory) and by the mechanism (relational encoding, working-memory chunking per Rosenshine's principle 10 rationale) but **not** by a clean meta-analytic effect size. Recommend them, but do not claim an effect size for them.

---

## 5. Narrative and coherence across lessons

The request was to be skeptical here. The skepticism is warranted.

### Project-based learning

- **Chen & Yang (2019), "Revisiting the effects of project-based learning on students' academic achievement: A meta-analysis investigating moderators," *Educational Research Review* 26, 71–81, https://doi.org/10.1016/j.edurev.2018.11.001.** 46 studies, reported medium-to-large effect on achievement, commonly quoted as **g ≈ 0.71**. **[unverified-here — Crossref carries no abstract for this DOI and the full text was not reachable this session.]**
- **Zhang & Ma (2023), "A study of the impact of project-based learning on student learning effects: a meta-analysis," *Frontiers in Psychology* 14, https://doi.org/10.3389/fpsyg.2023.1202728** (abstract fetched). 66 studies, 190 effect values, 20 years. Positive on achievement, affect, and thinking skills. **The moderator analysis is where the skepticism lives:** effects "in Asia, especially in Southeast Asia, were significantly better than those in Western Europe and North America"; larger in "engineering and technology subjects"; "better applied in laboratory classes than in theory classes"; best in small groups of 4–5.

That moderator profile is a warning, not a recommendation. A large region effect in an education meta-analysis is a standard signature of publication bias and of weak-control comparison conditions. The finding that PBL works better in *lab* classes than *theory* classes is directly unfavourable to probability theory. And the group-size finding (4–5 people) does not transfer to 1:1 at all — much of PBL's measured benefit is plausibly collaborative.

- **Dochy, Segers, Van den Bossche & Gijbels (2003), "Effects of problem-based learning: a meta-analysis," *Learning and Instruction* 13(5), 533–568, https://doi.org/10.1016/S0959-4752(02)00025-7.** The classic split result: PBL shows a **positive** effect on *skills/application* and a **negative or null** effect on *knowledge acquisition*, with the knowledge decrement attenuating or reversing at longer retention intervals. **[unverified-here for the exact d values; the qualitative split is the well-replicated part.]**
- **Zhang, Loyens et al. (2024), "The Effects of Problem-Based, Project-Based, and Case-Based Learning on Students' Motivation: a Meta-Analysis," *Educational Psychology Review* 36, https://doi.org/10.1007/s10648-024-09864-3** (abstract fetched). 132 reports, 139 subsamples. Overall **d = 0.498** on motivation, "small to moderate, heterogeneous." Crucially: "effect sizes were larger when problem-driven learning was applied in a **single course** (when compared to a curriculum-level approach)." The motivational benefit shrinks when you make the whole programme problem-driven.
- **Kirschner, Sweller & Clark (2006), "Why Minimal Guidance During Instruction Does Not Work," *Educational Psychologist* 41(2), 75–86, https://doi.org/10.1207/s15326985ep4102_1** (abstract fetched). The standing objection: minimally guided approaches "ignore both the structures that constitute human cognitive architecture and evidence from empirical studies over the past half-century." Their stated boundary condition matters: "The advantage of guidance begins to recede only when learners have sufficiently high prior knowledge to provide 'internal' guidance."

### Anchored instruction

**Cognition and Technology Group at Vanderbilt (1990), "Anchored Instruction and Its Relationship to Situated Cognition," *Educational Researcher* 19(6), 2–10, https://doi.org/10.3102/0013189X019006002**; and CTGV (1992) on the *Jasper Woodbury Problem Solving Series* — twelve videodisc adventures, each ending in a complex challenge whose data is embedded in the narrative, designed for generative problem-formulation rather than problem-solving-with-given-numbers. Reported gains concentrate in **problem-posing, planning, and attitudes toward maths**, with more modest gains on standard computation measures. **[unverified-here — both Wikipedia lookups 404'd and the primary sources were not reachable this session.]** Jasper was also never cleanly randomized at scale; the evidence is design-study evidence.

### The honest bottom line on through-lines

There is **no clean evidence that a narrative through-line beats a well-sequenced topic list on knowledge outcomes.** The reliable findings are:
1. Problem-driven structures help **application and transfer**, hurt or fail to help **initial knowledge acquisition** (Dochy et al.).
2. They help **motivation** at about **d = 0.5**, and *more so when used in one course than across a whole curriculum* (Zhang et al. 2024).
3. The knowledge decrement is worst for novices and recedes with prior knowledge (Kirschner et al.).

**Implication for Seba — a specific and defensible compromise.** Do not restructure the curriculum around a project. Do keep a **running motivating problem per unit** that is *referenced* at unit open and unit close and used as the synthesis task, while ordinary sessions remain directly instructed with worked examples and guided practice. That configuration takes the motivational effect (which is where the evidence is), takes the application/transfer effect at the one point in the unit where transfer is actually the goal, and avoids the novice knowledge-acquisition penalty that comes from making every session problem-driven. It also matches the 4C/ID whole-task-with-fading-support shape rather than fighting it.

For probability specifically: a recurring concrete scenario (one estimation problem the learner actually cares about) that gets revisited as the tools accumulate. For Italian: a recurring communicative goal, which is standard task-based language teaching practice anyway.

---

## 6. Interleaving across sessions

Direct evidence for *across-session* interleaving is thinner than for within-session, and there is a live theoretical dispute about whether cross-session interleaving is even the same phenomenon.

- **Samani & Pan (2021), "Interleaved practice enhances memory and problem-solving ability in undergraduate physics," *npj Science of Learning* 6, https://doi.org/10.1038/s41539-021-00110-x** (abstract fetched). This is the closest thing to across-session evidence: **thrice-weekly homework assignments over 8 weeks**, interleaved (alternating topics) vs conventionally blocked. On two surprise tests with novel, harder problems: "students recalled more relevant information and more frequently produced correct solutions after having engaged in interleaved practice (with observed **median improvements of 50% on test 1 and 125% on test 2**)." And the metacognitive trap: "students tended to rate the technique as **more difficult** and incorrectly believed that they **learned less** from it."
- **Firth, Rivers & Boyle (2021), "A systematic review of interleaving as a concept learning strategy," *Review of Education* 9, https://doi.org/10.1002/rev3.3266** (abstract fetched). 26 studies, 17 in the meta-analysis (32 datasets). Memory benefit **Hedges' g up to 0.65**; transfer to novel items **up to 0.66**. Key moderator: **"Interleaving was found to be of greatest use when differences between items are subtle."** Benefits extend to delayed tests. Caveat the authors themselves raise: "the literature is dominated by laboratory studies of university undergraduates."
- **Sana, Yan & Kim (2014)-type work and Carvalho & Goldstone, "Effects of interleaved and blocked study on delayed test of category learning generalization," *Frontiers in Psychology* 5:936, https://doi.org/10.3389/fpsyg.2014.00936** (abstract fetched). This one argues *against* the naive spacing account of interleaving: an interaction between schedule and category similarity, and "increasing the retention interval did not modulate this interaction." Their conclusion: **"the benefit of interleaving is not primarily due to temporal spacing during study, but rather due to the cross-category comparisons that interleaving facilitates."**

**This last point is the decisive one for session chaining.** If interleaving's active ingredient is **discriminative contrast** — juxtaposing confusable things so the learner must notice what distinguishes them — then it operates best at **short range**, within a session or across adjacent sessions, not across a whole course. Alternating *topics* across consecutive sessions gets you the spacing (which FSRS already gives you) but loses the contrast (because the confusable pair is never side by side).

**Implication for Seba, and it cuts against the obvious design.** Do **not** simply alternate topics session-to-session for its own sake. Instead:
1. Keep the **teaching** blocked — one concept per session, as currently designed. This is correct and the evidence supports it for acquisition.
2. Put the interleaving in the **practice block**, mixing today's concept with its **confusable siblings** in the concept graph — not with arbitrary due items. Confusability is the moderator (Firth et al.: "greatest use when differences between items are subtle"), and the concept graph can encode it.
3. Expect the learner to report that mixed practice feels worse and is less effective. Samani & Pan quantifies exactly this misperception. A tutor should say so out loud rather than let the learner conclude the method is failing.

This suggests one new piece of state: **a "confusable-with" edge type in the concept graph**, distinct from prerequisite edges. Cheap to add, and it is the thing that makes interleaving targeted rather than random. Candidates in probability: independence vs mutual exclusivity; P(A|B) vs P(B|A); PMF vs CDF; variance vs standard error. In Italian: passato prossimo vs imperfetto; essere vs avere auxiliaries; sapere vs conoscere.

---

## 7. Sleep-dependent consolidation between sessions

**Rasch & Born (2013), "About Sleep's Role in Memory," *Physiological Reviews* 93(2), 681–766, https://pmc.ncbi.nlm.nih.gov/articles/PMC3768102/** (fetched).

What the fetched text supports:
- **Both** declarative (facts, events, spatial) and procedural/non-declarative (motor skills, implicit learning) memory consolidate during sleep, "though through different mechanisms and sleep stages."
- **Slow-wave sleep** primarily supports **declarative** consolidation "through active reactivation of recently encoded representations, which are then redistributed to long-term cortical storage." **REM** shows "more selective benefits, particularly for procedural memory tasks with motor components," with effects "linked to specific conditions."
- **Active systems consolidation:** repeated reactivation during SWS, stabilization during REM. Hippocampal replay at "10–20 times" compressed speed, concentrated "within the first 20–40 min of sleep."
- **Naps work:** "a 90-min sleep period as well as 60-min naps, both containing mainly SWS," protect memory against interference.
- The classic contrast is **Jenkins & Dallenbach (1924)**: sleep substantially reduced forgetting relative to equivalent waking intervals across 1–8 hour retention periods.
- Effect sizes are not cleanly summarized in the review; the literature reports percentage improvements that vary widely by task.

**Targeted memory reactivation (TMR)** — re-presenting a cue (odour or sound) present at encoding during subsequent SWS — reliably improves retention of the cued material. Not implementable by a text tutor, but it is the mechanistic proof that *what gets reactivated during sleep is what gets consolidated*, and that reactivation is biased toward material tagged as **relevant/expected-to-be-tested** at encoding.

That last point is the actionable one. **Wilhelm et al. (2011), "Sleep selectively enhances memory expected to be of future relevance," *Journal of Neuroscience* 31(5), 1563–1569, https://doi.org/10.1523/JNEUROSCI.3575-10.2011** — participants told before sleep that they would be tested showed sleep-dependent retention benefits; those not told showed markedly less. **[unverified-here]**

**Implications for Seba, and they are specific:**

1. **At least one night should separate sessions on the same material.** This is a floor, not an optimum, and it coincides with what FSRS would schedule anyway. It argues against same-day double sessions for new material specifically — the second session gets no consolidation dividend from the first.
2. **The end-of-session recap is doing consolidation work, not just summary work.** Telling the learner explicitly what will be revisited next time plausibly tags that material as future-relevant, which is the Wilhelm et al. manipulation. This makes the closing move cheap-to-improve and mechanistically motivated: *close by naming what will be tested next session*, not by summarizing what happened.
3. **The declarative/procedural split maps onto Seba's two subjects.** Probability's declarative content benefits from SWS-rich early-night sleep; Italian's pronunciation/production automatization has a larger REM/late-night component. Neither is controllable by the tutor, but it means Italian's fluency layer is more dependent on *number of nights* elapsed (favouring more frequent, shorter sessions) while probability's is more tolerant of long gaps. This is a second, independent argument for the frequency asymmetry proposed in §2.
4. **Do not end a session with novel, unconsolidated, error-ridden material.** Retroactive interference is strongest for material encoded just before a break with no stabilization. The last block of a session should be *consolidating* (recap, retrieval of today's concept at high success rate) rather than *introducing*. This is already the shape of Seba's session; the evidence supports keeping it and resisting the temptation to "squeeze one more thing in."

---

## 8. Momentum, habit, and dropout for voluntary adult learners

This is the section where the effect sizes are largest, because the counterfactual is *zero learning*.

### The scale of the problem

- **Onah, Sinclair & Boyatt (2014), "Dropout Rates of Massive Open Online Courses: Behavioural Patterns," *EDULEARN14* / Warwick Research Archive, https://doi.org/10.13140/RG.2.1.2402.0009** (abstract fetched): "the completion rate for most courses is **below 13%**."
- **Eriksson, Adawi & Stöhr (2017), "'Time is the bottleneck': a qualitative study exploring why learners drop out of MOOCs," *Journal of Computing in Higher Education* 29, 133–146, https://doi.org/10.1007/s12528-016-9127-8** (abstract fetched). "Why do over 90% of the learners in MOOCs never finish the course?" Four factors: perception of course content, perception of course design, social situation and characteristics, and **"the learner's ability to find and manage time effectively."** The title is the finding.
- **Jansen, van Leeuwen, Janssen, Conijn & Kester (2020), "Supporting learners' self-regulated learning in MOOCs," *Computers & Education* 146, https://doi.org/10.1016/j.compedu.2019.103771** (abstract fetched). A three-video SRL intervention "positively affected learners' course completion" and increased planning, help-seeking, and persistence — **but "intervention compliance was however low,"** because "the great majority of learners who did not comply with the intervention **dropped out of the MOOC before they encountered the implemented intervention.**"

That last finding is the most important structural fact in this section: **retention interventions must fire early or they never fire at all.** Anything Seba does to secure return behaviour must be front-loaded into the first handful of sessions.

- **Badali et al. (2022), "The role of motivation in MOOCs' retention rates: a systematic literature review," *RPTEL* 17, https://doi.org/10.1186/s41039-022-00181-3** (abstract fetched). 50 publications; six motive families (academic, social, course, personal, professional, technological), with **academic motives most important**; effects mediated by satisfaction, self-regulation, attitude, performance, engagement, participation.

The MOOC caveat: MOOC dropout numbers are inflated by free enrolment with near-zero intent. A 1:1 tutor with a learner who *chose* this is a different population. But the *direction* of the findings — time management, early attrition, self-regulation — transfers.

### Habit formation

**Lally, van Jaarsveld, Potts & Wardle (2010), "How are habits formed: Modelling habit formation in the real world," *European Journal of Social Psychology* 40(6), 998–1009, https://doi.org/10.1002/ejsp.674** (abstract fetched). 96 volunteers, one daily behaviour in a consistent context ("for example 'after breakfast'"), 12 weeks, daily Self-Report Habit Index. Findings:

- Automaticity follows an **asymptotic curve**, fitted at the individual level.
- Time to reach 95% of asymptote **ranged from 18 to 254 days** — the widely-quoted "66 days" is the *median*, and the spread is the real finding. **[median value unverified-here; the 18–254 range is in the fetched abstract.]**
- **"Performing the behaviour more consistently was associated with better model fit"** — consistency of *context*, not total repetitions, drives automaticity.
- **"Missing one opportunity to perform the behaviour did not materially affect the habit formation process."**

That last sentence should be printed on the wall. It is the direct empirical refutation of the streak-shaming design pattern.

**Wood & Rünger (2016), "Psychology of Habit," *Annual Review of Psychology* 67, 289–314, https://doi.org/10.1146/annurev-psych-122414-033417** (abstract fetched): "habits form as people pursue goals by repeating the same responses **in a given context**"; habits and deliberate goal pursuit "guide actions synergistically, although habits are the efficient, **default** mode of response."

### Implementation intentions

**Gollwitzer & Sheeran (2006), "Implementation Intentions and Goal Achievement: A Meta-Analysis of Effects and Processes," *Advances in Experimental Social Psychology* 38, 69–119, https://doi.org/10.1016/S0065-2601(06)38002-1.** 94 independent tests, ~8,000 participants, **medium-to-large effect d ≈ 0.65** on goal attainment over and above goal intentions alone. Format: **"If situation X arises, then I will perform response Y."** Mechanism: delegating action initiation to an environmental cue, making initiation automatic and cue-triggered rather than requiring deliberate intent at the moment of action. **[unverified-here — the NYU-hosted PDF now redirects to a faculty profile page and the full text was not reachable this session.]**

Note the convergence: Lally says *consistent context* drives automaticity; Gollwitzer says *if-then cue binding* drives initiation; Wood says habits are context-response bindings. All three point at the same design move: **bind the session to a specific recurring cue, and get the learner to state that binding explicitly.**

### Streaks: what Duolingo actually reports

**Duolingo Blog, "How the Duolingo streak builds habits," https://blog.duolingo.com/how-duolingo-streak-builds-habit/** (fetched). Company-reported, not peer-reviewed, and the metrics are engagement metrics rather than learning metrics — weight accordingly.

- "over 6 million people on a streak of 7 days or more."
- Showing streak animations to new learners made them **1.7% more likely** to be active seven days later.
- **"Learners who reach a streak of just 7 days are 3.6× more likely to complete their course."** This is almost certainly heavily confounded by selection — motivated learners both streak and complete — but the 7-day threshold as a *milestone* is consistent with Lally's early-steep automaticity curve.
- **Streak Freezes:** allowing two simultaneously equipped Streak Freezes increased daily active learners by **+0.38%**. Small in absolute terms, but the direction matters enormously: **making the streak more forgiving increased engagement.**
- Percentage psychology: "advancing from 2 to 3 days represents a 50% increase, while 200 to 201 days is only 0.5%" — i.e. streaks lose motivational power as they lengthen, by construction.

**The synthesis on streaks is more nuanced than "add a streak."** The evidence supports *consistency tracking* and *early milestones*; it does **not** support loss-aversion-based punishment. Lally's "missing one opportunity did not materially affect the habit formation process" plus Duolingo's own Streak Freeze result both say the same thing: a broken streak is not a broken habit, and systems that treat it as one lose users at exactly the moment they should be re-engaging them. A streak that resets to zero after one missed day encodes a *false* model of habit formation and creates a dropout cliff at the first slip.

**Implication for Seba.** Track consistency, celebrate early milestones (the 7-day threshold has both Duolingo's data and Lally's curve behind it), and design the **return-after-a-lapse** path as a first-class feature rather than an afterthought. Concretely: a learner returning after two weeks away should get a session explicitly designed for that — heavy FSRS backlog triage, no new concept, an explicit "here's where we were" re-orientation, and zero guilt framing. Seba's persisted state makes this easy and it is exactly what a streak-based app cannot do.

---

## 9. Goal setting across sessions

- **Locke & Latham (2002), "Building a practically useful theory of goal setting and task motivation: A 35-year odyssey," *American Psychologist* 57(9), 705–717, https://doi.org/10.1037/0003-066X.57.9.705.** Core: "specific, difficult goals lead to significantly higher performance than easy goals, no goals, or even... 'do your best'." Roughly **90% of laboratory and field studies** with specific challenging goals showed higher performance than easy or no goals (fetched summary). Moderators: **feedback** (goals and feedback are synergistic and neither works well alone), **commitment** (driven by outcome importance and self-efficacy), and **task complexity**.
- The **task-complexity moderator is critical and usually ignored**: for complex tasks where the learner lacks the requisite strategy, *specific performance goals can underperform "do your best,"* while **specific learning goals retain their effectiveness** (fetched: "In complex tasks, 'do your best' instruction can outperform specific performance goals, but specific learning goals maintain effectiveness"; "Learning goals prevent tunnel vision and excel when task knowledge gaps exist").
- **Bandura & Schunk (1981), "Cultivating competence, self-efficacy, and intrinsic interest through proximal self-motivation," *Journal of Personality and Social Psychology* 41(3), 586–598, https://doi.org/10.1037/0022-3514.41.3.586** (abstract fetched). Children with "gross deficits and disinterest in mathematical tasks" did self-directed learning under **proximal subgoals**, **distal goals**, or **no goals**. Results: "support for the superiority of proximal self-influence. Under proximal subgoals, children progressed rapidly in self-directed learning, achieved substantial mastery of mathematical operations, and developed a sense of personal efficacy and intrinsic interest in arithmetic activities that initially held little attraction for them. **Distal goals had no demonstrable effects.**" Also: "goal proximity fostered veridical self-knowledge of capabilities as reflected in high congruence between judgments of mathematical self-efficacy and subsequent mathematical performance."

That is a remarkably on-point study for Seba: self-directed learning, initially disinterested learner, long horizon, and the finding is that **a distal goal alone does nothing** while proximal subgoals produce competence, self-efficacy, *and* intrinsic interest. "Learn probability theory" is a distal goal. It will do nothing on its own.

- **Epton, Currie & Armitage (2017), "Unique effects of setting goals on behavior change: Systematic review and meta-analysis," *Journal of Consulting and Clinical Psychology* 85(12), https://doi.org/10.1037/ccp0000260** (abstract fetched). 141 papers, **384 effect sizes, N = 16,523**. Unique effect of goal setting **d = 0.34** (CI [.28, .41]). Moderators: goal setting is more effective if the goal is **difficult** and **set publicly**.
- **Progress monitoring.** **Harkin et al. (2016), "Does monitoring goal progress promote goal attainment? A meta-analysis of the experimental evidence," *Psychological Bulletin* 142(2), 198–229, https://doi.org/10.1037/bul0000025.** 138 studies, N > 19,000; prompting progress monitoring had a small-to-medium effect (**d ≈ 0.40**) on goal attainment, and the effect was **larger when progress was physically recorded or publicly reported**. **[unverified-here — direct OpenAlex query surfaced adjacent goal-setting meta-analyses but not this one.]**

**Implications for Seba.**
1. The distal goal ("understand probability theory") should exist but should never be the operative goal in a session. It is Bandura & Schunk's null condition.
2. Each session needs a **specific, difficult, proximal** goal, stated at session open and evaluated at session close. Locke & Latham's specificity requirement means "learn about conditional probability" is not a goal; "be able to compute P(A|B) from a two-way table and explain why it differs from P(B|A)" is.
3. Because probability is a **complex task with knowledge gaps**, goals should be **learning goals** ("work out what distinguishes X from Y"), not performance goals ("get 8/10"). This is the one place where goal-setting theory's default advice inverts, and it is exactly Seba's regime.
4. **Progress must be visible.** Seba has a concept graph with statuses — that is a progress artifact that already exists and is currently invisible to the learner. Rendering it is the cheapest high-value motivational move available.
5. Goal + feedback are synergistic and neither works alone. A stated session goal with no closing evaluation of whether it was met is half an intervention.

---

## 10. Course-level assessment moments

Rosenshine's principle 10 explicitly pairs review with testing: "Some effective teachers also gave tests after their reviews," and the weekly-quizzes-beat-one-or-two-quizzes finding. Butler & Roediger (2007, https://doi.org/10.3758/bf03194052) establishes that test-enhanced learning generalizes from lab to classroom.

The distinct argument for a **checkpoint session** — as opposed to just more quizzing — rests on four things a checkpoint does that an ordinary session's review block does not:

1. **Cumulative, unpredictable retrieval across the whole unit**, rather than the FSRS-selected subset. FSRS shows you what it predicts you're about to forget; a checkpoint samples what you *believe* you know. The gap between those two sets is exactly where miscalibration lives.
2. **Recalibration of the learner model.** For a tutor with persistent state, a checkpoint is a *measurement* event that corrects accumulated drift in the concept-graph statuses. Statuses set during teaching sessions are contaminated by scaffolding; a checkpoint measures unscaffolded performance. This is the 4C/ID "final unsupported whole task" criterion.
3. **Metacognitive correction.** The Samani & Pan finding (interleaved practice felt harder and was believed less effective while being more effective) shows learners' judgements of their own learning are systematically wrong in the direction that discourages good practice. A checkpoint that demonstrates retention the learner did not expect is a direct intervention on that misjudgement — and Janes et al. (2021) found exactly this cluster of metacognitive benefits from successive relearning.
4. **A proximal goal with a deadline.** Per Bandura & Schunk, this is the mechanism, not a side effect.

**Caveat.** Do not make checkpoints high-stakes-feeling. Janes et al.'s finding of *reduced anxiety* came from low-stakes repeated relearning; a voluntary adult learner who experiences a checkpoint as an exam has a new reason not to come back, and per Jansen et al. the dropout happens before the intervention lands.

---

## Proposed multi-session architecture: a ~10-session unit

One **unit** = one 4C/ID task class = a run of sessions at one complexity level, ending when the learner can perform an unsupported whole task at that level. Roughly 10 sessions, but **state-terminated, not count-terminated**.

```
S1   UNIT OPEN / EPITOME
     - Wide-angle: the simplest complete version of what this unit lets you do
     - Introduce the unit's running problem (the motivating anchor)
     - Elicit the learner's proximal goal for the unit; state the distal goal once, then drop it
     - Full support: worked example end to end
     - Light review only (previous unit's FSRS backlog)

S2-4 ORDINARY LESSONS (high → medium support)
     Standard shape: open-review → one concept → practice → recap → close
     - Open-review = union of (FSRS-due) ∪ (prereqs of today's concept) ∪ (last session's error sites)
     - Practice block interleaves today's concept with its confusable siblings
     - Support fades: S2 worked example → S3 completion problem → S4 guided

S5   SYNTHESIS / ZOOM-OUT  (not a checkpoint)
     - No new concept
     - Render the concept graph: "here's the map; explain how these connect"
     - Return to the unit's running problem; solve a piece of it now that the tools exist
     - This is the Elaboration Theory synthesizer, and the cheapest use of existing state

S6-8 ORDINARY LESSONS (medium → low support)
     - Same shape; scaffolding continues fading toward independent
     - Cross-unit retrieval starts appearing in the open-review block (previous units)

S9   SYNTHESIS / ZOOM-OUT #2
     - Full unit map; the running problem now solvable end to end
     - This is the 4C/ID "final unsupported whole task"

S10  CHECKPOINT
     - Cumulative, unscaffolded, sampling the whole unit (not FSRS-selected)
     - Explicitly low-stakes; framed as measurement, not judgement
     - Outcome writes back to concept-graph statuses (the recalibration)
     - Close by setting the next unit's proximal goal
     → If checkpoint fails on ≥2 concepts: insert 1-2 repair sessions before the next unit,
       and re-scaffold (support goes back UP at the start of the next task class anyway)
```

**Recurrence table.**

| Element | Frequency | Basis |
|---|---|---|
| Open-review (5–8 min, retrieval) | Every session | Rosenshine P1; Good & Grouws 1979 |
| Explicit bridge to last session | Every session | Ausubel; ~0.2 SD, cheap |
| Stated proximal session goal | Every session | Bandura & Schunk 1981; Locke & Latham |
| Close by naming what's next | Every session | Wilhelm et al. 2011 (future-relevance tagging) |
| Interleaved practice w/ confusables | Every session | Firth et al. 2021; Carvalho & Goldstone 2014 |
| Cross-unit retrieval in open-review | From ~S6 | Rosenshine P10 |
| Synthesis / zoom-out | Every ~4–5 sessions | Elaboration Theory; 4C/ID (design theory, not RCT) |
| Checkpoint | Every ~10 sessions / unit end | Rosenshine P10 + Butler & Roediger 2007 |
| Progress rendered visible | Every session close | Harkin et al. 2016; Locke & Latham (goal+feedback) |
| Support level reset upward | At each unit open | 4C/ID sawtooth |

**Cadence:** ~25–45 min/session; 3–4×/week Italian, 2–3×/week probability; never two consecutive misses; at least one night between sessions on the same new material. Frequency asymmetry is theory-driven (automatization vs schema-building; REM vs SWS), not directly evidenced.

**Ratio:** roughly **7 ordinary : 2 synthesis : 1 checkpoint**. Note this spends ~30% of sessions not teaching new material. That is the uncomfortable implication of the review literature and Rosenshine says so plainly: material that is not adequately practised and reviewed is easily forgotten.

---

## Numbered recommendations, ordered by expected effect

**1. Widen the opening review from "FSRS-due" to a three-way union. — CHEAP (prompt + briefing generator).**
Open-review = FSRS-due ∪ prerequisites-of-today's-concept ∪ last-session's-error-sites, retrieved not restated, 5–8 minutes.
*Basis:* Rosenshine P1, read verbatim from source; working-memory mechanism.
*State change:* No new fields. The briefing generator must traverse concept-graph prerequisite edges for today's target and read error sites out of per-concept notes. Requires that notes record *errors* in a locatable way — currently freeform, so this is the one soft dependency.
*Why first:* Highest ratio of evidence-strength to implementation cost in the entire brief. FSRS due-ness is orthogonal to what today's lesson needs.

**2. Make `next_session_hint` a bridge, not a topic. — CHEAP (prompt).**
It should carry: the concept, the *relational* link to last session, the specific error to repair, and the opening move. One sentence becomes three.
*Basis:* Ausubel/advance organizers (~0.2 SD, small but cheap); Rosenshine P1's error-repair clause.
*State change:* Same field, richer contract. Add a schema/example to the prompt that writes it.

**3. Add a synthesis session every 4–5 sessions that renders the concept graph back to the learner. — CHEAP (prompt + existing state).**
No new concept. "Here's the map of this unit — explain how these three connect. Where does Tuesday's idea sit?"
*Basis:* Elaboration Theory synthesizers; 4C/ID; Rosenshine P10's *structural* rationale ("develop new knowledge into patterns"), which FSRS does not serve. **Design-theory support, not a meta-analytic effect size — recommend on structure, not on evidence strength.**
*State change:* Needs a session-type marker in state so the tutor knows which kind of session this is, and a session counter since last synthesis.

**4. Add a per-session proximal learning goal, stated at open and evaluated at close. — CHEAP (prompt + one state field).**
Specific and difficult; a *learning* goal not a performance goal, because probability is a complex task with knowledge gaps — this is where goal-setting theory's usual advice inverts.
*Basis:* Bandura & Schunk 1981 (distal goals had **no demonstrable effects**; proximal subgoals produced competence, self-efficacy *and* intrinsic interest); Locke & Latham 2002; Epton et al. 2017 (d = 0.34).
*State change:* One new field, `session_goal`, set at close of session N for session N+1, evaluated at close of N+1. Pairs naturally with `next_session_hint`.

**5. Render progress visibly at every session close. — CHEAP (prompt), MEDIUM if you want a real view.**
Concept-graph statuses and successive-relearning history ("you've now recalled this correctly on four occasions across five weeks") shown to the learner.
*Basis:* Locke & Latham (goals and feedback are synergistic, neither works alone); Harkin et al. 2016; Janes et al. 2021 (relearning produced increased self-reported sense of mastery and reduced anxiety).
*State change:* None new — this is pure surfacing of state Seba already holds. That is what makes it cheap and what makes the current invisibility wasteful.

**6. Add a `confusable-with` edge type to the concept graph and interleave practice against it. — MEDIUM (schema change + curation).**
Keep *teaching* blocked (one concept per session). Put interleaving in the *practice* block, against confusable siblings specifically, not random due items.
*Basis:* Firth et al. 2021 (g up to 0.65/0.66; **"greatest use when differences between items are subtle"**); Carvalho & Goldstone 2014 (the active ingredient is discriminative contrast, **not** temporal spacing — so random cross-session topic alternation gets you nothing FSRS isn't already giving you); Samani & Pan 2021.
*State change:* New edge type in the concept graph, populated as concepts are introduced. This is the main new *structure* recommended here, and it is what makes interleaving targeted instead of decorative.
*Corollary — CHEAP:* warn the learner that mixed practice will feel harder and less effective, because Samani & Pan shows it reliably does while being more effective.

**7. Design the return-after-a-lapse session as a first-class session type. — MEDIUM (new session type + trigger).**
Triggered by elapsed time since last session. Heavy FSRS backlog triage, **no new concept**, explicit re-orientation from the last summary, zero guilt framing.
*Basis:* Lally et al. 2010 — **"missing one opportunity to perform the behaviour did not materially affect the habit formation process"**; Duolingo's own Streak Freeze result (making streaks *more forgiving* raised engagement +0.38%); Jansen et al. 2019 (retention interventions fail because learners drop out before encountering them).
*State change:* Needs `last_session_date` (probably already implicit) and a session-type branch in the briefing generator. This is the highest-value *retention* move and it is precisely what a streak app structurally cannot do and a stateful tutor can.

**8. Add a checkpoint session per unit that writes back to the learner model. — MEDIUM.**
Cumulative, unscaffolded, samples the whole unit rather than the FSRS-selected subset; explicitly low-stakes; results update concept-graph statuses.
*Basis:* Rosenshine P10 ("classes that had weekly quizzes scored better on final exams than did classes with only one or two quizzes"); Butler & Roediger 2007; 4C/ID's unsupported-whole-task criterion; the statuses-drift argument (teaching-session statuses are contaminated by scaffolding).
*State change:* Session-type marker; a write-back path from checkpoint performance to concept statuses; a unit boundary concept in state. This is the most invasive recommendation and the one most worth doing properly.
*Caveat:* keep it low-stakes. Janes et al.'s anxiety-reduction finding came from low-stakes repeated relearning; a checkpoint that reads as an exam is a dropout risk.

**9. Explicitly manage scaffolding level across a unit, with a reset upward at unit boundaries. — MEDIUM (one state field, real behavioural consequences).**
Worked example → completion problem → guided → independent within a unit; back to worked example at the next unit's higher complexity.
*Basis:* 4C/ID task classes and fading support; Kirschner, Sweller & Clark 2006 ("the advantage of guidance begins to recede only when learners have sufficiently high prior knowledge"); Rosenshine's 80% success-rate target as the calibration signal.
*State change:* A `support_level` field per unit, advanced on success and reset at unit open. Without it, a tutor that fades support for six sessions then jumps complexity produces a failure that reads falsely as learner regression.

**10. Add a running motivating problem per unit — referenced at unit open, revisited at each synthesis, solved at unit close. — CHEAP (prompt + one state field).**
Do **not** restructure sessions around it. Ordinary sessions stay directly instructed with worked examples.
*Basis:* Zhang et al. 2024 (problem-driven learning, motivation **d = 0.498**, and notably **larger effects in a single course than at curriculum level**); Dochy et al. 2003 (PBL helps application/transfer, hurts initial knowledge acquisition); Kirschner et al. 2006. The honest reading: **there is no clean evidence a narrative through-line beats a well-sequenced topic list on knowledge outcomes.** Take the motivational effect where the evidence is and avoid the novice knowledge-acquisition penalty.
*State change:* One field, `unit_anchor`, set at unit open.

**11. Set cadence policy explicitly, and allow it to degrade gracefully. — CHEAP (prompt/policy).**
~25–45 min; 3–4×/week Italian, 2–3×/week probability; ≥1 night between sessions on the same new material; prefer widening gaps over demanding missed sessions be made up.
*Basis:* Baddeley & Longman 1978 (total time constant, distributed beat massed, **and the efficient group was the least satisfied**); Bahrick et al. 1993 (**13 sessions at 56 days ≈ 26 sessions at 14 days** — session count trades against gap width); Rasch & Born 2013 (overnight consolidation; SWS-declarative vs REM-procedural split).
*State change:* Policy in the prompt, not new state. Note honestly that the frequency asymmetry between the two subjects is theory-driven; Kasprowicz et al. 2019 found **minimal difference between 7-day and 3.5-day spacing** in an L2 classroom, so do not over-claim precision here.

**12. Close every session by naming what will be tested next time. — CHEAP (prompt).**
Not "here's what we covered" but "next time I'll ask you to derive X cold."
*Basis:* Wilhelm et al. 2011 (sleep selectively consolidates memory expected to be of future relevance); Rasch & Born 2013 on reactivation-driven consolidation. Also the last block of a session should consolidate, never introduce.
*State change:* None; it is the existing recap move, re-pointed forward instead of backward. Overlaps with #2 and #4 and should be implemented with them as a single "session close" contract.

---

### What is deliberately *not* recommended

- **Alternating topics session-to-session** for interleaving's sake. Carvalho & Goldstone's evidence says the active ingredient is discriminative contrast, which operates at short range; the spacing component is already covered by FSRS. See #6 for the version that is worth doing.
- **A streak with punitive reset.** Lally et al. and Duolingo's own Streak Freeze data both point the other way. See #7.
- **Restructuring the course as a project.** Dochy et al.'s knowledge-acquisition decrement plus Kirschner et al.'s novice-guidance argument. See #10.
- **Selling mastery gating as a large effect.** Kulik et al. and Slavin *agree* that effects on standardized measures are near zero. The prerequisite DAG already provides the sequencing hygiene that is the real benefit.
- **Claiming an effect size for synthesis sessions.** The support is design theory and mechanism, not meta-analysis. Recommend on structure; say so.

---

## Sources

- Rosenshine, B. (2012). Principles of Instruction. *American Educator* 36(1), 12–19, 39. https://www.aft.org/sites/default/files/Rosenshine.pdf *(full text read)*
- Good, T. & Grouws, D. (1979). The Missouri Mathematics Effectiveness Project. *J. Educational Psychology* 71(3), 355–362. https://doi.org/10.1037/0022-0663.71.3.355
- Kulik, C-L., Kulik, J. & Bangert-Drowns, R. (1990). Effectiveness of Mastery Learning Programs. *Review of Educational Research* 60(2). https://doi.org/10.3102/00346543060002265
- Slavin, R. (1990). Mastery Learning Re-Reconsidered. *Review of Educational Research* 60(2), 300–302. https://doi.org/10.3102/00346543060002300
- Janes, J., Dunlosky, J., Rawson, K. & Jasnow, A. (2021). The benefits of successive relearning on multiple learning outcomes. *J. Educational Psychology*. https://doi.org/10.1037/edu0000693
- Higham, P. et al. (2022). Enhancing learning and retention through the distribution of practice repetitions across multiple sessions. *Memory & Cognition* 50. https://doi.org/10.3758/s13421-022-01361-8
- Baddeley, A. & Longman, D. (1978). The influence of length and frequency of training session on the rate of learning to type. *Ergonomics* 21(8), 627–635. https://doi.org/10.1080/00140137808931764
- Bahrick, H. et al. (1993). Maintenance of foreign language vocabulary and the spacing effect. *Psychological Science* 4(5), 316–321. https://doi.org/10.1111/j.1467-9280.1993.tb00571.x
- Kasprowicz, R., Marsden, E. & Sephton, N. (2019). Investigating Distribution of Practice Effects... *Modern Language Journal* 103(3). https://doi.org/10.1111/modl.12586
- Elgort, I., Beliaeva, N. & Boers, F. (2020). Effects of spacing on contextual vocabulary learning. *Second Language Research* 36(4). https://doi.org/10.1177/0267658320927764
- Ausubel, D. (1960). The use of advance organizers... *J. Educational Psychology* 51(5), 267–272. https://doi.org/10.1037/h0046669
- Luiten, J., Ames, W. & Ackerson, G. (1980). A Meta-Analysis of the Effects of Advance Organizers. *AERJ* 17(2), 211–218. https://doi.org/10.3102/00028312017002211
- Sáez, M. & Chacón, J. (2023). Ausubel's meaningful learning re-visited. *Current Psychology*. https://doi.org/10.1007/s12144-023-04440-4
- Butler, A. & Roediger, H. (2007). Generalizing test-enhanced learning from the laboratory to the classroom. *Psychonomic Bulletin & Review* 14. https://doi.org/10.3758/bf03194052
- van Merriënboer, J., Clark, R. & de Croock, M. (2002). Blueprints for complex learning: The 4C/ID-model. *ETR&D* 50(2), 39–64. https://doi.org/10.1007/BF02504993
- Reigeluth, C. (1999). The Elaboration Theory. In *Instructional-Design Theories and Models, Vol. II*. Erlbaum.
- Chen, C-H. & Yang, Y-C. (2019). Revisiting the effects of project-based learning... *Educational Research Review* 26, 71–81. https://doi.org/10.1016/j.edurev.2018.11.001
- Zhang, L. & Ma, Y. (2023). A study of the impact of project-based learning on student learning effects. *Frontiers in Psychology* 14. https://doi.org/10.3389/fpsyg.2023.1202728
- Dochy, F. et al. (2003). Effects of problem-based learning: a meta-analysis. *Learning and Instruction* 13(5), 533–568. https://doi.org/10.1016/S0959-4752(02)00025-7
- Zhang, L., Loyens, S. et al. (2024). The Effects of Problem-Based, Project-Based, and Case-Based Learning on Students' Motivation. *Educational Psychology Review* 36. https://doi.org/10.1007/s10648-024-09864-3
- Kirschner, P., Sweller, J. & Clark, R. (2006). Why Minimal Guidance During Instruction Does Not Work. *Educational Psychologist* 41(2), 75–86. https://doi.org/10.1207/s15326985ep4102_1
- CTGV (1990). Anchored Instruction and Its Relationship to Situated Cognition. *Educational Researcher* 19(6), 2–10. https://doi.org/10.3102/0013189X019006002
- Samani, J. & Pan, S. (2021). Interleaved practice enhances memory and problem-solving ability in undergraduate physics. *npj Science of Learning* 6. https://doi.org/10.1038/s41539-021-00110-x
- Firth, J., Rivers, I. & Boyle, J. (2021). A systematic review of interleaving as a concept learning strategy. *Review of Education* 9. https://doi.org/10.1002/rev3.3266
- Carvalho, P. & Goldstone, R. (2014). Effects of interleaved and blocked study on delayed test of category learning generalization. *Frontiers in Psychology* 5:936. https://doi.org/10.3389/fpsyg.2014.00936
- Rasch, B. & Born, J. (2013). About Sleep's Role in Memory. *Physiological Reviews* 93(2), 681–766. https://pmc.ncbi.nlm.nih.gov/articles/PMC3768102/
- Wilhelm, I. et al. (2011). Sleep selectively enhances memory expected to be of future relevance. *J. Neuroscience* 31(5), 1563–1569. https://doi.org/10.1523/JNEUROSCI.3575-10.2011
- Onah, D., Sinclair, J. & Boyatt, R. (2014). Dropout Rates of Massive Open Online Courses. https://doi.org/10.13140/RG.2.1.2402.0009
- Eriksson, T., Adawi, T. & Stöhr, C. (2017). "Time is the bottleneck". *J. Computing in Higher Education* 29, 133–146. https://doi.org/10.1007/s12528-016-9127-8
- Jansen, R. et al. (2020). Supporting learners' self-regulated learning in MOOCs. *Computers & Education* 146. https://doi.org/10.1016/j.compedu.2019.103771
- Badali, M. et al. (2022). The role of motivation in MOOCs' retention rates. *RPTEL* 17. https://doi.org/10.1186/s41039-022-00181-3
- Lally, P. et al. (2010). How are habits formed. *European J. Social Psychology* 40(6), 998–1009. https://doi.org/10.1002/ejsp.674
- Wood, W. & Rünger, D. (2016). Psychology of Habit. *Annual Review of Psychology* 67, 289–314. https://doi.org/10.1146/annurev-psych-122414-033417
- Gollwitzer, P. & Sheeran, P. (2006). Implementation Intentions and Goal Achievement: A Meta-Analysis. *Advances in Experimental Social Psychology* 38, 69–119. https://doi.org/10.1016/S0065-2601(06)38002-1
- Duolingo Blog. How the Duolingo streak builds habits. https://blog.duolingo.com/how-duolingo-streak-builds-habit/
- Locke, E. & Latham, G. (2002). Building a practically useful theory of goal setting... *American Psychologist* 57(9), 705–717. https://doi.org/10.1037/0003-066X.57.9.705
- Bandura, A. & Schunk, D. (1981). Cultivating competence, self-efficacy, and intrinsic interest through proximal self-motivation. *JPSP* 41(3), 586–598. https://doi.org/10.1037/0022-3514.41.3.586
- Epton, T., Currie, S. & Armitage, C. (2017). Unique effects of setting goals on behavior change. *J. Consulting and Clinical Psychology* 85(12). https://doi.org/10.1037/ccp0000260
- Harkin, B. et al. (2016). Does monitoring goal progress promote goal attainment? *Psychological Bulletin* 142(2), 198–229. https://doi.org/10.1037/bul0000025
- Dunlosky, J. et al. (2013). Improving Students' Learning With Effective Learning Techniques. *PSPI* 14(1). https://doi.org/10.1177/1529100612453266
