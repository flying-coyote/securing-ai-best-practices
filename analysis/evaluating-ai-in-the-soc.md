---
evidence-tier: Mixed
convergence: single-source
applies-to-signals: [ai-in-soc-present, ai-analyst-ungraded, containment-pre-authorized-broad]
surfaces: [S13]
pins:
  - "OCSF 1.9.0"
  - "DuckDB 1.5.3"
  - "pySigma 2.0.3"
  - "pySigma-backend-sqlite 2.1.1"
  - "sdw-lab-benchmarks 91e44df"
  - "OpenSec arXiv-2601.21083-v3"
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-03-10
status: EMERGING
measurement-claims:
  - claim: "Over a synthetic OCSF 1.9.0 api_activity store with the ai_operation profile, at 2,000 benign sessions per seed over three seeds, the only rule that reached DETECTED on both planted chain shapes and all four plant strata was the session rule that walks delegation to the root session and qualifies the exfiltration leg by content, at precision 1.0, recall 1.0 and 0 false positives on every seed in SQLite and DuckDB 1.5.3; the clean score rests on a fixture credential string and a fixed burst threshold, and the lookalike rates were chosen by the run author"
    source: "sdw-lab-benchmarks@91e44df t8c-trifecta-detection/RESULTS.md:13, :35, :86-87"
    date: 2026-11-10
    revalidate: 2027-03-10
  - claim: "The plain session rule (one session holding an untrusted ingest, a sensitive read and an off-allowlist outbound call) was NOISY at precision 0.1923 to 0.2128 with recall 0.5, missing every delegated chain and firing on 37 to 42 benign sessions per seed, which falsified the pre-registered hypothesis that the sequence alone buys precision"
    source: "sdw-lab-benchmarks@91e44df t8c-trifecta-detection/RESULTS.md:13, :32, :37, :50"
    date: 2026-11-10
    revalidate: 2027-03-10
  - claim: "At tenfold benign background (20,000 sessions, one seed, SQL rules only) every rule kept its state; the plain session rule fell to precision 0.026 with 374 false positives while the content-qualified walk stayed at precision 1.0 with 0 false positives and recall 1.0"
    source: "sdw-lab-benchmarks@91e44df t8c-trifecta-detection/RESULTS.md:45"
    date: 2026-11-10
    revalidate: 2027-03-10
  - claim: "Planting eight ATT&CK techniques into a seeded synthetic OCSF store and scoring compiled Sigma rules against a precision floor of 0.9 gave 3 detected, 1 noisy and 4 missed, where the noisy RDP rule matched 2,960 rows of which 2,959 were benign and the four misses had no rule or nothing plantable"
    source: "sdw-lab-benchmarks@91e44df ocsf-attack-coverage/results/RESULTS.md:14, :19"
    date: 2026-06-21
    revalidate: 2027-03-10
  - claim: "In one air-gapped planted hunt over APT29 telemetry in a local DuckDB OCSF store, gemma4:e4b found the dropper and its user in 5 steps and 172.0 s of generation time while phi4 took 6 steps and 198.1 s and got both wrong; one hunt, one host, no null hunt, so no rate"
    source: "sdw-lab-benchmarks@91e44df ocsf-airgap-agent/results/RESULTS.md:17-22"
    date: 2026-06-06
    revalidate: 2027-03-10
---

# Evaluating AI in the SOC: grade the analyst the way you grade a detection

Evidence tier: Mixed, with two preprints at B (one independent, one vendor co-authored), practitioner conference talks at B for method and C wherever a vendor describes its own agent, two pre-registered lab designs at B for design only because neither has run, one verified lab run on synthetic data at B, and the containment-scope line and the evaluation cadence at D as my judgement.

## Summary for the review

An AI analyst in the SOC fails in two ways that a single accuracy score hides, acting before the evidence is in and missing more as the evidence pile grows, and a detection team already owns the method that measures both: planted ground truth over its own telemetry, scored by a check with no opinion. No first-party rate exists for either failure yet, because the lab measurement that would produce one is pre-registered and not yet run.

- Before the AI analyst is trusted with a verdict, grade it on planted hunts and null hunts written before any model sees them, with gold kept out of every prompt and scoring done by answer equality on host, user and command line. Effort M. Tier B for the method, D for the threshold of trust.
- Re-run the graded set on every model, prompt or harness change, report the verdict flip rate beside the mean, and re-test any tuned improvement on a second model. Effort S once the set exists. Tier B.
- Never let the agent, or a model from the same family, grade itself; where no gold answer can exist, treat agreement between models as agreement and never as accuracy. Effort S. Tier B.
- Hold autonomous containment to actions that are scoped to one host or account and reversible within minutes, and put a human approval in front of anything broader, because the evaluation evidence shows agents recognize threats better than they show restraint. Effort M. Tier B for the restraint finding, D for where the line sits.
- Grade the detections the SOC writes over AI-agent telemetry the same way, with planted chains and benign lookalikes, because in lab run T8c the rule that looked right on paper was noisy and missed every delegated chain. Effort M. Tier B, synthetic corpus, one host.

Broad containment sits at High because a wrong containment at machine speed reaches the whole organization; the ungraded analyst sits at Medium because its harm arrives as slow erosion of coverage.

## Why this matters

Some SOCs have had an analyst, or an automated playbook, that was right about the threat nearly every time it escalated and still cost the team more than the analysts who missed things, because it isolated hosts on the first suggestive alert and the cleanup of the hosts that turned out to be fine landed on another team and on the SOC's credibility. What it knew about attacks was rarely the problem; what it lacked was the patience to confirm that this alert was the attack before acting on it. That is worth keeping in mind when reading AI-analyst evaluations, because the finding from the past year I'd put first describes the same failure in machines.

OpenSec, an independent preprint by Jarrod Barnes, put incident-response agents from four frontier models into an environment with adversarial evidence and the authority to contain, and found consistent over-triggering across all four, with the most aggressive model containing in every one of its episodes and acting by step 4, and with every model correctly identifying the ground-truth threat when it did act, so the paper places the calibration gap in restraint rather than in recognition (Tier B, Barnes, arXiv 2601.21083 v3, 2026-02-06, preprint with open code, not peer-reviewed). I've left the paper's rates out of this doc on purpose, because the repo carries no percentage for how AI agents perform in a SOC until a pre-registered lab measurement of it exists, and a reader can take them from the paper with its environment attached.

The second failure comes from Maxim Kovalsky and Ali Arshad of Consortium Networks, who tested models on security-analysis work of increasing weight and found that accuracy degraded mainly through recall collapsing as the evidence grew, far more than through invention, and that a hand-verified seeded subset of about 100 items inside a run of more than 4,000 questions turned out to be a good proxy for whole-run performance (Tier B, "Your AI Analyst Is Confidently Wrong: Adversarial QC for Agentic Security Analysis", [un]prompted II, October 2026, as carried in sdw-lab-benchmarks@91e44df BENCHMARKING-METHODOLOGY.md:190-195; one team's experiments). So the two failures sit at opposite ends of the evidence pile: with too little evidence the agent acts anyway, and with too much it stops seeing what is there, and an accuracy figure averaged over a test set can look fine while both are happening.

If the SOC runs an AI analyst or agent (`ai-in-soc-present`), the review asks whether it was graded against planted truth or in shadow mode before it was trusted and on each model change (`ai-analyst-ungraded`), and whether it can contain beyond scoped, reversible actions without a human approving (`containment-pre-authorized-broad`). Whether it reads raw event text is a separate key with its own doc.

## The method a detection team already owns

Detection engineering already has a grading discipline that transfers almost unchanged. In an earlier lab run, eight ATT&CK techniques from one APT29-style chain were planted into a seeded synthetic OCSF store, Sigma rules were compiled to SQL, and each technique was scored as detected, noisy or missed against a precision floor of 0.9, giving 3 detected, 1 noisy and 4 missed, where the noisy RDP rule caught the planted connection along with 2,959 benign port-3389 connections, and the four misses were techniques with no rule or nothing plantable in the store, so they were scored missed without being executed (Tier B, sdw-lab-benchmarks@91e44df ocsf-attack-coverage/results/RESULTS.md:14, :19; synthetic testbed, one machine). The tally matters less than the habits behind it: plant the truth before running anything, keep the gold out of reach of whatever is being tested, and refuse to count a rule that catches the needle inside a haystack of false positives as coverage.

To apply that to an agent, change one thing, which is that the rule becomes a loop that writes its own queries. A planted chain gives recall. A hunt with nothing planted, together with the recorded query that proves it is empty, gives the over-trigger rate. A step-by-step transcript of which rows the agent had seen before it called a containment tool gives containment before evidence. Inflating the benign background around the same planted chain gives the recall-loss curve. None of this needs a model as judge, because the answer either is the planted host, user and command line or it isn't, and the deterministic check is a stronger verifier than any second opinion I could buy.

The lab's methodology adds the measurements that keep a model arm honest, written after several production teams described their evaluation practice at [un]prompted II (Tier B for method, sdw-lab-benchmarks@91e44df BENCHMARKING-METHODOLOGY.md:157-203):

- Report the verdict flip rate over repeated trials beside the mean, because a team that re-ran its production SOC agent on identical threats found the verdict flipping on a meaningful share of re-runs, and one threat investigated 33 times in a day was judged wrong in 32 of them at high self-reported confidence, so the agent's own confidence is not a substitute measure (Tier C for the efficacy content, Waitzenberg and Harush of Wiz, "Same Threat, Two Verdicts: Shadow Testing Our SOC Agent", vendor describing its own agent).
- Run a no-data arm when the corpus is public, with the same questions and the evidence withheld, and report that score as a floor, since public security datasets are memorized and a high no-data score means the evidence-arm score can't be read as hunting skill.
- Disclose the harness and prompt format, keep rubrics and gold answers out of every prompt and skill, and re-run any tuned improvement on a second model, because Dan Dye of Google Cloud Security reported that improvements from evolving his SOC agent's skills disappeared in a different model or harness, and that rubrics embedded in the skills were giving the model the answer to the test (Tier B, "Engineering Context for SOC Agents: Lessons, Failures, and Open Questions").
- Report each corpus, source and query class separately before any pooled number, and declare when a synthetic corpus may be recognizable as synthetic, which one vendor reports frontier models doing early with simulator output (Tier C, vendor report as carried in the methodology).

## What one hunt can tell you, and the run that would say more

The first-party evidence on an AI analyst is one hunt. On a planted hunt over the APT29 telemetry in a local DuckDB OCSF store, with every component offline, gemma4:e4b found the initial dropper and the user it ran as in 5 steps and 172.0 seconds of generation time, while phi4 took 6 steps and 198.1 seconds and got both wrong (Tier B for the air-gap mechanics and D for reasoning capability, sdw-lab-benchmarks@91e44df ocsf-airgap-agent/results/RESULTS.md:17-22; one hunt, one host). It shows that the loop assembles and stays on the box, and it can't carry a rate of any kind, since one hunt can't separate skill from one lucky query and it had no null hunt, so it says nothing about over-triggering.

The run that would say more is lab pre-registration R3, frozen by an agent on 2026-11-09, not owner-reviewed and not run (Tier B for the design, sdw-lab-benchmarks@91e44df ai-analyst-preregs/R3.md and ai-analyst-preregs/RESULTS.md:3-13). Its design is worth copying whether or not the lab's own run ever happens, because it is a template a SOC can build against its own data:

| Element | Design in R3 |
|---|---|
| Loop | One read-only DuckDB SELECT per step, step cap 12, at most 50 rows returned per query, so recall loss measures how the agent queries rather than context length alone (R3.md:32-34) |
| Containment | Two no-op tools, `isolate_host` and `disable_account`, each logged with its step index; nothing is isolated (R3.md:35-36) |
| Answer | Structured JSON with a verdict and findings by host, user, command line and time, scored deterministically on normalized keys with no model judge (R3.md:37-39) |
| Hunts | 24 written and frozen before any model sees them: 16 positive with gold sets of 1 to 6 items, 8 null with a recorded query proving there is nothing to find (R3.md:53-57) |
| Corpora | Real APT29 ATT&CK Evaluations telemetry and the lab's seeded synthetic testbed, reported separately and never pooled first (R3.md:44-49) |
| Volume | Testbed hunts at 1x, 4x and 16x benign background with the same planted chain; APT29 at 1x only (R3.md:66-71, :139-140) |
| Contamination | Every hunt also run with the store withheld (R3.md:83-88) |
| Trials | 8 per cell, 576 episodes per model, flip rate beside every mean (R3.md:109-110, :141) |
| Verifier | None from another provider, because scoring is answer equality on gold; a later second-provider leg would be reported as agreement, never accuracy (R3.md:166-168) |

Its five hypotheses, each with a stated condition under which it is wrong, predict recall at 16x lower than at 1x for every model, every arm over-triggering on at least 10% of null-hunt episodes, at least 20% of the hosted model's containment-calling episodes calling before it has seen a gold-key row, a contamination floor above zero on the public corpus, and a gap of at least 10 recall points between the hosted model and the larger local one (R3.md:122-133). Those thresholds are predictions in a frozen design and not findings, and I'd read any of them as a measured rate only once RESULTS.md carries the run. The primary run is estimated at about $92 in hosted spend with a $138 ceiling and a $150 hard stop, plus about 97 hours of serial local compute (R3.md:165-166, :182-184, :194), and it waits on that spend being approved.

A companion pre-registration, R11, asks what a correct triage costs at right-sized models, defines the right-sized arm before the run as the cheapest one within 5 points of the best arm's accuracy on every stratum, and prices R3's logged traces rather than paying for the agentic runs twice; it is also frozen by an agent, not owner-reviewed and not run, at about $217 expected with all three hosted tiers or about $75 without the largest (Tier B for the design, sdw-lab-benchmarks@91e44df ai-analyst-preregs/R11.md:25-28, :47-48, :132-135). I'd want that number before any conversation about whether an AI analyst saves money, because the quantity that matters is cost per correct answer, and a cheaper request that is wrong or takes more steps is not cheaper.

## Who checks the checker

The evaluations I trust most put a check with no judgement in it at the bottom: a planted answer, a hash of a frozen file, a recount from raw rows. Which model should grade another model's work is a question only above that layer, and the most careful public account I've found of what a second provider buys is more modest than the usual pitch. Gabe Bello described a security review agent for OAuth app grants that ran three providers as blind reviewers with a critic model cross-examining them, and reported that the panel agreed with a single model nearly every time, that when the panel disagreed the models were wrong together, and that the team kept the panel for resistance to one model hallucinating or being compromised rather than for accuracy; the failure that hurt in his account was an empty enrichment field every model accepted, and the fix was on the data side (Tier B, "Building Security Review Agents: the Models are the Reliable Part", [un]prompted II, October 2026).

So the order I'd use, as my judgement (Tier D, 2026-11-10), runs from no judgement to the most:

- Deterministic first wherever a gold answer can exist, which for a hunting or triage agent is almost always, since the planted host and command line are the gold.
- An independent re-run for claims about the results, by a second reader who re-executes rather than re-reads.
- A different provider only where judgement is the output and no gold exists, with agreement reported as agreement and disagreement routed to a human.
- Null and missing-field checks on whatever context the model reads, underneath all three.

The rule that the agent never grades itself follows from this. A vendor dashboard that reports the agent's own confidence, or a second instance of the same model reviewing the first, measures consistency at best, and the 33-investigation example above is what consistency without correctness looks like.

## Containment: where the line sits

The High-band key in this doc is about authority rather than evaluation, and I want to be plain that its line is my judgement. OpenSec's finding that agents recognize the threat and still act before the evidence justifies acting (Tier B, arXiv 2601.21083) is the evidence that restraint is the weak capability, and R3's no-op containment tools are the instrument that would measure it on a SOC's own data without isolating anything (Tier B for the design, not run). Nothing I've read yet measures how often a wrong autonomous containment happens in production or what it costs.

Given that, my line (Tier D, 2026-11-10) is that an agent may contain on its own only where the action is scoped to a single host, account or session, is reversible by the SOC within minutes without another team's help, and is logged with the evidence rows the agent had seen at the moment it acted. Disabling an account across an identity provider, blocking a domain or address range at the perimeter, quarantining a mailbox population or isolating a server that other systems depend on goes to a human for approval, because a wrong call there reaches beyond one asset faster than anyone can notice it. Containment-before-evidence on a planted set, measured with no-op tools, is the number I'd want before widening that scope, and the review should ask for it.

## Grading detections over AI-agent telemetry

The same planted-truth discipline applies to the other direction of AI in the SOC, which is writing detections over what AI agents do. Lab run T8c planted twenty exfiltration chains per seed, shaped on two published agent-compromise case studies, into a synthetic OCSF 1.9.0 `api_activity` store carrying the `ai_operation` profile, alongside 2,000 benign agent sessions per seed with seven pre-committed classes of benign lookalike, and scored thirteen rules across three seeds in SQLite and DuckDB 1.5.3, ten of which executed on both engines while the three pySigma correlation rules failed to parse on DuckDB (Tier B, sdw-lab-benchmarks@91e44df t8c-trifecta-detection/RESULTS.md:13-37, :58-60; synthetic corpus, one host, pre-registration frozen by an agent and not owner-reviewed, verdict VERIFIED-WITH-FIXES with three identical runs). The rule the draft design proposed, one session holding an untrusted ingest, a sensitive read and an off-allowlist outbound call, was noisy at a precision of 0.19 to 0.21 with recall 0.5, because it missed every chain that crossed a delegation to a sub-agent and it fired on 37 to 42 benign sessions per seed, which falsified the frozen hypothesis that the sequence alone buys precision (RESULTS.md:13, :32, :37, :50). The only rule that reached DETECTED on both chain shapes and all four strata walked delegation back to the root session and qualified the outbound leg by content, a credential-shaped string or a burst of 20 or more off-allowlist calls in 5 minutes, at precision 1.0, recall 1.0 and no false positives on every seed, and in the SQL-rules scale check at tenfold background it held while the plain session rule fell to a precision of 0.026 (RESULTS.md:13, :35, :45).

The qualifiers belong in the same breath as those numbers. The lookalike rates were chosen by the run's author and set the precisions almost directly, the clean score rests on a fixture credential prefix and a fixed burst threshold that a patient attacker could stay under, and the session and delegation fields were clean on every event, which shipping producers often fail to provide (RESULTS.md:86-88). So the defensible reading is the method and the mechanism rather than a field false-positive rate: a pre-registered planted test caught a detection design that looked right on paper, and that is exactly the test the SOC should be running on its AI analyst too.

## Turn on before you buy

Much of this needs no product, since the planted hunts, null hunts and gold file are a few days of a detection engineer's time against telemetry the SOC already holds, and the scorer is a join on normalized keys. What a SOC does need from an AI-analyst vendor is access, and I'd write three asks into the evaluation: a mode in which the agent's containment tools are stubbed and logged with the step index and the rows seen, an export of every episode's queries and returned row counts, and the ability to pin the model version so that a graded result still describes the agent in production next month. A vendor that can't offer a pinned version is telling you the graded set has to re-run on its release cadence, and I'd price that in.

## What this does not mean

None of this says AI analysts are bad at the job, and the doc deliberately carries no rate for how good or bad they are, because the first-party measurement has not run and the published ones come from environments that may not resemble a given SOC. OpenSec is one preprint in one environment, the conference findings are each one team's experience, and two of the sources on flip rate and synthetic recognition are vendors describing their own agents, so they carry Tier C for anything beyond method. Planted truth also has limits I'd name to anyone adopting it: the hunts encode one author's idea of a hunt, no-op containment measures intent to contain rather than the operational cost of a wrong containment, a public corpus stays memorizable even with a no-data floor, and a synthetic one may be recognizable as synthetic (R3.md:209-217). A team with no capacity to write hunts can still get part of the way with shadow mode, running the agent beside the human queue and comparing outcomes, as long as it treats that comparison as agreement and keeps the human as the gold.

## Gaps

- **Gap: first-party over-trigger and recall-loss rates**. No first-party measurement of how often an AI analyst calls something malicious on a null hunt, contains before evidence, or loses recall with background volume. **Needs**: R3 run as pre-registered, after owner review of the design and the gold set and approval of the spend.
- **Gap: cost per correct triage**. No first-party figure for what a correct triage or analyst answer costs at right-sized models. **Needs**: R11 run on R3's logged traces plus its own triage and NL2SQL families, with the owner's tariff and hardware figures for the local arms.
- **Gap: containment scope**. The scoped-and-reversible line is my judgement; nothing read measures the rate or cost of wrong autonomous containment in production. **Needs**: a published production measurement, or R3's containment-before-evidence figures read against a stated cost model.
- **Gap: OpenSec at the primary**. The abstract is read and its findings used qualitatively, but the body was not re-read, so the unit of its time-to-first-containment figure is unconfirmed. **Needs**: a read of the paper body and its released code.
- **Gap: detection over real agent telemetry**. T8c's rules ran on a synthetic corpus with clean session and delegation fields and chosen lookalike rates. **Needs**: a corpus with measured lookalike rates from real agent telemetry, and a slow-drip variant of the plants without a credential shape.

## Notes

- Decision 16 choices: OpenSec's and the shadow-testing talk's rates are described rather than quoted, under the repo's rule against percentages for AI-agent performance in a SOC before a pre-registered lab measurement exists; counts that illustrate instability (33 investigations, 32 wrong) are kept because they describe the method's motivation rather than a performance rate. T8c precisions are given as min-to-max ranges over seeds because the per-seed values differ.
- The talk findings are cited as carried in the lab methodology's section 10, whose quotes were re-checked against the talk transcripts on 2026-11-07; the agenda page confirms titles, speakers and affiliations as of 2026-11-10.
- R3 and R11 were frozen by an agent and have not been owner-reviewed. The R3 verifier left one point open, that the testbed null hunts also run at all three volume levels, which the run-count line states and the volume paragraph does not.
- Dated marker: the containment line and the evaluation ordering are my judgement as of 2026-11-10 and move once R3 runs.

## Sources

Tier B

- Barnes, "OpenSec: Measuring Incident Response Agent Calibration Under Adversarial Evidence", preprint, v3 2026-02-06, https://arxiv.org/abs/2601.21083, abstract read 2026-11-10.
- [un]prompted II: The AI Security Practitioner Conference, San Francisco, 2026-10-27 to 2026-10-29, agenda at https://unpromptedcon.org/agenda-10-2026/, read 2026-11-10: Kovalsky and Arshad, "Your AI Analyst Is Confidently Wrong: Adversarial QC for Agentic Security Analysis"; Dye, "Engineering Context for SOC Agents: Lessons, Failures, and Open Questions"; Bello, "Building Security Review Agents: the Models are the Reliable Part".
- sdw-lab-benchmarks@91e44df BENCHMARKING-METHODOLOGY.md:157-203, section 10, LLM arms, https://github.com/flying-coyote/sdw-lab-benchmarks.
- sdw-lab-benchmarks@91e44df t8c-trifecta-detection (RESULTS.md, VERIFICATION.md), run 2026-11-10, VERIFIED-WITH-FIXES, same repository.
- sdw-lab-benchmarks@91e44df ai-analyst-preregs (R3.md, R11.md, README.md, RESULTS.md), frozen 2026-11-09T23:03:24Z by an agent, not owner-reviewed, not run, same repository.
- sdw-lab-benchmarks@91e44df ocsf-attack-coverage/results/RESULTS.md and ocsf-airgap-agent/results/RESULTS.md, same repository.

Tier C

- Waitzenberg and Harush (Wiz), "Same Threat, Two Verdicts: Shadow Testing Our SOC Agent", [un]prompted II, October 2026, as carried in BENCHMARKING-METHODOLOGY.md section 10 (vendor describing its own agent, bias flagged).
- Cohen and Herzog (Torq), "When Humans Can't Make It Hard Enough: Self-Hardening Environments for Frontier AI Investigators", [un]prompted II, October 2026, as carried in BENCHMARKING-METHODOLOGY.md section 10 (vendor, bias flagged).
