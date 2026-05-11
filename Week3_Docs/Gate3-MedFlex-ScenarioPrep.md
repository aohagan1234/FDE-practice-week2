# Gate 3 — MedFlex Scenario Preparation
**Status:** Pre-release preparation. Based on partial scenario brief only.
**Do not treat this as the authoritative scenario. Verify every assumption against the released Gate3-Participant-Pack.md.**

---

## What we know

- Healthcare staffing agency, 200 employees
- CEO goal: "10x the business without 10x-ing the coordinators"
- Two prior failed AI projects: a chatbot and a recommendation engine that nobody used
- CEO timeline demand: results in 8 weeks

---

## What the full scenario likely looks like

Healthcare staffing agencies place temporary and permanent clinical staff — nurses, allied health professionals, locum doctors — into hospitals, clinics, and care homes. The core operational loop is:

1. A facility sends a job order (shift or placement need)
2. A coordinator identifies a suitable candidate from the agency's pool
3. The coordinator checks compliance (credentials, licences, background clearance)
4. The candidate is contacted, confirms availability, and is placed
5. The shift happens; timesheet is submitted and approved
6. Invoice raised; payment processed

At scale, coordinators run this loop dozens of times per day across multiple facilities and candidates simultaneously. The bottlenecks are almost always in steps 2–4: finding the right candidate fast, verifying they are compliant, and confirming them before the facility calls a competitor.

**What "10x without 10x-ing" actually means:**
This is not a technical requirement. It means the coordinator headcount cannot scale linearly with revenue. Currently, each coordinator likely manages a fixed book of facilities and candidates. To grow 10x, either coordinators handle 10x more cases (impossible without AI), or the work that consumes coordinator time is reduced dramatically. The real question is: which parts of the coordination loop consume skilled time that could be handled differently?

**Why the two prior projects failed:**
The chatbot tried to automate communication without solving the underlying matching and compliance problems — coordinators still had to do the hard work; the chatbot just added a layer on top. The recommendation engine surfaced matches but coordinators didn't trust it, probably because it didn't account for relationship history, client-specific preferences, or compliance edge cases. Both projects automated the wrong thing or at the wrong layer.

The CEO's impatience and the 8-week demand are signals: any solution must produce a visible, measurable result quickly. This rules out foundational infrastructure work (data pipelines, CRM replacement, compliance platform rebuild). The target is something that demonstrably reduces coordinator time on a specific, high-frequency task within 8 weeks.

---

## Likely coordinator pain points

These are hypotheses — confirm or refute each during the discovery call.

| Pain point | Why likely | Discovery question to validate |
|---|---|---|
| Manually searching for available, compliant candidates when a job order arrives | High frequency, time-sensitive, requires checking multiple systems | "Walk me through what happens the moment a job order lands. What do you do first?" |
| Compliance document expiry — chasing workers to renew licences, certifications | Ongoing admin burden; consequences of missing it are severe | "How do you know when a worker's credentials are about to expire? What do you do?" |
| Last-minute cancellations triggering a scramble to find a replacement | Urgent, stressful, high-consequence | "Tell me about the last time a worker cancelled a shift last-minute. What happened?" |
| High volume of routine confirmations, reminders, and status updates | Repetitive; consumes time that could be used for matching | "What percentage of your messages are chasing confirmations or reminders vs actual decisions?" |
| Job order intake from facilities arriving inconsistently (email, phone, portal) | Creates manual triage before matching even begins | "How do job orders come in? Do they always arrive in the same format?" |

---

## Discovery questions for the call

Organised by the 60-minute call structure.

### Minutes 0–5 — Context setting

- "Before we go into process detail — in a typical week, where does your team's time actually go? Not what the system tracks, but where you feel the effort is."
- "You mentioned wanting to grow without growing the team. If I asked a coordinator right now what takes up most of their day, what would they say?"

### Minutes 5–15 — Broad funnel

- "Walk me through a coordinator's day. What is the first thing they do when they arrive, and how does it unfold from there?"
- "What are the tasks that feel repetitive — where you know what to do before you even start?"
- "When a coordinator is under pressure, what's the work that gets dropped or delayed first?"
- "How many job orders does a coordinator handle in a typical day, and how many of those fill cleanly vs. cause problems?"

### Minutes 15–30 — Narrow funnel (matching process)

- "Take me through a real job order from this week. Not how it's supposed to work — what actually happened, step by step."
- "When you're looking for the right candidate for a shift, how do you decide who to contact first?"
- "At what point in the process do you stop and have to think, rather than just execute?"
- "What information do you need before you feel confident placing someone, and where does that information come from?"
- "Are there candidates you would always call first for certain facilities? Why? Is that written down anywhere?"

### Minutes 30–45 — Lived vs documented

- "Is there a standard process for filling a job order? How closely does what actually happens match that process?"
- "What are the most common reasons a straightforward job order becomes complicated?"
- "When you check a candidate's compliance status, where do you look? Is it always in the same system, or do you check multiple places?"
- "Are there decisions that two coordinators might make differently for the same job order? What causes that?"

### Minutes 45–55 — Delegation signals

- "If you had to write down the rules you follow when choosing a candidate — the factors you weigh — could you do it? What would be on the list?"
- "What percentage of job orders fit a clear pattern versus require a judgment call?"
- "If an AI system surfaced the top three candidates for a job order with reasons, and you could override it at any point — would that be useful, or would you not trust it?"
- "What would have to be true about a system's output for you to use it without double-checking every time?"
- "What's the worst thing that could happen if the system made the wrong call? How would you detect it?"

### Minutes 55–60 — Close

- "Based on what you've told me, the heaviest coordinator burden seems to be [X]. Is that accurate, or is there something more significant I've missed?"
- "Is there anything about how MedFlex operates that would make a standard staffing automation approach not work here?"

---

## Assumptions to test during the call

| Assumption | What breaks if wrong |
|---|---|
| Coordinators are the main bottleneck, not the candidate or facility side | The agent targets the wrong part of the workflow |
| Job orders arrive in a consistent enough format to be processed systematically | Intake cannot be automated; structured data is unavailable |
| Candidate compliance data is centralised and accessible in one system | Compliance checks remain manual regardless of automation |
| The matching criteria are partially codifiable (even if not fully) | Full agentic matching is not feasible; recommendation engine failure repeats |
| Coordinators are willing to act on agent-surfaced candidates without full re-verification | Trust gap prevents adoption; same failure mode as prior recommendation engine |
| 8 weeks is a constraint on showing early value, not on full deployment | Timeline is unachievable if interpreted as full production deployment |

---

## Agentic vs deterministic analysis

This is the most important output of this section. The prior recommendation engine failed partly because it tried to do agentic work (reasoning about fit) with deterministic methods (a scoring algorithm coordinators didn't trust). The distinction below should drive what goes into a capability spec vs. what gets built as a scheduled job or rule-based workflow.

### Deterministic — use a scheduled job or workflow, not an agent

These tasks follow fixed rules with no context-dependent judgment. Building an agent for them adds cost and complexity with no additional value.

| Task | Why deterministic | Correct implementation |
|---|---|---|
| Licence and certification expiry alerts | Check expiry date against today + threshold. No reasoning required. | Scheduled job: runs daily, sends alert when days_until_expiry < 30 |
| Shift confirmation reminders | Send reminder N hours before shift if status = unconfirmed. No reasoning required. | Scheduled job: time-triggered message |
| Timesheet submission reminders | Send reminder if timesheet not submitted by deadline. No reasoning. | Scheduled job |
| Compliance document collection follow-up | If document X not received by date Y, send chase. No reasoning. | Scheduled workflow with escalation after N days |
| Basic candidate availability check | Is candidate marked available for this date/time? Binary lookup. | Rule-based filter, not an agent |
| Invoice generation | Hours × rate = amount. No reasoning. | Automated calculation triggered by approved timesheet |

### Genuinely agentic — requires reasoning over context

These tasks cannot be solved reliably by a fixed rule because the right answer depends on context that varies per case.

| Task | Why agentic | What the agent reasons over |
|---|---|---|
| Prioritising which unfilled job orders to pursue first | Depends on client relationship value, margin, time pressure, candidate pool depth, facility tolerance — not reducible to a single rule | Order urgency + client tier + fill probability + coordinator capacity |
| Candidate outreach sequencing | Who to contact first for a given shift depends on past performance at that facility, relationship, recent availability pattern, channel preference — not just a ranked list by score | Candidate history, facility fit, channel effectiveness, recency |
| Last-minute cancellation recovery | Finding a replacement in hours requires reasoning about who is available, compliant, experienced with that facility, and reachable — with escalation logic if no match found | Urgency + compliance + facility familiarity + contact probability |
| Job order interpretation | Facilities often send vague or non-standard requests; determining what they actually need before searching requires reading intent | Request text + facility history + common patterns for that client |

### The boundary question — where coordinators push back hardest

The prior recommendation engine failed because coordinators didn't trust it. The agent design must account for this. Recommendations must be:
- Explainable (why this candidate for this role)
- Overridable (coordinator always has final say)
- Fast to act on (one click to confirm, not a form)
- Accurate enough that overriding becomes the exception, not the norm

The agent earns trust incrementally. Start with lower-stakes use cases (outreach sequencing, cancellation recovery) before attempting full match recommendation.

---

## What the 8-week constraint actually means

8 weeks to full production is not realistic for a complex matching agent. 8 weeks to a demonstrable result is.

Realistic 8-week target: a working agent that handles one high-frequency, high-pain task end-to-end — most likely either cancellation recovery (urgent, high-stress, clear value) or compliance expiry tracking with automated outreach (deterministic but visible and immediate). Neither requires the full matching engine.

Frame this to the CEO as: the first agent proves the infrastructure and trust model. The matching capability is Wave 2, built on the proof of Wave 1. This addresses his two prior failures — both tried to skip to the complex capability without building coordinator trust first.

---

## What to watch for in the discovery call

- **Evasion:** "We have a process for that" — push for the lived version, not the documented one
- **Contradiction:** "Matching is straightforward" followed by descriptions of frequent overrides and exceptions — this is where the agent value lives
- **Scope inflation:** the CEO saying "and it should also do X" — each addition adds risk to the 8-week target; note it, do not commit
- **Trust signals:** listen for how coordinators talk about the failed recommendation engine — their specific objections tell you what the new design must address
