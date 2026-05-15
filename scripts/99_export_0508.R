# ════════════════════════════════════════════════════════════════
# 99_export_actual_livingpop_v2.R
# 전처리 CSV → data2_1.js / data2_2.js / data2_3.js 생성
#
# 생성 파일
#   1) data2_1.js : GU, YEARLY, LIVING_POP, RECYCLE_INDUSTRY, CLUSTER_RESULT
#   2) data2_2.js : 자치구별 요인 분석, 생활인구 보정 1인당 지표, 특이사례
#   3) data2_3.js : 잔차 분석 + 회귀 유의변수 해석
#
# data.js는 생성하지 않음
# ════════════════════════════════════════════════════════════════

library(jsonlite)
library(dplyr)

# ════════════════════════════════════════════════════════════════
# 0. 경로 설정
# ════════════════════════════════════════════════════════════════

DATA_DIR <- "C:/Users/USER/OneDrive/바탕 화면/유영우/2026_빅콘_0507/data/preprocess"
DASH_DIR <- "C:/Users/USER/OneDrive/바탕 화면/유영우/2026_빅콘_0507/dashboard"

SEARCH_DIRS <- unique(c(
  DATA_DIR,
  DASH_DIR,
  getwd()
))

if (!dir.exists(DASH_DIR)) {
  dir.create(DASH_DIR, recursive = TRUE)
}

# ════════════════════════════════════════════════════════════════
# 1. 유틸 함수
# ════════════════════════════════════════════════════════════════

first_existing <- function(file_names, search_dirs = SEARCH_DIRS, required = TRUE) {
  candidates <- as.vector(outer(search_dirs, file_names, file.path))
  hit <- candidates[file.exists(candidates)]
  
  if (length(hit) > 0) return(hit[1])
  
  if (required) {
    stop(
      "파일을 찾지 못했습니다: ",
      paste(file_names, collapse = " / "),
      "\n검색 경로:\n",
      paste(search_dirs, collapse = "\n"),
      call. = FALSE
    )
  }
  
  return(NA_character_)
}

read_csv_safe <- function(path, required = TRUE) {
  if (is.na(path) || !file.exists(path)) {
    if (required) stop("파일 없음: ", path, call. = FALSE)
    return(NULL)
  }
  
  tryCatch(
    read.csv(
      path,
      fileEncoding = "UTF-8-BOM",
      check.names = FALSE,
      stringsAsFactors = FALSE
    ),
    error = function(e1) {
      tryCatch(
        read.csv(
          path,
          fileEncoding = "UTF-8",
          check.names = FALSE,
          stringsAsFactors = FALSE
        ),
        error = function(e2) {
          read.csv(
            path,
            fileEncoding = "CP949",
            check.names = FALSE,
            stringsAsFactors = FALSE
          )
        }
      )
    }
  )
}

first_col <- function(df, candidates, required = TRUE) {
  hit <- candidates[candidates %in% names(df)]
  if (length(hit) > 0) return(hit[1])
  
  if (required) {
    stop(
      "컬럼을 찾지 못했습니다: ",
      paste(candidates, collapse = " / "),
      call. = FALSE
    )
  }
  
  return(NA_character_)
}

num0 <- function(x) {
  y <- suppressWarnings(as.numeric(x))
  y[is.na(y)] <- 0
  y
}

num_na <- function(x) {
  suppressWarnings(as.numeric(x))
}

bool01 <- function(x) {
  y <- tolower(trimws(as.character(x)))
  as.integer(y %in% c("1", "true", "t", "yes", "y"))
}

normalize_living_pop <- function(x) {
  x_num <- num0(x)
  
  divisor <- ifelse(
    median(x_num, na.rm = TRUE) > 2000000,
    24,
    1
  )
  
  round(x_num / divisor, 0)
}

write_window_block <- function(name, obj, file, append = TRUE) {
  json <- jsonlite::toJSON(
    obj,
    auto_unbox = TRUE,
    pretty = FALSE,
    na = "null"
  )
  
  cat(
    paste0("window.", name, " = ", json, ";\n\n"),
    file = file,
    append = append
  )
}

safe_pct_label <- function(x, digits = 1) {
  x <- num_na(x)
  
  ifelse(
    is.na(x),
    NA_character_,
    ifelse(
      x > 0,
      paste0("+", round(x, digits), "%"),
      paste0(round(x, digits), "%")
    )
  )
}

sig_label_one <- function(var_name, effect, sig) {
  sig <- bool01(sig)
  effect <- num_na(effect)
  
  if (is.na(sig) || sig != 1 || is.na(effect)) {
    return(NA_character_)
  }
  
  sign <- ifelse(effect > 0, "+", "")
  paste0(var_name, " ", sign, round(effect, 1), "%")
}

make_sig_summary <- function(living_eff, living_sig,
                             elderly_eff, elderly_sig,
                             day_night_eff, day_night_sig,
                             food_eff, food_sig) {
  out <- na.omit(c(
    sig_label_one("생활인구", living_eff, living_sig),
    sig_label_one("고령비율", elderly_eff, elderly_sig),
    sig_label_one("낮/밤 인구비", day_night_eff, day_night_sig),
    sig_label_one("음식·숙박업 비중", food_eff, food_sig)
  ))
  
  if (length(out) == 0) return("유의한 추가 활동 변수 없음")
  paste(out, collapse = " · ")
}

# ════════════════════════════════════════════════════════════════
# 2. CSV 로드
# ════════════════════════════════════════════════════════════════

cat("── 1. CSV 로드 중...\n")

per_cap_path <- first_existing("per_capita.csv")
trash_pr_path <- first_existing("trash_process.csv")
food_sp_path <- first_existing("food_split.csv")
recycle_ind_path <- first_existing("recycle_industry.csv")
cluster_path <- first_existing("cluster_result.csv")
living_pop_path <- first_existing(c(
  "living_pop_merged_by_gu_year.csv",
  "living_pop_merged_by_gu_year (1).csv"
))

waste_int_path <- first_existing(
  c("waste_integrated.csv", "eda_master_v2_by_gu_year.csv"),
  required = FALSE
)

# 여기 중요:
# 2.2 / 2.3 잔차 + 회귀 유의변수는 이 파일을 우선 사용
resid_path <- first_existing(
  c(
    "resid_by_gu_2023_cluster_direct.csv",
    "resid_by_gu_2023_v2.csv",
    "resid_by_gu_2023.csv",
    "resid_by_gu.csv"
  ),
  required = FALSE
)

per_cap <- read_csv_safe(per_cap_path)
trash_pr <- read_csv_safe(trash_pr_path)
food_sp <- read_csv_safe(food_sp_path)
recycle_ind <- read_csv_safe(recycle_ind_path)
cluster_res <- read_csv_safe(cluster_path)
living_pop <- read_csv_safe(living_pop_path)
waste_int <- read_csv_safe(waste_int_path, required = FALSE)
resid_raw <- read_csv_safe(resid_path, required = FALSE)

for (nm in c("per_cap", "trash_pr", "food_sp", "recycle_ind", "cluster_res", "living_pop")) {
  obj <- get(nm)
  names(obj) <- trimws(names(obj))
  assign(nm, obj)
}

if (!is.null(waste_int)) names(waste_int) <- trimws(names(waste_int))
if (!is.null(resid_raw)) names(resid_raw) <- trimws(names(resid_raw))

cat("  per_capita      :", nrow(per_cap), "\n")
cat("  trash_process   :", nrow(trash_pr), "\n")
cat("  food_split      :", nrow(food_sp), "\n")
cat("  recycle_industry:", nrow(recycle_ind), "\n")
cat("  cluster_result  :", nrow(cluster_res), "\n")
cat("  living_pop      :", nrow(living_pop), "\n")
cat("  waste_integrated:", ifelse(is.null(waste_int), 0, nrow(waste_int)), "\n")
cat("  resid           :", ifelse(is.null(resid_raw), 0, nrow(resid_raw)), "\n")

# ════════════════════════════════════════════════════════════════
# 3. GU 배열 생성
# ════════════════════════════════════════════════════════════════

cat("\n── 2. GU 배열 생성 중...\n")

district_col <- first_col(per_cap, c("district", "gu", "자치구", "n"))

gu <- per_cap %>%
  rename(n = all_of(district_col))

# 필수 컬럼명 안전 처리
if (!"daily" %in% names(gu)) {
  stop("per_capita.csv에 daily 컬럼이 필요합니다.", call. = FALSE)
}
if (!"pop" %in% names(gu)) {
  stop("per_capita.csv에 pop 컬럼이 필요합니다.", call. = FALSE)
}
if (!"perCap" %in% names(gu)) {
  gu <- gu %>%
    mutate(perCap = round(num0(daily) * 1000 / num0(pop), 3))
}

gu <- gu %>%
  mutate(
    daily = num0(daily),
    pop = num0(pop),
    perCap = num0(perCap)
  )

# 처리현황
trash_district_col <- first_col(trash_pr, c("district", "gu", "자치구", "n"))

tp <- trash_pr %>%
  rename(n = all_of(trash_district_col)) %>%
  mutate(
    recycle = round(num0(recycle_pct) * 100, 1),
    inc = round(num0(incin_pct) * 100, 1),
    land = round(num0(landfill_pct) * 100, 1)
  ) %>%
  select(n, recycle, inc, land)

gu <- gu %>% left_join(tp, by = "n")

# 음식물 비중
if (!is.null(waste_int) && all(c("year", "district", "food_intensity") %in% names(waste_int))) {
  snapshot_year <- max(waste_int$year, na.rm = TRUE)
  
  wi_food <- waste_int %>%
    filter(year == snapshot_year) %>%
    transmute(
      n = district,
      food = round(num0(food_intensity) * 100, 1)
    )
  
  gu <- gu %>% left_join(wi_food, by = "n")
} else {
  food_district_col <- first_col(food_sp, c("district", "gu", "자치구", "n"))
  
  fs_food <- food_sp %>%
    rename(n = all_of(food_district_col)) %>%
    select(n, food_total) %>%
    mutate(food_total = num0(food_total))
  
  gu <- gu %>%
    left_join(fs_food, by = "n") %>%
    mutate(
      food = ifelse(
        !is.na(food_total) & daily > 0,
        round(food_total / daily * 100, 1),
        NA_real_
      )
    ) %>%
    select(-food_total)
}

# 음식물 가정/사업장 비중
food_district_col <- first_col(food_sp, c("district", "gu", "자치구", "n"))

fs <- food_sp %>%
  rename(n = all_of(food_district_col)) %>%
  mutate(
    homeProp = round(num0(home_prop) * 100, 1),
    bizProp = round(num0(biz_prop) * 100, 1)
  ) %>%
  select(n, homeProp, bizProp)

gu <- gu %>% left_join(fs, by = "n")

# 좌표
coords <- data.frame(
  n = c(
    "강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구", "금천구", "노원구",
    "도봉구", "동대문구", "동작구", "마포구", "서대문구", "서초구", "성동구", "성북구", "송파구",
    "양천구", "영등포구", "용산구", "은평구", "종로구", "중구", "중랑구"
  ),
  lat = c(
    37.517, 37.530, 37.640, 37.550, 37.478, 37.538, 37.495, 37.457, 37.655, 37.669,
    37.574, 37.512, 37.566, 37.579, 37.483, 37.563, 37.606, 37.515, 37.517, 37.526,
    37.532, 37.603, 37.573, 37.564, 37.606
  ),
  lng = c(
    127.047, 127.124, 127.025, 126.849, 126.952, 127.082, 126.886, 126.896, 127.056, 127.047,
    127.040, 126.940, 126.902, 126.937, 127.033, 127.037, 127.017, 127.105, 126.867, 126.896,
    126.990, 126.929, 126.979, 126.998, 127.093
  ),
  stringsAsFactors = FALSE
)

gu <- gu %>% left_join(coords, by = "n")

# 클러스터 결과
cluster_gu_col <- first_col(cluster_res, c("gu", "district", "자치구", "n"))
cluster_anchor_col <- first_col(cluster_res, c("cluster_anchor", "cluster", "anchor"))
cluster_type_col <- first_col(cluster_res, c("cluster_type", "clusterType", "type"))

cluster_use <- cluster_res %>%
  rename(n = all_of(cluster_gu_col)) %>%
  transmute(
    n,
    cluster = as.integer(num0(.data[[cluster_anchor_col]])),
    clusterType = as.character(.data[[cluster_type_col]])
  )

gu <- gu %>% left_join(cluster_use, by = "n")

# 생활인구 최신연도
lp_gu_col <- first_col(living_pop, c("gu", "district", "자치구", "n"))

lp <- living_pop %>%
  rename(n = all_of(lp_gu_col)) %>%
  mutate(
    n = trimws(n),
    year = as.integer(year)
  )

living_snapshot_year <- max(lp$year, na.rm = TRUE)

lp_snapshot <- lp %>%
  filter(year == living_snapshot_year) %>%
  transmute(
    n,
    livingPop = normalize_living_pop(living_pop_daily_avg),
    foreignerLivingPop = normalize_living_pop(foreigner_lp_daily_avg),
    daytimePop = normalize_living_pop(daytime_avg),
    nighttimePop = normalize_living_pop(nighttime_avg),
    dayNightRatio = round(num0(day_night_ratio), 3)
  )

gu <- gu %>% left_join(lp_snapshot, by = "n")

gu_out <- gu %>%
  select(
    n, lat, lng,
    daily, pop, perCap,
    recycle, food, inc, land,
    homeProp, bizProp,
    livingPop, foreignerLivingPop, daytimePop, nighttimePop, dayNightRatio,
    cluster, clusterType
  )

gu_out[is.na(gu_out)] <- 0

cat("  GU 자치구 수:", nrow(gu_out), "\n")
cat("  생활인구 스냅샷 연도:", living_snapshot_year, "\n")

# ════════════════════════════════════════════════════════════════
# 4. LIVING_POP 객체
# ════════════════════════════════════════════════════════════════

cat("\n── 3. LIVING_POP 객체 생성 중...\n")

lp_clean <- lp %>%
  transmute(
    year = as.integer(year),
    n,
    livingPop = normalize_living_pop(living_pop_daily_avg),
    foreignerLivingPop = normalize_living_pop(foreigner_lp_daily_avg),
    daytimePop = normalize_living_pop(daytime_avg),
    nighttimePop = normalize_living_pop(nighttime_avg),
    dayNightRatio = round(num0(day_night_ratio), 3)
  )

living_years <- sort(unique(lp_clean$year))

living_list <- setNames(
  lapply(living_years, function(yy) {
    yy_df <- lp_clean %>% filter(year == yy)
    
    setNames(
      lapply(seq_len(nrow(yy_df)), function(i) {
        list(
          livingPop = yy_df$livingPop[i],
          foreignerLivingPop = yy_df$foreignerLivingPop[i],
          daytimePop = yy_df$daytimePop[i],
          nighttimePop = yy_df$nighttimePop[i],
          dayNightRatio = yy_df$dayNightRatio[i]
        )
      }),
      yy_df$n
    )
  }),
  as.character(living_years)
)

cat("  생활인구 연도:", paste(living_years, collapse = ", "), "\n")

# ════════════════════════════════════════════════════════════════
# 5. RECYCLE_INDUSTRY 객체
# ════════════════════════════════════════════════════════════════

cat("\n── 4. RECYCLE_INDUSTRY 객체 생성 중...\n")

ri_district_col <- first_col(recycle_ind, c("district", "gu", "자치구", "n"))

ri <- recycle_ind %>%
  rename(n = all_of(ri_district_col)) %>%
  mutate(
    life = round(num0(life_pct), 1),
    industry = round(num0(industry_pct), 1),
    construction = round(num0(construction_pct), 1),
    designated = round(num0(designated_pct), 1)
  ) %>%
  select(n, life, industry, construction, designated)

ri_list <- setNames(
  lapply(seq_len(nrow(ri)), function(i) {
    list(
      life = ri$life[i],
      industry = ri$industry[i],
      construction = ri$construction[i],
      designated = ri$designated[i]
    )
  }),
  ri$n
)

cat("  RECYCLE_INDUSTRY 자치구 수:", length(ri_list), "\n")

# ════════════════════════════════════════════════════════════════
# 6. CLUSTER_RESULT 객체
# ════════════════════════════════════════════════════════════════

cat("\n── 5. CLUSTER_RESULT 객체 생성 중...\n")

cl <- cluster_res %>%
  rename(n = all_of(cluster_gu_col)) %>%
  transmute(
    n,
    anchor = as.integer(num0(.data[[cluster_anchor_col]])),
    type = as.character(.data[[cluster_type_col]]),
    clusterType = as.character(.data[[cluster_type_col]]),
    workHome = round(num0(L1_work_home_ratio), 3),
    dayNightRatio = round(num0(L1_work_home_ratio), 3),
    weekendActive = round(num0(L2_weekend_active_ratio), 3),
    weekendHome = if ("weekend_home_ratio" %in% names(cluster_res)) round(num0(weekend_home_ratio), 3) else 0,
    avgEmpPerBiz = round(num0(B1_avg_emp_per_biz), 2),
    officeRatio = round(num0(B2_office_emp_ratio_no_support), 3),
    tourismRatio = round(num0(B3_consumption_tourism_emp_ratio), 3),
    lifeServiceRatio = round(num0(B4_life_service_emp_ratio), 3),
    industryRatio = round(num0(B5_industrial_logistics_emp_ratio), 3),
    pc1 = if ("PC1_도시기능" %in% names(cluster_res)) round(num0(`PC1_도시기능`), 2) else 0,
    pc2 = if ("PC2_도시기능" %in% names(cluster_res)) round(num0(`PC2_도시기능`), 2) else 0
  )

cluster_list <- setNames(
  lapply(seq_len(nrow(cl)), function(i) {
    list(
      anchor = cl$anchor[i],
      type = cl$type[i],
      clusterType = cl$clusterType[i],
      workHome = cl$workHome[i],
      dayNightRatio = cl$dayNightRatio[i],
      weekendActive = cl$weekendActive[i],
      weekendHome = cl$weekendHome[i],
      avgEmpPerBiz = cl$avgEmpPerBiz[i],
      officeRatio = cl$officeRatio[i],
      tourismRatio = cl$tourismRatio[i],
      lifeServiceRatio = cl$lifeServiceRatio[i],
      industryRatio = cl$industryRatio[i],
      pc1 = cl$pc1[i],
      pc2 = cl$pc2[i]
    )
  }),
  cl$n
)

cat("  CLUSTER_RESULT 자치구 수:", length(cluster_list), "\n")

# ════════════════════════════════════════════════════════════════
# 7. YEARLY 객체
# ════════════════════════════════════════════════════════════════

cat("\n── 6. YEARLY 객체 생성 중...\n")

yearly_list <- list()

if (!is.null(waste_int) &&
    all(c("year", "living_waste", "living_recycle", "living_incineration", "living_landfill", "food_waste") %in% names(waste_int))) {
  
  yearly_raw <- waste_int %>%
    group_by(year) %>%
    summarise(
      living_waste_sum = sum(num0(living_waste), na.rm = TRUE),
      living_recycle_sum = sum(num0(living_recycle), na.rm = TRUE),
      living_incineration_sum = sum(num0(living_incineration), na.rm = TRUE),
      living_landfill_sum = sum(num0(living_landfill), na.rm = TRUE),
      food_waste_sum = sum(num0(food_waste), na.rm = TRUE),
      per_capita_mean = mean(num0(per_capita_living_waste), na.rm = TRUE),
      recycle_rate_mean = mean(num0(recycle_rate), na.rm = TRUE),
      incineration_rate_mean = mean(num0(incineration_rate), na.rm = TRUE),
      landfill_rate_mean = mean(num0(landfill_rate), na.rm = TRUE),
      .groups = "drop"
    ) %>%
    mutate(
      total = round(living_waste_sum / 10000, 1),
      recycle = round(living_recycle_sum / 10000, 1),
      incineration = round(living_incineration_sum / 10000, 1),
      landfill = round(living_landfill_sum / 10000, 1),
      food = round(food_waste_sum / 10000, 1),
      perCap = round(per_capita_mean, 3),
      recycle_pct = round(recycle_rate_mean * 100, 1),
      incineration_pct = round(incineration_rate_mean * 100, 1),
      landfill_pct = round(landfill_rate_mean * 100, 1),
      etc_pct = round(100 - recycle_pct - incineration_pct - landfill_pct, 1),
      daily_avg = round(living_waste_sum / 365, 1)
    )
  
  yearly_list <- setNames(
    lapply(seq_len(nrow(yearly_raw)), function(i) {
      r <- yearly_raw[i, ]
      list(
        total = r$total,
        recycle = r$recycle,
        incineration = r$incineration,
        landfill = r$landfill,
        food = r$food,
        perCap = r$perCap,
        recycle_pct = r$recycle_pct,
        incineration_pct = r$incineration_pct,
        landfill_pct = r$landfill_pct,
        etc_pct = r$etc_pct,
        daily_avg = r$daily_avg
      )
    }),
    as.character(yearly_raw$year)
  )
  
} else {
  total_daily <- sum(num0(gu_out$daily), na.rm = TRUE)
  total_annual_10k <- round(total_daily * 365 / 10000, 1)
  
  recycle_pct <- round(mean(num0(gu_out$recycle), na.rm = TRUE), 1)
  inc_pct <- round(mean(num0(gu_out$inc), na.rm = TRUE), 1)
  land_pct <- round(mean(num0(gu_out$land), na.rm = TRUE), 1)
  
  yearly_list <- list(
    "2024" = list(
      total = total_annual_10k,
      recycle = round(total_annual_10k * recycle_pct / 100, 1),
      incineration = round(total_annual_10k * inc_pct / 100, 1),
      landfill = round(total_annual_10k * land_pct / 100, 1),
      food = round(total_annual_10k * mean(num0(gu_out$food), na.rm = TRUE) / 100, 1),
      perCap = round(mean(num0(gu_out$perCap), na.rm = TRUE), 3),
      recycle_pct = recycle_pct,
      incineration_pct = inc_pct,
      landfill_pct = land_pct,
      etc_pct = round(100 - recycle_pct - inc_pct - land_pct, 1),
      daily_avg = round(total_daily, 1)
    )
  )
}

cat("  YEARLY 연도:", paste(names(yearly_list), collapse = ", "), "\n")

# ════════════════════════════════════════════════════════════════
# 8. data2_1.js 생성
# ════════════════════════════════════════════════════════════════

cat("\n── 7. data2_1.js 생성 중...\n")

cluster_names <- c("🏢 상업형", "🏠 주거형", "🚶 유동집중형", "🔀 혼합형")
cluster_colors <- c("#dc2626", "#2563eb", "#d97706", "#7c3aed")

gu_by_name <- setNames(
  lapply(seq_len(nrow(gu_out)), function(i) {
    as.list(gu_out[i, ])
  }),
  gu_out$n
)

cluster_members <- split(gu_out$n, gu_out$clusterType)

data2_1 <- list(
  gu = gu_out,
  guByName = gu_by_name,
  clusterNames = cluster_names,
  clusterColors = cluster_colors,
  clusterMembers = cluster_members,
  clusterResult = cluster_list,
  recycleIndustry = ri_list,
  yearly = yearly_list,
  livingPop = living_list
)

out_21 <- file.path(DASH_DIR, "data2_1.js")

cat(
  paste0(
    "/* Auto-generated: ", as.character(Sys.time()), " */\n",
    "/* data2_1.js : GU / YEARLY / LIVING_POP / RECYCLE_INDUSTRY / CLUSTER_RESULT */\n\n"
  ),
  file = out_21,
  append = FALSE
)

write_window_block("DATA2_1", data2_1, out_21, append = TRUE)

cat(
  paste0(
    "window.GU = window.DATA2_1.gu || [];\n",
    "window.CLUSTER_RESULT = window.DATA2_1.clusterResult || {};\n",
    "window.LIVING_POP = window.DATA2_1.livingPop || {};\n",
    "window.RECYCLE_INDUSTRY = window.DATA2_1.recycleIndustry || {};\n",
    "window.YEARLY = window.DATA2_1.yearly || {};\n\n"
  ),
  file = out_21,
  append = TRUE
)

cat("  ✓ data2_1.js 생성 완료:", out_21, "\n")

# ════════════════════════════════════════════════════════════════
# 9. data2_2.js 생성 — 요인 분석 + 생활인구 보정
# ════════════════════════════════════════════════════════════════

cat("\n── 8. data2_2.js 생성 중...\n")

ri_factor <- ri %>%
  transmute(
    n,
    industryWastePct = industry,
    constructionWastePct = construction
  )

factor_features <- cl %>%
  select(
    n,
    workHome,
    dayNightRatio,
    weekendActive,
    officeRatio,
    tourismRatio,
    lifeServiceRatio,
    industryRatio
  )

factor_df <- gu_out %>%
  left_join(factor_features, by = "n", suffix = c("", "_cluster")) %>%
  left_join(ri_factor, by = "n") %>%
  mutate(
    livingPop = ifelse(is.na(livingPop) | livingPop <= 0, pop, livingPop),
    residentPerCap = round(perCap, 3),
    livingPerCap = round(daily * 1000 / livingPop, 3),
    
    dayNightRatio = ifelse(
      is.na(dayNightRatio) | dayNightRatio <= 0,
      dayNightRatio_cluster,
      dayNightRatio
    ),
    
    foreignerLivingRatio = ifelse(
      !is.na(foreignerLivingPop) & livingPop > 0,
      foreignerLivingPop / livingPop,
      0
    ),
    
    industryWastePct = ifelse(is.na(industryWastePct), 0, industryWastePct),
    constructionWastePct = ifelse(is.na(constructionWastePct), 0, constructionWastePct),
    
    message = case_when(
      clusterType == "상업형" ~ "업무·상업 기능이 강해 거주인구 기준 1인당 배출량이 과대평가될 수 있음",
      clusterType == "주거형" ~ "생활밀착·가정 배출 특성이 강해 감량 정책과 분리배출 개선 효과를 보기 좋은 유형",
      clusterType == "유동집중형" ~ "방문·소비·주말 활동 인구의 영향이 커 생활인구 보정지표가 필요함",
      TRUE ~ "주거·상업·산업 기능이 섞여 있어 단일 지표보다 복합 요인 해석이 필요함"
    )
  )

factor_by_gu <- setNames(
  lapply(seq_len(nrow(factor_df)), function(i) {
    r <- factor_df[i, ]
    
    list(
      daily = round(as.numeric(r$daily), 3),
      pop = round(as.numeric(r$pop), 0),
      livingPop = round(as.numeric(r$livingPop), 0),
      foreignerLivingPop = round(as.numeric(r$foreignerLivingPop), 0),
      daytimePop = round(as.numeric(r$daytimePop), 0),
      nighttimePop = round(as.numeric(r$nighttimePop), 0),
      
      residentPerCap = round(as.numeric(r$residentPerCap), 3),
      livingPerCap = round(as.numeric(r$livingPerCap), 3),
      
      dayNightRatio = round(as.numeric(r$dayNightRatio), 3),
      foreignerLivingRatio = round(as.numeric(r$foreignerLivingRatio), 4),
      
      recycle = round(as.numeric(r$recycle), 1),
      food = round(as.numeric(r$food), 1),
      inc = round(as.numeric(r$inc), 1),
      land = round(as.numeric(r$land), 1),
      
      workHome = round(as.numeric(r$workHome), 4),
      weekendActive = round(as.numeric(r$weekendActive), 4),
      officeRatio = round(as.numeric(r$officeRatio), 4),
      tourismRatio = round(as.numeric(r$tourismRatio), 4),
      lifeServiceRatio = round(as.numeric(r$lifeServiceRatio), 4),
      industryRatio = round(as.numeric(r$industryRatio), 4),
      
      industryWastePct = round(as.numeric(r$industryWastePct), 1),
      constructionWastePct = round(as.numeric(r$constructionWastePct), 1),
      
      cluster = as.integer(r$cluster),
      clusterType = r$clusterType,
      message = r$message
    )
  }),
  factor_df$n
)

adjusted_percap <- factor_df %>%
  transmute(
    gu = n,
    cluster = as.integer(cluster),
    clusterType,
    resident_percap = residentPerCap,
    living_percap = livingPerCap,
    living_pop = round(livingPop, 0),
    daytime_pop = round(daytimePop, 0),
    nighttime_pop = round(nighttimePop, 0),
    day_night_ratio = round(dayNightRatio, 3),
    foreigner_living_pop = round(foreignerLivingPop, 0),
    foreigner_living_ratio = round(foreignerLivingRatio, 4)
  )

data2_2 <- list(
  factorByGu = factor_by_gu,
  adjustedPerCap = adjusted_percap,
  caseStudies = list(
    gangseo = list(
      title = "강서구 — 사업장·건설계 영향 가능성",
      summary = "강서구는 생활계 외 사업장·건설계 폐기물 비중이 커 일반적인 자치구와 다른 패턴을 보일 수 있음"
    ),
    jongnoJunggu = list(
      title = "거주인구 기준 vs 생활인구 기준 1인당 총배출량 비교",
      summary = "거주인구는 작지만 낮 시간대 유입과 상업활동이 커 거주인구 기준 1인당 배출량이 과대평가될 수 있음"
    )
  )
)

out_22 <- file.path(DASH_DIR, "data2_2.js")

cat(
  paste0(
    "/* Auto-generated: ", as.character(Sys.time()), " */\n",
    "/* data2_2.js : 요인 분석 + 생활인구 보정 지표 */\n\n"
  ),
  file = out_22,
  append = FALSE
)

write_window_block("DATA2_2", data2_2, out_22, append = TRUE)

cat(
  paste0(
    "if (typeof GU !== 'undefined' && Array.isArray(GU)) {\n",
    "  GU.forEach(function(d) {\n",
    "    var f = window.DATA2_2.factorByGu[d.n];\n",
    "    if (f) Object.assign(d, f);\n",
    "  });\n",
    "}\n"
  ),
  file = out_22,
  append = TRUE
)

cat("  ✓ data2_2.js 생성 완료:", out_22, "\n")

# ════════════════════════════════════════════════════════════════
# 10. data2_3.js 생성 — 잔차 분석 + 회귀 유의변수 해석
# ════════════════════════════════════════════════════════════════

cat("\n── 9. data2_3.js 생성 중...\n")

if (is.null(resid_raw)) {
  stop(
    "resid_by_gu_2023_cluster_direct.csv 또는 잔차 CSV를 찾지 못했습니다.",
    call. = FALSE
  )
}

rs <- resid_raw
names(rs) <- trimws(names(rs))

gu_col <- first_col(rs, c("gu", "district", "자치구", "n"))
actual_col <- first_col(rs, c("waste_total", "actual", "actual_waste", "actual_waste_total"))
pred_col <- first_col(rs, c("pred_waste_baseline", "pred_baseline", "pred", "predicted"))
resid_col <- first_col(rs, c("baseline_residual", "residual", "resid"))
resid_pct_col <- first_col(rs, c("baseline_residual_pct", "residPct", "resid_pct", "residual_pct"))

rs <- rs %>%
  rename(gu = all_of(gu_col)) %>%
  mutate(
    cluster_type = if ("cluster_type" %in% names(.)) cluster_type else NA_character_,
    is_gangseo = if ("is_gangseo" %in% names(.)) bool01(is_gangseo) else as.integer(gu == "강서구"),
    is_yongsan = if ("is_yongsan" %in% names(.)) bool01(is_yongsan) else as.integer(gu == "용산구"),
    
    waste_total = num0(.data[[actual_col]]),
    pred_waste_baseline = num0(.data[[pred_col]]),
    baseline_residual = num0(.data[[resid_col]]),
    baseline_residual_pct = num0(.data[[resid_pct_col]]),
    
    living_coef = if ("living_coef" %in% names(.)) num_na(living_coef) else NA_real_,
    living_pvalue = if ("living_pvalue" %in% names(.)) num_na(living_pvalue) else NA_real_,
    living_effect_pct = if ("living_effect_pct" %in% names(.)) num_na(living_effect_pct) else NA_real_,
    living_sig = if ("living_sig" %in% names(.)) bool01(living_sig) else 0,
    living_direction = if ("living_direction" %in% names(.)) living_direction else NA_character_,
    
    elderly_coef = if ("elderly_coef" %in% names(.)) num_na(elderly_coef) else NA_real_,
    elderly_pvalue = if ("elderly_pvalue" %in% names(.)) num_na(elderly_pvalue) else NA_real_,
    elderly_effect_pct = if ("elderly_effect_pct" %in% names(.)) num_na(elderly_effect_pct) else NA_real_,
    elderly_sig = if ("elderly_sig" %in% names(.)) bool01(elderly_sig) else 0,
    elderly_direction = if ("elderly_direction" %in% names(.)) elderly_direction else NA_character_,
    
    day_night_coef = if ("day_night_coef" %in% names(.)) num_na(day_night_coef) else NA_real_,
    day_night_pvalue = if ("day_night_pvalue" %in% names(.)) num_na(day_night_pvalue) else NA_real_,
    day_night_effect_pct = if ("day_night_effect_pct" %in% names(.)) num_na(day_night_effect_pct) else NA_real_,
    day_night_sig = if ("day_night_sig" %in% names(.)) bool01(day_night_sig) else 0,
    day_night_direction = if ("day_night_direction" %in% names(.)) day_night_direction else NA_character_,
    
    food_coef = if ("food_coef" %in% names(.)) num_na(food_coef) else NA_real_,
    food_pvalue = if ("food_pvalue" %in% names(.)) num_na(food_pvalue) else NA_real_,
    food_effect_pct = if ("food_effect_pct" %in% names(.)) num_na(food_effect_pct) else NA_real_,
    food_sig = if ("food_sig" %in% names(.)) bool01(food_sig) else 0,
    food_direction = if ("food_direction" %in% names(.)) food_direction else NA_character_,
    
    model_name = if ("model_name" %in% names(.)) model_name else "M4 재학습 모델",
    model_r2 = if ("model_r2" %in% names(.)) num_na(model_r2) else NA_real_,
    model_adj_r2 = if ("model_adj_r2" %in% names(.)) num_na(model_adj_r2) else NA_real_,
    model_note = if ("model_note" %in% names(.)) model_note else NA_character_,
    
    sig_vars_summary = if ("sig_vars_summary" %in% names(.)) sig_vars_summary else NA_character_,
    cluster_interpretation = if ("cluster_interpretation" %in% names(.)) cluster_interpretation else NA_character_,
    
    residual_class_key = case_when(
      is_gangseo == 1 ~ "special",
      baseline_residual_pct > 10 ~ "over",
      baseline_residual_pct < -10 ~ "under",
      TRUE ~ "normal"
    ),
    
    residual_class = case_when(
      residual_class_key == "special" ~ "특이 사례",
      residual_class_key == "over" ~ "과다 배출",
      residual_class_key == "under" ~ "상대적으로 양호",
      TRUE ~ "예측 범위 내"
    ),
    
    residual_pct_label = safe_pct_label(baseline_residual_pct),
    
    sig_vars_for_card = mapply(
      make_sig_summary,
      living_effect_pct, living_sig,
      elderly_effect_pct, elderly_sig,
      day_night_effect_pct, day_night_sig,
      food_effect_pct, food_sig
    )
  ) %>%
  left_join(
    gu_out %>% select(n, clusterType_from_gu = clusterType),
    by = c("gu" = "n")
  ) %>%
  mutate(
    cluster_type = ifelse(
      is.na(cluster_type) | cluster_type == "",
      clusterType_from_gu,
      cluster_type
    ),
    cluster_type = ifelse(is.na(cluster_type) | cluster_type == "", "혼합형", cluster_type)
  )

resid_list <- setNames(
  lapply(seq_len(nrow(rs)), function(i) {
    r <- rs[i, ]
    
    list(
      clusterType = r$cluster_type,
      isGangseo = as.logical(r$is_gangseo),
      isYongsan = as.logical(r$is_yongsan),
      
      actual = round(as.numeric(r$waste_total), 3),
      pred = round(as.numeric(r$pred_waste_baseline), 3),
      residual = round(as.numeric(r$baseline_residual), 3),
      resid = round(as.numeric(r$baseline_residual), 3),
      residPct = round(as.numeric(r$baseline_residual_pct), 1),
      
      residualClassKey = r$residual_class_key,
      residualClass = r$residual_class,
      residualPctLabel = r$residual_pct_label,
      
      sigVarsSummary = r$sig_vars_summary,
      sigVarsForCard = r$sig_vars_for_card,
      clusterInterpretation = r$cluster_interpretation
    )
  }),
  rs$gu
)

regression_by_gu <- setNames(
  lapply(seq_len(nrow(rs)), function(i) {
    r <- rs[i, ]
    
    list(
      gu = r$gu,
      clusterType = r$cluster_type,
      residualClass = r$residual_class,
      residualPct = round(as.numeric(r$baseline_residual_pct), 1),
      residualPctLabel = r$residual_pct_label,
      sigVarsSummary = r$sig_vars_summary,
      sigVarsForCard = r$sig_vars_for_card,
      clusterInterpretation = r$cluster_interpretation,
      
      living = list(
        coef = r$living_coef,
        pvalue = r$living_pvalue,
        effectPct = r$living_effect_pct,
        sig = as.logical(r$living_sig),
        direction = r$living_direction
      ),
      
      elderly = list(
        coef = r$elderly_coef,
        pvalue = r$elderly_pvalue,
        effectPct = r$elderly_effect_pct,
        sig = as.logical(r$elderly_sig),
        direction = r$elderly_direction
      ),
      
      dayNight = list(
        coef = r$day_night_coef,
        pvalue = r$day_night_pvalue,
        effectPct = r$day_night_effect_pct,
        sig = as.logical(r$day_night_sig),
        direction = r$day_night_direction
      ),
      
      food = list(
        coef = r$food_coef,
        pvalue = r$food_pvalue,
        effectPct = r$food_effect_pct,
        sig = as.logical(r$food_sig),
        direction = r$food_direction
      )
    )
  }),
  rs$gu
)

model_info <- list(
  source = basename(resid_path),
  year = 2023,
  target = "waste_total",
  modelName = rs$model_name[1],
  r2 = rs$model_r2[1],
  adjR2 = rs$model_adj_r2[1],
  note = rs$model_note[1]
)

data2_3 <- list(
  modelInfo = model_info,
  resid = resid_list,
  residuals = rs,
  regressionByGu = regression_by_gu
)

out_23 <- file.path(DASH_DIR, "data2_3.js")

cat(
  paste0(
    "/* Auto-generated: ", as.character(Sys.time()), " */\n",
    "/* data2_3.js : 잔차 분석 + 회귀 유의변수 해석 */\n\n"
  ),
  file = out_23,
  append = FALSE
)

write_window_block("DATA2_3", data2_3, out_23, append = TRUE)

cat(
  paste0(
    "window.RESID = window.DATA2_3.resid || {};\n",
    "window.REGRESSION_BY_GU = window.DATA2_3.regressionByGu || {};\n",
    "window.REGRESSION_MODEL_INFO = window.DATA2_3.modelInfo || {};\n"
  ),
  file = out_23,
  append = TRUE
)

cat("  ✓ data2_3.js 생성 완료:", out_23, "\n")

# ════════════════════════════════════════════════════════════════
# 11. 검증 출력
# ════════════════════════════════════════════════════════════════

cat("\n✅ JS 파일 생성 완료\n")
cat("   - ", out_21, "\n")
cat("   - ", out_22, "\n")
cat("   - ", out_23, "\n")

cat("\n[검증] GU 행 수:", nrow(gu_out), "\n")
cat("[검증] RESID 행 수:", length(resid_list), "\n")
cat("[검증] REGRESSION_BY_GU 행 수:", length(regression_by_gu), "\n")

cat("\n[잔차 분류]\n")
print(table(rs$residual_class))

cat("\n[군집 분포]\n")
print(table(gu_out$clusterType))

cat("\n완료되었습니다.\n")