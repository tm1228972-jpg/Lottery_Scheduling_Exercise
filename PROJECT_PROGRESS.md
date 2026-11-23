# Project progress and quality record

Updated: **2026-11-23**
Working branch: `arena/4447560a-lottery-scheduling-exercise`
Seed: `8a71ba01619b8eb5dbb6efaf55b2796ebef640bd`

## Repository and remote-branch audit

- The seed commit in the active worktree tracked only `README.md`.
- A later `git ls-remote --heads origin` query found all six assignment branches listed in that README. They were fetched as remote-tracking refs for reading; no assignment branch was checked out or edited.
- Each of the six remote assignment branches currently has three root-level Markdown files: `README.md`, `report.md`, and `references.md`. No standalone `src/`, tests, `docs/`, figures, saved experiment outputs, DOCX, or PDF were found. Exercise 5 has an inline Python sample in `report.md`; Exercise 3 has an input task set and a note that the full Gantt chart still needs to be added.
- The remote branch-level findings, content summaries, and limitations are in [`docs/remote-branch-audit.md`](docs/remote-branch-audit.md). The named branches are linked from [`PROJECT_INDEX.md`](PROJECT_INDEX.md).
- The request and screenshot show six identifiable earlier assignments, while the message says seven. The seventh is unnamed and has no branch. Exercise 8 is explicitly specified by the user.

## Work added on the active branch

1. **Exercise 1 — Lottery Scheduling teaching model**
   - `src/lottery_lab/lottery.py`: positive integer ticket validation, cumulative ticket mapping, seeded draws, trace values, and theoretical share calculation.
   - `assignments/01-lottery-introduction/`: Persian-first README, detailed technical guide, Persian/English Markdown notes, two structural SVGs, a frequency PNG/SVG generated from 50,000 actual seeded draws, and the source CSV.
2. **Exercise 8 — dining-philosophers analysis/model**
   - `src/lottery_lab/philosophers.py`: atomic two-fork admission in a discrete model, weighted lottery among safe candidates, optional age-threshold override, wait ages, meal counts, and round trace.
   - `assignments/08-lottery-dining-philosophers/`: analysis answering that lottery alone guarantees neither deadlock prevention nor a finite starvation bound; pseudocode, comparison table, Persian/English Markdown notes, two structural SVGs, a Gantt PNG/SVG generated from the simulator, and the source CSV.
3. **Project audit and reproducibility**
   - `PROJECT_INDEX.md`, `PROJECT_PROGRESS.md`, screenshot transcription, and audit of all six remote branch trees.
   - `pyproject.toml` defines a dependency-free package; optional Pillow supports PNG regeneration. `tools/generate_figures.py` uses fixed seeds and writes CSVs alongside figures.
   - `tests/` contains 13 standard-library unit tests for validation, reproducibility, ticket mapping, safety, and model fairness behavior.

## Validation performed

- `.venv/bin/pip install -e '.[docs]'` — **passed**.
- `.venv/bin/python -m unittest discover -s tests -v` — **13 tests passed**.
- Both example programs ran successfully: 20 lottery draws and a 12-round dining-philosophers trace.
- Fairness-age smoke check passed for **1,000 seeded configurations** (`N=3..10`, thresholds `1..5`). This checks the stated discrete simulator model; it is not a real-time concurrency proof.
- `.venv/bin/python tools/generate_figures.py` — generated four structural SVGs, two data-chart SVGs, two PNG charts, and two source CSVs.
- XML parsing passed for all six SVG files; Pillow verified both PNG files; all relative Markdown links and assignment README image paths resolve.
- `git diff --check` passed before commit.

## Not completed / remaining

- **Exercises 2–6 remain unchanged on their remote branches.** The existing reports are short Markdown summaries; there are no implementations/tests/assets or DOCX/PDF files there. The available Exercise 3 task set is recorded in the audit, but its report still lacks the promised complete schedule/Gantt chart.
- No earlier **Exercise 7** could be identified from the README, screenshot, or remote branches; its title/specification is required rather than guessed.
- The work has not been split into commits on Exercises 1–6 or a separate Exercise 8 branch; changes are confined to the active Arena branch. No remote assignment branch was modified or merged.
- No DOCX/PDF existed to improve. The newly added bilingual Markdown notes are concise technical notes, not the requested 35–40/40+ page Word/PDF reports. Producing that length without approved content, sources, and verified experiments would require padding or unsupported claims, so those files were not fabricated.
- The Lottery and philosophers code is an educational discrete model, not a kernel scheduler or real multithreaded implementation. Charts are explicitly labeled with model scope and seeds.

## Inputs/actions needed for full completion

1. Identify the missing Exercise 7 and confirm the low-resolution EDF/RM acronym in the screenshot.
2. Decide how the existing remote assignment branches should be handled in a later branch-authorized session; this session changed only the active work branch.
3. Provide instructor-approved requirements and references for each report. For Exercise 3, retain the remote task set `(C,T=D)=(1,4),(1,5),(2,10)` and complete/verify the full schedules if that is the intended input.
4. Add real code, tests, figures, and checked results to the remaining exercises without representing assumptions as experimental facts.
5. Generate, format, and validate Persian and English DOCX/PDF reports against the requested page counts only after adequate substantive content is approved.

The current changes, test run, CSVs, and figure generator describe exactly what is implemented; no other exercise is marked complete by inference.
