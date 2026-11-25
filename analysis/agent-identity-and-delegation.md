---
evidence-tier: Mixed
convergence: single-source
applies-to-signals: [nhi-inventory-absent, agent-static-secrets, delegation-record-absent, agent-identity-owner-absent]
surfaces: [S4, S5, S6, S8]
pins:
  - "Keycloak 26.8.1 (lab run T7, start-dev, default and preview delegation feature sets)"
  - "OCSF 1.10.0 (delegation object with scopes, audience and expiration_time; lab run T7 validated against 1.9.0 at schema.ocsf.io)"
  - "IETF RFC 8693 and RFC 9700 as read 2026-11-09"
  - "DuckDB 1.5.3 and chDB 4.4.0 (lab run R7)"
  - "NHI and agent-identity vendor and incumbent documentation as read 2026-11-09"
  - "CoSAI Agentic Identity and Access Management v1.0"
  - "MCP specification 2026-07-28"
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-05-18
status: EMERGING
measurement-claims:
  - claim: "Every Keycloak 26.8.1 TOKEN_EXCHANGE event named the client the subject token was issued to (subject_token_client_id, 72 of 72 successful exchanges in the default arm and 15 of 15 exchange events in the delegation arm) and none named the subject token's own id (0 of 78 and 0 of 15 hops), so the chain is explicit at client granularity and only implicit at token granularity; one host, one IdP version, synthetic realm"
    source: "sdw-lab-benchmarks@91e44df t7-idp-delegation-logging/RESULTS.md:28-31, :57"
    date: 2026-11-10
    revalidate: 2027-05-10
    replication: same-host
  - claim: "With one user token exchanged by three agent instances in one session, a nearest-earlier attribution rule linked 5 of 15 hop-2 events to the right hop 1, a figure the harness design fixes because every hop 1 was issued before any hop 2 and no event field could disambiguate them; a scope-equality heuristic scored 15 of 15 only because the fixture gave each chain a distinct scope set"
    source: "sdw-lab-benchmarks@91e44df t7-idp-delegation-logging/RESULTS.md:32-36, :59"
    date: 2026-11-10
    revalidate: 2027-05-10
    replication: same-host
  - claim: "Keycloak dropped a scope the user had no role for in 8 of 8 attempts and recorded the requested scope in no event field; with the downscope enforcer policy on, its 6 refusals carried the attempted scope only inside client_policy_error_detail and carried no userId, sessionId, username or subject_token_client_id; switching the policy on and off produced zero admin events on REST and in the INFO log"
    source: "sdw-lab-benchmarks@91e44df t7-idp-delegation-logging/RESULTS.md:41-49, :60-61, :91-94"
    date: 2026-11-10
    revalidate: 2027-05-10
    replication: same-host
  - claim: "Keycloak's RFC 8693 delegation preview put the actor into the token (act, 9 of 9) and the event (actor, actor_id, actor_type), dropped sid from 9 of 9 delegated tokens and sessionId from the delegated exchange events, refused a second actor hop 3 of 3, and granted a delegated re-exchange with data:write that the subject token did not hold 3 of 3"
    source: "sdw-lab-benchmarks@91e44df t7-idp-delegation-logging/RESULTS.md:58, :62, :84"
    date: 2026-11-10
    revalidate: 2027-05-10
    replication: same-host
  - claim: "Mapped to OCSF 1.9.0, an IdP-events-only producer filled delegation.uid, issuer_uid and created_time on every exchange hop and parent_uid on 0 of 81; scopes and audience were on OCSF main only at the time of the run (they shipped in 1.10.0); a producer holding the subject token (the agent's own record) filled parent_uid on every hop"
    source: "sdw-lab-benchmarks@91e44df t7-idp-delegation-logging/RESULTS.md:64, :143-153"
    date: 2026-11-10
    revalidate: 2027-05-10
    replication: same-host
  - claim: "Over synthetic delegation-shaped records at 1e5 to 1e7 rows and chain depths 2 to 12, the recursive walk, a one-join parent check and a write-time materialized filter each returned exactly the planted escalation set in 18 of 18 cells in both engines and both runs, while a root-only check missed every reacquire plant (31,758 chains per run) and nothing else"
    source: "sdw-lab-benchmarks@91e44df delegation-chain-query/RESULTS.md:31-39, :66"
    date: 2026-11-09
    revalidate: 2027-05-09
    replication: same-host
  - claim: "At 1e7 rows and depth 12 the recursive walk ran in a median 1.56 to 1.70 s in DuckDB 1.5.3 and 0.87 to 0.99 s in chDB 4.4.0, the one-join check in 0.28 to 0.41 s and the materialized filter in 20 to 27 ms, on one shared host under a load average of 7.5 to 26; within-cell ratios are the defensible output"
    source: "sdw-lab-benchmarks@91e44df delegation-chain-query/RESULTS.md:11, :16, :40-50, :73-79"
    date: 2026-11-09
    revalidate: 2027-05-09
    replication: same-host
---

# Agent identity and delegation: what the agent borrows, what the token says, and what to log

Evidence tier: Mixed, with IETF and NIST standards and peer-reviewed measurement at A, two verified lab runs on one host at B, vendor documentation at B for what a feature does and C for coverage and ratio claims, two vendor-authored preprints at C, and the sizing and buy-or-enable judgements at D.

## Summary for the review

An AI agent rarely holds an identity of its own; it borrows a user's delegated grant, a workload's service account or a long-lived API key, and the record a security team would want, the agent-era analogue of a Windows 4624 logon that says "agent A acted as user U through tool T under scope S", is one that no production source I examined emits in full today. So the work starts with knowing which identities agents hold, then shortening what they hold, then assembling the partial delegation record that can be built now.

- Inventory the identities agents use (agent identities, borrowed workload identities, static secrets and delegated OAuth grants) from the IdP, cloud and code-scanning features already licensed, before buying a discovery product whose value grows with the number of sources it joins. Effort M. Tier B for the features, D for the buy threshold.
- Replace long-lived agent API keys with short-lived, audience-restricted tokens, first from the cloud's or IdP's own workload identity and token exchange, and add a broker the organization runs only where it builds its own agents on S5 to S8 and the hyperscaler's broker has been evaluated (see the sizing section). Scan code and agent configuration for the keys that remain. Effort M to L. Tier A (RFC 9700 §2.3, NIST SP 800-207 tenet 3, Meli et al. for leakage); Tier D for the broker threshold.
- Review and cut each agent identity's permissions, starting from the unused-access findings the cloud already produces (the Access Analyzer row below) and from the tools each agent can call, because the evidence below is about over-privilege. Effort M. Tier A for least privilege (NIST SP 800-207 tenet 3) and the over-privilege studies; Tier B for the feature; Tier D for the order.
- Give every agent identity a named human owner, run an offboarding query each quarter for agents whose owner has left or whose agent was deleted while its grants remain, and test once that revoking an agent's grant actually stops it. Effort S to M. Tier B for the sponsor and dormancy features below; Tier D for the cadence and the test.
- Where agents use OAuth 2.0 Token Exchange, have the agent or gateway log the id of the subject token it presented beside the IdP's event, because in lab run T7 the IdP named the issuing client on every successful hop but never the parent token, and once three agent instances shared a session nothing in the events could tell their hops apart. Effort M. Tier B, one IdP at one version.
- Evaluate scope chain-aware, each hop against its parent hop, because a root-only check missed every re-grant plant in lab run R7, and materialize the parent's effective scope at write time where the ingest path can look it up. Effort M. Tier B for the measurement, A for the attenuation property.
- Snapshot IdP authorization-policy configuration on a schedule, because a policy change produced no admin event in T7, on one IdP (Keycloak 26.8.1). Effort S. Tier B, one IdP at one version.

The delegation-record key sits at Low priority on the risk factors, not on effort: the gap it describes is internal-only, touches business data rather than credentials, is reversible by changing what gets logged, and slows one team's investigation rather than exposing the organization, so it ranks below the identity and secret keys above it.

## Why this matters

NIST SP 800-63-4 scopes itself to human users and says in §1.1 that it does "not explicitly address" machine-to-machine authentication or "access to Application Programming Interfaces (APIs) on behalf of subjects", which is the agent-delegation case (Tier A, NIST SP 800-63-4), so the identity guidance most programs are built on stops at the point where agents start. What fills the space today is a mix of OAuth practice, cloud workload identity and a vendor category that sells inventories of non-human identities, and the evidence that the underlying condition is common is now better than vendor surveys. Six of eleven models tested as LLM agents chose a higher-privilege tool when a sufficient lower one existed more than 30% of the time (Tier A, Yang et al., Findings of EMNLP 2026), 47.7% of 789 AWS Lambda applications carried excess permissions with a median of 9 granted against 1 required (Tier B, preprint arXiv 2607.02875), and secret leakage on public GitHub reached over 100,000 repositories with only 19% of leaked secrets removed after 16 days (Tier A, Meli et al., NDSS 2019, on 2017 to 2018 data from public repositories only). None of those studies measures enterprise non-human identity populations directly, and the vendor ratios of non-human to human identities (100:1, 50:1, 109:1) differ by a factor of two and show no method (Tier C, vendor homepages read 2026-11-09, bias flagged), so I would not quote a ratio to a board.

The logging gap is the part I find most interesting, because it is structural rather than a product defect. RFC 8693 represents a delegation chain inside the token as nested `act` claims of any depth, treats prior actors as "informational only" and "not to be considered in access control decisions" (§4.1), defines no per-hop scope, and says nothing about what the authorization server should log (Tier A, RFC 8693). Chan et al. treat agent identifiers, real-time monitoring and activity logging as three separate visibility measures with separate implementations (Tier A, ACM FAccT 2024), which matches what the identity-plane logs show: they record that an agent authenticated, and the reads and writes it then made live in each resource's own log.

## Token exchange, delegation and what an IdP actually records

Lab run T7 put an OAuth 2.0 Token Exchange chain (user, then agent A, then agent B, then a tool API) through Keycloak 26.8.1 in two arms, the default feature set and the RFC 8693 delegation preview, and read every event, token and admin record back (Tier B, sdw-lab-benchmarks@91e44df t7-idp-delegation-logging/RESULTS.md:26-64, one host, synthetic realm, pre-registration frozen by an agent and not owner-reviewed, verdict VERIFIED-WITH-FIXES with every scored number reproduced by a full independent re-run). The findings, each a Keycloak 26.8.1 result that another IdP may well not share:

- Every successful exchange event, and each refusal in the delegation arm, named the client the subject token was issued to (`subject_token_client_id`), and each successful one also named the id of the token it issued (`token_id`, equal to the new token's `jti`), but none named the subject token's own id, so the chain is explicit at client granularity and implicit, by session and time order, at token granularity.
- When three agent instances exchanged one user token in one session, nothing linked a hop 2 to its hop 1, and the pre-registered nearest-earlier rule attributed 5 of 15 correctly, which is the one-in-three the harness design guarantees when the events carry no disambiguating field rather than an accuracy rate. A scope-matching heuristic would have scored 15 of 15, but only because each planted chain had a distinct scope set, which real traffic does not guarantee.
- Each event carried the effective scope of the token it issued, so a re-grant inside one session was detectable from IdP events alone. A scope the user had no role for was silently dropped, though, and no field recorded what had been requested.
- With the downscope enforcer policy on, refusals named the attempted scope inside a free-text detail string and carried no user, session or chain field, so the attempt could not be attributed from the event alone. Turning that policy on and off produced no admin event, and the admin-event type list has no client-policy type, so on the surfaces checked this looks like an event kind Keycloak does not have.
- The delegation preview wrote the actor into the token (`act`) and the event, which is the audit trail the RFC describes, and in the same move dropped the session identifier from both and refused a second actor hop. The one-hop limit is an implementation choice, since §4.1 allows nesting to any depth, and the preview granted a delegated re-exchange a scope the subject token never held, which the standard permits because neither RFC 8693 nor RFC 9700 requires a delegated token's scope to be a subset of its subject token's (Tier A, RFC 8693 §5, RFC 9700 §2.3).

Two published documents speak to the same hops, and a reviewer can read an IdP's and a gateway's behaviour beside them. CoSAI's Agentic Identity and Access Management paper (Version 1.0, 20 March 2026) says MCP servers, API gateways and service meshes "SHOULD terminate and validate agent tokens" and "forward only scoped OBO credentials downstream", never raw upstream tokens, that "Decisions MUST be recorded in immutable logs" (§5.1), and that "Scope SHOULD narrow at each hop and MUST NOT expand beyond the delegating principal's effective permissions" (§3.4), which is a different test from subset-of-the-subject-token and a looser one wherever the principal holds more than the subject token carries, so a delegated scope the subject token never held can still fall inside it, and its eighth principle applies the same forwarding rule to agent-to-agent boundaries (Tier A, read at the publisher 2026-11-17). At the MCP layer, the specification's Security Best Practices page keeps the rule that "MCP servers MUST NOT accept any tokens that were not explicitly issued for the MCP server", a rule that binds MCP servers rather than IdPs and restates for MCP the RFC 9700 §2.3 requirement that a resource server refuse a token not meant for it, which closes the token-passthrough form of the problem at the protocol boundary and leaves the server's own downstream credentials as the thing to record (Tier A, version 2026-07-28, read 2026-11-17; [mcp-servers-and-manifest-drift.md](mcp-servers-and-manifest-drift.md) covers the rest of that page).

The academic record lines up with this without adding an independent measurement. A Splunk and Cisco preprint shows on synthetic workloads that audit logs and traces can be identical under incompatible delegation assignments and that time-window reconstruction degrades once more than about a fifth of delegations overlap (Tier C, Mishra and Sharad, arXiv 2606.09692, vendor-authored, bias flagged), and Nian et al. call cross-chain attribution in multi-agent systems "largely open" (Tier B, preprint arXiv 2604.05485). OAuch found that the average deployed IdP omits about a third of OAuth security specifications, though it did not test token exchange (Tier A, Philippaerts et al., RAID 2022), which I read as a reason to repeat T7 on a second IdP rather than generalize from Keycloak.

## Why chain-aware evaluation, and what it costs

Lab run R7 asked what it costs to evaluate scope across a delegation chain at query time (Tier B, sdw-lab-benchmarks@91e44df delegation-chain-query/RESULTS.md:31-56, synthetic integer-keyed records, one shared host, agent-frozen pre-registration, VERIFIED-WITH-FIXES). It planted one escalation in 1% of chains and compared four checks. The recursive walk, a one-join check of each hop against its parent and a filter on a write-time materialized parent-scope column each returned exactly the planted set in 18 of 18 cells, in DuckDB 1.5.3 and chDB 4.4.0 and in both runs, while the root-only check, which compares each hop with the human root's authority, missed every `reacquire` plant and nothing else. A hop that re-grants authority an intermediate agent had already dropped stays inside the root's authority, so a root-only check cannot see it, and T7 restated the same result on real Keycloak fields (5 of 5 re-grants caught chain-aware, 0 of 5 root-only). The per-cell recall of the root-only check (0.55 to 0.67 in the larger cells) is set by the generator's plant mix, so it shows the blind spot exists and says nothing about how often re-grants happen in real agent traffic.

The cost side favours not walking. At 1e7 rows and depth 12 the walk took a median 1.56 to 1.70 s in DuckDB and 0.87 to 0.99 s in chDB, the one-join check 0.28 to 0.41 s, and the materialized filter 20 to 27 ms, which is answer-identical to the walk. Those absolute numbers were taken under a load average of 7.5 to 26 from other work on the host, the pre-registered depth hypothesis was falsified for DuckDB, and the cost of looking up the parent's scope at ingest was not measured, so the defensible reading is the within-cell ratio and the design consequence: the cheap checks are exact only when each hop's record carries its own granted scopes and a pointer to its parent. Monotonic attenuation at each hop is old and peer-reviewed as a property, being the defining property of macaroons (Tier A, Birgisson et al., NDSS 2014, largely Google-authored), but I should say plainly that asking for per-hop scopes plus a parent pointer goes beyond what RFC 8693 asks for, and a vendor that follows the RFC to the letter has a documented reason not to evaluate the chain in access decisions.

## What to log, field by field

The record below is what I would ask each hop to produce, mapped to OCSF where an attribute exists. T7 validated these attribute names against the 1.9.0 schema; in 1.9.0 the `delegation` object reaches the authentication class only through the `ai_operation` profile, and `scopes`, `audience` and `expiration_time`, which T7 found only on OCSF main (Tier B, T7 RESULTS, OCSF mapping section), shipped in the 1.10.0 release of 2026-11-20 (Tier A, OCSF 1.10.0 release notes, #1705, and `objects/delegation.json` at the release commit `2d20903`, read 2026-11-24), so a pipeline on 1.10.0 can type them.

| Field | OCSF 1.9.0 (1.10.0 where it differs) | Who can fill it today | Note |
|---|---|---|---|
| Hop id (issued token id) | `delegation.uid` | The IdP, on every exchange in T7 | Keycloak `token_id` |
| Parent hop id | `delegation.parent_uid` | The agent or gateway that presented the subject token; the IdP in 0 of 81 hops in T7 | The single most useful field to add |
| Issuer | `delegation.issuer_uid` | The IdP | Realm or tenant issuer |
| Time | `delegation.created_time` | The IdP | Clock-sync the agent and IdP |
| Granted scopes | not in 1.9.0; `delegation.scopes` in 1.10.0 | The IdP, effective scope per hop in T7 | Map to `delegation.scopes` on 1.10.0; carry in `unmapped` only while the pipeline is still on 1.9.0 |
| Requested scopes | none | Nobody in T7; the enforcer refusal string only | Needed to see attempts the IdP silently trimmed |
| Audience | not in 1.9.0; `delegation.audience` in 1.10.0 | The IdP | Resource the hop is for |
| Acting agent | `actor.app_name` | The IdP (requesting client) | `act` claim in delegation mode |
| Human subject | `user` | The IdP on success; absent on enforcer refusals in T7 | Refusals then fail the class's required `user` |
| Session | `actor.session` (my mapping, not validated in T7) | The IdP in the default arm; dropped in Keycloak's delegation preview | Do not rely on it as the chain key |

Beyond the per-hop record, two more things belong in the store. The first is the IdP's configuration of exchange and scope policy, captured on a schedule and diffed, since T7 found no admin event for a policy change. The second is the downstream activity, which stays in each resource's own log under the application or agent id. The join from "granted in March" to "read the mailbox in October" is assembled there, by matching the grant's client id to the resource log, and no identity-plane source I read records it as a grant id (Tier B, vendor documentation read 2026-11-09).

## Turn on before you buy

Much of the inventory and posture half of the non-human identity category is available per platform from licences many organizations already hold, while the cross-platform join is what no incumbent sells and the per-hop delegation record, with each hop's scopes and a pointer to its parent, is something I found documented by no commercial product on its public pages (Tier B for what the pages say, read 2026-11-09 for twelve NHI and agent-identity vendors and six incumbents; Tier D for the absence, since three portals were gated and a search of vendor pages is not a complete catalogue). The nearest documented record is Aembit's: its pages say every access event carries both the user and the AI agent with the resource and the policy outcome, and its authorization event carries an `authorizationChain` described as "an ordered list of context IDs that identify the authorization decisions behind a request", though neither page mentions scopes or a parent token (Tier B, Aembit blended-identity and access-authorization-event pages, read 2026-11-24). Research prototypes carry parts of it, AIP most completely with one attenuating Biscuit block per hop and the parent implied by block order (Tier B, preprint arXiv 2603.24775).

| Platform family | Setting | Default | Where the record lands | last-checked |
|---|---|---|---|---|
| AWS IAM Access Analyzer | Unused access analysis (roles, access keys, passwords, unused services and actions) | Runs once an unused-access analyzer is created; charged per IAM role and user analyzed per analyzer per month | Access Analyzer findings | 2026-11-09 |
| AWS Bedrock AgentCore | CloudTrail data events for WorkloadIdentity, WorkloadIdentityDirectory and TokenVault | Off; billed when enabled | CloudTrail trail or lake the customer configures | 2026-11-09 |
| Microsoft Entra Agent ID | Agent identities with sponsors; agent sign-in and audit logs | Platform available to all Entra customers; Entra security features for agents need Microsoft Agent 365, which is included in Microsoft 365 E7 and sold as an add-on to E5, A5 and Business Premium (Microsoft Learn, "What is Microsoft Entra Agent ID?", ms.date 2026-04-14, read 2026-11-24) | Entra sign-in and audit logs (authentication events, not downstream activity) | 2026-11-09 |
| Okta ISPM | Dormant-account detection across human and non-human identities | 90-day dormancy threshold as documented | Okta ISPM findings | 2026-11-09 |

The rows say what the vendor documents and not how well it works; the Entra overview's line that "all agent authentication and activity is logged" is true at the identity plane for Entra-identified agents, and agents admitted through neither the Entra ID Auth SDK sidecar nor workload identity federation, such as a framework agent nobody federated, are outside it by Microsoft's own documentation (Tier B, vendor documentation read 2026-11-09).

On sizing, my judgement (Tier D, 2026-11-10) is that an organization on one cloud and one IdP gets most of the inventory from the rows above and should route their findings to a store it owns before evaluating a discovery product, and that a broker is worth its cost only where the organization builds its own agents on S5 to S8, after the hyperscaler's own broker has been evaluated. A large organization with several clouds, IdPs and hundreds of SaaS tenants has a join large enough to buy, and I would write three conditions into the contract: export of the inventory and findings in a documented schema (ask for the OCSF `actor`, `ai_agent` and `delegation` mappings and expect "not yet"), a one-year term, given that five of the twelve vendors I profiled changed hands between June and September 2026 (Tier C, press and vendor releases), and a review of the per-connector permission manifest before anything is connected, because the discovery tool may be the most privileged non-human identity the organization adds that year.

## Secrets in agent and tool configuration

The keys that survive the move to short-lived tokens tend to sit in configuration rather than code, and the place differs by surface (Tier D for the grouping). On S4 and S5 they sit in the coding agent's or MCP client's configuration, where a server entry can carry a literal token in its environment block or arguments, or a reference to an environment variable or a secret manager; the repo's `mcp_config` reducer counts literal secrets separately from references, and a reference is the better state, because the secret then rotates in one place and stays out of anything that copies the file. On S6 they sit in the builder's credential store, which `stubs/agent-builders.md` covers, and on S8 they are the application's provider keys and the gateway's upstream keys, which `ai-apis-and-the-gateway.md` treats as a crown-jewel store. Vendor OAuth grants an agent holds are the delegated form of the same thing and belong in the inventory beside the static keys. Whatever form a secret takes, it needs an owner, a rotation date and a revocation path that someone has exercised, and secret scanning should read the agent and MCP configuration paths as well as repositories (Tier A for leakage and slow removal, Meli et al.; Tier D for the per-surface reading).

## Owners, offboarding and revocation

An agent identity outlives the project that made it more easily than a person's does, because nobody leaves the company when an agent stops being used. Entra Agent ID's sponsors and Okta ISPM's dormancy detection, in the table above, give a per-platform owner field and an inactivity signal, and the builders stub records, for Google Cloud Agent Identity, IAM bindings that remain as inactive grants after the agent is deleted, so the quarterly query is a join of agent identities and their grants against the owner directory and against recent activity (Tier B for the features, D for the query). Revocation is the part I would test rather than assume: revoke one agent's grant in a test tenant, confirm the next call fails, and confirm how long an already-issued token keeps working, since a short-lived token is what makes revocation take effect quickly. Step-up approval for an agent's high-impact actions belongs with the approval caveat in `decision-sequence.md` (row 6), and I have not analysed it here.

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
- **Gap: the full join in production**. No production source examined carries agent, user, tool and scope per action; Aembit's documented event comes closest, with user, agent, resource and outcome but no scope. **Needs**: a vendor or platform record that does, verified against its documentation and a captured event.
- **Gap: revocation latency**. How long an issued agent token keeps working after its grant is revoked is unmeasured here. **Needs**: a revoke-and-retry test on at least two IdPs.

## Notes

- Decision 16 choices: the T7 counts are quoted per arm because the arms used different login grants; the R7 latency ranges are given across both runs because the pre-registered single-run thresholds were unstable under load.
- The vendor rows and the "no commercial product documents a per-hop record" sentence come from a documentation read of 2026-11-09 in which three vendors' documentation portals were gated, so their export schemas could not be checked. Aembit's documentation was read on 2026-11-24 to check that sentence: the access-authorization-event page lists the event's fields, including `authorizationChain`, and the blended-identity page says each access event carries the user and the agent, and neither documents per-hop scopes or a parent token, so the sentence stands with Aembit named as the nearest case. I did not find a "chain step" attribute under that name on those pages.
- R7's attribute names were its own and were not checked against OCSF 1.9.0; the field table above uses T7's validated names instead.
- 2026-11-17: the CoSAI Agentic IAM and MCP Security Best Practices citations were added from readings at each publisher; they change no lab number, grade or signal. The IAM paper is graded A on the same basis `SOURCES.md` grades CoSAI's AI Incident Response Framework V1.0, an approved version 1.0 from an OASIS Open project, and its forwarding rule is a SHOULD, not a MUST.
- 2026-11-22: the CoSAI and MCP paragraph's lead was corrected, since §3.4's MUST NOT is measured against the delegating principal's effective permissions rather than the subject token and the MCP rule binds servers and restates RFC 9700 §2.3; §5.1's subject is MCP servers, API gateways and service meshes. No lab number, grade or signal changed.
- 2026-11-24: the broker advice in the Summary was conditioned on the sizing section, and actions for privilege reduction and for owners, offboarding and revocation were added with two short sections, because the evidence in "Why this matters" is about over-privilege and `decision-sequence.md` assigns small organizations quarterly agent offboarding queries that route here. The two documents added on 2026-11-17 were pinned, and the delegation-record priority reason was restated against the four risk factors. The `replication` value on every measurement claim is `same-host`, because each run's verifier re-ran it on the original host.
- 2026-11-24: OCSF 1.10.0 (release tag `1.10` at `2d20903`, published 2026-11-20) carries `delegation.scopes`, `audience` and `expiration_time`, so the field table maps scopes and audience to them and the carry-in-`unmapped` advice now applies only to pipelines still on 1.9.0; T7's validation stays a 1.9.0 result.
- Both lab runs carry an independent verification with the verdict VERIFIED-WITH-FIXES; T7's verification included a cross-provider leg and R7's record names none. The pre-registrations were frozen by an agent before each run and were not owner-reviewed.

## Sources

Tier A

- IETF RFC 8693, OAuth 2.0 Token Exchange, 2020, https://www.rfc-editor.org/rfc/rfc8693, §4.1 and §5, read 2026-11-09.
- IETF RFC 9700, Best Current Practice for OAuth 2.0 Security, 2025, https://www.rfc-editor.org/rfc/rfc9700, §2.3 and §4.10.1, read 2026-11-09.
- Coalition for Secure AI (an OASIS Open project), Workstream 4, "Agentic Identity and Access Management", Version 1.0, 20 March 2026, https://www.coalitionforsecureai.org/wp-content/uploads/2026/04/agentic-identity-and-access-control.pdf, §1.2 principle 8, §3.4 and §5.1, read 2026-11-17.
- Model Context Protocol, Security Best Practices, version 2026-07-28, Token Passthrough, https://modelcontextprotocol.io/specification/2026-07-28/basic/security_best_practices, read 2026-11-17.
- NIST SP 800-207, Zero Trust Architecture, 2020, https://doi.org/10.6028/NIST.SP.800-207, §2.1 (tenet 3, "Access should also be granted with the least privileges needed to complete the task", read in the PDF at nvlpubs.nist.gov on 2026-11-24).
- OCSF schema 1.10.0, release "1.10" (https://github.com/ocsf/ocsf-schema/releases/tag/1.10, commit `2d20903`), release notes and `objects/delegation.json`, read 2026-11-24.
- NIST SP 800-63-4, Digital Identity Guidelines, 2025, https://doi.org/10.6028/NIST.SP.800-63-4, §1.1.
- Meli, McNiece, Reaves, "How Bad Can It Git? Characterizing Secret Leakage in Public GitHub Repositories", NDSS 2019, https://doi.org/10.14722/ndss.2019.23418.
- Birgisson et al., "Macaroons: Cookies with Contextual Caveats for Decentralized Authorization in the Cloud", NDSS 2014, https://doi.org/10.14722/ndss.2014.23212 (largely Google-authored).
- Philippaerts, Preuveneers, Joosen, "OAuch: Exploring Security Compliance in the OAuth 2.0 Ecosystem", RAID 2022, https://doi.org/10.1145/3545948.3545955.
- Chan et al., "Visibility into AI Agents", ACM FAccT 2024, https://doi.org/10.1145/3630106.3658948.
- Yang et al., "When Lower Privileges Suffice: Investigating Over-Privileged Tool Selection in LLM Agents", Findings of EMNLP 2026, https://doi.org/10.18653/2026.findings-emnlp.2059.

Tier B

- sdw-lab-benchmarks@91e44df t7-idp-delegation-logging (RESULTS.md, VERIFICATION.md; lab master), run 2026-11-10, https://github.com/flying-coyote/sdw-lab-benchmarks/tree/91e44df/t7-idp-delegation-logging.
- sdw-lab-benchmarks@91e44df delegation-chain-query (RESULTS.md, VERIFICATION.md; lab master), run 2026-11-09, same repository.
- Yeboah-Duako, Datta, "Permissions on the Loose: Measuring Overprivilege in Real-World Serverless Applications", preprint, 2026, https://arxiv.org/abs/2607.02875.
- Nian et al., "Auditable Agents", preprint, 2026, https://arxiv.org/abs/2604.05485.
- Prakash, "AIP: Agent Identity Protocol for Verifiable Delegation Across MCP and A2A", preprint, 2026, https://arxiv.org/abs/2603.24775.
- Microsoft Learn, Microsoft Entra Agent ID overview (updated 2026-08-13) and agent ID Governance (updated 2026-11-07), read 2026-11-09.
- AWS documentation, IAM Access Analyzer unused access analysis and Bedrock AgentCore CloudTrail data events, read 2026-11-09.
- Okta Identity Security Posture Management product page (undated), read 2026-11-09.
- Aembit documentation, "Access authorization events", https://docs.aembit.io/user-guide/audit-report/access-authorization-events, and "Blended identity", https://docs.aembit.io/user-guide/access-policies/blended-identity/, read 2026-11-24 (what the event records; nothing here grades how well it works).

Tier C

- Mishra, Sharad, "Observability for Delegated Execution in Agentic AI Systems", preprint, 2026, https://arxiv.org/abs/2606.09692 (Splunk and Cisco authors, bias flagged).
- Dantuluri, Sundi, "Delegation Without Trust", preprint, 2026, https://arxiv.org/abs/2609.00267 (VotalAI authors, bias flagged).
- Vendor homepages and releases for non-human-to-human identity ratios and acquisitions (Astrix, Token Security, Palo Alto Networks Idira, Cyera, SailPoint, Cisco, Snowflake, Okta), read 2026-11-09.
