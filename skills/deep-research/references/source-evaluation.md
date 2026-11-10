# Source Evaluation — hierarchy and criteria

## Contextual hierarchy (not absolute)

Prefer, adapting to the subject:

1. **Official documentation and original technical specifications** — product docs,
   RFCs/ISO/standards texts, API references.
2. **Primary research** — original papers, datasets, experiments, official statistics.
3. **Official repositories** — source code, commit history, issue trackers, release
   notes, security advisories.
4. **Governmental and recognized institutional publications** — regulator, agency,
   standards-body statements.
5. **Original statements by relevant actors** — the company's/researcher's own
   published position (with self-interest discount applied).
6. **Established specialist publications & independent expert analysis** — reputable
   technical press, recognized practitioners.
7. **Community discussions, forums, user experience** — Stack Overflow, Reddit,
   issue comments, HN.

The hierarchy is contextual: community discussions are the BEST source for "does this
break in practice / undocumented gotchas", and issue trackers are primary for
"is there a known bug". What never changes: anecdote must not be presented as an
established technical or scientific fact; vendor marketing is not neutral even when
positioned as documentation; third-party tutorials rank below the docs they paraphrase.

## Evaluation criteria (apply per candidate source)

- **Relevance** — does it address YOUR question and the exact version/timeframe, or
  merely share keywords?
- **Authority** — who published it, with what standing, and would they be embarrassed
  if it were wrong?
- **Recency** — is it current enough for the claim type? Version-sensitive claims
  age fast; math and history do not.
- **Originality** — origin or echo? Trace citation chains back; five posts citing one
  press release are one source.
- **Independence** — would this source's conclusion have been the same if the other
  side were true? Corroboration only counts across independent evidence chains.
- **Availability of primary evidence** — does it show its work (links to the spec, the
  dataset, the code), or just assert?
- **Bias & conflict of interest** — vendor, affiliate, political, or reputation
  stakes; note them in the ledger.

## Decision rules

- A critical conclusion needs: one primary source, or ≥2 independent secondary
  sources. Between those, cap confidence at medium and say so.
- Community signal without primary support → report as "reported by users", never as
  FACT.
- Primary source exists but is unreadable (paywall/JS/403) → search for an authorized
  mirror, preprint, or official secondary (press kit, standards summary); failing
  that, disclose "primary source inaccessible" and downgrade dependent claims.
- An old primary that has been superseded → cite the current one; cite the old one
  only for the historical claim.
- For software claims, the project's own repository/issue tracker/docs beat any
  blog — and the claim must match the artifact for the exact version under
  investigation.

## Quick scoring for the ledger

Not numeric theater — three honest labels drive the report:

- **high** — primary, current, directly on point (or two independent secondaries of
  good standing).
- **medium** — secondary but credible; or primary with caveats (undated, stale,
  partially paywalled, single-source).
- **low** — community/anecdotal/undated/conflicted — usable as signal, not as proof.
