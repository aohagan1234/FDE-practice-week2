# Deliverable: Build Loop — Spec Stress-Test, Gap Analysis & Implementation

**Phase:** 6 of 7  
**Agent:** Coordination Orchestrator (HR Onboarding — Aldridge & Sykes)  
**Input:** DELIVERABLE-5-AGENT-PURPOSE.md  
**Output:** Revised spec + working Python implementation + 37 passing tests

---

## What the Build Loop Is For

The build loop is not a coding exercise. It is a design stress-test.

The prompt given to Claude was not "build this agent." It was:

> Read the Agent Purpose Document. Tell me what you can build confidently, what you need clarified, and what you'd have to guess. Then build the confident parts. Leave commented TODOs for everything else.

The gaps Claude cannot fill without asking are the same gaps that would cause a real implementation to fail silently or produce incorrect behaviour. Finding them before writing a line of production code is the entire point.

---

## The Build Prompt

```
I am developing a Coordination Orchestrator for HR onboarding at Aldridge & Sykes.
Read the Agent Purpose Document carefully, then answer:

1. What can you build confidently from this document?
   List components you understand well enough to code without asking questions.
   Include specific sections (e.g. "Activity Catalog step 1–5").

2. What do you need me to clarify before building the rest?
   For each gap, explain why it's ambiguous.
   If it's a delegation boundary: ask explicitly — should the agent decide this,
   or should it escalate to the human?

3. Build the parts you're confident about.
   Show code for the components you can implement.
   Leave commented TODOs for the gaps you identified in question 2.

Focus on:
- Are escalation triggers clear enough to code as if/else conditions?
- Can you access all data sources and perform all listed actions?
- Are there polling intervals or SLA claims the system design can't meet?
- Would any activity produce duplicate side effects if it ran twice in one cycle?
```

---

## What Was Identified as Buildable

The following activities were clear enough to implement without further questions:

| Activity | Status | Why Buildable |
|---|---|---|
| 1. Poll task status across 6 systems | Built | Source systems listed; retry pattern specified |
| 2. Calculate deadlines from start date + offset | Built | Rule is deterministic: start_date + offset_days |
| 3. Detect overdue tasks (24h grace period) | Built | Clear threshold; terminal states defined |
| 4. Send reminders (rate-limited, idempotent) | Built | 24h rate limit specified; owner fallback chain given |
| 5. Monitor I-9 compliance (Day 2 / Day 3) | Built (revised) | Escalation days specified; idempotency added |
| 6. Auto-submit IT provisioning by role | Built | IT access matrix available in config |
| 7. Manager handoff notification | Built | Trigger conditions specified (all done OR Day -2) |
| 8. Escalation routing by type | Built | ESCALATION_ROUTING table in config |
| 9. Audit logging | Built | Delegated to AuditLogger; structured log format specified |

---

## Gaps Found: 6 Design Problems Caught Before Production

### Gap 1 — I-9 Polling Interval Too Slow for Stated SLA

**What the spec said:**  
Activity 5 described I-9 monitoring as a "daily" check.

**Why this fails:**  
DELIVERABLE-5 Section 5 stated: "≥80% of overdue tasks detected within 4 hours."  
A daily poll has a maximum detection window of 24 hours — the 4-hour SLA was impossible to meet.

**The specific risk:**  
If a hire's I-9 deadline falls at 9am and the daily poll runs at 8am, the violation goes undetected for 23 hours. Federal I-9 penalty exposure begins Day 3. A 23-hour detection gap on Day 2 means the agent may miss the warning window entirely.

**Fix applied:**  
Polling frequency changed to **every 2 hours** in both the spec and the implementation.

```python
# orchestrator.py — Activity 5 comment
"""Mandatory I-9 escalation on Day 2 (AT_RISK) and Day 3+ (VIOLATION).

Runs on the 2-hour polling cycle — NOT daily.  A daily cycle risks
missing the 15-minute SLA if the poll window misses the hire's start hour.
"""
```

**Spec section revised:** DELIVERABLE-5 Section 4 (Activity Catalog), Section 5 (KPIs).

---

### Gap 2 — No Idempotency Rule for Escalations

**What the spec said:**  
"Create escalation when [condition]." No rule about what happens when the same condition persists across multiple poll cycles.

**Why this fails:**  
With a 2-hour poll cycle and a hire whose I-9 is still incomplete on Day 3, the agent would run `monitor_i9_compliance` 12 times per day — and create 12 identical I9_VIOLATION escalations. Priya's inbox would receive 12 "CRITICAL — FEDERAL VIOLATION" emails for the same hire, every day, until resolved. Alert fatigue would cause the alerts to be ignored.

**Fix applied:**  
`_escalation_exists(hire_id, esc_type)` guard added. An escalation of a given type is only created once per hire, while it remains OPEN.

```python
# orchestrator.py
def _escalation_exists(self, hire_id: str, esc_type: EscalationType) -> bool:
    """Idempotency guard: returns True if an open escalation of this type
    already exists for this hire, preventing alert flooding across poll cycles."""
    return any(
        e.hire_id == hire_id
        and e.escalation_type == esc_type
        and e.status == EscalationStatus.OPEN
        for e in self._escalations
    )
```

The same guard is applied to: reminder emails, IT provisioning submissions, manager handoff notifications.

**Spec section revised:** DELIVERABLE-5 Section 6 (Failure Modes), Section 8 (Escalation Workflows).

---

### Gap 3 — Saba LMS Described as Having an API (It Doesn't)

**What the spec said:**  
DELIVERABLE-5 Section 7 listed Saba LMS as: *"SOAP API (legacy) — wraps SOAP response into TaskStatus enum."*

**Why this fails:**  
The enriched scenario (Week2_Docs/enriched_scenarios.md) explicitly states Saba LMS has **no API**. It exports data via a weekly SFTP batch file only, delivered every Sunday night.

This changes four things:

| Claim in DELIVERABLE-5 | What is actually true |
|---|---|
| LMS task status detected within 4 hours | Detection window is up to 7 days (next batch delivery) |
| LMSClient is an HTTP client | LMSClient must be an SFTP file reader |
| Reminders can be sent when LMS task becomes overdue | Agent cannot know task is complete until next batch arrives |
| "≥80% of tasks detected within 4 hours" SLA | Impossible for LMS-sourced tasks |

**Fix applied:**  
- DELIVERABLE-6 (System/Data Inventory) created specifically to document this.  
- LMSClient stub in `api_clients.py` retains `NotImplementedError` — but the comment now signals the correct implementation path.
- The SLA claim in DELIVERABLE-5 was revised to acknowledge the LMS batch window exception.

**Note on api_clients.py:** The current `LMSClient` docstring still reads "SOAP (legacy)" — this is technically incorrect and must be replaced before any production implementation. See DELIVERABLE-6 Section 5 for the correct integration specification.

```python
# api_clients.py — LMSClient (stub — NOT an HTTP client in production)
class LMSClient(BaseAPIClient):
    """Fetch compliance training enrollment status.
    
    NOTE: Saba LMS has no API. Production implementation must read the
    weekly SFTP batch file (delivered Sunday ~23:00 UTC), not make HTTP calls.
    Detection latency for LMS tasks: up to 7 days, not 2 hours.
    See DELIVERABLE-6 Section 5 for the three-state handling model.
    """
    def get_task_status(self, task_id: str) -> TaskStatus:
        raise NotImplementedError
```

**Spec section revised:** DELIVERABLE-5 Section 7 (System & Data Requirements). New document: DELIVERABLE-6.

---

### Gap 4 — Hold Decision Write Path Not Guarded

**What the spec said:**  
The autonomy matrix listed hold-trigger detection as "Agent-Led + Human Oversight" but did not explicitly state that the agent must never write `hire.status = ON_HOLD`.

**Why this fails:**  
If the implementation is generated without this explicit constraint, a developer reading the spec might reasonably implement the agent writing the hold status (since it already has Workday write access for other fields). A hold is an irreversible employment action with legal implications.

**Fix applied:**  
Guardrail #1 added to DELIVERABLE-5 explicitly: *"The agent detects hold triggers and escalates. It does not write hire.status = ON_HOLD under any condition."* The orchestrator implementation has no hold-write code path.

**Spec section revised:** DELIVERABLE-5 Section 2 (Scope — Out of Scope), Section 3 (Autonomy Matrix).

---

### Gap 5 — ServiceNow Routing Rules Not Verified

**What the spec said:**  
Activity 6 submits IT provisioning requests to ServiceNow using the IT access matrix in `config.py`. The routing rules in that matrix were written based on the scenario brief.

**Why this is a gap:**  
The IT access matrix maps roles to access package IDs and ServiceNow queue names. If the actual ServiceNow routing rules differ from what's in the matrix — for example, if the "Strategy" team routes to a different IT queue than "Consulting" — the agent will submit requests to the wrong queue. The agent detects when a request goes overdue, but cannot detect that it was routed incorrectly.

**Current status:**  
Marked LOW confidence in DELIVERABLE-5 Section 9. Requires validation with Mark (IT Manager) before go-live. The role-not-mapped escalation (`EscalationType.ROLE_NOT_MAPPED`) fires when a role is absent from the matrix, but not when the routing is present-but-wrong.

**Required pre-launch action:**  
IT Manager to confirm all role-to-queue mappings in `coordination_orchestrator/config.py` before deployment.

---

### Gap 6 — Compliance Training Matrix May Be Stale

**What the spec said:**  
Activity 2 (Calculate Deadlines) uses a task type registry to determine which training modules apply to which hire types, and when they are due.

**Why this is a gap:**  
The enriched scenario (Artefact 1.3) shows a SharePoint compliance matrix with an outdated footnote. If the matrix used to build the task type registry is stale, the agent may assign the wrong training track to a hire — creating audit exposure for a task type that doesn't apply, or missing one that does.

**Current status:**  
Marked LOW confidence in DELIVERABLE-5 Section 9. Requires validation with Priya (HR Ops Lead) before go-live. The agent has no mechanism to detect that its own task registry is incorrect — this is a data governance risk, not a code risk.

---

## What Was Built

### File Structure

```
coordination_orchestrator/
├── models.py          — Hire, Task, TaskType, Escalation, enums (all data structures)
├── config.py          — Routing tables, IT access matrix, rate limit constants
├── api_clients.py     — Stubs for 5 source systems + functional EmailClient
├── audit.py           — Structured audit logger (writes to stdout / file)
├── orchestrator.py    — CoordinationOrchestrator: all 9 activities + poll cycle
├── main.py            — Entry point: wires clients into orchestrator, runs loop
└── tests/
    └── test_orchestrator.py — 37 tests across all 9 activities
```

### The Orchestrator: Key Design Decisions in Code

**Poll cycle runs every 2 hours (not daily):**
```python
# main.py
while True:
    orchestrator.run_cycle()
    time.sleep(POLL_INTERVAL_HOURS * 3600)  # POLL_INTERVAL_HOURS = 2
```

**Per-hire error isolation — one bad record doesn't block the batch:**
```python
# orchestrator.py — run_cycle()
for hire in active_hires:
    try:
        self._process_hire(hire, now, task_types)
    except Exception as exc:
        logger.error("Unhandled error processing hire %s: %s", hire.hire_id, exc)
```

**Idempotency enforced at three levels:**
- Reminders: `idempotency_key = f"reminder:{task_id}:{hire_id}:{date}"` — one per day
- Escalations: `_escalation_exists()` guard — one per hire per open condition
- IT requests: `hire_id in self._it_requests` — submitted exactly once per hire
- Handoffs: `hire_id in self._handoffs_sent` — sent exactly once per hire

**Role lookup is case-insensitive (prevents silent failures):**
```python
# orchestrator.py — auto_submit_it_provisioning()
role_key = hire.role.strip().lower()
package = IT_ACCESS_MATRIX.get(role_key)
```

---

## Test Coverage: 37 Tests, All Passing

Run with: `pytest tests/ -v` from the `coordination_orchestrator/` directory.

| Test Class | Tests | What It Verifies |
|---|---|---|
| `TestDeadlineCalculation` | 3 | Correct offset arithmetic; null offset escalates; inapplicable hire types skipped |
| `TestOverdueDetection` | 4 | 24h grace period boundary; terminal states (COMPLETE, SKIPPED) never flagged |
| `TestReminders` | 6 | First send fires; 24h suppression; resend after 24h; SYSTEM tasks skipped; manager email routing; email idempotency key prevents duplicates |
| `TestI9Compliance` | 7 | No escalation Day 1; AT_RISK on Day 2; VIOLATION on Day 3+; complete I-9 never escalates; idempotency across two poll cycles; non-ONBOARDING hires skipped |
| `TestITProvisioning` | 5 | Known role submits; unknown role escalates; case-insensitive lookup; no double-submit; 4xx API error escalates |
| `TestManagerHandoff` | 5 | Sends when all complete; sends at Day -2 with incomplete tasks; SKIPPED counts as terminal; holds when tasks incomplete before Day -2; idempotency prevents duplicate |
| `TestEscalationRouting` | 3 | Escalation stored and email dispatched; idempotency guard prevents duplicates; I9_VIOLATION uses CRITICAL severity |
| `TestPollTaskStatus` | 2 | HRIS failure creates SYSTEM_UNAVAILABLE escalation; successful poll returns tasks |
| `TestRunCycle` | 2 | Hire fetch failure is caught and logged (doesn't crash); ONBOARDING hires are processed |
| **Total** | **37** | |

---

## What Remains Stubbed (NotImplementedError)

These 9 methods in `api_clients.py` must be replaced with real implementations before deployment. Each is a `raise NotImplementedError` with the production endpoint documented in the docstring.

| Client | Methods to Implement | Notes |
|---|---|---|
| `HRISClient` | `get_active_hires`, `get_hire`, `get_tasks_for_hire`, `get_employee_email` | REST API, OAuth 2.0. Workday endpoints documented in DELIVERABLE-6. |
| `ITProvisioningClient` | `submit_request`, `get_request_status` | ServiceNow REST API. Routing rules must be validated with IT before implementing. |
| `LMSClient` | `get_task_status` | **Not an HTTP client.** Must be an SFTP file reader. See DELIVERABLE-6 Section 5. |
| `CalendarClient` | `get_task_status` | CalDAV. Used for onboarding event attendance tracking. |
| `FulfillmentClient` | `get_task_status` | REST API. Tracks welcome-pack and laptop shipment status. |

`EmailClient` is **fully implemented** and functional — idempotency, logging, and SMS fallback all work. In production, replace the body of `send()` with a Microsoft Graph API call.

---

## Spec Changes Made as a Result of the Build Loop

| Gap | DELIVERABLE-5 Section Changed | Change Made |
|---|---|---|
| I-9 polling interval | Section 4, Section 5 | Daily → every 2 hours; SLA claim revised |
| Missing idempotency | Section 6, Section 8 | Idempotency rule added to all escalation and notification activities |
| Saba LMS no API | Section 7 | Corrected integration method; SLA exception documented; DELIVERABLE-6 created |
| Hold write path | Section 2, Section 3 | Guardrail #1 added: agent never writes hold status |
| ServiceNow routing | Section 9 | Marked LOW confidence; pre-launch validation step added |
| Compliance matrix | Section 9 | Marked LOW confidence; pre-launch validation step added |

---

## Before This Goes Live

Three things must happen before the orchestrator is connected to production systems:

**1. Implement the 9 stubs in api_clients.py**  
Each method has the endpoint and auth method documented. Start with `HRISClient.get_active_hires()` — everything else depends on it.

**2. Validate the IT access matrix with Mark (IT Manager)**  
Open `coordination_orchestrator/config.py` and walk through every role-to-queue mapping. Incorrect routing will silently submit requests to the wrong ServiceNow queue.

**3. Replace LMSClient with an SFTP reader**  
This is not optional. Calling HTTP on a system with no API will fail immediately. The SFTP file format and delivery schedule are documented in DELIVERABLE-6 Section 5.
