---
name: spine-manuscript
description: Draft, revise, and check clinical spine surgery manuscripts for Dr. Corvi. Formats for a target journal (Spine, The Spine Journal, JNS Spine, Global Spine Journal, European Spine Journal, Spine Deformity, Clinical Spine Surgery, JBJS), applies the right reporting checklist (STROBE, CONSORT, PRISMA, TRIPOD+AI), and verifies every reference against PubMed. Use for "help me write this paper", "check my manuscript before I submit", "format this for Spine", "verify my references", "write the abstract", or "respond to reviewers".
---

# Spine manuscript

Work from the user's data and drafts. Never invent results, numbers, patients, or references. If a number is missing, leave a marked gap like `[N = ?]` and list it at the end.

## Writing rules (Dr. Corvi's standing preferences)

- No en or em dashes, anywhere.
- Plain sentences. No filler, no grand opening or closing lines. Do not start the Introduction with "Spine surgery is a rapidly evolving field" or similar.
- Prefer "use" over "utilize", "about" over "approximately" in prose, "we" for the authors.
- One claim per sentence where possible. Each claim in the Introduction and Discussion has a citation.
- `scripts/check_manuscript.py` flags stock AI phrases. Rewrite each flagged sentence unless the word is the correct technical term (for example "robust" in "robust standard errors").

## Steps

### 1. Pin down the paper
Ask for anything missing:
- Study design and data source (single center retrospective, prospective registry, RCT, NSQIP, systematic review)
- Primary question and primary outcome
- Target journal and article type
- What exists already (data, tables, draft sections, reviewer comments)

Then choose the reporting guideline from `references/reporting_and_conventions.md` and the format from `references/journals.md`. The journal values there are unconfirmed. Tell the user which ones to confirm on the journal site, or confirm them yourself if the site is reachable, then update both files.

### 2. Draft or revise
Order that works: Methods, Results (from the tables), Introduction, Discussion, Abstract last, title last.

- **Introduction**: 3 short paragraphs. What is known (cited), the gap, the question and hypothesis.
- **Methods**: design, setting, IRB, inclusion and exclusion, surgical technique if relevant, outcomes with instrument versions and time points, radiographic methods, statistics (tests, adjustment, missing data, significance level, software and version). Name the reporting guideline.
- **Results**: cohort flow first (with a figure for any exclusions), baseline table, primary outcome, secondary outcomes, complications. Numbers in the text match the tables exactly.
- **Discussion**: main finding in the first sentence, comparison with prior work (cited), mechanism or explanation, limitations as a paragraph, conclusion that does not go beyond the data.
- **Abstract**: the target journal's exact headings. Numbers must match the main text.
- Use `references/reporting_and_conventions.md` for outcome measures, radiographic parameters, complications, and statistics reporting.

For literature searches, use the `literature-review` skill. For finding and formatting a specific reference, use `citation-management`. For a systematic review's screening, use `sr-screener`. For analysis, use `data:statistical-analysis`.

### 3. Check before submission
Run both scripts and fix what they report.

```bash
python3 .claude/skills/spine-manuscript/scripts/check_manuscript.py paper.docx --journal spine
python3 .claude/skills/spine-manuscript/scripts/check_refs.py paper.docx --out refcheck.md
```

Journal keys: `spine`, `spinej`, `jns`, `gsj`, `esj`, `deformity`, `css`, `jbjs`. Override any limit with `--abstract-limit`, `--text-limit`, `--ref-limit`.

`check_manuscript.py` (works offline): word counts by section, abstract headings for the journal, citation order and uncited references, table and figure order, abbreviations used before definition, dashes, filler phrases, possible patient identifiers.

`check_refs.py` (needs PubMed access): finds each reference in PubMed by PMID, DOI, citation match, or title; flags wrong first author, title, year, volume, or page; flags retracted papers and errata; prints the corrected AMA citation from PubMed. Cloud sessions block PubMed, so run it from the desktop app or a local terminal. Use `--offline` to check parsing only.

Use headings on their own line (Abstract, Introduction, Methods, Results, Discussion, Conclusions, References) so the scripts can find the sections. Bracketed citations like [3] or [4-6] can be checked; Word superscript citations cannot.

Then walk the reporting checklist item by item and give the user a filled-in checklist with the manuscript location of each item, marking any item that is missing.

### 4. Reviewer responses
Make a table: reviewer comment (quoted), response, change made with page and line. Agree where the reviewer is right. Where you disagree, give the reason and a citation. Do not promise analyses the data cannot support.

## AI disclosure

Journals require it and the wording differs (see `references/journals.md`). Default text to adapt:

"The authors used Claude (Anthropic) to edit the manuscript for language and to check references against PubMed. The authors reviewed and verified all content and take full responsibility for it."

If AI was used for data analysis, say so in Methods, per JNS and JBJS rules.
