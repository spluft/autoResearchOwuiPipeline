# Evidence Ledger — <short topic>

> One row per important claim. A claim without a row must not appear in the final
> report. Keep epistemic status explicit — never promote a source's opinion into an
> established fact.

## Claim table

| ID | Claim | Evidence (what the source ACTUALLY establishes) | Source URL | Source type¹ | Pub date | Last updated | Verified on | Confidence² | Limitations | Independent confirmation |
|----|-------|------------------------------------------------|------------|--------------|----------|--------------|-----------|-------------|-------------|--------------------------|
| C1 | <factual statement> | <quote/paraphrase grounded in fetched page> | <exact URL fetched> | primary / secondary / community | <date or "unknown"> | <date or "n/a"> | <access date> | high / med / low | <missing context> | <C7, or "none — single source"> |
| C2 | … | | | | | | | | | |

¹ `primary` = official docs/spec/paper/repo/source-code/original statement by the actor;
`secondary` = established specialist publication, expert analysis; `community` = forums,
user reports. For software claims, the project's own repository/issue tracker is primary.

² Confidence = trust in the evidence itself (authority × directness × recency), not in
how much the claim is liked. Single-source critical claims cap at **medium**.

## Epistemic status tags (use in the report alongside each claim)

- **FACT** — established by primary evidence or ≥2 independent sources.
- **CLAIM(source)** — asserted by a source; attribution kept visible.
- **INTERPRETATION** — the analyst's reading of the evidence.
- **HYPOTHESIS** — plausible, not yet supported enough.
- **ASSUMPTION** — adopted provisionally; flagged as unverified.
- **RECOMMENDATION** — advice, not a factual finding.

## Inaccessible / rejected sources log

| URL | Attempted | Result | Consequence |
|-----|-----------|--------|-------------|
| <url> | <round> | paywalled / 403 / truncated / JS-required | claim downgraded / replaced with <alt source> |

## Contradiction register

| Topic | Position 1 (source, date) | Position 2 (source, date) | Difference explained by? | Better supported because |
|-------|---------------------------|---------------------------|--------------------------|--------------------------|
| <topic> | <…> | <…> | version / methodology / scope / unresolved | <reasoning> |

## Coverage check (run before Phase 10)

- Every research area from the plan maps to ≥1 row (or a documented gap).
- Every critical conclusion cites rows, not search snippets.
- Every HIGH-confidence claim is primary-sourced or independently corroborated.
