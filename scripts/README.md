# Scripts

Which scripts exist, where each came from, and whether anything runs it automatically. That last column matters in both directions, because a reader can assume a script is guarding something when nothing calls it, or assume it is inert when its output is something the repo depends on. To check for yourself, look for invocations rather than mentions:

```bash
grep -rn "python scripts/\|python3 scripts/" .github/workflows/*.yml
```

| Script | Origin | Runs automatically? | What it does |
|---|---|---|---|
| [`measure-link-reachability.py`](measure-link-reachability.py) | copied from claude-code-project-best-practices (MIT), with two changes: it fails closed on an empty or untracked corpus in `--links` mode, as the reachability report already did, and `--links` also reads reference-style definitions and checks `#anchors` against GitHub's heading slugs, counting a missing one as dangling | Yes, in the required `check-internal-links` job, on every pull request and push to `main` | With `--links`, counts internal markdown links by class; the job fails on any `dangling` row above zero, and on a corpus git does not track, so the gate cannot pass on a tree it never read |
| [`test-measure-link-reachability.py`](test-measure-link-reachability.py) | copied and adapted (see below) | Yes, in the required `test-instruments` job | Determinism across eight hash seeds, mode and entry-tier monotonicity, currency buckets, the disclosures, and the job's own awk gate against a clean and a broken corpus |
| [`check-measurement-expiry.py`](check-measurement-expiry.py) | copied and adapted (see below) | Yes, in `test-instruments`, scoped to a pull request's changed files | Fails only when an expired, undated or mistyped `measurement-claims` entry sits in a file the change touches; on other events prints the full count and passes, and the weekly standing issue carries that count |
| [`list-declared-gaps.py`](list-declared-gaps.py) | copied unchanged from claude-code-project-best-practices (MIT) | No, operator-run in the weekly review | Enumerates every `**Gap:** ... **Needs**:` declaration in `analysis/` |
| [`check-prompt-blocks.py`](check-prompt-blocks.py) | new | Yes, in `test-instruments` | README and ONE-LINE-PROMPT fetch-mode blocks byte-identical; with `--tag-commit` (which the workflow resolves, since the script never runs git) the block must pin that commit, and with no tag it must still carry the `<release-sha>` placeholder; in every mode the offline block must match the fetch block, the output template must not name a release, neither banner may claim placeholders beside a pinned block, and no fetched or bundled file may name another release's tag or SHA |
| [`check-routing-coverage.py`](check-routing-coverage.py) | new | Yes, in `test-instruments` | Keys unique and asked; factors fold into each band; every escalation has a machine-readable `escalate-if`; every `enables`, `requires` and `escalate-if` name exists; every surface enables a non-INVENTORY key; every family has a Question Packet owner; every shipped doc routed and its `applies-to-signals` matching the rows that route to it; the rendered AUDIT-CONTEXT section current. Routed docs not yet written are counted, and fail only with `--release` |
| [`render-audit-context.py`](render-audit-context.py) | new | No, operator-run after any `routing.yaml` edit; CI checks its output through the coverage check | Renders AUDIT-CONTEXT's routing section from `routing.yaml`; `--check` exits 1 when stale |
| [`route.py`](route.py) and [`../fixtures/`](../fixtures/) | new | Yes, in `test-instruments` (`--check-fixtures`) | The reference mapper: an Answers Block and any reducer outputs in, the branch, ranked actions (ordered by band, then factor sum, then the `sequence-order` block in `analysis/decision-sequence.md`, then row order), conflicts (an answer that contradicts its derivation, a yes to a row whose surfaces are not selected, a reducer value that disagrees with a stated one), any `not-applicable` rows, review rows, doc list and Question Packets out; checked against three hand-verified golden fixtures |
| [`check-exclusions.py`](check-exclusions.py) | new | Yes, in `test-instruments`, over the tree and, with `--messages`, over the commit messages a pull request or push adds | Temporary paths in `source:` fields, home-directory or private working-tree paths anywhere, the licence-restricted crosswalk folder, 2025-form OWASP LLM IDs, the not-legal-advice sentence missing from either prompt block, the output format or the law doc, any file that is not valid UTF-8 (a failure, not a skip), invisible or control characters, and credential-shaped strings (never printed); every file is scanned except known binary types, and the reducer fixtures are exempt from the last two rules because they carry such strings on purpose |
| [`check-pins.py`](check-pins.py) | new | No, weekly review | Counts docs whose `pins:` differ from `analysis/revalidation-and-pins.md`, after dropping a trailing parenthetical or `@` and matching a longer name that extends a canon name with no digits (`CISA KEV catalogVersion`, `CoSAI secure-ai-tooling risk-map`), with a SHA matching its abbreviation; counts and lists every doc-local pin that matches no canon name; fails only when the pins doc itself lacks a version or, given `--current`, is behind the newest known release |
| [`probe-source-accessibility.py`](probe-source-accessibility.py) | new | Yes, in the scheduled `check-source-accessibility` job, which never runs on a pull request | Reads the pinned versions from `analysis/revalidation-and-pins.md`, fetches the pinned ATLAS, OCSF, MCP specification, CoSAI and OWASP pages, and reports for each whether the page answers and whether the upstream moved past its pin (newest release tag, or a change to CoSAI's component file since the pinned commit); its tally line counts `unknown` beside broken, refused and moved (a moved-past-pin probe that failed, or a pin it could not find), and the weekly standing issue reads clean only when that is zero and no SOURCES.md URL is broken; `--current FILE` writes the newest-known versions in the form `check-pins.py --current` reads. Never fails on what it finds, exits 2 when it cannot read the pins doc |
| [`build-release-bundle.sh`](build-release-bundle.sh) | new | No, release-run | `stamp` writes the tag and date into AUDIT-CONTEXT and `routing.yaml` and retires every pre-release statement (AUDIT-CONTEXT's banner, the ONE-LINE-PROMPT paragraph, the `routing.yaml` header comment, the README status banner, the `Release:` line in the pins doc) and resets both prompt blocks to the placeholders, writing nothing unless all of them match; `bundle` reads the given commit with `git archive` (never the working tree), refuses when a local tag of that name points elsewhere, when `check-prompt-blocks.py` fails on the commit, while any Always Fetch or routed doc is missing or any pre-release wording survives, then builds the deterministic offline bundle and a `git archive` tar of `scripts/reducers/` from the same commit into `dist/`, prints both SHA-256 values and adds the release row to `RELEASES.md` with the reducer archive's hash in the Notes column; runs read-only git only. A tag push also rebuilds both in the `rebuild-release-bundle` job and prints the hashes to its summary |
| [`reducers/`](reducers/) | new | Never; the practitioner runs them offline, standard library only | One per export type (five SaaS admin exports, MCP configs, coding-agent settings), each printing only names declared in `routing.yaml` with integer, boolean or `not-checked` values; see the table below |
| [`hooks/pre-push-employer-denylist.sh`](hooks/pre-push-employer-denylist.sh) | new | No, by design; each maintainer installs it as a local `pre-push` hook | Refuses a push whose new commit messages, author or committer fields, ref names, annotated tag messages, added lines, new or renamed paths or binary file contents contain any term from a private denylist held outside the repo; fails closed when the denylist is not configured; see the section below |
| [`test-checks.py`](test-checks.py) | new | Yes, in `test-instruments` | Runs each check above on a temporary copy of the tree (must pass) and on a copy with one planted defect (must fail and say why), and builds the bundle twice to show the hash is reproducible; where a check depends on a doc being absent (the pins doc, an Always Fetch doc), the test removes it in its own copy rather than reading that state off the tree |
| [`test-reducers.py`](test-reducers.py) | new | Yes, in `test-instruments` | Exact goldens for every reducer, no input string in output (emails, hostnames, identifiers, secret-shaped values, an injected instruction in plain and hidden text), every name declared, `emit` refusing undeclared names and string values, reducer output read by `route.py`, and a robustness pass: each reducer's `malformed.json` fixture, wrong columns, an empty export and one page of a paginated response refused with nothing on standard output, JSONC and NDJSON read, a skipped file turning a clean-reading value into `not-checked`, near-miss catalogue names, and both directions of the secret, pin, personal-spend and managed-tier matching |
| [`test-hooks.py`](test-hooks.py) | new | Yes, in `test-instruments` | The denylist hook's exit codes 0, 1 and 2 against a made-up term in a temporary denylist and throwaway repositories (the real denylist is never read), including a term in an author or committer field, a ref name, a renamed path, a binary file, beside a non-UTF-8 byte, and a byte-order mark on the denylist's first line |
| [`test-scripts.py`](test-scripts.py) | new | Yes, in `test-instruments` | Planted cases for `check-pins.py`'s name normalization, the expiry check's refusal of undated or mistyped claims, the probe's tally (an API failure and a 403 each keep the standing issue open), the link gate's reference links and anchors, the exclusion check's new rules, and the bundle's reducer archive (in the row, reproducible) |

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
| [`mcp_config.py`](reducers/mcp_config.py) | One or more MCP configs (`.mcp.json`, `~/.claude.json`, Claude Desktop, Cursor, VS Code, Codex TOML) | Server, local, remote, pinned, unpinned, unread-launch and inline-secret counts; `mcp-unpinned` (`not-checked` when none is unpinned but a launch could not be read), `mcp-remote`, and `agent-static-secrets: true` when a secret is inline |
| [`coding_agent_settings.py`](reducers/coding_agent_settings.py) | Claude Code settings files and Cursor `hooks.json`, each optionally prefixed with its scope | Hook, fail-closed, deny-rule and lock counts; `coding-agent-managed-tier-absent`, `hook-fail-open`, `hooks-user-disableable`, `mcp-allowlist-absent`, each `not-checked` where the files cannot show it |

Run them from a checkout of the release tag the review pins, so the reducers are the ones the release hashed (the tag and the reducer archive's SHA-256 are in `RELEASES.md`), and paste only what they print on standard output. Standard error carries only fixed notices (a sanitize count, a skipped file) and never input text or a path, but it is not part of what a review reads.

```bash
git checkout vYYYY.MM          # the tag named in the review's prompt block
python3 scripts/reducers/mcp_config.py ~/.claude.json .mcp.json
python3 scripts/reducers/coding_agent_settings.py managed:/etc/claude-code/managed-settings.json project:.claude/settings.json
```

Each has a fixture under `reducers/fixtures/<name>/` (input, arguments, the canary strings that must never appear in output, the hand-checked expected output, and a `malformed.json` the reducer must refuse).

A reducer that cannot read its input completely prints nothing on standard output and exits 2 with one fixed line on standard error: an unparseable file, a single-export reducer given a file with none of its expected columns or no rows at all, or one page of a paginated API response (a `@odata.nextLink`, `nextPageToken` or similar key beside the list; merge every page into one JSON list first). The two multi-file reducers skip an unparseable file, say how many they skipped, and print `not-checked` for any value the skipped file could have changed. JSON with comments (VS Code's `mcp.json`) and one JSON object per line are both read.

### Export recipes

Two things in the Entra recipe were read at Microsoft Learn on 2026-11-24 (Tier B for what each endpoint returns): the [oauth2PermissionGrant list](https://learn.microsoft.com/en-us/graph/api/oauth2permissiongrant-list?view=graph-rest-1.0) page, for the `GET /oauth2PermissionGrants` path, its `Get-MgOauth2PermissionGrant` cmdlet and the `clientId`, `consentType` (`AllPrincipals` in its example) and `scope` fields, and the [appRoleAssignedTo list](https://learn.microsoft.com/en-us/graph/api/serviceprincipal-list-approleassignedto?view=graph-rest-1.0) page, for app-only permissions. The rest of it (the `Principal` value, which the reducer docstring takes from the resource page, the `-All` paging switch, `@odata.nextLink` and the `Get-MgServicePrincipal` join) is the maintainer's reading and was not re-read for this note, and none of it has been run against a live tenant. The other recipes are the maintainer's reading of each console and are neither re-read nor run for this note (Tier D); the column aliases each reducer accepts are in its docstring.

- **Entra delegated grants** (`entra_consent_grants.py`). `GET /oauth2PermissionGrants` (`Get-MgOauth2PermissionGrant -All` in the Microsoft Graph PowerShell SDK) returns `clientId`, `consentType` (`AllPrincipals` or `Principal`) and `scope`, but the client only as an ID, so join each grant to its service principal's `displayName` (`Get-MgServicePrincipal -ServicePrincipalId <clientId>`) and export one row per grant with `displayName`, `consentType` and `scope`. Follow every `@odata.nextLink` page (the SDK's `-All` does) before exporting; the reducer refuses a page that still carries one.
- **Entra application permissions** are not covered. App-only permissions are app role assignments (`GET /servicePrincipals/{id}/appRoleAssignedTo` on a resource such as Microsoft Graph's service principal lists the clients granted app-only permissions to it), which carry no `consentType` and name the role by `appRoleId`, so the reducer counts such rows in `grant-rows-unparsed` rather than reading them. Review them by hand until a reducer for them exists.
- **Google Workspace** (`google_workspace_oauth.py`). The Admin console's OAuth log events (Reporting, Audit and investigation), downloaded as CSV with the event name, application name, scope and user columns. Without a user column the reducer counts grant rows, which can count repeated events for one user more than once.
- **Okta** (`okta_apps.py`). The Apps API (`GET /api/v1/apps`) as JSON, with every page merged into one list (the API pages through a `Link` header, which a saved body does not carry, so merging is on the person exporting), or a CSV with the same `label`, `signOnMode` and `status` fields.
- **Browser extensions** (`browser_extensions.py`). The Chrome Enterprise apps and extensions usage report, or Edge's extension inventory, exported as CSV with the extension name, ID and install type.
- **Card and expense** (`expense_ai_vendors.py`). Any line-level export with a merchant or description column; a reimbursable, payment-method, card-type or funding-source column lets the reducer count reimbursed personal spend.
- **MCP configs and coding-agent settings** (`mcp_config.py`, `coding_agent_settings.py`). The files themselves, from the paths in each reducer's docstring; pass `managed:` before a copy of a managed settings file taken off a machine, since only a file at a documented system path is classed as managed without it.

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
python3 scripts/test-hooks.py
python3 scripts/test-scripts.py
python3 scripts/check-measurement-expiry.py --changed-files
```

CI also runs `check-exclusions.py --messages` over the commit messages a pull request adds; the local equivalent is `git log --format='%an%n%ae%n%B' origin/main..HEAD | python3 scripts/check-exclusions.py --messages -`.

The one dependency outside the standard library is PyYAML (CI installs 6.0.2 with `pip install --require-hashes -r .github/requirements-ci.txt`); the reducers need none.

Run with no arguments on the default branch after a release, `check-prompt-blocks.py` prints `FAIL no release tag given but the block pins '<sha>'` and exits 1, and that is the check working as designed rather than a defect. With no `--tag-commit` the script assumes the repo is unreleased and requires the `<release-sha>` placeholder, because it never runs git itself, so after the first release it needs to be told which commit the newest tag points at. CI resolves that from the tags (`.github/workflows/checks.yml`), and the local equivalent is:

```bash
TAG=$(git tag --list 'v*' --sort=-v:refname | grep -E '^v[0-9]{4}\.[0-9]{2}(\.[0-9]+)?$' | head -n1)
python3 scripts/check-prompt-blocks.py --tag "$TAG" --tag-commit "$(git rev-list -n1 "$TAG")"
```

On the commit the tag itself points at, CI runs it with no arguments, because that commit carries the placeholders: the stamp step in `build-release-bundle.sh` resets both prompt blocks to `<release-sha>` and `<vYYYY.MM>` before the commit is tagged (see `RELEASES.md` for why a commit cannot contain its own SHA), and the bundle step runs the same no-argument check on the archived commit and refuses to build when it fails. Through v2026.12.1 the stamp did not reset the blocks, so the v2026.12 and v2026.12.1 tagged commits each pin the release before them. In every mode the script also fails when a file the review fetches or the bundle holds names a release other than the one on AUDIT-CONTEXT's `Release:` line (by tag in AUDIT-CONTEXT, ONE-LINE-PROMPT, routing.yaml and README, by commit SHA in every fetched or bundled file), when the offline block's commit or tag differs from the fetch block's, and when the Structured Output Format's `release:` line names a release instead of saying where to copy it from.

## The README count line

The README carries one count line (DECISIONS.md, Decision 8), and `check-routing-coverage.py` prints two document counts beside it that look as if they should match it and do not, because each counts a different set. This section explains the relationship without restating the numbers, since Decision 8 keeps the counts in the README line alone.

| Count | Where it is printed | What it counts |
|---|---|---|
| routable docs | README count line | Top-level `analysis/*.md` files with status `PRODUCTION` or `EMERGING`, excluding the template; this includes the four Always Fetch documents and leaves out `VERIFICATION-LOG.md`, whose status is `REFERENCE` |
| shipped docs checked | `check-routing-coverage.py` | The routable documents plus the stubs under `analysis/stubs/`, which is every document the coverage check reads for `applies-to-signals`, so it equals the README's routable and stub figures added together |
| docs routed | `check-routing-coverage.py` | Distinct documents named in some signal row's `docs` list, which is the shipped figure less any Always Fetch document that no signal row names (`check-routing-coverage.py` does not list them by name; compare `routing.yaml` `always-fetch` with the rows' `docs`), since every review reads those through the `always-fetch` list instead |

An Always Fetch document that a signal row also names counts as routed. The weekly review re-derives the README line from disk with the procedure in `.claude/commands/maintenance/weekly-review.md` (step 2), and that procedure, not this table, is the definition.

## The employer and identifier denylist hook

The employer and identifier denylist is deliberately not in CI. It runs as a local pre-push hook, [`hooks/pre-push-employer-denylist.sh`](hooks/pre-push-employer-denylist.sh), reading a file outside the repo, because a check backed by a secret list would still print its matches into public CI logs, and because the list itself is the thing that must not be published. The hook carries no names. It reads one term per line from the file named in the `SECURING_AI_DENYLIST` environment variable (blank lines and `#` comments ignored, a byte-order mark or CRLF line ends stripped), matches case-insensitively as fixed strings rather than regular expressions, and treats every input as text, so a non-UTF-8 or NUL byte beside a term cannot hide it. In each range being pushed it scans the commit messages, the author and committer names and emails, the local and remote ref names, an annotated tag's message, every added line, the new path of every added, copied, modified or renamed file, and the contents of every added or modified binary file, which a diff shows as no added line at all. `scripts/test-hooks.py` tests all of this against a made-up term in CI.

It fails closed, which matters because this repo itself treats a fail-open hook as a finding (`hook-fail-open`): with the variable unset, or the file missing, unreadable or empty of terms, the push is refused with exit 2. `SECURING_AI_DENYLIST_SKIP=1` bypasses it for one command and says so, for a machine that has no denylist. `SECURING_AI_DENYLIST_WORDS=1` switches to whole-word matching, which cuts false positives from short terms.

To install it, from the repo root:

```bash
mkdir -p ~/.config/securing-ai && chmod 700 ~/.config/securing-ai
$EDITOR ~/.config/securing-ai/denylist.txt        # one term per line; never inside the working tree
cp scripts/hooks/pre-push-employer-denylist.sh .git/hooks/pre-push
chmod +x .git/hooks/pre-push
echo 'export SECURING_AI_DENYLIST="$HOME/.config/securing-ai/denylist.txt"' >> ~/.bashrc   # or your shell's profile
```

A copied hook stays at the version copied, so copy it again whenever this file changes (the scans above arrived after earlier installs). A symlink would never go stale, but it would run whatever the checked-out branch says, so a branch could switch the check off for its own push; the copy is the documented install for that reason. If the repo uses `core.hooksPath`, copy the script into that directory as `pre-push` instead. To check a list or a draft without pushing, run the script with `--scan-paths` and the files to read, which involves no git at all:

```bash
SECURING_AI_DENYLIST=~/.config/securing-ai/denylist.txt scripts/hooks/pre-push-employer-denylist.sh --scan-paths README.md analysis/*.md
```

A match prints the term and where it was found, on the maintainer's own terminal only. If the term is already in a commit, removing it from the working tree is not enough, and the commits need rewriting before the push.
