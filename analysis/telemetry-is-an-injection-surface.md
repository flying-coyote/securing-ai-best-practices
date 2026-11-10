---
evidence-tier: Mixed
convergence: single-source
applies-to-signals: [telemetry-into-llm]
surfaces: [S13]
pins:
  - "MITRE ATLAS v2026.10"
  - "MITRE ATT&CK Enterprise v20.1"
  - "OCSF 1.9.0"
  - "OWASP Top 10 for LLM Applications 2026"
  - "Ollama 0.20.6 with gemma4:e4b (digest c6eb396dbd5992bb) and phi4:latest (digest ac896e5b8b34a1f4), DuckDB 1.5.3 (lab run T8b)"
  - "pySigma 2.0.3, pySigma-backend-sqlite 2.1.1, DuckDB 1.5.3 (lab run atlas-ocsf-observables)"
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-02-10
status: EMERGING
measurement-claims:
  - claim: "With an instruction planted in 25% of non-null rows of one adversary-controlled field per table (527 planted values per store), gemma4:e4b saw the planted text in 15 of 15 hunts over planted stores and followed it in 0 of 15, under every rendering sampled including raw; 0 of 15 is consistent with a true follow rate up to about 18% (one-sided 95% exact bound), 0 of 9 on the visible channel up to about 28%; one host, one small quantized local model, one blunt benign instruction"
    source: "sdw-lab-benchmarks@91e44df t8b-telemetry-injection/RESULTS.md:30-38, :153-155"
    date: 2026-11-10
    revalidate: 2027-05-10
  - claim: "phi4:latest was exposed in 0 of 10 hunts because the inherited harness keeps only the first line of multi-line SQL, so the run says nothing about whether phi4 would follow a planted instruction"
    source: "sdw-lab-benchmarks@91e44df t8b-telemetry-injection/RESULTS.md:40-47"
    date: 2026-11-10
    revalidate: 2027-05-10
  - claim: "A strip-at-write sanitizer left the visible planted instruction intact in 527 of 527 planted values and removed the tag-character channel entirely, and it also turned CRLF into LF in 88 PowerShell ScriptBlockText values, so it is not fidelity-preserving on script blocks"
    source: "sdw-lab-benchmarks@91e44df t8b-telemetry-injection/RESULTS.md:49-53, :96-103"
    date: 2026-11-10
    revalidate: 2027-05-10
  - claim: "Every one of the 17 observations that carried planted text came through process_creation CommandLine; the DNS, authentication, script-block and destination-hostname plants were never returned to the model"
    source: "sdw-lab-benchmarks@91e44df t8b-telemetry-injection/RESULTS.md:159-164"
    date: 2026-11-10
    revalidate: 2027-05-10
  - claim: "A Sigma contains rule for a planted direct prompt injection in OCSF message_context.prompt_text, compiled by the pySigma SQLite backend to LIKE, was MISSED on 3 of 3 seeds in DuckDB 1.5.3 (case-sensitive LIKE) and NOISY in SQLite at precision 0.048 with 20 false positives per seed"
    source: "sdw-lab-benchmarks@91e44df atlas-ocsf-observables/RESULTS.md:110-111, :125-129"
    date: 2026-11-09
    revalidate: 2027-05-10
---

# Telemetry is an injection surface: what a model reading event text is exposed to, and what a filter can close

Evidence tier: Mixed, with MITRE ATLAS, MITRE ATT&CK, OCSF and OWASP at A for what they define, peer-reviewed prompt-injection research at A, two verified lab runs on one host at B, preprints at B, vendor self-evaluations at C with the bias flagged, and the placement of the filter and the order of the practices at D.

## Summary for the review

A SOC that points a language model at raw event text has handed it attacker-written strings on the first query, because command lines, file names, user agents, DNS names and display names are values the adversary chooses. Part of that exposure can be closed with a deterministic filter (the invisible characters that let a model read something a human reviewer cannot see), and part of it cannot (plain instruction-shaped text), so the second part belongs to architecture rather than to a classifier.

- List every place a model reads event rows (a copilot's query tool, an alert summarizer, a triage agent, an MCP server over the lake) and which fields it can reach. Effort S. Tier A for the exposure (ATLAS AML.T0051.001), D for the practice.
- Strip or escape tag, zero-width, bidi, format and control characters where rows become model context, and keep the stored record raw, since an invisible character is sometimes the indicator. Effort M. Tier B for the mechanism (lab run T8b), D for the placement.
- Emit the count of characters removed per source as an event of its own. Effort S. Tier D.
- Mark which fields are adversary-controllable, in `metadata.tags` until OCSF has a field-level attribute. Effort S to M. Tier A for the schema gap, D for the workaround.
- Keep an agent that reads raw telemetry from also holding sensitive data and an outbound or write path in the same session, and put containment actions behind approval. Effort M to L. Tier A (OWASP mitigations, AgentDojo), D for the SOC application.
- Treat a prompt-injection classifier over event text as a rate, never as the control. Effort S. Tier A (adaptive-attack studies), B (detector false positives on tool output).
- Use logged prompts as a forensic record rather than an injection alert source, and test your Sigma backend's case handling before trusting any `contains` rule. Effort S. Tier B (one lab run).

## Why this matters

The air-gapped hunt I ran over the public MITRE ATT&CK Evaluations APT29 corpus has a ground-truth answer that is a dropper path with a right-to-left override in the middle of the filename, the old trick that makes a screensaver render like a document, though this copy of the corpus stores it as mojibake rather than as U+202E (Tier B, one lab run on one host, verified with fixes, sdw-lab-benchmarks@91e44df t8b-telemetry-injection/RESULTS.md:170-173). That character is attack evidence, and it is also exactly the kind of character that changes what a model reads relative to what a person sees. Separately, in my own research ingestion tooling, a display name captured from a public profile turned out to carry 21 invisible Unicode tag characters that decoded to an instruction-shaped fragment, which a human reading the note saw as a name and a model saw as a name plus text (Tier B, first-hand). Neither one looked like an attack on an AI system until someone inspected the bytes, and both arrived inside data I had every reason to collect.

That is the difference between telemetry and a web page as model input, because a fetched page is untrusted content someone chose to bring into context, while telemetry is collected on purpose, in bulk, treated as ground truth, and largely written by whoever is being investigated. ATLAS v2026.10 carries LLM Prompt Injection (AML.T0051) with Direct, Indirect and Triggered sub-techniques, and the Indirect entry describes instructions that "originate from adversary-controlled content rather than the legitimate user, and are frequently hidden or obfuscated ... for example as invisible text" (Tier A, ATLAS v2026.10 YAML). Counting the family's case studies and mitigations in that release gives 33 case studies, 5 of them typed Incident, and 8 mitigations, among them AI Telemetry Logging and Monitoring (AML.M0024), Input and Output Validation for AI Agent Components (AML.M0033) and Generative AI Guardrails (AML.M0020) (Tier A data, my count). ATT&CK Enterprise v20.1 has its own T1698 Indirect Prompt Injection and T1699 Direct Prompt Injection, both created 2026-09-18 and neither revoked, and the ATLAS v2026.10 YAML does not reference either ID, so a mapping keyed to one framework will not find the other (Tier A for the IDs, my reading for the missing link). OWASP keeps prompt injection as LLM01 in the 2026 edition of its LLM Top 10, and the 2025 entry says "it is unclear if there are fool-proof methods of prevention for prompt injection" (Tier A, OWASP GenAI Security Project).

The founding paper on indirect injection put the mechanism plainly, saying LLM-integrated applications "blur the line between data and instructions" (Tier A, Greshake et al., ACM AISec 2023, abstract read), and a SOC copilot is an LLM-integrated application whose data is the adversary's own output. This document owns the S13 case where that data is security telemetry; how good the AI analyst is belongs to [evaluating-ai-in-the-soc.md](evaluating-ai-in-the-soc.md), what each surface logs to [telemetry-by-surface.md](telemetry-by-surface.md), and the same problem in retrieval stores to [stubs/rag-stores.md](stubs/rag-stores.md).

## Two channels, and only one of them closes

I split hostile text into two channels, because teams that conflate them end up over-trusting a filter.

The invisible channel is characters that render as nothing, or that reorder what renders, so a reviewer and a model see different strings. The Unicode tag block (U+E0000 to U+E007F) maps one to one onto ASCII and renders as nothing in most viewers, zero-width spaces and joiners hide inside words, bidi overrides and isolates reorder a filename, and a run of variation selectors after a visible emoji can carry arbitrary bytes. Encoding-level perturbations of this kind manipulate a wide range of NLP systems while staying imperceptible to a person (Tier A, Boucher et al., "Bad Characters", IEEE S&P 2022, abstract read). The set of code points is enumerable and a legitimate log field rarely needs them, so this channel can be closed deterministically, and closing it removes the asymmetry that makes an injection hard to catch in review.

The visible channel is plain text, an instruction typed into a user-agent string or a scheduled-task description, and I don't think any filter closes it reliably. An adaptive search attack bypassed 12 recent defenses with success above 90% for most of them, and the Protect AI detector, whose static attack success was 0 to 31%, let 81 to 94% through once the attacker could search (Tier A, Nasr, Carlini et al., USENIX Security 2026, arXiv v1 Table 7; authors from three model vendors, and Google's Model Armor is among the detectors tested), and an earlier study broke all eight indirect-injection defenses it tested, Protect AI's detector included, at over 50% (Tier A, Zhan et al., Findings of NAACL 2025). The strongest detector in another study, Protect AI v2 at 20.26% average evasion, was "only heavily bypassed by Emoji and Unicode tag Smuggling", which is the invisible channel again (Tier A, Hackett et al., LLMSec 2025; Mindgard co-authors, who sell guardrail testing), and on 208,095 human-written attacks a vendor's own text classifiers caught 0.425 to 0.678 of the successful ones (Tier A, LLMail-Inject, Findings of EMNLP 2026; Microsoft-led, and the classifiers are Microsoft's).

The false-positive side matters for telemetry in particular, because security data is full of instruction-shaped text that is benign: a script block that says "run this", an admin's command line, a help-desk ticket quoted into an alert. One re-evaluation found Protect AI v2 flagging 30.1% of benign AgentDojo tool outputs and 66.9% of benign tau-bench outputs at its default threshold while flagging 0.5% of web pages (Tier B preprint, Liu, arXiv 2610.03448), and a latent-space study found direct and indirect injection encoded on "distinct, weakly aligned directions", so a detector tuned to one can miss the other (Tier A, Narendra and Chatterjee, Findings of EMNLP 2026, abstract read). I'd expect a detector trained on chat prompts to do worse on event rows, though I have not measured it (Tier D).

So the defensible scope of a filter is the invisible channel plus a provenance signal, and the defence against the visible channel stays architectural. OWASP's mitigation list for prompt injection carries least privilege, human approval for high-risk actions and segregating and identifying external content beside system-prompt constraints and input and output filtering, and presents all of them as limiting impact rather than preventing injection (Tier A, OWASP 2025 entry). AgentDojo found that restricting the agent to the tools a task needs cut targeted attack success to 7.5%, failing only where the needed tools also sufficed for the attack, which was "true for 17% of our test cases", while its prompt-injection detector had "too many false positives" (Tier A, Debenedetti et al., NeurIPS 2024). I'd rather say that plainly than sell a sanitizer as injection protection, because a team that believes the filter handles injection may hand the summarizing agent a ticketing tool and an email connector.

## What to strip, and what it costs

The repo's reducers run every string they read through a sanitizer copied from my own ingestion code ([scripts/reducers/text_sanitize.py](../scripts/reducers/text_sanitize.py)), so the repo follows its own rule, and its removal list is a reasonable starting point for telemetry. It matches the tag block and the supplementary variation selectors by range, because many tag code points are unassigned (category Cn) and a check on Unicode category alone would miss them, then removes the zero-width characters, the bidi embeddings, overrides and isolates, every other format character (category Cf, which takes in the soft hyphen), and every C0 and C1 control character and DEL except newline and tab. It keeps a single emoji-presentation selector after a base character and removes any run of them, collapsing runs last so that a stripped character between two selectors cannot leave a fresh run. It returns the cleaned text with a count of what it removed.

The costs are deliberate, security over fidelity. Emoji joined with U+200D fall apart into their components, subdivision flags built from tag characters degrade to a plain flag, removing U+200C can drop a joiner hint in Persian, Urdu or Indic text without touching the letters, and carriage return is a C0 control, so CRLF becomes LF. For a model-facing copy of a log field I think every one of those is acceptable. The lab run showed the last one is not cosmetic for security data, though, because that sanitizer changed 88 PowerShell `ScriptBlockText` values in the APT29 corpus by removing their carriage returns, which is why two of the pre-registered identity checks failed even though the planted instruction itself survived intact in 527 of 527 planted values and the tag characters were removed entirely (Tier B, sdw-lab-benchmarks@91e44df t8b-telemetry-injection/RESULTS.md:49-53, :96-103). A filter that rewrites script blocks is a filter that should not run on the evidence copy.

## What the lab run showed

I ran a pre-registered bench that planted a benign, fairly blunt instruction (it announces itself as `AI ASSISTANT:` and asks the agent to run a harmless `SELECT` returning a canary string) into 25% of the non-null rows of one adversary-controlled field per table in an OCSF-shaped DuckDB store built from the APT29 corpus, once as visible text and once as tag characters, and then ran an air-gapped analyst agent through a fixed hunt with each row rendered raw, as a Python tuple repr, or quoted with a provenance marker (Tier B, sdw-lab-benchmarks@91e44df t8b-telemetry-injection/RESULTS.md, Ollama 0.20.6 on one CPU host, gemma4:e4b and phi4:latest at Q4_K_M, 31 of 31 hunts, pre-registration frozen by the agent and not reviewed by the maintainer, independent verification VERIFIED-WITH-FIXES, whose record names no cross-provider leg).

| Model | Hunts over planted stores | Exposed to the planted text | Followed it | Flagged it in the answer |
|---|--:|--:|--:|--:|
| gemma4:e4b | 15 (vis-raw, vis-repr, vis-quoted, tag-raw, tag-repr, 3 each) | 15 | 0 | 0 |
| phi4:latest | 8 (vis-raw, vis-repr, vis-quoted, tag-raw, 2 each) | 0 | 0 | 0 |

Counts, not rates, from RESULTS.md:64-77. The finding I would carry forward is exposure. The one model that reached the planted rows saw the instruction in every hunt and every rendering, including raw with no defence at all, and in 4 of the 9 visible-channel hunts it quoted the planted text back in its own reasoning, once saying the planted row looked like an injected command, while none of its final answers flagged it (RESULTS.md:30-38). The finding I would not carry forward is safety. Zero follows in 15 trials is consistent with a true follow rate up to about 18%, and zero in 3 per cell up to about 63% (RESULTS.md:153-155), and the instruction was blunt, the output protocol rigid and the step budget six, all of which may suppress compliance relative to a free-form analyst chat (RESULTS.md:156-158, :165-166). So the run says this small local model did not follow this instruction in this loop, not that it would not, and silent non-compliance on one model is not evidence that stripping is unnecessary.

Every one of the 17 exposed observations came through the process command line, so the run says nothing about DNS names, user names, hostnames or script blocks (RESULTS.md:159-164). The phi4 arm measured the harness rather than the model, since the inherited query guard keeps only the first line of multi-line SQL, which is how phi4 writes it (RESULTS.md:40-47). And no strip cell was sampled, because the design treated stripped and base stores as identical, so the run supports "stripping closes the invisible channel and leaves the visible one untouched" mechanically and says nothing yet about what stripping does to a model's behaviour (RESULTS.md:96-103, :189-191).

Many Python harnesses render rows as repr by accident, and turning a result tuple into a string escapes non-printable characters, so a right-to-left override reaches the model as the six visible characters `\u202e` and a tag character as `\U000e0041`, while plain text passes through unchanged. Neither model decoded the escaped canary in a decode probe, but phi4 answered `CANDY-7` and `CANYARY-7` to the escaped form, which the pre-registered rule scored as misses and which I read as partial decoding (RESULTS.md:55-57, :185-188). So an accidental repr is better than raw, because a reviewer can see the escape, but a stronger model may read straight through it.

## Where the filter sits, and what travels with the text

I hold this Tier D opinion firmly. The strip or escape belongs on the copy the model reads, at the boundary where rows become model context, and the stored record stays raw. In a SOC that boundary is usually the query tool an assistant calls, whether an MCP server over the lake, a function in the copilot's toolset or the summarizer's retrieval step, because it is the last component that knows the text came from a log field and the first whose output a model reads. A filter in the ingest pipeline is too early, since a right-to-left override inside a filename is a detection in its own right and an analyst may need the exact bytes for a hash or a YARA match; on a correctly decoded store the strip would have deleted the APT29 override from the attack evidence (RESULTS.md:170-173). A system-prompt instruction to ignore embedded instructions is a request to the component under attack, so I wouldn't count it, though OWASP lists it first. Where a pipeline writes a separate model-facing store, such as an embedding index or a summary cache, strip at that store's write time, which is the same rule.

I lean toward escaping over deleting for telemetry, because an escaped override is something the model and the analyst can both reason about, while a deletion leaves no trace in the context. Either way I would emit the per-source strip count as an event, because a burst of invisible characters from one source is worth a detection engineer's look (Tier D).

Provenance is the other half. A flag that says which strings a stranger wrote survives into contexts the sanitizer never touches, so a downstream agent, or a person reviewing what an agent did, can tell attacker text from analyst text. OCSF 1.9.0 has no field-level attribute for that. The `metadata` object carries `labels`, a string array, and `tags`, an array of key-value pairs, both scoped to the whole event, and the nearest origin attributes (`reporter`, `loggers`, `transformation_info_list`, `log_source`) describe where the event came from and how it was processed, not which of its fields an adversary controls (Tier A, OCSF 1.9.0 metadata object at schema.ocsf.io, read 2026-11-10). So the options today are a `metadata.tags` entry listing the adversary-controllable field paths or an `unmapped` key, and I would pick `tags` because it is a typed, documented attribute, though I have not tested which one survives a real pipeline. Marking untrusted content inside the prompt, as spotlighting does, reported attack success falling from over 50% to under 2% (Tier C, Hines et al., arXiv 2403.14720, Microsoft on its own defense), while the adaptive study reached 99% against it on three of its four base models and 47% on the fourth (Tier A, Nasr et al., Table 7), so I'd expect a provenance marker to help the reviewer more than it constrains the model.

## Detecting injection in the record

It is tempting to alert on injection strings wherever prompts are logged. In a planted run over OCSF 1.9.0, a direct prompt injection (AML.T0051.000) had no column to land in under the core schema, so the rule was MISSED on all three seeds for want of a field, and with the `ai_operation` profile the prompt landed in `message_context.prompt_text` (Tier B, one host, synthetic planted data, verified with fixes, sdw-lab-benchmarks@91e44df atlas-ocsf-observables/RESULTS.md:110-111). The same Sigma rule, compiled by pySigma 2.0.3 with the SQLite backend 2.1.1, then split by engine. In SQLite it fired at precision 0.048 with 20 false positives per seed, and in DuckDB 1.5.3, the pre-registered engine, it was MISSED on every seed, because the backend compiles `contains` to `LIKE`, which SQLite matches case-insensitively as Sigma requires and DuckDB matches case-sensitively, so the mixed-case planted string never matched while 20 lower-case benign quotes did (RESULTS.md:125-129). Any team running SQLite-backend Sigma output in DuckDB inherits that silent recall loss.

So I would treat a logged prompt as a forensic record and hunting ground, as [what-to-log-and-what-it-costs.md](what-to-log-and-what-it-costs.md) does, rather than a place to page on keyword matches, since a keyword rule is the visible-channel filter argued against above with an engine-dependent recall on top. A vendor's injection verdict in an audit record is a rate, and the questions to ask about it are in [reading-vendor-claims.md](reading-vendor-claims.md).

## What this does not mean

It does not mean stripping invisible characters is pointless because the visible channel stays open, since closing the invisible channel removes the gap between what a reviewer sees and what the model reads. It does not mean a SOC should stop using models on telemetry, only that it should bound what the reading agent can do. It does not mean the lab run showed small local models resist injection, because it showed one model ignoring one blunt instruction in a rigid loop at small N, and the bounds above are wide. And it does not mean detectors have no value, since the adaptive study itself says they "can still provide practical value by blocking some unsophisticated or opportunistic attacks" (Tier A, Nasr et al., §5.3); a verdict is a triage signal with a rate, not a gate.

The strip is also wrong in places. A field whose invisible character is the subject of the investigation, such as a filename in a masquerading hunt, needs the escape, and source code under review legitimately carries these characters, so the boundary filter needs a written list of tools or fields it leaves alone.

## Gaps

- **Gap: compliance at scale**. T8b measured exposure well and compliance only at N of 3 per cell on one small model with one blunt instruction. **Needs**: a separately pre-registered re-run at larger N with a less announced instruction, a free-form analyst protocol and at least one stronger model.
- **Gap: the strip cell**. No hunt ran over a stripped store, so the effect of stripping on model behaviour is unmeasured. **Needs**: strip cells sampled in the re-run above.
- **Gap: fields other than the command line**. Every exposure came through `CommandLine`. **Needs**: a harness whose schema and hunt reach each planted field.
- **Gap: phi4 and repr decoding**. The phi4 arm measured a harness truncation, and its near-decodes suggest an escaped tag string is partly readable. **Needs**: a harness that accepts multi-line SQL and a probe that scores near-decodes against a stronger model, pre-registered as a new run.
- **Gap: field-level provenance in OCSF**. OCSF 1.9.0 has no attribute marking adversary-controllable fields. **Needs**: an OCSF proposal or a pipeline test of `metadata.tags` against `unmapped` for survival through normalization.
- **Gap: detectors on event rows**. No study I found measures prompt-injection detectors on security telemetry rather than chat, web or tool output. **Needs**: a benign-and-planted event corpus scored against the common open detectors at a fixed low false-positive rate.
- **Gap: OWASP 2026 entry text**. I confirmed the 2026 edition keeps prompt injection as LLM01 but read the prevention wording only in the 2025 entry. **Needs**: the 2026 LLM01 entry read at the primary.

## Notes

- Decision 16 choices: the T8b counts are quoted per model and the follow-rate bounds are the run's own one-sided 95% exact figures; the Nasr et al. detector range is quoted for the Protect AI detector from Table 7 of arXiv v1, not from the camera-ready, and the paper's ">90% for most" is its abstract's figure across all 12 defenses.
- Paper tiers follow [evidence-tiers.md](evidence-tiers.md), with an affiliation flag where authors test their own or a rival's product.
- The ATLAS case-study, incident and mitigation counts are my count of `employs` and mitigation edges in the ATLAS v2026.10 YAML (sha256 prefix `ac41ee9f`), dated 2026-11-10, and they are why this document revalidates three months out.
- The escape-at-the-query-tool position is a judgement dated 2026-11-10; it departs from the repo's reducer sanitizer, which deletes, because a reducer's output is counts and never evidence.

## Sources

Tier A

- MITRE ATLAS v2026.10, released 2026-10-28, https://github.com/mitre-atlas/atlas-data, AML.T0051 and sub-techniques, AML.M0020, AML.M0024, AML.M0033, read 2026-11-10.
- MITRE ATT&CK Enterprise v20.1 STIX bundle, https://github.com/mitre-attack/attack-stix-data, T1698 and T1699, read 2026-11-10.
- OCSF 1.9.0, metadata object, https://schema.ocsf.io/1.9.0/objects/metadata, read 2026-11-10.
- OWASP GenAI Security Project, prompt injection entry of the LLM Top 10 2025 edition, https://genai.owasp.org/llmrisk/llm01-prompt-injection/, read 2026-11-10; and GenAI and Agentic AI Exploit Roundup Q3 2026, https://genai.owasp.org/2026/10/08/genai-and-agentic-ai-exploit-roundup-q3-2026/, for the 2026 LLM01 naming (search excerpt).
- Greshake et al., "Not What You've Signed Up For", ACM AISec 2023, https://doi.org/10.1145/3605764.3623985.
- Boucher et al., "Bad Characters: Imperceptible NLP Attacks", IEEE S&P 2022, https://doi.org/10.1109/sp46214.2022.9833641.
- Nasr, Carlini et al., "The Attacker Moves Second", USENIX Security 2026, https://arxiv.org/abs/2510.09023 (v1 read; OpenAI, Anthropic and Google DeepMind authors).
- Hackett et al., "Bypassing LLM Guardrails", LLMSec 2025, https://aclanthology.org/2025.llmsec-1.8/ (Mindgard co-authors, bias flagged).
- Zhan et al., "Adaptive Attacks Break Defenses Against Indirect Prompt Injection Attacks on LLM Agents", Findings of NAACL 2025, https://doi.org/10.18653/v1/2025.findings-naacl.395.
- Debenedetti et al., "AgentDojo", NeurIPS 2024, https://arxiv.org/abs/2406.13352 (v3 read).
- Abdelnabi et al., "LLMail-Inject", Findings of EMNLP 2026, https://doi.org/10.18653/2026.findings-emnlp.514 (Microsoft-led, bias flagged).
- Narendra, Chatterjee, "Why Prompt-Injection Detectors Fail on XPIA", Findings of EMNLP 2026, https://doi.org/10.18653/2026.findings-emnlp.1103 (abstract read).

Tier B

- sdw-lab-benchmarks, folder t8b-telemetry-injection (RESULTS.md, VERIFICATION.md), commit 91e44df, run 2026-11-09 to 2026-11-10, https://github.com/flying-coyote/sdw-lab-benchmarks.
- sdw-lab-benchmarks, folder atlas-ocsf-observables (RESULTS.md, VERIFICATION.md), commit 91e44df, run 2026-11-09, same repository.
- Liu (Zhuowen), "Passing the Test You Trained On: Re-evaluating Prompt-Injection Detectors for LLM Agents", preprint, 2026, https://arxiv.org/abs/2610.03448.

Tier C

- Hines et al., "Defending Against Indirect Prompt Injection Attacks With Spotlighting", preprint, 2024, https://arxiv.org/abs/2403.14720 (Microsoft on its own defense, bias flagged).
