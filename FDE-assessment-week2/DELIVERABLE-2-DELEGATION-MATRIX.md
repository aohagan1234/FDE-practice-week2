# DELIVERABLE 2 — DELEGATION SUITABILITY MATRIX

**Scenario:** Apex Distribution Ltd (Gate 2)  
**Exercise:** Week 2 Assessment, Timed  
**Task clusters:** 7 clusters derived from W2 + W4 decomposition (DELIVERABLE-1)  
**Scoring methodology:** 6-point dimension rubric (Determinism, Reversibility, Time criticality, Data availability, Compliance risk, Exception frequency)

---

## 1. SCORING RUBRIC

### 1.1 Dimensions and scale

| Dimension | Ideal for agentic (HIGH score) | Risky for agentic (MEDIUM score) | Poor for agentic (LOW score) |
|---|---|---|---|
| **Determinism** | Rule-based, <5% edge cases; no subjective judgment | Mixed: 70–80% rule-based, 20–30% judgment; moderate edge cases | Highly judgmental, >50% edge cases; significant subjective calls |
| **Reversibility** | Reversible or zero consequence (e.g., lookup, inquiry) | Partially reversible; low financial consequence (<£50); human can easily undo | Irreversible or high consequence (e.g., delivery rejection, manager-level decision, compliance exposure) |
| **Time criticality** | 5+ min response acceptable; customer can wait | <5 min response required; real-time SLA exists but with 1–2 min slack | <2 min response required; real-time response is mandatory; no margin for delay |
| **Data availability** | Real-time API available; zero lag; high confidence in freshness | Real-time API with sync gaps (5–10 min lag); or batch + manual correlation required | Batch-only (T-1 lag); manual lookup required; data freshness uncertain or external/async |
| **Compliance risk** | No audit trail required; no regulatory exposure; SLA miss is service-level, not compliance | Audit trail helpful for traceability; some regulatory exposure; reversibility reduces risk | Audit trail mandatory; high regulatory exposure; irreversibility is high risk; compliance review will scrutinize this decision |
| **Exception frequency** | 90%+ happy path; <10% edge cases requiring escalation | 70–90% happy path; 10–30% edge cases; escalation protocol required | <70% happy path; >30% edge cases; frequent surprises; judgment call needed for majority |

### 1.2 Archetype definitions

**Fully agentic:** Agent independently handles task; human oversight is not required. Escalation is rare (<5% of cases). Suitable when: ≥5 of 6 dimensions score HIGH.

**Agent-led with oversight:** Agent independently handles the happy path (~80% of cases); human reviews decisions or has override authority. Escalation happens 15–20% of the time. Suitable when: 3–4 dimensions score HIGH, 1–2 score MEDIUM.

**Human-led with agent support:** Human makes the core decision; agent surfaces data, options, and recommendations. Agent does not approve/reject; human does. Suitable when: 2–3 dimensions score HIGH, 3–4 score MEDIUM, or any dimension scores LOW.

**Human-only:** Task requires human judgment, significant reversibility risk, or compliance/regulatory override. Agent has no role (or only monitoring role). Suitable when: ANY dimension scores VERY LOW, or 2+ dimensions score LOW.

---

## 2. TASK CLUSTER SCORING

### Cluster 2a: Consignment lookup + status classification (W2 Zone A)

**What:** Customer/dispatcher inquires about delivery status; agent searches CRM by consignment ID, returns delivery status (pre-dispatch, out-for-delivery, delivered, exception).

**Scoring:**

| Dimension | Score | Rationale |
|---|---|---|
| **Determinism** | **HIGH** | Consignment ID search is deterministic (database query). Status enum is predefined (4–5 states). No judgment required. >95% of inquiries map to a known state. |
| **Reversibility** | **HIGH** | Lookup is read-only; no side effects. Customer receives information but no transaction is triggered. Wrong lookup is merely informational and can be corrected by re-query. |
| **Time criticality** | **MEDIUM** | Customer expects <5 min response. Agent can deliver in <1 min. No hard SLA pressure; acceptable to wait for Salesforce API response (<1 sec typical). |
| **Data availability** | **HIGH** | Salesforce CRM has REST API. Customer records are real-time. Delivery status is updated by driver app at point-of-scan or end-of-day. Data freshness is high confidence. |
| **Compliance risk** | **HIGH** | Status lookup is read-only inquiry. No audit trail needed. No regulatory exposure. SLA miss is service-level, not compliance. |
| **Exception frequency** | **HIGH** | 95%+ of inquiries return a valid consignment. <5% are "not found" (customer error or data lag). Happy path is dominant. |
| **TOTAL** | **5/6 HIGH** | — |

**Archetype: WORKFLOW / API INTEGRATION — not an LLM agent**

**Rationale:** Determinism is necessary but not sufficient to justify an agent. This task is a database query followed by a `switch` on a status enum (5 states). No natural language reasoning, no ambiguity resolution, no multi-step judgment — just a lookup and a template response. An event-driven API wrapper or rule-based SMS responder handles the 95% happy path cheaper, faster, and with zero hallucination risk. An LLM agent adds no value on a deterministic lookup. The agent earns its place only at the edges: malformed or unrecognised consignment IDs, null/unknown status states, and the exception-routing handoff to the dispatcher. Implementing the whole cluster as "fully agentic" would be over-engineering a database call.

**Correct implementation:** Event-driven workflow (triggered by customer inquiry) → CRM REST API call → rule-based response template keyed on status. LLM agent invoked only for the <5% edge cases (ID not found, null status, ambiguous input).

**Escalation triggers:** (1) Consignment not found → fall back to "checking manual records"; (2) CRM API unavailable → escalate to manual queue; (3) Status is "exception" (delivery refused, damaged, held) → escalate to dispatcher for root-cause context (this is an information handoff, not an approval).

---

### Cluster 2b: Driver contact + ETA generation (W2 Zone B)

**What:** Agent needs to provide tight ETA (better than 4h window). For active deliveries, agent contacts driver to request current location + next-stop ETA. If driver responds in <2 min, agent relays tight ETA; if driver doesn't respond, agent falls back to 4h window or escalates.

**Scoring:**

| Dimension | Score | Rationale |
|---|---|---|
| **Determinism** | **MEDIUM** | ETA generation (given driver location) is deterministic: lookup remaining stops, calculate travel time, apply buffer. But driver response is async/optional. If driver doesn't respond, escalation decision is a judgment call (wait more, escalate to dispatcher, or fallback?). Happy path (driver responds) is ~80%; exception path (driver delayed) is ~20%. |
| **Reversibility** | **MEDIUM** | Wrong ETA is not reversible in real-time. Customer waits at wrong time or escalates. Reputational cost exists but is recoverable (customer can call back for update). Not an irreversible business decision, but SLA miss is costly. |
| **Time criticality** | **HIGH** | Customer expects response in <5 min. Agent needs to make async decision (contact driver, wait, decide) within this window. If agent waits >2 min for driver response and then escalates, total response time is ~2.5 min (acceptable). If agent escalates immediately (no driver contact), response is <1 min (good). But if agent waits 3+ min for driver and then escalates, response time reaches 4+ min (tight). |
| **Data availability** | **MEDIUM** | CRM has real-time delivery status (HIGH). Driver app has real-time GPS (HIGH), but sync lag to CRM is 5–10 min (MEDIUM). Driver messaging is async (customer queries driver via app; response time is 1–5 min depending on driver workload). Data is available but has synchronization delays. |
| **Compliance risk** | **HIGH** | ETA provision is service-level, not compliance-level. No audit trail needed. SLA miss is a service failure, not a compliance exposure. |
| **Exception frequency** | **MEDIUM** | For active deliveries: ~80% driver responds within 2 min (happy path: agent provides tight ETA). ~20% driver is delayed or non-responsive (exception path: agent escalates or falls back to 4h window). Escalation is frequent enough to require explicit handling. |
| **TOTAL** | **3/6 HIGH** | — |

**Archetype: AGENT-LED WITH ESCALATION**

**Rationale:** Agent can independently handle ~80% of active-delivery ETA requests (driver responds promptly). But driver latency is real (Artefact 3: 5 min from agent query to dispatch response). Agent design must include explicit escalation protocol: (1) Query driver async; (2) Wait max 2 min for response; (3) If response arrives, relay tight ETA; (4) If no response, escalate to dispatcher or reply with fallback 4h window. This keeps agent efficiency high (no human review needed for happy path) while protecting SLA (explicit fallback prevents excessive waiting). Human oversight is not required, but escalation trigger must be automatic.

**Escalation triggers:** (1) Driver doesn't respond in 2 min → escalate to dispatcher for manual driver contact, or reply with fallback 4h window; (2) CRM status is ambiguous (not clearly "out for delivery") → escalate to dispatcher for context; (3) Multiple inquiries for same consignment within 1h → deduplicate and use prior response (cache).

---

### Cluster 4a: Dispute intake + triage (W4 Zone A)

**What:** Customer submits dispute (email, call, SMS). Agent logs case in CRM, extracts dispute type, and categorizes into enum (FUEL_SURCH, REDELIVERY_FEE, DIM_WEIGHT, DAMAGE_GOODWILL, INV_ERROR).

**Scoring:**

| Dimension | Score | Rationale |
|---|---|---|
| **Determinism** | **HIGH** | Dispute categorization is rule-based enum assignment. Customer text is parsed for keywords or reason code. Rules are clear: "fuel surcharge dispute" → FUEL_SURCH; "redelivery charged incorrectly" → REDELIVERY_FEE. <5% of disputes are ambiguous (customer says "charge seems high" without specificity). >95% of disputes fit one of the 5 categories. |
| **Reversibility** | **HIGH** | Case categorization is not irreversible. If agent categorizes dispute as FUEL_SURCH but later evidence shows it's DAMAGE_GOODWILL, case can be re-categorized. No financial transaction has been triggered; categorization is purely administrative. |
| **Time criticality** | **MEDIUM** | Triage can be done asynchronously. Acceptable SLA is <1h (customer wants quick acknowledgement, but doesn't need decision on the same call). No hard real-time constraint. |
| **Data availability** | **HIGH** | Dispute input is email / phone call / SMS (synchronous). CRM case logging is real-time. No external data lookups needed at this stage. Data is immediately available. |
| **Compliance risk** | **HIGH** | Case intake is purely administrative. No audit trail of triage decision is needed (triage is a routing decision, not an approval). No compliance exposure. |
| **Exception frequency** | **HIGH** | >95% of disputes fit one of the 5 categories. <5% are truly ambiguous (customer vague or dispute type is novel). Escalation is rare. |
| **TOTAL** | **5/6 HIGH** | — |

**Archetype: RULE-BASED CLASSIFIER (primary) + LLM FALLBACK (ambiguous cases only)**

**Rationale:** For 95% of disputes, categorisation is keyword classification: "fuel surcharge" → FUEL_SURCH, "redelivery" → REDELIVERY_FEE, "weight" → DIM_WEIGHT. A lightweight keyword classifier or decision-tree matcher handles this with no LLM needed. An LLM agent earns its place only for the ~5% where the customer is vague ("this charge seems wrong" with no further detail) and category must be inferred from context, tone, or cross-referenced invoice history. Implementing the full cluster as "fully agentic" applies LLM inference to 95% of cases that don't need it.

**Correct implementation:** Rule-based keyword classifier as primary path (handles ~95%). LLM agent as fallback for inputs the classifier cannot confidently categorise above a confidence threshold. This minimises inference cost and latency on the happy path.

**Escalation triggers:** (1) Classifier confidence below threshold → escalate to LLM agent for interpretation; (2) Dispute contains multiple issues → split into multiple case records or flag for manual handling.

---

### Cluster 4b: Validation & investigation (W4 Zone B)

**What:** Agent gathers data to determine if charge is correct: invoice lookup in Aurum batch, delivery exception lookup in CRM, shipper confirmation (if dim weight), insurance pre-auth (if damage).

**Scoring:**

| Dimension | Score | Rationale |
|---|---|---|
| **Determinism** | **MEDIUM** | Invoice lookup is deterministic (database query). Charge verification against business rule is deterministic IF rule is clear (e.g., "fuel surcharge must be <15% of net amount"). But edge cases exist: dimensional weight disputes require shipper confirmation (external, async); insurance claims require pre-auth query (external system, slow). Judgment is required to interpret conflicting data (e.g., invoice says £340 surcharge, but customer says it should be £250 based on alternative rate table; which is correct?). ~70% of investigations are deterministic; ~30% require judgment or external confirmation. |
| **Reversibility** | **MEDIUM** | Investigation doesn't trigger a financial transaction, so reversible. But if investigation is incorrect (e.g., agent misreads invoice amount), subsequent credit decision is wrong. Reversibility exists, but cost of incorrect investigation is high (affects downstream decision). |
| **Time criticality** | **LOW** | Investigation can be asynchronous. If shipper confirmation is needed, case can wait 24–48h. If insurance pre-auth is needed, case can wait 24h. Acceptable SLA is <24h for initial investigation; <48h for completion with external confirmation. No real-time constraint. |
| **Data availability** | **MEDIUM** | Invoice data from Aurum batch is available (T-1 lag). Exception data from CRM is real-time. Shipper contact is external/async (email, phone). Insurance system is external. Data is available but with significant lag and async waits. Aurum batch lag means agent cannot query invoice if dispute is received same-day; must wait for next batch (max 24h) or request manual invoice copy from shipper. |
| **Compliance risk** | **MEDIUM** | Investigation is informational (surfaces data), but if audit trail is broken (as shown in Artefact 2), investigation results are not defensible. Compliance review will ask: "Who looked at the invoice? When? What was their conclusion?" If no audit trail, compliance exposure exists. Current manual override gap makes this higher-risk. |
| **Exception frequency** | **MEDIUM** | ~70% of charges verify as correct in first lookup (happy path: agent checks invoice, amount matches, rule validates, proceed to approval). ~30% require external confirmation (shipper, insurance) or involve edge cases (customer cites alternative rate table; agent must escalate to finance for interpretation). |
| **TOTAL** | **2/6 HIGH** (HIGH: Determinism-partial, Data avail-partial, Exception freq-partial; MEDIUM: Reversibility, Compliance risk, Time criticality-LOW) | — |

**Archetype: HUMAN-LED WITH AGENT SUPPORT**

**Rationale:** Investigation requires human judgment and data synthesis. Agent's role is to surface data and flag ambiguities: (1) Agent queries Aurum for invoice, displays amount + surcharge details; (2) Agent queries CRM for delivery exception (if linked); (3) Agent flags if exception is missing ("Damage claim but no driver exception record"); (4) Agent initiates shipper confirmation request (async). Human (billing agent or supervisor) makes the judgment call: "Is this charge correct?" Shipper confirmation is human-driven (agent just sends request). Insurance pre-auth is queried via external system (agent invokes, human interprets response). Agent does not approve/reject; agent surfaces data for human decision.

**Escalation triggers:** (1) Invoice not found in Aurum (batch lag or customer error) → escalate to shipper for manual invoice copy; (2) Delivery exception not found but damage claim exists → escalate to dispatcher to request retroactive damage photo; (3) Shipper doesn't respond to confirmation request within 24h → re-send or escalate to supervisor; (4) Insurance pre-auth denial → escalate to claims team; (5) Conflicting data (e.g., two different rate tables for surcharge) → escalate to finance for interpretation.

---

### Cluster 4c: Credit decision & approval (W4 Zone C)

**Split into two sub-clusters:**

#### Sub-cluster 4c-i: Credit decision for <£50 (Agent approval)

**What:** Investigation concludes charge is incorrect. Credit amount is <£50. Agent applies decision rule: "Charge is wrong → apply credit" and immediately approves.

**Scoring:**

| Dimension | Score | Rationale |
|---|---|---|
| **Determinism** | **HIGH** | Decision rule is deterministic: IF charge_is_incorrect AND credit_amount < £50 THEN approve_credit. Rule is clear, no edge cases. |
| **Reversibility** | **MEDIUM** | Credit <£50 is reversible via manual ticket to Aurum (48h turnaround). Low financial consequence. However, reversal is a formal process; once credit is entered, it creates a transaction that must be formally reversed if incorrect. |
| **Time criticality** | **MEDIUM** | Same-day approval is desirable but not critical. Acceptable SLA is <4h (customer sees decision on same day). |
| **Data availability** | **HIGH** | Decision depends on prior investigation (data already gathered). No new data queries needed. Approver lookup is straightforward. |
| **Compliance risk** | **HIGH** — IF audit trail is enforced. **MEDIUM** — IF audit trail is missing. | Current state: Artefact 2 shows manual credit with no AUDIT_REF (compliance gap). Agent design must enforce audit logging (APPROVER_ID + AUDIT_REF). If audit trail is mandatory in agent design, compliance risk is manageable. If audit trail is optional, compliance risk is high. **Assumption: Agent design enforces audit logging.** |
| **Exception frequency** | **HIGH** | ~70% of disputes result in approval (charge was wrong). ~10% result in rejection (charge is correct). ~20% are edge cases or pending external confirmation. For the 70% approval rate, ~65% are <£50 (agent auto-approves); ~5% are ≥£50 (manager approval). So ~93% of approvals are <£50 (happy path for agent-only decisions). |
| **TOTAL** | **5/6 HIGH** (assuming audit logging is enforced) | — |

**Archetype: WORKFLOW RULE EVALUATION — not an LLM agent**

**Rationale:** The decision rule is `IF charge_is_incorrect AND credit_amount < £50 THEN approve`. That is a conditional expression, not a reasoning task. A workflow rule engine evaluates this in milliseconds with no inference cost, no hallucination risk, and deterministic auditability. An LLM agent deciding this adds nothing. The agent's role in the wider W4 flow (4b investigation) has already produced the `charge_is_incorrect` determination; 4c-i is just applying a threshold check to route to execution. Calling this "fully agentic" conflates automatable with agentic.

**Correct implementation:** Workflow rule evaluation triggered on completion of 4b investigation. If `charge_is_incorrect = true AND credit_amount < £50`, auto-route to 4d execution with logged AUDIT_REF. No LLM agent required. CRITICAL: Audit logging must be enforced by the workflow — APPROVER_ID (workflow/system), AUDIT_REF (case ID), REASON_CODE, timestamp — closing the compliance gap from Artefact 2.

**Escalation triggers:** (1) Credit amount is edge case (exactly £50 or within £5 of threshold) → escalate to manager for discretion; (2) Dispute is linked to reputational risk (VIP customer, social media, escalated complaint) → escalate to manager even if <£50; (3) Credit involves refund (customer overpaid) rather than account credit → escalate for finance processing (different workflow).

#### Sub-cluster 4c-ii: Credit approval for ≥£50 (Manager approval)

**What:** Investigation concludes charge is incorrect. Credit amount is ≥£50. Agent routes to manager for approval (authority threshold).

**Scoring:**

| Dimension | Score | Rationale |
|---|---|---|
| **Determinism** | **LOW** | Manager approval is a discretionary decision. While the charge may be verifiably incorrect, whether to approve credit (vs. offer partial credit, vs. decline and handle via insurance claim) is a judgment call. Manager may reject even if charge is incorrect (e.g., "Customer has history of false claims; escalate to collections"). ~20% of ≥£50 credits are rejected or modified by manager. |
| **Reversibility** | **MEDIUM** | Approval is reversible via formal reversal process (48h with Aurum + audit). But reversing a manager-approved credit requires manager sign-off again. |
| **Time criticality** | **MEDIUM** | Manager approval SLA is 2–4h on average (Artefact 2 email thread shows multi-hour waits). Acceptable SLA is <8h (customer should see decision same business day). On busy days, SLA may slip to next day. |
| **Data availability** | **HIGH** | All investigation data is available to manager (agent prepares summary). Manager has access to CRM, Aurum, prior case history. Data is available. |
| **Compliance risk** | **HIGH** | Manager approval is required for audit trail (APPROVER_ID must be manager, not agent). Audit trail is mandatory. If manager approves without audit logging, compliance exposure is high. |
| **Exception frequency** | **MEDIUM** | ~30% of disputes result in ≥£50 credit decision. ~70% of these are approved (1 out of 3 is approved). ~30% are modified or rejected. So escalation is frequent (~30 of 60 disputes/day × 30% = 9 escalations/day), requiring clear manager queue discipline. |
| **TOTAL** | **2/6 HIGH** (High: Data avail., Compliance risk if audit enforced; Low/MEDIUM: Determinism-LOW, Reversibility-MEDIUM, Time crit.-MEDIUM, Exception freq.-MEDIUM) | — |

**Archetype: HUMAN-ONLY (Manager approval required)**

**Rationale:** Credit ≥£50 is above agent authority and requires manager discretion. This is not a constraint or design flaw; it's a control. Manager approval is a standard financial control in billing workflows. Agent's role is to route the case with complete investigation summary, not to approve. Manager makes the final decision: approve, modify, or reject. This ensures compliance (APPROVER_ID is manager) and reduces risk (manager can catch edge cases agent missed).

**Escalation triggers:** Manager is absent (vacation, meeting) → escalate to finance supervisor; manager queue is >4h behind → escalate to senior manager for expedite; dispute is linked to litigation or regulatory issue → escalate directly to legal/compliance.

---

### Cluster 4d: Execution & notification (W4 Zone D)

**What:** Manager (or agent, for <£50) has approved credit. Agent enters credit into Aurum system (manual UI entry or support ticket), logs audit trail (AUDIT_REF, APPROVER_ID), notifies customer, and closes case in CRM.

**Scoring:**

| Dimension | Score | Rationale |
|---|---|---|
| **Determinism** | **HIGH** | Credit entry workflow is deterministic: fill Aurum form with (credit_amount, reason_code, customer_id, invoice_no, approver_id, audit_ref), submit. Notification template is deterministic. Case closure is deterministic. No judgment required; all inputs are predetermined by prior approval. |
| **Reversibility** | **LOW** | Credit entry in Aurum creates a transaction record. Reversal requires formal process (manual ticket, 48h). Customer notification is sent immediately; customer may act on credit (e.g., accept it, cascade into downstream customer expectations). Reversal is possible but costly and procedurally heavy. Irreversibility risk is real. |
| **Time criticality** | **LOW** | Aurum entry has no real-time SLA. Acceptable SLA is <48h (credit must be entered before next batch export to appear on next statement; batch runs daily 02:00–04:00 GMT, so agent has 24h window). If credit is entered same-day, it appears in next day's batch export (T-1 lag). |
| **Data availability** | **MEDIUM** | Aurum has no API for credit entry; agent must use manual UI or submit support ticket. This is a system constraint (not a data availability issue, but an integration issue). Manual entry is deterministic but slow. Support ticket turnaround is 48h (slow). Data/system availability is the bottleneck. |
| **Compliance risk** | **VERY HIGH** | Audit trail is mandatory. Agent must log credit with (1) APPROVER_ID (person who approved); (2) AUDIT_REF (case/transaction ID); (3) reason code; (4) timestamp. Artefact 2 incident shows manual credit with no AUDIT_REF (compliance gap; no audit trail). Current state is a known risk. Agent design must enforce audit logging or compliance exposure will fail review. **CRITICAL:** If audit logging is skipped, compliance penalty is high. |
| **Exception frequency** | **MEDIUM** | ~95% of approved credits are entered successfully on first attempt. ~5% fail due to schema changes (Aurum schema changes quarterly) or system issues (batch export delay). Escalation is infrequent. |
| **TOTAL** | **2/6 HIGH** (High: Determinism, Exception freq.; VERY HIGH: Compliance risk; Low/MEDIUM: Reversibility-LOW, Time crit.-LOW, Data avail.-MEDIUM) | — |

**Archetype: TRIGGERED WORKFLOW WITH HUMAN AUDIT CHECK — not an LLM agent**

**Rationale:** Credit entry is deterministic form-fill: `(credit_amount, reason_code, customer_id, invoice_no, approver_id, audit_ref)` → submit. Customer notification is template substitution. Case closure is a status update. None of these steps involve reasoning, ambiguity, or judgment — they are execution steps triggered by a prior approval event. A workflow triggered on approval handles this correctly. The "oversight" requirement is on the *audit trail*, not on any agent reasoning — a human (finance team) spot-checks that AUDIT_REF and APPROVER_ID are present on every credit weekly. Framing this as "agent-led" implies LLM involvement where there is none. The Aurum entry itself may require a human to click through a UI or raise a ticket (no API) — that step is human-executed within the workflow, not agent-executed.

**Correct implementation:** Approval event (4c-i or manager sign-off) triggers a workflow that: (1) creates structured Aurum entry record with all required audit fields; (2) initiates Aurum UI entry or support ticket (human-assisted, no API); (3) sends customer notification from template; (4) closes CRM case; (5) writes structured log entry for weekly audit check. No LLM agent required.

**Escalation triggers:** (1) Aurum schema change breaks credit entry form → escalate to IT/Aurum support (manually submit ticket); (2) Customer doesn't see credit on next statement (batch export failed) → investigate batch export logs and resubmit; (3) AUDIT_REF is missing → escalate to finance for audit recovery (compliance incident); (4) Credit amount doesn't match approved amount (data entry error) → reverse and re-enter.

---

## 3. DELEGATION MATRIX SUMMARY

| Cluster | Implementation | Justification | Happy-path handling | Escalation rate | Agent needed? |
|---|---|---|---|---|---|
| **2a: Lookup** | **Workflow / API integration** | Deterministic CRM query + status enum → template response. No reasoning required. | Event-driven workflow handles 95%+ of inquiries | <5% (edges only) | ❌ No — LLM adds nothing to a database call |
| **2b: ETA + driver sync** | **LLM Agent-led with escalation** | Async driver comms, ETA reasoning from variable inputs, escalation decisions under time pressure | Agent provides tight ETA for 80% of active deliveries; escalates or falls back for 20% | ~20% | ✅ Yes — async reasoning + fallback decision under time pressure |
| **4a: Triage** | **Rule-based classifier + LLM fallback** | 95% of disputes are keyword-classifiable; LLM only needed for ambiguous cases | Keyword classifier handles ~95%; LLM invoked for <5% below confidence threshold | <5% | ⚠️ Partial — classifier primary, LLM only for ambiguous inputs |
| **4b: Validation** | **Human-led with agent support** | Investigation requires judgment + external confirmation; data has lags | Agent surfaces data + initiates external requests; human makes correctness judgment | ~100% (human always involved) | ✅ Yes — multi-source synthesis and ambiguity flagging |
| **4c-i: Approval <£50** | **Workflow rule evaluation** | `IF charge_is_incorrect AND amount < £50 THEN approve` is a conditional, not a reasoning task | Workflow rule fires on 4b completion; auto-routes to execution with AUDIT_REF | 0% (deterministic) | ❌ No — a rule engine is the right tool |
| **4c-ii: Approval ≥£50** | **Human-only** | Manager authority required; compliance control | Manager always involved; workflow routes with investigation summary | ~100% (manager always involved) | ❌ No — financial control, not an automation problem |
| **4d: Execution** | **Triggered workflow + human Aurum entry** | Deterministic form-fill + template notification triggered by approval event; Aurum has no API so entry is human-assisted | Workflow executes on approval trigger; human clicks through Aurum UI or raises ticket | ~5% (schema changes) | ❌ No — execution steps with human-assisted entry; no reasoning required |

---

## 4. ANTI-PATTERN CHECK: "IS EVERYTHING AGENTIC?"

**Summary distribution:**
- **LLM Agent required:** 2 clusters (2b, 4b) — async reasoning, multi-source synthesis, ambiguity resolution
- **Workflow / rule engine:** 3 clusters (2a, 4c-i, 4d) — deterministic, no reasoning needed
- **Classifier + LLM fallback:** 1 cluster (4a) — rule-based primary, LLM only for edge cases
- **Human-only:** 1 cluster (4c-ii) — financial control, manager authority required

**Verdict: ✅ NOT an anti-pattern — and not "everything is agentic" either.**

**Key distinction applied:** Determinism is necessary but not sufficient to justify an LLM agent. Clusters 2a, 4c-i, and 4d are fully automatable — but the correct implementation is a workflow, rule engine, or triggered job, not an LLM. An agent adds value when there is ambiguity to resolve, async communication to manage, or multi-source data to synthesise under uncertainty. Where none of those apply, a workflow is cheaper, faster, and more reliable.

**Rationale by cluster:**
- **2a (Lookup):** CRM query + status enum = workflow. LLM is engineering overhead on a database call.
- **2b (ETA + driver sync):** Async driver comms + ETA reasoning + escalation decisions under time pressure = LLM agent justified.
- **4a (Triage):** 95% keyword classification = rule-based classifier. LLM fallback for the 5% that are ambiguous.
- **4b (Investigation):** Cross-system data synthesis + judgment under uncertainty = LLM agent justified.
- **4c-i (Approval <£50):** `IF x AND y THEN approve` = rule engine. Calling this "agent" is over-engineering a conditional.
- **4c-ii (Approval ≥£50):** Financial control = human-only. Neither agent nor workflow.
- **4d (Execution):** Deterministic form-fill + template notification + Aurum human entry = triggered workflow.

**Constraints reflected:**
- Aurum batch-only (no API) → 4d requires human-assisted entry; no agent can write to Aurum directly
- Driver messaging latency → 2b requires async reasoning with explicit fallback
- Manager approval queue → 4c-ii stays human-only regardless of automation potential
- Audit trail gap (Artefact 2) → 4c-i and 4d must enforce AUDIT_REF in the workflow, not rely on human discipline

**Comparison to Week 1 (HR Onboarding) anti-patterns:**
- Week 1: Some clusters scored "fully agentic" on compliance risk even though auditable events were involved (minor gap).
- Gate 2: Explicitly acknowledging audit trail as mandatory (Artefact 2 incident as learning trigger).

---

## 5. SCORING SUMMARY TABLE

| Cluster | Determinism | Reversibility | Time criticality | Data availability | Compliance risk | Exception frequency | **IMPLEMENTATION** |
|---|---|---|---|---|---|---|---|
| 2a | HIGH | HIGH | MEDIUM | HIGH | HIGH | HIGH | **Workflow / API integration** |
| 2b | MEDIUM | MEDIUM | HIGH | MEDIUM | HIGH | MEDIUM | **LLM Agent-led + escalation** |
| 4a | HIGH | HIGH | MEDIUM | HIGH | HIGH | HIGH | **Rule classifier + LLM fallback** |
| 4b | MEDIUM | MEDIUM | LOW | MEDIUM | MEDIUM | MEDIUM | **Human-led + agent support** |
| 4c-i (<£50) | HIGH | MEDIUM | MEDIUM | HIGH | HIGH* | HIGH | **Workflow rule evaluation** |
| 4c-ii (≥£50) | LOW | MEDIUM | MEDIUM | HIGH | HIGH | MEDIUM | **Human-only** |
| 4d | HIGH | LOW | LOW | MEDIUM | **VERY HIGH** | MEDIUM | **Triggered workflow + human Aurum entry** |

*Audit logging enforced by the workflow — AUDIT_REF + APPROVER_ID mandatory fields. Not optional.

---

## 6. NEXT STEPS

This matrix is the baseline for:
- **Deliverable 3 (Volume × Value)** — Which stream wins? (Likely W4, because investigation + approval complexity is higher; agent support is valuable. Or W2, because volume is highest at 400/day and simple lookup can free up 15+ person-hours/month.)
- **Deliverable 4 (Agent Purpose)** — For the winning stream, design the agent spec including which clusters are in scope and which are out-of-scope.

---

## 7. CRITICAL DESIGN NOTES FOR BUILD

### Audit logging (CRITICAL for compliance)

**Issue (Artefact 2):** Manual credit applied (£170) with no AUDIT_REF. Compliance gap.

**Solution (Cluster 4c-i + 4d):** Agent design must enforce:
- Every credit decision is logged with APPROVER_ID (agent or manager)
- Every credit is linked to AUDIT_REF (case ID or transaction ID)
- Every credit entry includes REASON_CODE (FUEL_RECALC, GOODWILL, INV_CORR, etc.)
- Weekly audit report is generated for Finance review

**If audit logging is not implemented as mandatory in Phase 6 (Build), this design fails compliance review.**

### Escalation protocol (CRITICAL for SLA)

**Issue (Artefact 3 + W2 Zone B):** Driver doesn't respond in time; customer gets stale ETA or escalated complaint.

**Solution (Cluster 2b):** Agent design must include:
- Max 2-min wait for driver response
- Automatic fallback to "afternoon window" if driver doesn't respond
- Optional escalation to dispatcher (adds 3–5 min SLA)
- Explicit decision rule: if response SLA is <7 min, escalate; if ≥7 min, accept fallback

**If escalation protocol is not implemented, agent will hold too long waiting for driver and miss SLA.**

### Data correlation (CRITICAL for accuracy)

**Issue (W4 Zone B):** Exception record missing because driver didn't scan damage in app. Invoice shows damage surcharge, but no linked exception in CRM.

**Solution:** Agent design must handle three states:
1. Exception found + invoice matches → approve credit
2. Exception not found + invoice suggests damage → escalate to dispatcher for retroactive photo
3. Exception exists + invoice doesn't match → investigate discrepancy (escalate to supervisor)

**If correlation logic is not explicit, agent will miss edge cases and approve incorrect credits.**

