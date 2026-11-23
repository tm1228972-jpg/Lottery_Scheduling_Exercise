"""Figures, callout boxes and rule lines for the PDF engine."""
from __future__ import annotations

import os

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Flowable, KeepTogether, Paragraph, Spacer

from . import theme
from .fonts import register_reportlab_fonts
from .rtl import shape, has_arabic, to_fa_digits
from .tables import caption


class Figure(Flowable):
    """Image with aspect-preserving fit and bilingual caption."""

    def __init__(self, path, cap, lang, width, max_h=400, number=""):
        super().__init__()
        self.path, self.cap, self.lang = path, cap, lang
        ir = ImageReader(path)
        iw, ih = ir.getSize()
        self.caption = caption((number, cap[0] if lang == "fa" else cap[1]), lang, "figure")
        if isinstance(width, float) and width <= 1.0:
            self.w = None  # filled at wrap time
            self.rel = width
        else:
            self.w = float(width)
            self.rel = None
        self.ratio = ih / iw
        self.max_h = max_h
        self.allow_split = True
        self.iw, self.ih = iw, ih

    def split(self, availWidth, availHeight):
        """Allow a figure that does not fit to move to the next page instead of leaving a gap."""
        return []

    def wrap(self, availWidth, availHeight):
        w = self.rel * availWidth if self.rel is not None else min(self.w, availWidth)
        h = w * self.ratio
        if h > self.max_h:
            h = self.max_h
            w = h / self.ratio
        # Shrink to the space actually left on this page so pages stay full (no gaps),
        # but only down to a legibility floor; below that the figure moves to the next page.
        cw0, ch0 = self.caption.wrap(availWidth, 200)
        room = availHeight - ch0 - 12
        if room < h:
            if room >= max(150, 0.52 * (self.rel or 0.92) * availWidth * self.ratio):
                h = room
                w = h / self.ratio
        self.w, self.h = w, h
        cw, ch = self.caption.wrap(availWidth, 200)
        self.ch = ch
        self.width = availWidth
        self.height = h + ch + 10
        return (availWidth, self.height)

    def draw(self):
        c = self.canv
        fa = self.lang == "fa"
        x = (self.width - self.w) / 2
        c.drawImage(self.path, x, self.height - self.h - 2, self.w, self.h, mask="auto")
        c.setStrokeColor(colors.HexColor(theme.RULE))
        c.setLineWidth(0.5)
        c.rect(x, self.height - self.h - 2, self.w, self.h, stroke=1, fill=0)
        c.saveState()
        c.translate(0, 2)
        self.caption.drawOn(c, 0, 0)
        c.restoreState()


def _plain_md(text):
    """Strip the light markdown used in model text (bold/code) for canvas-drawn boxes."""
    import re as _re
    text = _re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = _re.sub(r"`(.+?)`", r"\1", text)
    return text


class Callout(Flowable):
    """Coloured note/warning/insight box with bilingual text."""

    def __init__(self, title, body, lang, kind="note", width=None):
        super().__init__()
        self.title, self.body, self.lang, self.kind = title, body, lang, kind
        self._w = width

    KIND = {
        "note": ("#e8f3f9", "#0b6e99"),
        "warn": ("#fdf0e6", "#c1440e"),
        "key": ("#eaf5ee", "#2e7d4f"),
        "quote": ("#f4f1f8", "#6a4c93"),
    }

    def wrap(self, availWidth, availHeight):
        w = self._w or availWidth
        self.width = w
        self.pad = 7
        self.lh = 12.4
        self.size = 8.9
        fa = self.lang == "fa"
        text = _plain_md(self.body)
        if fa:
            text = shape(to_fa_digits(text))
        self._text_lines = self._wrap_text(text, w - 2 * self.pad - 4, fa)
        t = _plain_md(self.title)
        if fa:
            t = shape(t)
        self._title = t
        # ReportLab asks for wrap() twice: once with the room left on the current page and
        # once with a fresh page. Only keep the line breaks when they fit, otherwise the
        # box would report a height it cannot render within.
        self._full_lines = len(self._text_lines)
        if self._text_lines and len(self._text_lines) * self.lh + 2 * self.pad + 10 > availHeight:
            self._tight = True
        self.height = 2 * self.pad + 10 + len(self._text_lines) * self.lh
        self.height = min(self.height, max(28.0, availHeight))
        return (w, self.height)

    def _wrap_text(self, text, max_w, fa):
        from reportlab.pdfbase.pdfmetrics import stringWidth

        words = text.split(" ")
        lines, cur = [], ""
        for word in words:
            trial = (cur + " " + word).strip()
            if stringWidth(trial, "Vazir", self.size) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def draw(self):
        c = self.canv
        fa = self.lang == "fa"
        bg, fg = self.KIND[self.kind]
        c.saveState()
        c.setFillColor(colors.HexColor(bg))
        c.setStrokeColor(colors.HexColor(fg))
        c.setLineWidth(2.2)
        c.roundRect(0, 0, self.width, self.height, 3, stroke=0, fill=1)
        c.rect(0, 0, 2.6, self.height, stroke=0, fill=1)
        c.setFillColor(colors.HexColor(fg))
        c.setFont("Vazir-Bold", 9.6)
        if fa:
            c.drawRightString(self.width - self.pad, self.height - self.pad - 8, self._title)
        else:
            c.drawString(self.pad + 4, self.height - self.pad - 8, self._title)
        c.setFillColor(colors.HexColor(theme.INK))
        c.setFont("Vazir", self.size)
        y = self.height - self.pad - 24
        room = max(0, int((self.height - self.pad - 24) / self.lh) + 1)
        for line in self._text_lines[:room]:
            if fa:
                c.drawRightString(self.width - self.pad, y, line)
            else:
                c.drawString(self.pad + 4, y, line)
            y -= self.lh
        c.restoreState()


class Rule(Flowable):
    def __init__(self, width_ratio=1.0, color=theme.RULE, thickness=0.6, space=8):
        super().__init__()
        self.width_ratio, self.color, self.thickness, self.space = width_ratio, color, thickness, space

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        self.height = self.space
        return (availWidth, self.space)

    def draw(self):
        self.canv.setStrokeColor(colors.HexColor(self.color))
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, self.space / 2, self.width * self.width_ratio, self.space / 2)


class KVBox(Flowable):
    """Two-column definition grid (metadata / specifications)."""

    def __init__(self, pairs, lang, col_w=None):
        super().__init__()
        self.pairs, self.lang = pairs, lang

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        self.row_h = 17
        self.height = len(self.pairs) * self.row_h + 6
        return (availWidth, self.height)

    def draw(self):
        c = self.canv
        fa = self.lang == "fa"
        y = self.height - self.row_h + 4
        for i, (k, v) in enumerate(self.pairs):
            kk = k[0] if fa else k[1]
            vv = v[0] if fa else v[1]
            if fa:
                kk, vv = shape(to_fa_digits(kk)), shape(to_fa_digits(vv))
            if i % 2 == 0:
                c.setFillColor(colors.HexColor(theme.PANEL))
                c.rect(0, y - 5, self.width, self.row_h, stroke=0, fill=1)
            c.setFillColor(colors.HexColor(theme.ACCENT_DARK))
            c.setFont("Vazir-Bold", 8.6)
            c.setFillColor(colors.HexColor(theme.MUTED))
            c.setFont("Vazir-Bold", 8.4)
            if fa:
                c.drawRightString(self.width - 4, y, kk)
                c.setFillColor(colors.HexColor(theme.INK))
                c.setFont("Vazir", 8.6)
                c.drawRightString(self.width * 0.74, y, vv)
            else:
                c.drawString(4, y, kk)
                c.setFillColor(colors.HexColor(theme.INK))
                c.setFont("Vazir", 8.6)
                c.drawString(self.width * 0.30, y, vv)
            y -= self.row_h
