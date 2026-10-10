"""보정(calibration): 불확실 파라미터를 경계 안에서 조정해 보정용 검증 지표와의 오차를 줄인다.
끼워맞춤 방지 장치: (1) 조정 가능한 파라미터는 출처 등급 C/D 또는 명시 목록만, (2) 경계는 측정값 ±출처 폭, (3) 홀드아웃 지표는 목적함수에 넣지 않고 사후 판정만,
(4) 규제항(측정값에서 멀어질수록 벌점), (5) 파라미터 수 ≤ 보정 지표 수 (식별 가능성).
사용: python3 calibrate.py factory.json --targets '[{"metric":"throughput_steady_per_day","actual":85,"weight":1},{"metric":"lead_time_work_min_avg","actual":700,"weight":1}]' \
      --params CUT2.cycle EB2.cycle transport.handler_speed_mps --holdout '[{"metric":"avg_wip_batches","actual":28,"tolerance_pct":20}]'
알고리즘: 파라미터별 격자 라인서치(경계 안 5점, 반복마다 축소) + CRN seed 평균. 손실 = Σ((지표−관측)/se)² + λ·Σ((m−1)/폭)² (χ², λ=1 기본). 작은 공장 모델엔 충분; 더 정교한 방법(GP 에뮬레이터·베이지안)은 docs/research/14 참고.
"""
import json, sys, copy, pathlib, argparse, statistics
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from factory_sim import Sim
from validate import get, validate
from common import BOUND as WIDTH


def _setp(d, path, v):
    ks = path.split("."); cur = d
    for kk in ks[:-1]: cur = cur[int(kk)] if isinstance(cur, list) else cur[kk]
    if isinstance(cur, list): cur[int(ks[-1])] = v
    else: cur[ks[-1]] = v


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
                v = s[key] * mult; s[key] = max(1, int(round(v))) if isinstance(s[key], int) and key in ("buffer_batches", "capacity") else v
    return g


def run(f, seeds, return_sd=False):
    ks = [Sim(f, seed=sd).run() for sd in seeds]
    means = {m: statistics.mean(get(k, m) for k in ks) for m in METRICS}
    if return_sd:
        sds = {m: (statistics.pstdev([get(k, m) for k in ks]) / max(1, len(ks)) ** 0.5) for m in METRICS}
        return means, sds
    return means


def loss(f, targets, mults, lam, seeds, bounds=None):
    """χ² 형태: 지표 오차는 관측 표준오차(se)로, 파라미터 이동은 출처 폭(se 또는 경계)으로 정규화해 같은 눈금에 둔다.
    se 는 targets 의 "se"(절대) 또는 "se_rel"(상대) → 없으면 시뮬 평균의 표준오차(SE0, 사전점검에서 계산)를 하한으로 쓴다.
    이전 구현(상대 제곱오차 + λ=0.02 경계 벌점)은 벌점이 오차보다 커서 진짜 25% 이동도 1.0 근처로 끌려갔다(라운드트립 실패 원인)."""
    out = run(f, seeds)
    err = 0.0
    for t in targets:
        se = t.get("se") or (t.get("se_rel", 0) * abs(t["actual"])) or SE0.get(t["metric"], 0) or 0.05 * abs(t["actual"])
        se = max(se, SE0.get(t["metric"], 0))  # 시뮬 잡음보다 작은 se 는 의미 없음
        err += t.get("weight", 1) * ((out[t["metric"]] - t["actual"]) / max(1e-9, se)) ** 2
    reg = lam * sum(((m - 1) / (SCALE.get(p) or (bounds[p] if bounds else 0.3))) ** 2 for p, m in mults.items())
    return err + reg, out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("factory"); ap.add_argument("--targets", required=True); ap.add_argument("--params", nargs="+", required=True)
    ap.add_argument("--holdout", default="[]"); ap.add_argument("--seeds", type=int, default=2); ap.add_argument("--lam", type=float, default=1.0, help="χ² 눈금에서 1.0 = 출처 폭을 1σ 로 취급"); ap.add_argument("--iters", type=int, default=3); ap.add_argument("--out", default=None)
    a = ap.parse_args(); f = json.loads(pathlib.Path(a.factory).read_text(encoding="utf-8")); targets = json.loads(a.targets); holdout = json.loads(a.holdout)
    global METRICS; METRICS = sorted({t["metric"] for t in targets} | {h["metric"] for h in holdout})
    if len(a.params) > len(targets):
        print(f"중단: 조정 파라미터 {len(a.params)}개 > 보정 지표 {len(targets)}개 → 식별 불가(여러 해). 파라미터를 줄이거나 지표를 늘리세요."); return
    prov = f.get("provenance", {}); mults = {p: 1.0 for p in a.params}; seeds = list(range(1, a.seeds + 1))
    bounds = {p: WIDTH.get(prov.get(p, "estimated"), 0.4) for p in a.params}
    global SCALE; SCALE = {}
    for p in a.params:  # 측정 사이클(n 있음)은 se 로 규제 스케일
        if p.endswith(".cycle"):
            st = next((s for s in f["stations"] if s["id"] == p.split(".")[0]), None)
            if st and (st.get("cycle") or {}).get("n", 0) > 1: SCALE[p] = max(0.02, st["cycle"].get("cv", 0.3) / st["cycle"]["n"] ** 0.5 * 2)
    evaluated = []  # (손실, 배수들) → 적격 집합
    def build(ms):
        g = f
        for q, mq in ms.items(): g = set_param(g, q, mq)
        return g
    # 사전 점검: 시뮬레이션 잡음(평균의 표준오차) vs 목표와의 차이 → 식별 가능한지
    out0, sd0 = run(f, seeds, return_sd=True)
    global SE0; SE0 = dict(sd0)
    for t in targets:
        gap = abs(out0[t["metric"]] - t["actual"]); noise = sd0[t["metric"]]
        flag = "OK" if gap > 2 * noise else "경고: 차이가 잡음의 2배 미만 → seed 를 늘리거나 지평을 늘려야 보정 가능"
        print(f"사전점검 {t['metric']}: 명목 {out0[t['metric']]:.4g} vs 관측 {t['actual']:.4g} (차 {gap:.3g}, 평균의 se {noise:.3g}) {flag}")
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
                L, out = loss(g, targets, ms, a.lam, seeds, bounds); evaluated.append((L, dict(ms)))
                if L < best:
                    best, mults[p], cur, improved = L, m2, g, True; print(f"  iter {it + 1}: {p} ×{m2:.3f} → 손실 {L:.4f} {[round(out[t['metric']], 1) for t in targets]}")
        if not improved and it >= 1: break
    print("최종 배수", {k: round(v, 3) for k, v in mults.items()}, "손실", round(best, 4))
    elig = [ms for L, ms in evaluated if L <= best + 2 + 1e-9]  # χ² 눈금: 최소 +2 이내(≈1σ) 가 적격
    print(f"적격 집합(손실 ≤ 최소+2): {len(elig)}개 조합 — 파라미터별 범위:", {p: (round(min(ms[p] for ms in elig), 3), round(max(ms[p] for ms in elig), 3)) for p in a.params} if elig else "-")
    for p in a.params:
        if abs(mults[p] - 1) >= bounds[p] - 1e-9: print(f"  주의: {p} 가 경계({bounds[p]:.0%})에 닿음 → 구조 오류 의심(측정 재확인)")
    if holdout:
        hk = [Sim(cur, seed=90 + i).run() for i in range(3)]  # 홀드아웃은 3회 평균
        ks = hk[0]
        for m in METRICS:
            try:
                vals = [get(x, m) for x in hk]
                if all(isinstance(v, (int, float)) for v in vals): _setp(ks, m, sum(vals) / len(vals))
            except Exception: pass
        ok, rows = validate(ks, holdout)
        print("홀드아웃 판정:", "통과" if ok else "실패"); [print("  ", r) for r in rows]
    if a.out:
        cur["calibration"] = {"multipliers": mults, "targets": targets, "loss": best}
        pathlib.Path(a.out).write_text(json.dumps(cur, ensure_ascii=False, indent=1), encoding="utf-8"); print("wrote", a.out)


if __name__ == "__main__":
    main()
