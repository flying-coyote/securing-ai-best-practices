# Releases

Each release is a frozen, tagged commit. The one-line review pins the commit SHA, so this file is where a practitioner checks that the SHA in the block they were handed is a real release and that the offline bundle they downloaded is the one published with it.

The release mechanic, because a commit cannot contain its own SHA: freeze and tag commit C as `vYYYY.MM` (monthly at most), with the release script stamping the tag and date into the header of `AUDIT-CONTEXT.md` before tagging; build the offline bundle from C; record C's full SHA and the bundle's SHA-256 here and in the GitHub release notes; then update the blocks in `README.md` and `ONE-LINE-PROMPT.md` on the default branch to name C's SHA. An old block therefore keeps working and announces its own age in every review it produces.

## Release log

No release has been cut. The first, v0.1, is the small-organization slice.

| Tag | Date | Commit SHA | Bundle SHA-256 | Pins | Agents tested | Notes |
|---|---|---|---|---|---|---|

## What each column holds

- Tag is `vYYYY.MM`.
- Commit SHA is the full 40-character SHA of the tagged commit, which is what the block pins.
- Bundle SHA-256 is the checksum of the offline bundle built from that commit.
- Pins are the framework, schema and catalogue versions the release was checked against, copied from `analysis/revalidation-and-pins.md` at freeze (MITRE ATLAS and ATT&CK releases, the CoSAI registry commit, the OCSF and MCP specification versions, the OWASP list edition, and the CISA KEV catalogue version, among others).
- Agents tested names each agent and version the block was run against on the fixtures, in fetch mode and offline mode.
