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

    # per-form checks, so a false positive and a false negative cannot cancel in an aggregate golden
    import importlib.util
    import json

    def load(name):
        spec = importlib.util.spec_from_file_location(name, RED / f"{name}.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    mc = load("mcp_config")
    secret_cases = [
        ({"env": {"API_TOKEN": "env:API_TOKEN"}}, 0, "env:VAR reference"),
        ({"env": {"VAULT_KEY": "op://vault/item/field"}}, 0, "op:// reference"),
        ({"headers": {"Authorization": "Bearer ${TOKEN}"}}, 0, "Bearer ${TOKEN} reference"),
        ({"env": {"GITHUB_TOKEN": "${env:GITHUB_TOKEN}"}}, 0, "${env:VAR} reference"),
        ({"env": {"MAX_TOKENS": "4096"}}, 0, "MAX_TOKENS number"),
        ({"env": {"AUTH_MODE": "oauth"}}, 0, "AUTH_MODE word"),
        ({"env": {"TOKEN_URL": "https://login.example.invalid/token"}}, 0, "TOKEN_URL"),
        ({"args": ["--max-tokens", "4096"]}, 0, "--max-tokens 4096"),
        ({"args": ["--api-key=env:KEY"]}, 0, "--api-key=env:KEY"),
        ({"env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "EXAMPLE-NOT-A-REAL-TOKEN"}}, 1, "inline token"),
        ({"headers": {"Authorization": "Bearer EXAMPLEopaque0123"}}, 1, "inline bearer"),
        ({"headers": {"X-Api-Key": "EXAMPLE-KEY-value"}}, 1, "inline X-Api-Key"),
        ({"env": ["ACCESS_TOKEN=EXAMPLE-LIST-SECRET", "LOG_LEVEL=debug"]}, 1, "list-typed env"),
        ({"env": "not-a-mapping", "args": "not-a-list"}, 0, "malformed env and args"),
        ({"args": ["--api-key", "EXAMPLE-ARG-SECRET"]}, 1, "--api-key value"),
    ]
    for server, want_n, label in secret_cases:
        try:
            got_n = mc.count_secrets(server)
        except Exception as e:  # a crash is a failure, not a skip
            got_n = f"{type(e).__name__}"
        check(got_n == want_n, f"mcp-config: {label}: counted {got_n}, want {want_n}")
    launch_cases = [
        ("cmd", ["/c", "npx", "-y", "@example/a@1.0.0"], ("runner", "@example/a@1.0.0")),
        ("sh", ["-c", "npx @example/b"], ("runner", "@example/b")),
        ("npm", ["exec", "@example/c@2.0.0"], ("runner", "@example/c@2.0.0")),
        ("npm", ["x", "--", "@example/c"], ("runner", "@example/c")),
        ("uvx", ["--python", "3.12", "pkg==1.2.3"], ("runner", "pkg==1.2.3")),
        ("uvx", ["-p", "3.12", "pkg@1.2.3"], ("runner", "pkg@1.2.3")),
        ("npx", ["--registry", "https://registry.example.invalid", "pkg@1.0.0"], ("runner", "pkg@1.0.0")),
        ("npx", ["-p", "pkg@1.0.0", "pkg-bin"], ("runner", "pkg@1.0.0")),
        ("env", ["NODE_ENV=production", "npx", "pkg@1.0.0"], ("runner", "pkg@1.0.0")),
        ("npx -y pkg@1.0.0", [], ("runner", "pkg@1.0.0")),
        ("bash", ["-c", "cd /srv && uvx pkg"], ("unknown", None)),
        ("cmd", ["/q"], ("unknown", None)),
        ("sh", ["-c", "exec npx @example/d"], ("runner", "@example/d")),
        ("sh", ["-c", "FOO=1 npx @example/e@1.0.0"], ("runner", "@example/e@1.0.0")),
        ("bash", ["-lc", "npx @example/f"], ("runner", "@example/f")),
        ("uv", ["tool", "run", "--with", "extra", "pkg==2.0.0"], ("runner", "pkg==2.0.0")),
        ("uvx", ["-w", "extra", "pkg"], ("runner", "pkg")),
        ("bun", ["x", "pkg@1.0.0"], ("runner", "pkg@1.0.0")),
        ("pipx", ["run", "--spec", "pkg==1.0.0", "pkg-cmd"], ("runner", "pkg==1.0.0")),
        ("node", ["/opt/server.js"], ("neither", None)),
        ("npm", ["run", "start"], ("neither", None)),
    ]
    for cmd, args, want in launch_cases:
        got = mc.launch(cmd, args)
        check(got == want, f"mcp-config: launch {cmd} {args}: got {got}, want {want}")
    with tempfile.TemporaryDirectory() as td:
        cfg = Path(td) / "unknown-only.json"
        cfg.write_text(json.dumps({"mcpServers": {"x": {"command": "bash", "args": ["-c", "a && npx b"]}}}), encoding="utf-8")
        p = subprocess.run([sys.executable, "-I", str(RED / "mcp_config.py"), str(cfg)], capture_output=True, text=True)
        doc = yaml.safe_load(p.stdout) if p.returncode == 0 else {}
        check(((doc.get("signals") or {}).get("mcp-unpinned") or {}).get("value") == "not-checked",
              f"mcp-config: an unread launch with no unpinned server printed {p.stdout[-200:]}{p.stderr[-200:]}")
    print("ok   mcp-config per-form secrets, references and launchers")

    # coding-agent-settings branches the fixture does not reach
    cases = [
        ({"permissions": {"deny": ["Bash(rm:*)"]}}, "user", {"hook-fail-open": "not-checked", "hooks-user-disableable": "not-checked"},
         "no hooks configured"),
        ({"hooks": {"PreToolUse": [{"matcher": "*", "hooks": [{"type": "command", "command": "x"}]}]},
          "permissions": {"deny": ["Bash(rm:*)"]}}, "project",
         {"hook-fail-open": True, "hooks-user-disableable": "not-checked"}, "hooks outside managed beside a deny rule"),
        ({"hooks": {"PreToolUse": [{"matcher": "*", "hooks": [{"type": "command", "command": "x", "onFailure": "block"}]}]}},
         "managed", {"hook-fail-open": False, "hooks-user-disableable": False}, "only managed hooks, all fail closed"),
    ]
    for data, scope, want, label in cases:
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "settings.json"
            f.write_text(json.dumps(data), encoding="utf-8")
            p = subprocess.run([sys.executable, "-I", str(RED / "coding_agent_settings.py"), f"{scope}:{f}"],
                               capture_output=True, text=True)
            sig = (yaml.safe_load(p.stdout) or {}).get("signals") or {} if p.returncode == 0 else {}
            for k, v in want.items():
                check((sig.get(k) or {}).get("value") == v, f"coding-agent-settings: {label}: {k} is {sig.get(k)}, want {v}")
    print("ok   coding-agent-settings prints not-checked where the files cannot show the answer")

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
