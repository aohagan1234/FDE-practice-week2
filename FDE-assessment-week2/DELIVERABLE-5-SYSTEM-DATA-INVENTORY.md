# DELIVERABLE 5 — SYSTEM/DATA INVENTORY

**Scenario:** Apex Distribution Ltd (Gate 2)  
**Agent in scope:** Coordinator ETA (W2 — ETA Inquiries, Phase 1)  
**Coverage:** All four systems in brief + full Aurum Billing constraint analysis + assumption register

---

## 1. SYSTEM LANDSCAPE

| System | Type | Hosting | API | Key data owned | Relevance to ETA agent | Risk |
|---|---|---|---|---|---|---|
| **Salesforce CRM** | Modern CRM | Cloud (SaaS) | REST API (confirmed available) | Customer records, case history, consignment status, delivery status, route codes | **PRIMARY** — all consignment lookups + escalation case creation | MEDIUM (status freshness unknown) |
| **Driver App** | In-house mobile (iOS/Android) | Internal (cloud backend assumed) | API surface **unconfirmed** | GPS position, route sequence, scan-on-delivery events, driver-to-dispatch messaging | **PRIMARY** — ETA generation depends on driver location + response | HIGH (API surface undefined) |
| **Dispatch Console** | Java desktop via Citrix | On-prem | Limited API ("limited" undefined) | Route assignments, driver allocations, exception triage | OUT OF SCOPE for Phase 1 (W2 only). Relevant for W3 and W1 Phase 2 | HIGH for W3 (read/write capability unconfirmed) |
| **Aurum Billing** | Legacy on-prem ERP (Oracle, 2008) | On-prem | **No API. Batch CSV exports only (02:00–04:00 GMT daily)** | Invoices, fuel surcharges, credits, disputes, reconciliation, customer master | OUT OF SCOPE for Phase 1 (W2 only). Critical constraint for W4 Phase 2 | **CRITICAL** for W4 (batch latency + schema drift) |

---

## 2. DATA INVENTORY — ETA AGENT (W2, Phase 1)

### 2.1 Data inputs to the agent

| Data element | Source system | Access method | Freshness | Required? | Risk |
|---|---|---|---|---|---|
| Consignment ID | Customer (SMS/call/app) | Direct input | Real-time | YES | Low — agent receives it directly |
| Consignment status | Salesforce CRM | REST API (GET /consignment/{id}) | **Unknown — estimated 5–10 min lag from driver app sync** | YES — determines agent decision branch | MEDIUM — stale status produces wrong reply |
| Route code | Salesforce CRM | REST API | Same as status | Conditional | MEDIUM — needed for fallback ETA window calculation |
| Customer record + contact channel | Salesforce CRM | REST API | Near real-time (CRM-native) | YES — reply channel must match inquiry channel | LOW |
| VIP / contract flag | Salesforce CRM (customer master) | REST API | Near real-time | Conditional — needed to decide optional escalation path | LOW |
| Driver current GPS position | Driver App | **API surface unconfirmed** | Real-time (GPS) or message-based (async) | Conditional — needed for tight ETA | **HIGH — if no GPS API, agent must fall back to driver-message pattern only** |
| Driver next-drop sequence | Driver App | **API surface unconfirmed** | Real-time (route loaded at start of shift) | Conditional — needed to estimate drop order | HIGH |

### 2.2 Data outputs from the agent

| Data element | Target | Method | Notes |
|---|---|---|---|
| ETA reply to customer | Customer via original inquiry channel | SMS / push / CRM case reply | Must use same channel as inquiry (SMS → SMS, etc.) |
| Escalation case | Salesforce CRM | REST API (POST /case) | Created with category "ETA_ESCALATION", assigned to dispatcher queue |
| Driver non-response log | Internal analytics store | Agent audit log (structured JSON) | Required for weekly KPI reporting — driver response rate metric |
| Cache entry | Agent local cache | In-memory or Redis | 1h TTL; deduplicate repeat inquiries for same consignment |

### 2.3 Data NOT needed by ETA agent (Phase 1)

The ETA agent intentionally **does not access** Aurum Billing. The consignment lookup, status classification, and ETA generation are all served from CRM + Driver App. Any ETA inquiry that reveals a billing dispute (e.g., customer asks ETA but mentions a disputed invoice) is escalated to a human case with a CRM note — the agent does not attempt to cross-reference Aurum data.

---

## 3. AURUM BILLING — DEDICATED CONSTRAINT ANALYSIS

*Required by brief: "The legacy billing system constraints are part of this — address them, don't hand-wave."*

### 3.1 Batch file catalogue (from Artefact 5 + sample CSVs)

| File | Lag | Frequency | Schema observed | Key fields |
|---|---|---|---|---|
| `APEX_BILL_DAILY` | T-1 (yesterday's invoices) | Daily | INVOICE_NO, CUSTOMER_ID, CUSTOMER_NAME, INVOICE_DT, AMT_NET, AMT_FUEL_SURCH, AMT_VAT, AMT_GROSS, ROUTE_CODE, DEPOT | Primary billing record |
| `APEX_FUEL_SURCH` | T-1 | Daily | INVOICE_NO, ROUTE_CODE, FUEL_RATE_TIER, BASE_NET, FUEL_PCT, FUEL_AMT, CALC_TIMESTAMP, CALC_USER | Fuel surcharge calculation detail |
| `APEX_CREDITS` | T-1 | Daily | CREDIT_ID, INVOICE_NO, CUSTOMER_ID, CREDIT_AMT, REASON_CODE, APPROVER_ID, AUDIT_REF, APPLIED_DT | Credits applied to invoices |
| `APEX_DISPUTES_OPEN` | T-1 | Daily | DISPUTE_ID, INVOICE_NO, CUSTOMER_ID, OPEN_DT, DISPUTE_TYPE, DISPUTE_AMT, ASSIGNED_TO, STATUS, LAST_UPDT | Open dispute register |
| `APEX_RECON` | **T-2** (24h behind invoice generation) | Daily | RECON_ID, INVOICE_NO, EXPECTED_AMT, RECEIVED_AMT, VAR, AGEING_DAYS, FLAG | Payment reconciliation |
| `APEX_AGED_RECEIVABLES` | Weekly (Friday) | Weekly | CUSTOMER_ID, AGE_0_30, AGE_31_60, AGE_61_90, AGE_OVER_90, TOTAL_OPEN | Overdue balances by customer |
| `APEX_CUSTOMER_MASTER` | Monthly (1st of month) | Monthly | CUSTOMER_ID, CUSTOMER_NAME, ACCT_OPEN_DT, CONTRACT_TYPE, RATE_CARD, CR_LIMIT, ACCT_MGR, STATUS | Customer static data |

**Batch delivery window:** 02:00–04:00 GMT daily. Files are written to `/exports/aurum/`. No delivery confirmation mechanism stated — whether files arrive is not guaranteed.

### 3.2 What an agent CAN do with Aurum batch data

| Capability | Mechanism | Latency | Value |
|---|---|---|---|
| Detect open disputes older than X days | Query `APEX_DISPUTES_OPEN`; filter by OPEN_DT + STATUS | T-1 (yesterday's data) | Can triage aging disputes for human follow-up |
| Identify pattern customers (repeat disputes) | Group `APEX_DISPUTES_OPEN` by CUSTOMER_ID; count disputes | T-1 | Hayes & Sons (C-04451) has 3 open FUEL_SURCH_DAMAGE disputes — agent can surface this pattern |
| Cross-reference credit application vs. dispute status | Join `APEX_CREDITS` + `APEX_DISPUTES_OPEN` on INVOICE_NO | T-1 | Can flag disputes where credit has been applied but dispute status not updated to RESOLVED |
| Alert on RECON variance above threshold | Filter `APEX_RECON` by VAR < -£X and FLAG = DISPUTE_OPEN | T-2 (24h lag) | Can surface large reconciliation gaps for investigation |
| Detect audit trail gaps | Check `APEX_CREDITS` for rows with AUDIT_REF = NULL or missing | T-1 | Directly addresses the compliance risk exposed in Artefact 2 |

### 3.3 What an agent CANNOT do with Aurum batch data

| Capability | Reason | Impact |
|---|---|---|
| Modify an invoice in real-time | No API. Invoice modification requires a manual ticket to Aurum support (48h turnaround) | Phase 2 billing agent cannot self-close a dispute by applying a credit — it must escalate to a human who raises the support ticket |
| Check if a credit has been applied to a dispute today | T-1 batch lag means credits applied this morning won't appear until tomorrow's export | Agent may incorrectly show a dispute as "unresolved" when a credit was actually applied hours ago |
| Verify fuel surcharge calculation against current rate card | Rate card data is in `APEX_CUSTOMER_MASTER` (monthly export). FUEL_RATE_TIER changes are not surfaced until the next monthly file | Surcharge dispute resolution depends on data that may be up to 30 days stale |
| Detect a schema change before it breaks the batch ingestion | Schema changes "happen quarterly without prior notice" | A field rename in `APEX_FUEL_SURCH` would silently produce NULLs in the agent's surcharge calculation — wrong outputs with no error |

### 3.4 Critical data integrity observation (from sample data)

**Artefact 2 shows Sandra applied a £170 goodwill credit to INV-2026-04318 (Hayes & Sons, D-2026-00342) on day 6 of the email thread. Internal note: "no entry in the credits audit log."**

Examining the `APEX_CREDITS` export for 2026-04-14:
- CR-2026-00814 shows a £88 GOODWILL credit for C-04451 (Hayes & Sons) with APPROVER_ID U-0089 and AUDIT_REF AUD-2026-00212. This is a different credit amount and different invoice than Sandra's £170.
- There is no CR entry for INV-2026-04318 (the disputed invoice) in the credits file. Sandra's £170 credit is absent.

**Interpretation:** Sandra applied the credit via a path that bypasses Aurum's structured credit entry process. The AUDIT_REF field exists in the schema — suggesting credits *should* be audited — but manual overrides can be applied in a way that skips the export. This is a known compliance exposure. Any Phase 2 billing agent must treat `APEX_CREDITS` as incomplete: it captures structured credits only, not manual overrides.

### 3.5 Fuel surcharge data anomaly

`APEX_FUEL_SURCH` for 2026-04-14 shows three invoices on route R-008 (all tier T3) with different FUEL_PCT values: 11.97%, 9.37%, 12.00%. If T3 is a fixed tier, the percentage should be constant. This suggests either:
1. The fuel percentage within a tier varies by contract (RATE_CARD determines actual %) — not documented in the brief
2. There is a calculation inconsistency in the Aurum batch job

**Impact:** A Phase 2 billing agent that attempts to verify fuel surcharge accuracy will produce incorrect results unless the per-contract rate calculation logic is exposed. This is an assumption to validate with Sarah (see D6 Q5).

### 3.6 Schema drift risk (historical precedent)

The prior RPA project for billing reconciliation "broke whenever Aurum's schema changed." This is not hypothetical — it happened. For any agent ingesting Aurum batch files:

- **Minimum mitigation:** Schema validation step at ingestion (column count, column names, data types) that alerts before parsing
- **Ideal mitigation:** A schema contract (expected columns + types as a config file) checked against each daily export; failures halt processing and alert the billing team
- **Without mitigation:** A quarterly schema change silently corrupts 24h of dispute/credit data before anyone notices

---

## 4. SYSTEMS NOT DETAILED IN THE BRIEF

These systems are implied by the work streams but not named. Each is an assumption requiring validation.

| Implied system | Why implied | Assumption | Confidence | Test |
|---|---|---|---|---|
| **Insurance/claims system** | Damaged consignment exceptions (W1) require insurance involvement to resolve. Artefact 2 shows Hayes & Sons dispute involves a damaged pallet. | An insurance or claims tracking system exists; or claims are handled entirely within CRM case notes | LOW | Ask Sarah: "Where do damage insurance claims get tracked after a customer reports them?" |
| **Route optimisation engine** | Dispatch adjustments (W3) require re-routing logic. The dispatch console is described as "route planning" but the computational engine behind it is unnamed. | Route optimisation is embedded in the dispatch console or handled by a third-party SaaS | LOW | Ask Sarah: "When a driver is diverted, does someone manually re-sequence the route, or does the system suggest a new sequence?" |
| **SMS/contact platform** | Artefact 3 shows an SMS inquiry. The CRM doesn't natively handle SMS for inbound inquiries — a middleware or SMS gateway is implied. | Apex has a third-party SMS platform (Twilio or similar) or the carrier app handles this | MEDIUM | Ask Sarah: "When a customer texts your ETA line, what system receives that message before it reaches an agent?" |
| **VIP/SLA tier flag in CRM** | D4 escalation protocol specifies "if VIP flag" as optional escalation condition for tight ETAs. | Salesforce CRM has a customer tier or VIP field per account | LOW | Ask Sarah: "Do you have any tier or priority classification on customer accounts in Salesforce?" |

---

## 5. INTEGRATION RISKS (ETA AGENT, PHASE 1)

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Driver App has no programmatic API — only in-app messaging | MEDIUM | HIGH — removes GPS-based ETA calculation; agent must rely solely on driver reply | Escalation protocol is already designed for driver non-response; fallback window covers this. Accept if confirmed. |
| CRM delivery status updates are end-of-shift (not real-time) | MEDIUM | HIGH — "out-for-delivery" status could be hours old; ETA accuracy degrades | Include staleness disclosure in agent reply: "Status as of [last-updated timestamp]" |
| Salesforce REST API rate limits hit during peak inquiry period (400/day, AM cluster) | LOW | MEDIUM — API calls throttled; response time increases | Implement inquiry queue with async response; set customer expectation to "within 5 min" rather than instant |
| Driver app messaging channel unavailable (driver phone offline) | HIGH (routine) | LOW — already handled by 2-min wait + fallback window | No change needed; fallback is the primary response for non-responsive drivers |
| CRM consignment ID format mismatch (customer says "AX771" vs CRM stores "AX-771-3344") | MEDIUM | MEDIUM — lookup fails; escalation triggered unnecessarily | Normalisation step at input: strip hyphens, validate prefix, try multiple format variants before declaring not-found |

---

## 6. ASSUMPTION REGISTER

| # | Assumption | Confidence | What changes if wrong | How to test |
|---|---|---|---|---|
| A1 | CRM delivery status is updated from driver app in near-real-time (≤10 min lag) | **MEDIUM** | If end-of-day batch, "out-for-delivery" status is unreliable; agent must disclose staleness or escalate all active deliveries | D6 Q2 |
| A2 | Driver App has a programmatic API that allows the agent to query driver location and send messages | **LOW** | If message-only (no GPS API), ETA calculation is limited to driver-reported location; tight ETAs are not possible without driver cooperation | D6 Q1 |
| A3 | Salesforce CRM is the single source of truth for consignment status (driver app events sync to CRM, not to a separate system) | **MEDIUM** | If driver app has its own status store not synced to CRM, the agent is reading stale data from the wrong system | D6 Q2 |
| A4 | The 400/day ETA inquiry volume is representative of a typical day; peak days do not exceed 2× (i.e., ~800) | **MEDIUM** | If peaks are 3–5× (e.g., pre-holiday), agent SLA targets require revisiting | D6 Q8 |
| A5 | Aurum batch files arrive reliably every morning by 06:00 GMT (after the 02:00–04:00 write window) | **LOW** | If batch delivery fails silently, any Phase 2 agent working from batch data has no data without knowing it | D6 Q4 |
| A6 | The `APEX_CREDITS` batch export captures all credits — including manual overrides | **LOW** — contradicted by Artefact 2 | If manual overrides bypass the export, credits file is incomplete; Phase 2 billing agent will misidentify resolved disputes as open | D6 Q3 |
| A7 | Aurum is managed by an external vendor (not self-hosted by Apex IT) and schema changes originate externally | **MEDIUM** | If Apex IT controls the schema, they can provide advance notice of changes internally — lower risk than assumed | D6 Q4/Q11 |
| A8 | The fuel surcharge percentage within a tier is fixed (e.g., T3 = 12%) and the observed variation in sample data is a data quality issue | **LOW** | If fuel % is contract-specific within a tier, surcharge calculation requires per-customer rate card lookup — much more complex | D6 Q5 |
| A9 | Customer inquiry channel (SMS, phone, app) is recorded in the Salesforce CRM case so the agent can reply on the correct channel | **MEDIUM** | If channel is not recorded in CRM, agent must default to one channel (e.g., SMS) and may mis-route replies | D6 Q10 |
| A10 | The dispatch console "limited API" at minimum supports read queries for route and driver assignment data | **LOW** — "limited" is vague | If no API at all (screen-scraping only via Citrix), W3 automation and W1 Phase 2 have no viable build path | D6 Q6 |
