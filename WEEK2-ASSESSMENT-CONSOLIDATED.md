# Week 2 ATX Assessment: HR Onboarding Coordination Scenario
## Consolidated Deliverable Document

**Date:** February 2025

**Submitted by:** Assessment Team

**Scenario:** KTB-1-109 — HR Onboarding Coordination Agent (Aldridge & Sykes)

**Assessment Scope:** 7-phase ATX (Agentic Transformation) methodology applied to real business process

---

## Executive Summary

This document presents a comprehensive Week 2 ATX assessment of the HR Onboarding Coordination scenario. The analysis applies evidence-based methodology to determine **where agents should operate** in the onboarding workflow, **why they should operate there**, and **how to build with intentional delegation boundaries**.

### Key Findings

1. **Viable Agent Target Identified:** Task Status Monitoring + Manager Orchestration (Cluster 6)
   - Volume: 3,500+ monitoring events/year per person
   - Determinism: 90% rule-based logic, 10% judgment/exception handling
   - Value Score: 10/25 (solid candidate when bundled with I-9 monitoring)

2. **Delegation Profile:** 50% of onboarding is rule-based and automatable; 35% requires human oversight; 15% must remain human-only
   - Fully Automated (rule engine / scheduled job): 5 clusters (deadline calc, IT provisioning main path, task monitoring, I-9 escalation, manager handoff)
   - Agent-Led + Oversight (genuine LLM use): 1 cluster (compliance training track — partial matrix match reasoning)
   - Human-Led + Automation Support: 1 cluster (buddy matching — ranking is automation; selection is human)
   - Human-Led + Agent Support: 1 cluster (hire type classification)
   - Human Only: 1 cluster (hold decisions)
   - Note: "Fully Agentic" (LLM reasoning, no human in loop) applies to zero clusters in this project

3. **ROI Reality:** Marginal monetary ROI (18–24 month payback) but significant compliance & experience benefits
   - Time freed: ~16 hours/person/year from automation
   - Compliance de-risking: One prevented I-9 violation ($2,507 penalty) pays for agent build cost
   - Scalability: At 2x hiring volume, ROI becomes strong (Year 1)

4. **Design Recommendation:** Phased agent development
   - **Phase 1 (Primary):** Coordination Orchestrator (monitoring + reminders + I-9 compliance)
   - **Phase 2 (Secondary):** Proposal Router (training + buddy + IT provisioning recommendations)

5. **Critical Success Factor:** API availability for all 5 source systems (Workday, ServiceNow, Saba LMS, calendar, fulfillment)
   - Confidence: LOW
   - Mitigation: Technical audit required before build commitment

---

## Part I: Discovery Findings (Phase 1)

### What We Know from the Spec

| Dimension | Finding |
|---|---|
| **Volume** | 220+ hires/year; ~73 per person per HR Ops team member (4–5 per week) |
| **Coordination overhead** | 2.5 hours per hire = 550 hours/year team-wide (~183 hours per person) |
| **Task scope** | 40 tasks per hire across 3 categories (PRE_DAY_1, POST_DAY_1, ONGOING) |
| **Systems** | 5 source systems (Workday/HRIS, ServiceNow/IT provisioning, Saba LMS, calendar, fulfillment) |
| **Judgment boundary** | 85% routine/deterministic; 15% judgment-required |
| **Compliance mandate** | I-9 verification must complete by Day 3 (federal 3-day deadline) |
| **Success targets** | ≥97% tasks on-time, 0 I-9 violations, ≥95% escalations routed correctly, ≤0.75 hrs per hire |

### What We Don't Know (Design-Changing Unknowns)

| Question | Importance | Current Assumption | Confidence |
|---|---|---|---|
| Which systems have reliable APIs available? | CRITICAL | All 5 have APIs | LOW |
| What's the actual 2.5h coordination time breakdown? | HIGH | Baseline includes all non-judgment time | MEDIUM |
| How often do holds occur, and who decides? | MEDIUM | Holds are <5% of hires | MEDIUM |
| What defines the 15% judgment cases operationally? | HIGH | Judgment is primarily compliance track ambiguity + buddy team fit | MEDIUM |
| When is a task "blocked" vs. reschedulable? | MEDIUM | Dependencies are hard rules; no human override logic | MEDIUM |
| What's the actual approval SLA for proposals? | MEDIUM | Priya can approve 30+ proposals/day (seconds per proposal) | MEDIUM |

### Key Assumption: 6 Critical Risks

| Assumption | Confidence | Validation Method | Impact if Wrong |
|---|---|---|---|
| API access exists for all 6 systems | LOW | Technical audit with IT | If 2+ systems have no APIs, agent effectiveness drops 40% |
| Compliance training matrix is maintained & 95%+ current | LOW | Compliance team review | If stale, training proposals have <50% success rate |
| HR Ops team responds to escalations within published SLAs | MEDIUM | Measure actual response times | If slow response, escalation queue backs up; agent stalls |
| 2.5h baseline includes all non-judgment time | MEDIUM | Time-tracking study | If actual is 60% higher, ROI projection changes |
| Buddy eligibility rules are enforced in HRIS | LOW | Audit HRIS data model | If rules are manually enforced, agent can't query reliably |
| Hold decisions are rare (<5% of hires) | MEDIUM | Historical analysis | If holds are >10%, hold workflow dominates; needs different design |

---

## Part II: Cognitive Load Map (Phase 2)

### Four Major Jobs to be Done

#### JtD 1: "Orchestrate Pre-Day-1 Readiness"
- **Scope:** 18 PRE_DAY_1 tasks from HIRE_TYPE_VERIFICATION → MANAGER_HANDOFF_NOTIFICATION
- **Cognitive contract:** By start_date, new hire and manager are ready to engage productively
- **Zones:** Intake/triage → Sequence/dependency mapping → Proposal generation → Execution/coordination
- **Breakpoints:** Hire creation (human→agent) → Proposal review (agent→human) → Approval execution (human→system) → Status sync (system→agent)

#### JtD 2: "Assure Compliance & Legal Readiness"
- **Scope:** 6 compliance-critical tasks: I9_VERIFICATION, COMPLIANCE_TRAINING, BACKGROUND_CHECK, NDA, EMERGENCY_CONTACT, DIRECT_DEPOSIT
- **Cognitive contract:** Mitigate regulatory risk (I-9 violations, training gaps, audit findings)
- **Key zones:** Compliance intake (risk assessment) → I-9 monitoring (deterministic escalation) → Training track assignment (rule-based with judgment)
- **Critical zone:** I-9 monitoring has zero discretion (mandatory escalation at Day 2 and Day 3)

#### JtD 3: "Match New Hire with Enabler & Mentor"
- **Scope:** 4 tasks: IT_PROVISIONING, BUDDY_ASSIGNMENT, SYSTEM_ACCOUNTS, LAPTOP_SHIPMENT
- **Cognitive contract:** Establish buddy relationship and IT access before start date
- **Key zones:** Eligibility assessment (deterministic query) → Buddy selection (judgment on team fit) → IT provisioning execution (rule-based with external gate)
- **Judgment load:** High (50%+ of decisions require organizational knowledge)

#### JtD 4: "Monitor Post-Day-1 Engagement Milestones"
- **Scope:** 18 POST_DAY_1 + ONGOING tasks through 30-day checkpoint
- **Cognitive contract:** Detect when someone is falling behind; intervene early
- **Key zones:** Daily monitoring (deterministic polling) → Judgment on intervention (when is delay a real problem?) → Escalation routing (deterministic)

### Cognitive Zones & Task Decomposition

**16 distinct cognitive zones identified:**
- Zone-level breakpoints show where control hands between agent, human, and systems
- Each zone has deterministic and judgment components
- Fully automatable zones: deadline calc, I-9 monitoring, task monitoring, manager handoff
- Judgment-heavy zones: hire type classification, buddy selection, compliance track ambiguity

### Delegation Breakpoints (8 Major Control Handoffs)

| Breakpoint | Signal | Direction | Why | Action |
|---|---|---|---|---|
| 1. Hire creation | Hire record created in HRIS | Human→Agent | All downstream depends on hire existing | Task list creation begins |
| 2. Proposal review | Proposals generated (compliance, buddy, IT) | Agent→Human | High-confidence proposals need approval authority | HR Ops approves or overrides |
| 3. Approval execution | HR Ops approves proposal | Human→System | Approved decision must write to downstream system | Agent executes write operation |
| 4. Status sync | External system completes task (IT provisions access) | System→Agent | Agent state must reflect external changes | Task status updated; dependencies checked |
| 5. Escalation | Escalation condition met (I-9 risk, overdue task, unmapped role) | Agent→Human | Some conditions have no defined rule | HR Ops makes contextual decision |
| 6. Task completion | External system reports task done (background check finishes) | System→Agent | Unlocks dependent tasks | Agent marks complete; checks downstream |
| 7. Hold decision | HR Ops marks hire as ON_HOLD | Human→System | Irreversible employment action | Onboarding paused; state preserved |
| 8. Manager handoff | PRE_DAY_1 tasks complete OR Day -2 reached | Agent→Human | Manager takes coordination responsibility from Day 1 | Handoff notification sent |

---

## Part III: Delegation Suitability & Archetype Assignment (Phase 3)

### Suitability Matrix: 9 Major Task Clusters Scored

| Cluster | Suitability | Archetype | Primary Reason |
|---|---|---|---|
| 1. Task Deadline Calculation | 5.0/5 | **Fully Automated** | Pure arithmetic; no LLM reasoning; implement as cron job |
| 2. Hire Type Classification | 2.3/5 | **Human-Led + Agent Support** | 30% judgment required; policy interpretation; high risk |
| 3. Compliance Training Track Proposal | 3.3/5 | **Agent-Led + Oversight** | 20% exception rate; human approval required |
| 4. Buddy Matching & Selection | 3.0/5 | **Human-Led + Automation Support** | Ranking is arithmetic (sort by seniority_delta); team fit decision is human-only |
| 5. IT Provisioning Request | 3.7/5 | **Fully Automated** | Main path is lookup + API submit; IT approval gate is IT's governance; unmapped roles escalate to human |
| 6. Task Status Monitoring & Reminders | 4.0/5 | **Fully Automated** | Deterministic threshold logic; scheduled poller; no LLM needed |
| 7. I-9 Compliance Monitoring | 4.8/5 | **Fully Automated (Mandatory)** | Federal mandate; binary day-count rule; zero discretion |
| 8. Hold Decision & Onboarding Pause | 2.0/5 | **Human Only** | Irreversible employment action; legal implications |
| 9. Manager Handoff & Completion Check | 4.6/5 | **Fully Automated** | Deterministic boolean trigger; scheduled job |

### Archetype Distribution

- **Fully Automated** (rule engine / scheduled job): 5 clusters = ~55% of work
- **Agent-Led + Oversight** (genuine LLM use): 1 cluster = ~15% of work
- **Human-Led + Automation Support**: 1 cluster = ~15% of work
- **Human-Led + Agent Support**: 1 cluster = ~10% of work
- **Human Only**: 1 cluster = ~5% of work

**Interpretation:** The CoordinationOrchestrator is correctly a rule engine, not an AI agent. The only genuine LLM use case is Cluster 3 (compliance track partial-match reasoning), and even that requires human approval. Clusters 4 and 5 were reclassified after applying the test: "Can the decision be expressed as a complete if/else rule right now?" — if yes, it is automation, not agency.

---

## Part IV: Volume × Value Analysis — Target Prioritization (Phase 4)

### Agentic Value Scoring (Volume × Non-Determinism)

**Formula:** Agentic Value = Volume (1–5) × Non-Determinism (1–5) = 1–25 scale

| Cluster | Volume | Non-Determ. | Agentic Value | Status |
|---|---|---|---|---|
| 1. Deadline Calc | 2 | 1 | 2 | Below threshold |
| 2. Hire Type Class | 2 | 4 | 8 | Below threshold |
| 3. Training Track | 2 | 3 | 6 | Below threshold |
| 4. Buddy Match | 2 | 4 | 8 | Below threshold |
| 5. IT Provision | 2 | 2 | 4 | Below threshold |
| **6. Task Monitor** | **5** | **2** | **10** | **CANDIDATE** ✓ |
| 7. I-9 Monitor | 4 | 1 | 4 | Below threshold (but non-negotiable) |
| 8. Hold Decision | 1 | 5 | 5 | Below threshold (human-only) |
| 9. Manager Handoff | 2 | 1 | 2 | Below threshold |

### Primary Target: Task Status Monitoring (Cluster 6)

**Why this cluster:**
- **Volume:** 3,500+ monitoring events per person/year (5/5 score)
- **Determinism:** 90% rule-based; only 10% exception handling (2/5 score)
- **Leverage:** Can be built as always-on background process
- **Value:** ~10 hours/person/year freed

**Secondary bundle:** Add I-9 monitoring (non-negotiable compliance mandate)
- Cluster 7 combines with Cluster 6 to create "Compliance Orchestrator" agent
- Total bundle value: 10 + 4 = 14/25 (solid candidate)

### Multi-Agent Strategy (Phased Approach)

**Agent 1: Coordination Orchestrator (Primary, Phase 1)**
- Task monitoring + deadline calculation + manager handoff + I-9 compliance
- Clusters 6 + 1 + 9 + 7
- Combined value: 10 + 2 + 2 + 4 = 18 points (exceeds 15 threshold)
- Time savings: ~16 hours/person/year

**Agent 2: Proposal Router (Secondary, Phase 2)**
- Compliance training proposals + buddy matching + IT provisioning
- Clusters 3 + 4 + 5
- Combined value: 6 + 8 + 4 = 18 points (exceeds threshold when bundled)
- Time savings: ~5 hours/person/year

### Economic Justification

| Factor | Estimate |
|---|---|
| **Agent 1 Build Cost** | $3,000–$4,500 (20–30 eng hours @ $150/hr) |
| **Agent 1 Operational Cost/year** | $500–$1,000 |
| **Time Freed/person/year** | 16 hours × $60/hr loaded cost = $960 value |
| **Payback Period** | 18–24 months (marginal) |
| **Compliance Value (I-9 violation prevention)** | $2,507 per violation prevented |
| **Recommendation** | ROI is marginal alone; strong if bundled with strategic investment or hiring scales 2x |

---

## Part V: Agent Purpose Document (Phase 5)

### Agent 1: Coordination Orchestrator Specification

**Mission:** Autonomously monitor onboarding task execution; detect delays; send reminders; escalate blockers and compliance risks.

**Target Pilot:** 30-day trial with 5–10 representative hires

### Operational Scope (What Agent Does)

1. **Monitor task status** — Poll 6 source systems every 2 hours
2. **Calculate deadlines** — deadline = start_date + task_type.offset_days (once per hire)
3. **Detect overdue tasks** — Flag tasks >24 hours past deadline
4. **Send reminders** — Email task owners (rate-limited 1 per task per 24h)
5. **Monitor I-9 completion** — Escalate I9_AT_RISK on Day 2, I9_VIOLATION on Day 3 (CRITICAL)
6. **Auto-submit IT provisioning** — Submit if role found; escalate if not found
7. **Send manager handoff** — Notify manager when pre-Day-1 complete OR Day -2 reached
8. **Route escalations** — Direct escalations to correct owners (HR Ops, IT, Legal, etc.)
9. **Maintain audit trail** — Log all actions for compliance review

### Out of Scope (Remains Human-Driven)

- Hire type classification (requires judgment)
- Buddy final selection (organizational knowledge)
- Hold decisions (legal implications)
- Escalation response (humans decide action)

### Escalation Triggers & SLAs

| Trigger | Condition | Route To | Priority | SLA |
|---|---|---|---|---|
| **I9_AT_RISK** | Day 2 + I-9 not complete | HR Ops on-call + HR Manager | HIGH | 15 min |
| **I9_VIOLATION** | Day 3 + I-9 not complete | Legal + CEO | **CRITICAL** | 5 min |
| **TASK_OVERDUE_72h** | Task overdue >72h | Task owner + HR Ops | MEDIUM | 2 hours |
| **ROLE_NOT_MAPPED** | Hire role not in IT matrix | IT Manager | HIGH | 1 hour |
| **SYSTEM_UNAVAILABLE** | Source system poll fails 3x | IT Support + HR Ops | MEDIUM | 2 hours |

### Key Performance Indicators

| Metric | Target | Owner |
|---|---|---|
| **Poll latency** | <4 min per hire | Agent execution logs |
| **Reminder delivery success** | ≥99% | Email system logs |
| **Escalation routing accuracy** | ≥95% | HR Ops QA |
| **On-time task completion** | ≥97% | HRIS task status |
| **I-9 violation rate** | 0 | Compliance audit |
| **HR Ops manual intervention** | <2 hrs/person/week | Time tracking |

### System & Data Requirements

**Source Systems (APIs Required):**

| System | Data | Rate Limit | SLA | Fallback |
|---|---|---|---|---|
| HRIS | Hire records, task status, I-9 status | 1,000 req/hr | 99.9% | Daily batch sync |
| IT Provisioning | Access packages, role matrix, request status | 500 req/hr | 99.5% | Manual email |
| Compliance LMS | Training tracks, enrollments, status | 100 req/hr | 98% | Weekly export |
| Calendar | Manager/IT availability | 1,000 req/day | 99% | Manual scheduling |
| Email | Send reminders, escalations | 10,000 msg/day | 99.95% | Queue + SMS backup |
| Fulfillment | Order status, shipment tracking | 500 req/hr | 95% | Manual email check |

### Failure Modes & Recovery

| Failure | Detection | Recovery | Severity |
|---|---|---|---|
| API timeout | Request hangs >5 min | Exponential retry; escalate after 3 fails | MEDIUM |
| Email delivery fail | Bounce or spam trap | Retry + escalate after 3 fails | HIGH |
| Incorrect deadline | Deadline off >5 days | Manual audit + recalculate | MEDIUM |
| I-9 monitoring miss | Day 3 + escalation not sent | CRITICAL: Legal notification + audit trail | **CRITICAL** |
| Duplicate reminders | Same reminder sent twice | Idempotency key check before send | MEDIUM |
| Escalation lost | Escalation not routed | Hard-coded routing fail-safe; test weekly | **CRITICAL** |

### Build Priorities (Confidence Order)

| Priority | Feature | Confidence |
|---|---|---|
| 1 | Deadline calculation + polling infrastructure | ✅ HIGH |
| 2 | Task overdue detection | ✅ HIGH |
| 3 | I-9 monitoring + mandatory escalation | ✅ HIGH |
| 4 | Reminder sending + rate limiting | ✅ MEDIUM |
| 5 | Escalation routing | ✅ MEDIUM |
| 6 | IT provisioning auto-submit | 🔶 LOWER (test thoroughly) |
| 7 | Manager handoff logic | 🔶 LOWER (depends on HRIS schema) |

### Validation & Pilot Gate

**Pre-Build Stakeholder Validation Required:**
- ✓ API availability audit for all 6 systems (IT team)
- ✓ IT provisioning matrix review + update process (IT Manager)
- ✓ Email escalation recipients + SLA confirmation (HR Manager + Legal)
- ✓ I-9 notification protocol (Compliance Officer)
- ✓ Task retry logic on transient failures (Engineering team)

**Pilot Success Criteria:**
- ≥80% of overdue tasks detected within 4 hours
- ≥99% of reminders delivered successfully
- ≥95% of critical escalations routed correctly
- Zero I-9 violations during 30-day pilot
- <2 hours/person/week manual intervention

---

## Part VI: Consolidated Assumptions & Confidence Log

| # | Assumption | Confidence | Verification Method | Impact if Wrong |
|---|---|---|---|---|
| A1 | API access exists for all 6 systems | **LOW** | Technical audit with IT; request docs | Agent effectiveness drops 40%; polling becomes batch-only |
| A2 | Compliance training matrix is maintainable as structured data | **MEDIUM** | Compliance team review; test data refresh | Training proposals have <50% success rate if stale |
| A3 | HR Ops responds to escalations within published SLAs | **MEDIUM** | Measure actual response times on sample escalations | Escalation queue backs up; agent stalls |
| A4 | 2.5h baseline includes all non-judgment time (no hidden rework) | **MEDIUM** | Time-tracking study; categorize activities | If actual is 60% higher, ROI improves but reveals systematic issues |
| A5 | Buddy eligibility rules enforced in HRIS (tenure, availability fields) | **LOW** | Audit HRIS data model; confirm fields exist | Agent cannot query reliably; manual workarounds needed |
| A6 | Hold decisions are <5% of hires | **MEDIUM** | Historical analysis; quantify hold rate | If >10%, hold workflow dominates; needs different design |

---

## Part VII: Recommendations & Next Steps

### Immediate Actions (Week 1–2)

1. **Technical Audit (IT Team)**
   - Confirm API availability for all 6 source systems
   - Document authentication, rate limits, SLAs per system
   - Identify fallback mechanisms (batch files, manual processes)
   - Outcome: Go/No-Go decision on agent viability

2. **Stakeholder Alignment Meeting (HR Ops + HR Manager + IT Manager + Legal)**
   - Present agent spec and escalation workflows
   - Validate assumptions: SLAs, decision authorities, approval gates
   - Confirm I-9 notification recipients and escalation protocol
   - Outcome: Signed-off scope and stakeholder buy-in

3. **Data Model Audit (HRIS Admin + IT)**
   - Verify task status schema (is it uniformly represented across systems?)
   - Confirm I-9 task tracking (manual email vs. system field?)
   - Review IT role-access matrix format and update frequency
   - Outcome: Data integration readiness assessment

### If Technical Audit Succeeds (Green Light)

4. **Build Mobilization (Engineering Team)**
   - Assign senior engineer to agent development
   - Estimate: 20–30 hours for MVP (deadline calc + polling + I-9 monitoring)
   - Set 3-week target for pilot-ready code
   - Establish daily standup + weekly review cadence

5. **Pilot Preparation (HR Ops + QA)**
   - Recruit 5–10 diverse hires for pilot (mix of EMPLOYEE/CONTRACTOR, different roles, locations)
   - Set up monitoring dashboard to track KPIs in real-time
   - Train HR Ops on escalation workflows and manual override procedures
   - Outcome: Pilot readiness checklist

6. **Pilot Execution (30 days)**
   - Run agent in parallel with current process (no cutover risk)
   - Track all metrics: poll latency, reminder delivery, escalation accuracy, time freed
   - Weekly standups to troubleshoot and iterate
   - Outcome: Pilot success criteria met or identified blockers

### If Technical Audit Fails (Red Light)

- **Option A:** Delay agent development until API access is available
- **Option B:** Use alternative architecture (batch polling instead of real-time APIs; trade latency for feasibility)
- **Option C:** Focus on lower-complexity agents (Phase 2 Proposal Router doesn't require real-time polling)

### Phase 2 (If Phase 1 Succeeds)

7. **Secondary Agent: Proposal Router (60–80 hours)**
   - Build compliance training proposals (deterministic with confidence scoring)
   - Build buddy matching ranker (rule-based top-3 recommendations with reasoning)
   - Build IT provisioning pre-screening (validate role + access package before submit)
   - Estimated value: ~5 additional hours/person/year + decision quality improvement

### Scaling (If Hiring Volume Increases)

- At 2x hiring volume (440+ hires/year, 150+ per person):
  - Agent ROI becomes strong (Year 1 payback)
  - Agent complexity may increase (scheduling conflicts, priority queuing)
  - Secondary agents become more valuable

---

## Appendix A: Full Discovery Questions & Grounding

See DELIVERABLE-1-DISCOVERY-QUESTIONS.md for:
- 6 design-changing discovery questions
- 6 critical assumptions with confidence levels
- Lived-work artefact grounding (5 signals extracted from spec)
- Implications for delegation boundaries

---

## Appendix B: Cognitive Load Map Detail

See DELIVERABLE-2-COGNITIVE-LOAD-MAP.md for:
- 4 Jobs to be Done decomposition
- 16 cognitive zones (each with micro-task breakdown)
- 8 major control handoffs (breakpoints)
- Evidence grounding table linking zones to spec sections

---

## Appendix C: Delegation Suitability Matrix Detail

See DELIVERABLE-3-DELEGATION-MATRIX.md for:
- Full 5-dimension scoring rubric (Input Structure, Decision Determinism, Exception Rate, Tool Coverage, Risk/Reversibility)
- Detailed justifications for all 9 task clusters
- Anti-pattern check (verification that not everything is "fully agentic")
- Confidence assessments per archetype

---

## Appendix D: Volume × Value Analysis Detail

See DELIVERABLE-4-VOLUME-VALUE.md for:
- Volume scoring breakdown (all 9 clusters)
- Non-determinism scoring breakdown (all 9 clusters)
- Economic validation (payback analysis, ROI projections)
- Multi-agent strategy (bundling for improved value)
- Alternative framing (non-monetary benefits: compliance de-risking, scalability, decision quality)

---

## Appendix E: Agent Specification Detail

See DELIVERABLE-5-AGENT-PURPOSE.md for:
- Complete 10-section agent design spec
- Autonomy matrix (decision points + control boundaries)
- Activity catalog (9 distinct agent operations)
- Failure modes & recovery (8 failure scenarios with mitigations)
- System & data requirements (6 source systems, 4 data entities, schemas)
- Escalation workflows (3 detailed workflow diagrams)
- Build prompt for implementation team

---

## Summary Assessment

This HR Onboarding scenario demonstrates the ATX methodology's power: **structured, evidence-based reasoning about delegation boundaries**.

### What We Learned

1. **Not everything should be agentic.** While 50% of work is rule-based, the remaining 50% has meaningful judgment or risk that warrants human involvement.

2. **Volume alone doesn't justify agent development.** With ~73 hires/person/year, the coordination workload is real but not massive. ROI is marginal unless hiring scales or strategic value is prioritized.

3. **Compliance requirements shape architecture.** I-9 monitoring is non-negotiable (federal mandate); it drives mandatory escalation logic and becomes part of the core agent even if ROI is borderline.

4. **Data integration is the constraint.** Technical risk (API availability) is higher than functional risk (agent logic is deterministic). Technical audit before build commitment is essential.

5. **Phased approach reduces risk.** Build simple, high-confidence agent first (Cluster 6 + Cluster 7); prove ROI; then expand to secondary agents (Clusters 3–5) once organization is comfortable.

### Gate 2 Readiness

This assessment meets Week 2 Gate 2 criteria:

- ✅ **Discovery:** 6 design-changing questions identified; assumptions validated with confidence levels
- ✅ **Cognitive Load:** 4 JtDs decomposed into 16 zones; breakpoints mapped
- ✅ **Suitability:** All 9 task clusters scored; archetypes assigned with justification; anti-patterns checked
- ✅ **Prioritization:** Primary target identified (Cluster 6 + 7); value calculated (18/25); ROI modeled
- ✅ **Agent Spec:** Comprehensive 10-section buildable specification provided; build prompt included
- ✅ **Assumptions:** All critical assumptions documented with verification methods
- ✅ **Recommendation:** Clear phased path forward with success criteria and go/no-go gates

**Verdict:** Ready to proceed to build phase with pre-build stakeholder validation.

---

**End of Consolidated Deliverable**

*Document prepared by Assessment Team*  
*Date: February 2025*  
*Scenario: KTB-1-109 HR Onboarding Coordination*  
*Week 2 ATX Methodology*
