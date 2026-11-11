#!/usr/bin/env bash
# build-release-bundle.sh: the two release steps that touch files.
#
# A commit cannot contain its own SHA, so a release runs in this order
# (RELEASES.md and DECISIONS.md, Decision 2):
#
#   1. stamp:  write the tag and date into AUDIT-CONTEXT.md's release header and
#              routing.yaml's `release:` field, and retire every pre-release
#              statement so a stamped tree does not argue with itself: remove
#              AUDIT-CONTEXT's pre-release banner, rewrite the pre-release
#              paragraph in ONE-LINE-PROMPT.md, routing.yaml's header comment
#              and README.md's status banner (each between pre-release:start
#              and pre-release:end markers, which stay so the next release's
#              stamp finds them), and rewrite the `Release:` line in
#              analysis/revalidation-and-pins.md. Every one of these seven
#              edits, the release header and `release:` field included,
#              must match exactly once or nothing is
#              written. Then commit and tag that commit.
#   2. bundle: from the tagged commit, concatenate the release files into one
#              offline bundle, compute its SHA-256, and add the release row to
#              RELEASES.md (tag, date, commit SHA, bundle hash, pins).
#   3. by hand: bump the README and ONE-LINE-PROMPT blocks to the tagged SHA on
#              the default branch; check-prompt-blocks.py then holds them to it.
#
# The bundle holds AUDIT-CONTEXT.md, ONE-LINE-PROMPT.md, routing.yaml, the four
# Always Fetch docs and every routed doc, in that order, each under a header
# line naming its path, with no timestamps, so the same commit always produces
# the same bytes and the same hash. It refuses when any Always Fetch or routed
# doc is missing, because a review routed to a doc the bundle does not hold can
# only guess at it, and it refuses when any pre-release text survived the stamp.
#
# Usage:
#   scripts/build-release-bundle.sh stamp  vYYYY.MM YYYY-MM-DD
#   scripts/build-release-bundle.sh bundle vYYYY.MM <40-hex commit sha>
#
# Environment:
#   ROOT=DIR          repo root (default: the parent of this script's folder)
#   ALLOW_MISSING=1   build even if an Always Fetch or routed doc is missing
#                     (tests only; a real release must never set it)
#
# This script never runs git; the operator passes the commit SHA.

set -euo pipefail

ROOT="${ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cmd="${1:-}"
tag="${2:-}"

die() { echo "ERROR: $*" >&2; exit 2; }

[[ "$tag" =~ ^v[0-9]{4}\.[0-9]{2}$ ]] || die "tag must look like vYYYY.MM (got '${tag}')"

case "$cmd" in
  stamp)
    date="${3:-}"
    [[ "$date" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] || die "date must be YYYY-MM-DD (got '${date}')"
    python3 - "$ROOT" "$tag" "$date" <<'PY'
import re, sys
from pathlib import Path
root, tag, date = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
edits, errors = {}, []

def sub(rel, pattern, repl, what, flags=0):
    p = root / rel
    if not p.is_file():
        errors.append(f"{rel} not found ({what})")
        return
    text = edits.get(rel, p.read_text(encoding="utf-8"))
    new, n = re.subn(pattern, repl, text, flags=flags)
    if n != 1:
        errors.append(f"{rel}: expected exactly one {what}, found {n}")
        return
    edits[rel] = new

sub("AUDIT-CONTEXT.md", r"(<!-- release-header:[^\n]*-->\n)Release: [^\n]*\n",
    lambda m: f"{m.group(1)}Release: {tag}. Date: {date}.\n", "release-header comment followed by a Release: line")
# The markers stay, so the next release's stamp finds them again; only the text between them changes.
sub("AUDIT-CONTEXT.md", r"(<!-- pre-release:start[^\n]*-->\n).*?(<!-- pre-release:end -->\n)",
    lambda m: m.group(1) + m.group(2), "pre-release banner between markers", re.S)
sub("ONE-LINE-PROMPT.md", r"(<!-- pre-release:start[^\n]*-->\n).*?(<!-- pre-release:end -->\n)",
    lambda m: m.group(1) + (f"This copy belongs to release {tag}, stamped {date}. The blocks below still carry the "
               "`<release-sha>` and `<vYYYY.MM>` placeholders, because a commit cannot contain its own SHA, "
               "so take the release's full commit SHA, its tag and the SHA-256 of the offline bundle from "
               "`RELEASES.md`; the copy on the default branch carries them filled in.\n") + m.group(2),
    "pre-release paragraph between markers", re.S)
sub("routing.yaml", r"(?m)^release: .*$", lambda m: f"release: {tag}", "top-level release: line")
sub("routing.yaml", r"(# pre-release:start[^\n]*\n).*?(# pre-release:end\n)",
    lambda m: m.group(1) + (f"# State: release {tag}, stamped {date}. The factor scores and the surface-to-signal\n"
               "# \"enables\" lists are the author's judgement (Tier D) and may move between\n"
               "# releases.\n") + m.group(2),
    "pre-release header comment between markers", re.S)
sub("README.md", r"(<!-- pre-release:start[^\n]*-->\n).*?(<!-- pre-release:end -->\n)",
    lambda m: m.group(1) + (f"> Status: release {tag}, stamped {date}. On the tagged commit the blocks below carry the "
               "`<release-sha>` and `<vYYYY.MM>` placeholders, because a commit cannot contain its own SHA, and on the "
               "default branch they carry the tagged commit. Either way, the release's full commit SHA, its tag and the "
               "SHA-256 of the offline bundle are in `RELEASES.md`.\n") + m.group(2),
    "pre-release status banner between markers", re.S)
sub("analysis/revalidation-and-pins.md", r"Release: [^;\n]+; pins last verified",
    lambda m: f"Release: {tag}; pins last verified", "'Release: ...; pins last verified' line")
if errors:
    sys.exit("ERROR: stamp refused, nothing written:\n  " + "\n  ".join(errors))
for rel, text in edits.items():
    (root / rel).write_text(text, encoding="utf-8")
print(f"stamped {tag} ({date}) into {', '.join(sorted(edits))}")
PY
    ;;
  bundle)
    sha="${3:-}"
    [[ "$sha" =~ ^[0-9a-f]{40}$ ]] || die "commit must be a full 40-hex SHA (got '${sha}')"
    python3 - "$ROOT" "$tag" "$sha" "${ALLOW_MISSING:-0}" <<'PY'
import hashlib, re, sys
from pathlib import Path
import yaml
root, tag, sha, allow_missing = Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4] == "1"
routing = yaml.safe_load((root / "routing.yaml").read_text(encoding="utf-8"))
ac_text = (root / "AUDIT-CONTEXT.md").read_text(encoding="utf-8")
m = re.search(r"^Release: (\S+?)\. Date: (\d{4}-\d{2}-\d{2})\.$", ac_text, re.M)
if not m or m.group(1) != tag:
    sys.exit(f"ERROR: AUDIT-CONTEXT.md is not stamped with {tag}; run the stamp step first")
date = m.group(2)
if routing.get("release") != tag:
    sys.exit(f"ERROR: routing.yaml release is {routing.get('release')!r}, not {tag}")

always = list(routing.get("always-fetch") or [])
routed = sorted({d for r in routing["signals"] for d in r.get("docs", [])} - set(always))
missing = [d for d in always if not (root / d).is_file()]
missing_routed = [d for d in routed if not (root / d).is_file()]
errors = []
if missing and not allow_missing:
    errors.append(f"Always Fetch docs missing: {missing}")
if missing_routed and not allow_missing:
    errors.append(f"routed docs missing ({len(missing_routed)}); write them or stop routing to them "
                  f"before the release: {missing_routed}")
files = ["AUDIT-CONTEXT.md", "ONE-LINE-PROMPT.md", "routing.yaml"]
files += [d for d in always if (root / d).is_file()]
files += [d for d in routed if (root / d).is_file()]
# Text between pre-release markers must be empty or name this release; anything else is
# pre-release wording the stamp step did not retire.
marker = re.compile(r"pre-release:start[^\n]*\n(.*?)(?:<!-- |# )pre-release:end", re.S)
leftover = [f for f in files for body in marker.findall((root / f).read_text(encoding="utf-8"))
            if body.strip() and f"release {tag}" not in body]
if (root / "analysis/revalidation-and-pins.md").is_file() and re.search(
        r"Release: unreleased", (root / "analysis/revalidation-and-pins.md").read_text(encoding="utf-8")):
    leftover.append("analysis/revalidation-and-pins.md")
if leftover:
    errors.append(f"pre-release text survives the stamp in: {sorted(set(leftover))}")
if errors:
    sys.exit("ERROR: " + "\nERROR: ".join(errors))

parts = [f"# securing-ai-best-practices offline bundle, release {tag}, commit {sha}\n",
         f"# {len(files)} files follow, each under a line of the form '===== FILE: <path> ====='.\n"]
for f in files:
    body = (root / f).read_text(encoding="utf-8")
    if not body.endswith("\n"):
        body += "\n"
    parts.append(f"\n===== FILE: {f} =====\n")
    parts.append(body)
data = "".join(parts).encode("utf-8")
digest = hashlib.sha256(data).hexdigest()
out = root / "dist" / f"securing-ai-best-practices-{tag}.md"
out.parent.mkdir(exist_ok=True)
out.write_bytes(data)

pins = "see analysis/revalidation-and-pins.md"
pd = root / "analysis/revalidation-and-pins.md"
if pd.is_file():
    fm = re.match(r"^---\n(.*?)\n---\n", pd.read_text(encoding="utf-8"), re.S)
    if fm:
        plist = (yaml.safe_load(fm.group(1)) or {}).get("pins") or []
        if plist:
            pins = "; ".join(str(p) for p in plist)

rel = root / "RELEASES.md"
rtext = rel.read_text(encoding="utf-8")
if re.search(rf"^\| {re.escape(tag)} \|", rtext, re.M):
    sys.exit(f"ERROR: RELEASES.md already has a row for {tag}")
header = "| Tag | Date | Commit SHA | Bundle SHA-256 | Pins | Agents tested | Notes |\n|---|---|---|---|---|---|---|\n"
if header not in rtext:
    sys.exit("ERROR: RELEASES.md release-log table header not found")
row = f"| {tag} | {date} | `{sha}` | `{digest}` | {pins} | to record after the dry runs | {len(files)} files |\n"
rtext = rtext.replace(header, header + row, 1)
rel.write_text(rtext, encoding="utf-8")
print(f"bundle: {out.relative_to(root)} ({len(data)} bytes, {len(files)} files)")
print(f"sha256: {digest}")
if missing or missing_routed:
    print(f"WARNING: built with ALLOW_MISSING=1; missing Always Fetch docs: {missing}; "
          f"missing routed docs: {missing_routed}")
PY
    ;;
  *)
    die "usage: $0 stamp vYYYY.MM YYYY-MM-DD | bundle vYYYY.MM <commit-sha>"
    ;;
esac
