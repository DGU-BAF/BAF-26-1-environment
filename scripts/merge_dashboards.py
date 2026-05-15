"""
3개 브랜치의 대시보드 병합 (v2 — 각 챕터의 헬퍼/init 함수 모두 보존):

- 베이스: gyubeen 의 dashboard/0508/index_claude_0508.html
  - gyubeen 은 `switchTab(i)` / `init11`, `init13` / 자체 const 사용
- CH.2: youngwoo 의 main script 전체를 IIFE 로 감싸 별도 <script> 블록으로 추가
  - 노출: initCh2, setRadarCluster, showMetricInfo, updateFactorPanel
- CH.3: 내 0505 의 main script 전체를 IIFE 로 감싸 별도 <script> 블록으로 추가
  - 노출: initCh3, runSim, updateWeights, closePopup
- switchTab 가로채기: i=1 → initCh2(), i=2 → initCh3() 1회 호출
"""
import re
import shutil
from pathlib import Path

BASE = Path('d:/바탕화면/BAF/환경_대시보드/seoul-bigdata')
OUT  = BASE / 'dashboard' / '0508'
WORK = BASE / '_merge_work'

GYU_PATH  = BASE / 'dashboard' / '0508' / 'index_claude_0508.html'
MINE_PATH = BASE / 'dashboard' / '0505' / 'index_claude_0505.html'
YW_PATH   = WORK / 'yw_ch2.html'

gyu  = GYU_PATH.read_text(encoding='utf-8')
mine = MINE_PATH.read_text(encoding='utf-8')
yw   = YW_PATH.read_text(encoding='utf-8')


# ─────────────────────────────────────────────────────────────────────
# 헬퍼: <div class="page" id="pgN">...</div> 추출 (깊이 카운트)
# ─────────────────────────────────────────────────────────────────────
def extract_page_div(html: str, pg_id: str) -> str:
    m = re.search(rf'<div\s+class="page[^"]*"\s+id="{pg_id}"[^>]*>', html)
    if not m:
        raise ValueError(f'pg_id={pg_id} not found')
    start = m.start()
    i = m.end()
    depth = 1
    while i < len(html) and depth > 0:
        no = html.find('<div', i); nc = html.find('</div>', i)
        if nc == -1: raise ValueError('unclosed div')
        if no != -1 and no < nc:
            depth += 1; i = no + 4
        else:
            depth -= 1; i = nc + 6
            if depth == 0: return html[start:i]
    raise ValueError('end not reached')


# ─────────────────────────────────────────────────────────────────────
# 헬퍼: <style>...</style> 본문 추출
# ─────────────────────────────────────────────────────────────────────
def style_body(html: str) -> str:
    m = re.search(r'<style[^>]*>', html)
    e = html.find('</style>', m.end())
    return html[m.end():e]


# ─────────────────────────────────────────────────────────────────────
# 헬퍼: main <script> 본문 추출 (GeoJSON 가 아닌, 챕터 로직 들어있는 마지막 <script>)
# ─────────────────────────────────────────────────────────────────────
def main_script_body(html: str) -> str:
    """가장 큰 inline <script> 본문 — 챕터 로직이 들어있는 블록."""
    blocks = re.findall(r'<script(?![^>]*src=)[^>]*>(.*?)</script>', html, re.DOTALL)
    return max(blocks, key=len)


# ─────────────────────────────────────────────────────────────────────
# 헬퍼: addEventListener('load', ...) 줄 제거 (CH.1 자동 init 막기)
# ─────────────────────────────────────────────────────────────────────
def strip_load_handler(js: str) -> str:
    # window.addEventListener('load',()=>initCh1());
    return re.sub(
        r"window\.addEventListener\(\s*['\"]load['\"]\s*,\s*\(\s*\)\s*=>\s*initCh1\(\)\s*\)\s*;?",
        "// [stripped] load->initCh1 (gyubeen 의 CH.1 init 사용)",
        js,
    )


# ─────────────────────────────────────────────────────────────────────
# 헬퍼: IIFE 로 감싸고 지정 함수를 window 에 노출
# ─────────────────────────────────────────────────────────────────────
def wrap_iife(js: str, exports: list[str], label: str) -> str:
    export_lines = '\n'.join(
        f'  if (typeof {n} !== "undefined") window.{n} = {n};'
        for n in exports
    )
    return (
        f'/* ════════════════ {label} (IIFE 격리) ════════════════ */\n'
        f'(function(){{\n'
        f'{js}\n'
        f'/* — window 노출 — */\n'
        f'{export_lines}\n'
        f'}})();\n'
    )


# ─────────────────────────────────────────────────────────────────────
# 1) 페이지 div 주입
# ─────────────────────────────────────────────────────────────────────
yw_ch2_div  = extract_page_div(yw,   'pg1')
my_ch3_div  = extract_page_div(mine, 'pg2')
gyu_ch2_div = extract_page_div(gyu,  'pg1')
gyu_ch3_div = extract_page_div(gyu,  'pg2')

merged = gyu.replace(gyu_ch2_div, yw_ch2_div, 1)
merged = merged.replace(gyu_ch3_div, my_ch3_div, 1)
print(f'[HTML] CH.2 div ({len(yw_ch2_div)} chars), CH.3 div ({len(my_ch3_div)} chars) 주입 완료')


# ─────────────────────────────────────────────────────────────────────
# 2) youngwoo / mine main script 추출 및 IIFE 감싸기
# ─────────────────────────────────────────────────────────────────────
yw_js   = strip_load_handler(main_script_body(yw))
mine_js = strip_load_handler(main_script_body(mine))

yw_iife = wrap_iife(
    yw_js,
    exports=[
        'initCh1', 'initCh2', 'initCh3',     # 챕터 init (CH.2 우리가 사용)
        'sw',                                # youngwoo 의 sw — 노출 안 해도 되지만 안전망
        'setRadarCluster', 'showMetricInfo', 'updateFactorPanel',
        'setJongnoSlide', 'setAdjustedSlide',
    ],
    label='CH.2 from youngwoo',
)
mine_iife = wrap_iife(
    mine_js,
    exports=[
        'initCh1', 'initCh2', 'initCh3',
        'runSim', 'updateWeights',
        'closePopup',                       # CH.1 popup 의 "매칭 시뮬레이터로" 버튼이 호출
    ],
    label='CH.3 from mine 0505 + 페이지3 작업',
)
print(f'[JS]   youngwoo main script: {len(yw_js):,} chars -> IIFE')
print(f'[JS]   mine main script    : {len(mine_js):,} chars -> IIFE')


# ─────────────────────────────────────────────────────────────────────
# 3) switchTab 인터셉터 — 탭 진입 시 CH.2/CH.3 init 호출
# ─────────────────────────────────────────────────────────────────────
SWITCHTAB_HOOK = """
/* ════════════════ switchTab 인터셉터 ════════════════ */
(function(){
  if (typeof window.switchTab !== 'function') return;
  var _orig = window.switchTab;
  window._chInit = { 1: false, 2: false };
  window.switchTab = function(i){
    _orig(i);
    if (i === 1 && !window._chInit[1] && typeof window.initCh2 === 'function') {
      try { window.initCh2(); } catch(e){ console.error('initCh2 실패:', e); }
      window._chInit[1] = true;
    }
    if (i === 2 && !window._chInit[2] && typeof window.initCh3 === 'function') {
      try { window.initCh3(); } catch(e){ console.error('initCh3 실패:', e); }
      window._chInit[2] = true;
    }
  };
})();
"""


# ─────────────────────────────────────────────────────────────────────
# 4) </body> 직전에 새 <script> 블록들 삽입
# ─────────────────────────────────────────────────────────────────────
inserts = (
    '\n<script>\n' + yw_iife   + '</script>\n'
    '<script>\n'   + mine_iife + '</script>\n'
    '<script>'    + SWITCHTAB_HOOK + '</script>\n'
)

body_close = merged.rfind('</body>')
if body_close == -1:
    body_close = len(merged)
merged = merged[:body_close] + inserts + merged[body_close:]
print(f'[JS]   3개 추가 <script> 블록 삽입 (IIFE 2개 + switchTab hook)')


# ─────────────────────────────────────────────────────────────────────
# 5) CSS 추가 — 순서: mine → youngwoo → gyubeen (가장 마지막이 이김)
#    gyubeen 의 </style> 직전에 mine + youngwoo CSS 를 추가하면
#    gyubeen 정의 + (mine, youngwoo 가 추가/덮어쓴 것) 순으로 적용됨
#    → gyubeen 의 정의가 먼저 등장하므로 conflict 시 mine/youngwoo 가 이김
#    원래 의도는 gyubeen 이 이기는 것이므로, gyubeen 본체를 마지막에 두고
#    mine/youngwoo 는 그 앞에 둔다.
# ─────────────────────────────────────────────────────────────────────
yw_css   = style_body(yw)
mine_css = style_body(mine)

# gyubeen <style> 시작 직후에 mine/youngwoo 의 base CSS 를 prepend
m_style_open = re.search(r'<style[^>]*>', merged)
insert_pos = m_style_open.end()
prepend_css = (
    '\n/* ════════ FROM MINE 0505 (CH.3 대비 base) ════════ */\n' + mine_css +
    '\n/* ════════ FROM YOUNGWOO (CH.2 대비 base) ════════ */\n' + yw_css +
    '\n/* ════════ ↓ FROM GYUBEEN 0508 (CH.1 base, 마지막이라 conflict 시 이김) ════════ */\n'
)
merged = merged[:insert_pos] + prepend_css + merged[insert_pos:]
print(f'[CSS]  mine ({len(mine_css):,}) + youngwoo ({len(yw_css):,}) prepend 완료')


# ─────────────────────────────────────────────────────────────────────
# 6) 데이터 스크립트 태그 추가
# ─────────────────────────────────────────────────────────────────────
old_tag = '<script src="data.js"></script>'
new_tags = (
    '<script src="data.js"></script>\n'
    '<script src="data2_1.js"></script>\n'
    '<script src="data2_2.js"></script>\n'
    '<script src="data2_3.js"></script>\n'
    '<script src="facilities.js"></script>\n'
    '<script src="distance_matrix.js"></script>'
)
assert old_tag in merged
merged = merged.replace(old_tag, new_tags, 1)
print(f'[SCRIPT] data file 태그 추가')


# ─────────────────────────────────────────────────────────────────────
# 7) 결과 저장 & 데이터 파일 복사
# ─────────────────────────────────────────────────────────────────────
out_html = OUT / 'index_merged.html'
out_html.write_text(merged, encoding='utf-8')
print(f'[OUT]  {out_html} ({len(merged):,} chars)')

for src, dst in [
    (WORK / 'data2_1.js', OUT / 'data2_1.js'),
    (WORK / 'data2_2.js', OUT / 'data2_2.js'),
    (WORK / 'data2_3.js', OUT / 'data2_3.js'),
    (BASE / 'dashboard' / 'distance_matrix.js', OUT / 'distance_matrix.js'),
    (BASE / 'dashboard' / 'facilities.js',      OUT / 'facilities.js'),
]:
    shutil.copy(src, dst)

print('[done] merge v2 완료')
