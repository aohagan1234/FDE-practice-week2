# D8 — Reflection Document
**MedFlex Engagement | Ann OHagan**

---

**1. What would you design differently if you were starting this engagement again, and why?**

I would confirm the board timeline with Marcus before proposing any delivery plan. The 8-week plan was structurally sound but immediately wrong for the client's actual constraint, and the pushback consumed time that could have been spent on the architecture. I would also ensure both ADRs addressed genuinely contested design decisions from the start. The original ADR2 was a scope justification that duplicated the Wave 1/Wave 2 table rather than capturing a decision a builder would actually face, and replacing it mid-engagement created unnecessary rework.

---

**2. Where in your specification did you leave the most room for a builder to misinterpret your intent?**

The error handling rows in the capability specs are the weakest section. Each row defines what the agent should do when an external system is unavailable, but the function signature accepts no availability state as input, so a builder has no mechanism to implement those paths as written. A builder following the spec exactly would either add undocumented parameters or silently skip the error paths, and either outcome is a build-loop failure waiting to happen. The proximity normalization was a second gap: naming proximity as a ranking factor without defining a scoring formula means every builder chooses their own, and different choices produce materially different rankings for the same pool.

---

**3. What did the build output reveal that you did not expect?**

The build made the error handling gap immediately visible in a way the spec review did not. Writing the function signature forced a concrete decision about what information the function could receive, and the CRM and compliance system error paths simply had nowhere to land. The rule 7 "within 10%" preference boost also surfaced an ambiguity that read as precise in the spec: "all other ranking factors within 10%" sounds specific, but the implementation had to choose between checking the composite score or each individual factor, and those produce different outcomes.

---

**4. What is one specific thing you will do differently when writing requirements in future, and what experience from this engagement led you to that conclusion?**

Every error handling row that references an external system state will have a corresponding input parameter in the function signature before the spec is handed to a builder. The D5 build-loop made this concrete: "if CRM unavailable, apply median imputation" is not a requirement a builder can implement without a `crm_available: bool` parameter, and discovering that at build time rather than spec time is avoidable. The discipline of writing the function signature alongside the error handling table, rather than after it, would have closed this gap before the build started.
