"""
SINGLE SOURCE OF TRUTH — non-WSQ course metadata (TEMPLATE).

Copy this to course_data.py in your course's
.agents/skills/non-wsq-courseware-build/build/ folder and fill in the values,
then add data_domain1.py … data_domainN.py (one per topic) using
data_domain.example.py as the pattern. Every artifact (PPT, LP, LG, LG.md) is
generated from these files so they stay 100% aligned.

NON-WSQ RULES — the engine enforces these, do not reintroduce them here:
  * NO assessment of any kind (no WA/SAQ, no PP, no case study, no marking).
  * NO SSG / SkillsFuture / WSQ funding or subsidy content.
  * NO TRAQOM survey, NO digital attendance, NO 75% attendance rule.
  * NO TGS course reference — use the plain non-WSQ course code (e.g. C524).
"""

# ------------------------------------------------------------------ metadata
TITLE        = "Your Course Title (CODE)"
SHORT_TITLE  = "Your Course Title (CODE)"   # used in output filenames
COURSE_CODE  = "C000"                       # non-WSQ code — never a TGS- ref
VERSION      = "v1.0"
VERSION_DATE = "1 January 2026"
ORG          = "Tertiary Infotech Academy Pte Ltd"
UEN          = "UEN: 201200696W"
TRAINER      = "Trainer Name"
DAYS         = 2
MODE         = "Instructor-led, hands-on practical labs"

# Optional: all-white house style is the default. Set True for the dark deck.
DARK_THEME = False

# ------------------------------------------------------------------ outcomes
LEARNING_OUTCOMES = [
    "LO1: …",
    "LO2: …",
]
# Optional short tile titles for the Learning Outcomes slide (index-matched).
LO_TITLES = []

# ------------------------------------------------------------------ topics
# num, code, title, subtitle, concept bullets. `weighting` is OPTIONAL for
# non-WSQ courses (there is no exam) — include it only as a share of course time.
TOPICS = [
    dict(num=1, code="01",
         title="Topic 1 Title",
         subtitle="Sub-topics · shown under the section header",
         concepts=[
            "Key concept 1 for this topic.",
            "Key concept 2 for this topic.",
         ]),
]

# ------------------------------------------------------------------ day themes (8 training hours/day)
DAY_THEMES = {
    1: "Day 1 theme",
    2: "Day 2 theme",
}

# ------------------------------------------------------------------ schedule
# Either a plain dict, or a callable receiving lab_titles(nums) -> str so the
# activity text is built straight from the lab data.
#   kind: admin | topic | lab | break | lunch | recap   (NEVER "assess")
# Each day must total exactly 480 training minutes (lunch excluded).
def SCHEDULE(lab_titles):
    return {
     1: (DAY_THEMES[1], [
        ("9:30","9:50",20,"admin","Welcome, course introduction and ground rules"),
        ("9:50","10:30",40,"topic","Topic 1 — "+TOPICS[0]["title"]+" (concepts + demo)"),
        ("10:30","11:00",30,"lab","Hands-on: "+lab_titles([1,2])),
        ("11:00","11:15",15,"break","Tea break"),
        ("11:15","13:00",105,"lab","Hands-on: "+lab_titles([3,4,5])),
        ("13:00","14:00",60,"lunch","Lunch break"),
        ("14:00","15:30",90,"lab","Hands-on: "+lab_titles([6,7])),
        ("15:30","15:45",15,"break","Tea break"),
        ("15:45","18:15",150,"lab","Hands-on: "+lab_titles([8,9,10])),
        ("18:15","18:30",15,"recap","Day 1 recap and Q&A"),
     ]),
    }

# ------------------------------------------------------------------ optional deck content
# The generic "Core Concepts" section. Omit to skip the section entirely.
COURSE_OVERVIEW = dict(
    section_title="Course Fundamentals",
    concepts_title="Key Concepts",
    concepts=[("Tile title", "Tile body text."), ],
    framework_title="The Framework",
    framework=[("Element", "What it does."), ],
    statement=dict(headline="A memorable one-liner.", body="Supporting sentence.", kicker="KEY IDEA"),
    pillars_title="What You'll Build",
    pillars=[("Pillar name", ["bullet one", "bullet two"]), ],
    arc_title="How Every Lab Progresses",
    arc=["Step of the learning arc.", ],
)

# Optional per-lab screenshots: files live in courseware/assets/screenshots/
LAB_SHOTS = {}   # e.g. {2: [("dashboard.png","Dashboard","What this shows")]}

# ------------------------------------------------------------------ optional LG content
LG_INTRO   = None   # defaults to a generated paragraph
LG_INTRO2  = None
LG_SETUP   = dict(
    needs=["A laptop with …"],
    verify_text="Confirm your setup before you begin.",
    verify_code="$ tool --version",
    conventions=["Placeholders such as <VALUE> are replaced with your own values."],
)
LAB_NOTE   = "Use only accounts and data you are authorised to use."
LG_WRAPUP  = dict(title="Wrap-Up", intro="…", sections=[dict(title="…", bullets=["…"])])
LG_NEXT_STEPS = []   # defaults to a generic set
LG_GLOSSARY   = []   # [(term, definition), …] — omit to skip the glossary

# ------------------------------------------------------------------ version history
# (version, effective date, summary of changes, author) — drives the Document
# Version Control Record in both the LP and the LG.
VERSION_HISTORY = [
    ("1.0", VERSION_DATE, "Initial release.", TRAINER),
]
