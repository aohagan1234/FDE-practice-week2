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

## Scoring formula

All factor scores are normalised to [0, 1] before weighting. Composite score = sum of (weight × factor score) for the three factors.

### Factor weights by urgency tier

| Factor | HIGH (≤4h) | MEDIUM (4–24h) | LOW (>24h) |
|---|---|---|---|
| Credential specificity | 0.2 | 0.4 | 0.6 |
| Proximity | 0.5 | 0.4 | 0.1 |
| Response rate | 0.3 | 0.2 | 0.3 |
| **Total** | **1.0** | **1.0** | **1.0** |

### Factor score definitions

**Credential specificity score:**
```
credential_score = count(required_credentials matched in candidate.credentials)
                 / count(required_credentials)
```
Returns 1.0 if all required credentials matched; proportional fraction otherwise. Returns 1.0 if `required_credentials` is empty.

**Proximity score:**
```
proximity_score = 1 / (1 + proximity_miles / R)
```
R = 10 miles (configurable reference unit; validate against MedFlex geographic footprint before build). A candidate at 0 miles scores 1.0; at 10 miles scores 0.5; at 30 miles scores 0.25.

**Response rate score:** Used directly. `response_rate` is a float in [0.0, 1.0] representing historical proportion of outreach attempts resulting in a confirmed placement. If absent, rule 8 applies (pool median imputation; fallback 0.5 neutral default if no pool data is available).

### Composite score calculation

```
composite_score = (credential_weight × credential_score)
               + (proximity_weight × proximity_score)
               + (response_rate_weight × response_rate)
```

Rule 6 overrides composite score ordering on specialist shifts: all exact-match candidates rank above all near-match candidates regardless of composite scores. Within each group, candidates sort by composite score descending.

---

## Decision rules

1. If `in_active_outreach` is `true` for a candidate on any active fill cycle, exclude that candidate from the ranked output entirely.
2. If `no_show_history` contains a record at this `facility_type` within the last 90 days, place that candidate last in the ranked output regardless of all other factors.
3. If `urgency_hours` ≤ 4 (HIGH tier), apply weights: proximity 0.5, response_rate 0.3, credential 0.2. Proximity is the dominant factor.
4. If `urgency_hours` > 24 (LOW tier), apply weights: credential 0.6, response_rate 0.3, proximity 0.1. Credential specificity is the dominant factor.
5. If 4 < `urgency_hours` ≤ 24 (MEDIUM tier), apply weights: credential 0.4, proximity 0.4, response_rate 0.2. Credential and proximity are equally weighted.
6. If the required credential is classified as specialist-tier in the credential classification config (provided by the compliance team before build), rank candidates with an exact credential match above all candidates with near-match credentials, regardless of urgency tier. The credential classification config is owned by Linda/compliance — it is a config input to this capability, not a hardcoded list.
7. If `hospital_preference_history` contains a record pairing this `facility_type` with a `nurse_id` in `eligible_candidates`, and the gap between the candidate immediately above that nurse and that nurse's own composite score satisfies `(score_above - score_below) / score_above ≤ 0.10`, move that nurse up one rank position. The boost never crosses the specialist exact/near-match boundary defined in rule 6.
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

## Delegation boundaries

Labels: **[Agent Alone]** = executes without notification; **[Agent + Log]** = executes and writes to audit record; **[Agent + Escalate]** = executes and notifies coordinator immediately; **[Human Required]** = agent surfaces information and waits for human decision before proceeding.

| Decision or action | Label | Escalation SLA |
|---|---|---|
| Apply urgency tier and select factor weights | [Agent Alone] | — |
| Score all candidates and apply composite ranking | [Agent Alone] | — |
| Apply rule 6 specialist hard-split | [Agent Alone] | — |
| Apply rule 2 no-show demotion | [Agent + Log] | — |
| Apply rule 7 preference boost | [Agent + Log] | — |
| Apply rule 8 response rate imputation | [Agent + Log] | — |
| Apply rule 1 active-outreach exclusion | [Agent Alone] | — |
| Select tiebreaker by nurse_id alphanumeric sort | [Agent + Log] | — |
| Trigger `pool_exhausted` escalation | [Agent + Escalate] | Coordinator acknowledges within 15 minutes; if no response, escalate to team lead |
| Trigger `intake_parsing_ambiguity` escalation | [Human Required] | Ranking is blocked until coordinator confirms credential requirements; no timeout |
| Trigger `data_source_unavailable` escalation (compliance system) | [Human Required] | Ranking is blocked; coordinator acknowledges within 15 minutes |
| Log `active_fill_cycles` state unavailability and proceed | [Agent + Escalate] | Coordinator notified immediately that concurrent fill state could not be confirmed |

**Override mechanism:** Coordinators may override the ranked output at the coordinator approval interface. Any override must be logged with `coordinator_id`, `original_rank`, `override_rank`, and `override_reason`. The original ranking output is retained in the audit record unchanged.

---

## Shared entities

The following fields are shared with the parallel outreach capability spec. Field names and types must be identical in both specs:

- `nurse_id` (string)
- `job_order_id` (string)
- `in_active_outreach` (boolean) — parallel outreach must set this to `true` when outreach begins for a nurse on any fill cycle; candidate ranking reads this state
- `RankedCandidate` — the output of this spec is the primary input to parallel outreach; the full record including `nurse_id`, `rank`, `rationale`, and `in_active_outreach` passes through unchanged

---

## Validation scenarios

### Happy path

**Input:** ICU specialist shift; `urgency_hours` = 48 (LOW tier); `required_credentials` = ["ICU_RN"]; pool of 4 eligible nurses: Nurse A (exact ICU_RN match, 5 miles, response_rate 0.8), Nurse B (near-match, 2 miles, response_rate 0.9), Nurse C (exact ICU_RN match, 15 miles, response_rate 0.6), Nurse D (near-match, 3 miles, response_rate 0.7); no active outreach; no no-show history; no preference history; `specialist_credential_config` includes "ICU_RN".

**Expected output:** Nurse A rank 1, Nurse C rank 2 (exact ICU match — rule 6 hard-split; within exact group, Nurse A wins on proximity-adjusted composite at LOW weights); Nurse B rank 3, Nurse D rank 4 (near-match group sorted by composite score); rationale for each cites urgency tier, credential match status, and proximity; `escalation_type` = None; 4 candidates returned.

### Edge cases

1. **Pool reduced to one after active-outreach filter (rule 1):** 5 eligible candidates; 4 have `in_active_outreach` = true. Expected: 1 ranked candidate at rank 1; `escalation_type` = None; no escalation triggered.

2. **All response rates absent:** All candidates have `response_rate` = None; pool median not calculable. Expected: neutral default 0.5 substituted for all candidates; every rationale flags "response_rate (imputed — no historical data)"; ranking proceeds without error.

3. **No-show at different facility within lookback window:** Candidate has a no-show record within 90 days but for a different `facility_type` than the current job order. Expected: rule 2 does not apply; candidate ranked normally on composite score.

4. **Preference boost at specialist boundary:** Preferred nurse is in the near-match group on a specialist shift. The candidate ranked immediately above in the near-match group has a composite score within 10% of the preferred nurse. Expected: preference boost applies within the near-match group; preferred nurse moves up one position. The preferred nurse does not cross above any exact-match candidate (rule 6 boundary is respected).

5. **Pool larger than 5 after filtering:** 8 eligible candidates after rules 1 and 2. Expected: top 5 by composite score (with rule 6 and 7 applied) returned; candidates 6–8 not included; `ranked_candidates` length = 5.

### Failure modes

1. **All candidates excluded — pool exhausted:** After rules 1 and 2, zero candidates remain (all in active outreach). Expected: `escalation_type` = POOL_EXHAUSTED; `ranked_candidates` = []; escalation payload includes nurse_ids excluded and reasons (IN_ACTIVE_OUTREACH or RECENT_NO_SHOW); no outreach triggered.

2. **Compliance system unavailable:** `credentials` cannot be verified for any candidate. Expected: ranking is not attempted; `data_source_unavailable` escalation triggered immediately; coordinator notified; no ranked output produced; ranking resumes only on coordinator instruction.

3. **`required_credentials` absent from job order:** `required_credentials` is empty or missing. Expected: `intake_parsing_ambiguity` escalation triggered; ranking is blocked until coordinator confirms credential requirements; no output produced.

---

## Assumptions

| Assumption | Status | What changes if wrong | Validation |
|---|---|---|---|
| CRM holds per-nurse response rate and no-show history logged by coordinators | [Flagged] | Rules 8 and 2 cannot be applied reliably; ranking falls back to credential specificity and proximity only; rationale thins and coordinator trust declines | Ask Kim: what percentage of fills have response rate and no-show data logged in the CRM? |
| `hospital_preference_history` in CRM is consistently logged and current | [Flagged] | Rule 7 applies stale preferences; a nurse the hospital has flagged negatively may be boosted above a preferred nurse | Ask Kim: is hospital preference history actively maintained in the CRM, or only logged on request? |
| `in_active_outreach` state is accurate and updated in real time across all concurrent fill cycles | [Flagged] | Rule 1 fails; candidates already in outreach for another fill are contacted, risking double-booking. Fallback: implement as a database flag per nurse. | Ask Aaron (week 1): does shared state infrastructure exist? What is the write-to-read latency? |
| `urgency_hours` derived from parsed `shift_start_datetime` is accurate | [Assumed] | Wrong urgency tier applied; factor weighting does not match actual fill window | Validate with a sample of 20 past job orders: does the parsed shift_start_datetime match the actual shift start? |
| Urgency tier thresholds (≤4h, 4–24h, >24h) reflect how MedFlex shift urgency clusters in practice | [Flagged] | Factor weighting is applied to the wrong tier for a material proportion of fills. Thresholds are configurable defaults and can be adjusted without architectural change. | Ask Kim: how do shifts typically cluster by urgency? Review 3 months of fill data from the CRM if available. |
| Specialist credential classification config is provided by the compliance team before build and kept current | [Flagged] | Rule 6 misidentifies specialist vs. generalist credentials; near-match nurses excluded or boosted incorrectly. | Ask Linda: can she provide and own the credential classification config before build starts? What is the review cadence? |

---

## Integration contracts

Every item marked [REQUIRED BEFORE BUILD] must be confirmed with the named system owner before implementation begins.

### CRM (reads: hospital_preference_history, response_rate, no_show_history)

| Item | Value |
|---|---|
| System owner | Aaron — confirm before build |
| Endpoint URL | [REQUIRED BEFORE BUILD] |
| Authentication | [REQUIRED BEFORE BUILD: API key / OAuth / other] — credentials stored in secrets manager |
| Response format — preference history | List of PlacementRecord: {nurse_id: string, facility_type: string, placement_date: ISO 8601 date} |
| Response format — response_rate | float [0.0, 1.0]; null if no history exists for that nurse |
| Response format — no_show_history | List of {date: ISO 8601 date, facility_type: string} |
| Timeout | [REQUIRED BEFORE BUILD — recommended ≤ 3 seconds] |
| Retry logic | HTTP 5xx: up to 2 retries with 1s, 2s backoff. HTTP 4xx: do not retry; log and treat as data unavailable. Timeout: do not retry; apply rule 8 fallback |
| Rate limits | [REQUIRED BEFORE BUILD] |
| Fallback if unavailable | Apply rule 8 (median imputation, fallback 0.5) for all candidates; log data_source_unavailable; proceed with ranking |

### Compliance system (reads: nurse credentials)

| Item | Value |
|---|---|
| System owner | Linda — confirm before build |
| Endpoint URL | [REQUIRED BEFORE BUILD] |
| Authentication | [REQUIRED BEFORE BUILD] — credentials stored in secrets manager |
| Response format — credentials | List of credential strings per nurse_id (e.g., ["ICU_RN", "BLS", "ACLS"]) |
| Timeout | [REQUIRED BEFORE BUILD — recommended ≤ 3 seconds] |
| Retry logic | HTTP 5xx: up to 2 retries. Timeout or 4xx: trigger data_source_unavailable escalation; hold ranking |
| Fallback if unavailable | Hold ranking; trigger data_source_unavailable escalation; do not rank with unverifiable credentials |

### Agent state store (reads: in_active_outreach, active_fill_cycles)

| Item | Value |
|---|---|
| System owner | Aaron — implementation TBD (shared database or in-memory cache) |
| Read latency requirement | ≤ 500ms; reads within this window are treated as current |
| Write latency requirement | `in_active_outreach` write by parallel outreach must be visible to concurrent fill cycles within 500ms |
| Fallback if unavailable | Treat in_active_outreach = false for all candidates; log state unavailability; escalate to coordinator |

---

## Governance and audit

### Audit trail schema

Every ranking invocation produces an immutable audit record. Fields:

| Field | Type | Notes |
|---|---|---|
| ranking_id | UUID | Generated on invocation; immutable |
| job_order_id | string | From CRM |
| ranking_timestamp | ISO 8601 datetime UTC | When ranking executed |
| urgency_tier | enum: HIGH, MEDIUM, LOW | Tier applied |
| factor_weights | JSON | {credential: float, proximity: float, response_rate: float} |
| is_specialist_shift | boolean | Whether rule 6 applied |
| pool_size_before_filter | integer | Eligible candidates before rules 1 and 2 |
| pool_size_after_filter | integer | Candidates after rules 1 and 2 |
| escalation_type | string or null | POOL_EXHAUSTED / INTAKE_PARSING_AMBIGUITY / DATA_SOURCE_UNAVAILABLE / null |
| ranked_candidate_ids | string[] | nurse_ids in rank order |
| response_rate_imputed | boolean | Whether any candidate used imputed response_rate |
| concurrent_fill_state_confirmed | boolean | Whether active_fill_cycles state was available |
| coordinator_override | boolean | Whether a coordinator overrode the ranked output |
| coordinator_override_detail | JSON or null | {coordinator_id, original_rank, override_rank, override_reason} |

**Retention:** Minimum 3 years. MedFlex legal counsel must confirm whether state nursing board, Joint Commission, or other healthcare staffing compliance requirements extend this period.

**Applicable regulations:** Nurse credential data and fill records may be subject to state nursing board regulations and, depending on facility type, Joint Commission accreditation requirements. All nurse PII (nurse_id, contact details, credential records) must be accessible only to authorised HR and compliance personnel. Data access to audit records must be logged.

### HITL checkpoints

| Checkpoint | Who acts | SLA | If SLA missed |
|---|---|---|---|
| Coordinator approval of ranked output before hospital notification | Kim's team | 15 minutes from ranking completion | Escalate to team lead; hold fill cycle if no action within 30 minutes |
| Credential requirement confirmation (intake_parsing_ambiguity) | Coordinator | No timeout — ranking blocked | Fill cycle on hold until resolved |
| Compliance system unavailability acknowledgement | Coordinator | 15 minutes | Team lead notified; fill cycle on hold |

---

## Economics

| Operation | Classification | Notes |
|---|---|---|
| Read eligible_candidates (from eligibility pre-filter) | Check | In-memory input; no external call |
| Read hospital_preference_history from CRM | Coordinate | One CRM read per ranking invocation; cache at fill cycle scope |
| Read active_fill_cycles from agent state store | Check | Latency-sensitive shared state read |
| Score all candidates (composite calculation) | Validate | O(n) over pool size; negligible at MedFlex volumes (~10 candidates per fill) |
| Generate rationale string per RankedCandidate | Generate | One string per candidate (max 5); deterministic template; minimal token cost |
| Trigger escalation and write escalation record | Coordinate | One write per escalation event; infrequent |
| Write audit record to CRM | Coordinate | One write per ranking invocation |

**Caching:** Load `specialist_credential_config` once at startup; reload only on config change. Cache `hospital_preference_history` for the duration of a fill cycle; do not re-read CRM mid-ranking.

**Circuit breaker:** Not required at current MedFlex fill volumes. If concurrent fills exceed 20 per hour, add a circuit breaker on CRM reads to prevent cascading failure under load.
