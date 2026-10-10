"""현장수집_템플릿.xlsx → data/<factory>.json (schema/factory.schema.json) 변환.
빈 칸은 샘플 기본값/추정치로 채우고 'assumptions' 목록에 기록한다."""
import sys, json, pathlib, math
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
                  "energy": {"tariff_krw_per_kwh": num(basic.get("평균 단가 (원/kWh)"), 165), "contract_kw": num(basic.get("계약전력 (kW)"), 0), "base_load_kw": num(basic.get("기본부하 (kW)"), 10)}},
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
    ct = {}
    for r in rows(wb["4_공정_사이클타임"]):
        sec = num(r.get("소요(초)"))
        if sec is None: continue
        ct.setdefault(r["기계ID"], []).append((sec / 60, r.get("구분(가공/핸들링/셋업/대기)")))
    for st in f["stations"]:
        obs = [m for m, kind in ct.get(st["id"], []) if kind in (None, "", "가공", "핸들링")]
        if obs:
            mean = sum(obs) / len(obs); sd = (sum((o - mean) ** 2 for o in obs) / len(obs)) ** 0.5
            st["cycle"] = {"base_min": round(mean, 3), "per_unit": {}, "cv": round(sd / mean, 2) if mean else 0}
        elif st["process"] not in ("raw", "fg"):
            st["cycle"] = {"base_min": 1.0, "per_unit": {}, "cv": 0.3}; assumptions.append(f"{st['id']}: 사이클타임 측정 없음 → 1분/부품 가정")
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
    tot = sum(f["orders"]["mix"].values()) or 1
    f["orders"]["mix"] = {k: round(v / tot, 3) for k, v in f["orders"]["mix"].items()}
    f["assumptions"] = assumptions
    pathlib.Path(out).write_text(json.dumps(f, ensure_ascii=False, indent=1), encoding="utf-8")
    print("wrote", out, "| stations", len(f["stations"]), "| products", len(f["products"]), "| assumptions", len(assumptions))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "capture/templates/현장수집_템플릿.xlsx", sys.argv[2] if len(sys.argv) > 2 else "data/survey_factory.json")
