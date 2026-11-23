"""Word (.docx) writer: true RTL for Persian, LTR for English, same content model."""
from __future__ import annotations

import os

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from . import theme
from .model import code_lines, guess_lang

FA_FONT = "Vazirmatn"
LATIN_FONT = "Vazirmatn"
MONO_FONT = "Consolas"


def _rgb(h):
    h = h.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _set_rtl_paragraph(p, rtl=True):
    pPr = p._p.get_or_add_pPr()
    bidi = OxmlElement("w:bidi")
    bidi.set(qn("w:val"), "1" if rtl else "0")
    pPr.append(bidi)


def _set_run_fonts(run, font=FA_FONT, size=None, bold=None, color=None, mono=False):
    run.font.name = MONO_FONT if mono else font
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    name = MONO_FONT if mono else font
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rFonts.set(qn(attr), name)
    run.font.rtl = True if not mono else False
    if size:
        run.font.size = Pt(size)
        rPr2 = run._element.get_or_add_rPr()
        szcs = OxmlElement("w:szCs")
        szcs.set(qn("w:val"), str(int(size * 2)))
        rPr2.append(szcs)
    if bold is not None:
        run.font.bold = bold
    if color:
        run.font.color.rgb = _rgb(color)


def _shade(cell, hex_fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_fill.lstrip("#"))
    tcPr.append(shd)


def _cell_margins(table, top=40, bottom=40, left=80, right=80):
    tblPr = table._tbl.tblPr
    mar = OxmlElement("w:tblCellMar")
    for side, val in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:w"), str(val))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tblPr.append(mar)


def _borders(table):
    tblPr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), theme.RULE.lstrip("#"))
        borders.append(el)
    tblPr.append(borders)


def _add_toc_field(doc, rtl):
    """Insert a real Word TOC field (updates on open with F9)."""
    p = doc.add_paragraph()
    if rtl:
        _set_rtl_paragraph(p, True)
    run = p.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = r' TOC \o "1-2" \h \z \u '
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    placeholder = OxmlElement("w:t")
    placeholder.text = "Right-click and choose Update Field to build the table of contents."
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    for el in (fld_begin, instr, fld_sep, placeholder, fld_end):
        run._r.append(el)


class DocxWriter:
    def __init__(self, model, out_path, lang):
        self.m, self.out, self.lang = model, out_path, lang
        self.fa = lang == "fa"
        self.doc = Document()
        self._setup()

    # ------------------------------------------------------------------ setup
    def _setup(self):
        d = self.doc
        sec = d.sections[0]
        sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
        sec.left_margin = sec.right_margin = Cm(2.2)
        sec.top_margin = Cm(2.0)
        sec.bottom_margin = Cm(2.0)
        style = d.styles["Normal"]
        style.font.name = FA_FONT
        style.font.size = Pt(10.5)
        rPr = style.element.get_or_add_rPr()
        rFonts = rPr.find(qn("w:rFonts"))
        if rFonts is None:
            rFonts = OxmlElement("w:rFonts")
            rPr.append(rFonts)
        for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rFonts.set(qn(attr), FA_FONT)
        # page numbers in the footer
        footer = sec.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT if self.fa else WD_ALIGN_PARAGRAPH.LEFT
        run = fp.add_run()
        _set_run_fonts(run, size=8.4, color=theme.MUTED)
        fld = OxmlElement("w:fldSimple")
        fld.set(qn("w:instr"), "PAGE")
        fp._p.append(fld)

    def para(self, text="", size=10.5, bold=False, color=theme.INK, align=None, mono=False,
             space_after=6, space_before=0, indent=0):
        p = self.doc.add_paragraph()
        if self.fa:
            _set_rtl_paragraph(p, True)
        p.alignment = align or (WD_ALIGN_PARAGRAPH.JUSTIFY if not self.fa else WD_ALIGN_PARAGRAPH.JUSTIFY)
        pf = p.paragraph_format
        pf.space_after = Pt(space_after)
        pf.space_before = Pt(space_before)
        pf.line_spacing = 1.32
        if indent:
            pf.left_indent = Cm(indent)
        self._runs(p, text, size=size, bold=bold, color=color, mono=mono)
        return p

    def _runs(self, p, text, size=10.5, bold=False, color=theme.INK, mono=False):
        import re

        from .richtext import parse_inline

        for run in parse_inline(text or ""):
            r = p.add_run(run.text)
            _set_run_fonts(r, size=size - (1.4 if run.mono else 0), bold=bold or run.bold,
                           color=(theme.ACCENT if run.mono else color), mono=run.mono)

    def heading(self, text, level=1, page_break=False, number=""):
        if page_break:
            self.doc.add_page_break()
        p = self.doc.add_paragraph(style=f"Heading {level}")
        if self.fa:
            _set_rtl_paragraph(p, True)
        label = f"{number}  {text}" if number else text
        r = p.add_run(label)
        size = {1: 17, 2: 13, 3: 11}[level]
        _set_run_fonts(r, size=size, bold=True,
                       color=theme.ACCENT_DARK if level == 1 else (theme.INK if level == 2 else theme.ACCENT))
        p.paragraph_format.space_before = Pt(12 if level == 1 else 8)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        return p

    # ------------------------------------------------------------------ blocks
    def _translate_cell(self, fa_text, en_text):
        import re as _re

        from .tables import _as_latin

        if self.fa:
            return fa_text
        if en_text and not _re.search(r"[\u0600-\u06FF]", en_text):
            return en_text
        latin = _as_latin(en_text or "") or _as_latin(fa_text)
        if latin:
            return latin
        from .i18n import translate

        tr = translate(fa_text)
        if tr is None:
            raise ValueError(f"DOCX: missing English translation for table cell {fa_text!r}")
        return tr

    def _translate_key(self, fa_text, en_text):
        """Key labels in definition tables: strip a Persian-only label to its English part."""
        import re as _re

        if self.fa:
            return fa_text
        if en_text and not _re.search(r"[\u0600-\u06FF]", en_text):
            return en_text
        from .i18n import translate

        tr = translate(fa_text)
        if tr is not None:
            return tr
        # labels like "کلاینت (Client)" already carry the English term in parentheses
        m = _re.search(r"\(([A-Za-z][^)]*)\)", fa_text)
        if m:
            return m.group(1).strip()
        raise ValueError(f"DOCX: missing English label for {fa_text!r}")

    def table(self, spec, number=""):
        fa = self.fa
        head = spec["head"][0 if fa else 1]
        rows = [[self._translate_cell(c[0], c[1]) for c in row] for row in spec["rows"]]
        cap = spec["cap"][0 if fa else 1]
        label = {"fa": "جدول", "en": "Table"}[self.lang]
        self.para(f"{label} {number}: {cap}" if number else f"{label}: {cap}",
                  size=9, bold=True, color=theme.MUTED,
                  align=WD_ALIGN_PARAGRAPH.RIGHT if fa else WD_ALIGN_PARAGRAPH.LEFT, space_after=3)
        t = self.doc.add_table(rows=1, cols=len(head))
        t.alignment = WD_TABLE_ALIGNMENT.RIGHT if fa else WD_TABLE_ALIGNMENT.LEFT
        t.style = "Table Grid"
        _borders(t)
        _cell_margins(t)
        hdr = t.rows[0].cells
        for i, h in enumerate(head):
            hdr[i].text = ""
            p = hdr[i].paragraphs[0]
            if fa:
                _set_rtl_paragraph(p, True)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(str(h))
            _set_run_fonts(r, size=9, bold=True, color="#ffffff")
            _shade(hdr[i], theme.ACCENT)
        # mark header row to repeat
        trPr = t.rows[0]._tr.get_or_add_trPr()
        th = OxmlElement("w:tblHeader")
        trPr.append(th)
        for ri, row in enumerate(rows):
            cells = t.add_row().cells
            for i, v in enumerate(row):
                cells[i].text = ""
                p = cells[i].paragraphs[0]
                if fa:
                    _set_rtl_paragraph(p, True)
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r = p.add_run(str(v))
                _set_run_fonts(r, size=8.8)
                if ri % 2 == 1:
                    _shade(cells[i], theme.ZEBRA)
        if spec.get("note"):
            self.para(spec["note"][0 if fa else 1], size=8.4, color=theme.MUTED,
                      align=WD_ALIGN_PARAGRAPH.RIGHT if fa else WD_ALIGN_PARAGRAPH.LEFT)
        self.para("", size=4, space_after=2)

    def figure(self, path, cap, number="", width_cm=16.0):
        fa = self.fa
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        if os.path.exists(path):
            run.add_picture(path, width=Cm(width_cm))
        label = {"fa": "شکل", "en": "Figure"}[self.lang]
        self.para(f"{label} {number}: {cap}" if number else f"{label}: {cap}", size=8.8,
                  color=theme.MUTED, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)

    def code(self, block, number=""):
        fa = self.fa
        label = {"fa": "قطعه کد", "en": "Listing"}[self.lang]
        cap = block["cap"][0 if fa else 1]
        self.para(f"{label} {number}: {cap}" if number else f"{label}: {cap}", size=8.6, bold=True,
                  color=theme.MUTED, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=2)
        lines, start = code_lines(block)
        t = self.doc.add_table(rows=1, cols=1)
        t.alignment = WD_TABLE_ALIGNMENT.LEFT
        cell = t.rows[0].cells[0]
        _shade(cell, "#f7f9fb")
        _borders(t)
        _cell_margins(t, 60, 60, 100, 100)
        cell.text = ""
        first = True
        fname = block.get("label", (None, None))[1] or (
            block["path"].split("/")[-1] if "path" in block else "listing"
        )
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(f"{fname}   ({guess_lang(block.get('path'), block.get('lang')).upper()})")
        _set_run_fonts(r, size=7.6, bold=True, color=theme.ACCENT, mono=True)
        for i, line in enumerate(lines):
            p = cell.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            rn = p.add_run(f"{start + i:>4}  ")
            _set_run_fonts(rn, size=7.2, color="#9aa7b2", mono=True)
            r2 = p.add_run(line if line.strip() else " ")
            _set_run_fonts(r2, size=7.2, color="#24292f", mono=True)
        self.para("", size=4, space_after=2)

    def callout(self, title, body, kind="note"):
        fill, fg = {
            "note": ("#e8f3f9", "#0b6e99"),
            "warn": ("#fdf0e6", "#c1440e"),
            "key": ("#eaf5ee", "#2e7d4f"),
            "quote": ("#f4f1f8", "#6a4c93"),
        }[kind]
        t = self.doc.add_table(rows=1, cols=1)
        t.style = "Table Grid"
        _borders(t)
        _cell_margins(t, 90, 90, 120, 120)
        cell = t.rows[0].cells[0]
        _shade(cell, fill)
        cell.text = ""
        p = cell.paragraphs[0]
        if self.fa:
            _set_rtl_paragraph(p, True)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT if self.fa else WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(title)
        _set_run_fonts(r, size=9.6, bold=True, color=fg)
        p2 = cell.add_paragraph()
        if self.fa:
            _set_rtl_paragraph(p2, True)
        p2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r2 = p2.add_run(body)
        _set_run_fonts(r2, size=9.2)
        self.para("", size=4, space_after=2)

    def bullets(self, items, ordered=False):
        for i, (ifa, ien) in enumerate(items, 1):
            txt = ifa if self.fa else ien
            mark = "•" if not ordered else f"{i}."
            p = self.doc.add_paragraph()
            if self.fa:
                _set_rtl_paragraph(p, True)
            p.paragraph_format.left_indent = Cm(0.7)
            p.paragraph_format.space_after = Pt(2)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            self._runs(p, f"{mark} {txt}", size=10.2)

    # ------------------------------------------------------------------ build
    def build(self):
        m, fa = self.m, self.fa
        # ---------------- cover page
        for _ in range(3):
            self.para("", size=8)
        p = self.doc.add_paragraph()
        if fa:
            _set_rtl_paragraph(p, True)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(m.course_fa if fa else m.course_en)
        _set_run_fonts(r, size=12, color=theme.MUTED)
        p = self.doc.add_paragraph()
        if fa:
            _set_rtl_paragraph(p, True)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(m.title_fa if fa else m.title_en)
        _set_run_fonts(r, size=26, bold=True, color=theme.ACCENT_DARK)
        if (m.subtitle_fa if fa else m.subtitle_en):
            p = self.doc.add_paragraph()
            if fa:
                _set_rtl_paragraph(p, True)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(m.subtitle_fa if fa else m.subtitle_en)
            _set_run_fonts(r, size=12.5, color=theme.ACCENT)
        for _ in range(4):
            self.para("", size=8)
        t = self.doc.add_table(rows=0, cols=2)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for (kfa, ken), v in [(("نگارنده", "Author"), (m.author, m.author_en)),
                              (("درس", "Course"), (m.course_fa, m.course_en)),
                              (("تاریخ", "Date"), (m.date_fa, m.date_en))]:
            row = t.add_row().cells
            row[0].text = ""
            row[1].text = ""
            r1 = row[0].paragraphs[0].add_run(kfa if fa else ken)
            _set_run_fonts(r1, size=10, bold=True, color=theme.MUTED)
            r2 = row[1].paragraphs[0].add_run(v[0] if fa else v[1])
            _set_run_fonts(r2, size=10.5)
        self.doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

        # ---------------- TOC
        self.heading("فهرست مطالب" if fa else "Table of Contents", 1)
        self.para("Word updates this field automatically: press Ctrl+A then F9 (or right-click → Update Field)."
                  if not fa else
                  "این فهرست یک فیلد Word است؛ برای به‌روزرسانی کلیدهای Ctrl+A و سپس F9 را بزنید.",
                  size=8.6, color=theme.MUTED)
        _add_toc_field(self.doc, fa)
        self.doc.add_page_break()

        # ---------------- abstract
        self.heading("چکیده" if fa else "Abstract", 1)
        self.para(m.abstract_fa if fa else m.abstract_en, size=10.6)
        kw = m.keywords_fa if fa else m.keywords_en
        if kw:
            self.para(("کلیدواژه‌ها: " if fa else "Keywords: ") + kw, size=9.6, color=theme.MUTED)
        counters = {"fig": 0, "tab": 0, "code": 0}
        for b in m.front_blocks:
            self.block(b, counters)

        for i, sec in enumerate(m.sections, 1):
            self.heading(sec.fa if fa else sec.en, 1, page_break=True, number=str(i))
            kicker = sec.kicker_fa if fa else sec.kicker_en
            if kicker:
                self.para(kicker, size=9, color=theme.MUTED)
            sub = 0
            for b in sec.blocks:
                if b["type"] == "h2":
                    sub += 1
                    self.heading(b["fa"] if fa else b["en"], 2, number=f"{i}.{sub}")
                    continue
                self.block(b, counters)

        for i, sec in enumerate(m.appendix, 1):
            mark = ("پ" + str(i)) if fa else f"A{i}"
            self.heading(sec.fa if fa else sec.en, 1, page_break=True, number=mark)
            sub = 0
            for b in sec.blocks:
                if b["type"] == "h2":
                    sub += 1
                    self.heading(b["fa"] if fa else b["en"], 2, number=f"{mark}.{sub}")
                    continue
                self.block(b, counters)

        if m.references:
            self.heading("منابع و مراجع" if fa else "References", 1, page_break=True)
            for i, (rfa, ren) in enumerate(m.references, 1):
                self.para(f"[{i}]  " + (rfa if fa else ren), size=9.4, space_after=3)
        self.doc.save(self.out)
        return self.out

    def block(self, b, counters):
        fa = self.fa
        t = b["type"]
        if t == "p":
            self.para(b["fa"] if fa else b["en"])
        elif t == "lead":
            self.para(b["fa"] if fa else b["en"], size=11.2, color="#33414f", space_after=9)
        elif t == "h2":
            self.heading(b["fa"] if fa else b["en"], 2)
        elif t == "h3":
            self.heading(b["fa"] if fa else b["en"], 3)
        elif t in ("ul", "ol"):
            self.bullets(b["items"], ordered=(t == "ol"))
        elif t == "table":
            counters["tab"] += 1
            self.table(b, number=str(counters["tab"]))
        elif t == "figure":
            counters["fig"] += 1
            self.figure(b["path"] if fa else b.get("en_path") or b["path"],
                        b["cap"][0 if fa else 1], number=str(counters["fig"]),
                        width_cm=16.2 * (b.get("width") or 0.92) / 0.92)
        elif t == "code":
            counters["code"] += 1
            self.code(b, number=str(counters["code"]))
        elif t == "note":
            self.callout(b["title"][0 if fa else 1], b["body"][0 if fa else 1], b.get("kind", "note"))
        elif t == "quote":
            self.callout(b["src"][0 if fa else 1] or "—", b["fa"] if fa else b["en"], "quote")
        elif t == "formula":
            self.para(b["fa"] if fa else b["en"], size=10, mono=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        elif t == "kv":
            tb = self.doc.add_table(rows=0, cols=2)
            tb.style = "Table Grid"
            _borders(tb)
            for (kfa, ken), (vfa, ven) in [(p[0], p[1]) for p in b["pairs"]]:
                row = tb.add_row().cells
                row[0].text = ""
                row[1].text = ""
                r1 = row[0].paragraphs[0].add_run(kfa if fa else self._translate_key(kfa, ken))
                _set_run_fonts(r1, size=9, bold=True, color=theme.ACCENT_DARK)
                r2 = row[1].paragraphs[0].add_run(vfa if fa else (ven if ven else vfa))
                _set_run_fonts(r2, size=9)
            self.para("", size=4, space_after=2)
        elif t == "pagebreak":
            self.doc.add_page_break()
        elif t == "spacer":
            self.para("", size=b["h"] / 3)


def write(model, out_path, lang):
    return DocxWriter(model, out_path, lang).build()
