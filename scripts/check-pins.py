#!/usr/bin/env python3
"""
Count analysis docs pinned to a superseded release of a framework, schema or
catalogue.

The current pins are the `pins:` list in the frontmatter of
analysis/revalidation-and-pins.md, which every review fetches; each entry is a
name followed by its version as the last word ("MITRE ATLAS v2026.10",
"OCSF 1.9.0"). Every other doc's `pins:` entry with the same name and a
different version is behind, and is counted. That count goes into the weekly
self-test line and never fails the run, because a doc one ATLAS release behind
is a revalidation task, not a broken build, and an advisory check that blocks
merges is the retired source-monitoring pattern.

Doc pins are matched to the canon after three normalizations, so a doc pin
written in a longer form is still compared rather than skipped: a trailing
parenthetical is dropped ("MITRE ATLAS v2026.10 (released 2026-10-28)"), a
trailing "@" before the version is dropped ("... risk-map @ 622605a1"), and a
doc name that extends a canon name by words with no digit in them matches it
("CISA KEV catalogVersion" matches "CISA KEV catalog", "CoSAI
secure-ai-tooling risk-map" matches "CoSAI secure-ai-tooling"). A commit SHA
matches its own abbreviation. A doc pin that still matches no canon name is a
doc-local pin (a lab tool version, a statute as read on a date), which is
legitimate; those are counted and listed on every run, so a typo in a canon
name shows up there instead of being skipped silently.

The run fails in exactly one case: when the pins doc itself is behind. Given
--current FILE (a YAML mapping of name to the newest known version, written by
the scheduled source-accessibility probe or by hand in the weekly review), a
pins-doc entry older than the newest known version fails, and so does a
pins-doc entry with no version, because the pins doc is the one every review
prints and it must not be stale.

Usage:
    python scripts/check-pins.py [--current pins-current.yaml] [--root DIR]
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

PINS_DOC = "analysis/revalidation-and-pins.md"
TEMPLATE = "analysis/CANONICAL-DOC-TEMPLATE.md"


def frontmatter(path: Path) -> dict:
    m = re.match(r"^---\n(.*?)\n---\n", path.read_text(encoding="utf-8"), re.S)
    return (yaml.safe_load(m.group(1)) or {}) if m else {}


def split_pin(pin: str) -> tuple[str, str | None]:
    """'MITRE ATLAS v2026.10' -> ('MITRE ATLAS', 'v2026.10'); a pin with no
    digit in its last word has no version."""
    parts = str(pin).strip().split()
    if len(parts) >= 2 and re.search(r"\d", parts[-1]):
        return " ".join(parts[:-1]), parts[-1]
    return str(pin).strip(), None


def _n(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def doc_pin(pin: str, canon: dict) -> tuple[str | None, str | None]:
    """(canon name or None, version or None) for a pin in some other doc."""
    s = str(pin).strip()
    while re.search(r"\s*\([^()]*\)\s*$", s):
        s = re.sub(r"\s*\([^()]*\)\s*$", "", s)
    name, ver = split_pin(s)
    parts = s.split()
    if ver is None and len(parts) >= 2 and re.fullmatch(r"[0-9a-f]{7,40}", parts[-1]):
        name, ver = " ".join(parts[:-1]), parts[-1]  # a commit SHA that happens to hold no digit
    name = re.sub(r"\s*@$", "", name).strip()
    if name in canon:
        return name, ver
    best = None
    for c in canon:
        rest = _n(name)[len(_n(c)):] if _n(name).startswith(_n(c)) else None
        if rest is not None and rest and not re.search(r"\d", rest) and (best is None or len(c) > len(best)):
            best = c
    return best, ver


def same_version(a: str, b: str) -> bool:
    """Equal, or one hex commit SHA (7 or more characters) abbreviating the other."""
    if a == b:
        return True
    hexsha = re.compile(r"^[0-9a-f]{7,40}$")
    return bool(hexsha.match(a) and hexsha.match(b)) and (a.startswith(b) or b.startswith(a))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--current", help="YAML mapping of pin name to newest known version")
    args = ap.parse_args()
    root = Path(args.root)
    pins_doc = root / PINS_DOC

    if not pins_doc.is_file():
        print(f"pins doc not written yet ({PINS_DOC}); 0 docs checked, 0 behind")
        return 0

    canon: dict[str, str | None] = {}
    errors = []
    for pin in frontmatter(pins_doc).get("pins") or []:
        name, ver = split_pin(pin)
        if ver is None:
            errors.append(f"{PINS_DOC}: pin '{pin}' has no version")
        if name in canon:
            errors.append(f"{PINS_DOC}: '{name}' pinned twice")
        canon[name] = ver

    if args.current:
        newest = yaml.safe_load(Path(args.current).read_text(encoding="utf-8")) or {}
        for name, ver in sorted(newest.items()):
            if name in canon and canon[name] is not None and str(ver) != canon[name]:
                errors.append(f"{PINS_DOC}: '{name}' pinned at {canon[name]} but {ver} is the newest known")

    behind, local, checked = [], [], 0
    for p in sorted((root / "analysis").rglob("*.md")):
        rel = p.relative_to(root).as_posix()
        if rel in (PINS_DOC, TEMPLATE):
            continue
        checked += 1
        for pin in frontmatter(p).get("pins") or []:
            name, ver = doc_pin(pin, canon)
            if name is None:
                local.append(f"{rel}: {pin}")
            elif ver is not None and canon[name] is not None and not same_version(ver, canon[name]):
                behind.append(f"{rel}: '{name}' at {ver}, pins doc has {canon[name]}")

    print(f"pins doc: {len(canon)} pins; docs checked: {checked}; docs pins behind: {len(behind)}; "
          f"doc-local pins (no canon name): {len(local)}")
    for b in behind:
        print(f"  behind {b}")
    for loc in local:
        print(f"  doc-local {loc}")
    for e in errors:
        print(f"FAIL {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
