# Phase 5: Agent Purpose Document — Design the Agent

**Goal:** Write a precise, buildable specification for your agent that defines purpose, scope, decisions, autonomy, and failure modes.

**Input:** Cognitive Load Map + Delegation Suitability Matrix + Volume × Value Analysis.

---

## Agent Purpose Document Structure

An Agent Purpose Document is **not** a feature spec or architecture document. It answers:
- **What is the agent for?** (purpose, not what it does)
- **What does it decide autonomously vs. what does it escalate?** (autonomy matrix)
- **How do we know it succeeded?** (KPIs)
- **What can go wrong, and how do we recover?** (failure modes)
- **What data does it need and where does it act?** (system/data requirements)

---

## 1. Agent Identity & Purpose

Write a single-paragraph purpose statement that captures **intent**, not features:

**Good:**
> The buddy-matching agent reduces time Priya spends surfacing candidate mentors by 80%. The agent queries HR data to rank potential buddies on team composition, availability, and experience level, then surfaces top 3 candidates with reasoning to Priya, who makes the final match. This accelerates onboarding velocity while keeping human judgment on the match itself.

**Bad:**
> The buddy-matching agent queries the HR system and surfaces candidate mentors.

(Why bad: doesn't clarify purpose, just restates a feature)

---

### Key Elements of Purpose

- **Who benefits?** (e.g., Priya)
- **What problem does it solve?** (e.g., time-consuming manual candidate search)
- **What outcome does it unlock?** (e.g., faster onboarding, better matches)
- **What does it do?** (e.g., query data, rank, surface candidates)
- **What does the human do?** (e.g., review and decide)

---

## 2. Scope: What The Agent Handles

Define boundaries clearly:

**In Scope:**
- New-hire buddy assignment only (not existing-employee mentor requests)
- Matching within the hiring department + adjacent departments
- Availability defined as: not assigned to > 3 ongoing buddies, not on leave this quarter
- Experience defined as: tenure in role > 6 months + prior buddy assignment (preferred)

**Out of Scope:**
- Emergency/same-day matches (these bypass normal process and go to manager)
- Cross-office matches (London site has no data on Dublin team; would require manual review)
- Rehires (past buddy relationships complicate logic; Priya reviews all rehires manually)
- Determining buddy role (agent assumes "mentor" role provided by hiring manager; doesn't infer role)

**Escalation Triggers:**
- < 3 qualified candidates found (insufficient choice) → escalate to Priya with available candidates
- Tied candidates with identical scores → escalate with tie-breaking criteria to Priya
- New hire marked as "high visibility" or "VIP" → automatic escalation to Priya (executive hires handled specially)

---

## 3. Autonomy Matrix: Who Decides What

This is the most critical section. For each decision point in the cognitive zones, specify:

| Decision Point | Who Decides | Threshold/Criteria | Escalation Condition |
|---|---|---|---|
| **Is new hire eligible for buddy match?** | Agent (rule) | Hire status = "onboarding"; start date within 2 weeks | Status ≠ "onboarding" OR start date > 2 weeks away → skip (no match needed yet) |
| **Which team(s) to search for buddies?** | Agent (rule) | Hiring department + adjacent departments per org chart | Department not in system OR org chart stale > 60 days → escalate |
| **Who qualifies as buddy candidate?** | Agent (rule-based) | Tenure > 6 months, availability check (see criteria), no conflicts | Criteria ambiguous (e.g., "tenure in role" vs "tenure at company") → escalate to Priya |
| **How to rank qualified candidates?** | Agent (scoring) | Scoring formula: (team_diversity +0.3) × (availability +0.2) × (experience +0.5) | Candidates tied on score with difference < 5% → escalate with reasoning to Priya |
| **How many candidates to surface?** | Agent (fixed) | Top 3, always | [No escalation; rule is fixed] |
| **Is final match valid?** | Human (Priya) | Subjective: manager relationship, team dynamics, growth opportunity | [Priya reviews top 3; makes match or rejects all] |
| **If match rejects all 3 candidates, what happens?** | Human (Priya) | Priya manually searches or asks manager for suggestions | [Manual process outside agent scope] |

---

## 4. Activity Catalog: What The Agent Actually Does

List every action the agent takes in the process:

1. **Intake**: Receive new-hire record (Workday event trigger or daily batch check)
2. **Eligibility Check**: Query Workday for hire status, start date, department, manager; filter out ineligible hires
3. **Candidate Search**: Query HR system for all employees in eligible departments with tenure > 6 months
4. **Availability Verification**: Check each candidate's current buddy assignments + leave calendar; filter to available candidates
5. **Ranking**: Score each candidate using formula; sort by score descending
6. **Reasoning Generation**: For top 3 candidates, generate explanation (team diversity match, availability, experience fit)
7. **Surface to Priya**: Create entry in queue or send email with top 3 candidates + reasoning + link to hire record
8. **Receive Priya's Decision**: Priya clicks "Assign to [Candidate Name]" in queue or replies to email
9. **Execute Assignment**: Write buddy assignment + match date to Workday + notify candidate (auto-email template) + create calendar reminder for 30-day check-in
10. **Log & Document**: Record decision + reasoning + timestamp in audit log (for later analysis of "did the agent's recommendation match Priya's choice?")

---

## 5. KPIs: How We Measure Success

Define success at three levels:

### Operational KPIs (Does it work as designed?)
- **Average time to surface candidates:** < 5 minutes from eligibility check
- **Candidate availability accuracy:** > 99% of surfaced candidates actually available (Priya doesn't pick someone on leave)
- **System uptime:** Agent accessible ≥ 99.5% of business hours
- **False escalations:** < 2 per week (escalations where Priya expected agent to handle it)
- **Missed cases:** < 2% of new hires (hires where agent fails to trigger and Priya catches manually)

### Outcome KPIs (Does it create value?)
- **Time saved per match:** Priya spends < 5 minutes choosing from top 3 (vs. ~30 min manual search)
- **Adoption:** Priya uses agent-recommended match on ≥ 80% of cases (rejection rate < 20%)
- **Quality of matches:** 30-day check-in feedback score ≥ 7/10 (manager + new hire rate quality of buddy match)
- **Time to first buddy interaction:** Average time from assignment to first meeting < 3 business days

### Business KPIs (Does it move the needle?)
- **Onboarding velocity:** Days from hire creation to "buddy engaged" decreases 20% (from ~5 days to ~4 days)
- **Retention:** First-year retention rate for cohorts with AI-matched buddies vs. manually matched (baseline: 85%; target: 88%)

---

## 6. Failure Modes & Recovery

For each major failure scenario, describe detection and recovery:

| Failure Mode | Detection | Impact | Recovery |
|---|---|---|---|
| **Agent surfaces unavailable buddy** | Candidate on leave; Priya notices in email | Low: 1 manual filter, ~2 min | Manual check; agent learns to improve leave-calendar sync |
| **Agent escalates unnecessarily** | Flags low-priority cases as ties or exceptions | Medium: creates false work for Priya | Tune scoring thresholds; reduce False Positive escalation rate |
| **Agent assigns same buddy twice** | Candidate receives 2 buddy assignments on same day | High: conflict; manager confusion | Implement pessimistic locking in Workday write; verify candidate's current count before write |
| **Scoring formula produces unintuitive ranking** | Priya rejects top 3 and picks 4th candidate | Medium: undermines trust | Monthly review of rejected candidates; refine scoring weights |
| **New hire not found in Workday** | Agent filters out legitimate hire (status field mismatch or timing lag) | High: hire never gets buddy | Implement retry logic; escalate if not found after 24 hours; notify Priya manually |
| **Agent sends duplicate email to candidate** | Candidate receives notification twice (system glitch + retry) | Low: minor confusion | Implement idempotency key in notification; deduplicate on email address + timestamp |
| **Org chart stale; agents surface outdated teams** | Priya notices candidates from closed team | Medium: wasted cycles | Manual org chart refresh; implement stale-data warning in agent logic (flag if org chart > 90 days old) |

---

## 7. System & Data Requirements

### Data Inputs

| Data Element | Source System | Freshness | Quality Notes |
|---|---|---|---|
| New-hire record (name, dept, start date, manager) | Workday | Real-time (event trigger) | Vetted by HR; 99%+ completeness |
| Employee directory (ID, name, dept, tenure) | HR system / Workday | Daily refresh (0200 UTC) | Accurate to ±1 day; includes contractors/FTEs |
| Buddy assignment history | Workday (custom field) | Real-time | Maintained by Priya; ~2% manual errors annually |
| Leave calendar | Workday | Daily refresh (0200 UTC) | Managed by employees; ~10% incomplete (no PTO submitted yet) |
| Org chart / department structure | ServiceNow or manual | Manual update (ad-hoc) | **Risk:** Often stale; delays when hiring manager changes |
| Team composition (how many buddies per team) | Workday query (count buddies per manager) | Real-time | Derived; very reliable |

### System Actions

| Action | Target System | API/Method | Prerequisites | Rollback |
|---|---|---|---|---|
| Query new hires | Workday | REST API (hrh-list-hires) | OAuth token + permissions | Read-only; no rollback needed |
| Query employees + availability | Workday | REST API (emp-search) + leave-calendar join | OAuth token | Read-only; no rollback needed |
| Write buddy assignment | Workday | REST API (emp-update-custom-field) | OAuth token + write permissions + hire record ID + candidate ID | Delete assignment within 24h or notify Priya to revert |
| Send notification email | Outlook | Microsoft Graph API (send email) | OAuth token + template ID | Retract email within 2 hours (if supported); notify recipient of correction |
| Create calendar reminder | Outlook | Graph API (calendar event) | OAuth token | Delete event within 24h |
| Log decision + reasoning | Internal audit table | Direct DB write or API | DB credentials | Delete log entry within 24h (for corrections) |

---

## 8. Escalation & Human Oversight

Define exactly when the human is called in:

**Automatic Escalation (Agent → Queue for Priya):**
- < 3 qualified candidates found
- Top candidates tied in score (difference < 5%)
- New hire marked "VIP" or "high visibility"
- Candidate's current buddy count ≥ 3 (fully booked)
- Leave calendar missing or inconsistent for > 30% of candidates

**Periodic Human Review (Metrics-Driven):**
- Weekly: Rejection rate > 20% (Priya rejecting agent's top 3)
- Weekly: Time-to-match > 5 minutes (system performance issue)
- Monthly: Scoring formula review (see which candidates Priya picks when agent offers alternatives)
- Monthly: Quality feedback (30-day check-in scores; flag low-quality matches)

**On-Call Escalation (If Failure Detected):**
- Agent crashes or is unreachable for > 5 minutes → notify Priya; fallback to manual process
- Duplicate assignment or data corruption → rollback + alert to engineering team + escalate to Priya

---

## 9. Assumptions & Confidence Levels

Record assumptions that, if wrong, would change the design:

| Assumption | Confidence | Impact if Wrong | Verification Plan |
|---|---|---|---|
| Priya can review & decide on top 3 in < 5 minutes | High | If takes 15+ min, ROI drops 50% | Pilot with Priya; measure actual time |
| Leave calendar is 90%+ complete | Medium | If only 70% populated, false availability ~15% → escalations spike | Audit leave data for Jan–Mar; assess coverage |
| Buddy assignments are 1:1 (each buddy has ≤ 3 concurrent matches) | Medium | If some buddies do 5+ matches, data is wrong → agent surfaces overloaded candidates | Priya to confirm max capacity rule |
| All qualifying employees are in Workday | High | If 10%+ are in legacy systems, agent misses them | HR audit of employee directory vs. actual headcount |
| Manager always specifies "new hire" role (vs. "contractor" or "secondment") | Low | If role ambiguous, agent might miss hiring context | Check hire form data quality; may need to ask manager to clarify |
| Org chart is accessible via Workday API | Medium | If not, agent must use manual list maintained by HR | Verify API access + schema with IT; establish data refresh SLA |

---

## 10. Build Prompt for Claude Code

When you're ready to hand this to an AI for implementation, use this build prompt:

```
I have an Agent Purpose Document for a buddy-matching assistant. 
Please read it carefully and tell me:

1. What can you build confidently with the APIs and systems listed?
2. What do you need me to clarify before building the rest?
3. Build the parts you are confident about (include comments on what's blocked).

Focus on:
- What doesn't make sense in the autonomy matrix?
- Where is delegation ambiguous (should this be agent vs. human)?
- What's missing in the system requirements (APIs, schemas, authentication)?
- What failure modes are you unsure how to implement?
```

Then review Claude's output for:
- **What it built**: Is it faithful to your Purpose Document or did it drift toward "fully agentic"?
- **What it asked**: Each question reveals a gap in your document; revise.
- **What it can't build**: Each gap is likely a delegation boundary issue; clarify in the document.

---

## Output: Agent Purpose Document Template

```markdown
# Agent Purpose Document: [Agent Name]

## 1. Purpose
[Single-paragraph purpose statement]

## 2. Scope
- **In Scope:** [Bullet list]
- **Out of Scope:** [Bullet list]
- **Escalation Triggers:** [Bullet list]

## 3. Autonomy Matrix
[Table: Decision Point | Who Decides | Criteria | Escalation Condition]

## 4. Activity Catalog
1. [Action with inputs/outputs]
2. [Action with inputs/outputs]
...

## 5. KPIs
- **Operational:** [Metrics]
- **Outcome:** [Metrics]
- **Business:** [Metrics]

## 6. Failure Modes & Recovery
[Table: Failure Mode | Detection | Impact | Recovery]

## 7. System & Data Requirements
- **Data Inputs:** [Table]
- **System Actions:** [Table]

## 8. Escalation & Human Oversight
[Describe automatic, periodic, and on-call escalation]

## 9. Assumptions & Confidence
[Table of assumptions with confidence and impact]

## 10. Notes for Implementation
[Any clarifications for the build team]
```

---

## Refinement Prompts: Commands Used to Improve This Deliverable

The initial draft of DELIVERABLE-5 was technically complete but written primarily for a technical audience. The escalation workflow diagrams were simple text arrows (↓) with no branch logic shown. The following prompts improved clarity for a mixed audience and made the diagrams testable.

---

### Prompt 1: Add a plain-English introduction

```
Add a "The Problem This Agent Solves" section at the very top of the document,
before Section 1. Write it in plain English for a non-technical reader who has
not read the discovery or delegation documents. It should answer:
- What problem exists today (specific, with numbers if available)
- What the agent does about it
- What humans still control and why
Keep it to 3–4 short paragraphs. No jargon.
```

**What this fixed:** Non-technical reviewers (HR leadership, compliance) can now understand the agent's purpose without reading 10 sections. The plain-English section also served as the verbal 5-minute summary anchor.

---

### Prompt 2: Rewrite escalation diagrams to show branch logic

```
The escalation workflow diagrams in Section 8 use simple downward arrows (↓) with no
branch logic. Rewrite each diagram as a box-flow using:

- TRIGGER: [condition] as the entry point
- Labeled boxes for Agent steps and Human steps
- Branch paths using ├── for intermediate branches and └── for the final path
- Clear labels: [Agent] and [Human] before each action
- A timeout/fallback path shown as a separate branch

The reader should be able to trace exactly what happens in each scenario
without reading the surrounding text.
```

**What this fixed:** Replaced 4 flat arrow-chain diagrams with branching box-flow diagrams that show TRIGGER → Agent action → branch condition → Human action, with escalation and timeout paths visible as separate branches. The diagrams are now directly testable against the code.

---

### Prompt 3: Review section headers for accessibility

```
Review all section headers in this document. Rename any that:
- Use technical jargon a non-technical reader would not understand
- Are vague (e.g., "Scope" — scope of what?)
- Don't tell the reader what they are about to learn

Replace with headers that state the content, not just the category.
```

**What this fixed:** Changed "Scope" → "What This Agent Handles (and What It Doesn't)", "Autonomy Matrix" → "Who Decides What: The Autonomy Matrix", "Activity Catalog" → "Activity Catalog: What the Agent Does, Step by Step".

---

### Prompt 4: Check for spec claims the build loop might invalidate

```
Review Sections 3 (Autonomy Matrix) and 8 (Escalation Workflows) for claims
that assume system capabilities not yet confirmed:
- SLA claims that depend on polling frequency
- Escalation triggers that assume specific API responses
- KPIs that assume data freshness levels not yet verified

Flag each claim with [ASSUMPTION — verify before build] and state what would
need to be true for the claim to hold.
```

**Why this matters:** The build loop (Phase 6) identified that Activity 5's daily I-9 polling was insufficient for the stated 15-minute SLA. Doing this check before the build loop would have caught it earlier.

---

## Next Step

Once your Agent Purpose Document is draft-ready, move to **Phase 6: Build Loop & Refinement** or **Phase 7: System/Data Inventory** (if pursuing a formal submission).
