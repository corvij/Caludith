# Skills in this repo

Claude Code loads these automatically in any session opened on this repo.

## Written for this repo

| Skill | Use it for |
|---|---|
| `case-prep` | Case plans in `case_plans/` and Anki decks in `anki/`, including missed ResStudy questions. Uses `anki/ankibuild.py` to check and build every deck. |
| `spine-manuscript` | Drafting and checking spine manuscripts for a target journal, reporting checklists, PubMed reference verification. |

## Copied from other repos

Copied unchanged except where noted. To update, copy the folder again from the source commit you want and note the new commit here.

| Skill | Source | Commit | License | Notes |
|---|---|---|---|---|
| `sr-screener` | github.com/Imbad0202/academic-research-skills | 1d42587 | CC BY-NC 4.0 (non-commercial use only, credit Cheng-I Wu) | Five files from the source repo's `shared/` folder are in `sr-screener/shared/`. Its reviewer subagent is `.claude/agents/screening-reviewer-agent.md`. |
| `citation-management` | github.com/K-Dense-AI/scientific-agent-skills | c21d13b | MIT | Google Scholar search may be blocked by Google. |
| `literature-review` | github.com/K-Dense-AI/scientific-agent-skills | c21d13b | MIT | The optional schematic generator sends prompts to OpenRouter and needs an `OPENROUTER_API_KEY`. Not set up here. |

The copied scripts were checked before adding. They only contact PubMed (NCBI E-utilities), Crossref, OpenAlex, DataCite, doi.org, arXiv, and (literature-review schematics only) OpenRouter. None of them run shell commands from untrusted input.

## Network

PubMed, Crossref, and doi.org are blocked in the cloud sessions this repo has been used in. Anything that verifies references needs the desktop app or a local terminal.
