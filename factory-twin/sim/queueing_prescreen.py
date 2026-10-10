"""Kingman(VUT) 대기행렬 사전 스크리닝: 시뮬레이션 전에 스테이션별 가동률 u, 대기시간 CT_q 를 근사해 투자 후보를 거른다.
u = λ·t_e/m, t_e = (평균 처리시간/부품 × 배치 부품수 + 셋업)/가용률, c_e² = c_0² + 고장 항 (Hopp & Spearman)
CT_q ≈ ((c_a²+c_e²)/2) · u^{√(2(m+1))−1}/(m(1−u)) · t_e
사용: python3 queueing_prescreen.py ../data/sample_factory.json [--demand 1.2]  (수요 ×1.2 체제)"""
import json, sys, pathlib, math, argparse

ap = argparse.ArgumentParser(); ap.add_argument("factory"); ap.add_argument("--demand", type=float, default=1.0); ap.add_argument("--ca2", type=float, default=1.0)
a = ap.parse_args(); f = json.loads(pathlib.Path(a.factory).read_text(encoding="utf-8"))
o = f["orders"]; mix = o["mix"]; prods = {p["id"]: p for p in f["products"]}
shift_min = 450  # 추정: 교대 가용 분 (휴식 제외)
sh = f["meta"]["shift"]; shift_min = (int(sh["end"][:2]) * 60 + int(sh["end"][3:])) - (int(sh["start"][:2]) * 60 + int(sh["start"][3:])) - sum((int(b[:2]) * 60 + int(b[3:])) - (int(a_[:2]) * 60 + int(a_[3:])) for a_, b in sh.get("breaks", []))
orders_day = o.get("orders_per_day", 8) * a.demand
by_proc = {}
for s in f["stations"]:
    by_proc.setdefault(s["process"], []).append(s)
rows = []
for proc, sts in by_proc.items():
    if proc in ("raw", "fg"): continue
    # 공정별 일 수요(배치 수)와 배치당 평균 처리시간(부품 속성 가중)
    lam = 0.0; work = 0.0; setup = 0.0
    for pid, share in mix.items():
        p = prods[pid]
        if proc not in p["routing"]: continue
        n_batches = orders_day * share; qty = o.get("batch_size", {}).get(pid, 5)
        lam += n_batches
        s0 = sts[0]; c = s0.get("cycle", {})
        if s0.get("batch_time_min"): t = s0["batch_time_min"]
        elif proc in ("assemble", "pack"): t = c.get("per_product", {}).get(pid, c.get("base_min", 0)) * qty
        else:
            t = 0.0
            for part in p["parts"]:
                n = part["qty"] * qty; perim = 2 * (part["w"] + part["d"]); edges_m = perim * part.get("n_edges", 0) / 4
                attrs = {"area_m2": part["w"] * part["d"], "edges_m": edges_m, "n_edges": part.get("n_edges", 0), "holes": part.get("holes", 0), "board": 0}
                if proc == "edge" and part.get("n_edges", 0) == 0: continue
                if proc == "finish" and not part.get("finish"): continue
                if proc == "bore" and part.get("holes", 0) == 0: continue
                t += n * (c.get("base_min", 0) + sum(v * attrs.get(k, 0) for k, v in c.get("per_unit", {}).items()))
            if proc == "cut":
                area = sum(part["w"] * part["d"] * part["qty"] * qty for part in p["parts"]); boards = math.ceil(area / (2.44 * 1.22 * 0.78))
                t += boards * c.get("per_unit", {}).get("board", 0)
        work += n_batches * t; setup += n_batches * s0.get("setup_min", 0) * 0.7  # 전환 확률 추정 0.7
    m = sum(s.get("capacity", 1) for s in sts); avail = sum((s.get("availability", 1.0) or 1.0) for s in sts) / len(sts)
    te = (work + setup) / max(1e-9, lam) / avail  # 배치당 유효 처리시간
    u = lam * te / (m * shift_min)
    c0 = sts[0].get("cycle", {}).get("cv", 0.3) ** 2
    mtbf, mttr = sts[0].get("mtbf_min", 0), sts[0].get("mttr_min", 0)
    A = mtbf / (mtbf + mttr) if mtbf else 1.0; ce2 = c0 + (2 * A * (1 - A) * mttr / max(1e-9, te)) if mtbf else c0
    if u < 1: ctq = ((a.ca2 + ce2) / 2) * (u ** (math.sqrt(2 * (m + 1)) - 1) / (m * (1 - u))) * te
    else: ctq = float("inf")
    rows.append((u, proc, ",".join(s["id"] for s in sts), m, round(te, 1), round(ctq, 1), round(ce2, 2)))
rows.sort(reverse=True)
print(f"# Kingman 사전 스크리닝 (수요 ×{a.demand}, 교대 {shift_min}분/일)\n\n| 공정 | 스테이션 | 대수 m | 배치당 유효시간 t_e(분) | 가동률 u | 예상 대기 CT_q(분) | c_e² | 판정 |\n|---|---|---|---|---|---|---|---|")
for u, proc, ids, m, te, ctq, ce2 in rows:
    verdict = "증설 후보(u≥0.85)" if u >= 0.85 else ("주의(u≥0.7)" if u >= 0.7 else "여유")
    print(f"| {proc} | {ids} | {m} | {te} | {u:.2f} | {ctq if ctq != float('inf') else '∞'} | {ce2} | {verdict} |")
print("\n해석: u 가 0.8→0.9 로 가면 대기가 약 2배. 수요 ×1.2(성수기) 로 다시 돌려 체제별 후보를 본다. 이 근사는 시뮬레이션 전 거름망이며, 최종 판단은 트윈 + 신뢰구간.")
