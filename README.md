# Lottery Scheduling Exercise — six-assignment working repository

> **Status (2026-11-23):** The current Arena branch contains working drafts and supporting artifacts for the six assignments transcribed from the supplied checklist. It is not a finished submission. The requested long-form bilingual reports are **not complete**: the current Word/PDF exports are short technical drafts, not approximately 40-page deliverables. The video is 2:12 and silent with Persian/English captions. Seminar-rule compliance cannot be confirmed without the readable rule sheet.

## Six requested assignments

1. **Lottery Scheduling introduction:** teaching simulator, bilingual technical drafts, flow diagrams, seeded frequency data, and report exports under [`assignments/01-lottery-introduction/`](assignments/01-lottery-introduction/README.md).
2. **Lottery vs. EDF/RM comparison:** bilingual comparison drafts, diagrams, and references under [`assignments/02-edf-rm-comparison/`](assignments/02-edf-rm-comparison/README.md).
3. **Three-task EDF/RM schedule by hand:** explicit event-by-event derivation, deadline audit, Gantt chart, CSV, simulator cross-check, and bibliography under [`assignments/03-edf-rm-three-processes/`](assignments/03-edf-rm-three-processes/README.md).
4. **Dekker, Peterson, semaphore, and monitor comparison:** bilingual technical drafts, a tested readers-writers monitor, diagrams, and source audit under [`assignments/04-readers-writers-comparison/`](assignments/04-readers-writers-comparison/README.md).
5. **Lottery Scheduling clip:** [`132-second bilingual captioned MP4`](assignments/05-lottery-scheduling-clip/outputs/lottery-scheduling-comparison.mp4), separate narration scripts, sources, and technical notes under [`assignments/05-lottery-scheduling-clip/`](assignments/05-lottery-scheduling-clip/README.md). The MP4 has no audio track.
6. **Article and seminar:** bilingual article drafts, agenda/speaker notes, a 10-slide editable PPTX, and provisional Word/PDF exports under [`assignments/06-lottery-seminar/`](assignments/06-lottery-seminar/README.md). The detailed seminar rules are not available in a readable form; no compliance with unseen rules is claimed.

## Quick start

Requires Python 3.11 or later.

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python examples/run_lottery_demo.py
python examples/run_philosophers_demo.py  # supplemental, outside the six-task checklist
```

Regenerate CSVs and figures:

```bash
python -m pip install -e ".[docs]"
python tools/generate_figures.py
```

Build the silent Exercise 5 clip and 10-slide seminar deck:

```bash
python -m pip install -e ".[media,seminar]"
python tools/build_exercise5_video.py
python tools/build_seminar_deck.py
```

Export the current Markdown working drafts to DOCX/PDF:

```bash
python -m pip install -e ".[reports]"
python tools/build_reports.py
```

`REPORT_EXPORT_MANIFEST.json` records the page counts. Every current report/article export is explicitly compared with the approximately 40-page target; all are short drafts, none meets the target, and none is described as a final submission.

## Research and project records

- [`PROJECT_INDEX.md`](PROJECT_INDEX.md): six-exercise map and current branch status.
- [`PROJECT_PROGRESS.md`](PROJECT_PROGRESS.md): implemented work, validation, remaining requirements, and push record.
- [`docs/assignment-screenshot-audit.md`](docs/assignment-screenshot-audit.md): cautious transcription of the checklist and scope clarifications.
- [`docs/remote-branch-audit.md`](docs/remote-branch-audit.md): historical audit of the six remote assignment branches; these branches have not been updated in this work.
- [`docs/research-source-audit.md`](docs/research-source-audit.md): primary/authoritative pages fetched, metadata checked, supported claims, and limits.

## Scope and integrity notes

All current edits are on `arena/4447560a-lottery-scheduling-exercise`; the six existing `assignment-*` remote branches and `main` have not been edited in this continuation. No commit or push has been made for these uncommitted changes. The separate-branch arrangement requested earlier is therefore not complete in this session.

The simulator and concurrency monitor are educational models. The Lottery seed output and EDF/RM trace are generated locally and are not presented as published results or production benchmarks. The actual assignment asks for six exercises; a prior supplemental dining-philosophers directory remains in the repository for continuity but is not included as a seventh requested assignment or in the six-exercise export manifest.

The checked sources are cited in the assignment reference files. No claim that Claude AI authored or reviewed a report is made.
