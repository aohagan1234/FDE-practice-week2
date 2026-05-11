# D4 — Two Production-Grade Capability Specifications
**Paste in:** D3 architecture. Run this prompt twice — once per capability.

---

## Prompt

```
Using the architecture below, produce a capability specification for [CAPABILITY NAME].

[PASTE D3 HERE]

**Capability name:**
**What it does:** 1 sentence. No vague words (do not use: appropriate, valid, handle, manage).

**Inputs** — table:
| Field | Type | Source system | Required? |

**Outputs** — table:
| Field | Type | Destination |

**Decision rules** — numbered list.
Each rule must be deterministic: if [condition] then [exact action].
No judgment calls. No implied logic.

**Error handling** — table:
| Error condition | What the agent does |

**Shared entities** — list any data entities this spec shares with the other capability spec.
Field names and types must be identical across both specs.

**Assumptions** — table:
| Assumption | Confidence (H/M/L) | What changes if wrong |
```

---

**Output should be:** The 6 sections above, exactly. Run once per capability. Check shared entities are consistent between the two outputs before submitting.
