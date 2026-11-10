---
evidence-tier: Mixed
convergence: single-source
applies-to-signals: [audit-always-fetch, owasp-ids-2025]
surfaces: [S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12, S13]
pins:
  - "MITRE ATLAS v2026.10"
  - "MITRE ATT&CK Enterprise v20.1"
  - "MITRE D3FEND 1.6.0"
  - "OCSF 1.9.0"
  - "MCP specification 2026-07-28"
  - "CoSAI secure-ai-tooling 622605a1"
  - "NIST CSF 2.0"
  - "NIST IR 8596 iprd-2025-12-16"
  - "NIST AI RMF 1.0"
  - "OWASP Top 10 for LLM Applications 2026"
  - "OWASP Top 10 for Agentic Applications 2026"
  - "ISO/IEC 42001 2023"
  - "CSA AI Controls Matrix v1.1"
  - "AIUC-1 2026-10-15"
  - "EU AI Act consolidated CELEX-02024R1689-20260727"
  - "CISA KEV catalog 2026.11.09"
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-02-10
status: EMERGING
measurement-claims:
  - claim: "Between MITRE ATLAS v2026.06 and v2026.10 the technique count went from 173 to 221, with 56 added, 8 removed, 12 renamed and 68 of the 165 surviving IDs given changed definition text; the 8 removed IDs left the STIX bundle with no revoked flag, no deprecated flag and no revoked-by relationship"
    source: "atlas-d3fend-crosswalk@66b7726 VERSION-DIFF-2026-11.md §1 (re-derivable with scripts/01_diff_atlas_releases.py over the stix-atlas.json release assets)"
    date: 2026-11-02
    revalidate: never
  - claim: "Moving the MCP Python SDK from 1.30.0 to 2.3.0 on the same protocol revision added OTel spans (0 to 11 client and 12 server), moved a raising tool's failure cause from the client's text to server stderr and dropped the per-request stderr line (10 to 0), while moving from revision 2025-11-25 to 2026-07-28 on the same SDK removed the initialize handshake and the Mcp-Session-Id header and added the Mcp-Method header (11 of 11 POSTs) and per-request _meta; one fixture server, single host under contention, pre-registration frozen by agent and not reviewed by the maintainer, VERIFIED-WITH-FIXES"
    source: "sdw-lab-benchmarks@91e44df t8a-mcp-before-after/RESULTS.md:44-46, :51-62"
    date: 2026-11-10
    revalidate: 2027-04-10
  - claim: "CISA KEV catalogVersion 2026.11.09 (1,773 entries) lists, among entries added during 2026, three BerriAI LiteLLM entries (2026-05-08, 2026-06-08, 2026-09-02), one MLflow entry (2026-08-19), one Ray entry (2026-08-17), five Langflow entries (a sixth dates from 2025-05-05) and one n8n entry, and no entry for vLLM or Ollama"
    source: "CISA KEV kev.json catalogVersion 2026.11.09, released 2026-11-09T19:54Z"
    date: 2026-11-09
    revalidate: 2027-01-10
---

# Revalidation and pins: what reopens a decision

Evidence tier: Mixed. The release records, STIX diffs, statute dates and catalogue entries are Tier A because they are the standards bodies' and regulators' own data; the SDK comparison and the release diff are Tier B first-party derivations; the ISO/IEC 42001 adoption note is Tier C because it rests on a national body's catalogue page; the revalidation offsets and the monthly reading cadence are Tier D, the maintainer's judgement.

## Summary for the review

A review is only as current as the framework versions it was checked against, and the AI frameworks this repo leans on are moving faster than many security teams re-read them, so every review prints the release it ran from, the pins below and this document's last-verified date, and every recommendation names what would reopen it. Release: v2026.11; pins last verified 2026-11-10. If the review date is past 2027-02-10, print that these pins are unverified since then.

- Print the release tag from `RELEASES.md`, the pins list and the last-verified date in the "Staleness and open revalidation triggers" section of every output. Effort S. Tier D.
- Record the framework version on every mapping row, rule tag and coverage record that cites an ATLAS, ATT&CK, OWASP or CoSAI ID, because ATLAS removed eight technique IDs in four releases without tombstones. Effort S. Tier A for the removal, B for the practice.
- Diff each ATLAS release by external ID against the last one you ingested, treat a disappearance as a change in its own right, and resolve old IDs through a local successor table before anything is joined or scored. Effort M. Tier A data, B method.
- Where internal controls cite OWASP LLM Top 10 entries by their 2025 IDs (`owasp-ids-2025`), re-map them against the 2026 edition, published 2026-08-03, before the next control review. Effort S to M. Tier B.
- Record the MCP SDK version and the negotiated protocol revision as two separate inventory fields, since a lab run found they move different telemetry facts. Effort S. Tier B, one host.
- Put the dated triggers on a calendar now (EU AI Act 2026-12-02, 2027-12-02 and 2028-08-02; each contract renewal; each internal build's re-decision date) and read the signal list monthly. Effort S. Tier A for the dates, D for the cadence.
- Do not build or buy a mapping to NIST AI control overlays yet, because none is published: IR 8596 is still an initial preliminary draft and the overlay project has only a concept paper and an outline. Effort S. Tier A.

## Why this matters

When I re-ran an ATLAS-to-D3FEND crosswalk against the October 2026 ATLAS release, eight technique IDs, seven of which had rows in my mapping queue, were simply gone. They had not been marked revoked or deprecated, and nothing in the STIX bundle pointed from the old ID to wherever its content had moved, so the only reason I noticed is that the rebaseline script diffs every release against the previous one by external ID and printed eight lines with nothing on the right-hand side (Tier B, atlas-d3fend-crosswalk `VERSION-DIFF-2026-11.md` §1, over Tier A MITRE data). A consumer that trusted the flags, which is how ATT&CK tooling usually works, would have carried eight live-looking techniques with June definitions into its next build and never known.

That is the general problem this document exists to manage. A recommendation in this repo rests on some combination of a framework release, a schema version, a protocol revision, a catalogue snapshot and a vendor default, and each of those moves on its own schedule, some monthly, some never, and some without announcing what moved. The repo answers it in three ways: a pin list that `scripts/check-pins.py` compares every other document against, a staggered `revalidate-by` on every document (three months for anything that depends on ATLAS, up to eight otherwise), and the trigger tables below, which name the event and the documents and decisions it reopens so a practitioner can tell a stale recommendation from a dated one.

## The pin table

Checked 2026-11-09 and 2026-11-10 against each project's own release surface. "Reopens" names the repo documents whose claims a new version would put back in question.

| Framework or catalogue | Pinned | Released | What a new version reopens | Watched where | last-checked |
|---|---|---|---|---|---|
| MITRE ATLAS | v2026.10, data format 6.1.0, YAML sha256 prefix `ac41ee9f` | 2026-10-28 | `frameworks-and-what-they-reach.md`; every ATLAS ID in a routing row's reason | atlas-data releases | 2026-11-09 |
| MITRE ATT&CK Enterprise | v20.1 (collection modified 2026-11-05, attack-stix-data commit `f59b03e`) | v20.0 on 2026-10-13 | overlap claims in `frameworks-and-what-they-reach.md`; the injection and exfiltration rows of `agent-identity-and-delegation.md` | attack-stix-data | 2026-11-09 |
| MITRE D3FEND | 1.6.0 (tag `91629ab`) | 2026-08-31 | defence mappings in `frameworks-and-what-they-reach.md` | d3fend-ontology releases | 2026-11-09 |
| OCSF | 1.9.0 | 2026-08-03 | `landing-ai-events-in-ocsf.md`; the landing section of `coding-agent-hooks-and-policy.md`; `tamper-evident-record.md` | ocsf-schema releases and #1754 | 2026-11-09 |
| MCP specification | revision 2026-07-28 | 2026-07-28 | `mcp-servers-and-manifest-drift.md`; `landing-ai-events-in-ocsf.md` | specification changelog | 2026-11-09 |
| CoSAI secure-ai-tooling risk map | `main` at `622605a1`, 42 components | 2026-10-21 | `surface-ownability.md`; every CoSAI component ID in the repo | the repository's `main` | 2026-11-09 |
| NIST CSF | 2.0 | February 2024 | the CSF column in `frameworks-and-what-they-reach.md` | CSRC | 2026-11-09 |
| NIST IR 8596 Cyber AI Profile | initial preliminary draft | 2025-12-16, comments closed 2026-01-30 | any CSF-to-AI bridge; redo when the next draft lands | CSRC | 2026-11-09 |
| NIST SP 800-53 AI overlays (COSIS) | none published | concept paper 2025-08-14, outline 2026-01-08 | nothing yet; the repo writes no overlay explainer before CSRC publishes a draft | CSRC project page | 2026-11-09 |
| NIST AI RMF | 1.0 | January 2023; nist.gov says it "is being revised", no draft | the NIST section of `frameworks-and-what-they-reach.md` | nist.gov | 2026-11-09 |
| OWASP Top 10 for LLM Applications | 2026 edition | 2026-08-03 | `frameworks-and-what-they-reach.md` §OWASP; the `owasp-ids-2025` row | OWASP GenAI project | 2026-11-09 |
| OWASP Top 10 for Agentic Applications | "for 2026" edition | 2025-12-09 | same | same | 2026-11-09 |
| ISO/IEC 42001 | 42001:2023 (EN ISO/IEC 42001:2026 is the CEN adoption, text reported unchanged) | 2023 | management-system references only | iso.org (returned 403; adoption read from a national body's catalogue) | 2026-11-09 |
| CSA AI Controls Matrix | v1.1, 247 control objectives in 18 domains | 2026-06-22 | link-out only, because its licence allows internal reference and no derivatives | CSA artifacts page | 2026-11-09 |
| AIUC-1 | 2026-10-15 quarterly release | 2026-10-15 | link-out only (all rights reserved) | AIUC-1 changelog | 2026-11-09 |
| EU AI Act | consolidated text CELEX 02024R1689-20260727, as amended by Regulation (EU) 2026/1744 | in force 2026-07-27 | `prompt-capture-and-the-law.md` | EUR-Lex | 2026-11-09 |
| CISA KEV | catalogVersion 2026.11.09, 1,773 entries | 2026-11-09 | dated footnotes in `models-you-hold.md` and `ai-apis-and-the-gateway.md` | CISA feed | 2026-11-09 |

## How each upstream moves, and what that does to a pin

ATLAS ships often and moves techniques without leaving a forwarding address. From v2026.06 to v2026.10 the technique count went from 173 to 221, with 56 techniques added, 8 removed, 12 renamed and 68 of the 165 surviving IDs given changed definition text, and the eight removals left the STIX bundle outright, with no `revoked` flag, no `x_mitre_deprecated` flag and no `revoked-by` relationship (Tier A data, Tier B derivation, `VERSION-DIFF-2026-11.md` §1). Successors exist only in the prose release notes, which I found carried four errors against the data, including a v2026.10 removal of `AML.T0024.002` that the notes omit, so that one successor (`AML.T0005.001`) is my inference and carries Tier D. The practical consequence goes beyond any one team's detection tags, because other frameworks ingest ATLAS too: D3FEND's importer on `develop` deprecates a technique only when one of those flags is present, and was still four ATLAS releases behind at v2026.06 on 2026-11-02, so the next bump would leave the eight IDs as live classes unless someone resolves them by hand (Tier A for the code, Tier B for my reading of what the bump would do). Definition changes are the slower form of the same drift, and they matter wherever a mapping's justification quotes the definition, since a single added hyphen breaks a substring check. I raised the missing tombstones upstream as mitre-atlas/atlas-data#33 on 2026-11-02 and have not checked its state for this document, so a reader should look before relying on either outcome. This is why ATLAS-dependent documents in this repo revalidate at three months.

ATT&CK handles the same situation with tombstones, which is the contrast that shows what ATLAS is missing. When ATT&CK retired T1656 on 2026-04-14 (v19), the object stayed in the bundle marked revoked with a `revoked-by` pointer to T1684.001, and ATLAS itself used that pointer to repoint its own reference by v2026.10 (Tier A data, Tier B derivation, `VERSION-DIFF-2026-11.md` §1). The Enterprise bundle counts 867 attack-pattern objects, but 149 of them are revoked and 12 deprecated, so the active set is 706 (227 techniques and 479 sub-techniques), and a pin or a coverage denominator that quotes 867 is counting tombstones (Tier A). v20 added five AI items of its own (T1698 Indirect Prompt Injection, T1699 Direct Prompt Injection, T1700 AI-Enabled Exfiltration, T1608.007 AI Result Poisoning and T1685.007 Impair Autonomous Defenses), and none of them appears anywhere in the ATLAS v2026.10 YAML, which carries ATT&CK references on 48 techniques (Tier A, re-derived 2026-11-10 by searching the pinned YAML). So `AML.T0051` and its children now have ATT&CK twins that neither framework links, and a team mapping prompt-injection detections to both will split or double-count its coverage depending on which ID an analyst picked.

MCP is the case where one pin is not enough. In a lab run against one fixture server, moving the official Python SDK from 1.30.0 to 2.3.0 while keeping the older 2025-11-25 revision added OpenTelemetry spans (from 0 to 11 client and 12 server spans), moved a raising tool's failure cause from the text the client sees to the server's stderr, and dropped the per-request stderr line (from 10 lines to 0), while moving from 2025-11-25 to 2026-07-28 on the same SDK removed the `initialize` handshake and the `Mcp-Session-Id` header and added the `Mcp-Method` routing header on 11 of 11 POSTs and per-request `_meta` (Tier B, sdw-lab-benchmarks@91e44df `t8a-mcp-before-after/RESULTS.md:44-46, :51-62`; one host under contention, so no latency claim, a pre-registration frozen by the agent and not reviewed by the maintainer, verdict VERIFIED-WITH-FIXES). A team that upgrades the SDK but pins the old revision gets the first set of changes and not the second, which is why the repo asks for both values and why `mcp-spec-pre-2026-07` routes to the MCP documents rather than here.

OCSF, CoSAI and the OWASP lists change less often but in ways that rename what a control points at. OCSF 1.9.0 is pinned; the AI Agent Activity class draft (#1754) is not in a release, and an OCSF release that carries it, or that adds a weights digest to `ai_model`, reopens the landing guidance. CoSAI's component list is the canon every surface row in this repo is keyed to, so a commit past `622605a1` that renames or splits a component reopens `surface-ownability.md` before anything else. OWASP published a 2026 edition of the LLM Top 10 on 2026-08-03, so any control text keyed to an LLM0x:2025 ID needs re-mapping, and I have not read a published crosswalk between the two editions, which is listed as a gap below.

The NIST rows are pins on an absence. IR 8596 has only its December 2025 draft, the AI RMF is "being revised" with no draft, and the SP 800-53 overlay project was renamed on 2026-10-20 from COSAiS to Control Overlays for Super Intelligence Systems (COSIS) with only a concept paper and an annotated outline published (Tier A, CSRC). I would not spend on a mapping to any of them until a public draft exists, and the repo will not write an overlay explainer before then.

KEV is pinned for the record rather than as a standard. The catalogue changes several times a week, so the pin says which snapshot a release read, and it matters for one kind of claim: in the 2026.11.09 snapshot the exploited AI-adjacent entries added during 2026 sit in orchestration and gateway software (three LiteLLM entries, five Langflow, one n8n, one MLflow, one Ray) and none names an inference engine such as vLLM or Ollama (Tier A). Any sentence in this repo that says "no KEV entries for" a product class carries the catalogue version beside it, because a "zero 2026 entries" sentence in my own earlier research was true on its date and false a day later, when MLflow entered the catalogue.

## Triggers that reopen a decision

The dated rows go on a calendar now. The signal rows are what a monthly or quarterly sweep reads by hand from release notes, the KEV feed and the standards repositories; the repo does not watch them by feed.

| Date | Event | Reopens | Applies to | Source |
|---|---|---|---|---|
| 2026-12-02 | AI Act Art. 50 marking grace period ends for generative systems already on the market (Art. 111(4)) | notice wording in `prompt-capture-and-the-law.md`; customer-facing generative features in `saas-embedded-ai-and-vendor-terms.md` | organizations placing generative systems on the EU market | Tier A, EUR-Lex |
| 2027-12-02 | Stand-alone Annex III high-risk obligations apply, including Art. 26 deployer duties | retention and worker notice for high-risk systems in `prompt-capture-and-the-law.md` | EU-exposed organizations with, for example, an HR or credit-decision assistant | Tier A, Regulation (EU) 2026/1744 |
| 2028-08-02 | Annex I obligations apply | same, for Annex I product systems | EU product manufacturers | Tier A, same |
| each contract's renewal | renewal | the export-schema and typed-verdict asks in `reading-vendor-claims.md` and `configure-before-you-buy.md` | every AI purchase | Tier D |
| each internal build's re-decision date, which I would set no later than twelve months after it ships | build sunset | `build-buy-and-the-high-priest.md` | every build, glue included | Tier D |
| rolling, per product | a vendor-held log retention window closes before an export job has been confirmed | `telemetry-by-surface.md`, `what-to-log-and-what-it-costs.md` | every sanctioned product whose record the vendor holds | Tier B, per product, dated in `telemetry-by-surface.md` |

| Signal | Example condition | Reopens |
|---|---|---|
| An ATLAS release | added, removed or renamed techniques; a new case study on a surface you run or rent | `frameworks-and-what-they-reach.md`; any detection or coverage record tagged with an ATLAS ID |
| An ATT&CK release | a new AI technique, or ATLAS gaining links to the v20 AI techniques | overlap claims; prompt-injection detection tagging |
| An OCSF release | the AI Agent Activity class (#1754) ships, or `ai_model` gains a weights digest | `landing-ai-events-in-ocsf.md`, `models-you-hold.md` |
| An MCP specification revision past 2026-07-28, or an SDK major version | a new revision; a new SDK release that changes what is logged | `mcp-servers-and-manifest-drift.md`, `landing-ai-events-in-ocsf.md` |
| A CoSAI commit that renames or splits a component | a new component under the agent subcategory | `surface-ownability.md` |
| A NIST AI public draft | IR 8596 initial public draft; a COSIS overlay draft; AI RMF revision draft | `frameworks-and-what-they-reach.md` §NIST |
| A platform changes a logging default, export schema or licence tier | content logging turned on by default; an audit log arriving at a lower plan tier | `telemetry-by-surface.md` default-state rows, `rent-or-own-sized-to-the-org.md` |
| A preview feature you were waiting on goes generally available | a discovery, policy or logging feature losing its preview label | `configure-before-you-buy.md`, `incumbent-tool-coverage.md` |
| A KEV entry for software you run or rent in the AI path | a further gateway entry; a first entry for an inference engine | `models-you-hold.md`, `ai-apis-and-the-gateway.md` |
| An acquisition of a vendor you hold in a sensor family | a discovery or non-human-identity vendor changing hands | `reading-vendor-claims.md` |
| A sanctioned coding agent changes a lock, precedence or failure default | a minor version that changes how managed settings or hooks fail | `coding-agent-hooks-and-policy.md` |
| EU guidance or a ruling on prompt capture | an EDPB guideline going final; a supervisory authority ruling on AI-assistant logging | `prompt-capture-and-the-law.md` |
| A model change behind any evaluated system | a version, quantization or fine-tune change | `evaluating-ai-in-the-soc.md`, `fine-tuned-model-is-a-data-store.md` |
| A lab run lands that a declared gap names | the gap's bench or study completes | the document that declared the gap (`scripts/list-declared-gaps.py` lists them) |

## What this does not mean

A document whose pins are one release behind is not wrong. It is a revalidation task, which is why `check-pins.py` counts lagging documents in the weekly self-test line and fails only when this document is behind the newest known release, since this is the one every review prints. Nor does a trigger firing mean the recommendation it reopens has changed; many ATLAS releases add techniques without touching the claims a given document makes, and the work is a re-read with a date, not a rewrite.

Pinning is also not a substitute for reading. The pins say which version the repo checked; they do not say the repo read every change in it, and a practitioner whose own controls key to a framework ID should run the diff against their own records rather than trust that this repo's revalidation covered their use. The revalidation offsets and the monthly cadence are my judgement about how fast these upstreams have moved in 2026, and if ATLAS settles into a slower cadence or starts shipping tombstones, the three-month offset should lengthen.

## Gaps

- **Gap: ATLAS successor for AML.T0024.002**. The successor (`AML.T0005.001`) is inferred from the v2026.10 definition text because the release notes omit the removal, so any mapping resolved through it is Tier D. **Needs**: MITRE errata or a revoked-by relationship in the STIX bundle (mitre-atlas/atlas-data#33).
- **Gap: OWASP 2025 to 2026 ID mapping**. The repo flags controls keyed to LLM0x:2025 IDs but carries no table from 2025 entries to 2026 entries, and I have not read a published one. **Needs**: a desk pass comparing the two editions entry by entry, or a crosswalk published by the OWASP project.
- **Gap: MCP revision and SDK split beyond one SDK**. The finding that the SDK and the revision move different telemetry facts rests on the Python SDK, one fixture server and one host. **Needs**: a repeat of the same run on the TypeScript SDK, and a gateway arm that reads whether common gateways log `Mcp-Method` and `Mcp-Name` by default.
- **Gap: newest-known versions file**. `check-pins.py --current` compares this document against a hand-written list, so a missed upstream release goes unnoticed until the weekly review. **Needs**: a scheduled probe of each release surface in the pin table that writes the newest-known versions file.
- **Gap: revalidation offsets**. The three-to-eight-month offsets are not measured against how often upstream releases actually reopen a claim. **Needs**: a year of weekly self-test counts of documents behind their pins, set against the claims each release actually changed.

## Notes

- The ATLAS release diff takes `revalidate: never` because it compares two frozen, tagged releases; re-running it on the same assets gives the same counts, and the next release gets its own row rather than an update to this one.
- KEV sits in the pin list so `RELEASES.md` can record which snapshot a release read. Because the catalogue changes several times a week, the newest-known versions file passed to `check-pins.py --current` should not list KEV, or this document would fail between weekly reviews; the weekly review bumps the KEV pin by hand.
- ATT&CK's site dates v19.x from 28 April 2026, while the v19.2 STIX tag was cut 2026-08-05; both are right for what they describe, and the pin uses the STIX collection's own version (Tier A).
- The ISO/IEC 42001 row rests on a national standards body's catalogue page because iso.org returned 403; treat the "text unchanged" statement as Tier C until read at the primary.
- The vendor retention windows referenced in the dated table live as default-state rows with their own `last-checked` dates in `telemetry-by-surface.md`, not here, so this document carries no vendor default.
- Judgement marker, 2026-11-10: the monthly reading cadence and the twelve-month build sunset are the maintainer's practice, Tier D, recorded here so a review can print them as such.

## Sources

Tier A
- MITRE ATLAS data releases, v2026.06 to v2026.10, https://github.com/mitre-atlas/atlas-data/releases (v2026.10 released 2026-10-28; `ATLAS-2026.10.yaml` and `stix-atlas.json` read 2026-11-02 and 2026-11-10).
- MITRE ATT&CK STIX data, https://github.com/mitre-attack/attack-stix-data (v20.0 2026-10-13; v20.1 collection modified 2026-11-05, commit `f59b03e`), and https://attack.mitre.org/resources/versions/ (read 2026-11-02).
- MITRE D3FEND ontology, https://github.com/d3fend/d3fend-ontology (release 1.6.0, tag `91629ab`; `develop` read 2026-11-02 and 2026-11-05).
- OCSF schema, https://github.com/ocsf/ocsf-schema (1.9.0, 2026-08-03; #1754 read 2026-11-09).
- Model Context Protocol specification, revision 2026-07-28, https://modelcontextprotocol.io/specification/2026-07-28 (read 2026-11-09).
- CoSAI secure-ai-tooling, https://github.com/cosai-oasis/secure-ai-tooling (`risk-map/yaml/components.yaml` at `622605a1`, 2026-10-21; head re-checked 2026-11-09).
- NIST CSF 2.0 and quick-start guides, https://csrc.nist.gov/news/2026/two-new-csf-2-0-quick-start-guides (read 2026-11-09).
- NIST IR 8596 initial preliminary draft, https://csrc.nist.gov/pubs/ir/8596/iprd (read 2026-11-09).
- NIST Control Overlays for Securing AI Systems, renamed COSIS, https://csrc.nist.gov/projects/cosais (read 2026-11-09).
- NIST AI Risk Management Framework, https://www.nist.gov/itl/ai-risk-management-framework (read 2026-11-09).
- Regulation (EU) 2024/1689, consolidated text CELEX 02024R1689-20260727, https://eur-lex.europa.eu/eli/reg/2024/1689 (read 2026-11-09), and Regulation (EU) 2026/1744.
- CISA Known Exploited Vulnerabilities catalog, https://www.cisa.gov/known-exploited-vulnerabilities-catalog (`kev.json` catalogVersion 2026.11.09).

Tier B
- atlas-d3fend-crosswalk, `VERSION-DIFF-2026-11.md` and `scripts/01_diff_atlas_releases.py`, https://github.com/flying-coyote/atlas-d3fend-crosswalk (commit `66b7726`; own derivation over the Tier A MITRE data above).
- sdw-lab-benchmarks@91e44df (lab master), `t8a-mcp-before-after/RESULTS.md` and `VERIFICATION.md`, https://github.com/flying-coyote/sdw-lab-benchmarks/tree/91e44df/t8a-mcp-before-after (run 2026-11-10).
- mitre-atlas/atlas-data#33, https://github.com/mitre-atlas/atlas-data/issues/33 (opened 2026-11-02; state not checked for this document).
- OWASP Top 10 for LLM Applications 2026, https://genai.owasp.org/llm-top-10/ (project page for the list; 2026 edition published 2026-08-03).
- OWASP Top 10 for Agentic Applications for 2026, https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/ (2025-12-09).
- CSA AI Controls Matrix v1.1, https://cloudsecurityalliance.org/artifacts/ai-controls-matrix-v1-1 (2026-06-22).
- AIUC-1 changelog, https://standard.aiuc-1.com/changelog/ (2026-10-15 release).

Tier C
- EVS catalogue entry for EN ISO/IEC 42001:2026, https://www.evs.ee/en/evs-en-iso-iec-42001-2026 (read 2026-11-09; used only because iso.org returned 403).
