---
evidence-tier: D
convergence: single-source
applies-to-signals: [contributing-new-analysis]
surfaces: []
pins: []
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-05-10
status: EMERGING
---

# Canonical document template

This is the shape every analysis document in `analysis/` takes, and the shape a declared-gap stub in `analysis/stubs/` takes in a shorter form. Copy it, rename it, and fill it in. It is adapted from the canonical template in claude-code-project-best-practices, with four fields added (`surfaces`, `pins`, `summary-section`, and `last-checked` on default-state rows), a size budget, and this repo's tier ladder. The template is itself Tier D, since it is the maintainer's judgement about structure rather than a finding.

## Frontmatter

```yaml
---
evidence-tier: A | B | C | D | Mixed         # Mixed docs name the tier of each claim inline
convergence: converged | emerging | single-source
applies-to-signals: [keys from routing.yaml]  # every entry must be a routing.yaml key
surfaces: [S1, S2]                            # the surfaces the doc's practices apply to
pins:                                         # versions the doc was checked against
  - "MITRE ATLAS <release>"
  - "OCSF <version>"
summary-section: "Summary for the review"     # the heading the review reads first
last-verified: YYYY-MM-DD
revalidate-by: YYYY-MM-DD                     # staggered 3 to 8 months out; 3 if ATLAS-dependent
status: PRODUCTION | EMERGING | RETIRING | RETIRED | REFERENCE | ARCHIVED
follows: "..."                                # optional; mutually exclusive with replacement-by
replacement-by: "..."                         # required when RETIRING or RETIRED
measurement-claims:                           # optional; re-runnable claims only
  - claim: "..."
    source: "sdw-lab-benchmarks@<commit> <run folder>/RESULTS.md"
    date: YYYY-MM-DD
    revalidate: YYYY-MM-DD                    # or: never, with a one-line reason below
---
```

| Field | What it carries |
|---|---|
| `evidence-tier` | The tier of the doc's claims under `CONTRIBUTING.md`. Vendor documentation of what a feature does is B; vendor efficacy or comparison claims are C, flagged. |
| `convergence` | How broadly the practice is adopted. Born `single-source`; `converged` only by the standards route or the weekly review's check (Decision 7). |
| `applies-to-signals` | The routing keys that send a review here. The routing-coverage check fails if a key here is missing from `routing.yaml`, or if a shipped doc has no routing row. |
| `surfaces` | Which of the thirteen surfaces the doc applies to, by S-number. |
| `pins` | The framework, schema and catalogue versions the doc was checked against, so a release can tell which docs a new upstream version reopens. |
| `summary-section` | The exact heading of the routable summary. The review reads this section for every routed doc and reads below it only when an action needs the depth. |
| `last-verified`, `revalidate-by` | When the claims were last checked, and when they expire. |
| `status` | `PRODUCTION` validated and active; `EMERGING` not yet validated or carrying a declared gap; `RETIRING` deferring to a cleared replacement; `RETIRED` tombstone; `REFERENCE` imported reference; `ARCHIVED` superseded. |
| `follows`, `replacement-by` | The two absorption lanes (see `CONTRIBUTING.md` and `ABSORPTION-MAP.md`). |
| `measurement-claims` | Dated quantitative claims something can re-run, each pinned to a commit, release or dated primary. A frozen claim takes `revalidate: never` with a one-line reason in the notes. Judgements, perspectives and models with stated assumptions do not go here; they carry a dated prose marker and, where they are repo-level, a pointer to `DECISIONS.md`. |

## Size budget

The routable summary section stays under about 350 words and opens with the doc's thesis in one or two sentences, then the practices as actions, each with its effort (S, M or L) and the tier of its evidence. The whole document aims for about 2,500 words and should not pass 4,000; depth beyond that belongs in the lab repo or the cited primaries, linked. The reason is arithmetic: a review reads four Always Fetch documents and up to about eight routed ones beside a long interview, and an agent that runs out of context drops the end of the review, which is where the Question Packets and the appendices live. These numbers are a starting budget and will be re-set once the fixtures measure a full run's context use.

## Default-state rows

Any table row that states a vendor default (a content channel on, opt-in, paid or absent; where a record lands; which plan tier carries an audit log) carries its own `last-checked` date in a column, and the review prints "as of <date>" beside anything drawn from it, so a stale row degrades into a dated one rather than a wrong one.

| Platform family | Setting | Default | Where the record lands | last-checked |
|---|---|---|---|---|

## Section order

```markdown
# <Title>

Evidence tier: <tier>, <one-line justification>

## Summary for the review

<Thesis in one or two sentences. The practices as actions, each with effort and tier.
Under about 350 words. This is the section the review reads.>

## Why this matters

<The problem and the context needed for the rest.>

## <The analysis: the framework, the comparison, the default-state table>

<Every claim carries an inline citation with its tier.>

## What this does not mean

<Where the thesis breaks, the known exceptions, the alternative framings.>

## Gaps

<One line per gap in the declared-gap form from CONTRIBUTING.md.>

## Notes

<Claim-level choices (Decision 16) and dated markers for judgements.>

## Sources

<Grouped by tier, each with URL, date and the version read.>
```

Not every section is needed in every doc, but a missing one should be a choice. A stub in `analysis/stubs/` carries the frontmatter with `status: EMERGING`, a short summary naming the standard to read instead, one declared gap, and the sources.

## Citation form

Cite at the point of the claim, with the tier: "(Tier A, GDPR Article 35)", "(Tier B, vendor admin documentation, read 2026-11-09)", "(Tier C, vendor efficacy claim, bias flagged)". A lab result is cited by run and commit, never by a local path, and carries its qualifiers (single host, synthetic data, the verification verdict) in the same sentence.

## Gaps

- **Gap: size budget**. The word limits above are a starting estimate, not a measurement. **Needs**: a full review's context use measured on each of the three fixtures, in at least two agents.
