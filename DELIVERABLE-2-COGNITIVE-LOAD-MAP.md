# Deliverable 2: Cognitive Load Map — What HR Ops Is Actually Doing

**Organisation:** Aldridge & Sykes — 3-person HR Ops team, 220+ hires per year  
**Purpose of this document:** Break down the onboarding workflow into the specific mental work HR Ops performs — to identify which parts an agent can safely own and which parts require human judgment.

---

## What This Analysis Is For

An agent can't replace judgment it doesn't understand. Before deciding what to automate, we need to know *exactly* what HR Ops is thinking about when they coordinate an onboarding:

- What information do they need at each step?
- Are they making a decision (judgment required) or executing a rule (agent-safe)?
- Where does one person's work stop and another's begin?
- Where does the process *have* to pause for a human?

This document answers those questions by breaking the workflow into four major jobs, then zooming in on each to map the specific tasks, decisions, and handoffs involved.

---

## The Four Jobs HR Ops Is Doing

Each "job" below is a cluster of related work with a single outcome HR Ops is responsible for delivering. Structuring work this way (rather than as a flat list of 40 tasks) reveals where the real coordination load sits and why.

| Job | Outcome HR Ops Must Deliver | Primarily Involves |
|---|---|---|
| **1. Pre-Day-1 Readiness** | New hire and manager are prepared before the start date | HR Ops + IT + Managers |
| **2. Compliance & Legal Readiness** | All legal requirements met before deadlines (I-9, training, background check) | HR Ops + Compliance + Legal |
| **3. Buddy Matching & IT Access** | Hire has a buddy assigned and systems access before Day 1 | HR Ops (buddy decision) + IT (provisioning) |
| **4. Post-Day-1 Monitoring** | Hire completes onboarding milestones through 30 days | Managers + New Hire + HR Ops (monitoring) |

---

## Jobs to be Done — Detail

### JtD 1: "Orchestrate pre-Day-1 readiness" 
**Purpose:** Ensure all Day-1 blockers are resolved and managers are prepared

**Scope:** 18 PRE_DAY_1 tasks (from task registry): HIRE_TYPE_VERIFICATION → MANAGER_HANDOFF_NOTIFICATION

**Why it's a JtD not just tasks:** The cognitive contract is "by start_date, the new hire and manager are ready to engage productively." This requires sequencing (dependencies), judgment (exceptions), and coordination (multiple stakeholders). Failure = delayed productivity, missed compliance, manager confusion.

**Ownership:** Primarily HR Ops + IT + Managers

---

### JtD 2: "Assure compliance and legal readiness"
**Purpose:** Mitigate regulatory risk (I-9, training, background check, NDA)

**Scope:** 6 compliance-critical tasks: I9_VERIFICATION, COMPLIANCE_TRAINING_ASSIGNED, BACKGROUND_CHECK_INITIATED, NDA_SIGNED, EMERGENCY_CONTACT_COLLECTED, DIRECT_DEPOSIT_SETUP

**Why it's a JtD:** Compliance failures have irreversible consequences (I-9 violation = $252–$2,507 penalty; audit finding on training = regulatory exposure). The cognitive work is "detect risk early enough to remediate before deadline."

**Ownership:** HR Ops (primary) + Compliance + Legal

---

### JtD 3: "Match new hire with enabler and mentor"
**Purpose:** Establish buddy relationship and IT access before start date so hire is productive on Day 1

**Scope:** 4 tasks: IT_PROVISIONING_REQUESTED, BUDDY_ASSIGNED, SYSTEM_ACCOUNTS_CREATED, LAPTOP_SHIPPED

**Why it's a JtD:** This is a coordination **and judgment** challenge. The agent must coordinate timing (access before start) with both systems (IT) and people (buddy selection). Buddy matching has judgment (seniority norms, team dynamics) and risk (poor match → retention impact).

**Ownership:** HR Ops (buddy decision) + IT (provisioning execution)

---

### JtD 4: "Monitor post-Day-1 engagement milestones"
**Purpose:** Ensure new hire is on-boarding trajectory through 30 days and manager is engaged

**Scope:** 18 POST_DAY_1 + ONGOING tasks: DAY_1_ORIENTATION_COMPLETE → CHECKPOINT_30_DAY_COMPLETE

**Why it's a JtD:** Post-Day-1 work is mostly execution (new hire completes forms, manager meets with them, payroll processes), but HR Ops is the "monitor and nudge" agent. The cognitive work is "detect when someone is falling behind and intervene early."

**Ownership:** Primarily managers + new hire + HR Ops (monitoring)

---

## Micro-Task Breakdown by Cognitive Zone

Each job is divided into **zones** — clusters of tasks that involve the same *type* of mental activity. For example, "looking up data and applying a rule" is a different cognitive zone from "judging whether something is a real problem or operational noise."

For each zone, the table shows:
- **Input** — what triggers the task
- **Type** — **D** = Decision (human judgment required) or **E** = Execution (a rule can handle it; agent-safe)
- **Output** — what the task produces
- **Data Source** — where the data lives
- **Pause Points** — where a human must intervene (agent handoff boundaries)

### JtD 1: Pre-Day-1 Readiness Orchestration

**Cognitive Zone 1: Intake & Triage**

| Micro-Task | Input | Type | Output | Data Source | Pause Points |
|---|---|---|---|---|---|
| Receive new hire record | HRIS webhook + hire_id, start_date, role, manager_id | **E** — rule-based | Hire object ingested | HRIS | None (deterministic) |
| Verify hire_type (EMPLOYEE vs. CONTRACTOR) | hire_type field + context (employment agreement) | **D** — judgment | Classification confirmed OR ESCALATED to HR Ops | HRIS + employment records | If NULL or ambiguous → escalate |
| Determine applicable tasks (40 vs. subset) | hire_type + role | **E** — rule-based | 20–40 Task objects created per hire_type | Task registry | None (deterministic) |

**Why it's a zone:** All three micro-tasks happen at intake, before any downstream activity. The human pauses here to verify hire_type if ambiguous.

---

**Cognitive Zone 2: Sequence & Dependency Mapping**

| Micro-Task | Input | Type | Output | Data Source | Pause Points |
|---|---|---|---|---|---|
| Calculate task deadlines | hire.start_date + task_type.offset_days | **E** — rule-based | deadline per task | Calendar system | If offset_days is ambiguous (business days vs. calendar days) → infer |
| Resolve dependencies | dependency_task_types from registry | Execution (rule lookup) | dependency_task_ids (Task IDs for this hire) | Task registry | If dependency is circular or undefined → escalate |
| Assess critical path | tasks + deadlines + dependencies | **E** — rule-based | Gantt-like view: which tasks must complete to unblock Day 1? | Task model | If >3 tasks on critical path converge on same date → flag for manager briefing |

**Why it's a zone:** All three involve determining the task graph. Once completed, the rest of the workflow executes against this graph.

---

**Cognitive Zone 3: Proposal Generation & Quality Check**

| Micro-Task | Input | Type | Output | Data Source | Pause Points |
|---|---|---|---|---|---|
| Propose compliance training track | hire_type + role + location | **D** — rule + policy judgment | ComplianceTrainingProposal with confidence level | Compliance matrix | If no matrix row matches (0 of 3 fields align) → LOW confidence → escalate |
| Propose buddy match | hire.department + seniority_level + eligible employees | **D** — rule + seniority judgment | BuddyProposal with rationale + confidence | Employee directory + 90-day history | If seniority_delta > 2 → LOW confidence → escalate; if no candidates → escalate |
| Generate IT provisioning request | hire.role + IT matrix | **D** — rule + policy judgment | ITProvisioningRequest + access_package | IT role-access matrix | If role not found in matrix → HIGH priority escalation |

**Why it's a zone:** All three are proposal generation. These are points where the human reviews and approves (or rejects/overrides) the agent's recommendation. This is the main human-in-loop checkpoint before Day 1.

---

**Cognitive Zone 4: Execution & Coordination**

| Micro-Task | Input | Type | Output | Data Source | Pause Points |
|---|---|---|---|---|---|
| Send welcome materials (5 business days before start) | hire.address + hire_type + material_set_id | **E** — rule-based | Fulfillment API call | Fulfillment system | If address NULL → escalate (missing data) |
| Schedule manager handoff notification | All PRE_DAY_1 tasks complete OR start_date - 2 days | **E** — rule-based | Email to manager with checklist + completion status | Email system | If >2 PRE_DAY_1 tasks incomplete at T-2d → alert flag in email |
| Create 30-day checkpoint meeting | hire.start_date reached + manager + HR Ops availability | **E** — mostly rule-based | Calendar invite + meeting confirmation | Calendar system | If no common availability in window (days 28–32) → escalate to HR Ops for manual scheduling |

**Why it's a zone:** All three are "push" activities (agent sends notifications, triggers workflows) once pre-Day-1 tasks are sufficiently complete.

---

### JtD 2: Compliance & Legal Readiness Assurance

**Cognitive Zone 1: Compliance Intake**

| Micro-Task | Input | Type | Output | Data Source | Pause Points |
|---|---|---|---|---|---|
| Receive compliance requirements | hire_type + role + location + start_date | **E** — rule-based | Compliance task list (BACKGROUND_CHECK_INITIATED, I9_FORM_SENT, NDA_SIGNED, etc.) | Task registry | None (deterministic) |
| Flag high-risk profiles | Background check status + I-9 timing + offers history | **D** — judgment (risk) | Risk score: LOW, MEDIUM, HIGH | Past hire history + risk matrix | If HIGH risk → escalate to Legal |

**Why it's a zone:** Early intake where compliance risk is assessed.

---

**Cognitive Zone 2: I-9 Compliance Monitoring**

| Micro-Task | Input | Type | Output | Data Source | Pause Points |
|---|---|---|---|---|---|
| Poll I-9 completion status | hire_id + hire.start_date + current_date | **E** — rule-based | I9_VERIFICATION task status | HRIS + I-9 system | Check every 2 hours if hire started |
| Calculate days since start | current_date - hire.start_date | **E** — rule-based | Days elapsed | System clock | None |
| Apply federal deadline logic | Days elapsed vs. 3-day threshold | **D** — judgment (consequence) | Escalation: I9_AT_RISK (day 2, URGENT) OR I9_VIOLATION (day 3, CRITICAL) | Regulation + policy | **No discretion:** escalation is mandatory per federal requirement |

**Why it's a zone:** All three tasks focus on one high-consequence compliance item. Cognitive load is detection + timeliness, not complexity.

---

**Cognitive Zone 3: Compliance Training Assignment**

| Micro-Task | Input | Type | Output | Data Source | Pause Points |
|---|---|---|---|---|---|
| Look up compliance matrix row | hire_type + role + location (exact match) | **E** — rule-based | Matrix row or NULL | Compliance matrix | If NULL → escalate (no clear track) |
| Determine confidence | Number of fields matched (3/3, 2/3, 1/3, 0/3) | **E** — rule-based | Confidence: HIGH, MEDIUM, LOW | Logic | None (deterministic) |
| Create proposal or escalate | Confidence level + matrix row | **D** — judgment (risk) | ComplianceTrainingProposal OR ESCALATION | Policy | If confidence < HIGH → escalate to HR Ops |

**Why it's a zone:** Deterministic lookup with one judgment call (when to escalate low-confidence matches).

---

### JtD 3: Buddy Matching & IT Access Enablement

**Cognitive Zone 1: Eligibility Assessment**

| Micro-Task | Input | Type | Output | Data Source | Pause Points |
|---|---|---|---|---|---|
| Query eligible buddies | hire.department + tenure_min=6 months + buddy_available=true + not_assigned_90_days | **E** — rule-based | Candidate list (0–20 employees) | Employee directory | If result = 0 → NO_ELIGIBLE_BUDDY escalation |
| Assess seniority matching | hire.seniority_level vs. each candidate.seniority_level | **E** — rule-based | seniority_delta per candidate | HRIS | None (calculation) |

**Why it's a zone:** Data gathering and eligibility filtering.

---

**Cognitive Zone 2: Buddy Selection (Judgment)**

| Micro-Task | Input | Type | Output | Data Source | Pause Points |
|---|---|---|---|---|---|
| Rank candidates | seniority_delta + tenure_months + past_buddy_performance | **D** — judgment (team dynamics) | Best match candidate + confidence level | Multiple sources | If best match has seniority_delta >2 → flag SENIORITY_GAP, LOW confidence |
| Assess team dynamics | Department + past matches + manager preference (implicit) | **D** — judgment (org knowledge) | Team fit score | Organizational context (tribal knowledge) | Often requires human intuition; agent can't fully codify |
| Create proposal | Selected candidate + rationale + confidence | **E** — rule-based | BuddyProposal object | Proposal template | None (deterministic) |

**Why it's a zone:** This is where the cognitive load is highest. Ranking involves multiple judgment calls. Human must approve.

---

**Cognitive Zone 3: IT Provisioning Execution**

| Micro-Task | Input | Type | Output | Data Source | Pause Points |
|---|---|---|---|---|---|
| Look up IT role-access matrix | hire.role | **E** — rule-based | access_package_id + package_name | IT matrix | If role not found → ROLE_NOT_MAPPED escalation |
| Create provisioning request | hire details + access_package | **E** — rule-based | ITProvisioningRequest object + external_request_id | IT provisioning system API | If API fails → escalate; if 4xx error (invalid role) → escalate |
| Poll for completion | external_request_id | **E** — rule-based | Status: PENDING_APPROVAL, APPROVED, REJECTED, COMPLETED | IT system | If REJECTED → ESCALATION; if timeout >48h → escalate |

**Why it's a zone:** Execution-heavy. One judgment call (role lookup). Mostly deterministic polling and state transitions.

---

### JtD 4: Post-Day-1 Monitoring & Engagement Nudging

**Cognitive Zone 1: Daily Monitoring**

| Micro-Task | Input | Type | Output | Data Source | Pause Points |
|---|---|---|---|---|---|
| Poll task completion status | hire_id + all POST_DAY_1 tasks | **E** — rule-based | Task completion %, overdue count | 6 source systems | If system unavailable >4h → escalate to IT |
| Calculate task aging | completed_at vs. deadline | **E** — rule-based | Overdue_hours per task | Clock | None |
| Detect overdue tasks | Overdue_hours > threshold (24h, 72h) | **E** — rule-based | Alert: MEDIUM (24h) or HIGH (72h) | Thresholds | If overdue >72h and no progress → escalate to manager |

**Why it's a zone:** Monitoring and alerting. Low cognitive load; mostly polling and thresholding.

---

**Cognitive Zone 2: Judgment on Intervention**

| Micro-Task | Input | Type | Output | Data Source | Pause Points |
|---|---|---|---|---|---|
| Assess task blocker | Task status = BLOCKED + blocked_reason | **D** — judgment (legitimacy) | Is blocker real (e.g., awaiting external input) or excuse? | Context | If unclear → escalate to task owner + HR Ops for resolution |
| Decide on escalation level | Task overdue + dependency chain + risk | **D** — judgment (consequence) | Escalation priority: LOW, MEDIUM, HIGH | Task context | If high-risk (e.g., benefits enrollment not done by Day 30) → HIGH |
| Determine human intervention | Escalation priority + task type | **E** — rule-based | Route to: task owner, manager, HR Ops, or specialist | Rules | None (deterministic routing) |

**Why it's a zone:** Light judgment on whether a delay is a real problem or operational noise.

---

## Control Handoffs — Where Work Passes Between People and Systems

A **control handoff** is a moment where responsibility shifts: from human to agent, agent to human, or system back to agent. These are the structural boundaries of the agent's autonomy. Missing them in the design leads to the agent either overstepping (taking actions it shouldn't) or stalling (waiting for input that never arrives).

Eight handoffs are identified below. Each one is described by: what triggers it, why it exists, what happens next, and how it's detected.

**Breakpoint 1: Human → Agent (Hire Creation)**
- **Signal:** Hire record created in HRIS (status = PENDING)
- **Why:** All downstream automation depends on hire record existing
- **What agent does:** Task creation, deadline calculation, initial proposals
- **How to detect:** Webhook on hire creation OR polling HRIS every 15 minutes for new hires

**Breakpoint 2: Agent → Human (Proposal Review)**
- **Signal:** ComplianceTrainingProposal, BuddyProposal, ITProvisioningRequest all created
- **Why:** These are high-confidence rule-based proposals but require human override authority
- **What human does:** Approves or overrides each proposal; may request reassessment
- **How to detect:** Agent pushes proposals to HR Ops approval queue; waits for response

**Breakpoint 3: Human → System (Approval Execution)**
- **Signal:** HR Ops approves a proposal (e.g., BuddyProposal.status = APPROVED)
- **Why:** Approved decision must be written to downstream system (Workday, LMS, etc.)
- **What agent does:** Execute write operation (update hire record, create assignment, send email)
- **How to detect:** Agent monitors BuddyProposal.status field for APPROVED state change

**Breakpoint 4: System → Agent (Status Sync)**
- **Signal:** IT system updates provisioning request status (PENDING_APPROVAL → APPROVED)
- **Why:** External system state changes must trigger agent state updates
- **What agent does:** Update ITProvisioningRequest record, move task to next state
- **How to detect:** Agent polls IT system every 2 hours

**Breakpoint 5: Agent → Human (Escalation Alert)**
- **Signal:** I-9 completion missing at Day 2 (I9_AT_RISK trigger) OR any other escalation condition met
- **Why:** Some conditions have no defined rule; human must decide next action
- **What human does:** Acknowledge escalation, take action (contact hire, escalate to Legal, etc.)
- **How to detect:** Agent creates Escalation object; sends email to HR Ops on-call

**Breakpoint 6: System → Agent (Task Completion)**
- **Signal:** External system reports task completion (e.g., background check completes; BACKGROUND_CHECK_COMPLETE task moves to COMPLETE)
- **Why:** Agent must track completion to unlock dependent tasks
- **What agent does:** Update Task.status, check if dependent tasks can now proceed
- **How to detect:** Agent polls source systems every 2 hours for completion status

**Breakpoint 7: Human → System (Hold Decision)**
- **Signal:** HR Ops marks hire.status = ON_HOLD (due to late I-9, background check failure, etc.)
- **Why:** Hold is irreversible employment action; requires human accountability
- **What agent does:** Stop all non-critical tasks; preserve state for later resumption
- **How to detect:** Agent monitors hire.status field for ON_HOLD transition

**Breakpoint 8: System → Human (Manager Handoff)**
- **Signal:** All PRE_DAY_1 tasks complete OR start_date - 2 days (whichever first)
- **Why:** Manager needs to know onboarding is ready; Day 1 coordination is human's responsibility
- **What agent does:** Send manager notification with completion status
- **How to detect:** Agent checks: all_tasks_complete(hire_id, category=PRE_DAY_1) → send notification

---

## Grounding in Artefacts

All decomposition above is grounded in:

1. **Task Registry (from spec § 3.3):** The 40 task types and their metadata (offset_days, dependencies, owner_type, category)
2. **Delegation Analysis (from spec § 2):** Which tasks are Fully Agentic, Agent-Led+Oversight, Human-Led
3. **Escalation Triggers (from spec § 3.5):** 15+ escalation types indicate where human judgment is needed
4. **Entity State Machines (from spec § 3.3):** Hire, Task, BuddyProposal, ComplianceTrainingProposal, ITProvisioningRequest state transitions show breakpoints
5. **Decision Logic (from spec § 3.6):** Requirements 1–10 detail the specific cognitive steps (deadline calc, buddy matching algo, I-9 monitoring, etc.)

---

## Assumptions & Confidence

| Element | Assumption | Confidence | Validation |
|---|---|---|---|
| JtD 1 completion is binary (all pre-Day-1 or fail) | Medium | Spec allows partial completion with Day-1 manager notification, so not fully binary | Review manager handoff notification logic in practice |
| JtD 2 (compliance) has no judgment | Low | "Compliance" actually has judgment: which back-check vendor? Legal escalation thresholds? | Compliance manager interview |
| JtD 3 buddy matching seniority norm (delta ≤2) is enforced | Medium | Spec defines this as rule but also creates SENIORITY_GAP escalation, suggesting it's often violated | Review past buddy matches; what % exceed delta 2? |
| JtD 4 monitoring is primarily polling (no proactive outreach) | Medium | Spec defines agent reminders but doesn't say who initiates day-1 orientation or policy signing | Manager vs. new hire email patterns: who drives? |
| All cognitive zones are non-overlapping | Medium | Zones are logical clusters but real workflow may interleave (e.g., compliance check may resurface during post-Day-1) | Real-world walkthrough with HR Ops |

---

## What This Tells Us

The breakdown above reveals that the onboarding workflow is not a uniform block of automation opportunity. The work splits roughly as:

- **~50% Execution-heavy** (deadline calculations, monitoring, routing, notifications) — rules are clear, decisions are deterministic, agent-safe
- **~35% Judgment-assisted** (compliance track proposals, buddy ranking, IT provisioning) — agent can generate a proposal, but a human must approve before anything is written
- **~15% Human-only** (hold decisions, hire type classification, escalation responses) — too consequential, too ambiguous, or legally irreversible to automate

The next step scores each task cluster against specific criteria to determine *which* clusters should be automated first and at what level of oversight.

**→ Proceed to Deliverable 3: Delegation Suitability Matrix**
