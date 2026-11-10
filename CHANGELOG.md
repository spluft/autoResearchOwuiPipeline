# Changelog

All notable changes to this repository. Format loosely follows Keep a Changelog.

## [Unreleased] — 2026-11-10

### Added — Deep Research Skill (`skills/deep-research/`)
- `SKILL.md` — Open WebUI-native skill (frontmatter limited to documented keys
  `name`/`description`; OWUI standard body sections; ~10.5k chars, within the
  documented 20,000-char read limit). Adaptive modes quick/standard/deep with hard
  tool budgets; 10-phase research procedure; evidence-ledger discipline; completion
  gates A–F; honest tool-availability degradation.
- `references/research-methodology.md` — full phase specification including query
  perspectives and falsification rounds.
- `references/source-evaluation.md` — contextual source hierarchy, evaluation
  criteria, decision rules, confidence labels.
- `references/fact-checking.md` — Phase-9 independent verification checklist
  (universal + software-version-specific + scientific evidence ladder).
- `references/citation-policy.md` — Open WebUI citation mechanics (v0.13.3: only
  `fetch_url`-read pages become citations; snippets not citable) + integrity rules
  + anti-patterns.
- `references/openwebui-integration.md` — verified capability matrix, exact built-in
  tool names/signatures (`search_web`, `fetch_url`, KB tools, `delegate_task`),
  provider & loader notes, admin minimum-configuration checklist. Grounded in
  official docs, verified 2026-11-10 against v0.13.3.
- `references/research-completion-criteria.md` — gates A–F detail, mode-specific
  expectations, budget-exhaustion rule.
- `templates/research-plan.md`, `templates/evidence-ledger.md`,
  `templates/final-report.md` — reusable working artifacts.
- `examples/technical-research.md`, `examples/comparative-research.md`,
  `examples/current-information-research.md` — illustrative walkthroughs
  (explicitly marked as teaching material, not run results).
- `tools/validate_skill.py` — structural validator (frontmatter spec, section
  completeness, bundled-file reachability, size limits). Executed: passes.
- `evaluation/scenarios.md` — 10-scenario evaluation suite with 12-criterion,
  24-point rubric and an execution status log (EXECUTED / SIMULATED / REQUIRES-OWUI).

### Documentation
- `README.md` rewritten sections: project now spans two independent capabilities —
  Auto Tool Permissions (shim + docs/) and the Deep Research Skill — with an
  explicit four-way distinction (Auto Tool Permissions vs Deep Research Skill vs
  Open WebUI native web search vs optional sub-agents), import instructions, and a
  capability checklist.
- `docs/04-skill-separation.md` — design decision record: why the skill and the
  permission shim stay architecturally independent.

### Preserved (audit)
- `shim/` (app.py, test_app.py, Dockerfile, deployment.yaml, requirements.txt,
  runserver.py) and `docs/00–03, plan, report` untouched — zero diff. Baseline
  `pytest shim/test_app.py`: 12 passed (re-confirmed 2026-11-10 after skill work).
