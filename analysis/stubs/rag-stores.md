---
evidence-tier: Mixed
convergence: single-source
applies-to-signals: [rag-acl-propagation-unknown, ingestion-integrity-unreviewed, embeddings-outside-governance]
surfaces: [S12]
pins:
  - "CoSAI secure-ai-tooling 622605a1"
  - "OWASP Top 10 for LLM Applications 2026"
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-03-17
status: EMERGING
---

# RAG and vector stores (S12): declared gap

Evidence tier: Mixed, A for what the CoSAI risk map and the OWASP Top 10 for LLM Applications 2026 say, D for the ownership framing and for my reading of where CoSAI is silent, and no lab result behind any of it.

## Summary for the review

This repo has no researched document for retrieval pipelines and vector stores yet, so for S12 the review should send the reader to two standards that already describe the failure modes well, which are OWASP's LLM09:2026 Vector and Embedding Weaknesses, with LLM02:2026 and LLM01:2026 for the disclosure and injection consequences, and the CoSAI risk map's Retrieval/Vector Store Poisoning risk together with the controls it lists. What the repo cannot yet say is how often real deployments get these wrong or which store configurations make the safe choice the default, and that is the gap below.

Actions, each drawn from a standard rather than from a measurement in this repo:

1. Where source-document permissions do not demonstrably carry into retrieval (`rag-acl-propagation-unknown`), move the authorization decision into the index query, server-side and at chunk level, so nothing the user may not read is ever handed to the model. Effort M to L. Tier A for the practice (OWASP LLM09:2026 Prevention 1; LLM02:2026).
2. Where ingestion is unreviewed (`ingestion-integrity-unreviewed`), record provenance for every embedding (source, ingestion time, trust tier, pipeline version), keep external and internal content in separate indexes, and put human review in front of externally sourced content bound for sensitive indexes. Effort M. Tier A (CoSAI Retrieval and Vector System Integrity Management; OWASP LLM09:2026 Prevention 2 and 3).
3. Where embeddings sit outside the source data's retention and access policy (`embeddings-outside-governance`), treat the vector store and its backups as the same sensitivity tier as the documents, delete embeddings when their source is deleted and reconcile to prove it, and classify an embeddings-only leak as a source-data leak in incident playbooks. Effort S to M. Tier A (OWASP LLM09:2026 Prevention 5 and 6).

Each of these is single-source in this repo, which means adopting it is the reader's own risk acceptance even though the standards behind it are sound.

## Why this matters

S12 is one of the three surfaces on which the organization instantiates every component on the CoSAI map itself, usually bar a rented embedding model (Tier D, one author's reading; see `analysis/surface-ownability.md`), so it is also one of the few places where every control in this stub is the organization's own to apply and nobody else's to blame. OWASP frames the boundary plainly, saying that "[w]henever similarity search sits between a data source and the prompt, the embedding layer becomes part of the application's trust boundary" (Tier A, OWASP LLM09:2026, Description). The injection half of the problem is older than the vector-store half, since the founding indirect prompt injection paper showed that LLM-integrated applications "blur the line between data and instructions" when they process retrieved content (Tier A, Greshake et al., ACM AISec 2023).

The three signals that route here correspond to three different failures, and I think it helps to keep them apart because they land with different owners. ACL propagation is an access-control problem that data engineering usually holds, because the vector store is a copy of the organization's data with an access model of its own; ingestion integrity is a supply problem for whoever runs the ingest pipeline; and embedding governance is a retention and breach-classification problem for privacy and legal as much as for security.

## What the two standards say, signal by signal

Access control (`rag-acl-propagation-unknown`). OWASP's prevention guidance is to "[e]nforce tenant scoping inside the index query, not as a post-retrieval filter, and validate it server-side", adding that "[a] client-supplied scope is a suggestion, not a control" and that access control belongs at chunk level because "a mostly-public document can contain a confidential paragraph" (Tier A, OWASP LLM09:2026, Prevention 1). The disclosure entry gives the reason in one line, "Cosine similarity does not respect ACLs. Authorize before retrieval, because post-generation filtering cannot undo a chunk already supplied to the model" (Tier A, OWASP LLM02:2026, Common Examples item 3). OWASP also describes leakage that happens even when every document is tagged correctly, because similarity search runs over the whole index before the application filters, so result counts, score distributions and timing reveal what exists (Tier A, OWASP LLM09:2026, Common Examples 1 and 5). On the CoSAI side, the only control at this commit that names the RAG content component explicitly is Agent Permissions (four more apply to every component), which asks for least privilege that adapts to "the specific user query and trusted contextual information" (Tier A, CoSAI `controlAgentPluginPermissions`); I read nothing in the map that addresses source-ACL propagation into a vector store directly (Tier D, my reading of 37 controls).

Ingestion integrity (`ingestion-integrity-unreviewed`). CoSAI's Retrieval/Vector Store Poisoning risk says it "is introduced during data ingestion and indexing processes when malicious content is added to knowledge bases, vector stores, or retrieval corpora without proper validation and sanitization", and lists five controls against it, of which Retrieval and Vector System Integrity Management is the one written for this surface, asking for "provenance tracking, cryptographic signing, deduplication, embedding anomaly detection, and index integrity checks", placed on the data sources, data storage and data filtering and processing components (Tier A, CoSAI `riskRetrievalVectorStorePoisoning` and `controlRetrievalAndVectorSystemIntegrity`). OWASP splits the same ground differently, which matters when mapping internal controls, because poisoning that works through embedding geometry, retrieval jamming with a single blocker document, and threshold attacks on semantic caches sit in LLM09:2026, while attacker instructions that ride in a retrieved passage are prompt injection under LLM01:2026, whose Scenario 4 is RAG repository poisoning (Tier A, OWASP LLM09:2026 Description and Common Examples 3, 4 and 6; LLM01:2026 Scenario 4). OWASP's mitigations here are normalizing content before embedding, provenance per embedding, segregation of mixed-trust content into separate indexes rather than tags on a shared one, and anomaly detection at ingest and retrieval (Tier A, OWASP LLM09:2026, Prevention 2 to 4).

Embedding governance (`embeddings-outside-governance`). OWASP reports that stored embeddings can be inverted to recover source text, including by zero-shot methods that need no encoder-specific training, and concludes that "[e]mbeddings only" is not a safe-harbor classification (Tier A for the standard's conclusion, OWASP LLM09:2026 Common Examples 2 and Scenario 3, and LLM02:2026 Common Examples item 3; I have not read the inversion papers it cites, so this stub carries none of their recovery rates). Its storage lifecycle guidance is to delete embeddings within a bounded time after the source is deleted and verify by reconciliation, to hold vector-database backups at the source documents' tier, to re-embed the corpus when the embedding model rotates rather than mixing vectors, and to treat embedding-API keys as secrets (Tier A, OWASP LLM09:2026, Prevention 5). I found no CoSAI control at this commit scoped to retention or access on the vector store itself, since User Data Management covers prompts and logs and Model and Data Access Controls lists model storage rather than data storage, so OWASP carries this leg alone (Tier D, my reading).

## What this does not mean

It does not mean the standards are wrong where they are silent, or that a deployment following both is safe, because neither document measures anything and neither says which store configurations make in-query scoping the default. It also does not mean that a vectorless retrieval system escapes the problem, since OWASP notes such systems "inherit the non-geometric risks but have no LLM09 attack surface", which I read as leaving access control and injection through retrieved content fully in play (Tier A for the quote, OWASP LLM09:2026 Description; Tier D for my reading). And because the CoSAI poisoning risk carries no MITRE ATLAS mapping at this commit, while OWASP's LLM09:2026 text points to an ATLAS RAG-poisoning technique, a team that builds its coverage report by joining CoSAI risks to ATLAS will find no path from this risk and may read the surface as quieter than it is.

## Gaps

- **Gap: retrieval-time access control in practice**. The repo has no default-state table showing, per vector-store family, whether metadata or permission filters are applied inside the similarity search or after it, and no bench measuring what leaks across the two (unauthorized chunks reaching the prompt, and count, score and timing side channels) or whether deleting a source document removes its embeddings and backups. **Needs**: a dated default-state table read from each store family's documentation with `last-checked` per row, and a lab bench on two or three open-source vector stores with a seeded permission model that measures pre- and post-filter leakage and deletion reconciliation; a published practitioner study of how often deployed RAG systems propagate source ACLs would also close it.

## Notes

- `convergence` is `single-source` because, although two standards prescribe in-query scoping and provenance tracking, this stub names no independent implementation that demonstrates them, so the standards route in `CONTRIBUTING.md` does not complete. Dated 2026-11-10.
- OWASP IDs are cited only in their 2026 form. The CoSAI control records at this commit carry their own mappings to the earlier edition, which this stub deliberately does not reproduce; re-mapping them is covered in `analysis/revalidation-and-pins.md`.
- The CoSAI counts (37 controls, 36 risks, five controls on the poisoning risk, one control naming the RAG content component explicitly) were read from the YAML at the pinned commit on 2026-11-10.
- `revalidate-by` is about four months out because both pins are young (the OWASP edition was published in August 2026) and a CoSAI commit that adds a retrieval access-control or retention control would change the third paragraph of the analysis.

## Sources

Tier A, standards and framework projects:

- OWASP GenAI Security Project, "OWASP Top 10 for LLM Applications 2026", resource page dated 2026-08-03, https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/ (PDF, read 2026-11-10): LLM01:2026 Prompt Injection (Scenario 4), LLM02:2026 Sensitive Information Disclosure (Common Examples item 3), LLM09:2026 Vector and Embedding Weaknesses (Description, Common Examples 1 to 7, Prevention 1 to 6, Scenario 3).
- Coalition for Secure AI (OASIS Open Project), secure-ai-tooling risk map, commit 622605a1 (main, 2026-10-21), https://github.com/cosai-oasis/secure-ai-tooling, files `risk-map/yaml/risks.yaml` (`riskRetrievalVectorStorePoisoning`), `risk-map/yaml/controls.yaml` (`controlRetrievalAndVectorSystemIntegrity`, `controlAgentPluginPermissions`, `controlUserDataManagement`, `controlModelAndDataAccessControls`), `risk-map/yaml/components.yaml` (`componentRAGContent`), read 2026-11-10.

Tier A, peer-reviewed research:

- Greshake, Abdelnabi, Mishra, Endres, Holz and Fritz, "Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection", ACM AISec Workshop 2023, doi:10.1145/3605764.3623985 (arXiv 2302.12173).

Tier D, this repo:

- `analysis/surface-ownability.md`, for the S12 ownership band.
