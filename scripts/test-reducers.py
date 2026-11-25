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
oauth-grants-unreviewed to High). The robustness pass then feeds every
reducer its `malformed.json` fixture and, for the single-export reducers, a CSV
with none of the expected columns, an empty export and one page of a paginated
response, and requires each to be refused (non-zero exit, nothing on standard
output, no traceback, no path); reads JSONC and NDJSON; checks that a skipped
file in a multi-file run turns a clean-reading value into not-checked; and
tests near-miss catalogue names and both directions of the secret, pin,
personal-spend and managed-tier matching.

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
    hidden = "ChatGPT" + "".join(chr(0xE0000 + ord(c)) for c in "ignore previous") + "\u200b\u202e"
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

    robustness(load)

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


def run_reducer(script: str, *args, cwd=None):
    return subprocess.run([sys.executable, "-I", str(RED / script), *map(str, args)],
                          capture_output=True, text=True, encoding="utf-8", cwd=cwd)


def refused(p, label: str, secret_bits=()) -> None:
    """A reducer that cannot read its input must print nothing on stdout, exit
    non-zero, and say so on stderr in a fixed line with no traceback, no path and
    no input text, so a malformed or partial export never reads as a clean count."""
    check(p.returncode != 0, f"{label}: exit 0 on unreadable input; stdout {p.stdout[-200:]!r}")
    check(p.stdout == "", f"{label}: printed on stdout although the input could not be read: {p.stdout[-200:]!r}")
    check("Traceback" not in p.stderr, f"{label}: printed a traceback")
    for bit in secret_bits:
        check(bit.lower() not in p.stderr.lower(), f"{label}: stderr names {bit!r}")


def robustness(load) -> None:
    """Malformed and partial inputs, near-miss catalogue names, and both directions
    of the secret, pin and personal-spend matching."""
    import json
    singles = ["browser_extensions.py", "entra_consent_grants.py", "expense_ai_vendors.py",
               "google_workspace_oauth.py", "okta_apps.py"]

    # 1. The malformed fixture in each reducer's folder is refused, and its file name is not echoed.
    for fx in sorted((RED / "fixtures").iterdir()):
        mal = fx / "malformed.json"
        check(mal.is_file(), f"{fx.name}: no malformed.json fixture")
        if not mal.is_file():
            continue
        p = run_reducer(fx.name.replace("-", "_") + ".py", mal.name, cwd=fx)
        refused(p, f"{fx.name}: malformed.json", ("malformed",))
    print("ok   every reducer refuses its malformed.json fixture without a traceback or a path")

    with tempfile.TemporaryDirectory(prefix="reducer-robustness-ZZPATHCANARY-") as td:
        td = Path(td)
        # 2. A CSV with none of the expected columns, an empty export, and a page of a longer list.
        wrong = td / "wrong-columns.csv"
        wrong.write_text("colour,weight\nred,3\nblue,4\n", encoding="utf-8")
        empty = td / "empty.json"
        empty.write_text("[]", encoding="utf-8")
        paged = td / "paged.json"
        paged.write_text(json.dumps({"value": [{"displayName": "ChatGPT", "consentType": "Principal",
                                                "scope": "Mail.Read", "label": "ChatGPT", "Merchant": "OPENAI",
                                                "Application name": "ChatGPT", "App name": "ChatGPT"}],
                                     "@odata.nextLink": "https://graph.example.invalid/next"}), encoding="utf-8")
        for script in singles:
            for f in (wrong, empty, paged):
                refused(run_reducer(script, f), f"{script} {f.name}", ("ZZPATHCANARY", "graph.example"))
        # 3. JSON with comments and trailing commas (VS Code mcp.json is JSONC), and NDJSON rows.
        jsonc = td / "mcp.json"
        jsonc.write_text('{\n  // a comment\n  "servers": {\n    "a": {"command": "npx", "args": ["pkg@1.0.0",],},\n'
                         '    /* block */ "b": {"url": "https://mcp.example.invalid/x"},\n  },\n}\n', encoding="utf-8")
        p = run_reducer("mcp_config.py", jsonc)
        doc = yaml.safe_load(p.stdout) if p.returncode == 0 else {}
        obs = (doc or {}).get("observations") or {}
        check(obs.get("mcp-server-count") == 2 and obs.get("mcp-pinned-count") == 1,
              f"mcp-config: JSONC config not read: {p.stdout[-300:]}{p.stderr[-200:]}")
        nd = td / "grants.ndjson"
        nd.write_text("\n".join(json.dumps({"displayName": n, "consentType": c, "scope": s}) for n, c, s in [
            ("ChatGPT", "Principal", "Mail.Read"), ("Claude", "AllPrincipals", "User.Read"),
            ("Payroll", "Principal", "User.Read")]) + "\n", encoding="utf-8")
        p = run_reducer("entra_consent_grants.py", nd)
        obs = ((yaml.safe_load(p.stdout) or {}) if p.returncode == 0 else {}).get("observations") or {}
        check(obs.get("ai-apps-with-grants") == 2 and obs.get("ai-grants-mail-or-file-scope") == 1,
              f"entra-consent-grants: NDJSON not read: {p.stdout[-300:]}{p.stderr[-200:]}")
        # 4. Multi-file reducers: one bad file among good ones is skipped, counted on stderr,
        #    and a zero that would read as clean becomes not-checked; all files bad is refused.
        bad = td / "bad.json"
        bad.write_text('{"mcpServers": {', encoding="utf-8")
        good = td / "good.json"
        good.write_text(json.dumps({"mcpServers": {"a": {"command": "npx", "args": ["pkg@1.0.0"]}}}), encoding="utf-8")
        p = run_reducer("mcp_config.py", good, bad)
        doc = (yaml.safe_load(p.stdout) or {}) if p.returncode == 0 else {}
        check(((doc.get("signals") or {}).get("mcp-unpinned") or {}).get("value") == "not-checked",
              f"mcp-config: a skipped file left mcp-unpinned reading clean: {p.stdout[-300:]}{p.stderr[-200:]}")
        check("1 of 2" in p.stderr and "ZZPATHCANARY" not in p.stderr, f"mcp-config: skip notice {p.stderr[-200:]!r}")
        refused(run_reducer("mcp_config.py", bad), "mcp-config: only a bad file", ("ZZPATHCANARY",))
        noserv = td / "no-servers.json"
        noserv.write_text(json.dumps({"theme": "dark", "projects": {}}), encoding="utf-8")
        p = run_reducer("mcp_config.py", noserv)
        sig = ((yaml.safe_load(p.stdout) or {}) if p.returncode == 0 else {}).get("signals") or {}
        check((sig.get("mcp-unpinned") or {}).get("value") == "not-checked"
              and (sig.get("mcp-remote") or {}).get("value") == "not-checked",
              f"mcp-config: a config with no servers printed a clean-reading 0: {p.stdout[-300:]}{p.stderr[-200:]}")
        cas_good = td / "settings.json"
        cas_good.write_text(json.dumps({"hooks": {"PreToolUse": [{"matcher": "*", "hooks": [
            {"type": "command", "command": "x", "onFailure": "block"}]}]}}), encoding="utf-8")
        p = run_reducer("coding_agent_settings.py", f"managed:{cas_good}", f"user:{bad}")
        sig = ((yaml.safe_load(p.stdout) or {}) if p.returncode == 0 else {}).get("signals") or {}
        check((sig.get("hook-fail-open") or {}).get("value") == "not-checked"
              and (sig.get("hooks-user-disableable") or {}).get("value") == "not-checked",
              f"coding-agent-settings: a skipped file left a false standing: {p.stdout[-400:]}{p.stderr[-200:]}")
        refused(run_reducer("coding_agent_settings.py", f"user:{bad}"), "coding-agent-settings: only a bad file",
                ("ZZPATHCANARY",))
        # 5. The sanitize notice names no file.
        tagged = td / "tagged-ZZFILECANARY.csv"
        tagged.write_text("App name,Install type\nChatGPT" + chr(0xE0041) + ",FORCED\n", encoding="utf-8")
        p = run_reducer("browser_extensions.py", tagged)
        check(p.returncode == 0 and "ZZFILECANARY" not in p.stderr and "sanitize" in p.stderr,
              f"browser-extensions: sanitize notice {p.stderr[-200:]!r}")
        # 6. Personal spend, both directions.
        exp = td / "spend.csv"
        rows = [("OPENAI", "Corporate card", 0), ("OPENAI", "Not reimbursable", 0), ("OPENAI", "Non-reimbursable", 0),
                ("OPENAI", "non reimbursable", 0), ("OPENAI", "No", 0), ("OPENAI", "false", 0),
                ("OPENAI", "Reimbursable", 1), ("OPENAI", "Personal card - reimbursement", 1), ("OPENAI", "yes", 1),
                ("OPENAI", "Out of pocket", 1), ("OPENAI", "TRUE", 1),
                ("OPENAI", "Personal card (non-corporate)", 1), ("OPENAI", "No reimbursement", 0)]
        for merchant, flag, want in rows:
            exp.write_text(f"Merchant,Payment method\n{merchant},{flag}\n", encoding="utf-8")
            p = run_reducer("expense_ai_vendors.py", exp)
            got = (((yaml.safe_load(p.stdout) or {}) if p.returncode == 0 else {}).get("observations") or {}).get(
                "ai-spend-lines-personal-card")
            check(got == want, f"expense-ai-vendors: {flag!r} counted {got} personal, want {want}")
        # 7. Google grants with no user column count rows, not one merged pair.
        g = td / "google.csv"
        g.write_text("Event name,Application name,Scope\nauthorize,ChatGPT,openid\nauthorize,ChatGPT,"
                     "https://www.googleapis.com/auth/drive.readonly\nauthorize,ChatGPT,email\n", encoding="utf-8")
        p = run_reducer("google_workspace_oauth.py", g)
        obs = ((yaml.safe_load(p.stdout) or {}) if p.returncode == 0 else {}).get("observations") or {}
        check(obs.get("ai-grants-user-consented") == 3 and obs.get("ai-grants-mail-or-file-scope") == 1,
              f"google-workspace-oauth: no user column: {p.stdout[-300:]}{p.stderr[-200:]}")
    print("ok   wrong columns, empty, paged, JSONC, NDJSON, skipped files, spend and grant edge cases")

    # 8. Near-miss catalogue names: each alternative keeps its word boundaries; NFKC folds full-width forms.
    cat = load("ai_catalog")
    for text, want in [("Cursor IDE", "Anysphere (Cursor)"), ("Anysphere", "Anysphere (Cursor)"),
                       ("cursor ideal", None), ("xanysphere", None), ("OpenAirline", None), ("mychatgpt", None),
                       ("ChatGPT Plus", "OpenAI"), ("OPENAI *CHATGPT", "OpenAI"), ("deeplink", None),
                       ("DeepL Pro", "DeepL"), ("claudette", None), ("Claude.ai", "Anthropic"), ("perplexityx", None),
                       ("tabnines", None), ("Grok app", "xAI"), ("groks", None), ("Gemini for Workspace", "Google"),
                       ("gemini", None), ("\uff23\uff48\uff41\uff54\uff27\uff30\uff34", "OpenAI")]:
        got = cat.ai_vendor(text)
        check(got == want, f"ai_catalog: {text!r} -> {got!r}, want {want!r}")
    print("ok   catalogue near-miss names and full-width forms")

    # 9. Secrets and pins, both directions.
    mc = load("mcp_config")
    for server, want_n, label in [
        ({"env": {"API_KEY": "prefix-${API_KEY}"}}, 0, "value containing ${VAR}"),
        ({"headers": {"Authorization": "Bearer ${env:TOKEN}"}}, 0, "Bearer ${env:VAR}"),
        ({"url": "https://user:EXAMPLEpassw0rd@mcp.example.invalid/sse"}, 1, "URL userinfo credential"),
        ({"url": "https://${USER}:${PASS}@mcp.example.invalid/sse"}, 0, "URL userinfo references"),
        ({"url": "https://mcp.example.invalid/sse?token=EXAMPLEtoken123"}, 1, "URL query token"),
        ({"url": "https://mcp.example.invalid/sse"}, 0, "plain URL"),
        ({"url": "https://user@mcp.example.invalid/sse"}, 0, "URL user without password"),
        ({"env": {"OPENAI_API_KEY": "sk-proj-EXAMPLEEXAMPLEEXAMPLE01"}}, 1, "token-shaped value"),
        ({"env": {"LOG_LEVEL": "sk-proj-EXAMPLEEXAMPLEEXAMPLE01"}}, 1, "token shape under any name"),
        ({"env": {"API_KEY": "short"}}, 0, "too short to be a credential"),
        ({"env": {"PROFILE": "risk-management-framework-2026"}}, 0, "'sk-' inside a word"),
        ({"args": ["--profile", "risk-management-framework-2026"]}, 0, "'sk-' inside a word in args"),
    ]:
        try:
            got_n = mc.count_secrets(server)
        except Exception as e:  # a crash is a failure, not a skip
            got_n = type(e).__name__
        check(got_n == want_n, f"mcp-config: {label}: counted {got_n}, want {want_n}")
    for spec, want in [("pkg@1.2.3", True), ("@scope/pkg@1.2.3", True), ("pkg==1.2.3", True), ("pkg@v1.2.3", True),
                       ("pkg@1.2.3-beta.1", True), ("pkg@latest", False), ("pkg@^1.2.3", False), ("pkg@~1.2", False),
                       ("pkg>=1.2", False), ("pkg", False), ("@scope/pkg", False), ("pkg@1", False), (None, False)]:
        check(mc.pinned(spec) is want, f"mcp-config: pinned({spec!r}) is {mc.pinned(spec)}, want {want}")
    print("ok   mcp-config secrets and pins in both directions")

    # 10. The managed tier comes from location or an explicit prefix, never the file name alone.
    cas = load("coding_agent_settings")
    for arg, want in [("managed-settings.json", "unscoped"), ("./project/managed-settings.json", "unscoped"),
                      ("/srv/x/etc/claude-code/managed-settings.json", "unscoped"),
                      ("/etc/claude-code/managed-settings.json", "managed"),
                      ("/Library/Application Support/ClaudeCode/managed-settings.json", "managed"),
                      ("C:\\Program Files\\ClaudeCode\\managed-settings.json", "managed"),
                      ("C:\\ProgramData\\Cursor\\hooks.json", "managed"),
                      ("managed:anything.json", "managed"), ("settings.local.json", "local")]:
        got = cas.split_arg(arg)[0]
        check(got == want, f"coding-agent-settings: {arg!r} classed {got}, want {want}")
    print("ok   coding-agent-settings classes the managed tier by location")


if __name__ == "__main__":
    sys.exit(main())
