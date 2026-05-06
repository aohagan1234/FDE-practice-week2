# DELIVERABLE 1 — COGNITIVE LOAD MAP

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

