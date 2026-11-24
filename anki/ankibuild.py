"""Shared builder for Anki cloze decks in this repo.

Each deck script defines its notes and calls build(). This module checks every
note, writes the Anki text import file (.txt), and writes an .apkg (with media)
when genanki is installed.

Note format: a list of (key, text, extra) tuples.
  key   : a question ID (ResStudy) or a tag group such as "Anatomy::Axillary_nerve"
  text  : the cloze Text field (HTML, one line, cues separated by <br>)
  extra : the Back Extra field (HTML, one line). May be empty.

Run a deck script directly: python3 anki/build_<name>.py
Lint any existing .txt deck: python3 anki/ankibuild.py anki/<deck>.txt
Check a case plan or other .md file: python3 anki/ankibuild.py case_plans/<plan>.md
  (.md files are checked for en or em dashes and likely patient identifiers)
"""

import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join(HERE, "media")

CLOZE_RE = re.compile(r"\{\{c(\d+)::")
IMG_RE = re.compile(r"<img[^>]*src=\"([^\"]+)\"", re.I)

# Patterns that suggest patient identifiers. Decks and case plans must not hold
# PHI, so any hit stops the build.
PHI_PATTERNS = [
    (re.compile(r"\bMRN\b|\bmedical record (number|no)\b", re.I), "MRN"),
    (re.compile(r"\bDOB\b|\bdate of birth\b", re.I), "date of birth"),
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "SSN-like number"),
    (re.compile(r"\b(Mr|Mrs|Ms|Miss)\.? [A-Z][a-z]+"), "patient name with title"),
]


def stable_id(*parts):
    """Stable 31-bit ID from text, so rebuilding a deck never duplicates it in Anki."""
    h = hashlib.sha1("::".join(parts).encode()).hexdigest()
    return 1 << 30 | int(h[:7], 16)


def lint_field(label, field):
    """Return a list of problems in one field."""
    problems = []
    if re.search("[\u2013\u2014]", field):
        problems.append("en or em dash")
    if re.search(r"<(?=[\s\d=])", field):
        problems.append('raw "<" (write &lt;)')
    if "\t" in field or "\n" in field:
        problems.append("tab or newline")
    for pat, name in PHI_PATTERNS:
        if pat.search(field):
            problems.append(f"possible patient identifier ({name})")
    return [f"{label}: {p}" for p in problems]


def lint_note(key, text, extra):
    problems = lint_field(f"{key} Text", text) + lint_field(f"{key} Back Extra", extra)
    nums = sorted({int(n) for n in CLOZE_RE.findall(text)})
    if not nums:
        problems.append(f"{key} Text: no cloze deletions")
    elif nums != list(range(1, nums[-1] + 1)):
        problems.append(f"{key} Text: cloze numbers skip ({nums})")
    if text.count("{{") != text.count("}}"):
        problems.append(f"{key} Text: unbalanced {{{{ }}}}")
    for src in IMG_RE.findall(text + extra):
        if not os.path.exists(os.path.join(MEDIA_DIR, src)):
            problems.append(f"{key}: image {src} not found in anki/media/")
    return problems


def card_count(notes):
    return sum(len(set(CLOZE_RE.findall(t))) for _, t, _ in notes)


def build(deck, basename, notes, tags, extra_suffix="", apkg=True,
          deck_id=None, model_id=None, model_name=None, outdir=HERE):
    """Lint, then write <basename>.txt and (optionally) <basename>.apkg.

    tags         : function (key) -> space separated tag string
    extra_suffix : function (key) -> text appended to Back Extra after <br><br>,
                   or a fixed string. Empty means nothing is appended.
    deck_id, model_id : pass the old IDs when rebuilding a deck that is
                   already in Anki. New decks get stable IDs from the deck name.
    """
    problems, rows, seen = [], [], {}
    for key, text, extra in notes:
        suffix = extra_suffix(key) if callable(extra_suffix) else extra_suffix
        if suffix:
            extra = (extra + "<br><br>" if extra else "") + suffix
        problems += lint_note(key, text, extra)
        norm = re.sub(r"\W+", " ", re.sub(r"<[^>]+>", " ", text)).strip().lower()
        if norm in seen:
            problems.append(f"{key}: same Text as {seen[norm]}")
        seen[norm] = key
        rows.append((text, extra, tags(key)))
    if problems:
        print("Build stopped. Fix these first:")
        for p in problems:
            print("  " + p)
        sys.exit(1)

    lines = ["#separator:tab", "#html:true", "#notetype:Cloze",
             f"#deck:{deck}", "#tags column:3"]
    lines += ["\t".join(r) for r in rows]
    txt = os.path.join(outdir, basename + ".txt")
    with open(txt, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"{len(notes)} notes, {card_count(notes)} cards -> {txt}")

    if not apkg:
        return txt, None
    try:
        import genanki
    except ImportError:
        print("genanki not installed (pip install genanki), skipping .apkg")
        return txt, None

    model = genanki.Model(
        model_id or stable_id("model", deck),
        model_name or f"Cloze ({deck.split('::')[-1]})",
        fields=[{"name": "Text"}, {"name": "Back Extra"}],
        templates=[{
            "name": "Cloze",
            "qfmt": "{{cloze:Text}}",
            "afmt": "{{cloze:Text}}<hr id=answer>{{Back Extra}}",
        }],
        css=".card { font-family: arial; font-size: 20px; text-align: left; color: black; "
            "background-color: white; } .cloze { font-weight: bold; color: blue; }",
        model_type=genanki.Model.CLOZE,
    )
    d = genanki.Deck(deck_id or stable_id("deck", deck), deck)
    media = set()
    for text, extra, tag_str in rows:
        d.add_note(genanki.Note(model=model, fields=[text, extra], tags=tag_str.split()))
        media.update(IMG_RE.findall(text + extra))
    pkg = genanki.Package(d)
    pkg.media_files = [os.path.join(MEDIA_DIR, m) for m in sorted(media)]
    out = os.path.join(outdir, basename + ".apkg")
    pkg.write_to_file(out)
    print(f"wrote {out}" + (f" with {len(media)} image(s)" if media else ""))
    return txt, out


def lint_txt(path):
    """Lint an existing Anki text import file. Returns the number of problems."""
    problems, n = [], 0
    with open(path) as f:
        for i, line in enumerate(f, 1):
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            n += 1
            cols = line.split("\t")
            if len(cols) < 2:
                problems.append(f"line {i}: fewer than 2 columns")
                continue
            problems += lint_note(f"line {i}", cols[0], cols[1])
    for p in problems:
        print("  " + p)
    print(f"{path}: {n} notes, {len(problems)} problem(s)")
    return len(problems)


def lint_md(path):
    """Check a markdown file for dashes and likely PHI. Returns the number of problems."""
    problems = []
    with open(path) as f:
        for i, line in enumerate(f, 1):
            if re.search("[\u2013\u2014]", line):
                problems.append(f"line {i}: en or em dash")
            for pat, name in PHI_PATTERNS:
                if pat.search(line):
                    problems.append(f"line {i}: possible patient identifier ({name})")
    for p in problems:
        print("  " + p)
    print(f"{path}: {len(problems)} problem(s)")
    return len(problems)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    n = sum(lint_md(p) if p.endswith(".md") else lint_txt(p) for p in sys.argv[1:])
    sys.exit(1 if n else 0)
