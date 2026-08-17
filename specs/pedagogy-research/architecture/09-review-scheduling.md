# 09 — Review scheduling: is flashcard-style spaced repetition the right substrate?

Scope: whether FSRS-scheduled minted cards are the right review mechanism for a tutor teaching conceptual (probability) and procedural/linguistic (Italian) material, and how review should be scheduled and formatted.

Sourcing note: several key papers are paywalled (Springer/Nature/ScienceDirect returned 303/403). Where I could only get a search-engine abstract rather than the primary text, it is marked **[abstract only]**. Numbers without that mark come from primary text I fetched.

---

## 1. Does spaced retrieval transfer beyond paired associates?

### 1.1 The core meta-analysis: it transfers, but weakly and conditionally

Pan & Rickard (2018), *Psychological Bulletin* 144(7), 710–756 — 192 transfer effect sizes, 122 experiments, N = 10,382, 40 years of research. <https://pdf.retrievalpractice.org/transfer/Pan_Rickard_2018.pdf> (summary via <https://notes.andymatuschak.org/zC1oBp6yE72b7YHzaJZmjXf>)

- Grand mean transfer effect vs. a **restudy** control: **d = 0.40, 95% CI [0.31, 0.50]**. Compare with the direct (same-question) testing effect, routinely d ≈ 0.5–0.8. Transfer is roughly **half** the size of the retention benefit you get on the exact item you practiced.
- Transfer across **test format only** (cued recall → free recall → MCQ, same content): **d = 0.58**. This is the *easy* kind of transfer, and it is the biggest one they found.
- **Response congruency is the dominant moderator.** When the final test's correct answer overlaps the answer you produced during practice: d = 0.58. When it does not: **d = 0.28**. I.e. once you stop asking for the same response, most of the benefit evaporates.
- **Initial practice accuracy predicts transfer**, +0.0058 d per percentage point of practice accuracy. Critically: *"the transfer effect disappears completely for particularly poor performance."* Retrieval practice on items you're failing does not transfer at all.
- **Elaborated retrieval practice adds d = 0.23** — practice that requires thinking through related information, producing explanations, or higher-order responses, plus elaborative feedback after retrieval.

Read against Seba: the mechanism that carries the *most* weight in this literature (response congruency) is precisely the mechanism that produces inert knowledge. A card that reliably reproduces its own `back` string is buying you the d = 0.58 branch of the tree, not the d = 0.28 one. The d = 0.23 elaboration bonus, by contrast, is the one thing a conversational tutor is structurally better placed to deliver than Anki.

### 1.2 Domain evidence: it works for complex material, but smaller and noisier

- **Mathematics meta-analysis** (Educational Psychology Review, 2025, <https://link.springer.com/article/10.1007/s10648-025-10035-1>) **[abstract only]**: spacing improves mathematics learning but **the effect is smaller in maths than in other domains**; the retrieval-practice effect is *stronger* when content is more complex, when retrieval is more effortful, and when feedback is given.
- **Nine introductory STEM courses, single-paper meta-analyses** (*IJ STEM Education*, 2024, <https://stemeducationjournal.springeropen.com/articles/10.1186/s40594-024-00468-5>) **[abstract only]** — the title itself is *"is the glass half full or half empty?"*: spaced retrieval practice in authentic STEM courses produces real but modest and inconsistent effects on course exams. This is the closest thing to Seba's setting and it is *not* an overwhelming result.
- **Health professions state-of-the-art review** (2025, <https://pmc.ncbi.nlm.nih.gov/articles/PMC12292765/>) — the most directly damaging source for a flashcard-only design:
  - "Some cognitive psychology studies have failed to find *far transfer effects*" where practice and criterion diverge in content or format.
  - Flashcards promote "repeated exposure to discrete facts" while the criterion task demands "deep, applied reasoning" — the review names this as a **format mismatch**, and invokes transfer-appropriate processing: practice should look like the target performance.
  - **"Very few studies … have examined the effects of retrieval practice of any kind on skills learning."** For procedural competence, the evidence base is close to empty.
  - On SRS schedulers specifically: "it is unclear exactly how the algorithms for many of these programs are designed, whether they are designed to maximize learning."

### 1.3 The pro-conceptual case

Matuschak, *Spaced repetition memory systems can be used to develop conceptual understanding* <https://notes.andymatuschak.org/z9Vi7YVx7NzxU2wawNgsJbk> and *How to write good prompts* <https://andymatuschak.org/prompts/>:

- Conceptual prompts (connections, implications, causes, consequences) work, but only if the concept is attacked **from multiple angles**, not as one atomic card — "prompts collectively trace a concept's boundary" rather than memorizing a definition.
- Conceptual information may need **much slower optimal schedules** than factual material.
- The technique for conceptual encoding is "not well or widely understood," and success depends on the learner engaging in authoring.
- Explicitly: **"Creative/application prompts … don't rely on retrieval practice's mechanisms and remain poorly understood."** The most influential practitioner of conceptual SRS says the `apply`/`produce` end of Seba's type system is *outside* the mechanism whose evidence base justifies SRS.

**Net:** spaced retrieval is well-evidenced as a *retention* mechanism, including for complex material. It is weakly evidenced as a *competence* mechanism, and effectively unevidenced for procedural skill. Card-level retention does not license an inference to real competence — the response-congruency finding is direct evidence that much of what a card measures is the card.

---

## 2. FSRS specifically

### 2.1 What it models

DSR model, inherited from MaiMemo's DHP (<https://expertium.github.io/Algorithm.html>, <https://github.com/open-spaced-repetition/awesome-fsrs/wiki/ABC-of-FSRS>):

- **R** — probability of recall now. **S** — days for R to fall 100% → 90%. **D** — 1..10, described in the algorithm's own docs as *"a crude heuristic without precise definition."*
- FSRS-6 uses a **power-law** forgetting curve (parameter w20 controls decay shape); at t = S, R = 90% by construction.
- Success: `S_new = S_old × SInc`, SInc ≥ 1 — **stability can never decrease on a successful review**. SInc rises as D falls, falls as S rises (harder to stabilise already-stable memories), and rises as R falls (**reviewing near the forgetting point is most productive**).
- Lapse: `S_new = w11 × S_old × f(D)`, clamped ≤ S_old.
- Difficulty: `D = w0 + w1 × (4 − G)` initially, then grade-driven: Again adds a lot, Hard a little, Good nothing, Easy subtracts, plus damping and mean reversion.
- ~21 params (FSRS-6) / 35 (FSRS-7), fit by gradient descent on log loss over the user's own history.

### 2.2 Benchmark numbers

<https://github.com/open-spaced-repetition/srs-benchmark>, <https://expertium.github.io/Benchmark.html>. 10,000 Anki collections, ~727M reviews raw; 9,999 collections / **349,923,850 reviews** evaluated excluding same-day reviews (519M with).

| Algorithm | Log loss ↓ | RMSE(bins) ↓ | AUC ↑ | Params |
|---|---|---|---|---|
| RWKV-P (neural, cross-user) | 0.2773 | 0.02502 | 0.8329 | 2,762,884 |
| LSTM | 0.3332 | 0.05378 | 0.7329 | 8,869 |
| GRU | 0.3333 | 0.0556 | 0.7316 | 503 |
| FSRS-7 recency | 0.3414 | 0.0627 | 0.7097 | 35 |
| FSRS-6 | 0.3460 | 0.0653 | 0.7034 | 21 |
| FSRS-4.5 | 0.3624 | 0.0764 | 0.6893 | 17 |

- **FSRS beats Anki's SM-2 on log loss in ~99.6% of collections** — but the benchmark authors themselves note SM-2 "was never designed to predict probabilities," so formulas had to be bolted on for the comparison to exist. Practitioner claim: ~20–30% fewer reviews for equal retention.
- The benchmark maintainers warn explicitly that **AUC can be high while calibration is poor**, and that these metrics measure *prediction*, not *scheduling quality*. **No published experiment shows FSRS produces better learning outcomes than SM-2**; the entire benchmark is a calibration contest on already-collected review logs.
- Note the ceiling: a 2.7M-parameter sequence model gets log loss 0.277 vs FSRS-6's 0.346. Even the best model leaves large irreducible error — recall on a given day is substantially unpredictable.

### 2.3 Where FSRS's assumptions break — and how each breaks for Seba

| FSRS assumption | Status in FSRS | How Seba violates it |
|---|---|---|
| Cards are **independent** memories, each with its own D/S/R | Baked in — "each card has its own DSR values" | Seba mints ~10 cards *about one concept* per session. They are one memory, not ten. Interference and mutual cueing are unmodelled; success on card 3 is partly the residue of card 2 answered a minute earlier. |
| A review is a **discrete retrieval attempt** at a known timestamp | Baked in | In a dialogue the item is discussed, hinted, scaffolded, and re-raised. What is graded is not a clean retrieval attempt. |
| Grades are **honest and consistent** | Anki manual: *"FSRS can adapt to almost any habit, except for one: pressing 'Hard' instead of 'Again' when you forget the information"* → "all intervals will be unreasonably high" (<https://docs.ankiweb.net/deck-options.html>) | The grader is an LLM that just watched the learner struggle and is under conversational pressure to be encouraging. This is *exactly* the failure mode the manual singles out as unrecoverable. |
| Card **content is fixed** | Implicit; no mechanism handles content edits | Fine today (static front/back), but blocks the generated-variant design in §5. |
| **Short-term / same-day** behaviour | Author's own words: neither FSRS-5 nor FSRS-6 "have a proper model of short-term memory," only "crude heuristics" | Every card minted in a session is same-day-new; the first interval is entirely from the 4 initial-stability params. |
| D should depend on R | Acknowledged by the authors as **theoretically flawed** ("~33% MAPE"), kept because it fits | Amplified when the grade is a noisy LLM judgement. |
| Minimum interval | py-fsrs clamps to **1 day** (<https://deepwiki.com/open-spaced-repetition/py-fsrs/5-the-fsrs-algorithm>) | If the learner does two sessions in one day, FSRS has nothing sensible to say about the second. |

py-fsrs implements `desired_retention` default **0.9**, `next_interval = (S / FACTOR) × (DR^(1/DECAY) − 1)`, states Learning/Review/Relearning, max interval 36,500 days, optional fuzz.

---

## 3. Desired retention, and the Cepeda gap

### 3.1 What FSRS optimises

<https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-optimal-retention>, <https://expertium.github.io/Retention.html>, <https://docs.ankiweb.net/deck-options.html>:

- Desired retention = "I will recall this % of cards **when they are due**." Not average knowledge — average retrievability across a collection runs much higher, since most cards aren't due.
- Workload vs. DR is **U-shaped**: high DR → short intervals → many reviews; low DR → much relearning. Anki ≤ 24.02 optimised *maximum knowledge*; **Anki 24.04+ optimises minutes-of-study ÷ knowledge**, i.e. efficiency, not learning.
- Manual: default **0.90**; "above 90% the workload increases very quickly, and above 97% the workload can be overwhelming"; keep below 0.97. Reasonable range quoted as 0.70–0.97.
- Nothing in the theory says 0.90 is pedagogically right. It is a **budget knob**, chosen to minimise workload per unit retained.

### 3.2 The gap/retention-interval finding

Cepeda, Vul, Rohrer, Wixted & Pashler (2008), *Psych Science* 19, 1095–1102. N > 1,350. <https://files.eric.ed.gov/fulltext/ED505660.pdf> / <https://escholarship.org/uc/item/0kp5q19x>

- Optimal inter-study gap as a proportion of the retention interval **declines with RI**: ~20–40% of a 1-week RI, ~10–20% at intermediate RIs, ~5–10% of a 1-year RI.
- The ridgeline is **broad, not sharp** — performance is decent across a wide band around the optimum.

Two consequences for Seba:

1. **The optimum depends on when you need the knowledge, which FSRS never asks.** FSRS optimises workload-per-unit-recall under an implicit infinite horizon. A learner with a probability exam in 6 weeks and a learner doing Italian for life want different schedules from the *same* card. This is a genuine, cheap-to-add input FSRS lacks.
2. Because the ridgeline is broad, **precision in scheduling is worth much less than Seba's design implies**. Lindsey, Shroyer, Pashler & Mozer (2014), *Psych Science* 25(3), 639–647, N = 179 middle-school Spanish students, personalized review beat massed by **16.5%** and one-size-fits-all spacing by **10.0%** on a cumulative post-semester exam (<https://pubmed.ncbi.nlm.nih.gov/24444515/>). Note the split: **spacing at all** is most of the win; personalization adds a real but smaller 10%. FSRS-vs-a-crude-schedule lives in that 10% band; item quality lives in the much larger band.

---

## 4. Item format: what the five types are worth

Evidence hierarchy (Endres et al. 2020, *Instructional Science*, <https://link.springer.com/article/10.1007/s11251-020-09526-1> **[abstract only]**; relational-processing account, *JML* 2019, <https://www.sciencedirect.com/science/article/abs/pii/S0749596X19300026> **[abstract only]**; Karpicke, *Retrieval-Based Learning: A Decade of Progress*, <https://files.eric.ed.gov/fulltext/ED599273.pdf>):

- Cued recall **g ≈ 0.72**, free recall **g ≈ 0.81**. Free recall requires self-initiated organisation and inter-item relational processing; recognition provides the most retrieval support and the least benefit.
- Division of labour: **short answer → better retention of the specifically targeted fact; free recall → better retention of surrounding, non-targeted information** and better relational/organisational learning.
- Karpicke reviews MCQ as having "positive and negative effects" — MCQ can work if it forces retrieval of competitors, but it invites recognition rather than production.
- Pan & Rickard: transfer *across* formats is the strongest transfer category (d = 0.58), so practicing in a harder format than the criterion is a safe bet; practicing in an easier one is not.

Matuschak's prompt criteria (<https://andymatuschak.org/prompts/>) converge on the same ranking and add two design failures Seba is exposed to:

- **Binary/yes-no prompts** "require minimal effort and encourage shallow pattern-matching rather than genuine understanding."
- **Cloze deletions, especially mechanically copied from source text, produce false positives** — you learn what the answer *looks like*. Expertium's note-type essay makes the same argument and recommends randomising cloze position/phrasing to defeat it (anecdotal, no citations: <https://expertium.github.io/Avoid_Pattern_Matching.html>).
- Target ~**90% correct** at review — which is, satisfyingly, the same number as the FSRS default DR.

Mapping onto Seba's five types, best to worst on evidence:

1. `produce` / `apply` — closest to free recall and to the criterion performance; also the elaborated-retrieval condition (+0.23 in Pan & Rickard). **But** these are exactly the "creative/application prompts" Matuschak flags as *not* operating via the retrieval-practice mechanism, and their answers are unbounded, so grading is the weak point.
2. `recall` — cued recall, g ≈ 0.72, the well-evidenced workhorse.
3. `cloze` — cued recall with heavy support; false-positive-prone unless the deletion is semantically load-bearing.
4. `recognize` — the weakest retrieval condition in every source above. Free recall > recognition is one of the most robust findings in the literature, and the only defensible use of recognition is for material where recognition *is* the criterion task (e.g. reading comprehension of Italian, hearing a word in speech). For probability it has no defence.

---

## 5. Generative / open-ended review as an alternative

- **Interleaving, and varied problems, beat blocked fixed items — with the largest effect size in this whole report.** Rohrer, Dedrick, Hartwig & Cheung (2020), *J. Educational Psychology*, preregistered cluster RCT, 54 seventh-grade maths classes, 4 months, unannounced test 1 month later: **interleaved 61% vs blocked 38%, d = 0.83**. Mechanism: interleaving forces *discrimination* — choosing which strategy applies — which blocked practice never trains. <https://api.semanticscholar.org/graph/v1/paper/search?query=interleaved+mathematics+practice+randomized+controlled+trial>
  This effect (d = 0.83) is larger than the transfer effect of testing (d = 0.40) and larger than the FSRS-vs-crude-scheduling margin (~10%). For probability, *the strategy-selection problem is the subject*. A fixed card with a fixed answer trains none of it.
- **Elaborated retrieval** (+d = 0.23, Pan & Rickard) covers self-explanation prompts and post-retrieval elaborative feedback — a dialogue tutor's home turf.
- **Free recall / brain-dump** review is the format that best captures non-targeted and relational information (Endres et al.). No card can do this, because a card by construction targets one thing.
- **Fresh generated variants vs. fixed cards: NO DIRECT EVIDENCE.** I found no study comparing an LLM-generated fresh variant against a fixed item under a spaced schedule. The indirect case is strong (interleaving d = 0.83; response-congruency shows fixed-response practice is what fails to transfer; Matuschak's and Expertium's independent arguments against pattern matching). The counter-case is also real:
  - Matuschak's **consistency** criterion — prompts should "light the same bulbs each time"; varying the item risks inconsistent, incomplete retrievals and makes difficulty uncontrolled.
  - **It breaks FSRS's model.** D and S are estimated for *this card*. Regenerate the item and the D estimate is stale, the observed grade reflects a different item's difficulty, and stability updates are applied to a memory that was never practiced. FSRS has no notion of item drift.
  - The precedent that *does* exist: **Duolingo's half-life regression** (Settles & Meeder, ACL 2016, 13.3M learning events, <https://aclanthology.org/P16-1174.pdf>) schedules at the level of a **lexeme tag**, not a fixed sentence — the same knowledge component recurs in varied sentence contexts, and the memory model is attached to the *component*, not the surface item. This is the correct architecture for varied review, and it is a different data model from one-DSR-per-card.

---

## 6. Mastery learning + spaced review

- Cognitive Tutors mark a skill mastered when the knowledge-tracing posterior crosses ~0.95 and then **stop presenting it** — the same "done and never revisited" policy as Seba's concepts. This is a known weakness: mastery-at-a-moment says nothing about decay, and the ACT-R line of work (Pavlik & Anderson's optimal-scheduling models) exists precisely to graft decay onto mastery. Survey background: *Knowledge Tracing: A Survey* (2022), <https://doi.org/10.1145/3569576>.
- The Lindsey et al. (2014) result above is the clean demonstration that **mastery + personalized spaced review > mastery alone**, in a real semester-long course, at equal time cost.
- Seba's structure is therefore half-right in an interesting way: it has mastery-then-stop for *concepts* and decay-aware scheduling for *cards*. The bug is that these are different objects. The thing FSRS keeps alive is not the thing the tutor decided was mastered.

---

## 7. Who should author the items?

- **Generation effect / learner-authored:** the practitioner literature strongly favours self-authored prompts (Matuschak: conceptual SRS "depends on learners writing their own prompts"), but the controlled evidence is thin and mixed. Teacher-made digital flashcards improve outcomes at low cost (Ingebrigtsen et al., *Applied Cognitive Psychology* 2025, <https://onlinelibrary.wiley.com/doi/10.1002/acp.70086>) **[abstract only]**; premade decks save time but "the quality of premade flashcards cannot be guaranteed." I found **no clean head-to-head** establishing learner-generated > expert-generated for retention.
- **LLM-generated items:** the one empirical study I found — *Enhancing Student Learning with LLM-Generated Retrieval Practice Questions*, arXiv 2507.05629, ~60 students across two data-science courses — reports **89% vs 73%** accuracy in weeks with vs without LLM-generated MCQ practice. <https://arxiv.org/abs/2507.05629>. Crucially, the authors state that **"instructors must still manually verify and revise the generated questions before releasing them to students."** The positive result is for *human-reviewed* LLM output.
- Practitioner benchmark claims of high unusable-card rates for LLM-generated flashcards circulate (e.g. <https://evakeiffenheim.substack.com/p/when-ai-flashcards-pollute-your-anki> claims ~36% unusable in a self-run 2026 benchmark) — **not peer-reviewed, treat as anecdote**, but the described failure mode is precisely the one the design literature predicts: not hallucination, but cards that are "ambiguous, wordy, or context-dependent" — i.e. violations of Matuschak's focused/precise/consistent criteria that only surface weeks later under a spaced schedule.
- Relevant asymmetry: Seba mints items **during** the session, when it has the richest possible context about what the learner actually struggled with. That is a real advantage over both premade decks and out-of-context generation. The offsetting risk is that nothing ever reviews the card afterwards, and a bad card is a debt that comes due for months.

---

## 8. Volume, load, and when to stop

Little peer-reviewed work exists on SRS abandonment; what exists is arithmetic and practitioner guidance.

- Matuschak: prompts are cheap individually ("10–30 seconds across the entire first year"), a first reading should yield **5–10** prompts, and — the load-bearing advice — **"an obsession with completionism will drain your gumption"**; delete prompts you no longer care about.
- Anki manual: the entire desired-retention guidance is framed as workload management; workload rises "very quickly" above 0.90 and can be "overwhelming" above 0.97.

**Seba's arithmetic does not close.** Assume 3 sessions/week.

- Minting: 10 cards/session → **30 new cards/week**, ~1,500/year.
- Review capacity: probability cap is 6 due items/session → **18 reviews/week ≈ 2.6/day**.
- Demand: even at a generous *average* interval of 30 days once mature (and much shorter while young), 30 new cards/week reach ~1 review/card/month, i.e. after 10 weeks ≈ 300 cards ≈ **70 reviews/week** demanded against 18 available.
- The due queue therefore **diverges within roughly 2–4 weeks** of steady use, and stays diverged. From then on the cap, not FSRS, is the scheduler: FSRS's carefully calibrated intervals are being systematically overrun, every card is reviewed late, and the DSR estimates — which assume the review happened at the scheduled R — are being fed increasingly wrong inputs. The algorithm degrades exactly where it is silently most confident.

This is the single most concrete defect in the current design, and it is arithmetic, not opinion. Either the mint rate must fall by roughly 3–5× or the review capacity must rise correspondingly — and the review capacity is bounded by session length, which is bounded by the human.

---

## 9. Interleaving vs. a due-only queue

FSRS assigns intervals per card. Cards minted in the same session share: same concept, same creation date, same initial stability parameters, similar first grades. They therefore come due **together**, and keep coming due together for the first several cycles until fuzz and grade differences disperse them.

The result is that a due-only queue **blocks by topic by accident** — exactly the arrangement Rohrer's RCT shows is worth d = 0.83 to avoid. Anki's `fuzz` exists partly to break this clustering, but it only jitters dates; it does not deliberately interleave across concepts. Nothing in Seba's design counteracts it, and the per-subject cap makes it worse: if 8 probability cards from one session are due and the cap is 6, the session becomes 6 cards about one concept.

Cheap fix: when the due set exceeds the cap, select for **concept diversity** rather than taking the oldest-due first, and order the selected items so no two consecutive items share a concept.

---

## 10. Does the conversational format change anything?

Yes, and this is the strongest empirical support in Seba's favour.

**QuizBot** (Ruan et al., CHI 2019), *A Dialogue-based Adaptive Learning System for Factual Knowledge*, 76 students, two within-subject studies, science / safety / English vocabulary. <https://doi.org/10.1145/3290605.3300587>

- Same sequencing algorithm in both conditions — **the only difference was dialogue vs. flashcard app**.
- QuizBot produced **>20% more correct answers** on recognition and recall.
- It is **slower per item**, but in a free-choice study students voluntarily spent **2.6× longer** learning with it, and strongly preferred it for casual learning.
- Second study: improved learning gains on recall specifically.

Supporting mechanism from Pan & Rickard: elaborated retrieval — thinking through related information, producing explanations, elaborative feedback — is worth **d = 0.23** on top. Dialogue naturally supplies this; a flashcard cannot.

The cost is on the other side of the ledger and is not addressed by QuizBot: dialogue makes the *grade* unreliable (hints leak the answer; the graded event is no longer a clean retrieval attempt), and it makes each item cost more minutes, which tightens the load arithmetic in §8.

---

## 11. Verdicts on Seba's design

**(a) FSRS over fixed cards as the review substrate for conceptual/procedural subjects — PARTIALLY SUPPORTED, with the conceptual half UNSUPPORTED.**
Spacing-at-all is very well supported (Cepeda 2008; Lindsey 2014: +16.5% over massed). FSRS specifically is the best-calibrated cheap predictor available (99.6% of collections beat SM-2 on log loss, 350M reviews) — but calibration is not learning; **no study shows FSRS produces better learning outcomes than any other spaced schedule**, and the benchmark authors say as much. For *procedural* material the review of health-professions education states outright that almost no retrieval-practice-for-skills evidence exists. For *conceptual* material the mechanism works (Pan & Rickard d = 0.40) but at half the strength of same-item retention, collapsing to d = 0.28 once the response changes. The substrate is defensible; the marginal value of FSRS over "space it out roughly right" is small relative to the item-quality and format decisions around it, and the personalization band in Lindsey et al. was 10% while the spacing band was 16.5%.

**(b) LLM-authored items during the session — SUPPORTED, conditionally.**
The one controlled study (arXiv 2507.05629, ~60 students, 89% vs 73%) is positive but explicitly required human review before release. Seba has no review step. In-session authoring gives Seba context no premade deck has, which is a genuine advantage, but the known failure mode is not hallucination — it is cards that are ambiguous, wordy, or context-dependent, which fail silently three weeks later. The verdict is conditional on adding a quality gate and a repair path.

**(c) The 4-grade rubric judged by the LLM — CONTRADICTED (as currently specified).**
The Anki manual names one failure FSRS cannot absorb: pressing *Hard* when you actually forgot, which makes "all intervals unreasonably high." An encouraging conversational tutor grading a learner who needed two hints is a machine purpose-built to commit that error. Compounding it: FSRS's difficulty update is driven entirely by grade, and its own authors call the D formula theoretically flawed (~33% MAPE) even with honest grades. Also unaddressed: a dialogue turn that included a hint is not the retrieval event FSRS thinks it is. Either the grader needs an explicit, hint-aware rubric ("Again if any hint was needed to produce the core answer") or the grade should be reduced to binary correct/incorrect, which FSRS handles honestly through initial-stability params for Again/Good.

**(d) `recognize` as an item type — CONTRADICTED for probability, DEFENSIBLE for Italian.**
Free recall > cued recall > recognition is among the most robust findings in the retrieval literature (free g ≈ 0.81, cued g ≈ 0.72, recognition lowest); Matuschak singles out binary/recognition prompts as low-effort and pattern-matching-prone. The only justification for recognition is transfer-appropriate processing — when recognition *is* the criterion (understanding heard/read Italian). For probability there is no such criterion, and `recognize` should not be minted.

**(e) 10 items/session mint cap and per-subject review caps — CONTRADICTED.**
Not on pedagogy but on arithmetic (§8): 30 new cards/week against 18 review slots/week diverges in 2–4 weeks and never recovers. Once the cap binds, the cap is the scheduler and FSRS's intervals are systematically overrun, silently corrupting the DSR estimates it fits from those same reviews. Matuschak's independent practitioner guidance lands in the same place: 5–10 prompts per *reading*, and delete aggressively. The mint cap should be ~3, and it should be a *budget with a ledger*, not a per-session constant.

**(f) Concepts never revisited once done — only their cards recur — CONTRADICTED.**
This is mastery-at-a-moment with no decay model on the object that actually matters, the same known weakness as Cognitive Tutor mastery criteria, and Lindsey et al. (2014) is the direct demonstration that adding decay-aware review to mastery is worth 16.5%. Worse, the object FSRS keeps alive (a card) is not the object the tutor certified (a concept), and Pan & Rickard's response-congruency result says a card's survival is substantially evidence about the card. A concept whose three cards are all green may still be gone.

**(g) Static front/back rather than generated variants — UNSUPPORTED, and the strongest indirect case runs against it.**
No study directly compares generated variants to fixed cards under a spaced schedule — genuinely NO EVIDENCE on the head-to-head. But: interleaving/varied practice is d = 0.83 in a preregistered classroom RCT; response congruency (d 0.58 → 0.28) says fixed-response practice is exactly what fails to transfer; and both Matuschak and Expertium independently warn that fixed surface forms are learned as surface forms. Against this: variants break FSRS's per-card D/S estimation and Matuschak's consistency criterion. The resolution is not "vary everything" but **vary within a stable knowledge component**, which is what Duolingo's half-life regression does at 13.3M-event scale — schedule the component, render a fresh surface each time.

---

## 12. Recommendations, ordered by expected effect

1. **Cut the mint cap from 10 to ~3 and make it a running budget, not a per-session allowance.** [cheap] The queue arithmetic in §8 is the design's biggest single defect, and it is fixed by one number. Track new-cards-in-flight; refuse to mint when the outstanding due load already exceeds review capacity. Expected effect: the difference between a working scheduler and one permanently in arrears.

2. **Fix the grader before anything else about scheduling.** [cheap] Give the LLM an explicit, hint-aware rubric: *Again* if the learner needed a hint that contained the answer, or produced the wrong core idea; *Hard* if correct but slow/partial and unprompted; *Good* if correct unprompted; *Easy* only if immediate and complete. Log whether a hint preceded the answer and make it a hard input to the grade. The Anki manual identifies grade dishonesty as the one habit FSRS cannot adapt to; every other scheduling improvement is downstream of this.

3. **Schedule the concept, render the item.** [expensive] Attach the DSR state to the *knowledge component* (concept + skill), not to a fixed front/back string, and generate a fresh surface form at review time from a stable spec. This is the Duolingo lexeme architecture, it resolves verdict (f) and (g) together, and it is what makes interleaving and varied practice available at all. Guard the FSRS assumption by keeping the *component's* difficulty stable — vary numbers, contexts and phrasings, not the required inference.

4. **Add problem-based review for probability: re-solve a varied problem rather than recall a fact.** [medium] d = 0.83 in Rohrer's RCT is the largest effect in this report, and strategy selection *is* the subject matter. Concretely: for probability, one worked-problem item is worth more than three `recall` cards, and should count against the same budget at a 3:1 rate.

5. **Interleave the review set deliberately.** [cheap] When due items exceed the cap, select for concept diversity instead of oldest-due-first, and order so that no two consecutive items share a concept. Pure upside; a scoring tweak in the queue builder.

6. **Drop `recognize` for probability; keep it for Italian comprehension only.** [cheap] Recognition is the weakest retrieval condition in every source here; transfer-appropriate processing is its only justification, and probability has no recognition criterion.

7. **Add a retention-interval input to desired retention.** [cheap] FSRS's DR default of 0.9 optimises workload-per-unit-knowledge under an infinite horizon; Cepeda's ridgeline says the right schedule depends on when the knowledge is needed. Let a subject declare a horizon (exam in 6 weeks vs. lifelong Italian) and set DR from it — higher for near deadlines, lower for open-ended goals. Cheap because FSRS already exposes the knob.

8. **Add periodic free-recall / brain-dump review at the concept level.** [medium] "Tell me everything you remember about conditional independence" captures the relational and non-targeted information no card can hold (free recall g ≈ 0.81, and superior for untargeted material), and it is the natural repair for verdict (f): schedule *concepts* on a slow FSRS track with free recall as the item type. Matuschak's own note argues conceptual material wants much slower schedules, so this is cheap in review minutes.

9. **Put a quality gate on minted items.** [medium] The controlled LLM-question result required instructor verification. Approximate it: a second-pass check against Matuschak's criteria (focused, precise, consistent, tractable, effortful — and *not* answerable by pattern-matching the phrasing), plus a repair loop when a card is repeatedly graded *Again* — a card failing three times in a row is usually a bad card, not a bad learner, and should be rewritten or deleted rather than rescheduled.

10. **Instrument, then trust the numbers over this report.** [medium] Log true retention vs. desired retention, review-queue depth over time, per-card lapse counts, and grade distribution. Two months of Seba's own data will settle the grader-honesty question (true retention far above 0.9 ⇒ the LLM is over-grading) more decisively than any citation here.

11. **Keep the conversational framing — it is the best-supported part of the design.** [free] QuizBot: >20% more correct answers with an identical scheduling algorithm, and 2.6× voluntary time on task. Do not "fix" the tutor by making review look more like a quiz sheet.
