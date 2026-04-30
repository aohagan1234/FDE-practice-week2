# Phase 6: Build Loop — Close Gaps in Your Design

**Goal:** Use AI (Claude Code) to stress-test your Agent Purpose Document and identify gaps before Gate 2.

**Input:** Agent Purpose Document from Phase 5.

---

## The Build Loop Pattern

The build loop is designed to expose the "everything is fully agentic" anti-pattern and delegation boundary gaps:

1. **Hand your Agent Purpose Document to Claude Code**
2. **Ask Claude three structured questions**
3. **Diagnose the gaps Claude reveals**
4. **Revise your document**
5. **Repeat until Claude can build it without major questions**

---

## Step 1: The Build Prompt

Send your Agent Purpose Document to Claude Code with this prompt:

```
I am developing an agent for [process name]. Read my Agent Purpose Document carefully, then answer:

1. **What can you build confidently from this document?**
   - List the components you understand well enough to code without asking questions.
   - Include specific sections (e.g., "Activity Catalog step 1-5," "Failure mode detection for X").

2. **What do you need me to clarify before building the rest?**
   - For each gap, explain why it's ambiguous.
   - Suggest what information would resolve it.
   - If it's a delegation boundary, ask explicitly: "Should the agent decide this, or should it escalate to the human?"

3. **Build the parts you're confident about.**
   - Show me code/pseudocode for the components you can implement.
   - Leave commented TODOs for the gaps you identified in question 2.

Focus on:
- Are there delegation decisions that sound like they should be agent-decided but are actually human decisions (or vice versa)?
- Are the escalation triggers clear enough to code?
- Can you access all the data sources and perform all the actions listed?
- Are the failure modes implementable, or do they require capabilities I haven't specified?
```

---

## Step 2: Analyze Claude's Response

Claude will typically identify three types of gaps:

### Gap Type 1: Ambiguous Delegation Boundaries

**Claude says:** "The autonomy matrix says the agent 'ranks candidates by scoring formula,' but doesn't specify what happens if the formula produces a tie or an unintuitive result. Should the agent break ties autonomously or escalate?"

**Diagnosis:** You haven't specified the decision rule precisely enough. The boundary between "agent decides" and "human decides" is unclear.

**Fix:** Revise your autonomy matrix. Example:
- **Before:** "Agent ranks candidates by formula"
- **After:** "Agent ranks candidates by formula (team_diversity × 0.3 + availability × 0.2 + experience × 0.5). If top 2 candidates score within 5%, escalate both with reasoning to Priya."

---

### Gap Type 2: Missing Data or System Access

**Claude says:** "You list 'leave calendar' as required input, but I don't see an API endpoint in your system requirements. How does the agent access it? Is it a query into Workday, an external calendar system, or a manual data file?"

**Diagnosis:** Your system/data requirements section is incomplete. The agent can't act without knowing where to get the data.

**Fix:** Add specifics:
- **System:** Workday REST API endpoint: `/employees/{id}/leave-calendar`
- **Freshness:** Daily refresh at 0200 UTC
- **Quality:** ~10% incomplete (employees haven't submitted PTO yet)
- **Fallback:** If leave data missing, treat as "available" and let Priya verify

---

### Gap Type 3: Failure Mode That Requires Human Intervention

**Claude says:** "If the agent can't find < 3 qualified candidates, your document says to 'escalate.' But what does the human see? Do you want me to flag it in a dashboard, send an email, create a ticket? And what should the human do if they receive this escalation—search manually, lower the criteria, or wait?"

**Diagnosis:** Your escalation process is vague. You've defined the condition but not the workflow.

**Fix:** Add specifics:
- **Detection:** Agent finds < 3 candidates
- **Escalation action:** Send email to Priya with subject "Buddy matching escalation for [hire name]" including available candidates (even if <3) + explanation of why criteria weren't met
- **Human action:** Priya reviews available candidates or reaches out to hiring manager to relax criteria (e.g., "Can we accept someone with 3 months tenure instead of 6?")
- **Timeout:** If Priya doesn't respond within 24h, resend reminder email

---

## Step 3: Categorize Gaps by Type

Use this taxonomy to classify each gap Claude raises:

| Gap Category | Definition | Fix Approach |
|---|---|---|
| **Delegation Boundary** | Unclear whether agent or human should decide; Claude defaulted to cheapest implementation | Revise autonomy matrix; add explicit decision rule + escalation threshold |
| **Data Missing** | System/data requirements incomplete; agent can't access input or act on output | Verify API exists; add endpoint, schema, freshness, quality notes |
| **Workflow Ambiguous** | Escalation or feedback loop not specified; unclear what human sees or does | Specify: detection → escalation action → human response → timeout/fallback |
| **Failure Mode Incomplete** | A failure scenario exists but detection or recovery not coded-able | Add detection method (e.g., "query Workday after write to verify") + recovery action |
| **Assumption Not Tested** | Document assumes something (e.g., "all buddies have < 3 assignments") that Claude can't verify; affects correctness | Mark as assumption; plan to verify during pilot; adjust design if wrong |

---

## Step 4: Revise Your Agent Purpose Document

For each gap Claude found, update your document:

**Example revision:**

**Original Autonomy Matrix entry:**
```
| Escalation Triggers | (Vague) Unclear circumstances |
```

**After Claude feedback:**
```
| Escalation Triggers | 
| - < 3 qualified candidates found (insufficient choice) | 
| - Top 2 candidates tied on score (diff < 5%) | 
| - Candidate's current buddy count ≥ 3 | 
| - New hire marked "VIP" | 
| - Leave calendar incomplete for > 30% of candidates |
```

**Original System Requirements:**
```
| Leave calendar | Workday | Daily refresh | Managed by employees |
```

**After Claude feedback:**
```
| Leave calendar | Workday API `/employees/{id}/leave-calendar` | Daily 0200 UTC | Managed by employees; ~10% incomplete (PTO not yet submitted). Fallback: if missing, treat as available; let Priya verify in escalation step. |
```

---

## Step 5: Re-Run the Build Loop (If Major Gaps Found)

If Claude identified > 3 delegation boundary gaps or critical missing data:

1. **Update your document** with the revisions from Step 4
2. **Send the revised document back to Claude** with the prompt: "I've revised based on your feedback. Can you now build more of this? What new questions do you have?"
3. **Repeat until** Claude says: "I can now build all of this. My remaining comments are implementation details (e.g., error handling, performance optimization), not design gaps."

---

## Step 6: Diagnose Specific Patterns

### Anti-Pattern 1: "Everything is Fully Agentic"

If Claude says: "Your document doesn't specify when the human reviews the agent's work," you've built a fully-agentic design where Claude will implement autonomous execution with no human in the loop.

**Diagnosis:** You skipped human oversight in your autonomy matrix.

**Fix:** Add human touchpoints:
- Does Priya see the agent's decision before it executes? (Agent-led + Human Oversight)
- Or does the agent execute, and Priya audits weekly? (Periodic review)
- Or does the agent execute, and humans only intervene if an alert fires? (Exception-driven oversight)

### Anti-Pattern 2: "Fully Human" (Agent Underutilization)

If Claude says: "According to your autonomy matrix, every decision escalates to the human, so the agent only queries data and sends emails," you've built an agent that's really just a UI wrapper.

**Diagnosis:** You over-estimated risk or under-estimated the agent's capability.

**Fix:** Review your Volume × Value analysis and Delegation Suitability scores. If you scored high on determinism and low on exception rate, the agent should decide more autonomously. Adjust the autonomy matrix to give the agent decision authority on high-confidence cases.

### Anti-Pattern 3: "Ambiguous Delegation" (Agent Doesn't Know When to Escalate)

If Claude says: "The document doesn't specify what makes a buddy 'qualified,' only that the agent should rank them," you've left a critical decision undefined.

**Diagnosis:** Your autonomy matrix conflates "scoring" with "filtering." The agent can score, but it can't decide who qualifies without clear rules.

**Fix:** Separate qualification from ranking:
- **Qualification (rules):** Tenure > 6 months, availability = true, buddy count < 3 (agent decides deterministically)
- **Ranking (scoring):** Among qualified candidates, score by formula (agent decides)
- **Final selection (human):** Among top 3, Priya chooses (human decides)

---

## Step 7: Track Assumption Confidence

As Claude asks questions, note which of your assumptions are shaky:

| Assumption | Claude Question | Confidence | Plan to Verify |
|---|---|---|---|
| Leave calendar 90% complete | "What if PTO data is incomplete?" | Medium → Low | Audit leave records for Jan–Mar; ask Priya if this is real problem |
| Org chart always current | Claude can't code org chart logic if it's ad-hoc | Low | Get SLA from IT on org chart refresh cadence |
| Priya can decide in < 5 minutes | Not questioned by Claude; but untested | Medium | Pilot with Priya; measure actual time |

---

## Build Loop Output Checklist

After running the build loop, verify:

- [ ] Claude identified no delegation boundary gaps (or you've clarified them)
- [ ] Claude has access to all required data sources (APIs, schemas, endpoints specified)
- [ ] Escalation workflows are coded-able (detection method + action defined)
- [ ] Failure modes have detection and recovery logic
- [ ] You've tagged low-confidence assumptions and planned verification
- [ ] Your autonomy matrix is no longer "everything to agent" or "everything to human" (reflects intentional design choice)

---

## When to Stop the Build Loop

Stop when Claude Code says:

> "I can now build this agent confidently. My remaining comments are implementation details: error handling patterns, performance optimization, monitoring setup. The design is clear."

This is your signal to move to **Phase 7: System/Data Inventory** (if needed for formal submission) or submit your refined artefacts for peer review.

---

## Next Step

Depending on your timeline:
- **If peer review is next:** Prepare your Cognitive Load Map, Delegation Matrix, Volume × Value Analysis, and Agent Purpose Document for submission.
- **If Gate 2 is next:** Use your refined artefacts as the seed for your Gate 2 timed exercise (you'll be given a new sealed scenario, but your methodology is now solid).
