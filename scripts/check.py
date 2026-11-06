#!/usr/bin/env python3
"""textbook-engine / scripts/check.py — 빌드 결과 검수 (고아 줄·파리티·백지·정답 푸터)

사용: python3 scripts/check.py <책 폴더>/build/main.pdf [--first N] [--src <책 폴더>]
  --first N : 첫 쪽의 실제 쪽 번호 (도비라 쪽 번호). 생략하면 PDF 1쪽 = 책 1쪽.
  --src     : 소스 폴더를 주면 setans 푸터와 sol 의 '답 X' 를 대조한다.

검사 항목
  1. 고아 줄: 한 쪽 안에서 길이 1~3 글자의 단독 줄 (문단 마지막 토막). '초진'·'풀이' 같은 라벨은 오탐.
  2. 파리티: 강 시작(\themetitle 줄 = 두 자리 번호 + 공백 + 제목)은 짝수 쪽, 도비라는 홀수 쪽.
  3. 백지: 글자 수 1 이하인 쪽 목록 (의도된 백지인지 확인).
  4. 정답 푸터: 소스의 \setans{NN \; 답 ·...} 와 해당 문항 \sol 끝의 '답 …' 비교.
"""
import re, subprocess, sys, argparse, glob, os

def page_text(pdf, p, layout=True):
    args = ["pdftotext", "-f", str(p), "-l", str(p)] + (["-layout"] if layout else []) + [pdf, "-"]
    return subprocess.run(args, capture_output=True, text=True).stdout

def npages(pdf):
    out = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    m = re.search(r"Pages:\s+(\d+)", out); return int(m.group(1))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("pdf"); ap.add_argument("--first", type=int, default=1); ap.add_argument("--src")
    a = ap.parse_args()
    n = npages(a.pdf); off = a.first - 1
    orphans, blanks, starts, covers = [], [], [], []
    for i in range(1, n + 1):
        t = page_text(a.pdf, i, layout=False)
        if len(t.strip()) <= 1: blanks.append(i + off); continue
        lines = [l.strip() for l in t.splitlines()]
        for j, l in enumerate(lines):
            if 1 <= len(l) <= 3 and re.search(r"[가-힣]", l) and l not in ("초진", "풀이", "정답", "접선", "TIP"):
                if j > 0 and len(lines[j - 1]) > 20: orphans.append((i + off, l))
        head = "\n".join(lines[:12])
        if re.search(r"^\s*\d{2}\s{2,}\S", head, re.M): starts.append(i + off)
        if "정확하게 진단하고" in head: covers.append(i + off)
    print(f"pages {n} (book {a.first}~{n+off})")
    print("blank pages:", blanks or "none")
    bad = [p for p in starts if p % 2]; print("chapter starts:", starts, "| odd (BAD):", bad or "none")
    badc = [p for p in covers if p % 2 == 0]; print("part covers:", covers, "| even (BAD):", badc or "none")
    print("orphan lines:", orphans or "none")
    if a.src:
        for f in sorted(glob.glob(os.path.join(a.src, "ch*.tex"))):
            s = open(f, encoding="utf-8").read()
            foot = dict(re.findall(r"\\setans\{.*?(\d\d)\s*\\;\s*([^·}]+?)\s*(?:\\;·\\;|\})", s))
            foot.update(dict(re.findall(r"·\\;(\d\d)\s*\\;\s*([^}]+?)\s*\}", s)))
            sols = re.findall(r"\\phead\{(\d\d)\}.*?\\sol\{\}\{.*?답\s*([^.}\n]+)[.}]", s, re.S)
            for num, ans in sols:
                fa = foot.get(num, "").strip()
                if fa and fa.replace(" ", "") != ans.strip().replace(" ", ""):
                    print(f"  ANSWER MISMATCH {os.path.basename(f)} {num}: footer '{fa}' vs sol '{ans.strip()}'")
if __name__ == "__main__": main()
