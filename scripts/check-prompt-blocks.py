#!/usr/bin/env python3
"""
Check that the one-line review block in README.md is byte-identical to the
fetch-mode block in ONE-LINE-PROMPT.md, and that the commit SHA the block pins
is the commit the newest release tag points at. Also check that the offline
block names the same commit and release as the fetch block, that the
Structured Output Format's `release:` line is copied at run time rather than
written into the file, that neither status banner says the blocks carry
placeholders while they are pinned, and that no file the review fetches or the
bundle holds names another release's tag or commit SHA (the stale self-naming
that shipped at v2026.12 and v2026.12.1, where the tagged copy pinned the
release before it).

The two blocks are copies of one text, and a practitioner may paste either, so
a drift between them means two different reviews depending on which page they
read. The SHA check exists because the block pins a commit rather than a branch
or a tag (DECISIONS.md, Decision 2): after a release the README must name the
tagged commit, and before the first release it must still carry the
`<release-sha>` placeholder.

This script never runs git. CI resolves the newest tag and passes its commit
with --tag-commit; with no --tag-commit the repo is treated as unreleased and
the placeholder is required. That keeps the check testable on a plain copy of
the tree.

Usage:
    python scripts/check-prompt-blocks.py
    python scripts/check-prompt-blocks.py --tag-commit <40-hex sha> [--tag vYYYY.MM[.N]]
    python scripts/check-prompt-blocks.py --root /path/to/tree

Exit 0 when every check passes, 1 when any fails, 2 when a file is missing or
has no block where one is expected (fails closed).
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

FENCE_RE = re.compile(r"^```text\n(.*?)^```\s*$", re.S | re.M)
SHA_RE = re.compile(r"/securing-ai-best-practices/([^/\s]+)/AUDIT-CONTEXT\.md")
TAG_RE = re.compile(r"\(release ([^;\s]+);")
OFFLINE_RE = re.compile(r"\(release ([^,\s]+), commit ([^;\s]+);")
RELEASE_ROW_RE = re.compile(r"^\| (v\d{4}\.\d{2}(?:\.\d+)?) \| [^|]* \| `([0-9a-f]{40})` \|", re.M)
# files where a release is named by tag; the SHA rule covers every fetched or bundled file
TAG_FILES = ("AUDIT-CONTEXT.md", "ONE-LINE-PROMPT.md", "routing.yaml", "README.md")
PLACEHOLDER_SHA = "<release-sha>"
PLACEHOLDER_TAG = "<vYYYY.MM>"


def section(text: str, heading: str) -> str:
    """Text under a level-2 heading up to the next level-2 heading, ignoring
    headings inside fenced code blocks (the output template carries its own)."""
    lines = text.splitlines(keepends=True)
    out, inside, fence = None, False, False
    for line in lines:
        if line.startswith("```"):
            fence = not fence
        if not fence and line.startswith("## "):
            if inside:
                break
            if line.strip() == f"## {heading}":
                inside, out = True, []
                continue
        if inside:
            out.append(line)
    return "".join(out) if out is not None else ""


def first_block(text: str) -> str | None:
    m = FENCE_RE.search(text)
    return m.group(1) if m else None


def other_release_names(root: Path) -> list[str]:
    """Every place a fetched or bundled file (or the README) names a release other
    than the one AUDIT-CONTEXT's Release line states. The release list is
    RELEASES.md's rows, never a vYYYY.MM pattern, because the docs pin framework
    versions such as 'MITRE ATLAS v2026.10' and lab commits as 40-hex SHAs."""
    rel = root / "RELEASES.md"
    if not rel.is_file():
        return []
    rows = RELEASE_ROW_RE.findall(rel.read_text(encoding="utf-8"))
    ac = root / "AUDIT-CONTEXT.md"
    m = re.search(r"^Release: (\S+?)\. Date:", ac.read_text(encoding="utf-8"), re.M) if ac.is_file() else None
    current = m.group(1) if m else None
    others = [(t, sha) for t, sha in rows if t != current]
    if not others:
        return []
    files = ["AUDIT-CONTEXT.md", "ONE-LINE-PROMPT.md", "routing.yaml", "README.md"]
    rp = root / "routing.yaml"
    if rp.is_file():
        data = yaml.safe_load(rp.read_text(encoding="utf-8")) or {}
        files += list(data.get("always-fetch") or [])
        files += sorted({d for r in data.get("signals") or [] for d in r.get("docs", [])})
    seen, found = set(), []
    for f in files:
        p = root / f
        if f in seen or not p.is_file():
            continue
        seen.add(f)
        text = p.read_text(encoding="utf-8")
        for tag, sha in others:
            if re.search(rf"(?<![0-9a-f]){sha[:7]}", text):
                found.append(f"{f} names {tag}'s commit {sha[:12]}")
            if f in TAG_FILES and re.search(rf"(?<![\w.]){re.escape(tag)}(?![.\d])", text):
                found.append(f"{f} names release {tag}")
    return found


def banner_says_placeholders(path: Path, marker_end: str = "<!-- pre-release:end") -> bool:
    text = path.read_text(encoding="utf-8")
    b = re.search(r"pre-release:start[^\n]*\n(.*?)" + re.escape(marker_end), text, re.S)
    return bool(b and "still carry" in b.group(1))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=".", help="repo root (default: current directory)")
    ap.add_argument("--tag-commit", help="commit SHA the newest release tag points at")
    ap.add_argument("--tag", help="name of the newest release tag (optional, checked if given)")
    args = ap.parse_args()

    root = Path(args.root)
    readme_p, olp_p = root / "README.md", root / "ONE-LINE-PROMPT.md"
    for p in (readme_p, olp_p):
        if not p.is_file():
            print(f"ERROR: {p} not found")
            return 2

    readme_block = first_block(section(readme_p.read_text(encoding="utf-8"), "The one-line review"))
    olp_block = first_block(section(olp_p.read_text(encoding="utf-8"), "Fetch mode"))
    if readme_block is None or olp_block is None:
        print("ERROR: could not find a ```text block under README '## The one-line review' "
              "and ONE-LINE-PROMPT '## Fetch mode'")
        return 2

    failures = []

    if readme_block == olp_block:
        print(f"PASS blocks identical ({len(readme_block.encode('utf-8'))} bytes)")
    else:
        a, b = readme_block.splitlines(), olp_block.splitlines()
        first = next((i for i in range(max(len(a), len(b)))
                      if i >= len(a) or i >= len(b) or a[i] != b[i]), None)
        failures.append(f"README and ONE-LINE-PROMPT blocks differ, first at block line {first + 1}")

    m = SHA_RE.search(readme_block)
    if not m:
        print("ERROR: README block has no pinned AUDIT-CONTEXT URL")
        return 2
    pinned = m.group(1)
    tag_m = TAG_RE.search(readme_block)
    pinned_tag = tag_m.group(1) if tag_m else None

    if args.tag_commit is None:
        if pinned == PLACEHOLDER_SHA:
            print("PASS unreleased: no tag given and the block carries the <release-sha> placeholder")
        else:
            failures.append(f"no release tag given but the block pins '{pinned}'; "
                            "pass --tag-commit or restore the placeholder")
    else:
        want = args.tag_commit.strip().lower()
        if not re.fullmatch(r"[0-9a-f]{40}", want):
            print(f"ERROR: --tag-commit '{args.tag_commit}' is not a full 40-hex SHA")
            return 2
        if pinned == PLACEHOLDER_SHA:
            failures.append("a release tag exists but the block still carries the <release-sha> placeholder")
        elif pinned.lower() != want:
            failures.append(f"block pins {pinned} but the newest tag points at {want}")
        else:
            print(f"PASS block pins the newest tag's commit {want[:12]}")
        if args.tag:
            if pinned_tag != args.tag:
                failures.append(f"block names release '{pinned_tag}' but the newest tag is '{args.tag}'")
            else:
                print(f"PASS block names release {args.tag}")

    # The README prose around the block must agree with the block and with RELEASES.md:
    # a pinned block under a banner saying the placeholders remain, or "Tested agents:
    # none yet" beside a release row, tells a reader two different things.
    readme_text = readme_p.read_text(encoding="utf-8")
    if pinned != PLACEHOLDER_SHA:
        for label, p in (("README status banner", readme_p), ("ONE-LINE-PROMPT release paragraph", olp_p)):
            if banner_says_placeholders(p):
                failures.append(f"{label} says the blocks still carry placeholders, but the block is pinned")

    # The offline block must name the commit and release the fetch block pins.
    olp_text = olp_p.read_text(encoding="utf-8")
    offline_block = first_block(section(olp_text, "Offline mode"))
    om = OFFLINE_RE.search(offline_block or "")
    if not om:
        failures.append("ONE-LINE-PROMPT offline block has no '(release <tag>, commit <sha>;' line")
    elif (om.group(2), om.group(1)) != (pinned, pinned_tag):
        failures.append(f"offline block names release {om.group(1)} commit {om.group(2)}, "
                        f"but the fetch block names release {pinned_tag} commit {pinned}")
    else:
        print("PASS offline block names the fetch block's commit and release")

    # The output template's release line is filled in at run time; a SHA or tag written
    # into the file goes stale at the next release.
    fmt = section(olp_text, "Structured Output Format")
    rl = re.search(r"^release: (.*)$", fmt, re.M)
    if not rl:
        failures.append("Structured Output Format has no 'release:' line")
    elif re.search(r"[0-9a-f]{7,40}|v\d{4}\.\d{2}", rl.group(1)):
        failures.append(f"Structured Output Format release line names a release ('{rl.group(1)}'); "
                        "it must tell the agent where to copy the tag and SHA from")

    others = other_release_names(root)
    if others:
        failures.extend(f"stale release named: {o}" for o in others)
    else:
        print("PASS no fetched or bundled file names another release's tag or commit")
    rel_p = root / "RELEASES.md"
    released = rel_p.is_file() and re.search(r"(?m)^\| v\d{4}\.\d{2}", rel_p.read_text(encoding="utf-8"))
    if released and "Tested agents: none yet" in readme_text:
        failures.append("README says 'Tested agents: none yet' but RELEASES.md records a release")
    elif released:
        print("PASS README prose agrees with the block and RELEASES.md")

    for f in failures:
        print(f"FAIL {f}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
