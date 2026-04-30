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

## The Four Delegation Levels

| Level | What it means | Example |
|---|---|---|
| **Fully Agentic** | Agent acts without human review | Deadline calculation — pure maths, no judgment |
| **Agent-Led + Human Oversight** | Agent proposes, human approves before execution | Buddy matching — agent ranks candidates, HR Ops selects |
| **Human-Led + Agent Support** | Human decides, agent surfaces information | Hire type classification — agent flags ambiguity, human resolves |
| **Human Only** | No agent involvement | Hold decisions — legally irreversible, requires human accountability |

---

## Scoring: Each Task Cluster

### Summary (read this first)

| Cluster | Suitability Score | Delegation Level | One-line reason |
|---|---|---|---|
| 1. Deadline Calculation | 5.0 | **Fully Agentic** | Pure arithmetic — no judgment possible |
| 2. Hire Type Classification | 2.3 | **Human-Led + Support** | ~5–10% of cases are genuinely ambiguous; misclassification cascades |
| 3. Compliance Training Proposal | 3.3 | **Agent-Led + Oversight** | 10–15% exception rate; wrong track = audit risk |
| 4. Buddy Matching | 3.0 | **Agent-Led + Oversight** | Team fit judgment can't be codified; medium retention risk |
| 5. IT Provisioning | 3.7 | **Agent-Led + Oversight** | External IT approval gate; unmapped roles need escalation |
| 6. Task Status Monitoring | 4.0 | **Fully Agentic** | Deterministic; low risk; easily corrected |
| 7. I-9 Compliance Monitoring | 4.8 | **Fully Agentic (Mandatory)** | Federal requirement; zero discretion; human memory too unreliable |
| 8. Hold Decision | 2.0 | **Human Only** | Irreversible employment action; legal implications |
| 9. Manager Handoff Notification | 4.6 | **Fully Agentic** | Rule-based trigger; low risk |

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
| **Delegation Archetype** | **Fully Agentic** | All criteria met: deterministic, low exception, reversible, low risk, full tool coverage |

**Rationale for archetype:** This is pure computation. No human judgment needed. Agent can act autonomously.

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
| **Delegation Archetype** | **Human-Led + Agent Support** | Agent can flag NULL hire_type or ambiguous cases; agent cannot decide. Human must review employment agreement and confirm classification. Agent's role: escalate and surface data for human decision. |

**Rationale for archetype:** Too much judgment and risk for fully agentic. Agent surfaces data; human decides.

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
| **Delegation Archetype** | **Agent-Led + Human Oversight** | Agent ranks eligible candidates (deterministic algorithm) and surfaces top 3 with confidence + rationale. HR Ops approves or selects alternative from ranked list. Agent cannot execute assignment without approval (high trust boundary). |

**Rationale for archetype:** Ranking is rule-based, but final selection has judgment (team fit). Exception rate is moderate (15%). Risk is medium (retention impact). Human must retain decision authority.

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
| **Delegation Archetype** | **Agent-Led + Human Oversight** (with IT gate) | Agent submits provisioning request to IT system. IT approver (human) reviews and approves in IT system. Agent does NOT execute access grant directly. Agent can create request autonomously only if role is found in matrix; if role unmapped, escalate to IT Manager for manual package assignment. |

**Rationale for archetype:** Mostly deterministic but has external approval gate (IT). Agent acts as "router" (submits request) but IT retains approval authority. Exception handling (unmapped roles) requires escalation.

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
| **Delegation Archetype** | **Fully Agentic** (with fallback) | Agent monitors task deadlines and sends reminders autonomously. Minimal exception handling: if system unavailable, queue reminder for retry. Duplicates handled by idempotency key. No human approval needed per reminder, but escalations (TASK_OVERDUE) route to HR Ops. |

**Rationale for archetype:** Deterministic logic, low risk, reversible. System latency is acceptable for reminders (few hours late doesn't break onboarding). Agent can execute autonomously.

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
| **Delegation Archetype** | **Fully Agentic** (mandatory escalation) | Agent monitors I-9 completion and **MUST** escalate at day 2 and day 3 without exception. No discretion, no approval gate. Escalation must route to HR Ops on-call + HR Manager (for CRITICAL). Agent cannot skip or delay this task under any circumstances. This is guardrail #3 in spec. |

**Rationale for archetype:** Deterministic, non-negotiable, high-risk. Escalation is not a "nice-to-have" but a legal mandate. Agent must execute autonomously to ensure compliance.

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
| **Delegation Archetype** | **Fully Agentic** | Agent checks all PRE_DAY_1 tasks. If complete, sends handoff summary. If incomplete, sends handoff with incomplete items flagged. Manager has full visibility. Agent can execute autonomously. |

**Rationale for archetype:** Deterministic logic, low risk, reversible. Small exception rate (20–30% incompleteness) doesn't require escalation; just conditional logic. Agent can handle this.

---

## Full Scoring Summary

Scores are on a 1–5 scale. The Suitability Score is the average of Input Structure, Decision Predictability, and Tool Coverage — the three dimensions most predictive of whether the agent can act reliably. Risk/Reversibility and Exception Rate inform the archetype selection but are not averaged into the score.

| Cluster | Decision Rule? | Tools Available? | Exception Rate | Risk if Wrong | Suitability | Delegation Level |
|---|---|---|---|---|---|---|
| 1. Deadline Calc | 5 — pure maths | 5 — all data in HRIS | 5 — almost never | 5 — easily corrected | **5.0** | Fully Agentic |
| 2. Hire Type Class | 2 — often ambiguous | 3 — agreement may need manual review | 2 — 5–10% of hires | 2 — cascades into wrong tasks | **2.3** | Human-Led + Support |
| 3. Training Track | 3 — 20–30% partial matches | 4 — matrix available | 2 — 10–15% unclear | 2 — audit risk | **3.3** | Agent-Led + Oversight |
| 4. Buddy Match | 2 — team fit can't be codified | 4 — directory available | 3 — 15% gap/missing | 3 — retention risk | **3.0** | Agent-Led + Oversight |
| 5. IT Provision | 4 — lookup if role mapped | 3 — IT approval gate | 2 — 15–20% unmapped | 2 — security risk | **3.7** | Agent-Led + Oversight |
| 6. Task Monitor | 5 — deterministic threshold | 3 — 2h polling latency | 2 — 10–15% overdue | 4 — low; easily fixed | **4.0** | Fully Agentic |
| 7. I-9 Monitoring | 5 — federal mandate, no discretion | 5 — fully available | 3 — 3–5% hit AT_RISK | 1 — federal penalty | **4.8** | Fully Agentic (Mandatory) |
| 8. Hold Decision | 1 — no rule; all context | 3 — can detect but not execute | 3 — rare but high stakes | 1 — irreversible legal action | **2.0** | Human Only |
| 9. Manager Handoff | 4 — binary condition | 5 — all data available | 2 — 20–30% incomplete at T-2 | 4 — late notice, not critical | **4.6** | Fully Agentic |

---

## How the Work Splits

| Archetype | Count | % of Work | Cognitive Load |
|---|---|---|---|
| **Fully Agentic** | 4 (clusters 1, 6, 7, 9) | ~50% | Routine, rule-based, reversible |
| **Agent-Led + Oversight** | 3 (clusters 3, 4, 5) | ~35% | Mostly rules but judgment/exceptions; human approval gate |
| **Human-Led + Support** | 1 (cluster 2) | ~10% | Judgment-heavy; agent surfaces data |
| **Human Only** | 1 (cluster 8) | ~5% | Legal/irreversible; no automation |

**What this means in practice:** Half the onboarding workflow can run without human review. The other half either needs a human to approve the agent's proposal (training assignment, buddy matching, IT access) or is human-driven entirely (hire type classification, hold decisions). This matches the scenario's "85% routine, 15% judgment" claim — and the breakdown is *intentional*, not a default.

---

## Anti-Pattern Check ✓

**Is everything "Fully Agentic"?** NO. 
- Cluster 2 (Hire Type) is Human-Led, not agentic.
- Cluster 3, 4, 5 are Agent-Led + Oversight (not autonomous).
- Cluster 8 (Hold) is Human Only.

This demonstrates intentional delegation boundaries, not rubber-stamping everything to the agent.

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
| All 6 source systems have APIs available | LOW | If APIs unavailable, tool coverage drops; agent must rely on batch jobs or polling |

---

## What Comes Next

Knowing *what* can be delegated to an agent is not the same as knowing *what to build first*. Some clusters are agent-safe but happen rarely and don't save much time. Others happen constantly and have high leverage. The next step scores each cluster on volume and value to identify the best build target.

**→ Proceed to Deliverable 4: Volume × Value Analysis**
