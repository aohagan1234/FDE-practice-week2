# DELIVERABLE 3 — VOLUME × VALUE ANALYSIS

**Scenario:** Apex Distribution Ltd (Gate 2)  
**Exercise:** Week 2 Assessment, Timed  
**Objective:** Plot 4 work streams on volume × value axes; identify primary agentic target; justify selection.

---

## 1. VOLUME CALCULATION (Monthly, 22 business days)

| Work stream | Daily volume | Avg handling time | Daily hours | Monthly hours (22 days) | % of total 35-person-team output |
|---|---|---|---|---|---|
| **W1: Exceptions** | 180 | 12 min | 36 | 792 | 22.6% |
| **W2: ETA inquiries** | 400 | 4 min | 26.7 | 587 | 16.8% |
| **W3: Adjustments** | 90 | 18 min | 27 | 594 | 17.0% |
| **W4: Billing disputes** | 60 | 28 min | 28 | 616 | 17.6% |
| **TOTAL** | **730** | **~10.5 min avg** | **117.7** | **2,589** | **~74%** |

**Notes:**
- Total team capacity: 35 people × 20 hours/week (9–5 with breaks) × 22 days = ~3,500 hours/month (theoretical full capacity)
- Actual output: 2,589 hours on these 4 work streams = ~74% of team (rest: meetings, admin, edge cases, other projects)
- **Volume leader:** W1 (exceptions, 792 h/month) + W2 (ETA, 587 h/month) = 1,379 h/month = 53% of the 2,589 h total
- **Time-intensive:** W4 (disputes, 28 min avg) is highest per-case effort

---

## 2. VALUE DIMENSIONS (Operational + Strategic)

### 2.1 Operational value (Time savings × Automation potential)

| Stream | Automation potential (from Matrix) | Estimated monthly time savings | FTE equivalent |
|---|---|---|---|
| **W1** | ~50% (exception detection + escalation; damage assessment stays human) | ~396 h/month | 2.0 FTE |
| **W2** | ~95% (lookup fully agentic; ETA generation agent-led with escalation) | ~558 h/month | 2.8 FTE |
| **W3** | ~30% (data surfacing + option generation; human decides) | ~178 h/month | 0.9 FTE |
| **W4** | ~50% (triage + execution + <£50 approval; investigation + ≥£50 approval human-led) | ~308 h/month | 1.5 FTE |

**Calculation:** Monthly hours × automation potential = monthly time savings. FTE = time savings ÷ 200 (hours per FTE per month).

**Ranking by operational value (time savings):**
1. **W2:** 558 h/month (2.8 FTE) — Highest time savings
2. **W1:** 396 h/month (2.0 FTE) — Second highest
3. **W4:** 308 h/month (1.5 FTE) — Lower (compliance complexity reduces automation)
4. **W3:** 178 h/month (0.9 FTE) — Lowest (route re-optimization is hard to automate)

---

### 2.2 Strategic value (Risk reduction + ROI payback)

| Stream | Risk type | Strategic value | ROI payback |
|---|---|---|---|
| **W1** | Reputational (missed exception = angry customer) | MEDIUM | 6–12 months (time savings + risk reduction) |
| **W2** | Service level (stale ETA = lost customer) | LOW | 1–2 months (pure time savings, fastest payback) |
| **W3** | Operational (wrong re-routing = SLA miss + churn) | MEDIUM-HIGH | 12–18 months (risky; slow payback) |
| **W4** | **Compliance (audit trail gap + penalty exposure)** | **HIGH** | **3–6 months (risk reduction worth £100K+ if 1 penalty avoided)** |

**Compliance risk detail (W4):** Artefact 2 shows manual credit audit trail missing (no AUDIT_REF). Compliance review penalty for insufficient audit trail could be £10K–£100K+ depending on jurisdiction. If agent design enforces audit logging, compliance exposure is reduced, justifying investment even with lower time savings.

**Reputational risk detail (W1):** Exception handling failures (missed damages, wrong re-attempts) lead to customer escalation and churn. Volume is high (180/day); one bad exception = multiple customer touches. Strategic value is real but hard to quantify in £.

**SLA risk detail (W3):** Dispatch adjustments have tight SLA. Wrong decision = missed delivery window = penalty to Apex + customer churn. Risk is HIGH; automation potential is LOW (judgment-heavy). Not a good bet for Phase 1.

---

### 2.3 Build complexity & integration risk

| Stream | API availability | Data freshness | External dependencies | Build risk |
|---|---|---|---|---|
| **W1** | CRM lookup (REST API ✓); Dispatch console query (limited SOAP) | Real-time (driver app via CRM) | Insurance (slow); shipper (async) | MEDIUM (dispatch console API limited) |
| **W2** | CRM lookup (REST API ✓); Driver app messaging (async) | 5–10 min lag acceptable | Driver messaging latency (real constraint) | **LOW** (simple lookup + async message) |
| **W3** | Dispatch console (limited API); route optimization (external SaaS?) | Real-time route data needed | Route optimizer API (unknown if exists) | **HIGH** (no route optimizer confirmed) |
| **W4** | CRM + Aurum batch (CSV, T-1 lag, NO API) | 24h lag for batch; shipper async | Aurum batch (slow); shipper (async); insurance (async); manager approval queue | **HIGH** (multiple async waits + Aurum batch dependency) |

---

## 3. VOLUME × VALUE MATRIX

```
                HIGH VALUE (Strategic + Compliance)
                        ↑
                   W4 ◆ |  W1 ◆
                        |
     Build risk: HIGH   |    Build risk: MEDIUM
     ROI: 3–6 mo        |    ROI: 6–12 mo
                        |
────────────────────────┼────────────────────────→ LOW VALUE (Operational only)
                        |
                   W3 ◆ |  W2 ◆
     Build risk: HIGH   |    Build risk: LOW
     ROI: 12–18 mo      |    ROI: 1–2 mo
                        |
   LOW VOLUME (60–90/day) HIGH VOLUME (180–400/day)
```

**Quadrant interpretation:**

- **Upper-right (W1):** HIGH volume, MEDIUM value — Good balance, but build risk is MEDIUM (dispatch console API)
- **Upper-left (W4):** LOW volume, HIGH value (compliance) — Strategic win, but HIGH build complexity (Aurum batch, async waits)
- **Lower-right (W2):** HIGH volume, LOW value (operational only) — Fastest payback, LOWEST risk — **BEST for Phase 1**
- **Lower-left (W3):** LOW volume, LOW value — Avoid; highest complexity + longest payback

---

## 4. DECISION: PRIMARY AGENTIC TARGET

### **Winner: W2 (ETA Inquiries) — Phase 1 primary target**

**Rationale:**

1. **Highest volume leverage:** 400 inquiries/day = 558 h/month savings = 2.8 FTE freed up. At £50K/FTE cost, **£140K/month operational value** (or redeployment capacity).

2. **Lowest build risk:** 
   - Cluster 2a (lookup) is fully agentic with no risk
   - Cluster 2b (ETA + driver sync) has explicit escalation protocol (2 min driver wait, then fallback)
   - No external dependencies (Salesforce REST API is available; driver messaging is async)
   - No compliance complexity (no audit trail needed; SLA miss is service-level, not regulatory)

3. **Fastest ROI payback:** 1–2 months to recover build cost (assuming 4-week build), enabling quick proof-of-value.

4. **Credibility rebuild:** Sarah has seen 2 prior failures (2024 chatbot, RPA). Quick operational win (W2) on ETA handling rebuilds trust. After W2 succeeds, propose W4 as Phase 2 (compliance risk reduction).

5. **Data freshness risk is acceptable:** W2 doesn't depend on Aurum batch (unlike W4). CRM sync lag (5–10 min) is acceptable for ETA inquiries (customer doesn't need tighter than 1h window for most cases).

### **Secondary target: W4 (Billing Disputes) — Phase 2 opportunity**

**Rationale for deferral:**
- Lower volume (60/day vs. 400/day)
- Higher complexity (investigation + async waits: shipper 24–72h, manager queue 2–4h)
- Higher build risk (Aurum batch dependency, no API)
- BUT high strategic value: compliance risk reduction (audit trail gap) + customer satisfaction (faster dispute resolution)

**Recommendation for Sarah (live round):**
> "Build W2 first (ETA, 1–2 month payback, low risk). After W2 proves value in production, we'll propose W4 (Phase 2) — lower volume but higher strategic impact on compliance and customer satisfaction."

---

## 5. AGENT SCOPE FOR W2 (ETA Inquiries)

**In scope (Phase 1):**
- **Cluster 2a:** Consignment lookup + status classification (fully agentic)
- **Cluster 2b:** ETA generation + driver sync (agent-led with escalation)

**Out of scope (future phases or manual):**
- W1 (exceptions) — Defer to Phase 2; higher complexity requires build discipline
- W3 (dispatch adjustments) — Defer indefinitely; requires route optimizer API (not confirmed)
- W4 (billing disputes) — Defer to Phase 2; lower volume, but strategic value after W2 succeeds

**Agent name:** "Coordinator ETA" (works with driver app to provide tight ETAs)

**KPIs (Phase 1):**
- Response time: <5 min (current agent SLA)
- Resolution rate (no escalation): >80% (for active deliveries)
- Accuracy: ETA within ±15 min of actual delivery (customer satisfaction proxy)
- Uptake: % of 400/day inquiries handled by agent vs. human

---

## 6. FINANCIAL SUMMARY

| Metric | W2 (ETA) | W4 (Billing) | W1 (Exceptions) |
|---|---|---|---|
| **Monthly time savings** | 558 h | 308 h | 396 h |
| **FTE equivalent** | 2.8 | 1.5 | 2.0 |
| **£ value (at £50K/FTE)** | £140K/month | £75K/month | £100K/month |
| **Build complexity** | LOW | HIGH | MEDIUM |
| **ROI payback** | 1–2 months | 3–6 months | 6–12 months |
| **Strategic value** | LOW (operational) | HIGH (compliance) | MEDIUM (reputational) |
| **Dependency risk** | LOW | HIGH (Aurum batch) | MEDIUM (Dispatch console) |

**Build cost assumption:** £50–100K (4-week effort for W2; agent + integration testing)

**Payback calculation (W2):**
- £140K/month operational value ÷ £75K build cost = **1 month to break even** (conservative: assumes 50% of time savings are realized in Month 1)

---

## 7. ANTI-PATTERN CHECK

✅ **Not chasing the "sexy" problem:** W4 (compliance) is strategic, but deferring it to Phase 2 is discipline. Building W2 first (operational, low-risk) establishes credibility for Phase 2.

✅ **Not over-scoping:** Staying within W2 clusters 2a + 2b only. Not trying to do W1 + W2 + W4 in parallel.

✅ **Not ignoring risk:** Escalation protocol for 2b is explicit (2 min driver wait, then fallback). Not assuming driver will always respond.

---

## 8. RECOMMENDATION TO SARAH (Live round)

> "The data shows W2 (ETA inquiries, 400/day) is your Phase 1 target. Lowest build risk, highest volume leverage, fastest payback (1–2 months). After W2 succeeds, Phase 2 is W4 (billing disputes) for compliance risk reduction. W3 and W1 stay on roadmap but aren't Phase 1 priorities given build complexity and lower ROI clarity."

---

## 9. NEXT STEP

Deliverable 4 (Agent Purpose Document) designs the full spec for W2: autonomy matrix, escalation triggers, failure modes, success metrics.

