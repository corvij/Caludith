import os, sys

# Case prep deck for <procedure> with Dr. <Attending>. No patient data.
# Copy to anki/build_<attending>_<topic>_<YYYY-MM-DD>.py and run it from anywhere.

DECK = "OITE 2026::OITE 2026::2 Case prep::<Attending> <topic>"
BASENAME = "<attending>_<topic>_<YYYY-MM-DD>"

notes = [
    # (tag group, Text, Back Extra)

    # ---------- <Section, e.g. Anatomy> ----------
    ("Anatomy::<Structure>",
     "<Topic line><br>"
     "<Cue 1>: {{c1::<fact 1>}}<br>"
     "<Cue 2>: {{c2::<fact 2>}}",
     "<Why it matters, why the distractors are wrong. Source: First author year.>"),
]

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ankibuild import build

build(
    DECK, BASENAME, notes,
    tags=lambda group: f"CasePrep <Attending> <Region> {group}",
    extra_suffix="Case prep: <Attending> <topic>, <MM/YYYY>",
)
