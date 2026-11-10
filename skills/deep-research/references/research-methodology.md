# Research Methodology — full phase specification

Load this at the start of standard/deep mode. SKILL.md holds the compact version;
this file is the authority when detail matters.

## Phase 1 — Understand the request

Before searching anything, establish:

- **The actual research question.** Restate it in one sentence. Users often ask a
  proxy question ("is X good?") for a real decision ("should we migrate?"). Answer
  the real one; note the distinction.
- **Key entities & terminology:** products, projects, people, orgs, standards,
  acronyms, non-English synonyms worth querying.
- **Temporal scope:** "current" as of what date? Which versions/releases are in
  play? Historical questions need the time of the event, not today's framing.
- **Geographic/organizational scope** where it changes the answer.
- **Required evidence level:** a snippet suffices for trivia; version-specific
  technical claims need official docs or source code; scientific claims need study
  designs.
- **Ambiguity:** alternative interpretations. If one interpretation is 90% likely,
  proceed and state the reading; if genuinely 50/50 and expensive, ask one targeted
  question.
- **Forbidden assumptions:** what you must NOT assume (that a feature exists in the
  user's version, that a vendor's claim is current, that two same-named things are
  the same thing).
- **Pre-conditions:** what must be established before anything else makes sense
  (e.g. "which product is actually meant", "what version is deployed").

## Phase 2 — Decompose

Split complex questions into 2–6 independent research areas. For each:

- objective (one sentence), key questions (bullets), relevant terminology,
  likely primary sources, required evidence (what closes the area),
  potential contradictions, expected output.

Reject subtasks that do not contribute to the main question — a decomposition into
ten decorative buckets is worse than three honest ones. For complex topics, build a
**dependency map**: which questions must be answered before others can be scoped
(e.g. you cannot compare "performance" before you know which versions are compared).

## Phase 3 — Search strategy generation

Several complementary queries per area; every query has a stated purpose and a
distinct perspective from this list:

1. **General concept** — how the topic is discussed at large.
2. **Exact terminology / named entities** — quoted phrases, official names, acronyms,
   translations, common misspellings.
3. **Official documentation & primary sources** — `site:`-style limits if the engine
   supports them; "official documentation", "specification", "RFC", "whitepaper".
4. **Technical implementation / source code** — repository paths, issue tracker terms,
   commit/release-note wording, config key names.
5. **Scientific papers / formal studies** — when the domain has them: study names,
   "meta-analysis", "randomized", journal/preprint venues.
6. **Independent analysis / expert commentary** — practitioners unaffiliated with the
   vendor.
7. **Critical perspectives & documented failures** — "problems with", "limitations
   of", "why X failed", "security issues", "known bugs".
8. **Recency / version-specific** — year, release name, "changelog", "breaking
   changes".

Do not repeat a query with cosmetic rewording. If a query returns junk, change the
perspective, not the adjectives. Include at least one **falsification query** per
critical claim — search for evidence the claim is WRONG.

## Phase 4 — Initial discovery

Run the first round. For each hit judge: relevance to the actual question, authority
of the publisher, recency, originality (is this the origin or a copy), source
independence (two outlets reprinting one wire story = one source), presence of primary
evidence, detectable bias (vendor blog, affiliate content). Build a preliminary
source map: strong primary candidates / useful secondary / community signal / missing
areas / suspected contradictions / pages that must be fetched.

Search snippets are discovery material, never evidence for complex claims.

## Phase 5 — Full-page source investigation

Fetch relevant sources and read the original documents. Per inspected source record:
exact title, publisher/author, URL, publication date, last-updated if available,
access date, source type, relevant findings, specific supporting evidence,
limitations, conflicts of interest, your confidence.

Rules:

- Never infer page contents from title or snippet.
- Inaccessible (paywall, 403, JS-required, truncated): log in the ledger's
  rejected-sources table with consequence; never write as if it were read.
- Follow links discovered inside fetched pages when they lead to the primary source
  (the doc page links the RFC; fetch the RFC).
- For software: prefer the project's own repo/docs/issues over third-party tutorials
  explaining the feature.

## Phase 6 — Evidence extraction (ledger)

Maintain the ledger continuously (see `templates/evidence-ledger.md`). Keep strictly
distinct: established facts, claims made by a source, interpretations, hypotheses,
recommendations, unverified assumptions. Consequence of blurring them: the report
launders an opinion into a fact.

## Phase 7 — Iterative research and gap detection

After each round, audit every area:

- Have all key questions been answered?
- Are sources authoritative enough for the evidence level set in Phase 1?
- Have primary sources been located (not just articles about them)?
- Any claim resting on a single source that matters?
- Is the information current enough for the question?
- Any unresolved technical detail a practitioner would notice?
- Any contradiction still unexplained?

Turn each gap into a targeted query: find the original spec behind the secondary
article; the actual source-code implementation behind a documentation claim; known
limitations and failure reports; whether a feature exists in the EXACT version
asked about; independent evidence challenging the attractive conclusion; whether an
apparent contradiction is just a version difference.

Stop when additional searches are unlikely to materially change the conclusion, or
when remaining gaps are explicitly documented. Respect mode budgets (SKILL.md table);
budget exhaustion forces "document gaps and conclude", not silent overrun.

## Phase 8 — Contradiction analysis

Actively attempt to disprove preliminary conclusions — do not optimize for confirming
the first hypothesis. For each important disputed claim: enumerate the competing
explanations; inspect the evidence behind each; compare source dates and versions;
check genuine independence (did both sides use the same original measurement?);
identify methodology/context differences; state which explanation is better
supported and why. If reliable sources simply agree, do not stage a fake debate. If
the contradiction survives your analysis, keep it visible in the report.

## Phase 9 — Independent fact-checking

A dedicated pass BEFORE final synthesis — an independent evaluation of the research,
not a restatement of conclusions. See `references/fact-checking.md` for the full
checklist. Log what was checked and what failed/downgraded.

## Phase 10 — Synthesis

Answer the ORIGINAL question; explain how findings relate; do not emit a string of
source summaries. Follow `templates/final-report.md`. No new claims may appear in
Conclusions that are not established above. Citations sit next to the claims they
support and point to fetched documents. State "verified through <date>". Run gates
B–F and report them.
