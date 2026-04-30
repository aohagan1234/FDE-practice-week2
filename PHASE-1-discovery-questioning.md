# Phase 1: Discovery Questioning — Elicit Lived Work

**Goal:** Move beyond documented SOPs to understand how work actually happens.

**Use this prompt with your assigned stakeholder (coach role-playing).**

---

## Funnel Structure (50-60 minutes total)

### Level 1: Broad Funnel — Work Patterns & Cognitive Load (10 min)

Ask for categories and patterns, not tasks:

- "Walk me through how your team spends time on a typical day. What are the biggest time sinks?"
- "When you say you're 'busy,' what kinds of work are you actually doing? Can you give me an example from this week?"
- "If I were shadowing your team, what would I see consuming the most attention?"
- "What work feels repetitive vs. what feels genuinely new each time?"
- "How many [cases/requests/transactions] does your team handle per week/month?"

**Listen for:**
- Categories of work and their frequency
- Frustration points and context switching
- Volume scales and handling times
- Pause points where humans stop to think or verify

**Avoid:** "Tell me about your current system" or "What are your pain points?"

---

### Level 2: Narrow Funnel — Zoom Into One Category (20 min)

Pick one high-cognitive-load category. Get specifics about lived practice:

- "You mentioned [category] is a headache. Walk me through an actual [category] scenario from the past week. Not how it's supposed to work — how did it actually happen?"
- "Where do you have to stop and think? Where do you have to call someone or check something?"
- "Tell me about the last time something went wrong in this process. What happened?"
- "You said you're [workaround]. Why can't the system do that automatically?"
- "What sources of information do you have to consult to make a decision here?"

**Listen for:**
- Specific pause points and coordination work
- Judgment criteria and decision patterns
- Exception handling (% of cases vs standard pattern)
- Information sources (how many systems/people to consult?)
- Async waits and blockers

**Push back gently on SOP answers:** "That's what the manual says, but in practice what actually happens?"

---

### Level 3: Probe Funnel — Detect Agentic Patterns (15-20 min)

Probe for where decisions might be structured and delegatable:

- "When you make that decision [the judgment you identified], is there a pattern? If X is true and Y is true, you do A; if Z is true, you do B?"
- "How often are you actually thinking vs. executing a pattern you've already decided?"
- "Could you articulate the criteria you use to decide this right now?"
- "Are there cases where you'd be comfortable with an AI agent making this decision if you could review it first?"
- "If the agent got it wrong, what's the consequence? How would you detect it?"
- "Does this need to happen in real-time, or could it happen asynchronously (agent queues it, you review later)?"
- "What percentage of cases fit the standard pattern vs. exceptions?"

**Listen for:**
- Codifiability (can the rule be articulated?)
- Exception rate (if >20%, agent must handle or escalate)
- Risk and reversibility (is a mistake high-stakes or easily corrected?)
- Latency requirements (immediate vs asynchronous?)
- Human trust (openness to agent involvement?)

---

## Discovery Questions Output

Record at least **6 design-changing discovery questions** whose answers would materially reshape your agent architecture. Examples:

- "How many [work items] fall into exception categories vs. the standard pattern?"
- "What prior automation attempts have been tried, and what went wrong?"
- "Which stakeholders must approve [decision] vs. which would you handle alone if delegated to you?"
- "How is success measured for [this work]? What metrics matter?"
- "What data sources are authoritative, and which are approximate/advisory?"
- "Where is information currently copied between systems, and why?"

---

## What NOT to skip

- **Lived work over documented work**: Always push back on "we follow the SOP." Ask what actually happens.
- **Specificity**: Generic answers ("we process a lot") don't move the design. Nail down volumes, times, constraints.
- **Exception handling**: This is where most agents fail. 20%+ exception rate = major design challenge.
- **Context switching**: If the human has to consult 5 systems to make one decision, that's a system design problem to solve alongside delegation.

---

## Refinement Prompts: Commands Used to Improve This Deliverable

The initial draft of DELIVERABLE-1 produced six technically sound discovery questions that read like an audit checklist — they confirmed what was in the SOP rather than surfacing what the human actually does. The following prompts were used to rewrite it into a lived-work discovery document.

---

### Prompt 1: Rewrite for lived work, not SOP confirmation

```
Rewrite the discovery questions so they surface lived work, not documented processes.
Each question must probe one of these categories:

- What is actually on the human's screen (not what the system is supposed to show)
- Workarounds and shadow systems they use instead of the official tool
- Informal channels used when something is urgent (Teams, WhatsApp, phone)
- Instinct decisions made before checking any system
- What tribal knowledge would be lost if this person left

Do not ask "how does the process work?" Ask questions that force the human to describe
specific recent incidents, name actual tools they use, and reveal the gap between
what the SOP says and what they do.
```

**What this fixed:** Moved from 6 confirmatory questions ("What systems do you use?") to 6 operational probes ("What's on your screen right now when you do this work?"), each targeting a distinct category of lived-work signal.

---

### Prompt 2: Simulate the stakeholder answering

```
Imagine you are [stakeholder name], the [role], answering these discovery questions.
Answer each one as someone who:
- Has been doing this work for [X] years
- Has developed workarounds because the official system is unreliable
- Uses informal channels the SOP doesn't mention
- Has specific incidents in mind (name real artifacts, real people, real systems)
- Would not volunteer these details unless asked directly

Use the answers to identify what changed in the agent design — not what you already knew,
but what the lived-work answers revealed that the SOP didn't show.
```

**What this fixed:** Produced a COO simulation with specific named artifacts (iPhone Notes app as real I-9 tracker, Priya's Excel tracker as operational source of truth, Legacy HR tab for pre-2019 contractor records). Each answer revealed a concrete design change.

---

### Prompt 3: Generate refined follow-up questions from the answers

```
For each COO answer that revealed a gap or assumption not in the original design,
write one targeted follow-up question. The follow-up should:
- Target the specific gap the answer opened (not a general probe)
- Use the stakeholder's own language from their answer
- Have a clear design impact if answered "yes" vs. "no"

Structure as: RQ[N]: [Question] — Design impact: [what changes if the answer is X]
```

**What this fixed:** Turned the COO simulation into 7 actionable follow-ups (RQ1–RQ7), each with a stated design consequence, so the next conversation with the real stakeholder has a precise agenda rather than open-ended questions.

---

### Prompt 4: Update the assumptions table to reflect what the simulation revealed

```
Review the original assumptions table against the COO simulation answers.
For each assumption:
- If the simulation confirmed it: keep, mark HIGH confidence
- If the simulation revealed it may be wrong: update, mark LOW confidence, add "What changes if wrong"
- If the simulation revealed a new assumption not in the original table: add it

Mark any assumption as LOW if the only evidence for it is the SOP.
```

---

## Next Step

Once you have recorded lived-work insights and discovery questions, move to **Phase 2: Cognitive Load Mapping**.
