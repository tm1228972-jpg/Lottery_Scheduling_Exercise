# Technical Note — Exercise 1: Lottery Scheduling

**Document type:** evidence-based starter note, not the requested 40-page final report
**Model:** Python teaching implementation; experiment seed `20261123`

## Abstract

Lottery scheduling is a proportional-share selection mechanism. Each ready process receives a positive integer number of tickets. A uniformly selected ticket identifies the process for one modeled dispatch. A process holding `tᵢ` of a total `T` tickets therefore has probability `tᵢ/T` of winning one independent draw. This note documents the runnable model, its input validation, and a seeded 50,000-draw sample compared with the theoretical ratios.

## Problem, model, and assumptions

The modeled problem is to choose one winner from a set of ready processes. The process set remains fixed for a `run()` trace. Draws use a seeded pseudo-random generator. The program does not simulate real CPU time, interrupts, context switches, blocking, arrivals, or dynamic ticket changes. “Scheduling” here means an abstract dispatch choice, not a kernel scheduler.

## Rule and analysis

Each process `i` has `tᵢ > 0` tickets, and `T = Σ tᵢ`. The implementation draws an integer `k` from the closed range `1..T`, then maps it to the owner's cumulative ticket interval. Hence `P(i)=tᵢ/T`. This is a per-draw probability, not a promise that a finite prefix will have the exact ratio.

For `P1=1`, `P2=2`, and `P3=4`, the ticket intervals are `[1]`, `[2,3]`, and `[4,7]`. Every ticket belongs to exactly one process, so each valid `k` has one owner.

## Implementation and input handling

`Process` stores a name and ticket count. Empty names, non-integer/non-positive counts, and duplicate process names are rejected. `LotteryScheduler.draw()` uses `random.Random(seed)` and returns the winning ticket, total, and owner. `run(n)` returns the complete trace and rejects negative or non-integer `n`. `expected_share()` reports the theoretical ticket ratio.

## Reproducible sample and observed output

The figure generator uses 50,000 draws and seed `20261123`. The exact data is stored in `outputs/lottery-frequency.csv`:

| Process | Tickets | Expected | Observed draws | Observed share |
|---|---:|---:|---:|---:|
| P1 | 1 | 14.285714% | 7,243 | 14.486% |
| P2 | 2 | 28.571429% | 14,420 | 28.840% |
| P3 | 4 | 57.142857% | 28,337 | 56.674% |

The counts sum to 50,000 and the observed shares sum to 100%. A finite sample can differ from the expectation. One seed cannot establish a general deviation bound, performance result, or fairness guarantee.

## Figures and interpretation

1. `figures/lottery-pipeline.svg` shows the conceptual path from ready set through ticket pool and draw to dispatch; process-state transitions are intentionally outside scope.
2. `figures/lottery-control-flow.svg` shows total calculation, ticket draw, and cumulative-interval mapping.
3. `figures/lottery-frequency.png` compares observed bars with theoretical markers. It is a data visualization, not a speed benchmark.

## Advantages, limitations, and use

Ticket counts provide a simple, understandable way to alter relative selection probabilities. However, an individual draw may select a low-ticket process, and a short sequence can differ noticeably from the expected ratio. Lottery selection alone does not provide a deterministic deadline or finite waiting bound. This package is intended for teaching and analysis, not as a production kernel scheduler.

## Reproduction

```bash
python -m pip install -e .
python examples/run_lottery_demo.py
python -m unittest discover -s tests -v
python -m pip install -e ".[docs]"
python tools/generate_figures.py
```

The generator records its seed and draw count in the CSV. Tests are in `tests/test_lottery.py`.

## Report limitation and reference

The seed repository contained no source code, report, or course references. This note restricts itself to claims supported by the new model. A 40-page Word/PDF report has not been generated; padding or inventing results would not be appropriate. Suggested foundational reading to verify against the instructor's citation style: Carl A. Waldspurger and William E. Weihl, “Lottery Scheduling: Flexible Proportional-Share Resource Management,” OSDI 1994.
