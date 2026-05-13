# D4 — Capability Specification: Parallel Outreach
**MedFlex Engagement | Discovery: 2026-05-12**

---

**Capability name:** Parallel outreach

**What it does:** Contacts ranked nurse candidates simultaneously via existing channels and adapts outreach strategy in real time based on pool size, urgency, and concurrent fill cycle state.

---

## Inputs

| Field | Type | Source system | Required? |
|---|---|---|---|
| job_order_id | string | CRM | Yes |
| ranked_candidates | RankedCandidate[] | Candidate ranking output | Yes |
| shift_start_datetime | datetime | CRM (parsed job order) | Yes |
| urgency_hours | integer | Derived: hours until shift_start_datetime at outreach time | Yes |
| facility_type | string | CRM (parsed job order) | Yes |
| active_fill_cycles | FillCycle[] | Agent state (live concurrent fills) | Yes |
| max_concurrent_outreach | integer | Configuration (default: 3) | Yes |

Each `RankedCandidate` (from candidate ranking):

| Field | Type | Source system | Required? |
|---|---|---|---|
| nurse_id | string | CRM | Yes |
| rank | integer | Candidate ranking | Yes |
| rationale | string | Candidate ranking | Yes |
| in_active_outreach | boolean | Agent state | Yes |
| contact_details | ContactDetail[] | Nurse record | Yes |

Each `ContactDetail`:

| Field | Type | Source system | Required? |
|---|---|---|---|
| channel | enum: SMS, email, phone | Nurse record | Yes |
| address | string | Nurse record | Yes |
| preferred | boolean | Nurse record | Yes |

---

## Outputs

| Field | Type | Destination |
|---|---|---|
| job_order_id | string | Response tracking; CRM audit log |
| outreach_log | OutreachRecord[] | Response tracking; CRM audit log |
| confirmed_nurse_id | string | Coordinator approval interface |
| confirmation_timestamp | datetime | CRM audit log |
| escalation_type | enum: pool_exhausted, no_nurse_confirmed | Escalation handler |

Each `OutreachRecord`:

| Field | Type | Destination |
|---|---|---|
| nurse_id | string | CRM audit log |
| channel | enum: SMS, email, phone | CRM audit log |
| outreach_sent_at | datetime | CRM audit log |
| response_received_at | datetime | CRM audit log |
| response_status | enum: confirmed, declined, no_response | CRM audit log; response tracking |
| in_active_outreach | boolean | Agent state; candidate ranking (read by concurrent fill cycles) |

---

## Decision rules

1. On entry, filter `ranked_candidates` to exclude any candidate with `in_active_outreach` = `true`; if the filtered list is empty, trigger `pool_exhausted` escalation immediately without sending outreach.
2. Contact the top N candidates from the filtered ranked list simultaneously, where N = min(`max_concurrent_outreach`, count of available candidates after filtering).
3. For each contacted candidate, set `in_active_outreach` = `true` in agent state immediately upon sending outreach.
4. Contact each candidate via their `preferred` channel first. If no channel is flagged `preferred`, contact via SMS first. If the preferred channel fails, retry via the next available channel in the order: SMS, email, phone. If all three channels fail, log all channel failures in `outreach_log` and contact the next-ranked candidate.
5. If `urgency_hours` ≤ 4, set outreach response window to 20 minutes per candidate; if 4 < `urgency_hours` ≤ 24, set window to 60 minutes; if `urgency_hours` > 24, set window to 120 minutes. These windows and tier thresholds are configurable defaults — validate against pilot data from weeks 2–5 and adjust without architectural change.
6. If `urgency_hours` ≤ 4 and the available pool after filtering is ≤ 2, contact all available candidates immediately and trigger coordinator escalation in parallel — do not wait for the response window to expire.
7. If a candidate declines, set `in_active_outreach` = `false` and `response_status` = `declined`; contact the next-ranked available candidate immediately without waiting for the current window to expire.
8. If a candidate does not respond within the outreach window, set `in_active_outreach` = `false` and `response_status` = `no_response`; contact the next-ranked available candidate immediately.
9. If a candidate confirms, set `confirmed_nurse_id` and `confirmation_timestamp`; set `in_active_outreach` = `false` for all other candidates contacted on this fill cycle; route to coordinator approval interface.
10. If multiple candidates confirm simultaneously, accept the confirmation with the earliest `confirmation_timestamp` (ISO 8601 UTC; precision to milliseconds). If two confirmations have identical timestamps, accept the confirmation from the highest-ranked candidate (lowest `rank` value) and decline all others; log all confirmation timestamps and the tiebreak method applied.
11. If all ranked candidates have been contacted and no confirmation received, trigger `no_nurse_confirmed` escalation with the full `outreach_log`.
12. Do not contact the hospital at any point during outreach — all hospital communication routes through the coordinator.

---

## Error handling

| Error condition | What the agent does |
|---|---|
| Nurse contact details missing for a candidate | Skip that candidate; log missing contact details in `outreach_log`; contact next-ranked candidate |
| Outreach channel unavailable (SMS gateway down, email delivery failure) | Retry via next available channel for that nurse; if all channels fail, log and contact next-ranked candidate |
| Candidate confirms but `in_active_outreach` state cannot be updated | Log state update failure; escalate to coordinator flagging potential double-booking risk before approval proceeds |
| `active_fill_cycles` state unavailable at entry | Log state unavailability; proceed using `in_active_outreach` values from `ranked_candidates` input; flag to coordinator that concurrent fill state could not be re-confirmed at outreach time |
| Fill cycle cancelled by coordinator during active outreach | Set `in_active_outreach` = `false` for all contacted candidates immediately; send cancellation notification via original outreach channel to each; log cancellation in `outreach_log` |

---

## Delegation boundaries

Labels: **[Agent Alone]** = executes without notification; **[Agent + Log]** = executes and writes to audit record; **[Agent + Escalate]** = executes and notifies coordinator immediately; **[Human Required]** = agent surfaces information and waits for human decision.

| Decision or action | Label | Escalation SLA |
|---|---|---|
| Filter ranked candidates by in_active_outreach on entry (rule 1) | [Agent Alone] | — |
| Select top N candidates for simultaneous contact (rule 2) | [Agent Alone] | — |
| Set in_active_outreach = true on outreach send (rule 3) | [Agent + Log] | — |
| Select contact channel per candidate (rule 4) | [Agent Alone] | — |
| Retry via next available channel on channel failure | [Agent + Log] | — |
| Set outreach response window by urgency tier (rule 5) | [Agent Alone] | — |
| Trigger coordinator escalation in parallel for shallow pool (rule 6) | [Agent + Escalate] | Coordinator acknowledges within 5 minutes (≤4h urgency fills) |
| Set in_active_outreach = false and contact next candidate on decline (rule 7) | [Agent + Log] | — |
| Set in_active_outreach = false and contact next candidate on no_response (rule 8) | [Agent + Log] | — |
| Route confirmed nurse to coordinator approval interface (rule 9) | [Agent + Escalate] | Coordinator approves or overrides within 15 minutes; if no action, escalate to team lead |
| Apply confirmation timestamp tiebreak (rule 10) | [Agent + Log] | — |
| Trigger no_nurse_confirmed escalation (rule 11) | [Agent + Escalate] | Coordinator acknowledges within 15 minutes; team lead notified if no action |
| Send cancellation notification to contacted nurses on cycle cancel | [Agent + Log] | — |

**Override mechanism:** Coordinators may override the confirmed nurse at the approval interface. Override must be logged with `coordinator_id`, `original_confirmed_nurse_id`, `override_nurse_id`, and `override_reason`. Agent re-routes outreach to the override nurse; all other candidates notified of decline.

---

## Shared entities

The following fields are shared with the candidate ranking capability spec. Field names and types must be identical in both specs:

- `nurse_id` (string)
- `job_order_id` (string)
- `in_active_outreach` (boolean) — this spec writes `in_active_outreach` = `true` on outreach send and `false` on decline, no_response, or fill cycle complete; candidate ranking reads this state for concurrent fill exclusion
- `RankedCandidate` — this spec consumes the full `RankedCandidate` record from candidate ranking; `nurse_id`, `rank`, `rationale`, and `in_active_outreach` must be identical to the candidate ranking spec

---

## Validation scenarios

### Happy path

**Input:** 4 ranked candidates; `urgency_hours` = 6 (MEDIUM tier — 60-minute outreach window); `max_concurrent_outreach` = 3; all candidates available (in_active_outreach = false); candidate 1 preferred channel = SMS; candidate 2 preferred channel = email; candidate 3 preferred channel = SMS; candidate 4 no preferred channel. Candidate 2 confirms 35 minutes after outreach sent.

**Expected output:** 3 outreach records created simultaneously for candidates 1, 2, 3 (N = min(3, 4)); in_active_outreach = true for all 3 on send; candidate 4 not contacted (cap not reached). Candidate 2 confirmation received within window; `confirmed_nurse_id` = candidate 2's nurse_id; in_active_outreach set to false for candidates 1 and 3; decline notification sent via their original channels; routed to coordinator approval interface; `escalation_type` = null.

### Edge cases

1. **Shallow pool at high urgency (rule 6):** `urgency_hours` = 2 (≤4h); available pool after filtering = 2 candidates. Expected: both candidates contacted immediately; coordinator escalation triggered in parallel at the same timestamp as outreach send; outreach response window not awaited before escalation.

2. **Candidate declines — next contacted immediately:** Candidate 1 declines 5 minutes into a 60-minute window. Expected: candidate 1 in_active_outreach set to false; response_status = declined; candidate 4 (next ranked, not yet contacted) contacted immediately without waiting for the window to expire; outreach_log records decline time and next-contact time.

3. **No preferred channel set for any candidate:** All ContactDetail records have preferred = false. Expected: SMS used as default first channel for all candidates (rule 4 fallback); no error; outreach proceeds normally.

4. **Candidate confirms via different channel than contacted:** Nurse is contacted by SMS but responds by calling the coordinator directly. The system does not receive a programmatic reply. Expected: outreach window expires; response_status = no_response; next candidate contacted. This failure mode is noted in the validation plan as undetectable by automated test — requires human observation in live operation.

5. **Fill cycle cancelled during active outreach:** Coordinator cancels the fill cycle while 3 nurses are in_active_outreach. Expected: in_active_outreach set to false for all 3 immediately; cancellation notification sent to each via their original outreach channel; cancellation logged in outreach_log with timestamp; no confirmation route triggered.

### Failure modes

1. **All ranked candidates contacted — no confirmation:** All candidates have been contacted; all responses are declined or no_response. Expected: `escalation_type` = NO_NURSE_CONFIRMED; full `outreach_log` included in escalation payload; coordinator alerted immediately.

2. **All contact channels fail for a candidate:** SMS gateway down and email delivery fails for candidate 1; phone also unavailable. Expected: all channel failure attempts logged in outreach_log for candidate 1; candidate 1 skipped; next-ranked candidate contacted immediately; escalation triggered only if all candidates are exhausted.

3. **in_active_outreach state cannot be updated on confirmation:** Candidate confirms but the state write fails. Expected: coordinator escalated immediately with "potential double-booking risk" flag before approval proceeds; agent does not route to hospital notification until coordinator acknowledges the risk.

---

## Assumptions

| Assumption | Status | What changes if wrong | Validation |
|---|---|---|---|
| SMS, email, and phone outreach channels are accessible via API or integration at send time | [Flagged] | Outreach cannot be sent programmatically; parallel outreach degrades to coordinator-assisted manual process, removing the primary fill-time reduction mechanism | Ask Aaron: which channels are API-accessible today? Are there existing vendor contracts for SMS and email gateways? |
| `in_active_outreach` state is consistent and readable in real time across all concurrent fill cycles | [Flagged] | Rules 1 and 3 fail; candidates may be double-contacted across concurrent fills. Fallback: implement as a database flag per nurse. | Ask Aaron (week 1): does shared state infrastructure exist? What is the write-to-read latency guarantee? |
| Urgency tier thresholds (≤4h, 4–24h, >24h) and corresponding outreach windows (20 / 60 / 120 min) reflect actual MedFlex nurse response patterns | [Flagged] | Outreach windows expire too early or too late; fill time target is missed or pool is burned through prematurely. Thresholds and windows are configurable defaults — can be adjusted from pilot data without architectural change. | Ask Kim: what is the typical nurse response time to outreach? Review 3 months of fill data if available. |
| Nurses respond via the same channel they were contacted on | [Assumed] | Response detection fails for nurses who reply via a different channel; outreach window expires and nurse remains in_active_outreach | Not testable before live operation — note as a known production failure mode; monitor cross-channel responses in pilot. |
| Nurse contact details in the nurse record are current | [Assumed] | Outreach sent to stale details; no response received; fill time extends by at least one outreach window per stale candidate | Ask Kim: how frequently are nurse contact records updated in the CRM? Is there a self-service update mechanism for nurses? |
| A nurse's confirmation reply is sufficient evidence of availability before routing to coordinator approval | [Assumed] | Nurses who confirm and then no-show inflate the no-show rate; a harder commitment mechanism may be needed | Monitor during pilot: track confirmation-to-no-show rate over first 30 fills; revisit if rate exceeds 5% |

---

## Integration contracts

Every item marked [REQUIRED BEFORE BUILD] must be confirmed with the named system owner before implementation begins.

### SMS gateway

| Item | Value |
|---|---|
| System owner | [REQUIRED BEFORE BUILD: confirm with Aaron — existing vendor contract or new procurement] |
| Endpoint URL | [REQUIRED BEFORE BUILD] |
| Authentication | [REQUIRED BEFORE BUILD] — credentials stored in secrets manager |
| Request format | {to: string (E.164 phone number), body: string (max 160 chars), metadata: {job_order_id, nurse_id}} |
| Response format — success | {message_id: string, status: "queued"} |
| Response format — failure | {error_code: string, error_message: string} |
| Inbound reply format | [REQUIRED BEFORE BUILD: webhook or polling — confirm with vendor] |
| Timeout | [REQUIRED BEFORE BUILD — recommended ≤ 5 seconds] |
| Retry logic | HTTP 5xx: up to 2 retries with 2s, 4s backoff. HTTP 4xx: do not retry; log channel failure; try email channel |
| Rate limits | [REQUIRED BEFORE BUILD] |
| Fallback if unavailable | Try email channel; if email also fails, log and contact next-ranked candidate |

### Email gateway

| Item | Value |
|---|---|
| System owner | [REQUIRED BEFORE BUILD] |
| Endpoint URL | [REQUIRED BEFORE BUILD] |
| Authentication | [REQUIRED BEFORE BUILD] — credentials stored in secrets manager |
| Request format | {to: string (email address), subject: string, body: string, metadata: {job_order_id, nurse_id}} |
| Inbound reply detection | [REQUIRED BEFORE BUILD: webhook, IMAP polling, or reply-to address — confirm with vendor] |
| Timeout | [REQUIRED BEFORE BUILD — recommended ≤ 5 seconds] |
| Retry logic | HTTP 5xx: up to 2 retries. HTTP 4xx: do not retry; log channel failure; try phone channel |
| Fallback if unavailable | Try phone channel; if phone also fails, log and contact next-ranked candidate |

### Agent state store (reads and writes: in_active_outreach)

| Item | Value |
|---|---|
| System owner | Aaron — implementation TBD |
| Write latency requirement | `in_active_outreach` = true must be visible to concurrent fill cycles within 500ms of write |
| Read latency requirement | ≤ 500ms |
| Concurrency requirement | Writes from concurrent fill cycles must be atomic; no race conditions on in_active_outreach flag |
| Fallback if write fails | Log state update failure; escalate to coordinator flagging potential double-booking risk before approval proceeds |
| Fallback if read unavailable at entry | Log unavailability; proceed using in_active_outreach values from ranked_candidates input; flag to coordinator |

### CRM (writes: outreach_log, confirmed_nurse_id, confirmation_timestamp)

| Item | Value |
|---|---|
| System owner | Aaron |
| Endpoint URL | [REQUIRED BEFORE BUILD] |
| Authentication | [REQUIRED BEFORE BUILD] — credentials stored in secrets manager |
| Write format — outreach_log | {job_order_id, nurse_id, channel, outreach_sent_at: ISO 8601 UTC, response_received_at: ISO 8601 UTC or null, response_status: enum[confirmed, declined, no_response], in_active_outreach: boolean} |
| Write format — confirmation | {job_order_id, confirmed_nurse_id, confirmation_timestamp: ISO 8601 UTC milliseconds} |
| Timeout | [REQUIRED BEFORE BUILD — recommended ≤ 3 seconds] |
| Retry logic | HTTP 5xx: up to 2 retries with 1s, 2s backoff. Timeout: retry once; if second failure, log and flag for manual reconciliation |
| Fallback if unavailable | Buffer outreach records locally; write to CRM when available; flag in audit log that CRM write was delayed |

---

## Governance and audit

### Audit trail schema

Every outreach event and state change produces an immutable audit record. Fields:

| Field | Type | Notes |
|---|---|---|
| outreach_event_id | UUID | Generated per outreach send; immutable |
| job_order_id | string | From CRM |
| fill_cycle_id | UUID | Unique per fill cycle; links all events for one fill |
| nurse_id | string | Candidate contacted |
| channel | enum: SMS, EMAIL, PHONE | Channel used for this outreach event |
| outreach_sent_at | ISO 8601 datetime UTC ms precision | When outreach sent |
| response_received_at | ISO 8601 datetime UTC ms precision or null | When response received |
| response_status | enum: CONFIRMED, DECLINED, NO_RESPONSE | Outcome of this outreach event |
| in_active_outreach_before | boolean | State before this event |
| in_active_outreach_after | boolean | State after this event |
| channel_failure_reason | string or null | Error message if channel failed |
| tiebreak_applied | boolean | Whether rule 10 tiebreak was applied for this confirmation |
| coordinator_override | boolean | Whether coordinator overrode the confirmation |
| coordinator_override_detail | JSON or null | {coordinator_id, original_confirmed_nurse_id, override_nurse_id, override_reason} |

**Retention:** Minimum 3 years. Legal counsel to confirm healthcare staffing compliance requirements.

**Applicable regulations:** Nurse contact data (phone numbers, email addresses) is PII. Access to outreach audit records must be restricted to authorised personnel. Confirmation records for placed shifts may be subject to state labour and healthcare staffing regulations.

### HITL checkpoints

| Checkpoint | Who acts | SLA | If SLA missed |
|---|---|---|---|
| Coordinator approval of confirmed nurse before hospital notification | Kim's team | 15 minutes from confirmation | Escalate to team lead; hold hospital notification |
| Shallow pool high-urgency escalation (rule 6) | Coordinator | 5 minutes (≤4h urgency) | Team lead notified immediately |
| no_nurse_confirmed escalation | Coordinator | 15 minutes | Team lead notified; fill may require manual coordinator outreach |

---

## Economics

| Operation | Classification | Notes |
|---|---|---|
| Filter ranked_candidates by in_active_outreach on entry | Check | In-memory read; negligible |
| Send outreach per candidate (SMS or email) | Coordinate | One outreach gateway call per candidate contacted simultaneously; max 3 per fill cycle at default cap |
| Receive and match inbound reply to job_order_id and nurse_id | Check | Event-driven (webhook) or polling; polling is more expensive — prefer webhook implementation |
| Set in_active_outreach in agent state store | Coordinate | One write per state change; latency-critical |
| Write outreach_log record to CRM | Coordinate | One write per outreach event |
| Route to coordinator approval interface | Generate | One notification per confirmed fill |
| Trigger escalation (pool_exhausted, no_nurse_confirmed, shallow pool) | Coordinate | One write per escalation event; infrequent |

**Batching:** Simultaneous outreach to N candidates (rule 2) sends N requests in parallel, not sequentially. This is the intended design — do not serialize outreach sends.

**Cost sensitivity:** SMS gateway costs are per-message. At current MedFlex volumes (~5.5 hires/month), gateway cost is negligible. If volume grows above 100 fills/month, review gateway pricing tier and consider batched send confirmation where vendor supports it.
