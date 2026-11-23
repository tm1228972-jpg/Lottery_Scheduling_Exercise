#!/usr/bin/env python3
"""Report pages whose content stops well short of the bottom (visible blank bands).

Usage:  python3 tools/gapscan.py <a.pdf> [<b.pdf> ...] [--max-gap 0.15]
Exit code 1 when any page exceeds the threshold (so it can gate a build).
"""
import sys

import numpy as np
import pypdfium2 as pdfium


def scan(path, max_gap=0.15, quiet=False):
    doc = pdfium.PdfDocument(path)
    bad = []
    for i in range(len(doc)):
        arr = np.array(doc[i].render(scale=0.8).to_pil().convert("L"))
        h = arr.shape[0]
        body = arr[int(h * 0.09):int(h * 0.93)]
        rows = (body < 240).sum(axis=1)
        nz = np.nonzero(rows > 3)[0]
        if len(nz) == 0:
            bad.append((i + 1, 1.0))
            continue
        gap = (body.shape[0] - nz[-1]) / body.shape[0]
        if gap > max_gap:
            bad.append((i + 1, round(float(gap), 3)))
    if not quiet:
        print(f"{path}: {len(doc)} pages, {len(bad)} page(s) with gap > {max_gap}")
        for p, g in bad:
            print(f"   page {p:3d}  gap {g:.0%}")
    return bad, len(doc)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    thr = 0.15
    for a in sys.argv[1:]:
        if a.startswith("--max-gap"):
            thr = float(a.split("=", 1)[1]) if "=" in a else thr
    rc = 0
    for p in args:
        bad, _ = scan(p, thr)
        rc = rc or (1 if bad else 0)
    raise SystemExit(rc)
