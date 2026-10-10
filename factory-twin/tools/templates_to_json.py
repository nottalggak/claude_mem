"""현장수집_템플릿.xlsx → data/<factory>.json (schema/factory.schema.json) 변환.
빈 칸은 샘플 기본값/추정치로 채우고 'assumptions' 목록에 기록한다."""
import sys, json, pathlib, math, re
from openpyxl import load_workbook

def rows(ws):
    hdr = [c.value for c in ws[2]]
    for r in ws.iter_rows(min_row=3, values_only=True):
        if not any(v not in (None, "") for v in r):
            continue
        yield dict(zip(hdr, r))

def num(v, default=None):
    try:
        return float(v) if v not in (None, "") else default
    except (TypeError, ValueError):
        return default

def main(xlsx, out):
    wb = load_workbook(xlsx, data_only=True)
    assumptions = []
    basic = {r[0]: r[1] for r in wb["0_공장기본"].iter_rows(min_row=3, values_only=True) if r and r[0]}
    W = num(basic.get("건물 가로 x (m)"), 60); D = num(basic.get("건물 세로 y (m)"), 36)
    brk = [b for b in [basic.get("휴식1"), basic.get("점심"), basic.get("휴식2")] if b]
    f = {"meta": {"name": basic.get("공장명") or "공장", "address": basic.get("주소") or "", "captured_on": str(basic.get("방문일") or ""), "source": "survey",
                  "shift": {"start": str(basic.get("근무 시작") or "08:00"), "end": str(basic.get("근무 종료") or "17:00"),
                            "breaks": [s.replace(" ", "").split("-") for s in brk], "days_per_week": int(num(basic.get("주 근무일수"), 5))},
                  "energy": {"tariff_krw_per_kwh": num(basic.get("평균 단가 (원/kWh)"), 165), "contract_kw": num(basic.get("계약전력 (kW)"), 0), "base_load_kw": num(basic.get("기본부하 (kW)"), 10), "monthly_bill_krw": num(basic.get("월 평균 전기요금 (원)"), None)},
                  "overtime_note": basic.get("잔업 패턴") or "", "erp": basic.get("ERP/MES 사용") or "", "headcount": basic.get("종업원 수 (내국인/외국인)") or ""},
         "site": {"width": W, "depth": D, "height": num(basic.get("천장고 (m)"), 8), "grid_m": 1.0, "zones": [], "obstacles": []},
         "stations": [], "ancillary": [], "transport": {"handlers": 2, "handler_speed_mps": 1.2, "cart_capacity_parts": 30, "forklifts": 1, "forklift_speed_mps": 2.0, "load_unload_min": 1.5, "forklift_processes": ["raw", "fg"]},
         "workers": [], "products": [], "orders": {"mode": "generate", "horizon_days": 5, "orders_per_day": 8, "release": "spread", "batch_size": {}, "mix": {}}}
    for r in rows(wb["1_구역"]):
        x0, y0, x1, y1 = (num(r[k], 0) for k in ("x0", "y0", "x1", "y1"))
        f["site"]["zones"].append({"id": r["구역ID"], "name": r["구역명"], "type": r.get("유형(storage/process/assembly/office/aisle/shipping/utility)") or "other",
                                   "polygon": [[x0, y0], [x1, y0], [x1, y1], [x0, y1]], "color": "#78909c"})
    for r in rows(wb["2_기계대장"]):
        pos = [num(r["중심 x"], 0), num(r["중심 y"], 0)]; size = [num(r["길이(x,m)"], 2), num(r["깊이(y,m)"], 1.5), num(r["높이(m)"], 1.5)]
        ratedA = num(r.get("정격 A")); idleA = num(r.get("클램프 A(공회전)")); runA = num(r.get("클램프 A(가공)")); V = 380
        rated_kw = num(r.get("정격 kW(명판)"))
        if rated_kw is None and ratedA: rated_kw = math.sqrt(3) * V * ratedA * 0.85 / 1000
        if rated_kw is None: rated_kw = 5; assumptions.append(f"{r['기계ID']}: 정격 kW 미입력 → 5 kW 가정")
        lf = num(r.get("부하율(추정)")); idle_kw = num(r.get("대기 kW(추정)"))
        if runA and rated_kw: lf = lf or min(1.0, math.sqrt(3) * V * runA * 0.85 / 1000 / rated_kw)
        if idleA: idle_kw = idle_kw or math.sqrt(3) * V * idleA * 0.6 / 1000
        proc = r.get("공정(cut/edge/bore/finish/dry/sand/press/assemble/pack/raw/fg)") or "other"
        st = {"id": r["기계ID"], "name": r["기계명"], "process": proc, "zone": r.get("구역ID") or "", "pos": pos, "size": size, "rotation_deg": num(r.get("회전(도)"), 0),
              "maker": r.get("제조사") or "", "model": r.get("모델") or "", "year": int(num(r.get("연식"), 0)) or None,
              "capacity": int(num(r.get("대수(capacity)"), 1)), "workers_required": int(num(r.get("작업자 수"), 1)), "rated_kw": round(rated_kw, 1), "load_factor": lf or 0.6, "idle_kw": round(idle_kw or rated_kw * 0.1, 2),
              "mtbf_min": num(r.get("MTBF(시간)"), 0) * 60, "mttr_min": num(r.get("MTTR(분)"), 0), "setup_min": num(r.get("셋업 시간(분)"), 0), "buffer_batches": int(num(r.get("버퍼 용량(배치/대차 수)"), 4)),
              "scrap_rate": num(r.get("불량률(%)"), 0) / 100, "ancillary": [a.strip() for a in str(r.get("집진 연결(ID)") or "").split(",") if a.strip()],
              "in_pos": [num(r.get("입력버퍼 x"), pos[0] - size[0] / 2 - 1), num(r.get("입력버퍼 y"), pos[1] - size[1] / 2 - 1)],
              "out_pos": [num(r.get("출력버퍼 x"), pos[0] + size[0] / 2 + 1), num(r.get("출력버퍼 y"), pos[1] - size[1] / 2 - 1)],
              "photo": r.get("전체사진 파일") or "", "notes": r.get("비고") or ""}
        f["stations"].append(st)
    for r in rows(wb["3_부대설비"]):
        f["ancillary"].append({"id": r["설비ID"], "name": r["설비명"], "pos": [num(r.get("x"), 0), num(r.get("y"), 0)], "size": [num(r.get("길이"), 1.5), num(r.get("깊이"), 1.5), num(r.get("높이"), 2)],
                               "rated_kw": num(r.get("정격 kW"), 10), "mode": r.get("운전 모드(when_any_on/shift/always)") or "shift", "load_factor": num(r.get("부하율(추정)"), 0.7)})
    # 사이클타임 → 기계별 부품당 시간 (평균, cv)
    ct = {}  # 기계ID -> 측정# -> {"min": 합산 분, "edges": n, "holes": n}
    for r in rows(wb["4_공정_사이클타임"]):
        sec = num(r.get("소요(초)")); kind = r.get("구분(가공/핸들링/셋업/대기)")
        if sec is None or kind in ("셋업", "대기"): continue
        if str(r.get("첫 사이클(버림 Y)") or "").upper().startswith("Y"): continue
        rating = num(r.get("평정(100=정상 속도)"), 100) / 100.0
        k = (r["기계ID"], r.get("측정#") or id(r))
        d = ct.setdefault(r["기계ID"], {}).setdefault(k, {"min": 0.0, "edges": num(r.get("엣지 변 수"), 0), "holes": num(r.get("홀 수"), 0)})
        d["min"] += sec / 60 * rating  # 정상 속도로 정규화
    for st in f["stations"]:
        obs = list(ct.get(st["id"], {}).values())
        if obs:
            ys = [o["min"] for o in obs]; mean = sum(ys) / len(ys); sd = (sum((y - mean) ** 2 for y in ys) / len(ys)) ** 0.5
            per_unit = {}
            # 단순 1변수 회귀: 엣지(엣지 공정) 또는 홀(보링 공정)
            key = "n_edges" if st["process"] == "edge" else ("holes" if st["process"] == "bore" else None)
            xs = [o["edges"] if key == "n_edges" else o["holes"] for o in obs] if key else []
            if key and len(obs) >= 5 and max(xs) > min(xs):
                xm = sum(xs) / len(xs); b = sum((x - xm) * (y - mean) for x, y in zip(xs, ys)) / sum((x - xm) ** 2 for x in xs)
                a = mean - b * xm
                if b > 0 and a >= 0: per_unit = {key: round(b, 4)}; mean = a
            st["cycle"] = {"base_min": round(mean, 3), "per_unit": per_unit, "cv": round(sd / (mean + sum(per_unit.values()) * (sum(xs) / len(xs) if xs else 0) + 1e-9), 2), "n": len(obs)}
        elif st["process"] not in ("raw", "fg"):
            st["cycle"] = {"base_min": 1.0, "per_unit": {}, "cv": 0.3}; assumptions.append(f"{st['id']}: 사이클타임 측정 없음 → 1분/부품 가정")
    # 시트 2 추가 열 → 가용률·메타
    for r in rows(wb["2_기계대장"]):
        for st in f["stations"]:
            if st["id"] == r["기계ID"]:
                micro = num(r.get("소정지 빈도(회/시간)"), 0); warm = num(r.get("예열/청소 시간(분/일)"), 0)
                st["availability"] = round(max(0.5, 1 - micro * 2 / 60 - warm / 450), 3)  # 소정지 2분/회 가정, 450분 교대
                for col, key in [("이동 등급(A자유/B리깅/C고정)", "move_class"), ("이전 비용(만원, 추정)", "relocation_cost_10k"), ("처리 가능 범위(최대 판 치수·두께)", "capability"), ("투입측 판재 공간(m)", "infeed_m"), ("배출측 판재 공간(m)", "outfeed_m"), ("셋업 트리거(색상/두께/제품)", "setup_trigger"), ("PLC/HMI 브랜드", "plc"), ("공압 사용(Y/N)", "air")]:
                    if r.get(col) not in (None, ""): st[key] = r.get(col)
    # 시트 5 셋업: 기계별 평균 소요·빈도
    if "5_셋업_체인지오버" in wb.sheetnames:
        su = {}
        for r in rows(wb["5_셋업_체인지오버"]):
            m = num(r.get("소요(분)"))
            if m is not None: su.setdefault(r["기계ID"], []).append((m, num(r.get("빈도(회/일)"), None)))
        for st in f["stations"]:
            if st["id"] in su:
                vals = su[st["id"]]; st["setup_min"] = round(sum(v for v, _ in vals) / len(vals), 1)
                fr = [q for _, q in vals if q]; 
                if fr: st["setup_per_day_observed"] = sum(fr) / len(fr)
    # 시트 11 전력 측정 → 부하율·대기전력
    if "11_전력측정" in wb.sheetnames:
        for r in rows(wb["11_전력측정"]):
            tgt = r.get("측정 대상(기계ID/분전반/인입)"); state = str(r.get("상태(정지/공회전/가공)") or "")
            A = [num(r.get(k)) for k in ("전류 A (R)", "A (S)", "A (T)")]; A = [a for a in A if a]
            if not tgt or not A: continue
            kw = math.sqrt(3) * num(r.get("전압 V"), 380) * (sum(A) / len(A)) * num(r.get("역률(추정)"), 0.85 if "가공" in state else 0.6) / 1000
            for st in f["stations"]:
                if st["id"] == tgt:
                    if "가공" in state and st.get("rated_kw"): st["load_factor"] = round(min(1.0, kw / st["rated_kw"]), 2)
                    elif "공회전" in state: st["idle_kw"] = round(kw, 2)
    for r in rows(wb["6_작업자"]):
        f["workers"].append({"id": r["작업자ID"], "name": r.get("이름/호칭") or "", "role": r.get("역할") or "", "station": r.get("주 담당 기계ID") or None,
                             "skills": [s.strip() for s in str(r.get("보조 가능 공정(스킬)") or "").split(",") if s.strip()], "employment": r.get("고용형태(정규/계약/E-9)") or "", "monthly_wage_krw": num(r.get("월 임금(원, 추정)"), 0)})
    prods = {}
    for r in rows(wb["7_제품_BOM"]):
        pid = r["제품ID"]
        p = prods.setdefault(pid, {"id": pid, "name": r.get("제품명") or pid, "routing": [s.strip() for s in str(r.get("라우팅(cut>edge>bore>finish>dry>assemble>pack)") or "cut>edge>bore>assemble>pack").split(">")],
                                   "parts": [], "price_krw": num(r.get("판매가(원)"), 0)})
        if r.get("부품명"):
            p["parts"].append({"id": r["부품명"], "qty": int(num(r.get("수량/제품"), 1)), "w": num(r.get("가로 w(m)"), 0.6), "d": num(r.get("세로 d(m)"), 0.4), "t": num(r.get("두께 t(m)"), 0.018),
                               "material": r.get("자재") or "", "n_edges": int(num(r.get("엣지 변 수"), 0)), "holes": int(num(r.get("홀 수"), 0)), "finish": str(r.get("도장(Y/N)") or "N").upper().startswith("Y")})
        if num(r.get("주문당 수량(배치)")): f["orders"]["batch_size"][pid] = int(num(r.get("주문당 수량(배치)")))
        if num(r.get("월 수량")): f["orders"]["mix"][pid] = num(r.get("월 수량"))
        for st in f["stations"]:
            if st["process"] == "assemble" and num(r.get("조립 시간(분/제품)")): st.setdefault("cycle", {"base_min": 0, "per_unit": {}, "cv": 0.2}).setdefault("per_product", {})[pid] = num(r.get("조립 시간(분/제품)"))
            if st["process"] == "pack" and num(r.get("포장 시간(분/제품)")): st.setdefault("cycle", {"base_min": 0, "per_unit": {}, "cv": 0.2}).setdefault("per_product", {})[pid] = num(r.get("포장 시간(분/제품)"))
    f["products"] = list(prods.values())
    # 외주 병렬 경로 (시트 20)
    f["outsourced"] = []
    if "20_외주경로" in wb.sheetnames:
        for r in rows(wb["20_외주경로"]):
            oa = str(r.get("발주 시점(어느 공정 후·시공일 D-n)") or "order")
            order_at = "order" if ("주문" in oa or oa == "order") else ("release" if "투입" in oa else (f"after:{oa.split('후')[0].strip()}" if "후" in oa else "order"))
            f["outsourced"].append({"id": "OUT_" + str(r["외주 품목(도어/상판/철재/유리/도장)"]), "name": str(r["외주 품목(도어/상판/철재/유리/도장)"]) + " 외주 (" + str(r.get("외주처") or "") + ")",
                                    "products": [x.strip() for x in str(r.get("적용 제품ID(쉼표)") or "").split(",") if x.strip()], "order_at": order_at,
                                    "lead_days": {"min": num(r.get("리드타임 min(일)"), 3), "mode": num(r.get("mode"), 5), "max": num(r.get("max"), 9)},
                                    "join_process": {"조립": "assemble", "포장": "pack", "시공현장": "install"}.get(str(r.get("합류 지점(조립/포장/시공현장)") or "조립"), "assemble"),
                                    "delay_prob": min(1.0, num(r.get("지연 빈도(회/월)"), 0) / max(1, num(r.get("월 건수"), 1))), "delay_days": 2})
            if not f["outsourced"][-1]["products"]: assumptions.append(f"외주 {f['outsourced'][-1]['id']}: 적용 제품ID 열이 비어 있음 → 지정 필요")
    f["orders"]["release"] = "install_date"; f["orders"].setdefault("install_lead_days", {"min": 5, "mode": 8, "max": 12, "start_before_days": 2})
    f["orders"]["batching"] = {"cut_key": "order", "cut_window_min": 60, "sort_min_per_part": 0.1}
    # 시트 8 주문이력 → 일 주문 수·시공 여유일 분포·제품 믹스·재생용 목록
    if "8_주문이력" in wb.sheetnames:
        hist = list(rows(wb["8_주문이력"]))
        if hist:
            import datetime as _dt
            def _d(v):
                if isinstance(v, _dt.datetime): return v.date()
                if isinstance(v, _dt.date): return v
                try: return _dt.datetime.strptime(str(v)[:10], "%Y-%m-%d").date()
                except Exception: return None
            days = {}; leads = []; mixc = {}
            for r in hist:
                od, dd = _d(r.get("주문일")), _d(r.get("납기일"))
                if od: days[od] = days.get(od, 0) + 1
                if od and dd: leads.append(max(0, (dd - od).days * 5 / 7))  # 근무일 환산
                mixc[r.get("제품ID")] = mixc.get(r.get("제품ID"), 0) + num(r.get("수량"), 1)
            if days:
                span = (max(days) - min(days)).days * 5 / 7 + 1
                f["orders"]["orders_per_day"] = round(len(hist) / max(1, span), 2)
            if leads:
                leads.sort(); f["orders"]["install_lead_days"] = {"min": round(leads[0], 1), "mode": round(leads[len(leads) // 2], 1), "max": round(leads[-1], 1), "start_before_days": 2}
                assumptions.append("투입 규칙 D-2 는 기본값 → 시트 16 규칙으로 교체")
            if mixc and not f["orders"]["mix"]: f["orders"]["mix"] = {k: v for k, v in mixc.items() if k}
            f["orders"]["history_list"] = [{"order_date": str(r.get("주문일")), "due_date": str(r.get("납기일")), "product": r.get("제품ID"), "qty": num(r.get("수량"), 1), "shipped": str(r.get("출하일") or "")} for r in hist]
    # 시트 16 의사결정규칙 → 배치 키·투입 규칙(최소 매핑), 나머지는 rules 로 보존
    if "16_의사결정규칙" in wb.sheetnames:
        f["rules"] = []
        for r in rows(wb["16_의사결정규칙"]):
            f["rules"].append({k: r.get(k) for k in r})
            topic = str(r.get("주제(배치구성/투입/기계선택/셋업시점/운반/잔업/급한주문/조립착수/품질판정/인력대체)") or ""); then = str(r.get("그러면 (행동)") or "")
            if "배치" in topic and ("색상" in then or "두께" in then): f["orders"]["batching"]["cut_key"] = "color_thickness"
            if "투입" in topic:
                m = re.search(r"D\s*-\s*(\d+)", then)
                if m: f["orders"].setdefault("install_lead_days", {"min": 5, "mode": 8, "max": 12})["start_before_days"] = int(m.group(1))
    # 시트 18 검증지표 → observations.validation
    if "18_검증지표" in wb.sheetnames:
        val = []
        for r in rows(wb["18_검증지표"]):
            key = r.get("모델 KPI 키(kpis.json 경로)"); actual = r.get("실제 값")
            if not key or actual in (None, ""): continue
            o = {"metric": key, "actual": num(actual, actual), "source": r.get("출처") or "", "stage": r.get("단계(v0.5/v1)") or "v0.5"}
            if num(r.get("허용 오차 절대값(비율형)")) is not None: o["tolerance_abs"] = num(r.get("허용 오차 절대값(비율형)"))
            elif num(r.get("허용 오차 % (v0.5)")) is not None: o["tolerance_pct"] = num(r.get("허용 오차 % (v0.5)"))
            val.append(o)
        f["observations"] = {"validation": val}
    # 시트 23 운반·출하 대장 → transport
    if "23_운반_출하대장" in wb.sheetnames:
        for r in rows(wb["23_운반_출하대장"]):
            item = str(r.get("항목(대차/A형대차/팔레트/지게차/탑차/시공팀)") or "")
            if "대차" in item:
                f["transport"]["handlers"] = int(num(r.get("수량"), f["transport"]["handlers"])); f["transport"]["cart_capacity_parts"] = int(num(r.get("적재량(부품 수 또는 현장 수)"), 30))
                if num(r.get("속도(m/s) 또는 상차 시간(분/현장)")): f["transport"]["handler_speed_mps"] = num(r.get("속도(m/s) 또는 상차 시간(분/현장)"))
                if num(r.get("적재·하역 시간(분)")): f["transport"]["load_unload_min"] = num(r.get("적재·하역 시간(분)"))
            elif "지게차" in item:
                f["transport"]["forklifts"] = int(num(r.get("수량"), 1))
                if num(r.get("속도(m/s) 또는 상차 시간(분/현장)")): f["transport"]["forklift_speed_mps"] = num(r.get("속도(m/s) 또는 상차 시간(분/현장)"))
            elif "탑차" in item or "시공" in item:
                f.setdefault("shipping", {})[item] = {"count": num(r.get("수량"), 0), "sites_per_day": num(r.get("하루 시공 가능 현장 수"), None), "load_min_per_site": num(r.get("속도(m/s) 또는 상차 시간(분/현장)"), None)}
    # 시트 7 색상·두께 → products
    for r in rows(wb["7_제품_BOM"]):
        for p in f["products"]:
            if p["id"] == r["제품ID"]:
                if r.get("원장 색상"): p["color"] = r.get("원장 색상")
                if num(r.get("원장 두께(mm)")): p["thickness"] = num(r.get("원장 두께(mm)"))
    # 시트 20 외주 products 열 → 매핑(쉼표 구분 제품ID)
    tot = sum(f["orders"]["mix"].values()) or 1
    f["orders"]["mix"] = {k: round(v / tot, 3) for k, v in f["orders"]["mix"].items()}
    f["assumptions"] = assumptions
    pathlib.Path(out).write_text(json.dumps(f, ensure_ascii=False, indent=1), encoding="utf-8")
    print("wrote", out, "| stations", len(f["stations"]), "| products", len(f["products"]), "| assumptions", len(assumptions))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "capture/templates/현장수집_템플릿.xlsx", sys.argv[2] if len(sys.argv) > 2 else "data/survey_factory.json")
