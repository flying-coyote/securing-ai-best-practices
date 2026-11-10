# Sources

One dossier per source the analysis documents rely on: what it is, who publishes it, its evidence tier, the version or date this repo is pinned to, which documents cite it, and when it was last checked. The tier rules are in `CONTRIBUTING.md` and `analysis/evidence-tiers.md`. Upstream, the [security-data-literature-review](https://github.com/flying-coyote/security-data-literature-review) is the broader bibliography, and a dossier here cites its entry where one exists rather than repeating it.

Last curated: 2026-11-10. This is the first fill, built from the Sources section of each of the fifteen routable documents and five stubs, so a dossier's "Last checked" is the read date the citing document records and not a fresh fetch for this file. Cross-references to literature-review entries are not added yet. Document paths below drop the `analysis/` prefix, and a stub is written `stubs/<name>`.

## How a dossier reads

```markdown
### <Source name>

- Publisher: <standards body, regulator, vendor, author>
- Tier: <A | B | C, with the bias flagged | D, labelled>
- Pinned: <version, commit or edition, and the date it was read>
- URL: <primary URL>
- Cited by: <analysis docs>
- Last checked: <YYYY-MM-DD>
- Notes: <what it does and does not cover; anything that limits the tier>
```

A vendor source gets two lines when it is cited both ways: Tier B for what a feature does, and Tier C for any claim about how well it works, how fast it is or how it compares.

The sources several documents share get a full dossier. Sources a single document cites, which is most of the research papers and vendor pages, are grouped in tables that carry the same fields in columns, because about two hundred seven-line dossiers would be harder to keep true than the documents they describe. "Pinned" takes the value a document's frontmatter `pins:` gives; where a document pins nothing, the dossier says "unpinned" and gives the read date.

## Standards, frameworks and catalogues (Tier A)

### CoSAI secure-ai-tooling (risk map)

- Publisher: Coalition for Secure AI, an OASIS Open project
- Tier: A (`decision-sequence.md` grades it B; see Tier disagreements)
- Pinned: commit `622605a13fafaa2784acbdbe3f8d23ee22da4be7` (main, 2026-10-21); `risk-map/yaml/components.yaml`, `risks.yaml`, `controls.yaml`, `personas.yaml`
- URL: https://github.com/cosai-oasis/secure-ai-tooling
- Cited by: surface-ownability, decision-sequence, build-buy-and-the-high-priest, configure-before-you-buy, inventory-and-shadow-ai, reading-vendor-claims, rent-or-own-sized-to-the-org, revalidation-and-pins, stubs/agent-builders, stubs/assistant-oversharing, stubs/rag-stores
- Last checked: 2026-11-10 (counts re-derived for surface-ownability; head re-checked 2026-11-09 for revalidation-and-pins)
- Notes: Apache-2.0. The component map describes a system its operator owns end to end, which is the gap `surface-ownability.md` fills for rented surfaces. Pinned by commit because the documents cite the YAML, not a tagged release.

### CoSAI AI Incident Response Framework V1.0

- Publisher: Coalition for Secure AI, Workstream 2
- Tier: A
- Pinned: document version `24fecc8c`, dated 27 October 2025, PDF read 2026-11-10
- URL: https://www.coalitionforsecureai.org/wp-content/uploads/2026/03/AI-Incident-Response-1.pdf (project: https://github.com/cosai-oasis/ws2-defenders)
- Cited by: stubs/ai-incident-response
- Last checked: 2026-11-10

### MITRE ATLAS

- Publisher: MITRE
- Tier: A (`decision-sequence.md` grades it B; see Tier disagreements)
- Pinned: v2026.10, released 2026-10-28; v2026.06 to v2026.10 data releases for the diff in revalidation-and-pins
- URL: https://atlas.mitre.org/ and https://github.com/mitre-atlas/atlas-data/releases
- Cited by: surface-ownability, decision-sequence, reading-vendor-claims, revalidation-and-pins, stubs/agent-builders
- Last checked: 2026-11-10
- Notes: between v2026.06 and v2026.10, eight technique IDs left the STIX bundle with no revoked or deprecated flag, which is why the documents pin a release and the revalidation document treats each ATLAS release as a reopen trigger. The upstream issue on revocation markers is mitre-atlas/atlas-data#33 (opened 2026-11-02, state not re-checked).

### MITRE ATT&CK and MITRE D3FEND

- Publisher: MITRE
- Tier: A
- Pinned: ATT&CK Enterprise v20.1 (collection modified 2026-11-05, attack-stix-data commit `f59b03e`); D3FEND 1.6.0 (tag `91629ab`)
- URL: https://github.com/mitre-attack/attack-stix-data and https://github.com/d3fend/d3fend-ontology
- Cited by: revalidation-and-pins
- Last checked: 2026-11-05

### OWASP Top 10 for LLM Applications 2026

- Publisher: OWASP GenAI Security Project
- Tier: A (`revalidation-and-pins.md` grades it B; see Tier disagreements)
- Pinned: 2026 edition, resource page dated 2026-08-03, PDF read 2026-11-10
- URL: https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/ (list page https://genai.owasp.org/llm-top-10/)
- Cited by: stubs/ai-you-ship, stubs/rag-stores, revalidation-and-pins
- Last checked: 2026-11-10
- Notes: the entries are cited by their 2026 IDs (LLM01, LLM02, LLM06, LLM09, LLM10), which differ from the 2025 numbering; the routing key `owasp-ids-2025` flags internal controls that still cite the 2025 IDs.

### OWASP Top 10 for Agentic Applications for 2026

- Publisher: OWASP GenAI Security Project
- Tier: B as cited
- Pinned: release of 2025-12-09
- URL: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
- Cited by: revalidation-and-pins
- Last checked: 2026-11-09

### NIST AI Risk Management Framework 1.0 (NIST AI 100-1)

- Publisher: NIST
- Tier: A
- Pinned: AI RMF 1.0, January 2023
- URL: https://doi.org/10.6028/NIST.AI.100-1 (Govern subcategory text at https://airc.nist.gov/airmf-resources/airmf/5-sec-core/)
- Cited by: ai-use-policy-and-intake, saas-embedded-ai-and-vendor-terms (GOVERN 6), revalidation-and-pins
- Last checked: 2026-11-10

### NIST AI 600-1, Generative AI Profile

- Publisher: NIST
- Tier: A
- Pinned: July 2024
- URL: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf
- Cited by: stubs/ai-you-ship
- Last checked: 2026-11-10
- Notes: actions MS-2.7-007, MS-4.2-001, MG-3.1-004, MG-4.1-002 and MG-4.3-001 to -003; thin on output handling as a software-integration problem, so the stub reads OWASP first for that signal.

### Other NIST publications

| Source | Pinned | URL | Cited by | Last checked | Notes |
|---|---|---|---|---|---|
| NIST CSF 2.0 and its quick-start guides | CSF 2.0 | https://csrc.nist.gov/news/2026/two-new-csf-2-0-quick-start-guides | revalidation-and-pins | 2026-11-09 | |
| NIST IR 8596 | initial preliminary draft, 2025-12-16 | https://csrc.nist.gov/pubs/ir/8596/iprd | revalidation-and-pins | 2026-11-09 | a draft, so a reopen trigger rather than a basis for any practice |
| NIST Control Overlays for Securing AI Systems (renamed COSIS) | unpinned | https://csrc.nist.gov/projects/cosais | revalidation-and-pins | 2026-11-09 | |
| NIST SP 800-53 Rev. 5, CM-8 System Component Inventory | Rev. 5 update 1 | https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final | build-buy-and-the-high-priest | 2026-11-10 | |
| NIST SP 800-61 Rev. 3 | April 2025 | https://csrc.nist.gov/pubs/sp/800/61/r3/final | stubs/ai-incident-response | 2026-11-10 | |
| Garfinkel, De-Identification of Personal Information, NIST IR 8053 | 2015, §3.2 | https://doi.org/10.6028/NIST.IR.8053 | prompt-capture-and-the-law, what-to-log-and-what-it-costs | 2026-11-09 | the unkeyed-hash enumeration example |

### ISO/IEC 42001

- Publisher: ISO and IEC
- Tier: A for the standard; the Annex A control numbers rest on secondary summaries and are B at best, and the EVS catalogue entry is C
- Pinned: ISO/IEC 42001:2023; the EN ISO/IEC 42001:2026 catalogue entry was read only to confirm the European adoption
- URL: https://www.iso.org/standard/42001 (EVS entry https://www.evs.ee/en/evs-en-iso-iec-42001-2026)
- Cited by: ai-use-policy-and-intake, saas-embedded-ai-and-vendor-terms, revalidation-and-pins
- Last checked: 2026-11-10
- Notes: paywalled, and iso.org returned 403 to the fetcher, so no document quotes the text. The Annex A summaries used (docs.modulos.ai and riskprofs.com, read 2026-11-10) disagree on some details. Listed under Unverified for that reason.

### OCSF schema

- Publisher: Open Cybersecurity Schema Framework project
- Tier: A (`decision-sequence.md` grades it B; see Tier disagreements)
- Pinned: 1.9.0 (2026-08-03); `message_context` object and `ai_operation` profile
- URL: https://schema.ocsf.io/ and https://github.com/ocsf/ocsf-schema
- Cited by: telemetry-by-surface, what-to-log-and-what-it-costs, decision-sequence, reading-vendor-claims, revalidation-and-pins, build-buy-and-the-high-priest (pin)
- Last checked: 2026-11-09
- Notes: issue #1754 read 2026-11-09 for revalidation-and-pins.

### Model Context Protocol specification

- Publisher: Model Context Protocol project
- Tier: A (`decision-sequence.md` grades it B; see Tier disagreements)
- Pinned: revision 2026-07-28
- URL: https://modelcontextprotocol.io/specification/2026-07-28
- Cited by: decision-sequence, revalidation-and-pins
- Last checked: 2026-11-09

### CISA Known Exploited Vulnerabilities catalog

- Publisher: CISA
- Tier: A (`decision-sequence.md` and `build-buy-and-the-high-priest.md` grade it B; see Tier disagreements)
- Pinned: `kev.json` catalogVersion 2026.11.09 (1,773 entries), released 2026-11-09T19:54Z
- URL: https://www.cisa.gov/known-exploited-vulnerabilities-catalog
- Cited by: revalidation-and-pins, decision-sequence, build-buy-and-the-high-priest, stubs/agent-builders, stubs/ai-incident-response
- Last checked: 2026-11-10
- Notes: the count of 2026 AI orchestration and serving entries (BerriAI LiteLLM, MLflow, Ray, Langflow, n8n; none for vLLM or Ollama) is the documents' own derivation from the catalogue and is carried as a `measurement-claims` row in revalidation-and-pins.

### OASIS CACAO Security Playbooks 2.0

- Publisher: OASIS
- Tier: A
- Pinned: Version 2.0
- URL: https://docs.oasis-open.org/cacao/security-playbooks/v2.0/security-playbooks-v2.0.html
- Cited by: stubs/ai-incident-response
- Last checked: 2026-11-10

### Specifications and overlays graded B as cited

| Source | Publisher | Pinned | URL | Cited by | Last checked | Notes |
|---|---|---|---|---|---|---|
| Sigma specification | SigmaHQ | 2.0.0 | https://github.com/SigmaHQ/sigma-specification | build-buy-and-the-high-priest | 2026-11-10 | |
| OpenTelemetry semantic conventions for generative AI | OpenTelemetry | registry v1.45.0 | https://github.com/open-telemetry/semantic-conventions | telemetry-by-surface | 2026-11-09 | attributes at development stability on the read date |
| CSA AI Controls Matrix | Cloud Security Alliance | v1.1 (2026-06-22) | https://cloudsecurityalliance.org/artifacts/ai-controls-matrix-v1-1 | revalidation-and-pins | 2026-11-09 | link-out only, because its licence allows internal reference and no derivatives |
| AIUC-1 | AIUC | release of 2026-10-15 | https://standard.aiuc-1.com/changelog/ | revalidation-and-pins | 2026-11-09 | link-out only (all rights reserved) |
| Google Secure AI Framework (components; Focus on Agents) | Google | no version on the page, fetched 2026-11-09 | https://saif.google/secure-ai-framework/components and https://saif.google/focus-on-agents | surface-ownability | 2026-11-09 | vendor-published framework, so B and not A |

## Statute, regulation and court text (Tier A)

This is not legal advice; these dossiers record what was read, not what it means for any organization.

| Source | Pinned | URL | Cited by | Last checked | Notes |
|---|---|---|---|---|---|
| GDPR, Regulation (EU) 2016/679 | consolidated text, CELEX 32016R0679 | https://eur-lex.europa.eu/eli/reg/2016/679/oj | prompt-capture-and-the-law, what-to-log-and-what-it-costs, saas-embedded-ai-and-vendor-terms | 2026-11-09 | Recital 49 and Arts. 5, 6, 9, 17, 28, 32, 35, 88 |
| AI Act, Regulation (EU) 2024/1689 as amended by (EU) 2026/1744 | consolidated CELEX 02024R1689-20260727 | https://eur-lex.europa.eu/eli/reg/2024/1689/oj | prompt-capture-and-the-law, decision-sequence, revalidation-and-pins, build-buy-and-the-high-priest, stubs/ai-you-ship | 2026-11-10 | stand-alone Annex III obligations apply from 2 December 2027 (Art. 113) |
| NIS2 Directive (EU) 2022/2555 | as in force | EUR-Lex | prompt-capture-and-the-law | 2026-11-09 | Arts. 21 and 23 |
| DORA, Regulation (EU) 2022/2554, and RTS (EU) 2024/1774 | RTS CELEX 32024R1774 | EUR-Lex | prompt-capture-and-the-law | 2026-11-09 | RTS Arts. 12 and 22 at the primary; DORA Art. 17 through a non-EUR-Lex rendering |
| ePrivacy Directive 2002/58/EC | consolidated CELEX 02002L0058-20091219 | EUR-Lex | prompt-capture-and-the-law | 2026-11-09 | Art. 5(3) |
| CJEU Case C-65/23 | judgment of 19 December 2024, ECLI:EU:C:2024:1051 | https://curia.europa.eu/juris/liste.jsf?num=C-65/23 | prompt-capture-and-the-law, decision-sequence | 2026-11-09 | |
| ECtHR [GC] Bărbulescu v Romania, no. 61496/08 | 5 September 2017, §121 | HUDOC item 001-177082 | prompt-capture-and-the-law, what-to-log-and-what-it-costs | 2026-11-09 | |
| BetrVG §§80, 87 (Germany) | as published | gesetze-im-internet.de | prompt-capture-and-the-law | 2026-11-09 | the Federal Labour Court's "objectively capable" reading is settled case law not re-verified, so that reading is B |
| WOR Art. 27 (Netherlands) | BWBR0002747 | wetten.overheid.nl | prompt-capture-and-the-law | 2026-11-09 | |
| UK Data (Use and Access) Act 2025, s. 70 and Sch. 4 | as enacted | legislation.gov.uk | prompt-capture-and-the-law | 2026-11-09 | commencement not checked |
| UK SI 2018/356, regs. 3 and 4 | as made | legislation.gov.uk | prompt-capture-and-the-law | 2026-11-09 | |
| 18 U.S.C. §2511 | as read 2026-11-09 | https://www.law.cornell.edu/uscode/text/18/2511 | prompt-capture-and-the-law, ai-use-policy-and-intake | 2026-11-09 | |
| CB Financial Services, Inc., Form 8-K, Item 1.05 | report dated 2026-05-07, signed 2026-05-11 | https://www.sec.gov/Archives/edgar/data/1605301/000160530126000021/cbfv-20260507.htm | ai-use-policy-and-intake, inventory-and-shadow-ai | 2026-11-10 | a public filing, cited for what the registrant itself disclosed |

## Regulator and agency guidance

| Source | Tier | Pinned | URL | Cited by | Last checked | Notes |
|---|---|---|---|---|---|---|
| WP29 Opinion 2/2017 on data processing at work (WP249) | B as cited | 8 June 2017 | EDPB-endorsed WP29 archive | prompt-capture-and-the-law, what-to-log-and-what-it-costs | 2026-11-09 | §§5.3, 6.2, 6.4 |
| WP29 DPIA Guidelines (WP248 rev.01) | B as cited | 4 October 2017 | EDPB-endorsed WP29 archive | prompt-capture-and-the-law | 2026-11-09 | |
| EDPB Opinion 28/2024 (AI models) | B as cited | 17 December 2024 | edpb.europa.eu | prompt-capture-and-the-law | 2026-11-09 | |
| EDPB Guidelines 1/2024 on Art. 6(1)(f) | B as cited | version 1.0 for consultation, 8 October 2024 | edpb.europa.eu | prompt-capture-and-the-law, what-to-log-and-what-it-costs | 2026-11-09 | final version not confirmed as of 2026-11-09 |
| EDPB Guidelines 01/2025 on pseudonymisation | B as cited | consultation version | edpb.europa.eu | prompt-capture-and-the-law | 2026-11-09 | final version not confirmed as of 2026-11-09 |
| EDPB-EDPS Joint Opinion 2/2026 | B as cited | 10 February 2026 | edpb.europa.eu | prompt-capture-and-the-law | 2026-11-09 | on the Digital Omnibus proposal |
| CNIL délibération 2021-122 (logging) | B as cited | 14 October 2021 | cnil.fr | prompt-capture-and-the-law | 2026-11-09 | quoted in the document's own translation |
| Garante provvedimento 364 | B as cited | 6 June 2024, docweb 10026277 | garanteprivacy.it | prompt-capture-and-the-law | 2026-11-09 | orientative by its own account |
| ArbVG §96 (Austria) | B as cited | as published | ris.bka.gv.at | prompt-capture-and-the-law | 2026-11-09 | read with secondary summaries |
| UK NCSC, "Prompt injection is not SQL injection (it may be worse)" | B | 2025-12-08 | https://www.ncsc.gov.uk/blog-post/prompt-injection-is-not-sql-injection | reading-vendor-claims | 2026-11-10 | |
| NSA and CISA, AA23-278A, top ten misconfigurations | B | 2023-10-05 | https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-278a | configure-before-you-buy | 2026-11-10 | |
| CISA BOD 25-01 implementation guidance | B | issued 2024-12-17 | https://www.cisa.gov/news-events/directives/bod-25-01-implementation-guidance-implementing-secure-practices-cloud-services | configure-before-you-buy | 2026-11-10 | |
| CISA ScubaGear | B | unpinned | https://github.com/cisagov/ScubaGear | configure-before-you-buy | 2026-11-10 | |
| CISA ScubaGoggles baselines, including `gemini.md` | A as cited (see Tier disagreements) | main, read 2026-11-09 | https://github.com/cisagov/ScubaGoggles/blob/main/baselines/README.md | saas-embedded-ai-and-vendor-terms | 2026-11-09 | |
| OMB M-25-21 | B | 2025-04-03 | https://www.whitehouse.gov/wp-content/uploads/2025/02/M-25-21-Accelerating-Federal-Use-of-AI-through-Innovation-Governance-and-Public-Trust.pdf | build-buy-and-the-high-priest | 2026-11-10 | federal policy, cited as practice evidence |
| Federal CIO Council, Application Rationalization Playbook | B | v1.1, June 2019 | not linked | build-buy-and-the-high-priest | 2026-11-10 | read through summaries; listed under Unverified |
| Center for Internet Security, Community Defense Model v2.0 | B | blog announcement | https://www.cisecurity.org/insights/blog/cis-introduces-v2-0-of-the-cis-community-defense-model | configure-before-you-buy | 2026-11-10 | |

## Lab measurement and the author's other public repositories (Tier B)

### sdw-lab-benchmarks

- Publisher: the author's public lab repository
- Tier: B (first-party measurement, single host unless a run says otherwise; each run's qualifiers travel with the claim)
- Pinned: branch `hub/ai-research-2026-11-09`, at the commit each document's `measurement-claims` row gives (table below); the branch has not merged to master, and the rows are re-pinned to master hashes when it does
- URL: https://github.com/flying-coyote/sdw-lab-benchmarks
- Cited by: the runs below
- Last checked: 2026-11-10
- Notes: every run cited here is linked to its RESULTS and VERIFICATION files by commit hash, never copied (Decision 10). Every run listed carries a VERIFIED-WITH-FIXES verdict in its VERIFICATION file.

| Run folder | What it measured | Cited by | Pin as the document cites it |
|---|---|---|---|
| `t1-shadow-ai-discovery` | five discovery methods against nine planted shadow-AI surfaces on one endpoint | inventory-and-shadow-ai | `e568f5b` |
| `t2-platform-telemetry` | Claude Code 2.1.321 OpenTelemetry fields at defaults and with content gates on; Ollama 0.20.6 server log | telemetry-by-surface, what-to-log-and-what-it-costs | `e568f5b` in telemetry-by-surface; no hash in what-to-log-and-what-it-costs |
| `t8a-mcp-before-after` | MCP Python SDK 1.30.0 to 2.3.0 and protocol revision 2025-11-25 to 2026-07-28 on one fixture server | revalidation-and-pins | `e0aaadc` |
| `t9-pretooluse-hook-enforcement` | Claude Code hook and deny-rule enforcement across settings sources and precedence pairs | coding-agent-hooks-and-policy | pending (`T9-FIX-COMMIT-PENDING`), since the verifier's fixes were not yet committed when the document was written |
| `atlas-ocsf-observables` | ATLAS techniques with mapped OCSF fields, detection outcome per technique across three seeds | reading-vendor-claims | `e0aaadc` |
| `ai-artifact-sbom` | four SBOM tools against six AI artifacts on one host | reading-vendor-claims | `e0aaadc` |
| `mcp-manifest-drift` | snapshot-and-diff detection over three real MCP servers | reading-vendor-claims | `e0aaadc` |
| `agent-toolcall-schemas` | one MCP tools/call typed in OCSF, OpenTelemetry and OWASP AOS | reading-vendor-claims, what-to-log-and-what-it-costs | `e0aaadc` in reading-vendor-claims; no hash in what-to-log-and-what-it-costs |
| `agent-telemetry-retention` | storage footprint and cost per capture tier (R6) | what-to-log-and-what-it-costs | no hash yet |

### atlas-d3fend-crosswalk

- Publisher: the author's public crosswalk repository
- Tier: B (own derivation over Tier A MITRE data)
- Pinned: commit `66b7726`, `VERSION-DIFF-2026-11.md` and `scripts/01_diff_atlas_releases.py`
- URL: https://github.com/flying-coyote/atlas-d3fend-crosswalk
- Cited by: revalidation-and-pins
- Last checked: 2026-11-02

### claude-code-project-best-practices

- Publisher: the author's public repository for Claude Code projects
- Tier: B (practitioner methodology)
- Pinned: unpinned, read 2026-11-10; `analysis/evidence-tiers.md`, Decision 15, `analysis/safety-and-sandboxing.md`, `analysis/ai-tool-vetting.md`
- URL: https://github.com/flying-coyote/claude-code-project-best-practices
- Cited by: evidence-tiers, coding-agent-hooks-and-policy (`follows:`)
- Last checked: 2026-11-10
- Notes: MIT licence. Shares a maintainer with this repo, so it is cited as methodology and as the follow-lane canon for the Claude Code mechanism, never as independent corroboration.

### The forthcoming ai-config-pointers set

- Publisher: the author; a separate repository that serves as this repo's platforms layer (Decision 12)
- Tier: not graded here, because it is not public and no document cites it as evidence
- Pinned: none
- URL: none until it is public
- Cited by: configure-before-you-buy, rent-or-own-sized-to-the-org, telemetry-by-surface, saas-embedded-ai-and-vendor-terms, stubs/agent-builders, stubs/assistant-oversharing, all as forthcoming
- Last checked: 2026-11-10
- Notes: the vendor admin pages behind its rows were read on 2026-11-09, and the documents cite the vendor pages directly wherever they rely on them, except the retention and default-state rows in rent-or-own-sized-to-the-org, whose row-level URLs wait for that set to publish.

## Practitioner talks (Tier B)

| Source | Pinned | Cited by | Last checked | Notes |
|---|---|---|---|---|
| [un]prompted practitioner conferences, March and October 2026 | talks by the speakers each document names | decision-sequence, stubs/ai-incident-response | 2026-11-09 | auto-transcripts read by line and paraphrased, so no talk is quoted; one practitioner each, so B for what they report doing and D for anything generalised from it |

## Peer-reviewed research (Tier A)

| Source | Venue | Identifier | Cited by | Notes |
|---|---|---|---|---|
| Nasr, Carlini et al., "The Attacker Moves Second" | USENIX Security 2026 | arXiv 2510.09023 | reading-vendor-claims, decision-sequence, build-buy-and-the-high-priest | figures from arXiv v1 (§5.3, Table 7, App. G.1); authors affiliated with model vendors, flagged in decision-sequence |
| Mireshghallah et al., "Trust No Bot" | COLM 2024 | arXiv 2407.11438 | inventory-and-shadow-ai, prompt-capture-and-the-law, telemetry-by-surface | |
| Zhan, Fang, Panchal and Kang, adaptive attacks on indirect prompt injection defences | Findings of NAACL 2025 | doi:10.18653/v1/2025.findings-naacl.395 | coding-agent-hooks-and-policy, reading-vendor-claims | |
| Debenedetti et al., "Defeating Prompt Injections by Design" (CaMeL) | IEEE SaTML 2026 | doi:10.1109/satml68715.2026.00040 | coding-agent-hooks-and-policy | |
| Debenedetti et al., "AgentDojo" | NeurIPS 2024 | doi:10.52202/079017-2636 | reading-vendor-claims | |
| Hackett, Birch, Trawicki, Suri and Garraghan, "Bypassing LLM Guardrails" | LLMSec 2025 | ACL Anthology 2025.llmsec-1.8 | reading-vendor-claims | vendor flag in the document |
| Abdelnabi et al., "LLMail-Inject" | Findings of EMNLP 2026 | 10.18653/2026.findings-emnlp.514 | reading-vendor-claims, what-to-log-and-what-it-costs | Microsoft-led, and the classifier defences tested are Microsoft's, flagged |
| Shire and Kim, "PIDS-Bench" | IEEE Access 2026 | doi:10.1109/access.2026.3728186 | reading-vendor-claims, what-to-log-and-what-it-costs | |
| Turpin, Michael, Perez and Bowman, "Language Models Don't Always Say What They Think" | NeurIPS 2023 | 10.52202/075280-3275 | what-to-log-and-what-it-costs | |
| Greshake, Abdelnabi, Mishra, Endres, Holz and Fritz, indirect prompt injection | ACM AISec 2023 | doi:10.1145/3605764.3623985 | stubs/rag-stores | |
| Gruber and Hilgert, forensic analysis of OpenClaw | Digital Threats: Research and Practice 2026 | doi:10.1145/3848419 | telemetry-by-surface | |
| Ravid et al., electronic monitoring meta-analysis | Personnel Psychology 2022 | 10.1111/peps.12514 | prompt-capture-and-the-law | studies predate generative-AI assistants |
| Mollaeefar et al., "Chatbot Confessions" | PoPETs 2026(3) | 10.56553/popets-2026-0081 | prompt-capture-and-the-law, what-to-log-and-what-it-costs | |
| Aghili, Li and Khomh, privacy in software logs | FSE 2025 | 10.1145/3715779 | prompt-capture-and-the-law, what-to-log-and-what-it-costs | |
| Pilán et al., text anonymization | Computational Linguistics 2022 | 10.1162/coli_a_00458 | prompt-capture-and-the-law | |
| Humlum and Vestergaard | PNAS 2024 | doi:10.1073/pnas.2414972121 | inventory-and-shadow-ai | |
| Carlini, Tramèr, Wallace et al., "Extracting Training Data from Large Language Models" | USENIX Security 2021 | usenix.org | rent-or-own-sized-to-the-org | |
| Qi, Zeng, Xie et al., fine-tuning compromises safety | ICLR 2024 | arXiv 2310.03693 | rent-or-own-sized-to-the-org | |
| Goldwasser, Kim, Vaikuntanathan and Zamir, undetectable backdoors | FOCS 2022 | arXiv 2204.06974 | rent-or-own-sized-to-the-org | |
| Sculley et al., "Hidden Technical Debt in Machine Learning Systems" | NeurIPS 2015 | proceedings.neurips.cc | build-buy-and-the-high-priest | |
| Avelino, Passos, Hora and Valente, truck factors | ICPC 2016 | doi:10.1109/ICPC.2016.7503718 | build-buy-and-the-high-priest | |
| Avelino, Constantinou, Valente and Serebrenik, abandonment and survival of open source projects | ESEM 2019 | doi:10.1109/ESEM.2019.8870181 | build-buy-and-the-high-priest | the 86 percent figure re-read from the RQ2 text |
| Coelho and Valente, "Why Modern Open Source Projects Fail" | ESEC/FSE 2017 | doi:10.1145/3106237.3106246 | build-buy-and-the-high-priest | |
| MacCormack, Baldwin and Rusnak, the mirroring hypothesis | Research Policy 41(8), 2012 | doi:10.1016/j.respol.2012.04.011 | build-buy-and-the-high-priest | read at abstract level |
| Farrell and Klemperer, switching costs and network effects | Handbook of Industrial Organization vol. 3, 2007 | doi:10.1016/S1573-448X(06)03031-7 | build-buy-and-the-high-priest | |
| Yin et al., configuration errors | SOSP 2011 | doi:10.1145/2043556.2043572 | configure-before-you-buy | parameter-mistake range from the authors' slides |
| Liu, Zhou, Zhang et al., software misconfigurations | Empirical Software Engineering 2026 | doi:10.1007/s10664-026-10892-6 | configure-before-you-buy | read in full (arXiv 2412.11121v4) |
| Dietrich, Krombholz, Borgolte and Fiebig, operators and misconfigurations | CCS 2018 | doi:10.1145/3243734.3243794 | configure-before-you-buy | |
| Xu, Zhang, Huang et al., "Do Not Blame Users for Misconfigurations" | SOSP 2013 | doi:10.1145/2517349.2522727 | configure-before-you-buy | abstract only |
| Alahmadi, Axon and Martinovic, "99% False Positives" | USENIX Security 2022 | usenix.org | configure-before-you-buy | |
| Uetz et al., evasions of SIEM rules | USENIX Security 2024 | arXiv 2311.10197 | configure-before-you-buy | |
| Wool, firewall configuration errors | IEEE Internet Computing 2010 | doi:10.1109/mic.2010.29 | configure-before-you-buy | |
| Weichselbaum et al., "CSP Is Dead, Long Live CSP!" | CCS 2016 | doi:10.1145/2976749.2978363 | configure-before-you-buy | |
| Álvarez, Nuño, Bulnes et al., network misconfigurations in Spanish organisations | Computer Networks 2026 | doi:10.1016/j.comnet.2026.112631 | configure-before-you-buy | abstract only |
| Rahman et al., security smells in Ansible and Chef; Kubernetes manifests | ACM TOSEM 2021 and 2023 | doi:10.1145/3408897; doi:10.1145/3579639 | configure-before-you-buy | |

## Preprints and working papers (Tier B)

| Source | Identifier | Cited by | Notes |
|---|---|---|---|
| Chhetri, Tariq, Aamir, Grobler et al., "From Frontier to Shadow AI" (CSIRO) | arXiv 2606.00088 | ai-use-policy-and-intake, inventory-and-shadow-ai, saas-embedded-ai-and-vendor-terms | interview study of 27 Australian critical-infrastructure organisations; preprint under review |
| METR, early-2025 AI and experienced open-source developer productivity | arXiv 2507.09089 | build-buy-and-the-high-priest | |
| Bick, Blandin and Deming | NBER w32966 | inventory-and-shadow-ai | |
| Shi et al., Progent | arXiv 2504.11703 | coding-agent-hooks-and-policy | |
| Beurer-Kellner et al., design patterns for securing LLM agents | arXiv 2506.08837 | coding-agent-hooks-and-policy | |
| Sharma et al., Ajar | arXiv 2609.26900 | coding-agent-hooks-and-policy | |
| Davidovich et al., Permission Denied | arXiv 2608.02670 | coding-agent-hooks-and-policy | |
| Yan, security rules in CLAUDE.md versus built-in controls | arXiv 2608.23550 | coding-agent-hooks-and-policy | |
| Zhu and Pu, "TelemetrySuffBench" | arXiv 2608.07899 | telemetry-by-surface, what-to-log-and-what-it-costs | |
| Muhamed and Smith, "MOLE" | arXiv 2609.06966 | what-to-log-and-what-it-costs, prompt-capture-and-the-law | synthetic setting |

## Practitioner and historical sources

| Source | Tier | Cited by | Notes |
|---|---|---|---|
| Beyer, Jones, Petoff and Murphy (eds.), Site Reliability Engineering, ch. 1 (2016), https://sre.google/sre-book/introduction/ | B | build-buy-and-the-high-priest | |
| David P. Reed, "That Sneaky Exponential" (1999), https://www.deepplum.com/gfn/reedslaw.html | B | build-buy-and-the-high-priest | |
| Briscoe, Odlyzko and Tilly, "Metcalfe's Law Is Wrong", IEEE Spectrum, July 2006 | B | build-buy-and-the-high-priest | |
| Melvin E. Conway, "How Do Committees Invent?", Datamation 14(4), 1968 | C | build-buy-and-the-high-priest | trade magazine |
| Maintenance-share figures attributed to Lientz and Swanson 1980 and Erlikh 2000 | C | build-buy-and-the-high-priest | secondary compilations only; direction used, no figure; listed under Unverified |
| Permiso, "Exploiting hosted models" (2024-10-03) | B | what-to-log-and-what-it-costs | practitioner incident write-up |
| Invariant Labs, GitHub MCP vulnerability (2025-05-26) | B | what-to-log-and-what-it-costs | vendor research with a product to sell, flagged |
| Wiz, "s1ngularity's aftermath" (2025-09-03) | B | what-to-log-and-what-it-costs | vendor research, flagged |
| Anthropic, "Disrupting the first reported AI-orchestrated cyber espionage campaign" (November 2025) | B | what-to-log-and-what-it-costs | the vendor describing its own detection, flagged |
| AI Incident Database report 5593 (Replit agent, July 2025), https://incidentdatabase.ai/reports/5593/ | C | stubs/ai-incident-response | the agent's own statements were the only account of why |

## Vendor and open-source tool documentation (Tier B for what a feature does)

Every row here is Tier B for what the product does, read on the date given, and any efficacy, coverage or comparison claim from the same publisher is Tier C with the bias flagged, listed in the next section. Neither line can raise a document's confidence past B (the README's Boundaries and `analysis/evidence-tiers.md`).

| Vendor or project | Pages read | Read | Cited by |
|---|---|---|---|
| Anthropic | Claude Code hooks, permissions, settings, managed settings, settings reference, sandboxing, monitoring, headless and costs (code.claude.com/docs); Compliance API (platform.claude.com); custom data retention for Enterprise (support.claude.com article 10440198); tenant restrictions (support.claude.com article 13198485); pricing (claude.com/pricing) | 2026-11-09 and 2026-11-10 | coding-agent-hooks-and-policy, configure-before-you-buy, telemetry-by-surface, what-to-log-and-what-it-costs, saas-embedded-ai-and-vendor-terms, rent-or-own-sized-to-the-org, inventory-and-shadow-ai |
| Microsoft | Purview audit for Copilot and AI apps (ms.date 2026-08-26), auditing solutions overview, Purview for generative AI apps, DSPM for AI, DLP for Microsoft 365 Copilot, sensitivity labels; Microsoft 365 Copilot privacy (updated 2026-11-04), Copilot admin center settings, public web access; Restricted SharePoint Search and restricted content discovery; Copilot Studio data policies, security and governance, Managed Environments sharing limits; Entra agent identities, application permissions, diagnostic settings; Azure OpenAI monitoring and Foundry model monitoring; Secure Score | 2026-11-09 and 2026-11-10 | telemetry-by-surface, configure-before-you-buy, saas-embedded-ai-and-vendor-terms, inventory-and-shadow-ai, ai-use-policy-and-intake, what-to-log-and-what-it-costs, stubs/assistant-oversharing, stubs/agent-builders |
| Google | Workspace Gemini log events, BigQuery log export and retention, Gemini conversation history settings, OAuth log events, Privacy Hub, Gemini app access, DLP for Gemini; Gemini Enterprise usage audit logs; Cloud Logging quotas; Vertex AI audit logging and request-response logging (Pre-GA on the read date); Agent Identity overview; Security Command Center AI Protection; Chrome Enterprise reporting connectors | 2026-11-09 and 2026-11-10 | telemetry-by-surface, configure-before-you-buy, saas-embedded-ai-and-vendor-terms, inventory-and-shadow-ai, decision-sequence, stubs/assistant-oversharing, stubs/agent-builders |
| AWS | Bedrock model invocation logging; Bedrock and `bedrock-mantle` CloudTrail logging; CloudTrail event history and concepts; Bedrock AgentCore policy and enforcement modes | 2026-11-09 and 2026-11-10 | telemetry-by-surface, configure-before-you-buy, inventory-and-shadow-ai, coding-agent-hooks-and-policy, what-to-log-and-what-it-costs, stubs/agent-builders |
| OpenAI | Codex approvals and security, rules, governance and managed configuration (learn.chatgpt.com); ChatGPT pricing | 2026-11-09 and 2026-11-10 | coding-agent-hooks-and-policy, telemetry-by-surface, rent-or-own-sized-to-the-org |
| GitHub | Copilot hooks reference, coding agent firewall, Copilot audit logs, enterprise audit log streaming, Copilot plans | 2026-11-09 and 2026-11-10 | coding-agent-hooks-and-policy, telemetry-by-surface, configure-before-you-buy, rent-or-own-sized-to-the-org |
| Cursor | hooks; compliance and monitoring; pricing | 2026-11-09 and 2026-11-10 | coding-agent-hooks-and-policy, telemetry-by-surface, configure-before-you-buy, rent-or-own-sized-to-the-org |
| Gemini CLI | policy engine (updated 2026-04-30), hooks (updated 2026-04-10), enterprise (updated 2026-06-16) | 2026-11-09 | coding-agent-hooks-and-policy |
| GitLab | Duo MCP clients | 2026-11-09 | coding-agent-hooks-and-policy |
| Kong | `ai-mcp-proxy` per-tool ACLs | 2026-11-09 | coding-agent-hooks-and-policy |
| Atlassian | Rovo access, Rovo data usage and privacy, Atlassian Intelligence lesson, public issue AX-2026 | 2026-11-09 and 2026-11-10 | saas-embedded-ai-and-vendor-terms, inventory-and-shadow-ai |
| Salesforce | LLM data masking (Trailhead), generative AI audit and feedback data (Trailhead and data model guide), Agentforce Implementation Guide | 2026-11-09 | saas-embedded-ai-and-vendor-terms, telemetry-by-surface, stubs/agent-builders |
| ServiceNow | Now Assist data-sharing opt-out, data overflow processing, Generative AI Controller release notes, Now Assist Guardian, AI Control Tower asset discovery | 2026-11-09 and 2026-11-10 | saas-embedded-ai-and-vendor-terms, stubs/agent-builders |
| Slack | privacy principles for search, learning and AI; app approval; Audit Logs API | 2026-11-09 and 2026-11-10 | saas-embedded-ai-and-vendor-terms |
| Snowflake, Databricks, Workato, MuleSoft | Cortex cross-region inference; partner-powered AI features (doc date 2026-11-03); Workato Copilot, Agent Studio security and Genie governance; MuleSoft generative AI enablement | 2026-11-09 and 2026-11-10 | saas-embedded-ai-and-vendor-terms, stubs/agent-builders |
| Okta | log streaming | 2026-11-09 | telemetry-by-surface |
| CrowdStrike, Obsidian Security | shadow-AI and agent governance feature pages, cited for what the feature does | 2026-11-09 | saas-embedded-ai-and-vendor-terms |
| Ollama, vLLM | Ollama FAQ; `vllm serve` CLI reference | 2026-11-09 | telemetry-by-surface, inventory-and-shadow-ai |
| osquery, Zeek, Syft | osquery `vscode_extensions` table spec (master); tool versions pinned in inventory-and-shadow-ai (osquery 5.24.0, Zeek 8.0.11, Syft 1.55.0) | 2026-11-09 | inventory-and-shadow-ai |

## Vendor claims, vendor studies and secondary coverage (Tier C, bias flagged)

| Source | Cited by | Bias |
|---|---|---|
| IBM and Ponemon, Cost of a Data Breach Report 2025 (IBM Think summary, 2025-11-12) | ai-use-policy-and-intake | survey of 600 breached organizations by a vendor that sells breach response |
| Datadog, State of Cloud Security 2025 | configure-before-you-buy | publisher sells the remediation and measures its own customers |
| Orca Security, 2026 State of AI Security Report | configure-before-you-buy | as above; figures are per organization per its methodology page |
| Zylo, 2025 SaaS Management Index | configure-before-you-buy | as above |
| LayerX, Enterprise AI and SaaS Data Security Report 2025 | inventory-and-shadow-ai | telemetry from the vendor's own install base |
| Veracode, 2025 GenAI Code Security Report | build-buy-and-the-high-priest | vendor benchmark; Veracode sells code-security remediation |
| Google Cloud, Announcing the 2024 DORA report | build-buy-and-the-high-priest | self-report association |
| Vendor product pages re-read 2026-11-10 (Lakera Guard, Noma, Harmonic, Wiz AI-SPM, Zenity, HiddenLayer) and releases read 2026-11-09 (Runlayer, Oasis, and the acquirers in the reading-vendor-claims ledger) | reading-vendor-claims | marketing; acquirer releases are Tier B only for the fact and date of the acquisition |
| AI Security Startups Map, https://startups.prompt.security/ (data file pulled 2026-11-09) | reading-vendor-claims | curator owned by SentinelOne; no price from it appears as fact |
| TechCrunch, "OpenAI says AI browsers may always be vulnerable to prompt injection attacks" (2025-12-22) | reading-vendor-claims | press coverage of a vendor statement |
| Coverage counts and risk percentages on the CrowdStrike and Obsidian pages | saas-embedded-ai-and-vendor-terms | marketing, not tested |
| Guardrail and masking effectiveness statements for Salesforce Einstein Trust Layer, ServiceNow Now Assist Guardian and Atlassian Rovo | saas-embedded-ai-and-vendor-terms | vendor efficacy statements, not tested |
| Atlassian Community thread on the September 2025 Rovo rollout | saas-embedded-ai-and-vendor-terms | user reports |
| Salesforce developer and product blogs on hosted and external MCP servers (2026) | stubs/agent-builders | vendor blogs |
| A ServiceNow community post (June 2026) on MCP server approval | stubs/agent-builders | practitioner post, not vendor documentation |
| Anthropic Claude Code costs page, usage figures only | what-to-log-and-what-it-costs | vendor interest flagged; the page is B for what the product does |

## Tier D, the author's judgement

Each of these is labelled where the document uses it, orders actions within a priority band and never raises one (Decisions 3 and 15).

- The four perspectives and the decision order, dated 2026-11-09 (decision-sequence), argued at length in a forthcoming long-form article on securitydataworks.com.
- The configure-first view and the five-state grading rule (configure-before-you-buy, build-buy-and-the-high-priest, ai-use-policy-and-intake).
- The rent-leaning sizing perspective, dated 2026-11-10 (rent-or-own-sized-to-the-org).
- The ownability grid, bands and case-study assignments, dated 2026-11-09 (surface-ownability).
- The capture-tier model, triggers, buffer design and reconstruction rule (what-to-log-and-what-it-costs) and the decision table by jurisdiction, dated 2026-11-10 (prompt-capture-and-the-law).
- The procurement ask, the four sentence types and the fifth scanner question (reading-vendor-claims).
- The build list, sensor preference, preconditions, twelve-month default and small-team collapse (build-buy-and-the-high-priest).
- The ordering of the summary actions in stubs/agent-builders and stubs/ai-incident-response, dated 2026-11-10.
- The tier ladder's own structure (evidence-tiers, and the document template).

## Tier disagreements

Where documents grade the same source differently, the dossier carries the tier CONTRIBUTING's table gives and each document keeps its own grade for its own claims until a revalidation pass reconciles them; no document's tier was changed for this file.

- `decision-sequence.md` grades the CoSAI risk map, MITRE ATLAS, OCSF, the MCP specification and the CISA KEV catalogue as Tier B, where the other documents and the table grade them A.
- `build-buy-and-the-high-priest.md` grades the CISA KEV catalogue B, and the Sigma specification B.
- `revalidation-and-pins.md` grades the OWASP Top 10 for LLM Applications 2026 B, where `stubs/ai-you-ship.md` and `stubs/rag-stores.md` grade it A.
- `saas-embedded-ai-and-vendor-terms.md` grades CISA's ScubaGoggles baselines A, while `configure-before-you-buy.md` grades the sibling ScubaGear B.
- `prompt-capture-and-the-law.md` grades EDPB, WP29, CNIL and Garante guidance B, where CONTRIBUTING's table would allow A for regulator text; the stricter grade fits non-binding and consultation documents, and the dossier follows the document.
- The OpenAI Compliance API help article is B in `saas-embedded-ai-and-vendor-terms.md` and C in `telemetry-by-surface.md`, both for the same excerpt-only reading (see Unverified).

## Unverified

Claims or sources that could not be confirmed against a primary on the last pass are listed here, with the date and what was tried, until they are confirmed or dropped.

| Source | Cited by | Date | What was tried |
|---|---|---|---|
| OpenAI, "Compliance API for Enterprise customers" (help.openai.com article 9261474) | saas-embedded-ai-and-vendor-terms, telemetry-by-surface | 2026-11-09 | direct fetch returned HTTP 403; read through search excerpts only |
| OpenAI, corporate network controls in ChatGPT Enterprise (help.openai.com article 20001323) | inventory-and-shadow-ai | 2026-11-09 | fetch refused |
| Salesforce, "Export Agentforce Session Tracing Data (Beta)" | telemetry-by-surface | 2026-11-09 | direct fetch returned HTTP 403; read through a search summary |
| Microsoft, Copilot Studio audit logs for admins, makers and users | stubs/agent-builders | 2026-11-09 | the URL redirected when fetched; read through a search excerpt, as was the name of the tenant setting for publishing agents with generative AI features |
| ServiceNow, Now Assist data overflow processing default | saas-embedded-ai-and-vendor-terms | 2026-11-09 | page fetched, the default itself taken from a search summary |
| ISO/IEC 42001:2023 Annex A control numbering | ai-use-policy-and-intake, revalidation-and-pins | 2026-11-10 | iso.org returned 403; numbering taken from two secondary summaries that disagree on some details |
| ICO, "Monitoring workers" (3 October 2023) | prompt-capture-and-the-law | 2026-11-09 | ICO pages returned 403; read through law-firm summaries |
| NY Civil Rights Law §52-c, Conn. Gen. Stat. §31-48d, 19 Del. C. §705 | prompt-capture-and-the-law | 2026-11-09 | read through law-firm summaries, not at the statute |
| NLRB GC 25-05 (14 February 2025) and the Digital Omnibus Council mandate ST 14756/26 | prompt-capture-and-the-law | 2026-11-09 | read through press and law-firm reports |
| Federal Labour Court "objectively capable" reading of BetrVG §87(1) Nr. 6; DORA Art. 17; CCPA employee-data date | prompt-capture-and-the-law | 2026-11-09 | not re-read at the primary, so each stays at B in the document |
| Federal CIO Council, Application Rationalization Playbook v1.1 | build-buy-and-the-high-priest | 2026-11-10 | read through summaries |
| Lientz and Swanson 1980; Erlikh 2000 maintenance shares | build-buy-and-the-high-priest | 2026-11-10 | secondary compilations only; the document uses the direction and no figure |
| MacCormack 2012, the 2024 DORA report, Veracode 2025 | build-buy-and-the-high-priest | 2026-11-10 | rest on abstracts, vendor posts and search summaries, as the document's notes record |
