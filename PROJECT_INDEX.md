# Project index — six requested exercises

Audit date: **2026-11-23**

Seed/base commit: `8a71ba01619b8eb5dbb6efaf55b2796ebef640bd`

Current Arena branch: `arena/4447560a-lottery-scheduling-exercise`

This index describes the six tasks visible in the supplied checklist and clarified by the user. The repository is still a working draft; completion is not inferred from the presence of an artifact.

## Assignment map

| # | Requested task | Current-branch material | Status / key gap |
|---|---|---|---|
| 1 | Detailed introduction to Lottery Scheduling | [`assignments/01-lottery-introduction/`](assignments/01-lottery-introduction/README.md); fixed-ticket simulator; figures and seeded CSV; bilingual Markdown, DOCX, PDF | The 40-page final report is not done. Current exports are short drafts; no padding or invented results. |
| 2 | Compare Lottery with EDF and RM across properties, including starvation | [`assignments/02-edf-rm-comparison/`](assignments/02-edf-rm-comparison/README.md); bilingual comparison, figures, bibliography | Source-checked working drafts remain far below the approximately 40-page target. No numerical Lottery share is invented for the EDF/RM task set because ticket weights were not supplied. |
| 3 | Work out EDF/RM schedules by hand for three tasks | [`assignments/03-edf-rm-three-processes/`](assignments/03-edf-rm-three-processes/README.md); event-by-event hand derivation, deadline table, CSV, Gantt, simulator cross-check | Hand schedule is complete for the recovered task set; its bilingual 4–5-page report exports remain short and below the project-level page target. No real-hardware measurements are claimed. |
| 4 | Compare Dekker, Peterson, semaphores, and monitors for mutual exclusion/readers-writers | [`assignments/04-readers-writers-comparison/`](assignments/04-readers-writers-comparison/README.md); tested FIFO-by-phase monitor and diagrams | Bilingual technical drafts are substantially shorter than the requested approximately 40-page final. Tests are not a formal proof for all interleavings. |
| 5 | Explain Lottery Scheduling in a video longer than two minutes | [`assignments/05-lottery-scheduling-clip/`](assignments/05-lottery-scheduling-clip/README.md); 12 bilingual caption sections, 132-second H.264 MP4, narration scripts | Duration and frame count are verified. Supporting bilingual DOCX/PDF report exports are one-page drafts. The MP4 is silent; it has no voice-over/audio track. |
| 6 | Prepare an article and seminar under the supplied regulations | [`assignments/06-lottery-seminar/`](assignments/06-lottery-seminar/README.md); bilingual article drafts, agenda, speaker notes, 10-slide bilingual PPTX | Article DOCX/PDF exports are 3–4-page drafts, not long-form finals. Exact seminar duration, slide limit, citation style, and grading rules are not readable; no compliance with unseen rules is claimed. |

## Source and output records

- [`docs/assignment-screenshot-audit.md`](docs/assignment-screenshot-audit.md) records the six-row scope and image limitations.
- [`docs/research-source-audit.md`](docs/research-source-audit.md) lists the primary and authoritative pages checked online on 2026-11-23 and limits what is attributed to them.
- [`REPORT_EXPORT_MANIFEST.json`](REPORT_EXPORT_MANIFEST.json) records each provisional Word/PDF export and its PDF page count. Every current report/article export is checked against the approximately 40-page target; none passes.
- [`PROJECT_PROGRESS.md`](PROJECT_PROGRESS.md) is the detailed change, validation, and outstanding-work ledger.

## Historical remote assignment branches

The remote branches were audited at the heads below before the current continuation. The subsequent local assignment work has **not** been committed or pushed to those branch names.

| Historic remote branch | Last verified head | Current task relevance |
|---|---|---|
| `assignment-01-lottery-introduction` | `1b752aa` | Exercise 1 |
| `assignment-02-edf-rm-comparison` | `cdcd2d2` | Exercise 2 |
| `assignment-03-edf-rm-three-processes` | `702c94d` | Exercise 3 input provenance |
| `assignment-04-readers-writers-synchronization` | `635f59a` | Exercise 4 |
| `assignment-05-lottery-implementation` | `1a66735` | Historical branch contains an implementation report; current checklist Exercise 5 is the video |
| `assignment-06-lottery-seminar` | `21243a7` | Exercise 6 |

Full historic findings are in [`docs/remote-branch-audit.md`](docs/remote-branch-audit.md). The assignment branches and `main` remain unchanged in this work; all current changes are on the active Arena branch. No branch switch, merge, commit, or push has yet been performed for the current edits.

## Supplemental legacy material

`assignments/08-lottery-dining-philosophers/` and its source/test material are retained from earlier work, but the user clarified the requested scope is six exercises. The directory is not a seventh requested task and is excluded from this index's six deliverables and the report-export manifest.
