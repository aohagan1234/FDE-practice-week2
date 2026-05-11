# D9 — Self-Spec Build-Loop Reflection
**Pick ONE of your two D4 capability specs. Run it through Claude Code. Then use this prompt.**
**Paste in:** The spec you chose + what Claude Code produced.

---

## Step 1 — Run your spec through Claude Code

Paste this into Claude Code:

```
Build this capability from the spec below. Do not infer intent where the spec is silent — ask me instead.

[PASTE ONE D4 SPEC HERE]
```

Note what it built, what it asked, and where it went in a direction you didn't intend.

---

## Step 2 — Write the reflection

```
Using my capability spec and Claude Code's output below, produce a 1-page build-loop reflection.

[PASTE SPEC HERE]
[PASTE CLAUDE CODE OUTPUT HERE]

**What Claude Code built** — 3 bullet points describing what it produced.

**What it asked about** — bullet list of any clarifying questions it raised. If none, note that and say what that implies.

**Signals in the output** — table:
| Signal | Classification | What my spec failed to say |

Use these classifications: spec gap | builder misread | unjustified implementation choice | test/environment issue.

**What I would change in the spec** — bullet list of specific rewrites.
Each bullet names: the original requirement, what it should say instead, and why the original wording failed.
```

---

**Output should be:** 4 sections as above. 1 page. Graded on diagnosis honesty — a broken build diagnosed accurately scores higher than working code with no reflection.
