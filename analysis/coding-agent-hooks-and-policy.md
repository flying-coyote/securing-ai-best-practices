---
evidence-tier: Mixed
convergence: single-source
applies-to-signals: [coding-agent-managed-tier-absent, hook-fail-open, hooks-user-disableable]
surfaces: [S4, S5]
pins:
  - "Claude Code 2.1.321 (lab run T9)"
  - "Claude Code, Cursor, GitHub Copilot CLI, OpenAI Codex, Gemini CLI and GitLab Duo documentation as read 2026-11-09"
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-02-24
status: EMERGING
follows: "claude-code-project-best-practices analysis/safety-and-sandboxing.md and analysis/ai-tool-vetting.md (Claude Code mechanism, MCP vetting and the credential-boundary hook pattern)"
measurement-claims:
  - claim: "In 24 of 24 cells where a deny control was in force (a PreToolUse hook deny or a permissions.deny rule, placed in the user, shared-project, project-local or --settings source), 0 created the forbidden marker or leaked the fixture token; Claude Code 2.1.321 headless, one host, one model, one run per cell"
    source: "sdw-lab-benchmarks branch hub/ai-research-2026-11-09 @ T9-FIX-COMMIT-PENDING t9-pretooluse-hook-enforcement/RESULTS.md:20-22"
    date: 2026-11-10
    revalidate: 2027-02-10
  - claim: "disableAllHooks: true in .claude/settings.local.json switched off a PreToolUse hook committed in .claude/settings.json and the forbidden command ran, including when the project file pinned disableAllHooks: false (cells E1, E1b); a user-file true did the same when the project file was silent (E2) and lost only to an explicit project false (E2b)"
    source: "sdw-lab-benchmarks branch hub/ai-research-2026-11-09 @ T9-FIX-COMMIT-PENDING t9-pretooluse-hook-enforcement/RESULTS.md:24-32"
    date: 2026-11-10
    revalidate: 2027-02-10
  - claim: "Permission deny rules had no equivalent switch in the four precedence pairs measured (E3, E4, E6, E7); the managed tier and other pairs were not measured"
    source: "sdw-lab-benchmarks branch hub/ai-research-2026-11-09 @ T9-FIX-COMMIT-PENDING t9-pretooluse-hook-enforcement/RESULTS.md:24-32"
    date: 2026-11-10
    revalidate: 2027-02-10
  - claim: "With hooks disabled by a local file, the OTLP log-event stream carried no record that a hook had been configured and switched off; the only difference from a hooked session was the absent hook_registered startup event (cell E1c)"
    source: "sdw-lab-benchmarks branch hub/ai-research-2026-11-09 @ T9-FIX-COMMIT-PENDING t9-pretooluse-hook-enforcement/RESULTS.md (cell table, row E1c)"
    date: 2026-11-10
    revalidate: 2027-02-10
---

# Coding-agent hooks and policy: three enforcement shapes and which fail open

Evidence tier: Mixed, with vendor documentation of what each feature does at B, one verified lab run on one host and one version at B, peer-reviewed agent-security work at A where cited, and the policy order at D.

## Summary for the review

Most of the coding agents I read have a point where the model has chosen a tool call and the harness has not yet run it, and each vendor puts a programmable control there, but whether that control holds depends on which tier delivers it and on what happens when it fails. Hook scripts and declarative rules both run on the developer's machine, and a gateway policy is the only one of the three shapes that the laptop cannot switch off. In each of the four hook-bearing products whose failure behaviour I read, at least one failure path allows the call by default. In a lab run on Claude Code, deny rules held in every layer tested, while a hook committed to the repository was switched off by a developer's own local settings file.

- Put the agent's policy in the admin-owned managed tier and turn on the locks that make it the only source of rules and hooks. Effort M. Tier B (vendor docs).
- Express hard denies as permission rules wherever the product has rules, and keep hooks for argument-level checks that rules cannot express. Effort S. Tier B (docs and the lab run), D for the ordering.
- Set the fail-closed flag on every enforcement hook and keep a separate fail-open hook for telemetry. Effort S. Tier B.
- Alert on sessions that lack the hook-registration event, since a disabled hook leaves almost no other trace. Effort M. Tier B (one lab run).
- Verify by fleet inventory of the managed path's presence, hash and ownership, because per-machine status commands do not scale. Effort M. Tier B for the commands, D for the method.
- Where the agent calls remote MCP servers, put a default-deny gateway policy in front of them and restrict who can change its mode. Effort L. Tier B.

## Why this matters

A security team that hears "we have a PreToolUse hook" tends to hear "we have a block", and the two are different things. The hook runs as the developer, in the developer's environment, from a file the developer can often edit, and the Claude Code reference says outright that "command hooks execute shell commands with your full user permissions" (Tier B, Claude Code hooks reference, read 2026-11-09). Copilot CLI adds that its policy hooks "run on the host, outside the sandbox" (Tier B, GitHub hooks reference, read 2026-11-09). So the hook is part of the laptop's trusted computing base, and its strength is set by who can write the file it lives in and by what the harness does when it crashes or times out.

The research record does back the tool-call boundary as an enforcement point. CaMeL enforces capability policies "when tools are called" (Tier A, IEEE SaTML 2026, doi 10.1109/satml68715.2026.00040), and Progent's deterministic rules over tool names and arguments cut AgentDojo attack success from 39.9% to 1.0% (Tier B preprint, arXiv 2504.11703). But that support comes with a ceiling, since a design-patterns paper from mixed industry and academic authors judges it "unlikely that general-purpose agents can provide meaningful and reliable safety guarantees" (Tier B preprint, arXiv 2506.08837), and a coding agent with a shell is close to the general-purpose case. A pre-tool-use control confines what the agent can do, but it does not make the agent injection-proof.

## Three enforcement shapes

The products I read split into three shapes, and the split matters more than the product names (Tier D for the grouping, over Tier B docs).

- Hook scripts receive the proposed call as JSON and answer allow, deny or ask. Claude Code, Cursor, Copilot CLI, Gemini CLI and Devin Local all have them, and they see local tools such as the shell and file edits.
- Declarative rules are text the harness evaluates itself, such as Claude Code permission rules, Codex Starlark `prefix_rule` files, Gemini CLI's TOML policy engine and Copilot's cloud-agent firewall. They also see local tools, and they are evaluated by code the vendor ships rather than code you maintain.
- Gateway policy is evaluated outside the agent, between it and a remote tool, for example Amazon Bedrock AgentCore Policy in Cedar or Kong's `ai-mcp-proxy` per-tool ACLs. It is independent of the laptop, and it never sees the shell command, the file edit or a local stdio MCP server, because those never cross it.

So the first two shapes cover S4 and local S5 and run in the user's context, while the third covers the S5 hop to remote servers and nothing of S4. The two are complementary, and an organization with coding agents and remote MCP servers needs both.

The distinction between a hook and a rule is where the lab result lands. In Claude Code a hook's `allow` never overrides a `deny` or `ask` rule, and a blocking hook does override an `allow` rule, so the effective order is deny rule, blocking hook, ask rule, allow (Tier B, Claude Code permissions page, read 2026-11-09). The page itself tells you to "use the permission system, not hooks, to enforce hard allow or deny rules" (Tier B, Claude Code hooks reference). A model-evaluated hook (the `prompt` and `agent` types) is weaker again, since an LLM-based detector was among eight indirect-injection defences bypassed at over 50% success (Tier A, Zhan et al., Findings of NAACL 2025, doi 10.18653/v1/2025.findings-naacl.395), so I would count it as a signal rather than as the deny layer.

Argument-level control is where the shapes differ most, and it matters, because on AgentDojo a tool-name allowlist left 99 of 609 attack sinks open while an argument-exact allowlist left 1 of 609 (Tier B preprint, Ajar, arXiv 2609.26900, Table 6). Claude Code hooks can read and rewrite `tool_input`, but a settings-file rule can name an MCP server or tool and not a parameter; Gemini CLI's policy engine matches `argsPattern` against the arguments' JSON; Codex splits linear `bash -c` scripts and evaluates anything with redirection or substitution whole; AgentCore's Cedar conditions reach tool input parameters because its schema is generated from the tool definitions (Tier B, each vendor's docs, read 2026-11-09).

## Managed tiers and failure defaults

Claude Code, Copilot CLI, Cursor and Gemini CLI each document a tier users cannot override and name its OS path, and Codex delivers `requirements.toml` through an MDM profile, a cloud-managed workspace or a system file (Tier B, vendor docs and admin pages, read 2026-11-09). GitLab Duo has no hook tier that I found, and its admin levers for agents are a group switch for external MCP tools and a registry block that is a denylist, while per-session tool approval lives in a user-writable `mcp.json` (Tier B, GitLab MCP clients page, read 2026-11-09). The table below is the part a review should print with its date, because these defaults move between releases.

| Platform family | Setting | Default | Where the record lands | last-checked |
|---|---|---|---|---|
| Claude Code | PreToolUse hook timeout (`onFailure`) | Does not block; `onFailure: "block"` needs v2.1.295 or later | Debug log; OTel `claude_code.tool_decision` with `source: hook` | 2026-11-09 |
| Claude Code | `disableAllHooks` set outside the managed tier | Honoured for user, project and local hooks; cannot disable managed hooks | No decision record; T9 saw only a missing `hook_registered` event | 2026-11-09 |
| Claude Code | `allowManagedHooksOnly`, `allowManagedPermissionRulesOnly` | Unset | `/status` and `claude doctor` per machine; OTel `managed_settings_resolved` at startup | 2026-11-09 |
| Claude Code | `allowedHttpHookUrls` | Merges across settings files, so it pins hook URLs only together with `allowManagedHooksOnly` | None | 2026-11-09 |
| Cursor | Hook failure (crash, timeout, unexpected exit) | Fail-open unless `failClosed: true`; fails closed on invalid JSON; dashboard hooks accept neither `failClosed` nor `matcher` | Hooks output channel; audit log carries no prompts or tool output | 2026-11-09 |
| Cursor | Precedence across Enterprise, Team, Project and User hooks | Deny wins over ask over allow regardless of source | As above | 2026-11-09 |
| GitHub Copilot CLI | `preToolUse` failure | Command hooks fail closed; HTTP hooks fail open; "Timeouts are fail-open for every event, including `preToolUse` and admin-deployed policy hooks" | No central decision log named | 2026-11-09 |
| GitHub Copilot CLI | Policy hooks in `policy.d` or HKLM | Need elevated install; not disabled by `disableAllHooks` | Hook output only | 2026-11-09 |
| Gemini CLI | Hook exit other than 0 or 2 | Non-fatal warning; 60-second default timeout | stderr | 2026-11-09 |
| Gemini CLI | Admin policy directory | Ignored unless root-owned and not group- or world-writable | Not described | 2026-11-09 |
| OpenAI Codex | `[features] hooks = true` in `requirements.toml` | Unset; pins hooks on against a user turning them off | Hook output; opt-in OTel `codex.tool_decision` | 2026-11-09 |
| GitLab Duo | Per-session MCP tool approval | On; `"approvedTools": true` in a user-writable file makes it permanent | None stated | 2026-11-09 |
| Amazon Bedrock AgentCore | Policy engine mode | `LOG_ONLY` or `ENFORCE`; `bedrock-agentcore:UpdateGateway` can change it with no separate condition key | CloudWatch (field list not read) | 2026-11-09 |

The reason vendors default open is usability, since a broken hook should not brick the agent, and the cost is that an enforcement hook can be defeated by making it slow. I found no paper or bench that measures this under induced latency (see Gaps), so the risk rests on the documented defaults rather than on an observed bypass.

## What the lab measured

Run T9 put PreToolUse hook denies and `permissions.deny` rules into each settings source of Claude Code 2.1.321 in headless mode and scored each cell by whether a forbidden marker file appeared and whether a fixture token leaked, across 37 invocations on one host with one model and one run per cell, for about USD 0.05 in spend (Tier B measured; sdw-lab-benchmarks branch hub/ai-research-2026-11-09, t9-pretooluse-hook-enforcement/RESULTS.md, verified with fixes). A second agent re-ran 22 of the cells on a fresh rig directory using the same method, and all 22 matched on marker, token and decision fields; its seven required fixes corrected wording and three factual details, and none reversed an enforcement finding (same folder, VERIFICATION.md).

In the 24 cells where a deny control was in force, none created the marker or leaked the token. The marker appeared only where a hook had been switched off by `disableAllHooks` and in the allow cells built to show it. The finding I would put in front of a platform team is that switch, because `disableAllHooks: true` in a developer's `.claude/settings.local.json` disabled the hook in the committed `.claude/settings.json` and the forbidden command ran, and it still ran when the project file pinned `false`, because local outranks project. A deny rule had no such switch in the four precedence pairs measured, though the managed tier was not measured at all, so this holds for those pairs and not as a general rule.

Two record-keeping results follow from the same run. With hooks disabled, the OTLP log stream carried no record that a hook had been configured and switched off, and the only difference from a hooked session was the missing `hook_registered` startup event, so a collector has to alert on an absence. And when a subagent's call was denied, the parent's stream-json carried the denial in the first of two `result` events and not in the final one, so a consumer that reads only the last line misses it.

## A policy order, product-neutral

This is my ordering (Tier D for the order), and it assumes nothing about which products an organization runs. The order follows a simple dependency: the first step is what makes the rest enforceable, and the telemetry steps are what make verification possible.

1. Lock the tier before writing rules. In Claude Code that means managed `allowManagedPermissionRulesOnly`, `allowManagedHooksOnly` and `permissions.disableBypassPermissionsMode: "disable"`, delivered by MDM profile, HKLM or server-managed settings; the equivalents are Codex `requirements.toml`, Copilot CLI `policy.d`, Gemini CLI's admin directory and Cursor's system `hooks.json` (Tier B). The managed-settings page notes that a local administrator can edit the managed source, which is why MDM redeploys on a schedule.
2. Deny destructive and credential-bearing calls as rules, starting with reads of `.env*`, `~/.ssh` and cloud credential files and of the agent's own settings and hooks paths, writes to `.git/hooks` and shell startup files, force pushes, package publishes and egress outside an allowlist. Deterministic rules have design support (Tier A, CaMeL) with a utility cost, CaMeL refusing 41.5% of entitled calls in one external run (Tier B preprint, Ajar, Table 8).
3. Allowlist MCP servers by URL or command rather than by name alone, and lock the allowlist (Tier B for the keys each vendor documents). Vetting the servers themselves is outside this document.
4. Turn the sandbox on and make it admin-required, recording that hooks and local MCP servers run outside it (Tier B). Budget for it, since strict hardening cost coding agents up to 18.3 points of task success and inflated cost by up to 167.3% on Terminal-Bench 2.1 (Tier B preprint, arXiv 2608.02670).
5. Add one fail-closed enforcement hook where rules cannot express the check, kept local and dependency-free, with tests that replay recorded `tool_input` payloads.
6. Add a separate fail-open telemetry hook that posts every call to a collector you own, with its URL pinned.
7. Lock native telemetry in the managed tier, because a repository file can otherwise set an exporter selector to `none` (Tier B, Claude Code monitoring page).
8. At a gateway, default-deny in `ENFORCE` mode and restrict who holds the permission that changes the mode.
9. Verify by inventory, checking managed-path presence, hash and ownership per machine and joining that to agent telemetry, since a machine that runs an agent and emits no decision events is either unmanaged or has a signal switched off.

## What this does not mean

It does not mean hooks are useless. A hook is the only place most products let you check an argument, and a fail-closed hook delivered from the managed tier is a reasonable control, since the lab result is about a hook delivered from the project tier with no lock. It also does not mean deny rules are robust in general. T9 measured the layers and deliberately did not probe the matcher, and the permissions page itself documents prefix fragility around absolute paths, `sh -c` and variables. Blocked agents also tend to build workarounds rather than stop, with workaround construction making up 97% of the cost mechanism in one study (Tier B preprint, arXiv 2608.02670), so a prefix rule faces an adaptive caller even when nobody is attacking. And a written instruction is not a control at all: across 481 public CLAUDE.md files, about 4% to 16% of security rules had a matching built-in control (Tier B preprint, arXiv 2608.23550).

The lab run is one version of one product. Cursor, Copilot CLI, Gemini CLI and Codex were read and not measured, so every row about them in the table above is what the vendor documents, at Tier B, and nothing more.

## Gaps

- **Gap: G17, independent verification of T9**. Closed on one host: a second agent re-ran 22 of the 37 cells on a fresh rig directory with the same version and method and every one matched, which settles reproducibility on that machine and not across hosts, versions or interactive mode. **Needs**: the T9 cells re-run on a second host against a later Claude Code release, including interactive mode and the `PermissionRequest` hook.
- **Gap: managed tier unmeasured**. No lab run has put `allowManagedHooksOnly` or `allowManagedPermissionRulesOnly` in force and tried the lower-tier overrides against it. **Needs**: a T9 extension in a disposable VM where the managed path can be written, scoring the same marker and token cells.
- **Gap: fail-open under latency**. No paper or bench measures whether an enforcement hook that times out allows the call in practice, per product, with and without the fail-closed flag. **Needs**: a bench that delays a deny hook past its timeout in Claude Code, Cursor, Copilot CLI and Gemini CLI and records whether the call ran.
- **Gap: other agents unmeasured**. The precedence and switch-off findings come from Claude Code only. **Needs**: T9-style cells for Cursor, Copilot CLI, Gemini CLI and Codex, including whether Copilot CLI and Devin Local honour a `.claude/settings.json` hook they read.
- **Gap: rule-parser divergence**. Nothing tests how the same compound or wrapped command is split by each product's prefix-rule parser. **Needs**: a differential harness that feeds identical command strings to each product's rule tester or evaluator and publishes only the divergence table.
- **Gap: gateway decision records**. AgentCore says every enforcement decision is logged to CloudWatch, and I did not read the field list. **Needs**: a read of the logged fields, or a captured record from a test gateway.

## Notes

- 2026-11-10: the T9 citations are meant to point at the commit on branch hub/ai-research-2026-11-09 that carries the seven verifier fixes, and the `T9-FIX-COMMIT-PENDING` placeholder stands in for that hash until it exists. The branch head as of this date predates those fixes and serves the unfixed text, so it is not the cited source.
- 2026-11-10: the policy order and the three-shape grouping are my judgement (Tier D) and are expected to move as the gaps above close.
- 2026-11-10: the GitLab Duo row describes what the MCP clients page says about approvals; the page "doesn't describe allowlisting specific servers", so I have recorded the absence rather than inferred a feature.
- The canon for the Claude Code mechanism, MCP vetting and the credential-boundary hook is [safety-and-sandboxing.md](https://github.com/flying-coyote/claude-code-project-best-practices/blob/master/analysis/safety-and-sandboxing.md) and [ai-tool-vetting.md](https://github.com/flying-coyote/claude-code-project-best-practices/blob/master/analysis/ai-tool-vetting.md) in claude-code-project-best-practices; this document keeps the cross-vendor comparison and the lab result those do not carry.

## Sources

Tier A

- Debenedetti et al., "Defeating Prompt Injections by Design" (CaMeL), IEEE SaTML 2026, https://doi.org/10.1109/satml68715.2026.00040
- Zhan et al., adaptive attacks on indirect prompt injection defences, Findings of NAACL 2025, https://doi.org/10.18653/v1/2025.findings-naacl.395

Tier B, vendor documentation of what a feature does (all read 2026-11-09)

- Claude Code: hooks https://code.claude.com/docs/en/hooks, permissions https://code.claude.com/docs/en/permissions, settings https://code.claude.com/docs/en/settings, managed settings https://code.claude.com/docs/en/managed-settings, settings reference https://code.claude.com/docs/en/settings-reference, sandboxing https://code.claude.com/docs/en/sandboxing, monitoring https://code.claude.com/docs/en/monitoring-usage, headless https://code.claude.com/docs/en/headless
- Cursor hooks, https://cursor.com/docs/agent/hooks; compliance and monitoring, https://cursor.com/docs/enterprise/compliance-and-monitoring
- GitHub Copilot hooks reference, https://docs.github.com/en/copilot/reference/hooks-reference; coding agent firewall, https://docs.github.com/en/copilot/how-tos/agents/copilot-coding-agent/customizing-or-disabling-the-firewall-for-copilot-coding-agent
- OpenAI Codex approvals and security, https://learn.chatgpt.com/docs/agent-approvals-security; rules, https://learn.chatgpt.com/docs/agent-configuration/rules; managed configuration, https://learn.chatgpt.com/docs/enterprise/managed-configuration.md
- Gemini CLI policy engine, https://geminicli.com/docs/reference/policy-engine (updated 2026-04-30); hooks, https://geminicli.com/docs/hooks/reference/ (updated 2026-04-10); enterprise, https://geminicli.com/docs/cli/enterprise/ (updated 2026-06-16)
- GitLab MCP clients, https://docs.gitlab.com/user/gitlab_duo/model_context_protocol/mcp_clients/
- Amazon Bedrock AgentCore policy, https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/policy.html; enforcement modes, https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/policy-enforcement-modes.html
- Kong `ai-mcp-proxy` per-tool ACLs, https://developer.konghq.com/plugins/ai-mcp-proxy/examples/passthrough-listener-tool-acls/

Tier B, measured and preprints

- sdw-lab-benchmarks, branch hub/ai-research-2026-11-09, t9-pretooluse-hook-enforcement/RESULTS.md and VERIFICATION.md (verdict VERIFIED-WITH-FIXES), https://github.com/flying-coyote/sdw-lab-benchmarks
- Shi et al., Progent, arXiv 2504.11703
- Beurer-Kellner et al., design patterns for securing LLM agents, arXiv 2506.08837
- Sharma et al., Ajar, arXiv 2609.26900
- Davidovich et al., Permission Denied, arXiv 2608.02670
- Yan, security rules in CLAUDE.md versus built-in controls, arXiv 2608.23550
