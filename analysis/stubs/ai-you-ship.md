---
evidence-tier: Mixed
convergence: single-source
applies-to-signals: [output-handling-unreviewed, pre-release-eval-absent, abuse-monitoring-absent]
surfaces: [S8]
pins:
  - "OWASP Top 10 for LLM Applications 2026"
  - "NIST AI 600-1 2024-07"
  - "EU AI Act consolidated CELEX-02024R1689-20260727"
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-03-03
status: EMERGING
---

# AI the organization ships (S8 as provider): declared gap

Evidence tier: Mixed, A for what the three standards prescribe and where the AI Act reaches, D for the reading that this repo's evidence stops at the consumer side of S8 and for every judgement about what to do first.

## Summary for the review

This repo studied S8 as the place where an organization consumes a model API, and it has not studied the case where the organization wraps that API in a feature and ships it to its own customers, so for the three signals that route here the review should send the reader to the standards and say plainly that the repo carries no measured evidence of its own. The standards are specific enough to act on while that gap stays open.

1. If `output-handling-unreviewed` is set, review every place a shipped feature's model output reaches another system or a person (a rendered page, a query, a shell, a downstream API, an email) against LLM10:2026 Improper Output Handling in the OWASP Top 10 for LLM Applications 2026 edition, and treat the output as untrusted input at each of those places, which is the zero-trust stance that entry's prevention list opens with. Effort M. Tier A for the risk category.
2. If `pre-release-eval-absent` is set, put a security and misuse evaluation in front of each release, including model-version changes the provider makes underneath you, using NIST AI 600-1's red-teaming and adversarial-testing actions (MS-2.7-007, MS-4.2-001) as the checklist. Effort M to L. Tier A.
3. If `abuse-monitoring-absent` is set, stand up post-deployment monitoring and an incident record for the feature along the lines of NIST AI 600-1 MG-4.1-002 and MG-4.3-001 to -003, with per-customer usage and spend as the first signal, since the OWASP list carries resource consumption as its own entry (LLM06:2026 Unbounded Consumption). Effort M. Tier A for the actions, D for the choice of first signal.
4. Where the feature is placed on the EU market, check two AI Act questions with counsel: whether Article 50 transparency and output-marking duties apply (they reach providers of systems that interact with people or generate content, with 2 December 2026 as the compliance date for generative systems already on the market), and whether the feature is high-risk, which brings testing, cybersecurity, post-market monitoring and serious-incident duties. Effort S to ask, L if high-risk. Tier A. This is not legal advice.

## Why this matters

When a product team builds a customer-facing feature on a model API, the organization stops being only a consumer of that API and becomes, to its own customers, the provider of an AI system, and the risks change direction. The consumer reading in [`surface-ownability.md`](../surface-ownability.md) puts S8 in the band where the organization owns little beyond identity, the gateway and the exported record, which is right for internal use, but a shipped feature adds the application's own input and output handling and its public endpoint to what the organization owns, and those are the components the three signals ask about. A public AI feature is also an internet-reachable surface with its own abuse patterns: resource consumption billed to the organization, attempts to extract or replicate the feature's behaviour through its outputs, and misuse of the feature against third parties. I think silence here would be read as a clean result, which is why the family has signals and this stub rather than no row at all.

## What the standards carry

The OWASP Top 10 for LLM Applications 2026 edition names LLM10:2026 Improper Output Handling and LLM06:2026 Unbounded Consumption as entries in their own right, the second covering cost abuse and model cloning through excessive inference as well as service disruption (Tier A for the categories, read 2026-11-10 from the published PDF), and the repo points at the list rather than explaining it, per `CONTRIBUTING.md`.

NIST AI 600-1, the Generative AI Profile of the AI RMF (July 2024), carries suggested actions that map onto two of the three signals with little interpretation (Tier A, read 2026-11-10 from the published PDF):

- MS-2.7-007, AI red-teaming to assess resilience against abuse that facilitates attacks on other systems, GAI attacks such as prompt injection, and ML attacks such as model extraction and sponge examples.
- MS-4.2-001, adversarial testing at a regular cadence to map misuse scenarios and unintended outputs.
- MG-4.1-002, organizational processes for post-deployment monitoring of GAI systems, particularly for confabulation, CBRN or cyber risks.
- MG-4.3-001 to -003, after-action assessments for GAI incidents, recording errors and near-misses, and reporting incidents where law requires it.

The profile is thinner on output handling as a software-integration problem. The nearest action, MG-3.1-004, is about outputs that reproduce training data, so for `output-handling-unreviewed` the OWASP entry is the standard to read and 600-1 is context rather than a checklist (Tier D for that reading).

The EU AI Act reaches a shipped feature in two different ways, and the difference decides how much applies (Tier A, consolidated text CELEX 02024R1689-20260727):

- Article 50(1) requires providers to design systems that interact directly with natural persons so those people are informed they are dealing with an AI system, unless that is obvious, and Article 50(2) requires providers of systems generating synthetic audio, image, video or text to mark outputs in a machine-readable, detectable way. Article 111(4) gives generative systems placed on the market before 2 August 2026 until 2 December 2026 to comply with Article 50(2).
- If the feature is high-risk, the provider duties follow: testing under Article 9(6) and 9(8), resilience against data poisoning, model poisoning, adversarial examples and confidentiality attacks under Article 15(5), a post-market monitoring system under Article 72, and serious-incident reporting within the Article 73 deadlines. Most customer-facing chat or summarization features will not be high-risk, but a feature used in, say, credit or hiring decisions may be, and that is a question for counsel rather than for this repo.

## What this does not mean

It does not mean the repo considers shipped AI features low-risk because it routes them to a stub. The routing priority for `output-handling-unreviewed` is PROBLEM for a reason, since output that reaches a renderer or an interpreter unvalidated is a familiar injection class with a model in front of it. It also does not mean the consumer-side documents are irrelevant, because a shipped feature still calls the model API through the organization's own keys and gateway, and the gateway and identity guidance applies to those calls as it does to internal use.

## Gaps

- **Gap: provider-side S8 evidence**. The repo has no measured or researched evidence on securing AI features an organization ships to its customers: no output-handling test, no pre-release evaluation study and no abuse-monitoring signal study, and its S8 reading is the consumer one. **Needs**: a desk study mapping the three signals to the OWASP 2026 entries, the NIST AI 600-1 action IDs above and AI Act Articles 9, 15(5), 50, 72 and 73, plus a lab bench that runs a fixed corpus of injection payloads through a sample customer-facing feature into three sinks (an HTML renderer, a SQL query, a downstream tool call) and counts how many reach each sink with and without output validation, re-run on each model-version change so it doubles as the pre-release evaluation the second signal asks about.

## Notes

- Convergence is `single-source`. The standards route in `CONTRIBUTING.md` probably applies, since OWASP and NIST AI 600-1 both prescribe these practices and the AI Act requires some of them of high-risk providers, but the route also needs an independent implementation, and this repo has not verified one, so the stub does not claim it.
- The OWASP entries are cited by their 2026 IDs, read from the 2026 edition PDF on 2026-11-10. The IDs moved between editions (Improper Output Handling and Unbounded Consumption carried different numbers in 2025), so controls keyed to the 2025 IDs need re-mapping, and the edition-mapping gap is carried in [`revalidation-and-pins.md`](../revalidation-and-pins.md).
- `revalidate-by` is just under four months out because the Article 50(2) compliance date for systems already on the market passes on 2026-12-02 inside that window, and the AI Act has been amended once already in 2026, so the Article 50 and high-risk lines are the ones to re-read first.
- The choice of per-customer usage and spend as the first abuse signal is my judgement (Tier D, 2026-11-10), drawn from the consumer-side reading that a cost anomaly on a single key or identity is a better signal of stolen-credential cost abuse than a volume anomaly across a fleet, which is itself a Tier D comparison and has not been tested on the provider side.

## Sources

Tier A:

- OWASP GenAI Security Project, OWASP Top 10 for LLM Applications 2026, resource page dated 2026-08-03, https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/ (PDF, read 2026-11-10): LLM06:2026 Unbounded Consumption (Description), LLM10:2026 Improper Output Handling (Prevention item 1).
- NIST AI 600-1, Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile, July 2024, https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf, read 2026-11-10 (actions MS-2.7-007, MS-4.2-001, MG-3.1-004, MG-4.1-002, MG-4.3-001 to -003).
- Regulation (EU) 2024/1689 (AI Act) as amended by Regulation (EU) 2026/1744, consolidated text CELEX 02024R1689-20260727, https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02024R1689-20260727, read 2026-11-10 (Articles 9, 15, 50, 72, 73, 111).
