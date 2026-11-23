"""Theme: colours, spacing, page geometry shared by PDF, DOCX and slides."""
from __future__ import annotations

INK = "#1b2430"
MUTED = "#5b6b7c"
ACCENT = "#0b6e99"
ACCENT_DARK = "#08415c"
ACCENT_LIGHT = "#e6f2f7"
GOLD = "#b8860b"
RULE = "#cfd8e0"
PANEL = "#f4f7f9"
ZEBRA = "#eef4f7"

PALETTE = ["#0b6e99", "#e07a5f", "#3d9970", "#b8860b", "#6a4c93", "#2a9d8f", "#c1440e", "#577590"]

PAGE = dict(
    size="A4",
    left=22 * 2.834645,   # ~22 mm
    right=22 * 2.834645,
    top=20 * 2.834645,
    bottom=20 * 2.834645,
    header=12 * 2.834645,
    footer=11 * 2.834645,
)

SLIDE = dict(width=1280, height=720, dpi=110)


def hexrgb(h: str):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) / 255 for i in (0, 2, 4))
