---
evidence-tier: Mixed
convergence: single-source
applies-to-signals: [ai-gateway-absent, ai-gateway-present, gateway-token-store-unreviewed, cloud-trail-default-only]
surfaces: [S5, S7, S8, S9]
pins:
  - "CISA KEV catalogVersion 2026.11.09"
  - "MCP specification 2026-07-28"
  - "OCSF 1.9.0"
  - "OWASP API Security Top 10 2023"
  - "CoSAI secure-ai-tooling 622605a1"
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-03-10
status: EMERGING
measurement-claims:
  - claim: "Ten MCP tools/call exchanges through the official Python SDK 2.3.0 produced four tool errors, every one returned as a tool result with isError: true inside a successful JSON-RPC response, and the server masked three different causes behind the same text, Error executing tool <name>"
    source: "sdw-lab-benchmarks@91e44df agent-toolcall-schemas/RESULTS.md:37-47"
    date: 2026-11-09
    revalidate: 2027-05-10
  - claim: "On one million synthetic tool-call records, the layout that kept the tool name as a typed column was the fastest on every hunt, and the layouts that held it in an attributes map or an unmapped JSON blob were 4.7 to 32 times slower on the formal pass (ratios only; host isolation was violated, so absolute times are not claimed)"
    source: "sdw-lab-benchmarks@91e44df agent-toolcall-schemas/RESULTS.md:18-20, :114-122, :134-136"
    date: 2026-11-09
    revalidate: 2027-05-10
  - claim: "Metadata-only agent telemetry (token counts, model, agent, tool name) stores about 1.1 KB per million billed tokens in Parquet written with zstd at pyarrow's default level (level 1; pyarrow's default codec is snappy, so zstd was set explicitly)"
    source: "sdw-lab-benchmarks@91e44df agent-telemetry-retention/RESULTS.md:27-28, :57, :83, :115-117; PREREGISTRATION.md:101 for snappy as the pyarrow default"
    date: 2026-11-09
    revalidate: 2027-05-10
---

# AI APIs and the gateway

Evidence tier: Mixed (B facts, C cost figures, D mappings and judgements). What the clouds log by default and what a gateway feature does are Tier B vendor documentation read 2026-11-09; the KEV dates are Tier A; the two lab measurements are Tier B first-party runs on one host; the cost figures from vendors are Tier C with the bias flagged; the OWASP mapping and the advice on where to put the enforcement point are my judgement, Tier D.

## Summary for the review

An enforcement point the organization owns, a gateway or proxy on the path between its applications and the model and tool APIs they call, is where key custody, budgets, policy and a clear-text record can be applied once rather than per client, and for the same reason it often becomes the highest-value credential store in the environment, one that 2026's KEV catalogue already shows attackers reaching. It sees only the traffic pointed at it, and inside that traffic HTTP status codes no longer mean failure, so its record has to be read at the body or header level.

- Find out whether the cloud audit trail records model invocations by default on each cloud in use, and turn on the record where it does not (Vertex AI Data Access logs, Azure OpenAI diagnostic settings, Bedrock invocation logging for content). Effort S. Tier B.
- Where model calls bypass any owned enforcement point, route sanctioned application traffic through one, starting with the gateway features already licensed on an API-management or edge platform before buying another. Effort M. Tier B for the features, D for the sequencing.
- Bind every gateway key to an owner and a budget, and stop trusting client-supplied identity headers. Effort S to M. Tier B.
- Treat the gateway's credential store, admin API and own logs as a crown-jewel system: patch it on the KEV cadence, keep its admin surface off the internet, keep secrets out of its logs, and alert on its admin actions. Effort M. Tier A for the KEV record, B for the controls.
- Make the gateway log the tool name and the error inside the body (`isError`, the JSON-RPC error, the `Mcp-Method` and `Mcp-Name` headers) as typed fields, since anomaly rules keyed on 4xx rates see a stream of 200s. Effort M. Tier B, measured on one host.
- Alert on per-key spend, not fleet volume, for stolen-key abuse, because the token counts already exist and storing them costs almost nothing. Effort S. Tier B for the storage, D for the detection choice.

## Why this matters

Once an organization's own code calls a model API, which is surface S8 in this repo's vocabulary and sits underneath managed platforms (S7) and tool servers (S5) too, the security record stops being something a vendor hands over and becomes something the organization has to build. Without an enforcement point in the path, direct API use leaves DNS and TLS SNI to provider hosts, proxy logs if TLS is inspected, a bill per key or project, and secret-scanning hits when someone commits a key, which is enough to know that traffic exists and not enough to say who asked what (Tier B for the sources, D for the grade, which `telemetry-by-surface.md` sets out per surface). Provider-side administrative feeds, such as the organization and key events in Anthropic's Compliance API, cover key lifecycle rather than per-request content (Tier B, vendor documentation, read 2026-11-09), and I found no per-request content log offered by a model provider for plain API traffic in the documents I read (an absence claim, Tier D). That is why the gateway question is suppressed when S8 is absent, since an organization that only rents assistants and SaaS features has no API traffic of its own to route, and its controls sit in `telemetry-by-surface.md` and `saas-embedded-ai-and-vendor-terms.md`.

## The two directions of AI API traffic

AI consumes two kinds of API, model APIs and tool APIs (directly, through MCP servers on S5, or through a builder's connectors on S6), and it provides two kinds, inference endpoints (S7, S9, and S10 local servers that end up reachable) and agent endpoints such as hosted MCP servers and agent runtimes with an invoke API. The consumer side is where cost abuse and unsafe consumption of tool output live, while the provider side is where unauthenticated exposure and resource exhaustion live (Tier D for the split).

Read against the OWASP API Security Top 10 2023, the items that matter most for a gateway reviewer fall into three groups (Tier D mapping over Tier A/B titles from the OWASP project, read 2026-11-09).

- API2 Broken Authentication and API8 Security Misconfiguration describe the provider side: inference and orchestration endpoints that ship without authentication or with debug and admin routes exposed, which is the shape of several 2026 KEV entries below.
- API4 Unrestricted Resource Consumption is the consumer side's cost risk, covering token inflation, long contexts and tool loops, with LLMjacking as its stolen-credential form; CoSAI pairs `riskEconomicDenialOfWallet` with `controlApplicationAccessManagement`, the same control that carries identity and authorization, which I read as an instruction that a token budget belongs to an identity (Tier A/B, CoSAI secure-ai-tooling at commit 622605a1).
- API1 Broken Object Level Authorization and API10 Unsafe Consumption of APIs are the ones a gateway mostly cannot see, because a tool that authorizes the agent rather than the human returns a valid object on a valid call, and a poisoned tool response is a well-formed 200; reading API10 as indirect prompt injection is my analogy, not an OWASP statement.

## What the default cloud trail shows

The `cloud-trail-default-only` key exists because the three large clouds differ in whether a model invocation appears in the audit trail at all before anyone changes a setting. On Amazon Bedrock the runtime calls (`InvokeModel`, `InvokeModelWithResponseStream`, `Converse`, `ConverseStream`) are CloudTrail management events, and streaming calls add a stream-completion record carrying input and output token counts, while agent-runtime calls such as `InvokeAgent`, `Retrieve` and `ApplyGuardrail` are data events that are off by default and billed (Tier B, AWS Bedrock CloudTrail documentation, read 2026-11-09). On Vertex AI the `predict`, `rawPredict` and `generateContent` calls are Data Access audit logs, which Google's page says "are disabled by default and aren't written unless explicitly enabled" (Tier B, Google Cloud Vertex AI audit logging, read 2026-11-09). On Azure OpenAI in Foundry the activity log and platform metrics are automatic, but resource logs "aren't collected and stored until you create a diagnostic setting" (Tier B, Microsoft Learn, updated 2026-05-12).

| Platform family | Setting | Default | Where the record lands | last-checked |
|---|---|---|---|---|
| Amazon Bedrock | Runtime inference calls in CloudTrail | On, as management events, with a stream-completion record carrying token counts | CloudTrail, the customer's account | 2026-11-09 |
| Amazon Bedrock | Model invocation logging (request and response bodies) | Off | CloudWatch Logs or S3 in the customer's account, once configured | 2026-11-09 |
| Amazon Bedrock AgentCore | Data events for workload identity, token vault and gateway resource types | Off, billed per event | CloudTrail data events, once selected | 2026-11-09 |
| Google Vertex AI | Data Access audit logs for inference calls | Off | Cloud Logging, once enabled at project, folder or organization | 2026-11-09 |
| Azure OpenAI in Foundry | Resource logs for requests | Off until a diagnostic setting exists | Log Analytics (`AzureDiagnostics`), storage or an event hub | 2026-11-09 |
| Azure API Management | AI gateway in front of Foundry model endpoints | Absent until deployed and configured | Azure Monitor, including prompts and completions where enabled | 2026-11-09 |
| Self-hosted LiteLLM proxy | Message and response logging | On unless `turn_off_message_logging` is set (implied by the docs, which present it as an off switch) | Whichever callback destinations are configured | 2026-11-09 |
| Cloudflare AI Gateway | Request and response bodies | On | Cloudflare, exportable through Logpush | 2026-11-09 |

The last two rows run the other way from the usual finding. Most sanctioned AI platforms ship with the content channel off, but a self-hosted gateway and at least one hosted one capture prompts and completions unless someone turns that off (Cloudflare states its default outright, while LiteLLM's page implies it by documenting only the switch that stops it), so an organization that stands up a gateway for key custody may have started capturing prompt text without deciding to, and that decision belongs in `prompt-capture-and-the-law.md` and `what-to-log-and-what-it-costs.md` before the gateway goes live (Tier B for the defaults, D for the advice).

The detection consequence is concrete. The stolen-key pattern Sysdig described in May 2024, a new principal or user agent calling inference across regions and checking whether invocation logging is on, is visible in default CloudTrail on Bedrock, whereas on Vertex and Azure the same abuse leaves nothing in the default audit trail beyond the bill and platform metrics, so the first control on those two clouds is turning the record on (Tier B for Sysdig's observations, D for the comparison). One query hazard from the Bedrock page belongs in any detection content: the stream-completion event shares `eventName`, identity, source IP and user agent with the call that produced it and differs only in `eventType`, so a rule counting invocations has to filter on `AwsApiCall` or it double-counts streaming calls (Tier B, AWS documentation).

## What a gateway sees, and what it misses

A gateway sits on the hop between the application and the model or tool, so for traffic that crosses it the record can be the best an organization holds on any AI surface, because the gateway reads every request in clear text and the organization owns the log. The documented features show the shape. Azure API Management's AI gateway covers OpenAI, Anthropic Messages (on the v2 tiers) and Vertex AI request formats, self-hosted models, remote MCP servers and A2A agent APIs, with token limits keyed to a counter such as the subscription ID (`llm-token-limit`), token metrics (`llm-emit-token-metric`), a credential manager for OAuth to MCP servers, and logging of prompts and completions to Azure Monitor (Tier B, Microsoft Learn, ms.date 2026-05-29). LiteLLM attaches a standard logging object to each success and failure callback and ships to OpenTelemetry, S3 and about twenty other destinations, with budgets attached to virtual keys, teams or users (Tier B, LiteLLM documentation, read 2026-11-09). Kong's AI Gateway logs carry each MCP JSON-RPC method, tool name, latency and error, and its MCP proxy adds an audit entry with the access decision and the consumer once audit logging is switched on, though a call denied by an access rule leaves no request entry at all (Tier B, Kong documentation, read 2026-11-09 and re-read 2026-11-10). These are examples of what a documented feature does, and they are neither a comparison nor a recommendation. What the gateway misses comes in four kinds.

- It sees what was pointed at it. A gateway is a control for sanctioned S7, S8 and S9 traffic and close to useless for discovering unsanctioned AI, because a developer calling a provider directly with a personal key, a coding agent on a laptop, or a stdio MCP server that never touches the network all bypass it (Tier D, from the routing logic). Network-side enforcement that blocks non-gateway MCP traffic exists on at least one edge platform, and its vendor states that the detection needs TLS decryption and cannot see local stdio calls, off-network connections or Do Not Inspect traffic, adding that a missing MCP header does not prove a request is not MCP (Tier B, Cloudflare blog, "MCP security updates", 2026-08-14, read 2026-11-10). Discovery of the rest is a join over endpoint, identity and network telemetry, which `inventory-and-shadow-ai.md` covers.
- Status codes stop meaning failure. In the lab's MCP run, ten real `tools/call` exchanges through the official Python SDK 2.3.0 produced four tool errors, and every one came back as a tool result with `isError: true` inside a successful JSON-RPC response; the SDK server also returned three different causes (a SQL syntax error, a rejected `DROP`, a missing table) as the same text, `Error executing tool <name>`, so the cause never left the server (Tier B, sdw-lab-benchmarks@91e44df `agent-toolcall-schemas/RESULTS.md:37-47`; one host, stdio transport, VERIFIED-WITH-FIXES). MCP's Streamable HTTP transport is JSON-RPC over POST, so I expect the same at any HTTP gateway that does not parse the body, though that extension from a stdio capture is my inference and Tier D. An anomaly model built on 4xx rates sees nothing, and no gateway can recover a cause the server collapsed before the wire.
- The tool name is a header now, if anything logs it. The MCP 2026-07-28 revision requires `Mcp-Method` and `Mcp-Name` headers on Streamable HTTP POST requests, which lets a gateway record the method and tool without parsing the body (Tier A, MCP specification changelog). In the same lab run, the layout that kept the tool name as a typed column was the fastest on every hunt over a million synthetic records, and layouts that held it in an attributes map or an unmapped JSON blob were 4.7 to 32 times slower on the formal pass (Tier B, same commit and folder; the host was shared with other runs, so the ratios are the claim and the absolute times are not). Whether common gateways log those two headers by default I have not checked.
- The caller is a key, and the human is optional. Gateways meter and rate-limit per key or subscription, and the human appears only when the key is bound to one or a header supplies one; LiteLLM's documentation says an admin-created key with no `user_id` has no owner (Tier B, LiteLLM virtual keys page). A user ID taken from a client header is something the caller asserts about itself, which nobody authenticated, and even a gateway that propagates a verified user records a single hop with no parent and no scopes, so the delegation-chain question in `agent-identity-and-delegation.md` gets no feed from it.

API-security products that discover endpoints from traffic will find unregistered inference endpoints when that traffic crosses a sensor they watch, which helps with API9 Improper Inventory Management. Claims that such products understand prompts, tool semantics or agent intent are claims about how well a product works, so they stay Tier C until someone measures them against a labelled corpus, and I found no such measurement.

## The gateway is the credential store you built

The 2026 design pattern for agent and application credentials is to gather them into a broker, whether a gateway master key, a token vault or a credential manager, and that is the right instinct for key sprawl, but it also builds what is probably the highest-value target in the environment. The KEV record already shows one kind of broker being reached. As of the catalogue version pinned here, CISA KEV lists three LiteLLM entries added in 2026, a SQL injection (CVE-2026-42208, added 2026-05-08), a command injection (CVE-2026-42271, added 2026-06-08) and an improper-authentication flaw (CVE-2026-59822, added 2026-09-02), alongside six Langflow entries, five of them added in 2026, and one n8n entry added in 2026 (Tier A, CISA KEV catalogVersion 2026.11.09, re-queried 2026-11-10). I found no KEV entry or public exploitation report for the hyperscalers' own token vaults, so the evidence is that self-hosted gateways and orchestration platforms are reached, not that every broker is (Tier A for the absence in KEV, D for the reading). KEV records what was exposed and exploited, and a gateway kept behind a corporate network sits in a different population from an internet-exposed default install, which is both a reason to keep the admin surface private and a caution against reading the list as a product ranking.

The routing key for this is `gateway-token-store-unreviewed`, and its band is High because the gateway holds every upstream key, so compromising it compromises every route behind it. The controls are the ones a domain controller gets, applied to a newer system.

- Patch on the KEV cadence and watch the catalogue for the gateway and orchestration software actually run, which `revalidation-and-pins.md` already lists as a trigger for this document.
- Keep the admin and management API on a private network with its own strong authentication, separate from the proxy route applications use.
- Keep secrets out of the gateway's own logs, because a credential written into a log the gateway ships is as exposed as one committed to a repository.
- Send the gateway's admin actions (key creation, budget changes, route and policy edits) to the SIEM as their own stream and alert on them, and rotate the upstream provider keys it holds on a schedule.
- Prefer short-lived or workload-identity credentials to static upstream keys where the provider supports them, so that a stolen cache ages out.

## Cost abuse, and why the signal belongs to a key

LLMjacking, the use of stolen cloud or model-provider credentials to consume someone else's AI capacity, usually to resell it, is easy to put a number on and rarely instrumented. Sysdig's 2024 report estimated a worst case above $46,000 a day of charges to the victim, a ceiling computed from quotas and pricing rather than an observed loss (Tier C, vendor-computed estimate, bias flagged), and Microsoft's Digital Crimes Unit described the Storm-2139 group reselling access built on "exposed customer credentials scraped from public sources" (Tier B, Microsoft On the Issues, 2025-02-27). For scale, the lab's retention bench used a vendor-documented figure of roughly $13 per active day per coding-agent user to put a 1,000-user fleet at about $2.4M a year of inference (Tier C for the usage figure, which comes from the vendor's own page; cited in sdw-lab-benchmarks@91e44df `agent-telemetry-retention/RESULTS.md:40-41`). A stolen key running at quota for a day is in the same order of magnitude as a large fleet's daily spend, which is roughly why I think a spend anomaly on a single key is a better LLMjacking signal than a volume anomaly across the fleet (Tier D).

The token counts that signal needs already exist in the Bedrock stream-completion event, in gateway token metrics, in gateway spend tracking and in the provider usage APIs, and the OpenTelemetry GenAI conventions carry input and output token attributes for applications that instrument themselves (Tier B). Storing them is not a budget question, because the same bench measured metadata-only telemetry (token counts, model, agent, tool name) at about 1.1 KB per million billed tokens (Tier B, measured, same commit and folder; synthetic OCSF 1.9.0 records over real public text, one host, VERIFIED-WITH-FIXES). What the full prompt text costs to keep is a separate decision that `what-to-log-and-what-it-costs.md` prices.

## Where to put the enforcement point

For a small or mid-sized organization that mostly rents, the gateway question is often already half-answered by a platform it licenses. API-management platforms, edge and SSE platforms, and integration platforms now document AI gateway or MCP gateway features, so the first step is to check what is already in the contract and configure it, in the order `configure-before-you-buy.md` sets out, before buying a separate product (Tier B for the features existing, D for the order). A reviewer should expect three configuration gaps that recur across the pages I read: per-user identity propagation is a setting rather than a default, rate limits and quotas are often absent until set, and audit or payload logging on MCP routes is often off until someone switches it on (Tier B, vendor documentation, read 2026-11-09).

An organization that already runs an integration platform holding delegated OAuth into its SaaS can make that platform the gateway for agent-to-tool traffic, and it is probably the cheapest option because the proxy, the identity brokering and the log pipeline exist and are staffed. Doing so concentrates the organization's delegated SaaS authority behind one authentication surface, which the 2025 Salesloft Drift incident shows the cost of, since a third-party integration's OAuth tokens were used to export data from many corporate Salesforce instances and the advice was to treat every authentication token stored in or connected to the integration as potentially compromised (Tier B, Google Threat Intelligence Group, 2025-08-26). So the decision is which visibility gaps and which concentration the organization accepts, and I would not present it to a board as reducing risk outright (Tier D, dated 2026-11-10).

Bottom line: an owned gateway is where AI API traffic becomes legible and governable, provided the organization routes its sanctioned traffic through it, reads the body as well as the status code, binds keys to people, and protects the gateway itself as carefully as it protects its identity provider.

## What this does not mean

It does not mean a gateway finds shadow AI. The traffic that avoided the gateway is exactly the traffic it cannot see, and discovery stays a separate job.

It does not mean the gateway's record answers the delegation question. A gateway sees one hop, and the per-hop scopes and parent pointer that an escalation check needs are not emitted by any gateway I read about.

It does not mean a KEV-listed product should be avoided as a category, since the reading of the 2026 entries above is about where attackers are spending effort and says nothing about how the same software fares patched and kept off the internet.

## Gaps

- **Gap: gateway header logging**. Whether common gateways record `Mcp-Method` and `Mcp-Name` by default is unchecked. **Needs**: a lab run against at least three gateways at their default configuration, logging a fixed set of Streamable HTTP tool calls.
- **Gap: LiteLLM KEV root cause**. Whether CVE-2026-42271 sits in the credential-handling path or in an unauthenticated-exposure path is unread, which decides whether the broker-as-target point is an identity story or a misconfiguration story. **Needs**: the vendor advisory and CVE record for CVE-2026-42271 read and summarized.
- **Gap: gateway log leak incident**. A reported October 2026 compromise of a LiteLLM release, said to have begun from tokens leaked into a gateway's own logs, has no public primary in the sources read for this document. **Needs**: a first-party advisory or responder write-up before it is cited as evidence.
- **Gap: direct-provider audit APIs**. Whether OpenAI's organization audit-log API records per-request events could not be read (the fetch was refused). **Needs**: the provider's audit-log reference read and dated.
- **Gap: spend-anomaly detection**. The claim that per-key spend outperforms fleet volume as an LLMjacking signal is reasoning, not measurement. **Needs**: a labelled replay of stolen-key usage against a baseline fleet, scoring both rules.
- **Gap: API-security efficacy on AI traffic**. No labelled corpus measures how well API-security products detect prompt or tool abuse. **Needs**: a public or lab corpus of AI API traffic with labelled abuse and a scored run.

## Notes

- KEV counts, dated 2026-11-10. A re-query of the CISA KEV feed on 2026-11-10 returned catalogVersion 2026.11.09 (released 2026-11-09T19:54Z, 1,773 entries), the pinned version. Langflow has six entries in the catalogue in total and five added in 2026 (CVE-2026-33017, CVE-2025-34291, CVE-2026-55255, CVE-2026-0770, and CVE-2026-9198 listed under IBM as vendor), plus CVE-2025-3248 added 2025-05-05; the earlier "six versus five" discrepancy in the source research was a whole-catalogue count against a 2026 count, and both are stated with their windows here. LiteLLM three, n8n one, MLflow one (CVE-2026-64849, added 2026-08-19) and Ray one (CVE-2025-62593, added 2026-08-17) in the same catalogue.
- The R6 dollar range for retaining full prompt text is deliberately not used here; `what-to-log-and-what-it-costs.md` carries it under Decision 16 (the pre-registered grid, with the headline range in its notes).
- No gateway product was run in either bench, so the R2 findings describe the protocol and the reference SDK and the R6 figure describes storage; neither grades a gateway, and nothing here assumes any organization runs any product named.
- The forthcoming ai-config-pointers set (Decision 12) carries per-platform pages with console paths for the cloud and edge settings in the default-state table; it is not yet public, so this document calls it forthcoming and carries no link to it.
- The OWASP API mapping is one author's reading and has not been reviewed by a second reader.

## Sources

Tier A

- CISA, Known Exploited Vulnerabilities catalog, JSON feed, catalogVersion 2026.11.09, re-queried 2026-11-10, https://www.cisa.gov/known-exploited-vulnerabilities-catalog
- Model Context Protocol specification 2026-07-28, changelog and basic/authorization, read 2026-11-09, https://modelcontextprotocol.io/specification/2026-07-28
- OWASP API Security Top 10 2023, read 2026-11-09, https://api-security.owasp.org/editions/2023/en/0x11-t10
- CoSAI, secure-ai-tooling risk map, commit 622605a1, `risk-map/yaml/components.yaml`, `risks.yaml`, `controls.yaml`, read 2026-11-09, https://github.com/cosai-oasis/secure-ai-tooling
- OCSF 1.9.0 schema, https://schema.ocsf.io

Tier B, vendor documentation of what a feature does (all read 2026-11-09 unless dated otherwise)

- AWS, "Monitor Amazon Bedrock API calls using CloudTrail", https://docs.aws.amazon.com/bedrock/latest/userguide/logging-using-cloudtrail.html
- AWS, "Monitor model invocation using CloudWatch Logs and Amazon S3", https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html
- AWS, CloudTrail concepts, data-event resource types for Bedrock AgentCore, https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-concepts.html
- Google Cloud, "Vertex AI audit logging", https://docs.cloud.google.com/vertex-ai/docs/general/audit-logging
- Microsoft Learn, "Monitor Azure OpenAI", updated 2026-05-12, https://learn.microsoft.com/en-us/azure/foundry-classic/openai/how-to/monitor-openai
- Microsoft Learn, "AI gateway capabilities in Azure API Management", ms.date 2026-05-29, https://learn.microsoft.com/en-us/azure/api-management/genai-gateway-capabilities
- LiteLLM, "Virtual keys" and "Logging", https://docs.litellm.ai/docs/proxy/virtual_keys and https://docs.litellm.ai/docs/proxy/logging
- Kong, AI Gateway `ai-mcp-proxy` plugin and AI audit log reference, https://developer.konghq.com/plugins/ai-mcp-proxy/ and https://developer.konghq.com/ai-gateway/ai-audit-log-reference/
- Cloudflare, "Detect MCP traffic in Gateway logs" and AI Gateway logging, https://developers.cloudflare.com/cloudflare-one/tutorials/detect-mcp-traffic-gateway-logs/ and https://developers.cloudflare.com/ai-gateway/observability/logging/
- Cloudflare blog, "MCP security updates", 2026-08-14 (modified 2026-08-18), the vendor's own statement of what its MCP detection needs and cannot see, read 2026-11-10, https://blog.cloudflare.com/mcp-security-updates/
- Anthropic, "Compliance API", https://platform.claude.com/docs/en/manage-claude/compliance-api

Tier B, incident and threat reporting

- Microsoft On the Issues, "Disrupting a global cybercrime network abusing generative AI" (Storm-2139), 2025-02-27, https://blogs.microsoft.com/on-the-issues/2025/02/27/disrupting-cybercrime-abusing-gen-ai/
- Sysdig Threat Research, "LLMjacking: stolen cloud credentials used in new AI attack", 2024-05-06, https://www.sysdig.com/blog/llmjacking-stolen-cloud-credentials-used-in-new-ai-attack (observations Tier B; the $46,000 a day figure Tier C)
- Google Threat Intelligence Group, Salesloft Drift data theft advisory, 2025-08-26, https://cloud.google.com/blog/topics/threat-intelligence/data-theft-salesforce-instances-via-salesloft-drift

Tier B, first-party lab work

- sdw-lab-benchmarks@91e44df (lab master), R2 one MCP tools/call across three schemas, `agent-toolcall-schemas/RESULTS.md` and `VERIFICATION.md`, run 2026-11-09, verdict VERIFIED-WITH-FIXES; one host, MCP Python SDK 2.3.0, stdio transport, host isolation violated during timing, https://github.com/flying-coyote/sdw-lab-benchmarks
- sdw-lab-benchmarks@91e44df (lab master), R6 agent-telemetry retention, `agent-telemetry-retention/RESULTS.md` and `VERIFICATION.md`, run 2026-11-09, verdict VERIFIED-WITH-FIXES; one host, synthetic OCSF 1.9.0 records over real public text, AWS us-east-1 list prices of 2026-06-10, https://github.com/flying-coyote/sdw-lab-benchmarks

Tier C, flagged

- The $13 per active day coding-agent usage figure, a vendor's own published average, as carried in the R6 results; used here for order of magnitude only.
