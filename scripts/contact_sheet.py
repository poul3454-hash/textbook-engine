#!/usr/bin/env python3
"""textbook-engine / scripts/contact_sheet.py — 콘택트시트 (레이아웃 검수용)

사용: python3 scripts/contact_sheet.py build/main.pdf [--first N] [--pages 10-20] [--dpi 45] [--cols 5]
  출력: build/sheet_*.png (20쪽씩 한 장). 바뀐 쪽만 보려면 --pages 로 범위 지정, --dpi 90 으로 올린다.
"""
import argparse, subprocess, glob, os, tempfile
from PIL import Image

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("pdf"); ap.add_argument("--first", type=int, default=1)
    ap.add_argument("--pages"); ap.add_argument("--dpi", type=int, default=45); ap.add_argument("--cols", type=int, default=5)
    a = ap.parse_args()
    out = os.path.join(os.path.dirname(a.pdf) or ".", "sheet")
    tmp = tempfile.mkdtemp()
    cmd = ["pdftoppm", "-r", str(a.dpi), "-png"]
    if a.pages:
        lo, hi = a.pages.split("-"); cmd += ["-f", str(int(lo) - a.first + 1), "-l", str(int(hi) - a.first + 1)]
    subprocess.run(cmd + [a.pdf, os.path.join(tmp, "p")], check=True)
    files = sorted(glob.glob(os.path.join(tmp, "p-*.png")))
    per = a.cols * 4
    for k in range(0, len(files), per):
        ims = [Image.open(f) for f in files[k:k + per]]; w, h = ims[0].size
        rows = (len(ims) + a.cols - 1) // a.cols
        sheet = Image.new("RGB", (w * a.cols, h * rows), "white")
        for i, im in enumerate(ims): sheet.paste(im, ((i % a.cols) * w, (i // a.cols) * h))
        name = f"{out}_{k // per + 1}.png"; sheet.save(name); print(name, len(ims), "pages")
if __name__ == "__main__": main()
