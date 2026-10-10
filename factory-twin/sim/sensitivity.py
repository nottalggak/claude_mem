"""민감도 스크리닝(OAT): 주요 파라미터를 ±20% 흔들어 출하량·리드타임·병목 변화를 측정하고 영향 순위를 낸다.
→ 순위 상위 파라미터가 2주 로깅·2차 방문에서 다시 재야 할 것들이다 (03_공장복제_명세서 §6-5)."""
import json, sys, copy, pathlib, statistics, argparse
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from factory_sim import Sim

ROOT = pathlib.Path(__file__).parent.parent


def run(f, seeds):
    tp, lt, bn = [], [], []
    for sd in seeds:
        k = Sim(f, seed=sd).run()
        tp.append(k["throughput_steady_per_day"]); lt.append(k["lead_time_work_min_avg"]); bn.append(k["bottleneck_ranking"][0]["station"])
    return statistics.mean(tp), statistics.mean(lt), max(set(bn), key=bn.count)


def params(f):
    """(이름, getter, setter) 목록: 스테이션 사이클·셋업·MTTR·버퍼, 운반 인원·속도, 부대설비"""
    out = []
    for s in f["stations"]:
        if s["process"] in ("raw", "fg"):
            continue
        sid = s["id"]
        if s.get("cycle"):
            out.append((f"{sid}.cycle(가공시간)", lambda f, sid=sid: 1.0, lambda f, m, sid=sid: _scale_cycle(f, sid, m)))
        if s.get("batch_time_min"):
            out.append((f"{sid}.batch_time(배치시간)", None, lambda f, m, sid=sid: _set(f, sid, "batch_time_min", m)))
        if s.get("setup_min"):
            out.append((f"{sid}.setup(셋업)", None, lambda f, m, sid=sid: _set(f, sid, "setup_min", m)))
        if s.get("mttr_min"):
            out.append((f"{sid}.mttr(수리시간)", None, lambda f, m, sid=sid: _set(f, sid, "mttr_min", m)))
        out.append((f"{sid}.buffer(버퍼용량)", None, lambda f, m, sid=sid: _set(f, sid, "buffer_batches", m, integer=True)))
    out.append(("transport.handler_speed(운반속도)", None, lambda f, m: f["transport"].__setitem__("handler_speed_mps", f["transport"]["handler_speed_mps"] * m)))
    out.append(("transport.load_unload(적재하역)", None, lambda f, m: f["transport"].__setitem__("load_unload_min", f["transport"]["load_unload_min"] * m)))
    out.append(("orders.batch_size(배치크기)", None, lambda f, m: f["orders"].__setitem__("batch_size", {k: max(1, round(v * m)) for k, v in f["orders"]["batch_size"].items()})))
    return out


def _set(f, sid, key, m, integer=False):
    for s in f["stations"]:
        if s["id"] == sid:
            v = s[key] * m; s[key] = max(1, round(v)) if integer else v


def _scale_cycle(f, sid, m):
    for s in f["stations"]:
        if s["id"] == sid and s.get("cycle"):
            c = s["cycle"]; c["base_min"] = c.get("base_min", 0) * m
            c["per_unit"] = {k: v * m for k, v in c.get("per_unit", {}).items()}
            if "per_product" in c:
                c["per_product"] = {k: v * m for k, v in c["per_product"].items()}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--factory", default=str(ROOT / "data/sample_factory.json")); ap.add_argument("--seeds", type=int, default=3); ap.add_argument("--delta", type=float, default=0.2)
    a = ap.parse_args(); base = json.loads(pathlib.Path(a.factory).read_text(encoding="utf-8")); seeds = list(range(1, a.seeds + 1))
    tp0, lt0, bn0 = run(base, seeds)
    rows = []
    for name, _, setter in params(base):
        eff = {}
        for m in (1 - a.delta, 1 + a.delta):
            f = copy.deepcopy(base); setter(f, m); tp, lt, bn = run(f, seeds)
            eff[m] = ((tp - tp0) / tp0 * 100, (lt - lt0) / lt0 * 100, bn)
        rng_tp = abs(eff[1 + a.delta][0] - eff[1 - a.delta][0]); rng_lt = abs(eff[1 + a.delta][1] - eff[1 - a.delta][1])
        rows.append((rng_tp + rng_lt, name, rng_tp, rng_lt, eff[1 - a.delta][2], eff[1 + a.delta][2]))
    rows.sort(reverse=True)
    out = ["# 민감도 스크리닝 (±%d%%, seed %d회)" % (a.delta * 100, len(seeds)), "", f"베이스라인: 처리량 {tp0:.1f}/일, 리드타임 {lt0:.0f}분, 병목 {bn0}", "",
           "| 순위 | 파라미터 | 처리량 변동폭(%p) | 리드타임 변동폭(%p) | 병목(−20%) | 병목(+20%) | 재측정 우선순위 |", "|---|---|---|---|---|---|---|"]
    for i, (score, name, rtp, rlt, b0, b1) in enumerate(rows, 1):
        pri = "높음" if i <= 10 else ("중간" if i <= 20 else "낮음(추정 유지 가능)")
        out.append(f"| {i} | {name} | {rtp:.1f} | {rlt:.1f} | {b0} | {b1} | {pri} |")
    out += ["", "해석: 변동폭이 큰 파라미터일수록 측정 오차가 결론을 바꾼다. 상위 10개는 2주 로깅·2차 방문에서 표본을 늘려 다시 잰다. 하위는 추정으로 둬도 결론이 흔들리지 않는다."]
    (ROOT / "sim/out/sensitivity.md").write_text("\n".join(out), encoding="utf-8"); print("\n".join(out[:20]))


if __name__ == "__main__":
    main()
