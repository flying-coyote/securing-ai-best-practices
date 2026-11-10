---
evidence-tier: Mixed
convergence: single-source
applies-to-signals: [record-in-agent-reach]
surfaces: [S4, S5, S7, S8, S13]
pins:
  - "OCSF 1.9.0"
  - "NIST SP 800-53 Rev. 5 5.2.0"
  - "IETF RFC 8785 as read 2026-11-10"
  - "Claude Code 2.1.321 (lab run T9) and Claude Code documentation as read 2026-11-10"
  - "DuckDB 1.5.3, pyarrow 23.0.1, Polars 1.41.2, DataFusion 53.0.0 and chDB 4.1.8 (lab runs of 2026-06-06)"
  - "AWS CloudTrail and Amazon S3 Object Lock documentation as read 2026-11-10"
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-03-10
status: EMERGING
measurement-claims:
  - claim: "In Claude Code 2.1.321 headless, the evidence of a PreToolUse hook or permission-rule decision lived in four places (session transcript, stream-json, debug log, OpenTelemetry) and only OpenTelemetry was a wire format; the transcript and debug log are local files under the user's own config and working paths; one host, one version, one run per cell"
    source: "sdw-lab-benchmarks@91e44df t9-pretooluse-hook-enforcement/RESULTS.md:39-50, :119-122"
    date: 2026-11-09
    revalidate: 2027-03-10
  - claim: "disableAllHooks set in a developer's local settings file switched off a hook defined in the committed project file and the forbidden command ran; in the OTLP log stream the only trace of the disabled hook was a missing hook_registered event, and the debug log carried no hook line at all"
    source: "sdw-lab-benchmarks@91e44df t9-pretooluse-hook-enforcement/RESULTS.md:24-31, :100, :121"
    date: 2026-11-09
    revalidate: 2027-03-10
  - claim: "The same 500,000 logical rows written to Parquet by DuckDB's default multi-threaded path came out at 2,788,104, 2,788,326 and 2,869,621 bytes across three runs, with the order-independent logical hash 857a280427ea7f55 every time; single-threaded and ORDER BY writes were byte-stable; synthetic corpus, one host"
    source: "sdw-lab-benchmarks@91e44df ocsf-parquet-determinism/RESULTS.md:29-34, :46-50"
    date: 2026-06-05
    revalidate: 2027-05-10
  - claim: "With one byte flipped inside a checksummed Parquet data page, chDB 4.1.8 raised an error by default, pyarrow 23.0.1 and Polars 1.41.2 returned a silently wrong sum unless pyarrow's page_checksum_verification was turned on, and DuckDB 1.5.3 and DataFusion 53.0.0 exposed no read-side verification"
    source: "sdw-lab-benchmarks@91e44df parquet-checksum-integrity/results/RESULTS.md:15-41"
    date: 2026-06-06
    revalidate: 2027-03-10
  - claim: "Summing the same 2,000,000 doubles gave three distinct last-ULP results across five engines (DuckDB; pyarrow, Polars and DataFusion; chDB) while integer sum, count, min and max were bit-identical; a pyarrow-written Parquet Modular Encryption file was read by pyarrow with the key and refused by all five readers without it"
    source: "sdw-lab-benchmarks@91e44df parquet-determinism-encryption/results/RESULTS.md:33-46, :50-61"
    date: 2026-06-06
    revalidate: 2027-03-10
  - claim: "A parser pinned to the older published PAN-OS TRAFFIC spec read 35 of 47 fields to wrong but present values after a documented mid-record field shift, with nothing firing, while the equivalent changes in Zeek conn.log and CloudTrail announced themselves; replayed from vendor specs, existence and not prevalence"
    source: "sdw-lab-benchmarks@91e44df spec-vs-emitted-integrity/RESULTS-realvendor-2026-06-16.md:22, :36-38, :45-47"
    date: 2026-06-16
    revalidate: 2027-07-10
  - claim: "A drift rule over OCSF ai_capability fingerprints fired on 9 of 9 authored poisoned tool-manifest changes and 12 of 15 authored benign ones, because a hidden instruction and a wording fix move the same fingerprint"
    source: "sdw-lab-benchmarks@91e44df mcp-manifest-drift/RESULTS.md:37-45, :51"
    date: 2026-11-09
    revalidate: 2027-03-10
---

# Tamper-evident records: keeping the agent's account of itself out of its reach

Evidence tier: Mixed, with the OCSF 1.9.0 schema, NIST SP 800-53 and two peer-reviewed papers on secure logging at A, vendor documentation of what a feature does and six single-host lab runs at B (the PAN-OS replay at B/C, two runs independently verified), and the storage design and the order of the practices at D.

## Summary for the review

This repo's working thesis is that most of the telemetry about an AI agent today is the agent's harness describing itself, written on the same machine under the same user the agent runs as, so the first question about that record is who can change it, because a record the actor can edit or switch off proves little about what the actor did. The practices below move the record out of reach first, then make tampering detectable with a key the actor does not hold, then deal with storage.

- Find where each agent's record lands and which identity can write or delete it, exporter settings included. Effort S. Tier B (lab run T9, vendor documentation).
- Export the record off the machine from a settings tier the agent cannot edit, into a store where the producing identity cannot overwrite or delete, as NIST SP 800-53 AU-9(2) asks. Effort M. Tier A for the control, B for the features.
- Turn on provider-side integrity validation where the platform offers it, such as CloudTrail log file validation, and keep the digests apart from the logs. Effort S. Tier B.
- Attach OCSF 1.9.0 `record_integrity` attestations, chained per agent session with `chain_uid` and `prev_event`, signed with a key the agent cannot read, with the chain head committed somewhere the signer cannot rewrite. Effort L. Tier A for the schema, D for the design; my one search turned up one partial producer.
- In a lakehouse, keep the signed canonical bytes beside the typed columns and verify against them, and turn on Parquet page-checksum verification where the reader offers it. Effort M. Tier B for the checksum split, D for the design.
- Read a valid signature as evidence that the record is unchanged since signing, which says nothing about whether it was right when it was made. Effort S. Tier B/C.

The signed chain is single-source here, so adopting it is your risk acceptance; in plain terms, no standard requires this format yet, and if it never converges the cost is a signing service and its key custody.

## Why this matters

When I look at what an organization actually holds about its coding agents, MCP clients and SOC agents, the record is mostly self-reported. Lab run T9 put hook and permission-rule decisions through Claude Code 2.1.321 in headless mode and found the evidence of each decision in four places, the session transcript, the stream-json output, the debug log and OpenTelemetry, of which only OpenTelemetry is a wire format, while the transcript lives under the user's own config directory as `<config>/projects/<slug>/<session>.jsonl` and the debug log is a local plain-text file (Tier B, sdw-lab-benchmarks@91e44df t9-pretooluse-hook-enforcement/RESULTS.md:39-50, :119-122; one host, one version, one run per cell, verdict VERIFIED-WITH-FIXES). Two of those four channels are files the agent's own process can write to, since the agent runs as the developer (my reasoning from where the files live, Tier D), and that is the condition the `record-in-agent-reach` question asks about.

The same run showed how quietly a record can go missing. A `disableAllHooks: true` in a developer's local settings file switched off a hook the team had committed to the project file, the forbidden command ran, and in the OTLP log stream the only difference was that the `hook_registered` event never appeared, while the debug log carried no hook line at all, so a disabled hook looked exactly like no hook (Tier B, same run, RESULTS.md:24-31, :100, :121). The hook side is in [coding-agent-hooks-and-policy.md](coding-agent-hooks-and-policy.md), and this document owns the record. Claude Code's own documentation says a repository's settings files cannot turn telemetry on or choose where it goes, but "can still turn a signal off by setting its exporter selector, such as `OTEL_LOGS_EXPORTER`, to `none`, unless managed settings, a `--settings` file, or the environment you start Claude Code from sets that variable", and that `cleanupPeriodDays`, which sets how long transcripts are kept before a background sweep deletes them "without showing a message", defaults to 30 days and can be set from any settings file (Tier B, Claude Code monitoring and settings-reference documentation, read 2026-11-10). Put those together with an agent that can edit files in its working repository, and where the exporter is set in the user's own settings file rather than in managed settings, `--settings` or the launching environment, the documented behaviour allows an agent, or an injected instruction steering one, to switch off its own export and shorten its own transcript retention by writing one project file. That inference is mine (Tier D); T9 did not measure it, and I list it under Gaps.

None of this is new as a control, which is part of why I think it should come first. NIST SP 800-53 AU-9 asks that audit information be protected "from unauthorized access, modification, and deletion", and AU-9(2) asks that audit records be stored "in a repository that is part of a physically different system or system component than the system or component being audited" (Tier A, NIST SP 800-53 Rev. 5, OSCAL catalog 5.2.0). AU-9(3) asks for cryptographic mechanisms "to protect the integrity of audit information and audit tools", and in the OSCAL 5.2.0 baselines AU-9(2), AU-9(3) and AU-10 sit in High and none of them in Moderate, so a High-baseline system already owes cryptographic integrity in some format. Schneier and Kelsey's scheme makes entries written before a machine's compromise "impossible to modify or destroy undetectably", which says nothing about entries written after it (Tier A, ACM TISSEC 1999), and Crosby and Wallach keep an untrusted logger honest through auditors who hold earlier commitments to the log, so the property depends on someone other than the logger remembering what the log looked like (Tier A, USENIX Security 2009). An agent writing its own log on the machine it controls is that untrusted logger.

## Out of reach first

So the first practice is placement, and it costs less than the cryptography. The record that counts is the one exported, from a settings tier the agent cannot edit, to a store where the identity the agent runs as has no overwrite or delete right. For Claude Code that means the OpenTelemetry exporter variables set in managed settings, which the documentation says administrators can use to configure telemetry "for all users", rather than in a project file the agent can rewrite; for a SOC agent it means the agent's service identity has append rights on its own audit table at most, and the retention and deletion rights sit with a different role. Which fields go into that record, and at what content tier, is the subject of [what-to-log-and-what-it-costs.md](what-to-log-and-what-it-costs.md), and [prompt-capture-and-the-law.md](prompt-capture-and-the-law.md) already places tamper evidence at its T1 keyed-hash tier, so the out-of-reach practice does not require capturing prompt text.

Storage that refuses deletion is widely available and usually off. Each row below states what the vendor documents, not how well it works.

| Platform family | Setting | Default | Where the record lands | last-checked |
|---|---|---|---|---|
| Claude Code | Session transcripts | Written locally; deleted by a silent sweep after `cleanupPeriodDays`, default 30, settable from any settings file | User config directory on the developer's machine | 2026-11-10 |
| Claude Code | OpenTelemetry export (`CLAUDE_CODE_ENABLE_TELEMETRY`, `OTEL_LOGS_EXPORTER`) | Off until enabled; a repository file can set an exporter to `none` unless managed settings, `--settings` or the environment sets it | The collector the operator names | 2026-11-10 |
| AWS CloudTrail | Log file integrity validation (SHA-256 hashes, hourly digest files signed with SHA-256 with RSA, each digest carrying the previous digest's signature) | On by default for new trails created in the console; set explicitly with `--enable-log-file-validation` on the CLI or `EnableLogFileValidation` on the API | Digest files in the trail's S3 bucket, apart from the log files | 2026-11-10 |
| Amazon S3 | Object Lock, compliance mode | Off until configured; in compliance mode a protected object version "can't be overwritten or deleted by any user, including the root user", while governance mode can be bypassed with a specific permission | The bucket the operator configures | 2026-11-10 |

CloudTrail is the useful model here, because the party that signs the digests is AWS and not the account holder whose actions are logged, and the digest chain means a deleted log file or a deleted digest shows up on validation (Tier B, AWS CloudTrail documentation, read 2026-11-10). That separation of actor and signer is what an agent's self-written record lacks.

## What OCSF 1.9.0 added, and what it cannot do alone

OCSF 1.9.0, released on 2026-08-03, added a `record_integrity` profile to `base_event`, so any event class can carry one optional attribute, `attestation_list`, an array of `attestation` objects (Tier A, OCSF 1.9.0 CHANGELOG lines 55 and 120, PR #1661). Each attestation carries a `fingerprint` of the event, `signatures` computed over that fingerprint, an `authority_uid` naming the party that produced it, and two attributes that turn single records into a chain, `chain_uid` for the append-only chain and `prev_event`, which points at the predecessor by `uid` and `type_uid` and binds to its content through the predecessor's own `fingerprint`. The object requires at least one of `fingerprint` or `signatures`, so a fingerprint-only attestation is legal and catches accidental corruption, while a signed one adds authenticity against a named credential (Tier A, `objects/attestation.json` and `objects/prev_event.json` at v1.9.0). The schema's own example for `chain_uid` is the agent case: "every attestation produced during a single agent session shares one `chain_uid`".

What gets hashed matters for anyone storing these events. The attestation is computed over a canonical serialization of the whole event, including its own `authority_uid`, `chain_uid` and `prev_event` and excluding only `fingerprint` and `signatures`, and because `prev_event` sits inside the hashed content, "deleting or altering an event in a chain breaks the fingerprint and signatures of the event that references it" (Tier A, same file). PR #1662 added `serialization` and `serialization_id` to `digital_signature`, and #1661 mirrored them onto `fingerprint`, with an enum that in 1.9.0 reads Unknown (0), Flat (1), JCS (2), JWS (3), COSE (4), DSSE (5), Authenticode (6), Code Signing (7), App Package (8) and Other (99), and the dictionary text says plainly that "a verifier must apply the same scheme to reproduce the signing input" (Tier A, `objects/digital_signature.json` and CHANGELOG lines 92, 139 and 152-153). JCS is RFC 8785, an Informational RFC from the independent stream that canonicalizes a JSON value so that hashing and signing are repeatable (Tier A, RFC 8785).

So the schema can now say, in a standard field, that this event was produced by the holder of a credential, has not changed since, and follows another event in an append-only chain. Two limits follow from the literature above, and both bear directly on agents. The first is the key. The attestation text itself says the verifiable identity "is a technical credential, such as a key or certificate", so a signature proves only that someone holding that key signed, and if the agent's process or its host can read the key, the agent can rewrite an event and re-sign it, or rewrite the whole chain from the point it wants changed. The second is truncation. A hash chain shows that the entries present are consistent with each other, and it does not show that the newest entries are still there, which is why Crosby and Wallach's auditors hold commitments and why CloudTrail's digests are signed by a key the account holder never sees. My reading (Tier D) is that a useful agent chain needs the signing step outside the agent's process, in a collector or signing service under a different identity, and the chain head, or a periodic digest of it, committed somewhere the signer cannot rewrite, whether that is an Object Lock bucket, a second organization's store or a transparency log in the style of RFC 9162.

On adoption, I want to be careful. I ran one GitHub code search for `attestation_list` on 2026-11-10 and looked at the first 30 hits, most of which used the word for something else; I inspected one that mentioned OCSF and did not open the rest. That one emits the profile, an open-source AI SOC whose evidence-bundle exporter declares OCSF 1.9.0 and writes an `attestation_list` with a SHA-256 fingerprint and a signature entry naming HMAC-SHA256, with no `chain_uid`, `prev_event` or `serialization_id`, and whose bundle carries a note reading "Tamper-evidence, not non-repudiation" because anyone holding the deployment's key can produce a valid signature (Tier B for what the code does, beenuar/AiSOC `services/api/app/services/evidence_bundle.py` at commit a76073c, 2026-10-12). That is a real but partial implementation, applied at export time over a bundle rather than per event at the producer, and its symmetric key is exactly the condition where the producer can forge. One code search is not a survey, so I'd check any claim of support against emitted records.

## The storage layer under the record

Record-level attestation also fixes a problem that file hashing had in a lakehouse. The lab wrote the same 500,000 logical rows to Parquet three times through DuckDB's default multi-threaded path and got 2,788,104, 2,788,326 and 2,869,621 bytes, while the order-independent logical hash stayed at `857a280427ea7f55`, because the parallel hash aggregation and `UNION ALL` emit rows in whatever order the threads finish and Parquet's encodings turn row order into bytes; single-threaded and `ORDER BY` writes were byte-stable (Tier B, sdw-lab-benchmarks@91e44df ocsf-parquet-determinism/RESULTS.md:29-34, :46-50; synthetic corpus, one host). A file hash over Parquet evidence reports changes that never happened to the data, while a per-event attestation survives compaction and re-partitioning as long as the event comes out unchanged.

That condition is the hard part, and it is the part I have not tested. A verifier has to rebuild the exact canonical bytes the producer signed, and a lakehouse stores the event as columns: nested objects land in a struct or a Variant, timestamps take a storage precision, absent and null can collapse into one value, and anything unmapped may be dropped. JCS is deterministic over a JSON value, but it reproduces the signing input only if the JSON value handed to it is the one the producer had, so every lossy step between the wire and the table can turn a faithful record into one that fails verification and looks tampered. I rate that as a hypothesis (Tier D) until a round-trip loop runs. What the lab has measured points at where it will break. Summing the same 2,000,000 doubles gave three distinct last-ULP results across five engines (DuckDB alone; pyarrow, Polars and DataFusion together; chDB alone), while integer sum, count, min and max were bit-identical everywhere (Tier B, sdw-lab-benchmarks@91e44df parquet-determinism-encryption/results/RESULTS.md:33-46). That is about aggregates rather than stored values, so it does not predict that a stored double breaks a signature, but it does say that anything derived and then signed should be hashed over exact types only, and that any engine step which re-types a value on the way out is a candidate for a false tamper alarm.

The design I lean toward, as an opinion until that loop runs, is to keep the signed canonical bytes as their own column beside the typed columns, treat the typed columns as a queryable view, and verify against the stored form. That costs roughly a second compressed copy of each event, unmeasured for OCSF records, and makes verification a byte comparison and a signature check that an engine upgrade cannot quietly break.

Under the record sits the page. Parquet has an optional CRC32 per page, and the lab flipped one byte inside a checksummed data page and summed the column in five readers: chDB 4.1.8 raised an error by default, pyarrow 23.0.1 and Polars 1.41.2 returned a silently wrong sum unless pyarrow's `page_checksum_verification=True` was set (reachable from Polars only through its pyarrow passthrough), and DuckDB 1.5.3 and DataFusion 53.0.0 exposed no read-side verification (Tier B, sdw-lab-benchmarks@91e44df parquet-checksum-integrity/results/RESULTS.md:15-41). A team that verifies records on read gets bit-rot detection largely for free, because a flipped byte in a signed event usually breaks its signature, while a team relying on page CRCs depends on a reader default that differs by engine and version.

Encryption interacts with all of this in one useful way. A pyarrow-written Parquet Modular Encryption file was read by pyarrow with the key and refused by all five readers without it, with DuckDB's and DataFusion's errors naming the encryption (Tier B, same run, RESULTS.md:50-61, full strings in results/results.json). A reader without the key is supposed to fail, so this shows only that encryption fails loudly, and whether the other engines read the file given the key stays open. Until that runs, storage-layer encryption keeps the file readable by every engine that can reach the storage, and since signatures over the canonical event are independent of either scheme, record attestations survive a change of encryption in a way file hashes never did.

## What integrity evidence cannot tell you

Integrity answers whether a record changed after the attester saw it, and the lab has a sharp example of why that is a narrower question than whether the record is right. When a field in the PAN-OS TRAFFIC record moved mid-record between releases, a parser pinned to the older published spec read 35 of 47 fields to values that were wrong but present, with nothing firing, while the same kind of change in Zeek's header-described `conn.log` and in CloudTrail's JSON announced itself (Tier B/C, sdw-lab-benchmarks@91e44df spec-vs-emitted-integrity/RESULTS-realvendor-2026-06-16.md:22, :36-38; replayed from the vendors' published specs, existence and not prevalence). If a pipeline signed those parsed records, the attestation would faithfully prove that 35 wrong values had not changed since they were made wrong. The agent case has the same shape, since a harness that signs its own record proves the record is the one the harness wrote, which is worth having and says nothing about whether the harness reported what the agent did.

The same limit shows up when the fingerprinted thing is a tool manifest. In lab run R5, a rule over the `ai_capability` object on OCSF's main branch (1.10.0-dev, not in a release), which carries fingerprints of a tool's contract and no description text, fired on 9 of 9 authored poisoned changes and on 12 of 15 authored benign ones, because a hidden instruction and a typo fix move the same fingerprint (Tier B, sdw-lab-benchmarks@91e44df mcp-manifest-drift/RESULTS.md:37-45, :51, :156; one host, agent-frozen pre-registration not reviewed by the maintainer, verdict VERIFIED-WITH-FIXES). A fingerprint tells you something moved, and deciding whether the movement was hostile needs the content, which [mcp-servers-and-manifest-drift.md](mcp-servers-and-manifest-drift.md) covers.

## What this does not mean

It does not mean local transcripts are worthless. They are often the richest record of an agent session, and T9 found the transcript the only channel that named which settings file a rule decision came from; the point is only that they cannot be the record of last resort when the question is what the agent did. It does not mean every organization needs signed chains. For many, getting the record off the machine from the managed tier into a store with a separate write identity answers most of the `record-in-agent-reach` question, and the signing work is worth its cost mainly where a regulator, a court or an incident review will ask for proof of non-alteration. And the lakehouse half rests on single-host runs with five-month-old versions and an untested reconstitution argument, so I present it as a design to test, while the out-of-reach practice rests on a control catalogue that asked for it long before agents existed.

## Gaps

- **Gap: agent self-silencing**. That a project settings file the agent can write turns off its own OpenTelemetry export and shortens transcript retention is read from documentation, not measured. **Needs**: a T9-style cell in which an agent, prompted or steered by an injected instruction, edits the project file, with the OTLP sink and the transcript directory checked afterwards, and the same cell with the exporter set in managed settings.
- **Gap: managed tier**. T9 did not measure the managed settings tier, so the claim that managed exporter settings resist a project override is documented and unmeasured. **Needs**: a run with a managed settings file on a disposable host.
- **Gap: producer adoption**. One code search found one partial, HMAC-signed, chainless emitter of `record_integrity`. **Needs**: a dated sweep of shipped OCSF producers, pipeline tools and agent harnesses for the profile, with captured events.
- **Gap: round-trip verification**. Whether JCS-signed OCSF events verify after landing in Parquet or Iceberg and being read back through several engines is untested. **Needs**: a pre-registered loop signing events with chained `prev_event`, landing them through pyarrow, DuckDB and pyiceberg, re-canonicalizing from typed columns in four readers, with a control arm that stores the canonical bytes.
- **Gap: canonical-copy cost**. The storage cost of keeping signed canonical bytes beside typed columns is unmeasured. **Needs**: the control arm of the round-trip loop, reporting bytes per event.
- **Gap: encryption with keys**. Whether engines other than pyarrow read a pyarrow-written PME file when given the key is untested. **Needs**: the 2026-06-06 encryption arm re-run with each engine's own key configuration.
- **Gap: reader versions**. The checksum split is from June 2026 versions. **Needs**: the same byte-flip run on current DuckDB, DataFusion, pyarrow, Polars and chDB releases.

## Notes

- 2026-11-10: DESIGN names `record_integrity` under OCSF 1.9 as a practice that may be `converged` at birth by the standards route, and Decision 7 asks for a published schema plus at least one independent implementation. The only implementation I found is the partial, HMAC-signed, chainless one above, so the doc stays `single-source`, and whether that emitter satisfies the standards route is a reviewer's call.
- 2026-11-10: `surfaces` is my judgement. The `record-in-agent-reach` row sits in no surface's `enables` list, so I chose the surfaces where an agent harness or a SOC agent writes its own record.
- 2026-11-10: the T9 RESULTS.md front matter still reads "not yet independently verified"; its VERIFICATION.md records VERIFIED-WITH-FIXES, and the cited lines are from the fix commit 91e44df.
- 2026-11-10: the PME error strings are paraphrased because the raw strings carry temporary paths.
- Decision 16 choices: the determinism byte counts are quoted per run because the variation is the finding; R5's 12 of 15 is the OCSF-native rule under canonical hashing, and its contract-drift rule fired on 9 of 15.

## Sources

Tier A

- OCSF schema v1.9.0, released 2026-08-03: `profiles/record_integrity.json`, `objects/attestation.json`, `objects/prev_event.json`, `objects/digital_signature.json`, `objects/fingerprint.json` and `CHANGELOG.md` (lines 55, 70-71, 77, 92, 120, 139, 152-153; PRs #1661 and #1662), https://github.com/ocsf/ocsf-schema/tree/v1.9.0, read 2026-11-10.
- NIST SP 800-53 Rev. 5, AU-9 Protection of Audit Information, AU-9(2), AU-9(3), AU-10, OSCAL catalog 5.2.0, https://github.com/usnistgov/oscal-content, read 2026-11-10.
- IETF RFC 8785, JSON Canonicalization Scheme (JCS), June 2020, Informational, independent stream, https://www.rfc-editor.org/rfc/rfc8785.
- IETF RFC 9162, Certificate Transparency Version 2.0, December 2021, Experimental, https://www.rfc-editor.org/rfc/rfc9162.
- Schneier and Kelsey, "Secure audit logs to support computer forensics", ACM TISSEC 2(2):159-176, 1999, doi:10.1145/317087.317089 (abstract).
- Crosby and Wallach, "Efficient Data Structures for Tamper-Evident Logging", USENIX Security 2009, https://www.usenix.org/legacy/event/sec09/tech/full_papers/crosby.pdf.

Tier B, vendor and project documentation of what a feature does (read 2026-11-10)

- Claude Code Docs, "Monitoring", https://code.claude.com/docs/en/monitoring-usage
- Claude Code Docs, settings reference, `cleanupPeriodDays`, https://code.claude.com/docs/en/settings-reference
- AWS, "Validating CloudTrail log file integrity", https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-intro.html
- AWS, "Enabling log file integrity validation for CloudTrail", https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-enabling.html
- AWS, "Locking objects with Object Lock", https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html
- beenuar/AiSOC, `services/api/app/services/evidence_bundle.py` at commit a76073c (2026-10-12), https://github.com/beenuar/AiSOC, found by one GitHub code search for `attestation_list`.

Tier B, first-party lab work

- sdw-lab-benchmarks@91e44df, https://github.com/flying-coyote/sdw-lab-benchmarks: `t9-pretooluse-hook-enforcement/` (T9, run 2026-11-09, RESULTS.md and VERIFICATION.md, VERIFIED-WITH-FIXES), `mcp-manifest-drift/` (R5, run 2026-11-09, VERIFIED-WITH-FIXES), `ocsf-parquet-determinism/` (2026-06-05), `parquet-checksum-integrity/results/` (2026-06-06), `parquet-determinism-encryption/results/` (2026-06-06) and `spec-vs-emitted-integrity/RESULTS-realvendor-2026-06-16.md` (Tier B/C, replayed from published vendor specs). Each run is one host; the 2026-11-09 pre-registrations were frozen by an agent and not reviewed by the maintainer.
