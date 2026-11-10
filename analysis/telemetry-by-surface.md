---
evidence-tier: Mixed
convergence: single-source
applies-to-signals:
  - "audit-log-off-<platform>"
  - content-channel-off
  - content-channel-on
  - content-lands-vendor
  - content-lands-own-cloud
  - content-lands-laptop
surfaces: [S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12, S13]
pins:
  - "OCSF 1.9.0"
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-03-17
status: EMERGING
measurement-claims:
  - claim: "Claude Code 2.1.321 OpenTelemetry export at documented defaults delivered 8 of 12 per-interaction fields (identity, session, tool name, model, tokens, cost, host attributes, timestamps) and withheld prompt text, tool arguments, tool output and response text as lengths or <REDACTED>, identically in 3 of 3 trials"
    source: "sdw-lab-benchmarks branch hub/ai-research-2026-11-09 @ e568f5b t2-platform-telemetry/RESULTS.md:32-35"
    date: 2026-11-10
    revalidate: 2027-03-17
  - claim: "With every documented content gate on, Claude Code 2.1.321 delivered all 12 fields with values matching the known session in 3 of 3 trials, and tool output arrived only on the traces path behind a beta flag"
    source: "sdw-lab-benchmarks branch hub/ai-research-2026-11-09 @ e568f5b t2-platform-telemetry/RESULTS.md:35-38"
    date: 2026-11-10
    revalidate: 2027-03-17
  - claim: "Ollama 0.20.6 server log at default level carried none of the eight content, identity, model-per-request or token fields in 3 of 3 trials; model, token counts, tool call and response came back only in the client response body"
    source: "sdw-lab-benchmarks branch hub/ai-research-2026-11-09 @ e568f5b t2-platform-telemetry/RESULTS.md:40-47"
    date: 2026-11-10
    revalidate: 2027-03-17
---

# Telemetry by surface: what record exists, and the dated default-state table

Evidence tier: Mixed (B facts; D grades). What each platform records and how it ships is Tier B vendor documentation of what a feature does, read 2026-11-09; the two lab measurements are Tier B first-party runs on one host; the surface grades and the reading of what they mean for a collection plan are my judgement, Tier D.

## Summary for the review

On the sanctioned AI surfaces a per-interaction record mostly exists, but the content half of it (prompt, tool arguments, tool output, answer) is off by default nearly everywhere, identity often collapses to an application role or an API key at the platform layer, and where the content lands, with the vendor, in your own cloud or on a laptop, decides your retention and how much of an agent's behaviour you can reconstruct afterwards. On the surfaces where unsanctioned AI lives there is no first-party AI record to turn on at all, so the evidence there is network and endpoint telemetry joined against an inventory.

- Confirm the per-interaction audit record is on for each platform in the table below, and schedule an export to a store you own before the vendor's retention window closes (often 180 days, sometimes 30). Effort S. Tier B.
- Decide the content channel per platform on purpose rather than by default, using `prompt-capture-and-the-law.md` for the legal test and `what-to-log-and-what-it-costs.md` for the tier and the bill, and write down who owns the collector. Effort M. Tier B for the switches; D for the decision.
- Where content is captured, land it in object storage under your own retention and access control, and send a metadata projection to the SIEM. Effort M. Tier B.
- For coding agents, set and lock the telemetry exporter through managed settings, because a repository's settings can otherwise switch a signal off, and keep content flags off unless the decision above says otherwise. Effort S to M. Tier B, measured on one product and version.
- Make the record name a person: per-user roles or caller metadata on managed platforms, issued keys at a gateway. Effort M. Tier B.
- For self-hosted runtimes, assume the server log records nothing useful and put the record at the caller or a gateway in front. Effort M. Tier B, measured.

## Why this matters

Most of the AI an organization uses is rented, and on a rented surface the record the vendor exports is close to the only thing the organization holds besides its identity provider and its egress path. So the questions an investigation will ask later (who asked, which model answered, which tool ran with which arguments, what came back) can be answered only from records someone switched on, routed and kept before the incident. In the detection programmes I have run, the gap that hurt was rarely a log source missing from the catalogue and more often one that existed, was licensed, and was never turned on or never left the vendor's console, and AI telemetry repeats that pattern with the added twist that the useful half is a separate switch from the audit half.

## The record by surface

The grade describes the best per-interaction record a defender can get and the default it ships with, because the distance between the two is most of the story. A means a first-party record with identity, model, tools or data accessed and content (content may be opt-in); B the same without content in the log; C admin-only, aggregate, or no usable caller identity; D network or endpoint telemetry only; E nothing attributable. Grades are my reading of the vendor documents cited in the default-state table (Tier D), and they grade the category of surface, never a vendor.

| Surface | Best first-party record | Grade, best / default |
|---|---|---|
| S1 AI features embedded in SaaS | The SaaS app's own audit trail, where it records AI feature use at all; content channels exist on some platforms and are off | D / E |
| S2 Enterprise assistants | Assistant audit record (identity, agent, resources touched) with text held apart and reached through eDiscovery or a compliance API | A / B |
| S3 Browser AI | Browser management extension inventory; DLP on paste to AI sites | D / D |
| S4 Coding agents | OpenTelemetry export from the agent or a vendor compliance API, content opt-in and often top-tier | A / C |
| S5 MCP servers and tools | Client-side tool events, server stderr or spans, gateway headers | B / D |
| S6 Low-code builders | Platform audit or session tracing inside the builder | B / C |
| S7 Managed build platforms | Invocation or request-response logging into your own cloud account, off by default | A / C |
| S8 Direct model API | A gateway you own; without one, DNS, SNI and billing | A / D |
| S9 Self-hosted serving | Server request logs, off by default; a gateway lifts it | C / D |
| S10 Local models | EDR process, weight files, loopback listener | D / D |
| S11 Fine-tuned models | Training-job lifecycle events; no row-level lineage | C / C |
| S12 RAG stores | Platform retrieval records where the platform is managed; your own application logs otherwise | B / D |
| S13 AI inside security tools | The security tool's own admin audit, where it covers AI use | B / E |

None of the sources in the next table emits OCSF natively in the documents I read, and the OpenTelemetry GenAI conventions some of them borrow from are still at `development` stability, so every source is vendor JSON to normalize, which `landing-ai-events-in-ocsf.md` takes up (Tier D as an absence claim).

## The dated default-state table

Each row states a vendor default as read on the date in the last column, so anything a review draws from it should print "as of" that date. Where a row's family is one of the `audit-log-off-<platform>` values in `routing.yaml` it uses that name, and rows outside the closed list are labelled by surface; the small-organization platforms come first. Bracketed numbers point to Sources.

| Platform family | Setting | Default | Where the record lands | last-checked |
|---|---|---|---|---|
| office-suite-assistant (Microsoft 365 Copilot) | Purview Audit (Standard) `CopilotInteraction` record [1][2] | On when organization auditing is on; record carries user, app, agent, resources touched and two detection flags, but no text; 180 days, one year under Audit (Premium) | Purview unified audit log; text is stored in the user's mailbox and reached through eDiscovery or DSPM [3] | 2026-11-09 |
| office-suite-assistant (Microsoft 365, third-party AI apps) | `AIAppInteraction` audit for AI apps seen through browser or network DLP [1] | Off until pay-as-you-go billing is enabled; charged per record; 180 days | Purview unified audit log | 2026-11-09 |
| office-suite-assistant (Google Workspace with Gemini) | Gemini for Workspace log events [4]; BigQuery export of Workspace activity [5] | Log events kept six months in the Admin console; BigQuery export not running until the export box is checked | Admin console; your BigQuery dataset once export is on. Gemini conversation history is a user-side store, on for 18 months by default, with Vault coverage not stated on the pages read [6] | 2026-11-09 |
| office-suite-assistant (Gemini Enterprise) | Prompt-and-response logging setting on usage audit logs [7] | Off; text values are replaced with `<elided>`; `_Default` bucket keeps 30 days [8] | Cloud Logging in your project | 2026-11-09 |
| office-suite-assistant (Claude Enterprise) | Compliance API activity feed and content endpoints [9] | Off until enabled for the organization and a Compliance Access Key is created; transcript endpoints are Enterprise-only; retention not verified | Vendor-held, pulled on a schedule; custom retention (default indefinite, minimum 30 days) bounds what a pull can return [10] | 2026-11-09 |
| office-suite-assistant (ChatGPT Enterprise) | Compliance API and Compliance Logs Platform [11] | Owner must grant access; logs platform retention reported as 30 days | Vendor-held, pulled. Secondary sources only (see Gaps) | 2026-11-09 |
| coding-agent (Claude Code) | OpenTelemetry export and content flags (`OTEL_LOG_USER_PROMPTS`, `OTEL_LOG_ASSISTANT_RESPONSES`, `OTEL_LOG_TOOL_DETAILS`, `OTEL_LOG_TOOL_CONTENT`, `OTEL_LOG_RAW_API_BODIES`) [13] | Export off; every content flag off; exporter selectors not locked unless set in managed settings | Your collector, born on the laptop; Enterprise sign-ins also leave session transcripts vendor-side [9] | 2026-11-09 |
| coding-agent (OpenAI Codex) | `[otel]` in managed requirements; Compliance API `conversation_message` and `codex_log` [14] | OTel off; Compliance API collection off | Your collector for local events; vendor-held for the Compliance API | 2026-11-09 |
| coding-agent (GitHub Copilot) | Enterprise audit log and audit log streaming [15][16] | Audit log on, 180 days, settings, seats and agent activity on github.com, no client prompts; streaming off | GitHub; prompts only through customer-written hooks | 2026-11-09 |
| coding-agent (Cursor) | Audit log; OpenTelemetry Export [17] | Audit log on with no export, never carries prompts or output; OTel Export off; both Enterprise | Vendor console and Admin API (7-day default, 30-day maximum query window); your collector for OTel | 2026-11-09 |
| browser (Chrome Enterprise) | Cloud reporting and event reporting [27] | Cloud reporting off; event reporting must be enabled; events kept six months in the Admin console, with no export until a reporting connector is configured | Admin console; your SIEM through a connector | 2026-11-09 |
| identity-platform (Microsoft Entra ID) | Diagnostic setting for sign-in and audit logs [28] | Off; Entra ID P1 or P2 and an Azure destination needed | Your Log Analytics workspace or storage once routed | 2026-11-09 |
| identity-platform (Okta) | Log stream [29] | Unset; System Log retention reported as about 90 days (search excerpt, not read) | Okta System Log; your EventBridge or Splunk Cloud once streamed | 2026-11-09 |
| managed-model-platform (Amazon Bedrock) | Model invocation logging [18]; CloudTrail [19] | Invocation logging off; CloudTrail management events on with model id and no content; agent, knowledge-base and guardrail events are paid data events | Your S3 or CloudWatch Logs, kept until you delete them; `bedrock-mantle` calls are not captured | 2026-11-09 |
| managed-model-platform (Google Vertex AI) | Data Access audit logs [20]; request-response logging [21] | Both off. Request-response logging carries a page-top Pre-GA banner, has no caller-identity column, and is the only Vertex path to prompt and response content | Cloud Logging for audit; your BigQuery table for content, joined on `request_id` | 2026-11-09 |
| managed-model-platform (Microsoft Foundry) | Resource logs (`Audit`, `RequestResponse`, `Trace` and others) via diagnostic setting [22] | Not kept until a diagnostic setting exists; prompt text in `RequestResponse` not documented | Your Log Analytics workspace or storage | 2026-11-09 |
| SaaS with embedded AI, S1 (Salesforce Einstein and Agentforce) | Einstein Generative AI Data Collection [23]; Agentforce session tracing [24] | Data collection off; session tracing off per a search summary of a page that returned 403; Data 360 required for both | Data 360 audit and session-tracing objects in your org; `saas-embedded-ai-and-vendor-terms.md` covers the surface | 2026-11-09 |
| self-hosted runtime, S9 (Ollama, vLLM) | Ollama server log [25]; vLLM `--enable-log-requests` and `--enable-log-outputs` [26] | Ollama documents no request logging and binds 127.0.0.1:11434; vLLM request logging off, prompts only at DEBUG, outputs behind a second flag | Host log or journal; for Ollama the useful fields come back only to the caller (measured, below) | 2026-11-09 |

The pattern across the rows is that nearly every platform I could read ships an administrative trail and almost none of them ship the conversation into it, so a team that says it has "the Copilot logs" is worth asking which channel it means. The rows marked "no export" are the quietest gap, because the record exists and is aging out inside a vendor console that nobody pulls from. The forthcoming ai-config-pointers set, a separate repository that is not yet public, will carry one page per product with the setting path, licence tier and route for each of these rows, and each row here will link its page once that set is published.

## What the lab measured

Two cells in this table were measured rather than read, on one host, one account and one day (2026-11-10 UTC), three trials per configuration, with an independent verification that reproduced every headline number (sdw-lab-benchmarks branch hub/ai-research-2026-11-09 at `e568f5b`, t2-platform-telemetry/RESULTS.md and VERIFICATION.md, verdict VERIFIED-WITH-FIXES; Tier B).

Claude Code 2.1.321's OpenTelemetry export at its documented defaults delivered 8 of the 12 fields the bench scored: the account email and ids, session id, tool name, model id, four token counters, a list-price cost, host attributes and timestamps. The four content fields were present as lengths or as the literal `<REDACTED>`, so a parser sees the shape of the interaction without its content. With every documented content gate on, all 12 arrived with values matching the known session, though tool output arrived only on the traces path, which sits behind a beta flag. The attribute set was identical across trials. One detail matters for correlation: the network identity field was host attributes with no client IP, so the join key to a proxy or firewall record is the account email, not an address. The vendor's documentation says a direct API key, Bedrock, Vertex or Foundry deployment populates only the user id and session id, which the bench did not test.

Ollama 0.20.6's server log at default level carried none of the eight content, identity, model-per-request or token fields. It held access lines with a timestamp, status, latency and `127.0.0.1`, plus model-load lines naming the weights by blob digest, and the same windows held other clients' requests that nothing in a line distinguished from the bench's own. The loopback address was present on every line and attributed nothing. At debug level the log added the model name per request and the input token count, and still no text, tool, output count or user. Everything a security team would want came back in the client response body, so for a self-hosted runtime of this kind the record exists only if the caller keeps it.

Of the six platforms the bench documented but did not run, none carries all twelve fields at its default; Bedrock invocation logging, once switched on, comes closest (principal ARN, full bodies, token counts, no cost field). The Vertex arm was not run because no billing-enabled project was available, so its cells are documented only.

## Where the content lands

Where the content channel lands is the axis I would put in front of an architect before any feature list, because it sets retention, query cost and who can be asked for the record.

- With the vendor (enterprise assistants and their compliance APIs): you pull on the vendor's schedule, within the vendor's retention and pull window, so shortening retention for privacy also shortens what an investigation can recover (my inference from the retention and API pages, which do not state the link; Tier D).
- In your own cloud account (Bedrock, Vertex, Foundry, a gateway you run): the record sits under your IAM and your retention, which is the posture a detection engineer wants, and the price is that it is off until someone turns it on and pays for the storage.
- On the laptop (coding agents): the content is born on the developer's machine and reaches you only if an exporter there is configured and locked through managed settings, and even then it is the agent's view, so the local tool executions between model calls are in the agent's events and not in any platform log.

A coding agent forced to authenticate through a managed platform turns its model calls into platform traffic that lands in your invocation logs, which is probably the cheapest owned record of coding-agent model calls today, though it carries the model request and response and not the shell commands and file reads in between (Tier D, my inference from the vendor documents).

## What this does not mean

A record that exists is a precondition for detection and says little on its own about whether detection works. The academic record splits the two uses cleanly: in a 2026 preprint, metadata and OpenTelemetry-shaped views kept failure-detection F1 between 99.5% and 100% while the accuracy of locating the step where a failure originated never passed 0.5%, and fell to zero once decision content was removed (Tier B, preprint, synthetic fault traces rather than attacks). A peer-reviewed forensic analysis of an agent framework calls session transcripts "the single richest forensic artifact in the system" (Tier A). So metadata tends to tell you that something happened and content tends to tell you why, which is an argument for deciding the content channel deliberately rather than for turning it on everywhere, since captured prompts are a store of whatever users pasted; over 70% of queries in one large public conversation corpus contained some detected personal information, mostly names of people and organizations, even after a rule-based redactor had been run over it, which the authors found often missed personal information (Tier A, COLM 2024).

The table is also not a ranking. A platform with more cells filled is not the more secure choice, the defaults move on vendor release cycles, and a row can be wrong a month after its last-checked date, which is why every row carries one.

## Gaps

- **Gap: G1, mapped A-grade interactions**. Only the Claude Code half of a real interaction has been captured; what an assistant audit record (Purview `CopilotInteraction`) and a managed-platform invocation record (Bedrock `ModelInvocationLog`) look like once mapped to OCSF 1.9.0 `ai_operation`, and what each loses, is unmeasured. **Needs**: a pre-registered capture of one scripted interaction from a licensed Microsoft 365 tenant and a Bedrock lab account, mapped with the same rubric and independently verified.
- **Gap: G4, Foundry content in RequestResponse**. Whether Foundry's `RequestResponse` resource log carries prompt text rests on the absence of a documented field and a third-party integration's reading. **Needs**: a one-hour pre-registered capture of a diagnostic log on a lab Foundry resource.
- **Gap: G21, unreadable primaries**. The ChatGPT Enterprise rows rest on secondary sources because OpenAI's Compliance API help article and enterprise announcement returned HTTP 403, and so does the Salesforce session-tracing default; the Claude Enterprise Compliance API retention figure, Okta's System Log retention and the current Foundry tracing content-recording default were not read directly either. **Needs**: a desk pass that reads each page directly and updates the rows with a new last-checked date.
- **Gap: Vertex request-response logging status and measurement**. The feature carried a Pre-GA banner on 2026-11-09 and the lab's Vertex arm did not run. **Needs**: a re-read when the banner changes, and the Vertex arm of the platform-telemetry bench run on a billing-enabled lab project.
- **Gap: closed-list families without a row**. The `mcp-host` and `data-governance-platform` values of `audit-log-off-<platform>` have no row in the default-state table, so a review that selects either finds no dated default here. **Needs**: a desk pass over the MCP host settings of the coding agents and desktop assistants and over the AI audit records of data-governance platforms, each row with its own last-checked date.
- **Gap: Claude Code on other sign-in paths**. The measured cells cover one sign-in path; API-key and cloud-platform deployments are documented to populate fewer identity fields. **Needs**: the same bench rerun under an API key and through one managed platform.

## Notes

- Convergence is `single-source`. The standards route covers practices a standard prescribes; this document describes what products record, and no standard yet prescribes a per-interaction AI record outside the high-risk scope of the EU AI Act, which the law document covers.
- The `measurement-claims` sources name commit `e568f5b` on the lab branch hub/ai-research-2026-11-09, because the run has not yet merged to the lab's main line; they will be swapped to the merged commit before this document is gated. `revalidate-by` is about four months out because vendor logging defaults move on release cycles faster than the schemas do.
- The grade ladder and the "where content lands" framing are my judgement as of 2026-11-10 (Tier D). The last-checked dates are the dates the vendor pages were read, not the date this document was written.
- Microsoft's `ModelTransparencyDetails` field is described inconsistently on its own page (one section says model name is not available for Microsoft 365 Copilot, a later one says it is when a user picks a model), so the table does not claim the record names the model; test a tenant before relying on either reading.

## Sources

Tier A

- OCSF 1.9.0 schema and changelog, https://schema.ocsf.io and https://github.com/ocsf/ocsf-schema/blob/main/CHANGELOG.md, read 2026-11-09.
- Gruber and Hilgert, "Foundations for Investigations of Agentic AI Systems from the Forensic Analysis of OpenClaw", Digital Threats: Research and Practice (ACM), 2026, doi:10.1145/3848419.
- Mireshghallah et al., "Trust No Bot: Discovering Personal Disclosures in Human-LLM Conversations in the Wild", COLM 2024, arXiv:2407.11438.

Tier B, vendor documentation of what a feature does (all read 2026-11-09)

1. Microsoft Learn, "Audit logs for Copilot and AI applications", ms.date 2026-08-26, https://learn.microsoft.com/en-us/purview/audit-copilot
2. Microsoft Learn, "Learn about auditing solutions in Microsoft Purview", ms.date 2026-05-18, https://learn.microsoft.com/en-us/purview/audit-solutions-overview
3. Microsoft Learn, "Microsoft Purview data security and compliance protections for generative AI apps", ms.date 2026-05-27, https://learn.microsoft.com/en-us/purview/ai-microsoft-purview
4. Google Workspace Admin Help, "Gemini for Workspace log events", https://knowledge.workspace.google.com/admin/reports/gemini-for-workspace-log-events
5. Google Workspace Admin Help, "Set up service log exports to BigQuery" and "Data retention and lag times", https://knowledge.workspace.google.com/admin/reports/set-up-service-log-exports-to-bigquery and https://knowledge.workspace.google.com/admin/reports/data-retention-and-lag-times
6. Google Workspace Admin Help, "Manage Gemini in Workspace conversation history settings", https://knowledge.workspace.google.com/admin/generative-ai/workspace-with-gemini/manage-gemini-in-workspace-conversation-history-settings
7. Google Cloud, "Access Gemini Enterprise usage audit logs with Cloud Logging", https://docs.cloud.google.com/gemini/enterprise/docs/set-up-usage-audit-logs
8. Google Cloud, "Cloud Logging quotas and limits", https://docs.cloud.google.com/logging/quotas
9. Anthropic, "Compliance API", https://platform.claude.com/docs/en/manage-claude/compliance-api
10. Anthropic Help Center, "Configure custom data retention controls for Enterprise plans", https://support.claude.com/en/articles/10440198-configure-custom-data-retention-controls-for-enterprise-plans
13. Anthropic, Claude Code "Monitoring", https://code.claude.com/docs/en/monitoring-usage
14. OpenAI, Codex "Governance" and managed configuration, https://learn.chatgpt.com/docs/enterprise/governance and https://learn.chatgpt.com/docs/enterprise/managed-configuration.md
15. GitHub Docs, "Reviewing audit logs for GitHub Copilot", https://docs.github.com/en/copilot/how-tos/administer-copilot/manage-for-enterprise/review-audit-logs
16. GitHub Docs, "Streaming the audit log for your enterprise", https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/streaming-the-audit-log-for-your-enterprise
17. Cursor Docs, "Compliance and monitoring", https://cursor.com/docs/enterprise/compliance-and-monitoring
18. AWS, "Monitor model invocation using CloudWatch Logs and Amazon S3", https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html
19. AWS, "Monitor Amazon Bedrock API calls using CloudTrail", https://docs.aws.amazon.com/bedrock/latest/userguide/logging-using-cloudtrail.html
20. Google Cloud, "Vertex AI audit logging", https://docs.cloud.google.com/vertex-ai/docs/general/audit-logging
21. Google Cloud, "Log requests and responses" (Pre-GA banner present on the read date), https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/request-response-logging
22. Microsoft Learn, "Monitor model deployments in Microsoft Foundry Models", updated 2026-10-19, https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/monitor-models
23. Salesforce, "Generative AI Audit & Feedback Data Model", https://developer.salesforce.com/docs/platform/data-models/guide/generative-ai-audit-feedback-dmos.html
25. Ollama, FAQ, https://docs.ollama.com/faq
26. vLLM, `vllm serve` CLI reference, https://docs.vllm.ai
27. Google, "Manage Chrome Enterprise reporting connectors", https://support.google.com/chrome/a/answer/11375053
28. Microsoft Learn, "How to configure Microsoft Entra diagnostic settings", https://learn.microsoft.com/en-us/entra/identity/monitoring-health/howto-configure-diagnostic-settings
29. Okta, "Log streaming", https://help.okta.com/en-us/content/topics/reports/log-streaming/about-log-streams.htm

Tier B, practitioner and first-party lab work

- sdw-lab-benchmarks, branch hub/ai-research-2026-11-09 at commit e568f5b, t2-platform-telemetry/RESULTS.md and VERIFICATION.md, https://github.com/flying-coyote/sdw-lab-benchmarks, run 2026-11-10 UTC, verdict VERIFIED-WITH-FIXES; one host, one account, Claude Code 2.1.321, Ollama 0.20.6.
- OpenTelemetry semantic conventions for generative AI, v1.45.0 registry, https://github.com/open-telemetry/semantic-conventions (attributes at `development` stability on the read date).
- Zhu and Pu, "TelemetrySuffBench: Is Agent Telemetry Sufficient for Failure-Origin Diagnosis?", arXiv:2608.07899, 2026, preprint.

Tier C, secondary readings flagged

11. OpenAI Help Center, "Compliance API for Enterprise customers", https://help.openai.com/en/articles/9261474-compliance-api-for-enterprise-customers (HTTP 403 to direct fetch; read through search excerpts)
24. Salesforce, "Export Agentforce Session Tracing Data (Beta)", https://developer.salesforce.com/docs/ai/agentforce/guide/otel-api.html (HTTP 403 to direct fetch; read through a search summary)
