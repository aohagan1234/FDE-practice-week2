# D7 — Validation Plan
**MedFlex Engagement | Capabilities: Candidate Ranking + Parallel Outreach**

---

## Pre-production tests

| Test | What it checks | Pass criteria | Who runs it |
|---|---|---|---|
| Urgency tier classification | Correct tier assigned for urgency_hours at each boundary (4, 24) | Hours ≤4 → HIGH; 4 < hours ≤24 → MEDIUM; hours >24 → LOW | Dev (automated) |
| Specialist credential config loading | Credential classification config read from compliance team input, not hardcoded | Agent applies exact-match priority only for credentials in the loaded config | Dev + Linda (compliance) |
| Ranking factor weights per tier | Correct weights applied for each urgency tier | HIGH: proximity 0.5, response_rate 0.3, credential 0.2; MEDIUM: credential 0.4, proximity 0.4, response_rate 0.2; LOW: credential 0.6, response_rate 0.3, proximity 0.1 | Dev (automated) |
| Response rate imputation | Median correctly substituted when response_rate is None | Imputed value equals median of pool's known rates; rationale flags imputation | Dev (automated) |
| Pool exhausted escalation | Triggered when all candidates in_active_outreach or pool is empty | EscalationType.POOL_EXHAUSTED returned; no outreach sent | Dev (automated) |
| Preference boost boundary | Boost applied only when score gap ≤10%; specialist boundary never crossed | Preferred nurse moves up one rank when within threshold; does not cross exact/near-match split | Dev (automated) |
| No-show lookback window | Only no-shows within 90 days at the same facility demote a candidate | No-show at different facility or >90 days ago has no effect on rank | Dev (automated) |
| Outreach window per urgency tier | Correct window set before first candidate is contacted | ≤4h urgency → 20 min window; 4–24h → 60 min; >24h → 120 min | Dev (automated) |
| Simultaneous confirmation handling | First confirmation by timestamp accepted; others declined | Only one nurse confirmed per fill cycle; all others receive decline notification | Dev (automated) |
| Max candidates cap | No more than 5 candidates returned by ranking | Pool of 7+ returns exactly 5 ranked candidates | Dev (automated) |

---

## Agent decision tests

| Scenario | Input | Expected agent action | How to verify |
|---|---|---|---|
| **Candidate ranking — happy path** | ICU specialist shift, urgency 48h, 4 eligible nurses: 2 exact ICU credential match, 2 near-match; all available | Exact match candidates ranked above near-match regardless of proximity; rationale cites specialist credential and >24h urgency window | Assert ranked_candidates[0] and [1] are exact matches; assert rationale contains "exact specialist credential match" |
| **Candidate ranking — edge case** | Urgent fill (2h), pool of 5: 3 in_active_outreach on a concurrent fill, 1 with recent no-show at this facility, 1 available with no history | Single available candidate returned at rank 1; pool not exhausted because 1 candidate remains | Assert 1 ranked candidate returned; assert escalation_type is None; assert no-show nurse absent from ranked output |
| **Candidate ranking — error condition** | CRM unavailable; all candidates have response_rate = None; no no-show history | Ranking proceeds using 0.5 neutral default for all response rates; every rationale flags "imputed — no historical data" | Assert escalation_type is None; assert all rationale strings contain "imputed" |
| **Parallel outreach — happy path** | 4 ranked candidates, urgency 6h, max_concurrent_outreach = 3 | Top 3 candidates contacted simultaneously; in_active_outreach set to True for each on send; first to confirm triggers coordinator approval route | Assert 3 outreach records created simultaneously; assert confirmed_nurse_id populated on first response; assert in_active_outreach = False for non-confirmed candidates after fill |
| **Parallel outreach — edge case (shallow pool + high urgency)** | urgency_hours = 2, available pool = 2 after filtering | Both candidates contacted immediately; coordinator escalation triggered in parallel without waiting for response window to expire | Assert 2 outreach records; assert coordinator escalation fired at same timestamp as outreach; assert response window not awaited |
| **Parallel outreach — error condition (channel failure)** | Top candidate has SMS as preferred channel; SMS gateway unavailable | Retry via email for that candidate; if email also fails, log and contact next-ranked candidate; outreach_log records channel failure | Assert outreach_log contains channel failure entry for nurse; assert next-ranked nurse contacted; assert escalation not triggered unless all candidates exhausted |

---

## Integration tests

| System | What to test | Pass criteria |
|---|---|---|
| CRM | Read nurse response rate and no-show history at ranking time | Correct values returned per nurse_id; stale or missing data handled without ranking failure |
| CRM | Read hospital_preference_history for facility_type | Correct preferred nurse_ids returned; empty result handled gracefully |
| Compliance system | Read credential status per nurse at eligibility filter time | Credential list returned per nurse_id; system unavailability triggers data_source_unavailable escalation, not a silent failure |
| Nurse portal | Read availability status per nurse | Available/unavailable flag returned; mixed reliability acknowledged in eligibility filter |
| Agent state store | Write in_active_outreach = true on outreach send; read across concurrent fill cycles | State visible to candidate ranking for a concurrent fill within 500ms of write; no stale reads |
| SMS/email gateway | Send outreach message; detect inbound response on same channel | Message delivered; reply received and matched to correct nurse_id and job_order_id |
| Coordinator approval interface | Surface ranked candidates with rationale; receive approval or override | All ranked candidates displayed with rationale; approval triggers hospital notification; override re-routes to coordinator manual action |
| Hospital notification | Send confirmation email on coordinator approval | Email delivered to correct hospital contact; confirmation_timestamp logged in CRM |

---

## Most likely production failure modes

- **in_active_outreach state inconsistency at high fill volume.** When multiple fill cycles are running concurrently, the shared state for in_active_outreach must be written and read atomically. Under load, a stale read means a nurse already committed to one fill is contacted for a second simultaneously, the outreach window for the second fill is wasted, and the nurse either double-books or declines. This is the most critical dependency and the hardest to surface before production volume because it requires concurrent load that a single-shift test cannot replicate.

- **Nurse response via a different channel than contacted.** If a nurse is contacted by SMS and replies by calling the coordinator directly, the response is not detected by the system, the outreach window expires, the next candidate is contacted, and the original nurse remains in_active_outreach. If that nurse then shows up for the shift, the placement may be double-confirmed. This failure mode is invisible in testing because it depends on nurse behaviour patterns that are only observable in live operation.

- **CRM data sparsity reducing ranking quality below coordinator trust threshold.** If coordinators have not consistently logged response rates and no-show history, the ranking agent operates on credential specificity and proximity only rather than all six factors. The rationale thins, the first-recommendation acceptance rate falls below the 90% threshold needed to trigger Wave 2, and the engagement stalls at Wave 1 indefinitely. This failure mode is silent: the system operates correctly by its own logic while producing rankings that coordinators increasingly override.
