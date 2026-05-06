# Presentation Prep — Gate 2: Apex Distribution Ltd

**Format:** 7 minutes total. 4 minutes presenting. 3 minutes Q&A.  
**Assessed on:** Rigour of cognitive work mapping, delegation calls, agent purpose. Ability to defend boundaries and name trade-offs.

---

## 4-Minute Script

*Spoken at ~130 wpm ≈ 520 words. Timings are guides, not hard stops.*

---

### [0:00–0:30] Hook — the problem in one number

> "Apex Distribution's Customer Operations team handles 730 interactions a day. Four hundred of those are ETA inquiries — 'where is my delivery?' They take four minutes each. That's 26.7 person-hours a day on a task that is, in 80% of cases, a database lookup followed by a template reply. That's the before. Here's what the after looks like."

---

### [0:30–1:30] Before — current process, where the load and failures sit

> "Today the work runs in two cognitive zones. Zone A: an agent looks up the consignment in Salesforce CRM, reads a status enum — pre-dispatch, out-for-delivery, delivered, exception — and decides what to reply. This is deterministic. There's no judgment. It takes under a minute."

> "Zone B is where the load sits. If the consignment is active — out for delivery — the agent has to get a tighter ETA. Right now that means contacting dispatch, who contacts the driver, who may or may not respond. Artefact 3 shows this taking 10 minutes in practice — the customer asked at 11:14 and got a 'best guess' at 11:24, after a manual GPS ping through dispatch. The 4-hour window dissatisfied the customer before they even started."

> "The failures: CRM status lags 5–10 minutes behind reality. The SOP references DispatchHub, which was retired in October 2024. Driver non-response is routine, not exceptional — but the current process treats it as an edge case. And there's no deduplication: the same customer asking twice in an hour generates two separate driver queries."

---

### [1:30–2:45] After — the redesigned process, which steps are agentic, hybrid, human

> "The redesigned process has three layers."

> "**Workflow layer — fully agentic.** Consignment ID validation, CRM lookup, all five status branches, and inquiry deduplication. These are deterministic rules operating on real-time API data. No judgment, no discretion. An event-driven API wrapper handles 95% of the happy path. I want to be precise: this is not an LLM agent — it's a rule engine. Applying LLM inference to a database lookup is over-engineering."

> "**Agent layer — agent-led with human oversight on exceptions.** The out-for-delivery path. The agent contacts the driver via the driver app, waits up to 2 minutes, and either generates a tight ETA from GPS data or sends the fallback window — 13:00 to 17:00 — and closes the case. Escalation to a dispatcher is optional and only triggers if the customer has explicitly requested a tighter ETA. This path is handled by the agent; the human is not in the loop on the main path."

> "**Human layer.** Three cases remain human-led: consignment not found in CRM — manual records exist that only a human can check. Exception flag — the CRM has the reason, but what happens next requires dispatcher judgment. And null status — a data error that needs IT investigation, not a template reply."

---

### [2:45–4:00] Why — defend the key delegation calls

> "Three calls I want to defend explicitly."

> "**Why is driver non-response fully agentic?** Because the fallback is a timeout rule, not a decision. If two minutes pass with no response, send the template. There's no judgment in that — the message is pre-approved, the trigger is a clock. Moving this to human-in-the-loop adds 3–5 minutes and defeats the SLA. The agent doesn't decide what to do; it executes a pre-specified rule."

> "**Why is consignment lookup workflow and not LLM?** Because it's a switch statement on five enum values. CRM returns a status; the agent reads it and selects a template. Hallucination risk is real on LLM calls; it's zero on a database query. The workflow layer is faster, cheaper, and strictly safer."

> "**Why is exception handling human-led?** Not because the lookup is hard — the exception reason is in CRM. It's because the decision that follows — retry tomorrow? insurance claim? goodwill credit? — requires knowledge of customer history, dispatcher availability, and insurance pre-auth that no deterministic rule can encode. The agent surfaces the data. The dispatcher makes the call."

---

## Q&A Prep — Likely Probe Points

*Each answer should be under 30 seconds. Name the principle, then give the specific rationale. Don't expand unless pushed.*

---

**"Why is the driver non-response path agentic? Shouldn't a human check whether to escalate?"**

> The escalation decision is already pre-specified in the design. If `explicit_tight_eta_requested = true`, escalate. If not, send fallback and close. There's no runtime judgment — the human made the judgment when they approved the protocol. The agent executes it. If the rule turns out to be wrong, you update the rule, not the delegation archetype.

---

**"What if the agent sends a fallback window and the driver actually delivers 30 minutes early?"**

> That's the CRM lag problem — status is 5–10 minutes behind reality. The design names this explicitly as an acceptable variance, not a failure mode. The reply template includes: "Status may be a few minutes behind real-time." For a service-level SLA miss — which this is — that's the right trade-off. The alternative is halting every inquiry until the status is verified, which kills the SLA entirely.

---

**"Why can't the agent check manual records for consignments not found in CRM?"**

> Manual records are paper manifests, shipper emails, and hand-written notes. There's no API surface. An agent cannot read a paper manifest. The only option is screen automation on the manual lookup queue, which is exactly the approach that failed with the Aurum RPA. Human escalation is not a failure of ambition — it's the correct delegation call when the data source is analogue.

---

**"You said intent detection is keyword-based, not LLM. Couldn't an LLM do it better?"**

> Possibly more accurately — but the cost and latency are wrong for this task. "Urgent," "exact time," "by 2pm," "need to know" — these are a finite list. A keyword match is deterministic, auditable, zero-latency, and zero hallucination risk. If the keyword list misses a phrase, you add the phrase. Using an LLM for a keyword check adds inference cost, response time, and a failure mode (LLM decides someone is "urgent" when they're not). Save the LLM for tasks where rules genuinely can't encode the judgment.

---

**"What's your evidence that 80% autonomous resolution is achievable?"**

> The 80% target is derived from the automation potential score in the delegation matrix. Of the five status paths, four are fully agentic (delivered, pre-dispatch, exception-flag, null). The fifth — out-for-delivery — splits 80/20 by driver response rate. The 20% that escalate are: consignment not found (~5% of volume) and driver non-responsive cases where the customer explicitly wants a dispatcher (the 10% optional path). Combined, that's roughly 15–20% escalation rate, which maps to >80% autonomous. It's an estimate, not a guarantee — the canary rollout in Week 5 is where you validate it against real volume.

---

**"W4 — billing disputes. You've scoped it to Phase 2. Why not now?"**

> Two reasons. First, Aurum is batch-only with a 24-hour lag and schema changes without notice — that's exactly what broke the RPA project. Building a billing agent before W2 has proven value means funding a higher-risk project on an unproven track record. Second, Sarah has watched two projects fail. W2 gives her a working agent in six weeks. That win — visible, measurable, 2.8 FTE freed — is what makes the W4 conversation possible. Proposing W4 first is technically interesting and commercially poor.

---

**"What happens if the Salesforce CRM API goes down?"**

> The agent detects an API timeout, escalates to the manual inquiry queue immediately, and sends the customer: "We're experiencing a temporary system issue — a member of our team will contact you shortly." No silent failure. The failover is the same queue that handles inquiries today — it just gets more volume until CRM recovers. The agent monitors CRM availability as a secondary KPI.

---

## The Two Things to Say Unprompted If Time Allows

These signal that the analysis went beyond the scenario brief into the actual artefact data. Only raise them if the presentation flows ahead of time — don't force them.

1. **Sandra credit audit gap:** "One thing I found in the CSV data — Sandra's £170 goodwill credit for Hayes & Sons doesn't appear in the APEX_CREDITS batch export. That's a compliance gap: credits applied but no audit trail. A Phase 2 billing agent that enforces the structured credit entry path closes this automatically — it makes the non-audited override path structurally unavailable."

2. **Fuel surcharge anomaly:** "Route R-008 has three invoices all on tier T3, but three different fuel percentages: 11.97%, 9.37%, and 12.00%. That's either a per-contract rate variation that isn't documented anywhere in the seven batch exports, or a calculation error. Hayes & Sons — who have three open fuel surcharge disputes — are on that route. Before a Phase 2 agent verifies surcharge accuracy, we need to know which it is."

---

## Structure on a Card

```
BEFORE (1 min)
  400/day × 4 min = 26.7 hrs/day
  Zone A: deterministic lookup — no judgment
  Zone B: driver sync — where load + failures sit
  Failures: CRM lag, manual GPS ping, no dedup, stale SOP

AFTER (1:15 min)
  Workflow layer:  lookup + status branches + dedup → FULLY AGENTIC
  Agent layer:     driver contact + fallback decision → AGENT-LED
  Human layer:     not-found, exception, null status → HUMAN-LED

WHY (1:15 min)
  Driver fallback:     timeout rule, not decision — pre-approved, deterministic trigger
  Consignment lookup:  switch on 5 enums — LLM adds hallucination risk for zero benefit
  Exception handling:  CRM has the reason; what happens NEXT needs dispatcher judgment
```
