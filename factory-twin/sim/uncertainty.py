"""입력 불확실성 부트스트랩: 파라미터 추정 오차(표본 수 n, 또는 출처 등급)를 흔들어
시나리오 효과(Δ처리량·Δ리드타임·Δ납기준수율)의 분포 → 신뢰구간과 P(개선) 을 낸다.
- 측정 파라미터(cycle.n 있음): 평균의 표준오차 se = cv·mean/√n 로 정규 재표집 (평균의 파라메트릭 부트스트랩)
- 추정 파라미터(n 없음): 출처 등급별 폭으로 균등 재표집 (estimated ±30%, interview ±20%, record ±10%)
- 공통난수(CRN): 같은 부트스트랩 복제에서 베이스라인과 시나리오를 같은 seed 로 실행해 짝 비교
결과: sim/out/uncertainty.md
"""
import json, sys, copy, pathlib, random, statistics, argparse
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from factory_sim import Sim, apply_scenario
ROOT = pathlib.Path(__file__).parent.parent
WIDTH = {"measured": None, "record": 0.10, "interview": 0.20, "estimated": 0.30}


def perturb(f, rng):
    g = copy.deepcopy(f); prov = f.get("provenance", {})
    for s in g["stations"]:
        if s["process"] in ("raw", "fg"):
            continue
        c = s.get("cycle")
        if c:
            n = c.get("n"); tag = prov.get(f"{s['id']}.cycle", "measured" if n else "estimated")
            if n and n > 1:
                m = 1 + rng.gauss(0, (c.get("cv", 0.3)) / (n ** 0.5))
            else:
                w = WIDTH.get(tag, 0.3); m = 1 + rng.uniform(-w, w)
            c["base_min"] = c.get("base_min", 0) * m; c["per_unit"] = {k: v * m for k, v in c.get("per_unit", {}).items()}
            if "per_product" in c: c["per_product"] = {k: v * m for k, v in c["per_product"].items()}
        for key in ("setup_min", "mttr_min"):
            if s.get(key):
                w = WIDTH.get(prov.get(f"{s['id']}.{key}", "estimated"), 0.3) or 0.1
                s[key] = s[key] * (1 + rng.uniform(-w, w))
        if s.get("availability"):
            s["availability"] = min(1.0, s["availability"] * (1 + rng.uniform(-0.05, 0.05)))
    tr = g["transport"]; w = WIDTH.get(prov.get("transport.handler_speed_mps", "estimated"), 0.3) or 0.1
    tr["handler_speed_mps"] *= (1 + rng.uniform(-w, w)); tr["load_unload_min"] *= (1 + rng.uniform(-w, w))
    return g


def kpi(f, seed):
    k = Sim(f, seed=seed).run()
    return {"tp": k["throughput_steady_per_day"], "lead": k["lead_time_work_min_avg"], "ot": (k["on_time_ratio"] if k.get("on_time_ratio") is not None else 1.0) * 100, "bn": k["bottleneck_ranking"][0]["station"]}


def ci(xs, a=0.05):
    xs = sorted(xs); n = len(xs)
    return xs[int(a / 2 * (n - 1))], xs[int((1 - a / 2) * (n - 1))]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--factory", default=str(ROOT / "data/sample_factory.json")); ap.add_argument("--B", type=int, default=10); ap.add_argument("--scenarios", nargs="*", default=None)
    a = ap.parse_args(); base = json.loads(pathlib.Path(a.factory).read_text(encoding="utf-8"))
    files = sorted((ROOT / "scenarios").glob("*.json")); scns = [json.loads(p.read_text(encoding="utf-8")) for p in files]
    if a.scenarios: scns = [s for s in scns if s["id"] in a.scenarios]
    rng = random.Random(42); rows = {s["id"]: [] for s in scns}; names = {s["id"]: s["name"] for s in scns}
    for b in range(a.B):
        fb = perturb(base, rng); seed = 100 + b
        k0 = kpi(fb, seed)
        for s in scns:
            k1 = kpi(apply_scenario(fb, s), seed)
            rows[s["id"]].append({"dtp": (k1["tp"] - k0["tp"]) / max(1e-9, k0["tp"]) * 100, "dlead": (k1["lead"] - k0["lead"]) / max(1e-9, k0["lead"]) * 100, "dot": k1["ot"] - k0["ot"], "bn": k1["bn"]})
        print(f"bootstrap {b + 1}/{a.B} done", flush=True)
    out = [f"# 시나리오 효과의 불확실성 (입력 부트스트랩 B={a.B}, CRN 짝 비교)", "",
           "입력 파라미터를 표본 오차(측정)·출처 폭(추정)만큼 흔들어 베이스라인과 시나리오를 같은 seed 로 돌린 차이의 분포. **P(개선)이 0.9 미만이면 그 결론은 데이터를 더 모은 뒤에 말한다.**", "",
           "| 시나리오 | Δ처리량 % (평균, 95% 구간) | P(처리량↑) | Δ리드타임 % | P(리드타임↓) | Δ납기준수율 %p | P(납기↑) | 병목(최빈) |", "|---|---|---|---|---|---|---|---|"]
    for sid, rs in rows.items():
        d1 = [r["dtp"] for r in rs]; d2 = [r["dlead"] for r in rs]; d3 = [r["dot"] for r in rs]; bns = [r["bn"] for r in rs]
        c1, c2, c3 = ci(d1), ci(d2), ci(d3)
        out.append(f"| {names[sid]} | {statistics.mean(d1):+.1f} ({c1[0]:+.1f}, {c1[1]:+.1f}) | {sum(x > 0 for x in d1) / len(d1):.2f} | {statistics.mean(d2):+.1f} ({c2[0]:+.1f}, {c2[1]:+.1f}) | {sum(x < 0 for x in d2) / len(d2):.2f} | {statistics.mean(d3):+.1f} ({c3[0]:+.1f}, {c3[1]:+.1f}) | {sum(x > 0 for x in d3) / len(d3):.2f} | {max(set(bns), key=bns.count)} ({bns.count(max(set(bns), key=bns.count)) / len(bns):.0%}) |")
    out += ["", "해석: 구간이 0을 걸치면 입력 데이터의 정밀도가 결론을 지지하지 못하는 것. 어느 입력이 구간을 넓히는지는 sensitivity.md 상위 항목을 재측정해 B 를 다시 돌려 확인한다."]
    (ROOT / "sim/out/uncertainty.md").write_text("\n".join(out), encoding="utf-8"); print("\n".join(out))


if __name__ == "__main__":
    main()
