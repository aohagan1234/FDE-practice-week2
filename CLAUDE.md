# CLAUDE.md — Coordination Orchestrator Assessment

**Project:** Week 2 ATX Assessment — HR Onboarding Coordination  
**Scenario:** KTB-1-109 / Scenario 1 (enriched) — Aldridge & Sykes  
**Methodology:** 7-Phase Agentic Transformation (ATX)

---

## What this project is

**Plain-English summary:** A 3-person HR team at a professional services firm (Aldridge & Sykes, Manchester) spends 550+ hours a year manually chasing task completion across 5 disconnected systems every time a new employee joins. This project analyses which parts of that work an autonomous agent should handle, builds the specification for that agent, and implements a tested Python prototype.

The analysis uses the ATX (Agentic Transformation) methodology — a structured 7-phase process for deciding where to deploy autonomous agents and where not to. The conclusion is that automation is justified primarily on compliance risk reduction (one avoided I-9 penalty at $2,507 covers the build cost) rather than pure time savings, and that roughly 50% of the coordination work can be fully automated with the remaining 50% split between agent-led-with-oversight and human-only tasks.

The output is not a slide deck. It is a set of working artefacts: a scored analysis, a buildable specification, a tested Python implementation, and a system inventory that addresses real integration constraints.

---

## File structure

```
/
├── DELIVERABLE-1-DISCOVERY-QUESTIONS.md   # Phase 1: design-changing questions + assumptions
├── DELIVERABLE-2-COGNITIVE-LOAD-MAP.md    # Phase 2: JtDs, micro-tasks, zones, breakpoints
├── DELIVERABLE-3-DELEGATION-MATRIX.md     # Phase 3: suitability scores + delegation archetypes
├── DELIVERABLE-4-VOLUME-VALUE.md          # Phase 4: V×V analysis, primary target, ROI
├── DELIVERABLE-5-AGENT-PURPOSE.md         # Phase 5: full agent spec (revised after build loop)
├── DELIVERABLE-6-SYSTEM-DATA-INVENTORY.md # Phase 7: system table, data dict, risks, Saba LMS
├── WEEK2-ASSESSMENT-CONSOLIDATED.md       # Gate 2 submission: executive summary + all phases
├── DELIVERABLES-README.md                 # Navigation guide
│
├── coordination_orchestrator/             # Phase 6 build output
│   ├── models.py                          # Data models
│   ├── config.py                          # Routing tables, thresholds, IT matrix
│   ├── api_clients.py                     # Stubs for 5 source systems (replace NotImplementedError)
│   ├── audit.py                           # Structured audit logger
│   ├── orchestrator.py                    # All 9 activities + poll loop
│   ├── main.py                            # Entry point
│   └── tests/
│       └── test_orchestrator.py           # 37 tests; run with: pytest tests/
│
├── Resources/                             # ATX methodology reference materials
├── Week2_Docs/                            # Scenario briefs, enriched scenarios, artefacts
│
└── PHASE-1 through PHASE-7 *.md           # Methodology guides (not deliverables)
```

---

## How Claude was used in this project

### Phase 1 — Discovery Questions

Claude read the Week 1 spec (KTB-1-109) and enriched scenario (Scenario 1, Aldridge & Sykes) to identify assumptions that would materially change the agent design. The prompt was: *"What do you not know that would change the delegation architecture if you did?"* — not *"list some discovery questions."*

Claude identified the API availability risk (LOW confidence for all 6 systems) and the compliance matrix staleness risk as the two assumptions most likely to collapse the ROI case. Both appear as LOW-confidence items in DELIVERABLE-1.

### Phase 2 — Cognitive Load Map

Claude decomposed all 4 work streams into Jobs to be Done, then into cognitive zones and micro-tasks using a structured table format (Input / Decision or Execution? / Output / Data Source / Pause Points). The zone framing — rather than task-list framing — came from prompting Claude to identify *why* tasks cluster together cognitively, not just what the tasks are.

The 8 control-handoff breakpoints were identified by asking: *"Where does control transfer between agent, human, and system?"* — and answering with detection method, not just condition.

### Phase 3 — Delegation Suitability Matrix

Claude scored all 9 task clusters on 5 dimensions using explicit rubrics. The anti-pattern check (*"Is everything fully agentic?"*) was included by asking Claude to identify where it would be tempted to over-automate, then justify the boundary. Hold decisions (Cluster 8) and hire-type classification (Cluster 2) scored low on purpose, not by accident.

### Phase 4 — Volume × Value Analysis

Claude calculated volume per person per year (not per team), cross-checked against the enriched scenario's handling times, and was explicit when ROI was marginal. The honest conclusion — "no cluster scores ≥15; ROI payback is 18–24 months" — was preserved rather than massaged.

### Phase 5 — Agent Purpose Document

Claude drafted the full 10-section spec. Sections 3 (Autonomy Matrix) and 8 (Escalation Workflows) were generated with explicit decision tables rather than narrative, to make them testable.

### Phase 6 — Build Loop

Claude reviewed the Agent Purpose Document as if asked to implement it, answering three questions:
1. What can be built confidently?
2. What needs clarification?
3. Build the confident parts (code/pseudocode).

Six gaps were identified. The most critical: Activity 5 specified daily I-9 polling (insufficient to meet the 15-minute SLA), and there was no idempotency rule for escalations (would produce 12 duplicate alerts per 24h). The spec was revised and a full Python implementation was built, tested with 37 passing tests.

**Key build-loop output:** `coordination_orchestrator/orchestrator.py` — all 9 activities implemented; run `pytest tests/` to verify.

### Phase 7 — System/Data Inventory

Claude identified that DELIVERABLE-5 incorrectly described Saba LMS as "SOAP API (legacy)" when the enriched scenario explicitly states it has **no API**. Saba LMS uses a weekly SFTP batch file export. This changes: detection latency (2h → 7 days for LMS tasks), reminder logic, the 4-hour SLA claim, and the LMSClient implementation in the code.

DELIVERABLE-6 was created to address this with a dedicated Saba LMS section and a three-state handling model for batch-sourced task data.

---

## Key decisions and rationale

These are the non-obvious choices in the design — the places where a reasonable person might expect a different answer. The "why" behind each one matters more than the decision itself, because if the underlying constraints change, the decision should be revisited.

### Why the ROI case is honest rather than flattering

Volume is genuinely low at Aldridge & Sykes: 73 hires/person/year = ~5.5/month. At that rate, Year 1 ROI is negative. This was preserved in DELIVERABLE-4 rather than corrected to look better. The agent is justified on compliance de-risking (one prevented I-9 violation at $2,507 penalty covers build cost) and scalability, not pure time savings.

### Why hold decisions are Human Only

Cluster 8 scored 2.0/5.0 on suitability. Hold = irreversible employment action with legal implications. The agent detects hold triggers and escalates; it does not write `hire.status = ON_HOLD`. This is Guardrail #1 in the spec and is non-negotiable.

### Why I-9 monitoring is Fully Agentic despite CRITICAL risk

Counter-intuitive: the highest-risk item is the most appropriate for full automation. I-9 escalation is deterministic (day 2, day 3 — no judgment), non-deferrable (federal mandate), and is exactly where human memory fails under load. An agent that monitors every 2 hours is strictly better than a human who may forget during a busy week.

### Why Saba LMS batch-only changes the SLA claim

The spec's "≥80% of overdue tasks detected within 4 hours" is unachievable for LMS-sourced tasks. Rather than keep the claim and quietly fail, DELIVERABLE-6 corrects the SLA to reflect the 7-day batch window for LMS tasks. Honesty about system constraints is preferable to a spec that passes review and fails in production.

### Why buddy matching is Agent-Led + Oversight rather than Fully Agentic

Team dynamics judgment cannot be codified. The ranking algorithm is deterministic; the final selection from the ranked list is not. HR Ops approves the agent's top-3 proposal. This is Cluster 4's archetype and matches the enriched scenario's context: Tom Reeves' buddy assignment was overridden (Artefact 1.2 hidden column: "Paired with Sarah J (peer level), not Anna (rule says senior pair)").

---

## How to run the implementation

```bash
cd coordination_orchestrator

# Run all tests
pytest tests/ -v

# Start the orchestrator (requires API stubs implemented in api_clients.py)
python main.py
```

Before deploying: replace every `raise NotImplementedError` in `api_clients.py` with real HTTP calls for each source system. The Saba LMS client must be replaced with an SFTP file reader — not an HTTP client — per DELIVERABLE-6 Section 5.

---

## Assumptions that would change the design

The design is only as good as its assumptions. The ones below are rated LOW or MEDIUM confidence — meaning we don't have evidence to confirm them yet. They are the first things to validate with Priya (HR Ops Lead) and IT before committing to build:

| Assumption | Confidence | What changes if wrong |
|---|---|---|
| Saba LMS batch delivers reliably every Sunday | **LOW** | Batch-only design becomes untenable; must explore Saba API licence or manual sync |
| Workday updated daily (not just end-of-week) | **MEDIUM** | Reminder timing degrades; data_freshness handling becomes critical |
| ServiceNow routing rules are correct for all role types | **MEDIUM** | IT provisioning requests go to wrong queue; agent detects delay but can't fix routing |
| Compliance training matrix in SharePoint is current | **LOW** — Artefact 1.3 shows outdated footnote | Wrong track assigned; audit exposure |
| API access available for Workday, SNOW, Graph | **MEDIUM** | Without APIs, agent cannot function; fallback to batch-only for all systems |

---

## What this project does not cover

- **Buddy matching as a standalone agent (Agent 2 / Proposal Router):** Scoped out. DELIVERABLE-4 recommends building it after Agent 1 proves value. It would require structured HR Ops approval workflow infrastructure not present at Aldridge & Sykes today.
- **Edge-case resolution work stream:** The 4th work stream (~30–50 cases/year; ~4h/case) includes contractor-to-FTE conversions, frozen records, and right-to-work checks. Volume is low and judgment is very high (Cluster 2 territory). Not in scope for the Coordination Orchestrator.
- **Gate 2 new scenario:** This assessment is practice. Gate 2 will give a sealed scenario. The methodology here is reusable; the artefacts are not directly transferable.

---

## Contact and methodology references

- **Methodology guides:** PHASE-1 through PHASE-7 .md files in root
- **Enriched scenario brief:** `Week2_Docs/enriched_scenarios.md` (Scenario 1 — Aldridge & Sykes)
- **ATX concepts:** `Resources/atx-concepts.md`
- **Agent mapping reference:** `Resources/atx-agent-mapping.md`
