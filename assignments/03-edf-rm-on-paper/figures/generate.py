#!/usr/bin/env python3
"""Generate every figure of Assignment 3 (EDF/RM on paper) in Persian and English.

All schedules are read from data/paper_work.txt, i.e. from the hand-written answer,
so the figures can never drift away from the verified worksheet.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
sys.path.insert(0, os.path.join(ROOT, "code"))
os.chdir(REPO)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

from reportkit import diagrams as D
from reportkit import theme
from reportkit.fonts import register_matplotlib_fonts

register_matplotlib_fonts()
plt.rcParams["font.family"] = "Vazirmatn"
C = theme.PALETTE

from workbook import (Task, analyse, dbf, edf_feasible, hyperperiod, load,
                      max_demand_deficit, rm_bound, rta_table, utilisation)

OUT = os.path.join(ROOT, "figures")
DATA = json.load(open(os.path.join(ROOT, "data", "paper_check.json"), encoding="utf-8"))
WB = load(os.path.join(ROOT, "data", "paper_work.txt"))
TASKS = WB.tasks
H = hyperperiod(TASKS)
TASK_COLORS = [C[0], C[1], C[2]]

L = {
    "fa": dict(
        tick="تیک", rm="نرخ یکنواخت (RM)", edf="نزدیک‌ترین مهلت (EDF)",
        deadline="مهلت", release="آزادسازی", miss="مهلت از دست رفته",
        paper="برگه حل دستی", verified="تأییدشده توسط بازبین",
    ),
    "en": dict(
        tick="tick", rm="Rate-monotonic (RM)", edf="Earliest deadline first (EDF)",
        deadline="deadline", release="release", miss="deadline missed",
        paper="hand-drawn sheet", verified="checked by the verifier",
    ),
}


def tr(k, lang):
    return L[lang][k]


def gantt_from_rows(rows, path, lang, title, horizon):
    """Draw the hand-written rows as a proper Gantt chart (paper look)."""
    names = list(rows)
    fig, ax = plt.subplots(figsize=(11, 3.9), dpi=170)
    for i, name in enumerate(names):
        y = len(names) - i - 1
        row = rows[name]
        for tick, ch in enumerate(row[:horizon]):
            if ch == "#":
                ax.add_patch(Rectangle((tick, y - 0.30), 1, 0.60,
                                       facecolor=TASK_COLORS[i], edgecolor="white", linewidth=0.5))
        # hatching under the row to mimic graph paper
        ax.add_patch(Rectangle((0, y - 0.42), horizon, 0.84, facecolor="none",
                               edgecolor="#e3ebf1", linewidth=0.6, zorder=0))
        t = next(x for x in TASKS if x.name == name)
        for d in range(t.period, horizon + 1, t.period):
            ax.plot([d, d], [y - 0.42, y + 0.42], color="#c1440e", linewidth=1.1, zorder=4)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names[::-1], fontsize=9)
    ax.set_xlim(0, horizon)
    ax.set_ylim(-0.55, len(names) - 0.45)
    ax.set_xticks(range(0, horizon + 1, 2))
    ax.set_xlabel(tr("tick", lang), fontsize=8.8)
    ax.set_title(title, fontsize=11, color=theme.ACCENT_DARK, fontweight="bold", pad=8)
    ax.grid(axis="x", color="#eef3f7", linewidth=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


os.makedirs(OUT, exist_ok=True)
RM_ROWS = next(s.rows for s in WB.schedules if s.algorithm == "rm")
EDF_ROWS = next(s.rows for s in WB.schedules if s.algorithm == "edf")

# ---------------------------------------------------------------- fig 3, 4: hand schedules
for lang in ("fa", "en"):
    gantt_from_rows(RM_ROWS, os.path.join(OUT, f"fig03_hand_rm_{lang}.png"), lang,
                    "RM: " + tr("paper", lang), H)
    gantt_from_rows(EDF_ROWS, os.path.join(OUT, f"fig04_hand_edf_{lang}.png"), lang,
                    "EDF: " + tr("paper", lang), H)

# ---------------------------------------------------------------- fig 5: the missed deadline
for lang in ("fa", "en"):
    fig, ax = plt.subplots(figsize=(9.4, 3.5), dpi=170)
    row = RM_ROWS["P3"][:12]
    for tick, ch in enumerate(row):
        ax.add_patch(Rectangle((tick, 0.6), 1, 0.5,
                               facecolor=C[2] if ch == "#" else "#f3f6f8",
                               edgecolor="white", linewidth=0.8))
        if ch == "#":
            ax.text(tick + 0.5, 0.85, "1", ha="center", va="center", color="white", fontsize=8)
    ax.axvline(8, color="#c1440e", linewidth=2.0)
    ax.annotate(tr("deadline", lang), xy=(8, 1.28), xytext=(8.3, 1.42), fontsize=9, color="#c1440e")
    ax.annotate(tr("miss", lang), xy=(6.5, 1.05), xytext=(4.4, 1.44), fontsize=9.5,
                color="#c1440e", fontweight="bold",
                arrowprops=dict(arrowstyle="->", color="#c1440e", lw=1.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0.3, 1.7)
    ax.set_yticks([])
    ax.set_xticks(range(0, 13))
    ax.set_xlabel(tr("tick", lang), fontsize=8.8)
    ax.set_title(("P3 در RM: فقط ۲ از ۳ تیک پیش از مهلت" if lang == "fa" else
                  "P3 under RM: only 2 of 3 ticks before its deadline"),
                 fontsize=10.8, color=theme.ACCENT_DARK, fontweight="bold")
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    fig.savefig(os.path.join(OUT, f"fig05_miss_{lang}.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

# ---------------------------------------------------------------- fig 6: response times vs deadlines
for lang in ("fa", "en"):
    tab = rta_table(TASKS)
    names = [t.name for t in sorted(TASKS, key=lambda x: x.period)]
    rts = [tab[n]["R"] if tab[n]["R"] is not None else tab[n]["T"] + 2 for n in names]
    dls = [tab[n]["T"] for n in names]
    x = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(8.8, 3.6), dpi=170)
    ax.bar(x - 0.2, rts, 0.4, label="R", color=C[0])
    ax.bar(x + 0.2, dls, 0.4, label="T (=D)", color="#c9d6df")
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.set_ylabel(("زمان (تیک)" if lang == "fa" else "time (ticks)"), fontsize=8.6)
    ax.set_title(("زمان پاسخ دقیق در برابر مهلت؛ ستون قرمز P3 یعنی شکست"
                  if lang == "fa" else
                  "Exact response time versus deadline; the red bar for P3 is a failure"),
                 fontsize=10.6, color=theme.ACCENT_DARK, fontweight="bold")
    ax.legend(fontsize=8, frameon=False)
    ax.grid(axis="y", color="#eef3f7", lw=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.savefig(os.path.join(OUT, f"fig06_response_{lang}.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

# ---------------------------------------------------------------- fig 7: dbf curve
for lang in ("fa", "en"):
    Ls = list(range(0, H + 1))
    ds = [dbf(TASKS, l) for l in Ls]
    fig, ax = plt.subplots(figsize=(8.8, 3.7), dpi=170)
    ax.plot(Ls, Ls, ls="--", lw=1.3, color="#9aa7b2", label="L")
    ax.step(Ls, ds, where="post", lw=2.0, color=C[1], label="dbf(L)")
    worst = max_demand_deficit(TASKS)
    ax.fill_between(Ls, ds, Ls, where=[d > l for d, l in zip(ds, Ls)],
                    color="#c1440e", alpha=0.25, step="post")
    ax.set_xlabel(("طول پنجره L (تیک)" if lang == "fa" else "window length L (ticks)"), fontsize=8.6)
    ax.set_ylabel(("تقاضای پردازنده" if lang == "fa" else "processor demand"), fontsize=8.6)
    ax.set_title(("تابع تقاضا زیر خط L می‌ماند: EDF قابل زمان‌بندی است" if lang == "fa" else
                  "The demand bound stays below L: EDF is schedulable"),
                 fontsize=10.6, color=theme.ACCENT_DARK, fontweight="bold")
    ax.legend(fontsize=8, frameon=False)
    ax.grid(color="#eef3f7", lw=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.savefig(os.path.join(OUT, f"fig07_dbf_{lang}.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

# ---------------------------------------------------------------- fig 8: utilisation vs bound
for lang in ("fa", "en"):
    fig, ax = plt.subplots(figsize=(8.6, 3.4), dpi=170)
    u = utilisation(TASKS)
    ax.barh([0], [u], height=0.34, color=C[0], label="U")
    ax.barh([0], [rm_bound(3)], height=0.20, color="#c9d6df", label="n(2^(1/n)-1)")
    ax.axvline(1.0, color="#9aa7b2", ls="--", lw=1.1)
    ax.text(u - 0.01, 0.26, f"{u:.3f}", ha="right", fontsize=9, color=theme.INK)
    ax.text(rm_bound(3) + 0.006, -0.26, f"{rm_bound(3):.3f}", fontsize=8.6, color=theme.MUTED)
    ax.set_xlim(0, 1.06)
    ax.set_yticks([])
    ax.set_xlabel(("بهره‌وری" if lang == "fa" else "utilisation"), fontsize=8.6)
    ax.set_title(("بهره‌وری مجموعه بالاتر از کران RM است" if lang == "fa" else
                  "The task-set utilisation is above the RM bound"),
                 fontsize=10.6, color=theme.ACCENT_DARK, fontweight="bold")
    ax.legend(fontsize=8, frameon=False, loc="lower right")
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    fig.savefig(os.path.join(OUT, f"fig08_bound_{lang}.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

# ---------------------------------------------------------------- fig 2: flowchart of the method
FLOW_FA = ["شروع", "رسم محور زمان", "آزادسازی کارها", "انتخاب بر اساس قاعده",
           "کشیدن یک تیک", "آیا مهلت باقی است؟", "پایان"]
FLOW_EN = ["Start", "Draw the time axis", "Release jobs", "Pick by the rule",
           "Shade one tick", "Deadline still open?", "Done"]
for lang, steps, title, br in (
        ("fa", FLOW_FA, "روند حل دستی یک زمان‌بندی", ("بله", "خیر")),
        ("en", FLOW_EN, "Hand-solving one schedule", ("yes", "no"))):
    D.flowchart(steps, os.path.join(OUT, f"fig02_flowchart_{lang}.png"), lang, title,
                decision_at=5, branch_labels=br, figsize=(9.0, 6.6))

# ---------------------------------------------------------------- fig 1: gantt of the work plan
G_FA = [("خواندن صورت تمرین و استخراج پارامترها", 0, 1),
        ("محاسبه بهره‌وری و کران RM", 1, 1),
        ("رسم دستی زمان‌بندی RM", 2, 2),
        ("رسم دستی زمان‌بندی EDF", 4, 2),
        ("تحلیل زمان پاسخ", 5, 2),
        ("نوشتن بازبین خودکار", 6, 3),
        ("آزمون و اعتبارسنجی", 9, 2),
        ("نگارش گزارش دوزبانه", 10, 4)]
G_EN = [("Read the brief and extract parameters", 0, 1),
        ("Compute utilisation and the RM bound", 1, 1),
        ("Draw the RM schedule by hand", 2, 2),
        ("Draw the EDF schedule by hand", 4, 2),
        ("Response-time analysis", 5, 2),
        ("Write the automatic verifier", 6, 3),
        ("Test and validate", 9, 2),
        ("Write the bilingual report", 10, 4)]
for lang, g, title, xl in (("fa", G_FA, "برنامه انجام تمرین سوم", "زمان (روز)"),
                           ("en", G_EN, "Assignment 3 work plan", "time (days)")):
    D.gantt(g, os.path.join(OUT, f"fig01_gantt_{lang}.png"), lang, title, xl, figsize=(10, 4.4))

# ---------------------------------------------------------------- fig 9: architecture
for lang, blocks, title in (
        ("fa", [("برگه دستی\n(متن ساده)", 0.4, 2.0, 2.2, 1.2, 0),
                ("تجزیه‌گر", 3.0, 2.0, 1.9, 1.2, 1),
                ("بازبین", 5.3, 2.0, 1.9, 1.2, 2),
                ("تحلیل نظری", 7.6, 2.0, 2.1, 1.2, 3)],
         "معماری بازبین دفترچه"),
        ("en", [("Paper sheet\n(plain text)", 0.4, 2.0, 2.2, 1.2, 0),
                ("Parser", 3.0, 2.0, 1.9, 1.2, 1),
                ("Checker", 5.3, 2.0, 1.9, 1.2, 2),
                ("Theory engine", 7.6, 2.0, 2.1, 1.2, 3)],
         "Workbook verifier architecture")):
    D.block_diagram(blocks, os.path.join(OUT, f"fig09_architecture_{lang}.png"), lang, title,
                    arrows=[(2.6, 2.6, 3.0, 2.6), (4.9, 2.6, 5.3, 2.6), (7.2, 2.6, 7.6, 2.6)],
                    figsize=(10, 3.6))

# ---------------------------------------------------------------- fig 10: priority timeline (RM vs EDF)
for lang in ("fa", "en"):
    fig, ax = plt.subplots(figsize=(9.6, 3.5), dpi=170)
    for i, t in enumerate(sorted(TASKS, key=lambda x: x.period)):
        # dynamic priority = absolute deadline of the current job
        for k in range(0, H // t.period):
            r = k * t.period
            ax.plot([r, r + t.period], [i, i], color="#dbe6ee", lw=5, solid_capstyle="butt")
            ax.text(r + t.period / 2, i, f"{r + t.deadline}", ha="center", va="center",
                    fontsize=7.2, color=theme.MUTED)
    ax.set_yticks(range(3))
    ax.set_yticklabels([t.name for t in sorted(TASKS, key=lambda x: x.period)], fontsize=9)
    ax.set_xlim(0, H)
    ax.set_xlabel(("تیک (عدد داخل نوار: مهلت مطلق)" if lang == "fa" else
                   "tick (number inside the bar: absolute deadline)"), fontsize=8.4)
    ax.set_title(("مهلت‌های مطلق: EDF هر لحظه کوچک‌ترین را انتخاب می‌کند" if lang == "fa" else
                  "Absolute deadlines: EDF always picks the smallest at every instant"),
                 fontsize=10.4, color=theme.ACCENT_DARK, fontweight="bold")
    ax.grid(axis="x", color="#eef3f7", lw=0.6)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    fig.savefig(os.path.join(OUT, f"fig10_deadlines_{lang}.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

# ---------------------------------------------------------------- fig 11: workload profile
for lang in ("fa", "en"):
    fig, ax = plt.subplots(figsize=(9.2, 3.4), dpi=170)
    load_by_tick = [sum(1 for n in RM_ROWS if RM_ROWS[n][i] == "#") for i in range(H)]
    ax.bar(range(H), load_by_tick, color=C[2], width=0.85)
    ax.axhline(1, color="#c1440e", ls="--", lw=1.1)
    ax.set_ylim(0, 1.4)
    ax.set_xlabel(tr("tick", lang), fontsize=8.6)
    ax.set_ylabel(("کارهای در حال اجرا" if lang == "fa" else "tasks running"), fontsize=8.6)
    ax.set_title(("هیچ تیکی بیش از یک کار اجرا نمی‌شود" if lang == "fa" else
                  "No tick ever runs more than one task"), fontsize=10.4,
                 color=theme.ACCENT_DARK, fontweight="bold")
    ax.grid(axis="y", color="#eef3f7", lw=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.savefig(os.path.join(OUT, f"fig11_load_{lang}.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

# ---------------------------------------------------------------- fig 12: comparison of the two answers
for lang in ("fa", "en"):
    fig, ax = plt.subplots(figsize=(9.4, 3.6), dpi=170)
    labels = [t.name for t in sorted(TASKS, key=lambda x: x.period)]
    rm_served = [RM_ROWS[n][:H].count("#") for n in labels]
    edf_served = [EDF_ROWS[n][:H].count("#") for n in labels]
    need = [len(t.jobs_in(H)) * t.wcet for t in sorted(TASKS, key=lambda x: x.period)]
    x = np.arange(len(labels))
    ax.bar(x - 0.26, rm_served, 0.26, label="RM", color=C[1])
    ax.bar(x, edf_served, 0.26, label="EDF", color=C[0])
    ax.bar(x + 0.26, need, 0.26, label=("نیاز" if lang == "fa" else "required"), color="#c9d6df")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel(("تیک‌های اختصاص‌یافته" if lang == "fa" else "ticks granted"), fontsize=8.6)
    ax.set_title(("خدمت ارائه‌شده در یک ابررسال: RM به P3 کمتر از نیاز می‌دهد" if lang == "fa" else
                  "Service over one hyperperiod: RM under-serves P3"), fontsize=10.4,
                 color=theme.ACCENT_DARK, fontweight="bold")
    ax.legend(fontsize=8, frameon=False)
    ax.grid(axis="y", color="#eef3f7", lw=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.savefig(os.path.join(OUT, f"fig12_service_{lang}.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

print("figures:", len([f for f in os.listdir(OUT) if f.endswith(".png")]))
