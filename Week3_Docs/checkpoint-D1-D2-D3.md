# Decision Checkpoint — D1, D2, D3
**MedFlex Engagement | Run after: 2026-05-12**

---

## Critical decisions

---

**Decision 1: The 4.2-hour fill time is predominantly waiting time (sequential outreach), not decision time.**

**Assumed because:** The scenario states coordinators make ~120 decisions/day across an 8-hour shift — roughly one decision every 4 minutes — which suggests each individual decision is fast. Marcus could not give a breakdown of where the 4.2 hours goes and deferred to Kim. The architecture targets parallel outreach as the primary lever.

**If this is wrong:** If the 4.2 hours is mostly coordinators spending 20–40 minutes researching each complex case (verifying credentials, chasing availability updates, interpreting hospital requirements), then parallel outreach is the wrong fix. The bottleneck would be decision complexity, not outreach sequencing. The agent would need to own the research and decision, not just the execution.

**Confirm this with me:** Of the 4.2 hours, is most of the time waiting for nurse responses, or is most of it a coordinator actively working the case — checking credentials, assessing fit, tracking down availability?

---

**Decision 2: The 7% mismatch rate is primarily a credential or skills gap at placement time.**

**Assumed because:** Ann asked Marcus whether credentials being out of date could be a factor. Marcus said "it eventually comes down to skills not being a match... human error, credential update error... there may be several things." The architecture responds to this with real-time credential validation and pre-placement ambiguity flagging. The best-fit-without-disclosure finding from the call also directly contributes.

**If this is wrong:** If the 7% is mostly hospital expectation mismatch (the nurse's credentials were fine but the hospital wanted a different specialism, bedside manner, or seniority level), then pre-placement credential validation will not move the mismatch rate. The fix would be better job order intake — capturing hospital preferences more precisely — not credential checking. The entire compliance-validation thread in D3 would be addressing the wrong root cause.

**Confirm this with me:** Of the mismatch cases MedFlex is aware of, what is the most common reason — wrong credential type, credential that lapsed, hospital expectation the nurse couldn't meet, or something else?

---

**Decision 3: The coordinator approves the final placement but does not approve intermediate steps (outreach list, shortlist).**

**Assumed because:** ADR 1 chose this to balance speed with trust-building. The agent runs intake, filtering, ranking, and outreach autonomously; the coordinator reviews only the confirmed match before the hospital is notified.

**If this is wrong:** If coordinators require visibility of and approval over the outreach list before the agent contacts any nurse, the agent cannot parallelise outreach without coordinator involvement — reintroducing a human bottleneck before the time-critical step. If coordinators insist on seeing the shortlist before anyone is contacted, fill time will not reach <1h.

**Confirm this with me:** Would coordinators accept the agent contacting nurses directly without first approving who gets contacted, or would they require seeing and approving the shortlist first?

---

**Decision 4: Real-time per-nurse credential status queries are technically possible.**

**Assumed because:** Marcus said "I think there is an API somewhere. I don't know where it is." ADR 2 is built on the assumption that Aaron can confirm and provide API access to the compliance system. The entire credential-recency validation step depends on this.

**If this is wrong:** If Aaron confirms there is no queryable API for the compliance system — only the quarterly batch export — real-time credential checks are impossible. The agent can only read stale batch state, which reintroduces the credential lag the architecture was designed to close. ADR 2's fallback (compliance team on a 2-hour SLA) becomes the primary design, which adds a human to the critical path and likely breaks the <1h fill time target for any credential-flagged case.

**Confirm this with me:** Has Aaron confirmed that the compliance system supports a real-time per-nurse credential status query? If not, this must be the first technical question in Week 1.

---

**Decision 5: Coordinators do not verify credentials themselves during matching — they rely on what the compliance system holds.**

**Assumed because:** Marcus said clearly: "The coordinators don't do that. It's the job of the compliance team." This was in response to Oleksandra's question about state-level credential compliance.

**If this is wrong:** If coordinators currently do any credential spot-checking as part of making a match (e.g., a quick manual check of a state database when something looks off), there is a workflow step missing from D3's delegation map. The agent would need to replicate that step, not just read the compliance system's state.

**Confirm this with me:** Do coordinators ever manually look up credential status during a match, or do they trust entirely what is already in the system from the compliance team?

---

**Decision 6: Outreach confirmation (nurse says yes) is a reliable proxy for actual availability.**

**Assumed because:** D3 treats portal availability as indicative and uses outreach response as the safeguard. If a nurse confirms via SMS or email, the placement proceeds.

**If this is wrong:** If nurses routinely confirm shifts and then no-show because they were double-booked elsewhere or cancelled without notifying MedFlex — meaning the 12% no-show rate includes nurses who said yes — then outreach confirmation is not a reliable safeguard. The agent would be confirming placements based on responses that do not predict show-up.

**Confirm this with me:** Of the 12% no-shows, what fraction involves nurses who had confirmed the shift in advance? If most no-shows are confirmed-then-cancelled, the architecture needs a hard-confirmation step with a formal commitment mechanism, not just an outreach reply.

---

## Agentic step validation

---

**Step:** Job order intake — parse unstructured shift request into structured job order

**Marked as:** Agent-led + human oversight

**The case for an agent:** Shift requests arrive by email, phone note, and portal in variable formats. A deterministic parser cannot reliably extract facility type, shift time, specialism, and credential requirements from free-text email or dictated phone notes.

**Verdict:** Agent justified — with a caveat. If the portal submission form is already structured (dropdown fields, date pickers), portal-sourced requests should be processed by a deterministic extractor, not the agent. The agent is only justified for the unstructured channels (email, phone notes). The spec should distinguish these two paths explicitly, or the agent is applied where a rule would work.

---

**Step:** Candidate ranking — order eligible candidates with rationale

**Marked as:** Fully Agentic

**The case for an agent:** The right ranking depends on at least six context-dependent factors simultaneously (credential specificity, proximity, hospital preferences, response rate, no-show history at this facility, current workload). No fixed rule can weight these correctly across all shift types and hospital relationships.

**Verdict:** Agent justified. The prior recommendation engine failed because it used a fixed scoring algorithm coordinators did not trust. The agent must reason over the full context per job order and explain its reasoning — that explanation is what the recommendation engine lacked and is what builds coordinator trust over time.

---

**Step:** Parallel outreach — contact top-ranked candidates simultaneously

**Marked as:** Agent-led + human oversight

**The case for an agent:** Deciding how many candidates to contact, via which channel, and in what sequence requires reasoning over urgency, pool depth, channel preference, and expected response latency.

**Verdict:** Partially justified — needs tightening. The execution (sending the message) is a deterministic workflow. The "how many to contact" decision could be a configurable rule (e.g., always contact top 3 unless pool depth is <3, in which case contact all available). The genuinely agentic part is urgency-adaptive adjustment — if a shift starts in 2 hours, the agent should contact more candidates simultaneously and escalate faster than for a shift 48 hours out. The spec must distinguish what is a configurable rule from what requires real-time reasoning, or the agent will be applied to a deterministic decision unnecessarily.

---

**Step:** Credential validation at placement — check credential currency before confirming candidate

**Marked as:** Agent-led + human oversight

**The case for an agent:** For exact matches (credential A required / nurse has credential A, verified 30 days ago), this is deterministic. For ambiguous cases ("ICU-certified preferred" / nurse has "step-down ICU experience"), the agent reasons over credential detail, facility requirements text, and precedent from prior placements.

**Verdict:** Agent justified for the ambiguous case only. The exact-match case must be handled by a deterministic check (cheaper, faster, more reliable). The D4 spec must explicitly define the boundary: deterministic check runs first; if the result is ambiguous or the credential description does not map cleanly, the agent reasons over it. Applying the agent to the deterministic case is waste.

---

**Step:** No-show backfill — find replacement rapidly when a placed nurse no-shows

**Marked as:** Agent-led + human oversight

**The case for an agent:** Same as candidate ranking but with a time constraint and a reduced pool. The weighting of factors shifts under urgency (response rate and proximity become dominant); a rule cannot adapt to an unknown pool composition in real time.

**Verdict:** Agent justified. The combination of time pressure, reduced pool, and the need to adjust strategy based on how many candidates are still reachable makes a rule insufficient. The agent must reason over remaining pool state at the moment of backfill.

---

## What to do before D4

For each decision above: read it, answer the confirmation question, and confirm whether you agree, disagree, or cannot answer yet.

If you cannot answer — say so explicitly — that is the most important signal, because it means the assumption needs to be validated with Kim, Aaron, or Linda before D4 is written.

**Do not proceed to D4 until decisions 1, 3, and 4 are confirmed** — those three have the highest architectural consequence:
- Decision 1 determines whether parallel outreach is the right primary lever
- Decision 3 determines whether the coordinator gate placement is in the right place
- Decision 4 determines whether real-time credential validation is buildable at all
