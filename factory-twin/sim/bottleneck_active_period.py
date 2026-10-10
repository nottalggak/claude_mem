"""Roser–Nakano–Tanaka 활성기간(active period) 병목 탐지 — 자원 포화 기준.
활성 = 자원이 포화(점유 수 == 용량)인 연속 구간. 병렬 기계는 공정 그룹으로 묶어 그룹 전체 포화일 때 활성.
각 분(근무시간)마다 가장 긴 활성 구간에 있는 그룹이 병목. 그 구간이 2위 후보의 활성 구간과 시작 또는 끝에서 겹치면 '이동 병목', 아니면 '단독'.
→ 단독+이동 = 100% 분할. 가동률·대기 기반 순위와 다르면 두 결과를 함께 보고하고 이유(배치 길이, 병렬 용량)를 적는다.
사용: python3 bottleneck_active_period.py out/baseline"""
import json, sys, pathlib, collections
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from common import Calendar


def main(outdir):
    outdir = pathlib.Path(outdir)
    evs = [json.loads(l) for l in open(outdir / "events.jsonl", encoding="utf-8")]
    f = json.loads((outdir / "factory.json").read_text(encoding="utf-8")); cal = Calendar(f["meta"]["shift"])
    horizon = int(max(e["t"] for e in evs)) + 1
    cap = {s["id"]: s.get("capacity", 1) for s in f["stations"]}; proc = {s["id"]: s["process"] for s in f["stations"]}
    occ_ev = collections.defaultdict(list)
    for e in evs:
        if e["type"] == "state": occ_ev[e["station"]].append((e["t"], e.get("occ", 1 if e["state"] in ("busy", "setup", "down") else 0)))
    groups = collections.defaultdict(list)
    for sid in occ_ev: groups[proc[sid]].append(sid)
    # 분 단위 점유 수 시계열 (그룹 합)
    def occ_series(sid):
        arr = [0] * (horizon + 1); lst = sorted(occ_ev[sid]); cur = 0; t_prev = 0
        for t, o in lst + [(horizon, 0)]:
            for m in range(int(t_prev), min(int(t), horizon)): arr[m] = cur
            t_prev, cur = t, o
        return arr
    active = {}
    for g, sids in groups.items():
        tot_cap = sum(cap[s] for s in sids); series = [occ_series(s) for s in sids]
        periods = []; t0 = None
        for m in range(horizon):
            full = sum(sr[m] for sr in series) >= tot_cap and cal.working(m)
            if full and t0 is None: t0 = m
            if not full and t0 is not None: periods.append((t0, m)); t0 = None
        if t0 is not None: periods.append((t0, horizon))
        name = f"{g}({','.join(sids)})" if len(sids) > 1 else sids[0]
        active[name] = periods
    # 각 분: 최장 활성 구간 보유 그룹 = 병목
    sole = collections.Counter(); shift = collections.Counter(); total = 0
    idx = {k: 0 for k in active}
    for m in range(horizon):
        if not cal.working(m): continue
        cand = []
        for k, per in active.items():
            i = idx[k]
            while i < len(per) and per[i][1] <= m: i += 1
            idx[k] = i
            if i < len(per) and per[i][0] <= m < per[i][1]: cand.append((per[i][1] - per[i][0], k, per[i]))
        if not cand: continue
        total += 1; cand.sort(reverse=True); top = cand[0]
        shifting = False
        if len(cand) > 1:
            second = cand[1]
            # Roser: 최장 구간의 시작 또는 끝 부근에서 2위 구간과 겹치면 이동 병목
            if second[2][0] < top[2][0] or second[2][1] > top[2][1]: shifting = True
        (shift if shifting else sole)[top[1]] += 1
    rows = sorted(((sole[k] + shift[k]) / max(1, total), k, sole[k] / max(1, total), shift[k] / max(1, total)) for k in set(sole) | set(shift))
    rows.reverse()
    out = ["# 활성기간 병목 분석 (Roser et al., 자원 포화 기준)", "", f"근무 분 중 어떤 그룹이라도 포화였던 비율: {total / max(1, sum(1 for m in range(horizon) if cal.working(m))):.0%}", "",
           "| 순위 | 스테이션/그룹 | 단독 병목 비율 | 이동 병목 비율 | 합계 |", "|---|---|---|---|---|"]
    for i, (sc, k, so, sh) in enumerate(rows[:8], 1): out.append(f"| {i} | {k} | {so:.0%} | {sh:.0%} | {sc:.0%} |")
    out += ["", "해석: 비율은 '어느 그룹이든 포화였던 시간' 중의 분할(합 100%). 1위의 단독 비율이 50% 를 넘고 가동률 순위와 일치하면 그 설비 증설이 정당화된다. 가동률 1위와 다르면 배치가 길어 포화가 간헐적인 공정(건조·조립)일 수 있으므로 두 지표를 함께 보고한다."]
    (outdir / "bottleneck_active_period.md").write_text("\n".join(out), encoding="utf-8"); print("\n".join(out))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(pathlib.Path(__file__).parent / "out/baseline"))
