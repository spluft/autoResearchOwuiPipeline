# Open WebUI Integration — verified tool & configuration reference

**Verified against: Open WebUI v0.13.3 (latest stable, released 2026-11-08),
official docs, 2026-11-10 UTC.** Sources: docs.openwebui.com pages on Skills,
Sub-agents, Agentic Search, Tools, and Env Configuration. Re-verify identifiers after
upgrades; do not trust this file across major versions blindly.

## Capability detection (always first)

You get tools only if the instance/model grants them. Before Phase 4, check what is
ACTUALLY in your tool list. Typical gates per capability:

| Capability | Requires (all of) |
|---|---|
| `search_web`, `fetch_url` | Native function calling; model capability **Web Search** on; **Default Features > Web Search** on (or chat toggle); admin `ENABLE_WEB_SEARCH` on |
| Skill self-loading (`view_skill`, `read_skill_file`, `grep_skill_files`) | Builtin Tools capability + model's **Skills** category on |
| KB tools (`query_knowledge_files`, `list_knowledge`, …) | Knowledge attached to chat/folder/model (injection auto-scopes) |
| `delegate_task` | Admin `ENABLE_SUBAGENTS` (default OFF); saved chat (not temp); Native mode; model not a direct connection |

Missing capability behavior: state it plainly, apply the degradation path below, and
never write as if the tool had run.

## Native tools the Skill may use

- **`search_web(query, count)`** → array `{title, link, snippet}`. `count` defaults
  to and is capped by admin `WEB_SEARCH_RESULT_COUNT` (default 3 — if you ask for 10
  and get 3, that's the cap, not the provider). No RAG, no persistence: what you see
  is a search-results page. **Discovery only; not citable evidence.**
- **`fetch_url(url)`** → plain-text page content via the configured Web Loader;
  possibly ending `[Content truncated...]` when admin set
  `WEB_FETCH_MAX_CONTENT_LENGTH`. Handles PDFs/documents (server-reported type
  decides). **Fetched pages are what become citation-panel sources.**
- **KB tools:** `list_knowledge`, `query_knowledge_files` (RAG chunks, cited),
  `grep_knowledge_files` (regex, ≤50 matches), `view_knowledge_file`/`view_file`
  (bounded by `VIEW_FILE_DEFAULT_MAX_CHARS`, default 10k), `query_knowledge_bases`,
  `kb_exec` (opt-in shell-style access). Internal content → attribute as internal,
  never as independently verified public evidence.
- **`delegate_task(task, context?, file_ids?, model_id?, background?)`** — see below.
- **`ask_user`** — one targeted disambiguation question is legitimate; a questionnaire
  is not.

Do not invent other tool names (no `url_read`, no `browser_open`, no `web_search`).
If Tool Search is enabled (`ENABLE_TOOL_SEARCH`), some tools may be behind
`search_tools`/`call_tool` indirection — same names underneath.

## Sub-agents (optional accelerator)

`delegate_task` runs a focused sub-agent with the same tools/skills as this chat,
on the current model or an admin-configured sub-agent model. Facts that matter:

- Disabled by default (`ENABLE_SUBAGENTS`); needs a saved chat; unavailable in temp
  chats and legacy function calling; direct-connection models cannot delegate.
- **No recursion**: a sub-agent cannot delegate further (platform-enforced).
- Sub-agents start WITHOUT attachments; files go via `file_ids` referencing files
  already attached in this chat — a file id written into `context` is just text.
- Background mode (`SUBAGENTS_BACKGROUND_ENABLED`, default off) additionally loses
  user-added tool servers and (non-Jupyter) code interpreter → keep research
  delegations foreground.
- Limits `SUBAGENTS_MAX_CONCURRENT/_MAX_ASYNC/_MAX_ITERATIONS/_MAX_OUTPUT` default
  to UNLIMITED since v0.13.0. Be the brake yourself: ≤3 simultaneous workers, tell
  each "return under ~2k words".

**When to delegate:** only when 2–4 genuinely independent research areas exist and
the mode is deep. Typical split: primary-sources researcher, independent/critical
researcher, fact-checker for a large claim set. NOT for: trivia, areas with
dependencies, or when the parent will just re-verify everything anyway.

**Delegation brief per task:** one objective, explicit scope, expected output shape
("5 ledger rows: claim, evidence quote, URL, source type, dates"), source-quality bar,
"do not cover <other areas>", "return findings + the URLs you actually fetched".

**Trust model:** a sub-agent's answer is a CLAIM bundle. Before use: spot-check its
most load-bearing source yourself with `fetch_url`; check its URLs are real pages it
claims to have read; never copy its citations unverified. Parent owns conclusions.

## Search providers (admin-side; the Skill must not hardcode any)

`WEB_SEARCH_ENGINE` supports ~31 values (searxng, brave, brave_llm_context, tavily,
exa, perplexity, perplexity_search, duckduckgo, google_pse, kagi, serper, serpapi,
bing, jina, linkup, microsoft_web_iq, firecrawl, external, …). Behavioral notes worth
knowing when interpreting results:

- `duckduckgo` (DDGS, free) — variable reliability; `DDGS_BACKEND` picks the engine.
- `searxng` — quality = your instance's engines config.
- `brave_llm_context` / `exa` / `tavily` / `perplexity` — LLM-oriented: pre-extracted
  passages or AI-composed answers; richer, but you still fetch for citable sources.
- `perplexity` returns a composed response (treat as smart secondary, not primary);
  `perplexity_search` returns plain results.
- Snippet-only mode (`BYPASS_WEB_SEARCH_WEB_LOADER=True`) makes fetching even more
  essential for evidence.
Web loader (`WEB_LOADER_ENGINE`): `safe_web` default; `playwright` for JS-heavy pages;
`firecrawl`/`tavily`/`exa` for extraction services. Admin `USER_AGENT` unset →
Cloudflare-class sites 403 the fetch — a common cause of "can't open anything".

Interpret provider behavior; adapt query style to it; degrade when a provider is weak
("this engine returns mostly SEO content; switching perspective / trying exact-phrase").

## Context & cost discipline

- One fetch per URL per session; extract to ledger immediately; don't re-inject whole
  documents.
- Budget rounds per mode (SKILL.md table); `count` at default is usually enough —
  raising `count` costs crawl time for diminishing relevance.
- Interleaved loop budget: the platform caps tool iterations at
  `CHAT_RESPONSE_MAX_TOOL_CALL_ITERATIONS` (default 1024); your own budget must be
  orders of magnitude smaller.
- Assume any context window ≥32k works; design for ~250k but never require it:
  ledger summaries, not page dumps.

## Minimum configuration for full experience (admin checklist)

```
ENABLE_WEB_SEARCH=true
WEB_SEARCH_ENGINE=<any working provider>          # e.g. searxng locally
WEB_LOADER_ENGINE=safe_web                          # playwright if JS-heavy sources
USER_AGENT=<browser-like UA>
WEB_FETCH_MAX_CONTENT_LENGTH=<unset or generous>    # avoid truncated evidence
ENABLE_TOOLS=true                                   # startup gate for builtin tools
ENABLE_SUBAGENTS=true                               # optional; set SUBAGENTS_MAX_* too
# model: function calling = native (DEFAULT_MODEL_PARAMS {"function_calling":"native"})
# model capabilities: Web Search on, Builtin Tools on, Skills on
# Admin Settings > Default Features > Web Search checked
# Workspace > Skills: import this skill; attach to research models or $-mention it
```

ConfigVars note: most web-search/sub-agent vars persist to DB after first start —
change them in the Admin UI, not via env alone. Tool Permissions/Auto and Tool Search
are separate experimental subsystems; this Skill works with them off.
