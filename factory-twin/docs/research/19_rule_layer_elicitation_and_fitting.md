# 소규모 주문제작 가구공장 디지털 트윈을 위한 "반장 규칙 계층(rule layer)" 추출·검증 보고서

> 대상: 10–20인 규모, 판넬/MDF 기반, 주문제작(MTO), 시공일(설치일) 기준 납기 구조의 한국 맞춤가구 공장
> 목적: 하루 인터뷰로 수집한 "if … then …" 규칙 카드를 2주간의 현장 기록(공정별 배치 착수 순서, 셋업, 재단리스트)으로 검증하고, 이산사건 시뮬레이션에서 시나리오로 교체 가능한 형태로 인코딩하기 위한 근거와 절차

표기 규칙: **[확립된 연구 결과]**는 복수의 현장연구·실험으로 반복 확인된 내용, **[단일 연구]**는 한 편의 논문에 근거, **[추론]**은 본 보고서가 해당 공장 맥락에 맞춰 도출한 제안입니다. 검색으로 원문·초록을 확인한 출처는 URL을 붙였고, 서지만 기억에 의존한 것은 "(원문 미확인)"으로 표시했습니다.

---

## 1. 현장 계획자/반장은 실제로 어떻게 결정하는가: 경험적 증거

### 1.1 핵심 발견 요약

**[확립된 연구 결과] 현장의 일정 결정은 "최적화"가 아니라 "제약 수집 + 교란 흡수"다.**
- McKay, Safayeni & Buzacott (1988) "Job-Shop Scheduling Theory: What Is Relevant?" (*Interfaces* 18(4)) — 예비 현장연구 결과, 표준 잡샵 이론은 개방형 잡샵의 현실을 대표하지 못한다고 결론. https://pubsonline.informs.org/doi/fpi/10.1287/inte.18.4.84
- McKay, Safayeni & Buzacott (1995) "'Common sense' realities of planning and scheduling in printed circuit board production" (*IJPR* 33(6), 1587–1603) — PCB 공장 심층 현장연구. 공식/비공식 일정 관행을 비교하고, **불안정성(정책 변경, 설비 고장 등)을 다루는 휴리스틱**을 정리했으며, 계획자 전문성의 실체를 논의. https://www.iaorifors.com/paper/14986
- Fox & Smith (1984) ISIS 프로젝트 (원문 미확인, Westinghouse 터빈 공장): 일정 수립을 "제약지향(constraint-directed)" 활동으로 규정. 인간 계획자가 시간의 대부분을 제약 정보 수집에 쓴다는 관찰이 이 연구의 출발점이었습니다.
- Crawford, MacCarthy, Wilson et al. (1999) "Investigating the Work of Industrial Schedulers through Field Study" (*Cognition, Technology & Work* 1, 63–77) — 계획 실무의 인간요인 지식 부족을 지적하고, 현장연구를 가장 적절한 접근으로 제안. https://unpaywall.org/10.1007%2FS101110050033
- Jackson, Wilson & MacCarthy (2004) "A new model of scheduling in manufacturing: tasks, roles, and monitoring" (*Human Factors* 46(3)) — 4개 공장, 7명의 계획자 질적 현장연구. 실무 일정 업무는 **과업(task)·역할(role)·모니터링(monitoring)** 세 가지 활동으로 구성되며, 사업 환경이 계획자 행동을 규정. 많은 컴퓨터 기반 접근이 빠뜨리는 "촉진·실행" 업무를 포함하는 더 넓은 정의를 제안. https://oa.mg/work/10.1518/hfes.46.3.533.1628
- McKay & Wiers (2003) "Planners, schedulers and dispatchers: a description of cognitive tasks in production control" (*Cognition, Technology & Work*) 및 McKay & Wiers (2004) *Practical Production Control* — 중요하고 제약이 강한 결정부터 먼저 내려 문제를 분해한다는 서술이 발췌에서 확인됨. https://research.tue.nl/en/publications/planners-schedulers-and-dispatchers-a-description-of-cognitive-ta/ , https://www.globalspec.com/reference/24684/203279/chapter-5-the-tasks-of-production-control

**[확립된 연구 결과] 재일정(rescheduling)·소방(fire-fighting)이 일상의 대부분이다.**
- MacCarthy & Wilson 편 (2001) *Human Performance in Planning and Scheduling* (Taylor & Francis) — 의류·철강·공작기계·제지·자동차 사례를 모아, 대부분 기업의 일정 업무가 "반응적 재일정"이며 인간 개입 비중이 높다고 정리. 'The Scheduler–Supervisor Relationship' 장은 일정 생성과 실행(반장) 간 연결을 다룸. https://www.routledge.com/products/9780748409297
- Larco Martinelli, Fransoo, Gharehgozli & Wiers (2020) (*IJPR* 58(13)) — 화학공장 계획자 그림자 관찰. 계획자는 DSS의 교란 모니터링보다 **이메일 확인 같은 감지(sensing) 활동**을 우선. 소규모 공장에서 "카톡 확인"이 같은 역할을 할 것이라는 추론의 근거. https://ideas.repec.org/a/taf/tprsxx/v58y2020i13p3944-3955.html

**[확립된 연구 결과] 계획자의 역할은 비공식 권한과 사회적 연결에 의존한다.**
- Berglund & Karltun (2007) "Human, technological and organizational aspects influencing the production scheduling process" (*IJPE* 110, 160–174) — **스웨덴 목공 4개사(제재소, 마루, 가구, 주택)** 현장연구. 일정 결과는 자동화할 수 없는 인간 판단, 설비 제약, 소프트웨어, 그리고 **계획자의 비공식 권한과 조직 간 연결 역할**에 좌우됨. 가구 업종에서 수행된 거의 유일한 계획 실무 현장연구로, 본 프로젝트와 가장 가까운 선행연구. https://ideas.repec.org/a/eee/proeco/v110y2007i1-2p160-174.html
- Gasser, Fischer & Wäfler (2010) "Decision Making in Planning and Scheduling: A Field Study of Planning Behaviour in Manufacturing" (*Behavioral Operations in Planning and Scheduling*, Springer, 11–30) — 스위스 제조사에 자연주의적 의사결정(NDM) 방법 적용. 계획자는 상당한 일반 생산·사업 지식을 동원해 문제를 **인식(recognition)**하고 해결하며, 일상 계획 업무는 지지적 사회기술 환경에 크게 의존. https://ideas.repec.org/h/spr/sprchp/978-3-642-13382-4_2.html

**[단일 연구] 복잡도가 올라가면 계획자는 더 다양한 행동을 쓴다(루틴 회귀가 아님).**
- Fransoo & Wiers (2005 WP / 2006 JOM) "Action variety of planners: cognitive load and requisite variety" — ERP 데이터로 화학공장 계획자 분석. 시간압박 없는 복잡도 증가는 행동 다양성 증가로 이어짐. 즉 **"복잡한 날에는 규칙이 더 많이 섞인다"**는 것을 데이터에서 기대해야 함. https://research.tue.nl/en/publications/action-variety-of-planners-cognitive-load-and-requisite-variety-2/

### 1.2 계획자 행동 모델링의 고전: "한 사람의 규칙을 시뮬레이션으로 복제" 전통

이 프로젝트가 하려는 일(한 반장의 결정 규칙을 모델로 복제하고 실제 결정과 비교)은 1960년대부터 시도된 **행동 시뮬레이션(behavioral simulation)** 전통에 속합니다.
- Dutton (1962) "Simulation of an actual production scheduling and workload control system" (*IJPR* 1(4)) 및 Dutton & Starbuck (1971) "Finding Charlie's run-time estimator" (*Computer Simulation of Human Behavior*, Wiley) (두 편 모두 원문 미확인, 검색으로 서지 확인 실패) — 한 계획자("Charlie")의 결정 과정을 프로토콜 분석과 기록으로 모델링한 사례로 널리 인용됨.
- Hurst & McNamara (1967) "Heuristic Scheduling in a Woolen Mill" (*Management Science* 14(4), B182–B203) — **확인됨.** 특정 계획자의 평균 행동을 기술하는 모델을 만들고, 모델이 생성한 일정과 계획자의 실제 일정을 비교. 불일치를 **"모델의 부적절성"과 "계획자의 비일관성" 양쪽**으로 해석. 이 이중 해석 틀은 6절의 "임계치 미달 시 대응"의 기초가 됩니다. https://pubsonline.informs.org/doi/pdf/10.1287/mnsc.14.4.B182
- Wiers (1996) "A quantitative field study of the decision behaviour of four shopfloor schedulers" (*Production Planning & Control* 7(4)) (원문 미확인) — 현장 계획자 4명의 결정 행동을 정량화한 드문 연구. Stoop & Wiers (1996) "The complexity of scheduling in practice" 와 함께, 실무 계획자 결정의 상당 부분이 교란 대응이며 사람마다 행동이 다르다는 점을 지적. https://research.tue.nl/en/publications/what-is-really-happening-at-the-shop-floor-and-why-do-scheduling-/

### 1.3 소규모 잡샵에서 전형적으로 관찰되는 휴리스틱 (문헌 종합 + 추론)

문헌에서 반복적으로 보고되는 패턴을 가구공장 맥락으로 옮기면 다음과 같습니다. **[추론]** 표시 항목은 해당 업종 관찰에서 유추한 가설이며, 인터뷰에서 확인해야 합니다.

| 결정 | 문헌에서 반복되는 행동 | 가구공장 가설 [추론] |
|---|---|---|
| 순서(sequencing) | 명목상 EDD/FIFO, 실제로는 **셋업·자재·사람 제약이 우선**(McKay 1995; Fox & Smith 1984) | 색상×두께 묶음이 EDD보다 우선; 같은 현장(시공지) 묶음 |
| 배치(batching) | 셋업 회피와 "채우기" 논리; 긴급건은 배치를 깨고 삽입 | 재단기는 색상·두께, 엣지는 띠 색, 타공은 지그/프로그램 단위 |
| 투입(release) | 납기 역산 + **안전 여유 고정값**(예: "설치 3일 전 포장 완료") | 설치일 D-n 투입, n은 현장 거리·시공팀에 따라 변동 |
| 긴급(expediting) | 전화·대면 요청이 가장 강한 트리거(Jackson 2004; Larco 2020) | "사장이 카톡으로 찍어 내리면 최우선" |
| 재배치(reassignment) | 병목으로 다기능 작업자 이동; 신입은 고정 | 엣지→포장, 조립→포장 이동; 재단은 숙련자 고정 |
| 야근/외주 | 백로그가 임계 초과 시 단계적(야근→외주) | 주간 부하 눈대중 + 시공일 집중도 |

**[확립된 연구 결과] 말로 하는 규칙과 실제 행동의 괴리 패턴** (McKay 1995, Crawford 1999, Jackson 2004 종합):
1. 공식 규칙(예: "납기순")은 **예외 조건이 없는 평상시**에만 성립한다.
2. 규칙은 **계층적**이다: 긴급 요청 > 자재/도구 가용성 > 셋업 묶음 > 납기순. 계획자는 상위 조건이 없을 때만 하위 규칙을 적용한다.
3. 결정은 **사람(작업자 역량·출근)**과 **물리(카트·공간)**에 강하게 결합되어 있어, 작업만 보는 규칙으로는 재현이 안 된다.
4. 계획자는 **"하지 않을 일"**(어떤 주문은 절대 쪼개지 않음, 어떤 고객은 절대 늦추지 않음)에 대한 금지 규칙을 많이 갖고 있으며 이것이 말로는 잘 안 나온다.

---

## 2. 하루 안에 작동하는 지식 추출 방법과 "말한 규칙 vs 실제 규칙"의 정확도

### 2.1 자기보고의 한계와 대응 원칙

**[확립된 연구 결과]**
- Nisbett & Wilson (1977) "Telling more than we can know" (*Psychological Review* 84) — 사람은 자기 고차 인지과정에 대한 내성 접근이 제한적이며, 그럴듯하지만 부정확한 인과 설명을 내놓는다. https://resolve.cambridge.org/core/journals/philosophy/article/abs/telling-just-what-we-know-revisiting-nisbett-and-wilsons-stocking-case/2FCDD5A2BEB58FADD86122E80910A705
- Ericsson & Simon (1980, 1993) *Protocol Analysis: Verbal Reports as Data* — **작업기억에 있는 정보에 대한 동시적(concurrent) 구술은 비교적 타당**하지만, 회고적·설명적 보고("왜 그렇게 했나")는 신뢰도가 떨어진다. https://mitpressbookstore.mit.edu/book/9780262550239
- Hoffman (1987) "The problem of extracting the knowledge of experts…" (*AI Magazine* 8); Cooke (1994) "Varieties of knowledge elicitation techniques" (*IJHCS* 41) — 추출 기법을 (a) 관찰/면담, (b) 과정추적(process tracing), (c) 개념적 기법(카드 소팅, 반복 격자 등) 세 계열로 분류. 각 계열은 서로 다른 종류의 지식을 끌어내므로 **복수 기법 조합**이 표준. https://www.cambridge.org/core/books/abs/cambridge-handbook-of-expertise-and-expert-performance/eliciting-and-representing-the-knowledge-of-experts/942AE193BFC25B49F7507F309061C997
- Hoffman, Shadbolt, Burton & Klein (1995) "Eliciting knowledge from experts: A methodological analysis" (*OBHDP* 62) — 기법 비교 연구 정리. 관련 선행연구(Burton, Shadbolt, Rugg & Hedgecock 1990)에서는 **프로토콜 분석이 흔히 쓰이지만 가장 비효율적**이었고, 구조화 면담이 시간 대비 규칙 산출량에서 유리. Schweickert et al. (1987)에서 구조화 면담과 카드 소팅은 비슷한 수의 규칙을 냈으나 카드 소팅이 더 적었음. https://research.bond.edu.au/en/publications/eliciting-knowledge-from-experts-a-methodological-analysis/
- 정책포착(policy capturing)/판단분석 전통 (Slovic 1969 "Analyzing the expert judge", *J. Applied Psychology* 53; Hammond의 사회판단이론) — 전문가가 **말하는 가중치와 통계적으로 추정된 가중치가 체계적으로 다르며**, 전문가는 자신이 쓰는 단서 수를 과대 보고하는 경향. 2006년 *Organizational Research Methods* 연구는 비보상적(사전식) 전략을 가정할 때 정책포착 가중치가 직접추정치보다 우수함을 보고. https://experts.arizona.edu/en/publications/comparing-the-efficacy-of-policy-capturing-weights-and-direct-est/

**[추론] 이 공장에 대한 함의**: 반장의 규칙은 대부분 사전식(lexicographic)·비보상적일 가능성이 높으므로, "각 요소를 몇 % 보나요"보다 **"A와 B 중 무엇을 먼저 하나요, 왜"** 식 쌍대비교와 실제 사례 추적이 정확도가 높다.

### 2.2 하루 일정에 맞는 기법 4종

**(a) 결정적 사건 기법(Critical Decision Method, CDM)**
- Klein, Calderwood & MacGregor (1989) *IEEE SMC* 19(3), 462–472; Hoffman, Crandall & Shadbolt (1998) *Human Factors* 40(2), 254–276; Crandall, Klein & Hoffman (2006) *Working Minds* (MIT Press). 실제 비일상적 사건을 **다중 통과(multiple-pass) 회고**로 재구성하며 인지 프로브를 적용. 1998 논문은 신뢰도·타당도·효율·유용성을 방법론적으로 논의. https://www.gary-klein.com/cdm , https://eprints.soton.ac.uk/252284
- 가구공장 적용: "지난 2주에서 **가장 꼬였던 날** 하나"를 고르게 하고, (1) 사건 개요, (2) 시간선 재구성, (3) 각 결정점에서의 단서·대안·목표 심화, (4) "만약 …였다면" 가설 질문의 4패스로 진행. 소요 60–90분.

**(b) 응용 인지과업분석(ACTA)**
- Militello & Hutton (1998) *Ergonomics* 41(11), 1618–1641 — 실무자용 간소화 CTA. 과업도(task diagram) → 지식감사(knowledge audit) → 시뮬레이션 면담(simulation interview) → 인지요구표. 대학원생도 쉽게 쓸 수 있음이 확인됨. https://uwe-repository.worktribe.com/output/9887108/applied-cognitive-task-analysis-acta-a-practitioners-toolkit-for-understanding-cognitive-task-demands
- 적용: 지식감사 프로브("초보 반장이 흔히 틀리는 것은?", "한눈에 알아채는 징후는?", "편법·요령은?")가 금지 규칙과 암묵 단서를 잘 끌어냄. 시뮬레이션 면담은 아래 (c)로 대체.

**(c) 어제 계획으로 하는 동시적 구술(think-aloud) 재연**
- Ericsson & Simon 원칙에 따라, **어제(또는 기록 기간 중 하루)의 실제 재단리스트·화이트보드 사진**을 앞에 두고 "오늘 아침 상태라고 치고 순서를 다시 짜 보세요"를 **실시간 구술**로 진행. 설명("왜")은 묻지 않고 "다음에 뭘 보나요"만 묻는다. 끝난 뒤 실제 기록과 비교해 차이 나는 지점에서만 회고 질문.
- 이 방법은 Ericsson & Simon이 말한 "작업기억 내용의 구술"에 가까워 타당도가 가장 높고, 동시에 **첫 번째 재현율 측정 표본**(반장 자신이 자기 하루를 얼마나 재현하는지 = 일관성의 상한)을 제공한다 **[추론]**.

**(d) 주문 쌍대비교 + 카드 소팅**
- 기록에서 실제로 같은 날 같은 공정 대기열에 있었던 주문 쌍 15–25개를 골라(가능하면 속성이 하나만 다른 쌍 포함), "둘 중 어느 것을 먼저 재단하나요?"를 묻고, 응답을 쌍대 선호 데이터로 저장. 이후 3절의 로지스틱/순위회귀로 가중치를 추정하면 **말로 한 가중치와 행동 가중치를 같은 틀에서 비교**할 수 있다.
- 카드 소팅: 주문 속성 카드(설치일, 현장, 색상, 두께, 수량, 고객 유형, 시공팀, 사장 지시 여부 등)를 "순서를 정할 때 보는 것 / 안 보는 것 / 가끔 보는 것"으로 분류시키고, "보는 것"을 중요도 순으로 배열 → 사전식 순서 가설.

### 2.3 괴리를 줄이는 운영 원칙 **[추론, 문헌 원칙 적용]**
1. **사례 기반 질문만**: "보통 어떻게 하세요"를 금지하고 모든 질문을 특정 주문·특정 날짜에 붙인다(CDM 원칙).
2. **금지 규칙 전용 시간**: "절대 안 하는 것"을 따로 묻는다(ACTA 지식감사).
3. **두 명 이상**: 반장과 사장(또는 재단 담당)을 **따로** 인터뷰하고 불일치를 기록. Berglund & Karltun(2007)이 지적한 비공식 권한 구조가 여기서 드러난다.
4. **카드는 현장에서 바로 데이터 스키마로 변환**: 각 if–then 카드를 "트리거 / 조건 변수 / 비교값 / 행동 / 우선순위 / 예외"의 6칸으로 즉석 재작성하고 반장에게 읽어 확인시킨다(member check).
5. **사진 증거**: 화이트보드, 카톡 작업지시, 재단리스트 손글씨 메모를 촬영해 카드와 연결한다.

---

## 3. 기록에서 배치/투입 규칙을 식별하기: 규칙 적합과 재현율

### 3.1 관련 문헌 계보

- **데이터에서 디스패칭 규칙 학습**: Li & Olafsson (2005) "Discovering dispatching rules using data mining" (*J. Scheduling* 8, 515–527) — 과거 생산 데이터를 전처리해 학습 알고리즘(의사결정나무)으로 규칙 발견. Olafsson & Li (2010, *IJPE* 128) — 데이터 중 "모범 사례"에 해당하는 부분을 먼저 고른 뒤 나무를 귀납. https://unpaywall.org/10.1007%2FS10951-005-4781-0 , https://ideas.repec.org/a/eee/proeco/v128y2010i1p118-126.html
- Ingimundardottir & Runarsson (2011) "Supervised learning linear priority dispatch rules for job-shop scheduling" (LNCS 6683) — 각 결정 시점에서 "선택된 작업 vs 선택되지 않은 작업" 쌍을 만들어 **선형 우선순위 함수의 가중치를 순위회귀로 학습**. 후속 연구(2014, 2018)에서 가중 복합 규칙·모방학습으로 확장. https://iris.landsbokasafn.is/en/publications/supervised-learning-linear-priority-dispatch-rules-for-job-shop-s/
- Jun & Lee (2019 RANFORS, 2021 GRAFT, *IJPR*) — 일정 데이터를 결정 단위 학습 데이터로 변환하고 랜덤포레스트/의사결정나무로 IF–THEN 규칙 추출. https://gpbib.pmacs.upenn.edu/gp-html/Jun_2021_IJPR.html
- **시뮬레이션용 제어 행동 모방(가장 직접적 선행연구)**: Bergmann, Feldkamp & Straßburger (2015) "Approximation of dispatching rules for manufacturing simulation using data mining methods" (WSC 2015) 및 (2017) "Emulation of control strategies through machine learning in manufacturing simulations" (*J. Simulation* 11(1), 38–50) — **생산 데이터에서 작업 배정 행동을 학습해 시뮬레이션 모델에 자동으로 넣는** 것이 목표. 신경망·의사결정나무 등 지도학습을 비교하고 시뮬레이션 통합 권고를 제시. https://ideas.repec.org/a/taf/tjsmxx/v11y2017i1p38-50.html
- **프로세스 마이닝의 결정 마이닝**: Rozinat & van der Aalst (2006) "Decision Mining in ProM" (LNCS 4102) — 분기점마다 어떤 데이터 속성이 경로 선택을 설명하는지 의사결정나무로 학습. Mannhardt, de Leoni, Reijers & van der Aalst "Decision Mining Revisited" — 기존 방법은 상호배타적·결정론적 규칙을 가정하므로, **중첩 규칙(overlapping rules)**을 허용하는 방법 제안. 이 지적은 "반장 규칙은 결정론적이지 않고 기록되지 않은 요인이 있다"는 현실에 직접 맞닿아 있음. https://www.vdaalst.rwth-aachen.de/publications/p335.pdf , https://www.vdaalst.com/publications/p863.pdf
- **용어 주의**: 조합최적화의 "inverse scheduling"(Brucker & Shakhlevich 2009, 2011, *J. Scheduling*)은 주어진 순서가 최적이 되도록 처리시간·납기 같은 파라미터를 최소 조정하는 문제로, 본 과제의 "관찰된 순서를 재현하는 규칙 찾기"와는 다른 문제입니다. 다만 **"어떤 가중치면 관찰 순서가 규칙상 최적인가"**라는 발상은 3.3의 가중치 추정과 동일한 논리입니다. https://eprints.whiterose.ac.uk/81533/1/InvFlowShop-BruckerShakhlevich.pdf

주의: Li & Olafsson, Ingimundardottir, Jun & Lee 계열은 대개 **최적화 솔버가 만든 일정**에서 배우며, 원 생산 기록에서 배우는 것은 Bergmann et al.과 결정 마이닝 쪽입니다. 소표본(20–50 결정)에서 기계학습 모델을 바로 적합하면 과적합이 거의 확실하므로, 아래 절차는 **후보 규칙 열거 → 재현율 채점 → 소수 파라미터 추정**의 순서를 권합니다 **[추론]**.

### 3.2 결정 단위(decision instance) 재구성

재현율을 계산하려면 기록을 **"결정 순간"의 목록**으로 바꿔야 합니다.

1. 공정 s(재단, 엣지, 타공, 조립, 포장)별로 배치 착수 시각 t_k를 정렬한다.
2. 각 착수 시각에서 **대기열 Q(s, t_k)** = 그 시각에 해당 공정에 도착해 있었고 아직 착수되지 않은 작업 집합을 복원한다(선행 공정 완료 기록 또는 "재단리스트 발행 시각"으로 근사).
3. 결정 인스턴스 = (공정, 시각, 후보집합 Q, 실제 선택 c*).
4. 후보집합 크기 |Q| ≤ 1인 인스턴스는 **정보가 없으므로 제외**(어떤 규칙도 맞힌다). 이것이 소표본을 더 줄이는 주원인이므로, 2주 기록에서 유효 인스턴스가 20개 미만이면 공정별 집계가 아니라 전 공정 통합으로 평가한다.
5. 배치(batch) 결정은 두 층으로 분리한다: (i) **어느 묶음을 먼저**(묶음 간 순서), (ii) **묶음에 무엇을 넣었나**(묶음 구성). (ii)는 "창 안의 같은 색상×두께 주문 중 포함/제외" 이진 분류로 채점한다.

### 3.3 후보 규칙과 채점

**후보 규칙 집합(초기)**
- 단순 우선순위: FIFO(도착순), EDD(설치일순), SPT/LPT(판 수·m²), Slack(설치일 − 현재 − 잔여공정 표준시간), CR(critical ratio)
- 묶음 규칙: 같은 색상×두께 묶음 우선(셋업 회피), 같은 현장(시공지) 묶음 우선
- 트리거 규칙: 카트 가득 참(수량 ≥ N 또는 판 ≥ M)이면 이동; "고객/사장 연락" 플래그 있으면 최우선
- 사전식 복합: [긴급플래그] → [색상×두께 묶음 유지] → [EDD] → [FIFO] 와 같이 2–3단

**인스턴스 단위 재현율(top-1 hit rate)**
- 규칙 r이 Q에서 고르는 작업 r(Q)가 실제 c*와 같으면 1. 재현율 = 히트 수 / 유효 인스턴스 수.
- **동점 처리**: 규칙이 동점 집합 T ⊆ Q를 내면, (a) 엄격 채점: c* ∈ T 이면 1/|T| 부여(무작위 타이브레이크 기대값), (b) 관대 채점: c* ∈ T 이면 1. 둘 다 보고하고, 두 값의 차이가 크면 "규칙이 미결정 영역이 넓다"는 신호로 하위 규칙(타이브레이커)을 추가한다.
- **묶음 수준 평가**: 배치 묶음을 깨지 않는 규칙은 묶음 내부 순서를 평가하지 않으므로, 묶음 단위 인스턴스로 바꿔 채점한다.

**기준선(baseline)**: 무작위 선택의 기대 재현율은 Σ(1/|Q_k|)/K 이고, FIFO가 대개 가장 강한 자연 기준선입니다. 규칙 평가는 항상 **"기준선 대비 향상(lift)"**으로 보고해야 하며, 대기열이 작으면(|Q|=2–3) 무작위도 40–50%를 맞히므로 절대 재현율 숫자만으로는 의미가 없습니다.

**순서 수준 지표(보조)**: 각 날·공정의 실제 착수 순서와 규칙이 만든 순서 사이의 Kendall τ 또는 Spearman ρ. 하루 안의 순서가 10개 이하이면 τ의 표본 분산이 커서 보조 지표로만 쓴다.

**다기준 규칙 적합**
1. **사전식 탐색**: 속성 3–4개의 모든 순열(최대 24개)로 사전식 규칙을 만들어 재현율을 비교. 소표본에서 해석 가능성과 안정성이 가장 좋다.
2. **쌍대 선호 로지스틱/순위회귀**(Ingimundardottir & Runarsson 2011 방식): 각 인스턴스에서 (c*, q) ∀q ∈ Q\{c*} 쌍을 만들고 속성 차이 벡터에 로지스틱 회귀. 계수 부호와 크기가 가중치. 소표본에서는 L2 정규화와 **leave-one-decision-out** 교차검증 필수. 2.2(d)의 인터뷰 쌍대비교 응답과 같은 모델로 적합해 **"말한 가중치 vs 행동 가중치"**를 직접 비교.
3. **얕은 의사결정나무**(깊이 ≤ 2–3, 잎 최소 5건): Rozinat 방식. 규칙 발견용이지 최종 검증용이 아니다.

**불확실성 보고**
- 재현율은 이항 비율이므로 **Wilson 점수 구간(95%)**을 함께 보고한다. n=30, 24/30(0.80)이면 Wilson 95% 구간 ≈ [0.63, 0.90]. 의료영상·LLM 평가 분야의 비교연구에서 n≈50 이하에서는 Wilson이 부트스트랩보다 커버리지가 낫다고 보고됨. https://arxiv.org/pdf/2503.01747
- 두 규칙 비교는 같은 인스턴스에 대한 **짝지은(paired) 비교**이므로 McNemar 검정 또는 히트 차이의 순열검정을 쓴다.
- 인스턴스는 같은 날·같은 대기열에서 독립이 아니다(한 번의 선택이 다음 대기열을 바꿈). 날(day)을 블록으로 하는 **블록 부트스트랩**으로 구간을 보정하면 더 보수적이다 **[추론]**.
- 가중치 모델의 경우 계수 부호의 안정성(교차검증 폴드 간 부호 일치율)을 보고한다.

### 3.4 "규칙이 아닌 것" 분리하기
Mannhardt et al.이 지적한 **기록되지 않은 요인**을 다루려면, 미스(miss) 인스턴스를 반장과 함께 15–20분 **리뷰**하는 절차를 둔다. 미스는 보통 (a) 기록에 없는 정보(전화, 자재 미입고, 결근), (b) 규칙 누락, (c) 진짜 비일관성으로 분류된다. (a)는 해당 인스턴스에 플래그 변수를 추가해 재채점하고, 플래그가 **사후적으로 얼마나 자주 필요했는지**(예: 30건 중 6건)를 "기록되지 않은 교란율"로 별도 보고한다. 이것이 Hurst & McNamara(1967)가 말한 모델 부적절성과 계획자 비일관성의 분리입니다.

---

## 4. 시뮬레이션용 규칙 인코딩: 규칙을 데이터로

### 4.1 설계 원칙 **[추론, Bergmann et al. 2017 권고와 ECA 규칙 관례 적용]**
1. **규칙 = 데이터**: 코드가 아니라 YAML/JSON 테이블에 두고, 시뮬레이터는 (트리거, 조건, 행동) 해석기만 가진다. 시나리오 = 규칙 파일 교체.
2. **우선순위 함수와 트리거의 분리**: "무엇을 고르나"(priority function)와 "언제 결정하나"(trigger/event)를 다른 객체로.
3. **사전식 우선순위 + 타이브레이커 명시**: 3.3의 채점 결과와 1:1 대응되도록.
4. **모든 상수는 파라미터**: D−n의 n, 카트 용량, 창 길이, 야근 임계 백로그 등.
5. **출처·근거 메타데이터**: 각 규칙에 `source: interview_card_07`, `support: 21/27 (Wilson 0.58–0.89)` 를 기록해 트윈 문서와 검증 보고가 같은 파일을 가리키게 한다.
6. **기본 규칙 + 예외 규칙**: Mannhardt식 중첩을 허용하되, 시뮬레이터에서는 예외 규칙이 먼저 평가되고 매칭 시 기본 규칙을 덮어쓴다.

### 4.2 규칙 형태 예시 (YAML)

```yaml
# 1) 투입 시점: 설치일 역산
- id: REL-01
  type: release
  trigger: {event: daily_planning, time: "08:00"}
  condition:
    install_date_minus_today_days: {"<=": P.release_lead_days}   # 기본 5
    materials_available: true
  action: {release_to: cutting, priority_tag: normal}
  exceptions:
    - when: {site_distance_km: {">": 150}}
      override: {install_date_minus_today_days: {"<=": P.release_lead_days + 1}}
  params: {release_lead_days: 5}
  evidence: {card: C03, support: "18/22", wilson95: [0.62, 0.93]}

# 2) 재단 배치: 창 안의 색상×두께 묶음
- id: BAT-01
  type: batch_formation
  station: cutting
  trigger: {event: queue_changed}
  group_by: [panel_color, thickness_mm]
  window: {install_date_within_days: P.batch_window_days}   # 기본 3
  batch_limits: {max_sheets: P.max_sheets_per_batch}       # 재단기 1회 적재
  batch_priority: lexicographic
  priority_keys:
    - {key: has_urgent_flag, order: desc}
    - {key: min_install_date_in_batch, order: asc}
    - {key: batch_sheet_count, order: desc}                # 큰 묶음 먼저(셋업 상각)
  tie_break: fifo_arrival
  params: {batch_window_days: 3, max_sheets_per_batch: 25}

# 3) 카트 가득 참 운반 트리거
- id: TRN-01
  type: transport_trigger
  from: edgebanding
  to: boring
  trigger_any:
    - {cart_fill_ratio: {">=": P.cart_full_ratio}}         # 기본 0.9
    - {oldest_item_wait_min: {">=": P.max_wait_min}}       # 기본 90
    - {event: shift_end}
  action: {move_cart: true, reset_cart: true}
  params: {cart_full_ratio: 0.9, max_wait_min: 90}

# 4) 야근 결정
- id: OT-01
  type: overtime
  trigger: {event: daily_review, time: "15:30"}
  condition:
    backlog_hours_due_within_days: {days: 2, ">=": P.ot_backlog_hours}   # 기본 6
  action: {extend_shift_hours: P.ot_hours, stations: [cutting, edgebanding]}
  constraints: {max_consecutive_ot_days: 3}
  params: {ot_backlog_hours: 6, ot_hours: 2}

# 5) 외주 결정
- id: OUT-01
  type: outsourcing
  trigger: {event: weekly_review, weekday: Mon}
  condition:
    projected_cutting_load_next_week_hours: {">": P.cut_capacity_hours * P.out_threshold}  # 기본 1.2
  action:
    outsource: {operation: cutting, select: "largest_sheet_count_orders", up_to_hours: "excess"}
    outsourcing_lead_time_days: P.out_lead_days
  params: {out_threshold: 1.2, out_lead_days: 3}

# 6) 작업자 재배치(벤치 기아 상태)
- id: WRK-01
  type: worker_reassignment
  trigger: {event: station_starved, station: assembly, idle_min: {">=": 20}}
  condition:
    source_station_queue_hours: {station: edgebanding, ">=": 2}
  action:
    move_worker: {from: edgebanding, to: assembly, skill_required: assembly, count: 1}
    revert_when: {assembly_queue_hours: {">=": 1}}
  constraints: {never_move: [cutting_lead]}
```

### 4.3 검증과 시나리오 전환의 연결
- 3.3의 채점기는 **같은 규칙 파일**을 읽어 과거 결정 인스턴스에 적용한다(리플레이 모드). 시뮬레이터는 같은 파일을 실시간 모드에서 쓴다. 두 실행 경로가 같은 해석기를 쓰면 "검증한 규칙 ≠ 시뮬레이션 규칙" 문제가 사라진다.
- 시나리오 예: `batch_window_days: 3 → 5`, `release_lead_days: 5 → 4`, 예외 규칙 제거(사장 긴급지시 금지), 외주 임계 변경. 각 시나리오의 리드타임 분포 변화를 기록 기간의 기준 시뮬레이션과 비교한다.
- Bergmann et al.(2017)의 권고처럼, 학습된(또는 적합된) 규칙은 시뮬레이션 안에서 **데이터 기반 분류기 객체로도 교체 가능**하게 인터페이스를 맞춰 두면 나중에 표본이 커졌을 때 나무/회귀 모델을 꽂을 수 있다.

---

## 5. 한국 소규모 가구 제조 현장의 특수성

검색 범위에서 **한국 중소 가구공장의 생산계획 관행을 직접 다룬 학술 연구는 찾지 못했습니다.** 아래는 확인된 인접 자료와, 그로부터의 추론을 구분해 정리합니다.

**확인된 자료**
- 정성원 (2022) 아주대 석사논문 「가구산업의 설치물류 통합운영모형」 (지도: 임석철) — 가구산업은 **설치기사가 고객 현장에서 조립·설치하는 설치물류가 결합**된다는 점이 다른 산업과 다르며, 국내 가구업체 실데이터로 가정용/사무용 수요의 연중 분포가 상반됨을 확인. 설치 인력의 안정적 운용을 위해 작업량 평준화가 필요하다는 문제의식. https://dspace.ajou.ac.kr/handle/2018.oak/21276
- 딜사이트 (2021) — 가구제조업은 회생절차 신청이 꾸준한 대표 업종으로, 이케아·대기업 온라인몰 공세와 중소 제조사의 대응 어려움을 진단. https://dealsite.co.kr/articles/76417
- 숨고 등록 업체 프로필 — 거실 슬라이드장 제작 3–5주·시공 2시간, 싱크대 제작 약 7일·설치 1일 등 **"제작 기간 + 설치 1일"** 구조의 리드타임 관행 확인(사업자 자기 기술, 통계 아님). https://soomgo.com/profile/users/18094039 , https://soomgo.com/profile/users/17552946
- 오픈서베이 (2021) 직장인 1,000명 조사 — 53.3%가 업무용 메신저 대신 카카오톡 사용, **9인 이하 소규모 회사는 65.3%**. 제조 현장 작업지시에 특화된 통계는 없음. https://blog.opensurvey.co.kr/article/working-tool-2021-2/
- 중소기업중앙회 (2020) 스마트공장 구축 259개사 조사 — 제조 데이터 수집 방식 중 **업무일지·Excel 등 수기 작성 17.3%**(도입 기업 기준이므로 미도입 기업은 이보다 높을 것으로 추정). https://www.etoday.co.kr/news/view/1909069
- 경남테크노파크 (2022–2023 도입 439개사) — 납기 17.0% 개선, 50인 미만 소규모 기업에서 공정 개선 효과가 두드러짐(업종 불문 일반 성과). https://www.heraldk.com/article/2026061517590275819
- Berglund & Karltun (2007)의 스웨덴 가구공장 사례는 국내 자료는 아니지만 **목공 업종 계획자의 비공식 권한·조직 연결 역할**을 보여주는 가장 가까운 연구입니다.

**현장 특수성 가설 [추론]** — 인터뷰에서 반드시 확인할 항목:
1. **사장–반장 이중 권한**: 수주·시공일 협의·긴급 지시는 사장(또는 영업)이, 공정 순서·배치는 반장이. 사장의 카톡 지시는 반장 규칙 계층에서 **예외 규칙(최상위)**로 작동할 가능성이 높다. 트윈에는 "사장 개입 빈도(주당 n회)"를 **외생 사건 스트림**으로 모델링하고, 개입이 없다는 시나리오를 별도로 둔다.
2. **시공일이 유일한 납기**: 시공일은 인테리어 업체·시공팀·현장(공사 진행) 사정으로 변경되며, 변경은 카톡으로 들어온다. 기록에 "최초 시공일"과 "최종 시공일"을 모두 남겨야 투입 규칙(D−n)이 어느 시공일 기준인지 판별 가능하다.
3. **재단리스트 종이가 사실상의 작업지시서**: 재단리스트 발행 시각·발행 순서가 "투입" 결정의 가장 좋은 대리변수다. 종이에 손글씨로 쓴 순번·동그라미·별표를 촬영해 긴급 플래그로 코딩한다.
4. **색상×두께 묶음과 자재 입고의 결합**: 특수색 판넬은 발주 후 입고 대기가 있어 "자재 도착"이 사실상 release trigger일 수 있다.
5. **화이트보드 = 주간 부하의 유일한 가시화**: 보드를 매일 같은 시각에 촬영하면 2주 기록을 "일별 대기열 스냅샷"으로 복원하는 데 결정적이다.
6. **다기능 소수 인력**: 10–20인 규모에서는 작업자 1명의 결근이 공정 순서를 바꾼다. 출근부를 기록에 포함해야 한다.
7. **스마트공장 사업 맥락**: 중기부 스마트공장 보급사업으로 MES가 들어간 경우에도 실제 순서 결정은 보드/카톡에 남는 경우가 많다(중기중앙회 2020 조사에서 수기 비중 참조). MES 타임스탬프는 "착수"가 아니라 "입력 시각"일 수 있어 지연 편향을 점검해야 한다.

---

## 6. 실행 프로토콜

### 6.1 사전 준비 (인터뷰 D-3까지)
기록 2주분을 먼저 받아 3.2의 결정 인스턴스 표를 **초안으로 작성**해 두어야 인터뷰에서 실제 사례를 지목할 수 있습니다.

**필요한 기록(최소 세트)**
| 기록 | 용도 | 대체 수단 |
|---|---|---|
| 주문 마스터: 주문ID, 수주일, 최초/최종 시공일, 현장(주소·거리), 고객 유형, 색상, 두께, 판 수/부품 수 | 모든 속성 변수 | 견적서·발주서 |
| 재단리스트 발행 시각·순번(종이 사본 스캔) | 투입(release) 결정 | 화이트보드 사진 |
| 공정별 배치 착수·완료 시각(재단, 엣지, 타공, 조립, 포장) | 결정 인스턴스, 대기열 복원 | 작업일지, MES |
| 셋업 로그(색상·두께·띠 교체 시각) | 묶음 경계 확인 | 재단기 프로그램 로그 |
| 카트 이동 기록(가능하면 카트 번호·시각·수량) | 운반 트리거 | 사진 |
| 출근부·야근·외주 발주 기록 | 재배치·야근·외주 규칙 | 급여 자료 |
| 카톡 작업지시·시공일 변경 메시지(시각 포함, 개인정보 제외) | 긴급 플래그, 외생 교란 | 반장 메모 |
| 화이트보드 매일 2회(08:00, 15:30) 사진 | 대기열 스냅샷 | — |

### 6.2 하루 인터뷰 순서 (반장 기준 약 6시간, 사장 1시간 별도)
1. **09:00–09:30 과업도(ACTA)**: 하루 흐름을 5–7단계로 그리게 하고 "어려운 단계"에 표시. 라포 형성 겸 어휘 수집.
2. **09:30–10:45 어제 계획 재연(think-aloud)**: 기록 기간 중 하루의 아침 상태(보드 사진, 재단리스트)를 제시, 실시간 구술로 순서 재구성. 녹음. 설명 질문 금지.
3. **10:45–11:00 휴식**
4. **11:00–12:30 CDM**: 기록 기간 중 가장 꼬였던 날 1건(없으면 최근 1건). 4패스.
5. **13:30–14:30 쌍대비교 20쌍**: 기록에서 추출한 실제 공존 주문 쌍. 응답과 "결정적 이유" 한 줄 기록.
6. **14:30–15:00 카드 소팅 + 지식감사**: 속성 카드 분류·정렬, "절대 안 하는 것", "초보가 틀리는 것", "요령".
7. **15:00–15:45 규칙 카드 6칸 변환 + member check**: 수집된 if–then을 즉석에서 4.1 스키마로 옮기고 읽어 확인. 상수(n일, 카트 수량, 창 길이)를 숫자로 받는다.
8. **15:45–16:30 사장 인터뷰(별도)**: 긴급 지시 기준, 시공일 변경 처리, 외주·야근 결정권. 반장 카드와의 불일치 표시.
9. **16:30–17:00 (가능하면) 미스 리뷰 1차**: 초안 인스턴스 표에서 명백히 EDD/FIFO를 벗어난 5–10건을 보여주고 이유 수집.

### 6.3 지표와 수용 기준 **[추론; 문헌에 합의된 임계치는 없음]**
문헌은 재현율의 절대 임계치를 제시하지 않습니다. Hurst & McNamara(1967)와 Bergmann et al.(2017)도 "모델 vs 실제" 비교를 보고하되 합격선을 규정하지 않았습니다. 따라서 아래 기준은 **트윈의 목적(리드타임 예측)에 맞춘 제안**입니다.

**1차 지표(결정 수준)**: 엄격 채점 top-1 재현율, Wilson 95% 하한, FIFO 대비 lift.
- **"규칙 계층 복제" 주장 가능**: 재현율 ≥ 0.75 **이고** Wilson 하한 ≥ 0.60 **이고** 최선 단순 기준선(FIFO 또는 EDD) 대비 lift ≥ +0.15. n=30이면 대략 23/30 이상이 필요.
- **"조건부 복제"**: 재현율 0.60–0.75, 또는 lift < 0.15. 트윈에 쓰되 민감도 분석에서 규칙 변형(타이브레이커 교체, 창 길이 ±)을 반드시 포함하고 보고서에 한계를 명시.
- **"미복제"**: 재현율 < 0.60 또는 기준선과 통계적으로 구분 안 됨(McNemar p > 0.1).

**2차 지표(결과 수준, 필수 병행)**: 규칙 파일로 2주를 리플레이 시뮬레이션해 **주문별 리드타임(투입→포장 완료)과 납기 여유(포장 완료–시공일)** 분포를 실제와 비교. 평균·P90 오차 ±10% 이내, 또는 KS 검정에서 기각되지 않음. 결정 수준 재현율이 낮아도 결과 분포가 맞으면 "리드타임 예측에는 충분"이라고 **한정적으로** 주장할 수 있고, 반대로 결정 재현율이 높아도 결과 분포가 틀리면 공정시간 모델 쪽을 의심한다.

**보조 지표**: 반장 자기재현율(think-aloud 결과 vs 실제 기록). 이것이 0.8이면 어떤 외부 규칙도 그 이상은 기대하기 어렵다는 상한으로 보고한다. "기록되지 않은 교란율"(3.4)도 함께 보고.

**표본 가이드**: 유효 인스턴스 20개 미만이면 수용 판정을 보류하고 "탐색적"으로만 보고. 40–50개면 공정별 분리 보고가 가능. 2주로 부족하면 **기록 기간을 2주 더 연장하는 것이 인터뷰를 늘리는 것보다 낫다**(Ericsson & Simon / 정책포착 문헌의 함의).

### 6.4 임계치를 넘는 규칙이 없을 때
Hurst & McNamara의 이중 해석에 따라 순서대로 점검합니다.
1. **후보집합 복원 오류 점검**: 대기열 Q가 잘못되면 모든 규칙이 틀린다. 선행 공정 완료 시각 대신 재단리스트 발행 시각을 쓰고 있는지, 자재 미입고 건이 Q에 섞였는지 확인.
2. **누락 변수 추가**: 미스 리뷰에서 나온 플래그(사장 지시, 자재 도착, 결근, 시공일 변경)를 변수로 추가하고 재채점. 플래그가 사후적으로 필요한 비율이 30%를 넘으면 규칙 문제가 아니라 **외생 교란 스트림**을 트윈에 명시적으로 넣어야 한다.
3. **사전식 순서 재탐색 + 타이브레이커 추가**: 관대 채점과 엄격 채점의 차이가 크면 타이브레이커 부재가 원인.
4. **혼합 정책(mixture)으로 보고**: "평상시(백로그 < X) EDD-묶음, 과부하 시 셋업 최소화"처럼 **상태 의존 규칙**을 두 개로 나누어 적합. Fransoo & Wiers(2006)의 결과(복잡도 ↑ → 행동 다양성 ↑)는 이것이 정상적 현상임을 뒷받침한다.
5. **확률적 규칙으로 인코딩**: 결정론적 규칙 대신 쌍대 로지스틱 모델의 확률로 선택하는 "소프트 규칙"을 트윈에 넣고, 시뮬레이션 반복으로 리드타임 분포를 낸다. 결정 재현율 대신 2차 지표(결과 분포)로 검증한다. Mannhardt et al.의 중첩 규칙 관점과 일치.
6. **그래도 안 되면**: 반장 규칙 계층을 "미확정"으로 두고, 민감도 분석에서 **규칙을 시나리오 축으로** 돌려(FIFO/EDD/묶음/혼합) 리드타임 예측의 구간을 보고한다. 이는 실패가 아니라 "규칙이 리드타임을 지배한다"는 당초 민감도 결과를 의뢰인에게 정량적으로 보여주는 결과물이 된다.

---

## 7. 요약: 확립된 것과 추론한 것

**확립된 연구 결과**
- 현장 계획자는 최적화가 아니라 제약 수집·교란 흡수·재일정을 주 업무로 하며, 공식 규칙은 평상시에만 성립한다(McKay et al. 1988/1995; Crawford 1999; Jackson 2004; MacCarthy & Wilson 2001).
- 계획자의 비공식 권한과 조직 연결 역할이 결과를 좌우한다(Berglund & Karltun 2007, 목공 4사).
- 회고적 설명은 부정확하고, 동시적 구술·사례기반 질문·정책포착(행동 데이터에서 가중치 추정)이 더 타당하다(Nisbett & Wilson 1977; Ericsson & Simon 1993; Slovic 1969; Hoffman et al. 1995).
- 생산 기록에서 결정 규칙을 지도학습으로 복원해 시뮬레이션에 넣는 접근은 실행 가능함이 보고되었다(Bergmann et al. 2015/2017; Rozinat & van der Aalst 2006; Li & Olafsson 2005).
- 소표본 비율의 구간은 Wilson 점수 구간이 부트스트랩보다 신뢰할 만하다.

**본 보고서의 추론(검증 필요)**
- 가구공장 규칙의 사전식 구조(긴급 > 자재 > 색상×두께 묶음 > 시공일 > FIFO) 가설.
- 재현율 수용 기준(0.75 / Wilson 하한 0.60 / lift 0.15)과 결과 수준 병행 검증.
- 사장 카톡 지시를 외생 사건 스트림 + 최상위 예외 규칙으로 모델링.
- 한국 중소 가구공장 관행(재단리스트 종이, 화이트보드, 카톡)에 관한 서술은 인접 통계와 업계 자료에서의 유추이며, 해당 현장에서 직접 확인한 연구는 찾지 못했다.

---

### 참고문헌 (확인 URL 포함)
- McKay, Safayeni & Buzacott (1988). Job-Shop Scheduling Theory: What Is Relevant? *Interfaces* 18(4). https://pubsonline.informs.org/doi/fpi/10.1287/inte.18.4.84
- McKay, Safayeni & Buzacott (1995). 'Common sense' realities of planning and scheduling in printed circuit board production. *IJPR* 33(6). https://www.iaorifors.com/paper/14986
- McKay & Wiers (2003). Planners, schedulers and dispatchers. *Cognition, Technology & Work*. https://research.tue.nl/en/publications/planners-schedulers-and-dispatchers-a-description-of-cognitive-ta/
- McKay & Wiers (2004). *Practical Production Control*. J. Ross. https://jrosspub.com/?p=1527
- Crawford, MacCarthy, Wilson et al. (1999). Investigating the Work of Industrial Schedulers through Field Study. *CTW* 1. https://unpaywall.org/10.1007%2FS101110050033
- MacCarthy & Wilson (eds.) (2001). *Human Performance in Planning and Scheduling*. https://www.routledge.com/products/9780748409297
- Jackson, Wilson & MacCarthy (2004). A new model of scheduling in manufacturing. *Human Factors* 46(3). https://oa.mg/work/10.1518/hfes.46.3.533.1628
- Berglund & Karltun (2007). *IJPE* 110. https://ideas.repec.org/a/eee/proeco/v110y2007i1-2p160-174.html
- Fransoo & Wiers (2005/2006). Action variety of planners. https://research.tue.nl/en/publications/action-variety-of-planners-cognitive-load-and-requisite-variety-2/
- Gasser, Fischer & Wäfler (2010). Decision Making in Planning and Scheduling. https://ideas.repec.org/h/spr/sprchp/978-3-642-13382-4_2.html
- Larco Martinelli et al. (2020). The scheduler's balancing act. *IJPR* 58(13). https://ideas.repec.org/a/taf/tprsxx/v58y2020i13p3944-3955.html
- Hurst & McNamara (1967). Heuristic Scheduling in a Woolen Mill. *Management Science* 14(4). https://pubsonline.informs.org/doi/pdf/10.1287/mnsc.14.4.B182
- Dutton (1962) *IJPR* 1(4); Dutton & Starbuck (1971) — 원문 미확인.
- Wiers (1996) *PPC* 7(4); Stoop & Wiers (1996) — https://research.tue.nl/en/publications/what-is-really-happening-at-the-shop-floor-and-why-do-scheduling-/
- Fox & Smith (1984). ISIS. — 원문 미확인.
- Klein, Calderwood & MacGregor (1989). *IEEE SMC* 19(3). https://www.gary-klein.com/cdm
- Hoffman, Crandall & Shadbolt (1998). *Human Factors* 40(2). https://eprints.soton.ac.uk/252284
- Crandall, Klein & Hoffman (2006). *Working Minds*. MIT Press.
- Militello & Hutton (1998). ACTA. *Ergonomics* 41(11). https://uwe-repository.worktribe.com/output/9887108/
- Hoffman (1987). *AI Magazine* 8; Cooke (1994). *IJHCS* 41. https://www.cambridge.org/core/books/abs/cambridge-handbook-of-expertise-and-expert-performance/eliciting-and-representing-the-knowledge-of-experts/942AE193BFC25B49F7507F309061C997
- Hoffman, Shadbolt, Burton & Klein (1995). *OBHDP* 62. https://research.bond.edu.au/en/publications/eliciting-knowledge-from-experts-a-methodological-analysis/
- Nisbett & Wilson (1977). *Psychological Review* 84; Ericsson & Simon (1993). *Protocol Analysis*. https://mitpressbookstore.mit.edu/book/9780262550239
- Slovic (1969). Analyzing the Expert Judge. *J. Applied Psychology* 53; 정책포착 비교: https://experts.arizona.edu/en/publications/comparing-the-efficacy-of-policy-capturing-weights-and-direct-est/
- Li & Olafsson (2005). *J. Scheduling* 8. https://unpaywall.org/10.1007%2FS10951-005-4781-0 ; Olafsson & Li (2010). *IJPE* 128. https://ideas.repec.org/a/eee/proeco/v128y2010i1p118-126.html
- Ingimundardottir & Runarsson (2011). LNCS 6683. https://iris.landsbokasafn.is/en/publications/supervised-learning-linear-priority-dispatch-rules-for-job-shop-s/
- Jun & Lee (2021). GRAFT. *IJPR*. https://gpbib.pmacs.upenn.edu/gp-html/Jun_2021_IJPR.html
- Bergmann, Feldkamp & Straßburger (2015, WSC; 2017, *J. Simulation* 11(1)). https://ideas.repec.org/a/taf/tjsmxx/v11y2017i1p38-50.html
- Rozinat & van der Aalst (2006). Decision Mining in ProM. https://www.vdaalst.rwth-aachen.de/publications/p335.pdf ; Mannhardt et al. Decision Mining Revisited. https://www.vdaalst.com/publications/p863.pdf
- Brucker & Shakhlevich (2009, 2011). Inverse scheduling. https://eprints.whiterose.ac.uk/81533/1/InvFlowShop-BruckerShakhlevich.pdf
- Thürer, Stevenson et al. WLC 및 due-date/release 통합 연구. https://research.rug.nl/en/publications/on-the-integration-of-due-date-setting-and-order-release-control/
- Wilson 구간 소표본 커버리지: https://arxiv.org/pdf/2503.01747
- 정성원 (2022). 가구산업의 설치물류 통합운영모형. 아주대. https://dspace.ajou.ac.kr/handle/2018.oak/21276
- 오픈서베이 (2021). 업무용 카카오톡 사용 실태. https://blog.opensurvey.co.kr/article/working-tool-2021-2/
- 이투데이 (2020). 중기중앙회 스마트공장 조사. https://www.etoday.co.kr/news/view/1909069
- 헤럴드경제 (2026). 경남 스마트공장 효과. https://www.heraldk.com/article/2026061517590275819
- 딜사이트 (2021). 가구제조업 회생. https://dealsite.co.kr/articles/76417
