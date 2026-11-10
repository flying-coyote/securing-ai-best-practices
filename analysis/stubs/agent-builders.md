---
evidence-tier: Mixed
convergence: single-source
applies-to-signals: [agent-publish-approval-absent, maker-credential-agents, agent-external-sharing-unreviewed, connector-sprawl-unreviewed]
surfaces: [S6, S7]
pins:
  - "CoSAI secure-ai-tooling 622605a1"
  - "MITRE ATLAS v2026.10"
  - "CISA KEV catalog 2026.11.09"
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-02-12
status: EMERGING
---

# Agent builders and managed build platforms (S6, S7): declared gap

Evidence tier: Mixed, A for what the CoSAI control YAML says, B for what each platform's own governance documentation says a setting does, C for the rows flagged as read through a search excerpt, a vendor blog or a community post, and D for the order I would turn things on.

## Summary for the review

This family is a declared gap. The repo has not researched how publish approval, run-as identity, external sharing and connector scope behave across low-code agent builders (S6) and managed AI build platforms (S7), so the review should send the reader to the standard and to the platform's own governance page first, and use this stub only for the mapping and the defaults it records.

Read first: CoSAI's agent controls at commit `622605a1`, specifically `controlAgentPluginPermissions`, `controlAgentCredentialIsolation`, `controlAgentInventoryManagement` and `controlToolRegistryAndDiscoveryIntegrity` (Tier A), then the governance page of the builder in question (Tier B).

- `agent-publish-approval-absent`: put publishing behind a gate the platform already offers, which on the platforms read is a data policy or connector policy that blocks publish rather than a named approval step, and register every published agent in an inventory before it gets credentials, as `controlAgentInventoryManagement` asks. Effort M. Tier A for the control, B for the platform settings.
- `maker-credential-agents`: move agents off the maker's own connections onto either a dedicated least-privilege agent user or the invoking user's credential, so the agent cannot exceed the caller's authority (`controlAgentPluginPermissions`). Effort M to L, because existing flows break. Tier A and B.
- `agent-external-sharing-unreviewed`: require authentication on every published agent, block the public and web channels by policy, and cap sharing to named groups. Effort S. Tier B.
- `connector-sprawl-unreviewed`: treat the connector policy as the agent's tool allowlist and review it like one, including connectors that carry MCP tools (`controlToolRegistryAndDiscoveryIntegrity`). Effort M. Tier A and B.

The order I would turn these on is sharing first because it is cheap, then connectors, then credentials, with the publish gate and inventory set up alongside the connector review (Tier D). The defaults below are as of 2026-11-09 and the review prints that date beside them.

## Why this matters

On the CoSAI component map the organization owns most of what an S6 builder instantiates: the orchestration layer, the agent instructions, the tools, the node or connector catalogue, the hosting and the builder's own credential store, with the model rented through a direct API (Tier A for the component definitions; the ownership reading is mine, Tier D, and is set out in `../surface-ownability.md`). On S7 the cloud runs the serving and the registry, and the organization owns cloud IAM, the gateway where one is configured, and the cloud audit log. So these are surfaces where configuration is the organization's job, and the builders are often run by an automation or business-technology team outside central IT, which is why the family overlaps with shadow AI.

The incident record reaches both surfaces through familiar doors. MITRE ATLAS case study CS0070 records exploitation attempts against exposed Langflow and n8n instances by an AI-agent-driven threat actor, and the CISA KEV catalogue 2026.11.09 lists six Langflow entries (five added in 2026, one of them filed under the vendor name IBM) and one n8n entry added 2026-03-11 (Tier A, re-counted from the catalogue file). CS0057 is stolen cloud credentials used to call a managed model past its guardrails (Tier A). In both cases the AI-specific part is what the compromised identity can reach afterwards, because a builder keeps model keys, connector tokens and often data behind one credential store, so a web-application compromise turns into access across every tool the flows call.

## What the platforms ship (as of 2026-11-09)

Each row is the vendor's published default for the product, not any tenant's configuration. Where the first column names an ai-config-pointers companion page, that page carries the full row with console path and licence.

| Platform family | Setting | Default | Where the record lands | last-checked |
|---|---|---|---|---|
| Copilot Studio (`g1-microsoft-365-entra-copilot-studio.md`) | Data policy blocking the "Chat without Microsoft Entra ID authentication" connector (external sharing; B) | unset; new agents default to authenticated, but a maker can choose no authentication | violation row in the Channels page download; publish blocked | 2026-11-09 |
| Copilot Studio | Data policy blocking publishing channels, including Direct Line for websites and apps (external sharing; B) | Direct Line channels allowed | violation row; channel disabled for the maker | 2026-11-09 |
| Copilot Studio | Data policy blocking connectors used as tools, which also blocks MCP tools reached through them (connectors; B) | unset | violation row; publish blocked | 2026-11-09 |
| Copilot Studio | Managed Environments sharing limits: no security-group sharing, viewer cap (external sharing; B) | no limits until set; existing shares are not revoked | sharing error in the maker UI | 2026-11-09 |
| Copilot Studio | Tenant setting to publish agents with generative AI features (publish; C, name from a search excerpt) | not stated | none named | 2026-11-09 |
| Copilot Studio | Audit records for maker and admin activity such as agent creation (publish; C, page read via excerpt) | on, stays in Purview unless exported | Purview unified audit log | 2026-11-09 |
| Entra Agent ID (`g1-microsoft-365-entra-entra-id.md`) | Agent identity created for each Copilot Studio agent, creator recorded as sponsor (inventory; B) | on | Entra directory objects and sign-in logs | 2026-11-09 |
| Agentforce (`g8-saas-data-integration-salesforce.md`) | Agent running user (maker credential; C) | service agents get a new user with no inherited permissions plus a vendor permission set group; employee agents run as the invoking user | Setup Audit Trail for permission set changes | 2026-11-09 |
| Agentforce | External MCP server tool approval (connectors; C, vendor blogs) | off, no tools exposed until an admin approves them | tool approval event not documented | 2026-11-09 |
| ServiceNow (`g8-saas-data-integration-servicenow.md`) | AI Gateway approval playbook on MCP server registration (connectors; B, with the approval-before-activation detail from a community post, C) | not stated | AI Control Tower inventory | 2026-11-09 |
| ServiceNow | AI Control Tower flags for privileged and dormant agents (maker credential; B) | not stated | AI Control Tower inventory | 2026-11-09 |
| Workato (`g8-saas-data-integration-workato.md`) | Runtime user connections for agent skills, so each skill runs with the end user's credential (maker credential; B) | unset, builder's choice per skill | activity audit log | 2026-11-09 |
| Workato | Project Admin scope over who creates agents and adds MCP skills (publish; B) | role assignment; no separate publish permission named | activity audit log | 2026-11-09 |
| Amazon Bedrock AgentCore (`g3-clouds-aws.md`) | Workload identity and token vault API activity as CloudTrail data events (inventory; B) | off by default and billed when on | CloudTrail, only if data events are enabled | 2026-11-09 |
| Google Cloud Agent Identity (Agent Identity overview page; the `g3-clouds-gcp.md` row does not carry this detail) | IAM bindings left after an agent is deleted (inventory; B) | bindings remain as inactive grants | Cloud IAM policy | 2026-11-09 |

Two things stand out from building the table. As far as the four SaaS builder pages I read go, none names a publish-approval step for agents in the form the signal's question asks about; the closest equivalents are policies that block publish outright, an approval playbook on tool registration, and role scoping over who may build, which is why the first action above talks about a gate the platform already offers. And the maker-credential question has three different answers across three products (a dedicated agent user, the invoking user, or the builder's choice per skill), so the review should ask which one each built agent uses rather than which one the platform supports.

## What this does not mean

A blocked connector or an authenticated channel does not make an agent safe to run, because the data policy governs what an agent is built with and Microsoft states that it offers no tenant policy over what the agent says back beyond built-in moderation (Tier B, Copilot Studio security and governance page). Moving an agent onto the invoking user's credential trades one problem for another, since the agent then carries each user's full access and becomes the confused deputy CoSAI's `controlAgentPluginPermissions` warns about if it does not check the caller at each hop. And self-hosted builders (n8n, Langflow, Flowise) have no admin console comparable to the rows above, so for those the controls are the hosting and network ones, which this stub does not cover.

## Gaps

- **Gap: agent-builder governance defaults and attribution**. The repo has not read the publish, sharing, run-as and connector controls of the self-hosted builders or of the S7 agent builders (Foundry, Bedrock AgentCore, Vertex AI Agent Builder) in the depth of the four SaaS pages above, and has no measurement of whether a downstream audit log can attribute an agent run to the person who invoked it when the agent runs on its maker's connection. **Needs**: a desk census of those four controls across the self-hosted and S7 builders from vendor documentation, plus a lab bench that plants a maker-credential agent in a self-hosted builder and one SaaS builder and checks whether the target system's audit record names the invoking user, the maker or a shared service principal.

## Notes

- Convergence is single-source because CoSAI's agent controls are a draft framework in a working repository and no second implementation of a publish-approval control is shown here, so the standards route does not apply.
- No lab run this repo cites touches this family, so the frontmatter carries no `measurement-claims`.
- The turn-on order stated in the summary (sharing first because it is cheap, then connectors, then credentials) is my practitioner judgement, Tier D, dated 2026-11-10; the bullet list itself follows the signal order in `routing.yaml`.
- The companion pages are named by file rather than linked until the ai-config-pointers set has a public address; they are linked, never copied, per Decision 12.
- The CoSAI control descriptions are paraphrased, and the KEV count was re-derived from catalogue 2026.11.09 on 2026-11-10.

## Sources

Tier A
- CoSAI secure-ai-tooling, `risk-map/yaml/controls.yaml` and `risks.yaml` at commit 622605a13fafaa2784acbdbe3f8d23ee22da4be7 (main, 2026-10-21), https://github.com/cosai-oasis/secure-ai-tooling (read 2026-11-10).
- MITRE ATLAS v2026.10, case studies CS0070 and CS0057, https://atlas.mitre.org/ (2026-10-28).
- CISA Known Exploited Vulnerabilities catalog 2026.11.09, https://www.cisa.gov/known-exploited-vulnerabilities-catalog (released 2026-11-09).

Tier B (what each feature does, vendor documentation read 2026-11-09)
- Microsoft, "Configure data policies for agents", https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-data-loss-prevention (updated 2026-10-22).
- Microsoft, "Security and governance - Microsoft Copilot Studio", https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-and-governance (updated 2026-11-05).
- Microsoft, "Limit sharing", https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-sharing-limits (updated 2026-08-14).
- Microsoft, "What are agent identities", https://learn.microsoft.com/en-us/entra/agent-id/what-are-agent-identities (updated 2026-06-15).
- Salesforce, Agentforce Implementation Guide, https://resources.docs.salesforce.com/rel1/doc/en-us/static/pdf/agentforce_implementation_customer.pdf (undated).
- ServiceNow, "Discovering and managing AI assets" (AI Control Tower, Zurich), https://www.servicenow.com/docs/r/zurich/intelligent-experiences/aict-discovering-ai-assets.html.
- Workato, "Agent Studio security", https://docs.workato.com/en/agentic/agent-studio/security, and "Genie governance", https://docs.workato.com/en/agentic/agent-studio/genie-governance/genie-governance (undated).
- AWS, CloudTrail concepts (data event resource types), https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-concepts.html.
- Google Cloud, "Agent Identity overview", https://docs.cloud.google.com/iam/docs/agent-identity-overview.

Tier C (flagged)
- Microsoft, "View audit logs for admins, makers, and users of Copilot Studio", https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-logging-copilot-studio (read through a search excerpt; the URL redirected when fetched).
- Salesforce Developers blog, "Salesforce Hosted MCP Servers Are Now Generally Available" (2026-04), and Salesforce blog, "3 Ways to Connect Agentforce Agents and Slackbot to External MCP Servers", vendor blogs.
- A ServiceNow community post (June 2026) stating that AI stewards can require approval before an MCP server is activated in any agent builder, practitioner source not vendor documentation.
