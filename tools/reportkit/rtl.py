"""Persian/Arabic text utilities: shaping, bidi, digit conversion, wrapping."""
from __future__ import annotations

import functools
import re

import arabic_reshaper
from bidi.algorithm import get_display

ARABIC_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]")
PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
LATIN_DIGITS = "0123456789"

ZWNJ = "\u200c"
LRE = "\u202a"
PDF_ = "\u202c"


def balance_bidi(text: str) -> str:
    """Wrap Latin runs (and their adjacent bracketed content) in LRE/PDF isolates.

    The Persian press does this so that "الگوریتم (Lottery Scheduling) بلیت"
    keeps the parentheses around the Latin phrase instead of mirroring them.
    """
    import re

    # Latin word runs with optional bracketed Latin phrase or parentheses
    # a Latin run that optionally starts with "(" and ends with ")"
    pattern = re.compile(r"\([A-Za-z][A-Za-z0-9_\-+*/().:;, ']*\)|[A-Za-z][A-Za-z0-9_\-+*/.():;,']*[A-Za-z0-9_]")
    out = []
    last = 0
    for m in pattern.finditer(text):
        start, end = m.start(), m.end()
        if start > last:
            out.append(text[last:start])
        core = m.group(0)
        if "\u202a" in core:
            out.append(core)
        else:
            out.append(LRE + core + PDF_)
        last = end
    out.append(text[last:])
    return "".join(out)


_reshaper = arabic_reshaper.ArabicReshaper(
    configuration={"delete_harakat": False, "support_ligatures": True, "use_unshaped_instead_of_isolated": True}
)


@functools.lru_cache(maxsize=20000)
def shape(text: str, isolate_latin: bool = False) -> str:
    """Reshape Arabic/Persian and apply the bidi algorithm -> visual order string.

    Zero-width non-joiners (U+200C, Persian "nim-fasele") are removed by the
    shaper. We protect them with a private-use placeholder around reshaping so
    that words such as "زمان‌بندی" keep their correct half-space spelling.
    """
    if not text:
        return ""
    if isolate_latin:
        text = _isolate_latin_phrases(text)
    MARK = "\ue000"
    LUT = {"\u202a": "\ue001", "\u202c": "\ue002"}
    protected = text.replace(ZWNJ, MARK)
    for k, v in LUT.items():
        protected = protected.replace(k, v)
    visual = get_display(_reshaper.reshape(protected))
    visual = visual.replace(MARK, ZWNJ)
    for k, v in LUT.items():
        visual = visual.replace(v, k)
    return visual


def has_arabic(text: str) -> bool:
    return bool(ARABIC_RE.search(text or ""))


def to_fa_digits(text: str) -> str:
    return (text or "").translate(str.maketrans(LATIN_DIGITS, PERSIAN_DIGITS))


def to_en_digits(text: str) -> str:
    return (text or "").translate(str.maketrans(PERSIAN_DIGITS, LATIN_DIGITS))


def fmt(n, lang: str = "fa") -> str:
    """Format a number with thousands separators in the requested language."""
    if isinstance(n, float):
        s = f"{n:,.2f}".rstrip("0").rstrip(".")
    else:
        s = f"{n:,}"
    return to_fa_digits(s) if lang == "fa" else s


_LATIN_PHRASE = None


def _isolate_latin_phrases(text: str) -> str:
    """Wrap "(Latin phrase)" and bare Latin words in LRE/PDF markers."""
    global _LATIN_PHRASE
    import re as _re

    if _LATIN_PHRASE is None:
        _LATIN_PHRASE = _re.compile(r"\([A-Za-z][A-Za-z0-9_\-+*/().:;, ']*\)|[A-Za-z][A-Za-z0-9_\-+*/.]*[A-Za-z0-9_]")
    out, last = [], 0
    for m in _LATIN_PHRASE.finditer(text):
        out.append(text[last:m.start()])
        out.append(LRE + m.group(0) + PDF_)
        last = m.end()
    out.append(text[last:])
    return "".join(out)
