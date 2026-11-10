---
evidence-tier: Mixed
convergence: single-source
applies-to-signals: [schema-none, schema-vendor-json, schema-otel, schema-ocsf, mcp-spec-pre-2026-07]
surfaces: [S2, S4, S5, S7, S8]
pins:
  - "OCSF 1.9.0"
  - "OCSF main 1.10.0-dev at commit d1cbd61 for ai_capability and ai_status (not in a release; the repo pin is OCSF 1.9.0)"
  - "OCSF pull request 1754 AI Agent Activity draft at commit 08d6f53 (open, draft)"
  - "MCP specification 2026-07-28"
  - "MCP Python SDK (mcp) 1.30.0 and 2.3.0 (lab runs R2 and T8a)"
  - "OpenTelemetry GenAI and MCP semantic conventions at registry commit e6658f1 with semconv v1.45.0 (lab run R2)"
  - "OWASP Agent Observability Standard OCSF mapping at commit 9a9bc37 (lab run R2)"
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-03-10
status: EMERGING
measurement-claims:
  - claim: "Recording one MCP tools/call as 33 facts, OCSF main with the ai_operation profile on API Activity typed 24, the OCSF #1754 draft class 22, OpenTelemetry GenAI plus MCP 19, and OWASP AOS on OCSF 11 (8 under the page's other example), with AOS putting 22 facts in unmapped; stdio only, agent and model identity supplied by the harness"
    source: "sdw-lab-benchmarks@91e44df agent-toolcall-schemas/RESULTS.md:49-61"
    date: 2026-11-09
    revalidate: 2027-03-10
  - claim: "All 10 AOS records passed the public OCSF 1.9.0 validator with zero errors while all 10 OCSF-main records failed on ai_capability and the 1.10.0-dev version string"
    source: "sdw-lab-benchmarks@91e44df agent-toolcall-schemas/RESULTS.md:87-91"
    date: 2026-11-09
    revalidate: 2027-03-10
  - claim: "At 1M synthetic calls in DuckDB 1.5.3, the AOS unmapped-JSON layout ran four pre-registered hunts 4.7x to 22.5x slower than typed OCSF columns and a single OpenTelemetry attributes map ran 10.6x to 32.4x slower, with identical answers; host under contention, within-pass ratios only, Q3 and Q4 ranged roughly 5x to 16x between the formal run and a lower-load rerun"
    source: "sdw-lab-benchmarks@91e44df agent-toolcall-schemas/RESULTS.md:116-130, :156-171"
    date: 2026-11-09
    revalidate: 2027-03-10
  - claim: "At 1M calls the typed layout was 27.4 MB and the unmapped-JSON layout 30.9 MB (1.13x), so the cost of the unmapped shape fell on query time rather than storage"
    source: "sdw-lab-benchmarks@91e44df agent-toolcall-schemas/RESULTS.md:124, :146-148"
    date: 2026-11-09
    revalidate: 2027-03-10
  - claim: "On mcp 2.3.0, moving from revision 2025-11-25 to 2026-07-28 removed Mcp-Session-Id, added Mcp-Method on 11 of 11 POSTs and Mcp-Name on 6 of 6 tools/call, stamped protocol version and clientInfo on 11 of 11 requests and serverInfo on 10 of 10 results, and silenced in-protocol log notifications by default; on revision 2025-11-25, moving from mcp 1.30.0 to 2.3.0 moved a raising tool's failure cause from the client-visible text to server stderr and added OpenTelemetry spans that export nothing without a tracer provider"
    source: "sdw-lab-benchmarks@91e44df t8a-mcp-before-after/RESULTS.md:49-69, :134-135"
    date: 2026-11-10
    revalidate: 2027-03-10
  - claim: "Grading 25 rows between the D3FEND AI artifact nouns and the OCSF ai_* objects found 0 exact matches in either direction (D3FEND to OCSF 0/9/2/3, OCSF to D3FEND 0/4/3/4 as exact, partial, wrong-kind, none), and no OCSF object for agent memory"
    source: "sdw-lab-benchmarks@91e44df d3fend-ocsf-ai-alignment/RESULTS.md:9-14, :42-46"
    date: 2026-11-09
    revalidate: 2027-03-10
  - claim: "On 141 vendor fields mapped to OCSF 1.8.0, a schema-constrained alias mapper had a 0.00 invented-path rate by construction at 0.16 path-correctness and 0.67 coverage, while three blind frontier-model runs had 17.0 to 26.7 percent invented paths (subset-sensitive) at 57.6 to 68.5 percent path-correctness"
    source: "sdw-lab-benchmarks@91e44df ocsf-deterministic-mapper/README.md:11-16; ocsf-mapping-oracle/_frontier/REPLICATION-2026-06-14.md:40-54"
    date: 2026-06-14
    revalidate: 2027-03-10
---

# Landing AI events in OCSF: which class, which profile, and what the tool call costs if it lands in unmapped

Evidence tier: Mixed, with the OCSF schema and the MCP specification at A, three November lab runs on one host at B (each verified by a second agent, verdict VERIFIED-WITH-FIXES, pre-registrations frozen by the agent and not reviewed by the maintainer) and two June mapping runs at B, OpenTelemetry and OWASP AOS documentation at B for what each defines, and the path choices marked as judgement at D.

## Summary for the review

OCSF already has most of the AI vocabulary a security team needs to record an agent's tool call (the `ai_operation` profile and the `ai_agent`, `ai_model`, `delegation` and `message_context` objects in 1.9.0, with the `ai_capability` and `ai_status` objects on main), but it has no AI event class yet, so the record rides on an existing class, and where its hunt keys land decides whether anyone can query it. In one lab run the shape that passed the 1.9.0 validator with zero errors was the one that put 22 of 33 facts in `unmapped` and ran hunts roughly 5x to 22x slower.

- Land agent tool calls and model calls on API Activity (6003) with the `ai_operation` profile, and stop waiting for an AI class. Effort M. Tier A for the schema, B for the lab.
- Promote the hunt keys (tool name, agent, principal, server, decision) to typed columns at ingest and keep the raw message beside them. Effort M. Tier B.
- If the record is the vendor's own JSON, map it with a mapper that can only emit paths that exist in the pinned OCSF version, and review the wrong-but-valid mappings a validator cannot see. Effort M. Tier B.
- If the record is OpenTelemetry, land attributes as columns rather than one map, and expect the attribute names to move, since every GenAI and MCP attribute used was at Development stability. Effort M. Tier B for stability, D for the column landing.
- If nothing is emitted yet, start with the MCP request headers at a gateway (Streamable HTTP on revision 2026-07-28) and the client's own telemetry, which give the tool name without parsing a body. Effort M. Tier A for the headers, B for the lab.
- Record the negotiated MCP revision and SDK version per client and server, and ship server stderr or spans, because the failure cause moved there. Effort S. Tier B.
- Stamp `metadata.version` on every record and decide once whether to write main-branch `ai_capability` now or hold it in `unmapped`, so a later re-map is a query rather than a re-parse of the raw store. Effort S. Tier D.

## Why this matters

The review asks what format the AI audit record is emitted in, and each of its four answers (none, vendor JSON, OpenTelemetry, OCSF) leaves the pipeline owing a different amount of normalization before one query can run across agents, gateways and the rest of the SOC's data. The other routed documents say what to collect and where the record lands ([telemetry-by-surface.md](telemetry-by-surface.md), [what-to-log-and-what-it-costs.md](what-to-log-and-what-it-costs.md)); this one owns the step after that, which is the schema and the paths, and it owns the MCP protocol revision question jointly with [mcp-servers-and-manifest-drift.md](mcp-servers-and-manifest-drift.md) because the revision changed which facts reach a record at all.

The landing deserves its own document because the obvious success test, a record that validates, turned out to be a poor proxy for what a SOC wants. Three communities have published shapes for an agent's tool call that disagree with one another, and I think a team that picks one by which validator it satisfies will find out at hunt time that the agent and the tool it called sit inside a JSON document every query has to parse, a cost that shows neither in a procurement comparison nor on the storage bill.

## What OCSF has today, by release

The OCSF AI work moved in three steps over about eight months, and a fair amount of what I read about it was one step behind, so the versions matter (Tier A, OCSF `CHANGELOG.md`, read 2026-11-10).

| Object or profile | First in | What it carries | Note |
|---|---|---|---|
| `ai_operation` profile | 1.8.0 (March 2026, #1488) | Attaches AI context to an event | In 1.9.0 applied to the System, Network, Application and IAM base classes; 44 of the 87 classes in 1.9.0 carry it |
| `ai_model` | 1.8.0 (#1488) | `ai_provider`, `name`, `version`, `uid` | An identity descriptor, with no digest of the weights |
| `message_context` | 1.8.0 (#1488); `prompt_text`, `response_text` in 1.9.0 (#1674) | Role (`ai_role_id`, where 3 is Tool and 6 is Retriever), application, service, token counts, prompt and response text | Prompt capture is governed by [prompt-capture-and-the-law.md](prompt-capture-and-the-law.md) |
| `ai_agent` | 1.9.0 (2026-08-03, #1641) | `name`, `version`, `uid`, `instance_uid`, `type_id` (framework), `charter`, nested `ai_model` | Distinct from OCSF `agent`, which is a security sensor |
| `delegation` | 1.9.0 (#1665) | `uid`, `issuer_uid`, `parent_uid`, `created_time`; `scopes`, `audience`, `expiration_time` on main only | Owned by [agent-identity-and-delegation.md](agent-identity-and-delegation.md) |
| `ai_capability` | main, 1.10.0-dev (#1729, merged 2026-10-07) | The invoked capability (`source_id` MCP, Function or Built-in): `name`, `type_id` (Tool, Resource, Prompt Template), `transport_id` (stdio, Streamable HTTP, HTTP+SSE), the four tool annotations, `transaction_uid`, and fingerprints of the description and schemas | Not in a release; a 1.9.0 validator rejects it |
| `ai_status` | main (#1704, merged 2026-10-13) | `stop_reason_id`, `permission_result_id` | Not in a release |

The 1.9.0 rows were read from schema.ocsf.io and the main rows from `ocsf/ocsf-schema` at `d1cbd61`, still the head of main on 2026-11-10. There is no AI category on main either; that argument is happening in draft pull request #1754, an AI Agent Activity class, still open and marked draft, with seven of its nine info objects empty stubs at the commit the lab pinned (Tier B, `d3fend-ocsf-ai-alignment/RESULTS.md:65`). So for now an agent event rides on an existing class with the profile attached, and API Activity is the natural carrier for a tool call, since the call is an API operation against a server and the class already has an `api` object with `operation`, `version`, `service`, `request` and `response`.

## The paths, for a tool call and for the decision before it

Two occurrences need recording, the tool call and the hook or gateway decision before it ([coding-agent-hooks-and-policy.md](coding-agent-hooks-and-policy.md) covers the enforcement side), and I would keep them as two events rather than one event with a status, because a harness can allow a call that then never runs, and that absence is worth hunting for. Both land on API Activity 6003, which in 1.9.0 accepts the AI Operation, Security Control and Trace profiles among others (Tier A, schema.ocsf.io 1.9.0).

| Fact | OCSF 1.9.0 path | OCSF main path | Source of the choice |
|---|---|---|---|
| Tool name | `api.operation` | `ai_capability.name` | R2 mapping; 1.9.0 choice is my judgement (D) |
| MCP method (`tools/call`) | `unmapped` or `api.operation` if the tool name goes elsewhere | `api.operation` | R2 |
| MCP protocol revision | `api.version` | `api.version` | R2 judgement call (D) |
| MCP server name and version | `api.service.name`, `api.service.version` | `ai_capability.service` | R2 |
| Request id | `api.request.uid` | `ai_capability.transaction_uid` | R2 for main; 1.9.0 is my judgement (D) |
| Arguments and result | `api.request.data`, `api.response.data` (JSON blobs), plus `raw_data_hash` | same | R2; no schema types individual argument values |
| Failure | `status_id` 2 Failure, `api.response.error_message` | same | R2 |
| Agent | `ai_agent.name`, `.version`, `.instance_uid` (the session), `ai_agent.ai_model` | same | OCSF profile text |
| Human principal | `actor.user` | same | Actor has no `ai_agent` attribute; the agent goes in the profile |
| Delegated authority | `delegation` | `delegation` plus `scopes`, `audience` | [agent-identity-and-delegation.md](agent-identity-and-delegation.md) |
| Trace context from `_meta.traceparent` | `trace.uid`, `trace.span.uid`, `trace.span.parent_uid` (Trace profile) | same | My judgement (D); T8a used `metadata.correlation_uid` |
| Transport, annotations, description fingerprint | `unmapped` | `ai_capability.transport_id`, `is_readonly`, `is_destructive`, `is_idempotent`, `is_open_world`, `desc_fingerprint` | R2 |

The decision record adds the Security Control profile, which is what turns a hook's verdict into typed columns. `action_id` carries 1 Allowed, 2 Denied, 3 Observed (a gateway in log-only mode) or 4 Modified (the hook rewrote the arguments); `disposition_id` can say 8 Approved or 25 Rejected when a human answered a prompt, and 17 Logged when the policy only observed; and `policy` carries `name`, `uid` and `version`, with the tier the rule came from (managed, project, user, gateway) in `policy.data`, since the Policy object has no tier field (Tier A for the enums, read at schema.ocsf.io 1.9.0; the tier placement is my judgement, D). `activity_id` has no decision value, so it stays 99 Other. The two records share the harness's tool-use id, which has no typed home in 1.9.0 and goes to `unmapped.tool_use_id`; main's `ai_capability.transaction_uid` is the candidate once 1.10.0 ships. With the pair in place, an allow with no execution record in the session is the anomaly to hunt, because the harness said yes and either nothing ran or nothing was logged.

## What each emitted format owes

| Emitted as | Signal | What the pipeline owes | First move |
|---|---|---|---|
| Nothing | `schema-none` | A record before a schema | Gateway capture of `Mcp-Method` and `Mcp-Name`, client telemetry turned on, server stderr shipped |
| Vendor JSON | `schema-vendor-json` | A full mapping, version-pinned | A schema-constrained mapper, frozen into reviewable code |
| OpenTelemetry | `schema-otel` | A landing choice and a renaming plan | Column-per-attribute landing; a translation table to OCSF paths for the hunt keys |
| OCSF | `schema-ocsf` | A check that the hunt keys are typed and not in `unmapped` | Read three real records and count where the tool name, agent and principal sit |

The `schema-ocsf` row is the one teams tend to treat as finished, and the lab run below argues against that, because OWASP's Agent Observability Standard (AOS) is an OCSF mapping and still puts most agent facts in `unmapped`, so "OCSF-native" may mean a record that validates rather than one whose agent and tool fields are typed.

For vendor JSON the risk is the mapping itself. In an earlier lab run on 141 fields from six vendor log sources mapped to OCSF 1.8.0, a simple alias mapper that could only emit paths existing in the schema invented none by construction, at 0.16 path-correctness and 0.67 coverage, while three blind frontier-model runs invented a path for 17.0 to 26.7 percent of fields and got 57.6 to 68.5 percent exactly right (Tier B, `ocsf-deterministic-mapper/README.md`, `ocsf-mapping-oracle/_frontier/REPLICATION-2026-06-14.md`; frontier runs batched without temperature control, and the invented-path figure is inflated by a subset schema closure). So the constraint removes invented paths and the model supplies accuracy where it is strong, and neither catches a field mapped to a path that exists but is the wrong home, which validates, ships and leaves a detection blind. A gold key or planted-truth test for the sources you run is the control for that, and I would freeze the reviewed mapping into code rather than let a model map at ingest, where output can change between two days without a commit.

For OpenTelemetry the question is the landing, since the GenAI and MCP conventions typed the protocol layer most completely of the shapes tested and are the better wire format for traces, but every attribute R2 used was marked `stability: development` at the pinned registry commit, so a stored corpus may outlive the names it was written with (Tier B, OTel semantic-conventions registry at `e6658f1`, semconv v1.45.0, as read by R2).

## What the landing shape costs at query time

The lab run behind most of this document is small on purpose (Tier B, sdw-lab-benchmarks@91e44df `agent-toolcall-schemas/RESULTS.md`, run 2026-11-09). Ten `tools/call` requests went from the MCP Python SDK 2.3.0 client through a stdio tee to an SDK server, four of them returning `isError: true`, and each call was inventoried as 33 facts, six of them agent context the harness supplied because no agent runtime was in the loop. Each schema's declared mapping was written, read back and checked against the pinned definitions, with zero path failures.

| Class of fact | OCSF main (6003 + `ai_operation`) | OCSF #1754 draft | OTel GenAI + MCP | AOS on OCSF (example 2) |
|---|---|---|---|---|
| Typed | 24 | 22 | 19 | 11 |
| Fingerprint only | 3 | 3 | 0 | 0 |
| JSON blob | 3 | 3 | 3 | 0 |
| Unmapped or custom | 3 | 5 | 11 | 22 |
| Dropped | 0 | 0 | 0 | 0 |

OCSF main types the most because `ai_capability` has slots for the server identity, transport, primitive kind, request id and the four tool annotations, while OTel had no attribute for the server's name on a tool span, the annotations, the schemas or an agent instance id. AOS puts the agent in `actor.user` and nearly everything agent-specific under `unmapped.aos`, its two published examples disagree about where the tool name goes, and its SIEM query examples filter on `unmapped.asop.*`, spelled differently (R2, lines 81-85). The validator result is the one I keep coming back to: all ten AOS records passed the public OCSF 1.9.0 validator with zero errors and all ten OCSF-main records failed on `ai_capability` and the `1.10.0-dev` version string, which will clear when 1.10.0 ships but means the record with two-thirds of its facts in `unmapped` is the one a validator likes best today.

The second half priced the shapes, writing one million synthetic calls three ways in DuckDB 1.5.3 with zstd, as typed OCSF columns (L1), as OTel attributes in one `MAP(VARCHAR, VARCHAR)` column, the ClickHouse-exporter pattern (L2), and as the AOS shape with an `unmapped` JSON document (L3), then running five pre-registered hunts 21 times per cell, with identical answers in every layout.

| Hunt | L3 unmapped / L1 typed | L2 OTel map / L1 typed |
|---|---|---|
| Tool use by agent | 8.4x | 32.3x |
| Argument hunt (designed as the null control) | 5.3x | 7.4x |
| Tool breadth on errors | 5.4x | 10.6x |
| Failure bursts | 4.7x | 10.7x |
| Off-allowlist anti-join | 22.5x | 32.4x |

Other lab agents shared the host during the formal run, so I claim only the within-pass ratios. A rerun under lower load kept the direction on every hunt and barely moved the tool-use and anti-join ratios (8.5x and 21.6x), while the error and burst hunts swung to 14.7x and 16.1x because the typed layout finishes them in single-digit milliseconds, so for those two R2 itself says to quote "roughly 5x to 16x" rather than a point estimate. The argument hunt was meant to come out even, since arguments are JSON everywhere, and did not, because the typed layout filters on the tool name before parsing anything while the unmapped layout parses the whole document on every row just to learn which tool was called. Storage barely cared, 27.4 MB against 30.9 MB, because zstd absorbs the repeated keys, so `unmapped` is paid for at query time on every hunt. The OTel map was slowest on every query, which the pre-registration did not predict, and I would expect a column-per-attribute OTel landing to behave much more like the typed layout, though that was not measured (R2 limits, lines 209-218).

## What the MCP revision moved, and why `mcp-spec-pre-2026-07` is asked

The 2026-07-28 revision deprecated the protocol's Logging feature in favour of stderr or OpenTelemetry (SEP-2577), removed sessions and `Mcp-Session-Id` (SEP-2567), replaced the handshake with per-request `_meta` carrying the version and, as SHOULDs, client and server identity (SEP-2575), required `Mcp-Method` and `Mcp-Name` headers on Streamable HTTP POSTs (SEP-2243), and documented trace context in `_meta` (SEP-414) (Tier A, MCP changelog, re-read 2026-11-10). A lab run against one fixture server on both SDK releases found the revision and the SDK upgrade moving different facts (Tier B, sdw-lab-benchmarks@91e44df `t8a-mcp-before-after/RESULTS.md`; one host under contention, no latency claim).

On the same SDK, the newer revision removed the session id, added the method and tool-name headers, stamped client identity on 11 of 11 requests and server identity on 10 of 10 results, and silenced in-protocol log lines unless asked for. On the same revision, the SDK upgrade from 1.30.0 to 2.3.0 moved a raising tool's failure cause from the client's error text to a server stderr traceback and added OpenTelemetry spans that export nothing until the operator configures a tracer provider. For the landing that means four things:

- A gateway can log the tool name and method from headers without parsing the body, but only for Streamable HTTP on the newer revision, and never for a local stdio server.
- The session id that tied a run of calls together is gone on the newer revision, so the record's session slot empties and whatever replaces it lives in tool arguments, which no schema types (OCSF and OTel carry them as a blob, AOS in `unmapped`).
- A tool failure's cause is on the server, so a pipeline that collects only the client or the wire records failures it cannot explain.
- The trace id exists only if someone configured a tracer provider, and it stops at the MCP boundary unless the server's HTTP client is also instrumented (T8a, lines 163-167).

So `mcp-spec-pre-2026-07` is an inventory signal rather than a problem in itself. A team that upgraded the SDK and still negotiates the older revision gets the SDK's changes and not the revision's, so its gateway has no tool-name header to log, and in R2 the SDK's low-level session negotiated 2025-11-25 by default while the high-level client adopted 2026-07-28 when the server answered `server/discover` (T8a, lines 81-88). A collection plan should expect both shapes for a while and record which one each client and server spoke, as [revalidation-and-pins.md](revalidation-and-pins.md) also asks.

## Where the schema runs out

The field count says which shape to store, but whether any shape carries what a detection needs is a separate question, and the AI objects help less than their names suggest. `ai_capability` holds the tool description and schemas as fingerprints only, so a drift event cannot tell a typo fix from a hidden instruction and a poisoning detection needs the text from `unmapped` or a side store, as [mcp-servers-and-manifest-drift.md](mcp-servers-and-manifest-drift.md) measures. `ai_model` is an identity descriptor with four attributes, so a swapped model that reuses a name looks identical in telemetry until the object gains a digest of the weights (Tier B, `d3fend-ocsf-ai-alignment/RESULTS.md:22-26`). And OCSF has two competing tool-call shapes right now, main's structural `ai_capability` and the #1754 draft's free-text tool name with input and response payloads and an `is_pre_occurrence` flag, which is the one property that tells a proposed call from an issued one (same source, lines 32-41), so a team writing main-branch records today should expect a re-map when #1754 settles.

Lining the D3FEND AI artifact nouns up against the OCSF `ai_*` objects gave no exact match in 25 rows, mostly granularity and version gaps, and agent memory has no telemetry home in OCSF at all, since `memory_activity` is operating-system process memory (Tier B for a reading of pinned definitions, `d3fend-ocsf-ai-alignment/RESULTS.md:9-18, :42-46`). Training and fine-tuning events have no OCSF counterpart either, while inference maps partially to API Activity carrying the profile (same source, lines 51-52). Schema vocabulary is also not evidence that any producer emits it; my impression is that very little is landing in these objects natively yet, but that is an observation and not a measurement (Tier D).

## What this does not mean

It does not mean OCSF is the only defensible storage shape, since a SOC already on OTel traces in a column-per-attribute store may get most of the query benefit without it, and the case for OCSF here is mostly that a typed record joins on the same actor and endpoint columns as the rest of the SOC's data, a judgement about consolidation (Tier D). It does not mean AOS is wrong to exist, since a producer could type more AOS facts than its published examples show, and R2 scored the examples. And it does not mean writing main-branch `ai_capability` is free: those records fail a 1.9.0 validator today, and if #1754 merges in a different shape the mapping needs revisiting, which is why I would stamp the version and keep the raw message. The lab runs were one host, one SDK family, stdio for the schema comparison and a synthetic corpus for the timing, so I would carry the shape of each finding and not the exact ratios.

## Gaps

- **Gap: gateway header logging**. Whether common AI and API gateways log `Mcp-Method` and `Mcp-Name` by default is unchecked. **Needs**: a desk pass over gateway documentation with a dated row per product, shared with mcp-servers-and-manifest-drift.md.
- **Gap: OpenTelemetry column landing**. Only a single attributes map was timed. **Needs**: the R2 hunts re-run with one column per attribute on an isolated host.
- **Gap: Streamable HTTP and a real agent runtime**. The schema comparison was stdio only, with agent identity supplied by the harness. **Needs**: the R2 mapping repeated over a Streamable HTTP capture from a real agent runtime on revision 2026-07-28.
- **Gap: native producers**. No survey says which products emit OCSF records carrying the `ai_operation` profile today. **Needs**: a dated producer inventory from vendor documentation, Tier B per row.
- **Gap: AI event class**. The landing on API Activity is an interim choice until #1754 or a successor merges. **Needs**: a re-map of the path table against the first OCSF release that carries an AI event class.
- **Gap: agent memory telemetry**. OCSF has no object for agent memory, so memory poisoning has nowhere to land. **Needs**: an OCSF release that carries one, or an interim `unmapped` convention with a producer behind it.
- **Gap: frontier mapper behind the constraint**. Whether a frontier model behind a schema constraint keeps its accuracy with zero invented paths is unmeasured. **Needs**: the constrained-mapper harness run with a pinned frontier model.

## Notes

- 2026-11-10: lab citations point at sdw-lab-benchmarks commit 91e44df on master, which holds the R2, R8 and T8a folders and the earlier mapping runs.
- 2026-11-10: the 1.9.0 names in the path table were re-read from schema.ocsf.io (API Activity, three profiles and eleven objects), the main names from `d1cbd61`, and PR numbers and merge dates from the OCSF changelog and the pull requests.
- 2026-11-10: the 1.9.0 homes for the tool name, request id, trace context and policy tier are my judgement (Tier D).
- 2026-11-10: the recommendation to write main-branch `ai_capability` now, rather than hold it in `unmapped` until 1.10.0, is a judgement call (Tier D) that trades a re-map risk for typed columns today.
- 2026-11-10: the June mapping runs (OCSF 1.8.0) are cited for the shape of the result, not a current accuracy figure.
- 2026-11-10: the cross-provider verification leg found the summary listing `ai_operation` among the 1.9.0 objects; at tag v1.9.0 it is a profile (`profiles/ai_operation.json`, no `objects/ai_operation.json`), as the path table already said, so the summary sentence now names it as the profile (analysis/VERIFICATION-LOG.md).

## Sources

Tier A

- OCSF schema 1.9.0, published at https://schema.ocsf.io/1.9.0/ (API Activity class 6003, profiles and objects as listed in the notes), read 2026-11-10.
- OCSF schema repository, `CHANGELOG.md` and objects on main at commit d1cbd61 (1.10.0-dev), https://github.com/ocsf/ocsf-schema, read 2026-11-10.
- OCSF pull requests #1488, #1641, #1665, #1674, #1704 and #1729, https://github.com/ocsf/ocsf-schema/pulls, merge dates read 2026-11-10.
- Model Context Protocol specification 2026-07-28, changelog, https://modelcontextprotocol.io/specification/2026-07-28/changelog, read 2026-11-10.

Tier B, standards-body and project documentation of what a field is

- OCSF pull request #1754, "[draft] Add AI Agent Activity event class", https://github.com/ocsf/ocsf-schema/pull/1754, at commit 08d6f53, open and draft on 2026-11-10.
- OpenTelemetry semantic conventions, GenAI and MCP registries at commit e6658f1 with semconv v1.45.0, https://github.com/open-telemetry/semantic-conventions, as pinned by lab run R2.
- OWASP Agent Observability Standard, "Trace with OCSF", https://aos.owasp.org/spec/trace/extend_ocsf, at commit 9a9bc37, as pinned by lab run R2.

Tier B, first-party lab work (one host; the three November runs have pre-registrations frozen by the agent and not reviewed by the maintainer, each verdict VERIFIED-WITH-FIXES)

- sdw-lab-benchmarks@91e44df `agent-toolcall-schemas/` (R2), RESULTS.md and VERIFICATION.md, https://github.com/flying-coyote/sdw-lab-benchmarks/tree/91e44df/agent-toolcall-schemas
- sdw-lab-benchmarks@91e44df `t8a-mcp-before-after/` (T8a), RESULTS.md and VERIFICATION.md, https://github.com/flying-coyote/sdw-lab-benchmarks/tree/91e44df/t8a-mcp-before-after
- sdw-lab-benchmarks@91e44df `d3fend-ocsf-ai-alignment/` (R8), RESULTS.md and VERIFICATION.md, https://github.com/flying-coyote/sdw-lab-benchmarks/tree/91e44df/d3fend-ocsf-ai-alignment; an analysis of pinned definitions, not a measurement.
- sdw-lab-benchmarks@91e44df `ocsf-deterministic-mapper/` and `ocsf-mapping-oracle/` (June 2026 mapping runs, OCSF 1.8.0), https://github.com/flying-coyote/sdw-lab-benchmarks/tree/91e44df; frontier runs batched without temperature control, invented-path metric subset-sensitive.
