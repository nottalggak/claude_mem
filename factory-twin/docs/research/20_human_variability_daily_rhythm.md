# 수작업 공정의 인적 변동 요인이 시간당·일일 산출 재현에 미치는 영향과 저비용 측정 방안
## — 10–20인 규모 주문제작 패널가구 공장 디지털 트윈(v0.5/v1)을 위한 작업측정·인간성능 관점 보고서

> **표기 규칙**: [확립] = 동료심사 문헌·공식 통계로 뒷받침되는 사실, [추론] = 문헌을 본 과제 상황에 적용한 필자의 추정. 외부 페이지 본문 직접 열람이 차단된 환경에서 작성했으므로, 수치는 초록·검색 발췌 기준이며 원문 대조가 필요한 곳은 따로 표시했다.

---

## 0. 요약 (Executive Summary)

현재 트윈은 수작업을 lognormal/gamma(CV 0.2–0.35), 근무시간 내 균일, 작업자 동질, 피로·학습·결근 없음으로 두고 있다. 검증 허용오차(일일 산출 ±10%, 리드타임 ±15%, 가동률 ±5%p)에 비추어 각 요인의 크기를 정리하면:

| 요인 | 일일 산출에 대한 영향 크기(추정) | CV로 흡수 가능? | 권고 |
|---|---|---|---|
| 휴게·청소·시업 지연 등 **고정 시간 블록** | 명목 근무시간의 10–20% (평균을 이동) | **불가** (평균 편향) | **v0.5 필수** — 스케줄 블록으로 |
| 시간대별 **작업 속도 프로파일**(워밍업·점심 후·막판) | 시간당 ±10–25%, 일일 합계엔 ±0–5% | 일일 지표만 보면 부분적으로 가능 | v0.5: 블록만 / **v1: 시간가변 승수** (시간당 재현 목표 시) |
| **작업자 간 이질성** | 작업자 간 SD ≈ 평균의 15–20%; 병목에 누가 배치되느냐에 따라 일일 ±5–15% | **불가** (일 단위로 평균화되지 않는 지속 편차) | v0.5: 스테이션별 "실측 유효 속도"로 흡수 / **v1: 2–3 숙련등급** |
| **피로/회복**(PF&D 10–15%) | 실측 사이클에 이미 포함 → 이중계상 위험 | 실측 기반이면 이미 흡수됨 | v0.5/v1 모두 **별도 모델 불필요**, 단 연장근무(>9h/일) 시 승수 |
| **학습**(신제품·신입) | 신입 1인(E-9 3개월 미만 ≈ 내국인의 60–67%)이 15인 중 1명이면 팀 산출 −2~−4%; 신규 제품군 첫 로트는 +20–40% 공수 | 반복 제품군은 정상상태로 흡수 | v0.5: 제외 / v1: "first-of-family" 패널티 옵션 |
| **결근·지각** | 결근 1건이 병목 작업자면 그 날 −10~−30% | **불가** (특정 날짜의 큰 편차) | **v0.5: 실제 출근표를 입력(trace-driven)** / v1: 확률 모델 |
| **중단(전화·고객·자재탐색·지게차 대기)** | 작업자 시간의 20–35%가 비부가가치 → 유효 가용률을 결정 | **불가** (평균을 바꿈) | **v0.5: 스테이션별 유효 가용률 계수** / v1: idle-gap 분포 명시 |

핵심 결론 두 가지:
1. **일일 산출 ±10%를 맞추는 데 치명적인 것은 "분산"이 아니라 "평균 편향"이다.** 고정 블록, 비부가가치 시간, 결근은 평균을 움직이므로 CV로 흡수할 수 없다. 반대로 사이클 단위 CV(0.2–0.35)는 하루 수십~수백 사이클로 평균화되어 일일 산출 변동에는 거의 기여하지 않는다(CV_daily ≈ CV_cycle/√N). [추론, 통계적 사실에 기반]
2. **2주 로그로 가장 싸게 얻을 수 있는 것은 "기계별 시간대별 가동비율 프로파일"과 "idle-gap 분포"이며, 이 둘만으로 v0.5의 평균 편향 문제 대부분을 해결할 수 있다.**

---

## 1. 근무시간 내 생산성 프로파일 (시업·점심 전·점심 후·종업)

### 1.1 증거
- [확립] **시간대(shift hour)가 생산성의 가장 강한 예측변수**: Sun, Liu & Ouyang(2023, *M&SOM*, "Time-Varying Physician Productivity and Implications for ED Modeling and Staffing")은 캐나다 응급실 데이터로 "교대 시작 후 경과시간"이 의사 생산성의 가장 유의한 예측변수임을 보이고, **시간대 의존 서비스율을 가진 다중서버 큐 모델은 실측 대기시간을 재현하지만 일정 서비스율 모델은 유의하게 벗어난다**고 보고했다. 제조 현장은 아니지만 "일정 서비스율 vs 시간가변 서비스율"의 모델링 결론은 그대로 전용 가능하다. https://pubsonline.informs.org/doi/10.1287/msom.2023.0081
- [확립] **첫 1시간은 나머지와 유의하게 다르고, 피크는 2–7시간째, 점심 후 약간 상승**: Durakovic(2025, Springer RTASCE 프로시딩, 금속 코팅 공정 3교대 사례)은 실공정 계측으로 (a) 각 교대에서 첫 시간과 나머지 시간의 생산성 차이가 유의, (b) 피크는 2–7시간째, (c) **세 교대 모두 점심 직후 생산성이 소폭 상승**, (d) 근무가 길어질수록 생산성 하락·오류율 상승을 보고했다. 즉 산업 현장에선 "점심 후 dip"보다 **휴식 후 회복(rebound)**이 관측될 수 있다. https://link.springer.com/chapter/10.1007/978-3-031-82881-2_20 (초록 기반; 퍼센트 크기는 원문 확인 필요)
- [확립] **점심 후 dip은 내인성(circadian)**: Monk(2005, *Clin Sports Med*, "The post-lunch dip in performance")는 오후 중반의 수행 저하가 식사와 무관하게 나타나는 생체리듬 현상이며, 아침형 인간에게 더 뚜렷하다고 정리했다. 다만 이는 주로 인지·각성 과제 기반이며, 반복 수작업 산출에 그대로 투영되지는 않는다. https://pubmed.ncbi.nlm.nih.gov/15892914/
- [확립] **근무시간–산출의 비선형성**: Pencavel(2015, *Economic Journal*, "The Productivity of Working Hours")은 1차대전 영국 군수공장 데이터로 주당 약 49시간 이후 한계생산성이 급감함을 보였다. https://docs.iza.org/dp8129.pdf ; Collewet & Sauermann(2017, *Labour Economics*)은 콜센터 일별 데이터로 근무시간이 길수록 통화처리시간이 길어짐(피로)을 보였다. https://swopec.hhs.se/sofiwp/abs/sofiwp2017_003.htm ; Brachet, David & Drechsler(2012, *AEJ: Applied*)는 구급대원 74만 건 데이터로 장시간 교대 말미 수행 저하를 보였다. https://www.nber.org/papers/w16418.pdf
- [확립] **기계 주도 공정에서는 시간대 효과가 사라질 수 있음**: 뉴질랜드 목재 가공 야드(2교대, 214교대 분석)에서 시간대는 기계 생산성·가치회수에 유의한 영향이 없었고, 저자들은 조명과 스캐너 자동화로 인적 입력 의존이 낮았기 때문으로 해석했다. https://fwpa.com.au/news/time-of-day-study-on-machine-productivity/ → **에지밴더·보링기 같은 기계페이스 공정에는 프로파일을 적용하지 말 것**의 근거.
- [확립] 역사적 문헌: Vernon(1921, *Industrial Fatigue and Efficiency*)은 "시간별·일별 산출", "작업 스펠과 휴식"에 별도 장을 두어 오전 스펠의 워밍업 상승, 스펠 말미의 하락과 성과급 하의 "end spurt"를 기술했다(원문 미열람; 목차와 2차 인용 기반). https://www.routledge.com/Industrial-Fatigue-and-Efficiency/Vernon/p/book/9781032270364
- [확립] Folkard & Tucker(2003, *Occup Med*)는 교대·근무지속시간·휴식간격이 안전·생산성에 미치는 영향을 종합하며 **요인 간 상호작용(긴 교대라도 휴식이 잦으면 더 안전할 수 있음)**을 강조했다. https://pubmed.ncbi.nlm.nih.gov/12637593/
- [확립] Baines et al.(2004, *Simulation Modelling Practice & Theory*, "Humans: the missing link in manufacturing simulation?")은 Ford와의 작업에서 노화·생체리듬 모델을 DES에 넣어 인적 변동이 시뮬레이션–현실 괴리의 상당 부분을 설명한다고 주장했다. https://publications.aston.ac.uk/id/eprint/38667/1/Humans_the_missing_link_in_manufacturing_simulation.pdf

### 1.2 크기 추정 [추론]
문헌을 종합하면 **인간 페이스 작업**의 시간당 유효 속도 승수 m(h)는 대략: 시업 첫 30–60분 0.80–0.90(공구·자재 세팅, 조회), 2–4시간째 1.00–1.05(피크), 점심 직전 30분 0.90–0.95, 점심 직후 30분 0.90–0.95(산업 데이터로는 rebound도 가능), 종업 전 30–60분 0.70–0.85(청소·정리·마감). **일일 합계로는 ±3–5% 수준**이지만, 시간당 산출로 보면 ±15–25%의 편차를 만들며, "시간당 산출 히스토그램"을 재현하려면 반드시 필요하다. 한국 소규모 공장은 통상 08:00/08:30–17:00/17:30, 점심 12:00–13:00, 10시·15시 전후 10–15분 참(휴게)이 관행이며(구인공고 기반; 근로기준법상 4시간당 30분 휴게 의무), 하루 명목 9시간 중 **휴게·청소·시업지연을 합치면 1.2–1.8시간(13–20%)**이 비가동으로 빠진다.

### 1.3 2주 로그에서 프로파일 추정하는 법
1. 전류 1 Hz 신호를 기계별로 off/idle/run 3상태로 분할(임계값 + 2–5초 디바운스; 비침습 전류클램프 기반 상태판별은 EP4030254 특허 등에서 통계적 자가학습 방식으로 기술됨). https://data.epo.org/publication-server/rest/v1.2/patents/EP4030254NWA1/document.html
2. **15분 빈(bin)** 단위 run-fraction을 계산 → 10 근무일 × 36빈 = 빈당 10개 표본. 요일 효과를 보려면 부족하지만 "평일 평균 프로파일"은 충분하다(빈당 run-fraction의 SE ≈ 0.1–0.15).
3. 카운터 게이트의 **시간당 통과 수** 히스토그램을 같은 빈으로 집계하고, 전류 run-fraction과 교차검증(두 신호가 같은 dip을 보이면 '작업자 부재', 전류만 run인데 카운터 0이면 '세팅/시운전').
4. 프로파일 분리: 먼저 **하드 블록**(run-fraction이 거의 0인 연속 구간: 점심, 참, 청소, 시업)을 식별해 스케줄로 빼고, 남은 가동 구간에서의 run-fraction 또는 카운트율을 피크 빈 대비 정규화 → **소프트 승수 m(h)**.
5. 수작업 스테이션(조립·샌딩)은 전류·카운터가 없으므로 카메라 존 점유율(occupancy, 분당 '사람 수'만 집계)로 동일 프로파일 산출.

### 1.4 시뮬레이션 표현: 승수 vs 블록
- **하드 블록(스케줄 휴게·청소·시업)**: 자원 비가용 캘린더로 넣어야 한다. 승수로 흉내 내면 큐 거동(블록 직전 WIP 적체, 블록 후 버스트)이 왜곡되어 리드타임 재현이 나빠진다. [추론]
- **소프트 승수 m(h)**: 서비스 시간 = 기본 분포 샘플 / m(h). 블록 제거 후 남는 잔여 변동만 담아야 이중계상을 피한다. 기계페이스 공정(에지밴더 피드, CNC 보링 사이클)에는 적용하지 않고 **로딩/언로딩 수작업 성분에만** 적용한다. [추론, 1.1의 NZ 결과와 Durakovic 결과에 근거]
- 검증 지표: 시간당 산출 히스토그램의 형태(KS 통계 또는 빈별 ±1 SE 포함률)로 v1에서 판단.

---

## 2. 작업자 간 이질성

### 2.1 증거
- [확립] **저복잡도 직무의 작업자 간 산출 SD ≈ 평균의 19%**: Hunter, Schmidt & Judiesch(1990, *J Applied Psychology* 75:28–42)는 측정오차·범위제한을 보정한 메타분석으로 SDp가 복잡도별로 약 19% / 32% / 48%임을 보고했다. 2차 요약에 따르면 저복잡도 직무의 상위 10%는 평균보다 25%, 하위 10%보다 75% 더 산출한다. https://www.gwern.net/doc/iq/ses/1990-hunter.pdf , https://80000hours.org/2012/09/how-good-are-the-best/
- [확립] **최속:최저속 ≈ 1:2.0–2.5**: 1981년 Human Factors Society 연례회의 논문은 문헌상 1:2.0을 보수적 추정치, 산업별로 1:2.0–2.5라 정리하고, 평균 작업자 기준으로 페이스를 설정한 라인은 인력 절반이 따라오지 못한다고 지적했다. https://sage.cnpereading.com/doi/10.1177/1071181381025001140 ; 작업연구 교재 강의노트도 "같은 방법으로 같은 과업을 하는 대집단에서 최속 작업자는 최저속의 약 2배"를 통례로 든다. https://staff.emu.edu.tr/orhankorhan/Documents/courses/ieng301-mane301/Lecture-Notes/spring2019-2020/CH21.pdf
- [확립] **목제 도어 공장의 사이클 CV**: Mississippi State Univ. 박사논문(2019, 지도교수 Jilei Zhang; 저자명은 레코드에서 미확인)은 목제 도어 라인 시간·동작연구에서 **수작업 스테이션의 공정시간 CV 12–23%, 반자동 2–20%**, 개선 후 수작업 9–14%를 보고했다. https://scholarsjunction.msstate.edu/td/3642 → 현재 가정 CV 0.2–0.35는 **수작업 상한과 비슷하거나 다소 높다**(단, 이 CV는 작업자 간 혼합 포함 여부가 불명확).
- [확립] **이질성을 평균으로 뭉개면 산출을 체계적으로 과소추정**: Shafer, Nembhard & Uzumeri(2001, *Management Science* 47:1639–1653)는 카라디오 조립라인의 실제 작업자 학습·망각 분포로 시뮬레이션하여 중심경향만 모델링하면 전체 생산성을 체계적으로 과소추정한다고 보였다. https://pubsonline.informs.org/doi/pdf/10.1287/mnsc.47.12.1639.10236 ; Nembhard & Osothsilp(2002, *IJIE* 29:297–306)는 과업 복잡도가 높을수록 개인 간 학습률·망각률·정상상태 생산성의 **분산**이 커진다고 보고했다. https://iro.uiowa.edu/esploro/outputs/journalArticle/Task-complexity-effects-on-between-individual-learningforgetting/9984187065302771
- [확립] **DES 관점의 실측**: Siebers의 Cranfield 박사논문(지도 Baines)은 자동차 수동조립라인 장기 수집 데이터로 작업자 성능 히스토그램을 제시하며 **퍼짐과 왜도가 연구자·실무자 예상보다 훨씬 컸다**고 결론지었다. https://dspace.lib.cranfield.ac.uk/handle/1826/10750
- [확립] Peltokorpi & Niemi(2018, *Procedia Manufacturing* 25:535–542)는 10개 작업자 쌍의 조립을 4회 반복 촬영하여 쌍 간 조립시간 차이가 유의하고, **반복할수록 상대 변동은 줄지만 순위는 유지**됨을 보였다(지속적 개인 효과). https://acris.aalto.fi/ws/portalfiles/portal/27476511/1_s2.0_S2351978918306498_main.pdf

### 2.2 '작업자 간' vs '작업자 내' 분해와 순환배치 효과 [추론]
- 통상 관측되는 혼합 CV(0.2–0.35)는 작업자 내 변동(CV_w ≈ 0.10–0.20)과 작업자 간 변동(CV_b ≈ 0.15–0.20)의 합성으로 볼 수 있다(CV²_mix ≈ CV²_w + CV²_b).
- **일일 산출에 대한 함의가 전혀 다르다.** 작업자 내 변동은 하루 N사이클에서 √N으로 평균화된다(N=50이면 CV 0.3 → 일일 0.04). 작업자 간 변동은 **그날 그 공정에 누가 서 있느냐**로 결정되어 평균화되지 않는다. 병목 스테이션(예: 조립·검사)에 평균보다 20% 느린 작업자가 배치된 날의 일일 산출은 ±10% 허용오차를 단독으로 넘길 수 있다.
- 순환배치(rotation)가 있으면 일 단위로 이 편차가 랜덤화되어 **일일 산출 분산**을 키우고, 고정배치면 분산은 작지만 **평균이 "그 사람"에 고정**된다. 따라서 모델은 "스테이션별 숙련 승수 × 배치 규칙"을 가져야 하고, 2주 동안 배치 규칙(고정/순환/응원)을 현장방문·카메라 존 점유로 반드시 기록해야 한다.
- 병렬 2인 작업(큰 패널 조립)에서는 느린 쪽이 페이스를 결정하므로 쌍의 유효속도 ≈ min(v1, v2) — Peltokorpi & Niemi의 쌍 간 차이가 큰 이유와 일치.

### 2.3 개인 식별 없이 탐지하기 (프라이버시 보존 집계)
- 법적 전제 [확립]: 사업장 감시설비는 근로자참여법 제20조 제1항 제14호의 노사협의 사항이며, 개인정보보호법상 목적·항목 고지·동의, 촬영범위 최소화, 개인정보처리방침 공개가 원칙이다(개인정보위·고용노동부 인사노무 가이드라인). CCTV 정보를 수집 목적 외로 쓰면 '이용'에 해당한다는 2025.6.26 대법원 판결도 있다. https://www.shinkim.com/kor/media/newsletter/2201 , https://byline.network/2023/01/0131_02/ → **"생산 분석 목적, 개인 식별·인사평가 불사용"을 서면 고지·협의**하고 원본 영상 보존기간을 짧게 둘 것.
- 기술 [확립]: 포즈 키포인트만 추출하거나(YOLOv8-Pose 기반 난독화, arXiv 2505.07306), 전신을 GAN으로 치환(DeepPrivacy2 산업 적용, arXiv 2405.19173)해도 작은 부서에선 체형·보행으로 재식별이 가능하다는 경고가 있다. https://arxiv.org/pdf/2505.07306 , https://arxiv.org/abs/2405.19173v1
- 실무 권고 [추론]: (1) 영상은 엣지에서 **존별 '사람 수/분', '움직임 에너지', '작업 사이클 시작/종료 이벤트'**만 산출하고 프레임은 폐기, (2) 개인 식별 대신 **"스테이션-시간대" 단위의 사이클 간격 분포**를 저장, (3) 이질성은 **일자 간·반일 간 사이클 간격 중앙값의 분산**(배치가 바뀌면 중앙값이 뛰는 패턴)으로 간접 추정 — 혼합분포(2–3 성분 lognormal) 적합으로 "빠른/보통/느린" 성분의 비율과 속도비를 얻되 개인에 귀속시키지 않는다, (4) 카운터 게이트에서는 연속 통과 간격의 **일중 run 세그먼트별 중앙값**을 비교해 배치 교체를 탐지한다.

---

## 3. 피로/회복과 ILO·MTM 여유율

### 3.1 여유율의 정체 [확립]
- ILO *Introduction to Work Study*(Kanawaty 편, 4판 1992)는 기본시간에 **relaxation allowance**(개인 필요 + 피로 회복)를 더해 표준시간을 만든다. 인도표준 IS 11500(1985)은 ILO 방식을 거의 그대로 가져와 점수제→퍼센트 변환표를 제시한다. https://services.bis.gov.in/tmp/SR11500.pdf , https://digitallibrary.un.org/record/115655
- Niebel & Freivalds(*Methods, Standards and Work Design*) 계열 교재는 **개인 여유 ≈ 5%, 기본 피로 ≈ 4%**를 상수로, 자세·중량·조명·소음 등 변동 피로와 불가피 지연을 추가하여 **총 PF&D 10–15%**가 통례다. 표준시간 = 정상시간 × (1 + PF&D). https://en.wikipedia.org/wiki/PFD_allowance , https://open-exam-prep.com/study-guides/pe-industrial/methods-engineering-work-measurement/time-study-work-measurement (교재 원문 대조 필요)
- 생리학적 근거: Rohmert(1973)의 지구력 곡선과 휴식여유 공식 RA = 18(T/MET)^1.4(%MVC/100−0.15)^0.5 등이 있으나, 후속 연구는 이 곡선이 %MVC≤45%에서 지구력을 과대추정한다고 지적한다. https://pubmed.ncbi.nlm.nih.gov/8817118 , https://ijoh.tums.ac.ir/index.php/ijoh/article/view/512/735

### 3.2 트윈에서 여유율과 유효 사이클의 관계 [추론 — 중요]
- 여유율은 **"정상 페이스로 쉬지 않고 했을 때의 시간"에 더해 하루 전체에 걸쳐 분산되는 휴식·개인시간의 예산**이다. 트윈이 **카운터/전류로 실측한 사이클 간격 분포**를 쓰면 그 분포에는 이미 미세휴식·개인시간·피로에 의한 감속이 들어 있다. 여기에 PF&D를 또 곱하면 **10–15% 이중계상**이 되고, 이는 가동률 ±5%p 허용오차를 단독으로 깨뜨린다.
- 반대로 **스톱워치 시간연구(1일 방문)로 얻은 정상시간**을 쓰는 스테이션에는 PF&D를 반드시 곱해야 한다. 즉 **스테이션별로 "출처 플래그"(실측 분포 vs 시간연구 정상시간)를 두고 여유율 적용 여부를 결정**하는 것이 올바르다.
- 여유율을 "사이클 승수"로 넣을지 "확률적 미세중단"으로 넣을지: 시간당 산출만 재현하려면 승수로 충분하다. 리드타임·대기열 재현에는 미세중단(개인 필요 5% ≈ 1시간에 3분, 지수분포 간격)으로 넣는 편이 큐 거동을 더 잘 재현하지만 v1 이후 과제다.

### 3.3 작업자 페이스 vs 기계 페이스 [확립 + 추론]
- Burke & Salvendy(1981, 85개 연구 메타분석)와 Salvendy(1982, NIOSH 리뷰)는 자기페이스 조건에서 스트레스는 다르지만 **수행은 자기페이스가 더 높았고**, 인지·지각부하가 높은 과업은 자기페이스로, 작업 세션은 휴식으로 끊어 각성 수준을 유지하라고 권고했다. https://stacks.cdc.gov/view/cdc/236960 , https://www.iloencyclopaedia.org/component/k2/item/19-work-pacing
- NZ 목재야드 연구(1.1)는 기계·자동화 비중이 높은 공정에서 시간대 효과가 소멸함을 보였다.
- 적용 [추론]:
  - **에지밴더**: 통과시간 = 패널 길이 / 피드속도(기계 결정, 변동 거의 0). 작업자는 투입·배출·검사·재투입(4변 가공 시 회전)에만 개입한다. 유효 사이클 = max(피드 간격, 작업자 핸들링 시간). 패널이 짧거나 1인 운전이면 **핸들링이 병목**이 되어 피로·시간대 효과가 나타나고, 2인 운전·긴 패널이면 기계페이스가 지배해 프로파일을 꺼야 한다. 전류 신호에서는 run 구간의 **간격(gap) 분포**가 핸들링 시간을 직접 보여준다.
  - **CNC 보링/러닝쏘**: 가공 사이클은 결정적, 로딩/언로딩만 인적 변동. 전류 run-length가 거의 일정하면 기계페이스로 분류.
  - **조립·샌딩·포장**: 완전 작업자 페이스 → 프로파일·이질성·여유율 적용 대상.
- 연장근무: Pencavel·Collewet & Sauermann·Hanna et al.(2005, *J Constr Eng Mgmt* 131:734–739, 88개 프로젝트, 주당 시간 증가 시 생산성 감소) 결과에 비추어 **일 9시간 초과 구간에 0.85–0.90 승수**를 두는 정도가 v1에서 합리적이다. https://ascelibrary.com/doi/10.1061/%28ASCE%290733-9364%282005%29131%3A6%28734%29

---

## 4. 학습곡선 (신제품·신입)

### 4.1 모델과 전형적 값 [확립]
- Wright(1936) 누적평균 모델: 항공기에서 누적 생산량 2배마다 단위공수 20% 감소(80% 곡선). Crawford 단위 모델, DeJong(1957)은 기계 비중(학습 불가 부분, 압축불가계수 M)을 분리, Stanford-B는 선행 경험을 반영한다. https://en.wikipedia.org/wiki/Learning_curve , https://scholar.afit.edu/cgi/viewcontent.cgi?article=2116&context=facpub
- 제조 전반의 **최빈 학습률 ≈ 81%**(AFIT 조사; 분산 큼). 자동화가 적고 수작업이 많을수록 DeJong류가 더 잘 맞는다. https://dair.nps.edu/bitstream/123456789/4291/1/AFIT-AM-20-161.pdf
- 비용추정 실무 지침(Stewart, *Cost Estimator's Reference Manual*): 수작업 75%/기계 25% → 80%, 50/50 → 85%, 25/75 → 90%. https://www.globalsecurity.org/military/intro/reference/calc/learn.htm
- Dar-El, Ayas & Gilad(1995, *IIE Transactions*) 이중위상 모델: 초기 사이클은 인지 요소(학습률 낮음≈70%)가, 반복이 많아지면 운동 요소(≈90%)가 지배. https://acnpsearch.tweb-dev.unibo.it/singlejournalindex/483895
- 망각: Jaber & Bonney의 LFCM은 학습·망각을 모두 시간 함수로 두어 **짧은 간헐 생산에서 망각 손실이 심각**함을 보인다(Nembhard & Osothsilp 2001의 실증 비교에서 적합도 논란 있음). https://acris.aalto.fi/ws/portalfiles/portal/78655209/1_s2.0_S016981412100175X_main.pdf
- Nembhard(2000, *Human Factors*)는 섬유 조립공장 2,853개 학습·망각 에피소드로 복잡도·경험이 학습·망각률에 유의한 영향을 준다고 보고했다. https://iro.uiowa.edu/esploro/outputs/journalArticle/The-Effects-of-Task-Complexity-and/9984187063002771
- **가구 산업 고유의 학습률 실증치는 찾지 못했다.** [확인됨: 부재] 교재의 "의자 제조 85%→실제 80%" 예시는 가상 사례다.

### 4.2 한국 중소제조업 외국인력의 "신입 곡선" [확립 — 가장 직접적인 국내 수치]
중소기업중앙회 「2023년 외국인력 고용 관련 종합애로 실태조사」(중소제조업 1,200개사, 2024.1.8 발표): 동일 조건 내국인=100 대비 외국인 생산성은 **3개월 미만 59.0%, 6개월–1년 미만 83.7%, 3년 이상 99.2%**. https://www.dailian.co.kr/news/view/1315006 , https://www.imaeil.com/page/view/2024010816372982126 ; 후속 조사(2026.1 보도)에서는 3개월 미만 66.8%, 1–2년차 98.3, 3년 이상 99.7로 보도됨(연도 구분 필요). https://www.khan.co.kr/article/202601111429001 ; 2024년 조사(1,225개사)에서 기업이 요구하는 수습기간 평균 4개월. https://www.etoday.co.kr/news/view/2214017 . 2018년 조사(600개사)에서는 전체 외국인 생산성 87.4%. https://www.imaeil.com/page/view/2018122516090544766
→ 이를 Wright형으로 역산하면 [추론] 입사 후 약 3개월(≈60근무일)에 60–67%, 9개월에 84%, 24개월에 98%: 완만한 곡선이며, **"3년 이상이면 내국인과 동등"**이므로 근속 1년 이상 인력은 정상상태로 간주해도 된다.

### 4.3 주문제작 가구에서 학습이 언제 중요한가 [추론]
- **반복 제품군(붙박이장·싱크 도어·수납장 모듈)**: 패널 가공은 CNC·에지밴더가 치수만 바꿔 처리하므로 학습 요소가 거의 없다(DeJong M≈1). 조립·검품도 패턴이 같아 정상상태. **v0.5/v1 모두 학습 무시 가능.**
- **신규 제품군(첫 도면·새 하드웨어·곡면)**: 첫 1–3개 유닛의 조립 공수가 정상 대비 +20–40%(85% 곡선에서 1→8번째 유닛 누적평균 비 1.0→0.61의 역수 관점). 이 효과는 **일일 산출 ±10%에는 거의 영향이 없으나 그 주문의 리드타임 ±15%에는 걸릴 수 있다.** 2주 검증창 안에 신규 제품군 주문이 1–2건 있을 수 있으므로, v1에서 "제품군 첫 로트 패널티 계수"(기본 1.3, 2번째 로트 1.1)를 옵션으로 두는 것이 비용 대비 효과적이다.
- **신입(E-9 3개월 미만)**: 15명 중 1명이 60% 속도이면 팀 평균 −2.7%; 그가 병목 공정에 단독 배치되면 그 공정은 −40% → 배치 규칙이 다시 관건. 2주 동안 신입 유무와 배치를 기록하고, 있으면 **숙련 승수 0.6–0.7의 작업자 클래스**로 처리(§2의 이질성 메커니즘 재사용).
- 망각: 주문 간격이 수 주인 특수 제품군은 LFCM 관점에서 매번 "첫 로트" 패널티가 부분적으로 재발한다 — 리드타임 분석에서 제품군 간격 변수로 v1 이후 검토.

---

## 5. 결근·지각·중단

### 5.1 결근·지각 수준 [확립 + 격차 표시]
- 미국 BLS CPS Table 47(2024): 전체 상용근로자 결근율 3.2%(2023년 3.1%, 2020년 3.0%); 제조업은 2.9% 수준(2025, 3자 인용, 원표 대조 필요). https://www.bls.gov/cps/data/aa2024/cpsaat47.htm , https://manufacturingleadgeneration.com/manufacturing-absenteeism-statistics/
- 한국: 2014 근로환경조사(KWCS) 기반 비교에서 연간 병가 경험자 비율 **9.9%**(유럽 OECD 평균 33.0%), 아픈데도 출근(presenteeism) 23.5–23.7%. 즉 **한국 제조 현장은 결근율은 낮고 프리젠티즘(출근했지만 저성능)이 높은 구조**다. https://link.springer.com/article/10.1186/s12889-026-26944-x , https://view.asiae.co.kr/en/article/2024080615353157663 ; 제조·건설 사업체 중 유급병가 제도 보유 3.0%(KIHASA). https://kihasa.re.kr/api/kihasa/file/download?seq=9391
- 오래된 국내 제조업 직접 자료: 대전 제조업 근로자 1,184명(1992) 3개월간 총결근 경험 21.1%, 질병결근 6.9%. https://koreascience.kr/article/JAKO199324717599331.pub?lang=ko (수치가 30년 전이라 참고만)
- **E-9 외국인력**: 2020–2024.8 입국 약 26.5만 명 중 사업장 이탈 7,410명(≈2.8%; 제조업 1,320명, 어업·농축산 비중이 더 큼). https://biz.heraldcorp.com/article/3486909 ; 불법체류율 약 18–20%. https://www.seoul.co.kr/news/newsView.php?id=20241003010005 ; 2023 대한상의 조사에서 사업장 변경 거부 시 태업 41.1%, 무단결근 14.8%, 무단이탈 8.7%. 5일 이상 무단결근 시 이탈신고 가능. https://m.work24.go.kr/cm/c/f/1100/selecSystInfo.do?systClId=SC00000335&systId=SI00000332
- **국내 소규모 제조업의 일 단위 결근율·지각률 공식통계는 존재하지 않는다**(사업체노동력조사는 근로일수·시간만 집계). [확인됨: 부재] → 현장 출근부가 유일한 1차 자료.

### 5.2 중단(interruption)의 크기 [확립 + 추론]
- 작업표본조사(work sampling) 벤치마크: 봉제 라인 부가가치 53%, 비부가가치 37.5%(자재 대기·잡담·이동·돌발정비); https://apparelresources.com/business-news/manufacturing/work-sampling-in-apparel-manufacturing/ 재제조 분해 69.4% VA; https://ieomsociety.org/proceedings/2021indonesia/593.pdf 기계가공 공장(선반·호빙·밀링)에서 **작업자 유휴 34%**, 자재 유휴가 주요 요인; https://www.slideshare.net/rahuluit/machine-utilization-at-krishan-and-co 음료공장 1,000관측에서 자재 대기로 30% 손실. https://jet.utem.edu.my/jet/article/view/6583 ; Chalmers 자동차 사례의 작업자 다운타임 주원인은 자재취급·투입지연·지각·순환·결원. https://odr.chalmers.se/items/3ab1cfc7-f39a-4235-85b2-a904f3419f80
- 가구 전용 작업표본 연구는 찾지 못했으나 [추론] 10–20인 주문제작 공장은 전담 자재담당·지게차 기사가 없고 사장/반장이 전화·고객 응대·도면 확인을 겸하므로 **작업자 시간의 20–35%가 자재 탐색·대기·이동·응대**로 빠지는 위 범위의 상단에 있을 가능성이 높다. 이는 분산이 아니라 **평균 가용률**이므로 CV로 흡수 불가.
- 사무직 중단 빈도(시간당 4–15회) 통계는 제조 현장과 무관하므로 인용하지 않는다.

### 5.3 2주 안에 기록하는 법 [추론, 작업표본 통계는 확립]
- **출근·지각**: 종이 출근부 + 카메라 입구 존의 '첫 사람 등장 시각/마지막 퇴장 시각'(개인 식별 없이 인원수 시계열) → 실제 유효 근무창. 10일 × 15명 = 150 인-일 → 결근 3–5건 기대. 표본은 작지만 **"그 날 누가 없었고 산출이 얼마였나"**를 trace로 재현하는 데는 충분하다.
- **중단**: 카메라 프레임을 무작위 시각에 추출하는 **원격 작업표본조사**. p=0.3, 절대오차 ±5%, 95% 신뢰에 n = 1.96²·0.3·0.7/0.05² ≈ 323관측 → 존당 320–400프레임을 2주에 걸쳐 임의 시각으로 뽑아 {가공/핸들링/이동/탐색·대기/부재/대화·전화} 6범주로 분류(사람 손으로 1–2시간이면 끝난다). 범주별 비율이 곧 스테이션별 유효 가용률이다.
- **긴 중단의 시간 구조**: 전류 idle-gap 분포를 로그 스케일 히스토그램으로 그리면 통상 **3봉**이 나온다 — (a) <2분: 패널 교체·핸들링, (b) 2–10분: 자재 가져오기·측정·전화, (c) >10분: 자재 탐색·지게차 대기·회의·휴게·세팅. (a)는 사이클 분포에 포함, (b)(c)는 **랜덤 비가용 이벤트**(간격 지수분포, 지속 lognormal)로 모델링. 카운터 간격 분포도 같은 방식으로 분해.
- 모델링 선택: 휴게·청소처럼 **시각이 고정된 것은 스케줄**, 자재대기·전화처럼 **시각이 불규칙한 것은 랜덤 비가용**, 결근은 **v0.5에서 실제 출근표를 그대로 입력**(검증용 trace-driven), v1에서 Bernoulli(p≈0.03–0.05/인-일) + 병목 재배치 규칙.

---

## 6. 의사결정 규칙: v0.5 vs v1

### 6.1 판단 기준 [추론]
각 효과가 (i) **평균을 움직이는가**(→ CV로 흡수 불가, 포함 필수) (ii) 효과 크기가 허용오차(일일 ±10%, 리드타임 ±15%, 가동률 ±5%p)의 **절반 이상**인가 (iii) 2주 로그에서 **추가 비용 없이 추정 가능한가**로 판정한다.

| 효과 | 일일 산출 | 리드타임 | 가동률 | 평균 이동? | 2주 로그로 추정? | **v0.5** | **v1** |
|---|---|---|---|---|---|---|---|
| 고정 블록(휴게·청소·시업) | 13–20% | 큼(블록 전후 적체) | 13–20%p | 예 | 예(run-fraction ≈ 0 구간) | **포함** | 포함 |
| 시간가변 승수 m(h) | ±3–5% | ±5% | ±3%p | 소폭 | 예 | 제외(시간당 재현 불필요 시) | **포함**(시간당 히스토그램 검증 시) |
| 유효 가용률(중단·NVA) | 20–35% | 큼 | 20–35%p | 예 | 예(idle-gap, 작업표본) | **포함(스테이션별 계수)** | 랜덤 비가용 이벤트로 분해 |
| 결근·지각 | 특정 날 10–30% | 그 주 주문 +10–20% | 5–10%p | 예(해당 일) | 출근부 필요 | **포함(trace-driven)** | 확률 모델 + 재배치 규칙 |
| 작업자 이질성 | ±5–15%(배치 의존) | ±10% | ±5%p | 예(배치가 고정되면) | 부분(혼합분포·세그먼트 중앙값) | 스테이션별 실측 속도로 흡수 | **2–3 숙련등급 + 배치 규칙** |
| 사이클 CV 0.2–0.35 | <±3%(√N 평균화) | ±5–10%(큐 변동) | ≈0 | 아니오 | 예 | 유지(실측으로 교체) | 유지 |
| 피로/PF&D | 이미 실측에 포함 | — | 이중계상 시 −10%p | 이중계상 위험 | — | **별도 모델 금지**(출처 플래그) | 연장근무 승수만 |
| 학습(신입) | −2~−4%(팀), 병목이면 큼 | — | — | 예(신입 있을 때) | 근속 정보로 | 제외(신입 없을 때) / 숙련등급으로 | 숙련등급 0.6–0.7 |
| 학습(신규 제품군) | <2% | 해당 주문 +20–40% | — | 해당 주문만 | 주문 이력 | 제외 | first-of-family 계수 옵션 |

### 6.2 "CV에 흡수"의 함정 [추론]
- 현재 CV 0.2–0.35는 작업자 간 편차·미세중단을 뭉뚱그린 값일 가능성이 높다. 이 CV로는 **일일 산출 분포의 폭은 얼추 맞추더라도 "어느 날이 낮았는가"는 맞출 수 없다**(그 날의 결근·배치·자재대기가 원인이기 때문). 검증을 "2주 평균 ±10%"가 아니라 **"일별 산출의 절대오차 중앙값 ≤10%"**로 정의한다면 결근·배치·중단은 v0.5부터 필수다.
- 통계적 한계: 10 근무일의 일일 산출 CV가 10–15%면 2주 평균의 표준오차가 3–5%이므로, ±10% 허용오차 자체가 데이터 한계에 근접한다. v0.5 검증은 평균뿐 아니라 **가동률 프로파일·idle-gap 분포 형태**의 일치를 함께 보는 것이 더 강한 검증이다.

---

## 7. 저비용 측정 계획

### 7.1 2주 로그에서 추출할 것 (자동)
**전류 클램프(1 Hz, 기계별)**
1. 상태 분할: off/idle/run(임계값 2단, 디바운스 3–5초). 보링·러닝쏘는 run 전력이 사이클 내에서 변하므로 **run-length 히스토그램**이 곧 가공 사이클(기계페이스 판정: CV<5%면 결정적).
2. **시간대별 run-fraction 프로파일**(15분 빈, 평일 평균 ± SE) → 하드 블록 + 소프트 승수.
3. **idle-gap 분포**(로그 빈, 3봉 분해) → 핸들링 시간 / 단기 중단 / 장기 비가용.
4. **실제 유효 근무창**: 첫 run 시각, 마지막 run 시각의 일별 분포(시업 지연·조기 마감·연장근무 실태).
5. 요일·일별 총 run 시간 → 일일 가동률의 분산(결근일·자재 결품일 탐지).
6. 에지밴더: run 구간 길이 ≈ 패널 길이/피드속도 → **패널 길이 혼합분포**도 부수적으로 얻는다; 연속 run 간 gap = 핸들링 → 1인/2인 운전 판별.

**광전 카운터(2–3 게이트)**
7. 시간당 통과 수 히스토그램(15분 빈) → 전류 프로파일과 교차검증.
8. 연속 통과 간격 분포 → 사이클 혼합분포(2–3성분) 적합, **일중 세그먼트별 중앙값 변화**로 배치 교체 탐지.
9. 게이트 간 누적곡선 차이 → 구간 WIP·체류시간(리드타임 검증용 Little's law).

**카메라(3대, 엣지 처리·프레임 폐기)**
10. 존별 인원수/분 → 수작업 스테이션의 점유 프로파일(=수작업 run-fraction), 이동·탐색 존(자재창고·지게차 통로) 점유.
11. 무작위 320–400프레임 작업표본(존당) → 6범주 유효 가용률.
12. 입구 존 첫/마지막 인원 시각 → 지각·조퇴 집계(개인 비식별).

### 7.2 1일 방문에서만 얻을 수 있는 것
- **스톱워치 시간연구**: 수작업 스테이션별 10–20 사이클, 요소 분해(핸들링/가공/검사), **성과평정(rating)** 기록 — 실측 분포가 없는 스테이션의 정상시간 + PF&D 적용 근거.
- **배치 규칙 인터뷰**: 고정/순환/응원 규칙, 2인 작업 조합, 병목 공정에 누가 주로 서는가(개인 식별은 "숙련 등급" 수준으로만 기록).
- **여유·휴게·청소 관행**: 참 시간, 청소 시작 시각, 조회, 월요일 자재 입고 패턴, 연장근무 결정 규칙.
- **출근부 3개월치 + 근속표**: 결근·지각률, 신입(3개월 미만) 수, E-9 비율 — 2주 표본의 소표본 문제를 보완.
- **주문 이력 3–6개월**: 제품군별 재주문 간격(망각·first-of-family 판단), 긴급주문 비율.
- **중단 원인 목록**: 전화·고객 방문 응대자, 자재 위치 체계, 지게차 1대 공유 여부 — 7.1의 idle-gap 3봉에 원인 라벨을 붙이는 데 쓴다.
- **에지밴더·CNC 파라미터**: 피드속도, 공구교환·프로그램 로딩 시간 → 기계페이스 사이클의 결정적 모델.

### 7.3 산출물을 모델 파라미터로 연결
- v0.5: 스테이션별 {출처 플래그, 기본 사이클 분포(실측/시간연구×PF&D), 유효 가용률 계수, 캘린더(블록)}, 공장 전체 {실제 출근표 trace}.
- v1: 추가로 {m(h) 15분 승수 벡터(수작업 스테이션만), 숙련등급 2–3단계 × 배치 규칙, 랜덤 비가용 이벤트(간격·지속 분포), 연장근무 승수, first-of-family 계수}.
- 각 단계의 검증: v0.5는 일별 산출·가동률·게이트 간 체류시간, v1은 추가로 시간당 산출 히스토그램·idle-gap 분포의 형태 일치.

---

## 8. 한계와 미확인 사항
- Durakovic(2025)의 시간대별 퍼센트, Baines et al.(2004)의 오차 크기, Sun et al.(2023)의 시간대별 서비스율 곡선 값, Mississippi State 논문의 저자명, Niebel & Freivalds의 정확한 상수는 원문 미열람(초록·검색 발췌 기반)이다.
- 가구 산업 고유의 학습률·작업표본 수치, 국내 소규모 제조업의 일 단위 결근·지각 통계는 **존재를 확인하지 못했다**. 본 보고서의 해당 수치는 인접 산업과 국내 외국인력 조사로 대체한 추정이다.
- 작업자 간/내 CV 분해 비율(0.15–0.20 / 0.10–0.20)은 Hunter et al.의 SDp 19%와 1:2 비율 통례에서 역산한 추론이며, 현장 혼합분포 적합으로 교체해야 한다.

---

## 참고문헌 (저자, 연도, 제목, URL)
1. Sun, Liu & Ouyang (2023). Time-Varying Physician Productivity and Implications for ED Modeling and Staffing. *M&SOM*. https://pubsonline.informs.org/doi/10.1287/msom.2023.0081
2. Durakovic, B. (2025). The Relationship Among Production Errors and Working Hours for Three Shifts: A Case Study from a Metal Coating Business. Springer RTASCE. https://link.springer.com/chapter/10.1007/978-3-031-82881-2_20
3. Monk, T.H. (2005). The post-lunch dip in performance. *Clin Sports Med*. https://pubmed.ncbi.nlm.nih.gov/15892914/
4. Pencavel, J. (2015). The Productivity of Working Hours. *Economic Journal* (IZA DP 8129). https://docs.iza.org/dp8129.pdf
5. Collewet & Sauermann (2017). Working hours and productivity. *Labour Economics*. https://swopec.hhs.se/sofiwp/abs/sofiwp2017_003.htm
6. Brachet, David & Drechsler (2012). The Effect of Shift Structure on Performance. *AEJ: Applied*. https://www.nber.org/papers/w16418.pdf
7. Folkard & Tucker (2003). Shift work, safety and productivity. *Occup Med*. https://pubmed.ncbi.nlm.nih.gov/12637593/
8. FWPA (NZ). Time of day study on machine productivity (wood processing yard). https://fwpa.com.au/news/time-of-day-study-on-machine-productivity/
9. Vernon, H.M. (1921). Industrial Fatigue and Efficiency. https://www.routledge.com/Industrial-Fatigue-and-Efficiency/Vernon/p/book/9781032270364
10. Baines, Mason, Siebers & Ladbrook (2004). Humans: the missing link in manufacturing simulation? *SMPT*. https://publications.aston.ac.uk/id/eprint/38667/1/Humans_the_missing_link_in_manufacturing_simulation.pdf
11. Siebers, P.-O. (Cranfield thesis). Impact of human performance variation on the accuracy of manufacturing system simulation models. https://dspace.lib.cranfield.ac.uk/handle/1826/10750
12. Hunter, Schmidt & Judiesch (1990). Individual Differences in Output Variability as a Function of Job Complexity. *J Appl Psych* 75:28–42. https://www.gwern.net/doc/iq/ses/1990-hunter.pdf
13. HFES 25th Annual Meeting (1981) paper on fastest/slowest operator ratio and paced lines. https://sage.cnpereading.com/doi/10.1177/1071181381025001140
14. Mississippi State Univ. dissertation (2019). Wooden door manufacturing process capability/line balance (CV 12–23% manual). https://scholarsjunction.msstate.edu/td/3642
15. Shafer, Nembhard & Uzumeri (2001). The Effects of Worker Learning, Forgetting, and Heterogeneity on Assembly Line Productivity. *Management Science* 47:1639–1653. https://pubsonline.informs.org/doi/pdf/10.1287/mnsc.47.12.1639.10236
16. Nembhard & Osothsilp (2002). Task complexity effects on between-individual learning/forgetting variability. *IJIE* 29:297–306. https://iro.uiowa.edu/esploro/outputs/journalArticle/Task-complexity-effects-on-between-individual-learningforgetting/9984187065302771
17. Nembhard, D.A. (2000). Effects of task complexity and experience on learning and forgetting. *Human Factors*. https://iro.uiowa.edu/esploro/outputs/journalArticle/The-Effects-of-Task-Complexity-and/9984187063002771
18. Peltokorpi & Niemi (2018). Differences between worker pairs in manual assembly: a case study. *Procedia Manufacturing* 25. https://acris.aalto.fi/ws/portalfiles/portal/27476511/1_s2.0_S2351978918306498_main.pdf
19. ILO / Kanawaty (ed.) (1992). Introduction to Work Study, 4th ed. https://digitallibrary.un.org/record/115655 ; IS 11500 (1985) Relaxation allowances. https://services.bis.gov.in/tmp/SR11500.pdf
20. PFD allowance (Niebel & Freivalds 계열 요약). https://en.wikipedia.org/wiki/PFD_allowance
21. Rohmert rest allowance 적용·비판. https://ijoh.tums.ac.ir/index.php/ijoh/article/view/512/735 ; https://pubmed.ncbi.nlm.nih.gov/8817118
22. Salvendy (1982) NIOSH review; Burke & Salvendy (1981) meta-analysis on pacing. https://stacks.cdc.gov/view/cdc/236960 ; https://www.iloencyclopaedia.org/component/k2/item/19-work-pacing
23. Hanna, Taylor & Sullivan (2005). Impact of extended overtime on construction labor productivity. *J Constr Eng Mgmt* 131:734–739. https://ascelibrary.com/doi/10.1061/%28ASCE%290733-9364%282005%29131%3A6%28734%29
24. Learning curve 개요(Wright/Crawford/DeJong/Stanford-B). https://en.wikipedia.org/wiki/Learning_curve ; AFIT 학습률 조사(최빈 81%). https://dair.nps.edu/bitstream/123456789/4291/1/AFIT-AM-20-161.pdf ; Stewart 수작업/기계 비중별 학습률. https://www.globalsecurity.org/military/intro/reference/calc/learn.htm
25. Dar-El, Ayas & Gilad (1995). A dual-phase model for the individual learning process in industrial tasks. *IIE Trans*. https://acnpsearch.tweb-dev.unibo.it/singlejournalindex/483895
26. Jaber & Bonney LFCM 및 망각 모델 비교(Sikström & Jaber 2004 등). https://acris.aalto.fi/ws/portalfiles/portal/78655209/1_s2.0_S016981412100175X_main.pdf
27. 중소기업중앙회 (2024.1). 2023년 외국인력 고용 관련 종합애로 실태조사 — 근속별 생산성 59.0/83.7/99.2. https://www.dailian.co.kr/news/view/1315006 ; https://www.imaeil.com/page/view/2024010816372982126 ; 후속 조사 보도(66.8). https://www.khan.co.kr/article/202601111429001 ; 수습기간 4개월(2024). https://www.etoday.co.kr/news/view/2214017
28. BLS CPS Table 47 (2024) Absences. https://www.bls.gov/cps/data/aa2024/cpsaat47.htm ; 제조업 2.9%(3자 인용). https://manufacturingleadgeneration.com/manufacturing-absenteeism-statistics/
29. 한국 결근·프리젠티즘 비교(KWCS 2014 vs EWCS 2015). https://link.springer.com/article/10.1186/s12889-026-26944-x ; https://view.asiae.co.kr/en/article/2024080615353157663 ; KIHASA 병가제도. https://kihasa.re.kr/api/kihasa/file/download?seq=9391
30. 제조업 근로자들의 결근요인 분석 (1992, 대전). https://koreascience.kr/article/JAKO199324717599331.pub?lang=ko
31. E-9 이탈 통계(헤럴드경제 2024; 서울신문 2024). https://biz.heraldcorp.com/article/3486909 ; https://www.seoul.co.kr/news/newsView.php?id=20241003010005 ; 이탈신고 기준(고용24). https://m.work24.go.kr/cm/c/f/1100/selecSystInfo.do?systClId=SC00000335&systId=SI00000332
32. 작업표본 벤치마크: 봉제. https://apparelresources.com/business-news/manufacturing/work-sampling-in-apparel-manufacturing/ ; 재제조. https://ieomsociety.org/proceedings/2021indonesia/593.pdf ; 기계가공. https://www.slideshare.net/rahuluit/machine-utilization-at-krishan-and-co ; 음료. https://jet.utem.edu.my/jet/article/view/6583 ; Chalmers 자동차. https://odr.chalmers.se/items/3ab1cfc7-f39a-4235-85b2-a904f3419f80
33. 비침습 전류 기반 기계상태 판별 특허 EP4030254. https://data.epo.org/publication-server/rest/v1.2/patents/EP4030254NWA1/document.html
34. 프라이버시 보존 영상분석: arXiv 2505.07306; arXiv 2405.19173. https://arxiv.org/pdf/2505.07306 ; https://arxiv.org/abs/2405.19173v1
35. 사업장 CCTV 법적 요건(근로자참여법 §20①14, 개인정보보호법, 가이드라인). https://www.shinkim.com/kor/media/newsletter/2201 ; https://byline.network/2023/01/0131_02/
36. 국내 가구공장 근무시간 관행(구인공고). https://www.jobploy.kr/ko/recruit/manufacturing-gyeonggi-wood-furniture-production-staff ; https://www.invione.com/jobs/recruitment/all/detail/K130232605220019