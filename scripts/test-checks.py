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
block in analysis/decision-sequence.md), check-exclusions.py, check-pins.py and
build-release-bundle.sh (including the stamp step retiring every pre-release
statement and the bundle refusing a missing routed doc).

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
        "CONTRIBUTING.md", "analysis", "fixtures"]
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
          "bundle: two builds of the same tree have the same SHA-256"}


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
        text = re.sub(r"\(release v\d{4}\.\d{2}([;,])", r"(release <vYYYY.MM>\1", text)
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
        edit(r / "routing.yaml", "then factor sum, highest first,", "then the backing doc's evidence tier, then factor sum, highest first,")
        expect("render --check fails when routing.yaml's ordering rule changes", run(["render-audit-context.py", "--root", str(r), "--check"], r), False, "ordering rule is stale")
        expect("routing coverage fails when the ordering rule drifts", run(["check-routing-coverage.py", "--root", str(r)], r), False, "stale")
        expect("render rewrites the ordering rule", run(["render-audit-context.py", "--root", str(r)], r), True)
        results.append(("then the backing doc's evidence tier, then factor sum" in (r / "AUDIT-CONTEXT.md").read_text(encoding="utf-8"),
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
    results.append((in_order(ordering, ["Within a band", "sequence group", "factor sum, highest first", "`#`"])
                    and in_order(mapper, ["band", "sequence group", "factor sum descending", "routing.yaml row order"])
                    and bool(sort_key) and in_order(sort_key.group(1), ["BAND_RANK", "sequence-group", "factor-sum", "t[0]"])
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
               run(["check-pins.py", "--root", str(r)], r), True, "docs pins behind: 1")
        cur = r / "current.yaml"
        cur.write_text("MITRE ATLAS: v2026.11\n", encoding="utf-8")
        expect("pins: the pins doc behind the newest known release fails",
               run(["check-pins.py", "--root", str(r), "--current", str(cur)], r), False, "newest known")

    # build-release-bundle.sh
    with tempfile.TemporaryDirectory() as td:
        r = tree(td)
        env = {"ROOT": str(r)}
        expect("bundle: refuses to build before the stamp step",
               run(["build-release-bundle.sh", "bundle", "v2099.01", sha], r, dict(env, ALLOW_MISSING="1")), False, "not stamped")
        expect("bundle: stamp writes the tag and date", run(["build-release-bundle.sh", "stamp", "v2099.01", "2099-01-01"], r, env), True)
        ac = (r / "AUDIT-CONTEXT.md").read_text(encoding="utf-8")
        results.append(("Release: v2099.01. Date: 2099-01-01." in ac, "bundle: AUDIT-CONTEXT header stamped"))
        olp = (r / "ONE-LINE-PROMPT.md").read_text(encoding="utf-8")
        ry = (r / "routing.yaml").read_text(encoding="utf-8")
        pins = (r / "analysis" / "revalidation-and-pins.md").read_text(encoding="utf-8")
        readme = (r / "README.md").read_text(encoding="utf-8")
        results.append(("> Pre-release." not in ac and "should stop and say the repo is unreleased" not in ac
                        and "has not cut a release yet" not in olp and "release v2099.01, stamped 2099-01-01" in olp
                        and "State: pre-release" not in ry and "# State: release v2099.01, stamped 2099-01-01." in ry
                        and "release: v2099.01\n" in ry
                        and "Release: unreleased" not in pins and "Release: v2099.01; pins last verified" in pins
                        and "Status: pre-release" not in readme and "> Status: release v2099.01, stamped 2099-01-01." in readme
                        and "<!-- pre-release:start" in readme and "<!-- pre-release:end -->" in readme,
                        "bundle: stamp retires the banner, the prompt paragraph, the routing comment, the README banner and the pins Release line"))
        held = always_fetch(r)[0]
        body = (r / held).read_bytes()
        unwrite(r, held)
        expect("bundle: refuses to build while Always Fetch docs are missing",
               run(["build-release-bundle.sh", "bundle", "v2099.01", sha], r, env), False, "Always Fetch docs missing")
        (r / held).write_bytes(body)
        fill_routed(r)
        gone = unwrite(r, routed_docs(r)[0])
        expect("bundle: refuses to build while a routed doc is missing",
               run(["build-release-bundle.sh", "bundle", "v2099.01", sha], r, env), False, f"routed docs missing (1)")
        expect("bundle: names the missing routed doc", run(["build-release-bundle.sh", "bundle", "v2099.01", sha], r, env), False, gone)
        p = run(["build-release-bundle.sh", "bundle", "v2099.01", sha], r, dict(env, ALLOW_MISSING="1"))
        expect("bundle: builds with ALLOW_MISSING=1", p, True)
        out = r / "dist" / "securing-ai-best-practices-v2099.01.md"
        digest = hashlib.sha256(out.read_bytes()).hexdigest() if out.is_file() else ""
        rel = (r / "RELEASES.md").read_text(encoding="utf-8")
        results.append((bool(digest) and digest in rel and sha in rel and digest in p.stdout,
                        "bundle: RELEASES.md row carries the commit and the bundle's real SHA-256"))
        results.append((bool(re.search(r"^===== FILE: routing.yaml =====$", out.read_text(encoding="utf-8"), re.M)) if out.is_file() else False,
                        "bundle: contains routing.yaml under its file header"))
        expect("bundle: refuses a second row for the same tag",
               run(["build-release-bundle.sh", "bundle", "v2099.01", sha], r, dict(env, ALLOW_MISSING="1")), False, "already has a row")
    with tempfile.TemporaryDirectory() as td:
        r = tree(td)
        env = {"ROOT": str(r)}
        fill_routed(r)
        run(["build-release-bundle.sh", "stamp", "v2099.01", "2099-01-01"], r, env)
        expect("bundle: builds without ALLOW_MISSING once every routed doc exists",
               run(["build-release-bundle.sh", "bundle", "v2099.01", sha], r, env), True, "sha256:")
        out = (r / "dist" / "securing-ai-best-practices-v2099.01.md")
        text = out.read_text(encoding="utf-8") if out.is_file() else ""
        results.append((all(f"===== FILE: {d} =====" in text for d in routed_docs(r)),
                        "bundle: holds every routed doc"))
        results.append(("pre-release:start" in text and "has not cut a release yet" not in text
                        and "Release: unreleased" not in text, "bundle: carries no pre-release wording"))
        expect("bundle: a second stamp for the next release finds the markers again",
               run(["build-release-bundle.sh", "stamp", "v2027.01", "2027-01-05"], r, env), True, "stamped v2027.01")
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
        unstamped = (r / "ONE-LINE-PROMPT.md").read_text(encoding="utf-8")
        run(["build-release-bundle.sh", "stamp", "v2099.01", "2099-01-01"], r, env)
        (r / "ONE-LINE-PROMPT.md").write_text(unstamped, encoding="utf-8")
        expect("bundle: refuses when pre-release wording survives the stamp, even with ALLOW_MISSING=1",
               run(["build-release-bundle.sh", "bundle", "v2099.01", sha], r, env), False, "survives the stamp")
    with tempfile.TemporaryDirectory() as td:
        r1, r2 = tree(td), None
        r2 = Path(td) / "repo2"
        shutil.copytree(r1, r2)
        digests = []
        for rr in (r1, r2):
            env = {"ROOT": str(rr), "ALLOW_MISSING": "1"}
            run(["build-release-bundle.sh", "stamp", "v2099.01", "2099-01-01"], rr, env)
            run(["build-release-bundle.sh", "bundle", "v2099.01", sha], rr, env)
            digests.append(hashlib.sha256((rr / "dist" / "securing-ai-best-practices-v2099.01.md").read_bytes()).hexdigest())
        results.append((digests[0] == digests[1], "bundle: two builds of the same tree have the same SHA-256"))

    for good, label in results:
        if label in DIRECT:
            print(f"{'ok  ' if good else 'FAIL'} {label}")
    bad = [label for good, label in results if not good]
    print(f"{len(results)} checks, {len(bad)} failed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
