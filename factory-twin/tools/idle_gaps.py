"""CT 로그 상태 구간(states.csv: state,t0_utc,t1_utc,dur_s — capture/sensing/states_from_current.py 출력)에서
(1) 유효 근무창: 일별 첫 가동·마지막 가동 시각 분포 → meta.shift 시작·종료 권고와 시업 지연·조기 마감 실태
(2) idle-gap 3봉 분해(연구 20 §5.3): <2분 핸들링(사이클에 포함) / 2~10분 자재·측정·전화(소정지 → availability) / >10분 탐색·지게차 대기·세팅·휴게(비가용 이벤트: 간격·지속)
(3) run-length 분포 → 기계 페이스 판정(CV<5% 면 결정적)
사용: python3 tools/idle_gaps.py states.csv [--tz 9] [--out gaps.json]"""
import csv, sys, argparse, json, pathlib, statistics, datetime as dt


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("states"); ap.add_argument("--tz", type=float, default=9); ap.add_argument("--out"); ap.add_argument("--short", type=float, default=2); ap.add_argument("--long", type=float, default=10); ap.add_argument("--factory", help="factory.json: 휴게 시간대와 겹치는 공백은 '달력 블록'으로 분리")
    a = ap.parse_args()
    segs = []
    for r in csv.DictReader(open(a.states, encoding="utf-8")):
        t0 = float(r["t0_utc"]) + a.tz * 3600; t1 = float(r["t1_utc"]) + a.tz * 3600; segs.append((r["state"], t0, t1))
    segs.sort(key=lambda x: x[1])
    runs = [s for s in segs if s[0] in ("busy", "run")]
    if not runs: print("가동(busy/run) 구간 없음"); return
    # (1) 유효 근무창
    by_day = {}
    for _, t0, t1 in runs:
        d = dt.datetime.fromtimestamp(t0, dt.timezone.utc).date(); by_day.setdefault(d, []).append((t0, t1))
    firsts = []; lasts = []; run_min = []
    for d, xs in sorted(by_day.items()):
        f = min(x[0] for x in xs); l = max(x[1] for x in xs)
        firsts.append(dt.datetime.fromtimestamp(f, dt.timezone.utc).hour * 60 + dt.datetime.fromtimestamp(f, dt.timezone.utc).minute); lasts.append(dt.datetime.fromtimestamp(l, dt.timezone.utc).hour * 60 + dt.datetime.fromtimestamp(l, dt.timezone.utc).minute)
        run_min.append(sum(x[1] - x[0] for x in xs) / 60)
    hm = lambda m: f"{int(m) // 60:02d}:{int(m) % 60:02d}"
    print(f"## 유효 근무창 ({len(by_day)}일)\n첫 가동 중앙값 {hm(statistics.median(firsts))} (최빠름 {hm(min(firsts))}, 최늦음 {hm(max(firsts))}) / 마지막 가동 중앙값 {hm(statistics.median(lasts))} / 일 가동 분 중앙값 {statistics.median(run_min):.0f} (최소 {min(run_min):.0f}, 최대 {max(run_min):.0f})")
    print("→ meta.shift.start 는 첫 가동 중앙값, end 는 마지막 가동 중앙값으로 두고 명목 시업·종업과의 차이를 '시업 지연·청소 블록'으로 적는다(승수가 아니라 달력 블록으로, 연구 20 §1.4). 일 가동 분이 중앙값의 70% 아래인 날은 결근·결품·고장 후보 → 출근부와 대조.")
    # (2) idle gaps
    breaks = []
    if a.factory:
        sh = json.loads(pathlib.Path(a.factory).read_text(encoding="utf-8"))["meta"]["shift"]; hm = lambda x: int(x[:2]) * 60 + int(x[3:5])
        breaks = [(hm(b[0]), hm(b[1])) for b in sh.get("breaks", [])]
    gaps = []; blocked = []
    for i in range(1, len(runs)):
        g = (runs[i][1] - runs[i - 1][2]) / 60
        if not (0 < g < 240 and dt.datetime.fromtimestamp(runs[i][1], dt.timezone.utc).date() == dt.datetime.fromtimestamp(runs[i - 1][2], dt.timezone.utc).date()): continue
        t0 = dt.datetime.fromtimestamp(runs[i - 1][2], dt.timezone.utc); m0 = t0.hour * 60 + t0.minute; m1 = m0 + g
        if any(m0 < b1 and m1 > b0 for b0, b1 in breaks): blocked.append(g); continue  # 휴게와 겹침 → 달력 블록(비가용 이벤트가 아님)
        gaps.append(g)
    if blocked: print(f"휴게 시간대와 겹치는 공백 {len(blocked)}건(합 {sum(blocked):.0f}분)은 달력 블록으로 분리(비가용 이벤트에서 제외)")
    sh = [g for g in gaps if g < a.short]; md = [g for g in gaps if a.short <= g < a.long]; lg = [g for g in gaps if g >= a.long]
    tot = sum(gaps) or 1
    print(f"\n## idle-gap 분해 (가동 사이 공백 {len(gaps)}건, 같은 날·4시간 미만)\n| 구간 | 건수 | 비율(건) | 시간 합(분) | 비율(시간) | 중앙값(분) | 모델 반영 |\n|---|---|---|---|---|---|---|")
    for name, xs, how in ((f"<{a.short:g}분 핸들링", sh, "사이클에 포함(엣지밴더 핸들링 = 1인/2인 운전 판별)"), (f"{a.short:g}~{a.long:g}분 자재·측정·전화", md, "소정지 → availability (빈도/시간, 평균 길이)"), (f"≥{a.long:g}분 탐색·대기·세팅·휴게", lg, "비가용 이벤트: 간격 지수·지속 로그정규, 휴게와 겹치면 달력 블록")):
        if xs: print(f"| {name} | {len(xs)} | {len(xs) / len(gaps):.0%} | {sum(xs):.0f} | {sum(xs) / tot:.0%} | {statistics.median(xs):.1f} | {how} |")
    # (3) run-length → 기계 페이스
    rl = [(t1 - t0) / 60 for _, t0, t1 in runs if t1 > t0]
    if len(rl) >= 10:
        m = statistics.mean(rl); cv = statistics.pstdev(rl) / m if m else 0
        print(f"\n## run-length: 평균 {m:.2f}분, CV {cv:.2f} → " + ("기계 페이스(결정적 사이클, 시간대 승수 적용 안 함)" if cv < 0.05 else "작업자 개입 변동 있음(핸들링 성분에 시간대 승수·여유율 적용)"))
    if a.out:
        pathlib.Path(a.out).write_text(json.dumps({"shift_start_median_min": statistics.median(firsts), "shift_end_median_min": statistics.median(lasts), "run_min_per_day": run_min,
            "gaps": {"short_n": len(sh), "mid_n": len(md), "mid_median_min": statistics.median(md) if md else None, "long_n": len(lg), "long_median_min": statistics.median(lg) if lg else None, "mid_per_hour": len(md) / max(1e-9, sum(run_min) / 60), "long_per_hour": len(lg) / max(1e-9, sum(run_min) / 60)}}, ensure_ascii=False, indent=1), encoding="utf-8"); print("wrote", a.out)


if __name__ == "__main__":
    main()
