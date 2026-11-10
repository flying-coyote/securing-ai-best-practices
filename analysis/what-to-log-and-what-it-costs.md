---
evidence-tier: Mixed
convergence: single-source
applies-to-signals: [content-channel-off, content-channel-on, prompt-capture-tier-none, prompt-capture-tier-metadata, prompt-capture-tier-hash, prompt-capture-tier-delta, prompt-capture-tier-full]
surfaces: [S2, S4, S5, S7, S8, S9, S10]
pins:
  - "OCSF 1.9.0"
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-04-10
status: EMERGING
measurement-claims:
  - claim: "Per million billed tokens, coding tier, Parquet with zstd at its default level 1: metadata only about 1.1 KB, metadata plus prompt and response hashes about 2.6 KB, delta text 26 to 32 KB, full prompt as sent about 0.2 MB to 0.9 MB, roughly 180 to 800 times the metadata footprint, with the top of that range from a single-seed exploratory probe"
    source: "sdw-lab-benchmarks branch hub/ai-research-2026-11-09 agent-telemetry-retention/RESULTS.md"
    date: 2026-11-09
    revalidate: 2027-05-10
  - claim: "Full prompt text for 1,000 coding users at the documented average volume costs $20 to $79 a month on S3 Standard on the pre-registered grid ($19 to $89 including the exploratory probe), against an inference bill of roughly $2.4M a year; AWS us-east-1 list prices of 2026-06-10"
    source: "sdw-lab-benchmarks branch hub/ai-research-2026-11-09 agent-telemetry-retention/RESULTS.md"
    date: 2026-11-09
    revalidate: 2027-01-10
  - claim: "Raw JSON at ingest is about 100 GB per active day per 1,000 coding users for full-context text, against about 3.3 GB for delta text and 0.6 GB for metadata"
    source: "sdw-lab-benchmarks branch hub/ai-research-2026-11-09 agent-telemetry-retention/RESULTS.md"
    date: 2026-11-09
    revalidate: 2027-05-10
  - claim: "Claude Code 2.1.321 OpenTelemetry export at documented defaults delivers 8 of 12 fields and withholds the four content fields as lengths or <REDACTED>; all 12 arrive only with the content gates on"
    source: "sdw-lab-benchmarks branch hub/ai-research-2026-11-09 t2-platform-telemetry/RESULTS.md"
    date: 2026-11-09
    revalidate: 2027-03-10
---

# What to log and what it costs: metadata first, content on trigger

Evidence tier: Mixed. B for the lab's measured bytes (single host, synthetic records built from real public text, pre-registered and independently re-run), B for vendor documentation of what a feature does, for regulator guidance and for preprints, and C for the vendor usage figures behind the volume, A for the statute, court and peer-reviewed sources, and D for the capture-tier model and the trigger list, which are my design.

## Summary for the review

Keeping full prompt text is cheap in object storage and expensive everywhere else, so the record worth building is metadata and keyed hashes on every surface, with content written only when a defined trigger or a defined surface earns it. The storage bill for full text is tens of dollars a month per thousand coding users; the real costs are erasure, privacy, legal exposure and any tool licensed on ingest.

- Keep the metadata tier on every surface that emits a record, widened with the tool-call decision, typed arguments where a schema types them, classifier verdicts and sensitivity labels, routed to the SIEM. Effort S. Tier B (lab, vendor docs).
- Add a keyed hash of prompt and response, with the key held by security and destroyed at the end of retention. Effort S. Tier A for keyed over plain hashing; D for key destruction as an erasure control.
- Write a short list of triggers that promote a session's delta text into the record (a verdict fires, a destructive or external-write tool is called, an investigation is opened, a credential is confirmed stolen), and get it into the DPIA and any works agreement before switch-on. Effort M. Tier D.
- Buffer content for days, not months, so a trigger can reach what came before it; land it in object storage and send only the metadata projection to an ingest-metered tool. Effort M. Tier B for the ingest arithmetic, D for the buffer design.
- Keep full context only where the deployer owns the prompts, where a specific law names the record, or where delta reconstruction breaks. Effort S to decide. Tier D.
- If you keep text, set the compaction job (sort by session, higher zstd level) as the place the retention bill is decided. Effort M. Tier B.
- Where the attacker is on a stolen cloud key, turning on invocation logging is a control in its own right. Effort S. Tier B.

## Why this matters

Agent telemetry is the first log source I've worked with where the most forensically useful fields are also the largest and the most privacy-exposed, because the prompt, the tool arguments and outputs and the delegation chain are the record of intent, and they are also where pasted secrets and personal data live. OCSF 1.9.0 gave that record a standard home, the `ai_operation` profile with a `message_context` object whose `prompt_text` is "the verbatim instruction, query, or context" given to the model (Tier A, OCSF 1.9.0 schema, read 2026-11-09), so "should we keep the prompt" has become a column a pipeline either populates or leaves null. The instinct I hear most is to log metadata, drop the text and call it a cost decision. The lab measured whether the cost half of that holds, and it mostly doesn't, which moves the decision to where it belongs.

The default state of the platforms is already metadata. The content channel is a second, separately enabled path on almost every sanctioned surface, and `analysis/telemetry-by-surface.md` carries the full table; the rows below are the ones this doc leans on.

| Platform family | Setting | Default | Where the record lands | last-checked |
|---|---|---|---|---|
| Coding agent (Claude Code 2.1.321, OpenTelemetry) | prompt, tool detail, response and tool-content gates | off; the four content fields arrive as lengths or `<REDACTED>` (lab-measured, three trials) | your collector | 2026-11-09 |
| Managed platform (Amazon Bedrock) | model invocation logging | off until configured; bodies up to 100 KB inline once on | your S3 bucket or CloudWatch | 2026-11-09 |
| Local runtime (Ollama 0.20.6) | server log | no content, identity, per-request model or token fields at the default level (lab-measured) | nowhere unless the caller keeps the response | 2026-11-09 |
| Enterprise assistant (Microsoft 365 Copilot, Purview `CopilotInteraction`) | audit record | on; resource ids, labels and `XPIADetected`/`JailbreakDetected` verdicts, with message text held in the mailbox, not the audit record | vendor cloud, reached by audit search and eDiscovery | 2026-11-09 |

## The analysis

### Five capture tiers and what each costs

The tiers below are the five the interview asks about, and they map one-to-one onto the four arms of the lab's retention run (R6) plus "none". The run wrote synthetic OCSF 1.9.0 `ai_operation` records for coding-agent and chat sessions each way, measured the bytes per million billed tokens, and priced a year of retention from those bytes, in Parquet with pyarrow 24.0.0, zstd at its default level 1 (the codec was set explicitly, since pyarrow defaults to snappy) (Tier B, sdw-lab-benchmarks branch hub/ai-research-2026-11-09, agent-telemetry-retention, VERIFIED-WITH-FIXES: every measured number reproduced byte for byte, two hypothesis verdicts were restated, and the real-text corpora reproduce only from the stored files because the prose pool was not snapshotted).

| Tier | What it holds | Bytes per million billed tokens (coding, session-sorted to random) | Raw ingest per active day, 1,000 coding users |
|---|---|---|---|
| none | nothing beyond what the platform keeps on its own terms | 0 | 0 |
| metadata | identity, session, model, token triple, tool name, cost, timestamps; plus the typed decision, verdict and label columns described below | 1,067 to 1,151 | about 0.6 GB |
| hash | metadata plus a hash of prompt and response | 2,563 to 2,655 | not separately stated |
| delta | the new text each request added, in session order | 25,922 to 32,476 | about 3.3 GB |
| full | the whole prompt as sent on every request, and the response | 195,906 to 785,203 (pre-registered grid) | about 100 GB |

The run puts full-context text at roughly 180 to 800 times the metadata footprint, with the top of that range coming from a single-seed exploratory probe, and in every delta and full cell at the default codec level the text columns were 95% to 99.9% of the compressed bytes, so content is the whole storage question. Priced at AWS us-east-1 list ($0.023 per GB-month for S3 Standard, read 2026-06-10) and the volume the Claude Code costs page implies (about $13 per developer per active day, converted through the page's own `/usage` example to about 23.5M billed tokens a day over about 185 active days; Tier B for what the product does, C for the usage figures, and the conversion assumes the example's model and cache mix), 1,000 coding users holding full text cost $20 to $79 a month on the pre-registered grid, or $19 to $89 once the exploratory probe is included, against an inference bill of roughly $2.4M a year. So object-storage dollars are a poor reason to drop the text, and I'd push back on anyone who frames it that way.

The bytes bite in two other places. The first is any tool metered on ingest, where full-context raw JSON is about 100 GB per active day per 1,000 users, so the run supports landing content in object storage and sending a metadata projection to the SIEM, which is the split I'd use for any high-volume source. The second is that the full-context number moved by an order of magnitude on knobs few people treat as retention policy, since session-sorted full text was 4.0 times smaller than randomly ordered full text, and most of a large zstd-19 saving came from oversized pages a streaming writer won't see. A collector that flushes small files every few seconds lands near the random-order row, and a nightly compaction that sorts by session and rewrites at a higher level brings the same data down several-fold, which is why I'd call the compaction job the real retention budget.

### Which tier answers which security question

Prompt and response text is the record of intent, and nearly every other security question about an AI interaction is about action, which leaves a different record. In my reading of the published incidents, the action record answers most detection and scoping questions, and content is decisive in three narrower kinds of question.

- The instruction behind an action an agent took. Invariant Labs' May 2025 disclosure described an agent on GitHub's MCP server hijacked by a public issue into reading a private repository and leaking it into a public pull request (Tier B, vendor research). Every step is a tool call, so metadata catches "private read then public write" and names what leaked, which is enough to contain and notify, while only the text says which issue carried the instruction and so which other sessions read it.
- What text actually moved. A sensitivity label or DLP verdict says something labelled left; it cannot say what was pasted that no label ever touched, which only the text or a classifier over it can.
- Reproducing or characterizing an interaction. Permiso's 2024 honeypot report found that "none of the affected clients had invocation logging enabled to better understand the motivations of the attacker", so victims could count and price the abuse and could not say what had been generated, which matters when some of it is material with a reporting duty (Tier B, permiso.io, 2024-10-03).

Two cases bound the claim from either side. Anthropic's November 2025 GTG-1002 report describes a campaign whose tasks each "appeared legitimate when evaluated in isolation", caught by "the sustained nature of the attack" and content classifiers at the provider (Tier B, the vendor describing its own detection), which I read as the strongest argument for classifier verdicts in the always-on record and a weak one for a deployer keeping every word. The Nx "s1ngularity" compromise of 2025 went the other way, since Wiz's published indicators were GitHub audit events and repository names, and no prompt log was needed to detect, scope or remediate it (Tier B, wiz.io, 2025-09-03).

The academic record supports the split for known patterns and qualifies it for agent misuse. A 2026 preprint found metadata and OpenTelemetry-shaped views detect 99.5% to 100% of synthetic faults while localising at most 0.5% of their origins (Tier B, preprint, arXiv 2608.07899), which is "detect on the facts, find the cause in the words" stated as a benchmark. Another found that adding tool results and agent reasoning lifted the strongest monitor's recall on goal-directed agent misuse from 0.52 to 0.94 in one generator panel, with smaller gains in two more and none at all in the fourth (Tier B, preprint, synthetic setting, arXiv 2609.06966), so for misuse hidden in routine agent work, content read by a monitor seems to help detection too. I take that as a reason to run classifiers over the content and keep their verdicts, rather than a reason to retain all text. Two other limits hold whichever tier you choose. An agent's own account of what it did is generated text, not a log, and model explanations can omit the real cause of an answer (Tier A, Turpin et al., NeurIPS 2023). And the cause of a tool failure may never leave the server: the lab saw one MCP Python SDK server return the same `Error executing tool <name>` for three different failures (Tier B, sdw-lab-benchmarks branch hub/ai-research-2026-11-09, agent-toolcall-schemas, one SDK version), so the server's stderr belongs beside the tool-call facts.

### The metadata tier is not content-free

Three cautions apply to the cheap tiers. A typed tool argument such as a file path or SQL string is content in miniature, and file paths turned up in 72% of 25 public log datasets while 7% of the anonymisation literature discussed them (Tier A, Aghili, Li and Khomh, FSE 2025, 10.1145/3715779). A plain hash of a short prompt can be confirmed by guessing, which NIST documents with the 2014 New York taxi release, where MD5-hashed medallion numbers were reversed by hashing every possible value and a keyed hash with an unreleased key would have prevented it (Tier A, NIST IR 8053, §3.2), so the hash tier needs a keyed hash, and it still leaks equality between identical prompts for as long as the key lives. And a classifier verdict is a judgement about a person's text with an error rate, since one prompt-injection detector above F1 0.98 in distribution misclassified roughly a third of external benign security-adjacent text (Tier A, PIDS-Bench, IEEE Access 2026, 10.1109/ACCESS.2026.3728186), so the DPIA should name each classifier and what it gets wrong.

### Content on trigger, and the buffer that makes it work

This is my proposal (Tier D), and it is also the shape the EU texts point at. Recital 49 GDPR and the EDPB's Guidelines 1/2024 (paras. 126 to 128) accommodate security processing on legitimate interest while warning that it "cannot justify an excessive processing" and asking whether a less restrictive means would do; the 2017 WP29 opinion on data processing at work says a security appliance "may also be configured not to store log data unless the appliance signals the occurrence of an incident"; and Bărbulescu v. Romania (ECtHR Grand Chamber, 2017, §121) distinguishes monitoring "the flow of communications" from their content, which needs "weightier justification" (Tier A for the Regulation and the judgment, B for the EDPB and WP29 guidance; my reading is D and not legal advice, and `analysis/prompt-capture-and-the-law.md` carries it). A trigger written into the pipeline is that weightier, separate reason made mechanical.

The triggers I'd start from are a classifier or guardrail verdict, a DLP match, a destructive or external-write tool call, an off-allowlist MCP server, a delegation chain that escalates, an identity under a documented investigation, a user-reported model fault and a confirmed stolen credential. Two qualifiers come with that list. Stacking verdict triggers compounds their false positives, since LLMail-Inject's stress test put single defences at 0% to 5.7% false positives and all of them stacked at 10% (Tier A, Findings of EMNLP 2026, appendix Table 8, a Microsoft-led study of largely Microsoft defences), so measure the rule on your own tool outputs first. And a trigger can reach content that came before it only if the content channel is on and buffered somewhere short-lived (a bucket with a lifecycle rule of days, or a collector that drops text after a window unless a trigger promotes the session); without that buffer, delta capture runs forward from the trigger, which answers what the agent did next and loses what it was told.

Delta text in session order plus a version hash of the system prompt can rebuild an append-only agent's full prompt, and the hash of the full prompt verifies the rebuild, which on the run's medians is roughly an eighth to a twenty-fourth of full-context storage. That rebuild breaks wherever the agent compacts or summarises its own context, which many coding agents do on long sessions, and that is the real reason for a full-context exception.

## What this does not mean

It does not mean storage is free, because the bill excludes SIEM ingest licensing, query, PUT requests from small-file writers and the cost of erasure, which in a full-context store means rewriting every later record in a session that repeated one pasted secret. It does not mean content is useless for detection, since the agent-misuse result above cuts the other way. It does not mean pseudonymising text at write makes the delta tier low-risk: an LLM-plus-rules detector recalled 69.0% of what human annotators found in shared chatbot conversations (Tier A, Mollaeefar et al., PoPETs 2026, 10.56553/popets-2026-0081), so a redacted delta store is still personal data. Outside the EU the legal posture differs, and a US employer can keep full text with notice or consent, which is why US-designed products often default to capture. And the volume rests on one vendor page, so an organization with its own token counts should use the bytes-per-million-tokens figures and its own volume.

## Gaps

- **Gap: price of the widened metadata tier**. R6 priced the hash arm only; the verdict, label and typed-decision columns this doc puts in the metadata tier are small typed columns nobody has measured. **Needs**: a fifth R6 arm with those columns populated at realistic cardinality.
- **Gap: trigger false-positive rate on real tool outputs**. The detector numbers cited are external benchmarks, not an organization's own agent traffic. **Needs**: a pre-registered bench running the trigger list over a recorded fixture of real coding-agent tool outputs and counting the windows it opens.
- **Gap: how often delta rebuild fails**. The context-compaction break is documented in behaviour but uncounted. **Needs**: a count of compaction events per session on a real or realistically driven coding-agent fleet.
- **Gap: real prompt compressibility**. R6's records are synthetic in arrangement and one record per request. **Needs**: a re-run of R6's instrument on a consented real prompt corpus and on an emitter that writes one record per tool call or the full message array per span.
- **Gap: ingest-metered cost**. No SIEM licence cost is priced, and licence terms may vary too much to model. **Needs**: a desk pass over published ingest price lists, dated, with the 100 GB per day figure applied.
- **Gap: key destruction as erasure**. Destroying the hash key at the end of retention is a design, untested as an erasure control. **Needs**: a regulator or court position on keyed-hash pseudonyms after key destruction, or a documented DPIA that relied on it.

## Notes

- Tier definitions (claim-level choice, Decision 16, 2026-11-10). The research this doc draws on used two definitions of the second tier: one as metadata plus a keyed hash, the other adding typed tool arguments, classifier verdicts and sensitivity labels. This doc uses the first for the `hash` tier, because it matches the interview's five keys and the lab arm that was priced, and moves the typed decision, verdict and label fields into the `metadata` tier as typed columns, because they are flow facts emitted at metadata cost and the always-on record needs them. The cautions in "The metadata tier is not content-free" travel with that choice.
- Ranges (claim-level choice, Decision 16). The bill leads with R6's pre-registered grid ($20 to $79 a month) and names the headline range that includes the single-seed exploratory probe ($19 to $89) beside it; the 180 to 800 times ratio is quoted as the run states it.
- The price claim revalidates earlier than the byte claims because AWS list prices were read 2026-06-10. Every lab source is cited by branch and folder until the branch merges, and each becomes a commit hash before the v0.1 release.
- The trigger list, the buffer design and the reconstruction rule are my judgement as of 2026-11-10 and carry Tier D until a bench closes the gaps above.

## Sources

Tier A
- OCSF 1.9.0 schema, `message_context` object and `ai_operation` profile, schema.ocsf.io, read 2026-11-09.
- Regulation (EU) 2016/679, Recital 49 and Articles 5, 6(1)(f), 17, EUR-Lex CELEX 32016R0679, read 2026-11-09.
- Bărbulescu v. Romania, ECtHR Grand Chamber, application 61496/08, 5 September 2017, §121, HUDOC item 001-177082.
- Garfinkel, "De-Identification of Personal Information", NIST IR 8053, 2015, 10.6028/NIST.IR.8053, §3.2.
- Aghili, Li, Khomh, "Protecting Privacy in Software Logs: What Should Be Anonymized?", FSE 2025, 10.1145/3715779.
- Mollaeefar et al., "Chatbot Confessions", Proceedings on Privacy Enhancing Technologies 2026(3), 10.56553/popets-2026-0081.
- Shire, Kim, "PIDS-Bench", IEEE Access 2026, 10.1109/ACCESS.2026.3728186.
- Abdelnabi et al., "LLMail-Inject: A Dataset from a Realistic Adaptive Prompt Injection Challenge", Findings of EMNLP 2026, appendix Table 8 (Microsoft-led; the classifier defences tested are Microsoft's, flagged).
- Turpin, Michael, Perez, Bowman, "Language Models Don't Always Say What They Think", NeurIPS 2023, 10.52202/075280-3275.

Tier B
- SDW lab, R6 agent-telemetry retention, sdw-lab-benchmarks branch hub/ai-research-2026-11-09, agent-telemetry-retention/RESULTS.md and VERIFICATION.md, 2026-11-09 (pre-registration frozen by the run agent before the run, independently re-run; single host; synthetic records with real public code and prose).
- SDW lab, T2 platform telemetry, same branch, t2-platform-telemetry/RESULTS.md, 2026-11-09 (one host, three trials per configuration).
- SDW lab, R2 tool-call schemas, same branch, agent-toolcall-schemas/RESULTS.md, 2026-11-09 (one SDK, one host).
- EDPB Guidelines 1/2024 on Article 6(1)(f), version 1.0 for consultation, 8 October 2024, paras. 126 to 128.
- Article 29 Working Party, Opinion 2/2017 on data processing at work (WP249), §5.3.
- Anthropic, Claude Code costs, code.claude.com/docs/en/costs, fetched 2026-11-09 (B for what the product does; C for the usage figures, vendor interest flagged).
- Amazon Bedrock model invocation logging documentation, read 2026-11-09; Microsoft Learn, "Audit logs for Copilot and AI applications", ms.date 2026-08-26.
- Permiso, "Exploiting hosted models", permiso.io/blog/exploiting-hosted-models, 2024-10-03.
- Invariant Labs, GitHub MCP vulnerability, invariantlabs.ai/blog/mcp-github-vulnerability, 2025-05-26 (vendor research with a product to sell).
- Anthropic, "Disrupting the first reported AI-orchestrated cyber espionage campaign", November 2025 (the vendor describing its own detection).
- Wiz, "s1ngularity's aftermath", wiz.io/blog/s1ngularitys-aftermath, 2025-09-03.
- Zhu, Pu, "TelemetrySuffBench", arXiv 2608.07899, 2026 (preprint).
- Muhamed, Smith, "MOLE: Detecting Insider Threats in AI Agents", arXiv 2609.06966, 2026 (preprint, synthetic setting).

Tier D
- The capture-tier model, trigger list, buffer design and reconstruction rule in this document.
