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

    behind, checked = [], 0
    for p in sorted((root / "analysis").rglob("*.md")):
        rel = p.relative_to(root).as_posix()
        if rel in (PINS_DOC, TEMPLATE):
            continue
        checked += 1
        for pin in frontmatter(p).get("pins") or []:
            name, ver = split_pin(pin)
            if name in canon and ver is not None and canon[name] is not None and ver != canon[name]:
                behind.append(f"{rel}: '{name}' at {ver}, pins doc has {canon[name]}")

    print(f"pins doc: {len(canon)} pins; docs checked: {checked}; docs pins behind: {len(behind)}")
    for b in behind:
        print(f"  behind {b}")
    for e in errors:
        print(f"FAIL {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
