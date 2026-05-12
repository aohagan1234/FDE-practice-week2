# Gate 3 — MedFlex Scenario Preparation
**Updated with full scenario brief. Verified against Gate3-Participant-Pack.**

---

## Confirmed facts

| Fact | Value |
|---|---|
| Company | MedFlex, healthcare staffing agency |
| Size | 200 employees, 5-state US region |
| Model | B2B (hospital systems) + B2C (travel nurses) |
| Coordinators | 8, matching nurses to shifts manually |
| Decisions per coordinator per day | ~120 |
| Average time to fill a shift | 4.2 hours |
| Target fill time | Under 1 hour |
| Mismatch rate (wrong credentials for facility) | 7% |
| No-show rate | 12% |
| Stakeholder | Marcus Reyes, CEO. Series B closed. Board wants significant growth in 24 months. |
| Prior AI failures | Chatbot (hospital staff rejected it) + recommendation engine (nobody used it) |
| Engagement goal | "10x the business without 10x-ing the coordinators" — in 8 weeks |

**Out of scope (named explicitly — do not drift into these):**
- Hospital-facing portal for shift submission
- Nurse-facing mobile app
- Pricing engine / margin optimisation
- Continuing-education renewal automation

---

## What the numbers actually tell us

**120 decisions per coordinator per day** means roughly one decision every 4 minutes across an 8-hour day. At 4.2-hour average fill time, the bottleneck is not the decision itself — it is the waiting. Coordinators are likely spending time identifying candidates, then waiting for responses sequentially, then re-checking compliance, then confirming with the hospital. Each handoff adds delay.

**The 4.2 → 1 hour target is a 76% reduction in fill time.** This is not achievable by making coordinators faster. It requires eliminating the waiting from the critical path — which means parallel outreach to multiple candidates simultaneously, compliance pre-verified before the shift request arrives, and hospital confirmation automated where possible.

**7% mismatch rate** — wrong credentials for the facility type. With 8 coordinators each making 120 decisions per day, that is roughly 67 mismatches per day. Each mismatch is a placed nurse who cannot legally or contractually work that shift. This is a compliance risk, a client relationship risk, and a revenue risk. It suggests the matching step is either not checking facility-specific credential requirements reliably, or those requirements are not codified clearly enough to check.

**12% no-show rate** is very high. Not all of this is solvable by an agent — some no-shows are personal emergencies. But a portion are preventable: nurses who accepted but weren't properly confirmed, double-booked nurses, or commitments made without a formal acknowledgement. Better confirmation workflows with hard deadlines can reduce this. The remainder is a behavioural/supply problem, not a coordination problem.

---

## What "10x without 10x-ing" actually requires

The coordination bottleneck is the constraint on growth. More hospital contracts = more shift requests = more matching decisions. At 120/coordinator/day with 8 coordinators, the ceiling is approximately 960 decisions/day. To 10x, you would need either 80 coordinators or you need coordinators to handle 10x the volume each. Neither is realistic without fundamentally changing what coordinators do.

The question the architecture must answer is: which of the 120 daily decisions require a coordinator, and which can the agent handle end-to-end?

---

## Agentic vs deterministic analysis

### Deterministic — scheduled job or rule-based workflow, not an agent

| Task | Why deterministic | Implementation |
|---|---|---|
| Credential / licence expiry alert | Check expiry date vs today + threshold. No judgment. | Scheduled job: daily check, alert at 30 / 14 / 7 days |
| Basic availability filter | Is the nurse marked available for this date and time? Binary lookup. | Rule-based filter at job order intake |
| Proximity filter | Is the nurse within acceptable distance of the facility? Distance calculation. | Rule-based filter |
| Shift confirmation reminder | Send reminder N hours before shift if not confirmed. No judgment. | Scheduled job: time-triggered |
| No-show flag and escalation | If nurse has not confirmed by T-4h, flag to coordinator. | Scheduled job with threshold |
| Hospital notification on fill | When shift is confirmed, notify the hospital. No judgment. | Triggered workflow on status change |
| Compliance status lookup | Query state regulatory database for licence status. Return current / lapsed / expired. | API call, deterministic output |

### Genuinely agentic — requires reasoning over context

| Task | Why agentic | What the agent reasons over |
|---|---|---|
| Candidate ranking for a job order | The right candidate depends on credential match, proximity, nurse preference, hospital preference, past performance at that facility, response rate, and current workload — not reducible to a single rule | All of the above, simultaneously, per job order |
| Parallel outreach sequencing | Which candidates to contact, in what order, via what channel, with what timing — given urgency and the nurse pool's known response patterns | Urgency of fill, channel preference, expected response latency, pool depth |
| Mismatch prevention on ambiguous requirements | Hospital says "ICU-certified preferred." Nurse has step-down ICU experience. Does that qualify? Requires reading the facility's actual requirement and the nurse's credential detail, not just checking a boolean | Facility requirement text + nurse credential detail + precedent from prior placements at that facility |
| Cancellation recovery | Last-minute cancellation — who to contact first, given time pressure, that this is a specific facility with specific requirements, and that the standard pool may already be partially committed | Same as candidate ranking but with time constraint and reduced pool |
| Job order triage and interpretation | Job orders arrive by email, portal, and phone. Inconsistent format. Agent must extract the structured data — shift date, time, facility, specialism, credential requirements — from unstructured input before matching can begin | Natural language understanding of job order text |

---

## The prior failure modes — do not repeat these

**The chatbot** — hospital staff rejected it. Hospital-facing. Likely tried to replace the relationship layer (how hospitals communicate with MedFlex) without solving the operational problem underneath. Hospitals did not want a chatbot; they wanted their shifts filled quickly.

**The recommendation engine** — nobody used it. Coordinator-facing. Most likely ranked candidates by a scoring algorithm that coordinators did not trust, because the score did not account for the things coordinators actually care about (relationship history with specific facilities, recent nurse behaviour, edge-case credential nuances). No explanation of why the candidate was recommended = no trust.

**The common failure pattern:** both projects automated at the interface layer without fixing the operational layer underneath. The agent design must work from the inside out — fix the matching and compliance verification first, then surface it to coordinators in a way they will actually use.

---

## Discovery questions for the call

### Minutes 0–5 — Context setting

- "Before we go into the detail — when a shift goes unfilled or misfilled, what does that actually cost MedFlex? I want to understand what we are solving against."
- "You mentioned two prior AI projects. Before we talk about what we want to build, can you tell me what those projects were supposed to do and why they did not work?"

### Minutes 5–15 — Broad funnel

- "Walk me through what happens in your operations between the moment a hospital submits a shift request and the moment a nurse shows up. Not the ideal version — what actually happens today."
- "Of the 4.2 hours average fill time, where does the time go? Is the delay in finding a candidate, reaching them, verifying credentials, or something else?"
- "When a coordinator has 120 decisions to make in a day, what does 'making a decision' actually look like? Is it a 2-minute task or a 20-minute task?"

### Minutes 15–30 — Narrow funnel (the matching process)

- "Take me through a real shift request from this week. Not a textbook case — one that actually came through. What happened?"
- "When you identify potential nurses for a shift, how do you decide who to contact first? Is that written down, or is it in the coordinator's head?"
- "You said the mismatch rate is 7%. When a mismatch happens, at what point does someone find out — before the shift, when the nurse arrives, or after?"
- "What does it mean for a nurse to be 'available'? How does your system know? Who updates that?"

### Minutes 30–45 — Lived vs documented

- "Is there a standard process document for how coordinators match nurses to shifts? How closely does what actually happens match that process?"
- "When a nurse calls in sick or cancels, what is the actual chain of events? Who calls whom, and what gets updated where?"
- "Credential verification — you said it is done manually against state databases. Walk me through that. Which database, how often, who does it?"
- "You mentioned a quality score. What does that score measure, and is it used in the matching decision today?"

### Minutes 45–55 — Delegation signals

- "If an agent surfaced the top three nurses for a shift with a reason for each recommendation — would a coordinator act on that, or would they verify independently before contacting anyone?"
- "What percentage of shift requests fill cleanly versus require coordinator judgment or intervention?"
- "When something goes wrong — wrong nurse placed, no-show, last-minute cancellation — who is accountable? How is that tracked?"
- "If the agent makes the wrong call on a placement and the wrong nurse shows up, what happens? To MedFlex, to the hospital, to the nurse?"

### Minutes 55–60 — Close

- "Based on what you have told me, the biggest lever seems to be the time from shift request to first nurse contact. Is that where you would focus, or is there something more important I have missed?"
- "You mentioned Kim, Aaron, and Linda handle the operational, IT, and compliance detail. Before Friday, what is the best way to get the specific questions I have in front of them?"

---

## The three planted contradictions — catch these

These are the specific contradictions signalled in the brief. The actual session may use different wording but the same underlying gaps. Flag each directly when you hear it — do not wait until the end.

### Contradiction 1 — Nurse availability data

**What Marcus will likely say early:** "Our app is the source of truth for nurse availability."

**What he will likely say later:** "When a nurse calls in sick they call Kim, and Kim updates the schedule by hand."

**Why it matters:** If Kim is updating manually by phone call, the app is not the source of truth — Kim's notes are. If the agent reads from the app, it will see stale data and make matches against nurses who are no longer available. The agent's data foundation is broken before it starts.

**How to call it out:** "You said the app is the source of truth for availability, but it sounds like changes come in through Kim by phone and get updated manually. Is there a lag between a nurse calling in and the app reflecting that? How long?"

---

### Contradiction 2 — Credential verification completeness

**What Marcus will likely say early:** "All credentials are verified before a nurse joins our roster."

**What he will likely say later:** "When a credential lapses we get a state regulatory ping and we re-verify within a week."

**Why it matters:** Initial verification is done once at onboarding. But credentials lapse. If the re-verification happens within a week of a state ping, there is a window — potentially days — where a nurse is on the active roster with a lapsed credential and could be placed. The 7% mismatch rate may partly live in this gap.

**How to call it out:** "You said credentials are verified before a nurse joins the roster. But if a licence lapses mid-engagement, it sounds like you might not know for up to a week. Could a nurse with a lapsed credential be matched and placed during that window?"

---

### Contradiction 3 — The quality score vs the mismatch rate

**What Marcus will likely say:** "The 7% mismatch rate is hospital-flagged dissatisfaction." And later: "We have a quality score. Trust me, it's reliable."

**Why it matters:** If the quality score is reliable and coordinators have access to it, why is the mismatch rate 7%? Either the quality score does not capture the credential dimension (it measures satisfaction, not compliance fit), or it is not being used in the matching decision, or it is not as reliable as stated. The prior recommendation engine may have been built on this score — which would explain why coordinators did not trust it.

**How to call it out:** "You mentioned a quality score and you described a 7% mismatch rate. If the quality score is reliable and coordinators use it, what is causing the 7%? Is the score measuring the same thing as the mismatch — credential fit — or something different, like satisfaction?"

---

## Engaging Marcus Reyes

**What works with Marcus:**
- Lead with numbers and outcomes, not system descriptions
- Challenge framing directly when it does not add up — he respects it
- Short questions. He cuts off rambling.
- Acknowledge the prior failures without apologising for them — treat them as useful information, not embarrassing history

**What will get you pushed back:**
- Proposing a solution before you have diagnosed the problem ("That sounds like a chatbot. We tried that.")
- Asking generic questions that could have been written without reading the brief
- Accepting surface answers on the contradictions
- Committing to the 8-week scope without interrogating what "results" means to him

**The 8-week question to ask Marcus directly:**
"When you say results in 8 weeks — what does a result look like to you specifically? A live agent in production, or a demonstrated reduction in fill time on a pilot cohort?"

The answer will tell you whether the 8 weeks is a hard deployment deadline or a proof-of-value milestone. The architecture changes depending on which it is.

---

## Likely architecture based on confirmed facts

**The real problem is fill time, not coordinator headcount.**

4.2 hours to fill a shift is predominantly waiting time — waiting for nurse responses, waiting for compliance checks, waiting for hospital confirmation. An agent that runs these in parallel rather than sequentially collapses the fill time without replacing the coordinator's judgment.

**The agent's primary job:** take a job order, pre-filter on deterministic criteria (available, compliant, proximity), rank the remaining candidates using context-dependent reasoning (facility fit, preference history, response rate), contact the top candidates in parallel, track responses, and surface the first confirmed match to the coordinator for final approval.

**What remains human:** the final placement decision. The coordinator reviews the agent's recommended match with reasons, approves or overrides, and the hospital is notified. The agent executes; the coordinator controls.

**Wave 1 scope (8 weeks):**
The tightest path to a demonstrable result in 8 weeks is an agent that handles job order intake through to first-contact confirmation — the first half of the fill cycle. Deterministic compliance filtering, agentic outreach sequencing, parallel contact, response tracking, escalation to coordinator if no fill within a target window. This alone should reduce fill time from 4.2 hours to under 2 hours and demonstrate the infrastructure for Wave 2.

**Wave 2:** full candidate ranking with facility-specific credential reasoning, mismatch prevention on ambiguous requirements, no-show prediction and mitigation.
