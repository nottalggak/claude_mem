"""디스패칭·배치 규칙 재현율: 관측 착수 순서를 어느 규칙이 가장 잘 재현하는가 (03 §8-5a '규칙은 튜닝하지 말고 재현율로 선택').
입력: worklog.csv(batch,product,n_parts,station,arrive,start,end) + releases.csv(batch,product,qty,release,due)
각 스테이션에서 '착수 결정 시점'마다 대기 중이던 후보 집합을 복원하고, 실제 착수된 배치가 규칙의 선택과 같은지 센다.
규칙: FIFO(먼저 도착), EDD(납기 빠른 순), SPT/LPT(가공 짧은/긴 순), SAME(직전 제품과 같은 제품 우선=셋업 회피), SLACK(납기−현재−잔여가공), RANDOM(기준선).
동점은 후보 집합 안에 실제 선택이 있으면 1/|동점| 로 부분 점수(규칙이 '설명'하는 정도). 후보 ≥2 인 결정만 센다.
사용: python3 tools/rule_fit.py worklog.csv [--releases releases.csv] [--out sim/out/rule_fit.md]"""
import csv, sys, argparse, pathlib, statistics, math


def wilson_lo(p, n, z=1.96):
    """Wilson 점수 구간 하한 — 소표본(n<50) 비율에는 정규근사·부트스트랩보다 커버리지가 낫다(연구 19)."""
    if n == 0: return 0.0
    den = 1 + z * z / n; c = p + z * z / (2 * n); r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return max(0.0, (c - r) / den)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("worklog"); ap.add_argument("--releases"); ap.add_argument("--out"); ap.add_argument("--min-candidates", type=int, default=2); ap.add_argument("--factory", help="factory.json: 제품→색상·두께 매핑으로 GROUP(같은 색상×두께 우선 = 재단 묶음·셋업 회피) 규칙 추가")
    a = ap.parse_args()
    steps = [dict(r, arrive=float(r["arrive"]), start=float(r["start"]), end=float(r["end"])) for r in csv.DictReader(open(a.worklog, encoding="utf-8"))]
    due = {}; 
    if a.releases:
        for r in csv.DictReader(open(a.releases, encoding="utf-8")):
            due[r["batch"]] = float(r["due"]) if r.get("due") else None
    by_st = {}
    for s in steps: by_st.setdefault(s["station"], []).append(s)
    # 배치별 잔여 가공(슬랙용): 이 단계 이후 단계들의 (end-start) 합
    by_batch = {}
    for s in steps: by_batch.setdefault(s["batch"], []).append(s)
    for b, ss in by_batch.items():
        ss.sort(key=lambda x: x["arrive"]); rem = 0.0
        for s in reversed(ss): s["remaining_after"] = rem; rem += s["end"] - s["start"]
    D = lambda c: (due.get(c["batch"]) if due.get(c["batch"]) is not None else 1e12)
    grp = {}
    if a.factory:
        import json, pathlib as _pl
        for pr in json.loads(_pl.Path(a.factory).read_text(encoding="utf-8"))["products"]: grp[pr["id"]] = (pr.get("color", "-"), pr.get("thickness", 18))
    # 모든 규칙은 동점 시 FIFO 로 깨진다(현장도 그렇다). 'EDD' = 납기 → 도착 순.
    rules = {"FIFO": lambda c, now, prev: (c["arrive"],), "EDD": lambda c, now, prev: (D(c), c["arrive"]),
             "SPT": lambda c, now, prev: (c["end"] - c["start"], c["arrive"]), "LPT": lambda c, now, prev: (-(c["end"] - c["start"]), c["arrive"]),
             "SAME": lambda c, now, prev: (0 if prev and c["product"] == prev else 1, c["arrive"]),
             "SLACK": lambda c, now, prev: (D(c) - now - (c["end"] - c["start"]) - c["remaining_after"], c["arrive"])}
    if grp: rules["GROUP"] = lambda c, now, prev: (0 if prev and grp.get(c["product"]) == grp.get(prev) else 1, c["arrive"])  # 같은 색상×두께 묶음 유지(셋업 회피)
    disc = {}  # (규칙A, 규칙B) -> [A가 맞은 수, B가 맞은 수, 두 규칙이 다른 선택을 한 결정 수]
    lines = ["# 규칙 재현율 (관측 착수 순서 vs 규칙 선택)", "", "| 스테이션 | 결정 수(후보≥%d) | 평균 후보 수 | " % a.min_candidates + " | ".join(rules) + " | RANDOM | 최적 규칙 | 95% 신뢰 하한 |", "|---|---|---|" + "---|" * (len(rules) + 3)]
    total = {r: [0.0, 0] for r in rules}; total_rand = [0.0, 0]
    for sid, ss in sorted(by_st.items()):
        ss.sort(key=lambda x: x["start"]); score = {r: 0.0 for r in rules}; n = 0; cand_n = []; rand = 0.0; prev = None
        ends = sorted(x["end"] for x in ss)
        import bisect
        for s in ss:
            # 결정 시점 ≠ 착수 시점: 기계는 직전 작업이 끝날 때(또는 이 배치 도착 때) 다음 배치를 고르고, 셋업·야간을 지나 착수한다.
            # 결정 시점 = max(이 배치 도착, 이 스테이션에서 착수 전 가장 최근에 끝난 작업의 종료) — 후보는 그 시점에 도착해 있고 아직 착수 안 한 배치
            i = bisect.bisect_left(ends, s["start"]); freed = ends[i - 1] if i > 0 else 0.0
            now = max(s["arrive"], freed)
            same_t = [c for c in ss if abs(c["start"] - s["start"]) < 1e-6]  # 동시 착수 집합(다슬롯 스테이션): 어느 것이 먼저 선택됐는지 구분 불가 → 집합 중 하나면 적중
            cands = [c for c in ss if c["arrive"] <= now + 1e-9 and c["start"] > s["start"] + 1e-9] + same_t
            if len(cands) < a.min_candidates:
                prev = s["product"]; continue
            n += 1; cand_n.append(len(cands)); rand += 1 / len(cands)
            pick = {}
            for r, key in rules.items():
                vals = [(key(c, now, prev), c["batch"]) for c in cands]; best = min(v for v, _ in vals); ties = [b for v, b in vals if v == best]
                if s["batch"] in ties or any(c["batch"] in ties for c in same_t): score[r] += 1 / len(ties)
                pick[r] = set(ties)
            for ra in rules:
                for rb in rules:
                    if ra < rb and pick[ra] != pick[rb]:  # 두 규칙이 다른 선택 → 판별 결정
                        d = disc.setdefault((ra, rb), [0, 0, 0]); d[2] += 1
                        if s["batch"] in pick[ra]: d[0] += 1
                        if s["batch"] in pick[rb]: d[1] += 1
            prev = s["product"]
        if n == 0: continue
        for r in rules: total[r][0] += score[r]; total[r][1] += n
        total_rand[0] += rand; total_rand[1] += n
        rates = {r: score[r] / n for r in rules}; best = max(rates, key=rates.get); p = rates[best]
        lo = wilson_lo(p, n)
        lines.append(f"| {sid} | {n} | {statistics.mean(cand_n):.1f} | " + " | ".join(f"{rates[r]:.0%}" for r in rules) + f" | {rand / n:.0%} | **{best}** | {max(0, lo):.0%} |")
    if total["FIFO"][1]:
        N = total["FIFO"][1]; rates = {r: total[r][0] / N for r in rules}; best = max(rates, key=rates.get); pb = rates[best]; lo = wilson_lo(pb, N)
        second = sorted(rules, key=lambda r: rates[r])[-2]; nd = (disc.get((best, second)) or disc.get((second, best)) or [0, 0, 0])
        simple = {r: rates[r] for r in ("FIFO", "EDD")}; base_r = max(simple, key=simple.get)
        lift = pb - (rates[second] if best in ("FIFO", "EDD") else simple[base_r])  # 최선 단순 기준선 대비(연구 19 §4); best 가 단순 규칙이면 차순위 대비
        lines.append("| **전체** | %d | — | " % N + " | ".join(f"{rates[r]:.0%}" for r in rules) + f" | {total_rand[0] / total_rand[1]:.0%} | **{best}** | {lo:.0%} |")
        if N < 20: verdict = "탐색적(유효 결정 <20) — 판정 보류, 기록 기간 2주 연장"
        elif pb >= 0.75 and lo >= 0.60 and nd[2] < 10: verdict = f"복제 가능하나 **식별 불가**: {best}≈{second} (판별 결정 {nd[2]}건 <10 — 이 기록으로는 둘을 구분 못 함; 트윈에는 어느 쪽을 넣어도 같고 시나리오 축으로만 의미)"
        elif pb >= 0.75 and lo >= 0.60 and (lift >= 0.15 or (nd[2] >= 10 and nd[0] >= 0.8 * nd[2])): verdict = f"규칙층 복제 가능: {best} (재현율 {pb:.0%}, Wilson 하한 {lo:.0%}, {second} 대비 판별 {nd[0]}/{nd[2]})"
        elif pb >= 0.60: verdict = f"조건부 복제: {best} (재현율 {pb:.0%}) — 민감도에 규칙 변형(타이브레이커·묶음 창 ±)을 포함하고 한계를 명시"
        else: verdict = "미복제: 어떤 단순 규칙도 설명 못 함 → 미스 리뷰(기록에 없는 정보: 사장 지시·자재·결근), 상태 의존 혼합 규칙, 또는 규칙을 시나리오 축으로"
        lines.append(f"\n**판정(연구 19 기준: 재현율 ≥0.75, Wilson 95% 하한 ≥0.60, 단순 기준선 대비 lift ≥0.15)**: {verdict}")
    if total["FIFO"][1]:
        top = sorted(rules, key=lambda r: -total[r][0] / total[r][1])[:3]
        lines += ["", "**판별 결정**(두 규칙이 서로 다른 배치를 고른 결정만 — 여기서 이겨야 규칙이 식별된 것):", "", "| 규칙 A | 규칙 B | 판별 결정 수 | A 적중 | B 적중 |", "|---|---|---|---|---|"]
        for ra in top:
            for rb in top:
                if ra < rb:
                    d = disc.get((ra, rb)) or disc.get((rb, ra))
                    if d: lines.append(f"| {ra} | {rb} | {d[2]} | {d[0]} | {d[1]} |")
        lines.append("판별 결정이 10개 미만이면 두 규칙은 이 기록으로 구분되지 않는다(투입이 납기 역산이면 FIFO≈EDD) → 트윈에는 어느 쪽을 넣어도 같고, 시나리오로만 의미가 있다.")
    lines += ["", "**범위**: 이 도구는 규칙의 두 층 중 (i) **묶음 간 순서(디스패칭)** 만 본다. (ii) **묶음 구성**(색상×두께 창에 어떤 주문을 합쳤나)은 대기열 순서가 아니라 '한 배치에 여러 주문'으로 나타나므로 시트 13 '함께 처리한 배치' 열과 `cut_batching`·`setups_per_day` KPI 로 따로 검증한다 — 자체 검증: 색상 묶음 공장(S6)에서도 재단 결정 수가 122→11 로 줄고 FIFO=GROUP=100% 로 나와 순서만으로는 묶음을 식별하지 못했다.", "읽는 법: RANDOM 열은 '무작위로 골라도 맞출 확률'(후보 수의 역수 평균) — 규칙 재현율이 이 값과 비슷하면 그 규칙은 설명력이 없다.",
              "합격 기준은 위 판정 줄(연구 19). 미달이면 인터뷰 규칙(시트 16)의 조건이 더 있거나(급한 주문·사장 지시·자재 도착) 상태 의존 혼합(평상시 EDD-묶음 / 과부하 시 셋업 최소화)이다 → 미스 15~20건을 반장과 함께 리뷰해 '기록되지 않은 교란율'을 따로 보고한다.",
              "주의: 후보 집합은 '도착했고 아직 착수 안 함'으로 복원하므로 기록되지 않은 대기(외주·자재)는 후보를 과대 집계한다. 결정 수 <20 이면 신뢰 하한만 믿는다."]
    out = "\n".join(lines); print(out)
    if a.out: pathlib.Path(a.out).write_text(out, encoding="utf-8")


if __name__ == "__main__":
    main()
