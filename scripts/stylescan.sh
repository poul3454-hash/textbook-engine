#!/usr/bin/env bash
# textbook-engine / scripts/stylescan.sh — 집필 자기 검열 (저자 성향 프로파일 §1·§2)
# 사용: scripts/stylescan.sh <책 폴더>
#   1) 그림 묘사형 동사·비유·수사 후보   2) 금지 표기(줄표, '자체 제작', 수능 언급)   3) lim 첨자 누락 의심
#   걸린 줄이 저자가 직접 준 문장이면 그대로 둔다. 아니면 직설로 고친다.
set -u
BOOK="${1:?책 폴더}"
cd "$BOOK"
echo "== 1. 비유·수사·그림 묘사형 동사 후보"
grep -n -E '건너|건넌|가로지|뚫|누른|눌러|눌린|달라붙|접착|처럼|마치|셈이다|세계|무기|자격|가른다|살아남|심판|울타리|공범|변장|도착지|달아나|치솟|몰린다|운명|주연|승부' ch*.tex summary.tex 2>/dev/null | cut -c1-160 || true
echo "== 2. 금지 표기"
grep -n -E ' — |—|자체 제작|수능은|수능이|시험은 이|수능 link|REMARK|APPROACH|STEP UP' ch*.tex summary.tex 2>/dev/null | cut -c1-160 || true
echo "== 3. lim 뒤에 첨자 없음 의심"
grep -n -E '\\lim[^_\\]' ch*.tex 2>/dev/null | grep -v 'limits' | cut -c1-120 || true
echo "== 4. 인라인 ∞/∞ (세로 분수 \\frac 써야 함)"
grep -n -E '∞/∞|0/0' ch*.tex summary.tex 2>/dev/null | grep -v '\\frac' | cut -c1-120 || true
echo "(끝)"
