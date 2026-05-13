# Gate 3 Talking Script — MedFlex Defense
**10-minute coach call | Ann O'Hagan**

---

## Before you start

The title slide shows the three probe questions the coach is likely to ask. Slides 3, 4, and 5 are the direct answers to those. The coach will probably interrupt during slide 3 or 4 — that is fine, those slides are designed to anchor a conversation, not to be read through.

Do not rush. If the coach picks one thread and you spend eight minutes on it, that is a better session than skimming nine slides in ten minutes.

---

## Slide 1 — Title (~30 seconds)

"So what I built for Gate 3 was a MedFlex engagement. MedFlex is a healthcare staffing firm, and the two capabilities I took through the full cycle were candidate ranking and parallel outreach. I put three questions on the title slide because I want to be upfront about what I expect you to push on — whether this is genuinely agentic, how it's different from AI projects that fail, and what would actually kill it in production. Happy to take those in any order."

*Pause. Let the coach respond. If they pick a thread, go directly to that slide.*

---

## Slide 2 — What Was Built (~60 seconds)

"The problem is straightforward. MedFlex coordinators fill nurse shifts by contacting nurses one at a time. For urgent fills — anything under four hours — that sequential approach can mean the window expires before anyone confirms.

The two capabilities I built address that directly. Candidate ranking takes all the eligible nurses for a shift and scores them across six factors simultaneously, returning up to five ranked candidates with a written explanation for each. Parallel outreach then contacts the top candidates at the same time rather than in sequence, and adapts its strategy in real time based on how urgent the fill is and how many candidates are available.

The wave structure is important. Wave 1 is a six-week pilot, deliberately small — standard fills over 24 hours, two or three coordinators, established hospital accounts, coordinator approves every placement. Wave 2 only starts at month five if the first-recommendation acceptance rate hits 90% over 60 days. If the pilot doesn't produce that, Wave 2 doesn't start. That threshold is set before build, not after."

---

## Slide 3 — Is This Agentic? (~2 minutes)

*This is the slide most likely to attract the hardest question. Go slowly.*

"This is the question I want to answer honestly. Some parts of this are deterministic. The urgency tier calculation is an if/else. The factor weights are a lookup table. The no-show lookback is date arithmetic. A script could run those.

The case for the agent is in what a standard app would do versus what this does. A standard app would contact nurses sequentially in a fixed order, stop when someone confirms, and give no explanation. It would also fail silently when data is missing.

What the agent does differently is three things working together. First, it contacts multiple nurses simultaneously, and the number it contacts changes based on live pool state and urgency at the time of ranking — not a fixed rule. Second, it coordinates across concurrent fills. If two shifts are being filled at the same time, the agent knows which nurses are already in outreach for the other fill and excludes them — that requires real-time shared state, not a scheduled job. Third, it produces a written rationale specific to this candidate, in this context, for this urgency tier — so the coordinator can see why and override if they disagree.

The honest answer to 'is this just a script with AI sprinkled on top' is: any one of those things alone could be a script. The combination of simultaneous outreach, contextual ranking under incomplete data, real-time state awareness across concurrent fills, and an explainable output — that combination is what justifies the agent. A fixed workflow cannot encode all of that."

*If the coach pushes: "But couldn't you just hard-code all those rules?"*

"You could hard-code the rules for a single fill in isolation. The problem is concurrent fills. When two fills are running at the same time, the agent needs to read shared state in real time to exclude nurses who are already committed elsewhere. A fixed rule table doesn't know what is happening in a parallel process. That's where the agent earns its place."

---

## Slide 4 — CEO's Failed AI Projects (~90 seconds)

*Coach picks this OR slide 5 — not both. If they picked slide 3's thread, you may not get here.*

"AI projects fail in predictable ways, and I tried to design against each one specifically.

The most common failure is automating the wrong thing. Here the bottleneck is real, it is measurable, and the two capabilities go directly at fill time. That is the primary metric for the board.

The second failure is black box decisions — nobody can see why the system did what it did, so nobody trusts it. Every ranked candidate in this system has a written rationale the coordinator reads before approving anything. The coordinator can see why, override it, and that override is logged. Trust is built incrementally, not assumed.

The third is removing humans from decisions they need to own. The coordinator approves every placement. The agent never contacts the hospital directly. Kim's team owns that relationship, and the design respects that.

The fourth is launching too big. Wave 1 is two or three coordinators, standard fills only, established accounts. It is small enough to stop and reverse without damaging live operations.

And the fifth is having no success criteria. The Wave 2 trigger — 90% acceptance rate over 60 days — is defined before build. If the pilot does not hit that, Wave 2 does not start. There is no ambiguity about whether it worked."

---

## Slide 5 — What Kills This in Production (~90 seconds)

*Coach picks this OR slide 4.*

"Three things could kill this, and I want to be honest about all of them.

The first is concurrent fill state inconsistency. If two fills are running at the same time and there is a stale read in the shared state, a nurse already committed to one fill gets contacted for a second. We have a fallback — a database flag per nurse if shared state is unavailable — but this is not fully testable before live volume.

The second is a nurse confirming via a different channel. If the agent contacts a nurse by SMS and she calls the coordinator directly, the system does not detect the confirmation. The outreach window expires, the next candidate is contacted, and if the first nurse shows up, the shift may be double-placed. There is no technical fix for this — it depends on nurse behaviour that is only observable in live operation. It is flagged as a known gap.

The third is the one I think is the real risk, and I have highlighted it in red. If coordinators have not consistently logged response rates and no-show history in the CRM, the ranking agent is working on credentials and proximity only. The rationale thins. Coordinators start overriding. The acceptance rate stays below 90% and Wave 2 never starts. The system works correctly by its own logic while producing rankings that coordinators increasingly do not trust. It fails silently."

*If the coach asks: "What do you do about that?"*

"We monitor the acceptance rate from week one of the pilot. If it is not tracking towards 90% by week four, we stop and diagnose. We look at whether it is a ranking problem, a data quality problem, or an outreach problem — not both at once. And we validate CRM data quality before build starts, not after."

---

## Slide 6 — Marcus's Feedback (~60 seconds)

"Marcus came back with three things. The timeline — he needed it in six weeks, not eight. I restructured the plan, and the important thing I said in the response was that the week six board deliverable would be directional data, not proof of 10x capacity. Going in with a realistic claim is a stronger position than an overcommitted one.

The second was to remove credential verification from Wave 1. I agreed, but I made the point that the original design already had that as conditional — it was waiting on Linda to confirm the root cause of a 7% mismatch rate in credentials. So removing it from Wave 1 was consistent with where we were, not a concession.

The third was Kim's observation about the failure path. The spec did not say who manages the hospital conversation when things go wrong. That was a genuine gap. I added a failure path section covering four scenarios, and in all four the coordinator owns the hospital relationship — the agent pre-drafts the status message, the coordinator makes the call."

---

## Slide 7 — Build Loop (~60 seconds)

"The build loop is where I found out what was wrong with my spec, and the key observation is that no clarifying questions were asked during the build. That sounds fine, but it means wherever my spec was unclear, the builder made a decision and moved on without telling me.

Five signals came out of it. The one that is red — an unjustified implementation choice — is the proximity formula. I listed proximity as a ranking factor, but I never said how to convert distance into a number. The builder invented a formula I never specified. Different formulas produce different rankings from the same pool.

The four orange ones are spec gaps. The most significant is the system unavailability one: I wrote rules for what should happen when a system was down, but the tool had no way of receiving that information. The rule existed; the mechanism did not.

All five were fixed in the updated spec — the scoring formula is now explicit, the rule 7 threshold is defined, system availability is an input, and the excluded candidates field is defined in the output type."

---

## Slide 8 — Reflection (~60 seconds)

"Two things I would do differently in how I ran the engagement.

Confirm the timeline in the first conversation. Marcus told me it was six weeks after I had already written the plan. That is a basic question.

Involve Kim's team in discovery. Kim was not in the discovery session. The failure path gap she spotted would have been caught in a 30-minute conversation I did not have.

Four things from the spec writing.

Define the output before writing the error handling rule. I said 'include excluded candidates in the escalation payload' — the output I had designed had nowhere to put them. The rule and the output were not aligned.

For every 'if X is unavailable' rule, ask how the tool actually finds out. I kept writing fallback rules without thinking about what signal the tool would receive.

Every ranking factor needs a formula, not just a name. And ambiguous thresholds — 'within 10%' — sound specific but are not. I needed to say what was being compared."

---

## Slide 9 — Honest Trade-offs (~30 seconds)

"The close. Three columns — what I am confident about, what I am not, and what would change the design if the assumptions turn out to be wrong.

The confident column is where the design holds regardless. The uncertain column is where I have assumptions I have not been able to validate yet — CRM data quality is the big one. And the right column is the contingency: if those assumptions break, here is what changes and how."

*Pause. Invite the coach to push back.*

"That is everything. Happy to go deeper on any of it."

---

## Quick answers if the coach probes outside the slides

**"Why not just build a simple rule engine?"**
A rule engine handles one fill. The agent handles concurrent fills with shared state, incomplete data, and natural language explanation. The rule engine can't coordinate across parallel processes in real time.

**"How do you know the acceptance rate threshold is right?"**
We don't — 90% is a design assumption based on what would give a coordinator team enough confidence to expand. The pilot either validates it or gives us data to revise it. It is a hypothesis, not a guarantee.

**"What does success look like at week six?"**
Fill time reduction on 20 to 30 live shifts, and a first-recommendation acceptance rate we can project forward. Not proof the system works at scale — proof that it is worth scaling.

**"What if Kim's team doesn't trust it?"**
The rationale exists precisely for that. If coordinators override, we ask why. If the rationale is not explaining the right things, we adjust it. The override log is the feedback mechanism.
