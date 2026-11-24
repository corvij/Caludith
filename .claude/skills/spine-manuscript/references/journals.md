# Spine journal requirements

Looked up 2026-11-24. Spine was confirmed on its live author instructions page. The other journals' pages sit behind anti-bot screens, so their values come from search result snippets and are **not confirmed**. Treat every value as a starting point and confirm it on the journal site before formatting a submission. When you confirm or correct a value, update this file and the `JOURNALS` table in `scripts/check_manuscript.py`, and change its status to "confirmed <date>".

Status key: **C** = confirmed on the journal's own page (date given). **S** = snippet attributed to the journal's own author page. **X** = secondary source or sources conflict. Blank = not found.

## Spine (Wolters Kluwer)
Author instructions: https://www.editorialmanager.com/spine/accounts/ifauth.htm
**Confirmed on that page 2026-11-24** (status C) unless marked otherwise.

| Item | Value | Status |
|---|---|---|
| Main text | 3000 words excluding abstract and references. The submission checklist on the same page says 2800. Stay under 2800 to satisfy both | C |
| Text headings | Introduction, Materials and Methods, Results, Discussion | C |
| Abstract | Structured, 300 words max, no citations, few abbreviations | C |
| Abstract headings | Study Design, Objective, Summary of Background Data, Methods, Results, Conclusions | C |
| Key Words | 3 to 8 | C |
| Key Points | 3 to 5 bullets, placed right after the key words | C |
| Mini abstract (precis) | About 3 sentences, 50 words max, for the table of contents | C |
| References | Double spaced, numbered in order of appearance. AMA Manual of Style. More than 3 authors: first 3, then et al | C |
| Figure legends | Under 150 characters or about 50 words, on a separate page | C |
| Title page | Funding, IRB approval, and disclosures | C |
| Clinical trials | Follow CONSORT | C |
| Case report | 1500 words, structured abstract, online only | C |
| Level of Evidence | Required (Oxford CEBM) per search snippets; not found on this page | S |

## The Spine Journal (Elsevier, NASS)
Author instructions: https://www.sciencedirect.com/journal/the-spine-journal/publish/guide-for-authors

| Item | Value | Status |
|---|---|---|
| Clinical study text | 1500 to 4500 words | S |
| Abstract | 250 words max | S |
| Abstract headings | Background Context, Purpose, Study Design, Patient Sample, Outcome Measures, Methods, Results, Conclusions | S |
| References | "10 or fewer" seen, possibly for research letters only | X |
| Reference format | No strict format at submission | S |
| Reporting checklist | Follow the relevant reporting guideline | S |

## Journal of Neurosurgery: Spine
Limits page: https://thejns.org/page/manuscript-limits/manuscript-types-and-limits-policy

| Item | Value | Status |
|---|---|---|
| Clinical article text | 4000 words | S |
| Abstract | 375 words (one secondary source says 250) | S/X |
| Abstract headings | Objective, Methods, Results, Conclusions | X |
| Tables plus figures | 8 combined | S |
| References | 45 | S |
| Videos | 2 | S |
| Title page | State abstract, text, and reference counts and the table/figure total. Update on revision | S |
| AI | Disclose in the manuscript. Allowed for data analysis if declared in Methods or Acknowledgments. Writing help limited to readability and language. AI cannot be an author | S |

## Global Spine Journal (SAGE, AO Spine)
Author instructions: https://journals.sagepub.com/author-instructions/GSJ

| Item | Value | Status |
|---|---|---|
| Abstract | 250 words max | S |
| Abstract headings | Study Design (2 to 3 words), Objectives, Methods, Results, Conclusions. Returned if not structured this way | S |
| Keywords | 4 to 8 | S |
| Trial registration | Registry name, URL, and number at the end of the abstract | S |

## European Spine Journal (Springer)
Author instructions: https://link.springer.com/journal/586/submission-guidelines

| Item | Value | Status |
|---|---|---|
| Original article text | 2500 words | S |
| References | 25 max | S |
| Abstract | 150 to 250 words, structured (up to 450 if a reporting guideline needs it) | S |
| Abstract headings | Purpose, Methods, Results, Conclusion, plus trial registration if applicable | S |
| Reporting guideline | CONSORT, PRISMA, or STROBE as applicable, named in Methods | S |
| Review or meta-analysis | 3500 words, 50 to 70 references | S |
| Case report | 1500 words, 350 word abstract, 15 references | S |

## Spine Deformity (Springer, SRS)
Author instructions: https://link.springer.com/journal/43390/submission-guidelines

| Item | Value | Status |
|---|---|---|
| Original article text | 2700 words, excluding abstract and references | S |
| Abstract | 150 to 250 words, structured | S |
| Abstract headings | Purpose, Methods, Results, Conclusion | S |
| Case report | 750 words, structured abstract | S |
| Trial registration | Number and date as the last line of the abstract | S |

## Clinical Spine Surgery (Wolters Kluwer)
Journal page: https://journals.lww.com/jspinaldisorders/pages/default.aspx

| Item | Value | Status |
|---|---|---|
| Abstract headings | Study Design, Objective, Summary of Background Data, Methods, Results, Conclusions, plus Level of Evidence (taken from published papers) | X |

## JBJS (for comparison)
Author instructions: https://jbjs.org/jbjs-ifa.php

| Item | Value | Status |
|---|---|---|
| Abstract | Background (with the research question), Methods, Results, Conclusions, Level of Evidence | S |
| Abstract length | 325 or 350 words (sources conflict) | X |
| Word count rule | Counts include the abstract, exclude references and legends | S |
| Level of Evidence | Authors assign it from the JBJS table; editors decide | S |
| AI | Disclose every tool (version or year, maker) and how its output was verified | S |

## Gaps to fill

These journal pages show anti-bot screens to automated tools. To confirm a journal, open its author instructions in a browser, copy the text into the session, and update this file and `scripts/check_manuscript.py` together.

- Reference count limits for The Spine Journal, GSJ, Spine Deformity, JBJS
- Author count before "et al" in each journal's reference style
- Blinded manuscript and title page rules
- AI disclosure rules for Spine, The Spine Journal, GSJ, ESJ, Spine Deformity
