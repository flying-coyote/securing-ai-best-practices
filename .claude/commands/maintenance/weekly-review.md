# Weekly Maintenance Review

Run the weekly mechanical review of this repository. The prompt is standalone, so run it in a fresh session with the working directory at the repo root, and everything it needs is either in this file or derivable from disk. Derive every count and date from disk on each run rather than trusting what a document says about itself, because the README's count line and the root-doc currency markers are exactly the claims this review exists to check.

This review is mechanical. Judgement work (re-reading absorbers, reading upstream release notes, re-checking the default-state table) belongs to the quarterly sweep, which writes a dated file under `scans/` named `scans/SCAN-YYYY-MM-DD.md`, and this review only reports how many days have passed since the newest one. Adapted from the weekly review in claude-code-project-best-practices (MIT).

Every step writes its scratch output into one temporary directory, so start with:

```bash
WR=$(mktemp -d)
```

## Steps

1. Gather the week's activity.

   ```bash
   git fetch --prune origin
   git log --since="7 days ago" --oneline
   ```

   Note which analysis documents, stubs, routing rows and scripts changed, since those are the places a drifted count or a stale marker usually comes from.

2. Re-derive the README count line. DECISIONS.md says the README carries exactly one count line and no other file states those counts. A routable document is a top-level `analysis/*.md` file with status `PRODUCTION` or `EMERGING`, excluding the template, and the count includes the four Always Fetch documents that `routing.yaml` lists (they are reported separately as `always` as well, since they are fetched on every review rather than routed to by a signal); a stub is the same test applied to `analysis/stubs/*.md`; a signal is one row under `signals:` in `routing.yaml`.

   ```bash
   read routable always stubs signals <<<"$(python3 - <<'PY'
   import re, yaml, pathlib
   def status(p):
       m = re.match(r"^---\n(.*?)\n---\n", p.read_text(encoding="utf-8"), re.S)
       return (yaml.safe_load(m.group(1)) or {}).get("status") if m else None
   r = yaml.safe_load(open("routing.yaml", encoding="utf-8"))
   af = set(r.get("always-fetch") or [])
   live = {"PRODUCTION", "EMERGING"}
   top = [p for p in sorted(pathlib.Path("analysis").glob("*.md"))
          if p.name != "CANONICAL-DOC-TEMPLATE.md" and status(p) in live]
   routable = top
   always = [p for p in top if p.as_posix() in af]
   stubs = [p for p in sorted(pathlib.Path("analysis/stubs").glob("*.md")) if status(p) in live]
   print(len(routable), len(always), len(stubs), len(r.get("signals") or []))
   PY
   )"
   grep -nE '^[0-9]+ routable docs, [0-9]+ signals, [0-9]+ stubs, last derived [0-9]{4}-[0-9]{2}-[0-9]{2}\.' README.md
   ```

   Compare the three numbers in that README line against `routable`, `signals` and `stubs`, and check that `always` is 4. If any number disagrees, rewrite the line by hand with the derived values and today's date, and set `readme-match=no` for this run (the fix is recorded next week as a match). If the grep finds no line at all, that is also `readme-match=no`, since the line is what the decision requires.

3. Run the deterministic checks the required CI job runs, so a red default branch shows up here even if nobody opened the Actions tab.

   ```bash
   python3 scripts/check-routing-coverage.py > "$WR/routing.txt" 2>&1 && routing=PASS || routing=FAIL
   python3 scripts/route.py --check-fixtures  > "$WR/fixtures.txt" 2>&1 && fixtures=PASS || fixtures=FAIL
   python3 scripts/check-exclusions.py        > "$WR/excl.txt" 2>&1 && exclusions=PASS || exclusions=FAIL
   python3 scripts/check-prompt-blocks.py     > "$WR/blocks.txt" 2>&1 && blocks=PASS || blocks=FAIL
   python3 scripts/test-reducers.py           > "$WR/reducers.txt" 2>&1 && reducers=PASS || reducers=FAIL
   grep -E 'not yet written' "$WR/routing.txt"
   ```

   Any `FAIL` forces `DRIFT`. The routing check also prints how many routed documents are not yet written; that number is allowed before a release and fails only under `--release`, so read it as a progress figure rather than a defect, and note it beside next week's priorities.

4. Measurement expiry, full count.

   ```bash
   python3 scripts/check-measurement-expiry.py --changed-files > "$WR/expiry.txt" 2>&1
   expired=$(grep -oE 'expired-claims total=[0-9]+' "$WR/expiry.txt" | cut -d= -f2)
   unreadable=$(grep -oE 'unreadable total=[0-9]+' "$WR/expiry.txt" | cut -d= -f2)
   ```

   Given no paths, the script reports the full count and never fails, which is why the review reads the numbers rather than the exit code. A non-zero `expired` forces `DRIFT`, and so does a non-zero `unreadable`, because a claim the script could not parse is a claim nobody is checking. An empty value for either means the script's output changed shape, and the review must not record a number it did not read.

5. Pins and the KEV snapshot.

   ```bash
   python3 scripts/check-pins.py > "$WR/pins.txt" 2>&1 && pins_doc=PASS || pins_doc=FAIL
   pins_behind=$(grep -oE 'docs pins behind: [0-9]+' "$WR/pins.txt" | grep -oE '[0-9]+$')
   # optional, needs network: compare the pins doc against the newest releases
   python3 scripts/probe-source-accessibility.py --current "$WR/pins-current.yaml" && \
     python3 scripts/check-pins.py --current "$WR/pins-current.yaml"
   ```

   `pins_behind` is reported and never gated, since a document one release behind is a revalidation task rather than a broken build. `pins_doc=FAIL` forces `DRIFT`, because `analysis/revalidation-and-pins.md` is the document every review prints. The scheduled `check-source-accessibility` job writes the same probe into the standing issue each Monday, so the optional run here is for a week when that issue looks stale. The CISA KEV pin is bumped by hand in this step, by reading the current `catalogVersion` from the feed and updating the pin and its row in the pins document, because the catalogue changes several times a week and is deliberately kept out of the newest-known versions file.

6. SOURCES freshness.

   ```bash
   curated=$(grep -m1 -oE '^Last curated: [0-9]{4}-[0-9]{2}-[0-9]{2}' SOURCES.md | grep -oE '[0-9-]{10}$')
   curated_age=$(( ( $(date +%s) - $(date -d "$curated" +%s) ) / 86400 ))
   ```

   If `curated_age` is over 45 days, add a SOURCES curation pass to next week's priorities, and the run is `DRIFT`. Skim the unverified quarantine at the end of SOURCES.md for any item whose stated revalidation condition came due this week.

7. Convergence fields. DECISIONS.md (Decision 7) has every document born `convergence: single-source`, with `converged` granted at birth only by the standards route (a published standard, statute or schema prescribes the practice and at least one independent implementation exists) and otherwise only by this review on recorded external adoption evidence. No function in this repo is rated above `single-source` yet, so any other value is a change this review has to have seen.

   ```bash
   conv_present=0
   for f in analysis/*.md analysis/stubs/*.md; do
     [ "$f" = "analysis/CANONICAL-DOC-TEMPLATE.md" ] && continue
     v=$(grep -m1 '^convergence:' "$f" | awk '{print $2}')
     if [ -z "$v" ]; then echo "MISSING convergence: $f"; continue; fi
     conv_present=$((conv_present + 1))
     [ "$v" != "single-source" ] && echo "CHECK convergence=$v: $f"
   done
   ```

   A missing field forces `DRIFT`. A `CHECK` line is not a defect in itself, but the document must cite, in its own text, either the standard and the independent implementation or the adoption evidence that justified the upgrade; if it cites neither, set the value back to `single-source` and record why. Never write adoption evidence that was not found, and when in doubt the value stays `single-source`.

8. Absorption-map consistency. This is greps only, with no fetching; judging whether an absorber now covers a document is the quarterly sweep's job.

   ```bash
   map_rows=$(grep -cE '^\| \[?`?analysis/' ABSORPTION-MAP.md)
   follows_docs=$(grep -l '^follows:' analysis/*.md 2>/dev/null | grep -v CANONICAL-DOC-TEMPLATE | wc -l)
   retiring_docs=$(grep -l '^replacement-by:' analysis/*.md 2>/dev/null | grep -v CANONICAL-DOC-TEMPLATE | wc -l)
   lane_conflicts=$(grep -l '^follows:' analysis/*.md 2>/dev/null | grep -v CANONICAL-DOC-TEMPLATE | xargs -r grep -l '^replacement-by:' | wc -l)
   sweep_line=$(grep -m1 'Last verified sweep' ABSORPTION-MAP.md)
   if echo "$sweep_line" | grep -qi 'none yet'; then map_verified=none
   else map_verified=$(echo "$sweep_line" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -1); map_verified=${map_verified:-none}; fi
   ```

   `map_rows` should equal `routable + stubs`, one row per routable document and per stub; every document carrying `follows:` needs a `follow`-lane row and every `replacement-by:` document a `retire-toward`-lane row, which is worth spot-checking by name and not only by count; and `lane_conflicts` must be 0, because the two fields are mutually exclusive. The `none yet` test comes first because that line can say no sweep has run while still carrying the date of the map's initial fill, which is not a sweep date, and the `head -1` matters because a line carrying two dates would otherwise produce a two-line value that parses as no date and silently disables the age check. If `map_verified` is more than 100 days old, or is `none` once the repository is more than 100 days old (see step 12 for the first-commit date), add an absorption sweep to next week's priorities. The map is derived, so on any conflict the per-document frontmatter wins and the map is corrected to match it.

9. Internal links and reachability. This repo has no `CLAUDE.md`, and its front door is the README, so reachability is measured from the E3 entry tier.

   ```bash
   python3 scripts/measure-link-reachability.py --links > "$WR/links.txt"
   python3 scripts/measure-link-reachability.py --currency > "$WR/currency.txt"
   python3 scripts/measure-link-reachability.py --entry E3 --mode refs > "$WR/reach.txt"
   dangling_live=$(awk '$1=="dangling"{print $2; exit}' "$WR/links.txt")
   if grep -q 'no dead lane found' "$WR/currency.txt"; then wrong_status=0
   else wrong_status=$(grep -oE 'WRONG=[0-9]+' "$WR/currency.txt" | cut -d= -f2 | paste -sd+ | bc); fi
   guidance=$(grep -oE 'guidance [0-9]+/[0-9]+' "$WR/reach.txt" | tail -1 | awk '{print $2}')
   ```

   `dangling_live` must be 0, since a non-zero value is a live document pointing at something that is not there, and removing or renaming a document is the usual cause. `wrong_status` must be 0; the repo has no archive lane today, which is why the instrument reports no dead lane and the value is 0 by construction, but the check stays so that the first archive pass is covered from the day it exists. `guidance` must be `n/n`, every guidance file reachable from the README.

   Then run the instrument's own determinism test. It takes a little over two minutes (eight hash seeds across every mode over the whole corpus), which is past a two-minute foreground tool timeout, so run it in the background and read the result when it lands rather than shortening it, because the multi-seed sweep is what once caught the instrument returning a different count depending on the hash seed.

   ```bash
   python3 scripts/test-measure-link-reachability.py > "$WR/instrument.txt" 2>&1 && instrument=OK || instrument=BROKEN
   ```

   `instrument=BROKEN` means the three numbers above are not trustworthy and must not be recorded for this run.

10. Declared gaps, enumerated and never gated.

    ```bash
    python3 scripts/list-declared-gaps.py
    declared_gaps=$(python3 scripts/list-declared-gaps.py --json | python3 -c 'import json,sys; print(json.load(sys.stdin)["count"])')
    ```

    The template's `**Gap:** ... **Needs**:` convention is how a document says what it does not know, and this step exists so those declarations get read somewhere other than inside the document that makes them. A rising count is not a defect, because declaring a gap and leaving it open is an honest outcome and a target here would reward deleting declarations over closing them. Read the list, decide whether any gap became closable this week (a new release, a lab result landing, a published crosswalk), and carry those into next week's priorities.

11. Root-doc currency markers, compared against git.

    ```bash
    stale_markers=0
    for f in DECISIONS.md AUDIT-CONTEXT.md SOURCES.md CONTRIBUTING.md README.md RELEASES.md; do
      [ -f "$f" ] || continue
      oldest=$(grep -oiE '^[*_ ]*\*{0,2}last (updated|curated)[^0-9]{0,6}(([0-9]{4}-[0-9]{2}-[0-9]{2})|([A-Z][a-z]+ [0-9]{1,2}, [0-9]{4}))' "$f" \
               | grep -oE '([0-9]{4}-[0-9]{2}-[0-9]{2})|([A-Z][a-z]+ [0-9]{1,2}, [0-9]{4})' \
               | while read -r d; do date -d "$d" +%Y-%m-%d 2>/dev/null; done | sort | head -1)
      [ -z "$oldest" ] && continue
      edited=$(git log -1 --format=%ad --date=short -- "$f")
      if [[ "$oldest" < "$edited" ]]; then
        echo "STALE MARKER  $f  says $oldest, last edited $edited"
        stale_markers=$((stale_markers + 1))
      fi
    done
    ```

    `stale_markers` must be 0, because a currency marker that a content edit did not update certifies a freshness the file no longer has. The loop takes the oldest marker in each file rather than the newest, so a fresh header beside a stale footer is still caught, and it anchors the match to the start of a line, so prose that quotes a marker is not read as one. A file with no marker is fine. `ABSORPTION-MAP.md` is left out on purpose, since its date records a sweep rather than an edit and step 8 checks it against the right threshold. The AUDIT-CONTEXT release header is stamped by the release script and is not a currency marker.

12. Repository settings, stale branches and the quarterly sweep.

    ```bash
    REPO=flying-coyote/securing-ai-best-practices
    protected=$(gh api "repos/$REPO/branches/main" --jq .protected 2>/dev/null || echo unknown)
    read del_on_merge squash merge_commit rebase <<<"$(gh api "repos/$REPO" --jq '[.delete_branch_on_merge,.allow_squash_merge,.allow_merge_commit,.allow_rebase_merge]|map(tostring)|join(" ")' 2>/dev/null || echo 'unknown unknown unknown unknown')"
    force_push=$(gh api "repos/$REPO/branches/main/protection" --jq .allow_force_pushes.enabled 2>/dev/null || echo unknown)
    required=$(gh api "repos/$REPO/branches/main/protection" --jq '[.required_status_checks.checks[].context]|sort|join(",")' 2>/dev/null || echo unknown)

    stale_branches=0
    now=$(date +%s)
    for ref in $(git for-each-ref --format='%(refname:short)' refs/remotes/origin/ | grep -vE '^origin(/HEAD|/main)?$'); do
      age=$(( (now - $(git log -1 --format=%ct "$ref")) / 86400 ))
      ahead=$(git cherry origin/main "$ref" | grep -c '^+')
      if [ "$age" -gt 7 ] && [ "$ahead" -gt 0 ]; then
        merged_pr=$(gh pr list -R "$REPO" --head "${ref#origin/}" --state merged --json number --jq 'length' 2>/dev/null || echo "?")
        echo "STALE BRANCH  $ref  ${age}d old, $ahead unmerged patch(es), merged PRs from it: $merged_pr"
        stale_branches=$((stale_branches + 1))
      fi
    done

    first_commit=$(git log --reverse --format=%ad --date=short | head -1)
    latest_scan=$(ls scans/SCAN-*.md 2>/dev/null | sed -E 's/.*SCAN-([0-9-]{10})\.md/\1/' | sort | tail -1)
    if [ -n "$latest_scan" ]; then
      scan_days=$(( (now - $(date -d "$latest_scan" +%s)) / 86400 ))
    else
      scan_days="none"
      repo_days=$(( (now - $(date -d "$first_commit" +%s)) / 86400 ))
    fi
    ```

    CONTRIBUTING.md's branch section names the two required checks, squash-only merges and deletion of the branch on merge, and protection on `main` with no force push is what makes those checks binding, so the expected values are `protected=true`, `required=check-internal-links,test-instruments`, `force_push=false`, `del_on_merge=true`, `squash=true`, `merge_commit=false` and `rebase=false`. Any other value, `unknown` included, forces `DRIFT`, because a setting that was written down and never applied, or applied and later loosened, is the exact failure this line exists to catch. If the required list comes back empty but protection is on, the API may be reporting checks under `contexts` instead, so read `.required_status_checks.contexts` before calling it drift.

    A stale branch is a remote branch older than seven days carrying patches that `main` does not. Squash merges change patch identity, so a branch whose work was squash-merged still shows patches here, which is why the loop also counts merged PRs from it; a branch with a merged PR is reap-able once you have looked, and one without is unmerged work someone should decide about. With delete-branch-on-merge on, either kind should be rare, and any non-zero `stale_branches` forces `DRIFT`.

    `scan_days` over 92 forces `DRIFT`. When no scan file exists yet, `scan_days` prints `none`, and that forces `DRIFT` only once `repo_days` passes 92, so a new repository is not flagged for a sweep it could not yet have run.

13. Identify blockers and set next week's priorities. List anything steps 2 to 12 flagged that this pass did not fix, any document waiting on a source or a lab result, and any declared gap from step 10 that became closable. This repo keeps no plan file, so the priorities go into the session's hand-off summary, and every `DRIFT` item must appear there.

14. Print the self-test line. The run ends by printing exactly one line in this shape, with every value derived during this run.

    ```bash
    echo "WEEKLY-REVIEW SELF-TEST: routable=$routable always-fetch=$always stubs=$stubs signals=$signals readme-match=<yes|no> routing=$routing fixtures=$fixtures exclusions=$exclusions prompt-blocks=$blocks reducers=$reducers expired-claims=$expired unreadable-claims=$unreadable pins-doc=$pins_doc pins-behind=$pins_behind sources-curated=$curated convergence-fields=$conv_present/$((routable + stubs)) absorption-rows=$map_rows/$((routable + stubs)) follows=$follows_docs lane-conflicts=$lane_conflicts map-verified=$map_verified dangling-live=$dangling_live wrong-status=$wrong_status guidance=$guidance instrument=$instrument declared-gaps=$declared_gaps stale-markers=$stale_markers protected=$protected required=$required force-push=$force_push delete-on-merge=$del_on_merge squash-only=$squash/$merge_commit/$rebase stale-branches=$stale_branches days-since-quarterly-scan=$scan_days => <OK|DRIFT>"
    ```

    `OK` means every comparison above matched and nothing is overdue. Any of the following makes it `DRIFT`, and each drifted check must already be in step 13's priorities: a README mismatch; a failing routing, fixture, exclusion, prompt-block, reducer or pins-doc check; a non-zero expired or unreadable claim count; SOURCES curated more than 45 days ago; a missing convergence field; absorption rows short of `routable + stubs`, a non-zero `lane_conflicts`, or an overdue sweep date; a non-zero `dangling-live` or `wrong-status`, a `guidance` figure that is not `n/n`, or `instrument=BROKEN`; a non-zero `stale-markers`; any repository setting off its expected value; a non-zero `stale-branches`; or the quarterly scan overdue as step 12 defines it. `pins-behind` and `declared-gaps` are reported and never gated, for the reasons in steps 5 and 10. If the line cannot be printed with real values, the review did not run its checks, and saying it did is the failure this line exists to prevent.

15. Commit, if the review changed anything. Only the files this review edits, by explicit path: `README.md` (the count line), `ABSORPTION-MAP.md` (a correction to match frontmatter), `analysis/revalidation-and-pins.md` (the KEV pin) and any document whose convergence value was set back. Use one branch for the review and merge it through a pull request, since `main` is protected.

    ```bash
    git switch -c "weekly-review-$(date +%F)"
    git add README.md ABSORPTION-MAP.md analysis/revalidation-and-pins.md   # only those that changed
    git commit -m "Weekly review $(date +%F)"
    ```

## Expected outcome

The README count line matches what is on disk; the deterministic checks the required CI job runs pass on the default branch; no measurement claim has expired or gone unread; the pins document is current and the KEV pin carries this week's snapshot; SOURCES curation is inside 45 days; every live document carries a convergence value that its own text justifies; the absorption map is row-consistent with per-document frontmatter; no live document has a dangling internal link and every guidance file is reachable from the README; the declared gaps have been read; no root document claims a currency date its own later edits have passed; branch protection and the merge settings match CONTRIBUTING.md's branch section, with no stale branch carrying unmerged work; the days since the last quarterly scan are known; and the run printed its one-line self-test.
