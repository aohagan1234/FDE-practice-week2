# MedFlex Discovery Call Guide — Marcus Reyes
**Thursday 09:30–10:30. 60 minutes. Keep this open during the call.**

---

## Marcus — what to expect

- Answers executive-layer facts precisely: numbers, board pressure, prior failures
- Defers operational detail to Kim (senior coordinator), Aaron (IT), Linda (compliance) — none of whom are in the session
- Pushes back hard on premature solutioning: "That sounds like a chatbot. We tried that."
- Respects directness. Cuts off rambling. Ask one question at a time.
- When you catch a contradiction: call it out directly, no grandstanding. One sentence. He will acknowledge and defer resolution.

---

## Contradiction watch — know these before the call

These are the three planted contradictions. They will not be flagged. Your job is to catch them as they happen.

### C1 — Availability data
**Listen for:** Marcus says the app is the source of truth for nurse availability.
**Then listen for:** nurses call Kim when they are sick, and Kim updates manually.
**The gap:** if updates are manual and go through Kim, the app is not the source of truth — Kim is. An agent reading from the app will see stale data.
**Call it out:** *"You said the app is the source of truth for availability, but it sounds like changes come in through Kim by phone. Is there a lag between a nurse calling in and the app reflecting that? How long?"*

### C2 — Credential currency
**Listen for:** all credentials are verified before a nurse joins the roster.
**Then listen for:** when a credential lapses, MedFlex gets a state regulatory ping and re-verifies within a week.
**The gap:** there is a window — up to a week — where a nurse with a lapsed credential is on the active roster and could be placed. The 7% mismatch may live partly here.
**Call it out:** *"If a licence lapses mid-engagement, you might not know for up to a week. Could a nurse with a lapsed credential be matched and placed during that window?"*

### C3 — Quality score vs mismatch rate
**Listen for:** the 7% mismatch rate is hospital-flagged dissatisfaction.
**Then listen for:** we have a quality score, it is reliable.
**The gap:** if the quality score is reliable and coordinators use it, what is producing the 7% mismatch? Either the score does not capture the credential dimension, or it is not used in matching, or it is not as reliable as stated. This is likely why the prior recommendation engine failed.
**Call it out:** *"You have a quality score and a 7% mismatch rate. If the score is reliable and coordinators use it in matching, what is producing the mismatch? Is the score measuring credential fit, or something else — like satisfaction?"*

---

## 60-minute call plan

### Minutes 0–5 — Establish the real cost of the problem

**Goal:** get Marcus to quantify what unfilled and misfilled shifts actually cost. This anchors the ROI case before you have proposed anything.

- *"Before we go into process — when a shift goes unfilled, or the wrong nurse shows up, what does that cost MedFlex concretely? Revenue lost, client relationship, regulatory exposure?"*
- *"The two prior AI projects — before we talk about what we want to build, what specifically went wrong with each? Not at a high level — what did coordinators actually reject about the chatbot, and why did no one use the recommendation engine?"*

**What to listen for:** his answer on the prior failures tells you the failure mode to avoid. If he says "coordinators didn't trust it" — trust is the design constraint. If he says "hospitals didn't adopt it" — you are building coordinator-facing, not hospital-facing.

---

### Minutes 5–15 — Broad funnel: where does coordinator time actually go?

**Goal:** confirm or challenge the assumption that matching is the bottleneck, not something else.

- *"Walk me through what happens between a hospital submitting a shift request and a nurse showing up. Not the ideal version — what actually happens today."*
- *"Of the 4.2 hours average fill time, where does the time go? Is the delay in identifying candidates, reaching them, verifying credentials, getting hospital sign-off, or something else?"*
- *"When a coordinator has 120 decisions in a day, what does one decision actually look like? Is it a 2-minute task or a 20-minute task?"*
- *"What work do coordinators do that they feel only they can do — versus what feels like it could be done by anyone or anything?"*

**What to listen for:** if the 4.2 hours is mostly waiting for nurse responses, the fix is parallel outreach — the agent contacts multiple candidates simultaneously. If it is mostly compliance verification, the fix is pre-verified compliance status. The answer changes the architecture.

**When Marcus defers to Kim:** note the specific question he deferred. Ask: *"Can you give me your best read on it, and flag it as something to confirm with Kim?"* This keeps the session moving and signals which gaps need follow-up.

---

### Minutes 15–30 — Narrow funnel: the matching process in detail

**Goal:** understand how coordinators actually select a nurse — what criteria, in what order, from what systems.

- *"Take me through a real shift request from this week. Not a textbook case — one that came through and had to be filled. What happened, step by step?"*
- *"When you are looking at your candidate pool for a shift, how do you decide who to contact first? Is that documented anywhere, or does it live in the coordinator's head?"*
- *"What information does a coordinator need before they feel confident placing someone? Where does each piece of that information come from?"*
- *"[TRIGGER FOR C1] Where does a coordinator look right now to know which nurses are available? Is that always current?"*

**What to listen for:** any mention of the app being the source of truth — this sets up C1. Listen for "it depends on the coordinator" — that signals inconsistency in the matching process that an agent must account for.

---

### Minutes 30–45 — Lived vs documented: where the real process differs from the stated one

**Goal:** surface the gaps between how the process is supposed to work and how it actually works. This is where the contradictions are most likely to appear.

- *"Is there a standard process for how coordinators match nurses? How closely does what actually happens match it?"*
- *"[TRIGGER FOR C1] When a nurse calls in sick or becomes unavailable last minute, what is the actual chain of events? Who calls whom, and what gets updated where?"*
- *"[TRIGGER FOR C2] Credential verification — you said it is done before a nurse joins the roster. Once they are on the roster, how do you monitor whether their credentials stay current? What happens when something lapses?"*
- *"The 7% mismatch rate — when a mismatch happens, at what point does someone find out? Before the shift, when the nurse arrives, or after?"*
- *"[TRIGGER FOR C3] How do you measure the quality of a placement today? Is there a score or rating system?"*

**What to listen for:** any answer that contradicts something said in the first 15 minutes. Do not wait to call it out — do it in the moment.

---

### Minutes 45–55 — Delegation signals: what the agent can and cannot own

**Goal:** understand how much autonomy coordinators would accept from an agent, and what the consequences of an agent error look like.

- *"If an agent surfaced the top three candidates for a shift, ranked with a reason for each — would a coordinator act on that, or verify independently before contacting anyone?"*
- *"What percentage of shift requests fill cleanly — no judgment required — versus need a coordinator's intervention?"*
- *"When something goes wrong — wrong nurse placed, no-show, last-minute cancellation — who is accountable? Is it the coordinator, MedFlex as a business, or shared with the hospital?"*
- *"If the agent makes the wrong call on a placement and the wrong nurse shows up — what actually happens? To the hospital relationship, to MedFlex, to the nurse?"*
- *"What would the agent have to get right consistently before a coordinator would stop double-checking its recommendations?"*

**What to listen for:** the answer to the accountability question tells you where the human must stay in the loop. The answer to the trust question tells you what Wave 1 must demonstrate before Wave 2 is viable.

---

### Minutes 55–60 — Close and confirm

**Goal:** validate your understanding, surface any gaps, and agree on how to access Kim, Aaron, and Linda before Friday.

- *"Based on what you have told me, the biggest constraint on fill time seems to be [waiting for nurse responses / compliance verification / X]. Is that accurate, or is there something more significant I have missed?"*
- *"You mentioned Kim, Aaron, and Linda handle the operational, IT, and compliance detail. What is the best way to get specific questions to them before Friday? Even written answers would help."*
- *"One direct question before we close: when you say results in 8 weeks — is that a live agent in production, or a demonstrated reduction in fill time on a pilot cohort? The answer changes what we design."*

**The last question is the most important one in the call.** His answer tells you whether the 8-week scope is a hard deployment deadline or a proof-of-value milestone.

---

## If Marcus pushes back on solutioning

If he says *"That sounds like a chatbot"* or *"We tried something like that"* — do not defend the idea. Respond with:

*"Understood. What specifically did coordinators reject about the chatbot / not use about the recommendation engine? I want to make sure we are not repeating that."*

This turns his pushback into useful discovery data rather than a dead end.

---

## Questions that will get you marked as generic — avoid these

- "What are your pain points?"
- "Tell me about your current technology stack"
- "What does a typical day look like for your team?"
- "How do you currently handle compliance?"
- Any question that could have been written without reading the MedFlex brief

---

## After the call — run immediately

Paste your notes into Claude with this prompt:

```
Here are my notes from the MedFlex discovery call with Marcus Reyes.

[PASTE NOTES HERE]

Produce:
1. Every contradiction or inconsistency detected — quote what was said each time
2. Every question Marcus deferred to Kim, Aaron, or Linda — list the specific gap
3. The lived process for shift matching as described (not the SOP — what was actually said)
4. ATX delegation suitability signals — for each process discussed, what did Marcus say that indicates high or low suitability for an agent?
5. What I did not ask that I should have
```
