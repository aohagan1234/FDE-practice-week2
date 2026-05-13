# D9 — Self-Spec Build-Loop Reflection
**MedFlex Engagement | Capability: Candidate Ranking**

---

## What was built

A working tool that ranks nurse candidates for a shift. It looks at how urgent the fill is, what credentials each nurse has, how far away they are, and how often they respond to outreach, and uses those factors to put candidates in order. The tool also handles situations where no candidates are available, or where a system it relies on is down, and it produces a short written explanation for each candidate explaining why they were ranked where they were.

---

## What Claude Code asked about

Nothing. No questions were asked during the build. At first that seemed fine, but it is actually a warning sign. It means that wherever my spec was unclear, the builder made a decision and moved on without flagging it. I only found out what those decisions were by reading the output afterwards. For several of them, I would have wanted to be asked before the decision was made.

---

## Signals in the output

| Signal | Classification | What my specification failed to say |
|---|---|---|
| The builder invented a formula for turning distance into a score, using a reference distance I never mentioned | Unjustified implementation choice | I listed proximity as a ranking factor but never said how it should be converted into a number. Two different builders would come up with two different approaches, and the candidate rankings would differ as a result |
| The "within 10%" rule was applied to an overall score, not to each individual factor | Spec gap | My wording sounded precise but did not actually say what was being compared. It was ambiguous in a way I did not notice when I wrote it |
| When a system was unavailable, the builder handled it the same way as when data was simply missing for a candidate | Spec gap | I wrote a rule for what to do when a system was down, but never said how the tool would know the difference between a system being down and that system just returning no data |
| The rule about holding ranking when a system was unavailable could not actually be followed as written | Spec gap | I wrote "if the system is unavailable, hold ranking" but the tool had no way of being told whether a system was available or not. It was a rule that depended on information that was never passed to it |
| The escalation message when no candidates were available did not include the list of excluded candidates I said it should | Spec gap | I said the message should include a list of who was excluded and why, but I never defined where in the output that information would go. There was no space for it in the output I had designed |

---

## What I would change in the specification

- **How proximity is scored:** I said proximity should be a factor but did not say how it should be turned into a number. I should have given a simple formula and defined what the reference point is, for example, a nurse at the exact location scores the highest and the score drops off at a defined rate with distance. Without that, whoever builds it has to guess, and different guesses produce different rankings.

- **What "within 10%" actually means:** I thought writing "within 10%" was specific enough. It was not. I should have said: compare the overall score of the preferred nurse to the overall score of the nurse ranked immediately above them, and only apply the boost if the gap between those two overall scores is 10% or less. "Within 10%" on its own does not say what is being compared or how the comparison is made.

- **How the tool finds out a system is down:** For every rule I wrote about what should happen when a system is unavailable, I should have stopped and asked myself how the tool would actually receive that information. If there is no mechanism for the tool to be told a system is down, the rule cannot be acted on. I needed to say that the tool should be given a clear signal for each system it depends on, telling it whether that system is currently available.

- **What the escalation message should contain:** I wrote that the escalation should include a list of excluded candidates and the reasons they were excluded. But the output I had designed had no field to hold that information. The rule and the output were not aligned. I should have designed the output first and then written the rules around it, rather than adding detail to a rule without checking whether the output could actually support it.
