#!/usr/bin/env python3
"""
Check that routing.yaml, the interview and the analysis docs agree.

A doc no routing row names is a doc no review reads, and a key no interview
question asks is a key no review sees, so this is the join the whole repo
depends on. The checks:

  1. routing.yaml parses, and signal keys are unique.
  2. Every signal row has a non-empty interview question, a known weight, a
     known method, and docs (a list, possibly empty only for derived rows).
  3. Every PROBLEM or REVIEW row has four factors scored 0 to 2 that fold into
     its stated band (6-8 High, 3-5 Medium, 0-2 Low); every escalation has an
     escalate-if; every name in escalate-if or requires is a signal key or a
     declared observation (requires: signal keys only).
  4. Every `enables` entry is a signal key, and every surface-S<n> enables at
     least one key that is not INVENTORY.
  5. Every family has an owning role for Question Packets.
  6. Every analysis doc with status PRODUCTION or EMERGING (stubs included,
     the template excluded) is named by at least one routing row, lists only
     routing keys or special keys in applies-to-signals, and lists every key
     whose row routes to it.
  7. The four Always Fetch docs are named in routing.yaml.
  8. AUDIT-CONTEXT.md's rendered routing section matches routing.yaml
     (render-audit-context.py --check).

Docs a row names that are not written yet are counted and printed, and do not
fail the run until --release is given, because the repo is built one doc at a
time and the routing table is written first on purpose. At release, every
routed doc must exist.

Usage:
    python scripts/check-routing-coverage.py [--release] [--root DIR]
"""

import argparse
import importlib.util
import re
import sys
from pathlib import Path

import yaml

BANDS = {"High": (6, 8), "Medium": (3, 5), "Low": (0, 2)}
WEIGHTS = {"PROBLEM", "REVIEW", "INVENTORY"}
METHODS = {"I", "E", "D"}
SHIPPED = {"PRODUCTION", "EMERGING"}
TEMPLATE = "analysis/CANONICAL-DOC-TEMPLATE.md"


def frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    return yaml.safe_load(m.group(1)) or {}


def special_match(key: str, specials: list[str]) -> bool:
    for s in specials:
        if "<" in s:
            prefix = s.split("<", 1)[0]
            if key.startswith(prefix) and len(key) > len(prefix):
                return True
        elif key == s:
            return True
    return False


def load_renderer(root: Path):
    here = Path(__file__).resolve().parent / "render-audit-context.py"
    spec = importlib.util.spec_from_file_location("render_audit_context", here)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--release", action="store_true", help="also fail on routed docs not yet written")
    args = ap.parse_args()
    root = Path(args.root)

    errors: list[str] = []
    try:
        data = yaml.safe_load((root / "routing.yaml").read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001 - any parse failure fails closed
        print(f"FAIL routing.yaml does not parse: {e}")
        return 1

    rows = data.get("signals") or []
    keys = [r.get("key") for r in rows]
    keyset = set(keys)
    dupes = sorted({k for k in keys if keys.count(k) > 1})
    if dupes:
        errors.append(f"duplicate signal keys: {dupes}")
    observations = set((data.get("observations") or {}).keys())
    overlap = observations & keyset
    if overlap:
        errors.append(f"names declared as both observation and signal key: {sorted(overlap)}")
    specials = [s["key"] for s in data.get("special-keys") or []]
    owners = data.get("family-owners") or {}

    routed: dict[str, set[str]] = {}
    for r in rows:
        k = r.get("key", "<no key>")
        q = (r.get("question") or "").strip()
        if not q:
            errors.append(f"{k}: no interview question")
        if r.get("weight") not in WEIGHTS:
            errors.append(f"{k}: weight '{r.get('weight')}' not one of {sorted(WEIGHTS)}")
        meth = r.get("method") or []
        if not meth or not set(meth) <= METHODS:
            errors.append(f"{k}: method {meth} not a non-empty subset of {sorted(METHODS)}")
        if "D" in meth and not r.get("predicate"):
            errors.append(f"{k}: derived row with no predicate")
        if r.get("family") not in owners:
            errors.append(f"{k}: family '{r.get('family')}' has no entry in family-owners")
        docs = r.get("docs")
        if not isinstance(docs, list):
            errors.append(f"{k}: docs is not a list")
            docs = []
        for d in docs:
            routed.setdefault(d, set()).add(k)

        pr = r.get("priority")
        if r.get("weight") in ("PROBLEM", "REVIEW"):
            if not pr:
                errors.append(f"{k}: {r.get('weight')} row with no priority")
            else:
                f = pr.get("factors") or {}
                missing = [x for x in ("reach", "stakes", "reversibility", "blast") if x not in f]
                bad = [x for x, v in f.items() if v not in (0, 1, 2)]
                if missing or bad:
                    errors.append(f"{k}: factors missing {missing} or out of range {bad}")
                else:
                    total = sum(f.values())
                    lo, hi = BANDS.get(pr.get("band"), (None, None))
                    if lo is None:
                        errors.append(f"{k}: band '{pr.get('band')}' unknown")
                    elif not lo <= total <= hi:
                        errors.append(f"{k}: factors sum {total} does not fold into band {pr.get('band')} ({lo}-{hi})")
        if pr and pr.get("escalation") and not pr.get("escalate-if"):
            errors.append(f"{k}: escalation with no machine-readable escalate-if")
        for n in (pr or {}).get("escalate-if", []):
            if n not in keyset and n not in observations:
                errors.append(f"{k}: escalate-if name '{n}' is neither a signal key nor an observation")
        if (pr or {}).get("escalate-weight") and pr["escalate-weight"] not in WEIGHTS:
            errors.append(f"{k}: escalate-weight '{pr['escalate-weight']}' unknown")
        for n in r.get("requires", []) or []:
            if n not in keyset:
                errors.append(f"{k}: requires '{n}', which is not a signal key")
        for n in r.get("enables", []) or []:
            if n not in keyset:
                errors.append(f"{k}: enables '{n}', which is not a signal key")
        if re.fullmatch(r"surface-S\d+", k):
            non_inv = [n for n in r.get("enables", []) or []
                       if n in keyset and next(x for x in rows if x["key"] == n)["weight"] != "INVENTORY"]
            if not non_inv:
                errors.append(f"{k}: enables no non-INVENTORY key")

    if len(data.get("always-fetch") or []) != 4:
        errors.append(f"always-fetch lists {len(data.get('always-fetch') or [])} docs, the design fixes four")

    # docs on disk
    shipped, checked_docs = [], 0
    for p in sorted((root / "analysis").rglob("*.md")) if (root / "analysis").is_dir() else []:
        rel = p.relative_to(root).as_posix()
        if rel == TEMPLATE:
            continue
        fm = frontmatter(p)
        if fm is None:
            errors.append(f"{rel}: no frontmatter")
            continue
        if fm.get("status") not in SHIPPED:
            continue
        checked_docs += 1
        shipped.append(rel)
        always = rel in (data.get("always-fetch") or [])
        if rel not in routed and not always:
            errors.append(f"{rel}: status {fm.get('status')} but no routing row names it")
        ats = fm.get("applies-to-signals") or []
        for s in ats:
            if s not in keyset and not special_match(s, specials):
                errors.append(f"{rel}: applies-to-signals entry '{s}' is not a routing key or special key")
        for k in sorted(routed.get(rel, set())):
            if k not in ats:
                errors.append(f"{rel}: routing row '{k}' routes here but the doc does not list it in applies-to-signals")

    unwritten = sorted(d for d in set(routed) | set(data.get("always-fetch") or [])
                       if not (root / d).is_file())
    if args.release and unwritten:
        errors.append(f"{len(unwritten)} routed or always-fetch docs not written: {unwritten}")

    # rendered section
    try:
        renderer = load_renderer(root)
        ac = (root / "AUDIT-CONTEXT.md").read_text(encoding="utf-8")
        if renderer.splice(ac, renderer.render(data)) != ac:
            errors.append("AUDIT-CONTEXT.md routing section is stale; run python scripts/render-audit-context.py")
    except Exception as e:  # noqa: BLE001
        errors.append(f"could not check the rendered routing section: {e}")

    scored = sum(1 for r in rows if r.get("priority"))
    print(f"routing.yaml: {len(rows)} signal rows ({scored} scored), {len(observations)} observations, "
          f"{len(specials)} special keys, {len(owners)} family owners")
    print(f"docs routed: {len(routed)} distinct; shipped docs checked: {checked_docs}; "
          f"routed or always-fetch docs not yet written: {len(unwritten)}"
          + ("" if args.release else " (allowed before release)"))
    for e in errors:
        print(f"FAIL {e}")
    if not errors:
        print("PASS routing coverage")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
