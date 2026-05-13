"""Generate Gate 3 presentation — MedFlex, Candidate Ranking & Parallel Outreach."""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

NAVY   = RGBColor(0x1B, 0x3A, 0x6B)
BLUE   = RGBColor(0x2E, 0x5F, 0xA3)
ORANGE = RGBColor(0xE3, 0x6B, 0x2A)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
DARK   = RGBColor(0x2D, 0x2D, 0x2D)
MID    = RGBColor(0x60, 0x60, 0x60)
LGREY  = RGBColor(0xF2, 0xF4, 0xF7)
GREEN  = RGBColor(0x1A, 0x7A, 0x3C)
RED    = RGBColor(0xBF, 0x35, 0x2A)
AMBER  = RGBColor(0xCC, 0x84, 0x00)
TEAL   = RGBColor(0x0E, 0x7C, 0x7B)
LBLUE  = RGBColor(0xBB, 0xCC, 0xEE)
DBLUE2 = RGBColor(0x23, 0x52, 0x96)
LGREEN = RGBColor(0xD6, 0xEE, 0xDC)
LRED   = RGBColor(0xF7, 0xDC, 0xDA)
LAMBER = RGBColor(0xFD, 0xF0, 0xD5)
LTEAL  = RGBColor(0xD0, 0xED, 0xEC)

prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
TOTAL = 6


def new_slide():
    return prs.slides.add_slide(BLANK)

def rect(s, x, y, w, h, color):
    sh = s.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = color
    sh.line.fill.background()
    return sh

def txt(s, text, x, y, w, h, size=14, bold=False, color=DARK,
        align=PP_ALIGN.LEFT, italic=False):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.italic = italic
    return tb

def mtxt(s, x, y, w, h, lines):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    first = True
    for (text, size, bold, color, align, italic) in lines:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = align
        run = p.add_run()
        run.text = text
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = color
        run.font.italic = italic
    return tb

def header(s, title, subtitle=None):
    rect(s, 0, 0, 13.33, 1.25, NAVY)
    txt(s, title, 0.38, 0.07, 12.5, 0.7, size=26, bold=True, color=WHITE)
    if subtitle:
        txt(s, subtitle, 0.38, 0.77, 12.5, 0.42, size=12, color=LBLUE)

def slide_number(s, n):
    txt(s, f"{n} / {TOTAL}", 12.6, 7.15, 0.65, 0.3,
        size=9, color=MID, align=PP_ALIGN.RIGHT)


# ═══════════════════════════════════════════════════════════
# SLIDE 1 — TITLE
# ═══════════════════════════════════════════════════════════
s = new_slide()
rect(s, 0, 0, 13.33, 7.5, NAVY)
rect(s, 0, 4.8,  13.33, 2.7,  DBLUE2)
rect(s, 0, 2.82, 13.33, 0.07, ORANGE)

txt(s, "MEDFLEX  ·  GATE 3  ·  AGENTIC STAFFING",
    0.55, 0.32, 12.2, 0.42, size=10, color=LBLUE, bold=True)
txt(s, "Candidate Ranking\n& Parallel Outreach",
    0.55, 0.82, 12.0, 1.9, size=42, bold=True, color=WHITE)
txt(s, "From brief to specification to build to reflection — "
       "what was delivered, what the build revealed, and what I would do differently.",
    0.55, 2.95, 11.5, 0.6, size=13, color=LBLUE)

rect(s, 0.55, 5.0, 3.5, 1.72, ORANGE)
txt(s, "9 deliverables",
    0.72, 5.08, 3.2, 0.52, size=18, bold=True, color=WHITE)
txt(s, "D1 – D9  ·  Problem to reflection\nWorking Python build  ·  18 passing tests",
    0.72, 5.56, 3.2, 1.05, size=12, color=WHITE)

mtxt(s, 4.35, 5.12, 8.5, 1.45, [
    ("Two capabilities built and specified to production grade:", 13, True, LBLUE, PP_ALIGN.LEFT, False),
    ("Candidate ranking — 6-factor urgency-weighted scoring, specialist credential hard-split",
     12, False, LBLUE, PP_ALIGN.LEFT, False),
    ("Parallel outreach — simultaneous contact, adaptive response windows, shallow pool escalation",
     12, False, LBLUE, PP_ALIGN.LEFT, False),
    ("",  5, False, WHITE, PP_ALIGN.LEFT, False),
    ("Presenter: Ann O'Hagan  ·  2026-05-13",
     10, False, RGBColor(0x88, 0x99, 0xBB), PP_ALIGN.LEFT, False),
])


# ═══════════════════════════════════════════════════════════
# SLIDE 2 — THE SCENARIO
# ═══════════════════════════════════════════════════════════
s = new_slide()
rect(s, 0, 0, 13.33, 7.5, LGREY)
header(s, "The Scenario — MedFlex",
       "Healthcare staffing. Coordinators filling nurse shifts manually, one call at a time.")
slide_number(s, 2)

# Left: situation
rect(s, 0.35, 1.38, 6.1, 0.4, NAVY)
txt(s, "The situation", 0.5, 1.41, 5.85, 0.34, size=12, bold=True, color=WHITE)
rect(s, 0.35, 1.78, 6.1, 2.5, WHITE)
mtxt(s, 0.5, 1.85, 5.85, 2.35, [
    ("MedFlex places nurses into hospital shifts. When a shift needs filling, coordinators "
     "manually call or message nurses one at a time until someone confirms.",
     11, False, DARK, PP_ALIGN.LEFT, False),
    ("", 5, False, DARK, PP_ALIGN.LEFT, False),
    ("For urgent fills (≤4h window), this is slow and unreliable. A coordinator who "
     "contacts nurses sequentially may burn through the fill window before getting a confirmation.",
     11, False, DARK, PP_ALIGN.LEFT, False),
    ("", 5, False, DARK, PP_ALIGN.LEFT, False),
    ("Kim's team (operations) owns the hospital relationship. The agent must never "
     "contact the hospital directly — all communication routes through the coordinator.",
     11, True, NAVY, PP_ALIGN.LEFT, False),
])

# Right: constraints
rect(s, 6.7, 1.38, 6.28, 0.4, NAVY)
txt(s, "Key constraints", 6.85, 1.41, 6.03, 0.34, size=12, bold=True, color=WHITE)

constraints = [
    (ORANGE, "6-week board deadline",
     "Marcus pushed from 8 to 6 weeks mid-engagement. Plan restructured before the first draft was finalised."),
    (AMBER, "Credential verification: Wave 2 only",
     "Removed from Wave 1 at Marcus's request. Consistent with the original conditional design — not a concession, a confirmation."),
    (TEAL, "Pilot criteria",
     "Standard fills >24h only. 2–3 coordinators. 2–3 established hospital accounts. Coordinator approves all placements."),
]
for i, (color, title, body) in enumerate(constraints):
    by = 1.78 + i * 1.3
    rect(s, 6.70, by, 0.38, 1.18, color)
    rect(s, 7.08, by, 5.90, 1.18, WHITE)
    txt(s, title, 7.22, by + 0.08, 5.62, 0.34, size=11, bold=True, color=DARK)
    txt(s, body,  7.22, by + 0.42, 5.62, 0.68, size=10, color=MID)

# Bottom: what was asked
rect(s, 0.35, 4.42, 12.63, 0.38, ORANGE)
txt(s, "What was asked: run a full ATX engagement — problem framing, architecture, production capability specs, build loop, client response, validation plan, and reflections.",
    0.50, 4.45, 12.35, 0.32, size=11, bold=True, color=WHITE)
rect(s, 0.35, 4.80, 12.63, 1.85, WHITE)
mtxt(s, 0.5, 4.88, 12.35, 1.7, [
    ("Two capabilities were selected for specification and build: candidate ranking and parallel outreach. "
     "These are the two capabilities most directly responsible for fill time reduction — the primary metric "
     "for the board presentation.", 11, False, DARK, PP_ALIGN.LEFT, False),
    ("", 5, False, DARK, PP_ALIGN.LEFT, False),
    ("Wave 2 (credential recency checking, no-show backfill, pre-shift mismatch detection) is condition-triggered: "
     "it starts at month 5 if first-recommendation acceptance rate reaches ≥90% over 60 days.",
     11, False, MID, PP_ALIGN.LEFT, True),
])


# ═══════════════════════════════════════════════════════════
# SLIDE 3 — WHAT WAS DELIVERED
# ═══════════════════════════════════════════════════════════
s = new_slide()
rect(s, 0, 0, 13.33, 7.5, LGREY)
header(s, "What Was Delivered — D1 to D9",
       "Nine deliverables. Problem to specification to build to reflection.")
slide_number(s, 3)

deliverables = [
    (NAVY,   "D1", "Problem framing",       "Success metrics and 6-week delivery timeline with pilot selection criteria"),
    (NAVY,   "D2", "Engagement intake",      "Scope definition, Wave 1 vs Wave 2 boundary, stakeholders"),
    (NAVY,   "D3", "Architecture + ADRs",    "Agentic architecture, 2 ADRs with alternatives and revisit conditions"),
    (ORANGE, "D4a", "Candidate ranking spec", "Production-grade: 11 rules, scoring formula, delegation boundaries, governance"),
    (ORANGE, "D4b", "Parallel outreach spec", "Production-grade: 12 rules, channel retry, escalation SLAs, integration contracts"),
    (TEAL,   "D5", "Build-loop memo",        "5 signals from the build — 4 spec gaps, 1 unjustified implementation choice"),
    (TEAL,   "D6", "Client feedback response","Email to Marcus: 6-week timeline, credential verification, failure path"),
    (GREEN,  "D7", "Validation plan",         "10 pre-production tests, 6 agent decision scenarios, 8 integration tests"),
    (GREEN,  "D8", "Reflection",              "Honest account: confirm timeline early, involve Kim, test error handling rules"),
    (GREEN,  "D9", "Self-spec build loop",    "What the build revealed about gaps I did not see when writing the spec"),
]

col_w = 6.05
for i, (color, label, title, body) in enumerate(deliverables):
    col = i % 2
    row = i // 2
    bx = 0.35 + col * 6.48
    by = 1.38 + row * 1.18
    rect(s, bx,        by, 0.65, 1.05, color)
    txt(s, label, bx + 0.04, by + 0.28, 0.57, 0.5, size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    rect(s, bx + 0.65, by, col_w - 0.65, 1.05, WHITE)
    txt(s, title, bx + 0.8, by + 0.07, col_w - 0.85, 0.34, size=11, bold=True, color=DARK)
    txt(s, body,  bx + 0.8, by + 0.44, col_w - 0.85, 0.54, size=10, color=MID)

# Python build callout
rect(s, 0.35, 7.1, 12.63, 0.32, NAVY)
txt(s, "Python build: candidate_ranking.py  ·  18 passing tests  ·  run with: pytest medflex_agent/tests/",
    0.5, 7.13, 12.35, 0.26, size=10, bold=True, color=LBLUE)


# ═══════════════════════════════════════════════════════════
# SLIDE 4 — KEY DESIGN DECISIONS DEFENDED
# ═══════════════════════════════════════════════════════════
s = new_slide()
rect(s, 0, 0, 13.33, 7.5, LGREY)
header(s, "Four Design Decisions — and Why",
       "Each one was a deliberate choice. Here is the rationale for each.")
slide_number(s, 4)

decisions = [
    (GREEN, "Specialist credential config owned by Linda, not hardcoded in the spec",
     "The original spec listed specialist credentials as a fixed list — written by me, not the compliance team.",
     "If that list was wrong, every ranking decision on a specialist shift would be wrong. "
     "The config is now a compliance team input: Linda owns it, the agent reads it, and it can be updated without touching the code. "
     "The agent applies the rules; it does not decide what counts as a specialist credential."),

    (ORANGE, "Wave 1 scope: candidate ranking + parallel outreach only",
     "Could have included credential verification, no-show backfill, pre-shift mismatch detection in Wave 1.",
     "6 weeks is enough to demonstrate fill time and first-recommendation acceptance rate — the two metrics the board needs. "
     "Adding more capabilities adds more integration risk without adding more evidence. "
     "Wave 2 is condition-triggered: it starts when the pilot data supports it, not on a fixed date."),

    (TEAL, "Escalation always goes to coordinator — agent never contacts the hospital directly",
     "The agent could theoretically contact the hospital in a pool_exhausted scenario.",
     "The hospital relationship belongs to Kim's team. If the agent contacts the hospital independently, "
     "it undermines that relationship and may contradict what the coordinator was already managing. "
     "The agent pre-drafts the status message and surfaces the remaining pool state; the coordinator makes the call."),

    (AMBER, "Pilot: standard fills >24h only, 2–3 coordinators, established accounts",
     "Could have run the pilot across all fill types from day 1.",
     "Urgent fills (≤4h) have the highest stakes. A ranking failure on a 2-hour fill has more consequences "
     "than on a 48-hour fill. The pilot starts where the consequences of error are lowest. "
     "If the >24h fills validate the design, expanding to urgent fills is a configuration change, not a rebuild."),
]

for i, (color, title, label, body) in enumerate(decisions):
    by = 1.38 + i * 1.47
    rect(s, 0.35, by, 0.22, 1.33, color)
    rect(s, 0.57, by, 12.41, 0.38, color)
    txt(s, title, 0.72, by + 0.05, 12.12, 0.30, size=11, bold=True, color=WHITE)
    rect(s, 0.57, by + 0.38, 12.41, 0.95, WHITE)
    txt(s, label, 0.72, by + 0.42, 4.5, 0.28, size=10, bold=True, color=DARK)
    txt(s, body,  0.72, by + 0.68, 11.88, 0.58, size=10, color=MID, italic=False)


# ═══════════════════════════════════════════════════════════
# SLIDE 5 — BUILD LOOP: WHAT IT REVEALED
# ═══════════════════════════════════════════════════════════
s = new_slide()
rect(s, 0, 0, 13.33, 7.5, LGREY)
header(s, "The Build Loop — What It Revealed",
       "Five signals from building the candidate ranking implementation against the spec.")
slide_number(s, 5)

# Key observation box
rect(s, 0.35, 1.38, 12.63, 0.72, NAVY)
mtxt(s, 0.5, 1.43, 12.35, 0.62, [
    ("Key observation: ", 12, True, WHITE, PP_ALIGN.LEFT, False),
    ("Claude Code asked no clarifying questions during the build. "
     "Gaps in the spec were resolved silently — I only found out what decisions had been made by reading the output. "
     "A builder who asks nothing either has a perfect spec, or has made undocumented assumptions. In this case, it was the latter.",
     12, False, LBLUE, PP_ALIGN.LEFT, False),
])

# Signal table header
rect(s, 0.35, 2.20, 12.63, 0.38, DBLUE2)
txt(s, "Signal",          0.50,  2.24, 5.80, 0.30, size=10, bold=True, color=WHITE)
txt(s, "Classification",  6.50,  2.24, 3.00, 0.30, size=10, bold=True, color=WHITE)
txt(s, "What the spec failed to say", 9.70, 2.24, 3.55, 0.30, size=10, bold=True, color=WHITE)

signals = [
    (RED,   "Proximity formula (1/(1+miles/10)) — reference distance invented by builder",
             "Unjustified implementation choice",
             "Spec named proximity as a factor but defined no scoring formula"),
    (AMBER, '"Within 10%" applied to composite score, not individual factors',
             "Spec gap",
             "Ambiguous — composite vs. per-factor comparison produce different rankings"),
    (AMBER, "CRM unavailable and missing data handled identically (median imputation)",
             "Spec gap",
             "No input mechanism to distinguish system down from data simply absent"),
    (AMBER, "System unavailability rules could not be implemented as written",
             "Spec gap",
             "Function had no way to be told whether a system was available or not"),
    (AMBER, "pool_exhausted payload contained no excluded_candidates list",
             "Spec gap",
             "Spec required this data in the payload; the output type had no field for it"),
]

row_colors = [WHITE, LGREY, WHITE, LGREY, WHITE]
for i, (sig_color, signal, classification, failure) in enumerate(signals):
    by = 2.58 + i * 0.86
    rect(s, 0.35, by, 12.63, 0.86, row_colors[i])
    rect(s, 0.35, by, 0.18, 0.86, sig_color)
    txt(s, signal,         0.62, by + 0.08, 5.70, 0.70, size=10, color=DARK)
    txt(s, classification, 6.50, by + 0.08, 2.95, 0.70, size=10, color=DARK, bold=(sig_color == RED))
    txt(s, failure,        9.70, by + 0.08, 3.50, 0.70, size=10, color=MID, italic=True)

# Fix applied note
rect(s, 0.35, 6.92, 12.63, 0.40, GREEN)
txt(s, "All five gaps addressed: scoring formula, rule 7 threshold, system availability inputs, "
       "and excluded_candidates field now defined in the updated D4a spec.",
    0.50, 6.95, 12.35, 0.32, size=10, bold=True, color=WHITE)


# ═══════════════════════════════════════════════════════════
# SLIDE 6 — WHAT I WOULD DO DIFFERENTLY
# ═══════════════════════════════════════════════════════════
s = new_slide()
rect(s, 0, 0, 13.33, 7.5, LGREY)
header(s, "What I Would Do Differently",
       "Six specific things — from the build loop, the client response, and the engagement overall.")
slide_number(s, 6)

learnings = [
    (RED,   "Spec writing",
     "Define output types before writing error handling rules",
     "If the output has no field for something I said should be in it, the rule cannot be delivered. "
     "I wrote 'include excluded candidates in the escalation payload' without checking whether the output supported it."),

    (RED,   "Spec writing",
     "For every 'if X is unavailable' rule, ask: how does the tool actually find out?",
     "I wrote rules for system unavailability without thinking about what signal the tool would receive. "
     "A rule that depends on information that is never passed in is not a rule — it is a wish."),

    (AMBER, "Spec writing",
     "Every ranking factor needs a formula, not just a name",
     "I listed proximity as a factor. I did not say how to convert distance into a number. "
     "That decision was made by the builder without asking me. Different formulas produce different rankings."),

    (AMBER, "Spec writing",
     "Ambiguous thresholds are false precision — define the calculation, not just the number",
     "'Within 10%' sounds specific. It is not. I needed to say what was being compared and how. "
     "The builder made a reasonable interpretation; it was not the only reasonable one."),

    (TEAL,  "Engagement management",
     "Confirm the board timeline before writing the plan",
     "Marcus told me the board meeting was in 6 weeks, not 8, after I had already structured the plan. "
     "That is a basic question I should have asked in the first conversation."),

    (GREEN, "Engagement management",
     "Involve operations (Kim) in discovery — not just leadership",
     "Kim was not in the discovery session. The failure path gap she spotted would have been "
     "caught in a 30-minute conversation. She was not difficult to reach; I just did not reach her."),
]

col_w = 6.05
for i, (color, category, title, body) in enumerate(learnings):
    col = i % 2
    row = i // 2
    bx = 0.35 + col * 6.48
    by = 1.38 + row * 1.95
    rect(s, bx, by, col_w, 0.30, color)
    txt(s, category, bx + 0.12, by + 0.04, col_w - 0.2, 0.22,
        size=9, bold=True, color=WHITE)
    rect(s, bx, by + 0.30, col_w, 1.55, WHITE)
    txt(s, title, bx + 0.15, by + 0.36, col_w - 0.25, 0.40,
        size=11, bold=True, color=DARK)
    txt(s, body,  bx + 0.15, by + 0.76, col_w - 0.25, 1.02,
        size=10, color=MID)


# ── Save ──────────────────────────────────────────────────
OUT = (r"C:\Users\AnnOHagan\OneDrive - EPAM\FDE AI Program"
       r"\FDE-practice-week2\FDE-practice-week2"
       r"\Week3_Docs\Gate3-MedFlex-Presentation.pptx")
prs.save(OUT)
print(f"Saved: {OUT}")
