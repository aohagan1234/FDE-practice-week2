# D1 — Problem Framing & Success Metrics
**MedFlex Engagement | Discovery: 2026-05-12**

---

## Scenario summary

**Client:** MedFlex — healthcare staffing agency, 200 employees, 5-state US region. B2B with hospital systems; B2C with travel nurses. Of the 200 employees, 8 are coordinators responsible for manually matching nurses to hospital shift requests.

**Stakeholder:** Marcus Reyes, CEO. Series B closed. Board mandate: significant revenue growth within 24 months. Two prior AI projects failed (chatbot rejected by hospital staff; recommendation engine unused by coordinators).

**Engagement brief:** *"10x the business without 10x-ing the coordinators"* — in 8 weeks.

| Metric | Current state | Target | Timeframe |
|---|---|---|---|
| Coordinators | 8, matching manually | Flat headcount | Ongoing |
| Matching decisions per coordinator per day | ~120 | ~10x volume, same headcount | Wave 2 (post-MVP) |
| Average time to fill a shift | 4.2 hours | <1 hour | 6-week MVP pilot |
| Mismatch rate (wrong credentials for facility) | 7% | <2% | Wave 2 (post-MVP) |
| No-show rate | 12% | <7% | Wave 2 (post-MVP) |

---

## What is actually broken

- The matching workflow is entirely manual and sequential. Coordinators receive unstructured shift requests across email, phone, and portal, then manually check credentials, availability, and proximity before contacting nurses one at a time. The 4.2-hour fill time is waiting time, not decision time — the bottleneck is sequential outreach, not coordinator judgment.

- There is no pre-placement validation of credential fit. Mismatches (7%) are detected post-shift through hospital satisfaction surveys, not at the moment of placement. When no perfect match exists, MedFlex proposes a best-fit nurse without flagging to the hospital that it is not an exact match — this undisclosed substitution is a direct driver of the mismatch rate and the trust erosion with hospital clients.

- Availability and credential data are unreliable at the moment of placement. Nurse availability is split across a portal and ad-hoc phone updates (coordinators and Kim manually update). Credentials are maintained on a quarterly compliance cadence — creating a window where a nurse with a lapsed credential remains on the active roster and can be placed. Both introduce data lag that produces incorrect matches even when the coordinator follows the correct process.

---

## What "10x without 10x-ing" requires architecturally

Current ceiling: 8 coordinators × 120 decisions/day = **960 shift-fill cycles/day**. 10x revenue without headcount growth cannot be achieved by making coordinators faster — the math does not work.

| Scenario | Fill cycles/day | Coordinator active time/fill | Result |
|---|---|---|---|
| Current state | 960 | ~20 min (researching, calling sequentially, chasing) | Coordinator is the bottleneck |
| Agent assists (coordinator still in loop per step) | 960 | ~10 min | ~2x capacity — not 10x |
| Agent autonomous on clean cases (coordinator approves only final placement) | 9,600 | ~5 min per approval | 10x capacity with flat headcount — if ≥80% of fills are clean |

For the 10x target to be architecturally achievable, the agent must satisfy four requirements:

1. **Autonomous resolution rate ≥80%** — the agent resolves clean cases (exact credential match, portal availability confirmed, nurse responds within window) end-to-end, routing only exceptions and final approval to the coordinator.
2. **Intake to first outreach in <15 minutes** — the coordinator cannot sit between request receipt and nurse contact. The agent must parse and initiate outreach without waiting for coordinator review of each job order.
3. **Concurrent fill cycle capacity ≥9,600** — a synchronous, sequential agent (one fill at a time) cannot reach 10x volume. The agent must manage all active fill cycles in parallel, independently. Coordinators review a queue, not individual cycles.
4. **Coordinator active time <5 minutes per fill** — releasing coordinator capacity for the higher volume requires removing them from all steps except the final approval gate.

The 6-week MVP does not need to achieve 10x volume — it must demonstrate the architecture that enables it. A pilot demonstrating <1h fill time, ≥80% first-recommendation acceptance rate, and parallel outreach on 20–30 shifts is sufficient to validate the design.

---

## Success metrics

| Stakeholder | What success looks like | Measurable target | How it is measured |
|---|---|---|---|
| MedFlex (CEO / board) | Operational capacity scales without proportional headcount growth; board confidence in revenue trajectory | Fill volume per coordinator increased ≥3x within 6 weeks; coordinator headcount held flat | Shifts filled per coordinator per day, tracked in internal CRM |
| MedFlex coordinators | Routine matching is handled by the agent; coordinators spend time on exceptions and relationship decisions, not sequential phone calls | Fill time from request receipt to nurse confirmation: 4.2h → <1h | Average time-to-fill per shift, logged in CRM |
| Hospital clients | Right nurse for every shift; confirmed faster than competitor agencies | Mismatch rate: 7% → <2%; confirmation time: <1h | Post-shift satisfaction survey mismatch flag; time-to-confirmation log |
| Nurses | Matched to appropriate shifts; fewer last-minute cancellations from coordinators discovering a credential problem | No-show rate: 12% → <7% (Wave 2 target; Wave 1 mechanism is faster confirmation via parallel outreach only — pre-placement credential validation deferred to Wave 2) | No-show rate tracked per nurse in coordinator system |
| MedFlex compliance team | No increase in credential-related compliance exposure during pilot | Compliance team continues operating under current process during Wave 1 pilot; credential recency check at placement deferred to Wave 2 pending Linda's validation that stale credentials are a material mismatch driver | Compliance team confirms no new credential-related incidents during pilot period |

---

## How each metric is achieved

| Metric | Mechanism | Where demonstrated | Dependency / caveat |
|---|---|---|---|
| Fill time 4.2h → <1h | Parallel outreach replaces sequential outreach. The agent contacts multiple candidates simultaneously; the coordinator is removed from the outreach loop and touches the fill cycle only at intake review and final approval (~5 min active time vs. ~20 min today). The waiting time between sequential contact attempts — which is where the 4.2 hours comes from — is eliminated. The agentic component of outreach is not the sending (deterministic) but the real-time strategy adaptation: when pool is shallow, urgency is high, and some candidates are already in outreach for a concurrent fill, the agent reads live fill cycle state and adapts — contacting remaining available candidates immediately and escalating in parallel rather than waiting. A rule with no access to concurrent fill state cannot make this call. | D3 before/after lifecycle diagrams; D3 parallel outreach step (Agent-led + human oversight — agentic component is urgency-adaptive strategy, not message sending); ADR 1 (coordinator gate at final step only); ADR 2 (agentic ranking with stated rationale builds coordinator trust in recommendations) | Low confidence — to validate with Kim. Three risks to the <1h target: (1) If fill time is partly decision work, impact depends on type — availability verification is the critical gap; if coordinators call nurses to confirm availability before shortlisting because portal data is unreliable, the agent inherits the same lag. (2) Nurse response time is the dominant time component — if nurses routinely take longer than 40 minutes to respond via any channel, the target is missed regardless of agent processing speed; channel choice and time-of-day patterns affect this materially (validate with pilot data from first 20–30 shifts). (3) Coordinator queue monitoring — if coordinators take 15–20 minutes to review a confirmation at high fill volume, the target is missed even when nurse response is fast; queue prioritisation by shift urgency is required (validate with Kim's team during workflow design). |
| Fill volume per coordinator ≥3x | At ~5 min coordinator active time per fill (approval gate only), a coordinator can supervise ~96 fills/day across an 8-hour day, vs. the current ~20 fills where they are actively engaged throughout each cycle. This is a ~4-5x capacity increase, which supports the ≥3x Wave 1 target. The candidate ranking step is the specific agentic decision that makes this sustainable: the agent adapts factor weighting per job order context (credential specificity dominates for specialist shifts; response rate and proximity dominate for urgent same-day fills) and produces a stated rationale per candidate. A fixed-weight sort produces the same ranking regardless of context and was already rejected by coordinators as untrustworthy. | D1 architectural requirements table; ADR 1; ADR 2 | Wave 1 target only. 10x requires ≥80% autonomous resolution rate — not achieved until Wave 2 (see D3 Wave 1/Wave 2 scope) |
| Mismatch rate 7% → <2% | Wave 1 mechanism: structured job order intake parsing captures hospital requirements more precisely, reducing ambiguous matches that become mismatches. Wave 2 mechanism (pending Linda validation): credential recency check at placement catches nurses with lapsed or stale credentials before confirmation. | D3 intake parsing step (LLM-assisted extraction, not agentic reasoning — handles input variability a deterministic parser cannot); D3 Wave 1/Wave 2 scope | **Wave 2 target.** Root cause of the 7% is unconfirmed — Marcus could not identify the breakdown. Credential recency check deferred pending Linda confirming stale credentials are a material driver. Wave 1 intake parsing alone is unlikely to move the mismatch rate to <2%; the target is achievable only when both mechanisms are in place. |
| No-show rate 12% → <7% | Wave 1 mechanism: parallel outreach secures nurse confirmation faster, closing the window in which a nurse can be double-booked by a competitor before MedFlex confirms — Marcus confirmed that some no-shows are nurses who accepted a competitor's booking first. Wave 2 mechanism (deferred): credential validation prevents placements where the nurse cannot legally fulfil the shift, removing a subset of no-shows caused by nurses declining on arrival. | D3 parallel outreach step; D3 Wave 1/Wave 2 scope | **Wave 2 target.** Wave 1 parallel outreach alone addresses the competitor double-booking subset; the credential-related subset is not addressed until Wave 2. The specific 5pp reduction to reach <7% assumes both mechanisms; Wave 1 data will establish how much faster confirmation alone moves the rate. |
| Zero stale-credential placements | **Wave 2 only.** Credential recency check at placement time deferred pending Linda's confirmation that stale credentials are a material driver of the 7% mismatch rate and Aaron's confirmation of a queryable compliance system API. During Wave 1, the compliance team continues operating under its current quarterly cadence. Known risk: a small compliance exposure exists during the pilot — accepted as a condition of the 6-week timeline. | D3 Wave 1/Wave 2 scope | Hard dependencies before Wave 2 build: (1) Linda validates stale credentials as mismatch driver; (2) Aaron confirms real-time compliance API. Neither confirmed at discovery. |

---

## Delivery timeline

### Wave 1 — 6-week pilot

| Weeks | Activity | Gate |
|---|---|---|
| Week 1 | Aaron confirms CRM and nurse portal APIs; Kim validates fill time breakdown and availability data reliability; Linda consulted on credential mismatch root cause | If APIs unconfirmed by end of week 1, timeline slips — this is the hard dependency |
| Weeks 2–5 | Build: LLM-assisted intake parser, deterministic eligibility filter, candidate ranking agent, parallel outreach automation, response tracking scheduler, coordinator approval interface, hospital notification | Integration with CRM and outreach channels (SMS, email, phone) |
| Week 6 | Pilot on 20–30 live shifts; fill time and coordinator acceptance rate tracked | Board presentation: early directional data, not statistically significant proof |

**Pilot selection criteria for week 6:**

The 20–30 shifts are a structured sample, not a random cross-section of all fills. Selection criteria limit exposure while producing meaningful data:

| Criterion | Scope | Rationale |
|---|---|---|
| Coordinators | 1–2 from Kim's team | Limits blast radius; keeps the pilot controllable and debriefable |
| Shift type | Standard fills with >24h lead time, known facility types, standard credentials only | Excludes urgent same-day fills and specialist high-acuity shifts where a failure carries the highest relationship risk |
| Hospital clients | 2–3 accounts with established MedFlex relationships | Ensures a slower or failed fill during the pilot does not immediately cost a contract |
| Coordinator role | Approves every placement, as per Wave 1 design | Agent never confirms with the hospital unilaterally during the pilot |

**What is measured across the 20–30 shifts:**
- Average fill time from intake to hospital confirmation
- First-recommendation acceptance rate: did the coordinator approve the agent's top-ranked nurse, or override?
- Escalation path frequency: how many fills hit each escalation type (no confirmation within window, pool exhausted, parsing ambiguity)

**Realistic results at week 6:**

| Outcome | Realistic range | What determines it |
|---|---|---|
| Fill time | 40 min–2 hours | Nurse response time (dominant factor) and coordinator queue monitoring; <1h if both assumptions hold |
| Fill volume per coordinator | ≥3x | Achievable if coordinators are genuinely released from the outreach loop |
| Coordinator acceptance rate | Unknown until pilot | First-recommendation acceptance rate is the leading indicator for Wave 2 readiness |
| Board deliverable | Architecture demonstrated on live shifts | 20–30 shifts shows the design works; not enough to prove 10x capacity |

---

### Wave 2 — condition-triggered, estimated months 5–8

Wave 2 has no fixed start date. It is triggered when Wave 1 data meets both conditions: coordinator approval adds <30 minutes to fill time consistently **and** agent first-recommendation acceptance rate ≥90% over 60 operational days.

| Phase | Timing | Activity |
|---|---|---|
| Wave 1 operational | Months 2–5 | Run live; collect 60 operational days of acceptance rate and approval time data |
| Wave 2 trigger assessment | Month 5 | Review data against both trigger conditions; if not met, Wave 2 is delayed until conditions are satisfied |
| Wave 2 build | Months 5–7 | Credential recency check (requires Aaron's compliance API confirmation); no-show backfill agent; pre-shift mismatch check; ≥80% autonomous resolution path for clean cases |
| Wave 2 live | Month 7–8 | Full autonomous resolution for clean cases; coordinator approves exceptions only |

**Realistic results at Wave 2:**

| Outcome | Target | Dependency |
|---|---|---|
| Autonomous resolution rate | ≥80% of fills | Clean case definition must hold in production: exact credential match + availability confirmed + zero no-show history |
| Fill time | <1 hour (maintained) | Nurse response time and coordinator queue assumptions carry forward |
| Mismatch rate | 7% → <2% | Only if Linda confirms stale credentials are a material driver and recency check is built |
| No-show rate | 12% → <7% | Both mechanisms in place: faster confirmation (Wave 1) + credential validation (Wave 2) |
| Coordinator headcount | Flat | 10x capacity with same headcount — achievable only if ≥80% autonomous resolution holds |

**Risk to board mandate:** Wave 2 going live at month 7–8 leaves 16–17 months of operation within the 24-month revenue growth window — sufficient if Wave 1 trigger conditions are met at month 5. If Wave 1 data does not meet trigger conditions, Wave 2 is delayed and the operational window before the board's deadline compresses.
