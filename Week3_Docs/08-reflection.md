# D8 — Reflection Document
**MedFlex Engagement | Ann OHagan**

---

**1. What would you design differently if you were starting this engagement again, and why?**

The first thing I would do is confirm the board timeline before putting any plan on paper. I proposed an 8-week delivery and Marcus came back immediately to say the board meeting was in 6 weeks. That is a basic piece of information I should have had from the first conversation, and not having it meant I had to rework the plan before the architecture work was even finished. I would also make sure the ADRs were capturing real design decisions from the start. The first version of ADR2 was essentially just restating the Wave 1/Wave 2 scope split, which was already in a table. That is not an architectural decision, and I had to replace it once I realised it was not doing any useful work.

---

**2. Where in your specification did you leave the most room for a builder to misinterpret your intent?**

The error handling section is where I fell short. I wrote rows like "if the CRM is unavailable, apply median imputation" but never defined how the function would actually know the CRM was unavailable. A builder reading that would have no way to implement it without adding a parameter that was not in the spec, or just skipping it entirely. That is a gap I only noticed when I started writing the actual code. I also named proximity as a ranking factor without saying how to score it. That sounds like a small thing but it means two different builders could produce two completely different rankings from the same pool of nurses, and both would be following the spec correctly.

---

**3. What did the build output reveal that you did not expect?**

I did not expect the error handling gaps to be as obvious as they were once I started coding. When you write a spec it can look complete, but the moment you write a function signature you have to decide exactly what inputs it takes, and that is when vague requirements become impossible to implement. The CRM and compliance system error paths had nowhere to go. I also found that the "within 10%" rule for the preference boost, which I thought was precise, turned out to be ambiguous. The spec said "all other ranking factors within 10%" but that could mean checking each factor individually or checking the overall score, and those give different results.

---

**4. What is one specific thing you will do differently when writing requirements in future, and what experience from this engagement led you to that conclusion?**

Going forward, I will write the function signature at the same time as the error handling table, not after it. If a row in the error handling table says "if system X is unavailable, do Y," I need to make sure there is an input parameter that tells the function whether system X is available. If there is no parameter, the error path cannot be built. I learned this the hard way on this engagement, where the build-loop immediately showed me that several of my error handling requirements were essentially undeliverable as written. That is a straightforward fix and there is no good reason to leave it to the builder to figure out.
