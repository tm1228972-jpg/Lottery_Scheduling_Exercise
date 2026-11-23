"""Content model: bilingual (fa,en) blocks authored once, rendered to PDF/DOCX/slides."""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field


# ----------------------------------------------------------------------------- block constructors
def p(fa: str, en: str, **kw):
    return {"type": "p", "fa": fa, "en": en, **kw}


def lead(fa: str, en: str):
    return {"type": "lead", "fa": fa, "en": en}


def h2(fa: str, en: str):
    return {"type": "h2", "fa": fa, "en": en}


def h3(fa: str, en: str):
    return {"type": "h3", "fa": fa, "en": en}


def ul(items_fa, items_en=None, tight=False):
    items_en = items_en if items_en is not None else [None] * len(items_fa)
    items = []
    for fa, en in zip(items_fa, items_en):
        items.append((fa, en if en is not None else fa))
    return {"type": "ul", "items": items, "tight": tight}


def ol(items_fa, items_en=None):
    d = ul(items_fa, items_en)
    d["type"] = "ol"
    return d


def _cell(x):
    if isinstance(x, tuple):
        return x
    return (str(x), str(x))


def tbl(cap_fa, cap_en, head_fa, head_en, rows, widths=None, font=8.7, align=None, note_fa=None, note_en=None):
    """rows: list[list[str|(fa,en)]]"""
    r = [[_cell(c) for c in row] for row in rows]
    return {
        "type": "table",
        "cap": (cap_fa, cap_en),
        "head": (list(head_fa), list(head_en)),
        "rows": r,
        "widths": widths,
        "font": font,
        "align": align,
        "note": (note_fa, note_en) if note_fa else None,
    }


def fig(path, cap_fa, cap_en, width=0.92, height=None, en_path=None):
    """A figure. If `en_path` is given it is used in the English edition so that the
    chart's own labels are in English too (captions alone are not enough)."""
    return {"type": "figure", "path": path, "en_path": en_path or path,
            "cap": (cap_fa, cap_en), "width": width, "height": height}


def code(path, cap_fa, cap_en, start=None, end=None, label_fa=None, label_en=None):
    return {
        "type": "code",
        "path": path,
        "cap": (cap_fa, cap_en),
        "start": start,
        "end": end,
        "label": (label_fa, label_en),
    }


def snippet(code_text, cap_fa, cap_en, lang="text", label_fa=None, label_en=None):
    return {
        "type": "code",
        "text": code_text,
        "cap": (cap_fa, cap_en),
        "lang": lang,
        "label": (label_fa, label_en),
    }


def note(title_fa, title_en, body_fa, body_en, kind="note"):
    return {"type": "note", "title": (title_fa, title_en), "body": (body_fa, body_en), "kind": kind}


def quote(fa, en, source_fa="", source_en=""):
    return {"type": "quote", "fa": fa, "en": en, "src": (source_fa, source_en)}


def formula(text, en=None):
    """A display formula. Formulas are usually language-neutral (Latin/maths), so the
    same text is used in both editions unless an explicit English variant is given."""
    return {"type": "formula", "fa": text, "en": en or text}


def kv(pairs, cap_fa="", cap_en=""):
    return {"type": "kv", "pairs": [(_cell(a), _cell(b)) for a, b in pairs], "cap": (cap_fa, cap_en)}


def pagebreak():
    return {"type": "pagebreak"}


def spacer(h=10):
    return {"type": "spacer", "h": h}


# ----------------------------------------------------------------------------- document model
@dataclass
class Section:
    fa: str
    en: str
    blocks: list = field(default_factory=list)
    kicker_fa: str = ""
    kicker_en: str = ""


class Model:
    """One assignment report, authored bilingually."""

    def __init__(
        self,
        key: str,
        title_fa: str,
        title_en: str,
        subtitle_fa: str = "",
        subtitle_en: str = "",
        course_fa: str = "سیستم‌های عامل",
        course_en: str = "Operating Systems",
        author: str = "دانشجوی درس سیستم‌های عامل",
        author_en: str = "Operating Systems Student",
        date_fa: str = "",
        date_en: str = "",
        abstract_fa: str = "",
        abstract_en: str = "",
        keywords_fa: str = "",
        keywords_en: str = "",
        cover_figure: str = "",
    ):
        self.key = key
        self.title_fa = title_fa
        self.title_en = title_en
        self.subtitle_fa = subtitle_fa
        self.subtitle_en = subtitle_en
        self.course_fa = course_fa
        self.course_en = course_en
        self.author = author
        self.author_en = author_en
        self.date_fa = date_fa
        self.date_en = date_en
        self.abstract_fa = abstract_fa
        self.abstract_en = abstract_en
        self.keywords_fa = keywords_fa
        self.keywords_en = keywords_en
        self.cover_figure = cover_figure
        self.front_blocks: list = []      # placed right after abstract
        self.sections: list[Section] = []
        self.references: list[tuple[str, str]] = []
        self.appendix: list[Section] = []

    def section(self, fa, en, blocks, kicker_fa="", kicker_en=""):
        self.sections.append(Section(fa, en, blocks, kicker_fa, kicker_en))
        return self

    def references_list(self, items):
        self.references = items
        return self

    def appendix_section(self, fa, en, blocks):
        self.appendix.append(Section(fa, en, blocks))
        return self


# ----------------------------------------------------------------------------- code extraction
_CODE_CACHE: dict[str, list[str]] = {}


def read_code(path: str) -> list[str]:
    path = os.path.abspath(path)
    if path not in _CODE_CACHE:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            _CODE_CACHE[path] = fh.read().splitlines()
    return _CODE_CACHE[path]


def code_lines(block) -> tuple[list[str], int]:
    """Return the listing lines and the first line number (1-based)."""
    if "text" in block:
        return block["text"].splitlines(), 1
    lines = read_code(block["path"])
    start = block.get("start") or 1
    end = block.get("end") or len(lines)
    start = max(1, min(start, len(lines)))
    end = max(start, min(end, len(lines)))
    return lines[start - 1 : end], start


PY_KEYWORDS = {
    "def", "class", "return", "if", "elif", "else", "for", "while", "in", "not", "and", "or",
    "import", "from", "as", "with", "try", "except", "finally", "raise", "yield", "lambda",
    "pass", "break", "continue", "global", "None", "True", "False", "assert", "del", "is",
}
C_KEYWORDS = {
    "int", "char", "float", "double", "void", "return", "if", "else", "for", "while", "do",
    "struct", "typedef", "unsigned", "long", "short", "const", "static", "sizeof", "break",
    "continue", "switch", "case", "default", "enum", "union", "goto", "extern", "volatile",
    "include", "define", "ifdef", "endif", "pthread_t", "pthread_mutex_t", "pthread_cond_t",
}
BASH_KEYWORDS = {"for", "do", "done", "if", "then", "else", "fi", "while", "echo", "export", "cd", "function"}


def guess_lang(path: str, explicit: str | None = None) -> str:
    if explicit:
        return explicit
    ext = os.path.splitext(path or "")[1].lower()
    return {".py": "python", ".c": "c", ".h": "c", ".sh": "bash", ".json": "json", ".txt": "text"}.get(ext, "text")


def keywords_for(lang: str) -> set[str]:
    return {"python": PY_KEYWORDS, "c": C_KEYWORDS, "bash": BASH_KEYWORDS}.get(lang, set())


_TOKEN_RE = re.compile(
    r"(?P<comment>#.*|//.*|/\*.*?\*/|--.*$)"
    r"|(?P<string>\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*')"
    r"|(?P<num>\b\d+(?:\.\d+)?\b)"
    r"|(?P<word>[A-Za-z_][A-Za-z_0-9]*|\d)"
    r"|(?P<space>\s+)"
    r"|(?P<other>.)",
    re.S,
)


def tokenize_line(line: str, lang: str):
    kws = keywords_for(lang)
    out = []
    for m in _TOKEN_RE.finditer(line):
        kind = m.lastgroup
        text = m.group()
        if kind == "word":
            if text in kws:
                out.append(("kw", text))
            elif text in ("0", "1") or text.isdigit():
                out.append(("num", text))
            else:
                out.append(("code", text))
        elif kind == "num":
            out.append(("num", text))
        elif kind == "space":
            out.append(("space", text))
        elif kind == "comment":
            out.append(("comment", text))
        elif kind == "string":
            out.append(("string", text))
        else:
            out.append(("code", text))
    return out
