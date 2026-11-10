---
evidence-tier: Mixed
convergence: single-source
applies-to-signals: [saas-ai-toggles-unreviewed, vendor-training-optout-unknown, ai-subprocessor-review-absent, vendor-terms-unknown]
surfaces: [S1, S2, S6]
pins: []
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-02-17
status: EMERGING
---

# SaaS-embedded AI and vendor terms: what turned on, what it does with your data, what you can switch off

Evidence tier: Mixed. What each feature does and what each default is comes from the vendor's own admin and terms documentation (B); statements about how well a vendor's guardrail or masking works are vendor efficacy claims (C, flagged where they appear); the processor and third-party obligations come from regulation and standards (A); the review cadence, the three-way pattern and the questionnaire are my judgement (D).

## Summary for the review

AI inside SaaS you already pay for arrives through the vendor's release train rather than through your intake process, so the controls that matter are a recurring toggle review, the vendor's written answers on training, retention, sub-processors and residency, and a short questionnaire that turns those answers into a record you can re-check when the terms change.

- Run a toggle review of the SaaS products with the most users, starting with the office suite, the CRM, the ITSM platform, the chat tool and the data platform, and record each AI feature's state, owner and the date you checked it. Effort M the first time, S each quarter after. Tier B for what each setting does, D for the cadence.
- For each product with AI features, find the training-on-your-data statement, decide whether it is a setting, a contractual promise or an opt-out you have to request, and set or request it. Effort S per product. Tier B.
- Subscribe to each vendor's sub-processor list and treat a new model provider on it as a change you review, the way GDPR Article 28(2) already expects a processor to give notice of. Effort S. Tier A for the obligation, B for the lists.
- Check residency and capacity routing separately from the training answer, because at least two vendors in the table, Microsoft and ServiceNow, route inference to other regions or to a partner cloud under load while keeping their no-training promise. Effort S. Tier B.
- Turn on the AI content or audit record where the product has one, since in several products it is off until someone enables it. Effort S to M. Tier B.
- Send the eight-question vendor AI questionnaire below to the vendors whose answers you cannot find in public documentation, and file the replies with a date. Effort M. Tier D.

Every default in the table below carries the date it was read, and the review prints that date beside anything drawn from it.

## Why this matters

The usual intake path for a new AI tool assumes someone asks for it. Embedded AI skips that step, because the vendor turns the feature on server-side inside a product that already passed procurement, and the network sees the same SaaS domain it always saw. A CSIRO interview study of 27 Australian critical-infrastructure organisations heard that vendors "were effectively turning [features] on" in enterprise tools without a risk assessment, and that security teams had "some level of awareness ... but not a great detail" of them (Tier B, Chhetri et al., arXiv 2606.00088, preprint). I think that matches what a lot of practitioners would say if asked, though a 27-organisation interview sample in one country is a description of a pattern and not a base rate.

The three questions a team needs answered per product are what turned on, what the vendor does with the data that flows through it, and what the customer can switch off, restrict or negotiate. The first is an admin-console question, the second is a terms and sub-processor question, and the third depends on which of the two the vendor chose to make it. That last distinction carries most of the work, because a training promise that lives in a contract cannot be checked in a console, and a setting that defaults to on is a finding only if somebody looks.

There is also an obligation behind the sub-processor part that predates AI. Under GDPR Article 28(2) a processor may not engage another processor without the controller's prior specific or general written authorisation, and under a general authorisation it must tell the controller about intended additions or replacements so the controller can object (Tier A, Regulation (EU) 2016/679, Article 28(2)). When a SaaS vendor adds a model provider to serve an AI feature, that is often exactly such a change. NIST's AI RMF puts the same concern in governance terms under GOVERN 6, which asks for policies and procedures covering AI risks from third-party software, data and supply chains (Tier A, NIST AI 100-1, January 2023), and ISO/IEC 42001:2023 carries third-party and customer relationships as its own Annex A control family (Tier A).

As far as I could find, none of the SaaS products in the table has a government or consensus-body baseline written for its AI features (the CIS benchmark list I read, which was truncated at the end, has no benchmark for Salesforce, ServiceNow, Slack or Atlassian), so the vendor's admin documentation is the best guidance available, which is a weaker thing. The exception I know of is CISA's SCuBA work for Google Workspace, which ships a dedicated `gemini.md` baseline (Tier A, CISA ScubaGoggles, read 2026-11-09; not yet drawn on here, see Gaps).

## What turned on, and what you can switch off

### Three shapes a vendor default takes

Reading the vendor pages in the table, the defaults fall into three shapes, and the shape tells you what kind of action the review produces. This grouping is my reading of the documentation, Tier D, and a vendor can move between shapes in one release.

- On by default, riding an existing licence. The feature is available to users as soon as the vendor ships it, and the customer's lever is a block, an opt-out or a narrower parameter. Atlassian's per-app Rovo access, Databricks' partner-powered AI features, ServiceNow's Now Assist data sharing and overflow processing, and Snowflake's cross-region inference default for newer organisations all take this shape.
- Off until an administrator enables it or signs something. Salesforce's Einstein generative AI switch, Workato's Copilot in Automation HQ workspaces and MuleSoft's generative AI in Anypoint sit behind a master switch, an addendum or an acceptance step, so the review question becomes who enabled it and when.
- A contractual statement with no setting. Microsoft's no-training statement for Copilot, Slack's generative-training statement and Atlassian's statement about its hosted model providers are promises in documentation or terms, so there is nothing to toggle and the evidence is the dated document and your contract.

The practical consequence is that a toggle review alone covers the first two shapes and misses the third, and a terms review alone covers the third and misses the first, which is why the summary asks for both.

### Default-state table

Every row is the vendor's published default as read on the `last-checked` date and says nothing about any particular organisation's tenant. Rows checked on 2026-11-09 were read from the vendor pages listed in Sources while the forthcoming ai-config-pointers pages were drafted; rows checked on 2026-11-10 were re-fetched for this document.

| Platform family | Setting | Default | Where the record lands | last-checked |
|---|---|---|---|---|
| Microsoft 365 Copilot | Use of prompts, responses and Graph data to train foundation models | Not used, per Microsoft's privacy page; a contractual statement with no setting | Microsoft Product Terms and DPA | 2026-11-10 |
| Microsoft 365 Copilot | Anthropic and OpenAI models as sub-processors | Admin decides whether these models power experiences; the settings page does not state the default for "AI providers operating as Microsoft subprocessors"; Anthropic models are excluded from the EU Data Boundary | Microsoft 365 admin center, Copilot settings | 2026-11-10 |
| Microsoft 365 Copilot | Cross-region capacity routing | LLM calls may go to other regions under high utilisation; EU traffic stays inside the EU Data Boundary | No customer-visible record documented | 2026-11-10 |
| Microsoft 365 Copilot | Web search in Copilot | Available to users when the policy is not configured | Microsoft 365 admin center | 2026-11-09 |
| Atlassian Rovo | Rovo access per app | "Everyone in your organization will have access to Rovo features"; blocking one Jira-family app does not remove shared Search, Chat and Create while another Jira app on the site keeps Rovo | Organisation audit log (Atlassian Guard tiers) | 2026-11-10 |
| Atlassian Rovo | Rovo as a platform | Atlassian's learning material says Rovo "is enabled by default and can't be turned off", with per-app deactivation as the lever | None documented | 2026-11-09 |
| Atlassian Rovo | Hosted model providers retaining or training on inputs | Atlassian states its providers do not retain inputs and outputs or train on them; contractual, no setting | Rovo admin guide | 2026-11-09 |
| Salesforce Einstein and Agentforce | Einstein generative AI master switch | Off until an admin turns it on | Setup Audit Trail | 2026-11-09 |
| Salesforce Einstein Trust Layer | LLM data masking | Off until turned on; Company Name masking stays off even when masking is on | Setup Audit Trail | 2026-11-09 |
| Salesforce Einstein Trust Layer | Generative AI audit and feedback data collection | Off; when on, prompts and outputs land in Data 360 within 24 hours; retention not stated in the sources read | Data 360 | 2026-11-09 |
| ServiceNow Now Assist | Data sharing with ServiceNow to improve its models | Participation is implied unless you opt out; opt-out is per instance and can take up to five business days; opting back in goes through the account executive; data sharing is not available on GCC or self-hosted instances | Now Assist Admin settings | 2026-11-10 |
| ServiceNow Now Assist | Overflow processing to Azure-hosted GPUs under high demand | Opted in, independent of the data-sharing opt-out | Now Assist Admin settings | 2026-11-09 |
| ServiceNow Now Assist | Generative AI log (`sys_generative_ai_log`) retention | 180 days from Zurich Patch 10, previously 30 days | Instance table | 2026-11-09 |
| Slack | Training generative models on Customer Data | Not without the customer's affirmative opt-in consent | Slack privacy principles | 2026-11-10 |
| Slack | Customer Data in Slack's global (non-generative) ML models | Included unless an Owner requests an opt-out by email; the page describes the opt-out and does not state the default in words | No console record; the email is the record | 2026-11-10 |
| Slack | Require approved apps | Off; members can install apps without Owner approval | Audit Logs API (Enterprise plan) | 2026-11-09 |
| Snowflake Cortex | `CORTEX_ENABLED_CROSS_REGION` | `ANY_REGION` for new organisations created after 2026-03-09; older commercial accounts inherit a same-cloud geography such as `AWS_US`; `DISABLED` keeps inference in the home region | Account parameter (`SHOW PARAMETERS`) | 2026-11-10 |
| Databricks | Partner-powered AI features | Enabled for workspaces without a compliance security profile, using Azure OpenAI, OpenAI on Databricks or Anthropic on Databricks; disabled by default on compliance-security-profile workspaces; the setting is being removed | Account and workspace settings | 2026-11-10 |
| Workato | Copilot | Disabled by default in Automation HQ workspaces, not stated for standalone workspaces; Copilot data goes to OpenAI servers in the US; needs the AI feature addendum | Activity audit log | 2026-11-09 |
| MuleSoft Anypoint | Generative AI in Anypoint | Disabled until a root Organization Administrator accepts it after enablement in the connected Salesforce org | Anypoint audit log | 2026-11-09 |
| Claude Enterprise | Chat retention | Indefinite by default, custom minimum 30 days; some cloud features that run Claude Code are excluded from custom retention | Vendor cloud, reached by the Compliance API | 2026-11-09 |
| Gemini Enterprise | Logging of prompt inputs and response outputs | Text is elided unless the toggle is on; the toggle's default is not stated | Cloud Logging `_Default` bucket | 2026-11-09 |

Three rows deserve a comment. ServiceNow's overflow processing and Microsoft's capacity routing show that where inference happens is a separate question from whether the vendor trains on it, so a review that asks only the training question will miss a residency change. Snowflake's default changed on a date, so two accounts can carry different values depending on when the organisation was created, and the parameter is worth reading from each account. And Databricks' setting is being removed, so a control document citing it will soon describe nothing, which is the general hazard with default-state rows and the reason each carries a date.

### What the record looks like once you find it

Turning on the feature and turning on the record of it are usually two separate decisions. In the enterprise assistants, the admin audit trail of settings and seats tends to exist by default while the prompt and answer arrive through a second channel that is licence-gated, opt-in or held in the vendor's cloud behind a compliance API (Tier B, vendor admin documentation for Microsoft Purview Audit, the OpenAI and Anthropic Compliance APIs and Gemini Enterprise usage logs, read 2026-11-09). The embedded products follow the same pattern at smaller scale: Salesforce's generative AI audit collection is off until enabled, Atlassian's Rovo user-action events need Guard Premium and Atlassian's own public tracker (AX-2026) records that usage events are not fully captured, and Slack's AI and app actions leave Slack only through the Audit Logs API on the Enterprise plan (Tier B, vendor documentation, read 2026-11-09). So for a renter the plan tier often decides how much of the record exists at all, which `rent-or-own-sized-to-the-org.md` takes up in its tier section.

Where a vendor ships a guardrail beside the feature, such as Salesforce's masking, ServiceNow's Now Assist Guardian or Atlassian's Rovo Chat sensitive-data rules, what the feature does is Tier B and how well it catches anything is a vendor efficacy claim, Tier C, which this document has not tested. ServiceNow documents Guardian's offensiveness and prompt-injection detections as defaulting to log rather than block (Tier B, ServiceNow Zurich documentation, read 2026-11-09), which is a reasonable default and worth knowing before anyone describes it as a block.

### Third-party tooling that reads these settings

SaaS security posture management products reach this layer through the same vendor admin APIs, and several now market AI-agent and feature discovery for Copilot, Agentforce and ChatGPT Enterprise (Tier B for what they say they read, Tier C for their coverage counts; CrowdStrike Falcon Shield blog 2026-03-23 and Obsidian Security's Copilot page, read 2026-11-09). I would use them to stretch a small team across many tenants once the review exists, since on the pages I read neither documents reconciling what you licensed against what is switched on, and each holds an admin or compliance-API token per tenant, which is its own credential-scope question.

### The vendor AI questionnaire

These eight questions are my judgement about the minimum written record (Tier D). They are meant for vendors whose public documentation does not answer them, and the answer to each one is filed with its date and the name of the document it came from.

1. Which AI features are enabled in our tenant today, which were enabled by default, and how will you notify us before enabling a new one?
2. Is our data, including prompts, outputs, files and metadata, used to train or improve any model, yours or a provider's, and is the answer a setting, a contract term or an opt-out we must request?
3. Which model providers process our data for each feature, are they on your sub-processor list, and do they process as your sub-processor or under their own terms?
4. Where does inference run, including any capacity or overflow routing to other regions or clouds, and can we restrict it?
5. How long do you and each provider retain prompts, outputs and logs, and does deletion on our side reach the provider's copy?
6. What record of AI use can we export (admin actions, user invocations, content), on which plan, with what retention, and through which API?
7. Which AI features can we switch off per tenant, per app and per user group, and which cannot be switched off?
8. What independent attestation covers the AI features specifically (for example a SOC 2 report or an ISO/IEC 42001 certificate whose scope names them)?

Question 3 matters more than it looks, because Microsoft's Copilot settings separate providers that operate as Microsoft sub-processors from providers that operate as independent processors under their own terms (Tier B, Microsoft 365 admin center Copilot settings documentation, read 2026-11-09), and the same prompt then sits under a different data-controller relationship depending on which toggle is on.

## What this does not mean

A default of "on" is not evidence of harm, and a contractual no-training promise is not evidence the vendor breaks it; neither can be checked from the customer's side beyond reading the terms and the attestation scope, which is why this document treats them as a record to keep current and not as a finding to escalate on their own. The routing rows that send a review here are Medium priority for that reason, and the training opt-out row scores higher on reversibility only because data that has been trained on is hard to recall, which the planned `fine-tuned-model-is-a-data-store.md` (scheduled for v0.2) will discuss from the research side.

The table is not a vendor comparison. The products in it are the ones the forthcoming ai-config-pointers set covers, and a vendor that looks better here may simply document more, so reading the rows as a ranking would get it wrong.

A toggle review is also not discovery. It covers the SaaS products you already know you run, and AI tools nobody approved are the subject of `inventory-and-shadow-ai.md`, where the toggle review is one step in a longer sequence. And this document is not legal advice; the GDPR, NIST and ISO references describe what those texts ask for, and whether a given change needs notice or consent under a specific contract is a question for counsel.

## Gaps

- **Gap: AI invocation events in SaaS audit logs**. Several products record AI configuration changes but not AI use as distinct events, and Atlassian's own tracker says its usage events are incomplete; there is no cross-vendor count of which products log invocations. **Needs**: an audit-schema census in trial tenants of the products in the table, enabling each AI feature and counting the distinct event types it produces, written up as a lab study.
- **Gap: How often vendors change AI defaults**. The claim that vendors switch features on through the release train rests on one interview study and forum reports; nobody here has measured the rate. **Needs**: the default-state table re-read every quarter for at least four quarters, with each change diffed and dated, which the quarterly sweep can produce as a by-product.
- **Gap: Whether contractual opt-outs hold**. No customer can verify a no-training or no-retention promise from outside. **Needs**: a review of which public attestation reports and ISO/IEC 42001 certificates name AI features in scope, which is a desk study, not a bench.
- **Gap: The questionnaire is untested**. The eight questions have not been sent to any vendor. **Needs**: dry runs against the repo's fixtures and returned answers from a handful of vendors, scored for which questions the public documentation already answers.
- **Gap: Google Workspace Gemini, ChatGPT Enterprise and Business-tier rows**. The table has no Gemini for Workspace row and no ChatGPT Enterprise row read directly (OpenAI's help pages returned errors to the fetcher), and the CISA SCuBA `gemini.md` baseline has not been read for this document. **Needs**: the configuration pointer pages for those products read from primary pages, and the SCuBA baseline's controls mapped into the table.
- **Gap: Non-EU processor law**. The sub-processor argument leans on GDPR Article 28. **Needs**: a desk pass over the equivalent notice and sub-processor terms in US state privacy laws, which `prompt-capture-and-the-law.md` scopes.

## Notes

- Claim-level choice (Decision 16): the statement that Rovo "can't be turned off" comes from Atlassian's learning material, while Atlassian's admin page on managing Rovo access, re-read on 2026-11-10, describes per-app blocking and the Jira-family caveat without saying any feature is permanent. The table carries both with their sources rather than choosing one.
- Claim-level choice: Slack's privacy page describes how to opt out of global models and does not state the default in words, and ServiceNow's opt-out page implies participation without stating it for standard instances. The rows say "included unless" and "implied" to keep that difference visible.
- Microsoft's Copilot privacy page now resolves to a `copilot/plan/` path (updated 2026-11-04); the older `copilot/microsoft-365/` path redirects there.
- No lab bench backs this document and it carries no `measurement-claims`; vendor defaults are dated rows with `last-checked`, not re-runnable measurements, as the template directs.
- The three-shape grouping, the review cadence and the questionnaire are dated judgements as of 2026-11-10 (Tier D).

## Sources

Tier A

- Regulation (EU) 2016/679 (GDPR), Article 28, https://eur-lex.europa.eu/eli/reg/2016/679/oj, consolidated text.
- NIST AI 100-1, Artificial Intelligence Risk Management Framework 1.0, January 2023, GOVERN 6, https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf.
- ISO/IEC 42001:2023, Information technology, Artificial intelligence, Management system, Annex A (third-party and customer relationships), https://www.iso.org/standard/81230.html.
- CISA, ScubaGoggles baselines for Google Workspace including `gemini.md`, https://github.com/cisagov/ScubaGoggles/blob/main/baselines/README.md, read 2026-11-09.

Tier B (vendor documentation for what a feature does; research preprints)

- Chhetri, Tariq, Aamir, Grobler et al., "From Frontier to Shadow AI: A Simmering Threat to Assurance and Security in Critical Infrastructure", interview study of 27 Australian critical-infrastructure organisations, CSIRO, arXiv 2606.00088, preprint under review, https://arxiv.org/abs/2606.00088.
- Microsoft, "Data, Privacy, and Security for Microsoft Copilot", updated 2026-11-04, https://learn.microsoft.com/en-us/copilot/plan/microsoft-365-copilot-privacy, read 2026-11-10.
- Microsoft, "Configure Microsoft Copilot settings in the Microsoft 365 admin center", updated 2026-11-04, https://learn.microsoft.com/en-us/copilot/implement/configure-copilot-admin-center, read 2026-11-09.
- Microsoft, "Manage public web access in Microsoft Copilot", https://learn.microsoft.com/en-us/copilot/plan/manage-public-web-access, read 2026-11-09.
- Microsoft, "Audit logs for Copilot and AI applications", ms.date 2026-08-26, https://learn.microsoft.com/en-us/purview/audit-copilot, read 2026-11-09.
- Atlassian, "Manage Rovo access", https://support.atlassian.com/organization-administration/docs/manage-rovo-access/, read 2026-11-10.
- Atlassian, Rovo admin guide, "Rovo data usage and privacy", https://wac-cdn-a.atlassian.com/software/rovo/guides/admin-guide/rovo-data-usage-privacy, read 2026-11-09.
- Atlassian, learning lesson "Use Atlassian Intelligence across your organization", https://community.atlassian.com/learning/lesson/use-atlassian-intelligence-across-your-organization, read 2026-11-09.
- Atlassian, public issue AX-2026, https://jira.atlassian.com/browse/AX-2026, read 2026-11-09.
- Salesforce Trailhead, "Configure LLM Data Masking Policies", https://trailhead.salesforce.com/content/learn/modules/llm-data-masking-in-the-einstein-trust-layer/configure-llm-data-masking-policies, read 2026-11-09.
- Salesforce Trailhead, "Discover Insights from Einstein Generative AI Audit and Feedback Data", https://trailhead.salesforce.com/content/learn/modules/search-analytics-for-ai-generated-search-answers/discover-insights-from-einstein-generative-ai-audit-and-feedback-data, read 2026-11-09.
- ServiceNow, "Opt out of data sharing for Now Assist", https://www.servicenow.com/docs/r/intelligent-experiences/opt-out-of-data-sharing-for-now-assist.html, read 2026-11-10.
- ServiceNow, "Configure Now Assist data overflow processing", https://www.servicenow.com/docs/r/_yCRwrQYX6H0b46tCsDNZA/PtsnFCVy_rvcHzEBe_rBVQ, read 2026-11-09 (default via search summary).
- ServiceNow, Generative AI Controller release notes, https://www.servicenow.com/docs/r/release-notes/generative-ai-controller-rn.html, read 2026-11-09.
- ServiceNow, Now Assist Guardian (Zurich), https://www.servicenow.com/docs/r/zurich/intelligent-experiences/now-assist-guardian.html, read 2026-11-09.
- Slack, "Privacy principles: search, learning and artificial intelligence", https://slack.com/trust/data-management/privacy-principles, read 2026-11-10.
- Slack, "Manage app approval for your workspace", https://slack.com/help/articles/222386767-Manage-app-approval-for-your-workspace, read 2026-11-09.
- Slack, Audit Logs API, https://docs.slack.dev/admins/audit-logs-api/, read 2026-11-09.
- Snowflake, "Cross-region inference", https://docs.snowflake.com/en/user-guide/snowflake-cortex/cross-region-inference, read 2026-11-10.
- Databricks, "Partner-powered AI features", doc date 2026-11-03, https://docs.databricks.com/aws/en/databricks-ai/partner-powered, read 2026-11-10.
- Workato, "Workato Copilot", https://docs.workato.com/en/ai-features/copilot, read 2026-11-09.
- MuleSoft, "Enabling generative AI", https://docs.mulesoft.com/access-management/enabling-generative-ai, read 2026-11-09.
- Anthropic, "Configure custom data retention controls for Enterprise plans", https://support.claude.com/en/articles/10440198-configure-custom-data-retention-controls-for-enterprise-plans, read 2026-11-09.
- Anthropic, Compliance API, https://platform.claude.com/docs/en/manage-claude/compliance-api, read 2026-11-09.
- Google Cloud, "Access Gemini Enterprise usage audit logs with Cloud Logging", https://docs.cloud.google.com/gemini/enterprise/docs/set-up-usage-audit-logs, read 2026-11-09.
- OpenAI, "Compliance API for Enterprise customers", https://help.openai.com/en/articles/9261474-compliance-api-for-enterprise-customers (HTTP 403 to the fetcher; read via search excerpt only, so treat as unconfirmed).
- CrowdStrike, "New CrowdStrike innovations secure AI agents and govern shadow AI", 2026-03-23, https://www.crowdstrike.com/en-us/blog/new-crowdstrike-innovations-secure-ai-agents-govern-shadow-ai/, read 2026-11-09 (what the feature does).
- Obsidian Security, Microsoft Copilot agent page, https://www.obsidiansecurity.com/ai-agent/microsoft-copilot, read 2026-11-09 (what the feature does).

Tier C (vendor claims and user reports, bias flagged)

- Coverage counts and risk percentages on the CrowdStrike and Obsidian pages above; marketing, not tested.
- Guardrail and masking effectiveness for Salesforce Einstein Trust Layer, ServiceNow Now Assist Guardian and Atlassian Rovo Chat security; vendor efficacy statements this document did not test.
- Atlassian Community, "About this week's forced rollout of Rovo", https://community.atlassian.com/forums/Jira-questions/About-this-week-s-forced-rollout-of-Rovo/qaq-p/3109430, user reports from September 2025.
