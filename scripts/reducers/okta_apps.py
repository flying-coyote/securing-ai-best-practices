#!/usr/bin/env python3
"""Reduce an Okta application list to counts of AI apps and how they sign in.

Input: the JSON array the Okta Apps API returns (GET /api/v1/apps), or a CSV
with the same fields. The reducer reads, per app:

  label       label, App name, Application or Name (used only for the
              AI-product match; never printed); the app's catalogue name
              (`name`) is checked too
  signOnMode  signOnMode or Sign on mode; SAML_2_0, SAML_1_1, OPENID_CONNECT
              and WS_FEDERATION are federated, and every other documented
              mode (BOOKMARK, BASIC_AUTH, BROWSER_PLUGIN,
              SECURE_PASSWORD_STORE, AUTO_LOGIN) is not
  status      status: ACTIVE or INACTIVE

The field names and sign-on modes are those of the Okta Apps API (Tier B,
vendor documentation); the CSV header aliases are the maintainer's assumption
(Tier D). An app with no readable sign-on mode counts as not federated, since
the reducer cannot show it is.

Output: ai-apps-in-idp, ai-apps-federated, ai-apps-not-federated and
ai-apps-inactive. No signal key: an app list cannot say whether the apps were
reviewed.

Usage: python scripts/reducers/okta_apps.py APPS.json|APPS.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import emit, field, read_rows  # noqa: E402
from ai_catalog import ai_vendor  # noqa: E402

OBS = {"ai-apps-in-idp", "ai-apps-federated", "ai-apps-not-federated", "ai-apps-inactive"}
FEDERATED = {"SAML_2_0", "SAML_1_1", "OPENID_CONNECT", "WS_FEDERATION"}


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        sys.exit(__doc__.strip().splitlines()[-1])
    seen, fed, notfed, inactive = set(), 0, 0, 0
    for row in read_rows(argv[0]):
        label = field(row, "label", "App name", "Application", "Name")
        if not ai_vendor(label, row.get("name")):
            continue
        ident = str(row.get("id") or label).strip().lower()
        if ident in seen:
            continue
        seen.add(ident)
        mode = str(field(row, "signOnMode", "Sign on mode") or "").strip().upper()
        if mode in FEDERATED:
            fed += 1
        else:
            notfed += 1
        if str(field(row, "status") or "").strip().upper() == "INACTIVE":
            inactive += 1
    emit("okta-apps", 1,
         {"ai-apps-in-idp": len(seen), "ai-apps-federated": fed,
          "ai-apps-not-federated": notfed, "ai-apps-inactive": inactive},
         {}, OBS, set())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
