"""RTL/LTR rich-text layout for ReportLab.

Persian text is laid out by shaping each word and reversing the word order per
line (the classic shape-then-reorder approach). Latin/code runs are kept intact
as LTR islands, so nothing is ever mirrored and no Persian word is broken.
"""
from __future__ import annotations

import re

from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Flowable

from .rtl import shape, has_arabic

_SPACE_RE = re.compile(r"[ \t]+")
_MARK_RE = re.compile(r"(\*\*(?!\s).+?(?<!\s)\*\*|`[^`]+`|\*(?!\s)[^*]+?\*)", re.S)


# tokens: whitespace | "(Latin phrase)" | Persian run (no spaces) | other
# a token that is nothing but neutral punctuation/brackets (no letters, no digits)
_PURE_PUNCT = re.compile(r"^[^\w\u0600-\u06FF]+$")

# Unicode bidi mirrors brackets when they appear in a right-to-left run
_MIRROR = str.maketrans("()[]{}", ")(][}{")

_TOKEN_SPLIT = re.compile(
    r"([ \t]+"
    r"|\([A-Za-z][A-Za-z0-9_\-+*/().:;, '<>=!]*\)"
    r"|[\u0600-\u06FF\u200c]+"
    r"|[A-Za-z0-9_\-+*/.():;,<>=!&|~^%]+"
    r"|[^ \t])"
)


def _shape_token(tok: str) -> str:
    """Shape one Persian token; Latin sub-runs inside it get LRE/PDF so that
    parentheses around Latin text are never mirrored by the bidi pass."""
    if not _BRACKET_LATIN.search(tok):
        return shape(tok)
    from .rtl import LRE, PDF_

    return shape(tok, isolate_latin=True)


class Run:
    __slots__ = ("text", "bold", "mono", "italic")

    def __init__(self, text, bold=False, mono=False, italic=False):
        self.text, self.bold, self.mono, self.italic = text, bold, mono, italic

    def __repr__(self):
        return f"Run({self.text!r})"


def parse_inline(text: str) -> list[Run]:
    """Parse **bold**, `code`, *italic* markup into styled runs."""
    runs: list[Run] = []
    pos = 0
    for m in _MARK_RE.finditer(text):
        if m.start() > pos:
            runs.append(Run(text[pos : m.start()]))
        tok = m.group(0)
        if tok.startswith("**"):
            runs.append(Run(tok[2:-2], bold=True))
        elif tok.startswith("`"):
            runs.append(Run(tok[1:-1], mono=True))
        else:
            runs.append(Run(tok[1:-1], italic=True))
        pos = m.end()
    if pos < len(text):
        runs.append(Run(text[pos:]))
    return [r for r in runs if r.text]


class Atom:
    __slots__ = ("text", "font", "size", "color", "ltr", "width", "src")

    def __init__(self, text, font, size, color, ltr, src):
        self.text, self.font, self.size, self.color, self.ltr, self.src = text, font, size, color, ltr, src
        self.width = 0.0


class RichText(Flowable):
    """A paragraph that renders correctly in RTL (Persian) and LTR (English)."""

    def __init__(
        self,
        text,
        style,
        lang="fa",
        bullet=None,
        bullet_color="#0b6e99",
        first_indent=0.0,
        left_indent=0.0,
        keep_with_next=False,
    ):
        super().__init__()
        self.text = text
        self.style = style
        self.lang = lang
        self.bullet = bullet
        self.bullet_color = bullet_color
        self.left_indent = left_indent
        self.first_indent = first_indent
        self.keep_with_next = keep_with_next
        self.lines = []          # list of list[Atom]
        self.gap = 0.0
        self._height = 0.0
        self._wrapped_width = 0.0

    # ------------------------------------------------------------------ atoms
    def _font_for(self, run: Run, style) -> str:
        base = style.fontName
        if run.mono:
            return "Mono"
        if run.bold or run.italic:
            return "Vazir-Bold"
        return base

    def _build_atoms(self):
        atoms: list[Atom] = []
        mono_size = self.style.fontSize - 1.4
        for run in parse_inline(self.text):
            font = self._font_for(run, self.style)
            size = mono_size if run.mono else self.style.fontSize
            color = self.style.textColor if not run.mono else "#0b6e99"
            # keep the whitespace structure: a word atom followed by an optional space atom
            # split on spaces, but keep "(Latin phrase)" together as one LTR island
            tokens = _TOKEN_SPLIT.findall(run.text)
            for tok in tokens:
                if tok == "":
                    continue
                if tok.isspace():
                    sp = Atom(" ", font, size, color, True, run)
                    sp.width = self.style.fontSize * 0.30 + getattr(self.style, "wordSpacing", 0)
                    atoms.append(sp)
                    continue
                if has_arabic(tok):
                    # Persian text: shape it; any Latin island inside keeps its direction
                    atoms.append(Atom(shape(tok), font, size, color, False, run))
                elif self.lang == "fa" and _PURE_PUNCT.match(tok):
                    # Neutral punctuation in an RTL run: the cluster is drawn as one atomic
                    # glyph run from the right, so reverse it (or a trailing full stop jumps
                    # to the front) and mirror the brackets, exactly as the bidi algorithm does.
                    atoms.append(Atom(tok[::-1].translate(_MIRROR), font, size, color, True, run))
                else:
                    atoms.append(Atom(tok, font, size, color, True, run))
        # Code (mono) runs must stay unbreakable; merge their words back into one atom.
        merged: list[Atom] = []
        for a in atoms:
            if (
                merged
                and a.ltr
                and a.text != " "
                and merged[-1].text != " "
                and a.font == "Mono"
                and merged[-1].font == "Mono"
                and merged[-1].size == a.size
            ):
                m = merged[-1]
                sep = " "
                if m.text.endswith("()") or a.text.startswith(")"):
                    sep = " "
                m.text = m.text + sep + a.text
                m.src = a.src
                m.width = 0.0
            else:
                merged.append(a)
        for a in merged:
            a.width = stringWidth(a.text, a.font, a.size)
        return merged

    # ------------------------------------------------------------------ wrap
    def wrap(self, availWidth, availHeight):
        indent = self.left_indent + (self.first_indent or 0)
        bullet_w = 0
        if self.bullet:
            bullet_w = self.style.fontSize * 1.05
        width = availWidth - indent - bullet_w
        atoms = self._build_atoms()
        lines: list[list[Atom]] = []
        cur: list[Atom] = []
        cur_w = 0.0
        for a in atoms:
            add = a.width
            if cur and cur_w + add > width:
                # An over-long single atom (a long Latin identifier) is split at character
                # level; otherwise it would run off the right edge of the text block.
                if add > width and not a.text.isspace():
                    parts = self._split_atom(a, width)
                    for j, part in enumerate(parts):
                        if j:
                            lines.append(cur)
                            cur, cur_w = [], 0.0
                        cur.append(part)
                        cur_w += part.width
                    continue
                lines.append(cur)
                cur, cur_w = [a], a.width
            else:
                cur.append(a)
                cur_w += add
        if cur:
            lines.append(cur)
        if not lines:
            lines = [[]]
        self.lines = lines
        self.gap = 0.0
        if len(lines) > 1 and self.style.alignment == 4:  # justify
            extra = 0
            for ln in lines[:-1]:
                w = sum(a.width for a in ln)
                extra += max(0.0, width - w)
        self._wrapped_width = width
        self._indent = indent
        self._bullet_w = bullet_w
        self._height = len(lines) * self.style.leading + self.style.spaceBefore + self.style.spaceAfter
        self.width = availWidth
        self.height = self._height
        return (availWidth, self._height)

    def _split_atom(self, atom, max_w):
        """Split one over-wide atom into pieces that each fit `max_w`."""
        from reportlab.pdfbase.pdfmetrics import stringWidth

        text, out, cur = atom.text, [], ""
        for ch in text:
            trial = cur + ch
            if cur and stringWidth(trial, atom.font, atom.size) > max_w:
                out.append(Atom(cur, atom.font, atom.size, atom.color, atom.ltr, atom.src))
                cur = ch
            else:
                cur = trial
        if cur:
            out.append(Atom(cur, atom.font, atom.size, atom.color, atom.ltr, atom.src))
        for a in out:
            a.width = stringWidth(a.text, a.font, a.size)
        return out or [atom]

    # ------------------------------------------------------------------ draw
    def draw(self):
        c = self.canv
        style = self.style
        leading = style.leading
        y = self._height - style.spaceBefore - style.fontSize
        indent = getattr(self, "_indent", 0)
        bullet_w = getattr(self, "_bullet_w", 0)
        width = getattr(self, "_wrapped_width", self.width)
        rtl = self.lang == "fa"
        justify = style.alignment == 4
        for idx, line in enumerate(self.lines):
            n = len(line)
            if not n:
                y -= leading
                continue
            natural = sum(a.width for a in line)
            last = idx == len(self.lines) - 1
            gap = 0.0
            nspaces = sum(1 for a in line if a.text == " ")
            if justify and not last and nspaces:
                extra = max(0.0, width - natural) / nspaces
            else:
                extra = 0.0
            x_start = indent + bullet_w
            if self.bullet:
                c.setFillColor(self.bullet_color)
                c.setFont("Vazir", style.fontSize)
                if rtl:
                    c.drawRightString(self.width - self._indent_draw, y, self.bullet)
                else:
                    c.drawString(0, y, self.bullet)
            if rtl:
                x = self.width - x_start
                for a in line:
                    c.setFont(a.font, a.size)
                    c.setFillColor(a.color)
                    c.drawRightString(x, y, a.text)
                    x -= a.width + (extra if a.text == " " else 0.0)
            else:
                x = x_start
                for a in line:
                    c.setFont(a.font, a.size)
                    c.setFillColor(a.color)
                    c.drawString(x, y, a.text)
                    x += a.width + (extra if a.text == " " else 0.0)
            y -= leading

    @property
    def _indent_draw(self):
        return self.left_indent
