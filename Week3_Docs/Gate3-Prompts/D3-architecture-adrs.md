# D3 — Agentic Solution Architecture + ADRs
**Paste in:** Your D1 and D2 outputs.

---

## Prompt

```
Using the problem framing and scope below, produce the following. Do not include any explanation or preamble.

[PASTE D1 HERE]
[PASTE D2 HERE]

**Workflow delegation map** — table:
| Workflow step | Current method | Delegation level | Reason |

Delegation levels: Fully Agentic | Agent-led + human oversight | Human-led + automation support | Human only.

For every step marked Fully Agentic or Agent-led, the reason column must answer this question:
"Does this step require reasoning over context to reach an outcome that a fixed rule or scheduled job could not reach?"
If the answer is no — if the step could be implemented as an if/else rule, a deterministic function, or a scheduled job — do not mark it as agentic. Mark it as Human-led + automation support and note the simpler implementation instead.
A step is only agentic if the input conditions are too variable or ambiguous for a rule to handle reliably.

**ADR 1 — [name the decision]**
- Decision:
- Alternative A: [name it] — consequences if this had been chosen:
- Alternative B: [name it] — consequences if this had been chosen:
- Why the chosen option was selected:
- Conditions that would require this decision to be revisited:

**ADR 2 — [name the decision]**
- Decision:
- Alternative A: [name it] — consequences if this had been chosen:
- Alternative B: [name it] — consequences if this had been chosen:
- Why the chosen option was selected:
- Conditions that would require this decision to be revisited:
```

---

**Expected output:** 1 workflow table and 2 ADRs in the exact structure above. Do not write ADRs as justifications — each must name real alternatives and their consequences.
