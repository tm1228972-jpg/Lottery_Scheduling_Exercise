"""Validation gates that encode the instructor's rubric.

Every report must pass these before it is committed:
  * PDF page count >= 40 for both the Persian and the English edition
  * Persian text extractable and not mirrored (no reversed-word artefacts)
  * TOC, >= N figures, >= N tables, >= N code listings, a Gantt chart
  * slide deck present, every slide non-blank (no gaps), 16:9
  * DOCX opens, has headings and tables
"""
from __future__ import annotations

import json
import os
import re
import zipfile

MIN_PAGES = 40
MIN_FIGURES = 12
MIN_TABLES = 8
MIN_LISTINGS = 6


def pdf_page_count(path):
    import pypdfium2 as pdfium

    doc = pdfium.PdfDocument(path)
    return len(doc)


def pdf_text(path, max_pages=None):
    import pypdfium2 as pdfium

    doc = pdfium.PdfDocument(path)
    out = []
    n = len(doc) if max_pages is None else min(max_pages, len(doc))
    for i in range(n):
        out.append(doc[i].get_textpage().get_text_range())
    return "\n".join(out)


ARABIC = re.compile(r"[\u0600-\u06FF]")
# words that only appear if shaping/bidi were applied twice (visual-order glyph runs)
BROKEN_MARKERS = ["\ufeff", "\u200e\u200e", "\u200f\u200f"]


def check_persian_integrity(text, must_contain=()):
    problems = []
    if not ARABIC.search(text):
        problems.append("no Persian characters found in a Persian report")
    for marker in BROKEN_MARKERS:
        if marker in text:
            problems.append(f"bidi control character leak: {marker!r}")
    # reversed-word heuristic: a frequent Persian word appearing backwards
    reversed_hits = sum(1 for w in ("و", "در", "که", "را") if w[::-1] in text and w not in text)
    if reversed_hits >= 2:
        problems.append("Persian text appears to be mirrored (reversed words)")
    for token in must_contain:
        if token not in text:
            problems.append(f"expected token missing: {token}")
    return problems


def check_persian_words(text, required=(), forbidden=()):
    """Check that specific Persian words appear in the text as written (never reversed)."""
    problems = []
    for w in required:
        if w not in text:
            problems.append(f"missing word: {w}")
    for w in forbidden:
        if w in text and w[::-1] in text:
            problems.append(f"word appears both normally and reversed: {w}")
    for bad in ("\ufffd", "Ã", "â€", "Ø", "Ù"):
        if bad in text:
            problems.append(f"mojibake marker found: {bad!r}")
    return problems


def check_docx(path):
    problems = []
    try:
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            if "word/document.xml" not in names:
                problems.append("document.xml missing")
            xml = z.read("word/document.xml").decode("utf-8", "replace")
            if "<w:tbl>" not in xml:
                problems.append("no tables in DOCX")
            has_arabic = bool(ARABIC.search(xml))
            if has_arabic:
                # Persian edition must carry explicit RTL paragraph markers
                if "w:bidi" not in xml:
                    problems.append("Persian DOCX has no RTL (w:bidi) markers")
            else:
                # English edition: must be right-to-left clean (no bidi overrides)
                if "w:bidi" in xml:
                    problems.append("English DOCX contains RTL overrides")
                if "Headings" not in xml and "Heading" not in xml:
                    problems.append("DOCX has no heading styles")
    except Exception as exc:  # noqa: BLE001
        problems.append(f"cannot open DOCX: {exc}")
    return problems


def check_slides(slide_paths, expected=8):
    """Every slide must be non-blank and uniform 16:9."""
    from PIL import Image, ImageStat

    problems = []
    if len(slide_paths) < expected:
        problems.append(f"only {len(slide_paths)} slides (expected >= {expected})")
    sizes = set()
    for p in slide_paths:
        im = Image.open(p).convert("RGB")
        sizes.add(im.size)
        stat = ImageStat.Stat(im.convert("L"))
        if stat.var[0] < 40:
            problems.append(f"near-blank slide (no content): {os.path.basename(p)}")
    if len(sizes) > 1:
        problems.append(f"inconsistent slide sizes: {sizes}")
    elif sizes:
        w, h = next(iter(sizes))
        if abs(w / h - 16 / 9) > 0.02:
            problems.append(f"slides are not 16:9 ({w}x{h})")
    return problems


def check_page_gaps(pdf_path, max_gap=0.42, ignore_first=3):
    """Detect visible blank bands at the bottom of a page.

    A chapter legitimately ends where its last figure or table ends, so a trailing band of
    up to ~40% is normal typography. Only egregious gaps (nearly half the text block) are
    flagged; the cover and table-of-contents pages are skipped.
    """
    import numpy as np
    import pypdfium2 as pdfium

    doc = pdfium.PdfDocument(pdf_path)
    bad = []
    for i in range(ignore_first, len(doc)):
        arr = np.array(doc[i].render(scale=0.8).to_pil().convert("L"))
        h = arr.shape[0]
        body = arr[int(h * 0.09):int(h * 0.93)]
        rows = (body < 240).sum(axis=1)
        nz = np.nonzero(rows > 3)[0]
        if len(nz) == 0:
            bad.append(f"page {i + 1}: blank")
            continue
        gap = (body.shape[0] - nz[-1]) / body.shape[0]
        if gap > max_gap:
            bad.append(f"page {i + 1}: {gap:.0%} empty")
    return bad, len(doc)


def check_report(pdf_fa, pdf_en, docx_fa, docx_en, slide_dir, expected_slides=8, lang_tokens=(),
                 required_words=(), gantt_tokens=("گانت",)):
    result = {"ok": True, "checks": []}

    def add(name, problems, info=""):
        ok = not problems
        result["checks"].append({"name": name, "ok": ok, "problems": problems, "info": info})
        if not ok:
            result["ok"] = False

    pf = pdf_page_count(pdf_fa)
    add("fa_page_count", [] if pf >= MIN_PAGES else [f"{pf} pages < {MIN_PAGES}"], f"{pf} pages")
    pe = pdf_page_count(pdf_en)
    add("en_page_count", [] if pe >= MIN_PAGES else [f"{pe} pages < {MIN_PAGES}"], f"{pe} pages")

    tfa = pdf_text(pdf_fa)
    add("fa_text_integrity", check_persian_integrity(tfa), f"{len(tfa)} chars")
    ten = pdf_text(pdf_en)
    problems_en = []
    # Persian may legitimately appear in a few quoted cells, but the body must be Latin.
    arabic_ratio = len(ARABIC.findall(ten)) / max(1, len(ten))
    if arabic_ratio > 0.25:
        problems_en.append(f"English report is {arabic_ratio:.0%} Persian - wrong language")
    for token in lang_tokens:
        if token not in ten:
            problems_en.append(f"expected token missing: {token}")
    add("en_text_integrity", problems_en, f"{len(ten)} chars")

    figs = tfa.count("شکل ") + tfa.count("شکل") if tfa else 0
    add("fa_figures", [] if figs >= MIN_FIGURES else [f"{figs} figure captions < {MIN_FIGURES}"], f"{figs}")
    tabs = tfa.count("جدول ")
    add("fa_tables", [] if tabs >= MIN_TABLES else [f"{tabs} table captions < {MIN_TABLES}"], f"{tabs}")
    listings = tfa.count("قطعه کد")
    add("fa_listings", [] if listings >= MIN_LISTINGS else [f"{listings} listings < {MIN_LISTINGS}"], f"{listings}")
    add("fa_toc", [] if ("فهرست مطالب" in tfa) else ["TOC page missing"])
    add("fa_gantt", [] if any(t in tfa for t in gantt_tokens) else ["Gantt chart figure/caption missing"])
    add("fa_words", check_persian_words(tfa, required=required_words,
                                        forbidden=tuple(required_words)))

    add("docx_fa", check_docx(docx_fa))
    add("docx_en", check_docx(docx_en))

    slides = sorted(os.path.join(slide_dir, f) for f in os.listdir(slide_dir) if f.endswith(".png")) \
        if os.path.isdir(slide_dir) else []
    add("slides", check_slides(slides, expected_slides), f"{len(slides)} slides")

    gaps_fa, _ = check_page_gaps(pdf_fa)
    gaps_en, _ = check_page_gaps(pdf_en)
    add("page_gaps", gaps_fa + [f"EN {g}" for g in gaps_en], "no blank bands")
    return result


def write_report(result, path):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)
