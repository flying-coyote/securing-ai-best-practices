#!/usr/bin/env python3
"""Reduce one or more MCP client configuration files to counts.

Input: any number of MCP config files: a Claude Code `.mcp.json` or
`~/.claude.json`, a Claude Desktop config, a Cursor `mcp.json`, a VS Code
`.vscode/mcp.json`, or a Codex `config.toml`. Servers are found under any key
named `mcpServers`, `servers` (VS Code) or `mcp_servers` (Codex TOML), at any
depth, so a `~/.claude.json` with per-project server lists is read whole.

Per server the reducer decides, without printing anything about it:

  remote or local  a `url` (or a type of http, sse or streamable-http) is
                   remote; a `command` is local
  pinned           a local server started by a package runner (npx, bunx,
                   pnpx, uvx, or pnpm or yarn dlx) is pinned when its package
                   argument carries an exact version (`pkg@1.2.3`,
                   `@scope/pkg@1.2.3`, `pkg==1.2.3`, or uvx `--from` with an
                   exact version); `latest`, ranges and no version are
                   unpinned; servers started any other way are neither
  inline secrets   values in `env` or `headers` whose name looks like a secret
                   (key, token, secret, password, auth, credential) and which
                   are not a reference (`${VAR}`, `$VAR`, `env:`, `op://`,
                   `{{...}}`), plus token-shaped strings anywhere in args,
                   env, headers or the URL; each counts once and no value is
                   ever printed

The config shapes are the clients' documented formats (Tier B); the secret
heuristics are the maintainer's (Tier D) and will miss secrets that look like
ordinary words.

Output: mcp-server-count, mcp-local-count, mcp-remote-count,
mcp-unpinned-count, mcp-pinned-count and mcp-inline-secret-count, and the
signals mcp-unpinned and mcp-remote (the counts), with agent-static-secrets
set to true when any inline secret is found (false is never printed, because a
clean config file does not show that agents hold no long-lived keys).

Usage: python scripts/reducers/mcp_config.py CONFIG [CONFIG ...]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import emit, load_structured  # noqa: E402

OBS = {"mcp-server-count", "mcp-local-count", "mcp-remote-count", "mcp-unpinned-count",
       "mcp-pinned-count", "mcp-inline-secret-count"}
SIGNALS = {"mcp-unpinned", "mcp-remote", "agent-static-secrets"}
SERVER_KEYS = {"mcpServers", "servers", "mcp_servers"}
RUNNERS = {"npx", "bunx", "pnpx", "uvx"}
DLX = {"pnpm", "yarn"}
SECRET_NAME = re.compile(r"(key|token|secret|passw|auth|credential|bearer)", re.I)
REFERENCE = re.compile(r"^\s*(\$\{[^}]+\}|\$[A-Za-z_][A-Za-z0-9_]*|env:|op://|\{\{.*\}\}|<[^>]+>)\s*$")
TOKEN_SHAPES = re.compile(
    r"(sk-(ant-|proj-)?[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}"
    r"|xox[abprs]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16}|glpat-[A-Za-z0-9_-]{16,}|AIza[0-9A-Za-z_-]{30,}"
    r"|Bearer\s+[A-Za-z0-9._~+/=-]{20,})")
URL_SECRET = re.compile(r"[?&](api[_-]?key|key|token|access[_-]?token|secret)=[^&\s]+", re.I)
EXACT_NPM = re.compile(r"^(@[^/\s]+/)?[^@\s]+@v?\d+\.\d+\.\d+([-+][0-9A-Za-z.-]+)?$")
EXACT_PY = re.compile(r"^[A-Za-z0-9_.\[\],-]+(==|@)v?\d+(\.\d+)*([-+.][0-9A-Za-z.-]+)?$")


def find_servers(node, out: list):
    if isinstance(node, dict):
        for k, v in node.items():
            if k in SERVER_KEYS and isinstance(v, dict):
                out.extend(s for s in v.values() if isinstance(s, dict) and ("command" in s or "url" in s or "type" in s))
            else:
                find_servers(v, out)
    elif isinstance(node, list):
        for v in node:
            find_servers(v, out)


def package_arg(command: str, args: list[str]) -> tuple[str | None, bool]:
    """(package spec, started by a package runner?)"""
    base = Path(str(command)).name.lower().removesuffix(".cmd").removesuffix(".exe")
    rest = [str(a) for a in args]
    if base in DLX:
        if not rest or rest[0] != "dlx":
            return None, False
        rest = rest[1:]
    elif base not in RUNNERS:
        return None, False
    i = 0
    while i < len(rest):
        a = rest[i]
        if a == "--from" and i + 1 < len(rest):
            return rest[i + 1], True
        if a in ("-p", "--package") and i + 1 < len(rest):
            return rest[i + 1], True
        if a.startswith("--from=") or a.startswith("--package="):
            return a.split("=", 1)[1], True
        if a.startswith("-"):
            i += 1
            continue
        return a, True
    return None, True


def pinned(spec: str | None) -> bool:
    if not spec:
        return False
    return bool(EXACT_NPM.match(spec) or EXACT_PY.match(spec))


def count_secrets(server: dict) -> int:
    n = 0
    for block in ("env", "headers"):
        for k, v in (server.get(block) or {}).items():
            if not isinstance(v, str) or not v.strip() or REFERENCE.match(v):
                continue
            if SECRET_NAME.search(str(k)) or TOKEN_SHAPES.search(v):
                n += 1
    args = [str(a) for a in server.get("args") or []]
    for i, a in enumerate(args):
        if TOKEN_SHAPES.search(a):
            n += 1
        elif re.match(r"^--?[A-Za-z0-9-]*(key|token|secret|password)[A-Za-z0-9-]*=(.+)$", a, re.I):
            if not REFERENCE.match(a.split("=", 1)[1]):
                n += 1
        elif re.match(r"^--?[A-Za-z0-9-]*(key|token|secret|password)[A-Za-z0-9-]*$", a, re.I) and i + 1 < len(args):
            nxt = args[i + 1]
            if not nxt.startswith("-") and not REFERENCE.match(nxt):
                n += 1
    url = str(server.get("url") or "")
    if URL_SECRET.search(url) or TOKEN_SHAPES.search(url):
        n += 1
    return n


def main(argv: list[str]) -> int:
    if not argv:
        sys.exit(__doc__.strip().splitlines()[-1])
    servers: list[dict] = []
    for p in argv:
        find_servers(load_structured(p), servers)
    local = remote = unp = pin = secrets = 0
    for s in servers:
        stype = str(s.get("type") or "").lower()
        if s.get("url") or stype in ("http", "sse", "streamable-http", "streamablehttp"):
            remote += 1
        elif s.get("command"):
            local += 1
            spec, runner = package_arg(s["command"], s.get("args") or [])
            if runner:
                if pinned(spec):
                    pin += 1
                else:
                    unp += 1
        secrets += count_secrets(s)
    signals = {"mcp-unpinned": unp, "mcp-remote": remote}
    if secrets:
        signals["agent-static-secrets"] = True
    emit("mcp-config", 1,
         {"mcp-server-count": len(servers), "mcp-local-count": local, "mcp-remote-count": remote,
          "mcp-unpinned-count": unp, "mcp-pinned-count": pin, "mcp-inline-secret-count": secrets},
         signals, OBS, SIGNALS)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
