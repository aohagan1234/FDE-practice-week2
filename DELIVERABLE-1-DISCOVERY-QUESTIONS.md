# Deliverable 1: Discovery Questions — Probing the Lived Work

**Organisation:** Aldridge & Sykes, Manchester — professional services firm (1,200 employees)  
**Team:** 3-person HR Ops team managing 220+ new hires per year  
**The problem:** HR Ops spends over 550 hours per year chasing task completion across 5 disconnected systems. That's roughly a quarter of each person's working year spent on coordination that could, in principle, be automated.

---

## Why SOP Questions Fail

A process audit asks: *"What does the SOP say happens?"*  
A lived-work discovery asks: *"What do you actually open, click, check, and decide — and where does the SOP stop matching reality?"*

The gap between those two questions is where agents break.

The gap is where Priya has a personal spreadsheet more accurate than Workday. Where I-9 "In Progress" turns out to mean "started the form but not submitted." Where hold decisions happen on WhatsApp because email gets buried. Where IT provisioning that matters gets resolved by emailing Mark directly, and the ServiceNow ticket gets raised afterwards for the audit trail. Where a second tab stays permanently open to a legacy system from 2014 because it has the contractor history that never fully migrated.

These questions are designed to find that gap. They ask for stories, not procedures. Every answer that diverges from the SOP is a design implication.

---

## Situation Summary

| Fact | Detail |
|---|---|
| Hires per year | 220+ (roughly 4–5 new starts per week across the team) |
| Coordination time | ~2.5 hours per hire on chasing, checking, and reminding |
| Team total per year | 550+ hours — a significant slice of a 3-person team's capacity |
| Tasks per hire | 40 tasks across pre-start, post-start, and ongoing categories |
| Systems (official) | Workday, ServiceNow, Saba LMS, SharePoint, Outlook |
| Judgment required | ~15% of tasks; 85% are rule-based |
| Key compliance risk | I-9 verification: federal penalty of up to $2,507 per violation if not complete within 3 days of start |

---

## Part 1: The Discovery Questions

Six questions designed to surface what SOP interviews miss: the workarounds, the screen-switching, the instinct calls, the legacy tabs, and the moments where the real answer isn't in any official system.

> **Simulation note:** The answers labelled "The COO's answer" below were generated through a structured role-play exercise in which an AI simulated a senior stakeholder's responses. The actual primary stakeholder at Aldridge & Sykes is **Priya Aggarwal (HR Ops Lead)** — not a COO. Several details in the simulated answers are **not confirmed by the enriched scenario brief** and must be validated with Priya before being treated as real design inputs:
>
> - iPhone Notes app as I-9 tracker — **not in scenario**
> - Legacy HR system from 2014 — **not in scenario** (scenario lists 5 systems: Workday, ServiceNow, Saba LMS, SharePoint, Outlook)
> - "Mark in IT" as informal contact — **not in scenario**
> - WhatsApp for urgent escalations — **not in scenario**
> - Connections HR recruiter mislabelling hire_type — **not in scenario**
> - Strategy/Finance buddy exclusion rule — **not in scenario**
>
> Details that **are** confirmed in the enriched scenario: Priya's Excel tracker on OneDrive (Artefact 1.2), the TEMP-EXT hire type retired Q1 2024 (Artefact 1.3), and CFO (not COO) involvement. The questions themselves are valid discovery questions. The simulated answers illustrate the *type* of detail discovery questions should surface — treat them as hypotheses to validate, not confirmed facts.

---

### Q1 — "What's on your screen?" *(targets: shadow systems, screen-switching sequence)*

> *"It's Monday morning, 9am. Four new hires start this week. Physically walk me through what you open and in what order — not what you're supposed to open, what you actually do. If it helps, pretend I'm sitting next to you watching."*

**What we're listening for:** How many screens are open before she feels oriented. Whether Workday is the first thing she opens or the last. Whether there's a spreadsheet or tracker she goes to first. Whether any tab is to a system not on the official list.

**The COO's answer:**
> "Priya opens her spreadsheet first. It's on her desktop — she calls it the live tracker. It's an Excel file, not in any official system. She updates it every morning with what she knows from the day before. Then she opens Workday, cross-checks the hire records against her spreadsheet, and updates anything that's changed. That takes about 20 minutes. Then she opens ServiceNow in a second window to check IT provisioning tickets. And she usually has a second tab in the ServiceNow window open to what we call 'Legacy HR' — it's our old system from before the 2019 Workday migration. She keeps it open because contractor records didn't fully migrate. Any time she's dealing with a contractor, she checks Legacy HR first because Workday's contractor history is unreliable before 2020. She doesn't call it a workaround. She's been doing it so long it just feels like the job."

**Design implications:**
- There are three systems open that aren't in the official stack: Priya's desktop Excel, Legacy HR, and a manually maintained SharePoint tracker for management reporting
- Workday is the third or fourth thing she opens, not the first — it is not the operational source of truth
- The agent cannot read Legacy HR if it has no API and no migration plan; contractor onboarding data quality is therefore unreliable from the start
- Building an agent that only reads Workday gives it less situational awareness than Priya's Excel tracker already has

**Refined follow-up:**
> *"Can I see the Excel tracker? Specifically: what columns does it have that Workday doesn't? What does the 'Verbal confirm?' column capture — does it mean she got an email reply, or that she spoke to someone? And how does she know to update Legacy HR — does it update automatically from Workday, or is she manually maintaining both?"*

---

### Q2 — "What's the number you actually trust?" *(targets: legacy system, real vs. official data)*

> *"If I asked you right now how many hires are inside their I-9 compliance window — started but not yet confirmed complete — where would you go to get that number? And if that number didn't match what Workday shows, which one would you trust?"*

**What we're listening for:** Whether the answer is a system, a spreadsheet, a sticky note, or her memory. Whether she's ever been burned by trusting official status. What "In Progress" actually means at a granular level.

**The COO's answer:**
> "She'd look at her iPhone. Literally — she has a note in the Notes app with every hire currently in their I-9 window. It has the hire's name, their start date, and a brief note like 'called 14th, waiting on section 2' or 'submitted per hire, needs HR section.' She started keeping it after our second I-9 violation. The violation happened because Workday showed 'In Progress' and we assumed that meant the hire had submitted the form. What 'In Progress' actually means in Workday is that the hire opened the portal and started filling it in. Submitted is different. There's a separate status — I think it's called 'Pending Review' — but it only appears if the hire went all the way through the portal submission. A lot of hires start it on their phone, get interrupted, intend to come back. The status looks the same whether they finished or not. Priya knows this. She confirmed it verbally with each hire and wrote it on her phone. Two violations taught us that Workday's I-9 status is only reliable at COMPLETE. Everything above PENDING is a yellow flag."

**Design implications:**
- `IN_PROGRESS` in Workday ≠ "submitted." The agent must treat anything below `COMPLETE` as at-risk, not just `PENDING`
- The real monitoring system for I-9 is a personal notes app — there is no system-level equivalent
- Two violations occurred under the current process despite the SOP calling for monitoring — this is an explicit failure the agent must address
- The agent may need to trigger an active confirmation request to the hire (not just poll system status), since system status lags behind reality

**Refined follow-up:**
> *"In Workday, what are all the exact I-9 status values that can appear — every single one, not just the common three? Is 'Pending Review' visible without drilling into the record? And has IT ever discussed adding a 'Submitted' vs 'In Progress' distinction to the Workday I-9 integration, or is that a system limitation from the I-9 vendor?"*

---

### Q3 — "When it's urgent, what channel?" *(targets: informal escalation paths, decision timing)*

> *"Think of the last time you needed a hold decision or a fast response from someone senior in under an hour. Walk me through how that actually happened — did you go through the system, or did you use something else?"*

**What we're listening for:** Whether the formal escalation path (email to HR Manager, update Workday) is the actual path. What happens when waiting for a system response is too slow. Whether Workday is updated before or after the decision.

**The COO's answer:**
> "Teams. Or WhatsApp if it's really urgent. I'll give you a specific example — last March, a hire's background check came back with a flag two days before their start date. Priya messaged me on Teams at 7:30pm: 'Background check flag on James Chen — need to decide by 8am whether to proceed. I've drafted a hold in Workday but haven't confirmed it. Call me.' I called her at 7:45. We agreed to hold. She confirmed it in Workday at 8:10am the next morning. The decision happened on a phone call at night. The system got updated the next morning. That's how it works for anything truly urgent. Email is for things that can wait four hours. Teams or phone is for things that can't. The Workday record is the audit trail of a decision that was already made. It's not the decision workflow."

**Design implications:**
- Workday hold entries are retrospective records of decisions made informally — not workflow triggers
- For CRITICAL escalations (I-9 Day 3, background check flag), email delivery latency of 3–4 hours makes the 15-minute SLA impossible by design
- The agent's escalation channel must be Teams or SMS for anything with a response SLA under 2 hours
- The agent needs to distinguish between "hold entered in Workday" (which may be hours old) and "hold decision made in real time"
- A provisional hold state is needed: the agent alerts, the human decides informally, and the system records it after

**Refined follow-up:**
> *"When Priya messages you on Teams about a hold — does that Teams message include a link to the hire record in Workday, or is it plain text? When you reply, does anyone log that exchange anywhere, or is it just a conversation that Priya later translates into a Workday update? And: what's the longest gap you've seen between a verbal hold decision and the Workday update?"*

---

### Q4 — "What would you lose if Priya left tomorrow?" *(targets: instinct calls, tribal knowledge, undocumented rules)*

> *"If Priya handed in her notice tomorrow and was gone in two weeks — what operational knowledge would leave with her? Not what's in the SOP. What does she know that isn't written down anywhere?"*

**What we're listening for:** Undocumented rules that affect routing decisions. Named individuals who have informal relationships with Priya. Instinct calls she makes that others would have to look up. Any data she maintains personally that would be lost.

**The COO's answer:**
> "Several things. First, the compliance training matrix on SharePoint is out of date. The version there still has a track called TEMP-EXT that was retired in Q1 2024. Priya has her own annotated version on her desktop — she updates it manually when Compliance sends an email. She's the only one who knows which version to use. Second: she knows never to assign a buddy from the Strategy department to a Finance hire. That's because of a conflict between two senior people two years ago. It's not written anywhere. She just knows. Third: she knows that any hire coming through a recruiter called Connections HR will almost always have the hire_type field set wrong in Workday — they consistently mark contractors as employees. She checks every Connections HR hire manually. Nobody else does. Fourth: she knows to call Mark in IT, not raise a ticket, when something is urgent. Mark will pick up. The ticket queue has a 48-hour turnaround. And fifth: her Excel tracker. If she left, we would lose our real-time view of every active hire. There is no backup."

**Design implications:**
- The compliance training matrix in SharePoint is wrong — the agent cannot use it without Priya's annotated corrections being formally captured first
- The "no Strategy buddies for Finance hires" rule cannot be encoded without explicit confirmation of the rule's scope and duration
- Recruiter-specific data quality issues (Connections HR → wrong hire_type) are entirely undetectable by the agent from system data alone
- The IT informal path (Priya → Mark) is a named relationship, not a process — it won't transfer to the agent
- The Excel tracker is a single point of failure that the agent must replace before Priya's knowledge walks out with her

**Refined follow-up:**
> *"The compliance matrix on Priya's desktop — can I get a copy of it alongside the SharePoint version so we can diff them? How many changes has she made to it? And the Connections HR hire_type issue — is there a way to flag hire source in Workday so the agent can check hire_type more aggressively for those records? Or would we need a separate validation rule?"*

---

### Q5 — "Before you send a reminder, what do you check?" *(targets: pre-conditions to actions, unstated decision logic)*

> *"Walk me through the last time you were about to send a reminder to a task owner and stopped yourself. What did you check first, and what made you hold back?"*

**What we're listening for:** The implicit pre-conditions that prevent a reminder from going out. Whether she checks OOO/leave status before chasing. Whether she checks system activity (not just status) before deciding the person hasn't done the work.

**The COO's answer:**
> "Last Tuesday. She was going to send a chase to Alex in IT about a provisioning ticket that was 3 days open. Before she sent it she opened the ServiceNow ticket to look at the activity log — not the status, the actual comments and internal notes. She saw that Mark had added a note two days ago saying 'waiting on VPN licence allocation from vendor, ETA Friday.' The status still showed 'Open' but the work was in progress. She held off. She wouldn't have known that from the status field alone. She also checks the company holiday calendar before chasing anyone — she has it bookmarked and she looks at it every time before sending a reminder to make sure the person isn't on leave. She said once she sent an urgent I-9 chase to a hire on their honeymoon. The hire called her panicking at 11pm. She's been checking the calendar ever since."

**Design implications:**
- Reminder logic based only on task status will fire on in-progress work that just hasn't been updated yet — this is a high-noise failure mode
- The agent needs to check activity/comment log in ServiceNow, not just ticket status, before deciding a task is stale
- The agent needs calendar/OOO integration before firing any reminder — sending a chase to someone on leave damages trust and creates a noise problem
- "Status = Open" is insufficient; "status = Open AND no activity in last 48h AND person is not on leave" is the real trigger
- The honeymoon example shows the human cost of getting this wrong — not just inconvenience but brand damage

**Refined follow-up:**
> *"In ServiceNow, how do you access the activity log for a ticket — is it a separate tab, or is it visible on the main ticket view? And for the holiday calendar: is that in Outlook/Exchange or a separate system? Can the agent query it via an API, or is it a manually maintained SharePoint page?"*

---

### Q6 — "What does your gut tell you before the system catches up?" *(targets: instinct calls, early signals, predictive patterns)*

> *"Think of a hire onboarding that you knew was going to go wrong before anything appeared in any system. What was the signal? Not the official trigger — the thing in your gut that told you this one needed watching."*

**What we're listening for:** The early-warning patterns that experienced operators recognise and systems can't yet detect. These often translate into leading indicators — data signals the agent could surface as risk flags at intake.

**The COO's answer:**
> "Priya would say: start date on a Thursday or Friday. Those almost always have IT provisioning problems because there isn't enough runway before the weekend and IT doesn't work weekends. She's mentioned that at least four times. Also: any hire with a seniority level of 4 or 5 where the department doesn't have many senior people — she knows the buddy pool is thin and she'll have a problem. She can see that from the org chart before she even opens the buddy matching criteria. And the third one: if the hiring manager sends her a message saying 'excited about this one, really need everything to go smoothly' — that hire will definitely hit a hold or a complication. She says it's not superstition, it's just that the hires where managers are anxious tend to be the edge cases: unusual role, atypical contract, new territory. The manager's anxiety is a proxy for process complexity. She can't write that in a tracker. But she knows it."

**Design implications:**
- Start date proximity to Friday/weekend is a machine-detectable risk flag the agent could surface at intake — not just monitor post-event
- Seniority level vs. department buddy pool depth is computable from the employee directory — the agent could flag thin buddy pools before matching even starts
- Manager communication tone is not a signal any system can read — this instinct remains human-only
- These early flags change the design from a reactive monitor to a proactive risk-ranker at intake — a different and more valuable capability

**Refined follow-up:**
> *"If the agent surfaced a 'risk flag' at intake — 'this hire starts Friday, IT provisioning historically runs long on Friday starters' — would Priya find that useful? Or would it create noise? And the buddy pool depth signal: can the agent compute that from the current employee directory in Workday, or would it need a separate query?"*

---

## Part 2: What the COO's Answers Change

The table below maps each revelation against its design impact.

| Revelation | What the SOP Assumed | What the COO Said | Specific Design Change |
|---|---|---|---|
| **Shadow tracker (Excel)** | Workday is the operational source of truth | Priya's desktop Excel is the real operational view; Workday is 1–5 days behind | Agent must replace the Excel tracker, not supplement Workday. Study the Excel schema first — its columns define the real data model |
| **Legacy HR system** | 5 systems in scope | 6 systems — Legacy HR stays open for all contractor onboarding pre-2020 | Add Legacy HR to system inventory; assess API or batch access; contractor onboarding risk is higher than assumed |
| **I-9 IN_PROGRESS ≠ submitted** | PENDING / IN_PROGRESS / COMPLETE are reliable signals | IN_PROGRESS means "started, not submitted." COMPLETE is the only safe signal. Two violations occurred under current process | Treat anything below COMPLETE as at-risk. Consider active confirmation request to hire on Day 1, not just passive status poll |
| **Escalations on Teams/phone** | Email escalations will be seen and acted on within SLA | Email latency is 3–4 hours; urgent decisions happen on Teams or phone | Critical escalations (I-9 Day 2+, background flags) must route via Teams or SMS. Email alone cannot meet the 15-minute SLA |
| **ServiceNow tickets are retrospective** | SNOW ticket status shows real-time IT progress | Urgent IT work happens via direct email to Mark; ticket raised after the fact | Agent monitoring open SNOW tickets will produce false overdue alerts for work already done. Must check activity log and ticket age, not just status |
| **Compliance matrix is stale** | SharePoint version is current | SharePoint matrix has a retired track (TEMP-EXT, retired Q1 2024). Priya's desktop version is the real one | Agent cannot use SharePoint compliance matrix without Priya's corrections first. Require formal handover of annotated version before launch |
| **Undocumented routing rules** | Buddy matching follows documented seniority rules | Additional rule: no Strategy dept. buddies for Finance hires. Not in any system | This rule cannot be encoded without formal documentation. Surface to Compliance/HR Manager; get it written before build |
| **Recruiter data quality** | Workday hire_type is reliable | Connections HR consistently mislabels hire_type. Priya manually corrects every hire | Agent needs a recruiter-flagging rule: if hire_source = Connections HR, force hire_type validation before task set creation |
| **Activity log before reminding** | Status field is the correct overdue signal | Status alone is insufficient; Priya checks activity log for recent work before sending chase | Reminder logic must check: status OPEN AND no activity in 48h AND person not on OOO — not just status |
| **Start-date risk signals** | All hires enter monitoring with equal priority | Friday starters and thin buddy pools are predictable risk patterns | Agent should compute risk flags at intake and prioritise monitoring accordingly — not treat all hires equally |

---

## Part 3: Refined Second-Round Questions

Based on what the COO revealed, these are the follow-up questions that now matter most. First-round SOP questions would never have reached them.

| # | Refined Question | Why It Matters Now |
|---|---|---|
| **RQ1** | Can I see Priya's Excel tracker? What columns does it have that Workday doesn't? What does "Verbal confirm?" track — email reply or phone call? | Agent must replicate the Excel schema. If "verbal confirm" means a phone call, the agent cannot replicate it — and that changes the I-9 monitoring design |
| **RQ2** | What are all the exact I-9 status values in Workday? Is "Pending Review" visible without drilling into the record? Has IT discussed distinguishing "submitted" from "in progress"? | If IN_PROGRESS is ambiguous, the agent must escalate at Day 1, not Day 2 — earlier than the spec currently assumes |
| **RQ3** | When Priya messages you on Teams about a hold — does the message link to the hire record? Who logs the decision afterwards, and how long after the phone call? | If the decision channel and the record channel are disconnected, the agent's audit trail will have holes. This may require a structured Teams bot, not a plain Teams message |
| **RQ4** | Can I get both versions of the compliance matrix — SharePoint and Priya's desktop version — to diff them? How many active tracks has she changed? | The diff tells us exactly how stale the system version is. If it's >5 changes, the matrix must be formally refreshed before launch — not just "checked" |
| **RQ5** | Is the ServiceNow activity log accessible via API? What fields does it expose — timestamp, author, note text? Can the agent query "last activity" without downloading the full ticket? | If the activity log isn't API-queryable, the agent cannot replicate Priya's "check if work is happening" step before sending a reminder |
| **RQ6** | Is the holiday/OOO calendar in Exchange (queryable via Graph API) or a separate SharePoint list? And does Priya check leave for the task owner or for the hire — or both? | Agent OOO checking requires API access to the calendar. If it's a SharePoint list, that's a different integration. If she checks both owner and hire, that's two lookups per reminder |
| **RQ7** | For Friday-start hires: what's the actual IT provisioning delay pattern? Is it a 24h delay, or does it sometimes push to the following Monday? And which role types are most affected? | If the pattern is consistent, the agent can apply a "Friday-start adjustment" to the IT provisioning deadline automatically at intake |

---

## Part 4: Updated Assumptions After Simulation

| Assumption | Original Confidence | Revised Confidence | What Changed |
|---|---|---|---|
| Workday is the operational system of record | MEDIUM | **LOW** | COO confirmed a parallel Excel status sheet is the real operational view; Workday is a formal record, not a live tool |
| 5 systems are in scope | MEDIUM | **LOW** | Legacy HR is a 6th system, permanently open for contractor onboarding |
| I-9 COMPLETE status in Workday is reliable | HIGH | **CONFIRMED HIGH** — but scope narrowed | COMPLETE is reliable; IN_PROGRESS is not |
| I-9 IN_PROGRESS means "on track" | MEDIUM | **VERY LOW** | IN_PROGRESS = "started portal, not submitted" — was root cause of both violations |
| Critical escalations via email will be acted on | MEDIUM | **LOW** | COO email latency = 3–4 hours; Teams latency = under 1 hour. Email cannot meet CRITICAL SLA |
| ServiceNow ticket status = real-time provisioning status | MEDIUM | **LOW** | Urgent IT work bypasses SNOW; tickets raised retrospectively. Status = open may mean "done but not updated" |
| Compliance matrix in SharePoint is current | LOW | **CONFIRMED LOW** | TEMP-EXT track retired Q1 2024 still present in SharePoint version. Priya's desktop copy is the real matrix |
| Buddy matching follows documented seniority rules | MEDIUM | **LOW** | Undocumented department exclusion rule exists (Strategy → Finance). Not encodable without formal documentation |
| Reminder logic: if overdue AND no reminder in 24h → send | MEDIUM | **LOW** | Real logic: overdue AND no system activity in 48h AND person not on leave AND person not on travel → send |

---

## What Must Be Resolved Before Building

Three things must be in place before the agent can do its job reliably. Without them, the agent will have less operational knowledge than Priya already has:

**1. Acquire Priya's Excel tracker and make it the schema baseline.**  
The tracker is the real mental model of the work. Every column it has that Workday doesn't is a gap the agent must fill. Get the file, document its schema, and treat it as the primary design input — not the SOP.

**2. Establish the escalation channel with the actual decision-makers.**  
Teams or SMS for anything with a response SLA under 2 hours. This requires IT provisioning of the integration and confirmation from the COO and HR Manager that they will respond to that channel. Without this, the I-9 SLA is structurally unachievable.

**3. Formally document every undocumented rule before launch.**  
The Connections HR hire_type issue, the Strategy/Finance buddy exclusion, Priya's compliance matrix corrections — none of these are encodable from system data alone. They must be captured in structured configuration before the agent goes live. If Priya leaves before this happens, these rules leave with her.
