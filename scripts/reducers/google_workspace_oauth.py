#!/usr/bin/env python3
"""Reduce a Google Workspace OAuth log-events export to counts.

Input: a CSV or JSON export of the Admin console's OAuth log events (Reporting,
Audit and investigation, OAuth log events; Tier B for what that log records).
The reducer reads, per row:

  event       Event name or Event; only grant events count (authorize, grant,
              or an empty event column); revoke and activity rows are skipped
  app name    Application name, App name, Client name or Name (used only for
              the AI-product match; never printed)
  scopes      Scope, Scopes or Requested scopes
  user        User, Actor or Email, used only to count one grant per app and
              user pair; never printed and never kept after the run

The column names are the maintainer's reading of the export (Tier D; the
console's column labels have changed before). A row with no app name counts
in grant-rows-unparsed. Workspace OAuth grants are user consents unless an
administrator marked the app trusted, which this log does not show, so every
counted grant is reported as user-consented and no admin count is printed.

Output: ai-apps-with-grants, ai-grants-mail-or-file-scope,
ai-grants-user-consented and grant-rows-unparsed.

Usage: python scripts/reducers/google_workspace_oauth.py EXPORT.csv|EXPORT.json
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import emit, field, read_rows  # noqa: E402
from ai_catalog import ai_vendor  # noqa: E402
from consent_common import scopes, touches_mail_or_files  # noqa: E402

OBS = {"ai-apps-with-grants", "ai-grants-mail-or-file-scope", "ai-grants-user-consented", "grant-rows-unparsed"}
GRANT_EVENTS = {"", "authorize", "grant", "token_grant", "oauth grant"}


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        sys.exit(__doc__.strip().splitlines()[-1])
    apps, pairs, mail_pairs, unparsed = set(), set(), set(), 0
    for row in read_rows(argv[0]):
        event = str(field(row, "Event name", "Event") or "").strip().lower()
        if event not in GRANT_EVENTS:
            continue
        name = field(row, "Application name", "App name", "Client name", "Name")
        if not name:
            unparsed += 1
            continue
        if not ai_vendor(name):
            continue
        app = str(name).strip().lower()
        who = str(field(row, "User", "Actor", "Email") or "").strip().lower()
        apps.add(app)
        pairs.add((app, who))
        if touches_mail_or_files(scopes(field(row, "Scope", "Scopes", "Requested scopes"))):
            mail_pairs.add((app, who))
    emit("google-workspace-oauth", 1,
         {"ai-apps-with-grants": len(apps), "ai-grants-mail-or-file-scope": len(mail_pairs),
          "ai-grants-user-consented": len(pairs), "grant-rows-unparsed": unparsed},
         {}, OBS, set())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
