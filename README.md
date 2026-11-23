# Lottery Scheduling Exercise — repository status and reference work

> **Status (2026-11-23):** the supplied base commit in this worktree contained only this README. A subsequent remote-branch audit found the six assignment branches listed below; each has three root-level Markdown files, but no standalone implementation tree, tests, `docs/`, figures, output data, Word files, or PDFs. Exercise 5 contains an inline Python snippet in its report. This branch adds a reproducible teaching model for the Lottery Scheduling introduction and the newly requested dining-philosophers analysis; it does **not** claim that the other assignments or the requested 40-page bilingual reports are complete.

## What is in this branch

- **Exercise 1 — Lottery Scheduling:** an explicit weighted-draw simulator, tests, a runnable example, algorithm diagrams, and a frequency chart generated from 50,000 actual seeded draws.
- **Exercise 8 — Dining Philosophers:** a safe atomic-admission model, lottery selection among non-conflicting philosophers, an optional age-based fairness override, tests, a round trace, and a Gantt-style chart generated from the simulator.
- **Repository audit and task map:** [`PROJECT_INDEX.md`](PROJECT_INDEX.md) and [`PROJECT_PROGRESS.md`](PROJECT_PROGRESS.md) record which materials were and were not present.

The algorithm code is a **teaching model**, not an operating-system scheduler or a production concurrent program. The reports distinguish mathematical properties from finite seeded demonstrations; sample results are never presented as guarantees.

## Quick start

Requires Python 3.11 or later. The scheduler and tests use only the Python standard library.

```bash
python -m pip install -e .
python examples/run_lottery_demo.py
python examples/run_philosophers_demo.py
python -m unittest discover -s tests -v
```

To regenerate the data-driven PNG charts, install the optional Pillow dependency and run the figure generator:

```bash
python -m pip install -e ".[docs]"
python tools/generate_figures.py
```

The generator uses fixed seeds and writes CSV traces beside the figures. The structural diagrams are SVG; the observed-frequency and simulated-meal charts are PNG. All chart data can be inspected in the corresponding `outputs/` directory.

## Start here

- [Exercise 1: Lottery Scheduling](assignments/01-lottery-introduction/README.md)
- [Exercise 8: Lottery scheduling and dining philosophers](assignments/08-lottery-dining-philosophers/README.md)
- [Project index and branch audit](PROJECT_INDEX.md)
- [Audit of the supplied assignment checklist image](docs/assignment-screenshot-audit.md)
- [Progress, validation, and outstanding requirements](PROJECT_PROGRESS.md)

## Scope and honesty note

The seed README names six assignment branches, and all six are present on the GitHub remote. Their contents were read and audited, but left unchanged; the audit is in [`docs/remote-branch-audit.md`](docs/remote-branch-audit.md). The request refers to seven earlier exercises, while the image and seed README identify six; no title or source for Exercise 7 is available. This work remains on the active branch, and no other branch was edited. See the index for exact branch names and gaps.

There were no existing reports to improve. The included Markdown technical notes are evidence-based starter reports for the two implemented topics; they do **not** meet the requested 35–40/40+ page Word/PDF target. Producing pages by padding or inventing experimental claims would contradict the request to use only real content. The remaining source materials, the unnamed Exercise 7, and instructor-approved report content are needed before that deliverable can be completed responsibly.
