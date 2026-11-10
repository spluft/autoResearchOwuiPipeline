# Deep Research Skill — Evaluation Suite

Status legend for every scenario:

- `EXECUTED` — actually run end-to-end against a real Open WebUI instance (record
  instance version + model + search provider in the result log).
- `SIMULATED` — walked through on paper / in a plain LLM chat with real web tools
  standing in for Open WebUI's built-ins; behavioral expectations checked, UI-level
  citation panel behavior NOT verified.
- `REQUIRES-OWUI` — needs a configured Open WebUI instance (search provider keys,
  skills enabled, sub-agents toggle); not yet executed.

An unexecuted scenario must never be reported as passed.

## Scoring rubric (per scenario, 0–2 each, max 24)

| # | Criterion | 0 | 1 | 2 |
|---|-----------|---|---|---|
| 1 | Research decomposition | copies question into one search | some structure | explicit areas w/ objectives + dependency awareness |
| 2 | Search strategy | one query, rewordings repeated | several queries | queries with distinct perspectives/purposes, exact terms, site-specific, falsification queries |
| 3 | Source diversity | single source or single domain | 2+ sources | primary + independent secondary + (where relevant) community |
| 4 | Primary-source coverage | none fetched | some | key claims rest on official docs/spec/repo/paper |
| 5 | Full-page fetching | snippets only | mixed | claims trace to fetched pages, not snippets |
| 6 | Citation correctness | fabricated/misplaced | minor misattribution | citations next to supported claims, specific documents, no homepage-padding |
| 7 | Fact-checking | absent | partial | independent verification pass on names/versions/dates/citations |
| 8 | Contradiction handling | ignored | noted | competing positions compared, better-supported side argued |
| 9 | Conclusion accuracy | contradicts evidence | mostly right, gaps | matches evidence, uncertainty calibrated |
| 10 | Context/cost efficiency | runaway searches/fetches | acceptable | bounded rounds, selective fetches, no doc re-injection |
| 11 | Graceful degradation | pretends missing tools ran | vague disclosure | explicit limitation disclosure + sequential fallback |
| 12 | Mode selection | deep for trivia / quick for deep | mostly right | right-sized mode, explicit upgrade/downgrade justification |

Pass bar: ≥ 16/24 with no zero on criteria 5, 6, 9 (evidence integrity is non-negotiable).

## Scenarios

### S1 — Simple factual question (expect: Quick mode)
Q: "What is the release year of the first PostgreSQL version?"
Checks: 1–2 searches, primary source (postgresql.org/docs), concise answer + citation;
does NOT spin up a 10-phase ceremony or sub-agents.

### S2 — Current information (expect: Quick/Standard, recency discipline)
Q: "What is the latest stable release of Open WebUI and what changed around tools?"
Checks: date-stamped verification, official releases page fetched, "verified through <date>"
statement, no stale cached knowledge presented as current.

### S3 — Version-specific technical investigation (expect: Standard)
Q: "Does Open WebUI v0.13.3 include a filter hook that can deny tool calls before execution?"
Checks: pins version, consults source/CHANGELOG (primary), distinguishes issue-state vs
shipped-code reality, refuses to answer from secondary blog posts alone.

### S4 — Technical architecture comparison (expect: Standard/Deep)
Q: "Compare SSE vs WebSocket for a self-hosted LLM chat gateway with tool streaming."
Checks: balanced coverage, primary docs for both, comparison table, recommendations
separated from findings.

### S5 — Scientific question requiring evidence evaluation (expect: Deep)
Q: "What does the current evidence say about efficacy of X for condition Y?" (pick a
contested topic, e.g. a supplement or a screening test)
Checks: distinguishes RCTs/meta-analyses vs observational vs expert opinion; names study
designs; avoids both dismissiveness and overclaiming.

### S6 — Conflicting sources (expect: Standard/Deep)
Q: a topic where a vendor doc and independent reports disagree (e.g. "Is browser extension
A privacy-safe?" vendor claims vs independent audits).
Checks: contradiction register populated; independence of sources assessed; better-supported
position argued, unresolved residue disclosed.

### S7 — Hard-to-find primary sources (expect: Deep)
Q: "Who first proposed <concept> and in which original paper/talk?" where secondary blogs
cite each other circularly.
Checks: traces citation chain back to the original; refuses to cite "a blog citing a blog";
records inaccessible-primary attempts in the ledger's rejected-sources log.

### S8 — Knowledge Base + public sources combined (expect: Standard) [REQUIRES-OWUI]
Setup: upload a project spec doc to a Knowledge Base.
Q: "Does our spec's architecture comply with the current official requirements of framework X?"
Checks: internal-KB claims attributed to the internal doc, NOT presented as independently
verified public evidence; external requirements fetched from official docs.

### S9 — Web Search unavailable (expect: honest degradation) [REQUIRES-OWUI]
Setup: disable web search (or select a model without search tools).
Q: any S2-style current-information question.
Checks: states the limitation, does not invent citations, offers knowledge-based answer
clearly labeled as unverified against live sources; does not claim to have searched.

### S10 — Deep research with several independent areas (expect: Deep + delegation if enabled)
Q: "Evaluate whether our homelab should standardize on search provider P1 vs P2 vs P3 for
agentic research: quality, cost, rate limits, privacy, self-hosting."
Checks: multi-area plan, bounded rounds, evidence ledger, fact-check pass, sub-agents only
if enabled and each with single objective; sequential fallback equivalent quality; final
report follows template, gates A–F reported.

## Result log

| ID | Scenario | Status | Date | OWUI version | Model | Provider | Score | Notes |
|----|----------|--------|------|--------------|-------|----------|-------|-------|
| S1–S10 | (fill on execution) | | | | | | | |
