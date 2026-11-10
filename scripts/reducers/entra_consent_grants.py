#!/usr/bin/env python3
"""Reduce a Microsoft Entra ID OAuth consent-grant export to counts.

Input: a CSV or JSON file with one row per delegated permission grant. The
reducer reads three things from each row and nothing else:

  app name    displayName, appDisplayName, clientDisplayName, Application name,
              App name or Name (used only to decide whether the app is an AI
              product, via ai_catalog.py; never printed)
  consent     consentType: AllPrincipals means an administrator consented for
              the whole tenant and Principal means one user consented, which
              is how Microsoft Graph's oauth2PermissionGrant resource reports
              it (Tier B, vendor documentation); the words admin and user are
              accepted too
  scopes      scope, scopes, permissions or permission, space or comma separated

The column aliases beyond the Graph property names are the maintainer's
assumption about common export shapes (Tier D); a row whose app name or
consent type cannot be read is counted in grant-rows-unparsed rather than
guessed at. Graph returns the client as an ID, so join the service principal's
display name onto each grant before running this (any export that already
carries the app name works as it is).

Output: ai-apps-with-grants, ai-grants-mail-or-file-scope,
ai-grants-user-consented, ai-grants-admin-consented and grant-rows-unparsed.
It prints no signal key, because a grant count cannot say whether anyone
reviews the grants; ai-grants-mail-or-file-scope above zero is the observation
that raises oauth-grants-unreviewed to High.

Usage: python scripts/reducers/entra_consent_grants.py EXPORT.csv|EXPORT.json
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import emit, field, read_rows  # noqa: E402
from ai_catalog import ai_vendor  # noqa: E402
from consent_common import scopes, touches_mail_or_files  # noqa: E402

OBS = {"ai-apps-with-grants", "ai-grants-mail-or-file-scope", "ai-grants-user-consented",
       "ai-grants-admin-consented", "grant-rows-unparsed"}


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        sys.exit(__doc__.strip().splitlines()[-1])
    apps, mailfile, user, admin, unparsed = set(), 0, 0, 0, 0
    for row in read_rows(argv[0]):
        name = field(row, "displayName", "appDisplayName", "clientDisplayName", "Application name", "App name", "Name")
        ctype = str(field(row, "consentType", "consent type", "Granted through", "consent") or "").strip().lower()
        kind = ("admin" if ctype in ("allprincipals", "admin", "admin consent", "administrator")
                else "user" if ctype in ("principal", "user", "user consent") else None)
        if not name or kind is None:
            unparsed += 1
            continue
        vendor = ai_vendor(name)
        if not vendor:
            continue
        apps.add(str(name).strip().lower())
        if touches_mail_or_files(scopes(field(row, "scope", "scopes", "permissions", "permission"))):
            mailfile += 1
        if kind == "admin":
            admin += 1
        else:
            user += 1
    emit("entra-consent-grants", 1,
         {"ai-apps-with-grants": len(apps), "ai-grants-mail-or-file-scope": mailfile,
          "ai-grants-user-consented": user, "ai-grants-admin-consented": admin,
          "grant-rows-unparsed": unparsed},
         {}, OBS, set())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
