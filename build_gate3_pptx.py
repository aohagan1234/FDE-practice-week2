"""Gate 3 presentation — MedFlex. Clean, readable, 10-minute coach call."""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

NAVY   = RGBColor(0x1B, 0x3A, 0x6B)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
DARK   = RGBColor(0x2D, 0x2D, 0x2D)
MID    = RGBColor(0x60, 0x60, 0x60)
LGREY  = RGBColor(0xF5, 0xF6, 0xF8)
ORANGE = RGBColor(0xE3, 0x6B, 0x2A)
GREEN  = RGBColor(0x1A, 0x7A, 0x3C)
RED    = RGBColor(0xBF, 0x35, 0x2A)
LBLUE  = RGBColor(0xBB, 0xCC, 0xEE)
RULE   = RGBColor(0xDD, 0xDD, 0xDD)

prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
TOTAL = 6


def slide():
    return prs.slides.add_slide(BLANK)

def box(s, x, y, w, h, color):
    sh = s.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = color
    sh.line.fill.background()
    return sh

def label(s, text, x, y, w, h, size=16, bold=False, color=DARK,
          align=PP_ALIGN.LEFT, italic=False):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    r.font.italic = italic
    return tb

def bullets(s, items, x, y, w, h, size=16, color=DARK, gap=0.0, bold_first=False):
    """items = list of strings; each gets its own paragraph."""
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, text in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        if gap and i > 0:
            sp = tf.add_paragraph()
            sp.space_before = Pt(gap)
        r = p.add_run()
        r.text = text
        r.font.size = Pt(size)
        r.font.color.rgb = color
        r.font.bold = (bold_first and i == 0)

def header(s, title, subtitle=None):
    box(s, 0, 0, 13.33, 1.1, NAVY)
    label(s, title, 0.45, 0.1, 12.4, 0.65, size=28, bold=True, color=WHITE)
    if subtitle:
        label(s, subtitle, 0.45, 0.72, 12.4, 0.34, size=13, color=LBLUE, italic=True)

def slide_num(s, n):
    label(s, f"{n} / {TOTAL}", 12.5, 7.15, 0.75, 0.28, size=10, color=MID, align=PP_ALIGN.RIGHT)

def rule_line(s, y):
    box(s, 0.45, y, 12.43, 0.02, RULE)

def dot(s, x, y, color=NAVY):
    box(s, x, y, 0.13, 0.13, color)


# ═══════════════════════════════════════════════════════════
# SLIDE 1 — TITLE
# ═══════════════════════════════════════════════════════════
s = slide()
box(s, 0, 0, 13.33, 7.5, NAVY)
box(s, 0, 5.8, 13.33, 0.06, ORANGE)

label(s, "MEDFLEX  ·  GATE 3", 0.55, 0.4, 12.0, 0.5,
      size=13, bold=True, color=LBLUE)
label(s, "Candidate Ranking\n& Parallel Outreach",
      0.55, 1.0, 11.5, 2.2, size=44, bold=True, color=WHITE)
label(s, "From brief to specification to build to reflection.",
      0.55, 3.25, 10.0, 0.5, size=16, color=LBLUE, italic=True)

box(s, 0.55, 4.15, 3.0, 1.4, ORANGE)
label(s, "9 deliverables\n18 passing tests",
      0.72, 4.28, 2.7, 1.1, size=18, bold=True, color=WHITE)

box(s, 3.85, 4.15, 9.0, 1.4, RGBColor(0x23, 0x52, 0x96))
bullets(s,
    ["Candidate ranking  —  6-factor urgency-weighted scoring",
     "Parallel outreach  —  simultaneous contact, adaptive response windows"],
    4.05, 4.3, 8.7, 1.1, size=14, color=WHITE)

label(s, "Ann O'Hagan  ·  2026-05-13",
      0.55, 6.2, 5.0, 0.4, size=11, color=LBLUE)


# ═══════════════════════════════════════════════════════════
# SLIDE 2 — THE SCENARIO
# ═══════════════════════════════════════════════════════════
s = slide()
box(s, 0, 0, 13.33, 7.5, WHITE)
header(s, "The Scenario", "MedFlex — healthcare staffing, nurse shifts, manual coordination")
slide_num(s, 2)

# Problem
label(s, "The problem", 0.45, 1.3, 4.0, 0.38, size=13, bold=True, color=NAVY)
rule_line(s, 1.68)
bullets(s, [
    "MedFlex places nurses into hospital shifts",
    "When a shift needs filling, coordinators contact nurses one at a time",
    "For urgent fills (≤4 hours), this is too slow — the window can expire before anyone confirms",
    "Kim's team owns the hospital relationship; the agent must never contact the hospital directly",
], 0.45, 1.75, 5.8, 2.8, size=15, color=DARK)

# Vertical divider
box(s, 6.6, 1.25, 0.04, 5.5, RULE)

# Constraints
label(s, "Key constraints going in", 6.85, 1.3, 6.0, 0.38, size=13, bold=True, color=NAVY)
rule_line(s, 1.68)

constraints = [
    (ORANGE, "6-week board deadline",
     "Marcus moved it from 8 weeks mid-engagement. Plan restructured before the first draft was finished."),
    (NAVY,   "Credential verification: Wave 2 only",
     "Removed from Wave 1 at Marcus's request — consistent with the original conditional design."),
    (GREEN,  "Pilot criteria",
     "Standard fills >24h only. 2–3 coordinators. Established hospitals. Coordinator approves all placements."),
]
for i, (color, title, body) in enumerate(constraints):
    by = 1.8 + i * 1.65
    box(s, 6.85, by, 0.1, 1.3, color)
    label(s, title, 7.1, by + 0.08, 5.9, 0.4, size=14, bold=True, color=DARK)
    label(s, body,  7.1, by + 0.52, 5.9, 0.72, size=13, color=MID, italic=True)


# ═══════════════════════════════════════════════════════════
# SLIDE 3 — WHAT WAS DELIVERED
# ═══════════════════════════════════════════════════════════
s = slide()
box(s, 0, 0, 13.33, 7.5, WHITE)
header(s, "What Was Delivered", "Nine deliverables across the full ATX engagement")
slide_num(s, 3)

col1 = [
    ("D1", NAVY,   "Problem framing",          "Success metrics + 6-week delivery timeline + pilot criteria"),
    ("D2", NAVY,   "Engagement intake",         "Scope, Wave 1 vs Wave 2 boundary, stakeholders"),
    ("D3", NAVY,   "Architecture + ADRs",       "Agent design with 2 ADRs — alternatives, consequences, revisit conditions"),
    ("D4a", ORANGE, "Candidate ranking spec",    "Production-grade: scoring formula, delegation boundaries, governance"),
    ("D4b", ORANGE, "Parallel outreach spec",    "Production-grade: channel retry order, escalation SLAs, integration contracts"),
]
col2 = [
    ("D5", RGBColor(0x0E,0x7C,0x7B), "Build-loop memo",           "5 signals: 4 spec gaps, 1 unjustified implementation choice"),
    ("D6", RGBColor(0x0E,0x7C,0x7B), "Client feedback response",  "Email to Marcus: timeline, credential verification, failure path"),
    ("D7", GREEN,  "Validation plan",           "10 pre-production tests + 6 agent scenarios + 8 integration tests"),
    ("D8", GREEN,  "Reflection",                "Honest account: timeline, Kim, error handling rules"),
    ("D9", GREEN,  "Self-spec build loop",       "What the build revealed about gaps I did not notice when writing the spec"),
]

for col_items, cx in [(col1, 0.45), (col2, 6.9)]:
    for i, (num, color, title, body) in enumerate(col_items):
        by = 1.28 + i * 1.18
        box(s, cx, by, 0.62, 1.0, color)
        label(s, num, cx, by + 0.28, 0.62, 0.45,
              size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        label(s, title, cx + 0.72, by + 0.08, 5.7, 0.38, size=13, bold=True, color=DARK)
        label(s, body,  cx + 0.72, by + 0.52, 5.7, 0.42, size=11, color=MID, italic=True)

box(s, 0, 7.18, 13.33, 0.32, NAVY)
label(s, "Python build: candidate_ranking.py  ·  18 passing tests  ·  pytest medflex_agent/tests/",
      0.45, 7.21, 12.4, 0.26, size=11, bold=True, color=LBLUE)


# ═══════════════════════════════════════════════════════════
# SLIDE 4 — KEY DESIGN DECISIONS
# ═══════════════════════════════════════════════════════════
s = slide()
box(s, 0, 0, 13.33, 7.5, WHITE)
header(s, "Four Design Decisions", "Each one was deliberate. Here is the rationale.")
slide_num(s, 4)

decisions = [
    (ORANGE, "Specialist credential config owned by Linda — not hardcoded",
     "My original spec listed specialist credentials. That list came from me, not the compliance team. "
     "If it was wrong, every specialist shift ranking was wrong. Now Linda owns the config; the agent reads it."),
    (NAVY,   "Wave 1 scope: candidate ranking + parallel outreach only",
     "6 weeks produces credible fill time and acceptance rate data. "
     "Adding more capabilities adds integration risk without adding more useful evidence for the board."),
    (GREEN,  "Agent never contacts the hospital directly — always through the coordinator",
     "Kim's team owns that relationship. An agent contacting the hospital independently "
     "can contradict what a coordinator was already managing."),
    (RGBColor(0x0E,0x7C,0x7B), "Pilot limited to standard fills >24h only",
     "A ranking failure on a 2-hour urgent fill has more consequences than on a 48-hour fill. "
     "Start where mistakes are cheapest to recover from. Expanding to urgent fills is a config change, not a rebuild."),
]

for i, (color, title, body) in enumerate(decisions):
    by = 1.25 + i * 1.5
    box(s, 0.45, by, 0.12, 1.25, color)
    label(s, title, 0.75, by + 0.08, 12.1, 0.42, size=15, bold=True, color=DARK)
    label(s, body,  0.75, by + 0.55, 12.1, 0.62, size=13, color=MID, italic=False)
    if i < 3:
        rule_line(s, by + 1.28)


# ═══════════════════════════════════════════════════════════
# SLIDE 5 — BUILD LOOP
# ═══════════════════════════════════════════════════════════
s = slide()
box(s, 0, 0, 13.33, 7.5, WHITE)
header(s, "The Build Loop — What It Revealed",
       "Five signals from building the candidate ranking implementation against my own spec.")
slide_num(s, 5)

# Key observation
box(s, 0.45, 1.25, 12.43, 0.78, LGREY)
box(s, 0.45, 1.25, 0.12, 0.78, ORANGE)
label(s, "No clarifying questions were asked during the build. "
         "Wherever my spec was unclear, the builder made a decision and moved on. "
         "I only found out what those decisions were by reading the output.",
      0.75, 1.35, 11.95, 0.58, size=14, color=DARK, italic=True)

# Table header
by = 2.2
box(s, 0.45, by, 12.43, 0.4, NAVY)
label(s, "What the builder did",         0.65, by + 0.07, 6.2, 0.28, size=12, bold=True, color=WHITE)
label(s, "Classification",               7.05, by + 0.07, 2.8, 0.28, size=12, bold=True, color=WHITE)
label(s, "What my spec failed to say",   10.0, by + 0.07, 2.8, 0.28, size=12, bold=True, color=WHITE)

rows = [
    (RED,    "Invented a formula for scoring proximity — using a reference distance I never specified",
             "Unjustified\nimplementation choice", "I listed proximity as a factor but never said how to turn distance into a score"),
    (ORANGE, '"Within 10%" applied to overall score, not to each individual factor',
             "Spec gap",                           "My wording sounded specific but did not say what was being compared"),
    (ORANGE, "CRM unavailable and missing data treated identically",
             "Spec gap",                           "No way to distinguish system down from data simply not existing for that nurse"),
    (ORANGE, "System unavailability rules could not be followed as written",
             "Spec gap",                           "The tool had no way of being told whether a system was available or not"),
    (ORANGE, "Escalation payload had no space for excluded candidates list",
             "Spec gap",                           "I said include it; the output I designed had no field for it"),
]

bgcolors = [WHITE, LGREY, WHITE, LGREY, WHITE]
for i, (sig_color, signal, classification, failure) in enumerate(rows):
    ry = 2.6 + i * 0.84
    box(s, 0.45, ry, 12.43, 0.84, bgcolors[i])
    box(s, 0.45, ry, 0.12,  0.84, sig_color)
    label(s, signal,         0.68, ry + 0.14, 6.2,  0.56, size=12, color=DARK)
    label(s, classification, 7.05, ry + 0.14, 2.75, 0.56, size=12, color=DARK, bold=True)
    label(s, failure,        10.0, ry + 0.14, 2.75, 0.56, size=11, color=MID, italic=True)

box(s, 0.45, 6.82, 12.43, 0.4, GREEN)
label(s, "All five gaps fixed in the updated D4a spec — scoring formula, rule 7 threshold, "
         "system availability inputs, excluded_candidates field.",
      0.65, 6.88, 12.1, 0.3, size=12, bold=True, color=WHITE)


# ═══════════════════════════════════════════════════════════
# SLIDE 6 — WHAT I'D DO DIFFERENTLY
# ═══════════════════════════════════════════════════════════
s = slide()
box(s, 0, 0, 13.33, 7.5, WHITE)
header(s, "What I Would Do Differently",
       "Four things from the spec. Two things from how I ran the engagement.")
slide_num(s, 6)

label(s, "Spec writing", 0.45, 1.25, 6.0, 0.35, size=13, bold=True, color=ORANGE)
rule_line(s, 1.6)

spec_items = [
    ("Define the output type before writing the error handling rule",
     "If the output has no field for something, the rule can't be delivered. I required excluded candidates "
     "in the escalation payload — but the output I designed had nowhere to put them."),
    ("For every 'if X is unavailable' rule, ask: how does the tool actually find out?",
     "I wrote rules about what to do when systems were down. The tool had no signal telling it a system was down. "
     "The rule existed; the mechanism did not."),
    ("Every ranking factor needs a formula, not just a name",
     "I listed proximity as a factor and did not say how to convert distance into a score. "
     "The builder made a choice I would not have made if I had been asked."),
    ("'Within 10%' is not specific — define what is being compared",
     "It sounds precise. It is not. I needed to say: compare the overall scores, "
     "and boost only if the gap between them is 10% or less."),
]
for i, (title, body) in enumerate(spec_items):
    by = 1.65 + i * 1.12
    dot(s, 0.45, by + 0.1, ORANGE)
    label(s, title, 0.72, by,       5.95, 0.38, size=13, bold=True, color=DARK)
    label(s, body,  0.72, by + 0.42, 5.95, 0.62, size=11, color=MID)

# Vertical divider
box(s, 6.88, 1.2, 0.04, 5.9, RULE)

label(s, "Engagement management", 7.1, 1.25, 5.8, 0.35, size=13, bold=True, color=NAVY)
rule_line(s, 1.6)

eng_items = [
    ("Confirm the board timeline in the first conversation",
     "Marcus told me the meeting was in 6 weeks — not 8 — after the plan was already written. "
     "A basic question I should have asked before putting anything on paper."),
    ("Involve Kim's team in discovery, not just leadership",
     "Kim was not in the discovery session. The failure path gap she spotted would have been caught "
     "in a 30-minute conversation that I simply did not have."),
]
for i, (title, body) in enumerate(eng_items):
    by = 1.65 + i * 2.3
    dot(s, 7.1, by + 0.1, NAVY)
    label(s, title, 7.38, by,        5.6, 0.38, size=13, bold=True, color=DARK)
    label(s, body,  7.38, by + 0.42, 5.6, 1.75, size=11, color=MID)


# ── Save ──────────────────────────────────────────────────
OUT = (r"C:\Users\AnnOHagan\OneDrive - EPAM\FDE AI Program"
       r"\FDE-practice-week2\FDE-practice-week2"
       r"\Week3_Docs\Gate3-MedFlex-Presentation-v2.pptx")
prs.save(OUT)
print(f"Saved: {OUT}")
