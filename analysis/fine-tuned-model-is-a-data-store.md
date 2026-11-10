---
evidence-tier: Mixed
convergence: single-source
applies-to-signals: [fine-tuned-models, training-record-absent]
surfaces: [S11]
pins:
  - "MITRE ATLAS v2026.10"
  - "CoSAI secure-ai-tooling 622605a1"
  - "OCSF 1.9.0"
  - "SmolLM2-135M 93efa2f097d58c2a74874c7e644dbc9b0cee75a2 (lab run T6, LoRA r 16, CPU)"
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-03-10
status: EMERGING
measurement-claims:
  - claim: "In one seed of a CPU LoRA fine-tune (r 16, 3 epochs, 59,257 synthetic tokens) of SmolLM2-135M, no planted 4-digit secret was returned at any insertion count from 0 to 50: 0 of 1,510 extraction attempts per checkpoint (greedy plus three sampled settings, 10 canaries) and 0 of 200 blind samples, on the base model and after each of three epochs; seeds 8 and 9 and the full fine-tune arm did not run"
    source: "sdw-lab-benchmarks@91e44df t6-finetune-memorization/RESULTS.md:16-34, :72-85"
    date: 2026-11-10
    revalidate: 2027-03-10
  - claim: "The strongest exposure rise was canary c09 at 50 insertions, from 1.73 bits (rank 3,011 of 10,000) on the base model to 4.89 bits (rank 337) after epoch 3, against a 13.29-bit ceiling; the other 50-insertion canary ended at 3.00 bits, below its base-model 3.08, and controls (the n = 0 canaries and the untouched base model) ranged 0.74 to 3.96 bits, with the base model itself topping out at 3.57"
    source: "sdw-lab-benchmarks@91e44df t6-finetune-memorization/RESULTS.md:21-26, :42-60, :106-108"
    date: 2026-11-10
    revalidate: 2027-03-10
  - claim: "Held-out perplexity fell from 43.93 on the base model to 2.48 after epoch 3, so the null on the secrets is not a fine-tune that failed to train; each saved fp32 r 16 adapter directory was 19,599,208 bytes"
    source: "sdw-lab-benchmarks@91e44df t6-finetune-memorization/RESULTS.md:26-28, :87-93"
    date: 2026-11-10
    revalidate: 2027-03-10
  - claim: "The pre-registered predictions that exposure rises strictly with insertion count and that both 50-insertion canaries are greedy-extracted in every seed were both wrong as stated on the one seed that ran"
    source: "sdw-lab-benchmarks@91e44df t6-finetune-memorization/RESULTS.md:95-114"
    date: 2026-11-10
    revalidate: 2027-03-10
---

# A fine-tuned model is a data store: memorization, lineage and the tests before release

Evidence tier: Mixed, with peer-reviewed memorization, membership-inference and safety-regression research at A, preprints and one verified single-seed lab run at B, a first-party incident disclosure at B, and the classification rule, the lineage record's shape and the order of the practices at D.

## Summary for the review

Fine-tuning on organization data copies some of that data into the weights, in a form that DLP, row-level access, retention schedules and deletion requests cannot read, so a fine-tuned model inherits the classification of its most sensitive training record and should be stored, tested and logged as a data store as well as a model. How much it retains depends on the task, the method, the duplication in the set and the training budget, which is why the answer for a given model comes from testing it rather than from arguing about the method.

- Classify each fine-tuned model, its adapters, checkpoints and training logs at the class of its training data, and store and grant access to them on that basis. Effort S. Tier A for memorization (Carlini et al. 2021, Nasr et al. 2025), D for the rule.
- Keep a lineage record per training run (weights digest, base-model and adapter digests, dataset version and the row identifiers that went in), and route erasure requests and incident scoping through it. Effort M. Tier D for the record, A for why it is needed (unlearning reached only about a 40% reduction in Szep et al. 2026).
- Minimize and deduplicate the set before training and strip identifiers the task does not need. Effort M. Tier A (Lee et al. 2022, Kandpal et al. 2022), which shows reduction and not removal.
- Test every model before release with planted canaries, extraction and membership inference, a success criterion looser than exact match and more than one training seed. Effort M. Tier A for the method, B for lab run T6.
- Re-run the safety evaluation on every derivative, since the base model's evaluation does not transfer. Effort M. Tier A (Qi et al. 2024, Betley et al. 2025).
- Turn on access logging for the dataset and checkpoint buckets and alert on reads by any principal other than the training and serving identities. Effort S. Tier B for the logs, D for the detection value.

## Why this matters

On the thirteen-surface map this repo uses, S11 is one of three surfaces where the organization owns every CoSAI component it instantiates, from the training data through tuning, the model, storage and usually the registry, which may be rented (see [surface-ownability.md](surface-ownability.md)), so there is no provider abuse monitoring, safety filter or retention policy to lean on unless the organization builds one. In CoSAI's terms the data moves from `componentTrainingData` through `componentModelTrainingTuning` into `componentTheModel` and then sits in `componentModelStorage` and `componentModelRegistry`, and the risks that attach include `riskSensitiveDataDisclosure` (which CoSAI maps to AML.T0024 at ATLAS 5.0.1, Exfiltration via AI Inference API in v2026.10), `riskInferredSensitiveData` with no ATLAS mapping, `riskUnauthorizedTrainingData` and `riskModelExfiltration`, which on this surface is also exfiltration of part of a dataset (Tier A or B, CoSAI risk map at 622605a1, an OASIS working draft).

ATLAS v2026.10 gives the privacy side its own parent, AML.T0137 Training Data Information from AI Models, with Infer Membership (.000) and Invert AI Model (.002) at Feasible and Extract Memorized Data (.003) at Demonstrated (Tier A, MITRE ATLAS v2026.10). The two routing rows that send a review here sit at Medium because the exposure is serious and hard to reverse while the reach is usually small, since many organizations that fine-tune hold only a handful of models served to a limited set of internal users.

## What the literature says about memorization

The extraction record is strong and has held up on re-reading. Carlini et al. extracted 604 unique memorized training examples out of 1,800 candidates from GPT-2 with query access only, including sequences present in a single training document (Tier A, USENIX Security 2021), and then showed that memorization grows log-linearly with model capacity, duplication and prompt context length, with GPT-J 6B memorizing at least 1% of the Pile (Tier A, ICLR 2023). Nasr et al. showed that alignment does not remove it, recovering thousands of training examples from ChatGPT (Tier A, ICLR 2025), and the often-quoted figure of training data emitted at 150 times the normal rate belongs to the earlier arXiv version (2311.17035) rather than the published abstract.

For fine-tuning the answer depends on the task and the method. Zeng et al. found memorization high for summarization and dialogue and low for classification, reading comprehension and translation (Tier A, ACL 2024), so I treat memorization as settled for planning when the fine-tune is generative over the organization's own text and as overstated for a classifier head. Mireshghallah et al. put 50 copies of a canary into GPT-2 fine-tunes over 20 epochs and found head-only fine-tuning leaked most while full fine-tuning and small bottleneck adapters leaked least, though a larger adapter beat head-only on canary exposure in two of three datasets while sitting below full fine-tuning on membership-inference recall, which they measured on Wikipedia only, so the ranking depends on the metric (Tier A, EMNLP 2022). Those were Pfeiffer adapters, not LoRA, which is what most enterprise fine-tunes use.

On LoRA the evidence leans towards less memorization than full fine-tuning without settling it. Szep et al. found that PII appearing only in the inputs of QLoRA fine-tunes was still memorized, and that how often a piece of PII repeated explained under 24% of the variance in whether it was extracted (Tier A, EACL 2026). Preprints report that pre-training's duplication and scale trends do not carry over to LoRA (Tier B, Wang and Li, arXiv 2506.20856) and that adapters store about 2 to 3.4 bits per trainable parameter, less than full fine-tuning, while still storing "most of the bits of secrets planted in the training data" (Tier B, Tan et al., arXiv 2607.21351), and one cuts the other way, with LoRA fine-tunes reaching 0.775 membership AUC partly because the public base model is a free reference (Tier B, LoRA-Leak, arXiv 2507.18302).

Duplication matters because enterprise sets often carry it. For pre-training and full training it is well evidenced, since a sequence present 10 times is regenerated about 1,000 times more often than one present once (Tier A, Kandpal, Wallace and Raffel, ICML 2022) and deduplication cut memorized output from over 1% to 0.1% (Tier A, Lee et al., ACL 2022), but for adapter fine-tunes the Szep result makes it contested. In the environments I have seen, a fine-tuning set is usually small, often carries templated near-duplicates such as ticket forms, signatures and boilerplate clauses, and is trained for several epochs, which is a Tier D premise that no work I fetched has measured.

Membership inference is where fine-tuning differs most from pre-training. Duan et al. found membership attacks barely beat random guessing on Pile-trained models from 160M to 12B parameters (Tier A, COLM 2024), and Hayes et al. found strong attacks stay under AUC 0.7 on pre-trained models in practical settings, with many per-sample verdicts flipping across training seeds (Tier A, NeurIPS 2025). Against fine-tuned models, Fu et al. raised membership AUC from 0.7 to 0.9 (Tier A, NeurIPS 2024) and Kandpal et al. showed that inferring whether any of a user's data was in a fine-tune works, at times near-perfectly, from black-box access (Tier A, EMNLP 2024). The contrast is cleanest at the single-record level, since aggregated inference can also work on pre-training data (Tier A, Puerto et al., Findings of NAACL 2025), which matters for a regulator asking whether a given customer's records were used.

The result closest to a security team's own data is Kapelinski and Kreutz, who fine-tuned 1B to 3B models with LoRA for three epochs on CSIRT vulnerability records carrying planted IP addresses, hostnames, MAC addresses and asset names, ten copies each, and measured mean exposure of 3.49 to 4.98 bits on a scale from about 1 bit at chance to 6.66 at the ceiling; differential privacy at ε 8 and 2 added no significant reduction beyond fewer optimizer updates, while HMAC pseudonymization cut exposure of the original identifiers by 40% to 61% (Tier A, BRACIS 2026, lightly cited so far).

## What lab run T6 adds, and what it does not

Lab run T6 asked at what insertion count a short secret becomes retrievable from a light LoRA fine-tune (Tier B, sdw-lab-benchmarks@91e44df t6-finetune-memorization/RESULTS.md:16-34, one host under heavy contention, synthetic corpus, pre-registration frozen by an agent and not owner-reviewed, verdict VERIFIED-WITH-FIXES with every headline number reproduced on an independent re-run slice). Using the Secret Sharer method (Tier A, Carlini et al., USENIX Security 2019), it planted ten canaries with random 4-digit secrets at insertion counts from 0 to 50 into a 59,257-token corpus, fine-tuned SmolLM2-135M with LoRA at rank 16 for three epochs on CPU, and ranked each secret among all 10,000 candidates on the base model and after each epoch.

No planted secret came back. Across four checkpoints, 0 of 1,510 extraction attempts per checkpoint hit under greedy decoding and three sampling settings, and 0 of 200 blind samples matched (RESULTS.md:72-85). The strongest rise was one 50-insertion canary moving from 1.73 bits (rank 3,011) to 4.89 bits (rank 337), roughly the top 3.4% and far from the 13.29-bit ceiling, while the other ended at 3.00 bits, just under its base-model value, and controls (the n = 0 canaries and the untouched base model) ranged 0.74 to 3.96 bits, with the base model itself topping out at 3.57 on its digit prior (RESULTS.md:21-26, :42-60, :106-108). Held-out perplexity fell from 43.93 to 2.48, so the run did learn the domain (RESULTS.md:26-28), and the pre-registered predictions that exposure rises strictly with insertion count and that both 50-insertion canaries are greedy-extracted were wrong as stated (RESULTS.md:95-114).

The fair reading is narrow. Fifty copies of a short secret in about 4% of the notes were not retrievable in one seed of a light CPU LoRA run, which says nothing about heavier fine-tunes, full-parameter training (the arm that did not run), longer secrets, or seed variance, since seeds 8 and 9 were cut by the stop rule (RESULTS.md:126-157, :182-200), and it is not evidence against the Carlini and Nasr results, which come from far larger models, far more training and real data. An exploratory check run after the results were seen, which scores no hypothesis, put one canary's real host-note text in front of it and saw exposure rise from 1.83 to 6.41 bits, so the pre-registered prefix may understate what a realistic prompt recovers, though the same check showed a context-copying artifact that would need its own control (RESULTS.md:159-180).

Two things in T6 bear on practice. Each saved adapter directory was 19.6 MB in fp32 (RESULTS.md:87-93), a separately distributable file carrying whatever the fine-tune retained, and nothing I read tests extraction from an adapter on its own. And the spread in the literature, from a translation model memorizing a canary fully at four insertions to a production email model reaching only 10 bits at 10,000 in the Secret Sharer paper, is why a given model's leakage has to be tested rather than predicted from its method.

## The pipeline is a supply chain, and the derivative is a new model

The fine-tuning pipeline pulls a base model, datasets, training libraries and often adapters, and runs with access to the organization's most sensitive data. CoSAI's `riskAdapterPEFTInjection` covers trojaned adapters merged at runtime, citing two preprints (Tier B, LoRATK arXiv 2403.00108, PETA arXiv 2310.00648), with no ATLAS mapping in CoSAI and AML.T0018.000 Poison AI Model as the closest v2026.10 fit. Training-data poisoning (AML.T0020, and AML.T0115.000 for poisoned public datasets) plausibly needs fewer records to move a small fine-tune than a pre-training run, which is my inference and unmeasured on enterprise fine-tunes (Tier D). The processing pipeline is a target too, since Hugging Face's July 2026 disclosure describes an intrusion driven by an autonomous agent system that began with a malicious dataset abusing two code-execution paths in dataset processing and reached a limited set of internal datasets and several service credentials (Tier B, first-party disclosure, read 2026-11-10).

Fine-tuning also changes safety behavior. Qi et al. removed GPT-3.5 Turbo's guardrails by fine-tuning on 10 adversarial examples for under $0.20, and found that benign, commonly used datasets also degraded safety alignment, to a lesser extent (Tier A, ICLR 2024). Betley et al. found that fine-tuning on the narrow task of writing insecure code produced broadly misaligned behavior on unrelated prompts, and that it could be made to appear only behind a trigger (Tier A, ICML 2025). So the base model's evaluation says little about the derivative, and a managed platform (S7) may keep its filters in front of a fine-tune while a self-hosted copy of the same weights has nothing in front of it. The managed interface is a privacy surface as well, since Chen et al. recovered PII the base model had "forgotten" at more than 10 times the baseline through provider fine-tuning APIs (Tier A, ACM CCS 2024).

## The controls, mapped

| Control | What it does here | ATLAS v2026.10 | CoSAI 622605a1 | Evidence |
|---|---|---|---|---|
| Classify the model as its data | Weights, adapters, checkpoints and training logs take the training set's class, storage and access | AML.M0005, AML.M0019 | `controlModelAndDataAccessControls` | D for the rule; A for the reason |
| Lineage record | Weights digest to dataset version and rows, per run | AML.M0025 | `controlTrainingDataManagement` | D |
| Minimize and deduplicate | Remove duplicates and identifiers the task does not need | AML.M0007 | `controlTrainingDataSanitization` | A; reduces, does not remove |
| Pseudonymize identifiers | Keyed hashing of hostnames, IPs and similar before training | AML.M0007 | `controlTrainingDataSanitization` | A, one study |
| Privacy-preserving training | DP fine-tuning where the data warrants it | AML.M0041 | `controlModelPrivacyEnhancingTechnologies` | A, with the unit caveat |
| Release testing | Canaries, extraction and membership inference, several seeds | AML.M0035 | `controlAdversarialTrainingAndTesting` | A for the method |
| Derivative safety evaluation | Evaluate the fine-tuned model as well as the base | AML.M0008 | `controlAdversarialTrainingAndTesting` | A |

Differential privacy carries a real guarantee at a modest utility cost for larger models, with RoBERTa-Large at 87.8% on MNLI at ε 6.7 against 90.2% without it (Tier A, Yu et al., Journal of Privacy and Confidentiality 2024), but the bound covers the unit DP is applied to, so PII repeated across records or across one user's records can still leak, and sentence-level DP still leaked about 3% of PII sequences (Tier A, Lukas et al., IEEE S&P 2023). With Szep et al. finding it unstable to train and the CSIRT study finding it added nothing beyond fewer optimizer updates, I would keep DP for regulated data where the team can afford the tuning, and make pseudonymization plus deduplication the default.

Release testing has its own qualifiers, because a filter that perfectly blocks verbatim regurgitation still leaks through lightly modified prompts (Tier A, Ippolito et al., INLG 2023) and per-sample membership verdicts flip with training randomness (Tier A, Hayes et al.), so a one-seed exact-match test is weaker than it looks.

## Lineage, erasure and the record that is missing

The second routing key exists because without a link from each model to its rows, erasure and incident scoping stop at the weights. A deletion request under a statute such as GDPR Article 17 cannot reach a model that memorized the record unless someone knows which models the record went into, and even then post-hoc remedies only partly work, since the best unlearning and preference-alignment methods in one benchmark reached about a 40% reduction in direct PII memorization (Tier A, Szep et al.), which leaves retraining without the record as the only complete remedy I know of. The legal side is in [prompt-capture-and-the-law.md](prompt-capture-and-the-law.md). The same gap shows up in an incident, where "which models were trained on the compromised bucket" has an answer only if the training job recorded what it read.

The record I would ask each training run to produce (Tier D, 2026-11-10) carries the output's weights digest, the digests of the base model and every merged adapter, the dataset version and row identifiers, the job identity with start and end times, and the classification assigned. The weights digest is the join key, and OCSF 1.9.0's `ai_model` object has four attributes (`ai_provider`, `name`, `version`, `uid`) with no weights digest or base-model link, so a same-name swap looks identical in an event (Tier B, sdw-lab-benchmarks@91e44df d3fend-ocsf-ai-alignment/RESULTS.md:22-26, a schema read rather than a measurement). Until a release adds it, the digest belongs in `unmapped` or the organization's registry, keyed so a serving log's model version resolves back to a training run.

The surrounding telemetry is mostly the organization's own: training-job history, object-store access logs on dataset and checkpoint buckets, registry promotion events and inference logs. The useful detections are ordinary ones aimed at a new asset, such as a checkpoint read by a principal that is neither the training nor the serving identity. A burst of near-identical prompts against a fine-tuned endpoint is sometimes proposed as an extraction signal, and since I found no work measuring what extraction traffic looks like in serving logs, I hold that one at Tier D.

## What this does not mean

It does not mean every fine-tune leaks enough to matter. Classifier fine-tunes and small adapters sit at the low end of the measurements, and T6 shows a light fine-tune can learn a domain thoroughly without making a short secret retrievable, so classification is a planning default that a test result can relax for a specific model. Nor is renting automatically safer, because a managed fine-tuning API moves storage and serving controls to the provider while the data still leaves and the Janus result shows the interface can surface base-model PII; whether to own S11 at all is argued in [decision-sequence.md](decision-sequence.md). The memorization evidence comes mostly from public text and research models, with one peer-reviewed run on security records, and several Tier A works come from Google, Google DeepMind and Microsoft staff, which leaves their tier alone but is worth knowing where a paper recommends a defense those labs ship. Retrieval exposure where the same data sits in a vector store is out of scope (see [stubs/rag-stores.md](stubs/rag-stores.md)).

## Gaps

- **Gap: seed variance and the full fine-tune arm (G6)**. T6 ran one seed of three and no full-parameter arm. **Needs**: T6 seeds 8 and 9 and the full fine-tune arm, on an idle host.
- **Gap: templated near-duplicates**. No fetched work measures memorization under template repetition with varying secrets. **Needs**: a pre-registered templated arm against a deduplicated one-epoch control, scored by canary recovery and membership AUC.
- **Gap: decoding settings**. T6 compared four settings but had no hits to order. **Needs**: the same comparison on a run where some canary is extracted.
- **Gap: adapters as separate artifacts**. Nothing tests extraction from an adapter file on its own. **Needs**: extraction and membership tests against a LoRA adapter loaded onto a fresh copy of its base.
- **Gap: security-operations data**. No peer-reviewed study covers SOC tickets, incident notes or detection logs as fine-tune data. **Needs**: a canary study on a realistic synthetic SOC-ticket corpus.
- **Gap: extraction in serving logs**. Nothing measures what extraction or membership traffic looks like in inference logs. **Needs**: a lab capture of extraction and benign traffic scored by a candidate detection.
- **Gap: enterprise poisoning threshold**. How many poisoned records move a small fine-tune is unmeasured. **Needs**: a defensive bench varying poisoned-record counts.
- **Gap: weights digest and lineage**. OCSF 1.9.0 `ai_model` has no weights digest, and no work tests whether an organization can trace records to models. **Needs**: an OCSF release or producer extension carrying the digest, and a registry feature recording dataset rows per run, verified against a captured record.

## Notes

- Decision 16 choices: T6 is quoted per canary rather than as medians by insertion count, because with one seed each median covers two cells; the Mireshghallah ranking is given with its metric because exposure and membership recall order the adapters differently.
- The T6 in-context check is a lead only, as RESULTS.md labels it, and backs no action. Betley et al. is cited for direction and trigger-conditionality, not its headline percentage, which was not re-read; the Qi figures are from the arXiv abstract read 2026-11-10.
- No vendor default-state table is carried because no managed fine-tuning platform's documentation was read for this doc; a dated row on where a managed platform records training-job history and dataset reads is the first addition I would make.
- Judgements dated 2026-11-10: the classification rule, the lineage record's fields, the order of the summary actions, and pseudonymization plus deduplication over DP as the default.

## Sources

Tier A

- MITRE ATLAS v2026.10 release data, AML.T0137 and sub-techniques, AML.T0024, AML.T0018.000, AML.T0020, AML.T0115.000, AML.M0005, M0007, M0008, M0019, M0025, M0035, M0041, from the v2026.10 release data in the mitre-atlas/atlas-data distribution, https://github.com/mitre-atlas/atlas-data, read 2026-11-10.
- CoSAI secure-ai-tooling risk map at 622605a1 (components, risks, controls), https://github.com/cosai-oasis/secure-ai-tooling/tree/622605a13fafaa2784acbdbe3f8d23ee22da4be7/risk-map/yaml, read 2026-11-10 (an OASIS working draft, so B is also defensible).
- Carlini et al., "The Secret Sharer", USENIX Security 2019, https://arxiv.org/abs/1802.08232.
- Carlini et al., "Extracting Training Data from Large Language Models", USENIX Security 2021, https://doi.org/10.48550/arxiv.2012.07805.
- Carlini et al., "Quantifying Memorization Across Neural Language Models", ICLR 2023, https://doi.org/10.48550/arxiv.2202.07646.
- Nasr, Rando, Carlini et al., "Scalable Extraction of Training Data from Aligned, Production Language Models", ICLR 2025, https://openreview.net/forum?id=vjel3nWP2a (150x figure in arXiv 2311.17035 only).
- Mireshghallah et al., "An Empirical Analysis of Memorization in Fine-tuned Autoregressive Language Models", EMNLP 2022, https://doi.org/10.18653/v1/2022.emnlp-main.119.
- Zeng et al., "Exploring Memorization in Fine-tuned Language Models", ACL 2024, https://doi.org/10.18653/v1/2024.acl-long.216.
- Szep et al., "Unintended Memorization of Sensitive Information in Fine-Tuned Language Models", EACL 2026, https://doi.org/10.18653/v1/2026.eacl-long.304.
- Kapelinski, Kreutz, "Decomposing Memorization Reduction in Privacy-Preserving Fine-Tuning of SLMs for CSIRTs", BRACIS 2026, https://doi.org/10.1007/978-3-032-39898-7_43.
- Lee et al., "Deduplicating Training Data Makes Language Models Better", ACL 2022, https://doi.org/10.18653/v1/2022.acl-long.577.
- Kandpal, Wallace, Raffel, "Deduplicating Training Data Mitigates Privacy Risks in Language Models", ICML 2022, https://arxiv.org/abs/2202.06539.
- Duan et al., "Do Membership Inference Attacks Work on Large Language Models?", COLM 2024, https://arxiv.org/abs/2402.07841.
- Hayes et al., "Exploring the limits of strong membership inference attacks on large language models", NeurIPS 2025, https://arxiv.org/abs/2505.18773.
- Fu et al., "Membership Inference Attacks against Fine-tuned Large Language Models via Self-prompt Calibration", NeurIPS 2024, https://doi.org/10.52202/079017-4290.
- Kandpal et al., "User Inference Attacks on Large Language Models", EMNLP 2024, https://doi.org/10.18653/v1/2024.emnlp-main.1014.
- Puerto et al., "Scaling Up Membership Inference", Findings of NAACL 2025, https://doi.org/10.18653/v1/2025.findings-naacl.234.
- Ippolito et al., "Preventing Generation of Verbatim Memorization in Language Models Gives a False Sense of Privacy", INLG 2023, https://doi.org/10.18653/v1/2023.inlg-main.3.
- Lukas et al., "Analyzing Leakage of Personally Identifiable Information in Language Models", IEEE S&P 2023, https://doi.org/10.1109/sp46215.2023.10179300.
- Yu et al., "Differentially Private Fine-tuning of Language Models", Journal of Privacy and Confidentiality 2024, https://doi.org/10.29012/jpc.880.
- Chen et al., "The Janus Interface", ACM CCS 2024, https://doi.org/10.1145/3658644.3690325.
- Qi et al., "Fine-tuning Aligned Language Models Compromises Safety, Even When Users Do Not Intend To!", ICLR 2024, https://arxiv.org/abs/2310.03693.
- Betley et al., "Emergent Misalignment: Narrow Finetuning Can Produce Broadly Misaligned LLMs", ICML 2025, https://arxiv.org/abs/2502.17424.
- Regulation (EU) 2016/679 (GDPR), Article 17, https://eur-lex.europa.eu/eli/reg/2016/679/oj.

Tier B

- sdw-lab-benchmarks, folders t6-finetune-memorization (RESULTS.md, VERIFICATION.md, PREREGISTRATION.md) and d3fend-ocsf-ai-alignment (RESULTS.md), commit 91e44df, https://github.com/flying-coyote/sdw-lab-benchmarks.
- Hugging Face, "Security incident disclosure, July 2026", https://huggingface.co/blog/security-incident-july-2026, read 2026-11-10.
- Wang, Li, "Leaner Training, Lower Leakage", preprint, 2025, https://arxiv.org/abs/2506.20856.
- Tan, Du, Feng, "How Much Can a LoRA Adapter Memorize?", preprint, 2026, https://arxiv.org/abs/2607.21351.
- Ran et al., "LoRA-Leak", preprint, 2025, https://arxiv.org/abs/2507.18302.
- LoRATK, https://arxiv.org/abs/2403.00108, and PETA, https://arxiv.org/abs/2310.00648, preprints cited by CoSAI `riskAdapterPEFTInjection`.
