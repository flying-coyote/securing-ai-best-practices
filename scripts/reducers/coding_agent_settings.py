#!/usr/bin/env python3
"""Reduce coding-agent settings and hooks files to counts and four signals.

Input: any number of files, each optionally prefixed with its scope as
`managed:PATH`, `user:PATH`, `project:PATH` or `local:PATH`. Without a prefix
the scope is inferred from location only: a file whose absolute path starts
with a documented system directory (`/etc/claude-code/`, `/Library/Application
Support/ClaudeCode/`, `C:\\Program Files\\ClaudeCode\\`, `/etc/cursor/`,
`/Library/Application Support/Cursor/`, `C:\\ProgramData\\Cursor\\`) is managed,
whatever its name, and `settings.local.json` is local. A file named
`managed-settings.json` anywhere else is not treated as managed, because a
project or user file can carry that name; pass `managed:` for a copy of the
managed file taken off a machine. Anything else is user or project and is
treated as not managed, which is the safe reading. Two products are read, from
their documented formats (Tier B, vendor documentation of what a setting
does):

  Claude Code settings JSON: `hooks` (event, then matcher groups, then hook
  commands; a hook blocks on failure only with `onFailure: "block"`),
  `permissions.deny`, `disableAllHooks`, and in the managed tier the locks
  `allowManagedHooksOnly`, `allowManagedPermissionRulesOnly`,
  `permissions.disableBypassPermissionsMode: "disable"`, and the MCP allowlist
  `allowManagedMcpServersOnly` with `allowedMcpServers`
  Cursor `hooks.json`: `hooks` (event, then hook entries; an entry blocks on
  failure only with `failClosed: true`)

Signals, each reported only as far as the files can show it:

  coding-agent-managed-tier-absent  false when a managed file is among the
      inputs; not-checked otherwise, because a missing file on one machine is
      not proof that no managed tier exists
  hook-fail-open    true when any configured hook lacks its product's
      fail-closed setting; false when every hook has it; not-checked when the
      files configure no hook, because files without hooks do not show how
      hooks configured elsewhere fail
  hooks-user-disableable  true when hooks are configured outside the managed
      tier and no deny rule exists in any file, since a user's own local
      settings can switch such hooks off; false when every configured hook is
      in the managed tier; not-checked when no hook is configured, or when
      hooks sit outside the managed tier beside deny rules, because the
      reducer does not read what a deny rule covers and so cannot tell whether
      any of them stops a user switching the hooks off
  mcp-allowlist-absent  from a Claude Code managed file only: false when
      `allowManagedMcpServersOnly` is true and `allowedMcpServers` is
      non-empty, true otherwise; not-checked with no Claude Code managed file

An input file that cannot be parsed is skipped and counted on standard error,
and any of the last three signals that would have printed false prints
not-checked instead, because the skipped file could hold the hook or setting
that makes it true. When no file can be parsed, nothing is printed.

Hook commands, matchers, rule text, server names and paths are never printed.

Usage: python scripts/reducers/coding_agent_settings.py [scope:]FILE [...]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import NOT_CHECKED, InputError, emit, load_structured, run  # noqa: E402

OBS = {"settings-files-read", "managed-tier-seen", "hooks-configured", "hooks-fail-closed",
       "hooks-outside-managed", "deny-rules", "disable-all-hooks-set", "managed-locks-set"}
SIGNALS = {"coding-agent-managed-tier-absent", "hook-fail-open", "hooks-user-disableable", "mcp-allowlist-absent"}
SCOPES = {"managed", "user", "project", "local"}
# The documented system directories, matched at the start of the path (after
# any drive letter), so a project or user file that happens to be named
# managed-settings.json, or a copy under some other tree, is not the managed tier.
MANAGED_DIRS = re.compile(r"^(?:[a-z]:)?/(?:etc/claude-code/|library/application support/claudecode/"
                          r"|program files/claudecode/|etc/cursor/|library/application support/cursor/"
                          r"|programdata/cursor/)")


def split_arg(arg: str) -> tuple[str, str]:
    m = re.match(r"^(managed|user|project|local):(.+)$", arg)
    if m:
        return m.group(1), m.group(2)
    low = arg.replace("\\", "/").lower()
    name = Path(low).name
    if MANAGED_DIRS.match(low):
        return "managed", arg
    if name == "settings.local.json":
        return "local", arg
    return "unscoped", arg


def hooks_in(data: dict) -> list[tuple[bool]]:
    """One entry per hook command: True if it fails closed."""
    out = []
    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        return out
    cursor = "version" in data
    top_fail_closed = data.get("failClosed") is True
    for groups in hooks.values():
        if not isinstance(groups, list):
            continue
        for g in groups:
            if not isinstance(g, dict):
                continue
            if cursor or "hooks" not in g:
                out.append(g.get("failClosed") is True or top_fail_closed or g.get("onFailure") == "block")
                continue
            group_block = g.get("onFailure") == "block"
            for h in g.get("hooks") or []:
                if isinstance(h, dict):
                    out.append(h.get("onFailure") == "block" or group_block)
    return out


def main(argv: list[str]) -> int:
    if not argv:
        sys.exit(__doc__.strip().splitlines()[-1])
    files = hooks_total = fail_closed = outside = deny = disable_all = locks = 0
    managed_seen = cc_managed_seen = False
    allowlist_enforced = False
    skipped = 0
    for arg in argv:
        scope, path = split_arg(arg)
        try:
            data = load_structured(path)
        except (InputError, OSError):
            skipped += 1  # one unreadable file does not abort the others; counted below
            continue
        if not isinstance(data, dict):
            skipped += 1
            continue
        files += 1
        is_cursor = "version" in data and isinstance(data.get("hooks"), dict)
        hs = hooks_in(data)
        hooks_total += len(hs)
        fail_closed += sum(1 for h in hs if h)
        perms = data.get("permissions") if isinstance(data.get("permissions"), dict) else {}
        deny += len(perms.get("deny") or [])
        if data.get("disableAllHooks") is True:
            disable_all += 1
        if scope == "managed":
            managed_seen = True
            if not is_cursor:
                cc_managed_seen = True
                locks += sum([data.get("allowManagedHooksOnly") is True,
                              data.get("allowManagedPermissionRulesOnly") is True,
                              perms.get("disableBypassPermissionsMode") == "disable"])
                if data.get("allowManagedMcpServersOnly") is True and (data.get("allowedMcpServers") or []):
                    allowlist_enforced = True
        else:
            outside += len(hs)
    if skipped == len(argv):
        raise InputError("no input file could be read as a settings or hooks object")
    if skipped:
        sys.stderr.write(f"skipped {skipped} of {len(argv)} input files that could not be parsed; "
                         "values that would read as clean print not-checked instead.\n")
    signals = {
        "coding-agent-managed-tier-absent": False if managed_seen else NOT_CHECKED,
        "hook-fail-open": (hooks_total > fail_closed) if hooks_total else NOT_CHECKED,
        "hooks-user-disableable": (NOT_CHECKED if not hooks_total
                                   else True if outside and not deny
                                   else NOT_CHECKED if outside
                                   else False),
        "mcp-allowlist-absent": (not allowlist_enforced) if cc_managed_seen else NOT_CHECKED,
    }
    if skipped:  # a skipped file could hold the hook or setting that turns a false into a true
        signals = {k: (NOT_CHECKED if v is False and k != "coding-agent-managed-tier-absent" else v)
                   for k, v in signals.items()}
    emit("coding-agent-settings", 1,
         {"settings-files-read": files, "managed-tier-seen": managed_seen, "hooks-configured": hooks_total,
          "hooks-fail-closed": fail_closed, "hooks-outside-managed": outside, "deny-rules": deny,
          "disable-all-hooks-set": disable_all, "managed-locks-set": locks},
         signals, OBS, SIGNALS)
    return 0


if __name__ == "__main__":
    run(main)
