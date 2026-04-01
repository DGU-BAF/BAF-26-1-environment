# 26-1 환경 프로젝트

## 프로젝트 소개
서울시는 수도권 매립지 반입 제한과 공공 소각시설 부재로 인해 생활폐기물을 수백 킬로미터 떨어진 지방 민간 소각장에 위탁 처리하고 있다. 이는 발생지처리원칙에 위배될 뿐만 아니라, 장거리 운송에 따른 탄소 배출 증가와 비용 낭비 문제를 수반한다.

본 프로젝트는 이러한 서울시 생활폐기물 처리 위기를 데이터 기반으로 분석하고, 두 가지 대시보드를 구현하는 것을 목표로 한다.

- 서울시 쓰레기 발생 현황 대시보드 — 자치구별 폐기물 발생량 및 처리 방식을 시각화하여 현황을 한눈에 파악
- 소각장 최적 매칭 대시보드 — 운송 거리·비용·탄소 배출을 고려한 소각장 최적 배분 방안을 제시

## 실행 방법

### 1. 팀원용

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
# 1) main 브랜치 최신화
git checkout main
git pull origin main

# 2) 본인 브랜치로 전환 후 main 반영
git checkout feature/본인이름
git merge main

# 3) 작업 후 커밋 & 푸시
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

### 2. 임원진용 (클론 → 실행)

```bash
# 1) 레포 클론
git clone https://github.com/DGU-BAF/BAF-26-1-environment.git
cd BAF-26-1-environment

# 2) 필요한 패키지 설치
pip install -r requirements.txt

# 3) 대시보드 실행
#    (구체적인 실행 명령어는 개발 완료 후 업데이트 예정)
```


## 폴더 구조

```
26-1-env-project/
├── README.md          # 프로젝트 소개, 실행 방법, 폴더 구조 설명
├── docs/              # 기획안, 회의록, 설계 문서, 발표 자료
├── data/              # 원본 데이터, 전처리 데이터, 외부 수집 데이터
├── src/               # EDA 노트북, 전처리 코드, 분석/모델링 코드
├── outputs/           # 그래프, 결과 CSV, 모델 산출물, 리포트 결과물
├── apps/              # 선택: 프론트엔드, 백엔드, API, 대시보드 코드
├── infra/             # 선택: Docker, 배포, CI/CD, 클라우드 설정 파일
├── .github/           # 선택: GitHub Actions, 이슈/PR 템플릿
└── scripts/           # 선택: 실행, 자동화, 데이터 수집/전처리 스크립트
```

## 팀원
| 이름 |
|------|
|  김규빈    |
|  박서연    |
|  유민서    |
