"""이벤트 로그 → 15분 전력 프로파일 → 피크 kW·시간대별 요금.
- 기계 상태(state 이벤트: busy/setup/idle/down)별 kW = 정격×부하율(busy,setup) / 대기전력(idle,down)
- 부대설비: when_any_on(연결 기계 중 하나라도 busy/setup) / shift(근무시간) / always
- 기본부하: 근무시간 내 base_load_kw
- 요금: meta.energy.tou (없으면 단일 단가). tou 형식:
  {"demand_krw_per_kw": 8320, "bands": {"off": 90, "mid": 130, "peak": 190}, "hours": {"off": [[22,8]], "mid": [[8,18],[21,22]], "peak": [[18,21]]}, "weekend_mid_discount": 0.5}
  ※ 실제 2026 요율은 한전 요금표 원문으로 교체 (docs/research/16 참고)
출력: sim/out/<scenario>/power_15min.csv, power_summary.json
"""
import json, sys, pathlib, csv, collections


def band_of(hour, hours):
    for b, ranges in hours.items():
        for a, c in ranges:
            if (a <= hour < c) if a < c else (hour >= a or hour < c):
                return b
    return "mid"


def main(outdir):
    outdir = pathlib.Path(outdir)
    f = json.loads((outdir / "factory.json").read_text(encoding="utf-8"))
    evs = [json.loads(l) for l in open(outdir / "events.jsonl", encoding="utf-8")]
    sh = f["meta"]["shift"]; s0 = int(sh["start"][:2]) * 60 + int(sh["start"][3:]); s1 = int(sh["end"][:2]) * 60 + int(sh["end"][3:])
    horizon = max(e["t"] for e in evs) + 1; slots = int(horizon // 15) + 1
    spec = {s["id"]: s for s in f["stations"]}
    # 상태 타임라인
    state_ev = collections.defaultdict(list)
    for e in evs:
        if e["type"] == "state":
            state_ev[e["station"]].append((e["t"], e["state"]))
    per_slot = collections.defaultdict(lambda: [0.0] * slots)
    on_any = collections.defaultdict(lambda: [False] * slots)
    def working(k):
        m = (k * 15) % 1440; d = (k * 15) // 1440
        return d % 7 < 5 and s0 <= m < s1
    for sid, lst in state_ev.items():
        sp = spec[sid]; lst.sort(); cur = "idle"; t_prev = 0.0
        lst.append((horizon, cur))
        for t, st in lst:
            # [t_prev, t) 구간 cur 상태
            a, b = int(t_prev // 15), int(t // 15)
            for k in range(a, min(b + 1, slots)):
                lo, hi = max(t_prev, k * 15), min(t, (k + 1) * 15)
                if hi > lo:
                    # 가동/셋업: 정격×부하율. 대기: 근무시간에만 대기전력(야간·주말은 전원 OFF 가정)
                    p = sp.get("rated_kw", 0) * sp.get("load_factor", 0.6) if cur in ("busy", "setup") else (sp.get("idle_kw", 0) if working(k) else 0.0)
                    per_slot[sid][k] += p * (hi - lo) / 15
                    if cur in ("busy", "setup"):
                        for aid in sp.get("ancillary", []): on_any[aid][k] = True
            t_prev, cur = t, st
    for a in f.get("ancillary", []):
        for k in range(slots):
            on = (on_any[a["id"]][k] if a["mode"] == "when_any_on" else (working(k) if a["mode"] == "shift" else True))
            per_slot[a["id"]][k] = a["rated_kw"] * a.get("load_factor", 0.7) if on else 0.0
    base = f["meta"].get("energy", {}).get("base_load_kw", 0)
    for k in range(slots):
        per_slot["BASE"][k] = base if working(k) else base * 0.2
    total = [sum(v[k] for v in per_slot.values()) for k in range(slots)]
    en = f["meta"].get("energy", {}); tou = en.get("tou")
    cost = 0.0; by_band = collections.defaultdict(float)
    for k in range(slots):
        kwh = total[k] * 0.25; hour = ((k * 15) % 1440) / 60; wd = (k * 15) // 1440 % 7
        if tou:
            b = band_of(hour, tou["hours"]); rate = tou["bands"][b]
            if wd >= 5 and b == "mid" and tou.get("weekend_mid_discount"): rate *= (1 - tou["weekend_mid_discount"])
            by_band[b] += kwh; cost += kwh * rate
        else:
            cost += kwh * en.get("tariff_krw_per_kwh", 160); by_band["flat"] += kwh
    peak = max(total); peak_k = total.index(peak)
    days = horizon / 1440
    demand_charge = (tou or {}).get("demand_krw_per_kw", 0) * max(peak, en.get("contract_kw", 0) * 0.3) * (days / 30)
    summary = {"peak_kw": round(peak, 1), "peak_at": f"Day {peak_k * 15 // 1440 + 1} {int((peak_k * 15) % 1440 // 60):02d}:{int((peak_k * 15) % 60):02d}",
               "contract_kw": en.get("contract_kw"), "peak_over_contract": round(peak / en["contract_kw"], 2) if en.get("contract_kw") else None,
               "kwh_total": round(sum(total) * 0.25), "kwh_by_band": {k: round(v) for k, v in by_band.items()},
               "energy_cost_krw": round(cost), "demand_charge_krw_est": round(demand_charge), "days": round(days, 1),
               "top_contributors_at_peak": sorted(((sid, round(v[peak_k], 1)) for sid, v in per_slot.items()), key=lambda x: -x[1])[:6]}
    with open(outdir / "power_15min.csv", "w", newline="", encoding="utf-8") as fp:
        w = csv.writer(fp); w.writerow(["slot", "day", "hhmm", "total_kw"] + list(per_slot.keys()))
        for k in range(slots):
            w.writerow([k, k * 15 // 1440 + 1, f"{int((k * 15) % 1440 // 60):02d}:{int((k * 15) % 60):02d}", round(total[k], 2)] + [round(v[k], 2) for v in per_slot.values()])
    (outdir / "power_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(pathlib.Path(__file__).parent / "out/baseline"))
