---
title: OWUI Auto mode — доки, issues, community
date: 2026-11-09
tags: [owui, security, research]
related: [[deep-owui-automode-2026-11/report]] [[open-webui]]
source: docs.openwebui.com, GitHub API, Arctic Shift (Reddit)
---

# 02 — Community & issues intelligence: OWUI Auto tool-permission mode
Date: 2026-11-09 | Researcher leaf | Sources: docs.openwebui.com (fetched 2026-11-09), GitHub issues API, Reddit via Arctic Shift, HN Algolia. All quotes verbatim from fetched data.

---

## F1. Official docs: what Auto is, and the full config surface
**Rationale:** Baseline of what users/admins are told; proposal must not contradict it.
**Evidence:** docs tools page, verbatim: "Auto | Each tool call is checked against an approval policy. A call that needs approval waits for **Allow** or **Deny** like under **Ask for approval**; the others run immediately. Users who have not chosen a mode get **Auto**." And: "By default a model runs its tool calls as soon as it makes them. An administrator can offer more modes by turning on Tool Permissions in Settings > Admin > Interface ( ENABLE_TOOL_PERMISSIONS ). The feature is experimental and off by default." Config table verbatim: "Engine ( TOOL_PERMISSIONS_AUTO_ENGINE ) Default | Approval policy ( TOOL_PERMISSIONS_AUTO_PROMPT ) Empty (built-in policy) | API Base URL ( TOOL_PERMISSIONS_AUTO_DECISIONS_API_BASE_URL ) https://api.openai.com/v1 | API Key ( TOOL_PERMISSIONS_AUTO_DECISIONS_API_KEY ) Empty | Model ( TOOL_PERMISSIONS_AUTO_DECISIONS_MODEL ) gpt-6-luna | Approval threshold ( TOOL_PERMISSIONS_AUTO_DECISIONS_THRESHOLD ) 0.5" + "Both engines use the Approval policy . The last four settings apply to the Decisions API engine only."
**Summary:** Auto = per-call policy check; default mode for users who never chose; 6 admin fields; feature-flagged `ENABLE_TOOL_PERMISSIONS` + `ENABLE_TOOL_PERMISSIONS_AUTO`, off by default, "experimental".
**URL/date/type:** https://docs.openwebui.com/features/extensibility/plugin/tools/ #tool-approval / #auto | fetched 2026-11-09 | official docs.
**Confidence:** high.
**Follow-ups:** confirm exact settings-UI labels against v0.13.3 code (SC2, parent's code leaf).

## F2. Docs: Default engine = chat model judges itself (injection vector documented)
**Rationale:** Directly answers parent's prompt-injection concern — the docs state it outright.
**Evidence:** verbatim: "With the Default engine, the chat model decides. Open WebUI adds the approval policy to the system prompt and a required `__approval__` argument to each tool, and removes that argument before the tool runs. A call runs without approval only when the model sends exactly `{"required": false}` in that argument; anything else, including leaving it out, asks for approval. Tools whose parameters are not a plain JSON object or that define their own `__approval__` parameter get no `__approval__` argument, so their calls always ask for approval. In Legacy Mode no tool gets the argument, so every call asks for approval. ... The chat model judges its own calls, so content that steers the model, such as instructions in a tool result, can also steer its decision."
**Summary:** Default engine has NO independent reviewer — self-approval, and the docs explicitly warn tool-result content can steer the decision. Fail-closed on missing/invalid `__approval__`. Only Decisions API engine gives a separate review model.
**URL/date/type:** same docs URL, #auto section | fetched 2026-11-09 | official docs.
**Confidence:** high.
**Follow-ups:** for our family instance, Default engine is the unsafe mode; verify Decisions-API-only deployment posture in code leaf.

## F3. Docs: Decisions API mechanics + fail-closed rules
**Rationale:** Defines the scoring contract we'd self-host; latency/fallback behavior matters for our local-GPU review model.
**Evidence:** verbatim: "Open WebUI sends a POST request to <API Base URL>/decisions for each tool call with the Model , the approval policy, your latest request and your last four messages, the tool's definition and name, the call's arguments and the tool type and Open Terminal ID. The service answers with the probability that the call needs approval. The call asks for approval when that probability is at or above the Approval threshold . The call also asks for approval when the review does not answer within 5 seconds, fails or returns an invalid answer, when the Approval threshold is not a number from 0 to 1 and when the request data apart from the model and approval policy would exceed 64 KB. The review service must implement the same /decisions endpoint as the Tool Search Decisions API engine."
**Summary:** Per-call POST /decisions, probability vs threshold 0.5; fail-closed on 5 s timeout/error/invalid/>64 KB; payload = policy + last request + last 4 messages + tool def + args + tool type + Open Terminal ID. No mention of caching/dedup of identical calls → every tool round pays a scoring call.
**URL/date/type:** same | fetched 2026-11-09 | official docs.
**Confidence:** high.
**Follow-ups:** grep code for any caching layer; check `/decisions` endpoint spec shared with Tool Search.

## F4. Docs: scope boundaries — where Auto does NOT apply
**Rationale:** Answers parent's open question "does Auto cover terminal / coding agents / channels".
**Evidence:** verbatim: "Channel replies always run with full access, and Auto cannot be selected in channel chats. Automations have no chosen mode, so they run in Auto when it is offered and with full access otherwise. Questions from the ask user tool never need approval." And: "The search_tools call of Tool Search runs without a review. If you turn Auto permissions off, chats that used Auto switch to Ask for approval." And temp chats: "It is also denied when the browser tab is gone or nobody answers within 120 seconds, or within WEBSOCKET_EVENT_CALLER_TIMEOUT when that is set lower."
**Summary:** Auto applies to chat tool calls incl. Open Terminal calls (payload carries "Open Terminal ID"); EXEMPT: channel replies (full access!), automations-without-Auto, ask_user, search_tools. Temp-chat approvals auto-DENY after 120 s or tab close. Turning Auto off silently downgrades chats to Ask, not Full.
**URL/date/type:** same | fetched 2026-11-09 | official docs.
**Confidence:** high.
**Follow-ups:** coding-agent sessions (Claude Code via Open Terminal) — verify in code whether their internal tool calls are OWUI tool calls subject to review.

## F5. Reddit: users don't understand Auto / can't find the decision-model option
**Rationale:** Direct "people don't understand the feature" evidence (SC3), incl. the anchor's known comment.
**Evidence:** r/OpenWebUI thread 1xqw605 ("Open WebUI 0.13.1: CODING AGENTS like Claude Code...", 2026-11-08, score 99, 26 comments), u/AccomplishedOne9144 (score 3): "Great stuff as always! The auto mode sounds great. But I did not understand it fully. Can the decision be made by a decision model like jev or Decider 2B?" — and the same user's later self-answer: "Checked the docs and also online that Luna 6 can be a decision model. Was not aware of that!" Related discoverability complaint, u/NakedxCrusader: "you publish so much different tools that I seriously can't follow properly and I use OWUI professionally."
**Summary:** Even motivated users couldn't find that Auto supports a dedicated decision model; docs answered it but not discoverably. Feature-request-shaped demand for small local decider models (jev/Decider 2B class) — matches our local-GPU review setup.
**URL/date/type:** https://reddit.com/r/OpenWebUI/comments/1xqw605/ | 2026-11-08 | Reddit via Arctic Shift.
**Confidence:** high (verbatim from Arctic Shift).
**Follow-ups:** none blocking.

## F6. Core dev himself runs with approvals off: over-blocking complaint
**Rationale:** Strongest practitioner signal: the blocking behavior, not the review model, is the pain; voiced by core team.
**Evidence:** u/ClassicMain (core team) in r/OpenWebUI t3_1wo05i7 (~2026-09-23, via Arctic Shift): "I never had security issues because I don't give the AI tasks that would have it do something I don't want it to do and generally i always monitor them during execution as well. Plus there's an tool auto approve mode which would block commands if you wanna use that. Personally i go for no tool approvals because for me it blocks a few too many commands. Needs some improvement, i put a feature request for it to the repository already"
**Summary:** Core dev: over-blocks "a few too many commands", so he uses Full access + human monitoring instead; acknowledged "needs some improvement" + filed his own feature request (number not captured [no-quote]). Also note his security posture is human monitoring, not the reviewer.
**URL/date/type:** https://reddit.com/r/OpenWebUI/comments/1wo05i7/ | ~2026-09-23 | Reddit via Arctic Shift.
**Confidence:** high on quote; medium on which FR he meant (likely #28279).
**Follow-ups:** identify his feature request number via GitHub.

## F7. Risk-perception soundbites around Auto launch
**Rationale:** Community trust framing for the proposal's motivation.
**Evidence:** 1xqw605, u/Layney_Butcher: "Auto tool permissions is either going to save me hours or delete something I need, probably both." Related terminal risk anecdote in same thread, u/Numael80: "also deleted the home folder in the open-terminal docker container."
**Summary:** Sentiment = excitement + fear of false-approve; concrete adjacent incident (agent deleted home folder in Open Terminal container) with no reviewer catching it. No reports found of the review model itself false-approving [no-quote — absence, not survey].
**URL/date/type:** https://reddit.com/r/OpenWebUI/comments/1xqw605/ | 2026-11-08 | Reddit via Arctic Shift.
**Confidence:** high on quotes; low on prevalence of false-approvals (no data).
**Follow-ups:** monitor issues for "auto mode approved" reports post-0.13.1 adoption.

## F8. GitHub: the approval state-machine bug cluster (why trust in Auto is thin)
**Rationale:** Auto shares the approval plumbing with Ask; these recent bugs (many closed within days) show the layer was brittle — false-Deny stalls, silent bypasses, context loss after approval.
**Evidence:** issue titles verbatim: #29249 [closed 2026-10-10] "Ask for approval tool permission is silently ignored in temporary chats" — reporter: "I hit this with `search_chats`, which read my saved chats and returned results without ever asking me."; #33873 [closed 2026-11-08] "A tool call in a side chat waits for approval forever, with no Allow or Deny to press"; #29293 [closed] "Ask-for-approval: repeated same-name tool calls in one approval batch stay \"Executing…\" forever, and the stuck state is persisted"; #33403 [closed] "Allow and Deny on a tool call waiting for approval can't be pressed with the keyboard"; fix PRs #31315 "approve every tool call from a multi-call turn in ask mode", #31502 "approved tool results are lost and approved tools can run twice", #31501 "system prompt and compacted context are lost after approving a tool call", #32028/#32030 attached file/image lost after approval, #31986 "uploaded file source context is lost after tool approval".
**Summary:** Two-sided failure modes all documented: silent bypass (#29249 = security-shaped: reads ran with no prompt) and stuck/lost approvals (#33873, #29293, #31315); approval path dropped context (system prompt, attachments, sources). Mostly fixed in ~v0.13.x but shows the review→run handoff is fragile.
**URL/date/type:** github.com/open-webui/open-webui/issues/{29249,33873,29293,33403,31315,31502,31501,32028,32030,31986} | 2026-08…2026-11 | GitHub issues.
**Confidence:** high (API titles/bodies).
**Follow-ups:** retest side-chat + temp-chat approvals on our v0.13.3.

## F9. GitHub: feature requests & gaps — custom policy, visibility, audit logging
**Rationale:** Maps onto parent's feature-request checklist (custom prompts, logging, per-user, allowlists).
**Evidence:** #28279 [closed 2026-08-11] concept: "Add a point where a filter can see the tool calls a model asked for, before any of them run, and deny them. Core ships the hook, deployments ship the policy." (custom dialogs, per-tool policy, "approve all for this chat", second approver — via Filter Functions; body also notes web-search has "its own confirmation toggle ... and it covers web search only"). #33735 [OPEN, 2026-11-04]: "When the model calls ask_user, the card uses the same quiet styling ... easy to scroll past it or assume the assistant is still working while the chat sits waiting" — wants tab-title prefix "(1) Answer needed", auto-scroll, primary Submit. #33238 [closed]: "Audit log usage misses most model calls" — audit coverage gap (relevant: review-model calls plausibly unaudited too [no-quote]).
**Summary:** Community wants policy-as-code hooks (filter-level), session-scoped remembers, escalation; approval visibility for non-technical users is an open ask; audit log is incomplete so Auto decisions likely leave little forensic trail. No per-user Auto mode found requested/found [no-quote]; mode is saved "to your user settings" per docs (per-user choice exists, per-user thresholds do not).
**URL/date/type:** github.com/open-webui/open-webui/issues/{28279,33735,33238} | 2026-08-07 / 2026-11-04 / 2026-10-27 | GitHub issues.
**Confidence:** high on quotes; medium on audit-gap implication.
**Follow-ups:** check code for where review decisions are logged; check if #28279 was implemented or closed-wontfix.

## F10. Hacker News: no relevant coverage
**Evidence:** [LACK_OF_DATA: HN Algolia queries "open webui auto mode" (tags=comment/story), "open webui tool permission", "open webui 0.13"] — all returned 0-16 hits, zero on-topic (verified by reading all hits' snippets).
**Summary:** The Auto-mode discussion lives on r/OpenWebUI + GitHub, not HN. Community intel = Reddit+GitHub (this file) + code.
**URL/date/type:** hn.algolia.com/api/v1/search | 2026-11-09 | HN API.
**Confidence:** high (small result sets fully inspected).
**Follow-ups:** none.

## F11. PullPush & Arctic Shift keyword search — partial lack of data
**Evidence:** [LACK_OF_DATA: PullPush comment search link_id=1xqw605 → HTTP 526; Arctic Shift body searches "auto mode"/"review model"/"auto mode tool" → 422 "Timeout. Maybe slow down a bit"]
**Summary:** Broad keyword sweeps over r/OpenWebUI comments failed (rate limits); targeted link_id fetches succeeded, so anchor-thread and security-comment evidence is complete but no exhaustive corpus scan was possible. Absence of more false-approval complaints below is NOT strong evidence of absence.
**Confidence:** n/a (method limitation).
**Follow-ups:** if parent wants breadth: retry Arctic Shift body search later with `after/before` windows and 1 query/30 s.

---

Bottom line for parent: Auto mode = admin-gated, per-call policy check with two engines (Default = chat model self-approves, docs-warned injection vector; Decisions API = external /decisions scorer, threshold 0.5, fail-closed at 5 s), exempting channels/automations/ask_user/search_tools; community pain is (a) confusion even for power users, (b) over-blocking so bad that a core dev uses no-approvals himself, (c) a brittle approval state machine (silent bypass #29249, stuck approvals #33873/#29293, context loss #31501/#31986), (d) thin audit trail (#33238) and poor pending-approval visibility (#33735, open) — while demand exists for small dedicated decider models (#5, our exact setup) and policy-as-code hooks (#28279).
