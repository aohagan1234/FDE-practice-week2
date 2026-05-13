# D4 — Capability Specification: Candidate Ranking
**MedFlex Engagement | Discovery: 2026-05-12**

---

**Capability name:** Candidate ranking

**What it does:** Ranks eligible nurse candidates for a shift by reasoning over six context-dependent factors simultaneously and returns a ranked list with a stated rationale per candidate.

---

## Inputs

| Field | Type | Source system | Required? |
|---|---|---|---|
| job_order_id | string | CRM | Yes |
| facility_type | string | CRM (parsed job order) | Yes |
| shift_start_datetime | datetime | CRM (parsed job order) | Yes |
| urgency_hours | integer | Derived: hours until shift_start_datetime at ranking time | Yes |
| required_credentials | string[] | CRM (parsed job order) | Yes |
| eligible_candidates | Candidate[] | Eligibility pre-filter output | Yes |
| hospital_preference_history | PlacementRecord[] | CRM | No |
| active_fill_cycles | FillCycle[] | Agent state (live concurrent fills) | Yes |

Each `Candidate` in `eligible_candidates`:

| Field | Type | Source system | Required? |
|---|---|---|---|
| nurse_id | string | CRM | Yes |
| credentials | string[] | Compliance system | Yes |
| proximity_miles | float | Nurse record | Yes |
| response_rate | float | CRM (historical) | No |
| no_show_history | NoShowRecord[] | CRM | No |
| in_active_outreach | boolean | Agent state | Yes |

---

## Outputs

| Field | Type | Destination |
|---|---|---|
| job_order_id | string | Parallel outreach; CRM audit log |
| ranked_candidates | RankedCandidate[] | Parallel outreach |
| ranking_timestamp | datetime | CRM audit log |

Each `RankedCandidate`:

| Field | Type | Destination |
|---|---|---|
| nurse_id | string | Parallel outreach |
| rank | integer | Parallel outreach; coordinator approval interface |
| rationale | string | Coordinator approval interface |
| in_active_outreach | boolean | Parallel outreach |

---

## Decision rules

1. If `in_active_outreach` is `true` for a candidate on any active fill cycle, exclude that candidate from the ranked output entirely.
2. If `no_show_history` contains a record at this `facility_type` within the last 90 days, place that candidate last in the ranked output regardless of all other factors.
3. If `urgency_hours` ≤ 4, rank by: proximity_miles (primary), response_rate (secondary), credential specificity (tertiary) — provided minimum credential requirements are met.
4. If `urgency_hours` > 24, rank by: credential specificity (primary), response_rate (secondary), proximity_miles (tertiary).
5. If 4 < `urgency_hours` ≤ 24, rank by: credential specificity and proximity_miles equally weighted (primary), response_rate (tiebreaker).
6. If the required credential is classified as specialist-tier in the credential classification config (provided by the compliance team before build), rank candidates with an exact credential match above all candidates with near-match credentials, regardless of urgency tier. The credential classification config is owned by Linda/compliance — it is a config input to this capability, not a hardcoded list.
7. If `hospital_preference_history` contains a record pairing this `facility_type` with a `nurse_id` in `eligible_candidates`, and all other ranking factors for that nurse are within 10% of the next-ranked candidate, move that nurse up one rank position.
8. If `response_rate` is absent for a candidate, substitute the median `response_rate` across the eligible pool for ranking purposes and flag as `response_rate_imputed: true` in the rationale.
9. Return a minimum of 1 and maximum of 5 ranked candidates.
10. If ranked output would be empty after applying rules 1 and 2, do not return a ranked list — trigger `pool_exhausted` escalation instead.
11. Each `RankedCandidate` must include a `rationale` string that names the specific factors that determined its position and the urgency tier applied (e.g., "exact ICU credential match; proximity secondary given 48h urgency window; facility preference record applied").

---

## Error handling

| Error condition | What the agent does |
|---|---|
| `eligible_candidates` is empty on entry | Trigger `pool_exhausted` escalation immediately; do not run ranking |
| All candidates excluded by rules 1 and 2 | Trigger `pool_exhausted` escalation; include list of excluded candidates and exclusion reasons in escalation payload |
| `required_credentials` missing from job order | Hold ranking; trigger `intake_parsing_ambiguity` escalation; do not proceed until coordinator confirms credential requirements |
| CRM unavailable — cannot read `response_rate` or `no_show_history` | Apply rule 8 for all candidates; log `data_source_unavailable`; proceed with ranking; flag in rationale |
| Compliance system unavailable — cannot verify `credentials` | Hold ranking; trigger `data_source_unavailable` escalation; do not rank candidates with unverifiable credential status |
| `active_fill_cycles` state unavailable | Treat `in_active_outreach` as `false` for all candidates; log state unavailability; flag in rationale; escalate to coordinator that concurrent fill state could not be confirmed |
| Tie unresolvable by any rule | Select candidate with lower `nurse_id` (alphanumeric); log tie and tiebreak method in audit record |

---

## Shared entities

The following fields are shared with the parallel outreach capability spec. Field names and types must be identical in both specs:

- `nurse_id` (string)
- `job_order_id` (string)
- `in_active_outreach` (boolean) — parallel outreach must set this to `true` when outreach begins for a nurse on any fill cycle; candidate ranking reads this state
- `RankedCandidate` — the output of this spec is the primary input to parallel outreach; the full record including `nurse_id`, `rank`, `rationale`, and `in_active_outreach` passes through unchanged

---

## Assumptions

| Assumption | Confidence | What changes if this assumption is wrong |
|---|---|---|
| CRM holds per-nurse response rate and no-show history logged by coordinators | Low | Rules 7 and 2 cannot be applied reliably; ranking falls back to credential specificity and proximity only; rationale thins and coordinator trust impact is unknown |
| `hospital_preference_history` in CRM is consistently logged and current | Low | Rule 7 applies stale or incorrect preferences; a nurse the hospital has flagged negatively may be boosted above a preferred nurse |
| `in_active_outreach` state is accurate and updated in real time across all concurrent fill cycles | Medium | Rule 1 fails; candidates already in outreach for another fill are contacted, wasting the outreach window and risking double-booking. **Validate with Aaron (week 1).** Fallback if no shared state infrastructure exists: implement as a database flag per nurse — slower but achieves the same exclusion without architectural change |
| `urgency_hours` derived from parsed `shift_start_datetime` is accurate | Medium | Wrong urgency tier applied (rules 3–5); factor weighting does not match actual fill window |
| Urgency tier thresholds (≤4h, 4–24h, >24h) reflect how MedFlex shift urgency clusters in practice | Low | Factor weighting and outreach windows are applied to the wrong tier for a material proportion of fills. **Thresholds are configurable defaults** — pilot data from weeks 2–5 will establish whether MedFlex shifts cluster around these breakpoints; thresholds can be adjusted without architectural change. Validate with Kim. |
| Specialist credential classification config is provided by the compliance team before build and kept current | Low | Rule 6 misidentifies specialist vs. generalist credentials; near-match nurses are incorrectly excluded or exact-match preference is not applied where required. Config is owned by Linda/compliance — agent reads it but does not interpret or modify it |
