# D6 — Client Feedback Response
**To:** Marcus Reyes, CEO, MedFlex
**From:** Ann OHagan
**Date:** 2026-05-15
**Re:** Revised plan — 6-week timeline, credential scope, and failure path

---

Marcus,

All three points are addressed below. The revised documents are attached.

---

**On the 6-week timeline**

You're right — 8 weeks doesn't work for a board update in 6. The plan has been restructured accordingly. Parallel outreach and the coordinator approval gate — the two things you said you need to see working — are the core of Wave 1 and will be live on 20–30 shifts by week 6. What moves out is credential recency checking, no-show backfill, and pre-shift mismatch detection; all three are now Wave 2, with a condition-triggered start at month 5 once the pilot data meets the readiness thresholds. The board deliverable at week 6 is directional data from live shifts — fill time and first-recommendation acceptance rate — not proof of 10x capacity, which Wave 1 was never designed to deliver.

---

**On credential verification**

Removed from Wave 1. The compliance team continues under its current quarterly cadence during the pilot; the known exposure window is accepted as a condition of the 6-week timeline. We have not confirmed with Linda that stale credentials are driving the 7% mismatch rate, and you're right that building against an unconfirmed root cause is the wrong call. I have also replaced the credential-scoping ADR — which was duplicating the Wave 1/Wave 2 table rather than making a genuinely architectural decision — with a contested design decision that directly affects build outcomes: whether candidate ranking should use agentic reasoning with stated rationale per candidate, or a deterministic sort with fixed weights. That is the decision that addresses coordinator trust and fill volume in Wave 1, and it is the one that needs to be in the architecture record.

---

**On the failure path**

Kim's question was the right one to ask and it exposed a real gap. A failure path section is now in the architecture covering four specific scenarios: no confirmation within the outreach window, pool exhausted, parsing error caught at the coordinator approval gate, and no-show detected post-placement. Each has a defined agent action, a coordinator action, and a hospital notification SLA. The short version: the coordinator owns the hospital relationship in all failure cases. The agent pre-drafts the status message and surfaces the remaining pool state so the coordinator has everything they need to make that call within 15–30 minutes of escalation. The agent does not contact the hospital directly under any circumstances — that call belongs to Kim's team.

---

The revised timeline, scope table, and failure path are in the updated documents. Let me know if you want to walk through any of this before Monday.

Ann
