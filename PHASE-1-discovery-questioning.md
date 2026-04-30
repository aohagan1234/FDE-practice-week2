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

## Next Step

Once you have recorded lived-work insights and discovery questions, move to **Phase 2: Cognitive Load Mapping**.
