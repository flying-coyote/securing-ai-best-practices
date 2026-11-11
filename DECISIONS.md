# Decisions

This file records the design decisions the repo was built on, in a fixed format so that it stays useful as it grows. Entries are numbered from 1 and never skipped or reused. Each carries a `date`, a `status` (Active, or Superseded by N when a later entry replaces it, in which case the old entry stays and says so), an `executed:` line that holds the hash of the commit that put the decision into effect (empty until that commit exists), and a line saying what would prove the decision wrong, because a decision with no stated failure condition tends to outlive the reasons for it.

Claim-level choices, such as which of two published ranges a document cites, are recorded beside the claim in that document's notes and not here (Decision 16).

## Decision 1: Thin prompt, fat fetched map

- date: 2026-11-09
- status: Active
- executed: 44eb4b1

The pasted block carries only what changes the agent's behaviour, and everything substantive (the interview, the signal definitions, the priority rubric, the drop order and the output format) lives in the files it fetches, carried over from the one-line audit in claude-code-project-best-practices. The practitioner never edits the block, so the block and the routing table cannot drift apart.

What would prove it wrong: practitioners editing the block to add questions, which would show the map is not carrying them.

## Decision 2: Commit-SHA pin, monthly releases, an offline bundle

- date: 2026-11-09
- status: Superseded by 17 (its failure condition was met on 2026-11-11)
- executed: a44a7cd (the first tagged release; the blocks were pinned to its SHA and the bundle SHA-256 recorded in RELEASES.md at ce86036)

The block fetches from a pinned commit SHA with the release tag named beside it, because branches and tags can both move. Releases are monthly at most. Each release publishes a concatenated bundle with its SHA-256 in `RELEASES.md`, so the review runs in two modes: fetch mode from the pinned commit, and offline mode from the checked bundle with web fetch off.

What would prove it wrong: a correctness fix that cannot wait for the next monthly release, which would argue for a hotfix lane.

## Decision 3: Priority is risk, confidence is tier

- date: 2026-11-09
- status: Active
- executed: 44eb4b1

Priority comes from a published rubric over reach, stakes, reversibility and blast radius, applied per signal in `routing.yaml`. Confidence is the backing document's frontmatter `evidence-tier` and `convergence`. The ordering perspectives order actions within a priority band and never score them, and a `believed` observation caps priority at Medium.

What would prove it wrong: reviewers consistently re-sorting the output by tier, which would show they trust confidence more than the risk ranking.

## Decision 4: The tier ladder

- date: 2026-11-09
- status: Active
- executed: 44eb4b1

Standards, statute and peer-reviewed research are Tier A. Vendor documentation of what a feature does is Tier B, alongside practitioner work and first-party lab measurement. Vendor claims about how well a feature works, how fast it is or how it compares are Tier C with the bias flagged. One author's judgement, or a model with stated assumptions, is Tier D and labelled. This is one rung below claude-code-project-best-practices (its Decision 15), which keeps first-party documentation at A because that repo is about one vendor's product; this repo grades many vendors and so cannot.

What would prove it wrong: a change to the evidence rubric I use across my public research, which this repo follows rather than forks.

## Decision 5: The interview branches on size and profile first

- date: 2026-11-09
- status: Active
- executed: 44eb4b1

The first two questions are size band and rent-or-own profile. A small organization that rents its AI gets a branch of about twelve questions; every other profile gets about five questions per surface family present.

What would prove it wrong: small-organization practitioners reporting that the branch misses a surface they run, measured by what they say in answer to the "anything else?" question.

## Decision 6: Reducers over raw exports, and no shell commands

- date: 2026-11-09
- status: Active
- executed: 44eb4b1

The repo ships local reducers that turn an admin export into signal keys and counts, and the fetched files contain no shell commands anywhere. A raw export is accepted only with a once-per-session reminder that it has left the practitioner's environment.

What would prove it wrong: practitioners reporting that the reducers are harder to run than reading the export themselves.

## Decision 7: Every document starts single-source

- date: 2026-11-09
- status: Active
- executed: 44eb4b1 (the weekly review that runs the convergence check arrived at 12619c5)

Every document is born `convergence: single-source`. A practice becomes `converged` only through the weekly review's check, and at birth only by the standards route, meaning a published standard, statute or schema prescribes the practice and at least one independent implementation exists.

What would prove it wrong: an independent adoption survey becoming available, which would give a better basis for convergence than the standards route.

## Decision 8: One derived count line

- date: 2026-11-09
- status: Active
- executed: 44eb4b1 (the weekly review that re-derives the line from disk arrived at 12619c5)

The README carries exactly one count line (routable docs, signals, stubs, and the date it was last derived), and the weekly review re-derives it from disk. No other file states those counts.

What would prove it wrong: the line drifting from disk between reviews often enough that it gets quoted stale, which would argue for generating it in CI instead.

## Decision 9: No job files a new issue

- date: 2026-11-09
- status: Active
- executed: 12619c5 (no quarterly scan file exists yet, since the first sweep is not due)

The scheduled external scan updates one standing issue in place. Quarterly judgement sweeps produce dated scan files. Nothing feeds an inflow of automatically filed issues.

What would prove it wrong: a broken source or an expired claim sitting unnoticed past one weekly review, which would show the standing issue is not being read either.

## Decision 10: Measurement lives in the lab repo, linked by commit

- date: 2026-11-09
- status: Active
- executed: 44eb4b1 (the last placeholder citation was replaced and every lab link moved to lab master 91e44df at 754de93)

Every lab result cited here lives in [sdw-lab-benchmarks](https://github.com/flying-coyote/sdw-lab-benchmarks) and is linked by commit hash. There is no `research/` folder, because a copied result is a second copy that the lab corrects and this repo does not. No local or temporary path is ever cited as a source. The `measurement-claims` frontmatter holds only claims something can re-run; judgements carry a dated prose marker instead.

What would prove it wrong: a cited commit becoming unreachable, or the lab correcting a result and the document here not following within one release.

## Decision 11: Staggered revalidation, scoped expiry

- date: 2026-11-09
- status: Active
- executed: 44eb4b1

`revalidate-by` dates are staggered at birth across three to eight months by document, with ATLAS-dependent documents at three, so documents written together do not expire together. The expiry check fails a pull request only when an expired claim sits in a document that pull request touches.

What would prove it wrong: expiries still clustering into one fortnight, or expired claims accumulating in documents nobody touches because the scoped check never fires for them.

## Decision 12: Platform settings pages stay a separate, linked set

- date: 2026-11-09
- status: Active (staged default, see below)
- executed: not yet (ai-config-pointers is not public, so no document links a settings page)

The per-product configuration pages (the setting, its default, the licence tier, the log it produces and where it lands) are a companion set, ai-config-pointers, linked from the documents that need them rather than folded into this repo, because they change on vendor release cycles, they run their own one-line worksheet over tenant APIs, and someone who wants only the settings pages should not need this repo's routing to use them.

What would prove it wrong: practitioners routinely needing both sets in one review and the cross-links failing them, which would argue for one repo and one release train.

## Decision 13: Figures live on the site

- date: 2026-11-09
- status: Active
- executed: not yet (no figure is published, so none is linked)

Figures are hosted on securitydataworks.com and linked from the documents, because a figure pinned to a framework release would need regenerating here every month from a repo that holds no data. A figure is linked only once it is published.

What would prove it wrong: a linked figure going stale against its pinned release while the document citing it is current.

## Decision 14: Declared-gap stubs from the first release

- date: 2026-11-09
- status: Active
- executed: 44eb4b1

Five families the first release does not research (assistant oversharing, RAG and vector stores, agent builders and managed build platforms, AI the organization ships, and AI incident response) get signals in `routing.yaml` from the start, routing to stub documents that point at the standard to read instead and declare the gap. A stub becomes a routable document only when a researched source exists.

What would prove it wrong: practitioners reading a stub's output section as coverage rather than as a gap, or a stub family still lacking a researched source a year after the first release.

## Decision 15: The decision sequence is the fourth Always Fetch document

- date: 2026-11-09
- status: Active (staged default, see below)
- executed: 44eb4b1

`analysis/decision-sequence.md` is fetched on every review and carries the ordering perspectives as one section. It ships `EMERGING` before the long-form article that argues the sequence is published, and gains a `follows:` line when it is.

What would prove it wrong: the sequence changing materially when the article is written, which would show it shipped before the argument was settled.

## Decision 16: Claim-level choices live beside the claim

- date: 2026-11-09
- status: Active
- executed: 44eb4b1

Choices about a single claim (which published range a document cites, or which tier a headline figure carries until a pending measurement runs) are recorded in that document's notes beside the claim, not as entries here, so this file holds only decisions about the repo.

What would prove it wrong: a claim-level choice that has to be found from outside its document, by the weekly review or a contributor, and cannot be.

## Decision 17: Monthly releases with a correction lane

- date: 2026-11-11
- status: Active
- supersedes: 2
- executed:

Everything in Decision 2 stands (the block pins a commit SHA with the release tag beside it, and each release publishes an offline bundle with its SHA-256 in `RELEASES.md`), except the cadence. Feature releases stay monthly at most and are tagged `vYYYY.MM`. A correction that cannot wait for the next monthly release (a wrong fact, a wrong citation, a front-door statement that contradicts the release record) ships as `vYYYY.MM.N`, numbered from 1 after the release it corrects. A correction release changes no routing behaviour and moves no golden, so a change that does either waits for the next monthly release. Decision 2's own failure condition was met on 2026-11-11, when an external review found front-door errors a day after v2026.12, which is why this entry exists.

What would prove it wrong: correction releases arriving often enough that practitioners stop treating a pinned block as current, or a correction release that turns out to have changed routing behaviour.

## Staged defaults

Decisions 12 and 15 are applied as defaults and stay open until I confirm or change them. Each is in effect as written; if one changes, the change is a new numbered entry that supersedes it.

## Maintainer exceptions

None yet. An exception to a decision above is recorded here with its date, the decision it departs from, and why.
