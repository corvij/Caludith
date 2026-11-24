# Reporting guidelines and spine conventions

## Which reporting guideline

All are on the EQUATOR Network (https://www.equator-network.org). Name the guideline in Methods and submit the completed checklist with page numbers.

| Study design | Guideline |
|---|---|
| Retrospective or prospective cohort, case-control, cross-sectional | STROBE |
| Study using registry or claims data (NSQIP, PearlDiver, NIS, QOD) | RECORD (STROBE extension) |
| Randomized trial | CONSORT 2025 |
| Trial protocol | SPIRIT 2025 |
| Systematic review or meta-analysis | PRISMA 2020 (and PRISMA-S for the search) |
| Meta-analysis of observational studies | MOOSE, with PRISMA |
| Diagnostic accuracy | STARD 2015 |
| Prediction model or machine learning model | TRIPOD+AI |
| Cost-effectiveness | CHEERS 2022 |
| Case report | CARE |
| Quality improvement | SQUIRE 2.0 |
| Animal or cadaver biomechanics | ARRIVE 2.0 for animal work. For cadaver biomechanics, no single standard; report specimen details, testing protocol, and loading |

Version years: confirm the current version on EQUATOR before citing it.

## Level of evidence

Spine uses the Oxford CEBM levels. JBJS and many orthopaedic journals use the JBJS table (Therapeutic, Prognostic, Diagnostic, Economic). Most single-center retrospective comparative studies are Level III. A case series without a comparison group is Level IV. Confirm against the table the target journal names.

## Outcome measures: report them consistently

- Name the instrument and version on first use, for example Oswestry Disability Index (ODI) version 2.1a, Neck Disability Index (NDI), modified Japanese Orthopaedic Association score (mJOA), SRS-22r, EQ-5D-5L, PROMIS Physical Function, numeric rating scale (NRS) for back and leg pain separately.
- State the time points and the window (for example 12 months, accepted 9 to 15 months).
- Report the follow-up rate at each time point and how missing data were handled.
- If MCID is used, cite the source study for that specific population and anchor method. MCID values vary by population and method. Look up the value and verify the citation with `scripts/check_refs.py` before using it. Do not quote an MCID from memory.

## Radiographic parameters

- Define each on first use and say how it was measured (software, who measured, blinded or not, intra and interrater reliability if reported).
- Sagittal: pelvic incidence (PI), lumbar lordosis (LL, state the levels, usually L1 to S1), PI minus LL mismatch, pelvic tilt (PT), sacral slope (SS), sagittal vertical axis (SVA), T1 pelvic angle (TPA). Cervical: C2 to C7 lordosis, C2 to C7 SVA, T1 slope.
- Fusion: state the criteria (CT bridging bone, flexion-extension motion threshold in degrees or mm) and who graded it.
- Name the classification used (SRS-Schwab, Lenke, Meyerding, AOSpine) and cite it.

## Complications and reoperation

- Define complications in advance, and the window (90 day, 1 year). Use a named grading system if possible (for example Clavien-Dindo).
- Separate reoperation at the index level from adjacent segment surgery.
- Report deaths and losses to follow-up.

## Statistics: what reviewers ask for

- Sample size or power calculation, or say there was none.
- Effect sizes with 95% confidence intervals, not only p values.
- Exact p values to 2 or 3 decimals (write p < .001 for smaller values).
- Adjusted analyses for confounding in observational comparisons (multivariable regression or propensity methods), with the covariates listed and why they were chosen.
- Clustering (multiple levels per patient, surgeon effects) if relevant.
- Mean and SD for normal data, median and IQR otherwise.

## Ethics and disclosure

- IRB approval with protocol number, and consent or waiver.
- Trial registration for prospective interventional studies.
- Conflicts of interest and funding, including implant company consulting.
- AI use: disclose per the journal. The default statement in `SKILL.md` covers language editing and checking.
