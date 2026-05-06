# CLAUDE.md — Gate 2 Assessment: Apex Distribution Ltd

**Project:** Gate 2 — Cognitive Work Assessment & Agent Design  
**Scenario:** Apex Distribution Ltd, Birmingham — Customer Operations (35 people, 4 work streams)  
**Methodology:** ATX (Agentic Transformation) — 7-phase assessment  
**Primary agent target:** W2 ETA Inquiries (Coordinator ETA agent)

---

## What this project is

A 35-person Customer Operations team at Apex Distribution Ltd handles ~730 customer interactions per day across four work streams: delivery exceptions, ETA inquiries, dispatch adjustments, and billing disputes. The work is messy, cross-system, and partially undocumented — the live SOP references a system (DispatchHub) that was retired in October 2024 and has an incomplete damage-handling section ("TBD pending review").

This assessment applies the ATX methodology to determine which parts of this work an autonomous agent should handle, designs the agent for the highest-value target, and produces a system/data inventory that is honest about the legacy billing constraint (Aurum Billing: on-prem Oracle, batch-only, no API, schema changes quarterly without notice).

The recommendation is to build the ETA inquiry agent (W2) first — 400 inquiries/day, 2.8 FTE savings, 1–2 month ROI payback, low build risk — before tackling billing disputes (W4), which has higher compliance value but higher build complexity due to the Aurum batch dependency.

---

## File structure

```
FDE-assessment-week2/
├── DELIVERABLE-1-COGNITIVE-LOAD-MAP.md        # W2 + W4 decomposed: zones, micro-tasks, lived workflow
├── DELIVERABLE-2-DELEGATION-MATRIX.md         # 7 task clusters scored; archetypes with rationale
├── DELIVERABLE-3-VOLUME-VALUE-ANALYSIS.md     # Volume × Value matrix; W2 wins; W4 deferred
├── DELIVERABLE-4-AGENT-PURPOSE.md             # Full spec for Coordinator ETA (W2 Phase 1)
├── DELIVERABLE-5-SYSTEM-DATA-INVENTORY.md     # System landscape + Aurum constraint analysis + assumption register
├── DELIVERABLE-6-DISCOVERY-QUESTIONS.md       # 10 targeted questions for Sarah; live round prep
├── CLAUDE.md                                  # This file
│
├── Gate2-Participant-Pack.md                  # Scenario brief + 5 artefacts
├── artefacts/                                 # 7 Aurum batch CSV samples (2026-04-13/14)
│   ├── APEX_BILL_DAILY_20260414.csv
│   ├── APEX_FUEL_SURCH_20260414.csv
│   ├── APEX_CREDITS_20260414.csv
│   ├── APEX_DISPUTES_OPEN_20260414.csv
│   ├── APEX_RECON_20260413.csv
│   ├── APEX_AGED_RECEIVABLES_20260410.csv
│   └── APEX_CUSTOMER_MASTER_20260401.csv
```

---

## How Claude was used in this assessment

### Phase 1 — Domain orientation and scenario reading

Claude read the Gate 2 brief twice: first for the stated facts (system names, volumes, handling times), second for what the artefacts imply about lived work vs. documented process. Key gap surfaced immediately: the SOP (Artefact 4) references DispatchHub (retired October 2024) — so any SOP-based analysis of delivery exceptions would describe a process that no longer exists.

Claude also cross-referenced the Aurum batch CSV samples against each other to identify schema relationships (e.g., INVOICE_NO is the join key across all 7 files) and anomalies — most critically, that Sandra's £170 goodwill credit (Artefact 2) does not appear in the APEX_CREDITS export, and that R-008 route invoices show different FUEL_PCT values within the same T3 tier.

### Phase 2 — Cognitive Load Map (Deliverable 1)

Claude decomposed W2 (ETA inquiries) and W4 (billing disputes) into cognitive zones and micro-tasks. The zone framing — rather than task-list framing — came from asking: *"Why do these tasks cluster together cognitively?"* not *"What happens next?"*

The 8 control-handoff breakpoints were identified by asking where control transfers between system, agent, and human — and naming the failure mode at each transfer, not just the happy path.

W4 Zone B (validation and investigation) was explicitly not marked as fully agentic even though the lookup steps within it are deterministic. The zone includes async external dependencies (shipper confirmation, insurance pre-auth) and judgment calls (conflicting rate tables) that cannot be resolved by a rule engine. Naming these explicitly prevents the "everything is agentic" anti-pattern from creeping in during build.

### Phase 3 — Delegation Suitability Matrix (Deliverable 2)

Claude scored all 7 clusters on 6 dimensions. The anti-pattern check was built in from the start: *"Is there any cluster here that should NOT be fully agentic, but I'm tempted to make it so?"*

Two clusters required explicit justification for non-obvious archetypes:
- **4b (Validation):** Human-led even though the invoice lookup is deterministic. The judgment call ("is this charge correct given conflicting rate tables?") is the cluster's defining task, not the lookup.
- **4c-ii (Manager approval):** Human-only even though the routing decision is deterministic. Manager approval ≥£50 is a financial control, not an inefficiency to be automated.

The compliance gap in 4c-i and 4d (audit logging mandatory after the Artefact 2 incident) was made non-negotiable rather than optional.

### Phase 4 — Volume × Value Analysis (Deliverable 3)

Claude calculated time savings by stream (automation potential × monthly hours), not just raw volume. W2 wins on operational ROI (2.8 FTE, 1–2 month payback). W4 wins on strategic value (compliance risk reduction) but loses on build complexity (Aurum batch dependency, async waits). The analysis deliberately named both and recommended sequencing: W2 first, then W4 — not because W4 is unimportant, but because W2 rebuilds Sarah's confidence after two failed projects before the harder problem is tackled.

### Phase 5 — Agent Purpose Document (Deliverable 4)

Claude drafted the full 12-section spec for the Coordinator ETA agent. Key design decisions:
- 2-minute driver response window (not 5-minute) — avoids eating most of the 5-minute customer SLA before even generating a reply
- Fallback window as primary response, not secondary — most drivers don't respond in time; designing the fallback as a first-class path (not a failure mode) makes the agent reliable
- Inquiry deduplication cache — prevents the agent from querying the driver multiple times when a customer asks the same question within an hour

### Phase 6 — System/Data Inventory (Deliverable 5)

Claude read all 7 Aurum batch CSV files for schema, lag times, and cross-file joins. Two findings changed the design:
1. **Missing credit:** Sandra's £170 credit for INV-2026-04318 (Artefact 2) is not in the APEX_CREDITS export. The file has an AUDIT_REF field — meaning structured credits should be audited — but manual overrides bypass this. APEX_CREDITS is an incomplete record of credits applied.
2. **Fuel surcharge anomaly:** Three invoices on R-008 (all T3 tier) have different FUEL_PCT values. Either the rate is contract-specific within a tier (undocumented), or there's a calculation error in the Aurum batch job. Either answer changes what a Phase 2 billing agent can claim about verifying surcharge accuracy.

### Phase 7 — Discovery Questions (Deliverable 6)

Claude identified 10 questions in 3 priority tiers. Each question has an explicit "if X then design changes this way / if Y then changes that way" statement. The questions are grounded in specific artefact tensions rather than generic process discovery.

Most important for the live round: Q3 (the Sandra credit audit gap) and Q5 (the fuel surcharge anomaly) are both visible in the CSV data and not mentioned by Sarah in the brief. Raising them demonstrates that the assessment is based on the actual data, not just the scenario summary.

---

## Key decisions and rationale

### Why W2 (ETA inquiries) is the Phase 1 target and not W4 (billing disputes)

W4 has higher strategic value (compliance risk reduction, audit trail enforcement). W2 has lower build risk and faster payback. The sequencing logic is not about value — it is about Sarah. She has watched two prior automation initiatives fail. A quick operational win on ETA handling (1–2 month payback, no compliance complexity, no Aurum dependency) rebuilds the trust required to get sign-off for the harder W4 project. Proposing W4 first — the compliance-heavy, batch-dependent, Aurum-constrained problem — before W2 has proven value is a commercially poor choice, even if it's technically the more interesting problem.

### Why Aurum batch-only is a hard constraint, not a workaround

The brief states explicitly: "no real-time API; reconciliation file lags 24 hours behind invoice generation; modifications require a manual ticket to the Aurum support team (typical turnaround 48 hours)." The prior RPA project broke when the Aurum schema changed. Any agent that depends on Aurum data for real-time decisions will fail in the same way. The inventory (D5) treats Aurum as batch-only throughout — agent reads from exports, agent cannot write via API, agent cannot verify if a credit was applied today.

### Why driver non-response is the primary path, not the exception

Artefact 3 shows the ETA inquiry handled in 10 minutes (11:14 → 11:24), with 5 minutes spent getting a driver location from dispatch. The brief says 4 min avg handling time — which means the human currently lives on the edge of SLA even without driver latency. The ETA agent's 2-minute wait + fallback protocol is designed around the assumption that driver non-response is routine (~20% of active delivery inquiries), not exceptional. Designing for the driver-responds path and escalating to the driver-doesn't-respond path inverts the real distribution.

### Why the compliance gap in W4 is named as a design requirement, not a risk to monitor

Artefact 2 internal note: "no entry in the credits audit log for this £170; Sandra applied it via a manual override." The APEX_CREDITS export has an AUDIT_REF field — which means the system supports audit logging but can be bypassed. A Phase 2 billing agent that enforces the structured credit entry path (as opposed to the manual override path) closes this gap automatically. This is not a monitoring requirement (detect when audit trail is missing) — it is a design requirement (make the non-audited path structurally unavailable to the agent).

### Why dispatch adjustments (W3) are scoped out indefinitely

The dispatch console is described as having a "limited API surface." What "limited" means is unspecified — this is a D6 Question 6 for Sarah. Until that question is answered, any estimate of W3 automation potential is fiction. If the API is read-only, agent support is limited to data surfacing. If there is no API, W3 can only be automated via screen automation (Citrix), which is the same approach that failed with Aurum. W3 is not deferred; it is scoped out until the API surface is confirmed.

---

## Assumptions that would change the design

These are rated LOW or MEDIUM confidence. They are the first things to validate with Sarah before committing to build.

| Assumption | Confidence | What changes if wrong |
|---|---|---|
| CRM delivery status is updated in ≤10 min from driver app scan | **MEDIUM** | If end-of-shift batch: "out-for-delivery" status is unreliable; agent must disclose staleness or escalate all active deliveries |
| Driver App has a programmatic API for GPS query or agent messaging | **LOW** | If message-only: ETA accuracy limited to driver reply; if no API at all: agent becomes a lookup tool only |
| APEX_CREDITS export captures all credits applied (including manual overrides) | **LOW** — contradicted by Artefact 2 | Phase 2 billing agent will misidentify resolved disputes as open |
| Aurum schema changes are vendor-managed (external, no advance notice) | **MEDIUM** | If self-hosted by Apex IT: advance notice is achievable internally; schema drift risk is lower |
| Fuel surcharge percentage within a tier is fixed (T3 = constant %) | **LOW** — anomaly visible in sample data | If contract-specific: surcharge verification requires per-customer rate card lookup; Phase 2 agent needs a data source not in the 7 batch exports |
| ETA inquiry channel (SMS, call, etc.) is recorded in CRM per case | **MEDIUM** | If not recorded: agent must default to one channel; may mis-route replies for non-SMS inquirers |

---

## What this project does not cover

- **W1 (Delivery exceptions):** Deferred to Phase 2. Higher complexity (damage assessment rules, insurance lookup, SOP is out of date). Volume is high (180/day) but build risk is medium due to dispatch console API uncertainty.
- **W3 (Dispatch adjustments):** Scoped out until API surface confirmed (D6 Q6). Route optimisation engine is unnamed in the brief. Cannot estimate automation potential without knowing if write access exists.
- **W4 (Billing disputes):** Deferred to Phase 2 after W2 proves value. The compliance risk reduction case is strong (audit trail enforcement), but Aurum batch-only constraint means no real-time resolution — agent can triage and detect, not close.
- **Proactive ETA notifications:** Out of scope. Agent handles reactive inquiries (customer asks). Future: proactive alerts before delivery window from driver app GPS.
- **Customer-facing chatbot interface:** Explicitly avoided. Sarah's 2024 chatbot failed because customers hated it. Agent replies via the customer's existing inquiry channel (SMS, app) — no new bot interface.

---

## How to use the deliverables in the live round

Sarah will be impatient and sceptical. Three things she is most likely to probe:

1. **"Why ETA first, not the billing mess?"** Answer: Proven value on a low-risk win before asking her to fund a project with Aurum batch dependency. She can see W2 succeed in 6 weeks; W4 will take 6 months just to understand the data landscape properly.

2. **"How is this different from the chatbot that failed?"** Answer: The chatbot failed for one of three reasons (D6 Q7). If it was wrong answers, the ETA agent's driver sync protocol directly addresses that. If it was the bot format, the ETA agent is invisible — it replies via SMS, not via a new interface. If it was integration failures, the ETA agent's system requirements (CRM REST API only) are minimal and well-understood.

3. **"What happens when Aurum breaks your billing agent?"** Answer: Acknowledge the risk directly — it broke the RPA, and it will break any agent that doesn't have schema validation at ingestion. Phase 2 billing agent design includes schema validation as a first-class feature, not a bolt-on. If the schema changes, the agent halts and alerts before producing incorrect output.

The questions that will land best in the live round are Q3 (the Sandra audit trail gap) and Q5 (the fuel surcharge anomaly) — both visible only from reading the CSV data, not the scenario brief. Raising them signals that the assessment is grounded in evidence, not just the summary.
