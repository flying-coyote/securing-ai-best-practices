#!/usr/bin/env python3
"""
Test that each new check passes on the tree and fails on a deliberately broken
copy of it.

A check that reports clean when its instrument is broken manufactures the
evidence that nothing is wrong, so every check here is run twice: once on a
fresh copy of the repo (it must pass) and once on a copy with one defect
planted (it must fail, and say why). Nothing in the working tree is modified;
every copy lives in a temporary directory.

Some checks depend on a file being absent (no pins doc yet, an Always Fetch
doc not written). Those states belonged to the skeleton and vanish as the repo
fills in, so the test no longer reads them off the real tree: it plants each
one in its own temporary copy by removing the file there, which keeps every
check meaningful whether the working tree is a bare skeleton or a release
candidate.

Covered: check-prompt-blocks.py, check-routing-coverage.py,
render-audit-context.py (including the ordering rule it renders from
routing.yaml into the Priority rubric, held to route.py's sort keys),
route.py (including its reading of the sequence-order
block in analysis/decision-sequence.md, its conflicts and not-applicable
handling), check-exclusions.py, check-pins.py, probe-source-accessibility.py's
tally line, and build-release-bundle.sh (including the stamp step retiring
every pre-release statement and resetting the prompt blocks, and the bundle
reading the commit with git archive and refusing a missing routed doc or a
commit that names another release).

Usage: python scripts/test-checks.py
"""

import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
COPY = ["README.md", "ONE-LINE-PROMPT.md", "AUDIT-CONTEXT.md", "routing.yaml", "RELEASES.md",
        "CONTRIBUTING.md", "analysis", "fixtures", "scripts/reducers"]
results: list[tuple[bool, str]] = []
# results appended directly rather than through expect(), printed in the summary
DIRECT = {"bundle: AUDIT-CONTEXT header stamped",
          "bundle: stamp retires the banner, the prompt paragraph, the routing comment, the README banner and the pins Release line",
          "render: routing.yaml ordering names the mapper's keys in its sort order, with no tier or effort key",
          "bundle: RELEASES.md row carries the commit and the bundle's real SHA-256",
          "bundle: contains routing.yaml under its file header",
          "bundle: holds every routed doc",
          "bundle: carries no pre-release wording",
          "bundle: a refused stamp leaves AUDIT-CONTEXT unstamped",
          "bundle: two builds of the same tree have the same SHA-256",
          "bundle: stamp resets both prompt blocks to the placeholders",
          "probe: unknown moved state is counted, and the workflow parses both tally lines",
          "route: a reducer's yes on a row whose surfaces are all answered no is a conflict, not dropped",
          "route: a read no against a stated yes is a conflict and the yes stands",
          "route: not-applicable is neither clean, an action nor a packet"}


def tree(td: str) -> Path:
    root = Path(td) / "repo"
    root.mkdir()
    for name in COPY:
        src = ROOT / name
        if src.is_dir():
            shutil.copytree(src, root / name)
        else:
            shutil.copy2(src, root / name)
    return root


GIT_ENV = {"GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "test@example.invalid",
           "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "test@example.invalid",
           "GIT_AUTHOR_DATE": "2099-01-01T00:00:00Z", "GIT_COMMITTER_DATE": "2099-01-01T00:00:00Z",
           "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}


def git(root: Path, *args: str) -> str:
    import os
    p = subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false", "-c", "tag.gpgsign=false",
                        *args], cwd=root, capture_output=True, text=True, env=dict(os.environ, **GIT_ENV), check=True)
    return p.stdout.strip()


def commit(root: Path, allow_empty: bool = False) -> str:
    """Commit the whole test tree (a throwaway repo in a temporary directory) and
    return the SHA; identity and dates are fixed, so the same tree gives the same SHA."""
    if not (root / ".git").exists():
        git(root, "init", "-q")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "test", *(["--allow-empty"] if allow_empty else []))
    return git(root, "rev-parse", "HEAD")


def unwrite(root: Path, rel: str) -> str:
    """Plant the skeleton state 'this doc is not written yet' in a copy."""
    p = root / rel
    if p.is_file():
        p.unlink()
    return rel


def always_fetch(root: Path) -> list[str]:
    docs = list((yaml.safe_load((root / "routing.yaml").read_text(encoding="utf-8")) or {}).get("always-fetch") or [])
    assert docs, "routing.yaml has no always-fetch list to plant a missing doc from"
    return docs


def routed_docs(root: Path) -> list[str]:
    data = yaml.safe_load((root / "routing.yaml").read_text(encoding="utf-8")) or {}
    always = set(data.get("always-fetch") or [])
    return sorted({d for r in data["signals"] for d in r.get("docs", [])} - always)


def fill_routed(root: Path) -> list[str]:
    """Plant a placeholder for every routed doc not written yet, in a copy only, so the
    bundle's missing-doc refusal can be tested both ways whatever the working tree holds."""
    planted = []
    for d in routed_docs(root):
        p = root / d
        if not p.is_file():
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("---\nstatus: test-placeholder\n---\n\n# Placeholder planted by test-checks.py\n", encoding="utf-8")
            planted.append(d)
    return planted


def run(args: list[str], root: Path, env: dict | None = None) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(SCRIPTS / args[0]), *args[1:]] if args[0].endswith(".py") else [str(SCRIPTS / args[0]), *args[1:]]
    import os
    e = dict(os.environ, **(env or {}))
    return subprocess.run(cmd, cwd=root, capture_output=True, text=True, env=e)


def expect(label: str, proc: subprocess.CompletedProcess, ok: bool, needle: str | None = None):
    good = (proc.returncode == 0) == ok and (needle is None or needle in proc.stdout + proc.stderr)
    results.append((good, label))
    if not good:
        print(f"FAIL {label}: exit {proc.returncode}\n{proc.stdout[-800:]}{proc.stderr[-800:]}")
    else:
        print(f"ok   {label}")


def check(label: str, good: bool, detail: str = ""):
    """Record a check computed in the test itself (not from one process's exit code)."""
    results.append((good, label))
    print(f"ok   {label}" if good else f"FAIL {label}: {detail[-800:]}")


def route_out(r: Path, answers: str, *reducers: str) -> tuple[dict, subprocess.CompletedProcess]:
    """Run route.py on an Answers Block written into the copy; return its parsed output (empty on failure)."""
    a = r / "answers-under-test.yaml"
    a.write_text(answers, encoding="utf-8")
    paths = []
    for i, text in enumerate(reducers):
        q = r / f"reducer-under-test-{i}.yaml"
        q.write_text(text, encoding="utf-8")
        paths.append(str(q))
    p = run(["route.py", "--root", str(r), str(a), *paths], r)
    return (yaml.safe_load(p.stdout) or {}) if p.returncode == 0 else {}, p


def packet_keys(out: dict) -> list[str]:
    return [e["key"] for v in (out.get("question-packets") or {}).values() for e in v]


def edit(path: Path, old: str, new: str):
    text = path.read_text(encoding="utf-8")
    assert old in text, f"{path.name}: '{old[:40]}' not found"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def placeholder_blocks(r: Path):
    """Return the prompt blocks to their placeholder form, so these tests run
    the same before a release and after the default branch is bumped to a tag."""
    for f in ("README.md", "ONE-LINE-PROMPT.md"):
        p = r / f
        text = p.read_text(encoding="utf-8")
        text = re.sub(r"/securing-ai-best-practices/[0-9a-f]{40}/", "/securing-ai-best-practices/<release-sha>/", text)
        text = re.sub(r"commit [0-9a-f]{40}", "commit <release-sha>", text)
        text = re.sub(r"\(release v\d{4}\.\d{2}(?:\.\d+)?([;,])", r"(release <vYYYY.MM>\1", text)
        p.write_text(text, encoding="utf-8")


def main() -> int:
    sha = "0123456789abcdef0123456789abcdef01234567"

    # check-prompt-blocks
    with tempfile.TemporaryDirectory() as td:
        r = tree(td)
        placeholder_blocks(r)
        expect("prompt blocks pass on the tree", run(["check-prompt-blocks.py", "--root", str(r)], r), True)
        expect("prompt blocks: tag given while placeholder remains fails",
               run(["check-prompt-blocks.py", "--root", str(r), "--tag-commit", sha], r), False, "placeholder")
        for f in ("README.md", "ONE-LINE-PROMPT.md"):
            edit(r / f, "<release-sha>/AUDIT-CONTEXT.md", f"{sha}/AUDIT-CONTEXT.md")
            edit(r / f, "(release <vYYYY.MM>;", "(release v2099.01;")
        edit(r / "ONE-LINE-PROMPT.md", "(release <vYYYY.MM>, commit <release-sha>;", f"(release v2099.01, commit {sha};")
        expect("prompt blocks: bumped to the tag's commit passes",
               run(["check-prompt-blocks.py", "--root", str(r), "--tag-commit", sha, "--tag", "v2099.01"], r), True)
        expect("prompt blocks: pinned SHA differs from the tag's commit fails",
               run(["check-prompt-blocks.py", "--root", str(r), "--tag-commit", "f" * 40], r), False, "newest tag points at")
        edit(r / "README.md", "Tested agents: each release", "Tested agents: none yet. Each release")
        expect("prompt blocks: 'Tested agents: none yet' beside a release row fails",
               run(["check-prompt-blocks.py", "--root", str(r), "--tag-commit", sha], r), False, "none yet")
        edit(r / "README.md", "Tested agents: none yet. Each release", "Tested agents: each release")
        edit(r / "README.md", "On the tagged commit the blocks below carry", "The blocks below still carry")
        expect("prompt blocks: banner says placeholders remain while the block is pinned fails",
               run(["check-prompt-blocks.py", "--root", str(r), "--tag-commit", sha], r), False, "status banner")
        edit(r / "README.md", "The blocks below still carry", "On the tagged commit the blocks below carry")
        edit(r / "ONE-LINE-PROMPT.md", "On the tagged commit the blocks below carry", "The blocks below still carry")
        expect("prompt blocks: ONE-LINE-PROMPT paragraph says placeholders remain while the block is pinned fails",
               run(["check-prompt-blocks.py", "--root", str(r), "--tag-commit", sha], r), False, "ONE-LINE-PROMPT release paragraph")
        edit(r / "ONE-LINE-PROMPT.md", "The blocks below still carry", "On the tagged commit the blocks below carry")
        edit(r / "ONE-LINE-PROMPT.md", f"(release v2099.01, commit {sha};", "(release v2099.01, commit " + "e" * 40 + ";")
        expect("prompt blocks: offline block naming another commit fails",
               run(["check-prompt-blocks.py", "--root", str(r), "--tag-commit", sha], r), False, "offline block names")
        edit(r / "ONE-LINE-PROMPT.md", "(release v2099.01, commit " + "e" * 40 + ";", f"(release v2099.01, commit {sha};")
        edit(r / "ONE-LINE-PROMPT.md", "release: <tag from AUDIT-CONTEXT.md's Release line> (<full commit SHA from the block you were given>)",
             f"release: v2099.01 ({sha})")
        expect("prompt blocks: a release written into the output template fails",
               run(["check-prompt-blocks.py", "--root", str(r), "--tag-commit", sha], r), False, "release line names a release")
        edit(r / "ONE-LINE-PROMPT.md", f"release: v2099.01 ({sha})",
             "release: <tag from AUDIT-CONTEXT.md's Release line> (<full commit SHA from the block you were given>)")
        edit(r / "README.md", "Change nothing in any system.", "Change nothing.")
        expect("prompt blocks: README block drifts from ONE-LINE-PROMPT fails",
               run(["check-prompt-blocks.py", "--root", str(r), "--tag-commit", sha], r), False, "differ")

    # render-audit-context and check-routing-coverage
    with tempfile.TemporaryDirectory() as td:
        r = tree(td)
        expect("render --check passes on the tree", run(["render-audit-context.py", "--root", str(r), "--check"], r), True)
        expect("routing coverage passes on the tree", run(["check-routing-coverage.py", "--root", str(r)], r), True)
    with tempfile.TemporaryDirectory() as td:
        r = tree(td)
        unwrite(r, always_fetch(r)[0])
        expect("routing coverage --release fails while routed docs are unwritten",
               run(["check-routing-coverage.py", "--root", str(r), "--release"], r), False, "not written")
    with tempfile.TemporaryDirectory() as td:
        r = tree(td)
        edit(r / "routing.yaml", "      factors: {reach: 2, stakes: 2, reversibility: 1, blast: 1}",
             "      factors: {reach: 0, stakes: 2, reversibility: 1, blast: 1}")
        expect("routing coverage: factors that no longer fold into the band fail",
               run(["check-routing-coverage.py", "--root", str(r)], r), False, "does not fold")
    with tempfile.TemporaryDirectory() as td:
        r = tree(td)
        edit(r / "routing.yaml", "docs: [analysis/tamper-evident-record.md]", "docs: [analysis/tamper-evident-record.md, analysis/other.md]")
        expect("render --check fails after routing.yaml changes", run(["render-audit-context.py", "--root", str(r), "--check"], r), False, "stale")
        expect("routing coverage fails on a stale rendered section", run(["check-routing-coverage.py", "--root", str(r)], r), False, "stale")
        expect("render rewrites the section", run(["render-audit-context.py", "--root", str(r)], r), True)
        expect("render --check passes after rendering", run(["render-audit-context.py", "--root", str(r), "--check"], r), True)
    with tempfile.TemporaryDirectory() as td:
        r = tree(td)
        edit(r / "routing.yaml", "then the sequence group from", "then the backing doc's evidence tier, then the sequence group from")
        expect("render --check fails when routing.yaml's ordering rule changes", run(["render-audit-context.py", "--root", str(r), "--check"], r), False, "ordering rule is stale")
        expect("routing coverage fails when the ordering rule drifts", run(["check-routing-coverage.py", "--root", str(r)], r), False, "stale")
        expect("render rewrites the ordering rule", run(["render-audit-context.py", "--root", str(r)], r), True)
        results.append(("then the backing doc's evidence tier, then the sequence group" in (r / "AUDIT-CONTEXT.md").read_text(encoding="utf-8"),
                        "render: the ordering rule in AUDIT-CONTEXT is the one routing.yaml states"))
    with tempfile.TemporaryDirectory() as td:
        r = tree(td)
        ac = r / "AUDIT-CONTEXT.md"
        text = ac.read_text(encoding="utf-8")
        i = text.index("<!-- ordering:end -->")
        ac.write_text(text[:i] + "For a small organization, rank effort S above M within a band.\n" + text[i:], encoding="utf-8")
        expect("render --check fails on a hand edit inside the ordering rule", run(["render-audit-context.py", "--root", str(r), "--check"], r), False, "stale")
    # the ordering rule routing.yaml states (and AUDIT-CONTEXT renders) names route.py's sort keys in order
    ordering = (yaml.safe_load((ROOT / "routing.yaml").read_text(encoding="utf-8"))["priority-rubric"]["ordering"])
    route_src = (SCRIPTS / "route.py").read_text(encoding="utf-8")
    m = re.search(r'^ORDERING = \((.*?)\)\n', route_src, re.S | re.M)
    mapper = "".join(re.findall(r'"([^"]*)"', m.group(1))) if m else ""
    def in_order(text, needles):
        pos = [text.find(n) for n in needles]
        return all(p >= 0 for p in pos) and pos == sorted(pos)
    sort_key = re.search(r"def sort_items.*?key=lambda t: \((.*?)\)\)", route_src, re.S)
    results.append((in_order(ordering, ["Within a band", "factor sum, highest first", "sequence group", "`#`"])
                    and in_order(mapper, ["band", "factor sum descending", "sequence group", "routing.yaml row order"])
                    and bool(sort_key) and in_order(sort_key.group(1), ["BAND_RANK", "factor-sum", "sequence-group", "t[0]"])
                    and "Tier does not break ties" in ordering and "never sort by it" in ordering
                    and not re.search(r"evidence tier as the tie-breaker", ordering),
                    "render: routing.yaml ordering names the mapper's keys in its sort order, with no tier or effort key"))
    with tempfile.TemporaryDirectory() as td:
        r = tree(td)
        doc = r / "analysis" / "tamper-evident-record.md"
        doc.write_text("---\nevidence-tier: B\nconvergence: single-source\napplies-to-signals: [not-a-key]\n"
                       "status: EMERGING\n---\n\n# Stub\n", encoding="utf-8")
        p = run(["check-routing-coverage.py", "--root", str(r)], r)
        expect("routing coverage: a shipped doc listing a non-key fails", p, False, "not a routing key")
        expect("routing coverage: a shipped doc missing a key routed to it fails", p, False, "does not list it")
        orphan = r / "analysis" / "orphan.md"
        orphan.write_text("---\nevidence-tier: B\napplies-to-signals: []\nstatus: PRODUCTION\n---\n", encoding="utf-8")
        expect("routing coverage: an unrouted shipped doc fails",
               run(["check-routing-coverage.py", "--root", str(r)], r), False, "no routing row names it")
    with tempfile.TemporaryDirectory() as td:
        r = tree(td)
        edit(r / "routing.yaml", "      escalate-if: [runtime-internet-reachable]\n", "")
        expect("routing coverage: an escalation without escalate-if fails",
               run(["check-routing-coverage.py", "--root", str(r)], r), False, "escalate-if")

    # route.py
    with tempfile.TemporaryDirectory() as td:
        r = tree(td)
        expect("route.py fixtures match their goldens", run(["route.py", "--root", str(r), "--check-fixtures"], r), True)
        edit(r / "routing.yaml", "      band: High\n      factors: {reach: 1, stakes: 2, reversibility: 1, blast: 2}\n    docs: [analysis/stubs/ai-incident-response.md]",
             "      band: Low\n      factors: {reach: 1, stakes: 2, reversibility: 1, blast: 2}\n    docs: [analysis/stubs/ai-incident-response.md]")
        expect("route.py: a band change moves a golden and fails",
               run(["route.py", "--root", str(r), "--check-fixtures"], r), False, "differs")
    with tempfile.TemporaryDirectory() as td:
        r = tree(td)
        bad = r / "bad.yaml"
        bad.write_text("answers-block: 1\nsignals:\n  no-such-key: true\n", encoding="utf-8")
        expect("route.py: an unknown key is refused", run(["route.py", "--root", str(r), str(bad)], r), False, "not a routing key")
        bad.write_text("answers-block: 1\nsignals:\n  audit-log-off-mainframe: true\n", encoding="utf-8")
        expect("route.py: a platform outside the closed list is refused", run(["route.py", "--root", str(r), str(bad)], r), False, "platform list")
        bad.write_text("answers-block: 1\nsignals:\n  surface-S1: maybe\n", encoding="utf-8")
        expect("route.py: a free-text value is refused", run(["route.py", "--root", str(r), str(bad)], r), False, "must be")
    # route.py never discards an answer: ineligible yes and read-vs-stated disagreements are conflicts
    with tempfile.TemporaryDirectory() as td:
        r = tree(td)
        a = r / "a.yaml"
        a.write_text("answers-block: 1\nsignals:\n  org-size-small-mid: true\n  surface-S4: false\n"
                     "  surface-S5: false\n  surface-S8: false\n", encoding="utf-8")
        red = r / "red.yaml"
        red.write_text("reducer: mcp-config\nversion: 1\nsignals:\n  agent-static-secrets: {value: true, confidence: read}\n",
                       encoding="utf-8")
        p = run(["route.py", "--root", str(r), str(a), str(red)], r)
        out = yaml.safe_load(p.stdout) if p.returncode == 0 else {}
        results.append((any(c.startswith("agent-static-secrets:") and "enablers" in c for c in out.get("conflicts", [])),
                        "route: a reducer's yes on a row whose surfaces are all answered no is a conflict, not dropped"))
        a.write_text("answers-block: 1\nsignals:\n  org-size-small-mid: true\n  surface-S4: true\n"
                     "  hook-fail-open: {value: true, confidence: owner-stated}\n", encoding="utf-8")
        red.write_text("reducer: coding-agent-settings\nversion: 1\nsignals:\n  hook-fail-open: {value: false, confidence: read}\n",
                       encoding="utf-8")
        p = run(["route.py", "--root", str(r), str(a), str(red)], r)
        out = yaml.safe_load(p.stdout) if p.returncode == 0 else {}
        results.append((any(c.startswith("hook-fail-open:") and "stated yes stands" in c for c in out.get("conflicts", []))
                        and any(x["key"] == "hook-fail-open" for x in out.get("actions", []))
                        and "hook-fail-open" not in out.get("clean", []),
                        "route: a read no against a stated yes is a conflict and the yes stands"))
        a.write_text("answers-block: 1\nsignals:\n  org-size-small-mid: true\n  surface-S4: true\n"
                     "  hook-fail-open: not-applicable\n", encoding="utf-8")
        p = run(["route.py", "--root", str(r), str(a)], r)
        out = yaml.safe_load(p.stdout) if p.returncode == 0 else {}
        packeted = [e["key"] for v in (out.get("question-packets") or {}).values() for e in v]
        results.append((out.get("not-applicable") == ["hook-fail-open"] and "hook-fail-open" not in out.get("clean", [])
                        and "hook-fail-open" not in packeted
                        and not any(x["key"] == "hook-fail-open" for x in out.get("actions", []) + out.get("review", [])),
                        "route: not-applicable is neither clean, an action nor a packet"))
        a.write_text("answers-block: 1\nobservations:\n  runtime-internet-reachable: not-applicable\n", encoding="utf-8")
        expect("route.py: not-applicable is refused for an observation",
               run(["route.py", "--root", str(r), str(a)], r), False, "must be")

    # route.py: the small-org branch, gates, follow-ups and the other routing rules the review findings asked for
    with tempfile.TemporaryDirectory() as td:
        r = tree(td)
        short = yaml.safe_load((r / "fixtures/small-org-short/expected.yaml").read_text(encoding="utf-8"))
        pk = packet_keys(short)
        check("route: small-org asks only its own questions; unasked rows are not-asked, never packets",
              not {"delegation-record-absent", "record-in-agent-reach", "coverage-view-absent"} & set(pk)
              and {"delegation-record-absent", "record-in-agent-reach", "coverage-view-absent"} <= set(short.get("not-asked", []))
              and "anything-else" in pk and "plan-tier-below-audit" in pk, str(pk))
        data = yaml.safe_load((r / "routing.yaml").read_text(encoding="utf-8"))
        claims = []
        for b in ("small-org", "full"):
            claims += re.findall(r"(\d+) on fixtures/([a-z-]+)", str(data["interview-branches"][b].get("target", "")))
        got = {n: yaml.safe_load((r / "fixtures" / n / "expected.yaml").read_text(encoding="utf-8")).get("questions-asked")
               for _, n in claims}
        check("route: the question counts routing.yaml claims are the ones route.py measures on the fixtures",
              len(claims) >= 3 and all(got[n] == int(c) for c, n in claims), f"{claims} vs {got}")
        # DPIA and works council are gated on capture and jurisdiction
        out, p = route_out(r, "answers-block: 1\nsignals:\n  org-size-large-regulated: true\n  jurisdiction-us: true\n"
                              "  content-channel-off: true\n  dpia-absent: false\n  works-council-unconsulted: false\n")
        rows = [x["key"] for x in out.get("actions", []) + out.get("review", [])] + out.get("clean", []) + packet_keys(out)
        check("route: a US-only block with no capture shows the DPIA and works-council rows nowhere",
              p.returncode == 0 and "dpia-absent" not in rows and "works-council-unconsulted" not in rows, p.stdout + p.stderr)
        out, p = route_out(r, "answers-block: 1\nsignals:\n  org-size-large-regulated: true\n  content-channel-on: true\n")
        check("route: capture on with jurisdiction unanswered keeps the DPIA row as a packet",
              "dpia-absent" in packet_keys(out), p.stdout + p.stderr)
        # a believed answer keeps its band; a believed escalation input adds the deadline too
        out, p = route_out(r, "answers-block: 1\nobservations:\n  runtime-internet-reachable: {value: true, confidence: believed}\n"
                              "signals:\n  org-size-large-regulated: true\n  surface-S4: true\n  surface-S9: true\n"
                              "  agent-static-secrets: {value: true, confidence: believed}\n"
                              "  inference-runtime-default-bind: {value: true, confidence: owner-stated}\n")
        acts = {x["key"]: x for x in out.get("actions", [])}
        check("route: a believed High stays High with a confirm deadline, and so does a believed escalation",
              acts.get("agent-static-secrets", {}).get("band") == "High" and "confirm-within-days" in acts["agent-static-secrets"]
              and acts.get("inference-runtime-default-bind", {}).get("band") == "High"
              and "confirm-within-days" in acts["inference-runtime-default-bind"], p.stdout + p.stderr)
        # every platform a present surface implies is packeted; a platform whose surface is no is a conflict
        out, p = route_out(r, "answers-block: 1\nsignals:\n  org-size-large-regulated: true\n  surface-S2: true\n  surface-S3: true\n"
                              "  surface-S4: false\n  audit-log-off-office-suite-assistant: true\n  audit-log-off-coding-agent: true\n")
        check("route: one platform answered still packets the others a present surface implies",
              "audit-log-off-browser" in packet_keys(out)
              and any(c.startswith("audit-log-off-coding-agent:") for c in out.get("conflicts", []))
              and "audit-log-off-coding-agent" not in [x["key"] for x in out.get("actions", [])], p.stdout + p.stderr)
        check("route: an unknown escalation input on a selected row is a follow-up question on the full branch",
              "internet-reachable-office-suite-assistant" in packet_keys(out), p.stdout)
        # a family not run suppresses its rows and joins the how-do-you-know line
        out, p = route_out(r, "answers-block: 1\nsignals:\n  org-size-large-regulated: true\n  surface-S1: true\n"
                              "  family-not-run-saas: true\n")
        check("route: family-not-run suppresses the family's rows and is asked how-do-you-know",
              out.get("families-not-run") == ["saas"] and "saas-ai-toggles-unreviewed" not in packet_keys(out)
              and any("family-not-run-saas" in e["why"] for e in out.get("question-packets", {}).get("security lead", [])),
              p.stdout + p.stderr)
        # on-trigger is a value only the capture tiers accept; a stub-backed action is a declared gap
        out, p = route_out(r, "answers-block: 1\nsignals:\n  org-size-large-regulated: true\n"
                              "  prompt-capture-tier-delta: on-trigger\n  agent-kill-switch-absent: true\n")
        rev = {x["key"]: x for x in out.get("review", [])}
        acts = {x["key"]: x for x in out.get("actions", [])}
        check("route: on-trigger selects a capture tier and is quoted; a stub-backed action carries declared-gap",
              rev.get("prompt-capture-tier-delta", {}).get("answered") == "on-trigger"
              and acts.get("agent-kill-switch-absent", {}).get("declared-gap") is True
              and "priority-basis" in out, p.stdout + p.stderr)
        _, p = route_out(r, "answers-block: 1\nsignals:\n  ai-aup-absent: on-trigger\n")
        expect("route.py: on-trigger is refused on a row that does not list it", p, False, "must be")
        # reducer output: named sources only, once each, counts printed as floors
        red = "reducer: entra-consent-grants\nversion: 1\nobservations:\n  ai-apps-with-grants: 3\nsignals: {}\n"
        _, p = route_out(r, "answers-block: 1\nsignals:\n  org-size-large-regulated: true\n", red, red)
        expect("route.py: a second block from the same reducer is refused, never summed", p, False, "second output")
        _, p = route_out(r, "answers-block: 1\nsignals: {}\n", "reducer: totally-real\nversion: 1\nobservations: {}\nsignals: {}\n")
        expect("route.py: a reducer routing.yaml does not name is refused", p, False, "not one routing.yaml names")
        out, p = route_out(r, "answers-block: 1\nsignals:\n  org-size-large-regulated: true\n", red)
        check("route: read counts are printed as floors", out.get("counts-at-least") == {"ai-apps-with-grants": 3}, p.stdout)

    # check-routing-coverage: the new joins fail closed
    with tempfile.TemporaryDirectory() as td:
        r = tree(td)
        doc = r / "analysis/tamper-evident-record.md"
        edit(doc, "\nstatus: EMERGING\n", "\nstatus: EMERGNIG\n")
        expect("routing coverage: a mistyped status fails instead of exempting the doc",
               run(["check-routing-coverage.py", "--root", str(r)], r), False, "not one the canonical template lists")
    with tempfile.TemporaryDirectory() as td:
        r = tree(td)
        edit(r / "routing.yaml", ', question: "Is that runtime reachable from the internet?"}', "}")
        expect("routing coverage: an interview escalation input with no question fails",
               run(["check-routing-coverage.py", "--root", str(r)], r), False, "has no question")
    with tempfile.TemporaryDirectory() as td:
        r = tree(td)
        edit(r / "routing.yaml", "  - key: delegation-record-absent\n    family: identity\n", "  - key: delegation-record-absent\n    family: identity\n    method: [I, E]\n")
        text = (r / "routing.yaml").read_text(encoding="utf-8")
        i = text.index("  - key: delegation-record-absent")
        j = text.index("    method: [I]\n", i)
        (r / "routing.yaml").write_text(text[:j] + text[j + len("    method: [I]\n"):], encoding="utf-8")
        expect("routing coverage: a row collected by E with no reducer behind it fails",
               run(["check-routing-coverage.py", "--root", str(r)], r), False, "no shipped reducer prints it")
    with tempfile.TemporaryDirectory() as td:
        r = tree(td)
        edit(r / "AUDIT-CONTEXT.md", "Always fetch these four", "Always fetch these five")
        expect("routing coverage: an always-fetch count that disagrees with AUDIT-CONTEXT fails",
               run(["check-routing-coverage.py", "--root", str(r)], r), False, "Always fetch these five")

    seq_doc = "analysis/decision-sequence.md"
    with tempfile.TemporaryDirectory() as td:
        r = tree(td)
        edit(r / seq_doc, "\nsequence-order:\n", "\nsequence-ordering:\n")
        expect("route.py: no sequence-order block is refused, not silently replaced by another order",
               run(["route.py", "--root", str(r), "--check-fixtures"], r), False, "sequence-order")
    with tempfile.TemporaryDirectory() as td:
        r = tree(td)
        edit(r / seq_doc, "  7-containment: [incident-response]\n", "  7-containment: []\n")
        expect("route.py: a family in no sequence group is refused",
               run(["route.py", "--root", str(r), "--check-fixtures"], r), False, "families in no sequence group")
    with tempfile.TemporaryDirectory() as td:
        r = tree(td)
        edit(r / seq_doc, "  containment-pre-authorized-broad: 7-containment\n",
             "  containment-pre-authorized-broad: 9-no-such-group\n")
        expect("route.py: a row override naming an unknown group is refused",
               run(["route.py", "--root", str(r), "--check-fixtures"], r), False, "not a sequence group")
    with tempfile.TemporaryDirectory() as td:
        r = tree(td)
        edit(r / seq_doc, "  1-ownership: [profile, surface]\n  2-risk-tolerance-and-owners: [governance]\n",
             "  1-ownership: [profile, surface]\n  2-risk-tolerance-and-owners: [frameworks]\n")
        edit(r / seq_doc, "  8-vendor-conversation: [frameworks]\n", "  8-vendor-conversation: [governance]\n")
        expect("route.py: moving a family to another sequence group moves a golden and fails",
               run(["route.py", "--root", str(r), "--check-fixtures"], r), False, "differs")

    # check-exclusions
    with tempfile.TemporaryDirectory() as td:
        r = tree(td)
        expect("exclusions pass on the tree", run(["check-exclusions.py", "--root", str(r)], r), True)
        planted = r / "analysis" / "planted.md"
        planted.write_text("---\nmeasurement-claims:\n  - claim: x\n    source: " + "/" + "tmp/" + "run/RESULTS.md\n---\n"
                           "See LLM01" + ":2025 and " + "scf" + "-mapping/ai-frameworks and " + "/" + "home/someone/notes.\n",
                           encoding="utf-8")
        p = run(["check-exclusions.py", "--root", str(r)], r)
        for rule in ("tmp-source", "owasp-2025-id", "licensed-crosswalk", "local-path"):
            expect(f"exclusions: planted {rule} is found", p, False, rule)
        planted.unlink()
        edit(r / "ONE-LINE-PROMPT.md", "This review is not legal advice.\n\n1. Read AUDIT-CONTEXT.md from the bundle",
             "\n\n1. Read AUDIT-CONTEXT.md from the bundle")
        expect("exclusions: not-legal-advice removed from the offline block fails",
               run(["check-exclusions.py", "--root", str(r)], r), False, "Offline mode block")

    # check-pins
    with tempfile.TemporaryDirectory() as td:
        r = tree(td)
        unwrite(r, "analysis/revalidation-and-pins.md")
        expect("pins: no pins doc yet passes", run(["check-pins.py", "--root", str(r)], r), True, "not written yet")
        (r / "analysis" / "revalidation-and-pins.md").write_text(
            "---\npins:\n  - \"MITRE ATLAS v2026.10\"\n  - \"OCSF 1.9.0\"\n---\n", encoding="utf-8")
        (r / "analysis" / "old.md").write_text("---\npins:\n  - \"MITRE ATLAS v2026.06\"\n---\n", encoding="utf-8")
        expect("pins: a doc behind the pins doc is counted and does not fail",
               run(["check-pins.py", "--root", str(r)], r), True, "behind analysis/old.md")
        cur = r / "current.yaml"
        cur.write_text("MITRE ATLAS: v2026.11\n", encoding="utf-8")
        expect("pins: the pins doc behind the newest known release fails",
               run(["check-pins.py", "--root", str(r), "--current", str(cur)], r), False, "newest known")

    # probe-source-accessibility: a failed moved-past-pin probe is unknown, never clean,
    # and the workflow parses the tally lines the script actually prints
    import importlib.util
    spec = importlib.util.spec_from_file_location("probe", SCRIPTS / "probe-source-accessibility.py")
    probe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(probe)
    line = probe.tally_line([
        {"page_state": "ok", "moved": None, "checks_moved": False},   # page-only probe: nothing to read
        {"page_state": "ok", "moved": None, "checks_moved": True},    # API probe failed
        {"page_state": "not-pinned", "moved": None},                  # no pin to probe
        {"page_state": "ok", "moved": False, "checks_moved": True},
    ])
    wf = (ROOT / ".github" / "workflows" / "checks.yml").read_text(encoding="utf-8")
    probe_src = (SCRIPTS / "probe-source-accessibility.py").read_text(encoding="utf-8")
    results.append((line == "sources-probed=4 broken=0 refused=0 moved=0 unknown=2"
                    and all(f"fields('{pfx}')" in wf and f"{pfx}=" in probe_src for pfx in ("sources-probed", "source-urls-probed"))
                    and "'unknown'" in wf,
                    "probe: unknown moved state is counted, and the workflow parses both tally lines"))

    # build-release-bundle.sh (the bundle step reads a commit with git archive, so each
    # test tree is made a throwaway git repo with a fixed identity and date)
    with tempfile.TemporaryDirectory() as td:
        r = tree(td)
        env = {"ROOT": str(r)}
        placeholder_blocks(r)
        c = commit(r)
        expect("bundle: refuses to build before the stamp step",
               run(["build-release-bundle.sh", "bundle", "v2099.01", c], r, dict(env, ALLOW_MISSING="1")), False, "not stamped")
        expect("bundle: refuses a SHA that is not a commit",
               run(["build-release-bundle.sh", "bundle", "v2099.01", "f" * 40], r, dict(env, ALLOW_MISSING="1")), False, "is not a commit")
        expect("bundle: stamp writes the tag and date", run(["build-release-bundle.sh", "stamp", "v2099.01", "2099-01-01"], r, env), True)
        ac = (r / "AUDIT-CONTEXT.md").read_text(encoding="utf-8")
        results.append(("Release: v2099.01. Date: 2099-01-01." in ac, "bundle: AUDIT-CONTEXT header stamped"))
        olp = (r / "ONE-LINE-PROMPT.md").read_text(encoding="utf-8")
        ry = (r / "routing.yaml").read_text(encoding="utf-8")
        pins = (r / "analysis" / "revalidation-and-pins.md").read_text(encoding="utf-8")
        readme = (r / "README.md").read_text(encoding="utf-8")
        results.append(("> Pre-release." not in ac and "should stop and say the repo is unreleased" not in ac
                        and "has not cut a release yet" not in olp and "release v2099.01, stamped 2099-01-01" in olp
                        and "still carry" not in olp
                        and "State: pre-release" not in ry and "# State: release v2099.01, stamped 2099-01-01." in ry
                        and "release: v2099.01\n" in ry
                        and "Release: unreleased" not in pins and "Release: v2099.01; pins last verified" in pins
                        and "Status: pre-release" not in readme and "> Status: release v2099.01, stamped 2099-01-01." in readme
                        and "<!-- pre-release:start" in readme and "<!-- pre-release:end -->" in readme,
                        "bundle: stamp retires the banner, the prompt paragraph, the routing comment, the README banner and the pins Release line"))
        held = always_fetch(r)[0]
        body = (r / held).read_bytes()
        unwrite(r, held)
        c = commit(r)
        expect("bundle: refuses to build while Always Fetch docs are missing",
               run(["build-release-bundle.sh", "bundle", "v2099.01", c], r, env), False, "Always Fetch docs missing")
        (r / held).write_bytes(body)
        fill_routed(r)
        gone = unwrite(r, routed_docs(r)[0])
        c = commit(r)
        expect("bundle: refuses to build while a routed doc is missing",
               run(["build-release-bundle.sh", "bundle", "v2099.01", c], r, env), False, f"routed docs missing (1)")
        expect("bundle: names the missing routed doc", run(["build-release-bundle.sh", "bundle", "v2099.01", c], r, env), False, gone)
        p = run(["build-release-bundle.sh", "bundle", "v2099.01", c], r, dict(env, ALLOW_MISSING="1"))
        expect("bundle: builds with ALLOW_MISSING=1", p, True)
        out = r / "dist" / "securing-ai-best-practices-v2099.01.md"
        digest = hashlib.sha256(out.read_bytes()).hexdigest() if out.is_file() else ""
        rel = (r / "RELEASES.md").read_text(encoding="utf-8")
        results.append((bool(digest) and digest in rel and c in rel and digest in p.stdout,
                        "bundle: RELEASES.md row carries the commit and the bundle's real SHA-256"))
        results.append((bool(re.search(r"^===== FILE: routing.yaml =====$", out.read_text(encoding="utf-8"), re.M)) if out.is_file() else False,
                        "bundle: contains routing.yaml under its file header"))
        expect("bundle: refuses a second row for the same tag",
               run(["build-release-bundle.sh", "bundle", "v2099.01", c], r, dict(env, ALLOW_MISSING="1")), False, "already has a row")
    with tempfile.TemporaryDirectory() as td:
        r = tree(td)
        env = {"ROOT": str(r)}
        fill_routed(r)
        run(["build-release-bundle.sh", "stamp", "v2099.01", "2099-01-01"], r, env)
        c = commit(r)
        (r / "routing.yaml").write_text("not: [the committed file\n", encoding="utf-8")
        expect("bundle: builds from the commit, not an edited working tree",
               run(["build-release-bundle.sh", "bundle", "v2099.01", c], r, env), True, "sha256:")
        git(r, "checkout", "-q", "--", "routing.yaml")
        out = (r / "dist" / "securing-ai-best-practices-v2099.01.md")
        text = out.read_text(encoding="utf-8") if out.is_file() else ""
        results.append((all(f"===== FILE: {d} =====" in text for d in routed_docs(r)),
                        "bundle: holds every routed doc"))
        results.append(("pre-release:start" in text and "has not cut a release yet" not in text
                        and "Release: unreleased" not in text, "bundle: carries no pre-release wording"))
        expect("bundle: a second stamp for the next release finds the markers again",
               run(["build-release-bundle.sh", "stamp", "v2027.01", "2027-01-05"], r, env), True, "stamped v2027.01")
    with tempfile.TemporaryDirectory() as td:
        # the v2026.12 and v2026.12.1 defect: the tagged copy pinned the release before it
        r = tree(td)
        env = {"ROOT": str(r), "ALLOW_MISSING": "1"}
        prior_tag = re.search(r"^\| (v\S+) \| [^|]* \| `([0-9a-f]{40})`", (r / "RELEASES.md").read_text(encoding="utf-8"), re.M)
        run(["build-release-bundle.sh", "stamp", "v2099.01", "2099-01-01"], r, env)
        olp_t = (r / "ONE-LINE-PROMPT.md").read_text(encoding="utf-8")
        results.append(("<release-sha>/AUDIT-CONTEXT.md" in olp_t and "(release <vYYYY.MM>, commit <release-sha>;" in olp_t
                        and not re.search(r"/securing-ai-best-practices/[0-9a-f]{40}/", olp_t)
                        and "<release-sha>/AUDIT-CONTEXT.md" in (r / "README.md").read_text(encoding="utf-8"),
                        "bundle: stamp resets both prompt blocks to the placeholders"))
        for f in ("README.md", "ONE-LINE-PROMPT.md"):
            edit(r / f, "<release-sha>/AUDIT-CONTEXT.md", f"{prior_tag.group(2)}/AUDIT-CONTEXT.md")
        c = commit(r)
        expect("bundle: refuses a commit whose blocks pin an earlier release",
               run(["build-release-bundle.sh", "bundle", "v2099.01", c], r, env), False, "check-prompt-blocks.py fails")
        expect("prompt blocks: a stamped tree naming an earlier release's commit fails",
               run(["check-prompt-blocks.py", "--root", str(r), "--tag-commit", prior_tag.group(2)], r), False,
               f"names {prior_tag.group(1)}'s commit")
        git(r, "tag", "v2099.01", "HEAD~0")
        other = commit(r, allow_empty=True)
        expect("bundle: refuses when the local tag points at another commit",
               run(["build-release-bundle.sh", "bundle", "v2099.01", other], r, env), False, "points at")
    with tempfile.TemporaryDirectory() as td:
        r = tree(td)
        env = {"ROOT": str(r)}
        before = (r / "AUDIT-CONTEXT.md").read_text(encoding="utf-8")
        edit(r / "routing.yaml", "# pre-release:end\n", "")
        expect("bundle: stamp refuses when a pre-release marker is missing, and writes nothing",
               run(["build-release-bundle.sh", "stamp", "v2099.01", "2099-01-01"], r, env), False, "nothing written")
        results.append(((r / "AUDIT-CONTEXT.md").read_text(encoding="utf-8") == before,
                        "bundle: a refused stamp leaves AUDIT-CONTEXT unstamped"))
    with tempfile.TemporaryDirectory() as td:
        r = tree(td)
        env = {"ROOT": str(r)}
        before = (r / "README.md").read_text(encoding="utf-8")
        edit(r / "README.md", "<!-- pre-release:end -->\n", "")
        expect("bundle: stamp refuses when the README banner marker is missing",
               run(["build-release-bundle.sh", "stamp", "v2099.01", "2099-01-01"], r, env), False, "README.md: expected exactly one")
    with tempfile.TemporaryDirectory() as td:
        r = tree(td)
        env = {"ROOT": str(r), "ALLOW_MISSING": "1"}
        run(["build-release-bundle.sh", "stamp", "v2099.01", "2099-01-01"], r, env)
        olp_p = r / "ONE-LINE-PROMPT.md"
        olp_p.write_text(re.sub(r"(<!-- pre-release:start[^\n]*-->\n).*?(<!-- pre-release:end -->)",
                                r"\1This repo has not cut a release yet.\n\2", olp_p.read_text(encoding="utf-8"), flags=re.S),
                         encoding="utf-8")
        c = commit(r)
        expect("bundle: refuses when pre-release wording survives the stamp, even with ALLOW_MISSING=1",
               run(["build-release-bundle.sh", "bundle", "v2099.01", c], r, env), False, "survives the stamp")
    with tempfile.TemporaryDirectory() as td:
        r1, r2 = tree(td), None
        r2 = Path(td) / "repo2"
        shutil.copytree(r1, r2)
        digests = []
        for rr in (r1, r2):
            env = {"ROOT": str(rr), "ALLOW_MISSING": "1"}
            run(["build-release-bundle.sh", "stamp", "v2099.01", "2099-01-01"], rr, env)
            c = commit(rr)
            run(["build-release-bundle.sh", "bundle", "v2099.01", c], rr, env)
            out = rr / "dist" / "securing-ai-best-practices-v2099.01.md"
            digests.append(hashlib.sha256(out.read_bytes()).hexdigest() if out.is_file() else None)
        results.append((digests[0] is not None and digests[0] == digests[1], "bundle: two builds of the same tree have the same SHA-256"))

    for good, label in results:
        if label in DIRECT:
            print(f"{'ok  ' if good else 'FAIL'} {label}")
    bad = [label for good, label in results if not good]
    print(f"{len(results)} checks, {len(bad)} failed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
