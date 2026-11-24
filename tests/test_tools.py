#!/usr/bin/env python3
"""Tests for the repo's scripts. Run before committing a change to any of them.

  python3 tests/test_tools.py          # offline tests only
  python3 tests/test_tools.py --live   # also checks real references against PubMed and Crossref

Covers anki/ankibuild.py, spine-manuscript/scripts/check_manuscript.py and
check_refs.py. Exits 1 if any test fails.
"""

import contextlib
import io
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, ".claude", "skills", "spine-manuscript", "scripts")
sys.path.insert(0, os.path.join(ROOT, "anki"))
sys.path.insert(0, SCRIPTS)
sys.dont_write_bytecode = True

import ankibuild  # noqa: E402
import check_manuscript  # noqa: E402
import check_refs  # noqa: E402

FAILS = []
EM = "\u2014"


def test(name):
    def wrap(fn):
        try:
            fn()
            print(f"ok    {name}")
        except AssertionError as e:
            FAILS.append(name)
            print(f"FAIL  {name}: {e}")
        return fn
    return wrap


def run_main(module, argv):
    old = sys.argv
    sys.argv = ["x"] + argv
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            code = module.main()
    finally:
        sys.argv = old
    return code, buf.getvalue()


# ---------- Anki builder ----------

@test("anki: clean note passes")
def _():
    assert ankibuild.lint_note("k", "Topic<br>Cue: {{c1::a}}<br>Cue: {{c2::b}}", "Why.") == []


@test("anki: catches dash, raw <, skipped cloze, PHI, missing image")
def _():
    p = " ".join(ankibuild.lint_note("k", f"A {EM} {{{{c1::x}}}} {{{{c3::y}}}}",
                                     'MRN 1, <5 mm <img src="missing.png">'))
    for want in ("dash", 'raw "<"', "skip", "MRN", "missing.png"):
        assert want in p, f"missing {want!r} in {p}"


@test("anki: existing decks still lint clean")
def _():
    for f in ("galatz_shoulder_2026-10-25.txt", "foot_ankle_missed_2026-10-04.txt"):
        with contextlib.redirect_stdout(io.StringIO()):
            assert ankibuild.lint_txt(os.path.join(ROOT, "anki", f)) == 0, f


@test("anki: deck scripts rebuild byte-identical .txt")
def _():
    for script, out in (("build_galatz_shoulder_2026-10-25.py", "galatz_shoulder_2026-10-25.txt"),
                        ("build_foot_ankle_2026-10-04.py", "foot_ankle_missed_2026-10-04.txt")):
        path = os.path.join(ROOT, "anki", out)
        before = open(path, "rb").read()
        apkg = path[:-4] + ".apkg"
        apkg_before = open(apkg, "rb").read() if os.path.exists(apkg) else None
        subprocess.run([sys.executable, "-B", os.path.join(ROOT, "anki", script)],
                       check=True, capture_output=True)
        after = open(path, "rb").read()
        # restore the committed .apkg so a test run leaves git clean
        if apkg_before is not None:
            open(apkg, "wb").write(apkg_before)
        elif os.path.exists(apkg):
            os.remove(apkg)
        assert before == after, f"{out} changed"


@test("case plans lint clean")
def _():
    d = os.path.join(ROOT, "case_plans")
    for f in os.listdir(d):
        if f.endswith(".md"):
            with contextlib.redirect_stdout(io.StringIO()):
                assert ankibuild.lint_md(os.path.join(d, f)) == 0, f


# ---------- manuscript checker ----------

SAMPLE = f"""# Title

## Abstract
Study Design: Retrospective cohort.
Objective: Compare fusion rates.
Methods: We reviewed 200 patients.
Results: Fusion was 92% vs 85%.
Conclusions: TLIF fused more often.

## Introduction
Lumbar fusion plays a crucial role [1]. Transforaminal lumbar interbody fusion (TLIF) is common [3]. Posterolateral fusion (PLF) is an option [2]. We used the ODI {EM} it is robust.

## Methods
The Oswestry Disability Index (ODI) was recorded [4-5]. See Table 2 and Table 1.

## Results
TLIF had higher fusion [4].

## References
1. Smith A. One. Spine. 2020;45:1-5.
2. Jones B. Two. Spine J. 2019;19:2-8.
3. Lee C. Three. Eur Spine J. 2018;27:3-9.
4. Kim D. Four. Spine. 2017;42:10-15.
5. Park E. Five. Global Spine J. 2016;6:1-4.
6. Unused F. Six. Spine. 2015;40:1-2.
"""


@test("manuscript: finds order, uncited, tables, abbreviations, dash, filler, headings")
def _():
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(SAMPLE)
    code, out = run_main(check_manuscript, [f.name, "--journal", "spine"])
    os.unlink(f.name)
    assert code == 1
    for want in ("not numbered in order", "never cited: [6]", "NOT IN ORDER",
                 "Used before definition: ODI", "en or em dash", "crucial",
                 "Missing: Summary of Background Data", "limit 300"):
        assert want in out, f"missing {want!r}"


@test("manuscript: superscript citations in Word are read")
def _():
    import docx
    d = docx.Document()
    d.add_paragraph("Introduction")
    p = d.add_paragraph("A.")
    for text, sup in (("1", True), (" B.", False), ("3,", True), ("4", True), (" C.", False), ("2", True)):
        r = p.add_run(text)
        r.font.superscript = sup
    path = tempfile.mktemp(suffix=".docx")
    d.save(path)
    lines = check_manuscript.read_text(path)
    os.unlink(path)
    assert "A.[1] B.[3,4] C.[2]" in lines, lines


@test("manuscript: citation ranges expand")
def _():
    assert check_manuscript.citation_numbers("x [1\u20133] y [5, 7-8]") == [1, 2, 3, 5, 7, 8]


# ---------- reference checker (offline) ----------

@test("refs: parses AMA journal reference, ignores 'Phila Pa 1976'")
def _():
    r = check_refs.parse_ref("Fairbank JC, Pynsent PB. The Oswestry Disability Index. "
                             "Spine (Phila Pa 1976). 2000;25(22):2940-2952. PMID: 11074683")
    got = (r["first_author"], r["journal"], r["year"], r["volume"], r["issue"], r["first_page"], r["pmid"])
    assert got == ("Fairbank", "Spine", "2000", "25", "22", "2940", "11074683"), got


@test("refs: page expansion")
def _():
    for a, b in (("968-74", "968-974"), ("2940-52; discussion 2952", "2940-2952"), ("S12-8", "S12-S18")):
        assert check_refs.expand_pages(a) == b, (a, check_refs.expand_pages(a))


@test("refs: compare flags wrong year and retraction")
def _():
    r = check_refs.parse_ref("Doe J. A title here about spine. Spine. 2004;30(1):1-5.")
    s = {"authors": [{"name": "Doe J"}], "title": "A title here about spine.", "pubdate": "2005",
         "volume": "30", "pages": "1-5", "pubtype": ["Journal Article", "Retracted Publication"]}
    p = check_refs.compare(r, s)
    assert p[0] == "RETRACTED" and any("year 2004" in x for x in p), p


# ---------- reference checker (live) ----------

LIVE_REFS = """References
1. Copay AG, Glassman SD, Subach BR, Berven S, Schuler TC, Carreon LY. Minimum clinically important difference in lumbar spine surgery patients: a choice of methods using the Oswestry Disability Index, Medical Outcomes Study questionnaire Short Form 36, and pain scales. Spine J. 2008;8(6):968-974.
2. Glassman SD, Bridwell K, Dimar JR, Horton W, Berven S, Schwab F. The impact of positive sagittal balance in adult spinal deformity. Spine. 2004;30(18):2024-2029.
3. Wakefield AJ, Murch SH, Anthony A, et al. Ileal-lymphoid-nodular hyperplasia, non-specific colitis, and pervasive developmental disorder in children. Lancet. 1998;351(9103):637-641.
4. Made Up A, Fake B. Lumbar fusion outcomes in a population of imaginary patients with fictional disease. Spine. 2019;44(3):100-108.
"""


def live():
    @test("live: PubMed match, wrong year, retraction, fake reference")
    def _():
        refs = check_refs.split_refs(check_refs.reference_block(LIVE_REFS.splitlines()))
        rows = check_refs.check(refs, log=lambda *a: None)
        got = [r["status"] for r in rows]
        assert got == ["OK", "MISMATCH", "RETRACTED", "NOT FOUND"], got
        assert "2005" in rows[1]["ama"], rows[1]["ama"]

    @test("live: Crossref fallback")
    def _():
        r = check_refs.parse_ref("Fairbank JC, Pynsent PB. The Oswestry Disability Index. "
                                 "Spine (Phila Pa 1976). 2001;25(22):2940-2952.")
        it = check_refs.crossref_lookup(r)
        assert it and it.get("DOI"), "no Crossref match"
        p = check_refs.compare(r, check_refs.crossref_as_summary(it), "Crossref")
        assert p == ["year 2001 vs Crossref 2000"], p


if __name__ == "__main__":
    if "--live" in sys.argv:
        live()
    print(f"\n{len(FAILS)} failed" if FAILS else "\nall passed")
    sys.exit(1 if FAILS else 0)
