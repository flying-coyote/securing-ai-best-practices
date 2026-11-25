#!/usr/bin/env python3
"""
Test the employer and identifier denylist pre-push hook against a fake denylist.

Every case builds a throwaway git repository in a temporary directory, writes a
temporary denylist holding one made-up term, and runs
scripts/hooks/pre-push-employer-denylist.sh the way git runs a pre-push hook
(ref lines on standard input, the repository as the working directory). The
subprocess environment is built from scratch, so a real SECURING_AI_DENYLIST
on the machine running the test is never inherited, read or printed, and git
runs with an isolated global config so nothing outside the temporary directory
is touched.

It checks the three exit codes: 2 for a setup error (variable unset, file
missing, file with no terms), 0 for a clean push, and 1 when the term appears
in an added line, a commit message, an author name, a committer email, a ref
name, a renamed path, a binary file's contents, beside a non-UTF-8 byte, or
when the denylist's first line carries a byte-order mark; and that
--scan-paths finds a term in a file holding a NUL byte.

Usage: python scripts/test-hooks.py   (HOOK=path overrides the hook under test)
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOK = Path(os.environ.get("HOOK") or ROOT / "scripts" / "hooks" / "pre-push-employer-denylist.sh")
TERM = "zq" + "plantedterm" + "xv"   # assembled so this file never holds the literal
ZERO = "0" * 40

failures: list[str] = []


def check(cond: bool, msg: str) -> None:
    print(f"{'ok  ' if cond else 'FAIL'} {msg}")
    if not cond:
        failures.append(msg)


class Repo:
    def __init__(self, base: Path):
        self.dir = base / "repo"
        self.dir.mkdir()
        home = base / "home"
        home.mkdir()
        gitconfig = base / "gitconfig"
        gitconfig.write_text("[user]\n\tname = Test Author\n\temail = author@example.invalid\n"
                             "[init]\n\tdefaultBranch = main\n[commit]\n\tgpgsign = false\n", encoding="utf-8")
        self.env = {"PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": str(home), "LC_ALL": "C.UTF-8",
                    "GIT_CONFIG_GLOBAL": str(gitconfig), "GIT_CONFIG_NOSYSTEM": "1"}
        self.git("init", "-q")
        self.write("README.txt", "clean\n")
        self.base = self.commit("base")

    def git(self, *args, env_extra=None) -> str:
        env = dict(self.env, **(env_extra or {}))
        return subprocess.run(["git", *args], cwd=self.dir, env=env, check=True,
                              capture_output=True, text=True).stdout.strip()

    def write(self, rel: str, data) -> None:
        p = self.dir / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        (p.write_bytes if isinstance(data, bytes) else lambda d: p.write_text(d, encoding="utf-8"))(data)

    def commit(self, msg: str, env_extra=None) -> str:
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg, env_extra=env_extra)
        return self.git("rev-parse", "HEAD")

    def hook(self, denylist: Path | None, stdin: str, *args, extra=None) -> subprocess.CompletedProcess:
        env = dict(self.env)
        if denylist is not None:
            env["SECURING_AI_DENYLIST"] = str(denylist)
        env.update(extra or {})
        return subprocess.run(["bash", str(HOOK), *args], cwd=self.dir, env=env, input=stdin,
                              capture_output=True, text=True)


def push_line(local_sha: str, remote_sha: str, local_ref="refs/heads/main", remote_ref="refs/heads/main") -> str:
    return f"{local_ref} {local_sha} {remote_ref} {remote_sha}\n"


def case(label: str, setup, want: int, deny_text: str | bytes | None = None) -> None:
    with tempfile.TemporaryDirectory(prefix="hook-test-") as td:
        td = Path(td)
        repo = Repo(td)
        deny = td / "denylist.txt"
        text = deny_text if deny_text is not None else f"# a comment\n\n  {TERM}  \n"
        (deny.write_bytes if isinstance(text, bytes) else lambda d: deny.write_text(d, encoding="utf-8"))(text)
        stdin, args, denylist, extra = setup(repo, deny)
        p = repo.hook(denylist, stdin, *args, extra=extra)
        check(p.returncode == want, f"{label}: exit {p.returncode}, want {want}"
              + ("" if p.returncode == want else f" (stderr: {p.stderr.strip()[-300:]})"))


def main() -> int:
    if not HOOK.is_file():
        print(f"FAIL hook not found at {HOOK}")
        return 1

    # setup errors: exit 2
    case("variable unset", lambda r, d: (push_line(r.base, ZERO), [], None, None), 2)
    case("denylist file missing", lambda r, d: (push_line(r.base, ZERO), [], d.parent / "absent.txt", None), 2)
    case("denylist holds only comments", lambda r, d: (push_line(r.base, ZERO), [], d, None), 2,
         deny_text="# nothing here\n\n")

    # clean: exit 0
    case("clean new branch", lambda r, d: (push_line(r.base, ZERO), [], d, None), 0)

    def clean_range(r, d):
        r.write("notes.txt", "nothing to see\n")
        return push_line(r.commit("ordinary change"), r.base), [], d, None
    case("clean range", clean_range, 0)
    case("branch deletion pushes nothing", lambda r, d: (push_line(ZERO, r.base), [], d, None), 0)

    # matches: exit 1
    def added_line(r, d):
        r.write("doc.md", f"text naming {TERM.upper()} here\n")
        return push_line(r.commit("add doc"), r.base), [], d, None
    case("term in an added line (case-insensitive)", added_line, 1)

    def message(r, d):
        r.write("doc.md", "fine\n")
        return push_line(r.commit(f"mention {TERM}"), r.base), [], d, None
    case("term in a commit message", message, 1)

    def author(r, d):
        r.write("doc.md", "fine\n")
        sha = r.commit("ordinary", env_extra={"GIT_AUTHOR_NAME": f"Someone {TERM}"})
        return push_line(sha, r.base), [], d, None
    case("term in the author name", author, 1)

    def committer(r, d):
        r.write("doc.md", "fine\n")
        sha = r.commit("ordinary", env_extra={"GIT_COMMITTER_EMAIL": f"me@{TERM}.example"})
        return push_line(sha, r.base), [], d, None
    case("term in the committer email", committer, 1)

    def ref_name(r, d):
        r.write("doc.md", "fine\n")
        sha = r.commit("ordinary")
        return push_line(sha, r.base, f"refs/heads/{TERM}-work", f"refs/heads/{TERM}-work"), [], d, None
    case("term in a ref name", ref_name, 1)

    def rename(r, d):
        r.git("mv", "README.txt", f"{TERM}-readme.txt")
        return push_line(r.commit("move"), r.base), [], d, None
    case("term in a pure rename's new path", rename, 1)

    def binary(r, d):
        r.write("blob.bin", b"\x00\x01\x02 header " + TERM.encode() + b" \x00\xff tail")
        return push_line(r.commit("add binary"), r.base), [], d, None
    case("term inside a binary file", binary, 1)

    def non_utf8(r, d):
        r.write("latin.txt", b"caf\xe9 \xff " + TERM.encode() + b"\n")
        return push_line(r.commit("add latin-1 text"), r.base), [], d, None
    case("term beside a non-UTF-8 byte", non_utf8, 1)

    def tag_message(r, d):
        r.git("tag", "-a", "v1", "-m", f"release {TERM}")
        return push_line(r.git("rev-parse", "v1"), ZERO, "refs/tags/v1", "refs/tags/v1"), [], d, None
    case("term in an annotated tag's message", tag_message, 1)

    case("byte-order mark on the denylist's first line", added_line, 1,
         deny_text=b"\xef\xbb\xbf" + TERM.encode() + b"\r\n# trailing comment\r\n")

    def scan_nul(r, d):
        r.write("draft.bin", b"x\x00y " + TERM.encode() + b"\n")
        return "", ["--scan-paths", "draft.bin"], d, None
    case("--scan-paths finds a term in a file with a NUL byte", scan_nul, 1)

    def skipped(r, d):
        r.write("doc.md", f"{TERM}\n")
        return push_line(r.commit("x"), r.base), [], d, {"SECURING_AI_DENYLIST_SKIP": "1"}
    case("SECURING_AI_DENYLIST_SKIP=1 bypasses and says so", skipped, 0)

    print(f"{'PASS' if not failures else str(len(failures)) + ' failure(s)'}: denylist hook")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
