# Fixtures

Three synthetic Answers Blocks and the output `scripts/route.py` produces for each, which CI compares on every pull request (`python scripts/route.py --check-fixtures`). They are the repo's test of its own routing and also its worked examples, so each `answers.yaml` opens with a comment saying what organization it stands for and which routing rules it exercises. None of them describes a real organization.

| Folder | Stands for | Branch |
|---|---|---|
| [`small-org-renter/`](small-org-renter/answers.yaml) | A 300-person SaaS company with no sector regulator that rents every AI surface it uses | small-org |
| [`mid-size-mixed/`](mid-size-mixed/answers.yaml) | An 800-person company with EU and US staff that rents most of its AI, runs one RAG store and has chosen a gateway | full |
| [`own-heavy-regulated/`](own-heavy-regulated/answers.yaml) | A regulated organization of about 8,000 people serving and fine-tuning its own models, with an AI analyst in the SOC | full |

When a change to `routing.yaml`, or to the `sequence-order` block in `analysis/decision-sequence.md`, moves a fixture's output, the check fails and prints the difference. If the new output is what the change intended, regenerate the golden and check it by hand against the table before committing it in the same pull request:

```bash
python3 scripts/route.py fixtures/small-org-renter/answers.yaml
```

The goldens were written by running the mapper and then checking each action's band, escalation and belief cap, each doc and each Question Packet against `routing.yaml` by hand, so a golden that merely records whatever the code printed is a defect in the fixture.

## Worked examples

These are the doc lists and top actions the routing table actually produces for each fixture, which is why they live here rather than in `ONE-LINE-PROMPT.md`: this README is left out of the offline release bundle, so an agent under test has to route a fixture's Answers Block itself instead of copying its answer from the bundle.

| Fixture | Branch | Top actions, in order | Docs fetched |
|---|---|---|---|
| [Small-org renter](small-org-renter/answers.yaml): 300 people, no regulator, every surface rented | small-org | `oauth-grants-unreviewed` (raised to High by the consent-grant count); `agent-kill-switch-absent`; `ai-aup-absent`; `ai-tool-intake-absent`; `incumbent-inventory-absent` | 18 |
| [Mid-size mixed](mid-size-mixed/answers.yaml): 800 people, EU and US staff, one RAG store, a gateway chosen | full | `agent-static-secrets`; `dpia-absent`; `prompt-capture-tier-full` (raised to a High action because EU staff are in scope and no DPIA exists); `incumbent-inventory-absent`; `hook-fail-open`; `mcp-allowlist-absent`; `oauth-grants-unreviewed` | 24 |
| [Own-heavy regulated](own-heavy-regulated/answers.yaml): 8,000 people, regulated, self-hosted and fine-tuned models, an AI analyst in the SOC | full | `pickle-formats-present`; `inference-runtime-default-bind` (raised to High because the runtime is internet-reachable); `agent-kill-switch-absent`; `ai-analyst-ungraded`; `model-store-unscanned`; `containment-pre-authorized-broad` (High by its factors, capped at Medium because it was only believed); `mapping-treated-as-coverage` | 18 |

Each `expected.yaml` carries the full output: every action and review row with its band, sequence group and factor sum, the doc list, the Question Packets by owning role, the surfaces not run, what was answered clean, and any answer that contradicted its derivation. Within a band the mapper orders by the sequence group from the `sequence-order` block in `analysis/decision-sequence.md` (a row under `row-overrides` takes that group, any other row its family's), then by factor sum, highest first, then by row order in `routing.yaml`, which is the rule AUDIT-CONTEXT's Priority rubric states. Top actions come from PROBLEM rows only, so on the mid-size fixture `gateway-token-store-unreviewed`, a High REVIEW row, is listed under `review` and takes no top-action slot. On small-org the believed cap drops `agent-static-secrets` to Medium, where the identity family's group 4 places it behind the governance and configure-what-you-own rows, so it falls outside the top five.
