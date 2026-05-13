# D6 — Client Feedback Response
**To:** Marcus Reyes, CEO, MedFlex  
**From:** Ann O'Hagan  
**Date:** 2026-05-15  
**Re:** Revised plan, 6-week timeline, credential scope, and failure path

---

Hi Marcus,

Thank you for the detailed feedback. All three points are addressed below, with the revised documents attached.

---

**On the 6-week timeline**

The plan has been restructured to 6 weeks. Parallel outreach and the coordinator approval gate, the two things you said you need to see working, are the core of Wave 1 and will be running on 20–30 live shifts by week 6. Credential recency checking, no-show backfill, and pre-shift mismatch detection move to Wave 2, with a condition-triggered start at month 5 once the pilot data meets the readiness thresholds.

One thing worth being clear about before Monday: the week 6 board deliverable will be directional data from a structured pilot, specifically fill time and first-recommendation acceptance rate, not proof of 10x capacity. That is the honest version of what 6 weeks can demonstrate, and going into the board meeting with a realistic claim is a stronger position than an overcommitted one that gets challenged.

---

**On credential verification**

Credential verification has been removed from Wave 1. The compliance team will continue under its current quarterly cadence during the pilot, and the known exposure window is accepted as a condition of the 6-week timeline.

Just to give you some context on this one: we had already flagged in the original design that credential verification was conditional on Linda confirming the root cause of the 7% mismatch rate. So removing it from Wave 1 is very much in line with our own thinking, and we are happy to take it out now. It is not going away permanently; it moves forward as soon as Linda gives us the confirmation we need.

---

**On the failure path**

Kim was right to raise this, and it was a genuine gap in the document. A failure path section is now in the architecture covering four specific scenarios: no confirmation within the outreach window, pool exhausted, parsing error caught at the coordinator approval gate, and no-show detected post-placement. The coordinator owns the hospital relationship in all failure cases. The agent pre-drafts the status message and surfaces the remaining pool state so the coordinator has everything they need to make that call within 15–30 minutes of escalation. The agent does not contact the hospital directly under any circumstances; that call belongs to Kim's team.

Kim's instinct to ask who manages the hospital conversation when things go wrong is exactly the right question for someone in her role, and the design is stronger for it.

---

The revised timeline, scope table, and failure path are in the updated documents. I am available to walk through any of this before Monday if that would be helpful.

Best Regards,  
Ann
