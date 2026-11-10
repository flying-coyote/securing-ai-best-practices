---
evidence-tier: Mixed
convergence: single-source
applies-to-signals: [audit-always-fetch, profile-override-own-by-mandate, profile-override-gateway-chosen]
surfaces: [S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12, S13]
pins:
  - "CoSAI secure-ai-tooling risk-map @ 622605a1"
  - "MITRE ATLAS v2026.10"
  - "OCSF 1.9.0"
  - "MCP specification 2026-07-28"
  - "CISA KEV catalogVersion 2026.11.09"
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-02-17
status: EMERGING
---

# Decision sequence: sixteen decisions, the not-yet list and the 90-day / one-year / later order

Evidence tier: Mixed. Each of the sixteen decisions is carried by practitioner talks, vendor documentation or peer-reviewed work at Tier B or better, named per row; the order they come in, the not-yet list, the horizons and the four perspectives are my practitioner judgement at Tier D, and they order recommendations without ever raising one.

## Summary for the review

The ordering principle, in two sentences: take the decisions in the order ownership, risk tolerance, configure what you own, gateway and identities, log tier, evaluation, containment, and only then the vendor conversation, because each earlier step produces the inventory or telemetry the later ones depend on. That order is my judgement as a practitioner (Tier D), the interview accepts a one-line override of it, and the output should print which variant it applied.

Practices for the review, as actions:

- Record rent-or-own and the sanctioned list as one dated note first, sized to the organization (S, Tier D for the sizing and the ownership reading, B for the practitioner talks behind it).
- Collect first from the three components owned on every surface: the identity provider, the network enforcement point and the exported audit record (S, Tier D reading of the CoSAI map).
- Inventory what you license as entitled, available and enabled, and switch on what is off before any purchase (M, Tier B; D for how much it covers).
- Turn on and export the vendor-held records that expire first, into storage you own (M, Tier B).
- Put one gateway in front of direct model calls, observe first, bind every key to an owner, and treat it as tier 0 (M, Tier B).
- Evaluate before trusting and on every model change, with a planted test in your own tenant before any efficacy-based purchase (M to L, Tier A and B).
- Pre-authorize only scoped, reversible, pre-tested containment and gate everything else (M, Tier B).
- Read the not-yet list before buying, and put the dated re-decision triggers on a calendar now (S, Tier D).

Any L action routed elsewhere carries a high-priest cost line (a custom build needs a person who understands it and a second, for as long as it runs) and the configure-first alternative where one exists.

## Why this matters

A practitioner reading the routed documents gets more actions than a team of two can take in a quarter, so the order carries much of the value. It also has to survive a market where much of the product surface was renamed, acquired or put behind a preview banner during 2026, which is why each decision is keyed to what it produces rather than to a product, and why the waits are written down as decisions. The most common failure I have seen is buying a sensor before knowing what the licensed stack already records, which is a sequencing error before it is a technology one.

## The sixteen decisions

Speakers are cited by surname from the two 2026 [un]prompted practitioner conferences (March and October), Tier B, paraphrased because the source text is an auto-transcript.

| # | Decision | Who argued it | Tier | Caveat |
|---|---|---|---|---|
| 1 | Own or rent, sized to the team; small and mid-sized organizations lean to vendor-managed surfaces through a gateway | My first perspective (below); the CoSAI component map; Grinstead as the large-team counter-case | B; D for the ownership reading | Renting moves risk into what the vendor logs, so the choice is which visibility gaps you accept |
| 2 | Decide risk tolerance once, then build paved roads and monitor the detours | Grinstead | B, one CISO | The large-team version of row 1 |
| 3 | Establish system ownership before scaling any AI review or control | Karimi | B | Unit cost unknown to the speaker; the review load fell on a small team |
| 4 | Configure what you own first: quantify, evaluate, buy, then build | My second perspective; Wood; Iqbal; Woodruff | B; D for how much is present | Every custom build carries the high-priest cost |
| 5 | Force model traffic through a gateway you own and treat it as tier 0 | Woodruff; Sima and Eckmann; Bursztein | B | It counts only if nothing routes around it, and its logs are what an attacker reaches first |
| 6 | Give every agent its own identity, tiered by the data it touches, with approvals and credentials bound per action | Woodruff; Garg; Finol; Agrawal | B | An approval proves a human clicked, not that they understood (McMillin) |
| 7 | No long-lived agent credentials; mint per call through a broker the agent never sees | Grinstead; Finol; Zimmerle | B | The broker becomes the prize; LiteLLM, an open-source AI gateway, had three vulnerabilities added to the CISA KEV catalog in 2026 |
| 8 | Log before you buy: pick the record tier, land content in storage you own, send metadata to the SIEM | `what-to-log-and-what-it-costs.md`; Schneier; Finol | B | Content logs serve investigation more than detection, and EU law decides whether capture is viable |
| 9 | Deterministic first; the model is never the final authority | Six March talks; Deshpande; Garg | B | Prescriptive rules belong in the enforcement layer and descriptive ones in the reasoning layer (Yu), and descriptive skills transfer across models while prescriptive ones break (Dye) |
| 10 | Pick one end-to-end outcome metric before buying an AI finding tool | Molnar; Kim; Ravipati | B | Speed moves to wherever the human gate sits |
| 11 | Evaluate before trusting and on every model change | Meyerovich; Kovalsky and Arshad; Dye; Waitzenberg and Harush | B | Benchmark numbers degrade over multi-step work; the agent should not grade itself |
| 12 | Pre-authorize only scoped, reversible, pre-tested containment | Nagarajan; Jaksic | B | Speed asks for pre-authorization and trust asks for a gate |
| 13 | Test the control itself, adversarially, with canaries | Cuthbert; McMillin; Severi | B | Cuthbert reported that most agent harnesses tested so far sit on the lowest sandboxing rung, and another speaker that models have escaped nearly every sandboxing product (Nevo) |
| 14 | Keep a defensive open-weight capability and inventory its provenance | Sima and Eckmann; Meyerovich | B | One talk stated that no deployable trojan detector exists |
| 15 | Treat context management as a control to monitor | Lambros and Wilmot; Nevo; Dye | B; C for one sponsor-presented decay figure, flagged | The 0 to 38 percent governance-decay figure is one measurement, from a talk with a vendor sponsor |
| 16 | Decisions not to make yet (below) | My synthesis | D | Each wait names the trigger that ends it |

## The sequence, as data

The routing order within a priority band follows these eight groups. The family assignment is mine (Tier D) and is written as data so `scripts/route.py` can read it; a row listed under `row-overrides` takes its own group rather than its family's.

```yaml
sequence-order:
  1-ownership: [profile, surface]
  2-risk-tolerance-and-owners: [governance]
  3-configure-what-you-own: [shadow-ai, saas, assistant-oversharing, coding-agent, mcp, agent-builders, rag]
  4-gateway-and-identities: [identity]
  5-log-tier: [record]
  6-evaluation: [artifacts, soc, ai-you-ship]
  7-containment: [incident-response]
  8-vendor-conversation: [frameworks]
row-overrides:
  containment-pre-authorized-broad: 7-containment
  vendor-evaluation-in-progress: 8-vendor-conversation
  custom-build-planned: 8-vendor-conversation
  vendor-terms-unknown: 8-vendor-conversation
```

## The 90-day, one-year and later order

Two rules set the order. Each step is cheaper and easier to reverse than the next, so a gap moves forward only when the current step has been shown not to reach it, and nothing in the first two horizons depends on a feature that is only claimed, so a feature behind a preview label appears only as a trigger.

### First 90 days: decide, inventory, switch on, lock

| Step | What | Rows | Produces | Small and mid-sized | Large or regulated |
|---|---|---|---|---|---|
| 1 | Record rent-or-own, the sanctioned list, the risk tolerance and an owner per sanctioned system as one dated note | 1, 2, 3 | The surface list that scopes every later step | One page: rent the assistant, the managed platform and API use through a gateway | The three-cell test per owned surface (below) |
| 2 | Inventory entitled, available and enabled features over the sanctioned products | 4 | The turn-on list and first gap list | A licence and settings audit | One inventory for security and the regulator |
| 3 | Write the capture-tier policy; open DPIA and works-council talks where they apply | 8 | The legal basis for step 4 | Metadata plus exported verdicts | DPIA and works agreements |
| 4 | Turn on and export records with a vendor retention clock, plus IdP and cloud control-plane audit, into a store you own with identity, model and tool in typed columns | 8 | The identity-keyed metadata stream | Object storage plus a SIEM projection | An owned landing schema |
| 5 | Lock the managed settings tier and write deny rules for each sanctioned coding agent, by MDM | 4, 9 | The tool-decision record | Same | Same, under build review |
| 6 | Start shadow-AI discovery from sensors you hold: the CASB AI category and tenant-restriction headers, the OAuth consent-grant query, endpoint queries for extensions, AI runtimes, loopback listeners and model or MCP config paths, and an AI-provider filter on secrets scanning | 4 | The device table and first list of unsanctioned runtimes | Start at the consent-grant query without an SSE | Add process-attributed network events |
| 7 | Inventory direct API keys, bind each to an owner, run the gateway in observe mode | 5, 7 | The credential key for the join | A rented gateway | Decide which gateway you will own |
| 8 | Owners only: digest every held model, apply a format policy at intake, classify each fine-tune with its training data, close unauthenticated serving paths | 14 | The model inventory and exposure baseline | Usually not applicable | Mandatory |
| 9 | Stand up a build review gate for every AI-security build | 4 | The build register | A row per glue script | A standing review board |

This is a full quarter for a team of two. If something has to slip, I'd let step 7 slip before step 4, because vendor-held retention windows are the only clock on the list that deletes evidence (dated per platform in `telemetry-by-surface.md`). The list assumes an EDR and an IdP with usable logs; without them there is less to configure and the rent decision carries more of the load.

### First year: join, evaluate, tighten, buy what stays blind

1. Join what the first 90 days switched on over four keys (host, identity, resource, credential), which gives the first reliable inventory of AI in use and the denominator every later evaluation needs (rows 3, 4; `inventory-and-shadow-ai.md`).
2. Move the gateway to enforce once every key has an owner (rows 5, 7).
3. Agree the triggers for on-demand content capture with privacy and works councils, with a measured redaction recall in the DPIA (row 8).
4. Finish the coding-agent order: MCP allowlist with a manifest snapshot and diff, the required sandbox, one fail-closed hook only where deny rules cannot reach (rows 4, 9; `coding-agent-hooks-and-policy.md`).
5. Large or regulated, and any owner: per-agent IdP identities, a record of what the IdP writes per hop, and an evaluation harness before the first owned model serves traffic (rows 6, 11, 13, 14). Small and mid-sized: quarterly agent offboarding queries.
6. Test the flagged add-ons and the guardrail you already own with a planted event in your own tenant, then buy only for what stays blind, on one-year terms (rows 10, 11, 13; `reading-vendor-claims.md`).
7. Write the pre-authorized containment list and canary-test it (rows 12, 13).
8. Review SaaS AI toggles and subprocessor changes quarterly, re-read logging defaults, and enable the non-default cloud audit paths for inference (row 4; `saas-embedded-ai-and-vendor-terms.md`).
9. Run the first rationalization pass over the build register; EU-exposed organizations classify systems against Annex III ahead of 2 December 2027 (rows 4, 8).

### Later: re-decide on triggers, and only then own more

The later horizon is mostly re-decision: content capture stays exception-only, agent records move off the interim OCSF 1.9.0 landing only when a release carries an agent class, a cross-vendor control-state product is a second-year question at the earliest, context management is monitored wherever agents run long sessions, and owning a surface comes back only on a named need, with the evaluation harness as a prerequisite (rows 1, 14, 15).

## The four perspectives behind the order

These are my stated views as a practitioner, dated 2026-11-09, Tier D. They set the order within a priority band and never raise a priority or a tier.

The first is that vendor-managed parts of the AI deployment surface may be preferable depending on the organization, because for small and mid-sized companies a larger owned surface, self-hosted serving of fine-tuned models being the clearest case, is a real challenge in a sector this new and this fast. The cost side is the CoSAI component map, on which the organization owns every component it instantiates on only three surfaces (S9 self-hosted serving, S11 fine-tuning, S12 RAG stores), a one-author reading argued in `surface-ownability.md`. Extending the view to S12 is my reading too, with a limit, since a company of a few hundred people will usually want AI grounded in its own documents, so renting S12 means the assistant's own grounding or a managed knowledge base, and the permissions on the source documents stay the organization's to own.

The second is configure before you buy. Incumbent platforms have extended toward AI governance, so the first question is what the held stack would cover if it were understood and turned on, and my observation from operational work before August 2026 is that on the order of 80 to 90 percent of what I needed was already present, mostly unconfigured or misconfigured. That is a dated observation, not a measurement, and a gap below names what would test it.

The third is that every custom build gets a high priest: a person who has to understand it, plus the coordination cost of everyone who depends on that person, so an organization that favours building needs an architecture-review and rationalization process, heavy centralization on a few core systems or vendors with lock-in treated as close to permanent, or both.

The fourth is to decide slowly while the domain moves fast: record why each decision was made, key it to components and data flows rather than products, pin and re-check versions, prefer controls you can verify, and write down the waits.

## Variants of the sequence

The review prints which variant it applied, so the reader can see why.

Small-org (under about 1,000 people, no sector regulator, no owned surface): ninety-day steps 1 to 7 with step 9 reduced to a row per glue script, and year-one steps 1, 2, 4, 6 and 8, with step 5 reduced to the offboarding queries.

Own-by-mandate (`profile-override-own-by-mandate`, for residency, a supervisor's expectation about processing location, cost at volume or a capability): perspective one's sizing argument is not applied. Each owned surface takes a three-cell test instead, naming the need renting cannot meet, an owner and a second person who can patch, log and answer for it, and the telemetry contract it meets before going live, and a surface that cannot fill all three is rented. Ninety-day step 8 is mandatory and follows step 2, and the year-one evaluation harness is a prerequisite for serving traffic.

Gateway-chosen (`profile-override-gateway-chosen`): ninety-day step 7 records the chosen gateway as tier 0 and binds keys to owners, starting in enforce mode only if every key already has one, and the gateway's own record joins step 4's export list.

## Decisions not to make yet

Waiting is a decision too, and while the market and the law settle it is often the cheaper one. These are my judgements, Tier D, on the sources named.

| Not yet | Why wait | What ends the wait |
|---|---|---|
| An inline prompt-injection classifier bought on an efficacy page, or a second one beside the guardrail you own | Adaptive attacks reverse static benchmark results (Nasr, Carlini et al., Tier A, vendor-affiliation flag) | Written vendor answers and a planted test in your tenant |
| Continuous content capture over EU staff, or an insider-risk classifier over employee prompts | Doubtful for a private employer after CJEU C-65/23; the classifier may itself fall under Annex III 4(b) (Tier D reading; `prompt-capture-and-the-law.md`, not legal advice) | A final EDPB guideline, a supervisory decision or a court reading |
| An MCP gateway for policy, or a fleet-wide fail-closed hook | A gateway covers only the remote hop; a hook misfire hits every developer at once | Hooks-first steps in place; a measured false-deny rate |
| Treating any "complete visibility" AI inventory as complete | At least one cloud AI posture product excludes self-hosted models and agents by its own documentation | A tool that reads local model stores, confirmed by a re-run |
| Self-hosting or fine-tuning without a named need | Owned components bring patching, logging, identity and detection | A named need, plus an owner and a second |
| A standards-mapping product, or a vendor chosen on "mapped to MITRE ATLAS" | A mapping is a cross-reference, not a detection result (`frameworks-and-what-they-reach.md`) | A planted-event result per mapped technique |
| Re-platforming detections onto a proposed OCSF AI agent class | Not in a release (OCSF 1.9.0) | An OCSF release carrying it |
| SPIFFE-style agent identity on the promise, reasoning-trace monitoring in production, or a weight-level backdoor detector | One production report for the first; no peer-reviewed evaluation of a commercial detector | A second production report; a peer-reviewed evaluation |
| Multi-year contracts in NHI and AI-security point categories | Five of the twelve NHI vendors the series tracked changed hands between June and September 2026 | The category settles |
| Building a sensor of any kind | It duplicates what the market sells without cross-customer cost sharing | For the large reader, a gap no vendor sells into that passes the build gate |

## Re-decision triggers

The dated rows go on a calendar now; the signal rows are short enough for one person to read monthly from release notes, the CISA KEV feed and the standards repositories.

| Date or signal | Event | Reopens rows |
|---|---|---|
| 2026-12-02 | EU AI Act Article 50 marking grace period ends for generative systems already on the market (Regulation (EU) 2026/1744) | 8 |
| 2027-05-21 | Google Cloud Security Command Center Enterprise tier retired, automatic move to Premium (Tier B, vendor documentation) | 4, 10 |
| 2027-12-02 | Stand-alone Annex III high-risk obligations, including Article 26 deployer duties, apply | 3, 8 |
| 2028-08-02 | Annex I obligations apply | 8 |
| Each build's sunset (at most twelve months) and each contract renewal | Build re-decision; export schema as a contract term | 1, 4, 10 |
| A preview feature goes generally available, or a platform changes a logging default or the tier of its audit record | Content logging on by default; an audit log at a lower tier | 1, 4, 6, 8 |
| A MITRE ATLAS release adds a case study on a surface you run | ATLAS has shipped monthly | 1, 10 |
| A KEV entry for a gateway, agent builder or inference engine you run or rent | A fourth LiteLLM entry; a first for an inference server | 1, 5, 14 |
| An acquisition of a vendor you hold in a sensor family | As in the NHI churn above | 6, 10 |
| An OCSF or MCP specification release, or a coding agent changing a lock or failure default | An AI agent activity class; a protocol revision past 2026-07-28 | 5, 6, 8, 9 |
| A model change behind any evaluated system, or a new named need to own | Version, quantization or fine-tune; a regulator expectation | 1, 11, 14 |

## What this does not mean

The sequence is not a maturity score, and a regulated organization that owns a surface by mandate may rightly do ninety-day step 8 in its first week. It does not say buying is wrong, only that buying goes better last, when the inventory can say what the purchase is for. And it does not carry the sixteen as converged practice: the talks agreed broadly on four things (the model is not the control point, borrowed identity is the failure mode, log at a gateway you own, evaluate before you trust), argued about most of the rest and rarely named a published standard, so `convergence` stays single-source.

## Gaps

- **Gap: the order itself**. No study shows that this order, or any order, produces better outcomes than another. **Needs**: dry runs of the review on the three fixtures with a second reader re-sorting the output, then reports from practitioners who ran the sequence for two quarters or more.
- **Gap: how much of the held stack goes unused**. The 80 to 90 percent observation is one practitioner's view, and the series' count of governance features against CoSAI components measures something different, so the two are never quoted together. **Needs**: a measured study of entitled versus enabled AI-relevant features across several organizations' licence and settings exports.
- **Gap: what network-only discovery misses**. The share has a planning model and no measurement, so it is never a headline. **Needs**: a lab bench on a mixed fleet measuring network-invisible AI use against an endpoint and IdP join.
- **Gap: fail-closed hook cost**. The wait on a fleet-wide fail-closed hook rests on reasoning, not a measured false-deny rate. **Needs**: a replay corpus of real tool calls and a bench measuring the hook's false-deny rate on it.

## Notes

- Status (2026-11-10): ships `EMERGING` ahead of the long-form article that argues the sequence (`DECISIONS.md` Decision 15) and gains a `follows:` line naming the article when it publishes.
- Measurement claims: none. The lab figures the decisions rest on live in the routed documents, pinned to lab master at `91e44df` (the research branch merged there on 2026-11-10).
- The 80 to 90 percent observation (dated 2026-11-09) is a perspective, not a measurement; any anecdote behind it comes from operational work before August 2026 or is stated generally.
- Revalidate-by is three months out because ATLAS releases and the 2026-12-02 trigger fall inside the window. Products in the trigger table are examples of a trigger kind; nothing here says any named organization runs any product.

## Sources

Tier A

- Regulation (EU) 2024/1689 (AI Act), consolidated text CELEX 02024R1689-20260727, and amending Regulation (EU) 2026/1744, read 2026-11-09: https://eur-lex.europa.eu/eli/reg/2024/1689/oj
- CJEU, Case C-65/23, judgment of 19 December 2024: https://curia.europa.eu/juris/liste.jsf?num=C-65/23
- Nasr, Carlini et al., "The Attacker Moves Second," arXiv 2510.09023, accepted at USENIX Security 2026 (figures from arXiv v1; authors affiliated with model vendors, flagged): https://arxiv.org/abs/2510.09023

Tier B

- [un]prompted practitioner conferences, March and October 2026, talks by the speakers named in the table; auto-transcripts read by line, paraphrased here.
- CoSAI secure-ai-tooling risk map at commit 622605a1: https://github.com/cosai-oasis/secure-ai-tooling/tree/622605a1
- CISA Known Exploited Vulnerabilities catalog, catalogVersion 2026.11.09: https://www.cisa.gov/known-exploited-vulnerabilities-catalog
- OCSF schema 1.9.0: https://schema.ocsf.io/
- MCP specification 2026-07-28: https://modelcontextprotocol.io/specification
- MITRE ATLAS v2026.10: https://atlas.mitre.org/
- Google Cloud, "AI Protection overview" (Security Command Center tiers and Enterprise shutdown date), read 2026-11-09: https://docs.cloud.google.com/security-command-center/docs/ai-protection-overview

Tier D

- My four perspectives and the ordering, dated 2026-11-09, argued at length in the forthcoming capstone article of the securing-AI series on securitydataworks.com.
