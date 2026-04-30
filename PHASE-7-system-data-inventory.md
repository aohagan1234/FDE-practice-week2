# Phase 7: System/Data Inventory — Map Integration Requirements

**Goal:** Document all systems the agent touches, data flows, API requirements, and integration assumptions.

**Input:** Agent Purpose Document + System/Data Requirements section.

---

## Why This Matters

A detailed System/Data Inventory:
- Clarifies what the IT/platform team must configure before agent launch
- Exposes data quality risks (incomplete fields, stale data, missing integrations)
- Identifies single points of failure (if one API fails, what's the fallback?)
- Supports cost estimation (how many API calls? Token cost of retrieval?)
- Enables testing and rollout planning

---

## System Inventory: Systems The Agent Touches

For each system, document:

### Template

| System | API Type | Endpoints Used | Auth | Rate Limit | SLA | Fallback |
|---|---|---|---|---|---|---|
| [Name] | [REST/GraphQL/Direct DB/SDK] | [List endpoints] | [OAuth/API Key/Service Account] | [Calls/sec or calls/day] | [99.9% / 99% / Custom] | [If system down, what does agent do?] |

### Example: Workday

| System | API Type | Endpoints Used | Auth | Rate Limit | SLA | Fallback |
|---|---|---|---|---|---|---|
| **Workday** | REST API | `/hrh-get-hire`, `/hrh-list-hires`, `/emp-search`, `/emp-update-custom-field`, `/emp-get-leave-calendar` | OAuth 2.0 (client credentials) | 100 calls/sec | 99.9% (contractual) | If Workday down: agent stops; queue escalations; notify Priya manually by email |

### Example: Outlook/Microsoft Graph

| System | API Type | Endpoints Used | Auth | Rate Limit | SLA | Fallback |
|---|---|---|---|---|---|---|
| **Outlook (Microsoft Graph)** | REST API | `/me/messages/send`, `/me/calendar/events`, `/me/mailFolders` | OAuth 2.0 (delegated) | 10,000 req/min | 99.9% (SLA not contractual) | If Graph API down: queue emails; retry with exponential backoff; if 24h+ failure, escalate to IT |

### Example: Internal HR Database

| System | API Type | Endpoints Used | Auth | Rate Limit | SLA | Fallback |
|---|---|---|---|---|---|---|
| **HR Audit Log (Internal DB)** | Direct DB query + ORM | `INSERT INTO buddy_audit_log`, `SELECT buddy_assignments WHERE period = X` | Service account + IP whitelist | No limit (internal) | 99.5% (non-critical) | If DB down: log to local queue; replay once DB recovers |

---

## Data Flow Diagram

Create a simple flow showing how data moves through the agent:

```
1. INTAKE
   Workday (new hire event) 
   → Agent trigger (event subscription or daily batch)

2. QUERY & VALIDATE
   Workday API: /hrh-get-hire (fetch hire record)
   → Agent validates: start date < 2 weeks? status = "onboarding"?

3. SEARCH
   Workday API: /emp-search (find eligible employees in dept)
   → Workday API: /emp-get-leave-calendar (check availability for each)
   → HR Audit DB: SELECT buddy_assignments WHERE employee_id = X (count current buddies)

4. SCORE & RANK
   [Local computation; no system calls]
   → Sort by score; pick top 3

5. SURFACE
   Microsoft Graph API: /me/messages/send (email Priya)
   → Outlook: Create email with top 3 candidates + reasoning

6. RECEIVE DECISION
   [Human: Priya clicks "Assign" link or replies to email]
   → Webhook or polling: Agent receives decision

7. EXECUTE
   Workday API: /emp-update-custom-field (write buddy assignment)
   → Microsoft Graph: Send confirmation email to candidate
   → Microsoft Graph: Create calendar reminder for 30-day check-in

8. LOG
   HR Audit DB: INSERT INTO buddy_audit_log (decision, score, reasoning, timestamp)
```

---

## Data Dictionary: Entities & Fields

For each major entity the agent reads or writes, document:

### New Hire Record (Workday)

| Field | Type | Source | Required? | Quality Notes | Agent Use |
|---|---|---|---|---|---|
| `hire_id` | UUID | Workday auto-generate | Yes (PK) | Unique; immutable | Read: lookup hire |
| `hire_name` | String | Hiring manager input | Yes | 98% complete; ~2% missing names | Read: display to Priya |
| `start_date` | Date | Hiring manager input | Yes | 99% populated; ~1% data-entry errors (future date when should be today) | Read: check if hire eligible (start < 2 weeks away) |
| `department` | String (Enum) | Hiring manager selects from dropdown | Yes | 99.5% valid; ~0.5% misclassified | Read: determine eligible buddy departments |
| `hiring_manager_id` | UUID | Org chart auto-populate | Yes | 99% accurate; ~1% stale when manager changes | Read: reference; not used in buddy matching |
| `role` | String | HR + hiring manager | Yes | 98% populated; ambiguous for dual roles | Read: inferred (not used directly) |
| `status` | String (Enum: pending, onboarding, active, offer_declined, on_hold) | HR workflow | Yes | 99.9% accurate | Read: filter to "onboarding" only |
| `created_at` | Timestamp | Workday | Yes (audit) | Accurate | Read: timestamp for audit |

### Employee Record (Workday)

| Field | Type | Source | Required? | Quality Notes | Agent Use |
|---|---|---|---|---|---|
| `emp_id` | UUID | Workday | Yes (PK) | Unique; immutable | Read: identify candidate |
| `emp_name` | String | HR on hire | Yes | 99% complete | Read: display to Priya |
| `department` | String (Enum) | Org chart or HR input | Yes | 99% accurate; can drift with transfers | Read: filter by department |
| `tenure_in_role_months` | Int | Derived from start_date + role history | No (null for new roles) | 95% accurate; manual override possible | Read: filter candidates with > 6 months tenure |
| `emp_status` | String (Enum: FTE, Contractor, Secondment, Rehire) | HR | Yes | 98% accurate | Read: filter to include contractors + FTEs; exclude secondments |
| `leave_calendar_id` | UUID (FK to Workday leave calendar) | Workday integration | Yes | 99% valid link | Read: join to check availability |
| `buddy_assignment_current` | JSON array of {hire_id, match_date, status} | Custom Workday field maintained by agent | No | 90% complete (maintenance lag); up to 1 week behind | Read: count current assignments; exclude employees with ≥ 3 |

### Leave Record (Workday)

| Field | Type | Source | Required? | Quality Notes | Agent Use |
|---|---|---|---|---|---|
| `leave_id` | UUID | Workday | Yes (PK) | Unique | Read: lookup |
| `emp_id` | UUID (FK) | Workday | Yes | Accurate | Read: filter by employee |
| `leave_start` | Date | Employee input | Yes | 98% populated; ~2% incomplete (employees haven't submitted) | Read: check if employee away during onboarding |
| `leave_end` | Date | Employee input | Yes | 98% populated; same as above | Read: check availability window |
| `leave_type` | String (Enum: PTO, Sick, Sabbatical, Unpaid) | Employee or HR | Yes | 99% valid | Read: filter to PTO + Sabbatical (skip Sick, Unpaid) |
| `status` | String (Enum: Pending, Approved, Rejected, Cancelled) | Manager approval | Yes | 98% accurate; ~2% pending approval | Read: only count Approved leaves |

### Buddy Assignment Record (Agent-written, Workday custom field)

| Field | Type | Target System | Format | Notes |
|---|---|---|---|---|
| `hire_id` | UUID | Workday custom field | String | References hire record |
| `buddy_emp_id` | UUID | Workday custom field | String | References employee record |
| `match_date` | Date | Workday custom field | ISO 8601 | Date agent made assignment |
| `agent_score` | Float | Workday custom field | Decimal (0.0–1.0) | Ranking score for audit |
| `agent_reasoning` | String | Workday custom field or HR audit DB | Text (max 500 chars) | Why this candidate was chosen |
| `assigned_by` | String | Workday audit field | "ai-agent" | Who made the assignment (for audit trail) |

---

## API Endpoint Reference

For each system, list all endpoints the agent calls:

### Workday APIs

**Endpoint 1: Get Hire Record**
```
GET /hrh-get-hire?hire_id={hire_id}

Request:
  Authorization: Bearer {oauth_token}
  Accept: application/json

Response:
  {
    "hire_id": "uuid-1234",
    "hire_name": "John Smith",
    "start_date": "2025-05-15",
    "department": "Consulting",
    "status": "onboarding",
    "created_at": "2025-05-01T09:00:00Z"
  }

Rate limit: 100 calls/sec
Timeout: 5 seconds
Retry: Exponential backoff, max 3 attempts
```

**Endpoint 2: List Hires (Daily Batch)**
```
GET /hrh-list-hires?status=onboarding&start_date_after={date_minus_2_weeks}

Request:
  Authorization: Bearer {oauth_token}
  Accept: application/json

Response:
  {
    "hires": [
      { "hire_id": "uuid-1234", "hire_name": "...", ... },
      { "hire_id": "uuid-5678", "hire_name": "...", ... }
    ],
    "count": 5,
    "next_page": "token-xyz"
  }

Rate limit: 10 calls/sec
Timeout: 10 seconds
Pagination: Cursor-based; fetch all pages
```

**Endpoint 3: Search Employees**
```
GET /emp-search?department={dept}&status=active&tenure_months_min=6

Request:
  Authorization: Bearer {oauth_token}
  Accept: application/json

Response:
  {
    "employees": [
      {
        "emp_id": "uuid-abc",
        "emp_name": "Alice Johnson",
        "department": "Consulting",
        "tenure_in_role_months": 18,
        "emp_status": "FTE",
        "leave_calendar_id": "cal-xyz"
      },
      ...
    ],
    "count": 42
  }

Rate limit: 100 calls/sec
Timeout: 5 seconds
```

**Endpoint 4: Get Leave Calendar**
```
GET /emp-get-leave-calendar?emp_id={emp_id}&period={start_date}~{end_date}

Request:
  Authorization: Bearer {oauth_token}
  Accept: application/json

Response:
  {
    "leave_records": [
      {
        "leave_id": "leave-123",
        "leave_start": "2025-05-20",
        "leave_end": "2025-05-27",
        "leave_type": "PTO",
        "status": "Approved"
      }
    ],
    "available": true  // convenience field: true if employee is available for the period
  }

Rate limit: 100 calls/sec
Timeout: 5 seconds
Note: "available" is true if no Approved/Sabbatical leaves overlap the period
```

**Endpoint 5: Update Custom Field (Write Buddy Assignment)**
```
PUT /emp-update-custom-field?emp_id={emp_id}&field_name=buddy_assignment_current&operation=append

Request:
  Authorization: Bearer {oauth_token}
  Content-Type: application/json

  {
    "hire_id": "uuid-1234",
    "buddy_emp_id": "uuid-abc",
    "match_date": "2025-05-15",
    "agent_score": 0.87,
    "agent_reasoning": "High team diversity match; available; 18 months tenure.",
    "assigned_by": "ai-agent"
  }

Response:
  {
    "status": "success",
    "emp_id": "uuid-abc",
    "field_updated": true,
    "timestamp": "2025-05-15T09:15:00Z"
  }

Rate limit: 50 calls/sec
Timeout: 5 seconds
Retry: Idempotency key required (hash of hire_id + emp_id + match_date) to prevent duplicates
Critical: This write is irreversible; implement rollback logic if subsequent write fails
```

### Microsoft Graph (Outlook) APIs

**Endpoint 1: Send Email**
```
POST /me/messages/send
Or for service account: POST /users/{user_id}/messages/send

Request:
  Authorization: Bearer {oauth_token}
  Content-Type: application/json

  {
    "message": {
      "subject": "Buddy matching: 3 candidates for [hire name]",
      "body": {
        "contentType": "HTML",
        "content": "<h3>Top 3 buddy candidates for John Smith...</h3>..."
      },
      "toRecipients": [
        { "emailAddress": { "address": "priya.aggarwal@aldridgesykes.com" } }
      ]
    },
    "saveToSentItems": true
  }

Response:
  {
    "id": "msg-xyz"
  }

Rate limit: 10 messages/sec per user
Timeout: 5 seconds
Idempotency: Implement client-side deduplication (track sent message IDs; don't resend same message twice)
```

**Endpoint 2: Create Calendar Event (Reminder)**
```
POST /me/calendar/events
Or: POST /users/{user_id}/calendar/events

Request:
  Authorization: Bearer {oauth_token}
  Content-Type: application/json

  {
    "subject": "30-day buddy check-in: John Smith",
    "start": {
      "dateTime": "2025-06-15T10:00:00",
      "timeZone": "UTC"
    },
    "end": {
      "dateTime": "2025-06-15T10:30:00",
      "timeZone": "UTC"
    },
    "attendees": [
      { "emailAddress": { "address": "priya.aggarwal@aldridgesykes.com" }, "type": "required" },
      { "emailAddress": { "address": "{buddy_email}", "type": "optional" }
    ]
  }

Response:
  {
    "id": "event-abc"
  }

Rate limit: 10 events/sec per user
Timeout: 5 seconds
```

---

## Integration Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| **Workday API downtime** | Low (99.9% SLA) | High (agent completely blocked) | Implement graceful degradation: queue work, retry with backoff, escalate to Priya if unresolved after 1 hour |
| **Stale leave calendar** | Medium (employees don't submit PTO) | Medium (agent surfaces employees on upcoming leave) | Audit leave data quality; if < 85% complete, add warning note to email to Priya: "Note: leave calendar may be incomplete" |
| **Org chart out of sync** | Medium (hiring manager changes, delays propagate) | Medium (agent can't find correct department) | Implement manual refresh trigger for HR; add SLA requirement to IT (org chart refreshed within 24h of change) |
| **Duplicate buddy assignments** | Low (if idempotency implemented correctly) | High (buddy overloaded; confusion) | Implement pessimistic locking in Workday write; query employee's current count immediately before and after write |
| **Email delivery failure** | Low (Graph API 99.9% SLA) | Medium (Priya doesn't get notification; hire delayed) | Implement retry with exponential backoff; if fails after 24h, escalate to IT + send SMS to Priya |
| **Scoring formula produces unintuitive results** | Medium (formula not validated) | Medium (Priya rejects agent's candidates; erodes trust) | Implement monthly audit of rejected candidates; flag if rejection rate > 20%; trigger formula review |

---

## Cost Estimation

Based on API calls, estimate monthly cost:

### Token Cost
```
Scenario: 250 buddy assignments per month

Per assignment:
  - /hrh-get-hire: ~500 input tokens + 300 output = 800 tokens
  - /emp-search: ~200 input tokens + 2,000 output (42 employees × 50 tokens each) = 2,200 tokens
  - /emp-get-leave-calendar: ~5 calls × (300 input + 500 output) = 4,000 tokens
  - Email generation: ~200 input + 1,000 output = 1,200 tokens
  - Total per assignment: ~8,200 tokens

Model: GPT-4 (assume)
  - Input: $0.001 / 1K tokens
  - Output: $0.003 / 1K tokens
  - Weighted average: ~$0.002 / token

Cost per assignment: 8,200 × $0.002 = $16.40
Monthly cost (250 assignments): 250 × $16.40 = $4,100
Annual: ~$49,200

Optimization opportunity: Implement prompt caching (repeat /emp-search queries can be cached)
Estimated savings: 30-40% reduction in input tokens
Revised annual: ~$30,000
```

### Tool Call Cost
```
Per assignment:
  - Workday API: 5 calls × $0.10 per call = $0.50
  - Graph API: 2 calls × $0.05 per call = $0.10
  - Total per assignment: $0.60

Monthly (250 assignments): 250 × $0.60 = $150
Annual: ~$1,800
```

### Infrastructure Cost
```
Assume AWS Lambda hosting:
  - 250 invocations/month × 10 seconds average duration × 512 MB memory
  - Lambda free tier: 1M invocations/month, 400k GB-seconds
  - Usage: 250 × 10 = 2,500 GB-seconds/month
  - Cost: Within free tier; negligible
  - Estimate: $0 (or $50/month for sustained growth to 5K assignments/month)

Database (audit log):
  - ~250 records/month × 500 bytes per record = 125 KB/month
  - Query volume: minimal
  - Estimate: $10/month (within free tier of most DBs)
```

### Total Monthly Cost
```
Tokens: $342 (monthly, $4,100 annual)
Tool calls: $150 (monthly, $1,800 annual)
Infrastructure: $50 (monthly, $600 annual)
HITL review (Priya's time): 250 × 5 min = 1,250 min ≈ 21 hours @ £75/hr = £1,575/month
Total: ~$2,117/month or ~$25,000 annual

Baseline (manual buddy matching): 250 × 0.5 hr × £75 = £9,375/month
Savings: ~£7,258/month or ~£87,000 annual
ROI: 3.4:1
```

---

## Pre-Launch Checklist

Before the agent goes live:

- [ ] All API endpoints tested and documented
- [ ] Rate limits confirmed with vendors
- [ ] Authentication (OAuth, API keys) configured and tested
- [ ] Data quality audit completed (leave calendar %, org chart recency, etc.)
- [ ] Fallback / rollback procedures documented
- [ ] Monitoring alerts configured (API failures, escalation rates, SLA breaches)
- [ ] Manual audit process established (weekly review of agent decisions)
- [ ] Pilot group identified (start with Priya only; measure actual time saved + satisfaction)
- [ ] Success metrics baseline established (time per match, adoption rate, quality scores)

---

## System/Data Inventory Output

Compile all sections into a single document for your implementation team:

```markdown
# System/Data Inventory: [Agent Name]

## System Inventory
[Table: System | API Type | Endpoints | Auth | Rate Limits | SLA | Fallback]

## Data Flow Diagram
[Flowchart showing all systems and data movement]

## Data Dictionary
[For each entity: fields, types, sources, quality notes, agent usage]

## API Endpoint Reference
[Complete endpoint documentation for each system]

## Integration Risks & Mitigations
[Risk table with probability, impact, mitigation]

## Cost Estimation
[Token cost + tool call cost + infrastructure]

## Pre-Launch Checklist
[Verification items]

## Implementation Notes
[Any special considerations for IT team]
```

---

## Refinement Prompts: Commands Used to Improve This Deliverable

DELIVERABLE-6 was created after the build loop revealed a critical error in DELIVERABLE-5: Saba LMS was described as having a SOAP API when the scenario brief explicitly states it has no API at all. The following prompts were used to identify the error, create the inventory document, and improve its readability.

---

### Prompt 1: Cross-check system descriptions against the scenario brief

```
Review all systems listed in the Agent Purpose Document's System & Data Requirements section.
For each system:
1. Check the scenario brief (enriched_scenarios.md) for any description of that system
2. If the scenario brief describes the integration method, does the spec match it?
3. Flag any system where the spec claims an API exists but the brief says otherwise

Pay particular attention to legacy or third-party systems — these are most likely to have
incorrect integration assumptions.
```

**What this found:** DELIVERABLE-5 Section 7 described Saba LMS as "SOAP API (legacy)." The enriched scenario (Week2_Docs/enriched_scenarios.md) explicitly states Saba LMS has **no API** — it exports via weekly SFTP batch file only. This changes detection latency from 2 hours to 7 days for all LMS-sourced tasks, invalidates the 4-hour SLA claim, and requires the LMSClient to be an SFTP file reader, not an HTTP client.

---

### Prompt 2: Create the system inventory document

```
Create a System/Data Inventory document (DELIVERABLE-6) for the [agent name].
For each system the agent touches, document:
- Integration method (REST API / SFTP / webhook / no access)
- Authentication method
- Data freshness (real-time / daily batch / weekly batch)
- Known data quality issues
- What the agent reads and writes
- Fallback if the system is unavailable

Add a dedicated section for any system where the integration method is significantly
different from what a developer would assume (e.g., batch-only when API was expected).
For that system, document: what changes in the agent design, what SLA claims are affected,
and how the agent should handle the batch window.
```

---

### Prompt 3: Improve the data flow diagram

```
Make sure all tables are formatted properly and are easy to read.
Make sure any diagrams are easily understood.

Specifically: replace the plain text data flow (numbered list with arrows using hyphens)
with a Unicode box diagram using ┌──┐ │ └──┘ and ▼ characters.
Each stage should be a distinct box with a label, the systems involved, and the
direction of data flow shown by ▼ connectors between stages.
```

**What this fixed:** The plain-text data flow was a numbered list with `→` arrows that couldn't visually convey stages or parallel operations. The Unicode box diagram makes stages visually distinct and the data flow direction unambiguous.

---

### Prompt 4: Add a three-state handling model for batch-sourced data

```
For any system that uses batch-only integration (not real-time API), add a section
explaining how the agent handles the three states that exist between batch runs:

State 1: Task completed — batch not yet delivered (agent sees task as outstanding)
State 2: Task outstanding — batch not yet delivered (agent correctly sees it as outstanding)  
State 3: Task completed — batch delivered (agent updates status correctly)

For State 1, specify: does the agent send a false reminder? How does it recover
when the batch arrives? Does it log a correction?

This prevents the agent from sending incorrect escalations during the batch window.
```

**What this fixed:** DELIVERABLE-6 Section 5 now includes a three-state model for Saba LMS specifically, with explicit rules for each state and a note that the "completed but not yet delivered" case is the most dangerous (agent sends a reminder for work already done).

---

### The key lesson from this phase

The Phase 7 inventory is most valuable when it reveals a **spec error** in Phase 5, not just when it confirms what you already assumed. The discipline of checking every system claim against primary sources (the scenario brief, not your own earlier document) is what makes the inventory worth doing.

If your inventory only confirms what you wrote in Phase 5, you probably haven't checked carefully enough.

---

## Next Step

Once your System/Data Inventory is complete, you're ready to:
- **Submit for peer review** (if applicable)
- **Prepare for Gate 2 timed exercise** (use these phases as your methodology template)
- **Begin implementation** (hand all artefacts to your development team)
