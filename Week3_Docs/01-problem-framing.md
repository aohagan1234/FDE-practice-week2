# D1 — Problem Framing & Success Metrics
**MedFlex Engagement | Discovery: 2026-05-12**

---

## Scenario summary

**Client:** MedFlex — healthcare staffing agency, 200 employees, 5-state US region. B2B with hospital systems; B2C with travel nurses. Of the 200 employees, 8 are coordinators responsible for manually matching nurses to hospital shift requests.

**Stakeholder:** Marcus Reyes, CEO. Series B closed. Board mandate: significant revenue growth within 24 months. Two prior AI projects failed (chatbot rejected by hospital staff; recommendation engine unused by coordinators).

**Engagement brief:** *"10x the business without 10x-ing the coordinators"* — in 8 weeks.

| Metric | Current state | Target |
|---|---|---|
| Coordinators | 8, matching manually | Flat headcount |
| Matching decisions per coordinator per day | ~120 | ~10x volume, same headcount |
| Average time to fill a shift | 4.2 hours | <1 hour |
| Mismatch rate (wrong credentials for facility) | 7% | <2% |
| No-show rate | 12% | <7% |

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

The 8-week MVP does not need to achieve 10x volume — it must demonstrate the architecture that enables it. A pilot demonstrating <1h fill time, ≥80% first-recommendation acceptance rate, and parallel outreach on 20–30 shifts is sufficient to validate the design.

---

## Success metrics

| Stakeholder | What success looks like | Measurable target | How it is measured |
|---|---|---|---|
| MedFlex (CEO / board) | Operational capacity scales without proportional headcount growth; board confidence in revenue trajectory | Fill volume per coordinator increased ≥3x within 8 weeks; coordinator headcount held flat | Shifts filled per coordinator per day, tracked in internal CRM |
| MedFlex coordinators | Routine matching is handled by the agent; coordinators spend time on exceptions and relationship decisions, not sequential phone calls | Fill time from request receipt to nurse confirmation: 4.2h → <1h | Average time-to-fill per shift, logged in CRM |
| Hospital clients | Right nurse for every shift; confirmed faster than competitor agencies | Mismatch rate: 7% → <2%; confirmation time: <1h | Post-shift satisfaction survey mismatch flag; time-to-confirmation log |
| Nurses | Matched to appropriate shifts; fewer last-minute cancellations from coordinators discovering a credential problem | No-show rate: 12% → <7% (agent pre-validates before confirming; reduces unwanted placements) | No-show rate tracked per nurse in coordinator system |
| MedFlex compliance team | Credential gaps surfaced before placement, not after | Zero placements confirmed with credentials last verified >90 days; lapsed credentials flagged to compliance team on detection | Compliance system audit log; mismatch attribution report |

---

## How each metric is achieved

| Metric | Mechanism | Where demonstrated | Dependency / caveat |
|---|---|---|---|
| Fill time 4.2h → <1h | Parallel outreach replaces sequential outreach. The agent contacts multiple candidates simultaneously; the coordinator is removed from the outreach loop and touches the fill cycle only at intake review and final approval (~5 min active time vs. ~20 min today). The waiting time between sequential contact attempts — which is where the 4.2 hours comes from — is eliminated. | D3 before/after lifecycle diagrams; D3 parallel outreach step (Agent-led); ADR 1 (coordinator gate at final step only) | Assumes fill time is predominantly waiting time, not decision complexity — Low confidence; to validate with Kim |
| Fill volume per coordinator ≥3x | At ~5 min coordinator active time per fill (approval gate only), a coordinator can supervise ~96 fills/day across an 8-hour day, vs. the current ~20 fills where they are actively engaged throughout each cycle. This is a ~4-5x capacity increase, which supports the ≥3x Wave 1 target. | D1 architectural requirements table; ADR 1 | Wave 1 target only. 10x requires ≥80% autonomous resolution rate — not achieved until Wave 2 (see D3 Wave 1/Wave 2 scope) |
| Mismatch rate 7% → <2% | Two mechanisms: (1) pre-placement credential recency check catches nurses with lapsed or stale credentials before confirmation; (2) structured job order intake parsing captures hospital requirements more precisely, reducing ambiguous matches that become mismatches. | D3 credential validation step; D3 intake parsing step; ADR 2 | **Low confidence.** Root cause of the 7% is unconfirmed — Marcus could not identify the breakdown. If the mismatch is driven by hospital expectation gaps rather than stale credentials, mechanism (1) will not move this metric and mechanism (2) becomes the primary lever. Must validate with Linda before this target is treated as achievable from the current architecture. |
| No-show rate 12% → <7% | Two mechanisms: (1) parallel outreach secures nurse confirmation faster, closing the window in which a nurse can be double-booked by a competitor before MedFlex confirms — Marcus confirmed that some no-shows are nurses who accepted a competitor's booking first; (2) pre-placement credential validation prevents placements where the nurse cannot legally fulfil the shift, removing a subset of no-shows caused by nurses declining on arrival. The <7% target assumes approximately 5 percentage points of the 12% are preventable through faster confirmation and pre-placement validation. Genuine emergencies and personal cancellations remain outside the agent's control. | D3 parallel outreach step; D3 credential validation step; D3 no-show backfill step | Assumes a meaningful share of no-shows are caused by slow confirmation (competitor double-booking) — this was inferred from Marcus's comment about competitors, not directly measured. The specific 5pp reduction is an estimate; actual figure will only be known after pilot data is collected. |
| Zero stale-credential placements | Credential recency check runs at placement time (after nurse confirms, before coordinator approves). Candidates with credentials last verified >90 days or with a lapsed status are excluded from confirmation and flagged to the compliance team. Other candidates in the pool are not blocked. | D3 credential validation step; ADR 2 | Requires compliance system API to support real-time per-nurse queries — Low confidence; to validate with Aaron. If API is unavailable, falls back to compliance team manual verification on a 2-hour SLA. |
