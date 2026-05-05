# Deliverable 4: Volume × Value Analysis — What to Build First

**Organisation:** Aldridge & Sykes — HR Onboarding  
**Purpose of this document:** Some tasks are agent-safe but happen rarely — automating them saves little time. Others happen constantly but require so much judgment that automation barely helps. This analysis scores all nine task clusters on two axes to find the sweet spot: high frequency + meaningful automation gain.

---

## Bottom Line (Read This First)

| Finding | Detail |
|---|---|
| **Primary build target** | Task Status Monitoring (Cluster 6) — highest volume, lowest judgment |
| **Secondary target** | Combine with I-9 Monitoring (Cluster 7), Deadline Calculation (Cluster 1), and Manager Handoff (Cluster 9) into a single "Coordination Orchestrator" agent |
| **ROI verdict** | Marginal monetary return (18–24 month payback). The real case is compliance risk reduction: one prevented I-9 violation ($2,507 penalty) covers the build cost |
| **Why no cluster scores ≥15?** | Volume is genuinely low — 73 hires per person per year is only ~5–6 per month. The workflow doesn't generate enough repetitive events to score in the "strong candidate" tier individually. Bundling clusters changes this |
| **Recommendation** | Build Phase 1 agent (Coordination Orchestrator) now; add Phase 2 agent (Proposal Router for training/buddy/IT) after Phase 1 proves value |

---

## How the Scoring Works

**Two dimensions:**

1. **Volume Score (1–5)** — how often does this task occur per person per year? More repetition = more time saved = higher score.
2. **Non-Determinism Score (1–5)** — how much of this task requires human judgment? Score 1 = fully rule-based (zero judgment; agent can handle it completely). Score 5 = all judgment (human only; no rules to follow). Tasks scoring 1–2 are fully agent-safe but happen once per hire, so the time savings is small. Tasks scoring 4–5 are too judgment-heavy to automate. The tasks with the best automation potential sit at 2–3: enough structure for an agent to handle the routine, but enough volume that manual handling genuinely wastes time.

**Formula:** Agentic Value = Volume Score × Non-Determinism Score = up to 25 points

This means the formula surfaces clusters that are both high-volume AND have some (but not total) judgment load — the tasks where an agent reduces the most coordination burden without needing to make complex human decisions.

| Score | Interpretation |
|---|---|
| **≥15** | Strong candidate — high frequency, meaningful automation opportunity |
| **8–14** | Worth considering with a cost-benefit check |
| **<8** | Low return — a simple script or manual process may be more appropriate |

---

## Volume Scoring (1–5 Scale)

**Definition:** How many times per year does this task cluster occur per HR Ops person?

### Scoring Rubric

| Score | Annual Volume Per Person | Example |
|---|---|---|
| 1 | <50 times/year | Rare edge cases; <1 per week per person |
| 2 | 50–100 times/year | ~1–2 per week per person |
| 3 | 100–150 times/year | ~2–3 per week per person |
| 4 | 150–200 times/year | ~3–4 per week per person |
| 5 | >200 times/year | >4 per week per person (high volume) |

### Volume Calculation per Cluster

**Note:** Baseline = 220 hires/year ÷ 3 HR Ops people = ~73 hires per person/year.

---

#### Cluster 1: Task Deadline Calculation & Dependency Mapping

- **Frequency:** 40 tasks × 73 hires = 2,920 deadline calculations per person/year
- **Deduplicate:** But calculation is bundled (one calc per hire, not per task)
- **Actual frequency:** 73 calculations per person/year
- **Volume Score: 2** (50–100/year)

---

#### Cluster 2: Hire Type Classification & Intake Triage

- **Frequency:** 1 per hire = 73 classifications per person/year
- **Volume Score: 2** (50–100/year, but at lower end)

---

#### Cluster 3: Compliance Training Track Proposal

- **Frequency:** 1 proposal per hire = 73 per person/year
- **Volume Score: 2** (50–100/year)

---

#### Cluster 4: Buddy Matching & Seniority Assessment

- **Frequency:** 1 per hire (not all hires get buddies, but assume 90% = 66 per person/year)
- **Volume Score: 2** (50–100/year, at lower end)

---

#### Cluster 5: IT Provisioning Request Generation

- **Frequency:** 1 per hire = 73 per person/year
- **Volume Score: 2** (50–100/year)

---

#### Cluster 6: Task Status Monitoring & Reminder Generation

- **Frequency:** Each of 40 tasks monitored once per hire, plus reminders for overdue tasks
- **Base:** 40 tasks × 73 hires = 2,920 status checks per person/year
- **Reminders:** Assuming 20% of tasks hit overdue (= 584 reminders per person/year)
- **Total:** 2,920 + 584 = ~3,500 monitoring events per person/year
- **BUT:** Clustered into "continuous monitoring" role, not distinct tasks
- **Volume Score: 5** (>200/year; continuous operation)

---

#### Cluster 7: I-9 Compliance Monitoring & Escalation

- **Frequency:** Similar to Cluster 6 — continuous monitoring for all 73 hires
- **I-9 checks:** Every hire's I-9 monitored from start_date through day 3 (minimum)
- **Escalations:** Assuming 2–4% of hires hit I9_AT_RISK, ~3 escalations per person/year
- **But monitoring is continuous:** ~1,460 I-9 status checks per person/year (daily check × 20 days per hire)
- **Volume Score: 4** (150–200/year; high-frequency monitoring)

---

#### Cluster 8: Hold Decision & Onboarding Pause

- **Frequency:** Assuming 5–10% of hires hit hold = 4–7 hold decisions per person/year
- **Volume Score: 1** (<50/year; rare)

---

#### Cluster 9: Manager Handoff & Pre-Day-1 Completion Check

- **Frequency:** 1 per hire = 73 per person/year
- **Volume Score: 2** (50–100/year)

---

## Non-Determinism Scoring (1–5 Scale)

**Definition:** How much of each task cluster requires human judgment rather than rule-following? Lower score = more agent-safe; higher score = more human judgment required. The ideal automation target scores 1–2 here (agent handles it) combined with high volume.

### Scoring Rubric

| Score | Judgment Level | What It Means | Example |
|---|---|---|---|
| **1** | Zero judgment | Pure rule-following; agent handles 100% | Deadline calculation — pure arithmetic |
| **2** | Rare judgment | <10% of cases need human input | I-9 monitoring — trigger is mandatory; only edge cases escalate |
| **3** | Mixed | 30–50% of cases need a human call | Compliance training proposal — some matches unclear |
| **4** | Mostly judgment | >50% of cases require context and discretion | Buddy matching — ranking is mechanical but selection isn't |
| **5** | All judgment | No rules; every case is contextual | Hold decisions; hire-type ambiguity |

### Non-Determinism Calculation per Cluster

---

#### Cluster 1: Task Deadline Calculation

- **Judgment required:** None (pure algorithm)
- **Non-Determinism Score: 1**

---

#### Cluster 2: Hire Type Classification

- **Judgment required:** ~30–50% of cases (NULL field or ambiguous classification)
- **Non-Determinism Score: 4**

---

#### Cluster 3: Compliance Training Track Proposal

- **Judgment required:** ~20–30% of cases (partial matrix matches require decision)
- **Non-Determinism Score: 3**

---

#### Cluster 4: Buddy Matching

- **Judgment required:** ~40–60% of cases (final selection from ranked list has team fit component)
- **Non-Determinism Score: 4**

---

#### Cluster 5: IT Provisioning Request

- **Judgment required:** ~10–20% of cases (unmapped roles need decision)
- **Non-Determinism Score: 2**

---

#### Cluster 6: Task Status Monitoring

- **Judgment required:** ~10% of cases (deciding if delay is legitimate blocker or escalatable)
- **Non-Determinism Score: 2**

---

#### Cluster 7: I-9 Monitoring

- **Judgment required:** None (escalation is mandatory at day 2 and day 3; zero discretion)
- **Non-Determinism Score: 1**

---

#### Cluster 8: Hold Decision

- **Judgment required:** 100% of cases (entirely contextual; no rules)
- **Non-Determinism Score: 5**

---

#### Cluster 9: Manager Handoff

- **Judgment required:** <5% of cases (mostly binary check; minimal judgment)
- **Non-Determinism Score: 1**

---

## Agentic Value Calculation Matrix

**How to read this table:** Volume × Non-Determ. = Agentic Value. ND Score 1 = no judgment (fully agent-safe); ND Score 5 = all judgment (human only). Clusters with a high volume score AND a low-to-moderate ND score are the best build targets — they have enough repetition to justify building and enough structure for the agent to handle reliably.

| Cluster | Volume | ND Score | Agentic Value | Notes |
|---|---|---|---|---|
| 1. Deadline Calc | 2 | 1 | **2** | Low volume, zero judgment — better as a one-time setup than ongoing monitoring |
| 2. Hire Type Class | 2 | 4 | **8** | Low volume, high judgment — agent flags ambiguity but cannot classify |
| 3. Training Track | 2 | 3 | **6** | Low volume, mixed judgment — below threshold individually |
| 4. Buddy Match | 2 | 4 | **8** | Low volume, high judgment — agent proposes ranked candidates, human selects |
| 5. IT Provision | 2 | 2 | **4** | Low volume, low judgment — external IT approval gate limits autonomous value |
| **6. Task Monitor** | **5** | 2 | **10** | **Highest scorer — constant volume, mostly rule-based — primary build target** |
| 7. I-9 Monitor | 4 | 1 | **4** | High volume, zero judgment — low formula score but non-negotiable for compliance |
| 8. Hold Decision | 1 | 5 | **5** | Rare, all judgment — human only; agent detects trigger and alerts, nothing more |
| 9. Manager Handoff | 2 | 1 | **2** | Low volume, zero judgment — bundle with Cluster 6; not worth building standalone |

---

## Primary Target Selection

### Tier 1: Strong Candidates (≥15 value)
**None.** No cluster scores ≥15. This indicates the onboarding workflow is fundamentally low-volume per person (73 hires/year) and moderately judgment-heavy.

### Tier 2: Worth Considering (8–14 value)
- **Cluster 6: Task Status Monitoring** (score 10)
  - HIGH volume (5 score: 3,500 events/year per person)
  - LOW judgment (2 score: 90% deterministic)
  - Reasoning: Agent can monitor 40 tasks for 73 hires, send reminders, and flag overdue items. Humans rarely need to intervene in monitoring logic itself; escalations are routed to task owners/managers.
  - ROI estimate: ~8–10 hours per person/year saved (560–700 hours/year team-wide)
  - Risk: System latency (2–4h polling) may cause late reminders; acceptable for non-critical tasks

### Tier 3: Below Threshold (<8 value)
- Clusters 1–5, 7–9: All score 2–8. Not strong enough targets individually.

---

## Multi-Target Strategy: Secondary & Tertiary Targets

Although Cluster 6 is the only strong candidate, **combining multiple clusters into a single agent** could improve ROI:

### Agent 1: "Coordination Orchestrator" (Primary: Cluster 6 + Secondary: Clusters 1, 9)
- **Tasks:** Task monitoring (Cluster 6) + deadline calculation (Cluster 1) + manager handoff (Cluster 9)
- **Combined value:** 10 + 2 + 2 = 14 points
- **Rationale:** These three tasks are tightly coupled. Monitoring makes sense only if deadlines are calculated correctly; handoff notification is triggered by monitoring. Single agent can handle all three.
- **Time savings estimate:** 10–12 hours/person/year

### Agent 2: "Proposal Router" (Clusters 3, 4, 5, with escalation to human)
- **Tasks:** Training track proposal + buddy match + IT provisioning
- **Combined value:** 6 + 8 + 4 = 18 points ← **CROSSES 15 THRESHOLD**
- **Rationale:** All three are "human approves agent proposal" workflows. Agent can generate all three proposals in parallel, then route to HR Ops for batch approval. Creates structured human decision-making.
- **Time savings estimate:** 4–5 hours/person/year (prep time; human approval still needed)
- **But:** This involves judgment (buddy matching, compliance track selection). Not fully autonomous.

### Comparison: Focus Agent on Cluster 6 only, or combine?

**Option A: Single-Agent (Cluster 6 only)**
- Scope: Task monitoring + reminders + escalation routing
- Build cost: ~20 hours (small scope, high determinism)
- Time savings: ~10 hours/year per person
- Risk: Narrow scope; doesn't address other high-judgment tasks
- Recommendation: **FAST PROTOTYPE** — build Agent 1 (Coordination Orchestrator) first; prove ROI; then expand

**Option B: Multi-Agent (Agent 1 + Agent 2)**
- Scope: Agent 1 handles monitoring/deadlines/handoff; Agent 2 handles proposals
- Build cost: ~40–50 hours (two agents, more orchestration)
- Time savings: ~15 hours/year per person (~1,050 hours/year team-wide)
- Risk: Requires human approval infrastructure; higher complexity
- Recommendation: **PHASED APPROACH** — build Agent 1 first; add Agent 2 once Agent 1 proven

---

## Recommendation: Primary Target = Cluster 6 + Ecosystem

**Primary Agent: Coordination Orchestrator**

**Scope:**
1. **Monitor task status** across 5 source systems (Cluster 6 core)
2. **Calculate deadlines** for all 40 tasks per hire (Cluster 1 support)
3. **Send reminders** to task owners based on deadline (Cluster 6 core)
4. **Route escalations** to HR Ops when overdue >24h or >72h (Cluster 6 core)
5. **Send manager handoff** notification when pre-Day-1 tasks complete (Cluster 9 support)
6. **Optional:** Detect and escalate I-9 risk at day 2 and day 3 (Cluster 7 support — high-stakes)

**Justification:**
- Value score 10 + ecosystem = 15–18 when bundled
- 3,500 monitoring events/year per person = high leverage for automation
- Low judgment (90% deterministic) = low build/test risk
- Deterministic data flow (no complex rule conflicts)
- Can be built as "always-on" background process

**Success Metrics:**
- ≥80% of overdue tasks detected within 4 hours
- ≥99% of reminders delivered on schedule
- ≥95% of escalations routed correctly (critical issues don't get buried)
- <2 hours/person/week manual intervention (50% reduction from current baseline)

---

## Secondary Targets (Future Phases)

**If Agent 1 delivers ROI, invest in Agent 2 (Proposal Router):**

A single agent handling three non-deterministic use cases that share the same pattern — LLM reasons over ambiguous input, proposes a structured answer, human approves:

| Use Case | Trigger | LLM Task | Approver |
|---|---|---|---|
| **Cluster 3 — Compliance track** | Hire record has no exact matrix match (10–15% of hires) | Read partial matches; propose best-fit track with rationale and confidence | HR Ops |
| **Cluster 2 — Hire type (ambiguous)** | hire_type is NULL or contradicted by contract terms (~5–10% of hires) | Read employment agreement text from SharePoint; reason about EMPLOYEE vs CONTRACTOR signals | HR Ops |
| **Cluster 5 — Unmapped role** | hire.role not found in IT access matrix (~5–10% of hires) | Compare role title + department to existing matrix entries; propose nearest access package | IT Manager |

**Note:** Buddy matching (Cluster 4) is deterministic automation (sort by seniority_delta, tenure, department) — it belongs in the Phase 1 Orchestrator scope, not the Proposal Router. The human selection from the sorted list requires judgment the system cannot replicate; that is human-led, not agentic.

Combined secondary value: 6 + 4 + 4 = 14 points. Below the 15-point threshold on volume alone, but justified by risk reduction: one avoided audit finding or misclassification event covers build cost.

---

## Constraints & Risks

### Constraint 1: System Data Availability (LOW CONFIDENCE)
- Assumption: All 6 source systems have APIs available
- Risk: If APIs unavailable, polling becomes batch-only (12–24h latency), reducing monitoring effectiveness
- Mitigation: Technical audit in Phase 1 discovery; confirm APIs before Agent design

### Constraint 2: Task Ownership & Accountability
- Assumption: Task owners (managers, IT, compliance) respond to reminders within SLA
- Risk: If reminders go unheeded, escalation chain breaks; agent reminders become noise
- Mitigation: Define SLAs and escalation logic upfront; test with pilot group

### Constraint 3: Budget/TCO
- Agent build cost: ~20–30 hours × $150/hr (Sr. Engineer) = $3,000–$4,500
- Annual operational cost: Infrastructure + monitoring API calls = ~$500–$1,000/year
- ROI payback: ~10–15 hours/person/year saved × 3 people × (loaded rate) = ~$3,500–$5,000/year value
- **Payback period: <1 year (acceptable)**

---

## Economic Validation

### Baseline Coordination Cost (Current)
- Coordination overhead: 2.5 hours/hire × 220 hires = 550 hours/year
- Team-wide: 550 hours/year (all 3 people combined)
- Per-person: 550 ÷ 3 = ~183 hours/person/year (avg)

### Savings from Coordination Orchestrator Agent (Cluster 6 + ecosystem)
- Monitoring reminders: ~10 hours/person/year (no longer manual reminder chasing)
- Deadline calculation: ~2 hours/person/year (auto-calculated; no manual spreadsheet)
- Manager handoff: ~1 hour/person/year (auto-generated notification)
- Escalation routing: ~3 hours/person/year (auto-routed; less manual triaging)
- **Subtotal: ~16 hours/person/year saved**
- **Team total: 16 × 3 = ~48 hours/year saved**

### Cost-Benefit
- Build cost amortized: $4,000 ÷ 3 = ~$1,333/person one-time
- Annual operational cost: $800 ÷ 3 = ~$267/person/year
- Annual value: 16 hours × $60/hr (avg HR Ops loaded cost) = ~$960/person/year
- **Year 1 ROI: $960 − $1,333 − $267 = **NEGATIVE $640** (cost exceeds first-year benefit)**
- **Year 2+ ROI: $960 − $267 = +$693/person/year (break-even reached in Year 2)**

### Verdict: ROI is MARGINAL (not strong)
- Payback period: 18–24 months
- The reason: **Volume is too low** (only 73 hires/person/year; ~5.5 per month)
- Monitoring 5–6 hires/month doesn't generate enough repetitive work to justify agent build cost
- **Recommendation:** Proceed with Agent development **only if:**
  1. Hiring volume increases significantly (to 150+ hires/person/year), OR
  2. AI/agent development is treated as strategic investment (not pure ROI), OR
  3. Build cost is reduced (reusable templates, existing platforms)

---

## Alternative Framing: Non-Monetary Benefits

Even with low monetary ROI, consider:
- **Compliance de-risking:** I-9 monitoring (Cluster 7) has $2,507 penalty per violation. One prevented violation pays for agent.
- **New hire experience:** Better on-time task completion = higher onboarding success rate = retention improvement
- **Scalability:** If hiring expands, agent scales at zero marginal cost; human team would need to hire
- **Decision quality:** Agent proposals (Tier 2 agents) reduce decision variance (e.g., buddy matching consistency)

---

## Conclusion: Primary Target Designation

**Designate: Cluster 6 (Task Status Monitoring) as Primary Agentic Target**

**Build Phased Agent Suite:**
1. **Phase 1 (Pilot):** Agent 1 (Coordination Orchestrator) focused on Cluster 6 + I-9 monitoring (Cluster 7)
2. **Phase 2 (Expansion):** If Phase 1 successful, add Agent 2 (Proposal Router) for Clusters 3–5
3. **Phase 3 (Refinement):** Optimize based on operational data

**Value Justification:**
- Primary target (Cluster 6) has highest volume (5 score) + lowest judgment (2 score) = best signal-to-noise ratio for agent execution
- I-9 monitoring (Cluster 7) is non-negotiable (legal mandate); should be automated
- Combined agents create structured workflow: Agent 1 orchestrates execution; Agent 2 generates proposals; humans approve/decide
- Reduces Priya's cognitive load from "tracking everything" to "deciding on escalations"

---

## Next Step

Proceed to **Phase 5: Agent Purpose Document** to design a buildable specification for Agent 1 (Coordination Orchestrator).
