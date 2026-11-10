# Research Plan — <short topic>

> Produced in Phase 1–3, before any search is treated as evidence. Keep this plan
> visible in the working context; update statuses as areas complete.

## 1. Question under investigation

- **Original request (verbatim):** <copy the user's exact words>
- **Research question (restated):** <what must actually be established>
- **Interpretation notes:** <ambiguities resolved, interpretations rejected and why>
- **What must NOT be assumed:** <e.g. "that feature X exists in version Y">

## 2. Scope

| Dimension | Decision |
|---|---|
| Temporal scope | <e.g. "state as of <month year>", "versions ≥ 2.0"> |
| Geographic / organizational scope | <if relevant, else "n/a"> |
| Domain | <technical / scientific / market / historical / mixed> |
| Required evidence level | <snippet-level OK / primary source required / reproducible claim> |
| Explicit exclusions | <what the user does not want> |

## 3. Entities and terminology

- **Key entities:** <products, projects, people, orgs, standards>
- **Key terms & synonyms/acronyms to use in queries:** <term (synonym, acronym, translation)>
- **Version/edition identifiers that matter:** <exact version strings, if any>

## 4. Research areas

For each area: objective, key questions, likely primary sources, required evidence,
expected output. Do not create areas that do not serve the main question.

### Area A — <name>
- Objective: <one sentence>
- Key questions: <1..n bullets>
- Likely primary sources: <official docs, spec, repo, paper, dataset>
- Required evidence: <what closes this area>
- Status: `todo` / `searched` / `fetched` / `evidence-OK` / `gap:<reason>`

### Area B — <name>
- …

## 5. Dependency map (complex topics only)

- <Area B key question 2 depends on Area A answer (which version?)>
- <Which questions must be answered before others>

## 6. Search strategy (per area, distinct purposes)

Every query states its purpose; never re-issue the same query with rewording only.

| # | Area | Query | Perspective (concept / exact term / official docs / source code / papers / critique / recency) | Purpose | Status |
|---|---|---|---|---|---|
| 1 | A | <query> | official docs | find authoritative definition | todo |
| 2 | A | <query> | known limitations | falsify optimistic claim | todo |

## 7. Bounded budget

- Search rounds: quick ≤ 1, standard ≤ 3, deep ≤ 5 (hard caps).
- Pages to fetch per round: ≤ 5 (standard), ≤ 10 (deep); fetch only sources that
  passed the relevance/authority filter.
- Stop condition: additional searches are unlikely to materially change the conclusion,
  OR remaining gaps are explicitly documented here.

## 8. Mode and delegation

- Mode chosen: `quick` / `standard` / `deep` + one-line justification.
- Delegation: none / <roles, each with single objective + scope + expected output>
  (only if the capability is actually available in this chat).

## 9. Completion gates (check off or state why impossible)

- [ ] A — Scope: question and boundaries understood
- [ ] B — Coverage: all material areas investigated
- [ ] C — Evidence: key conclusions have authoritative evidence
- [ ] D — Contradictions: competing explanations evaluated
- [ ] E — Verification: claims/dates/versions/citations fact-checked
- [ ] F — Completion: answer supported by evidence, residual uncertainty transparent
