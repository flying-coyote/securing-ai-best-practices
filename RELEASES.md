# Releases

Each release is a frozen, tagged commit. The one-line review pins the commit SHA, so this file is where a practitioner checks that the SHA in the block they were handed is a real release and that the offline bundle they downloaded is the one published with it.

The release mechanic, because a commit cannot contain its own SHA: freeze and tag commit C as `vYYYY.MM` (monthly at most), with the release script stamping the tag and date into the header of `AUDIT-CONTEXT.md` before tagging; build the offline bundle from C; record C's full SHA and the bundle's SHA-256 here and in the GitHub release notes; then update the blocks in `README.md` and `ONE-LINE-PROMPT.md` on the default branch to name C's SHA. An old block therefore keeps working and announces its own age in every review it produces.

## Release log

The first release, v2026.11, is the small-organization slice (v0.1 in the build plan).

| Tag | Date | Commit SHA | Bundle SHA-256 | Pins | Agents tested | Notes |
|---|---|---|---|---|---|---|
| v2026.11 | 2026-11-10 | `a44a7cd17999cc791efa82e22a261843632444b7` | `1bdd3de35528b49c69ae63bcb65394c091865de4b9d77fcbfa4846d281b475cf` | MITRE ATLAS v2026.10; MITRE ATT&CK Enterprise v20.1; MITRE D3FEND 1.6.0; OCSF 1.9.0; MCP specification 2026-07-28; CoSAI secure-ai-tooling 622605a1; NIST CSF 2.0; NIST IR 8596 iprd-2025-12-16; NIST AI RMF 1.0; OWASP Top 10 for LLM Applications 2026; OWASP Top 10 for Agentic Applications 2026; ISO/IEC 42001 2023; CSA AI Controls Matrix v1.1; AIUC-1 2026-10-15; EU AI Act consolidated CELEX-02024R1689-20260727; CISA KEV catalog 2026.11.09 | Claude Opus 5.5 and Gemini 3.8 Flash, offline mode, three fixtures (fetch mode untested) | 34 files; offline bundle attached to the GitHub release |

## What each column holds

- Tag is `vYYYY.MM`.
- Commit SHA is the full 40-character SHA of the tagged commit, which is what the block pins.
- Bundle SHA-256 is the checksum of the offline bundle built from that commit.
- Pins are the framework, schema and catalogue versions the release was checked against, copied from `analysis/revalidation-and-pins.md` at freeze (MITRE ATLAS and ATT&CK releases, the CoSAI registry commit, the OCSF and MCP specification versions, the OWASP list edition, and the CISA KEV catalogue version, among others).
- Agents tested names each agent and version the block was run against on the fixtures, in fetch mode and offline mode.
