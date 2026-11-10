---
title: OWUI Auto mode — /decisions экосистема, #28279, per-user
date: 2026-11-09
tags: [owui, security, research]
related: [[deep-owui-automode-2026-11/report]] [[open-webui]]
source: docs вендоров, GitHub API, tarball v0.13.3
---

# 03 — Round-2: /decisions ecosystem, #28279 filter-hook status, per-user mode config
Date: 2026-11-09 | Round-2 leaf. Complements 01-code-anatomy.md + 02-community-issues.md; nothing re-derived.
Local source for code greps: `src/open-webui-0.13.3/` (tarball from code leaf).

## F1. (Q1) `/decisions` is OpenAI's official Decisions API — OWUI's default points straight at it
**Rationale:** Explains the odd default `gpt-6-luna` @ `https://api.openai.com/v1` (01-F1); tells us the wire format is not OWUI-invented.
**Evidence (VERBATIM, OpenAI developer guide, developers.openai.com/api/docs/guides/decisions, fetched 2026-11-09 via search):** "| `predicate` | Check a condition, such as visible damage or passage relevance. | `probability`: an estimate from 0 to 1 that the condition is true. |" — with `client.decisions().create(DecisionCreateParams.builder().model("gpt-6-luna")...`. Request shape (`model`, `input`, `questions[]` of `{type,name,instructions}`) and response `answers[]` with `probability` match OWUI's payload/parser (01-F3) exactly.
**Summary:** The /decisions contract is OpenAI's Decisions API (predicate/choice/score question types); OWUI is one of its clients. Compatible servers must speak this dialect.
**URL/date/type:** https://developers.openai.com/api/docs/guides/decisions | 2026-11-09 | official vendor docs (search snippet; not fully fetched).
**Confidence:** high.
**Follow-ups:** none.

## F2. (Q1) OWUI itself ships NO decisions server — client only
**Evidence:** `grep -rn "'/decisions'" --include='*.py' backend/open_webui` → **no matches** (verified v0.13.3). Only consumers: `utils/tool_search.py` `post_decisions` (01-F3) and config validation in `routers/chats.py:52,71-74`. [no-quote, negative-evidence]
**Summary:** Open WebUI never serves /decisions; engine `decisions` requires an external compatible server (OpenAI or a gateway). Self-hosting = run a compatible server ourselves (see F3, LiteLLM/Bifrost are FOSS-compatible paths).
**URL/date/type:** local v0.13.3 tarball grep | 2026-11-09 | source inspection.
**Confidence:** high.
**Follow-ups:** none.

## F3. (Q1) 2026 vendor ecosystem: OpenAI native + gateways; "jev" = TypeSafe Jev (also on OpenRouter), "Decider" = Perplexity's
**Rationale:** Answers "who serves /decisions in 2026" incl. the Reddit user's "jev or Decider 2B".
**Evidence (VERBATIM):** Bifrost docs provider table: "| [OpenRouter](...) | `openrouter/~typesafe/jev-latest` | `/v1/decisions` | ..." and its OpenRouter operations table: "| Decisions | ✅ | - | `/v1/decisions` |" (docs.getbifrost.ai, fetched 2026-11-09) → OpenRouter serves decision models and a native decisions endpoint reachable through gateways. Bifrost blog: "One request format across all Decision model providers ... TypeSafe's Jev is the default decision classifier" (models `typesafe/jev-1.13.0`–`jev-1.14.0`, native API `/v1/systemone`). Portkey: `curl https://api.portkey.ai/v1/decisions ... "model": "jev-latest"` w/ provider `typesafe`. LiteLLM: "The Endpoint selector picks /v1/decisions (OpenAI Decisions format) or /v1/systemone (System One format)" (docs.litellm.ai/docs/decisions). TrueFoundry lists TypeSafe Jev + Cloudflare Clef (`@cf/cloudflare/clef`). "Decider": towardsai benchmark — "Jev, Clef and Perplexity's decider say `noul`" (i.e., Perplexity has a decider model family).
**Summary:** Implementors/servers: OpenAI (native), OpenRouter (hosts `~typesafe/jev-*`), gateways LiteLLM, Bifrost (8 providers), Portkey, TrueFoundry. "jev"=TypeSafe Jev (small classifier family); "Decider"=Perplexity decider; "JEVA"=no such product found (likely garbling of Jev); exact "Decider 2B" size unconfirmed [no-quote]. **Dialect caveat:** Portkey's doc example uses dict-shaped `questions`/`answers` + `state` instead of OpenAI's list + `input` — only the OpenAI dialect matches OWUI's `parse_decision_scores` (01-F3); Portkey-format replies would fail parse → fail-closed [inference, not tested].
**URL/date/type:** docs.getbifrost.ai/quickstart/gateway/decisions + /providers/supported-providers/openrouter, docs.litellm.ai/docs/decisions, docs.portkey.ai/docs/product/ai-gateway/decisions-api, truefoundry.com/docs/ai-gateway/decisions, pub.towardsai.net jev-vs-clef article | all 2026-11-09 | vendor docs (Bifrost page fully fetched; others search-served).
**Confidence:** high on ecosystem; medium on dialect claims (Portkey inference).
**Follow-ups:** does our new-api gateway expose /decisions? (not found here — [LACK_OF_DATA: new-api decisions endpoint support]); test LiteLLM/Bifrost against a local GPU review model.

## F4. (Q2) Issue #28279: CLOSED as completed 2026-08-11 — but no filter tool-call hook shipped in v0.13.3
**Rationale:** Parent's Q2 final-state question.
**Evidence (VERBATIM, GitHub API 2026-11-09):** state `closed`, state_reason `completed`, `closed_at 2026-08-11T09:48:29Z`, labels `[]`, `pull_request: null`. Body: "Add a point where a filter can see the tool calls a model asked for, before any of them run, and deny them. Core ships the hook, deployments ship the policy." Design: "No new filter method. This reuses `stream` ... Core sends the assembled calls through `stream` as one more event carrying a field a filter can test on".
**Summary:** Marked completed ~3 months before Auto even shipped (Auto = 0.13.1, 2026-11-03). No CHANGELOG line references 28279 (`grep -n '28279' CHANGELOG.md` → empty, verified) and no release description matches the hook.
**URL/date/type:** github.com/open-webui/open-webui/issues/28279 | API 2026-11-09 | GitHub issue.
**Confidence:** high on state/quotes; medium on *why* closed-completed (maintainer call vs Auto-counted-as-answer).
**Follow-ups:** read issue comments (API, 1 call) to see maintainer's close rationale.

## F5. (Q2) v0.13.3 filter API reality: no pre-execution tool-call interception for Filters
**Evidence (VERBATIM, `utils/middleware.py:3206-3225`, execute_tool_call):** `requires_approval = await requires_tool_approval(form_data, metadata, tool_call, tool, params)` → `tool_call['status'] = 'pending'; raise ToolApprovalRequired`, else `event_caller({'type': 'confirmation', 'data': {'tool_call': {'id': ..., 'name': name, 'arguments': params}}})`. Stream filters dispatch only via `process_filter_functions(...)` on the request body (`middleware.py:2141-2153,2333-2336`); `grep -rn "'type': 'tool..." --include='*.py'` finds only sources/anthropic events, **no tool_calls event to filters** [no-quote, negative grep]. Closest shipped thing (VERBATIM, CHANGELOG line 895, 0.12.x): "🚦 **Filters before approved tool calls.** After you approve a tool call, request filters now check the request before the tool runs, where the tool ran first and a filter rejecting the request came only after its effects".
**Summary:** The only pre-run gate is core's own `requires_tool_approval` (Ask/Auto) + a `confirmation` event to the websocket event-caller — not filter authorship. Filters can veto the *request* (inlet/stream body) but cannot see or deny assembled tool calls per-call. Policy-as-code via Filter Functions (#28279) is still NOT possible in v0.13.3; the Decisions-engine endpoint is the only programmatic policy hook.
**URL/date/type:** local v0.13.3 tarball + CHANGELOG.md | 2026-11-09 | source inspection.
**Confidence:** high.
**Follow-ups:** check if any Function (not Filter) example exploits `confirmation`; check issue comments for the promised-but-maybe-unmerged hook.

## F6. (Q3) Per-user default mode: YES — user-chosen, persisted server-side in user settings
**Evidence (VERBATIM, `src/lib/components/chat/Chat.svelte:549-573`):** `$: toolApprovalMode = resolveToolApprovalMode(params?.tool_approval_mode ?? $settings?.params?.tool_approval_mode, ...)` ... `await saveParam('tool_approval_mode', tool_approval_mode);` and `await updateUserSettings(localStorage.token, { ui: { params: $settings.params } }).catch(...)`. Same pattern in `SideChat.svelte:157`. Resolver: `src/lib/utils/toolPermissions.ts:3`.
**Summary:** Each user's chosen mode persists to their server-side user settings (`settings.ui.params.tool_approval_mode`) and becomes that user's default for new chats — matches docs "Users who have not chosen a mode get Auto" (02-F1). It is entirely self-serve: no Settings-page admin surface for it (frontend grep for `tool_approval_mode` hits only Chat.svelte + SideChat.svelte [no-quote, negative grep]).
**URL/date/type:** v0.13.3 source | 2026-11-09 | source inspection.
**Confidence:** high.
**Follow-ups:** confirm UI location users change it in (InputMenu, 01-F8).

## F7. (Q3) Admin per-user/per-group forcing: NOT supported — only soft per-model defaults, always overridable
**Evidence (VERBATIM, `backend/open_webui/main.py:1201-1216`):** `default_model_params = copy.deepcopy(await Config.get('models.default_params', {}) or {})` → `model_info_params = merge_model_params(default_model_params, model_info.params...)` → `request_params = {key: value for key, value in (form_data.get('params') or {}).items() if value is not None}` → `form_data['params'] = merge_model_params(model_info_params, request_params)`; then `resolve_tool_approval_mode(form_data.get('params', {}).get('tool_approval_mode'), ...)` (`main.py:1301-1305`). Whitelist: `'tool_approval_mode': str` in `open_webui_params` (`utils/payload.py:118,174`).
**Summary:** Admins CAN seed a default `tool_approval_mode` via Admin model-defaults (`models.default_params` / per-model Advanced Params, since it's a whitelisted param) — and via group-scoped model access this becomes a per-group *default*. But request params merge last: an explicit client choice always overrides it, and `resolve_tool_approval_mode` never consults user/group (01-F2). Hard gates exist only globally: `ENABLE_TOOL_PERMISSIONS` / `ENABLE_TOOL_PERMISSIONS_AUTO` (off→`full`, auto-off→saved auto downgrades to `ask`) + channel-forcing. No per-user override lock, no "user may not pick full" flag.
**URL/date/type:** v0.13.3 source | 2026-11-09 | source inspection.
**Confidence:** high.
**Follow-ups:** family workaround: give Марина a model whose admin-set default is `ask` AND verify frontend can't flip it (it can — so this is comfort, not enforcement); real enforcement = PR upstream (per-group policy in `resolve_tool_approval_mode`).

## Bottom line for parent:
Q1: `/decisions` is OpenAI's official Decisions API (predicate/`probability` contract, default model `gpt-6-luna` = OpenAI's); OWUI ships only the client — servers come from OpenAI, OpenRouter (hosts TypeSafe **Jev** = the Reddit "jev", as `~typesafe/jev-*`), and gateways LiteLLM / Bifrost / Portkey / TrueFoundry; "Decider" is Perplexity's decider family, "JEVA" doesn't exist. LiteLLM speaking "OpenAI Decisions format" is our self-host path for a local review model (verify dialect strictly; Portkey's dict dialect would fail-closed). Q2: #28279 is closed-as-**completed** (2026-08-11) but the promised stream-filter tool-call hook is **absent in v0.13.3** — filters still cannot intercept tool calls before execution; core's Ask/Auto gate + the Decisions endpoint are the only pre-run policy points, so the upstream close looks nominal (read issue comments for rationale). Q3: per-user mode = user-self-serve default persisted in user settings (`settings.ui.params.tool_approval_mode`); admins can seed soft per-model/per-group defaults via `models.default_params`, but client choice always wins — no enforcement knob exists; real per-user RBAC remains a PR-upstream item (01-F8).
