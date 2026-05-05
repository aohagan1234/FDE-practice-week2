# Deliverable 3: Delegation Suitability Matrix — What Should the Agent Own?

**Organisation:** Aldridge & Sykes — HR Onboarding  
**Purpose of this document:** Not everything that *can* be automated *should* be. This document scores each task cluster against four questions, then assigns a delegation level — from "agent acts alone" to "human only." The scores make the reasoning transparent and auditable.

---

## The Four Questions We Score Against

For each cluster of related tasks, we ask:

| Question | What we're checking | Low score means… | High score means… |
|---|---|---|---|
| **How structured is the input?** | Is the data the agent needs complete and unambiguous? | Inputs are often missing or unclear | Inputs are always available and well-defined |
| **How predictable is the decision?** | Can a rule replace human judgment? | High judgment required; no clear rule | Fully rule-based; zero discretion needed |
| **How often do exceptions occur?** | What fraction of cases need special handling? | Frequent exceptions; agent often hits edge cases | Rare exceptions; agent can handle 95%+ of cases |
| **What's the cost of a mistake?** | If the agent gets it wrong, how bad is it? | Irreversible, legal, or high-cost error | Easily corrected; low financial or operational impact |

**Scoring:** Each dimension is rated 1–5. The three most important (input structure, decision predictability, tool coverage) are averaged to produce a suitability score. The higher the score, the more autonomy the agent can safely have.

---

## The Five Delegation Archetypes

| Archetype | Description | When to use |
|---|---|---|
| **Human Only** | Tacit knowledge, ethics, irreversibility | No suitable structure or automation path |
| **Human-led + Automation Support** | Tools accelerate execution; judgment stays human | Rule-bound tasks where human control is preferred |
| **Human-led + Agent Support** | Agent provides synthesis and recommendations | Complex analysis, research, decision support |
| **Agent-led + Human Oversight** | Execution delegated; supervision mandatory | High-volume structured decisions with human backstop |
| **Fully Agentic** | Autonomous within defined bounds | High-volume, structured, reversible, well-governed |

> **Implementation note:** "Fully Agentic" describes the governance model — the agent acts without per-case human review. The implementation may be a rule engine, a scheduled job, or an LLM depending on whether the task is deterministic or not. Both are correctly "Fully Agentic" if they execute autonomously within defined bounds. The technology choice (rules engine vs LLM) is an implementation detail, not an archetype distinction.

---

## Scoring: Each Task Cluster

### Summary (read this first)

| Cluster | Suitability Score | Delegation Level | One-line reason |
|---|---|---|---|
| 1. Deadline Calculation | 5.0 | **Fully Agentic** | High-volume, structured, reversible; autonomous arithmetic — implemented as rule engine |
| 2. Hire Type Classification | 2.3 | **Human-led + Agent Support** | Agent synthesises evidence from employment agreement text; human decides due to cascading risk |
| 3. Compliance Training Proposal | 3.3 | **Agent-led + Human Oversight** | LLM proposes from partial matrix matches; HR Ops approval mandatory before LMS write |
| 4. Buddy Matching | 3.0 | **Human-led + Automation Support** | Automation surfaces sorted candidates; team fit selection is human-only judgment |
| 5. IT Provisioning | 3.7 | **Fully Agentic** (main path) / **Agent-led + Human Oversight** (unmapped roles) | Dominant path: autonomous lookup + submit. Exception (~10%): LLM proposes nearest package; IT Manager approves |
| 6. Task Status Monitoring | 4.0 | **Fully Agentic** | High-volume (3,500+ events/year), structured, reversible; autonomous threshold poller |
| 7. I-9 Compliance Monitoring | 4.8 | **Fully Agentic** (mandatory) | Federal mandate; zero discretion; non-negotiable autonomous escalation |
| 8. Hold Decision | 2.0 | **Human Only** | Irreversible employment action; ethics and legal accountability |
| 9. Manager Handoff Notification | 4.6 | **Fully Agentic** | High-volume, structured, reversible; autonomous trigger and send |

The detailed scoring for each cluster follows.

---

## Delegation Suitability Scoring Matrix

### Major Task Clusters

#### Cluster 1: Task Deadline Calculation & Dependency Mapping (JtD 1, Zone 2)

| Dimension | Score | Rationale |
|---|---|---|
| **Input Structure** | 5 | Hire record has all required fields (start_date, hire_type); task registry is structured (offset_days, dependencies); zero ambiguity |
| **Decision Determinism** | 5 | Pure algorithmic: deadline = start_date + offset_days; dependencies are hardcoded in registry; zero judgment |
| **Exception Rate** | 5 | <1% of cases hit exceptions; almost all dates calculable; only edge case: offset_days = undefined (spec design issue) |
| **Tool Coverage** | 5 | All inputs available in HRIS or task registry (local config); no external API dependencies |
| **Risk/Reversibility** | 5 | Incorrect deadline is easily corrected by update; no impact if deadline is wrong for 1 hour; cost <$50 |
| **Suitability Score** | 5.0 | (5+5+5)/3 |
| **Delegation Archetype** | **Fully Agentic** | High-volume, structured, reversible, well-governed. Agent executes autonomously within defined bounds with no per-case human review. Implementation: rule engine / cron job (no LLM required — the task is fully deterministic). |

**Rationale for archetype:** Pure computation (`start_date + offset_days`). Executes autonomously at scale. No judgment, no exceptions, no risk of irreversible action. The implementation is a scheduled job; the governance model is fully agentic.

---

#### Cluster 2: Hire Type Classification & Intake Triage (JtD 1, Zone 1)

| Dimension | Score | Rationale |
|---|---|---|
| **Input Structure** | 3 | Hire record includes hire_type field but field is nullable. If NULL, structure is incomplete. Employment agreement may exist in multiple systems (offer letter, contract, email). Ambiguity at intake. |
| **Decision Determinism** | 2 | Deterministic IF hire_type is populated (EMPLOYEE or CONTRACTOR = binary). But if NULL or ambiguous (some hires may be dual-status), requires judgment. "Is this person truly a contractor or misclassified?" involves policy interpretation. |
| **Exception Rate** | 2 | ~5–10% of hires have hire_type ambiguity based on spec escalation frequency (HIRE_TYPE_AMBIGUOUS is defined as escalation trigger). If >5%, escalation rate is high. |
| **Tool Coverage** | 3 | Hire_type may be in HRIS, but may also require manual review of employment agreement in document system. Not fully automated data source. |
| **Risk/Reversibility** | 2 | Incorrect hire_type cascades: wrong compliance training, wrong task set (contractor doesn't need I-9). Downstream impact is medium ($500–$5,000 rework). Reversible but costly. |
| **Suitability Score** | 2.3 | (3+2+3)/3 |
| **Delegation Archetype** | **Human-led + Agent Support** | Agent provides synthesis and recommendations: for ambiguous cases (~10%), LLM reads employment agreement text and surfaces the clauses pointing to EMPLOYEE vs CONTRACTOR with a confidence score. Human reviews and decides. Clear cases (hire_type populated, unambiguous) are flagged and routed by automation without LLM involvement. |

**Rationale for archetype:** Too high-risk for the agent to decide — misclassification cascades into wrong task set, wrong compliance training, payroll errors. The agent's role is synthesis (reading unstructured contract text, surfacing evidence), not execution. Human retains the decision. Ambiguous path is part of the Phase 2 Proposal Router.

---

#### Cluster 3: Compliance Training Track Proposal (JtD 2, Zone 3)

| Dimension | Score | Rationale |
|---|---|---|
| **Input Structure** | 4 | Hire has role, location, hire_type (fields needed for matrix lookup). Compliance matrix is structured (table rows: hire_type, role, location, required_track). One ambiguity: role title variations (e.g., "Senior Consultant" vs. "Consultant") may not match exactly. |
| **Decision Determinism** | 3 | Deterministic IF exact match found in matrix (lookup = deterministic). But ~20–30% of cases match only partially (2 of 3 fields) or not at all (per assumption from spec: LOW confidence = no single row found). Partial matches require judgment: "Should we use the CONSULTANT track or escalate?" |
| **Exception Rate** | 2 | Spec defines COMPLIANCE_TRACK_UNCLEAR escalation, suggesting ~10–15% of hires have unclear track. If >10%, exception rate is HIGH. |
| **Tool Coverage** | 4 | Compliance matrix available as reference data (fetched via API or config). Role/location/hire_type available in HRIS. All data accessible. BUT: no ability to auto-assign to LMS; human must submit assignment to training system after approval. |
| **Risk/Reversibility** | 2 | Incorrect training track = audit finding ($2,000–$10,000). Reversible (re-assign track) but high-stakes. Federal/state training mandates are not-deferrable. |
| **Suitability Score** | 3.3 | (4+3+4)/3 |
| **Delegation Archetype** | **Agent-Led + Human Oversight** | Agent proposes track with confidence level. HIGH confidence (exact 3/3 match) = recommend approval. MEDIUM/LOW confidence = route to HR Ops for review before execution. Human approves before assignment written to LMS. |

**Rationale for archetype:** Mostly deterministic but meaningful exception rate (10–15%). Risk is medium-high (audit exposure). Requires human approval before execution. Agent can narrow the decision space.

---

#### Cluster 4: Buddy Matching & Seniority Assessment (JtD 3, Zone 2)

| Dimension | Score | Rationale |
|---|---|---|
| **Input Structure** | 3 | Hire has seniority_level (in HRIS), department. Employee directory has seniority_level, tenure_months, buddy_eligible flag. One ambiguity: seniority_level may be NULL if role is unmapped (per spec: SENIORITY_UNMAPPED escalation). |
| **Decision Determinism** | 2 | Partially deterministic: filtering by department + tenure is deterministic. Ranking by seniority_delta is deterministic. BUT: final selection from ranked list has judgment component: "Does this person fit our team dynamics?" Seniority norm (delta ≤2) is a rule, but exceptions exist (hire a director; only seniors available but all busy). |
| **Exception Rate** | 3 | Spec defines two escalations: NO_ELIGIBLE_BUDDY (~5% of cases, per assumption) and SENIORITY_GAP (~10% of cases, per assumption). Combined exception rate ~15%. Moderate-to-high. |
| **Tool Coverage** | 4 | Employee directory available (HRIS). Can query eligible buddies via API. But cannot measure team dynamics programmatically; this is tribal knowledge. Agent can surface top candidate; cannot guarantee fit. |
| **Risk/Reversibility** | 3 | Poor buddy match = retention risk, $1,000–$3,000 impact (hiring cost for replacement if hire quits). Reversible (re-assign buddy) but takes time and has morale impact. Medium risk. |
| **Suitability Score** | 3.0 | (3+2+4)/3 |
| **Delegation Archetype** | **Human-led + Automation Support** | Tools accelerate execution; judgment stays human. Automation sorts eligible candidates by seniority_delta, tenure, and department. HR Ops selects from the sorted list based on team dynamics the system cannot observe. |

**Rationale for archetype:** The tool does the legwork (sort + filter); the human makes the call the tool cannot make (team fit). This is "tools accelerate execution, judgment stays human" — the textbook Human-led + Automation Support pattern. Tom Reeves' buddy was overridden (Artefact 1.2: paired with Sarah J, not Anna per the rule) — precisely because team dynamics are not in the data model.

---

#### Cluster 5: IT Provisioning Request Generation (JtD 3, Zone 3)

| Dimension | Score | Rationale |
|---|---|---|
| **Input Structure** | 4 | Hire has role (in HRIS). IT role-access matrix is structured (role → access_package_id). One ambiguity: hire.role may not match any row in matrix (ROLE_NOT_MAPPED escalation is defined). ~5–10% of new roles not in matrix. |
| **Decision Determinism** | 4 | Lookup is deterministic IF role found. Choosing access_package is rule-based. BUT if role unmapped, requires judgment: "What access should this role get?" = policy decision. |
| **Exception Rate** | 2 | ROLE_NOT_MAPPED escalation suggests ~5–10% of hires have unmapped roles. Additional exception: IT provisioning system may reject request (REJECTED state in ITProvisioningRequest SM). Combined rate ~15–20%. |
| **Tool Coverage** | 3 | Can query IT role-access matrix. Can call IT provisioning API to submit request. BUT IT system has approval gate (external human reviews request before provisioning), and IT system may be unavailable (fallback: escalate to IT Support). Not fully autonomous. |
| **Risk/Reversibility** | 2 | Incorrect access grant = security incident ($1,000–$5,000 remediation) or compliance violation. Non-trivial risk. Reversible (revoke access) but requires security team. High-stakes. |
| **Suitability Score** | 3.7 | (4+4+3)/3 |
| **Delegation Archetype** | **Fully Agentic** (main path) **+ Agent-led + Human Oversight** (unmapped role exception) | **Main path (~90%):** Deterministic lookup (`hire.role → access_package_id`) + API submit. Agent executes autonomously within defined bounds — no per-case human review. **Unmapped role path (~10%):** Rather than firing a blind `ROLE_NOT_MAPPED` escalation, an LLM reads the role title and department, compares to similar roles in the matrix, and proposes the nearest access package with a rationale ("Head of ESG Compliance — closest match: Compliance Manager, 85% similarity. Suggested package: Compliance_Senior"). IT Manager approves or adjusts. Part of the Phase 2 Proposal Router. |

**Rationale for archetype:** The main path needs no LLM — a rules engine handles it correctly and cheaply. The exception path (unmapped role) currently produces a blind escalation that IT Manager must resolve from scratch. An LLM proposal reduces that from "figure it out" to "approve or adjust" — genuine value at low volume (~22–33 cases/year).

---

#### Cluster 6: Task Status Monitoring & Reminder Generation (JtD 4, Zone 1)

| Dimension | Score | Rationale |
|---|---|---|
| **Input Structure** | 4 | Task records have all required fields (deadline, status, task_type, owner_type, owner_id). Status is fetched from 6 source systems via API. Two ambiguities: (1) system APIs may be unavailable; (2) status may not sync within 2 hours (latency). |
| **Decision Determinism** | 5 | Comparison logic is deterministic: if (deadline - 48h) <= now AND status != COMPLETE AND no reminder in last 24h → send reminder. Pure logic, zero judgment. |
| **Exception Rate** | 2 | Spec defines two exceptions: TASK_OVERDUE_24h and TASK_OVERDUE_72h escalations, suggesting ~10–15% of tasks exceed deadline. Rate is elevated by system latency and interdependencies. |
| **Tool Coverage** | 3 | Can query task status (6 source systems via polling). Can send reminders (email API). BUT: polling every 2 hours means latency; if reminder is late (sent after deadline), it's useless. Partial tool coverage. |
| **Risk/Reversibility** | 4 | Missed or duplicate reminder is low-impact ($<100, minor friction). Reversible (send correction email). |
| **Suitability Score** | 4.0 | (4+5+3)/3 |
| **Delegation Archetype** | **Fully Agentic** | Monitors task deadlines and sends reminders autonomously within defined bounds. Minimal exception handling: if system unavailable, queue reminder for retry. Duplicates handled by idempotency key. No human approval needed per reminder, but escalations (TASK_OVERDUE) route to HR Ops. Implementation: scheduled rule engine (no LLM required — fully deterministic threshold logic). |

**Rationale for archetype:** Deterministic threshold logic (`if deadline + 24h elapsed AND status != COMPLETE → remind`). Low risk, reversible. A scheduled Python script or Power Automate flow is sufficient; no agent framework needed.

---

#### Cluster 7: I-9 Compliance Monitoring & Escalation (JtD 2, Zone 2)

| Dimension | Score | Rationale |
|---|---|---|
| **Input Structure** | 4 | Hire has hire_type, start_date. I-9 task has status, deadline. I-9 system (HRIS or separate) provides completion status. Mostly structured; one ambiguity: I-9 completion status may have latency (not updated real-time). |
| **Decision Determinism** | 5 | Escalation logic is deterministic + mandated by federal regulation: if i9_task.status != COMPLETE at day 2 → escalate I9_AT_RISK; if still not complete at day 3 → escalate I9_VIOLATION. ZERO discretion. Agent cannot override or delay escalation. |
| **Exception Rate** | 3 | Spec assumes I-9 violations = 2–4 per year (out of 220+ hires = <2%). But if hiring spikes (rush period), exception rate may increase. Assume moderate (3–5% of hires hit I9_AT_RISK escalation). |
| **Tool Coverage** | 5 | All data available in HRIS. Agent can poll I-9 status directly. Agent can create escalations automatically (no external system dependency). Full coverage. |
| **Risk/Reversibility** | 1 | I-9 violation = federal penalty ($252–$2,507) + legal liability. Irreversible (violation occurred). Cannot be "fixed" post-facto. CRITICAL RISK. |
| **Suitability Score** | 4.8 | (4+5+5)/3 |
| **Delegation Archetype** | **Fully Agentic (mandatory)** | Monitors I-9 completion and **MUST** escalate at day 2 and day 3 without exception. Agent acts autonomously within defined bounds — no per-case human review. No discretion, no approval gate. Escalation must route to HR Ops on-call + HR Manager (for CRITICAL). Cannot skip or delay under any circumstances. This is guardrail #3 in spec. Implementation: scheduled poller (no LLM required — the rule is binary: day count + completion status = escalate or not). |

**Rationale for archetype:** Deterministic, non-negotiable, high-risk. Escalation is a legal mandate, not a judgment call. Implement as a scheduled poller with hard-coded thresholds; no agent framework needed. Automation is mandatory because human memory fails under load — this is the case where automation is justified by reliability, not sophistication.

---

#### Cluster 8: Hold Decision & Onboarding Pause (JtD 1 or 4, cross-cutting)

| Dimension | Score | Rationale |
|---|---|---|
| **Input Structure** | 2 | Hold decision may be triggered by multiple conditions (late I-9, failed background check, visa delay, offer retraction). Each has different data model. Inputs are heterogeneous and unstructured. |
| **Decision Determinism** | 1 | Hold decision is fundamentally a judgment call: "Should we pause this hire?" Legal, HR, and hiring manager must align. No rule exists; each case is contextual. |
| **Exception Rate** | 3 | Assuming holds happen 5–10% of hires (spec doesn't quantify); if rare, exception rate is high (only unusual hires hit this). |
| **Tool Coverage** | 3 | Can detect hold triggers (I-9 delayed, background check failed) via monitoring. But cannot execute hold decision; cannot write to hire.status = ON_HOLD without human authority. |
| **Risk/Reversibility** | 1 | Hold decision is irreversible employment action. Hiring is paused. Legal implications. Cannot be automated. |
| **Suitability Score** | 2.0 | (2+1+3)/3 |
| **Delegation Archetype** | **Human Only** | Agent can detect hold triggers and escalate (e.g., "I-9 violation triggered → escalate to HR Ops for hold decision"). But agent **cannot** make or execute hold decision. Hold decision requires human accountability. This is guardrail #1 in spec. |

**Rationale for archetype:** Irreversible action with legal implications. Zero automation appropriate.

---

#### Cluster 9: Manager Handoff & Pre-Day-1 Completion Check (JtD 1, Zone 4)

| Dimension | Score | Rationale |
|---|---|---|
| **Input Structure** | 5 | Pre-Day-1 task list is structured (task_type.category = PRE_DAY_1). Task status is binary (COMPLETE or not). All data in task records. |
| **Decision Determinism** | 4 | Handoff notification logic is mostly deterministic: if all_tasks_complete(hire_id, PRE_DAY_1) then send, else send with flags. But "all complete" has one gray area: should SKIPPED tasks count as complete? (Spec doesn't clarify.) Otherwise deterministic. |
| **Exception Rate** | 2 | Some hires have uncompleted tasks at Day -2 (pre-handoff), requiring conditional handoff with flags. Estimate 20–30% of hires have 1–2 PRE_DAY_1 tasks still in progress at Day -2. Moderate exception rate. |
| **Tool Coverage** | 5 | All task data available. Email system available. Can send handoff notifications. Full coverage. |
| **Risk/Reversibility** | 4 | Late handoff = manager not prepared for Day 1 (friction, poor new hire experience). Reversible (send late notification). Low cost (~$200). |
| **Suitability Score** | 4.6 | (5+4+5)/3 |
| **Delegation Archetype** | **Fully Agentic** | Checks all PRE_DAY_1 tasks and sends handoff notification autonomously within defined bounds — no per-case human review. If complete, sends handoff summary. If incomplete, sends handoff with incomplete items flagged. Manager has full visibility. Implementation: scheduled rule engine (no LLM required for the trigger or content structure). |

**Rationale for archetype:** Deterministic logic, low risk, reversible. The exception case (incomplete tasks at Day -2) requires conditional logic, not judgment. Implement as a scheduled job or workflow trigger; no agent framework needed. **Optional lower-priority enhancement:** LLM-generated handoff content (contextualised summary rather than template) could add value for managers, but at 220 hires/year the template is sufficient — the content enhancement is not worth the added complexity at this scale.



---

## Full Scoring Summary

Scores are on a 1–5 scale. The Suitability Score is the average of Input Structure, Decision Predictability, and Tool Coverage — the three dimensions most predictive of whether the agent can act reliably. Risk/Reversibility and Exception Rate inform the archetype selection but are not averaged into the score.

| Cluster | Decision Rule? | Tools Available? | Exception Rate | Risk if Wrong | Suitability | Delegation Level |
|---|---|---|---|---|---|---|
| 1. Deadline Calc | 5 — pure maths | 5 — all data in HRIS | 5 — almost never | 5 — easily corrected | **5.0** | Fully Agentic |
| 2. Hire Type Class | 2 — ambiguous cases require LLM reasoning from employment agreement text | 3 — agreement text in SharePoint; LLM reads and reasons for ambiguous ~10% | 2 — 5–10% of hires ambiguous | 2 — cascades into wrong tasks | **2.3** | Human-led + Agent Support (LLM for ambiguous path) |
| 3. Training Track | 3 — 20–30% partial matches require LLM inference | 4 — matrix available; LLM handles no-exact-match cases | 2 — 10–15% unclear | 2 — audit risk | **3.3** | Agent-led + Human Oversight |
| 4. Buddy Match | 2 — ranking is arithmetic; team fit selection is human judgment | 4 — directory available | 3 — 15% gap/missing | 3 — retention risk | **3.0** | Human-led + Automation Support |
| 5. IT Provision | 4 — deterministic lookup (main path); LLM proposes for unmapped roles | 3 — main path: autonomous; unmapped: LLM proposes nearest package for IT to approve | 2 — 15–20% unmapped | 2 — security risk | **3.7** | Fully Agentic (main) + Agent-led + Human Oversight (unmapped) |
| 6. Task Monitor | 5 — deterministic threshold | 3 — 2h polling latency | 2 — 10–15% overdue | 4 — low; easily fixed | **4.0** | Fully Agentic |
| 7. I-9 Monitoring | 5 — federal mandate, no discretion | 5 — fully available | 3 — 3–5% hit AT_RISK | 1 — federal penalty | **4.8** | Fully Agentic (mandatory) |
| 8. Hold Decision | 1 — no rule; all context | 3 — can detect but not execute | 3 — rare but high stakes | 1 — irreversible legal action | **2.0** | Human Only |
| 9. Manager Handoff | 4 — binary condition | 5 — all data available | 2 — 20–30% incomplete at T-2 | 4 — late notice, not critical | **4.6** | Fully Agentic |

---

## How the Work Splits

| Archetype | Clusters | % of Work | Implementation |
|---|---|---|---|
| **Fully Agentic** | Clusters 1, 5 (main path), 6, 7, 9 | ~50% | Phase 1: CoordinationOrchestrator. Agent executes autonomously within defined bounds — no per-case human review. Implementation: scheduled Python rule engine (no LLM required; all paths deterministic). |
| **Agent-led + Human Oversight** | 3 use cases: cluster 3 (full), cluster 2 (ambiguous path ~10%), cluster 5 (unmapped role path ~10%) | ~20% | Phase 2: Proposal Router. One agent, three trigger types, one approval workflow. LLM proposes; HR Ops or IT Manager approves before execution. Execution delegated; supervision mandatory. |
| **Human-led + Automation Support** | Cluster 4 | ~15% | Automation sorts the buddy candidate list (deterministic sort). Human selects based on team dynamics the system cannot observe. Tools accelerate execution; judgment stays human. |
| **Human-led + Agent Support** | Cluster 2 (unambiguous path) | ~10% | For unambiguous hire types, automation flags and routes. LLM synthesis activates only for the ambiguous ~10% (handled in Agent-led row above). Agent provides synthesis and recommendations; human decides. |
| **Human Only** | Cluster 8 | ~5% | No automation. Irreversible legal action; tacit knowledge and ethics. |

**What this means in practice:** Phase 1 (CoordinationOrchestrator) is a rule engine covering ~50% of coordination work — autonomous, no LLM. Phase 2 (Proposal Router) is where AI reasoning genuinely adds value: three non-deterministic use cases where the correct answer cannot be expressed as an if/else rule. The test that separates them: *"Can you write the complete if/else rule right now with no ambiguity?"* Yes = Fully Agentic (rule engine). No = Agent-led + Human Oversight (LLM proposes, human approves).

---

## Anti-Pattern Check ✓

**Is everything "Fully Agentic"?** No — by design, the five archetypes span the full range.

- Clusters 1, 5 (main path), 6, 7, 9 are **Fully Agentic** — agent acts autonomously within defined bounds. Implementation is a rule engine (no LLM needed; all paths deterministic). The governance model is agentic; the technology is deliberately simple.
- **Three genuine LLM use cases** (Agent-led + Human Oversight), all in the Phase 2 Proposal Router:
  - Cluster 3 (full): compliance track partial-match reasoning
  - Cluster 2 (ambiguous ~10%): hire type inference from employment agreement text
  - Cluster 5 (unmapped ~10%): access package proposal from role title/department similarity
- Cluster 4 (Buddy Matching) is **Human-led + Automation Support** — sorting is arithmetic; team fit selection is human judgment that cannot be codified.
- Cluster 8 (Hold Decision) is **Human Only** — irreversible legal action.

**All three LLM use cases include a human approval step** — none are fully autonomous. The key distinction: deterministic work (complete if/else rule possible) → Fully Agentic rule engine. Non-deterministic work (cannot write the complete rule because input space is too large or context-dependent) → Agent-led + Human Oversight with LLM.

---

## Grounding in Evidence

All archetype assignments cite:
1. **Spec Section 2 (Delegation Analysis)** — explicit archetype assignments for individual tasks
2. **Spec Section 3.6 (Decision Logic)** — requirements 1–10 show which steps are deterministic vs. judgment-heavy
3. **Spec Section 3.5 (Escalation Triggers)** — 15+ escalation types indicate where human judgment is needed
4. **Spec Section 2.3 (Guard Rails)** — defines what agent "must NOT do" (e.g., hold decisions, hire_type determination)

---

## Assumptions & Confidence

| Assumption | Confidence | Impact if Wrong |
|---|---|---|
| Exception rate for compliance training = 10–15% | MEDIUM | If >20%, confidence score drops; may need escalation instead of oversight |
| Buddy matching seniority norm (delta ≤2) is enforced 85% of time | MEDIUM | If <70% enforced, need to escalate more often or adjust rule |
| I-9 completion status available with <2h latency | MEDIUM | If latency >4h, may miss escalation window; need different monitoring strategy |
| Hold decisions are <5% of hires | MEDIUM | If >10%, hold workflow dominates; may need more structured hold decision process |
| All 5 source systems have APIs available | LOW | If APIs unavailable, tool coverage drops; agent must rely on batch jobs or polling |

---

## What Comes Next

Knowing *what* can be delegated to an agent is not the same as knowing *what to build first*. Some clusters are agent-safe but happen rarely and don't save much time. Others happen constantly and have high leverage. The next step scores each cluster on volume and value to identify the best build target.

**→ Proceed to Deliverable 4: Volume × Value Analysis**
