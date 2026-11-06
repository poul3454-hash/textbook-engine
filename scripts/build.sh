#!/usr/bin/env bash
# textbook-engine / scripts/build.sh
# 사용: scripts/build.sh <책 폴더> [출력 이름]
#   책 폴더에는 pre.tex, chNN.tex (번호순), summary.tex 가 있어야 한다.
#   pre.tex 는 \bookname·\partlabel·\partfoot 정의 → \input{preamble.tex} → \begin{document} → 도비라 까지.
#   결과: <책 폴더>/build/<출력 이름>.pdf, 에러·쪽수·overfull 요약 출력.
set -euo pipefail
BOOK="$(cd "${1:?책 폴더}" && pwd)"
OUT="${2:-main}"
ENGINE="$(cd "$(dirname "$0")/.." && pwd)"
cd "$BOOK"
mkdir -p build
{
  cat pre.tex
  for f in $(ls ch*.tex 2>/dev/null | sort -V); do cat "$f"; echo; done
  [ -f summary.tex ] && cat summary.tex
  echo '\end{document}'
} > "build/$OUT.tex"
export TEXINPUTS="$ENGINE/template:$BOOK:${TEXINPUTS:-}"
cd build
xelatex -interaction=nonstopmode "$OUT.tex" >/dev/null 2>&1 || true
xelatex -interaction=nonstopmode "$OUT.tex" >/dev/null 2>&1 || true
ERR=$(grep -c '^!' "$OUT.log" || true)
PAGES=$(pdfinfo "$OUT.pdf" 2>/dev/null | awk '/^Pages/{print $2}')
OVER=$(grep -c 'Overfull .hbox' "$OUT.log" || true)
echo "errors: $ERR  pages: ${PAGES:-?}  overfull: $OVER  -> $BOOK/build/$OUT.pdf"
if [ "$ERR" != "0" ]; then grep -n -A3 '^!' "$OUT.log" | head -40; exit 1; fi
if [ "$OVER" != "0" ]; then grep -n 'Overfull .hbox' "$OUT.log" | head; fi
