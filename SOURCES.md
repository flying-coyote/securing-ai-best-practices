# Sources

One dossier per source the analysis documents rely on: what it is, who publishes it, its evidence tier, the version or date this repo is pinned to, which documents cite it, and when it was last checked. The tier rules are in `CONTRIBUTING.md` and, once written, `analysis/evidence-tiers.md`. Upstream, the [security-data-literature-review](https://github.com/flying-coyote/security-data-literature-review) is the broader bibliography, and a dossier here cites its entry where one exists rather than repeating it.

Last curated: 2026-11-10 (skeleton; dossiers are added with the documents that cite them, so this file opens with the standards the routing table names and no pinned versions yet).

## How a dossier reads

```markdown
### <Source name>

- Publisher: <standards body, regulator, vendor, author>
- Tier: <A | B | C, with the bias flagged | D, labelled>
- Pinned: <version, commit or edition, and the date it was read>
- URL: <primary URL>
- Cited by: <analysis docs>
- Last checked: <YYYY-MM-DD>
- Notes: <what it does and does not cover; anything that limits the tier>
```

A vendor source gets two lines when it is cited both ways: Tier B for what a feature does, and Tier C for any claim about how well it works, how fast it is or how it compares.

## Standards and frameworks (Tier A)

These are the primaries the routing table's Why cells name. Each gets a full dossier with its pinned version when the first document citing it is written.

### CoSAI secure-ai-tooling

- Publisher: Coalition for Secure AI (an OASIS Open project)
- Tier: A
- URL: https://github.com/cosai-oasis/secure-ai-tooling

### MITRE ATLAS

- Publisher: MITRE
- Tier: A
- URL: https://atlas.mitre.org/

### OWASP Top 10 for LLM Applications

- Publisher: OWASP GenAI Security Project
- Tier: A
- URL: https://genai.owasp.org/llm-top-10/

### NIST AI Risk Management Framework 1.0

- Publisher: NIST
- Tier: A
- URL: https://www.nist.gov/itl/ai-risk-management-framework

### NIST AI 600-1, Generative AI Profile

- Publisher: NIST
- Tier: A
- URL: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf

### OCSF schema

- Publisher: Open Cybersecurity Schema Framework project
- Tier: A
- URL: https://schema.ocsf.io/

### Model Context Protocol specification

- Publisher: Model Context Protocol project
- Tier: A
- URL: https://modelcontextprotocol.io/specification

### CISA Known Exploited Vulnerabilities catalog

- Publisher: CISA
- Tier: A
- URL: https://www.cisa.gov/known-exploited-vulnerabilities-catalog

## Lab measurement (Tier B)

### sdw-lab-benchmarks

- Publisher: the author's public lab repository
- Tier: B (first-party measurement, single host unless a run says otherwise; each run's qualifiers travel with the claim)
- URL: https://github.com/flying-coyote/sdw-lab-benchmarks
- Notes: every run cited here is linked to its RESULTS and VERIFICATION files by commit hash, never copied (Decision 10).

## Unverified

Claims or sources that could not be confirmed against a primary on the last pass are listed here, with the date and what was tried, until they are confirmed or dropped. None yet.
