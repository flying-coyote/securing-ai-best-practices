"""Scope classification shared by the two consent-grant reducers.

Mail and file scopes are named from the platforms' own permission references
(Tier B, vendor documentation of what a permission grants): Microsoft Graph
permissions in the Mail, Files and Sites families, and Google OAuth scopes for
Gmail, Drive, Docs, Sheets and Slides. A scope string is split on spaces and
commas.
"""

from __future__ import annotations

import re

_MS = re.compile(r"^(mail|files|sites)\.", re.I)
_GOOGLE = re.compile(r"(mail\.google\.com|/auth/(gmail|drive|documents|spreadsheets|presentations))", re.I)


def scopes(value) -> list[str]:
    if not value:
        return []
    return [s for s in re.split(r"[\s,;]+", str(value)) if s]


def touches_mail_or_files(scope_list: list[str]) -> bool:
    return any(_MS.match(s) or _GOOGLE.search(s) for s in scope_list)
