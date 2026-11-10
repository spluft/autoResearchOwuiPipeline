# Fact-Checking — the independent verification pass

Run as Phase 9, before synthesis. This is an evaluation of the research, not a
rehearing of its conclusions: assume the interesting error is in the claims you feel
best about.

## Universal checklist

For every important claim (and every claim that made it into the executive summary):

- **Names & entities** — exact official spelling; right entity? (Same-name products,
  renamed projects, forks.)
- **Dates** — publication date vs last-updated vs date of the event; year implied vs
  stated; "recent" translated to a date.
- **Versions** — the claim's version matches the artifact fetched (docs for v2 do not
  certify behavior in v3).
- **Technical parameters & numbers** — units, limits, defaults; number came from the
  fetched page, not memory; re-read the sentence it sits in (adjacent numbers get
  spliced).
- **URLs** — the cited URL is the one you fetched and that actually contains the
  support; no 404s; no deep link that redirects to homepage.
- **Quoted statements** — exact words appear in the fetched content; attribution to
  the right speaker/organization; quote not stitched from two contexts.
- **Source attribution** — the source really establishes the claim (open the row,
  open the page, match the sentence).
- **Causal relationships** — correlation reported as causation? who actually claims
  the causal link?
- **Comparative conclusions** — both sides held to the same evidence bar; same
  version/timeframe on both sides of the comparison.

Log: items checked, failures found, corrections or confidence downgrades applied.
Report this pass in the final answer (one short paragraph) — an unreported pass is an
unexecuted pass.

## Software / technology investigations

Critical claims should be verifiable against one of, in order of preference:

1. The exact version's **source code** (file + symbol you can name).
2. The **official documentation or changelog** for that version.
3. **Reproducible behavior** (a command sequence the user can run).
4. The project's **issue tracker** (a maintainer statement is near-primary).

Blogs, tutorials, and AI-generated explainer farms are claims, not verification. If
only such sources exist, the claim ships as CLAIM(source) with medium/low confidence.

Watch: doc describing a newer version than the user's; features behind flags/
enterprise tiers; behavior changed between patch releases; deprecations that make an
answer true-but-misleading.

## Scientific / evidence-based questions

Rank explicitly and label each study accordingly:

1. Systematic reviews / meta-analyses
2. Randomized controlled trials (sample size, pre-registered?, replication?)
3. Cohort / observational studies (confounders?)
4. Case reports, expert consensus, mechanism-based reasoning

State which tier supports the conclusion; note where the popular narrative outruns
the evidence tier. Distinguish "no evidence of effect" from "evidence of no effect".
Funding/conflict notes where material.

## Failure handling

- Check fails → fix the claim, downgrade it (FACT→CLAIM→HYPOTHESIS), or remove it.
- A failing critical claim with no reachable corroboration → it becomes an unresolved
  question in the report, with what would close it.
- Never "fix" a failing number by loosening the wording until the check passes.
