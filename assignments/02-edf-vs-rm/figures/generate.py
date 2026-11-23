#!/usr/bin/env python3
"""Regenerate all figures of Assignment 2 (EDF vs RM) from real simulator data."""
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

from reportkit import diagrams as D
from reportkit import theme
from reportkit.fonts import register_matplotlib_fonts

register_matplotlib_fonts()
plt.rcParams["font.family"] = "Vazirmatn"
C = theme.PALETTE

from rt_sim import Task, hyperperiod, lcm, random_taskset, simulate

OUT = os.path.join(ROOT, "figures")
DATA = json.load(open(os.path.join(ROOT, "data", "rt_results.json"), encoding="utf-8"))

SAMPLE = [Task("T1", 10, 2), Task("T2", 15, 3), Task("T3", 30, 7), Task("T4", 40, 9)]


LANG_SUFFIX = {"fa": "fa", "en": "en"}


def tr(fa, en, lang):
    return fa if lang == "fa" else en


def schedule_figure(alg, out_dir, base, title_fa, title_en, xlabel_fa="زمان (تیک)",
                    xlabel_en="Time (ticks)", colors=None):
    """Draw a real Gantt-style schedule chart for one algorithm, in both languages."""
    tasks = SAMPLE
    h = hyperperiod(tasks)
    res = simulate(tasks, alg, h, trace=True)
    tl = res["timeline"]
    names = [t.name for t in tasks]
    for lang in ("fa", "en"):
        fig, ax = plt.subplots(figsize=(11, 3.4), dpi=170)
        for i, name in enumerate(names):
            y = len(names) - i - 1
            for tick in range(h):
                if tl[tick] == name:
                    ax.barh(y, 1, left=tick, height=0.55, color=C[i], edgecolor="white", linewidth=0.4)
            for d in range(tasks[i].period, h + 1, tasks[i].period):
                ax.plot([d, d], [y - 0.34, y + 0.34], color="#c1440e", linewidth=1.1)
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names[::-1], fontsize=8.4)
        ax.set_xlim(0, h)
        ax.set_xlabel(tr(xlabel_fa, xlabel_en, lang), fontsize=8.6)
        ax.set_title(tr(title_fa, title_en, lang), fontsize=11,
                     color=theme.ACCENT_DARK, fontweight="bold", pad=8)
        ax.grid(axis="x", color="#e6edf2", linewidth=0.7)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        fig.savefig(os.path.join(out_dir, f"{base}_{lang}.png"), bbox_inches="tight", facecolor="white")
        plt.close(fig)
    return res


os.makedirs(OUT, exist_ok=True)

# 1-3 real schedules
rm = schedule_figure("rm", OUT, "fig03_schedule_rm",
                     "زمان‌بندی RM روی مجموعه نمونه (نشانگرهای قرمز: مهلت‌ها)",
                     "RM schedule of the sample set (red markers: deadlines)")
edf = schedule_figure("edf", OUT, "fig04_schedule_edf",
                      "زمان‌بندی EDF روی مجموعه نمونه",
                      "EDF schedule of the sample set")
fcfs = schedule_figure("fcfs", OUT, "fig05_schedule_fcfs",
                       "زمان‌بندی FCFS روی مجموعه نمونه (بیشترین تأخیر)",
                       "FCFS schedule of the sample set (worst latency)")

# 4 utilisation sweep (both languages)
rows = DATA["sweep"]["rows"]
u = [r["utilisation"] for r in rows]
for lang in ("fa", "en"):
    fig, ax = plt.subplots(figsize=(8.8, 3.9), dpi=170)
    ax.plot(u, [r["rm_misses"] for r in rows], marker="o", lw=2, color=C[1], label="RM")
    ax.plot(u, [r["edf_misses"] for r in rows], marker="s", lw=2, color=C[0], label="EDF")
    ax.axvline(0.7568, ls="--", lw=1.2, color=C[3],
               label=tr("کران RM ≈ ۰٫۷۵۷", "RM bound = 0.757", lang))
    ax.set_xlabel(tr("بهره‌وری مجموعه", "Task-set utilisation", lang), fontsize=8.8)
    ax.set_ylabel(tr("تعداد از دست رفتن مهلت", "Deadline misses", lang), fontsize=8.8)
    ax.set_title(tr("نرخ از دست رفتن مهلت برحسب بهره‌وری (۴۰ مجموعه تصادفی در هر نقطه)",
                    "Deadline misses versus utilisation (40 random sets per point)", lang),
                 fontsize=10.6, color=theme.ACCENT_DARK, fontweight="bold")
    ax.legend(fontsize=8, frameon=False)
    ax.grid(color="#e6edf2", lw=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.savefig(os.path.join(OUT, f"fig06_sweep_{lang}.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

# 5 CPU utilisation of the sample by algorithm (both languages)
labels = ["RM", "EDF", "FCFS"]
busy = [sum(1 for x in simulate(SAMPLE, a, hyperperiod(SAMPLE), trace=True)["timeline"] if x != "idle")
        / hyperperiod(SAMPLE) * 100 for a in ("rm", "edf", "fcfs")]
for lang in ("fa", "en"):
    fig, ax = plt.subplots(figsize=(8.4, 3.4), dpi=170)
    ax.bar(labels, busy, color=[C[1], C[0], C[4]], width=0.5)
    for i, v in enumerate(busy):
        ax.text(i, v + 0.6, f"{v:.1f}%", ha="center", fontsize=8, color=theme.MUTED)
    ax.set_ylim(0, 100)
    ax.set_ylabel(tr("بهره‌وری پردازنده (٪)", "CPU utilisation (%)", lang), fontsize=8.6)
    ax.set_title(tr("بهره‌وری پردازنده در افق ابردوره ۱۲۰ تیکی",
                    "CPU utilisation over the 120-tick hyperperiod", lang),
                 fontsize=10.6, color=theme.ACCENT_DARK, fontweight="bold")
    ax.grid(axis="y", color="#e6edf2", lw=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.savefig(os.path.join(OUT, f"fig07_utilisation_{lang}.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

# 6 response time comparison (both languages)
names = [t.name for t in SAMPLE]
import numpy as np

x = np.arange(len(names))
w = 0.26
for lang in ("fa", "en"):
    fig, ax = plt.subplots(figsize=(9, 3.7), dpi=170)
    ax.bar(x - w, [rm["response_max"][n] for n in names], w, label="RM", color=C[1])
    ax.bar(x, [edf["response_max"][n] for n in names], w, label="EDF", color=C[0])
    ax.bar(x + w, [fcfs["response_max"][n] for n in names], w, label="FCFS", color=C[4])
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=8.4)
    ax.set_ylabel(tr("بیشترین زمان پاسخ (تیک)", "Maximum response time (ticks)", lang), fontsize=8.6)
    ax.set_title(tr("بیشترین زمان پاسخ هر کار در سه الگوریتم",
                    "Maximum response time per task under the three algorithms", lang),
                 fontsize=10.8, color=theme.ACCENT_DARK, fontweight="bold")
    ax.legend(fontsize=8, frameon=False)
    ax.grid(axis="y", color="#e6edf2", lw=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.savefig(os.path.join(OUT, f"fig08_response_{lang}.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

# 7 overload experiment (both languages)
ov = DATA["overload"]
names = ["T1", "T2", "T3", "T4"]
x = np.arange(4)
for lang in ("fa", "en"):
    fig, ax = plt.subplots(figsize=(8.4, 3.5), dpi=170)
    ax.bar(x - 0.2, [ov["rm"]["misses"][n] for n in names], 0.4, label="RM", color=C[1])
    ax.bar(x + 0.2, [ov["edf"]["misses"][n] for n in names], 0.4, label="EDF", color=C[0])
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.set_ylabel(tr("از دست رفتن مهلت", "Deadline misses", lang), fontsize=8.6)
    ax.set_title(tr(f"رفتار در اضافه‌بار (بهره‌وری {ov['heavy_utilisation']:.2f})",
                    f"Behaviour under overload (utilisation {ov['heavy_utilisation']:.2f})", lang),
                 fontsize=10.6, color=theme.ACCENT_DARK, fontweight="bold")
    ax.legend(fontsize=8, frameon=False)
    ax.grid(axis="y", color="#e6edf2", lw=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.savefig(os.path.join(OUT, f"fig09_overload_{lang}.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

# 8 utilisation bound curve (both languages)
n = np.arange(1, 21)
bound = n * (2 ** (1 / n) - 1)
for lang in ("fa", "en"):
    fig, ax = plt.subplots(figsize=(8.6, 3.6), dpi=170)
    ax.plot(n, bound * 100, marker="o", ms=3.6, lw=1.8, color=C[0])
    ax.axhline(69.3, ls="--", lw=1.2, color=C[3],
               label=tr("حد مجانبی ln ۲ ≈ ۶۹٫۳٪", "Asymptote ln 2 = 69.3%", lang))
    ax.set_xlabel(tr("تعداد کارها", "Number of tasks", lang), fontsize=8.6)
    ax.set_ylabel(tr("کران بهره‌وری RM (٪)", "RM utilisation bound (%)", lang), fontsize=8.6)
    ax.set_title(tr("کران بهره‌وری زمان‌بندی نرخ یکنواخت برحسب تعداد کارها",
                    "Rate-monotonic utilisation bound versus task count", lang),
                 fontsize=10.6, color=theme.ACCENT_DARK, fontweight="bold")
    ax.legend(fontsize=8, frameon=False)
    ax.grid(color="#e6edf2", lw=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.savefig(os.path.join(OUT, f"fig10_bound_{lang}.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

# 9 project gantt (both languages)
GANTT_FA = [("مطالعه نظریه زمان‌بندی بلادرنگ", 0, 4), ("طراحی شبیه‌ساز تیک‌محور", 4, 3),
            ("پیاده‌سازی RM و EDF", 7, 4), ("تحلیل زمان پاسخ دقیق", 9, 3),
            ("آزمایش جاروب بهره‌وری", 11, 5), ("آزمایش اضافه‌بار", 14, 3),
            ("نگارش گزارش دوزبانه", 17, 5), ("تهیه اسلاید", 21, 2)]
GANTT_EN = [("Real-time theory study", 0, 4), ("Tick simulator design", 4, 3),
            ("RM and EDF implementation", 7, 4), ("Response-time analysis", 9, 3),
            ("Utilisation sweep", 11, 5), ("Overload experiment", 14, 3),
            ("Bilingual report writing", 17, 5), ("Slide preparation", 21, 2)]
for lang, tasks_g, title, xl in (
        ("fa", GANTT_FA, "نمودار گانت انجام تمرین دوم", "زمان (روز)"),
        ("en", GANTT_EN, "Assignment plan: Gantt chart", "Time (days)")):
    D.gantt(tasks_g, os.path.join(OUT, f"fig01_gantt_{lang}.png"), lang, title, xl, figsize=(10, 4.7))

# 10 flowchart of EDF decision (both languages)
FLOW_FA = ["شروع تیک", "به‌روزرسانی کارهای آزادشده", "حذف کارهای پایان‌یافته",
           "آیا کار آماده‌ای وجود دارد؟", "انتخاب کار با نزدیک‌ترین مهلت",
           "اجرای یک تیک", "بررسی مهلت‌های گذشته", "پایان"]
FLOW_EN = ["Tick begins", "Release eligible jobs", "Drop completed jobs",
           "Any ready job?", "Pick the earliest deadline",
           "Execute one tick", "Check expired deadlines", "End of tick"]
for lang, steps, title, br in (
        ("fa", FLOW_FA, "روند تصمیم‌گیری EDF در هر تیک", ("بله", "خیر")),
        ("en", FLOW_EN, "EDF decision flow within one tick", ("yes", "no"))):
    D.flowchart(steps, os.path.join(OUT, f"fig02_flowchart_{lang}.png"), lang, title,
                decision_at=3, branch_labels=br, figsize=(9.6, 7.0))

# 11 architecture (both languages)
for lang, blocks, title in (
        ("fa", [("مجموعه کارها\n(T, C, D)", 0.4, 2.1, 2.1, 1.2, 0),
                ("شبیه‌ساز تیک‌محور", 2.9, 2.1, 2.2, 1.2, 1),
                ("سیاست RM / EDF / FCFS", 5.5, 2.1, 2.3, 1.2, 2),
                ("آمار و خط زمانی", 8.2, 2.1, 1.6, 1.2, 3)],
         "معماری شبیه‌ساز بلادرنگ"),
        ("en", [("Task set\n(T, C, D)", 0.4, 2.1, 2.1, 1.2, 0),
                ("Tick-based simulator", 2.9, 2.1, 2.2, 1.2, 1),
                ("Policy RM / EDF / FCFS", 5.5, 2.1, 2.3, 1.2, 2),
                ("Statistics and timeline", 8.2, 2.1, 1.6, 1.2, 3)],
         "Real-time simulator architecture")):
    D.block_diagram(blocks, os.path.join(OUT, f"fig11_architecture_{lang}.png"), lang, title,
                    arrows=[(2.5, 2.7, 2.9, 2.7), (5.1, 2.7, 5.5, 2.7), (7.8, 2.7, 8.2, 2.7)],
                    figsize=(10, 3.7))

# 12 utilisation heat map of random task sets (both languages)
sets = []
for s_ in range(1, 9):
    ts = random_taskset(s_, 4, 0.9)
    if ts:
        sets.append(ts)
mat = []
for ts in sets:
    h = min(hyperperiod(ts), 2000)
    r_rm = simulate(ts, "rm", h)["total_misses"]
    r_edf = simulate(ts, "edf", h)["total_misses"]
    mat.append([r_rm, r_edf])
import numpy as np

m = np.array(mat, dtype=float)
for lang in ("fa", "en"):
    fig, ax = plt.subplots(figsize=(6.8, 4.2), dpi=170)
    im = ax.imshow(m.T, cmap="OrRd", aspect="auto")
    ax.set_xticks(range(len(sets)))
    ax.set_xticklabels([f"S{i+1}" for i in range(len(sets))], fontsize=8)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["RM", "EDF"], fontsize=8.6)
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            ax.text(i, j, f"{m[i, j]:.0f}", ha="center", va="center", fontsize=7.4, color="#1b2430")
    ax.set_title(tr("از دست رفتن مهلت در هشت مجموعه با بهره‌وری ۰٫۹",
                    "Deadline misses across eight task sets at utilisation 0.9", lang),
                 fontsize=10.4, color=theme.ACCENT_DARK, fontweight="bold")
    fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    fig.savefig(os.path.join(OUT, f"fig12_miss_heat_{lang}.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

print("figures:", len([f for f in os.listdir(OUT) if f.endswith(".png")]))
