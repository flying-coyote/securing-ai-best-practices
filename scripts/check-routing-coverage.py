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
  7. The Always Fetch docs are named in routing.yaml, and their count is the
     one AUDIT-CONTEXT.md's "Always fetch these N" sentence states, with each
     doc named there.
  8. AUDIT-CONTEXT.md's rendered routing section and Priority rubric ordering
     rule match routing.yaml (render-audit-context.py --check).
  9. A doc whose status is not one the canonical template lists fails, rather
     than being skipped as unshipped.
 10. Every escalation input has a source: an interview observation carries a
     question, and every other source it names is a reducer shipped in
     scripts/reducers/. A row collected by E is a key some shipped reducer
     prints, or escalates on a count one prints.
 11. The small-org branch's families are surfaces and its asks are routing
     keys.
 12. Every row with docs carries `evidence`: a `tier` that starts with a grade
     A to D (a compound label as the Summary writes it), found after "Tier "
     in the Summary of one of the row's written docs, and a `convergence`
     equal to that doc's frontmatter value (Decision 7). A row may say
     `tier-source: doc` only where its tier is the doc's frontmatter tier.
 13. Every shipped doc says `maintenance: maintained` or `maintenance: frozen`
     (anything else fails, so a typo cannot drop a doc out of the checks). A
     maintained doc has a `revalidate-by` date no more than eight months after
     its `last-verified`, three where it pins ATLAS; a frozen doc has none and
     opens its Summary with "Frozen reference: not revalidated since
     <last-verified>.". The Always Fetch docs and every doc a small-org
     fixture's golden routes to must be maintained, and no more than three
     maintained docs may fall due in any 30-day window.

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
from datetime import date, timedelta
from pathlib import Path

import yaml

BANDS = {"High": (6, 8), "Medium": (3, 5), "Low": (0, 2)}
WEIGHTS = {"PROBLEM", "REVIEW", "INVENTORY"}
METHODS = {"I", "E", "D"}
SHIPPED = {"PRODUCTION", "EMERGING"}
TEMPLATE = "analysis/CANONICAL-DOC-TEMPLATE.md"
REDUCERS = Path(__file__).resolve().parent / "reducers"
MAINTENANCE = {"maintained", "frozen"}
CONVERGENCE = {"converged", "emerging", "single-source"}
TIER_RE = re.compile(r"^[A-D](?:$|[ ,;/])")
WINDOW_DAYS, WINDOW_MAX = 30, 3
NUMBERS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8}


def known_statuses(root: Path) -> set[str]:
    """The status values the canonical template lists (its `status: A | B | ...` line)."""
    t = root / TEMPLATE
    m = re.search(r"^status: ([A-Z]+(?: \| [A-Z]+)+)", t.read_text(encoding="utf-8"), re.M) if t.is_file() else None
    return set(m.group(1).split(" | ")) if m else SHIPPED


def shipped_reducers() -> tuple[set[str], set[str]]:
    """Reducer names (from each emit call) and the signal keys their SIGNALS sets allow."""
    names, sigs = set(), set()
    for f in sorted(REDUCERS.glob("*.py")) if REDUCERS.is_dir() else []:
        src = f.read_text(encoding="utf-8")
        names |= set(re.findall(r'emit\(\s*"([a-z0-9-]+)"', src))
        for body in re.findall(r"^SIGNALS = \{(.*?)\}", src, re.M | re.S):
            sigs |= set(re.findall(r'"([a-z0-9<>-]+)"', body))
    return names, sigs


def frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    return yaml.safe_load(m.group(1)) or {}


def summary_texts(path: Path, fm: dict) -> tuple[str, str]:
    """The doc's routable Summary, whitespace-collapsed, as written and with parentheticals removed,
    so a label like "Tier A (RFC 9700); Tier D for X" matches "A; Tier D for X"."""
    text = path.read_text(encoding="utf-8")
    head = re.escape(str(fm.get("summary-section") or "Summary for the review"))
    m = re.search(rf"^## {head}[^\n]*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    raw = " ".join((m.group(1) if m else "").split())
    stripped = raw
    while True:
        nxt = re.sub(r"\s*\([^()]*\)", "", stripped)
        if nxt == stripped:
            break
        stripped = nxt
    return raw, " ".join(stripped.split())


def add_months(d: date, n: int) -> date:
    y, m = divmod(d.month - 1 + n, 12)
    y, m = d.year + y, m + 1
    for day in (d.day, 30, 29, 28):
        try:
            return date(y, m, day)
        except ValueError:
            continue
    raise ValueError(d)


def as_date(v) -> date | None:
    if isinstance(v, date):
        return v
    try:
        return date.fromisoformat(str(v))
    except ValueError:
        return None


def small_org_docs(root: Path) -> set[str]:
    """Docs any small-org fixture's golden routes to: with the Always Fetch docs, the maintained core."""
    out: set[str] = set()
    for p in sorted((root / "fixtures").glob("*/expected.yaml")) if (root / "fixtures").is_dir() else []:
        g = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        if g.get("interview-branch") == "small-org":
            out |= set(g.get("docs") or [])
    return out


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

    af = data.get("always-fetch") or []
    try:
        ac_text = (root / "AUDIT-CONTEXT.md").read_text(encoding="utf-8")
    except OSError:
        ac_text = ""
    m = re.search(r"^Always fetch these (\w+)[^:]*:(.*)$", ac_text, re.M)
    if not m:
        errors.append("AUDIT-CONTEXT.md has no 'Always fetch these N' sentence to hold always-fetch to")
    else:
        stated = NUMBERS.get(m.group(1).lower(), int(m.group(1)) if m.group(1).isdigit() else None)
        if stated != len(af):
            errors.append(f"always-fetch lists {len(af)} docs but AUDIT-CONTEXT.md says 'Always fetch these {m.group(1)}'")
        for d in af:
            if f"`{d}`" not in m.group(2):
                errors.append(f"always-fetch doc {d} is not named in AUDIT-CONTEXT.md's Always fetch sentence")

    # escalation inputs and method E have something behind them
    red_names, red_signals = shipped_reducers()
    obs_meta = data.get("observations") or {}
    for name, meta in obs_meta.items():
        for src in [x.strip() for x in str((meta or {}).get("from", "")).split(",") if x.strip()]:
            if src == "interview":
                if not (meta or {}).get("question"):
                    errors.append(f"observation '{name}' is from the interview but has no question")
            elif src not in red_names:
                errors.append(f"observation '{name}' names source '{src}', which is no reducer in scripts/reducers/")
    for r in rows:
        if "E" not in (r.get("method") or []):
            continue
        esc = (r.get("priority") or {}).get("escalate-if") or []
        from_reducer = any(n in obs_meta and "interview" not in str(obs_meta[n].get("from", "")) for n in esc)
        if r.get("key") not in red_signals and not from_reducer:
            errors.append(f"{r.get('key')}: collected by E, but no shipped reducer prints it or a count it escalates on")

    # the small-org branch names real surfaces and keys
    so = (data.get("interview-branches") or {}).get("small-org") or {}
    for f in so.get("families") or []:
        if f"surface-{f}" not in keyset:
            errors.append(f"interview-branches.small-org.families names '{f}', which is not a surface")
    for k in so.get("asks") or []:
        if k not in keyset:
            errors.append(f"interview-branches.small-org.asks names '{k}', which is not a routing key")
    for k in (data.get("interview-branches") or {}).get("first-questions") or []:
        if k not in keyset:
            errors.append(f"interview-branches.first-questions names '{k}', which is not a routing key")

    # docs on disk
    shipped, checked_docs = [], 0
    statuses = known_statuses(root)
    for p in sorted((root / "analysis").rglob("*.md")) if (root / "analysis").is_dir() else []:
        rel = p.relative_to(root).as_posix()
        if rel == TEMPLATE:
            continue
        fm = frontmatter(p)
        if fm is None:
            errors.append(f"{rel}: no frontmatter")
            continue
        if fm.get("status") not in statuses:
            errors.append(f"{rel}: status '{fm.get('status')}' is not one the canonical template lists {sorted(statuses)}")
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

    # per-row confidence, held to the Summary of the doc the row cites
    fm_cache: dict[str, dict | None] = {}

    def doc_fm(d: str) -> dict | None:
        if d not in fm_cache:
            p = root / d
            fm_cache[d] = frontmatter(p) if p.is_file() else None
        return fm_cache[d]

    fallback = 0
    for r in rows:
        k, docs = r.get("key", "<no key>"), [d for d in (r.get("docs") or []) if isinstance(d, str)]
        if not docs:
            continue
        ev = r.get("evidence")
        if not isinstance(ev, dict) or not ev.get("tier") or not ev.get("convergence"):
            errors.append(f"{k}: routes to docs but has no evidence tier and convergence")
            continue
        tier, conv, src = str(ev["tier"]), ev["convergence"], ev.get("tier-source")
        if conv not in CONVERGENCE:
            errors.append(f"{k}: convergence '{conv}' not one of {sorted(CONVERGENCE)}")
        written = [(d, doc_fm(d)) for d in docs if doc_fm(d) is not None]
        if written and conv not in {f.get("convergence") for _, f in written}:
            errors.append(f"{k}: convergence '{conv}' is not the frontmatter convergence of any doc it routes to (Decision 7)")
        if src is not None:
            if src != "doc":
                errors.append(f"{k}: tier-source '{src}' unknown (only 'doc')")
            elif written and tier not in {str(f.get("evidence-tier")) for _, f in written}:
                errors.append(f"{k}: tier-source doc, but '{tier}' is not the frontmatter evidence-tier of a doc it routes to")
            fallback += 1
            continue
        if not TIER_RE.match(tier):
            errors.append(f"{k}: evidence tier '{tier}' does not start with a grade A to D")
            continue
        if written and not any(f"Tier {tier}" in t for d, f in written for t in summary_texts(root / d, f)):
            errors.append(f"{k}: evidence tier 'Tier {tier}' is not stated in the Summary of {', '.join(d for d, _ in written)}")

    # maintained core and frozen reference
    core = set(data.get("always-fetch") or []) | small_org_docs(root)
    due: list[tuple[date, str]] = []
    for rel in shipped:
        fm = doc_fm(rel) or {}
        mt = fm.get("maintenance")
        if mt not in MAINTENANCE:
            errors.append(f"{rel}: maintenance '{mt}' is not one of {sorted(MAINTENANCE)}")
            continue
        lv = as_date(fm.get("last-verified"))
        if lv is None:
            errors.append(f"{rel}: last-verified '{fm.get('last-verified')}' is not a date")
            continue
        if mt == "frozen":
            if rel in core:
                errors.append(f"{rel}: frozen, but it is in the maintained core (Always Fetch or routed by a small-org fixture)")
            if "revalidate-by" in fm:
                errors.append(f"{rel}: frozen docs carry no revalidate-by")
            raw, _ = summary_texts(root / rel, fm)
            want = f"Frozen reference: not revalidated since {lv.isoformat()}."
            if not raw.startswith(want):
                errors.append(f"{rel}: frozen, but its Summary does not open with '{want}'")
            continue
        rb = as_date(fm.get("revalidate-by"))
        if rb is None:
            errors.append(f"{rel}: maintained, but revalidate-by '{fm.get('revalidate-by')}' is not a date")
            continue
        atlas = any("ATLAS" in str(x) for x in fm.get("pins") or [])
        limit = add_months(lv, 3 if atlas else 8)
        if rb > limit:
            errors.append(f"{rel}: revalidate-by {rb} is past {limit}, {'three' if atlas else 'eight'} months after last-verified"
                          + (" (it pins ATLAS)" if atlas else ""))
        due.append((rb, rel))
    due.sort()
    for i in range(len(due) - WINDOW_MAX):
        if (due[i + WINDOW_MAX][0] - due[i][0]).days < WINDOW_DAYS:
            names = ", ".join(f"{r} {d}" for d, r in due[i:i + WINDOW_MAX + 1])
            errors.append(f"more than {WINDOW_MAX} maintained docs fall due within {WINDOW_DAYS} days: {names}")
            break

    unwritten = sorted(d for d in set(routed) | set(data.get("always-fetch") or [])
                       if not (root / d).is_file())
    if args.release and unwritten:
        errors.append(f"{len(unwritten)} routed or always-fetch docs not written: {unwritten}")

    # rendered section
    try:
        renderer = load_renderer(root)
        ac = (root / "AUDIT-CONTEXT.md").read_text(encoding="utf-8")
        if renderer.apply(ac, data) != ac:
            errors.append("AUDIT-CONTEXT.md routing section or ordering rule is stale; run python scripts/render-audit-context.py")
    except Exception as e:  # noqa: BLE001
        errors.append(f"could not check the rendered routing section: {e}")

    scored = sum(1 for r in rows if r.get("priority"))
    print(f"routing.yaml: {len(rows)} signal rows ({scored} scored), {len(observations)} observations, "
          f"{len(specials)} special keys, {len(owners)} family owners")
    print(f"evidence: {sum(1 for r in rows if r.get('evidence'))} rows carry a tier and convergence, "
          f"{fallback} from a doc's frontmatter; maintenance: {len(due)} maintained docs, "
          f"{sum(1 for d in shipped if (doc_fm(d) or {}).get('maintenance') == 'frozen')} frozen")
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
