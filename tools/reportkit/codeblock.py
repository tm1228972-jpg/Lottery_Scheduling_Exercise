"""Syntax-highlighted, line-numbered code listing flowable (LTR, never mirrored)."""
from __future__ import annotations

from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Flowable

from .model import code_lines, guess_lang, tokenize_line

COLORS = {
    "kw": "#1f6feb",
    "num": "#b45309",
    "comment": "#6b7f8f",
    "string": "#3f8f4f",
    "code": "#24292f",
    "lineno": "#9aa7b2",
}


class CodeBlock(Flowable):
    """A framed, numbered source listing. LTR always (code is never right-to-left)."""

    def __init__(self, block, lang=None, size=7.1, max_lines=None, repeat_header=True, width=None):
        super().__init__()
        self.lines, self.first_no = code_lines(block)
        self.lang = guess_lang(block.get("path"), block.get("lang") or lang)
        self.filename = block.get("label", (None, None))[1] or (
            block["path"].split("/")[-1] if "path" in block else "listing"
        )
        self.size = size
        self.leading = size * 1.36
        self.max_lines = max_lines
        self.width = width
        self.repeat_header = repeat_header
        self.tokens = [tokenize_line(l, self.lang) for l in self.lines]
        # pagination support
        self._offset = 0          # index of the first line drawn by this part
        self._rows = None         # explicit row count for a continuation part
        self._cont = False        # True when this flowable is a continuation
        self._last = True

    def _avail_width(self):
        w = self.width or 1
        num_w = stringWidth(str(self.first_no + len(self.lines)), "Mono", self.size) + 10
        return w - (num_w + 4) - 10

    def _fit_rows(self, cap_rows):
        """Choose how many source lines fit in `cap_rows` rendered rows."""
        total = len(self.lines)
        start = self._offset
        avail = self._avail_width()
        rows, used = 0, 0
        while rows < cap_rows and start + rows < total:
            need = len(_wrap_tokens(self.tokens[start + rows], avail, self.size))
            if used + need > cap_rows:
                break
            used += need
            rows += 1
        return rows, used

    def wrap(self, availWidth, availHeight):
        w = self.width or availWidth
        self.width = w
        total = len(self.lines)
        start = self._offset
        room = availHeight if (availHeight and availHeight > 0) else 10 ** 6
        cap_rows = max(1, int((room - 20) // self.leading))
        rows, used = self._fit_rows(cap_rows)
        if rows == 0:
            rows, used = 1, 1
        self._part_rows = rows
        self._part_height = self.leading * used + 20
        self.height = self._part_height
        self._last = (start + rows) >= total
        return (w, self.height)

    def split(self, availWidth, availHeight):
        """Split a long listing across pages instead of pushing a whole page break."""
        total = len(self.lines)
        start = self._offset
        self.width = self.width or availWidth
        room = availHeight if availHeight and availHeight > 0 else 10 ** 6
        cap_rows = max(1, int((room - 20) // self.leading))
        rows, _ = self._fit_rows(cap_rows)
        if rows <= 0 or rows >= total - start or rows < 3:
            return []
        head = CodeBlock.__new__(CodeBlock)
        head.__dict__.update(self.__dict__)
        head._rows = rows
        tail = CodeBlock.__new__(CodeBlock)
        tail.__dict__.update(self.__dict__)
        tail._offset = start + rows
        tail._rows = None
        tail._cont = True
        tail.first_no = self.first_no + start + rows
        return [head, tail]

    def draw(self):
        c = self.canv
        w = self.width
        h = self.height
        start = self._offset
        rows = getattr(self, "_part_rows", len(self.lines) - start)
        avail = self._avail_width()
        wrapped = []          # [(source_line_no, tokens)]
        for k, toks in enumerate(self.tokens[start:start + rows]):
            for j, part in enumerate(_wrap_tokens(toks, avail, self.size)):
                wrapped.append((self.first_no + start + k if j == 0 else None, part))
        c.saveState()
        c.setFillColor("#f7f9fb")
        c.setStrokeColor("#d7e0e8")
        c.setLineWidth(0.6)
        c.roundRect(0, 0, w, h, 4, stroke=1, fill=1)
        c.setFillColor("#0b6e99")
        c.rect(0, h - 13, w, 13, stroke=0, fill=1)
        c.setFillColor("#ffffff")
        c.setFont("Vazir-Bold", 6.6)
        label = self.filename + ("  (continued)" if self._cont else "")
        c.drawString(6, h - 9.4, label)
        c.setFont("Vazir", 6.2)
        first_no = self.first_no + start
        last_no = max(first_no, self.first_no + start + rows - 1)
        c.drawRightString(w - 6, h - 9.4, f"{self.lang.upper()}  |  L{first_no}-{last_no}")
        y = h - 13 - self.leading
        num_w = stringWidth(str(self.first_no + len(self.lines)), "Mono", self.size) + 10
        for lineno, toks in wrapped:
            c.setFillColor(COLORS["lineno"])
            c.setFont("Mono", self.size - 0.5)
            if lineno is not None:
                c.drawRightString(num_w - 4, y, str(lineno))
            else:
                c.drawRightString(num_w - 4, y, "\u21b3")   # continuation marker
            x = num_w + 4
            for kind, text in toks:
                c.setFont("Mono-Bold" if kind == "kw" else "Mono", self.size)
                c.setFillColor(COLORS.get(kind, COLORS["code"]))
                c.drawString(x, y, text)
                x += stringWidth(text, "Mono", self.size)
            y -= self.leading
        c.restoreState()

def _wrap_tokens(tokens, avail, size):
    """Hard-wrap one tokenised source line to fit `avail` points.

    Long identifiers/strings are split at character boundaries; indentation of the
    continuation is preserved as a hanging indent so the code stays readable.
    """
    from reportlab.pdfbase.pdfmetrics import stringWidth as _sw
    total = sum(_sw(t, "Mono", size) for _, t in tokens)
    if total <= avail:
        return [tokens]
    out, cur, used = [], [], 0.0
    for kind, text in tokens:
        piece = text
        while piece:
            wpiece = _sw(piece, "Mono", size)
            if used + wpiece <= avail:
                cur.append((kind, piece))
                used += wpiece
                piece = ""
            else:
                room = avail - used
                # how many characters still fit?
                if room > _sw("0", "Mono", size) * 2:
                    lo, hi = 1, len(piece)
                    while lo < hi:
                        mid = (lo + hi + 1) // 2
                        if _sw(piece[:mid], "Mono", size) <= room:
                            lo = mid
                        else:
                            hi = mid - 1
                    cut = lo
                    cur.append((kind, piece[:cut]))
                    out.append(cur)
                    piece = piece[cut:]
                else:
                    if cur:
                        out.append(cur)
                cur, used = [], 0.0
    if cur:
        out.append(cur)
    return out or [tokens]
