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
4. Contact each candidate via their `preferred` channel first; if no channel is flagged `preferred`, contact via SMS first.
5. If `urgency_hours` ≤ 4, set outreach response window to 20 minutes per candidate; if 4 < `urgency_hours` ≤ 24, set window to 60 minutes; if `urgency_hours` > 24, set window to 120 minutes.
6. If `urgency_hours` ≤ 4 and the available pool after filtering is ≤ 2, contact all available candidates immediately and trigger coordinator escalation in parallel — do not wait for the response window to expire.
7. If a candidate declines, set `in_active_outreach` = `false` and `response_status` = `declined`; contact the next-ranked available candidate immediately without waiting for the current window to expire.
8. If a candidate does not respond within the outreach window, set `in_active_outreach` = `false` and `response_status` = `no_response`; contact the next-ranked available candidate immediately.
9. If a candidate confirms, set `confirmed_nurse_id` and `confirmation_timestamp`; set `in_active_outreach` = `false` for all other candidates contacted on this fill cycle; route to coordinator approval interface.
10. If multiple candidates confirm simultaneously, accept the confirmation with the earliest `confirmation_timestamp`; set `in_active_outreach` = `false` and send a decline notification via original outreach channel to all others; log all confirmation timestamps.
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

## Shared entities

The following fields are shared with the candidate ranking capability spec. Field names and types must be identical in both specs:

- `nurse_id` (string)
- `job_order_id` (string)
- `in_active_outreach` (boolean) — this spec writes `in_active_outreach` = `true` on outreach send and `false` on decline, no_response, or fill cycle complete; candidate ranking reads this state for concurrent fill exclusion
- `RankedCandidate` — this spec consumes the full `RankedCandidate` record from candidate ranking; `nurse_id`, `rank`, `rationale`, and `in_active_outreach` must be identical to the candidate ranking spec

---

## Assumptions

| Assumption | Confidence | What changes if this assumption is wrong |
|---|---|---|
| SMS, email, and phone outreach channels are accessible via API or integration at send time | Low | Outreach cannot be sent programmatically; parallel outreach degrades to coordinator-assisted manual outreach, removing the primary fill-time reduction mechanism |
| `in_active_outreach` state is consistent and readable in real time across all concurrent fill cycles | Medium | Rules 1 and 3 fail; candidates may be double-contacted across concurrent fills, wasting the outreach window |
| Nurses respond via the same channel they were contacted on | Medium | Response detection fails for nurses who reply via a different channel; confirmation is missed and the outreach window expires before the candidate is registered as confirmed |
| Nurse contact details in the nurse record are current | Medium | Outreach is sent to stale contact details; no response is received; fill time extends by at least one outreach window per candidate with stale details |
| A nurse's confirmation reply is sufficient evidence of availability before routing to coordinator approval | Medium | Nurses who confirm and then no-show inflate the no-show rate; a harder commitment mechanism may be required beyond an outreach reply |
