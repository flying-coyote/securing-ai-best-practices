#!/usr/bin/env python3
"""
The reference mapper: an Answers Block in, the review's doc list, ranked
actions and Question Packets out, computed only from routing.yaml.

An agent running the one-line review does this matching itself. This script
exists so that anyone can check the agent's routing against the table, and so
that CI can hold the table to three golden fixtures: if a change to
routing.yaml moves a fixture's doc list or top actions, the change shows up as
a failing diff that has to be accepted on purpose.

Usage:
    python scripts/route.py ANSWERS.yaml [REDUCER-OUTPUT.yaml ...]
    python scripts/route.py --check-fixtures          # every fixtures/*/ golden
    python scripts/route.py --root DIR ...

Rules, all read from routing.yaml (AUDIT-CONTEXT.md states them for agents):

  - A value of true or an integer above zero selects a key; false or 0 is an
    answer of "no"; `unsure` or a missing answer is "not checked".
  - Derived rows (method D with a predicate) are evaluated in three-valued
    logic, so a predicate over an unanswered surface is unknown, never false.
    Where a row is both asked and derived and the two disagree, the derived
    value is used and the disagreement is reported under `conflicts`.
  - A row that some other row `enables` is eligible only when at least one of
    its enablers is selected, and a row with `requires` only when every
    required key is selected. Ineligible rows are not asked.
  - A surface answered false is recorded as not run; its rows are suppressed
    and it goes into one batched how-do-you-know line.
  - Rows that share an interview question (identical text, or "Same question
    as <key>") are one question: answering one answers the others as no.
  - An escalation applies only when every name in its escalate-if is observed
    (a key selected, or an observation above zero or true). The band becomes
    High and the weight becomes escalate-weight if given.
  - A believed observation caps the band at Medium, and every believed,
    unsure or missing answer to an eligible PROBLEM or REVIEW row becomes a
    Question Packet entry for the row's owning role.
  - INVENTORY rows fetch nothing. Docs are the four Always Fetch docs, then the
    docs of selected actions, then of selected review rows, deduplicated in
    that order.
  - Ordering within a band: until analysis/decision-sequence.md exists and
    carries a machine-readable sequence, the mapper orders by factor sum
    (descending) and then by row order in routing.yaml. This is a
    deterministic stand-in, recorded in the output as `ordering`.

Exit 0 on success (and, with --check-fixtures, when every golden matches);
1 on a mismatch or an invalid Answers Block.
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

BAND_RANK = {"High": 0, "Medium": 1, "Low": 2}
CONFIDENCES = {"read", "owner-stated", "believed"}
ORDERING = "band, then factor sum descending, then routing.yaml row order (stand-in until decision-sequence.md carries a sequence)"


class AnswersError(ValueError):
    pass


# ---------- three-valued predicate evaluation (and / or / not / parentheses) ----------

def tokenize(expr: str) -> list[str]:
    return re.findall(r"\(|\)|[A-Za-z0-9][A-Za-z0-9<>_-]*", expr)


def eval_predicate(expr: str, truth) -> bool | None:
    toks = tokenize(expr)
    pos = 0

    def peek():
        return toks[pos] if pos < len(toks) else None

    def take():
        nonlocal pos
        pos += 1
        return toks[pos - 1]

    def atom():
        t = take()
        if t == "(":
            v = disj()
            if take() != ")":
                raise AnswersError(f"unbalanced predicate: {expr}")
            return v
        if t == "not":
            v = atom()
            return None if v is None else (not v)
        return truth(t)

    def conj():
        v = atom()
        while peek() == "and":
            take()
            w = atom()
            v = False if (v is False or w is False) else (None if (v is None or w is None) else True)
        return v

    def disj():
        v = conj()
        while peek() == "or":
            take()
            w = conj()
            v = True if (v is True or w is True) else (None if (v is None or w is None) else False)
        return v

    out = disj()
    if pos != len(toks):
        raise AnswersError(f"trailing tokens in predicate: {expr}")
    return out


# ---------- loading ----------

def norm_entry(name: str, raw) -> dict:
    if isinstance(raw, dict):
        val, conf = raw.get("value"), raw.get("confidence", "owner-stated")
    else:
        val, conf = raw, "owner-stated"
    if conf not in CONFIDENCES:
        raise AnswersError(f"{name}: confidence '{conf}' not one of {sorted(CONFIDENCES)}")
    if val == "not-checked":
        val = "unsure"
    if not (isinstance(val, bool) or (isinstance(val, int) and val >= 0) or val == "unsure"):
        raise AnswersError(f"{name}: value {val!r} must be true, false, an integer of 0 or more, or unsure")
    return {"value": val, "confidence": conf}


def selected(entry: dict | None) -> bool | None:
    """True if the answer selects the key, False if it is a no, None if not checked."""
    if entry is None or entry["value"] == "unsure":
        return None
    v = entry["value"]
    return bool(v) if isinstance(v, bool) else v > 0


def merge(answers: dict, reducer_docs: list[dict]) -> tuple[dict, dict]:
    signals = {k: norm_entry(k, v) for k, v in (answers.get("signals") or {}).items()}
    obs = {k: norm_entry(k, v) for k, v in (answers.get("observations") or {}).items()}
    for doc in reducer_docs:
        for k, v in (doc.get("observations") or {}).items():
            e = norm_entry(k, {"value": v, "confidence": "read"})
            if k in obs and obs[k]["value"] != "unsure":
                a, b = obs[k]["value"], e["value"]
                e["value"] = (a or b) if isinstance(a, bool) or isinstance(b, bool) else a + b
            obs[k] = e
        for k, v in (doc.get("signals") or {}).items():
            e = norm_entry(k, v)
            if e["value"] == "unsure":
                continue  # a reducer that could not see the setting adds nothing
            prev = signals.get(k)
            if prev and prev["confidence"] == "read" and prev["value"] != "unsure":
                a, b = prev["value"], e["value"]
                e["value"] = (a or b) if isinstance(a, bool) or isinstance(b, bool) else a + b
            signals[k] = e
    return signals, obs


# ---------- routing ----------

def route(data: dict, answers: dict, reducer_docs: list[dict]) -> dict:
    rows = data["signals"]
    by_key = {r["key"]: r for r in rows}
    order = {r["key"]: i for i, r in enumerate(rows)}
    observations_decl = set((data.get("observations") or {}).keys())
    specials = [s["key"] for s in data.get("special-keys") or []]
    owners = data.get("family-owners") or {}

    signals, obs = merge(answers, reducer_docs)

    # resolve pattern instances (audit-log-off-coding-agent -> audit-log-off-<platform>)
    patterns = {r["pattern"].split("<", 1)[0]: r for r in rows if r.get("pattern")}
    instances: dict[str, list[str]] = {}
    for k in list(signals):
        if k in by_key:
            continue
        for prefix, r in patterns.items():
            if k.startswith(prefix):
                val = k[len(prefix):]
                if val not in r.get("values", []):
                    raise AnswersError(f"{k}: '{val}' is not in the platform list of {r['key']}")
                instances.setdefault(r["key"], []).append(k)
                break
        else:
            raise AnswersError(f"{k}: not a routing key")
    for k in obs:
        if k not in observations_decl:
            raise AnswersError(f"observation '{k}' is not declared in routing.yaml")
    overrides = list(answers.get("overrides") or [])
    for o in overrides:
        if not o.startswith("profile-override-") or o == "profile-override-":
            raise AnswersError(f"override '{o}' must be profile-override-<reason>")

    # question groups
    group_of: dict[str, str] = {}
    by_question: dict[str, str] = {}
    for r in rows:
        # the parenthetical "(<value> selects this key.)" names the answer, not the question
        q = re.sub(r"\s*\([^()]*selects this key[^()]*\)\s*$", "", (r.get("question") or "").strip())
        m = re.match(r"Same question as ([A-Za-z0-9<>_-]+)", q)
        if m and m.group(1) in by_key:
            group_of[r["key"]] = group_of.get(m.group(1), m.group(1))
        elif q in by_question and not q.startswith("Derived"):
            group_of[r["key"]] = by_question[q]
        else:
            by_question.setdefault(q, r["key"])
            group_of[r["key"]] = r["key"]
    groups: dict[str, list[str]] = {}
    for k, g in group_of.items():
        groups.setdefault(g, []).append(k)

    def entry(k):
        return signals.get(k)

    def answered_in_group(k) -> bool:
        return any(selected(entry(m)) is not None for m in groups[group_of[k]])

    # derived rows, in routing.yaml order (predicates only reference earlier or asked keys)
    truth_cache: dict[str, bool | None] = {}
    conflicts = []
    derived_selected = []

    def truth(k: str) -> bool | None:
        if k in truth_cache:
            return truth_cache[k]
        if k in observations_decl:
            return selected(obs.get(k))
        r = by_key.get(k)
        if r is None:
            raise AnswersError(f"predicate names unknown key '{k}'")
        if r.get("pattern"):
            vals = [selected(entry(i)) for i in instances.get(k, [])]
            v = True if True in vals else (False if vals and all(x is False for x in vals) else None)
        elif r.get("predicate"):
            v = eval_predicate(r["predicate"], truth)
            asked = selected(entry(k))
            if v is None:
                v = asked if asked is not None else (False if answered_in_group(k) else None)
            elif asked is not None and asked != v:
                conflicts.append(f"{k}: answered {str(asked).lower()} but derived {str(v).lower()} from '{r['predicate']}'")
        else:
            v = selected(entry(k))
            if v is None and k in group_of and answered_in_group(k):
                v = False
        truth_cache[k] = v
        return v

    for r in rows:
        if r.get("predicate") and truth(r["key"]) and "D" in r.get("method", []):
            if selected(entry(r["key"])) is not True:
                derived_selected.append(r["key"])

    branch = "small-org" if (truth("org-size-small-mid") and truth("profile-rent-heavy")) else "full"
    stated_branch = answers.get("interview-branch")
    if stated_branch and stated_branch != branch:
        conflicts.append(f"interview-branch: answers say {stated_branch} but the first two answers select {branch}")

    surfaces = [r["key"] for r in rows if re.fullmatch(r"surface-S\d+", r["key"])]
    present = [s.split("-", 1)[1] for s in surfaces if truth(s) is True]
    not_run = [s.split("-", 1)[1] for s in surfaces if truth(s) is False]
    unknown_surfaces = [s.split("-", 1)[1] for s in surfaces if truth(s) is None]

    enablers: dict[str, list[str]] = {}
    for r in rows:
        for n in r.get("enables", []) or []:
            enablers.setdefault(n, []).append(r["key"])

    def eligible(k: str) -> bool:
        if k in enablers and not any(truth(e) is True for e in enablers[k]):
            return False
        return all(truth(q) is True for q in by_key[k].get("requires", []) or [])

    def observed(n: str) -> bool:
        return truth(n) is True

    actions, review, packets, clean = [], [], {}, []
    packeted: set[str] = set()

    def add_packet(r, key, why):
        role = r.get("owner") or owners.get(r.get("family"), "security lead")
        packets.setdefault(role, []).append({"key": key, "why": why})

    for r in rows:
        k = r["key"]
        if r["weight"] == "INVENTORY" or not eligible(k):
            continue
        keys_here = instances.get(k, []) if r.get("pattern") else [k]
        if r.get("pattern") and not keys_here:
            add_packet(r, k, "not checked")
            continue
        for kk in keys_here:
            e = entry(kk)
            if r.get("predicate"):
                sel = truth(k)
            else:
                sel = selected(e)
                if sel is None and answered_in_group(k):
                    sel = False
            conf = e["confidence"] if e else ("derived" if r.get("predicate") else None)
            if sel is None:
                # one packet per interview question, addressed by the group's first key
                head = group_of.get(kk, kk)
                if head not in packeted and (not r.get("predicate") or "I" in r.get("method", [])):
                    packeted.add(head)
                    add_packet(by_key.get(head, r), head, "not checked")
                continue
            if conf == "believed":
                add_packet(r, kk, "believed only")
            if not sel:
                # only an explicit "no" counts as working well, never one implied by a sibling answer
                if e is not None and conf not in ("believed", "derived") and selected(e) is False:
                    clean.append(kk)
                continue
            pr = r.get("priority") or {}
            f = pr.get("factors", {})
            band, weight, escalated, capped = pr.get("band"), r["weight"], False, False
            cond = pr.get("escalate-if") or []
            if cond and all(observed(n) for n in cond):
                band, escalated = "High", True
                weight = pr.get("escalate-weight", weight)
            if conf == "believed" and band == "High":
                band, capped = "Medium", True
            item = {"key": kk, "weight": weight, "band": band, "factor-sum": sum(f.values()),
                    "confidence": conf, "docs": list(r.get("docs", []))}
            if escalated:
                item["escalated"] = True
            if capped:
                item["capped-by-belief"] = True
            (actions if weight == "PROBLEM" else review).append((order[k], item))

    for s_ in unknown_surfaces:
        r = by_key[f"surface-{s_}"]
        add_packet(r, r["key"], "not checked")

    def sort_items(items):
        return [it for _, it in sorted(items, key=lambda t: (BAND_RANK[t[1]["band"]], -t[1]["factor-sum"], t[0], t[1]["key"]))]

    actions_s, review_s = sort_items(actions), sort_items(review)
    docs = []
    for d in list(data.get("always-fetch") or []) + [d for it in actions_s + review_s for d in it["docs"]]:
        if d not in docs:
            docs.append(d)
    n_top = (data.get("interview-branches") or {}).get("top-actions", {}).get(branch, 5)

    out = {
        "interview-branch": branch,
        "overrides": overrides,
        "surfaces-present": present,
        "not-run": not_run,
        "surfaces-not-checked": unknown_surfaces,
        "derived": derived_selected,
        "top-actions": [it["key"] for it in actions_s[:n_top]],
        "actions": actions_s,
        "review": review_s,
        "docs": docs,
        "question-packets": {role: packets[role] for role in sorted(packets)},
        "clean": clean,
        "conflicts": conflicts,
        "ordering": ORDERING,
    }
    if not reducer_docs and not any(
            e.get("confidence") == "read" for e in list(signals.values()) + list(obs.values())):
        out["questionnaire-only"] = True
    return out


def run(root: Path, answers_path: Path, reducer_paths: list[Path]) -> dict:
    data = yaml.safe_load((root / "routing.yaml").read_text(encoding="utf-8"))
    answers = yaml.safe_load(answers_path.read_text(encoding="utf-8")) or {}
    if answers.get("answers-block") != 1:
        raise AnswersError("not an Answers Block (missing 'answers-block: 1')")
    paths = [root / p for p in answers.get("reducer-outputs") or []] + list(reducer_paths)
    reducer_docs = []
    for p in paths:
        doc = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        if "reducer" not in doc:
            raise AnswersError(f"{p}: not reducer output (no 'reducer' field)")
        reducer_docs.append(doc)
    return route(data, answers, reducer_docs)


class _NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def dump(obj) -> str:
    return yaml.dump(obj, Dumper=_NoAliasDumper, sort_keys=False, default_flow_style=False, width=1000, allow_unicode=True)


def check_fixtures(root: Path) -> int:
    fixtures = sorted(p for p in (root / "fixtures").glob("*/answers.yaml"))
    if not fixtures:
        print("FAIL no fixtures found under fixtures/*/answers.yaml")
        return 1
    bad = 0
    for a in fixtures:
        exp_p = a.parent / "expected.yaml"
        try:
            got = run(root, a, [])
        except AnswersError as e:
            print(f"FAIL {a.parent.name}: {e}")
            bad += 1
            continue
        if not exp_p.is_file():
            print(f"FAIL {a.parent.name}: no expected.yaml")
            bad += 1
            continue
        want = yaml.safe_load(exp_p.read_text(encoding="utf-8"))
        if got == want:
            print(f"PASS {a.parent.name}: {got['interview-branch']} branch, {len(got['docs'])} docs, "
                  f"top actions {got['top-actions']}")
        else:
            bad += 1
            print(f"FAIL {a.parent.name}: output differs from expected.yaml")
            for k in sorted(set(got) | set(want)):
                if got.get(k) != want.get(k):
                    print(f"  {k}:\n    expected: {want.get(k)}\n    got:      {got.get(k)}")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("answers", nargs="?", type=Path)
    ap.add_argument("reducer_outputs", nargs="*", type=Path)
    ap.add_argument("--root", default=".", type=Path)
    ap.add_argument("--check-fixtures", action="store_true")
    args = ap.parse_args()
    if args.check_fixtures:
        return check_fixtures(args.root)
    if not args.answers:
        ap.error("give an Answers Block, or --check-fixtures")
    try:
        print(dump(run(args.root, args.answers, args.reducer_outputs)), end="")
    except AnswersError as e:
        print(f"ERROR invalid Answers Block: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
