---
evidence-tier: Mixed
convergence: single-source
applies-to-signals: [framework-claimed-atlas, framework-claimed-owasp, framework-claimed-nist-ai-rmf, framework-claimed-iso-42001, framework-claimed-cosai, framework-claimed-eu-ai-act, framework-claimed-scf, mapping-treated-as-coverage, owasp-ids-2025]
surfaces: [S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12, S13]
pins:
  - "MITRE ATLAS v2026.10"
  - "MITRE ATT&CK Enterprise v20.1"
  - "MITRE D3FEND 1.6.0"
  - "OCSF 1.9.0"
  - "CoSAI secure-ai-tooling 622605a1"
  - "NIST CSF 2.0"
  - "NIST IR 8596 iprd-2025-12-16"
  - "NIST AI RMF 1.0"
  - "OWASP Top 10 for LLM Applications 2026"
  - "OWASP Top 10 for Agentic Applications 2026"
  - "ISO/IEC 42001 2023"
  - "CSA AI Controls Matrix v1.1"
  - "AIUC-1 2026-10-15"
  - "EU AI Act consolidated CELEX-02024R1689-20260727"
  - "atlas-d3fend-crosswalk 65cdab0"
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-02-10
status: EMERGING
measurement-claims:
  - claim: "Of the 290 steps in ATLAS v2026.10's 27 Incident case studies, 235 (81.0%) reach some OCSF 1.9.0 field through the ATLAS-to-D3FEND crosswalk and 161 (55.5%) reach a specific one; the specific-versus-generic grades are one author's single pass and Tier D, and with the broad File and UserAccount artifacts set aside (not pre-registered) the specific share is 123 (42.4%)"
    source: "sdw-lab-benchmarks@91e44df atlas-ocsf-observables/RESULTS.md:32-36,58-62,198-202"
    date: 2026-11-09
    revalidate: 2027-02-10
  - claim: "Steps using the 36 techniques that carry an ATT&CK reference (122 steps) reach a specific OCSF field 85.2% of the time and some field 97.5%; steps using the 71 ATLAS-native techniques (168 steps) reach a specific field 33.9% and some field 69.0% (supplementary split, not pre-registered)"
    source: "sdw-lab-benchmarks@91e44df atlas-ocsf-observables/RESULTS.md:45-56"
    date: 2026-11-09
    revalidate: 2027-02-10
  - claim: "54 of the 55 incident steps with no OCSF field come from the 15 techniques that have no crosswalk row, and one from a mapped artifact (d3f:DigitalText) with no core field"
    source: "sdw-lab-benchmarks@91e44df atlas-ocsf-observables/RESULTS.md:85-87"
    date: 2026-11-09
    revalidate: 2027-02-10
  - claim: "Of 8 pre-registered ATLAS techniques with a mapped OCSF field, one Sigma rule each over a synthetic background gave 2 DETECTED, 5 NOISY and 1 MISSED in the core arm on DuckDB 1.5.3, stable across three seeds; the prompt-injection rule over message_context.prompt_text was MISSED on DuckDB (case-sensitive LIKE) and NOISY on SQLite; authored rules and corpus, one host"
    source: "sdw-lab-benchmarks@91e44df atlas-ocsf-observables/RESULTS.md:101-118,125-132"
    date: 2026-11-09
    revalidate: 2027-02-10
  - claim: "A blind second grader (one model, three passes) moved the R1 specific-field share from 161 to 168 of 290 (57.9%; passes 167 to 173) and the any-field share from 235 to 204 of 290 (70.3%), with five-category Cohen's kappa 0.452 on 79 artifact rows; the adjudication leg did not run, so no consensus grade exists (partial run, VERIFIED-WITH-FIXES)"
    source: "sdw-lab-benchmarks@91e44df m1-r1-blind-regrade/RESULTS.md:14-28"
    date: 2026-11-10
    revalidate: 2027-02-10
  - claim: "Of the top twelve ATLAS mitigations in a greedy step-coverage order, four have no artifact a check can key on; implementing the other eight as the check each mitigation's text describes, 1 of 22 rule-selected incident step-slots was CAUGHT on SQLite (7 NOISY, 8 MISSED, 6 MISSED by construction), and 2 on DuckDB, every state stable across three seeds; authored fixtures and checks, one host"
    source: "sdw-lab-benchmarks@91e44df t4-interdiction/RESULTS.md:37-58,139"
    date: 2026-11-10
    revalidate: 2027-02-10
  - claim: "Appending the crosswalk's core restrictions moved ATLAS from 0 to 117 of 140 techniques integrated in D3FEND 1.4.0 (MITRE's dashboard script); on D3FEND develop a24ebcc an rdflib proxy count gives 2 of 173 ATLAS classes with an artifact restriction on develop alone and 137 of 173 with the 2026-11 rebaseline snippet applied"
    source: "atlas-d3fend-crosswalk@65cdab0 README.md:19-20"
    date: 2026-11-02
    revalidate: 2027-02-10
---

# Frameworks and what they reach: what each AI framework covers, and where a mapping stops being evidence

Evidence tier: Mixed, with the frameworks, statute and catalogues at A for what they contain, my counts over ATLAS, ATT&CK, D3FEND and NIST data at B (first-party computation over Tier A inputs, some not yet published), two verified lab runs on one host at B for their mechanics and D for the artifact grades, a partial blind re-grade of the first at B for what it measured, and the layer labels and the order of the practices at D.

## Summary for the review

A framework reaches the layer it was built for and stops there, so the useful question about any framework an organization claims is which layer that is: a technique taxonomy, a control catalogue, a management system or a statute. The claim I see break most often is the step from "mapped" to "caught", because MITRE ATLAS carries no detection layer, the ATLAS to D3FEND to SP 800-53 chain computes but runs through a thin 800-53 hop, and in planted lab runs a mapped field became a clean detection on 2 of 8 techniques.

- Record each framework the organization aligns to beside the layer it reaches, using the table below. Effort S. Tier A for each framework's own scope, D for the labels.
- Split ATLAS-tagged coverage into its ATT&CK-referenced and ATLAS-native halves before mapping anything, because about half the steps in ATLAS's real incidents are familiar tradecraft. Effort S. Tier B over Tier A data.
- Stop citing a mapping as detection coverage (`mapping-treated-as-coverage`); for each technique claimed, ask for a field the organization's own sources populate and a planted-event result. Effort M. Tier B.
- Use the ATLAS to D3FEND to 800-53 chain as a map of where to look, report coverage per incident step with the denominator named, and read the 800-53 hop as the weakest link. Effort M. Tier B.
- Re-map any control text keyed to OWASP LLM Top 10 2025 IDs against the 2026 edition (`owasp-ids-2025`). Effort S to M. Tier A for the edition.
- Use NIST AI RMF 1.0 and ISO/IEC 42001 for governance structure rather than technical coverage, and buy no mapping to NIST's AI control overlays until a draft exists. Effort S. Tier A.
- Link to the licence-restricted overlays (SCF, CSA AICM, AIUC-1) and build no derived table from them. Effort S. Tier A for the licence terms.

The 55.5% specific-field figure below stays Tier D, since a second grader's partial run puts it at 57.9% while its adjudication leg never ran.

## Why this matters

Frameworks enter a review through two requests that ask different things. Governance asks "which of our existing controls cover the AI systems", which is fair, because most controls were written before anyone deployed an agent with tool access. Procurement and detection engineering meet products and rule packs described as "mapped to MITRE ATLAS" or "covering the OWASP Top 10", where the reader is meant to infer that something would be caught; [reading-vendor-claims.md](reading-vendor-claims.md) treats that as a claim type, and this document supplies the framework side of it.

The frameworks sit at different layers and get cited as if they were interchangeable, so a claim can be true at one layer and empty at the next. A practitioner who knows ATT&CK will find most of this familiar, and what is new is the ATLAS-native half of the technique set, the missing detection layer, and how thin the bridges from AI frameworks to existing control catalogues still are.

## What each framework reaches

"Reaches" means the layer a claim citing the framework can support without further evidence.

| Framework (pin) | What it is | A claim citing it can support | Where it stops |
|---|---|---|---|
| MITRE ATLAS (v2026.10) | Technique taxonomy, mitigations, case studies | A technique is real; a mitigation is relevant to it | No detection layer; relevance is not interdiction |
| D3FEND (1.6.0) with the ATLAS crosswalk | Defensive ontology keyed to artifacts | A defence acts on the artifact a technique touches | Most ATLAS rows are unmerged proposals |
| SP 800-53 Rev. 5 via D3FEND | Control catalogue | A control is linked to a defence | The linking spreadsheet names a defence on 117 of 1,189 rows |
| CSF 2.0 via NIST IR 8596 (iprd) | Outcome catalogue, draft AI profile | A mitigation sits under a subcategory | 18 of 44 mitigations have no bridge edge |
| OWASP LLM and Agentic Top 10 (2026) | Risk-category lists | A risk category is recognised | No technique IDs, telemetry or test procedure |
| NIST AI RMF 1.0, AI 600-1 | Governance framework and profile | An AI risk process exists with owners | Technical coverage of any attack |
| ISO/IEC 42001:2023 | Certifiable management system | An AI management system is run and audited | Technical coverage of any attack |
| CoSAI secure-ai-tooling (622605a1) | Component, risk and control map | Which components and risks are owned | Detection or telemetry |
| EU AI Act (consolidated 2026-07-27) | Statute | Obligations by role and risk class | Whether any control works |
| SCF, CSA AICM v1.1, AIUC-1 | Licence-restricted control frameworks | What the publisher's documents say | Any table derived from them |

Tier A for what each framework is; the last column is my reading (Tier D) except where a count is cited below.

### MITRE ATLAS: real techniques, and no column for where you would see them

ATLAS v2026.10 carries 221 techniques, 44 mitigations and 77 case studies, 27 typed Incident and 50 Exercise (Tier A, re-derived from the release YAML on 2026-11-10). Its STIX bundle holds 221 attack-pattern objects, 44 course-of-action objects and 1,429 relationships, and no object of type `x-mitre-data-source`, `x-mitre-data-component`, `x-mitre-detection-strategy` or `x-mitre-analytic` (Tier A, counted from the v2026.10 `stix-atlas.json` asset), so nothing in the framework names an observable. ATT&CK introduced data components in v10 (2021-10-21) and detection strategies in v18 (October 2025), which means a team working from ATT&CK has had a structured answer to "where would I see this" for five years while a team working from ATLAS has a mitigation map and nothing on the detection side (Tier A, attack-stix-data bundles).

By ATLAS's own linkage, 48 techniques carry an ATT&CK reference, 23 are sub-techniques of one that does, and 150 (67.9%) have neither, so roughly two thirds of ATLAS is net new to an ATT&CK team (Tier B, my count over the YAML's `attack-reference` field). The incident record is more familiar than that, though, because of the 290 steps in the 27 Incident case studies, 146 (50.3%) use ATLAS-native techniques, against 373 of 469 steps (79.5%) in the Exercises (same derivation). The red-team record makes AI attacks look more novel than the incident record does, and the incident record says about half of a real AI attack is an ordinary intrusion. I read 150 as an upper bound, since AML.T0011 and AML.T0079 share exact names with unlinked ATT&CK techniques (T1204, T1608) and ATT&CK v20 added T1698 and T1699 for prompt injection, which ATLAS v2026.10 does not link (Tier A, both bundles). The other ATLAS property a reviewer needs, eight IDs removed between v2026.06 and v2026.10 with no revoked or deprecated flag, is in [revalidation-and-pins.md](revalidation-and-pins.md), and it is why this document revalidates at three months. So `framework-claimed-atlas` earns credit for a shared vocabulary and a relevance map, and the review should ask where the detection column comes from.

### The chain from ATLAS to D3FEND to SP 800-53 and CSF

The nearest thing to a control column for ATLAS today is a chain built from public data, which I computed against v2026.10. Techniques reach D3FEND through the artifacts they act on, using the public crosswalk (Tier B, atlas-d3fend-crosswalk at 65cdab0); D3FEND defences reach SP 800-53 Rev. 5 through D3FEND's published mapping spreadsheet; and ATLAS mitigations reach CSF 2.0 through the bridge in the initial preliminary draft of NIST IR 8596. A defence counts if it restricts the same artifact class or an ancestor, the rule MITRE's D3FEND API applies.

| Hop | ATLAS v2026.10 techniques reached (of 221) |
|---|---|
| Has an ATLAS mitigation directly (with inherited) | 168 (186) |
| Has a D3FEND artifact row | 183 |
| Reaches a D3FEND defence under MITRE's rule | 176 |
| Reaches an SP 800-53 Rev. 5 control | 141 |
| Reaches a CSF 2.0 subcategory directly (with inherited) | 135 (155) |
| Reaches 800-53 or CSF | 191 |
| Reaches neither | 30 |

Tier B, my computation on 2026-11-09 over ATLAS v2026.10, the crosswalk, D3FEND develop `048c693` (whose 800-53 mapping matches release 1.6.0 exactly) and the IR 8596 iprd bridge; outputs not yet published (see Gaps).

Read quickly, 191 of 221 says about 86% of ATLAS lands on a control many regulated organizations already report against, and I would read it more slowly for three reasons. The first is provenance, since two of the crosswalk's restrictions (AML.T0021 and AML.T0037) are merged upstream and the rest are open pull requests and a rebaseline queue, so D3FEND develop alone gives 2 of 173 ATLAS classes an artifact restriction against 137 of 173 with the rebaseline applied (crosswalk README at 65cdab0, an rdflib proxy count). The second is that the 800-53 hop is weak by construction: D3FEND's spreadsheet was last edited on 2022-09-19, before ATLAS had agent techniques, and names a defence on 117 of 1,189 control rows (180 edges, 111 controls, 41 defences), with 20 further references to the retired `D3-MAC` dropped as unresolvable, and only 17 of the 41 defences are among the 150 the chain reaches (Tier A spreadsheet, Tier B parse). The CSF route is thin too, with 26 of 44 mitigations carrying a bridge edge and all seven added in v2026.10, AML.M0037 to AML.M0043, among the 18 without one (Tier A, the bridge file).

The third is that a chain can be valid at every hop and still say very little. AML.T0051.000, direct prompt injection, injects a DigitalMessage in the crosswalk, D3FEND's defences on that artifact are Message Authentication and Message Encryption, and D3FEND maps those to CM-14 Signed Components, so a widely discussed attack on language models comes out "covered" by a control about signed components (Tier B, my trace through Tier A sources). The 30 techniques that reach no catalogue include the External Harms family, which are outcomes rather than acts on an artifact, attacker-side resource development, and agent-era techniques such as AML.T0117 Autonomous Attack-Path Adaptation, where the act happens inside an agent's planning loop.

### Mapped, relevant and caught are three different claims

Coverage claims tend to blur three statements, and the runs below test each one separately.

A mapping says a control is relevant. Picking ATLAS mitigations greedily over the 290 incident steps reached 19.3% after one control, 50.7% after four and 71.7% after ten, then stopped at a ceiling of 75.5% (219 of 290), with 17 of 44 mitigations ever adding a step; ATT&CK's mitigations reach 142 of the 144 familiar steps, and 31 steps in 18 of the 27 incidents are reached by neither catalogue, 30 of them ATLAS-native (Tier B, my computation over ATLAS v2026.10 and ATT&CK v20.1, independently re-implemented, no pre-registration). A degree-preserving shuffle produced curves at or above the real one in 13.7% to 16.1% of shuffles across three seeds, so a greedy top ten is not distinguishable from what each control's breadth alone would give, and I would not use one as a priority order. An earlier adversarial pass over nine agentic and generative-AI case studies refuted all 17 mitigation-and-case pairs that looked like plausible interdictions (Tier B, on ATLAS v2026.06, an older release and a smaller corpus).

An observable says the schema could hold the fact. Following the crosswalk's artifacts into OCSF 1.9.0, 235 of 290 incident steps (81.0%) reach some field and 161 (55.5%) a specific one, falling to 123 (42.4%) if the broad File and UserAccount artifacts are set aside (sdw-lab-benchmarks@91e44df atlas-ocsf-observables/RESULTS.md:32-36, 58-62; the join is Tier B, the specific-versus-generic grades one author's single pass and Tier D, the sensitivity not pre-registered). A blind second grader moved the specific share to 168 (57.9%) and the any-field share down to 204 (70.3%), with a five-category kappa of 0.452 on 79 artifact rows, and its adjudication leg did not run, so the 55.5% stays Tier D (sdw-lab-benchmarks@91e44df m1-r1-blind-regrade/RESULTS.md:14-28; one model, partial run). The reading I trust most is the split by origin, where ATT&CK-referenced steps reach a specific field 85.2% of the time and ATLAS-native steps 33.9% (atlas-ocsf-observables/RESULTS.md:45-56, supplementary), and 54 of the 55 no-field steps come from the 15 techniques with no crosswalk row (RESULTS.md:85-87), so the dark area is mostly a mapping gap.

A detection says a rule over that field fires on the attack and not on the background. For eight techniques chosen before the run, one Sigma rule each over a planted synthetic background gave 2 DETECTED, 5 NOISY and 1 MISSED across three seeds, and the clean two matched the attack's own content, the injected SQL and the decoded command line, while a mapping table would have scored all eight as covered (atlas-ocsf-observables/RESULTS.md:101-118; I wrote the rules, background and needles, so precision shows the mechanism and is not a field false-positive rate). The prompt-injection rule over `message_context.prompt_text` was MISSED on DuckDB because the compiled `LIKE` is case-sensitive there, and fired noisily on SQLite (RESULTS.md:125-132). The same question asked of controls gave a sharper answer: of the twelve top mitigations in the greedy order four have no artifact a check could key on, and implementing the other eight as their text describes caught 1 of 22 rule-selected incident step-slots cleanly on SQLite, with 7 NOISY, 8 MISSED and 6 MISSED by construction (sdw-lab-benchmarks@91e44df t4-interdiction/RESULTS.md:37-58, 139; authored fixtures, one host). Code Signing there missed the compromised release that its real publisher had validly signed (t4-interdiction/RESULTS.md:97).

So `mapping-treated-as-coverage` selects when a mapping is offered as the third claim while supporting only the first, and the evidence that moves it is a planted-event result per technique on the organization's own sources, the same ask [decision-sequence.md](decision-sequence.md) makes of a vendor chosen on "mapped to MITRE ATLAS".

### OWASP Top 10 for LLM Applications and for Agentic Applications

The OWASP lists are Tier A for the risk categories they name ([evidence-tiers.md](evidence-tiers.md)), which makes them useful for checking that a design review asks about each category, and they carry no technique IDs that join to ATT&CK or ATLAS, no telemetry and no test procedure, so "covers the OWASP Top 10" says which risks a team discussed. The live issue is versioning. OWASP published a 2026 edition of the LLM Top 10 on 2026-08-03 with numbering that differs from 2025, and the Agentic list has a "for 2026" edition dated 2025-12-09 (Tier A, OWASP GenAI Security Project), so control text keyed to 2025 IDs points at the wrong entries, which `owasp-ids-2025` detects. I have not read a published crosswalk between the editions, and the repo writes no explainer of the list itself.

### NIST: AI RMF 1.0, AI 600-1, CSF 2.0 and the Cyber AI Profile

NIST AI RMF 1.0 (NIST AI 100-1, January 2023) organizes AI risk management into Govern, Map, Measure and Manage, and the Generative AI Profile (NIST AI 600-1, July 2024) adds suggested actions for generative systems (Tier A). Both reach governance outcomes, an AI risk process with owners, an inventory and third-party review, which is how [ai-use-policy-and-intake.md](ai-use-policy-and-intake.md) uses the Govern function, and neither names a technique or a log source; NIST says AI RMF 1.0 "is being revised", with no draft as of 2026-11-09. IR 8596 (iprd, 2025-12-16) is the only published bridge from ATLAS mitigations to CSF 2.0 that I have found, with the limits above. The SP 800-53 AI overlay project, renamed on 2026-10-20 to Control Overlays for Super Intelligence Systems (COSIS), has only a concept paper (2025-08-14) and an annotated outline (2026-01-08) (Tier A, CSRC), so I would not buy or build a mapping to it yet.

### ISO/IEC 42001

ISO/IEC 42001:2023 is a certifiable management-system standard for AI, adopted in Europe as EN ISO/IEC 42001:2026, valid from 2026-04-01, which a national body's catalogue lists with ISO/IEC 42001:2023 as its base document (Tier A for the standard, C for the adoption note, read from that catalogue because iso.org returned 403; I have not confirmed the adoption is textually identical). A certificate supports the claim that an AI management system is run and audited within its stated scope, and says nothing about technical coverage, much as an ISO/IEC 27001 certificate says nothing about whether a given detection fires. The review should read the scope statement before crediting a certificate to a surface, as [saas-embedded-ai-and-vendor-terms.md](saas-embedded-ai-and-vendor-terms.md) asks of vendors.

### CoSAI secure-ai-tooling

CoSAI's risk map at `622605a1` describes 42 components of an AI system with the risks and controls attached, under Apache-2.0 (Tier A). It reaches the question of which components and risks an organization is responsible for, which is why [surface-ownability.md](surface-ownability.md) keys every surface to it and adjusts it for rented surfaces, and it carries no detection content, so CoSAI alignment supports a risk-to-control assignment and leaves observability open.

### EU AI Act

The AI Act, consolidated as CELEX 02024R1689-20260727 after amendment by Regulation (EU) 2026/1744, reaches obligations by role and risk class, with dated triggers such as the end of the Article 50 marking grace period on 2026-12-02 and stand-alone Annex III obligations from 2027-12-02 under Article 113 (Tier A, EUR-Lex). Alignment supports a claim that obligations are identified and assigned, and none about whether a control works. This is not legal advice; [prompt-capture-and-the-law.md](prompt-capture-and-the-law.md) carries the logging provisions.

### Licence-restricted frameworks: SCF, CSA AICM and AIUC-1

The Secure Controls Framework is published under CC BY-ND 4.0 and its terms say derivative works need a commercial licence, so a table reshaping SCF rows onto ATLAS techniques would be one (Tier A, the publisher's terms). CSA's AI Controls Matrix v1.1 is free for internal reference with no derivatives, and AIUC-1 reserves all rights (Tier A, the publishers' pages). The repo draws no control content from any of the three and says nothing here about what SCF reaches, which is a declared gap; when `framework-claimed-scf` is selected the review points at the publisher's own mapping documents and asks which SCF controls the organization can tie to a technique and a field. What the frameworks agree on and which controls touch real attack paths are different questions, and I would keep their answers as two linked documents rather than one table.

## What this does not mean

It does not mean ATLAS or the chain is not worth using, since ATLAS is the shared vocabulary for AI attacks and its case studies are a curated public record of what has happened, and the chain is a reasonable map of where to look, especially for the familiar half of an incident. Nor is a NOISY result a failure, because a parent-process allowlist would have made two NOISY rules clean, which is ordinary detection engineering on real data that the run withheld to avoid tuning to its own corpus (atlas-ocsf-observables/RESULTS.md:170-171).

The counts have limits. The incident weights are ATLAS-only, 27 incidents, and should not be quoted as figures for AI incidents in general. The lab runs used synthetic backgrounds on one host with rules and fixtures by the same author, and "has a field" means the schema can hold the fact, not that a product emits it. The T4 checks were written as each mitigation sentence describes, so 1 of 22 measures how far a mitigation's text is from a working check rather than how good any deployed control is.

## Gaps

- **Gap: public home for the chain and burn-down outputs**. The chain counts, the greedy burn-down and the null model are my computations over public data, independently re-implemented but unpublished. **Needs**: the scripts, input hashes and outputs released publicly with a README naming MITRE's artifact rule and the spreadsheet's edit date.
- **Gap: consensus grade for the OCSF specific-field share**. The 55.5% rests on one author's grades and a second grader's partial run. **Needs**: the M1 adjudication leg completed, and a grader from a second provider family.
- **Gap: incident weights beyond ATLAS**. Every step count covers ATLAS's 27 Incident case studies. **Needs**: a published step list for further public incidents and a re-run of the observable join and burn-down over the combined set.
- **Gap: interdiction on the current release**. The 0 of 17 counterfactual ran on ATLAS v2026.06 and nine case studies. **Needs**: the same adversarial pass over v2026.10's mapped pairs.
- **Gap: a second CSF route**. CSF reach depends on an ATLAS mitigation being in the IR 8596 bridge. **Needs**: the 800-53 to CSF 2.0 route through NIST's OLIR mappings computed and compared.
- **Gap: OWASP 2025 to 2026 entry mapping**. The repo flags 2025 IDs but carries no table between editions. **Needs**: an entry-by-entry comparison, or a crosswalk published by the OWASP project.
- **Gap: what SCF reaches for AI**. SCF content is excluded by rule, so its row has no analysis. **Needs**: a reading of the publisher's own AI mapping documents that can be cited without deriving from them.
- **Gap: field population in real products**. The observable join says what OCSF can hold, not what sources emit. **Needs**: the join re-graded against the fields common EDR, cloud and gateway sources populate, per source and version.

## Notes

- 2026-11-10: `surfaces` lists all thirteen because no surface's `enables` list in `routing.yaml` names a frameworks-family key, and framework alignment applies to whichever surfaces an organization runs.
- 2026-11-10: `revalidate-by` is three months out because the document cites ATLAS IDs and counts.
- 2026-11-10: M1 ran as a partial run (grader complete, adjudication refused at a quota floor), so it sits beside the 55.5% without lifting it out of Tier D; whether a partial M1 is enough is a maintainer decision, not taken here.
- 2026-11-10: lab citations point at sdw-lab-benchmarks master at 91e44df; the crosswalk is cited at 65cdab0, its initial public release.
- 2026-11-10: the ATLAS overlap and STIX object counts were re-derived from the v2026.10 YAML and bundle for this document; the chain and burn-down counts were read from their verified outputs.
- 2026-11-10: the "where it stops" column, the layer labels and the order of the practices are my judgement (Tier D).

## Sources

Tier A

- MITRE ATLAS data release v2026.10 (2026-10-28), `ATLAS-2026.10.yaml` and `stix-atlas.json`, https://github.com/mitre-atlas/atlas-data/releases, read 2026-11-10.
- MITRE ATT&CK Enterprise STIX v20.1 (commit `f59b03e`) and earlier bundles, https://github.com/mitre-attack/attack-stix-data.
- MITRE D3FEND ontology, release 1.6.0 (tag `91629ab`) and develop `048c693`, including `extensions/nist/sp800-53r5-control-catalog-d3fend-mapping.xlsx`, https://github.com/d3fend/d3fend-ontology.
- NIST IR 8596, Cyber AI Profile, initial preliminary draft, 2025-12-16, with its ATLAS-to-CSF bridge, https://csrc.nist.gov/pubs/ir/8596/iprd; NIST COSIS project, https://csrc.nist.gov/projects/cosais; both read 2026-11-09.
- NIST SP 800-53 Rev. 5, https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final.
- NIST AI RMF 1.0, NIST AI 100-1, https://doi.org/10.6028/NIST.AI.100-1, and resource page https://www.nist.gov/itl/ai-risk-management-framework (read 2026-11-09); NIST AI 600-1, https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf.
- OWASP Top 10 for LLM Applications 2026, https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/, and for Agentic Applications for 2026, https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/, read 2026-11-09 and 2026-11-10.
- ISO/IEC 42001:2023, https://www.iso.org/standard/42001 (403; EN adoption at https://www.evs.ee/en/evs-en-iso-iec-42001-2026, Tier C).
- CoSAI secure-ai-tooling at `622605a1`, https://github.com/cosai-oasis/secure-ai-tooling.
- Regulation (EU) 2024/1689, consolidated CELEX 02024R1689-20260727, https://eur-lex.europa.eu/eli/reg/2024/1689/oj.
- OCSF schema 1.9.0, https://schema.ocsf.io/.
- Licence facts only: Secure Controls Framework terms, https://securecontrolsframework.com/terms-and-conditions; CSA AI Controls Matrix v1.1, https://cloudsecurityalliance.org/artifacts/ai-controls-matrix-v1-1, with the licence terms from CSA's CCM and AICM Licensing FAQ (PDF dated 2026-03-13), which says the free versions are "for internal reference only" and may not be altered or used for derivatives without a licence; AIUC-1, https://standard.aiuc-1.com/changelog/; read 2026-11-09.

Tier B, first-party lab work and datasets

- sdw-lab-benchmarks at 91e44df, `atlas-ocsf-observables/` (R1), `m1-r1-blind-regrade/` (M1) and `t4-interdiction/` (T4), each with RESULTS.md and VERIFICATION.md, https://github.com/flying-coyote/sdw-lab-benchmarks; R1 and T4 on one host over synthetic backgrounds, M1 a blind re-grade by one model (Gemini 3.8 Flash, three passes), pre-registrations frozen by the agent and not reviewed by the maintainer, all VERIFIED-WITH-FIXES, M1 partial.
- atlas-d3fend-crosswalk at 65cdab0, README, crosswalk CSVs and `VERSION-DIFF-2026-11.md`, https://github.com/flying-coyote/atlas-d3fend-crosswalk (MIT); upstream coordination at https://github.com/d3fend/d3fend-ontology/issues/606.
- My chain, overlap and burn-down computations over the Tier A sources above, run 2026-11-09 and independently re-implemented; outputs not yet published.
