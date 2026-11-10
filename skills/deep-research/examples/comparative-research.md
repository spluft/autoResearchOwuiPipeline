# Example — Comparative Research (Standard → borderline Deep)

> ILLUSTRATIVE example for instruction purposes. Content is stylized teaching
> material, NOT actual research results from a run.

**User:** "Should our homelab standardize on SearXNG, Brave, or Tavily for agentic
research in Open WebUI?"

**Mode pick:** standard, upgrade once to deep — comparison has four dimensions
(result quality, cost/limits, self-hosting/privacy, Open WebUI integration depth)
and the recommendation is decision-bearing.

**Plan (condensed).** Decision question behind the proxy question: which provider
maximizes research reliability per euro and per hour of admin time on self-hosted
infrastructure. Scope: current offerings (free tiers move!), Open WebUI's documented
integration (primary = OWUI env docs per provider). Forbidden: assuming a provider's
marketing benchmark is neutral.

**Areas:** A result quality/diversity for technical queries; B pricing & rate limits
(primary = provider's own pricing/limits pages); C self-hostability & privacy
(SearXNG-only); D integration behavior in OWUI (`brave_llm_context` pre-extracted
passages vs plain snippets — affects whether you still must `fetch_url`).

**Query strategy sample.** A: `searxng vs brave vs tavily technical search quality`;
B per provider: `site:brave.com search api pricing`, `tavily pricing free tier
requests`; C: `searxng instance block rate ban`; D: `openwebui BRAVE_LLM_CONTEXT
WEB_FETCH_MAX_CONTENT_LENGTH` — integration docs & issues; falsifier: `tavily results
outdated complaints` and `searxng google bang broken`.

**Discovery judgment.** Multiple "best search API 2026" listicles inter-cite → treat
as one weak secondary chain; go to primaries. Community (r/selfhosted, OWUI issues)
valuable for rate-limit pain (undocumented in marketing).

**Fetch plan:** each provider's pricing/limits page (primary for B/C), OWUI env-config
docs (primary for D), 1–2 independent practitioner threads (community, clearly
labeled). One listicle fetched only to check whether it adds data.

**Ledger rows (excerpt).**

| ID | Claim | Source | Type | Conf |
|----|-------|--------|------|------|
| C2 | Brave free tier ≈1 req/s → set WEB_SEARCH_CONCURRENT_REQUESTS=1 | OWUI env docs (fetched) | primary | high |
| C5 | Tavily free quota = N/mo | tavily pricing (fetched) | primary | med — quotas change; date-stamped |
| C8 | `brave_llm_context` returns pre-extracted passages | OWUI docs (fetched) | primary | high |

**Contradiction register (excerpt).** Practitioner thread says SearXNG "stops
returning results" vs SearXNG docs' simplicity. Independence check: thread is about
public instances + upstream engine blocking — real; docs describe self-run
instances. Resolution: not contradictory once instance-type and engine-upstream
dependence are separated → recommendation must distinguish public vs private
SearXNG.

**Comparison table in report:** rows = dimensions, cells = claims + [C-ids], plus a
"cost of being wrong" column. Recommendation section explicitly tagged
**RECOMMENDATION** (depends on user's tolerance for admin work, which is their input,
not a finding).

**What this example teaches:** decision-behind-the-question; primary pricing pages
over listicles; date-stamping volatile facts; separating config-mechanics (OWUI docs)
from provider behavior (provider docs) from folklore (community).
