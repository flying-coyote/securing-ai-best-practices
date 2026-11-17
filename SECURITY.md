# Security policy

This repo ships three things a weakness could hide in, and each one is run by someone who trusts it with something: the one-line review block, which an agent executes with whatever the practitioner pastes into the session; the reducers in `scripts/reducers/`, which read admin exports on the practitioner's own machine and are meant to print nothing from them but counts; and the checks in `scripts/`, which are supposed to fail closed. A report about any of them is welcome, and so is a report that a document recommends something that would weaken a reader's security if followed as written.

## What counts as a security report

- A way to make the review block, `AUDIT-CONTEXT.md` or a fetched document redirect the agent, for example an injection that survives the Boundaries paragraph and changes what the review ranks, asks for or writes.
- A reducer printing any string from its input (a name, an email, a hostname, an identifier or a secret), printing a name `routing.yaml` does not declare, or running code from its input.
- A check that passes on a tree it should fail, the fail-open class `scripts/README.md` already records for the copied scripts.
- A release bundle whose SHA-256 does not match the one in `RELEASES.md`, or a pinned commit in a block that `RELEASES.md` does not list.
- A recommendation whose literal text would lower a reader's security, such as a setting described with the wrong default.

A factual error that carries no security consequence, such as a wrong version or a stale citation, is a correction rather than a security report, and the quick path for it is in [CONTRIBUTING.md](CONTRIBUTING.md).

## How to report

Use GitHub's private vulnerability reporting for this repository (the Security tab, then "Report a vulnerability"), which keeps the report between you and the maintainer until a fix ships. If that option is not shown, open an ordinary issue that says only that you have a security report and asks for a private channel, with no details, and the maintainer will reply with one.

Please describe your organization by category only, as the anonymization rule in [CONTRIBUTING.md](CONTRIBUTING.md) asks, and do not attach a real admin export or reducer input; a synthetic input that reproduces the problem is enough, and the reducer fixtures under `scripts/reducers/fixtures/` show the shape.

## What happens next

A confirmed weakness in a released block, bundle or reducer is the kind of correction the correction lane in Decision 17 of [DECISIONS.md](DECISIONS.md) exists for, so where the fix changes no routing behaviour and moves no golden it can ship as a correction release (`vYYYY.MM.N`), with the fix described in its row of [RELEASES.md](RELEASES.md), and a fix that does change routing waits for the next monthly release, as that decision requires. Older blocks keep pointing at the commit they pin, which is why each review prints the release it ran from and why a reader who has an older block should check `RELEASES.md` for a later one.

## Supported versions

Only the newest release in [RELEASES.md](RELEASES.md) receives fixes. A block pinned to an older commit keeps working as it did, but it will not pick up a fix until the practitioner replaces it with the current block from the README.
