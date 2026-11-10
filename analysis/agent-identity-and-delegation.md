---
evidence-tier: Mixed
convergence: single-source
applies-to-signals: [nhi-inventory-absent, agent-static-secrets, delegation-record-absent]
surfaces: [S4, S5, S6, S8]
pins:
  - "Keycloak 26.8.1 (lab run T7, start-dev, default and preview delegation feature sets)"
  - "OCSF 1.9.0 (delegation object and ai_operation profile, validated by lab run T7 at schema.ocsf.io)"
  - "IETF RFC 8693 and RFC 9700 as read 2026-11-09"
  - "DuckDB 1.5.3 and chDB 4.4.0 (lab run R7)"
  - "NHI and agent-identity vendor and incumbent documentation as read 2026-11-09"
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-03-10
status: EMERGING
measurement-claims:
  - claim: "Every Keycloak 26.8.1 TOKEN_EXCHANGE event named the client the subject token was issued to (subject_token_client_id, 72 of 72 successful exchanges in the default arm and 15 of 15 exchange events in the delegation arm) and none named the subject token's own id (0 of 78 and 0 of 15 hops), so the chain is explicit at client granularity and only implicit at token granularity; one host, one IdP version, synthetic realm"
    source: "sdw-lab-benchmarks@e568f5b (branch hub/ai-research-2026-11-09) t7-idp-delegation-logging/RESULTS.md:28-31, :57"
    date: 2026-11-10
    revalidate: 2027-05-10
  - claim: "With one user token exchanged by three agent instances in one session, a nearest-earlier attribution rule linked 5 of 15 hop-2 events to the right hop 1, a figure the harness design fixes because every hop 1 was issued before any hop 2 and no event field could disambiguate them; a scope-equality heuristic scored 15 of 15 only because the fixture gave each chain a distinct scope set"
    source: "sdw-lab-benchmarks@e568f5b (branch hub/ai-research-2026-11-09) t7-idp-delegation-logging/RESULTS.md:32-36, :59"
    date: 2026-11-10
    revalidate: 2027-05-10
  - claim: "Keycloak dropped a scope the user had no role for in 8 of 8 attempts and recorded the requested scope in no event field; with the downscope enforcer policy on, its 6 refusals carried the attempted scope only inside client_policy_error_detail and carried no userId, sessionId, username or subject_token_client_id; switching the policy on and off produced zero admin events on REST and in the INFO log"
    source: "sdw-lab-benchmarks@e568f5b (branch hub/ai-research-2026-11-09) t7-idp-delegation-logging/RESULTS.md:41-49, :60-61, :91-94"
    date: 2026-11-10
    revalidate: 2027-05-10
  - claim: "Keycloak's RFC 8693 delegation preview put the actor into the token (act, 9 of 9) and the event (actor, actor_id, actor_type), dropped sid from 9 of 9 delegated tokens and sessionId from the delegated exchange events, refused a second actor hop 3 of 3, and granted a delegated re-exchange with data:write that the subject token did not hold 3 of 3"
    source: "sdw-lab-benchmarks@e568f5b (branch hub/ai-research-2026-11-09) t7-idp-delegation-logging/RESULTS.md:58, :62, :84"
    date: 2026-11-10
    revalidate: 2027-05-10
  - claim: "Mapped to OCSF 1.9.0, an IdP-events-only producer filled delegation.uid, issuer_uid and created_time on every exchange hop and parent_uid on 0 of 81; scopes and audience exist on OCSF main only; a producer holding the subject token (the agent's own record) filled parent_uid on every hop"
    source: "sdw-lab-benchmarks@e568f5b (branch hub/ai-research-2026-11-09) t7-idp-delegation-logging/RESULTS.md:64, :143-153"
    date: 2026-11-10
    revalidate: 2027-05-10
  - claim: "Over synthetic delegation-shaped records at 1e5 to 1e7 rows and chain depths 2 to 12, the recursive walk, a one-join parent check and a write-time materialized filter each returned exactly the planted escalation set in 18 of 18 cells in both engines and both runs, while a root-only check missed every reacquire plant (31,758 chains per run) and nothing else"
    source: "sdw-lab-benchmarks@7301388 (branch hub/ai-research-2026-11-09) delegation-chain-query/RESULTS.md:31-39, :66"
    date: 2026-11-09
    revalidate: 2027-05-09
  - claim: "At 1e7 rows and depth 12 the recursive walk ran in a median 1.56 to 1.70 s in DuckDB 1.5.3 and 0.87 to 0.99 s in chDB 4.4.0, the one-join check in 0.28 to 0.41 s and the materialized filter in 20 to 27 ms, on one shared host under a load average of 7.5 to 26; within-cell ratios are the defensible output"
    source: "sdw-lab-benchmarks@7301388 (branch hub/ai-research-2026-11-09) delegation-chain-query/RESULTS.md:40-50, :73-79"
    date: 2026-11-09
    revalidate: 2027-05-09
---

# Agent identity and delegation: what the agent borrows, what the token says, and what to log

Evidence tier: Mixed, with IETF and NIST standards and peer-reviewed measurement at A, two verified lab runs on one host at B, vendor documentation at B for what a feature does and C for coverage and ratio claims, two vendor-authored preprints at C, and the sizing and buy-or-enable judgements at D.

## Summary for the review

An AI agent rarely holds an identity of its own; it borrows a user's delegated grant, a workload's service account or a long-lived API key, and the record a security team would want, the agent-era analogue of a Windows 4624 logon that says "agent A acted as user U through tool T under scope S", is one that no production source I examined emits in full today. So the work starts with knowing which identities agents hold, then shortening what they hold, then assembling the partial delegation record that can be built now.

- Inventory the identities agents use (agent identities, borrowed workload identities, static secrets and delegated OAuth grants) from the IdP, cloud and code-scanning features already licensed, before buying a discovery product whose value grows with the number of sources it joins. Effort M. Tier B for the features, D for the buy threshold.
- Replace long-lived agent API keys with short-lived, audience-restricted tokens minted by a broker the organization controls, and scan code for the keys that remain. Effort M to L. Tier A (RFC 9700 §2.3, NIST SP 800-207 tenet 3, Meli et al. for leakage).
- Where agents use OAuth 2.0 Token Exchange, have the agent or gateway log the id of the subject token it presented beside the IdP's event, because in lab run T7 the IdP named the issuing client on every successful hop but never the parent token, and once three agent instances shared a session nothing in the events could tell their hops apart. Effort M. Tier B, one IdP at one version.
- Evaluate scope chain-aware, each hop against its parent hop, because a root-only check missed every re-grant plant in lab run R7, and materialize the parent's effective scope at write time where the ingest path can look it up. Effort M. Tier B for the measurement, A for the attenuation property.
- Snapshot IdP authorization-policy configuration on a schedule, because a policy change produced no admin event in T7. Effort S. Tier B.

The delegation-record key sits at Low priority because no production source carries the full join, so it is assembly work.

## Why this matters

NIST SP 800-63-4 scopes itself to human users and says in §1.1 that it does "not explicitly address" machine-to-machine authentication or "access to Application Programming Interfaces (APIs) on behalf of subjects", which is the agent-delegation case (Tier A, NIST SP 800-63-4), so the identity guidance most programs are built on stops at the point where agents start. What fills the space today is a mix of OAuth practice, cloud workload identity and a vendor category that sells inventories of non-human identities, and the evidence that the underlying condition is common is now better than vendor surveys. Six of eleven models tested as LLM agents chose a higher-privilege tool when a sufficient lower one existed more than 30% of the time (Tier A, Yang et al., Findings of EMNLP 2026), 47.7% of 789 AWS Lambda applications carried excess permissions with a median of 9 granted against 1 required (Tier B, preprint arXiv 2607.02875), and secret leakage on public GitHub reached over 100,000 repositories with only 19% of leaked secrets removed after 16 days (Tier A, Meli et al., NDSS 2019, on 2017 to 2018 data from public repositories only). None of those studies measures enterprise non-human identity populations directly, and the vendor ratios of non-human to human identities (100:1, 50:1, 109:1) differ by a factor of two and show no method (Tier C, vendor homepages read 2026-11-09, bias flagged), so I would not quote a ratio to a board.

The logging gap is the part I find most interesting, because it is structural rather than a product defect. RFC 8693 represents a delegation chain inside the token as nested `act` claims of any depth, treats prior actors as "informational only" and "not to be considered in access control decisions" (§4.1), defines no per-hop scope, and says nothing about what the authorization server should log (Tier A, RFC 8693). Chan et al. treat agent identifiers, real-time monitoring and activity logging as three separate visibility measures with separate implementations (Tier A, ACM FAccT 2024), which matches what the identity-plane logs show: they record that an agent authenticated, and the reads and writes it then made live in each resource's own log.

## Token exchange, delegation and what an IdP actually records

Lab run T7 put an OAuth 2.0 Token Exchange chain (user, then agent A, then agent B, then a tool API) through Keycloak 26.8.1 in two arms, the default feature set and the RFC 8693 delegation preview, and read every event, token and admin record back (Tier B, sdw-lab-benchmarks branch hub/ai-research-2026-11-09, folder t7-idp-delegation-logging, one host, synthetic realm, pre-registration frozen by an agent and not owner-reviewed, verdict VERIFIED-WITH-FIXES with every scored number reproduced by a full independent re-run). The findings, each a Keycloak 26.8.1 result that another IdP may well not share:

- Every successful exchange event, and each refusal in the delegation arm, named the client the subject token was issued to (`subject_token_client_id`), and each successful one also named the id of the token it issued (`token_id`, equal to the new token's `jti`), but none named the subject token's own id, so the chain is explicit at client granularity and implicit, by session and time order, at token granularity.
- When three agent instances exchanged one user token in one session, nothing linked a hop 2 to its hop 1, and the pre-registered nearest-earlier rule attributed 5 of 15 correctly, which is the one-in-three the harness design guarantees when the events carry no disambiguating field rather than an accuracy rate. A scope-matching heuristic would have scored 15 of 15, but only because each planted chain had a distinct scope set, which real traffic does not guarantee.
- Each event carried the effective scope of the token it issued, so a re-grant inside one session was detectable from IdP events alone. A scope the user had no role for was silently dropped, though, and no field recorded what had been requested.
- With the downscope enforcer policy on, refusals named the attempted scope inside a free-text detail string and carried no user, session or chain field, so the attempt could not be attributed from the event alone. Turning that policy on and off produced no admin event, and the admin-event type list has no client-policy type, so on the surfaces checked this looks like an event kind Keycloak does not have.
- The delegation preview wrote the actor into the token (`act`) and the event, which is the audit trail the RFC describes, and in the same move dropped the session identifier from both and refused a second actor hop. The one-hop limit is an implementation choice, since §4.1 allows nesting to any depth, and the preview granted a delegated re-exchange a scope the subject token never held, which the standard permits because neither RFC 8693 nor RFC 9700 requires a delegated token's scope to be a subset of its subject token's (Tier A, RFC 8693 §5, RFC 9700 §2.3).

The academic record lines up with this without adding an independent measurement. A Splunk and Cisco preprint shows on synthetic workloads that audit logs and traces can be identical under incompatible delegation assignments and that time-window reconstruction degrades once more than about a fifth of delegations overlap (Tier C, Mishra and Sharad, arXiv 2606.09692, vendor-authored, bias flagged), and Nian et al. call cross-chain attribution in multi-agent systems "largely open" (Tier B, preprint arXiv 2604.05485). OAuch found that the average deployed IdP omits about a third of OAuth security specifications, though it did not test token exchange (Tier A, Philippaerts et al., RAID 2022), which I read as a reason to repeat T7 on a second IdP rather than generalize from Keycloak.

## Why chain-aware evaluation, and what it costs

Lab run R7 asked what it costs to evaluate scope across a delegation chain at query time (Tier B, sdw-lab-benchmarks branch hub/ai-research-2026-11-09, folder delegation-chain-query, synthetic integer-keyed records, one shared host, agent-frozen pre-registration, VERIFIED-WITH-FIXES). It planted one escalation in 1% of chains and compared four checks. The recursive walk, a one-join check of each hop against its parent and a filter on a write-time materialized parent-scope column each returned exactly the planted set in 18 of 18 cells, in DuckDB 1.5.3 and chDB 4.4.0 and in both runs, while the root-only check, which compares each hop with the human root's authority, missed every `reacquire` plant and nothing else. A hop that re-grants authority an intermediate agent had already dropped stays inside the root's authority, so a root-only check cannot see it, and T7 restated the same result on real Keycloak fields (5 of 5 re-grants caught chain-aware, 0 of 5 root-only). The per-cell recall of the root-only check (0.55 to 0.67 in the larger cells) is set by the generator's plant mix, so it shows the blind spot exists and says nothing about how often re-grants happen in real agent traffic.

The cost side favours not walking. At 1e7 rows and depth 12 the walk took a median 1.56 to 1.70 s in DuckDB and 0.87 to 0.99 s in chDB, the one-join check 0.28 to 0.41 s, and the materialized filter 20 to 27 ms, which is answer-identical to the walk. Those absolute numbers were taken under a load average of 7.5 to 26 from other work on the host, the pre-registered depth hypothesis was falsified for DuckDB, and the cost of looking up the parent's scope at ingest was not measured, so the defensible reading is the within-cell ratio and the design consequence: the cheap checks are exact only when each hop's record carries its own granted scopes and a pointer to its parent. Monotonic attenuation at each hop is old and peer-reviewed as a property, being the defining property of macaroons (Tier A, Birgisson et al., NDSS 2014, largely Google-authored), but I should say plainly that asking for per-hop scopes plus a parent pointer goes beyond what RFC 8693 asks for, and a vendor that follows the RFC to the letter has a documented reason not to evaluate the chain in access decisions.

## What to log, field by field

The record below is what I would ask each hop to produce, mapped to OCSF 1.9.0 where an attribute exists. T7 validated these attribute names against the 1.9.0 schema; in 1.9.0 the `delegation` object reaches the authentication class only through the `ai_operation` profile, and `scopes`, `audience` and `expiration_time` exist on OCSF main and not in the 1.9.0 release (Tier B, T7 RESULTS, OCSF mapping section).

| Field | OCSF 1.9.0 | Who can fill it today | Note |
|---|---|---|---|
| Hop id (issued token id) | `delegation.uid` | The IdP, on every exchange in T7 | Keycloak `token_id` |
| Parent hop id | `delegation.parent_uid` | The agent or gateway that presented the subject token; the IdP in 0 of 81 hops in T7 | The single most useful field to add |
| Issuer | `delegation.issuer_uid` | The IdP | Realm or tenant issuer |
| Time | `delegation.created_time` | The IdP | Clock-sync the agent and IdP |
| Granted scopes | not in 1.9.0 (main only) | The IdP, effective scope per hop in T7 | Carry in `unmapped` until a release adds it |
| Requested scopes | none | Nobody in T7; the enforcer refusal string only | Needed to see attempts the IdP silently trimmed |
| Audience | not in 1.9.0 (main only) | The IdP | Resource the hop is for |
| Acting agent | `actor.app_name` | The IdP (requesting client) | `act` claim in delegation mode |
| Human subject | `user` | The IdP on success; absent on enforcer refusals in T7 | Refusals then fail the class's required `user` |
| Session | `actor.session` (my mapping, not validated in T7) | The IdP in the default arm; dropped in Keycloak's delegation preview | Do not rely on it as the chain key |

Beyond the per-hop record, two more things belong in the store. The first is the IdP's configuration of exchange and scope policy, captured on a schedule and diffed, since T7 found no admin event for a policy change. The second is the downstream activity, which stays in each resource's own log under the application or agent id. The join from "granted in March" to "read the mailbox in October" is assembled there, by matching the grant's client id to the resource log, and no identity-plane source I read records it as a grant id (Tier B, vendor documentation read 2026-11-09).

## Turn on before you buy

Much of the inventory and posture half of the non-human identity category is available per platform from licences many organizations already hold, while the cross-platform join is what no incumbent sells and the per-hop delegation record is something no commercial product documents on its public pages as of 2026-11-09 (Tier B, vendor documentation of twelve NHI and agent-identity vendors and six incumbents, read 2026-11-09). Research prototypes carry parts of it, AIP most completely with one attenuating Biscuit block per hop and the parent implied by block order (Tier B, preprint arXiv 2603.24775).

| Platform family | Setting | Default | Where the record lands | last-checked |
|---|---|---|---|---|
| AWS IAM Access Analyzer | Unused access analysis (roles, access keys, passwords, unused services and actions) | Runs once an unused-access analyzer is created; charged per IAM role and user analyzed per analyzer per month | Access Analyzer findings | 2026-11-09 |
| AWS Bedrock AgentCore | CloudTrail data events for WorkloadIdentity, WorkloadIdentityDirectory and TokenVault | Off; billed when enabled | CloudTrail trail or lake the customer configures | 2026-11-09 |
| Microsoft Entra Agent ID | Agent identities with sponsors; agent sign-in and audit logs | Platform available to Entra customers; security features for agents need Agent 365 or E7 | Entra sign-in and audit logs (authentication events, not downstream activity) | 2026-11-09 |
| Okta ISPM | Dormant-account detection across human and non-human identities | 90-day dormancy threshold as documented | Okta ISPM findings | 2026-11-09 |

The rows say what the vendor documents and not how well it works; the Entra overview's line that "all agent authentication and activity is logged" is true at the identity plane for Entra-identified agents, and agents admitted through neither the Entra ID Auth SDK sidecar nor workload identity federation, such as a framework agent nobody federated, are outside it by Microsoft's own documentation (Tier B, vendor documentation read 2026-11-09).

On sizing, my judgement (Tier D, 2026-11-10) is that an organization on one cloud and one IdP gets most of the inventory from the rows above and should route their findings to a store it owns before evaluating a discovery product, and that a broker is worth its cost only where the organization builds its own agents on S5 to S8, after the hyperscaler's own broker has been evaluated. A large organization with several clouds, IdPs and hundreds of SaaS tenants has a join large enough to buy, and I would write three conditions into the contract: export of the inventory and findings in a documented schema (ask for the OCSF `actor`, `ai_agent` and `delegation` mappings and expect "not yet"), a one-year term, given that five of the twelve vendors I profiled changed hands between June and September 2026 (Tier C, press and vendor releases), and a review of the per-connector permission manifest before anything is connected, because the discovery tool may be the most privileged non-human identity the organization adds that year.

## What this does not mean

T7 measured one IdP at one version in dev mode on one host, and another IdP's exchange event may well carry the subject token's id, so the specific gaps above are Keycloak 26.8.1 findings and the general point is only that the standard does not require the IdP to log the chain. R7's records are synthetic, linear and integer-keyed, real delegation forms trees and sometimes cycles, and string keys would raise the cost of the walk and the join. The chain-aware rule goes beyond RFC 8693's access-control posture, so I present it as a detection design rather than a compliance requirement, and a team that cannot get per-hop scopes from its sources can still run the root-only check, knowing which class it misses. The upgraded evidence on over-privilege comes from LLM tool choice and serverless permissions rather than enterprise identity inventories, and the vendor-authored preprints that corroborate the logging gap (Mishra and Sharad; Dantuluri and Sundi, arXiv 2609.00267, by VotalAI staff) are Tier C and carry less weight than the RFC text does.

## Gaps

- **Gap: second IdP**. The exchange-event schema is measured on Keycloak 26.8.1 only. **Needs**: the T7 harness re-run against Entra, Okta or Auth0 token exchange.
- **Gap: requested versus granted scope**. No source examined records the scope an agent asked for when the IdP trimmed it. **Needs**: an IdP that logs requested scope, or a gateway-side capture measured against IdP events.
- **Gap: policy-change admin events**. T7 found none for a client-policy change on REST and the INFO log; DEBUG was not checked. **Needs**: a DEBUG-level check and the same test on a second IdP.
- **Gap: re-grant frequency**. R7 and T7 show the blind spot exists; nothing measures how often re-grants occur in production agent traffic. **Needs**: a production or realistic multi-agent trace scored with the chain-aware check.
- **Gap: write-time materialization cost**. R7 generated the parent's effective scope for free. **Needs**: an ingest path that looks it up per hop, measured for cost and freshness.
- **Gap: concurrent delegation-mode attribution**. Keycloak's delegation arm was linked correctly 9 of 9 only in sequential single-chain runs. **Needs**: an interleaved delegation-arm scenario.
- **Gap: NHI ratios**. Vendor ratios of non-human to human identities show no method. **Needs**: a published enterprise measurement with its method.
- **Gap: the full join in production**. No production source examined carries agent, user, tool and scope per action. **Needs**: a vendor or platform record that does, verified against its documentation and a captured event.

## Notes

- Decision 16 choices: the T7 counts are quoted per arm because the arms used different login grants; the R7 latency ranges are given across both runs because the pre-registered single-run thresholds were unstable under load.
- The vendor rows and the "no commercial product documents a per-hop record" sentence come from a documentation read of 2026-11-09 in which three vendors' documentation portals were gated, so their export schemas could not be checked. Aembit's "chain step" conditional-access attribute is the first place I would look before repeating that sentence, because if it is a logged field it would be the first.
- R7's attribute names were its own and were not checked against OCSF 1.9.0; the field table above uses T7's validated names instead.
- Both lab runs carry an independent verification with the verdict VERIFIED-WITH-FIXES; T7's verification included a cross-provider leg and R7's record names none. The pre-registrations were frozen by an agent before each run and were not owner-reviewed.

## Sources

Tier A

- IETF RFC 8693, OAuth 2.0 Token Exchange, 2020, https://www.rfc-editor.org/rfc/rfc8693, §4.1 and §5, read 2026-11-09.
- IETF RFC 9700, Best Current Practice for OAuth 2.0 Security, 2025, https://www.rfc-editor.org/rfc/rfc9700, §2.3 and §4.10.1, read 2026-11-09.
- NIST SP 800-207, Zero Trust Architecture, 2020, https://doi.org/10.6028/NIST.SP.800-207, §2.1.
- NIST SP 800-63-4, Digital Identity Guidelines, 2025, https://doi.org/10.6028/NIST.SP.800-63-4, §1.1.
- Meli, McNiece, Reaves, "How Bad Can It Git? Characterizing Secret Leakage in Public GitHub Repositories", NDSS 2019, https://doi.org/10.14722/ndss.2019.23418.
- Birgisson et al., "Macaroons: Cookies with Contextual Caveats for Decentralized Authorization in the Cloud", NDSS 2014, https://doi.org/10.14722/ndss.2014.23212 (largely Google-authored).
- Philippaerts, Preuveneers, Joosen, "OAuch: Exploring Security Compliance in the OAuth 2.0 Ecosystem", RAID 2022, https://doi.org/10.1145/3545948.3545955.
- Chan et al., "Visibility into AI Agents", ACM FAccT 2024, https://doi.org/10.1145/3630106.3658948.
- Yang et al., "When Lower Privileges Suffice: Investigating Over-Privileged Tool Selection in LLM Agents", Findings of EMNLP 2026, https://doi.org/10.18653/2026.findings-emnlp.2059.

Tier B

- sdw-lab-benchmarks, branch hub/ai-research-2026-11-09, folder t7-idp-delegation-logging (RESULTS.md, VERIFICATION.md), commit e568f5b, run 2026-11-10, https://github.com/flying-coyote/sdw-lab-benchmarks.
- sdw-lab-benchmarks, branch hub/ai-research-2026-11-09, folder delegation-chain-query (RESULTS.md, VERIFICATION.md), commit 7301388, run 2026-11-09, same repository.
- Yeboah-Duako, Datta, "Permissions on the Loose: Measuring Overprivilege in Real-World Serverless Applications", preprint, 2026, https://arxiv.org/abs/2607.02875.
- Nian et al., "Auditable Agents", preprint, 2026, https://arxiv.org/abs/2604.05485.
- Prakash, "AIP: Agent Identity Protocol for Verifiable Delegation Across MCP and A2A", preprint, 2026, https://arxiv.org/abs/2603.24775.
- Microsoft Learn, Microsoft Entra Agent ID overview (updated 2026-08-13) and agent ID Governance (updated 2026-11-07), read 2026-11-09.
- AWS documentation, IAM Access Analyzer unused access analysis and Bedrock AgentCore CloudTrail data events, read 2026-11-09.
- Okta Identity Security Posture Management product page (undated), read 2026-11-09.

Tier C

- Mishra, Sharad, "Observability for Delegated Execution in Agentic AI Systems", preprint, 2026, https://arxiv.org/abs/2606.09692 (Splunk and Cisco authors, bias flagged).
- Dantuluri, Sundi, "Delegation Without Trust", preprint, 2026, https://arxiv.org/abs/2609.00267 (VotalAI authors, bias flagged).
- Vendor homepages and releases for non-human-to-human identity ratios and acquisitions (Astrix, Token Security, Palo Alto Networks Idira, Cyera, SailPoint, Cisco, Snowflake, Okta), read 2026-11-09.
