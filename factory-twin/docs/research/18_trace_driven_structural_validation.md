# 구조 오차와 입력분포 오차의 분리: 소규모 주문가구 공장 디지털 트윈의 검증 방법론

**대상**: 10–20인 규모 한국 주문가구(패널/MDF) 공장의 이산사건 디지털 트윈. 데이터: 현장 방문 1회, 2주간 비침습 로깅(전류 클램프·광전 카운터·카메라 3대), 3–12개월 종이 기록(재단표, 발주서, 시공 캘린더, 송장), 2주간 종이 배치 추적표(공정별 도착/시작/종료).

**표기**: [확립] = 교과서·동료심사 문헌에서 잘 확립된 내용. [추론] = 본 보고서 저자의 추론·적용(검증 필요). [계산] = 본 보고서에서 직접 계산.

---

## 0. 요약 (핵심 주장)

1. 트윈이 실측과 다를 때 그 차이는 네 성분으로 분해된다: (a) **구조(model-form) 오차** — 라우팅·버퍼·자원 논리·배칭·디스패칭이 틀림, (b) **입력분포 오차** — 서비스시간·도착·재작업 확률 등의 분포 모형이 틀림(파라미터 오차 포함), (c) **몬테카를로 오차**, (d) **데이터(측정) 오차**. 종단 KPI(평균 리드타임, 처리량) 하나만 비교하는 "블랙박스 검증"은 이 네 가지를 **합산한 것**만 보여주므로 구조 결함을 입력분포로 보상해 맞추는(“틀린 이유로 맞는”) 위험이 크다. [확립: Kleijnen 1999; Oreskes et al. 1994; Beven 2006; Ghasemloo/Eckman/Li 2026]
2. **트레이스 구동(trace-driven) 재생**은 (b)와 (c)를 설계상 제거한다. 관측된 주문 투입 시각과 관측된 배치별 서비스시간을 그대로 강제하면, 남는 차이는 대기시간(큐잉)에서만 발생하며, 그 대기시간은 오직 모델의 **구조 논리**가 만든 것이다. 따라서 공정별 "구조 잔차" r_ik = (모델 대기) − (관측 대기)의 패턴이 결함의 종류를 가리킨다. [확립: Law & Kelton의 correlated inspection; Kleijnen et al. 1996/1998/2001] [추론: 잔차 패턴 → 결함 유형 매핑표]
3. 검증 순서 **구조 → 결정적 시간 → 변동성 → 규칙**은 Zeigler의 타당성 위계(구조 ⊃ 예측 ⊃ 복제), Barlas의 "구조 먼저", Robinson의 white-box→black-box와 일관된다 [확립]. 다만 DES에서 "규칙(디스패칭)"은 구조의 일부이고, 변동성을 도입해야만 드러나는 구조 결함(봉쇄·경합)이 있으므로, 순서는 엄격한 직렬이 아니라 "강제 수준을 단계적으로 풀어가는 사다리"로 운영해야 한다. [추론]
4. 10–30 배치면 **큰 구조 결함**(잔차 ≥ 서비스시간 1회분 수준)은 공정 단위로 검출 가능하지만, 디스패칭 규칙의 미세 차이나 분포 형태는 검출 불가능하다. 공정별 유효 표본은 "배치 수"이지 "배치×공정"이 아니다. [계산/추론]
5. 공장에 요청할 최소 기록은 **배치 ID로 연결되는 공정별 도착/시작/종료 + 자원 + 그룹핑 키(색상/두께) + 재작업/외주 플래그**이며, 완료시각만 있을 때는 Larson(1990)의 queue inference 류 재구성과 Little 법칙 일관성 검사로 후퇴해야 하고, 이 경우 구조/입력 분리는 부분적으로만 가능하다. [확립+추론]

---

## 1. 개념 틀: 어떤 오차를 분리하려는가

### 1.1 오차 분해

시뮬레이션 출력 Y_model과 실측 Y_real의 차이는 다음과 같이 쓸 수 있다(개념적 분해, 수학적 항등식은 아님):

Y_model − Y_real = [구조/모델형태 오차] + [입력모형 오차(분포형태+파라미터)] + [MC 표본오차] + [측정·기록 오차]

- **입력 불확실성(input uncertainty)**은 시뮬레이션 문헌에서 잘 정의된 개념이다: "시뮬레이션을 구동하는 기본 확률과정의 참 분포를 모르는 데서 오는 (대개 측정되지 않는) 효과"이며, 실측 자료에 적합한 분포라면 부트스트랩으로 그 기여를 정량화할 수 있다. [확립: Song, Nelson & Pegden 2014, *Advanced tutorial: input uncertainty quantification*, WSC 2014, https://informs-sim.org/wsc14papers/includes/files/016.pdf; Barton, Lam & Song, "Input uncertainty in stochastic simulation"]
- **모델형태 불확실성(model-form uncertainty)**은 Roy & Oberkampf(2011)가 "모델이 의존하는 모든 가정·개념화·추상화·근사·수학적 정식화"로 정의했으며, 이들은 면적 검증 척도(area validation metric)로 그 크기를 잰다. [확립: Roy & Oberkampf 2011, *A comprehensive framework for VV&UQ in scientific computing*, CMAME 200:2131–2144, https://www.aoe.vt.edu/content/dam/aoe_vt_edu/people/faculty/cjroy/Publications-Articles/VVUQ-CMAME.Final-Accepted-FIGURES.pdf]
- DES 커뮤니티의 분류에서도 입력 불확실성, 모델(구조) 불확실성, 파라미터 불확실성은 별개 항목으로 열거된다. [확립: NSF 2012 Workshop on simulation modeling error, https://www.isye.gatech.edu/sites/default/files/documents/conferences/2012wsm/ModelingError.pdf]

### 1.2 타당성 위계

Zeigler의 세 수준: **복제 타당성(replicative)** — 실험 프레임 안에서 모델과 시스템의 행동이 허용오차 내 일치; **예측 타당성(predictive)** — 같은 입력 궤적에 대해 모델이 시스템 출력 궤적을 예측; **구조 타당성(structural)** — 모델 내부 구조가 시스템 구조를 표상. 구조 ⇒ 예측 ⇒ 복제의 함의 관계가 성립한다. [확립: Zeigler, Praehofer & Kim, *Theory of Modeling and Simulation*; ACIMS 용어집 https://acims.asu.edu/education/education-modeling-and-simulation-all-definitions-p-v]

이 위계가 본 보고서의 핵심 논리다. 트레이스 구동 재생은 "같은 입력 궤적"을 문자 그대로 구현하므로 **예측 타당성**을 직접 시험한다. 종단 KPI 비교(분포 샘플링 후)는 **복제 타당성**만 시험한다. 디지털 트윈은 "what-if" 예측에 쓰이므로 복제 타당성으로는 부족하다.

### 1.3 Kleijnen의 세 가지 데이터 상황

Kleijnen(1999)은 (i) 실데이터 없음, (ii) 출력 데이터만 있음, (iii) 입력과 출력 데이터 모두 있음(= 트레이스 구동 가능)을 구분하고, (ii)에서는 2표본 t 검정 류, (iii)에서는 산점도에 직선을 맞춰 기울기 1·절편 0을 검정하는 통념적 방법이 **틀렸음**을 지적하고 대안 회귀·부트스트랩 절차를 제시했다. [확립: Kleijnen 1999, *Validation of models: statistical techniques and data availability*, CentER DP 1999-104, https://ideas.repec.org/p/tiu/tiucen/f7518d14-a5e9-4c69-a579-6f514489c246.html]

본 과제의 2주 배치 추적표는 명백히 상황 (iii)이고, 3–12개월 송장/시공캘린더는 상황 (ii)에 가깝다. 두 데이터원을 다른 수준의 검증에 배정해야 한다.

### 1.4 최신 전개: 부분 트레이스 조건부 검증

Ghasemloo, Eckman & Li(2026)는 "관측된 시스템 상태에서 모델을 반복 초기화하고, 확률 입력 모형의 **일부**를 관측 실현값으로 고정한 조건부 출력분포"로 적합도 검정을 하고, "어느 입력 모형이 불일치에 가장 기여하는지"를 찾는 진단 도구를 제안했다. M/M/1과 탠덤 큐 디지털 트윈 실험에서 주변 출력분포만 검증하는 기존 방법이 놓치는 입력 오지정을 검출했다고 보고한다. [확립(초록 수준 확인): arXiv:2607.17088, https://arxiv.org/abs/2607.17088] 이는 본 보고서가 제안하는 "강제 수준 사다리"(§2.2)와 같은 발상을 통계적으로 정식화한 것이다. 국내에서도 황보훈·천현재·이홍철(2009)이 "입력 데이터 차이가 검증 결과 신뢰성을 떨어뜨린다"는 동일한 문제의식으로 트레이스 구동 검증을 제안했다. [확립: 한국시뮬레이션학회논문지 18(4):185–195, https://www.koreascience.or.kr/article/JAKO201210348673804.page]

---

## 2. 트레이스 구동 시뮬레이션: 구조 검증 프로토콜

### 2.1 원리

Law & Kelton은 "실제 시스템의 과거 입력 데이터를 모델에 그대로 넣고 모델 출력을 시스템의 과거 출력과 비교"하는 것을 **correlated inspection approach**라 불렀고, Kleijnen 등은 이를 트레이스 구동 시뮬레이션이라 부르며 "시뮬레이션과 실제 시스템이 공통 입력(예: 과거 도착시각)을 공유하여 두 출력이 교차상관된다"고 정의한다. [확립: Kleijnen, Bettonvil & van Groenendaal 1996, WSC, https://www.informs-sim.org/wsc96papers/047.pdf; Kleijnen, Cheng & Bettonvil 2001, *Management Science* 47(11):1533–1538, https://pubsonline.informs.org/doi/fpi/10.1287/mnsc.47.11.1533.10255]

핵심 통찰 [추론, 그러나 큐잉 항등식에서 직접 따라옴]: 공정 k에서 배치 i의 흐름시간은
F_ik = (대기 q_ik) + (서비스 s_ik) + (이동/대기 m_ik)
이다. s_ik를 관측값으로 **강제**하면 모델이 "만들어내는" 것은 q_ik와 m_ik뿐이며, 이 둘은 전적으로 (1) 다른 배치의 도착·서비스(이것도 강제됨)와 (2) 모델의 자원·버퍼·순서 논리에 의해 결정된다. 따라서 **q̂_ik − q_ik는 구조 잔차**다. 입력분포를 샘플링하지 않으므로 입력분포 오차는 정의상 0이고, 난수를 쓰지 않으면(또는 공통난수) MC 오차도 0에 가깝다.

### 2.2 강제 수준 사다리(Forcing ladder)

| 수준 | 강제(관측값 사용) | 샘플링(분포 사용) | 시험 대상 | 데이터원 |
|---|---|---|---|---|
| L0 "완전 재생" | 주문 투입 시각, 배치 구성(수량·자재·색), 라우팅 **관측값**, 공정별 s_ik, 외주 반출/반입 시각, 작업자 출근·휴식 캘린더, 고장 구간 | 없음 | **결정론적 검증**: 모델이 관측 시작/종료 시각을 재현하는가? 잔차는 순수 논리 버그 또는 미기록 사건 | 2주 추적표 + 클램프 |
| L1 "구조 재생" | L0에서 **라우팅과 순서를 뺌** — 투입 시각, 배치 구성, s_ik, 캘린더만 강제 | 없음(라우팅·순서·배칭은 모델 논리가 결정) | **구조 검증**: 라우팅·배칭 키·디스패칭·자원 공유·버퍼/봉쇄·운반 경합 | 동일 |
| L2 "서비스 샘플링" | 투입 시각, 배치 구성, 캘린더 | s_ik를 적합 분포에서 샘플링(공정×자재 조건부) | **서비스시간 분포 검증**: L1과 L2의 차이가 입력분포 오차 | 2주 + 클램프 |
| L3 "도착 샘플링" | 캘린더만 | 도착과정(시공일 역산)과 배치 구성도 샘플링 | **도착모형 검증**: 3–12개월 송장/시공캘린더 KPI와 비교 | 종이 기록 |
| L4 "자유 실행" | 없음 | 전부 | 복제 타당성(통상의 검증) | 전부 |

[추론] 이 사다리는 Ghasemloo et al.(2026)의 "부분 입력 고정" 프레임을 실무적으로 번역한 것이다. 각 단계 간 잔차 변화가 그 단계에서 풀어준 요소의 오차 크기다: Δ(L1→L2) ≈ 서비스 분포 오차, Δ(L2→L3) ≈ 도착 모형 오차.

**주의 — 무엇을 "서비스시간"으로 강제할 것인가** [추론]:
- 전류 클램프는 **기계 가동 구간**을 주지, 배치 ID를 주지 않는다. 광전 카운터는 **부품 수**를 준다. 추적표는 배치별 start/end를 분 단위로 준다. 세 가지를 결합해 s_ik를 정의할 때, "start/end"가 **작업자 기준(세팅 포함)**인지 **기계 가동 기준**인지 명시해야 한다. 세팅·검사·이동이 포함된 작업자 기준 시간을 쓰고, 클램프의 순수 가동시간은 **교차검증용**으로만 쓰는 것이 안전하다.
- 재단(패널소)·CNC는 "배치"가 아니라 "원판(sheet) 묶음" 단위로 돌아가고, 엣지밴딩·조립은 "부품"→"배치" 단위로 돌아간다. 단위 변환(네스팅: 여러 주문의 부품이 한 원판에 섞임)이 그 자체로 구조 가설이므로 L1에서 시험 대상이다.

### 2.3 구조 잔차의 정의와 계산

배치 i, 공정 k에 대해 (관측: a=도착, b=시작, e=종료; 모델: â, b̂, ê):

- 대기 잔차: r^q_ik = (b̂_ik − â_ik) − (b_ik − a_ik)
- 이동/전달 잔차: r^m_ik = (â_{i,k+1} − ê_ik) − (a_{i,k+1} − e_ik)
- 시작시각 잔차(누적): r^b_ik = b̂_ik − b_ik  (상류 오차가 누적되므로 진단용으로는 r^q를 우선)
- 순서 잔차: 공정 k에서 관측 처리순서 π_k와 모델 처리순서 π̂_k의 Kendall τ_k (1−τ_k가 디스패칭 불일치 척도)
- 라우팅 잔차: 배치별 관측 공정열과 모델 공정열의 편집거리(루프·건너뜀 포함)
- 자원 점유 잔차: 클램프 가동 구간과 모델 가동 구간의 Jaccard 유사도(기계별)

정규화: 잔차를 그 공정의 중앙 서비스시간 s̃_k로 나누어 ρ_ik = r_ik / s̃_k (무차원)로 보고한다. [추론] 분 단위 종이 기록의 해상도 한계(±5–10분)보다 작은 잔차는 해석하지 않는다. 1977년 공항 큐 검증 사례에서도 "도착시각 해상도 부족"이 분포 적합도 검정 실패의 원인으로 지목되었다. [확립: Airport Facility Queuing Model Validation, 1977, https://rosap.ntl.bts.gov/view/dot/9307]

### 2.4 잔차 패턴 → 구조 결함 진단표

[추론 — 큐잉 논리에서 연역한 것으로, 각 행은 "이 결함이 있을 때 L1 재생에서 반드시 이런 잔차가 생긴다"는 필요조건이며 충분조건은 아니다. 2개 이상 지표가 동시에 맞을 때 가설로 채택하고, 카메라 영상으로 확인한다.]

| 잔차 패턴 | 유력 결함 | 보조 확인 |
|---|---|---|
| 공정 k에서 r^q 전부 **음수**(모델이 덜 기다림), 크기가 동시 재공(WIP) 수에 비례 | **자원 누락/과다 설정** — 실제는 작업자 1명이 두 기계를 겸임하는데 모델은 기계마다 전담 | 클램프: 두 기계 가동구간이 상호 배타적(동시 가동 거의 없음)이면 겸임 증거 |
| 공정 k에서 r^q 전부 **양수**, 특히 소량 배치에서 큼 | 모델에 없는 **병렬 자원/우회**(수작업 대체, 임시 작업자) 또는 모델이 셋업을 과대 | 카메라: 다른 위치에서 같은 작업 |
| r^q 부호가 **배치 속성(색상·두께·자재)**에 따라 군집; 순서 잔차 1−τ_k 큼; 관측 처리열에서 같은 속성이 연속 | **배칭 키 오류** — 실제는 엣지밴딩 색상/두께별로 묶어 셋업을 줄이는데 모델은 FIFO | 관측 처리열에서 동일 속성 런 길이 vs 무작위 기대치 |
| 1−τ_k 큼, r^q 부호가 **시공일까지 남은 여유(slack)**와 상관(여유 적은 배치는 음수 잔차 = 실제가 더 빨리 처리) | **디스패칭 규칙 오류** — 실제는 EDD/긴급 우선, 모델은 FIFO(또는 반대) | 시공캘린더와 조인 |
| 공정 k−1에서 r^q **음수**이면서 ê_{k−1} < e_{k−1}, 동시에 공정 k 앞 재공이 관측상 상한에 머무름 | **봉쇄(blocking) 누락** — 하류 버퍼(바닥 적치 공간) 유한 | 카메라: 적치 공간 포화 시점과 상류 정지 시점 일치 |
| r^m(이동 잔차) **양수**가 **동일 시간대의 여러 배치**에 동시에 발생; 실제 전달이 "몰려서" 일어남 | **운반 경합/운반 배칭** 누락 — 지게차·대차 1대, 또는 "쌓였다가 한 번에 옮김" | 카메라: 운반 사건 시각 클러스터링 |
| r^m 크고 하루 중 특정 시각(휴식 직후, 교대 직전)에 집중 | **캘린더/휴식** 누락 또는 잘못된 시프트 | 클램프: 전 기계 동시 휴지 구간 |
| 배치의 라우팅 편집거리 > 0; 일부 배치만 공정 열에 "구멍"(예: 도장 공정 없음) 또는 외부 소멸 후 재출현 | **라우팅/외주 경로 오류** — 외주 도장·유리·철물 병렬 경로, 조건부 분기 | 발주서(외주 발주 시각)와 조인 |
| 같은 배치가 같은 공정에 두 번 등장(자기 루프)하는데 모델 라우팅엔 없음; 또는 모델에 루프가 있는데 관측엔 없음 | **재작업 루프** 오지정 | 프로세스 마이닝의 self-loop/repetition 필터 [확립: Fluxicon, bupaR] |
| 관측 배치 수량이 공정 사이에서 줄거나(분실) 늘어남(병합); 모델은 원자 배치 | **부품 식별 손실/배치 분할·병합** 미모델링 | 광전 카운터 수량 vs 재단표 수량 |
| r^q가 **재공 체류시간이 긴 배치**에서 음수 (오래 기다린 배치를 실제가 우선 처리) | **동적 우선순위/독촉(expediting)** 미모델링 | 추적표 비고란 |
| 잔차 평균 ≈ 0이나 **분산**이 큼, 특정 패턴 없음 | 구조는 맞고 **기록 해상도/기록 오류** 혹은 모델링 수준에 없는 미시 사건 | 해상도 한계와 비교; 더 쪼개지 말 것 |

### 2.5 실무 절차(2주 데이터 기준)

1. **L0 완전 재생**으로 먼저 모델 코드의 버그를 제거한다(관측 라우팅·순서·시간을 다 넣으면 모델은 추적표를 그대로 복제해야 한다; 못 하면 검증 이전 문제). Balci의 **trace 분석**과 Sargent의 **traces** 기법이 바로 이것이다. [확립: Sargent 2013, *Verification and validation of simulation models*, J. Simulation 7:12–24, https://ics-websites.science.uu.nl/docs/vakken/msosi/VerificationValidationSargent.pdf]
2. **L1 구조 재생**: 라우팅·순서·배칭을 모델 논리에 맡긴다. 공정별 ρ_ik 분포, τ_k, 편집거리를 산출하고 §2.4 표에 대조한다.
3. 결함 가설마다 **하나씩** 모델을 수정하고 L1을 재실행 → 잔차 감소를 확인한다(한 번에 하나만 고쳐야 보상 효과를 피한다).
4. L1 잔차가 기록 해상도 수준으로 수렴하면 **L2(서비스 샘플링)**로 넘어가 분포 적합도를 검정한다.

---

## 3. 이벤트 타당성·트레이스 비교·회귀 검증·Little 법칙 — 소표본 적용

### 3.1 Balci·Sargent의 기법 명칭과 본 과제 적용

Balci(1998)는 77개 V&V 기법을 비형식·정적·동적·형식으로 분류했고 [확립: Balci 1998, *Verification, validation, and accreditation*, WSC, https://www.informs-sim.org/wsc98papers/006.PDF], Sargent(2013)의 기법 목록 중 본 과제에 직접 대응하는 것은 다음과 같다 [확립: Sargent 2013; WSC 2010 재수록 https://www.informs-sim.org/wsc10papers/016.pdf]:

- **Event validity**: "모델의 사건 발생을 실제 시스템의 사건 발생과 비교" (예: 소방서 모델의 화재 횟수). 본 과제에서는 광전 카운터의 **공정별 통과 부품 수/일**, 클램프의 **기계별 가동 개시 횟수/일**, 추적표의 **재작업 발생 횟수**, 발주서의 **외주 반출 건수**를 모델 사건 수와 비교한다. 작은 표본에서도 Poisson/이항 정확검정이 가능하므로 가장 먼저 쓸 수 있는 검정이다.
- **Traces**: 특정 개체를 모델 안에서 추적해 논리가 맞는지 보는 것 — L0와 동일.
- **Predictive validation**: "모델로 시스템 행동을 예측하고 실제 행동과 비교" — 2주 중 1주차로 조정하고 2주차를 예측하는 **홀드아웃**이 최소 형태. Sargent의 **historical data validation**도 같은 맥락(일부로 구축, 나머지로 시험).
- **Comparison to other models**: 단순 큐잉 근사(Kingman VUT 식, Little 법칙, 결정론적 CPM 역산)와 비교. 가구 공장처럼 분석해가 없는 경우 "모델 간 비교"는 **상한·하한 모델**(무한 자원 모델 = 흐름시간 하한, 단일 서버 직렬 모델 = 상한)과의 비교로 운용한다. [추론] Kingman 근사와 Little 법칙을 벤치마크로 쓰는 실무 사례가 있다. [확립: FHWS 보고서 https://opus4.kobv.de/opus4-fhws/files/1906/challenges_using_kingman_eq_for_pred_val3.pdf]
- **Turing test**(Schruben 1980): 공장장에게 실제 추적표와 모델 생성 추적표(같은 양식)를 섞어 제시하고 구분하게 한다. 소표본에서는 통계보다 이 방식이 더 강력한 경우가 많다 — 현장 전문가는 "이 배치가 이 순서로 나올 리 없다"를 즉시 짚는다. [확립: Schruben 1980, *Establishing the credibility of simulations*, Simulation 34(3); Robinson의 white-box validation]
- **Degenerate/extreme condition tests**: 주문을 0으로, 또는 한 공정의 서비스시간을 10배로 — 보상 결함 검출에 특히 중요(§4.3).

### 3.2 Kleijnen의 회귀 기반 트레이스 검증

Kleijnen, Bettonvil & van Groenendaal(1996, 1998)의 검정: 배치별 (모델 출력 − 실제 출력)을 (모델 출력 + 실제 출력)에 회귀하여 **기울기 = 0 과 절편 = 0**을 동시에 F-검정한다. 귀무가설은 "두 출력의 평균과 분산이 같다"이며, 통념적인 "모델을 실제에 회귀해 기울기 1, 절편 0 검정"은 교차상관 때문에 **타당한 모델을 과도하게 기각**함을 Monte Carlo로 보였다. [확립: WSC 1996 https://www.informs-sim.org/wsc96papers/047.pdf; Management Science 44(6):812–819, 1998] 후속으로 Kleijnen, Cheng & Bettonvil(2001)은 복제 실행 기반 **부트스트랩** 검정을 제안해 단일 서버 큐에서 제1종·제2종 오류가 수용 가능함을 보였다. [확립: MS 47(11), 2001]

본 과제 적용 [추론]:
- 반응변수로 **종단 흐름시간**이 아니라 **공정별 대기시간 q_ik**를 쓴다(공정별로 검정해야 결함 위치가 드러남).
- 관측 대기 q_ik와 모델 대기 q̂_ik의 쌍 (i=1..n_k)에서 d_i = q̂_i − q_i, s_i = q̂_i + q_i 로 회귀. n_k = 10–30, 회귀 자유도 n_k−2.
- 가정(잔차 정규·등분산)은 대기시간이 0에 쌓이는(zero-inflated) 경우 깨진다. 대기 0인 배치가 절반이면 회귀 대신 **부호검정/Wilcoxon** 또는 2001년의 부트스트랩판을 쓴다.
- 본 보고서의 간이 Monte Carlo [계산]: 감마(2,1) 대기에 작은 잡음(sd 0.3)을 더한 설정에서 n=10일 때 귀무 기각률 0.05(명목 유지), n=20에서 0.06, n=30에서 0.08 — 소표본에서 제1종 오류는 유지되나, 잡음이 커지면 검정력은 급락한다(§5).

### 3.3 Little 법칙 일관성 검사

L = λW는 정상상태 장기평균에 대한 법칙이다. Kim & Whitt(2013)는 **유한 관측창**에서 창 경계가 비어 있지 않을 때의 **편향 보정**과 배치평균 기반 신뢰구간을 제시했고 [확립: Kim & Whitt 2013, *Statistical analysis with Little's law*, Oper. Res. 61(4):1030–1045, https://pubsonline.informs.org/doi/10.1287/opre.2013.1193], 도착률이 시간에 따라 변하고 체류시간이 길면 단순 간접추정이 크게 편향되므로 **시간변동 Little 법칙**(time-varying Little's law)을 써야 함을 보였다 [확립: Kim & Whitt, *Estimating waiting times with the time-varying Little's law*, PEIS]. 2주 창에 배치 체류 수일인 본 과제는 정확히 이 조건이다.

세 가지 용도 [추론]:
1. **데이터 자체의 일관성**: 카메라로 센 평균 재공(L_obs)과 추적표의 λ·W가 창 보정 후 ±20% 내인지. 틀리면 "부품 식별 손실"이나 "기록 누락"의 신호(§4.3).
2. **공정별 재공 보존**: 공정 k의 (유입 수 − 유출 수) 누적이 카메라 재공과 맞는지. 광전 카운터로 공정별 유입/유출을 세면 **배치 ID 없이도** 가능하다.
3. **모델–데이터 일관성**: 모델이 L, λ, W를 각각 맞추는지 — 셋 중 둘만 맞으면 나머지 정의(특히 "도착" 시점 정의: 발주 시각 vs 재단표 발행 시각 vs 투입 시각)가 다른 것이다.

**경고** [확립+계산]: n≈20 배치, 2주 창에서는 경계효과가 전체 체류시간의 상당 부분을 차지하므로 Little 법칙은 **검정이 아니라 정합성 점검**으로만 써야 한다. 창을 "첫 배치 도착 ~ 마지막 배치 완료"로 닫아 잡으면 항등식은 정확히 성립하나(본 보고서 간이 계산에서 비율 = 1.000), 그렇게 잡은 창은 공장의 실제 2주와 다르다.

### 3.4 소표본(10–30 배치)에서의 적용 원칙 [추론, 통계 일반론에 근거]

- **검정보다 추정**: p-value 대신 잔차의 **효과크기와 신뢰구간**(또는 동치검정 TOST로 "허용범위 안에 있음"을 보이는 Sargent의 range-of-accuracy 접근). Sargent는 운영 타당성을 "모델의 정확도 범위"로 정의하며, 가설검정 시 모델 구축자 위험(타당한 모델을 기각)과 사용자 위험(부당한 모델을 채택)을 함께 통제할 것을 요구한다. [확립: Balci & Sargent 1981, *A methodology for cost-risk analysis in the statistical validation of simulation models*, CACM 24(4):190–197; Sargent 2013]
- **쌍대 설계의 이점**: 트레이스 구동은 모델과 실제를 **같은 배치**에서 쌍으로 비교하므로 입력 변동이 상쇄된다. 이것이 소표본에서 검정력을 확보하는 유일한 구조적 방법이다. Kleijnen 2001도 같은 논리(교차상관을 이용)를 따른다.
- **다중비교**: 공정 6개 × 지표 3개 = 18개 검정을 α=0.05로 하면 거짓양성이 거의 확실. Holm 보정 또는 "패턴 기반 해석"(§2.4 표처럼 두 지표가 같은 결함을 가리킬 때만 채택).
- **비모수 우선**: 대기시간은 0 과잉·우측 꼬리이므로 부호검정(n=10이면 10개 중 9개 이상 같은 부호여야 양측 p<0.05)과 Wilcoxon을 기본으로 한다.

---

## 4. 검증 순서: 구조 → 결정적 시간 → 변동성 → 규칙

### 4.1 이 순서를 지지하는 근거

- Zeigler: 구조 타당성 ⇒ 예측 타당성 ⇒ 복제 타당성. 상위를 확보하면 하위가 따라오므로 상위부터 시험하는 것이 효율적. [확립]
- Barlas: 인과·서술 모델에서는 "구조 신뢰성 확립이 행동 신뢰성에 **엄격히 선행**해야 하며, 전자 없는 후자는 가치가 없다"; 시험을 구조 시험 → 구조지향 행동 시험 → 행동 패턴 시험 순으로 배열. [확립: Barlas 1996, *Formal aspects of model validity and validation in system dynamics*, SDR 12(3); Barlas 1994 flowchart https://archives.albany.edu/concern/daos/zs25xt134]
- Robinson(2004): 개념모델 검증 → 데이터 검증 → white-box(미시) → black-box(거시) → 실험·해 검증. [확립: Robinson, *Simulation: The Practice of Model Development and Use*; WSC 1997 https://www.informs-sim.org/wsc97papers/0053.PDF]
- Sargent: 개념모델 타당성 → 전산모델 검증 → 운영 타당성, 데이터 타당성은 전 과정. [확립]
- Kleijnen 1995: 검증 단계에서 "모듈별 중간 출력의 추적과 통계검정" 후에 최종 출력 검증. [확립: Kleijnen 1995, EJOR 82(1):145–162]

이 문헌들은 모두 **"내부(구조) 먼저, 외부(행동) 나중"**에 수렴한다. 본 과제의 "구조 → 결정적 시간 → 변동성 → 규칙"은 이를 DES 운영 용어로 바꾼 것으로, 앞의 세 단계는 잘 지지된다.

### 4.2 반론과 수정 [추론]

1. **"규칙"은 구조의 일부다.** 디스패칭·배칭·릴리스 규칙은 DES에서 라우팅·자원과 같은 층위의 구조 가정이며, Ahn(MSU)은 디스패칭 규칙 선택이 릴리스 메커니즘보다 성능에 더 큰 영향을 준다고 보고했다. [확립: https://d.lib.msu.edu/etd/28742/OBJ/download] Thürer et al.(2014)은 상충하는 선행 연구 결과가 "풀(pool) 내 작업 순서 규칙"이라는 무시된 요인으로 설명됨을 보였다 — 규칙을 마지막으로 미루면 앞 단계의 결론이 뒤집힐 수 있다. [확립: Thürer et al. 2014, IJPR, https://eprints.lancs.ac.uk/id/eprint/68845/] 따라서 규칙은 **L1 단계에서 구조와 함께** 시험한다(순서 잔차 τ_k가 그 도구).
2. **변동성이 있어야 드러나는 구조가 있다.** 봉쇄·운반 경합·작업자 겸임은 재공이 쌓일 때만 작동한다. 2주 관측창이 한가한 기간이었다면 L1 잔차가 0이어도 구조가 검증된 것이 아니라 **식별 불가능**한 것이다. 관측창의 부하(ρ)를 반드시 보고하고, 부하가 낮았다면 "구조 검증은 부하 ≤ 관측 수준에서만 유효"로 적용범위를 한정한다. Sargent도 "여러 실험 조건에서 충분한 정확도를 보여도 모델의 전체 적용 영역에서의 타당성은 보장되지 않는다"고 명시한다. [확립: Sargent 2001, https://informs-sim.org/wsc01papers/013.PDF]
3. **실용적 순서(수정안)**: L0(코드 검증) → L1(구조+규칙, 결정론적) → 이벤트 타당성(건수) → L2(서비스 변동성) → L3(도착 모형) → 극단조건/민감도 → 예측(홀드아웃). 각 단계는 "앞 단계 잔차가 기록 해상도 이내"를 진입 조건으로 한다.

### 4.3 두 결함이 서로 보상할 때

**현상**: 자원 누락(대기 과소)과 서비스시간 과대(처리 지연)가 합쳐져 종단 흐름시간은 맞는다. 지구과학에서 Oreskes et al.(1994)은 "모델 결과는 결코 유일하지 않다"는 비유일성을, Beven(2006)은 "서로 다른 구조/파라미터 집합이 동등하게 관측을 재현한다"는 **등결과성(equifinality)**을, Kirchner(2006)는 "옳은 이유로 옳은 답"의 필요성을 정식화했다. [확립: Oreskes, Shrader-Frechette & Belitz 1994, Science 263:641–646, https://science.whoi.edu/users/mcgillic/12_823/2021/Model_evaluation_May_10/oreskes_etal_94.pdf; Beven 2006, J. Hydrology 320:18–36, https://eprints.lancs.ac.uk/id/eprint/4419; Kirchner 2006, WRR] DES 문헌에서 이 주제를 정면으로 다룬 논문은 본 조사에서 찾지 못했으며(Tsioptsias, Tako & Robinson의 "틀린 모델도 유용한가"는 수용성 문제이지 보상 오차 문제는 아님), 아래는 [추론]이다.

**검출 전략**:
1. **분해된 잔차**: 종단이 아니라 공정별·성분별(q, s, m) 잔차를 본다. 보상은 대개 다른 공정/다른 성분 사이에서 일어나므로 분해하면 각각 드러난다. 트레이스 구동에서 s를 강제하면 "s 과대"라는 보상 항이 애초에 생기지 않는다 — 이것이 보상 결함에 대한 가장 강한 방어다.
2. **불변량 검사**: Little 법칙·재공 보존·자원 가동률(클램프)은 흐름시간과 독립적으로 각각 맞아야 한다. 가동률이 틀리면서 흐름시간이 맞으면 보상의 증거.
3. **체제 변경(regime shift) 시험**: 보상은 특정 부하에서만 성립한다. 2주 안의 바쁜 날/한가한 날, 3–12개월 기록의 성수기/비수기로 나누어 각각 적합도를 본다(parameter variability/sensitivity 기법). 극단조건(주문 2배)에서 보상 쌍은 갈라진다.
4. **부분 트레이스 조건화**(Ghasemloo et al. 2026): 입력 하나씩 고정/해제하며 어느 입력이 불일치를 만드는지 귀속.
5. **한 번에 하나만 고친다**: 두 파라미터를 동시에 조정해 KPI를 맞추는 "캘리브레이션"은 금지. 조정은 L1 잔차가 가리키는 결함 하나에만 허용하고, 조정 후 **모든** 잔차 지표가 동시에 개선되어야 채택.
6. **설명 불가능한 조정은 기록**: 물리적 근거 없이 맞춘 파라미터(예: "조립 시간 ×1.3")는 보상 결함의 잠복 지표로 목록화해 트윈의 적용범위 제한에 반영.

---

## 5. 주문가구 공장 특유의 함정과 트레이스 검출법

### 5.1 시공일 기반의 시간변동 도착

주문가구는 **시공일에서 역산**해 투입된다(업계 지침: 설치일을 정하고 리드타임+여유를 빼서 발주·투입; 선택사항 확정 후에야 릴리스). [확립(업계 자료): Eagle Woodworking, https://www.eaglewoodworking.com/blog/cabinet-job-scheduling-problems-and-how-to-fix-them; MRPeasy backward scheduling] 결과적으로 도착은 비정상(non-stationary)이고 월말·입주 시즌에 군집한다.

- **검출**: Kim & Whitt(2014)의 조건부 균등 KS 검정은 구간별 비동질 Poisson(NHPP) 가설을 검정하되, 반올림·구간 내 과도한 율 변화·주별 율 차이로 인한 과분산을 처리해야 함을 보였다. [확립: Kim & Whitt 2014, MSOM 16(3):464–480, https://pubsonline.informs.org/doi/fpi/10.1287/msom.2014.0490] 본 과제는 3–12개월 발주서로 주·일 단위 율을 추정하고, "도착 = 시공일 − 상수"가 아니라 "도착 = 시공일 − (리드타임 분포)"임을 시공캘린더와 재단표 발행일의 차이 분포로 확인한다.
- **트레이스 검출**: L3에서 도착을 샘플링했을 때만 월별 KPI가 틀리고 L1/L2에서는 맞으면 도착 모형 오류. L1에서도 순서 잔차가 slack과 상관되면 시공일이 **디스패칭에도** 쓰이는 것(구조).
- **함정**: 시공일 지연(현장 사정)으로 완성품이 창고에 머무는 시간은 생산 리드타임이 아니다. 송장 기준 "완료"와 출하 기준 "완료"를 분리하지 않으면 W가 과대평가된다. [추론]

### 5.2 외주 병렬 경로

도장·유리·철물·특수가공을 외주로 보내 조립 전에 합류시키는 **병렬 분기–합류** 구조. 합류 대기(assembly wait for the slowest branch)가 리드타임을 지배하는 경우가 많다.
- **트레이스 검출**: L1에서 조립 공정의 r^q가 양수(모델이 더 기다림)이고 외주 품목이 있는 배치에만 집중 → 모델이 외주 리드타임을 과대/합류 논리 오류. 반대로 음수이면 외주를 "즉시 도착"으로 모델링한 것. 발주서의 외주 발주/입고 시각을 L0에 강제하여 재생하면 합류 논리 버그를 분리할 수 있다.
- **함정**: 외주 리드타임은 분포가 아니라 **외주업체의 배칭**(주 2회 수거)으로 결정되므로 캘린더형 모델이 맞을 수 있다. 2주 자료로는 외주 분포 추정이 불가능하므로 L3 이전에는 반드시 강제한다.

### 5.3 부품 식별 손실

패널 가구는 한 주문이 수십 개 부품으로 쪼개져 네스팅(여러 주문 혼합 재단) → 부품 단위 엣지밴딩/타공 → 주문 단위 재조립된다. 라벨 분실·오분류 시 부품을 찾거나 재재단하며, 이는 기록에 "대기"로 나타나거나 아예 기록되지 않는다. 프로세스 마이닝 문헌이 정리한 로그 품질 문제(누락 사건, 부정확 타임스탬프, 사례 ID 누락 — "elusive case" 패턴)가 그대로 적용된다. [확립: Bose, Mans & van der Aalst 2013, *Wanna improve process mining results?*, https://research.tue.nl/en/publications/wanna-improve-process-mining-results-its-high-time-we-consider-da-2/; Suriadi et al. 2017; Fluxicon data quality https://fluxicon.com/book/read/dataquality/]
- **트레이스 검출**: (a) 광전 카운터의 공정별 유입−유출 보존 위반(부품이 "사라졌다가" 재단에 재등장), (b) 재단 공정의 자기 루프(재재단)가 추적표에 없는데 카운터/클램프에는 있음, (c) L1 r^q가 소수 배치에서 극단적 양수(실제가 훨씬 오래 기다림)이면서 다른 지표 정상 → 식별 손실 가설. 카메라로 확정.
- **모델링 함의**: 이 현상은 "서비스시간 분포의 긴 꼬리"로 흡수되기 쉽다 — 전형적 보상 결함. 재작업/탐색 사건을 **별도 사건**(확률 p, 지연 분포)으로 모델링해야 L2에서 분포가 정상화된다. [추론]

### 5.4 재작업 루프

- **검출**: 추적표에서 같은 배치가 같은 공정에 비연속 재등장(repetition) 또는 연속 재등장(self-loop). Fluxicon의 "직접 반복 필터 → eventually-follows 필터" 절차가 표준. [확립: https://fluxicon.com/blog/2017/03/how-to-identify-rework-in-your-process/] Rozinat & van der Aalst의 적합성 검사(conformance checking)는 모델과 로그의 불일치를 fitness/precision/structure 차원으로 정량화하며, 재생(replay) 기반 정렬로 "어느 사건이 모델의 어느 요소와 안 맞는지"를 짚는다 — L1의 라우팅 편집거리는 이것의 간이판이다. [확립: Rozinat & van der Aalst 2005/2008, https://vdaalst.com/publications/p284.pdf; van der Aalst 2018 "Process mining and simulation: a match made in heaven!", https://www.vdaalst.com/publications/p1002.pdf]
- **함정**: 2주에 재작업이 2–3건이면 확률 p의 신뢰구간이 0–30%에 이른다. 3–12개월 송장의 "재시공/AS" 기록으로 p를 보강하고, 2주 자료는 루프의 **존재와 위치**(구조)만 확인하는 데 쓴다. [추론]

---

## 6. 얼마나 많은 데이터가 필요한가

### 6.1 유효 표본의 단위 [추론]

구조 결함은 공정에 국소적이므로 공정 k의 검정에 쓰이는 유효 표본은 **그 공정을 지난 배치 수 n_k**(≈ 10–30)이지, 배치×공정의 곱이 아니다. 라우팅·순서 잔차는 공정 간 상관이 강하므로 더 줄어든다. 다만 "이벤트 타당성"(부품 수, 가동 개시 횟수)은 **일 단위**(10 근무일)와 **부품 단위**(수백~수천)로 집계되므로 표본이 훨씬 크다 — 소표본 프로젝트에서 사건 건수 비교를 먼저 하는 이유다.

### 6.2 검정력: 쌍대 잔차 검정 [계산]

쌍대 t-검정(양측 α=0.05)에서 80% 검정력으로 검출 가능한 최소 표준화 효과 d = (평균 잔차)/(잔차 표준편차):

| n_k | 10 | 15 | 20 | 30 | 50 |
|---|---|---|---|---|---|
| 최소 검출 d | 1.0 | 0.78 | 0.66 | 0.53 | 0.40 |

부호검정(양측 α=0.05): 잔차가 한쪽 부호일 확률 0.75일 때 검정력은 n=10: 0.24, 20: 0.62, 30: 0.80; 0.85일 때 n=10: 0.54, 15: 0.82, 20: 0.93.

**해석**: 10–20 배치로는 잔차 평균이 잔차 산포의 **0.7–1.0배 이상**인 결함만 잡힌다. 트레이스 구동은 입력 변동을 제거해 잔차 산포를 줄이므로(관측 대기 자체의 분산이 아니라 **모델–관측 차이**의 분산만 남음), 같은 n에서 자유 실행보다 훨씬 작은 결함을 잡는다. 이것이 소표본에서 트레이스 구동을 써야 하는 정량적 이유다. §2.4 표의 결함(자원 누락, 봉쇄, 배칭 키)은 전형적으로 잔차 ≥ 서비스시간 1회분(= 해당 공정 대기의 산포와 비슷하거나 큼)을 만들므로 n=10–20에서 검출 기대가 합리적이다. 반면 "EDD vs SPT" 같은 디스패칭 미세 차이는 순서 잔차로만 나타나며 n≥30과 혼잡한 관측창이 필요하다.

### 6.3 검정력 계산의 실무적 방법: 결함 주입(fault injection) [추론]

이론적 검정력은 잔차 분포를 알아야 하므로 현실적이지 않다. 대안:
1. 현재 모델(가설 M0)에 결함 하나를 **의도적으로 주입**(예: 겸임 작업자를 전담으로, 버퍼를 무한으로, 배칭 키 제거).
2. 같은 트레이스로 L1 재생 → 잔차 벡터 r^(fault) 를 얻는다.
3. M0의 잔차 r^(0)와 비교해 선택한 검정(부호/Wilcoxon/Kleijnen 회귀)이 기각하는지 본다. 부트스트랩(배치 재표본)으로 기각률을 추정하면 그것이 **그 결함에 대한 그 n에서의 경험적 검정력**이다.
4. 검정력 < 0.5인 결함은 "현 데이터로 식별 불가"로 문서화하고 트윈 적용범위에서 제외하거나 추가 로깅을 요청한다.

이는 소프트웨어의 변이 검사(mutation testing)와 Kleijnen의 Monte Carlo 검정력 평가를 결합한 것이다. Lugaresi et al.(2019)의 "quasi trace-driven simulation"과 신호처리 기반 실시간 검증도 "대량 데이터 없이" 모델 정렬을 판정하려는 같은 동기에서 출발한다. [확립(초록): Lugaresi, Aglio, Folgheraiter & Matta 2019, IEEE CASE, https://re.public.polimi.it/handle/11311/1110279; Lugaresi et al. 2022 WSC https://informs-sim.org/wsc22papers/294.pdf]

### 6.4 데이터 수집 최소 조건 [추론]

- **배치**: 공정당 ≥15–20 배치가 2주 안에 지나가야 한다. 소량 공정(특수 도장)은 2주로는 불가능 — 강제 처리.
- **부하**: 관측창에 재공이 쌓인 날이 최소 3–4일 포함되어야 구조가 식별된다. 한가한 2주는 구조 검증에 거의 무가치하다(대기 0 → 잔차 0 → 모든 구조가 동등). 로깅 시작 전 공장장에게 "다음 2주가 평상시보다 한가한가"를 반드시 묻는다.
- **해상도**: 추적표는 5분 단위 이상, 클램프는 초 단위. 공정 서비스시간 중앙값의 1/5보다 거친 기록은 그 공정의 잔차 해석을 불가능하게 한다.
- **입력 데이터 관리 공수**: Skoogh & Johansson(2008)은 입력 데이터 관리가 DES 프로젝트 시간의 주된 소모처임을 보이고 13개 활동 방법론을 제시했다. 2주 로깅 설계 전에 이 체크리스트를 적용할 것. [확립: Skoogh & Johansson 2008, WSC, https://research.chalmers.se/publication/79631]

---

## 7. 공장에 요청할 최소 기록 양식, 그리고 완료시각만 있을 때

### 7.1 최소 기록 양식(2주 배치 추적표 개정안) [추론, §2–5의 요구를 역산]

**배치-공정 행(한 줄 = 한 배치가 한 공정을 한 번 지남)**:

| 필드 | 이유 |
|---|---|
| 배치 ID(재단표 번호) + 주문 ID + 시공일 | 트레이스 연결, slack 계산(디스패칭 검정) |
| 공정명, 자원(기계/작업자 이름) | 자원 공유·겸임 검출 |
| 도착 시각, 시작 시각, 종료 시각, 다음 공정 전달 시각 | q, s, m 분해의 전제 |
| 부품 수(입력/출력) | 식별 손실·분할·병합 검출(Little/보존) |
| 그룹핑 키: 색상, 두께, 자재, 엣지 종류 | 배칭 키 검정 |
| 함께 처리한 다른 배치 ID(같은 원판/같은 셋업) | 네스팅·셋업 배칭 구조 |
| 재작업 플래그 + 사유 | 루프 구조/확률 |
| 외주 반출/반입 시각 + 업체 | 병렬 경로 강제 |
| 대기 사유 한 단어(자재 없음/작업자 없음/공간 없음/부품 찾는 중/다른 급한 일) | 봉쇄·경합·독촉의 직접 라벨 — 가장 가치 높은 열 |

**일별 행**: 근무 시작/종료, 휴식, 결근자, 기계 고장 구간, 외주 수거 시각, 당일 "급한 주문" 지정 여부.

**연결 키**: 재단표 ↔ 발주서 ↔ 시공캘린더 ↔ 송장을 주문 ID 하나로 잇도록 요청. 기존 종이 기록에 공통 키가 없으면 2주 동안만이라도 스티커 번호를 부여한다.

**센서와의 정합**: 클램프 채널 ↔ 기계명, 카운터 위치 ↔ 공정 경계, 카메라 시야 ↔ 적치 공간(버퍼)을 설치 당일 문서화. 카메라는 **버퍼**(바닥 적치)를 보게 두는 것이 기계를 보는 것보다 구조 검증에 유리하다 — 봉쇄와 재공 수를 직접 준다. [추론]

### 7.2 완료시각(또는 출하/송장)만 있을 때

이 상황은 Kleijnen의 "출력 데이터만" 상황이며 구조/입력 분리는 **부분적으로만** 가능하다. 할 수 있는 것과 없는 것:

1. **큐 재구성(queue inference)**: Larson(1990)의 Queue Inference Engine은 거래(완료) 시각만으로 Poisson 도착 가정 하에 큐 통계를 추론한다. [확립: Larson 1990, *The queue inference engine: deducing queue statistics from transactional data*, Management Science 36(5)] 본 과제에서는 클램프의 기계 가동 구간이 **서비스 시작/종료**를 주므로, 완료 순서와 가동 구간을 매칭해 배치별 b_ik, e_ik를 재구성할 수 있다(가동 구간 수 = 배치 수일 때 1:1 매칭; 아니면 네스팅 가설이 필요). 도착 a_ik는 상류 공정의 e_{i,k−1} + 이동시간 가정으로 대체 — 이 가정 자체가 검증 대상이므로 r^m은 식별 불가.
2. **출발 간격 분석**: 연속 완료 간격이 서비스시간보다 짧을 수 없으므로, 간격 ≈ 서비스시간이면 그 구간은 **바쁜 기간**(큐 비어있지 않음), 간격 ≫ 서비스시간이면 유휴. 바쁜 기간의 길이 분포는 구조(자원 수)에 민감하므로 "모델 바쁜 기간 vs 클램프 바쁜 기간" 비교가 가능하다. [추론]
3. **순서 적합성**: 완료 순서와 투입 순서(재단표 발행 순)의 Kendall τ는 디스패칭 규칙의 흔적을 남긴다(FIFO면 τ≈1). 모델의 완료 순서와 비교. [추론]
4. **Little 법칙 간접 추정**: W = L/λ (Kim & Whitt 2013의 창 보정 적용)로 체류시간을 추정하고 모델과 비교 — 단, 구조와 입력이 혼합된 종단 지표.
5. **할 수 없는 것**: 공정별 q와 s의 분리, 따라서 보상 결함 검출. 이 경우 트윈의 신뢰 수준을 "복제 타당성"으로 한정해 보고하고, 2주 추적표 수집을 **다시** 요구하는 것이 정직한 답이다.

---

## 8. 종합 권고 체크리스트

1. 로깅 전: 부하가 평상 수준인 2주를 고르고, 추적표에 "대기 사유"와 그룹핑 키 열을 추가하라.
2. L0 완전 재생으로 코드 버그를 제거하라(추적표를 그대로 복제해야 함).
3. L1 구조 재생에서 공정별 r^q, r^m, τ_k, 편집거리를 산출하고 §2.4 표로 진단하라. 한 번에 하나만 고쳐라.
4. 이벤트 건수(부품 수, 가동 횟수, 재작업, 외주)를 Poisson/이항으로 비교하라 — 소표본에서 가장 검정력이 높다.
5. L2에서 서비스 분포, L3에서 시공일 역산 도착 모형을 검정하라. 12개월 송장으로 월별 KPI를 홀드아웃 예측하라.
6. Little 법칙·재공 보존·가동률을 **각각** 맞추어라. 셋 중 하나가 틀리면 보상 결함을 의심하라.
7. 결함 주입으로 경험적 검정력을 계산해 "식별 불가 결함"을 명시하라.
8. 검증 보고서에는 적용 범위(부하 수준, 공정, 기간)를 명시하고, 물리적 근거 없는 파라미터 조정은 목록으로 남겨라.

---

## 참고문헌

- Balci, O. (1998). Verification, validation, and accreditation. *Proc. WSC 1998*. https://www.informs-sim.org/wsc98papers/006.PDF
- Balci, O. & Sargent, R.G. (1981). A methodology for cost-risk analysis in the statistical validation of simulation models. *Comm. ACM* 24(4):190–197.
- Barlas, Y. (1996). Formal aspects of model validity and validation in system dynamics. *System Dynamics Review* 12(3). Barlas (1994) Model validation in SD: https://archives.albany.edu/concern/daos/zs25xt134
- Beven, K. (2006). A manifesto for the equifinality thesis. *J. Hydrology* 320:18–36. https://eprints.lancs.ac.uk/id/eprint/4419
- Bose, R.P.J.C., Mans, R.S., van der Aalst, W.M.P. (2013). Wanna improve process mining results? https://research.tue.nl/en/publications/wanna-improve-process-mining-results-its-high-time-we-consider-da-2/
- Ghasemloo, M., Eckman, D.J., Li, Y. (2026). Subtrace-conditional validation of simulation models and digital twins. arXiv:2607.17088. https://arxiv.org/abs/2607.17088
- 황보훈, 천현재, 이홍철 (2009). 가중 F 척도를 이용한 Trace-Driven 시뮬레이션 모델의 검증 방법. *한국시뮬레이션학회논문지* 18(4):185–195. https://www.koreascience.or.kr/article/JAKO201210348673804.page
- Khan, A., Dahl, M., Falkman, P., Fabian, M. (2018). Digital twin for legacy systems: simulation model testing and validation. *IEEE CASE*. https://research.chalmers.se/publication/509423
- Kim, S.-H. & Whitt, W. (2013). Statistical analysis with Little's law. *Oper. Res.* 61(4):1030–1045. https://pubsonline.informs.org/doi/10.1287/opre.2013.1193
- Kim, S.-H. & Whitt, W. (2014). Are call center and hospital arrivals well modeled by nonhomogeneous Poisson processes? *MSOM* 16(3):464–480. https://pubsonline.informs.org/doi/fpi/10.1287/msom.2014.0490
- Kim, S.-H. & Whitt, W. Estimating waiting times with the time-varying Little's law. *PEIS*. https://www.cambridge.org/core/product/18BF94EF65D06A5E52B72D1F81F3BFE0
- Kirchner, J.W. (2006). Getting the right answers for the right reasons. *Water Resources Research* 42.
- Kleijnen, J.P.C. (1995). Verification and validation of simulation models. *EJOR* 82(1):145–162. https://ideas.repec.org/p/tiu/tiutis/cb477373-4711-405d-b712-3587bd81e878.html
- Kleijnen, J.P.C., Bettonvil, B., van Groenendaal, W. (1996). Validation of trace-driven simulation models: regression analysis revisited. *Proc. WSC 1996*:352–360. https://www.informs-sim.org/wsc96papers/047.pdf
- Kleijnen, J.P.C., Bettonvil, B., van Groenendaal, W. (1998). Validation of trace-driven simulation models: a novel regression test. *Management Science* 44(6):812–819.
- Kleijnen, J.P.C. (1999). Validation of models: statistical techniques and data availability. CentER DP 1999-104. https://ideas.repec.org/p/tiu/tiucen/f7518d14-a5e9-4c69-a579-6f514489c246.html
- Kleijnen, J.P.C., Cheng, R.C.H., Bettonvil, B. (2001). Validation of trace-driven simulation models: bootstrap tests. *Management Science* 47(11):1533–1538. https://pubsonline.informs.org/doi/fpi/10.1287/mnsc.47.11.1533.10255
- Larson, R.C. (1990). The queue inference engine. *Management Science* 36(5):586–606.
- Law, A.M. & Kelton, W.D. (1991/2015). *Simulation Modeling and Analysis* — correlated inspection approach.
- Lugaresi, G., Aglio, G., Folgheraiter, F., Matta, A. (2019). Real-time validation of digital models for manufacturing systems: a novel signal-processing-based approach. *IEEE CASE*. https://re.public.polimi.it/handle/11311/1110279
- Lugaresi, G., Gangemi, S., Gazzoni, G., Matta, A. (2022). Online validation of simulation-based digital twins exploiting time series analysis. *WSC 2022*. https://informs-sim.org/wsc22papers/294.pdf
- Oreskes, N., Shrader-Frechette, K., Belitz, K. (1994). Verification, validation, and confirmation of numerical models in the earth sciences. *Science* 263:641–646. https://science.whoi.edu/users/mcgillic/12_823/2021/Model_evaluation_May_10/oreskes_etal_94.pdf
- Robinson, S. (1997). Simulation model verification and validation: increasing the users' confidence. *WSC 1997*. https://www.informs-sim.org/wsc97papers/0053.PDF; Robinson (2004) *Simulation: The Practice of Model Development and Use*.
- Roy, C.J. & Oberkampf, W.L. (2011). A comprehensive framework for verification, validation, and uncertainty quantification in scientific computing. *CMAME* 200:2131–2144. https://www.aoe.vt.edu/content/dam/aoe_vt_edu/people/faculty/cjroy/Publications-Articles/VVUQ-CMAME.Final-Accepted-FIGURES.pdf
- Rozinat, A. & van der Aalst, W.M.P. (2008). Conformance checking of processes based on monitoring real behavior. *Information Systems* 33(1). https://vdaalst.com/publications/p284.pdf
- Sargent, R.G. (2013). Verification and validation of simulation models. *J. Simulation* 7:12–24. https://ics-websites.science.uu.nl/docs/vakken/msosi/VerificationValidationSargent.pdf; Sargent (2001) WSC https://informs-sim.org/wsc01papers/013.PDF; Sargent, Goldsman & Yaacoub (2016) WSC https://www.informs-sim.org/wsc16papers/016.pdf
- Schruben, L.W. (1980). Establishing the credibility of simulations. *Simulation* 34(3):101–105.
- Skoogh, A. & Johansson, B. (2008). A methodology for input data management in discrete event simulation projects. *WSC 2008*. https://research.chalmers.se/publication/79631
- Song, E., Nelson, B.L., Pegden, C.D. (2014). Advanced tutorial: input uncertainty quantification. *WSC 2014*. https://informs-sim.org/wsc14papers/includes/files/016.pdf
- Thürer, M. et al. (2014). Continuous workload control order release revisited. *IJPR*. https://eprints.lancs.ac.uk/id/eprint/68845/
- van der Aalst, W.M.P. (2018). Process mining and simulation: a match made in heaven! https://www.vdaalst.com/publications/p1002.pdf
- Zeigler, B.P., Praehofer, H., Kim, T.G. (2000). *Theory of Modeling and Simulation* (2nd ed.). ACIMS 용어집: https://acims.asu.edu/education/education-modeling-and-simulation-all-definitions-p-v
- NSF Workshop (2012). Simulation modeling error taxonomy. https://www.isye.gatech.edu/sites/default/files/documents/conferences/2012wsm/ModelingError.pdf
- Airport Facility Queuing Model Validation (1977). https://rosap.ntl.bts.gov/view/dot/9307
- Fluxicon. How to identify rework in your process (2017). https://fluxicon.com/blog/2017/03/how-to-identify-rework-in-your-process/

**조사 한계 고지**: informs-sim.org, Tilburg, Chalmers, arXiv 원문 PDF는 본 환경의 네트워크 제한으로 직접 열람하지 못했고 초록·2차 인용으로 확인했다. Kleijnen 1998 회귀 검정의 정확한 표본수 권고, Balci 1998의 기법별 원문 정의, Larson 1990의 세부 가정은 원문 확인을 권한다. §2.4 진단표, §4.2 순서 수정안, §6.3 결함 주입 검정력, §7 양식은 본 보고서의 추론이다.