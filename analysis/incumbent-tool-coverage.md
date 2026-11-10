---
evidence-tier: Mixed
convergence: single-source
applies-to-signals: [coverage-view-absent]
surfaces: [S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12, S13]
pins:
  - "CoSAI secure-ai-tooling 622605a1"
  - "OCSF 1.9.0"
  - "Syft 1.55.0, Grype 0.121.0, Trivy 0.76.0, ai-bom 3.6.0 and cyclonedx-bom 8.0.1 (lab run R4)"
  - "Incumbent vendor documentation for fourteen tool categories as read 2026-11-09, five defaults re-read 2026-11-10"
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-03-10
status: EMERGING
measurement-claims:
  - claim: "Across Syft, Grype, Trivy, ai-bom and cyclonedx-bom run three times over six AI artifacts (315 invocations, 88 of 88 tool-fixture pairs identical across runs), the pre-registered strict name match found 4 of 6 in some form (3 of 6 without Trivy rootfs mode, which was not pre-registered) and 1 of 6 as an AI artifact; the lenient post-run rule gives 5 of 6 (4 of 6 without Trivy rootfs mode) and 2 of 6; the Ollama blob store was found by no tool; one host"
    source: "sdw-lab-benchmarks@91e44df ai-artifact-sbom/RESULTS.md:26-29,33-47,62-68"
    date: 2026-11-09
    revalidate: 2027-03-10
  - claim: "The two MCP servers surfaced as ordinary npm and PyPI packages with every OSV-listed advisory matched (2 of 2 and 4 of 4) and no tool labelled the installed packages as MCP servers; in a post-hoc run that was not pre-registered, ai-bom labelled both from client config files with no version and no link to the package or its advisories"
    source: "sdw-lab-benchmarks@91e44df ai-artifact-sbom/RESULTS.md:41-44,127-133"
    date: 2026-11-09
    revalidate: 2027-03-10
  - claim: "Over synthetic delegation-shaped records, a check against only the human root's authority missed every reacquire plant (31,758 planted chains per run) and nothing else, while a recursive walk, a parent self-join and a write-time filter returned exactly the planted set in 18 of 18 cells"
    source: "sdw-lab-benchmarks@91e44df delegation-chain-query/RESULTS.md:31-39"
    date: 2026-11-09
    revalidate: 2027-03-10
---

# Incumbent tool coverage: what the security stack you already own can see of AI

Evidence tier: Mixed, with the CoSAI component map at A, vendor documentation of what a feature does and three verified lab runs at B, vendor efficacy claims at C, and every coverage grade and the join design at D, since the grades are one author's reading with no second reader.

## Summary for the review

The security tools a mid-to-large organization usually already runs see the identity plane, the cloud resources a managed AI platform creates, and the traffic someone routed through their own enforcement points, and they are blind by position to local models, stdio tool servers, the agent-to-tool hop inside managed platforms and the stages that run inside an agent's process. Graded against CoSAI's 42 components, fourteen incumbent categories see 11 in full, 30 partially at best, and one, `componentModelEvaluation`, not at all, so a coverage view is mostly a map of partial views that only become useful once they are joined.

- Draw the coverage view: grade each owned tool category against the 42 CoSAI components and the 13 surfaces as sees, partial or blind, from documented features. Effort M. Tier B facts, D grades.
- List the structural misses separately, so nobody buys a better product in the same category to close a gap that comes from where the category sits. Effort S. Tier D on B facts.
- Check the deployment condition behind every "sees" grade (TLS inspection and its bypass list, browser extension and device onboarding, the add-on licence, the connected cloud account), and downgrade any cell whose condition the organization does not meet. Effort S. Tier B.
- Turn on the AI-specific checks already paid for, which today include vulnerability-scanner plugin families for AI software and secret-scanning patterns for model-provider keys. Effort S. Tier B.
- Do not count an SBOM as a model inventory, since the lab run found one of six AI artifacts typed as AI under its pre-registered rule and the Ollama store found by no tool. Effort S. Tier B (one host).
- Join the partial views on host first, then identity, then cloud resource, and plan to build the credential key through a gateway or a provider admin feed. Effort L. Tier D design over Tier B fields.
- Treat model evaluation as the one cell to build for yourself, as a harness the team controls. Effort M. Tier D.

## Why this matters

A team asked "how much of our AI can we see" usually answers by product, which overstates coverage, since it counts a datasheet feature as deployed in the position the datasheet assumes and counts a category as covering a component when one vendor in it documents one feature for one assistant. The routing row behind this document, `coverage-view-absent`, is scored Low because a coverage view informs rather than protects, but it feeds the more expensive decisions in [configure-before-you-buy.md](configure-before-you-buy.md), which asks what owned features can be switched on before anything is bought, and [reading-vendor-claims.md](reading-vendor-claims.md), which asks which of a new vendor's promises land on cells the owned stack already reaches. That most organizations already run these fourteen categories is my practitioner observation, and I have not found a survey I would cite for it (Tier D), so the grades describe categories as documented and never one organization's environment.

## How the grades were made

The component list is CoSAI's `risk-map/yaml/components.yaml` at commit `622605a1`, which holds 42 components in 11 subcategories, the agent zoom-in components among them (Tier A, CoSAI secure-ai-tooling at commit 622605a1, count re-derived from the file on 2026-11-10). The surfaces are this repo's S1 to S13, defined in [surface-ownability.md](surface-ownability.md).

A cell is graded sees when the category's documented features observe or control that component natively, with content or configuration detail, once the product sits in its normal position; partial when it observes existence, metadata or a subset (a domain with no content, a package with no AI role), or sees fully only under a deployment condition most teams do not meet by default; and blind when no documented feature reaches it. Fourteen of the 42 components are stages that run inside an application, agent or tool-server process (prompt assembly, reasoning, memory, consent prompts, input and output handling), graded together in groups of six and eight. Each vendor named below stands in for its category on one or two documented features, so none of this is a vendor comparison, and where one vendor is the only evidence for a grade the text says so.

## Where component coverage sits

| Category | Sees (of 42) | Partial | Blind |
|---|---|---|---|
| SSE, CASB and SWG | 2 | 15 | 25 |
| DLP | 0 | 12 | 30 |
| EDR and XDR | 1 | 16 | 25 |
| Enterprise browser and browser management | 1 | 7 | 34 |
| Email security | 0 | 2 | 40 |
| IAM, IGA and PAM | 2 | 13 | 27 |
| CNAPP, CSPM and DSPM, including AI-SPM | 2 | 19 | 21 |
| API gateway, WAAP and AI gateway | 4 | 25 | 13 |
| SIEM and SOAR | 1 | 39 | 2 |
| SCA and SBOM | 1 | 7 | 34 |
| Secrets scanning | 0 | 5 | 37 |
| MDM and UEM | 1 | 1 | 40 |
| NDR | 0 | 10 | 32 |
| Vulnerability and exposure management | 1 | 6 | 35 |

All grades Tier D over Tier B vendor documentation read 2026-11-09; totals re-derived from the full grid on 2026-11-10. The 11 components some category sees cluster in the identity plane (identity provider, decision point), the cloud platform (data storage, serving, runtime hosting) and the enforcement points, while none of the 14 in-process components is seen by any category, so the best available there is the content those stages handle, caught at the wire by an inline proxy, a browser control or an AI gateway, or whatever the application writes to a log.

Two rows need care. The AI gateway collects the most sees grades because it sits on the hop between application and model where the composed prompt (user query, system instruction and retrieved context together) passes, and Azure API Management documents logging "prompts and completions to Azure Monitor" (Tier B, Microsoft Learn, read 2026-11-09), but a gateway sees only traffic someone pointed at it, and in my experience the traffic nobody routed is where shadow AI lives, which is why [ai-apis-and-the-gateway.md](ai-apis-and-the-gateway.md) treats it as a control for sanctioned traffic. The SIEM is partial on 39 components because it can hold any record someone sends it, which makes its grade a producer-by-producer question that [telemetry-by-surface.md](telemetry-by-surface.md) answers.

## Where surface coverage sits

| Surface | Categories that see it (of 14) | Blind (of 14) | Best partial or full view |
|---|---|---|---|
| S1 AI in SaaS apps | 0 | 8 | SSE, DLP, browser; the AI call shares a host with the app |
| S2 enterprise assistants | 4 | 4 | SSE, DLP, browser and IAM, through vendor connectors |
| S3 browser AI | 0 | 6 | Browser management for extensions; MDM or EDR for a second browser |
| S4 IDE and coding agents | 0 | 3 | Scanner and EDR inventory; secrets and SCA in repositories |
| S5 MCP servers and agent tools | 0 | 4 | EDR for stdio servers; gateway for routed remote ones |
| S6 low-code agent builders | 0 | 2 | IAM for platform agents; scanner for self-hosted instances |
| S7 managed AI build platforms | 1 | 7 | CNAPP and AI-SPM, plus cloud audit logs |
| S8 direct model API use | 2 | 3 | AI gateway and secrets scanning |
| S9 self-hosted serving | 0 | 7 | Scanner, EDR, NDR, partially |
| S10 local open-weight models | 0 | 7 | EDR, MDM and scanner on the endpoint, partially |
| S11 fine-tuned models | 0 | 9 | CNAPP, cloud logs, SCA, partially |
| S12 RAG and vector stores | 0 | 6 | DLP, CNAPP, email as retrieval content |
| S13 AI inside security tools | 0 | 12 | The security vendor's own audit log |

All grades Tier D over Tier B, counts re-derived 2026-11-10. S2 is best covered because the large vendors built connectors and audit records for that case, though its DLP and browser grades each rest on one vendor's feature (Purview and Chrome Enterprise Premium), and S13 is worst, which leaves a team trusting the security vendor to audit its own agent.

## What each category sees, and the condition behind it

SSE, CASB and SWG earn their reputation for SaaS AI used through a browser on a managed device, since Microsoft documents a generative AI category of "more than a thousand generative AI-related apps" in the Defender for Cloud Apps catalogue and Netskope documents prompt and response scanning for a named list of assistants (Tier B, vendor documentation, read 2026-11-09). Prompt visibility depends on TLS inspection, though, and Netskope's predefined certificate-pinned apps bypass its cloud by default; I found no AI desktop app on that list, so the risk I would name is drift, where a desktop client breaks under inspection, someone adds a bypass, and the SSE is back to a domain and a byte count. DLP and the managed browser see the paste and the upload, and Purview DSPM for AI's weekly oversharing assessment over the top 100 SharePoint sites is the closest incumbent feature to posture management for `componentRAGContent`, for one vendor's assistant only (Tier B, Microsoft Learn).

EDR is the only category with a native view of the laptop, so it is the main instrument for S10 and stdio MCP servers. An MCP server started by an IDE is `node`, `npx` or `python` by image name and recognisable only by its parent process and command line, which Sysmon's process-creation schema carries (Tier B, the `microsoft/SysmonCommon` manifest at schema version 4.90, read 2026-11-09). CrowdStrike describes AI Discovery as finding "AI apps and agents, LLM runtimes, MCP servers, and IDE extensions" on endpoints (Tier B for the feature as announced 2026-03-23, C for any efficacy, untested). What EDR cannot say is what a process sent to a model.

IAM is where the incumbent stack has moved fastest, since Microsoft Entra Agent ID gives agents their own identity type and says "all agent authentication and activity is logged", though its security features for agents need a Microsoft Agent 365 licence, and Okta's Cross App Access lists autonomous agents with no user session under "when not to use" (Tier B, vendor documentation). An identity provider sees only the agents that authenticate through it, and a delegation record needs every hop, since in a synthetic lab run a check against only the human root's authority missed every chain in which an intermediate agent re-acquired authority it had dropped, while a full walk caught them all (Tier B, sdw-lab-benchmarks@91e44df delegation-chain-query/RESULTS.md:31-39, verdict VERIFIED-WITH-FIXES; [agent-identity-and-delegation.md](agent-identity-and-delegation.md) carries the argument).

CNAPP and AI-SPM are the strongest category for S7, discovering managed AI resources through the cloud API reads the CSPM already makes and AI libraries through disk and image scanning, and the limits are in the vendors' own words, since Defender's runtime AI threat protection lists "Connected AWS accounts: No", so for one Bedrock agent the posture tool sees the resource while that vendor's runtime detection does not, and Prisma AIRS says custom or self-hosted models and agents are outside its posture checks (Tier B, vendor documentation). Wiz and Orca were read only from solutions pages, so their scope statements are Tier C, and Orca's "100% Visibility" heading is a marketing absolute.

Secrets scanning and the vulnerability scanner see AI before it runs or as installed software, since GitHub's secret-scanning patterns cover OpenAI, Anthropic, Hugging Face, Azure OpenAI, Groq and Replicate keys with partner validation (Tier B, GitHub Docs), and a leaked provider key is often the first sign a team calls a provider directly. Tenable's Nessus plugin family Artificial Intelligence held 330 plugins on 2026-11-09, mostly installed-software and detection checks, including Ollama Unauthenticated Access (302134, Critical), LiteLLM Detection (324116) and AI Agent Skills Inventory (377737 and 377738, published that day), plus installed-software plugins for several coding agents and AI browsers (Tier B, Tenable plugin pages and family listing, 377738 from the listing only). So a scanner with an agent on the laptop inventories much of S4. For Rapid7 and Qualys I found no public answer for several AI products, which is "not found on public pages", never "no check exists".

The SBOM result is the one first-party measurement among these tools, where five tools run three times over six AI artifacts found, under the pre-registered strict name match, four of the six in some form (three without Trivy's `rootfs` mode, which was not pre-registered) and one typed as an AI artifact, and the Ollama blob store, which is how models actually sit on a host running Ollama, was found by no tool, while the model components carried no usable PURL (Syft gave none and ai-bom a made-up `pkg:pypi/<filename>`) and no CPE, so a vulnerability matcher had nothing to key on (Tier B, sdw-lab-benchmarks@91e44df ai-artifact-sbom/RESULTS.md:33-47 and :101-102, one host, pre-registration frozen by the agent and not reviewed by the maintainer, verdict VERIFIED-WITH-FIXES). The two MCP servers surfaced as ordinary npm and PyPI packages with every OSV-listed advisory matched, and no tool labelled the installed packages as MCP servers, though a labelled post-hoc run found ai-bom naming both from client config files with no version or package link (same file, :41-44 and :127-133; :35 for the made-up PURL).

The rest contribute one narrow view each, since Zeek's `ssl.log` records the client's SNI, enough to find egress to model-provider and model-hub domains (Tier B, Zeek documentation); device management inventories the Ollama, LM Studio and second-browser installs behind S10 and S3 without seeing what they do; and email security sits in front of `componentRAGContent` for S2 because mail is retrieval content, as the zero-click injection against Microsoft 365 Copilot recorded as CVE-2025-32711 showed (Tier B, public CVE record published 2025-06-11, delivery mechanism from press coverage).

| Feature | Default or condition | Effect on the grade | last-checked |
|---|---|---|---|
| Netskope predefined certificate-pinned apps | Bypass the inspection cloud by default; no AI desktop app on the list | An app later added to a bypass drops to domain-level visibility | 2026-11-10 |
| Purview DSPM for AI, third-party AI sites | Needs the Purview browser extension and device onboarding | Only as good as endpoint enrolment | 2026-11-09 |
| Entra Agent ID security features | Need a Microsoft Agent 365 licence | Identity seen; protections only if licensed | 2026-11-09 |
| Okta Cross App Access | Autonomous agents listed under "when not to use" | No standard delegation flow for agents without a user session | 2026-11-10 |
| Defender AI threat protection | Azure OpenAI and Azure AI Model Inference only; "Connected AWS accounts: No" | Bedrock resources posture-only | 2026-11-10 |
| Defender AI-SPM agent discovery | Foundry and third-party cloud agents need an Agent 365 licence from 2026-07-01 | Accounts and projects found; agents not | 2026-11-10 |
| Prisma AIRS posture | Custom or self-hosted models and agents not covered | Managed cloud resources only | 2026-11-09 |
| Bedrock model invocation logging | Disabled by default; calls through `bedrock-mantle` not captured | No content in the SIEM until enabled, and none for that endpoint | 2026-11-10 |
| AgentCore CloudTrail | Certain capabilities only (Gateway and Agent Registry) | Agent-to-tool hop mostly unexported | 2026-11-09 |

All rows Tier B, vendor documentation; rows dated 2026-11-10 were re-read that day and matched. Cloud audit-log defaults are in [telemetry-by-surface.md](telemetry-by-surface.md).

## Structural misses

These come from where a tool sits, so a better product in the same category does not close them (Tier D over the Tier B facts above).

- Local models with no egress (S10), seen after the download only by EDR, MDM and the scanner, none of which understands model storage.
- Stdio MCP servers (S5), local child processes with no network hop, so SSE, NDR and gateways are blind by construction ([mcp-servers-and-manifest-drift.md](mcp-servers-and-manifest-drift.md) covers what to collect).
- The agent-to-tool hop inside a managed platform (S7), where you see only what the platform exports, which the table above shows is thin by default.
- AI inside sanctioned SaaS (S1) and inside security tools (S13), where the AI call shares a domain and an identity with the normal app.
- The composed prompt, which only a hop between application and model sees, and only when traffic is routed through it.
- Model identity, since weights have no PURL, CPE or advisory feed, which the lab run recorded as a structural zero.
- Agent memory, for which OCSF has no object (its `memory_activity` is operating-system process memory), so even a willing producer has no standard field to write to (Tier B, sdw-lab-benchmarks@91e44df d3fend-ocsf-ai-alignment/RESULTS.md:42-46, a reading of pinned definitions, verdict VERIFIED-WITH-FIXES).

## Joining the partial views

Shadow AI discovery with owned tools works when the partial views are joined, and that join is a data problem before it is a tooling one, because the SSE knows a user and a domain, the SBOM a repository and a PURL, EDR a host and a process and the cloud audit log a principal and a resource, and those records share no key by default. I would build the join in the order host, identity, resource, credential, because host and identity reach almost every family (Tier D, my judgement).

The host-side families use different identifiers for the same machine, so the practical pattern is a device table published from the MDM or EDR, both of which hold an enrolment-time identifier, with everything else keyed to it. Then "which laptops have Ollama installed, a listener on 11434 this month and an unapproved MCP server configured" becomes a join on device ID over a scanner plugin, an osquery `listening_ports` query and a file read, and since Ollama binds 127.0.0.1 port 11434 by default, the listener query finds a local model server no network scanner will (Tier B, Ollama FAQ, read 2026-11-09). The identity join is where cloud logs earn their place, since CloudTrail carries `userIdentity.arn` and the Azure Activity log carries `caller` on every row, and it breaks on shared roles, where an `AssumedRole` session named after an instance tells you which workload called Bedrock and not which person, and `sourceIdentity` populates only when STS requires it, which in the environments I have seen is rare (Tier B, AWS CloudTrail and Azure Activity Log schema documentation, read 2026-11-09). The resource join is the easy one, since ARNs, Azure resource IDs and GCP resource names are already the primary keys of a CNAPP's resource graph.

The credential join mostly does not work, because a secret scanner's fingerprint of an OpenAI key in a repository and the key a laptop process used to call the provider cannot be matched by anything in these families when the provider's log is not yours and the endpoint never sees the key's value, so credential is the key an organization builds, through a gateway that binds keys to owners or through the provider's admin feed, rather than one it already holds. [inventory-and-shadow-ai.md](inventory-and-shadow-ai.md) has the lab measurement of how far five discovery methods get together.

## What this does not mean

It does not settle whether the owned stack is sufficient. An organization that has not switched a feature on, bought the licence or connected the cloud account sits below its column, while one that routes all model traffic through a gateway sits above the S8 and S9 rows.

Nor are the gaps a shopping list. Model evaluation is reached by no product I read, and [build-buy-and-the-high-priest.md](build-buy-and-the-high-priest.md) argues that an evaluation harness against an attack set the team controls is the one build worth suggesting to a team of any size, and new vendors' claims on the missed cells stay Tier C until something tests them.

And the view dates quickly, since Tenable published its agent-skills plugins on the day I read the family and Defender moved agent discovery behind a new licence four months earlier, which is why [revalidation-and-pins.md](revalidation-and-pins.md) lists a preview feature going generally available as a trigger to re-read this document. If a measured pass found that one owned category, configured as documented, saw most of the in-process components, the central claim here would be wrong.

## Gaps

- **Gap: second reader**. No second reader has gone over the 588 component cells or the 182 surface cells. **Needs**: an independent grading pass against the same documentation, with agreement per category.
- **Gap: the two most contested cells are untested**. SSE prompt capture for a desktop client behind a decryption bypass, and EDR telemetry for a stdio MCP server, rest on documentation. **Needs**: a lab run that exercises both cells on one host and records what each tool actually logs.
- **Gap: published coverage figure**. The figure drawing these grades over the CoSAI map is built but unpublished, so the tables stand in for a link. **Needs**: the figure published on securitydataworks.com after the second-reader pass, then linked here.
- **Gap: gateway header logging**. Whether Azure API Management and Kong log the MCP `Mcp-Method` and `Mcp-Name` headers by default is unchecked. **Needs**: a desk pass over both gateways' logging documentation, with a `last-checked` date per row.
- **Gap: scanner coverage outside Tenable**. Rapid7 and Qualys gave no public answer for several AI products. **Needs**: the vendors' customer knowledge bases, read and dated.
- **Gap: the join is unmeasured**. The join is a design with no measured effort or yield. **Needs**: a lab run joining scanner, endpoint and identity records over a synthetic fleet, with the match rate per key.

## Notes

- 2026-11-10: the component and surface counts were re-derived from the full grading grid, and the 42-component count from `components.yaml` at `622605a1`; every count matched the 2026-11-09 reading.
- 2026-11-10: five defaults were re-read against their pages (Bedrock invocation logging, Defender AI threat protection, Defender AI-SPM, Okta Cross App Access and Netskope certificate-pinned apps), and each matched.
- 2026-11-10: `surfaces` lists all thirteen because `coverage-view-absent` sits in no surface's enables list and the document grades every surface.
- 2026-11-09: the grading rules, grades, join order and structural-miss list are my judgement (Tier D).
- 2026-11-10: four vendor statements known only from search summaries are left out rather than cited unfetched.
- 2026-11-10: an independent verification pass re-derived both grid totals from strand tables, recounted `components.yaml` at `622605a1` (42 components, 11 subcategories), re-read the R4, R7 and R8 lines at `91e44df`, and re-fetched eight vendor pages (Bedrock invocation logging, Defender AI-SPM, Defender AI threat protection, Purview DSPM for AI, Entra Agent ID, Okta Cross App Access, Netskope certificate-pinned apps, Prisma AIRS Cortex AISPM), each matching; it qualified the lenient R4 count by Trivy `rootfs` mode and the model-PURL wording, and added the figure's page-pending marker to Sources.

## Sources

Tier A

- CoSAI, `risk-map/yaml/components.yaml`, cosai-oasis/secure-ai-tooling at commit 622605a1, https://github.com/cosai-oasis/secure-ai-tooling, fetched and counted 2026-11-10.
- OCSF schema 1.9.0, https://schema.ocsf.io/1.9.0/, read 2026-11-09.

Tier B, vendor documentation of what a feature does (read 2026-11-09 unless noted)

- Microsoft Learn, "How do I discover AI apps and the sensitive data these use in my organization?", https://learn.microsoft.com/en-us/security/security-for-ai/discover
- Microsoft Learn, "Microsoft Purview Data Security Posture Management for AI (classic)", https://learn.microsoft.com/en-us/purview/dspm-for-ai
- Netskope, "AI Guardrails", https://docs.netskope.com/en/ai-guardrails
- Netskope, "Certificate Pinned Applications", https://docs.netskope.com/en/certificate-pinned-applications, re-read 2026-11-10
- Google, "Use Chrome Enterprise Premium to integrate DLP with Chrome", https://knowledge.workspace.google.com/admin/security/use-chrome-enterprise-premium-to-integrate-dlp-with-chrome
- Microsoft Learn, "Sysmon", https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon, and `microsoft/SysmonCommon` `manifest.xml` (schema version 4.90), https://github.com/microsoft/SysmonCommon
- osquery table specifications, https://github.com/osquery/osquery/tree/master/specs
- CrowdStrike, "New CrowdStrike Innovations Secure AI Agents and Govern Shadow AI Across Endpoints, SaaS, and Cloud", 2026-03-23, https://www.crowdstrike.com/en-us/blog/new-crowdstrike-innovations-secure-ai-agents-govern-shadow-ai/ (C for any efficacy)
- Microsoft Learn, "What is Microsoft Entra Agent ID?", https://learn.microsoft.com/en-us/entra/agent-id/what-is-microsoft-entra-agent-id
- Okta Developer, "Cross App Access", https://developer.okta.com/docs/concepts/xaa, re-read 2026-11-10
- Microsoft Learn, "AI security posture management", https://learn.microsoft.com/en-us/azure/defender-for-cloud/ai-security-posture, re-read 2026-11-10
- Microsoft Learn, "AI threat protection in Microsoft Defender for Cloud", https://learn.microsoft.com/en-us/azure/defender-for-cloud/ai-threat-protection, re-read 2026-11-10
- Palo Alto Networks, "AI Discovery with Cortex AISPM", updated 2026-10-05, https://docs.paloaltonetworks.com/prisma-airs/ai-inventory/agent-discovery/ai-agent-discovery-with-cortex-cloud
- Microsoft Learn, "AI gateway capabilities in Azure API Management", https://learn.microsoft.com/en-us/azure/api-management/genai-gateway-capabilities
- Kong, "AI Gateway", https://developer.konghq.com/ai-gateway/
- AWS, "Monitor model invocation using CloudWatch Logs and Amazon S3", https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html, re-read 2026-11-10
- AWS, "Observability, audit logging, and tracing for your agents", https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html
- AWS, "CloudTrail record contents" and "CloudTrail userIdentity element", https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-record-contents.html and https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-user-identity.html
- Microsoft Learn, "Azure Activity Log event schema", https://learn.microsoft.com/en-us/azure/azure-monitor/fundamentals/activity-log-schema
- GitHub Docs, "Supported secret scanning patterns", https://docs.github.com/en/code-security/secret-scanning/introduction/supported-secret-scanning-patterns
- Tenable, Nessus plugin family "Artificial Intelligence", https://www.tenable.com/plugins/nessus/families/Artificial%20Intelligence, and plugin pages 302134, 324116 and 377737
- Ollama FAQ, https://docs.ollama.com/faq
- Zeek documentation, `base/protocols/ssl/main.zeek`, https://docs.zeek.org/en/master/scripts/base/protocols/ssl/main.zeek.html
- CVE-2025-32711, record published 2025-06-11, https://www.cve.org/CVERecord?id=CVE-2025-32711

Tier B, first-party lab work

- sdw-lab-benchmarks@91e44df, `ai-artifact-sbom/` (R4), `delegation-chain-query/` (R7) and `d3fend-ocsf-ai-alignment/` (R8), RESULTS.md and VERIFICATION.md each, https://github.com/flying-coyote/sdw-lab-benchmarks; one host, pre-registrations frozen by the agent and not reviewed by the maintainer, each verdict VERIFIED-WITH-FIXES; R7 runs on synthetic records and R8 is a reading of pinned schema definitions rather than a bench.

Page pending

- securitydataworks.com, CoSAI component coverage figure (incumbent tools and telemetry layers over the 42 components at `622605a1`): built, not yet published; no page to link as of 2026-11-10, see the published-figure gap.

Tier C, vendor marketing (bias flagged)

- Wiz, "AI Security Posture Management", https://www.wiz.io/solutions/ai-security-posture-management
- Orca Security, "AI-SPM", https://orca.security/platform/ai-security/ai-spm/
