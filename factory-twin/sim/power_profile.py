"""이벤트 로그 → 15분 전력 프로파일 → 피크·시간대 요금 (common.energy_from_events 와 단일 경로).
meta.energy 설정:
  tariff_class: "산업용(갑)I 저압" | "산업용(갑)I 고압A" | "산업용(갑)II 고압A" | "산업용(을) 고압A"  (300 kW 미만은 (갑); 저압 (갑)I 는 계시별 아님)
  contract_kw, pf (평균 역률, 기본 0.9), tou: {
    "season_of_month": {"summer":[7,8],"winter":[12,1,2]},   # 그 외 봄·가을
    "hours": {"off":[[22,8]], "mid":[[8,18],[21,22]], "peak":[[18,21]]},     # 2026-04-16 개편 구조 [원문 확인 필요]
    "rates": {"summer":{"off":..,"mid":..,"peak":..}, "winter":{...}, "spring_fall":{...}},   # 원/kWh, 요금표 원문으로 교체
    "flat": 116.2,                       # 계시별이 아닌 종별(저압 (갑)I)의 단일 단가
    "demand_krw_per_kw": {"I":7220,"II":8320,"III":9810},  # 선택요금별 기본요금 (또는 숫자 하나)
    "rate_option": "II", "weekend_discount": {"months":[3,4,5,6,9,10,11], "hours":[11,14], "ratio":0.5},
    "climate_krw": 9, "fuel_adj_krw": 5, "vat": 0.10, "fund": 0.027, "overage_multiplier": 1.5 }
출력: power_15min.csv, power_summary.json  (요금적용전력은 시뮬 기간 내 최대수요로 근사 — 실제는 직전 11개월 하계·동계 최대 [미구현 표기])"""
import json, sys, pathlib, csv, collections
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from common import energy_from_events, Calendar


def band_of(hour, hours):
    for b, ranges in hours.items():
        for a, c in ranges:
            if (a <= hour < c) if a < c else (hour >= a or hour < c):
                return b
    return "mid"


def main(outdir, start_month=10):
    outdir = pathlib.Path(outdir)
    f = json.loads((outdir / "factory.json").read_text(encoding="utf-8"))
    evs = [json.loads(l) for l in open(outdir / "events.jsonl", encoding="utf-8")]
    horizon = max(e["t"] for e in evs) + 1
    per, total, slots = energy_from_events(f, evs, horizon)
    en = f["meta"].get("energy", {}); tou = en.get("tou") or {}; cal = Calendar(f["meta"]["shift"])
    tclass = en.get("tariff_class", "산업용(을) 고압A" if en.get("contract_kw", 0) >= 300 else "산업용(갑)II 고압A")
    tou_based = "저압" not in tclass and bool(tou.get("rates"))
    seasons = tou.get("season_of_month", {"summer": [7, 8], "winter": [12, 1, 2]})
    def season(month): return "summer" if month in seasons["summer"] else ("winter" if month in seasons["winter"] else "spring_fall")
    wd_disc = tou.get("weekend_discount", {"months": [3, 4, 5, 6, 9, 10, 11], "hours": [11, 14], "ratio": 0.5})
    energy_cost = 0.0; by_band = collections.defaultdict(float); kwh_total = 0.0
    for k in range(slots):
        kwh = total[k] * 0.25; kwh_total += kwh
        day = (k * 15) // 1440; hour = ((k * 15) % 1440) / 60; wd = day % 7
        month = ((start_month - 1 + day // 30) % 12) + 1  # 근사: 시작 월 + 30일/월
        if tou_based:
            b = band_of(hour, tou.get("hours", {"off": [[22, 8]], "mid": [[8, 18], [21, 22]], "peak": [[18, 21]]}))
            if wd == 6: b = "off"  # 일요일·공휴일 전일 경부하 (개편 보도 기준) [원문 확인 필요]
            elif wd == 5 and b == "peak": b = "mid"  # 토요일 최대부하 없음
            rate = tou["rates"][season(month)][b]
            if wd >= 5 and month in wd_disc["months"] and wd_disc["hours"][0] <= hour < wd_disc["hours"][1]: rate *= (1 - wd_disc["ratio"])
            by_band[b] += kwh; energy_cost += kwh * rate
        else:
            rate = tou.get("flat", en.get("tariff_krw_per_kwh", 160)); by_band["flat"] += kwh; energy_cost += kwh * rate
    peak = max(total); peak_k = total.index(peak); days = horizon / 1440
    contract = en.get("contract_kw", 0) or 0
    billing_kw = max(peak, contract * 0.3)  # 요금적용전력 ≈ 기간 내 최대수요 (실제: 직전 11개월 하계·동계 최대, 미구현)
    dem = tou.get("demand_krw_per_kw", 0); opt = tou.get("rate_option", "II")
    dem_rate = dem[opt] if isinstance(dem, dict) else dem
    months = days / 30
    demand_charge = dem_rate * billing_kw * months
    overage = max(0.0, peak - contract) if contract else 0.0
    overage_charge = overage * dem_rate * (tou.get("overage_multiplier", 1.5) - 1) * months if overage > 0 else 0.0
    pf = en.get("pf", 0.9); pf_adj = 0.0
    if pf < 0.9: pf_adj = (0.9 - pf) * 100 * 0.002 * demand_charge
    elif pf > 0.9: pf_adj = -min(0.05, pf - 0.9) * 100 * 0.002 * demand_charge
    addons = kwh_total * (tou.get("climate_krw", 9) + tou.get("fuel_adj_krw", 5))
    subtotal = energy_cost + demand_charge + overage_charge + pf_adj + addons
    bill = subtotal * (1 + tou.get("vat", 0.10)) + subtotal * tou.get("fund", 0.027)
    # 선택요금 I/II/III 동시 비교 (기본요금만 다르고 전력량 단가 차이는 미반영 [요금표 원문 필요])
    options = {o: round(r * billing_kw * months + energy_cost) for o, r in dem.items()} if isinstance(dem, dict) else None
    summary = {"tariff_class": tclass, "tou_based": tou_based, "peak_kw": round(peak, 1), "peak_at": f"Day {peak_k * 15 // 1440 + 1} {int((peak_k * 15) % 1440 // 60):02d}:{int((peak_k * 15) % 60):02d}",
               "contract_kw": contract, "billing_kw_est": round(billing_kw, 1), "overage_kw": round(overage, 1),
               "kwh_total": round(kwh_total), "kwh_by_band": {k: round(v) for k, v in by_band.items()}, "days": round(days, 1),
               "energy_charge_krw": round(energy_cost), "demand_charge_krw": round(demand_charge), "overage_charge_krw": round(overage_charge),
               "pf": pf, "pf_adjust_krw": round(pf_adj), "addons_krw": round(addons), "bill_est_krw": round(bill),
               "rate_option_compare_krw": options,
               "top_contributors_at_peak": sorted(((sid, round(v[peak_k], 1)) for sid, v in per.items()), key=lambda x: -x[1])[:6],
               "notes": ["요금적용전력은 기간 내 최대수요로 근사(실제: 직전 11개월 하계·동계 최대)", "월은 시작 월 + 30일 단위 근사", "단가는 설정 파일 값 — 한전 요금표 원문으로 교체"]}
    with open(outdir / "power_15min.csv", "w", newline="", encoding="utf-8") as fp:
        w = csv.writer(fp); w.writerow(["slot", "day", "hhmm", "total_kw"] + list(per.keys()))
        for k in range(slots):
            w.writerow([k, k * 15 // 1440 + 1, f"{int((k * 15) % 1440 // 60):02d}:{int((k * 15) % 60):02d}", round(total[k], 2)] + [round(v[k], 2) for v in per.values()])
    (outdir / "power_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("tariff_class", "peak_kw", "kwh_total", "energy_charge_krw", "demand_charge_krw", "bill_est_krw", "rate_option_compare_krw")}, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(pathlib.Path(__file__).parent / "out/baseline"), int(sys.argv[2]) if len(sys.argv) > 2 else 10)
