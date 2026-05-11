# W3D3 Build-Loop Exercise — Cascade Public Libraries
**Submitted by:** Ann OHagan

---

### Signal 1 — 72-hour notification window

**Classification:** Spec gap

**Rationale (1 sentence with citation):** R3 states "72 hours" without defining calendar vs business hours, and the Assumptions section explicitly flags this as unresolved — the builder implemented calendar hours, which matches the stated assumption, but that assumption has not been confirmed by the FDE.

**Response:**

I should have locked this down in R3 before the build. The builder did the right thing by following the stated assumption — this is on me, not them. Updating R3 to read: *"A notified patron has 72 calendar hours to claim the hold. The clock starts at the notification timestamp, regardless of library opening hours."* If the Cascade Libraries team later decides business hours is the right model (e.g. Sundays excluded), we revisit — but the builder should not be blocked on this. Confirm and proceed.

---

### Signal 2 — Accessibility priority implemented as 0.25x weight

**Classification:** Builder misread

**Rationale (1 sentence with citation):** R4 explicitly states accessibility-priority patrons "jump to queue position 1" — a position override, not a fractional weight — and the builder implemented `ACCESSIBILITY = 0.25` as a weight multiplier instead.

**Response:**

R4 specifies a direct position jump to 1, not a weight calculation. The `ACCESSIBILITY = 0.25` multiplier in `PriorityWeights` contradicts the spec — `raw_position × 0.25` is not the same as inserting at position 1. Please change `accessibility_priority.py` so that when a patron has `has_accessibility_modifier`, the system inserts their hold at position 1 directly on placement. The FIFO tie-break only applies when another accessibility-priority patron is already at position 1; in all other cases, position 1 is the hard output, not a weighted calculation.

---

### Signal 3 — Return reminder scheduled at loan end minus 3 days

**Classification:** Unjustified implementation choice

**Rationale (1 sentence with citation):** No requirement in the spec covers post-checkout return reminders — R7 specifies only that the loan is created automatically, and R10 covers the 21-day period and auto-return.

**Response:**

I can see the thinking here and it's not a bad idea, but the spec doesn't ask for return reminders and adding unspecified features in a build loop means we're shipping behaviour that hasn't been reviewed or tested as a requirement. Please remove the `schedule_reminder` call from `auto_checkout_handler.py`. If the team wants return reminders as a feature, raise it as a spec change — we can add it deliberately in the next iteration with proper acceptance criteria.

---

### Signal 4 — `test_overdrive_refresh.py` fails in 2026

**Classification:** Test/environment issue

**Rationale (1 sentence with citation):** The implementation correctly matches R8 (advance queue by N new copies), but the test fixture `overdrive_refresh_2025_q4.json` encodes Q4 2025 queue state in its `expected_advances` field, making the assertion time-dependent.

**Response:**

The implementation is correct — `on_overdrive_catalog_refresh` advances the queue by the count of added copies per title, which is exactly what R8 requires. The test is the problem, not the code. Refactor the test to assert relative advancement: capture `queue_count_before`, run the refresh, then assert `queue_count_after == queue_count_before + total_new_copies`. That assertion holds regardless of when the test runs. Do not touch the implementation.

---

### Signal 5 — Duplicate hold check blocks format-distinct holds

**Classification:** Builder misread

**Rationale (1 sentence with citation):** R11 explicitly states that ebook and audiobook holds on the same title are treated as two separate holds, both counting toward the limit — but the `patron_has_active_hold_on_title` check uses `title_id` alone, which would reject a patron who holds the ebook from also placing an audiobook hold on the same title.

**Response:**

R11 is explicit: ebook and audiobook editions of the same title are separate holds and both are permitted. The current duplicate guard checks `title_id` only, which directly contradicts R11 — a patron with an ebook hold would be blocked from placing an audiobook hold. Change the guard to check on `(title_id, format_type)` as a compound key so format-distinct holds on the same title are allowed through. The hold limit check on `active_count` is correct and doesn't need to change.

---

### Signal 6 — Email sent to paused patron when skipped

**Classification:** Unjustified implementation choice

**Rationale (1 sentence with citation):** R6 requires only that paused holds are skipped when a title becomes available — it says nothing about notifying the paused patron, and the builder added a "you've been skipped" email that the spec never requested.

**Response:**

R6 defines the behaviour for paused holds as skip-and-continue to the next eligible patron — there's no notification requirement for the paused patron. The "your hold is paused, so we've skipped over it" email is an addition the spec doesn't cover. Please remove it from `paused_holds.py`. If the team decides that skipped-patron notification is good UX, add it to R6 explicitly first — it needs a deliberate spec entry, an email template decision, and likely a test before it ships.

---

### Signal 7 — SMS-opted patrons receive SMS only, not email

**Classification:** Spec gap

**Rationale (1 sentence with citation):** R12 explicitly states "the business has not yet decided whether SMS-opted patrons should receive both email and SMS, or only SMS," and the Assumptions section confirms this is pending — the builder made a choice (SMS-only) that the spec intentionally left open.

**Response:**

I should have resolved the R12 channel question before the build started — this is a business decision I didn't close, and the builder reasonably picked one interpretation. I'm escalating to the Cascade Libraries product team this week. In the meantime, please implement email-only for all patrons as a safe placeholder — including SMS-opted patrons — so nothing ships on an unconfirmed assumption. Once the business decides, I'll update R12 and we can add the SMS path in the next iteration with the correct channel logic specified.

---

### Signal 8 — Builder question: Academic + Accessibility-priority intersection

**Classification:** Legitimate clarification request

**Rationale (1 sentence with citation):** The Assumptions section explicitly acknowledges this intersection is unresolved ("Pending FDE confirmation"), and the builder correctly identified three distinct interpretations before implementing — this is the builder doing their job, not a failure.

**Response:**

Good catch, and thank you for holding the PR rather than guessing. The intended behaviour is option (a): when a patron is both Academic and Accessibility-priority, R4 wins fully — they jump to position 1, and the Academic 0.5x weight is not applied at any stage. Updating the Assumptions section now to read: *"Academic + Accessibility-priority intersection: R4 wins. Patron jumps to position 1. The 0.5x Academic weight is not applied when R4 has been invoked — the two rules do not compound."* Please implement option (a) and unblock the PR.

---

## Reflection

The hardest diagnostic move for me was distinguishing Signal 6 (the paused patron email) from a design gap. At first it looked like a gap — R6 is silent on whether the paused patron should be notified, and a real patron would reasonably want to know they were skipped. But the key question is directional: did the builder *miss* something the spec required, or did they *add* something it didn't ask for? Once I ran that check, the answer was clear — the builder satisfied R6 correctly and added an unsolicited feature on top. Calling it a design gap would have been wrong, and the response would have been wrong too: I'd have updated the spec to fill a gap that isn't there, shipping undocumented behaviour as a confirmed requirement. The same logic applied to Signal 3. Recognising that the same category (unjustified implementation choice) could appear twice, for different-looking situations, was the part I would have missed without explicitly running the ownership question for each signal separately.
