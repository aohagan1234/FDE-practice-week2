# Deliverable 5: Agent Purpose Document — Coordination Orchestrator Specification

**Agent Name:** Coordination Orchestrator

**Primary Objective:** Autonomously monitor and orchestrate onboarding task execution across 5 source systems; detect delays, send reminders, escalate blockers.

**Target Release:** Pilot phase (30-day trial with 3–5 hires)

---

## The Problem This Agent Solves

When a new hire joins Aldridge & Sykes, 40 separate tasks need to happen across 5 different systems — IT setup, compliance training, I-9 verification, equipment delivery, and more. None of these systems talk to each other. Someone has to check all of them manually.

That someone is Priya's 3-person HR Ops team. They spend over 550 hours a year just *chasing* — checking whether tasks are done, emailing people who haven't completed theirs, and escalating issues that have gone too long. That's roughly a quarter of each person's working year spent on coordination rather than anything a human is uniquely needed for.

The Coordination Orchestrator takes that coordination work off the team. It watches all 5 systems, spots when tasks are overdue, sends reminders automatically, and escalates problems before they become compliance violations. Humans still make the judgment calls — whether to put a hire on hold, how to handle a disputed contractor classification, which buddy to assign. The agent handles the coordination.

This document specifies exactly what the agent does, where it stops, and what success looks like.

---

## 1. Purpose Statement

The Coordination Orchestrator agent automates the HR Ops team's "monitoring and reminder" workload. It tracks onboarding tasks per hire across 5 source systems (Workday/HRIS, ServiceNow/IT provisioning, Saba LMS/compliance training, calendar, fulfillment), detects when tasks are overdue, sends reminders to task owners, and escalates blockers to HR Ops.

**Primary outcome:** Reduce HR Ops monitoring time by 50%, improve on-time task completion to ≥97%, ensure I-9 compliance with zero violations via automatic Day-2 and Day-3 escalation.

**Success criteria:**
- ≥80% of overdue tasks detected within 4 hours
- ≥99% of reminders delivered (not lost to spam filters or system outages)
- ≥95% of critical escalations (I-9, holds, role-not-mapped) routed correctly to HR Ops on-call
- <2 hours/person/week manual intervention (down from ~4 hours today)

---

## 2. Scope: What the Agent Does and Doesn't Do

The table below separates what the agent handles on its own, what it never touches, and what it does only to alert a human. The goal is to be explicit about boundaries — not because the agent couldn't attempt more, but because the consequences of getting it wrong differ dramatically between categories.

### IN SCOPE (Agent Executes Autonomously)

| Activity | Decision Rule | Output |
|---|---|---|
| **Monitor task status** | Poll 5 source systems every 2 hours for task status | Task status snapshot per hire |
| **Calculate deadlines** | deadline = hire.start_date + task_type.offset_days | Deadline per task |
| **Detect overdue tasks** | if (current_time > deadline + 24h) & (task.status != COMPLETE) → mark OVERDUE_24 | Overdue flags per hire |
| **Send reminders** | if (OVERDUE_24 within last 24h & no reminder in last 24h) → send email to task owner | Reminder email |
| **Escalate I-9 risk** | if (hire.start_date + 2 days == today & i9_task.status != COMPLETE) → escalate I9_AT_RISK | Escalation to HR Ops on-call + HR Manager |
| **Escalate I-9 violation** | if (hire.start_date + 3 days <= today & i9_task.status != COMPLETE) → escalate I9_VIOLATION CRITICAL | CRITICAL escalation; must route to Legal + CEO (per compliance protocol) |
| **Generate manager handoff** | if (all_tasks_complete(hire_id, category=PRE_DAY_1) OR start_date - 2 days reached) → send handoff notification | Handoff email to manager |
| **Batch propose IT provisioning** | if (IT_PROVISION_REQUEST task status = PENDING) & (role found in matrix) → auto-submit to IT system | ITProvisioningRequest object submitted |

### OUT OF SCOPE (Manual or Human-Driven)

| Activity | Why Not Agentic | Who Does |
|---|---|---|
| **Hire type classification** | Judgment required; ambiguous cases need legal review | HR Ops + HR Manager |
| **Buddy matching** | Ranking is deterministic (sort by seniority_delta, tenure, department); team fit selection is human-only judgment | HR Ops (receives sorted candidate list from automation; makes selection based on team dynamics) |
| **Compliance track selection** | Low-confidence matches need policy interpretation | HR Ops + Compliance |
| **Hold decision** | Irreversible employment action; legal implications | HR Manager + Legal |
| **Escalation response** | Agent escalates; human decides action (close, reassign, override) | HR Ops on-call / task owner |
| **IT provisioning approval** | IT system approves/rejects; agent submits only | IT team (in IT system) |

### ESCALATION TRIGGERS (Route to Human)

| Trigger | Condition | Route To | Priority | SLA |
|---|---|---|---|---|
| **I9_AT_RISK** | hire.start_date + 2 days & i9 not complete | HR Ops on-call + HR Manager | HIGH | 15 min |
| **I9_VIOLATION** | hire.start_date + 3 days & i9 not complete | Legal + CEO | **CRITICAL** | 5 min |
| **TASK_OVERDUE_72h** | Any task overdue >72 hours | Task owner + manager | MEDIUM | 2 hours |
| **TASK_BLOCKED_UNRESOLVED** | Task.status = BLOCKED for >24h | Task owner + HR Ops | MEDIUM | 4 hours |
| **ROLE_NOT_MAPPED** | hire.role not found in IT matrix | IT Manager | HIGH | 1 hour |
| **SYSTEM_UNAVAILABLE** | Source system poll fails 3x in a row | IT Support + HR Ops | MEDIUM | 2 hours |
| **NO_ELIGIBLE_BUDDY** | Buddy query returns 0 candidates | HR Ops + Manager | MEDIUM | 4 hours |
| **SENIORITY_GAP** | Best buddy candidate has seniority_delta >2 | HR Ops | LOW | 8 hours |
| **COMPLIANCE_TRACK_UNCLEAR** | Compliance matrix returns 0 rows (no match) | HR Ops + Compliance | MEDIUM | 4 hours |

---

## 3. Autonomy Matrix: Where the Agent Decides and Where It Doesn't

This table lists every decision point in the orchestration cycle and states explicitly who makes it — the agent or a human — and why. If a decision is agent-owned, the criterion is always deterministic (a rule with no judgment). If it's human-owned, the agent escalates and waits.

| Decision Point | Input | Who Decides? | Decision Criteria | Escalation Condition |
|---|---|---|---|---|
| **Task is overdue** | deadline vs. current_time + task.status | Agent | Deterministic: current_time > deadline + 24h | No escalation needed; just flag for reminder |
| **Send reminder** | (OVERDUE & last_reminder >24h ago) | Agent | Deterministic: rate-limit check | If email delivery fails, queue for retry; escalate after 3 retries |
| **I-9 is at risk** | i9_task.status & hire.start_date | Agent | Deterministic: start_date + 2 days == today & not COMPLETE | **Must escalate**; no discretion |
| **I-9 is violated** | i9_task.status & hire.start_date | Agent | Deterministic: start_date + 3 days <= today & not COMPLETE | **Must escalate CRITICAL**; no discretion |
| **IT provisioning request ready** | hire.role + IT matrix lookup | Agent | Deterministic: role found in matrix = submit; not found = escalate | If role not in matrix, escalate ROLE_NOT_MAPPED; don't guess |
| **Manager handoff triggered** | all_tasks_complete(PRE_DAY_1) OR start_date - 2 days | Agent | Deterministic: check both conditions; send if either true | No escalation; send handoff with flags if incomplete |
| **Escalation routing** | Escalation.type + priority | Agent | Deterministic: lookup routing table | No discretion; all escalations route per table |
| **System unavailable** | Poll result = timeout/error | Agent | Deterministic: count retries; escalate after 3 failures | Escalate SYSTEM_UNAVAILABLE; fall back to manual polling |
| **Escalation idempotency** | Any escalation condition met | Agent | Before creating escalation: check if open escalation of same (hire_id, escalation_type) already exists; if yes, skip creation | Prevents alert flooding across poll cycles (e.g., 12 I9_AT_RISK alerts in 24h) |
| **all_tasks_complete definition** | PRE_DAY_1 task list | Agent | `all_tasks_complete` = all tasks where status IN [COMPLETE, SKIPPED]; SKIPPED counts as terminal (contractors have legitimately N/A tasks) | If SKIPPED were not terminal, handoff would never fire for contractor hires |

---

## 4. Activity Catalog: The 9 Things the Agent Does

Each activity below is one discrete unit of agent behaviour. They run together in a 2-hour poll cycle. Activities 1–3 are data-gathering; 4–7 are actions; 8–9 are supporting infrastructure that runs in response to the others.

### Activity 1: Poll Task Status
- **Input:** hire_id, task_ids (array of 40 task types)
- **Process:** For each task, query source system (HRIS, IT provisioning, LMS, etc.) via API
- **Output:** Task status snapshot {task_id, status, last_updated_at, data_freshness}
- **Frequency:** Every 2 hours
- **Retry logic:** On API error, retry after 5 min; if 3 retries fail, escalate SYSTEM_UNAVAILABLE

### Activity 2: Calculate Deadlines
- **Input:** hire.start_date, task_type registry (offset_days per task)
- **Process:** deadline = start_date + offset_days for each task
- **Output:** Array of {task_id, deadline}
- **Frequency:** Once per hire (at intake)
- **Edge case:** If offset_days is NULL or unparseable, escalate DEADLINE_CALC_ERROR (should not happen)

### Activity 3: Detect Overdue Tasks
- **Input:** Task status snapshot, deadline snapshot, current_time
- **Process:** For each task, if (current_time > deadline + 24h) & (status != COMPLETE) → mark OVERDUE
- **Output:** Overdue task list {task_id, days_overdue, owner_type, owner_id}
- **Frequency:** Every 2 hours (with poll)
- **Threshold:** 24-hour grace period (catch delays 1+ days late)

### Activity 4: Send Reminders
- **Input:** Overdue task list, last_reminder timestamp per task
- **Process:** For each overdue task, if (now - last_reminder >24h), compose and send email reminder
- **Output:** Email sent to task owner {recipient, subject, body, send_timestamp}
- **Frequency:** Every 2 hours (check once per cycle)
- **Rate limit:** Max 1 reminder per task per 24h (avoid spam)
- **Template:** Parameterized email with hire name, task name, deadline, link to task in source system

### Activity 5: Monitor I-9 Compliance
- **Input:** hire_id, i9_task.status, hire.start_date, current_date
- **Process:**
  - Every 2 hours, check i9_task.status for all hires in ONBOARDING state
  - Calculate days since start: days_since = current_date - start_date
  - If days_since == 2 & i9_task.status != COMPLETE → escalate I9_AT_RISK
  - If days_since >= 3 & i9_task.status != COMPLETE → escalate I9_VIOLATION
- **Output:** Escalation object {escalation_type, hire_id, severity, timestamp}
- **Frequency:** Every 2 hours (same poll cycle as Activity 1; **not daily** — a daily poll risks missing the 15-minute SLA on Day-2 detection if the poll window doesn't align with the hire's start time)
- **Alert routing:** I9_AT_RISK → HR Ops on-call + HR Manager (email + SMS); I9_VIOLATION → Legal + CEO + HR Manager (email + SMS + phone call)

### Activity 6: Auto-Submit IT Provisioning Requests
- **Input:** hire_id, hire.role, IT role-access matrix (lookup table)
- **Process:**
  - Lookup hire.role in matrix
  - If found → retrieve access_package_id
  - If not found → escalate ROLE_NOT_MAPPED (do not guess)
  - If found → compose ITProvisioningRequest object {hire_id, role, access_package_id, requested_by=agent, requested_at=now}
  - Call IT Provisioning API to submit request
- **Output:** ITProvisioningRequest created in IT system {request_id, status=PENDING_APPROVAL, external_request_id}
- **Frequency:** Once per hire (triggered by IT_PROVISION_REQUEST task becoming READY)
- **Failure handling:** If API rejects (4xx), escalate; if API timeout (5xx), retry exponentially

### Activity 7: Generate & Send Manager Handoff Notification
- **Input:** hire_id, all PRE_DAY_1 task statuses, hire.start_date, current_date
- **`all_tasks_complete` definition:** status IN [COMPLETE, **SKIPPED**] — SKIPPED counts as terminal; contractor hires have legitimately N/A tasks (e.g. I-9 not required for some contractor types) and must not block handoff
- **Process:**
  - Check condition: all_tasks_complete(hire_id, PRE_DAY_1) OR (start_date - 2 == current_date)
  - If condition met, retrieve manager contact from hire.manager_id
  - Compose handoff notification with:
    - ✓ Completed tasks count
    - ✗ Incomplete tasks (if any)
    - 📅 Day 1 checklist preview
  - Send email to manager
- **Output:** Manager notification email {recipient, subject, body, send_timestamp}
- **Frequency:** Once per hire (triggered at Day-2 or all-complete, whichever first)
- **Template:** Parameterized with hire name, manager name, completed/incomplete counts, next steps

### Activity 8: Route Escalations to Correct Owner
- **Input:** Escalation object {type, hire_id, severity}
- **Process:** Lookup escalation routing table → determine recipient(s) and channel (email/SMS/phone)
- **Output:** Escalation notification sent {recipient, channel, timestamp}
- **Frequency:** Immediate (triggered by escalation creation)
- **Routing table:** See Escalation Triggers section above

### Activity 9: Log All Actions & Audit Trail
- **Input:** Every action taken above
- **Process:** Write to audit log {action_type, hire_id, timestamp, input_data, output_data, status, error_if_any}
- **Output:** Audit log entry
- **Frequency:** Real-time (every action)
- **Purpose:** Compliance audit trail; debugging; performance metrics

---

## 5. Key Performance Indicators (KPIs)

### Operational KPIs (Speed & Reliability)

| KPI | Target | Measurement | Owner |
|---|---|---|---|
| **Poll latency** | <4 minutes per hire | Time from data change in source system to agent detection | Agent execution logs |
| **Reminder delivery time** | <30 min from trigger | Time from overdue detection to reminder email sent | Email system logs |
| **Reminder delivery success rate** | ≥99% | % of reminders delivered (not bounced/spam filtered) | Email system + HR Ops report |
| **I-9 detection latency** | <1 hour on Day 2 | Time from Day-2 reached to I9_AT_RISK escalation sent | Agent logs |
| **Escalation routing accuracy** | ≥95% | % of escalations routed to correct owner (no misdirects) | HR Ops QA check |

### Outcome KPIs (Business Impact)

| KPI | Target | Measurement | Owner |
|---|---|---|---|
| **On-time task completion** | ≥97% | % of tasks completed by deadline | Task status (HRIS) |
| **I-9 violation rate** | 0 | # of I-9 violations (federal deadline missed) | Compliance audit |
| **Manager handoff accuracy** | ≥95% | % of handoffs that accurately reflect pre-Day-1 completion | Manager survey |
| **HR Ops manual intervention time** | <2 hrs/person/week | Time spent manually chasing task status or sending reminders | Time tracking |

### Business KPIs (ROI)

| KPI | Target | Measurement | Owner |
|---|---|---|---|
| **HR Ops time freed** | 16 hrs/person/year | Baseline monitoring time (183h/y) - new time (167h/y) | Time tracking |
| **Agent build-to-value payback period** | <24 months | (Build cost + ops cost) / annual value freed | Finance |
| **New hire experience score** | >4.2/5 | Post-30-day survey: "Was onboarding smooth?" | Survey |

---

## 6. Failure Modes & Recovery

| Failure Mode | Detection | Impact | Recovery | Severity |
|---|---|---|---|---|
| **Source system API timeout** | Poll request hangs >5 min | Task status not updated; reminders may be stale | Retry exponentially; escalate SYSTEM_UNAVAILABLE after 3 failures | MEDIUM |
| **Email delivery failure** | Email bounce (4xx) or spam trap | Reminder not received; task owner unaware of overdue | Retry with exponential backoff; escalate after 3 failures; notify HR Ops to manual-send | HIGH |
| **Incorrect deadline calculation** | Calculated deadline is 5+ days off target | Agent sends reminders at wrong time (too early or too late) | Manual review of task registry; recalculate deadlines if error detected; notify engineer | MEDIUM |
| **I-9 monitoring miss** | Day 3 reached but I9_VIOLATION escalation not sent | Federal I-9 violation occurs | CRITICAL: Manual audit trail review; determine why escalation failed; legal notification | **CRITICAL** |
| **Hire record corrupted** | hire.start_date is NULL or far future | Deadline calc fails; agent stalls on this hire | Skip hire; log error; escalate DATA_INTEGRITY_ERROR to IT; investigate HRIS | MEDIUM |
| **Role not in IT matrix** | IT matrix is stale; new role added but not mapped | Agent escalates ROLE_NOT_MAPPED repeatedly (same hire); IT team manually maps each time | Pre-seed matrix with common roles; establish monthly matrix update process; escalate to IT manager if >5 unmapped roles/month | LOW |
| **Duplicate reminders sent** | Idempotency key logic breaks; sends same reminder twice | Task owner receives two emails; confusion; noise | Implement idempotency key (task_id + hire_id + reminder_date = unique key); check before send; log all sends | MEDIUM |
| **Escalation not routed** | Routing table lookup fails; escalation gets lost | High-priority issue (e.g., I9_AT_RISK) is silently ignored | Hard-code escalation routing as fail-safe; no dynamic lookup; test escalations weekly | **CRITICAL** |

---

## 7. System & Data Requirements

**DELIVERABLE-6 supersedes this section** for Saba LMS integration. The table below has been corrected to reflect the SFTP batch approach, but DELIVERABLE-6 contains the authoritative constraint analysis, three-state handling model, and full data dictionary for all source systems. If DELIVERABLE-6 and this section conflict, DELIVERABLE-6 is correct.

### Source Systems (Data Inputs)

| System | Data Provided | API Type | Rate Limit | SLA | Fallback |
|---|---|---|---|---|---|
| **HRIS** | hire records, task status (PRE_DAY_1, POST_DAY_1), manager info, i9_task.status | REST API (OAuth2) | 1,000 req/hr | 99.9% | Batch file sync (daily) |
| **IT Provisioning** | IT access packages, role-access matrix, IT_PROV_REQUEST status, approvals | REST API (API key) | 500 req/hr | 99.5% | Manual ticket system (email) |
| **Saba LMS** | Compliance training enrollment status, COMPLIANCE_TRAINING_ASSIGNED status | **No API — SFTP batch file (weekly, Sunday 02:00 UTC)** | N/A | ~95% batch delivery reliability | Batch file is the only path; no real-time fallback. Detection latency: up to 7 days. See DELIVERABLE-6 for full Saba LMS constraint analysis and three-state handling model. |
| **Calendar System** | Manager availability, IT team calendar for handoff scheduling | CalDAV (open standard) | 1,000 req/day | 99% | Manual scheduling |
| **Email System** | Send reminders, send handoff notifications, send escalations | SMTP (standard) | 10,000 msg/day | 99.95% | Queue and retry; SMS backup |
| **Fulfillment** | Fulfillment order status, shipment tracking (laptop, welcome pack) | REST API (API key) | 500 req/hr | 95% | Manual status check (email) |

### Owner Type → Email Resolution (Gap 3 Fix)

When `task.owner_id` is NULL, the agent resolves the reminder recipient via the table below. `MANAGER` is always resolved from `hire.manager_email`; `SYSTEM`-owned tasks never receive reminders.

| owner_type | Resolution Method | Fallback Email |
|---|---|---|
| **MANAGER** | `hire.manager_email` (runtime lookup) | — |
| **HR_OPS** | Team alias | hr-ops@aldridge.com |
| **IT** | Team alias | it-team@aldridge.com |
| **COMPLIANCE** | Team alias | compliance@aldridge.com |
| **SYSTEM** | No reminder sent | — |

If `owner_id` is populated, the agent calls `GET /emp-get?emp_id={owner_id}` in HRIS to retrieve the individual's email before falling back to the team alias.

---

### Deep-Link URL Templates (Gap 6 Fix)

Each reminder email includes a direct link to the task in its source system. Template `{task_id}` is substituted at runtime.

| Source System | Deep-Link Template |
|---|---|
| **HRIS** | `https://hris.aldridge.com/tasks/{task_id}` |
| **IT_PROVISIONING** | `https://it.aldridge.com/requests/{task_id}` |
| **LMS** | `https://lms.aldridge.com/enrollments/{task_id}` |
| **CALENDAR** | `https://calendar.aldridge.com/events/{task_id}` |
| **FULFILLMENT** | `https://fulfillment.aldridge.com/orders/{task_id}` |
| **EMAIL** | *(no direct link; fallback text: "Check your email inbox")* |

---

### IT Role-Access Matrix (Gap 5 Fix)

**Production endpoint:** `GET https://it.aldridge.com/api/v1/roles/{role_normalized}/access-package`
**Auth:** API key (header `X-API-Key`)  **Rate limit:** 500 req/hr  **Refresh:** IT team updates on role changes; agent re-fetches matrix every 24h

Role lookup uses `role.strip().lower()` to normalise input (handles "Senior Consultant" == "senior consultant"). If role not found → escalate `ROLE_NOT_MAPPED` immediately; do not guess.

---

### Data Entities & Schema

#### Entity 1: Hire

```json
{
  "hire_id": "HI-2025-1234",
  "first_name": "Alice",
  "last_name": "Johnson",
  "role": "Senior Consultant",
  "department": "Strategy",
  "start_date": "2025-02-17",
  "hire_type": "EMPLOYEE",  // or CONTRACTOR
  "manager_id": "MGR-1001",
  "manager_email": "bob@aldridge.com",
  "status": "ONBOARDING",  // or ON_HOLD, COMPLETED
  "office_location": "Manchester",
  "seniority_level": 3,  // 1=entry, 2=mid, 3=senior, 4=lead, 5=director
  "created_at": "2025-02-03T10:30:00Z"
}
```

#### Entity 2: Task

```json
{
  "task_id": "TASK-HI-1234-PRE-001",
  "hire_id": "HI-2025-1234",
  "task_type": "MANAGER_HANDOFF_NOTIFICATION",
  "category": "PRE_DAY_1",
  "status": "PENDING",  // or IN_PROGRESS, COMPLETE, BLOCKED, SKIPPED
  "deadline": "2025-02-15T17:00:00Z",
  "owner_type": "SYSTEM",  // or HR_OPS, MANAGER, IT, COMPLIANCE
  "owner_id": null,
  "source_system": "HRIS",
  "data_freshness": "2025-02-12T14:22:00Z",  // last status update
  "blocked_reason": null,
  "created_at": "2025-02-03T10:30:00Z",
  "completed_at": null,
  "last_reminder_sent_at": null
}
```

#### Entity 3: Escalation

```json
{
  "escalation_id": "ESC-HI-1234-001",
  "hire_id": "HI-2025-1234",
  "escalation_type": "I9_AT_RISK",  // from enum above
  "severity": "HIGH",  // LOW, MEDIUM, HIGH, CRITICAL
  "route_to": ["HR_OPS_ONCALL", "HR_MANAGER"],
  "route_to_emails": ["oncall@aldridge.com", "hr-manager@aldridge.com"],
  "message": "I-9 verification not completed 2 days after start date.",
  "created_at": "2025-02-19T09:00:00Z",
  "acknowledged_by": null,
  "acknowledged_at": null,
  "status": "OPEN",  // or ACKNOWLEDGED, RESOLVED, DISMISSED
  "resolution_notes": null
}
```

#### Entity 4: Reminder

```json
{
  "reminder_id": "REM-HI-1234-TASK-001",
  "hire_id": "HI-2025-1234",
  "task_id": "TASK-HI-1234-POST-015",
  "recipient_email": "alice@aldridge.com",
  "recipient_type": "TASK_OWNER",  // TASK_OWNER, MANAGER, HR_OPS
  "subject": "Action Needed: Compliance Training Not Yet Complete for Alice Johnson (Day 5)",
  "body_template": "Hi Alice,\n\nYour compliance training was due by {deadline}. Please complete it at {lms_link}.\n\nThank you,\nHR Ops",
  "sent_at": "2025-02-18T09:15:00Z",
  "delivery_status": "DELIVERED",  // or PENDING, BOUNCED, SPAM_TRAPPED, FAILED
  "delivery_error": null
}
```

---

## 8. Escalation & Human Oversight

### Escalation Workflows

Each workflow below shows the chain of events from trigger to resolution. The agent handles every step marked "Agent" automatically. Steps marked "Human" require a person to respond.

**Workflow 1: I-9 At-Risk** *(Day 2 after start — highest urgency)*
```
TRIGGER  Day 2 after hire start date; I-9 status not COMPLETE
   │
   ▼ Agent
   Create I9_AT_RISK Escalation (HIGH severity)
   │
   ▼ Agent
   Send email + SMS to: HR Ops on-call + HR Manager
   │
   ▼ Waiting... (SLA: 15 minutes)
   │
   ├── Acknowledged within 15 min ──▶ Human: contact hire; resolve or escalate to Legal
   │
   └── NOT acknowledged in 15 min ──▶ Agent auto-escalates to CEO's office (CRITICAL)
```

**Workflow 2: Task Overdue 72h** *(any task more than 3 days late)*
```
TRIGGER  Task deadline passed by >72 hours; status still not COMPLETE
   │
   ▼ Agent
   Create TASK_OVERDUE_72H Escalation (MEDIUM severity)
   │
   ▼ Agent
   Send email to: task owner (manager/IT/compliance) + HR Ops
   │
   ▼ Waiting... (SLA: 4 hours)
   │
   ├── Resolved within 4 hours ──▶ Task marked complete; escalation closed
   │
   └── NOT resolved in 4 hours ──▶ Human: HR Ops follows up directly (phone call)
```

**Workflow 3: Role Not Mapped** *(IT access can't be auto-submitted)*
```
TRIGGER  hire.role not found in IT role-access matrix
   │
   ▼ Agent
   Create ROLE_NOT_MAPPED Escalation (HIGH severity)
   │
   ▼ Agent
   Email to IT Manager: "Map this role to an access package or approve manually"
   │
   ▼ Waiting... (SLA: 1 hour)
   │
   ├── Approved ──▶ Agent: update matrix + resubmit provisioning request
   │
   └── Denied   ──▶ Agent marks ROLE_NOT_MAPPED_UNRESOLVABLE; escalates to HR Manager
```

### Approval Gates (Human Retains Authority)

| Decision | Agent's Role | Human's Role | Approval SLA |
|---|---|---|---|
| **Approve IT provisioning** | Submit request to IT system | IT system approver reviews (human) | 4 hours |
| **Resolve I-9 at-risk** | Escalate + flag | HR Ops calls hire, escalates to Legal if needed | 15 min for ack; 2 days for resolution |
| **Override task deadline** | Can observe if manager overrides in HRIS | Manager can manually extend deadline | Immediate (no SLA) |

---

## 9. Assumptions & Confidence Levels

| Assumption | Confidence | Validation Method | Impact if Wrong |
|---|---|---|---|
| All 5 source systems have APIs available | LOW | Technical audit with IT; request API docs | If APIs unavailable, polling becomes batch-only (12–24h latency); agent effectiveness drops 60% |
| Task status is updated within 2 hours of completion | MEDIUM | Monitor data freshness field; compare agent detection vs. actual completion time | If latency >4h, reminders will be late; may miss escalation windows |
| HR Ops team responds to escalations within SLA | MEDIUM | Interview Priya; measure actual response times on sample escalations | If response is slow (>30 min), escalation queue grows; agent load backs up |
| I-9 task status is available in HRIS or separate system | HIGH | Confirm in HRIS schema review | If I-9 tracking is manual (email), agent cannot monitor; compliance risk remains |
| Email system can deliver 10,000 reminders/day reliably | MEDIUM | IT audit; email system SLA review | If email fails, reminders don't reach owners; tasks remain overdue |
| IT provisioning system rejects (not crashes) on invalid role | MEDIUM | IT system documentation review; test with invalid role | If system crashes, agent stalls; fallback to manual is needed |
| Hiring volume remains 220+/year (doesn't spike) | MEDIUM | Business forecast review | If volume doubles, latency issues may surface; agent may need performance tuning |

---

## 10. Build Prompt for Implementation

**Prompt for Claude Code / Dev Team:**

> You are building an autonomous onboarding orchestration system. Here's your specification:
>
> **Core mission:** Monitor onboarding tasks per hire across 5 source systems (Workday, ServiceNow, Saba LMS, Calendar, Fulfillment); detect delays; send reminders; escalate blockers.
>
> **Primary features to build:**
> 1. Poll task status from [Workday/HRIS, ServiceNow, Saba LMS, Calendar, Fulfillment] every 2 hours
> 2. Calculate task deadlines (start_date + offset_days)
> 3. Detect overdue tasks (>24 hours past deadline + not complete)
> 4. Send email reminders to task owners (rate-limited to 1 per task per 24h)
> 5. Monitor I-9 completion; escalate I9_AT_RISK on Day 2, I9_VIOLATION on Day 3 (CRITICAL)
> 6. Auto-submit IT provisioning requests (if role found in matrix; else escalate)
> 7. Send manager handoff notification (when pre-Day-1 tasks complete OR Day -2 reached)
> 8. Route all escalations to correct owner (email + SMS for critical)
> 9. Log all actions to audit trail
>
> **Constraints & must-haves:**
> - I-9 escalations have ZERO discretion: mandatory on Day 2 and Day 3
> - Do NOT guess on invalid data; escalate instead (e.g., role not in matrix)
> - Do NOT send duplicate reminders (idempotency key check)
> - Do NOT execute hold decisions; escalate to HR Manager
> - All data must be source-system-agnostic (pull via API or fallback to batch)
>
> **What to build first (confidence order):**
> 1. ✅ **HIGH confidence:** Deadline calculation (pure math)
> 2. ✅ **HIGH confidence:** Task polling + status comparison
> 3. ✅ **HIGH confidence:** I-9 monitoring (deterministic logic)
> 4. ✅ **MEDIUM confidence:** Reminder sending + rate limiting
> 5. ✅ **MEDIUM confidence:** Escalation routing
> 6. 🔶 **LOWER confidence:** IT provisioning auto-submit (test thoroughly)
> 7. 🔶 **LOWER confidence:** Manager handoff logic (depends on HRIS schema)
>
> **What to clarify with stakeholders before building:**
> - API endpoints & authentication for each of 6 systems
> - Current IT provisioning matrix format & update frequency
> - Email template standards & approval process
> - Escalation routing table (who owns each escalation type?)
> - I-9 compliance matrix & notification recipients (Legal? CEO?)
> - Task retry logic on transient failures
>
> **Success criteria for MVP (30-day pilot):**
> - ≥80% of overdue tasks detected within 4 hours
> - ≥99% of reminders delivered successfully
> - ≥95% of critical escalations routed correctly
> - Zero I-9 violations during pilot period
> - <2 hours/person/week manual intervention

---

## Next Steps

1. **Stakeholder Validation:** Present this spec to Priya (HR Ops Lead) and confirm all assumptions, especially around system availability and escalation routing.
2. **Technical Audit:** With IT team, validate API availability and authentication for all 6 systems.
3. **Build Mobilization:** Assign engineer to build core features (deadline calc, polling, I-9 monitoring) first.
4. **Pilot Preparation:** Recruit 5–10 pilot hires for 30-day trial; establish monitoring dashboard to track KPIs.
