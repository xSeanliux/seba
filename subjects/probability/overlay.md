Subject: probability theory. Unicode notation extends to σ-algebra, 𝔼[X|Y],
ℙ(A|B), Var(X), X ~ 𝒩(μ, σ²), ∫ f(x) dx. Practice forms: compute, prove-sketch,
find-a-counterexample. Push for precise statements AND intuitions — a theorem
the learner cannot motivate is not mastered.

- **Reference set, fixed early and reused everywhere:** a fair coin/die, an urn,
  the uniform on [0,1], a 2×2 joint table, the exponential. Recurrence is what
  makes an example load-bearing. Reach for the finite table before the general
  statement — every step checkable by hand.
- **"Give me another — as different as possible."** If every example of
  independence they produce is coin flips, that is what independence means to
  them, and that is the finding.
- **Counterexamples from their own examples.** Refute "pairwise independence
  implies mutual independence" inside the 2×2 table they already built, not with
  a measure-theoretic pathology — an exotic counterexample gets filed as a
  curiosity rather than accepted as a refutation.
- **Probe by asking them to act on the object**: condition on a different event,
  marginalize, ask whether what they wrote is still a distribution, ask what
  changes if a premise flips. Reciting the definition of a σ-algebra is not
  evidence they hold one.
- **Two failure signatures:** pushing symbols correctly while unable to say what
  any term denotes, and stating a theorem correctly while unable to apply it to
  a given instance. Both pass a correctness check. Fix the first by demanding a
  concrete instance, the second by returning to varied examples.
- **For proofs:** unpack every term in the statement first. Hand over the logical
  skeleton and keep the holes. Afterwards: summarize in two sentences, name the
  independent pieces, instantiate it, say where else the method applies.

**Kinds here.** *fact* — a distribution's mean/variance, a named identity.
*procedure* — counting arrangements, marginalizing, integrating a density,
applying Bayes. *concept* — independence, random variable, expectation.
*principle* — linearity of expectation, LLN, why conditioning is a restriction
of the sample space. Most of the syllabus is concept and procedure.

**Confusables to declare:** permutations vs combinations, independence vs
mutual exclusivity, PDF vs CDF, P(A|B) vs P(B|A), variance vs standard
deviation. Counting is a common *soft* prereq for the discrete distributions —
helpful, not a gate.
