# Absorption map

For each routable document, this map names the standard, specification or maintained project that could carry its load instead, which lane the document is in, and what would move it along. The repo's aim is to shrink toward the standards rather than grow beside them, so "none found" is a real and useful answer, and a document whose only contribution is a mapping the standards body has not made yet should retire once that mapping is accepted upstream.

This file is derived. Each document's frontmatter (`status`, `convergence`, `follows`, `replacement-by`) is canonical, and where this map disagrees with a document, the map is corrected to match it.

Last verified sweep: none yet (no routable documents exist). The quarterly judgement sweep re-checks every row against its absorber; the weekly review runs only the consistency greps.

## Lanes and the four-bar test

- `none`: no absorber found, so the analysis is this repo's to keep.
- `follow`: an external canon carries the conceptual load for the document's slice; the document keeps its delta and stops growing there (`follows:` in its frontmatter).
- `retire-toward`: an absorber clears all four bars, and the document defers to it (`replacement-by:` and `status: RETIRING`).

The four bars are supported (a maintained project or a standards body with a release process), generally available (not a preview or draft), covers the substance (checked by reading the absorber against the document's claims, never by popularity), and citeable (a stable URL and version).

## Map

| Document | Absorber (pinned) | Lane | Bars (Supported / GA / Substance / Citeable) | Delta kept | Advance trigger | Verified |
|---|---|---|---|---|---|---|

Rows are added with each document. The candidate absorbers already named in the design are the CoSAI controls and component registry, the OWASP lists, the MCP specification's security guidance, the OCSF schema and its proposed AI event class, NIST AI RMF and ISO/IEC 42001 for governance structure, and the vendors' own governance documentation for the stub families.
