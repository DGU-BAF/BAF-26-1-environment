# 26-1 환경 프로젝트

## 프로젝트 소개
서울시는 수도권 매립지 반입 제한과 공공 소각시설 부재로 인해 생활폐기물을 수백 킬로미터 떨어진 지방 민간 소각장에 위탁 처리하고 있다. 이는 발생지처리원칙에 위배될 뿐만 아니라, 장거리 운송에 따른 탄소 배출 증가와 비용 낭비 문제를 수반한다.

본 프로젝트는 이러한 서울시 생활폐기물 처리 위기를 데이터 기반으로 분석하고, 두 가지 대시보드를 구현하는 것을 목표로 한다.

- 서울시 쓰레기 발생 현황 대시보드 — 자치구별 폐기물 발생량 및 처리 방식을 시각화하여 현황을 한눈에 파악
- 소각장 최적 매칭 대시보드 — 운송 거리·비용·탄소 배출을 고려한 소각장 최적 배분 방안을 제시



## Git 워크플로우

#### 처음 세팅 (클론 → 파일 옮기기 → 브랜치 생성 → 푸시)

```bash
# 1) 레포 클론
git clone https://github.com/DGU-BAF/BAF-26-1-environment.git
cd BAF-26-1-environment

# 2) 본인이 로컬에서 작업한 데이터 & 코드를 폴더 구조에 맞게 옮기기
#    - 데이터 파일 → data/
#    - 노트북·분석 코드 → src/
#    - 결과물(그래프, CSV 등) → outputs/
#    - 문서(기획안, 회의록 등) → docs/

# 3) 본인 브랜치 생성 & 전환
git checkout -b feature/본인이름

# 4) 변경사항 스테이징 → 커밋 → 푸시
git add .
git commit -m "본인이름: 작업 내용 요약"
git push -u origin feature/본인이름
```

#### 이후 작업물 올리기 (로컬 최신화 → 작업 → 푸시)

```bash
# 1) (작업 시작 전!!) main 브랜치 최신화
git checkout main
git pull origin main

# 2) 본인 브랜치로 전환 후 main 반영
git checkout feature/본인이름
git merge main

# 3) (작업 후!!!) 커밋 & 푸시
git add .
git commit -m "본인이름: 작업 내용 요약"
git push origin feature/본인이름
```

#### ⚠️ 주의사항: 상대 경로 사용

데이터를 불러오거나 결과를 저장할 때 **반드시 상대 경로**를 사용해야 팀원 모두의 환경에서 동일하게 동작합니다.

```python
# ✅ 올바른 예시 (상대 경로)
df = pd.read_csv("../data/waste_data.csv")
df.to_csv("../outputs/result.csv", index=False)
plt.savefig("../outputs/chart.png")

# ❌ 잘못된 예시 (절대 경로 — 본인 PC에서만 동작)
df = pd.read_csv("C:/Users/본인이름/Desktop/waste_data.csv")
```

> 노트북(`.ipynb`)이나 스크립트의 위치가 `src/` 안이라면 `../data/`, `../outputs/` 처럼 한 단계 상위로 올라가서 접근합니다.

---


## 🖥️ 최종 대시보드 보는 법

> **별도 설치 없이 브라우저만 있으면 됩니다.**

### 방법 1 — 최소 파일만 다운로드 (권장)

대시보드 실행에 필요한 파일은 `apps/dashboard/` 폴더 전체입니다.

```
apps/dashboard/
├── 통합대시보드.html   ← 이 파일을 열면 됩니다
├── ch1/               (ch1.html, data.js)
├── ch2/               (ch2.html, data2_1.js, data2_2.js, data2_3.js, data_finance_burden2023.js)
├── ch3/               (ch3.html, data.js, facilities.js, distance_matrix.js, data_finance_burden2023.js)
└── icons/
```

**다운로드 방법:**
1. 이 레포 우측 상단 **`<> Code` → `Download ZIP`** 클릭
2. 압축 해제 후 `apps/dashboard/` 폴더만 꺼내기
3. `통합대시보드.html`을 더블클릭하여 브라우저로 열기

> ⚠️ 반드시 **폴더 구조를 유지한 채** 열어야 합니다.  
> `통합대시보드.html` 파일만 따로 빼면 ch1~ch3 데이터를 불러오지 못합니다.

### 방법 2 — 레포 전체 클론 후 실행

```bash
git clone https://github.com/DGU-BAF/BAF-26-1-environment.git
cd BAF-26-1-environment/apps/dashboard
# 통합대시보드.html 을 브라우저로 열기
```

---

## 실행 방법

### 운영진용 (클론 → 실행)

```bash
# 1) 레포 클론
git clone https://github.com/DGU-BAF/BAF-26-1-environment.git
cd BAF-26-1-environment

# 2) 필요한 패키지 설치(추후 대시보드 실행 시 필요)
pip install -r requirements.txt

# 3) 대시보드 실행
#    apps/dashboard/통합대시보드.html 을 브라우저로 열기
```


## 폴더 구조

```
BAF-26-1-environment/
├── README.md
├── apps/
│   └── dashboard/          # 최종 통합 대시보드 (← 여기만 받으면 실행 가능)
│       ├── 통합대시보드.html
│       ├── ch1/            # Ch1. 현황 진단
│       ├── ch2/            # Ch2. 원인 분석
│       ├── ch3/            # Ch3. 처방 (민간 소각장 매칭 시뮬레이터 포함)
│       └── icons/
├── data/
│   ├── raw/                # 원본 수집 데이터
│   ├── processed/          # 전처리 완료 데이터
│   └── final/              # 최종 통합 데이터셋
├── src/                    # EDA 노트북 (.ipynb)
├── outputs/                # 분석 산출물 (CSV, 리포트)
├── scripts/                # 데이터 전처리·대시보드 빌드 Python 스크립트
├── docs/
│   └── screenshots/        # 대시보드 스크린샷
└── infra/                  # 배포·인프라 설정
```

## 팀원
| 이름 |
|------|
|  김규빈    |
|  박서연    |
|  유민서    |
