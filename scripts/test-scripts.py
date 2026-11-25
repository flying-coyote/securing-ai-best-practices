#!/usr/bin/env python3
"""
Planted-case tests for the scripts test-checks.py does not cover in these
respects: check-pins.py's name normalization, check-measurement-expiry.py's
refusal of undated or mistyped claims, the probe's tally line,
measure-link-reachability.py's reference links and anchors, the new rules in
check-exclusions.py (undecodable files, hidden characters, secret-shaped
strings, commit messages), and the reducer archive the release bundle step
writes. Every case runs on a temporary tree; nothing in the working tree is
written, and git runs only inside the temporary directories, with a fixed
identity and an isolated config.

Usage: python scripts/test-scripts.py
"""

import hashlib
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
failures: list[str] = []


def check(cond: bool, msg: str, detail: str = "") -> None:
    print(f"{'ok  ' if cond else 'FAIL'} {msg}" + ("" if cond or not detail else f"\n     {detail[-600:]}"))
    if not cond:
        failures.append(msg)


def py(script: str, *args, cwd=None, stdin=None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)], cwd=cwd, input=stdin,
                          capture_output=True, text=True, encoding="utf-8")


def git_env(base: Path) -> dict:
    cfg = base / "gitconfig"
    if not cfg.exists():
        cfg.write_text("[init]\n\tdefaultBranch = main\n[commit]\n\tgpgsign = false\n[tag]\n\tgpgsign = false\n",
                       encoding="utf-8")
    return dict(os.environ, GIT_CONFIG_GLOBAL=str(cfg), GIT_CONFIG_NOSYSTEM="1",
                GIT_AUTHOR_NAME="test", GIT_AUTHOR_EMAIL="test@example.invalid",
                GIT_COMMITTER_NAME="test", GIT_COMMITTER_EMAIL="test@example.invalid",
                GIT_AUTHOR_DATE="2099-01-01T00:00:00Z", GIT_COMMITTER_DATE="2099-01-01T00:00:00Z")


def git(repo: Path, env: dict, *args) -> str:
    return subprocess.run(["git", "-c", "core.hooksPath=/dev/null", *args], cwd=repo, env=env, check=True,
                          capture_output=True, text=True).stdout.strip()


def write(root: Path, rel: str, text) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(text, bytes):
        p.write_bytes(text)
    else:
        p.write_text(text, encoding="utf-8")


def test_check_pins() -> None:
    with tempfile.TemporaryDirectory() as td:
        r = Path(td)
        write(r, "analysis/revalidation-and-pins.md", "---\npins:\n  - \"MITRE ATLAS v2026.10\"\n"
              "  - \"CoSAI secure-ai-tooling 622605a1\"\n  - \"CISA KEV catalog 2026.11.09\"\n  - \"OCSF 1.9.0\"\n---\n")
        write(r, "analysis/a.md", "---\npins:\n  - \"MITRE ATLAS v2026.06 (released 2026-06-30)\"\n---\n")
        write(r, "analysis/b.md", "---\npins:\n  - \"CoSAI secure-ai-tooling risk-map @ deadbeef (main)\"\n---\n")
        write(r, "analysis/c.md", "---\npins:\n  - \"CoSAI secure-ai-tooling risk-map @ "
              "622605a13fafaa2784acbdbe3f8d23ee22da4be7 (main, 2026-10-21)\"\n"
              "  - \"CISA KEV catalogVersion 2026.11.09\"\n  - \"MITRE ATLAS v2026.10 (released 2026-10-28)\"\n---\n")
        write(r, "analysis/d.md", "---\npins:\n  - \"CISA KEV catalogVersion 2026.10.01\"\n"
              "  - \"OCSF main 1.10.0-dev at commit d1cbd61 for ai_capability (not in a release; the repo pin is "
              "OCSF 1.9.0)\"\n  - \"Keycloak 26.8.1 (lab run T7)\"\n---\n")
        p = py("check-pins.py", "--root", r)
        out = p.stdout
        check(p.returncode == 0, "check-pins: behind docs never fail the run", out + p.stderr)
        check("docs pins behind: 3" in out, "check-pins: a parenthetical, a 'risk-map @' and a 'catalogVersion' pin "
              "are compared, and three behind are counted", out)
        check("a.md: 'MITRE ATLAS' at v2026.06" in out and "b.md: 'CoSAI secure-ai-tooling' at deadbeef" in out
              and "d.md: 'CISA KEV catalog' at 2026.10.01" in out, "check-pins: each behind pin is named", out)
        check("c.md" not in out.split("doc-local")[0], "check-pins: a full SHA matches its abbreviation and equal "
              "versions are not behind", out)
        check("doc-local pins (no canon name): 2" in out and "OCSF main" in out and "Keycloak" in out,
              "check-pins: unmatched pins (the OCSF dev pin, a lab tool) are counted and listed, not behind", out)


def test_expiry() -> None:
    cases = [
        ("dated", "  - claim: \"x\"\n    source: \"s\"\n    revalidate: 2099-01-01\n", 0),
        ("undated", "  - claim: \"x\"\n    source: \"s\"\n", 1),
        ("not a list", "  claim: \"x\"\n", 1),
        ("a claim that is a string", "  - \"just text\"\n", 1),
        ("never", "  - claim: \"x\"\n    source: \"s\"\n    revalidate: never\n", 0),
    ]
    for label, block, want in cases:
        with tempfile.TemporaryDirectory() as td:
            r = Path(td)
            write(r, "analysis/doc.md", "---\nstatus: EMERGING\nmeasurement-claims:\n" + block
                  + "---\n\n# Doc \u2014 with non-ASCII text, caf\u00e9\n")
            p = py("check-measurement-expiry.py", "--patterns-dir", r / "analysis", cwd=r)
            check(p.returncode == want, f"expiry: {label} claim exits {want}", p.stdout[-400:])
            if want:
                q = py("check-measurement-expiry.py", "--patterns-dir", r / "analysis", "--changed-files",
                       r / "analysis" / "doc.md", cwd=r)
                check(q.returncode == 1, f"expiry: {label} claim fails when its doc is in the change", q.stdout[-300:])


def test_probe_tally() -> None:
    spec = importlib.util.spec_from_file_location("probe", SCRIPTS / "probe-source-accessibility.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    ok = {"page_state": "ok", "moved": False, "checks_moved": True}
    api_failed = {"page_state": "ok", "moved": None, "checks_moved": True}
    page_only = {"page_state": "ok", "moved": None, "checks_moved": False}
    refused = {"page_state": "refused", "moved": None, "checks_moved": False}
    not_pinned = {"page_state": "not-pinned", "moved": None}
    line = mod.tally_line([ok, page_only])
    check(line.endswith("broken=0 refused=0 moved=0 unknown=0"), "probe: a clean run tallies zero", line)
    line = mod.tally_line([ok, api_failed])
    check("unknown=1" in line, "probe: a planted API failure counts as unknown, which keeps the issue open", line)
    line = mod.tally_line([ok, refused])
    check("refused=1" in line, "probe: a planted 403 counts as refused, which keeps the issue open", line)
    line = mod.tally_line([not_pinned])
    check("unknown=1" in line, "probe: a probe with no pin counts as unknown", line)
    wf = (ROOT / ".github" / "workflows" / "checks.yml").read_text(encoding="utf-8")
    check("fields('source-urls-probed')" in wf and "'unknown'" in wf and "expired-claims" in wf,
          "probe: the standing issue reads both tally lines by name, unknown included, and the expiry tally")


def test_links() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        r = base / "repo"
        r.mkdir()
        env = git_env(base)
        write(r, "README.md", "# Top\n\n[ok](docs/b.md#real-heading) [ok2](#local-part) [bad](docs/b.md#missing)\n"
              "[gone][ref1] [anchor][ref2]\n\n## Local part\n\n[ref1]: docs/c.md\n[ref2]: docs/b.md#missing-two\n"
              "[ref3]: docs/b.md#second-1\n[ref4]: docs/b.md#the-one-thing\n[ref5]: docs/b.md#snake_case-name\n\n"
              "A note.[^1]\n\n[^1]: See the table above.\n")
        write(r, "docs/b.md", "# B\n\n## Real heading\n\n## Second\n\n## Second\n\n## The _one_ **thing**\n\n"
              "## snake_case name\n\n```\n## Not a heading\n```\n"
              "[x](#not-a-heading)\n")
        git(r, env, "init", "-q")
        git(r, env, "add", "-A")
        git(r, env, "commit", "-q", "-m", "t")
        p = py("measure-link-reachability.py", "--root", r, "--links")
        row = re.search(r"^dangling\s+(\d+)", p.stdout, re.M)
        check(row is not None and row.group(1) == "4", "links: a missing anchor, a missing reference target, a "
              "missing reference anchor and a heading inside a fence count as dangling (4)", p.stdout)
        check("#missing (no such heading)" in p.stdout and "docs/c.md" in p.stdout and "#missing-two" in p.stdout,
              "links: each is listed in the detail", p.stdout)
        check("#second-1" not in p.stdout and "#local-part" not in p.stdout and "#real-heading" not in p.stdout
              and "the-one-thing" not in p.stdout and "snake_case" not in p.stdout and "See" not in p.stdout,
              "links: a heading, a repeated heading's -1 slug, a same-file anchor, a heading with emphasis, a "
              "snake_case heading resolve, and a footnote definition is not a link", p.stdout)


def test_exclusions() -> None:
    home = "/" + "home" + "/"
    secret = "AKIA" + "ABCDEFGHIJKLMNOP"
    with tempfile.TemporaryDirectory() as td:
        r = Path(td)
        write(r, "ONE-LINE-PROMPT.md", "## Fetch mode\nnot legal advice\n## Offline mode\nnot legal advice\n"
              "## Structured Output Format\nnot legal advice\n")
        write(r, "README.md", "## The one-line review\nnot legal advice\n")
        p = py("check-exclusions.py", "--root", r)
        check(p.returncode == 0, "exclusions: the minimal clean tree passes", p.stdout)
        write(r, "notes.cff", b"title: caf\xe9\n")
        write(r, "a.md", "text\u200bwith a zero-width space\n")
        write(r, "b.md", "line one\u2028line two\n")
        write(r, "c.yaml", f"key: {secret}\n")
        write(r, "scripts/reducers/fixtures/x/input.csv", "name\nChatGPT\U000E0041\n")
        write(r, "d.toml", f"path = \"{home}someone/x\"\n")
        p = py("check-exclusions.py", "--root", r)
        out = p.stdout
        check(p.returncode == 1, "exclusions: planted defects fail the run", out)
        check("undecodable notes.cff" in out, "exclusions: an undecodable file fails instead of being skipped", out)
        check("hidden-char a.md:1" in out and "U+200B" in out, "exclusions: a zero-width space is found", out)
        check("hidden-char b.md:1" in out, "exclusions: a U+2028 line separator is found, not split on", out)
        check("secret-shaped c.yaml:1" in out and secret not in out, "exclusions: a secret-shaped string is "
              "found and not printed", out)
        check("scripts/reducers/fixtures" not in out, "exclusions: the reducer fixtures are exempt", out)
        check("local-path d.toml:1" in out, "exclusions: a file with an unlisted extension is scanned", out)
    msg = f"Add notes\n\nWorking copy at {home}someone/project\n"
    p = py("check-exclusions.py", "--messages", "-", stdin=msg)
    check(p.returncode == 1 and "local-path commit messages:3" in p.stdout,
          "exclusions: a local path in a commit message fails", p.stdout)
    p = py("check-exclusions.py", "--messages", "-", stdin="Fix a typo\n\nThe gate writes /" + "tmp/links.txt.\n")
    check(p.returncode == 0, "exclusions: a clean commit message passes, a temporary path in it included", p.stdout)


def test_bundle_reducer_archive() -> None:
    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split("\n")
    digests = []
    for n in (1, 2):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            r = base / "repo"
            for rel in tracked:
                src = ROOT / rel
                if rel and src.is_file():
                    (r / rel).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, r / rel)
            env = git_env(base)
            env.update(ROOT=str(r), ALLOW_MISSING="1")
            stamp = subprocess.run(["bash", str(r / "scripts" / "build-release-bundle.sh"), "stamp", "v2099.01",
                                    "2099-01-01"], cwd=r, env=env, capture_output=True, text=True)
            if stamp.returncode != 0:
                check(False, "bundle: stamp ran on a copy of the tracked tree", stamp.stdout + stamp.stderr)
                return
            git(r, env, "init", "-q")
            git(r, env, "add", "-A")
            git(r, env, "commit", "-q", "-m", "t")
            sha = git(r, env, "rev-parse", "HEAD")
            p = subprocess.run(["bash", str(r / "scripts" / "build-release-bundle.sh"), "bundle", "v2099.01", sha],
                               cwd=r, env=env, capture_output=True, text=True)
            tar = r / "dist" / "securing-ai-best-practices-v2099.01-reducers.tar"
            if p.returncode != 0 or not tar.is_file():
                check(False, "bundle: builds with a reducer archive", p.stdout + p.stderr)
                return
            d = hashlib.sha256(tar.read_bytes()).hexdigest()
            digests.append(d)
            rel = (r / "RELEASES.md").read_text(encoding="utf-8")
            names = subprocess.run(["tar", "-tf", str(tar)], capture_output=True, text=True).stdout.split()
            if n == 1:
                check(f"reducers sha256: {d}" in p.stdout and f"SHA-256 `{d}`" in rel,
                      "bundle: the reducer archive's SHA-256 is printed and written into the RELEASES.md row",
                      p.stdout)
                check("securing-ai-reducers-v2099.01/scripts/reducers/mcp_config.py" in names
                      and not any("__pycache__" in x for x in names),
                      "bundle: the archive holds the committed reducers and nothing untracked", " ".join(names[:10]))
    check(len(digests) == 2 and digests[0] == digests[1], "bundle: two builds of the same commit give the same "
          "reducer archive SHA-256", str(digests))


def main() -> int:
    test_check_pins()
    test_expiry()
    test_probe_tally()
    test_links()
    test_exclusions()
    test_bundle_reducer_archive()
    print(f"{'PASS' if not failures else str(len(failures)) + ' failure(s)'}: test-scripts")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
