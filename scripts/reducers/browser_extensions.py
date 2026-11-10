#!/usr/bin/env python3
"""Reduce a browser extension report to counts of AI extensions by install mode.

Input: a CSV or JSON extension inventory, such as the Chrome Enterprise "Apps
& extensions usage" report exported to CSV, or an Edge or Intune extension
inventory. The reducer reads, per row:

  name          App name, Extension name, Name or Display name (used only for
                the AI-product match; never printed)
  id            App ID, Extension ID or ID, used only to count each extension
                once
  install mode  Install type, Installation mode, Install mode or installType

Install modes are read from the vocabularies the browsers document (Tier B):
Chrome's ExtensionSettings policy (force_installed, normal_installed,
allowed) and the extension management API's installType (admin, normal,
sideload, development). force_installed, a value containing "force", or
admin is force-installed; normal_installed or a value containing "allow" is
admin-allowed; normal, sideload, development or a value containing "user" is
user-installed; anything else is unknown. The report column names are the
maintainer's assumption (Tier D).

Output: ai-extensions-total, ai-extensions-force-installed,
ai-extensions-admin-allowed, ai-extensions-user-installed and
ai-extensions-mode-unknown, plus the signal surface-S3 set to true when any AI
extension is present (an absence proves nothing about browser AI, so false is
never printed).

Usage: python scripts/reducers/browser_extensions.py REPORT.csv|REPORT.json
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import emit, field, read_rows  # noqa: E402
from ai_catalog import ai_vendor  # noqa: E402

OBS = {"ai-extensions-total", "ai-extensions-force-installed", "ai-extensions-admin-allowed",
       "ai-extensions-user-installed", "ai-extensions-mode-unknown"}
RANK = {"force": 0, "allowed": 1, "user": 2, "unknown": 3}


def mode_of(value) -> str:
    v = str(value or "").strip().lower().replace(" ", "_")
    if "force" in v or v == "admin":
        return "force"
    if v == "normal_installed" or "allow" in v:
        return "allowed"
    if v in ("normal", "sideload", "development") or "user" in v:
        return "user"
    return "unknown"


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        sys.exit(__doc__.strip().splitlines()[-1])
    modes: dict[str, str] = {}
    for row in read_rows(argv[0]):
        name = field(row, "App name", "Extension name", "Name", "Display name")
        if not ai_vendor(name):
            continue
        ident = str(field(row, "App ID", "Extension ID", "ID") or name).strip().lower()
        m = mode_of(field(row, "Install type", "Installation mode", "Install mode", "installType"))
        # an extension seen with several modes is counted once, under its most administrator-controlled mode
        if ident not in modes or RANK[m] < RANK[modes[ident]]:
            modes[ident] = m
    counts = {k: sum(1 for v in modes.values() if v == k) for k in RANK}
    signals = {"surface-S3": True} if modes else {}
    emit("browser-extensions", 1,
         {"ai-extensions-total": len(modes), "ai-extensions-force-installed": counts["force"],
          "ai-extensions-admin-allowed": counts["allowed"], "ai-extensions-user-installed": counts["user"],
          "ai-extensions-mode-unknown": counts["unknown"]},
         signals, OBS, {"surface-S3"})
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
