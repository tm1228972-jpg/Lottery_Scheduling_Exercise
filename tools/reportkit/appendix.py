"""Helpers that turn real source files into paginated code listings."""
from __future__ import annotations

import os


def full_listing(path, title_fa, title_en, chunk=46, lang=None, first_label=None):
    """Split a source file into consecutive listings, one per page-sized chunk.

    Returns a list of block dicts suitable for ``Model.appendix_section``.
    """
    path = os.path.abspath(path)
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    total = len(lines)
    fname = os.path.basename(path)
    blocks = []
    start = 1
    part = 1
    while start <= total:
        end = min(start + chunk - 1, total)
        blocks.append({
            "type": "code",
            "path": path,
            "start": start,
            "end": end,
            "cap": (
                f"{title_fa} — بخش {part} (خطوط {start} تا {end})",
                f"{title_en} — part {part} (lines {start}-{end})",
            ),
            "label": (
                f"{fname} — بخش {part}",
                f"{fname} — part {part}" if first_label is None else f"{first_label} — part {part}",
            ),
            "lang": lang,
        })
        start = end + 1
        part += 1
    return blocks


def source_stats(paths):
    """Real line/character counts, used in the report tables."""
    out = []
    for p in paths:
        with open(p, encoding="utf-8") as fh:
            text = fh.read()
        lines = text.splitlines()
        code = [l for l in lines if l.strip() and not l.strip().startswith("#")]
        out.append({
            "file": os.path.basename(p),
            "lines": len(lines),
            "code_lines": len(code),
            "chars": len(text),
            "functions": sum(1 for l in lines if l.lstrip().startswith(("def ", "static ", "int ", "void "))),
        })
    return out
