# textbook-engine

XeLaTeX 수학 교재(정면돌파 시리즈) 제작 엔진. **책 내용은 들어 있지 않다** — 조판 템플릿, 빌드·검수 스크립트, 피드백 판독 도구, 규칙 문서만. 책의 소스(강별 .tex)는 Claude 프로젝트 문서에 편별 최신판으로 보관한다.

## 구조
```
template/   preamble.tex        공통 프리앰블(양면 레이아웃·박스·소도구·tikz 스타일·한 장 정리 매크로)
            part-cover.tex      파트 도비라
            chapter-template.tex  강 골격(더미)
            summary-template.tex  한 장 정리 골격(번역기 표 정렬 구조 포함)
scripts/    build.sh            pre + ch* + summary → xelatex ×2 → 에러·쪽수·overfull 요약
            check.py            고아 줄·강 시작 파리티·백지·정답 푸터 대조
            contact_sheet.py    콘택트시트 PNG
            redpen_scan.py      빨간펜 스캔 → 빨간 픽셀 띠 크롭 (판독 누락 방지)
            stylescan.sh        비유·수사·금지 표기·lim 첨자 자기 검열
            split_source.py     프로젝트의 합본 소스 → pre/chNN/summary 로 분리
rules/      typesetting-rules.md  조판 규칙 ①~⑱ + 레이아웃
            writing-checklist.md  집필·피드백 절차
example/    sample-book/        더미 책 1강 — 엔진 동작 확인용
```

## 환경
- `xelatex` (texlive-xetex + xeCJK: Ubuntu는 `texlive-lang-chinese`), `fonts-noto-cjk` (Noto Serif/Sans CJK KR)
- `pdftoppm`, `pdftotext` (poppler-utils)
- Python 3: `pillow numpy sympy`

## 빠른 시작
```bash
# 1) 동작 확인
scripts/build.sh example/sample-book sample
python3 scripts/check.py example/sample-book/build/sample.pdf --src example/sample-book

# 2) 실제 책 재개: 프로젝트에서 '…-조판소스-vX.Y.tex' 를 받아 쪼갠다
python3 scripts/split_source.py ~/downloads/함수의극한편-1-6강-조판소스-v2.7.tex books/limits --use-engine
scripts/build.sh books/limits limits
python3 scripts/check.py books/limits/build/limits.pdf --first 1 --src books/limits
python3 scripts/contact_sheet.py books/limits/build/limits.pdf

# 3) 피드백 판독
python3 scripts/redpen_scan.py 피드백/11강.pdf fb/11 --first 101
#    → fb/11/summary.txt 와 strip-*.png 를 위에서부터 판독
```
`books/` 는 .gitignore 되어 있다. 책 소스는 여기에 올리지 않는다.

## 책별 pre.tex 작성법
```tex
\newcommand{\bookname}{정면돌파 미적분Ⅰ}
\newcommand{\partlabel}{함수의 연속편 v2.4}   % 헤더
\newcommand{\partfoot}{Ⅱ. 함수의 연속}        % 바깥 하단
\input{preamble.tex}
\begin{document}
\newcommand{\partnum}{PART Ⅱ. \; 함수의 연속 \; (7강--11강)}
\newcommand{\partlist}{7강 \; … \\ 8강 \; …}
\newcommand{\partchart}{…} \newcommand{\partprep}{…}
\newcommand{\firstpage}{57}                   % 앞 파트 마지막 쪽 + 1 (홀수)
\input{part-cover.tex}
```
- 강 파일은 `chNN.tex`, 맨 앞에 `\cleartoevenpage`. 한 장 정리는 `summary.tex`
- `\reflex`, `\bnum`, `\capt` 는 preamble에 있다. 기존 소스에 `\newcommand`로 남아 있으면 `\renewcommand`로 (split_source가 자동 처리)

## 다른 책에 쓸 때
색·폰트·박스 이름은 preamble 상단에서 바꾼다. 코너 명칭(개념/오진 주의/개념 문진/출제 차트/풀이 처방/초진/STEP/한 장 정리)은 시리즈 공통.
