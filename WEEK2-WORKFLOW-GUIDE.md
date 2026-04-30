# Week 2 ATX Assessment — Complete Workflow Guide

**Welcome to the FDE Week 2 prompt command files.** This guide walks you through a complete ATX (Agentic Transformation) assessment workflow for decomposing cognitive work and designing agents.

---

## What This Is

This is a **methodology toolkit** for Week 2, organized as 7 linked prompt phases. Each phase:
- Builds on the previous one
- Includes templates, rubrics, and examples
- Can be used with AI tools (Claude Code, Copilot) to accelerate your work
- Produces a deliverable that feeds into the next phase

---

## The 7-Phase Workflow

### Phase 1: Discovery Questioning — Elicit Lived Work
**File:** `PHASE-1-discovery-questioning.md`

**What you do:**
- Conduct structured interviews with your process owner / stakeholder
- Use a 3-funnel pattern (broad → narrow → probe) to uncover how work *actually* happens
- Record lived work, not documented process
- Surface discovery questions that would materially change your agent design

**Deliverable:** 
- Discovery Questions (6+) that reflect gaps between documentation and reality
- Notes on volume, frequency, pause points, and judgment calls

**Time:** 50–60 minutes with stakeholder

---

### Phase 2: Cognitive Load Map — Decompose Into Workable Units
**File:** `PHASE-2-cognitive-load-map.md`

**What you do:**
- Break work streams into Jobs to be Done (JtDs) — cognitive contracts, not just tasks
- Map micro-tasks into cognitive zones (intake, diagnosis, decision, execution, documentation)
- Identify breakpoints where control must hand off (human → agent → system → human)
- Ground every claim in artefacts (emails, system extracts, case notes)
- Mark assumptions with confidence levels

**Deliverable:** 
- Cognitive Load Map with JtDs, micro-tasks, zones, breakpoints
- Evidence table linking zones to artefacts
- Assumptions log

**Time:** 2–3 hours (iterative)

---

### Phase 3: Delegation Suitability Matrix — Score & Assign Archetypes
**File:** `PHASE-3-delegation-suitability.md`

**What you do:**
- Score each major task cluster on 5 dimensions: Input Structure, Decision Determinism, Exception Rate, Tool Coverage, Risk/Reversibility
- Calculate Suitability Score and Agentic Value Score
- Assign delegation archetypes (Fully Agentic, Agent-led + Oversight, Human-led + Agent Support, Human-led + Automation, Human Only)
- Defend each archetype assignment with evidence

**Deliverable:** 
- Delegation Suitability Matrix (table with scores and rationale)
- Assumption log (confidence for each score)

**Key anti-pattern to catch:** "Everything is Fully Agentic" — most common Week 2 mistake. Your matrix should show intentional variation in delegation levels.

**Time:** 1–2 hours

---

### Phase 4: Volume × Value Analysis — Prioritize the Highest-Impact Target
**File:** `PHASE-4-volume-value-analysis.md`

**What you do:**
- Score each work stream on Volume (execution frequency) and Non-Determinism (cognitive load)
- Calculate Agentic Value = Volume × Non-Determinism (1–25 scale)
- Plot on 2D chart; identify highest-value opportunity
- Verify economics close: baseline cost vs. agent cost
- Justify why you chose this target and why you didn't choose others

**Deliverable:** 
- Volume × Value Analysis with scores, chart, and justification
- Economic feasibility check (ROI calculation)
- Rationale for primary target and secondary targets (if applicable)

**Time:** 1–2 hours

---

### Phase 5: Agent Purpose Document — Design the Agent
**File:** `PHASE-5-agent-purpose-doc.md`

**What you do:**
- Write a precise, buildable specification for your agent
- Define Purpose, Scope, Autonomy Matrix, Activity Catalog, KPIs, Failure Modes, System/Data Requirements, Escalation & Oversight, Assumptions
- Make delegation boundaries explicit (what the agent decides vs. escalates)
- Include a build prompt for Claude Code that stress-tests your design

**Deliverable:** 
- Agent Purpose Document (comprehensive design spec)
- Build Prompt (structured prompt to hand to Claude Code)

**Time:** 3–4 hours (first draft); see Phase 6 for refinement

---

### Phase 6: Build Loop — Close Gaps in Your Design
**File:** `PHASE-6-build-loop.md`

**What you do:**
- Hand your Agent Purpose Document to Claude Code
- Ask three structured questions: What can you build? What needs clarification? Build the confident parts.
- Diagnose gaps Claude reveals (delegation boundary gaps, missing data/systems, ambiguous workflows, incomplete failure modes)
- Revise your document and re-run until Claude can build without major questions

**Deliverable:** 
- Refined Agent Purpose Document with gaps closed
- Build evidence (screenshots of Claude's questions and your revisions)
- Updated Assumptions log

**Time:** 2–3 hours per build loop (typically 1–2 loops needed)

---

### Phase 7: System/Data Inventory — Map Integration Requirements
**File:** `PHASE-7-system-data-inventory.md`

**What you do:**
- Document all systems the agent touches, data flows, API requirements
- Create data dictionary for each major entity (hire record, employee record, leave calendar, etc.)
- List all API endpoints with schemas, rate limits, timeouts, idempotency, fallbacks
- Map integration risks and mitigations
- Estimate cost (token cost + tool call cost + infrastructure)
- Create pre-launch checklist

**Deliverable:** 
- System/Data Inventory (comprehensive integration spec)
- Pre-Launch Checklist

**Time:** 3–4 hours (technical depth varies by complexity)

**Note:** This phase is optional if your focus is on Gate 2 evaluation rather than implementation. But it's essential if you're building.

---

## How to Use These Files

### Solo Workflow (You're Working Alone)

1. **Read the full context**: Start with Week 2 course materials (README-Participants-Week2.md, ATX concepts, scoring reference)
2. **Work through phases sequentially**: Each builds on the last
3. **Use AI as your thought partner**: 
   - Phase 1: Don't need AI; you're doing stakeholder interviews
   - Phase 2–5: Use Claude or Copilot to brainstorm, validate thinking, and surface gaps
   - Phase 6: Explicitly hand your work to Claude Code for stress-testing
   - Phase 7: Use AI to help structure and verify completeness

### Squad Workflow (You're Working With a Peer Review Partner)

1. **Monday–Tuesday**: Work through Phases 1–4 independently (or pair on Phase 1 interviews)
2. **Tuesday evening**: Share your Volume × Value Analysis with your peer; get feedback
3. **Wednesday**: Refine based on feedback; start Phase 5 (Agent Purpose Document)
4. **Wednesday afternoon**: Mid-week coach checkpoint; show your draft Agent Purpose Document
5. **Thursday morning**: Phase 6 (Build Loop) — run with Claude Code
6. **Thursday noon**: Exchange Phase 5 drafts with your peer for red-teaming
7. **Thursday 14:15**: Submit your strongest artefacts (Phases 1–5) for peer review
8. **Thursday 14:30–16:00**: Peer cross-review (review 2 others; receive 2 reviews)
9. **Thursday 16:00–17:00**: Incorporate feedback; refine
10. **Thursday evening / Friday morning**: Prepare for Gate 2 timed exercise

### Gate 2 Preparation

**These phases are your methodology toolkit for the timed exercise.**

On Gate 2 Friday (3-hour timed window), you'll receive a sealed scenario and must produce 7 deliverables:
1. Cognitive Load Map (Phase 2)
2. Delegation Suitability Matrix (Phase 3)
3. Volume × Value Analysis (Phase 4)
4. Agent Purpose Document (Phase 5)
5. System/Data Inventory (Phase 7)
6. Discovery Questions
7. Assumptions Discipline

Your practice using these phases **this week** is how you'll execute efficiently under time pressure in the gate.

---

## Key Principles Across All Phases

### Principle 1: Lived Work, Not Documented Work

Every phase requires grounding in evidence, not theory:
- In Phase 1, push back on "we follow the SOP" — ask what actually happens
- In Phase 2, cite artefacts (emails, system screenshots, case notes) for every zone and breakpoint
- In Phase 3, justify archetype assignments with lived-work examples
- In Phase 4, use actual volume data from discovery, not projections

**If you can't ground it in evidence, mark it as an assumption.**

---

### Principle 2: Assumptions Discipline

Every inference you make is an assumption. Record them explicitly:

| Assumption | Confidence | Impact if Wrong | Plan to Verify |
|---|---|---|---|
| [What you're assuming] | High/Medium/Low | [What changes if this is false] | [How you'll check] |

This discipline is a **Gate 2 rubric criterion**. Unmarked inferences read as bluffing.

---

### Principle 3: Avoid the "Everything is Fully Agentic" Anti-Pattern

This is the **#1 Week 2 mistake**. Most people assign "Fully Agentic" to everything because the agent *can* technically do it, not because it should.

Guard against this:
- Phase 3: Varied delegation levels (not all Fully Agentic)
- Phase 5: Clear escalation triggers (where agent hands off to human)
- Phase 6: Claude's questions about delegation boundaries

If your deliverables show everything is autonomous with no human oversight, you've missed the ATX methodology.

---

### Principle 4: Human Oversight Is a Design Choice, Not a Fallback

When you assign "Agent-led + Human Oversight" or "Human-led + Agent Support," you're making an intentional design choice based on:
- Exception rate (if > 20%, agent must escalate)
- Risk/reversibility (if mistake is high-stakes, human reviews)
- Stakeholder trust (is Priya comfortable with agent autonomy?)
- Volume (if rare, not worth fully automating)

Write this reasoning explicitly in your Delegation Suitability Matrix and Agent Purpose Document.

---

## Timeline Guidance

### Minimum (Deadline-Driven)
- **Phase 1**: 1 hour (quick stakeholder call)
- **Phase 2**: 2 hours (lightweight cognitive map)
- **Phase 3**: 1 hour (score major tasks only)
- **Phase 4**: 1 hour (identify top 1–2 targets)
- **Phase 5**: 2 hours (draft Agent Purpose Document)
- **Total**: 7 hours

Risks: Gaps in discovery, shallow analysis, weak assumptions discipline.

### Standard (Week 2 Pace)
- **Phase 1**: 1–2 hours (structured interview)
- **Phase 2**: 3–4 hours (detailed cognitive map + evidence)
- **Phase 3**: 2 hours (full scoring + archetype assignment)
- **Phase 4**: 2 hours (Volume × Value analysis + economics check)
- **Phase 5**: 4–5 hours (comprehensive Agent Purpose Document)
- **Phase 6**: 2–3 hours (1–2 build loops with Claude)
- **Total**: 14–17 hours

**Typical Week 2 distribution:**
- Monday: Phases 1–2 (discovery + initial mapping)
- Tuesday–Wednesday: Phases 3–4 (scoring + target selection) + mid-week checkpoint
- Wednesday evening–Thursday: Phases 5–6 (agent design + build loop refinement)
- Thursday 14:15: Submit; Thursday 14:30–16:00 peer review; Thursday 16:00–17:00 incorporate feedback

### Comprehensive (If You're Building)
- **All 7 phases**: 20–25 hours
- Plus Phase 7 (System/Data Inventory): 3–4 hours
- **Total**: 23–29 hours

---

## Deliverables Summary

| Phase | Output | Format | Gate 2 Use |
|---|---|---|---|
| 1 | Discovery Questions | List of 6+ questions | Gate 2 deliverable #6 |
| 2 | Cognitive Load Map | Markdown table + flowchart | Gate 2 deliverable #1 |
| 3 | Delegation Suitability Matrix | Markdown table + rationale | Gate 2 deliverable #2 |
| 4 | Volume × Value Analysis | Analysis doc + 2D plot | Gate 2 deliverable #3 |
| 5 | Agent Purpose Document | Comprehensive design spec | Gate 2 deliverable #4 |
| 7 | System/Data Inventory | Technical spec (if building) | Gate 2 deliverable #5 (if needed) |
| All | Assumptions Log | Table with confidence levels | Gate 2 deliverable #7 |

---

## How to Navigate This Toolkit

**Start here:** Read this file (you're reading it now)

**Pick your phase:**
- If you haven't interviewed the stakeholder yet → Phase 1
- If you need to decompose the work → Phase 2
- If you're scoring delegation suitability → Phase 3
- If you're prioritizing targets → Phase 4
- If you're designing the agent → Phase 5
- If you want to stress-test your design → Phase 6
- If you're integrating with systems → Phase 7

**Each phase file has:**
- Purpose statement (what you're trying to achieve)
- Step-by-step instructions
- Scoring rubrics / decision frameworks
- Templates and examples
- Common pitfalls to avoid
- Output format guidance
- Link to next phase

---

## FAQ

### Q: Do I have to do all 7 phases?

**A:** For Gate 2, you must do Phases 1–5 (plus discovery questions and assumptions discipline). Phase 6 (Build Loop) is optional but highly recommended because it catches delegation boundary gaps. Phase 7 is only needed if you're actually building the agent.

### Q: Can I skip Phase 1 (Discovery)?

**A:** No. Phase 1 is where you uncover the gap between documented process and lived work. If you skip it, your Cognitive Load Map will be built on fiction, and your delegation archetypes will be wrong.

### Q: What if my stakeholder doesn't have time for Phase 1?

**A:** Use async methods:
- Email them the 3 funnel levels and ask them to write responses
- Review existing artefacts (emails, system screenshots, tickets) and infer patterns
- Use office hours or coach checkpoints to validate your inferences

But try hard to do a live interview; it's where the insights emerge.

### Q: How do I know if my Agent Purpose Document is good?

**A:** It's good when Claude Code says (after Phase 6): "I can build this. My remaining questions are implementation details, not design gaps."

### Q: What should I do if peer review feedback contradicts the course materials?

**A:** Trust the ATX methodology first. If peer feedback says "everything should be fully agentic," that's the anti-pattern the course is designed to catch. Respond by citing the rubric criteria for delegation archetypes and explaining why you chose varied levels.

### Q: Should I use AI to *write* these deliverables?

**A:** Use AI to *think alongside you*, not to write on your behalf.
- **Good use:** "I'm stuck on whether this decision should be agent or human. Here's my thinking: [draft]. What gaps do you see?"
- **Bad use:** "Write my Cognitive Load Map for me."

AI should accelerate *your reasoning*, not replace it.

### Q: What's the difference between Phase 5 (Agent Purpose Document) and Phase 7 (System/Data Inventory)?

**A:** 
- **Phase 5** is *what the agent does* (purpose, scope, decisions, autonomy, KPIs, failure modes)
- **Phase 7** is *what systems and data the agent touches* (APIs, schemas, integrations, cost)

Both are important. Phase 5 is essential for Gate 2; Phase 7 is essential if you're actually building.

---

## Getting Help

### During Week 2

- **Monday–Thursday office hours**: Ask coaches clarifying questions about discovery, lived work gaps, or delegation archetypes
- **Wednesday mid-week checkpoint**: Show your Phases 2–4 drafts; get feedback before you commit to Agent Purpose Document
- **Thursday peer review**: Exchange drafts with other squads; get external eyes on your assumptions and archetype assignments

### Using These Prompt Files

Each phase file is self-contained. If you get stuck:
1. **Re-read the phase file's "Common Pitfalls" section** — the answer is probably there
2. **Check the examples** — see how archetype assignment or scaling works in practice
3. **Ask your coach** — they role-play your stakeholder and can answer domain-specific questions

### Using AI as Your Thought Partner

- **Phase 1**: Not applicable (you're interviewing humans)
- **Phase 2–5**: Paste your draft + ask: "What gaps do you see?" or "What questions would I need to answer to move from [current state] to [next state]?"
- **Phase 6**: Paste your Agent Purpose Document exactly as specified
- **Phase 7**: Paste your Phase 5 document + ask: "What APIs and data sources would you need access to? What's missing?"

---

## Final Word

Week 2 is where you learn to see cognitive work as it actually is, not as it should be or as documentation claims. The ATX methodology is a discipline in **evidence-driven reasoning about where agents can and should operate in real business processes**.

The prompt files in this folder are your tools for doing that reasoning systematically. Use them, trust the process, and when you're unsure, go back to discovery — to the lived work, the artefacts, the actual people who do the work.

**Good luck with Week 2. See you at Gate 2.**

---

## File Structure

```
PHASE-1-discovery-questioning.md     → Elicit lived work
PHASE-2-cognitive-load-map.md        → Decompose into JtDs + zones + breakpoints
PHASE-3-delegation-suitability.md    → Score + assign archetypes
PHASE-4-volume-value-analysis.md     → Prioritize high-value targets
PHASE-5-agent-purpose-doc.md         → Design the agent
PHASE-6-build-loop.md                → Stress-test with Claude Code
PHASE-7-system-data-inventory.md     → Map integrations & requirements
WEEK2-WORKFLOW-GUIDE.md              → This file
```

Start with this guide, then move to the phase you need.
