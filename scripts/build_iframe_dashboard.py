"""
챕터별 iframe 분리 대시보드 빌더.

각 팀의 원본 파일을 손대지 않고, 작은 snippet (탭 숨김 + 자동 챕터 활성화) 만
삽입해서 챕터별 폴더에 배치한다. 외부 shell index.html 이 탭과 iframe 전환을 담당.

산출물:
  dashboard/final/
    ├── index.html       (shell — 탭 + iframe)
    ├── ch1/  (gyubeen)
    ├── ch2/  (youngwoo)
    └── ch3/  (mine + 페이지 3 작업)
"""
import shutil
from pathlib import Path

BASE  = Path('d:/바탕화면/BAF/환경_대시보드/seoul-bigdata')
FINAL = BASE / 'dashboard' / 'final'

# ─── 원본 파일 ───────────────────────────────────────────────
GYU_HTML  = BASE / 'dashboard' / '0508' / 'index_claude_0508.html'
GYU_DATA  = BASE / 'dashboard' / '0508' / 'data.js'

YW_HTML   = BASE / '_merge_work' / 'yw_ch2.html'
YW_DATA1  = BASE / '_merge_work' / 'data2_1.js'
YW_DATA2  = BASE / '_merge_work' / 'data2_2.js'
YW_DATA3  = BASE / '_merge_work' / 'data2_3.js'

MINE_HTML       = BASE / 'dashboard' / '0505' / 'index_claude_0505.html'
MINE_DATA       = BASE / 'dashboard' / '0505' / 'data.js'
FACILITIES      = BASE / 'dashboard' / 'facilities.js'
DISTANCE_MATRIX = BASE / 'dashboard' / 'distance_matrix.js'

# ─── 디렉토리 준비 ────────────────────────────────────────────
for sub in ['ch1', 'ch2', 'ch3']:
    (FINAL / sub).mkdir(parents=True, exist_ok=True)


def inject_iframe_setup(html: str, chapter_idx: int) -> str:
    """body 끝에 탭숨김 CSS + 챕터자동활성화 JS 삽입."""
    snippet = f'''
<!-- ═══════════ iframe 모드 자동 주입 (shell 에서 로드 시) ═══════════ -->
<style>
  /* 외부 shell 이 탭 담당 → 내부 탭 숨김 */
  .tabs {{ display: none !important; }}
</style>
<script>
  /* DOM 준비되면 즉시 CH.{chapter_idx+1} 활성화 */
  document.addEventListener('DOMContentLoaded', function() {{
    if (typeof sw === 'function') sw({chapter_idx});
    else if (typeof switchTab === 'function') switchTab({chapter_idx});
  }});
</script>
'''
    if '</body>' in html:
        return html.replace('</body>', snippet + '</body>')
    return html + snippet


# ─── CH.1 (gyubeen) ─────────────────────────────────────────
shutil.copy(GYU_DATA, FINAL / 'ch1' / 'data.js')
ch1 = inject_iframe_setup(GYU_HTML.read_text(encoding='utf-8'), 0)
(FINAL / 'ch1' / 'index.html').write_text(ch1, encoding='utf-8')
print(f'[ch1] index.html ({len(ch1):,} chars), data.js')

# ─── CH.2 (youngwoo) ────────────────────────────────────────
shutil.copy(YW_DATA1, FINAL / 'ch2' / 'data2_1.js')
shutil.copy(YW_DATA2, FINAL / 'ch2' / 'data2_2.js')
shutil.copy(YW_DATA3, FINAL / 'ch2' / 'data2_3.js')
ch2 = inject_iframe_setup(YW_HTML.read_text(encoding='utf-8'), 1)
(FINAL / 'ch2' / 'index.html').write_text(ch2, encoding='utf-8')
print(f'[ch2] index.html ({len(ch2):,} chars), data2_1/2/3.js')

# ─── CH.3 (mine) ─────────────────────────────────────────────
shutil.copy(MINE_DATA, FINAL / 'ch3' / 'data.js')
shutil.copy(FACILITIES, FINAL / 'ch3' / 'facilities.js')
shutil.copy(DISTANCE_MATRIX, FINAL / 'ch3' / 'distance_matrix.js')
ch3 = inject_iframe_setup(MINE_HTML.read_text(encoding='utf-8'), 2)
(FINAL / 'ch3' / 'index.html').write_text(ch3, encoding='utf-8')
print(f'[ch3] index.html ({len(ch3):,} chars), data.js, facilities.js, distance_matrix.js')


# ─── Shell index.html ────────────────────────────────────────
shell = '''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>서울 폐기물 대시보드 — 통합</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=JetBrains+Mono:wght@500;600&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#0a0a0a; --bg2:#141414; --bg3:#1a1a1a;
  --border:#262626; --border2:#3a3a3a;
  --text:#e5e5e5; --text2:#a8a8a8; --text3:#666;
  --green:#16a34a; --amber:#d97706; --red:#dc2626;
  --teal:#009975;
}
*{margin:0;padding:0;box-sizing:border-box}
html,body{height:100%;overflow:hidden}
body{font-family:'Noto Sans KR',-apple-system,BlinkMacSystemFont,sans-serif;background:var(--bg);color:var(--text);display:flex;flex-direction:column}
header{display:flex;align-items:center;gap:16px;padding:10px 20px;background:var(--bg2);border-bottom:1px solid var(--border);flex-shrink:0}
.brand{font-size:14px;font-weight:700;color:var(--text);letter-spacing:-.3px;display:flex;align-items:center;gap:10px}
.brand .mono{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--text3);font-weight:500}
nav.tabs{display:flex;gap:6px;margin-left:auto}
.tab{display:flex;align-items:center;gap:8px;padding:8px 16px;background:var(--bg3);border:1px solid var(--border);border-radius:6px;cursor:pointer;font-size:13px;color:var(--text2);transition:all .15s;user-select:none}
.tab:hover{border-color:var(--border2);color:var(--text)}
.tab .num{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;letter-spacing:.04em;color:var(--text3);background:var(--bg);padding:2px 6px;border-radius:3px}
.tab.active{color:var(--text);font-weight:500}
.tab.green.active{border-color:var(--green);background:rgba(22,163,74,.1)}
.tab.green.active .num{color:var(--green);background:rgba(22,163,74,.18)}
.tab.amber.active{border-color:var(--amber);background:rgba(217,119,6,.1)}
.tab.amber.active .num{color:var(--amber);background:rgba(217,119,6,.18)}
.tab.red.active{border-color:var(--red);background:rgba(220,38,38,.1)}
.tab.red.active .num{color:var(--red);background:rgba(220,38,38,.18)}
.frames{flex:1;position:relative;overflow:hidden}
iframe{position:absolute;inset:0;width:100%;height:100%;border:0;background:var(--bg);display:none}
iframe.active{display:block}
</style>
</head>
<body>
<header>
  <div class="brand">서울 폐기물 대시보드<span class="mono">2020 → 2024</span></div>
  <nav class="tabs">
    <div class="tab green active" onclick="show(0)"><span class="num">CH.1</span>진단</div>
    <div class="tab amber" onclick="show(1)"><span class="num">CH.2</span>분석</div>
    <div class="tab red" onclick="show(2)"><span class="num">CH.3</span>처방</div>
  </nav>
</header>
<div class="frames">
  <iframe id="f0" class="active" src="ch1/index.html"></iframe>
  <iframe id="f1" data-src="ch2/index.html"></iframe>
  <iframe id="f2" data-src="ch3/index.html"></iframe>
</div>
<script>
function show(i){
  document.querySelectorAll('.tab').forEach(function(t,j){ t.classList.toggle('active', i===j); });
  document.querySelectorAll('iframe').forEach(function(f,j){
    f.classList.toggle('active', i===j);
    /* lazy load: 처음 클릭 시점에 src 세팅 */
    if (i===j && !f.src && f.dataset.src) { f.src = f.dataset.src; }
  });
}
</script>
</body>
</html>
'''
(FINAL / 'index.html').write_text(shell, encoding='utf-8')
print(f'[shell] index.html ({len(shell):,} chars)')

print('\n[done] dashboard/final/ 빌드 완료')
