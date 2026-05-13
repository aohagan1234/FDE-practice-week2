# D9 — Self-Spec Build-Loop Reflection
**MedFlex Engagement | Capability: Candidate Ranking**

---

## What was built

- A Python implementation of candidate ranking covering all 11 decision rules: urgency tier classification, weighted composite scoring, specialist credential hard-split, preference boost, no-show demotion, response rate imputation, and pool exhausted escalation, with 18 passing tests
- A scoring function that applies different factor weights by urgency tier (HIGH/MEDIUM/LOW) and a hard group split for specialist credentials that overrides raw scores regardless of urgency
- A rationale builder that generates a natural language explanation per candidate referencing the specific factors and urgency tier applied, matching the example format in rule 11

---

## What Claude Code asked about

No clarifying questions were raised. Implementation decisions were made without surfacing ambiguity back to the spec author. This is significant: it means gaps in the spec were resolved silently by the builder rather than flagged for confirmation. A builder who asks no questions either has a perfectly complete spec or has made undocumented assumptions, and in this case it was the latter. The proximity normalization formula, the interpretation of "within 10%", and the handling of system unavailability were all decided without consultation.

---

## Signals in the output

| Signal | Classification | What the specification failed to say |
|---|---|---|
| Proximity scored as `1/(1 + miles/10)` — 10-mile reference unit is an undocumented builder choice | Unjustified implementation choice | Spec names proximity as a factor but defines no scoring formula; different normalization choices produce materially different rankings for the same pool |
| Rule 7 "within 10%" implemented as composite raw_score comparison | Spec gap | "All other ranking factors within 10%" is ambiguous between checking composite score vs. each individual factor; these produce different outcomes |
| CRM unavailability and absent response_rate data collapse to the same code path (median imputation) | Spec gap | Error handling table requires `data_source_unavailable` escalation for CRM down and median imputation for missing data, but spec provides no input mechanism to distinguish the two conditions |
| Compliance system unavailability is unimplementable | Spec gap | "Hold ranking; trigger data_source_unavailable escalation" requires the function to know the system is unavailable, but the function signature accepts no availability state parameter |
| `pool_exhausted` escalation payload contains no excluded_candidates list | Spec gap | Error handling requires "include list of excluded candidates and exclusion reasons in escalation payload" but RankingResult has no field for this data |

---

## What I would change in the specification

- **Proximity scoring:** Original: "proximity (primary/secondary/tertiary)." Should say: "proximity scored as 1/(1 + miles/R) where R is a reference unit set in configuration; default R = 10 miles. Validate R against MedFlex's actual geographic footprint before build." Why: without a defined formula, every builder chooses their own, and different choices make the spec untestable.

- **Rule 7 threshold:** Original: "all other ranking factors for that nurse are within 10% of the next-ranked candidate." Should say: "the candidate's composite raw_score is within 10% of the next-ranked candidate's composite raw_score, calculated as (score_above - score_below) / score_above ≤ 0.10." Why: "all other ranking factors" sounds precise but requires a comparison method that the spec does not define.

- **Error handling — system availability:** Original: "CRM unavailable — apply rule 8 for all candidates; log data_source_unavailable; proceed." Should say: the same, plus: "Function signature must include `crm_available: bool` and `compliance_system_available: bool` parameters. When False, apply the specified fallback. Without these parameters, error paths cannot be implemented." Why: error handling rules that depend on runtime system state are unimplementable without a corresponding input.

- **pool_exhausted escalation payload:** Original: "include list of excluded candidates and exclusion reasons in escalation payload." Should say: "RankingResult must include an `excluded_candidates: list[ExcludedCandidate]` field populated when escalation_type is POOL_EXHAUSTED. Each ExcludedCandidate includes nurse_id and exclusion_reason (enum: IN_ACTIVE_OUTREACH, RECENT_NO_SHOW)." Why: the spec requires data in the payload that the output type does not define, making the requirement undeliverable as written.
