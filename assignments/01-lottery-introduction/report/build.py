#!/usr/bin/env python3
"""Build every deliverable for one assignment.

    python3 report/build.py            # PDF (fa/en) + DOCX (fa/en) + slides + validation

Outputs (inside the assignment folder)::

    report/out/<key>_report_fa.pdf
    report/out/<key>_report_en.pdf
    report/out/<key>_report_fa.docx
    report/out/<key>_report_en.docx
    report/out/slides_fa/slide_001.png ...
    report/out/validation.json
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSIGN = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(ASSIGN, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))


def load_content():
    spec = importlib.util.spec_from_file_location("content", os.path.join(HERE, "content.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.build()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-slides", action="store_true")
    ap.add_argument("--only", choices=["pdf", "docx", "slides", "all"], default="all")
    args = ap.parse_args()

    from reportkit import docx as rdocx
    from reportkit import pdf as rpdf
    from reportkit import validate
    from reportkit.fonts import register_matplotlib_fonts

    model = load_content()
    out = os.path.join(HERE, "out")
    os.makedirs(out, exist_ok=True)
    os.chdir(HERE)  # relative figure paths in the content resolve against report/

    fa_pdf = os.path.join(out, f"{model.key}_report_fa.pdf")
    en_pdf = os.path.join(out, f"{model.key}_report_en.pdf")
    fa_doc = os.path.join(out, f"{model.key}_report_fa.docx")
    en_doc = os.path.join(out, f"{model.key}_report_en.docx")

    if args.only in ("pdf", "all"):
        print("[1/4] Persian PDF ...")
        rpdf.build(model, fa_pdf, "fa")
        print("[2/4] English PDF ...")
        rpdf.build(model, en_pdf, "en")

    if args.only in ("docx", "all"):
        print("[3/4] Word documents ...")
        rdocx.write(model, fa_doc, "fa")
        rdocx.write(model, en_doc, "en")

    slide_dir = os.path.join(out, "slides_fa")
    if args.only in ("slides", "all") and not args.skip_slides:
        print("[4/4] Persian slide deck ...")
        register_matplotlib_fonts()
        from reportkit.slides import Deck

        Deck(model, "fa", slide_dir).build()

    print("validating ...")
    result = validate.check_report(fa_pdf, en_pdf, fa_doc, en_doc, slide_dir,
                                   expected_slides=8,
                                   lang_tokens=(model.title_en.split()[0], "References"),
                                   required_words=("زمان‌بندی", "قرعه‌کشی", "بلیت"),
                                   gantt_tokens=("گانت",))
    result["assignment"] = model.key
    with open(os.path.join(out, "validation.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)
    for c in result["checks"]:
        mark = "PASS" if c["ok"] else "FAIL"
        print(f"  [{mark}] {c['name']:<18} {c['info']}  {'; '.join(c['problems'])}")
    failures = [c for c in result["checks"] if not c["ok"]]
    if failures:
        print(f"\n{len(failures)} check(s) failed - see report/out/validation.json")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
