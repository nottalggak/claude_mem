"""보정(calibration): 불확실 파라미터를 경계 안에서 조정해 보정용 검증 지표와의 오차를 줄인다.
끼워맞춤 방지 장치: (1) 조정 가능한 파라미터는 출처 등급 C/D 또는 명시 목록만, (2) 경계는 측정값 ±출처 폭, (3) 홀드아웃 지표는 목적함수에 넣지 않고 사후 판정만,
(4) 규제항(측정값에서 멀어질수록 벌점), (5) 파라미터 수 ≤ 보정 지표 수 (식별 가능성).
사용: python3 calibrate.py factory.json --targets '[{"metric":"throughput_steady_per_day","actual":85,"weight":1},{"metric":"lead_time_work_min_avg","actual":700,"weight":1}]' \
      --params CUT2.cycle EB2.cycle transport.handler_speed_mps --holdout '[{"metric":"avg_wip_batches","actual":28,"tolerance_pct":20}]'
알고리즘: 파라미터별 격자 라인서치(경계 안 5점, 반복마다 축소) + CRN seed 평균. 규제 λ·Σ((m−1)/bound)². 작은 공장 모델엔 충분; 더 정교한 방법(GP 에뮬레이터·베이지안)은 docs/research/14 참고.
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


def run(f, seeds, return_sd=False):
    ks = [Sim(f, seed=sd).run() for sd in seeds]
    means = {m: statistics.mean(get(k, m) for k in ks) for m in METRICS}
    if return_sd:
        sds = {m: (statistics.pstdev([get(k, m) for k in ks]) / max(1, len(ks)) ** 0.5) for m in METRICS}
        return means, sds
    return means


def loss(f, targets, mults, lam, seeds, bounds=None):
    out = run(f, seeds)
    err = sum(t.get("weight", 1) * ((out[t["metric"]] - t["actual"]) / max(1e-9, abs(t["actual"]))) ** 2 for t in targets)
    # 규제: 경계 폭으로 정규화 ((m−1)/bound)² — 경계 끝에서 λ 만큼 벌점. λ 기본 0.02 (오차 항 ~0.01 수준과 균형)
    reg = lam * sum(((m - 1) / (bounds[p] if bounds else 0.3)) ** 2 for p, m in mults.items())
    return err + reg, out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("factory"); ap.add_argument("--targets", required=True); ap.add_argument("--params", nargs="+", required=True)
    ap.add_argument("--holdout", default="[]"); ap.add_argument("--seeds", type=int, default=2); ap.add_argument("--lam", type=float, default=0.02); ap.add_argument("--iters", type=int, default=3); ap.add_argument("--out", default=None)
    a = ap.parse_args(); f = json.loads(pathlib.Path(a.factory).read_text(encoding="utf-8")); targets = json.loads(a.targets); holdout = json.loads(a.holdout)
    global METRICS; METRICS = sorted({t["metric"] for t in targets} | {h["metric"] for h in holdout})
    if len(a.params) > len(targets):
        print(f"경고: 조정 파라미터 {len(a.params)}개 > 보정 지표 {len(targets)}개 → 식별 불가(여러 해). 파라미터를 줄이거나 지표를 늘리세요.")
    prov = f.get("provenance", {}); mults = {p: 1.0 for p in a.params}; seeds = list(range(1, a.seeds + 1))
    bounds = {p: WIDTH.get(prov.get(p, "estimated"), 0.4) for p in a.params}
    def build(ms):
        g = f
        for q, mq in ms.items(): g = set_param(g, q, mq)
        return g
    # 사전 점검: 시뮬레이션 잡음(평균의 표준오차) vs 목표와의 차이 → 식별 가능한지
    out0, sd0 = run(f, seeds, return_sd=True)
    for t in targets:
        gap = abs(out0[t["metric"]] - t["actual"]); noise = sd0[t["metric"]]
        flag = "OK" if gap > 2 * noise else "경고: 차이가 잡음의 2배 미만 → seed 를 늘리거나 지평을 늘려야 보정 가능"
        print(f"사전점검 {t['metric']}: 명목 {out0[t['metric']]:.1f} vs 관측 {t['actual']:.1f} (차 {gap:.1f}, 평균의 se {noise:.1f}) {flag}")
    cur = f; best, out0 = loss(cur, targets, mults, a.lam, seeds, bounds); print("초기 손실", round(best, 4), {m: round(v, 1) for m, v in out0.items()})
    grid_n = 5
    for it in range(a.iters):
        improved = False
        for p in a.params:
            # 파라미터별 격자 라인서치 (경계 안 grid_n 점, 반복마다 현재값 주변으로 축소)
            w = bounds[p] / (2 ** it)
            cands = [max(1 - bounds[p], min(1 + bounds[p], mults[p] + w * (2 * i / (grid_n - 1) - 1))) for i in range(grid_n)]
            for m2 in cands:
                if abs(m2 - mults[p]) < 1e-6: continue
                ms = {**mults, p: m2}; g = build(ms)
                L, out = loss(g, targets, ms, a.lam, seeds, bounds)
                if L < best:
                    best, mults[p], cur, improved = L, m2, g, True; print(f"  iter {it + 1}: {p} ×{m2:.3f} → 손실 {L:.4f} {[round(out[t['metric']], 1) for t in targets]}")
        if not improved and it >= 1: break
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
