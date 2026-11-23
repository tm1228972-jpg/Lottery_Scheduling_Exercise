"""16:9 slide deck renderer + narrated MP4.

Each slide is drawn edge-to-edge (no white gutters between slides) and every
Persian string is shaped + bidi-reordered so nothing is ever mirrored.
"""
from __future__ import annotations

import os
import subprocess

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch, Rectangle

import arabic_reshaper
from bidi.algorithm import get_display

from . import theme

_reshaper = arabic_reshaper.ArabicReshaper(
    configuration={"delete_harakat": False, "support_ligatures": True}
)


_GLYPH_FALLBACK = {
    "\u2308": "",   # LEFT CEILING
    "\u2309": "",   # RIGHT CEILING
    "\u230a": "",   # LEFT FLOOR
    "\u230b": "",   # RIGHT FLOOR
    "\u03a3": "SUM",  # GREEK CAPITAL SIGMA
    "\u2211": "SUM",  # N-ARY SUMMATION
    "\u2264": "\u2264",
}


def _safe(text: str) -> str:
    """Replace glyphs the slide font is missing so nothing renders as a blank box."""
    for bad, good in _GLYPH_FALLBACK.items():
        text = text.replace(bad, good)
    return text


def fa(text: str) -> str:
    """Matplotlib's raqm backend performs shaping and bidi itself, so Persian text is
    passed through unchanged here. Pre-shaping would reverse it a second time and
    produce mirrored words."""
    return text or ""


class Deck:
    def __init__(self, model, lang, out_dir, w=1280, h=720, dpi=100):
        self.m, self.lang, self.out = model, lang, out_dir
        self.fa_mode = lang == "fa"
        self.W, self.H, self.dpi = w, h, dpi
        os.makedirs(out_dir, exist_ok=True)
        self.slides = []

    # ------------------------------------------------------------------ canvas
    def _fig(self):
        fig = Figure(figsize=(self.W / self.dpi, self.H / self.dpi), dpi=self.dpi,
                     facecolor=theme.ACCENT_DARK)
        FigureCanvasAgg(fig)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, self.W)
        ax.set_ylim(0, self.H)
        ax.axis("off")
        ax.add_patch(Rectangle((0, 0), self.W, self.H, color=theme.ACCENT_DARK, zorder=0))
        return fig, ax

    def _text(self, ax, x, y, text, size=20, color="#ffffff", weight="normal", ha="left", va="center",
              wrap=None, fa_text=False, alpha=1.0, style="normal"):
        import re as _re
        text = _re.sub(r"\*\*(.+?)\*\*", r"\1", str(text or ""))
        text = _re.sub(r"`(.+?)`", r"\1", text)
        t = fa(text) if fa_text else text
        if fa_text and ha == "left":
            # Mirror the anchor instead of just flipping it: a caller asking for
            # "left-aligned at x" wants "right-aligned at the mirrored x", otherwise the
            # text runs off the left edge of the canvas.
            ha = "right"
            x = self.W - x
        text = _safe(text)
        if wrap:
            words = (text or "").split(" ")
            lines, cur = [], ""
            # `wrap` is a width in slide units; the drawn font is size*0.72, so the
            # per-character budget must use that effective size.
            eff = size * 0.72
            for w in words:
                trial = (cur + " " + w).strip()
                if len(trial) * eff * 0.52 <= wrap or not cur:
                    cur = trial
                else:
                    lines.append(cur)
                    cur = w
            if cur:
                lines.append(cur)
            lines = lines[:8]
            if len(lines) > 1:
                block_h = len(lines) * size * 1.45
                y0 = y + block_h / 2 - size * 0.7
                for i, line in enumerate(lines):
                    ax.text(x, y0 - i * size * 1.45, fa(line) if fa_text else line, fontsize=size * 0.72,
                            color=color, ha=ha, va="center", weight=weight, alpha=alpha, style=style,
                            family="Vazirmatn")
                return len(lines)
        ax.text(x, y, t, fontsize=size * 0.72, color=color, ha=ha, va=va, weight=weight,
                alpha=alpha, family="Vazirmatn", style=style)
        return 1

    def _chrome(self, ax, idx, total, title, kicker=""):
        ax.add_patch(Rectangle((0, self.H - 8), self.W, 8, color=theme.GOLD, zorder=3))
        ax.add_patch(Rectangle((0, 0), self.W, 5, color=theme.ACCENT, zorder=3))
        # title: shrink the font until the longest line fits the available width
        import re as _re

        clean = _re.sub(r"\*\*(.+?)\*\*", r"\1", str(title or ""))
        max_w = self.W - 150
        size = 34
        while size > 18 and len(clean) * size * 0.52 > max_w:
            size -= 2
        x = self.W - 70 if self.fa_mode else 70
        self._text(ax, x, self.H - 105, clean, size=size, weight="bold", fa_text=self.fa_mode,
                   ha="right" if self.fa_mode else "left")
        if kicker:
            self._text(ax, 70, self.H - 52, kicker, size=15, color="#9fc4d8", fa_text=self.fa_mode)
        # slide number
        num = f"{idx}/{total}"
        self._text(ax, self.W - 60, self.H - 52, num, size=14, color="#9fc4d8", ha="right")
        ax.add_patch(Rectangle((70, self.H - 78), 90, 3, color=theme.ACCENT, zorder=4))

    def _save(self, fig, idx):
        path = os.path.join(self.out, f"slide_{idx:03d}.png")
        fig.savefig(path, dpi=self.dpi, facecolor=fig.get_facecolor())
        plt.close(fig)
        return path

    # ------------------------------------------------------------------ slides
    def build(self, script=None):
        m, fa_mode = self.m, self.fa_mode
        script = script or {}
        total = 1 + 1 + len(m.sections) * 2 + 1
        idx = 1

        # ---- title slide
        fig, ax = self._fig()
        ax.add_patch(Rectangle((0, 0), self.W, 10, color=theme.ACCENT, zorder=2))
        ax.add_patch(Rectangle((0, 10), 380, 5, color=theme.GOLD, zorder=2))
        self._text(ax, 70, self.H - 120, m.course_fa if fa_mode else m.course_en, size=18, color="#9fc4d8",
                   fa_text=fa_mode)
        self._text(ax, 70, self.H / 2 + 60, m.title_fa if fa_mode else m.title_en, size=52, weight="bold",
                   fa_text=fa_mode, wrap=self.W - 260)
        sub = m.subtitle_fa if fa_mode else m.subtitle_en
        self._text(ax, 70, self.H / 2 - 90, sub, size=22, color="#cfe6f2", fa_text=fa_mode, wrap=self.W - 260)
        self._text(ax, 70, 90, (m.author_fa if fa_mode else m.author_en) if hasattr(m, "author_fa")
                   else (m.author if fa_mode else m.author_en), size=16, color="#9fc4d8", fa_text=fa_mode)
        self._text(ax, self.W - 70, 90, m.date_fa if fa_mode else m.date_en, size=16, color="#9fc4d8",
                   ha="right", fa_text=fa_mode)
        self.slides.append((self._save(fig, idx), script.get("title", "")))
        idx += 1

        # ---- agenda slide
        fig, ax = self._fig()
        self._chrome(ax, idx, total, "سرفصل‌ها" if fa_mode else "Agenda")
        y = self.H - 230
        for i, sec in enumerate(m.sections[:8], 1):
            ax.add_patch(FancyBboxPatch((70, y - 30), 26, 26, boxstyle="round,pad=0.5",
                                        color=theme.ACCENT, zorder=3))
            self._text(ax, 83, y - 17, str(i), size=15, weight="bold", ha="center")
            self._text(ax, 120, y - 17, sec.fa if fa_mode else sec.en, size=22, fa_text=fa_mode,
                       wrap=self.W - 300)
            y -= 62
        self.slides.append((self._save(fig, idx), script.get("agenda", "")))
        idx += 1

        # ---- content slides: one "key ideas" + one figure/table per section
        fig_no = 0
        for si, sec in enumerate(m.sections, 1):
            concepts = [b for b in sec.blocks if b["type"] in ("ul", "ol")]
            paras = [b for b in sec.blocks if b["type"] == "p"]
            fig, ax = self._fig()
            self._chrome(ax, idx, total, sec.fa if fa_mode else sec.en,
                         ("بخش " + self._num(si)) if fa_mode else f"Section {si}")
            items = concepts[0]["items"][:5] if concepts else []
            if items:
                y = self.H - 240
                for i, (ifa, ien) in enumerate(items, 1):
                    if fa_mode:
                        ax.add_patch(Rectangle((self.W - 76, y - 6), 6, 30, color=theme.GOLD, zorder=3))
                        self._text(ax, self.W - 100, y + 9, ifa, size=19, fa_text=True,
                                   wrap=self.W - 300)
                    else:
                        ax.add_patch(Rectangle((70, y - 6), 6, 30, color=theme.GOLD, zorder=3))
                        self._text(ax, 95, y + 9, ien, size=19, fa_text=False, wrap=self.W - 260)
                    y -= 74
            elif paras:
                body = (paras[0]["fa"] if fa_mode else paras[0]["en"])
                if len(body) > 460:
                    cut = body[:460]
                    for sep in ("\u061f", "\u06d4", "?", "."):
                        pos = cut.rfind(sep)
                        if pos > 320:
                            cut = cut[: pos + 1]
                            break
                    body = cut
                self._text(ax, 70, self.H - 250, body, size=24, color="#e6eef4", fa_text=fa_mode,
                           wrap=self.W - 200)
            self.slides.append((self._save(fig, idx), script.get(f"sec{si}_a", "")))
            idx += 1

            # figure/table slide
            figs = [b for b in sec.blocks if b["type"] == "figure"]
            tabs = [b for b in sec.blocks if b["type"] == "table"]
            if figs:
                fig_no += 1
                fig, ax = self._fig()
                self._chrome(ax, idx, total, figs[0]["cap"][0 if fa_mode else 1], "" if not fa_mode else "شکل")
                img = plt.imread(figs[0]["path"])
                ax_img = fig.add_axes([0.12, 0.10, 0.76, 0.62])
                ax_img.imshow(img)
                ax_img.axis("off")
                self.slides.append((self._save(fig, idx), script.get(f"sec{si}_fig", "")))
                idx += 1
            elif tabs:
                fig, ax = self._fig()
                spec = tabs[0]
                self._chrome(ax, idx, total, spec["cap"][0 if fa_mode else 1], "")
                head = spec["head"][0 if fa_mode else 1]
                rows = [[c[0] if fa_mode else c[1] for c in row] for row in spec["rows"]][:6]
                ncol = len(head)
                colw = (self.W - 160) / ncol
                y = self.H - 250
                for ci, h in enumerate(head):
                    ax.add_patch(Rectangle((80 + ci * colw, y - 14), colw - 6, 44, color=theme.ACCENT, zorder=3))
                    self._text(ax, 80 + ci * colw + colw / 2, y + 8, str(h), size=16, weight="bold", ha="center",
                               fa_text=fa_mode and any(ord(c) > 1500 for c in str(h)))
                y -= 62
                for ri, row in enumerate(rows):
                    for ci, v in enumerate(row):
                        if ri % 2 == 1:
                            ax.add_patch(Rectangle((80 + ci * colw, y - 12), colw - 6, 38, color="#124a63",
                                                   zorder=2))
                        self._text(ax, 80 + ci * colw + colw / 2, y + 6, str(v), size=14, ha="center",
                                   fa_text=any(ord(c) > 1500 for c in str(v)))
                    y -= 40
                self.slides.append((self._save(fig, idx), script.get(f"sec{si}_fig", "")))
                idx += 1

        # ---- closing slide
        fig, ax = self._fig()
        ax.add_patch(Rectangle((0, 0), self.W, 10, color=theme.ACCENT, zorder=2))
        self._text(ax, self.W / 2, self.H / 2 + 40, "سپاس از توجه شما" if fa_mode else "Thank you", size=54,
                   weight="bold", ha="center", fa_text=fa_mode)
        self._text(ax, self.W / 2, self.H / 2 - 50,
                   "پرسش‌ها و گفتگو" if fa_mode else "Questions & discussion", size=24,
                   color="#cfe6f2", ha="center", fa_text=fa_mode)
        self.slides.append((self._save(fig, idx), script.get("end", "")))
        # fix total in chrome of already drawn slides is approximate; keep as is
        return self.slides

    def _num(self, n):
        digits = "۰۱۲۳۴۵۶۷۸۹"
        return "".join(digits[int(d)] for d in str(n))


def slides_to_video(slide_paths, audio_dir, out_mp4, lang="fa", per_slide_default=14, voice=None):
    """Concatenate slides with per-slide audio (or silence) into a 16:9 MP4."""
    import imageio_ffmpeg

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    tmp = out_mp4 + ".parts"
    os.makedirs(tmp, exist_ok=True)
    parts = []
    for i, path in enumerate(slide_paths, 1):
        audio = os.path.join(audio_dir, f"narration_{i:03d}.mp3") if audio_dir else None
        part = os.path.join(tmp, f"part_{i:03d}.mp4")
        dur = per_slide_default
        if audio and os.path.exists(audio):
            dur = max(4.0, _audio_duration(ffmpeg, audio) + 0.6)
        cmd = [ffmpeg, "-y", "-loglevel", "error", "-loop", "1", "-i", path]
        if audio and os.path.exists(audio):
            cmd += ["-i", audio]
        cmd += ["-t", f"{dur:.2f}"]
        if audio and os.path.exists(audio):
            cmd += ["-af", "apad", "-shortest"]
        else:
            cmd += ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"]
        cmd += ["-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=0x08415c",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2", "-r", "25", part]
        subprocess.run(cmd, check=True)
        parts.append(part)
    lst = os.path.join(tmp, "list.txt")
    with open(lst, "w") as fh:
        for p in parts:
            fh.write(f"file '{p}'\n")
    subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", out_mp4], check=True)
    return out_mp4


def _audio_duration(ffmpeg, path):
    import re

    proc = subprocess.run([ffmpeg, "-i", path], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", proc.stderr)
    if not m:
        return 10.0
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)
