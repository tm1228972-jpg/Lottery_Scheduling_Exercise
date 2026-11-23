"""reportkit — bilingual (Persian RTL / English LTR) report engine.

Used by every assignment branch to build:
  * a >=40-page PDF report (Persian) with tables, figures, gantt chart,
  * a >=40-page PDF report (English),
  * matching Word (.docx) reports,
  * a narrated 16:9 slide deck (mp4) generated from the report content.

The engine enforces the rubric checks: page-count >= 40, no mirrored/mojibake
Persian text, no blank gaps between slides, table of contents, figures,
flowcharts, Gantt chart and real code listings.
"""
