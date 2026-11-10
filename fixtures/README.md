# Fixtures

Three synthetic Answers Blocks and the output `scripts/route.py` produces for each, which CI compares on every pull request (`python scripts/route.py --check-fixtures`). They are the repo's test of its own routing and also its worked examples, so each `answers.yaml` opens with a comment saying what organization it stands for and which routing rules it exercises. None of them describes a real organization.

| Folder | Stands for | Branch |
|---|---|---|
| [`small-org-renter/`](small-org-renter/answers.yaml) | A 300-person SaaS company with no sector regulator that rents every AI surface it uses | small-org |
| [`mid-size-mixed/`](mid-size-mixed/answers.yaml) | An 800-person company with EU and US staff that rents most of its AI, runs one RAG store and has chosen a gateway | full |
| [`own-heavy-regulated/`](own-heavy-regulated/answers.yaml) | A regulated organization of about 8,000 people serving and fine-tuning its own models, with an AI analyst in the SOC | full |

When a change to `routing.yaml` moves a fixture's output, the check fails and prints the difference. If the new output is what the change intended, regenerate the golden and check it by hand against the table before committing it in the same pull request:

```bash
python3 scripts/route.py fixtures/small-org-renter/answers.yaml
```

The goldens were written by running the mapper and then checking each action's band, escalation and belief cap, each doc and each Question Packet against `routing.yaml` by hand, so a golden that merely records whatever the code printed is a defect in the fixture.
