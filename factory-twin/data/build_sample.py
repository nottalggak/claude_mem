"""
샘플 가구공장(판넬가구 OEM, 60m x 36m, 작업자 약 20명) 데이터 생성기.
실제 방문 후에는 이 스크립트 대신 capture/ 템플릿에서 채운 값을 tools/templates_to_json.py 로 변환한다.
모든 수치는 '추정 기본값' 이며 현장 측정값으로 교체되어야 한다.
"""
import json, pathlib

W, D = 60.0, 36.0

def rect(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]

factory = {
    "meta": {
        "name": "샘플 판넬가구 공장 (가상)",
        "captured_on": "2026-10-10",
        "source": "sample",
        "shift": {"start": "08:00", "end": "17:00",
                  "breaks": [["10:00", "10:15"], ["12:00", "13:00"], ["15:00", "15:15"]],
                  "days_per_week": 5, "overtime": {"weekday_min": 0, "saturday": None}},
        "energy": {"tariff_krw_per_kwh": 165, "contract_kw": 300, "base_load_kw": 12,
                   "tou": {"note": "[추정] 2026-04-16 개편 구조만 반영. 단가는 한전 요금표 원문으로 교체", "demand_krw_per_kw": 8320,
                           "bands": {"off": 95, "mid": 125, "peak": 160}, "hours": {"off": [[22, 8]], "mid": [[8, 18], [21, 22]], "peak": [[18, 21]]}, "weekend_mid_discount": 0.5}},
        "finance": {"margin_rate": 0.25, "working_days_per_year": 250, "note": "제품 판매가 × 마진율 = 공헌이익(추정). 현장 손익으로 교체"}
    },
    "site": {
        "width": W, "depth": D, "height": 8, "grid_m": 1.0,
        "zones": [
            {"id": "Z_RAW",   "name": "원자재 창고(PB/MDF)", "type": "storage",  "polygon": rect(0, 0, 12, 36),  "color": "#8d6e63"},
            {"id": "Z_CUT",   "name": "재단",               "type": "process",  "polygon": rect(12, 18, 26, 36), "color": "#5c6bc0"},
            {"id": "Z_EDGE",  "name": "엣지밴딩",           "type": "process",  "polygon": rect(26, 18, 40, 36), "color": "#26a69a"},
            {"id": "Z_BORE",  "name": "보링/가공",          "type": "process",  "polygon": rect(40, 18, 52, 36), "color": "#7e57c2"},
            {"id": "Z_FIN",   "name": "도장/건조",          "type": "process",  "polygon": rect(52, 18, 60, 36), "color": "#ef5350"},
            {"id": "Z_OFFICE","name": "사무실",             "type": "office",   "polygon": rect(12, 0, 24, 8),   "color": "#90a4ae"},
            {"id": "Z_HW",    "name": "부자재/하드웨어",     "type": "storage",  "polygon": rect(12, 8, 24, 16),  "color": "#a1887f"},
            {"id": "Z_ASM",   "name": "조립",               "type": "assembly", "polygon": rect(26, 0, 46, 16),  "color": "#ffa726"},
            {"id": "Z_PACK",  "name": "포장",               "type": "process",  "polygon": rect(46, 0, 54, 16),  "color": "#66bb6a"},
            {"id": "Z_FG",    "name": "완제품/출하",         "type": "shipping", "polygon": rect(54, 0, 60, 16),  "color": "#42a5f5"},
            {"id": "Z_AISLE", "name": "주통로",             "type": "aisle",    "polygon": rect(12, 16, 60, 18), "color": "#e0e0e0"}
        ],
        # 기둥 (x, y, w, d)
        "obstacles": [[25.5, 17.5, 0.6, 0.6], [39.5, 17.5, 0.6, 0.6], [24.5, 1.5, 0.6, 0.6], [44.5, 1.5, 0.6, 0.6]]
    },
    "stations": [],
    "ancillary": [
        {"id": "DC1", "name": "집진기 #1 (재단/엣지)", "pos": [20, 35], "size": [2, 1.5, 4], "rated_kw": 22, "mode": "when_any_on", "load_factor": 0.85},
        {"id": "DC2", "name": "집진기 #2 (보링/샌딩)", "pos": [46, 35], "size": [2, 1.5, 4], "rated_kw": 15, "mode": "when_any_on", "load_factor": 0.85},
        {"id": "COMP1", "name": "컴프레서 (스크류 22kW)", "pos": [58, 35], "size": [1.5, 1, 1.5], "rated_kw": 22, "mode": "shift", "load_factor": 0.6}
    ],
    "transport": {
        "handlers": 2, "handler_speed_mps": 1.2, "cart_capacity_parts": 30,
        "forklifts": 1, "forklift_speed_mps": 2.0, "load_unload_min": 1.5,
        "forklift_processes": ["raw", "fg"]
    },
    "workers": [],
    "outsourced": [
        {"id": "OUT_DOOR", "name": "PET 도어 외주", "products": ["P_CAB", "P_WARD"], "order_at": "order",
         "lead_days": {"min": 3, "mode": 5, "max": 9}, "join_process": "assemble", "delay_prob": 0.15, "delay_days": 2}
    ],
    "products": [],
    "orders": {
        "mode": "generate", "horizon_days": 40, "orders_per_day": 13, "release": "install_date",
        "install_lead_days": {"min": 5, "mode": 8, "max": 12, "start_before_days": 2},
        "batching": {"cut_key": "order", "cut_window_min": 60, "sort_min_per_part": 0.1},
        "batch_size": {"P_DESK": 10, "P_BOOK": 6, "P_CAB": 12, "P_WARD": 4},
        "mix": {"P_DESK": 0.35, "P_BOOK": 0.25, "P_CAB": 0.25, "P_WARD": 0.15}
    }
}

def station(id, name, process, zone, pos, size, **kw):
    s = {"id": id, "name": name, "process": process, "zone": zone, "pos": pos, "size": size,
         "rotation_deg": 0, "capacity": 1, "workers_required": 1, "rated_kw": 0, "load_factor": 0.6,
         "idle_kw": 0, "mtbf_min": 0, "mttr_min": 0, "setup_min": 0, "buffer_batches": 4, "scrap_rate": 0.0}
    s.update(kw)
    # 입/출 버퍼 위치: 기본은 기계 아래쪽(통로 방향)
    s.setdefault("in_pos", [pos[0] - size[0] / 2 - 1.0, pos[1] - size[1] / 2 - 1.0])
    s.setdefault("out_pos", [pos[0] + size[0] / 2 + 1.0, pos[1] - size[1] / 2 - 1.0])
    return s

S = factory["stations"]
# 원자재 창고 (가상 스테이션: 배치가 여기서 출발)
S.append(station("RAW", "원자재 적치장", "raw", "Z_RAW", [6, 20], [8, 20, 1.2], capacity=99, workers_required=0,
                 buffer_batches=99, in_pos=[10.5, 17], out_pos=[10.5, 19]))
# 재단
S.append(station("CUT1", "런닝쏘(빔쏘) 3200", "cut", "Z_CUT", [17, 30], [6.5, 4.5, 2.2], maker="(국산)", model="런닝쏘 3.2m", year=2012,
                 workers_required=2, rated_kw=18.5, load_factor=0.55, idle_kw=1.5, mtbf_min=600, mttr_min=25, setup_min=3,
                 cycle={"base_min": 0.12, "per_unit": {"board": 2.6}, "cv": 0.25}, ancillary=["DC1"], scrap_rate=0.01,
                 in_pos=[13.5, 25.5], out_pos=[21.5, 25.5]))
S.append(station("CUT2", "CNC 네스팅 (2440x1220)", "cut", "Z_CUT", [22, 22.5], [4.5, 3.2, 2.0], maker="(중국산)", model="네스팅 1325", year=2019,
                 workers_required=1, rated_kw=13, load_factor=0.6, idle_kw=1.2, mtbf_min=900, mttr_min=40, setup_min=6,
                 cycle={"base_min": 0.05, "per_unit": {"board": 6.0}, "cv": 0.15}, ancillary=["DC1"], scrap_rate=0.005,
                 in_pos=[18.5, 20.5], out_pos=[25, 20.5]))
# 엣지밴딩
S.append(station("EB1", "자동 엣지밴더 (사전밀링+코너라운딩)", "edge", "Z_EDGE", [33, 31], [7.0, 1.6, 1.6], maker="(독일/이탈리아 중고)", model="자동 EB 12m/min", year=2016,
                 workers_required=2, rated_kw=15, load_factor=0.5, idle_kw=2.5, mtbf_min=480, mttr_min=30, setup_min=8,
                 cycle={"base_min": 0.0, "per_unit": {"edges_m": 1 / 12.0, "n_edges": 0.22}, "cv": 0.2}, ancillary=["DC1"], scrap_rate=0.02, availability=0.92,
                 in_pos=[28.5, 29.0], out_pos=[37.5, 29.0]))
S.append(station("EB2", "반자동 엣지밴더", "edge", "Z_EDGE", [32, 24], [5.0, 1.5, 1.5], maker="(국산)", model="반자동 EB 8m/min", year=2010,
                 workers_required=1, rated_kw=7.5, load_factor=0.5, idle_kw=1.0, mtbf_min=360, mttr_min=20, setup_min=5,
                 cycle={"base_min": 0.0, "per_unit": {"edges_m": 1 / 8.0, "n_edges": 0.35}, "cv": 0.25}, ancillary=["DC1"], scrap_rate=0.03,
                 in_pos=[28.5, 22.0], out_pos=[35.5, 22.0]))
# 보링
S.append(station("BOR1", "CNC 보링/가공센터", "bore", "Z_BORE", [45, 31], [4.0, 3.0, 2.0], maker="(국산)", model="CNC 보링 PTP", year=2018,
                 workers_required=1, rated_kw=11, load_factor=0.55, idle_kw=1.0, mtbf_min=720, mttr_min=35, setup_min=4,
                 cycle={"base_min": 0.55, "per_unit": {"holes": 0.035}, "cv": 0.15}, ancillary=["DC2"], scrap_rate=0.01,
                 in_pos=[42, 28.5], out_pos=[48, 28.5]))
S.append(station("BOR2", "다축 보링기 (수동)", "bore", "Z_BORE", [48, 24], [2.5, 2.0, 1.6], maker="(국산)", model="21축 보링", year=2008,
                 workers_required=1, rated_kw=4, load_factor=0.5, idle_kw=0.3, mtbf_min=1200, mttr_min=15, setup_min=9,
                 cycle={"base_min": 0.35, "per_unit": {"holes": 0.03}, "cv": 0.3}, ancillary=["DC2"], scrap_rate=0.02,
                 in_pos=[45.5, 22.0], out_pos=[50.5, 22.0]))
# 도장/건조 (도어 등 도장 부품만)
S.append(station("FIN1", "스프레이 부스", "finish", "Z_FIN", [56, 31], [5.0, 4.0, 2.5], workers_required=1, rated_kw=7.5, load_factor=0.7, idle_kw=0.5,
                 mtbf_min=0, mttr_min=0, setup_min=10, cycle={"base_min": 1.6, "per_unit": {"area_m2": 0.8}, "cv": 0.2}, scrap_rate=0.04,
                 in_pos=[53, 28.5], out_pos=[59, 28.5]))
S.append(station("DRY1", "건조실 (강제건조)", "dry", "Z_FIN", [56, 22], [5.0, 5.0, 2.5], capacity=3, workers_required=0, rated_kw=9, load_factor=0.8,
                 idle_kw=0, batch_time_min=70, buffer_batches=6, in_pos=[53, 19.5], out_pos=[59, 19.5]))
# 조립 (6개 벤치)
for i in range(6):
    col, row = i % 3, i // 3
    x, y = 29 + col * 6, 12 - row * 7
    S.append(station(f"ASM{i+1}", f"조립 벤치 {i+1}", "assemble", "Z_ASM", [x, y], [3.0, 1.6, 0.9], workers_required=1, rated_kw=0.5, idle_kw=0.05,
                     setup_min=2, cycle={"base_min": 0, "per_product": {"P_DESK": 16, "P_BOOK": 24, "P_CAB": 13, "P_WARD": 42}, "cv": 0.2},
                     buffer_batches=2, in_pos=[x - 2.5, y + 1.8], out_pos=[x + 2.5, y + 1.8]))
# 포장
for i in range(2):
    y = 12 - i * 7
    S.append(station(f"PACK{i+1}", f"포장대 {i+1}", "pack", "Z_PACK", [50, y], [3.0, 1.5, 0.9], workers_required=1, rated_kw=0.3, idle_kw=0.05,
                     cycle={"base_min": 0, "per_product": {"P_DESK": 5, "P_BOOK": 7, "P_CAB": 4, "P_WARD": 9}, "cv": 0.2},
                     buffer_batches=3, in_pos=[47.5, y + 1.8], out_pos=[52.5, y + 1.8]))
# 완제품
S.append(station("FG", "완제품 적치/출하", "fg", "Z_FG", [57, 8], [5, 14, 1.5], capacity=99, workers_required=0, buffer_batches=99,
                 in_pos=[55.5, 16.8], out_pos=[55.5, 16.8]))

# 작업자
roles = [("W01", "재단 반장", "cut", "CUT1", 3900000), ("W02", "재단 보조", "cut", "CUT1", 2900000), ("W03", "CNC 재단", "cut", "CUT2", 3300000),
         ("W04", "엣지 반장", "edge", "EB1", 3700000), ("W05", "엣지 보조", "edge", "EB1", 2700000), ("W06", "엣지(반자동)", "edge", "EB2", 2800000),
         ("W07", "CNC 보링", "bore", "BOR1", 3300000), ("W08", "다축 보링", "bore", "BOR2", 2800000),
         ("W09", "도장", "finish", "FIN1", 3400000),
         ("W10", "조립", "assemble", "ASM1", 3000000), ("W11", "조립", "assemble", "ASM2", 3000000), ("W12", "조립", "assemble", "ASM3", 2800000),
         ("W13", "조립", "assemble", "ASM4", 2800000), ("W14", "조립(E-9)", "assemble", "ASM5", 2600000), ("W15", "조립(E-9)", "assemble", "ASM6", 2600000),
         ("W16", "포장", "pack", "PACK1", 2700000), ("W17", "포장(E-9)", "pack", "PACK2", 2600000),
         ("H01", "운반(대차)", "handler", None, 2700000), ("H02", "운반(대차)", "handler", None, 2700000),
         ("F01", "지게차", "forklift", None, 3100000)]
for wid, name, role, st, wage in roles:
    factory["workers"].append({"id": wid, "name": name, "role": role, "skills": [role], "station": st, "monthly_wage_krw": wage})

# 제품 (판넬 치수 m, 엣지 변 수, 홀 수)
def part(id, qty, w, d, n_edges, holes, finish=False, t=0.018):
    return {"id": id, "qty": qty, "w": w, "d": d, "t": t, "n_edges": n_edges, "holes": holes, "finish": finish, "material": "PB 18T LPM"}

factory["products"] = [
    {"id": "P_DESK", "name": "사무용 책상 1400", "routing": ["cut", "edge", "bore", "assemble", "pack"],
     "parts": [part("상판", 1, 1.4, 0.7, 4, 8), part("측판", 2, 0.72, 0.7, 3, 10), part("가림판", 1, 1.3, 0.4, 2, 6), part("서랍판", 4, 0.4, 0.15, 2, 4, t=0.015)],
     "price_krw": 180000, "color": "화이트", "thickness": 18},
    {"id": "P_BOOK", "name": "5단 책장 800x1800", "routing": ["cut", "edge", "bore", "assemble", "pack"],
     "parts": [part("측판", 2, 1.8, 0.3, 3, 14), part("상하판", 2, 0.76, 0.3, 2, 6), part("선반", 4, 0.76, 0.28, 1, 4), part("뒷판", 1, 0.8, 1.8, 0, 0, t=0.005)],
     "price_krw": 120000, "color": "오크", "thickness": 18},
    {"id": "P_CAB", "name": "상부수납장 600 (도어 도장)", "routing": ["cut", "edge", "bore", "finish", "dry", "assemble", "pack"],
     "parts": [part("측판", 2, 0.7, 0.35, 2, 10), part("상하판", 2, 0.56, 0.35, 1, 6), part("도어", 1, 0.6, 0.7, 4, 6, finish=True), part("뒷판", 1, 0.6, 0.7, 0, 0, t=0.005)],
     "price_krw": 95000, "color": "화이트", "thickness": 18},
    {"id": "P_WARD", "name": "붙박이장 모듈 1200x2400", "routing": ["cut", "edge", "bore", "finish", "dry", "assemble", "pack"],
     "parts": [part("측판", 2, 2.4, 0.6, 3, 24), part("상하판", 2, 1.16, 0.6, 2, 8), part("선반", 3, 1.16, 0.55, 1, 4), part("도어", 2, 0.6, 2.35, 4, 10, finish=True), part("뒷판", 1, 1.2, 2.4, 0, 0, t=0.005)],
     "price_krw": 520000, "color": "그레이", "thickness": 18},
]

out = pathlib.Path(__file__).with_name("sample_factory.json")
out.write_text(json.dumps(factory, ensure_ascii=False, indent=1), encoding="utf-8")
print("wrote", out, len(S), "stations")
