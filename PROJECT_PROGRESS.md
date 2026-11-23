# Project progress and quality record

Updated: **2026-11-23**

Working branch: `arena/4447560a-lottery-scheduling-exercise`

Base commit: `8a71ba01619b8eb5dbb6efaf55b2796ebef640bd`

## Requested scope

The user clarified that the supplied checklist comprises **six exercises**; no seventh exercise is requested. The tasks are: Lottery Scheduling introduction; comparison with EDF/RM; a three-task hand schedule; synchronization comparison including Dekker and Peterson; a Lottery Scheduling video over two minutes; and an article/seminar. The report deliverables have an approximately 40-page target. Do not satisfy that count with repeated prose or unsupported claims. The available checklist image does not provide a readable detailed seminar regulation sheet, so no compliance with unseen duration, slide-count, citation, or grading rules is claimed.

## Deliverable status

1. **Exercise 1 — Lottery Scheduling introduction**
   - Educational fixed-ticket simulator, tests, example, flow diagrams, seeded frequency chart/CSV, references, and bilingual report Markdown are present.
   - Reports cover ticket-to-probability mapping, expected share and variance, first-win waiting, ticket-management abstractions, code boundaries, and a reproducible sample.
   - Current DOCX/PDF exports are 4 pages each, far below target.
2. **Exercise 2 — Lottery vs. EDF/RM**
   - Bilingual reports and conceptual figures compare objectives, workload assumptions, utilization, response-time concerns, overload, fairness, and starvation.
   - EDF's `U≤1` result is qualified by its ideal implicit-deadline uniprocessor assumptions; the RM utilization formula is labeled sufficient, not necessary.
   - No Lottery ticket weights are invented for the Exercise 3 task set. Current exports are 4 pages each.
3. **Exercise 3 — three-process hand schedule**
   - Recovered tasks: `(C,T,D)=(1,4,4),(1,5,5),(2,10,10)`; `U=0.65`, `H=20`, RM sufficient bound `0.7797631496846196`.
   - Bilingual reports include a manual event schedule, job deadline audit, hand-check table, CSV, Gantt figure, and simulator cross-check. EDF/RM have no misses on this input only; no hardware result is claimed.
   - Current exports: Persian 4 pages, English 5 pages.
4. **Exercise 4 — synchronization comparison**
   - Bilingual reports cover Dekker, Peterson, semaphores, monitor semantics, readers-writers policies, safety/progress/fairness, busy waiting, and memory-model boundaries.
   - `FairReadersWritersMonitor` uses FIFO-by-phase admission and has four focused tests. Those tests are not a formal proof over all interleavings or a real-time guarantee.
   - Current exports are 5 pages each.
5. **Exercise 5 — video**
   - `assignments/05-lottery-scheduling-clip/outputs/lottery-scheduling-comparison.mp4` is a 132-second bilingual-captioned H.264 video with 12 sections, 1,320 frames at 10 fps, 1280×720, and no audio stream. Separate English/Persian narration scripts are present, but the MP4 is silent.
   - Supporting bilingual report exports are one page each.
6. **Exercise 6 — article/seminar**
   - Bilingual source-cited article drafts, a proposed agenda, speaker notes, and an editable 10-slide bilingual PPTX are present. The agenda is explicitly provisional because exact seminar rules are unavailable.
   - Article exports are 3 pages (Persian) and 4 pages (English). The deck passes structural checks, but no presentation renderer was available for visual review.
7. **Source audit and report exporter**
   - `docs/research-source-audit.md` records checked sources, metadata, supported claims, and source-access limits.
   - `tools/build_reports.py` exports the six report/article pairs as DOCX/PDF and writes `REPORT_EXPORT_MANIFEST.json`. All 12 exports are marked as short drafts, below the approximately 40-page target, and not submission-ready. The supplemental Exercise 8 is excluded from this six-exercise export manifest; its source material remains.

## Validation performed in this continuation

- `.venv/bin/python -m unittest discover -s tests -v`: **21 tests passed** across Lottery Scheduling, dining philosophers (supplemental), readers-writers, and real-time scheduling.
- `.venv/bin/python tools/generate_figures.py`: regenerated the repository diagrams/data-backed figure sets and CSVs.
- `.venv/bin/python tools/build_reports.py`: generated the 12 bilingual DOCX/PDF exports above. Automated QA opened every DOCX/PDF, checked page counts against the manifest, confirmed nonblank PDF pages, and confirmed none meets the 40-page target.
- Selected PDF pages were rendered and visually spot-checked for Persian RTL, table layout, Gantt placement, reference formatting, and clipping. The reviewed samples appeared legible; this is a spot-check, not a page-by-page audit of every PDF or a Word-rendering check.
- `.venv/bin/python tools/build_exercise5_video.py`: rebuilt the MP4; bundled FFmpeg decoded it successfully. `imageio_ffmpeg.count_frames_and_secs` confirmed 1,320 frames and 132.0 seconds; stream metadata confirmed H.264 High, 1280×720, 10 fps, video only.
- `.venv/bin/python tools/build_seminar_deck.py`: generated the 10-slide PPTX. `python-pptx` inspection confirmed 10 nonempty slides, bilingual text, citation footers, two chart images, and shape bounds within slide dimensions. No LibreOffice/PowerPoint renderer was available for visual review.
- Relative-Markdown-link checker: **85 local links checked across 38 Markdown files; all resolved**.
- `clean_inline` smoke checks preserve code identifiers such as `read_count` and `X_i`, render Markdown emphasis, and show readable link labels rather than raw local paths.
- `py_compile` passed for the report, video, deck, and figure-builder scripts. A first `git diff --check` found trailing spaces used for Markdown line breaks in the index/progress files; those were removed, and the final `git diff --check` passed.
- An initial system-Python unittest invocation failed to import the uninstalled package; it is superseded by the successful full `.venv` run above.

## Research and integrity notes

The listed source pages were fetched on **2026-11-23**. See [`docs/research-source-audit.md`](docs/research-source-audit.md) for bibliography metadata, specific claims reviewed, and limits. This source audit is not a peer review of every sentence. The seeded Lottery counts and Exercise 3 schedules are local program/reproducibility outputs, not published findings or hardware benchmarks. No Claude authorship/use is claimed.

## Git and branch record

- Last previously verified pushed head on this Arena branch: `21fc0fd` (after the earlier `e05c741` work).
- All changes since those pushes remain uncommitted on the active branch.
- The six pre-existing `assignment-*` remote branches and `main` were audited historically but were not updated in this continuation. No branch switch, merge, commit, or push has occurred for the current edits.
- The requested separate-branch arrangement is therefore not complete; this session remains on the fixed Arena branch `arena/4447560a-lottery-scheduling-exercise`.

## Remaining work / honest limitations

- Create substantive, source-cited long-form bilingual reports and meet the approximately 40-page target without filler. Current reports/articles are short working drafts, not final submissions.
- Confirm the instructor's readable row-specific page requirements and seminar regulations; do not claim compliance with the unreadable rules.
- Review the remaining PDF pages and Word pagination/RTL in a suitable renderer. Visually review the 10-slide PPTX in PowerPoint/LibreOffice when available.
- Keep the Exercise 5 video silent unless narration is separately recorded and muxed; the existing narration files are scripts only.
- Re-run final `git diff --check` and `git status --short --branch` after any further edits. Commit/push only to this active Arena branch if/when requested and ready; do not modify the historical assignment branches or `main`.
