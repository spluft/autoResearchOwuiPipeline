# Example — Current-Information Research + Honest Degradation (Quick mode)

> ILLUSTRATIVE example for instruction purposes. Content is stylized teaching
> material, NOT actual research results from a run.

**User:** "What's the latest stable Open WebUI release and anything important about
tool calling in it?"

**Mode pick:** quick. Single fact + one bounded follow-up. Two search rounds, ≤4
fetches, done — the ceremony would be a failure, not a feature.

**Execution sketch (happy path, tools available).**

1. Memory offers a plausible answer → **must not ship it**: version numbers are
   exactly the class of claim that goes stale in days. Verify or label UNVERIFIED.
2. `search_web("open webui latest release")` → discovery; a result naming a version
   is a HYPOTHESIS, not evidence.
3. `fetch_url("https://github.com/open-webui/open-webui/releases")` (or the releases
   API) → primary; note the non-prerelease tag and its publish timestamp. That fetch
   is what makes the page citable in the citation panel.
4. Targeted follow-up fetch: that release's notes page → grep mentally for
   tools/search-related lines; quote at most a short phrase.
5. Answer: one paragraph, version + date + "verified through <today>", 1–2 citations
   to fetched pages. Fact-check light: does the tag say `latest`, is it non-prerelease?

**Degradation path — Web Search unavailable** (tools missing from this chat):

> ⚠️ Search tools aren't available in this chat, so I can't verify current state.
> As of my training data … [claim] — **UNVERIFIED against live sources and possibly
> outdated.** Enable Web Search (admin `ENABLE_WEB_SEARCH` + model capability + chat
> toggle) and ask again for a verified answer with a verified-through date.

Never: "I searched and found…" (false claim); never emit plausible-looking URLs;
never cite a version number without a fetched source or the UNVERIFIED tag.

**Degradation path — fetch broken but search works** (e.g. empty `USER_AGENT` →
Cloudflare 403s): report the pattern ("4 of 5 sources returned 403 — likely the
instance's USER_AGENT setting"), cite what genuinely fetched, mark snippet-only
claims as such, and suggest the admin fix. Partial evidence honestly labeled beats
confident fiction.

**What this example teaches:** quick-mode economy; the dated-fact rule; the three
truth-tiers (verified+fetched / snippet-only / unverified memory); turning an
infrastructure failure into a diagnosable, actionable disclosure.
