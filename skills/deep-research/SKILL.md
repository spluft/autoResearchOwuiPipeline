---
name: deep-research
description: Conducts disciplined multi-round research using search and page-fetch tools, with an evidence ledger, contradiction analysis, independent fact-checking and a fully cited report. Use for technical, scientific, comparative or current-information questions where verified evidence matters more than speed, or when the user asks for deep research. Supports quick, standard and deep modes and degrades honestly when search, fetch or sub-agent tools are unavailable.
---

# Deep Research

Turns this chat into a research analyst: understands the real question, plans,
searches with purpose, fetches and reads actual sources, keeps an evidence ledger,
hunts contradictions, fact-checks, then writes a structured cited report.

It does NOT: invent sources, answer current-events questions from training memory,
run heavy ceremony for trivia, or claim tools ran when they are not available.
It assumes: Open WebUI Native (Agentic) mode with built-in tools enabled. Everything
else is detected and degraded from, not assumed.

## When to Use

Activate for any question where being wrong would be expensive or where the user
wants sources: technical investigations ("does feature X exist in version Y"),
comparisons and recommendations, scientific/evidence questions, current information,
historical attribution, multi-dimensional "investigate X" requests.

Stay out of: trivial lookups the model can answer reliably, pure writing/coding tasks,
and questions already answered by attached Knowledge Base documents (answer from KB,
cite it, done).

Choose the least expensive mode that can reliably answer — never default to deep:

| Mode | For | Budget (hard caps) |
|---|---|---|
| `quick` | simple facts, single-fact current info | ≤2 search rounds, ≤4 fetches |
| `standard` | technical questions, comparisons, multi-dimension | ≤3 search rounds, ≤15 fetches |
| `deep` | explicit "deep research", complex multi-area, contested claims | ≤5 search rounds, ≤30 fetches |

User override: "quick research", "standard research", "deep research" set the mode
explicitly. You may downgrade (state why) or upgrade once (state why); say so in one
line before proceeding.

## Prerequisites

None required — but capability determines the quality ceiling:

- `search_web` + `fetch_url` → external research. Without them you cannot verify
  anything public: say so, answer only from provided documents/your knowledge, and
  label every factual claim as UNVERIFIED. Never simulate searching.
- Knowledge tools (`query_knowledge_files`, `list_knowledge`) → internal research.
- `delegate_task` → optional parallel research; if absent, run the same methodology
  sequentially.
- Native function calling; a browser-like `USER_AGENT` (admin setting; empty UA gets
  403 from Cloudflare-class sites); `WEB_SEARCH_ENGINE` configured by admin.

Full environment checklist and tool semantics: read
`references/openwebui-integration.md` (via `read_skill_file`) when setup or tool
behavior is in doubt.

## How to Run

1. Detect available tools for this chat (what is actually in your tool list, nothing
   assumed).
2. Instantiate a research plan — follow `templates/research-plan.md`: restate the
   question, scope, entities, research areas, search strategy, mode, budgets. Keep it
   short (it is working material, not a deliverable).
3. Execute the Procedure below. Maintain the evidence ledger per
   `templates/evidence-ledger.md` in your visible notes as you go — a claim with no
   ledger row never reaches the report.
4. Pass the gates, then write the report per `templates/final-report.md`.

For standard/deep mode, first read `references/research-methodology.md` and follow it
phase by phase; consult other references on demand (pointers below).

## Quick Reference

- `search_web(query, count)` → `{title, link, snippet}` list = DISCOVERY ONLY.
  Snippets are not evidence and are not citable. Never cite a search-results page.
- `fetch_url(url)` → page text (watch for `[Content truncated...]`) = EVIDENCE.
  A source counts as inspected only after you fetched it. Fetched pages are what
  populate the citation panel.
- KB tools query internal documents; label their content as internal, never as
  independently verified public evidence.
- Citation mechanics & anti-patterns: `references/citation-policy.md`.
- Worked examples: `examples/technical-research.md`,
  `examples/comparative-research.md`, `examples/current-information-research.md`.
- `delegate_task(task, context, model_id)` — only if present; one objective per
  delegation; no nesting exists; treat returned findings as CLAIMS until you spot-
  check their key source yourself.
- Query perspectives (rotate, never reword-rehash): concept / exact term & acronym /
  official docs / source code & issues / papers & standards / expert analysis /
  criticism & known failures / recency & version-specific.

## Procedure

**Phase 1 — Understand.** Extract the real question, entities, terminology, temporal
and version scope, evidence level required, ambiguity. Separate "what the user asked"
from "what must be established". List forbidden assumptions. Gate A.

**Phase 2 — Decompose.** Split into 2–6 independent research areas, each with
objective, key questions, likely primary sources, required evidence. Note dependencies
between areas. Drop areas that don't serve the question.

**Phase 3 — Plan queries.** Per area, 2–5 queries with distinct perspectives and an
explicit purpose each. Include at least one falsification query (search for the claim
being WRONG). `references/research-methodology.md` §3.

**Phase 4 — Discover.** Run first search round. Judge results for relevance,
authority, recency, independence, bias; build a source map: primary candidates,
useful secondary, community, gaps, suspected contradictions. Quick mode may stop here
with verified concise answer (primary source fetched).

**Phase 5 — Fetch and read.** Fetch the pages that carry evidence — full text, not
titles. Record per source: title, author/publisher, URL, pub/updated/access dates,
type, findings, limitations. Unread = inaccessible: log it in the ledger's rejected
sources table, never fabricate its contents. `references/source-evaluation.md` for the
hierarchy (official docs/specs/repos/papers > institutions > specialist press >
community; contextual, not absolute).

**Phase 6 — Evidence ledger.** One row per important claim with the full field set;
tag epistemic status: FACT / CLAIM(source) / INTERPRETATION / HYPOTHESIS / ASSUMPTION /
RECOMMENDATION. A source's opinion never becomes FACT. Single-source critical claim caps
at medium confidence.

**Phase 7 — Iterate on gaps.** Re-audit each area: unanswered? only snippets? no
primary source? single-sourced critical claim? stale? contradiction unexplained?
Generate new targeted queries from the gaps (find the spec behind the blog post, the
source code behind the doc claim, the failure reports behind the marketing). Stop when
further searches cannot materially change the conclusion, or when gaps are documented.
Respect mode budgets.

**Phase 8 — Contradictions.** For disputed claims: both positions with sources and
dates, independence check, version/methodology differences, which side is better
supported and why. Don't manufacture disagreement; don't hide real disagreement.

**Phase 9 — Fact-check (dedicated pass).** Re-verify independently: names, dates,
versions, numbers, cited URLs resolve, quotes are from the fetched page, attributions
correct. Software claims → official docs/source/issues of the EXACT version. Scientific
→ evidence ladder (meta-analysis > RCT > observational > expert opinion).
`references/fact-checking.md`. Fix or downgrade every failure; report the pass.

**Phase 10 — Synthesize.** Structure the answer per `templates/final-report.md`:
executive summary → main findings → detailed investigation (by area, not by source) →
comparisons → contradictions & limitations → conclusions → recommendations (only if
asked, tagged) → unresolved questions → numbered sources with dates and what each was
used for. Citations sit next to the claims they support. State "verified through
<date>". Gates B–F.

## Tool Usage Rules

- Fetch before citing. If a page cannot be fetched, either find an alternative source
  or present the claim as unverified with the limitation disclosed.
- Never open every search hit; fetch sources that passed the Phase-4 filter.
- Never re-fetch a page already read this session — use the ledger.
- One source cannot support claims it does not establish; check the sentence you are
  actually citing for.
- If `fetch_url` truncates a page mid-claim, treat the claim as partially verified and
  say so.
- Keep total injected page text lean: extract findings into ledger rows immediately;
  don't re-quote whole documents.

## Completion Gates (report each as passed or state why impossible — never fake)

Detail and mode-specific expectations: `references/research-completion-criteria.md`.

- **A Scope** — question and boundaries understood.
- **B Coverage** — every material area investigated (or gap-documented).
- **C Evidence** — key conclusions rest on fetched primary/independent sources.
- **D Contradictions** — competing explanations evaluated.
- **E Verification** — fact-check pass executed.
- **F Completion** — report traceable to ledger; residual uncertainty transparent.

Deep mode additionally requires: primary source inspected for every critical claim,
≥1 falsification round executed, fact-check pass reported explicitly.

## Pitfalls

- Snippet-as-evidence: the most common failure. Titles and snippets are discovery
  material only.
- Circular sourcing: five blogs citing one press release = one weak source. Trace to
  the origin.
- Version drift: answering about "v2" while the primary doc describes "v3". Pin
  versions early; verify version-specific claims against that version's artifacts.
- Confident memory: training knowledge presented as current fact. For anything dated,
  versioned, or contested — verify live or label UNVERIFIED.
- Citation laundering: citing a homepage for a specific claim, or attaching a source to
  a neighboring sentence it doesn't support.
- Ceremony bloat: running the full 10-phase pipeline for "what year did X ship".
  Quick mode exists.
- Delegation without verification: a sub-agent's summary is CLAIM until checked.
- Silent tool absence: never write "I searched" when `search_web` was unavailable.

## Verification (one focused check before you finish)

Pick your two most load-bearing conclusions; for each, name the ledger row and the
exact fetched URL that establishes it. If you cannot, the report is not done — go back
to Phase 7. Then confirm the citation panel/list contains only pages you actually
fetched.
