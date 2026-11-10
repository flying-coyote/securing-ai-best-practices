#!/usr/bin/env python3
"""Reduce coding-agent settings and hooks files to counts and three signals.

Input: any number of files, each optionally prefixed with its scope as
`managed:PATH`, `user:PATH`, `project:PATH` or `local:PATH`. Without a prefix
the scope is inferred where the vendor documents an unambiguous name or path:
`managed-settings.json`, or a file under a documented system directory
(`/etc/claude-code/`, `/Library/Application Support/ClaudeCode/`,
`C:\\Program Files\\ClaudeCode\\`, `/etc/cursor/`, `/Library/Application
Support/Cursor/`, `C:\\ProgramData\\Cursor\\`), is managed, and
`settings.local.json` is local. Anything else is user or project and is
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
      fail-closed setting; false when every hook has it or none is configured
  hooks-user-disableable  true when hooks are configured outside the managed
      tier and no deny rule exists in any file, since a user's own local
      settings can switch such hooks off while a deny rule has no such switch
  mcp-allowlist-absent  from a Claude Code managed file only: false when
      `allowManagedMcpServersOnly` is true and `allowedMcpServers` is
      non-empty, true otherwise; not-checked with no Claude Code managed file

Hook commands, matchers, rule text, server names and paths are never printed.

Usage: python scripts/reducers/coding_agent_settings.py [scope:]FILE [...]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import NOT_CHECKED, emit, load_structured  # noqa: E402

OBS = {"settings-files-read", "managed-tier-seen", "hooks-configured", "hooks-fail-closed",
       "hooks-outside-managed", "deny-rules", "disable-all-hooks-set", "managed-locks-set"}
SIGNALS = {"coding-agent-managed-tier-absent", "hook-fail-open", "hooks-user-disableable", "mcp-allowlist-absent"}
SCOPES = {"managed", "user", "project", "local"}
MANAGED_DIRS = ("/etc/claude-code/", "/library/application support/claudecode/", "program files/claudecode/",
                "/etc/cursor/", "/library/application support/cursor/", "programdata/cursor/")


def split_arg(arg: str) -> tuple[str, str]:
    m = re.match(r"^(managed|user|project|local):(.+)$", arg)
    if m:
        return m.group(1), m.group(2)
    low = arg.replace("\\", "/").lower()
    name = Path(low).name
    if name.startswith("managed-settings") or any(d in low for d in MANAGED_DIRS):
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
    for arg in argv:
        scope, path = split_arg(arg)
        data = load_structured(path)
        if not isinstance(data, dict):
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
    signals = {
        "coding-agent-managed-tier-absent": False if managed_seen else NOT_CHECKED,
        "hook-fail-open": hooks_total > fail_closed,
        "hooks-user-disableable": outside > 0 and deny == 0,
        "mcp-allowlist-absent": (not allowlist_enforced) if cc_managed_seen else NOT_CHECKED,
    }
    emit("coding-agent-settings", 1,
         {"settings-files-read": files, "managed-tier-seen": managed_seen, "hooks-configured": hooks_total,
          "hooks-fail-closed": fail_closed, "hooks-outside-managed": outside, "deny-rules": deny,
          "disable-all-hooks-set": disable_all, "managed-locks-set": locks},
         signals, OBS, SIGNALS)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
