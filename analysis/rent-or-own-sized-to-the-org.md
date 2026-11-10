---
evidence-tier: Mixed
convergence: single-source
applies-to-signals: [org-size-small-mid, org-size-large-regulated, profile-rent-heavy, profile-own-heavy, own-heavy-small-org, plan-tier-below-audit]
surfaces: [S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12, S13]
pins:
  - "CoSAI secure-ai-tooling 622605a1"
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-03-03
status: EMERGING
---

# Rent or own, sized to the organization, and which tier of rent

Evidence tier: Mixed. Tier A for the CoSAI component vocabulary and for the peer-reviewed work on what a fine-tuned or downloaded model carries; Tier B for vendor plan pages and admin documentation of what each plan tier includes, each row dated; Tier D for the sizing default, the size bands and the ownership cells, which are my practitioner judgement and one author's reading of the component map.

## Summary for the review

For a small or mid-sized organization I think the default should lean toward renting AI, because owning a surface means owning its patching, logging, identity and detection in a sector whose parts change monthly, and once an organization rents, the plan tier it rents on decides more of the record than any setting it can change. Renting does not shrink the risk, though; it moves the risk into what the vendor logs, so the decision is which visibility gaps you accept.

- Record a rent-or-own decision for every surface the organization runs. Under about 1,000 people with no sector regulator, default to enterprise assistants, one managed build platform and direct model calls through a gateway, and own self-hosted serving, fine-tuning or a RAG store only for a named need (residency, cost at volume, a capability the rented models lack). Effort S. Tier D for the default; Tier D for the ownership bands it rests on.
- Write down the visibility gaps each rented surface leaves, starting with content logging that ships off and vendor-held retention windows. Effort S. Tier B.
- Where a small organization owns a surface anyway, name the need, an owner and a second person, and the telemetry contract before it serves traffic, and rent it if any of the three is missing. Effort M. Tier D.
- Where a larger or regulated organization owns more, staff each owned surface for patching, logging, identity and detection, and read the models document for what the tooling misses there. Effort L. Tier D for the staffing, Tier A and B for the gaps.
- Move every AI seat used for work onto a business or enterprise tier with SSO enforced, and check per product which tier carries the audit log, the compliance export, an admin-held training default and control of connectors. Effort S to M. Tier B (plan pages, as of 2026-11-10).
- Budget for the top tier where the record lives only there, which on several coding agents and assistants it does. Effort S to decide. Tier B.

## Why this matters

Many organizations did not choose their AI surface. The assistant arrived with the productivity suite, the coding agents arrived with the developers, and the managed platform arrived with the first product team that wanted to ship a feature, so the first question a security team faces is less about which product to buy and more about which of these parts it should own at all. The CoSAI risk map at commit `622605a1` gives a way to answer that, and the reading of it in `analysis/surface-ownability.md` finds that the organization owns every component it instantiates on only three of the thirteen surfaces (self-hosted serving, fine-tuning pipelines and RAG or vector stores), owns the agent half on three more (coding agents, MCP servers, low-code builders), and on the remaining seven owns little beyond the identity provider, the network enforcement point and whatever audit record the vendor exports (Tier A for the component definitions, Tier D for the cells, one reader).

Read as a cost sheet, that grid says the three fully owned surfaces bring the whole operating load with them, and the rented ones bring a smaller and different load. My view as a practitioner is that a small or mid-sized company finds the larger internal surface a real burden, especially in a sector this new and this fast-moving, and that the vendor-managed parts may well be preferable for it. That is a judgement, carried at Tier D, and the rest of this document lays out what it rests on and where it stops holding.

## What owning costs, what renting costs

Owning a surface means the organization carries every component on it. On a self-hosted serving cluster that is the model server, the weights, the model store, the runtime host and its isolation, the identity in front of it and the audit record behind it, and every one of those is a patch cycle, a log source and a detection someone has to write (`analysis/surface-ownability.md`, Tier D). On a fine-tuned model the load includes the training data, because a model trained on an organization's records can reproduce some of them; extraction of verbatim training text from a production language model was shown by Carlini et al. at USENIX Security 2021 (Tier A), safety behaviour can regress after fine-tuning on benign data (Qi et al., ICLR 2024, Tier A), and a backdoor planted in a model can be undetectable in the general case (Goldwasser et al., FOCS 2022, Tier A). None of that is a reason a large team cannot own these surfaces, but each item is work that lands on named people, and in a small security team the same one or two people already carry the identity provider, the EDR and the cloud. The detail on what the off-the-shelf tooling misses on owned models will be in `analysis/models-you-hold.md`, which is in preparation.

Renting moves the work rather than removing it. On the rented surfaces the content record usually ships switched off (Bedrock model invocation logging, Vertex AI Data Access audit logs and Azure diagnostic settings are all off until configured, and coding-agent content export is opt-in), and the record that does exist is often held by the vendor for a fixed window, such as 180 days for Purview Audit (Standard) and for the GitHub enterprise audit log and 90 days for CloudTrail Event history (Tier B, vendor documentation read 2026-11-09; the dated rows are in `analysis/configure-before-you-buy.md` and `analysis/telemetry-by-surface.md`). So a renter's security work is the identity provider, the enforcement point, the configuration and the exported audit log, which is cheaper to turn on than a serving cluster is to run and harder to verify, because the vendor's documentation is usually the only evidence of what a toggle does.

| Size band (from the interview) | Default | Own a surface only when | Where the security team's effort goes |
|---|---|---|---|
| Under about 1,000 people, no sector regulator | Rent: enterprise assistant, one managed build platform, direct model calls through a gateway | A named need renting cannot meet, an owner and a second, and a telemetry contract, all three before it goes live | Identity, the gateway or SSE enforcement point, configuration, exporting vendor records before retention closes |
| About 1,000 or more, or any sector regulator | Rent by default, own where residency, a supervisor's expectation, cost at volume or capability requires it | The same three cells, plus the staff to patch, log and detect on every owned component | The renter's list, plus the full operating load of each owned surface and an evaluation harness before an owned model serves traffic |

The band boundary is the interview's own question in `routing.yaml` and is my judgement (Tier D); it marks where I'd expect a security function to have room for a named owner per surface, and a 900-person firm with a large security team can reasonably answer as the second row. An organization that owns a surface by mandate takes the override in `analysis/decision-sequence.md`, which replaces the sizing argument with the three-cell test.

## Which tier of rent

Renting is not one thing either, and for a small organization the tier of the rented product may matter more than the rent-or-own choice itself. A consumer seat used for work leaves the organization owning nothing on the surface: no identity provider in front of it, no audit record, and a training setting the individual controls. A business or team seat usually adds SSO and an admin-held training default, and the audit log and compliance export often sit one tier higher still. The pattern I read across the plan pages is that for coding agents and assistants the record of who did what is a top-tier feature, while Microsoft inverts this for its own Copilot by recording interactions in Audit (Standard) and charging separately for non-Microsoft AI apps (Tier B, as of the dates below).

The rows below are the vendors' published plan contents, not any tenant's configuration, and the review prints "as of" the row's date beside anything drawn from it. Where a companion page is named, the full row with its console path is there (Decision 12). A plan page is a summary; the binding training and retention promise lives in the commercial terms, which `analysis/saas-embedded-ai-and-vendor-terms.md` covers.

| Product (companion page) | Tier | SSO | Audit log or compliance export | Training on content | Admin control of connectors or tools | last-checked |
|---|---|---|---|---|---|---|
| Claude (g6-dev-appsec-coding-agents-claude-code) | Individual plans | No | No audit log, no Compliance API | User opt-out | No | 2026-11-10 |
| Claude | Team | Yes | Plan page lists no audit log and no Compliance API | None by default | Admin controls for remote and local connectors | 2026-11-10 |
| Claude | Enterprise | Yes, with SCIM | Audit logs, Compliance API, custom retention | None by default | Yes, with role-based permissions | 2026-11-10 |
| ChatGPT (g6-dev-appsec-coding-agents-codex) | Free, Go, Plus, Pro | Not stated | Not stated | Used for training, opt-out available | Not stated | 2026-11-10 |
| ChatGPT | Enterprise | Not read this pass | Compliance API and Compliance Logs Platform, off until collected | Not read this pass | Workspace toggles for Codex | 2026-11-09 |
| GitHub Copilot (g6-dev-appsec-coding-agents-github-enterprise-copilot) | Free, Pro, Pro+, Max | SAML SSO not included | Audit logs listed from Pro+ up, not on Free or Pro | Interaction data may be used for training, opt-out | MCP in agent mode, no admin policy | 2026-11-10 |
| GitHub Copilot | Business, Enterprise | Through the GitHub organization or enterprise | Enterprise audit log, 180 days, streaming off until configured | Not re-read this pass | MCP policy and managed MCP allowlist | 2026-11-09 |
| Cursor (g6-dev-appsec-coding-agents-cursor) | Individual plans | No | No | Privacy mode, user-enabled | No | 2026-11-10 |
| Cursor | Teams | SAML or OIDC | Not listed | Team-wide privacy settings | Not listed | 2026-11-10 |
| Cursor | Enterprise | SAML or OIDC, with SCIM | Audit logs and service accounts (the Admin API caps each query at a 30-day window, admin docs read 2026-11-09) | Team-wide privacy settings | Repository, model and MCP access controls | 2026-11-10 |
| Microsoft 365 Copilot (g1-microsoft-365-entra-purview) | Copilot licence | Entra ID | `CopilotInteraction` in Audit (Standard), 180 days; non-Microsoft AI apps billed pay-as-you-go | Contractual statement, no setting | Agent and model-provider settings in the admin center | 2026-11-09 |
| Google Workspace with Gemini (g2-google-okta-browsers-google-workspace) | Enterprise Standard, Plus | Workspace identity | Gemini log events in the Admin console | Unlicensed users let in by the "regardless of license" setting fall under terms that allow model improvement | Gemini app access to Workspace apps, per OU | 2026-11-09 |

Two rows deserve a comment. The Claude Team row lists no audit log on the plan page, while the Claude Code settings documentation records audit events for server-managed settings changes on Team and Enterprise, so I read the plan row as the organization-wide audit log and compliance export rather than as no record at all (Tier B, both read on the dates shown). And the Google Workspace row shows the tier question inside a single tenant, since one admin checkbox can put unlicensed users on the assistant under consumer-style terms, which is the consumer-seat problem without any shadow-AI purchase behind it.

So the practical check for a renter is per product and per seat: is every seat used for work on a tier with SSO enforced, does that tier carry the audit log and the content export the organization needs, is the training default held by the admin or by the user, and can an admin restrict which connectors and tool servers the product reaches. A yes to the `plan-tier-below-audit` question means at least one of those is missing somewhere, and the cheapest fix is usually a seat move rather than a new control.

## What this does not mean

It does not mean renting is safer in any absolute sense, because the risk moves into what the vendor records and retains, and an organization that rents without turning on and exporting those records has given up visibility for nothing. It does not mean a small organization must never own a surface, since data residency, a sector supervisor's expectation about processing location, cost at high volume or a capability gap can each justify owning, and the own-by-mandate override exists for that case. It does not mean the enterprise tier is a working control either, because a plan page lists that a feature exists and says nothing about whether it is configured or whether it records what an investigation needs. It does not mean a large organization should own more by default; the size band changes what an organization can staff, not the cost of each owned component. And the table is a reading of plan pages that change often, so a stale row should be read as dated rather than as wrong.

What would change my mind on the sizing default: a managed platform dropping a log feature the rent decision relied on, a sustained run of KEV entries against a rented gateway or agent platform that small teams cannot patch faster than the vendor, or evidence that small teams operate self-hosted serving with the same incident rate as renters.

## Gaps

- **Gap: the sizing threshold**. No public study measures how much security staffing an owned AI surface needs, or whether incidents differ between organizations that rent and own the same capability, so the size band and the default are Tier D. **Needs**: a practitioner survey of staffing per owned AI surface by size band, or an incident corpus coded for whether the affected surface was rented or owned.
- **Gap: second reading of the ownership cells**. The component grid this document's cost side rests on has one reader. **Needs**: a blind second reading of the surface-by-component grid against the CoSAI descriptions, with disagreements published.
- **Gap: ChatGPT business-tier plan contents**. OpenAI's plan page did not show the Business and Enterprise columns, and the enterprise privacy page returned HTTP 403 to the fetcher, so the SSO and training cells for those tiers are unread. **Needs**: a browser read of OpenAI's business plan comparison and enterprise privacy page, dated.
- **Gap: GitHub Copilot business-tier training statement**. The plan page's training language covers individual subscribers only. **Needs**: a dated re-read of GitHub's Copilot product-specific terms for Business and Enterprise.
- **Gap: what each tier's audit log records**. Plan pages say an audit log exists, not which actions land in it. **Needs**: a pre-registered tier-audit bench in sdw-lab-benchmarks that signs in on each tier of each product, performs a fixed set of admin, connector and content actions, and records which reach the exportable log; not yet registered.
- **Gap: memorization in an enterprise-shaped fine-tune**. Whether a small fine-tune on organizational records memorizes enough for a canary test to find is not measured at enterprise scale. **Needs**: the CPU LoRA canary run pre-registered on sdw-lab-benchmarks branch hub/ai-research-2026-11-09, which is frozen and not yet run.

## Notes

- 2026-11-10, judgement marker: the rent-leaning default for small and mid-sized organizations is my practitioner view, carried at Tier D as a reference perspective. It is the first of the ordering perspectives in `analysis/decision-sequence.md`, which order actions within a priority band and never raise one (DECISIONS.md Decision 3 and Decision 15); recording the tier here follows Decision 16.
- There are no `measurement-claims` rows because no lab result backs this document. The storage cost of exporting rented records lives in `analysis/what-to-log-and-what-it-costs.md`.
- The plan-page rows were read on 2026-11-10 and the companion-page rows on 2026-11-09. Plan pages change more often than admin documentation, which is why this document revalidates in under four months.
- Plan names differ between vendors and between a vendor's pricing page and its documentation, so the table groups individual plans together and names business tiers as the vendor does.
- Companion pages are named by file rather than linked until the ai-config-pointers set has a public address (Decision 12).

## Sources

Tier A, standards and peer-reviewed

- CoSAI, secure-ai-tooling `risk-map/yaml/components.yaml` at commit `622605a1`, https://github.com/cosai-oasis/secure-ai-tooling (component vocabulary).
- Carlini, Tramèr, Wallace et al., "Extracting Training Data from Large Language Models", USENIX Security 2021, https://www.usenix.org/conference/usenixsecurity21/presentation/carlini-extracting.
- Qi, Zeng, Xie et al., "Fine-tuning Aligned Language Models Compromises Safety, Even When Users Do Not Intend To!", ICLR 2024, https://arxiv.org/abs/2310.03693.
- Goldwasser, Kim, Vaikuntanathan and Zamir, "Planting Undetectable Backdoors in Machine Learning Models", FOCS 2022, https://arxiv.org/abs/2204.06974.

Tier B, vendor plan pages and documentation of what a feature does

- Anthropic, Claude pricing and plan comparison, https://www.claude.com/pricing (read 2026-11-10).
- Anthropic, "Configure custom data retention controls for Enterprise plans", https://support.claude.com/en/articles/10440198-configure-custom-data-retention-controls-for-enterprise-plans (read 2026-11-09, via companion page).
- OpenAI, ChatGPT pricing, https://chatgpt.com/pricing (read 2026-11-10; Business and Enterprise columns not shown).
- GitHub, Copilot plans, https://github.com/features/copilot/plans (read 2026-11-10); "Plans for GitHub Copilot", https://docs.github.com/en/copilot/get-started/plans (read 2026-11-10, first half of the page).
- Cursor, pricing, https://cursor.com/pricing (read 2026-11-10).
- Microsoft, Google, AWS and GitHub admin documentation for the retention and default-state rows, as cited row by row in the ai-config-pointers companion pages named above (read 2026-11-09).

Tier D, practitioner judgement

- The author's sizing perspective, dated 2026-11-10, carried in `analysis/decision-sequence.md`.
