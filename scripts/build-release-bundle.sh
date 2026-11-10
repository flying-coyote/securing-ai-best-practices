#!/usr/bin/env bash
# build-release-bundle.sh: the two release steps that touch files.
#
# A commit cannot contain its own SHA, so a release runs in this order
# (RELEASES.md and DECISIONS.md, Decision 2):
#
#   1. stamp:  write the tag and date into AUDIT-CONTEXT.md's release header and
#              routing.yaml's `release:` field, then commit and tag that commit.
#   2. bundle: from the tagged commit, concatenate the release files into one
#              offline bundle, compute its SHA-256, and add the release row to
#              RELEASES.md (tag, date, commit SHA, bundle hash, pins).
#   3. by hand: bump the README and ONE-LINE-PROMPT blocks to the tagged SHA on
#              the default branch; check-prompt-blocks.py then holds them to it.
#
# The bundle holds AUDIT-CONTEXT.md, ONE-LINE-PROMPT.md, routing.yaml, the four
# Always Fetch docs and every routed doc that exists, in that order, each under
# a header line naming its path, with no timestamps, so the same commit always
# produces the same bytes and the same hash.
#
# Usage:
#   scripts/build-release-bundle.sh stamp  vYYYY.MM YYYY-MM-DD
#   scripts/build-release-bundle.sh bundle vYYYY.MM <40-hex commit sha>
#
# Environment:
#   ROOT=DIR          repo root (default: the parent of this script's folder)
#   ALLOW_MISSING=1   build even if an Always Fetch doc is missing (tests only;
#                     a real release must never set it)
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
ac = root / "AUDIT-CONTEXT.md"
text = ac.read_text(encoding="utf-8")
new, n = re.subn(r"(<!-- release-header:[^\n]*-->\n)Release: [^\n]*\n",
                 rf"\g<1>Release: {tag}. Date: {date}.\n", text, count=1)
if n != 1:
    sys.exit("ERROR: AUDIT-CONTEXT.md has no release-header comment followed by a Release: line")
ac.write_text(new, encoding="utf-8")
ry = root / "routing.yaml"
rtext = ry.read_text(encoding="utf-8")
rnew, n = re.subn(r"(?m)^release: .*$", f"release: {tag}", rtext, count=1)
if n != 1:
    sys.exit("ERROR: routing.yaml has no top-level release: line")
ry.write_text(rnew, encoding="utf-8")
print(f"stamped {tag} ({date}) into AUDIT-CONTEXT.md and routing.yaml")
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
if missing and not allow_missing:
    sys.exit(f"ERROR: Always Fetch docs missing: {missing}")
files = ["AUDIT-CONTEXT.md", "ONE-LINE-PROMPT.md", "routing.yaml"]
files += [d for d in always if (root / d).is_file()]
files += [d for d in routed if (root / d).is_file()]

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
if missing:
    print(f"WARNING: built with ALLOW_MISSING=1; missing Always Fetch docs: {missing}")
PY
    ;;
  *)
    die "usage: $0 stamp vYYYY.MM YYYY-MM-DD | bundle vYYYY.MM <commit-sha>"
    ;;
esac
