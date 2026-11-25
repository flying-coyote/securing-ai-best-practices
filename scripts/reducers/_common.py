"""Shared plumbing for the reducers: read an export, sanitize it, print only a
closed vocabulary of names with integer, boolean or `not-checked` values.

The guarantee the reducers make is structural rather than a matter of care in
each one: `emit` refuses to print any name the calling reducer did not declare,
and any value that is not an integer of zero or more, true, false or the string
`not-checked`, so a reducer cannot echo an app name, a hostname or a user even
by mistake. If a reducer tries, it exits with an error and prints nothing on
standard output. Standard library only, so a practitioner can run the reducers
on any machine with Python 3.11 or later and no packages installed.
"""

from __future__ import annotations

import csv
import io
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from text_sanitize import sanitize_record  # noqa: E402

NOT_CHECKED = "not-checked"


def _norm(h: str) -> str:
    return re.sub(r"[^a-z0-9]", "", h.lower())


class InputError(Exception):
    """An input the reducer cannot read as a complete export. Its message is a
    fixed sentence written by the reducer, never text from the input or a path."""


# Keys a paginated API response uses to point at the next page. A page that
# carries one is part of a longer list, so counting it would undercount.
NEXT_PAGE_KEYS = {"odatanextlink", "nextlink", "nextpagetoken", "nextpage", "next", "nextcursor"}


def _strip_jsonc(raw: str) -> str:
    """Remove // and /* */ comments outside strings, and a trailing comma before
    a closing bracket or brace (VS Code's mcp.json and settings files are JSONC)."""
    out, i, n = [], 0, len(raw)
    while i < n:
        c = raw[i]
        if c == '"':
            j = i + 1
            while j < n and raw[j] != '"':
                j += 2 if raw[j] == "\\" else 1
            out.append(raw[i:j + 1])
            i = j + 1
        elif raw.startswith("//", i):
            while i < n and raw[i] != "\n":
                i += 1
        elif raw.startswith("/*", i):
            end = raw.find("*/", i + 2)
            i = n if end < 0 else end + 2
        elif c == "," and re.match(r"\s*[}\]]", raw[i + 1:i + 1 + 4096] or ""):
            i += 1  # a trailing comma before a closing brace or bracket
        else:
            out.append(c)
            i += 1
    return "".join(out)


def parse_json(raw: str):
    """JSON, then JSONC, then NDJSON (one object per line). Raises InputError."""
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    try:
        return json.loads(_strip_jsonc(raw))
    except json.JSONDecodeError:
        pass
    lines = [ln for ln in raw.splitlines() if ln.strip()]
    if len(lines) > 1:
        try:
            return [json.loads(ln) for ln in lines]
        except json.JSONDecodeError:
            pass
    raise InputError("the input is not JSON, JSON with comments, or one JSON object per line")


def read_rows(path: str | Path) -> list[dict]:
    """Rows from a CSV, a JSON list, NDJSON, or a JSON object wrapping a list under
    `value`, `items`, `data`, `apps`, `grants` or `extensions`. Every string is
    sanitized; keys are normalized to lower-case alphanumerics so header spelling
    does not matter. Raises InputError for an input that holds no rows, or that
    is one page of a paginated response (a next-page key beside the list), since
    either would otherwise print counts that read as complete."""
    raw = Path(path).read_bytes().decode("utf-8-sig", errors="replace")
    stripped = raw.lstrip()
    rows: list = []
    if stripped.startswith("[") or stripped.startswith("{"):
        data = parse_json(raw)
        if isinstance(data, dict):
            if any(_norm(str(k)) in NEXT_PAGE_KEYS and data[k] for k in data):
                raise InputError("the export is one page of a longer list (it carries a next-page link); "
                                 "merge every page into one JSON list and run again")
            for k in ("value", "items", "data", "apps", "grants", "extensions"):
                if isinstance(data.get(k), list):
                    data = data[k]
                    break
            else:
                data = [data]
        rows = [r for r in data if isinstance(r, dict)]
    else:
        rows = list(csv.DictReader(io.StringIO(raw)))
    if not rows:
        raise InputError("the export holds no rows, which cannot be told apart from a wrong or empty file")
    rows = sanitize_record(rows)
    return [{_norm(str(k)): v for k, v in r.items() if k is not None} for r in rows]


def require_columns(rows: list[dict], *aliases: str) -> None:
    """Raise InputError unless some row carries one of the aliases, so a file
    with none of the expected columns is refused instead of counted as zero."""
    want = {_norm(a) for a in aliases}
    if not any(want & set(r) for r in rows):
        raise InputError("none of the expected columns was found; check the export type and its column names")


def field(row: dict, *aliases: str):
    """First non-empty value among the aliases (normalized like the headers)."""
    for a in aliases:
        v = row.get(_norm(a))
        if v not in (None, ""):
            return v
    return None


def load_structured(path: str | Path):
    """A JSON, JSONC or TOML file, sanitized. Raises InputError when unparseable."""
    p = Path(path)
    raw = p.read_bytes().decode("utf-8-sig", errors="replace")
    if p.suffix.lower() == ".toml":
        import tomllib
        try:
            data = tomllib.loads(raw)
        except tomllib.TOMLDecodeError:
            raise InputError("the input is not valid TOML") from None
    else:
        data = parse_json(raw)
    return sanitize_record(data)


def run(main) -> None:
    """Run a reducer's main and exit. An InputError or any unexpected exception
    prints one fixed line on standard error (the exception's type name at most,
    never its message, a path or a traceback, since a message can quote the
    input) and nothing on standard output."""
    try:
        code = main(sys.argv[1:])
    except InputError as e:
        sys.stderr.write(f"reducer refused its input: {e}. Nothing was printed on standard output.\n")
        sys.exit(2)
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as e:  # noqa: BLE001 - the point is that nothing escapes unguarded
        sys.stderr.write(f"reducer failed ({type(e).__name__}) and printed nothing on standard output; "
                         "check the export type, and paste only standard output into a review.\n")
        sys.exit(2)
    sys.exit(code)


def _valid(v) -> bool:
    if isinstance(v, bool):
        return True
    if isinstance(v, int):
        return v >= 0
    return v == NOT_CHECKED


def emit(reducer: str, version: int, observations: dict, signals: dict,
         allowed_observations: set[str], allowed_signals: set[str]) -> None:
    """Validate everything, then print. Nothing reaches stdout unless all of it
    passes."""
    for name, v in list(observations.items()) + list(signals.items()):
        if not _valid(v):
            sys.exit(f"reducer defect: value for '{name}' is not an integer, true, false or {NOT_CHECKED}")
    bad = sorted(set(observations) - allowed_observations) + sorted(set(signals) - allowed_signals)
    if bad:
        sys.exit(f"reducer defect: undeclared names {bad}")

    def fmt(v):
        return ("true" if v else "false") if isinstance(v, bool) else str(v)

    out = [f"# {reducer} reducer v{version}: signal keys and counts only; nothing from the input is printed.",
           f"reducer: {reducer}", f"version: {version}", "observations:"]
    out += [f"  {k}: {fmt(observations[k])}" for k in sorted(observations)] or []
    if not observations:
        out[-1] = "observations: {}"
    out.append("signals:" if signals else "signals: {}")
    out += [f"  {k}: {{value: {fmt(signals[k])}, confidence: read}}" for k in sorted(signals)]
    sys.stdout.write("\n".join(out) + "\n")
