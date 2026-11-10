---
evidence-tier: Mixed
convergence: single-source
applies-to-signals: [mcp-allowlist-absent, mcp-unpinned, mcp-remote, mcp-manifest-snapshot-absent, mcp-spec-pre-2026-07]
surfaces: [S4, S5, S7]
pins:
  - "MCP specification 2026-07-28"
  - "MCP Python SDK (mcp) 1.30.0 and 2.3.0 (lab run T8a)"
  - "@modelcontextprotocol/server-everything and server-filesystem 2026.8.31 (lab run R5)"
  - "OCSF main 1.10.0-dev at commit 6461440 for ai_capability (not in a release; the repo pin is OCSF 1.9.0)"
  - "Claude Code, GitHub Copilot, OpenAI Codex, Cursor, Windsurf, Gemini CLI, Amazon Bedrock AgentCore, Kong AI Gateway, LiteLLM and Microsoft Foundry documentation as read 2026-11-09"
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-03-10
status: EMERGING
measurement-claims:
  - claim: "Snapshotting tools/list from three static MCP servers produced 0 drift events across 51 consecutive snapshot pairs (17 per server, 2 of each server's 17 across process restarts), under both raw and canonical hashing; one host, three servers on protocol 2025-06-18"
    source: "sdw-lab-benchmarks@91e44df mcp-manifest-drift/RESULTS.md:62"
    date: 2026-11-09
    revalidate: 2027-03-10
  - claim: "Under raw json.dumps hashing a pure key reorder emitted 34 Update events (every tool on every server); canonical hashing (sorted keys, compact separators) emitted none"
    source: "sdw-lab-benchmarks@91e44df mcp-manifest-drift/RESULTS.md:77"
    date: 2026-11-09
    revalidate: 2027-03-10
  - claim: "An OCSF-native any-drift rule fired on 9 of 9 authored poisoned mutations and 12 of 15 authored benign ones; a body-aware composite over producer-computed fields fired on 9 of 9 and 0 of 15, on a corpus where the same agent wrote the mutations and the rules and the real-release arm did not run, so 0 of 15 is an upper bound and not a false-positive rate"
    source: "sdw-lab-benchmarks@91e44df mcp-manifest-drift/RESULTS.md:35-56,81-96"
    date: 2026-11-09
    revalidate: 2027-03-10
  - claim: "tools/list round trips after initialize had medians of 2.04, 3.44 and 7.65 ms on the three servers (verifier re-run 2.26, 5.36 and 9.52 ms), with single snapshots spiking to about 20 to 37 ms"
    source: "sdw-lab-benchmarks@91e44df mcp-manifest-drift/RESULTS.md:127-148"
    date: 2026-11-09
    revalidate: 2027-03-10
  - claim: "On the same SDK (mcp 2.3.0), moving from revision 2025-11-25 to 2026-07-28 removed Mcp-Session-Id (from 11 of 12 POSTs to 0), added Mcp-Method on 11 of 11 POSTs and Mcp-Name on 6 of 6 tools/call, and dropped in-protocol log notifications from 2 to 0 by default; one fixture server, both transports, three repeats"
    source: "sdw-lab-benchmarks@91e44df t8a-mcp-before-after/RESULTS.md:42-66,95-105,136"
    date: 2026-11-10
    revalidate: 2027-03-10
  - claim: "On the same revision (2025-11-25), moving the SDK from mcp 1.30.0 to 2.3.0 moved a raising tool's failure cause from the client-visible error text to a server stderr traceback, dropped the per-request server stderr line (10 to 0) and added OpenTelemetry spans (0 to 11 client and 12 server), which export nothing unless the operator configures a tracer provider"
    source: "sdw-lab-benchmarks@91e44df t8a-mcp-before-after/RESULTS.md:60-66,106,134"
    date: 2026-11-10
    revalidate: 2027-03-10
  - claim: "Recording one MCP tools/call, OCSF main with the ai_operation profile typed 24 of 33 facts, the OCSF #1754 draft class 22, OpenTelemetry GenAI plus MCP 19 and OWASP AOS on OCSF 11; the SDK server returned the same text for three different tool failures, so the cause never left the server process"
    source: "sdw-lab-benchmarks@91e44df agent-toolcall-schemas/RESULTS.md:44-47,49,57"
    date: 2026-11-09
    revalidate: 2027-03-10
---

# MCP servers and manifest drift: inventory, allowlists and what each layer logs

Evidence tier: Mixed, with the MCP specification at A, vendor documentation of what each allowlist and gateway feature does at B, three verified lab runs on one host at B, peer-reviewed MCP security work at A and preprints at B, and the order of the practices at D.

## Summary for the review

An MCP allowlist decides which servers an agent may start, and it says nothing about whether an approved server changed what its tools claim to do, so an organization that runs MCP needs three things that are easy to conflate: an inventory of the servers its clients are configured to reach, an allowlist keyed on something a user cannot rename, and a snapshot of each server's `tools/list` diffed over time. Since the 2026-07-28 revision deprecated the protocol's own Logging feature, and servers now send in-protocol log lines only for requests that ask for a log level, the record of a tool call has to be assembled from the client, the wire or gateway, the server's stderr or spans, and the authorization server.

- Inventory MCP client configuration on managed endpoints and count local, remote, unpinned and inline-secret servers. Effort S. Tier B for the config shapes, D for the secret heuristics.
- Allowlist by URL or exact command from the admin-owned tier, and treat a name-keyed or self-described bypassable allowlist as an inventory, which is how the routing row scores it. Effort M. Tier B.
- Pin local servers that a package runner starts to an exact version, and bump the pin on purpose. Effort S. Tier D for the practice, B for the exposure.
- Snapshot `tools/list` per server with canonical (JCS) hashing and send every change to a review queue rather than a page. Effort M. Tier B (one lab run, authored corpus).
- Put a gateway in front of remote servers that logs the caller, the `Mcp-Method` and `Mcp-Name` headers and the allow or deny decision. Effort L. Tier B.
- Ship server stderr, or turn on the SDK's OpenTelemetry export, wherever you run the server, because failure causes stay there. Effort M. Tier B.
- Record the negotiated protocol revision and SDK version per client and server, since the logging behaviour depends on both. Effort S. Tier B.

## Why this matters

The MCP attack classes that concern a security team live where a name-keyed control does not look. Tool poisoning and rug pulls are documented in peer-reviewed work, including malicious servers that passed the audits of three aggregation platforms (Tier A, Song et al., IEEE TSE 2026, abstract read). Poisoning through tool metadata alone reached 72.8% attack success in the most susceptible of 20 agent settings and 36.5% on average, with the highest refusal rate under 3%, so model alignment is not a control here either (Tier B preprint, MCPTox, arXiv 2508.14925). A census of 12,230 tools on 1,360 servers found 27.2% of servers (370) able to take part in a chained "parasitic toolchain" attack, with the root cause stated as MCP lacking "context-tool isolation and least-privilege enforcement" (Tier A, Zhao et al., IEEE S&P 2026). A metadata scanner flagged potential tool poisoning in roughly 4 of the 73 servers that scanned successfully, out of a random sample of 83 drawn from 1,899 collected, which I read as an existence proof rather than a prevalence figure (Tier A, Hasan et al., ACM TOSEM 2026, Section 5.2). A survey of the protocol sets out the wider taxonomy of four attacker types and 16 threat scenarios across the server lifecycle (Tier A, Hou et al., ACM TOSEM 2026, abstract read).

None of that is caught by asking whether a server is on the list, because an approved server can change its tool descriptions at the next start, and a server started with `npx some-server` with no version runs whatever the registry serves that day. So this document owns the server side of S5: which servers exist, how the allowlist is keyed, whether anyone is watching the manifests, and where the record lands. The harness-side controls that sit at the same boundary, hooks and permission rules on the coding agent, are in [coding-agent-hooks-and-policy.md](coding-agent-hooks-and-policy.md), and the discovery of servers nobody approved is in [inventory-and-shadow-ai.md](inventory-and-shadow-ai.md).

## Inventory: what the configuration files already say

The cheapest inventory is the client configuration on managed endpoints, since each MCP client I read keeps its server list in a file: Claude Code's `.mcp.json` and `~/.claude.json`, the Claude Desktop config, Cursor's `mcp.json`, VS Code's `.vscode/mcp.json` and Codex's `config.toml` (Tier B for the documented shapes). The repo's `scripts/reducers/mcp_config.py` reads any of these and reports counts only, never names or values (`mcp-remote-count`, `mcp-unpinned-count`, `mcp-inline-secret-count` and three more), which set the `mcp-unpinned` and `mcp-remote` signals and, when an inline secret is found, `agent-static-secrets`; its secret heuristics are mine (Tier D) and will miss a secret that looks like an ordinary word. Collecting the files across a fleet is an endpoint query that names the paths in advance, with the limits [inventory-and-shadow-ai.md](inventory-and-shadow-ai.md) describes.

Each count maps to a different exposure. A remote server's tool list and behaviour can change with no change on your side. An unpinned local server runs whatever the registry serves at every start, and an exact pin helps against a legitimate package shipping a malicious later version, as long as someone reads the diff before bumping it (my reasoning, Tier D). An inline secret is a long-lived credential in a user-readable file, and since the specification tells stdio servers to take credentials "from the environment", the local population tends to carry static secrets with no token log anywhere (Tier A, MCP specification 2026-07-28, Authorization).

## Allowlists: the match key decides whether it is a control

Allowlisting has matured unevenly, and the question for each product is what the allowlist matches on and whether a user can edit it. GitHub says its registry allowlist matches name or ID only, "can be bypassed by editing configuration files" and is not enforced for Copilot in the cloud, and recommends its managed-settings allowlist instead. Claude Code warns that a `serverName` entry "is not a security control", since a user can call any server `github`. Codex enables a server only when name and identity both match. That is the distinction `mcp-allowlist-absent` turns on, since an allowlist the vendor documents as bypassable selects the key just as no allowlist does.

| Product | Mechanism | Match key | Who can override | Default | last-checked |
|---|---|---|---|---|---|
| GitHub Copilot, registry allowlist | Enterprise registry (public preview) | Server name or ID | Bypassable by editing configuration files, per the vendor; not enforced for Copilot in the cloud | None until configured | 2026-11-09 |
| GitHub Copilot, managed-settings allowlist | `managed-settings.json` (GA) | Name, URL or stdio command | Users cannot override; the vendor says enforcement is overridable for enterprise teams | None until configured | 2026-11-09 |
| Claude Code | `managed-mcp.json` for exclusive control; `allowedMcpServers` with `allowManagedMcpServersOnly` | URL or exact command; `serverName` alone is "not a security control" | Managed tier wins; `managed-mcp.json` is a file at a system path deployed by MDM or an admin-privileged process, not through server-managed settings | None until configured | 2026-11-09 |
| OpenAI Codex | `[mcp_servers]` in managed configuration | Name and identity (command for stdio, URL for HTTP) must both match, and the string form of a command ignores `args`; an empty table disables MCP | Managed `requirements.toml` | None until configured | 2026-11-09 |
| Gemini CLI | Policy engine rules | `mcpName`, `toolName` wildcards, `toolAnnotations` | Admin tier if the directory is root-owned and not group- or world-writable; supplemental admin policy paths skip that ownership check | None until configured | 2026-11-09 |
| Cursor | "MCP server trust management" named on the Enterprise page | Not described | Not described | Not described | 2026-11-09 |
| Windsurf | MCP allowlist (Beta) | Not read | Not read | Not read | 2026-11-09 |
| Amazon Bedrock AgentCore Policy | Cedar policy at the gateway | Tool as action, conditions on tool input and token claims | IAM: `UpdateGateway` can flip `ENFORCE` to `LOG_ONLY` | Default deny, forbid wins | 2026-11-09 |
| Kong AI Gateway `ai-mcp-proxy` (3.12+, Enterprise) | Per-tool ACL | Consumer or consumer group to tool | Gateway admin | Not stated | 2026-11-09 |
| LiteLLM proxy | Server-level access | Key, team, org, access group; per-tool deny not on the page read | Proxy admin | Not stated | 2026-11-09 |
| Microsoft Foundry AI gateway | Governance (preview) | Only new portal-created MCP tools without managed OAuth | Azure RBAC | Off; subset only | 2026-11-09 |

All rows Tier B, vendor documentation; the AgentCore default-deny statement came through a search excerpt. A harness allowlist covers local and remote servers but runs on the laptop, while a gateway policy covers only remote servers routed through it and never sees a stdio server, so an organization with both kinds needs both. And on AgentDojo a tool-name allowlist left 99 of 609 attack sinks open where an argument-exact one left 1 of 609 (Tier B preprint, Ajar, arXiv 2609.26900, Table 6), the same lesson one level down, since a name says little about what the call will do.

## Manifest drift: what a snapshot-and-diff separates and what it cannot

The MCP 2026-07-28 revision says servers "SHOULD return tools from `tools/list` in a deterministic order to enable client-side caching" and requires a `ttlMs` freshness hint and a `cacheScope` field on `tools/list` and the other list results (SEP-2549), so the tool list is now a document the specification expects clients to cache and re-fetch (Tier A, MCP changelog), which is most of the way to a snapshot-and-diff detector. I ran one over three servers, the lab's own and the reference `server-everything` and `server-filesystem` at 2026.8.31, with three poisoned changes (a rug-pull rewrite of a description, an appended hidden instruction, a widened input schema) and five benign ones (a wording fix, a clarifying sentence, a new tool, a narrowed schema, a key reorder), emitting OCSF Application Lifecycle Update events carrying `ai_capability` and running five pre-registered Sigma rules over them (Tier B, sdw-lab-benchmarks@91e44df `mcp-manifest-drift/RESULTS.md:35-56`; one host, servers on protocol 2025-06-18, pre-registration frozen by the agent and not reviewed by the maintainer, verdict VERIFIED-WITH-FIXES).

Two results came before any rule ran, and both argue for doing this. Static servers produced no drift noise at all, 0 events over 51 consecutive snapshot pairs, and a verifier's second session returned byte-identical tool lists, so on this sample a server that is not changing does not look like it is. And canonical hashing mattered more than I expected, since raw `json.dumps` hashing turned a pure key reorder into 34 Update events, one for every tool on every server, while sorted-key compact hashing produced none; the OCSF attribute text already points at JCS serialization, and this is a concrete reason to follow it. The snapshot costs a few milliseconds per server at the median, so cost is not what limits the interval.

| Rule | What it reads | Poisoned detected (of 9) | Benign fired (of 15) |
|---|---|---|---|
| S1 any drift | OCSF-native `ai_capability` fingerprints | 9 | 12 |
| S2 contract drift | Native fingerprints against previous values carried in `unmapped` | 9 | 9 |
| S3, S4, S5 composite | Description delta, similarity score and a widening verdict, all producer-computed and in `unmapped` | 9 | 0 |

Each count is server-by-mutation cells where any event matched (same source). The change rules catch every poisoning because they catch every change, and the reason is structural: `ai_capability` carries fingerprints of the description and schema and no description text, so a hidden instruction and a wording fix produce the same native signal. A native-only rule is therefore a change-inventory alert, useful as a review queue because static servers were silent, and written as a poisoning detection it will page someone for typo fixes. The body-aware composite separated the two sets completely, but I wrote both the poisonings and the rules, so 0 of 15 is an upper bound on how good the rules look and not a field false-positive rate, and the arm that would have measured one, 13 real published releases diffed in sequence, did not run. The margin also looks thin, since the similarity rule depends on description length (a benign sentence added to a short description came within 0.071 of its threshold) and the rug-pull rewrite was caught by that one rule alone.

The literature agrees on the attack and is thin on the detector. ETDI proposes cryptographic tool identity and immutable versioned definitions without a measurement (Tier A venue, CARS 2025), and I found no paper measuring a snapshot-and-diff detector on real description changes. I would want signing and diffing together, because a malicious update from the legitimate publisher verifies cleanly while a diff shows what changed regardless of who signed it (Tier D).

## Hosted and local servers

Where a server runs decides who can see it and which controls apply, and the split is sharper than for most surfaces (Tier A for the specification, B for vendor behaviour, D for the summary).

- A local stdio server is a child process of the client. Its credentials come from the environment, it often runs outside the agent's sandbox (Claude Code lists local MCP servers among the things that run outside it, and GitHub's cloud-agent firewall "does not apply directly" to MCP server processes), and the endpoint's EDR process tree is usually the only telemetry independent of the client that sees it start.
- A remote server you host is reached over Streamable HTTP with OAuth 2.1 tokens bound to its audience under RFC 8707, and servers "MUST NOT accept or transit any other tokens", so the token-passthrough form of the confused deputy is closed at the protocol layer while the server's own downstream credentials remain the deputy (Tier A, MCP specification 2026-07-28, Authorization). You own its stderr, its spans and its authorization server.
- A hosted server run by a vendor gives you the client half and the gateway half of the record and whatever server-side half the vendor exports, and its manifest can change with no change on your side, which is why `mcp-remote` is a REVIEW signal and why the snapshot matters most here.

## What each layer logs

The 2026-07-28 revision deprecated the protocol's Logging feature with the note "log to `stderr` (stdio) or use OpenTelemetry instead of Logging" (SEP-2577), removed sessions and `Mcp-Session-Id` (SEP-2567) and the `initialize` handshake (SEP-2575), and requires `Mcp-Method` and `Mcp-Name` headers on Streamable HTTP POSTs (SEP-2243) (Tier A, MCP changelog). In a lab run against one fixture server I separated what the revision moved from what the SDK upgrade moved (Tier B, sdw-lab-benchmarks@91e44df `t8a-mcp-before-after/RESULTS.md:42-69`; one host under contention so no latency claim, verdict VERIFIED-WITH-FIXES). On the same SDK, the newer revision removed the session id, added the method and tool-name headers and silenced in-protocol log lines by default. On the same revision, the SDK upgrade moved a raising tool's failure cause from the client's error text to a server stderr traceback and added OpenTelemetry spans that export nothing until the operator configures a tracer provider. A team that upgrades the SDK but pins the older revision gets the second list and not the first, which is why `mcp-spec-pre-2026-07` asks for the revision and [revalidation-and-pins.md](revalidation-and-pins.md) asks for both values.

| Layer | What it carries | What it misses | Default | last-checked |
|---|---|---|---|---|
| Client (agent) | Intent: tool, arguments, decision; for example Claude Code `tool_result` and `tool_decision`, the latter carrying `tool_source: mcp` | Server and tool names unless `OTEL_LOG_TOOL_DETAILS=1`; the failure cause on SDK 2.3.0 servers | OTel export off until enabled | 2026-11-09 |
| Wire or gateway | Caller identity, method and tool name (as headers on 2026-07-28 HTTP), arguments if it parses the body; Kong writes an `ai.mcp.audit` object per allow or deny, and a denied call returns 403 with no `rpc` entry | Local stdio servers; failure causes; Foundry says its AI gateway does not log tool traces; AgentCore logs every decision to CloudWatch, fields not read | Gateway-specific | 2026-11-09 |
| Server stderr | Failure cause and traceback on SDK 2.3.0; per-request lines on 1.30.0 only | Anything, unless someone ships it | Written, not collected | 2026-11-10 (T8a) |
| Server OpenTelemetry | Client-parented request spans with `mcp.method.name`, `gen_ai.tool.name`, `error.type`; no arguments or results | Downstream HTTP hop unless that client is also instrumented | Off until a tracer provider is set | 2026-11-10 (T8a) |
| Authorization server | Client registration, issuer, token issuance for remote servers | Stdio servers, which take credentials from the environment | Product-specific | 2026-11-09 |
| EDR | Stdio servers as child processes, HTTP servers as connections | Tool names, arguments, results | On where EDR runs | 2026-11-09 |

Two blind spots apply whichever product sits in front. Tool failures arrive inside successful JSON-RPC responses with `isError: true`, so an anomaly model built on HTTP error rates sees a stream of 200s, and the SDK server I tested returned the same text for a syntax error, a rejected `DROP` and a missing table, so the cause existed only on the server (Tier B, `agent-toolcall-schemas/RESULTS.md`, one SDK). And OCSF main with the `ai_operation` profile typed 24 of 33 facts of one `tools/call`, more than the three other shapes I tried, while keeping descriptions and schemas only as fingerprints, so a drift event says something changed without saying what (same source); landing the tool call is the subject of the planned `landing-ai-events-in-ocsf.md`.

## What this does not mean

It does not mean the allowlist is pointless, since a URL- or command-keyed allowlist from the managed tier keeps unknown servers off managed machines and the snapshot is a second control on the servers that pass it. It does not mean the body-aware rules are ready to page anyone, because their behaviour on real releases is unmeasured. And manifest diffing has a hard floor, since a malicious later version of a legitimate package whose tool descriptions did not move is invisible to any manifest differ; pinning, an AI bill of materials and review of version bumps answer that case, outside this document. The lab runs were on one host, with servers on older revisions and an authored mutation corpus, so I would not generalize the counts beyond the shape of the finding.

## Gaps

- **Gap: field false-positive rate**. The body-aware rules have no estimate on drift nobody wrote. **Needs**: the R5 real-release arm (13 published versions of two reference servers), with its diffing code written and the package fetch approved.
- **Gap: servers on the 2026-07-28 revision**. All three R5 servers answered on 2025-06-18. **Needs**: a re-snapshot of a server that implements `CacheableResult`, after adapting the snapshotter to `server/discover`.
- **Gap: runtime-changing manifests and annotation flips**. `toolsListChanged` servers, a rug pull that flips `readOnlyHint` or `destructiveHint`, and three widening-check branches were not exercised. **Needs**: added mutations in a follow-up run.
- **Gap: gateway header logging**. Whether common gateways log `Mcp-Method` and `Mcp-Name` by default is unchecked. **Needs**: a desk pass over the gateways in the allowlist table, with a `last-checked` date per row.
- **Gap: hosted-server legibility**. How much server-side record hosted MCP vendors export rests on my unpublished desk scoring. **Needs**: a published, re-runnable inventory with its rubric.
- **Gap: other SDKs**. T8a covered the Python SDK's high-level API only. **Needs**: the same cells on a TypeScript or Go server.

## Notes

- 2026-11-10: lab citations point at lab master `91e44df`, where the research branch merged at the same commit; the R2, R5 and T8a RESULTS.md files are unchanged from `e0aaadc`, and the R2 row's range was tightened to 44-47, 49 and 57 so it names the 33-fact inventory line.
- 2026-11-10: R2 reported that the SDK 2.3.0 client negotiated 2025-11-25 by default; T8a traced that to R2's low-level `ClientSession.initialize()`, while the high-level `Client` adopts 2026-07-28 when the server answers `server/discover`. A collection plan should still expect older revisions for a while.
- 2026-11-10: the practice order in the summary and the hosted and local split are my judgement (Tier D).
- 2026-11-10: the allowlist table records "not described" or "not read" where a page did not say, rather than inferring a feature.
- 2026-11-10: adversarial verification pass re-derived every lab number from the three RESULTS.md files at 91e44df and re-read the MCP changelog and Authorization pages and the vendor pages for GitHub, Claude Code, Codex, Gemini CLI, Cursor, Windsurf, AgentCore, Kong, LiteLLM and Foundry; no number changed, and the fixes tightened the Logging wording (deprecated, not removed), the SEP-2549 description, the Hasan et al. denominators, the Codex identity match, the Gemini CLI supplemental-policy exception, the GitHub team override and which Claude Code event carries `tool_source`.

## Sources

Tier A

- Model Context Protocol specification 2026-07-28, changelog, https://modelcontextprotocol.io/specification/2026-07-28/changelog, read 2026-11-09.
- Model Context Protocol specification 2026-07-28, Authorization, https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization, read 2026-11-09.
- Model Context Protocol specification 2026-07-28, Deprecated features, https://modelcontextprotocol.io/specification/2026-07-28/deprecated, read 2026-11-09.
- OCSF schema `objects/ai_capability.json` at commit 6461440 (main, 1.10.0-dev), https://github.com/ocsf/ocsf-schema.
- Hou, Zhao, Wang and Wang, "Model Context Protocol (MCP): Landscape, Security Threats, and Future Research Directions", ACM TOSEM 2026, doi:10.1145/3796519 (abstract).
- Hasan, Li, Fallahzadeh, Rajbahadur, Adams and Hassan, "MCP at First Glance", ACM TOSEM 2026, doi:10.1145/3814959 (full text, arXiv 2506.13538v5).
- Song et al., "Beyond the Protocol: Unveiling Attack Vectors in the MCP Ecosystem", IEEE TSE 2026, doi:10.1109/tse.2026.3694876 (abstract).
- Zhao et al., "Parasites in the Toolchain", IEEE S&P 2026, doi:10.1109/sp63933.2026.00154.
- Bhatt, Narajala and Habler, "ETDI: Mitigating Tool Squatting and Rug Pull Attacks in MCP", CARS 2025, doi:10.1109/cars67163.2025.11337310 (abstract; design proposal, authors affiliated with OWASP Foundation and Intuit).

Tier B, vendor documentation of what a feature does (all read 2026-11-09)

- GitHub Docs, "MCP management", https://docs.github.com/en/copilot/concepts/enterprise/mcp-management
- GitHub Docs, "MCP allowlist enforcement", https://docs.github.com/en/copilot/reference/enterprise-administrators/mcp-allowlist-enforcement
- GitHub Docs, "Customizing or disabling the firewall for Copilot coding agent", https://docs.github.com/en/copilot/how-tos/agents/copilot-coding-agent/customizing-or-disabling-the-firewall-for-copilot-coding-agent
- Claude Code Docs, "Control MCP server access for your organization", https://code.claude.com/docs/en/managed-mcp
- Claude Code Docs, "Monitoring", https://code.claude.com/docs/en/monitoring-usage
- Claude Code Docs, sandboxing, https://code.claude.com/docs/en/sandboxing
- OpenAI, Codex managed configuration, https://learn.chatgpt.com/docs/enterprise/managed-configuration.md
- Gemini CLI Docs, "Policy engine", https://geminicli.com/docs/reference/policy-engine
- Cursor Docs, "Enterprise", https://cursor.com/docs/enterprise
- Cognition, "Windsurf Guide for Enterprise Admins", https://docs.devin.ai/windsurf/plugins/guide-for-admins
- AWS, "Policy in Amazon Bedrock AgentCore", https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/policy.html (default deny read through a search excerpt)
- AWS, AgentCore "Policy enforcement modes", https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/policy-enforcement-modes.html
- AWS, AgentCore "Observability, audit logging, and tracing", https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html
- Kong, "Configure per-tool access control for passthrough-listener mode MCP servers", https://developer.konghq.com/plugins/ai-mcp-proxy/examples/passthrough-listener-tool-acls/
- Kong, "Observe MCP traffic with the File Log Policy", https://developer.konghq.com/ai-gateway/observe-mcp-traffic/
- LiteLLM Docs, "MCP", https://docs.litellm.ai/docs/mcp
- Microsoft Learn, "Govern MCP tools by using an AI gateway", updated 2026-08-27, https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/governance

Tier B, first-party lab work and preprints

- sdw-lab-benchmarks@91e44df (lab master), `mcp-manifest-drift/` (R5), `t8a-mcp-before-after/` (T8a) and `agent-toolcall-schemas/` (R2), RESULTS.md and VERIFICATION.md each, https://github.com/flying-coyote/sdw-lab-benchmarks/tree/91e44df; one host, pre-registrations frozen by the agent and not reviewed by the maintainer, each verdict VERIFIED-WITH-FIXES.
- Wang et al., "MCPTox", arXiv 2508.14925, preprint.
- Sharma, Jiang, Chen and Lin, "Ajar: Measuring Open Privilege in Agent Defenses", arXiv 2609.26900, preprint (Table 6).
