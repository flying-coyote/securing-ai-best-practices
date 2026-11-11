#!/usr/bin/env python3
"""
Probe the release pages of the upstreams the pins doc names, and report which
ones moved past their pin.

The pinned versions are read from the `pins:` list in the frontmatter of
analysis/revalidation-and-pins.md, so this script carries no version of its own
and never goes stale against that document. For each upstream it knows how to
probe, it fetches the pinned release page (is it still there?) and, where the
upstream publishes releases through the GitHub API, the newest release or the
newest commit that touches the pinned file (has it moved?):

  MITRE ATLAS              pinned release page; newest atlas-data release tag
  OCSF                     pinned release page; newest ocsf-schema release tag
  MCP specification        the pinned revision's specification page
  CoSAI secure-ai-tooling  repository page; whether risk-map/yaml/components.yaml
                           changed between the pinned commit and main
  OWASP Top 10 for LLM Applications, OWASP Top 10 for Agentic Applications
                           the 2026 edition pages

A page answers in one of three ways: ok (2xx or 3xx), refused (401, 403 or 429,
which usually means a bot filter rather than a missing page, so it is a task to
check by hand and not a broken source), or broken (anything else, including no
answer at all). A moved upstream is a revalidation task under the trigger table
in the pins doc, never a failure.

So the run never fails on what it finds. It exits 0 with a report, and exits 2
only when it cannot read the pins doc at all, because a probe that reports
clean when it read nothing manufactures the evidence that nothing moved.

Given --current FILE it also writes the newest-known versions as a YAML
mapping, in the form `scripts/check-pins.py --current FILE` reads, for the
upstreams whose newest version it could establish. KEV is never written there
(the pins doc explains why), and the CoSAI entry is written only when the
component file itself changed, since commits that leave it alone do not
reopen anything.

Network and API access: standard library only. GITHUB_TOKEN, when set, is sent
to api.github.com to lift the unauthenticated rate limit; it is never printed.

Usage:
    python scripts/probe-source-accessibility.py [--root DIR] [--current FILE] [--json]
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

import yaml

PINS_DOC = "analysis/revalidation-and-pins.md"
UA = "Mozilla/5.0 (compatible; securing-ai-best-practices source-accessibility probe)"
TIMEOUT = 15

# name in pins: -> how to probe it. `page` takes {ver}; `release_repo` reports
# the newest GitHub release tag; `commit_path` reports whether a file changed
# between the pinned commit and the default branch.
PROBES = {
    "MITRE ATLAS": {
        "page": "https://github.com/mitre-atlas/atlas-data/releases/tag/{ver}",
        "release_repo": "mitre-atlas/atlas-data",
    },
    "OCSF": {
        "page": "https://github.com/ocsf/ocsf-schema/releases/tag/{ver}",
        "release_repo": "ocsf/ocsf-schema",
    },
    "MCP specification": {
        "page": "https://modelcontextprotocol.io/specification/{ver}",
    },
    "CoSAI secure-ai-tooling": {
        "page": "https://github.com/cosai-oasis/secure-ai-tooling",
        "commit_path": ("cosai-oasis/secure-ai-tooling", "main", "risk-map/yaml/components.yaml"),
    },
    "OWASP Top 10 for LLM Applications": {
        "page": "https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/",
    },
    "OWASP Top 10 for Agentic Applications": {
        "page": "https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/",
    },
}


def frontmatter(path: Path) -> dict:
    m = re.match(r"^---\n(.*?)\n---\n", path.read_text(encoding="utf-8"), re.S)
    return (yaml.safe_load(m.group(1)) or {}) if m else {}


def split_pin(pin: str) -> tuple[str, str | None]:
    """Same rule as check-pins.py: the version is the last word if it has a digit."""
    parts = str(pin).strip().split()
    if len(parts) >= 2 and re.search(r"\d", parts[-1]):
        return " ".join(parts[:-1]), parts[-1]
    return str(pin).strip(), None


def http_status(url: str) -> int:
    req = urllib.request.Request(url, headers={"User-Agent": UA}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


def classify(code: int) -> str:
    if 200 <= code < 400:
        return "ok"
    if code in (401, 403, 429, 999):
        return "refused"
    return "broken"


def gh_api(path: str):
    headers = {"User-Agent": UA, "Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"https://api.github.com/{path}", headers=headers)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.load(r)


def same_form(newest: str, pinned: str) -> str:
    """Write the newest version in the pin's own form ('v1.9.0' -> '1.9.0' when
    the pin has no leading v), so check-pins compares like with like."""
    if pinned.startswith("v") and not newest.startswith("v"):
        return "v" + newest
    if not pinned.startswith("v") and newest.startswith("v") and newest[1:2].isdigit():
        return newest[1:]
    return newest


def probe(name: str, ver: str, spec: dict) -> dict:
    row = {"name": name, "pinned": ver, "page": spec["page"].format(ver=ver)}
    code = http_status(row["page"])
    row["http"] = code
    row["page_state"] = classify(code)
    row["newest"] = None
    row["moved"] = None
    row["note"] = ""
    try:
        if "release_repo" in spec:
            tag = gh_api(f"repos/{spec['release_repo']}/releases/latest")["tag_name"]
            row["newest"] = same_form(tag, ver)
            row["moved"] = row["newest"] != ver
        elif "commit_path" in spec:
            repo, branch, path = spec["commit_path"]
            cmp = gh_api(f"repos/{repo}/compare/{ver}...{branch}")
            files = [f.get("filename") for f in cmp.get("files") or []]
            touched = path in files
            head = (cmp.get("commits") or [{}])[-1].get("sha", "")[: len(ver)]
            row["moved"] = touched
            row["note"] = f"{cmp.get('ahead_by', 0)} commit(s) on {branch} since the pin; {path} {'changed' if touched else 'unchanged'}"
            if len(files) >= 300 and not touched:
                row["note"] += " (compare truncated at 300 files, check by hand)"
                row["moved"] = None
            if touched and head:
                row["newest"] = head
    except Exception as e:  # report, never hide, an API failure
        row["note"] = f"API probe failed: {type(e).__name__}"
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--current", help="write newest-known versions here, for check-pins.py --current")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--sources", action="store_true",
                    help="also probe every external URL in SOURCES.md and list the refused and broken ones")
    args = ap.parse_args()

    pins_doc = Path(args.root) / PINS_DOC
    try:
        pins = frontmatter(pins_doc).get("pins") or []
    except Exception as e:
        print(f"ERROR: cannot read {PINS_DOC}: {type(e).__name__}", file=sys.stderr)
        return 2
    canon = dict(split_pin(p) for p in pins)
    if not canon:
        print(f"ERROR: no pins found in {PINS_DOC}; refusing to report a clean probe", file=sys.stderr)
        return 2

    rows = []
    for name, spec in PROBES.items():
        ver = canon.get(name)
        if ver is None:
            rows.append({"name": name, "pinned": None, "page": "", "http": None,
                         "page_state": "not-pinned", "newest": None, "moved": None,
                         "note": f"no versioned pin named '{name}' in {PINS_DOC}"})
            continue
        rows.append(probe(name, ver, spec))

    if args.current:
        newest = {r["name"]: r["newest"] for r in rows if r["newest"]}
        Path(args.current).write_text(yaml.safe_dump(newest, sort_keys=True), encoding="utf-8")

    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        print("| Upstream | Pinned | Page | Newest known | Moved past pin | Note |")
        print("|---|---|---|---|---|---|")
        for r in rows:
            page = f"{r['page_state']} ({r['http']})" if r["http"] is not None else r["page_state"]
            moved = {True: "yes", False: "no", None: "unknown"}[r["moved"]]
            print(f"| {r['name']} | {r['pinned'] or ''} | {page} | {r['newest'] or ''} | {moved} | {r['note']} |")
        broken = sum(r["page_state"] == "broken" for r in rows)
        refused = sum(r["page_state"] == "refused" for r in rows)
        moved = sum(r["moved"] is True for r in rows)
        print(f"\nsources-probed={len(rows)} broken={broken} refused={refused} moved={moved}")
    if args.sources and not args.json:
        sources_report(Path(args.root) / "SOURCES.md")
    return 0


def sources_report(path: Path) -> None:
    """List SOURCES.md URLs that answer refused or broken. The CI link checker
    counts 401, 403 and 999 as alive so a bot filter never turns a pull request
    red, which means a source that refuses every fetch would otherwise never be
    seen; this table is where the weekly review sees it, as a task to check by
    hand or move to the Unverified quarantine. It never fails the run."""
    import concurrent.futures, re as _re
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"\nSOURCES.md not read ({type(e).__name__}); source-URL probe skipped")
        return
    urls = sorted(set(u.rstrip(").,;") for u in _re.findall(r"https?://[^\s|<>`\]]+", text)))
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        codes = dict(zip(urls, ex.map(http_status, urls)))
    bad = [(u, c, classify(c)) for u, c in codes.items() if classify(c) != "ok"]
    print("\n| SOURCES.md URL | Answer | State |")
    print("|---|---|---|")
    for u, c, s in sorted(bad, key=lambda x: (x[2], x[0])):
        print(f"| {u} | {c or 'no answer'} | {s} |")
    print(f"\nsource-urls-probed={len(urls)} refused={sum(s == 'refused' for _, _, s in bad)} "
          f"broken={sum(s == 'broken' for _, _, s in bad)}")


if __name__ == "__main__":
    sys.exit(main())
