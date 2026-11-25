---
evidence-tier: D
convergence: single-source
applies-to-signals: [audit-always-fetch]
surfaces: []
pins: []
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-06-14
status: EMERGING
---

# Evidence tiers: how this repo grades confidence

Evidence tier: D, because the ladder is the maintainer's judgement about how to grade sources (DECISIONS.md Decision 4), adapted from a published ladder rather than prescribed by any standard.

## Summary for the review

A source's tier depends on what it is cited for, so the same vendor page can be Tier B for what a setting does and Tier C for how well it works, and the tier always measures confidence in a claim, never how urgent an action is. Every review fetches this document so that the confidence printed beside each action means the same thing to the agent and to the reader.

- Print the backing document's frontmatter `evidence-tier` and `convergence` beside every action, read from the frontmatter and never inferred from the prose, and where the document is Mixed name the tier of the specific claim the action rests on. Effort S; Tier D (repo rule).
- Keep priority and confidence apart: priority comes from the rubric in `routing.yaml`, so a Tier A source never raises a band and a Tier D perspective orders actions inside a band without raising one. Effort S; Tier D.
- Treat any vendor claim about efficacy, speed or comparison as Tier C with the bias flagged, however it is phrased, and say so in the action. Effort S; Tier D.
- Carry compound labels as written ("A schema; D grades") rather than collapsing them to the higher or the average tier. Effort S; Tier D.
- Cite a lab result by repository, commit or branch and run folder, with its qualifiers (single host, synthetic data, the verification verdict) in the same sentence, and grade it Tier B. Effort S; Tier D.
- Before acting on a Tier C or Tier D item, check it in your own tenant or environment, since that check is what would move the claim up. Effort S to M depending on the surface; Tier D.
- Read an "I found no X" claim as Tier D unless the document says it searched a complete, versioned catalogue whole, and print it that way. Effort S; Tier D.

## Why this matters

The review this repo drives prints two things beside every action, a priority and a confidence, and a reader with an hour to spend will sort by one of them. If confidence is muddled, either because a vendor's efficacy number has been graded like a standard or because a strong source has been allowed to make a minor finding look urgent, the reader spends the hour on the wrong things. So the ladder has two jobs: grading each source honestly for the claim it supports, and staying out of the priority ranking, which `routing.yaml` scores on reach, stakes, reversibility and blast radius (DECISIONS.md Decision 3).

The second reason is that this repo grades many vendors at once. A repo about one vendor's product can reasonably treat that vendor's documentation as the primary source for everything about the product, and claude-code-project-best-practices does exactly that. A repo that sets assistants, coding agents, gateways, identity providers and SaaS platforms from different vendors side by side cannot, because the vendors' documentation would then outrank the standards and peer-reviewed work the repo uses to check them.

## The ladder

| Tier | What earns it | Examples in this domain |
|---|---|---|
| A | Standards and frameworks from standards bodies and open framework projects, statute, court and regulator text, peer-reviewed research | NIST AI RMF 1.0, NIST AI 600-1, the CoSAI secure-ai-tooling controls, MITRE ATLAS, the OWASP Top 10 for LLM Applications, the OCSF schema, the MCP specification, regulation text |
| B | Practitioner work, first-party lab measurement, and vendor documentation of what a feature does | an admin guide stating which audit event a setting emits, a practitioner's published method, a run in sdw-lab-benchmarks |
| C | Vendor claims about how well a product works, how fast it is or how it compares, and marketing, with the bias flagged every time | a vendor's detection-rate figure, a vendor-run benchmark, a survey published by a company that sells the remedy |
| D | One author's judgement, or a model with stated assumptions, labelled as a hypothesis | the ordering perspectives in `decision-sequence.md`, a prevalence model with stated inputs, this ladder |

This is the same ladder as the table in `CONTRIBUTING.md`, which stays the contributor's copy and names Tier A more briefly; this document carries the reasoning and the hard cases behind it. Open framework projects (ATLAS, OWASP, CoSAI, OCSF, the MCP specification, Sigma) are Tier A for what they prescribe or catalogue, on the same footing as a standards body, and a figure or opinion that rides inside one of their documents is graded by where it came from.

Regulator text splits by what it is. A binding instrument (a statute, a regulation, a court judgment, a supervisory decision, a directive the addressee must follow) is Tier A for what it requires, and guidance a regulator or agency publishes about how it reads the law or what it recommends (an EDPB guideline, a national authority's FAQ, a joint advisory, implementation guidance) is Tier B, because it binds nobody and can be revised without a legislative process.

### Absence claims

A sentence of the form "I found no X" is Tier D unless the search covered a complete, versioned catalogue read whole, such as every entry of a pinned KEV catalogVersion or every technique in a pinned ATLAS release, in which case the absence takes the catalogue's tier for that version and says nothing about the world outside it. A search across vendor pages, papers or documentation portals is never complete in that sense, however many pages it covered, so its absences stay at D and the document says what was searched.

### Hard cases

| Case | Tier | Why |
|---|---|---|
| A design, method or pre-registration that has not been run, or that an agent froze and the maintainer has not reviewed | D for any outcome it predicts; the run, once it happens, is B | nothing has been measured yet |
| A standard or paper read only through an abstract | the source's tier, for what the abstract itself states | the claim and the read text are the same words |
| A standard or paper read only through someone else's summary, a search snippet or a second model's account | B at most for the summary's content, D where only a second model vouches for it, and listed under Unverified in `SOURCES.md` either way | the primary's words were not read |
| A practitioner talk | B for what the speaker reports doing; D for a rule generalised beyond it | one practitioner's experience, as `SOURCES.md` grades the conference talks |
| Vendor advice on what to configure (a hardening guide, a best-practice page) | B for what the setting does; D for the advice that it should be set unless an independent source backs it; C if it claims an effect | the vendor is a fair witness to its product, not to the threat model |
| A party's statement about itself (a Form 8-K, a breach notice, an incident post) | A that it was filed or published and says what it says; B for the account of events | the account is the party's own |
| An essay or trade-press paper by a practitioner (Conway 1968, Reed 1999) | B | practitioner argument, not a vendor claim |

### Grade by claim type, not by source

The rule that does the most work is that a source is graded for the claim it supports. A vendor is the authority on what its own product does, so its documentation of a setting, a default, a log field or a licence tier is Tier B, and `SOURCES.md` gives such a source two lines when a document cites it both ways. The same vendor is not a neutral party on whether the product works, so a detection rate, a latency figure or a comparison with a competitor is Tier C with the bias flagged, and `CONTRIBUTING.md` holds that no vendor efficacy claim rises above C here, whatever the vendor's reputation. In practice I've found this split matters most in a single sentence, the kind a vendor page writes as "the setting blocks prompt injection", where "the setting exists and is on by default" is B and "blocks prompt injection" is C.

A framework gets the same treatment in reverse. A standard is Tier A for what it prescribes or catalogues, so ATLAS is A for the technique it describes and OWASP's list is A for the risk category it names, but a figure that rides along inside a standards document (a case study's loss estimate, say) is graded by where that figure came from.

### Where first-party lab measurement sits

Lab results from sdw-lab-benchmarks are Tier B, which is a choice and deserves to be stated as one. They are first-party measurements on a published method, so they are stronger than a vendor's self-measurement, but they are usually single-host runs on synthetic data and nobody independent has replicated them yet, which keeps them below peer review. The qualifiers travel with the claim in the same sentence rather than in a footnote, so a reader sees "measured on one host, synthetic data, verified by a second model" beside the number, and the result is cited by commit, or by branch and run folder until it merges, never by a local path (DECISIONS.md Decision 10).

Because a sentence is not something a check can count, a `measurement-claims` row should also carry a `replication` field with one of four values: `none` (the run or read as reported), `partial` (some of the cells behind the claim re-run on the original host, not all), `same-host` (every cell behind it re-run on the original host or rig, by the author or a verifier) or `independent` (re-run by someone else on other hardware). The field was introduced on 2026-11-24 and not every document carries it yet; where it is present, the weekly review can list the unreplicated claims a document rests on, which is the population the lab-placement gap below is about.

### Where it came from

The ladder is adapted, under the MIT licence, from `analysis/evidence-tiers.md` and Decision 15 in claude-code-project-best-practices, and the four places it departs from that ladder are recorded with their reasons under Decision 4 in `DECISIONS.md`, which the review does not fetch.

## Four axes the review keeps separate

| Axis | Question it answers | Where it comes from | What it may never do |
|---|---|---|---|
| Priority | How bad is this if it is true? | the four-factor rubric in `routing.yaml`, folded into High, Medium or Low | be raised by a source's tier |
| Evidence tier | How good is the source behind the practice? | the backing document's frontmatter, and the claim's inline tier where the document is Mixed | be read from prose or guessed |
| Convergence | How broadly is the practice adopted? | frontmatter; born `single-source`, `converged` only by the standards route or the weekly review (Decision 7) | be inferred from a single citation |
| Observation confidence | How sure is the practitioner that the condition holds here? | the interview or a reducer: read, owner-stated or believed | change a tier; a believed observation keeps its band and adds a confirm-within deadline instead |

The axes are easy to blur because they all sound like confidence, so the review prints them as separate fields, and a reader can see that a High action backed by a Tier D perspective rests on a real exposure and a weak argument for the fix, which is a different thing from a Low action backed by a Tier A standard.

## When sources disagree

When two sources conflict, the document records both positions with their tiers and follows the higher tier by default, so an independent measurement at B outweighs a vendor's figure at C for the same claim, and the C figure stays in the document as the vendor's statement rather than being deleted. When two Tier A sources disagree, which happens when two frameworks scope the same control differently, the document names both and says in its notes which one it follows and why, the way Decision 16 asks for claim-level choices to be kept beside the claim.

## What this does not mean

A tier is not a vendor ranking, and a vendor whose documentation is cited at B has not been endorsed by that grade, since B says only that the vendor is a fair witness to what its own product does. A Tier A source can be wrong or late, and in this field standards often trail practice by a release or two, so a Tier A citation tells the reader the source went through a public process and says nothing about whether it has caught up with last month's agent features. Citing a standard also does not make a practice converged, because convergence needs the standards route or the weekly review's check (Decision 7). And a Tier D label is not an apology, since the decision sequence and the sizing perspectives are D because they are one practitioner's judgement, and labelling them that way is what lets a reader weigh them against their own experience of the same trade-offs.

## Gaps

- **Gap: calibration**. Nothing yet shows that a claim's tier predicts whether it survives, so the ladder orders sources by how they were produced rather than by measured reliability. **Needs**: a tally, kept by the weekly review over at least two releases, of claims corrected or withdrawn per tier.
- **Gap: lab placement is self-graded**. Placing first-party lab measurement at B is the maintainer grading his own work. **Needs**: an independent replication of at least one sdw-lab-benchmarks run cited here, which would either confirm B or argue for a lower rung for unreplicated runs.
- **Gap: the claim-type split is applied by hand**. No check finds a vendor efficacy claim that has been tiered B or A. **Needs**: a pattern check over `analysis/` for efficacy wording ("blocks", "detects", "faster", percentages) on lines tiered A or B, run in the weekly review.
- **Gap: tier and priority in readers' hands**. Decision 3 fails if reviewers re-sort the output by tier. **Needs**: dry runs on the four fixtures with practitioner readers, recording whether they act in priority order.

## Notes

- Preprints that have not been through peer review are graded Tier B as researcher work and move to Tier A when a peer-reviewed version appears; this is a claim-level choice recorded here under Decision 16, dated 2026-11-10.
- No claim in this document is re-runnable, so it carries no `measurement-claims` rows.
- `revalidate-by` is set seven months out because the ladder depends on no framework release and moves only when the evidence rubric it follows changes; the offset also keeps it off the template's expiry date.
- `surfaces` is empty because the ladder applies to every surface equally and routes only through `audit-always-fetch`.

## Sources

Tier B (practitioner methodology)

- claude-code-project-best-practices, `analysis/evidence-tiers.md` and DECISIONS.md Decision 15 ("Grade sources by claim type", dated 2026-11-09), MIT licence, read 2026-11-10. https://github.com/flying-coyote/claude-code-project-best-practices

Tier D (this repo's own decisions)

- DECISIONS.md, Decisions 3, 4, 7, 10 and 16, dated 2026-11-09.
- CONTRIBUTING.md, "Evidence tiers" and "Boundaries the maintainer keeps".
- SOURCES.md, the two-line rule for vendor sources cited both ways.
