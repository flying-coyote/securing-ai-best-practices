"""Strip invisible and control characters from untrusted text before a reducer reads it.

Every reducer in this folder runs its input through ``sanitize_record`` before
matching anything, because admin exports, MCP configs and settings files carry
text that someone outside the organization wrote (an app's display name, a
server description, a hook comment), and a string can carry instructions a
human reviewer cannot see: Unicode tag characters (U+E0000 to U+E007F) render
as nothing and decode to ASCII, which makes them a prompt-injection channel.
The reducers print only counts and enums, so nothing from the input reaches
their output anyway; sanitizing first means the matching itself (is this app
name an AI product?) cannot be steered by invisible text either. This is the
same rule ``analysis/telemetry-is-an-injection-surface.md`` recommends for any
pipeline that hands event text to a model: strip control and format
characters at write time.

What is removed:
  * Unicode tag block U+E0000-U+E007F (matched by range, because many of those
    code points are unassigned, category Cn, so a category check misses them)
  * zero-width U+200B-U+200D, U+2060-U+2064, U+FEFF
  * bidi controls U+202A-U+202E, U+2066-U+2069, U+200E, U+200F
  * every other format character (category Cf), such as U+00AD soft hyphen
  * C0 and C1 control characters plus DEL (category Cc), except \\n and \\t
  * variation selectors that can smuggle bytes after a visible character:
    U+E0100-U+E01EF and U+FE00-U+FE0D always, and any U+FE0E/U+FE0F that
    follows another selector (a lone VS15/VS16 after a base is kept)

Trade-offs, security over fidelity: emoji ZWJ sequences degrade to their
component emoji, subdivision flags degrade to a plain flag, ZWNJ is stripped
(so some Persian, Urdu and Indic text loses a joiner hint), and CRLF becomes LF.
Non-Latin scripts and ordinary emoji pass through unchanged. Standard library
only. Copied from the maintainer's own ingestion code under this repo's MIT
licence.
"""
from __future__ import annotations

import re
import sys
import unicodedata

_EXPLICIT = re.compile(
    "["
    "\U000E0000-\U000E007F"   # tag block
    "\U000E0100-\U000E01EF"   # variation selectors supplement (VS17-VS256)
    "\uFE00-\uFE0D"           # variation selectors VS1-VS14
    "\u180B-\u180D\u180F"     # Mongolian free variation selectors
    "\u200B-\u200F"           # ZWSP, ZWNJ, ZWJ, LRM, RLM
    "\u202A-\u202E"           # bidi embeddings / overrides
    "\u2060-\u2064"           # word joiner, invisible operators
    "\u2066-\u2069"           # bidi isolates
    "\uFEFF"                  # BOM / ZWNBSP
    "]"
)

# VS15/VS16 (text/emoji presentation) are kept, but only one per base
# character: a run of selectors is how "emoji smuggling" encodes bytes.
_SELECTOR_RUN = re.compile("(?<=[\uFE0E\uFE0F])[\uFE0E\uFE0F]+")

_KEEP_CONTROLS = {"\n", "\t"}


def _strip_category(ch: str) -> bool:
    if ch in _KEEP_CONTROLS:
        return False
    return unicodedata.category(ch) in ("Cc", "Cf")


def scrub(text) -> tuple[str, int]:
    """Return (clean_text, number_of_characters_removed). None -> ("", 0)."""
    if text is None:
        return "", 0
    if not isinstance(text, str):
        text = str(text)
    if not text:
        return text, 0
    cleaned = "".join(ch for ch in _EXPLICIT.sub("", text) if not _strip_category(ch))
    # Collapse selector runs LAST, so stripping a soft hyphen or control char
    # between two selectors cannot leave a fresh run behind.
    cleaned = _SELECTOR_RUN.sub("", cleaned)
    return cleaned, len(text) - len(cleaned)


def sanitize_text(text, context: str = "") -> str:
    """Strip invisible/control characters; log a count to stderr when any were removed.

    Does not trim whitespace, so it is safe to apply to whole documents.
    """
    cleaned, removed = scrub(text)
    if removed:
        where = f" in {context}" if context else ""
        print(f"   [sanitize] stripped {removed} invisible/control char(s){where}",
              file=sys.stderr)
    return cleaned


def sanitize_record(obj, context: str = ""):
    """Recursively sanitize every str in a dict/list/tuple/set (keys included).

    Non-string scalars are returned unchanged. Returns a new object; the input is
    not mutated.
    """
    if isinstance(obj, str):
        return sanitize_text(obj, context)
    if isinstance(obj, dict):
        return {
            (sanitize_text(k, context) if isinstance(k, str) else k): sanitize_record(v, context)
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [sanitize_record(v, context) for v in obj]
    if isinstance(obj, tuple):
        return tuple(sanitize_record(v, context) for v in obj)
    if isinstance(obj, (set, frozenset)):
        return type(obj)(sanitize_record(v, context) for v in obj)
    return obj
