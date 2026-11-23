"""PDF assembler: cover, abstract, TOC, sections, figures, code, references, headers/footers."""
from __future__ import annotations

import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    CondPageBreak,
    BaseDocTemplate,
    CondPageBreak,
    Frame,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
)

from . import theme
from .codeblock import CodeBlock
from .figures import Callout, Figure, KVBox, Rule
from .fonts import register_mono
from .richtext import RichText
from .rtl import shape, to_fa_digits
from .tables import build_table, caption

PAGE_W, PAGE_H = A4
MARGIN_L = MARGIN_R = 20 * mm
MARGIN_T = 22 * mm
MARGIN_B = 20 * mm

_STYLE_CACHE = {}


def styles(lang):
    if lang in _STYLE_CACHE:
        return _STYLE_CACHE[lang]
    fa = lang == "fa"
    s = {}
    s["body"] = ParagraphStyle(
        "body", fontName="Vazir", fontSize=11.5, leading=20.4, alignment=4,
        spaceBefore=0, spaceAfter=9.4, textColor=colors.HexColor(theme.INK),
    )
    s["lead"] = ParagraphStyle(
        "lead", fontName="Vazir", fontSize=11.9, leading=21.0, alignment=4,
        spaceAfter=11, textColor=colors.HexColor("#33414f"),
    )
    s["ch"] = ParagraphStyle(
        "ch", fontName="Vazir-Bold", fontSize=16.0, leading=23, alignment=2 if fa else 0,
        spaceBefore=0, spaceAfter=10, textColor=colors.HexColor(theme.ACCENT_DARK),
    )
    s["h2"] = ParagraphStyle(
        "h2", fontName="Vazir-Bold", fontSize=12.6, leading=18.6, alignment=2 if fa else 0,
        spaceBefore=9, spaceAfter=4.6, textColor=colors.HexColor(theme.INK),
    )
    s["h3"] = ParagraphStyle(
        "h3", fontName="Vazir-Bold", fontSize=11.2, leading=16.8, alignment=2 if fa else 0,
        spaceBefore=6, spaceAfter=3, textColor=colors.HexColor(theme.ACCENT),
    )
    s["bullet"] = ParagraphStyle(
        "bullet", fontName="Vazir", fontSize=11.2, leading=19.2, alignment=4,
        spaceAfter=4.0, textColor=colors.HexColor(theme.INK), leftIndent=6,
    )
    s["small"] = ParagraphStyle(
        "small", fontName="Vazir", fontSize=8.6, leading=13.2, alignment=2 if fa else 0,
        textColor=colors.HexColor(theme.MUTED),
    )
    _STYLE_CACHE[lang] = s
    return s


class ChapterHeading(Spacer):
    """Chapter title with accent rule; registers itself in the TOC."""

    def __init__(self, text, lang, level=0, number="", toc=True):
        super().__init__(1, 1)
        self.text = text
        self.lang = lang
        self.level = level
        self.number = number
        self.toc = toc
        self._para = None
        label = f"{number}  {text} " if number else text
        self._toc_label = shape(to_fa_digits(label)) if lang == "fa" else label

    def wrap(self, availWidth, availHeight):
        st = styles(self.lang)["ch" if self.level == 0 else "h2"]
        fa = self.lang == "fa"
        label = self.text
        if self.number:
            label = f"{self.number}  " + label
        if fa:
            label = shape(to_fa_digits(label))
        escaped = label.replace("<", "&lt;").replace(">", "&gt;")
        self._para = Paragraph(escaped, st)
        w, h = self._para.wrap(availWidth, availHeight)
        self.width, self.height = availWidth, h + (26 if self.level == 0 else 14)
        return (availWidth, self.height)

    def draw(self):
        fa = self.lang == "fa"
        c = self.canv
        h = self.height
        self._para.drawOn(c, 0, 0)
        c.setStrokeColor(colors.HexColor(theme.ACCENT if self.level == 0 else theme.RULE))
        c.setLineWidth(1.4 if self.level == 0 else 0.6)
        y = h - (7 if self.level == 0 else 4)
        if fa:
            c.line(self.width, y, self.width - (58 if self.level == 0 else 34), y)
        else:
            c.line(0, y, (58 if self.level == 0 else 34), y)


class TocFlow(Spacer):
    """Draws a table of contents from a precomputed entry list (level, label, page)."""

    def __init__(self, lang, entries=None, row_h=14.4, show_leaders=True):
        super().__init__(1, 1)
        self.lang = lang
        self.entries = entries or []
        self.row_h = row_h
        self.show_leaders = show_leaders

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        self.height = max(30, len(self.entries) * self.row_h + 4)
        # split across pages when there are many headings
        if self.height > availHeight and self.entries:
            fit = max(1, int((availHeight - 8) // self.row_h))
            self._split_at = fit
            self.height = min(self.height, availHeight - 2)
            return (availWidth, self.height)
        self._split_at = None
        return (availWidth, self.height)

    def split(self, availWidth, availHeight):
        if getattr(self, "_split_at", None):
            n = self._split_at
            head = TocFlow(self.lang, entries=self.entries[:n], row_h=self.row_h,
                           show_leaders=self.show_leaders)
            tail = TocFlow(self.lang, entries=self.entries[n:], row_h=self.row_h,
                           show_leaders=self.show_leaders)
            head._split_at = None
            return [head, tail]
        return []

    def draw(self):
        c = self.canv
        fa = self.lang == "fa"
        y = self.height - 11
        for level, label, page in self.entries:
            indent = 0 if level == 0 else 15
            if level == 0:
                c.setFillColor(colors.HexColor(theme.ACCENT_DARK))
                c.setFont("Vazir-Bold", 9.4)
                fs = 9.4
            else:
                c.setFillColor(colors.HexColor(theme.MUTED))
                c.setFont("Vazir", 8.6)
                fs = 8.6
            c.setStrokeColor(colors.HexColor(theme.RULE))
            c.setLineWidth(0.35)
            c.setDash(0.7, 1.7)
            page_s = to_fa_digits(str(page)) if fa else str(page)
            pw = c.stringWidth(page_s, "Vazir", 8.3)
            lw = c.stringWidth(label, "Vazir-Bold" if level == 0 else "Vazir", fs)
            if fa:
                right = self.width - indent
                c.drawRightString(right, y, label)
                c.drawString(4, y, page_s)
                if self.show_leaders:
                    x1 = max(pw + 8, 4)
                    c.line(x1, y + 3, max(x1, right - lw - 5), y + 3)
            else:
                c.drawString(indent, y, label)
                c.drawRightString(self.width - 4, y, page_s)
                if self.show_leaders:
                    x1 = min(indent + lw + 5, self.width - pw - 8)
                    c.line(x1, y + 3, max(x1, self.width - pw - 8), y + 3)
            y -= self.row_h


class ReportDoc(BaseDocTemplate):
    def __init__(self, filename, lang, meta, **kw):
        super().__init__(
            filename, pagesize=A4, leftMargin=MARGIN_L, rightMargin=MARGIN_R,
            topMargin=MARGIN_T, bottomMargin=MARGIN_B, **kw,
        )
        self.lang = lang
        self.meta = meta
        self.headings = []
        frame = Frame(
            MARGIN_L, MARGIN_B, PAGE_W - MARGIN_L - MARGIN_R, PAGE_H - MARGIN_T - MARGIN_B,
            id="main", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
        )
        cover_frame = Frame(0, 0, PAGE_W, PAGE_H, id="cover", leftPadding=0, rightPadding=0,
                            topPadding=0, bottomPadding=0)
        self.addPageTemplates([
            PageTemplate(id="cover", frames=[cover_frame]),
            PageTemplate(id="body", frames=[frame], onPage=self.draw_furniture),
        ])

    def draw_furniture(self, canv, doc):
        fa = self.lang == "fa"
        canv.saveState()
        canv.setStrokeColor(colors.HexColor(theme.RULE))
        canv.setLineWidth(0.6)
        canv.line(MARGIN_L, PAGE_H - 15 * mm, PAGE_W - MARGIN_R, PAGE_H - 15 * mm)
        canv.setFont("Vazir", 7.6)
        canv.setFillColor(colors.HexColor(theme.MUTED))
        course = self.meta["course"][0 if fa else 1]
        title = self.meta["short_title"][0 if fa else 1]
        if fa:
            # Persian header: title on the right, course on the left (both shaped)
            canv.drawRightString(PAGE_W - MARGIN_R, PAGE_H - 12.8 * mm, shape(title))
            canv.drawString(MARGIN_L, PAGE_H - 12.8 * mm, shape(course))
        else:
            canv.drawString(MARGIN_L, PAGE_H - 12.8 * mm, course)
            canv.drawRightString(PAGE_W - MARGIN_R, PAGE_H - 12.8 * mm, title)
        canv.setStrokeColor(colors.HexColor(theme.RULE))
        canv.line(MARGIN_L, 14 * mm, PAGE_W - MARGIN_R, 14 * mm)
        canv.setFont("Vazir", 7.6)
        canv.setFillColor(colors.HexColor(theme.MUTED))
        footer = self.meta["footer"][0 if fa else 1]
        if fa:
            canv.drawRightString(PAGE_W - MARGIN_R, 10.2 * mm, shape(footer))
            canv.drawString(MARGIN_L, 10.2 * mm, str(doc.page))
        else:
            canv.drawString(MARGIN_L, 10.2 * mm, str(doc.page))
            canv.drawRightString(PAGE_W - MARGIN_R, 10.2 * mm, footer)
        canv.restoreState()

    def afterFlowable(self, flowable):
        if isinstance(flowable, ChapterHeading) and flowable.toc:
            self.headings.append((flowable.level, flowable._toc_label, self.page))
        else:
            # headings inside KeepTogether/Table never reach afterFlowable themselves,
            # so register any nested ones against the page we are currently drawing
            for h in _nested_headings(flowable):
                if h.toc:
                    self.headings.append((h.level, h._toc_label, self.page))


# ------------------------------------------------------------------ cover
def _wrap_plain(text, font, size, max_w):
    from reportlab.pdfbase.pdfmetrics import stringWidth

    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if stringWidth(trial, font, size) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


class CoverBand(Spacer):
    def __init__(self, model, lang, h=248):
        super().__init__(1, 1)
        self.model, self.lang, self.H = model, lang, h

    def wrap(self, availWidth, availHeight):
        self.width, self.height = PAGE_W, self.H
        return (PAGE_W, self.H)

    def draw(self):
        c = self.canv
        fa = self.lang == "fa"
        m = self.model
        c.saveState()
        c.setFillColor(colors.HexColor(theme.ACCENT_DARK))
        c.rect(0, 0, PAGE_W, self.H, stroke=0, fill=1)
        c.setFillColor(colors.HexColor(theme.ACCENT))
        c.rect(0, 0, PAGE_W, 9, stroke=0, fill=1)
        c.setFillColor(colors.HexColor(theme.GOLD))
        c.rect(0, 9, 130 if not fa else PAGE_W - 130, 3, stroke=0, fill=1)
        c.setFillColor(colors.HexColor("#bcd9e8"))
        c.setFont("Vazir", 10.5)
        head = m.course_fa if fa else m.course_en
        c.drawRightString(PAGE_W - 42, self.H - 40, shape(head) if fa else head)
        c.setFont("Vazir", 9.2)
        c.setFillColor(colors.HexColor("#9fc4d8"))
        if fa:
            c.drawString(42, self.H - 40, shape("نسخه فارسی"))
        else:
            c.drawString(42, self.H - 40, "English Edition")
        c.setFillColor(colors.white)
        c.setFont("Vazir-Bold", 24)
        y = self.H - 96
        for line in _wrap_plain(m.title_fa if fa else m.title_en, "Vazir-Bold", 24, PAGE_W - 110):
            c.drawRightString(PAGE_W - 42, y, shape(line) if fa else line)
            y -= 34
        subs = (m.subtitle_fa, m.subtitle_en)[0 if fa else 1]
        if subs:
            c.setFillColor(colors.HexColor("#cfe6f2"))
            c.setFont("Vazir", 11)
            for line in _wrap_plain(subs, "Vazir", 11, PAGE_W - 110):
                c.drawRightString(PAGE_W - 42, y - 3, shape(line) if fa else line)
                y -= 17
        c.restoreState()


class CoverMeta(Spacer):
    def __init__(self, model, lang):
        super().__init__(1, 1)
        self.model, self.lang = model, lang

    def wrap(self, availWidth, availHeight):
        self.width, self.height = availWidth, 430
        return (availWidth, self.height)

    def draw(self):
        c = self.canv
        fa = self.lang == "fa"
        m = self.model
        x0, w = 40, PAGE_W - 80
        rows = [
            (("نگارنده", "Author"), (m.author, m.author_en)),
            (("درس", "Course"), (m.course_fa, m.course_en)),
            (("تاریخ", "Date"), (m.date_fa, m.date_en)),
        ]
        y = self.height - 6
        for (kfa, ken), (vfa, ven) in rows:
            c.setFillColor(colors.HexColor(theme.MUTED))
            c.setFont("Vazir", 9)
            c.drawString(x0, y, ken if not fa else shape(kfa))
            c.setFillColor(colors.HexColor(theme.INK))
            c.setFont("Vazir-Bold", 10)
            c.drawRightString(x0 + w, y, shape(vfa) if fa else ven)
            c.setStrokeColor(colors.HexColor(theme.RULE))
            c.setLineWidth(0.5)
            c.line(x0, y - 8, x0 + w, y - 8)
            y -= 31
        # abstract card
        card_top = y - 8
        card_h = min(238, card_top - 24)
        c.setFillColor(colors.HexColor(theme.PANEL))
        c.setStrokeColor(colors.HexColor(theme.RULE))
        c.roundRect(x0, card_top - card_h, w, card_h, 4, stroke=1, fill=1)
        c.setFillColor(colors.HexColor(theme.ACCENT_DARK))
        c.setFont("Vazir-Bold", 10.5)
        c.drawRightString(x0 + w - 14, card_top - 24, shape("چکیده") if fa else "Abstract")
        body = m.abstract_fa if fa else m.abstract_en
        c.setFillColor(colors.HexColor(theme.INK))
        c.setFont("Vazir", 8.7)
        yy = card_top - 42
        for line in _wrap_plain(body, "Vazir", 8.7, w - 30)[:13]:
            if fa:
                c.drawRightString(x0 + w - 14, yy, shape(line))
            else:
                c.drawString(x0 + 14, yy, line)
            yy -= 13.2
        if yy > 30:
            c.setFillColor(colors.HexColor(theme.MUTED))
            c.setFont("Vazir", 7.6)
            kw = (m.keywords_fa if fa else m.keywords_en)
            if kw:
                c.drawRightString(x0 + w - 14, yy - 2, shape("کلیدواژه‌ها: " + kw)[:110] if fa else "Keywords: " + kw[:100])


def _cover(model, lang):
    return [Spacer(1, 42), CoverBand(model, lang), Spacer(1, 30), CoverMeta(model, lang)]


# ------------------------------------------------------------------ build
def _dedupe_breaks(story):
    """Drop page breaks that would render as a fully blank page.

    A break is redundant when the previous flowable is already a PageBreak (possibly
    separated only by spacers/rules), which happens whenever a chapter ends exactly on a
    page boundary.
    """
    out = []
    seen_break = False
    for f in story:
        if isinstance(f, PageBreak):
            if seen_break:
                continue
            seen_break = True
            out.append(f)
            continue
        if isinstance(f, (Spacer, Rule)):
            # keep, but do not reset the "we just broke" flag
            out.append(f)
            continue
        seen_break = False
        out.append(f)
    while out and isinstance(out[0], PageBreak):
        out.pop(0)
    while out and isinstance(out[-1], PageBreak):
        out.pop()
    return out


def _emit_section_blocks(story, blocks, lang, st, counters, heading):
    """Render a section body, keeping every sub-heading glued to the block that follows it.

    Without this a heading can end a page on its own, which looks like a gap.
    """
    fa = lang == "fa"
    items = []
    sub = 0
    for b in blocks:
        if b["type"] == "h2":
            sub += 1
            items.append(("head", heading(b, sub)))
            continue
        items.append(("body", b))

    # Find heading->next-body pairs and emit them keep-together.
    i = 0
    while i < len(items):
        kind, payload = items[i]
        if kind == "head":
            if i + 1 < len(items) and items[i + 1][0] == "body":
                nxt = items[i + 1][1]
                flows = [payload] + render_block(nxt, lang, st, counters)
                cheap = nxt["type"] in ("p", "lead", "note", "quote", "formula")
                est = 0.0
                for f in flows:
                    # A ChapterHeading is a zero-sized Spacer whose height lives in its inner
                    # paragraph, so measure real flowables explicitly instead of trusting wrap().
                    if isinstance(f, ChapterHeading):
                        st_h = styles(lang)["ch" if f.level == 0 else "h2"]
                        est += st_h.leading + (26 if f.level == 0 else 14)
                        continue
                    try:
                        est += f.wrap(PAGE_W - MARGIN_L - MARGIN_R, PAGE_H)[1]
                    except Exception:
                        est = 1e9
                        break
                if cheap or est < 190:
                    story.append(KeepTogether(flows))
                else:
                    story.extend(flows)
                i += 2
                continue
            story.append(payload)
            i += 1
            continue
        story.extend(render_block(payload, lang, st, counters))
        i += 1


def _story(model, lang, st, toc_entries):
    fa = lang == "fa"
    story = []
    story += _cover(model, lang)
    story.append(NextPageTemplate("body"))
    story.append(PageBreak())

    story.append(ChapterHeading("فهرست مطالب" if fa else "Table of Contents", lang, 0, toc=False))
    story.append(Spacer(1, 8))
    story.append(TocFlow(lang, entries=toc_entries))
    story.append(PageBreak())

    # ---- front matter: abstract
    story.append(ChapterHeading("چکیده" if fa else "Abstract", lang, 0))
    story.append(Spacer(1, 6))
    story.append(RichText(model.abstract_fa if fa else model.abstract_en, st["lead"], lang))
    kw = model.keywords_fa if fa else model.keywords_en
    if kw:
        story.append(Spacer(1, 4))
        story.append(RichText(("**کلیدواژه‌ها:** " if fa else "**Keywords:** ") + kw, st["body"], lang))
    counters = {"fig": 0, "tab": 0, "code": 0}
    # Front matter continues on the abstract page while it fits; a heading that would be
    # stranded at the bottom moves to a fresh page together with its block.
    front = []
    for b in model.front_blocks:
        front += render_block(b, lang, st, counters)
    # Glue the roadmap heading to its table and note so the group moves as a whole;
    # this is what keeps the abstract page from ending in a stray callout.
    if front:
        story.append(KeepTogether(front))

    # ---- numbered sections: start a new page only when little room is left, so that
    #      sections flow continuously and no page ends with a large empty band.
    for i, sec in enumerate(model.sections, 1):
        if i == 1:
            story.append(PageBreak())
        else:
            story.append(CondPageBreak(280))
        story.append(ChapterHeading(sec.fa if fa else sec.en, lang, 0, number=str(i)))
        kicker = sec.kicker_fa if fa else sec.kicker_en
        if kicker:
            story.append(Spacer(1, 1))
            story.append(RichText(kicker, st["small"], lang))
        story.append(Spacer(1, 9))
        _emit_section_blocks(
            story, sec.blocks, lang, st, counters,
            lambda b, sub: ChapterHeading(b["fa"] if fa else b["en"], lang, 1, number=f"{i}.{sub}"),
        )

    # ---- appendix
    for i, sec in enumerate(model.appendix, 1):
        story.append(CondPageBreak(280))
        mark = ("پ" + to_fa_digits(str(i))) if fa else f"A{i}"
        story.append(ChapterHeading(sec.fa if fa else sec.en, lang, 0, number=mark))
        story.append(Spacer(1, 8))
        _emit_section_blocks(
            story, sec.blocks, lang, st, counters,
            lambda b, sub, mark=mark: ChapterHeading(
                b["fa"] if fa else b["en"], lang, 1,
                number=(f"{mark}.{to_fa_digits(str(sub))}" if fa else f"{mark}.{sub}")),
        )

    # ---- references
    if model.references:
        story.append(CondPageBreak(280))
        story.append(ChapterHeading("منابع و مراجع" if fa else "References", lang, 0, number=""))
        story.append(Spacer(1, 8))
        for i, (rfa, ren) in enumerate(model.references, 1):
            num = to_fa_digits(str(i)) if fa else str(i)
            story.append(RichText(f"[{num}]  " + (rfa if fa else ren), st["body"], lang))
    return _dedupe_breaks(story)


def build(model, out_path, lang, verbose=False):
    """Two-pass build: pass 1 learns heading pages, pass 2 draws a correct TOC."""
    register_mono()
    fa = lang == "fa"
    meta = {
        "course": (model.course_fa, model.course_en),
        "short_title": (model.title_fa, model.title_en),
        "footer": ("گزارش تمرین سیستم‌های عامل", "Operating Systems Assignment Report"),
    }
    st = styles(lang)
    tmp = out_path + ".pass1"
    doc1 = ReportDoc(tmp, lang, meta)
    doc1.build(_story(model, lang, st, []))
    entries = _unique_entries(doc1.headings)
    doc = ReportDoc(out_path, lang, meta)
    doc.build(_story(model, lang, st, entries))
    entries2 = _unique_entries(doc.headings)
    if [e[2] for e in entries] != [e[2] for e in entries2]:
        # page numbers shifted because the TOC grew: rebuild once more
        doc = ReportDoc(out_path, lang, meta)
        doc.build(_story(model, lang, st, entries2))
    try:
        os.remove(tmp)
    except OSError:
        pass
    return doc


def _nested_headings(flowable, depth=0):
    """Yield ChapterHeading instances nested inside a container flowable."""
    if depth > 4:
        return
    if isinstance(flowable, ChapterHeading):
        yield flowable
        return
    for attr in ("_content", "_flowables"):
        inner = getattr(flowable, attr, None)
        if inner:
            for c in inner:
                yield from _nested_headings(c, depth + 1)


def _collect_headings(doc):
    """Walk the story flowables (including nested Tables/KeepTogether) for chapter headings.

    `afterFlowable` only sees top-level flowables, so headings placed inside a
    KeepTogether were never registered and their TOC page numbers were lost.
    """
    out = []

    def visit(flowable, page_hint=None):
        if isinstance(flowable, ChapterHeading):
            out.append((flowable.level, flowable._toc_label, getattr(flowable, "_page", None) or page_hint))
            return
        inner = getattr(flowable, "_content", None)
        if inner:
            for c in inner:
                visit(c, page_hint)

    for f in doc.story_flowables if hasattr(doc, "story_flowables") else []:
        visit(f)
    return out


def _unique_entries(headings):
    seen, out = set(), []
    for level, label, page in headings:
        key = (level, label)
        if key in seen:
            continue
        seen.add(key)
        out.append((level, label, page))
    return out


def render_block(b, lang, st, counters=None):
    fa = lang == "fa"
    t = b["type"]
    out = []
    if t == "p":
        return [RichText(b["fa"] if fa else b["en"], st["body"], lang)]
    if t == "lead":
        return [RichText(b["fa"] if fa else b["en"], st["lead"], lang)]
    if t == "h2":
        return [ChapterHeading(b["fa"] if fa else b["en"], lang, 1)]
    if t == "h3":
        text = b["fa"] if fa else b["en"]
        if fa:
            text = shape(to_fa_digits(text))
        return [Spacer(1, 3), Paragraph(text.replace("<", "&lt;"), st["h3"])]
    if t in ("ul", "ol"):
        for i, (ifa, ien) in enumerate(b["items"], 1):
            txt = ifa if fa else ien
            mark = "•" if t == "ul" else (to_fa_digits(str(i)) + "." if fa else f"{i}.")
            out.append(RichText(txt, st["bullet"], lang, bullet=mark, left_indent=4))
        out.append(Spacer(1, 5))
        return out
    if t == "table":
        num = ""
        if counters is not None:
            counters["tab"] += 1
            num = to_fa_digits(str(counters["tab"])) if fa else str(counters["tab"])
        return build_table(b, lang, PAGE_W - MARGIN_L - MARGIN_R, number=num)
    if t == "figure":
        num = ""
        if counters is not None:
            counters["fig"] += 1
            num = to_fa_digits(str(counters["fig"])) if fa else str(counters["fig"])
        path = b["path"] if fa else b.get("en_path") or b["path"]
        if not os.path.isabs(path):
            path = os.path.join(os.getcwd(), path)
        f = Figure(path, b["cap"], lang, b.get("width") or 0.92, number=num)
        return [Spacer(1, 4), f, Spacer(1, 8)]
    if t == "code":
        num = ""
        if counters is not None:
            counters["code"] += 1
            num = to_fa_digits(str(counters["code"])) if fa else str(counters["code"])
        cap = caption((num, b["cap"][0 if fa else 1]), lang, "code")
        cb = CodeBlock(b, size=6.7)
        # CodeBlock.split() paginates listings, so no KeepTogether is needed; keeping the
        # caption glued to the block prevents the "caption alone at the page bottom" look.
        flows = [Spacer(1, 3), cap, Spacer(1, 3), cb, Spacer(1, 9)]
        return flows
    if t == "note":
        box = Callout(b["title"][0 if fa else 1], b["body"][0 if fa else 1], lang,
                      b.get("kind", "note"), width=PAGE_W - MARGIN_L - MARGIN_R)
        return [Spacer(1, 3), KeepTogether([box]), Spacer(1, 9)]
    if t == "quote":
        box = Callout(b["src"][0 if fa else 1] or "", b["fa"] if fa else b["en"], lang, "quote",
                      width=PAGE_W - MARGIN_L - MARGIN_R)
        return [Spacer(1, 4), KeepTogether([box]), Spacer(1, 9)]
    if t == "formula":
        text = b["fa"] if fa else b["en"]
        if fa:
            text = shape(text)
        fst = ParagraphStyle("f", fontName="Vazir", fontSize=8.6, leading=13.6, alignment=1,
                             textColor=colors.HexColor(theme.ACCENT_DARK), spaceBefore=3, spaceAfter=7,
                             backColor=colors.HexColor(theme.PANEL))
        return [Paragraph(text.replace("<", "&lt;"), fst)]
    if t == "kv":
        return [KVBox(b["pairs"], lang), Spacer(1, 10)]
    if t == "pagebreak":
        return [PageBreak()]
    if t == "spacer":
        return [Spacer(1, b["h"])]
    return out
