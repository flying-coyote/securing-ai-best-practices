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


def read_rows(path: str | Path) -> list[dict]:
    """Rows from a CSV, a JSON list, or a JSON object wrapping a list under
    `value`, `items`, `data` or `apps`. Every string is sanitized; keys are
    normalized to lower-case alphanumerics so header spelling does not matter."""
    raw = Path(path).read_bytes().decode("utf-8-sig", errors="replace")
    stripped = raw.lstrip()
    rows: list = []
    if stripped.startswith("[") or stripped.startswith("{"):
        data = json.loads(raw)
        if isinstance(data, dict):
            for k in ("value", "items", "data", "apps", "grants", "extensions"):
                if isinstance(data.get(k), list):
                    data = data[k]
                    break
            else:
                data = [data]
        rows = [r for r in data if isinstance(r, dict)]
    else:
        rows = list(csv.DictReader(io.StringIO(raw)))
    rows = sanitize_record(rows, context=Path(path).name)
    return [{_norm(str(k)): v for k, v in r.items() if k is not None} for r in rows]


def field(row: dict, *aliases: str):
    """First non-empty value among the aliases (normalized like the headers)."""
    for a in aliases:
        v = row.get(_norm(a))
        if v not in (None, ""):
            return v
    return None


def load_structured(path: str | Path):
    """A JSON or TOML file, sanitized."""
    p = Path(path)
    raw = p.read_bytes().decode("utf-8-sig", errors="replace")
    if p.suffix.lower() == ".toml":
        import tomllib
        data = tomllib.loads(raw)
    else:
        data = json.loads(raw)
    return sanitize_record(data, context=p.name)


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
