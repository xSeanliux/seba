# 07 — Knowledge Structures: Is a Hand-Authored Prerequisite DAG the Right Representation?

Scope: formal theory of domain structure for adaptive instruction (Knowledge Space Theory, learning spaces, Q-matrices/CDMs, KC models), and what the evidence says about Seba's specific choice — an LLM-authored DAG of concepts with hard prereq gates, three-state status, and no data-driven revision.

---

## 1. Knowledge Space Theory: states, not nodes

### 1.1 The primitives

Doignon & Falmagne (1985); authoritative treatment in *Learning Spaces* (Springer, 2011), with a compact self-contained exposition in Falmagne & Doignon, "Knowledge Spaces and Learning Spaces," arXiv:1511.06757 (https://arxiv.org/abs/1511.06757).

- **Knowledge structure**: a pair `(Q, 𝒦)` where `Q` is a finite domain of *items* and `𝒦 ⊆ 2^Q` is a family of *knowledge states*. `∅ ∈ 𝒦` and `Q ∈ 𝒦`. A state is a set of items a student could, in principle, answer correctly.
- **Knowledge space**: a knowledge structure closed under **union**.
- **Learning space**: a knowledge structure satisfying two axioms (arXiv:1511.06757, Definition 3, §3):

  > **[L1] Learning smoothness.** For any two states `K, L` with `K ⊂ L`, there exists a finite chain of states `K = K₀ ⊂ K₁ ⊂ … ⊂ K_p = L` such that `|Kᵢ \ Kᵢ₋₁| = 1` for `1 ≤ i ≤ p`.
  > *In words: If the learner is in some state K included in some state L, then the learner can reach state L by mastering items one by one.*

  > **[L2] Learning consistency.** For any two states `K, L` with `K ⊂ L`, if `q` is an item such that `K ∪ {q}` is a state, then `L ∪ {q}` is also a state.
  > *In words: Knowing more does not prevent learning something new.*

- **Well-gradedness**: for any two states `K, L` there is a chain of states from `K` to `L` each differing by exactly one item, of length exactly `|K △ L|`.
- **Equivalence theorem** (arXiv:1511.06757, Thm 8; originally Cosyn & Uzun): the following are equivalent — `(Q,𝒦)` is a **learning space** ⟺ `(Q,𝒦)` is an **antimatroid** ⟺ `(Q,𝒦)` is a **well-graded knowledge space**. Learning spaces are literally the same objects as antimatroids / the duals of convex geometries (Edelman & Jamison 1985), so the whole combinatorial-geometry toolkit applies.

### 1.2 The fringes — "ready to learn" is a derived quantity, not an authored one

For a state `K` (Cosyn, Uzun, Doble & Matayoshi 2021, §1.1, https://jmatayoshi.github.io/publications/JMP2021_KST_ALEKS_preprint.pdf):

- **Outer fringe** `K^O = { q ∉ K : K ∪ {q} ∈ 𝒦 }`. "The outer fringe of a student's state may be thought of as the set of items the student is **'ready to learn.'**"
- **Inner fringe** `K^I = { q ∈ K : K \ {q} ∈ 𝒦 }` — "the items representing the 'high points' of the student's competence."
- **Theorem A.2**: in a learning space, a state is *completely determined* by its two fringes. So the entire learner model compresses to two small item sets.

This is the direct analogue of Seba's "frontier," but computed from a state lattice rather than read off a DAG.

### 1.3 Where a prerequisite DAG sits inside this theory — the decisive result

This is the crux. A prerequisite DAG is not merely *simpler* than a knowledge space; it is a **named special case with a known pathology**.

**Birkhoff's theorem** (1937), as stated in arXiv:1511.06757, Thm 10:

> There exists a one-to-one correspondence between the collection of all **quasi-ordinal spaces** `𝒦` on a set `Q` and the collection of all **quasi orders** `𝒬` on `Q`:
> `q 𝒬 r ⟺ 𝒦_q ⊇ 𝒦_r`; and `K ∈ 𝒦 ⟺ (∀(q,r) ∈ 𝒬 : r ∈ K ⇒ q ∈ K)`.

A *quasi-ordinal space* is a knowledge space closed under **both union and intersection** (Definition 9). And a quasi-order on items is exactly a prerequisite relation — the transitive closure of a prereq DAG.

So: **a prerequisite DAG ≡ a knowledge structure closed under union *and* intersection.** The states it admits are precisely the "downward-closed" sets — every set of concepts whose prereqs are all included. That is *literally* Seba's rule ("teach the first concept whose prereqs are all done"), and the theory names the object it generates.

Immediately after the theorem, Falmagne & Doignon add the damning line:

> "Note in passing that the closure under intersection does not make good pedagogical sense."

Why it doesn't: intersection-closure forces the structure to assert that if two different students can each be in states `K` and `L`, then some student is in exactly `K ∩ L`. That manufactures states nobody occupies. The consequence is stated explicitly in the construction section (§ below): a DAG-derived structure "typically contains a possibly very large number of **false states**, which are due to the closure of intersection."

**What a knowledge space captures that a DAG cannot:**

1. **Disjunctive prerequisites (OR, not just AND).** A DAG says: to learn `q`, have *all* of `prereqs(q)`. A knowledge space's **base/atoms** (§4 of arXiv:1511.06757) permit *several minimal states* containing `q` — i.e. alternative sufficient prerequisite bundles. Formally this is a *surmise system* (an AND/OR structure) rather than a *surmise relation* (pure AND). Real domains are full of this: you can reach "solving quadratics" via factoring *or* via completing the square; either route licenses the next topic.
2. **Genuinely multiple learning paths.** In a learning space the number of orderings from `∅` to `Q` is enormous and *many are equally valid*; the outer fringe typically offers a learner many simultaneous choices. A DAG's frontier can also be a set, but the DAG cannot express that mastering `a` *changes which* of the remaining items are appropriate next in a way not derivable from ancestry.
3. **States as first-class objects.** Assessment in KST is a search over the *state lattice*, so evidence about item `x` moves probability mass onto/off *whole states*, propagating to items never asked. A DAG has no state space, so it has no mechanism for this inference.
4. **Scale, quantified.** The gap is not marginal. For one ALEKS course of **314 items**, `|𝒦| ≈ 10²³` states — against `2³¹⁴ ≈ 10⁹⁴` subsets (Cosyn et al. 2021, §1.1). ALEKS's public page claims Algebra 1's ~350 items give "millions of empirically feasible knowledge states" (https://www.aleks.com/about_aleks/knowledge_space_theory). A DAG over 314 concepts admits exactly one state per antichain-closed set — a vastly smaller and differently shaped family.

---

## 2. ALEKS: the deployed instance

### 2.1 How the structure is built — and this is the part that matters most for Seba

ALEKS is the industrial instantiation of KST (~4–5 million students/yr; Cosyn et al. 2021 §1). Structures are built by the **QUERY routine** (Koppen 1993; Müller 1989), which asks queries of the form:

> **[Q]** Suppose a student has just provided wrong responses to all items in some set `A`. Is it practically certain the student will also fail item `q`?

Queries are grouped into **Blocks** by `|A|`. From arXiv:1511.06757, §"About Building Knowledge Spaces or Learning Spaces":

- **Block 1** asks only *pairwise* questions `[Q1]` ("student failed `q` — will they also fail `r`?"). "In principle an expert teacher is able to provide the answer to any query in Block 1." The responses give a relation `R`; its **transitive closure is a quasi order**; by Birkhoff this yields an **ordinal space `L₁`**.
- **`L₁` is exactly a prerequisite DAG.** And: "it also typically contains a possibly very large number of **false states**, which are due to the closure of intersection of `L₁`."
- **"While human experts are capable of providing useful responses to queries of the type [Q1], their responses to queries of higher blocks are less reliable."**
- The fix is data: "The data collected by assessments using `L₁` can then be used to **simulate human expert responses to queries of higher block numbers**," e.g. Block 2 via estimated `P(q = 0 | r = t = 0) > θ`.

**Read that sequence carefully. Seba's design is `L₁` — Block 1 only, expert-elicited, never refined.** ALEKS's own authors describe `L₁` as (a) the starting point, (b) full of false states, and (c) something you deploy in order to collect the data that fixes it. There is a pragmatic concession worth quoting in Seba's favour: "despite the presence of false states, the learning space `L₁` is sufficiently informative to be used in the schools and colleges." A DAG is a *defensible v1*. It is explicitly not the end state.

### 2.2 Assessment: locating the learner

An ALEKS assessment is "a probabilistic search among all of the feasible states to uncover the student's latent state" (Cosyn et al. 2021 §1.3). Start from a prior over states; repeatedly select an item whose **likelihood is near 0.5** (states containing it sum to ~0.5); Bayesian-update state probabilities on each response; stop when one state dominates. ~25–30 questions. Careless-error and lucky-guess parameters are modelled; ALEKS items are open-response so lucky guesses are rare and slips dominate (update parameters "about 35 for a [correct]" — §1.3 fn). Because structures are too large to enumerate, the item set is **partitioned** and parallel sub-assessments run on projections, with information carried across partitions (per Falmagne et al. 2013 §8.8).

Learning mode: after assessment, "the student's **outer fringe** is determined and serves as the student's entry point"; the learner **chooses** an item from the outer fringe (a graphical list — learner agency over the frontier, not system-dictated); on success the item is added and the fringe recomputed. Periodic **progress assessments** re-locate the state — deliberately framed as retrieval practice and as forced interleaving over previously massed items.

### 2.3 Does the assessment actually work? (internal validation)

Cosyn et al. 2021, §2, using an "extra problem" (one item chosen uniformly at random, excluded from the state estimate) across **3.1M initial assessments (2012–early 2020)**:

| Course | n assessments | AUROC | Accuracy |
|---|---|---|---|
| Sixth-Grade Math | 162,900 | 0.875 | 0.801 |
| College Algebra | 174,073 | 0.863 | 0.808 |
| College Placement | 2,775,432 | 0.889 | 0.814 |

Classification breakdown (College Placement): in-state items correct 0.838, out-of-state 0.102, "uncertain" 0.449 — the uncertain bucket sitting near 0.5 is offered as a calibration check. Measures converge by **question ~10** of 29.

That is a genuinely strong result: a structural model predicting unseen item performance at AUROC ≈ 0.88 from ~25 questions.

### 2.4 Does ALEKS actually teach better? (independent evidence — much weaker)

- **Sun, Else-Quest, Hodges, French & Dowling (2021)**, *Investigations in Mathematics Learning*, https://doi.org/10.1080/19477503.2021.1926194 — meta-analysis, **56 effect sizes, 9,238 students, 33 studies (2000–2020)**: "learning performance with ALEKS was **comparable to** that with traditional instruction (**Hedges' g = 0.05, 95% CI [−0.01, 0.20]**)"; effective specifically "when used to **supplement** traditional instruction (**g = 0.43, 95% CI [0.02, 0.83]**)."
- **Fang, Ren, Hu & Graesser (2018/2019)**, *Educational Psychology*, https://doi.org/10.1080/01443410.2018.1495829 — 15 studies, 24 samples: "ALEKS was **as good, but not better than**, traditional classroom teaching." Notably, "effect sizes were greater when ALEKS was used for **shorter** periods of time rather than longer" — a pattern consistent with novelty effects rather than accumulating structural benefit.
- An IES-funded RCT in 10 Pennsylvania schools (20 teachers, ~1,320 students/yr, Keystone Algebra outcome) ran 2014–2017: https://ies.ed.gov/use-work/awards/efficacy-aleks-improving-student-algebra-achievement — the award page reports design but **no results**.

**Interpretation for Seba.** The most mathematically sophisticated domain-structure system ever deployed, with 10²³ states and AUROC-0.88 state estimation, produces `g ≈ 0.05` against ordinary classroom teaching. This is the single most important calibration fact in this document: **investment in structural fidelity has, empirically, a poor conversion rate into learning outcomes.** It is an argument against Seba building a knowledge space at least as much as it is an argument against Seba's DAG. The confidence interval `[−0.01, 0.20]` does not license "structure doesn't matter" — but it firmly rejects "more structure is where the gains are."

---

## 3. Q-matrices and cognitive diagnostic models

### 3.1 The apparatus

- **Q-matrix** (Tatsuoka 1983): a `J × K` binary matrix; `q_jk = 1` iff item `j` requires attribute `k`. Introduced with the **rule space** method (Tatsuoka 1983; *Cognitive Assessment: An Introduction to the Rule Space Method*, 2009), which maps response patterns into a space of IRT ability × "caution index" to classify examinees against ideal-response patterns and diagnose *misconceptions* (erroneous rules), not just deficits.
- **DINA** (Deterministic Input, Noisy "And") — conjunctive: you get item `j` right iff you have *all* attributes in `q_j`, modulo slip `s_j` and guess `g_j`. **DINO** — disjunctive "Or": *any* one attribute suffices. The DINA/DINO contrast is the psychometric version of exactly the AND-vs-OR prerequisite question raised in §1.3.
- **Attribute Hierarchy Method** (Leighton, Gierl & Hunka 2004): a variation on rule space that adds an explicit **hierarchy among attributes** — i.e. a prerequisite DAG *over attributes*, which then constrains the set of admissible attribute patterns. AHM is the closest formal cousin to Seba's design: a DAG over latent skills, admitting only downward-closed mastery patterns.

### 3.2 How Q-matrices are validated or learned

- **Misspecification is consequential**: it "can seriously affect the accuracy of the classification of examinees" and biases item parameters, class sizes, and attribute-pattern estimates (DeCarlo 2011; de la Torre et al. 2010; de la Torre & Chiu 2016; Köhn & Chiu 2018).
- **GDI method** (de la Torre & Chiu, *Psychometrika* 2016, https://doi.org/10.1007/s11336-015-9467-8): a discrimination index generalizing the δ-method to the G-DINA family; identifies and replaces misspecified q-entries. Implemented in R's `GDINA`.
- **Iterative/dynamic validation** (Nájera et al., https://pmc.ncbi.nlm.nih.gov/articles/PMC7383688/): Q-matrix recovery rates of **0.940 / 0.933 / 0.913 / 0.893** at 10/20/30/40% initial misspecification; classification accuracy at 40% misspecification recovered to 0.895 vs 0.910 with the true Q-matrix. On the real fraction-subtraction data, ~6 q-entries were proposed for modification.
- The methodological premise is telling: "it would be difficult, if not impossible, for the same experts to correctly specify all the entries of the Q-matrix, particularly when the test is long," and simulation studies routinely assume misspecification rates **up to 40%**. The field's *default assumption* is that expert-authored structure is substantially wrong.
- Fully **data-driven Q-matrix learning** exists (Liu, Xu & Ying, "Data-driven learning of Q-matrix," https://sites.stat.columbia.edu/jcliu/paper/PsyMeth4Name.pdf; Chen et al., arXiv:1106.0721), with identifiability conditions — but requires large response matrices.

**Relevance to Seba.** Seba has no Q-matrix at all: concepts are not decomposed into attributes, and there are no items formally mapped onto them. This isn't a misspecified Q-matrix; it's `K = 1` per concept with `J` unmodelled. That forecloses the entire validation apparatus above — there is nothing to validate against.

---

## 4. Knowledge Components, learning curves, and the KLI framework

### 4.1 KCs and learning-curve analysis

A **knowledge component** is "an acquired unit of cognitive function or structure that can be inferred from performance on a set of related tasks" (Koedinger, Corbett & Perfetti 2012). The **Additive Factors Model (AFM)** is a logistic growth model: `logit(p_ij) = θ_i + β_k + γ_k · T_ik` — student ability, KC difficulty, and a KC-specific learning rate times opportunity count.

**Learning curve analysis as a model-diagnosis tool.** If the KC model is correct, aggregating over all opportunities for a KC should produce a smooth, monotone decreasing error curve (a power/exponential law of practice). It does not when the labelled "KC" actually bundles several distinct KCs: the curve shows **blips** (non-monotonic jumps) and poor fit, because opportunity `n` for one student is a different underlying skill from opportunity `n` for another. **Learning Factors Analysis** (Cen, Koedinger & Junker 2006, "Learning Factors Analysis – A General Method for Cognitive Model Evaluation and Improvement," https://doi.org/10.1007/11774303_17, ~573 citations) automates the search: it splits KCs on candidate factors and selects by cross-validated fit, producing a *better* KC model from data. This is a real, working feedback loop from learner data to domain structure. (Note: I could not retrieve the full text of Cen et al. 2006/2007 — the CMU PACT server's certificate has expired and its publication index 404s — so the "blips" characterisation above is from secondary descriptions, e.g. Scheines et al. 2014, and the KLI paper's account of related model-refinement work, not verbatim from the primary.)

Downstream, model refinement has been shown to feed back into instruction: Stamper & Koedinger, "Human-Machine Student Model Discovery and Improvement Using DataShop" (AIED 2011); Koedinger, Stamper, McLaughlin & Nixon, "Using Data-Driven Discovery of Better Student Models to Improve Student Learning" (AIED 2013, https://doi.org/10.1007/978-3-642-39112-5_43). LearnSphere/DataShop (https://pslcdatashop.web.cmu.edu/) is the public repository.

### 4.2 The regularity result — how much practice a KC actually needs

Koedinger, Carvalho, Liu & McLaughlin, "An Astonishing Regularity in Student Learning Rate," *PNAS* 2023 (preprint: https://praxis-ai.com/wp-content/uploads/2023/03/An-Astoninshing-Regularity-in-Student-Learning-Rate-1.pdf). **1.3 million observations, 27 datasets.** Verbatim:

> "students demonstrate modest initial performance … initial performance varies substantially from about 55% correct for those in the lower half to …"
> "students are astonishingly similar in estimated learning rate, typically increasing by about **0.1 log odds or 2.5% in accuracy per opportunity**."
> "Students do need extensive practice, about **7 opportunities per component of knowledge**."

Three consequences for Seba:

1. **~7 practice opportunities per KC** is the calibration for what "done" should mean. A concept marked done after one teaching pass and a couple of checks is nowhere near this.
2. **Individual differences live almost entirely in prior knowledge (initial performance), not in learning rate.** So the highest-value personalisation is *knowing where the learner already is* — precisely the assessment/state-location problem — not adapting pace or method.
3. Learning rate is roughly constant across students *and* KCs, which means a well-specified KC model has predictable practice budgets. A concept-level unit has no such budget.

### 4.3 KLI: knowledge type should determine instructional method

Koedinger, Corbett & Perfetti (2012), *Cognitive Science* 36(5), 757–798, https://doi.org/10.1111/j.1551-6709.2012.01245.x (authors' final version retrieved from pact.cs.cmu.edu).

**The KC taxonomy** (Table 3, verbatim structure) — four distinctions: generality of *application conditions*, generality of *response*, whether the relationship is *verbal*, and whether the KC has a *rationale*:

| Application conditions | Response | Relationship | Rationale | Labels |
|---|---|---|---|---|
| constant | constant | non-verbal | no | association |
| constant | constant | verbal | no | **fact** |
| variable | constant | non-verbal | no | category |
| variable | constant | verbal | no | concept |
| variable | variable | non-verbal | no | production, schema, skill |
| variable | variable | verbal | no | **rule**, plan |
| variable | variable | verbal | **yes** | **principle**, rule, model |

**Learning processes** (§4): (A) *Memory and fluency-building* — non-verbal strengthening/compilation; (B) *Induction and refinement* — non-verbal accuracy improvement (generalization, discrimination, schema induction), modifying a KC's conditions; (C) *Understanding and sense-making* — explicit, verbally-mediated reasoning, linking a KC to its rationale.

**The core claim** (§3.3.2, "Kinds of KCs drive Instructional Event choices"), verbatim:

> "The differentiation of knowledge types has implications for the effectiveness of an instructional principle… many learning processes and instructional design decisions are not restricted to a domain as whole, but are determined by the **type of KCs being learned**… instructional principles should refer to **KCs rather than to domains**. A hypothetical principle 'drill and practice is not effective for mathematics' is at the wrong level of analysis."

The specific mapping hypotheses:

- **Constant–constant KCs** (facts, vocabulary) and non-verbal probabilistic variable-condition KCs → **recall/testing, spaced practice, tutored practice, optimized scheduling** (Roediger & Karpicke 2006; Cepeda et al. 2006; Pavlik 2007).
- **Complex variable–variable KCs** (e.g. designing a controlled experiment) → **comparison/blocking and worked-example study** (Gick & Holyoak 1983; Sweller & Cooper 1985).
- **Integrated variable–variable KCs** learned in both procedural and declarative form (math/science principles) → **prompted self-explanation** (Aleven & Koedinger 2002).
- **KCs with rationales** (discoverable principles, not conventions) → **argumentation and instructional dialogue** (Michaels, O'Connor & Resnick 2008). And conversely, on rationale: "Instruction that involves students in explicitly discovering KCs from data or deriving KCs through argumentation may be **productive for KCs with a rationale, but not for ones without**."

And the punchline for any system with one teaching method:

> "The various instructional recommendations seem **mutually incompatible** without the taxonomy. They would reflect 'education wars:' More worked example study is at odds with more testing of recall, blocked comparison of examples is at odds with spacing, pure non-verbal practice is at odds with prompts for self-explanation and extended classroom dialogue and argumentation."

Plus an asymmetry worth noting (§4.4): "simpler learning processes (fluency and refinement) may support complex knowledge but **complex learning processes (e.g., argumentation) may fail to support simple knowledge** (e.g., arbitrary constant-constant associations)." A Socratic-dialogue tutor applied uniformly is predicted to fail *specifically* on facts, vocabulary, notation, and conventions — and Seba, being conversational, defaults to exactly that method everywhere.

Caveat in fairness: KLI presents these as "tentative hypotheses… all these hypotheses require further testing," each with "some support in the research literature." It is a strong framework claim, not a settled experimental result.

---

## 5. Are expert-authored prerequisite structures accurate?

### 5.1 Expert blind spot

Nathan & Koedinger (2000a,b); Nathan, Koedinger & Alibali (2001), "Expert Blind Spot: When Content Knowledge Eclipses Pedagogical Content Knowledge," https://pact.cs.cmu.edu/pubs/2001_NathanEtAl_ICCS_EBS.pdf; Nathan & Petrosino (2003), *AERJ* 40(4), 905–928, https://doi.org/10.3102/00028312040004905.

The hypothesis: educators with advanced subject knowledge "tend to use the powerful organizing principles, formalisms, and methods of analysis that serve as the foundation of that discipline as guiding principles for their students' conceptual development … rather than being guided by knowledge of the learning needs and developmental profiles of novices."

The concrete finding: 105 teachers ranked algebra problems by expected student difficulty. Teachers with **more advanced mathematics education were more likely to view symbolic reasoning as a prerequisite for word/story problems**. Students actually performed *better* on simple algebra story problems than on the mathematically equivalent equations. **The expert-asserted prerequisite direction was backwards.**

This is not a peripheral result. It is a prerequisite edge, asserted by domain experts, on a central topic in the most-studied curriculum in learning science, pointing the wrong way — and the mechanism generating the error (reasoning from the discipline's logical structure rather than from learners' behaviour) is *exactly* the mechanism an LLM reading a table of contents will use. A textbook's TOC **is** the discipline's organizing structure. It is the canonical source of expert blind spot, not a corrective to it.

### 5.2 Direct empirical tests of expert prereq graphs

- **Vuong, Nixon & Towle (2011)**, "A Method for Finding Prerequisites Within a Curriculum," EDM 2011, pp. 211–216. As characterised by Scheines, Silver & Goldin (2014): they "applied a test to data on almost every possible instructional unit pairing in **four Carnegie Learning math curricula**. The test relied on natural variation in longitudinal data collected from many instructors' use of the Cognitive Tutor to see if students could succeed on a unit **without having earlier mastered another unit**." *(I was unable to retrieve the primary PDF — EDM 2011 proceedings server returns 500, ResearchGate/studylib block automated access — so I do not have their confirmation rates first-hand and am not asserting a number.)*
- **Scheines, Silver & Goldin (2014)**, "Discovering Prerequisite Relationships among Knowledge Components," EDM 2014, https://www.stat.cmu.edu/~brian/nynke/726-2021/week06/HCI%20prereq%20discovery/ScheinesSilverGoldin-EDM2014.pdf. Their stated motivation, verbatim:

  > "How can we choose a topic ordering? It seems obvious to ask an expert. But just as an instructor or researcher may hold an '**expert blind spot**' regarding which topic is more difficult for learners, we suspect that **expert opinions are not a reliable way to determine effective topic order**. Besides, there are a great many topics in each domain, and asking experts is prohibitively costly in time and effort."

  Their method treats KCs as latent variables and prerequisites as **causal** relations, then applies causal structure discovery (Spirtes, Glymour & Scheines) to a *single* cross-sectional assessment (~120 students, developmental math), exploiting the "screening off" signature: if `A → B → C`, conditioning on `B` renders `A` uninformative about `C`. They assume the Q-matrix is known. Simulation results: low false-positive orientation rates, good precision, "quite well" on false negatives. They note the motivating uncertainty honestly: "should one study the computation of the area of a square before or after the area of a rectangle? … **it may be effective to study either topic first**."
- They also flag a granularity point directly relevant to Seba, quoting Carnegie Learning: "**the unit is not the smallest level of organization where prerequisite structure matters.** 'Units cover distinct mathematical topics; sections [within units] cover distinct sets of problems on that topic, with a distinct student skill model for each section.'"

### 5.3 …but data-driven discovery isn't reliable either

This is the honest counterweight, and it materially softens the case against Seba.

- **PREREQ** (Roy, Madhyastha, Lawrence & Rajan, AAAI 2019, arXiv:1811.12640): concept prerequisite inference. On the University Course Dataset (654 courses, 861 course-prereq edges, 1008 annotated concept pairs, 365 concepts) the **best F-score is 59.68** (P 46.76 / R 91.64), versus CPR-Recover 24.54 and MOOC-RF 50.95. On the NPTEL MOOC dataset PREREQ precision 55.60. State of the art on automatic prerequisite extraction is **F1 ≈ 0.6**.
- **Knowledge-structure discovery from interaction logs** (arXiv:2402.01672, "Prerequisite Structure Discovery in Intelligent Tutoring Systems"): on *synthetic* data with known ground truth, best F1 = **0.46** with random exercise sequencing, dropping to **0.17** when sequences follow a curriculum order — because "the biased sequencing of exercises in those datasets can hinder KS discovery." That second number is critical: **if you always teach in your DAG's order, your logs contain almost no evidence about whether the DAG is right.** You never observe the counterfactual.
- Newer LLM/graph work exists (e.g. arXiv:2509.05393 inferring PRs in educational knowledge graphs; K12-KGraph, arXiv:2605.09635) but reports no accuracy that changes this picture.

**Net.** Expert-authored prereq structures are demonstrably unreliable in a specific, well-documented direction (expert blind spot). Automated alternatives top out around F1 0.5–0.6. Nobody has a trustworthy prerequisite graph. The rational response is not "get a better graph" but "**stop treating the graph as ground truth**."

---

## 6. Granularity: how big should the tracked unit be?

Evidence, ordered by strength:

1. **KCs are much finer than textbook sections.** In Cognitive Tutor curricula, each *section within a unit* has "a distinct student skill model," and units decompose into dozens of KCs. ALEKS courses run **300–600 items** for one course (Cosyn et al. 2021 §1.2) — roughly one item per textbook *sub-subsection*. A textbook TOC at chapter/section level yields ~20–80 concepts. That's an order of magnitude coarser.
2. **The practice budget argument.** ~7 opportunities per KC (Koedinger et al. 2023). If a "concept" bundles 8 KCs, adequate coverage needs ~56 practice opportunities, and a single binary done/not-done flag cannot tell you which of the 8 is missing. All within-concept diagnostic signal is discarded by construction.
3. **Integrative KCs are invisible at coarse grain.** Heffernan & Koedinger (1997), reported in KLI §3.2: students were significantly worse at translating **two-step** algebra story problems (`800−40x`) than at two closely matched **one-step** problems (`800−y` and `40x`). The gap implicates a missing *integrative* KC — a recursive grammar rule for embedding expressions. Targeted instruction on that KC significantly improved performance (Koedinger & McLaughlin 2010). At concept granularity ("translating story problems") this KC does not exist and cannot be taught.
4. **The famous vocabulary case.** KLI §3.1.1: in ASSISTments, errors on "What is 3/4 of 1/2?" were "sometimes not about the math, but about **vocabulary**" — students erred more on "What does 'of' indicate?" than on "what is ¾ times ½?". A concept-level model attributes this to a fraction-multiplication failure and re-teaches the wrong thing.
5. **Counterweight — finer is not free.** LFA/AFM model *selection* is genuinely hard; "Better Model, Worse Predictions: The Dangers in Student Model Comparisons" (AIED 2021, https://doi.org/10.1007/978-3-030-78292-4_40) documents that improved fit statistics don't reliably mean improved models. And splitting KCs multiplies the data needed to estimate anything. Without a mastery model, a finer decomposition buys Seba little on its own.

**Conclusion**: the literature is unambiguous that KC-level ≪ concept-level, but the *benefit* of finer grain is realised through the mastery/assessment model, which Seba doesn't have. Grain size and modelling capability have to move together.

---

## 7. Are prerequisites hard gates or soft?

The evidence says **soft**, on several independent grounds:

1. **KST's own formalism is probabilistic at the boundary.** Even in ALEKS, states are latent and inferred with slip/guess parameters; assessments leave an explicit **"uncertain"** category (~10–17% of items, correct rate 0.42–0.45), and "the state assigned to the student at the end of the assessment does not include these uncertain items and so may **underestimate** the student's latent state." Learning of uncertain items is then "fast-tracked" — i.e. the system explicitly overrides its own gate. Mastery is not binary even in the canonical hard-structure system.
2. **The query itself is hedged.** [Q1] asks whether it is "**practically certain**" the student will also fail `r` — an epistemic, probabilistic judgement, and Block 2+ is operationalised as a *thresholded conditional probability* `P(q=0 | r=t=0) > θ`. Prerequisite-ness in KST is a probability compared against a tunable threshold, not a logical implication.
3. **Ordering is often genuinely free.** Scheines et al.: "it may be effective to study either topic first" (square vs rectangle area). A learning space's whole point is that many orderings are valid.
4. **Downstream systems treat them as soft.** arXiv:2402.01672 §II describes prior work that "exploits known prerequisite relations as **soft constraints** on the ordering of the estimated learner [state]" rather than as gates.
5. **Hard gates interact catastrophically with authoring error.** A false edge in a soft system costs a suboptimal ordering suggestion. A false edge in a hard-gate system makes a downstream concept **unreachable** until the learner completes something they may not need. Given expert blind spot (§5.1) and F1 ≈ 0.6 automated alternatives (§5.3), the expected number of wrong edges in an LLM-drafted DAG is not small, and hard gating maximises the damage per wrong edge.
6. **Countervailing.** Prerequisite structure is *real* — it's exactly why ALEKS's 314 items yield 10²³ states instead of 10⁹⁴, a compression of ~71 orders of magnitude driven entirely by "the inherent relatedness of items, as some items are prerequisites of other items." The claim is not that prerequisites are fictional; it's that they are strong statistical constraints, not logical gates.

---

## 8. Verdicts on Seba's design

### (a) A DAG rather than a knowledge space / state lattice — **SUPPORTED (with a named ceiling)**

A DAG is not an ad-hoc simplification; by Birkhoff's theorem it is exactly a **quasi-ordinal knowledge space**, and by ALEKS's own construction method it is exactly the **`L₁` structure produced by Block 1 of QUERY**. Falmagne & Doignon state plainly that `L₁` "is sufficiently informative to be used in the schools and colleges." So the representation has formal standing and a working precedent as a v1.

Three caveats attach. (i) It carries "a possibly very large number of **false states**" from intersection-closure, and the authors say intersection-closure "does not make good pedagogical sense." (ii) It cannot express **disjunctive prerequisites** (alternative routes to the same concept), which are common. (iii) Upgrading to a real learning space costs an assessment engine, a state-space search, and a data pipeline — and ALEKS, which has all three, beats traditional instruction by **g = 0.05**. For a 1:1 LLM tutor with no item bank, building a state lattice would be a large investment against weak evidence of payoff. Keep the DAG; know what it costs you.

### (b) Prereq edges as hard gates — **CONTRADICTED**

The clearest verdict here. KST's own prerequisite queries ask about "practical certainty" and are implemented as thresholded conditional probabilities; ALEKS maintains an explicit uncertain category and fast-tracks past it; downstream ITS work uses prereqs as soft ordering constraints; and Scheines et al. document ordering pairs where either direction works. Meanwhile the *error rate* on authored prereq edges is high (§5.1, §5.3), and hard gating converts each authoring error into an unreachable concept rather than a mildly suboptimal suggestion. Hard gates are the single worst-supported choice in Seba's design *conditional on* the structure being LLM-authored and unrevised.

### (c) Concept-level granularity rather than KC-level — **CONTRADICTED as a measurement choice; UNSUPPORTED-but-defensible as a teaching choice**

Deployed systems track 300–600 items per course; KCs need ~7 practice opportunities each; integrative KCs and vocabulary KCs are provably invisible at concept grain (Heffernan & Koedinger; the "of" example). A textbook TOC is roughly an order of magnitude too coarse for the thing you track mastery on.

But the split matters: it is fine for the *teaching session* to be organised around a concept. What is contradicted is using the concept as the *unit of mastery inference*. Since Seba has no mastery model at all, refining grain alone would not help — the two must move together, which is why the recommendation below couples them.

### (d) LLM-authored structure from a table of contents — **CONTRADICTED in its strong form; UNSUPPORTED in its weak form**

An LLM reading a TOC is doing exactly what the expert blind spot literature identifies as the failure mode: deriving learner-facing sequence from the discipline's own organizing structure. Nathan & Koedinger found expert-asserted prerequisite direction was *backwards* on a central algebra case. A TOC is the purest available expression of disciplinary rather than developmental structure.

Two mitigations. First, textbook TOCs *do* encode real sequencing knowledge accumulated over editions and classroom use — this is not random. Second, nobody has better: automated extraction runs F1 ≈ 0.6, and hiring experts gives you the blind spot anyway. The defensible position is that an LLM-drafted DAG is a **reasonable prior** and an **unreasonable ground truth**. Learner approval does not fix this — a learner new to the domain cannot detect an inverted prerequisite edge; that is what makes it a blind spot.

### (e) Never revising the structure from observed learner data — **CONTRADICTED**

Every serious tradition in this literature has a revision loop and treats it as essential, not optional:

- KST: Block 1 (`L₁`, the DAG) is explicitly the *starting* structure; deployment data simulates expert responses for Blocks 2+.
- CDM: GDI and iterative Q-matrix validation, with the field assuming misspecification up to 40% and recovering 89–94% of entries.
- KC modelling: LFA/DataShop exist for precisely this, and refined models have produced measured instructional improvements (Stamper & Koedinger 2011; Koedinger et al. 2013).
- Causal discovery: Scheines et al. built a method specifically because experts can't be trusted.

There is one strong technical caveat that *supports* Seba's caution: arXiv:2402.01672 shows structure discovery collapses from F1 0.46 to **0.17** when the observed sequences follow a curriculum order. Seba always teaches in DAG order, so its logs are maximally confounded — naive edge-learning from Seba's own data would be worse than useless. The fix is not "no revision" but **cheap, targeted revision** (§9.2–9.3): record explicit violation events rather than trying to induce a graph.

### (f) One uniform teaching method regardless of knowledge type — **CONTRADICTED**

This is the KLI framework's central claim: "instructional principles should refer to **KCs rather than to domains**"; the recommendations for facts (recall, spacing), for complex variable-variable KCs (worked examples, comparison), for principles (self-explanation), and for rationale-bearing KCs (argumentation, dialogue) "seem **mutually incompatible** without the taxonomy." A single method must be wrong for most cells of the taxonomy.

The specific risk for Seba is sharp and directional. Seba is a conversational tutor, so its default method is dialogue/elicitation/explanation — the **understanding and sense-making** end. KLI's asymmetry claim (§4.4) says complex processes like argumentation "may **fail to support** simple knowledge (e.g., arbitrary constant-constant associations)." Italian vocabulary, notation conventions, and definitional facts are constant-constant KCs with no rationale, for which the indicated instruction is spaced retrieval — and for which Socratic dialogue is predicted to be actively inefficient. Seba already has spaced review, so it has both tools; it just doesn't route between them by knowledge type.

Honesty about strength: KLI's mappings are framed by its authors as "tentative hypotheses [that] require further testing." The verdict is CONTRADICTED because the *uniformity* claim is what the framework directly attacks, and because the underlying instructional principles (testing effect, spacing, worked examples, self-explanation) are individually well-replicated even if their KC-type routing is not.

---

## 9. Recommendations, ordered by expected effect

**1. Make prereq edges soft. (CHEAP — schema + prompt)**
Add `strength: "hard" | "soft"` to each edge, default `soft`, and have the frontier rule admit any concept whose *hard* prereqs are done and whose *soft* prereqs are done-or-explicitly-waived. Surface soft-blocked concepts as available-with-a-warning. This is the highest-leverage change in the document: it removes the mechanism by which a single wrong LLM-authored edge makes content unreachable, and it aligns with how KST itself treats prerequisites (thresholded probabilities, "practically certain," fast-tracking of uncertain items). *Fixes verdict (b), and de-risks (d).*

**2. Tag each concept with a KC type and route teaching method off the tag. (CHEAP — prompt + one enum field)**
Add `kc_type: fact | concept | procedure | principle` (a coarsening of KLI Table 3) at DAG-authoring time. Then: facts → spaced retrieval, minimal dialogue; procedures → worked example then faded practice; principles → self-explanation prompts and argumentation. This is a prompt change plus a field, and it directly implements the one framework claim that most clearly indicts current behaviour. Ask the authoring LLM additionally for `has_rationale: bool` — KLI is explicit that discovery/argumentation is productive for KCs with a rationale "but not for ones without." *Fixes verdict (f).*

**3. Log prerequisite-violation evidence, even if you never act on it automatically. (CHEAP — logging)**
Every time a learner struggles on concept `C`, record which prereqs were done and how recently; every time a soft prereq is waived (per rec. 1) and the learner then succeeds, record that as evidence the edge is spurious. This is the *only* clean signal available given that Seba always teaches in DAG order and therefore has confounded logs (arXiv:2402.01672: F1 drops 0.46 → 0.17 under curriculum-ordered sequences). Waivers create the counterfactual variation that makes the data informative. Cheap now, and it's the prerequisite for everything expensive later. *Partially addresses (e).*

**4. Support disjunctive prerequisites. (CHEAP — schema)**
Change `prereqs: [id]` to `prereqs: [[id]]` — a list of alternative sufficient sets, satisfied if any inner set is complete. This is the single structural feature a DAG lacks that knowledge spaces have and that matters in practice (alternative routes to a concept), and it is a one-line schema change with a two-line frontier-rule change. Have the authoring LLM emit alternatives where they exist. *Narrows the gap in verdict (a) at near-zero cost.*

**5. Split concepts into sub-KCs at authoring time and track them. (MODERATE — schema + status model)**
Ask the authoring LLM for 3–8 named sub-KCs per concept, each with its own `kc_type`, and let `done` be derived from sub-KC coverage rather than asserted at concept level. Calibrate against ~7 practice opportunities per KC (Koedinger et al. 2023, PNAS). This is what makes concept-level "done" mean something and what lets review target the actual gap ("what does 'of' indicate?") instead of re-teaching the whole concept. Not cheap — it touches the status model, the review scheduler, and the session loop — but it is the change that unlocks recs 6 and 7. *Fixes verdict (c).*

**6. Prompt the authoring LLM specifically against expert blind spot. (CHEAP — prompt)**
The TOC is the disciplinary structure; that is the documented source of the error. Add explicit instructions: "For each edge, state whether A is required to *understand* B or merely conventionally taught first. Mark conventionally-ordered pairs as soft. Note where the concrete/applied version is likely easier for a novice than the formal one, and do not assume formalism precedes application." Cite the algebra story-problem case as the exemplar in the prompt. Cheap, and directly targets the specific failure mode in (d). Also: have a second LLM pass adversarially review the DAG for inverted edges, which is far more likely to catch them than learner approval.

**7. Replace binary status with a graded mastery estimate. (EXPENSIVE — real modelling)**
Per-sub-KC opportunity counts and a simple logistic growth model (AFM-style: learner ability + KC difficulty + rate × opportunities), with the PNAS rate prior (≈0.1 log-odds/opportunity) as a strong default so it works with very little data. This gives real "readiness" instead of a flag, and makes the frontier a ranked recommendation rather than a gate. Justified by §4.2's finding that individual differences are concentrated in *prior knowledge*, not learning rate — so the payoff is in locating the learner, which is exactly what this buys. Expensive; do it only after rec. 5 exists.

**8. Periodic re-assessment that can move a concept backwards. (MODERATE)**
ALEKS's progress assessments re-locate the state and can *remove* items — Seba's monotone unseen→in-progress→done has no mechanism for forgetting or for discovering that "done" was premature. Given a graded model (rec. 7) this falls out; without it, a cheap version is: periodically re-test a random done concept and demote on failure. Also delivers the retrieval-practice and interleaving benefits ALEKS explicitly credits to progress assessments.

**9. Do not build a knowledge space / state lattice. (EXPLICIT NON-RECOMMENDATION)**
Recorded here so the option is closed deliberately. It requires an item bank, a state-enumeration and projection scheme, and Bayesian state search — and the reference implementation with all of that, at 10²³ states and AUROC 0.88 state estimation, achieves **Hedges' g = 0.05 [−0.01, 0.20]** against ordinary classroom teaching (Sun et al. 2021). Structural fidelity has a demonstrably poor conversion rate into learning gains. Recs 1–6 capture most of the theory's actionable content for a few schema fields and prompt changes; recs 7–8 capture the rest of the realistic upside.

---

## Sources

- Falmagne, J.-C. & Doignon, J.-P. (2015). *Knowledge Spaces and Learning Spaces*. arXiv:1511.06757 — https://arxiv.org/abs/1511.06757 *(axioms [L1]/[L2], well-gradedness, antimatroids, Birkhoff Thm 10, base/atoms, QUERY routine and Block 1/Block 2 construction)*
- Falmagne, J.-C. & Doignon, J.-P. (2011). *Learning Spaces*. Springer, Interdisciplinary Applied Mathematics. — https://link.springer.com/book/10.1007/978-3-642-01039-2
- Doignon, J.-P. (2014). *Learning Spaces, and How to Build Them*. — https://doi.org/10.1007/978-3-319-07248-7_1
- Cosyn, E., Uzun, H., Doble, C. & Matayoshi, J. (2021). A practical perspective on knowledge space theory: ALEKS and its data. *J. Mathematical Psychology*. — https://jmatayoshi.github.io/publications/JMP2021_KST_ALEKS_preprint.pdf | https://doi.org/10.1016/j.jmp.2021.102512
- ALEKS, *Research Behind ALEKS — Knowledge Space Theory*. — https://www.aleks.com/about_aleks/knowledge_space_theory
- Doble, C., Matayoshi, J., Cosyn, E. et al. (2019). A Data-Based Simulation Study of Reliability for an Adaptive Assessment Based on Knowledge Space Theory. *IJAIED*. — https://doi.org/10.1007/s40593-019-00176-0
- Sun, S., Else-Quest, N. M., Hodges, L. C., French, A. M. & Dowling, R. (2021). The Effects of ALEKS on Mathematics Learning in K-12 and Higher Education: A Meta-Analysis. *Investigations in Mathematics Learning*. — https://doi.org/10.1080/19477503.2021.1926194
- Fang, Y., Ren, Z., Hu, X. & Graesser, A. C. (2018). A meta-analysis of the effectiveness of ALEKS on learning. *Educational Psychology*. — https://doi.org/10.1080/01443410.2018.1495829
- IES award: Efficacy of ALEKS for Improving Student Algebra Achievement. — https://ies.ed.gov/use-work/awards/efficacy-aleks-improving-student-algebra-achievement
- Koedinger, K. R., Corbett, A. T. & Perfetti, C. (2012). The Knowledge-Learning-Instruction Framework. *Cognitive Science* 36(5), 757–798. — https://doi.org/10.1111/j.1551-6709.2012.01245.x (authors' final version: https://pact.cs.cmu.edu/pubs/KLI-KoedingerCorbettPerfetti2012-pre.pdf)
- Koedinger, K. R., Carvalho, P. F., Liu, R. & McLaughlin, E. A. (2023). An astonishing regularity in student learning rate. *PNAS*. — https://praxis-ai.com/wp-content/uploads/2023/03/An-Astoninshing-Regularity-in-Student-Learning-Rate-1.pdf
- Cen, H., Koedinger, K. & Junker, B. (2006). Learning Factors Analysis – A General Method for Cognitive Model Evaluation and Improvement. *ITS 2006*. — https://doi.org/10.1007/11774303_17
- Koedinger, K. R., Stamper, J., McLaughlin, E. & Nixon, T. (2013). Using Data-Driven Discovery of Better Student Models to Improve Student Learning. *AIED*. — https://doi.org/10.1007/978-3-642-39112-5_43
- PSLC DataShop / LearnSphere. — https://pslcdatashop.web.cmu.edu/
- Nathan, M. J., Koedinger, K. R. & Alibali, M. (2001). Expert Blind Spot: When Content Knowledge Eclipses Pedagogical Content Knowledge. — https://pact.cs.cmu.edu/pubs/2001_NathanEtAl_ICCS_EBS.pdf
- Nathan, M. J. & Petrosino, A. (2003). Expert Blind Spot Among Preservice Teachers. *AERJ* 40(4). — https://doi.org/10.3102/00028312040004905
- Scheines, R., Silver, E. & Goldin, I. (2014). Discovering Prerequisite Relationships among Knowledge Components. *EDM 2014*. — https://www.stat.cmu.edu/~brian/nynke/726-2021/week06/HCI%20prereq%20discovery/ScheinesSilverGoldin-EDM2014.pdf
- Vuong, A., Nixon, T. & Towle, B. (2011). A Method for Finding Prerequisites Within a Curriculum. *EDM 2011*, 211–216. *(primary PDF not retrievable; cited via Scheines et al. 2014)*
- Roy, S., Madhyastha, M., Lawrence, S. & Rajan, V. (2019). Inferring Concept Prerequisite Relations from Online Educational Resources (PREREQ). arXiv:1811.12640 — https://arxiv.org/abs/1811.12640
- Prerequisite Structure Discovery in Intelligent Tutoring Systems. arXiv:2402.01672 — https://arxiv.org/abs/2402.01672
- Inferring Prerequisite Knowledge Concepts in Educational Knowledge Graphs. arXiv:2509.05393 — https://arxiv.org/abs/2509.05393
- Tatsuoka, K. K. (2009). *Cognitive Assessment: An Introduction to the Rule Space Method*. Routledge.
- Leighton, J. P., Gierl, M. J. & Hunka, S. M. (2004). The Attribute Hierarchy Method for Cognitive Assessment. *J. Educational Measurement*. — https://doi.org/10.1111/j.1745-3984.2004.tb01163.x
- de la Torre, J. & Chiu, C.-Y. (2016). A General Method of Empirical Q-matrix Validation. *Psychometrika*. — https://doi.org/10.1007/s11336-015-9467-8
- Nájera, P. et al. (2020). Improving Robustness in Q-Matrix Validation Using an Iterative and Dynamic Procedure. — https://pmc.ncbi.nlm.nih.gov/articles/PMC7383688/
- Liu, J., Xu, G. & Ying, Z. Data-driven learning of Q-matrix. — https://sites.stat.columbia.edu/jcliu/paper/PsyMeth4Name.pdf
- Better Model, Worse Predictions: The Dangers in Student Model Comparisons. *AIED 2021*. — https://doi.org/10.1007/978-3-030-78292-4_40
- Stahl, C. & Hockemeyer, C. *Knowledge Space Theory* (R package `kst` vignette). — https://cran.r-project.org/web/packages/kst/
