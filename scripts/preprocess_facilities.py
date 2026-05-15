"""
민간 소각장 매칭 시뮬레이터용 시설 데이터 전처리.

입력:
  - regional_incinerator_candidates_combined.csv  (52개 시설, 위경도 없음)
  - 서울구청_주소_위경도추가.csv                 (25개 자치구 위경도)
  - 경기도_폐기물처리업체현황.csv                  (경기 시설 위경도 매칭용)

좌표 부여:
  - 경기 → 경기도_폐기물처리업체현황.csv 에서 시설명 매칭으로 정밀 좌표
  - 인천·충남 → Kakao 지오코딩 API (지번/도로명 주소)
  - 매칭 실패 시 → 시·군청 중심 좌표 (CITY_COORDS) fallback
  - 인천 도서지역(소청·덕적·백령 등 작은 시설)은 cap<5 필터에서 자연 제외

처리:
  - 작은 시설(<5톤/일) 제외, 결측 용량은 지역 중앙값으로 추정
  - 처리대상이 일반 폐기물 아닌 것 제외
  - 단가·잔여용량·CO₂ 추정 (거리·지역 기반)

출력:
  - dashboard/facilities.js  (PRIVATE_FACILITIES, SEOUL_GU_COORDS)
  - data/geocode_cache.json  (Kakao 결과 캐시 — 재실행 시 API 호출 절감)
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ─── 경로 ──────────────────────────────────────────────────────
ROOT      = Path(r"d:\바탕화면\BAF")
SRC_DIR   = ROOT / "26-1_환경프로젝트" / "outputs" / "eda"
DASH_PROJ = ROOT / "환경_대시보드" / "seoul-bigdata"
DASH_DIR  = DASH_PROJ / "dashboard"
RAW_DIR   = DASH_PROJ / "data" / "raw"
OUT_JS    = DASH_DIR / "facilities.js"
CACHE_PATH = DASH_PROJ / "data" / "geocode_cache.json"
GG_CSV    = RAW_DIR / "경기도_폐기물처리업체현황.csv"

# ─── 시/군 중심 좌표 (지오코딩 실패 시 fallback) ────────────────
# 출처: 각 시·군청 공식 좌표 (±2km 오차 허용)
CITY_COORDS = {
    # 경기도
    "광주시":   (37.4292, 127.2553),  "동두천시": (37.9034, 127.0606),
    "시흥시":   (37.3800, 126.8030),  "안산시":   (37.3236, 126.8219),
    "양주시":   (37.7853, 127.0457),  "오산시":   (37.1499, 127.0773),
    "화성시":   (37.1995, 126.8313),  "평택시":   (36.9921, 127.1129),
    # 충청남도
    "천안시":   (36.8151, 127.1140),  "공주시":   (36.4467, 127.1190),
    "보령시":   (36.3334, 126.6128),  "아산시":   (36.7898, 127.0019),
    "논산시":   (36.1872, 127.0989),  "계룡시":   (36.2745, 127.2486),
    "금산군":   (36.1085, 127.4881),  "서천군":   (36.0801, 126.6919),
    "청양군":   (36.4592, 126.8023),  "예산군":   (36.6809, 126.8449),
    "태안군":   (36.7456, 126.2980),
    # 인천 (자치구·군)
    "서구":     (37.5454, 126.6760),  "남동구":   (37.4474, 126.7314),
    "연수구":   (37.4099, 126.6783),  "강화군":   (37.7466, 126.4882),
    "옹진군":   (37.4470, 126.6362),  "부평구":   (37.5071, 126.7218),
    "동구":     (37.4742, 126.6435),  "중구":     (37.4737, 126.6217),
}

# 동 단위 fallback (인천 매칭 실패 / 주소 prefix 누락 케이스용)
# ※ 인천 오류동은 서구 (남동구가 아님), 인천 영종은 중구
DONG_TO_GU = {
    "고잔동": "남동구", "논현": "남동구", "남촌동": "남동구",
    "오류동": "서구",   "가좌동": "서구",   "경서동": "서구",
    "석남동": "서구",   "원창동": "동구",   "청천동": "부평구",
    "영종": "중구",     "앵고개": "남동구",
    # 인천 도서지역 (옹진군)
    "대청면": "옹진군", "백령면": "옹진군", "연평면": "옹진군",
    "자월면": "옹진군", "덕적면": "옹진군",
}


# ─── Kakao API ────────────────────────────────────────────────
def load_dotenv_file(path: Path) -> None:
    """단일 .env 파일을 환경변수에 로드 (이미 설정된 키는 덮어쓰지 않음)."""
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
    """대시보드 .env → 부모 프로젝트 .env 순으로 KAKAO_REST_API_KEY 탐색."""
    for env_path in [DASH_PROJ / ".env", ROOT / "26-1_환경프로젝트" / ".env"]:
        load_dotenv_file(env_path)
    key = os.getenv("KAKAO_REST_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "KAKAO_REST_API_KEY가 없습니다. "
            f"{DASH_PROJ / '.env'} 또는 {ROOT / '26-1_환경프로젝트' / '.env'}에 설정하세요."
        )
    return key


_KAKAO_ADDR_URL = "https://dapi.kakao.com/v2/local/search/address.json"
_KAKAO_KW_URL   = "https://dapi.kakao.com/v2/local/search/keyword.json"


def load_geocode_cache() -> dict[str, dict]:
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def save_geocode_cache(cache: dict[str, dict]) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def normalize_raw_address(s: str) -> str:
    """원본 주소의 흔한 오기 정리 — 'in 인천. 중구', 콤마, 두중공백 등."""
    s = str(s).strip()
    s = s.replace("인천. ", "인천광역시 ").replace("인천.", "인천광역시")
    s = re.sub(r"\s+", " ", s)
    return s


def _kakao_get(url: str, headers: dict, params: dict) -> list[dict]:
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json().get("documents") or []
    except (requests.RequestException, ValueError, KeyError):
        return []


def kakao_address_search(query: str, headers: dict) -> tuple[float, float] | tuple[None, None]:
    """주소 API: exact → similar 순. 첫 결과 반환."""
    for at in ("exact", "similar"):
        docs = _kakao_get(_KAKAO_ADDR_URL, headers, {"query": query, "analyze_type": at})
        if docs:
            d = docs[0]
            return float(d["y"]), float(d["x"])
        time.sleep(0.1)
    return None, None


def kakao_keyword_search(query: str, headers: dict, expected_region: str | None = None) -> tuple[float, float, str] | tuple[None, None, None]:
    """장소(키워드) API. expected_region이 주어지면 결과 주소에 포함되는지 검증."""
    docs = _kakao_get(_KAKAO_KW_URL, headers, {"query": query, "size": 5})
    time.sleep(0.1)
    for d in docs:
        addr_name = d.get("road_address_name") or d.get("address_name") or ""
        if expected_region and expected_region not in addr_name:
            continue
        return float(d["y"]), float(d["x"]), addr_name
    return None, None, None


def build_address_variants(addr: str, region: str) -> list[str]:
    """주소 API용 변형. 정확 → 괄호제거 → 시군구·동까지(parcel 제거) → 인천 prefix 보정."""
    s = normalize_raw_address(addr)
    variants: list[str] = []
    seen: set[str] = set()

    def add(v: str) -> None:
        v = v.strip()
        if v and v not in seen:
            seen.add(v)
            variants.append(v)

    add(s)
    add(re.sub(r"\s*\([^)]*\)", "", s))                       # 괄호 제거

    # 인천 — prefix 누락 케이스 보정
    if region in ("인천", "인천광역시") and not s.startswith("인천"):
        for dong, gu in DONG_TO_GU.items():
            if dong in s:
                add(f"인천광역시 {gu} {re.sub(r'\\s*\\([^)]*\\)', '', s)}")
                break
        else:
            add(f"인천광역시 {re.sub(r'\\s*\\([^)]*\\)', '', s)}")

    # 충남 표기 정리
    if region in ("충청남도", "충남"):
        add(s.replace("충남", "충청남도"))

    # parcel-only fallback: "시 군구 동" 까지만 — Kakao address DB에 없는 옛 지번 처리
    # 예) "충남 태안군 태안읍 삭선리 21-3" → "충남 태안군 태안읍 삭선리"
    parcel_drop = re.sub(r"(리|동)\s*[\d산][\d\-\s]*$", r"\1", s).strip()
    if parcel_drop != s:
        add(parcel_drop)
        if region in ("인천", "인천광역시") and not parcel_drop.startswith("인천"):
            add(f"인천광역시 {parcel_drop}")

    return variants


def geocode_kakao(addr: str, region: str, headers: dict, cache: dict, name: str | None = None) -> tuple[float, float, str] | tuple[None, None, None]:
    """1) 주소 API → 2) 키워드 API(name) → 3) 실패. 결과/실패 모두 캐시."""
    cache_key = f"{region}::{addr}::{name or ''}"
    if cache_key in cache:
        c = cache[cache_key]
        if c.get("lat") is not None:
            return c["lat"], c["lng"], c.get("source", "kakao")
        return None, None, None

    region_short_map = {"인천": "인천", "인천광역시": "인천", "충청남도": "충남", "충남": "충남"}
    region_short = region_short_map.get(region, region)

    # 1) 주소 API — 변형들 순차 시도
    for v in build_address_variants(addr, region):
        lat, lng = kakao_address_search(v, headers)
        if lat is not None:
            cache[cache_key] = {"lat": lat, "lng": lng, "matched_query": v, "source": "kakao_addr"}
            return lat, lng, "kakao_addr"

    # 2) 키워드(장소) API — 시설명 + 지역. 동일 시·도 결과만 채택.
    if name:
        clean_name = re.sub(r"[㈜()주식회사\s]", "", str(name))
        for q in [
            f"{region_short} {clean_name}",
            f"{region_short} {name}",
            clean_name,
        ]:
            lat, lng, matched = kakao_keyword_search(q, headers, expected_region=region_short)
            if lat is not None:
                cache[cache_key] = {"lat": lat, "lng": lng, "matched_query": q, "matched_addr": matched, "source": "kakao_kw"}
                return lat, lng, "kakao_kw"

    cache[cache_key] = {"lat": None, "lng": None, "matched_query": None}
    return None, None, None


# ─── 경기도 시설 좌표 룩업 ────────────────────────────────────
def normalize_facility_name(s: str) -> str:
    if pd.isna(s):
        return ""
    s = str(s).replace("㈜", "").replace("(주)", "").replace("주식회사", "").strip()
    return re.sub(r"\s+", "", s)


def build_gyeonggi_lookup() -> pd.DataFrame:
    """경기도_폐기물처리업체현황.csv 로드 → 시설명 정규화 컬럼 추가."""
    df = pd.read_csv(GG_CSV, encoding="cp949")
    df["name_norm"] = df["사업장명"].apply(normalize_facility_name)
    # 동일 시설이 여러 처리업종으로 등록되는 경우 — 좌표는 같으므로 첫 행만 사용
    df = df.drop_duplicates(subset=["name_norm"], keep="first")
    return df[["name_norm", "사업장명", "WGS84위도", "WGS84경도", "소재지도로명주소"]]


def lookup_gyeonggi(facility_name: str, gg_df: pd.DataFrame) -> tuple[float, float] | tuple[None, None]:
    nm = normalize_facility_name(facility_name)
    if not nm:
        return None, None

    # 1차: 정확 일치
    hit = gg_df[gg_df["name_norm"] == nm]
    # 2차: 부분 일치 (양방향)
    if hit.empty:
        hit = gg_df[gg_df["name_norm"].apply(lambda x: x and (x in nm or (len(x) >= 3 and x in nm)))]
    if hit.empty and len(nm) >= 3:
        hit = gg_df[gg_df["name_norm"].str.contains(re.escape(nm), na=False)]
    if hit.empty:
        return None, None
    r = hit.iloc[0]
    if pd.isna(r["WGS84위도"]) or pd.isna(r["WGS84경도"]):
        return None, None
    return float(r["WGS84위도"]), float(r["WGS84경도"])


def fallback_city_coords(addr: str, region: str) -> tuple[float, float] | tuple[None, None]:
    """기존 시·군청 중심 좌표 매핑 (지오코딩 실패 시)."""
    if pd.isna(addr):
        return None, None
    s = str(addr).replace("충청남도", "충남").replace("인천광역시", "인천").replace("경기도", "경기")
    m = re.search(r"(경기|충남|인천)\s+([가-힣]+(?:시|군|구))", s)
    if m and m.group(2) in CITY_COORDS:
        return CITY_COORDS[m.group(2)]
    if region in ("인천", "인천광역시"):
        for dong, gu in DONG_TO_GU.items():
            if dong in s and gu in CITY_COORDS:
                return CITY_COORDS[gu]
    return None, None


# ─── 거리 계산 ──────────────────────────────────────────────
def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """위경도 두 점 간 거리(km). Haversine 공식."""
    R = 6371.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp = np.radians(lat2 - lat1)
    dl = np.radians(lng2 - lng1)
    a = np.sin(dp/2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl/2) ** 2
    return float(2 * R * np.arcsin(np.sqrt(a)))


# ─── 메인 ──────────────────────────────────────────────────
def main() -> None:
    inc_path = SRC_DIR / "regional_incinerator_candidates_combined.csv"
    gu_path  = SRC_DIR / "서울구청_주소_위경도추가.csv"

    inc = pd.read_csv(inc_path, encoding="utf-8-sig")
    gu  = pd.read_csv(gu_path,  encoding="utf-8-sig")
    print(f"[로드] 시설 후보 {len(inc)}개, 자치구 {len(gu)}개")

    gg_lookup = build_gyeonggi_lookup()
    print(f"[로드] 경기도 폐기물처리업체 {len(gg_lookup)}개 (시설명 정규화 후 중복 제거)")

    cache = load_geocode_cache()
    print(f"[로드] 지오코딩 캐시 {len(cache)}건")
    headers = {"Authorization": f"KakaoAK {get_kakao_key()}"}

    # ─── 좌표 부여 ─────────────────────────────────────────
    lats: list[float | None] = []
    lngs: list[float | None] = []
    sources: list[str] = []
    summary: dict[str, int] = {}

    for _, r in inc.iterrows():
        region, name, addr = r["지역"], r["시설명"], r["주소"]
        lat = lng = None
        src = "fail"

        if region == "경기도":
            lat, lng = lookup_gyeonggi(name, gg_lookup)
            if lat is not None:
                src = "gyeonggi_csv"

        if lat is None and region in ("인천", "충청남도"):
            lat, lng, kakao_src = geocode_kakao(addr, region, headers, cache, name=name)
            if lat is not None:
                src = kakao_src or "kakao"

        if lat is None:
            lat, lng = fallback_city_coords(addr, region)
            if lat is not None:
                src = "city_fallback"

        lats.append(lat)
        lngs.append(lng)
        sources.append(src)
        summary[src] = summary.get(src, 0) + 1

    inc["lat"] = lats
    inc["lng"] = lngs
    inc["geo_source"] = sources

    save_geocode_cache(cache)
    print(f"[좌표] 매칭 결과: {summary}")
    n_geo = inc[["lat", "lng"]].notna().all(axis=1).sum()
    print(f"[좌표] 성공 {n_geo}/{len(inc)}개 (실패는 도서지역 등 — 다음 필터에서 제외)")

    # ─── 용량 정제 ────────────────────────────────────────
    # ※ 결측 cap은 의도적으로 null로 보존 — 브라우저(enrichFacilities)에서 결정론적 랜덤(20-80톤) 부여
    inc["cap"] = pd.to_numeric(inc["시설용량"], errors="coerce").round(1)
    inc["cap_estimated"] = inc["시설용량"].isna()
    n_missing = int(inc["cap_estimated"].sum())
    print(f"[용량] 결측 {n_missing}건 — 브라우저에서 시설명 시드 기반 랜덤 보정 예정")

    # ─── 필터링 ───────────────────────────────────────────
    f = inc[inc["lat"].notna()].copy()
    print(f"[필터1] 좌표 있는 시설: {len(f)}개")

    # cap이 null이면 통과 (랜덤 보정 대상), 아니면 5톤 이상만 통과
    f = f[f["cap"].isna() | (f["cap"] >= 5.0)].copy()
    print(f"[필터2] 용량 미상 또는 ≥5톤/일: {len(f)}개")

    EXCLUDE_KW = ["병원", "건축전용"]
    def is_relevant(s):
        if pd.isna(s): return True
        return not any(kw in str(s) for kw in EXCLUDE_KW)
    f = f[f["처리대상폐기물"].apply(is_relevant)].copy()
    print(f"[필터3] 처리대상 적합: {len(f)}개")

    # ─── 표시값 계산 ──────────────────────────────────────
    # ※ cap·remain·unitCost·co2는 브라우저(recomputeForGu+enrichFacilities)에서
    #   자치구별 도로거리·결정론적 랜덤으로 재계산되므로 여기서는 placeholder만.
    seoul_center_lat = gu["위도"].mean()
    seoul_center_lng = gu["경도"].mean()
    f["dist_seoul"] = f.apply(
        lambda r: round(haversine(seoul_center_lat, seoul_center_lng, r["lat"], r["lng"]), 1),
        axis=1,
    )

    REGION_FLAG = {"경기도": "g", "인천": "y", "충청남도": "r"}
    f["flag"] = f["지역"].map(REGION_FLAG)
    f["region_short"] = f["지역"].map({"경기도": "경기", "인천": "인천", "충청남도": "충남"})

    # remain·unitCost·co2 placeholder (cap이 null인 행은 NaN → JS에서 enrichFacilities가 채움)
    f["remain"] = (f["cap"] * 0.25).round(1)
    REGION_COST_MULT = {"경기도": 1.00, "인천": 1.05, "충청남도": 1.20}
    base_cost = 150_000
    f["unitCost"] = f.apply(
        lambda r: int(round(
            (base_cost + r["dist_seoul"] * 500) * REGION_COST_MULT[r["지역"]] / 1000
        ) * 1000),
        axis=1,
    )
    # CO₂ placeholder — JS의 calcCO2가 시뮬레이터 실행 시 덮어씀
    f["co2"] = (f["dist_seoul"] * 0.013).round(2)

    f["name"] = f.apply(
        lambda r: f"{r['region_short']} {r['시설명'].strip()}".replace("㈜", "").replace("(주)", "").strip(),
        axis=1,
    )

    # 좌표 정밀도 다듬기 (소수 6자리)
    f["lat"] = f["lat"].astype(float).round(6)
    f["lng"] = f["lng"].astype(float).round(6)

    # ─── 출력 데이터 정리 ────────────────────────────────
    out_cols = ["name", "region_short", "flag", "cap", "remain",
                "unitCost", "co2", "lat", "lng", "주소", "처리대상폐기물", "geo_source"]
    facilities = f[out_cols].rename(columns={
        "region_short": "region",
        "주소": "address",
        "처리대상폐기물": "wasteType",
        "geo_source": "geoSource",
    })
    facilities = facilities.sort_values(by=["flag", "cap"], ascending=[True, False]).reset_index(drop=True)

    print(f"\n[최종] 시설 {len(facilities)}개")
    print(facilities[["name", "region", "cap", "remain", "unitCost", "co2", "geoSource"]].to_string())

    # ─── JS 파일 출력 ────────────────────────────────────
    DASH_DIR.mkdir(parents=True, exist_ok=True)

    fac_records = facilities.to_dict(orient="records")
    fac_records = [
        {k: (None if (isinstance(v, float) and np.isnan(v)) else v) for k, v in rec.items()}
        for rec in fac_records
    ]

    gu_records = []
    for _, r in gu.iterrows():
        if pd.isna(r["위도"]) or pd.isna(r["경도"]): continue
        gu_records.append({
            "name": str(r["자치구명"]),
            "lat":  round(float(r["위도"]),  6),
            "lng":  round(float(r["경도"]), 6),
        })

    js_lines = [
        "/* Auto-generated by scripts/preprocess_facilities.py */",
        "/* Source: regional_incinerator_candidates_combined.csv + 경기도_폐기물처리업체현황.csv (경기 좌표) + Kakao geocoding (인천/충남) */",
        "",
        f"/* {len(facilities)}개 민간 소각장 후보 (실데이터 기반, 단가·잔여용량·CO₂는 추정) */",
        "const PRIVATE_FACILITIES = " + json.dumps(fac_records, ensure_ascii=False, indent=2) + ";",
        "",
        f"/* {len(gu_records)}개 서울 자치구 좌표 (구청 위치 기준) */",
        "const SEOUL_GU_COORDS = " + json.dumps(gu_records, ensure_ascii=False, indent=2) + ";",
        "",
        "if (typeof window !== 'undefined') {",
        "  window.PRIVATE_FACILITIES = PRIVATE_FACILITIES;",
        "  window.SEOUL_GU_COORDS  = SEOUL_GU_COORDS;",
        "}",
        "",
    ]

    OUT_JS.write_text("\n".join(js_lines), encoding="utf-8")
    print(f"\n저장: {OUT_JS} ({OUT_JS.stat().st_size:,} bytes)")

    print("\n" + "="*60)
    print("최종 시설 분포 (좌표 출처별)")
    print("="*60)
    print(facilities.groupby(["region", "geoSource"]).size().to_string())
    print()
    print(facilities.groupby("region").agg(
        시설수=("name", "count"),
        평균용량=("cap", "mean"),
        평균단가=("unitCost", "mean"),
        평균CO2=("co2", "mean"),
    ).round(1).to_string())


if __name__ == "__main__":
    main()
