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

**Archetype: FULLY AGENTIC**

**Rationale:** This task is an ideal candidate for autonomous handling. Agent can independently resolve 95%+ of incoming inquiries without human oversight. For the <5% "not found" cases, agent falls back to: "This delivery is not yet in our system; checking manual records…" or escalates to dispatcher. The only constraint is Salesforce API availability; if API is down, escalate to manual queue. No compliance risk, no reversibility risk, no judgment required.

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

**Archetype: FULLY AGENTIC**

**Rationale:** Dispute triage is an ideal candidate for autonomous handling. Agent can independently log and categorize all disputes. For the <5% ambiguous cases, agent can escalate to billing supervisor with flagged comment: "Dispute type unclear; customer says '[quote]'; recommend manual categorization." No human oversight required for the happy path. Categorization is reversible if needed; no financial transaction has been triggered.

**Escalation triggers:** (1) Dispute type is ambiguous (customer didn't specify reason) → flag for manual triage; (2) Dispute contains multiple issues (e.g., "charged for surcharge + redelivery fee on same invoice") → split into multiple case records or flag for manual handling.

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

**Archetype: FULLY AGENTIC (with audit logging mandatory)**

**Rationale:** Credit approval for <£50 is rule-based and low-consequence. Agent can independently approve. CRITICAL CONSTRAINT: Audit logging is mandatory. Agent must log credit decision with (1) APPROVER_ID = agent ID; (2) AUDIT_REF = case ID; (3) REASON_CODE = category; (4) timestamp. This closes the compliance gap shown in Artefact 2. If audit logging is not enforced, this task downgrades to "agent-led with oversight" (human spot-checks audit trail). Artefact 2 incident (manual credit with no AUDIT_REF) is a known compliance risk; agent design must eliminate this risk.

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

**Archetype: AGENT-LED WITH OVERSIGHT (Audit logging mandatory)**

**Rationale:** Credit entry is deterministic and can be agent-executed, BUT audit logging is mandatory and must be enforced by design. Agent cannot skip AUDIT_REF logging (this is the compliance gap in Artefact 2). Oversight is required on the audit trail, not on the credit decision. Manager (or finance team) must spot-check audit logs weekly to ensure every credit has AUDIT_REF + APPROVER_ID + valid reason code. Agent execution is fast (~2 min); latency comes from Aurum batch (48h if manual ticket required, 24h if system accepts direct entry). Compliance review will scrutinize this step; audit logging is non-negotiable.

**Escalation triggers:** (1) Aurum schema change breaks credit entry form → escalate to IT/Aurum support (manually submit ticket); (2) Customer doesn't see credit on next statement (batch export failed) → investigate batch export logs and resubmit; (3) AUDIT_REF is missing → escalate to finance for audit recovery (compliance incident); (4) Credit amount doesn't match approved amount (data entry error) → reverse and re-enter.

---

## 3. DELEGATION MATRIX SUMMARY

| Cluster | Archetype | Justification | Happy-path handling | Escalation rate | Anti-pattern check |
|---|---|---|---|---|---|
| **2a: Lookup** | **Fully agentic** | Deterministic lookup, no reversibility risk, data available | Agent independently answers 95%+ of inquiries | <5% | ✅ Appropriate; lookup has no risk |
| **2b: ETA + driver sync** | **Agent-led with escalation** | Driver latency is real (5+ min possible); agent must have fallback | Agent provides tight ETA for 80% of active deliveries; escalates to dispatcher or fallback for 20% | ~20% | ✅ Appropriate; escalation protocol prevents SLA miss |
| **4a: Triage** | **Fully agentic** | Deterministic categorization, reversible, no compliance risk | Agent independently categorizes 95%+ of disputes | <5% | ✅ Appropriate; categorization is low-risk administrative task |
| **4b: Validation** | **Human-led with agent support** | Investigation requires judgment + external confirmation; data has lags | Agent surfaces data + initiates external requests; human makes correctness judgment | ~100% (human always involved) | ✅ Appropriate; investigation is complex with multiple data sources |
| **4c-i: Approval <£50** | **Fully agentic** (audit logging required) | Rule-based, low consequence, agent authority threshold | Agent independently approves <£50 credits; logs AUDIT_REF | 0% (deterministic) | ⚠️ **Only if audit logging is enforced.** Artefact 2 shows audit gap (no AUDIT_REF); agent design must eliminate this. |
| **4c-ii: Approval ≥£50** | **Human-only** | Manager authority required; compliance control | Manager always involved; agent routes with summary | ~100% (manager always involved) | ✅ Appropriate; financial control threshold is standard |
| **4d: Execution** | **Agent-led with oversight** (audit logging mandatory) | Deterministic entry, but reversibility risk + audit trail mandatory | Agent enters credit + logs AUDIT_REF; finance spot-checks audit trail weekly | ~5% (schema changes) | ⚠️ **Only if audit logging is non-negotiable.** Artefact 2 incident is a known gap; design must close it. |

---

## 4. ANTI-PATTERN CHECK: "IS EVERYTHING FULLY AGENTIC?"

**Summary distribution:**
- **Fully agentic:** 3 clusters (2a, 4a, 4c-i with audit)
- **Agent-led with escalation/oversight:** 2 clusters (2b, 4d with audit)
- **Human-led with agent support:** 1 cluster (4b)
- **Human-only:** 1 cluster (4c-ii)

**Verdict: ✅ NOT an anti-pattern. Delegation is honest.**

**Rationale:**
- W2 (ETA): Majority of inquiries can be agent-handled (fully agentic), but ~20% require real-time escalation due to driver latency. Escalation protocol is explicit.
- W4 (Billing): Only 2/7 task clusters are fully agentic. Investigation (4b) is explicitly human-led (judgment + external confirmation). Manager approval (4c-ii) is human-only (authority threshold + compliance control). Execution (4d) is agent-led but audit logging is mandatory (oversight-required).
- **Compliance gap is addressed, not hidden.** Artefact 2 shows manual credit audit trail missing. Agent design for 4c-i and 4d explicitly includes AUDIT_REF logging (mandatory, not optional). This closes a known compliance risk.

**Matrix reflects real constraints:**
- Aurum batch-only is a hard constraint (no real-time API) → acknowledged in 4b, 4d
- Driver messaging latency is real (5+ min) → acknowledged in 2b with escalation protocol
- Manager approval queue is real (2–4h) → acknowledged in 4c-ii as human-only
- Audit trail gap is known risk → addressed by making audit logging non-negotiable in 4c-i, 4d

**Comparison to Week 1 (HR Onboarding) anti-patterns:**
- Week 1: Some clusters scored "fully agentic" on compliance risk even though auditable events were involved (minor gap).
- Gate 2: Explicitly acknowledging audit trail as mandatory (Artefact 2 incident as learning trigger).

---

## 5. SCORING SUMMARY TABLE

| Cluster | Determinism | Reversibility | Time criticality | Data availability | Compliance risk | Exception frequency | **ARCHETYPE** |
|---|---|---|---|---|---|---|---|
| 2a | HIGH | HIGH | MEDIUM | HIGH | HIGH | HIGH | **Fully agentic** |
| 2b | MEDIUM | MEDIUM | HIGH | MEDIUM | HIGH | MEDIUM | **Agent-led + escalation** |
| 4a | HIGH | HIGH | MEDIUM | HIGH | HIGH | HIGH | **Fully agentic** |
| 4b | MEDIUM | MEDIUM | LOW | MEDIUM | MEDIUM | MEDIUM | **Human-led + support** |
| 4c-i (<£50) | HIGH | MEDIUM | MEDIUM | HIGH | HIGH* | HIGH | **Fully agentic** (audit required) |
| 4c-ii (≥£50) | LOW | MEDIUM | MEDIUM | HIGH | HIGH | MEDIUM | **Human-only** |
| 4d | HIGH | LOW | LOW | MEDIUM | **VERY HIGH** | MEDIUM | **Agent-led + oversight** (audit required) |

*Audit logging mandatory; if not enforced, compliance risk becomes HIGH (downgrade to Human-only).

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

