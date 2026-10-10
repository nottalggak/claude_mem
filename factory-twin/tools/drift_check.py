"""트윈 드리프트 점검(연구 21 §1-3·§2-2): 주간 KPI 실측−트윈 예측 잔차에 CUSUM + EWMA 를 걸어 재보정·재구성 트리거를 낸다.
입력 CSV 열: week, kpi, actual, predicted[, band_lo, band_hi]  (predicted 는 그 주 실제 주문 스트림을 넣고 돌린 트윈의 평균; band 는 90% 예측대 = 복제 CI + 입력 불확실성)
규칙: σ 는 보정 직후 첫 8주(--baseline-weeks) 잔차의 표준편차. CUSUM 허용치 k=0.5σ, 결정구간 h=4σ; EWMA λ=0.2, 한계 3σ·sqrt(λ/(2−λ)).
     두 탐지기 동시 경보 또는 월간(4주) 평균이 2개월 연속 예측대 밖, **그리고** 최근 4주 평균 잔차 ≥ 1σ → '재보정'(자체 검증: 드리프트 없는 KPI 가 8주 σ 과소추정으로 오경보 났던 것을 이 조건이 거른다). 변경 로그(changes.jsonl)에 구조 항목이 있으면 → '재구성'.
사용: python3 tools/drift_check.py residuals.csv [--changes changes.jsonl] [--baseline-weeks 8]"""
import csv, json, sys, argparse, pathlib, statistics, math


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("csv"); ap.add_argument("--changes"); ap.add_argument("--baseline-weeks", type=int, default=8); ap.add_argument("--k", type=float, default=0.5); ap.add_argument("--h", type=float, default=4.0); ap.add_argument("--lam", type=float, default=0.2)
    a = ap.parse_args()
    rows = list(csv.DictReader(open(a.csv, encoding="utf-8")))
    by = {}
    for r in rows: by.setdefault(r["kpi"], []).append(r)
    print("| KPI | 주 수 | 기준 σ(잔차) | CUSUM 경보(주) | EWMA 경보(주) | 최근 4주 평균 잔차 | 예측대 이탈(최근 8주 중 월 단위) | 판정 |"); print("|---|---|---|---|---|---|---|---|")
    any_recal = False
    for kpi, rs in by.items():
        rs.sort(key=lambda r: int(r["week"])); res = [float(r["actual"]) - float(r["predicted"]) for r in rs]
        base = res[:a.baseline_weeks]
        if len(base) < 4: print(f"| {kpi} | {len(rs)} | — | — | — | — | — | 기준 주 부족(<4) |"); continue
        sigma = statistics.pstdev(base) or 1e-9; mu0 = statistics.mean(base)
        # CUSUM (양측) — 기준 구간 이후부터 누적
        sp = sn = 0.0; c_alarm = []; e = mu0; e_alarm = []; L = 3 * sigma * math.sqrt(a.lam / (2 - a.lam))
        for i, x in enumerate(res):
            if i < a.baseline_weeks: continue
            z = x - mu0
            sp = max(0.0, sp + z - a.k * sigma); sn = max(0.0, sn - z - a.k * sigma)
            if sp > a.h * sigma or sn > a.h * sigma: c_alarm.append(int(rs[i]["week"])); sp = sn = 0.0
            e = a.lam * x + (1 - a.lam) * e
            if abs(e - mu0) > L: e_alarm.append(int(rs[i]["week"]))
        recent = res[-4:]; m4 = statistics.mean(recent)
        out_months = 0
        if rs[0].get("band_lo"):
            for blk in (rs[-8:-4], rs[-4:]):
                if len(blk) == 4:
                    am = statistics.mean(float(r["actual"]) for r in blk); lo = statistics.mean(float(r["band_lo"]) for r in blk); hi = statistics.mean(float(r["band_hi"]) for r in blk)
                    out_months += (am < lo or am > hi)
        both = bool(set(c_alarm) & set(e_alarm)) or (c_alarm and e_alarm and abs(c_alarm[-1] - e_alarm[-1]) <= 2)
        practical = abs(m4 - mu0) >= 1.0 * sigma  # 실질 크기: 최근 4주 평균 잔차가 1σ 이상 — 8주 σ 는 과소추정되기 쉬워 통계 경보만으로는 오경보가 난다
        verdict = "재보정" if ((both or out_months == 2) and practical) else ("주의(경보 있으나 실질 크기 <1σ 또는 한 탐지기만)" if (c_alarm or e_alarm or out_months == 1) else "정상")
        any_recal |= verdict == "재보정"
        print(f"| {kpi} | {len(rs)} | {sigma:.3g} | {c_alarm or '—'} | {e_alarm or '—'} | {m4:+.3g} | {out_months}/2 | **{verdict}** |")
    if a.changes and pathlib.Path(a.changes).exists():
        structural = [json.loads(l) for l in open(a.changes, encoding="utf-8") if l.strip()]
        structural = [c for c in structural if c.get("status") in (None, "logged") and str(c.get("type", "")).split(".")[0] in ("station", "machine", "routing", "rule", "worker", "shift", "outsourcing")]
        if structural: print(f"\n변경 로그에 미반영 구조 항목 {len(structural)}건 → **재구성**(MAJOR 버전) 후 재검증: " + ", ".join(c.get("change_id", "?") + ":" + c.get("type", "") for c in structural[:6]))
    print("\n절차(연구 21 §2-3): 재보정 = 민감도 상위 10개 중 전류·양식으로 재측정 가능한 것부터 calibrate.py; 채택 게이트 = 보정에 안 쓴 최근 4주 홀드아웃에서 잔차 절대값이 줄었는지(부호검정) — 실패하면 이전 버전 유지. 입력 드리프트만(믹스·주문수 변화, 트윈이 그 입력을 받으면 잔차 정상)이면 재보정 아님.")
    print("판정 규칙: CUSUM(k=0.5σ, h=4σ)·EWMA(λ=0.2) 동시 경보 또는 월 평균이 예측대 밖 2개월 연속 → 재보정." + (" **지금 재보정 필요.**" if any_recal else ""))


if __name__ == "__main__":
    main()
