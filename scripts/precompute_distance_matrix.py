"""
서울 25개 자치구 × 39개 민간 소각 시설 — 실제 도로거리·소요시간 매트릭스 계산.

소스: dashboard/facilities.js (PRIVATE_FACILITIES, SEOUL_GU_COORDS)
API : Kakao Mobility Directions (KAKAO_REST_API_KEY 동일)

호출 횟수: 25 × 38(고유좌표) ≈ 950회. 캐시(data/distance_matrix_cache.json) 활용 시 재실행 0회.

출력:
  - dashboard/distance_matrix.js
      const DISTANCE_MATRIX = { "강남구": { "37.354049,127.364479": {d: 42.2, t: 47}, ... }, ... };
      d = km, t = 분
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT      = Path(r"d:\바탕화면\BAF")
DASH_PROJ = ROOT / "환경_대시보드" / "seoul-bigdata"
DASH_DIR  = DASH_PROJ / "dashboard"
FACILITIES_JS = DASH_DIR / "facilities.js"
CACHE_PATH = DASH_PROJ / "data" / "distance_matrix_cache.json"
OUT_JS     = DASH_DIR / "distance_matrix.js"

KAKAO_DIR_URL = "https://apis-navi.kakaomobility.com/v1/directions"


def load_dotenv_file(path: Path) -> None:
    if not path.exists() or path.stat().st_size == 0:
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def get_kakao_key() -> str:
    for env_path in [DASH_PROJ / ".env", ROOT / "26-1_환경프로젝트" / ".env"]:
        load_dotenv_file(env_path)
    key = os.getenv("KAKAO_REST_API_KEY", "").strip()
    if not key:
        raise RuntimeError("KAKAO_REST_API_KEY 미설정")
    return key


def parse_facilities_js() -> tuple[list[dict], list[dict]]:
    txt = FACILITIES_JS.read_text(encoding="utf-8")
    fac = json.loads(re.search(r"const PRIVATE_FACILITIES = (\[[\s\S]*?\]);", txt).group(1))
    gu  = json.loads(re.search(r"const SEOUL_GU_COORDS = (\[[\s\S]*?\]);",   txt).group(1))
    return gu, fac


def coord_key(lat: float, lng: float) -> str:
    return f"{round(lat, 6):.6f},{round(lng, 6):.6f}"


def directions(orig_lat: float, orig_lng: float, dest_lat: float, dest_lng: float, headers: dict) -> dict | None:
    """1쌍 호출 — 성공 시 {distance_m, duration_s}, 실패 시 None."""
    params = {
        "origin": f"{orig_lng},{orig_lat}",      # Kakao는 x,y = lng,lat
        "destination": f"{dest_lng},{dest_lat}",
        "priority": "RECOMMEND",
    }
    try:
        r = requests.get(KAKAO_DIR_URL, headers=headers, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
    except (requests.RequestException, ValueError):
        return None
    routes = data.get("routes") or []
    if not routes:
        return None
    route = routes[0]
    if route.get("result_code") != 0:
        return None
    s = route.get("summary") or {}
    if "distance" not in s or "duration" not in s:
        return None
    return {"distance_m": int(s["distance"]), "duration_s": int(s["duration"])}


def load_cache() -> dict:
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def save_cache(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    headers = {"Authorization": f"KakaoAK {get_kakao_key()}"}
    gu_list, fac_list = parse_facilities_js()
    print(f"[로드] 자치구 {len(gu_list)}개, 시설 {len(fac_list)}개")

    # 시설 좌표 중복 제거 (예: 천안 환경에너지사업소 320·250톤 동일 좌표)
    unique_dests: dict[str, dict] = {}
    for f in fac_list:
        k = coord_key(f["lat"], f["lng"])
        if k not in unique_dests:
            unique_dests[k] = {"lat": f["lat"], "lng": f["lng"], "name": f["name"]}
    print(f"[중복제거] 고유 시설 좌표 {len(unique_dests)}개")

    cache = load_cache()
    print(f"[캐시] {len(cache)}건 로드됨")

    total_pairs = len(gu_list) * len(unique_dests)
    print(f"[목표] 총 호출 쌍 {total_pairs}개")

    matrix: dict[str, dict] = {}
    n_done = n_api = n_fail = 0
    SAVE_EVERY = 50  # 50쌍마다 캐시 디스크 저장

    for gu in gu_list:
        gu_name, gu_lat, gu_lng = gu["name"], gu["lat"], gu["lng"]
        matrix[gu_name] = {}

        for dk, dest in unique_dests.items():
            cache_key = f"{gu_name}|{dk}"
            if cache_key in cache and cache[cache_key].get("distance_m") is not None:
                rec = cache[cache_key]
            else:
                rec = directions(gu_lat, gu_lng, dest["lat"], dest["lng"], headers)
                n_api += 1
                if rec is None:
                    cache[cache_key] = {"distance_m": None, "duration_s": None}
                    n_fail += 1
                    time.sleep(0.1)
                else:
                    cache[cache_key] = rec
                    time.sleep(0.12)

                if n_api % SAVE_EVERY == 0:
                    save_cache(cache)
                    print(f"  [진행] API {n_api}회, 실패 {n_fail}건 (캐시 저장됨)")

            if rec and rec.get("distance_m") is not None:
                matrix[gu_name][dk] = {
                    "d": round(rec["distance_m"] / 1000, 1),     # km
                    "t": round(rec["duration_s"] / 60),          # 분
                }
            n_done += 1

    save_cache(cache)
    ok_count = sum(len(v) for v in matrix.values())
    print(f"\n[완료] 매트릭스 셀 {ok_count}/{total_pairs} (실패 {total_pairs - ok_count})")

    # ─── JS 출력 ─────────────────────────────────────────
    js_lines = [
        "/* Auto-generated by scripts/precompute_distance_matrix.py */",
        "/* Source: Kakao Mobility Directions API (실제 자동차 도로거리·소요시간) */",
        f"/* {len(gu_list)} 자치구 × {len(unique_dests)} 고유 시설좌표 = {ok_count} 셀 */",
        "/* lookup: DISTANCE_MATRIX[guName][`${lat.toFixed(6)},${lng.toFixed(6)}`] -> {d:km, t:분} */",
        "",
        "const DISTANCE_MATRIX = " + json.dumps(matrix, ensure_ascii=False, indent=2) + ";",
        "",
        "if (typeof window !== 'undefined') {",
        "  window.DISTANCE_MATRIX = DISTANCE_MATRIX;",
        "}",
        "",
    ]
    OUT_JS.write_text("\n".join(js_lines), encoding="utf-8")
    print(f"저장: {OUT_JS} ({OUT_JS.stat().st_size:,} bytes)")

    # 통계
    all_d = [c["d"] for v in matrix.values() for c in v.values()]
    all_t = [c["t"] for v in matrix.values() for c in v.values()]
    if all_d:
        print(f"\n[통계] 도로거리 min={min(all_d):.1f}km / mean={sum(all_d)/len(all_d):.1f}km / max={max(all_d):.1f}km")
        print(f"[통계] 소요시간 min={min(all_t)}분 / mean={sum(all_t)/len(all_t):.0f}분 / max={max(all_t)}분")


if __name__ == "__main__":
    main()
