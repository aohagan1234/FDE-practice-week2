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
| **Fully Agentic** | Agent uses LLM reasoning to make decisions that cannot be expressed as if/else rules | Compliance track matching when hire role is genuinely ambiguous — *not applicable to any cluster in this project* |
| **Fully Automated** | Deterministic rule engine or scheduled job; no LLM reasoning, no human review | Deadline calculation (pure arithmetic), I-9 threshold monitoring, task reminders |
| **Agent-Led + Human Oversight** | Agent proposes, human approves before execution | Buddy matching — agent ranks candidates, HR Ops selects |
| **Human-Led + Agent Support** | Human decides, agent surfaces information | Hire type classification — agent flags ambiguity, human resolves |
| **Human Only** | No agent involvement | Hold decisions — legally irreversible, requires human accountability |

---

## Scoring: Each Task Cluster

### Summary (read this first)

| Cluster | Suitability Score | Delegation Level | One-line reason |
|---|---|---|---|
| 1. Deadline Calculation | 5.0 | **Fully Automated** | Pure arithmetic — a cron job or workflow; no LLM reasoning needed |
| 2. Hire Type Classification | 2.3 | **Human-Led + Support** | ~5–10% of cases are genuinely ambiguous; misclassification cascades |
| 3. Compliance Training Proposal | 3.3 | **Agent-Led + Oversight** | 10–15% exception rate; wrong track = audit risk |
| 4. Buddy Matching | 3.0 | **Human-Led + Automation Support** | Ranking is a deterministic sort; the real decision (team fit) is human-only |
| 5. IT Provisioning | 3.7 | **Fully Automated** | Main path is lookup + API submit; IT approval gate is IT's governance, not agent reasoning; unmapped roles escalate to human |
| 6. Task Status Monitoring | 4.0 | **Fully Automated** | Deterministic threshold logic; rule engine or scheduled poller |
| 7. I-9 Compliance Monitoring | 4.8 | **Fully Automated (Mandatory)** | Federal requirement; zero discretion; deterministic day-count logic |
| 8. Hold Decision | 2.0 | **Human Only** | Irreversible employment action; legal implications |
| 9. Manager Handoff Notification | 4.6 | **Fully Automated** | Rule-based trigger; deterministic condition check |

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
| **Delegation Archetype** | **Fully Automated (rule engine / cron job)** | All criteria met: deterministic, low exception, reversible, low risk, full tool coverage. No LLM reasoning required — implement as a scheduled job or workflow automation. |

**Rationale for archetype:** Pure computation (`start_date + offset_days`). No human judgment or LLM reasoning needed. A cron job or Power Automate flow is the right tool; an agent framework adds cost and complexity for zero benefit.

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
| **Delegation Archetype** | **Human-Led + Automation Support** | Automation sorts eligible candidates by seniority_delta, tenure, and department — a deterministic algorithm. HR Ops makes the real decision from the sorted list. The sorting is automation, not agency; the judgment (team fit, historical conflicts, relationship dynamics) is entirely human. |

**Rationale for archetype:** The "agent" part of buddy matching is a sort function. Seniority_delta is arithmetic. Tenure comparison is arithmetic. Department filtering is a rule. None of this requires LLM reasoning. Calling it "Agent-Led" would imply the agent is reasoning about candidates — it isn't. HR Ops sees a sorted list and makes the decision that cannot be automated: whether this specific person is the right fit for this specific hire given team dynamics the system cannot observe.

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
| **Delegation Archetype** | **Fully Automated** (main path; human escalation for unmapped roles) | The main path is a deterministic lookup (`hire.role → access_package_id`) followed by an API submit. This is automation, not agency — a lookup table and an API call. The IT approval gate that follows is IT's internal governance process, not agent reasoning. For the ~5–10% of unmapped roles, the agent escalates to IT Manager; a human makes the non-deterministic decision about what access a novel role needs. |

**Rationale for archetype:** Lookup + API submit is automation. Having a human approve the result downstream does not make the submission step "agentic" — the agent applied a rule, not judgment. The only genuinely non-deterministic part (unmapped role → what access?) correctly escalates to a human rather than being guessed by the automation.

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
| **Delegation Archetype** | **Fully Automated (rule engine / scheduled poller)** | Monitors task deadlines and sends reminders autonomously. Minimal exception handling: if system unavailable, queue reminder for retry. Duplicates handled by idempotency key. No human approval needed per reminder, but escalations (TASK_OVERDUE) route to HR Ops. No LLM reasoning required — implement as a scheduled rule engine. |

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
| **Delegation Archetype** | **Fully Automated (mandatory — scheduled poller)** | Monitors I-9 completion and **MUST** escalate at day 2 and day 3 without exception. No discretion, no approval gate. Escalation must route to HR Ops on-call + HR Manager (for CRITICAL). Cannot skip or delay under any circumstances. This is guardrail #3 in spec. No LLM reasoning required — the rule is binary: day count + completion status = escalate or not. |

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
| **Delegation Archetype** | **Fully Automated (rule engine)** | Checks all PRE_DAY_1 tasks. If complete, sends handoff summary. If incomplete, sends handoff with incomplete items flagged. Manager has full visibility. No LLM reasoning required — the trigger condition is a deterministic boolean check. |

**Rationale for archetype:** Deterministic logic, low risk, reversible. The exception case (incomplete tasks at Day -2) requires conditional logic, not judgment. Implement as a scheduled job or workflow trigger; no agent framework needed.

---

## Full Scoring Summary

Scores are on a 1–5 scale. The Suitability Score is the average of Input Structure, Decision Predictability, and Tool Coverage — the three dimensions most predictive of whether the agent can act reliably. Risk/Reversibility and Exception Rate inform the archetype selection but are not averaged into the score.

| Cluster | Decision Rule? | Tools Available? | Exception Rate | Risk if Wrong | Suitability | Delegation Level |
|---|---|---|---|---|---|---|
| 1. Deadline Calc | 5 — pure maths | 5 — all data in HRIS | 5 — almost never | 5 — easily corrected | **5.0** | Fully Automated |
| 2. Hire Type Class | 2 — often ambiguous | 3 — agreement may need manual review | 2 — 5–10% of hires | 2 — cascades into wrong tasks | **2.3** | Human-Led + Support |
| 3. Training Track | 3 — 20–30% partial matches | 4 — matrix available | 2 — 10–15% unclear | 2 — audit risk | **3.3** | Agent-Led + Oversight |
| 4. Buddy Match | 2 — ranking is arithmetic; team fit selection is human judgment | 4 — directory available | 3 — 15% gap/missing | 3 — retention risk | **3.0** | Human-Led + Automation Support |
| 5. IT Provision | 4 — deterministic lookup (main path); unmapped roles escalate | 3 — IT approval gate is IT's governance, not agent reasoning | 2 — 15–20% unmapped | 2 — security risk | **3.7** | Fully Automated |
| 6. Task Monitor | 5 — deterministic threshold | 3 — 2h polling latency | 2 — 10–15% overdue | 4 — low; easily fixed | **4.0** | Fully Automated |
| 7. I-9 Monitoring | 5 — federal mandate, no discretion | 5 — fully available | 3 — 3–5% hit AT_RISK | 1 — federal penalty | **4.8** | Fully Automated (Mandatory) |
| 8. Hold Decision | 1 — no rule; all context | 3 — can detect but not execute | 3 — rare but high stakes | 1 — irreversible legal action | **2.0** | Human Only |
| 9. Manager Handoff | 4 — binary condition | 5 — all data available | 2 — 20–30% incomplete at T-2 | 4 — late notice, not critical | **4.6** | Fully Automated |

---

## How the Work Splits

| Archetype | Clusters | % of Work | Implementation |
|---|---|---|---|
| **Fully Automated** (rule engine / scheduled job) | 5 (clusters 1, 5, 6, 7, 9) | ~55% | Scheduled Python job or workflow automation (Power Automate, Azure Logic Apps). No LLM reasoning at runtime. Cluster 5's unmapped-role exception escalates to human. |
| **Agent-Led + Oversight** (genuine non-determinism) | 1 (cluster 3 only) | ~15% | Compliance track partial-match reasoning — the only cluster where LLM inference adds value over a lookup table. Agent proposes; HR Ops approves. |
| **Human-Led + Automation Support** | 1 (cluster 4) | ~15% | Automation sorts the buddy candidate list (deterministic algorithm). Human makes the selection based on team dynamics the system cannot observe. |
| **Human-Led + Agent Support** | 1 (cluster 2) | ~10% | Agent surfaces hire record data and flags ambiguities. Human makes the hire type classification decision. |
| **Human Only** | 1 (cluster 8) | ~5% | No automation. Irreversible legal action requires human accountability. |
| **Fully Agentic** (LLM reasoning, no human in loop) | 0 | — | No cluster in this project qualifies. True agentic work (non-deterministic, autonomous, LLM-reasoning) does not exist in this onboarding workflow at this scale. |

**What this means in practice:** The CoordinationOrchestrator is correctly a rule engine, not an AI agent. The only genuine LLM use case is Cluster 3 (compliance track matching with partial matrix results) — and that still requires human approval before execution. Everything else is either deterministic automation, human judgment with a sorted data feed, or human-only. This is the honest shape of this problem. If someone at Aldridge & Sykes asks "where does AI add value?" — the answer is Cluster 3, and only there.

---

## Anti-Pattern Check ✓

**Is everything "Fully Agentic"?** NO — and nothing is, by design.

- Clusters 1, 5, 6, 7, 9 are **Fully Automated** (rule engine / scheduled job). No LLM reasoning. Cluster 5's IT provisioning is a lookup + API call — the downstream IT approval gate is IT's governance process, not agent reasoning.
- Cluster 3 is the **only Agent-Led + Oversight** task — the only place where partial compliance matrix matches genuinely require inference that a lookup table cannot provide. Agent proposes; HR Ops approves.
- Cluster 4 (Buddy Matching) is **Human-Led + Automation Support** — the ranking is arithmetic. The human makes the real decision based on team dynamics. Calling this "agent-led" would misrepresent what the system does.
- Cluster 2 (Hire Type) is **Human-Led + Agent Support** — agent surfaces data and flags ambiguity; human classifies.
- Cluster 8 (Hold Decision) is **Human Only** — irreversible legal action.

**No cluster warrants "Fully Agentic" (LLM reasoning, no human in loop).** The one cluster using LLM reasoning (Cluster 3) still requires human approval before execution. For everything else: deterministic rules are more reliable, cheaper, and easier to audit than LLM inference. The right question is not "can an agent do this?" but "does non-determinism exist here that justifies the cost and complexity of an LLM?"

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
