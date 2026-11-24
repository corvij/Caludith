#!/usr/bin/env python3
"""Check a numbered reference list (AMA or Vancouver) against PubMed.

For each reference it finds the PubMed record, compares first author, title,
year, volume, and first page, flags retracted papers, and prints a corrected
AMA citation built from the PubMed record.

Lookup order: PMID or DOI in the reference, then NCBI ECitMatch (journal, year,
volume, first page, first author), then a title search (with the year, then
without it in case the year is the error). A title-search hit counts only if
its title matches at least 85%. References PubMed does not have (books,
chapters, unindexed journals) are then looked up in Crossref.

Usage:
  python3 check_refs.py paper.docx            # reads the References section
  python3 check_refs.py refs.txt              # a file holding only the list
  python3 check_refs.py paper.docx --offline  # parse only, no network
  python3 check_refs.py paper.docx --out refcheck.md

Needs network access to eutils.ncbi.nlm.nih.gov and api.crossref.org. Cloud sessions usually block
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


def title_ratio(a, b):
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def pmid_from_title(r):
    """Title search, first with the year and then without it (the year may be the
    error). Accept a hit only if its title closely matches."""
    if not r["title"] or len(r["title"]) < 15:
        return None
    t = re.sub(r"[^\w\s-]", " ", r["title"])
    terms = [f"{t}[ti] AND {r['year']}[dp]"] if r["year"] else []
    terms.append(f"{t}[ti]")
    for term in terms:
        body = json.loads(get(EUTILS + "esearch.fcgi", {"db": "pubmed", "retmode": "json",
                                                         "term": term, "retmax": "5"}))
        ids = body.get("esearchresult", {}).get("idlist", [])
        if not ids:
            continue
        best = max(summaries(ids).items(), key=lambda kv: title_ratio(r["title"], kv[1].get("title")),
                   default=None)
        if best and title_ratio(r["title"], best[1].get("title")) >= 0.85:
            return best[0]
    return None


def crossref_lookup(r):
    """For references PubMed does not have (books, chapters, some journals)."""
    q = r["raw"][:300]
    url = "https://api.crossref.org/works"
    params = {"query.bibliographic": q, "rows": "3",
              "select": "DOI,title,author,issued,container-title,short-container-title,volume,issue,page,type,update-to"}
    with urllib.request.urlopen(url + "?" + urllib.parse.urlencode(params), timeout=30) as resp:
        items = json.loads(resp.read().decode("utf-8"))["message"]["items"]
    time.sleep(0.2)
    if not r["title"]:
        return None
    for it in items:
        title = (it.get("title") or [""])[0]
        if title_ratio(r["title"], title) >= 0.85:
            return it
    return None


def crossref_as_summary(it):
    """Shape a Crossref item like a PubMed esummary record so compare() and ama() work."""
    authors = []
    for a in it.get("author", []):
        initials = "".join(p[0] for p in re.split(r"[\s.-]+", a.get("given", "")) if p)
        authors.append({"name": f"{a.get('family', '')} {initials}".strip()})
    year = str((it.get("issued", {}).get("date-parts") or [[""]])[0][0] or "")
    journal = (it.get("short-container-title") or it.get("container-title") or [""])[0]
    return {"authors": authors, "title": (it.get("title") or [""])[0], "source": journal,
            "pubdate": year, "volume": it.get("volume", ""), "issue": it.get("issue", ""),
            "pages": it.get("page", ""), "pubtype": [it.get("type", "")],
            "articleids": [{"idtype": "doi", "value": it.get("DOI", "")}]}


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


MAX_AUTHORS = 6  # AMA: list up to 6 authors, else the first 3 and et al. Spine uses 3.


def ama(s):
    names = [a["name"] for a in s.get("authors", []) if a.get("authtype", "Author") == "Author"]
    authors = ", ".join(names) if len(names) <= MAX_AUTHORS else ", ".join(names[:3]) + ", et al"
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


def compare(r, s, src="PubMed"):
    problems = []
    names = [a["name"] for a in s.get("authors", [])]
    pm_first = names[0].rsplit(" ", 1)[0] if names else ""
    if r["first_author"] and pm_first and norm(r["first_author"]) != norm(pm_first):
        problems.append(f"first author '{r['first_author']}' vs {src} '{pm_first}'")
    if r["title"]:
        ratio = difflib.SequenceMatcher(None, norm(r["title"]), norm(s.get("title"))).ratio()
        if ratio < 0.9:
            problems.append(f"title differs ({ratio:.0%} match)")
    pm_year = (s.get("pubdate") or "")[:4]
    if r["year"] and pm_year and r["year"] != pm_year:
        problems.append(f"year {r['year']} vs {src} {pm_year}")
    if r["volume"] and s.get("volume") and r["volume"] != s["volume"]:
        problems.append(f"volume {r['volume']} vs {src} {s['volume']}")
    pm_page = re.split(r"[-,]", s.get("pages", "") or "")[0]
    if r["first_page"] and pm_page and r["first_page"] != pm_page:
        problems.append(f"first page {r['first_page']} vs {src} {pm_page}")
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
            steps = [("DOI", lambda: pmid_from_doi(r["doi"]) if r["doi"] else None),
                     ("citation match", lambda: pmid_from_citmatch(r)),
                     ("title search", lambda: pmid_from_title(r))]
            for via, step in steps:
                if row["pmid"]:
                    break
                pmid = step()
                if pmid:
                    row["pmid"], row["via"] = pmid, via
        except RuntimeError as e:
            log(f"[{n}] {e}")
            row["status"] = "ERROR"
            continue
        if not row["pmid"]:
            row["status"] = "NOT FOUND"
            try:
                it = crossref_lookup(r)
            except Exception as e:
                log(f"[{n}] Crossref lookup failed: {e}")
                it = None
            if it:
                cr = crossref_as_summary(it)
                row["via"] = f"Crossref, doi:{it.get('DOI')}"
                row["problems"] = compare(r, cr, "Crossref")
                row["ama"] = ama(cr)
                row["status"] = "NOT IN PUBMED, " + ("MISMATCH" if row["problems"] else "OK")
    if offline:
        return rows
    try:
        found = summaries([r["pmid"] for r in rows if r["pmid"]])
    except RuntimeError as e:
        log(str(e))
        return rows
    for row in rows:
        s = found.get(row["pmid"]) if row["pmid"] else None
        if row["pmid"] and not s:
            row["status"] = "ERROR"
        if not s:
            continue
        row["problems"] = compare(row["ref"], s)
        row["ama"] = ama(s)
        if row["problems"] and row["problems"][0] == "RETRACTED":
            row["status"] = "RETRACTED"
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
        where = f"  PMID {row['pmid']} ({row['via']})" if row["pmid"] else (f"  ({row['via']})" if row["via"] else "")
        out.append(f"## [{row['n']}] {row['status']}{where}")
        out.append(f"As written: {r['raw']}")
        if offline:
            out.append("Parsed: " + "; ".join(f"{k}={r[k]}" for k in
                       ("first_author", "title", "journal", "year", "volume", "issue", "first_page", "doi", "pmid")))
        for p in row["problems"]:
            out.append(f"- {p}")
        if row["ama"] and row["problems"]:
            out.append(("PubMed" if row["pmid"] else "Crossref") + f" (AMA): {row['ama']}")
        if row["status"] == "NOT FOUND":
            out.append("- Not found in PubMed or Crossref. Check it by hand. Books are often missing from both; a journal article missing from both may not exist as written.")
        out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--offline", action="store_true", help="parse only, no PubMed calls")
    ap.add_argument("--out", help="write the report to this markdown file")
    ap.add_argument("--max-authors", type=int, default=6,
                    help="list all authors up to this many, else the first 3 and et al "
                         "(AMA default 6; Spine uses 3)")
    a = ap.parse_args()
    global MAX_AUTHORS
    MAX_AUTHORS = a.max_authors
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
    if a.offline:
        return 0
    bad = sum(not r["status"].endswith("OK") for r in rows)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
