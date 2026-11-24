---
name: case-prep
description: Build surgical case prep for Dr. Corvi in this repo. Writes a case plan (case_plans/) and an Anki cloze deck (anki/) in the house format, and turns missed AAOS ResStudy or OITE questions into cards. Use when the user names an upcoming case, attending, or procedure ("prep me for a TTO with Gladstone", "case plan for an L4-5 TLIF", "make cards for these missed questions", "Anki deck for tomorrow's shoulder cases").
---

# Case prep

Two outputs, same rules: a case plan in `case_plans/` and an Anki deck in `anki/`. Make both unless the user asks for only one. Missed-question cards go to the ResStudy deck and need no case plan.

## Rules for every file

- No patient identifiers. No names, MRN, DOB, dates of service, or images with identifiers. `anki/ankibuild.py` blocks the obvious ones, but check by eye too.
- No en or em dashes. Plain sentences. No filler.
- Implants and products: if the attending has not specified, mark every choice as a default to confirm. Never present a guess as the attending's preference.
- Numbers (distances, thresholds, percentages) need a source: a vendor technique guide, a named paper (first author, year), or the AAOS explanation. If you cannot source a number, leave it out or label it unverified.
- Write at the level of a surgeon reviewing the night before. Short lines, tables where they help.

## Inputs to get first

Ask only for what is missing:
1. Procedure(s) and side, plus the indication in general terms (no identifiers).
2. Attending, and any known preferences (implant system, approach, positioning, postop protocol).
3. Date of the case (used in file names).
4. For missed questions: the pasted question text with its ID, the user's answer, and the AAOS explanation.

## Case plan

File: `case_plans/<attending>_<procedure_short>_<YYYY-MM-DD>.md`, lowercase, underscores.
Start from `templates/case_plan_template.md`. The sections mirror `case_plans/gladstone_PF_realignment_2026-11-01.md`, which is the reference example:

1. Confirm with the attending before the day (decision, default, alternatives)
2. Preop imaging: numbers to have ready (measure, threshold, what it changes)
3. Room setup and positioning, antibiotics, exam under anesthesia
4. Equipment list (item, product, notes, backups)
5. Order of the case, with the reason for the order
6. Steps in detail, with the numbers that matter
7. Structures at risk (step, structure, how to avoid)
8. Postop (default, confirm with attending)
9. Consent discussion
10. Facts to know for the case (pimping list)
Sources (vendor technique guides, PMC links)

For spine cases also cover: levels and how they will be confirmed (counting method, fluoroscopy or navigation), neuromonitoring plan and alerts protocol, positioning risks (eyes, face, brachial plexus, lateral femoral cutaneous nerve), instrumentation sizes and trajectory notes, and blood loss plan (TXA, cell saver).

## Anki deck

Copy `templates/deck_template.py` to `anki/build_<attending>_<topic>_<YYYY-MM-DD>.py`, fill in the notes, and run it:

```bash
python3 anki/build_<name>.py
```

`anki/ankibuild.py` checks every note (dashes, raw `<`, cloze numbering, duplicates, missing images, likely PHI) and stops on any problem. It writes `<name>.txt` for Anki text import and, when genanki is installed (`pip install genanki`), `<name>.apkg` for direct import on mobile. Images go in `anki/media/` and are referenced as `<img src="file.png">`; the .apkg includes them.

Card format (match the existing decks):
- Note type Cloze, fields Text and Back Extra.
- Text: a topic line, then one cue per fact, each fact a cloze, separated by `<br>`. Group related facts in one note with c1, c2, c3 so they become separate cards.
- Back Extra: why the wrong answers are wrong, the source, and any mnemonic. One line of HTML.
- Write `<` as `&lt;` before a digit or space.
- Aim for facts that are tested or that matter in the OR: distances, structures at risk, thresholds, classification cutoffs, steps in order.

Decks and tags:

| Kind | Deck | Tags | Back Extra ends with |
|---|---|---|---|
| Case prep | `OITE 2026::OITE 2026::2 Case prep::<Attending> <topic>` | `CasePrep <Attending> <Region> <group>` | `Case prep: <Attending> <topic>, <MM/YYYY>` |
| Missed ResStudy | `OITE 2026::OITE 2026::1 Missed questions::ResStudy::Incorrect` | `ResStudy <Region> ResStudy::<ID>` | `Source: AAOS ResStudy #<ID>` |

For missed questions, use the question ID as the note key, and set `apkg=False` in `build()` so the cards go in by text import into the existing note type.

Rebuilding a deck that is already in Anki: pass its original `deck_id` and `model_id` to `build()` (see `anki/build_galatz_shoulder_2026-10-25.py`). New decks get stable IDs from the deck name automatically.

## Handoff to the local Anki

Cloud sessions cannot reach the user's Anki. After building, add a section to `anki/HANDOFF.md` from `templates/handoff_template.md`: what files to import, which deck, the duplicate check against the existing collection, and anything left undone (missing images, unverified facts, questions to ask the user).

## Finish

1. Run the deck script and fix any problems it reports.
2. Lint all decks and plans: `python3 anki/ankibuild.py anki/*.txt case_plans/*.md` should report 0 problems.
3. Read the case plan once more for anything stated as the attending's preference that is really a default.
4. Commit the case plan, deck script, .txt, .apkg, media, and HANDOFF update together.
5. Tell the user the card count, the deck name, and the open items to confirm with the attending.
