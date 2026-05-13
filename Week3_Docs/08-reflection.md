# D8 — Reflection Document
**MedFlex Engagement | Ann OHagan**

---

**1. What would you design differently if you were starting this engagement again, and why?**

The most obvious thing is that I would confirm the board timeline before writing any plan. Marcus came back within days to say the board meeting was in 6 weeks, not 8, and I had to restructure everything before the ink was dry. That is a basic question I should have asked in the first conversation. I would also have pushed harder to get Kim involved earlier. She was not in the discovery session, and a lot of the assumptions I made about how the matching workflow actually runs day to day would have been much stronger with her input. The failure path gap that she spotted was exactly the kind of thing she would have flagged in a 30-minute conversation.

---

**2. Where in your specification did you leave the most room for a builder to misinterpret your intent?**

The credential classification piece is the clearest example. I included a list of what I thought counted as a specialist credential, but that list came from me, not from Linda or the compliance system. A builder using that list would be working from my best guess rather than the actual source of truth, and if it was wrong it would affect every ranking decision the agent made. More generally, I think I wrote some of the error handling rules as though they were obvious, without thinking through whether someone reading the document for the first time would actually know how to act on them.

---

**3. What did the build output reveal that you did not expect?**

I was surprised by how quickly the gaps in the spec became visible once someone started building against it. Things that looked complete on paper turned out to have missing pieces that only became obvious when you tried to actually implement them. The error handling rules were the main example: I had written what should happen when a system was unavailable, but had not thought through how the system would even know it was unavailable. That is the kind of thing that is hard to spot just by reading a document, but obvious the moment you try to build it.

---

**4. What is one specific thing you will do differently when writing requirements in future, and what experience from this engagement led you to that conclusion?**

I will make sure that any rule I write about what happens when something goes wrong actually includes how the system finds out something has gone wrong. I kept writing things like "if the data is unavailable, do this" without thinking about where that information comes from. The build-loop showed me that those rules are not actionable as written. It is a simple check: for every error handling rule, ask yourself how the system would actually know it was in that situation. If you cannot answer that, the rule is incomplete.
