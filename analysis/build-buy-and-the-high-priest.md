---
evidence-tier: Mixed
convergence: single-source
applies-to-signals: [org-size-small-mid, org-size-large-regulated, vendor-evaluation-in-progress, custom-build-planned]
surfaces: [S2, S4, S5, S7, S8, S9, S10, S11, S12]
pins:
  - "CoSAI secure-ai-tooling 622605a1"
  - "Sigma specification 2.0.0"
  - "OCSF 1.9.0"
  - "OMB M-25-21 2025-04-03"
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-06-28
status: EMERGING
---

# Build, buy and the high priest: the lifetime cost of a custom system

Evidence tier: Mixed. Tier A for the peer-reviewed work on technical debt, truck factors, abandonment, the mirroring hypothesis and lock-in, for the standards that require an inventory and for the CoSAI control IDs; Tier B for Reed's essay, the Sigma specification, the SRE book, the METR trial (a preprint), the CIO Council playbook, OMB M-25-21 and CISA's KEV catalogue; Tier C for Conway's 1968 trade-magazine paper, DORA 2024's self-report association and Veracode's vendor benchmark, bias flagged; Tier D for the transfer of open-source results to internal tools, the build list, the preconditions and the configure-first view, all labelled where used.

## Summary for the review

A custom AI-security tool is cheap to build this year and as expensive to keep as software has ever been, because maintenance is the larger share of a system's lifetime cost and an internal tool usually has one person who understands it, so a build should be priced on who upgrades it in month four and what happens when that person leaves.

- Before approving a build, confirm the need is not reachable by turning on or scoping something already owned (`analysis/configure-before-you-buy.md`). Effort S. Tier D.
- Restrict builds to the thin layer that is configuration of a system already run: evaluation harnesses, detections as code, hook and policy configuration, telemetry adapters and pinned glue, and prefer buying the sensor itself. Effort S to decide. Tier D, resting on Tier A debt and truck-factor evidence.
- Have someone other than the person holding the coding agent write the maintenance estimate. Effort S. Tier D, resting on the Tier B METR trial.
- Give every surviving build a named owner and second, pinned interfaces with a test that fails when an upstream moves, a re-decision date within twelve months, a row in the same inventory as purchased tools, and a telemetry contract in the shared schema. Effort M per tool. Tier A for the inventory controls and truck-factor evidence; Tier D for the shape.
- An organization that favours building should first have a review body that can decline or retire systems, or have centralized on a few core platforms whose lock-in it treats as nearly permanent; without either, build nothing past the thin layer. Effort L. Tier B precedent, Tier D rule.
- For a small or mid-sized organization, keep the build list to configuration plus at most one pre-registered evaluation harness. Effort S. Tier D.

## Why this matters

AI coding tools have made it plausible for a three-person security team to write its own injection filter, MCP proxy or AI-usage dashboard in a week, and the temptation is easy to understand. It is reasonable on the build side and mispriced on the keep side, because organizations tend to budget a new system as one more contract and console while the larger cost arrives through everything the system now has to fit with, and through the person who becomes the only one who knows how it works. I call that person the high priest, and a custom system creates one more reliably than a purchase does, since a purchase has a vendor behind it and a custom tool has its author.

In my own earlier operational work, something like 80 to 90 percent of what I needed for AI governance was already present in platforms we licensed, and most of what we had was unconfigured or misconfigured. That is a practitioner view offered as a general observation, Tier D with the dated marker in Notes, and this document assumes the configure-first audit has happened and is about the residue it leaves.

## What a custom system costs the organization

Two laws frame the organizational cost. Reed's law says the number of possible subgroups among N members grows as 2^N, so adding one system to a stack of seven roughly doubles the groupings an integration, a veto or a territorial claim can form around (Tier B, Reed 1999); Reed's claim is about value and I am running the combinatorics in the cost direction, so the count is a direction rather than a tally, which is how Briscoe, Odlyzko and Tilly read network-size laws generally (Tier B, IEEE Spectrum 2006). Conway's law says an organization that designs a system is "constrained to produce designs which are copies of the communication structures of these organizations," so a tool written by one person inherits that person's interfaces and blind spots (Tier C, Conway 1968, trade magazine), and the peer-reviewed test found the product from the more loosely coupled organization more modular in every matched pair studied, by up to a factor of six in change propagation (Tier A, MacCormack, Baldwin and Rusnak 2012, abstract read through search). So a custom tool is a new node in Reed's count shaped by Conway's constraint, and both effects tend to outlive the author's time on it.

The software-engineering record on what that costs predates the AI boom, and I think it transfers, with the transfer labelled where it is mine.

*Maintenance is most of the cost.* The share figures usually quoted come from surveys I have read only secondhand, measuring different things, so I carry the direction without a number: the build is the smaller part (Tier C until the primaries are read; see Gaps).

*The debt of systems with a model in them has names.* Sculley and colleagues at Google argued, from Google's experience rather than a measured sample, that production machine-learning systems accumulate boundary erosion, entanglement, hidden feedback loops, undeclared consumers, data dependencies, configuration debt and exposure to changes in the external world (Tier A, NeurIPS 2015). An injection classifier wired into a gateway is an entangled model with undeclared consumers whose external world, the attacker, changes on purpose, which is why adaptive attacks push a learned classifier's block rate down so sharply (Tier A, Nasr et al., USENIX Security 2026; see `analysis/reading-vendor-claims.md`).

*Many projects rest on one or two people.* Avelino and colleagues estimated truck factors for 133 popular GitHub systems and found 65 percent at two or less (Tier A, ICPC 2016). Following 1,932 popular projects, a later study found 315 (16 percent) abandoned in the sense that every truck-factor developer had stopped contributing; 128 of those (41 percent) survived, and 86 percent of the survivors did so by attracting a single new truck-factor developer (Tier A, Avelino et al., ESEM 2019). Coelho and Valente surveyed the maintainers of 104 deprecated popular systems and grouped their answers into nine reasons for failure, one being usurped by a stronger competitor (Tier A, ESEC/FSE 2017). My inference, at Tier D, is that these results understate the risk for internal tools, because an open-source project has a worldwide pool of potential rescuers and an internal script has the rest of the team, who did not write it and have their own queues.

*Operations has a finite budget.* Google's SRE book places "a 50% cap on the aggregate 'ops' work for all SREs" and redirects the overflow to product teams (Tier B, Beyer et al. 2016, ch. 1). Security teams rarely keep that accounting, so a custom tool's toil lands on whoever is nearest, usually its author.

*The clock is what is different about this sector.* ATLAS publishes monthly, OCSF minors are adding AI attributes, the MCP specification's 2026-07-28 revision added required `Mcp-Method` and `Mcp-Name` headers, agent identity drafts are still drafts, and platform logging defaults change by release note (`analysis/revalidation-and-pins.md`). A custom tool that parses any of those has an upstream that moves monthly and an upgrade paid each time by the one person who understands the parser, while a vendor spreads that cost across its customers.

## The AI-coding-tool temptation, priced

AI coding tools have collapsed the visible cost of the build, and the visible cost was already the small part. I use these tools, so my claim is about the ratio between what the team sees and what the organization pays rather than about code quality.

The best controlled evidence I have found cuts against intuition. In METR's randomized trial, 16 experienced developers completed 246 tasks in mature repositories where they averaged five years of experience, and allowing early-2025 AI tools increased completion time by 19 percent, while the developers had forecast a 24 percent reduction and afterwards still estimated a 20 percent reduction (Tier B, arXiv 2507.09089, a preprint; METR notes the setting is not representative of all development). The perception gap is the finding that matters here, because people doing the work misjudged its cost by about forty points in the cheaper direction, and a proposal written in that state will under-price the build and say little about maintenance.

Two weaker sources point the same way. DORA 2024 estimated from roughly 39,000 survey responses that a 25 percent increase in AI adoption went with 1.5 percent lower delivery throughput and 7.2 percent lower stability, an association with no causal claim (Tier C). Veracode had more than a hundred models write code for 80 tasks built around specific CWEs and found the insecure option chosen in 45 percent (Tier C, vendor benchmark from a company selling the remedy, bias flagged). The honest reading is that AI-written code needs the same review as human-written code, and the proposal should carry that cost.

The old high priest at least wrote the tool slowly enough to understand it. The new one generated it in an afternoon, shipped it because it passed the test case, and is now the only person who can answer questions about code nobody, its author included, has read end to end. Configuration debt and undeclared consumers are the debts a fast build accumulates fastest, and in security that means a detection or block whose logic nobody can explain when an auditor asks, which is why I'd want the maintenance line written by someone else (Tier D, resting on the METR perception gap).

## When building is the right call

None of this argues against building, because incumbent tools stop at certain edges by position and some of that gap has to be closed by hand (`analysis/incumbent-tool-coverage.md`). My test is whether the build is configuration of a system the organization already runs, or a thin layer with a documented interface over one, as opposed to a new system with its own storage, model and console; the first is a few hundred lines a second engineer can read in an afternoon, and the second is a new node in Reed's count. Five cases pass in my judgement (Tier D).

- Evaluation harnesses. `componentModelEvaluation` is the one CoSAI component the repo's incumbent coverage grading finds no tool category reaching (Tier D grade over Tier B vendor documentation), and adaptive-attack results mean the only honest block rate a team can hold for its own filters, or a vendor's, is one it measured against an attack set it controls (Tier A, Nasr et al. 2026). A harness with a frozen pre-registration has no production traffic, and it is the one build I'd suggest to a team of any size.
- Detections as code. A Sigma rule (specification 2.0.0, public domain) over OCSF 1.9.0 fields is version-controlled text any SIEM with a converter can run, so the artifact is the interface (Tier B, SigmaHQ; `analysis/landing-ai-events-in-ocsf.md`).
- Hook and policy configuration. A managed-settings file, a hook that denies a tool call, or a gateway policy that pins a key to an owner is reviewable text on a system already in place (Tier B for what each feature does; `analysis/coding-agent-hooks-and-policy.md`, `analysis/ai-apis-and-the-gateway.md`). The structured tool-call record no vendor ships complete is often exactly such a rule, and it is where I'd spend a small team's whole build budget.
- Telemetry adapters. Few AI sources emit OCSF or stable OpenTelemetry, so mapping vendor JSON into typed identity, model and tool-name columns is the organization's cost either way, and an adapter between two published formats can be diffed (`analysis/what-to-log-and-what-it-costs.md`). Both ends move, hence the pinned version and loud failure in the checklist.
- Pinned glue. An inventory join over telemetry already collected is a saved query, and glue that re-reads a pinned source and fails loudly when a count or schema changes is glue a successor can trust.

What usually fails the test is building the sensor: your own inline inspection point, production injection classifier, agent-identity broker or model-file scanner. That rebuilds what the market sells, without the vendor's cross-customer upgrade amortization and with all of the priest cost, and the AI gateway category already has three LiteLLM entries in CISA's KEV catalogue added during 2026 (Tier B, read 2026-11-10), a reminder of what a home-built gateway would carry. An organization with a research team and a need no product meets may still build one, after the preconditions below.

## Preconditions for organizations that favour building

Large, regulated or engineering-led organizations sometimes favour building, and my view is that they need one or both of two things, each attacking a different term in Reed's count (Tier D).

An architecture-review and application-rationalization process attacks N, so every system entering the count clears a review and every system no longer earning its place leaves. The federal CIO Council's Application Rationalization Playbook (v1.1, June 2019) is the most concrete public version I know, a six-step process that starts with needs and governance (Tier B, read through summaries). OMB M-25-21 does the same for AI, requiring agencies to inventory AI use cases at least annually and charging each Chief AI Officer to ensure "custom-developed AI code" is "appropriately inventoried, shared, and released" (Tier B, 2025-04-03, read directly). A custom tool that enters through the same gate as a purchase, answering the same questions about owner, running cost and what it replaces, is priced on the same accounting, and an organization with no such gate has no routine way to make the count fall.

Centralization on a few core systems attacks the exponent. If the organization runs one identity provider, one cloud control plane, one SIEM and one gateway, every custom tool is glue among a small fixed set of published interfaces that a successor who knows those four systems can read. The cost is lock-in, which switching costs and network effects make durable (Tier A, Farrell and Klemperer 2007), so I treat centralization as nearly permanent, choose core systems for what they will likely still be in five years and for the open schemas they export, and require those schemas in everything bought and renewed to keep exits open.

An organization with neither adds systems one defensible decision at a time, each custom tool sits on a different combination of interfaces, and each gets its own priest.

## A governance checklist for any custom build

Each item names the CoSAI control it serves where one exists (secure-ai-tooling at `622605a1`). I'd apply it to glue too, since glue without an owner drifts into a private tool.

| # | Item | What done looks like | CoSAI control | Why |
|---|---|---|---|---|
| 1 | Owner and second | Two people who can each explain the tool and deploy a fix, recorded in the inventory row, reviewed when either changes role | `controlAgentInventoryManagement` | 65 percent of popular systems at truck factor two or less, and survival after abandonment usually meant one new truck-factor developer (Tier A) |
| 2 | Documented interfaces | Inputs (source, version pinned), outputs (schema, version) and known consumers listed, with a test that fails when a pinned upstream changes | `controlComponentIdentityProvenance` | Undeclared consumers and data dependencies (Tier A, Sculley et al.) |
| 3 | Re-decision date | At most twelve months out, brought forward by a framework release, a platform logging change or an acquisition | none | A stronger competitor is a named failure reason (Tier A), and here the competitor is often a vendor toggle; twelve months is my default (Tier D) |
| 4 | Inventory row | Owner, second, interfaces, date, surfaces and components, in the same register as purchased tools | `controlAgentInventoryManagement`, `controlModelAndDataInventoryManagement` | NIST SP 800-53 CM-8 (Tier A); M-25-21's annual inventory (Tier B); EU AI Act Article 49 registration for Annex III high-risk systems (Tier A) |
| 5 | Telemetry contract | Typed identity, model and tool-name fields at ingest, export schema by version (OCSF 1.9.0, or OpenTelemetry `gen_ai` with its Development status noted), retention the organization controls | `controlAgentObservability` | A tool that logs outside the shared shape becomes a blind cell in the coverage view it was built to improve |

Items 1 and 4 are what let a rationalization pass work at all, since a review can only retire what it can see and only reassign what has an owner.

## How this changes for small and mid-sized organizations

For a small team, my view is that the build list collapses to the thin layer by arithmetic (Tier D): a five-person team that builds a tool will in practice have a truck factor of one on the day it ships and no outside pool of rescuers, its operational time is already spent on the owned stack, and the monthly upgrade lands on the same person. So the list is the managed-settings file and the hook, Sigma rules over fields its SIEM already types, the inventory join as a saved query, and at most one pre-registered evaluation harness.

Renting most of the AI surface, which `analysis/rent-or-own-sized-to-the-org.md` treats as a reasonable default for many smaller organizations, moves configuration work rather than removing it, because what is already there becomes toggles and licence lines in someone else's product, cheaper to turn on than to build and harder to verify (Tier B for what a toggle does, Tier C for how well). The small organization's build step is mostly glue that lands vendor exports in a store it controls before the vendor's retention runs out. Larger or regulated organizations that own self-hosted serving or fine-tuned models will probably build past the thin layer whether they plan to or not, so for them the preconditions come first and the evaluation harness is the first build.

## What this does not mean

It does not mean building is wrong, since the five cases above are builds I'd recommend, and it does not make buying safe, because a purchase also joins Reed's count, still needs an owner, and its efficacy claims stay Tier C until tested (`analysis/reading-vendor-claims.md`). The truck-factor and abandonment results concern popular open-source projects, and my claim that they understate internal risk is unmeasured. The METR trial covers experienced developers in familiar large repositories with early-2025 tools, and a controlled study showing AI assistance shrinking the maintenance share would weaken the pricing argument. And a platform that shipped model evaluation with an inspectable adaptive attack set would turn the harness from a build into configuration.

## Gaps

- **Gap: internal security-tool maintenance and abandonment**. No study of the maintenance cost, truck factor or retirement rate of internal security tooling was found, so the open-source transfer stays Tier D. **Needs**: a published internal tool-retirement register with causes and owner changes over time, or a maintainer survey of security tooling in the style of Coelho and Valente.
- **Gap: maintenance share of lifecycle cost**. The commonly cited figures were read only through secondary compilations, so no number is used. **Needs**: a direct read of the primary surveys or a recent peer-reviewed measurement.
- **Gap: AI-assisted security-tool builds**. No controlled study covers AI-written security tools or measures maintenance rather than completion time. **Needs**: a randomized or matched study followed for at least a year, reporting maintenance effort and defects found.
- **Gap: the configure-first share and the playbook text**. The 80 to 90 percent view is unmeasured, and the CIO Council playbook's step names were read only through summaries. **Needs**: the practitioner worksheet aggregation in `analysis/configure-before-you-buy.md`, and a direct read of the playbook PDF.

## Notes

- 2026-11-10, judgement markers: the 80 to 90 percent configure-first view (earlier operational work, never scored or printed as a figure), the five-case build list, the sensor preference, the two preconditions, the twelve-month default and the small-team collapse are the author's judgement at Tier D; they order actions within a band and never raise one (DECISIONS.md Decisions 3, 15 and 16).
- No `measurement-claims` rows: nothing here is a re-runnable lab result, and coverage grades and lab figures bearing on the build list belong to the companion documents named in the text.
- Re-read from primaries on 2026-11-10: Avelino 2016 and 2019 (the 86 percent from the 2019 paper's RQ2 text), METR, Coelho and Valente, OMB M-25-21, SRE chapter 1, CISA KEV, and the CoSAI IDs at `622605a1`. MacCormack, DORA and Veracode rest on abstracts, vendor posts and search summaries.
- `revalidate-by` sits about seven and a half months out because the document depends more on the software-engineering literature than on monthly framework releases.

## Sources

Tier A, peer-reviewed and standards

- Sculley et al., "Hidden Technical Debt in Machine Learning Systems", NeurIPS 28, 2015, pp. 2503-2511, https://proceedings.neurips.cc/paper/2015/file/86df7dcfd896fcaf2674f757a2463eba-Paper.pdf.
- Avelino, Passos, Hora and Valente, "A Novel Approach for Estimating Truck Factors", ICPC 2016, https://doi.org/10.1109/ICPC.2016.7503718, arXiv 1604.06766.
- Avelino, Constantinou, Valente and Serebrenik, "On the Abandonment and Survival of Open Source Projects: An Empirical Investigation", ESEM 2019, https://doi.org/10.1109/ESEM.2019.8870181, arXiv 1906.08058.
- Coelho and Valente, "Why Modern Open Source Projects Fail", ESEC/FSE 2017, https://doi.org/10.1145/3106237.3106246, arXiv 1707.02327.
- MacCormack, Baldwin and Rusnak, "Exploring the Duality between Product and Organizational Architectures: A Test of the 'Mirroring' Hypothesis", Research Policy 41(8), 2012, pp. 1309-1324, https://doi.org/10.1016/j.respol.2012.04.011.
- Farrell and Klemperer, "Coordination and Lock-In: Competition with Switching Costs and Network Effects", Handbook of Industrial Organization vol. 3, ch. 31, 2007, https://doi.org/10.1016/S1573-448X(06)03031-7.
- Nasr, Carlini et al., "The Attacker Moves Second: Stronger Adaptive Attacks Bypass Defenses Against LLM Jailbreaks and Prompt Injections", USENIX Security 2026, arXiv 2510.09023.
- NIST SP 800-53 Rev. 5, CM-8 System Component Inventory, https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final.
- Regulation (EU) 2024/1689 (AI Act), Article 49, https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-49.
- CoSAI, secure-ai-tooling `risk-map/yaml/controls.yaml` and `components.yaml` at commit `622605a1`, https://github.com/cosai-oasis/secure-ai-tooling.

Tier B, practitioners, policy and vendor documentation of what a feature does

- David P. Reed, "That Sneaky Exponential: Beyond Metcalfe's Law to the Power of Community Building", 1999, https://www.deepplum.com/gfn/reedslaw.html.
- Briscoe, Odlyzko and Tilly, "Metcalfe's Law Is Wrong", IEEE Spectrum, July 2006.
- Beyer, Jones, Petoff and Murphy (eds.), Site Reliability Engineering, 2016, ch. 1, https://sre.google/sre-book/introduction/.
- METR, "Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity", arXiv 2507.09089, 2025-07-10 (preprint).
- OMB, M-25-21, "Accelerating Federal Use of AI through Innovation, Governance, and Public Trust", 2025-04-03, https://www.whitehouse.gov/wp-content/uploads/2025/02/M-25-21-Accelerating-Federal-Use-of-AI-through-Innovation-Governance-and-Public-Trust.pdf.
- Federal CIO Council, Application Rationalization Playbook, v1.1, June 2019 (read through summaries).
- SigmaHQ, sigma-specification 2.0.0, https://github.com/SigmaHQ/sigma-specification.
- CISA, Known Exploited Vulnerabilities Catalog, entries CVE-2026-42208, CVE-2026-42271 and CVE-2026-59822 (BerriAI LiteLLM), https://www.cisa.gov/known-exploited-vulnerabilities-catalog (read 2026-11-10).

Tier C, bias flagged where it applies

- Melvin E. Conway, "How Do Committees Invent?", Datamation 14(4), April 1968, pp. 28-31 (trade magazine).
- Google Cloud, "Announcing the 2024 DORA report", https://cloud.google.com/blog/products/devops-sre/announcing-the-2024-dora-report (self-report association).
- Veracode, 2025 GenAI Code Security Report, 2025-07-30, https://www.veracode.com/resources/2025-genai-code-security-report/ (vendor benchmark; Veracode sells code-security remediation).
- Maintenance-share figures attributed to Lientz and Swanson 1980 and Erlikh 2000, read only through secondary compilations; direction used, no figure.

Tier D

- The configure-first view, the open-source transfer, the build list, the sensor preference, the preconditions, the twelve-month default and the small-team collapse: the author's judgement, labelled where used.
