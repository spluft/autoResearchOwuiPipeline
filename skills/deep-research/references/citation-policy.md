# Citation Policy — Open WebUI mechanics and integrity rules

Citations are a core functional requirement, not decoration.

## How citations actually work in Open WebUI (Native/Agentic mode, v0.13.3)

- `search_web` returns `{title, link, snippet}` as tool output. Those hits are **not**
  listed in the citation panel and must not be cited — "nothing has opened those
  pages, so there is nothing to cite". (Older versions emitted empty `search_web`
  citation entries; that was removed as a mis-attribution risk. Legacy function-calling
  mode still RAG-cites retrieved web text — prefer Native mode.)
- `fetch_url` opens the page; **only successfully fetched pages appear as citable
  sources in the citation panel**, named by their URL. This is the only way a web page
  becomes a citation in Native mode.
- Consequence, operationally: **fetch first, then cite**. A claim you cannot ground in
  a fetched page is presented as unverified or dropped.
- Knowledge Base chunks from `query_knowledge_files`/`query_chat_files` DO render as
  citations — but attribute them as internal documents, distinct from public evidence.

## Integrity rules

1. Cite the **specific document** that supports the claim — not the site homepage, not
   the docs root, not a search page.
2. Put the citation **next to the claim it supports**; never attach a source to a
   neighboring sentence it does not establish.
3. One source backs only what it actually says; verify the sentence you cite for.
4. Do not cite sources because they contain matching keywords.
5. Never fabricate a citation, source ID, URL, publication date, or quote.
6. Distinguish dates when available: **published** / **last updated** / **date of the
   event described** / **accessed**. For current information, state "verified through
   <date>".
7. If a page could not be fetched fully (paywall, 403, `[Content truncated...]`),
   mark claims from it accordingly; never pretend the full text was inspected.
8. Short quotations only where the exact wording matters (definitions, licenses,
   commitments, direct statements); otherwise paraphrase with attribution. Do not
   reproduce lengthy copyrighted material.
9. Source numbering must match the ledger; every report citation maps to a row.

## Report source-list format

Per source: **Exact title** — author/publisher, published <date or "undated">,
updated <date or "n/a">, accessed <date>, URL, type (primary/secondary/community),
used for: [claim IDs].

## Worked anti-patterns

- ❌ "Studies show X is faster [1]" where [1] is the vendor's own marketing page and
  was only seen in a snippet.
  ✅ Fetch the benchmark or paper; cite it; if only vendor numbers exist, write
  "the vendor claims … (unverified by independent benchmark)".
- ❌ Ten bullet points each tagged [1] where [1] establishes only the first.
  ✅ Tag each bullet with the row that actually supports it, or split sources.
- ❌ Citing `https://example.com/docs` for a parameter default documented at
  `https://example.com/docs/config#param`.
  ✅ Cite the deep document you read.
- ❌ "According to Wikipedia (accessed today)" for a historical event.
  ✅ Follow the reference to the primary history source; keep dates of event vs
  publication distinct.
