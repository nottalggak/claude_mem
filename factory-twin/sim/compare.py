"""모든 시나리오를 여러 seed 로 실행하고 비교표(markdown/json) + 뷰어용 index.json 생성."""
import json, pathlib, statistics, sys, argparse
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from factory_sim import Sim, apply_scenario

ROOT = pathlib.Path(__file__).parent.parent


def run(factory, name, desc, seeds, outdir, extra=None):
    runs = []
    for sd in seeds:
        sim = Sim(factory, seed=sd)
        k = sim.run(); runs.append((sim, k))
    sim, k = runs[0]  # 대표 run (seed[0]) 을 뷰어용으로 저장
    k["scenario"] = {"id": name, "name": desc, **(extra or {})}
    agg = {}
    def m(fn):
        vals = [fn(r[1]) for r in runs]; return round(statistics.mean(vals), 1), round(statistics.pstdev(vals), 1)
    agg["throughput_per_day"] = m(lambda x: x["throughput_steady_per_day"])
    agg["on_time"] = m(lambda x: 100 * (x["on_time_ratio"] if x.get("on_time_ratio") is not None else 1.0))
    agg["lead_work_min"] = m(lambda x: x["lead_time_work_min_avg"])
    agg["lead_cal_min"] = m(lambda x: x["lead_time_min"]["avg"])
    agg["wip"] = m(lambda x: x["avg_wip_batches"])
    agg["energy_kwh"] = m(lambda x: x["energy"]["total_kwh"])
    agg["kwh_per_product"] = m(lambda x: x["energy"]["kwh_per_product"])
    agg["distance_per_product_m"] = m(lambda x: x["transport"]["distance_per_product_m"])
    agg["completed_ratio"] = m(lambda x: 100 * (x["completed_of_due"] if x.get("completed_of_due") is not None else x["orders_completed"] / max(1, x["orders_released"])))
    bns = [r[1]["bottleneck_ranking"][0]["station"] for r in runs]
    agg["bottleneck"] = max(set(bns), key=bns.count); agg["bottleneck_freq"] = round(bns.count(agg["bottleneck"]) / len(bns), 2)
    agg["bottleneck_util"] = m(lambda x: 100 * x["bottleneck_ranking"][0]["utilization"])
    # 제품당 공헌이익(추정): 판매가 × 마진율, 주문 믹스 가중
    fin = factory["meta"].get("finance", {}); mix = factory["orders"].get("mix", {})
    price = sum(p.get("price_krw", 0) * mix.get(p["id"], 0) for p in factory["products"]) / max(1e-9, sum(mix.values()))
    agg["margin_per_product_krw"] = round(price * fin.get("margin_rate", 0.25))
    agg["working_days_per_year"] = fin.get("working_days_per_year", 250)
    k["aggregate"] = {kk: list(v) if isinstance(v, tuple) else v for kk, v in agg.items()}
    d = outdir / name; d.mkdir(parents=True, exist_ok=True)
    with open(d / "events.jsonl", "w", encoding="utf-8") as fp:
        for e in sim.events:
            fp.write(json.dumps(e, ensure_ascii=False) + "\n")
    (d / "kpis.json").write_text(json.dumps(k, ensure_ascii=False, indent=1), encoding="utf-8")
    (d / "factory.json").write_text(json.dumps(factory, ensure_ascii=False), encoding="utf-8")
    return agg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--factory", default=str(ROOT / "data/sample_factory.json"))
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--out", default=str(ROOT / "sim/out"))
    a = ap.parse_args()
    base = json.loads(pathlib.Path(a.factory).read_text(encoding="utf-8"))
    seeds = list(range(1, a.seeds + 1)); outdir = pathlib.Path(a.out)
    results = [("baseline", "현재 상태 (Baseline)", run(base, "baseline", "현재 상태 (Baseline)", seeds, outdir, {"capex_krw": 0}))]
    index = [{"id": "baseline", "name": "현재 상태 (Baseline)"}]
    for sp in sorted((ROOT / "scenarios").glob("*.json")):
        scn = json.loads(sp.read_text(encoding="utf-8"))
        f = apply_scenario(base, scn)
        agg = run(f, scn["id"], scn["name"], seeds, outdir, {"capex_krw": scn.get("capex_krw", 0), "hypothesis": scn.get("hypothesis", "")})
        agg["capex"] = scn.get("capex_krw", 0)
        base_tp = results[0][2]["throughput_per_day"][0]
        gain_year = (agg["throughput_per_day"][0] - base_tp) * agg["margin_per_product_krw"] * agg["working_days_per_year"]
        energy_year = (results[0][2]["energy_kwh"][0] - agg["energy_kwh"][0]) / base.get("orders", {}).get("horizon_days", 5) * agg["working_days_per_year"] * base["meta"].get("energy", {}).get("tariff_krw_per_kwh", 160)
        agg["annual_gain_krw"] = round(gain_year + energy_year)
        agg["payback_years"] = round(scn.get("capex_krw", 0) / gain_year, 1) if gain_year > 0 and scn.get("capex_krw", 0) > 0 else (0 if scn.get("capex_krw", 0) == 0 else None)
        results.append((scn["id"], scn["name"], agg)); index.append({"id": scn["id"], "name": scn["name"]})
    (outdir / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    # 비교표
    b = results[0][2]
    lines = ["# 시나리오 비교 (seed %d회 평균 ± 표준편차)" % len(seeds), "",
             "| 시나리오 | 처리량/일(정상상태) | 납기준수율% | 작업시간 기준 리드타임(분) | 평균 WIP(배치) | 운반거리/제품(m) | kWh/제품 | 병목 (가동률%) | 기한내 주문 완료율% | CAPEX(만원) | 연간 효과(만원, 추정) | 회수기간(년) |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for sid, name, g in results:
        def cell(key, lower_better=None):
            v, s = g[key]; bv = b[key][0]
            d = "" if sid == "baseline" or bv == 0 else f" ({(v - bv) / bv * 100:+.0f}%)"
            return f"{v}±{s}{d}"
        lines.append(f"| {name} | {cell('throughput_per_day')} | {g['on_time'][0]:.0f} | {cell('lead_work_min')} | {cell('wip')} | {cell('distance_per_product_m')} | "
                     f"{cell('kwh_per_product')} | {g['bottleneck']} ({g['bottleneck_util'][0]:.0f}, 1위빈도 {g.get('bottleneck_freq', 1):.0%}) | {g['completed_ratio'][0]} | {g.get('capex', 0) // 10000:,} | "
                     f"{(g.get('annual_gain_krw', 0) // 10000):,} | {g.get('payback_years') if g.get('payback_years') is not None else '효과 없음'} |")
    lines += ["", "해석 가이드:", "- 처리량/완료율이 오르고 리드타임·WIP가 줄면 병목이 해소된 것. 병목 열이 바뀌면 병목이 '이동'한 것(다음 투자 대상).",
              "- 연간 효과 = (정상상태 처리량 증가 × 제품당 공헌이익 × 연 근무일) + 전력비 절감. 회수기간 = CAPEX / 연간 효과. 시공일 역산 투입(수요 고정)에서는 처리량이 거의 안 변하고 **납기준수율·리드타임·WIP** 가 비교 축이다.",
              "- 모든 수치는 샘플(가상) 공장 기본값 기준. 현장 측정값으로 교체 후 재실행."]
    (outdir / "comparison.md").write_text("\n".join(lines), encoding="utf-8")
    (outdir / "comparison.json").write_text(json.dumps([{"id": s, "name": n, **g} for s, n, g in results], ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
