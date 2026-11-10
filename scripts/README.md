# Scripts

Which scripts exist, where each came from, and whether anything runs it automatically. That last column matters in both directions, because a reader can assume a script is guarding something when nothing calls it, or assume it is inert when its output is something the repo depends on. To check for yourself, look for invocations rather than mentions:

```bash
grep -rn "python scripts/\|python3 scripts/" .github/workflows/*.yml
```

| Script | Origin | Runs automatically? | What it does |
|---|---|---|---|
| [`measure-link-reachability.py`](measure-link-reachability.py) | copied from claude-code-project-best-practices (MIT), with one change: it fails closed on an empty or untracked corpus in `--links` mode, as the reachability report already did | Yes, in the required `check-internal-links` job, on every pull request and push to `main` | With `--links`, counts internal markdown links by class; the job fails on any `dangling` row above zero, and on a corpus git does not track, so the gate cannot pass on a tree it never read |
| [`test-measure-link-reachability.py`](test-measure-link-reachability.py) | copied and adapted (see below) | Yes, in the required `test-instruments` job | Determinism across eight hash seeds, mode and entry-tier monotonicity, currency buckets, the disclosures, and the job's own awk gate against a clean and a broken corpus |
| [`check-measurement-expiry.py`](check-measurement-expiry.py) | copied and adapted (see below) | Yes, in `test-instruments`, scoped to a pull request's changed files | Fails only when an expired `measurement-claims` entry sits in a file the change touches; on other events prints the full count and passes |
| [`list-declared-gaps.py`](list-declared-gaps.py) | copied unchanged from claude-code-project-best-practices (MIT) | No, operator-run in the weekly review | Enumerates every `**Gap:** ... **Needs**:` declaration in `analysis/` |
| [`check-prompt-blocks.py`](check-prompt-blocks.py) | new | Yes, in `test-instruments` | README and ONE-LINE-PROMPT fetch-mode blocks byte-identical; with `--tag-commit` (which the workflow resolves, since the script never runs git) the block must pin that commit, and with no tag it must still carry the `<release-sha>` placeholder |
| [`check-routing-coverage.py`](check-routing-coverage.py) | new | Yes, in `test-instruments` | Keys unique and asked; factors fold into each band; every escalation has a machine-readable `escalate-if`; every `enables`, `requires` and `escalate-if` name exists; every surface enables a non-INVENTORY key; every family has a Question Packet owner; every shipped doc routed and its `applies-to-signals` matching the rows that route to it; the rendered AUDIT-CONTEXT section current. Routed docs not yet written are counted, and fail only with `--release` |
| [`render-audit-context.py`](render-audit-context.py) | new | No, operator-run after any `routing.yaml` edit; CI checks its output through the coverage check | Renders AUDIT-CONTEXT's routing section from `routing.yaml`; `--check` exits 1 when stale |
| [`route.py`](route.py) and [`../fixtures/`](../fixtures/) | new | Yes, in `test-instruments` (`--check-fixtures`) | The reference mapper: an Answers Block and any reducer outputs in, the branch, ranked actions, review rows, doc list and Question Packets out; checked against three hand-verified golden fixtures |
| [`check-exclusions.py`](check-exclusions.py) | new | Yes, in `test-instruments` | Temporary paths in `source:` fields, home-directory or private working-tree paths anywhere, the licence-restricted crosswalk folder, 2025-form OWASP LLM IDs, and the not-legal-advice sentence missing from either prompt block, the output format or the law doc |
| [`check-pins.py`](check-pins.py) | new | No, weekly review | Counts docs whose `pins:` differ from `analysis/revalidation-and-pins.md`; fails only when the pins doc itself lacks a version or, given `--current`, is behind the newest known release |
| [`probe-source-accessibility.py`](probe-source-accessibility.py) | new | Yes, in the scheduled `check-source-accessibility` job, which never runs on a pull request | Reads the pinned versions from `analysis/revalidation-and-pins.md`, fetches the pinned ATLAS, OCSF, MCP specification, CoSAI and OWASP pages, and reports for each whether the page answers and whether the upstream moved past its pin (newest release tag, or a change to CoSAI's component file since the pinned commit); `--current FILE` writes the newest-known versions in the form `check-pins.py --current` reads. Never fails on what it finds, exits 2 when it cannot read the pins doc |
| [`build-release-bundle.sh`](build-release-bundle.sh) | new | No, release-run | `stamp` writes the tag and date into AUDIT-CONTEXT and `routing.yaml`; `bundle` builds the deterministic offline bundle into `dist/`, prints its SHA-256 and adds the release row to `RELEASES.md`; never runs git |
| [`reducers/`](reducers/) | new | Never; the practitioner runs them offline, standard library only | One per export type (five SaaS admin exports, MCP configs, coding-agent settings), each printing only names declared in `routing.yaml` with integer, boolean or `not-checked` values; see the table below |
| [`hooks/pre-push-employer-denylist.sh`](hooks/pre-push-employer-denylist.sh) | new | No, by design; each maintainer installs it as a local `pre-push` hook | Refuses a push whose new commit messages or added lines contain any term from a private denylist held outside the repo; fails closed when the denylist is not configured; see the section below |
| [`test-checks.py`](test-checks.py) | new | Yes, in `test-instruments` | Runs each check above on a temporary copy of the tree (must pass) and on a copy with one planted defect (must fail and say why), and builds the bundle twice to show the hash is reproducible; where a check depends on a doc being absent (the pins doc, an Always Fetch doc), the test removes it in its own copy rather than reading that state off the tree |
| [`test-reducers.py`](test-reducers.py) | new | Yes, in `test-instruments` | Exact goldens for every reducer, no input string in output (emails, hostnames, identifiers, secret-shaped values, an injected instruction in plain and hidden text), every name declared, `emit` refusing undeclared names and string values, and reducer output read by `route.py` |

## What changed from the upstream copies

- `test-measure-link-reachability.py` reads `.github/workflows/checks.yml` instead of `link-checker.yml` when it extracts the awk gate. Two of its checks (the currency buckets, and the generated-inventory and hazard-exposure disclosures) read the upstream repo's own `archive/` lane and `INDEX.md`, neither of which this repo has, so the verbatim copy failed on this tree; those checks now run against small hermetic fixtures built in a temporary directory, which also pins the expected split instead of only checking a sum. It also gains a ninth group, which runs `--links` and `--include-archive` against an empty directory and against a fresh `git init` repo holding one untracked doc, and requires both to be refused.
- `measure-link-reachability.py` checked for an empty corpus only after the `--links` branch had already returned, so the reachability report refused an empty corpus while `--links` printed an all-zero table and exited 0, and the gate read that as no dangling links. The usual way to reach that state is a git repo whose docs are on disk but not yet tracked, since `git ls-files` then succeeds and returns nothing. The check now runs before any mode, and the error says whether the markdown is absent or merely untracked. This is the same fail-open class as the two below and is worth offering back upstream with them.
- `check-measurement-expiry.py` gains `--changed-files`. Upstream, the check failed for every expired claim anywhere, which turned the default branch red for a whole cohort of documents at once and blocked unrelated pull requests, including the one that would have fixed the expiry. It also scans `analysis/` recursively (so stubs are included), skips the template, refuses to report on a directory that does not exist, and its issue text no longer refers to the upstream repo's tooling. Two fail-open defects found while testing it are fixed here: an unquoted `revalidate: 2026-02-01` is parsed by PyYAML into a date object, which the upstream code handed to `strptime`, so the resulting TypeError was swallowed and the claim was never checked at all; and any file whose claims could not be read was reported as a warning and then counted as current. Both now fail the run (scoped to changed files when `--changed-files` is given), and both are worth offering back upstream.

## Reducers

Each reducer reads one kind of export on the practitioner's own machine and prints a short YAML block of signal keys and counts that the review reads under AUDIT-CONTEXT's Reducer Output rules. Every string in the input is sanitized before matching (`reducers/text_sanitize.py`), nothing from the input is printed, and `reducers/_common.py` refuses to print any name the reducer did not declare or any value that is not a count, true, false or `not-checked`. Which app and vendor names count as AI products is a Tier D heuristic in `reducers/ai_catalog.py`, so every count from it is a floor. Column aliases beyond the vendors' documented field names are stated in each reducer's docstring as the maintainer's assumption.

| Reducer | Input | Prints |
|---|---|---|
| [`entra_consent_grants.py`](reducers/entra_consent_grants.py) | Entra ID delegated permission grants with the app name joined on (CSV or JSON) | AI apps with grants; AI grants touching mail or files; user-consented and admin-consented AI grants; unparsed rows |
| [`google_workspace_oauth.py`](reducers/google_workspace_oauth.py) | Google Workspace OAuth log events export | AI apps with grants; AI grants touching mail or files; user-consented AI grants; unparsed rows |
| [`okta_apps.py`](reducers/okta_apps.py) | Okta Apps API JSON, or a CSV with the same fields | AI apps in the IdP; federated, not federated and inactive |
| [`browser_extensions.py`](reducers/browser_extensions.py) | Chrome Enterprise or Edge extension inventory | AI extensions by install mode; `surface-S3: true` when any is present |
| [`expense_ai_vendors.py`](reducers/expense_ai_vendors.py) | Card or expense export | Distinct AI vendors; matched lines; lines marked as reimbursed personal spend |
| [`mcp_config.py`](reducers/mcp_config.py) | One or more MCP configs (`.mcp.json`, `~/.claude.json`, Claude Desktop, Cursor, VS Code, Codex TOML) | Server, local, remote, pinned, unpinned and inline-secret counts; `mcp-unpinned`, `mcp-remote`, and `agent-static-secrets: true` when a secret is inline |
| [`coding_agent_settings.py`](reducers/coding_agent_settings.py) | Claude Code settings files and Cursor `hooks.json`, each optionally prefixed with its scope | Hook, fail-closed, deny-rule and lock counts; `coding-agent-managed-tier-absent`, `hook-fail-open`, `hooks-user-disableable`, `mcp-allowlist-absent`, each `not-checked` where the files cannot show it |

Run one like this, and paste only what it prints:

```bash
python3 scripts/reducers/mcp_config.py ~/.claude.json .mcp.json
python3 scripts/reducers/coding_agent_settings.py managed:/etc/claude-code/managed-settings.json project:.claude/settings.json
```

Each has a fixture under `reducers/fixtures/<name>/` (input, arguments, the canary strings that must never appear in output, and the hand-checked expected output).

## Local run

Every check CI runs, in the order it runs them:

```bash
python3 scripts/test-measure-link-reachability.py
python3 scripts/check-prompt-blocks.py
python3 scripts/check-routing-coverage.py
python3 scripts/route.py --check-fixtures
python3 scripts/check-exclusions.py
python3 scripts/test-checks.py
python3 scripts/test-reducers.py
python3 scripts/check-measurement-expiry.py --changed-files
```

The one dependency outside the standard library is PyYAML (CI pins 6.0.2); the reducers need none.

## The employer and identifier denylist hook

The employer and identifier denylist is deliberately not in CI. It runs as a local pre-push hook, [`hooks/pre-push-employer-denylist.sh`](hooks/pre-push-employer-denylist.sh), reading a file outside the repo, because a check backed by a secret list would still print its matches into public CI logs, and because the list itself is the thing that must not be published. The hook carries no names. It reads one term per line from the file named in the `SECURING_AI_DENYLIST` environment variable (blank lines and `#` comments ignored), matches case-insensitively as fixed strings rather than regular expressions, and scans the commit messages and every added line, file paths included, in each range being pushed.

It fails closed, which matters because this repo itself treats a fail-open hook as a finding (`hook-fail-open`): with the variable unset, or the file missing, unreadable or empty of terms, the push is refused with exit 2. `SECURING_AI_DENYLIST_SKIP=1` bypasses it for one command and says so, for a machine that has no denylist. `SECURING_AI_DENYLIST_WORDS=1` switches to whole-word matching, which cuts false positives from short terms.

To install it, from the repo root:

```bash
mkdir -p ~/.config/securing-ai && chmod 700 ~/.config/securing-ai
$EDITOR ~/.config/securing-ai/denylist.txt        # one term per line; never inside the working tree
cp scripts/hooks/pre-push-employer-denylist.sh .git/hooks/pre-push
chmod +x .git/hooks/pre-push
echo 'export SECURING_AI_DENYLIST="$HOME/.config/securing-ai/denylist.txt"' >> ~/.bashrc   # or your shell's profile
```

If the repo uses `core.hooksPath`, copy the script into that directory as `pre-push` instead. To check a list or a draft without pushing, run the script with `--scan-paths` and the files to read, which involves no git at all:

```bash
SECURING_AI_DENYLIST=~/.config/securing-ai/denylist.txt scripts/hooks/pre-push-employer-denylist.sh --scan-paths README.md analysis/*.md
```

A match prints the term and where it was found, on the maintainer's own terminal only. If the term is already in a commit, removing it from the working tree is not enough, and the commits need rewriting before the push.
