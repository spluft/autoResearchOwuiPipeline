# Example — Version-Specific Technical Investigation (Standard mode)

> ILLUSTRATIVE example for instruction purposes. Queries, findings and citations
> below are stylized teaching material, NOT actual research results from a run.

**User:** "Does Open WebUI v0.13.3 have a filter hook that lets me deny a tool call
before it executes?"

**Mode pick:** standard — version-pinned technical question; upgrade to deep only if
docs contradict issue-tracker reality.

**Plan (condensed).** Entities: Open WebUI, Filters, tool-call lifecycle, issue
#28279. Scope: exactly v0.13.3 (not main branch). Evidence level: source code or
official changelog — blog posts insufficient. Forbidden assumption: that an issue
closed as "completed" means the feature shipped. Areas: (A) shipped filter API surface
in 0.13.3, (B) status/history of the pre-execution hook.

**Query strategy (distinct purposes).**
1. `open webui filter functions stream event tool calls` — concept/lifecycle docs.
2. `open webui "tool calls" filter deny before execution site:github.com` — the
   feature discussion.
3. `open webui CHANGELOG 0.13 "filters" tool` — shipped-vs-promised (primary).
4. Falsifier: `open webui filter cannot intercept tool execution` — negative reports.

**Discovery findings.** Docs describe inlet/stream/outlet body filters (request-level);
an issue promises a stream hook carrying assembled tool calls; third-party blog says
"filters can block any tool call" (suspicious: keyword match, not lifecycle-aware).

**Fetch + read (evidence, not snippets).** Fetched: official Filters docs page
(shown filter types: no tool-call event documented); the GitHub issue (state, dates,
body verbatim); CHANGELOG lines for 0.13.x ("Filters before approved tool calls" —
i.e., AFTER approval, not pre-execution). Blog post: not fetched; excluded.

**Ledger (excerpt).**

| ID | Claim | Source | Type | Conf | Notes |
|----|-------|--------|------|------|-------|
| C1 | 0.13.3 filters see request body, not assembled tool calls | official docs (fetched) | primary | high | absence documented by enumeration |
| C2 | Promised hook issue closed completed 2026-08-11, no code in 0.13.3 changelog | issue + changelog (fetched) | primary | med | close rationale unread [gap] |
| C3 | "Filters can block any tool call" | blog snippet | secondary | low | not fetched; contradicts C1; excluded from report as FACT |

**Gap round.** C2 has no shipped-code confirmation → query `site:github.com
open-webui 0.13.3 CHANGELOG filters` → fetched release notes; nothing matches the
promised hook → contradiction C1-vs-C2 explained: nominal issue closure ≠ shipped
feature.

**Fact-check pass.** Re-opened the changelog page; quoted line verified verbatim;
issue close-date field re-read (closed_at ≠ created_at — initial draft had it wrong;
corrected).

**Report shape (excerpt).** Answer: *In v0.13.3 the only pre-execution gate is the
core Ask/Auto tool-permission path; Filters cannot see or deny assembled tool calls
(C1, C2). The claim in <blog> (C3) conflicts with the shipped lifecycle docs and is
treated as unverified.* Contradictions section explains completed-issue vs
absent-code. Unresolved: maintainer rationale for the close (what would close it:
read issue comments). Verified through <date>.

**What this example teaches:** version pinning; issue-state vs shipped-code
distinction; refusing the convenient blog source; the falsifier query earning its
keep.
