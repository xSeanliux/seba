# Teaching Highly Abstract Technical Subjects 1:1 — Research Report

**Sourcing note:** several primary PDFs (Sfard & Linchevski, Leinster, Fong & Spivak, Riehl, Atkinson/Renkl/Merrill, Kapur & Roll, Zazkis & Chernoff) would not parse or returned 403/402; claims from those are taken from abstracts, publisher pages, and secondary summaries and are marked where the distinction matters. Everything below is cited with a URL.

---

## 1. Advanced Mathematical Thinking: what the cognitive theories say about ORDER

### 1.1 Tall & Vinner (1981) — concept image vs concept definition

**Claim.** The *concept image* is "the total cognitive structure that is associated with the concept, which includes all the mental pictures and associated properties and processes," built over years of varied experience. It need not be globally coherent, and may conflict with the formal *concept definition*. The *evoked* concept image is the portion activated in a given moment — so a learner can hold mutually contradictory sub-images and never notice, because different contexts evoke different parts. A *potential conflict factor* becomes actual *cognitive conflict* only when two parts are evoked simultaneously.
[Tall & Vinner 1981, *Educational Studies in Mathematics* 12:151–169](https://link.springer.com/article/10.1007/BF00305619) · [full text PDF](http://homepages.math.uic.edu/~bshipley/Tall_David.pdf) · [summary](https://en.wikipedia.org/wiki/Concept_image_and_concept_definition)

**Implication for order.** A definition stated first does not create a concept image; it just adds a memorized string that the learner's pre-existing (often wrong) image will overrule under pressure. The definition's job is to *discipline* an image that already exists.

**LLM-tutor implication.** Never open a concept with its definition alone. Before stating "a functor is…", the learner must already have two or three things they'd call functor-like. And crucially: **conflicting parts of a learner's image must be co-evoked in a single question** to surface. "Is the free-group construction a functor? Is the center-of-a-group construction a functor?" placed side by side is the mechanism; asking them a week apart is not.

### 1.2 Dubinsky's APOS — action → process → object → schema

**Claim.** Concepts are built by *interiorizing* repeated actions into a process, then *encapsulating* the process into a static object that can itself be acted on; objects organize into schemas, which are *thematized* into objects at the next level. Mechanisms: interiorization, coordination, reversal, encapsulation, thematization.
[Arnon, Cottrill, Dubinsky et al., *APOS Theory* (Springer 2014)](https://link.springer.com/chapter/10.1007/978-1-4614-7966-6_2)

**Claim (pedagogy).** Dubinsky's operationalization is the **ACE cycle**: *Activities* (students build the object computationally — in abstract algebra, writing it in ISETL, a set-theoretic language whose syntax is near-identical to math notation, so programming overhead is minimal), then *Classroom discussion*, then *Exercises* to consolidate. Building the object as executable code forces encapsulation, because you cannot write a program over a process you only half-have.
[Dubinsky & Leron, *Learning Abstract Algebra with ISETL*](https://www.amazon.com/Learning-Abstract-Algebra-Mathematical-Systems/dp/0387941045) · [ACE cycle study](https://files.eric.ed.gov/fulltext/EJ1329228.pdf)

**LLM-tutor implication.** The failure mode in category theory is asking learners to act *on* an object they only hold as a process. "Natural transformation" is an object whose constituents (functors) are themselves encapsulated processes. If the learner still has to *unroll* "functor" step-by-step to think about it, they cannot hold a natural transformation. Diagnostic: ask them to do something *to* a functor (compose two, ask whether functors between fixed categories form a category). If that stalls, the level above is premature. For a text-based tutor, the ISETL move translates to: **have the learner write the construction in code** (Haskell/Python/pseudocode) or as an explicit finite table, which is checkable and forces total specification.

### 1.3 Sfard — operational precedes structural; reification is hard and discontinuous

**Claim.** Mathematical notions can be conceived operationally (as processes) or structurally (as objects); historically and individually, **the operational conception precedes the structural**, and the transition (reification) is a genuine ontological leap, not a smooth accumulation. Sfard & Linchevski document reification's "gains and pitfalls" in algebra: the same expression must be read as *a process to carry out* and *an object to manipulate*, and learners get stuck at the pseudo-structural stage where they manipulate symbols with no object behind them. "Process before object" describes each individual cycle, which then becomes the base of the next level.
[Sfard & Linchevski 1994, *ESM* 26:191–228](https://link.springer.com/article/10.1007/BF01273663) · [PDF](http://academic.sun.ac.za/mathed/174/GainsAndPitfalls.pdf) *(claims from abstract + secondary summary; PDF did not parse)*

**LLM-tutor implication.** Category theory is a tower of reifications: morphism → functor (morphism of categories) → natural transformation (morphism of functors) → adjunction/modification. Each level requires the previous to be reified. The pseudo-structural failure is exactly the student who can chase a diagram symbolically and cannot say what any node *is*. Detect it by demanding a non-symbolic answer: "what does this natural transformation *do*, in Set, to the element 3?"

### 1.4 Concrete synthesis for sequencing

The three theories converge: **operational experience → varied instances → felt need → definition → object-level manipulation → next level.** The definition is a *late* artifact within each cycle, not an opening move.

---

## 2. Example-first vs definition-first

### 2.1 Michener (1978) — a taxonomy of what mathematical knowledge is made of

**Claim.** Mathematical knowledge decomposes into three interacting *spaces*: **examples-space, results-space, concepts-space**, and understanding involves navigation *between* them, not mastery of one. Examples subdivide into four epistemologically distinct types:
- **start-up examples** — motivate the basic definitions, set up intuition in a new subject;
- **reference examples** — a small set of standard instances referred to repeatedly throughout the theory;
- **model examples** — paradigmatic/generic, carrying the general case;
- **counterexamples** — show a conjecture false, and show why hypotheses in theorems are load-bearing.

Every example has *dual items*: the concepts/results needed to construct it, and the concepts/results it motivates.
[Michener 1978, *Cognitive Science* 2(4):361–383](https://onlinelibrary.wiley.com/doi/abs/10.1207/s15516709cog0204_3) · [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0364021378800524) · [taxonomy restated in Antonini et al.](https://link.springer.com/article/10.1007/s11858-011-0334-5)

**LLM-tutor implication.** This is the single most directly implementable finding. A tutor should maintain, per concept, an explicit slot for each of the four example types, and should *not* treat "gave an example" as one undifferentiated act. For category theory the reference-example set is small and should be fixed early and reused relentlessly: **Set, a poset/preorder as a category, a monoid as a one-object category, Grp/Vect, and a small finite category drawn as a graph**. Reference examples earn their power by recurrence — the tutor must return to the *same* examples across concepts rather than showing a fresh one each time.

### 2.2 Watson & Mason — example spaces and learner-generated examples

**Claim.** A *personal example space* is "the set of mathematical objects and construction techniques that a learner has access to as examples of a concept while working on a given task" — distinct from the textbook's conventional example space, and it is structured, situational, and dynamic. The central pedagogical move is transferring the *responsibility for producing examples* from teacher to learner; doing so transforms and extends the learner's knowledge structure rather than merely testing it. Tasks: "give me an example of…; and another; and another that's as different as possible; and one that satisfies the definition but that you think I wouldn't expect."
[Watson & Mason, *Mathematics as a Constructive Activity: Learners Generating Examples* (Routledge 2005)](https://www.routledge.com/Mathematics-as-a-Constructive-Activity-Learners-Generating-Examples/Watson-Mason/p/book/9780805843446) · [Open Research Online record](https://oro.open.ac.uk/792) · [Goldenberg & Mason, "Shedding light on and with example spaces", *ESM* 2008](https://link.springer.com/article/10.1007/s10649-008-9143-3) · [Sinclair et al., "The structuring of personal example spaces"](https://www.sciencedirect.com/science/article/abs/pii/S0732312311000277) · [Extending example spaces, PME 2002 PDF](http://www.pmtheta.com/uploads/4/7/7/8/47787337/extending_example_spaces_pme_2002.pdf)

**LLM-tutor implication.** "And another, as different as possible" is a near-free, text-native, high-yield prompt, and it doubles as **assessment**: the learner's first three examples reveal the shape and poverty of their example space. If a learner's only functor examples are forgetful functors, their image of "functor" is "throw away structure" — a diagnosable defect invisible to a correctness-only check.

### 2.3 Generic examples (Mason & Pimm 1984)

**Claim.** A generic example is a particular case "presented in such a way as to bring out its intended role as the carrier of the general" — seeing the general in the particular. Generic arguments have strong explanatory power and can function as proof; teachers produce three grades of them, from example-based arguments dressed in generic language up to complete generic examples.
[Mason & Pimm 1984, *ESM* 15:277–289](https://link.springer.com/article/10.1007/BF00312078) · [Role of generic examples in teachers' proving, *ESM* 2020](https://link.springer.com/article/10.1007/s10649-020-10002-3) · [When Is a Generic Argument a Proof?](https://link.springer.com/chapter/10.1007/978-3-319-70996-3_17)

**LLM-tutor implication.** For category theory this licenses the **"prove it in Set, then check nothing you used was Set-specific"** move as a legitimate pedagogical step, provided the tutor explicitly marks the generic status and then runs the audit: "which lines of that argument used elements? Replace each with a generalized element $1 \to X$ or a universal property." That audit *is* the lesson.

### 2.4 Nonexamples, boundary examples, counterexamples

**Claim (variation theory).** Learners discern a feature only when it *varies* against an invariant background. Marton's patterns: **contrast** (example vs nonexample defines what the critical aspect is not), **generalization** (same critical aspect, varying irrelevant background), **fusion** (vary two dimensions simultaneously). "Dimensions of variation" = which aspects of a procedure/object are permitted to change.
[Marton & Booth 1997 / Marton 2015, summarized](https://files.eric.ed.gov/fulltext/ED573288.pdf) · [Mason, "Variation and mathematical structure"](http://www.pmtheta.com/uploads/4/7/7/8/47787337/variation_2007.pdf) · [Use of variation theory in teaching mathematics](https://files.eric.ed.gov/fulltext/EJ1442215.pdf)

**Claim (Zazkis & Chernoff).** A *pivotal example* creates cognitive conflict; when it also resolves it, it is a *bridging example*. Critically, **a counterexample only convinces to the extent it lies within the learner's example space** — an exotic counterexample outside that space is dismissed as pathological rather than accepted as refutation.
[Zazkis & Chernoff 2008, "What makes a counterexample exemplary?", *ESM* 68(3):195–208](https://link.springer.com/article/10.1007/s10649-007-9110-4) · [PDF](https://opencourses.uoa.gr/modules/document/file.php/MATH128/%CE%94%CE%B9%CE%B4%CE%B1%CE%BA%CF%84%CE%B9%CE%BA%CF%8C%20%CF%80%CE%B1%CE%BA%CE%AD%CF%84%CE%BF/%CE%86%CF%81%CE%B8%CF%81%CE%B1%20%CE%B3%CE%B9%CE%B1%20%CF%80%CE%B1%CF%81%CE%BF%CF%85%CF%83%CE%AF%CE%B1%CF%83%CE%B7/Arthra-Ylika%20gia%20deyteri%20ergasia%202015-2016/Paradeigmata/What%20makes%20a%20counterexample%20exemplary%20(Zazkis,%20Chernoff).pdf) *(from abstract + secondary summary)* · [Cognitive conflict via pivotal/bridging example](https://www.researchgate.net/publication/238734117_Cognitive_Conflict_and_its_resolution_via_pivotalbridging_example)

**LLM-tutor implication — important and non-obvious.** The tutor's instinct is to refute an overgeneralization with the sharpest available counterexample. Zazkis & Chernoff say pick the *nearest* one instead. If a learner believes every functor has a left adjoint, refuting with a large-cardinal/set-theoretic pathology fails; refuting inside a poset they already built ("here's a monotone map with no left adjoint, on a 3-element poset") lands. **Counterexamples must be drawn from the learner's already-established reference examples.**

---

## 3. Worked examples, fading, expertise reversal, self-explanation

### 3.1 Worked-example effect and its fading

**Claim.** For novices, studying worked examples beats equivalent problem-solving practice: attention goes to the solution structure rather than to means-ends search. Fading — progressively omitting steps from complete worked example → completion problem → full problem — bridges to independent solving.
[Salden, Aleven, Renkl, Schwonke, "Expertise reversal effect and worked examples in tutored problem solving"](http://www.cee.uma.pt/ron/Salden%20et%20al.%20-%20The%20Expertise%20Reversal%20Effect%20and%20Worked%20Examples.pdf) · [Atkinson, Renkl & Merrill 2003, "Transitioning from studying examples to solving problems"](https://mrbartonmaths.com/resourcesnew/8.%20Research/Making%20the%20most%20of%20examples/Fading%20out%20and%20Prompts.pdf) *(PDF did not parse; claims from abstract/secondary)* · [Recent replication/extension](https://www.tandfonline.com/doi/full/10.1080/01443410.2023.2273762)

### 3.2 Expertise reversal

**Claim.** "A reversal in the relative effectiveness of instructional methods as levels of learner knowledge in a domain change" (Kalyuga, Renkl). Support that helps novices becomes redundant and then *harmful* for more advanced learners, who do better with plain problem-solving; the redundant explanation costs working memory to integrate with existing schemas.
[Kalyuga & Renkl 2009, *Instructional Science* 37:209–216](https://link.springer.com/article/10.1007/s11251-009-9102-0) · [Cambridge Handbook of Expertise, ch. 40](https://www.cambridge.org/core/books/cambridge-handbook-of-expertise-and-expert-performance/cognitive-load-and-expertise-reversal/03F656FD334F23214426ACB4118FEBF9) · [Extension to ill-structured tasks (legal reasoning)](https://www.sciencedirect.com/science/article/abs/pii/S0361476X12000677)

**LLM-tutor implication — the strongest argument for 1:1 tutoring existing at all.** Expertise is *per-concept*, not per-learner. A learner may be expert on limits and novice on adjunctions in the same session; the tutor must fade support **per topic**, not globally, and must be willing to fade *back in* when a new concept starts. A tutor that keeps explaining fully to a learner who has got it is not being thorough — it is actively degrading learning.

### 3.3 Self-explanation

**Claim.** Chi et al. (1989): benefit from worked examples depends on how well learners explain the solution's rationale to themselves. High self-explainers solved novel problems correctly ~82% of the time vs ~46% for low self-explainers. Renkl (1997) replicated; Renkl, Stark, Gruber & Mandl (1998) showed a *short training* in self-explaining (informing learners it matters + modeling it) raised self-explanation frequency and near-transfer performance — i.e. it is trainable, not a fixed trait.
[Chi, Bassok, Lewis, Reimann & Glaser 1989, *Cognitive Science* 13(2):145–182](https://onlinelibrary.wiley.com/doi/abs/10.1207/s15516709cog1302_1) · [Chi et al. 1994, "Eliciting self-explanations improves understanding"](https://www.semanticscholar.org/paper/Eliciting-Self-Explanations-Improves-Understanding-Chi-Leeuw/dd869eeb2e13264d47eb0d150d05912b7afd9aba) · [Renkl, "Learning from worked-out examples via self-explanations: how it can (not) be fostered"](https://www.researchgate.net/publication/228741425_Learning_from_worked-out_examples_via_self-explanations_How_it_can_not_be_fostered) · [Boundary conditions on when self-explanation helps](https://link.springer.com/article/10.3758/s13423-016-1079-5)

**Caveat with teeth.** Renkl's "how it can (not) be fostered" and the *Psychonomic Bulletin & Review* constraints paper both find self-explanation is *not* universally beneficial and that heavy instructional explanation can **substitute** for self-explanation and suppress it.
[Instructional explanations support learning by self-explanations — but can displace it](https://www.sciencedirect.com/science/article/abs/pii/S0959475201000305)

**LLM-tutor implication — the sharpest warning in this report for an LLM.** An LLM's default failure mode is *over-explaining*, and the research says a good instructional explanation given too early **crowds out the self-explanation that produces the learning**. The prompt "why does this step work?" asked *before* the tutor answers it is worth more than a better paragraph.

---

## 4. Proof: comprehension and construction

### 4.1 Selden & Selden — proof frameworks and unpacking

**Claim.** A *proof framework* is "a representation of the top-level logical structure of a proof, which does not depend on a detailed knowledge of the mathematical concepts, but is rich enough to allow the reconstruction of the statement being proved." It is written *before* any mathematical content: for $\forall \varepsilon > 0\, \exists \delta$…, you write the first and last lines and the quantifier skeleton first. The Seldens distinguish three structures: hierarchical, the linear path an idealized prover would take, and the split into **"rhetorical" (formal/structural) vs "problem-solving" parts**.
[Selden & Selden, "Unpacking the logic of mathematical statements", *ESM* 1995](https://philpapers.org/archive/SELUTL.pdf) · [Validation of proofs as a type of reading, TN Tech TR-2015-4](https://www.tntech.edu/cas/pdf/math/techreports/TR-2015-4.pdf) · [Teaching proving by coordinating aspects of proofs with students' abilities](https://philarchive.org/rec/SELTPB) · [Selden's retrospective, TR-2023-1](https://www.tntech.edu/cas/pdf/math/techreports/TR-2023-1.pdf)

**Claim (severity).** Undergraduates succeeded at unpacking the logical structure of *simplified informal* calculus statements only **8.5%** of the time, and of *actual textbook* statements **5%** of the time — the Seldens infer such students cannot reliably construct or validate proofs at all.

**LLM-tutor implication.** Separate the rhetorical from the problem-solving part *explicitly and always*. In category theory the rhetorical part is huge and highly stereotyped — "to show $F \dashv G$, exhibit a bijection $\mathrm{Hom}(FA,B) \cong \mathrm{Hom}(A,GB)$ natural in $A$ and $B$; so fix $A, B$, define $\varphi$, define $\psi$, show mutually inverse, show naturality in each variable" — and it can be *dictated to the learner as a template* at zero cost to the real learning, which lives in defining $\varphi$. A tutor should write the framework, then hand the learner the holes. This is exactly a **completion problem** (§3.1), arrived at from a completely independent literature.

### 4.2 Weber & Mejía-Ramos — how mathematicians actually read proofs

**Claim.** In interview and survey studies (incl. 118 practicing mathematicians), mathematicians read published proofs mainly **to gain insight, not to check correctness**; they appeal to the reputation of author/journal; they shift repeatedly between *zooming out* (high-level ideas, modular structure) and *zooming in* (line-by-line on the parts that look problematic); they **apply steps to specific examples** as a comprehension technique; and many do not do a full line-by-line check even when refereeing.
[Weber & Mejía-Ramos 2011, "Why and how mathematicians read proofs: an exploratory study", *ESM*](https://www.researchgate.net/publication/226580934_Why_and_how_mathematicians_read_proofs_An_exploratory_study) · [Mejía-Ramos & Weber 2014, survey study, *ESM* 85:161–173](https://link.springer.com/article/10.1007/s10649-013-9514-2) · [Weber & Mejía-Ramos, "Mathematics majors' beliefs about proof reading", *IJMEST*](https://sites.math.rutgers.edu/~jpmejia/files/Weber%20&%20Mejia-Ramos%20(iJMEST).pdf) · [Inglis & Alcock, "On mathematicians' different standards when evaluating elementary proofs", *Topics in Cognitive Science*](https://onlinelibrary.wiley.com/doi/10.1111/tops.12019)

**Claim (assessment model).** Mejía-Ramos, Fuller, Weber, Rhoads & Samkoff (2012) give a **seven-dimension, non-hierarchical** model of proof comprehension in two families:
- **Local (3):** meaning of terms and statements; logical status of statements and the proof framework; justification of claims.
- **Holistic (4):** summarizing via high-level ideas; identifying the modular structure; transferring the general ideas/methods to another context; **illustrating the proof with examples**.

[Mejía-Ramos et al. 2012, *ESM* 79:3–18](https://eric.ed.gov/?id=EJ948400) · [Rutgers record](https://www.researchwithrutgers.com/en/publications/an-assessment-model-for-proof-comprehension-in-undergraduate-math/) · [Validated comprehension tests](https://www.tandfonline.com/doi/abs/10.1080/14794802.2017.1325776) · [Instructional intervention, *JMB* 2015](https://www.sciencedirect.com/science/article/abs/pii/S0732312315000413) · [Proof summaries & comparative judgement, *ESM* 2020](https://link.springer.com/article/10.1007/s10649-020-09984-x) · [Proof comprehension study, HAL](https://hal.science/hal-02398493/document)

**LLM-tutor implication.** This is a ready-made, directly implementable **question bank schema**. After any proof, the tutor has seven distinct comprehension probes, and the holistic four are the ones students never get asked and never do spontaneously. "Summarize this proof in two sentences," "which parts are independent modules?", "instantiate the proof for the poset case," "where else does this method apply?" — four questions, generated mechanically, targeting exactly the expert behaviors. Also: the tutor should *model* zoom-out-then-zoom-in reading rather than presenting proofs linearly, because the linear presentation teaches the novice reading strategy.

### 4.3 Weber & Alcock — semantic vs syntactic proof production

**Claim.** A **syntactic** proof production draws inferences by logically permissible manipulation of symbolic formulae; a **semantic** one uses *instantiations* of the concepts to guide which formal inferences to draw. Case studies (group theory, real analysis) show doctoral students routinely instantiate; undergraduates often cannot, having no instantiations to reason with, and are stuck in pure syntax.
[Weber & Alcock 2004, *ESM* 56:209–234](https://link.springer.com/article/10.1023/B:EDUC.0000040410.57253.a1) · [PDF](https://www.academia.edu/58975810/Semantic_and_Syntactic_Proof_Productions) · [Weber 2009 reply to Alcock & Inglis](https://eric.ed.gov/?id=EJ869405) · [Doctoral students' use of examples in evaluating/proving conjectures, *ESM* 2009](https://link.springer.com/article/10.1007/s10649-008-9149-x) · [Mathematicians' vs students' use of examples for conjecturing and proving, *JMB* 2017](https://www.sciencedirect.com/science/article/abs/pii/S0732312317300238)

**LLM-tutor implication — the deep justification for example-first in category theory.** The reason a learner cannot *construct* a categorical proof is usually not logical incompetence; it is an empty referential domain — no instantiation to think in. This makes §2's example-space work a **prerequisite for proof work**, not a parallel nicety. Diagram chasing without instantiation is the pseudo-structural failure mode of §1.3.

### 4.4 Weber's RACUM — how experts learn new math

**Claim.** RACUM (Resources and Acts for Constructing and Understanding Mathematics): mathematicians learn unfamiliar material by having a stock of mathematical resources and strategically coordinating them, in a "complex interaction between rigorous and intuitive thought."
[Weber, "How do mathematicians learn math?"](https://www.researchgate.net/publication/226344097_How_do_mathematicians_learn_math_Resources_and_acts_for_constructing_and_understanding_math) · [Weber 2012, mathematicians' perspectives on pedagogical practice](https://sites.math.rutgers.edu/~jpmejia/files/Weber_(2012IJMEST).pdf) · [Stylianides & Weber, Compendium chapter on teaching/learning proof](https://sites.math.rutgers.edu/~jpmejia/files/Stylianides_Weber_(Compedium).pdf)

---

## 5. Category theory pedagogy: what the good texts actually do

Reading the design of the canonical introductions, the recurring strategies are remarkably consistent, and each maps onto a research finding above.

**Lawvere & Schanuel, *Conceptual Mathematics*.** Applies categories to *elementary* mathematics; presupposes no specific field; develops directed graphs and discrete dynamical systems from scratch as its ambient categories; largely synthetic rather than analytic; dialogue/session format with student-voice objections.
[Archive.org full text](https://archive.org/details/F.WilliamLawvereStephenH.SchanuelConceptualMathematicsAFirstIntroductionToCatego) · [PhilPapers record](https://philpapers.org/rec/LAWCMA)
→ *This is Michener's "start-up examples" done deliberately: pick reference examples the learner can fully compute in (finite sets, graphs, dynamical systems) rather than examples that presuppose a math major.*

**Riehl, *Category Theory in Context*.** Preface opens with **"sample corollaries"** — striking payoffs stated before any machinery (e.g. in a path-connected space any choice of basepoint gives an isomorphic fundamental group; a continuous endomorphism of a disk has a fixed point). Riehl says she actively solicited examples from many fields before writing and collected "as many examples of this kind as I could," structuring the book to alternate foundational concepts with concrete applications from across mathematics.
[Book PDF](https://math.jhu.edu/~eriehl/context.pdf) · [Riehl's own account, n-Category Café](https://golem.ph.utexas.edu/category/2016/11/category_theory_in_context.html)
→ *Payoff-first is the felt-need move: motivate the definition by a result the learner already wants.*

**Leinster, *Basic Category Theory*.** Explicit learner advice: not every student needs every example — "all that matters is understanding enough examples to connect new concepts with mathematics already known"; if stuck on an exercise, go back through each term and make sure you understand it fully; and **"to understand the question is very nearly to know the answer,"** since in most basic-category-theory exercises there is only one possible way to proceed. Dualization is used systematically as an exercise generator (derive coequalizer by dualizing equalizer, then compute it concretely in Set). Familiar constructions (disjoint union, direct sum) are re-expressed diagrammatically to reveal them as instances of one categorical construction. Noted as compressed and therefore tough.
[arXiv:1612.09375 (CC BY-NC-SA)](https://arxiv.org/pdf/1612.09375) *(quotes via search-result excerpts; PDF did not parse)*
→ *Two distinct rules here: (a) "unfold every term in the statement" is Selden's unpacking, in the words of a category theorist; (b) dualization is a free, infinite, self-checking exercise generator.*

**Fong & Spivak, *Seven Sketches in Compositionality*.** Seven chapters, each **pairing a concrete application (databases, electric circuits, dynamical systems, resource theories) with one categorical structure**; no prior category theory assumed; exercises embedded inline in the text rather than collected at chapter end; the book climbs from posets/preorders → monoidal preorders → categories → profunctors → monoidal categories → operads/toposes.
[arXiv:1803.05316](https://arxiv.org/abs/1803.05316) · [Cambridge edition](https://www.cambridge.org/core/books/an-invitation-to-applied-category-theory/D4C5E5C2B019B2F9B8CE9A4E9E84D6BC) · [LibreTexts full text](https://math.libretexts.org/Bookshelves/Applied_Mathematics/Seven_Sketches_in_Compositionality:_An_Invitation_to_Applied_Category_Theory_(Fong_and_Spivak))
→ ***Posets before categories* is the key structural insight.** A preorder is a category with at most one morphism per hom-set. Every categorical concept degenerates to something the learner can already picture: product → meet, coproduct → join, adjunction → Galois connection, functor → monotone map, Yoneda → "$x \le y$ iff everything below $x$ is below $y$." This gives a *complete, checkable, fully computable* instantiation of the whole theory before generality arrives.

**Baez's ACT course.** Built on *Seven Sketches*; lectures deliberately **bite-sized, one idea each**, self-contained but readable alongside the book for two views of the same material; students did nearly all the book's exercises plus a large number of extra "Puzzles"; 250+ registrants discussing in a forum.
[Course site](https://math.ucr.edu/home/baez/act_course/) · [Lecture 1](https://math.ucr.edu/home/baez/act_course/lecture_1.html) · [Announcement](https://johncarlosbaez.wordpress.com/2018/03/26/seven-sketches-in-compositionality/) · [2023 lecture notes](https://johncarlosbaez.wordpress.com/2023/09/28/lectures-on-applied-category-theory/)
→ *One idea per unit + immediate puzzle. Directly imitable in a text tutor's turn structure.*

**Milewski, *Category Theory for Programmers*.** Argues category theory suits programmers because "it deals with the kind of structure that makes programs composable"; "composition is at the very root of category theory… and I will argue strongly that composition is the essence of programming." Explicitly informal — a "butcher's knife, with which I will butcher math to make it more palatable to programmers" — while committing to sound theory behind informal arguments. Gives examples in **both C++ and Haskell** deliberately, to refute the idea that CT only applies to functional programming.
[Preface](https://bartoszmilewski.com/2014/10/28/category-theory-for-programmers-the-preface/)
→ *Anchoring the abstraction in a domain where the learner already has thousands of instantiations (their own code) is the fastest possible way to populate a referential domain (§4.3).*

**Eugenia Cheng, *The Joy of Abstraction*.** Advocates a slower, explanatory approach focused on the *principles and choices* involved rather than speed and memorization; builds category theory rigorously for readers without a math-major background; famous for everyday analogies (food/baking). Part I builds abstraction-as-a-practice before Part II does formal category theory.
[Book](https://www.amazon.com/Joy-Abstraction-Exploration-Category-Theory/dp/1108477224) · [eugeniacheng.com](https://eugeniacheng.com/) · [Quanta interview](https://www.quantamagazine.org/is-there-math-beyond-the-equal-sign-20230322/)

**Synthesis of recurring category-theory-specific strategies:**
1. **Many concrete instantiations before the abstraction** (all six texts).
2. **A degenerate-but-complete model first** — posets/preorders (Fong–Spivak), monoids-as-one-object-categories, finite categories drawn as graphs.
3. **"Check it in Set first"** — instantiate the general claim in the most familiar category, then audit for element-based reasoning.
4. **Diagrams as reasoning tools, not illustrations** — re-express a known construction diagrammatically to reveal it as an instance of the general one (Leinster).
5. **Dualization as an exercise generator** — every definition yields a free exercise (state the dual, then compute it concretely).
6. **Payoff-first framing** — sample corollaries before machinery (Riehl).
7. **One idea per unit, immediately followed by a puzzle** (Baez).
8. **Ground in the learner's existing domain** — programming (Milewski), applications (Fong–Spivak), everyday life (Cheng).

---

## 6. Known misconception / difficulty inventories

### 6.1 Abstract algebra (well documented)

**Claim.** Cosets, normality and quotient groups are the hardest cluster; **quotient group is the single most challenging fundamental group-theoretic concept at introductory level**; cosets obstruct because students cannot visualize them; only about a third of participants could successfully construct quotients in a group as small as $D_3$. Group isomorphism carries its own misconception cluster. Difficulty with group theory correlates with difficulty constructing proofs, and indirect proofs are markedly harder than direct ones. Most of this work is framed in APOS.
[Asiala, Dubinsky, Mathews, Morics & Oktaç, "Development of students' understanding of cosets, normality and quotient groups", *JMB* 1997](https://www.academia.edu/27961571/Development_of_students_understanding_of_cosets_normality_and_quotient_groups) · [Leron, Hazzan & Zazkis, "Students' conceptions and misconceptions of group isomorphism"](https://www.academia.edu/31452718/Students_conceptions_and_misconceptions_of_group_isomorphism) · [Dubinsky, Dautermann, Leron & Zazkis, "On learning fundamental concepts of group theory", *ESM* 1994](https://link.springer.com/article/10.1007/BF01273732) · [Recent survey of abstract algebra difficulties, *Cogent Education* 2024](https://www.tandfonline.com/doi/pdf/10.1080/2331186X.2024.2355400)

**Pattern.** The hard concepts are precisely those where **an object at level $n$ becomes an element at level $n+1$** — a coset is a set that must be treated as a point; a quotient group is a group whose elements are sets. That is Sfard's reification / APOS encapsulation, exactly.

### 6.2 Topology

**Claim.** Students misunderstand not topology but its substrate: sets, families of sets, intersections within families. Many were **not even aware that a topological structure is a family of sets**. Students could recite the definition of a topological structure but could not apply it to a given example. Compactness is hard specifically because it is defined purely via open covers rather than any intuitive notion of size or finiteness. Recommended design principles emphasize production of examples and investigation of variations and invariants.
[Do Students Really Understand Topology in the Lesson?](https://files.eric.ed.gov/fulltext/ED510704.pdf) · [Digital experiences of mathematical cognitive functions in learning basic general topology, *IJRUME* 2024](https://link.springer.com/article/10.1007/s40753-024-00245-3)

**Note the diagnostic signature:** "can state the definition, cannot apply it to an instance" is the definition-first failure predicted by Tall & Vinner.

### 6.3 Category theory (thin formal literature — inventory below is inferred, flagged as such)

There is **no substantial peer-reviewed misconception inventory for category theory**; my searches turned up expository accounts and course notes, not empirical studies. What follows is assembled from expositors' repeated remarks plus by-analogy prediction from §6.1–6.2, and should be treated as a hypothesis list a tutor can *test*, not established findings.

- **Natural transformation.** "Natural transformations don't seem very natural when you first see the definition." Note the historical inversion: Eilenberg–Mac Lane invented categories *in order to* define functors *in order to* define natural transformations — the opposite of the modern teaching order. Predicted errors: forgetting the components form a *family indexed by objects*; treating the naturality square as decoration rather than the content; not seeing that in CS terms these are parametrically polymorphic functions (i.e. the learner has instantiations and doesn't know it).
[John D. Cook](https://www.johndcook.com/blog/2017/03/16/natural-transformations/) · [Category Theory Illustrated](https://abuseofnotation.github.io/category-theory-illustrated/11_natural_transformations/) · [Wisconsin course notes](https://pages.cs.wisc.edu/~jcyphert/categoryTheoryNotes/basics/3_NaturalTransformations.pdf)
- **Functor.** Predicted: image is "forgetful functor" only (impoverished example space); missing that the action on *morphisms* is the substance; missing functoriality as a *condition to check*, not a fact.
- **Universal property / limits.** Predicted: existence remembered, **uniqueness clause dropped** — the "unique factorization" is where all the power lives; treating a limit as a construction rather than a characterization; failing to see two constructions as the same object because they're not literally equal.
- **Adjunction.** Predicted: naturality of the hom-bijection ignored; unit/counit and hom-set formulations not recognized as the same thing; "free ⊣ forgetful" memorized as a slogan without a check.
- **Yoneda.** Predicted: the pseudo-structural failure par excellence — the proof is a short diagram chase that can be executed with zero object-level understanding. The tutor must demand the instantiation.
- **The general one.** In a subject where *everything* is defined up to isomorphism by universal properties, learners import equality intuitions from set theory.

---

## 7. Doing vs reading; deliberate practice

**Claim.** Meta-analytic and randomized evidence supports **spacing** and **retrieval practice** in mathematics; benefits of spacing shown in several randomized studies including three with college mathematics students. Spacing may benefit *conceptual* knowledge more than procedural. **Interleaving** improves learning ~30% over blocked practice, and works through two mechanisms: juxtaposing different problem kinds forces *strategy selection*, and same-kind problems become spaced.
[Meta-analytic review of spacing and retrieval practice for mathematics learning, *Educ Psych Review* 2025](https://link.springer.com/article/10.1007/s10648-025-10035-1) · [Rohrer, "Interleaved practice improves mathematics learning"](https://files.eric.ed.gov/fulltext/ED557355.pdf) · [Rohrer & Hartwig practitioner summary](https://www.unh.edu/teaching-learning-resource-hub/sites/default/files/media/2023-06/itow-spaced-and-interleaved-mathematics-practice-rohrer-hartwig.pdf) · [MIT summary](https://openlearning.mit.edu/mit-faculty/research-based-learning-findings/spaced-and-interleaved-practice)

**LLM-tutor implication.** The strategy-selection mechanism is the important one for category theory. Blocked practice ("here are six limit problems") teaches "apply the limit recipe." Interleaved practice ("is this a limit, a colimit, an adjunction, or none?") teaches recognition, which is the actual skill. A tutor with session memory should interleave across concepts and space revisits — and note that **interleaving is a form of un-cueing**, i.e. exactly the support-fading of §3.2.

---

## 8. Analogy and multiple representations

**Claim.** Multiple representations are distinct encodings of the same mathematical entity, used to develop and communicate different features and the connections between them.
[Multiple representations in mathematics education](https://en.wikipedia.org/wiki/Multiple_representations_(mathematics_education))

**Claim (what makes analogy work).** Comparison facilitates transfer via **structural alignment and mapping**; providing *multiple analogs* and explicitly asking learners to map the structural correspondences between them substantially increases spontaneous transfer. Learners left to induce the mapping alone frequently fail to transfer at all.
[Richland & Simms / Richland 2010, "Learning by analogy: discriminating between potential analogs"](https://learninglab.uchicago.edu/Publications_files/16%20Richland%20(2010)%20Learning%20by%20analogy.pdf) · [Analogical transfer in problem solving](https://www.researchgate.net/publication/288047613_Analogical_Transfer_in_Problem_Solving)

**Claim (the risk).** Negative transfer is real and documented even in young children's analogical problem solving. Learners interpret *structure through surface context*: given 12 tulips and 3 vases they divide, because that is what one does with flowers and vases — the context dictates the operation regardless of the mathematics.
[Positive and negative transfer in analogical problem solving by 6-year-olds, *Cognitive Development*](https://www.sciencedirect.com/science/article/abs/pii/S0885201489900312) · [Misanalogical construction in students' cognitive conflict](https://www.iejme.com/download/the-misanalogical-construction-of-undergraduate-students-in-solving-cognitive-conflict-3961.pdf)

**LLM-tutor implication.** LLMs generate fluent analogies effortlessly and this is a liability. Two mitigations, both from the research: (a) give **two structurally different analogs** and require the learner to map between them, which cancels the surface features that are not shared; (b) state the analogy's **breakdown point explicitly** — an unmarked analogy becomes a permanent, wrong part of the concept image (§1.1) and, since it is never co-evoked with the definition, is never detected.

---

## 9. Productive failure

**Claim.** Sinha & Kapur (2021) meta-analyzed **53 studies / 166 experimental comparisons / >12,000 participants**: problem-solving *before* instruction beat instruction-first on **conceptual understanding and transfer (Cohen's d ≈ 0.36)** without harming procedural knowledge. Effects were stronger for secondary and undergraduate students than for primary.
[Sinha & Kapur 2021, *Review of Educational Research*](https://journals.sagepub.com/doi/10.3102/00346543211019105) · [Phys.org summary](https://phys.org/news/2021-09-productively-wiser.html)

**Claim (design, not discovery).** Productive failure is **not** discovery learning: it *critically incorporates a structured instruction phase* — the learner grapples with a challenging task, and the design culminates in explicit teaching of the canonical solution. The generation phase produces failed/suboptimal representations whose *contrast* with the expert solution is the instructional content.
[Kapur & Roll, "Productive Failure"](https://boldscience.org/wp-content/uploads/2025/04/Productive-Failure.pdf) *(from abstract/secondary; PDF did not parse)* · [Kapur, "Productive failure in learning from generation and invention activities", *Instructional Science* 2012](https://link.springer.com/article/10.1007/s11251-012-9235-4)

**LLM-tutor implication — and the tension to manage.** Productive failure says *generate before instruction*; the worked-example effect (§3.1) says *study examples before problem-solving*. These are reconcilable and the reconciliation is the design: **PF's generation phase targets the concept (invent a way to compare structures), the worked-example effect governs the procedure (how to verify functoriality)**. Concepts get attempted first; procedures get demonstrated first. Also: PF *requires the consolidation phase*. An LLM tutor that lets a learner struggle and then moves on has implemented unproductive failure. The struggle is only worth its cost if it is followed by explicit contrast between what the learner produced and the canonical answer — and that contrast is where the tutor's explanation belongs, which also resolves the over-explaining problem in §3.3 by relocating the explanation rather than deleting it.

---

## 10. Directly implementable tutoring rules

For an LLM tutoring abstract mathematics 1:1 in text. Each rule names the finding it comes from.

1. **Never open with the definition.** Before stating a definition, make the learner meet at least three instances and one non-instance. The definition arrives as a *summary of a felt pattern*, not as a premise. (Tall & Vinner §1.1; topology "can state, cannot apply" §6.2)

2. **Fix a small set of reference examples early and reuse them across every concept.** For category theory: **Set; a poset/preorder; a monoid as a one-object category; a finite category drawn as a graph; Grp or Vect.** Resist introducing a fresh example per concept — recurrence is what makes a reference example load-bearing. (Michener §2.1)

3. **Teach the poset degeneration as a first-class parallel track.** Every concept gets stated twice: once in preorders (product = meet, adjunction = Galois connection, functor = monotone map), where everything is finite and checkable, and once in general. (Fong & Spivak §5)

4. **Run "check it in Set, then audit."** Have the learner prove/instantiate in Set, then ask: which steps used *elements*? Replace each with a universal property or generalized element. The audit is the lesson, not the Set proof. (Mason & Pimm generic examples §2.3)

5. **Ask "give me another, as different as possible"** after every concept, three times. Use the answers as *diagnosis* of example-space poverty, not just as practice. If all three functor examples are forgetful functors, that is the finding, and it dictates the next move. (Watson & Mason §2.2)

6. **Draw counterexamples from the learner's own established examples, never from pathology.** Refute an overgeneralization inside the 3-element poset they already built. A counterexample outside the learner's example space is dismissed, not accepted. (Zazkis & Chernoff §2.4)

7. **Vary one dimension at a time, then two.** Present example/nonexample pairs differing in exactly the critical feature (contrast), then fix the feature and vary everything else (generalization), then vary two features together (fusion). (Marton, variation theory §2.4)

8. **Diagnose the learner's APOS level before choosing the next concept, by asking them to act *on* the object.** "Compose these two functors." "Do functors $\mathcal{C} \to \mathcal{D}$ form a category?" If that stalls, the concept is still a process and the level above (natural transformations) is premature. Do not proceed on the evidence that they can recite the definition. (Dubinsky §1.2; Sfard §1.3)

9. **Make them build it, executably.** Have the learner write the construction as code, or as an explicit finite table of objects and arrows. Code and finite tables cannot be half-specified, so they force encapsulation and are mechanically checkable in text. (ACE/ISETL §1.2; Milewski §5)

10. **Fade support per concept, not per learner, and fade back in.** Track expertise per topic. Full worked example → completion problem (holes in a given skeleton) → bare problem. Continuing to explain fully to a learner who has got it *degrades* their learning. (Expertise reversal §3.2)

11. **Ask "why does this step work?" before answering it — every time.** The tutor's better explanation, given first, suppresses the self-explanation that produces the learning. When the learner's own explanation is wrong or thin, *then* explain. (Chi §3.3; Renkl's "how it can (not) be fostered")

12. **Split every proof into rhetorical and problem-solving parts, and hand over the framework for free.** Write the proof framework yourself ("fix $A,B$; define $\varphi:\mathrm{Hom}(FA,B)\to\mathrm{Hom}(A,GB)$; define $\psi$; show inverse; show naturality in each variable"), then have the learner fill the holes. This is a completion problem and a proof framework simultaneously. (Selden & Selden §4.1 + faded worked examples §3.1)

13. **Unpack every term in the statement before attempting a proof.** Both Selden ("unpacking the logic of informal statements": 5–8.5% success rates untrained) and Leinster ("go back through each term and make sure you understand it fully… to understand the question is very nearly to know the answer") converge here. Make it a ritual, not a hint of last resort. (§4.1, §5)

14. **After every proof, ask the four holistic comprehension questions,** which learners never ask themselves: (a) summarize it in two sentences; (b) what are its independent modules; (c) instantiate it in a reference example; (d) where else does this method apply. Then the three local ones: term meanings, logical status of each line, justification of each claim. (Mejía-Ramos et al. §4.2)

15. **Model expert reading: zoom out, then zoom in.** Present the high-level idea and modular structure of a proof *before* any line-by-line detail, and explicitly say you are doing so. Linear presentation trains the novice reading strategy. (Weber & Mejía-Ramos §4.2)

16. **When a learner is stuck on a proof, suspect an empty referential domain, not bad logic.** Ask them to instantiate the statement in a reference example first. Semantic proof production requires instantiations to reason with; a learner with none can only manipulate syntax. (Weber & Alcock §4.3)

17. **Use dualization as a free, infinite, self-checking exercise generator.** Every definition and theorem yields: "state the dual," then "compute the dual in Set and in a poset." Correctness is mechanically checkable and the learner is exercising the definition rather than recalling it. (Leinster §5)

18. **Lead with the payoff.** Before the machinery, state a striking corollary the learner already cares about. This supplies the felt need that makes the definition feel earned rather than arbitrary. (Riehl's "sample corollaries" §5)

19. **One idea per turn, followed immediately by a puzzle.** Keep the exposition unit small and never deliver two new concepts before the first has been exercised. (Baez §5)

20. **Attempt before instruction — for concepts; demonstrate before attempt — for procedures.** Ask the learner to invent a way to compare two structures *before* defining natural transformation (d≈0.36 on conceptual understanding and transfer). But demonstrate the mechanics of verifying functoriality before asking them to do it. (Kapur §9 + Sweller §3.1)

21. **Never let a struggle end without consolidation.** Productive failure is only productive if the learner's own attempt is explicitly contrasted with the canonical solution. Structure it as: their attempt → what it captures → what it misses → the canonical definition → why the difference matters. This is also the right place to put the explanation you suppressed in rule 11. (Kapur & Roll §9)

22. **Every analogy ships with its breakdown point, in the same message.** An unmarked analogy becomes a permanent, wrong component of the concept image that is never co-evoked with the definition and therefore never self-corrects. (Tall & Vinner §1.1; negative transfer §8)

23. **Give two structurally different analogies and ask the learner to map between them** rather than one polished analogy. Explicit structural mapping across multiple analogs is what drives transfer; a single analogy transfers its surface features along with its structure. (Richland §8)

24. **Interleave across concepts once several are in play, and space revisits.** Prefer "is this a limit, a colimit, an adjunction, or none?" over six consecutive limit problems: the strategy-selection demand is the mechanism, and it is also a form of support fading. (§7)

25. **Watch for the two named failure signatures and name them when you see them.** (a) *Pseudo-structural*: the learner chases the diagram correctly but cannot say what any node is — fix by demanding an instantiation. (b) *Definition-recital*: the learner states the definition correctly but cannot apply it to a given instance — fix by dropping back to varied examples. Both are invisible to correctness-only checking, which is the default an LLM will otherwise do. (Sfard §1.3; topology §6.2)

26. **Treat the category-theory misconception list in §6.3 as hypotheses to probe, not facts.** There is no validated empirical inventory for category theory. Probe specifically for: uniqueness clauses dropped from universal properties; naturality treated as decoration; functor examples all forgetful; Yoneda chased without instantiation; equality intuitions imported into an up-to-iso world. When probing confirms one, record it — the tutor is the instrument that would generate this inventory.

---

## Sources

- [Tall & Vinner 1981, *ESM* 12:151–169](https://link.springer.com/article/10.1007/BF00305619) · [PDF](http://homepages.math.uic.edu/~bshipley/Tall_David.pdf) · [ERIC](https://eric.ed.gov/?id=EJ246334) · [Wikipedia overview](https://en.wikipedia.org/wiki/Concept_image_and_concept_definition)
- [Arnon, Cottrill, Dubinsky et al., *APOS Theory*](https://link.springer.com/chapter/10.1007/978-1-4614-7966-6_2) · [Google Books](https://books.google.com/books/about/APOS_Theory.html?id=OrS9BAAAQBAJ) · [Reflections on APOS in elementary/advanced mathematical thinking](https://www.researchgate.net/publication/228596850_Reflections_on_APOS_theory_in_elementary_and_advanced_mathematical_thinking)
- [Sfard & Linchevski 1994, "The gains and the pitfalls of reification", *ESM*](https://link.springer.com/article/10.1007/BF01273663) · [PDF](http://academic.sun.ac.za/mathed/174/GainsAndPitfalls.pdf) · [Sfard on operational origins & the quandary of reification](https://www.researchgate.net/publication/242490242_Operational_origins_of_mathematical_objects_and_the_quandary_of_reification-The_case_of_function)
- [Michener 1978, "Understanding understanding mathematics", *Cognitive Science*](https://onlinelibrary.wiley.com/doi/abs/10.1207/s15516709cog0204_3) · [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0364021378800524) · [Antonini et al., "On examples in mathematical thinking and learning", *ZDM* 2011](https://link.springer.com/article/10.1007/s11858-011-0334-5) · [Exemplification in mathematics education](https://www.researchgate.net/publication/288922813_Exemplification_in_mathematics_education)
- [Watson & Mason 2005](https://www.routledge.com/Mathematics-as-a-Constructive-Activity-Learners-Generating-Examples/Watson-Mason/p/book/9780805843446) · [ORO](https://oro.open.ac.uk/792) · [Goldenberg & Mason 2008](https://link.springer.com/article/10.1007/s10649-008-9143-3) · [Sinclair et al. on personal example spaces](https://www.sciencedirect.com/science/article/abs/pii/S0732312311000277) · [Extending example spaces (PME 2002)](http://www.pmtheta.com/uploads/4/7/7/8/47787337/extending_example_spaces_pme_2002.pdf)
- [Mason & Pimm 1984, "Generic examples: seeing the general in the particular"](https://link.springer.com/article/10.1007/BF00312078) · [Generic examples in teachers' proving activities, *ESM* 2020](https://link.springer.com/article/10.1007/s10649-020-10002-3) · [When is a generic argument a proof?](https://link.springer.com/chapter/10.1007/978-3-319-70996-3_17)
- [Zazkis & Chernoff 2008, *ESM* 68(3)](https://link.springer.com/article/10.1007/s10649-007-9110-4) · [PDF](https://opencourses.uoa.gr/modules/document/file.php/MATH128/%CE%94%CE%B9%CE%B4%CE%B1%CE%BA%CF%84%CE%B9%CE%BA%CF%8C%20%CF%80%CE%B1%CE%BA%CE%AD%CF%84%CE%BF/%CE%86%CF%81%CE%B8%CF%81%CE%B1%20%CE%B3%CE%B9%CE%B1%20%CF%80%CE%B1%CF%81%CE%BF%CF%85%CF%83%CE%AF%CE%B1%CF%83%CE%B7/Arthra-Ylika%20gia%20deyteri%20ergasia%202015-2016/Paradeigmata/What%20makes%20a%20counterexample%20exemplary%20(Zazkis,%20Chernoff).pdf) · [Pivotal/bridging examples](https://www.researchgate.net/publication/238734117_Cognitive_Conflict_and_its_resolution_via_pivotalbridging_example) · [Manifestations of cognitive conflict](https://files.eric.ed.gov/fulltext/EJ1280100.pdf)
- [Marton variation theory (Leung)](https://files.eric.ed.gov/fulltext/ED573288.pdf) · [Mason, Variation and mathematical structure](http://www.pmtheta.com/uploads/4/7/7/8/47787337/variation_2007.pdf) · [Variation theory in teaching mathematics](https://files.eric.ed.gov/fulltext/EJ1442215.pdf) · [Sequencing and pairing of examples](https://scielo.org.za/scielo.php?script=sci_arttext&pid=S2223-78952022000100012)
- [Kalyuga & Renkl 2009, expertise reversal special issue](https://link.springer.com/article/10.1007/s11251-009-9102-0) · [Salden et al., expertise reversal & worked examples in tutored problem solving](http://www.cee.uma.pt/ron/Salden%20et%20al.%20-%20The%20Expertise%20Reversal%20Effect%20and%20Worked%20Examples.pdf) · [Cambridge Handbook ch. 40](https://www.cambridge.org/core/books/cambridge-handbook-of-expertise-and-expert-performance/cognitive-load-and-expertise-reversal/03F656FD334F23214426ACB4118FEBF9) · [Expertise reversal in ill-structured tasks](https://www.sciencedirect.com/science/article/abs/pii/S0361476X12000677) · [Worked examples & knowledge transfer 2023](https://www.tandfonline.com/doi/full/10.1080/01443410.2023.2273762)
- [Chi et al. 1989, *Cognitive Science* 13(2)](https://onlinelibrary.wiley.com/doi/abs/10.1207/s15516709cog1302_1) · [Chi et al., Eliciting self-explanations](https://www.semanticscholar.org/paper/Eliciting-Self-Explanations-Improves-Understanding-Chi-Leeuw/dd869eeb2e13264d47eb0d150d05912b7afd9aba) · [Atkinson, Renkl & Merrill 2003](https://mrbartonmaths.com/resourcesnew/8.%20Research/Making%20the%20most%20of%20examples/Fading%20out%20and%20Prompts.pdf) · [Renkl, how self-explanation can (not) be fostered](https://www.researchgate.net/publication/228741425_Learning_from_worked-out_examples_via_self-explanations_How_it_can_not_be_fostered) · [Instructional explanations vs self-explanations](https://www.sciencedirect.com/science/article/abs/pii/S0959475201000305) · [Constraints on when self-explanation aids learning](https://link.springer.com/article/10.3758/s13423-016-1079-5)
- [Selden & Selden, Unpacking the logic of mathematical statements](https://philpapers.org/archive/SELUTL.pdf) · [Validation of proofs as a type of reading (TR-2015-4)](https://www.tntech.edu/cas/pdf/math/techreports/TR-2015-4.pdf) · [Teaching proving by coordinating aspects of proofs](https://philarchive.org/rec/SELTPB) · [Selden, proof research retrospective (TR-2023-1)](https://www.tntech.edu/cas/pdf/math/techreports/TR-2023-1.pdf) · [Structures of proofs](https://www.academia.edu/62622391/Unpublished_Article_Structures_of_Proofs)
- [Weber & Mejía-Ramos 2011, exploratory study](https://www.researchgate.net/publication/226580934_Why_and_how_mathematicians_read_proofs_An_exploratory_study) · [Mejía-Ramos & Weber 2014, survey study](https://link.springer.com/article/10.1007/s10649-013-9514-2) · [Mejía-Ramos et al. 2012, assessment model for proof comprehension](https://eric.ed.gov/?id=EJ948400) · [Rutgers record](https://www.researchwithrutgers.com/en/publications/an-assessment-model-for-proof-comprehension-in-undergraduate-math/) · [Validated proof comprehension tests](https://www.tandfonline.com/doi/abs/10.1080/14794802.2017.1325776) · [Instructional intervention on proof comprehension](https://www.sciencedirect.com/science/article/abs/pii/S0732312315000413) · [Comparative judgement & proof summaries](https://link.springer.com/article/10.1007/s10649-020-09984-x) · [Proof comprehension study (HAL)](https://hal.science/hal-02398493/document) · [Mathematics majors' beliefs about proof reading](https://sites.math.rutgers.edu/~jpmejia/files/Weber%20&%20Mejia-Ramos%20(iJMEST).pdf) · [Inglis & Alcock, differing standards](https://onlinelibrary.wiley.com/doi/10.1111/tops.12019) · [Mathematical Proofs 101](https://arxiv.org/pdf/1806.06892)
- [Weber & Alcock 2004, Semantic and syntactic proof productions](https://link.springer.com/article/10.1023/B:EDUC.0000040410.57253.a1) · [PDF](https://www.academia.edu/58975810/Semantic_and_Syntactic_Proof_Productions) · [Weber 2009 reply](https://eric.ed.gov/?id=EJ869405) · [Doctoral students' use of examples](https://link.springer.com/article/10.1007/s10649-008-9149-x) · [Mathematicians' vs students' example use](https://www.sciencedirect.com/science/article/abs/pii/S0732312317300238) · [Weber, RACUM](https://www.researchgate.net/publication/226344097_How_do_mathematicians_learn_math_Resources_and_acts_for_constructing_and_understanding_math) · [Weber 2012, mathematicians' pedagogical practice](https://sites.math.rutgers.edu/~jpmejia/files/Weber_(2012IJMEST).pdf) · [Stylianides & Weber, Compendium chapter](https://sites.math.rutgers.edu/~jpmejia/files/Stylianides_Weber_(Compedium).pdf)
- [Lawvere & Schanuel, *Conceptual Mathematics* (Archive.org)](https://archive.org/details/F.WilliamLawvereStephenH.SchanuelConceptualMathematicsAFirstIntroductionToCatego) · [PhilPapers](https://philpapers.org/rec/LAWCMA)
- [Riehl, *Category Theory in Context* (PDF)](https://math.jhu.edu/~eriehl/context.pdf) · [n-Category Café post by Riehl](https://golem.ph.utexas.edu/category/2016/11/category_theory_in_context.html)
- [Leinster, *Basic Category Theory*, arXiv:1612.09375](https://arxiv.org/pdf/1612.09375)
- [Fong & Spivak, *Seven Sketches*, arXiv:1803.05316](https://arxiv.org/abs/1803.05316) · [Cambridge](https://www.cambridge.org/core/books/an-invitation-to-applied-category-theory/D4C5E5C2B019B2F9B8CE9A4E9E84D6BC) · [LibreTexts](https://math.libretexts.org/Bookshelves/Applied_Mathematics/Seven_Sketches_in_Compositionality:_An_Invitation_to_Applied_Category_Theory_(Fong_and_Spivak))
- [Baez ACT course](https://math.ucr.edu/home/baez/act_course/) · [Lecture 1](https://math.ucr.edu/home/baez/act_course/lecture_1.html) · [Azimuth announcement](https://johncarlosbaez.wordpress.com/2018/03/26/seven-sketches-in-compositionality/) · [2023 lectures](https://johncarlosbaez.wordpress.com/2023/09/28/lectures-on-applied-category-theory/) · [Spivak, Category theory for scientists](https://arxiv.org/pdf/1302.6946)
- [Milewski, Category Theory for Programmers preface](https://bartoszmilewski.com/2014/10/28/category-theory-for-programmers-the-preface/) · [Category Theory Illustrated: natural transformations](https://abuseofnotation.github.io/category-theory-illustrated/11_natural_transformations/) · [John D. Cook on natural transformations](https://www.johndcook.com/blog/2017/03/16/natural-transformations/) · [Wisconsin course notes](https://pages.cs.wisc.edu/~jcyphert/categoryTheoryNotes/basics/3_NaturalTransformations.pdf)
- [Eugenia Cheng](https://eugeniacheng.com/) · [Quanta interview](https://www.quantamagazine.org/is-there-math-beyond-the-equal-sign-20230322/) · [*The Joy of Abstraction*](https://www.amazon.com/Joy-Abstraction-Exploration-Category-Theory/dp/1108477224)
- [Asiala, Dubinsky et al. on cosets/normality/quotient groups](https://www.academia.edu/27961571/Development_of_students_understanding_of_cosets_normality_and_quotient_groups) · [Group isomorphism misconceptions](https://www.academia.edu/31452718/Students_conceptions_and_misconceptions_of_group_isomorphism) · [Dubinsky et al. 1994, learning fundamental concepts of group theory](https://link.springer.com/article/10.1007/BF01273732) · [Abstract algebra difficulties survey 2024](https://www.tandfonline.com/doi/pdf/10.1080/2331186X.2024.2355400) · [ACE cycle study](https://files.eric.ed.gov/fulltext/EJ1329228.pdf) · [Dubinsky & Leron, ISETL](https://www.amazon.com/Learning-Abstract-Algebra-Mathematical-Systems/dp/0387941045)
- [Do students really understand topology?](https://files.eric.ed.gov/fulltext/ED510704.pdf) · [Cognitive functions in learning general topology, *IJRUME* 2024](https://link.springer.com/article/10.1007/s40753-024-00245-3) · [Innovative possibilities for undergraduate topology](https://www.researchgate.net/publication/228389029_Innovative_Possibilities_for_Undergraduate_Topology)
- [Spacing/retrieval meta-analysis for mathematics, 2025](https://link.springer.com/article/10.1007/s10648-025-10035-1) · [Rohrer, interleaved practice](https://files.eric.ed.gov/fulltext/ED557355.pdf) · [Rohrer & Hartwig](https://www.unh.edu/teaching-learning-resource-hub/sites/default/files/media/2023-06/itow-spaced-and-interleaved-mathematics-practice-rohrer-hartwig.pdf) · [MIT open learning summary](https://openlearning.mit.edu/mit-faculty/research-based-learning-findings/spaced-and-interleaved-practice)
- [Multiple representations](https://en.wikipedia.org/wiki/Multiple_representations_(mathematics_education)) · [Richland, learning by analogy](https://learninglab.uchicago.edu/Publications_files/16%20Richland%20(2010)%20Learning%20by%20analogy.pdf) · [Analogical transfer in problem solving](https://www.researchgate.net/publication/288047613_Analogical_Transfer_in_Problem_Solving) · [Positive and negative transfer in analogical problem solving](https://www.sciencedirect.com/science/article/abs/pii/S0885201489900312) · [Misanalogical construction](https://www.iejme.com/download/the-misanalogical-construction-of-undergraduate-students-in-solving-cognitive-conflict-3961.pdf)
- [Sinha & Kapur 2021, *RER* meta-analysis](https://journals.sagepub.com/doi/10.3102/00346543211019105) · [Kapur & Roll, Productive Failure](https://boldscience.org/wp-content/uploads/2025/04/Productive-Failure.pdf) · [Kapur 2012, generation and invention activities](https://link.springer.com/article/10.1007/s11251-012-9235-4) · [Phys.org summary](https://phys.org/news/2021-09-productively-wiser.html)
