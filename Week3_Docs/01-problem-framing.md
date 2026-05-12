# D1 — Problem Framing & Success Metrics
**MedFlex Engagement | Discovery: 2026-05-12**

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
