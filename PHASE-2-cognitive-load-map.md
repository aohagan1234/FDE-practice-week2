# Phase 2: Cognitive Load Map — Decompose Into Workable Units

**Goal:** Break down work streams into Jobs to be Done (JtDs), cognitive zones, and breakpoints.

**Input:** Discovery questions answered + lived-work insights + artefacts (emails, system screenshots, case notes).

---

## What is a Cognitive Load Map?

A decomposition of a work stream into:

1. **Jobs to be Done (JtDs)** — cognitive contracts between actor and outcome
   - Not just tasks ("send email") but complete contracts ("resolve customer complaint")
   - Include what must be *decided* vs. what must be *executed*
   
2. **Micro-tasks** — atomic steps within each JtD
   - Input required (data, context, prior decisions)
   - Decision or execution?
   - Output and downstream dependencies
   
3. **Cognitive Zones** — clusters of similar cognitive activity
   - Intent recognition / intake
   - Diagnosis / analysis
   - Decision / judgment
   - Execution / action
   - Communication / documentation
   
4. **Breakpoints** — handoff points where control must pass
   - Human → Agent (at what signal?)
   - Agent → System (at what threshold?)
   - System → Human (when? why?)
   - These are where agents create value *or* risk

---

## How to Map: Step-by-Step

### Step 1: Identify the JtDs in your work stream

List 3–4 major Jobs to be Done (not processes, but cognitive contracts):

**Example from HR Onboarding:**
- "Ensure new hire has system access on Day 1"
- "Verify compliance training is correctly assigned for role/country"
- "Match new hire with mentor and establish relationship"
- "Resolve edge-case barriers to employment start"

For each, write a 1-sentence purpose:
- What outcome is the actor trying to achieve?
- Who is the primary actor (human, agent, system)?
- What makes success?

---

### Step 2: For each JtD, list the micro-tasks

Break the JtD into steps. For each step, record:

| Micro-task | Input | Decision or Execution? | Output | Data Source |
|---|---|---|---|---|
| Check if new hire exists in Workday | Hire name, start date | Execution | Record ID or "not found" | Workday API |
| Determine correct IT hardware spec | Hire role, org, prior system tenure | Decision (judgment on role/precedent) | Hardware SKU + shipping priority | HR record + IT precedent table + hiring manager input |
| Create ServiceNow ticket | Hardware SKU, shipping priority, location | Execution | Ticket ID | ServiceNow API |
| ... | ... | ... | ... | ... |

**Listen for:**
- Where does the human *think* vs. *execute*?
- What data sources must be consulted?
- Where do multiple sources conflict?
- What would an agent struggle with?

---

### Step 3: Map Cognitive Zones

Group micro-tasks into zones of similar cognitive character:

**Example zones for "resolve onboarding blocker":**

| Zone | Micro-tasks | Cognitive Character | Data needed | Error tolerance |
|---|---|---|---|---|
| **Intake & Triage** | Receive escalation, classify barrier type | Decision: pattern match to known categories | Current status, prior escalations | Low (wrong triage cascades) |
| **Diagnosis** | Consult systems, trace root cause | Decision: rule-based with exceptions | Workday, ServiceNow, compliance records | Medium (can be corrected) |
| **Resolution** | Execute fix or route to specialist | Execution: apply documented remedy | Permissions, system access | Low (irreversibility) |
| **Documentation** | Log resolution, communicate outcome | Execution: record state | Communication templates | Low (audit trail) |

---

### Step 4: Identify Breakpoints

Mark points where control must hand off:

```
Human → Agent:
  - Breakpoint: New hire record created in Workday
  - Signal: Workday event trigger (hire status = "awaiting equipment")
  - Why: All downstream tasks are rule-bound

Agent → System:
  - Breakpoint: ServiceNow ticket creation
  - Signal: Agent has validated specs and routed to IT queue
  - Why: System auto-execute from this point

System → Human:
  - Breakpoint: Exception (hardware spec not in price catalog)
  - Signal: ServiceNow auto-assign to "procurement exception" queue
  - Why: Decision authority stays with procurement

Human → Human:
  - Breakpoint: Edge-case visa verification
  - Signal: Flag in Workday, assign to compliance team
  - Why: Requires tacit legal judgment
```

---

### Step 5: Ground in Artefacts

For each zone or breakpoint, reference the lived-work evidence:

- "Email thread atx-1.1 shows that laptop spec escalations happen ~5% of onboarding cases"
- "System extract sys-2.3 shows ServiceNow has no routing rule for consulting division laptops, causing manual handoff"
- "Sticky note notes-1.4 shows Priya's workaround: manual SQL query to cross-check hardware pricing"

**If you can't ground it in evidence**, mark it as an assumption with confidence level.

---

## Output Format

Create a markdown table for each work stream:

```markdown
# Cognitive Load Map: [Work Stream Name]

## Jobs to be Done
1. [JtD name] — [1-sentence purpose]
2. [JtD name] — [1-sentence purpose]

## Micro-tasks & Zones
[Table with steps, inputs, decisions/executions, outputs, data sources]

## Breakpoints & Control Handoffs
[Annotated flowchart or list of breakpoints with signals and rationale]

## Grounding in Evidence
- Artefact X supports assumption Y with confidence [High/Medium/Low]
- Artefact Z is silent on [gap], assumed: [statement]
```

---

## Common Pitfalls to Avoid

- **Skipping the lived work:** Don't map the SOP; map what actually happens
- **Conflating tasks with decisions:** "Create a ticket" is execution; "which queue does it go to?" is decision
- **Assuming all breakpoints are human-agent:** Some are agent-system, some are system-human; mark each
- **Missing exception rates:** If you don't know what % of cases hit exceptions, you're guessing on delegation
- **Shallow zones:** "Communication" isn't a zone; "Draft email notification to manager + CC hiring director + include start date in body + link to welcome pack" is more useful

---

## Refinement Prompts: Commands Used to Improve This Deliverable

The initial draft of DELIVERABLE-2 had tables that were technically complete but hard to scan — the "Decision or Execution?" column had verbose multi-line entries that broke table alignment. The following prompts were used to standardize and improve readability.

---

### Prompt 1: Fix table column width and verbosity

```
Make sure all tables are formatted properly and are easy to read.
Make sure any diagrams are easily understood.
```

**What this caught:** Long values in the "Decision or Execution?" column (e.g., "Decision (Judgment on seniority norms + team dynamics)") were breaking table alignment across 11 micro-task tables. All values needed to be shortened to a consistent format.

---

### Prompt 2: Standardize the type column to short codes

```
The "Decision or Execution?" column header and values are too verbose for a table.

Replace the column header with "Type" across all micro-task tables.

Standardize all values to short codes:
- D — [brief reason]  for any step requiring judgment or discretion
- E — [brief reason]  for any step that is rule-based or agent-safe

Add a key in the intro text: D = Decision/judgment required, E = Execution/agent-safe.

Apply replace_all so the change is consistent across all tables.
```

**What this fixed:** Replaced approximately 23 verbose cell values with consistent short codes (e.g., "**D** — judgment (team dynamics)", "**E** — rule-based", "**E** — query"). The column is now scannable; the reader can visually separate agent-safe steps from judgment steps without reading each cell in full.

---

### Prompt 3: Check for inconsistent formatting after bulk replace

```
After applying the replace_all, check for any cells where:
- The original wording had slight variations (e.g., "Execution (deterministic)" vs "Execution (query)")
- The value was a standalone word ("Execution") with no qualifier
- The format differs from the D/E shortcode pattern

Fix each individually so the column is consistent across all 11 tables.
```

---

## Next Step

Once mapped, move to **Phase 3: Delegation Suitability Matrix**.
