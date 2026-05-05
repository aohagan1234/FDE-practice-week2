# Scenario 2 Gaps Analysis — Exact Locations & Fixes

This document shows exactly where gaps exist in Week2_Docs, what's currently there, and what should be added for Scenario 2.

---

## Gap 1: Rule-Based vs Judgment-Based Work

**File:** `PHASE-3-delegation-suitability.md`  
**Section:** "Decision Determinism" rubric (scoring scale 5-1)  
**Lines:** 25-38

### CURRENT TEXT:
```markdown
### Decision Determinism
- **5 - Fully Deterministic:** Pure rule application; no reasoning required 
  (e.g., "if hire_date < today, assign training module X")
- **4 - Mostly Deterministic:** Follows patterns, minor edge cases 
  (e.g., "assign training based on role; if role not found, ask manager")
- **3 - Mixed:** Core path is rules, exceptions require judgment 
  (e.g., "assign buddy based on team + availability + experience match")
- **2 - Mostly Judgment:** Some structure but significant judgment needed 
  (e.g., "resolve escalation based on policy + stakeholder priority + precedent")
- **1 - Fully Judgment:** Requires tacit knowledge or ethics; not codifiable 
  (e.g., "hire candidate" based on interview performance + cultural fit)
```

### WHAT'S MISSING:
The rubric explains the scale, but **does NOT explain** how to handle work that has a hard boundary (e.g., "no decision leaves this function without human approval, ever").

Amelia's rule in Scenario 2: **"No counteroffer leaves legal's queue without named lawyer's sign-off"** is not a score on this scale. It's a *veto*. The agent can score 4.5 on all other dimensions, but this rule means certain work cannot be fully agentic, period.

### WHAT SHOULD BE ADDED:
Add a new subsection after "Scoring Rubric" called **"Handling Hard Boundaries"**:

```markdown
## Special Case: Hard Boundaries (Non-Negotiable Rules)

Some stakeholders have rules that supersede the scoring rubric. These appear as statements like:
- "No [decision] leaves my desk without my sign-off"
- "We will never delegate [task] to a system"
- "[Task] must always have human approval, no exceptions"

**These are not negotiable based on scores.** They are organizational constraints.

### How to handle in your scoring:

1. **Identify hard boundaries:** Look in stakeholder quotes and escalation rules
2. **Record as assumption:** "Hard boundary exists: [boundary statement]" — Confidence: HIGH (stated by stakeholder)
3. **Do not override with scoring:** Even if the work scores 5.0 on all dimensions, if it has a hard boundary, assign it to "Agent-Led + Human Oversight" or "Human Only" — never "Fully Agentic"
4. **Discover the reason:** In Discovery Questions, ask: "If you had to relax this rule, what's the failure mode you're most afraid of?" (See Gap 5 below)

### Example: Scenario 2 — Counteroffer Sign-Off

**Hard boundary stated:** "No counteroffer leaves legal's queue without named lawyer's sign-off"

**Scoring logic says:** Clause classification could score 4.5+; should be agent-led

**But:** Hard boundary says counteroffer negotiation position is never delegated

**Design result:** 
- Work Stream 1 (classify clauses) → Agent-Led + Oversight (agent classifies, lawyer approves)
- Work Stream 4 (counteroffer strategy) → Human-Only (lawyer decides, agent cannot propose)

**Note in your Delegation Matrix:** Add a column "Hard Boundary?" with Yes/No. Any "Yes" means the archetype cannot be higher than "Agent-Led + Human Oversight."
```

---

## Gap 2: Vendor-Controlled Systems & Batch-Only Interfaces

**File:** `PHASE-7-system-data-inventory.md`  
**Section:** "System Inventory: Systems The Agent Touches" (Template section)  
**Lines:** 10-50

### CURRENT TEXT:
```markdown
For each system, document:

### Template

| System | API Type | Endpoints Used | Auth | Rate Limit | SLA | Fallback |
|---|---|---|---|---|---|---|
| [Name] | [REST/GraphQL/Direct DB/SDK] | [List endpoints] | [OAuth/API Key/Service Account] | [Calls/sec or calls/day] | [99.9% / 99% / Custom] | [If system down, what does agent do?] |

### Example: Workday

| System | API Type | Endpoints Used | Auth | Rate Limit | SLA | Fallback |
|---|---|---|---|---|---|---|
| **Workday** | REST API | `/hrh-get-hire`, `/hrh-list-hires`, `/emp-search`, ... | OAuth 2.0 (client credentials) | 100 calls/sec | 99.9% (contractual) | If Workday down: agent stops; queue escalations; notify Priya manually by email |
```

### WHAT'S MISSING:
The template assumes all systems have APIs that the agent can call. But in Scenario 2:
- **VendorCo won't accept SharePoint links** (they only take email attachments)
- **Saba LMS has no API** (data arrives via weekly batch file)
- **Compliance playbook is a PDF on SharePoint** (human has to read it; agent can't parse it reliably)

The current template has no row for "how do we handle data/interactions where the vendor controls the format?"

### WHAT SHOULD BE ADDED:
Add a new section after "System Inventory" called **"Vendor-Controlled & Batch-Only Interfaces"**:

```markdown
## Vendor-Controlled & Batch-Only Interfaces

### Red Flags in Artefacts (Scenario 2 Examples)

Look for these patterns in stakeholder communications:
- "Our system can't accept [format]" → vendor controls the format
- "They only take email attachments" → synchronous email, not system integration
- "We batch-import every [day/week]" → batch window is a design constraint
- "We export to Excel and manually upload" → workaround indicates system gap
- "That rule is documented in PDF, we read it manually" → source-of-truth is not machine-readable

### How to Document Vendor-Controlled Systems

Add rows to your System Inventory table for each vendor-controlled interface:

| System | Type | Data Format | Frequency | Auth | SLA | Fallback |
|---|---|---|---|---|---|---|
| VendorCo Procurement | Email attachment | Word .docx (redlines) | Per negotiation (async) | N/A (human-driven) | None (customer-controlled) | If vendor doesn't respond, escalate to sales |
| Saba LMS Batch | SFTP batch file | CSV export | Weekly (Sunday 2300 UTC) | SFTP key + IP whitelist | Not contractual | Batch delayed: agent waits; escalate to IT if > 24h late |
| Compliance Playbook | Manual document | PDF on SharePoint | Updated ad-hoc (stale) | Read access | None | Agent flags "playbook version unknown"; escalate to Legal |

### Design Implications

When data arrives via vendor-controlled or batch interface:
1. **No real-time triggers:** Agent cannot react immediately; must wait for batch or polling
2. **Audit trail is manual:** Email/attachment exchanges must be logged separately
3. **Versioning is risky:** If vendor sends wrong format or updates without notice, agent breaks
4. **Fallback requires human:** Agent cannot re-request; escalation goes to human to contact vendor

### 3-State Model for Batch Data (from Scenario 1 / Saba LMS)

```
STATE 1: PENDING-BATCH
  Agent waiting for batch file
  Detection method: time-based (if no batch by trigger time, escalate)
  Duration: up to 24 hours (configurable)

STATE 2: BATCH-ARRIVED
  Batch file received; agent processes
  Detection method: file exists in SFTP directory
  Duration: few minutes (agent parse & load)

STATE 3: PROCESSED
  Agent completes activity; waits for next batch window
  Detection method: agent logs completion; clears state
  Duration: until next batch arrives
```

If batch is > 24h late: escalate to IT with message "Saba LMS batch missing since [time]; last batch was [date]"
```

---

## Gap 3: What Happens to Tom (Labor Arbitrage & Role Redesign)

**File:** `PHASE-1-discovery-questioning.md`  
**Section:** "Level 3: Probe Funnel" (Agentic Patterns section)  
**Lines:** 65-85

### CURRENT TEXT:
```markdown
### Level 3: Probe Funnel — Detect Agentic Patterns (15-20 min)

Probe for where decisions might be structured and delegatable:

- "When you make that decision [the judgment you identified], is there a pattern? If X is true and Y is true, you do A; if Z is true, you do B?"
- "How often are you actually thinking vs. executing a pattern you've already decided?"
- "Could you articulate the criteria you use to decide this right now?"
- "Are there cases where you'd be comfortable with an AI agent making this decision if you could review it first?"
- "If the agent got it wrong, what's the consequence? How would you detect it?"
- "Does this need to happen in real-time, or could it happen asynchronously (agent queues it, you review later)?"
- "What percentage of cases fit the standard pattern vs. exceptions?"
```

### WHAT'S MISSING:
These questions focus on **what the agent does**, but not on **what happens to Tom (the paralegal)** if the agent takes his work.

In Scenario 2, Tom does ~45 min/contract on routine clause classification. If an agent handles that, Tom's time drops by 40%. The agent design must address:
- Does Tom get reassigned or reduced hours?
- Who will handle Tom's other work?
- Will Tom feel threatened and resist the agent?
- Does Amelia have budget to keep Tom if his hours drop?

### WHAT SHOULD BE ADDED:
Add a new subsection in Level 3 called **"Labor Arbitrage & Role Impact"**:

```markdown
### Sub-Level 3b: Labor Arbitrage & Organizational Design (5 min)

If the work you're automating is currently done by a junior person (paralegal, coordinator, analyst), ask:

**About the role:**
- "If we automate [Tom's task], what would Tom do with freed-up time?"
- "Would that new work be valuable to you?"
- "If not, is this a headcount-reduction opportunity or a redeployment?"
- "What would Tom think about this change? Has he expressed interest in other work?"

**About economics:**
- "[Tom] currently costs [£X/year]. If agent handles 50% of his work, do you reduce his hours or keep him?"
- "What's the break-even timeline for the agent investment vs. Tom's salary?"

**About implementation:**
- "If we build an agent and it works, do you expect this role to shrink or disappear?"
- "How would you communicate that to Tom?"

**Listen for:**
- Hidden organizational constraints (budget freeze, union rules, team morale)
- Role redesign plans (Tom could become "escalation specialist" or "quality auditor")
- Risk: agent built, but Tom feels threatened and doesn't help refine it

**In your Assumptions log, record:**
"Assumption: Tom's role will shift to [new responsibility] if agent handles routine classification. Confidence: MEDIUM. Validation: confirm with Amelia in mid-week checkpoint."
```

---

## Gap 4: Audit Trail & Decision Evidence

**File:** `PHASE-5-agent-purpose-doc.md`  
**Section:** "Failure Modes & Recovery" (lines 170-230)  
**Lines:** Approximately 170-230

### CURRENT TEXT:
```markdown
| Failure Mode | Detection | Impact | Recovery |
|---|---|---|---|
| **Agent surfaces unavailable buddy** | Candidate on leave; Priya notices in email | Low: 1 manual filter, ~2 min | Manual check; agent learns to improve leave-calendar sync |
| **Agent escalates unnecessarily** | Flags low-priority cases as ties or exceptions | Medium: creates false work for Priya | Tune scoring thresholds; reduce False Positive escalation rate |
| **Agent assigns same buddy twice** | Candidate receives 2 buddy assignments on same day | High: conflict; manager confusion | Implement pessimistic locking in Workday write; verify candidate's current count before write |
| **Scoring formula produces unintuitive ranking** | Priya rejects top 3 and picks 4th candidate | Medium: undermines trust | Monthly review of rejected candidates; refine scoring weights |
```

### WHAT'S MISSING:
There is **no failure mode for "audit trail completeness"** — a critical issue in legal workflows where:
- Agent must show evidence for every decision (for compliance and reversibility)
- If the agent decides "this clause is standard" but doesn't show *why*, a lawyer can't defend the decision later
- If a customer later disputes terms, you need proof that a lawyer actually reviewed clause X

This is especially important in Scenario 2 because legal workflows are audit-sensitive.

### WHAT SHOULD BE ADDED:
Add a new failure mode and a new design section to "System & Data Requirements":

```markdown
## 6. Failure Modes & Recovery (REVISED)

Add a new row to the failure mode table:

| Failure Mode | Detection | Impact | Recovery |
|---|---|---|---|
| **Agent decision lacks audit evidence** | Lawyer is asked "why did we classify clause X as standard?" and agent output has no justification | High: compliance risk; cannot defend decision if challenged | Agent must always output: (a) rule matched, (b) confidence score, (c) pointer to playbook section, (d) override flag if human changed it |

## 8b. Audit Trail Design (NEW SECTION)

For workflows with regulatory, compliance, or high-stakes decision reversal risk:

**Audit trail must include:**
1. **What the agent decided:** "Clause 7.3 (Limitation of Liability) → FLAG: below playbook minimum"
2. **Why it decided that:** "Playbook rule: caps must be ≥ £250k; this cap is £50k"
3. **Confidence score:** "Match confidence: 95% (exact field match)"
4. **Data sources consulted:** "Matched against: playbook v4.2, section 7.3.1"
5. **Human action:** If human approved: "Approved 14.05 by [Lawyer Name]"; if overridden: "Overridden 14.05 by [Lawyer Name], reason: [comment]"
6. **Timestamp:** Complete audit chain with dates/times

**Implementation approach:**
- Agent output format includes all 6 elements, not just the decision
- Audit log is immutable (append-only; no deletion)
- Human override is a *new decision* logged separately, not a correction to the original decision
- Export audit trail monthly for compliance review

**Tom's margin notes (Artefact 2.1) should be mirrored in agent output:** If Tom writes "FLAG — but negotiable, will redline to playbook position," the agent should output something equivalent: "Flagged: Non-standard but within negotiation range. Recommended action: redline to [playbook position]."
```

---

## Gap 5: Discovering the "Why" Behind Hard Boundaries

**File:** `PHASE-1-discovery-questioning.md`  
**Section:** "Level 3: Probe Funnel" (specifically the "Listen for" guidance)  
**Lines:** 77-85

### CURRENT TEXT:
```markdown
**Listen for:**
- Codifiability (can the rule be articulated?)
- Exception rate (if >20%, agent must handle or escalate)
- Risk and reversibility (is a mistake high-stakes or easily corrected?)
- Latency requirements (immediate vs asynchronous?)
- Human trust (openness to agent involvement?)
```

### WHAT'S MISSING:
When Amelia says "no counteroffer leaves my queue without sign-off," the current guidance tells you to listen for "Human trust" — but it doesn't tell you to **ask why**.

The *reason* behind the hard boundary determines the agent design:
- If it's regulatory risk → focus on audit trail
- If it's relationship risk → focus on accuracy/precision
- If it's prior liability → focus on escalation triggers
- If it's career risk → focus on transparency

### WHAT SHOULD BE ADDED:
Add a new question to Level 3, right after the existing list:

```markdown
### Level 3: Probe Funnel — Detect Agentic Patterns (15-20 min)

[EXISTING QUESTIONS...]

**NEW QUESTION — Surfacing Hidden Constraints Behind Hard Boundaries:**

If you hear a hard boundary like "no [decision] without human approval," ask:

- "You mentioned that [hard boundary]. If you had to relax it, what's the one failure you'd be most afraid of?"
  - This surfaces the hidden risk: liability, compliance, relationship, or career
  
- "Has there been a specific incident that made you set this rule?"
  - This grounds the boundary in a real event, not just preference

- "What would need to be true for you to trust an agent to make this decision without your review?"
  - This reveals the trust condition and quality bar

**Record the answer as an assumption:**
- "Hard boundary: No counteroffer without GC sign-off"
- "Reason (from stakeholder):" [insert answer]
- "Confidence: HIGH (stated by stakeholder); actual risk tolerance: MEDIUM (contingent on audit trail)"

**Use this in your Volume × Value Analysis:**
- If the boundary is about liability (£X cost if wrong), use that in ROI calculation
- If it's about compliance (audit penalty), use that in ROI
- If it's about trust, flag as a design-time investment (must build audit trail to earn trust)

**Use this in your Discovery Questions deliverable:**
Frame one of your 6 design-changing questions around the hidden risk:
- E.g., "If a customer later disputed clauses in a counteroffer, what specific evidence would you need to prove we reviewed them?" (This reveals what the audit trail must contain)
```

---

## Gap 6: Data Staleness & Source-of-Truth Quality

**File:** `PHASE-7-system-data-inventory.md`  
**Section:** "Data Dictionary: Entities & Fields" (Template section)  
**Lines:** 100-130

### CURRENT TEXT:
```markdown
| Field | Type | Source | Required? | Quality Notes | Agent Use |
|---|---|---|---|---|---|
| `hire_id` | UUID | Workday auto-generate | Yes (PK) | Unique; immutable | Read: lookup hire |
| `hire_name` | String | Hiring manager input | Yes | 98% complete; ~2% missing names | Read: display to Priya |
```

### WHAT'S MISSING:
The quality notes describe completeness and accuracy *now*, but do not flag:
- **Data that is known to be stale** (e.g., "compliance playbook last updated October 2023; new rules pending implementation")
- **Data that is under active maintenance** (e.g., "we're fixing the org chart this quarter")
- **Data where the human is uncertain** (e.g., Tom's note: "honestly not sure if this needs escalation")

In Scenario 2, Artefact 2.3 shows Amelia's sticky note: "DPDI Act updates landed Q1 — need to add new sections... talked about this in March, never got round to it."

This is critical because:
- If the agent's source-of-truth is stale, the agent will be stale
- You need to know this *before* building the agent
- It changes the agent design (e.g., "agent flags playbook version unknown; escalates to Legal")

### WHAT SHOULD BE ADDED:
Revise the Data Dictionary template to include a "Data Debt" column:

```markdown
## Data Dictionary: Entities & Fields (REVISED)

| Field | Type | Source | Required? | Quality Notes | Data Debt? | Agent Use |
|---|---|---|---|---|---|---|
| `hire_id` | UUID | Workday auto-generate | Yes (PK) | Unique; immutable | No | Read: lookup hire |
| `hire_name` | String | Hiring manager input | Yes | 98% complete; ~2% missing names | No | Read: display to Priya |
| `playbook_compliance_clauses` | Object | PDF on SharePoint | Yes (config) | Last updated Oct 2023; DPDI Act updates pending | **YES — HIGH** | Read: match clauses; agent flags if version unknown |
| `org_chart` | JSON | Manual sync from HR system | Yes (config) | Updated ad-hoc; often stale 30–60 days | **YES — MEDIUM** | Read: search candidates; agent warns if > 90 days old |

### New "Data Debt" Column Guidance

**Data Debt?** = Is this data known to be incomplete, outdated, or under maintenance?

- **No** = Current and maintained
- **YES — LOW** = Slightly stale but acceptable for agent use (e.g., org chart 1 week old)
- **YES — MEDIUM** = Noticeable staleness; agent should flag if possible (e.g., org chart 60+ days old; agent uses but flags "stale")
- **YES — HIGH** = Should NOT be used for agent decisions without human override (e.g., playbook known to have outdated rules; agent must escalate if matching against it)

### Data Debt Examples (Scenario 2)

| Data | Current State | Data Debt | Mitigation |
|---|---|---|---|
| Compliance Playbook | Last updated Oct 2023; DPDI Act updates "discussed in March, never implemented" | HIGH | Agent cannot classify DPA clauses confidently; escalate all DPA clauses to lawyer until playbook is v4.3+ |
| Contract precedents / past counteroffers | Stored in email threads and Word docs | HIGH | Agent cannot learn from precedent; only follows explicit playbook rules |
| Vendor negotiation patterns | Tribal knowledge (Tom's mental model) | HIGH | Agent doesn't know which vendors always negotiate on liability caps; no historical database |

### Action: Before Building the Agent

1. **Identify data debt:** In your System/Data Inventory, mark any data as "HIGH" if it's known to be stale or under maintenance
2. **Ask stakeholder:** "Is [data] on your roadmap to refresh before agent launch?"
3. **Record as assumption:** "Data [X] is known to be stale. Agent will not match against [X] until it's updated. Confidence: HIGH (acknowledged by stakeholder, but schedule uncertain)."
4. **Decide:** Should agent launch wait for data refresh, or should agent handle stale data with escalations?

Example for Scenario 2:
- Playbook refresh is pending but date is uncertain
- Decide: "Agent will not classify against DPA section until playbook v4.3 is live; until then, all DPA clauses escalate to GC"
```

---

## Summary: What to Do Now

**For someone building a Scenario 2 assessment this week:**

| Gap # | File | Section | Action |
|---|---|---|---|
| 1 | PHASE-3-delegation-suitability.md | "Decision Determinism" | Add subsection "Handling Hard Boundaries" — explains that stakeholder veto rules override scoring |
| 2 | PHASE-7-system-data-inventory.md | "System Inventory" | Add section "Vendor-Controlled & Batch-Only Interfaces" — template for email/batch/external data |
| 3 | PHASE-1-discovery-questioning.md | "Level 3 Probe Funnel" | Add subsection "Labor Arbitrage & Role Impact" — asks what happens to Tom if work is automated |
| 4 | PHASE-5-agent-purpose-doc.md | "Failure Modes" & "System/Data" | Add failure mode row for "audit trail completeness"; add section "Audit Trail Design" |
| 5 | PHASE-1-discovery-questioning.md | "Level 3 Probe Funnel" | Add new question "If you had to relax the hard boundary, what failure are you most afraid of?" |
| 6 | PHASE-7-system-data-inventory.md | "Data Dictionary" | Add "Data Debt?" column; show how to flag stale/under-maintenance data |

---

