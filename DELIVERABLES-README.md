# Week 2 ATX Assessment — Deliverables Guide

**Scenario:** KTB-1-109 HR Onboarding Coordination  
**Assessment Date:** February 2025  
**Scope:** 7-Phase ATX Methodology Application  

---

## What This Assessment Contains

This folder contains a complete Week 2 ATX (Agentic Transformation) assessment of the HR Onboarding Coordination scenario. The assessment applies evidence-driven methodology to determine **where agents should operate** in the business process, **why**, and **how to build with intentional delegation boundaries**.

---

## Document Navigation

### 📄 START HERE: Consolidated Submission
**File:** `WEEK2-ASSESSMENT-CONSOLIDATED.md`  
**Use this for:** Executive summary, overview, Gate 2 submission  
**Length:** ~8,000 words  
**Contains:** Executive summary + all 5 phase outputs + recommendations + appendices

---

### 🔍 Phase-by-Phase Breakdown

#### Phase 1: Discovery Questions (Understand the Work)
**File:** `DELIVERABLE-1-DISCOVERY-QUESTIONS.md`  
**Length:** ~3,500 words  
**Key Output:**
- 6 design-changing discovery questions (not generic questions)
- 6 critical assumptions with confidence levels (LOW/MEDIUM/HIGH)
- Grounding in Week 1 spec artefacts (lived-work signals)
- Implications for agent delegation boundaries
- Validation methods for each assumption

**Read this if:** You want to understand what we don't know about the process, or see examples of how to frame discovery questions.

---

#### Phase 2: Cognitive Load Map (Decompose the Work)
**File:** `DELIVERABLE-2-COGNITIVE-LOAD-MAP.md`  
**Length:** ~4,500 words  
**Key Output:**
- 4 Jobs to be Done (JtDs) with cognitive contracts
- 16 cognitive zones per JtD (micro-task decomposition)
- Cognitive zones with Input/Decision/Output tables
- 8 control handoffs (breakpoints) showing where control passes between agent, human, and systems
- Evidence grounding linking zones to spec sections

**Read this if:** You want to understand the detailed workflow decomposition, or see examples of cognitive zone mapping.

---

#### Phase 3: Delegation Suitability Matrix (Score & Assign Archetypes)
**File:** `DELIVERABLE-3-DELEGATION-MATRIX.md`  
**Length:** ~3,000 words  
**Key Output:**
- 5-point scoring rubrics for decision determinism, tool coverage, exception rate, risk/reversibility
- 9 major task clusters scored on each dimension
- Archetype assignment for each cluster (Fully Agentic / Agent-Led + Oversight / Human-Led + Support / Human Only)
- Anti-pattern check (verifying delegation boundaries are intentional, not everything is "fully agentic")
- Confidence assessments per assumption

**Read this if:** You want to see how suitability scoring works, or understand why certain tasks are/aren't delegated to agents.

---

#### Phase 4: Volume × Value Analysis (Prioritize Targets)
**File:** `DELIVERABLE-4-VOLUME-VALUE.md`  
**Length:** ~4,000 words  
**Key Output:**
- Volume scoring (1–5 scale) for all 9 clusters
- Non-determinism scoring (1–5 scale) for all 9 clusters
- Agentic Value calculation (Volume × Non-Determinism = 1–25 scale)
- Primary target identification (Task Status Monitoring = 10/25; strong candidate when bundled)
- Economic validation (ROI analysis, payback period, non-monetary benefits)
- Multi-agent strategy (phased approach: Agent 1 primary, Agent 2 secondary)

**Read this if:** You want to understand the prioritization methodology, or see economic justification for agent investment.

---

#### Phase 5: Agent Purpose Document (Design the Agent)
**File:** `DELIVERABLE-5-AGENT-PURPOSE.md`  
**Length:** ~6,000 words  
**Key Output:**
- Comprehensive 10-section agent specification:
  1. Purpose statement
  2. Scope (In/Out/Escalation boundaries)
  3. Autonomy matrix (decision points + control boundaries)
  4. Activity catalog (9 distinct operations the agent performs)
  5. Key performance indicators (operational, outcome, business)
  6. Failure modes & recovery (8 scenarios with mitigations)
  7. System & data requirements (6 source systems, schemas, APIs)
  8. Escalation & human oversight (workflows, approval gates)
  9. Assumptions & confidence levels
  10. Build prompt for implementation team

**Read this if:** You want to understand the detailed agent specification, or need the build prompt to give to your engineering team.

---

### 📋 Reference Materials

#### Quick Facts & Numbers
- **Organization:** Aldridge & Sykes (Manchester, 1,200 employees)
- **Team:** 3-person HR Ops
- **Volume:** 220+ hires/year (~73 per person, 4–5 per week)
- **Coordination overhead:** 2.5 hours/hire = 550 hours/year team-wide
- **Tasks:** 40 per hire across PRE_DAY_1, POST_DAY_1, ONGOING categories
- **Systems:** 6 disconnected (HRIS, IT provisioning, LMS, calendar, email, fulfillment)
- **Judgment split:** 85% routine, 15% judgment-required
- **Success targets:** ≥97% on-time, 0 I-9 violations, ≥95% escalations routed correctly

#### Key Findings Summary
- **Viable agent target:** Task Status Monitoring (Cluster 6) + I-9 Compliance Monitoring (Cluster 7)
- **Agentic value:** 18/25 (strong candidate)
- **Delegation profile:** 50% automatable, 35% oversight, 15% human-only
- **ROI:** Marginal monetary ROI (18–24 month payback), strong compliance value
- **Critical risk:** API availability for 6 source systems (LOW confidence)
- **Recommendation:** Phased build (Agent 1 primary, Agent 2 secondary)

#### Critical Assumptions (Confidence Levels)
| Assumption | Confidence |
|---|---|
| API access for all 6 systems | **LOW** |
| Compliance matrix current & maintained | **LOW** |
| HR Ops responds to escalations within SLA | **MEDIUM** |
| 2.5h baseline is accurate | **MEDIUM** |
| Buddy eligibility rules in HRIS | **LOW** |
| Hold decisions <5% of hires | **MEDIUM** |

---

## How to Use This Assessment

### For Gate 2 Submission
1. **Read:** `WEEK2-ASSESSMENT-CONSOLIDATED.md` (executive summary)
2. **Review:** Executive Summary section for 5 key findings
3. **Submit:** Entire consolidated document + appendix references

### For Stakeholder Alignment
1. **Present:** Executive Summary (2 min)
2. **Deep dive:** Delegation Suitability Matrix (why agent should do X, human should do Y)
3. **Address concerns:** Critical Assumptions & Validation Methods section
4. **Outline next steps:** Recommendations & Gates section

### For Technical Implementation
1. **Start with:** Phase 5 Agent Purpose Document
2. **Extract:** Section 10 (Build Prompt) → give to engineering team
3. **Reference:** Sections 7 & 8 (System/Data Requirements + Escalation Workflows)
4. **Confirm:** Pre-Build Validation Checklist before committing resources

### For Continuous Learning
1. **Discovery methodology:** Phase 1 (how to find design-changing questions)
2. **Decomposition technique:** Phase 2 (cognitive zones, breakpoints)
3. **Scoring rubrics:** Phase 3 (how to apply 5-point scales consistently)
4. **Prioritization logic:** Phase 4 (when to invest in agent development)
5. **Specification writing:** Phase 5 (how to write buildable agent specs)

---

## Key Methodological Insights

### Why Each Phase Matters

**Phase 1 (Discovery)** forces you to articulate what you don't know. It prevents you from building assumptions into the agent design. "What if all 6 systems have no APIs?" changes everything.

**Phase 2 (Cognitive Load)** prevents you from treating the workflow as a monolithic "process." Breaking it into zones reveals where humans can't be replaced (judgment calls) and where automation is straightforward (rule-based sequencing).

**Phase 3 (Suitability)** ensures delegation decisions are intentional, not default. Scoring rubrics force consistency. Anti-pattern checks prevent "let's just make everything fully agentic."

**Phase 4 (Prioritization)** prevents gold-plating. Not every rule-based task is worth automating. Volume + determinism score reveals high-leverage targets.

**Phase 5 (Specification)** bridges the gap between assessment and build. It's not enough to say "the agent should monitor tasks." You must specify exactly what "monitor" means, what escalations look like, and how failures are handled.

### Anti-Patterns This Assessment Detects

| Anti-Pattern | What Goes Wrong | How We Prevent It |
|---|---|---|
| "Everything is fully agentic" | Agent ends up making judgment calls it shouldn't; compliance risk | Archetype matrix shows delegation varies; <80% agentic |
| "Assumptions are hidden" | Build proceeds on wrong assumptions; fails in production | All assumptions listed with confidence + validation method |
| "ROI looks better than it is" | Agent costs more to maintain than it saves | Economic validation section shows 18–24 month payback (realistic) |
| "Spec is too vague for build" | Engineers guess about escalation logic; inconsistent behavior | Phase 5 spec includes decision tables, failure modes, test cases |
| "No discovery = integration friction" | Agent can't call APIs; fallback to manual; ROI collapses | Phase 1 identifies 6 critical unknowns; tech audit gates build |

---

## Next Steps (Post-Gate 2)

### If Assessment is Approved (Green Light)
1. **Week 1–2:** Technical audit (API availability, system integration)
2. **Week 3:** Stakeholder alignment meeting (confirm escalation workflows)
3. **Week 4–6:** Build Phase 1 Agent (Coordination Orchestrator)
4. **Week 7:** Pilot with 5–10 hires
5. **Week 8–9:** Review pilot results, iterate
6. **Week 10+:** Full rollout + Phase 2 Agent (Proposal Router)

### If Blockers Are Found (Red Light)
- **Option A:** Delay until APIs available
- **Option B:** Use alternative architecture (batch polling instead of real-time)
- **Option C:** Focus on Phase 2 agents (Proposal Router) which have lower integration complexity

### Success Criteria for Pilot
- ✅ ≥80% of overdue tasks detected within 4 hours
- ✅ ≥99% of reminders delivered successfully
- ✅ ≥95% of critical escalations routed correctly
- ✅ Zero I-9 violations during 30-day pilot
- ✅ <2 hours/person/week manual intervention

---

## Questions & Troubleshooting

**Q: Why is the ROI so marginal?**  
A: Volume is low (73 hires/person/year). With only ~5 hires/week, there isn't enough repetition to justify expensive agent development. ROI improves if hiring scales 2x or if compliance value (I-9 violation prevention) is prioritized.

**Q: Why not automate everything?**  
A: Some tasks (hire type classification, buddy selection, hold decisions) involve judgment, organizational knowledge, or legal implications that require human accountability. Automating them would introduce risk > benefit.

**Q: What if API access isn't available?**  
A: Agent effectiveness drops significantly. We'd need to fall back to batch polling (12–24h latency), which defeats the purpose of reminders. Technical audit is a gate.

**Q: Should we build the agent anyway?**  
A: Only if (1) strategic value is high (compliance de-risking, experience improvement), or (2) hiring volume is expected to grow significantly, or (3) agent development is treated as a capability-building investment, not a quick ROI play.

**Q: When should we build Agent 2 (Proposal Router)?**  
A: After Agent 1 is live and proving value in pilot. Don't overcommit resources until you know Agent 1 works.

---

## Document Maintenance

These deliverables are static snapshots of the assessment. If the business context changes (hiring volume increases, systems change, new regulations), the assessment should be revisited.

**When to reassess:**
- Hiring volume changes >50%
- New source system added or existing system replaced
- Regulatory compliance requirements change
- Pilot reveals unexpected operational constraints

---

## Contact & Support

For questions about this assessment:
- **Methodology questions:** Refer to Phase 1–5 documents
- **Agent specification questions:** Refer to Phase 5 + consolidated Executive Summary
- **Implementation questions:** Refer to Phase 5 Section 10 (Build Prompt)
- **ROI questions:** Refer to Phase 4 (Economic Validation)

---

**End of Deliverables Guide**

*Assessment completed: February 2025*  
*Scenario: KTB-1-109 HR Onboarding Coordination*  
*Methodology: Week 2 ATX (7-Phase)*
