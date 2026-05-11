# Gate 3 Prompt Files

One prompt file per deliverable. Use them in order — earlier outputs feed into later prompts.

| File | Deliverable | When to use | Input required |
|---|---|---|---|
| `00-discovery-prep.md` | Discovery preparation | Before the live discovery call | Scenario pack |
| `D1-problem-framing.md` | D1 — Problem framing & success metrics | After discovery call | Scenario + discovery notes |
| `D2-intake-scope.md` | D2 — Engagement intake & scope | After discovery call | Scenario + discovery notes + D1 |
| `D3-architecture-adrs.md` | D3 — Agentic architecture + 2 ADRs | After discovery call | D1 + D2 |
| `D4-capability-specs.md` | D4 — Two capability specifications | Timed gate | D3. Run once per capability. |
| `D5-build-loop-memo.md` | D5 — Build-loop response memo | Timed gate | Completed build-loop exercise |
| `D6-client-feedback-response.md` | D6 — Client feedback response | Timed gate | Client pushback communication |
| `D7-validation-plan.md` | D7 — Validation plan | Timed gate | Both D4 specs |
| `D8-reflection.md` | D8 — Reflection | Timed gate | Your own experience |
| `D9-self-spec-build-loop.md` | D9 — Self-spec build-loop reflection | Timed gate | One D4 spec + Claude Code output |

## Suggested order during the timed gate

| Order | Deliverable | Reason |
|---|---|---|
| 1 | D1, D2, D3 (revised) | Foundations — everything else depends on these |
| 2 | D4 (both specs) | Heaviest deliverable; do it while thinking is sharpest |
| 3 | D6 (client response) | You have had the morning to process the pushback |
| 4 | D5 (build-loop memo) | Substance already done earlier in the week |
| 5 | D7 (validation plan) | Flows directly from the D4 specs |
| 6 | D9 (self-spec reflection) | Run the spec through Claude Code first, then write |
| 7 | D8 (reflection) | Write last — it benefits from seeing the full picture |
