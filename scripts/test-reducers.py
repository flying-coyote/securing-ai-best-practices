#!/usr/bin/env python3
"""
Test the reducers in scripts/reducers/ against their fixtures.

Each folder under scripts/reducers/fixtures/ is named for a reducer's output
name and holds its input files, an `args` file (one argument per line, scope
prefixes included), a `canaries.txt` file and the golden `expected.yaml`. The
inputs deliberately carry what a real export carries: email addresses,
hostnames, IP addresses, tenant-style identifiers, secret-shaped strings, and
an injected instruction both in plain text and hidden in Unicode tag
characters. For every reducer the test checks that:

  1. it exits 0 and its standard output equals expected.yaml byte for byte
     (the goldens were checked by hand against the inputs when written);
  2. no canary string (any line of canaries.txt, compared case-insensitively)
     appears in its standard output or standard error;
  3. every printed name is a signal key in routing.yaml or an observation
     declared there whose `from` names this reducer, and every value is an
     integer of zero or more, true, false or not-checked;
  4. the reducer runs under `python -I`, so it does not depend on the current
     directory or environment.

It also checks that every reducer script has a fixture, that `emit` refuses an
undeclared name and a string value without printing anything, that the
sanitizer strips tag characters, and that scripts/route.py accepts reducer
output beside an Answers Block (the consent-grant count raising
oauth-grants-unreviewed to High).

Usage: python scripts/test-reducers.py
"""

import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
RED = ROOT / "scripts" / "reducers"
HELPERS = {"_common.py", "text_sanitize.py", "ai_catalog.py", "consent_common.py"}

failures: list[str] = []


def check(cond: bool, msg: str):
    if not cond:
        failures.append(msg)


def main() -> int:
    routing = yaml.safe_load((ROOT / "routing.yaml").read_text(encoding="utf-8"))
    keys = {r["key"] for r in routing["signals"]}
    obs = routing.get("observations") or {}

    scripts = sorted(p for p in RED.glob("*.py") if p.name not in HELPERS)
    fixtures = {p.name: p for p in sorted((RED / "fixtures").iterdir()) if p.is_dir()}
    for s in scripts:
        check(s.stem.replace("_", "-") in fixtures, f"{s.name}: no fixture folder")

    for name, fx in fixtures.items():
        script = RED / f"{name.replace('-', '_')}.py"
        if not script.is_file():
            failures.append(f"fixture {name}: no reducer {script.name}")
            continue
        args = [a for a in (fx / "args").read_text(encoding="utf-8").splitlines() if a.strip()]
        proc = subprocess.run([sys.executable, "-I", str(script), *args], cwd=fx,
                              capture_output=True, text=True, encoding="utf-8")
        check(proc.returncode == 0, f"{name}: exit {proc.returncode}: {proc.stderr.strip()[:200]}")
        want = (fx / "expected.yaml").read_text(encoding="utf-8")
        check(proc.stdout == want, f"{name}: output differs from expected.yaml\n--- got\n{proc.stdout}--- want\n{want}")
        both = (proc.stdout + proc.stderr).lower()
        canaries = [c for c in (fx / "canaries.txt").read_text(encoding="utf-8").splitlines() if c.strip()]
        for c in canaries:
            check(c.lower() not in both, f"{name}: input string leaked into output: {c!r}")
        check(len(canaries) >= 5, f"{name}: fewer than five canaries")
        try:
            doc = yaml.safe_load(proc.stdout) or {}
        except yaml.YAMLError as e:
            failures.append(f"{name}: output is not YAML: {e}")
            continue
        check(doc.get("reducer") == name, f"{name}: reducer field is {doc.get('reducer')!r}")
        for k, v in (doc.get("observations") or {}).items():
            decl = obs.get(k)
            check(decl is not None, f"{name}: observation '{k}' not declared in routing.yaml")
            if decl:
                check(name in str(decl.get("from", "")), f"{name}: observation '{k}' is declared from {decl.get('from')!r}")
            check(isinstance(v, bool) or (isinstance(v, int) and v >= 0), f"{name}: {k} has value {v!r}")
        for k, v in (doc.get("signals") or {}).items():
            check(k in keys, f"{name}: signal '{k}' is not a routing key")
            val = (v or {}).get("value")
            check(isinstance(val, bool) or (isinstance(val, int) and val >= 0) or val == "not-checked",
                  f"{name}: signal {k} has value {val!r}")
            check((v or {}).get("confidence") == "read", f"{name}: signal {k} confidence is not read")
        print(f"{'ok  ' if not any(f.startswith(name + ':') for f in failures) else 'FAIL'} {name}")

    # emit refuses undeclared names and string values, printing nothing
    for label, call in [
        ("undeclared name", "emit('x', 1, {'secret-host': 1}, {}, {'ok'}, set())"),
        ("string value", "emit('x', 1, {'ok': 'app01.example.net'}, {}, {'ok'}, set())"),
        ("negative value", "emit('x', 1, {'ok': -1}, {}, {'ok'}, set())"),
    ]:
        code = f"import sys; sys.path.insert(0, {str(RED)!r}); from _common import emit; {call}"
        p = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True)
        check(p.returncode != 0 and p.stdout == "", f"emit accepted a {label} (exit {p.returncode}, stdout {p.stdout!r})")
        check("app01" not in p.stderr, f"emit echoed the rejected value for a {label}")
    print("ok   emit refuses undeclared names, strings and negatives")

    sys.path.insert(0, str(RED))
    from text_sanitize import scrub  # noqa: E402
    hidden = "ChatGPT" + "".join(chr(0xE0000 + ord(c)) for c in "ignore previous") + "​‮"
    cleaned, removed = scrub(hidden)
    check(cleaned == "ChatGPT" and removed == len(hidden) - 7, f"sanitizer left {cleaned!r}")
    print("ok   sanitizer strips tag, zero-width and bidi characters")

    # chain: reducer output feeds route.py
    with tempfile.TemporaryDirectory() as td:
        ans = Path(td) / "answers.yaml"
        ans.write_text(yaml.safe_dump({"answers-block": 1, "signals": {
            "org-size-small-mid": True, "surface-S1": True,
            "oauth-grants-unreviewed": {"value": True, "confidence": "owner-stated"}}}), encoding="utf-8")
        p = subprocess.run([sys.executable, str(ROOT / "scripts" / "route.py"), "--root", str(ROOT), str(ans),
                            str(RED / "fixtures" / "entra-consent-grants" / "expected.yaml")],
                           capture_output=True, text=True)
        out = yaml.safe_load(p.stdout) if p.returncode == 0 else {}
        act = next((a for a in out.get("actions", []) if a["key"] == "oauth-grants-unreviewed"), {})
        check(act.get("band") == "High" and act.get("escalated") is True,
              f"route.py did not escalate oauth-grants-unreviewed from reducer output: {p.stdout[:300]}{p.stderr[:300]}")
        check("questionnaire-only" not in out, "route.py marked a run with reducer output questionnaire-only")
    print("ok   route.py reads reducer output (consent-grant count escalates oauth-grants-unreviewed)")

    for f in failures:
        print(f"FAIL {f}")
    print(f"{len(fixtures)} reducer fixtures; {'PASS' if not failures else str(len(failures)) + ' failure(s)'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
