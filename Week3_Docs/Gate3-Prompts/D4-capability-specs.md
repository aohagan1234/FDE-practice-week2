# D4 — Production-Grade Capability Specification
**Run this prompt once per capability. You need two specs in total.**
**Paste in:** Your D3 architecture output.

---

## Prompt

```
Using the architecture below, produce a capability specification for [CAPABILITY NAME]. Do not include any explanation or preamble.

[PASTE D3 HERE]

**Capability name:**
**What it does:** 1 sentence. Do not use vague words such as: appropriate, valid, handle, manage, ensure.

**Inputs** — table:
| Field | Type | Source system | Required? |

**Outputs** — table:
| Field | Type | Destination |

**Decision rules** — numbered list.
Each rule must follow the format: if [condition] then [exact action].
Do not include judgment calls or implied logic.

**Error handling** — table:
| Error condition | What the agent does |

**Shared entities** — list any data entities this spec shares with the other capability specification.
Field names and types must be identical across both specs.

**Assumptions** — table:
| Assumption | Confidence (H/M/L) | What changes if this assumption is wrong |
```

---

**Expected output:** The 6 sections above, exactly. Run once per capability. Before submitting, confirm that any shared entities are consistent between both specs.
