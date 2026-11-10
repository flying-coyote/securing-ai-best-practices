#!/usr/bin/env python3
"""
Render the routing section of AUDIT-CONTEXT.md from routing.yaml.

routing.yaml is the routing table as data and AUDIT-CONTEXT.md is what the
agent reads, so the section between the `routing:start` and `routing:end`
markers is generated from the data and never edited by hand. The rendered
section carries, per signal, how it is collected, its weight and priority
(with the escalation and the condition that triggers it), any row it requires,
and the docs it routes to. The interview question and the why for each row stay
in routing.yaml, which the review fetches beside this file, so the rendered
section stays small enough to sit in an agent's context.

Usage:
    python scripts/render-audit-context.py            # rewrite the section in place
    python scripts/render-audit-context.py --check    # exit 1 if the file is stale
    python scripts/render-audit-context.py --root DIR

The output is deterministic: rows render in routing.yaml order, grouped by
family in order of first appearance.
"""

import argparse
import sys
from pathlib import Path

import yaml

START = "<!-- routing:start (rendered from routing.yaml by scripts/render-audit-context.py; do not edit by hand) -->"
END = "<!-- routing:end -->"
START_PREFIX = "<!-- routing:start"


def cell(text: str) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def priority_cell(row: dict) -> str:
    weight = row.get("weight", "")
    pr = row.get("priority")
    if not pr:
        return weight
    f = pr.get("factors", {})
    total = sum(f.get(k, 0) for k in ("reach", "stakes", "reversibility", "blast"))
    out = f"{weight}, {pr.get('band')} ({f.get('reach')}+{f.get('stakes')}+{f.get('reversibility')}+{f.get('blast')}={total})"
    if pr.get("escalation"):
        cond = " and ".join(f"`{n}`" for n in pr.get("escalate-if", []))
        out += f"; escalates: {pr['escalation']}"
        if cond:
            out += f" [when {cond}]"
        if pr.get("escalate-weight"):
            out += f" [weight becomes {pr['escalate-weight']}]"
    return out


def render(data: dict) -> str:
    lines = [START, ""]
    lines.append(
        "Rendered from `routing.yaml`. Each row's interview question and its why are in that file. "
        "Weight: PROBLEM produces an action, REVIEW is listed with the answer quoted, INVENTORY enables "
        "other rows and fetches nothing on its own. Priority shows the band and the four factor scores "
        "(reach + stakes + reversibility + blast). Collected: I interview, E export or reducer output, "
        "D derived by the stated predicate."
    )
    families: dict[str, list] = {}
    for row in data.get("signals", []):
        families.setdefault(row.get("family", "other"), []).append(row)
    for fam, rows in families.items():
        owner = data.get("family-owners", {}).get(fam)
        lines += ["", f"### {fam}", ""]
        if owner:
            lines += [f"Question Packets for this family go to: {owner}.", ""]
        lines += ["| Key | Collected | Weight, priority | Conditions | Routes to |",
                  "|---|---|---|---|---|"]
        for r in rows:
            cond = []
            if r.get("predicate"):
                cond.append(f"derived: {r['predicate']}")
            if r.get("requires"):
                cond.append("requires " + ", ".join(f"`{k}`" for k in r["requires"]))
            if r.get("enables"):
                cond.append("enables " + ", ".join(f"`{k}`" for k in r["enables"]))
            if r.get("values"):
                cond.append("platform values: " + ", ".join(r["values"]))
            if r.get("owner"):
                cond.append(f"packets to {r['owner']}")
            docs = ", ".join(f"`{d}`" for d in r.get("docs", []))
            lines.append(
                f"| `{cell(r['key'])}` | {'/'.join(r.get('method', []))} | {cell(priority_cell(r))} "
                f"| {cell('; '.join(cond))} | {docs} |"
            )
    special = data.get("special-keys", [])
    if special:
        lines += ["", "### Special keys (fetch nothing)", "", "| Key | Effect |", "|---|---|"]
        for s in special:
            lines.append(f"| `{cell(s['key'])}` | {cell(s['effect'])} |")
    lines += ["", END]
    return "\n".join(lines)


def splice(doc: str, rendered: str) -> str:
    i = doc.find(START_PREFIX)
    j = doc.find(END)
    if i < 0 or j < 0 or j < i:
        raise ValueError("AUDIT-CONTEXT.md has no routing:start / routing:end markers")
    return doc[:i] + rendered + doc[j + len(END):]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--check", action="store_true", help="exit 1 if AUDIT-CONTEXT.md is stale")
    args = ap.parse_args()
    root = Path(args.root)
    data = yaml.safe_load((root / "routing.yaml").read_text(encoding="utf-8"))
    ac = root / "AUDIT-CONTEXT.md"
    doc = ac.read_text(encoding="utf-8")
    try:
        new = splice(doc, render(data))
    except ValueError as e:
        print(f"ERROR: {e}")
        return 2
    if args.check:
        if new != doc:
            print("FAIL AUDIT-CONTEXT.md routing section is stale; run python scripts/render-audit-context.py")
            return 1
        print(f"PASS AUDIT-CONTEXT.md routing section matches routing.yaml ({len(data['signals'])} rows)")
        return 0
    if new != doc:
        ac.write_text(new, encoding="utf-8")
        print(f"rendered {len(data['signals'])} rows into AUDIT-CONTEXT.md")
    else:
        print("AUDIT-CONTEXT.md already current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
