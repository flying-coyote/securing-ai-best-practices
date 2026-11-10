---
evidence-tier: Mixed
convergence: single-source
applies-to-signals: [surface-S1, surface-S2, surface-S3, surface-S4, surface-S5, surface-S6, surface-S7, surface-S8, surface-S9, surface-S10, surface-S11, surface-S12, surface-S13]
surfaces: [S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12, S13]
pins:
  - "CoSAI secure-ai-tooling risk-map @ 622605a13fafaa2784acbdbe3f8d23ee22da4be7 (main, 2026-10-21)"
  - "MITRE ATLAS v2026.10 (released 2026-10-28)"
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-02-10
status: EMERGING
---

# Surface ownability: thirteen surfaces on the CoSAI component map

Evidence tier: Mixed, A for the CoSAI YAML counts and the ATLAS step counts, D for every O/V/S cell, every band assignment and the case-study-to-surface assignment, all of which are one author's reading and have not had a second reader.

## Summary for the review

The CoSAI component map describes an AI system its operator owns end to end, and most of the thirteen ways AI gets deployed in an organization are systems the organization rents, so on most surfaces the parts it can configure and instrument are its identity provider, its network enforcement point and whatever audit record the vendor exports. The surfaces fall into three bands, which tell the review where effort can land.

- Own all: S9 self-hosted serving, S11 fine-tuning pipelines, S12 RAG and vector stores (a rented embedding model and a public model registry are the usual exceptions).
- Own the agent, tool and orchestration components, with the model reached through another surface: S4 coding agents, S5 MCP servers and agent tools, S6 low-code builders.
- Own little beyond identity, the enforcement point and the exported record: S1, S2, S3, S7, S8, S10, S13, with S3 and S10 as edge cases (S3 owns nothing on the map, and on S10 the components sit on company laptops but no team holds them).

Actions:

1. Band every surface the organization runs before ranking anything, and print the band beside each surface. Effort S. Tier D (the bands are one author's grid).
2. Start a collection plan from the identity provider, the egress or gateway enforcement point and the audit record, on the surfaces where each exists (the identity provider appears on 11 of 13 surfaces, an audit record repository on 8, a network enforcement point on 4 in the long view), and say plainly which surfaces have none of the three. Effort S to M. Tier D for the plan; Tier A for the component definitions.
3. On band-three surfaces, treat the vendor's exported audit or compliance log as the only record and confirm it is switched on and exported, using the platform's own documentation for what it records. Effort M. Tier B for what each export carries (see the telemetry and platform docs).
4. On band-one surfaces, expect to carry patching, logging, identity and detection for every component, and size the work accordingly. Effort L. Tier D.

## Why this matters

A review that asks "what are your AI risks?" before it asks "which parts of this system are yours?" ends up recommending controls on components the organization cannot touch, such as the vendor's model or the vendor's retrieval index. The CoSAI map is the finest-grained public map of an AI system's parts I have found, with stable IDs and a machine-readable join to risks and controls, so it is a sensible place to anchor that ownership question. But the map's personas are ecosystem roles (model provider, platform provider, application developer, end user) rather than functions inside a buying organization, which means somebody has to read each deployment surface against the component descriptions and say who actually holds each part. This document is that reading, and it is the reason every other routed document can talk about "the components you own on this surface" without re-deriving it.

## The map this reads against

Three versions of the map are in circulation and they disagree on how many parts an AI system has, which matters because a reader who meets the first one will think the other two describe a different framework.

| Version | Parts | Agent treatment | Versioned |
|---|---|---|---|
| Google SAIF components page | 12 components under Data, Infrastructure, Model, Application | one "Agent" box defined as tool use | no date or version on the page (Tier B, fetched 2026-11-09) |
| Google SAIF "Focus on Agents" | four stages (Application and Perception, Reasoning core, Orchestration, Response rendering) | six named sub-parts under two stages (system instructions, user queries, memory, tools, RAG content, optional auxiliary models) | no date or version (Tier B, fetched 2026-11-09) |
| CoSAI `risk-map/yaml/components.yaml` | 42 components, 4 categories, 11 subcategories | about twenty components across Application, Model, External Tools and Infrastructure | git commit `622605a1` (Tier A for the file's contents) |

I use the CoSAI IDs throughout, because they are the only version under version control and the only one with a risk and control join. Counted from the YAML at `622605a1` and re-counted on 2026-11-10 (Tier A):

| Category | Subcategory | n |
|---|---|---|
| Infrastructure | Data | 4 |
| Infrastructure | Deployment (ModelStorage, IsolationRuntime, ToolHosting, RuntimeHosting, AuditRecordRepository) | 5 |
| Infrastructure | Registries (ModelRegistry, ToolRegistry) | 2 |
| Infrastructure | Identity (IdentityProvider, AuthorizationPolicyDecisionPoint, FederationProxy) | 3 |
| Model | Training | 3 |
| Model | Core (ModelServing, TheModel) | 2 |
| Model | Orchestration (input and output handling, Memory, RAGContent) | 4 |
| Application | Application core (including a consent surface and a network policy enforcement point) | 5 |
| Application | Agent (ReasoningCore, user query, system instruction, input and output handling, consent surface, tool transport, network enforcement point) | 8 |
| External Tools | Tool invocation path (Tools, ToolServer, AuthorizationPolicyEnforcementPoint, tool input and output handling) | 5 |
| External Tools | Tool network controls | 1 |

The same commit carries 36 risks, of which 19 have a `mappings.mitre-atlas` list resolving to 24 distinct ATLAS technique IDs, and ten personas, two of them deprecated (Model Creator, Model Consumer) (Tier A). Google's single "Tools" sub-part became CoSAI's whole External Tools category plus the ToolRegistry, and the identity, enforcement and audit components that most of this document leans on (IdentityProvider, the policy decision and enforcement points, FederationProxy, the three network enforcement points, AuditRecordRepository) do not appear on either Google page at all.

## The grid

Codes: O, the organization instantiates and operates this component class on this surface; V, the component exists but a vendor operates it and the organization sees only what the vendor exports; S, shared, where the organization configures or feeds it and the vendor runs it (organization documents indexed into a vendor's retrieval store, or organization-authored system instructions executed by a vendor harness); a dash, absent or not meaningfully separable on this surface.

One-grader note: every cell below is my reading of a surface against the CoSAI component descriptions at `622605a1`, made once, by one person, and not yet checked by a second reader (Tier D). Treat a cell as a starting position to confirm with the team that runs the surface, and expect some cells to move when the second reader lands; the band column in the next table is the part the review relies on, and it is less sensitive to any single cell than the grid is.

| Surface | Data (4) | Model training (3) | Model core (2) | Orchestration (4) | Registries (2) | Deployment (5) | Identity (3) | App core (5) | Agent (8) | Tool invocation path (5) | Tool network (1) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 AI features in SaaS apps | – | – | V | V | – | V | S (IdP), V | V | V | V | – |
| S2 Enterprise assistants | S (DataSources, DataStorage via connectors) | – | V | S (RAGContent, Memory), V | – | V (AuditRecordRepository exported) | O (IdP, PDP), S (FederationProxy) | V, S (ConsentSurface) | V, S (SystemInstruction for custom agents) | S (Tools via connectors), V | V |
| S3 Browser AI | – | – | V | V | – | – | – (uses the user's own sessions) | S (the page as Application) | V (ReasoningCore), S (I/O in the page) | S (page and DOM as tools) | – |
| S4 IDE and coding agents | – | – | V, O when S10 backs it | O (harness I/O), S (Memory) | O (ToolRegistry = MCP client config) | O (RuntimeHosting = laptop; IsolationRuntime usually absent) | S (IdP), O (developer credentials) | O (IDE or CLI) | O (all 8; SystemInstruction = rules files) | O/S (local stdio servers; remote vendor servers) | O (egress) |
| S5 MCP servers and agent tools | – | – | – | – | O (ToolRegistry) | O (ToolHosting, IsolationRuntime, AuditRecordRepository) | O (PDP, FederationProxy, IdP) | – | O (ToolTransport, network enforcement point) | O (all 5) | O |
| S6 Low-code agent and workflow builders | S (DataSources) | – | V (model via API) | O (all 4) | O (ToolRegistry = node catalogue) | O (RuntimeHosting, AuditRecordRepository) | O (builder credential store), V | O | O (loop, SystemInstruction, I/O) | O (Tools, ToolServer) | O |
| S7 Managed AI build platforms | O (DataSources, DataStorage for tuning) | S (managed tuning and evaluation jobs) | V (ModelServing), S (TheModel if tuned) | S | V (model catalogue), S (ToolRegistry) | V (RuntimeHosting), O (AuditRecordRepository = cloud audit log) | O (cloud IAM as IdP and PDP) | O/S (Application, gateway as enforcement point) | S | S | S |
| S8 Direct model API and AI gateways | – | – | V | – (app-side) | – | O (AuditRecordRepository = gateway log) | O (API keys and IdP) | O (Application, gateway as enforcement point) | – | – | – |
| S9 Self-hosted model serving | – | – | O (ModelServing, TheModel) | – | O (ModelRegistry if run) | O (ModelStorage, RuntimeHosting, IsolationRuntime, AuditRecordRepository) | O | O | – | – | – |
| S10 Local on-device open-weight models | – | – | O (localhost daemon; TheModel) | – | V (public model hub) | O (local model store; laptop) | – | O | – | – | – |
| S11 Fine-tuned models and pipelines | O (all 4) | O (all 3) | O (TheModel), O/V (ModelServing) | – | O/V (ModelRegistry) | O (ModelStorage, RuntimeHosting) | O | – | – | – | – |
| S12 RAG pipelines and vector stores | O (DataSources, processing, DataStorage) | – | V/O (embedding model) | O (RAGContent, input handling, Memory) | – | O (RuntimeHosting, AuditRecordRepository) | O | O | – | – | – |
| S13 AI inside security tools | S (telemetry as DataSources) | V | V (vendor classifiers, ModelServing) | V, S (RAGContent = your telemetry) | – | V | S (IdP for the SOC tool) | V | V (ReasoningCore in agentic SOC products), S (SystemInstruction = playbooks) | S (Tools = your SIEM, EDR and SOAR APIs) | – |

## Three bands, per surface

The review prints this table rather than the grid, because the bands survive a disputed cell better than the cells do. The step columns count ATLAS v2026.10 Incident case-study steps on each surface after I assigned each case study to the surface it attacked (Tier D for the assignment, Tier A for the underlying steps); "on map" means the step's technique, or its parent, appears in some CoSAI risk's ATLAS mapping. ATLAS write-ups vary a lot in how finely they are broken into steps, so read the counts as presence on a surface, not as weight.

| Surface | Band | What the organization holds on the map | What it can instrument | CoSAI persona it plays | Incident steps (on map) |
|---|---|---|---|---|---|
| S1 SaaS AI features | 3 | a share of the IdP (SSO into the SaaS) | SSO log, vendor audit export | End User | 24 (5) |
| S2 Enterprise assistants | 3 | IdP and policy decision point; shares retrieval content, memory settings, connectors, custom-agent instructions, OAuth consent | IdP and conditional access, vendor audit or compliance log, connector grants | End User; Application Developer for what it builds; Data Provider for connector content | 6 (0) |
| S3 Browser AI | 3, edge | nothing on the map; the agent inherits the user's sessions | browser management telemetry, egress proxy | End User | 0 |
| S4 Coding agents | 2 | all eight agent components, MCP client config, harness I/O, the laptop | endpoint, egress, the harness's own logs and hooks | Application Developer | 7 (3) |
| S5 MCP servers and tools | 2 | the whole External Tools category, ToolRegistry, hosting, isolation, identity, audit | everything it runs, including the tool server's own audit record | Agentic Provider when publishing; Application Developer when consuming | 9 (1) |
| S6 Low-code builders | 2 | all four orchestration components, the loop and its instructions, tools, hosting, the builder's credential store, audit | the builder's own log, its host, egress | Application Developer | 18 (2) |
| S7 Managed build platforms | 3 | cloud IAM, the cloud audit log, its own data stores, the gateway where configured; shares tuning, agents and tool registry | cloud audit log, IAM, gateway | Application Developer and Data Provider | 9 (1) |
| S8 Direct API and gateways | 3 | the application, the gateway, the keys or workload identity, the gateway log | gateway log, vendor usage export, key inventory | Application Developer | 43 (16) |
| S9 Self-hosted serving | 1 | every component, including the model and its storage | all of it, and all of it is the organization's job | Model Serving | 7 (4) |
| S10 On-device models | 3, edge | the components are on company hardware, held by end users; no identity plane; public registry | endpoint software inventory, egress for model downloads | End User | 6 (1) |
| S11 Fine-tuning pipelines | 1 | all data and training components, the model, storage, identity (the registry may be rented) | all of it | Model Provider and Data Provider | 3 (2) |
| S12 RAG and vector stores | 1 | ingest, processing, the vector store, retrieval, memory, identity, audit (the embedding model is often rented) | all of it | Application Developer and Data Provider | 4 (0) |
| S13 AI in security tools | 3 | shares its telemetry as the vendor's data, its playbooks as instructions, its SIEM and EDR APIs as tools | the tool's own audit log, the API credentials it holds | End User; Application Developer for playbooks; Data Provider for its telemetry | 16 (9) |

The totals reconcile to the public step record: 27 Incident case studies and 290 steps, of which 78 reach a CoSAI risk, 99 are ATT&CK-referenced and off the map, 102 are ATLAS-native and off the map, and 11 are harm outcomes (Tier A data, author's count). Six of the 27 case studies, 137 steps, are AI held by the attacker with no deployment surface on the defender's side, and one more (a vendor API used as command-and-control against a third party) sits on S8's technology without the organization being the victim; both are outside this document because the map is a map of the defender's own system.

Two things in that table seem worth saying out loud. The band-one surfaces, where the organization owns the most and where the map's original model-centric risks were written, are the quietest in the incident record (14 steps across three surfaces), while the busiest defender surfaces (S8, S1, S6, S13) are band three or band two, so a review weighted by component count would put effort where the incidents are not. And on the agent-identity side, the three CoSAI risks that look best evidenced by incidents (Cross-Tenant Credential Propagation, 29 step hits; Shadow and Unknown Agents, 15; Stale Agent Identity Binding, 15) are reached only by Valid Accounts (all three) and Unsecured Credentials (the first only), which is credential tradecraft against AI services, and that lands on the identity provider, the one component the organization holds on most rented surfaces.

## The three components that recur

The practical consequence for a collection plan is to start from the components that keep appearing across surfaces and that the organization can configure where they appear. In the per-component long view behind the grid (130 rows across the thirteen surfaces, Tier D):

- IdentityProvider appears on 11 of 13 surfaces, owned outright on eight (S2, S5, S6, S7, S8, S9, S11, S12) and shared on three (S1, S4, S13); it is absent on S3, where the browser agent rides the user's existing sessions, and on S10, where there is no identity plane at all.
- AuditRecordRepository appears on eight surfaces, owned on six (S5, S6, S7, S8, S9, S12) and vendor-run with an export on two (S1, S2); on the rest, the record is whatever the vendor or the endpoint emits.
- A network policy enforcement point appears as a CoSAI component on four surfaces (S4's agent egress, S5's tool network, the gateway on S7 and on S8), and the organization's own egress proxy is the nearest equivalent on S1, S2, S3 and S10, even though it is not a component of the vendor's system.

So "start from identity, egress and the exported record" is a sound default, but it is a default with named holes, and the review should print which of the organization's surfaces fall into them rather than imply the three are present everywhere.

## What this does not mean

Band three does not mean nothing can be done. On S2 and S7 the organization still holds configuration that matters a great deal (connector scopes, retention, custom-agent instructions, cloud IAM), and the shared cells exist precisely to show that; the band describes what the organization operates, not what it can influence through settings and contract.

Band one does not mean the risk is highest there. It means the work is all the organization's, which is a statement about effort and accountability. The incident record above points the other way on frequency, though I would not read too much into that either, since 27 case studies is a small and unevenly documented sample.

S5 and S6 are all-O in the long view (13 of 13 rows each) and still sit in band two, which is a choice. S5 has no model components at all and S6 rents its model through an API, so on both the model half is reached through another surface (usually S8), and I think banding them with S4 is more useful to a reviewer than calling them fully owned. A reader who prefers to call them band one loses little, as long as the S8 surface behind them is also reviewed.

The CoSAI risk-to-component join through `controls.yaml` is too loose to replace the grid, because four assurance controls carry `risks: all` and `components: all` and four governance controls carry `components: none`, so a naive join has every risk reaching every component (Tier A for the file's contents). That is why the grid comes from reading each component description against each surface, since the computed join would say nothing.

CoSAI also maps generic Software supply chain (T0010.001) to MCP-server risks and Valid Accounts (T0012) to three agent-identity risks, so a dependency compromise on S11 or a tampered IDE extension on S4 "reaches" MCP risks in the join. Both mappings are defensible as direct-instance readings, and both inflate the agentic risks' apparent incident evidence; the counts above keep them as the join produces them.

## Gaps

- **Gap: second reader over the grid**. Every O/V/S cell and every band is one author's reading, and no second person has graded the 13 by 11 grid. **Needs**: an independent second grader working from the same CoSAI commit, with the cells that change recorded and the one-grader note removed once agreement is measured.
- **Gap: case-study-to-surface assignment**. Assigning each ATLAS Incident to one surface is one author's judgement, and three cases could reasonably sit elsewhere (CS0006 as S11 rather than S12, CS0047 as S5 as much as S4, CS0042 as attacker-side), though none of those moves changes the totals. **Needs**: the same second reader, or a surface tag carried by ATLAS case studies themselves.
- **Gap: re-runnable step counts**. The per-surface step counts come from joining ATLAS v2026.10 case-study steps to CoSAI's ATLAS mappings, and that join and its step table are not yet published as a re-runnable artefact. **Needs**: the join script and step table published in sdw-lab-benchmarks with a commit hash, so the counts move from author's count to a pinned measurement claim.
- **Gap: per-component long view not published**. The counts for the recurring components (11, 8 and 4 surfaces) come from a 130-row surface-by-component table behind the grid that is not yet in this repo, so a reader cannot check them row by row. **Needs**: that table published as a data file beside this document, with the same one-grader note.
- **Gap: S3 browser AI**. No ATLAS v2026.10 Incident is a browser-agent incident and the organization owns no component on the map for this surface, so its row rests on technique classes alone. **Needs**: an ATLAS Incident case study on a browser agent, or a CoSAI component for the user-session-as-tool shape.
- **Gap: auxiliary models**. Google's "Focus on Agents" names optional auxiliary models such as safety classifiers, and CoSAI has no component for them at `622605a1`, so the grid cannot place a gateway's guard model. **Needs**: a CoSAI component or modelling note for side models, or an explicit ruling that they are a second instance of ModelServing.

## Notes

- Banding (2026-11-10, Tier D). S5 and S6 placed in band two despite all-O rows, for the reason given above. S10 placed in band three although its rows are O, because the components are held by end users and there is no identity plane, so in practice no team can instrument them.
- Wording of the recurring components (2026-11-10). I do not say the three are "owned on every surface", because the long view shows the identity provider absent on two surfaces, the audit record absent on five, and a network enforcement point present as a component on four. The defensible claim is the narrower one in the section above.
- Revalidation is three months because the incident columns depend on ATLAS, and a new ATLAS release or a change to CoSAI's `components.yaml` (the registry was still changing at the time of reading) reopens this document. The step-count method is parent-or-self technique match against each risk's `mappings.mitre-atlas`; two of CoSAI's 24 mapped IDs (T0019 and T0024.002) are retired in v2026.10 and were carried to their successors before counting.
- The telemetry, identity and inventory measurements that go with each surface (OCSF field coverage, SBOM tool visibility, manifest drift, retention cost) live in the documents those questions route to, cited by lab run there, not here.

## Sources

Tier A:

- CoSAI, `cosai-oasis/secure-ai-tooling`, `risk-map/yaml/components.yaml`, `risks.yaml`, `controls.yaml`, `personas.yaml`, `risk-map/README.md` and `docs/guide-components.md`, commit `622605a13fafaa2784acbdbe3f8d23ee22da4be7` (main, 2026-10-21), Apache-2.0. https://github.com/cosai-oasis/secure-ai-tooling/tree/622605a13fafaa2784acbdbe3f8d23ee22da4be7/risk-map. Counts re-derived 2026-11-10.
- MITRE ATLAS v2026.10 (released 2026-10-28), case studies and techniques. https://github.com/mitre-atlas/atlas-data. Incident step classes counted 2026-11-10.

Tier B:

- Google, Secure AI Framework components page. https://saif.google/secure-ai-framework/components, fetched 2026-11-09, no version on the page.
- Google, Focus on Agents. https://saif.google/focus-on-agents, fetched 2026-11-09, no version on the page.

Tier D:

- The O/V/S grid, the bands, the owner and instrumentation columns, and the case-study-to-surface assignment: the author's reading, 2026-11-09, checked against the primaries above on 2026-11-10.
