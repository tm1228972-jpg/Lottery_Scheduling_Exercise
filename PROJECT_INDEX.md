# Project index and branch audit

Audit date: **2026-11-23**
Seed commit: `8a71ba01619b8eb5dbb6efaf55b2796ebef640bd`
Active work branch: `arena/4447560a-lottery-scheduling-exercise`

## Audit summary

The seed commit checked out on this branch contained only `README.md`. I then queried and fetched the named remote refs for reading. The six assignment branches listed in the seed README **do exist on GitHub**. Each of the six currently contains only three root-level Markdown files (`README.md`, `report.md`, `references.md`); there are no standalone source trees, test suites, `docs/`, figures, experiment output, Word files, or PDFs in those branch trees. Exercise 5 has a Python snippet embedded in `report.md`, not a separate executable source file.

The full content-level findings are in [`docs/remote-branch-audit.md`](docs/remote-branch-audit.md). The attached checklist transcription is in [`docs/assignment-screenshot-audit.md`](docs/assignment-screenshot-audit.md).

All changes made in this work remain on the active session branch. The existing assignment branches were read but **not modified**, and no merge was performed.

## Assignment map

| # | Topic from available material | GitHub branch / latest audited commit | Audit and current-branch work |
|---|---|---|---|
| 1 | Lottery Scheduling introduction | [`assignment-01-lottery-introduction`](https://github.com/tm1228972-jpg/Lottery_Scheduling_Exercise/tree/assignment-01-lottery-introduction) · `1b752aa` | Remote branch has a concise English Markdown summary and references. No executable source/tests/figures/Word/PDF. A new teaching implementation and dossier are under [`assignments/01-lottery-introduction/`](assignments/01-lottery-introduction/README.md) on the active branch. |
| 2 | Compare Lottery Scheduling with EDF and RM | [`assignment-02-edf-rm-comparison`](https://github.com/tm1228972-jpg/Lottery_Scheduling_Exercise/tree/assignment-02-edf-rm-comparison) · `cdcd2d2` | Remote branch gives high-level theory, but no worked Lottery-vs-EDF/RM task set, code, diagrams, tests, or bilingual long report. Not modified. |
| 3 | Schedule EDF/RM for three processes | [`assignment-03-edf-rm-three-processes`](https://github.com/tm1228972-jpg/Lottery_Scheduling_Exercise/tree/assignment-03-edf-rm-three-processes) · `702c94d` | Remote report supplies `C/T=(1/4, 1/5, 2/10)`, synchronous release and `D=T`, `U=0.65`, and hyperperiod 20, but says the full Gantt chart remains to be added. No schedule chart or code is in that branch. Not modified. |
| 4 | Readers/writers synchronization | [`assignment-04-readers-writers-synchronization`](https://github.com/tm1228972-jpg/Lottery_Scheduling_Exercise/tree/assignment-04-readers-writers-synchronization) · `635f59a` | Remote report gives a short conceptual comparison of Dekker, Peterson, semaphores, and monitors, but no implementation, tests, or figures. Not modified. |
| 5 | Lottery Scheduling implementation | [`assignment-05-lottery-implementation`](https://github.com/tm1228972-jpg/Lottery_Scheduling_Exercise/tree/assignment-05-lottery-implementation) · `1a66735` | Remote `report.md` contains an inline weighted-draw function and 60,000-draw example, but no saved output, standalone source, tests, or figures. New tested reference code is under `src/lottery_lab/` on the active branch; it is not represented as recovered student code. |
| 6 | Lottery Scheduling seminar | [`assignment-06-lottery-seminar`](https://github.com/tm1228972-jpg/Lottery_Scheduling_Exercise/tree/assignment-06-lottery-seminar) · `21243a7` | Remote branch has a short summary and discussion questions, but no actual slide deck/video/presentation materials. Not modified. |
| 7 | **Unspecified** | No title or branch identified | The request says there are seven earlier exercises, but the seed README and checklist image show six. There is no basis to infer the missing topic, so it remains open. |
| 8 | Apply lottery logic to deadlock/starvation in dining philosophers | No existing exercise branch identified | A reasoned analysis, executable discrete-round model, tests, diagrams, and actual trace are under [`assignments/08-lottery-dining-philosophers/`](assignments/08-lottery-dining-philosophers/README.md) on the [active branch](https://github.com/tm1228972-jpg/Lottery_Scheduling_Exercise/tree/arena/4447560a-lottery-scheduling-exercise). No separate branch was created. |

## Checklist-image observations

The attached table shows six numbered task titles and fields for items including diagrams/flowcharts, comparisons, code/clip, Persian and English files, page count, PDF, and Word. Its data cells are blank; it does not establish scores or actual completion. The acronym for the second algorithm in row 3 is low-resolution and recorded as uncertain in the image audit.

## Branch status

- Local `main` and the active work branch start at the seed commit.
- The six named assignment branches are present on `origin`; their audited commits and contents are listed above.
- They were fetched as remote-tracking refs only for inspection and were not checked out or changed.
- Exercise 7 is unspecified; Exercise 8 is new in the request.

The current branch is the only branch receiving edits in this work. See [`PROJECT_PROGRESS.md`](PROJECT_PROGRESS.md) for validation results, file changes, and remaining requirements.
