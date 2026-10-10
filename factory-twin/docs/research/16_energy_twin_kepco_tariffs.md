## 보고: 소규모 가구공장 디지털 트윈용 전기요금·전력 모델 조사 (2026-10-10 기준)

### 0. 조사 환경 및 원문 확인 여부 (중요)
- 이 세션에서는 **WebFetch와 curl이 모든 외부 도메인에 대해 차단**(DNS 해석 불가/프록시 403)되어 한전 사이버지점 요금표(`cyber.kepco.co.kr/.../CYEEHP00103.jsp`, `elec_total.pdf`), 전기공급약관, 기후에너지환경부 보도자료 **원문(PDF/HTML)을 직접 열람하지 못했습니다.** 아래 수치는 **WebSearch(extended) 요약에서 인용된 문장**과 사전 지식에 근거하며, 각 항목에 `[원문 미확인]` / `[검색요약 인용]` / `[추정]`을 표기했습니다. WebSearch 예산(세션 공유 200회)도 소진되어 추가 검색은 후속 메시지에서 계속해야 합니다.
- **최종 단가는 반드시** 한전 사이버지점 산업용 요금표 https://cyber.kepco.co.kr/ckepco/front/jsp/CY/E/E/CYEEHP00103.jsp 와 통합 요금표 PDF https://cyber.kepco.co.kr/cyber/updata/down/elec_total.pdf (또는 https://home.kepco.co.kr/kepco/front/html/CY/E/E/CYEEHP00103.html)에서 "적용일자 2026.4.16" 버전으로 교체하십시오. 디지털 트윈에서는 단가를 **설정 파일(적용일자별 버전)로 외부화**할 것을 권합니다.

---

### 1. 2026년 전기요금 (원문 확인 결과 및 대체 값)

#### 1-1. 2026-04-16 산업용(을) 계절·시간대별 요금 개편 — 확인된 내용 `[검색요약 인용, 보도자료 원문 미확인]`
출처: 전기신문 https://www.electimes.com/news/articleView.html?idxno=366017 , 에코미디어 https://m.ecomedia.co.kr/news/newsview.php?ncode=1065602617806520 , 기후에너지환경부 "(참고) 계절·시간대별 전기요금 체계 개편안 공개" https://mcee.go.kr/home/web/board/read.do?boardId=1849370&boardMasterId=1&menuId=286 , 포씨유신문 https://www.4cu.com/news/article.html?no=29254 , 철강금속신문 https://www.snmnews.com/news/articleView.html?idxno=566434 , 해줌 블로그 https://blog.haezoom.com/insight_re100_23/ , 에너센트 https://enersentry.com/%EC%82%B0%EC%97%85%EC%9A%A9-%EC%A0%84%EA%B8%B0%EC%9A%94%EA%B8%88-%EA%B0%9C%ED%8E%B8/

- 개편안 공개: 2026-03-13(전기위원회 심의). **산업용(을) 적용: 2026-04-16부터**, 전기차 충전 4-18, 일반용·교육용 **6-1**. 유예 신청 사업장(514곳 보도)은 **2026-10-01부터** 적용.
- 시간대 재편(49년 만의 개편): 평일 **11~12시, 13~15시: 최대부하→중간부하**(낮 9~15시가 중간부하로 통일), **18~21시: 중간부하→최대부하**. 경부하는 **22시~익일 08시**(봄·가을 기준 보도).
- 단가 변화: 최대부하 **여름·겨울 −16.9원/kWh, 봄·가을 −13.2원/kWh(평균 −15.4원)**, 경부하 **+5.1원/kWh**.
- **봄·가을 주말·공휴일 낮 11~14시 전력량요금 50% 할인**(토요일은 중간부하 요금의 50%, 공휴일은 경부하 요금의 50%로 보도. 일요일 처리는 보도에서 명시 확인 못함 → 약관 원문 확인 필요).
- 적용 대상: 산업용(을)(국가 전력소비의 약 46%). **산업용(갑)은 1차 대상이 아니며**, 블로그에서는 산업용(갑)Ⅱ 등이 6-1 적용이라는 서술도 있어 `[불일치, 원문 확인 필요]`.
- 2026년 1·3·4분기 요금 동결, **연료비조정단가 +5원/kWh 유지**(폴리뉴스 https://www.polinews.co.kr/news/articleView.html?idxno=717504 , 인사이트에너지뉴스 https://www.inenews.kr/news/articleView.html?idxno=28058 , 4분기 동결 블로그 https://www.make2t.kr/2026/09/electricity-rate-october-2026.html).

#### 1-2. 개편 후 시간대 정의 (디지털 트윈 구현용) `[보도 기반 재구성, 약관 원문 미확인]`
| 계절 | 경부하 | 중간부하 | 최대부하 |
|---|---|---|---|
| 여름(7~8월)·겨울(12~2월) 평일 | 22:00~08:00 | 08:00~18:00, 21:00~22:00 | **18:00~21:00** |
| 봄·가을(3~6, 9~11월) 평일 | 22:00~08:00 | 08:00~18:00, 21:00~22:00 | 18:00~21:00 (단가는 여름·겨울보다 낮음) |
| 토요일 | 22:00~08:00 | 08:00~22:00 (봄·가을 11~14시 50% 할인) | 없음 |
| 일요일·공휴일 | 전일 경부하 (봄·가을 11~14시 50% 할인) | — | — |

주의: 개편 전 표(gje.co.kr 등)는 최대부하 11~12, 13~18(여름·봄가을) / 10~12, 17~20, 22~23(겨울)이므로 2026 모델에 그대로 쓰면 안 됩니다. 겨울철 아침(10~12시) 최대부하 유지 여부는 보도에서 확인되지 않았습니다 `[원문 확인 필요]`.

#### 1-3. 기본요금·전력량요금 단가 — 확보된 값
완전한 2026-04-16 단가표는 원문 미열람으로 제시 불가. 아래는 2차 자료 인용값입니다.

**(a) 기본요금(원/kW) — 여러 자료에서 일관** `[검색요약 인용]`
| 계약종별 | 저압 | 고압A 선택Ⅰ | 고압A 선택Ⅱ | 고압A 선택Ⅲ |
|---|---|---|---|---|
| 산업용(갑)Ⅰ (300kW 미만) | 5,550 | 6,490 | 7,470 | — |
| 산업용(갑)Ⅱ (300kW 미만, 계시별) | — | 6,490 | 7,470 | 9,810 [추정] |
| 산업용(을) (300kW 이상) | — | 7,220 [추정] | **8,320** | 9,810 |
출처: 나무위키 전기요금 https://namu.wiki/w/%EC%A0%84%EA%B8%B0%EC%9A%94%EA%B8%88 , gje 요금표 http://gje.co.kr/%EC%A0%84%EA%B8%B0%EC%9A%94%EA%B8%88%ED%91%9C/ , elecmania https://elecmania.com/496 , 한전 요금표 https://cyber.kepco.co.kr/ckepco/front/jsp/CY/E/E/CYEEHP00103.jsp

**(b) 전력량요금(원/kWh)** `[검색요약 인용, 적용일자 불명·검증 필요]`
- 산업용(갑)Ⅰ 저압 (2025-04-01 시행 자료, 전력거래소 공공요금 PDF https://data.cmpi.or.kr/program/board/2025.04.01%20%EC%8B%9C%ED%96%89.pdf ): **여름 116.2 / 봄·가을 94.4 / 겨울 114.5** (2023-11-09 한전표: 107.7/85.9/106.0 → 2024-10-24 인상 반영).
- 산업용(갑)Ⅰ 고압A (2023-11-09 한전표): 선택Ⅰ 116.3/92.6/116.2, 선택Ⅱ 111.5/88.0/109.7. 2025년 값은 +8.5원/kWh 내외 인상 `[추정: 2024-10-24 중소기업용 인상폭 기억 기반]`.
- 산업용(갑)Ⅱ 고압A 선택Ⅱ(7,470): 여름 경부하 82.3 / 중간 108.1 / 최대 141.6, 겨울 경부하 89.7 (나무위키, 연도 미표기).
- 산업용(을) 고압A 선택Ⅱ(8,320): 경부하 여름·봄가을 94.0 / 겨울 101.0 (나무위키), 또는 92.8/99.8 (cmpi 2025-04) — **두 자료 불일치**. 중간·최대부하는 검색 요약이 행을 혼동(146.9/116.5/147.1, 163.8/133.4/164.0 등)하여 신뢰 불가.
- 2026-04-16 이후 값 = (2025 값) + (경부하 +5.1, 최대부하 −16.9/−13.2)로 근사 가능하나 **구간 재편으로 kWh 배분 자체가 달라지므로 원문 표 필요.**

**(c) 부가 항목**
- 기후환경요금 **9원/kWh** (yogum 가이드 https://yogum.kr/guides/climate-environment-charge/ , 나무위키 "2024년 기준 9.0원, 매년 변동") `[2026 공식 고시 미확인]`
- 연료비조정요금 **+5원/kWh** (2026년 전 분기 유지, 상한 ±5원)
- 부가가치세 10%, **전력산업기반기금 2.7%** (3.7→3.2%(2024-07)→2.7%(2025-07), 한국경제 https://www.hankyung.com/article/202406301237Y , 이투뉴스 http://www.e2news.com/news/articleView.html?idxno=307187 ). 나무위키는 3.2%로 표기하나 2.7%가 현행.

청구액 공식 (English):
```
Energy_charge  = Σ_t kWh_t × rate(season_t, period_t)   (15-min or hourly buckets)
Base_charge    = Billing_demand_kW × base_rate(option) × (1 ± PF_adj)
Subtotal       = Base + Energy + 9 × kWh + 5 × kWh      (climate + fuel-adj)
Bill           = Subtotal × (1 + 0.10 VAT) + Subtotal × 0.027 (fund, rounded to 10 KRW)
```

---

### 2. 요금 구조 메커니즘

- **계약전력 vs 요금적용전력** (전기공급약관 제8장 https://cyber.kepco.co.kr/ckepco/front/jsp/CY/D/C/CYDCHP00108.jsp `[원문 미확인]`): 최대수요전력계(고압·계약전력 20kW 이상 수용가)는 **15분 평균 전력의 월 최대값**을 기록. 요금적용전력 = 당월 및 직전 11개월 중 **12·1·2·7·8·9월의 최대수요전력 중 최대값**(단, 계약전력의 30% 미만이면 30%) `[사전지식, 약관 제68조 원문 확인 필요]`. 여름·겨울 피크 한 번이 12개월 기본요금을 결정.
- **계약전력 초과 할증**: 초과비율(초과전력÷계약전력) **20% 미만 → 기본요금 단가의 150%, 20~30% → 200%**, 그 이상 더 높은 배율; 초과 횟수 2~3회 150%, 4~5회 200%, 6회 이상 더 높은 배율 표도 존재 `[검색요약 인용, 적용조건 원문 확인 필요]` (클리앙 해설 https://www.clien.net/service/board/lecture/13159501 ). 모델: `penalty = max(0, Peak−Contract) × base_rate × multiplier`.
- **역률 요금** (약관 제5장 https://cyber.kepco.co.kr/ckepco/front/jsp/CY/D/C/CYDCHP00105.jsp `[검색요약 인용]`): 기준 지상역률 90%. 09~23시 평균역률(30분 단위 누적값의 월평균)이 90% 미달 시 **60%까지 매 1%당 기본요금 0.2% 추가**, 90% 초과 시 **95%까지 매 1%당 0.2% 감액**(최대 −1.0%). 23~09시 진상역률 95% 미달 시 매 1%당 0.2% 추가. 저압·비원격검침 고객은 1개월 누적값 사용. 구 자료(eom.co.kr)의 0.5%/1%는 폐기된 값.
- **선택요금제 손익분기**: `H* = Δbase / Δenergy` (월 사용시간 = kWh/요금적용전력). 2023 산업용(갑)Ⅰ 고압A 기준 Δbase 980원, Δenergy 4.6~4.8원 → **약 204~213 h/월**. 에너지신문 설명도 "월 200시간"(https://www.energy-news.co.kr/news/articleView.html?idxno=83259 ); 일부 자료는 500시간(선택Ⅲ 비교). 주간 1교대 가구공장(월 ~200~250h)은 **선택Ⅰ·Ⅱ 경계**이므로 트윈에서 세 요금제를 동시에 계산해 비교하도록 구현 권장.
- **전력량요금 적용**: 각 15분(또는 1시간) 구간 kWh × 해당 계절·시간대 단가 합산. 계절은 월 단위(7~8 여름, 12~2 겨울, 나머지 봄·가을).
- **계약전력 변경** (준기가스 https://junkigas.com/moving-in-or-out/modifying-electricity-contract , inside114 https://inside114.com/entry/%ED%95%9C%EC%A0%84-%EA%B3%84%EC%95%BD%EC%A0%84%EB%A0%A5-%EB%B3%80%EA%B2%BD%EC%A6%9D%EC%84%A4%EA%B0%90%EC%86%8C-%EB%B0%A9%EB%B2%95 , 에디슨이엔씨 https://edisonenc.com/insight/%EA%B3%84%EC%95%BD%EC%A0%84%EB%A0%A5-%EC%A6%9D%EC%84%A4-%EB%B9%84%EC%9A%A9-%EA%B8%B0%EC%A4%80 ): 감소(일부해지)는 관할 지사에 전기사용변경신청(변경신청서, 건물대장/등기, 임대차계약서, 6kW 이상은 소유자 인감), 1년 내 원복 가능, 3년 내 재증설 시 시설부담금 면제. 증설은 전기공사업체 내선공사 후 신청 + 한전 표준시설부담금 + 내부 공사비. 고압 kW당 표준시설부담금 단가는 미확인 `[한전 123 문의 필요]`. 300kW 경계를 넘으면 산업용(갑)↔(을) 종별 자체가 바뀜.
- **가구공장 전형적 월 요금 구성** `[추정]`: 계약 200kW, 피크 140kW, 월 35,000kWh, 선택Ⅱ 고압A 가정 → 기본요금 140×8,320≈116만원, 전력량 35,000×~110원≈385만원, 기후환경+연료비 14×35,000≈49만원 → 세전 ≈550만원, 기본요금 비중 **약 20~25%**(부하율 낮은 공장은 30%까지).

---

### 3. 데이터 접근

- **파워플래너**(pp.kepco.co.kr, 웹 안내서 https://pp.kepco.co.kr/files/manual/powerplanner_web.pdf , 앱 안내서 https://pp.kepco.co.kr/files/manual/powerplanner_app.pdf ) `[검색요약 인용]`: AMI 설치 고객만 이용. **고압 고객은 15분 단위 96건/일**, 저압은 60분 24건. 조회 항목: 사용량, 최대수요, 유효/무효전력량, 역률, CO₂. 요일별·시간대별 조회는 고압 기준 3개월 이내. **최대수요전력 목표 설정 → 초과 시 푸시/PC 팝업 알림**(피크 관리에 직접 활용). 엑셀 다운로드 메뉴 존재 여부는 안내서 텍스트 손상으로 미확인(블로그는 "엑셀 내려받기 가능" 언급). 뉴시스 https://www.newsis.com/view/NISX20240628_0002791606
- **한전ON**(online.kepco.co.kr): 구 사이버지점 '전력사용정보 → 시간대별 사용량'(AMI 필요) 기능 승계. 고압 사업자 15분 CSV 경로 미확인 → 123 콜센터/담당 영업소 확인 필요.
- **전력데이터 개방포털** https://bigdata.kepco.co.kr/cmsmain.do?scode=S01&pcode=000493&pstate=L&redirect=Y 및 공공데이터포털 API(계약종별 https://www.data.go.kr/data/15101360/openapi.do , 산업분류별 https://www.data.go.kr/data/15101403/openapi.do ): **집계 통계만 제공**, 고객 개별 LP 없음. 벤치마크(가구 제조업 법정동별 사용량 https://www.data.go.kr/data/15104908/fileData.do?recommendDataYn=Y )에는 유용.
- **제3자(컨설턴트) 열람**: 한전 **전력데이터 플랫폼(EDS 마켓 https://edsm.kepco.co.kr/cmsmain.do?scode=S02&pcode=000313&redirect=Y ) / EN:TER** https://www.en-ter.co.kr/ 에 "서비스사업자"로 등록한 뒤, 고객이 전체서비스 메뉴에서 **정보제공동의** 버튼으로 동의(개인정보 수집·제3자 제공 동의 포함, 이용약관 https://en-ter.co.kr/ft/agreement3.do ). 동의 유효기간 **1년**, 만료 전 갱신 필요(하나루프 절차 안내 https://www.hanaloop.com/en/docs/x30_platform/2022-10-12-kepco_data_share/ ). 사업자용 API의 15분 LP 연동 가능 여부는 미확인 `[EDS 사업자 포털 공지 확인 필요]`.
- **AMI 미설치 고객 대안**: (1) 고압 고객은 사실상 원격검침(AMR/AMI, 15~60분 주기)되어 있어 영업소에 "계량데이터(LP) 제공" 요청 가능(전기가계부 안내 https://cyber.kepco.co.kr/ckepco/front/jsp/CY/L/A/CYLAPP00102.jsp , 한전 AMI 서비스 https://home.kepco.co.kr/kepco/front/html/WZ/2024_01/light.html ). (2) 수용가 측 **수전반 CT에 파워미터/클램프 로거(1초~1분)** 설치로 자체 LP 생성 — 트윈 검증용으로도 필요. (3) 고지서의 월 최대수요·시간대별 kWh는 즉시 확보 가능.

---

### 4. 설비별 전력 모델

**(a) 상태별 전력 모델** (English):
```
P_machine(state) = P_standby (control/hydraulic idle, 2–10% of rated)
                 | P_idle    (spindle/motor running no cut, 20–40% of rated)
                 | P_busy    (cutting, 50–90% of rated, depends on feed/material)
Nameplate kW is shaft output; electrical input = P_shaft / η(load).  Measured 3-phase:
P = √3 · V · I · PF ;  I_rated ≈ P_rated / (√3·V·η·PF)
```
명판 kW는 축동력이므로 실측 입력은 명판보다 5~15% 크지만, 가공기는 부하율이 낮아 평균 입력은 명판의 30~60% `[추정]`.

**(b) 모터 부하율–효율–역률** (현대일렉트릭 IE3 카탈로그 https://hyundaiacmotor.com/product/hyundai-electric-motor-37kw/ , https://hyundaiacmotor.com/product/hyundai-electric-motor-1hp/ ): 37kW 4극 효율 100%/75%/50% 부하 = 94.5/94.5/93.3%, PF 0.85; 0.75kW 4극 = 83.5/82.6/78.5%, PF 0.78. 역률은 부하율 50% 이하에서 급락(0.5~0.6)하므로 공회전 많은 목공기계는 무효전력 비중이 큼. 트윈용 근사: `η(L) ≈ η_rated × (1 − k·(1−L)²)`, `PF(L) ≈ PF_rated × L/(L+0.15)` `[추정식]`.

**(c) 집진기(송풍기) — 팬 법칙**:
```
Q ∝ N,  ΔP ∝ N²,  P_fan ∝ N³   →  75% speed ≈ 42% power, 50 Hz(of 60) ≈ 58%
Damper throttling saves only 10–25% vs VFD on the same flow reduction
```
근거: Camfil VFD 블로그(25% 감속 → 42% 전력, 평균 30% 절감) https://camfilapc.com/blog/variable-frequency-drive/ ; NEEA "Just Enough Air" 목공 집진 프로그램 **23~39% 절감, 교체 시 최대 50%**(ACEEE 2005 https://www.aceee.org/wp-content/uploads/proceedings-1980-2020/2005/SS05_Panel01_Paper11.pdf ); 사이클론 집진 효율 논문(목제품 공장) https://www.scirp.org/journal/paperinformation?paperid=112270 ; 한국에너지공단 인버터 용도별 절감률 조사에서 **팬 43.13%**로 최고(헬로티 https://www.hellot.net/news/article.html?no=19041 ); 55Hz 운전 23%, 50Hz 운전 42% 계산 사례(에너지경제 https://m.ekn.kr/view.php?key=11401 ); 가구공장 2,500㎡ 집진 사례 20~30% 절감 https://www.qdequipment.com/news/dust-collection-system-furniture-factory-case-study.html . **"집진이 공장 전력의 50%"라는 수치는 공개 1차 자료에서 확인 못함** — 목공 집진이 "상당 비중"이라는 서술만 확인. 소형 가구공장에서 집진+컴프레서가 30~50%를 차지하는 것은 현장 경험상 흔함 `[추정]`.

**(d) 컴프레서** (아트라스콥코 https://www.atlascopco.com/ko-kr/compressors/air-compressor-blog/compressed-air-energy-costs , 에너지공단 EG-TIPS https://tips.energy.or.kr/commonsystem/commonsystem_view_01.do?code_num=CS&ch_code_num=CS01 , https://tips.energy.or.kr/diagnosis/qna_view.do?no=1746 ): 무부하(언로드) 전력 = 부하전력의 **25~50%**; 토출압 1 bar 하향 → **6~8%(≈7%)** 절감 및 누설량 13% 감소; 현장 누설은 소비량의 **10~20%**; 6 bar 기준 **1 mm 누설 1개소 ≈ 연 30만원**. VSD 절감 10~35%(논문 최대 20%, 제조사 최대 34~35%; 경원기계 100HP 인버터+누설개선 20% 이상 예상 http://www.anycomp.kr/m/sub2_1_1.html ).
```
P_comp(t) = P_load·u(t) + P_unload·(1−u(t)),  u = duty = Q_demand/Q_rated
Leak_kW ≈ Q_leak[m³/min] × SpecificPower[kW/(m³/min)] (≈6–7 kW per m³/min at 7 bar)
Leak_cost/yr = Leak_kW × hours × rate;  Leak_Q (orifice): Q = C·A·√(2ΔP/ρ)  or EG-TIPS Q=237.6/γ·(A·c·P)/√T [ℓ/min]
```
**(e) 건조실 히터**: 저항히터 PF≈1, 온도 제어 ON/OFF 듀티(정격 × 듀티 30~70% `[추정]`); 열펌프 건조기 COP 2~3. **UV/도장 부스 배기팬**: 정속 팬이면 운전 중 정격 80~100% 고정 → VFD·연동 제어 대상. **조명**: 면적당 10~15 W/㎡(형광/메탈) → LED 5~8 W/㎡ `[추정]`, LED 교체 절감 40~60%.

---

### 5. 15분 부하 프로파일 합성 알고리즘

```
Input: event log (machine_id, state, t_start, t_end), 1 Hz current optional
1. Per machine: P_i(t) = lookup(state_i(t)) [kW], add start transient:
   P_start = k_start × P_rated for Δt_start (DOL: k≈1.5–2.5 real-power for 2–5 s;
   15-min average impact = P_start·Δt/900 → usually negligible unless many DOL starts in one window)
2. Shared loads: P_dust(t) = f(Σ open gates, VFD on/off), P_comp(t) = duty model from Σ q_i(state), P_light, P_HVAC/dryer
3. Aggregate 1 Hz: P_total(t) = Σ P_i + losses (transformer no-load ≈0.2–0.5% of kVA, cable ≈1–2%)
4. Resample: kW_15 = mean over [t, t+15min);  kWh_15 = kW_15/4
5. Peak = max(kW_15) over month; billing demand per §2; TOU cost per §1
6. Simultaneity: CF = Peak / Σ P_rated_connected  (furniture shops: 0.3–0.5 [추정]);
   Monte-Carlo on start-time jitter → P(peak > contract)
Validation: compare with KEPCO 15-min LP (파워플래너/EDS): daily kWh MAPE < 10%, peak error < 5%, monthly PF ±2 pts;
calibrate state powers by least squares on sub-metered circuits (dust, compressor, machine groups).
```
참고 구현: 제조 생산데이터 기반 전력사용량 예측·피크 위험조건 분석 https://github.com/junseo0im/fac-power-forecast-final . 1 Hz 전류만 있으면 `P = √3·V·I·PF(state)`로 환산하되 PF는 상태별 측정값 사용.

---

### 6. 절감 레버 정량화 (국내 우선, 범위는 [추정] 포함)

| 레버 | 기대 절감 | 투자비·회수 | 근거 |
|---|---|---|---|
| 피크 분산(기동 순서 인터록, 18~21시 잔업 회피, 건조·컴프레서 선행 가동) | 피크 10~20% ↓ → 기본요금 10~20% ↓(청구액 2~5%); 18~21시 kWh를 중간부하로 이동 시 kWh당 ~28~30원 절감 | 시퀀스 변경 0~수백만원, 파워플래너 목표전력 알림 무료 | §1 개편 단가(여름 중간→최대 전환폭 28.5원 블로그 계산), 파워플래너 안내서 |
| 계약전력 적정화·선택요금 변경 | 과대 계약 시 기본요금 5~15% ↓; 선택Ⅰ↔Ⅱ 월 200h 경계 | 신청 비용 0, 3년 내 복구 시 부담금 면제 | §2 |
| 역률 개선(자동 역률 콘덴서) | 기본요금 최대 ±1.0%(85→95%: 약 2%p) + 변압기·케이블 손실 ↓ | 100~300 kvar 뱅크 수백만원, 회수 1~3년 `[추정]` | 약관 역률 조항 |
| 집진 VFD + 구역 댐퍼(블라스트 게이트 연동) | 집진 전력 23~39%(최대 50%) ↓ | 22~45kW VFD 200~500만원, 회수 1~2년(벤더 "1년 미만") | NEEA/ACEEE, Camfil, 공단 팬 43% |
| 컴프레서: 압력 1 bar ↓ / 누설 수리 / VSD | 7% / 10~20% / 10~35% | 누설 수리 수십만원, VSD 37kW 1,000만원대 `[추정]`, 회수 1~3년 | Atlas Copco, EG-TIPS |
| 봄·가을 주말 낮(11~14시) 50% 활용 | 해당 시간 kWh 요금 50% ↓(주말 잔업·건조 배치) | 0 | §1 |
| 조명 LED | 조명 전력 40~60% ↓(공장 전체 2~5%) | 회수 2~3년 `[추정]` | 일반 사례 |
| 대기전력·공회전 차단(자동 정지 타이머) | 공회전 kWh 5~15% ↓ `[추정]` | 저가 | 상태별 모델 |

---

### 7. 지원 제도 `[검색요약 인용, 2026 공고 원문 미확인]`
- **한국에너지공단 산업진단보조(무료 에너지진단)**: 연 300~2,000 toe 사용 중소·중견기업 대상, 2024년 한도 800만~1,000만원, 예산 75.2억/약 940개소(bizinfo 공고 https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/view.do?pblancId=PBLN_000000000095464 , 전기신문 https://www.electimes.com/news/articleView.html?idxno=333056 ). 전력 1 MWh ≈ 0.215 toe이므로 **연 1,400 MWh 미만 소규모 가구공장은 300 toe 기준에 못 미칠 수 있음** → 공단 '중소기업 에너지·탄소 인벤토리 구축지원'(https://www.bizinfo.go.kr/sii/siia/selectSIIA200Detail.do?pblancId=PBLN_000000000090827 ), 지자체 사업 활용. 문의 에너지진단실 052-920-0652/0653, https://www.energy.or.kr .
- **지자체**: 부산 2026 에너지진단·시설개선 지원(2,000 toe 미만, 시설개선비 50%·최대 1,300만원, 접수 2026-03-09~04-03 종료) https://sosangong.com/business-announcement/29186 . 타 지자체 2026 공고는 미조회.
- **에너지이용합리화자금(에너지절약시설 설치 융자)·고효율기기 지원**: 2026 금리·한도 미확인 → 공단 자금지원 페이지 확인 필요 `[미확인]`.
- **DR**: 국민DR은 **계약전력 200kW 이하** 소규모 사용자 대상, 감축 보상 약 1,600원/kWh(2023 보도, 에너지신문 https://www.energy-news.co.kr/news/articleView.html?idxno=88728 ); 신뢰성DR은 수요관리사업자(KT GiGA energy DR https://enterprise.kt.com/pd/P_PD_BS_ES_002.do 등)를 통해 1~4시간 감축 가능 공장 참여, 전력거래소 RRMSE 패턴 검증 필요. 200~400kW 공장은 수요관리사업자 집합자원으로 참여 가능 `[2026 요건 미확인]`. ESS는 개편 후 경부하–최대부하 차익 축소(+5.1/−15.4)로 경제성 재검토 필요 `[추정]`.

---

### 8. 디지털 트윈 전력 파라미터 표 (초기값, 전부 `[추정]` — 현장 실측으로 교체)

| 설비 | 정격 kW | 대기/정지 | 공회전 | 가공(부하율) | PF(가공/공회전) | 비고 |
|---|---|---|---|---|---|---|
| 패널쏘/런닝쏘 | 5.5~15 | 0.1~0.3 | 25~35% | 50~80% | 0.85/0.55 | 주축 DOL 기동 |
| CNC 라우터/보링 | 7.5~22 | 0.5~1.5(제어+진공) | 30~40% | 50~70% | 0.85/0.6 | 진공펌프 5.5~11kW 상시 |
| 엣지밴더 | 7.5~20 | 1~3(히터 유지) | 30~40% | 50~70% | 0.9 | 히터 PF≈1 |
| 와이드벨트 샌더 | 15~45 | 0.3 | 30~40% | 50~80% | 0.85/0.5 | 피크 기여 큼 |
| 집진기(송풍기) | 15~75 | 0 | 정속 80~100% | VFD 시 40~70% | 0.85 | 공장 전력 20~40% |
| 스크류 컴프레서 | 15~37 | 0 | 언로드 25~50% | 로드 100% | 0.85 | 듀티 30~70% |
| 건조실 히터 | 10~50 | 0 | — | 듀티 30~70% | 1.0 | 야간·주말 이동 가능 |
| 도장/UV 부스 배기팬 | 5.5~15 | 0 | — | 90~100% | 0.8 | 도장 시간만 |
| 조명 | 면적×10~15 W/㎡ (LED 5~8) | — | — | 100% | 0.9 | 자연광 연동 |
| 변압기 무부하손 | 0.2~0.5% kVA | 상시 | | | | |

**현장 측정 항목**: 수전반 15분 kW·kVar·PF(1개월 이상), 집진·컴프레서·건조·조명 분기별 서브미터(클램프 로거 1분), 각 기계 상태별 전류 스냅샷(정지/공회전/가공 3점), 컴프레서 로드/언로드 시간비 및 토출압, 집진 댐퍼 개도 수, 기동 시간 분포(출근 직후 동시 기동 여부), 고지서 12개월(최대수요·시간대별 kWh·역률).

### 후속 필요 작업
WebFetch/curl 차단과 검색 예산 소진으로 (1) 한전 2026-04-16 산업용(을)/(갑) 단가표 원문, (2) 약관 제68조·역률 조항 원문, (3) EDS 사업자 API 사양, (4) 2026 에너지이용합리화자금 조건은 후속 세션(네트워크 허용 환경 또는 사용자가 PDF를 직접 첨부)에서 열람해 교체해야 합니다.