# DELIVERABLE 6 — DISCOVERY QUESTIONS FOR THE MAIN STAKEHOLDER

**Scenario:** Apex Distribution Ltd (Gate 2)  
**Stakeholder:** Sarah Whitmore, COO  
**Purpose:** Questions whose answers would *materially change* the agent design — not generic process discovery.

Each question states what changes in the design if the answer is X versus Y.

---

## PRIORITY TIER 1 — Answers that change Phase 1 architecture

These three questions directly affect whether the ETA agent (D4) can be built as specced.

---

### Q1 — Driver App API surface

> "When the ETA agent needs a driver's current location to calculate a tight ETA, can it programmatically query the driver app for GPS coordinates and route sequence — via an API call? Or is the only available channel a message to the driver asking them to reply with their location?"

**Why this matters:**

- **If GPS API exists:** Agent can calculate ETA deterministically without driver involvement. Response time is <30 seconds. Driver non-response becomes irrelevant.
- **If message-only (no GPS API):** Agent must send a message and wait up to 2 minutes for the driver to reply. The 2-minute wait + fallback protocol in D4 is the correct design, but it introduces a 2-minute floor on ETA response time. SLA becomes "< 3 min," not "< 1 min."
- **If no API at all (driver app is closed/internal with no external integration surface):** The ETA agent cannot directly contact drivers. It can only read CRM status and give customers the last-known ETA window. This is a significant capability reduction — agent becomes a lookup tool, not an ETA generator.

---

### Q2 — CRM delivery status freshness

> "When a driver scans a package on delivery, how long before that status update appears in Salesforce CRM? Is it pushed immediately via a webhook, polled every few minutes, or batched end-of-shift?"

**Why this matters:**

- **If real-time (webhook, <1 min lag):** The ETA agent can trust CRM status as current. An "out-for-delivery" status means the package is genuinely still in transit. ETA accuracy is limited only by driver location freshness.
- **If 5–30 min polling:** CRM status is a lagging indicator. The agent must include a staleness disclaimer in every response: *"Status as of [timestamp] — may be a few minutes behind."* ETA accuracy target in D4 (±15 min) may need widening.
- **If end-of-shift or end-of-day batch:** "Out-for-delivery" in CRM at 3pm might mean the driver left the depot at 7am with no updates since. The agent cannot reliably distinguish "in transit" from "already delivered but CRM not updated." This breaks the core ETA logic and requires a full redesign — the agent must call the driver for every active delivery, not just edge cases.

---

### Q3 — The Sandra credit audit trail gap

> "In one of your customer email threads, I can see a £170 goodwill credit was applied to Hayes & Sons by a member of your billing team — but the internal note says it didn't appear in the credits audit log. Is that a known issue, or was this credit applied via a method that's off-policy? And does the Aurum credits batch export capture all credits actually applied to customer accounts, or only credits entered through the standard Aurum workflow?"

**Why this matters:**

- **If it's a known gap and manual overrides routinely bypass the export:** The `APEX_CREDITS` file is an incomplete record of credits applied. Any Phase 2 billing agent that uses this file to check if a dispute has been resolved will misidentify live disputes as unresolved, triggering duplicate resolution attempts. The compliance exposure — credits applied without audit trail — is also significant and should be flagged to Sarah directly.
- **If it's off-policy (Sandra shouldn't have done it):** The audit trail is theoretically intact; this is a process adherence problem. Phase 2 billing agent can enforce the structured path by refusing to accept disputes as "resolved" unless the audit trail entry exists. Solves the compliance risk automatically.
- **If the export is complete:** The internal note in Artefact 2 is wrong or refers to a lag (credit was applied but not yet in yesterday's batch). Lower risk — just a timing issue.

---

## PRIORITY TIER 2 — Answers that change Phase 2 architecture or risk profile

These questions affect the billing dispute agent design (W4, Phase 2) and overall system risk.

---

### Q4 — Aurum schema change notification

> "The previous RPA project for billing reconciliation broke when Aurum's schema changed. Does Apex receive any advance notice of those changes — even informal, like a support email or a ticket from the Aurum vendor? Or does a schema change just appear one morning in the batch files without warning? And is Aurum managed by an external vendor, or does your IT team control the schema directly?"

**Why this matters:**

- **If Aurum is self-hosted and Apex IT controls the schema:** The risk is internal. Apex IT can coordinate schema changes with the team building the agent. Advance notice is achievable. This is manageable.
- **If Aurum is vendor-managed and schema changes arrive without notice:** This is exactly what broke the RPA. Any agent ingesting Aurum batch files needs schema validation as a first-class feature — a config file of expected columns that is checked before every parse. Without it, a column rename silently corrupts 24 hours of dispute processing before anyone notices.
- **If there's a support contract that specifies notice period:** Negotiate a minimum 2-week schema change notice into the contract renewal. This single contractual change reduces the ongoing maintenance cost of any Aurum-dependent agent significantly.

---

### Q5 — Fuel surcharge calculation logic

> "In the fuel surcharge export, I can see route R-008 has three invoices all on tier T3 — but the fuel percentages differ: 11.97%, 9.37%, and 12.00%. Is the fuel percentage within a tier a fixed rate, or does it vary by customer contract or some other variable? And is the rate calculation done entirely within Aurum, or does it pull external data like live fuel prices?"

**Why this matters:**

- **If the percentage is fixed per tier:** The 9.37% figure is a data quality anomaly — a potential billing error in one of those invoices. Hayes & Sons has three open FUEL_SURCH_DAMAGE disputes; if there's a systemic calculation error on R-008, that explains the pattern and changes the dispute resolution logic.
- **If the percentage is contract-specific within a tier:** The surcharge calculation requires the customer's rate card at calculation time. The `APEX_CUSTOMER_MASTER` file (monthly) contains RATE_CARD but not the rate percentage — there's a missing join table. A Phase 2 billing agent cannot verify surcharge accuracy without access to the rate card detail, which isn't in any of the seven batch exports.
- **If it pulls live fuel prices:** There's a dependency on an external data source not mentioned in the brief. Schema drift risk is compounded by data source availability risk.

---

### Q6 — Dispatch console API surface

> "The dispatch console is described as having a 'limited API surface.' What does limited mean specifically — can an agent read current route assignments and driver positions from it? And can it write to the console — for example, to confirm a route change or re-assign a driver — or is it read-only?"

**Why this matters:**

- **If read + write API:** W3 (dispatch adjustments, 90/day, 18 min each) has a viable agentic path. An agent can read the current route state, generate a proposed re-routing, and commit it if the dispatcher approves. This is currently scoped out (D4 Phase 1), but becomes the most time-intensive target for Phase 2.
- **If read-only API:** Agent can surface data (current route, driver location, available drivers) but cannot act. This is "human-led with agent support" for all W3 tasks — saves some time but doesn't free headcount.
- **If no functional API (Citrix virtual desktop only):** W3 automation is only achievable via screen automation — exactly the approach that failed with Aurum. Recommend explicitly scoping W3 out until the console is replaced or a real API is exposed.

---

## PRIORITY TIER 3 — Answers that calibrate volume, risk, or SLA assumptions

---

### Q7 — Why the chatbot failed

> "You mentioned the 2024 chatbot failed because customers hated it. Do you know specifically what they hated — was it the bot format itself (they didn't want to talk to a bot), was it the quality of responses (it gave wrong ETAs), or was it integration problems (it couldn't actually pull live data)? This changes what guardrails the ETA agent needs."

**Why this matters:**

- **If customers hated the bot format:** The ETA agent's UX must be invisible — responding via the customer's existing SMS or app channel, not a new chatbot interface. The agent replies as "Apex Customer Service," not as "Apex Bot." No chatbot persona.
- **If it gave wrong ETAs:** Data quality is the real risk. Need to lock down CRM status freshness (Q2) and driver response latency (Q1) before go-live. Consider a confidence threshold: if the ETA calculation has low confidence (driver non-responsive, CRM status stale), respond with a range rather than a point estimate.
- **If it couldn't pull live data:** The ETA agent's CRM and Driver App integrations are business-critical — not optional. If those integrations are unreliable, the agent has the same failure mode. Integration testing in Week 5 (canary rollout) is non-negotiable.

---

### Q8 — Peak volume and staffing

> "The 400 ETA inquiries per day — is that a typical Monday–Thursday average? How much do volumes spike on the day before a public holiday or during Christmas? And how often does the 35-person team run below full strength — sick days, part-time, vacancies?"

**Why this matters:**

- **If peak volumes are 2×–3× average:** Agent SLA targets (>80% resolution, <5 min response) must be tested at peak load — 800–1,200 inquiries in a day, not just 400. Salesforce API rate limits and driver app messaging capacity become relevant at peak.
- **If team regularly runs below 35 people:** The "4 min avg handling time" is already under pressure. The baseline for the ROI case in D3 may be understated — current agents are handling more than 400/day or the SLA is already being missed. Agent value is higher than modelled.
- **If volumes are flat year-round:** The ROI case is as modelled. No adjustment needed.

---

### Q9 — Credit authority and approval threshold

> "Does Apex have a documented threshold below which a billing agent (or a junior agent) can approve a goodwill credit without sign-off, and above which a manager needs to approve? Or is every credit decision currently at individual discretion — like Sandra's £170?"

**Why this matters:**

- **If a threshold exists (e.g., < £100 self-approve, ≥ £100 needs sign-off):** The Phase 2 billing agent can be designed to auto-apply credits below the threshold — routing the customer a resolution within minutes for small disputes. Credits above threshold go to a manager approval queue. Clear automation boundary.
- **If it's currently at individual discretion:** There is no clean delegation surface. A Phase 2 billing agent cannot act autonomously on credits without a policy change. Sarah needs to define the threshold before build starts. Recommend this as a pre-build governance step.

---

### Q10 — Customer inquiry channel and CRM recording

> "When a customer sends an ETA inquiry via SMS, does that message arrive into Salesforce CRM as a case — with the inquiry channel (SMS, call, email, portal) recorded? Or does it arrive via a separate SMS gateway and then get manually logged?"

**Why this matters:**

- **If channel is recorded in CRM:** Agent can read the inquiry channel from the CRM case and reply on the same channel. Single-channel integration needed.
- **If channel is not recorded:** Agent defaults to one reply channel (SMS) and may send a response to the wrong medium for customers who called in or used a portal. Requires either a channel-routing layer or explicit agreement with Sarah that Phase 1 is SMS-only.
- **If ETA inquiries don't all go through CRM (some are direct calls, some are SMS to a separate line, some are emails):** Multi-channel normalisation is a Phase 1 prerequisite — the agent's "400/day" intake is actually several parallel channels that need to be unified before the agent can handle them all.

---

## DETECTION NOTES FOR THE LIVE ROUND

Sarah is described as likely to hedge, give vague answers, or redirect rather than admit she doesn't know. For each question above, the signal to watch for:

- **"I'd have to check with IT"** on Q1/Q6 → API surface is genuinely unknown. This is a HIGH risk — follow up: *"If it turned out there was no API, would you be willing to fund exposing one before we build?"*
- **"I think it's real-time"** on Q2 → This is a guess. Push: *"Can you put a number on it — is it seconds, minutes, or longer?"*
- **"That shouldn't have happened"** on Q3 → Sandra's override is off-policy. The audit trail gap is a compliance problem Sarah may not want to acknowledge. Follow up: *"Is this the first time you've seen this, or does it happen regularly with manual credits?"*
- **"It varies"** on Q8 → This is the answer for almost every volume question. Push: *"What's the highest single day you've ever seen? What week of the year?"*
- **Redirecting Q7 ("the chatbot was just bad")** → Press for specifics: *"If you had to choose one reason — wrong answers, wrong format, or couldn't pull data — which was the biggest complaint?"*
