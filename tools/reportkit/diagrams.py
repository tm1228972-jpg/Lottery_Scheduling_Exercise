"""Bilingual diagrams: Gantt charts, flowcharts, block diagrams, timeline charts.

Matplotlib's raqm text engine performs Arabic shaping + bidi, therefore Persian
strings are passed straight through (never pre-shaped) - this is what guarantees
the figures are never mirrored.
"""
from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

from . import theme
from .fonts import register_matplotlib_fonts

C = theme.PALETTE

plt.rcParams.update({
    "font.family": "Vazirmatn",
    "axes.edgecolor": "#9fb0bd",
    "axes.labelcolor": theme.INK,
    "text.color": theme.INK,
    "xtick.color": theme.MUTED,
    "ytick.color": theme.MUTED,
    "savefig.facecolor": "white",
    "figure.facecolor": "white",
})


def setup():
    register_matplotlib_fonts()


def _save(fig, path, dpi=190):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


# --------------------------------------------------------------------------- Gantt
def gantt(tasks, path, lang="fa", title="", xlabel="", unit_days=True, colors=None, figsize=(10, 5.4)):
    """tasks: list of (name, start, duration, milestone?) in days."""
    setup()
    fig, ax = plt.subplots(figsize=figsize, dpi=170)
    n = len(tasks)
    ypos = list(range(n))[::-1]
    for i, ((name, start, dur), y) in enumerate(zip(tasks, ypos)):
        color = (colors or C)[i % len(C or C)]
        ax.barh(y, dur, left=start, height=0.52, color=color, alpha=0.92, edgecolor="white", linewidth=0.8)
        label = f"{dur:g}"
        ax.text(start + dur + 0.25, y, label, va="center", fontsize=7.4, color=theme.MUTED)
    ax.set_yticks(ypos)
    ax.set_yticklabels([t[0] for t in tasks], fontsize=8.4)
    ax.set_xlabel(xlabel or ("زمان (روز)" if lang == "fa" else "Time (days)"), fontsize=9)
    if title:
        ax.set_title(title, fontsize=11.5, pad=10, color=theme.ACCENT_DARK, fontweight="bold")
    ax.grid(axis="x", color="#e2e9ef", linewidth=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(labelsize=8)
    ax.margins(x=0.02)
    return _save(fig, path)


# --------------------------------------------------------------------------- Flowchart
def flowchart(steps, path, lang="fa", title="", decision_at=None, branch_labels=None, figsize=(9.6, 6.4),
              vertical=True):
    """steps: list of labels; decision_at: index rendered as a diamond with two branches."""
    setup()
    fig, ax = plt.subplots(figsize=figsize, dpi=170)
    ax.set_xlim(0, 10)
    n = len(steps)
    top = n * 1.12 + 0.7
    ax.set_ylim(0, top)
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=11.5, color=theme.ACCENT_DARK, fontweight="bold", pad=6)
    cx = 4.2
    for i, label in enumerate(steps):
        y = top - 0.9 - i * 1.12
        is_decision = (decision_at is not None and i == decision_at)
        if is_decision:
            w, h = 2.0, 0.86
            pts = [(cx, y + h), (cx + w * 0.75, y), (cx, y - h), (cx - w * 0.75, y)]
            ax.add_patch(plt.Polygon(pts, closed=True, facecolor="#fff4dc", edgecolor=theme.GOLD, linewidth=1.4))
            import textwrap

            wrapped = "\n".join(textwrap.wrap(label, 22)) if len(label) > 22 else label
            ax.text(cx, y, wrapped, ha="center", va="center", fontsize=7.8)
        else:
            w = 4.0 if len(label) < 46 else 4.7
            box = FancyBboxPatch((cx - w / 2, y - 0.34), w, 0.68, boxstyle="round,pad=0.04,rounding_size=0.12",
                                 facecolor=theme.ACCENT_LIGHT if i % 2 == 0 else "#eef6ef",
                                 edgecolor=theme.ACCENT, linewidth=1.1)
            ax.add_patch(box)
            import textwrap

            wrapped = "\n".join(textwrap.wrap(label, 52)) if len(label) > 52 else label
            ax.text(cx, y, wrapped, ha="center", va="center", fontsize=7.8)
        if i < n - 1:
            # start the arrow below the current box bottom and stop above the next box top
            y_next = top - 0.9 - (i + 1) * 1.12
            top_cur = y - (0.86 if is_decision else 0.34)
            bot_next = y_next + (0.86 if (decision_at is not None and i + 1 == decision_at) else 0.34)
            ax.annotate("", xy=(cx, bot_next + 0.02), xytext=(cx, top_cur - 0.02),
                        arrowprops=dict(arrowstyle="-|>", color="#5b6b7c", lw=1.0,
                                        shrinkA=0, shrinkB=2))
    if decision_at is not None and branch_labels:
        y = top - 0.9 - decision_at * 1.12
        for side, txt, color in (("right", branch_labels[0], "#2e7d4f"), ("left", branch_labels[1], "#c1440e")):
            dx = 2.6 if side == "right" else -2.6
            ax.annotate("", xy=(cx + dx * 0.78, y), xytext=(cx + (0.7 if side == "right" else -0.7) * 1.0, y),
                        arrowprops=dict(arrowstyle="-|>", color=color, lw=1.1))
            ax.text(cx + dx * 0.86, y + 0.14, txt, fontsize=7.4, color=color,
                    ha="left" if side == "right" else "right")
    return _save(fig, path)


# --------------------------------------------------------------------------- block diagram
def block_diagram(blocks, path, lang="fa", title="", arrows=None, figsize=(10, 4.6)):
    """blocks: list of (label, x, y, w, h, color_idx). Coordinates in 0..10 / 0..5."""
    setup()
    fig, ax = plt.subplots(figsize=figsize, dpi=170)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=11.5, color=theme.ACCENT_DARK, fontweight="bold", pad=8)
    for i, (label, x, y, w, h, ci) in enumerate(blocks):
        col = C[ci % len(C)]
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.1",
                                    facecolor=col, alpha=0.16, edgecolor=col, linewidth=1.3))
        import textwrap

        ax.text(x + w / 2, y + h / 2, "\n".join(textwrap.wrap(label, 26)), ha="center", va="center",
                fontsize=7.4)
    for (x1, y1, x2, y2) in (arrows or []):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=11,
                                     color="#5b6b7c", linewidth=1.1))
    return _save(fig, path)


# --------------------------------------------------------------------------- timeline / scheduling chart
def timeline(rows, path, lang="fa", title="", horizon=30, colors=None, figsize=(10, 4.4), unit="ms"):
    """rows: list of (name, [(start, dur, label), ...])"""
    setup()
    fig, ax = plt.subplots(figsize=figsize, dpi=170)
    for i, (name, segs) in enumerate(rows):
        y = len(rows) - i - 1
        for j, (start, dur, label) in enumerate(segs):
            ax.barh(y, dur, left=start, height=0.46, color=(colors or C)[j % len(colors or C)],
                    edgecolor="white", linewidth=0.6)
            if dur > horizon * 0.045 and label:
                ax.text(start + dur / 2, y, label, ha="center", va="center", fontsize=6.8, color="white")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=8.2)
    ax.set_xlim(0, horizon)
    ax.set_xlabel(f"({unit})" if unit else "", fontsize=8.4)
    if title:
        ax.set_title(title, fontsize=11.2, color=theme.ACCENT_DARK, fontweight="bold", pad=8)
    ax.grid(axis="x", color="#e6edf2", linewidth=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    return _save(fig, path)


# --------------------------------------------------------------------------- bar / line
def bar(values, labels, path, lang="fa", title="", ylabel="", xlabel="", colors=None, figsize=(8.4, 3.8),
        rotate=0, value_fmt="{:.1f}", show_values=True):
    setup()
    fig, ax = plt.subplots(figsize=figsize, dpi=170)
    bars = ax.bar(labels, values, color=(colors or C)[: len(values)] if colors else C[: len(values)],
                  width=0.6, edgecolor="white", linewidth=0.8)
    if show_values:
        for b, v in zip(bars, values):
            ax.text(b.get_x() + b.get_width() / 2, b.get_height(), value_fmt.format(v),
                    ha="center", va="bottom", fontsize=7.4, color=theme.MUTED)
    ax.set_ylabel(ylabel, fontsize=8.6)
    ax.set_xlabel(xlabel, fontsize=8.6)
    if title:
        ax.set_title(title, fontsize=11, color=theme.ACCENT_DARK, fontweight="bold", pad=8)
    ax.grid(axis="y", color="#e6edf2", linewidth=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(labelsize=7.8)
    if rotate:
        plt.setp(ax.get_xticklabels(), rotation=rotate, ha="right" if rotate else "center")
    return _save(fig, path)


def lines(series, x, path, lang="fa", title="", ylabel="", xlabel="", figsize=(8.6, 3.9), markers=None):
    setup()
    fig, ax = plt.subplots(figsize=figsize, dpi=170)
    for i, (name, ys) in enumerate(series):
        ax.plot(x, ys, label=name, color=C[i % len(C)], linewidth=1.8,
                marker=(markers or "o"), markersize=3.4)
    ax.set_title(title, fontsize=11, color=theme.ACCENT_DARK, fontweight="bold", pad=8)
    ax.set_ylabel(ylabel, fontsize=8.6)
    ax.set_xlabel(xlabel, fontsize=8.6)
    ax.legend(fontsize=7.8, frameon=False)
    ax.grid(color="#e6edf2", linewidth=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(labelsize=7.8)
    return _save(fig, path)


def pie(values, labels, path, lang="fa", title="", figsize=(5.4, 4.2), donut=False):
    setup()
    fig, ax = plt.subplots(figsize=figsize, dpi=170)
    wedges, texts, autotexts = ax.pie(values, labels=labels, autopct="%1.0f%%", startangle=100,
                                      colors=C[: len(values)], textprops={"fontsize": 8},
                                      wedgeprops=dict(width=0.42, edgecolor="white") if donut else dict(edgecolor="white"))
    for t in autotexts:
        t.set_color("white")
        t.set_fontsize(7.6)
    if title:
        ax.set_title(title, fontsize=10.5, color=theme.ACCENT_DARK, fontweight="bold")
    return _save(fig, path)


def histogram(values_a, values_b, labels, path, lang="fa", title="", xlabel="", figsize=(8.6, 3.9), bins=30):
    setup()
    fig, ax = plt.subplots(figsize=figsize, dpi=170)
    ax.hist(values_a, bins=bins, alpha=0.66, label=labels[0], color=C[0], edgecolor="white", linewidth=0.4)
    ax.hist(values_b, bins=bins, alpha=0.66, label=labels[1], color=C[1], edgecolor="white", linewidth=0.4)
    ax.set_title(title, fontsize=10.6, color=theme.ACCENT_DARK, fontweight="bold", pad=8)
    ax.set_xlabel(xlabel, fontsize=8.4)
    ax.set_ylabel("Frequency" if lang != "fa" else "فراوانی", fontsize=8.4)
    ax.legend(fontsize=7.8, frameon=False)
    ax.grid(axis="y", color="#e6edf2", linewidth=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    return _save(fig, path)


def heatmap(matrix, row_labels, col_labels, path, lang="fa", title="", figsize=(7.6, 4.2), cmap="YlGnBu"):
    setup()
    fig, ax = plt.subplots(figsize=figsize, dpi=170)
    im = ax.imshow(matrix, cmap=cmap, aspect="auto")
    ax.set_xticks(range(len(col_labels)))
    ax.set_xticklabels(col_labels, fontsize=7.6, rotation=0)
    ax.set_yticks(range(len(row_labels)))
    ax.set_yticklabels(row_labels, fontsize=7.8)
    for i in range(len(row_labels)):
        for j in range(len(col_labels)):
            ax.text(j, i, f"{matrix[i][j]:.2f}", ha="center", va="center", fontsize=6.8, color="#1b2430")
    if title:
        ax.set_title(title, fontsize=10.6, color=theme.ACCENT_DARK, fontweight="bold", pad=8)
    fig.colorbar(im, ax=ax, fraction=0.028, pad=0.02)
    return _save(fig, path)
