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
  pinned           a local server started by a package runner (npx, bunx or
                   bun x, pnpx, uvx or uv tool run, npm exec or npm x, pnpm
                   or yarn dlx, or pipx run) is
                   pinned when its package argument carries an exact version
                   (`pkg@1.2.3`, `@scope/pkg@1.2.3`, `pkg==1.2.3`, or uvx
                   `--from` with an exact version); `latest`, ranges and no
                   version are unpinned. Option values (`uvx --python 3.12`,
                   `npx --registry URL`) are skipped, never taken for the
                   package. A runner wrapped in `cmd /c`, `sh -c` or `bash -lc`
                   (or zsh, dash, pwsh, powershell), `env VAR=value`, `exec`,
                   or a leading `VAR=value` inside the shell string is
                   unwrapped first. A wrapper the reducer cannot resolve (a shell string
                   with pipes or `&&`, or one it cannot split) is counted as
                   unknown, never dropped; servers started any other way
                   (`node server.js`, a binary) are neither
  inline secrets   values in `env` or `headers` (a mapping, or a list of
                   `NAME=value` strings) whose name ends in a secret word
                   (key, token, secret, password, auth, authorization,
                   credential, bearer, pat, so `MAX_TOKENS` and `AUTH_MODE` do
                   not count) and whose value looks like a credential (eight or
                   more characters with no spaces, not a number or a boolean,
                   after any `Bearer`, `Basic` or `Token` prefix) and is not a
                   reference (`${VAR}`, `$VAR`, `env:VAR`, `op://...`,
                   `{{...}}`, `<...>`, or any value that interpolates `${...}`
                   or `{{...}}`), the same rule for `--name value` and
                   `--name=value` arguments, plus token-shaped strings
                   anywhere in args, env, headers or the URL, and a password in
                   the URL's userinfo (`https://user:password@host`); each counts once
                   and no value is ever printed

The config shapes are the clients' documented formats (Tier B); the secret
heuristics are the maintainer's (Tier D) and will miss secrets that look like
ordinary words.

Output: mcp-server-count, mcp-local-count, mcp-remote-count,
mcp-unpinned-count, mcp-pinned-count, mcp-launch-unknown-count and
mcp-inline-secret-count, and the signals mcp-unpinned and mcp-remote (the
counts; mcp-unpinned is not-checked rather than 0 when no server was found
unpinned but some launch could not be read, and both are not-checked
rather than 0 when an input file could not be parsed and was skipped, or
when no server was found in any file), with
agent-static-secrets
set to true when any inline secret is found (false is never printed, because a
clean config file does not show that agents hold no long-lived keys).

Usage: python scripts/reducers/mcp_config.py CONFIG [CONFIG ...]
"""

from __future__ import annotations

import re
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import NOT_CHECKED, InputError, emit, load_structured, run  # noqa: E402

OBS = {"mcp-server-count", "mcp-local-count", "mcp-remote-count", "mcp-unpinned-count",
       "mcp-pinned-count", "mcp-inline-secret-count", "mcp-launch-unknown-count"}
SIGNALS = {"mcp-unpinned", "mcp-remote", "agent-static-secrets"}
SERVER_KEYS = {"mcpServers", "servers", "mcp_servers"}
RUNNERS = {"npx", "bunx", "pnpx", "uvx"}
DLX = {"pnpm", "yarn"}
SHELLS = {"sh", "bash", "zsh", "dash", "pwsh", "powershell"}
# Options that take a value, per runner, so the value is never read as the
# package, and the options whose value is the package. The uvx and npm exec
# lists were read from `uvx --help` (uv 0.9) and `npm exec --help` (npm 10.9) on
# the maintainer's machine (Tier B, the tools documenting their own flags); the
# npx -p, bunx, pnpm dlx, yarn dlx and pipx entries are the maintainer's reading
# of those tools' documentation (Tier D until rechecked). For uvx, -p is
# --python; for npx, bunx and yarn dlx it is --package; npm exec has no -p.
NPM_VALUE = {"--package", "--call", "-c", "--workspace", "-w", "--registry", "--cache", "--userconfig", "--prefix"}
UV_VALUE = {"--from", "--with", "-w", "--with-editable", "--with-requirements", "--constraints", "-c",
            "--build-constraints", "-b", "--overrides", "--env-file", "--python-platform", "--index",
            "--default-index", "--index-url", "-i", "--extra-index-url", "--find-links", "-f", "--index-strategy",
            "--keyring-provider", "--upgrade-package", "-P", "--resolution", "--prerelease", "--fork-strategy",
            "--exclude-newer", "--exclude-newer-package", "--reinstall-package", "--link-mode", "--config-setting",
            "-C", "--config-settings-package", "--no-build-isolation-package", "--no-build-package",
            "--no-binary-package", "--cache-dir", "--refresh-package", "--python", "-p", "--color",
            "--allow-insecure-host", "--directory", "--project", "--config-file"}
VALUE_OPTS = {
    "npx": NPM_VALUE | {"-p"}, "pnpx": {"--package"}, "npm": NPM_VALUE, "bunx": {"--package", "-p"},
    "pnpm": {"--package"}, "yarn": {"--package", "-p"}, "uvx": UV_VALUE, "pipx": {"--spec", "--python", "--index-url",
                                                                                "-i", "--pip-args"},
}
PACKAGE_OPTS = {"npx": {"--package", "-p"}, "pnpx": {"--package"}, "npm": {"--package"},
                "bunx": {"--package", "-p"}, "pnpm": {"--package"}, "yarn": {"--package", "-p"}, "uvx": {"--from"},
                "pipx": {"--spec"}}
SECRET_WORDS = {"key", "apikey", "token", "secret", "password", "passwd", "pwd", "credential", "credentials",
                "auth", "authorization", "bearer", "pat"}
REFERENCE = re.compile(r"^\s*(\$\{[^}]+\}|\$[A-Za-z_][A-Za-z0-9_]*|env:[A-Za-z_][A-Za-z0-9_]*|op://\S+"
                       r"|\{\{.*\}\}|<[^>]+>)\s*$")
SCHEME = re.compile(r"^\s*(bearer|basic|token)\s+", re.I)
# The leading guard keeps "risk-management-framework" from reading as an `sk-` key.
TOKEN_SHAPES = re.compile(
    r"(?<![A-Za-z0-9])(sk-(ant-|proj-)?[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}"
    r"|xox[abprs]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16}|glpat-[A-Za-z0-9_-]{16,}|AIza[0-9A-Za-z_-]{30,}"
    r"|Bearer\s+[A-Za-z0-9._~+/=-]{20,})")
URL_SECRET = re.compile(r"[?&](api[_-]?key|key|token|access[_-]?token|secret)=[^&\s]+", re.I)
# A password in the URL's userinfo (scheme://user:password@host); `user@host` alone is not one.
URL_USERINFO = re.compile(r"^[a-z][a-z0-9+.-]*://[^/@\s:]*:([^/@\s]+)@", re.I)
# A value that interpolates a variable anywhere (`prefix-${VAR}`, `Bearer ${env:X}`) is a reference.
EMBEDDED_REF = re.compile(r"\$\{[^}]+\}|\{\{[^}]+\}\}")
EXACT_NPM = re.compile(r"^(@[^/\s]+/)?[^@\s]+@v?\d+\.\d+\.\d+([-+][0-9A-Za-z.-]+)?$")
# `@` pins only with a full major.minor.patch (EXACT_NPM), because npm reads
# `pkg@1` and `pkg@1.2` as ranges; `==` pins at any precision.
EXACT_PY = re.compile(r"^[A-Za-z0-9_.\[\],-]+==v?\d+(\.\d+)*([-+.][0-9A-Za-z.-]+)?$")


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


def base_name(command) -> str:
    return Path(str(command).replace("\\", "/")).name.lower().removesuffix(".cmd").removesuffix(".exe")


def launch(command, args: list, depth: int = 0) -> tuple[str, str | None]:
    """("runner", package spec or None), ("neither", None) or ("unknown", None)."""
    rest = [str(a) for a in args]
    if not rest and re.search(r"\s", str(command).strip()):
        try:
            parts = shlex.split(str(command))
        except ValueError:
            return "unknown", None
        command, rest = parts[0], parts[1:]
    base = base_name(command)
    if depth > 3:
        return "unknown", None
    if base == "env":
        while rest and (re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", rest[0]) or rest[0].startswith("-")):
            rest = rest[1:]
        return launch(rest[0], rest[1:], depth + 1) if rest else ("unknown", None)
    if base == "cmd":
        if not rest or rest[0].lower() not in ("/c", "/k", "/s/c"):
            return "unknown", None
        inner = rest[1:]
        if len(inner) == 1:
            return shell_string(inner[0], depth)
        return launch(inner[0], inner[1:], depth + 1) if inner else ("unknown", None)
    if base in SHELLS:
        for i, a in enumerate(rest):
            if (a in ("-Command", "-command") or re.fullmatch(r"-[A-Za-z]*c[A-Za-z]*", a)) and i + 1 < len(rest):
                return shell_string(" ".join(rest[i + 1:]), depth)
        return "unknown", None
    if base == "exec":
        return launch(rest[0], rest[1:], depth + 1) if rest else ("unknown", None)
    if base == "uv" and rest[:2] == ["tool", "run"]:
        base, rest = "uvx", rest[2:]
    elif base == "bun" and rest[:1] == ["x"]:
        base, rest = "bunx", rest[1:]
    elif base == "pipx":
        if rest[:1] != ["run"]:
            return "neither", None
        rest = rest[1:]
    if base == "npm":
        if not rest or rest[0] not in ("exec", "x"):
            return "neither", None
        rest = rest[1:]
    elif base in DLX:
        if not rest or rest[0] != "dlx":
            return "neither", None
        rest = rest[1:]
    elif base not in RUNNERS and base != "pipx":
        return "neither", None
    values, pkg_opts = VALUE_OPTS[base], PACKAGE_OPTS[base]
    i = 0
    while i < len(rest):
        a = rest[i]
        if a == "--":
            return ("runner", rest[i + 1]) if i + 1 < len(rest) else ("runner", None)
        name, eq, val = a.partition("=")
        if a.startswith("-") and eq:
            if name in pkg_opts:
                return "runner", val
            i += 1
            continue
        if a in pkg_opts and i + 1 < len(rest):
            return "runner", rest[i + 1]
        if a in values:
            i += 2
            continue
        if a.startswith("-"):
            i += 1
            continue
        return "runner", a
    return "runner", None


def shell_string(text: str, depth: int) -> tuple[str, str | None]:
    if re.search(r"&&|\|\||[;|`]|\$\(", text):
        return "unknown", None
    try:
        parts = shlex.split(text)
    except ValueError:
        return "unknown", None
    while parts and (parts[0] == "exec" or re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", parts[0])):
        parts = parts[1:]  # `exec npx ...` and `FOO=1 npx ...` launch the command that follows
    return launch(parts[0], parts[1:], depth + 1) if parts else ("unknown", None)


def package_arg(command: str, args: list[str]) -> tuple[str | None, bool]:
    """(package spec, started by a package runner?); kept for callers of v1."""
    kind, spec = launch(command, args)
    return spec, kind == "runner"


def pinned(spec: str | None) -> bool:
    if not spec:
        return False
    return bool(EXACT_NPM.match(spec) or EXACT_PY.match(spec))


def secret_name(name: str) -> bool:
    """True when the name's last word is a secret word: GITHUB_TOKEN, X-Api-Key and
    apiKey count; MAX_TOKENS, AUTH_MODE and TOKEN_URL do not."""
    words = [w for w in re.split(r"[^A-Za-z0-9]+|(?<=[a-z0-9])(?=[A-Z])", str(name).lstrip("-")) if w]
    return bool(words) and words[-1].lower() in SECRET_WORDS


def credential_value(v) -> bool:
    """True when a value looks like a credential rather than a reference, a word,
    a number or a boolean."""
    if not isinstance(v, str):
        return False
    v = SCHEME.sub("", v.strip(), count=1).strip()
    if not v or REFERENCE.match(v) or EMBEDDED_REF.search(v) or re.search(r"\s", v) or len(v) < 8:
        return False
    return not (v.isdigit() or v.lower() in ("true", "false", "none", "null"))


def pairs(block) -> list[tuple[str, object]]:
    """env or headers as (name, value) pairs, from a mapping or a list of NAME=value strings."""
    if isinstance(block, dict):
        return list(block.items())
    if isinstance(block, list):
        return [tuple(str(x).split("=", 1)) for x in block if isinstance(x, str) and "=" in x]
    return []


def count_secrets(server: dict) -> int:
    n = 0
    for block in ("env", "headers"):
        for k, v in pairs(server.get(block)):
            if not isinstance(v, str):
                continue
            if TOKEN_SHAPES.search(v) or (secret_name(k) and credential_value(v)):
                n += 1
    args = [str(a) for a in server.get("args")] if isinstance(server.get("args"), list) else []
    for i, a in enumerate(args):
        if TOKEN_SHAPES.search(a):
            n += 1
            continue
        if not a.startswith("-"):
            continue
        name, eq, val = a.partition("=")
        if not secret_name(name):
            continue
        if eq:
            n += credential_value(val)
        elif i + 1 < len(args) and not args[i + 1].startswith("-"):
            n += credential_value(args[i + 1])
    url = str(server.get("url") or "")
    userinfo = URL_USERINFO.match(url)
    if (URL_SECRET.search(url) or TOKEN_SHAPES.search(url)
            or (userinfo and not EMBEDDED_REF.search(userinfo.group(1)) and not REFERENCE.match(userinfo.group(1)))):
        n += 1
    return n


def main(argv: list[str]) -> int:
    if not argv:
        sys.exit(__doc__.strip().splitlines()[-1])
    servers: list[dict] = []
    skipped = 0
    for p in argv:
        try:
            find_servers(load_structured(p), servers)
        except (InputError, OSError):
            skipped += 1  # one unreadable file does not abort the others; counted below
    if skipped == len(argv):
        raise InputError("no input file could be read as JSON, JSON with comments, or TOML")
    if skipped:
        sys.stderr.write(f"skipped {skipped} of {len(argv)} input files that could not be parsed; "
                         "counts that would read as clean print not-checked instead.\n")
    local = remote = unp = pin = unknown = secrets = 0
    for s in servers:
        stype = str(s.get("type") or "").lower()
        if s.get("url") or stype in ("http", "sse", "streamable-http", "streamablehttp"):
            remote += 1
        elif s.get("command"):
            local += 1
            args = s.get("args") if isinstance(s.get("args"), list) else []
            kind, spec = launch(s["command"], args)
            if kind == "runner":
                if pinned(spec):
                    pin += 1
                else:
                    unp += 1
            elif kind == "unknown":
                unknown += 1
        secrets += count_secrets(s)
    # a zero would read as clean; with unread launches it is only a floor
    # With no server parsed, a 0 would read as clean (route.py treats a read 0 so),
    # though the files may simply not be the ones that hold the servers.
    signals = {"mcp-unpinned": unp if (unp or not (unknown or skipped or not servers)) else NOT_CHECKED,
               "mcp-remote": remote if (remote or not (skipped or not servers)) else NOT_CHECKED}
    if secrets:
        signals["agent-static-secrets"] = True
    emit("mcp-config", 1,
         {"mcp-server-count": len(servers), "mcp-local-count": local, "mcp-remote-count": remote,
          "mcp-unpinned-count": unp, "mcp-pinned-count": pin, "mcp-launch-unknown-count": unknown,
          "mcp-inline-secret-count": secrets},
         signals, OBS, SIGNALS)
    return 0


if __name__ == "__main__":
    run(main)
