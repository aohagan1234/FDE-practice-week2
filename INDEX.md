# Week 2 ATX Prompt Command Files — Complete Index

This folder now contains **9 comprehensive prompt files** that guide you through the complete Week 2 ATX (Agentic Transformation) methodology for cognitive work assessment and agent design.

---

## Files Created

### 🎯 Start Here
- **[WEEK2-WORKFLOW-GUIDE.md](WEEK2-WORKFLOW-GUIDE.md)** — Master guide; overview of all 7 phases, timeline guidance, how to use these files
- **[QUICK-REFERENCE-CARD.md](QUICK-REFERENCE-CARD.md)** — One-page scoring rubrics, formulas, anti-patterns, and troubleshooting

### 📋 The 7-Phase Workflow

**Phase 1: Discovery Questioning**
- **[PHASE-1-discovery-questioning.md](PHASE-1-discovery-questioning.md)**
- Elicit how work *actually* happens (not documented SOP)
- 3-funnel interview structure (broad → narrow → probe)
- Output: Discovery questions (6+) + lived-work insights
- Time: 50–60 minutes with stakeholder

**Phase 2: Cognitive Load Mapping**
- **[PHASE-2-cognitive-load-map.md](PHASE-2-cognitive-load-map.md)**
- Decompose work into Jobs to be Done, cognitive zones, breakpoints
- Ground in artefacts (emails, screenshots, case notes)
- Output: Cognitive Load Map table + evidence table + assumptions log
- Time: 2–3 hours

**Phase 3: Delegation Suitability Matrix**
- **[PHASE-3-delegation-suitability.md](PHASE-3-delegation-suitability.md)**
- Score tasks on 5 dimensions (input structure, decision determinism, exception rate, tool coverage, risk)
- Assign one of 5 delegation archetypes per task cluster
- Output: Suitability Matrix + rationale + assumption confidence log
- Time: 1–2 hours

**Phase 4: Volume × Value Analysis**
- **[PHASE-4-volume-value-analysis.md](PHASE-4-volume-value-analysis.md)**
- Prioritize high-impact targets using Volume × Non-Determinism scoring
- Verify economics (ROI calculation)
- Output: Volume × Value Analysis + 2D plot + justification
- Time: 1–2 hours

**Phase 5: Agent Purpose Document**
- **[PHASE-5-agent-purpose-doc.md](PHASE-5-agent-purpose-doc.md)**
- Comprehensive agent design spec with purpose, scope, autonomy matrix, activity catalog, KPIs, failure modes, system/data requirements
- Includes build prompt to stress-test design with Claude Code
- Output: Agent Purpose Document (ready for implementation or build loop)
- Time: 3–4 hours (first draft)

**Phase 6: Build Loop & Refinement**
- **[PHASE-6-build-loop.md](PHASE-6-build-loop.md)**
- Hand Agent Purpose Document to Claude Code; diagnose delegation gaps, missing data, ambiguous workflows
- Iterate until design is solid
- Output: Refined Agent Purpose Document + build evidence
- Time: 2–3 hours per loop (typically 1–2 loops needed)

**Phase 7: System/Data Inventory**
- **[PHASE-7-system-data-inventory.md](PHASE-7-system-data-inventory.md)**
- Technical specification: systems, APIs, data flows, cost estimation, pre-launch checklist
- Optional (needed only if actually building); essential for implementation
- Output: System/Data Inventory + API documentation + risk mitigation + cost model
- Time: 3–4 hours

---

## How to Use These Files

### 🚀 Quick Start (5 minutes)

1. **Open [WEEK2-WORKFLOW-GUIDE.md](WEEK2-WORKFLOW-GUIDE.md)** — Read the overview and timeline
2. **Open [QUICK-REFERENCE-CARD.md](QUICK-REFERENCE-CARD.md)** — Keep this tab open while working
3. **Pick your phase** — Go to the corresponding PHASE file

### 📊 For Week 2 Coursework (Phases 1–5)

**Monday–Tuesday:**
- Phase 1: Conduct stakeholder interviews
- Phase 2: Map cognitive load

**Tuesday–Wednesday:**
- Phase 3: Score delegation suitability
- Phase 4: Analyze volume × value
- **Wednesday mid-week coach checkpoint:** Show Phases 2–4 drafts

**Wednesday evening–Thursday:**
- Phase 5: Draft Agent Purpose Document
- Phase 6: Build loop with Claude Code (refine design)

**Thursday 14:15:** Submit Phases 1–5 + assumptions log + discovery questions

**Thursday 14:30–16:00:** Peer review (review 2 others, receive 2 reviews)

**Friday 09:00–12:00:** Gate 2 timed exercise (apply methodology to new sealed scenario)

### 🔧 For Building an Agent (All 7 Phases + Implementation)

- Complete Phases 1–6 as above
- Add Phase 7: Technical systems/data inventory
- Hand all artefacts to engineering team with build prompt from Phase 5

### 🎓 For Gate 2 Preparation

These 7 phases **are your methodology template** for the 3-hour timed exercise. Practice using them this week so you can execute efficiently when you receive the sealed scenario on Friday.

---

## Key Features Across All Files

✅ **Step-by-step instructions** — Not just theory; actionable workflows

✅ **Scoring rubrics & decision frameworks** — Standardized assessment (reproducible, defensible)

✅ **Real examples** — HR Onboarding scenario threaded throughout

✅ **Anti-pattern detection** — "Everything is Fully Agentic" is the #1 Week 2 mistake; we flag it

✅ **AI integration prompts** — Ready-to-use prompts for Claude Code (Phase 6)

✅ **Evidence grounding** — Every claim must cite artefacts or assumptions logged

✅ **Assumptions discipline** — Track confidence levels; unmarked inferences = bluffing

✅ **Peer review guidance** — Red flags to catch in others' work

✅ **Gate 2 alignment** — All 7 deliverables directly mapped to Gate 2 rubric

---

## The 5 Core Principles Across All Phases

### 1. Lived Work, Not Documented Work
Every phase requires grounding in evidence. If you find yourself mapping the SOP instead of what people actually do, you've gone astray.

### 2. Assumptions Discipline
Record every inference explicitly with confidence levels. Unmarked assumptions read as bluffing.

### 3. Avoid "Everything is Fully Agentic"
Delegation levels should vary based on evidence. If everything is autonomous, you've skipped the ATX methodology.

### 4. Delegation Boundaries Are Design Choices
When you assign "Agent-led + Human Oversight" or "Human-led + Agent Support," you're making an intentional choice, not a fallback.

### 5. Escalation Triggers Must Be Specific
Not "if complex" or "if needed." Specify the exact condition: "if exception rate > 20%" or "if candidate availability is incomplete."

---

## Quick Troubleshooting

| **I'm stuck on...** | **File to read** |
|---|---|
| How to structure my stakeholder interview | PHASE-1-discovery-questioning.md → Funnel Structure section |
| What counts as a "Job to be Done" vs. a task | PHASE-2-cognitive-load-map.md → What is a Cognitive Load Map? section |
| How to score a task on delegation suitability | QUICK-REFERENCE-CARD.md → Delegation Suitability Scoring |
| Whether my archetype assignment is defensible | PHASE-3-delegation-suitability.md → Assigning Archetypes section |
| Why my Volume × Value score is so low | PHASE-4-volume-value-analysis.md → Interpretation thresholds section |
| What should go in an Agent Purpose Document | PHASE-5-agent-purpose-doc.md → 10 sections listed |
| How to use Claude Code to find design gaps | PHASE-6-build-loop.md → Gap Type 1, 2, 3 |
| What APIs I need to document | PHASE-7-system-data-inventory.md → API Endpoint Reference section |
| Why my peer review feedback says "everything is fully agentic" | QUICK-REFERENCE-CARD.md → Anti-Pattern Checklist |

---

## File Format & Dependencies

All files are **standalone Markdown documents**. You can:
- Read them in any order (though Phases 1–7 have sequential dependencies)
- Print them
- Share with peers or coaches
- Reference them during Gate 2 timed exercise
- Use them as templates for your own submissions

**No special software needed** — open in any text editor or Markdown viewer.

---

## How These Fit Into Week 2 Calendar

| **When** | **What** | **Which Files** |
|---|---|---|
| **Monday (Week 2)** | Orientation + start Phase 1 | WEEK2-WORKFLOW-GUIDE.md + PHASE-1 |
| **Tuesday** | Continue Phase 1 + do Phase 2 | PHASE-1 + PHASE-2 |
| **Tuesday evening** | Peer feedback on Phases 2–4 | WEEK2-WORKFLOW-GUIDE.md (squad workflow) |
| **Wednesday** | Phase 3 + Phase 4 + mid-week checkpoint | PHASE-3 + PHASE-4 + QUICK-REFERENCE-CARD |
| **Wednesday evening** | Start Phase 5 (Agent Purpose Document) | PHASE-5 |
| **Thursday** | Phase 6 (Build Loop with Claude Code) | PHASE-6 |
| **Thursday 14:15** | Submit best work (Phases 1–5) | All phases (use as templates) |
| **Thursday 14:30–16:00** | Peer cross-review | QUICK-REFERENCE-CARD (red flags section) |
| **Thursday 16:00–17:00** | Incorporate feedback | All phases (for refinement guidance) |
| **Friday 09:00–12:00** | Gate 2 timed exercise | WEEK2-WORKFLOW-GUIDE.md + QUICK-REFERENCE-CARD (on your desk) |

---

## How to Submit Your Week 2 Work

**Thursday 14:15 CET submission should include:**

1. **Cognitive Load Map** (Phase 2)
   - File: Your markdown table + flowchart / diagram
   - Evidence table linking zones to artefacts

2. **Delegation Suitability Matrix** (Phase 3)
   - File: Your scoring table + archetype assignments + rationale
   - Assumptions log with confidence levels

3. **Volume × Value Analysis** (Phase 4)
   - File: Your analysis + 2D plot + economic justification
   - Rationale for primary target selection

4. **Agent Purpose Document** (Phase 5)
   - File: Your comprehensive design spec
   - All 10 sections from the template

5. **Discovery Questions** (From Phase 1)
   - File: List of 6+ design-changing questions
   - Reference to where in your analysis each was addressed

6. **Assumptions Discipline** (From all phases)
   - File: Master assumptions table
   - Confidence levels + impact of each being wrong

7. **CLAUDE.md** (Optional but recommended)
   - Brief notes on:
     - Which phases you used AI for
     - Key Claude insights that shaped your design
     - Build loop iterations (how many? what changed?)

---

## Getting the Most Out of These Files

### ✅ Do This

- **Read each phase file fully before starting that phase** — context matters
- **Use QUICK-REFERENCE-CARD as your working document** — keep it on screen
- **Ground every claim in evidence** — cite artefacts, don't speculate
- **Iterate:** If your delegation suitability matrix looks wrong, go back to Phase 2 and refine your cognitive load map
- **Ask coaches:** If a phase seems unclear or the example doesn't match your scenario, ask during office hours
- **Peer review actively:** Use the red flags checklist to give constructive feedback

### ❌ Don't Do This

- **Skip Phase 1** — the entire methodology depends on lived-work discovery
- **Assume everything is Fully Agentic** — this is the anti-pattern the course is designed to catch
- **Leave assumptions unmarked** — that's bluffing, not analysis
- **Use AI to write for you** — use it to think alongside you
- **Submit without grounding in evidence** — every key claim needs an artefact or marked assumption

---

## Feedback & Iteration

If something in these files is unclear:

1. **Check WEEK2-WORKFLOW-GUIDE.md → FAQ section** — your question might already be answered
2. **Ask your coach** during office hours or mid-week checkpoint
3. **Peer review feedback** — if another squad got a similar clarification, they might have the answer

---

## What You'll Be Able to Do After Using These Files

By the end of Week 2:

- [ ] Elicit lived work instead of documented SOP
- [ ] Decompose cognitive work into Jobs to be Done, zones, and breakpoints
- [ ] Score delegation suitability defensibly (not just gut feel)
- [ ] Identify which work creates the most agentic value
- [ ] Design an agent with clear purpose, scope, autonomy, and escalation triggers
- [ ] Stress-test your design using Claude Code
- [ ] Map all system integrations and data requirements
- [ ] Distinguish evidence from assumptions (and mark assumptions honestly)
- [ ] Identify the anti-pattern (everything is fully agentic) and avoid it
- [ ] Be ready for Gate 2

---

## One More Thing

**Week 2 is the hardest week.** It requires you to think like a business process analyst + agentic systems designer + evidence-driven reasoner. That's a lot.

Use these files as your scaffold. They're not creativity killers; they're structure that frees you to think clearly. Trust the process. Ground in evidence. Mark your assumptions. And remember: delegation archetypes should vary. If they don't, you've skipped the work.

---

## File Checklist Before Gate 2

- [ ] All 7 PHASE files read and understood
- [ ] QUICK-REFERENCE-CARD printed or saved to easy access
- [ ] WEEK2-WORKFLOW-GUIDE bookmarked
- [ ] Phases 1–5 practiced on your assigned scenario
- [ ] Phase 6 (Build Loop) completed at least once
- [ ] Peer feedback incorporated
- [ ] Ready to apply all 7 phases to sealed Gate 2 scenario

---

**Start with WEEK2-WORKFLOW-GUIDE.md. Pick your phase. Go.**

Good luck with Week 2. See you at Gate 2.
