"""Shared experiment/evaluation figures every assignment report reuses."""
from __future__ import annotations

import os
import random

from . import diagrams as D
from . import theme


def base_figures(out_dir, cfg):
    """Generate the nine figures common to all assignments.

    cfg keys: title, gantt_tasks, gantt_title, gantt_xlabel, gantt_colors,
              flow_steps, flow_title, flow_decision, flow_branches,
              arch_blocks, arch_title, arch_arrows,
              bar_values, bar_labels, bar_title, bar_ylabel, bar_xlabel,
              line_series, line_x, line_title, line_ylabel, line_xlabel,
              seat_labels, content_titles,
              eval_title, eval_rows (metric, [values...]), eval_algorithms,
              state_blocks, state_title, state_arrows
    """
    os.makedirs(out_dir, exist_ok=True)
    made = []

    def p(name):
        return os.path.join(out_dir, name)

    D.gantt(cfg["gantt_tasks"], p("fig01_gantt.png"), "fa", cfg["gantt_title"],
            cfg.get("gantt_xlabel", "زمان (روز)"), figsize=(10, 4.7))
    made.append("fig01_gantt.png")

    D.flowchart(cfg["flow_steps"], p("fig02_flowchart.png"), "fa", cfg["flow_title"],
                decision_at=cfg.get("flow_decision"), branch_labels=cfg.get("flow_branches"),
                figsize=(9.6, 7.2))
    made.append("fig02_flowchart.png")

    D.block_diagram(cfg["arch_blocks"], p("fig03_architecture.png"), "fa", cfg["arch_title"],
                    arrows=cfg.get("arch_arrows"), figsize=(10, 3.8))
    made.append("fig03_architecture.png")

    D.bar(cfg["bar_values"], cfg["bar_labels"], p("fig04_bars.png"), "fa", cfg["bar_title"],
          cfg.get("bar_ylabel", ""), cfg.get("bar_xlabel", ""), figsize=(8.8, 3.9))
    made.append("fig04_bars.png")

    D.lines(cfg["line_series"], cfg["line_x"], p("fig05_lines.png"), "fa", cfg["line_title"],
            cfg.get("line_ylabel", ""), cfg.get("line_xlabel", ""), figsize=(8.8, 3.9))
    made.append("fig05_lines.png")

    D.timeline(cfg["timeline_rows"], p("fig06_timeline.png"), "fa", cfg["timeline_title"],
               horizon=cfg.get("timeline_horizon", 24), unit=cfg.get("timeline_unit", "کوانتوم"),
               figsize=(10, 2.9))
    made.append("fig06_timeline.png")

    D.pie(cfg["pie_values"], cfg["pie_labels"], p("fig07_pie.png"), "fa", cfg["pie_title"], donut=True)
    made.append("fig07_pie.png")

    D.heatmap(cfg["heat"],
              cfg["heat_rows"], cfg["heat_cols"], p("fig08_heatmap.png"), "fa", cfg["heat_title"])
    made.append("fig08_heatmap.png")

    D.histogram(cfg["hist_a"], cfg["hist_b"], cfg["hist_labels"], p("fig09_histogram.png"), "fa",
                cfg["hist_title"], cfg.get("hist_xlabel", ""), bins=24)
    made.append("fig09_histogram.png")

    D.block_diagram(cfg["state_blocks"], p("fig10_state_machine.png"), "fa", cfg["state_title"],
                    arrows=cfg.get("state_arrows"), figsize=(9.2, 4.3))
    made.append("fig10_state_machine.png")

    return made
