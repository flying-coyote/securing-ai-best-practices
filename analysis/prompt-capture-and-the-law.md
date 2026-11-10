---
evidence-tier: Mixed
convergence: single-source
applies-to-signals: [prompt-capture-tier-none, prompt-capture-tier-metadata, prompt-capture-tier-hash, prompt-capture-tier-delta, prompt-capture-tier-full, jurisdiction-eu, jurisdiction-us, jurisdiction-uk, jurisdiction-other, dpia-absent, works-council-unconsulted]
surfaces: [S2, S3, S4, S5, S7, S8, S13]
pins:
  - "GDPR Regulation (EU) 2016/679, consolidated text"
  - "AI Act Regulation (EU) 2024/1689 as amended by (EU) 2026/1744, consolidated CELEX 02024R1689-20260727"
  - "NIS2 Directive (EU) 2022/2555"
  - "DORA Regulation (EU) 2022/2554 and Commission Delegated Regulation (EU) 2024/1774"
  - "ePrivacy Directive 2002/58/EC, consolidated 2009-12-19"
  - "UK Data (Use and Access) Act 2025, s. 70 and Sch. 4"
  - "18 U.S.C. §2511, as read 2026-11-09"
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-04-10
status: EMERGING
---

# Prompt capture and the law: EU conditions, the AI Act's reach, and a US section

Evidence tier: Mixed. Statute, regulation and court text read at the primary are Tier A, regulator guidance and EDPB documents are Tier B, law-firm and press summaries used where a primary would not load are Tier B/C and flagged inline, and every cell of the decision table and every viability condition is Tier D, my synthesis.

## Summary for the review

This is not legal advice. It sorts the law by the questions a telemetry engineer asks, and a real deployment needs a privacy lawyer and, in much of Europe, a works council before it goes live. In the EU, capturing prompts for security is lawful under conditions, and an organization that switches on a vendor's content channel and lands the text in a SIEM under a general "security monitoring" purpose is probably in breach on several counts at once.

- Write down a security-only purpose and enforce the wall between the security store and HR or adoption analytics with access control (S, Tier A statute, B regulator).
- Keep metadata and a keyed hash by default, and write prompt text only when a detector, guardrail or incident opens it (M, Tier B regulator guidance, D for the tier mapping).
- Prefer a control that refuses the action, and log the refusal, over logging content for later review (M, Tier B).
- Set retention per tier, text inside the incident window and metadata inside the six-to-twelve-month band one regulator calls sufficient (S, Tier B).
- Do a DPIA before switch-on that names tiers, triggers, retention, roles and the special-category residue (M, Tier A statute, B guidance).
- Agree the design with the works council wherever national law requires it (L, Tier A statute).
- Tell users at the point of use what is logged, at which tier and for how long (S, Tier A).

The AI Act's logging duties reach only high-risk systems, so a general coding or chat assistant carries no AI Act duty to log prompts. NIS2 and DORA justify the metadata tier for regulated entities and say nothing about prompt text. Where the people in scope work only in the United States, this document is EU-first, and its US section names the federal wiretap rule and three state notice statutes and lists, for counsel, the state wiretap, privacy, sector and litigation questions it does not answer.

## Why this matters

Many AI platforms ship with the content channel off (the dated default-state table is in `telemetry-by-surface.md`), so a team deciding to capture prompts is making a legal choice as much as an engineering one. The cost arithmetic per tier lives in `what-to-log-and-what-it-costs.md`, and this document uses its four capture tiers under short labels. T0 is that document's metadata tier (identity, model, tool, token counts, timestamps); T1 is its hash tier, which I take to mean a keyed hash (HMAC) of prompt and response; T2 is its delta tier, the text each request added; T3 is its full tier, the whole context as sent on every request. A `none` answer raises no capture question but leaves an incident with no record, which is an evidence gap rather than a legal finding.

Purpose comes first (GDPR Art. 5(1)(b), Tier A), and most security purposes do not need the text. Identity, cost and capacity questions are T0, tamper evidence is T1, reconstructing an agent's actions needs T0 plus tool-call arguments; prompt-injection forensics needs the retrieved content that carried the injection, which is T2 on a trigger. The purpose that needs a human's own words is insider misuse, which regulators treat as employee monitoring rather than network security. A T2 capture on an injection trigger routed to the incident team reads as security processing, while the same store read by a manager is a purpose change, and the CNIL's logging recommendation says re-use "for purposes other than securing the processing is liable to constitute a misuse of purpose" (délibération 2021-122, para. 11, my translation; Tier B).

Tool-call arguments are content too, since they carry file paths, shell commands and SQL, and one study found file paths in 72% of 25 public log datasets while 7% of the anonymization literature discusses them (Aghili, Li and Khomh, FSE 2025, 10.1145/3715779; Tier A), so "we only log metadata and tool calls" needs the same minimization thinking as T2.

## The EU analysis

### Lawful basis and minimization

Consent is close to unusable at work, since employees "are almost never in a position to freely give, refuse or revoke consent" (WP29 Opinion 2/2017, WP249, §6.2; Tier B, EDPB-endorsed). That leaves legitimate interest under Art. 6(1)(f) for private employers. Recital 49 names processing "strictly necessary and proportionate for the purposes of ensuring network and information security" as a legitimate interest, though its own list of actors is public authorities, CERTs, CSIRTs and communications and security providers, so an ordinary employer reaches it through the EDPB's reading, which calls the recognition indirect and says security processing "may, in principle" rest on Art. 6(1)(f) if the necessity and balancing tests are met, while warning in the next paragraph that security "cannot justify an excessive processing of personal data" (Guidelines 1/2024, paras. 126 to 127; Tier B, consultation version of 8 October 2024). The EDPB's AI-models opinion lists "improving threat detection in an information system" as a legitimate interest in deployment (Opinion 28/2024, para. 69) and reads necessity together with minimization, so the purpose must not be reasonably achievable by other means (paras. 70 to 71). Public authorities cannot use Art. 6(1)(f) for their tasks and need Art. 6(1)(c) or (e) and a national law (Art. 6(1), last sentence; Tier A).

Minimization is where the tier gets decided, and the 2017 WP29 opinion reads like a design brief for an AI gateway: the employer "should first investigate other, less invasive, means", where misuse can be prevented by blocking "blocking should be chosen", and where some logging is strictly necessary the appliance "may also be configured not to store log data unless the appliance signals the occurrence of an incident, with a minimization of the information collected" (WP249 §5.3; §6.4 adds that "prevention should be given much more weight than detection"; Tier B). Read against the tiers, that is T0 and T1 by default, T2 on trigger and T3 as an exception. For workers, a meta-analysis of 94 samples and 23,461 workers found no evidence that electronic monitoring improves performance, a stress effect of ρ = .16 that grows with invasiveness and breadth (ρ = .20 and .22) (Ravid et al., Personnel Psychology 2022, 10.1111/peps.12514; Tier A), though the authors say stress rises "regardless of the characteristics of monitoring" and the studies predate generative-AI assistants.

### Retention, security and pseudonymization

No EU text sets a retention period for prompt logs, so the anchors are analogies. The CNIL recommends six months to a year for security logs (2021-122, para. 8), up to three years in the documented internal-control case (paras. 16 to 19), and pseudonymous identifiers where the main data is short-lived (para. 22), though it covers application logs and excludes perimeter equipment (para. 2), which is nearer to where a gateway sits. At the strict end, the Italian Garante's 2024 workplace-email guidance says metadata retention for the system's own operation should "not in any case exceed 21 days" without documented conditions or the Art. 4(1) Statuto procedure (orientative by its own account; provvedimento 364 of 6 June 2024; Tier B).

A prompt store is a copy of whatever users pasted. Over 70% of WildChat queries carried some detected PII after a Presidio pass, mostly names of people and organizations (Mireshghallah et al., COLM 2024, arXiv 2407.11438; Tier A per the PDF header), and 8% of 100,342 shared chatbot conversations carried privacy risk under a stricter definition, with authentication data at 250 of 9,623 issues (Mollaeefar et al., PoPETs 2026, 10.56553/popets-2026-0081; Tier A), so the gap between the figures is the definition. The EDPB's pseudonymization guidelines say pseudonymization can count in the balancing test (Guidelines 01/2025, para. 55), that the pseudonymization domain can be one organizational unit (paras. 35 to 38), and that keyed one-way functions "like HMACs" with confidential, possibly split, secrets are suitable means (paras. 107 to 108; Tier B, consultation version). Unkeyed hashes fail, as the 2014 New York taxi release's MD5 hashes did by enumeration (Garfinkel, NIST IR 8053, §3.2; Tier A). Key destruction as an erasure control is my reasoning and untested, and an HMAC still shows which records share a prompt while the key exists (Tier D). Redacting T2 text is weaker as engineering than as law: an LLM-plus-rules detector recalled 69.0% of what human annotators found in chatbot conversations that mix code, logs and prose (Mollaeefar et al., §7.2.2; Tier A), and removing named categories does not make text anonymous (Pilán et al., Computational Linguistics 2022, 10.1162/coli_a_00458; Tier A), so a redacted T2 store is still personal data with residual identifiers.

### DPIA and special-category data

Art. 35(1) is the general trigger, and Art. 35(3)(a) is narrower than it is often quoted, since it covers automated evaluation "on which decisions are based that produce legal effects ... or similarly significantly affect the natural person", so it reaches a prompt classifier only where its verdicts feed decisions about the worker; Art. 35(3)(b), large-scale special-category processing, is the likelier listed case for a T2 or T3 store (Tier A). WP29's DPIA guidelines say two criteria "in most cases" require one and mark systematic monitoring of employees' work stations and internet activity as likely to (WP248 rev.01; Tier B), so I would treat the DPIA as mandatory in practice for fleet-wide capture.

Art. 9(2) has no network-security ground, and prompts to an enterprise assistant will carry health, union, religious and political details at some rate, so a T2 or T3 store processes special-category data incidentally and at scale. The proposed Digital Omnibus exception for "incidental and residual" processing is not law, and the EDPB and EDPS read it as aimed at training data (Joint Opinion 2/2026, §6.2; Tier B). Today the mitigations are architectural: an input filter before write, redaction at write for T2, a trigger design that keeps T3 rare, short retention, and a content store a few named responders open with a recorded reason. I would still expect a supervisory authority to ask how Art. 9 is satisfied for the residue, and I do not have a confident answer. Separately, ePrivacy Art. 5(3) requires consent to store or access information on a user's device unless strictly necessary for a service the user requested (Tier A), so a laptop-side exporter capturing prompt text from an IDE agent or browser assistant may be an Art. 5(3) question in some member states' readings (Tier D).

### Works councils, national law and the court test afterwards

In Germany §87(1) Nr. 6 BetrVG gives the works council co-determination over "technical devices designed to monitor the behaviour or performance of employees" (Tier A), which the Federal Labour Court reads as "objectively capable of", so a prompt log joinable to a user is covered (settled case law not re-verified; Tier B). The Netherlands (WOR Art. 27(1)(k) and (l), Tier A), Austria (ArbVG §96(1) Z 3, Tier B) and Italy (Statuto dei lavoratori Art. 4, Tier B) have their own versions. The CJEU held in C-65/23 (19 December 2024, ECLI:EU:C:2024:1051) that a collective agreement under Art. 88 must still meet Arts. 5, 6(1) and 9 and that national courts keep "a full judicial review" of necessity (Tier A), so a works agreement is a safeguard and not a way past the necessity test.

If the log is ever used against someone, the Grand Chamber's factors in Bărbulescu v Romania (no. 61496/08, 5 September 2017, §121; Tier A) are what a court applies: notice that is "clear about the nature of the monitoring and given in advance"; a distinction "between monitoring of the flow of communications and of their content", with content needing "weightier justification"; whether the aim could be met "without directly accessing the full contents"; consequences; and safeguards against access to content without prior notice. That is the metadata-versus-content line written by a court in 2017, so a programme should be able to produce a dated notice, a stated tier and retention, a written purpose and the alternatives it considered.

### The AI Act, narrower than the headlines

The record-keeping duties are high-risk duties. Article 12 requires high-risk systems to allow automatic logging, Articles 19(1) and 26(6) require keeping those logs "at least six months, unless provided otherwise in the applicable Union or national law, in particular in Union law on the protection of personal data", and Article 26(7) requires employers to inform workers' representatives and affected workers before a high-risk system goes into service (consolidated text CELEX 02024R1689-20260727; Tier A). After Regulation (EU) 2026/1744, the stand-alone Annex III obligations apply from 2 December 2027 (Art. 113; Tier A). A general coding or chat assistant is not high-risk, and where a deployment is, the Act wants functioning logs rather than transcripts and defers to data-protection law on retention. One open question I would put to counsel (Tier D): a classifier that scores employees' prompts for insider risk is plausibly a system "intended to be used ... to monitor and evaluate the performance and behaviour of persons" under Annex III 4(b), and profiling keeps it high-risk despite Art. 6(3), so the security tool watching the assistant may be the regulated system.

### NIS2 and DORA

NIS2 requires incident handling and access-control measures (Art. 21(2)(b) and (i)) and reporting within 24 hours, 72 hours and one month (Art. 23(4); Tier A), and names no prompts. DORA's RTS 2024/1774 Art. 12 requires logging of access control, change, operations and network traffic, with detail aligned "with their purpose and usage" and retention set by the entity, and Art. 22(d) requires incident evidence be kept "no longer than necessary" (Tier A; DORA Art. 17 itself read through a non-EUR-Lex rendering). For an in-scope financial entity that is a legal-obligation basis for the metadata tier and a strong argument for incident evidence once classified, and the RTS's alignment clause is data minimization in its own words, so it is not a basis for every employee's prompt text.

### United Kingdom

UK GDPR carries the same Articles 5, 6(1)(f), 9, 32 and 35. The Data (Use and Access) Act 2025 added "recognised legitimate interests" that need no balancing test, and the Annex 1 list does not include network security (Sch. 4; Tier A), but s. 70 inserted Art. 6(11)(c), naming processing "necessary for the purposes of ensuring the security of network and information systems" as an example of an ordinary legitimate interest (Tier A for text; commencement not checked), so the interest sits in operative text while the balancing still runs. The 2018 Investigatory Powers interception-by-businesses regulations allow interception on a business's own system for listed purposes if the controller "has made all reasonable efforts to inform every person who may use" it (SI 2018/356, reg. 4(1)(c); Tier A). The ICO's 2023 monitoring guidance is reported to require a DPIA for message monitoring and limit covert monitoring to exceptional cases (Tier B/C, summaries; the ICO pages returned 403). With no works-council statute, the UK column is GDPR plus notice.

## A US section, and what it does not answer

Federal law is a consent regime. The Wiretap Act makes interception lawful where the interceptor "is a party to the communication or where one of the parties to the communication has given prior consent" (18 U.S.C. §2511(2)(d)), and separately lets a provider's staff intercept in the normal course of work where necessary to render service or protect the provider's rights or property (§2511(2)(a)(i)) (Tier A, read 2026-11-09). An acceptable-use policy acknowledged at hire is commonly treated as consent, and there is no federal proportionality or minimization test on what content is kept. Three state notice statutes add procedure: New York Civil Rights Law §52-c (effective 7 May 2022) requires prior written notice and acknowledgement, Connecticut Gen. Stat. §31-48d written and posted notice with an exception for suspected lawbreaking, and Delaware 19 Del. C. §705 allows a daily electronic notice or a one-time written one (Tier B, law-firm summaries). California's CCPA has covered employee data since 1 January 2023, which gives California workers access and deletion rights over prompt logs about them (Tier B, not re-verified). The NLRB General Counsel memo on electronic monitoring, GC 23-02, was rescinded by GC 25-05 on 14 February 2025 (Tier B, press reports). So with notice a US-only employer can generally keep full text, and the EU analysis is what changes when the same capture is switched on for a European workforce.

What this section does not answer, and a US reader should take to counsel: state wiretap statutes that require every party's consent, which may reach prompt capture where a conversation includes an outside party such as a customer; the Stored Communications Act (18 U.S.C. §2701 and following) and when a prompt store held by a vendor counts as stored communications; state comprehensive privacy laws other than California's, many of which exclude employee data in ways I have not read; sector rules such as HIPAA and GLBA when prompts carry patient or customer financial data; and litigation holds, e-discovery and privilege over prompt logs that an incident or lawsuit makes discoverable.

## Decision table by jurisdiction and tier

Every cell is my synthesis (Tier D), anchored in the sections above. "Viable" means a documented path a careful team could defend; "conditional" means the path depends on a trigger design, an agreement or a national procedure; "doubtful" means I could not find the path in the sources.

| Tier | EU private employer | Germany | EU public body | UK | US with notice or consent |
|---|---|---|---|---|---|
| T0 metadata | Viable on Art. 6(1)(f); notice under Art. 13 | Viable with a §87(1) Nr. 6 agreement | Viable on Art. 6(1)(c)/(e) with a national legal basis | Viable on Art. 6(1)(f); SI 2018/356 notice | Viable |
| T1 keyed hash | Viable; pseudonymization counts in the balancing | Viable; mapping held in the security domain | Viable, as T0 | Viable | Viable |
| T2 on trigger | Conditional: DPIA, incident-team access, short retention, Art. 9 residue unresolved | Conditional: agreement names triggers, roles, evaluation ban | Conditional, needs explicit statutory footing | Conditional: balancing plus DPIA | Viable |
| T2 continuous | Doubtful: fails necessity where metadata or blocking serves | Doubtful; an agreement cannot cure necessity | Doubtful | Doubtful | Viable |
| T3 on exception | Conditional: written reason per case, shortest retention, erasure through every copy | Conditional under the agreement | Doubtful | Conditional | Viable |
| T3 continuous | Doubtful to not viable on WP249 reasoning and Bărbulescu | Not viable in my reading | Not viable | Doubtful | Viable |

France, the Netherlands and Austria follow the EU column with their own consultation or consent procedures, while Italy's Art. 4(1) procedure moves T0 and T1 with extended retention to conditional, and T2 on trigger and T3 on exception to doubtful without a union agreement or inspectorate authorization. NIS2 and DORA strengthen the T0, T1 and incident-evidence rows and leave the continuous-content rows alone.

## What this does not mean

It does not mean a capture is lawful because it matches the conditions above, which are what the sources name; a determination needs counsel and the facts. It does not mean content is useless for security, since one 2026 benchmark found that giving a monitor tool results and agent reasoning raised recall on agent insider misuse in three of four generator panels (Muhamed and Smith, arXiv 2609.06966; Tier B, preprint, synthetic setting), which argues for capture on trigger rather than no capture. Several things would change the analysis: a final EDPB legitimate-interest guideline treating continuous gateway content logging as ordinary security processing would move continuous T2 from doubtful to conditional; a supervisory-authority decision on an AI-assistant logging programme, which I have not found as of 2026-11-09, would replace most of the analogies here; a court reading Annex III 4(b) to exclude security tooling would close the classifier question; and a German employee-data statute with an AI-logging rule would change the German column.

## Gaps

- **Gap: US and other non-EU jurisdictions**. The US section names the federal rule and three state notice statutes and leaves the questions it lists unanalysed, and `jurisdiction-other` gets no analysis. **Needs**: a desk pass reading the state statutes and federal sector rules at the primary, with the same tier discipline.
- **Gap: UK after the 2025 Act**. DUAA commencement was not re-checked, and the ICO's 2023 monitoring guidance is cited through summaries because its pages returned 403. **Needs**: the ICO guidance read at the primary and the commencement regulations checked on legislation.gov.uk.
- **Gap: special-category residue**. No Art. 9(2) ground clearly covers health or union details that appear incidentally in a security content log. **Needs**: a supervisory-authority decision or EDPB statement on incidental special-category data in security logs, or the enacted text of the Omnibus exception.
- **Gap: redaction recall on coding-agent text**. The one large recall figure (69.0%) is on shared chatbot conversations, not coding-agent text. **Needs**: a bench measuring PII and secret redaction recall on coding-agent prompt and tool-call text against human annotation.
- **Gap: the classifier as a high-risk system**. Whether an insider-risk classifier over prompts is an Annex III 4(b) system is my reading only. **Needs**: Commission guidelines on Annex III or a national authority's reading.
- **Gap: device-side exporters**. How ePrivacy Art. 5(3) applies to a laptop-side exporter capturing prompt text from IDE agents or browser AI is untested. **Needs**: a regulator statement on Art. 5(3) and endpoint telemetry.

## Notes

- A final version of EDPB Guidelines 1/2024 or 01/2025 was not confirmed as of 2026-11-09.
- The decision table is a dated judgement (2026-11-10), and this document cites no lab run, so it carries no `measurement-claims` rows.
- Revalidate-by is five months out because final EDPB guidelines or the Omnibus could move a row.

## Sources

Tier A (statute, regulation, court and official text, read 2026-11-09):
- EUR-Lex: GDPR CELEX 32016R0679 (Recital 49, Arts. 5, 6, 9, 32, 35, 88); AI Act consolidated CELEX 02024R1689-20260727 (Arts. 6(3), 12, 19, 26, 113, Annex III 4(b)); NIS2 (EU) 2022/2555 (Arts. 21, 23); DORA RTS CELEX 32024R1774 (Arts. 12, 22); ePrivacy CELEX 02002L0058-20091219 (Art. 5).
- CJEU C-65/23, ECLI:EU:C:2024:1051, EUR-Lex CELEX 62023CJ0065.
- ECtHR [GC] Bărbulescu v Romania, no. 61496/08, HUDOC item 001-177082, §121.
- BetrVG §§80, 87, gesetze-im-internet.de; WOR Art. 27, wetten.overheid.nl BWBR0002747.
- UK DUAA 2025 s. 70 and Sch. 4; SI 2018/356 regs. 3 and 4, legislation.gov.uk.
- 18 U.S.C. §2511, law.cornell.edu.
- Ravid et al., Personnel Psychology 2022, 10.1111/peps.12514. Mireshghallah et al., COLM 2024, arXiv 2407.11438. Mollaeefar et al., PoPETs 2026, 10.56553/popets-2026-0081. Aghili, Li and Khomh, FSE 2025, 10.1145/3715779. Pilán et al., Computational Linguistics 2022, 10.1162/coli_a_00458. Garfinkel, NIST IR 8053, 10.6028/NIST.IR.8053.

Tier B (regulator guidance, EDPB documents and one preprint, read 2026-11-09):
- WP29 Opinion 2/2017 (WP249), 8 June 2017; WP29 DPIA Guidelines WP248 rev.01, 4 October 2017.
- EDPB Opinion 28/2024, 17 December 2024; Guidelines 1/2024 v1.0 and Guidelines 01/2025, consultation versions; EDPB-EDPS Joint Opinion 2/2026, 10 February 2026.
- CNIL délibération 2021-122, 14 October 2021.
- Garante provvedimento 364, 6 June 2024, docweb 10026277.
- ArbVG §96 via ris.bka.gv.at and secondary summaries.
- Muhamed and Smith, "MOLE", arXiv 2609.06966.

Tier B/C (law-firm and press summaries where a primary would not load or was not re-read):
- ICO, "Monitoring workers", 3 October 2023, via law-firm summaries.
- NY Civil Rights Law §52-c, Conn. Gen. Stat. §31-48d, 19 Del. C. §705, via law-firm summaries.
- NLRB GC 25-05, 14 February 2025, via press and law-firm reports.
- Digital Omnibus (data) Council mandate ST 14756/26, via press and law-firm reports.

This is not legal advice.
