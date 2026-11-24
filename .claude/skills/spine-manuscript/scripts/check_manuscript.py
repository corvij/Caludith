#!/usr/bin/env python3
"""Pre-submission checks for a manuscript in .docx, .md, or .txt.

Reports:
  - word counts: abstract, main text (Introduction through Conclusion), references
  - abstract headings found vs. those the target journal wants
  - en or em dashes, and stock AI-sounding phrases
  - numbered citations: first-appearance order, gaps, numbers above the reference count
  - tables and figures: cited in order, and every one cited
  - abbreviations used before they are defined
  - likely patient identifiers

Usage:
  python3 check_manuscript.py paper.docx
  python3 check_manuscript.py paper.docx --journal spine
  python3 check_manuscript.py paper.md --abstract-limit 300 --text-limit 3000

Journal presets live in JOURNALS below. Limits change, so confirm them on the
journal's author instructions page before submitting (see references/journals.md).
"""

import argparse
import re
import sys

# Limits are from search snippets of each journal's author instructions, 2026-11-24.
# None of them was confirmed on the live page. Confirm before submitting and
# update references/journals.md and this table together. None = not enforced.
JOURNALS = {
    "spine": {"name": "Spine",
              "abstract_headings": ["Study Design", "Objective", "Summary of Background Data",
                                    "Methods", "Results", "Conclusion"],
              "abstract_limit": 300, "text_limit": None, "ref_limit": None},
    "spinej": {"name": "The Spine Journal",
               "abstract_headings": ["Background Context", "Purpose", "Study Design",
                                     "Patient Sample", "Outcome Measures", "Methods", "Results",
                                     "Conclusions"],
               "abstract_limit": 250, "text_limit": 4500, "ref_limit": None},
    "jns": {"name": "Journal of Neurosurgery: Spine",
            "abstract_headings": ["Objective", "Methods", "Results", "Conclusions"],
            "abstract_limit": 375, "text_limit": 4000, "ref_limit": 45},
    "gsj": {"name": "Global Spine Journal",
            "abstract_headings": ["Study Design", "Objectives", "Methods", "Results", "Conclusions"],
            "abstract_limit": 250, "text_limit": None, "ref_limit": None},
    "esj": {"name": "European Spine Journal",
            "abstract_headings": ["Purpose", "Methods", "Results", "Conclusion"],
            "abstract_limit": 250, "text_limit": 2500, "ref_limit": 25},
    "deformity": {"name": "Spine Deformity",
                  "abstract_headings": ["Purpose", "Methods", "Results", "Conclusion"],
                  "abstract_limit": 250, "text_limit": 2700, "ref_limit": None},
    "css": {"name": "Clinical Spine Surgery",
            "abstract_headings": ["Study Design", "Objective", "Summary of Background Data",
                                  "Methods", "Results", "Conclusion"],
            "abstract_limit": None, "text_limit": None, "ref_limit": None},
    "jbjs": {"name": "JBJS",
             "abstract_headings": ["Background", "Methods", "Results", "Conclusions", "Level of Evidence"],
             "abstract_limit": 325, "text_limit": None, "ref_limit": None},
}

# Phrases that read as machine-written or padded. Each hit is a suggestion, not an error.
FILLER = [
    r"\bdelve\w*", r"\bplays? a (crucial|pivotal|vital|key) role\b", r"\bpivotal\b",
    r"\bunderscores?\b", r"\bin the realm of\b", r"\blandscape\b", r"\ba testament to\b",
    r"\bit is (important|worth) (to note|noting)\b", r"\bnotably\b", r"\bparamount\b",
    r"\bshed(s)? light on\b", r"\bnavigat(e|ing) the complexit", r"\bever-evolving\b",
    r"\bmultifaceted\b", r"\bholistic\b", r"\bseamless(ly)?\b", r"\brobust\b",
    r"\bin today's\b", r"\bgame[- ]changer\b", r"\bnovel\b", r"\bparadigm shift\b",
    r"\bfurthermore\b", r"\bmoreover\b", r"\bin conclusion\b", r"\bharness(es|ing)?\b",
    r"\bleverag(e|es|ing)\b", r"\butiliz(e|es|ed|ing|ation)\b", r"\bcomprehensive\b",
    r"\bintricate\b", r"\bcrucial\b",
]

PHI = [
    (r"\bMRN\b|\bmedical record (number|no)\b", "MRN"),
    (r"\bDOB\b|\bdate of birth\b", "date of birth"),
    (r"\b\d{3}-\d{2}-\d{4}\b", "SSN-like number"),
]

SECTION_RE = re.compile(
    r"^\s*(abstract|introduction|background|methods?|materials and methods|patients and methods|"
    r"results|discussion|conclusions?|limitations|references|acknowledg\w*|key points|"
    r"level of evidence|figure legends?|tables?)\s*:?\s*$", re.I)


def read_text(path):
    if path.endswith(".docx"):
        import docx
        d = docx.Document(path)
        lines = [p.text for p in d.paragraphs]
        for t in d.tables:
            lines.append("")
            for row in t.rows:
                lines.append(" | ".join(c.text for c in row.cells))
        return lines
    with open(path, encoding="utf-8") as f:
        return [re.sub(r"^#+\s*", "", l.rstrip("\n")) for l in f]


def split_sections(lines):
    """Map lower-case section name -> list of lines. Text before the first heading is 'front'."""
    sections, cur = {"front": []}, "front"
    for line in lines:
        m = SECTION_RE.match(line)
        if m:
            cur = m.group(1).lower()
            cur = {"method": "methods", "materials and methods": "methods",
                   "patients and methods": "methods", "conclusion": "conclusions",
                   "background": "introduction"}.get(cur, cur)
            sections.setdefault(cur, [])
            continue
        sections.setdefault(cur, []).append(line)
    return sections


def words(lines):
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'%./-]*", " ".join(lines)))


def count_refs(ref_lines):
    numbered = [l for l in ref_lines if re.match(r"^\s*\[?\d{1,3}[.)\]]\s+\S", l)]
    return len(numbered) if numbered else len([l for l in ref_lines if l.strip()])


def citation_numbers(text):
    """Numbers inside [..] citations, in order of appearance, ranges expanded."""
    out = []
    for grp in re.findall("\\[(\\d[\\d,\\s\\-\u2013]*)\\]", text):
        for part in re.split(r"\s*,\s*", grp.strip()):
            m = re.match("(\\d+)\\s*[-\\u2013]\\s*(\\d+)$", part)
            if m:
                a, b = int(m.group(1)), int(m.group(2))
                out.extend(range(a, b + 1) if b >= a and b - a < 50 else [a, b])
            elif part.isdigit():
                out.append(int(part))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--journal", choices=sorted(JOURNALS))
    ap.add_argument("--abstract-limit", type=int)
    ap.add_argument("--text-limit", type=int)
    ap.add_argument("--ref-limit", type=int)
    a = ap.parse_args()

    lines = read_text(a.file)
    full = "\n".join(lines)
    sec = split_sections(lines)
    j = JOURNALS.get(a.journal, {})
    abstract_limit = a.abstract_limit or j.get("abstract_limit")
    text_limit = a.text_limit or j.get("text_limit")
    ref_limit = a.ref_limit or j.get("ref_limit")
    warn = 0

    print(f"== {a.file}" + (f"  (target: {j['name']}, limits unconfirmed, check the journal site)" if j else ""))
    found = [s for s in sec if s != "front" and sec[s]]
    print("Sections found: " + (", ".join(found) or "none (use plain headings like 'Methods' on their own line)"))

    # Word counts
    main_names = ["introduction", "methods", "results", "discussion", "limitations", "conclusions"]
    main_words = sum(words(sec.get(s, [])) for s in main_names)
    abs_words = words(sec.get("abstract", []))
    print("\n-- Word counts")
    print(f"Abstract: {abs_words}" + (f" (limit {abstract_limit})" if abstract_limit else ""))
    print(f"Main text, Introduction through Conclusions: {main_words}" + (f" (limit {text_limit})" if text_limit else ""))
    for s in main_names:
        if s in sec:
            print(f"  {s}: {words(sec[s])}")
    if abstract_limit and abs_words > abstract_limit:
        print(f"OVER: abstract is {abs_words - abstract_limit} words over"); warn += 1
    if text_limit and main_words > text_limit:
        print(f"OVER: main text is {main_words - text_limit} words over"); warn += 1

    # Abstract headings
    if j and "abstract" in sec:
        abs_text = "\n".join(sec["abstract"]).lower()
        missing = [h for h in j["abstract_headings"] if h.lower() not in abs_text]
        print("\n-- Abstract headings for " + j["name"])
        print("Missing: " + ", ".join(missing) if missing else "All expected headings present")
        warn += bool(missing)

    # References and citation order
    n_refs = count_refs(sec.get("references", []))
    body = "\n".join(sum((sec.get(s, []) for s in ["front", "abstract"] + main_names), []))
    cites = citation_numbers(body)
    print(f"\n-- References: {n_refs} listed" + (f" (limit {ref_limit})" if ref_limit else ""))
    if ref_limit and n_refs > ref_limit:
        print(f"OVER: {n_refs - ref_limit} references over"); warn += 1
    if cites:
        first, seen = [], set()
        for c in cites:
            if c not in seen:
                seen.add(c); first.append(c)
        out_of_order = [c for i, c in enumerate(first) if c != i + 1]
        if out_of_order:
            print(f"Citations not numbered in order of first appearance. First seen order starts: {first[:15]}"); warn += 1
        if n_refs:
            uncited = sorted(set(range(1, n_refs + 1)) - seen)
            too_high = sorted(c for c in seen if c > n_refs)
            if uncited:
                print(f"Listed but never cited: {uncited}"); warn += 1
            if too_high:
                print(f"Cited but not in the list: {too_high}"); warn += 1
        if not out_of_order:
            print("Bracketed citations are in order of first appearance.")
    else:
        print("No [n] citations found. Superscript citations in .docx cannot be checked here.")

    # Tables and figures
    print("\n-- Tables and figures")
    for kind in ("Table", "Figure"):
        nums = [int(n) for n in re.findall(rf"\b{kind}s?\.?\s+(\d+)", body, re.I)]
        if not nums:
            continue
        first = list(dict.fromkeys(nums))
        missing = sorted(set(range(1, max(first) + 1)) - set(first))
        msg = f"{kind}s cited in text: {first}"
        if first != sorted(first):
            msg += "  NOT IN ORDER"; warn += 1
        if missing:
            msg += f"  never cited: {missing}"; warn += 1
        print(msg)

    # Abbreviations: checked within the main text, which must define them again
    # even if the abstract already did.
    print("\n-- Abbreviations (main text)")
    main_text = "\n".join(sum((sec.get(s, []) for s in main_names), []))
    defined = set(re.findall(r"\(([A-Z][A-Za-z0-9-]*[A-Z0-9]s?)\)", main_text))
    late = []
    for ab in defined:
        pos = main_text.find(f"({ab})")
        m = re.search(rf"\b{re.escape(ab)}\b", main_text)
        if m and m.start() < pos - 1:
            late.append(ab)
    common = {"MRI", "CT", "USA", "US", "II", "III", "IV", "VI", "VII", "SD", "OR", "CI",
              "AND", "NOT", "IRB", "BMI", "ASA", "HIPAA"}
    undefined = sorted({w for w in re.findall(r"\b[A-Z]{2,}[0-9]?s?\b", main_text)} - defined - common)
    if late:
        print("Used before definition: " + ", ".join(sorted(late))); warn += 1
    if undefined:
        print("Never defined in parentheses (check each; some need no definition): " + ", ".join(undefined[:40]))
    if not late and not undefined:
        print("No problems found")

    # Dashes, filler, PHI
    print("\n-- Style")
    for i, line in enumerate(lines, 1):
        for m in re.finditer("[\u2013\u2014]", line):
            print(f"line {i}: en or em dash: ...{line[max(0, m.start() - 40):m.end() + 40]}..."); warn += 1
    hits = {}
    for i, line in enumerate(lines, 1):
        for pat in FILLER:
            for m in re.finditer(pat, line, re.I):
                hits.setdefault(m.group(0).lower(), []).append(i)
    if hits:
        print("Phrases to reconsider (word: lines):")
        for w, ls in sorted(hits.items(), key=lambda kv: -len(kv[1])):
            print(f"  {w}: {ls[:10]}")
    for i, line in enumerate(lines, 1):
        for pat, name in PHI:
            if re.search(pat, line, re.I):
                print(f"line {i}: possible patient identifier ({name})"); warn += 1

    print(f"\n{warn} item(s) to fix. Filler phrases are suggestions and are not counted.")
    return 1 if warn else 0


if __name__ == "__main__":
    sys.exit(main())
