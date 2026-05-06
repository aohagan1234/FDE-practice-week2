# DELIVERABLE 4 — AGENT PURPOSE DOCUMENT

**Scenario:** Apex Distribution Ltd (Gate 2)  
**Target:** Work Stream 2 (ETA inquiries)  
**Agent name:** "Coordinator ETA" (working title)  
**Build scope:** Phase 1 (Clusters 2a + 2b from CLM)  
**Timeline:** 4-week build + 2-week testing = 6 weeks to production

---

## 1. EXECUTIVE SUMMARY

**Purpose:** Autonomous handling of customer ETA (estimated time of arrival) inquiries for active and pre-dispatch deliveries. Current state: 400 inquiries/day, 4 min avg handling time = 26.7 person-hours/day. Target: Agent handles 95% independently; human handles <5% (edge cases). Expected outcome: 2.8 FTE freed for 140K/month redeployment value.

**Scope:**
- **In scope:** Consignment lookup (Cluster 2a), ETA generation (Cluster 2b), driver contact protocol
- **Out of scope:** Exception deliveries (damaged, refused, on-hold) → escalate to human; dispatch adjustments; billing disputes

**Success criteria:**
- Resolution rate >80% (no human escalation needed)
- Response time <5 min (match/beat current agent SLA)
- Accuracy: ETA within ±15 min of actual delivery (customer satisfaction proxy)
- Uptake: >95% of 400/day inquiries routed to agent

**Compliance:** None required. ETA provision is service-level; no audit trail needed. SLA miss is reputational, not regulatory.

---

## 2. AGENT AUTONOMY MATRIX

### 2.1 Fully autonomous (Agent decides, no human involved)

| Task | Condition | Decision | Action | SLA |
|---|---|---|---|---|
| **Consignment lookup** | Consignment ID matches CRM record | Status is one of: pre-dispatch, out-for-delivery, delivered | Return status to customer | <1 min |
| **Status = Delivered** | Delivery already completed | Return delivery time + signature | Reply: "Delivered at [time], signed by [name]" | <1 min |
| **Status = Pre-dispatch** | Consignment not yet left warehouse | No driver assigned yet | Reply: "Departing tomorrow 08:00. Will arrive by [next-day window]" | <1 min |
| **Status = Exception** | Delivery flagged as refused / damaged / on-hold | Return exception reason from CRM; create escalation case | Reply: "There's an issue with this delivery — our team will contact you within [SLA]"; route to dispatcher queue | <1 min (reply); dispatcher picks up case |
| **Inquiry deduplication** | Same customer + consignment asked <1h ago | Prior response is cached | Reply from cache (avoid duplicate driver query) | <30 sec |

### 2.2 Agent-led with explicit escalation

| Task | Condition | Happy path | Exception path | Escalation SLA |
|---|---|---|---|---|
| **ETA inquiry for active delivery** | Status = "out-for-delivery" | Query driver via Driver app for current location + next-stop ETA | Driver non-responsive >2 min | 2 min wait, then decide |
| **Driver responds in time** | Driver replies within 2 min | Calculate ETA from driver location + stops remaining + travel time | — | <1 min (templated reply) |
| **Driver doesn't respond in time** | No driver response within 2 min | Reply to customer with fallback "afternoon 13:00–17:00" window; log as escalation attempt | Escalate to dispatcher for manual driver contact (optional, if customer requests tighter ETA) | Reply sent <2.5 min total |

### 2.3 Human-led (Agent surfaces data, human decides)

| Task | Condition | Agent role | Human role | SLA |
|---|---|---|---|---|
| **Consignment not found** | ID doesn't match any CRM record | Flag with comment: "Consignment not found; customer says order [ID]; suggest manual shipper lookup" | Check manual records; confirm shipping label scanned; provide backorder ETA if applicable | <2 min (human response) |
| **Status = Exception** | Delivery marked "refused," "damaged," "on-hold" | Return exception reason from CRM + flag for dispatcher context | Contact customer with root cause + next steps (e.g., "Refused due to damaged pallet; will retry tomorrow") | <5 min (escalate to dispatcher) |
| **Status = Null** | Delivery status is empty/unknown in CRM (data error) | Flag with comment: "CRM status missing for consignment [ID]" | Investigate CRM sync issue; manually confirm delivery state with dispatch | <10 min (investigate) |

---

## 3. ESCALATION WORKFLOWS

### 3.1 Escalation conditions (auto-trigger)

| Trigger | Reason | Action | Route |
|---|---|---|---|
| **Consignment not found** | CRM lookup returns zero results | Reply: "Not in our system; checking manual records…" then escalate | CRM → Manual lookup queue → Human |
| **Driver non-responsive >2 min** | Agent queried driver; no response after 2 min wait | Reply: "Best ETA is afternoon (13:00–17:00). Want exact time?" then escalate | Driver app → Optional dispatcher escalation |
| **Status = Exception** | Consignment flagged for issue (refused, damaged, held) | Return exception + flag for dispatcher | CRM exception flag → Dispatcher queue |
| **CRM API down** | Salesforce REST API unavailable | Route to manual inquiry queue | Failover → Manual agent queue |
| **Driver app messaging unavailable** | Driver app is offline or not responding | Skip driver contact; reply with fallback window | No-op: driver contact skipped; fallback sent |
| **Multiple rapid inquiries for same consignment** | Customer asks 3x in 1 hour for same order | Reply from cache (avoid duplicate driver queries) | Cache hit: deduplicated response |

### 3.2 Escalation protocol details

**Scenario 1: Driver doesn't respond in 2 min**
```
T+00 sec: Agent receives inquiry for consignment #AX-771-3344 (active delivery)
T+05 sec: Agent queries CRM → status = "out-for-delivery" on route 028
T+10 sec: Agent sends message to driver: "Customer asking ETA for drop AX-771-3344. Current location?"
T+70 sec: [Agent waiting for driver response; <50% chance of response by now]
T+120 sec: [No response from driver]
T+121 sec: Agent decides: (a) Reply with fallback window (primary), or (b) Escalate to dispatcher (optional)

Primary (90% of cases): 
  → Reply to customer: "Your delivery is out for delivery. Best guess: 14:00–15:00 today. 
     Driver is in [area]; will call you 30 min before arrival."
  → Log as "driver non-responsive" for weekly metrics
  → Close case

Optional (10% of cases, if customer is VIP or explicitly requests tighter ETA):
  → Escalate to dispatcher with comment: "Customer needs tighter ETA. Can you contact driver?"
  → Dispatcher calls/messages driver manually (adds 3–5 min to SLA)
  → Dispatcher replies to agent; agent forwards tight ETA to customer
  → SLA: 7–10 min total (acceptable for VIP or urgent)
```

**Scenario 2: Consignment not found**
```
T+00 sec: Agent receives inquiry; customer says order #AX-771-3999
T+10 sec: Agent queries CRM → no match found
T+11 sec: Agent replies: "This delivery isn't in our system yet. It may be queued at our warehouse. 
          Let me check manually. I'll call you back in 2 minutes."
T+12 sec: Agent escalates to manual lookup queue (CRM → Human lookup pool)
T+120 sec: Human checks manual records (paper manifest, shipper email, hand-written notes)
T+180 sec: Human replies to customer directly with ETA or status update
```

---

## 4. DECISION TREE (Agent logic flow)

```
START: Customer inquiry received (SMS/call/app)
  │
  ├─→ Parse consignment ID
  │    │
  │    ├─→ ID is valid format? NO → Escalate (manual interpretation)
  │    └─→ ID is valid format? YES → Continue
  │
  ├─→ Query CRM for consignment
  │    │
  │    ├─→ Match found? NO → Escalate to manual lookup
  │    └─→ Match found? YES → Continue
  │
  ├─→ Check CRM status field
  │    │
  │    ├─→ Status = "delivered"? YES → Return delivery time + signature; CLOSE
  │    ├─→ Status = "pre-dispatch"? YES → Return "Tomorrow 08:00–17:00"; CLOSE
  │    ├─→ Status = "exception"? YES → Return exception reason; Escalate to dispatcher; CLOSE
  │    ├─→ Status = Null/unknown? YES → Escalate (data error); CLOSE
  │    └─→ Status = "out-for-delivery"? YES → Continue to ETA generation
  │
  ├─→ Check inquiry cache (did this customer ask <1h ago?)
  │    │
  │    ├─→ Cache hit? YES → Reply from cache; CLOSE
  │    └─→ Cache hit? NO → Continue
  │
  ├─→ Query driver for current location + ETA (async message)
  │    │
  │    ├─→ Wait up to 2 min for driver response
  │    │    │
  │    │    ├─→ Driver responded? YES → Calculate ETA; Reply with tight window (e.g., "14:15–14:45"); CLOSE
  │    │    └─→ Driver didn't respond? NO → Continue to fallback
  │    │
  │    ├─→ Reply with fallback window ("Afternoon, 13:00–17:00")
  │    ├─→ Optional: Escalate to dispatcher (if VIP flag or customer requests manual contact)
  │    └─→ CLOSE
  │
END
```

---

## 5. FAILURE MODES & MITIGATION

| Failure mode | Root cause | Detection | Impact | Mitigation |
|---|---|---|---|---|
| **Stale ETA provided** | CRM status is 5–10 min old; agent gives ETA that was accurate 10 min ago but driver has moved | Customer calls back: "I got delivery 30 min earlier than you said" | Reputational (low); customer wastes time waiting | Accept as acceptable variance. Document expected lag in agent response template: "Best guess based on last update." |
| **Driver non-response timeout causes SLA miss** | Driver phone is off/in pocket; agent waits full 2 min then replies with fallback. Customer expected <5 min response. | Response time >5 min logged; escalates if >10 cases/day exceed SLA | Customer escalation to supervisor | Escalation protocol includes dispatcher override (optional): if SLA at risk, escalate to human for manual driver contact. Accept <5% of cases may miss SLA. |
| **Consignment not found causes false negative** | Shipper hasn't scanned label yet; consignment is on pallet in warehouse but not in CRM. Customer thinks order is lost. | Customer calls back: "You said it's not in the system, but I have the label" | Reputational; customer annoyance | Escalation reply includes: "Checking manual records; shipper may not have scanned the label yet. Standing by." → Hands off to human. |
| **Wrong status returned due to CRM sync lag** | Driver completed delivery 5 min ago but CRM hasn't updated. Agent says "out for delivery" when actually delivered. | Customer says "I got my delivery already at 14:30" but agent said "14:00–15:00" | Low impact; customer has delivery; just timing mismatch | Accept. Include in response: "Status may be a few minutes behind real-time." |
| **API unavailable (Salesforce down)** | REST API timeout or 503 error | CRM query fails; agent gets exception | No ETA provided; customer escalated to manual queue | Failover: Escalate immediately to manual agent pool. SLA becomes human SLA (5–10 min). |
| **Driver app messaging unavailable** | Driver app is offline; agent cannot send message to driver | Message send fails; agent receives error | Driver contact skipped; fallback window sent (acceptable) | Skip driver contact; use fallback window. Accept: driver contact is best-effort, not mandatory. |

---

## 6. SUCCESS METRICS & MONITORING

### 6.1 Primary KPIs

| Metric | Target | Measurement | Frequency |
|---|---|---|---|
| **Resolution without escalation** | >80% | % of 400/day inquiries that agent handles autonomously | Daily |
| **Response time** | <5 min | P50 response time from inquiry receipt to response sent | Daily |
| **ETA accuracy** | Within ±15 min of actual delivery | Matched actual delivery time against agent ETA provided | Weekly |
| **Agent uptake** | >95% of 400/day routed to agent | Count of inquiries → agent pool (vs. manual queue) | Daily |

### 6.2 Secondary KPIs (health/risk)

| Metric | Target | Measurement | Frequency |
|---|---|---|---|
| **Driver response rate** | >80% within 2 min | % of driver queries that get response within 2 min | Weekly |
| **Fallback usage** | <20% of active-delivery inquiries | % of cases where agent gives fallback "afternoon" window | Weekly |
| **Escalation reasons** | Track & trend | % due to (driver non-response / consignment not found / API down / exception flag) | Weekly |
| **CRM API availability** | >99.5% | Uptime of Salesforce REST API (monitored via agent) | Daily |
| **Cache hit rate** | Track & trend | % of inquiries matched to <1h prior inquiry | Weekly |

### 6.3 Success criteria (Phase 1, 8 weeks post-production)

- ✅ Agent handles >80% of 400/day inquiries (320+ cases/day autonomous)
- ✅ Response time P50 <5 min, P95 <10 min
- ✅ ETA accuracy: delivered within ±15 min of agent prediction
- ✅ Zero critical incidents (API down, mass failures)
- ✅ Customer satisfaction: no increase in ETA-related complaints vs. baseline

---

## 7. DATA & INTEGRATION REQUIREMENTS

### 7.1 Data inputs

| Data | Source | API/Access | Freshness | Required? |
|---|---|---|---|---|
| **Consignment ID** | Customer inquiry (SMS/call/app) | Direct input | Real-time | YES |
| **CRM consignment record** | Salesforce CRM | REST API (available) | Real-time (CRM polling-based, 5–10 min lag) | YES |
| **Delivery status** | Salesforce CRM | REST API | 5–10 min lag | YES |
| **Route code** | Salesforce CRM | REST API | Real-time | Conditional (if active delivery) |
| **Driver location** | Driver app | Driver app messaging API (async) | Real-time GPS; message delivery 1–5 min lag | Conditional (if active delivery) |
| **Driver current ETA** | Driver app response (async message) | Driver app messaging | 1–5 min response time | Conditional (best-effort) |

### 7.2 Data outputs

| Data | Target | API/Method | Notes |
|---|---|---|---|
| **ETA reply** | Customer (SMS/call/app) | Message queue → SMS/push/email | Use existing channel (how inquiry arrived) |
| **Escalation flag** | Dispatcher / Manual queue | CRM case creation | Mark case as "escalated from ETA agent" |
| **Audit log** | Internal analytics | Local agent log (CSV daily) | Track resolution, fallback usage, failures |

### 7.3 Integration with existing systems

- **Salesforce CRM:** REST API (stated as available); agent queries consignment table, updates case status
- **Driver app:** Async messaging via existing driver-to-dispatch channel (no new API integration needed; use existing infrastructure)
- **Message queue:** Use existing SMS/call/app routing (agent replies go to same channel as inquiry)
- **Manual escalation:** Create cases in CRM "ETA escalation" queue for humans to handle

**Integration effort:** LOW to MEDIUM. Salesforce CRM REST API is confirmed available. Driver app integration is LOW confidence (D5 Assumption A2): the brief states driver-to-dispatch messaging exists, but whether the agent can programmatically query GPS coordinates or send messages via API is unconfirmed. If the driver app exposes a messaging API, integration effort is LOW. If message-only access exists via the existing dispatch channel, integration effort is MEDIUM (async message pattern). If no API surface is available, the driver contact capability is removed and integration effort drops back to LOW (CRM-only) but ETA tightness degrades.

---

## 8. ASSUMPTIONS & OPEN QUESTIONS

| Assumption | Confidence | Discovery Q |
|---|---|---|
| CRM REST API is available and real-time | MEDIUM | Q2: Is CRM delivery status updated real-time from driver app, or end-of-day batch? |
| Driver app messaging SLA is ~80% within 2 min | LOW | Q3: On Friday PM, 95th %ile latency for driver to receive+read message? |
| Escalation to dispatcher is optional, not mandatory | MEDIUM | Q10: If ETA agent can't reach driver, can it fallback to "afternoon window," or must it always escalate to dispatcher? |
| Customer satisfaction with "afternoon window" is acceptable | MEDIUM | Q5: What's minimum ETA tightness customers expect? (Current offering is 4h; is agent 2h fallback acceptable?) |

---

## 9. ANTI-PATTERNS AVOIDED

✅ **Not assuming 100% autonomous:** Agent-led with escalation (Cluster 2b) explicitly accounts for driver latency. If driver doesn't respond in 2 min, agent has a fallback (doesn't hang).

✅ **Not assuming CRM is real-time:** Noted 5–10 min lag in CLM. Agent accepts stale status as acceptable variance.

✅ **Not over-scoping:** Agent handles ETA inquiries only (W2 Clusters 2a + 2b). Does not handle exceptions (W1), dispatch adjustments (W3), or billing (W4).

✅ **Escalation protocol is explicit, not vague:** Driver non-responsive >2 min → decision rule: primary = fallback reply; optional = escalate to dispatcher.

---

## 10. SCOPE-OUTS FOR FUTURE PHASES

- **W1 (Delivery exceptions):** Defer to Phase 2. Complexity is higher; requires damage assessment rules + insurance lookup.
- **W3 (Dispatch adjustments):** Defer indefinitely. Requires route optimizer API (not confirmed available).
- **W4 (Billing disputes):** Defer to Phase 2. Lower volume; higher compliance complexity.
- **Proactive ETA notifications:** Out of scope. Agent handles reactive inquiries only (customer asks). Future: proactive alerts ("Your delivery will arrive by 3pm") from driver app.

---

## 11. BUILD TIMELINE & HANDOFF

**Phase 1 build (4 weeks):**
- Week 1: Data modeling (CRM schema, driver app schema) + decision tree validation
- Week 2: Agent logic implementation (Clusters 2a + 2b) + escalation protocol
- Week 3: Integration testing (CRM API, driver app messaging, manual queue)
- Week 4: End-to-end testing (100 test cases) + production readiness

**Phase 1 testing (2 weeks):**
- Week 5: Canary rollout (10% of 400/day inquiries = 40/day to agent; 360/day to human) + monitoring
- Week 6: Full rollout (100% of 400/day to agent) + 1-week production stabilization

**Success gate:** If Phase 1 KPIs are met (>80% resolution, <5 min response), Phase 2 is greenlit (W4 agent design).

---

## 12. NEXT STEPS

**Deliverable 5 (System/Data Inventory):** Detail system constraints, Aurum batch specifics, integration risks.

**Deliverable 6 (Discovery Questions):** Ask Sarah the 12 questions; get validation on assumptions (especially driver SLA, CRM real-time status, escalation protocol).

**Deliverable 7 (CLAUDE.md):** Workflow summary + anti-pattern avoidance + lessons learned from review.

