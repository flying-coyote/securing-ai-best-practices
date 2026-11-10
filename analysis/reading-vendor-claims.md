---
evidence-tier: Mixed
convergence: single-source
applies-to-signals: [vendor-evaluation-in-progress]
surfaces: [S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12, S13]
pins:
  - "MITRE ATLAS v2026.10"
  - "CoSAI secure-ai-tooling 622605a1"
  - "OCSF 1.9.0"
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-02-17
status: EMERGING
measurement-claims:
  - claim: "A pre-registered prompt-injection signature rule over the OCSF message_context.prompt_text field was MISSED on all three seeds on the pre-registered DuckDB engine (case-sensitive LIKE) and NOISY on SQLite at precision 0.048; authored corpus, one host"
    source: "sdw-lab-benchmarks@91e44df atlas-ocsf-observables/RESULTS.md:111,125-128,146-148"
    date: 2026-11-10
    revalidate: 2027-02-17
  - claim: "Of 8 pre-registered ATLAS techniques with a mapped OCSF field, 2 were DETECTED, 5 NOISY and 1 MISSED, stable across three seeds"
    source: "sdw-lab-benchmarks@91e44df atlas-ocsf-observables/RESULTS.md:113,145"
    date: 2026-11-10
    revalidate: 2027-02-17
  - claim: "Of six AI artifacts planted on one host, the union of Syft, Trivy, ai-bom and cyclonedx-py found 3 of 6 under the pre-registered strict name match without Trivy rootfs mode and 1 of 6 as an AI artifact; the same weights inside an Ollama store were seen by no tool, and no tool marked either installed MCP server package as an MCP server; in a labelled post-hoc run ai-bom did label both servers from client config files, with no version and no link to the package or its advisories"
    source: "sdw-lab-benchmarks@91e44df ai-artifact-sbom/RESULTS.md:40-44,57,66-68,127-133"
    date: 2026-11-10
    revalidate: 2027-02-17
  - claim: "A snapshot-and-diff detector over three real MCP servers fired on 9 of 9 poisoned mutations and on 12 of 15 (OCSF-native any-drift rule) or 9 of 15 (contract-drift rule) benign changes; a code-only change under a byte-stable manifest produces no manifest-level signal"
    source: "sdw-lab-benchmarks@91e44df mcp-manifest-drift/RESULTS.md:39,51-52,153"
    date: 2026-11-10
    revalidate: 2027-02-17
  - claim: "One real MCP tools/call recorded as 33 facts typed 24 in OCSF main with the ai_operation profile, 19 in OpenTelemetry GenAI plus MCP conventions and 11 in OWASP AOS on OCSF; the reference SDK server sent a syntax error, a rejected DROP and a missing table to the wire as the same text"
    source: "sdw-lab-benchmarks@91e44df agent-toolcall-schemas/RESULTS.md:44-47,49,57"
    date: 2026-11-10
    revalidate: 2027-02-17
---

# Reading vendor claims: four sentence types that fail and the four-part procurement ask

Evidence tier: Mixed. Tier C, bias flagged, for every vendor quote about efficacy or coverage; Tier B for vendor descriptions of what a feature does, for UK NCSC guidance and for the lab runs, which test the mechanisms the claims rely on rather than any vendor's product; Tier A for the peer-reviewed adaptive-attack and detector-evaluation work; Tier D for the four-part ask and the sentence-type grouping, which are my judgement.

## Summary for the review

Much of what the AI-security vendors sell is real, but four kinds of sentence keep appearing in their marketing that fail for architectural reasons that better engineering does not fix: "stops" or "blocks" prompt injection with no rate, "every agent" or "complete visibility", manifest or catalogue inspection that "detects" poisoning, and "mapped to MITRE ATLAS" offered as coverage. So the useful move in an evaluation is to ask four things in writing and judge the answers.

- Ask which sensor the product sits on, and get its placement in your environment named. Effort S. Tier D for the ask; Tier B for why sensor position decides reach.
- Ask on which surfaces that sensor sees, as a list of the tenants, browsers, endpoints and egress paths you would connect, and treat anything outside the list as not covered. Effort S. Tier D; lab mechanism evidence B.
- Ask what export schema the product emits, with a sample record and its field list (OCSF 1.9.0 `ai_operation`, OpenTelemetry GenAI attributes, or the vendor's own JSON). Effort S to ask, M to check the sample. Tier B.
- For any detection or blocking claim, ask which adaptive attack set it was evaluated against, at what false-positive rate, and on inputs shaped like yours, then run a time-boxed test on your own traffic before relying on the number. Effort M. Tier A for why static benchmarks overstate robustness.
- Rewrite each absolute claim into its deliverable form ("reduces the rate of known patterns", "every agent in the sources you connect") and buy against that form. Effort S. Tier D.
- Count a vendor efficacy or coverage number as Tier C with the vendor's incentive flagged, so it never raises a finding's tier on its own, and never add market-map category counts into a market size. Effort S. Tier D for the rule.

## Why this matters

The AI-security market grew faster than anyone's ability to test it. One public census, the AI Security Startups Map, lists 470 vendors whose 14 category tags sum to 1,252, a mean of 2.66 tags per vendor with 51 carrying a single tag, so a figure like "306 governance vendors" means 306 firms that tagged themselves with governance among other things, and the category counts can't be added up into a market (Tier C, curated by a vendor that SentinelOne acquired in August 2025, so it is an incumbent's view of its competitors; counts recomputed from the map's `/api/vendors` on 2026-11-09). Over 2025 and 2026 incumbents in five sensor families (SASE and SSE, browser, EDR, identity, and network and application delivery) bought many of those firms, each extending the surfaces its sensor already reached, so a buyer is usually reading marketing for a bundle of discovery, policy and inline inspection and has to take it apart one capability at a time. I read sixteen dated vendor claims against independent evidence and against lab runs that test the mechanisms those claims depend on; fifteen are in the ledger below, and one was dropped because its quoted phrase could not be found in any source.

## The four sentence types and why each fails

The first type is "stops" or "blocks" prompt injection, stated without a rate. An inline guardrail is a learned classifier in front of a model that has no internal boundary between data and instruction, and the attacker can query and optimize against that classifier, so the defender is measured against yesterday's attacks while the attacker moves second. The peer-reviewed record now measures this directly. Nasr, Carlini and twelve co-authors bypassed 12 recent defenses with tuned adaptive attacks, above 90 percent success for most of them where most had reported near-zero, and for the detector class the spread runs roughly 49 to 99 percent depending on base model and detector; the Protect AI detector goes from 0 to 31 percent attack success on static attacks to 81 to 94 percent under adaptive search (Tier A, USENIX Security 2026, numbers from arXiv v1 Table 7, camera-ready not read, so they may move; affiliation flag, since the authors include frontier-lab researchers and Google's Model Armor is among the detectors attacked). Zhan and colleagues bypassed all eight indirect-injection defenses they tested at over 50 percent (Tier A, Findings of NAACL 2025), LLMail-Inject measured models that sit below 5 percent attack success on existing benchmarks at 32 to 58 percent against human adaptive attackers and Microsoft's own text classifiers at 0.425 to 0.678 recall on successful attacks (Tier A, Findings of EMNLP 2026, Microsoft-led, flagged), and Hackett and colleagues reached up to 100 percent evasion of six commercial and open detectors with character injection, though "up to 100" is the best technique and Protect AI v2, the hardest of the six, averaged 20.26 percent (Tier A, LLMSec 2025, Mindgard co-authors, flagged because Mindgard sells guardrail red-teaming). The UK NCSC says it plainly to buyers: "Beware any that claim they can 'stop' prompt injection, and instead look at those who understand how they *reduce* it" (Tier B, NCSC, 2025-12-08). Nasr and colleagues also concede that detectors still block "some unsophisticated or opportunistic attacks", which is the deliverable half, a lower rate on known patterns plus friction for low-effort attackers. The architectural answer is to limit what a confused model can do (CoSAI `controlAgentExecutionBounds`, `controlAgentPluginPermissions`, `controlAgentCredentialIsolation`), and that half has peer-reviewed support too, since in AgentDojo tool filtering cut targeted attack success to single digits while failing in the 17 percent of cases where the tools a task needs also suffice for the attack (Tier A, NeurIPS 2024). A rule can also break with no attacker at all, as in a run I did in sdw-lab-benchmarks, where a pre-registered prompt-injection signature over a well-typed OCSF prompt field missed the planted attack on all three seeds on DuckDB because the compiled `LIKE` was case-sensitive, and fired noisily on SQLite at precision 0.048 (Tier B, sdw-lab-benchmarks@91e44df `atlas-ocsf-observables/RESULTS.md:111,125-128,146-148`, authored corpus, one host, verified with fixes).

The second type is "every agent", "every AI asset" or "complete visibility". That is a closed-world claim over the reach of a sensor, and each sensor family has a known edge. Unsanctioned AI tends to live where there is no sensor: extensions and AI browsers on unmanaged devices, open-weight models running offline on a laptop, citizen-built agents on a platform nobody connected, and calls made with a personal API key from a home network. In the same lab, six AI artifacts planted on one host were found three of six times by the union of four SBOM and scanner tools under the pre-registered name match with Trivy in its default mode, one of six as an AI artifact, the same model weights inside an Ollama store were seen by no tool, and no tool marked either installed MCP server package as an MCP server, though in a labelled post-hoc run ai-bom did label both servers from the client config files that declared them, with no version and no link back to the package or its advisories (Tier B, `ai-artifact-sbom`, one host, verified with fixes). Discovery finds what the scanner was built to recognize in the places it was given access to, so the defensible version of the sentence is "every agent in the tenants, browsers and endpoints you connect".

The third type is that manifest, gateway or catalogue inspection "detects" tool poisoning or supply-chain swaps. Protocol-layer inspection sees descriptions, schemas and names change, and it sees change rather than intent. A snapshot-and-diff detector over three real MCP servers fired on 9 of 9 poisoned mutations, but also on 12 of 15 benign changes with the OCSF-native rule and 9 of 15 with a contract rule, because a hidden instruction and a typo fix produce the same fingerprint change; body-aware text rules separated the sets on that corpus, though I wrote both sides and the real-release arm has not run (Tier B, `mcp-manifest-drift`, verified with fixes). A server whose code changes under a byte-stable manifest produces no protocol-level signal at all, and a catalogue keyed by name and version misses a same-name, same-version content swap. Tool poisoning is ATLAS AML.T0110 AI Agent Tool Poisoning (Tier A, ATLAS v2026.10), and detecting it needs build-time provenance and server-side behaviour, which is a different sensor from the one being sold.

The fourth type is coverage expressed as "mapped to MITRE ATLAS" or "covers the OWASP Top 10". A mapping is a cross-reference between a feature and a technique name. When I ran eight ATLAS techniques that each had a mapped OCSF field against planted events, two produced a clean detection, five were noisy and one was missed, stable across three seeds (Tier B, `atlas-ocsf-observables`, verified with fixes). A heatmap of green cells over ATLAS says the vendor has read ATLAS, which is worth something for triage, but it isn't a measure of what the product would have caught.

## The four-part procurement ask

The four questions follow from the four failures, and a vendor that can answer them in writing is probably selling something real.

| Part | Ask in writing | A good answer | What it guards against |
|---|---|---|---|
| Sensor | Which sensor does the product depend on (API connector, inline proxy or gateway, endpoint agent, browser extension, SDK hook), and where would it sit in our environment? | A named placement and what traffic or state passes it | "Every" and "complete" claims that outrun the sensor |
| Surfaces | On which of our surfaces does that sensor see, listed by tenant, browser, endpoint class and egress path? | A list, with what is out of scope said out loud | Unmanaged devices, local models and personal API keys assumed covered |
| Export schema | What record does the product emit, in what schema, with a sample event and field list? | OCSF 1.9.0 `ai_operation`, OpenTelemetry GenAI attributes, or a documented JSON shape with a sample | A verdict that stays in the vendor console and never reaches the SOC |
| Adaptive evaluation | Against which adaptive attack set was any detection or block rate measured, at what false-positive rate, on inputs shaped like ours? | A named set with an adaptive arm, a stated false-positive rate, and willingness to run on our traffic | "Blocks injection" and "99% efficacy" on a static, self-chosen benchmark |

The export question is the one I'd ask first in a security-data practice, and the market answers it worst. One run recorded a real MCP `tools/call` as 33 facts, of which 24 were typed in OCSF main with the `ai_operation` profile, 19 in OpenTelemetry GenAI plus MCP conventions and 11 in OWASP AOS on OCSF, and it found that the reference MCP SDK server sends a syntax error, a rejected `DROP` and a missing table to the wire as the same text, so the cause never leaves the server process and no client-side record or product watching the wire can carry it (Tier B, `agent-toolcall-schemas`, verified with fixes). Across roughly forty products whose public pages I read, none stated that it emits OCSF 1.9.0 `ai_operation` or OpenTelemetry GenAI attributes, though I read marketing pages and some documentation rather than every documentation portal, several of which are behind a login (Tier B for the absence on the pages read, 2026-11-09).

On the fourth part, PIDS-Bench found a detector above F1 0.98 in distribution still misclassified roughly a third of an external benign set (Tier A, IEEE Access 2026), which is why the false-positive rate on your own inputs sits inside that part. Until a time-boxed test on your own traffic runs, the product sits as claimed rather than verified, in the grading `configure-before-you-buy.md` uses.

## Claims ledger

Each row is a short phrase from the vendor's own page or release, tagged per clause: Tier C, bias flagged, for any efficacy or coverage claim, and B only where the clause describes what a feature does. "Live 2026-11-10" means I re-read the phrase on the live page that day; "read 2026-11-09" means it was read once through a fetch tool and has not been re-read. No product was tested, and the vendors are named because the claims are public and the acquisition announcements are in the public record, not because any organization is assumed to run them. The name in brackets is the announced acquirer, and several of those deals (Check Point and Lakera, CrowdStrike and Pangea, CrowdStrike's SGNL and Seraphic deals, Varonis and AllTrue.ai) had no primary completion notice I could confirm.

| # | Vendor (acquirer), category | Claim, tier and quote state | Type | Deliverable form |
|---|---|---|---|---|
| 1 | Lakera Guard (Check Point), guardrail | "Prompt injection, jailbreaks, and adversarial instructions blocked before they reach the model." (C) Live 2026-11-10 | 1 | A lower rate on known patterns, testable on your traffic |
| 2 | CrowdStrike (Pangea), AI detection and response | "up to 99% efficacy at sub-30ms latency", footnoted "internal benchmark testing on GPU-based edge deployment" (release 2025-09-16) (C; "up to" makes the best case the headline). Confirmed through release snippets; primary returned 403 | 1 | Credit for footnoting the method; uncheckable until the attack set and false-positive rate are published |
| 3 | Noma, agent security; Runlayer, MCP gateway; Oasis (Cyera), NHI | Noma "Discover every agent, MCP, skill, and tool, and surface risk", live 2026-11-10; Runlayer "See every agent, MCP, and skill in use" and Oasis "See every non-human identity in real time", read 2026-11-09 (C, all three) | 2 | Every one in the sources you connect; ask for that list |
| 4 | Harmonic, shadow-AI discovery | "The only platform that classifies every AI task", beside controls "where the surface supports them" and coverage "expanding as more endpoints and integrations come online" (C for "only" and "every"; the two scoping phrases are B). Live 2026-11-10 | 2 | The headline overclaims, but the page states its own limits, which is the scoping I'd want every vendor to publish |
| 5 | Wiz (Google), AI-SPM | "Discover AI services, technologies, and SDKs without any agents" (B, agentless discovery is a feature); "Uncover shadow AI" (C, coverage). Live 2026-11-10 | 2 | Deliverable inside connected cloud accounts and repositories; there, shadow AI means unsanctioned cloud AI, not laptop or browser use |
| 6 | Zenity, agent security | "Detect threats, investigate, and respond, mapped to OWASP and MITRE ATLAS." (C, coverage by mapping) Live 2026-11-10 | 4 | A useful cross-reference for triage, not detection coverage |
| 7 | Snyk (Invariant Labs), MCP security | Credited with "discovering and naming attack terminology such as 'tool poisoning' and 'MCP rug pulls'" (release 2025-06-24) (C, a credit claim in the acquirer's own release, though Invariant's own 2025-04-01 post does introduce the term "Tool Poisoning Attack"). Live 2026-11-10 | 3, by category | The quote claims no detection; the type applies to the MCP scanning the deal brought, where change detection is cheap and real and a code-only rug pull is invisible to a manifest scanner by construction |
| 8 | Palo Alto Networks (CyberArk); CrowdStrike (SGNL), identity | "secure every identity across the enterprise - human, machine, and agentic" (2026-02-11); "every agent a privileged identity that must be protected" (2026-01-08) (C, coverage). Read 2026-11-09 | 2 | Issuing and scoping agent identities; tracing a multi-hop delegation needs per-hop records many platforms don't yet emit |
| 9 | Proofpoint (Acuvity), AI usage control | "comprehensive visibility and enforcement across the full range of AI usage... and locally installed AI tools like OpenClaw and Ollama" (2026-02-12) (C, coverage). Read 2026-11-09 | 2 | Deliverable on managed endpoints running the agent; not on unmanaged or BYOD devices |
| 10 | HiddenLayer, AI detection and model security | "proactively defends against the full spectrum of AI threats"; "The most comprehensive security platform for AI" (C, superlative). Live 2026-11-10 | superlative | The page lists eight capabilities, from discovery and model scanning to runtime guardrails (B for what each does), and backs the superlatives with analyst recognition, awards and a company "75%" exposure-reduction figure (C), not a named independent test; ask the four parts of each capability |
| 11 | Palo Alto Networks (Protect AI), platform | "brings together model scanning, posture management, AI red teaming, runtime protection, and AI agent security" (2025-07-22) (B, feature list). Read 2026-11-09 | feature (B) | The scan is deliverable; a verdict carrying no digest or package identifier can't be joined to runtime telemetry about the same model. Protect AI's open injection detector, which need not be what the platform runs inline, is among those the adaptive-attack papers above bypassed (Tier A), the one place this ledger meets an independent measurement |
| 12 | F5 (CalypsoAI), inference guardrail | "the only full-lifecycle platform to secure AI models and applications at the inference layer" (2025-09-11) (C, superlative). Read 2026-11-09 | superlative | "Only" is marketing; the guardrail itself is a row 1 product |
| 13 | Varonis (AllTrue.ai), discovery and gateway | "Continuously discover AI assets, projects, and systems, including shadow AI"; "Enforce real-time policies via our LLM and tool-agnostic AI gateway" (C for "including shadow AI"; B for gateway enforcement). Read 2026-11-09 | 2 | Enforcement on routed traffic; shadow AI is by definition the traffic that isn't routed |
| 14 | Palo Alto Networks (Portkey), AI gateway | "an AI Gateway acts as the central nervous system for all AI traffic" (2026-05-29) (C, coverage). Read 2026-11-09 | 2 | "All" holds where egress is forced through it; direct API keys, local models and SaaS-embedded AI otherwise bypass it |
| 15 | CrowdStrike (Seraphic), browser security | "preventing shadow AI from scraping or exfiltrating" sensitive data (2026-01-13) (C, efficacy). Read 2026-11-09 | 1 | Deliverable on managed browsers; not in a second, unmanaged browser on the same machine |

## What this does not mean

It does not mean these products are bad or their builders careless, since much of what they sell is genuinely useful and the deliverable core is real: inventory within connected sources, identity issuance and scoping for agents, change detection on tool manifests, model-file scanning, and rate reduction for known injection patterns. It does not mean a guardrail is worthless either, because a lower rate on opportunistic attacks has value when the architecture already limits what a fooled model can do. And a vendor that answers all four parts well has shown it can be measured, which is different from having been measured on your traffic. For model and extension scanners I'd add a fifth question, what key the verdict carries, since a scan result with no content digest or signed manifest can't be joined to the inventory or the runtime record (Tier B, lab mechanism; Tier D for the ask). Finally, the lab rows test mechanisms on authored corpora on one host, so they bound what a class of product can see and say nothing about any vendor's accuracy.

## Gaps

- **Gap: G14, what "blocks prompt injection" means in measured terms**. No published, independent rate exists for a wrapped open classifier under documented transforms with confidence intervals, so this version names the failure mode from peer-reviewed work and carries no guardrail miss rates of its own. **Needs**: the T3 guardrail-adaptive bench in sdw-lab-benchmarks (open classifiers on public attack and benign sets under spacing, encoding and character transforms, paired-bootstrap intervals), which is written up and verified on branch hub/ai-research-2026-11-09 and enters this document once it is on the lab's main branch; Meta Prompt Guard 2 stays excluded while its weights are gated.
- **Gap: G21, primary pages not read**. Several primaries behind these claims returned 403 or 429 to my fetch: the SentinelOne Prompt Security release, the Zscaler investor-relations release, the CrowdStrike Pangea release (confirmed only through snippets), the Prisma AIRS product page and openai.com. **Needs**: a desk pass reading each primary directly, and a live re-read of the rows above still marked "read 2026-11-09".
- **Gap: export schemas behind login**. Vendor documentation portals that would state an export schema were often login-gated, so "none stated" is an absence on public pages, not a finding that none exists. **Needs**: sample events requested from vendors and contributed by category, mapped against OCSF 1.9.0 `ai_operation`.
- **Gap: real-release manifest drift**. The manifest-drift false-positive figures come from an authored corpus. **Needs**: the R5b arm in sdw-lab-benchmarks over the public release history of real MCP servers.

## Notes

- 2026-11-10, judgement marker: the four-part ask and the grouping of claims into four sentence types are my judgement (Tier D). The ask agrees with NCSC's buyer guidance and with the evaluation practice the detector literature recommends, but I found no test of whether it predicts outcomes in procurement.
- One of the sixteen claims I originally read, an MCP gateway release said to cover "more than 13,000 known MCP servers", was dropped because the phrase could not be found in any source; a document about reading claims shouldn't carry an unverifiable one.
- The OpenAI statement that prompt injection is "unlikely to ever be fully solved" is cited only through TechCrunch coverage (Tier C, secondary), because the original returned 403, so it supports nothing above.
- The Nasr et al. figures are from arXiv v1; if the camera-ready differs, the revalidation pass replaces them.
- 2026-11-10: lab citations point at lab master `91e44df`; they were first written against commit `e0aaadc` on branch hub/ai-research-2026-11-09, and the four cited RESULTS.md files are unchanged between the two, so the line ranges stand. Each run carries a VERIFIED-WITH-FIXES verdict from a second agent.
- Revalidate-by is three months out because the claims are vendor pages that change monthly and the tool-poisoning reference pins ATLAS.
- Build-versus-buy is in `build-buy-and-the-high-priest.md`; this document only covers reading what is offered.

## Sources

Tier A, peer-reviewed and standards

- Nasr, Carlini et al., "The Attacker Moves Second: Stronger Adaptive Attacks Bypass Defenses Against LLM Jailbreaks and Prompt Injections", USENIX Security 2026, https://www.usenix.org/conference/usenixsecurity26/presentation/nasr (arXiv 2510.09023 v1, §5.3, Table 7, App. G.1).
- Hackett, Birch, Trawicki, Suri and Garraghan, "Bypassing LLM Guardrails", LLMSec 2025, ACL Anthology 2025.llmsec-1.8 (vendor flag).
- Zhan, Fang, Panchal and Kang, "Adaptive Attacks Break Defenses Against Indirect Prompt Injection Attacks on LLM Agents", Findings of NAACL 2025, https://doi.org/10.18653/v1/2025.findings-naacl.395.
- Abdelnabi et al., "LLMail-Inject", Findings of EMNLP 2026, 10.18653/2026.findings-emnlp.514 (vendor flag).
- Debenedetti et al., "AgentDojo", NeurIPS 2024, https://doi.org/10.52202/079017-2636.
- Shire and Kim, "PIDS-Bench", IEEE Access 2026, https://doi.org/10.1109/access.2026.3728186.
- MITRE ATLAS v2026.10, AML.T0110 AI Agent Tool Poisoning, https://atlas.mitre.org/.
- CoSAI secure-ai-tooling, `controls.yaml` at `622605a1`, https://github.com/cosai-oasis/secure-ai-tooling.

Tier B, national guidance, lab runs and vendor descriptions of what a feature does

- UK NCSC, "Prompt injection is not SQL injection (it may be worse)", 2025-12-08, https://www.ncsc.gov.uk/blog-post/prompt-injection-is-not-sql-injection.
- sdw-lab-benchmarks@91e44df (lab master): `atlas-ocsf-observables`, `ai-artifact-sbom`, `mcp-manifest-drift`, `agent-toolcall-schemas` (RESULTS.md and VERIFICATION.md each), https://github.com/flying-coyote/sdw-lab-benchmarks.
- Acquirer releases for rows 2, 7, 8, 9, 11 to 15, as dated in the ledger, for the feature descriptions in them only (row 11, and the gateway-enforcement clause of row 13); every efficacy, coverage or credit phrase in the same releases is Tier C and listed below.
- Google's 2026-03-11 statement that it had closed the acquisition of Wiz ("Today, we announced we've closed the acquisition of Wiz"), read 2026-11-10 as reproduced by TelecomTV, https://www.telecomtv.com/content/digital-platforms-services/google-completes-acquisition-of-wiz-55062, since the Nasdaq copy of the release timed out (the fact of the acquisition for row 5).
- Invariant Labs, "MCP Security Notification: Tool Poisoning Attacks", 2025-04-01, https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks, read 2026-11-10 (where the tool-poisoning name appears, for row 7).

Tier C, vendor efficacy and coverage claims and secondary coverage, bias flagged

- Vendor pages re-read 2026-11-10: lakera.ai/lakera-guard, noma.security, harmonic.security, wiz.io/solutions/ai-spm, zenity.io, hiddenlayer.com, and the Snyk release on the Invariant Labs acquisition (snyk.io/news).
- Vendor pages and releases read 2026-11-09 through a fetch tool: Runlayer, Oasis, CrowdStrike (Pangea, SGNL, Seraphic), Palo Alto Networks (CyberArk, Protect AI, Portkey), Proofpoint (Acuvity), F5 (CalypsoAI), Varonis (AllTrue.ai).
- AI Security Startups Map, https://startups.prompt.security/ (data file pulled 2026-11-09; curator owned by SentinelOne).
- TechCrunch, "OpenAI says AI browsers may always be vulnerable to prompt injection attacks", 2025-12-22.

Tier D

- The four-part procurement ask, the four sentence types and the fifth scanner question: the author's judgement.
