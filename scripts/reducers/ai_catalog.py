"""Which app names, extension names and card descriptors count as AI products.

Evidence tier D: this list is the maintainer's judgement, built from product
names on the vendors' own public pages, and it is a heuristic. It misses
products it does not name, it will lag new launches, and it deliberately leaves
out names that are ordinary words or brand names shared with non-AI products
(so a count from it is a floor, not a census). It names no organization and
says nothing about who uses what. Corrections and additions are welcome
through CONTRIBUTING.md; keep each pattern unambiguous on its own.

Each entry is (regular expression, canonical vendor). Patterns are matched
case-insensitively against the sanitized text, with word boundaries.
"""

from __future__ import annotations

import re

CATALOG: list[tuple[str, str]] = [
    (r"openai|chat\s?gpt", "OpenAI"),
    (r"anthropic|claude(\.ai)?", "Anthropic"),
    (r"google\s+gemini|gemini\s+(for|in|app|advanced|enterprise|code)|notebooklm", "Google"),
    (r"microsoft\s+365\s+copilot|m365\s+copilot|copilot\s+studio|microsoft\s+copilot", "Microsoft"),
    (r"github\s+copilot", "GitHub"),
    (r"perplexity", "Perplexity"),
    (r"midjourney", "Midjourney"),
    (r"jasper(\.ai|\s+ai)", "Jasper"),
    (r"otter(\.ai|\s+ai)", "Otter.ai"),
    (r"fireflies(\.ai)?", "Fireflies.ai"),
    (r"read\.ai", "Read AI"),
    (r"tl;?dv", "tl;dv"),
    (r"grammarly", "Grammarly"),
    (r"deepl", "DeepL"),
    (r"mistral(\s+ai|\.ai)?", "Mistral AI"),
    (r"cohere", "Cohere"),
    (r"hugging\s?face", "Hugging Face"),
    (r"replicate\.com", "Replicate"),
    (r"elevenlabs", "ElevenLabs"),
    (r"synthesia", "Synthesia"),
    (r"runway(ml|\s+ml)", "Runway"),
    (r"tabnine", "Tabnine"),
    (r"codeium|windsurf", "Windsurf"),
    (r"cursor\s+(ai|editor|ide)|anysphere", "Anysphere (Cursor)"),
    (r"x\.ai|grok\s+(ai|app)", "xAI"),
    (r"deepseek", "DeepSeek"),
    (r"poe\.com", "Poe"),
    (r"character\.ai", "Character.AI"),
    (r"glean\s+(ai|assistant|work)", "Glean"),
    (r"monica\s*-?\s*(chatgpt|ai)", "Monica"),
]

_COMPILED = [(re.compile(rf"(?<![a-z0-9]){p}(?![a-z0-9])", re.I), v) for p, v in CATALOG]


def ai_vendor(*texts) -> str | None:
    """The canonical vendor if any text names a catalogued AI product, else None."""
    for t in texts:
        if not t:
            continue
        s = str(t)
        for rx, vendor in _COMPILED:
            if rx.search(s):
                return vendor
    return None
