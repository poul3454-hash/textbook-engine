#!/usr/bin/env python3
"""textbook-engine / scripts/split_source.py — 합쳐진 조판 소스(.tex 1개)를 pre.tex / chNN.tex / summary.tex 로 쪼갠다.

사용: python3 scripts/split_source.py <합본.tex> <출력 책 폴더>
  프로젝트 문서에 보관된 '…-조판소스-vX.Y.tex' 는 pre + ch* + summary + \\end{document} 를 이어 붙인 것이다.
  각 강은 "% === ... NN강 ..." 주석 블록으로, 한 장 정리는 "% === 한 장 정리" 로 시작한다.
  pre.tex 의 프리앰블은 engine의 template/preamble.tex 와 같으므로, 쪼갠 뒤 pre.tex 머리를
  \\bookname 등 정의 + \\input{preamble.tex} 로 바꿔 쓰면 된다 (--use-engine 옵션이 자동으로 시도).
"""
import re, sys, os, argparse

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("out"); ap.add_argument("--use-engine", action="store_true")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    s = open(a.src, encoding="utf-8").read()
    s = re.sub(r"\\end\{document\}\s*$", "", s)
    # 분리 지점: 강 주석 헤더 / 한 장 정리 헤더
    pat = re.compile(r"(?=^% =+\n% (\d{1,2})강 [^\n]*\n% =+\n)|(?=^% =+\n% 한 장 정리)", re.M)
    parts = [p for p in pat.split(s) if p is not None]
    # re.split with lookahead keeps delimiters attached to following chunk; group captures add None/num entries
    chunks, buf = [], ""
    for seg in re.split(r"(?=^% =+\n% (?:\d{1,2}강 |한 장 정리))", s, flags=re.M):
        if seg.strip(): chunks.append(seg)
    pre, rest = chunks[0], chunks[1:]
    if a.use_engine and "\\begin{document}" in pre:
        head, body = pre.split("\\begin{document}", 1)
        bn = re.search(r"\\cjkmed (.+?) \\textcolor\{prime\}\{\|\} (.+?)\};", head)
        pf = re.search(r"\\cjkmed (.+?) \\quad \{\\cjkbold\\textcolor\{prime\}\{\\thepage\}\}", head)
        pre = ("% pre.tex — engine preamble 사용\n"
               f"\\newcommand{{\\bookname}}{{{bn.group(1) if bn else '책 이름'}}}\n"
               f"\\newcommand{{\\partlabel}}{{{bn.group(2) if bn else '편 v0'}}}\n"
               f"\\newcommand{{\\partfoot}}{{{pf.group(1) if pf else 'Ⅰ. 단원'}}}\n"
               "\\input{preamble.tex}\n\\begin{document}" + body)
    open(os.path.join(a.out, "pre.tex"), "w", encoding="utf-8").write(pre)
    for c in rest:
        m = re.match(r"% =+\n% (\d{1,2})강", c)
        name = f"ch{int(m.group(1)):02d}.tex" if m else "summary.tex"
        if not m:  # 한 장 정리: \reflex·\bnum 은 engine preamble에 이미 있으므로 재정의로 바꾼다
            c = c.replace("\\newcommand{\\reflex}", "\\renewcommand{\\reflex}").replace("\\providecommand{\\reflex}", "\\renewcommand{\\reflex}")
            c = c.replace("\\newcommand{\\bnum}", "\\renewcommand{\\bnum}").replace("\\providecommand{\\bnum}", "\\renewcommand{\\bnum}")
        open(os.path.join(a.out, name), "w", encoding="utf-8").write(c)
        print("wrote", name, len(c), "chars")
    print("wrote pre.tex", len(pre), "chars")
if __name__ == "__main__": main()
