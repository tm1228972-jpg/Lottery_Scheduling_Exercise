"""Font helpers: register Vazirmatn (Persian/Arabic + Latin) for ReportLab and Matplotlib."""
from __future__ import annotations

import os
import functools

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FONT_DIR = os.path.join(ROOT, "assets", "fonts")

FILES = {
    "Vazir": "Vazirmatn-Regular.ttf",
    "Vazir-Bold": "Vazirmatn-Bold.ttf",
    "Vazir-Medium": "Vazirmatn-Medium.ttf",
}

_registered = False


def register_reportlab_fonts() -> None:
    """Register Vazirmatn faces once per process."""
    global _registered
    if _registered:
        return
    for name, fname in FILES.items():
        path = os.path.join(FONT_DIR, fname)
        pdfmetrics.registerFont(TTFont(name, path))
    from reportlab.pdfbase.pdfmetrics import registerFontFamily

    registerFontFamily(
        "Vazir", normal="Vazir", bold="Vazir-Bold", italic="Vazir", boldItalic="Vazir-Bold"
    )
    _registered = True


@functools.lru_cache(maxsize=1)
def register_matplotlib_fonts() -> str:
    """Register Vazirmatn with Matplotlib; return family name to use."""
    from matplotlib import font_manager as fm

    for fname in FILES.values():
        fm.fontManager.addfont(os.path.join(FONT_DIR, fname))
    return "Vazirmatn"


def mono_for_pdf() -> str:
    """Monospaced font for code blocks (DejaVu Sans Mono ships with matplotlib)."""
    import matplotlib

    path = os.path.join(
        os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf", "DejaVuSansMono.ttf"
    )
    return path


def register_mono() -> None:
    register_reportlab_fonts()
    from reportlab.pdfbase.pdfmetrics import registerFont

    registerFont(TTFont("Mono", mono_for_pdf()))
    bold = os.path.join(
        os.path.dirname(__import__("matplotlib").__file__),
        "mpl-data",
        "fonts",
        "ttf",
        "DejaVuSansMono-Bold.ttf",
    )
    registerFont(TTFont("Mono-Bold", bold))
