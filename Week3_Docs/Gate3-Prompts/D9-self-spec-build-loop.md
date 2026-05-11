# D9 — Self-Spec Build-Loop Reflection
**Select one of your two D4 capability specifications. Run it through Claude Code, then use this prompt.**

---

## Step 1 — Run your spec through Claude Code

Paste the following into Claude Code:

```
Build this capability from the specification below. Where the specification is silent on a decision, ask me rather than inferring intent.

[PASTE ONE D4 SPEC HERE]
```

Note what was built, what questions were raised, and where the output diverged from your intent.

---

## Step 2 — Produce the reflection

```
Using my capability specification and the Claude Code output below, produce a 1-page build-loop reflection. Do not include any explanation or preamble.

[PASTE SPEC HERE]
[PASTE CLAUDE CODE OUTPUT HERE]

**What was built** — 3 bullet points describing the output produced.

**What Claude Code asked about** — bullet list of clarifying questions it raised.
If no questions were raised, note this and state what that implies about the spec.

**Signals in the output** — table:
| Signal | Classification | What the specification failed to say |

Use these classifications: spec gap | builder misread | unjustified implementation choice | test/environment issue.

**What I would change in the specification** — bullet list of specific rewrites.
Each bullet must include: the original requirement, what it should say instead, and why the original wording produced the wrong result.
```

---

**Expected output:** 4 sections as above. Maximum 1 page. This deliverable is assessed on the accuracy of the diagnosis, not on whether the build output was correct.
