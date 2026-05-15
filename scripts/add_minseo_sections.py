"""
minseo (dashboard_minseo_0508_v5/dashboard) 의 2.4 (재정 부담 구조 분석) 와
3.2 (정책 시뮬레이터) 를 final/ch2/ 와 final/ch3/ 에 외과적으로 주입한다.

기존 챕터 동작은 건드리지 않고:
  - 2.4 HTML 을 ch2 의 CH.2 page div 닫기 직전에 삽입
  - 3.2 HTML 을 ch3 의 CH.3 page div 닫기 직전에 삽입
  - finance/policy CSS 를 각 파일의 <style> 끝에 추가
  - finance/policy JS 함수 묶음을 각 파일의 main <script> 끝에 추가
  - 데이터: minseo 의 새 data.js (const GU/LIVING_POP/... 통합본) 와
             data_finance_burden2023.js (BURDEN_2023 + FINANCE) 사용
  - iframe DOMContentLoaded 핸들러에 minseo init 호출 추가

* 새 minseo 파일의 정확한 라인 (origin/minseoyoo @ 8123f7c, 2722줄):
    2.4 HTML: 745-811   (CH.2 page close at 812)
    3.2 HTML: 876-935   (CH.3 page close at 936)
    CSS additions: 269-399   (</style> at 401)
    JS finance/policy: 2055-2711   (/* INIT */ at 2712)
"""
import re
import shutil
from pathlib import Path

BASE  = Path('d:/바탕화면/BAF/환경_대시보드/seoul-bigdata')
WORK  = BASE / '_merge_work' / 'minseo'
FINAL = BASE / 'dashboard' / 'final'

MINSEO_HTML  = WORK / 'index_minseo.html'
MINSEO_DATA  = WORK / 'data.js'
FINANCE_DATA = WORK / 'data_finance_burden2023.js'


# ─── helpers ────────────────────────────────────────────────
def find_div_close(html: str, open_pattern: str) -> int:
    m = re.search(open_pattern, html)
    if not m:
        raise ValueError(f'no match: {open_pattern}')
    i = m.end()
    depth = 1
    while i < len(html) and depth > 0:
        no = html.find('<div', i); nc = html.find('</div>', i)
        if nc == -1: return -1
        if no != -1 and no < nc:
            depth += 1; i = no + 4
        else:
            depth -= 1
            if depth == 0: return nc
            i = nc + 6
    return -1


# ─── 1) minseo 에서 추출 ────────────────────────────────────
m_html = MINSEO_HTML.read_text(encoding='utf-8')
m_lines = m_html.split('\n')

# 2.4 HTML: '<!-- 2.4' 부터 minseo 의 pg1 close 직전까지
m24_start = m_html.find('<!-- 2.4')
if m24_start == -1: raise ValueError('"<!-- 2.4" not found in minseo')
pg1_close_minseo = find_div_close(m_html, r'<div\s+class="page[^"]*"\s+id="pg1"[^>]*>')
ch24_html = m_html[m24_start:pg1_close_minseo].rstrip()

# 3.2 HTML: section-num 3.2 의 wrapping div 부터 pg2 close 직전까지
m32_match = re.search(
    r'<div\s+class="section-div"[^>]*>\s*<span\s+class="section-num">3\.2',
    m_html,
)
if not m32_match: raise ValueError('3.2 section-div not found in minseo')
m32_start = m32_match.start()
pg2_close_minseo = find_div_close(m_html, r'<div\s+class="page[^"]*"\s+id="pg2"[^>]*>')
ch32_html = m_html[m32_start:pg2_close_minseo].rstrip()

# CSS minseo 추가본: 라인 269-399 (1-indexed → 0-indexed 268:399)
css_block = '\n'.join(m_lines[268:399])

# JS finance/policy: 라인 2055-2711 (closePopup 다음 finance helper 부터 /* INIT */ 직전까지)
js_block = '\n'.join(m_lines[2054:2711])

print(f'[extract] 2.4 HTML: {len(ch24_html):,} chars')
print(f'[extract] 3.2 HTML: {len(ch32_html):,} chars')
print(f'[extract] CSS:      {len(css_block):,} chars (lines 269-399)')
print(f'[extract] JS:       {len(js_block):,} chars (lines 2055-2711)')


# ─── 2) ch2/index.html 수정 (youngwoo + 2.4) ────────────────
ch2_path = FINAL / 'ch2' / 'index.html'
ch2 = ch2_path.read_text(encoding='utf-8')

# (a) 2.4 HTML 을 pg1 close 직전에 주입
pg1_close = find_div_close(ch2, r'<div\s+class="page[^"]*"\s+id="pg1"[^>]*>')
ch2 = (
    ch2[:pg1_close]
    + '\n  <!-- ════════════ 2.4 (from minseo) ════════════ -->\n'
    + ch24_html
    + '\n\n'
    + ch2[pg1_close:]
)

# (b) CSS 추가 + ch2/2.4 레이아웃 override (지도를 위로 풀폭)
ch2_layout_override = """
/* ════════════ ch2/2.4 레이아웃 override: 지도 위로(full-width), 산점도+매트릭스 아래 ════════════ */
.finance-combined-grid{
  grid-template-columns: 1fr 1fr !important;
}
.finance-combined-grid > .finance-map-card{
  grid-column: 1 / -1 !important;
}
.finance-map-card .lmap{
  height: 380px !important;
}
.finance-detail-wide{
  grid-column: 1 / -1 !important;
}
@media(max-width:1100px){
  .finance-combined-grid{
    grid-template-columns: 1fr !important;
  }
}
"""
style_close = ch2.find('</style>')
ch2 = (
    ch2[:style_close]
    + '\n/* ════════════ FROM MINSEO (finance/policy/matrix/scenario styles) ════════════ */\n'
    + css_block
    + ch2_layout_override
    + ch2[style_close:]
)

# (c) JS 추가
last_script_close = ch2.rfind('</script>')
ch2 = (
    ch2[:last_script_close]
    + '\n\n/* ════════════ FROM MINSEO (helpers + finance/policy fns) ════════════ */\n'
    + js_block
    + '\n'
    + ch2[last_script_close:]
)

# (d) data 스크립트 태그 — youngwoo 의 data2_*.js 는 그대로 두고 (2.1-2.3 가 의존),
#     minseo 의 data_finance_burden2023.js 만 추가 (2.4 가 의존하는 BURDEN_2023, FINANCE)
old_data_tag = '<script src="data2_3.js"></script>'
new_data_tag = (
    '<script src="data2_3.js"></script>\n'
    '<script src="data_finance_burden2023.js"></script>'
)
assert old_data_tag in ch2, 'ch2 의 data2_3.js 스크립트 태그를 못 찾음'
ch2 = ch2.replace(old_data_tag, new_data_tag, 1)

# (e) iframe init 핸들러
old = "    else if (typeof switchTab === 'function') switchTab(1);\n  });"
new = (
    "    else if (typeof switchTab === 'function') switchTab(1);\n"
    "    setTimeout(function(){\n"
    "      if (typeof initFinanceAnalysis === 'function') initFinanceAnalysis();\n"
    "    }, 350);\n"
    "  });"
)
assert old in ch2, 'ch2 iframe handler 패턴 못 찾음'
ch2 = ch2.replace(old, new, 1)

ch2_path.write_text(ch2, encoding='utf-8')

# 데이터 파일: youngwoo 의 data2_*.js 는 build_iframe_dashboard.py 가 이미 복사함 (유지)
# minseo 의 finance 데이터만 추가
shutil.copy(FINANCE_DATA, FINAL / 'ch2' / 'data_finance_burden2023.js')
print(f'[ch2] index.html ({len(ch2):,} chars) - youngwoo data2_*.js 유지 + finance 추가')


# ─── 3) ch3/index.html 수정 (mine + 3.2) ────────────────────
ch3_path = FINAL / 'ch3' / 'index.html'
ch3 = ch3_path.read_text(encoding='utf-8')

# (a) 3.2 HTML
pg2_close = find_div_close(ch3, r'<div\s+class="page[^"]*"\s+id="pg2"[^>]*>')
ch3 = (
    ch3[:pg2_close]
    + '\n  <!-- ════════════ 3.2 (from minseo) ════════════ -->\n'
    + ch32_html
    + '\n\n'
    + ch3[pg2_close:]
)

# (b) CSS
style_close = ch3.find('</style>')
ch3 = (
    ch3[:style_close]
    + '\n/* ════════════ FROM MINSEO (finance/policy/matrix/scenario styles) ════════════ */\n'
    + css_block
    + '\n'
    + ch3[style_close:]
)

# (c) JS
last_script_close = ch3.rfind('</script>')
ch3 = (
    ch3[:last_script_close]
    + '\n\n/* ════════════ FROM MINSEO (helpers + finance/policy fns) ════════════ */\n'
    + js_block
    + '\n'
    + ch3[last_script_close:]
)

# (d) data 스크립트 — mine 의 data.js 를 minseo 의 enriched data.js + finance 로 교체
ch3 = ch3.replace(
    '<script src="data.js"></script>',
    '<script src="data.js"></script>\n'
    '<script src="data_finance_burden2023.js"></script>',
    1,
)

# (e) iframe init 핸들러
old = "    else if (typeof switchTab === 'function') switchTab(2);\n  });"
new = (
    "    else if (typeof switchTab === 'function') switchTab(2);\n"
    "    setTimeout(function(){\n"
    "      if (typeof initPolicySimulator === 'function') initPolicySimulator();\n"
    "    }, 350);\n"
    "  });"
)
assert old in ch3, 'ch3 iframe handler 패턴 못 찾음'
ch3 = ch3.replace(old, new, 1)

ch3_path.write_text(ch3, encoding='utf-8')

# 데이터 파일 복사 (mine 의 data.js 를 minseo enriched 로 덮어씀)
shutil.copy(MINSEO_DATA,  FINAL / 'ch3' / 'data.js')
shutil.copy(FINANCE_DATA, FINAL / 'ch3' / 'data_finance_burden2023.js')
print(f'[ch3] index.html ({len(ch3):,} chars) - data.js (minseo enriched) + finance')

print('\n[done] minseo 2.4 / 3.2 v3 (origin/minseoyoo 8123f7c)')
