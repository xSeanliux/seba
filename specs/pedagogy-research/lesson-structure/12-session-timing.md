# Within-Session Timing, Ordering, and Memory
### Research round 12 — where things go inside a single Seba session, and how long a session should be

Scope: effects operating *inside* one study episode (minutes to ~1 hour). Cross-session scheduling, turn-level moves, curriculum sequencing and learner modelling are covered elsewhere and are not re-derived here.

Headline: the within-session timing literature is **much weaker than the cross-session literature**. Almost everything popular here (10-minute attention spans, primacy/recency lesson design, "6-minute videos", micro-offline consolidation) is either unsupported or a mis-transfer from a different paradigm. The findings that *do* survive are: interpolated retrieval beats end-only retrieval; problem-solving-before-instruction beats instruction-first; within-session repetition has hard diminishing returns after ~2–3 successful retrievals; measurable fatigue accumulates over hours and a real break partly reverses it; and end-of-episode affect predicts *return*, not learning.

---

## 1. Serial position effects — does the middle of a lesson get lost?

**What the classic evidence actually is.** Serial position curves (Murdock 1962; Glanzer & Cunitz 1966) come from immediate free recall of ~15–20 item word lists presented at ~1 item/second. Two separate components:

- **Recency** is a short-term-store effect. Glanzer & Cunitz's central result is that a ~30-second *filled* delay (counting backwards) between the last item and recall **abolishes the recency advantage entirely** while leaving primacy intact. Anything that happens after the "last item" destroys recency.
- **Primacy** is a rehearsal/consolidation effect — early items get more rehearsal and enter long-term store.

The recency finding is the fatal one for the educational extrapolation. If 30 seconds of arithmetic wipes out recency in a word list, the material at minute 44 of a 45-minute lesson has no comparable protection when the test is tomorrow. Long-term recency does exist (continuous-distractor paradigm), but it operates at the level of *items within a series*, at ratios of spacing to retention interval — it is not a claim that "the last thing in a lesson sticks."

**The educational claim.** The lesson-design version — David Sousa's *How the Brain Learns*: "prime-time 1" (first ~20 min), a "down-time" trough in the middle, "prime-time 2" at the end, therefore teach new material first and last and do practice in the middle — is a direct extrapolation from word lists to 40-minute lessons. I could find **no primary study measuring recall as a function of position within a lecture or tutoring session**. Searches of OpenAlex and Europe PMC for position-within-lecture retention returned nothing on point. This should be treated as an untested extrapolation, in the same family as other classroom neuromyths, not as an evidence-based design rule.

**What is actually documented across a lecture is a monotonic decline, not a U.** Risko, Anderson, Sarwal, Engelhardt & Kingstone (2012, *Applied Cognitive Psychology*) and Risko, Buchanan, Medimorec & Kingstone (2013, "Everyday attention and lecture retention: the effects of time, fidgeting, and mind wandering", *Frontiers in Psychology* 4:619, doi:10.3389/fpsyg.2013.00619, ~189 citations) find that **mind wandering increases and retention of lecture material decreases as a function of time on task** — a downward slope, with no recovery at the end. Cherry et al. (2024, *Memory & Cognition*, PMID 38151674) confirm mind-wandering frequency predicts poorer recall at both immediate and 1-week test.

**Honest assessment.** Serial position in list learning: extremely robust, but at a timescale (seconds) and grain (items) that does not map onto lesson segments. "Middle of the lesson slump": no direct evidence; the observed shape is late decline, not a trough. Evidence quality for the educational claim: **very low**.

**Implication for Seba.** Do not build the session around a U-shape. Do build around (a) freshest-first for the most demanding work, (b) the fact that the *end* has no automatic memory protection — so an end-of-session recap has to earn its retention through *retrieval*, not through position, and (c) the end's real leverage is affective, not mnemonic (§7).

---

## 2. Attention span and session length

### 2.1 The 10–15 minute claim does not survive

**Wilson & Korn (2007), "Attention During Lectures: Beyond Ten Minutes", *Teaching of Psychology* 34(2):85–89, doi:10.1080/00986280701291291** (~270 citations). Reviewed the evidence base across note-taking studies, direct observation, self-report, and physiological measures. Conclusion: "the research on which this estimate is based provides little support for" a 10–15 minute attention decline; individual variation dominates.

**Bradbury (2016), "Attention span during lectures: 8 seconds, 10 minutes, or more?", *Advances in Physiology Education* 40(4):509–513, doi:10.1152/advan.00109.2016** (~480 citations). From the abstract: "several institutions have reduced their lectures to 15 min in length based upon the 'common knowledge' and 'consensus' that there is a decline in students' attention 10–15 min into lectures. A review of the literature on this topic reveals many discussions referring to prior studies but scant few primary investigations. **Alarmingly, the most often cited source for a rapid decline in student attention during a lecture barely discusses student attention at all.** Of the studies that do attempt to measure attention, many suffer from methodological flaws and subjectivity in data collection. Thus, the available primary data do not support the concept of a 10- to 15-min attention limit." His most consistent positive finding: **the largest source of variability in attention is the difference between teachers, not the format or duration.**

This is a case where institutions changed policy on a citation chain with no primary study at the root. It should be explicitly *not* encoded.

### 2.2 What the better attention data show

**Bunce, Flens & Neiles (2010), "How Long Can Students Pay Attention in Class? A Study of Student Attention Decline Using Clickers", *Journal of Chemical Education* 87(12):1438–1443, doi:10.1021/ed100409p** (~430 citations). Students self-reported attention lapses in real time via clickers. Findings: lapses are **short — mostly one minute or less — and cyclical**, not a single cliff; they cluster early (around 30 s, then ~4.5–5.5 min, then ~7–9 min into a segment) and their frequency **drops during and immediately after student-centred activities** (clicker questions, demonstrations), with the reduction persisting into the following segment. The operative variable is *activity structure*, not elapsed minutes.

**Vigilance decrement** is real but is the wrong model. Klein & Feltmate (2025, *Frontiers in Cognition*, PMID 42339245) review 75 years of vigilance research; Zanesco et al. (2026, *Attention, Perception & Psychophysics*, PMID 41920493) show detection accuracy depends on how long attention must be sustained on a trial. But vigilance paradigms are rare-target, low-stimulation, response-sparse monitoring tasks. A 1:1 text dialogue where the learner must produce an answer every 30–90 seconds is close to the *opposite* regime — the response requirement is itself the attention reset that Bunce et al. found works. Transferring vigilance decrement rates to interactive tutoring is unwarranted.

### 2.3 The MOOC video data — what it does and doesn't show

**Guo, Kim & Rubin (2014), "How video production affects student engagement: an empirical study of MOOC videos", *L@S '14*, doi:10.1145/2556325.2566239** — 6.9 million video watching sessions across four Fall-2012 edX courses (MIT/Harvard/Berkeley, all math/science). PDF: https://up.csail.mit.edu/other-pubs/las2014-pguo-engagement.pdf

Verbatim findings from the paper:
- "Video length was by far the most significant indicator of engagement."
- "**The median engagement time is at most 6 minutes, regardless of total video length.**"
- "Students often make it less than halfway through videos longer than 9 minutes."
- Shortest videos (0–3 min) had highest engagement and least variance: "75% of sessions lasted over three quarters of the video length."
- Tutorial videos: "students engaged with tutorials for only 2 to 3 minutes, regardless of video length," whereas lecture engagement rises and falls with length.
- Speaking rate mattered: faster-speaking instructors got up to 2× the engagement; the authors themselves call speaking rate "merely a surface feature that correlates with enthusiasm."

The authors' own **limitations section**, verbatim: "This paper presents a retrospective study, not a controlled experiment." Only seven Fall-2012 courses had full logs, all math/science; edX's first cohort "are more likely to be self-motivated learners and technology early adopters"; and "we cannot measure a student's true engagement with videos just from analyzing server logs… a student could be playing a video in the background while browsing Facebook."

**What it does not show:** it is not a measure of attention, it is a measure of *when people navigate away from a page*, in a medium with zero interaction requirement, no accountability, and free skipping. Video length was not randomly assigned — longer videos differ systematically in topic and production. The authors explicitly floated the confound that shorter videos may simply be better-planned content. Nothing in this dataset licenses a claim about how long an adult can sustain attention in a **dialogue where they must respond**. Treating "6 minutes" as a cognitive constant is a misreading of the paper by its own standards.

### 2.4 The best-quality duration/fatigue evidence

**Sievertsen, Gino & Piovesan (2016), "Cognitive fatigue influences students' performance on standardized tests", *PNAS* 113(10):2621–2624, PMID 26884183.** Population data: every Danish public school child, 2009/10–2012/13. Results:
- "For every hour later in the day, test performance decreases by 0.9% of an SD (95% CI 0.7–1.0%)."
- "**A 20- to 30-minute break improves average test performance by 1.7% of an SD (95% CI 1.2–2.2%).**"

A 20–30 minute break buys back roughly *two hours* of accumulated decline. This is the cleanest large-N evidence that (a) within-day cognitive fatigue is real and measurable, (b) breaks partially reverse it, and (c) **the magnitude is small** — ~1% of an SD per hour. Not a cliff. This is the number a session-length recommendation should be built on, not the 10-minute myth.

**Honest assessment of "optimal session length":** there is **no randomised trial of tutoring session duration** that I could locate. Any recommendation is triangulation from: fatigue slope (small but real, hours-scale), within-session diminishing returns (§5, strong), break benefits (small, §3), and adherence considerations (§7). Confidence: **low-moderate**, and the recommendation should be framed as a default the learner can override, not a rule.

---

## 3. Breaks, and what should happen in them

### 3.1 Wakeful rest — real, but smaller than the popular account, and weakest for exactly Seba's user

**Dewar, Alber, Butler, Cowan & Della Sala (2012), "Brief wakeful resting boosts new memories over the long term", *Psychological Science* 23(9):955–960, doi:10.1177/0956797612441220, PMID 22829465.** Participants heard two stories; one followed by 10 minutes of quiet wakeful rest (eyes closed, dim room), one by a 10-minute distraction (spot-the-difference task). Rest improved retention, and the advantage persisted at a 7-day delay. This is the canonical finding.

**Meta-analysis 1 — Weng, Yu, Lv, Yang, Jülich & Lei (2025), *Psychonomic Bulletin & Review*, PMID 40087245.** 37 studies, 63 experiments, 82 comparisons. **Hedges's g = 0.448 (95% CI [0.339, 0.557], p < .001)**; still g = 0.270 (p = .031) after a week. Moderators: **older adults benefit more than younger**; **recall shows the effect more than recognition**; and critically, **rest duration did not moderate the effect** — nor did eyes open/closed, lighting, or posture. (If duration doesn't matter, the mechanism is likely "absence of interference" rather than "amount of replay time" — which changes the practical advice from "rest for N minutes" to "don't immediately load in something else".)

**Meta-analysis 2 — Parra, Zhang & Radvansky (2026), "Should we all just take 10?", *Psychonomic Bulletin & Review*, PMID 41540313.** 51 studies, 142 effect sizes. Larger effects for **patient populations** than healthy adults, and "**weaker effects for younger than older adults**."

**Ecologically-valid null — Seban, Šikl, Prošek & Urban (2026), "Wakeful Rest and Memory Consolidation in Educational Settings", *Psychological Research*, PMID 41746415.** n = 161 university students, expository text (not word lists / stories), four 8-minute post-reading conditions: wakeful rest, social media, a maths task, or an interference text. Result: significant decline from immediate to delayed test in *all* groups, and "**wakeful rest condition did not yield consistent benefits relative to the distractor conditions**."

**Honest assessment.** The effect is real in the aggregate (two independent meta-analyses, g ≈ 0.3–0.45) but it is **largest for older adults and clinical populations, smaller for healthy young adults, and does not reliably appear with realistic educational material.** Seba's learner is a healthy adult studying expository material — i.e. the condition where the effect is weakest and has a published null. It is worth a *free* nudge, not a session-structure commitment. Note also that King & Nicosia (2022, *Frontiers in Psychology*, PMID 36389509) did replicate it online against distractor tasks, so the picture is mixed rather than debunked.

### 3.2 Micro-offline gains — contested, motor-specific, do not encode

**Bönstrup, Iturrate, Thompson, Cruciani, Censor & Cohen (2019), "A rapid form of offline consolidation in skill learning", *Current Biology*, PMCID PMC6482074.** MEG during a finger-sequence task: performance improvements occurred **during the ~10-second rest intervals between practice bouts**, not during practice, and accounted for most of early procedural learning; frontoparietal beta-band activity predicted the size of the gain. Supporting mechanism: **Sjøgård et al. (2025), "Hippocampal ripples predict motor learning during brief rest breaks in humans", *Nature Communications* 16:6089, PMID 40603846** (intracranial recordings, 17 patients); and **Mylonas et al. (2024), *J. Neuroscience* 44(14), PMID 38351000** — amnesic patients with hippocampal damage fail to retain gains over breaks.

**But the effect is now seriously challenged:**
- **Das et al. (2025), "Micro-offline gains do not reflect offline learning during early motor skill acquisition in humans", *PNAS* 122(44):e2509233122, PMID 41150724.** Five experiments: micro-offline gains are "transient performance benefits", not consolidation; the gains "vanished within seconds after training" once conditions were equated. Attributed to within-practice performance slowing (reactive inhibition) plus motor-planning effects.
- **Ahmed et al. (2026), *J. Neurophysiology* 136(2):625–632, PMID 42461591** — including motor preparation time in the metric "flipped MOGs from positive to negative."
- **Ahmed et al. (2025), *Scientific Reports* 15:37396** — replacing rest periods with an engaging task produced **no significant group differences** (Bayesian), which is hard to reconcile with a replay account.

**No declarative analogue at the seconds-to-tens-of-seconds scale exists.** The nearest declarative work is minutes-scale wakeful rest (§3.1) and Costa Dias & Peigneux (2026, *Clocks & Sleep*, PMID 42029563), who find that "transient interruption of input during a declarative learning session may favor memory consolidation at wake, partially independently of the attentional state" — suggestive, single study.

**Implication.** Do **not** encode "pause 10–20 seconds after each item so the brain consolidates". That is a motor-learning finding, in dispute in its home field, with no declarative equivalent.

### 3.3 What a break should contain

Converging from §3.1 and Sievertsen: the defensible content of a break is **low-interference and non-verbal** — no new learning, no reading, no social media (which was one of the *distractor* conditions in Seban et al.), no switching to another study topic. Walking, staring out of a window, or quiet sitting. The evidence that this specifically beats other break activities for a healthy adult is weak; the evidence that *taking* a break helps after ~an hour is better (Sievertsen).

---

## 4. Where to put hard material

**Direct evidence on easy→hard vs hard→easy ordering within a session is essentially absent.** Searches across OpenAlex and Europe PMC for problem-difficulty ordering returned nothing on point; the adjacent literature (interleaving, blocked vs mixed, faded worked examples) is curriculum-sequencing territory, covered in another round. Anyone claiming a settled answer on "easy first to build confidence" vs "hard first while fresh" is going beyond the data.

**The strongest relevant finding reframes the question.** The evidence is not about difficulty *order* but about **struggle before explanation**:

**Sinha & Kapur (2021), "When Problem Solving Followed by Instruction Works: Evidence for Productive Failure", *Review of Educational Research*, doi:10.3102/00346543211019105** (~190 citations). Meta-analysis: 53 studies, 166 comparisons of problem-solving-before-instruction (PS-I) vs instruction-before-problem-solving (I-PS). **g = 0.36 (95% CI [0.20, 0.51])** favouring PS-I. With high fidelity to Productive Failure principles, **g = 0.37–0.58**. Corrected for publication bias, the estimate rose to 0.87 (treat that number with caution — bias corrections are unstable). Moderators: the advantage held for **older students** and **domain-specific** outcomes; it **reversed** for grades 2–5 and for domain-general skills. Seba's learner (adult, domain-specific content: probability, Italian) is squarely in the favourable cell.

**Warm-up:** I found no usable cognitive warm-up literature for declarative learning (the hits are motor/surgical simulation, e.g. Gkekas et al. 2026, *Frontiers in Surgery*, PMID 42199894 — significant improvement from warm-up to first exercise, but that's a motor skill). The *spaced review block at the start of a Seba session already functions as a warm-up* — it is retrieval on familiar material, which is exactly the low-risk activation the warm-up intuition wants, and it has independent justification.

**Fatigue argument for early placement:** Sievertsen's ~0.9%-SD-per-hour decline and Risko's time-on-task retention decline both argue that the most cognitively demanding element should be **early**, not saved for the end. There is no counterevidence favouring late placement of hard material.

**Net for Seba:** review (warm-up, cheap) → **hard, unscaffolded attempt at the new concept before the explanation** (PS-I, g≈0.36–0.58) → explanation → practice. Note this is a genuine change from "teach then practise": the productive-failure evidence says the learner should hit the hard thing *before* being taught it, not after.

---

## 5. Spacing within a session — is re-touching material later in the same session wasted?

The brief's premise ("don't re-quiz an item successfully retrieved earlier in the same session") is **half right**, and the half that's wrong matters.

**Repeated retrieval within a session is not wasted — massed repetition is.** *Karpicke & Roediger (2008), "The critical importance of retrieval for learning", *Science* 319:966–968, doi:10.1126/science.1152408* (~1,800 citations). Students learned Swahili–English pairs; after an item was first recalled correctly it was either dropped from further study, dropped from further testing, both, or neither. Result: "**repeated studying after learning had no effect on delayed recall, but repeated testing had a large positive effect**" at one week. Crucially, the repetitions were *spaced within the session* — the list cycled, so each re-test came many items later. So: continuing to retrieve an already-correct item, at a lag of several minutes, still pays. Immediately re-asking it does not.

**But the returns fall off fast, and cross-session beats within-session for the same budget.**
- **Rawson & Dunlosky (2011), "Optimizing schedules of retrieval practice for durable and efficient learning: How much is enough?", *JEP: General*, doi:10.1037/a0023956** — 533 participants, >100,000 responses; items practised to 1–4 correct recalls in the initial session and 1–5 relearning sessions. Additional *within-session* correct recalls showed clear **diminishing returns for durability**; **relearning across sessions substantially improved 1–4 month retention "with relatively minimal cost in terms of additional practice trials."** The practical prescription that came out of this line: roughly **3 correct recalls in a session, then space the relearning**.
- **Schuchard, Rawson & Middleton (2020), *Cognition*, PMID 32044615** (naming treatment in aphasia): "later naming success was superior when the same number of correct retrievals of an item was distributed across multiple sessions rather than administered within one session," with a 7-day inter-session interval numerically better than 1 day at one month. **Same retrieval budget, better outcome, purely from distributing across sessions.**
- **Rohrer & Taylor (2006), "The effects of overlearning and distributed practise on the retention of mathematics knowledge", *Applied Cognitive Psychology*, doi:10.1002/acp.1266** (~260 citations). 216 students. Distributed practice showed no advantage at 1 week but a substantial advantage at 4 weeks. **Overlearning — extra practice problems beyond initial mastery within a session — produced no measurable improvement at either delay.** This is the single cleanest "extra within-session time stops paying" result.
- **Pyc, Balota, McDermott, Tully & Roediger (2014), "Between-list lag effects in recall depend on retention interval", *Memory & Cognition*, PMID 24643791** — short (within-session) lag benefits **diminished at a 1-day retention test but re-emerged at 1 week**. So within-session spacing is not worthless; its value depends on how far out you're measuring, and it grows with retention interval.

**Synthesis.** Within a session: (1) never re-ask an item immediately after a correct retrieval — that's the massed condition, worth ~nothing; (2) one re-touch much later in the session is cheap and mildly positive, especially for long-run retention (Pyc); (3) beyond ~2–3 correct retrievals in a single session the marginal value approaches zero (Rawson & Dunlosky; Rohrer & Taylor) and that time is strictly better spent on a different item or on ending the session; (4) the retrieval budget should be spread across sessions rather than deepened within one (Schuchard). Evidence quality here: **good** — multiple labs, large N, converging.

---

## 6. Where retrieval practice belongs in the session

Three positions, three distinct effects, and they are not in competition — the evidence supports doing all three.

### Front — pretesting / prequestions
**St Hilaire, Chan & Ahn (2024), preregistered meta-analysis, *Psychonomic Bulletin & Review*, PMID 37640836.** Prequestions before study: **g = 0.54 (k = 97) for the pretested material**, but **g = 0.04 (k = 91) for non-pretested material in the same lesson.** The pretesting effect is real and moderate but **narrowly targeted — it does not spread to material you didn't pre-ask about.** Supporting: Kliegl & Bäuml (2024, *Psychological Research*, PMID 39532710) found interpolated pretesting enhanced 24-hour cumulative recall across prose; Sana & Carpenter (2023, *PB&R*, PMID 37002447) found whether benefits generalise depends on the *placement* of pretested vs non-pretested information (an "attentional window" account). Caution: **Motz et al. (2025) ManyClasses, n = 1,571 across 30 classrooms** found the average benefit replicates in the field but that prequestions **caused disengagement in some students** — likely the ones who found being asked things they couldn't answer aversive. Also Pan & Rivers (2023, *Memory & Cognition*, PMID 36637644): learners are **unaware** pretesting helps them, so it will feel pointless to the learner and needs framing.

### Throughout — interpolated testing (the strongest within-session position finding)
**Szpunar, Khan & Schacter (2013), "Interpolated memory tests reduce mind wandering and improve learning of online lectures", *PNAS* 110(16):6313–6317, PMID 23576743, PMCID PMC3631699.** Design: a 21-minute statistics lecture in four ~5.5-minute segments. Experiment 2 (n = 48), tested vs restudy vs non-tested:

| Measure | Tested | Restudy | Non-tested |
|---|---|---|---|
| Mind wandering (% of probes) | **19%** | 39% | 41% |
| Slides with additional notes | **24%** | 9% | 7% |
| Final segment performance | **89%** | 65% | 70% |
| **Cumulative test (all segments)** | **90%** | 76% | 68% |

Plus significantly **lower anxiety about the final test** and **lower subjective cognitive demand** in the tested group. Experiment 1 (n = 32) showed the same pattern (84% vs 59% on the final segment; notes 17% vs 6%).

Two things make this the most directly applicable result in this whole round. First, the benefit is not just mnemonic — testing at segment boundaries **halved mind wandering and improved performance on the segment that came after it**, i.e. it protects the rest of the session. Second, the restudy control rules out "extra exposure": restudy got most of the mind-wandering problem and little of the benefit. Follow-up: **Jing, Szpunar & Schacter (2016), *JEP: Applied*, PMID 27295464** — interpolated testing improved *integration* of information, and mind wandering was more damaging in the restudy condition; lecture-related thought positively predicted final performance. Pan et al. (2026, preprint) found interpolated prequestioning during video lectures raised on-task thought, with mediation analyses attributing test-score gains to focused attention.

### End — post-test / recap
Well supported in general (the testing effect), but there is **no evidence I could find that end-position is special**. Given §1 (no automatic recency protection at day-scale delays), an end recap earns its keep only if it is *retrieval* ("what were the three conditions for independence?") rather than *restatement* by the tutor — restatement is the restudy condition, which underperformed in Szpunar.

**Net:** front (targeted pretest on the specific new concept only), throughout (retrieve at each conceptual boundary, ~every 4–6 minutes of exposition), end (retrieval-based recap, not tutor restatement).

---

## 7. Session end, closure, and whether the learner comes back

This section matters disproportionately for Seba because the learner is **voluntary and self-initiating**. A session that teaches slightly less but produces a return next Tuesday beats a session that teaches more and produces a lapse.

**Peak-end rule (Kahneman, Fredrickson, Schreiber & Redelmeier 1993; Redelmeier & Kahneman 1996).** Retrospective evaluation of an affective episode is approximately the average of its peak and its end, with **duration neglect** — total length has little effect on remembered quality. Well replicated for affective episodes; boundary conditions and moderators are still debated (Li & Lapate, 2024, *Emotion*, PMID 38330325, find the end-bias grows with episode duration and correlates with temporal-memory error).

**Directly in a learning app:** **Xie & Li (2026), "The Peak-End Rule and Retrospective Emotional Valence in Digital Learning Tasks: Evidence from a Word-Learning App", *Behavioral Sciences*, PMID 42193656.** Two vocabulary-learning experiments. Study 1: **task duration had no significant effect** on retrospective valence (duration neglect, in a study app). Study 2, 2×2 optimising peak and end moments: **both peak and end optimisation improved retrospective emotional valence, with a significant non-additive interaction** (doing both beats either alone, but sub-additively). This is the closest existing analogue to Seba.

**The best evidence that end-slope predicts voluntary return comes from exercise:** **Zenko, Ekkekakis & Ariely (2016), "Can you have your vigorous exercise and enjoy it too? Ramping intensity down increases postexercise, remembered, and forecasted pleasure", *Journal of Sport & Exercise Psychology*, PMID 27390185.** Cycling with **decreasing** intensity produced better post-exercise affect than the identical work done with increasing intensity, and the **slope of pleasure accounted for 35–46% of the variance in remembered and forecasted pleasure from 15 minutes to 7 days post-exercise.** Replicated in resistance training: **Hutchinson, Zenko, Santich & Dalton (2020), *JSEP*, PMID 32150721** — decreasing-load protocol produced an increasing pleasure slope and significantly greater remembered pleasure and enjoyment. *Forecasted* pleasure is the standard proximal predictor of intention to repeat a voluntary behaviour.

**Honest assessment.** No study directly shows that ending a *tutoring* session on success raises return rates. The inference chain is: peak-end operates in a learning app (Xie & Li, direct but small and new) + ending-slope drives remembered and forecasted pleasure in a comparable voluntary effortful activity (Zenko, good design, moderate N) → ending on success should raise the probability of the next session. Confidence: **moderate for adherence, near-zero for direct learning gain.** It is also close to free to implement, which is what makes it worth doing.

**A second, weaker argument for a calm ending:** in the wakeful-rest paradigm, the *distraction* condition is "immediately do something demanding". Ending a session by launching into new material or switching straight to another cognitive task is structurally the interference condition. Ending with retrieval-based recap and then stopping is at worst neutral.

---

## 8. Sleep and time of day

**Learning before sleep.** **Spiller & Gilmore (2023), *Royal Society Open Science*, PMID 37771973** — complex multiplication learned before bed vs in the morning, recall ~10.5 hours later: **d = 0.51 (n = 37)** and **d = 0.33 (n = 70)** favouring pre-sleep learning. Small samples, effect shrank in the larger one. **Washington, Arnett, Myers & Mozeiko (2026), *AJSLP*, PMID 41637250** (aphasia, word learning): significant training-schedule × test-timing interaction — **evening-trained words showed stable retention at 24 h while morning-trained words declined significantly.** Mechanism (sleep-dependent consolidation, spindles tracking pre-sleep learning circuits: Thom & Staresina 2025, *Sleep*, PMID 40289550) is well established even where the behavioural effect sizes in naturalistic settings are modest. **No meta-analysis pooling pre-sleep learning specifically** turned up.

**Time of day / chronotype.** **May, Hasher & Healey (2023), "For Whom (and When) the Time Bell Tolls: Chronotypes and the Synchrony Effect", *Perspectives on Psychological Science*, PMID 37369064** — optimal performance when task timing aligns with the individual's circadian arousal peak, most pronounced for effortful, inhibition-demanding tasks. **Chauhan et al. (2025), systematic review, *Chronobiology International*, PMID 40293205**: in adults 18–45, **>80% of studies showed no main effect of chronotype on cognition**; **45% showed synchrony effects** (attention, inhibition, memory); synchrony effects were much stronger in older adults (83% of studies). So for a working-age adult, the effect is **inconsistent and individual**.

Note that Sievertsen's per-hour decline is *not* a circadian finding — it confounds time of day with accumulated cognitive load since waking, and the authors interpret it as fatigue.

**Honest assessment.** Defensible: (a) a session shortly before sleep is at worst neutral and plausibly slightly better for overnight retention of new declarative material (d ≈ 0.3–0.5, small studies); (b) avoid scheduling demanding new-concept work at the end of a long working day if it can be avoided (fatigue, not circadian); (c) alignment with the *individual's* peak is more defensible than any universal "study in the morning". Overstated and to be avoided: universal time-of-day prescriptions, chronotype-based advice presented as strong, and any claim that studying at the "wrong" time wastes the session.

---

## 9. Fatigue and total-time effects — when does extra time stop paying?

Three independent lines converge on **strong within-session diminishing returns**:

1. **Overlearning null** — Rohrer & Taylor (2006): extra practice problems beyond mastery in a single session produced **no** benefit at 1 or 4 weeks, while distributing the same practice did. (§5)
2. **Retrieval-count diminishing returns** — Rawson & Dunlosky (2011): beyond ~3 correct recalls in a session, durability gains flatten; cross-session relearning gives large gains at minimal trial cost. (§5)
3. **Measurable fatigue** — Sievertsen et al. (2016): −0.9% SD per hour; a 20–30 min break recovers +1.7% SD. Plus Risko et al. (2013): retention of lecture material declines with time on task.

There is no evidence for a sharp cliff. The picture is a slow decline in performance plus a fast decline in the *marginal* value of additional repetition on already-learned material. The dominant term is (2) — the reason to stop is usually that there is nothing left worth repeating today, not that the learner has burned out.

**Implication:** the binding constraint on session length is **content, not stamina**. Once the new concept has been retrieved successfully ~2–3 times and the review queue is empty, additional minutes are near-worthless for retention. A tutor should be willing to end at 25 minutes.

---

## 10. Zeigarnik effect / deliberate incompleteness

**Historical status: not replicable as a memory effect.** **MacLeod (2020), "Zeigarnik and von Restorff: The memory effects and the stories behind them", *Memory & Cognition*, PMID 32291585** — the Zeigarnik effect originated in a 1927 dissertation; MacLeod's assessment is that "the memory advantage could not be reliably replicated."

**What the modern evidence does support:**
- **Ghibellini & Meier (2025), *Quarterly Journal of Experimental Psychology*, PMID 39075804** — n > 1,000: more *unsolved* anagrams recalled than solved ones, but **only for individuals high in hope of success**. The authors attribute it to a discrepancy/expectation-violation experience rather than persisting tension.
- **Ongchoco, Wong & Scholl (2026), *JEP: General*, PMID 41490391** — a *perceptual* Zeigarnik effect (unfinished maze paths reproduced more precisely). Real, but a very different construct from "leave the lesson unfinished".
- **Wendsche, Weigelt & Syrek (2026), meta-analysis, *Anxiety, Stress and Coping*, PMID 41554526** — k = 17, N = 2,473: unfinished work tasks predict work-related thoughts during off-job time (between-person ρ = .382, within-person ρ = .247), **strongest for rumination**. That is: incompleteness reliably produces continued thinking, and the flavour of that thinking is closer to rumination than to eager anticipation.
- **Fechner et al. (2024), *Sleep Advances*, PMID 39758352** — active (uncompleted) intentions bias dream content; completed tasks show lower semantic similarity.

**Honest assessment.** The memory claim is **not supported**. The continued-thought claim is supported but is affect-negative (rumination), and it **directly conflicts with the peak-end evidence in §7**, which is better designed and more relevant. For a voluntary learner, ending mid-struggle risks exactly the negative end-affect that predicts non-return.

**Recommendation:** do **not** deliberately end a session on an unresolved difficulty. The safe version that keeps whatever value exists here is: **resolve the difficulty, end on a successful retrieval, and then name the next open question as a one-line preview** ("next time: why this breaks when the events aren't independent"). That is a curiosity hook, not an incompleteness manipulation, and it does not put the negative moment at the end. Confidence: **low** — this is a design compromise between two literatures, not a tested intervention.

---

# TIMING MAP

Session shape, in order, with the evidence backing each placement. Times assume a ~40-minute default.

| # | Slot | Minutes | Activity | Evidence for this placement | Confidence |
|---|---|---|---|---|---|
| 1 | **Open** | 0–2 | One-line orientation + what's on today | None (housekeeping). Keep it short — no evidence that framing pays, and it costs the freshest minutes. | — |
| 2 | **Spaced review** | 2–10 | Retrieval on due items from previous sessions | Testing effect; doubles as warm-up on low-risk familiar material. Cross-session retrieval is where the durability comes from (Rawson & Dunlosky 2011; Schuchard et al. 2020). Early placement is a scheduling convenience, not an evidenced requirement. | High for doing it; low for *where* |
| 3 | **Pretest / hard attempt on the new concept** | 10–16 | Ask the learner to attempt the new idea *before* explaining it — a prequestion, or a genuine problem they can't yet solve | **Sinha & Kapur 2021**: PS-I vs I-PS, g = 0.36 (0.20–0.51), up to 0.58 at high fidelity, favourable for adults + domain-specific content. **St Hilaire et al. 2024**: prequestions g = 0.54 for pretested material. Early because it is the most demanding element and fatigue accumulates (Sievertsen 2016). | **Moderate-high** |
| 4 | **Teach the new concept, in segments** | 16–28 | Exposition broken into ~4–6 minute conceptual chunks | **Szpunar et al. 2013** used 5.5-min segments; segmenting is what enables slot 5. Bunce et al. 2010: activity resets attention lapses. | Moderate |
| 5 | **Retrieval at every segment boundary** | interleaved | A question at each chunk boundary — not a summary from the tutor | **Szpunar et al. 2013**: mind wandering 19% vs 39%/41%; cumulative test 90% vs 76%/68%; lower anxiety and lower perceived load. Restudy control rules out mere re-exposure. **The single strongest within-session position finding.** | **High** |
| 6 | **Practice** | 28–36 | Applied problems on the new concept; stop at ~2–3 successful retrievals per item | **Rohrer & Taylor 2006**: overlearning past mastery = zero benefit at 1 and 4 weeks. **Rawson & Dunlosky 2011**: diminishing returns past ~3 correct recalls. | **High** |
| 7 | **Retrieval-based recap** | 36–39 | Learner reconstructs the key points; tutor does not restate them | Testing effect; §1 shows the end position confers no automatic memory advantage, so the recap must *be* retrieval to earn its slot. | Moderate |
| 8 | **End on success + preview** | 39–40 | Finish with something the learner gets right; one-line hook for next time; explicitly *don't* end mid-failure | **Zenko et al. 2016**: pleasure slope explains 35–46% of variance in remembered/forecasted pleasure to 7 days. **Xie & Li 2026**: peak and end optimisation improve retrospective valence in a word-learning app. Contra-Zeigarnik (§10). | Moderate for **adherence**; near-zero for learning |
| — | **After** | post | Suggest not immediately switching to demanding cognitive work; a genuine break if a second session follows | **Weng et al. 2025** meta g = 0.448 (duration didn't moderate → it's about *absence of interference*, not rest length). Tempered by **Parra et al. 2026** (weaker for young healthy adults) and **Seban et al. 2026** (null with expository text in students). | **Low-moderate** |

### Recommended session length: 25–45 minutes of active work; hard stop suggestion at ~60

Reasoning, explicitly:
- **No RCT of tutoring session duration exists.** Any number is triangulated, and should be a soft default the learner can override.
- **Lower bound (~25 min)** is set by content, not attention: review queue + one new concept + enough practice to hit 2–3 successful retrievals. Ending at 25 minutes when that's done is *correct*, not lazy — Rohrer & Taylor and Rawson & Dunlosky both say the marginal minute after that is worth ~nothing for retention.
- **Upper bound (~45–60 min)** is set by (a) the fatigue slope, which is real but shallow — ~0.9% of an SD per hour (Sievertsen) — and (b) the fact that by then the learner has exhausted the material worth retrieving today. Past ~60 minutes, insert a real 20–30 min break (worth +1.7% SD, Sievertsen) or, better, end and make it a separate session (Schuchard et al.: same retrieval budget spread across sessions beats concentrating it).
- **What does *not* justify a limit:** the 10–15 minute attention span (§2.1) and the 6-minute MOOC video figure (§2.3). Neither survives, and the second is a measure of page-navigation in a non-interactive medium.
- **Interaction density matters more than duration.** Bunce et al. and Szpunar et al. both point the same way: attention is maintained by requiring output, not by keeping the clock short. A 45-minute session with a question every 4 minutes is better supported than a 20-minute monologue.

---

# NUMBERED RECOMMENDATIONS

Ordered by expected effect size × confidence.

1. **Ask a question at every conceptual boundary, not just at the end.** Roughly every 4–6 minutes of exposition. Szpunar et al. (2013): cumulative test 90% vs 68% untested and 76% restudy; mind wandering halved; *and* lower anxiety and lower perceived cognitive load. This is the highest-value within-session timing change available and the effect protects the segments that follow, not just the one tested. Critically, the questions must be **retrieval by the learner**, not recapitulation by the tutor — the restudy control captured very little of the benefit.

2. **Make the learner attempt the new concept before explaining it.** Sinha & Kapur (2021), g = 0.36 (95% CI 0.20–0.51), rising to 0.37–0.58 at high implementation fidelity, and *stronger* for older learners and domain-specific outcomes — Seba's exact case. This is a real change from teach-then-practise: the struggle goes first. Combine with a targeted prequestion (St Hilaire et al. 2024, g = 0.54 on pretested material). Two implementation constraints: the benefit **does not spread** to material you didn't pre-ask about (g = 0.04), so pre-ask about the actual target concept; and ManyClasses (Motz et al. 2025) found prequestions disengage some students, so frame the failure explicitly as expected and useful.

3. **Cap within-session repetition at ~2–3 successful retrievals per item, then stop.** Rohrer & Taylor (2006): overlearning beyond mastery gave zero benefit at 1 *and* 4 weeks. Rawson & Dunlosky (2011): durability gains flatten past ~3 correct recalls; cross-session relearning gives far more per trial. Schuchard et al. (2020): the *same* number of correct retrievals distributed across sessions beat concentrating them in one. Practical rule: once an item is right twice, hand it to the scheduler, not to more practice today.

4. **Never re-ask an item immediately after a correct retrieval; a re-touch much later in the session is fine and mildly useful.** The brief's premise needs this correction — Karpicke & Roediger (2008) found repeated *testing* after first correct recall had a large 1-week effect (repeated *studying* had none), with repetitions spaced across a cycling list. Pyc et al. (2014) show short-lag benefits are muted at 1 day but re-emerge at 1 week. So: massed = wasted, spaced-within-session = cheap and positive, but see #3 for the ceiling.

5. **End on a successful retrieval, and never end mid-failure.** Zenko et al. (2016): the affective slope over an episode explains 35–46% of variance in remembered and forecasted pleasure up to 7 days later; Xie & Li (2026) show peak-and-end optimisation raises retrospective valence in an actual word-learning app. This buys **adherence, not learning** — which for a voluntary self-directed learner is the higher-leverage variable. Cost: near zero.

6. **Put the most cognitively demanding element early.** Fatigue is real but shallow (−0.9% SD/hour, Sievertsen et al. 2016) and lecture retention declines with time on task (Risko et al. 2013). No evidence supports saving hard material for later. Conveniently, this coincides with #2.

7. **Let the session end when the content is done, even at 25 minutes.** The binding constraint is material, not stamina (#3). A tutor prompt that pads to fill a nominal 45 minutes is spending the learner's time on the flat part of the curve — and worse, spending it on the part of the session where fatigue is highest and the affective end-slope is going the wrong way.

8. **After ~60 minutes, take a real break or stop.** A 20–30 minute break is worth ~+1.7% SD (Sievertsen), roughly two hours of decline. But splitting into two sessions on different days beats one long session plus break (Schuchard et al.), so prefer stopping.

9. **Suggest not switching straight into demanding cognitive work afterwards.** Weng et al. (2025) meta: g = 0.448, with rest *duration* not a moderator — implying the mechanism is absence of interference, not amount of rest. Frame as "don't immediately start something else", not "meditate for 10 minutes". Flag honestly as low-confidence for this user: Parra et al. (2026) find the effect weaker for young healthy adults, and Seban et al. (2026, n = 161, expository text) found **no** consistent benefit in an educational setting.

10. **A session shortly before sleep is a mild positive; anything stronger about timing is overreach.** Spiller & Gilmore (2023): d = 0.51 and d = 0.33 in two samples. Washington et al. (2026): evening-trained material stable at 24 h, morning-trained declined. Worth mentioning once to the learner; not worth building scheduling logic around.

11. **Prefer alignment with the learner's own peak over any universal time-of-day rule.** Chauhan et al. (2025): >80% of studies find no main chronotype effect in adults 18–45; synchrony effects appear in 45% and are much stronger in older adults. If Seba ever asks about timing, ask when *this* learner feels sharpest, and don't imply an off-peak session is wasted.

---

## DO NOT ENCODE — popular claims that do not survive

| Claim | Verdict |
|---|---|
| **"Attention drops after 10–15 minutes."** | **Debunked.** Wilson & Korn (2007): the evidence base "provides little support". Bradbury (2016): "the most often cited source for a rapid decline in student attention during a lecture barely discusses student attention at all"; the primary data do not support a 10–15 min limit; institutions changed policy on a citation chain with nothing at the root. Bradbury's actual finding: the biggest source of variance is the *teacher*, not the format. |
| **"Keep it under 6 minutes — MOOC data proves it."** | **Misread.** Guo et al. (2014) measured *when people navigate away from a video page* in a zero-interaction, zero-accountability medium, in a retrospective non-experimental study of four Fall-2012 math/science courses, using a proxy the authors themselves say "cannot capture whether a watcher is actively paying attention". It says nothing about a dialogue where the learner must respond. |
| **"Primacy/recency: teach new material at the start and end, practise in the middle" (Sousa's prime-time 1/2).** | **Unsupported extrapolation.** No primary study of recall by position within a lesson was found. The list-learning recency component is abolished by ~30 s of filled delay (Glanzer & Cunitz) — it cannot survive to a next-day test. The documented within-lecture pattern is monotonic decline, not a U. |
| **"Pause briefly after each item so the brain consolidates" (micro-offline gains).** | **Contested and misapplied.** Bönstrup et al. (2019) is motor sequence learning; Das et al. (2025, *PNAS*, 5 experiments) conclude micro-offline gains "do not reflect offline learning" and are transient performance effects; Ahmed et al. (2026) show the sign flips when motor preparation time is included; Ahmed et al. (2025) found no difference when rests were filled with an engaging task. **No declarative analogue at this timescale exists.** |
| **"End the session mid-task — the Zeigarnik effect will make them come back."** | **Not supported, and probably counterproductive.** MacLeod (2020): the memory advantage "could not be reliably replicated"; Ghibellini & Meier (2025) find it only in high-hope-of-success individuals and attribute it to expectation violation. Wendsche et al. (2026) meta: unfinished tasks reliably produce continued thought, and it is **rumination**. Conflicts with the better-supported peak-end evidence (#5). Use a resolved ending plus a one-line preview instead. |
| **"Everyone should study in the morning / at their chronotype peak or the session is wasted."** | **Overstated.** >80% of studies find no main chronotype effect in adults 18–45 (Chauhan et al. 2025). Synchrony effects are real but inconsistent at this age and strongest in older adults. Sievertsen's time-of-day decline is fatigue since waking, not circadian. |
| **"Take 10 minutes of quiet rest after learning — it's a big memory boost."** | **Overstated for this user.** Real in aggregate (g ≈ 0.45, Weng et al. 2025) but weakest for healthy young adults (Parra et al. 2026) and null with realistic expository material in students (Seban et al. 2026). Rest duration doesn't moderate the effect, so "rest for 10 minutes" is the wrong framing — "don't immediately load in interfering material" is the right one. |

---

### Sourcing note
The session's WebSearch quota was exhausted by earlier rounds, so sources here were located and retrieved via the Europe PMC REST API, the OpenAlex API, Semantic Scholar's Graph API, Unpaywall, and direct PDF retrieval, rather than a general web search engine. All quoted passages are from abstracts or full texts retrieved through those routes; the Guo et al. (2014) figures and limitations are quoted from the full-text PDF at https://up.csail.mit.edu/other-pubs/las2014-pguo-engagement.pdf, and the Szpunar et al. (2013) table is from PMC3631699. Bradbury (2016) is quoted from its abstract (the full text is paywalled and returned 403); the specific primary studies he critiques individually were therefore not verified one by one, and that limitation is noted rather than papered over. Two effect sizes are reported as reconstructed from OpenAlex inverted-index abstracts (Karpicke & Roediger 2008; Rohrer & Taylor 2006) — the direction and presence/absence of effects are reliable, but exact percentages from those two were not independently verified and are stated qualitatively above for that reason.
