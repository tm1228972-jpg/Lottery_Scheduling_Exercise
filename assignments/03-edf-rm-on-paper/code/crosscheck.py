#!/usr/bin/env python3
"""Independent cross-check: does the hand drawing agree with a separate simulator?

The verifier in workbook.py checks *properties* (no collisions, deadlines met, theory
agrees).  This script checks something stronger and narrower: it replays the same task
set through the Assignment-2 simulator, which shares no code with workbook.py, and
compares the resulting tick-by-tick timeline with the tick-by-tick hand drawing.

    python3 code/crosscheck.py

Exit code 0 means both drawings match tick for tick.  A mismatch is reported as a
diff per row, never silently tolerated.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(ROOT, "..", "02-edf-vs-rm", "code"))
sys.path.insert(0, HERE)

import rt_sim  # noqa: E402  (Assignment 2 simulator, independent of workbook.py)
from workbook import hyperperiod, load  # noqa: E402

RUN = "#"


def rows_of(tasks, timeline):
    """Turn a simulator timeline into the sheet's row format (one char per tick)."""
    out = {t.name: [] for t in tasks}
    for name in timeline:
        for t in tasks:
            out[t.name].append(RUN if name == t.name else ".")
    return {k: "".join(v) for k, v in out.items()}


def main() -> int:
    wb = load(os.path.join(ROOT, "data", "paper_work.txt"))
    H = hyperperiod(wb.tasks)
    tasks = [rt_sim.Task(t.name, t.period, t.wcet, t.deadline) for t in wb.tasks]

    report = {}
    ok = True
    print(f"task set: {', '.join(f'{t.name}(T={t.period},C={t.wcet})' for t in wb.tasks)}")
    print(f"hyperperiod: {H}\n")
    for alg in ("rm", "edf"):
        res = rt_sim.simulate(tasks, alg, H, trace=True)
        sim = rows_of(wb.tasks, res["timeline"])
        hand = next(s.rows for s in wb.schedules if s.algorithm == alg)
        same = all(sim[n] == hand[n] for n in sim)
        idle = sum(1 for x in res["timeline"] if x == "idle")
        report[alg] = {
            "rows": sim,
            "hand": hand,
            "identical": same,
            "total_misses": res["total_misses"],
            "idle_ticks": idle,
        }
        print(f"{alg.upper():>4}  identical to the hand drawing: {same}"
              f"   (misses: {res['total_misses']}, idle ticks: {idle})")
        if not same:
            ok = False
            for n in sim:
                if sim[n] != hand[n]:
                    print(f"       {n} sim   {sim[n]}")
                    print(f"       {n} hand  {hand[n]}")
    print()
    print("PASS: the drawings are the schedules a separate simulator produces."
          if ok else "FAIL: the hand drawing and the simulator disagree.")
    with open(os.path.join(ROOT, "data", "crosscheck.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
