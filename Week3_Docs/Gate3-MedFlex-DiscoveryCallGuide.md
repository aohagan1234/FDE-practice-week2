# MedFlex Discovery Call Guide — Marcus Reyes
**Thursday 09:30–10:30. 60 minutes. Keep this open during the call.**

---

## Who is Marcus Reyes

Marcus Reyes is the CEO of MedFlex. He has a background in operations and growth — not engineering. He just closed a Series B and has board pressure to deliver significant growth within 24 months. He has seen two AI projects fail already and is impatient for something that actually works. He is confident, direct, and time-pressured. He will cut off questions that ramble or that could have been asked without reading the brief. He respects people who challenge his framing with substance and who demonstrate they have done their homework before walking in.

He is your primary point of contact through this engagement. He is not a technical stakeholder — he thinks in revenue, risk, and operational capacity. Frame everything in those terms.

---

## What to expect in the session

- Answers executive-layer facts precisely: numbers, board pressure, prior AI failures
- Defers operational detail to Kim (senior coordinator), Aaron (IT), Linda (compliance) — none of whom are available in the session
- Pushes back hard on premature solutioning: *"That sounds like a chatbot. We tried that."*
- Respects directness. Cuts off rambling. Ask one question at a time.
- When you catch a contradiction: call it out directly, no grandstanding. One sentence. He will acknowledge and defer resolution to the engagement.

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

### Opening — before the questions start

*Use this to set the tone in the first 60 seconds. Do not read it verbatim — adapt it.*

> "Marcus, thanks for making time. I have read the brief, so I am not going to ask you to explain what MedFlex does. What I want to do today is understand how the coordination work actually runs — not the intended process, but what actually happens when your coordinators are filling 120 shifts a day. I want to understand where the time goes, where things break, and what the last two projects did wrong. That will tell me what to build and what to avoid. I will ask focused questions. If I am heading in the wrong direction, push back."

---

### Minutes 0–5 — Establish the real cost of the problem

**Goal:** get Marcus to put a number on the cost of unfilled and misfilled shifts before anything else. This anchors the ROI case before you have proposed anything.

> **"Before we go into how the process works — when a shift goes unfilled, or the wrong nurse shows up, what does that actually cost MedFlex? I mean concretely: revenue lost, client relationship damage, regulatory exposure."**

> **"The chatbot and the recommendation engine — what specifically went wrong with each? Not 'it didn't work' — what did the hospitals or coordinators actually say when they rejected them?"** ⭐ Priority question

*Listen for:* "coordinators didn't trust it" → trust is the design constraint, not capability. "Hospitals rejected it" → build coordinator-facing, not hospital-facing. If the failure was about output format rather than logic, that is the most actionable signal.

---

### Minutes 5–15 — Where does coordinator time actually go?

**Goal:** confirm whether matching is the actual bottleneck or whether something else is eating the time.

> "Walk me through what happens between a hospital submitting a shift request and a nurse showing up. Not the ideal version — what actually happens today."

> "Of the 4.2 hours average fill time, where does the time go? Is the hold-up in finding candidates, reaching them, verifying credentials, getting hospital sign-off, or something else?"

> "When a coordinator has 120 decisions to make in a day, what does one decision actually look like? Is it a 2-minute task or a 20-minute task?"

> "What work do coordinators do that they feel only they can do — versus what feels like it could be done by anyone or anything?"

*Listen for:* if the 4.2 hours is mostly waiting for nurse responses, the fix is parallel outreach. If it is mostly compliance verification, the fix is pre-verified compliance status. The answer changes the architecture.

*When Marcus defers to Kim:* note what he deferred. Ask: *"Can you give me your best read on it, and flag it as something to confirm with Kim?"*

---

### Minutes 15–30 — The matching process in detail

**Goal:** understand how coordinators actually pick a nurse — what they weigh, in what order, and where judgment lives.

> "Take me through a real shift request from this week. Not a textbook example — one that came through and had to be filled. What happened, step by step?"

> **"When a coordinator picks a nurse for a shift, what is the actual moment of decision? What are they weighing? What makes one nurse the right call over another for a specific shift?"** ⭐ Priority question

*Listen for:* if the answer is codifiable — credentials plus proximity plus availability — the agent can lead the matching. If the answer is relationship knowledge — "Dr Chen prefers nurses who have worked his floor before" — it requires a different architecture. This determines whether Wave 1 can include matching or must start with something simpler.

> "What does a coordinator need to know before they feel confident placing someone? And where does each piece of that come from?"

> **[Trigger for C1]** *"Where does a coordinator look right now to know which nurses are available? Is that always current?"*

---

### Minutes 30–45 — Where the real process differs from the stated one

**Goal:** surface the gap between how the process is supposed to work and how it actually works. This is where the contradictions are most likely to appear.

> "Is there a standard process for how coordinators match nurses? How closely does what actually happens match it?"

> **[Trigger for C1]** *"When a nurse calls in sick or goes unavailable last minute, what is the actual chain of events? Who calls whom, and what gets updated where?"*

> **[Trigger for C2]** *"On credential verification — you said it is done before a nurse joins the roster. Walk me through a real verification. A coordinator gets a shift request — how do they actually check that nurse is credentialed for that facility type?"* ⭐ Priority question

> **"The 7% mismatch rate — is that the coordinator picking the wrong nurse, credentials being out of date, or the hospital's requirements being unclear? Which is it, mostly?"** ⭐ Priority question

*Listen for:* different root causes need different fixes. Wrong pick = better matching logic. Stale credentials = real-time verification pipeline. Unclear requirements = better job order intake. Building the wrong fix leaves the mismatch rate unchanged.

> **"The 12% no-show rate — what is driving that? Is it nurses cancelling, nurses not confirming, double-booking, or something else?"** ⭐ Priority question

*Listen for:* if no-shows are predictable — nurses with a history of no-shows, certain shift types — an agent can flag risk at placement time. If they are unpredictable, the agent needs rapid backfill capability instead. These require different architectures.

> **[Trigger for C3]** *"How do you measure the quality of a placement today? Is there a score or rating system?"*

*Do not wait until the end to call out contradictions — do it in the moment.*

---

### Minutes 45–55 — What the agent can and cannot own

**Goal:** understand how much autonomy coordinators would accept from an agent, and what happens when the agent gets it wrong.

> "If an agent surfaced the top three candidates for a shift, ranked with a reason for each — would a coordinator act on that, or verify independently before contacting anyone?"

> "What percentage of shift requests fill cleanly — no judgment required — versus need a coordinator's intervention?"

> "When something goes wrong — wrong nurse placed, no-show, last-minute cancellation — who is accountable? Is it the coordinator, MedFlex as a business, or shared with the hospital?"

> "If the agent makes the wrong call on a placement and the wrong nurse shows up — what actually happens? To the hospital, to MedFlex, to the nurse?"

> "What would the agent have to get right consistently before a coordinator would stop double-checking its recommendations?"

*Listen for:* the accountability question tells you where the human must stay in the loop. The trust question tells you what Wave 1 must demonstrate before Wave 2 is viable.

---

### Minutes 55–60 — Close and confirm

**Goal:** validate your understanding, surface any gaps, and agree on how to reach Kim, Aaron, and Linda before Friday.

> "Based on what you have told me, the biggest constraint on fill time seems to be [waiting for nurse responses / compliance verification / X]. Is that accurate, or is there something more significant I have missed?"

> "You mentioned Kim, Aaron, and Linda handle the operational, IT, and compliance detail. What is the best way to get specific questions to them before Friday? Even written answers would help."

> **"One direct question before we close: when you say results in 8 weeks — is that a live agent in production, or a demonstrated reduction in fill time on a pilot cohort? The answer changes what we design."** ⭐ Priority question

*This is the most important question in the call.* His answer tells you whether the 8-week scope is a hard deployment deadline or a proof-of-value milestone.

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
