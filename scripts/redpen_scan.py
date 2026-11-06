#!/usr/bin/env python3
"""textbook-engine / scripts/redpen_scan.py — 저자 빨간펜 스캔 판독 준비

사용: python3 scripts/redpen_scan.py <피드백.pdf> <출력 폴더> [--dpi 130] [--first N]
  1. 전 쪽을 dpi로 렌더 (p-NN.png)
  2. 쪽마다 빨간 픽셀을 세어 표시가 있는 쪽을 가려낸다 (한 쪽도 빠뜨리지 않도록 눈 대신 픽셀로)
  3. 표시가 있는 쪽은 빨간 픽셀이 있는 세로 띠(100px 단위)를 묶어 1.6배 확대 크롭 (strip-NN-k.png)
  4. 요약(summary.txt): 쪽 → 띠 목록. 판독 문서는 이 목록을 위에서부터 하나씩 대조하며 쓴다.
  --first N : PDF 1쪽의 책 쪽 번호 (판독 문서에 책 쪽 번호로 적기 위해)
교훈(9/17): 콘택트시트만 보고 판독하면 작은 취소선을 놓친다. 반드시 이 스캔을 먼저 돌린다.
"""
import argparse, subprocess, glob, os
import numpy as np
from PIL import Image

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("pdf"); ap.add_argument("out"); ap.add_argument("--dpi", type=int, default=130); ap.add_argument("--first", type=int, default=1)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    subprocess.run(["pdftoppm", "-r", str(a.dpi), "-png", a.pdf, os.path.join(a.out, "p")], check=True)
    lines = []
    for f in sorted(glob.glob(os.path.join(a.out, "p-*.png"))):
        idx = int(os.path.basename(f)[2:-4]); book = idx + a.first - 1
        im = Image.open(f).convert("RGB"); arr = np.asarray(im).astype(int)
        r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
        red = (r > 140) & (g < 130) & (b < 130) & (r - g > 50)
        n = int(red.sum())
        if n < 8: continue
        ys = np.where(red.any(axis=1))[0]
        bands, cur = [], [ys[0], ys[0]]
        for y in ys[1:]:
            if y - cur[1] > 60: bands.append(cur); cur = [y, y]
            else: cur[1] = y
        bands.append(cur)
        H, W = red.shape
        for k, (y0, y1) in enumerate(bands):
            y0 = max(0, y0 - 60); y1 = min(H, y1 + 60)
            crop = im.crop((0, y0, W, y1)); crop = crop.resize((int(W * 1.6), int((y1 - y0) * 1.6)), Image.LANCZOS)
            crop.save(os.path.join(a.out, f"strip-{book:03d}-{k+1}.png"))
        lines.append(f"book p{book} (pdf {idx}): red={n} bands={[(int(b[0]),int(b[1])) for b in bands]}")
    open(os.path.join(a.out, "summary.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines) if lines else "no red marks found")
if __name__ == "__main__": main()
