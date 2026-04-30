# Phase 3: Delegation Suitability Matrix — Score & Assign Archetypes

**Goal:** Determine which work can be delegated, at what autonomy level, and with what guardrails.

**Input:** Cognitive Load Map + discovery insights + ATX scoring reference.

---

## What You're Scoring

For each major JtD or task cluster, score on **5 dimensions**:

| Dimension | What it measures | Scoring |
|---|---|---|
| **Input Structure** | How well-defined and structured is the input data? | High (clear fields) → Low (unstructured, ambiguous) |
| **Decision Determinism** | How rule-bound vs. judgment-heavy is the decision? | High (deterministic rules) → Low (tacit judgment) |
| **Exception Rate** | What % of cases hit edge cases or exceptions? | Low (< 5% exceptions) → High (> 20% exceptions) |
| **Tool Coverage** | Can the agent access all systems needed to decide and act? | High (API access to all) → Low (manual workarounds needed) |
| **Risk/Reversibility** | If the agent gets it wrong, what's the impact and how hard is it to fix? | Low (easily reversed) → High (irreversible, high-stakes) |

---

## Scoring Rubric

### Input Structure
- **5 - Highly Structured:** Clear, validated fields; minimal ambiguity (e.g., hire record with all required fields populated)
- **4 - Mostly Structured:** Some ambiguity or conditional fields (e.g., hire record + optional manager notes)
- **3 - Mixed:** Combination of structured data and unstructured context (e.g., hiring paperwork + email thread)
- **2 - Mostly Unstructured:** Primarily narrative/context with some data points (e.g., customer complaint with scattered data)
- **1 - Highly Unstructured:** Narrative, context-dependent, no clear fields (e.g., open-ended complaint with embedded context)

### Decision Determinism
- **5 - Fully Deterministic:** Pure rule application; no reasoning required (e.g., "if hire_date < today, assign training module X")
- **4 - Mostly Deterministic:** Follows patterns, minor edge cases (e.g., "assign training based on role; if role not found, ask manager")
- **3 - Mixed:** Core path is rules, exceptions require judgment (e.g., "assign buddy based on team + availability + experience match")
- **2 - Mostly Judgment:** Some structure but significant judgment needed (e.g., "resolve escalation based on policy + stakeholder priority + precedent")
- **1 - Fully Judgment:** Requires tacit knowledge or ethics; not codifiable (e.g., "hire candidate" based on interview performance + cultural fit)

### Exception Rate
- **5 - Very Low (< 5%):** Almost all cases follow the standard path (e.g., 95% of hires are standard onboarding)
- **4 - Low (5-10%):** Most cases standard, a few exceptions (e.g., 90% standard, 10% contractor/visa issues)
- **3 - Moderate (10-20%):** Significant exception rate, but majority is standard (e.g., 80% standard, 20% role-specific variants)
- **2 - High (20-35%):** More exceptions than standard (e.g., 65% standard, 35% edge cases)
- **1 - Very High (> 35%):** Most cases hit exceptions; no clear "standard path" (e.g., 50%+ of cases are unique or contested)

### Tool Coverage
- **5 - Full Coverage:** Agent has API/system access to all required data sources and actions (e.g., Workday, ServiceNow, LMS all have APIs)
- **4 - Mostly Covered:** Agent can reach most systems; 1–2 manual workarounds (e.g., can auto-create tickets but must email manager manually)
- **3 - Partially Covered:** Agent can handle 50-70% of actions; significant manual steps remain (e.g., system A accessible, but system B requires manual query)
- **2 - Poorly Covered:** Agent can access data but can't act directly; limited to recommendations (e.g., can check Workday but can't write to ServiceNow)
- **1 - No Coverage:** No system access or all steps require manual work (e.g., must rely on email and manual spreadsheets)

### Risk/Reversibility
- **5 - Negligible Risk:** Mistake is easily spotted and reversed (e.g., wrong training module assigned; easily corrected with one email)
- **4 - Low Risk:** Mistake takes time to correct but is reversible (e.g., ticket routed to wrong team; re-route takes 10 minutes)
- **3 - Moderate Risk:** Correction requires escalation or has minor downstream impact (e.g., badge ordered to wrong location; costs time + money to re-route)
- **2 - High Risk:** Mistake causes significant disruption or cost (e.g., wrong hire marked as FTE instead of contractor; payroll impact)
- **1 - Critical Risk:** Mistake is irreversible or has severe consequences (e.g., hire marked as rejected when should be processed; legal implications)

---

## Delegation Archetypes

Based on your scores, assign each task cluster to one of five operating modes:

| Archetype | Characteristics | Score Drivers | Example |
|---|---|---|---|
| **Human Only** | No delegation; human does all work | Very high judgment + critical risk | Visa compliance review for expired work permit |
| **Human-led + Automation Support** | Tools accelerate execution; human controls | Deterministic rules + human prefers control | Auto-populate form fields; human reviews and submits |
| **Human-led + Agent Support** | Agent synthesizes & recommends; human decides | Mixed determinism + moderate complexity | Agent pulls salary benchmarks; HR approves offer |
| **Agent-led + Human Oversight** | Agent executes autonomously; human spot-checks | Mostly deterministic + low exception rate + reversible | Agent auto-assigns training modules; HR weekly audit |
| **Fully Agentic** | Agent acts without human in loop | Highly deterministic + low exception + low risk + full tool coverage | Auto-create Workday record from hire form |

---

## How to Assign Archetypes

**Scoring logic:**

1. **Calculate Suitability Score**: (Input Structure + Decision Determinism + Tool Coverage) / 3
   - Score ≥ 4.5: Likely candidate for autonomous or agent-led
   - Score 3–4.4: Requires human oversight or support
   - Score < 3: Likely human-only or human-led

2. **Adjust for Exception Rate & Risk**:
   - High exception rate (> 20%) → increase human involvement; agent must escalate
   - Critical risk (score 1–2) → require human oversight; no fully agentic
   - Low exception rate (< 5%) + low risk (score 4–5) → can reduce to agent-led

3. **Assign archetype**:
   - Suitability ≥ 4.5 + low exception + low risk → **Fully Agentic**
   - Suitability ≥ 4.5 + moderate exception → **Agent-led + Human Oversight**
   - Suitability 3–4.4 + mixed judgment → **Human-led + Agent Support**
   - Suitability < 3 → **Human-led + Automation Support** or **Human Only**

---

## Delegation Suitability Matrix — Example Format

```markdown
# Delegation Suitability Matrix: [Process Name]

| Task Cluster | Input Struct | Decision Determ | Exception Rate | Tool Coverage | Risk/Reverse | Suitability | Archetype | Rationale |
|---|---|---|---|---|---|---|---|---|
| Create Workday record | 5 | 5 | 5 | 5 | 5 | 5.0 | Fully Agentic | Deterministic, low exception, all data available |
| Assign training module | 4 | 4 | 4 | 5 | 4 | 4.3 | Agent-led + Oversight | Standard path 80%, but role exceptions exist; requires human spot-check |
| Match buddy | 3 | 3 | 3 | 3 | 3 | 3.0 | Human-led + Agent Support | Complex judgment; agent can surface candidates; human decides |
| Resolve visa issue | 2 | 1 | 2 | 2 | 1 | 1.7 | Human Only | Tacit legal judgment + critical risk; no automation |
```

---

## The Anti-Pattern: "Everything is Fully Agentic"

**Most common Week 2 mistake:** Assigning "Fully Agentic" to everything because the agent *can* technically do it.

**Guard against this:**
- Ask: "What makes success here?" If it's "human never sees it," risky.
- Ask: "What's the exception rate?" If > 15%, human must review or escalate.
- Ask: "If it fails, who notices?" If "the customer complains first," it's human-led oversight territory.
- Ask: "Is there policy discretion here?" If yes, agent can recommend but human should decide.

---

## Grounding in Evidence

For each archetype assignment, cite the lived-work evidence:

- "Assigned to 'Fully Agentic' because discovery revealed 98% of hires follow standard path (artefact X shows volume data)"
- "Assigned to 'Agent-led + Oversight' because exception rate is 12% (artefacts Y and Z show cases where discretion was needed)"
- "Assigned to 'Human Only' because discovery revealed Priya must make judgment calls on rehire status; no clear rule exists (email thread notes-1.5)"

---

## Output: Assumptions & Confidence

For each score, note:

| Task | Score | Confidence | Assumption/Gap |
|---|---|---|---|
| Training module assignment | 4 (Determinism) | Medium | Assuming role taxonomy is complete; haven't verified rare roles or exceptions |
| Buddy matching | 3 (Tool Coverage) | Low | Assuming availability data exists in HR system; need to verify system has this field |

---

## Refinement Prompts: Commands Used to Improve This Deliverable

The initial draft of DELIVERABLE-3 had a Full Scoring Summary table with 8 narrow columns using abbreviations (e.g., "Decision Determ.", "Risk/Reverse") that required the reader to cross-reference the scoring rubric to understand each score. The following prompt was used to make the table self-explanatory.

---

### Prompt 1: Make the scoring table readable without the rubric

```
Make sure all tables are formatted properly and are easy to read.
Make sure any diagrams are easily understood.
```

**What this caught:** The 8-column summary table used abbreviations that only made sense if the reader had the scoring rubric open alongside it. Scores alone (e.g., "4 / 3 / 5 / 4 / 3") conveyed no meaning without context.

---

### Prompt 2: Restructure the summary table to carry its own meaning

```
Rewrite the Full Scoring Summary table so a reader can understand each row
without looking at the scoring rubric. Replace the 8 score columns with 6 descriptive columns:

1. Decision Rule? — Yes/No with one-line explanation
2. Tools Available? — Yes/Partial/No with one-line explanation  
3. Exception Rate — Low/Medium/High with one-line explanation
4. Risk if Wrong — Low/Medium/High/Critical with one-line explanation
5. Suitability Score — numeric with brief rationale in the cell
6. Delegation Level — the archetype name

Build the rationale into each cell rather than requiring the reader to decode numbers.
Add a one-line explanatory note above the table explaining what it shows.
```

**What this fixed:** Replaced the abbreviation-heavy 8-column table with a 6-column table where each cell carries enough context to be understood standalone. The Delegation Level column is now the rightmost column so the eye naturally reads to the conclusion after scanning the evidence.

---

### Prompt 3: Anti-pattern check after restructure

```
Review the delegation archetypes assigned across all clusters.
Are any clusters assigned "Fully Agentic" that should have lower autonomy?
Specifically check:
- Clusters where Risk if Wrong is High or Critical
- Clusters where Exception Rate is Medium or High
- Clusters that involve irreversible employment decisions

If you find any over-automation, explain why the boundary should be lower
and revise the archetype accordingly.
```

**What this reinforced:** Hold decisions (Cluster 8) and hire-type classification (Cluster 2) were confirmed as correctly scored low — not by accident but as deliberate design choices grounded in specific risk criteria.

---

## Next Step

Once delegation archetypes are assigned, move to **Phase 4: Volume × Value Analysis**.
