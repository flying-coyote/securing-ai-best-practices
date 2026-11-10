# Contributing

Corrections, new sources and new analysis are welcome, and the bar for each is the same one the repo holds itself to: every claim carries its evidence tier, every number can be traced to the source that produced it, and nothing a contribution adds can identify an organization or the products it runs. The checklist below exists because a document that is not routed is a document no review will ever read, and a signal no interview asks about is a signal no review will ever see.

## What helps most

- A correction to a fact, a version, a default setting or a citation, with the primary source that shows it.
- A primary source for a claim currently held at a lower tier, or evidence against a claim.
- A researched source for one of the declared-gap families, which is how a stub becomes a routable document.
- A report from running the review: which agent and version, which branch, how long it took, and where the routing or the output went wrong. Please describe your organization by category only (see the anonymization rule).

## Integration checklist for a new analysis document

1. Copy `analysis/CANONICAL-DOC-TEMPLATE.md`, fill in the frontmatter, and keep the routable summary section inside the size budget the template sets.
2. Add or reuse at least one signal in `routing.yaml` whose `docs` names the new document. A routing row is mandatory, and so is an interview `question` for every key the row adds.
3. List exactly those keys in the document's `applies-to-signals`; every entry there must be a key in `routing.yaml`.
4. Give each new PROBLEM or REVIEW key its four priority factors and check that they fold to the band you intend.
5. Set `convergence: single-source` unless the standards route applies (a published standard, statute or schema prescribes the practice and at least one independent implementation exists), and say which in the document.
6. Stagger `revalidate-by` between three and eight months out, three for anything that depends on ATLAS.
7. Put every re-runnable measurement in `measurement-claims` with its source pinned to a commit, a release or a dated primary. Judgements and models with stated assumptions take a dated prose marker instead.
8. Add a dossier to `SOURCES.md` for any new source, and a row to `ABSORPTION-MAP.md` for the document.
9. Run the checks locally (see `scripts/README.md`) before opening the pull request.

## Evidence tiers

| Tier | What earns it |
|---|---|
| A | Standards, statute, court and regulator text, peer-reviewed research |
| B | Practitioner work, first-party lab measurement, and vendor documentation of what a feature does |
| C | Vendor claims about how well a product works, how fast it is or how it compares, and marketing, with the bias flagged every time |
| D | One author's judgement, or a model with stated assumptions, labelled as a hypothesis |

Compound labels are carried, never collapsed (a doc built on a Tier A schema and Tier D grades is "A schema; D grades"), and tier is confidence, never priority.

## The anonymization rule

Nothing merged into this repo identifies an organization's environment. That means no shared review, example or anecdote that names a vendor or product an identifiable organization runs, a hostname, an account or tenant identifier, a person, or a metric from a real environment. Describe a situation by category ("a 300-person SaaS company with Microsoft 365 Copilot and two coding agents") and never by name. The same split the review applies holds here: which assistant or cloud a kind of organization uses is low sensitivity, and security-tooling vendors, hostnames, identifiers and metrics are targeting aids.

## Boundaries the maintainer keeps

The maintainer's current and former employers are not named here, and nothing about any employer's tools, vendors in use, metrics, projects, findings or people appears in the repo, in either direction. Anecdotes come from earlier operational work or are stated as general observations.

The repo takes no vendor position beyond what the evidence supports. Grades are category grades and never a ranking of vendors, a vendor's efficacy claim never raises confidence past Tier C, prices from market maps are never stated as fact, and no contribution that reads as a product recommendation dressed as a category grade is merged. The maintainer may also do independent advisory work in this field, and no client, prospect or commercial relationship of any kind is referenced in the repo or shapes how a vendor is graded.

## What the repo does not carry

These come from the design and are enforced where a check can find them; the rest are review-only.

- No explainers of the OWASP Top 10 entries, no coverage of AI used in offense, no release recaps of ATLAS or other frameworks, and no explainers of framework overlays before the standards body publishes them.
- No exploit steps or payloads.
- No gateway, agent-platform or AI-security product reviews, and no vendor comparison presented as a category grade.
- No efficacy claim above Tier C for any vendor.
- No percentage for how well AI agents perform in a SOC until a pre-registered lab measurement of it exists.
- No headline figure from an unmeasured prevalence model; such a model can appear only as a labelled Tier D input.
- No control mappings taken from licence-restricted framework crosswalks.
- No re-derivation of a lab measurement inside a document; the document cites the run.
- No local or temporary filesystem path as a source.
- No telemetry, submitted reviews or answers blocks kept by the repo.
- The not-legal-advice sentence stays in the law document, the prompt blocks and the output format.

## Declaring a gap

When a document cannot back a claim it needs, it says so in its Gaps section in this form, which `scripts/list-declared-gaps.py` enumerates:

```markdown
- **Gap: <topic>**. <What is missing>. **Needs**: <the data, measurement or source that would close it>.
```

(That bold markup is the machine-readable convention and is the only bold the analysis documents carry.)

## Following a canon, and retiring a document

When a standard or a maintained external project comes to carry a document's argument, the document moves through two lanes recorded in its frontmatter and in `ABSORPTION-MAP.md`.

- Follow: the external canon carries the conceptual load for the document's slice. The document gains a `follows:` line naming it, keeps only what the canon does not cover, and stops growing there.
- Retire toward: a standard, feature or project clears all four bars (it is supported, generally available, covers the substance of the document's slice, and is citeable). The document gains `replacement-by:` and moves to `status: RETIRING`, then `RETIRED` once the replacement carries the whole load.

This repo's posture toward standards bodies and schema projects is to contribute rather than own: a document whose value is a missing mapping retires when the mapping is accepted upstream.

## Branches and pull requests

Work on a short-lived branch and open a pull request against `main`. The two required checks, `check-internal-links` and `test-instruments`, must pass; merges are squash-only and the branch is deleted on merge. Keep one topic per pull request, describe the evidence for any changed claim in the description, and expect a change to a priority band or a tier to be asked for its source.
