## 명세서 v2.2 비판적 검토 (리뷰 11 후속, 코드 실행 포함)

검토 대상: `/home/user/claude_mem/factory-twin/docs/03_공장복제_명세서.md`(v2.2, 56,883자), `docs/01_현장방문_체크리스트.md`, `docs/05_역할별_현장카드.md`, `docs/06_보고서_템플릿_STRESS-DES.md`, `docs/research/11_critical_review_of_spec_v2.md`, `tools/templates_to_json.py`, `sim/{factory_sim,validate,calibrate,uncertainty,queueing_prescreen,bottleneck_active_period,power_profile}.py`. 실행: `bash tools/test_chain.sh`(exit 0; 판정 6개 중 5개 실패 — 코드 경로 테스트이므로 정상), `python3 sim/validate.py`(exit 2, baseline에 `observations.validation` 없음), `queueing_prescreen.py`, history 모드 수동 실행. 템플릿 xlsx는 시트 24개(`0~24`, 9 없음; `data/sample_filled_template.xlsx`는 24 없음).

---

### 1. 리뷰 11의 수정 10개 — 항목별 판정

| # | 제안 | 판정 | 근거 |
|---|---|---|---|
| 1 | 허용 오차 한 표(v0.5/v1), 시트 18 → `observations.validation`, 01 §7-2 `validate.py` | **부분** | §1.2 두 열·시트 18 export·01 §7-2는 됨. 그러나 §4 표는 아직 독자 수치("도착/투입: 주 출하 ±5%", "모델 전체: 처리량 ±5%, 리드타임 ±10%", "WIP ±15%")를 단계 표시 없이 유지, §2.7은 "일 kWh MAPE <10%, 피크 ±5%, 역률 ±2%p"라는 세 번째 기준 추가. 00 §59 "출하량·WIP ±10%", 02 §15 "현장 수집 템플릿 (12 시트)" 미수정 |
| 2 | 5인 시간표·역할명 통일·반장 휴식 인터뷰·워크샘플링 무작위 | **부분** | §5·05 카드는 재작성됨. 01 §2는 "충돌 시 §5를 따른다" 한 줄을 붙이고 **옛 A/B/C/D 표를 그대로 둠**("15:15 카메라 회수", "워크샘플링(3분 간격 2시간)", 17:00 종료). 01 §0 "3명이면 D를 B, C가 분담"은 §0-6 "5명이 최소"와 정면 충돌 |
| 3 | 변환기: 측정# 합산, per_unit 회귀, 시트 5·8·11·16·20 읽기 | **대체로 적용** | 전부 읽음. 단 회귀는 edge(v_f 있을 때)·bore만, 시트 5는 쌍 무시 평균, 시트 8은 `history_list`만 만들고 `mode`는 `"generate"` 고정(§12-0 `orders.mode: history`를 켜는 경로 없음) |
| 4 | `Shift` 요일·잔업, 가용률 계수, 워밍업 문구 | **부분** | `Shift.working()`은 됨. 그러나 주문 생성 `if day % 7 >= 5`, 투입 역산 `if d % 7 < 5`, `steady_days … d % 7 < 5`, `power_profile.working()`, `bottleneck_active_period.clip()`이 전부 **월~금 하드코딩** → 토요 특근·6일제는 Shift만 알고 나머지 도구는 모름. 시트 0 "잔업 패턴"은 `overtime_note` 문자열로만 저장되어 `shift.overtime`은 템플릿 경로에서 생성되지 않음 |
| 5 | §2 표에 "모델 반영 v0.5/v1" 열 추가, §13 흡수 | **미적용** | §2.1~2.7 어디에도 열 없음. §13은 별도 표로 남았고 낡음(§2 참조) |
| 6 | 시트 23 운반·출하 대장 + 04 추가 | **적용** | 시트 23, 04 §26~31 확인. 단 변환기가 대차 `수량`을 **`transport.handlers`(운반 인원)** 에 넣음(`f["transport"]["handlers"] = int(num(r.get("수량")…`) — 대차 6대 = 운반자 6명. S8이 쓰는 `transport.carts`는 변환기가 만들지 않음 |
| 7 | 시트 9·14 통합, 시트 12 필수 행 | **적용** | 시트 9 삭제, 14 머리글 "검증 전용", 12에 【필수】 2행 |
| 8 | 시트 5 쌍, 13 셋업 열, ±1회→±20%, 재작업 제외 | **부분** | 시트 13 열·§1.2 ±20%·재작업 제외는 됨. 그러나 시트 18 "셋업 횟수/일" 행의 **KPI 키가 비어 있고**(`["셋업 횟수/일", "", "", "13 양식 셋업 열·CT 간격", 20…]`) kpis.json에도 셋업 횟수 키가 없어 `validate.py`가 이 지표를 영원히 판정 못 함(이벤트 로그엔 `setup` 370건이 있는데 집계 안 함) |
| 9 | 리드타임 정의 통일, `order_t` KPI, 병목 1위 빈도 | **대체로 적용** | §1.2 두 정의, `order_lead_days_avg`, `compare.py bottleneck_freq`. 단 §1.2 "생산 리드타임 **P90**"에 대응하는 키 없음(`lead_time_min.p90`은 달력 분 기준의 다른 지표) |
| 10 | 일관성 일괄 정리 | **부분** | CT 10대·카메라 3대·튜링 문장·시트 4 머리글·파워플래너는 됨. §14 "시트 0~23"은 실제 0~24(01 장비표가 "시트 24" 인용)라 **같은 유형의 드리프트 재발**. §3 "수작업 요소 시간(표본 5~10)" vs §4 "당일 최소 10" 잔존. 01 17:00 vs §5 18:00 종료 잔존 |

요약: 완전 적용 2, 대체로 2, 부분 5, 미적용 1.

---

### 2. v2.2에서 새로 생긴 모순·오류

**§1.2 KPI 키 vs kpis.json.** 실제 키: `products_completed, throughput_steady_per_day, lead_time_work_min_avg, order_lead_days_avg, lead_time_min{avg,p90,max}, avg_wip_batches, on_time_ratio, energy.total_kwh, bottleneck_ranking[], stations.<ID>.utilization`. §1.2 12행 중 키가 없는 것: 생산 리드타임 **P90**, 셋업 횟수/일, 게이트별 시간당 통과, 구역별 WIP(대차 단위 — `avg_wip_batches`는 전 공장 배치 수), 제품군별 출하(`products_completed`는 합계). 또 `products_completed`는 **워밍업 포함 horizon 20일 전체**인데 시트 18 행 이름은 "2주 출하량" — 기간이 다르면 ±10%는 무의미.

**전력 kWh가 도구마다 다르다.** 같은 baseline 실행에서 `kpis.energy.total_kwh = 8178`(when_any_on ×1.3 근사, 교대 내 idle만), `power_summary.kwh_total = 9924`(15분 게이팅). 차이 21% > 허용 ±10%. 시트 18은 전자를, §1.2 "15분 합산"은 후자를 가리킨다.

**§13 "구현" 표시가 코드와 반대.** "납기 우선 디스패칭: 미구현(큐 FIFO)" → `PriorityResource … dispatch == "edd"`(factory_sim.py 80행)와 S7 존재. "상류 복귀 재작업: 미구현" → `rework_rate/rework_to`, `rework_flow()`(367행). "대차 수 제약: 미구현" → `transport.carts`(147행), S8. "15분 전력·TOU: 미구현(일 합계, 단일 요율)" → `power_profile.py` 존재, §2.7이 그 파일을 인용. 네 행이 v2.1 모델 설명 그대로 남음. "요일·잔업 구현"은 위 #4처럼 반만 맞다.

**활성기간 병목: DRY1 1위는 말이 안 된다.** `sim/out/baseline/bottleneck_active_period.md`: DRY1 단독 25%·이동 17%, 점수 0.33. 그런데 DRY1은 `capacity 3`, util **0.166**(kpis)이고, 가동률 점수 1위는 CUT2, Kingman은 assemble/bore. 원인: `log_state("busy")`는 슬롯 하나만 차도 busy라 건조기(70분 배치, 3슬롯)는 거의 항상 "활성"이고, 그룹화는 **병렬 스테이션**(EB1,EB2)만 "전부 busy"로 묶고 **단일 스테이션의 capacity>1은 포화 판정을 안 함**. 표의 단독 합 64% + 이동 합 74% = 138% — 분할이 아니다(`shift[top[1]] += 1; shift[overl[0][1]] += 1` 두 번 증가). §12-1 "단독 >60%일 때만 증설 정당화"는 이 도구 출력으로는 어떤 공장에서도 도달 불가능한 문턱이고, §12-0 "두 방법이 다르면 그 자체가 정보"는 도구 결함을 해석으로 포장한 문장이다.

**power_profile은 §2.7 요금 구조를 구현하지 않는다.** 구현된 것: 시간대 단가 3밴드, 주말 mid 50% 할인, `demand_charge = demand_krw_per_kw × max(peak, contract×0.3) × days/30`. 미구현: 요금적용전력(당월·직전 11개월 중 하계·동계 최대수요 — 입력 자체가 없음), 역률 ±0.2%/1%, 계약전력 초과 150~200% 할증, 계절별 단가(여름·겨울 vs 봄·가을), 기후환경 9원·연료비 5원·부가세·기반기금, 선택Ⅰ/Ⅱ/Ⅲ 동시 계산. 주말 할인은 "봄·가을 11~14시"가 아니라 연중 전 주말 mid 밴드에 적용. 더 근본적으로 §2.7 전체가 **산업용(을)(300 kW 이상)** 단가인데 10~20인 가구공장은 대개 300 kW 미만 → 산업용(갑)Ⅰ(저압이면 계시별 아님 — 18~21시 회피 논의 자체가 무의미) 또는 (갑)Ⅱ. research 16 §1-3 표가 이미 (갑)Ⅰ/Ⅱ를 구분하는데 명세서는 (을)만 적었다.

**Kingman 사전 스크리닝 vs 시뮬.** 샘플에서 assemble u=0.99, bore 0.97, pack 0.86(증설 후보)인데 시뮬 util은 ASM 0.39~0.53, BOR 0.39~0.43. 20일 horizon에서 주문 255건 중 **144건만 투입**(시공일 역산 D-2 + 5일 워밍업)되어 정상상태 창이 사실상 없다. 샘플 민감도·불확실성·비교표가 모두 이 과도 구간에서 나온 수치다. §12-0 "체제별 30회" 전에 horizon을 늘려야 한다.

**기타 수치·참조.** §0-6 "4명이면 스캔을 오전 전담 **2명**" vs §5 "S2를 빼고 스캔을 **S1** 오전 전담". §2.2.1 "변환기가 회귀한다"는 런닝쏘(컷·스트립 수)·CNC(둘레·툴)·6면드릴·조립(조인트·하드웨어 수)에 대해 시트 4에 입력 열이 없어 성립 불가 — edge·bore만. §8-5a "적격 집합(손실 최소 +2 이내 전부)으로 보고", 06 부록 "적격 집합", 00 "규제 보정(적격 집합)" — `calibrate.py`는 argmin 하나만 출력. §8-7 "record ±10%, interview ±20%, estimated ±30%"는 `uncertainty.WIDTH`와 일치하지만 `calibrate.WIDTH = {measured .10, record .15, interview .25, estimated .40}`로 다름. test_chain의 스코어카드 "전체 신뢰 점수 0.00 / estimated 174"는 변환기가 `provenance`를 전혀 쓰지 않기 때문 — 시트 4 n=11 측정도 `estimated`로 집계된다.

---

### 3. 코드 버그·취약점

**`tools/templates_to_json.py` 엣지 물리항.** `feed_terms = [(o["edges"] * gap) / vf for o in obs]`는 G 항만 빼고 **L_edge/v_f를 빼지 않는다**(시트 4 "부품/제품 치수(mm)"를 읽지 않음). 잔차에 남은 이송시간이 γ1·γ0에 흡수된 뒤 `per_unit.edges_m = 1/vf`로 다시 더해져 시뮬에서 **이송시간 이중 계상**. 샘플 채움본은 v_f가 비어 이 분기를 타지 않으므로 test_chain이 검증하지 못한다(EB1은 일반 회귀, EB2는 `b > 0 and a >= 0` 실패로 `per_unit {}`). `obs` 초기값은 측정#의 **첫 행**의 엣지·홀 수를 쓰므로 핸들링 행이 먼저 오면 0. `k = (r["기계ID"], r.get("측정#") or id(r))`는 일시 객체 id를 키로 씀(재현은 안 됐으나 보장 없음). 시트 8 처리 뒤 "투입 규칙 D-2 는 기본값" 가정 메시지가 시트 16이 D-3으로 덮어써도 남는다.

**`sim/calibrate.py`.** 식별성은 `if len(a.params) > len(targets)`면 **경고만 하고 계속** 실행. 벌점 `reg = lam * sum((m - 1) ** 2 …)`는 §8-5a "λ·Σ((θ−θ_meas)/se)²"가 아니라 se 무관 — n=30 측정값과 추정값이 같은 벌점. 손실은 `/sd_k` 없이 상대오차. 홀드아웃은 `Sim(cur, seed=99)` **단일 실행**(리드타임 sd가 평균의 9%). `set_param`이 `buffer_batches`(int) 같은 키를 float로 바꿔 simpy capacity 오류 가능. 적격 집합 미구현.

**`sim/uncertainty.py` 재표집.** 측정 파라미터는 `gauss(0, cv/√n)` — 하루 오후 10사이클(자기상관·단일일)에 iid 가정, base_min·per_unit을 **같은 배수**로 흔들어 회귀계수 불확실성 무시. 흔들지 않는 것: `orders.batch_size`(민감도 **1위**), `orders_per_day`, `mix`, `install_lead_days`, `buffer_batches`, `mtbf`. B=10에서 `ci()`는 index 0과 8 → "95% 구간"이 사실상 min과 9번째 값; P(개선)≥0.9 기준은 10회 중 9회라 해상도 한계에 걸림. 부트스트랩마다 seed가 바뀌어(`seed = 100 + b`) σ_I²와 σ²/n이 섞인다(§8-7이 분리를 약속).

**`sim/queueing_prescreen.py` u 계산.** 배치당 시간 = per_part × qty(assemble/pack은 `per_product[pid] * qty`), 셋업 = `setup_min * 0.7`(전환 확률 상수), `c0 = cv²`는 **부품 1개**의 CV를 배치(부품 6~10개 합)에 그대로 적용 → c_e² 과대. λ는 전 주문이 투입된다고 가정, 시뮬은 시공일 역산으로 일부만 투입 — §2 괴리의 절반은 여기서. 재단 배치 묶음(`cut_key=color_thickness`)이 바꾸는 배치 크기 무시.

**`sim/bottleneck_active_period.py` 그룹화.** 위 §2에 더해: `overl` 조건 `c[2][0] < top[2][1] and c[2][1] > top[2][0]`는 두 구간이 모두 현재 t를 포함하므로 **항상 참** → 이동 병목 판정은 "길이 > 0.5×최장"만으로 결정. Roser 정의(최장 활성기간의 시작·끝이 인접 활성기간과 겹침)와 다르다. `clip`이 야간에서 활성기간을 자르므로 길이가 교대 길이로 상한. 그룹 키가 `process`라 EB1(반자동)·EB2(자동)처럼 호환 안 되는 기계도 "둘 다 busy"일 때만 활성.

**history 모드 요일 오프셋.** `off = d0.weekday(); day = (d - d0).days + off`는 요일 정합 자체는 맞다. 그러나 `self.horizon`을 **generator 안에서** 늘리는데 `run()`은 이미 `env.run(until=self.horizon)`(옛 값)으로 시작됨. 실측(`sample_from_template.json`, `mode=history`): `horizon_days 26`, 마지막 이벤트 **18.7일**, 즉 7일은 돌지도 않았는데 `worked_minutes(horizon)`·`steady_days`는 26일로 나눠 처리량·가동률이 과소. 주말 시공일(due)에 대한 역산은 되지만 `d % 7 < 5` 하드코딩이라 6일제 공장은 틀린다. 변환기의 `history_list` 날짜는 `"2026-09-01 00:00:00"` 문자열 — `[:10]` 슬라이스에 의존. 시트 13(생산 리드타임·셋업 횟수의 선언된 출처)은 어떤 도구도 읽지 않는다.

---

### 4. 명세서의 과잉/과소 — 하루 방문 팀이 읽을 수 있는가

03은 56,883자(§2만 15,303자, §5 6,159자, §6+6.1 5,328자)다. 현장에서 실제로 읽는 문서는 05 카드(5,884자)뿐이고, 05는 §5만 요약한다. 03의 §2.2.1(기계별 회귀 형태·기본 계수), §2.7(요금 구조), §6.1(카메라 기하·오차식·법리), §7(기록 복원), §8-5a~7(식별성·CRN·OCBA), §9, §10, §12는 **방문 당일에 아무도 쓰지 않는** 분석 설계 내용이다. 반면 당일에 꼭 필요한 것이 흩어져 있다: "오늘이 평소와 어떻게 다른가"(§3·§5·시트 12), 투입·출하 각각 세기(§5 16:30), 셋업 발생 시 최우선 관찰(05 T), 센서스는 검증 전용(§5 하단), 클램프는 D0(§5 전제), 촬영 협의·동의 없으면 촬영 금지(§6.1 끝). 현재의 §0 "한 장 요약"은 합격 기준 숫자 나열이라 현장용이 아니다.

제안: 03을 세 층으로 분리. (A) **1장 현장 요약**(§0 대체): 당일 산출 8가지(스캔·제어 치수, 기계 폴더, 사이클 ≥10/병목 후보, 셋업 1회, 센서스 3회, 배치 추적 2~3건, 규칙 IF-THEN ≥10개, 전력 카운터 2회) + 절대 규칙 5개 + "하지 않는 것"(REBA·야마즈미·클램프·반장 근무 중 인터뷰). (B) **본문**: §1(합격 기준), §3, §5(+5.1), §11, §14. (C) **부록**: §2.2.1, §2.7, §4, §6, §6.1, §7, §8, §9, §10, §12, §13 — 분석 담당만 읽는다. §2.1~2.6 표는 각 행에 "당일/2주/기록" 열과 "모델 반영 v0.5/v1" 열(리뷰 11 #5)을 넣어 현장용으로 절반 이하로 줄인다.

---

### 5. 우선순위 수정 제안 10개

1. **[sim/factory_sim.py `gen_orders` history 분기]** generator 안에서 `self.horizon`을 늘리지 말고 `Sim.__init__`에서 `history_list`로 horizon을 먼저 계산하거나, `run()`이 `until`을 generator 실행 후 결정하도록 변경. 함께 `d % 7 < 5` 5곳(주문 생성·투입 역산·steady_days·power_profile.working·bottleneck clip)을 `Shift.working()`으로 통일.
2. **[sim/bottleneck_active_period.py]** 활성 판정을 "자원 포화"로 재정의: 단일 스테이션은 `res.count == capacity`(state 이벤트에 점유 수 추가), 그룹은 전 기계 포화. `overl` 조건을 Roser 정의(최장 구간의 시작/끝에 인접 구간이 겹침)로 고치고 sole+shift가 100% 분할이 되게. §12-0의 "다르면 그 자체가 정보" 문장 삭제, §12-1 60% 문턱은 수정 후 샘플로 재보정.
3. **[tools/make_templates.py 시트 18, sim/factory_sim.py kpis]** `setups_per_day`(setup 이벤트/근무일), `lead_time_work_min_p90`, `products_completed_steady`(워밍업 제외, 기간 명시) 키를 추가하고 시트 18 행에 채운다. §1.2 표에 "KPI 키" 열을 넣어 키 없는 행(게이트 통과·구역별 WIP)은 "수동 대조"로 표시.
4. **[sim/factory_sim.py kpis energy / sim/power_profile.py]** 전력 kWh를 한 경로로: kpis의 ×1.3 근사를 제거하고 `power_profile`의 15분 합을 `energy.total_kwh`로 되돌려 쓰거나, §1.2·시트 18이 `power_summary.kwh_total`을 가리키게. 두 값 차이 21%를 00·03에 명시.
5. **[docs/03 §2.7, sim/power_profile.py]** 계약종별 선택(산업용(갑)Ⅰ 저압·(갑)Ⅱ·(을))을 `meta.energy.tariff_class`로 입력받고, 계절 밴드·역률·초과 할증·부가 요금·선택Ⅰ/Ⅱ/Ⅲ 동시 계산을 구현하거나, §2.7을 "구조 설명(미구현)"으로 정직하게 표기. 주말 할인을 봄·가을 11~14시로 제한.
6. **[docs/03 §13]** 납기 디스패칭·상류 재작업·대차 제약·15분 전력을 "구현"으로, 요일·잔업을 "부분(Shift만)"으로, 출하 용량은 "변환기 수집만(`shipping`), 시뮬 미사용"으로 수정. 리뷰 11 #5대로 §2 표에 열로 흡수해 §13을 없앤다.
7. **[tools/templates_to_json.py 엣지 분기]** 시트 4에 "엣지 길이 합(m)" 열(또는 치수 파싱)을 추가해 `feed = Σ(L+G)/v_f`를 관측치에서 빼고 γ만 회귀; 측정# 첫 행 의존 제거(행별 max). 시트 23 대차 `수량` → `transport.carts`, 운반 인원은 시트 6 역할에서. `provenance`를 자동 생성(시트 4 n≥10 → measured, 시트 8 → record, 시트 16 → interview, 기본값 → estimated). 시트 8이 있으면 `orders.mode`를 CLI 옵션으로 `history` 전환.
8. **[sim/calibrate.py, sim/uncertainty.py]** WIDTH 상수를 공용 모듈로 통일(§8-7 수치), 벌점을 `((m−1)/se_rel)²`로, 파라미터 수 > 지표 수면 중단, 손실 최소 +2 이내의 평가점 집합을 "적격 집합"으로 출력. uncertainty는 `orders.batch_size`·`orders_per_day`·`buffer_batches`를 흔들고, B≥50 기본값, 부트스트랩 복제 내 seed 고정으로 σ_I² 분리.
9. **[sim/queueing_prescreen.py]** c_e²를 배치 단위(cv²/n_parts)로, λ를 투입률(시공일 역산 반영 또는 `orders_released` 기반)로, 재단 묶음 배치 크기 반영. 샘플 비교표·민감도는 horizon 60일로 재실행해 §10·§8-7 수치를 갱신.
10. **[docs 일관성]** §14·01 §0 "시트 0~24", 01 §2 옛 A/B/C/D 표 삭제(§5로 대체), 01 §0 "3명이면…" 삭제, §0-6↔§5 4인 스캔 인원 통일, §3 "5~10"→"≥10", §4·§2.7의 독자 허용 오차를 §1.2 참조로 바꾸고 단계 표시, 00 §59 "±10%"·02 §15 "12 시트" 수정, 03을 §4 제안대로 1장 요약/본문/부록으로 재편.

(파일은 수정하지 않았음. 실행 로그는 `/tmp/claude-0/-home-user-claude-mem/508c8abb-4a55-5c43-94f1-9a63dde73d06/scratchpad/test_chain.log`.)