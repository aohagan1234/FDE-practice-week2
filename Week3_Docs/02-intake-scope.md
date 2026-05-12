# D2 — Engagement Intake & Scope
**MedFlex Engagement | Discovery: 2026-05-12**

---

## Business context

MedFlex is a 200-person healthcare staffing agency operating across 5 US states, matching travel nurses to hospital shift requests through 8 manual coordinators who collectively make ~960 matching decisions per day. This engagement exists because the current manual process cannot scale to meet the CEO's board-level revenue growth mandate: the coordination bottleneck is the ceiling on revenue, and two previous AI projects (chatbot, recommendation engine) failed to remove it.

---

## Stakeholder map

| Name / Role | What they care about | Their influence on this project |
|---|---|---|
| Marcus Reyes (CEO) | Revenue growth; board confidence; 10x capacity without 10x headcount | Primary decision-maker; approves scope, accepts or rejects deliverables; sceptical after two failed AI projects |
| Kim (lead coordinator, not in session) | Day-to-day matching workflow; accuracy of nurse availability data; managing exception cases | Defines how matching actually runs in practice; availability data flows through her; key for lived-process validation |
| Aaron (IT, not in session) | Internal systems; CRM; portal architecture; API availability | Determines what data the agent can access; API access for CRM, compliance system, and availability portal unconfirmed |
| Linda (compliance, not in session) | Credential accuracy; state regulatory requirements; quarterly update cadence | Defines credential data structure and update frequency; credential currency gap is a plausible mismatch driver but root-cause attribution is unconfirmed — Marcus could not identify the breakdown; must be validated with Linda before the credential validation step in D3 is treated as the primary mismatch fix |
| 8 coordinators | Reduced manual workload; recommendations they can trust | Adoption gatekeepers — the recommendation engine failed because coordinators did not trust it; agent design must address this |
| Hospital clients | Right nurse confirmed quickly; better than competitor agencies | Satisfaction survey data is the only current mismatch signal; their switching risk drives urgency |
| Nurses (travel nurses) | Matched to appropriate shifts; confirmed commitments | Their availability and response behaviour drives fill time; no-shows partly caused by double-booking with competitors |

---

## Constraints

- 8 weeks to demonstrable, measurable results (board-level confidence required; MVP definition is FDE's to propose)
- 5-state US region: credential requirements vary by state; agent must apply per-state rules, not a single national standard
- Credential data maintained on quarterly cadence by compliance team — real-time credential status cannot be assumed without a validated API
- CRM/internal portal API access not confirmed — Aaron (IT) must verify before architecture is finalised
- Compliance team (not coordinators) owns credential verification — agent cannot modify credential records; it can only read and flag
- Nurse availability is split across a portal and manual phone updates — availability data must be treated as indicative, not authoritative, until a single source of truth is confirmed with Kim
- No changes to hospital-facing channels (email/phone/portal) in scope — hospitals continue submitting requests as they do today
- No changes to nurse-facing channels in scope — nurses continue to be reached by phone, SMS, or email

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Availability data is stale at placement time (portal + manual phone updates create lag) | H | H | Agent treats portal availability as indicative; confirms via outreach before committing a placement |
| Credential data lag (quarterly update cadence creates placement window for lapsed credentials) — unconfirmed as primary mismatch driver; Marcus could not confirm root-cause breakdown | M | H | Agent checks credential status at placement time; excludes candidates with credentials last verified >90 days; flags to compliance team. Likelihood downgraded from H to M until Linda confirms credential currency is a material contributor to the 7% mismatch rate |
| Coordinator distrust of agent recommendations (recommendation engine failed for same reason) | H | M | Agent must surface ranking rationale per candidate — not just a ranked list; coordinators must see why, not just who |
| CRM / compliance system API access unavailable or restricted | M | H | Engage Aaron in week 1 to confirm; design agent with abstracted data layer so API stubs can be replaced without architecture change |
| State-level credential variation causes incorrect eligibility decisions | M | H | Linda (compliance) provides credential-to-facility-type mapping per state before build; agent applies it but does not interpret it |
| No pre-placement mismatch signal — mismatches currently only known post-shift | H | H | Add pre-placement credential validation step; flag best-fit matches as partial match with explicit reason shown to coordinator |
| Agent accuracy insufficient for coordinator trust in first 8 weeks | M | M | Wave 1 targets measurable fill-time reduction, not full autonomy; coordinator remains in approval loop throughout |
| Nurses double-booked with competitor apps (contributing to 12% no-show rate) | M | M | Parallel outreach gets confirmation faster; confirmed nurses are removed from the available pool immediately |

---

## MVP scope — IN

- **Job order intake parsing**: extract structured data (facility, shift date/time, specialism, required credentials) from unstructured shift requests arriving by email, phone note, or portal
- **Candidate eligibility pre-filter**: rule-based filter on three deterministic criteria — credentials match, availability (portal state), proximity within facility's region
- **Candidate ranking**: agent-led ranking of eligible candidates with stated rationale per candidate (why this nurse for this shift)
- **Parallel outreach**: contact top-ranked candidates simultaneously via existing channels (phone, SMS, email); do not wait for one response before contacting the next
- **Response tracking and escalation**: track nurse responses against a target confirmation window; escalate to coordinator if no confirmation within threshold
- **Coordinator confirmation gate**: surface confirmed match to coordinator with agent rationale before hospital is notified; coordinator approves or overrides
- **Hospital confirmation notification**: send confirmation to hospital on coordinator approval via email

---

## MVP scope — OUT

| Out of scope | Reason |
|---|---|
| Hospital-facing portal for shift submission | Named explicitly in brief; hospitals submit by email/phone/portal today and this engagement does not change that channel |
| Nurse-facing mobile app | Named explicitly in brief; separate product surface requiring separate discovery with nurses |
| Pricing engine and margin optimisation | Named explicitly in brief; pricing remains MedFlex's existing process |
| Continuing-education renewal automation for nurses | Named explicitly in brief; nurse development is a separate domain from shift matching |
| Credential renewal reminders to nurses | Compliance team's responsibility; agent reads credential state but does not manage the renewal lifecycle |
| Hospital sales and business development | Marcus confirmed this is the growth team's scope; operational efficiency is the agent's scope |
| Post-shift mismatch analysis and root-cause attribution | Requires historical data pipeline separate from the real-time matching workflow; deferred to Wave 2 |
| Coordinator NPS / internal satisfaction tracking | Discovery confirmed pain point is fill time; coordinator experience improvement is a downstream effect, not a primary agent goal |
| Multi-state regulatory interpretation | Agent applies compliance team's credential mapping per state; it does not interpret ambiguous regulatory requirements — those are escalated to Linda |
