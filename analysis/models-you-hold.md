---
evidence-tier: Mixed
convergence: single-source
applies-to-signals: [profile-own-heavy, model-artifacts-held, model-store-unscanned, pickle-formats-present, inference-runtime-default-bind]
surfaces: [S9, S10, S11]
pins:
  - "MITRE ATLAS v2026.10"
  - "CoSAI secure-ai-tooling 622605a1"
  - "CISA KEV catalog 2026.11.09"
  - "OCSF 1.9.0"
  - "Syft 1.55.0, Grype 0.121.0, Trivy 0.76.0, ai-bom 3.6.0, cyclonedx-bom 8.0.1 and Ollama 0.20.6 (lab run R4)"
  - "modelscan 0.8.8, picklescan 1.0.5 and fickling 0.1.12 (lab run T5)"
  - "Ollama, llama.cpp server (master), vLLM (latest) and LM Studio documentation as read 2026-11-10"
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-02-10
status: EMERGING
measurement-claims:
  - claim: "Pointed at six artifacts (a named GGUF file, the same weights in Ollama's store, a safetensors directory, an npm and a pip MCP server, a VS Code extension), Syft, Trivy, ai-bom and cyclonedx-bom found 4 of 6 in some form and 1 of 6 typed as an AI artifact under the pre-registered name match (3 of 6 found without the non-pre-registered Trivy rootfs mode); a lenient path rule added at scoring raises that to 5 of 6 and 2 of 6; no tool saw the Ollama store and no model component carried a usable PURL or CPE; one host, one fixture set, 3 identical runs"
    source: "sdw-lab-benchmarks@91e44df ai-artifact-sbom/RESULTS.md:31-47,62-68,99-102"
    date: 2026-11-09
    revalidate: 2027-02-10
  - claim: "Default scans surfaced none of three same-name, same-version swaps (npm server code, pip server code, extension publisher); Syft surfaced a one-byte flip in GGUF tensor data only through the file sha256 it records, and lost the GGUF entirely when it was renamed weights.bin"
    source: "sdw-lab-benchmarks@91e44df ai-artifact-sbom/RESULTS.md:104-123"
    date: 2026-11-09
    revalidate: 2027-02-10
  - claim: "On the 57 unsafe files in picklescan's bypass set, modelscan 0.8.8 flagged 3 (it scanned 48 and returned clean with no errors, and skipped 6), fickling 0.1.12 flagged 55, and picklescan 1.0.5 flagged 56 single-file and 55 in directory mode, picklescan's figures being circular because the files are its own suite"
    source: "sdw-lab-benchmarks@91e44df t5-model-artifact-scanning/RESULTS.md:13-18,53-60,162-163"
    date: 2026-11-09
    revalidate: 2027-02-10
  - claim: "At the pre-registered threshold fickling flagged 11 of 18 benign files, including all six real models in five formats; cut at its two overtly malicious severities (a post-freeze derived view) it held 78 of 96 unsafe and 0 of 18 benign; modelscan's 0 benign flags rests mostly on skipping 11 of the 18"
    source: "sdw-lab-benchmarks@91e44df t5-model-artifact-scanning/RESULTS.md:18-27,66-74,147-148"
    date: 2026-11-09
    revalidate: 2027-02-10
  - claim: "No output from modelscan, picklescan or fickling carried a content digest, PURL, CPE or artifact version across all three runs, so the scanner side and the SBOM side share no key beyond a file path; a nested zip was skipped by all three scanners for every anchor file"
    source: "sdw-lab-benchmarks@91e44df t5-model-artifact-scanning/RESULTS.md:22-23,103-105,122-123"
    date: 2026-11-09
    revalidate: 2027-02-10
  - claim: "CISA KEV catalogVersion 2026.11.09 (1,773 entries) holds no entry for Ollama, vLLM, NVIDIA Triton, TorchServe, llama.cpp, LM Studio, LMDeploy, PyTorch, Hugging Face Transformers or any NVIDIA product; the nearest are Ray CVE-2025-62593 (added 2026-08-17) and MLflow CVE-2026-64849 (added 2026-08-19)"
    source: "CISA KEV catalog JSON feed, catalogVersion 2026.11.09, dateReleased 2026-11-09T19:54Z, re-pulled 2026-11-10"
    date: 2026-11-10
    revalidate: 2027-02-10
---

# Models you hold: the artifact store, the loader and the runtime

Evidence tier: Mixed, with NVD CVE records, the CISA KEV catalogue, MITRE ATLAS v2026.10 and peer-reviewed backdoor research at A, two verified lab runs on one host and runtime project documentation of their own defaults at B, vendor research and exposure counts I could not re-read at C with the bias flagged, and the order of the practices at D.

## Summary for the review

An organization that holds model weights takes on the controls a hosted provider would otherwise run, and the first finding is that the tooling a security team already owns does not see the weights as AI: in lab run R4 one of six artifacts was typed as an AI artifact under the pre-registered match, no model got an identifier a vulnerability matcher can use, and the Ollama store was seen by no tool. So the work starts with an inventory keyed on a hash of the weights, then the format and loader rules, then the runtime's documented defaults, which leave authentication off in each of the three runtimes whose documentation states it.

- Inventory model files by hashing model directories and the Ollama blob store directly, recording a sha256, source and owner per file. Effort M. Tier B (R4, one host).
- Run a model-file scanner as a filter rather than an assurance, on versions past the published bypass fixes, joined to the inventory by your own hash, since no scanner output in lab run T5 carried one. Effort S. Tier B for T5, A for the bypass CVEs.
- Allow safetensors and GGUF from approved sources, block pickle checkpoints at the mirror or artifact repository, and keep PyTorch at 2.6.0 or later. Effort M. Tier A for the CVEs, D for the policy order.
- Pull models through a private registry or mirror so an acquisition carries a name, a hash and a requester. Effort L. Tier D.
- Check every self-hosted runtime against its documented default: nothing listening off loopback without authentication, vLLM behind a proxy that allowlists endpoints, llama.cpp with an API key and a restricted CORS origin. Effort S. Tier B.
- Detect unsanctioned local runtimes from acquisition, process, listener and file events existing tooling already emits. Effort M. Tier B for the event sources, D for the rule set.
- Patch serving hosts and the adjacent Ray and MLflow layers, the AI-adjacent entries closest to serving in KEV as of 2026-11-10. Effort S. Tier A.

## Why this matters

A team renting a model through an API gets the provider's abuse monitoring, safety layer, patching and request logs whether it looks at them or not. When the same team serves open weights from a workstation through Ollama or LM Studio (S10), from a data-centre box or cloud VM through vLLM or llama.cpp's server (S9), or produces its own weights by fine-tuning (S11), each of those jobs becomes the organization's or does not happen at all, which is why `profile-own-heavy` (selected by S9, S11 or S12) routes here alongside the rent-or-own sizing in [rent-or-own-sized-to-the-org.md](rent-or-own-sized-to-the-org.md), and S10 alone reaches it through the rows that surface enables.

Three things are held, and they fail differently. The artifact store is a set of large files whose provenance is asserted rather than attested, so the question is whether anyone knows which files exist and whether they changed. The loader is the code that turns those files into a model in memory, and several common formats let a file run code at that moment. The runtime is a network server that ships with authentication off in Ollama, llama.cpp and vLLM, and with the default unstated in LM Studio. This document covers all three for S9 and S10, and the artifact half of S11; what a fine-tuned model remembers about its training data, and the record that links a model to its rows, belong to [fine-tuned-model-is-a-data-store.md](fine-tuned-model-is-a-data-store.md).

## What the inventory tooling sees

Running the SBOM generator already in the pipeline over the model directories does not work today, and lab run R4 shows how. The lab pointed Syft, Grype, Trivy, Trusera's ai-bom and cyclonedx-bom (versions in the pins) at six artifacts: a TinyLlama GGUF file under its own name, the same weights inside Ollama's content-addressed store, an all-MiniLM-L6-v2 safetensors directory, an npm MCP server, a pip MCP server and a VS Code extension (Tier B, sdw-lab-benchmarks@91e44df ai-artifact-sbom/RESULTS.md:21-29, :54-61; one host, one fixture set, three identical runs, pre-registration frozen by the agent and not reviewed by the maintainer, verdict VERIFIED-WITH-FIXES). Under the pre-registered name match, four of the six were found by some tool and one, the named GGUF, was typed as an AI artifact; the headline figures of five of six and two of six depend on Trivy's `rootfs` mode and on a lenient path rule, neither of which was pre-registered (RESULTS.md:31-41, :65-68). The Ollama store was seen by no tool (RESULTS.md:43-44, :57).

The identifiers are the larger problem. No model component got a CPE, Syft's model components carry no PURL, and ai-bom's PURLs are `pkg:pypi/<filename>`, which puts a weights file in the PyPI namespace under whatever it happens to be called, so the advisory table for the model rows is a structural zero, not a measured one: there is nothing for a matcher to key on (RESULTS.md:33-36, :75-82, :99-102). The MCP servers fared better because they are ordinary packages, with a PURL and every listed advisory matched, though no tool marked either as an MCP server, and the two were chosen for having advisories, so this says nothing about MCP servers in general (RESULTS.md:41-43, :178-180).

What Syft did well is the shape I would build on. It recorded a file sha256 for the named GGUF, kept a renamed `.gguf` tied to the original through the name in the GGUF header and the hash, and surfaced a one-byte flip in the tensor data only through that hash; rename the same file `weights.bin` and Syft lost it, because its cataloger reads only `*.gguf` (RESULTS.md:109-123). No default scan surfaced a same-name, same-version swap of the MCP servers' code or the extension's publisher, which only a non-default whole-file hash diff against a known-good baseline showed (RESULTS.md:120-123, :134-144). So the first half of the answer to `model-store-unscanned` is a file-hash inventory of the places models live, with the model-file scanner below as the second half run against it, which for the local runtimes means `~/.ollama/models` on macOS and `/usr/share/ollama/.ollama/models` on Linux (Tier B, Ollama FAQ), the Hugging Face cache at `~/.cache/huggingface/hub` (Tier B, huggingface_hub cache guide) and whatever models directory LM Studio is set to, plus any file of a few hundred megabytes or more with a model extension. Ollama's manifests name each blob by digest, and a re-tag of the same weights showed up only there (RESULTS.md:142-144), so the manifests are worth collecting beside the blobs.

The event schema has the same gap one layer down. OCSF 1.9.0's `ai_model` object carries four attributes, `ai_provider`, `name`, `version` and `uid` (Tier A, OCSF schema `objects/ai_model.json` at tag v1.9.0), with no digest of the weights and no base-model link, so a swapped model that reuses a name looks identical in an event exactly as it does in an SBOM (Tier B, sdw-lab-benchmarks@91e44df d3fend-ocsf-ai-alignment/RESULTS.md:22-26, verdict VERIFIED-WITH-FIXES). Until a field exists, I would carry the sha256 in `uid` or `unmapped` and say so in the collection plan, since inventory and telemetry join only on a shared key.

## Formats that execute on load

I would treat serialization as a class rather than a list of bugs, because loading a model can mean running code. Python's pickle, still the container behind many PyTorch checkpoints, executes callables at deserialization, and Hugging Face describes its Hub scanner as ClamAV plus a pickle-import extractor with the disclaimer that it "is not 100% foolproof" (Tier B, Hugging Face Hub documentation, read 2026-11-10). The safer-loading defaults have their own record: CVE-2025-32434 was remote code execution in `torch.load` even with `weights_only=True`, in PyTorch 2.5.1 and earlier, fixed in 2.6.0 (Tier A, NVD, published 2025-04-18, CVSS 3.1 9.8 from NVD). Keras models could carry arbitrary code before 2.13 (CVE-2024-3660, published 2024-04-16), and GGUF carries a Jinja chat template in its metadata, which is how llama-cpp-python came to have a server-side template-injection flaw when loading a model (CVE-2024-34359, published 2024-05-14, CVSS 9.6 from the GitHub advisory) (Tier A, NVD). The loader in the runtime is attack surface too, since Ollama before 0.17.1 had a heap out-of-bounds read in its GGUF loader reachable through `/api/create` (CVE-2026-7482, published 2026-05-04, Tier A, NVD).

So the safer formats that `pickle-formats-present` asks about are safetensors, designed as a tensor-only container to remove code execution for weights, and GGUF from an approved source with a runtime that is patched against template and loader flaws (Tier B, the safetensors project's own description). Neither tells you which model a file holds, which is the R4 point again, and neither says anything about what the weights do. Behaviour planted in the weights is a separate problem: backdoors survive transfer learning (Gu et al., IEEE Access 2019) and a victim's own fine-tuning (Kurita et al., ACL 2020), and Goldwasser et al. (FOCS 2022) give an existence result, that under cryptographic hardness assumptions some backdoors can be planted which no computationally bounded observer can detect from input-output behaviour, all Tier A. I read the last as showing that no scanning or evaluation vendor can promise to catch every backdoor, so a pre-promotion evaluation of the exact weights is worth running and still cannot prove absence.

## What the model-file scanners catch

The scanners are the obvious control for pickle, and their bypass record is public: picklescan before 0.0.21 did not treat `pip` as an unsafe global (CVE-2025-1716, published 2025-02-26), and picklescan up to 0.0.30 passed a standard pickle given a PyTorch-style extension (CVE-2025-10155, published 2025-09-17) (Tier A, NVD). Lab run T5 measured three open scanners, at the newest versions outside the lab's two-week cooldown, against each other on 118 base files (96 unsafe, 18 benign, 4 junk) and 123 rename and container variants, three runs with no verdict flips (Tier B, sdw-lab-benchmarks@91e44df t5-model-artifact-scanning/RESULTS.md:42-49, :107-108; one contended host, pre-registration frozen by the agent and not maintainer-reviewed, harness edited after the freeze, verdict VERIFIED-WITH-FIXES).

| Arm | Unsafe flagged (of 96) | Bypass set flagged (of 57) | Benign flagged (of 18) | What the benign count rests on |
|---|---|---|---|---|
| modelscan 0.8.8 | 29 | 3 | 0 | Skipped 11 of 18 benign, including 5 of the 6 real models |
| picklescan 1.0.5, single file | 92 (circular) | 56 (circular) | 0 | Parses any bytes as a pickle, so a clean verdict on a GGUF is a file it did not meaningfully read |
| picklescan 1.0.5, directory | 91 (circular) | 55 (circular) | 0 | Skipped 7 benign |
| fickling 0.1.12, pre-registered threshold | 89 | 55 | 11 | Flagged all six real models in five formats |
| fickling, overtly malicious cut (post-freeze view) | 78 | not split | 0 | Derived after the freeze, labelled as such |

Cells from RESULTS.md:13-27, :53-74, :147-148. 109 of the 118 base fixtures come from picklescan's own suite, so its numbers are an install check rather than a detection rate, and the benign set holds 18 files, so the false positives are counts and never rates (RESULTS.md:162-164). The modelscan result matters most for a defender, I think, because it did not miss the bypass set by failing to open the files: it scanned 48 of the 57 and returned clean with no errors (RESULTS.md:15-18).

Containers and renames cut differently per tool. A zip whose member was renamed `.txt` defeated modelscan on 3 of 3 anchor files and fickling on 5 of 5, a nested zip was skipped by every scanner for every anchor, and fickling's zero defeats under rename and tar were not resilience, since it flagged 7 of 8 benign renames just as readily (RESULTS.md:80-101, :122). And no output from any of the three carried a content digest, PURL, CPE or artifact version, so the scanner verdict and the SBOM share no key beyond a file path, which a rename breaks (RESULTS.md:22-23, :103-105). Bottom line: on this host and fixture set, none of the three both looks inside the common model formats and gives a verdict that survives a rename, a tar or a nested zip, so I would run one as a filter at the mirror, record its verdict against my own sha256, and treat a clean result as "not known-bad" rather than "safe".

## Runtimes on their documented defaults

The runtimes whose documentation states a default are mostly safe on the network and open on authentication, which means exposure is one configuration change away, and `inference-runtime-default-bind` asks whether that change has been made without the matching control. Each row comes from the project's own documentation, which is the authority on its defaults (Tier B).

| Runtime | Default bind | Authentication as documented | What else is open | last-checked |
|---|---|---|---|---|
| Ollama | `127.0.0.1:11434`; `OLLAMA_HOST=0.0.0.0:11434` exposes it | "The local API at `http://localhost:11434` does not require authentication"; API keys apply to ollama.com | The same unauthenticated API includes model creation (`/api/create`, the path in CVE-2026-7482) | 2026-11-10 |
| llama.cpp server (master) | `--host` 127.0.0.1, `--port` 9931 (the README's Docker examples pass 8080) | `--api-key` default none; `/health` public | CORS reflects any `Origin` with credentials allowed by default; the README recommends an API key and a reverse proxy for public use | 2026-11-10 |
| vLLM (latest docs) | API server bind not stated on the security page; inter-node traffic "insecure by default"; PyTorch `TCPStore` listens on all interfaces | `--api-key` covers only the `/v1`, `/v2`, `/inference` and `/cohere` prefixes | `/invocations` serves the same inference unauthenticated, and `/update_weights`, `/metrics`, `/tokenize` and `/pause` are unauthenticated too | 2026-11-10 |
| LM Studio | Port is an integer setting and "Serve on Local Network" a switch; defaults not stated on the page | "Require Authentication" switch (token in the `Authorization` header); default not stated | MCP access switches, one requiring authentication | 2026-11-10 |

The vLLM row is the one I would put in front of a platform team, because an operator who sets `--api-key` will reasonably believe the inference endpoint is protected, while the project's own security page lists an unauthenticated path to the same inference functions on the same server, beside an endpoint that changes the weights. The guide's remedy is a reverse proxy that allowlists intended endpoints. The inference engines do have CVEs, for example a vLLM heap-address leak through the multimodal endpoint in 0.8.3 to before 0.14.1 (CVE-2026-22778, published 2026-02-02, Tier A, NVD), but an unauthenticated runtime needs none to be abused.

## Exposure and exploitation

Cisco Talos queried Shodan for Ollama banners and default ports, found 1,139 exposed servers, and found 214 of them, about 18.8%, actively hosting live models and responding to requests without authentication; the authors list the limits, including Shodan coverage and a bias toward default ports (Tier B, Cisco blog, 2025-09-01, read 2026-11-10). SentinelLABS and Censys reported a much larger longitudinal count, which I could not read at the primary and so do not repeat. Either way, the exposed population is a configuration choice layered on a runtime that ships without authentication.

The KEV catalogue points the same way. As of catalogVersion 2026.11.09 (1,773 entries, released 2026-11-09T19:54Z and still the current version when I re-pulled the feed on 2026-11-10), KEV holds no entry for Ollama, vLLM, NVIDIA Triton, TorchServe, llama.cpp, LM Studio, LMDeploy, PyTorch, Hugging Face Transformers or any NVIDIA product; the nearest are Ray (CVE-2025-62593, code injection, added 2026-08-17), a common distributed serving and training layer, and MLflow (CVE-2026-64849, server-side request forgery, added 2026-08-19), a model registry, while the remaining AI-adjacent entries are LiteLLM, Langflow and n8n, which [ai-apis-and-the-gateway.md](ai-apis-and-the-gateway.md) covers (Tier A, CISA KEV, re-pulled 2026-11-10). I would be careful with what that absence means, since KEV requires reliable evidence of exploitation and the inference-engine CVEs above exist; my reading is that the exploited 2026 surface sits in orchestration, gateways and the layers around serving rather than in the inference engines, and that the risk for a held runtime is exposure and stolen compute far more than an engine exploit (Tier D).

## Finding local models nobody approved

Once the weights are on disk, inference happens on loopback and nothing leaves the machine, so CASB, SSE and browser telemetry see at most the download. What remains visible is the acquisition, the process, the listener and the files, each an ordinary endpoint or network event (Tier B for the event sources, D for the rule set, and the discovery methods in [inventory-and-shadow-ai.md](inventory-and-shadow-ai.md) apply here too).

- Acquisition: DNS and TLS SNI for `registry.ollama.ai`, `huggingface.co` and the hub's download CDN hosts (take the current names from your own proxy logs, since they change), from Zeek `dns.log` and `ssl.log`, proxy logs or Sysmon event ID 22, landing in OCSF DNS Activity (4003) or Network Activity (4001). A multi-gigabyte download from those hosts is a strong signal on its own.
- Process: creation of `ollama`, `llama-server`, LM Studio's `lms` CLI or `llmster` daemon, or `python` with `vllm` in the command line, from Sysmon event ID 1 or EDR process telemetry, landing in OCSF Process Activity (1007).
- Listener: osquery `listening_ports` or EDR socket telemetry for 11434, 9931 and 8080, and the commonly seen 8000 and 1234 for vLLM and LM Studio (neither stated on the pages I read), with a high-severity variant whenever the bind address is not loopback.
- Files: creation of `.gguf`, `.safetensors`, `.pt`, `.pth`, `.bin` and `.pkl` files above a few hundred megabytes, and the store paths in the inventory section, from Sysmon event ID 11, landing in OCSF File System Activity (1001).

No AI-security product is required to find local models, only a decision to write the detections, though none of these events can say which model is running, so a sanctioned name with swapped weights passes all of them unless the file-hash inventory catches the change.

## Where the frameworks file this

ATLAS v2026.10 files the store under AML.T0010.003 Supply Chain Compromise: Model Repository and AML.T0115.001 Publish Poisoned AI Artifacts: Models, the loader under AML.T0011.000 User Execution: Unsafe AI Artifacts, behaviour in the weights under AML.T0043.004 Insert Backdoor Trigger, and the exposed runtime under AML.T0132 Misconfigured or Publicly Exposed AI Services, AML.T0040 AI Model Inference API Access and AML.T0034 Cost Harvesting, with AML.M0023 Maintain an AI Bill of Materials, AML.M0011 Restrict Library Loading and AML.M0019 Control Access to AI Models and Data in Production among the matching mitigations (Tier A, IDs and maturities read from the release file). AML.T0006.002 Scan for Exposed AI Infrastructure is rated Feasible while Talos publishes an internet-scale count of the exposure, which looks to me like more than Feasible by ATLAS's own definitions (Tier D until MITRE rules).

In the CoSAI risk map at commit 622605a1 the relevant risks are `riskModelSourceTampering` and `riskMaliciousLoaderDeserialization` on `componentModelServing` and `componentModelStorage` (Tier A), and two gaps look like easy upstream contributions: the loader risk carries no ATLAS mapping although AML.T0011.000 fits it, and `componentModelFrameworksAndCode`, where loader flaws live, is referenced by no control in `controls.yaml`.

## What this does not mean

It does not mean SBOM tooling is useless for AI, since in R4 it handled MCP servers as packages well, matched every listed advisory on the two servers chosen for having them, and kept a digest-bound identity for named GGUF and safetensors files, which is most of what the inventory needs once someone hashes the stores it skips. It does not rank the scanners, since the fixtures came mostly from picklescan's suite and fickling's breadth came with flags on every real model. It does not mean a loopback runtime is safe, since a browser page can reach a loopback listener that reflects any origin with credentials, so the llama.cpp row matters on a laptop too (my reasoning, Tier D). And it does not mean safetensors solves provenance, since a safe format holding the wrong weights passes every format check. The lab runs used one host and one version of each tool, so I would not generalize the counts beyond the shape of the finding.

## Gaps

- **Gap: benign corpus size**. T5's false positives rest on 18 benign files with 6 real models, so they are counts, not rates. **Needs**: a larger benign corpus of real models across formats, and unsafe fixtures from a source independent of all three scanners' suites.
- **Gap: untested formats and scanner modes**. TensorFlow SavedModel, Keras v3 and polyglot paths, `picklescan[7z]` and `--strict` were not run in T5. **Needs**: a follow-up run with TensorFlow and fickling's `torch` extra installed.
- **Gap: container-image scanning**. R4 scanned directories, never a container image. **Needs**: the R4 fixtures rebuilt as images and rescanned.
- **Gap: scanner and inventory join key**. No scanner output carries a digest or component identifier. **Needs**: a scanner release or documented wrapper that emits the sha256 of the scanned bytes, re-measured against R4's inventory.
- **Gap: runtime defaults not stated**. vLLM's security page does not state the API server's default bind, LM Studio's settings page states no switch defaults, and Triton was not read. **Needs**: a desk pass over each runtime's CLI reference or a fresh install, dated per row.
- **Gap: internet-scale exposure count**. The SentinelLABS and Censys longitudinal Ollama figures returned HTTP 429 at the primary on 2026-11-09 and 2026-11-10 and reached me only through secondary summaries. **Needs**: the primary read in full, with its method and window.
- **Gap: weights digest in the event schema**. OCSF 1.9.0 `ai_model` has no digest or base-model attribute. **Needs**: a field proposed or adopted upstream, or a documented `unmapped` convention measured for query cost.

## Notes

- 2026-11-10: lab citations use the master form `sdw-lab-benchmarks@91e44df`, where R4, R8 and T5 are merged (their RESULTS files last changed at `7301388`, `7301388` and `e0aaadc`); do not change them back to the pre-merge branch form some shipped docs still use.
- 2026-11-10: the KEV paragraph is a dated reading of catalogVersion 2026.11.09, re-pulled on 2026-11-10, and reopens when an inference engine is added, a trigger `revalidation-and-pins.md` lists.
- 2026-11-10: lab numbers were re-derived from the RESULTS files at 91e44df, CVEs from the NVD API, runtime rows from each project's page, ATLAS IDs from the v2026.10 release file and CoSAI statements from the YAML at 622605a1.
- 2026-11-10: the practice order, the scanner-as-filter reading and the KEV reading are my judgement (Tier D); `revalidate-by` is three months out because the document cites ATLAS IDs.

## Sources

Tier A

- CISA, Known Exploited Vulnerabilities catalog, JSON feed, catalogVersion 2026.11.09, https://www.cisa.gov/known-exploited-vulnerabilities-catalog, re-pulled 2026-11-10.
- NVD records for CVE-2025-32434, CVE-2025-1716, CVE-2025-10155, CVE-2024-3660, CVE-2024-34359, CVE-2026-7482 and CVE-2026-22778, https://nvd.nist.gov/vuln/detail/<CVE-ID>, read 2026-11-10.
- MITRE ATLAS v2026.10, https://github.com/mitre-atlas/atlas-data `dist/v6/ATLAS-2026.10.yaml`, read 2026-11-10.
- OCSF schema 1.9.0, `objects/ai_model.json`, https://github.com/ocsf/ocsf-schema/tree/v1.9.0.
- CoSAI secure-ai-tooling at commit 622605a1, `risk-map/yaml/{components,risks,controls}.yaml`, https://github.com/cosai-oasis/secure-ai-tooling, read 2026-11-10.
- Gu, Liu, Dolan-Gavitt and Garg, "BadNets", IEEE Access 2019, doi:10.1109/access.2019.2909068.
- Kurita, Michel and Neubig, "Weight Poisoning Attacks on Pretrained Models", ACL 2020, doi:10.18653/v1/2020.acl-main.249.
- Goldwasser, Kim, Vaikuntanathan and Zamir, "Planting Undetectable Backdoors in Machine Learning Models", FOCS 2022, doi:10.1109/focs54457.2022.00092.

Tier B, project and vendor documentation of what a feature does (read 2026-11-10 unless noted)

- Ollama FAQ, https://docs.ollama.com/faq, and API authentication, https://docs.ollama.com/api/authentication
- llama.cpp server README (master), https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md, lines 194-217, 396-410 and 481-483
- vLLM, Security, https://docs.vllm.ai/en/latest/usage/security.html
- LM Studio, Server Settings, https://lmstudio.ai/docs/developer/core/server/settings
- Hugging Face Hub, Pickle Scanning, https://huggingface.co/docs/hub/security-pickle
- safetensors README, https://github.com/huggingface/safetensors
- huggingface_hub, Manage the cache, https://huggingface.co/docs/huggingface_hub/guides/manage-cache

Tier B, first-party lab work and practitioner research

- sdw-lab-benchmarks@91e44df (master), `ai-artifact-sbom/` (R4), `t5-model-artifact-scanning/` (T5) and `d3fend-ocsf-ai-alignment/` (R8), RESULTS.md and VERIFICATION.md each, https://github.com/flying-coyote/sdw-lab-benchmarks; R4 and T5 on one host, R8 a desk analysis of pinned definitions, each pre-registration or method frozen by the agent and not reviewed by the maintainer, each verdict VERIFIED-WITH-FIXES.
- Tziakouris and Biasiotto, "Detecting Exposed LLM Servers: Shodan Case Study on Ollama", Cisco blog, 2025-09-01, https://blogs.cisco.com/security/detecting-exposed-llm-servers-shodan-case-study-on-ollama

Tier C, bias flagged

- SentinelLABS and Censys on exposed Ollama hosts, https://www.sentinelone.com/labs/silent-brothers-ollama-hosts-form-anonymous-ai-network-beyond-platform-guardrails/ (primary not read).
