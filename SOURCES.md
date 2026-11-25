# Sources

One dossier per source the analysis documents rely on: what it is, who publishes it, its evidence tier, the version or date this repo is pinned to, which documents cite it, and when it was last checked. The tier rules are in `CONTRIBUTING.md` and `analysis/evidence-tiers.md`. Upstream, the [security-data-literature-review](https://github.com/flying-coyote/security-data-literature-review) is the broader bibliography, and a dossier here cites its entry where one exists rather than repeating it.

Last curated: 2026-11-24. On that date the four research, preprint, practitioner and vendor-claim tables gained a "Last checked" column, the abstract-only and unnoted rows were added to Unverified, and the CoSAI Agentic IAM dossier's §5.1 note was brought in line with its citing document; no source was re-read for this pass. The file began as a first fill on 2026-11-10, built from the Sources section of each routable document and stub (the README's count line gives how many), first for the documents of the initial draft and then, on the same date, for those written after them, so a dossier's "Last checked" is the read date the citing document records and not a fresh fetch for this file. In the four tables that gained the column on 2026-11-24, a date appears only where the row or the citing document's Sources entry records one, and "not recorded" means neither does, which says nothing either way about whether the source was read; those rows are the first candidates for the next curation pass. Entries added on 2026-11-17 (the MCP Security Best Practices page, two CoSAI Workstream 4 papers, NIST AI 100-2 E2025 and its successor draft, and three model-vendor guidance pages) were each read at the publisher on that date. Cross-references to literature-review entries are not added yet. Document paths below drop the `analysis/` prefix, and a stub is written `stubs/<name>`.

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
- Cited by: surface-ownability, decision-sequence, build-buy-and-the-high-priest, configure-before-you-buy, inventory-and-shadow-ai, reading-vendor-claims, rent-or-own-sized-to-the-org, revalidation-and-pins, stubs/agent-builders, stubs/assistant-oversharing, stubs/rag-stores, models-you-hold, incumbent-tool-coverage, fine-tuned-model-is-a-data-store, frameworks-and-what-they-reach, ai-apis-and-the-gateway
- Last checked: 2026-11-10 (counts re-derived for surface-ownability; head re-checked 2026-11-09 for revalidation-and-pins)
- Notes: Apache-2.0. The component map describes a system its operator owns end to end, which is the gap `surface-ownability.md` fills for rented surfaces. Pinned by commit because the documents cite the YAML, not a tagged release. `incumbent-tool-coverage.md` grades fourteen tool categories against the 42 components in `components.yaml` at this commit, and `fine-tuned-model-is-a-data-store.md` notes that B is also defensible for an OASIS working draft.

### CoSAI AI Incident Response Framework V1.0

- Publisher: Coalition for Secure AI, Workstream 2
- Tier: A
- Pinned: document version `24fecc8c`, dated 27 October 2025, PDF read 2026-11-10
- URL: https://www.coalitionforsecureai.org/wp-content/uploads/2026/03/AI-Incident-Response-1.pdf (project: https://github.com/cosai-oasis/ws2-defenders)
- Cited by: stubs/ai-incident-response
- Last checked: 2026-11-10

### CoSAI Agentic Identity and Access Management

- Publisher: Coalition for Secure AI, Workstream 4 (Secure Design Patterns for Agentic Systems)
- Tier: A, on the same basis as the AI Incident Response Framework V1.0 above, an approved version 1.0 from an OASIS Open project
- Pinned: Version 1.0, 20 March 2026, PDF read 2026-11-17
- URL: https://www.coalitionforsecureai.org/wp-content/uploads/2026/04/agentic-identity-and-access-control.pdf
- Cited by: agent-identity-and-delegation
- Last checked: 2026-11-17
- Notes: cited for §5.1 (MCP servers, API gateways and service meshes SHOULD terminate and validate agent tokens and forward only scoped OBO credentials downstream, never raw upstream tokens; decisions MUST be recorded in immutable logs), §3.4 (scope SHOULD narrow at each hop and MUST NOT expand beyond the delegating principal's effective permissions) and principle 8, which extends the forwarding rule to agent-to-agent boundaries. The forwarding rule is a SHOULD.

### CoSAI Model Context Protocol (MCP) Security

- Publisher: Coalition for Secure AI, Workstream 4
- Tier: A, with a draft caveat, on the basis this file applies to NIST IR 8596's preliminary draft: the version cited was approved by the CoSAI Project Governing Board on 8 January 2026 but still prints "Status: Draft", so it is a reopen trigger rather than a basis for any practice on its own; B would also be defensible for a working draft (flagged for maintainer ruling)
- Pinned: version `7ec1306f2f55563f6eeef9d36a6bb2b531491ceb`, dated 8 January 2026, PDF read 2026-11-17
- URL: https://www.coalitionforsecureai.org/wp-content/uploads/2026/03/model-context-protocol-security-1.pdf
- Cited by: mcp-servers-and-manifest-drift
- Last checked: 2026-11-17
- Notes: cited for the MCP-T1 to MCP-T12 threat categories and section 3.2.2 (no token passthrough; RFC 8693 token exchange instead). It predates MCP revision 2026-07-28 (it describes stateful sessions and recommends Dynamic Client Registration), so the specification governs where the two differ.

### MITRE ATLAS

- Publisher: MITRE
- Tier: A (`decision-sequence.md` grades it B; see Tier disagreements)
- Pinned: v2026.10, released 2026-10-28; v2026.06 to v2026.10 data releases for the diff in revalidation-and-pins
- URL: https://atlas.mitre.org/ and https://github.com/mitre-atlas/atlas-data/releases
- Cited by: surface-ownability, decision-sequence, reading-vendor-claims, revalidation-and-pins, stubs/agent-builders, models-you-hold, telemetry-is-an-injection-surface, fine-tuned-model-is-a-data-store, frameworks-and-what-they-reach
- Last checked: 2026-11-10
- Notes: between v2026.06 and v2026.10, eight technique IDs left the STIX bundle with no revoked or deprecated flag, which is why the documents pin a release and the revalidation document treats each ATLAS release as a reopen trigger. The upstream issue on revocation markers is mitre-atlas/atlas-data#33 (opened 2026-11-02, state not re-checked).

### MITRE ATT&CK and MITRE D3FEND

- Publisher: MITRE
- Tier: A
- Pinned: ATT&CK Enterprise v20.1 (collection modified 2026-11-05, attack-stix-data commit `f59b03e`); D3FEND 1.6.0 (tag `91629ab`); frameworks-and-what-they-reach also reads D3FEND develop at `048c693`, including `extensions/nist/sp800-53r5-control-catalog-d3fend-mapping.xlsx`
- URL: https://github.com/mitre-attack/attack-stix-data and https://github.com/d3fend/d3fend-ontology
- Cited by: revalidation-and-pins, telemetry-is-an-injection-surface (ATT&CK T1698 and T1699), frameworks-and-what-they-reach
- Last checked: 2026-11-10 (2026-11-05 for revalidation-and-pins)

### OWASP Top 10 for LLM Applications 2026

- Publisher: OWASP GenAI Security Project
- Tier: A (`revalidation-and-pins.md` grades it B; see Tier disagreements)
- Pinned: 2026 edition, resource page dated 2026-08-03, PDF read 2026-11-10
- URL: https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/ (list page https://genai.owasp.org/llm-top-10/)
- Cited by: stubs/ai-you-ship, stubs/rag-stores, revalidation-and-pins, frameworks-and-what-they-reach, telemetry-is-an-injection-surface (see Notes)
- Last checked: 2026-11-10
- Notes: the entries are cited by their 2026 IDs (LLM01, LLM02, LLM06, LLM09, LLM10), which differ from the 2025 numbering; the routing key `owasp-ids-2025` flags internal controls that still cite the 2025 IDs. `telemetry-is-an-injection-surface.md` reads the prevention wording on the 2025 edition's LLM01 page (https://genai.owasp.org/llmrisk/llm01-prompt-injection/) and takes the 2026 LLM01 naming from a search excerpt of OWASP's Q3 2026 exploit roundup, which is a declared gap in that document.

### OWASP Top 10 for Agentic Applications for 2026

- Publisher: OWASP GenAI Security Project
- Tier: B as cited
- Pinned: release of 2025-12-09
- URL: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
- Cited by: revalidation-and-pins, frameworks-and-what-they-reach
- Last checked: 2026-11-09

### NIST AI Risk Management Framework 1.0 (NIST AI 100-1)

- Publisher: NIST
- Tier: A
- Pinned: AI RMF 1.0, January 2023
- URL: https://doi.org/10.6028/NIST.AI.100-1 (Govern subcategory text at https://airc.nist.gov/airmf-resources/airmf/5-sec-core/)
- Cited by: ai-use-policy-and-intake, saas-embedded-ai-and-vendor-terms (GOVERN 6), revalidation-and-pins, frameworks-and-what-they-reach
- Last checked: 2026-11-10

### NIST AI 600-1, Generative AI Profile

- Publisher: NIST
- Tier: A
- Pinned: July 2024
- URL: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf
- Cited by: stubs/ai-you-ship, frameworks-and-what-they-reach, revalidation-and-pins (pinned there since 2026-11-17)
- Last checked: 2026-11-17 (nist.gov landing page "Created July 26, 2024, Updated April 8, 2026"; PDF re-read)
- Notes: actions MS-2.7-007, MS-4.2-001, MG-3.1-004, MG-4.1-002 and MG-4.3-001 to -003; thin on output handling as a software-integration problem, so the stub reads OWASP first for that signal.

### Other NIST publications

| Source | Pinned | URL | Cited by | Last checked | Notes |
|---|---|---|---|---|---|
| NIST CSF 2.0 and its quick-start guides | CSF 2.0 | https://csrc.nist.gov/news/2026/two-new-csf-2-0-quick-start-guides | revalidation-and-pins | 2026-11-09 | |
| NIST IR 8596 | initial preliminary draft, 2025-12-16 | https://csrc.nist.gov/pubs/ir/8596/iprd | revalidation-and-pins, frameworks-and-what-they-reach (with its ATLAS-to-CSF bridge) | 2026-11-09 | a draft, so a reopen trigger rather than a basis for any practice |
| NIST Control Overlays for Securing AI Systems (renamed COSIS) | unpinned | https://csrc.nist.gov/projects/cosais | revalidation-and-pins, frameworks-and-what-they-reach | 2026-11-09 | |
| NIST AI 100-2 E2025, Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations | E2025, final 2025-03-24 (corrected PDF 2025-04-01) | https://csrc.nist.gov/pubs/ai/100/2/e2025/final | frameworks-and-what-they-reach, revalidation-and-pins | 2026-11-17 | a planning note of 2025-06-03 identifies an error on page x, with potential updates promised for a future update or revision |
| NIST SP 2400-102 E2026, Adversarial Machine Learning (initial public draft) | initial public draft, 2026-11-09, comments due 2026-12-18 | https://csrc.nist.gov/pubs/sp/2400-102/e2026/ipd | frameworks-and-what-they-reach, revalidation-and-pins | 2026-11-17 | the successor to AI 100-2 E2025 in draft, so a reopen trigger rather than a basis for any practice |
| NIST SP 800-53 Rev. 5, CM-8 System Component Inventory | Rev. 5 update 1 | https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final | build-buy-and-the-high-priest, frameworks-and-what-they-reach | 2026-11-10 | |
| NIST SP 800-61 Rev. 3 | April 2025 | https://csrc.nist.gov/pubs/sp/800/61/r3/final | stubs/ai-incident-response | 2026-11-10 | |
| Garfinkel, De-Identification of Personal Information, NIST IR 8053 | 2015, §3.2 | https://doi.org/10.6028/NIST.IR.8053 | prompt-capture-and-the-law, what-to-log-and-what-it-costs | 2026-11-09 | the unkeyed-hash enumeration example |
| NIST SP 800-53 Rev. 5, AU-9, AU-9(2), AU-9(3) and AU-10 | OSCAL catalog and baselines 5.2.0 | https://github.com/usnistgov/oscal-content | tamper-evident-record | 2026-11-10 | AU-9(2), AU-9(3) and AU-10 sit in the High baseline and none in Moderate at 5.2.0 |
| NIST SP 800-207, Zero Trust Architecture | 2020, §2.1 | https://doi.org/10.6028/NIST.SP.800-207 | agent-identity-and-delegation | 2026-11-09 | |
| NIST SP 800-63-4, Digital Identity Guidelines | 2025, §1.1 | https://doi.org/10.6028/NIST.SP.800-63-4 | agent-identity-and-delegation | 2026-11-09 | scoped to human users by its own §1.1 |

### ISO/IEC 42001

- Publisher: ISO and IEC
- Tier: A for the standard; the Annex A control numbers rest on secondary summaries and are B at best, and the EVS catalogue entry is C
- Pinned: ISO/IEC 42001:2023; the EN ISO/IEC 42001:2026 catalogue entry was read only to confirm the European adoption
- URL: https://www.iso.org/standard/42001 (EVS entry https://www.evs.ee/en/evs-en-iso-iec-42001-2026)
- Cited by: ai-use-policy-and-intake, saas-embedded-ai-and-vendor-terms, revalidation-and-pins, frameworks-and-what-they-reach (which grades the EVS entry C)
- Last checked: 2026-11-10
- Notes: paywalled, and iso.org returned 403 to the fetcher, so no document quotes the text. The Annex A summaries used (docs.modulos.ai and riskprofs.com, read 2026-11-10) disagree on some details. Listed under Unverified for that reason.

### OCSF schema

- Publisher: Open Cybersecurity Schema Framework project
- Tier: A (`decision-sequence.md` grades it B; see Tier disagreements)
- Pinned: 1.9.0 (2026-08-03); `message_context` object and `ai_operation` profile; main read at `d1cbd61` (1.10.0-dev) for landing-ai-events-in-ocsf and at `6461440` for mcp-servers-and-manifest-drift
- URL: https://schema.ocsf.io/ and https://github.com/ocsf/ocsf-schema
- Cited by: telemetry-by-surface, what-to-log-and-what-it-costs, decision-sequence, reading-vendor-claims, revalidation-and-pins, build-buy-and-the-high-priest (pin), models-you-hold (`ai_model`), landing-ai-events-in-ocsf, telemetry-is-an-injection-surface (`metadata`), tamper-evident-record (`record_integrity`), incumbent-tool-coverage, frameworks-and-what-they-reach, mcp-servers-and-manifest-drift (`ai_capability` on main), agent-identity-and-delegation (`delegation`), ai-apis-and-the-gateway
- Last checked: 2026-11-09
- Notes: issue #1754 read 2026-11-09 for revalidation-and-pins; pull request #1754, the draft AI Agent Activity event class, read at `08d6f53` on 2026-11-10 (open and draft, so Tier B in landing-ai-events-in-ocsf), and merge dates of pull requests #1488, #1641, #1665, #1674, #1704 and #1729 read the same day. The `record_integrity` profile and its objects came in with pull requests #1661 and #1662 (CHANGELOG at v1.9.0).

### Model Context Protocol specification

- Publisher: Model Context Protocol project
- Tier: A (`decision-sequence.md` grades it B; see Tier disagreements)
- Pinned: revision 2026-07-28
- URL: https://modelcontextprotocol.io/specification/2026-07-28
- Cited by: decision-sequence, revalidation-and-pins, mcp-servers-and-manifest-drift (changelog, Authorization, Deprecated features, Security Best Practices), landing-ai-events-in-ocsf (changelog), ai-apis-and-the-gateway (changelog, Authorization), agent-identity-and-delegation (Security Best Practices, Token Passthrough)
- Last checked: 2026-11-17 (Security Best Practices and the Authorization page's Dynamic Client Registration note; landing-ai-events-in-ocsf 2026-11-10; the others 2026-11-09)
- Notes: the Security Best Practices page for revision 2026-07-28 (https://modelcontextprotocol.io/specification/2026-07-28/basic/security_best_practices, which redirects to the `docs/2026-07-28/tutorials/security/` path) has eleven attack and mitigation sections, three of them new over 2025-11-25, and replaces Session Hijacking with State Handle Hijacking because the revision has no protocol-level sessions.

### CISA Known Exploited Vulnerabilities catalog

- Publisher: CISA
- Tier: A (`decision-sequence.md` and `build-buy-and-the-high-priest.md` grade it B; see Tier disagreements)
- Pinned: `kev.json` catalogVersion 2026.11.09 (1,773 entries), released 2026-11-09T19:54Z
- URL: https://www.cisa.gov/known-exploited-vulnerabilities-catalog
- Cited by: revalidation-and-pins, decision-sequence, build-buy-and-the-high-priest, stubs/agent-builders, stubs/ai-incident-response, models-you-hold, ai-apis-and-the-gateway
- Last checked: 2026-11-10
- Notes: the count of 2026 AI orchestration and serving entries (BerriAI LiteLLM, MLflow, Ray, Langflow, n8n; none for vLLM or Ollama) is the documents' own derivation from the catalogue and is carried as a `measurement-claims` row in revalidation-and-pins.

### OASIS CACAO Security Playbooks 2.0

- Publisher: OASIS
- Tier: A
- Pinned: Version 2.0
- URL: https://docs.oasis-open.org/cacao/security-playbooks/v2.0/security-playbooks-v2.0.html
- Cited by: stubs/ai-incident-response
- Last checked: 2026-11-10

### IETF, OWASP API and vulnerability records

| Source | Pinned | URL | Cited by | Last checked | Notes |
|---|---|---|---|---|---|
| IETF RFC 8693, OAuth 2.0 Token Exchange | 2020, §4.1 and §5 | https://www.rfc-editor.org/rfc/rfc8693 | agent-identity-and-delegation | 2026-11-09 | the `act` claim |
| IETF RFC 9700, Best Current Practice for OAuth 2.0 Security | 2025, §2.3 and §4.10.1 | https://www.rfc-editor.org/rfc/rfc9700 | agent-identity-and-delegation | 2026-11-09 | |
| IETF RFC 8785, JSON Canonicalization Scheme | June 2020 | https://www.rfc-editor.org/rfc/rfc8785 | tamper-evident-record | 2026-11-10 | Informational, independent stream |
| IETF RFC 9162, Certificate Transparency Version 2.0 | December 2021 | https://www.rfc-editor.org/rfc/rfc9162 | tamper-evident-record | 2026-11-10 | Experimental |
| OWASP API Security Top 10 2023 | 2023 edition | https://api-security.owasp.org/editions/2023/en/0x11-t10 | ai-apis-and-the-gateway | 2026-11-09 | the mapping onto gateway review is Tier D in the document |
| NVD records for CVE-2025-32434, CVE-2025-1716, CVE-2025-10155, CVE-2024-3660, CVE-2024-34359, CVE-2026-7482 and CVE-2026-22778 | as read | https://nvd.nist.gov/vuln/detail/<CVE-ID> | models-you-hold | 2026-11-10 | |
| CVE-2025-32711 record | published 2025-06-11 | https://www.cve.org/CVERecord?id=CVE-2025-32711 | incumbent-tool-coverage | 2026-11-09 | B as cited |

### Specifications and overlays graded B as cited

| Source | Publisher | Pinned | URL | Cited by | Last checked | Notes |
|---|---|---|---|---|---|---|
| Sigma specification | SigmaHQ | 2.0.0 | https://github.com/SigmaHQ/sigma-specification | build-buy-and-the-high-priest | 2026-11-10 | |
| OpenTelemetry semantic conventions for generative AI | OpenTelemetry | registry v1.45.0 | https://github.com/open-telemetry/semantic-conventions | telemetry-by-surface, landing-ai-events-in-ocsf (GenAI and MCP registries at `e6658f1`, as pinned by lab run R2) | 2026-11-09 | attributes at development stability on the read date |
| CSA AI Controls Matrix | Cloud Security Alliance | v1.1 (2026-06-22) | https://cloudsecurityalliance.org/artifacts/ai-controls-matrix-v1-1 | revalidation-and-pins, frameworks-and-what-they-reach (licence facts only, from CSA's CCM and AICM Licensing FAQ dated 2026-03-13) | 2026-11-09 | link-out only, because its licence allows internal reference and no derivatives |
| AIUC-1 | AIUC | release of 2026-10-15 | https://standard.aiuc-1.com/changelog/ | revalidation-and-pins, frameworks-and-what-they-reach (licence facts only) | 2026-11-09 | link-out only (all rights reserved) |
| Google Secure AI Framework (components; Focus on Agents) | Google | no version on the page, fetched 2026-11-09 | https://saif.google/secure-ai-framework/components and https://saif.google/focus-on-agents | surface-ownability | 2026-11-09 | vendor-published framework, so B and not A |
| OWASP Agent Observability Standard, "Trace with OCSF" | OWASP | commit `9a9bc37`, as pinned by lab run R2 | https://aos.owasp.org/spec/trace/extend_ocsf | landing-ai-events-in-ocsf | 2026-11-10 | an OCSF mapping that puts most agent facts in `unmapped` |
| Secure Controls Framework terms and conditions | Secure Controls Framework | read 2026-11-09 | https://securecontrolsframework.com/terms-and-conditions | frameworks-and-what-they-reach | 2026-11-09 | licence facts only |

## Statute, regulation and court text (Tier A)

This is not legal advice; these dossiers record what was read, not what it means for any organization.

| Source | Pinned | URL | Cited by | Last checked | Notes |
|---|---|---|---|---|---|
| GDPR, Regulation (EU) 2016/679 | consolidated text, CELEX 32016R0679 | https://eur-lex.europa.eu/eli/reg/2016/679/oj | prompt-capture-and-the-law, what-to-log-and-what-it-costs, saas-embedded-ai-and-vendor-terms, fine-tuned-model-is-a-data-store (Art. 17) | 2026-11-09 | Recital 49 and Arts. 5, 6, 9, 17, 28, 32, 35, 88 |
| AI Act, Regulation (EU) 2024/1689 as amended by (EU) 2026/1744 | consolidated CELEX 02024R1689-20260727; the amending act is CELEX 32026R1744 (OJ L, 2026/1744, 24.7.2026) | https://eur-lex.europa.eu/eli/reg/2024/1689/oj; amending act and consolidated text read at https://publications.europa.eu/resource/celex/32026R1744 and https://publications.europa.eu/resource/celex/02024R1689-20260727 | prompt-capture-and-the-law, decision-sequence, revalidation-and-pins, build-buy-and-the-high-priest, stubs/ai-you-ship, frameworks-and-what-they-reach | 2026-11-24 | Art. 111(4): providers of generative systems on the market before 2 August 2026 comply with Art. 50(2) by 2 December 2026. Art. 113, third paragraph, point (c): Chapter III Sections 1 to 3 apply from 2 December 2027 for Annex III systems and 2 August 2028 for Annex I systems. Point (a): the new Art. 5(1) points (ba) and (bb) apply from 2 December 2026. EUR-Lex returns an empty page to the fetcher, so the read is through the Publications Office, which serves the same Official Journal text |
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
| NSA and CISA, AA23-278A, top ten misconfigurations | B | 2023-10-05 | https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-278a | configure-before-you-buy | 2026-11-24 | read at cisa.gov on 2026-11-24; the 2026-11-10 pass could not fetch the page and had a second model's confirmation only |
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
- Pinned: master at `91e44df` (2026-11-10), which carries every run below; the research branch `hub/ai-research-2026-11-09` merged there, and each document's `measurement-claims` rows cite `sdw-lab-benchmarks@91e44df <folder>/RESULTS.md:<lines>`
- URL: https://github.com/flying-coyote/sdw-lab-benchmarks
- Cited by: the runs below
- Last checked: 2026-11-10
- Notes: every run cited here is linked to its RESULTS and VERIFICATION files by commit hash, never copied (Decision 10). The November 2026 runs carry a VERIFIED-WITH-FIXES verdict in their VERIFICATION files (M1 as a partial run), `ai-analyst-preregs` is a verified pre-registration that has not run, and the June 2026 folders hold no VERIFICATION file at `91e44df`, which the citing documents state where they use them.

| Run folder | What it measured | Cited by | Pin as the document cites it |
|---|---|---|---|
| `t1-shadow-ai-discovery` | five discovery methods against nine planted shadow-AI surfaces on one endpoint | inventory-and-shadow-ai | `91e44df` |
| `t2-platform-telemetry` | Claude Code 2.1.321 OpenTelemetry fields at defaults and with content gates on; Ollama 0.20.6 server log | telemetry-by-surface, what-to-log-and-what-it-costs | `91e44df` |
| `t8a-mcp-before-after` | MCP Python SDK 1.30.0 to 2.3.0 and protocol revision 2025-11-25 to 2026-07-28 on one fixture server | revalidation-and-pins, mcp-servers-and-manifest-drift, landing-ai-events-in-ocsf | `91e44df` |
| `t9-pretooluse-hook-enforcement` | Claude Code hook and deny-rule enforcement across settings sources and precedence pairs | coding-agent-hooks-and-policy, tamper-evident-record | `91e44df` (the commit that applies the verifier's seven fixes) |
| `atlas-ocsf-observables` | ATLAS techniques with mapped OCSF fields, detection outcome per technique across three seeds | reading-vendor-claims, telemetry-is-an-injection-surface, frameworks-and-what-they-reach (R1) | `91e44df` |
| `ai-artifact-sbom` | four SBOM tools against six AI artifacts on one host | reading-vendor-claims, models-you-hold, incumbent-tool-coverage (R4) | `91e44df` |
| `mcp-manifest-drift` | snapshot-and-diff detection over three real MCP servers | reading-vendor-claims, mcp-servers-and-manifest-drift, tamper-evident-record (R5) | `91e44df` |
| `agent-toolcall-schemas` | one MCP tools/call typed in OCSF, OpenTelemetry and OWASP AOS | reading-vendor-claims, what-to-log-and-what-it-costs, ai-apis-and-the-gateway, mcp-servers-and-manifest-drift, landing-ai-events-in-ocsf (R2) | `91e44df` |
| `t7-idp-delegation-logging` | Keycloak 26.8.1 token-exchange and delegation-preview events, tokens and admin records, mapped to OCSF 1.9.0 | agent-identity-and-delegation | `91e44df` |
| `delegation-chain-query` | recursive walk, one-join and materialized checks for scope escalation across delegation chains (R7) | agent-identity-and-delegation, incumbent-tool-coverage | `91e44df` |
| `agent-telemetry-retention` | storage footprint and cost per capture tier (R6) | what-to-log-and-what-it-costs, ai-apis-and-the-gateway | `91e44df` |
| `t5-model-artifact-scanning` | modelscan 0.8.8, picklescan 1.0.5 and fickling 0.1.12 on picklescan's bypass set and 18 benign files, including renames (T5) | models-you-hold | `91e44df` |
| `d3fend-ocsf-ai-alignment` | D3FEND AI artifact nouns against OCSF `ai_*` objects, a desk analysis of pinned definitions rather than a measurement (R8) | models-you-hold, landing-ai-events-in-ocsf, incumbent-tool-coverage, fine-tuned-model-is-a-data-store | `91e44df` |
| `t8b-telemetry-injection` | a planted instruction in adversary-controlled fields of an OCSF-shaped DuckDB store, visible and as tag characters, read by two local models under several renderings (T8b) | telemetry-is-an-injection-surface | `91e44df` |
| `t6-finetune-memorization` | planted-canary memorization in a LoRA fine-tune by insertion count and decoding setting (T6) | fine-tuned-model-is-a-data-store, rent-or-own-sized-to-the-org | `91e44df` |
| `t3-guardrail-adaptive` | three open prompt-injection and jailbreak classifiers on public attack and benign sets under seven published input transforms, with Wilson and paired-bootstrap intervals (T3) | reading-vendor-claims | `91e44df` |
| `m1-r1-blind-regrade` | a blind re-grade of R1's artifact-to-OCSF grades by one model, partial (M1) | frameworks-and-what-they-reach | `91e44df` |
| `t4-interdiction` | how many mapped incident steps the top burn-down controls catch (T4) | frameworks-and-what-they-reach | `91e44df` |
| `t8c-trifecta-detection` | thirteen detection rules over planted agent exfiltration chains and benign lookalikes in a synthetic OCSF 1.9.0 store (T8c) | evaluating-ai-in-the-soc | `91e44df` |
| `ai-analyst-preregs` | pre-registrations R3 and R11 for AI-analyst evaluation, frozen 2026-11-09 and not run | evaluating-ai-in-the-soc | `91e44df` |
| `BENCHMARKING-METHODOLOGY.md` section 10 | the lab's method for LLM arms (lines 157 to 203) | evaluating-ai-in-the-soc | `91e44df` |
| `ocsf-attack-coverage`, `ocsf-airgap-agent` | earlier OCSF coverage and air-gapped agent runs | evaluating-ai-in-the-soc | `91e44df` |
| `ocsf-deterministic-mapper`, `ocsf-mapping-oracle` | June 2026 mapping runs against OCSF 1.8.0 | landing-ai-events-in-ocsf | `91e44df` |
| `ocsf-parquet-determinism`, `parquet-checksum-integrity`, `parquet-determinism-encryption`, `spec-vs-emitted-integrity` | June 2026 Parquet reproducibility, checksum, encryption and spec-versus-emitted runs (the last Tier B/C, replayed from published vendor specs) | tamper-evident-record | `91e44df` |

### atlas-d3fend-crosswalk

- Publisher: the author's public crosswalk repository
- Tier: B (own derivation over Tier A MITRE data)
- Pinned: commit `66b7726`, `VERSION-DIFF-2026-11.md` and `scripts/01_diff_atlas_releases.py`; frameworks-and-what-they-reach cites `65cdab0` (README, crosswalk CSVs and `VERSION-DIFF-2026-11.md`), with upstream coordination at d3fend/d3fend-ontology#606
- URL: https://github.com/flying-coyote/atlas-d3fend-crosswalk
- Cited by: revalidation-and-pins, frameworks-and-what-they-reach
- Last checked: 2026-11-10 (2026-11-02 for revalidation-and-pins)

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
| [un]prompted II, San Francisco, 2026-10-27 to 2026-10-29, agenda at https://unpromptedcon.org/agenda-10-2026/ | Kovalsky and Arshad, "Your AI Analyst Is Confidently Wrong"; Dye, "Engineering Context for SOC Agents"; Bello, "Building Security Review Agents: the Models are the Reliable Part" | evaluating-ai-in-the-soc | 2026-11-10 | the two vendor talks the lab methodology carries are Tier C, in the vendor-claims table |

## Peer-reviewed research (Tier A)

| Source | Venue | Identifier | Cited by | Last checked | Notes |
|---|---|---|---|---|---|
| Nasr, Carlini et al., "The Attacker Moves Second" | USENIX Security 2026 | arXiv 2510.09023 | reading-vendor-claims, decision-sequence, build-buy-and-the-high-priest, telemetry-is-an-injection-surface | not recorded | figures from arXiv v1 (§5.3, Table 7, App. G.1); authors affiliated with model vendors, flagged in decision-sequence |
| Mireshghallah et al., "Trust No Bot" | COLM 2024 | arXiv 2407.11438 | inventory-and-shadow-ai, prompt-capture-and-the-law, telemetry-by-surface | not recorded | |
| Zhan, Fang, Panchal and Kang, adaptive attacks on indirect prompt injection defences | Findings of NAACL 2025 | doi:10.18653/v1/2025.findings-naacl.395 | coding-agent-hooks-and-policy, reading-vendor-claims, telemetry-is-an-injection-surface | not recorded | |
| Debenedetti et al., "Defeating Prompt Injections by Design" (CaMeL) | IEEE SaTML 2026 | doi:10.1109/satml68715.2026.00040 | coding-agent-hooks-and-policy | not recorded | |
| Debenedetti et al., "AgentDojo" | NeurIPS 2024 | doi:10.52202/079017-2636 | reading-vendor-claims, telemetry-is-an-injection-surface (arXiv 2406.13352 v3) | not recorded | |
| Hackett, Birch, Trawicki, Suri and Garraghan, "Bypassing LLM Guardrails" | LLMSec 2025 | ACL Anthology 2025.llmsec-1.8 | reading-vendor-claims, telemetry-is-an-injection-surface | not recorded | vendor flag in the document |
| Abdelnabi et al., "LLMail-Inject" | Findings of EMNLP 2026 | 10.18653/2026.findings-emnlp.514 | reading-vendor-claims, what-to-log-and-what-it-costs, telemetry-is-an-injection-surface | not recorded | Microsoft-led, and the classifier defences tested are Microsoft's, flagged |
| Shire and Kim, "PIDS-Bench" | IEEE Access 2026 | doi:10.1109/access.2026.3728186 | reading-vendor-claims, what-to-log-and-what-it-costs | not recorded | |
| Turpin, Michael, Perez and Bowman, "Language Models Don't Always Say What They Think" | NeurIPS 2023 | 10.52202/075280-3275 | what-to-log-and-what-it-costs | not recorded | |
| Greshake, Abdelnabi, Mishra, Endres, Holz and Fritz, indirect prompt injection | ACM AISec 2023 | doi:10.1145/3605764.3623985 | stubs/rag-stores, telemetry-is-an-injection-surface | not recorded | |
| Gruber and Hilgert, forensic analysis of OpenClaw | Digital Threats: Research and Practice 2026 | doi:10.1145/3848419 | telemetry-by-surface | not recorded | |
| Ravid et al., electronic monitoring meta-analysis | Personnel Psychology 2022 | 10.1111/peps.12514 | prompt-capture-and-the-law | not recorded | studies predate generative-AI assistants |
| Mollaeefar et al., "Chatbot Confessions" | PoPETs 2026(3) | 10.56553/popets-2026-0081 | prompt-capture-and-the-law, what-to-log-and-what-it-costs | not recorded | |
| Aghili, Li and Khomh, privacy in software logs | FSE 2025 | 10.1145/3715779 | prompt-capture-and-the-law, what-to-log-and-what-it-costs | not recorded | |
| Pilán et al., text anonymization | Computational Linguistics 2022 | 10.1162/coli_a_00458 | prompt-capture-and-the-law | not recorded | |
| Humlum and Vestergaard | PNAS 2024 | doi:10.1073/pnas.2414972121 | inventory-and-shadow-ai | not recorded | |
| Carlini, Tramèr, Wallace et al., "Extracting Training Data from Large Language Models" | USENIX Security 2021 | usenix.org | rent-or-own-sized-to-the-org, fine-tuned-model-is-a-data-store (doi:10.48550/arxiv.2012.07805) | not recorded | |
| Qi, Zeng, Xie et al., fine-tuning compromises safety | ICLR 2024 | arXiv 2310.03693 | rent-or-own-sized-to-the-org, fine-tuned-model-is-a-data-store | not recorded | |
| Goldwasser, Kim, Vaikuntanathan and Zamir, undetectable backdoors | FOCS 2022 | arXiv 2204.06974 | rent-or-own-sized-to-the-org, models-you-hold (doi:10.1109/focs54457.2022.00092) | not recorded | |
| Sculley et al., "Hidden Technical Debt in Machine Learning Systems" | NeurIPS 2015 | proceedings.neurips.cc | build-buy-and-the-high-priest | not recorded | |
| Avelino, Passos, Hora and Valente, truck factors | ICPC 2016 | doi:10.1109/ICPC.2016.7503718 | build-buy-and-the-high-priest | not recorded | |
| Avelino, Constantinou, Valente and Serebrenik, abandonment and survival of open source projects | ESEM 2019 | doi:10.1109/ESEM.2019.8870181 | build-buy-and-the-high-priest | not recorded | the 86 percent figure read in the RQ2 answer of the arXiv full text (1906.08058) on 2026-11-24 |
| Coelho and Valente, "Why Modern Open Source Projects Fail" | ESEC/FSE 2017 | doi:10.1145/3106237.3106246 | build-buy-and-the-high-priest | not recorded | |
| MacCormack, Baldwin and Rusnak, the mirroring hypothesis | Research Policy 41(8), 2012 | doi:10.1016/j.respol.2012.04.011 | build-buy-and-the-high-priest | not recorded | read at abstract level |
| Farrell and Klemperer, switching costs and network effects | Handbook of Industrial Organization vol. 3, 2007 | doi:10.1016/S1573-448X(06)03031-7 | build-buy-and-the-high-priest | not recorded | |
| Yin et al., configuration errors | SOSP 2011 | doi:10.1145/2043556.2043572 | configure-before-you-buy | not recorded | parameter-mistake range from the authors' slides |
| Liu, Zhou, Zhang et al., software misconfigurations | Empirical Software Engineering 2026 | doi:10.1007/s10664-026-10892-6 | configure-before-you-buy | not recorded | read in full (arXiv 2412.11121v4) |
| Dietrich, Krombholz, Borgolte and Fiebig, operators and misconfigurations | CCS 2018 | doi:10.1145/3243734.3243794 | configure-before-you-buy | not recorded | |
| Xu, Zhang, Huang et al., "Do Not Blame Users for Misconfigurations" | SOSP 2013 | doi:10.1145/2517349.2522727 | configure-before-you-buy | not recorded | abstract only |
| Alahmadi, Axon and Martinovic, "99% False Positives" | USENIX Security 2022 | usenix.org | configure-before-you-buy | not recorded | |
| Uetz et al., evasions of SIEM rules | USENIX Security 2024 | arXiv 2311.10197 | configure-before-you-buy | not recorded | |
| Wool, firewall configuration errors | IEEE Internet Computing 2010 | doi:10.1109/mic.2010.29 | configure-before-you-buy | not recorded | |
| Weichselbaum et al., "CSP Is Dead, Long Live CSP!" | CCS 2016 | doi:10.1145/2976749.2978363 | configure-before-you-buy | not recorded | |
| Álvarez, Nuño, Bulnes et al., network misconfigurations in Spanish organisations | Computer Networks 2026 | doi:10.1016/j.comnet.2026.112631 | configure-before-you-buy | not recorded | abstract only |
| Rahman et al., security smells in Ansible and Chef; Kubernetes manifests | ACM TOSEM 2021 and 2023 | doi:10.1145/3408897; doi:10.1145/3579639 | configure-before-you-buy | not recorded | |
| Boucher et al., "Bad Characters: Imperceptible NLP Attacks" | IEEE S&P 2022 | doi:10.1109/sp46214.2022.9833641 | telemetry-is-an-injection-surface | not recorded | |
| Narendra and Chatterjee, "Why Prompt-Injection Detectors Fail on XPIA" | Findings of EMNLP 2026 | doi:10.18653/2026.findings-emnlp.1103 | telemetry-is-an-injection-surface | not recorded | abstract read |
| Gu, Liu, Dolan-Gavitt and Garg, "BadNets" | IEEE Access 2019 | doi:10.1109/access.2019.2909068 | models-you-hold | not recorded | |
| Kurita, Michel and Neubig, "Weight Poisoning Attacks on Pretrained Models" | ACL 2020 | doi:10.18653/v1/2020.acl-main.249 | models-you-hold | not recorded | |
| Schneier and Kelsey, "Secure audit logs to support computer forensics" | ACM TISSEC 2(2), 1999 | doi:10.1145/317087.317089 | tamper-evident-record | not recorded | abstract |
| Crosby and Wallach, "Efficient Data Structures for Tamper-Evident Logging" | USENIX Security 2009 | usenix.org | tamper-evident-record | not recorded | |
| Carlini et al., "The Secret Sharer" | USENIX Security 2019 | arXiv 1802.08232 | fine-tuned-model-is-a-data-store | not recorded | |
| Carlini et al., "Quantifying Memorization Across Neural Language Models" | ICLR 2023 | doi:10.48550/arxiv.2202.07646 | fine-tuned-model-is-a-data-store | not recorded | |
| Nasr, Rando, Carlini et al., "Scalable Extraction of Training Data from Aligned, Production Language Models" | ICLR 2025 | OpenReview vjel3nWP2a | fine-tuned-model-is-a-data-store | not recorded | the 150x figure is in arXiv 2311.17035 only |
| Mireshghallah et al., memorization in fine-tuned autoregressive language models | EMNLP 2022 | doi:10.18653/v1/2022.emnlp-main.119 | fine-tuned-model-is-a-data-store | not recorded | |
| Zeng et al., "Exploring Memorization in Fine-tuned Language Models" | ACL 2024 | doi:10.18653/v1/2024.acl-long.216 | fine-tuned-model-is-a-data-store | not recorded | |
| Szep et al., unintended memorization in fine-tuned language models | EACL 2026 | doi:10.18653/v1/2026.eacl-long.304 | fine-tuned-model-is-a-data-store | not recorded | |
| Kapelinski and Kreutz, memorization reduction in privacy-preserving fine-tuning of SLMs for CSIRTs | BRACIS 2026 | doi:10.1007/978-3-032-39898-7_43 | fine-tuned-model-is-a-data-store | not recorded | lightly cited so far |
| Lee et al., "Deduplicating Training Data Makes Language Models Better" | ACL 2022 | doi:10.18653/v1/2022.acl-long.577 | fine-tuned-model-is-a-data-store | not recorded | |
| Kandpal, Wallace and Raffel, deduplication mitigates privacy risks | ICML 2022 | arXiv 2202.06539 | fine-tuned-model-is-a-data-store | not recorded | |
| Duan et al., "Do Membership Inference Attacks Work on Large Language Models?" | COLM 2024 | arXiv 2402.07841 | fine-tuned-model-is-a-data-store | not recorded | |
| Hayes et al., strong membership inference on large language models | NeurIPS 2025 | arXiv 2505.18773 | fine-tuned-model-is-a-data-store | not recorded | |
| Fu et al., membership inference against fine-tuned LLMs via self-prompt calibration | NeurIPS 2024 | doi:10.52202/079017-4290 | fine-tuned-model-is-a-data-store | not recorded | |
| Kandpal et al., "User Inference Attacks on Large Language Models" | EMNLP 2024 | doi:10.18653/v1/2024.emnlp-main.1014 | fine-tuned-model-is-a-data-store | not recorded | |
| Puerto et al., "Scaling Up Membership Inference" | Findings of NAACL 2025 | doi:10.18653/v1/2025.findings-naacl.234 | fine-tuned-model-is-a-data-store | not recorded | |
| Ippolito et al., preventing verbatim memorization gives a false sense of privacy | INLG 2023 | doi:10.18653/v1/2023.inlg-main.3 | fine-tuned-model-is-a-data-store | not recorded | |
| Lukas et al., PII leakage in language models | IEEE S&P 2023 | doi:10.1109/sp46215.2023.10179300 | fine-tuned-model-is-a-data-store | not recorded | |
| Yu et al., "Differentially Private Fine-tuning of Language Models" | Journal of Privacy and Confidentiality 2024 | doi:10.29012/jpc.880 | fine-tuned-model-is-a-data-store | not recorded | |
| Chen et al., "The Janus Interface" | ACM CCS 2024 | doi:10.1145/3658644.3690325 | fine-tuned-model-is-a-data-store | not recorded | |
| Betley et al., "Emergent Misalignment" | ICML 2025 | arXiv 2502.17424 | fine-tuned-model-is-a-data-store | not recorded | |
| Hou, Zhao, Wang and Wang, MCP landscape, threats and research directions | ACM TOSEM 2026 | doi:10.1145/3796519 | mcp-servers-and-manifest-drift | not recorded | abstract |
| Hasan, Li, Fallahzadeh, Rajbahadur, Adams and Hassan, "MCP at First Glance" | ACM TOSEM 2026 | doi:10.1145/3814959 | mcp-servers-and-manifest-drift | not recorded | full text, arXiv 2506.13538v5 |
| Song et al., "Beyond the Protocol" | IEEE TSE 2026 | doi:10.1109/tse.2026.3694876 | mcp-servers-and-manifest-drift | not recorded | abstract |
| Zhao et al., "Parasites in the Toolchain" | IEEE S&P 2026 | doi:10.1109/sp63933.2026.00154 | mcp-servers-and-manifest-drift | not recorded | |
| Bhatt, Narajala and Habler, "ETDI" | CARS 2025 | doi:10.1109/cars67163.2025.11337310 | mcp-servers-and-manifest-drift | not recorded | abstract; a design proposal, authors affiliated with OWASP Foundation and Intuit |
| Meli, McNiece and Reaves, "How Bad Can It Git?" | NDSS 2019 | doi:10.14722/ndss.2019.23418 | agent-identity-and-delegation | not recorded | |
| Birgisson et al., "Macaroons" | NDSS 2014 | doi:10.14722/ndss.2014.23212 | agent-identity-and-delegation | not recorded | largely Google-authored |
| Philippaerts, Preuveneers and Joosen, "OAuch" | RAID 2022 | doi:10.1145/3545948.3545955 | agent-identity-and-delegation | not recorded | |
| Chan et al., "Visibility into AI Agents" | ACM FAccT 2024 | doi:10.1145/3630106.3658948 | agent-identity-and-delegation | not recorded | |
| Yang et al., over-privileged tool selection in LLM agents | Findings of EMNLP 2026 | doi:10.18653/2026.findings-emnlp.2059 | agent-identity-and-delegation | not recorded | |

## Preprints and working papers (Tier B)

| Source | Identifier | Cited by | Last checked | Notes |
|---|---|---|---|---|
| Chhetri, Tariq, Aamir, Grobler et al., "From Frontier to Shadow AI" (CSIRO) | arXiv 2606.00088 | ai-use-policy-and-intake, inventory-and-shadow-ai, saas-embedded-ai-and-vendor-terms | not recorded | interview study of 27 Australian critical-infrastructure organisations; preprint under review |
| METR, early-2025 AI and experienced open-source developer productivity | arXiv 2507.09089 | build-buy-and-the-high-priest | not recorded | |
| Bick, Blandin and Deming | NBER w32966 | inventory-and-shadow-ai | not recorded | |
| Shi et al., Progent | arXiv 2504.11703 | coding-agent-hooks-and-policy | not recorded | |
| Beurer-Kellner et al., design patterns for securing LLM agents | arXiv 2506.08837 | coding-agent-hooks-and-policy | not recorded | |
| Sharma et al., Ajar | arXiv 2609.26900 | coding-agent-hooks-and-policy, mcp-servers-and-manifest-drift (Table 6) | not recorded | |
| Davidovich et al., Permission Denied | arXiv 2608.02670 | coding-agent-hooks-and-policy | not recorded | |
| Yan, security rules in CLAUDE.md versus built-in controls | arXiv 2608.23550 | coding-agent-hooks-and-policy | not recorded | |
| Zhu and Pu, "TelemetrySuffBench" | arXiv 2608.07899 | telemetry-by-surface, what-to-log-and-what-it-costs | not recorded | |
| Muhamed and Smith, "MOLE" | arXiv 2609.06966 | what-to-log-and-what-it-costs, prompt-capture-and-the-law | not recorded | synthetic setting |
| Liu (Zhuowen), "Passing the Test You Trained On", prompt-injection detectors re-evaluated | arXiv 2610.03448 | telemetry-is-an-injection-surface | not recorded | |
| Wang and Li, "Leaner Training, Lower Leakage" | arXiv 2506.20856 | fine-tuned-model-is-a-data-store | not recorded | |
| Tan, Du and Feng, "How Much Can a LoRA Adapter Memorize?" | arXiv 2607.21351 | fine-tuned-model-is-a-data-store | not recorded | |
| Ran et al., "LoRA-Leak" | arXiv 2507.18302 | fine-tuned-model-is-a-data-store | not recorded | |
| LoRATK and PETA | arXiv 2403.00108; arXiv 2310.00648 | fine-tuned-model-is-a-data-store | not recorded | cited through CoSAI `riskAdapterPEFTInjection` |
| Barnes, "OpenSec" | arXiv 2601.21083 v3 (2026-02-06) | evaluating-ai-in-the-soc | 2026-11-10 | abstract read; listed under Unverified for the body |
| Wang et al., "MCPTox" | arXiv 2508.14925 | mcp-servers-and-manifest-drift | not recorded | |
| Yeboah-Duako and Datta, "Permissions on the Loose" | arXiv 2607.02875 | agent-identity-and-delegation | not recorded | |
| Nian et al., "Auditable Agents" | arXiv 2604.05485 | agent-identity-and-delegation | not recorded | |
| Prakash, "AIP: Agent Identity Protocol" | arXiv 2603.24775 | agent-identity-and-delegation | not recorded | |

## Practitioner and historical sources

| Source | Tier | Cited by | Last checked | Notes |
|---|---|---|---|---|
| Beyer, Jones, Petoff and Murphy (eds.), Site Reliability Engineering, ch. 1 (2016), https://sre.google/sre-book/introduction/ | B | build-buy-and-the-high-priest | not recorded | |
| David P. Reed, "That Sneaky Exponential" (1999), https://www.deepplum.com/gfn/reedslaw.html | B | build-buy-and-the-high-priest | not recorded | |
| Briscoe, Odlyzko and Tilly, "Metcalfe's Law Is Wrong", IEEE Spectrum, July 2006 | B | build-buy-and-the-high-priest | not recorded | |
| Melvin E. Conway, "How Do Committees Invent?", Datamation 14(4), 1968 | C | build-buy-and-the-high-priest | not recorded | trade magazine |
| Maintenance-share figures attributed to Lientz and Swanson 1980 and Erlikh 2000 | C | build-buy-and-the-high-priest | not recorded | secondary compilations only; direction used, no figure; listed under Unverified |
| Permiso, "Exploiting hosted models" (2024-10-03) | B | what-to-log-and-what-it-costs | not recorded | practitioner incident write-up |
| Invariant Labs, GitHub MCP vulnerability (2025-05-26) | B | what-to-log-and-what-it-costs | not recorded | vendor research with a product to sell, flagged |
| Wiz, "s1ngularity's aftermath" (2025-09-03) | B | what-to-log-and-what-it-costs | not recorded | vendor research, flagged |
| Anthropic, "Disrupting the first reported AI-orchestrated cyber espionage campaign" (November 2025) | B | what-to-log-and-what-it-costs | not recorded | the vendor describing its own detection, flagged |
| AI Incident Database report 5593 (Replit agent, July 2025), https://incidentdatabase.ai/reports/5593/ | C | stubs/ai-incident-response | not recorded | the agent's own statements were the only account of why |
| Tziakouris and Biasiotto, "Detecting Exposed LLM Servers: Shodan Case Study on Ollama", Cisco blog, 2025-09-01 | B | models-you-hold | not recorded | vendor research, practitioner method |
| Hugging Face, "Security incident disclosure, July 2026", read 2026-11-10 | B | fine-tuned-model-is-a-data-store | 2026-11-10 | the vendor describing its own incident |
| Microsoft On the Issues, "Disrupting a global cybercrime network abusing generative AI" (Storm-2139), 2025-02-27 | B | ai-apis-and-the-gateway | not recorded | the vendor describing its own action, flagged |
| Sysdig Threat Research, "LLMjacking", 2024-05-06 | B | ai-apis-and-the-gateway | not recorded | observations B; the per-day cost figure is C and sits in the vendor-claims table |
| Google Threat Intelligence Group, Salesloft Drift data theft advisory, 2025-08-26 | B | ai-apis-and-the-gateway | not recorded | |
| beenuar/AiSOC, `services/api/app/services/evidence_bundle.py` at commit `a76073c` (2026-10-12), https://github.com/beenuar/AiSOC | B | tamper-evident-record | not recorded | for what the code does; found by one code search, so not a survey |

## Vendor and open-source tool documentation (Tier B for what a feature does)

Every row here is Tier B for what the product does, read on the date given, and any efficacy, coverage or comparison claim from the same publisher is Tier C with the bias flagged, listed in the next section. Neither line can raise a document's confidence past B (the README's Boundaries and `analysis/evidence-tiers.md`).

| Vendor or project | Pages read | Read | Cited by |
|---|---|---|---|
| Anthropic | Claude Code hooks, permissions, settings, managed settings, settings reference, sandboxing, monitoring, headless and costs (code.claude.com/docs); Compliance API (platform.claude.com); custom data retention for Enterprise (support.claude.com article 10440198); tenant restrictions (support.claude.com article 13198485); pricing (claude.com/pricing); Claude Code managed MCP (managed-mcp), monitoring and settings-reference `cleanupPeriodDays`; Claude Code security page (code.claude.com/docs/en/security, read 2026-11-17); "Mitigate jailbreaks and prompt injections" (platform.claude.com, read 2026-11-17) | 2026-11-09, 2026-11-10 and 2026-11-17 | telemetry-is-an-injection-surface, coding-agent-hooks-and-policy, configure-before-you-buy, telemetry-by-surface, what-to-log-and-what-it-costs, saas-embedded-ai-and-vendor-terms, rent-or-own-sized-to-the-org, inventory-and-shadow-ai, tamper-evident-record, mcp-servers-and-manifest-drift, ai-apis-and-the-gateway |
| Microsoft | Purview audit for Copilot and AI apps (ms.date 2026-08-26), auditing solutions overview, Purview for generative AI apps, DSPM for AI, DLP for Microsoft 365 Copilot, sensitivity labels; Microsoft 365 Copilot privacy (updated 2026-11-04), Copilot admin center settings, public web access; Restricted SharePoint Search and restricted content discovery; Copilot Studio data policies, security and governance, Managed Environments sharing limits; Entra agent identities, application permissions, diagnostic settings; Azure OpenAI monitoring and Foundry model monitoring; Secure Score; Security for AI app discovery, DSPM for AI (classic), Sysmon and `microsoft/SysmonCommon` `manifest.xml` (schema 4.90), Entra Agent ID overview and agent ID Governance, Defender for Cloud AI security posture and AI threat protection, Azure API Management AI gateway, Azure Activity Log schema, governing MCP tools through an AI gateway (updated 2026-08-27), Monitor Azure OpenAI (updated 2026-05-12) | 2026-11-09 and 2026-11-10 | telemetry-by-surface, configure-before-you-buy, saas-embedded-ai-and-vendor-terms, inventory-and-shadow-ai, ai-use-policy-and-intake, what-to-log-and-what-it-costs, stubs/assistant-oversharing, stubs/agent-builders, incumbent-tool-coverage, mcp-servers-and-manifest-drift, ai-apis-and-the-gateway, agent-identity-and-delegation |
| Google | Workspace Gemini log events, BigQuery log export and retention, Gemini conversation history settings, OAuth log events, Privacy Hub, Gemini app access, DLP for Gemini; Gemini Enterprise usage audit logs; Cloud Logging quotas; Vertex AI audit logging and request-response logging (Pre-GA on the read date); Agent Identity overview; Security Command Center AI Protection; Chrome Enterprise reporting connectors; Chrome Enterprise Premium DLP integration; Vertex AI audit logging | 2026-11-09 and 2026-11-10 | telemetry-by-surface, configure-before-you-buy, saas-embedded-ai-and-vendor-terms, inventory-and-shadow-ai, decision-sequence, stubs/assistant-oversharing, stubs/agent-builders, incumbent-tool-coverage, ai-apis-and-the-gateway |
| AWS | Bedrock model invocation logging; Bedrock and `bedrock-mantle` CloudTrail logging; CloudTrail event history and concepts; Bedrock AgentCore policy and enforcement modes; CloudTrail log file integrity validation (two pages) and S3 Object Lock; Bedrock CloudTrail monitoring, CloudTrail record contents and `userIdentity`; AgentCore policy, enforcement modes and observability; IAM Access Analyzer unused access and AgentCore CloudTrail data events | 2026-11-09 and 2026-11-10 | telemetry-by-surface, configure-before-you-buy, inventory-and-shadow-ai, coding-agent-hooks-and-policy, what-to-log-and-what-it-costs, stubs/agent-builders, tamper-evident-record, incumbent-tool-coverage, mcp-servers-and-manifest-drift, ai-apis-and-the-gateway, agent-identity-and-delegation |
| OpenAI | Codex approvals and security, rules, governance and managed configuration (learn.chatgpt.com); ChatGPT pricing; Codex managed configuration; "Safety in building agents" (developers.openai.com, read 2026-11-17, carrying an Agent Builder deprecation notice with a shutdown date of 2026-11-30) | 2026-11-09, 2026-11-10 and 2026-11-17 | coding-agent-hooks-and-policy, telemetry-by-surface, rent-or-own-sized-to-the-org, mcp-servers-and-manifest-drift, telemetry-is-an-injection-surface |
| GitHub | Copilot hooks reference, coding agent firewall, Copilot audit logs, enterprise audit log streaming, Copilot plans; MCP management, MCP allowlist enforcement, supported secret scanning patterns | 2026-11-09 and 2026-11-10 | coding-agent-hooks-and-policy, telemetry-by-surface, configure-before-you-buy, rent-or-own-sized-to-the-org, mcp-servers-and-manifest-drift, incumbent-tool-coverage |
| Cursor | hooks; compliance and monitoring; pricing; Enterprise | 2026-11-09 and 2026-11-10 | coding-agent-hooks-and-policy, telemetry-by-surface, configure-before-you-buy, rent-or-own-sized-to-the-org, mcp-servers-and-manifest-drift |
| Gemini CLI | policy engine (updated 2026-04-30), hooks (updated 2026-04-10), enterprise (updated 2026-06-16) | 2026-11-09 | coding-agent-hooks-and-policy, mcp-servers-and-manifest-drift |
| GitLab | Duo MCP clients | 2026-11-09 | coding-agent-hooks-and-policy |
| Kong | `ai-mcp-proxy` per-tool ACLs; per-tool ACLs for passthrough-listener MCP servers, observing MCP traffic with the File Log policy, AI Gateway overview, `ai-mcp-proxy` plugin and AI audit log reference | 2026-11-09 | coding-agent-hooks-and-policy, mcp-servers-and-manifest-drift, incumbent-tool-coverage, ai-apis-and-the-gateway |
| Atlassian | Rovo access, Rovo data usage and privacy, Atlassian Intelligence lesson, public issue AX-2026 | 2026-11-09 and 2026-11-10 | saas-embedded-ai-and-vendor-terms, inventory-and-shadow-ai |
| Salesforce | LLM data masking (Trailhead), generative AI audit and feedback data (Trailhead and data model guide), Agentforce Implementation Guide | 2026-11-09 | saas-embedded-ai-and-vendor-terms, telemetry-by-surface, stubs/agent-builders |
| ServiceNow | Now Assist data-sharing opt-out, data overflow processing, Generative AI Controller release notes, Now Assist Guardian, AI Control Tower asset discovery | 2026-11-09 and 2026-11-10 | saas-embedded-ai-and-vendor-terms, stubs/agent-builders |
| Slack | privacy principles for search, learning and AI; app approval; Audit Logs API | 2026-11-09 and 2026-11-10 | saas-embedded-ai-and-vendor-terms |
| Snowflake, Databricks, Workato, MuleSoft | Cortex cross-region inference; partner-powered AI features (doc date 2026-11-03); Workato Copilot, Agent Studio security and Genie governance; MuleSoft generative AI enablement | 2026-11-09 and 2026-11-10 | saas-embedded-ai-and-vendor-terms, stubs/agent-builders |
| Okta | log streaming; Cross App Access (re-read 2026-11-10); Identity Security Posture Management product page (undated) | 2026-11-09 | telemetry-by-surface, incumbent-tool-coverage, agent-identity-and-delegation |
| CrowdStrike, Obsidian Security | shadow-AI and agent governance feature pages, cited for what the feature does; CrowdStrike shadow-AI and agent innovations post (2026-03-23) | 2026-11-09 | saas-embedded-ai-and-vendor-terms, incumbent-tool-coverage |
| Ollama, vLLM | Ollama FAQ; `vllm serve` CLI reference; Ollama API authentication; vLLM security page | 2026-11-09 | telemetry-by-surface, inventory-and-shadow-ai, models-you-hold, incumbent-tool-coverage |
| osquery, Zeek, Syft | osquery `vscode_extensions` table spec (master); tool versions pinned in inventory-and-shadow-ai (osquery 5.24.0, Zeek 8.0.11, Syft 1.55.0); osquery table specifications; Zeek `base/protocols/ssl/main.zeek` | 2026-11-09 | inventory-and-shadow-ai, incumbent-tool-coverage |
| llama.cpp, LM Studio | llama.cpp server README (master, lines 194-217, 396-410 and 481-483); LM Studio server settings | 2026-11-10 | models-you-hold |
| Hugging Face, safetensors | Hub pickle scanning; safetensors README; `huggingface_hub` cache management | 2026-11-10 | models-you-hold |
| Netskope | AI Guardrails; certificate-pinned applications (re-read 2026-11-10) | 2026-11-09 and 2026-11-10 | incumbent-tool-coverage |
| Palo Alto Networks | AI discovery with Cortex AISPM (updated 2026-10-05) | 2026-11-09 | incumbent-tool-coverage |
| Tenable | Nessus plugin family "Artificial Intelligence" and plugin pages 302134, 324116 and 377737 | 2026-11-09 | incumbent-tool-coverage |
| Cognition | Windsurf guide for enterprise admins | 2026-11-09 | mcp-servers-and-manifest-drift |
| LiteLLM | MCP; proxy virtual keys and logging | 2026-11-09 | mcp-servers-and-manifest-drift, ai-apis-and-the-gateway |
| Cloudflare | detecting MCP traffic in Gateway logs; AI Gateway logging; "MCP security updates" blog (2026-08-14, read 2026-11-10) | 2026-11-09 and 2026-11-10 | ai-apis-and-the-gateway |

## Vendor claims, vendor studies and secondary coverage (Tier C, bias flagged)

| Source | Cited by | Last checked | Bias |
|---|---|---|---|
| IBM and Ponemon, Cost of a Data Breach Report 2025 (IBM Think summary, 2025-11-12) | ai-use-policy-and-intake | not recorded | survey of 600 breached organizations by a vendor that sells breach response |
| Datadog, State of Cloud Security 2025 | configure-before-you-buy | not recorded | publisher sells the remediation and measures its own customers |
| Orca Security, 2026 State of AI Security Report | configure-before-you-buy | not recorded | as above; figures are per organization per its methodology page |
| Zylo, 2025 SaaS Management Index | configure-before-you-buy | not recorded | as above |
| LayerX, Enterprise AI and SaaS Data Security Report 2025 | inventory-and-shadow-ai | not recorded | telemetry from the vendor's own install base |
| Veracode, 2025 GenAI Code Security Report | build-buy-and-the-high-priest | not recorded | vendor benchmark; Veracode sells code-security remediation |
| Google Cloud, Announcing the 2024 DORA report | build-buy-and-the-high-priest | not recorded | self-report association |
| Vendor product pages re-read 2026-11-10 (Lakera Guard, Noma, Harmonic, Wiz AI-SPM, Zenity, HiddenLayer) and releases read 2026-11-09 (Runlayer, Oasis, and the acquirers in the reading-vendor-claims ledger) | reading-vendor-claims | 2026-11-09 and 2026-11-10 | marketing; acquirer releases are Tier B only for the fact and date of the acquisition |
| AI Security Startups Map, https://startups.prompt.security/ (data file pulled 2026-11-09) | reading-vendor-claims | not recorded | curator owned by SentinelOne; no price from it appears as fact |
| TechCrunch, "OpenAI says AI browsers may always be vulnerable to prompt injection attacks" (2025-12-22) | reading-vendor-claims | not recorded | press coverage of a vendor statement |
| Coverage counts and risk percentages on the CrowdStrike and Obsidian pages | saas-embedded-ai-and-vendor-terms | not recorded | marketing, not tested |
| Guardrail and masking effectiveness statements for Salesforce Einstein Trust Layer, ServiceNow Now Assist Guardian and Atlassian Rovo | saas-embedded-ai-and-vendor-terms | not recorded | vendor efficacy statements, not tested |
| Atlassian Community thread on the September 2025 Rovo rollout | saas-embedded-ai-and-vendor-terms | not recorded | user reports |
| Salesforce developer and product blogs on hosted and external MCP servers (2026) | stubs/agent-builders | not recorded | vendor blogs |
| A ServiceNow community post (June 2026) on MCP server approval | stubs/agent-builders | not recorded | practitioner post, not vendor documentation |
| Anthropic Claude Code costs page, usage figures only | what-to-log-and-what-it-costs | not recorded | vendor interest flagged; the page is B for what the product does |
| SentinelLABS and Censys on exposed Ollama hosts | models-you-hold | not recorded | vendor research; primary not read, so listed under Unverified |
| Hines et al., "Defending Against Indirect Prompt Injection Attacks With Spotlighting", arXiv 2403.14720 | telemetry-is-an-injection-surface | not recorded | Microsoft authors evaluating their own defence |
| Wiz and Orca Security AI-SPM solutions pages | incumbent-tool-coverage | not recorded | marketing; read only from solutions pages |
| Waitzenberg and Harush (Wiz), "Same Threat, Two Verdicts", and Cohen and Herzog (Torq), "When Humans Can't Make It Hard Enough", [un]prompted II, October 2026, as carried in the lab's methodology section 10 | evaluating-ai-in-the-soc | not recorded | vendors describing their own agents |
| Mishra and Sharad, "Observability for Delegated Execution in Agentic AI Systems", arXiv 2606.09692 | agent-identity-and-delegation | not recorded | Splunk and Cisco authors |
| Dantuluri and Sundi, "Delegation Without Trust", arXiv 2609.00267 | agent-identity-and-delegation | not recorded | VotalAI authors |
| Vendor homepages and releases for non-human-to-human identity ratios and acquisitions (Astrix, Token Security, Palo Alto Networks Idira, Cyera, SailPoint, Cisco, Snowflake, Okta) | agent-identity-and-delegation | not recorded | marketing ratios, not tested |
| Sysdig's per-day LLMjacking cost figure; a vendor's published $13 per active day coding-agent usage average, as carried in the R6 results | ai-apis-and-the-gateway | not recorded | vendor figures, used for order of magnitude only |

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
- The order of the practices in each document written after the first fill (models-you-hold, landing-ai-events-in-ocsf, telemetry-is-an-injection-surface, tamper-evident-record, incumbent-tool-coverage, fine-tuned-model-is-a-data-store, frameworks-and-what-they-reach, evaluating-ai-in-the-soc, mcp-servers-and-manifest-drift, agent-identity-and-delegation, ai-apis-and-the-gateway), each labelled D where it is stated.
- The coverage grades over the 42 CoSAI components and the join design (incumbent-tool-coverage), the layer labels (frameworks-and-what-they-reach), the placement of the invisible-character filter (telemetry-is-an-injection-surface) and the OWASP API mapping onto gateway review (ai-apis-and-the-gateway).
- The tier ladder's own structure (evidence-tiers, and the document template).

## Tier disagreements

Where documents grade the same source differently, the dossier carries the tier CONTRIBUTING's table gives and each document keeps its own grade for its own claims until a revalidation pass reconciles them; no document's tier was changed for this file.

- `decision-sequence.md` grades the CoSAI risk map, MITRE ATLAS, OCSF, the MCP specification and the CISA KEV catalogue as Tier B, where the other documents and the table grade them A.
- `build-buy-and-the-high-priest.md` grades the CISA KEV catalogue B, and the Sigma specification B.
- `revalidation-and-pins.md` grades the OWASP Top 10 for LLM Applications 2026 B, where `stubs/ai-you-ship.md` and `stubs/rag-stores.md` grade it A.
- `saas-embedded-ai-and-vendor-terms.md` grades CISA's ScubaGoggles baselines A, while `configure-before-you-buy.md` grades the sibling ScubaGear B.
- `prompt-capture-and-the-law.md` grades EDPB, WP29, CNIL and Garante guidance B, where CONTRIBUTING's table would allow A for regulator text; the stricter grade fits non-binding and consultation documents, and the dossier follows the document.
- The OpenAI Compliance API help article is B in `saas-embedded-ai-and-vendor-terms.md` and C in `telemetry-by-surface.md`, both for the same excerpt-only reading (see Unverified).

Open for a maintainer ruling as of 2026-11-24, and changing no grade until it is made: whether a consortium paper approved by its governing board but still printing "Status: Draft" (CoSAI's MCP Security paper above) and a preliminary or public draft (NIST IR 8596, NIST SP 2400-102) are graded A or B, where the suggested default is B until the final version is published; and whether vendor prescriptive guidance (a model vendor's page saying what customers should do, as opposed to what its feature does) is B or C. A ruling either way amends Decision 4 in `DECISIONS.md` and clears the rows above that turn on it.

## Unverified

Claims or sources that could not be confirmed against a primary on the last pass are listed here, with the date and what was tried, until they are confirmed or dropped.

| Source | Cited by | Date | What was tried |
|---|---|---|---|
| OpenAI, "Compliance API for Enterprise customers" (help.openai.com article 9261474) | saas-embedded-ai-and-vendor-terms, telemetry-by-surface | 2026-11-09 | direct fetch returned HTTP 403; read through search excerpts only |
| OpenAI, corporate network controls in ChatGPT Enterprise (help.openai.com article 20001323) | inventory-and-shadow-ai | 2026-11-09 | fetch refused |
| Salesforce, "Export Agentforce Session Tracing Data (Beta)" | telemetry-by-surface | 2026-11-09 | direct fetch returned HTTP 403; read through a search summary |
| Microsoft, Copilot Studio audit logs for admins, makers and users | stubs/agent-builders | 2026-11-09 | the URL redirected when fetched; read through a search excerpt, as was the name of the tenant setting for publishing agents with generative AI features |
| ServiceNow, Now Assist data overflow processing default | saas-embedded-ai-and-vendor-terms | 2026-11-09 | page fetched, the default itself taken from a search summary |
| ISO/IEC 42001:2023 Annex A control numbering | ai-use-policy-and-intake, revalidation-and-pins, frameworks-and-what-they-reach | 2026-11-10 | iso.org returned 403; numbering taken from two secondary summaries that disagree on some details |
| ISO/IEC 42001:2023 clause numbers and titles (4.1, 5.2, 5.3, 7.2, 7.3) | ai-use-policy-and-intake | 2026-11-24 | paywalled, and iso.org returned 403 on 2026-11-10; the clause numbers follow the harmonized management-system structure and were confirmed only by a second model ("Gemini only" in the verification log), so the document now says the text was not read |
| ICO, "Monitoring workers" (3 October 2023) | prompt-capture-and-the-law | 2026-11-09 | ICO pages returned 403; read through law-firm summaries |
| NY Civil Rights Law §52-c, Conn. Gen. Stat. §31-48d, 19 Del. C. §705 | prompt-capture-and-the-law | 2026-11-09 | read through law-firm summaries, not at the statute |
| NLRB GC 25-05 (14 February 2025) and the Digital Omnibus Council mandate ST 14756/26 | prompt-capture-and-the-law | 2026-11-09 | read through press and law-firm reports |
| Federal Labour Court "objectively capable" reading of BetrVG §87(1) Nr. 6; DORA Art. 17; CCPA employee-data date | prompt-capture-and-the-law | 2026-11-09 | not re-read at the primary, so each stays at B in the document |
| Federal CIO Council, Application Rationalization Playbook v1.1 | build-buy-and-the-high-priest | 2026-11-10 | read through summaries |
| Lientz and Swanson 1980; Erlikh 2000 maintenance shares | build-buy-and-the-high-priest | 2026-11-10 | secondary compilations only; the document uses the direction and no figure |
| MacCormack 2012, the 2024 DORA report, Veracode 2025 | build-buy-and-the-high-priest | 2026-11-10 | rest on abstracts, vendor posts and search summaries, as the document's notes record |
| SentinelLABS and Censys exposed-Ollama counts | models-you-hold | 2026-11-09 and 2026-11-10 | primary not read; reached through secondary summaries |
| OWASP LLM01:2026 entry naming | telemetry-is-an-injection-surface | 2026-11-10 | taken from a search excerpt of the Q3 2026 exploit roundup; the 2026 entry text was not read |
| AWS Bedrock AgentCore policy default deny | mcp-servers-and-manifest-drift | 2026-11-09 | read through a search excerpt |
| OpenSec body, including the unit of its time-to-first-containment figure | evaluating-ai-in-the-soc | 2026-11-10 | abstract only |
| Xu, Zhang, Huang et al., "Do Not Blame Users for Misconfigurations" (SOSP 2013) | configure-before-you-buy | 2026-11-24 | its row and the document's Sources entry record the abstract only, so the body was not read |
| Álvarez, Nuño, Bulnes et al., network misconfigurations in Spanish organisations (Computer Networks 2026) | configure-before-you-buy | 2026-11-24 | its row records the abstract only |
| Narendra and Chatterjee, "Why Prompt-Injection Detectors Fail on XPIA" | telemetry-is-an-injection-surface | 2026-11-24 | its row records the abstract only |
| Schneier and Kelsey, "Secure audit logs to support computer forensics" | tamper-evident-record | 2026-11-24 | its row records the abstract only |
| Hou, Zhao, Wang and Wang, MCP landscape, threats and research directions | mcp-servers-and-manifest-drift | 2026-11-24 | its row records the abstract only |
| Song et al., "Beyond the Protocol" (IEEE TSE 2026) | mcp-servers-and-manifest-drift | 2026-11-24 | its row records the abstract only |
| Bhatt, Narajala and Habler, "ETDI" (CARS 2025) | mcp-servers-and-manifest-drift | 2026-11-24 | its row records the abstract only |
| Greshake et al. (ACM AISec 2023), Dietrich et al. (CCS 2018) and Boucher et al., "Bad Characters" | stubs/rag-stores, telemetry-is-an-injection-surface, configure-before-you-buy | 2026-11-24 | neither the row nor the citing document records how much was read, so these are listed until a read is recorded |
| Plan-tier, retention and default-state rows in rent-or-own-sized-to-the-org | rent-or-own-sized-to-the-org | 2026-11-24 | the document cites vendor admin documentation read 2026-11-09 but gives no row-level URL until ai-config-pointers is public, so the rows cannot be re-checked from this repo |
