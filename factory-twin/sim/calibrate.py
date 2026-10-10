"""보정(calibration): 불확실 파라미터를 경계 안에서 조정해 보정용 검증 지표와의 오차를 줄인다.
끼워맞춤 방지 장치: (1) 조정 가능한 파라미터는 출처 등급 C/D 또는 명시 목록만, (2) 경계는 측정값 ±출처 폭, (3) 홀드아웃 지표는 목적함수에 넣지 않고 사후 판정만,
(4) 규제항(측정값에서 멀어질수록 벌점), (5) 파라미터 수 ≤ 보정 지표 수 (식별 가능성).
사용: python3 calibrate.py factory.json --targets '[{"metric":"throughput_steady_per_day","actual":85,"weight":1},{"metric":"lead_time_work_min_avg","actual":700,"weight":1}]' \
      --params CUT2.cycle EB2.cycle transport.handler_speed_mps --holdout '[{"metric":"avg_wip_batches","actual":28,"tolerance_pct":20}]'
알고리즘: 좌표 탐색(coordinate search) + 축소 스텝, seed 2회 평균. 작은 공장 모델엔 충분; 더 정교한 방법(GP 에뮬레이터·베이지안)은 docs/research/14 참고.
"""
import json, sys, copy, pathlib, argparse, statistics
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from factory_sim import Sim
from validate import get, validate

WIDTH = {"measured": 0.10, "record": 0.15, "interview": 0.25, "estimated": 0.40}


def set_param(f, name, mult):
    g = copy.deepcopy(f)
    if name.startswith("transport."):
        g["transport"][name.split(".", 1)[1]] *= mult; return g
    sid, key = name.split(".", 1)
    for s in g["stations"]:
        if s["id"] == sid:
            if key == "cycle":
                c = s["cycle"]; c["base_min"] *= mult; c["per_unit"] = {k: v * mult for k, v in c.get("per_unit", {}).items()}
                if "per_product" in c: c["per_product"] = {k: v * mult for k, v in c["per_product"].items()}
            else:
                s[key] = s[key] * mult
    return g


def run(f, seeds):
    ks = [Sim(f, seed=sd).run() for sd in seeds]
    return {m: statistics.mean(get(k, m) for k in ks) for m in METRICS}


def loss(f, targets, mults, lam, seeds):
    out = run(f, seeds)
    err = sum(t.get("weight", 1) * ((out[t["metric"]] - t["actual"]) / max(1e-9, abs(t["actual"]))) ** 2 for t in targets)
    reg = lam * sum((m - 1) ** 2 for m in mults.values())
    return err + reg, out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("factory"); ap.add_argument("--targets", required=True); ap.add_argument("--params", nargs="+", required=True)
    ap.add_argument("--holdout", default="[]"); ap.add_argument("--seeds", type=int, default=2); ap.add_argument("--lam", type=float, default=0.5); ap.add_argument("--iters", type=int, default=3); ap.add_argument("--out", default=None)
    a = ap.parse_args(); f = json.loads(pathlib.Path(a.factory).read_text(encoding="utf-8")); targets = json.loads(a.targets); holdout = json.loads(a.holdout)
    global METRICS; METRICS = sorted({t["metric"] for t in targets} | {h["metric"] for h in holdout})
    if len(a.params) > len(targets):
        print(f"경고: 조정 파라미터 {len(a.params)}개 > 보정 지표 {len(targets)}개 → 식별 불가(여러 해). 파라미터를 줄이거나 지표를 늘리세요.")
    prov = f.get("provenance", {}); mults = {p: 1.0 for p in a.params}; seeds = list(range(1, a.seeds + 1))
    bounds = {p: WIDTH.get(prov.get(p, "estimated"), 0.4) for p in a.params}
    cur = f; best, out0 = loss(cur, targets, mults, a.lam, seeds); print("초기 손실", round(best, 4), {m: round(v, 1) for m, v in out0.items()})
    step = 0.15
    for it in range(a.iters):
        improved = False
        for p in a.params:
            for d in (+step, -step):
                m2 = max(1 - bounds[p], min(1 + bounds[p], mults[p] * (1 + d)))
                if m2 == mults[p]: continue
                g = set_param(f, p, m2)
                for q, mq in mults.items():
                    if q != p: g = set_param(g, q, mq)
                L, out = loss(g, targets, {**mults, p: m2}, a.lam, seeds)
                if L < best:
                    best, mults[p], cur, improved = L, m2, g, True; print(f"  iter {it + 1}: {p} ×{m2:.3f} → 손실 {L:.4f} {[round(out[t['metric']], 1) for t in targets]}")
        if not improved: step /= 2
    print("최종 배수", {k: round(v, 3) for k, v in mults.items()}, "손실", round(best, 4))
    for p in a.params:
        if abs(mults[p] - 1) >= bounds[p] - 1e-9: print(f"  주의: {p} 가 경계({bounds[p]:.0%})에 닿음 → 구조 오류 의심(측정 재확인)")
    if holdout:
        ks = Sim(cur, seed=99).run(); ok, rows = validate(ks, holdout)
        print("홀드아웃 판정:", "통과" if ok else "실패"); [print("  ", r) for r in rows]
    if a.out:
        cur["calibration"] = {"multipliers": mults, "targets": targets, "loss": best}
        pathlib.Path(a.out).write_text(json.dumps(cur, ensure_ascii=False, indent=1), encoding="utf-8"); print("wrote", a.out)


if __name__ == "__main__":
    main()
