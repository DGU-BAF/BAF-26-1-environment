/* ================================================================
   data_finance.js — 서울시 쓰레기 재정 데이터
   출처: 서울특별시 열린데이터광장 (2024년 기준)
   이 파일만 교체하면 대시보드 수치가 자동 갱신됩니다.
   ================================================================ */

const FINANCE = {

  /* 자치구 목록 (순서 고정) */
  gu: ['종로구','중구','용산구','성동구','광진구','동대문구','중랑구','성북구',
       '강북구','도봉구','노원구','은평구','서대문구','마포구','양천구','강서구',
       '구로구','금천구','영등포구','동작구','관악구','서초구','강남구','송파구','강동구'],

  /* 클러스터 (cluster_result.csv 기준)
     0=주거형  1=상업형  2=유동집중형  3=혼합형 */
  cluster: {
    종로구:1, 중구:1, 용산구:1, 성동구:3, 광진구:2,
    동대문구:2, 중랑구:2, 성북구:0, 강북구:2, 도봉구:0,
    노원구:0, 은평구:0, 서대문구:0, 마포구:3, 양천구:0,
    강서구:3, 구로구:3, 금천구:3, 영등포구:1, 동작구:0,
    관악구:0, 서초구:1, 강남구:1, 송파구:3, 강동구:2
  },

  /* 청소예산 재정자립도 (소수, 예: 0.41 = 41%)
     출처: 서울시_청소예산_재정자립도.xlsx */
  fiscalIndependence: {
    종로구:0.4096, 중구:0.2867, 용산구:0.3987, 성동구:0.4431, 광진구:0.2955,
    동대문구:0.2335, 중랑구:0.4123, 성북구:0.3861, 강북구:0.3630, 도봉구:0.2283,
    노원구:0.2438, 은평구:0.2353, 서대문구:0.2321, 마포구:0.3620, 양천구:0.3521,
    강서구:0.3618, 구로구:0.3301, 금천구:0.1750, 영등포구:0.4124, 동작구:0.2115,
    관악구:0.3869, 서초구:0.3474, 강남구:0.3956, 송파구:0.3580, 강동구:0.4881
  },

  /* 전체 주민부담률 (소수)
     출처: 서울시_주민부담률.xlsx */
  burdenRateTotal: {
    종로구:0.2885, 중구:0.2449, 용산구:0.3631, 성동구:0.4437, 광진구:0.2520,
    동대문구:0.3109, 중랑구:0.3565, 성북구:0.3597, 강북구:0.3232, 도봉구:0.2082,
    노원구:0.2302, 은평구:0.2102, 서대문구:0.2046, 마포구:0.3283, 양천구:0.3113,
    강서구:0.3284, 구로구:0.2992, 금천구:0.1528, 영등포구:0.3770, 동작구:0.1795,
    관악구:0.3462, 서초구:0.3157, 강남구:0.3538, 송파구:0.3045, 강동구:0.4490
  },

  /* 생활폐기물(일반쓰레기) 주민부담률
     출처: 서울시_생활폐기물_주민부담률.xlsx */
  burdenRateGeneral: {
    종로구:0.3537, 중구:0.2838, 용산구:0.2352, 성동구:0.4646, 광진구:0.4976,
    동대문구:0.3814, 중랑구:0.3830, 성북구:0.4937, 강북구:0.3708, 도봉구:0.1931,
    노원구:0.3789, 은평구:0.2104, 서대문구:0.2109, 마포구:0.5077, 양천구:0.3924,
    강서구:0.4557, 구로구:0.3399, 금천구:0.3202, 영등포구:0.3878, 동작구:0.3132,
    관악구:0.4083, 서초구:0.4554, 강남구:0.4608, 송파구:0.3855, 강동구:0.3798
  },

  /* 음식물류 주민부담률
     출처: 서울시_음식물류폐기물_주민부담률.xlsx */
  burdenRateFood: {
    종로구:0.4425, 중구:0.3669, 용산구:0.2935, 성동구:0.4845, 광진구:0.2729,
    동대문구:0.3026, 중랑구:0.2561, 성북구:0.4303, 강북구:0.3963, 도봉구:0.2905,
    노원구:0.4106, 은평구:0.3124, 서대문구:0.3868, 마포구:0.5492, 양천구:0.3915,
    강서구:0.4161, 구로구:0.2468, 금천구:0.2718, 영등포구:0.3484, 동작구:0.2908,
    관악구:0.3215, 서초구:0.3776, 강남구:0.3202, 송파구:0.3647, 강동구:0.6615
  },

  /* 청소예산 총수입 (백만원)
     출처: 서울시_청소예산_재정자립도.xlsx */
  incomeTotal: {
    종로구:8790, 중구:9014, 용산구:11114, 성동구:10962, 광진구:8239,
    동대문구:9663, 중랑구:10758, 성북구:13679, 강북구:7033, 도봉구:6836,
    노원구:10529, 은평구:10368, 서대문구:8103, 마포구:12201, 양천구:10221,
    강서구:14442, 구로구:12577, 금천구:6062, 영등포구:11850, 동작구:7196,
    관악구:12834, 서초구:15419, 강남구:25063, 송파구:15225, 강동구:11991
  },

  /* 청소예산 총지출 (백만원)
     출처: 서울시_청소예산_재정자립도.xlsx */
  expenseTotal: {
    종로구:21459, 중구:31443, 용산구:27874, 성동구:24741, 광진구:27879,
    동대문구:41391, 중랑구:26091, 성북구:35427, 강북구:19376, 도봉구:29937,
    노원구:43186, 은평구:44057, 서대문구:34914, 마포구:33705, 양천구:29025,
    강서구:39918, 구로구:38096, 금천구:34641, 영등포구:28731, 동작구:34030,
    관악구:33171, 서초구:44378, 강남구:63359, 송파구:42531, 강동구:24567
  },

  /* 종량제 수입 — 전체 기준 (백만원)
     출처: 서울시_주민부담률.xlsx */
  jongrangjeiIncome: {
    종로구:7309, 중구:7697, 용산구:10106, 성동구:10085, 광진구:6471,
    동대문구:8392, 중랑구:9214, 성북구:12736, 강북구:6239, 도봉구:6198,
    노원구:9926, 은평구:9256, 서대문구:7119, 마포구:11046, 양천구:9028,
    강서구:13096, 구로구:11390, 금천구:5286, 영등포구:10709, 동작구:6084,
    관악구:11466, 서초구:14004, 강남구:22382, 송파구:12984, 강동구:11016
  },

  /* 수집운반처리비 합계 (백만원)
     출처: 서울시_주민부담률.xlsx */
  collectionCost: {
    종로구:24538, 중구:30670, 용산구:26865, 성동구:21990, 광진구:24649,
    동대문구:26035, 중랑구:24420, 성북구:34516, 강북구:18586, 도봉구:29218,
    노원구:42583, 은평구:43141, 서대문구:34066, 마포구:32646, 양천구:27849,
    강서구:38559, 구로구:37255, 금천구:33875, 영등포구:27435, 동작구:32855,
    관악구:31997, 서초구:43312, 강남구:61234, 송파구:40629, 강동구:23885
  },

  /* 일반 종량제봉투 가정용 판매금액 (백만원)
     출처: 서울시_일반종량제봉투_판매현황.xlsx */
  bagSalesGeneral: {
    종로구:4594, 중구:4596, 용산구:3915, 성동구:3556, 광진구:3047,
    동대문구:4024, 중랑구:3775, 성북구:3761, 강북구:2751, 도봉구:1938,
    노원구:4595, 은평구:4504, 서대문구:3613, 마포구:6647, 양천구:3993,
    강서구:6042, 구로구:4833, 금천구:3480, 영등포구:5153, 동작구:3588,
    관악구:5121, 서초구:6906, 강남구:10218, 송파구:7141, 강동구:3898
  },

  /* 음식물 종량제봉투 판매금액 (백만원) — 0은 RFID 방식 사용 구
     출처: 서울시_음식물종량제봉투_판매현황.xlsx */
  bagSalesFood: {
    종로구:644, 중구:397, 용산구:650, 성동구:634, 광진구:1403,
    동대문구:1133, 중랑구:1315, 성북구:1041, 강북구:989, 도봉구:0,
    노원구:0, 은평구:1672, 서대문구:1039, 마포구:2195, 양천구:1649,
    강서구:2012, 구로구:2007, 금천구:990, 영등포구:810, 동작구:1269,
    관악구:1990, 서초구:1376, 강남구:3140, 송파구:355, 강동구:1392
  },

  /* 무단투기 과태료 부과건수 (건)
     출처: 서울시_불법행위단속및_신고현황.xlsx */
  fineCount: {
    종로구:18233, 중구:8215, 용산구:312, 성동구:2330, 광진구:72,
    동대문구:6364, 중랑구:657, 성북구:384, 강북구:1246, 도봉구:1419,
    노원구:2128, 은평구:3348, 서대문구:3918, 마포구:1218, 양천구:445,
    강서구:0, 구로구:1486, 금천구:222, 영등포구:1288, 동작구:1232,
    관악구:3733, 서초구:8611, 강남구:13505, 송파구:4198, 강동구:2528
  },

  /* 무단투기 과태료 부과금액 (천원)
     출처: 서울시_불법행위단속및_신고현황.xlsx */
  fineAmount: {
    종로구:684795, 중구:394774, 용산구:26225, 성동구:115500, 광진구:2990,
    동대문구:342880, 중랑구:51421, 성북구:27402, 강북구:31995, 도봉구:77360,
    노원구:85155, 은평구:211851, 서대문구:254565, 마포구:57795, 양천구:38104,
    강서구:0, 구로구:119740, 금천구:9965, 영등포구:67575, 동작구:105385,
    관악구:329809, 서초구:395969, 강남구:757735, 송파구:173021, 강동구:101640
  },

  /* 일반 종량제봉투 가정용 기준 자치구별 가중평균 봉투단가
     계산: 표준 용량(1L~75L) 판매금액 합계 ÷ 표준 용량 판매량 합계
     단위: 원/매, 판매량: 천매, 판매금액: 백만원
     출처: 서울시_일반종량제봉투_판매현황.xlsx */
  bagPriceGeneral: {"종로구":{"weightedAvg":939.7,"dominantVolume":"75L","dominantPrice":1880.0,"dominantQtyThousand":1430.0,"standardQtyThousand":4889.0,"standardAmountMillion":4594.0},"중구":{"weightedAvg":1194.1,"dominantVolume":"75L","dominantPrice":1880.0,"dominantQtyThousand":1665.0,"standardQtyThousand":3849.0,"standardAmountMillion":4596.18},"용산구":{"weightedAvg":877.1,"dominantVolume":"20L","dominantPrice":490.0,"dominantQtyThousand":1145.0,"standardQtyThousand":4330.0,"standardAmountMillion":3798.0},"성동구":{"weightedAvg":331.1,"dominantVolume":"10L","dominantPrice":250.0,"dominantQtyThousand":1954.0,"standardQtyThousand":3266.0,"standardAmountMillion":1081.45},"광진구":{"weightedAvg":208.3,"dominantVolume":"10L","dominantPrice":250.0,"dominantQtyThousand":2413.0,"standardQtyThousand":4762.0,"standardAmountMillion":992.0},"동대문구":{"weightedAvg":654.3,"dominantVolume":"10L","dominantPrice":250.0,"dominantQtyThousand":1962.0,"standardQtyThousand":6150.0,"standardAmountMillion":4024.0},"중랑구":{"weightedAvg":618.5,"dominantVolume":"10L","dominantPrice":250.0,"dominantQtyThousand":2253.0,"standardQtyThousand":6103.0,"standardAmountMillion":3775.0},"성북구":{"weightedAvg":326.1,"dominantVolume":"10L","dominantPrice":250.0,"dominantQtyThousand":2215.0,"standardQtyThousand":4802.0,"standardAmountMillion":1566.0},"강북구":{"weightedAvg":581.4,"dominantVolume":"10L","dominantPrice":250.0,"dominantQtyThousand":2229.0,"standardQtyThousand":4732.0,"standardAmountMillion":2751.0},"도봉구":{"weightedAvg":611.5,"dominantVolume":"10L","dominantPrice":250.0,"dominantQtyThousand":1099.0,"standardQtyThousand":3169.0,"standardAmountMillion":1938.0},"노원구":{"weightedAvg":939.3,"dominantVolume":"75L","dominantPrice":1880.0,"dominantQtyThousand":1430.0,"standardQtyThousand":4892.0,"standardAmountMillion":4595.0},"은평구":{"weightedAvg":577.2,"dominantVolume":"10L","dominantPrice":250.0,"dominantQtyThousand":2531.0,"standardQtyThousand":6828.0,"standardAmountMillion":3941.45},"서대문구":{"weightedAvg":618.8,"dominantVolume":"10L","dominantPrice":250.0,"dominantQtyThousand":2023.0,"standardQtyThousand":5839.0,"standardAmountMillion":3613.0},"마포구":{"weightedAvg":708.4,"dominantVolume":"10L","dominantPrice":250.0,"dominantQtyThousand":2680.0,"standardQtyThousand":9383.0,"standardAmountMillion":6647.0},"양천구":{"weightedAvg":533.0,"dominantVolume":"10L","dominantPrice":250.0,"dominantQtyThousand":3051.0,"standardQtyThousand":7491.0,"standardAmountMillion":3993.0},"강서구":{"weightedAvg":609.6,"dominantVolume":"10L","dominantPrice":250.0,"dominantQtyThousand":3288.0,"standardQtyThousand":9912.0,"standardAmountMillion":6042.0},"구로구":{"weightedAvg":651.8,"dominantVolume":"10L","dominantPrice":250.0,"dominantQtyThousand":2799.0,"standardQtyThousand":7415.0,"standardAmountMillion":4833.0},"금천구":{"weightedAvg":723.5,"dominantVolume":"10L","dominantPrice":250.0,"dominantQtyThousand":1507.0,"standardQtyThousand":4811.0,"standardAmountMillion":3480.81},"영등포구":{"weightedAvg":703.3,"dominantVolume":"10L","dominantPrice":250.0,"dominantQtyThousand":2815.0,"standardQtyThousand":7327.0,"standardAmountMillion":5153.44},"동작구":{"weightedAvg":531.0,"dominantVolume":"10L","dominantPrice":250.0,"dominantQtyThousand":2720.0,"standardQtyThousand":6757.0,"standardAmountMillion":3588.0},"관악구":{"weightedAvg":540.4,"dominantVolume":"10L","dominantPrice":250.0,"dominantQtyThousand":4089.0,"standardQtyThousand":9476.0,"standardAmountMillion":5121.0},"서초구":{"weightedAvg":340.2,"dominantVolume":"10L","dominantPrice":250.0,"dominantQtyThousand":2531.0,"standardQtyThousand":5314.0,"standardAmountMillion":1808.0},"강남구":{"weightedAvg":335.3,"dominantVolume":"10L","dominantPrice":250.0,"dominantQtyThousand":2407.0,"standardQtyThousand":5804.0,"standardAmountMillion":1946.0},"송파구":{"weightedAvg":710.1,"dominantVolume":"10L","dominantPrice":250.0,"dominantQtyThousand":3014.0,"standardQtyThousand":10057.0,"standardAmountMillion":7141.0},"강동구":{"weightedAvg":592.0,"dominantVolume":"10L","dominantPrice":250.0,"dominantQtyThousand":2529.0,"standardQtyThousand":6585.0,"standardAmountMillion":3898.0}},

  /* 가격조정률 시뮬레이션 설정
     priceElasticityByCluster: 가격 1% 조정 시 배출량 변화율
     국내 연구의 낮은 가격탄력도(약 -0.05~-0.146)를 기준으로,
     주거형은 직접 부담·가정 배출 비중이 커 상대적으로 민감하게,
     상업형은 비용 전가·업무/유동 배출 비중이 커 둔감하게 보정 */
  priceElasticityByCluster: {
    0: -0.06, /* 상업형: 가격 둔감 */
    1: -0.14, /* 주거형: 상대적으로 가격 민감 */
    2: -0.10, /* 유동집중형: 중간 */
    3: -0.08  /* 혼합형: 중간-하 */
  },
  variableCostShare: 0.35, /* 처리비 중 배출량 변화에 연동된다고 보는 변동비 비중 가정 */

  /* 기존 코드 호환용: priceElasticityByCluster와 동일 */
  bagElasticity: {
    0: -0.06,
    1: -0.14,
    2: -0.10,
    3: -0.08
  },

  /* 클러스터 표시명 */
  clusterNames: ['🏠 주거형','🏢 상업형','🚶 유동집중형','🔀 혼합형'],
  clusterColors: ['#2563eb','#dc2626','#d97706','#7c3aed']
};


/* 2023 주민부담률 원인분해 결과 — 01_burden_rate_by_gu_2023.ipynb 산출물
   기준: 25개 자치구 평균, 분자=인구당 일반 종량제봉투 판매액, 분모=인구당 일반 생활폐기물 총 처리비용 */
const BURDEN_2023 = [{"gu":"강남구","cluster_type":"상업형","burden_total_pct":35.38,"burden_general_pct":46.08,"burden_food_pct":32.02,"total_pop":550282,"households":239775,"bag_rev_per_pop":19724,"gen_cost_per_pop":42809,"bag_rev_per_hh":45267,"gen_cost_per_hh":98246,"fee_rev_per_pop":10360,"food_cost_per_pop":32351,"fee_rev_per_hh":23776,"food_cost_per_hh":74245,"gen_quad":"분자↑·분모↑","food_quad":"분자↑·분모↑","rfid":false,"scenario_id":"#01"},{"gu":"강동구","cluster_type":"유동집중형","burden_total_pct":44.9,"burden_general_pct":37.98,"burden_food_pct":66.15,"total_pop":463318,"households":203734,"bag_rev_per_pop":11033,"gen_cost_per_pop":29047,"bag_rev_per_hh":25092,"gen_cost_per_hh":66057,"fee_rev_per_pop":12743,"food_cost_per_pop":19263,"fee_rev_per_hh":28979,"food_cost_per_hh":43807,"gen_quad":"분자↓·분모↓","food_quad":"분자↑·분모↓","rfid":false,"scenario_id":"#08"},{"gu":"강북구","cluster_type":"유동집중형","burden_total_pct":32.32,"burden_general_pct":37.08,"burden_food_pct":39.63,"total_pop":292977,"households":143560,"bag_rev_per_pop":10335,"gen_cost_per_pop":27876,"bag_rev_per_hh":21092,"gen_cost_per_hh":56889,"fee_rev_per_pop":6342,"food_cost_per_pop":16001,"fee_rev_per_hh":12942,"food_cost_per_hh":32655,"gen_quad":"분자↓·분모↓","food_quad":"분자↓·분모↓","rfid":false,"scenario_id":"#08"},{"gu":"강서구","cluster_type":"혼합형","burden_total_pct":32.84,"burden_general_pct":45.57,"burden_food_pct":41.61,"total_pop":568826,"households":274084,"bag_rev_per_pop":12269,"gen_cost_per_pop":26926,"bag_rev_per_hh":25463,"gen_cost_per_hh":55881,"fee_rev_per_pop":6411,"food_cost_per_pop":15409,"fee_rev_per_hh":13306,"food_cost_per_hh":31979,"gen_quad":"분자↓·분모↓","food_quad":"분자↓·분모↓","rfid":false,"scenario_id":"#12"},{"gu":"관악구","cluster_type":"주거형","burden_total_pct":34.62,"burden_general_pct":40.83,"burden_food_pct":32.15,"total_pop":497883,"households":284578,"bag_rev_per_pop":12362,"gen_cost_per_pop":30274,"bag_rev_per_hh":21629,"gen_cost_per_hh":52966,"fee_rev_per_pop":6632,"food_cost_per_pop":20631,"fee_rev_per_hh":11603,"food_cost_per_hh":36096,"gen_quad":"분자↓·분모↓","food_quad":"분자↓·분모↓","rfid":false,"scenario_id":"#16"},{"gu":"광진구","cluster_type":"유동집중형","burden_total_pct":25.2,"burden_general_pct":49.76,"burden_food_pct":27.29,"total_pop":351180,"households":170077,"bag_rev_per_pop":11322,"gen_cost_per_pop":22752,"bag_rev_per_hh":23378,"gen_cost_per_hh":46979,"fee_rev_per_pop":4753,"food_cost_per_pop":17416,"fee_rev_per_hh":9813,"food_cost_per_hh":35960,"gen_quad":"분자↓·분모↓","food_quad":"분자↓·분모↓","rfid":false,"scenario_id":"#08"},{"gu":"구로구","cluster_type":"혼합형","burden_total_pct":29.92,"burden_general_pct":33.99,"burden_food_pct":24.68,"total_pop":415651,"households":184096,"bag_rev_per_pop":15037,"gen_cost_per_pop":44237,"bag_rev_per_hh":33950,"gen_cost_per_hh":99877,"fee_rev_per_pop":5375,"food_cost_per_pop":21775,"fee_rev_per_hh":12135,"food_cost_per_hh":49165,"gen_quad":"분자↑·분모↑","food_quad":"분자↓·분모↓","rfid":false,"scenario_id":"#09"},{"gu":"금천구","cluster_type":"혼합형","burden_total_pct":15.28,"burden_general_pct":32.02,"burden_food_pct":27.18,"total_pop":241105,"households":120381,"bag_rev_per_pop":15226,"gen_cost_per_pop":47548,"bag_rev_per_hh":30495,"gen_cost_per_hh":95231,"fee_rev_per_pop":6217,"food_cost_per_pop":22878,"fee_rev_per_hh":12452,"food_cost_per_hh":45821,"gen_quad":"분자↑·분모↑","food_quad":"분자↓·분모↑","rfid":false,"scenario_id":"#09"},{"gu":"노원구","cluster_type":"주거형","burden_total_pct":23.02,"burden_general_pct":37.89,"burden_food_pct":41.06,"total_pop":502925,"households":217904,"bag_rev_per_pop":9741,"gen_cost_per_pop":25712,"bag_rev_per_hh":22482,"gen_cost_per_hh":59343,"fee_rev_per_pop":7550,"food_cost_per_pop":18388,"fee_rev_per_hh":17425,"food_cost_per_hh":42441,"gen_quad":"분자↓·분모↓","food_quad":"분자↓·분모↓","rfid":false,"scenario_id":"#16"},{"gu":"도봉구","cluster_type":"주거형","burden_total_pct":20.82,"burden_general_pct":19.31,"burden_food_pct":29.05,"total_pop":309494,"households":138261,"bag_rev_per_pop":9810,"gen_cost_per_pop":50793,"bag_rev_per_hh":21958,"gen_cost_per_hh":113698,"fee_rev_per_pop":6986,"food_cost_per_pop":24046,"fee_rev_per_hh":15637,"food_cost_per_hh":53826,"gen_quad":"분자↓·분모↑","food_quad":"분자↓·분모↑","rfid":false,"scenario_id":"#15"},{"gu":"동대문구","cluster_type":"유동집중형","burden_total_pct":31.09,"burden_general_pct":38.14,"burden_food_pct":30.26,"total_pop":359873,"households":172801,"bag_rev_per_pop":12968,"gen_cost_per_pop":34006,"bag_rev_per_hh":27008,"gen_cost_per_hh":70821,"fee_rev_per_pop":7655,"food_cost_per_pop":25301,"fee_rev_per_hh":15943,"food_cost_per_hh":52691,"gen_quad":"분자↓·분모↓","food_quad":"분자↓·분모↑","rfid":false,"scenario_id":"#08"},{"gu":"동작구","cluster_type":"주거형","burden_total_pct":17.95,"burden_general_pct":31.32,"burden_food_pct":29.08,"total_pop":389714,"households":186675,"bag_rev_per_pop":10131,"gen_cost_per_pop":32344,"bag_rev_per_hh":21149,"gen_cost_per_hh":67524,"fee_rev_per_pop":4965,"food_cost_per_pop":17071,"fee_rev_per_hh":10366,"food_cost_per_hh":35639,"gen_quad":"분자↓·분모↓","food_quad":"분자↓·분모↓","rfid":false,"scenario_id":"#16"},{"gu":"마포구","cluster_type":"혼합형","burden_total_pct":32.83,"burden_general_pct":50.77,"burden_food_pct":54.92,"total_pop":375162,"households":181090,"bag_rev_per_pop":18203,"gen_cost_per_pop":35857,"bag_rev_per_hh":37711,"gen_cost_per_hh":74284,"fee_rev_per_pop":7799,"food_cost_per_pop":14202,"fee_rev_per_hh":16158,"food_cost_per_hh":29422,"gen_quad":"분자↑·분모↓","food_quad":"분자↓·분모↓","rfid":false,"scenario_id":"#10"},{"gu":"서대문구","cluster_type":"주거형","burden_total_pct":20.46,"burden_general_pct":21.09,"burden_food_pct":38.68,"total_pop":320629,"households":146845,"bag_rev_per_pop":12220,"gen_cost_per_pop":57942,"bag_rev_per_hh":26681,"gen_cost_per_hh":126514,"fee_rev_per_pop":6968,"food_cost_per_pop":18011,"fee_rev_per_hh":15213,"food_cost_per_hh":39327,"gen_quad":"분자↓·분모↑","food_quad":"분자↓·분모↓","rfid":false,"scenario_id":"#15"},{"gu":"서초구","cluster_type":"상업형","burden_total_pct":31.57,"burden_general_pct":45.54,"burden_food_pct":37.76,"total_pop":412078,"households":169884,"bag_rev_per_pop":18528,"gen_cost_per_pop":40682,"bag_rev_per_hh":44942,"gen_cost_per_hh":98679,"fee_rev_per_pop":9508,"food_cost_per_pop":25180,"fee_rev_per_hh":23063,"food_cost_per_hh":61077,"gen_quad":"분자↑·분모↓","food_quad":"분자↑·분모↑","rfid":false,"scenario_id":"#02"},{"gu":"성동구","cluster_type":"혼합형","burden_total_pct":44.37,"burden_general_pct":46.46,"burden_food_pct":48.45,"total_pop":284766,"households":133089,"bag_rev_per_pop":17362,"gen_cost_per_pop":37371,"bag_rev_per_hh":37148,"gen_cost_per_hh":79962,"fee_rev_per_pop":10700,"food_cost_per_pop":22085,"fee_rev_per_hh":22894,"food_cost_per_hh":47254,"gen_quad":"분자↑·분모↓","food_quad":"분자↑·분모↓","rfid":false,"scenario_id":"#10"},{"gu":"성북구","cluster_type":"주거형","burden_total_pct":35.97,"burden_general_pct":49.37,"burden_food_pct":43.03,"total_pop":438168,"households":196800,"bag_rev_per_pop":11292,"gen_cost_per_pop":22873,"bag_rev_per_hh":25142,"gen_cost_per_hh":50925,"fee_rev_per_pop":7748,"food_cost_per_pop":18007,"fee_rev_per_hh":17251,"food_cost_per_hh":40091,"gen_quad":"분자↓·분모↓","food_quad":"분자↓·분모↓","rfid":false,"scenario_id":"#16"},{"gu":"송파구","cluster_type":"혼합형","burden_total_pct":30.45,"burden_general_pct":38.55,"burden_food_pct":36.47,"total_pop":660025,"households":285927,"bag_rev_per_pop":12459,"gen_cost_per_pop":32315,"bag_rev_per_hh":28759,"gen_cost_per_hh":74596,"fee_rev_per_pop":7213,"food_cost_per_pop":19777,"fee_rev_per_hh":16651,"food_cost_per_hh":45652,"gen_quad":"분자↓·분모↓","food_quad":"분자↓·분모↓","rfid":false,"scenario_id":"#12"},{"gu":"양천구","cluster_type":"주거형","burden_total_pct":31.13,"burden_general_pct":39.24,"burden_food_pct":39.15,"total_pop":439252,"households":180695,"bag_rev_per_pop":10859,"gen_cost_per_pop":27672,"bag_rev_per_hh":26398,"gen_cost_per_hh":67268,"fee_rev_per_pop":6365,"food_cost_per_pop":16257,"fee_rev_per_hh":15474,"food_cost_per_hh":39520,"gen_quad":"분자↓·분모↓","food_quad":"분자↓·분모↓","rfid":false,"scenario_id":"#16"},{"gu":"영등포구","cluster_type":"상업형","burden_total_pct":37.7,"burden_general_pct":38.78,"burden_food_pct":34.84,"total_pop":397800,"households":190737,"bag_rev_per_pop":15606,"gen_cost_per_pop":40246,"bag_rev_per_hh":32547,"gen_cost_per_hh":83938,"fee_rev_per_pop":8731,"food_cost_per_pop":25058,"fee_rev_per_hh":18208,"food_cost_per_hh":52260,"gen_quad":"분자↑·분모↓","food_quad":"분자↑·분모↑","rfid":false,"scenario_id":"#02"},{"gu":"용산구","cluster_type":"상업형","burden_total_pct":36.31,"burden_general_pct":23.52,"burden_food_pct":29.35,"total_pop":227106,"households":107825,"bag_rev_per_pop":17653,"gen_cost_per_pop":75062,"bag_rev_per_hh":37181,"gen_cost_per_hh":158099,"fee_rev_per_pop":8996,"food_cost_per_pop":30651,"fee_rev_per_hh":18947,"food_cost_per_hh":64558,"gen_quad":"분자↑·분모↑","food_quad":"분자↑·분모↑","rfid":false,"scenario_id":"#01"},{"gu":"은평구","cluster_type":"주거형","burden_total_pct":21.02,"burden_general_pct":21.04,"burden_food_pct":31.24,"total_pop":470869,"households":215721,"bag_rev_per_pop":11228,"gen_cost_per_pop":53374,"bag_rev_per_hh":24509,"gen_cost_per_hh":116502,"fee_rev_per_pop":5289,"food_cost_per_pop":16928,"fee_rev_per_hh":11545,"food_cost_per_hh":36951,"gen_quad":"분자↓·분모↑","food_quad":"분자↓·분모↓","rfid":false,"scenario_id":"#15"},{"gu":"종로구","cluster_type":"상업형","burden_total_pct":28.85,"burden_general_pct":35.37,"burden_food_pct":44.25,"total_pop":150453,"households":72067,"bag_rev_per_pop":28201,"gen_cost_per_pop":79733,"bag_rev_per_hh":58876,"gen_cost_per_hh":166456,"fee_rev_per_pop":15347,"food_cost_per_pop":34682,"fee_rev_per_hh":32040,"food_cost_per_hh":72405,"gen_quad":"분자↑·분모↑","food_quad":"분자↑·분모↑","rfid":false,"scenario_id":"#01"},{"gu":"중구","cluster_type":"상업형","burden_total_pct":24.49,"burden_general_pct":28.38,"burden_food_pct":36.69,"total_pop":131793,"households":64714,"bag_rev_per_pop":33226,"gen_cost_per_pop":117093,"bag_rev_per_hh":67667,"gen_cost_per_hh":238465,"fee_rev_per_pop":20957,"food_cost_per_pop":57112,"fee_rev_per_hh":42680,"food_cost_per_hh":116312,"gen_quad":"분자↑·분모↑","food_quad":"분자↑·분모↑","rfid":false,"scenario_id":"#01"},{"gu":"중랑구","cluster_type":"유동집중형","burden_total_pct":35.65,"burden_general_pct":38.3,"burden_food_pct":25.61,"total_pop":387470,"households":188097,"bag_rev_per_pop":11203,"gen_cost_per_pop":29251,"bag_rev_per_hh":23079,"gen_cost_per_hh":60256,"fee_rev_per_pop":5923,"food_cost_per_pop":23124,"fee_rev_per_hh":12201,"food_cost_per_hh":47635,"gen_quad":"분자↓·분모↓","food_quad":"분자↓·분모↑","rfid":false,"scenario_id":"#08"}];
window.BURDEN_2023 = BURDEN_2023;
if (typeof FINANCE !== 'undefined') FINANCE.burden2023 = BURDEN_2023;

window.FINANCE = FINANCE;
