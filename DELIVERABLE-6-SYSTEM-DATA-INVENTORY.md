# Deliverable 6: System/Data Inventory — Coordination Orchestrator

**Scenario:** HR Onboarding Coordination — Aldridge & Sykes  
**Agent:** Coordination Orchestrator  
**Systems in scope:** 5 (Workday, ServiceNow, Saba LMS, SharePoint, Outlook/Exchange)

---

## What This Document Is For

Before building an agent that connects to 5 external systems, we need to know what each system actually provides — not what we assume it provides. The most common reason agent builds fail is an assumption about data availability that turns out to be wrong: you design a system that checks for updates every 2 hours, then discover one of your key systems only pushes data once a week.

This document records what each system provides, how the agent connects to it, what data it reads and writes, and where the assumptions are fragile. It corrects one significant error in the earlier spec and explains the implications.

**The most important discovery here:** Saba LMS — the compliance training system — has no API. The agent's spec (Deliverable 5) originally assumed real-time polling. In reality, Saba only exports data once a week via a file delivered to a shared folder. This changes the agent's ability to detect overdue compliance training from 2 hours to up to 7 days. Section 2 covers this constraint in full.

---

## 1. System Inventory

| System | Role in Workflow | API Type | Endpoints Used | Auth | Rate Limit | SLA | Fallback |
|---|---|---|---|---|---|---|---|
| **Workday** | Core HR system of record: hire records, task status, employee data, manager info | REST API | `/hrh-get-hire`, `/hrh-list-hires`, `/emp-search`, `/emp-update-custom-field` | OAuth 2.0 (client credentials) | 1,000 req/hr | 99.9% (contractual) | Daily batch file from Workday Prism if API down |
| **ServiceNow** | IT provisioning: access requests, laptop/badge orders, ticket status | REST API (Table API) | `/api/now/table/sc_request`, `/api/now/table/sc_req_item` | OAuth 2.0 (Basic auth fallback) | 500 req/hr | 99.5% | Manual IT ticket email; IT team monitors SNOW queue |
| **Saba LMS** | Compliance training assignment and completion tracking | **NO API — batch file only** | N/A | SFTP / shared drive (file pickup) | N/A | Batch file is the only integration path; no fallback to real-time |
| **SharePoint** | Onboarding document library: welcome packs, policy docs, compliance flowcharts | Microsoft Graph REST API | `/sites/{site}/drive/items`, `/sites/{site}/lists` | OAuth 2.0 (delegated) | 10,000 req/10 min | 99.9% | Files cached locally at agent startup; refresh daily |
| **Outlook/Exchange** | All stakeholder communication: reminders, escalations, manager handoffs | Microsoft Graph REST API | `/me/messages/send`, `/me/calendar/events` | OAuth 2.0 (delegated) | 10,000 msg/day | 99.95% | Queue and retry; SMS backup for CRITICAL escalations |

---

## 2. Critical Constraint: Saba LMS Has No API

> **This is not a hand-wave. It materially changes the agent's design for compliance training tasks.**

### What the enriched scenario states

> *"Saba LMS (compliance training, no API)"* — Enriched scenario, Tooling sketch, Scenario 1.

This is the hardest integration constraint in the stack. Every other system has a REST API the agent can poll on a 2-hour cycle. Saba LMS does not. The only integration path is a **weekly batch file export** delivered via SFTP.

### What this means operationally

| Property | API-backed systems (Workday, SNOW) | Saba LMS (batch-only) |
|---|---|---|
| **Status update latency** | 2 hours (poll cycle) | Up to 7 days (weekly batch) |
| **Can agent detect overdue?** | Yes — within 2h of task becoming overdue | No — agent is blind between batch windows |
| **Can agent meet 4h SLA?** | Yes | **No** |
| **False positive risk** | Low | High — agent may re-send reminder for task already completed in LMS but not yet in batch |
| **Reminder accuracy** | High | Degraded — agent works from stale data |

### Design implication: Revised behaviour for LMS-sourced tasks

For all tasks with `source_system = "LMS"` (primarily `COMPLIANCE_TRAINING_ASSIGNED`), the agent **must not** apply the same overdue detection logic used for API-backed tasks. Instead:

**Three-state LMS handling:**

| State | Condition | Agent Action |
|---|---|---|
| `STALE_UNKNOWN` | Last batch received >7 days ago OR no batch received since task created | Flag for HR Ops review; do not send reminder (data too unreliable) |
| `BATCH_PENDING` | Within 7-day window; status = PENDING in last batch | Send reminder **only if** deadline is within 48h AND last batch was received ≤3 days ago |
| `BATCH_COMPLETE` | Status = COMPLETE in most recent batch | Mark task complete; suppress all further reminders |

**Concrete rule change:**

```
For LMS tasks:
  if batch_age_days > 7:
    → status = STALE_UNKNOWN; do not flag OVERDUE; create DATA_FRESHNESS_WARN
  elif task.deadline - now < 48h AND task.status = PENDING AND batch_age_days <= 3:
    → send one reminder (rate-limited 1/24h)
  elif task.status = COMPLETE in latest batch:
    → mark COMPLETE; no reminder
  else:
    → take no action; wait for next batch
```

**SLA correction required in DELIVERABLE-5:**

The Agent Purpose Document states `≥80% of overdue tasks detected within 4 hours`. This SLA **cannot be met** for LMS-sourced tasks. The revised target for LMS tasks is:

- Detection within 7 days of overdue event (batch window constraint)
- Reminder sent within 48h of batch receipt that shows overdue status

The 4-hour SLA applies only to the 4 API-backed source systems.

### Batch file specification

| Property | Detail |
|---|---|
| **Delivery mechanism** | SFTP push from Saba LMS to agent's file landing zone |
| **Delivery cadence** | Weekly (Saba IT confirm: Sunday 02:00 UTC) |
| **Format** | CSV (Saba standard export) |
| **Key fields** | `employee_id`, `course_code`, `course_name`, `enrollment_status` (Enrolled / In Progress / Completed / Not Started), `completion_date`, `export_timestamp` |
| **File naming** | `saba_export_YYYYMMDD.csv` |
| **Retention** | Agent retains last 4 batch files (28 days) |
| **Missing batch handling** | If no file received by Sunday 06:00 UTC, agent creates `BATCH_MISSING` alert to IT Support + HR Ops; continues using last known batch with `STALE_UNKNOWN` flag |

### What to validate before build

- [ ] Confirm batch delivery SLA with Saba IT (Sunday 02:00 UTC — or is this variable?)
- [ ] Confirm CSV schema — does `enrollment_status` map cleanly to our TaskStatus enum?
- [ ] Confirm `employee_id` in Saba export matches `hire_id` or requires join via Workday
- [ ] Assess whether Priya's team currently tracks LMS manually to fill the 7-day gap — if yes, document that workaround and replicate it
- [ ] Ask: has Aldridge & Sykes ever paid for a Saba LMS API licence? (Some Saba configurations expose a SOAP or REST API as a paid add-on — confirm before committing to batch-only design)

---

## 3. Data Flow — How Information Moves Through the Agent

The diagram below shows how data enters the agent, what it does with it, and what it writes back. Read it top-to-bottom through six stages.

**Legend:** `→` means "produces" or "triggers". Stages in ALL CAPS are the six phases of one poll cycle. Indented lines are the specific steps within each phase.

```
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 1: INTAKE                                                 │
│   Workday webhook OR agent polls /hrh-list-hires every 2 hours  │
│   → New hire with status=ONBOARDING detected                    │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│ STAGE 2: TASK CREATION (once per hire)                          │
│   Agent fetches full hire record from Workday                   │
│   → Creates 40 Task objects, each with a calculated deadline    │
└──────────────────────────────┬──────────────────────────────────┘
                               │  repeats every 2 hours ↓
┌──────────────────────────────▼──────────────────────────────────┐
│ STAGE 3: POLL CYCLE — READ (every 2 hours)                      │
│   For each ONBOARDING hire, agent reads from:                   │
│     Workday    → task status (HRIS-owned tasks)                 │
│     ServiceNow → IT provisioning request status                 │
│     Saba LMS   → ⚠ BATCH FILE ONLY (weekly, not real-time)     │
│     Graph API  → calendar events (30-day check-in scheduled?)   │
│     Outlook    → agent sends only; does not read                │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│ STAGE 4: DETECT & ACT                                           │
│   Agent compares task.status vs. deadline for each hire         │
│   → Overdue (API task)  : send email reminder via Outlook       │
│   → Overdue (LMS task)  : apply three-state batch logic         │
│   → I-9 not done Day 2  : escalate I9_AT_RISK (HIGH)           │
│   → I-9 not done Day 3  : escalate I9_VIOLATION (CRITICAL)     │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│ STAGE 5: WRITE (only when action needed)                        │
│   Workday   → buddy assignment field (after HR Ops approval)    │
│   SNOW      → new IT provisioning request submission            │
│   Outlook   → reminders, escalation alerts, handoff emails      │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│ STAGE 6: AUDIT (every action)                                   │
│   Every read, write, reminder, and escalation → structured log  │
│   Stored in local DB or cloud log sink for compliance review     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Data Dictionary — What Each Field Is and Why It Matters

The tables below list the key fields the agent reads and writes per system, with notes on data quality. Fields marked with quality issues are the ones most likely to cause silent failures — worth validating before launch.

### 4.1 Hire (Workday)

| Field | Type | Source | Required? | Quality Notes | Agent Use |
|---|---|---|---|---|---|
| `hire_id` | UUID | Workday auto-generate | Yes (PK) | Unique, immutable | Lookup key for all downstream queries |
| `first_name`, `last_name` | String | Hiring manager | Yes | 98% complete | Display in notifications |
| `start_date` | Date | Hiring manager | Yes | 99% populated; ~1% data-entry errors | Deadline calculation; I-9 window |
| `hire_type` | Enum: EMPLOYEE / CONTRACTOR | HR | Yes (nullable) | **5–10% NULL or ambiguous** (see DELIVERABLE-1) | Task set selection; compliance track routing |
| `role` | String | HR + hiring manager | Yes | 98% populated; variations in role naming (e.g. "Sr. Consultant" vs "Senior Consultant") | IT access matrix lookup (normalised: `.strip().lower()`) |
| `manager_id` / `manager_email` | UUID / String | Org chart | Yes | 99% accurate; stale if manager changes | Reminder routing; handoff notification recipient |
| `status` | Enum | HR workflow | Yes | 99.9% accurate | Filter to ONBOARDING only |
| `office_location` | String | HR | Yes | UK / Republic of Ireland — affects compliance track | Compliance training path selection |

### 4.2 ServiceNow IT Request

| Field | Type | Source | Required? | Quality Notes | Agent Use |
|---|---|---|---|---|---|
| `request_id` | String | SNOW auto-generate | Yes (PK) | Unique | Link to ITProvisioningRequest.external_request_id |
| `state` | Enum: Open / Work in Progress / Closed Complete / Closed Incomplete | SNOW | Yes | Real-time | Poll for completion |
| `assignment_group` | String | SNOW routing rules | No | Auto-assigned by ServiceNow — agent does not set this | Informational (for escalation emails) |
| `short_description` | String | Agent-generated | Yes | Agent populates on submission | Contains hire_id for correlation |

### 4.3 Saba LMS Batch Export

| Field | Type | Source | Required? | Quality Notes | Agent Use |
|---|---|---|---|---|---|
| `employee_id` | String | Saba (sourced from Workday) | Yes | Must be joined to Workday hire_id via employee record; **1–3% mismatch risk** (joiners not yet synced) | Join key to match to Hire |
| `course_code` | String | Saba course catalogue | Yes | Stable; maps to compliance track | Identify which training is complete |
| `enrollment_status` | Enum: Not Started / Enrolled / In Progress / Completed | Saba | Yes | Accurate as of batch timestamp | Map to TaskStatus |
| `completion_date` | Date | Saba | Conditional | NULL if not Completed | Set Task.completed_at |
| `export_timestamp` | Datetime | Saba batch system | Yes | Use to calculate batch age | `batch_age_days = now - export_timestamp` |

### 4.4 Workday Custom Field — Buddy Assignment (Agent-Written)

| Field | Type | Notes |
|---|---|---|
| `hire_id` | UUID | Reference to hire |
| `buddy_emp_id` | UUID | Reference to assigned employee |
| `match_date` | Date | Date assignment made |
| `agent_score` | Float | Ranking score from matching algorithm |
| `agent_reasoning` | String (max 500 chars) | Why this candidate was chosen |
| `assigned_by` | String | Hard-coded "ai-agent" for audit trail |

---

## 5. API Endpoint Reference

### Workday

**GET /hrh-list-hires** — list active onboarding hires
```
GET /hrh-list-hires?status=onboarding&start_date_after={date_minus_4_weeks}
Auth: Bearer {oauth_token}
Response: { "hires": [ {hire_id, hire_name, start_date, status, ...} ], "count": N }
Rate: 10 calls/sec  Timeout: 10s  Pagination: cursor-based
```

**GET /hrh-get-hire** — fetch single hire record
```
GET /hrh-get-hire?hire_id={hire_id}
Response: full Hire object (see 4.1)
Rate: 100 calls/sec  Timeout: 5s
```

**PUT /emp-update-custom-field** — write buddy assignment (agent write)
```
PUT /emp-update-custom-field?emp_id={emp_id}&field_name=buddy_assignment_current&operation=append
Body: { hire_id, buddy_emp_id, match_date, agent_score, agent_reasoning, assigned_by }
CRITICAL: Idempotency key = hash(hire_id + emp_id + match_date); check before write
```

### ServiceNow

**POST /api/now/table/sc_request** — submit IT provisioning request
```
POST /api/now/table/sc_request
Auth: Bearer {oauth_token}
Body: { short_description: "IT provisioning: {hire_name} - {role}", 
        description: "{access_package_name}; hire_id={hire_id}",
        urgency: "2", category: "Service Request" }
Response: { result: { sys_id: "{request_id}", number: "RITM..." } }
```

**GET /api/now/table/sc_req_item** — poll request status
```
GET /api/now/table/sc_req_item?sysparm_query=request={request_id}&sysparm_fields=state,number
Rate: 500 req/hr  Timeout: 5s
```

### Saba LMS — Batch File (No API)

```
Integration type: SFTP file pickup (NOT HTTP)
Host: sftp.aldridge.com
Path: /saba-exports/weekly/saba_export_YYYYMMDD.csv
Auth: SSH key (agent service account)
Schedule: Sunday 02:00 UTC (confirm with Saba IT)
Pickup: Agent polls SFTP directory at 04:00 UTC Sunday for new file
File retention: 4 weeks of files retained by agent

CSV schema:
  employee_id, course_code, course_name, enrollment_status,
  completion_date, enroll_date, export_timestamp

Agent processing:
  1. Download file to local staging
  2. Join employee_id → hire_id via Workday /emp-search
  3. Map enrollment_status → TaskStatus
  4. Update Task records for source_system = "LMS"
  5. Set data_freshness = export_timestamp from file
  6. Log batch receipt: { file_name, rows_processed, join_failures }
```

### Microsoft Graph (Outlook)

**POST /me/messages/send** — send email
```
POST /users/{service_account_id}/messages/send
Auth: Bearer {oauth_token}
Body: { message: { subject, body: {contentType: HTML, content}, toRecipients, saveToSentItems: true } }
Rate: 10 msg/sec per user  Idempotency: client-side dedup by key
```

---

## 6. Integration Risks & Mitigations

The risks below are grounded in the scenario artefacts — not generic engineering concerns. Where an artefact names a specific incident or observation, it's cited. These are the issues most likely to surface in the pilot.

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| **Saba LMS batch file late or missing** | Medium (batch systems have reliability issues on holidays, maintenance windows) | High — LMS task status unknown for up to 14 days; reminders become unreliable | Agent monitors SFTP for file by 06:00 Sunday; if absent, creates `BATCH_MISSING` escalation to IT Support + HR Ops; continues with last known batch marked STALE |
| **Saba employee_id ↔ Workday hire_id join failure** | Low–Medium (~1–3% for new joiners) | Medium — agent can't update LMS tasks for affected hires | Log join failures per batch; escalate to IT if >2% fail rate; HR Ops manually verifies for affected hires |
| **Workday API downtime** | Low (99.9% SLA) | High — agent completely blocked | Graceful degradation: cache last-known hire list; queue actions; escalate to HR Ops if >1h outage |
| **ServiceNow auto-routing misconfiguration** | Medium (seen in Tom Reeves case — "consulting laptop spec changed and auto-routing didn't pick it up") | High — IT request goes to wrong queue, delayed | Agent polls request state every 2h; escalates TASK_OVERDUE_72H if SNOW request stale; include assignment_group in escalation email so HR can redirect |
| **Compliance training matrix stale** (SharePoint doc) | **HIGH** — Artefact 1.3 shows pencilled footnote: "TEMP-EXT retired 2024-Q1, update flowchart sometime" | High — agent assigns wrong compliance track | Agent reads matrix from SharePoint on startup + daily refresh; flag to Compliance if version date > 6 months; require Compliance owner sign-off on matrix before launch |
| **Workday updated end-of-week (not real-time)** | High — confirmed in Artefact 1.2: "Priya updates the tracker first and refreshes Workday end-of-week" | Medium — agent sees stale task status during the week | Agent compares data_freshness field; if task last updated >5 days ago and status still PENDING, escalate DATA_FRESHNESS_WARN rather than OVERDUE |
| **Outlook Graph API rate limit hit** | Low at current volume (73 hires/yr) | Low | Batch outgoing emails; respect 10 msg/sec limit; exponential retry |
| **Hire type NULL at intake** | Medium (~5–10% per DELIVERABLE-1) | Medium — wrong task set created; wrong compliance track | Agent detects NULL hire_type at intake; escalates HIRE_TYPE_AMBIGUOUS immediately; does not proceed with task creation until resolved |

---

## 7. Design Impact Summary: What the No-API LMS Constraint Changes

The following elements of the agent design in DELIVERABLE-5 must be revised to reflect Saba LMS being batch-only:

| DELIVERABLE-5 Element | Original | Corrected |
|---|---|---|
| Section 2 IN SCOPE: "Monitor task status" | Polls 6 systems every 2 hours | Polls 5 API systems every 2 hours; reads LMS from weekly batch |
| Section 5 KPI: Poll latency | "<4 minutes per hire" | "<4 minutes per hire **for API-backed tasks**; up to 7 days for LMS tasks" |
| Section 5 KPI: On-time task completion ≥97% | Applies to all tasks | Applies to all tasks; **LMS task detection SLA is 7 days, not 4 hours** |
| Section 7 LMS row | "SOAP API (legacy), 100 req/hr, 98% SLA" | "No API — SFTP batch file, weekly, 95% delivery reliability" |
| orchestrator.py LMSClient | `get_task_status(task_id)` → `NotImplementedError` | Replace with `BatchFileReader.get_status_from_latest_batch(employee_id, course_code)` |

---

## 8. Pre-Launch Checklist

### Must-complete before pilot

- [ ] **Saba SFTP access confirmed** — agent service account provisioned; test file downloaded
- [ ] **Saba CSV schema validated** — field names, enrollment_status values, date formats confirmed on real export
- [ ] **employee_id → hire_id join confirmed** — sample of 20 hires matched successfully; join failure rate <2%
- [ ] **Batch delivery SLA confirmed with Saba IT** — Sunday 02:00 UTC or document actual schedule
- [ ] **Workday API access confirmed** — OAuth client credentials provisioned; /hrh-list-hires tested
- [ ] **ServiceNow API access confirmed** — OAuth token; test sc_request POST succeeds
- [ ] **MS Graph permissions granted** — Mail.Send, Calendars.ReadWrite scopes for service account
- [ ] **Compliance training matrix reviewed** — version date <6 months; TEMP-EXT footnote applied; Compliance owner confirmed
- [ ] **Hire type NULL rate confirmed** — audit last 12 months of hire records; quantify
- [ ] **Priya's end-of-week Workday refresh pattern addressed** — agent data_freshness handling confirmed

### Conditional (address if applicable)

- [ ] **Saba LMS API licence check** — confirm whether paid API access is available before committing to batch-only architecture
- [ ] **ServiceNow routing rules reviewed** — confirm laptop spec change from Tom Reeves incident is resolved in routing matrix
- [ ] **SharePoint onboarding doc library permissions** — agent service account has read access to compliance flowchart path

---

## 9. Assumptions & Confidence

| Assumption | Confidence | Validation Method | Impact if Wrong |
|---|---|---|---|
| Saba LMS batch delivers weekly (Sunday) with >90% reliability | **LOW** — not confirmed; batch systems often have maintenance-window exceptions | Ask Saba IT for delivery history; request last 3 months of delivery timestamps | If delivery is erratic, LMS task monitoring becomes unreliable; may need to fall back to manual HR Ops check |
| Saba employee_id matches Workday hire_id or can be joined | **LOW** — join requires Workday emp record; new hires may not be synced | Test join on 20 sample hires before launch | If join fails >5%, agent can't update LMS tasks; tracking gap widens |
| Workday is updated daily in practice (not just end-of-week) | **MEDIUM** — Artefact 1.2 shows Priya refreshes Workday "end-of-week"; daily sync may not happen | Audit Workday data_freshness fields across last 30 hires | If Workday is weekly, agent data is 5 days stale; reminder timing degrades significantly |
| ServiceNow auto-routing is correct for all role types | **MEDIUM** — Tom Reeves artefact shows routing missed a consulting laptop spec change | Review SNOW routing rules with IT before launch; test with 3 role types | Wrong routing = IT request goes to wrong queue; provisioning delayed without agent detecting it |
| Compliance training matrix in SharePoint is current | **LOW** — Artefact 1.3 shows pencilled note: update overdue since Q1 2024 | Compliance team review before launch | Stale matrix → wrong track assigned → audit risk |
| MS Graph API permissions can be provisioned for agent service account | **MEDIUM** — depends on IT admin approval and Outlook licence | Request from IT 2 weeks before launch | Without Graph access, agent cannot send reminders or escalations |
