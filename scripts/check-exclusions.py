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
  undecodable      a file that is not valid UTF-8, which fails rather than
                   being skipped, since a skipped file is an unscanned one
  hidden-char      an invisible or control character (Unicode tags, zero-width
                   and bidi controls, other format and control characters, as
                   reducers/text_sanitize.py defines them, and the U+2028 and
                   U+2029 separators) in tracked text, since
                   the review hands these files to an agent; the reducer
                   fixtures carry them on purpose and are exempt
  secret-shaped    a string shaped like a live credential (provider key
                   prefixes, a private-key header); the line is never printed,
                   and the reducer fixtures and their test are exempt

Every file git tracks under the root is scanned (every file on disk when the
root is not a git checkout, as in the test copies), except known binary types
and the skipped folders, so a new extension is not silently left out and an
untracked local file does not fail the run.

With --messages FILE (or - for standard input) it scans commit-message text
instead of the tree, for the local-path, crosswalk, hidden-char and
secret-shaped rules. The script never runs git; CI writes the pull request's
or push's commit messages to a file and passes it.

The employer and identifier denylist is deliberately not here. It runs as a
local pre-push hook that reads a file outside the repo, because a check backed
by a secret list would print its matches into public CI logs.

Forbidden strings are assembled from pieces below so that this file and its
test do not match themselves.

Usage:
    python scripts/check-exclusions.py [--root DIR]
    python scripts/check-exclusions.py --messages FILE|-

Exit 0 when nothing is found, 1 when anything is.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

BINARY_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".gz", ".tgz", ".tar",
                   ".woff", ".woff2", ".ttf", ".otf", ".pyc"}
SKIP_DIRS = {".git", "__pycache__", "node_modules", "dist", ".venv", "venv"}
# Fixtures that carry hidden characters and secret-shaped strings on purpose, to
# test that the reducers strip and never print them.
HIDDEN_EXEMPT = ("scripts/reducers/fixtures/",)
SECRET_EXEMPT = ("scripts/reducers/fixtures/", "scripts/test-reducers.py")
SECRET_SHAPES = re.compile(
    r"(?<![A-Za-z0-9])(sk-(ant-|proj-)[A-Za-z0-9_-]{16,}|sk-[A-Za-z0-9]{32,}|gh[pousr]_[A-Za-z0-9]{30,}"
    r"|github_pat_[A-Za-z0-9_]{30,}|xox[abprs]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16}|glpat-[A-Za-z0-9_-]{20,}"
    r"|AIza[0-9A-Za-z_-]{35}|-----BEGIN [A-Z ]*PRIVATE KEY-----)")

LINE_SEPARATORS = {"\u2028", "\u2029"}

sys.path.insert(0, str(Path(__file__).resolve().parent / "reducers"))
from text_sanitize import scrub  # noqa: E402

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
    try:
        out = subprocess.run(["git", "-C", str(root), "ls-files", "-z"], capture_output=True, check=True).stdout
        tracked = [root / f for f in out.decode("utf-8", "surrogateescape").split("\0") if f]
    except (subprocess.CalledProcessError, FileNotFoundError):
        tracked = []
    for p in sorted(tracked or root.rglob("*")):
        if not p.is_file() or p.suffix.lower() in BINARY_SUFFIXES:
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


def line_hits(rel: str, i: int, line: str, messages: bool = False) -> list[tuple[str, str, int, str]]:
    """The per-line rules. Commit messages get the local-path, crosswalk,
    hidden and secret rules; a temporary path, an OWASP ID or a source: line in
    a message is harmless (a message may well name /tmp/links.txt)."""
    out = []
    if not messages and TMP in line and SOURCE_LINE.match(line):
        out.append(("tmp-source", rel, i, line.strip()))
    for lp in LOCAL_PATHS:
        if lp in line:
            out.append(("local-path", rel, i, line.strip()))
            break
    if CROSSWALK in line:
        out.append(("licensed-crosswalk", rel, i, line.strip()))
    if not messages and OWASP_2025.search(line):
        out.append(("owasp-2025-id", rel, i, line.strip()))
    if not rel.startswith(HIDDEN_EXEMPT):
        cleaned, removed = scrub(line.rstrip("\r"))
        # U+2028 and U+2029 are separators (category Zl and Zp), not format
        # characters, so scrub keeps them, but they break a line invisibly.
        seps = sum(cleaned.count(c) for c in LINE_SEPARATORS)
        cleaned = "".join(c for c in cleaned if c not in LINE_SEPARATORS)
        removed += seps
        if removed:
            kept = set(cleaned)
            names = sorted({f"U+{ord(c):04X}" for c in line.rstrip("\r") if c not in kept})
            out.append(("hidden-char", rel, i, f"{removed} invisible or control character(s): {', '.join(names[:6])}"))
    if not rel.startswith(SECRET_EXEMPT):
        m = SECRET_SHAPES.search(line)
        if m:
            out.append(("secret-shaped", rel, i, f"a string shaped like a credential at column {m.start() + 1} "
                                                 "(not printed)"))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--messages", metavar="FILE", help="scan commit-message text from FILE (- for stdin) instead")
    args = ap.parse_args()
    root = Path(args.root)
    hits: list[tuple[str, str, int, str]] = []
    scanned = 0

    if args.messages:
        raw = sys.stdin.buffer.read() if args.messages == "-" else Path(args.messages).read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            print("FAIL undecodable commit-message text is not valid UTF-8")
            return 1
        for i, line in enumerate(text.split("\n"), 1):
            hits += line_hits("commit messages", i, line, messages=True)
        print(f"scanned {len(text.split(chr(10)))} commit-message lines")
        for rule, rel, line, txt in hits:
            print(f"FAIL {rule} {rel}:{line}: {txt[:160]}")
        if not hits:
            print("PASS no greppable exclusion found in the commit messages")
        return 1 if hits else 0

    for p in iter_files(root):
        rel = p.relative_to(root).as_posix()
        try:
            # split on newline only: str.splitlines also breaks on U+2028, U+0085
            # and the like, which would hide them from the hidden-char rule
            lines = p.read_text(encoding="utf-8").split("\n")
        except UnicodeDecodeError:
            hits.append(("undecodable", rel, 0, "not valid UTF-8, so it was not scanned"))
            continue
        scanned += 1
        for i, line in enumerate(lines, 1):
            hits += line_hits(rel, i, line)

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
