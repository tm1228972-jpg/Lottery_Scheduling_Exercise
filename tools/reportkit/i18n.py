"""Cell-level translation catalog for bilingual tables.

Content authors write a Persian cell once; when the English edition needs it,
it is looked up here. Any cell without a translation raises, so a report can
never silently ship a Persian table inside the English edition.
"""
from __future__ import annotations

import json
import os

_CACHE: dict[str, str] = {}
_PATHS = [
    os.path.join(os.path.dirname(__file__), "i18n_cells.json"),
]


def load(extra_path=None):
    global _CACHE
    if _CACHE:
        return _CACHE
    merged = {}
    for p in _PATHS + ([extra_path] if extra_path else []):
        if os.path.exists(p):
            with open(p, encoding="utf-8") as fh:
                merged.update(json.load(fh))
    _CACHE = merged
    return _CACHE


def translate(text: str) -> str | None:
    cat = load()
    return cat.get(text.strip())
