# 4차 리서치 반영분 리뷰 (커밋 05cd66f · 782132c · 3024b68)

리뷰 방식: 저장소를 `/tmp/claude-0/-home-user-claude-mem/508c8abb-4a55-5c43-94f1-9a63dde73d06/scratchpad/review3/repo` 에 복사해 `test_chain.sh` 와 각 도구를 **실행**했고(표기 [실행]), 실행으로 못 본 것은 코드 읽기로 판단했다(표기 [읽기]). 저장소 파일은 수정하지 않았다. 스크래치 산출물: `review3/tv_L0.md`, `tv_L1.md`, `diag_trace.py`, `sim_test.py`, `states.csv`, `gaps.json`, 드리프트·규칙 합성 CSV. 리뷰 도중 HEAD 가 2개 더 올라갔고(782132c 문서, 3024b68 rule_fit GROUP) 그것까지 포함했다.

## 0. 실행 결과 요약

| 실행 | 결과 |
|---|---|
| `bash tools/test_chain.sh` | 종료 0, 1.7초. 변환기 회귀 "전부 통과". **그러나 체인은 새 도구 결과를 판정하지 않는다**(grep 출력만; F-13) |
| `events_to_worklog` baseline → `trace_validate` L0 (`data/sample_factory.json`, 3 seed) | 267배치·1539단계, 3.7초. 16곳 중 12 통과(ASM2 +10.1, ASM3·ASM4 운반 +13/+18, CUT2 −47.1 실패). **전 스테이션 부호검정 p=0.00, 부호 일치율 5~38%** → 올바른 구조인데 '체계적 오차' |
| 같은 자료 `--level L1` | n 이 절반~1/6(ASM1 132→21)로 줄고 누락 건수는 표시 안 됨. CUT2 −111.5(ρ=−1.62) → 올바른 구조가 L1 에서 **기각** |
| 결함 주입(EB2·ASM4~6 삭제, CUT2 버퍼 1) L0 | CUT2 −185(1%)·EB1 +158(98%)·CUT1 −95 → 03 §8-1 "−183·+151·−91" 과 일치(seed 차이) |
| `rule_fit` baseline / s7_edd / s6 (`--factory`) | FIFO 100%(EDD 98%, 판별 FIFO:EDD 3건) / EDD 100%(판별 6건) / FIFO 99%·GROUP 95%. 판별 결정 <10 인데도 "규칙층 복제 가능" |
| `hourly_profile --cycle --factory` baseline | 0.94~1.05(폭 0.11) → 생략. `--factory` 없이 0.53~1.15(경고 후 반영 판정). **카운터 모드(events.jsonl)는 리듬 없는 같은 시뮬에서 0.84~1.25(폭 0.41) → "넣는다"** |
| `idle_gaps` 합성 states.csv(KST 08:10~17:20, 1/5/30분 공백, UTC epoch) | 근무창 08:10/17:21, 3봉 229/67/34, run CV 0.03 → 정확. `--tz` 처리 정확. 점심 60분이 "≥10분" 5건에 섞임 |
| `drift_check` 합성 잔차 200 seed | 드리프트 없음 26주: **재보정 오경보 9.5%**, 주의 32%. +2σ 계단: 97% 검출. 기준 8주에 이미 있는 상수 편향: 탐지 불가(설계상) |
| 시뮬 단위 테스트(`sim_test.py`) | 결근 OK(단 토요일 결근도 540분 down 적산), **고장 종료가 결근을 해제**(3360 결근 → 3366 idle), **트레이스 240분이 점심을 통과**(656→897.8), **트레이스+hourly_factor 이중 적용**(ASM1 40→80분), `order_min` 비단조 시 클램프(100→900) |

## 1. 검증된 발견 (상=결론을 바꿈 / 중=수치 왜곡 / 하=경미)

| # | 위치 | 심각도 | 증거 | 수정 |
|---|---|---|---|---|
| F-1 | `tools/templates_to_json.py:122-125` | **상** [실행] | 시트 17 블록을 끼워 넣으며 `if st["id"] in ws_loss:` 가 `if st["id"] == r["기계ID"]:` 와 같은 들여쓰기가 됐고, 그 아래 `for col, key in [...]`(이송속도·간격·통과 횟수·이동 등급·이전 비용·capability·setup_trigger·PLC·공압) 가 **그 if 안으로 들어갔다**. 결과: 시트 2 추가 열이 어느 스테이션에도 안 읽힌다 — 커밋 전 `sample_from_template.json` 에 20건 있던 `feed_mpm/move_class/…` 가 커밋 후 **0건**(EB1 `feed_mpm 12`, `move_class B` 소실, 커밋된 JSON 자체가 퇴행). 워크샘플링 ≥30회 스테이션이 생기면 (a) 시트 2 **모든 행**의 값이 그 스테이션에 덮어쓰이고 (b) `availability *= (1−loss)` 가 시트 2 행 수(18)만큼 **반복 곱**돼 하한 0.4 로 떨어진다. `test_converter` 는 `feed_mpm` 을 검사하지 않아 통과 | P-1 |
| F-2 | `sim/factory_sim.py:443-445, 494-505` | **상** [실행] | 트레이스 가공시간을 `work_unit(st, 전체 분)` 한 번에 흘린다. `work_unit` 은 시작 시 `shift.wait()` 만 하고 중간 휴게·야간을 건너뛰지 않으므로 **관측 '근무 분' 240 이 달력 242분으로 끝남**(11:00 착수 → 점심 통과). 라운드트립에서 1537단계 중 966단계의 근무분 길이가 관측과 1분 이상 다르고 평균 −11.9분; 모델 단계 종료 272건이 비근무 시각(관측은 102). L0 전 스테이션 "모델이 덜 기다림(p=0.00)" 편향의 주 원인 | P-2 |
| F-3 | `sim/factory_sim.py:502` | 중 [실행] | `operator_paced` 면 트레이스 시간도 `/factor` → 관측값(이미 리듬 포함)을 **이중 보정**. ASM1 트레이스 40분 → 80분 | `work_unit(st, minutes, traced=False)`; traced 면 factor 생략 |
| F-4 | `tools/trace_validate.py:89-91, 103` | 중 [실행] | 부호검정이 **동점(잔차 0)을 '음'으로 센다**. DRY1(대기 0 vs 0, 잔차 +0.0)이 일치율 0%·p=0.00. 대기 0 과잉 자료(연구 18 §4 가 명시)에서 반드시 오판 | P-3 |
| F-5 | `tools/trace_validate.py:54, 69-74` | 중 [실행] | L1 에서 모델이 다른 병렬기를 고르면 그 단계는 `missing` 으로 버려지고, **rows 가 하나라도 있으면 누락 수를 표시하지 않는다**. ASM1 n 132→21, CUT2 318→134 — 남은 n 은 '모델이 관측과 같은 기계를 고른 배치'만이라 **선택 편향**. `continue` 가 `prev_obs_end/prev_mod_end` 갱신을 건너뛰어 다음 단계 '운반+전대기'가 상류 전체를 포함(L1 BOR1 관측 170분 vs L0 3.4분) | P-4 |
| F-6 | `tools/trace_validate.py:46` + 연구 18 §2.2 | 중 [실행] | 연구 18 의 L0 는 "고장 구간·출근 캘린더까지 강제해 **추적표를 그대로 복제**"인데 코드 L0 는 고장·셋업·스크랩 재작업을 여전히 표본추출(docstring 도 인정). 올바른 구조의 L0 에서 CUT2 −47분이 남고 03 §8-1 "L0 → 남는 차이를 먼저 0 으로" 는 달성 불가 | L0 에 고장 비활성 옵션(`meta.trace_no_breakdown`) + 시트 13 '셋업 발생' 열 강제 |
| F-7 | `tools/rule_fit.py:54-56` | 중 [실행] | capacity>1 또는 두 슬롯이 같은 시각에 착수하면 두 번째 배치 후보에 첫 번째가 남는다(`c["start"] >= s["start"]`). 합성 2슬롯 EDD 공장에서 EDD 재현율 83%(6 중 1 미스). 조립 벤치·DRY(cap 3)에서 **참 규칙도 감점** | P-5 |
| F-8 | `tools/rule_fit.py:80-83` | 중 [실행] | 판정이 **판별 결정 수를 쓰지 않는다**. s7_edd: EDD 100% 이지만 EDD vs FIFO 판별 6건 → 도구 자신이 "10건 미만이면 구분 안 됨"이라 쓰면서 "규칙층 복제 가능: EDD". best∈{FIFO,EDD} 면 lift 면제 — 연구 19 §4(최선 단순 기준선 대비 lift ≥0.15 **AND**)와 다름. McNemar 미구현 | P-5 |
| F-9 | `tools/drift_check.py:21, 39-40` | 중 [실행] | 8주 `pstdev`(n=8, 하향 편향) + h=4σ + "최근 4주 평균 ≥1σ"(4주 평균 SE=σ/2 → 2SE) 조합이 **드리프트 없는 26주에서 재보정 9.5%, 주의 32%**. docstring "이 조건이 오경보를 거른다" 는 과장 | P-6 |
| F-10 | `sim/factory_sim.py:80-89, 95-106` | 중 [실행] | 결근 중 고장이 나면 고장 종료 `self.down=False` 가 **결근을 해제**(상태 로그 3360 down → 3366 idle). 반대로 결근 종료가 진행 중 고장을 해제. `down_min` 중복 적산. 비근무일(토) 결근도 540분 down | P-8 |
| F-11 | `tools/hourly_profile.py` 카운터 모드 | 중 [실행] | 리듬 없는 시뮬 events.jsonl 에서 폭 0.41 → "hourly_factor 에 넣는다" + JSON 출력. 03 §2.5 는 "완료 건수 기반은 쓰지 않는다"고 했는데 도구 기본 모드가 그것 | P-9 |
| F-12 | `tools/templates_to_json.py:70-103, 89` | 중 [읽기+실행] | PF&D ×1.09 가 **엣지밴더에는 적용 안 됨**(물리항 분기가 `continue` 로 빠짐 — EB1/EB2 `source/pfd` 없음), 반면 CNC 재단·보링 같은 기계 페이스 공정은 **기계 시간 항까지** ×1.09. 연구 20 §3.3 은 "기계 결정 항 금지, 핸들링만" | 기계항(`edges_m`, 보링 기계 비중) 제외하고 `base_min`(핸들링)만 ×(1+PFD); 엣지 분기 γ0·γ1 에도 적용 |
| F-13 | `tools/test_chain.sh:12-14` | 중 [실행] | 새 도구 3개는 grep 출력만 하고 **판정하지 않는다**. `grep -c "통과"` 는 각주 "…외 통과" 줄까지 세어 **6**(실제 통과 5: ASM6·BOR1·BOR2·DRY1·FIN1). from_template rule_fit 은 결정 1건(검증 아님) | P-7 |
| F-14 | `sim/factory_sim.py:178-181` | 하 [실행] | list 모드가 `order_min` 순이 아니라 목록 순으로 대기 → 비단조면 클램프(100→900). `trace_validate` 는 release 순 정렬이라 order<release 배치의 외주 발주 시계가 밀림 | `sorted(o["list"], key=order_min)` 후 배치 id 를 list 에 넣어 매칭 |
| F-15 | `tools/trace_validate.py:54` + `merged_cut_flow` | 하 [읽기] | 모델↔관측 배치를 **인덱스**로 매칭. `cut_key=color_thickness` 공장은 재단이 `merged_cut_flow` 로 가고 `cb` 에 `trace` 가 없어 **재단 가공시간이 고정되지 않으며**, 관측 'C…' 배치는 제품 ID 없음으로 제외 → 재단 스테이션이 표에서 사라짐(S6 류 공장 구조 검증 불가) | `merged_cut_flow` 에 그룹 trace 합산 전달; 'C' 배치를 구성 주문에 분배 |
| F-16 | `tools/idle_gaps.py:34` | 하 [실행] | 점심·참을 모른 채 ≥10분 공백으로 집계(60분 5건 포함) → long_per_hour 과대 | `--factory` 로 달력 블록 겹침 제외 |
| F-17 | `tools/hourly_profile.py:29,40,43` | 하 [실행] | `d>300` 제외로 재단(수시간) 단계 전부 제외(미표기). 시각별 비율에 SE 가 없어 2주 현장 자료(시각당 20~50단계)면 잡음만으로 폭 0.2 를 넘길 수 있음 | P-9 |
| F-18 | `schema/factory.schema.json` | 하 [실행] | `orders.list` 항목이 `{"type":"object"}` 뿐 — `release_at`·`order_min`·`trace` 미정의. 09 의 `meta.validation_report`, 시나리오 `base_version`, 스코어카드 "측정 시점 경과(개월)" 열은 스키마·`data_quality.py`·시나리오 어디에도 없음(grep 0) | list 항목 정의; 09 세 항목 "예정" 표기 |
| F-19 | `tools/trace_validate.py:14-18` 성능 | 하 [실행] | 분 단위 파이썬 루프지만 40일·1539단계·3 seed 3.7초 → 문제 없음 | — |

## 2. 문서 간 불일치

1. **규칙 합격 기준이 세 가지**: 코드·연구 19 = "≥0.75 ∧ Wilson 하한 ≥0.60 ∧ lift ≥0.15" / 03 §8-4 = "재현율 ≥70%, 95% 하한 ≥ RANDOM+25%p" / 코드는 FIFO·EDD 에 lift 면제. 03 §8-4 를 연구 19 기준으로 통일.
2. **구조 검증 '통과' 수가 세 가지**: `trace_validate.py` 각주 "16개 중 CUT2·ASM2 외 통과(14)" / 03 §8-1 "16개 중 6개 통과·나머지 10분 내외" / 재실행 3 seed 12개·1 seed 14개. 03 의 '6' 은 from_template 체인 `grep -c` 오집계(각주 포함)이고 from_template 은 14 스테이션.
3. **부호 기준**: 03 §8-1 "부호 일치율 ≤20% 또는 ≥80% 는 체계적 오차" vs 코드는 p 만 출력하고 판정에 미사용. 문장대로면 올바른 구조 L0 에서 16곳 중 10곳이 '체계적 오차'(F-2·F-4 결과) — 문장·코드·실험이 서로 안 맞음.
4. **L0 정의**: 연구 18 §2.2(고장·캘린더 강제) ≠ 코드(고장·셋업 표본추출). 03 §8-1 은 연구 18 쪽 문장.
5. **드리프트 판정**: 09 §2 "동시 경보 또는 2개월 연속 이탈 → 재보정" 에 코드의 **"∧ 최근 4주 평균 ≥1σ"** 가 빠짐. 연구 21 §2-2 h=4~5σ, 코드·09 는 4σ 고정(근거 미기재).
6. **시간대 능률 산출 모드**: 03 §2.5 "완료 건수 기반은 쓰지 않는다" vs `hourly_profile.py` 기본 모드·docstring·연구 20 §1.4(카운터 교차검증 권장).
7. **현장 사진 시각**: 03 §2.6·01·07 = "08:00·15:30", 05 = 15:15 행. 그리고 **03 §5(01 이 '기준'이라 선언한 시간표)** 에는 화이트보드 사진·"앞으로 2주 한가한가"·반장① '순서 다시 짜기'·② '절대 안 하는 것' 이 **미반영**(§5 반장② 는 여전히 "기계 선택·셋업 시점·운반 트리거·급한 주문"). 01/05/07·§2.6 은 새 순서, §5 는 옛 순서.
8. **PF&D 수치**: 코드·03 §2.5·05 = 9%(5+4) / 연구 20 §1 표 = "PF&D 10–15%". 03 에 Niebel 5+4 채택 근거 한 줄 필요.
9. **워크샘플링 표본**: 03 §2.3 "271회(90%, ±5%)" 와 §2.5·08 "≥30회면 반영" 이 같은 표 → "30회 이상 반영, ±5% 정밀도는 271회" 로.
10. **시트 13 → 도구 입력 경로 부재**: 08·03 §8-1 은 "시트 13(또는 2주 양식)이 trace_validate/rule_fit 입력" 이라 하지만 worklog.csv 를 만드는 코드는 `events_to_worklog.py`(시뮬 이벤트)뿐. 시트 13 은 시계 시각·'출발 시각'·'셋업 발생'·'함께 처리한 배치' 열이고 도구는 Day0 기준 분·`n_parts` 를 요구. 변환기 없이는 현장 자료로 못 돌린다.
11. **08 "출근부 → meta.absences"**, 03 §13 "구현(`meta.absences`)": 시뮬은 읽지만 **템플릿 시트도 변환기 경로도 없음**(시트 6 결근 열 없음). `hourly_factor`·`paced` 도 손편집 JSON 만 가능.
12. **00 §2 표** "트레이스 구동 L0/L1 구조 잔차": F-2/F-5/F-6 때문에 L1 은 자기 라운드트립도 통과 못 함.
13. **09 §3 "학습곡선 모드(사이클 ×1.2→1.0)"** 는 03 §13 "미구현(v1)" — 09 는 운영 절차처럼 서술.

## 3. 과잉 주장 (코드가 실제로 하는 것 대비)

- **"L1 로 구조 검증"**: L1 자기 라운드트립에서 올바른 구조가 CUT2 ρ=−1.62 로 기각되고 n 절반이 조용히 버려진다. 현재 L1 은 "병렬기 선택이 관측과 같은 배치 부분집합에 대한 검증".
- **"L0 로 코드 버그·미기록 사건만 남긴다"**: 고장·셋업·스크랩 표본추출 + F-2 휴게 통과 버그 → L0 자체가 체계적 편향을 만든다.
- **"묶음 구성은 시트 13 '함께 처리한 배치' 열 + cut_batching 으로 검증"**: 그 열을 읽는 코드가 없다(제안 단계).
- **"EDD 공장 → EDD 100%(판별 6/6)"** 를 자체 검증 성공으로 인용: 도구 자기 기준(판별 ≥10)으로는 "구분 안 됨" → 식별 불가 사례로 적어야 정직.
- **drift_check "오경보를 거른다"**: 실측 9.5%/26주.
- **시트 17 → 유효 가용률 "중복 없음"**(코드 주석): F-1 로 실제는 18배 중복 곱. 시트 2 소정지와 워크샘플링 '대기' 가 같은 손실을 두 번 셀 수 있음.
- **"CT 실측 교체 시 여유율 제거"**: `log_to_model.py` 가 `source/pfd` 를 읽거나 지우지 않음(grep 0).
- **hourly_profile "리듬이 없으면 1.0 평탄"**: `--cycle --factory` 에서만 참.
- 03 §8-1 "근무 분 환산은 도구가 한다": 도구는 분 숫자를 받아 근무 분으로 바꿀 뿐, HH:MM·날짜 → 분 변환은 없음.

## 4. 우선순위 수정 10개

**P-1 (F-1) 변환기 들여쓰기 복구** — `templates_to_json.py:117-125`
```python
    for r in rows(wb["2_기계대장"]):
        for st in f["stations"]:
            if st["id"] != r["기계ID"]: continue
            micro = ...; warm = ...
            st["availability"] = round(max(0.5, 1 - micro * 2 / 60 - warm / 450), 3)
            for col, key in [...]:            # 원래 자리로 복귀
                if r.get(col) not in (None, ""): st[key] = r.get(col)
    for st in f["stations"]:                   # 워크샘플링은 시트 2 루프 밖에서 한 번만
        if st["id"] in ws_loss:
            st["availability"] = round(max(0.4, st.get("availability", 1.0) * (1 - ws_loss[st["id"]])), 3)
            st["availability_source"] = f"워크샘플링 손실 {ws_loss[st['id']]:.0%}"
```
`test_converter.py` 에 `check("EB1 feed_mpm", st["EB1"].get("feed_mpm") == 12, ...)`, `check("ASM1 PF&D", st["ASM1"]["cycle"].get("pfd") == 0.09, ...)` 추가. 커밋된 `data/sample_from_template.json` 재생성.

**P-2 (F-2, F-3) 트레이스 가공을 근무 분 단위로 분할** — `factory_sim.py:445`
```python
if tr_key is not None:
    left = float(batch["trace"][tr_key])
    while left > 0:                      # 휴게·야간·고장에서 끊기도록 5분 단위
        step = min(left, 5.0)
        yield from self.work_unit(st, step, traced=True); left -= step
```
`work_unit(self, st, minutes, traced=False)` 에서 `if st.operator_paced and not traced:`. 수정 후 `diag_trace.py` 의 "model work dur − obs work dur" 가 0 근처, 부호 일치율 40~60% 가 돼야 한다.

**P-3 (F-4) 부호검정 동점 제외** — `trace_validate.py:103`
```python
npos = sum(1 for r in rows if r[1] > r[0] + 0.5); nneg = sum(1 for r in rows if r[1] < r[0] - 0.5)
pos = npos / max(1, npos + nneg); pval = sign_p(npos, npos + nneg) if npos + nneg else 1.0
```
표에 "동점 n" 열 추가. 03 §8-1 "≤20%/≥80%" 문장은 "동점 제외 부호검정 p<0.05" 로 교체.

**P-4 (F-5) L1 매칭·누락 보고** — `trace_validate.py:69-74`
```python
m = next((x for x in ms if proc_of[x["station"]] == proc_of[s["station"]]), None)
if m is None: d["missing"] += 1; prev_obs_end = s["end"]; continue
if m["station"] != s["station"]: d["other_machine"] += 1
```
열에 `누락/다른 기계` 항상 출력, 대기 잔차는 공정 단위로 집계. "라우팅 오류" 는 L0 에서만, L1 은 "병렬기 선택 규칙 차이 x%".

**P-5 (F-7, F-8) rule_fit 결정 복원·판정**
```python
same_t = [c for c in ss if abs(c["start"] - s["start"]) < 1e-6]        # 동시 착수 집합(다슬롯)
cands = [c for c in ss if c["arrive"] <= now + 1e-9 and c["start"] > s["start"] + 1e-9] + same_t
hit = s["batch"] in ties or any(c["batch"] in ties for c in same_t)
```
판정: `second = sorted(rates, key=rates.get)[-2]; nd = (disc.get((best,second)) or disc.get((second,best)) or [0,0,0])[2]`; `nd < 10` 이면 "복제 가능(단 {best}≈{second}: 판별 {nd}건 — 트윈에는 어느 쪽이든 동일)". lift 는 best 가 FIFO/EDD 여도 차순위 단순규칙 대비로 표시. 03 §8-4 "≥70%, RANDOM+25%p" 를 코드 기준으로 교체.

**P-6 (F-9) drift_check 오경보**
```python
sigma = statistics.stdev(base)             # n−1
practical = abs(m4 - mu0) >= 1.5 * sigma   # 4주 평균 SE = σ/2 → 3SE
```
docstring·09 §2 에 "기준 8주 σ 과소추정 → 보정 후 12주까지는 '주의'만, 재보정은 두 조건 + 실질 1.5σ" 통일, 09 에 오경보율(합성 26주 ≈10% → 수정 후 값) 명기.

**P-7 (F-13) test_chain 에 판정 추가**
```bash
python3 tools/trace_validate.py ... --out sim/out/from_template/trace_validate.md >/dev/null
PASS=$(grep -c "| 통과 |" sim/out/from_template/trace_validate.md); echo "구조 검증 통과: $PASS"; [ "$PASS" -ge 4 ] || exit 1
python3 tools/events_to_worklog.py sim/out/baseline/events.jsonl /tmp/wl.csv /tmp/rel.csv >/dev/null
python3 tools/rule_fit.py /tmp/wl.csv --releases /tmp/rel.csv | grep -q "복제 가능: FIFO" || exit 1
# s7_edd 변환 후 "EDD" 확인 동일
```
from_template(결정 1건) 대신 baseline(226건)·s7_edd 로 규칙 도구를 검증.

**P-8 (F-10) 결근·고장 상태 분리** — `Station`: `self.down_reasons=set()`, `down` 은 `bool(self.down_reasons)` property; `absent_days` 는 `add/discard("absent")`, `breakdowns` 는 `add/discard("fault")`; 결근은 `if not self.sim.shift.is_workday(d): continue`.

**P-9 (F-11, F-17) hourly_profile** — 카운터 모드 JSON 키를 `"count_profile"` 로, `hourly_factor` 는 `--cycle` 에서만; `--cycle` 표에 `n`·`SE` 열, `spread >= 0.2 and spread > 2*max(SE)` 일 때만 "반영". 03 §2.5·02 문구와 일치.

**P-10 (불일치 2·7·10·11) 문서**
- 03 §8-1: "올바른 구조는 16개 중 6개 통과" → "샘플 공장(seed 3) 16개 중 12개 통과(ASM2·ASM3·ASM4·CUT2 실패), seed 1 이면 14개; 템플릿 체인 14개 중 5개". 부호 문장은 P-3.
- 03 §5 시간표를 §2.6·01·05·07 과 동기화(07:30 "앞으로 2주", 08:00/15:30 사진 2회, 반장① '순서 다시 짜기', ② '꼬였던 날·절대 안 하는 것', 15:15 출근부 3개월). 05 의 15:15 행 사진을 15:30 으로.
- 08 시트 6·13 행과 03 §13: `meta.absences`·`hourly_factor`·`paced` 는 "시뮬 입력 구현, **템플릿·변환기 경로 없음(손편집)**", 시트 13 → worklog 는 "변환기 미작성"(또는 `tools/sheet13_to_worklog.py` 작성: HH:MM·날짜 → Day0 분, 수량×BOM → n_parts, 셋업 열 → `setup`).
- 09 §2 판정 문장에 "최근 4주 평균 ≥1.5σ" 추가; §3 학습곡선·§4-2 `validation_report`·`base_version`·스코어카드 경과 열은 "(v1 예정)".
- `trace_validate.py` 각주·03 §8-1 결함 주입 수치는 재실행 값(CUT2 −185(1%)·EB1 +158(98%)·CUT1 −95)으로 갱신, seed=1 명시.

## 5. 기타 메모
- 결함 주입에서 BOR·PACK "운반 잔차 +145~+154" 는 EB2 삭제의 **파급**이지 운반 결함이 아니다. 03 §8-1 패턴표에 "상류 결함이 하류 운반 잔차로 번진다 → 가장 상류의 실패 스테이션부터" 한 줄 추가 권장.
- `absent` 이벤트는 `energy_from_events` 에서 'down' → 근무시간 idle_kw 로 적분. 결근 날 전원 OFF 가능성을 전력 검증에서 분리 표기.
- 연구 18 §6 검정력(n=10, 0.85 → 0.54)은 **동점 제외 n** 기준이어야 한다. 대기 0 이 절반이면 유효 n 은 절반.

관련 파일(절대 경로): `/home/user/claude_mem/factory-twin/tools/templates_to_json.py`, `/home/user/claude_mem/factory-twin/sim/factory_sim.py`, `/home/user/claude_mem/factory-twin/tools/trace_validate.py`, `/home/user/claude_mem/factory-twin/tools/rule_fit.py`, `/home/user/claude_mem/factory-twin/tools/drift_check.py`, `/home/user/claude_mem/factory-twin/tools/hourly_profile.py`, `/home/user/claude_mem/factory-twin/tools/idle_gaps.py`, `/home/user/claude_mem/factory-twin/tools/test_chain.sh`, `/home/user/claude_mem/factory-twin/schema/factory.schema.json`, `/home/user/claude_mem/factory-twin/docs/03_공장복제_명세서.md`, `/home/user/claude_mem/factory-twin/docs/09_트윈_유지_프로토콜.md`, `/home/user/claude_mem/factory-twin/docs/05_역할별_현장카드.md`, `/home/user/claude_mem/factory-twin/docs/08_시트_파라미터_KPI_지도.md`.