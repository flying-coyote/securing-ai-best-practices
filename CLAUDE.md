# Agent instructions for this repository

This file is for coding agents working on the repo (a local session, a cloud session or a Claude Code Project thread). It is not part of the review and is not in the release bundle.

- Work on a branch and open a draft pull request. Never push to `main`, never push a tag and never create a release: releases follow `RELEASES.md` and DECISIONS.md (Decisions 2 and 17) and are cut by the maintainer.
- The employer and identifier denylist scan is a local pre-push hook by design (`scripts/README.md`, "The employer and identifier denylist hook"), so a cloud session cannot run it. That is why pushes to `main` happen only from the maintainer's machine.
- Run `python3 scripts/test-checks.py` and `python3 scripts/check-routing-coverage.py` before calling work done, and paste their summary lines in the pull request.
- After any `routing.yaml` edit, run `python3 scripts/render-audit-context.py`. A change that moves a fixture's golden is a routing change and says so in the pull request (`fixtures/README.md`).
- Every new or changed claim cites its source with an evidence tier under `CONTRIBUTING.md`, and a source is read at its publisher before it is cited.
