# 납품 이후 트윈을 "살아 있게" 유지하기 — 드리프트, 재검증, 최소 데이터 인프라, 변경관리, 다공장 확장, 상업적 현실

**작성 기준일 2026-10-10. 조사 범위와 한계:** 웹 검색은 정상 동작했으나 이 세션의 송신 프록시가 거의 모든 원문 페이지(중기부·bizinfo·korcham 공고 PDF, arXiv, informs-sim, 국내 언론)의 직접 열람을 차단했다. 따라서 아래 수치는 검색 요약(스니펫)과 공고 제목·요약, 그리고 기존 저장소 리서치(`docs/research/05`, `14`)에 의존한다. **[확인]** = 출처 스니펫에서 직접 확인한 사실, **[추정]** = 내 추론·경험칙, **[원문 확인 필요]** = 공고 원문으로 재확인해야 하는 수치. 저장소 구조(`factory.json`, `sim/validate.py`, `sim/calibrate.py`, `sim/sensitivity.py`, `capture/sensing/esphome_ct_clamp.yaml`)와 맞물리도록 설계안을 썼다.

---

## 0. 요약 (10줄)

1. 트윈 드리프트는 "있느냐"가 아니라 "얼마나 빨리, 어떤 종류로"의 문제다. 10~20인 맞춤가구 공장에서는 **입력 드리프트(주문 믹스·계절)는 주 단위, 파라미터 드리프트(사이클·셋업·불량·인력 숙련)는 4~12주, 구조 드리프트(기계·배치·규칙·인원)는 분기~연 단위**로 일어난다 [추정, 근거는 §1].
2. 드리프트 탐지의 표준은 ML 모델 모니터링과 같다: **예측 잔차(실측−트윈 예측)에 관리도(I-MR/EWMA)와 CUSUM/Page-Hinkley**를 걸고, 입력 분포에는 ADWIN/PSI, 그리고 업데이트 채택 전에는 **검정 게이트(Mann–Whitney U, 홀드아웃)**를 둔다 [확인: arXiv 2607.18164, IoT 벤치마크, Sürer et al. WSC 2025].
3. 상시 로깅은 **7개 신호**로 족하다: ① 병목 2~3대 전류 클램프, ② 일일 재단 장수(네스팅/재단표 사진), ③ 수주·출고 내보내기(세금계산서/이카운트/엑셀), ④ 주간 A4 한 장 양식, ⑤ 화이트보드 사진, ⑥ 한전 고지서/파워플래너 15분 데이터, ⑦ 변경 로그. 공장 측 부담은 **하루 3분 + 주 10분**이어야 유지된다.
4. 월간 점검은 **8개 KPI를 트윈의 90% 예측대(복제 CI + 입력불확실성 σ_I)와 비교**하고, 2개월 연속 이탈 또는 CUSUM 경보 → **재보정**, 변경 로그에 구조 항목 → **재구성**. 공장 측 30분/월, 컨설턴트 2시간/월 원격, 분기 1회 방문.
5. MES 없는 공장의 현실적 최소 인프라는 "종이+사진+카톡 → 컨설턴트 측 구조화"이며, 비용은 **0~월 4만 원**(이카운트 수준). 클라우드 MES 공개 요금은 국내에서 사실상 비공개다.
6. 2026년 정부 사업은 **정부형(한도 2억, 50%, 9개월, 제조DX멘토단 필수)**, **상생형(기초 사업비 약 4,230만·정부 30%·대기업 30%·자부담 40%)**, **지방형 기초(포항 60%, 최대 6천만, 6개월)**, **제조AI특화 '데이터 수집·검증'(최대 0.5억, 6개월, 목표수준 없음)**, **수준확인(전액, 100만 원, 2,000개사)**로 구성된다 [확인, 세부는 원문 확인 필요]. 트윈은 "데이터 수집·검증" 과제 또는 기초(지방형·상생형)의 데이터 수집 산출물로 넣는 것이 가장 자연스럽다.
7. 변경관리는 **`factory.json` 시맨틱 버전(구조=MAJOR, 재보정=MINOR) + 변경 로그 JSON + 분기 as-built 감사**로 충분하다. 변경 효과 평가는 시뮬레이션에서는 **CRN 짝지은 t**, 현실에서는 **단절 시계열(ITS) 분할회귀**를 쓰되, 트윈의 "구(舊) 설정 반사실 예측"을 대조군으로 쓰면 루프가 닫힌다.
8. 다공장 확장에서 옮겨지는 것은 **공정 위상·기계 클래스별 사이클 모델·셋업 구조·물리 상수·계절성 형태**이고, 절대 옮겨지지 않는 것은 **레이아웃·비공식 규칙·병목의 정체·스킬 매트릭스·제품 믹스·사장의 목적함수**다.
9. 이전 공장의 사전분포는 **민감도 하위 파라미터에만, 넓은 분산으로, 유효표본수를 명시하고** 써야 한다. KOH 보정 파라미터는 예측이 맞아도 값 자체는 불안정하다(Tuo & Wu 2016)는 점이 핵심 주의사항이다.
10. ROI 근거는 약하다. 완료된 DT 프로젝트 손익분기 2년 미만(영국 99개 응답, 국방 편중), 비용이 최대 저해요인(ABI 2026), 시뮬레이션은 대기업에서도 "상시 의사결정 지원"으로 거의 쓰이지 않는다(2010 아일랜드). 사장이 실제로 쓰는 것은 **실측 대시보드(매일)와 결정 시점의 시나리오 메뉴(연 2~4회)**이며, 지속되는 납품 형식은 "소프트웨어"가 아니라 "월 1장 리포트 + 결정 메뉴 + 카톡 푸시"다 [추정].

---

## 1. 트윈 드리프트: 증거, 시간 척도, 탐지

### 1-1. 드리프트가 일어난다는 증거

- **개념 드리프트(ML)**: Gama, Žliobaitė, Bifet, Pechenizkiy, Bouchachia (2014) *A survey on concept drift adaptation*, ACM Computing Surveys 46(4), DOI 10.1145/2523813 — 입력과 목표의 관계가 시간에 따라 바뀌는 현상을 정의하고 적응 전략을 분류 [확인]. 드리프트 유형은 급격(sudden)·점진(gradual)·증분(incremental)·재발(recurring)으로 나뉜다 [확인, 프로세스 마이닝 문헌에서도 동일 분류: Kraus & van der Aa, CV4CDD-4D; Vienna 대학 드리프트 특성화 논문].
- **프로세스 드리프트(프로세스 마이닝)**: Bose, van der Aalst, Žliobaitė, Pechenizkiy의 "Dealing with concept drifts in process mining"(IEEE TNNLS 2014) 계열과 Martjushev–Bose–van der Aalst의 점진 드리프트·"2차 동역학(분석 중에 프로세스 자체가 바뀜)" 연구 [확인: vdaalst.com p822]. 제조 센서 스트림 기반 드리프트 원인 추적(Vienna, Du et al.) [확인]. 즉 "현실 프로세스는 로그를 분석하는 동안에도 바뀐다"는 것이 학계의 기본 전제다.
- **디지털 트윈 고유 증거**:
  - arXiv 2505.11847 (2025, *Bridging the Reality Gap in Digital Twins…*): 트윈이 현실과 벌어지는 원인을 (a) 신규 센서 데이터의 비체계적 통합, (b) 드리프트 미탐지, (c) 이력 지식 미보존, (d) **컨텍스트 불일치**(물리 시스템의 운영 조건·수명 단계가 트윈 가정과 어긋남)로 정리 [확인].
  - arXiv 2607.18164 (2026, Northwestern, *A Continual Validation, Updating, and Decision-Making Framework for Self-Adaptive Digital Twins…*): 서로게이트의 개념 드리프트를 Fisher score 기반 탐지기로 잡고, 1% 미만 파라미터만 LoRA 미세조정한 뒤 **Mann–Whitney U 검정으로 "업데이트가 실제로 정확도를 개선했는지" 확인하고서야 배포**. 사례(적층제조)에서 첫 업데이트 시도는 검증에 실패하고 두 번째만 통과 → 탐지기 리셋 [확인]. "업데이트가 항상 개선은 아니다"는 실증.
  - Twintinuum (암스테르담대, 네트워크 트윈): 동기화 지연과 지속 보정의 통신 비용 때문에 물리–디지털 간 괴리가 **누적적으로 커진다**; 불확실성 유도 자가보정을 제안 [확인, pure.uva.nl].
  - KBC(정유 트윈 블로그): 수동 재보정은 변화 속도를 못 따라가므로 주기적 재보정 → 지속적 수명주기 관리로 가야 한다 [확인, 벤더 자료].
  - NTNU 보정 노트: 측정되지 않은 센서 드리프트가 공정-모델 불일치로 전파된다 [확인].
  - Engineering News (2026-01-13, *Don't let the digital twin drift from reality*): as-built 데이터가 설계 시스템으로 되돌아가는 일이 드물어 운영·유지 단계에 이르면 모델은 이미 구식 [확인].
  - Sürer, Chen & Shashaani (WSC 2025, *Dynamic Calibration Framework for Digital Twins Using Active Learning and Conformal Prediction*): 새 데이터 배치가 트윈 예측대 밖에 떨어질 때만 θ를 재추정 [확인, 저장소 `docs/research/14`].
- **시뮬레이션 모델 유지의 고전적 증거**: WSC 2001 논문은 "정확한 시뮬레이션 모델을 유지하는 비용(갱신에 드는 공수)이 설계 단계 이후의 활용을 막는다"고 명시 [확인]. WSC 2002 논문은 제조 시스템의 수명주기가 제품 수명보다 훨씬 길어 모델이 만든 사람이 아닌 사람에 의해 갱신 가능해야 한다고 주장 [확인]. Chalmers 2023 석사논문은 트럭 공장 DES 모델의 유지보수성을 위해 조직적·기술적 프레임워크 두 개를 제안 [확인]. 아일랜드 7개 다국적 기업 조사(2010, U. Limerick, *Barriers to the application of simulation for tactical decision making*)는 시뮬레이션이 **상시 의사결정 지원으로는 거의 쓰이지 않으며** 소유비용을 낮추는 프레임워크가 필요하다고 결론 [확인].
- **인력 교체의 효과**: Twente 대학 학습곡선 자료는 이직이 생산성을 떨어뜨리고 일부 공장은 학습효과가 거의 없다고 지적하며 이를 이직·지식전수 실패와 연결 [확인]. Applied Sciences(2021) 램프업 논문은 인적 요인이 변동·불안정을 추가하며 보통 데이터가 없어 평가에서 빠진다고 지적 [확인]. 조립·검사 작업장의 램프 4~8주는 벤더 수치 [확인, 근거 약함].

**결론 [확인+추정]**: "시간이 지나면 트윈 정확도가 얼마나 떨어지는가"를 여러 시스템에 걸쳐 정량화한 종단 연구는 찾지 못했다. 존재하는 것은 (i) 드리프트 메커니즘의 분류, (ii) 탐지·갱신 프레임워크, (iii) "유지비 때문에 버려진다"는 반복되는 관찰이다. 따라서 시간 척도는 추론할 수밖에 없다.

### 1-2. 가구 공장용 드리프트 분류와 시간 척도 [추정]

| 드리프트 유형 | 예 | 전형적 시간 척도 | 트윈에서의 위치 (`factory.json`) | 대응 |
|---|---|---|---|---|
| **입력 드리프트** | 주문 믹스(책상↔붙박이장), 일일 주문수, 설치일 리드, 이사철·신학기 피크, 납기 독촉 비율 | 주~월(계절성은 연 주기 재발형) | `orders.mix`, `orders_per_day`, `install_lead_days` | 입력만 갱신(재보정 아님) |
| **파라미터 드리프트** | 사이클·셋업 시간(새 작업자 숙련, 톱날·엣지 접착제 상태), 불량·재작업률, MTBF/MTTR, 운반 속도 | 4~12주(점진), 기계 고장은 급격 | `stations[].cycle/setup_min/scrap_rate/mtbf_min`, `transport.*` | 재보정 |
| **구조 드리프트** | 기계 추가·교체·이동, 공정 순서 변경(선도장), 배치 규칙 변경("색상별 모아서"), 외주 전환, 인원 증감·재배치, 교대·잔업 규칙 | 분기~연, 사건형 | `stations[]`, `products[].routing`, `orders.batching`, `workers[]`, `outsourced[]`, `meta.shift` | 재구성 + 재검증 |
| **목적 드리프트** | 사장의 KPI 우선순위 변화(납기→원가→인력난) | 반기~연 | 시나리오 세트 | 시나리오 메뉴 갱신 |

근거: 개념 드리프트 분류(Gama 2014), 컨텍스트 불일치(arXiv 2505.11847), 학습곡선·이직(Twente, Applied Sciences 2021), 저장소 `docs/research/10`의 가구 공장 운영 실태(성수기 패턴·E-9 인력 교체). **비공식 규칙 변화**("요즘은 엣지 먼저 다 치고 보링한다")는 기록되지 않은 채 몇 주 안에 정착하므로 가장 위험한 드리프트다 [추정].

### 1-3. 탐지 방법 — 확립된 도구와 소규모 공장용 선택

| 방법 | 무엇을 보나 | 확립 근거 | 소규모 공장 적합성 |
|---|---|---|---|
| **재검증 주기(cadence)** | 정해진 주기에 Sargent식 운영타당성 재점검 | Sargent (2013) *Verification and validation of simulation models*, J. Simulation 7(1):12–24; Sargent–Goldsman–Yaacoub WSC 2016 튜토리얼: 타당성은 **목적별·질문별**로 판정 [확인] | 월간 경량 + 분기 정밀 |
| **잔차 관리도** | R(t)=실측−트윈예측에 I-MR/Shewhart(큰 이동), EWMA(작은 이동), CUSUM(빠른 탐지) | arXiv 2204.06688(잔차 I-MR 차트); Berkeley EE290H 모델기반 SPC(예측 잔차 회귀 차트); 김종걸·김동녘 2012(Shewhart/CUSUM/EWMA 비교) [확인] | 월 1점이면 n이 작으므로 **주간 KPI 잔차**에 적용 |
| **CUSUM / Page-Hinkley** | 예측오차 평균 변화의 순차 탐지 | IoT 스트림 벤치마크에서 CUSUM이 가장 강건, 라벨 오류 40% 미만까지 안정 [확인]; 파라미터 예(허용치 0.5σ, 결정구간 5σ, PH 경보 3σ√w)는 구현마다 다름 [확인] | 적합, 주간 처리량·리드타임 잔차 |
| **ADWIN / PSI·KS** | 입력 분포 변화(믹스, 사이클 샘플) | ADWIN은 δ 하나만 설정(기본값 0.002 또는 2e-5로 라이브러리마다 상이) [확인] | 믹스·주문수에 적합 |
| **컨포멀 예측대** | 새 배치가 예측대 밖인지 | Sürer et al. WSC 2025 [확인] | 저장소 `uncertainty.py`의 CI와 결합 |
| **업데이트 채택 게이트** | 재보정 후 홀드아웃에서 실제 개선됐는지 | arXiv 2607.18164(Mann–Whitney U) [확인]; `sim/calibrate.py --holdout` | 필수 |
| **합의(consensus)** | 복수 탐지기 동시 경보 | 실무 가이드 권고 [확인, 표준 아님] | CUSUM + 관리도 동시 |

**주의 [확인]**: 자기상관된 공정 데이터에 Shewhart/EWMA를 그대로 쓰면 오경보가 크게 늘어난다(TFT-LCD 연구는 AR(1) 잔차 차트로 완화). 주간 KPI는 주문 잔고 때문에 자기상관이 강하므로, 잔차를 **트윈 예측 대비**로 만들면(트윈이 잔고를 반영) 상당 부분 제거된다 [추정].

---

## 2. 소규모 공장용 재검증 프로토콜

### 2-1. 영구 로깅 신호 7개 (싸고, 자동이거나 하루 3분)

| # | 신호 | 수집 방법 | 비용 | 트윈 파라미터/검증값 | 드리프트 탐지 용도 |
|---|---|---|---|---|---|
| 1 | **병목 2~3대 전류** (CNC/판넬쏘, 엣지밴더, 보링) | 저장소 `capture/sensing/esphome_ct_clamp.yaml` + `states_from_current.py` 그대로 상설화; ESP32+SCT-013 계열 | 채널당 2~5만 원 하드웨어 [추정], 상용(HARDWARIO CHESTER, Fitfactory, TeepTrak) 월 구독형 [확인, 가격 비공개] | 가동/유휴/정지 시간, 사이클 수(전류 서명), MTBF/MTTR, kW | 가동률·사이클 잔차, 고장 급변 |
| 2 | **일일 재단 장수·주문 건수** | 네스팅 SW 출력/재단표를 **매일 1장 사진**(카톡 그룹) → 컨설턴트 측 구조화 | 0 | 처리량(장/일), 배치 크기 | 처리량 잔차 |
| 3 | **수주·출고 내보내기** | 세금계산서/이카운트/엑셀 월 1회 export (수주일·약속 설치일·출고일·금액·품목군) | 0~월 4만 원(이카운트 2024 기사 기준) [확인] | 주문수·믹스·리드타임·납기준수율 | 입력 드리프트(ADWIN/PSI), 리드타임 잔차 |
| 4 | **주간 A4 한 장 양식** | 요일×공정 인원, 잔업 시간, 결근, 외주 건, 재작업 건, 30분 이상 고장(원인), 그리고 **"이번 주 바뀐 것" 빈칸** | 0, 주 10분 | `workers[]`, `scrap_rate`, `mttr`, 변경 로그 씨앗 | 구조 드리프트의 조기 신호 |
| 5 | **화이트보드·대차 사진** | 아침 1장(일정판), 오후 1장(대차 적치) | 0 | WIP(대차 수), 진행 순서 | WIP 잔차, 규칙 변화 |
| 6 | **전기** | 한전 고지서(월) + 파워플래너 15분 데이터(가능 시) | 0 | kWh/장, 최대수요, 시간대 비중 | 에너지 트윈 교차검증(§저장소 `power_profile.py`) |
| 7 | **변경 로그** | §4 양식(종이·카톡·구글폼 어느 것이든) | 0 | 버전 트리거 | 재구성 트리거 |

선택 사항(공장이 원할 때만): 대차 QR 2지점(재단 출고·조립 투입) 스캔 — 리드타임 분포를 직접 준다. 그러나 작업자 준수율이 핵심 리스크(§3-3).

### 2-2. 월간 점검 (누가·무엇을·허용오차)

**역할**: 공장 측 1인(사무 담당 또는 사장) 30분 — 3·6번 export와 4·7번 양식 사진 전송. 컨설턴트 2시간 원격 — 구조화, 트윈 1개월 재실행(실제 주문 스트림 입력), 잔차 계산, 한 장 리포트 발송. 분기 1회 반나절 방문(§4-3 as-built 감사).

**비교 KPI 8개와 허용대** [추정, 저장소 `sim/validate.py`의 합격 판정 구조 재사용]:

| KPI | 실측 출처 | 1차 허용대(보정 상태 양호) | 근거·비고 |
|---|---|---|---|
| 처리량(장/일, 주문/주) | 2, 3 | ±10% 또는 트윈 90% 예측대 | 문헌에 표준 임계는 없음; 사례들은 5%(구급차 DES), 6%(반도체 처리시간) 수준 [확인]. 2주 로깅 기반 트윈은 입력불확실성이 크므로(저장소 14: σ_I가 복제오차의 3~4배) **예측대 기준**이 더 정직 |
| 리드타임 P50 / P90 | 3 (+5) | P50 ±15%, P90 ±25% | 꼬리는 소표본에서 불안정 |
| 납기준수율 | 3 | ±5 %p | |
| 병목 가동 시간(일) | 1 | ±10 %p | 전류 기반, 가장 신뢰 |
| 사이클·셋업 중앙값(병목) | 1 | ±15% | 숙련·공구 상태 |
| 잔업 시간/주 | 4 | ±20% | 사장이 가장 체감 |
| WIP(대차 수) | 5 | ±2대 | 사진 카운트 |
| kWh/장, 최대수요 kW | 6 | ±10% | 한전 고지서로 절대값 검증 |

**판정 규칙** [추정, §1-3 도구 조합]:
- 각 KPI의 **주간 잔차**에 CUSUM(허용치 0.5σ, 결정구간 4~5σ; σ는 보정 직후 8주로 추정)과 EWMA(λ=0.2)를 함께 걸고, **두 탐지기 동시 경보** 또는 **월간 KPI가 2개월 연속 허용대 이탈** → 재보정.
- **입력 드리프트만**(믹스·주문수가 ADWIN/PSI 경보, 그러나 믹스를 반영한 트윈 예측 잔차는 정상) → 재보정 불필요, 입력 파일만 갱신.
- **변경 로그에 구조 항목**(기계·배치·순서·규칙·인원 변화) → 즉시 재구성(MAJOR 버전), 재보정 여부와 무관.
- 재보정 후에는 반드시 **채택 게이트**: 보정에 쓰지 않은 최근 4주 홀드아웃에서 Mann–Whitney U(또는 짝지은 부호검정)로 잔차 절대값이 줄었는지 확인; 실패 시 이전 버전 유지(arXiv 2607.18164의 교훈).

### 2-3. 재보정 vs 재구성 결정표

| 관찰 | 조치 | 산출물 |
|---|---|---|
| 처리량·가동률 잔차 편향, 구조 변화 없음 | **재보정**: 민감도 상위 10개(`sensitivity.py`) 중 전류·양식에서 재측정 가능한 것부터 `calibrate.py` 규제 보정 | MINOR 버전, 잔차 리셋 |
| 리드타임만 이탈, 처리량 정상 | 우선 **입력·규칙 점검**(우선순위 규칙 변화, 외주 지연) → 규칙 변화면 재구성 | 변경 로그 등재 |
| 기계 추가·이동, 공정 순서 변경 | **재구성** + 2주 미니 로깅 + 재검증 | MAJOR 버전, 신규 기준선 |
| 인원 교체(핵심 1인) | 4~8주 **학습곡선 모드**(사이클 ×1.2→1.0 선형) 가정 후 재측정 [추정] | MINOR |
| 사장 목적 변화 | 시나리오 메뉴 재작성 | 시나리오 패치 |
| 12개월 경과 | 조치 없더라도 **연간 정밀 재검증**(2주 로깅) — "유효기간" 명시 | 재인증 리포트 |

---

## 3. MES 없는 공장의 최소 지속 가능 데이터 캡처

### 3-1. 국내 옵션과 현실 비용

| 옵션 | 무엇을 주나 | 비용(공장 부담) | 근거 | 트윈 적합성 |
|---|---|---|---|---|
| 종이 양식 + 스마트폰 사진 + 카톡 그룹 | 재단표·화이트보드·주간 양식 | 0 + 하루 3분 | — | ★★★ 가장 지속됨; 구조화는 컨설턴트 몫 |
| 구글 시트/폼 + AppSheet | 현장 입력 → 시트 DB; 10인 이하 무료 플랜 사례 | 0~수만 원/월 | 크몽 서비스 설명 [확인, 광고성] | ★★ 입력 준수율이 관건 |
| 이카운트 ERP(생산관리 포함) | 수주·출고·재고·생산 실적; 단일 요금제 | **월 4만 원** 수준, 가입비 20만 원(제3자 사이트) | fnnews 2024 [확인], 비교 사이트 [신뢰도 낮음] | ★★★ 3번 신호의 가장 싼 공식 출처 |
| 사진 OCR(재단표·작업일지) | 텍스트 추출 | 0~ | 국내 사례는 재고 라벨(OpenCV+Tesseract, Vision API) 뿐 [확인]; 손글씨·수기 수정 많은 현장 양식은 템플릿 없이는 어렵고 범용 모델 90~95%는 표준 문서 기준(벤더 주장) [확인] | ★ 손글씨 재단표 OCR에 기대지 말고 **네스팅 SW 출력 화면**을 찍게 할 것 |
| 대차 QR/바코드 2~3지점 | 리드타임·WIP 직접 | 스마트폰 스캔 앱 0~, 라벨 프린터 10~30만 원 [추정] | — | ★★ 공정이 안정된 곳에서만 |
| 전류 클램프(저장소 키트/상용) | 가동·사이클·고장·kW | 채널당 2~5만 원 [추정] 또는 월 구독 | 벤더 자료: 비침습, 수 분 설치, PLC 불필요, 품질은 못 잡음 → 수기 불량 입력과 병행 [확인] | ★★★ 1번 신호 |
| 저가·클라우드 MES(더존 MES10 Edge 라이트, 아이티컴, 각종 공급기업) | 작업지시·실적·추적 | **국내 월 요금은 공개 자료 없음**; 외산 대형 MES는 라이선스 5억+설치 10억 사례(2019) [확인] | kidd 2019, 2021 [확인] | ★ 10~20인 맞춤가구에는 과대 |
| 태블릿 작업지시 앱 | 전자 작업지시·실적 | 벤더 견적 | 벤더 블로그: 작업자가 피하는 디지털 양식은 품질 문제를 종이에서 태블릿으로 옮길 뿐; 정의(완료·불량의 기준) 불일치가 입력 오류보다 더 큰 손상 [확인] | ★★ 정의 먼저 |

**실태 수치 [확인, 중기부·스마트제조혁신추진단 제1차 스마트제조혁신 실태조사, 2025-04 발표]**: 공장 보유 중소·중견 163,273개사 중 스마트공장 도입 19.5%(중소 18.6%); 활용률 80% 이상이나 **부분 도입 99.8%**, 도입 기업의 **75.5%가 기초 수준**; 평균 도입비 11.3억(중소 7.5억); 도입 목적은 생산 효율(56.5%)·품질(37.1%)·비용(22.7%). 별도 설문(2024 이전)의 애로: 업무 과중으로 데이터 구축 소극 26.7%, 전문인력·유지비 각 20.0%, 공급기업 사후서비스 부실 11.7%. 의원실 조사("도입 목적대로 적극 활용")는 약 50%로, 질문이 달라 단순 비교 불가 [확인, eopla 분석].

### 3-2. 2026년 정부 지원사업 — 트윈을 어디에 끼워 넣나

| 사업 | 2026 조건 [확인/원문 확인 필요] | 트윈 포지셔닝 |
|---|---|---|
| **정부형 스마트공장 구축**(중기부, 수행 중소기업기술정보진흥원) | 통합공고 사전안내(2025-10-31): 한도 2억, 지원율 50%, 9개월; 신청 2025-12-08~2026-01-07(마감); **제조DX멘토단 컨설팅 필수**(블로그 요약); 2023년부터 고도화(중간1) 중심 기조 [확인] | 고도화 과제의 "실시간 모니터링(전류)+시뮬레이션 기반 의사결정" 모듈. 2027년 1~3월 공고 대비 |
| **대중소상생형**(대한상의·포스코, 한국도로공사 등) | 기초·고도화(동일수준 포함); 도로공사 공고: 기초 실제 구축비 4,230만, 고도화 7,120만; 정부 30%·대기업 30%·자부담 40%(기초 정부 0.15억, 고도화 0.24억) [확인] | **기초 과제로 가장 현실적**: MES-lite(이카운트/시트) + 전류 센서 + 트윈 검증 리포트 |
| **지방형 기초**(포항 등 경북, 전남, 경기) | 포항: 5개사, 60%, 최대 6,000만, 6개월; 전남: 지방비 60%(도 30·시군 30); 경북 2024: 최대 5,000만 [확인] | 동일 |
| **제조AI특화 스마트공장** | 'AI공장 구축'(최대 9개월·2억·50%·중간1 이상·기존 수준 이상 필수) / **'데이터 수집·검증'(최대 6개월·0.5억·목표수준 없음)**; 제조DX멘토단 기획지도 또는 구축지도 필수; 접수 2026-03-19~04-20; 수집·검증 완료 후 AI공장 신청은 별도 평가 [확인] | **"데이터 수집·검증" 유형이 트윈 1차 납품과 정확히 일치**(2주 로깅+기록 복원+검증 보고). 0.5억 규모가 P1 패키지(3,000~8,000만, 저장소 00 §6)와 맞음 |
| **스마트공장 수준확인** | 전액 지원, 기업당 최대 100만 원, 2,000개사; 수준확인서+고도화 전략 [확인] | 공식 Before/After 증빙. 트윈 검증 리포트의 KPI를 수준확인 항목에 맞춰 작성 |
| **소공인 스마트제조(스마트공방)** | 상시근로자 10인 미만 제조 소공인; 2026-04 개편: 공급기업 역량평가 도입, 도입장비 원가검증 강화, **자부담 30→40%**, 사업계획서 영상 제출; 국비 60%·자부담 40%, 예시 정부 3,600만/총 6,000만, SaaS 임차비 총사업비 10%(최대 600만) [확인]; 매출 요건은 출처 간 상충(2억 미만 vs 이상) [원문 확인 필요] | 10인 미만 공방에만 해당. 10~20인 대상에는 비적용 |

**공통 요구·의무 [확인/추정]**: smart-factory.kr 온라인 접수, 국세·지방세 완납증명, 사업자등록증명(3개월 이내)(전북 공고). 전담기관은 **사업완료 후 5년간** 도입기업의 구축시스템 활용도·성과 조사를 위한 사후점검·성과분석을 설문·현장방문으로 실시할 수 있다(지원사업 시행규정 제41조) [확인]. 공급기업 폐업 대비 소스 보관 '솔루션은행'(경남 2019) [확인]. 2020년 국조실·중기부 합동점검에서 담합·사업 부풀리기 사례 조사 [확인]. **따라서 트윈 납품은 "활용도 조사에서 살아남는 형태"**, 즉 월간 리포트 발송 이력 자체가 사후점검 증빙이 되도록 설계한다 [추정].

**데이터 요건 관련**: 기초=아날로그 생산정보의 디지털화·수기 업무 전산화, 중간1=디지털 정보의 실시간 수집·분석·공유(실시간 집계·모니터링), 중간2=인과 판단·실시간 제어, 고도=IoT 완전 지능형 [확인, 2016~2018 자료]. 수준별 자동수집 비율 같은 **정량 기준표는 공개 스니펫에서 확인 불가** [원문 확인 필요]. 전류 센서 기반 실시간 가동 모니터링은 중간1 요건의 최소 형태에 해당한다고 볼 수 있다 [추정].

### 3-3. 소규모 기업의 도입 실패 모드 (증거 + 현장 추론)

1. **업무 과중 → 입력 중단**(26.7%, 최다 애로) [확인]. 대응: 공장 측 입력을 하루 3분으로 제한, 사진 1장이 기본 단위.
2. **구축 후 관심 이탈**: 공급기업은 구축 매출을 우선하고 담당자는 다음 프로젝트로 가며, 연 단위 사후관리 비용과 잦고 작은 요청이 맞지 않음 [확인, eopla]. 대응: 월 구독에 "작은 요청 처리"를 포함.
3. **병행 운영의 함정**: 종이와 디지털을 동시에 돌리면 둘 다 부실 [확인, 벤더]. 대응: 종이는 유지하고 디지털은 사진으로만.
4. **정의 불일치**("완료"·"불량"의 기준) [확인]. 대응: 주간 양식 뒷면에 정의 5줄 인쇄.
5. **공급기업 폐업·업종 전환** [확인]. 대응: `factory.json`·변경 로그·리포트를 공장 소유 구글 드라이브에 복제, 오픈 포맷.
6. **보안·네트워크**: 전류 센서용 Wi-Fi가 없는 공장. 대응: LTE 라우터 또는 SD 카드 로컬 저장 후 월 1회 회수 [추정].
7. **외국인 근로자(E-9) 비중**: 양식 언어·픽토그램 [추정, 저장소 10].

---

## 4. 변경관리: 기록, 버전, as-built 감사, 효과 평가

### 4-1. 변경 로그 스키마 (제안, `factory.json`과 병치하는 `changes.jsonl`)

```json
{
  "change_id": "C-2026-11-03-01",
  "reported_on": "2026-11-05", "effective_from": "2026-11-03",
  "reporter": "사장|반장|컨설턴트", "evidence": ["photo:IMG_2231.jpg"],
  "type": "station.add|station.remove|station.move|machine.replace|routing.change|rule.change|worker.join|worker.leave|worker.reassign|shift.change|product.new|supplier.change|outsourcing.change|other",
  "scope": {"stations": ["EB2"], "products": ["P_WARD"], "workers": ["W07"]},
  "description": "엣지밴더 2호 교체(접착제 PUR), 위치 3m 동쪽 이동",
  "expected_effect": [{"kpi": "edge_cycle_min", "direction": "down", "magnitude": "10~20%"}],
  "twin_action": "restructure|recalibrate|input_only|none",
  "model_version_before": "2.3.1", "model_version_after": "3.0.0",
  "status": "logged|modeled|validated|closed",
  "evaluation": {"method": "ITS|CRN", "window_pre_weeks": 8, "window_post_weeks": 8, "result": null}
}
```

근거: Epsilon3 as-built 기록 가이드(직렬 부품·도면 리비전·승인된 편차를 기록, 설계–실물이 이유 없이 갈라지면 구성관리 문제) [확인]; Hexagon Smart 3D(as-built 모델에 대한 변경은 엄격한 변경 통제 아래 프로젝트 단위로) [확인]; Emerson Ovation Curation Tool(주기적 자동 변경 식별, 누가·무엇을·언제 감사 이력) [확인, 제어시스템 대상 유추]. 가구 공장 규모에서는 이 스키마의 **종이 버전(주간 양식의 "바뀐 것" 칸)**이 1차 입력이고, JSON은 컨설턴트가 만든다.

### 4-2. `factory.json` 버전 관리 (제안)

- `meta.version` = SemVer: **MAJOR** 구조 변화(stations/routing/workers/rules), **MINOR** 재보정(파라미터만), **PATCH** 표기·좌표 미세수정.
- `meta.calibrated_on`, `meta.valid_until`(12개월 또는 다음 MAJOR), `meta.parent_version`, `meta.calibration_data_window`(로깅 기간), `meta.validation_report`(링크).
- git 저장(이미 저장소가 git). 월간 스냅샷 태그 `v2.3.1+2026-11`. 시나리오 패치(`scenarios/*.json`)는 **기준 버전을 명시**(`"base_version": "2.3.x"`) — 구조가 바뀌면 시나리오도 무효.
- `tools/data_quality.py`의 출처 스코어카드에 **"측정 시점 경과(개월)"** 열을 추가해 파라미터별 노후도를 보이게 한다 [제안].

### 4-3. As-built vs As-modeled 감사 (분기, 반나절)

체크리스트: ① 기계 목록·위치(레이저 거리계 2~3점으로 `pos` 대조, 0.5 m 초과 시 갱신), ② 라우팅(화이트보드·대차 흐름 사진과 `products[].routing` 대조), ③ 인원·스킬(주간 양식 4주치와 `workers[]` 대조), ④ 규칙(배치·우선순위·외주 — 반장 10분 인터뷰 "요즘은 어떻게?"), ⑤ 교대·휴게·잔업(`meta.shift`), ⑥ 전류 센서 부착 상태(클램프 빠짐 = 흔한 고장), ⑦ 에너지(계약전력·요금제). 불일치 건수를 리포트에 "as-built 일치율"로 표기. 근거: 건설·플랜트 분야의 as-built 괴리 원인 목록(설계 변경·현장 조정·부품 대체·인적 오류) [확인, USPTO 11900296].

### 4-4. 변경 효과 평가 — 루프 닫기

**(a) 시뮬레이션 내 A/B**: 공통난수(CRN) + 짝지은 t 신뢰구간; 3개 이상 대안은 순위·선택(R&S) [확인, Law & Kelton 계열·GT ISyE 6644 강의]. CRN은 난수 스트림 **동기화**(같은 주문에 같은 난수)가 필수이며 양의 공분산으로 차이의 분산을 줄인다 [확인]. 저장소 `sim/compare.py`가 seed 고정으로 이미 이 구조.

**(b) 현실에서의 사후 평가 — 단절 시계열(ITS)**: Bernal, Cummins & Gasparrini (2017) *Interrupted time series regression for the evaluation of public health interventions: a tutorial*, Int J Epidemiol 46(1):348–355, DOI 10.1093/ije/dyw098 — 분할회귀로 수준·기울기 변화 추정, 과산포·자기상관·계절성·시변 교란 처리 [확인]. 단순 전후 평균 비교는 추세 때문에 과대·과소 추정하며 품질개선 연구에서 반복적으로 지적된 오류 [확인]. 세그먼트당 최소 점수(흔히 8점)는 기억에 의존하므로 원문 확인 [원문 확인 필요].
- 가구 공장 적용 [추정]: 주간 KPI, 변경 전 8~12주·후 8~12주, 공변량으로 주문수·믹스·인원·계절 더미, 자기상관은 Newey–West 또는 AR(1). 효과를 **트윈이 예측한 효과와 나란히** 표시.
- **트윈 반사실 대조군** [제안]: 변경 후 실제 주문 스트림을 **구(舊) 버전 트윈**에 넣어 "바꾸지 않았다면"의 KPI를 생성하고, 실측과의 차이를 효과로 본다(합성 대조군 역할). ITS 추정치와 트윈 추정치가 맞으면 트윈의 "효과 예측 신뢰도"가 올라가고, 틀리면 그 자체가 재보정 신호다. 이것이 "AX 컨설팅"의 루프를 닫는 가장 싼 방법이다.
- 호손 효과·동시 변화(새 작업자 합류와 기계 교체가 같은 달)는 변경 로그로 분리; 분리가 불가능하면 "효과 미확정"으로 정직하게 기록.

---

## 5. 다공장 확장: 참조 모델, 전이 가능성, 사전분포

### 5-1. 참조 모델·템플릿의 확립된 관행

- **재사용 스펙트럼** [확인]: Robinson et al.의 4단계 — 전체 모델 재사용, 컴포넌트 재사용, 함수 재사용, 코드 스캐빈징. 전체 모델 재사용은 효율이 가장 크지만 호환성·신뢰성 문제로 가장 어렵다(Hussain et al.); Paul, Nance, Robinson & Pidd (2004) *Simulation model reuse: definitions, benefits and obstacles*, Simulation Practice and Theory 12:479–494.
- **가구·목재 업종의 선례** [확인]: Wiedenbeck & Araman (1995, USDA Forest Service) — 기존 러프밀 모델을 **범용·유연 모델로 변환**해 소규모 업체의 비용·전문성 장벽을 제거하려 했다(treesearch/338). Wiedenbeck & Kline (1994) 모델 개발 수명주기 사례(treesearch/350). Varga et al. (2008/2010) SIMUL8 가구공장 물류 시뮬레이션; Rahman et al. (2018) 가구 재단 라인 배치 크기별 비교; 스페인 ROWOOD 로봇 가구 셀 트윈.
- **데이터 구동(generic) 모델** [확인]: Chalmers 2023 기술 프레임워크(파라미터 파일로 구동되는 모델), "Adaptable Simulation Models for Manufacturing"(개념→설계→운영으로 모델이 따라 바뀌어야 함). 저장소의 `factory.json` + 템플릿 xlsx 구조가 이미 이 방식이다.

### 5-2. 가구 공장 간 무엇이 옮겨지고 무엇이 절대 안 옮겨지나 [추정, 저장소 03·10·13 반영]

| 옮겨짐(아키타입 라이브러리에 넣을 것) | 공장마다 다시 재야 함 | 절대 전이 금지 |
|---|---|---|
| 판상가구 공정 위상(재단→엣지→보링→(도장)→조립→포장)과 변형(선도장, 외주 도장) | 사이클·셋업의 **절대값**(기계 연식·공구·작업자) | 레이아웃·거리·동선·대차 경로 |
| 기계 클래스별 사이클 **함수형**(엣지 m/분, 네스팅 장당 분, 보링 홀수) | 불량·재작업률 | 병목의 정체(어느 공장은 엣지, 어느 공장은 조립) |
| 셋업 구조(색상·두께·엣지테이프 교체가 셋업 유발) | MTBF/MTTR | 비공식 규칙(배치·우선순위·누가 대차를 미나) |
| 물리 상수(대차 용량, 보행 속도, 지게차 속도, 기계 정격 kW·부하율 범위) | 인원·스킬 매트릭스·결근율 | 제품 믹스·고객 채널(OEM vs B2C 맞춤) |
| 계절성 **형태**(이사철·신학기), 설치일 리드 분포 형태 | 주문수·설치일 리드 절대값 | 외주 결정, 사장의 목적함수 |
| 전기 요금 구조(산업용(을) TOU) | 계약전력·기저부하 | 화이트보드 스케줄링 휴리스틱 |
| 민감도 순위의 **대략적 형태**(셋업·조립이 상위) | 민감도 상위 10개의 값 | — |

### 5-3. 사전분포(priors)와 계층 모형 — 어떻게 쓰고 어떻게 쓰면 안 되나

**확립된 틀** [확인]: Kennedy & O'Hagan (2001) *Bayesian calibration of computer models*, JRSS-B 63(3):425–464 — y = η(x,θ)+δ(x)+ε, 불일치항 δ. 계층 보정(calibr8 문서: 배치별 절편을 계층으로 연결; ENBIS 2026: 기준 배치로 새 로트 보정, Beta 하이퍼프라이어의 선택이 결과를 좌우). 교환가능 사전분포는 추정치를 공통 평균으로 수축시켜 전체 오차를 줄일 수 있다(실험실 보정 연구). 부분 풀링(partial pooling)의 일반 원리(Gelman 계열).

**핵심 주의사항**
1. **보정된 파라미터 값은 예측이 맞아도 불안정하다** [확인]: Tuo & Wu (2016)는 KOH가 비합리적 보정값을 주는 예를 보였고, 2017 후속 논문은 KOH가 "파라미터 보정보다 물리 응답 예측에서 더 강건"하다고 결론. 저장소 14의 Bai & Lam(2020) 적격집합(eligibility set) 논의와 같은 맥락 — k개 KPI로 p개 파라미터를 점으로 식별할 수 없다. **따라서 이전 공장의 θ 점추정을 새 공장의 사전평균으로 옮기는 것은 식별되지 않은 값을 옮기는 것**이다. 옮길 것은 (a) 물리적으로 의미가 분명하고 직접 측정된 양(엣지 m/분, 대차 용량)의 분포, (b) 예측 품질(잔차 분산)의 사전분포다.
2. **사전분포가 2주 데이터를 압도한다**: 유효표본수를 계산해 사전분포의 가중이 새 공장 데이터(예: 셋업 12회 관측)보다 크면 분산을 넓힌다. 규칙 [추정]: 사전 유효표본수 ≤ 새 공장 실측 표본수의 1/3.
3. **전이 품질 게이트** [확인, SYN-DIGITS arXiv 2604.07513의 교훈을 유추]: 항상 보정을 적용하면 오히려 해롭다; 합성 적합 품질이 나쁘면 비보정 예측으로 되돌린다. 적용: 사전분포를 쓴 보정과 쓰지 않은 보정을 **홀드아웃 2주**에서 비교하고 나쁜 쪽을 버린다.
4. **민감도 기준 분리**: `sensitivity.py`에서 처리량 변동 <1%인 파라미터는 라이브러리 사전분포로 대체 가능(저장소 03 §5 규칙과 일치); 상위 10개는 반드시 현지 측정.
5. **풀링 최소 개수**: 공장 3개 미만이면 계층 하이퍼파라미터가 거의 식별되지 않는다 — 5개 이상 될 때까지는 "넓은 사전분포 + 수동 상한·하한"으로 운영 [추정]. 이상치 공장을 흡수하려면 정규 대신 Student-t 또는 혼합 사전분포 [추정].
6. **컨텍스트 불일치**(arXiv 2505.11847)를 아키타입 태그로 관리: 제품군(주방/붙박이장/사무 OEM), 재단 방식(런닝쏘/판넬쏘/CNC 네스팅), 도장 유무, 인원대, 고객 채널. 다른 태그 간 풀링 금지.
7. **표본 설계 편향**: 첫 공장들은 "참여에 동의한, 데이터가 있는" 공장이다. 그 사전분포는 낙관적으로 치우친다(선택 편향) [추정].

---

## 6. 상업적 현실 점검

### 6-1. 증거

- **ROI·손익분기** [확인]: Cranfield 설문(99명 응답·전문가 14명, 영국 국방 편중) — 완료된 DT 프로젝트는 평균 **2년 미만에 손익분기**; 장애요인은 전문성·자금·상호운용성. 표본이 작고 소규모 제조업 대표성 없음.
- **비용이 최대 저해요인** [확인]: ABI Research(2026) 제조 의사결정자 설문 — 트윈 도입·확장의 최대 저해는 "너무 비쌈"; 프로젝트가 대규모 통합·데이터 인프라 프로젝트로 비화해 가격이 급등. 51%는 생산 효율·다운타임 감소를 최대 동인으로 꼽음.
- **인지·정의 혼란** [확인]: NIST — 트윈 정의의 난립이 SME를 혼란시키고 제조 도입은 느리고 어렵다(6개 조직 인터뷰). Incisiv 설문(40명) — ROI 정량화 불가가 주요 장애. Altair 2022(2,000명+) — 절반 이상이 지식이 제한적이거나 혼란스럽다(벤더 설문).
- **실패율**: Gartner·McKinsey·Deloitte의 "트윈 프로젝트 X%가 확장에 실패" 수치는 **검색으로 확인되지 않았다**. Forrester는 "확장 시 기술·조직 장벽" 정도. 실패율을 인용하지 말 것 [확인된 부재].
- **SME 시뮬레이션의 구조적 문제** [확인]: Hill et al. (2011) — 유효 모델을 만드는 시간·전문성이 핵심 장애, 저량·다품종 운영은 적절히 모델링하기 복잡; 아일랜드 SME 연구(2021) — SME는 자기 시스템의 복잡성과 DES의 유용성을 과소평가; WSC 2022 — 인력·자금·전문성 부족, 초기 단계(문제 식별·사양)를 돕는 도구 제안(Delphi). 1998 WSC의 도입 4단계(separate→linked→activated→adopted).
- **대기업도 상시 활용 못 함** [확인]: 아일랜드 7개 다국적 기업(2010) — 시뮬레이션은 상시 의사결정 지원으로 거의 쓰이지 않음; 소유비용 절감 프레임워크 필요.
- **한국 스마트공장 성과 수치** [확인, 2019 중기부 성과분석]: 생산성 +30%, 품질 +43.5%, 원가 −15.9%, 납기준수 +15.5%, 매출 +7.7%, 고용 +3명/사, 산재 −18.3%; **10인 미만 기업의 생산성 개선 39.0%**로 평균 상회. 자기보고·선택편향 가능성이 크고 2024~2025 갱신 수치는 미확인.
- **사후관리 현실** [확인]: 활용률 80%+(정부) vs 약 50%(의원실, "목적대로 적극 활용"); 구축 후 담당자 이탈; 연 단위 사후관리 비용 구조와 잦은 소규모 요청의 불일치; 공급기업 폐업 리스크.

### 6-2. 납품 후 사장이 실제로 쓰는 것 [추정, 근거: 위 증거 + 저장소 10·05]

| 산출물 | 사용 빈도 | 지속 조건 |
|---|---|---|
| 실측 대시보드(전류 기반 가동, 오늘 재단 장수, 잔업) | 매일~매주 | 카톡으로 **푸시**될 것(앱을 열지 않음), 숫자 5개 이하 |
| 월 1장 "트윈 건강 리포트"(KPI 8개 vs 예측대, 드리프트 경보, 바뀐 것) | 월 1회 | 사장이 읽는 데 3분, 인쇄 A4 |
| 시나리오 연구(기계 투자·레이아웃·인원·배치 규칙) | 연 2~4회, 결정 시점 | **미리 돌려 둔 "결정 메뉴"**(저장소 `scenarios/s1~s8`)로 당일 답변; 새 질문은 1주 내 |
| 3D 뷰어 | 첫 달, 견학·은행·지원사업 심사 때 | 설득·증빙용; 운영 도구 아님 |
| 정부사업 서류(수준확인, 성과보고, 사후점검 응답) | 연 1~2회 | 트윈 리포트가 그대로 증빙이 되게 양식 정렬 |
| 변경 로그·as-built 감사 | 분기 | 컨설턴트가 주도 |

**지속되는 납품 형식**: 소프트웨어 라이선스가 아니라 **"월 구독 서비스(모니터링+리포트+결정 메뉴+작은 요청)"**. 저장소 00 §6의 월 50~150만 원 구독 구조와 정합. 전기요금 절감(산업용(을) TOU)·잔업 감소로 상쇄 가능성을 첫 리포트에서 수치로 보여줘야 갱신된다 [추정]. 트윈을 "AX"로 팔 때 가장 흔한 실패는 **사장이 결정할 일이 없는 달에 비용만 나가는 것**이므로, 구독의 기본 가치는 §2의 모니터링(드리프트 경보·고장 감지·에너지)에 두고 시나리오는 결정 시점의 "옵션 가치"로 포지셔닝한다.

### 6-3. 리스크 요약

- 실패율·ROI 통계는 **근거가 약하거나 벤더 자료**다. 제안서에 "손익분기 2년 미만(영국 설문)"·"10인 미만 생산성 +39%(2019 중기부)" 외의 수치는 쓰지 말 것.
- 사후관리 의무(5년 조사 가능)와 공급기업 역량평가 강화(2026 소공인 개편) 흐름은 "납품 후 생존"이 심사 요소가 되고 있음을 뜻한다 — §2·§4의 리포트 이력이 곧 자산.
- 인력 관련 시나리오는 재배치·교육 프레이밍(저장소 05 §6-4).

---

## 7. 출처

**드리프트·탐지**
- Gama, J., Žliobaitė, I., Bifet, A., Pechenizkiy, M., Bouchachia, A. (2014). *A survey on concept drift adaptation*. ACM Computing Surveys 46(4). https://doi.org/10.1145/2523813
- arXiv 2505.11847 (2025). *Bridging the Reality Gap in Digital Twins with Context-Aware, Physics-Guided Deep Learning*. https://arxiv.org/pdf/2505.11847
- arXiv 2607.18164 (2026, Northwestern). *A Continual Validation, Updating, and Decision-Making Framework for Self-Adaptive Digital Twins via Robust MPC: A Case Study in Additive Manufacturing*. https://arxiv.org/pdf/2607.18164
- Twintinuum (Univ. of Amsterdam). https://pure.uva.nl/ws/files/328888478/1571183093.pdf
- KBC. *Digital Twins in Refining: The Hidden Cost of Model Drift*. https://www.kbc.global/resources/blog/digital-twins-in-refining-the-hidden-cost-of-model-drift/
- NTNU SUBPRO. *Calibration of digital twins*. https://www.ntnu.edu/subpro/calibration-of-digital-twins
- Engineering News (2026-01-13). *Don't let the digital twin drift from reality*. https://www.engineeringnews.co.za/article/dont-let-the-digital-twin-drift-from-reality-2026-01-13
- Sürer, Chen, Shashaani (WSC 2025). *Dynamic Calibration Framework for Digital Twins Using Active Learning and Conformal Prediction*. https://www.informs-sim.org/wsc25papers/inv177.pdf
- arXiv 2606.07789. *A Framework for Evaluating and Benchmarking Concept Drift Detection Methods*; Tsukuba IoT 드리프트 벤치마크 https://www.cs.tsukuba.ac.jp/~machida/wfiot2021-wang.pdf; menelaus 문서 https://menelaus.readthedocs.io/en/dev/menelaus.change_detection.html; MetricGate 가이드 https://metricgate.com/blogs/concept-drift-model-monitoring/
- arXiv 2204.06688 (잔차 I-MR 관리도); Spanos & Poolla, Berkeley EE290H 강의 *From SPC to APC* https://inst.eecs.berkeley.edu/~ee290h/fa03/handouts/lectures/lecture%2016%20from%20SPC%20to%20APC.pdf; Shao & Lin (2013) TFT-LCD 잔차 차트 https://digitalcommons.aaru.edu.jo/amis/vol07/iss4/26; Nembhard et al. (2002) DES+SPC https://iro.uiowa.edu/esploro/outputs/journalArticle/Implementing-SPC-in-a-Simulation-Model/9984121869902771
- 김종걸·김동녘 (2012). Shewhart/CUSUM/EWMA 비교, 대한안전경영과학회. https://koreascience.kr/article/CFKO201208455513221.pdf
- 프로세스 드리프트: Vienna 대학 https://eprints.cs.univie.ac.at/8584 , https://eprints.cs.univie.ac.at/6422 ; Martjushev–Bose–van der Aalst https://www.vdaalst.com/publications/p822.pdf ; arXiv 2103.10749; Kraus & van der Aa CV4CDD-4D https://madoc.bib.uni-mannheim.de/69763/1/s44311-025-00012-w.pdf

**검증·유지·재사용**
- Sargent, R. G. (2013). *Verification and validation of simulation models*. J. Simulation 7(1):12–24. https://ideas.repec.org/a/taf/tjsmxx/v7y2013i1p12-24.html ; Sargent–Goldsman–Yaacoub WSC 2016 https://www.informs-sim.org/wsc16papers/016.pdf
- Robinson, S. (2008). *Conceptual modelling for simulation Part I*. JORS. https://repository.lboro.ac.uk/articles/journal_contribution/9504302
- WSC 2001 모델 유지비 https://informs-sim.org/wsc01papers/124.PDF ; WSC 2002 문서화 https://www.informs-sim.org/wsc02papers/144.pdf ; Chalmers 2023 DES 유지보수성 석사논문 https://odr.chalmers.se/items/b2c0969b-5321-4566-a080-6094543ac3b1
- Paul, Nance, Robinson, Pidd (2004). *Simulation model reuse*. SPT 12:479–494. https://eprints.lancs.ac.uk/id/eprint/43891/ ; WSC 2002 컴포넌트 재사용 https://www.informs-sim.org/wsc02papers/099.pdf ; Zschaler et al. (2025) On Simulation Reuse https://eprints.soton.ac.uk/507462/
- Wiedenbeck & Araman (1995) https://research.fs.usda.gov/treesearch/338 ; Wiedenbeck & Kline (1994) https://research.fs.usda.gov/treesearch/350 ; Araman (1977) https://research.fs.usda.gov/treesearch/3 ; Varga et al. (2010) https://doaj.org/article/80c804792dd14785ba2b416f0293288d ; Rahman et al. (2018) https://harisportal.hanken.fi/sv/publications/simulating-cutting-line-of-a-furniture-industry/ ; ROWOOD https://dev.ambitcluster.org/en/proyectos/proyectos-innovacion/rowood-en
- U. Limerick (2010) *Barriers to the application of simulation for tactical decision making* https://pure.ul.ie/en/publications/barriers-to-the-application-of-simulation-for-tactical-decision-m/ ; Hill et al. (2011) SME obstacles https://hpc.msstate.edu/pubs/?abs=8570 ; TUS Ireland (2021) https://research.tus.ie/en/publications/analysis-of-complexity-and-simulation-usage-in-manufacturing-smes/ ; WSC 2022 https://informs-sim.org/wsc22papers/181.pdf ; WSC 1998 https://www.informs-sim.org/wsc98papers/211.PDF
- 검증 허용오차 사례: arXiv 2604.24394(5%); MIT 반도체(6%) https://dspace.mit.edu/handle/1721.1/50485 ; UNIFEI 동등성 검정 https://repositorio.unifei.edu.br/xmlui/handle/123456789/3378
- ISO 23247 시리즈(-1 2021, -5 digital thread, -7 commissioning 초안: 주기·지연·충실도 검증) https://www.iso.org/standard/75066.html , https://standardsdevelopment.bsigroup.com/projects/9026-13850

**변경 평가**
- Bernal, Cummins, Gasparrini (2017). ITS tutorial. Int J Epidemiol 46(1):348–355. https://academic.oup.com/ije/article/46/1/348/2622842
- CRN·비교: Wikipedia Variance reduction https://en.wikipedia.org/wiki/Variance_reduction ; GT ISyE 6644 Comparing Systems https://www2.isye.gatech.edu/~sman/courses/6644/Module10-ComparingSystems-201128.pdf ; Nelson & Matejcik (1991) CRN+제어변량 다중비교 https://pubsonline.informs.org/doi/epdf/10.1287/opre.39.4.583
- As-built: Epsilon3 https://www.epsilon3.io/behind-the-console/building-a-traceable-as-built-record ; Hexagon Smart 3D https://docs.hexagonppm.com/r/en-US/Intergraph-Smart-3D-Integration-Project-As-Built-with-HxGN-SDx/13.1/938884 ; Emerson Ovation Curation Tool https://eepower.com/new-industry-products/emerson-launches-sync-tool-for-digital-twins-in-power-plants/ ; USPTO 11900296

**베이지안·전이**
- Kennedy & O'Hagan (2001) JRSS-B 63(3):425–464 https://www.asc.ohio-state.edu/statistics/comp_exp/jour.club/kennedy01.pdf ; Tuo & Wu 식별성 논의 https://ar5iv.arxiv.org/html/1703.01326 ; UQ with imperfect models review arXiv 2012.09449
- calibr8 계층 보정 https://calibr8.readthedocs.io/en/latest/Advanced_Hierarchical_Calibration.html ; ENBIS 2026 https://conferences.enbis.org/event/79/contributions/1055/ ; Bilkent 생산라인 보정 https://repository.bilkent.edu.tr/items/e6b0a1bb-8fd7-4574-9db5-c7553abfd6d9
- SYN-DIGITS arXiv 2604.07513; HIT cross-device DT https://scholar.hit.edu.cn/en/publications/establishing-a-digital-twin-diagnostic-model-based-on-cross-devic/ ; LLNL transfer calibration https://data-science.llnl.gov/sites/data_science/files/transfer_learning_for_the_calibration_of_the_icf_simulations.pdf

**한국 정책·시장**
- 중기부 2026년도 정부형 스마트공장 구축사업 공고 https://www.mss.go.kr/site/smba/ex/bbs/View.do?cbIdx=310&bcIdx=1063190&parentSeq=1063190 ; 기업마당 통합공고 https://www.bizinfo.go.kr/sii/siia/selectSIIA200Detail.do?pblancId=PBLN_000000000115994 ; 정부형 https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/view.do?pblancId=PBLN_000000000116263 ; 통합공고 PDF https://grant-documents.thevc.kr/282439_...pdf
- 대중소상생형(대한상의) https://ansancci.korcham.net/file/dext5uploaddata/2026/(기초 및 고도화 모집공고) 26년 대중소상생형 스마트공장 구축 지원사업 모집공고(대한상의)_____.pdf ; 한국도로공사 https://gimcheoncci.korcham.net/file/dext5uploaddata/2026/2026년 한국도로공사 대중소 상생형 스마트공장 구축 지원사업 공고문_.hwp
- 경북(포항) 기초 추가모집 https://pohangcci.korcham.net/file/dext5uploaddata/2026/[붙임1] 2026년 경북형(포항) 스마트공장(기초단계) 구축지원사업 추가모집 공고문.pdf ; 전북TP https://tour.gunsan.go.kr/_cms/board/eFileDownload/7/9297116/63c985a953315c03b88feed96be4f6f2 ; 전남 https://data.jntp.or.kr//files/20260810/2026081012555575996.pdf
- 제조AI특화 https://acci.korcham.net/file/dext5uploaddata/2026/(붙임1) 2026년도 제조AI특화 스마트공장 구축지원사업 공고.pdf ; 수준확인 https://gecci.korcham.net/file/dext5uploaddata/2026/2026년도 스마트공장 수준확인 사업 공고__.pdf
- 소공인 스마트제조 2026 추가모집·개편 https://view.asiae.co.kr/article/2026061410303966456 ; 2025 소공인 스마트제조 도약 공고 https://hwaseongcci.korcham.net/file/dext5uploaddata/2025/[붙임1] 2025년 「소공인 스마트 제조 도약」 지원 사업 모집공고.pdf
- 제1차 스마트제조혁신 실태조사(2025-04) 디지털데일리 https://www.ddaily.co.kr/page/view/2025042816294926205 ; 활용률·사후관리 분석 https://eopla.net/magazines/47744 ; 2019 성과분석 산업일보 https://kidd.co.kr/news/189847 ; 2020 보급실적 https://kidd.co.kr/news/202998 ; 뉴시스 2023 고도화 1.4% https://www.newsis.com/view/NISX20230118_0002163472 ; 경북 2024 기초 https://kbmaeil.com/article/202401250382948
- 사후관리 규정(제41조, 5년) https://www.tipa.or.kr/s040305/file_down/id/6462 ; 경남 솔루션은행 https://smartcity.go.kr/2019/05/31/경남도-스마트공장-솔루션은행-운영-업무협약-체결-2/ ; 경기 사후관리 지원 https://kyeonggi.com/article/202101271154635 ; 국조실 합동점검 https://www.fnnews.com/news/202103230948363989
- 이카운트 월 4만 원 https://www.fnnews.com/news/202406251223092059 ; 더존 MES10 Edge https://core.asiae.co.kr/article/2021031815382045545 ; 아이티컴 저비용 MES https://kidd.co.kr/news/180002 ; 기초데이터·스프레드시트 https://kidd.co.kr/news/239094 ; AppSheet+구글시트 사례 https://kmong.com/gig/748773
- 국내 OCR 연구 https://www.koreascience.kr/article/JAKO201912937047205.pdf , https://www.earticle.net/Article/A350457
- 전류 센서 벤더: Guidewheel https://www.guidewheel.com/blog/machine-monitoring-without-it-no-plc ; TeepTrak https://teeptrak.com/en/current-sensor-vs-multi-sensor-oee-monitoring-solutions/ ; HARDWARIO https://www.hardwario.com/products/chester/catalog/current/

**상업적 현실**
- Cranfield (2023 preprint / 논문) *Industrial insights on digital twins in manufacturing* https://dspace.lib.cranfield.ac.uk/handle/1826/19940 , https://www.preprints.org/manuscript/202305.0424
- ABI Research (2026) https://www.abiresearch.com/market-research/insight/7788351-as-factory-digital-twin-suppliers-jockey-f ; NIST https://www.nist.gov/node/1646816 ; Incisiv/Siemens 설문 https://www.incisiv.com/hubfs/ebook/Siemens/IMHE/... ; Altair 2022/2023 https://altair.com/resource/2023-digital-twin-survey-report-vertical-breakdown-manufacturing ; Forrester https://www.forrester.com/report/Grasp-The-Challenge-Of-Implementing-Digital-Twins-At-Scale/RES158396
- 학습곡선·이직: Twente https://fip.utwente.nl/article/second-issue/the-learning-curve-effect ; Applied Sciences 2021 https://art.torvergata.it/retrieve/e291c0d9-d4b0-cddb-e053-3a05fe0aa144/applsci-11-08620-v3.pdf
- 데이터 입력 준수: iFactory https://ifactoryapp.com/industries/manufacturing-plant/paperless-manufacturing-roi-digital-forms-records ; Poimapper https://www.poimapper.com/?p=13997

**저장소 내부 참조**: `/home/user/claude_mem/factory-twin/schema/factory.schema.json`, `sim/validate.py`, `sim/calibrate.py`, `sim/sensitivity.py`, `sim/uncertainty.py`, `capture/sensing/esphome_ct_clamp.yaml`, `capture/sensing/states_from_current.py`, `tools/data_quality.py`, `docs/research/14_twin_calibration_uncertainty.md`, `docs/research/05_korea_smart_factory_ax_market.md`, `docs/research/10_korean_furniture_shop_reality.md`, `docs/00_종합보고서.md` §6.
