#!/usr/bin/env python3
"""Check a numbered reference list (AMA or Vancouver) against PubMed.

For each reference it finds the PubMed record, compares first author, title,
year, volume, and first page, flags retracted papers, and prints a corrected
AMA citation built from the PubMed record.

Lookup order: PMID or DOI in the reference, then NCBI ECitMatch (journal, year,
volume, first page, first author), then a title search.

Usage:
  python3 check_refs.py paper.docx            # reads the References section
  python3 check_refs.py refs.txt              # a file holding only the list
  python3 check_refs.py paper.docx --offline  # parse only, no network
  python3 check_refs.py paper.docx --out refcheck.md

Needs network access to eutils.ncbi.nlm.nih.gov. Cloud sessions usually block
it, so run this from the desktop app or a local terminal. Set NCBI_API_KEY to
raise the rate limit and NCBI_EMAIL to identify yourself to NCBI (both optional).
"""

import argparse
import difflib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
TOOL = "refcheck"


# ---------- reading ----------

def read_lines(path):
    if path.endswith(".docx"):
        import docx
        d = docx.Document(path)
        out = []
        for p in d.paragraphs:
            # Word auto-numbered lists lose their numbers in p.text; keep the order.
            out.append(p.text)
        return out
    with open(path, encoding="utf-8") as f:
        return [l.rstrip("\n") for l in f]


def reference_block(lines):
    """Lines after a 'References' heading, up to the next major heading."""
    start = None
    for i, l in enumerate(lines):
        if re.match(r"^\s*#*\s*(references|bibliography|literature cited)\s*:?\s*$", l, re.I):
            start = i + 1
    if start is None:
        return lines
    out = []
    for l in lines[start:]:
        if re.match(r"^\s*#*\s*(figure legends?|tables?|appendix|supplement\w*)\s*:?\s*$", l, re.I):
            break
        out.append(l)
    return out


def split_refs(lines):
    """Return [(number, text)]. Numbered lines start a new reference; others continue it."""
    refs, cur = [], None
    for l in lines:
        if not l.strip():
            continue
        m = re.match(r"^\s*\[?(\d{1,3})[.)\]]\s+(.*)", l)
        if m:
            cur = [int(m.group(1)), m.group(2).strip()]
            refs.append(cur)
        elif cur is not None and not re.match(r"^\s*[A-Z][a-z]+ [A-Z]{1,3}[,.]", l):
            cur[1] += " " + l.strip()
        else:
            cur = [len(refs) + 1, l.strip()]
            refs.append(cur)
    return [(n, t) for n, t in refs]


# ---------- parsing ----------

def parse_ref(text):
    """Pull fields from an AMA or Vancouver journal reference. Missing fields are None."""
    r = {"raw": text, "authors": None, "first_author": None, "title": None, "journal": None,
         "year": None, "volume": None, "issue": None, "first_page": None, "doi": None, "pmid": None}
    m = re.search(r"\b(10\.\d{4,9}/[^\s,;]+[^\s,;.])", text)
    if m:
        r["doi"] = m.group(1)
    m = re.search(r"PMID:?\s*(\d{5,9})", text, re.I)
    if m:
        r["pmid"] = m.group(1)

    # Authors end at the first ". " that follows initials or "et al".
    m = re.match(r"^(.+?(?:\bet al|[A-Z]{1,3}|[A-Z]\.(?: ?[A-Z]\.)*))\.\s+(.*)$", text)
    rest = text
    if m:
        r["authors"], rest = m.group(1), m.group(2)
        first = re.split(r",|;| and ", r["authors"])[0].strip()
        r["first_author"] = re.sub(r"\s+[A-Z]{1,3}\.?$|\s+(?:[A-Z]\.\s?)+$", "", first).strip() or None

    # Title ends at the first period, question mark, or exclamation followed by a space.
    m = re.match(r"^(.+?[.?!])\s+(.*)$", rest)
    if m:
        r["title"], rest = m.group(1).rstrip("."), m.group(2)

    # Journal, then year;volume(issue):pages. "Spine (Phila Pa 1976)" holds a year
    # that is not the publication year, so drop it first.
    rest = re.sub(r"\s*\(Phila Pa 1976\)", "", rest)
    m = re.match(r"^(.+?)\.?\s+((?:19|20)\d{2})[^;:]*;\s*(\d+)?\s*(?:\(([^)]+)\))?\s*:\s*([A-Za-z]?\d+)", rest)
    if m:
        r["journal"], r["year"], r["volume"], r["issue"], r["first_page"] = m.groups()
        r["journal"] = r["journal"].strip().rstrip(".")
    else:
        m = re.search(r"\b((?:19|20)\d{2})\b", rest)
        if m:
            r["year"] = m.group(1)
    return r


# ---------- PubMed ----------

def get(url, params):
    key, email = os.getenv("NCBI_API_KEY"), os.getenv("NCBI_EMAIL")
    params = dict(params, tool=TOOL)
    if key:
        params["api_key"] = key
    if email:
        params["email"] = email
    full = url + "?" + urllib.parse.urlencode(params, safe="|")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(full, timeout=30) as resp:
                body = resp.read().decode("utf-8")
            time.sleep(0.11 if key else 0.35)
            return body
        except Exception as e:  # network errors, 429s
            if attempt == 2:
                raise RuntimeError(f"PubMed request failed: {e}") from None
            time.sleep(1.5 * (attempt + 1))


def pmid_from_doi(doi):
    body = json.loads(get(EUTILS + "esearch.fcgi", {"db": "pubmed", "retmode": "json",
                                                     "term": f"{doi}[doi]"}))
    ids = body.get("esearchresult", {}).get("idlist", [])
    return ids[0] if len(ids) == 1 else None


def pmid_from_citmatch(r):
    if not (r["journal"] and r["year"] and r["volume"] and r["first_page"]):
        return None
    fields = [r["journal"], r["year"], r["volume"], r["first_page"], r["first_author"] or "", "k", ""]
    bdata = "|".join(f.replace("|", " ") for f in fields)
    body = get(EUTILS + "ecitmatch.cgi", {"db": "pubmed", "retmode": "xml", "bdata": bdata})
    last = body.strip().split("\n")[-1].split("|")[-1].strip()
    return last if last.isdigit() else None


def pmid_from_title(r):
    if not r["title"] or len(r["title"]) < 15:
        return None
    t = re.sub(r"[^\w\s-]", " ", r["title"])
    term = f"{t}[ti]" + (f" AND {r['year']}[dp]" if r["year"] else "")
    body = json.loads(get(EUTILS + "esearch.fcgi", {"db": "pubmed", "retmode": "json", "term": term,
                                                     "retmax": "3"}))
    ids = body.get("esearchresult", {}).get("idlist", [])
    return ids[0] if ids else None


def summaries(pmids):
    if not pmids:
        return {}
    body = json.loads(get(EUTILS + "esummary.fcgi", {"db": "pubmed", "retmode": "json",
                                                      "id": ",".join(pmids)}))
    res = body.get("result", {})
    return {p: res[p] for p in pmids if p in res}


# ---------- comparing and formatting ----------

def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>|[^\w\s]", " ", s or "")).strip().lower()


def expand_pages(p):
    """NLM '1234-40' -> AMA '1234-1240'. Text after ';' (e.g. 'discussion 52') is dropped."""
    p = (p or "").split(";")[0].strip()
    m = re.match(r"^([A-Za-z]?)(\d+)-([A-Za-z]?)(\d+)$", p or "")
    if not m:
        return p
    a, b = m.group(2), m.group(4)
    if len(b) < len(a):
        b = a[: len(a) - len(b)] + b
    return f"{m.group(1)}{a}-{m.group(3) or m.group(1)}{b}"


def ama(s):
    names = [a["name"] for a in s.get("authors", []) if a.get("authtype", "Author") == "Author"]
    authors = ", ".join(names) if len(names) <= 6 else ", ".join(names[:3]) + ", et al"
    title = s.get("title", "").rstrip(".")
    journal = re.sub(r"\s*\(Phila Pa 1976\)", "", s.get("source", ""))
    year = (s.get("pubdate") or "")[:4]
    vol, iss = s.get("volume", ""), s.get("issue", "")
    pages = expand_pages(s.get("pages", ""))
    doi = next((i["value"] for i in s.get("articleids", []) if i.get("idtype") == "doi"), "")
    out = f"{authors}. {title}. {journal}. {year}"
    if vol:
        out += f";{vol}" + (f"({iss})" if iss else "")
    if pages:
        out += f":{pages}"
    out += "."
    if doi:
        out += f" doi:{doi}"
    return out


def compare(r, s):
    problems = []
    names = [a["name"] for a in s.get("authors", [])]
    pm_first = names[0].rsplit(" ", 1)[0] if names else ""
    if r["first_author"] and pm_first and norm(r["first_author"]) != norm(pm_first):
        problems.append(f"first author '{r['first_author']}' vs PubMed '{pm_first}'")
    if r["title"]:
        ratio = difflib.SequenceMatcher(None, norm(r["title"]), norm(s.get("title"))).ratio()
        if ratio < 0.9:
            problems.append(f"title differs ({ratio:.0%} match)")
    pm_year = (s.get("pubdate") or "")[:4]
    if r["year"] and pm_year and r["year"] != pm_year:
        problems.append(f"year {r['year']} vs PubMed {pm_year}")
    if r["volume"] and s.get("volume") and r["volume"] != s["volume"]:
        problems.append(f"volume {r['volume']} vs PubMed {s['volume']}")
    pm_page = re.split(r"[-,]", s.get("pages", "") or "")[0]
    if r["first_page"] and pm_page and r["first_page"] != pm_page:
        problems.append(f"first page {r['first_page']} vs PubMed {pm_page}")
    types = [t.lower() for t in s.get("pubtype", [])]
    if "retracted publication" in types:
        problems.insert(0, "RETRACTED")
    if any("erratum" in t or "corrected and republished" in t for t in types):
        problems.append("has an erratum or correction")
    return problems


def check(refs, offline=False, log=print):
    rows = []
    for n, text in refs:
        r = parse_ref(text)
        row = {"n": n, "ref": r, "pmid": r["pmid"], "via": "PMID in reference" if r["pmid"] else None,
               "problems": [], "ama": None, "status": "PARSED"}
        rows.append(row)
        if offline:
            continue
        try:
            if not row["pmid"] and r["doi"]:
                row["pmid"], row["via"] = pmid_from_doi(r["doi"]), "DOI"
            if not row["pmid"]:
                row["pmid"], row["via"] = pmid_from_citmatch(r), "citation match"
            if not row["pmid"]:
                row["pmid"], row["via"] = pmid_from_title(r), "title search"
        except RuntimeError as e:
            log(f"[{n}] {e}")
            row["status"] = "ERROR"
            continue
        if not row["pmid"]:
            row["status"] = "NOT FOUND"
    if offline:
        return rows
    try:
        found = summaries([r["pmid"] for r in rows if r["pmid"]])
    except RuntimeError as e:
        log(str(e))
        return rows
    for row in rows:
        s = found.get(row["pmid"]) if row["pmid"] else None
        if not s:
            continue
        row["problems"] = compare(row["ref"], s)
        row["ama"] = ama(s)
        if row["problems"] and row["problems"][0] == "RETRACTED":
            row["status"] = "RETRACTED"
        elif row["via"] == "title search" and row["problems"]:
            row["status"] = "CHECK MATCH"
        else:
            row["status"] = "MISMATCH" if row["problems"] else "OK"
    return rows


def report(rows, offline):
    out = []
    counts = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    out.append("# Reference check\n")
    out.append(", ".join(f"{k}: {v}" for k, v in sorted(counts.items())) + "\n")
    for row in rows:
        r = row["ref"]
        out.append(f"## [{row['n']}] {row['status']}" + (f"  PMID {row['pmid']} ({row['via']})" if row["pmid"] else ""))
        out.append(f"As written: {r['raw']}")
        if offline:
            out.append("Parsed: " + "; ".join(f"{k}={r[k]}" for k in
                       ("first_author", "title", "journal", "year", "volume", "issue", "first_page", "doi", "pmid")))
        for p in row["problems"]:
            out.append(f"- {p}")
        if row["ama"] and row["problems"]:
            out.append(f"PubMed (AMA): {row['ama']}")
        if row["status"] == "NOT FOUND":
            out.append("- Not found in PubMed. Check it by hand. Books, chapters, and some journals are not indexed.")
        out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--offline", action="store_true", help="parse only, no PubMed calls")
    ap.add_argument("--out", help="write the report to this markdown file")
    a = ap.parse_args()
    refs = split_refs(reference_block(read_lines(a.file)))
    if not refs:
        print("No references found. Put them under a 'References' heading, one per numbered line.")
        return 1
    rows = check(refs, offline=a.offline)
    text = report(rows, a.offline)
    if a.out:
        with open(a.out, "w") as f:
            f.write(text)
        print(f"{len(rows)} references checked -> {a.out}")
    else:
        print(text)
    bad = sum(r["status"] in ("MISMATCH", "RETRACTED", "NOT FOUND", "CHECK MATCH", "ERROR") for r in rows)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
