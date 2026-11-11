#!/usr/bin/env python3
"""
Check that the one-line review block in README.md is byte-identical to the
fetch-mode block in ONE-LINE-PROMPT.md, and that the commit SHA the block pins
is the commit the newest release tag points at.

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
    python scripts/check-prompt-blocks.py --tag-commit <40-hex sha> [--tag vYYYY.MM]
    python scripts/check-prompt-blocks.py --root /path/to/tree

Exit 0 when every check passes, 1 when any fails, 2 when a file is missing or
has no block where one is expected (fails closed).
"""

import argparse
import re
import sys
from pathlib import Path

FENCE_RE = re.compile(r"^```text\n(.*?)^```\s*$", re.S | re.M)
SHA_RE = re.compile(r"/securing-ai-best-practices/([^/\s]+)/AUDIT-CONTEXT\.md")
TAG_RE = re.compile(r"\(release ([^;\s]+);")
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
    banner = re.search(r"pre-release:start[^\n]*\n(.*?)<!-- pre-release:end", readme_text, re.S)
    if pinned != PLACEHOLDER_SHA and banner and "still carry" in banner.group(1):
        failures.append("README status banner says the blocks still carry placeholders, but the block is pinned")
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
