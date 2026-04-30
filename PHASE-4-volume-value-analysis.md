# Phase 4: Volume × Value Analysis — Prioritize the Highest-Impact Target

**Goal:** Determine which work stream delivers the most agentic value and justify why it should be the agent's primary target.

**Input:** Delegation Suitability Matrix + volume/frequency data from discovery + time cost data.

---

## The Framework

Agentic value is driven by two factors:

1. **Volume (Execution Frequency):** How many times per period is this work performed?
2. **Value (Non-Deterministic Decision Effort):** How much cognitive load does each instance consume?

**Agentic Value = Volume × Non-Determinism**

The highest-value target combines high frequency + high cognitive load. This is where an agent delivers the most ROI.

---

## Scoring Volume

| Score | Execution Frequency | Interpretation |
|---|---|---|
| 5 | Hundreds+ per day or continuous stream | ~250+ per week |
| 4 | 50–200 per day | ~100–500 per week |
| 3 | 10–50 per day | ~50–250 per week |
| 2 | Several per day or high volume per month | ~20–50 per week |
| 1 | Weekly or monthly | < 20 per week |

**Record the actual volumes from your discovery:**
- "HR Onboarding: ~220 hires/year = 4–5 per week" → Score: **2–3**
- "Compliance training assignment: same 220 hires/year, plus re-assignments" → Score: **2–3**
- "Buddy matching: 220 per year = 4–5 per week" → Score: **2–3**
- "Edge-case resolution: 30–50 per year = ~1 per week" → Score: **1**

---

## Scoring Non-Deterministic Decision Effort (Value Driver)

This is **not** about technical complexity. It's about cognitive load—how much judgment, synthesis, or reasoning is required per instance?

| Score | Decision Character | Interpretation |
|---|---|---|
| 5 | High reasoning | Multiple data sources + policy interpretation + contextual judgment required (e.g., "approve hire" is judgment; "assign training" might be) |
| 4 | Significant reasoning | Patterns exist but require contextual adaptation and exception handling (e.g., "resolve escalation" combines rules + judgment) |
| 3 | Mixed | Core path is rule-based; exceptions and edge cases require reasoning (e.g., "create Workday record" is mostly rules; "assign buddy" has judgment) |
| 2 | Mostly deterministic | Small reasoning component around structured rules (e.g., "tag record" has 1–2 decision points) |
| 1 | Fully deterministic | Pure rules/logic, no reasoning (e.g., "send confirmation email") |

**Assign scores for each work stream:**
- "Create Workday record": Mostly deterministic (rules-based) → Score: **2**
- "Assign training module": Mixed (standard roles + exceptions) → Score: **3**
- "Match buddy": Significant reasoning (team fit + availability + experience) → Score: **4**
- "Resolve edge-case": High reasoning (policy interpretation + stakeholder judgment) → Score: **5**

---

## Calculate Agentic Value

```
Agentic Value Score = Volume × Non-Determinism (1–25 scale)
```

| Work Stream | Volume | Non-Determinism | Agentic Value | Interpretation |
|---|---|---|---|---|
| Create Workday record | 3 (4–5/week) | 2 (deterministic) | 6 | Low value; automation is low-cognition |
| Assign training | 3 (4–5/week) | 3 (mixed) | 9 | Medium value; volume × moderate cognitive load |
| Match buddy | 3 (4–5/week) | 4 (significant reasoning) | 12 | High value; volume × reasoning |
| Resolve edge-case | 1 (~1/week) | 5 (high reasoning) | 5 | Low value; too infrequent to justify |

**Interpretation thresholds:**
- **≥ 15:** Strong agentic candidate; justify why this isn't the target
- **8–14:** Consider agentic; validate delegation suitability + TCO
- **< 8:** Use rules automation or don't automate

---

## Volume × Value Plot

Visualize all work streams on a 2D chart:

```
           High Cognitive Load (Non-Determinism = 5)
                      |
                      |        Buddy Matching (3, 4)
                      |        Value = 12
                      |
                      |  Training Assignment (3, 3)
                      |  Value = 9
                      |
     --------+--------+--------+-------- High Frequency (Volume)
             |        |
             |        | Workday Record (3, 2)
             |        | Value = 6
             |        |
             |        | Edge-case Resolution (1, 5)
             |        | Value = 5
           Low Cognitive Load (Non-Determinism = 1)
```

The quadrant in the **upper right** (high volume + high cognition) is your target.

---

## Justification: Why This Work Stream Wins

For your top 2–3 candidates, write a brief justification:

**Example:**

> **Primary Target: Buddy Matching (Value = 12)**
>
> Buddy matching combines steady volume (4–5/week × 52 weeks = 250–260/year) with significant reasoning. The human must score candidates on team fit (subjective), availability (data-driven), and experience level (pattern-match). 
>
> An agent can:
> - Query HR system for availability + experience + team composition
> - Surface ranked candidates + reasoning
> - Let Priya make final match in ~5 minutes vs. 30 minutes of consultation
>
> Time saving: 250 × (30 - 5) min = 6,250 minutes/year = 104 hours/year of cognitive work.
>
> Risk is low: if match is bad, it's noticed by manager in first week and re-assigned. Reversible.
>
> **Secondary Target: Training Assignment (Value = 9)**
>
> Higher volume (same 250/year as buddy, but also re-assignments), but lower reasoning (mostly role-based rules with 10–15% exceptions). Lower cognitive load per instance, but still valuable at scale.
>
> **Why not Edge-case Resolution (Value = 5)?**
>
> Infrequent (1/week = 50/year). While each case consumes 4 hours of high-cognition work, the total annual load is ~200 hours. The buddy matching + training assignment combo (250 × 25 min = 6,250 min ≈ 104 hours) and (250 × 15 min = 3,750 min ≈ 62 hours) = 166 hours saves more total time. Plus, edge cases are higher risk; Priya prefers to keep these human-led.

---

## Economic Reality-Check

Before selecting your primary target, verify the math closes:

```
Annual baseline cost = Cases/year × Time per case (hours) × Fully-loaded hourly cost

Example (Buddy Matching):
- Cases/year: 250
- Time per case: 0.5 hours
- Fully-loaded cost/hour: £75 (salary + benefits + overhead)
- Annual baseline: 250 × 0.5 × £75 = £9,375

Agent cost model (estimate):
- Avg input tokens: 2,000 × £0.001/1K tokens = £2
- Avg output tokens: 500 × £0.003/1K tokens = £1.50
- Tool calls: 3 API calls × £0.10/call = £0.30
- Total per case: £3.80
- Annual agent cost: 250 × £3.80 = £950
- Savings: £9,375 - £950 = £8,425 (90% cost reduction)
```

If the math doesn't close, either:
- Pick a higher-volume target
- Revisit your assumption about time saved per case
- Consider cost ≠ ROI justification (time freed for higher-value work)

---

## Grounding in Evidence & Assumptions

For each claim, cite discovery or evidence:

| Claim | Evidence | Confidence | Assumption |
|---|---|---|---|
| Buddy matching: 4–5/week | Hiring plan in HR records shows ~220/year | High | Assuming no backlog; hiring is steady |
| Time per buddy match: 30 min | Priya's calendar shows 1-2 buddy matching blocks/week of 1-2 hours for 2–4 matches | Medium | Assuming calendar time ≈ actual time (not including hidden context-switching) |
| Exception rate 5–10% | Email thread artefact X shows manager escalation ~3 times in sample of 50 matches | Low | Small sample; need more data to confirm |

---

## Output: Volume × Value Analysis Document

```markdown
# Volume × Value Analysis: [Process Name]

## Agentic Value Scores

| Work Stream | Volume | Non-Determinism | Value | Threshold |
|---|---|---|---|---|
| [Name] | [Score] | [Score] | [Score] | [≥15/8–14/<8] |
| [Name] | [Score] | [Score] | [Score] | [≥15/8–14/<8] |

## Primary Target: [Name]

**Justification:**
- Highest value score ([X]); combines [high/steady] volume with [significant/moderate] cognitive load
- Time saving: [calculation] hours/year
- Risk level: [low/moderate/high]
- Reversibility: [easily/can be/difficult to correct mistakes]

**Economic viability:**
- Annual baseline: £[X]
- Estimated agent cost: £[X]
- Net savings: £[X] ([X]% reduction)

## Secondary Targets (if applicable)

[List with rationale]

## Why Not [High-Risk or Low-Value Option]?

[Brief explanation]

## Grounding & Assumptions

[Table of evidence vs. assumptions with confidence levels]
```

---

## Next Step

Once your primary target is selected and justified, move to **Phase 5: Agent Purpose Document**.
