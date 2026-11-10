---
evidence-tier: Mixed
convergence: single-source
applies-to-signals: [agent-kill-switch-absent, ai-playbook-absent, model-rollback-untested]
surfaces: [S4, S5, S6, S7, S8, S9, S11, S12]
pins:
  - "CoSAI AI Incident Response Framework V1.0 (document version 24fecc8c, dated 27 October 2025)"
  - "NIST SP 800-61 Rev. 3 (April 2025)"
  - "OASIS CACAO Security Playbooks Version 2.0"
  - "CISA Known Exploited Vulnerabilities catalog, catalogVersion 2026.11.09"
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-04-24
status: EMERGING
---

# AI incident response: declared gap

Evidence tier: Mixed. The lifecycle comes from NIST SP 800-61 Rev. 3 (Tier A), the AI-specific containment and playbook content from the CoSAI framework, an OASIS Open Project publication graded like the repo's other CoSAI material (Tier A for what it prescribes), the pre-authorization rule from practitioner talks (Tier B), and the reading of how these fit a company that mostly rents its AI is mine (Tier D). This repo has measured nothing on the question yet, which is why this is a stub.

## Summary for the review

This repo has no researched document on AI incident response, so the advice is to extend the incident-response standard the organization already runs, which for most will be NIST SP 800-61 Rev. 3 or a SANS-style lifecycle, using the CoSAI AI Incident Response Framework V1.0 as the AI-specific supplement, and to treat the three routed signals as the first things to prove rather than to document. The actions, in the order I would take them:

- Add AI incident types to the existing plan and its severity criteria instead of writing a separate AI plan (S, Tier A).
- For every agent and every model route, write down the three containment levers (revoke the agent's credential, disable the route at the gateway or provider console, roll back the model, prompt or configuration version), who holds each one, and who has authority to pull it (M, Tier A).
- Pre-authorize only containment that is scoped, reversible and already tested, and keep a human gate on everything else (M, Tier B).
- Run a technical drill that actually pulls each lever once in a non-production copy and records how long it took to take effect and what kept running (M, Tier A for the practice; nothing measured here).
- Preserve agent memory, vector store state and the tool-call record before containment wipes them (S, Tier A).
- For rented surfaces, find out which levers the vendor holds and ask how fast they act on a customer's request (S, Tier D for the reading).

The declared gap is that I have not found a published measurement of whether these levers work when pulled, and this repo has not made one.

## Why this matters

The `agent-kill-switch-absent` signal is the only PROBLEM in this family and it carries a High band, because an agent acting on stolen or confused instructions keeps acting until something stops it, and the stopping mechanism is usually discovered during the incident. Woodruff's point at the October 2026 [un]prompted conference (Tier B, paraphrased from an auto-transcript) is the one I keep coming back to, that when an agent borrows a person's identity, pulling the plug on the agent locks out the person too, so in many environments the honest answer to "can you revoke this agent" is "only by revoking a human". Nagarajan, at the same conference, argued that autonomous attacks move faster than a human-gated response can, which is the case for pre-authorizing containment, and Jaksic described a recovery-path safeguard that became a single point of failure, which is the case for testing it first.

The serving and orchestration layer is also where 2026's known exploitation landed, so a rollback or emergency patch path is something a responder may well need this year. CISA's catalog at catalogVersion 2026.11.09 added eleven entries during 2026 for AI orchestration and serving software, three for LiteLLM, five for Langflow (one under IBM's product name), one each for MLflow, Ray and n8n (Tier A data, Tier B derivation, re-derived from the catalog JSON for this stub). That count says those products were exploited somewhere; it says nothing about which organizations were affected.

## What the standards already carry

NIST SP 800-61 Rev. 3 recasts incident response as a CSF 2.0 community profile, so an AI incident sits inside Govern, Identify, Protect, Detect, Respond and Recover like any other (Tier A). It names no AI-specific actions, which is the part CoSAI fills.

The CoSAI framework, a 27 October 2025 document from the coalition's defender workstream, maps itself to 800-61 Rev. 3 and to SANS PICERL (§1.2.1, §4.1) and lists the containment actions this family's signals ask about (Tier A for what it prescribes, PDF read 2026-11-10):

- in its five-phase plan summary, "Disable tools or rollback to prior model; gate high-risk features" (§1.3.2);
- architecture-specific containment, including memory reset and conversation-history purging for LLMs with memory, data source quarantine for RAG, and "Disable tools, enhance authorization, least privilege checks" for agentic systems (§3.3.3);
- model-level eradication by rolling back "to secure versions" and recovery that rolls back "fine-tuned models or agent states" (§3.3.3, §4.1);
- evidence preservation before containment, naming vector database state and model weight copies (§3.3.3);
- a RACI row for "Take Model Offline", with the incident commander accountable and the AI/ML engineer responsible (§1.3.3);
- quarterly tabletops and technical drills that "Test containment procedures" and "Validate recovery processes" (§3.4.2), and a lessons-learned line to "clarify authority to disable/rollback" (§1.3.5).

It also ships six sample playbooks, among them multi-channel prompt injection, memory injection and RAG poisoning, written in the OASIS CACAO 2.0 playbook structure (§4.2, §4.3), which is a reasonable starting point for the `ai-playbook-absent` signal.

What the framework assumes, as I read it, is an organization that runs its own models, which shows in its model-weight copies and retraining steps. Its own provider and consumer split (§3.4.1) puts incident detection on the consumer and inference infrastructure on the provider, and for a company whose AI is mostly SaaS assistants and API calls the levers it describes sit partly with a vendor whose response time the company has never tested (Tier D).

## What this does not mean

It does not mean a separate AI incident-response function is needed. Both sources treat AI incidents as a variant of the existing lifecycle, and I would resist anything that forks the on-call path. Nor does a written kill switch count as a working one: the signal asks whether the lever has been tested, and a documented procedure that has never been exercised should still answer no. And a rollback is only reversible containment if the previous version is still available and still safe, which the Replit case from July 2025 illustrates in an unflattering way, since press accounts disagreed on whether the deleted production database could be restored at all (Tier C, AI Incident Database report 5593 and press coverage).

## Gaps

- **Gap: AI containment drills**. No public measurement shows how long credential revocation, route disablement or model rollback takes to stop an agent that is already running, what keeps acting afterwards (in-flight sessions, cached or refresh tokens, scheduled tasks the agent created), or whether the action leaves a record in the audit log, and the incident write-ups I have read rarely report the containment step at all. **Needs**: a pre-registered lab bench that pulls each of the three levers against a running agent on at least two agent platforms and one gateway, timing time-to-effect and recording residual activity and audit trail per lever, plus a study coding the containment actions reported in public AI incident write-ups.

## Notes

The containment levers are named generically on purpose, because the mechanism differs by surface (a gateway route on S8, an app registration or connector on S6 and S7, an MCP server entry on S4 and S5, a model registry version on S9 and S11). The ordering of the summary actions is my practitioner judgement, dated 2026-11-10, and follows the containment step of `../decision-sequence.md`. No `measurement-claims` rows are carried, since no lab run backs this stub.

## Sources

Tier A

- NIST SP 800-61 Rev. 3, "Incident Response Recommendations and Considerations for Cybersecurity Risk Management: A CSF 2.0 Community Profile", April 2025: https://csrc.nist.gov/pubs/sp/800/61/r3/final
- CoSAI, "AI Incident Response Framework, V1.0", Workstream 2, document version 24fecc8c dated 27 October 2025, PDF read 2026-11-10: https://www.coalitionforsecureai.org/wp-content/uploads/2026/03/AI-Incident-Response-1.pdf (project: https://github.com/cosai-oasis/ws2-defenders)
- OASIS, CACAO Security Playbooks Version 2.0: https://docs.oasis-open.org/cacao/security-playbooks/v2.0/security-playbooks-v2.0.html
- CISA Known Exploited Vulnerabilities catalog, catalogVersion 2026.11.09 (1,773 entries), read 2026-11-09; the count of 2026 AI orchestration and serving entries is my derivation from it: https://www.cisa.gov/known-exploited-vulnerabilities-catalog

Tier B
- [un]prompted practitioner conference, October 2026, talks by Woodruff, Nagarajan and Jaksic; auto-transcripts read by line, paraphrased here.

Tier C

- AI Incident Database report 5593 (Replit agent deletes production database, July 2025) and press coverage; the agent's own statements were the only account of why: https://incidentdatabase.ai/reports/5593/

Tier D

- My reading of how the CoSAI levers fall between provider and consumer on rented surfaces, and the order of the summary actions, dated 2026-11-10.
