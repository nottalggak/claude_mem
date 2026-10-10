"""Roser–Nakano–Tanaka 활성기간(active period) 병목 탐지.
상태 로그에서 각 스테이션의 '활성 기간'(busy/setup/down 이 idle 로 끊기지 않고 이어진 구간)을 구하고,
각 시점에 가장 긴 활성 기간에 있는 스테이션을 그 시점의 병목으로 본다. 겹치는 구간은 '이동 병목(shifting)'.
출력: 스테이션별 단독 병목 비율·이동 병목 비율 → 가동률보다 신뢰할 수 있는 병목 순위.
사용: python3 bottleneck_active_period.py out/baseline"""
import json, sys, pathlib, collections


def main(outdir):
    outdir = pathlib.Path(outdir)
    evs = [json.loads(l) for l in open(outdir / "events.jsonl", encoding="utf-8")]
    f = json.loads((outdir / "factory.json").read_text(encoding="utf-8"))
    sh = f["meta"]["shift"]; s0 = int(sh["start"][:2]) * 60 + int(sh["start"][3:]); s1 = int(sh["end"][:2]) * 60 + int(sh["end"][3:])
    horizon = max(e["t"] for e in evs)
    st_ev = collections.defaultdict(list)
    for e in evs:
        if e["type"] == "state": st_ev[e["station"]].append((e["t"], e["state"]))
    # 활성 기간 목록 [(start, end)] per station (근무시간으로 클리핑)
    def clip(a, b):
        out = []; d = int(a // 1440)
        while d * 1440 <= b:
            lo, hi = max(a, d * 1440 + s0), min(b, d * 1440 + s1)
            if hi > lo and d % 7 < 5: out.append((lo, hi))
            d += 1
        return out
    # 공정 그룹(병렬 기계)으로 묶기: 그룹은 모든 기계가 비유휴(busy/setup/down)일 때만 '활성'(자원 포화)
    proc_of = {s["id"]: s["process"] for s in f["stations"]}
    groups = collections.defaultdict(list)
    for sid in st_ev: groups[proc_of.get(sid, sid)].append(sid)
    def busy_intervals(lst):
        lst = sorted(lst); cur = "idle"; t0 = 0.0; out = []
        for t, st in lst + [(horizon, "idle")]:
            if cur != "idle" and st == "idle": out.append((t0, t))
            if cur == "idle" and st != "idle": t0 = t
            cur = st
        return out
    active = {}
    for g, sids in groups.items():
        # 1분 격자에서 모든 기계가 busy 인 구간을 병합
        ivs = [busy_intervals(st_ev[sid]) for sid in sids]
        on = [0] * (int(horizon) + 2)
        for iv in ivs:
            for a, b in iv:
                for m_ in range(int(a), int(b) + 1): on[m_] += 1
        periods = []; t0 = None
        for m_ in range(len(on)):
            full = on[m_] >= len(sids)
            if full and t0 is None: t0 = m_
            if not full and t0 is not None: periods.append((t0, m_)); t0 = None
        active[g + "(" + ",".join(sids) + ")" if len(sids) > 1 else sids[0]] = [c for a, b in periods for c in clip(a, b)]
    # 시간축을 1분 격자로: 각 분마다 활성 중인 스테이션의 '현재 활성 기간 길이' 중 최장 = 병목
    sole = collections.Counter(); shift = collections.Counter(); total = 0
    lens = {sid: [(a, b, b - a) for a, b in per] for sid, per in active.items()}
    idx = {sid: 0 for sid in lens}
    t = s0
    while t < horizon:
        if int(t // 1440) % 7 < 5 and s0 <= t % 1440 < s1:
            cand = []
            for sid, per in lens.items():
                i = idx[sid]
                while i < len(per) and per[i][1] <= t: i += 1
                idx[sid] = i
                if i < len(per) and per[i][0] <= t < per[i][1]: cand.append((per[i][2], sid, per[i]))
            if cand:
                total += 1; cand.sort(reverse=True); top = cand[0]
                # 이동 병목: 최장 활성 기간과 겹치는 다른 스테이션의 활성 기간이 있으면 두 스테이션 모두 'shifting'
                overl = [c for c in cand[1:] if c[2][0] < top[2][1] and c[2][1] > top[2][0] and c[0] > 0.5 * top[0]]
                if overl: shift[top[1]] += 1; shift[overl[0][1]] += 1
                else: sole[top[1]] += 1
        t += 1
    rows = sorted(((sole[s] + 0.5 * shift[s]) / max(1, total), s, sole[s] / max(1, total), shift[s] / max(1, total)) for s in set(sole) | set(shift))
    rows.reverse()
    out = ["# 활성기간 병목 분석 (Roser et al.)", "", "| 순위 | 스테이션 | 단독 병목 비율 | 이동 병목 비율 | 병목 점수 |", "|---|---|---|---|---|"]
    for i, (sc, s, so, sh_) in enumerate(rows[:8], 1): out.append(f"| {i} | {s} | {so:.0%} | {sh_:.0%} | {sc:.2f} |")
    out += ["", "해석: 단독 병목 비율이 60% 를 넘으면 그 설비 증설이 정당화된다. 상위 2개가 이동 병목으로 번갈아 나오면 둘을 함께 봐야 하고, 투자 후 재실행해 병목 이동을 확인한다."]
    (outdir / "bottleneck_active_period.md").write_text("\n".join(out), encoding="utf-8"); print("\n".join(out))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(pathlib.Path(__file__).parent / "out/baseline"))
