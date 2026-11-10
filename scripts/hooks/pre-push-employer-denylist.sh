#!/usr/bin/env bash
# pre-push-employer-denylist.sh: block a push whose new content names anything
# on a private denylist (employer names, internal hostnames, colleague names,
# identifiers that must never reach a public repo).
#
# The denylist is NOT in this repo. The hook reads it from the file named by
# the SECURING_AI_DENYLIST environment variable, which should point outside the
# working tree (for example ~/.config/securing-ai/denylist.txt), so the terms
# never appear in the repo, its history or CI logs. One term per line; blank
# lines and lines starting with # are ignored. Matching is case-insensitive
# fixed-string (never a regex), so a term like "a.b" matches only "a.b".
#
# It fails closed: with the variable unset, or the file missing, unreadable or
# empty of terms, the push is refused. To push without the check (for example
# on a machine that has no denylist), set SECURING_AI_DENYLIST_SKIP=1 for that
# one command; the hook prints that it was skipped.
#
# Optional: SECURING_AI_DENYLIST_WORDS=1 matches whole words only (grep -w),
# which cuts false positives from short terms.
#
# Install (from the repo root):
#   cp scripts/hooks/pre-push-employer-denylist.sh .git/hooks/pre-push
#   chmod +x .git/hooks/pre-push
#   export SECURING_AI_DENYLIST="$HOME/.config/securing-ai/denylist.txt"
#
# Modes:
#   As a git pre-push hook: reads "<local ref> <local sha> <remote ref> <remote sha>"
#     lines on stdin and scans, for each pushed range, the commit messages and
#     every added line of the diff (including file paths).
#   --scan-paths FILE...: scans the named files directly, with no git involved.
#     Useful to test a denylist, or to check a draft before committing it.
#
# Exit 0 when nothing matches, 1 when something matches, 2 on a setup error.

set -euo pipefail

ZERO_SHA_RE='^0+$'

die_setup() {
  echo "pre-push denylist: $1" >&2
  echo "pre-push denylist: push refused (set SECURING_AI_DENYLIST_SKIP=1 to bypass this once)." >&2
  exit 2
}

if [[ "${SECURING_AI_DENYLIST_SKIP:-0}" == "1" ]]; then
  echo "pre-push denylist: SKIPPED by SECURING_AI_DENYLIST_SKIP=1; nothing was checked." >&2
  exit 0
fi

denylist="${SECURING_AI_DENYLIST:-}"
[[ -n "$denylist" ]] || die_setup "SECURING_AI_DENYLIST is not set."
[[ -f "$denylist" && -r "$denylist" ]] || die_setup "denylist file '$denylist' is missing or unreadable."

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT
terms="$tmpdir/terms"
# Strip comments, surrounding whitespace and blank lines.
sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e '/^#/d' -e '/^$/d' "$denylist" > "$terms"
[[ -s "$terms" ]] || die_setup "denylist file '$denylist' holds no terms."

grep_opts=(-i -F -o -f "$terms")
if [[ "${SECURING_AI_DENYLIST_WORDS:-0}" == "1" ]]; then
  grep_opts=(-w "${grep_opts[@]}")
fi

found=0

# report LABEL FILE: print each distinct matched term with its label.
report() {
  local label="$1" file="$2" hits
  hits="$(grep "${grep_opts[@]}" -- "$file" 2>/dev/null | tr '[:upper:]' '[:lower:]' | sort -u || true)"
  if [[ -n "$hits" ]]; then
    found=1
    while IFS= read -r term; do
      echo "pre-push denylist: match in $label: '$term'" >&2
    done <<< "$hits"
  fi
}

if [[ "${1:-}" == "--scan-paths" ]]; then
  shift
  [[ $# -gt 0 ]] || die_setup "--scan-paths needs at least one file."
  for path in "$@"; do
    [[ -r "$path" ]] || die_setup "cannot read '$path'."
    report "$path" "$path"
  done
else
  while read -r local_ref local_sha remote_ref remote_sha; do
    [[ -n "${local_sha:-}" ]] || continue
    # A branch deletion pushes no content.
    if [[ "$local_sha" =~ $ZERO_SHA_RE ]]; then
      continue
    fi
    if [[ "$remote_sha" =~ $ZERO_SHA_RE ]]; then
      # New branch: everything reachable from it that no remote-tracking ref has.
      range=("$local_sha" --not --remotes)
    else
      range=("$remote_sha..$local_sha")
    fi
    msgs="$tmpdir/msgs"
    added="$tmpdir/added"
    git log --format='%B' "${range[@]}" > "$msgs"
    git log -p --no-color --format='' "${range[@]}" | grep '^+' > "$added" || true
    report "commit messages for $remote_ref" "$msgs"
    report "added lines for $remote_ref" "$added"
  done
fi

if [[ "$found" -ne 0 ]]; then
  echo "pre-push denylist: push refused. Remove the matched terms (rewrite the commits if they are in history), then push again." >&2
  exit 1
fi
exit 0
