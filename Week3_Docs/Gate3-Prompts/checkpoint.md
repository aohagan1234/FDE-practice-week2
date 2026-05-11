# Decision Checkpoint Prompt
**Use after D1, D3, and D4 before moving to the next deliverable.**
**Paste in:** The output from the deliverable you just completed.

---

## Prompt

```
Review the output below and identify only the decisions that, if wrong, would change everything that comes after them.

[PASTE DELIVERABLE OUTPUT HERE]

For each decision produce:

**Decision:** what was decided
**Assumed because:** what information or assumption led to this conclusion
**If this is wrong:** what breaks in the deliverables that follow
**Confirm this with me:** one question I should be able to answer to verify this decision is correct

Do not include minor or implementation-level decisions. Surface only decisions that affect scope, architecture, or agent behaviour.
```

---

## What to do with the output

Read each decision and answer the question it raises.

- **If you agree:** move on to the next deliverable.
- **If you are unsure:** answer "I don't know" — the checkpoint will surface that this assumption needs to be validated before proceeding.
- **If you disagree:** correct that specific section of the deliverable output directly, then proceed. Do not re-run the full deliverable prompt.

---

## When to run this

| After | Why |
|---|---|
| **D1** | The problem framing drives every success metric. A wrong framing here means all subsequent work measures the wrong thing. |
| **D3** | The architecture and ADRs determine which parts of the workflow are agentic and why. D4 specs the wrong capability if D3 is wrong. |
| **D4** | The decision rules are what the builder implements. Ambiguous or missing rules here are the most common source of build-loop failures. |
