# Handoff: missed Foot & Ankle ResStudy cards

## Paste this into the other session

> I made Anki cards for missed AAOS ResStudy questions in a cloud session that couldn't reach my Anki. Please add them to my collection.
>
> Files are on GitHub: repo corvij/Caludith, branch claude/nifty-wozniak-gevfvu, folder anki/
> - foot_ankle_missed_2026-10-04.txt (Anki text import, 7 cloze notes, 20 cards)
> - media/ResStudy_Foot20-055.png (photo for the Foot20-055 card)
> - build_foot_ankle_2026-10-04.py (script that generated the .txt)
>
> Steps:
> 1. Before adding anything, check whether an existing card in "OITE 2026::OITE 2026::1 Missed questions" already covers each fact. Skip or merge duplicates.
> 2. Check that the notes match my existing missed-question notes (note type, field names, tags). The cloud session guessed Cloze with Text / Back Extra.
> 3. Store media/ResStudy_Foot20-055.png in Anki media under that exact filename (the Foot20-055 card front references it).
> 4. Add the notes to OITE 2026::OITE 2026::1 Missed questions::ResStudy::Incorrect.
> 5. Run cardlint and the media check on the deck. Target 0 errors and no broken images.
> 6. Open ResStudy question #25FOOT-097 (Q8 of that quiz) and add its ulcer photo to that card. I didn't have it as a file in the cloud session.
>
> Open questions for me: Q3 (#25FOOT-053) and Q5 (#Foot20-040) showed as correct. They were carded anyway. Ask me whether to keep them.

## What was done

Source: Build a Quiz, Study Mode, 10 questions (pasted as "Question N of 10"). Exact quiz date and score were not captured.

| Q | ID | Result | Card topic |
|---|---|---|---|
| 3 | 25FOOT-053 | Correct (carded anyway) | FHL stenosing tenosynovitis in a dancer, release fibro-osseous tunnel |
| 4 | Foot22-008 | Incorrect | TN fusion removes about 90% of hindfoot motion (under 8% left) |
| 5 | Foot20-040 | Correct (carded anyway) | Chronic Achilles gap: 2 to 5 cm V-Y +/- FHL, over 5 cm FHL transfer |
| 6 | Foot22-032 | Incorrect | Fibular sesamoid excision causes hallux varus; both causes cock-up hallux |
| 7 | 1046016 | Incorrect | Metatarsalgia: metatarsal pad; orthotic by foot type |
| 8 | 25FOOT-097 | Incorrect | Diabetic ulcer: total contact cast heals fastest |
| 9 | Foot20-055 | Incorrect | TAR wound breakdown at 3 weeks: debride, poly exchange, flap |

Q1, Q2 and Q10 were never sent to the cloud session. Check whether any of them were missed.

## Card format used

- Deck: OITE 2026::OITE 2026::1 Missed questions::ResStudy::Incorrect
- Note type: Cloze (fields Text, Back Extra)
- Front: a topic line, then one cue per fact, each fact a cloze
- Back Extra: AAOS explanation points, then "Source: AAOS ResStudy #ID"
- Tags: ResStudy, Foot_Ankle, ResStudy::ID
- No en or em dashes. A raw "<" before a digit is written as &lt;

## Not done

- Duplicate check against the existing collection
- cardlint and media check
- Q8 ulcer photo
- Extra teaching points (Wagner grades, Astion motion data, hallux varus causes and treatment, TAR wound management table). They were given in chat but not added to the cards.

## Card file contents

```
#separator:tab
#html:true
#notetype:Cloze
#deck:OITE 2026::OITE 2026::1 Missed questions::ResStudy::Incorrect
#tags column:3
```
(7 rows follow in foot_ankle_missed_2026-10-04.txt, one note per line: Text, Back Extra, tags, tab separated.)
