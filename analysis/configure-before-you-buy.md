---
evidence-tier: Mixed
convergence: single-source
applies-to-signals: [ai-tool-intake-absent, incumbent-inventory-absent]
surfaces: [S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12, S13]
pins:
  - "CoSAI secure-ai-tooling 622605a1"
  - "CISA AA23-278A 2023-10-05"
  - "CISA BOD 25-01 2024-12-17"
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-03-31
status: EMERGING
---

# Configure before you buy: entitled, available, enabled, and the five-state audit

Evidence tier: Mixed. Tier A for the peer-reviewed work on configuration error, ineffective deployment and alarm quality; Tier B for agency guidance (NSA and CISA, CISA BOD 25-01, CIS) and for vendor documentation of what a feature does and its default; Tier C, bias flagged, for every vendor-published study of configuration debt or unused licences; Tier D for the five-state scoring rule, the decision order and the 80 to 90 percent configure-first view, which is the author's practitioner judgement and is not measured anywhere.

## Summary for the review

Before an organization buys anything for AI security, it should find out what it already pays for that would see its AI use if someone turned it on, scoped it, exported it and gave it an owner, because the public record says the normal state of an owned control is default and unconfigured, and a new product bought into that habit tends to join it.

- Build a per-platform-family list of the AI governance features the organization is entitled to, which are available at its licence tier (GA or preview, with the date read), and which are enabled in its own tenant, read from the licence portal and the admin console rather than from memory. Effort M. Tier B for the agency precedent; Tier D for the three-column shape.
- Audit each enabled feature through five states (enabled, scoped, exported, alerted, owned) and grade it at the highest state where every earlier state is a yes. Effort M. Tier A for why scope, alert tuning and ownership each fail on their own; Tier D for the scoring rule.
- Turn on the content channels the AI platforms ship switched off, and export each record to a store the organization owns before the vendor's retention window closes. Effort S per feature. Tier B (vendor documentation; see the default-state table, as of 2026-11-09).
- For a small or mid-sized organization, aim for enabled, scoped and exported with a named quarterly review, keep "alerted" for the few records that matter most, and record "accepted" as a disposition when a gap is a deliberate choice. Effort S. Tier D.
- Decide in the order turn on, evaluate, buy, build, and put two preconditions in front of any build: a review body that can decline it, and a core platform the organization has already accepted long-term lock-in to. Effort S to decide. Tier D.
- Make the AI tool intake path run this check, so a request for a new tool first asks whether an owned feature already reaches the need. Effort S. Tier D.

## Why this matters

The question "what should we buy for AI security" has a prior question that many teams skip, which is what the platforms they already license now do for AI. Over 2025 and 2026 the suites, identity providers, clouds, endpoint agents, code platforms and SSE products shipped AI-specific features such as AI app catalogues, endpoint agent inventories, agent identity types and agent audit records, and many of those shipped into an admin centre the AI owner does not look at, or default to off, or produce a record that stays in the vendor's store and never reaches a defender (Tier B, vendor admin documentation read 2026-11-09; the per-product detail will be in the forthcoming ai-config-pointers set, Decision 12). So licence-sheet coverage and tenant coverage are two different numbers, and the distance between them is a configuration gap before it is a product gap.

In my own earlier operational work, something like 80 to 90 percent of what I needed for a given problem was already present in platforms we licensed, and the vast majority of what we had was unconfigured or misconfigured. That is a practitioner view, offered as a general observation, and it is carried here at Tier D (marker dated 2026-11-10; see Notes). I have found no survey that measures it, and I haven't found anything in the public record that contradicts it either, which is why the next section lays out what the record does measure and keeps those sources apart rather than adding them up.

## What the public record measures about owned controls

The sources that get quoted for "misconfiguration is the top risk" measure different things, so I'd read each for what it actually counts.

Assessments of real networks come first, because they are observations rather than surveys. The NSA and CISA red and blue teams put "default configurations of software and applications" first in their list of the ten most common misconfigurations, with "default configurations of systems, services, and applications can permit unauthorized access or other malicious activity" as the explanation, and they list insufficient internal network monitoring third, where "some organizations do not optimally configure host and network sensors for traffic collection and end-host logging" (Tier B, AA23-278A, 2023-10-05). The advisory's own caveat is that many of the assessments were of Windows and Active Directory environments, so it describes enterprise networks and says nothing about AI platforms directly, though item 1 describes the AI-platform logging defaults in the table below closely and item 3 is the export state of the audit in the government's words. The closest peer-reviewed analogue is a hands-on assessment of 61 organizations that found more than 93 percent vulnerable, attributed to persistent misconfiguration and the absence of systematic hardening (Tier A, Álvarez et al., Computer Networks 2026, abstract read).

The peer-reviewed support for "deployed but not effective" holds where the thing measured is a whole perimeter or policy. Wool found 42 percent of 84 corporate firewall rule-sets let Microsoft services in from outside (Tier A, IEEE Internet Computing 2010), and Weichselbaum and colleagues found that 99.34 percent of hosts that deployed Content Security Policy got no protection against XSS from it (Tier A, CCS 2016), which is the cleanest case I know of a control that was switched on and did nothing because its scope and parameters were wrong. Where the unit is a single artefact the picture is milder, a minority of infrastructure-as-code scripts and Kubernetes manifests carrying a finding (Tier A, Rahman et al., TOSEM 2021 and 2023), so misconfiguration is common and persistent there rather than the norm.

On why settings go wrong, Yin and colleagues' study of 546 real configuration errors found most were mistakes in setting parameter values rather than compatibility or component problems, a 70.0 to 85.5 percent range per system that comes from the authors' slides rather than the abstract and that I wouldn't present as replicated (Tier A, SOSP 2011). The current empirical anchor uses a different taxonomy and makes the point more directly: of 772 real misconfigurations drawn from 168,054 user-raised issues, 33.55 percent had semantic misinterpretation of a setting as the root cause, and 43.24 percent of those deviated silently rather than raising an error (Tier A, Liu et al., Empirical Software Engineering 2026), so a feature can be on and wrong with no signal. That is why the audit reads scopes and parameter values, not only an on/off bit.

On alerting, Alahmadi, Axon and Martinovic surveyed 20 practitioners and interviewed 21 across seven SOCs, and found that most of what analysts call false positives are benign triggers, alarms that fire correctly on behaviour that is legitimate in that environment (Tier A, USENIX Security 2022; the "99%" in the title is a participant's phrase, not a measured rate). Uetz and colleagues then showed that at least 44 percent of 292 public Sigma process-creation rules could be evaded with straightforward changes (Tier A, USENIX Security 2024), so a single planted event proves a rule fires rather than that it holds. On ownership, Dietrich and colleagues recommended clear responsibility structures, a four-eyes principle and blameless postmortems after studying operators' own view of security misconfiguration (Tier A, CCS 2018, recommendations read through a university summary), and Xu and colleagues argue that configuration errors get blamed on users when the interface shares the blame (Tier A, SOSP 2013, abstract read); both report perceived causes rather than a measured attribution.

The nearest thing to a share is a controls model. CIS's Community Defense Model v2.0 found that Implementation Group 1 safeguards defend against 77 percent of the ATT&CK (sub-)techniques used across the top five attack types and 74 percent framework-wide, and called Safeguard 4.1, a secure configuration process, "a linchpin Safeguard for all five attack types" (Tier B, CIS, 2021), which is a model over technique mappings rather than an incident count, from a body with nothing to sell.

Vendor telemetry points the same way, with the bias flag that each publisher sells the fix and measures its own customers. Datadog found 49 percent of EC2 instances enforce IMDSv2 while 82 percent had used only IMDSv2 for two weeks, a free, safe control left off on half the fleet (Tier C, State of Cloud Security 2025). Orca, across more than 1,200 customer organizations in Q2 2026, found 80 percent of SageMaker organizations running with all default settings enabled and 57.1 percent of Bedrock organizations with no guardrails configured (Tier C, 2026 State of AI Security Report). Zylo put 53 percent of SaaS licences unused or underused (Tier C, 2025 SaaS Management Index). I found nothing peer-reviewed that measures the unused half of the premise, so it rests on Tier C licence data.

The precedent for doing the audit at all is a mandate. CISA's BOD 25-01 required federal civilian agencies to inventory their Microsoft 365 tenants, deploy CISA's assessment tool and implement the mandatory SCuBA baselines by 2025-06-20, with Google Workspace following by 2026-12-31 (Tier B, CISA, issued 2024-12-17). Its tool, ScubaGear, reads tenant settings through the admin APIs and evaluates them against per-baseline policy (Tier B, CC0-licensed), and Microsoft Secure Score does the vendor-side version, showing recommendations regardless of licence edition, which makes it a list of what a tier upgrade would add (Tier B for what it does). That a directive was needed says something about how rarely the audit happens unprompted.

Taken together this is a consistent direction rather than a number, in which owned controls sit at default and entitled features sit unused, and none of it is the 80 to 90 percent figure, which the review should never imply.

## The method: inventory, audit, grade, decide

Step one is the inventory, one row per platform family rather than per product, because the review assumes no organization runs any named product. The three columns fail separately, so they stay separate.

| Column | Question | Where the answer lives |
|---|---|---|
| Entitled | Which licence tier or add-on is held, with its renewal date? | Licence portal, contract, reseller statement |
| Available | Which AI-relevant features does that tier include, GA or preview, read on what date? | Vendor documentation and release notes |
| Enabled | Is the feature on in this tenant, as of what date? | The admin console or its read-only API |

A recurring licence pattern decides more rows than the features do. The admin audit trail of settings and seats tends to ship in every tier, while the content channel (prompt, tool call, answer) is a separate decision with its own toggle or licence line, often at the top tier and often off (Tier B, vendor documentation read 2026-11-09). So "we have the assistant's logs" needs the follow-up question of which of the two. The inventory should also list what no owned feature reaches by position, such as local models after download, stdio MCP servers and agents with no user session, so that it does not create false hope about those rows (Tier D, author's reading).

Step two is the audit. An enabled feature is not yet a control, and each state below is a place where the record can stop before it reaches a defender. They form a pipeline, since a feature that fails at state two has nothing to offer states three to five.

1. Enabled: the toggle, policy or diagnostic setting exists and is on, with the date confirmed.
2. Scoped: it covers the users, devices, accounts, regions and endpoints that matter, and its parameters are right, which is where Content Security Policy and IMDSv2 both failed.
3. Exported: the record leaves the vendor's retention window and lands in a store the organization owns, with retention set on purpose.
4. Alerted: a detection or a review consumes the record, and it has been exercised against a planted event, ideally with a variant, on a known date.
5. Owned: a named role owns the configuration and the response, recorded somewhere a successor will find it.

The grade is the highest state at which every earlier state is a yes, so a feature that is exported but not scoped grades at state 1 (Tier D). That rule looks harsh, and I think it should, because the common finding is a record that exists for some users on some endpoints and sits in a 30-day vendor window, and calling that "logged" is how a coverage view turns into a brochure. The worksheet planned for the forthcoming ai-config-pointers set fills these same five states from read-only tenant APIs, which is why "accepted" is a disposition column here rather than a sixth state.

For a small or mid-sized organization, the realistic target is enabled, scoped and exported plus a named quarterly review, with "alerted" reserved for the few records whose absence would stall an investigation, and with any gap the organization chooses to live with written down as "accepted, reviewed quarterly" (Tier D). BOD 25-01's quarterly reporting cadence is a reasonable default for that review window.

Step three grades the result onto the CoSAI component map at commit `622605a1`, so that configuring a feature visibly moves a cell. Nothing entitled reaches a component: blind. Entitled or enabled but not through all five states: claimed, drawn on the map and never counted. All five states yes: documented. A planted event produced the record or alert in the organization's own store on a dated run: verified. A regression at any state drops the cell back to claimed, and a lapsed entitlement drops it to blind (Tier D, the grading scheme). Read that way the map yields a turn-on list (held but unaudited), a test list (audited, never planted) and a blind list, which holds the only components where buying or building is even a candidate.

Step four is the decision order, turn on, evaluate, buy, build, because each step is cheaper, faster to reverse and less expensive organizationally than the next, so a cell moves on only when the current step has been shown not to reach it (Tier D). Evaluation means a time-boxed planted-event test in the organization's own tenant, since a preview with no GA date is a vendor promise, and a purchase sits on the map as claimed until that test runs. A build carries the cost `analysis/build-buy-and-the-high-priest.md` describes, and the better alternative is often the skipped turn-on list. The one build I'd expect to pass the two preconditions in many environments is an ingest transform that normalizes identity, model and tool name into typed columns in a store the organization already runs, because it is glue on an existing core system rather than a new one.

## Default-state table: the content channels that ship off

These are the vendors' published defaults for the product, not any tenant's configuration, and the review prints "as of" the row's date beside anything drawn from it. The fuller version of each row (console path, licence verbatim, route-to destination) will sit on that product's page in the forthcoming ai-config-pointers set, and the rows will link those pages once it is public.

| Platform family | Setting | Default | Where the record lands | last-checked |
|---|---|---|---|---|
| AWS | Bedrock model invocation logging | Off; when on, covers `bedrock-runtime` and does not capture `bedrock-mantle` | CloudWatch Logs or S3, as configured | 2026-11-09 |
| AWS | CloudTrail Event history | On for management events | Vendor-held, past 90 days; longer needs a trail | 2026-11-09 |
| Google Cloud | Vertex AI Data Access audit logs | Off | Cloud Logging | 2026-11-09 |
| Google Cloud | Vertex AI request-response logging | Off; Pre-GA terms; no caller-identity column | BigQuery table, sampled | 2026-11-09 |
| Google Cloud | Gemini Enterprise usage audit logs, prompt-and-response setting | Content elided until an admin enables it | Cloud Logging `_Default` bucket, 30 days unless changed | 2026-11-09 |
| Azure | Azure OpenAI and Foundry diagnostic settings | Off until a diagnostic setting is created | Log Analytics, storage or Event Hubs, as configured | 2026-11-09 |
| Microsoft 365 | Purview Audit `CopilotInteraction` | On where auditing is on; the record carries no prompt text | Unified audit log, 180 days on Audit (Standard) | 2026-11-09 |
| Coding agents | Claude Code OpenTelemetry export, and its separate content flags | Opt-in | The collector the organization names | 2026-11-09 |
| Coding agents | Cursor audit log and OTel export | Enterprise plan only; audit log excludes prompts and agent output | Vendor-held, retention not stated; Admin API queries default to 7 days and span at most 30 | 2026-11-09 |
| Code platform | GitHub Copilot audit log | On for plan, policy and seat changes; no local client prompts | GitHub audit log, 180 days | 2026-11-09 |

## What this does not mean

It does not mean owned tools cover AI, since some components sit outside the reach of any incumbent feature by position and configuration cannot move a cell no owned feature can see. It does not mean a feature switched on is a working control either, since Content Security Policy shows that deployment with the wrong parameters changes nothing, and documented means the feature exists, not that it works. Nor are the Tier C figures from Datadog, Orca or Zylo rates for any organization, since each describes a vendor's own customers. And it does not apply the same way to every profile: an organization that self-hosts models for residency reasons, or that has already chosen a gateway, may reasonably skip the sizing argument, and the review accepts that override (see `analysis/decision-sequence.md`). If a measured pass found that well under half of the components an organization needs are reachable at documented or better without a purchase, the order would still hold, but the turn-on step would carry less weight than this document gives it.

## Gaps

- **Gap: G24, the configure-first share**. I found no published measurement of what fraction of the AI-security capability an organization needs is already present in what it owns, configured or not, so the 80 to 90 percent view stays Tier D and the review never prints it as a figure. **Needs**: a published worksheet in the five-state shape that practitioners fill for their own tenants and contribute by category, aggregated once enough rows exist; a pre-registered reference-tenant pass in sdw-lab-benchmarks (inventory, five-state audit, components reachable at documented or better before and after configuration, no purchase) would be a single-host precursor and would be labelled as one.
- **Gap: population distribution of configuration audits**. There is no public distribution of Secure Score values or SCuBA baseline pass rates, so the configuration-debt premise rests on vendor telemetry rather than a population measure. **Needs**: Microsoft or CISA publishing an anonymized distribution, or aggregated ScubaGear output contributed by category.
- **Gap: loss along the five states**. Studies measure one state at a time and none follows a control end to end to report where the record stops. **Needs**: a study tracking a sample of enabled features through all five states in real tenants.
- **Gap: does turning on change outcomes**. No before-and-after study of enabling owned controls in an enterprise was found. **Needs**: a controlled comparison, or VCDB records coded for configuration preconditions.

## Notes

- 2026-11-10, judgement marker: the 80 to 90 percent configure-first view is the author's practitioner judgement, carried at Tier D, never scored and never printed as a figure. It is one of the ordering perspectives that live in `analysis/decision-sequence.md` and order actions within a priority band without raising one (DECISIONS.md Decision 15 and Decision 3); recording the tier choice here follows Decision 16.
- Convergence is single-source because no standard prescribes this practice: BOD 25-01 mandates a tenant configuration audit against SCuBA baselines for federal Microsoft 365 and Google Workspace, which is a precedent for step two, not a prescription of the five-state AI audit.
- The Verizon DBIR is not cited, because its misconfiguration share within the error pattern was found only in secondary coverage. Orca's figures are per organization, as its methodology page states.
- "Accepted" is a disposition column rather than a sixth audit state, so the five-state shape stays the same data contract as the ai-config-pointers worksheet.
- The ai-config-pointers set is a separate repository, the platforms layer beside this one (Decision 12), and it is not yet public, so this document calls it forthcoming and carries no link to it; its pages will be linked, never copied, once it has a public address.
- The default-state rows were checked on 2026-11-09; vendor pages change monthly, hence revalidation in under five months.

## Sources

Tier A, peer-reviewed and standards

- Yin, Ma, Zheng, Zhou, Bairavasundaram and Pasupathy, "An Empirical Study on Configuration Errors in Commercial and Open Source Systems", SOSP 2011, https://doi.org/10.1145/2043556.2043572 (parameter-mistake range from the authors' slides).
- Liu, Zhou, Zhang et al., "Rethinking Software Misconfigurations in the Real World: An Empirical Study and Literature Analysis", Empirical Software Engineering 2026, https://doi.org/10.1007/s10664-026-10892-6 (arXiv 2412.11121v4, read in full).
- Dietrich, Krombholz, Borgolte and Fiebig, "Investigating System Operators' Perspective on Security Misconfigurations", CCS 2018, https://doi.org/10.1145/3243734.3243794.
- Xu, Zhang, Huang et al., "Do Not Blame Users for Misconfigurations", SOSP 2013, https://doi.org/10.1145/2517349.2522727 (abstract).
- Alahmadi, Axon and Martinovic, "99% False Positives: A Qualitative Study of SOC Analysts' Perspectives on Security Alarms", USENIX Security 2022, https://www.usenix.org/conference/usenixsecurity22/presentation/alahmadi.
- Uetz, Herzog, Hackländer, Schwarz and Henze, "You Cannot Escape Me: Detecting Evasions of SIEM Rules in Enterprise Networks", USENIX Security 2024, https://arxiv.org/abs/2311.10197.
- Wool, "Trends in Firewall Configuration Errors: Measuring the Holes in Swiss Cheese", IEEE Internet Computing 2010, https://doi.org/10.1109/mic.2010.29.
- Weichselbaum, Spagnuolo, Lekies and Janc, "CSP Is Dead, Long Live CSP!", CCS 2016, https://doi.org/10.1145/2976749.2978363.
- Álvarez, Nuño, Bulnes et al., "Network Security Misconfigurations in Spanish Organisations: An Empirical Study", Computer Networks 2026, https://doi.org/10.1016/j.comnet.2026.112631 (abstract).
- Rahman et al., "Security Smells in Ansible and Chef Scripts", ACM TOSEM 2021, https://doi.org/10.1145/3408897 (20.5 to 32.9 percent of scripts with a finding); "Security Misconfigurations in Open Source Kubernetes Manifests", ACM TOSEM 2023, https://doi.org/10.1145/3579639 (15.7 to 20.2 percent of manifests).
- CoSAI, secure-ai-tooling `risk-map/yaml/components.yaml` at commit `622605a1`, https://github.com/cosai-oasis/secure-ai-tooling (component vocabulary).

Tier B, agency guidance, practitioners and vendor documentation of what a feature does

- NSA and CISA, "NSA and CISA Red and Blue Teams Share Top Ten Cybersecurity Misconfigurations", AA23-278A, 2023-10-05, https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-278a (re-read 2026-11-10).
- CISA, BOD 25-01 implementation guidance, issued 2024-12-17, https://www.cisa.gov/news-events/directives/bod-25-01-implementation-guidance-implementing-secure-practices-cloud-services.
- CISA, ScubaGear, https://github.com/cisagov/ScubaGear.
- Center for Internet Security, "CIS Introduces v2.0 of the CIS Community Defense Model", https://www.cisecurity.org/insights/blog/cis-introduces-v2-0-of-the-cis-community-defense-model (re-read 2026-11-10).
- Microsoft Learn, "Microsoft Secure Score", ms.date 2026-03-07, https://learn.microsoft.com/en-us/defender-xdr/microsoft-secure-score.
- AWS documentation, read 2026-11-09: https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html, https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html.
- Google Cloud documentation, read 2026-11-09: https://docs.cloud.google.com/vertex-ai/docs/general/audit-logging, https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/request-response-logging, https://docs.cloud.google.com/gemini/enterprise/docs/set-up-usage-audit-logs, https://docs.cloud.google.com/logging/quotas.
- Microsoft Learn, read 2026-11-09: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/monitor-openai (ms.date 2025-11-06), https://learn.microsoft.com/en-us/purview/audit-copilot (ms.date 2026-08-26), https://learn.microsoft.com/en-us/purview/audit-solutions-overview (ms.date 2026-05-18).
- Anthropic, "Monitoring" (Claude Code), https://code.claude.com/docs/en/monitoring-usage (read 2026-11-09).
- Cursor, "Compliance and Monitoring", https://cursor.com/docs/enterprise/compliance-and-monitoring (read 2026-11-09).
- GitHub Docs, Copilot "Review audit logs" (read 2026-11-09).
- ai-config-pointers (Decision 12), the forthcoming platforms-layer repository: per-product pages for the platforms in the default-state table, an overlooked-settings list and a by-component view; not yet public, so not linked here.

Tier C, vendor-published studies, bias flagged (each publisher sells the remediation and measures its own customers)

- Datadog, "State of Cloud Security 2025", https://www.datadoghq.com/state-of-cloud-security/.
- Orca Security, "2026 State of AI Security Report", https://orca.security/wp-content/uploads/2026/07/2026-State-of-AI-Security-Report.pdf.
- Zylo, "2025 SaaS Management Index", released 2025-01-16, https://zylo.com/news/2025-saas-management-index.
