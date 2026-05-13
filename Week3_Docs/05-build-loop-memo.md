# D5 — Build-Loop Response Memo
**MedFlex Engagement | Capability: Candidate Ranking**

---

## Signal summary

| Signal | Classification | What the spec failed to say (if applicable) | What must change |
|---|---|---|---|
| Rule 7 "within 10%" checks composite raw_score, not individual factors | Spec gap | Spec says "all other ranking factors… within 10%" without defining whether this means composite score or each factor independently — two different calculations | Clarify rule 7: specify that the 10% threshold applies to composite raw_score, not per-factor comparison |
| No mechanism to distinguish CRM unavailable from response_rate simply absent | Spec gap | Error handling table requires `data_source_unavailable` escalation when CRM is down, but median imputation when data is missing — two different required responses with no input parameter to distinguish them | Add `crm_available: bool` parameter to function signature; current implementation always imputes regardless of cause |
| No function parameter for compliance system availability | Spec gap | Error handling rule "hold ranking; trigger data_source_unavailable escalation; do not rank candidates with unverifiable credential status" requires the function to know the system is unavailable — the current signature has no way to receive this signal | Add `compliance_system_available: bool` parameter; without it the error path is unimplementable as specified |
| Proximity normalization formula `1/(1 + miles/10)` not specified in spec | Unjustified implementation choice | Spec names proximity as a ranking factor but defines no scoring formula — the 10-mile reference unit is a builder choice that materially affects rankings for pools where all nurses are within 5 miles vs. spread over 50 | Add proximity scoring definition to decision rules: either define the formula or specify normalise-within-pool |
| `pool_exhausted` escalation payload has no `excluded_candidates` field | Spec gap | Error handling requires "include list of excluded candidates and exclusion reasons in escalation payload" but `RankingResult` has no field for this | Add `excluded_candidates` list to `RankingResult`; populate on pool_exhausted escalation |

---

## Patterns identified

- Three of five signals are spec gaps in error handling — the spec defines what the agent does when external systems are unavailable (CRM, compliance system, fill cycle state) but the function signature accepts none of these availability signals as inputs. Error handling requirements that depend on runtime system state cannot be implemented without a corresponding parameter — the spec wrote the "what" without the "how it gets told."
- The proximity normalization gap is the same failure mode seen in the Cascade Public Libraries exercise (Signals 1 and 7): a decision left open in the spec that the builder resolves with a reasonable default, making the output correct-looking but unverifiable against the requirement. Naming a factor in a decision rule is not the same as specifying it.

---

## Implications for my own specs

Every error handling row in a capability spec that references an external system state — "if CRM unavailable," "if compliance system unavailable" — requires a corresponding input parameter in the function signature; without it the error path exists only in the spec document, not in code. Every factor named in a decision rule must be accompanied by a scoring or comparison definition, not just a weight — "proximity (primary)" is half a rule until the normalization is specified.
