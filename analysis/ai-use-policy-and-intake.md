---
evidence-tier: Mixed
convergence: single-source
applies-to-signals: [ai-aup-absent, ai-tool-intake-absent, ai-owner-unnamed]
surfaces: [S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12, S13]
pins:
  - "NIST AI RMF 1.0"
  - "ISO/IEC 42001 2023"
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-03-10
status: EMERGING
---

# AI use policy and intake: the first controls for most organizations

Evidence tier: Mixed. The structure is Tier A, because NIST AI RMF 1.0 and ISO/IEC 42001:2023 both open AI risk management with policy, inventory and accountability; the supporting figures are Tier A (one SEC filing), Tier B (a preprint interview study) and Tier C (one vendor-sponsored survey, flagged); the small-organization template and the ordering argument are Tier D, the author's judgement.

## Summary for the review

For most organizations the first AI controls are an owner, an acceptable-use policy, an approved-tools list, an intake path that every new AI tool passes through, and a page of staff guidance, and telemetry comes after them, because a collection plan needs the approved list to know what it is collecting and a finding needs an owner to go to. The intake path is also where the configure-before-you-buy check runs, so it is the cheapest point at which to catch a purchase the organization already owns.

1. Name one accountable owner for AI use and open a risk-register entry. Effort S. Tier A for the structure (NIST AI RMF 1.0 GOVERN 2.1 and 2.3; ISO/IEC 42001 clause 5.3).
2. Write a one-page acceptable-use policy that says which data classes may go into which class of tool. Effort S. Tier A that a policy is expected (GOVERN 1; clause 5.2); Tier D for the content.
3. Keep an approved-tools list keyed to deployment classes, with an owner and a re-review date per row. Effort S. Tier A for the inventory duty (GOVERN 1.6); Tier D for the shape.
4. Stand up an intake path: one form, one reviewer, a stated turnaround, and a fixed set of checks, including whether an owned platform already covers the need and the five-state check (enabled, scoped, exported, alerted, owned) on whatever it would rely on. Effort M. Tier A for third-party structure (GOVERN 6.1); Tier D for the form.
5. Give staff a short guidance page and collect an acknowledgement, which in the US also serves as monitoring notice. Effort S. Tier A for the statute, Tier B for how courts and counsel read it.
6. Review the policy and the list on a cadence, and re-run intake when a listed tool changes plan, terms or default settings. Effort S. Tier A for the review duty (GOVERN 1.5).

Nothing here is measured, and I have found no study showing that a policy reduces AI incidents, which is the first gap below.

## Why this matters

The team this document is written for did not choose most of its AI surface. The assistant arrived with the productivity suite, the coding agents arrived with the developers, a managed model platform arrived with the first product team that wanted to ship a feature, and somewhere among the SaaS applications already under contract there are AI features a vendor switched on server-side without asking. An interview study of 27 Australian critical-infrastructure organizations found exactly that pattern, with vendors "effectively turning [features] on" in enterprise tools without a risk assessment (Tier B, Chhetri et al., arXiv 2606.00088, preprint). So the first question for a small or mid-sized organization is less about which AI security product to buy and more about who decides what is in use, on what terms, and where a finding goes once someone has one.

The public record says the decision layer is often missing. IBM's 2025 Cost of a Data Breach study reports that 63 percent of the 600 breached organizations it studied "lacked AI governance policies" and that one in five had a breach linked to shadow AI (Tier C, IBM and Ponemon survey of breached organizations, self-reported, bias flagged because IBM sells the services the report recommends; read 2026-11-10). I would use that figure for the shape of the gap and nothing finer, since a survey of breached organizations cannot say whether a policy would have prevented the breach. The sharper case is a Tier A one: a US bank holding company filed a Form 8-K under Item 1.05 in May 2026 after customer names, Social Security numbers and dates of birth were disclosed through "an unauthorized artificial intelligence-based software application", which it learned of on 2026-05-05, in a report dated 2026-05-07 and signed 2026-05-11 (Tier A, SEC filing, read 2026-11-10). "Unauthorized" presupposes a list of what is authorized, and the list is the control this document is about.

There is also an ordering reason. Telemetry for AI is a per-product decision, because the administrative audit trail usually ships on by default while the content channel (prompt, tool call, answer) sits behind a separate toggle or licence line, usually off (see [telemetry-by-surface.md](telemetry-by-surface.md) for the dated rows). Each sanctioned product therefore brings at least two records to find, configure, route and retain, so the number of products on the approved list sets the size of the logging project. Writing the list first keeps that project finite.

## What the standards ask, and what the intake path checks

### The structure both standards share

NIST AI RMF 1.0 makes Govern a cross-cutting function whose six categories run from policy and accountability through workforce diversity, culture and engagement to third-party risk (Tier A, NIST AI 100-1, January 2023; subcategory text read on the NIST AI Resource Center, 2026-11-10, which notes the framework is being updated). ISO/IEC 42001:2023 follows the harmonized management-system structure, so its policy, roles, competence and awareness duties sit in the same clause numbers as other ISO management-system standards (Tier A for the clause structure). The Annex A control numbers below were read through secondary summaries rather than the purchased text, which is why they carry a qualifier and a gap.

| Element | NIST AI RMF 1.0 (Govern) | ISO/IEC 42001:2023 | What a small organization writes |
|---|---|---|---|
| Policy | GOVERN 1, 1.2, 1.4 (risk management "established through transparent policies") | Clause 5.2 AI policy; Annex A.2 (secondary) | The one-page acceptable-use policy |
| Legal context | GOVERN 1.1 ("legal and regulatory requirements involving AI are understood, managed, and documented") | Clause 4.1 context | One line per jurisdiction where staff work |
| Inventory | GOVERN 1.6 ("mechanisms are in place to inventory AI systems") | Annex A.4 resources (secondary) | The approved-tools list |
| Retirement | GOVERN 1.7 (decommissioning and phasing out) | Annex A.6 life cycle (secondary) | A re-review date on every row |
| Accountability | GOVERN 2.1 (roles and responsibilities documented), 2.3 (executive leadership takes responsibility) | Clause 5.3 roles; Annex A.3.2 (secondary) | A named owner and a risk-register entry |
| Training | GOVERN 2.2 (personnel and partners receive AI risk management training) | Clauses 7.2 competence, 7.3 awareness | The staff guidance page |
| Third parties | GOVERN 6.1 (policies for third-party AI risk), 6.2 (contingency for third-party failures) | Annex A.10 (secondary) | The vendor-terms questions in intake |
| Review | GOVERN 1.5 (ongoing monitoring and periodic review planned) | Annex A.2.4 policy review (secondary) | A quarterly calendar item |

The two standards agree closely enough that I would not pick one for structure. An organization working toward a 42001 certification will need the full management system; an organization that just wants the first controls can take the left-hand column of this table as the checklist and treat the rest of the framework as where it goes next.

### The intake path

The intake path is the one control in this document that does work beyond writing things down, because it runs a fixed set of checks on every new tool before anyone depends on it. I would keep it to one short form and one reviewer, since an intake that takes weeks is an intake people route around, and the routing-around is the shadow-AI problem [inventory-and-shadow-ai.md](inventory-and-shadow-ai.md) then has to clean up. The checks, in order:

1. What is it, and which deployment class does it fall in (an enterprise assistant, a managed model platform, a coding agent, a direct API key, an AI feature inside a SaaS product, a local model)? The class decides which later documents apply.
2. Which data classes would go into it, against the acceptable-use policy's table.
3. Does something the organization already licenses cover the need, and if so, would configuring it be enough? This is the configure-before-you-buy check, and [configure-before-you-buy.md](configure-before-you-buy.md) carries the method.
4. For the record the decision would rely on, whether that is the new tool's own audit log or an owned feature that would watch it, where does it sit on the five-state check below?
5. What do the vendor's terms say about training on customer data, retention, subprocessors, which plan tier carries the audit log, and whether AI features ship on by default? [saas-embedded-ai-and-vendor-terms.md](saas-embedded-ai-and-vendor-terms.md) carries the questions.
6. Decide: add to the approved list with an owner and a re-review date, approve with written conditions, or decline and name the alternative.

The five-state check comes from the author's method for auditing owned features, where a feature that is enabled is not yet a control because each later state is a place the record can stop before it reaches a defender (Tier D, the author's analysis; a partial state is recorded with its coverage fraction, the way Microsoft's Secure Score awards partial points per protected user, Tier B for what that feature does).

| State | Question | A typical failure |
|---|---|---|
| Enabled | Is the toggle, policy or diagnostic setting on, as of a date? | The content channel exists and is off by default |
| Scoped | Does it cover the users, devices, accounts and regions that matter? | Logging covers one API endpoint and skips another |
| Exported | Does the record leave the vendor's retention window for a store the organization owns? | The vendor keeps 30 to 180 days and nobody pulls it |
| Alerted | Does a detection or review consume it, tested against a planted event on a known date? | A rule exists and has never fired here |
| Owned | Does a named role own the configuration and the response, recorded where a successor will find it? | One person understands it and nobody else |

A feature's grade is the highest state at which every earlier state is yes, so a record that is exported but not scoped scores at enabled. That looks harsh, and I think it should, because "we have the logs" usually turns out to mean some users, some endpoints, landing in a vendor's 30-day window, and the intake form is where that gets written down before a tool is approved on the strength of it.

### A small-organization template (Tier D)

This is my sketch of the minimum for an organization of roughly 200 to 2,000 people with a security team of two to eight and most of its AI rented, offered as a starting point to edit rather than as a finding. The acceptable-use policy fits on one page and carries four things:

- a table of data classes (public, internal, confidential, regulated personal data, credentials and secrets) against tool classes (approved enterprise tools with a signed agreement, approved consumer-grade tools, anything else), with each cell marked allowed, allowed with conditions, or not allowed;
- the approved-tools list by reference, so the policy does not need re-approval every time the list changes;
- a sentence saying that credentials, secrets and regulated personal data do not go into any tool outside the approved enterprise set, with the reason in one line;
- how to ask for a new tool, and how to report a mistake without penalty for reporting it.

The approved-tools list is a table with a row per product: deployment class, the data classes allowed, the plan tier held, whether the content channel is on, the owner, and the next re-review date. The intake form asks the six questions above and records the answer to each. The staff guidance is a page of examples, including what not to paste and what to do when an existing tool grows a new AI feature, and the acknowledgement is collected once at onboarding and again when the policy changes materially.

The ordering argument is also mine. I would put these ahead of telemetry because the first 90 days of almost any AI security plan are spent deciding scope, inventorying what is held and switching on what is already paid for, and each of those steps needs the approved list as its input. A team of two to eight people cannot run that inventory against everything in use, so the list is what makes the inventory finite.

## What this does not mean

A policy is not a control in the sense the rest of this repo uses the word, because nothing in it produces a record or blocks an action. It sets the scope, the owner and the terms, and the controls that enforce it (consent-grant reviews, endpoint queries, gateway keys, coding-agent managed settings) are covered in their own documents. I would say so plainly in the risk register so nobody reads a signed policy as coverage.

Intake does not reach AI that arrives without a request. A SaaS vendor that switches on an AI feature server-side never sends an intake form, so the quarterly toggle review and the renewal questions in [saas-embedded-ai-and-vendor-terms.md](saas-embedded-ai-and-vendor-terms.md) are the counterpart for that surface, and the approved list should carry those features as rows once the review finds them.

An approved list that is too short becomes a list people route around. The friction is real, and I would rather approve a consumer-grade tool with conditions on data classes than decline it and push the use somewhere the organization cannot see.

An acknowledged policy is not a sufficient basis for capturing employee prompts everywhere. In the US the federal Wiretap Act permits interception where a party has given prior consent (Tier A, 18 U.S.C. §2511(2)(d)), and an acceptable-use policy acknowledged at hire is routinely treated as that consent, with several states adding written-notice duties (Tier B, law-firm summaries); in the EU, necessity is read with data minimisation and works councils in several member states must agree before a monitoring-capable record goes in, so the same acknowledgement does much less there. [prompt-capture-and-the-law.md](prompt-capture-and-the-law.md) carries the detail. This is not legal advice.

A larger organization with an established third-party risk and architecture-review process should fold AI intake into those processes rather than build a parallel one. The checks above are what the existing review needs to add, and a second queue mostly adds a second place for requests to stall.

## Gaps

- **Gap: policy efficacy**. No study I found measures whether an acceptable-use policy or an intake path reduces shadow-AI use or AI-linked incidents; the IBM figure is a cross-sectional survey of breached organizations and cannot carry a causal claim. **Needs**: a before-and-after measurement of discovered unsanctioned AI use (from the consent-grant, endpoint and expense signals the shadow-AI document describes) in organizations that adopt a policy and intake path, against ones that do not.
- **Gap: the configure-first premise**. The practitioner view that most of what AI security needs is already licensed and left unconfigured is the author's stated observation (Tier D), and no public survey measures it. **Needs**: the published configuration worksheet filled in by readers and aggregated, which is a study rather than a lab bench.
- **Gap: ISO/IEC 42001 Annex A numbering**. The Annex A control numbers here were read through secondary summaries, which disagree with each other in places. **Needs**: a read of the purchased standard text to confirm each control number and title.
- **Gap: intake turnaround**. There is no evidence for how long an intake path can take before staff route around it. **Needs**: practitioner reports or a small survey of intake turnaround against discovered shadow use.

## Notes

- Convergence stays `single-source`. Both standards prescribe the policy and accountability elements, so the standards route under Decision 7 may apply to those two, but I have not documented an independent implementation record for this document, and the intake path and template are not prescribed by either standard in this form. The claim-level choice (Decision 16) is that the structure is cited at Tier A and every content recommendation at Tier D.
- `revalidate-by` is four months out rather than six because NIST's own resource page says AI RMF 1.0 is being updated, and a revised Govern function would reopen the table.
- No `measurement-claims` rows: nothing in this document is a re-runnable lab result.
- Dated judgement markers, 2026-11-10: the ordering of policy before telemetry, the six-question intake form, the small-organization template and the advice to approve with conditions rather than decline are the author's judgement.

## Sources

Tier A

- NIST, Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1, January 2023, https://doi.org/10.6028/NIST.AI.100-1; Govern subcategory text read at https://airc.nist.gov/airmf-resources/airmf/5-sec-core/ on 2026-11-10.
- ISO/IEC 42001:2023, Information technology, Artificial intelligence, Management system, https://www.iso.org/standard/42001 (clause structure; Annex A numbering via the secondary summaries below, see Gaps).
- CB Financial Services, Inc., Form 8-K, Item 1.05, date of report 2026-05-07, https://www.sec.gov/Archives/edgar/data/1605301/000160530126000021/cbfv-20260507.htm, read 2026-11-10.
- 18 U.S.C. §2511(2)(d), https://www.law.cornell.edu/uscode/text/18/2511.

Tier B

- Chhetri et al., interview study of 27 Australian critical-infrastructure organizations on AI adoption, arXiv 2606.00088, preprint.
- Microsoft, Microsoft Secure Score documentation, https://learn.microsoft.com/en-us/defender-xdr/microsoft-secure-score (what the partial-credit scoring does).
- Secondary summaries of ISO/IEC 42001 Annex A, used for control numbers only: https://docs.modulos.ai/frameworks/iso-42001/annexes-a-d.html and https://riskprofs.com/iso-42001-annex-a-controls-list/, read 2026-11-10 (vendor and consultancy pages; they disagree on some details).

Tier C

- IBM, "What data leaders need to know from the Cost of a Data Breach Report 2025", published 2025-11-12, https://www.ibm.com/think/insights/data-matters/cost-of-a-data-breach, read 2026-11-10 (IBM and Ponemon survey of 600 breached organizations; bias flagged).

Tier D

- The author's configure-first method (inventory, five-state audit, coverage grading, then turn on, evaluate, buy, build) and the small-organization template above, 2026-11.
