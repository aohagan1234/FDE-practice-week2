# Live Round Prep — Gate 2: Apex Distribution Ltd

**Format:** ~10 minutes. Coach plays Sarah Whitmore (COO). May be 1:1 or small group of 3.  
**What's being tested:** Can you ask questions whose answers materially change your design? Can you detect when you're being deflected?

---

## Opening move (30 seconds)

> "I've reviewed the scenario and the artefacts in detail — including the batch CSV files. I have three architecture-level questions before we could go to build, and two things I found in your data I want to flag directly. Can we start there?"

**Why this framing works:** It signals you've done the work (CSV detail), positions your questions as pre-build blockers not generic curiosity, and gives Sarah a reason to engage rather than deflect.

---

## Question priority — if time runs out, lead these

| Priority | Question | Why it's first |
|---|---|---|
| **1st** | Q1 — Driver app API surface | Changes Phase 1 architecture entirely. GPS vs MSG vs no API = three different agents. |
| **2nd** | Q3 — Sandra credit audit gap | Evidence bomb — visible in the CSV data, not in the brief. Shows you read the artefacts. Compliance risk Sarah may not want to acknowledge. |
| **3rd** | Q2 — CRM status freshness | Changes ETA accuracy claim and staleness disclaimer. "I think it's real-time" is a guess — push for a number. |
| **4th** | Q5 — Fuel surcharge anomaly | Second evidence bomb — three T3 invoices on R-008 with different FUEL_PCT values. Either a billing error or an undocumented per-contract rate. Either answer changes Phase 2. |
| **5th** | Q7 — Why the chatbot failed | Changes what guardrails the ETA agent needs. Critical for not repeating the same failure. |

**If you only get 3 questions:** Q1, Q3, Q5. These are the only ones Sarah can't answer by guessing.

---

## Q1 — Driver app API (lead question)

> "When the ETA agent needs a driver's current location, can it query the driver app programmatically for GPS coordinates — via an API? Or is the only available channel a message asking the driver to reply with their location?"

**If GPS API exists:** Agent calculates ETA in <30 sec without driver involvement. 2-minute wait protocol in the spec becomes unnecessary. Response time target improves.

**If message-only:** 2-min wait + fallback window is the correct design. Keep spec as is.

**If no API at all:** Agent becomes a CRM lookup tool only — no driver contact, no tight ETA. Significant capability reduction. Phase 1 scope changes.

---

## Q3 — Sandra credit audit gap (evidence bomb)

> "In the billing email thread, I can see Sandra applied a £170 goodwill credit to Hayes & Sons — but the internal note says there's no entry in the credits audit log. I checked your APEX_CREDITS export and that credit isn't in there. Is this a known gap — do manual overrides routinely bypass the audit log — or was this off-policy?"

**Why this lands:** You're citing a specific artefact + a specific CSV file. Sarah cannot dismiss it as a generic question.

**If manual overrides routinely bypass the export:** APEX_CREDITS is an incomplete record. Any Phase 2 billing agent using it to check dispute resolution will misidentify open disputes. Flag the compliance exposure directly: credits applied without audit trail.

**If it's off-policy (Sandra shouldn't have done it):** The audit trail is theoretically intact. Phase 2 agent can enforce the structured path — makes the non-audited path structurally unavailable.

---

## Q5 — Fuel surcharge anomaly (evidence bomb)

> "In the fuel surcharge export, route R-008 has three invoices all on tier T3 — but the fuel percentages are different: 11.97%, 9.37%, and 12.00%. Is the percentage within a tier a fixed rate, or does it vary by customer contract? Hayes & Sons has three open fuel surcharge disputes — if there's a calculation error on R-008, that could explain the pattern."

**Why this lands:** Connects a data anomaly directly to an open dispute pattern. Forces Sarah to either explain the rate logic or acknowledge she doesn't know.

**If fixed per tier:** The 9.37% is a billing error. Hayes & Sons may have been overcharged or undercharged. Changes Phase 2 dispute resolution logic.

**If contract-specific within a tier:** The rate card is missing from all 7 batch exports. Phase 2 agent cannot verify surcharge accuracy without a data source that doesn't exist yet.

---

## Sarah's likely challenge questions — your answers

### "Why ETA first? The billing mess is the real problem."

> "W4 has stronger compliance value — I agree. But it has a hard constraint: Aurum is batch-only, 24-hour lag, schema changes without notice. That's exactly what broke the RPA project. Building a billing agent before W2 has proven value means asking you to fund a higher-risk project before you've seen the approach work. W2 is 6 weeks to production, 2.8 FTE saved, no Aurum dependency. Once it's live and Sarah has seen it hold up, the case for W4 is much easier to make — and you'll have a working integration pattern to build on."

### "How is this different from the chatbot that failed?"

*(Buy time by asking the diagnostic question first)*

> "Can I ask — do you know what specifically customers hated about it? Was it the bot format, the quality of the answers, or that it couldn't pull live data?"

- **If bot format:** "The ETA agent is invisible. It replies via the customer's existing SMS channel as 'Apex Customer Service' — no chatbot persona, no new interface."
- **If wrong answers:** "That's a data quality problem. The agent's design is built around that risk — CRM freshness constraint is explicit, and the fallback window is the primary path when driver data is uncertain, not a failure mode."
- **If couldn't pull live data:** "The agent's only hard dependency is the Salesforce REST API — which you've confirmed is available. If that integration is unreliable, the agent has the same problem, which is why integration testing in the canary phase is non-negotiable."

### "What happens when Aurum breaks your billing agent?"

> "The same thing that broke the RPA — a column rename silently corrupts output. The Phase 2 design addresses this with schema validation as a first-class feature, not a bolt-on: the agent checks expected column names against the batch file before parsing. If validation fails, it halts and alerts before producing any output. It doesn't process bad data quietly. That's the core difference from the RPA."

---

## Detection signals — when Sarah is deflecting

| What she says | What it means | How to push |
|---|---|---|
| "I'd have to check with IT" (Q1, Q6) | API surface is genuinely unknown — HIGH risk | *"If it turned out there was no driver app API, would you be willing to fund exposing one before we build? It's a Phase 1 prerequisite."* |
| "I think it's real-time" (Q2) | She's guessing — don't accept it | *"Can you put a number on it — is it seconds, minutes, or longer? It changes the accuracy claim in the agent spec."* |
| "That shouldn't have happened" (Q3) | Off-policy, but she doesn't want to dwell | *"Is this the first time you've seen this, or does it happen regularly with manual credits? It affects whether the audit trail is reliable enough to build on."* |
| "It varies" (Q8 — peak volume) | Deflection on a number she should know | *"What's the highest single day you've ever seen? Even a rough figure helps size the SLA test."* |
| "The chatbot was just bad" (Q7) | Avoiding the specifics | *"If you had to choose one reason — wrong answers, wrong format, or couldn't pull live data — which was the biggest complaint?"* |

---

## Things not to do

- **Don't lead with ROI numbers.** Sarah is sceptical of consultants. The 2.8 FTE / £140K/month figure is in the deliverables; let her ask, then confirm.
- **Don't ask about W3 (dispatch adjustments) unless she raises it.** "Limited API surface" is a known unknown. Q6 is Tier 2 — only worth asking if time allows.
- **Don't defend the chatbot comparison defensively.** Ask what failed first, then tailor the answer. Defending before knowing the root cause sounds like you're papering over the risk.
- **Don't say "the agent will handle everything."** The delegation matrix explicitly doesn't. If she pushes on scope, point to Section 2.3 of D4 — Human-led tasks are named precisely to avoid overpromising.

---

## Close (30 seconds)

> "The three things I'd need from you before build starts: confirmation on the driver app API surface, the CRM status freshness number, and clarity on whether the credits audit trail gap is systemic or a one-off. Those three answers let us lock the Phase 1 spec. Everything else is Phase 2 — and we don't need it before the pilot."

---

## Quick-reference — key facts to have at hand

| Fact | Number |
|---|---|
| ETA inquiries per day | 400 |
| Avg handling time | 4 min |
| Daily person-hours on ETA | 26.7 hrs |
| FTE freed (Phase 1) | 2.8 FTE |
| Redeployment value | ~£140K/month |
| ROI payback | 1–2 months |
| Phase 1 build timeline | 4 weeks build + 2 weeks testing |
| Driver response timeout | 2 minutes |
| Fallback window | 13:00–17:00 (4-hour) |
| Cache TTL (deduplication) | 1 hour |
| Resolution rate target | >80% autonomous |
| Response time target | <5 min (P50) |
| Aurum batch lag | 24 hours (T-1); recon file T-2 |
| Aurum schema change notice | None — schema changes without warning |
| SOP last updated | October 2023 (DispatchHub retired Oct 2024 — SOP is stale) |
