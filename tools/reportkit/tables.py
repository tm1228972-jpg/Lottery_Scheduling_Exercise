"""Bilingual tables: RTL for Persian, LTR for English, zebra rows, captions."""
from __future__ import annotations

import re

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import KeepTogether, Paragraph, Spacer, Table, TableStyle

from . import theme
from .rtl import shape, has_arabic, to_fa_digits
from .fonts import register_reportlab_fonts


def _cell_para(text, lang, bold=False, size=8.6, align="center", color=theme.INK):
    register_reportlab_fonts()
    # detect the cell's own script so a Persian cell inside an English table is never mirrored
    if lang == "fa" or has_arabic(text):
        text = to_fa_digits(text)
        if has_arabic(text):
            text = shape(text)
    al = {"left": 0, "center": 1, "right": 2}[align]
    if has_arabic(text) and align == "left":
        al = 2
    st = ParagraphStyle(
        f"cell{lang}{bold}{size}",
        fontName="Vazir-Bold" if bold else "Vazir",
        fontSize=size,
        leading=size * 1.34,
        alignment=al,
        textColor=colors.HexColor(color),
        wordWrap=None if lang == "en" else "RTL",
    )
    # keep the visual order stable: shaped text must never be re-wrapped by reportlab
    safe = text.replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(safe, st)


def caption(text, lang, kind="table"):
    register_reportlab_fonts()
    label = {"table": ("جدول", "Table"), "figure": ("شکل", "Figure"), "code": ("قطعه کد", "Listing")}[kind][0 if lang == "fa" else 1]
    prefix = label
    num = text[0] if isinstance(text, tuple) else ""
    body = text[1] if isinstance(text, tuple) else text
    raw = f"{prefix} {num}: {body}" if num else f"{prefix}: {body}"
    if lang == "fa":
        raw = to_fa_digits(raw)
        raw = shape(raw)
        al = 2
    else:
        al = 0
    st = ParagraphStyle(
        "cap", fontName="Vazir-Bold" if lang == "fa" else "Vazir-Bold", fontSize=8.8, leading=13,
        alignment=al, textColor=colors.HexColor(theme.MUTED),
    )
    return Paragraph(raw.replace("<", "&lt;"), st)


def _as_latin(text):
    """Persian digits and neutral punctuation translate to Latin with no lookup needed."""
    t = str(text).strip()
    if not t:
        return ""
    latin = to_fa_digits_to_latin(t)
    if not re.search(r"[\u0600-\u06FF]", latin):
        return latin
    return ""


def to_fa_digits_to_latin(text):
    fa = "۰۱۲۳۴۵۶۷۸۹"
    out = text.translate(str.maketrans(fa, "0123456789")).replace("٫", ".")
    return out.replace("\u066a", "%")


def _needs_translation(cell_text):
    return bool(re.search(r"[\u0600-\u06FF]", str(cell_text)))


def build_table(spec, lang, avail_width, number=""):
    """Returns a list of flowables (caption + table)."""
    fa = lang == "fa"
    head = spec["head"][0 if fa else 1]
    head = [to_fa_digits(h) if fa else h for h in head]
    rows = []
    for row in spec["rows"]:
        out_row = []
        for c in row:
            if fa:
                out_row.append(c[0])
            else:
                en = _as_latin(c[1]) or _as_latin(c[0])
                if _needs_translation(en) or en.strip() == "":
                    from .i18n import translate

                    tr = translate(c[0])
                    if tr is None:
                        raise ValueError(
                            f"table '{spec['cap'][1]}': no English translation for cell {c[0]!r}; "
                            "add it to tools/reportkit/i18n_cells.json"
                        )
                    en = tr
                out_row.append(en)
        rows.append(out_row)
    size = spec.get("font") or 8.6
    ncols = len(head)
    widths = spec.get("widths")
    if not widths:
        widths = [1.0 / ncols] * ncols
    total = sum(widths)
    col_w = [w / total * avail_width for w in widths]
    data = [[_cell_para(h, lang, bold=True, size=size, align="center", color="#ffffff") for h in head]]
    for row in rows:
        data.append([_cell_para(v, lang, size=size) for v in row])
    t = Table(data, colWidths=col_w, repeatRows=1, hAlign="RIGHT" if fa else "LEFT")
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(theme.ACCENT)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor(theme.RULE)),
        ("TOPPADDING", (0, 0), (-1, -1), 3.4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor(theme.ZEBRA)))
    t.setStyle(TableStyle(style))
    flows = [caption((number, spec["cap"][0 if fa else 1]), lang), Spacer(1, 3), t]
    if spec.get("note"):
        flows.append(Spacer(1, 2))
        flows.append(_cell_para(spec["note"][0 if fa else 1], lang, size=size - 0.6, align="right" if fa else "left", color=theme.MUTED))
    flows.append(Spacer(1, 9))
    return flows
