# 한국 가구공장 디지털 트윈(DES + 3D) 구축을 위한 도메인 리서치 보고서

**작성일: 2026-10-10 | 대상: 디지털 트윈 모델링 팀 (공장 방문 전 사전 지식)**

> **리서치 범위 및 한계 (반드시 읽을 것)**
> - 이 세션의 웹 검색 예산(200회/턴)이 약 45회 검색 후 소진되었고, 이 환경의 egress 프록시가 대부분의 외부 사이트 직접 열람(mdpi.com, homag.com, scmgroup.com, 대한상의 korcham.net, ddaily, etnews, bizinfo.go.kr 등)을 403으로 차단해 **공고문 원문·논문 전문을 열어 보지 못했다.** 따라서 수치는 (1) 검색 스니펫에서 확인된 것과 (2) 산업공학/목공기계 일반 지식에 근거한 **추정치[est.]** 로 구분했다. `[est.]` 표시가 있는 값은 공장 방문 시 실측으로 교체해야 한다.
> - 추가 검색이 필요하면 후속 메시지로 요청하면 이어서 진행 가능하다(특히 KOSIS C32 통계, 국산 목공기계사 제원, 개별 가구사 스마트팩토리 보도).

---

## 1. 공정 흐름(Process flows)과 공정별 기본값

### 1(a) 판재가구 (PB/MDF/합판 기반, 붙박이장·주방·사무가구·KD 가구) — 가장 흔한 한국 중소 가구공장 형태

```
원자재 입고(PB/MDF 4x8, 6x8, 멜라민 LPM 판재) → 판재 보관(랙/바닥 적재, 지게차)
 → 재단: 런닝쏘(beam saw) 또는 판넬쏘(sliding table saw) 또는 CNC 네스팅
 → 엣지밴딩(edge bander, 직선/곡선·소프트포밍) [+ 리턴컨베이어]
 → 보링/가공: CNC 머시닝센터(수직/수평), 다축보링기(multi-boring), 6면 드릴
 → 하드웨어 삽입(힌지컵, 미니픽스/캠록, 다보, 레일) — 대부분 수작업 + 에어툴
 → (선택) 프레스/라미네이팅(PET/PVC 랩핑, 멤브레인 프레스, 진공프레스) — 도어/필름가구
 → (선택) 샌딩·도장(스프레이·UV라인·우레탄) — 도장가구/원목도어
 → 조립(완조립 full assembly) 또는 KD 플랫팩 분류(sorting/kitting)
 → 포장(수축필름·종이박스·스티로폼 앵글, 반자동 포장기)
 → 완제품 창고 → 출하(배송/시공)
```

#### 표 1-A. 판재가구 공정별 기본값 (DES 초기 파라미터)

| 공정(Station) | 대표 설비 / 브랜드 | 사이클타임(정상) | 셋업/체인지오버 | 인원 | 설치면적 | 전력(kW) | 비고 |
|---|---|---|---|---|---|---|---|
| 판재 입·출고 | 지게차, 진공리프터, (자동화) Homag STORETEQ / SCM Flexstore | 지게차 1팔레트 2–5분 [est.] | — | 1 | 100–400 m² [est.] | 지게차(전동) 10–15 | 수작업 판재 피킹이 숨은 병목인 경우 많음 |
| 재단 – 런닝쏘(beam saw) | Homag SAWTEQ B-300 (3,800 mm, 주모터 24 kW + 스코어링 2.2 kW, 이송 130 m/min), Biesse Selco WNTR 600 (13.5–18 kW, 150 m/min), SCM Gabbiani, Nanxing NPB, KDT KS-432; 국산 중고/중국산 다수 | 1 cut 10–20초, 시트당(4x8, 멀티컷 패턴) **1.5–4분/시트** [est.]; 북 컷(2–4장 적층) 시 장수당 환산 ↓ | 패턴 전환 1–3분(자동), 톱날 교체 15–30분 [est.] | 1–2 | 60–120 m² (리프트테이블 포함) | 15–30 | 시트당 산출 부품 10–25개 [est.] |
| 재단 – 판넬쏘(sliding table saw) | Altendorf F45, SCM si, Felder K series, 국산 | 1 cut 20–40초, 시트당 4–8분 [est.] | 각도/펜스 1–2분 | 1–2 | 30–50 m² | 4–7.5 | 영세공장의 주력 |
| 재단 – CNC 네스팅 | Homag CENTATEQ N-200/300, Biesse Rover, SCM Morbidelli x200, Nanxing NCG, KDT | **기계시간 6–12분/4x8 시트, 핸들링 포함 10–20분/시트**; 60–100 시트/8h ([woodweb](https://woodweb.com/knowledge_base/CNC_Routing_Minutes_per_Sheet.html), [woodweb](https://woodweb.com/knowledge_base/Nested_Base_Output__Nested_Base_Router_Workflow_an.html)) | 시트교체+스포일보드 청소 ~5분; 프로그램 전환 0(자동) | 1–2 | 60–100 m² | 20–35 (스핀들 9–12 + 진공펌프 7.5–11×1~2 + 축) [est.] | 재단+보링 통합, 라벨링 대기 중 기계 유휴 흔함 |
| 엣지밴딩 (직선) | Homag EDGETEQ S-200/S-300/S-380/S-500 (S-380: 8–18 m/min; S-500: 16–30 m/min [Homag](https://www.homag.com/en/news-events/news/article/livehomag-edge-processing-concepts-to-suit-every-production-level)), Biesse Akron 1440 (12–18 m/min, 13 kW [exapro](https://www.exapro.com/sp/biesse-akron1440-54203/)), Biesse Jade 340 (12 m/min, 18 kW), SCM Olimpic/Stefani, KDT KE-468J, Nanxing NB6J, 국산(현대산기 등) | 부품당 변 1개 = 길이/이송속도 + 간격(≈0.6–1.0 m) → **600 mm 부품 1변 ≈ 6–8초 @12 m/min**; 4변 밴딩 부품 1개 = 4회 통과 + 회전/핸들링 ≈ **40–90초/부품** [est.]; 수작업 리턴 시 **실효 200–400 부품/시프트/대**, 리턴컨베이어 시 500–800 [est.] | 엣지테이프 교체 2–5분, 접착제(EVA→PUR) 색 교체 15–40분, 두께/프로파일 교체 5–15분 [est.] | 1–2 (리턴컨베이어 시 1) | 40–80 m² (길이 5–8 m) | 10–20 (히터 포함), 압축공기 6–7 bar 소비 큼 | **중소공장 1순위 병목** |
| 엣지밴딩 (곡선/수동) | 수동 곡선 밴더, 핸드 트리밍 | 부품당 2–5분 [est.] | — | 1 | 10–20 m² | 2–3 | 트리밍·스크래핑 수작업 |
| CNC 보링(수직 머시닝) | Homag DRILLTEQ V-500 (라우터 10 kW, 25축: 수직15/수평10 [hoechsmann](https://wtp.hoechsmann.com/cz/lexikon/pdf/hom_drillteqv_-500_2019_en.pdf)), Biesse Skipper, Weeke BHX 200/500, SCM Morbidelli CX | **부품당 20–60초** (측판 힌지컵+다보+캠 기준) [est.]; 리턴 옵션 시 +15% 효율(제조사 주장) | 프로그램 자동, 툴 교체 5–15분 | 1 | 25–40 m² | 15–25 (진공 포함) [est.] | 바코드 스캔→프로그램 호출 |
| 다축 보링기 (multi-boring, 32 mm 시스템) | 국산/대만산 2–3열 보링, Vitap, SCM Startech | 부품당 15–40초 [est.] | 핀 셋업 10–30분(제품 바뀔 때마다) [est.] | 1 | 15–25 m² | 5–8 | 영세공장 주력, 셋업 손실 큼 |
| 6면 드릴 (six-side CNC drill) | Nanxing/KDT 6면 드릴, Homag DRILLTEQ H-600 | 부품당 15–30초 [est.] | 자동 | 0.5–1 | 40–60 m² | 15–20 [est.] | 네스팅+6면드릴 조합이 중국산 라인 표준 |
| 하드웨어 삽입/조립준비 | 힌지압입기, 에어드릴, 캠록 삽입 | 부품당 20–60초, 수납장 1대 5–15분 [est.] | — | 2–6 | 60–150 m² | 1–3 (에어툴은 컴프레서 부하) | 인력 집약, 교차훈련 효과 큼 |
| 프레스/랩핑 (선택) | 멤브레인 프레스(Wemhöner, 국산), 진공프레스, PVC/PET 랩핑기, 콜드프레스 | 멤브레인 1사이클 3–6분/장(10–20 도어) [est.]; 랩핑 10–20 m/min | 필름 교체 10–20분 | 2 | 60–100 m² | 20–40 (히터) [est.] | 도어/필름가구만 |
| 샌딩 (선택) | 와이드벨트 샌더 1,300 mm (총 11–50+ kW, 이송 5–25 m/min [exapro](https://www.exapro.com/boere-elite-tkk-1300-p230429006)), 국산 |  부품당 10–30초/패스 [est.] | 벨트 교체 5–10분 | 1 | 25–40 m² | 15–45 | 집진 부하 최대 공정 |
| 도장 (선택) | 스프레이부스(수동/왕복기), UV 플랫라인(롤러코터+UV램프), 건조실 | 스프레이 1면 1–2분/도어 [est.], 건조 **우레탄 4–24시간**, 수성 1–4시간, **UV 수초(인라인)** [est.] | 색 교체 20–40분(건 세척) [est.] | 2–4 | 100–300 m² (건조실 포함) | 부스 배기팬 5–15, UV램프 20–60/라인, 건조실 히터 10–30 [est.] | 건조 = 시간·공간 병목(WIP 체류) |
| 조립 (완조립) | 작업대, 에어타카, 클램프, 케이스클램프 | 수납장 1대 10–30분, 책상 5–15분 [est.] | — | 2–8 | 100–300 m² | 1–3 | 인력·숙련 의존 |
| KD 분류/키팅 | 소팅 랙, 바코드 스캐너, (자동) Homag SORTEQ | 부품당 10–20초 [est.]; 1오더 키트 5–15분 | — | 1–3 | 60–200 m² | 0 | 오더 완결성(kit completeness) 대기가 리드타임 지배 |
| 포장 | 반자동 수축포장기, 박스 밀봉기, 스트래핑 | 수납장 1대 3–8분, KD 박스 2–4분 [est.] | — | 2–4 | 80–150 m² | 수축터널 10–20 | |
| 완제품 창고/출하 | 랙, 지게차 | 상차 팔레트당 3–5분 [est.] | — | 1–2 | 200–800 m² | — | |
| **집진기(dust collection)** | 중앙집진(백필터/사이클론) 20–75 HP (15–55 kW) [est.], 국산(한국집진 등) | 상시 운전 | — | — | 외부 | **15–55** (중형), 영세 5.5–11 | 오리건 캐비닛도어 공장 사례: 집진기+팬이 **전력의 약 50%**, VFD on-demand로 연간 에너지 1/3 절감 ([Energy Trust](https://blog.energytrust.org/?p=2957)); 목재제품 제조 전력의 주요 end-use ([ACEEE 2005](https://www.aceee.org/files/proceedings/2005/data/papers/SS05_Panel01_Paper11.pdf)) |
| **컴프레서(압축공기)** | 스크류 15–37 kW (20–50 HP) [est.] | 상시(부하율 50–70%) | — | — | 외부 | **15–37** | 엣지밴더·CNC 진공·에어툴·프레스 공급. 누설 20–30% 흔함 [est.] |

**규모 감(중소 판재가구공장, 종업원 10–30명) [est.]:** 건평 1,500–5,000 m², 계약전력 150–400 kW, 설비 피크부하 100–250 kW(집진+컴프레서가 20–35%), 일 생산 수납장 환산 50–200대 또는 부품 1,500–5,000개/일.

**에너지 모델링 팁:** DES에 전력을 붙일 때 설비별 상태(idle/run/setup)별 kW를 두고, 집진기·컴프레서는 "공장 가동 중 상시 부하"로 별도 모델링(VFD 유무가 what-if 변수). Hoecker Polytechnik은 캐비닛 생산 에너지 50% 절감 사례를 주장한다([hoecker](https://www.hoecker-polytechnik.com/news-events/news/read/energy-use-in-cabinet-production-reduced-by-50)) — 벤더 자료.

### 1(b) 원목(solid wood) 가구

```
원목 야드(제재목 입고, 함수율 측정) → 건조(kiln: 천연건조 수개월 + 인공건조 1–4주, 목표 함수율 8–12%)
 → 러프밀(rough mill): 크로스컷(cut-off saw) → 립쏘(rip saw, 직선/멀티립) → 수압대패(jointer)/자동대패(planer) → 몰더(4면 몰더)
 → 집성(핑거조인트/판재 집성, 집성프레스 RF/콜드)
 → 가공/조이너리: 테노너, 도브테일/장부가공, CNC 라우터(3축/5축), 보링
 → 샌딩(와이드벨트 → 오비탈/수동)
 → 도장(스테인 → 샌딩실러 → 탑코트; 오일/수성/우레탄), 건조
 → 조립(프레임 클램프, 접착) → 검사 → 포장
```
[ILO 백과: 전형적 흐름 rough planer → cutoff saw → rip saw → finish planer → moulder → lathe/saws/routers/sanders; 건조는 자체 킬른 또는 건조목 구매](https://iloencyclopaedia.org/part-xiii-12343/woodworking/item/935-woodworking-processes)

| 공정 | 대표 설비 | 사이클/속도 | 인원 | kW [est.] |
|---|---|---|---|---|
| 건조(kiln) | 증기/전기/제습식 킬른 (Wood-Mizer 300–35,000 bf), 국산 | 1–4주/배치(수종·두께별), **배치 공정** — DES에서 "capacity-limited batch resource"로 | 0.5 | 히터 20–100, 팬 5–15 |
| 크로스컷 | 옵티마이징 크로스컷(Weinig OptiCut), 수동 | 5–15 컷/분 | 1 | 4–7.5 |
| 립쏘 | 멀티립(Raimann), 직선립 | 이송 10–40 m/min | 1–2 | 15–37 |
| 대패/몰더 | Weinig Powermat, Yates, 국산 4면대패 | 이송 6–30 m/min; 셋업 20–60분(프로파일 교체) | 1–2 | 몰더 25–60(4–6 스핀들 합산) |
| 집성 프레스 | RF 집성기, 콜드프레스 | RF 2–5분/배치, 콜드 30–60분 | 1–2 | RF 10–30 |
| CNC/테노너 | 5축 CNC, 더블엔드 테노너 | 부품당 1–5분 | 1 | 15–25 |
| 샌딩 | 와이드벨트 + 수동 | 부품당 0.5–3분 | 1–3 | 15–45 |
| 도장·건조 | 부스+건조실 | 도장 2–5분/부품, 건조 4–24시간 | 2–4 | 15–40 |
| 조립 | 클램프 | 의자 10–20분, 테이블 20–40분 | 2–6 | 1–3 |

원목 공정은 **수율(yield) 변동**(옹이·휨 제거로 40–65%), **건조 배치**, **셋업이 긴 몰더**가 모델의 핵심 불확실성. Weinig/Progressive Systems 사례처럼 WoodEye 스캐너 → 옵티마이징 크로스컷으로 수율을 올린다([Woodworking Network](https://www.woodworkingnetwork.com/red-book/best-practices-guide/miller-wood-expands-component-capabilities)).

### 1(c) 소파/침대 등 장식(upholstered) 가구

```
프레임 제작(합판/원목/PB 재단 → 조립, 타카) → 스프링/웨빙(지그재그 스프링, 탄성벨트) → 폼 재단(CNC 폼커터/밴드나이프) → 폼 접착·성형
 || 병렬: 원단/가죽 재단(CNC 커터 또는 수동) → 봉제(sewing, 산업용 미싱 20–30대 규모)
 → 장식(upholstery: 폼 부착, 커버 씌우기, 스테이플 1,000–1,800개/대) → 쿠션 충전(폼+솜/깃털) → 다리/하드웨어 → 검사 → 포장(비닐+박스/랩)
```
- 수치 근거: 영국 HSL 공장 사례 — 봉제부서 23명이 소파 1대 48피스 봉제, 장식공정 **최대 1,800 스테이플/대**([hslchairs](https://hslchairs.com/inside-the-factory/the-process)); 공장식 표준 소파 **총 작업시간 8–20시간/대**(2026 비용가이드, 신뢰도 중) vs 수공예 52시간(마케팅 자료)([risingsunartscentre](https://new.risingsunartscentre.org/news/cost-of-making-a-couch-2026.html), [hitchmylius](https://www.hitchmylius.co.uk/?p=25)).
- DES 기본값 [est.]: 프레임 20–40분/대(2인), 폼 재단 5–10분/대, 원단 재단 10–20분/대, 봉제 60–150분/대(여러 미싱 병렬), 장식 90–240분/대(1인 셀 방식), 포장 10분. 소파는 **공정별 병렬 셀 + 자재 동기화(프레임·폼·커버 3갈래 합류)** 가 모델 구조의 핵심. 매트리스 공장은 TOC 적용 논문 참고([PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4977234/)).

### 국산 목공기계 메이커
요청된 신우·대성·양지·우성·한국목공기계는 검색 예산 소진으로 제원 확인 못 함(검색 1회에선 중국 공급자 목록과 **(주)현대산기 엣지밴더 유닛**만 확인됨([komachine](https://www.komachine.com/ko/companies/hyundai-sangi/products/23991-edge-bander-unit-edge-bander))). 현장 방문 시 **명판(nameplate) 사진으로 kW·이송속도·제조년도**를 수집할 것. 한국 중소 가구공장은 통상 **런닝쏘·엣지밴더·보링기는 중국산(KDT/Nanxing/Holztek) 또는 유럽 중고, 보조기계는 국산**이 섞인 구성 [est.].

---

## 2. 중소 가구공장의 전형적 병목·비효율과 개선 레버

### 2.1 병목·비효율 (방문 시 체크리스트)
1. **엣지밴더**: 부품 1개가 4변 → 4회 통과, 수작업 리턴으로 1대당 실효 처리량이 기계 능력의 40–60%. 벤더 블로그 사례: 더 빠른 엣지밴더로 교체했는데 생산량 12%만 증가 — **핸들링이 진짜 제약**([bcamcnc](https://www.bcamcnc.com/how-to-choose-the-right-edge-banding-machine-for-your-furniture-factory-in-2026/)); Neville Johnson은 노후 엣지밴더가 "significant production bottleneck"이라 SCM Stefani XD 2대 도입 후 잔업 없이 기록 생산([SCM case](https://www.casestudies.com/company/scm/case-study/neville-johnson-achieves-record-production-outputs-in-12-months-with-scm)).
2. **도장·건조**: 건조시간(4–24h)이 WIP 체류와 공간을 잠식, 색 교체 셋업이 배치를 키움.
3. **수작업 운반/핸들링**: 대차·지게차 이동, 라벨 붙이는 동안 CNC 유휴("let parts sit on the router bed while they label", woodweb).
4. **판재 보관·피킹**: 바닥 적층 → 원하는 색상 판재 꺼내려면 재적재(double handling).
5. **잔재(offcut) 관리**: 잔재 미등록 → 수율 저하, 재단 최적화 소프트웨어 미사용.
6. **오더 체인지오버·배치 크기**: 색상/두께 기준 큰 배치 → 키트 완결 대기, 분류 공간 폭증.
7. **키팅/분류**: 한 오더의 부품이 여러 배치에 흩어져 마지막 부품을 기다림(assembly starvation).
8. **다축 보링기 셋업**: 제품 바뀔 때마다 핀 재배치 10–30분.
9. **집진·공압**: 집진기 상시 풀가동, 공압 누설, 컴프레서 용량 부족 시 엣지밴더 품질불량.
10. **정보 흐름**: 종이 작업지시, 바코드 미사용 → 진척 불가시(MES 부재).

### 2.2 개선 레버 (what-if 시나리오 후보)
| 레버 | 기대효과(문헌/벤더 주장) | DES 모델링 방식 |
|---|---|---|
| 재단 최적화(네스팅/컷 리스트 소프트웨어: Homag intelliDivide, Cutrite, OptiCut 등) | 수율 +3–8%p, 재단시간 −10–20% [est.] | 시트당 부품수·잔재율 파라미터 변경 |
| Batch-one / 오더 기반 흐름 + 바코드 | 리드타임 −30–60% [est.]; SCM Rimobel "3배 빠르고 자원 절반"(벤더)([SCM](https://www.casestudies.com/company/scm/case-study/rimobel-becomes-3x-faster-with-half-the-resources-using-scm)); SCM 배치1 캐비닛 셀 **600 pcs/shift**([SCM](https://scmgroup.com/en/scmwood/solutions/store-e-9x12-x400-1536-cell-h-ux200.sp129802)) | 배치 크기·시퀀싱 규칙 변경 |
| 엣지밴더 리턴컨베이어(Homag LOOPTEQ O-300/O-600, SCM) | 1인 운전 가능, 처리량 +30–60% [est.]; Homag 셀: EDGETEQ S-380+LOOPTEQ O-300, S-500+O-600([Homag](https://www.homag.com/en/news-events/news/article/livehomag-edge-processing-concepts-to-suit-every-production-level)) | 핸들링 시간 단축, 작업자 1명 해제 |
| 2호기 엣지밴더 추가 | 병목 해소(Neville Johnson 사례) | 리소스 capacity 2 |
| 자동 판재창고(Homag STORETEQ, SCM Flexstore) + 쏘/네스팅 직결 | 피킹 인력 0, 재단 셀 1인화, 잔재 자동관리 | 입고→재단 대기·핸들링 시간 제거 |
| 소팅/버퍼 시스템(SORTEQ, 소팅랙 + 스캔) | 조립 기아(starvation) 감소 | 키트 완결 로직 |
| U자형/셀 레이아웃, 스파게티 다이어그램 기반 재배치 | 이동거리 −20–40% [est.]; 단, 슬로베니아 AnyLogic 연구는 "기계 재배치만으론 총 제조시간 거의 불변 → 설비 추가 필요"([academia](https://www.academia.edu/48165884/Optimization_of_a_furniture_factory_layout)) | 이동시간 매트릭스 |
| SMED(엣지테이프·접착제·보링핀) | 셋업 −50% [est.] | setup time 분포 변경 |
| Kanban(하드웨어·엣지테이프·포장재) | 결품 대기 제거 | 자재 가용성 제약 |
| OEE 모니터링/MES, 교차훈련 | 가동률 가시화, 인력 유연성 | 작업자 스킬 매트릭스 |
| 집진 VFD on-demand, 공압 누설 관리 | 전력 −30%(오리건 사례) | 에너지 상태 모델 |

---

## 3. 한국 가구산업 맥락

### 3.1 산업 통계
- **시장 규모**: IMARC 추정 한국 가구시장 **2024년 126억 달러**, 2025–2033 CAGR 3.42%, 2033년 177억 달러([IMARC](https://www.imarcgroup.com/report/ko/south-korea-furniture-market)) — 민간 추정치. 홈퍼니싱 시장은 2015년 12.5조 → 2023년 18조 원 전망(통계청 인용, 2017 기사)([한경](https://magazine.hankyung.com/business/article/201709189486b)).
- **사업체/종사자 (C32 가구 제조업)**: 검색 결과에 KOSIS 수치가 직접 잡히지 않았다. **KOSIS → 광업제조업조사 → 산업중분류(32 가구) → 사업체수·종사자수·출하액(10인 이상)** 및 **전국사업체조사(1인 이상)** 에서 직접 조회 필요([KOSIS 사업체수](https://kosis.kr/visual/nsportalStats/detailContents.do?listId=B&statJipyoId=3649&vStatJipyoId=4974)). 참고: 2023년 전국사업체조사(잠정) 전체 사업체 623.9만 개, 제조업 사업체 −9.2%([국가데이터처](https://mods.go.kr/board.es?mid=a10301010000&bid=233&list_no=432931&act=view&mainXml=Y)). 일반 지식 기준 [est.]: 가구제조 사업체(1인 이상) 약 1.5–2만 개, 종사자 7–9만 명, 10인 이상 사업체 ~1,500–2,000개, 출하액 10인 이상 기준 ~8–10조 원 — **반드시 KOSIS로 검증**.
- **클러스터**: 경기 북부(포천·남양주·양주·파주)·김포·인천(서구·남동)이 집적지. 2014년 기사: 포천시 가구업체 **약 500곳 = 경기북부 가구제조업체의 24.5%, 경기도의 10.9%**, 대부분 영세([경기일보](https://kyeonggi.com/article/201406240582035)); 포천 송우가구거리 2000년대 120여 업체([경기일보](https://www.kyeonggi.com/article/202005271127154)). 구인 사이트 프로필상 포천 가산면 목재가구 업체는 직원 1–10명 규모가 다수([jobploy](https://www.jobploy.kr/ko/recruit/manufacturing-gyeonggi-manufacturing-assistant-152454)).
- **전형적 규모 [est.]**: 영세(5인 미만) 60%+, 5–19인 25–30%, 20–49인 5–8%, 50인 이상 <3%. 디지털 트윈 대상은 보통 **10–50인, 매출 30–300억 원**의 OEM/주문가구 공장.
- **임금 [est.]**: 생산직 월 280–350만 원(초임~중간, 2025–26년 최저임금 ≥ 월 215만 원 기준), 숙련 기술자(도장·조립 반장) 350–450만 원; 외국인(E-9) 비중 높음(영세 공장 30–60%). 한국 통계는 검색에서 확인되지 않음 → 고용노동부 고용형태별근로실태조사 "가구 제조업" 확인 필요.
- **디지털화 수준 (제1차 스마트제조혁신 실태조사, 2025.4 발표)**: 공장 보유 중소·중견 제조기업 163,273개 중 스마트공장 도입 **19.5%(중소 18.6%)**, 도입 기업의 **75.5%가 기초 수준, 99.8%가 부분 도입**; 도입 기술 **ERP 76.3%, 제어컨트롤러 16.9%, MES 14.4%**; 활용률 80% 이상(HW 90.5%, 제조데이터 89.7%, SW 83.1%); **제조AI 도입률 0.1%**, 정부 목표 10%([디지털데일리](https://www.ddaily.co.kr/page/view/2025042816294926205), [벤처스퀘어](https://www.venturesquare.net/966944), [머니투데이](https://www.mt.co.kr/economy/2025/10/24/2025102415433311872)). 가구업종은 평균보다 낮을 가능성 큼 [est.]: ERP(더존/영림원 수준) 보유 30–50%, MES 5–10%, 바코드 공정추적 <20%.

### 3.2 가구사 스마트팩토리 사례
- **한샘**: 주문→생산→설치→물류 전과정 자동화, 부품·자재 배치 최적화 SW 도입, **2010년부터 매년 약 40억 원 자동화라인 투자**, 현장 주문 입력 시 통합정보시스템으로 설계정보가 실시간 제조공정에 연계(2022 전자신문)([etnews](https://www.etnews.com/20220214000173)). 2020년 이영식 한샘 부회장이 한국가구산업협회 6대 회장([dealsite](https://dealsite.co.kr/articles/60440)); 현 이주성 회장은 "AI·데이터 기반 산업 생태계 구축"을 언급(통계 미포함).
- **현대리바트·퍼시스·에넥스·에이스침대·시몬스·일룸/까사미아·장인가구·보루네오**: 검색 예산 소진으로 2023–2026 개별 보도 확인 못 함. 일반 지식 [unverified]: 현대리바트 용인 스마트워크센터(물류·생산 통합), 에이스침대 음성·시몬스 이천의 매트리스 자동화 라인, 퍼시스 안성 공장 자동창고 등이 알려져 있으나 **출처 확인 필요**.
- **정책 동향 2026**: 산업부는 디지털트윈+AI 운영플랫폼 결합 "다크팩토리"와 기구축 3만여 스마트공장 기반 AI팩토리 확산을 추진([FA저널](https://www.fajournal.com/news/articleView.html?idxno=20550)); 삼성SDS는 2025년부터 디지털트윈이 시각화→시뮬레이션 기반 최적화·Physical AI로 진화한다고 설명([Samsung SDS](https://www.samsungsds.com/kr/insights/the-evolution-of-digital-twin.html)). **가구 업종 특화 디지털트윈 사례는 공개 기사에서 확인되지 않음** → 본 프로젝트의 차별화 포인트.

---

## 4. 2026년 정부 지원사업 (AX 컨설팅 벤더 = 공급기업 관점)

| 사업 | 주관 | 지원 내용(2026) | 한도/비율 | 기간·일정 | 출처 |
|---|---|---|---|---|---|
| **정부형 스마트공장 구축(고도화)** — 스마트제조혁신 지원사업 통합공고(중기부 공고 2025-574호) | 중기부/스마트제조혁신추진단 | 265개 과제 | **최대 2억 원, 정부 50%** | 9개월 | [솔트소프트](https://soltsoft.com/factory/factory01.html), [Polaris3D](https://polaris3d.com/blog/newsroom/2026-government-led-smartfactory/) |
| 동일수준 고도화(2회차) | 〃 | 목표수준별 총 2.5억 내 2회 지원 | 2회차 **최대 0.5억, 6개월** | | [bizcube](https://bizcube-sol.com/fund_view/15530) |
| **부처협업형** | 〃 | 150개 과제 | 2억, 50% | 9개월 | 솔트소프트 |
| **제조AI특화 스마트공장 구축** | 중기부 (공고 2026-03-19) | ① AI공장 구축: 중간1 이상 목표수준 필수 ② 데이터 수집·검증 | ① **최대 2억, 9개월, 50% 이내** ② 최대 0.5억, 6개월; 합산 2억 cap; **제조DX멘토단(기획지도/구축지도) 참여 필수**; 전남은 도·시군 각 15% 추가(지역별) | 신청 ~4/20, 평가 5–6월, 협약 7월 | [포항상의 공고](https://pohangcci.korcham.net/file/dext5uploaddata/2026/2026년도 제조AI특화 스마트공장 구축지원사업 공고_.hwp), [헤럴드](https://www.heraldk.com/article/2026041300355648023) |
| **대중소상생형(삼성 등)** | 중기부+대기업+대한상의 | 기초 = 신규 구축기업만; 목표 초과달성 기업 1회 한 최대 1.5억 | 통상 정부 30%+대기업 30%+기업 40% [est., 구조는 전년 기준] | | [coreglobal](https://coreglobal.kr/blog/지원사업/2026년-대중소상생형-삼성-스마트공장-구축지원사업-공고) |
| 구 체계 참고(2022) | | 기초 5천만, 고도화1 2억, 고도화2 4억 | | | [기업마당](https://bizinfo.go.kr/biz/biza/selectBIZA200Detail.do?policyNewsId=61235) |
| **스마트공장 수준확인** | 추진단 | 자체구축 기업 수준 인증(1~5) | 무료/소액 | 연중 | [bizinfo](https://www.bizinfo.go.kr/sii/siia/selectSIIA200Detail.do?pblancId=PBLN_000000000118006) |
| **경기도형 스마트공장 구축·컨설팅** | 경기도·경기TP·시군 | 기초공정 디지털화, 자동화설비·맞춤 솔루션, 전문가 현장지도 | **총사업비 70% 이내, 과제당 최대 5천만 원**, 7개월 | 2026 접수 3/20~3/30 마감(기사별 상이); 2025 예산 105억(+50%) | [데일리안](https://www.dailian.co.kr/news/view/1611213/), [파이낸셜뉴스](https://www.fnnews.com/news/202502180837511247) |
| **산단공 입주기업 스마트공장** | 한국산업단지공단 | 2026년 300억, 약 150개사 | | | [이투데이](https://www.etoday.co.kr/news/view/2554560) |
| **AX 원스톱 바우처** | 과기정통부/NIPA | 개발+클라우드+데이터 패키지; 260억, 20개 과제 내외; 중견·대기업 참여 가능 | **과제당 최대 13억(2년)** | 수요기업 모집 ~2026-05-07 | [엘리스](https://elice.io/ko/resources/event/ax-voucher-2026-elice-support) |
| **AI 바우처** | 〃 | 일반/AI반도체/소상공인/글로벌 4개 분과, 수요-공급 컨소시엄 | 최대 2억 | 공급기업 선정 2026.3 | [머니투데이](https://www.mt.co.kr/tech/2026/03/11/2026031108233469429) |
| 산업부 제조AI 확산센터(지역) | 산업통상(자원)부 | 예: 대구 모빌리티부품 제조AI 확산센터 2026–2029 총 245억 | | | [경북매일](https://kbmaeil.com/article/20260722500125) |

**공급기업이 되는 방법 (스마트공장 사업관리시스템 smart-factory.kr)**: 공급기업 등록(사업자·기술·실적 서류) → 등록 공급기업 수는 2022년 1,728 → 2025년 1,987 → **2026년 3월 2,510개사**; 중기부는 2023년부터 **공급기업 역량진단**(2026: '통합 역량진단' + '제조AI 개발역량 진단' 투트랙; 경영·기술·PM 기본진단 + 기술 심화)을 운영하고, 과제 평가표에 "공급기업의 사업수행 전문성 및 투입인력(개발PM) 적정성" 항목이 있음([헤럴드](https://www.heraldk.com/article/2026042119000552558), [MTN](https://news.mtn.co.kr/news-detail/2026042213013475077)). 디지털트윈/시뮬레이션 컨설팅은 (i) 제조AI특화 과제의 '기획지도' 멘토 또는 (ii) 고도화 과제에서 MES+디지털트윈 솔루션 공급기업으로 들어가는 것이 현실적 경로 [est.]. 중요: 스마트공장 사업비는 **SW·설비 구축비 중심이며 순수 컨설팅만으로는 인정 폭이 작으므로**, 디지털트윈을 "생산계획/스케줄링 모듈" 등 운영 SW로 패키징하는 것이 유리 [est.].

**법 제도**: 「산업 디지털 전환 촉진법」(2022 시행)은 「**산업 디지털 전환 및 인공지능 활용 촉진법**」으로 개칭되었고, 시행령이 2026-06-30 개정(대통령령 36467호)·**2026-07-01 시행**([nepla](https://www.nepla.ai/law/산업-디지털-전환-및-인공지능-활용-촉진법-시행령)). 추가로 「산업인공지능전환 촉진법」으로 재개칭하고 **제조AX 얼라이언스**(제조기업·산업AI 공급/수요기업·대학·연구기관), 숙련기술자 암묵지 데이터 수집·활용 지원을 담은 개정안이 발의됨(통과 여부 미확인)([칸](https://www.kharn.kr/news/article.html?no=31433)). 산업데이터 활용·보호, 선도사업 지정이 이 법의 핵심이며, 공급기업은 "산업 디지털 전환 선도사업" 참여 실적이 가점 요소.

---

## 5. 적용할 KPI·분석 기법 (수식 + 참고 URL)

| 기법 | 수식/정의 | 가구공장 적용 포인트 | 참고 |
|---|---|---|---|
| **OEE** | OEE = Availability × Performance × Quality; A = Run time / Planned time; P = (Ideal CT × Total count) / Run time; Q = Good / Total | 엣지밴더·CNC에 우선 적용. 중소 가구공장 OEE **35–55%** 수준이 흔함 [est.]; 세계 수준 85% | https://www.oee.com/calculating-oee/ |
| **Takt vs Cycle time** | Takt = 가용 생산시간 / 고객 수요량; 각 스테이션 CT ≤ Takt 여야 함 | 예: 8h×60=480분, 일 수요 수납장 100대 → takt 4.8분/대 → 엣지밴더가 부품 기준 대당 6부품×60초=6분 > takt → 병목 | https://www.lean.org/lexicon-terms/takt-time/ |
| **Little's Law** | WIP = Throughput × Lead time (L = λW) | 현장 WIP(대차 수×대차당 부품수)와 일 처리량으로 리드타임 역산; 모델 검증(validation)의 첫 체크 | https://en.wikipedia.org/wiki/Little%27s_law |
| **VSM** | 공정별 C/T, C/O, 가동률, 재고일수, 정보흐름; PCE = VA time / Lead time | 가구 VSM 전형: VA 2–4시간 vs 리드타임 5–15일 → PCE 1–3% [est.]; MDPI VSM+TOC+Arena 논문이 템플릿 | https://www.lean.org/store/book/learning-to-see/ ; [MDPI Processes 2019](https://doi.org/10.3390/pr7110816) |
| **Spaghetti diagram** | 1오더/1대차의 실제 이동경로·거리 기록 | 판재→쏘→밴더→보링→조립 왕복 경로; 3D 트윈의 경로 데이터로 직결 | https://www.isixsigma.com/dictionary/spaghetti-diagram/ |
| **SLP (Muther)** | 활동관계도(A/E/I/O/U/X) → 관계 다이어그램 → 공간 요구 → 블록 레이아웃 | 집진 배관·공압 배관·도장부스 위치가 X(격리) 제약 | https://en.wikipedia.org/wiki/Systematic_layout_planning |
| **CRAFT / BLOCPLAN** | 목적함수 min Σ f_ij·c_ij·d_ij (흐름×비용×거리), 쌍 교환 개선 | from-to 차트를 DES 출력으로 생성 → 레이아웃 후보 비교 | https://www.sciencedirect.com/topics/engineering/computerized-relative-allocation-of-facilities-technique |
| **Line balancing** | 효율 = Σ task time / (N × CT); 최소 스테이션 수 = ⌈Σt / Takt⌉ | 조립·포장 라인; FlexSim 가구 사례 밸런스율 +46.71% | https://en.wikipedia.org/wiki/Assembly_line#Line_balancing |
| **TOC / DBR** | Drum = 병목 스케줄, Buffer = 병목 앞 시간버퍼, Rope = 투입 통제 | 엣지밴더를 드럼으로: 재단 투입을 밴더 능력에 묶기(과잉 재단 금지) | https://www.tocinstitute.org/drum-buffer-rope.html |
| **M/M/1 큐잉** | ρ = λ/μ; L = ρ/(1−ρ); Lq = ρ²/(1−ρ); W = 1/(μ−λ); Wq = ρ/(μ−λ) | 가동률 80%→Lq 3.2, 90%→8.1: 밴더 가동률이 85% 넘으면 대기 폭증 → 2호기/리턴컨베이어 효과 정량화 | https://en.wikipedia.org/wiki/M/M/1_queue |
| **M/G/1 (Pollaczek–Khinchine)** | Lq = (λ²σ² + ρ²) / (2(1−ρ)) | 셋업 포함 서비스시간 분산이 큰 보링기·도장 | https://en.wikipedia.org/wiki/Pollaczek%E2%80%93Khinchine_formula |
| **Kingman (VUT)** | Wq ≈ (ρ/(1−ρ)) × ((ca²+cs²)/2) × τ | 배치 크기↓ → 도착 변동 ca² 변화 평가 | https://en.wikipedia.org/wiki/Kingman%27s_formula |
| **시뮬레이션 what-if** | 복제수 ≥10, 워밍업 제거, 95% CI | 시나리오: ① 엣지밴더 2호기 ② 배치 크기(색상 배치 vs 오더 배치) ③ 오더 시퀀싱(색상 그룹핑으로 셋업 최소화 vs 납기순) ④ 교차훈련(작업자 스킬 풀) ⑤ 리턴컨베이어 ⑥ 집진 VFD | FlexSim/AnyLogic/SimPy 문서 |

---

## 6. 공개된 가구공장 시뮬레이션 모델과 추출 수치

| 연구 | 도구 | 모델 내용 | 추출 가능한 수치/결과 |
|---|---|---|---|
| Hybrid VSM + TOC + Simulation, wooden furniture (Processes 2019, 7(11):816) | **Arena 14.7** | 목재가구 공장 전체 DES; 가동률·대기시간·시나리오 기반 병목 탐지 | 병목 탐지 3방법(utilization, waiting time, scenario) 비교 — **가장 좋은 템플릿**; 전문 미열람([MDPI](https://doi.org/10.3390/pr7110816)) |
| Optimization of a furniture factory layout (슬로베니아) | **AnyLogic** | 오픈 오더에서 모델 자동생성 | 기계 재배치는 총 제조시간에 미미 → 설비 추가 필요([academia](https://www.academia.edu/48165884/Optimization_of_a_furniture_factory_layout)) |
| Company A 목재가구 판재 라인 | **FlexSim** | 공정: 목재 밀링→오일 밀링→프라이머→오일 밀링→탑코트→가공센터→분류→검사→포장; 스톱워치 시간연구 | **라인 밸런스율 +46.71%**([ResearchGate](https://www.researchgate.net/publication/387879413_Optimization_and_Simulation_of_Production_Lines_Based_on_Flexsim)) |
| Optimal worker allocation, wooden furniture (JETAP) | Simulation + DEA | 4개 공정 작업자 배치 | 작업자 **109→103명**, 4공정 평균 대기 **191.17→189.77분**([JETAP](https://journals.mmupress.com/index.php/jetap/article/view/3267)) |
| Utilization of computer simulation… furniture production (BioResources) | **Tecnomatix Plant Simulation** | 목재가구 라인, 조립 병목 | 총 생산시간 **34.25h → 12.02h**, CNC 작업장 추가로 조립 병목 해소([BioResources](https://bioresources.cnr.ncsu.edu/resources/utilization-of-computer-simulation-for-optimization-of-furniture-production-system/)) |
| Mixed assembly line of wooden furniture (Procedia Manufacturing 2020) | **Arena + Taguchi** | 혼류 조립 라인 리드타임·플로우타임 | 실험계획으로 요인 효과 추정([ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2351978920304649)) |
| Headboard assembly workstation, AX Furniture (Muar, 말레이시아) | **Arena** | 조립 워크스테이션 CT | 인터뷰·관찰·Arena로 CT 산정([IEOM](http://www.ieomsociety.org/ieomuk/papers/26.pdf)) |
| Productivity enhancement by work procedures & plant layout (태국 목재가구) | Arena | 레이아웃 변경 | 평균 작업시간 **260→245분**([academia](https://www.academia.edu/9985967/Productivity_Enhancement_in_a_Wood_Furniture_Manufacturing_Factory_by_Improving_Work_Procedures_and_Plant_Layout)) |
| DES + Lean, wooden sector (팔레트 조립, 스페인어) | Arena, DMAIC | 조립시간 | **25±2 → 19±1분**([ResearchGate](https://www.researchgate.net/publication/343780358_Discrete_Event_Simulation_Applying_Lean_methodologies_Case_study_Wooden_Sector)) |
| VSM + simulation lean, furniture industry | VSM+DES | 리드타임·WIP | 전문 미열람([academia](https://www.academia.edu/77546434/)) |
| FlexSim case-based study (일반 제조) | FlexSim | 작업자별 idle/processing/waiting | 평균 대기 **−29.5%**, 총 생산시간 **−31.7%**([MDPI Eng Proc](https://www.mdpi.com/2673-4591/128/1/9)) |
| Mattress line, TOC (PMC) | TOC 동적 병목 제거 | 매트리스 라인 | 장식가구 참고([PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4977234/)) |

### 6.1 DES 초기 기본값 제안 (판재가구, 10–30인 공장) — 전부 [est.], 방문 후 교체
- **오더 도착**: 일 15–40 오더(주문가구) 또는 주간 생산계획 배치 투입; 오더당 부품 20–80개(평균 40), 부품 규격 Triangular(300, 600, 2400) mm 길이, 두께 18 mm 90%.
- **재단(런닝쏘)**: 시트당 Triangular(1.5, 2.5, 4.0)분, 시트당 부품 Uniform(10, 25); 패턴 셋업 1–3분; 가동률 목표 60%.
- **네스팅 CNC**: 시트당 Triangular(8, 12, 20)분(핸들링 포함); 60–100 시트/시프트.
- **엣지밴딩**: 변당 = 길이/이송속도(12 m/min) + 1.5초 간격; 부품당 핸들링·회전 Triangular(15, 25, 45)초; 테이프 교체 Triangular(2, 4, 8)분(색상 변경 시), 접착제 교체 30분(주 1회); MTBF 8h / MTTR 20분; **가동률 85–95%(병목)**.
- **CNC 보링**: 부품당 Triangular(20, 35, 60)초; 다축 보링기 셋업 Triangular(10, 20, 30)분 per 품목.
- **하드웨어/조립**: 수납장 대당 Triangular(10, 18, 30)분, 작업자 풀 3–6명.
- **도장(해당 시)**: 도장 Triangular(1, 2, 4)분/면, 건조 고정 8–12h(배치 건조실 용량 40–80 도어).
- **포장**: Triangular(3, 5, 8)분/대.
- **운반**: 대차 용량 30–60 부품, 이동속도 1 m/s, 지게차 1대 공유.
- **근무**: 1교대 8h(+잔업 1–2h), 주 5–5.5일, 가용률 90%.
- **전력 상태 모델**: 각 설비 idle 10–20% / run 100% of nameplate; 집진기 30 kW·컴프레서 22 kW 상시.
- 검증 목표: Little's law(현장 WIP ≈ 2–5일분), 엣지밴더 가동률, 일 출하량 ±10% 일치.

### 6.2 공장 방문 시 수집 리스트
1. 설비 명판 사진(kW, 이송 m/min, 연식), 집진기·컴프레서 용량(HP)과 계약전력, 전기요금 고지서(월 kWh).
2. 1주일 작업지시서·출하 기록(오더 수, 부품 수, 품목 믹스) → 도착 분포 적합.
3. 스톱워치 시간연구: 엣지밴더 부품 10개, 보링 10개, 조립 3대, 포장 3대(최소값·최빈값·최대값 → Triangular).
4. 셋업 관찰: 테이프 교체, 보링 핀 재배치, 도장 색 교체.
5. WIP 스냅샷(대차 수·위치) 2회/일, 스파게티 경로(대차 1개 추적), 도면/평면도(CAD·면적).
6. 정보흐름: ERP/바코드/엑셀 여부, 작업지시 전달 방식, 품질불량(엣지 박리, 치수) 비율.
7. 근무·인원: 공정별 인원, 교차훈련 가능 여부, 외국인 비율, 잔업 패턴.

---

### 핵심 출처 요약
- 엣지밴더·쏘 제원: [exapro Jade 340](https://www.exapro.com/biesse-jade-340-p260724122/), [exapro Akron 1440](https://www.exapro.com/sp/biesse-akron1440-54203/), [exapro Homag KAL 210](https://www.exapro.com/homag-optimat-kal2106a20s2-p260803095), [exapro SAWTEQ B-300](https://www.exapro.com/homag-sawteq-b-300-profiline-panel-saw-p260713249/), [exapro Selco WNTR 600](https://www.exapro.com/biesse-selco-wntr-600-p260918105/), [Homag EDGETEQ S-300 brochure](https://www.homag.com/fileadmin/product/edge/brochures/edgeteq-s-300/Edge-banding-machines-edgeteq-s-300-en.pdf)
- 네스팅 사이클: [woodweb Minutes per Sheet](https://woodweb.com/knowledge_base/CNC_Routing_Minutes_per_Sheet.html), [woodweb Nested Base Output](https://woodweb.com/knowledge_base/Nested_Base_Output__Nested_Base_Router_Workflow_an.html), [mfgrobots ROI](https://www.mfgrobots.com/Article/equipment/cnc/52182.html)
- 에너지: [Energy Trust Oregon](https://blog.energytrust.org/?p=2957), [ACEEE 2005](https://www.aceee.org/files/proceedings/2005/data/papers/SS05_Panel01_Paper11.pdf), [Nederman](https://nederman.com/contacts/se/magnus-andreasson), [Energies 2022 review](https://ideas.repec.org/a/gam/jeners/v15y2022i3p916-d735469.html)
- 한국 통계·정책: [디지털데일리 실태조사](https://www.ddaily.co.kr/page/view/2025042816294926205), [헤럴드 역량진단](https://www.heraldk.com/article/2026042119000552558), [소트소프트 2026 현황](https://soltsoft.com/factory/factory01.html), [데일리안 경기도형](https://www.dailian.co.kr/news/view/1611213/), [nepla 시행령](https://www.nepla.ai/law/산업-디지털-전환-및-인공지능-활용-촉진법-시행령), [kharn 개정안](https://www.kharn.kr/news/article.html?no=31433), [etnews 한샘](https://www.etnews.com/20220214000173), [경기일보 포천](https://kyeonggi.com/article/201406240582035), [IMARC](https://www.imarcgroup.com/report/ko/south-korea-furniture-market)

**후속 검색 권장 항목(예산 소진으로 미완)**: KOSIS C32 사업체·종사자·출하액(2023), 가구제조업 임금(고용형태별근로실태조사), 국산 목공기계(신우·대성·양지·우성) 제원, 현대리바트/에이스침대/퍼시스/시몬스 자동화 보도(2023–2026), 2026 통합공고 원문(기초단계 한도), 과기정통부 디지털트윈 실증 공고, 산업부 AI 자율제조 선도프로젝트 2026, 엣지밴더 체인지오버 SMED 사례, UV/스프레이 라인 전력.