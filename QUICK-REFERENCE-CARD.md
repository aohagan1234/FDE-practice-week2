# Quick Reference Card — Week 2 ATX Scoring & Decision Frameworks

Keep this open while working through Phases 3 and 4. Print if needed.

---

## Delegation Suitability Scoring (Phase 3)

### Input Structure (How clear are the inputs?)
| **5** | Highly Structured — Clear, validated fields; minimal ambiguity |
| **4** | Mostly Structured — Some conditional fields |
| **3** | Mixed — Combination of structured + unstructured |
| **2** | Mostly Unstructured — Primarily narrative |
| **1** | Highly Unstructured — Context-dependent, no clear fields |

### Decision Determinism (How rule-bound vs. judgment-heavy?)
| **5** | Fully Deterministic — Pure rules; no reasoning |
| **4** | Mostly Deterministic — Follows patterns, minor edge cases |
| **3** | Mixed — Core path rules, exceptions require judgment |
| **2** | Mostly Judgment — Some structure, significant judgment needed |
| **1** | Fully Judgment — Tacit knowledge; not codifiable |

### Exception Rate (What % hit edge cases?)
| **5** | Very Low (< 5%) — Almost all cases follow standard path |
| **4** | Low (5–10%) — Most standard, a few exceptions |
| **3** | Moderate (10–20%) — Significant exceptions, but majority standard |
| **2** | High (20–35%) — More exceptions than standard |
| **1** | Very High (> 35%) — Most cases are exceptions |

### Tool Coverage (Can the agent access what it needs?)
| **5** | Full Coverage — APIs for all data sources & actions |
| **4** | Mostly Covered — Agent can reach most systems; 1–2 workarounds |
| **3** | Partially Covered — 50–70% of actions; significant manual steps |
| **2** | Poorly Covered — Can access data but can't act; recommendations only |
| **1** | No Coverage — No system access; all steps manual |

### Risk/Reversibility (What happens if it fails?)
| **5** | Negligible Risk — Mistake easily spotted & reversed |
| **4** | Low Risk — Reversible; takes time to correct |
| **3** | Moderate Risk — Escalation required; minor downstream impact |
| **2** | High Risk — Significant disruption or cost |
| **1** | Critical Risk — Irreversible; severe consequences |

---

## Calculate Suitability & Agentic Value

```
Suitability Score = (Input Structure + Decision Determinism + Tool Coverage) / 3

Agentic Value = Volume Score × Non-Determinism Score
```

### Suitability Score Interpretation
- **≥ 4.5** — Likely candidate for autonomous or agent-led
- **3.0–4.4** — Requires human oversight or support
- **< 3.0** — Likely human-only or human-led

### Agentic Value Interpretation
- **≥ 15** — Strong agentic candidate
- **8–14** — Consider agentic; validate with TCO
- **< 8** — Use rules automation or don't automate

---

## Delegation Archetypes (Phase 3)

Choose one for each task cluster:

### 5 Operating Modes

| **Fully Agentic** | Agent acts autonomously within defined bounds | Deterministic + low exception + low risk + full tool coverage |
| **Agent-led + Human Oversight** | Execution delegated; supervision mandatory | High-volume structured decisions with human spot-checks |
| **Human-led + Agent Support** | Agent provides synthesis & recommendations | Complex analysis; human makes final call |
| **Human-led + Automation Support** | Tools accelerate execution; human controls | Rule-bound tasks; human prefers to retain control |
| **Human Only** | No delegation | Tacit knowledge, ethics, irreversibility |

### Decision Tree for Assignment

1. **Suitability ≥ 4.5 + Exception Rate < 5% + Risk/Reversibility 4–5** → **Fully Agentic**
2. **Suitability ≥ 4.5 + Exception Rate 5–15% + Risk/Reversibility 3–4** → **Agent-led + Human Oversight**
3. **Suitability 3.0–4.4 + Significant reasoning required** → **Human-led + Agent Support**
4. **Suitability 3.0–4.4 + Mostly rules** → **Human-led + Automation Support**
5. **Suitability < 3.0 OR Risk/Reversibility 1 OR Decision Determinism 1** → **Human Only**

---

## Volume Scoring (Phase 4)

| **5** | Hundreds+ per day OR continuous stream (250+ per week) |
| **4** | 50–200 per day (100–500 per week) |
| **3** | 10–50 per day (50–250 per week) |
| **2** | Several per day OR high volume per month (20–50 per week) |
| **1** | Weekly OR monthly (< 20 per week) |

---

## Non-Determinism Scoring (Phase 4)

| **5** | High reasoning — Multiple sources + policy interpretation + contextual judgment |
| **4** | Significant reasoning — Patterns exist but require contextual adaptation |
| **3** | Mixed — Core path rules; exceptions need judgment |
| **2** | Mostly deterministic — Small reasoning component |
| **1** | Fully deterministic — Pure rules/logic |

---

## Autonomy Matrix Template (Phase 5)

For each decision point, fill in:

```
| Decision Point | Who Decides | Criteria/Threshold | Escalation Condition |
|---|---|---|---|
| [What needs to be decided?] | Agent/Human | [Rule or criteria] | [When to hand off] |
```

**Red flag:** If the "Who Decides" column is all "Human" → you've under-delegated. If it's all "Agent" → check if you've missed exception cases.

---

## Failure Mode Recovery Template (Phase 5)

For each major risk:

```
| Failure Mode | Detection | Impact | Recovery |
|---|---|---|---|
| [What can go wrong?] | [How will you detect it?] | [Consequence if undetected] | [How to fix it?] |
```

**Minimum to cover:**
- System downtime (API fail)
- Data quality issue (stale/incomplete data)
- Escalation mistake (escalated when shouldn't)
- Execution mistake (wrote wrong value)
- Duplicate action (ran twice)

---

## Assumptions Confidence Scale

Use this when logging assumptions:

| **High** | Verified by discovery data or multiple artefacts; >85% certainty |
| **Medium** | Based on reasonable inference; need to verify during pilot; 50–85% certainty |
| **Low** | Hypothesis; not yet tested; < 50% certainty; high impact if wrong |

---

## Anti-Pattern Checklist

Before submitting your work:

- [ ] **Delegation levels are varied** (not all Fully Agentic)
- [ ] **Escalation triggers are specific** (not vague like "if complex")
- [ ] **Exception rate is explicitly called out** (not ignored)
- [ ] **Each archetype is justified** (citing evidence, not assumptions)
- [ ] **Human oversight is intentional** (not a fallback)
- [ ] **Tool coverage gaps are named** (not assumed to exist)
- [ ] **Failure modes include both detection AND recovery** (not just "what could go wrong")
- [ ] **Assumptions are marked with confidence** (unmarked inferences = bluffing)

---

## ROI Quick Calc

```
Annual Baseline = (Cases/year) × (Hours per case) × (Loaded $/hr)

Agent Cost Per Case = 
  Tokens × $/1K tokens + 
  Tool calls × $/call + 
  Infrastructure ÷ Cases/year + 
  HITL ÷ Cases/year

Annual Savings = Baseline - (Cases/year × Agent Cost Per Case)

ROI = Savings ÷ Agent Cost (should be ≥ 2:1)
```

---

## Common Problem → Solution Map

| **I see...** | **This means...** | **Fix it by...** |
|---|---|---|
| Lots of scores = 3 (mixed) | High uncertainty; unclear delegation | Get more discovery data; test assumptions |
| Suitability score 2.5, but I want "Fully Agentic" | You've under-estimated tool coverage or over-estimated determinism | Re-score based on actual data; adjust to Agent-led at best |
| Exception rate > 20% but assigning "Agent-led" | Agent will escalate constantly; no efficiency gain | Revise to "Human-led + Agent Support" or redesign to reduce exceptions |
| No escalation triggers defined | Agent won't know when to hand off; will run off the rails | Add specific decision rules: "If X < threshold, escalate to Human" |
| Risk/Reversibility score 1–2 but assigning "Fully Agentic" | High consequence if agent makes a mistake | Require human approval before execution; change to "Agent-led + Human Oversight" |
| Autonomy matrix all "Human" | Not actually an agent; just a UI wrapper | Increase agent decision authority for high-confidence cases (low exception, high determinism) |
| Autonomy matrix all "Agent" with 30% exception rate | Agent won't handle exceptions; they'll stack up | Add explicit escalation rule: "If case matches [exception pattern], escalate immediately" |

---

## Peer Review Red Flags (What to Look For in Others' Work)

When reviewing a peer's submission, flag:

- [ ] Delegation levels all Fully Agentic (the anti-pattern)
- [ ] No exception rate mentioned (critical gap)
- [ ] Escalation triggers vague ("if needed"; "if complex")
- [ ] Archetype assignments not justified with evidence
- [ ] Assumptions not marked; inferences presented as facts
- [ ] Suitability scores don't match archetype (high score = Fully Agentic; low score = Human-led)
- [ ] No mention of what happens when agent fails
- [ ] Tool coverage gaps not acknowledged
- [ ] Volume/Value analysis uses estimates, not discovery data

**Constructive feedback pattern:**
> "I see you assigned this to [Archetype]. The justification cites [evidence]. But I notice [gap]. If [assumption] is wrong, this might need [adjustment]. What's your thinking on [specific question]?"

---

## During the Build Loop (Phase 6)

When Claude asks: **"What does the agent do if [scenario]?"**

This is a **delegation boundary question**. Answer:

```
Agent: [specific rule or decision criteria]
  → If rule matches: [agent action]
  → If rule doesn't match: [escalate to Human; Human does X]
```

**Example of good answer:**
> "If candidate availability is unclear (leave calendar incomplete), agent flags the candidate but includes a note: 'Leave calendar incomplete; verify with candidate.' Priya sees this flag and makes the final call."

**Example of bad answer:**
> "Agent handles it intelligently."

(Reason: "intelligently" is not code-able. Claude needs explicit rules.)

---

## Quick Checklist: Is Your Agent Purpose Document Ready for Build Loop?

- [ ] Purpose statement is one paragraph; answers: who, problem, outcome, what agent does, what human does
- [ ] Scope is clear: 3+ "In Scope" + 3+ "Out of Scope" + 3+ "Escalation Triggers"
- [ ] Autonomy Matrix has 6+ decision points with explicit Who/Criteria/Escalation for each
- [ ] Activity Catalog has 7+ actions with inputs/outputs named
- [ ] KPIs defined at Operational, Outcome, and Business levels
- [ ] Failure Modes: 5+ scenarios with Detection and Recovery
- [ ] System/Data Requirements: all APIs, schemas, rate limits named
- [ ] Escalation workflow: specific (not "notify stakeholder"; describe the actual workflow)
- [ ] Assumptions logged with confidence levels
- [ ] Build prompt included and ready to send to Claude

---

## When to Use Each Tool

| **Need to...** | **Use this tool** | **Output** |
|---|---|---|
| Score a task on delegation suitability | Scoring rubrics (top of this card) | Scores 1–5 for each dimension |
| Calculate suitability score | Formula: (Input + Determinism + Tool) / 3 | Score 1–5 |
| Calculate agentic value | Formula: Volume × Non-Determinism | Score 1–25 |
| Assign an archetype | Decision tree (above) | One of 5 archetypes |
| Define escalation triggers | Autonomy Matrix template | Specific conditions |
| Assess if assumptions are risky | Confidence scale | High/Medium/Low |
| Find the anti-pattern in your work | Anti-Pattern Checklist | List of items to fix |
| Understand a peer's feedback | Problem → Solution Map | Specific fix |

---

## Gate 2 Rubric Snapshot

Your 7 deliverables are graded on:

1. **Cognitive Load Map** — Completeness, grounding in evidence, clarity of zones/breakpoints
2. **Delegation Suitability Matrix** — Defensible scores, varied archetypes, rationale
3. **Volume × Value Analysis** — Accuracy of data, economic viability, justification
4. **Agent Purpose Document** — Clarity, specificity, completeness, buildability
5. **System/Data Inventory** (if needed) — Completeness, accuracy, integration detail
6. **Discovery Questions** — Design-changing (not generic), grounded in gaps
7. **Assumptions Discipline** — Marked explicitly, confidence levels, impact statements

**Hidden criteria that decide close calls:**
- **Varied delegation levels** (not everything Fully Agentic)
- **Evidence-driven reasoning** (not guesses)
- **Lived work vs. documented work** (not SOP-based)

---

**Use this card. Reference it. Print it. Good luck.**
