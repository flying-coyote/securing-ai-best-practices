#!/usr/bin/env python3
"""
Check the greppable subset of the exclusions in CONTRIBUTING.md.

Most of the repo's exclusions are judgements a reviewer makes (no product
reviews, no exploit steps, no vendor comparison dressed as a category grade).
The ones below are mechanical, so they are checked mechanically:

  tmp-source       a temporary filesystem path in a `source:` field, which no
                   reader can follow
  local-path       a home-directory or private working-tree path anywhere in a
                   published file
  licensed-crosswalk  the folder name of a licence-restricted framework
                   crosswalk, which the repo never draws on
  owasp-2025-id    an OWASP LLM Top 10 ID in its 2025 form (LLM01 followed by a colon and 2025,
                   and so on), since the docs are pinned to the 2026 edition
  not-legal-advice the not-legal-advice sentence missing from either prompt
                   block, from the Structured Output Format, or from the law
                   document once it exists

The employer and identifier denylist is deliberately not here. It runs as a
local pre-push hook that reads a file outside the repo, because a check backed
by a secret list would print its matches into public CI logs.

Forbidden strings are assembled from pieces below so that this file and its
test do not match themselves.

Usage:
    python scripts/check-exclusions.py [--root DIR]

Exit 0 when nothing is found, 1 when anything is.
"""

import argparse
import re
import sys
from pathlib import Path

SCAN_SUFFIXES = {".md", ".yaml", ".yml", ".py", ".sh", ".json", ".csv", ".txt"}
SKIP_DIRS = {".git", "__pycache__", "node_modules", "dist"}

TMP = "/" + "tmp" + "/"
LOCAL_PATHS = [
    "/" + "home" + "/",
    "/" + "Users" + "/",
    "~" + "/project1",
    "02" + "-projects/",
    "01" + "-knowledge-base/",
]
CROSSWALK = "scf" + "-mapping/ai-frameworks"
OWASP_2025 = re.compile(r"\bLLM\d{2}" + ":" + r"2025\b")
SOURCE_LINE = re.compile(r"^\s*-?\s*source\s*:", re.I)

NOT_LEGAL = re.compile(r"not legal advice", re.I)
LAW_DOC = "analysis/prompt-capture-and-the-law.md"


def iter_files(root: Path):
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.suffix not in SCAN_SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in p.relative_to(root).parts):
            continue
        yield p


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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    root = Path(args.root)
    hits: list[tuple[str, str, int, str]] = []
    scanned = 0

    for p in iter_files(root):
        rel = p.relative_to(root).as_posix()
        try:
            lines = p.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        scanned += 1
        for i, line in enumerate(lines, 1):
            if TMP in line and SOURCE_LINE.match(line):
                hits.append(("tmp-source", rel, i, line.strip()))
            for lp in LOCAL_PATHS:
                if lp in line:
                    hits.append(("local-path", rel, i, line.strip()))
                    break
            if CROSSWALK in line:
                hits.append(("licensed-crosswalk", rel, i, line.strip()))
            if OWASP_2025.search(line):
                hits.append(("owasp-2025-id", rel, i, line.strip()))

    # the not-legal-advice sentence
    required = []
    olp = root / "ONE-LINE-PROMPT.md"
    readme = root / "README.md"
    if olp.is_file():
        t = olp.read_text(encoding="utf-8")
        required += [("ONE-LINE-PROMPT.md, Fetch mode block", section(t, "Fetch mode")),
                     ("ONE-LINE-PROMPT.md, Offline mode block", section(t, "Offline mode")),
                     ("ONE-LINE-PROMPT.md, Structured Output Format", section(t, "Structured Output Format"))]
    else:
        hits.append(("not-legal-advice", "ONE-LINE-PROMPT.md", 0, "file missing"))
    if readme.is_file():
        required.append(("README.md, one-line review block", section(readme.read_text(encoding="utf-8"), "The one-line review")))
    law = root / LAW_DOC
    if law.is_file():
        required.append((LAW_DOC, law.read_text(encoding="utf-8")))
    law_state = "present" if law.is_file() else "not written yet"
    for where, text in required:
        if not NOT_LEGAL.search(text):
            hits.append(("not-legal-advice", where, 0, "sentence missing"))

    print(f"scanned {scanned} files; not-legal-advice checked in {len(required)} places (law doc {law_state})")
    for rule, rel, line, text in hits:
        loc = f"{rel}:{line}" if line else rel
        print(f"FAIL {rule} {loc}: {text[:160]}")
    if not hits:
        print("PASS no greppable exclusion found")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
