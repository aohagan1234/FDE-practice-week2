# Gate2-AnnOHagan.md

**Assessment:** Gate 2 — Cognitive Work Assessment & Agent Design
**Scenario:** Apex Distribution Ltd, Birmingham — Customer Operations
**Participant:** Ann O'Hagan
**Submission date:** 2026-05-06

---

## DELIVERABLE 1 — COGNITIVE LOAD MAP


**Scenario:** Apex Distribution Ltd (Gate 2, Birmingham)  
**Exercise:** Week 2 Assessment, Timed  
**Streams covered:** W2 (ETA inquiries) + W4 (Billing disputes)  
**Rationale for stream selection:** W2 + W4 represent the highest complexity (W2: async driver sync latency; W4: multi-system batch dependency + compliance gap). Together they show agent constraints in both real-time and batch-dependent workflows.

---

## 1. WORK STREAM 2 — ETA INQUIRIES (~400/day, 4 min avg)

### 1.1 Jobs to be Done (User perspective, not system)

**Customer:** "I need to know when my delivery will arrive so I can plan my day."  
**Driver:** "I need to know what my next stop is and when I should be there."  
**Dispatcher:** "I need to keep customers happy with accurate ETAs without getting bogged down in driver comms."

### 1.2 Cognitive zones

**Zone A: Status lookup & classification** (0–1 min)
- *What is happening here?* Agent locates consignment in CRM and determines current delivery state.
- *Why these tasks cluster?* All are deterministic lookups with no judgment required. Success = consignment found + status is clear.
- *Data source:* Salesforce CRM (REST API, real-time customer records)
- *Pause point:* If consignment not found → fallback to "not yet dispatched" or escalate to manual queue.

**Zone B: ETA decision & driver sync** (1–3 min)
- *What is happening here?* Agent either replies directly (if status is pre-dispatch or delivered) or negotiates with driver for tight ETA.
- *Why these tasks cluster?* All involve the same question: "Can I answer this without driver contact, or do I need real-time info from the road?"
- *Data source:* CRM (for status) + Driver app messaging (for active delivery)
- *Pause point:* If driver doesn't respond within 2 min → escalate to fallback response (4h window) or escalate to dispatcher.

### 1.3 Micro-tasks breakdown

| Task | Duration | Deterministic? | Data source | Decision point? | Escalation trigger |
|------|----------|---|---|---|---|
| **1. Consignment ID lookup** | <30 sec | YES (search by ID or order#) | Salesforce CRM (REST API) | NO — system query | Not found (consignment never entered) |
| **2. Status classification** | <30 sec | YES (status enum: pre-dispatch / out-for-delivery / delivered / exception) | CRM status field | NO — deterministic flag | Null status (data error) |
| **3. Route/driver lookup (if active)** | 30 sec | MOSTLY (route code is deterministic; driver identity is deterministic) | CRM + Dispatch console (limited API or manual query) | NO — lookup only | Route data missing or stale (>5 min old) |
| **4. Driver contact (if needed)** | 1–2 min | OPTIONAL (needed only if status = out-for-delivery and no tight ETA available) | Driver app messaging (async) | NO (but triggers escalation risk) | Driver non-responsive >2 min |
| **5. ETA generation** | <30 sec | YES (apply response template based on zone B decision tree) | Prior lookups | NO — templated | N/A |
| **6. Response to customer** | <30 sec | YES (send SMS, email, or in-app notification) | Message queue | NO — execution only | Delivery channel unavailable |
| **Total zone A** | **~1 min** | — | — | — | — |
| **Total zone B** | **1–3 min** | — | — | — | — |
| **Total inquiry lifecycle** | **~4 min** | — | — | — | — |

### 1.4 Control handoffs & lived workflow

**Handoff 1: Intake → Zone A (Automatic)**
- *Who:* Incoming SMS/call system → Agent (or agent pool)
- *How:* Case logged in CRM automatically; routed to next available agent or to intelligent routing queue
- *Duration:* <30 sec
- *Failure mode:* SMS/call system down (rare); case dropped if system unavailable

**Handoff 2: Zone A → Zone B decision (Automatic)**
- *Who:* Agent → Driver app (if needed)
- *How:* Agent queries CRM status. If status = "out for delivery," agent sends message to driver via Driver app.
- *Duration:* <30 sec lookup + 1–2 min wait for driver response
- *Failure mode:* Zone A returns stale status (e.g., status was "out for delivery" at 10:45, but customer data synced at 10:40 and driver just completed delivery at 10:55). Agent gives old ETA.

**Handoff 3: Driver non-response → Escalation (Manual)**
- *Who:* Agent (waiting on driver) → Dispatcher or escalate to customer
- *How:* If driver doesn't respond within 2 min, agent either (a) escalates to dispatcher for manual driver contact (adds 3–5 min), or (b) replies to customer with fallback "afternoon" window.
- *Duration:* 2 min wait + escalation decision
- *Failure mode:* Agent waits >2 min (driver is busy, phone in pocket). Customer loses patience and escalates to complaint.

**Lived workflow vs. SOP:**
- *SOP assumption:* Dispatcher always available to contact driver. *Reality:* Dispatcher is handling 12+ concurrent exceptions (at 12 min avg per exception). Callback is queued, not immediate.
- *SOP assumption:* Driver app status is real-time in CRM. *Reality:* Sync lag is 5–10 min (confirmed in Artefact 3: agent had to manually ask dispatch for GPS ping). CRM refresh is polling-based.
- *Artefact 3 evidence:* Customer asked for tighter ETA; agent queried dispatch manually (not an automated API call); received back "best guess" based on route progress; lag was 5 min (11:19 → 11:24).

### 1.5 Pause points & escalation protocol

| Pause point | Trigger | Action | SLA | Escalation? |
|---|---|---|---|---|
| **Consignment not found** | ID doesn't match any delivery in system | Reply: "Not yet entered / shipping label not scanned" | <1 min | NO (fallback response) |
| **Status = Exception** | Consignment is marked "refused," "damaged," or "on-hold" | Reply with exception reason + reference to case number | <1 min | NO (information delivery) |
| **Status = Out for delivery, driver unresponsive** | Agent messages driver; no response within 2 min | Escalate to dispatcher (adds 3–5 min to SLA) or reply with fallback 4h window | 2 min wait + escalation | YES (escalate to manual dispatcher) |
| **Status = Delivered** | Consignment marked delivered with timestamp | Reply with delivery time + signature scan reference | <1 min | NO |
| **Inquiry deduplication** | Same customer + consignment asked <1h ago | Reply from cache (prior agent's response) if inquiry is identical | <30 sec | NO (efficiency gain) |

### 1.6 Key constraints (from Artefacts + system model)

1. **Driver app messaging is asynchronous.** No guarantee driver sees message in <2 min on busy Friday afternoon (Artefact 3 empirical: 5 min from agent query to dispatch response). Escalation protocol must account for 2+ min fallback.

2. **CRM status sync from Driver app is polling-based, not real-time.** Lag is 5–10 min on normal days, potentially 15+ min on system-busy days. Agent cannot assume CRM reflects current road state.

3. **ETA window offered (4 hours: 13:00–17:00 in Artefact 3) is customer-dissatisfying.** Customers expect <2h windows. Tighter ETA requires driver contact (adds latency). Agent design must balance speed vs. tightness.

4. **Escalation to dispatcher increases total SLA from 4 min to 7–10 min.** If >20% of inquiries need dispatcher escalation, agent is not a time-saver; it's a queuing redistributor.

---

## 2. WORK STREAM 4 — BILLING DISPUTES (~60/day, 28 min avg)

### 2.1 Jobs to be Done (User perspective, not system)

**Customer:** "I was charged for something I don't think I should be charged for. I want it fixed and an explanation."  
**Finance/Billing agent:** "I need to verify the charge is correct, apply credit if needed, and close the case so we don't get escalated."  
**Compliance/audit:** "I need an audit trail showing who approved what credit and why, so we're not exposed on a compliance review."

### 2.2 Cognitive zones

**Zone A: Dispute intake & triage** (0–2 min)
- *What is happening here?* Agent receives dispute (email, call, SMS), logs it in CRM, and categorizes the dispute type (fuel surcharge, redelivery fee, dimensional weight, damage goodwill, invoice error).
- *Why these tasks cluster?* All are deterministic classification tasks with no judgment. Success = dispute is logged and categorized.
- *Data source:* Email / phone / SMS (incoming), Salesforce CRM (log case)
- *Pause point:* If dispute category is ambiguous (e.g., "charge seems high but I don't know why") → ask customer for clarification before proceeding.

**Zone B: Validation & investigation** (2–10 min)
- *What is happening here?* Agent gathers data to verify whether the charge is correct: invoice lookup (Aurum batch export), delivery exception lookup (if damage-linked), shipper confirmation (if dimensional weight), insurance pre-auth (if claim involved).
- *Why these tasks cluster?* All require cross-system data correlation. Risk of gaps is high (data lags, manual linkage, missing exception record).
- *Data source:* Aurum batch exports (APEX_BILL_DAILY, APEX_FUEL_SURCH, APEX_CREDITS, APEX_DISPUTES_OPEN); Salesforce CRM (delivery exception); Insurance system (pre-auth query); Shipper email (confirmation request).
- *Pause point:* If investigation requires shipper confirmation or insurance pre-auth → case enters async wait (24–72h).

**Zone C: Credit decision & approval** (0–2 min or 2–4 hours)
- *What is happening here?* Agent applies decision rule: Is the charge correct? If not, should credit be applied? If credit is <£50, agent approves; if ≥£50, agent escalates to manager.
- *Why these tasks cluster?* All are approval decisions that require authority check. Success = decision is made and logged with approver ID.
- *Data source:* Prior investigation data + approver lookup table (U-0089, U-0042, per APEX_CREDITS schema)
- *Pause point:* If credit ≥£50 → wait for manager approval (2–4h on average, varies with manager queue).

**Zone D: Execution & notification** (2–3 min + 24–48 hour latency)
- *What is happening here?* Agent enters credit into Aurum system (manual UI entry or support ticket), notifies customer, and closes case in CRM.
- *Why these tasks cluster?* All are execution/completion tasks. Data propagation is slow (Aurum batch export T-1 lag, plus 48h support ticket if schema-dependent).
- *Data source:* Aurum UI (manual entry) or support ticket system (escalation); Email / SMS (customer notification)
- *Pause point:* Customer may not see credit on next statement for 2–3 days (batch lag). If customer escalates before credit appears, case reopens.

### 2.3 Micro-tasks breakdown

| Task | Duration | Deterministic? | Data source | Decision? | Escalation trigger |
|------|----------|---|---|---|---|
| **Zone A1: Dispute intake** | <1 min | YES (read email/call, log in CRM) | Email / phone / SMS | NO | Unclear dispute type (ask customer) |
| **Zone A2: Dispute category** | 1 min | YES (apply enum: FUEL_SURCH / REDELIVERY_FEE / DIM_WEIGHT / DAMAGE / INV_ERROR) | Customer text + implicit rules | YES (classify type) | Ambiguous category (escalate to manual review) |
| **Zone B1: Invoice lookup** | 2 min | YES (search Aurum batch by invoice#, customer ID, date range) | Aurum APEX_BILL_DAILY + APEX_FUEL_SURCH | NO (lookup only) | Invoice not found (data lag or customer error) |
| **Zone B2: Charge verification** | 1–3 min | MOSTLY (verify calculation is correct per rule; edge cases require domain judgment) | Invoice data (amount, date, route) + business rule (fuel table, dimensional weight formula) | YES (is charge correct?) | Rule is ambiguous or invoice has data error |
| **Zone B3: Delivery exception lookup (if damage-linked)** | 2 min | YES (search CRM for delivery exception linked to invoice date + customer + amount) | Salesforce CRM case history | NO (lookup only) | Exception not found (damage not recorded; case is unsupported) |
| **Zone B4: Insurance pre-auth query (if damage)** | 3–5 min | PARTLY (lookup is deterministic; approval is not) | External insurance system (slow query) | YES (is claim pre-approved?) | Insurance system unavailable; claim not pre-authorized |
| **Zone B5: Shipper confirmation request (if dim weight)** | 30 sec + 24–72h async | NO (shipper response time varies) | Email to shipper; response time unpredictable | NO (outcome is external) | Shipper doesn't respond (async timeout) |
| **Zone C1: Credit decision rule** | <1 min | YES (apply rule: charge correct? If no, apply credit) | Prior investigation | YES (approve / reject credit) | Judgment call (edge case) |
| **Zone C2: Authority check** | <1 min | YES (if credit <£50, agent approves; if ≥£50, escalate to manager) | Approver lookup table | YES (route to approver) | Amount is edge case (e.g., exactly £50) |
| **Zone C3: Manager approval wait (if ≥£50)** | 2–4 hours | NO (external; depends on manager queue) | Manager email / approval system | NO (external approval) | Manager absent or queue is long |
| **Zone D1: Aurum credit entry** | 2 min + 48h | PARTLY (entry is deterministic; Aurum ticket is slow) | Aurum UI or support ticket form | NO (execution only) | Schema change breaks entry form; ticket forgotten |
| **Zone D2: Audit trail logging** | <1 min | YES (create AUDIT_REF, link to APPROVER_ID) | CRM case log | NO (logging only) | **COMPLIANCE GAP:** Audit trail not created (Artefact 2 incident) |
| **Zone D3: Customer notification** | 1 min | YES (send email/SMS with credit amount + reference) | Email / SMS template | NO (execution only) | Customer address unavailable |
| **Zone D4: Case closure** | <1 min | YES (mark case "resolved" in CRM) | Salesforce CRM | NO (execution only) | Case marked closed prematurely (before credit appears) |
| **Total zone A** | **~2 min** | — | — | — | — |
| **Total zone B** | **5–10 min** (or 24–72h if shipper involved) | — | — | — | — |
| **Total zone C** | **0–2 min** (<£50) or **2–4h** (≥£50) | — | — | — | — |
| **Total zone D** | **2–3 min + 48h** | — | — | — | — |
| **Total dispute lifecycle** | **~28 min** (assuming no async waits + same-day manager approval) | — | — | — | — |

### 2.4 Control handoffs & lived workflow

**Handoff 1: Intake → Triage (Automatic → Manual)**
- *Who:* Customer (email) → CRM routing → Billing agent
- *How:* Email arrives in billing inbox; CRM auto-logs case; agent reviews.
- *Duration:* <2 min
- *Failure mode:* Email routed to wrong queue (customer services vs. billing); agent doesn't see it for 4+ hours.

**Handoff 2: Triage → Investigation (Manual)**
- *Who:* Agent → Aurum system (batch) + Salesforce CRM (lookup)
- *How:* Agent queries Aurum batch export for invoice; if damage-linked, searches CRM for delivery exception.
- *Duration:* 2–10 min (depends on exception lookup latency)
- *Failure mode:* Aurum batch is delayed (T-1 lag); agent searches for invoice dated "today" but batch hasn't been generated yet. Exception record is missing if driver didn't scan damage in app.

**Handoff 3: Investigation → Approval decision (Manual)**
- *Who:* Agent (if <£50) or Agent + Manager (if ≥£50)
- *How:* Agent applies decision rule. If credit ≥£50, routes case to manager via email / approval workflow.
- *Duration:* <1 min (agent) or 2–4 hours (manager queue)
- *Failure mode:* Manager queue is busy (Friday afternoon, 10+ cases waiting). Case sits unreviewed for 8+ hours. Customer escalates.

**Handoff 4: Approval → Execution (Manual)**
- *Who:* Manager (approves) → Agent or Aurum support (executes credit entry)
- *How:* Agent receives approval; enters credit into Aurum UI. If credit requires invoice modification, creates support ticket to Aurum (48h turnaround).
- *Duration:* 2 min + 48h (if ticket required)
- *Failure mode:* Manual credit override is not logged with AUDIT_REF (Artefact 2 incident). Finance has no record of approval. Customer later disputes ("I was promised a credit") and case reopens.

**Handoff 5: Execution → Notification (Async)**
- *Who:* Aurum batch export (T-1) → CRM → Customer
- *How:* Credit is entered in Aurum; batch export runs daily 02:00–04:00 GMT; CRM syncs batch data; customer sees credit on next statement (2–3 days after approval).
- *Duration:* 2 min + 24–48 hours
- *Failure mode:* Batch export fails or is delayed. Credit doesn't appear in APEX_CREDITS export. Customer doesn't see credit on next statement. Case reopens.

**Lived workflow vs. SOP:**
- *SOP assumption:* Damage section (4.3) is complete with rubric. *Reality:* Section 4.3 is incomplete ("TBD pending review of insurance protocol"). No formalized damage assessment rubric exists. Damage claims are approved on a case-by-case basis.
- *SOP assumption:* Credit decisions are always logged. *Reality:* Artefact 2 shows £170 credit applied with no AUDIT_REF. Audit trail gap is a known compliance risk.
- *Artefact 2 evidence:* 9-day email thread showing multiple async waits (customer on hold, agent escalation to manager, billing redirects to customer ops). Internal note shows manual override with no audit trail. Customer frustration is evident ("This is the second time…").

### 2.5 Pause points & escalation protocol

| Pause point | Trigger | Action | SLA | Escalation? |
|---|---|---|---|---|
| **Unclear dispute type** | Customer says "charge seems high" but can't articulate why | Ask for clarification before proceeding | <5 min | NO (customer service) |
| **Invoice not found** | Aurum batch lag; invoice date is "today" but batch hasn't run yet | Wait for next batch (max 24h) or ask customer for invoice copy | <24 h | NO (normal lag) |
| **Delivery exception not found** | Damage claim but no exception record in CRM (driver didn't scan in app) | Request driver to upload damage photo retroactively, or reject claim | <4 h | YES (escalate to dispatch team) |
| **Insurance pre-auth required, system is slow** | Query to insurance takes >5 min | Request pre-auth async; case enters 24h wait | <24 h | YES (async hold) |
| **Shipper confirmation required, shipper doesn't respond** | Dimensional weight dispute; shipper asked for confirmation; no response in 4 hours | Re-send email, set reminder for 24h; case enters async hold | <24–72 h | YES (async hold) |
| **Credit ≥£50, manager approval queue is long** | Case routed to manager; 8+ cases ahead in queue | Agent follows up or escalates to manager's manager if SLA at risk | <4 h | YES (escalate to senior manager) |
| **Aurum credit entry requires schema modification** | Credit reason is "custom" and doesn't map to REASON_CODE enum | Create Aurum support ticket (48h turnaround); case enters 48h hold | <48 h + invoice cycle | YES (external vendor) |
| **Customer escalates before credit appears** | Customer called back saying "I don't see the credit on my statement" (batch lag not yet visible) | Confirm credit was entered; reference AUDIT_REF + batch export date; manage expectations (2–3 day lag) | <2 h | NO (informational, no rework) |
| **Audit trail missing for manual credit** | Agent (or manager) applied credit without AUDIT_REF logging (like Artefact 2 incident) | **COMPLIANCE GAP:** Audit trail is missing; risk is exposure on compliance review | N/A | YES (escalate to Finance for audit recovery) |

### 2.6 Key constraints (from Artefacts + system model)

1. **Aurum batch is T-1.** Invoice data is available daily at 02:00–04:00 GMT. Reconciliation file lags additional 24h. Agent cannot query Aurum in real-time; must work with daily snapshots. This is a hard constraint, not a tuning parameter.

2. **Aurum manual credit entry has no API.** Agent must use UI or create manual support ticket. Ticket turnaround is 48h. This is the bottleneck for dispute resolution speed.

3. **Manual credit audit trail is not automatic.** Artefact 2 shows £170 credit with no AUDIT_REF. Compliance gap is known; agent design must enforce audit logging to close this gap.

4. **Manager approval queue is real.** Artefact 2 shows multi-day resolution for ≥£50 credits. If 20–30% of 60 disputes/day are ≥£50 (= 12–18 escalations/day), and manager can approve 5–6 per hour, queue can back up to 2–3 hours on busy days.

5. **Shipper confirmation blocks for 24–48h.** If 15% of 60 disputes are dimensional weight (= 9 disputes/day), and 50% of shippers respond within 24h, 4–5 disputes/day will backlog waiting for shipper.

6. **Billing system schema changes quarterly without notice.** Agent design must include monitoring/alerting for schema breaks, not assume schema is static.

---

## 3. SUMMARY — ZONES ACROSS BOTH STREAMS

| Work stream | Zone A | Zone B | Zone C | Zone D | Total lifecycle |
|---|---|---|---|---|---|
| **W2 (ETA)** | Status lookup (1 min) | Driver sync / ETA gen (1–3 min) | — | — | ~4 min |
| **W4 (Billing)** | Dispute triage (2 min) | Validation & investigation (5–10 min or 24–72h async) | Approval decision (0–4 hours) | Execution & notification (2–3 min + 48h latency) | ~28 min (or 3–5 days if async waits) |

---

## 4. ANTI-PATTERNS AVOIDED IN THIS CLM

1. ✅ **Lived workflow reflected, not SOP claims.** (e.g., DispatchHub is retired, SOP section 4.3 is incomplete, manual credit audit trail is missing)
2. ✅ **Async waits called out explicitly.** (e.g., driver non-response in W2, shipper confirmation and manager approval queues in W4)
3. ✅ **Compliance gaps highlighted.** (W4 Zone D: manual credit audit trail is missing; agent design must close this gap)
4. ✅ **Escalation protocol is explicit, not vague.** (e.g., W2: driver non-responsive >2 min → escalate to dispatcher or fallback response; W4: credit ≥£50 → manager queue)
5. ✅ **Constraints are named as constraints, not hidden.** (e.g., Aurum batch-only is a hard constraint; manager queue is real; shipper confirmation blocks for 24–48h)

---

## 5. NEXT STEPS

This CLM is the baseline for **Deliverable 2 (Delegation Suitability Matrix).** The micro-tasks, zones, and pause points here will be scored on delegation dimensions (determinism, reversibility, data availability, compliance risk, time criticality, exception frequency) to determine which tasks can be automated, which need human oversight, and which must remain human-only.


---

## DELIVERABLE 2 — DELEGATION SUITABILITY MATRIX


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

**Archetype: FULLY AGENTIC (approval decision only) + AGENT-LED WITH OVERSIGHT (execution)**

**Rationale:** Credit *approval* for <£50 is rule-based and low-consequence — the agent independently makes the approve/reject decision. However, credit *execution* (entering the credit into Aurum) cannot be fully agentic: Aurum has no API, so entry requires either manual UI or a support ticket (48h turnaround). This is handled in Cluster 4d. The boundary is explicit: agent autonomously decides, then initiates execution via the structured path (which enforces audit logging). CRITICAL CONSTRAINT: Audit logging is mandatory. Agent must log credit decision with (1) APPROVER_ID = agent ID; (2) AUDIT_REF = case ID; (3) REASON_CODE = category; (4) timestamp. This closes the compliance gap shown in Artefact 2. If audit logging is not enforced, this task downgrades to "agent-led with oversight" (human spot-checks audit trail). Artefact 2 incident (manual credit with no AUDIT_REF) is a known compliance risk; agent design must eliminate this risk by making the structured entry path the only available path.

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


---

## DELIVERABLE 3 — VOLUME × VALUE ANALYSIS


**Scenario:** Apex Distribution Ltd (Gate 2)  
**Exercise:** Week 2 Assessment, Timed  
**Objective:** Plot 4 work streams on volume × value axes; identify primary agentic target; justify selection.

---

## 1. VOLUME CALCULATION (Monthly, 22 business days)

| Work stream | Daily volume | Avg handling time | Daily hours | Monthly hours (22 days) | % of total 35-person-team output |
|---|---|---|---|---|---|
| **W1: Exceptions** | 180 | 12 min | 36 | 792 | 22.6% |
| **W2: ETA inquiries** | 400 | 4 min | 26.7 | 587 | 16.8% |
| **W3: Adjustments** | 90 | 18 min | 27 | 594 | 17.0% |
| **W4: Billing disputes** | 60 | 28 min | 28 | 616 | 17.6% |
| **TOTAL** | **730** | **~10.5 min avg** | **117.7** | **2,589** | **~74%** |

**Notes:**
- Total team capacity: 35 people × 20 hours/week (9–5 with breaks) × 22 days = ~3,500 hours/month (theoretical full capacity)
- Actual output: 2,589 hours on these 4 work streams = ~74% of team (rest: meetings, admin, edge cases, other projects)
- **Volume leader:** W1 (exceptions, 792 h/month) + W2 (ETA, 587 h/month) = 1,379 h/month = 53% of the 2,589 h total
- **Time-intensive:** W4 (disputes, 28 min avg) is highest per-case effort

---

## 2. VALUE DIMENSIONS (Operational + Strategic)

### 2.1 Operational value (Time savings × Automation potential)

| Stream | Automation potential (from Matrix) | Estimated monthly time savings | FTE equivalent |
|---|---|---|---|
| **W1** | ~50% (exception detection + escalation; damage assessment stays human) | ~396 h/month | 2.0 FTE |
| **W2** | ~95% (lookup fully agentic; ETA generation agent-led with escalation) | ~558 h/month | 2.8 FTE |
| **W3** | ~30% (data surfacing + option generation; human decides) | ~178 h/month | 0.9 FTE |
| **W4** | ~50% (triage + execution + <£50 approval; investigation + ≥£50 approval human-led) | ~308 h/month | 1.5 FTE |

**Calculation:** Monthly hours × automation potential = monthly time savings. FTE = time savings ÷ 200 (hours per FTE per month).

**Ranking by operational value (time savings):**
1. **W2:** 558 h/month (2.8 FTE) — Highest time savings
2. **W1:** 396 h/month (2.0 FTE) — Second highest
3. **W4:** 308 h/month (1.5 FTE) — Lower (compliance complexity reduces automation)
4. **W3:** 178 h/month (0.9 FTE) — Lowest (route re-optimization is hard to automate)

---

### 2.2 Strategic value (Risk reduction + ROI payback)

| Stream | Risk type | Strategic value | ROI payback |
|---|---|---|---|
| **W1** | Reputational (missed exception = angry customer) | MEDIUM | 6–12 months (time savings + risk reduction) |
| **W2** | Service level (stale ETA = lost customer) | LOW | 1–2 months (pure time savings, fastest payback) |
| **W3** | Operational (wrong re-routing = SLA miss + churn) | MEDIUM-HIGH | 12–18 months (risky; slow payback) |
| **W4** | **Compliance (audit trail gap + penalty exposure)** | **HIGH** | **3–6 months (risk reduction worth £100K+ if 1 penalty avoided)** |

**Compliance risk detail (W4):** Artefact 2 shows manual credit audit trail missing (no AUDIT_REF). Compliance review penalty for insufficient audit trail could be £10K–£100K+ depending on jurisdiction. If agent design enforces audit logging, compliance exposure is reduced, justifying investment even with lower time savings.

**Reputational risk detail (W1):** Exception handling failures (missed damages, wrong re-attempts) lead to customer escalation and churn. Volume is high (180/day); one bad exception = multiple customer touches. Strategic value is real but hard to quantify in £.

**SLA risk detail (W3):** Dispatch adjustments have tight SLA. Wrong decision = missed delivery window = penalty to Apex + customer churn. Risk is HIGH; automation potential is LOW (judgment-heavy). Not a good bet for Phase 1.

---

### 2.3 Build complexity & integration risk

| Stream | API availability | Data freshness | External dependencies | Build risk |
|---|---|---|---|---|
| **W1** | CRM lookup (REST API ✓); Dispatch console query (limited SOAP) | Real-time (driver app via CRM) | Insurance (slow); shipper (async) | MEDIUM (dispatch console API limited) |
| **W2** | CRM lookup (REST API ✓); Driver app messaging (async) | 5–10 min lag acceptable | Driver messaging latency (real constraint) | **LOW** (simple lookup + async message) |
| **W3** | Dispatch console (limited API); route optimization (external SaaS?) | Real-time route data needed | Route optimizer API (unknown if exists) | **HIGH** (no route optimizer confirmed) |
| **W4** | CRM + Aurum batch (CSV, T-1 lag, NO API) | 24h lag for batch; shipper async | Aurum batch (slow); shipper (async); insurance (async); manager approval queue | **HIGH** (multiple async waits + Aurum batch dependency) |

---

## 3. VOLUME × VALUE MATRIX

```
                HIGH VALUE (Strategic + Compliance)
                        ↑
                   W4 ◆ |  W1 ◆
                        |
     Build risk: HIGH   |    Build risk: MEDIUM
     ROI: 3–6 mo        |    ROI: 6–12 mo
                        |
────────────────────────┼────────────────────────→ LOW VALUE (Operational only)
                        |
                   W3 ◆ |  W2 ◆
     Build risk: HIGH   |    Build risk: LOW
     ROI: 12–18 mo      |    ROI: 1–2 mo
                        |
   LOW VOLUME (60–90/day) HIGH VOLUME (180–400/day)
```

**Quadrant interpretation:**

- **Upper-right (W1):** HIGH volume, MEDIUM value — Good balance, but build risk is MEDIUM (dispatch console API)
- **Upper-left (W4):** LOW volume, HIGH value (compliance) — Strategic win, but HIGH build complexity (Aurum batch, async waits)
- **Lower-right (W2):** HIGH volume, LOW value (operational only) — Fastest payback, LOWEST risk — **BEST for Phase 1**
- **Lower-left (W3):** LOW volume, LOW value — Avoid; highest complexity + longest payback

---

## 4. DECISION: PRIMARY AGENTIC TARGET

### **Winner: W2 (ETA Inquiries) — Phase 1 primary target**

**Rationale:**

1. **Highest volume leverage:** 400 inquiries/day = 558 h/month savings = 2.8 FTE freed up. At £50K/FTE cost, **£140K/month operational value** (or redeployment capacity).

2. **Lowest build risk:** 
   - Cluster 2a (lookup) is fully agentic with no risk
   - Cluster 2b (ETA + driver sync) has explicit escalation protocol (2 min driver wait, then fallback)
   - No external dependencies (Salesforce REST API is available; driver messaging is async)
   - No compliance complexity (no audit trail needed; SLA miss is service-level, not regulatory)

3. **Fastest ROI payback:** 1–2 months to recover build cost (assuming 4-week build), enabling quick proof-of-value.

4. **Credibility rebuild:** Sarah has seen 2 prior failures (2024 chatbot, RPA). Quick operational win (W2) on ETA handling rebuilds trust. After W2 succeeds, propose W4 as Phase 2 (compliance risk reduction).

5. **Data freshness risk is acceptable:** W2 doesn't depend on Aurum batch (unlike W4). CRM sync lag (5–10 min) is acceptable for ETA inquiries (customer doesn't need tighter than 1h window for most cases).

### **Secondary target: W4 (Billing Disputes) — Phase 2 opportunity**

**Rationale for deferral:**
- Lower volume (60/day vs. 400/day)
- Higher complexity (investigation + async waits: shipper 24–72h, manager queue 2–4h)
- Higher build risk (Aurum batch dependency, no API)
- BUT high strategic value: compliance risk reduction (audit trail gap) + customer satisfaction (faster dispute resolution)

**Recommendation for Sarah (live round):**
> "Build W2 first (ETA, 1–2 month payback, low risk). After W2 proves value in production, we'll propose W4 (Phase 2) — lower volume but higher strategic impact on compliance and customer satisfaction."

---

## 5. AGENT SCOPE FOR W2 (ETA Inquiries)

**In scope (Phase 1):**
- **Cluster 2a:** Consignment lookup + status classification (fully agentic)
- **Cluster 2b:** ETA generation + driver sync (agent-led with escalation)

**Out of scope (future phases or manual):**
- W1 (exceptions) — Defer to Phase 2; higher complexity requires build discipline
- W3 (dispatch adjustments) — Defer indefinitely; requires route optimizer API (not confirmed)
- W4 (billing disputes) — Defer to Phase 2; lower volume, but strategic value after W2 succeeds

**Agent name:** "Coordinator ETA" (works with driver app to provide tight ETAs)

**KPIs (Phase 1):**
- Response time: <5 min (current agent SLA)
- Resolution rate (no escalation): >80% (for active deliveries)
- Accuracy: ETA within ±15 min of actual delivery (customer satisfaction proxy)
- Uptake: % of 400/day inquiries handled by agent vs. human

---

## 6. FINANCIAL SUMMARY

| Metric | W2 (ETA) | W4 (Billing) | W1 (Exceptions) |
|---|---|---|---|
| **Monthly time savings** | 558 h | 308 h | 396 h |
| **FTE equivalent** | 2.8 | 1.5 | 2.0 |
| **£ value (at £50K/FTE)** | £140K/month | £75K/month | £100K/month |
| **Build complexity** | LOW | HIGH | MEDIUM |
| **ROI payback** | 1–2 months | 3–6 months | 6–12 months |
| **Strategic value** | LOW (operational) | HIGH (compliance) | MEDIUM (reputational) |
| **Dependency risk** | LOW | HIGH (Aurum batch) | MEDIUM (Dispatch console) |

**Build cost assumption:** £50–100K (4-week effort for W2; agent + integration testing)

**Payback calculation (W2):**
- £140K/month operational value ÷ £75K build cost = **1 month to break even** (conservative: assumes 50% of time savings are realized in Month 1)

---

## 7. ANTI-PATTERN CHECK

✅ **Not chasing the "sexy" problem:** W4 (compliance) is strategic, but deferring it to Phase 2 is discipline. Building W2 first (operational, low-risk) establishes credibility for Phase 2.

✅ **Not over-scoping:** Staying within W2 clusters 2a + 2b only. Not trying to do W1 + W2 + W4 in parallel.

✅ **Not ignoring risk:** Escalation protocol for 2b is explicit (2 min driver wait, then fallback). Not assuming driver will always respond.

---

## 8. RECOMMENDATION TO SARAH (Live round)

> "The data shows W2 (ETA inquiries, 400/day) is your Phase 1 target. Lowest build risk, highest volume leverage, fastest payback (1–2 months). After W2 succeeds, Phase 2 is W4 (billing disputes) for compliance risk reduction. W3 and W1 stay on roadmap but aren't Phase 1 priorities given build complexity and lower ROI clarity."

---

## 9. NEXT STEP

Deliverable 4 (Agent Purpose Document) designs the full spec for W2: autonomy matrix, escalation triggers, failure modes, success metrics.


---

## DELIVERABLE 4 — AGENT PURPOSE DOCUMENT


**Scenario:** Apex Distribution Ltd (Gate 2)  
**Target:** Work Stream 2 (ETA inquiries)  
**Agent name:** "Coordinator ETA" (working title)  
**Build scope:** Phase 1 (Clusters 2a + 2b from CLM)  
**Timeline:** 4-week build + 2-week testing = 6 weeks to production

---

## 1. EXECUTIVE SUMMARY

**Purpose:** Autonomous handling of customer ETA (estimated time of arrival) inquiries for active and pre-dispatch deliveries. Current state: 400 inquiries/day, 4 min avg handling time = 26.7 person-hours/day. Target: Agent handles 95% independently; human handles <5% (edge cases). Expected outcome: 2.8 FTE freed for 140K/month redeployment value.

**Scope:**
- **In scope:** Consignment lookup (Cluster 2a), ETA generation (Cluster 2b), driver contact protocol
- **Out of scope:** Exception deliveries (damaged, refused, on-hold) → escalate to human; dispatch adjustments; billing disputes

**Success criteria:**
- Resolution rate >80% (no human escalation needed)
- Response time <5 min (match/beat current agent SLA)
- Accuracy: ETA within ±15 min of actual delivery (customer satisfaction proxy)
- Uptake: >95% of 400/day inquiries routed to agent

**Compliance:** None required. ETA provision is service-level; no audit trail needed. SLA miss is reputational, not regulatory.

---

## 2. AGENT AUTONOMY MATRIX

### 2.1 Fully autonomous (Agent decides, no human involved)

| Task | Condition | Decision | Action | SLA |
|---|---|---|---|---|
| **Consignment lookup** | Consignment ID matches CRM record | Status is one of: pre-dispatch, out-for-delivery, delivered | Return status to customer | <1 min |
| **Status = Delivered** | Delivery already completed | Return delivery time + signature | Reply: "Delivered at [time], signed by [name]" | <1 min |
| **Status = Pre-dispatch** | Consignment not yet left warehouse | No driver assigned yet | Reply: "Departing tomorrow 08:00. Will arrive by [next-day window]" | <1 min |
| **Status = Exception** | Delivery flagged as refused / damaged / on-hold | Return exception reason from CRM; create escalation case | Reply: "There's an issue with this delivery — our team will contact you within [SLA]"; route to dispatcher queue | <1 min (reply); dispatcher picks up case |
| **Inquiry deduplication** | Same customer + consignment asked <1h ago | Prior response is cached | Reply from cache (avoid duplicate driver query) | <30 sec |

### 2.2 Agent-led with explicit escalation

| Task | Condition | Happy path | Exception path | Escalation SLA |
|---|---|---|---|---|
| **ETA inquiry for active delivery** | Status = "out-for-delivery" | Query driver via Driver app for current location + next-stop ETA | Driver non-responsive >2 min | 2 min wait, then decide |
| **Driver responds in time** | Driver replies within 2 min | Calculate ETA from driver location + stops remaining + travel time | — | <1 min (templated reply) |
| **Driver doesn't respond in time** | No driver response within 2 min | Reply to customer with fallback "afternoon 13:00–17:00" window; log as escalation attempt | Escalate to dispatcher for manual driver contact (optional, if customer requests tighter ETA) | Reply sent <2.5 min total |

### 2.3 Human-led (Agent surfaces data, human decides)

| Task | Condition | Agent role | Human role | SLA |
|---|---|---|---|---|
| **Consignment not found** | ID doesn't match any CRM record | Flag with comment: "Consignment not found; customer says order [ID]; suggest manual shipper lookup" | Check manual records; confirm shipping label scanned; provide backorder ETA if applicable | <2 min (human response) |
| **Status = Exception** | Delivery marked "refused," "damaged," "on-hold" | Return exception reason from CRM + flag for dispatcher context | Contact customer with root cause + next steps (e.g., "Refused due to damaged pallet; will retry tomorrow") | <5 min (escalate to dispatcher) |
| **Status = Null** | Delivery status is empty/unknown in CRM (data error) | Flag with comment: "CRM status missing for consignment [ID]" | Investigate CRM sync issue; manually confirm delivery state with dispatch | <10 min (investigate) |

---

## 3. ESCALATION WORKFLOWS

### 3.1 Escalation conditions (auto-trigger)

| Trigger | Reason | Action | Route |
|---|---|---|---|
| **Consignment not found** | CRM lookup returns zero results | Reply: "Not in our system; checking manual records…" then escalate | CRM → Manual lookup queue → Human |
| **Driver non-responsive >2 min** | Agent queried driver; no response after 2 min wait | Reply: "Best ETA is afternoon (13:00–17:00). Want exact time?" then escalate | Driver app → Optional dispatcher escalation |
| **Status = Exception** | Consignment flagged for issue (refused, damaged, held) | Return exception + flag for dispatcher | CRM exception flag → Dispatcher queue |
| **CRM API down** | Salesforce REST API unavailable | Route to manual inquiry queue | Failover → Manual agent queue |
| **Driver app messaging unavailable** | Driver app is offline or not responding | Skip driver contact; reply with fallback window | No-op: driver contact skipped; fallback sent |
| **Multiple rapid inquiries for same consignment** | Customer asks 3x in 1 hour for same order | Reply from cache (avoid duplicate driver queries) | Cache hit: deduplicated response |

### 3.2 Escalation protocol details

**Scenario 1: Driver doesn't respond in 2 min**
```
T+00 sec: Agent receives inquiry for consignment #AX-771-3344 (active delivery)
T+05 sec: Agent queries CRM → status = "out-for-delivery" on route 028
T+10 sec: Agent sends message to driver: "Customer asking ETA for drop AX-771-3344. Current location?"
T+70 sec: [Agent waiting for driver response; <50% chance of response by now]
T+120 sec: [No response from driver]
T+121 sec: Agent decides: (a) Reply with fallback window (primary), or (b) Escalate to dispatcher (optional)

Primary (90% of cases): 
  → Reply to customer: "Your delivery is out for delivery. Best guess: 14:00–15:00 today. 
     Driver is in [area]; will call you 30 min before arrival."
  → Log as "driver non-responsive" for weekly metrics
  → Close case

Optional (10% of cases, if customer is VIP or explicitly requests tighter ETA):
  → Escalate to dispatcher with comment: "Customer needs tighter ETA. Can you contact driver?"
  → Dispatcher calls/messages driver manually (adds 3–5 min to SLA)
  → Dispatcher replies to agent; agent forwards tight ETA to customer
  → SLA: 7–10 min total (acceptable for VIP or urgent)
```

**Scenario 2: Consignment not found**
```
T+00 sec: Agent receives inquiry; customer says order #AX-771-3999
T+10 sec: Agent queries CRM → no match found
T+11 sec: Agent replies: "This delivery isn't in our system yet. It may be queued at our warehouse. 
          Let me check manually. I'll call you back in 2 minutes."
T+12 sec: Agent escalates to manual lookup queue (CRM → Human lookup pool)
T+120 sec: Human checks manual records (paper manifest, shipper email, hand-written notes)
T+180 sec: Human replies to customer directly with ETA or status update
```

---

## 4. DECISION TREE (Agent logic flow)

```
START: Customer inquiry received (SMS/call/app)
  │
  ├─→ Parse consignment ID
  │    │
  │    ├─→ ID is valid format? NO → Escalate (manual interpretation)
  │    └─→ ID is valid format? YES → Continue
  │
  ├─→ Query CRM for consignment
  │    │
  │    ├─→ Match found? NO → Escalate to manual lookup
  │    └─→ Match found? YES → Continue
  │
  ├─→ Check CRM status field
  │    │
  │    ├─→ Status = "delivered"? YES → Return delivery time + signature; CLOSE
  │    ├─→ Status = "pre-dispatch"? YES → Return "Tomorrow 08:00–17:00"; CLOSE
  │    ├─→ Status = "exception"? YES → Return exception reason; Escalate to dispatcher; CLOSE
  │    ├─→ Status = Null/unknown? YES → Escalate (data error); CLOSE
  │    └─→ Status = "out-for-delivery"? YES → Continue to ETA generation
  │
  ├─→ Check inquiry cache (did this customer ask <1h ago?)
  │    │
  │    ├─→ Cache hit? YES → Reply from cache; CLOSE
  │    └─→ Cache hit? NO → Continue
  │
  ├─→ Query driver for current location + ETA (async message)
  │    │
  │    ├─→ Wait up to 2 min for driver response
  │    │    │
  │    │    ├─→ Driver responded? YES → Calculate ETA; Reply with tight window (e.g., "14:15–14:45"); CLOSE
  │    │    └─→ Driver didn't respond? NO → Continue to fallback
  │    │
  │    ├─→ Reply with fallback window ("Afternoon, 13:00–17:00")
  │    ├─→ Optional: Escalate to dispatcher (if VIP flag or customer requests manual contact)
  │    └─→ CLOSE
  │
END
```

---

## 5. FAILURE MODES & MITIGATION

| Failure mode | Root cause | Detection | Impact | Mitigation |
|---|---|---|---|---|
| **Stale ETA provided** | CRM status is 5–10 min old; agent gives ETA that was accurate 10 min ago but driver has moved | Customer calls back: "I got delivery 30 min earlier than you said" | Reputational (low); customer wastes time waiting | Accept as acceptable variance. Document expected lag in agent response template: "Best guess based on last update." |
| **Driver non-response timeout causes SLA miss** | Driver phone is off/in pocket; agent waits full 2 min then replies with fallback. Customer expected <5 min response. | Response time >5 min logged; escalates if >10 cases/day exceed SLA | Customer escalation to supervisor | Escalation protocol includes dispatcher override (optional): if SLA at risk, escalate to human for manual driver contact. Accept <5% of cases may miss SLA. |
| **Consignment not found causes false negative** | Shipper hasn't scanned label yet; consignment is on pallet in warehouse but not in CRM. Customer thinks order is lost. | Customer calls back: "You said it's not in the system, but I have the label" | Reputational; customer annoyance | Escalation reply includes: "Checking manual records; shipper may not have scanned the label yet. Standing by." → Hands off to human. |
| **Wrong status returned due to CRM sync lag** | Driver completed delivery 5 min ago but CRM hasn't updated. Agent says "out for delivery" when actually delivered. | Customer says "I got my delivery already at 14:30" but agent said "14:00–15:00" | Low impact; customer has delivery; just timing mismatch | Accept. Include in response: "Status may be a few minutes behind real-time." |
| **API unavailable (Salesforce down)** | REST API timeout or 503 error | CRM query fails; agent gets exception | No ETA provided; customer escalated to manual queue | Failover: Escalate immediately to manual agent pool. SLA becomes human SLA (5–10 min). |
| **Driver app messaging unavailable** | Driver app is offline; agent cannot send message to driver | Message send fails; agent receives error | Driver contact skipped; fallback window sent (acceptable) | Skip driver contact; use fallback window. Accept: driver contact is best-effort, not mandatory. |

---

## 6. SUCCESS METRICS & MONITORING

### 6.1 Primary KPIs

| Metric | Target | Measurement | Frequency |
|---|---|---|---|
| **Resolution without escalation** | >80% | % of 400/day inquiries that agent handles autonomously | Daily |
| **Response time** | <5 min | P50 response time from inquiry receipt to response sent | Daily |
| **ETA accuracy** | Within ±15 min of actual delivery | Matched actual delivery time against agent ETA provided | Weekly |
| **Agent uptake** | >95% of 400/day routed to agent | Count of inquiries → agent pool (vs. manual queue) | Daily |

### 6.2 Secondary KPIs (health/risk)

| Metric | Target | Measurement | Frequency |
|---|---|---|---|
| **Driver response rate** | >80% within 2 min | % of driver queries that get response within 2 min | Weekly |
| **Fallback usage** | <20% of active-delivery inquiries | % of cases where agent gives fallback "afternoon" window | Weekly |
| **Escalation reasons** | Track & trend | % due to (driver non-response / consignment not found / API down / exception flag) | Weekly |
| **CRM API availability** | >99.5% | Uptime of Salesforce REST API (monitored via agent) | Daily |
| **Cache hit rate** | Track & trend | % of inquiries matched to <1h prior inquiry | Weekly |

### 6.3 Success criteria (Phase 1, 8 weeks post-production)

- ✅ Agent handles >80% of 400/day inquiries (320+ cases/day autonomous)
- ✅ Response time P50 <5 min, P95 <10 min
- ✅ ETA accuracy: delivered within ±15 min of agent prediction
- ✅ Zero critical incidents (API down, mass failures)
- ✅ Customer satisfaction: no increase in ETA-related complaints vs. baseline

---

## 7. DATA & INTEGRATION REQUIREMENTS

### 7.1 Data inputs

| Data | Source | API/Access | Freshness | Required? |
|---|---|---|---|---|
| **Consignment ID** | Customer inquiry (SMS/call/app) | Direct input | Real-time | YES |
| **CRM consignment record** | Salesforce CRM | REST API (available) | Real-time (CRM polling-based, 5–10 min lag) | YES |
| **Delivery status** | Salesforce CRM | REST API | 5–10 min lag | YES |
| **Route code** | Salesforce CRM | REST API | Real-time | Conditional (if active delivery) |
| **Driver location** | Driver app | Driver app messaging API (async) | Real-time GPS; message delivery 1–5 min lag | Conditional (if active delivery) |
| **Driver current ETA** | Driver app response (async message) | Driver app messaging | 1–5 min response time | Conditional (best-effort) |

### 7.2 Data outputs

| Data | Target | API/Method | Notes |
|---|---|---|---|
| **ETA reply** | Customer (SMS/call/app) | Message queue → SMS/push/email | Use existing channel (how inquiry arrived) |
| **Escalation flag** | Dispatcher / Manual queue | CRM case creation | Mark case as "escalated from ETA agent" |
| **Audit log** | Internal analytics | Local agent log (CSV daily) | Track resolution, fallback usage, failures |

### 7.3 Integration with existing systems

- **Salesforce CRM:** REST API (stated as available); agent queries consignment table, updates case status
- **Driver app:** Async messaging via existing driver-to-dispatch channel (no new API integration needed; use existing infrastructure)
- **Message queue:** Use existing SMS/call/app routing (agent replies go to same channel as inquiry)
- **Manual escalation:** Create cases in CRM "ETA escalation" queue for humans to handle

**Integration effort:** LOW to MEDIUM. Salesforce CRM REST API is confirmed available. Driver app integration is LOW confidence (D5 Assumption A2): the brief states driver-to-dispatch messaging exists, but whether the agent can programmatically query GPS coordinates or send messages via API is unconfirmed. If the driver app exposes a messaging API, integration effort is LOW. If message-only access exists via the existing dispatch channel, integration effort is MEDIUM (async message pattern). If no API surface is available, the driver contact capability is removed and integration effort drops back to LOW (CRM-only) but ETA tightness degrades.

---

## 8. ASSUMPTIONS & OPEN QUESTIONS

| Assumption | Confidence | Discovery Q |
|---|---|---|
| CRM REST API is available and real-time | MEDIUM | Q2: Is CRM delivery status updated real-time from driver app, or end-of-day batch? |
| Driver app messaging SLA is ~80% within 2 min | LOW | Q3: On Friday PM, 95th %ile latency for driver to receive+read message? |
| Escalation to dispatcher is optional, not mandatory | MEDIUM | Q10: If ETA agent can't reach driver, can it fallback to "afternoon window," or must it always escalate to dispatcher? |
| Customer satisfaction with "afternoon window" is acceptable | MEDIUM | Q5: What's minimum ETA tightness customers expect? (Current offering is 4h; is agent 2h fallback acceptable?) |

---

## 9. ANTI-PATTERNS AVOIDED

✅ **Not assuming 100% autonomous:** Agent-led with escalation (Cluster 2b) explicitly accounts for driver latency. If driver doesn't respond in 2 min, agent has a fallback (doesn't hang).

✅ **Not assuming CRM is real-time:** Noted 5–10 min lag in CLM. Agent accepts stale status as acceptable variance.

✅ **Not over-scoping:** Agent handles ETA inquiries only (W2 Clusters 2a + 2b). Does not handle exceptions (W1), dispatch adjustments (W3), or billing (W4).

✅ **Escalation protocol is explicit, not vague:** Driver non-responsive >2 min → decision rule: primary = fallback reply; optional = escalate to dispatcher.

---

## 10. SCOPE-OUTS FOR FUTURE PHASES

- **W1 (Delivery exceptions):** Defer to Phase 2. Complexity is higher; requires damage assessment rules + insurance lookup.
- **W3 (Dispatch adjustments):** Defer indefinitely. Requires route optimizer API (not confirmed available).
- **W4 (Billing disputes):** Defer to Phase 2. Lower volume; higher compliance complexity.
- **Proactive ETA notifications:** Out of scope. Agent handles reactive inquiries only (customer asks). Future: proactive alerts ("Your delivery will arrive by 3pm") from driver app.

---

## 11. BUILD TIMELINE & HANDOFF

**Phase 1 build (4 weeks):**
- Week 1: Data modeling (CRM schema, driver app schema) + decision tree validation
- Week 2: Agent logic implementation (Clusters 2a + 2b) + escalation protocol
- Week 3: Integration testing (CRM API, driver app messaging, manual queue)
- Week 4: End-to-end testing (100 test cases) + production readiness

**Phase 1 testing (2 weeks):**
- Week 5: Canary rollout (10% of 400/day inquiries = 40/day to agent; 360/day to human) + monitoring
- Week 6: Full rollout (100% of 400/day to agent) + 1-week production stabilization

**Success gate:** If Phase 1 KPIs are met (>80% resolution, <5 min response), Phase 2 is greenlit (W4 agent design).

---

## 12. NEXT STEPS

**Deliverable 5 (System/Data Inventory):** Detail system constraints, Aurum batch specifics, integration risks.

**Deliverable 6 (Discovery Questions):** Ask Sarah the 12 questions; get validation on assumptions (especially driver SLA, CRM real-time status, escalation protocol).

**Deliverable 7 (CLAUDE.md):** Workflow summary + anti-pattern avoidance + lessons learned from review.


---

## DELIVERABLE 5 — SYSTEM/DATA INVENTORY


**Scenario:** Apex Distribution Ltd (Gate 2)  
**Agent in scope:** Coordinator ETA (W2 — ETA Inquiries, Phase 1)  
**Coverage:** All four systems in brief + full Aurum Billing constraint analysis + assumption register

---

## 1. SYSTEM LANDSCAPE

| System | Type | Hosting | API | Key data owned | Relevance to ETA agent | Risk |
|---|---|---|---|---|---|---|
| **Salesforce CRM** | Modern CRM | Cloud (SaaS) | REST API (confirmed available) | Customer records, case history, consignment status, delivery status, route codes | **PRIMARY** — all consignment lookups + escalation case creation | MEDIUM (status freshness unknown) |
| **Driver App** | In-house mobile (iOS/Android) | Internal (cloud backend assumed) | API surface **unconfirmed** | GPS position, route sequence, scan-on-delivery events, driver-to-dispatch messaging | **PRIMARY** — ETA generation depends on driver location + response | HIGH (API surface undefined) |
| **Dispatch Console** | Java desktop via Citrix | On-prem | Limited API ("limited" undefined) | Route assignments, driver allocations, exception triage | OUT OF SCOPE for Phase 1 (W2 only). Relevant for W3 and W1 Phase 2 | HIGH for W3 (read/write capability unconfirmed) |
| **Aurum Billing** | Legacy on-prem ERP (Oracle, 2008) | On-prem | **No API. Batch CSV exports only (02:00–04:00 GMT daily)** | Invoices, fuel surcharges, credits, disputes, reconciliation, customer master | OUT OF SCOPE for Phase 1 (W2 only). Critical constraint for W4 Phase 2 | **CRITICAL** for W4 (batch latency + schema drift) |

---

## 2. DATA INVENTORY — ETA AGENT (W2, Phase 1)

### 2.1 Data inputs to the agent

| Data element | Source system | Access method | Freshness | Required? | Risk |
|---|---|---|---|---|---|
| Consignment ID | Customer (SMS/call/app) | Direct input | Real-time | YES | Low — agent receives it directly |
| Consignment status | Salesforce CRM | REST API (GET /consignment/{id}) | **Unknown — estimated 5–10 min lag from driver app sync** | YES — determines agent decision branch | MEDIUM — stale status produces wrong reply |
| Route code | Salesforce CRM | REST API | Same as status | Conditional | MEDIUM — needed for fallback ETA window calculation |
| Customer record + contact channel | Salesforce CRM | REST API | Near real-time (CRM-native) | YES — reply channel must match inquiry channel | LOW |
| VIP / contract flag | Salesforce CRM (customer master) | REST API | Near real-time | Conditional — needed to decide optional escalation path | LOW |
| Driver current GPS position | Driver App | **API surface unconfirmed** | Real-time (GPS) or message-based (async) | Conditional — needed for tight ETA | **HIGH — if no GPS API, agent must fall back to driver-message pattern only** |
| Driver next-drop sequence | Driver App | **API surface unconfirmed** | Real-time (route loaded at start of shift) | Conditional — needed to estimate drop order | HIGH |

### 2.2 Data outputs from the agent

| Data element | Target | Method | Notes |
|---|---|---|---|
| ETA reply to customer | Customer via original inquiry channel | SMS / push / CRM case reply | Must use same channel as inquiry (SMS → SMS, etc.) |
| Escalation case | Salesforce CRM | REST API (POST /case) | Created with category "ETA_ESCALATION", assigned to dispatcher queue |
| Driver non-response log | Internal analytics store | Agent audit log (structured JSON) | Required for weekly KPI reporting — driver response rate metric |
| Cache entry | Agent local cache | In-memory or Redis | 1h TTL; deduplicate repeat inquiries for same consignment |

### 2.3 Data NOT needed by ETA agent (Phase 1)

The ETA agent intentionally **does not access** Aurum Billing. The consignment lookup, status classification, and ETA generation are all served from CRM + Driver App. Any ETA inquiry that reveals a billing dispute (e.g., customer asks ETA but mentions a disputed invoice) is escalated to a human case with a CRM note — the agent does not attempt to cross-reference Aurum data.

---

## 3. AURUM BILLING — DEDICATED CONSTRAINT ANALYSIS

*Required by brief: "The legacy billing system constraints are part of this — address them, don't hand-wave."*

### 3.1 Batch file catalogue (from Artefact 5 + sample CSVs)

| File | Lag | Frequency | Schema observed | Key fields |
|---|---|---|---|---|
| `APEX_BILL_DAILY` | T-1 (yesterday's invoices) | Daily | INVOICE_NO, CUSTOMER_ID, CUSTOMER_NAME, INVOICE_DT, AMT_NET, AMT_FUEL_SURCH, AMT_VAT, AMT_GROSS, ROUTE_CODE, DEPOT | Primary billing record |
| `APEX_FUEL_SURCH` | T-1 | Daily | INVOICE_NO, ROUTE_CODE, FUEL_RATE_TIER, BASE_NET, FUEL_PCT, FUEL_AMT, CALC_TIMESTAMP, CALC_USER | Fuel surcharge calculation detail |
| `APEX_CREDITS` | T-1 | Daily | CREDIT_ID, INVOICE_NO, CUSTOMER_ID, CREDIT_AMT, REASON_CODE, APPROVER_ID, AUDIT_REF, APPLIED_DT | Credits applied to invoices |
| `APEX_DISPUTES_OPEN` | T-1 | Daily | DISPUTE_ID, INVOICE_NO, CUSTOMER_ID, OPEN_DT, DISPUTE_TYPE, DISPUTE_AMT, ASSIGNED_TO, STATUS, LAST_UPDT | Open dispute register |
| `APEX_RECON` | **T-2** (24h behind invoice generation) | Daily | RECON_ID, INVOICE_NO, EXPECTED_AMT, RECEIVED_AMT, VAR, AGEING_DAYS, FLAG | Payment reconciliation |
| `APEX_AGED_RECEIVABLES` | Weekly (Friday) | Weekly | CUSTOMER_ID, AGE_0_30, AGE_31_60, AGE_61_90, AGE_OVER_90, TOTAL_OPEN | Overdue balances by customer |
| `APEX_CUSTOMER_MASTER` | Monthly (1st of month) | Monthly | CUSTOMER_ID, CUSTOMER_NAME, ACCT_OPEN_DT, CONTRACT_TYPE, RATE_CARD, CR_LIMIT, ACCT_MGR, STATUS | Customer static data |

**Batch delivery window:** 02:00–04:00 GMT daily. Files are written to `/exports/aurum/`. No delivery confirmation mechanism stated — whether files arrive is not guaranteed.

### 3.2 What an agent CAN do with Aurum batch data

| Capability | Mechanism | Latency | Value |
|---|---|---|---|
| Detect open disputes older than X days | Query `APEX_DISPUTES_OPEN`; filter by OPEN_DT + STATUS | T-1 (yesterday's data) | Can triage aging disputes for human follow-up |
| Identify pattern customers (repeat disputes) | Group `APEX_DISPUTES_OPEN` by CUSTOMER_ID; count disputes | T-1 | Hayes & Sons (C-04451) has 3 open FUEL_SURCH_DAMAGE disputes — agent can surface this pattern |
| Cross-reference credit application vs. dispute status | Join `APEX_CREDITS` + `APEX_DISPUTES_OPEN` on INVOICE_NO | T-1 | Can flag disputes where credit has been applied but dispute status not updated to RESOLVED |
| Alert on RECON variance above threshold | Filter `APEX_RECON` by VAR < -£X and FLAG = DISPUTE_OPEN | T-2 (24h lag) | Can surface large reconciliation gaps for investigation |
| Detect audit trail gaps | Check `APEX_CREDITS` for rows with AUDIT_REF = NULL or missing | T-1 | Directly addresses the compliance risk exposed in Artefact 2 |

### 3.3 What an agent CANNOT do with Aurum batch data

| Capability | Reason | Impact |
|---|---|---|
| Modify an invoice in real-time | No API. Invoice modification requires a manual ticket to Aurum support (48h turnaround) | Phase 2 billing agent cannot self-close a dispute by applying a credit — it must escalate to a human who raises the support ticket |
| Check if a credit has been applied to a dispute today | T-1 batch lag means credits applied this morning won't appear until tomorrow's export | Agent may incorrectly show a dispute as "unresolved" when a credit was actually applied hours ago |
| Verify fuel surcharge calculation against current rate card | Rate card data is in `APEX_CUSTOMER_MASTER` (monthly export). FUEL_RATE_TIER changes are not surfaced until the next monthly file | Surcharge dispute resolution depends on data that may be up to 30 days stale |
| Detect a schema change before it breaks the batch ingestion | Schema changes "happen quarterly without prior notice" | A field rename in `APEX_FUEL_SURCH` would silently produce NULLs in the agent's surcharge calculation — wrong outputs with no error |

### 3.4 Critical data integrity observation (from sample data)

**Artefact 2 shows Sandra applied a £170 goodwill credit to INV-2026-04318 (Hayes & Sons, D-2026-00342) on day 6 of the email thread. Internal note: "no entry in the credits audit log."**

Examining the `APEX_CREDITS` export for 2026-04-14:
- CR-2026-00814 shows a £88 GOODWILL credit for C-04451 (Hayes & Sons) with APPROVER_ID U-0089 and AUDIT_REF AUD-2026-00212. This is a different credit amount and different invoice than Sandra's £170.
- There is no CR entry for INV-2026-04318 (the disputed invoice) in the credits file. Sandra's £170 credit is absent.

**Interpretation:** Sandra applied the credit via a path that bypasses Aurum's structured credit entry process. The AUDIT_REF field exists in the schema — suggesting credits *should* be audited — but manual overrides can be applied in a way that skips the export. This is a known compliance exposure. Any Phase 2 billing agent must treat `APEX_CREDITS` as incomplete: it captures structured credits only, not manual overrides.

### 3.5 Fuel surcharge data anomaly

`APEX_FUEL_SURCH` for 2026-04-14 shows three invoices on route R-008 (all tier T3) with different FUEL_PCT values: 11.97%, 9.37%, 12.00%. If T3 is a fixed tier, the percentage should be constant. This suggests either:
1. The fuel percentage within a tier varies by contract (RATE_CARD determines actual %) — not documented in the brief
2. There is a calculation inconsistency in the Aurum batch job

**Impact:** A Phase 2 billing agent that attempts to verify fuel surcharge accuracy will produce incorrect results unless the per-contract rate calculation logic is exposed. This is an assumption to validate with Sarah (see D6 Q5).

### 3.6 Schema drift risk (historical precedent)

The prior RPA project for billing reconciliation "broke whenever Aurum's schema changed." This is not hypothetical — it happened. For any agent ingesting Aurum batch files:

- **Minimum mitigation:** Schema validation step at ingestion (column count, column names, data types) that alerts before parsing
- **Ideal mitigation:** A schema contract (expected columns + types as a config file) checked against each daily export; failures halt processing and alert the billing team
- **Without mitigation:** A quarterly schema change silently corrupts 24h of dispute/credit data before anyone notices

---

## 4. SYSTEMS NOT DETAILED IN THE BRIEF

These systems are implied by the work streams but not named. Each is an assumption requiring validation.

| Implied system | Why implied | Assumption | Confidence | Test |
|---|---|---|---|---|
| **Insurance/claims system** | Damaged consignment exceptions (W1) require insurance involvement to resolve. Artefact 2 shows Hayes & Sons dispute involves a damaged pallet. | An insurance or claims tracking system exists; or claims are handled entirely within CRM case notes | LOW | Ask Sarah: "Where do damage insurance claims get tracked after a customer reports them?" |
| **Route optimisation engine** | Dispatch adjustments (W3) require re-routing logic. The dispatch console is described as "route planning" but the computational engine behind it is unnamed. | Route optimisation is embedded in the dispatch console or handled by a third-party SaaS | LOW | Ask Sarah: "When a driver is diverted, does someone manually re-sequence the route, or does the system suggest a new sequence?" |
| **SMS/contact platform** | Artefact 3 shows an SMS inquiry. The CRM doesn't natively handle SMS for inbound inquiries — a middleware or SMS gateway is implied. | Apex has a third-party SMS platform (Twilio or similar) or the carrier app handles this | MEDIUM | Ask Sarah: "When a customer texts your ETA line, what system receives that message before it reaches an agent?" |
| **VIP/SLA tier flag in CRM** | D4 escalation protocol specifies "if VIP flag" as optional escalation condition for tight ETAs. | Salesforce CRM has a customer tier or VIP field per account | LOW | Ask Sarah: "Do you have any tier or priority classification on customer accounts in Salesforce?" |

---

## 5. INTEGRATION RISKS (ETA AGENT, PHASE 1)

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Driver App has no programmatic API — only in-app messaging | MEDIUM | HIGH — removes GPS-based ETA calculation; agent must rely solely on driver reply | Escalation protocol is already designed for driver non-response; fallback window covers this. Accept if confirmed. |
| CRM delivery status updates are end-of-shift (not real-time) | MEDIUM | HIGH — "out-for-delivery" status could be hours old; ETA accuracy degrades | Include staleness disclosure in agent reply: "Status as of [last-updated timestamp]" |
| Salesforce REST API rate limits hit during peak inquiry period (400/day, AM cluster) | LOW | MEDIUM — API calls throttled; response time increases | Implement inquiry queue with async response; set customer expectation to "within 5 min" rather than instant |
| Driver app messaging channel unavailable (driver phone offline) | HIGH (routine) | LOW — already handled by 2-min wait + fallback window | No change needed; fallback is the primary response for non-responsive drivers |
| CRM consignment ID format mismatch (customer says "AX771" vs CRM stores "AX-771-3344") | MEDIUM | MEDIUM — lookup fails; escalation triggered unnecessarily | Normalisation step at input: strip hyphens, validate prefix, try multiple format variants before declaring not-found |

---

## 6. ASSUMPTION REGISTER

| # | Assumption | Confidence | What changes if wrong | How to test |
|---|---|---|---|---|
| A1 | CRM delivery status is updated from driver app in near-real-time (≤10 min lag) | **MEDIUM** | If end-of-day batch, "out-for-delivery" status is unreliable; agent must disclose staleness or escalate all active deliveries | D6 Q2 |
| A2 | Driver App has a programmatic API that allows the agent to query driver location and send messages | **LOW** | If message-only (no GPS API), ETA calculation is limited to driver-reported location; tight ETAs are not possible without driver cooperation | D6 Q1 |
| A3 | Salesforce CRM is the single source of truth for consignment status (driver app events sync to CRM, not to a separate system) | **MEDIUM** | If driver app has its own status store not synced to CRM, the agent is reading stale data from the wrong system | D6 Q2 |
| A4 | The 400/day ETA inquiry volume is representative of a typical day; peak days do not exceed 2× (i.e., ~800) | **MEDIUM** | If peaks are 3–5× (e.g., pre-holiday), agent SLA targets require revisiting | D6 Q8 |
| A5 | Aurum batch files arrive reliably every morning by 06:00 GMT (after the 02:00–04:00 write window) | **LOW** | If batch delivery fails silently, any Phase 2 agent working from batch data has no data without knowing it | D6 Q4 |
| A6 | The `APEX_CREDITS` batch export captures all credits — including manual overrides | **LOW** — contradicted by Artefact 2 | If manual overrides bypass the export, credits file is incomplete; Phase 2 billing agent will misidentify resolved disputes as open | D6 Q3 |
| A7 | Aurum is managed by an external vendor (not self-hosted by Apex IT) and schema changes originate externally | **MEDIUM** | If Apex IT controls the schema, they can provide advance notice of changes internally — lower risk than assumed | D6 Q4/Q11 |
| A8 | The fuel surcharge percentage within a tier is fixed (e.g., T3 = 12%) and the observed variation in sample data is a data quality issue | **LOW** | If fuel % is contract-specific within a tier, surcharge calculation requires per-customer rate card lookup — much more complex | D6 Q5 |
| A9 | Customer inquiry channel (SMS, phone, app) is recorded in the Salesforce CRM case so the agent can reply on the correct channel | **MEDIUM** | If channel is not recorded in CRM, agent must default to one channel (e.g., SMS) and may mis-route replies | D6 Q10 |
| A10 | The dispatch console "limited API" at minimum supports read queries for route and driver assignment data | **LOW** — "limited" is vague | If no API at all (screen-scraping only via Citrix), W3 automation and W1 Phase 2 have no viable build path | D6 Q6 |

---

## DELIVERABLE 6 — DISCOVERY QUESTIONS


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

---

## DELIVERABLE 7 — CLAUDE.md


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
