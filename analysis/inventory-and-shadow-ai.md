---
evidence-tier: Mixed
convergence: single-source
applies-to-signals: [surface-unknown, shadow-ai-method-none, shadow-ai-method-network-only, oauth-grants-unreviewed, tenant-restriction-absent]
surfaces: [S1, S2, S3, S4, S5, S6, S7, S8, S10]
pins:
  - "osquery 5.24.0"
  - "Zeek 8.0.11"
  - "Syft 1.55.0"
  - "CoSAI secure-ai-tooling risk map 622605a1"
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-04-10
status: EMERGING
measurement-claims:
  - claim: "Across nine planted shadow-AI surfaces scored as ten cells on one endpoint, the union of five discovery methods (Zeek, a DNS log, osquery, Syft, an egress allowlist) found 8, reached 1 only partially (a local OpenAI-compatible server seen as a port) and missed 1 (model weights in the Ollama store)"
    source: "sdw-lab-benchmarks@e568f5b (branch hub/ai-research-2026-11-09) t1-shadow-ai-discovery/RESULTS.md"
    date: 2026-11-09
    revalidate: 2027-05-10
  - claim: "osquery found 6 of 10 cells and was the only method to reach the IDE extension, the MCP client configs and the browser extension; four of its six finds needed the query to name the path or table in advance, and under the literally frozen query text it scores 4"
    source: "sdw-lab-benchmarks@e568f5b (branch hub/ai-research-2026-11-09) t1-shadow-ai-discovery/RESULTS.md"
    date: 2026-11-09
    revalidate: 2027-05-10
  - claim: "Each network method (Zeek on an eth0 tap, the DNS log, the egress allowlist) found 2 of 10 cells, the outbound model-API calls and the AI SaaS visits, and saw local runtimes only as a port on a peer's connection"
    source: "sdw-lab-benchmarks@e568f5b (branch hub/ai-research-2026-11-09) t1-shadow-ai-discovery/RESULTS.md"
    date: 2026-11-09
    revalidate: 2027-05-10
  - claim: "Exactly one false positive across all methods and benign controls: the port 8080 rule (Zeek and osquery) on a benign Python file server"
    source: "sdw-lab-benchmarks@e568f5b (branch hub/ai-research-2026-11-09) t1-shadow-ai-discovery/RESULTS.md"
    date: 2026-11-09
    revalidate: 2027-05-10
---

# Inventory and shadow AI: discovery is an inventory join

Evidence tier: Mixed. A for the incident filing, the peer-reviewed measurement papers and the standards-body risk map; B for vendor documentation of what a feature does, one interview preprint and one first-party lab run; C, flagged, for vendor surveys and catalogue sizes; D for the method-by-surface judgement, the order of the sequence and the prevalence model.

## Summary for the review

Finding AI use nobody approved is a join across several inventories an organization already half-holds (the network catalogue, the identity platform's consent grants, endpoint queries, cloud audit logs, card spend and SaaS admin settings), and a programme that rests on the network catalogue alone sees the remote destinations well and the local and embedded surfaces hardly at all. In a single-host lab run each network method found 2 of 10 planted cells while an endpoint agent found 6, four of them only because its queries already named where to look (Tier B, first-party lab).

Actions, in the order I would take them from an SSE and an EDR:

1. Turn on the SSE or CASB generative-AI category, and where TLS inspection already runs, add the vendors' tenant-restriction headers and log the blocked requests as personal-account attempts. Effort S. Tier B.
2. Schedule a query over OAuth consent grants in the identity platform, joined against an AI app list, and treat any AI grant with mail or file scope as the first review item. Effort S to M. Tier B, with Tier A for why it matters.
3. Push four endpoint queries to managed devices: IDE extensions across editor forks, browser extensions, AI runtime processes and loopback listeners, and a path hunt for MCP configs and model files that names the hidden directories explicitly. Effort M. Tier B.
4. Turn on the non-default cloud audit paths for inference wherever AI services are permitted, and fix detections that filter on the older event source. Effort M. Tier B.
5. Add an AI-provider filter to the secrets-scanning report and a monthly expense keyword sweep. Effort S. Tier B.
6. Review AI feature toggles in the top SaaS vendors by user count each quarter. Effort L, recurring. Tier B.

The ordering is my judgement (Tier D). No published measurement says what share of AI use a network-only programme misses, so no figure for it appears here as a finding.

## Why this matters

Every later control in this repo assumes the organization knows which of the thirteen surfaces it runs, and shadow AI is the part of that inventory nobody registered. The case for treating it as an incident class, rather than a governance nuisance, has a Tier A anchor. CB Financial Services filed a Form 8-K under Item 1.05 (material cybersecurity incident) after "customer names, social security numbers and dates of birth" were disclosed through "an unauthorized artificial intelligence-based software application", with the bank becoming aware of the incident on 5 May 2026, the report dated 7 May and signed 11 May (Tier A, SEC filing, read 2026-11-10). I'd hold the emphasis a little lower than that filing suggests, though, because the one organizational sample I found, a CSIRO interview study of 27 Australian critical-infrastructure organizations, describes shadow-AI incidents as "limited in scope and severity" while its authors frame those benign events as incrementally raising exposure to serious breaches, so the fair reading is low severity per event and rising cumulative risk (Tier B, Chhetri et al., arXiv 2606.00088, preprint).

The frameworks place the problem unevenly. The CoSAI risk map names `riskShadowAndUnknownAgents` and `riskZombieShadowMCPServers` directly, and the controls discovery actually feeds are `controlModelAndDataInventoryManagement` and `controlAgentInventoryManagement` (Tier A, CoSAI secure-ai-tooling at commit 622605a1), so in those terms this document is about how you populate two inventories when nobody registered the thing being inventoried. The data-leakage path behind it is well evidenced, since Mireshghallah et al. found private emails shared verbatim, "especially related to work and finances", and PII in about 48 percent of translation queries in a public chat corpus (Tier A, COLM 2024, arXiv 2407.11438; the corpus skews to consumer use).

## Where each method leaves evidence

The surfaces that grow fastest leave their evidence away from the network. AI that a sanctioned SaaS vendor calls server-side never appears in the user's traffic, local models make one visible download and then run over loopback, and local MCP servers start as child processes of an editor from a JSON file in a home directory. The CSIRO interviews give the embedded-SaaS part independent support, with vendors "effectively turning [features] on" in enterprise tools without risk assessment (Tier B, preprint); the same study found "no evidence of shadow agentic AI" in its sample, so the MCP part has neither support nor a base rate yet, and the local-model part remains my model.

| Method | Finds | Structurally misses | Evidence |
|---|---|---|---|
| SSE or CASB AI category, DNS, egress logs | Remote AI destinations from managed, on-network devices; machine traffic to model APIs | Server-side SaaS AI, loopback runtimes, files on disk, personal devices, cloud egress that bypasses the SSE | B; T1 (2 of 10 cells each) |
| Tenant-restriction headers | Personal-account or foreign-tenant attempts against a sanctioned service, by user | Anything the proxy does not decrypt | B |
| OAuth consent grants | AI apps holding delegated access to mail, files or calendars | Copy-paste and uploads, local agents on the user's own session, API keys | B |
| Endpoint queries (osquery or EDR) | Runtimes, IDE and browser extensions, MCP configs, packages, model files | Whatever the query does not name | B; T1 (6 of 10, path-dependent) |
| SBOM and SCA | AI packages with PURLs, named model files | Extensions, MCP configs, runtime model stores | B; T1 (2 of 10) |
| Cloud audit logs | Managed AI resources and, where enabled, inference calls | Inference paths logged as off-by-default data events | B |
| Secrets scanning, expense data | Provider keys in code; paid seats and API spend with a budget owner | Keys outside scanned repos, free tiers | B |
| SaaS admin toggles | Which tenants have embedded AI on, since when | The actual use, in many products | B |

The specifics behind the table, each read from the vendor's own page on 2026-11-09 or 2026-11-10 (Tier B for what the feature does):

- Anthropic's `anthropic-allowed-org-ids` header, available to Enterprise plans and Console organizations, requires TLS inspection and answers a non-allowlisted organization with HTTP 403 and error code `tenant_restriction_violation`, while a malformed header gets a 400 (Anthropic support article 13198485). OpenAI documents a `ChatGPT-Allowed-Workspace-Id` header for ChatGPT Enterprise, which I could not re-read because the page refused the fetch, so treat that name as unconfirmed.
- Entra exposes user-consent grants through Graph `oauth2PermissionGrants` and makes admin and user grants reviewable per enterprise app (Microsoft Learn, updated 2026-02-19), and Google Workspace OAuth log events carry application name, client ID, scope, user, IP and ASN, plus fields marking actions taken by an AI agent (Google Workspace admin help).
- osquery's `vscode_extensions` table reports a `vscode_edition` column covering VS Code, VSCodium, Cursor, Windsurf and other forks (osquery table spec, master), and Ollama "binds 127.0.0.1 port 11434 by default" (Ollama FAQ), so a host listening-port query finds it where a network scan will not.
- AWS logs `bedrock-runtime` inference as management events at no extra cost, but the `bedrock-mantle` endpoint logs `CreateInference` as data events, which "are not logged by default", and detective controls filtering on `bedrock.amazonaws.com` or `bedrock-runtime.amazonaws.com` "will not capture `bedrock-mantle` activity" (AWS Bedrock user guide). On Google Cloud, `generateContent` and `predict` are Data Access audit logs, which "are disabled by default and aren't written unless explicitly enabled" (Vertex AI audit logging page).
- Atlassian's own learning material says Rovo "is enabled by default and can't be turned off, though org admins can deactivate AI features in individual apps", which is the embedded-SaaS pattern in a vendor's words.

## What the lab run showed

The T1 bench planted nine shadow-AI surfaces on one simulated endpoint, with the Ollama model store scored separately to make ten cells, and ran five methods over three fresh runs whose fired-rule sets were identical (Tier B, first-party, sdw-lab-benchmarks@e568f5b on branch hub/ai-research-2026-11-09, `t1-shadow-ai-discovery/RESULTS.md`; single host, planted fixtures, rules written by the same agent that planted them, independently re-run with a VERIFIED-WITH-FIXES verdict that changed no grade). The union found eight cells, reached the local OpenAI-compatible server only as a port, and missed the weights in the Ollama store. osquery found six and was the only method to reach the IDE extension, the MCP configs and the browser extension at all, while Zeek, the DNS log and the egress allowlist each found the two remote surfaces and nothing on disk. There was exactly one false positive, the port 8080 rule firing on a benign Python file server.

The finding I'd carry forward is about how the endpoint wins, since four of osquery's six finds needed the query to already name a path or a table, and its recursive `%%` glob skips hidden directories, so the pre-registered query never reached `.ollama`. Two of the finds also rest on harness changes made after the freeze, which leaves osquery at four under the literal frozen text. That makes the path list itself the control, which is why action 3 names the hidden directories explicitly and why the maintenance of that list is a recurring cost. Syft reported nothing for the extension directories or the config files, and the two model files it did catalogue carried no PURL, which is the same blind spot for model artifacts that the repo's planned document on models the organization holds will take up in depth.

## How the inventories join

The methods above land in different record types and join on four keys: the user, the device, the AI app or provider, and the credential (an OAuth client ID, an API key fingerprint or an IAM principal). The joins break in predictable places, since proxy logs carry a user but no tenant, endpoint inventory carries a file but no notion of a model, SaaS admin logs carry a tenant setting with no device, and cloud audit logs carry a principal that maps to a person only through the identity graph. So most of the work is identity resolution across sources, and in my experience the detection logic on top is simple once that exists. The repo's reducers for Entra and Google Workspace consent grants, Okta app lists, browser extension reports, expense exports and MCP configs produce counts that feed the routing table without a raw export leaving the environment.

## What this does not mean

It does not mean blocking fails. Monitoring before blocking matches the practice the CSIRO interviewees described (Tier B), but restrictions measurably suppress some use, since 36 percent of Danish workers who did not intend to use ChatGPT despite large time savings cited active employer restrictions (Tier A, Humlum and Vestergaard, PNAS 2024, 10.1073/pnas.2414972121). It does not mean the network catalogue is a waste, because it is cheap and it is the only method that names every remote destination, which T1 confirmed on every run. And the lab grades say what a method can see with a competent query on one planted host, which is a different thing from what a team sees with the queries it happens to have on a real fleet.

## Gaps

- **Gap: network-only miss share**. Nobody has published what share of AI use a network-only programme misses, and T1 is a single planted host. **Needs**: a 30-day comparison on a real fleet of a network-derived AI inventory against an endpoint, identity and SaaS-admin inventory over the same window, which the lab can run at small scale and must label as a small fleet; an organization's own number stays a reader-supplied input.
- **Gap: endpoint query noise**. T1 measured the four endpoint queries on planted fixtures with five benign controls, which says nothing about false-positive rates on ordinary developer machines. **Needs**: the four query packs published and run against unplanted endpoints, with per-query false-positive counts.
- **Gap: personal-account share**. The only figure for how much browser AI use runs through unmanaged personal accounts is vendor telemetry (Tier C). **Needs**: an independent measurement, or tenant-restriction block counts reported across several organizations.
- **Gap: OpenAI tenant header**. The `ChatGPT-Allowed-Workspace-Id` header name and its blocked-request response could not be re-read on 2026-11-10. **Needs**: a successful read of the OpenAI help page or a tested proxy deployment.

## Notes

- The prevalence model (dated 2026-11-09). I built an illustrative weighting in which roughly 40 to 60 percent of AI use in a hybrid organization never crosses a network control point in a form identifiable as AI, with embedded SaaS AI as the dominant term. It is a Tier D model with stated assumptions, it carries no measurement, and under `CONTRIBUTING.md` it never appears as a headline; the first gap above names the study that would replace it.
- Claim-level choice (Decision 16). The T1 osquery count is stated as 6 of 10 with the frozen-text 4 beside it, because the verification kept both readings and either alone would mislead.
- The method-by-surface table above is my judgement on Tier B facts (Tier D as a grid).
- Prevalence surveys measure different things and are not interchangeable: 41 percent of 18,000 Danish workers in exposed occupations had used ChatGPT for work (Tier A, PNAS 2024), 23 percent of employed US respondents used generative AI for work in the prior week (Tier B, NBER w32966), and a vendor reports 67 percent of AI use in its customers' browsers ran through unmanaged personal accounts (Tier C, LayerX 2025, bias flagged since the vendor sells the measuring extension). None measures unsanctioned or network-invisible use.

## Sources

Tier A

- CB Financial Services, Form 8-K, Item 1.05, report dated 2026-05-07, signed 2026-05-11. https://www.sec.gov/Archives/edgar/data/1605301/000160530126000021/cbfv-20260507.htm (read 2026-11-10)
- CoSAI, secure-ai-tooling risk map (`risks.yaml`, `controls.yaml`), commit 622605a1. https://github.com/cosai-oasis/secure-ai-tooling
- Mireshghallah et al., "Trust No Bot", COLM 2024. https://arxiv.org/abs/2407.11438
- Humlum and Vestergaard, PNAS 2024. https://doi.org/10.1073/pnas.2414972121

Tier B

- sdw-lab-benchmarks, T1 shadow-AI discovery, commit e568f5b on branch hub/ai-research-2026-11-09, `t1-shadow-ai-discovery/RESULTS.md` and `VERIFICATION.md` (run 2026-11-09). https://github.com/flying-coyote/sdw-lab-benchmarks
- Chhetri et al., "From Frontier to Shadow AI", arXiv 2606.00088, preprint, 2026. https://arxiv.org/abs/2606.00088
- Bick, Blandin and Deming, NBER working paper w32966, 2024. https://doi.org/10.3386/w32966
- Anthropic, tenant restrictions. https://support.claude.com/en/articles/13198485 (read 2026-11-10)
- OpenAI, corporate network controls in ChatGPT Enterprise. https://help.openai.com/en/articles/20001323-corporate-network-controls-in-chatgpt-enterprise (fetch refused 2026-11-09)
- Microsoft, manage application permissions in Entra (updated 2026-02-19). https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/manage-application-permissions
- Google, Workspace OAuth log events. https://knowledge.workspace.google.com/admin/reports/oauth-log-events (read 2026-11-09)
- osquery, `specs/vscode_extensions.table`, master. https://github.com/osquery/osquery (read 2026-11-09)
- Ollama FAQ. https://docs.ollama.com/faq (read 2026-11-09)
- AWS, monitor `bedrock-mantle` API calls using CloudTrail. https://docs.aws.amazon.com/bedrock/latest/userguide/logging-cloudtrail-mantle.html (read 2026-11-10)
- Google Cloud, Vertex AI audit logging. https://docs.cloud.google.com/vertex-ai/docs/general/audit-logging (read 2026-11-10)
- Atlassian, use Atlassian Intelligence across your organization. https://community.atlassian.com/learning/lesson/use-atlassian-intelligence-across-your-organization (read 2026-11-09)

Tier C (bias flagged)

- LayerX, Enterprise AI and SaaS Data Security Report 2025, vendor telemetry from its own install base. https://go.layerxsecurity.com/the-layerx-enterprise-ai-saas-data-security-report-2025
