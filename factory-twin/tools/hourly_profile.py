"""시간대 능률 프로파일: 2주 카운터·CT 로그(또는 시뮬 이벤트)에서 시각별 처리 건수를 세어 교대 평균 대비 배수(hourly_factor)를 만든다.
연구 20(인간 변동성) 근거: 시업 직후·점심 후·종업 전 능률 저하는 일 출력 ±10% 허용 안에서 흔히 5~15% 폭이라 v0.5 에서는 '측정해서 넣거나, 넣지 않고 CV 에 흡수' 둘 중 하나를 명시한다.
입력 형식(택1):
  - counter.csv: 열 timestamp(ISO 또는 분), station(선택), count(선택, 기본 1)  — 광전 카운터·CT 상태 전이 로그
  - events.jsonl(시뮬): proc_end 이벤트를 센다(라운드트립용)
  - worklog.csv(--cycle): 단계별 start,end 로 '착수 시각별 가공 길이'를 스테이션 평균 대비 배수로 낸다 — 완료 건수와 달리 상류 기아·휴게 직후 몰림의 영향을 받지 않는 **진짜 능률** 지표(시뮬 자체 검증: 리듬이 없으면 1.0 평탄)
출력: 시각별 배수 JSON(meta.shift.hourly_factor 에 붙여 넣음) + 표. 배수 = 그 시각의 시간당 처리 건수 / 근무시간 평균. 휴게 시간대는 제외(근무 분이 30분 미만인 시각은 생략).
사용: python3 tools/hourly_profile.py counter.csv [--factory factory.json] [--station EB1] [--out hourly.json]"""
import csv, json, sys, argparse, pathlib, datetime as dt
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "sim"))
from common import Calendar


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("--cycle", action="store_true", help="worklog.csv 의 start/end 로 가공 길이 기준 배수"); ap.add_argument("--factory"); ap.add_argument("--station"); ap.add_argument("--out"); ap.add_argument("--min-work-min", type=int, default=30)
    a = ap.parse_args()
    counts = {}; days = set()
    if a.cycle:
        rows = [r for r in csv.DictReader(open(a.src, encoding="utf-8")) if r.get("start") and r.get("end") and (not a.station or r["station"] == a.station)]
        cal = Calendar(json.loads(pathlib.Path(a.factory).read_text(encoding="utf-8"))["meta"]["shift"]) if a.factory else None
        if cal is None: print("경고: --factory 없음 → 휴게·야간을 뺄 수 없어 11시·16시 착수 단계가 길게 보인다(점심 포함). factory.json 을 주면 근무 분으로 환산한다.")
        def dur(r):
            t0, t1 = float(r["start"]), float(r["end"])
            if cal is None or t1 <= t0: return t1 - t0
            a_, b_ = int(t0), int(t1); n = sum(1 for t in range(a_, b_) if cal.working(t)); return n + (t1 - t0) - (b_ - a_)
        by_grp = {}  # (스테이션, 제품) 별 정규화 — 배치 크기·제품 차이가 시각 효과로 오인되지 않게
        for r in rows:
            d = dur(r)
            if d <= 0 or d > 300: continue  # 밤을 넘긴 단계·배치 단위 긴 가공은 제외
            by_grp.setdefault((r["station"], r.get("product", "")), []).append((float(r["start"]), d))
        ratio = {}
        for g, xs in by_grp.items():
            if len(xs) < 5: continue
            mean = sum(d for _, d in xs) / len(xs)
            for t0, d in xs:
                h = int((t0 % 1440) // 60); ratio.setdefault(h, []).append(d / mean)
        print("| 착수 시각 | 단계 수 | 가공 길이 / 그룹 평균 | SE | 능률 배수(역수) |"); print("|---|---|---|---|---|")
        out = {}; ses = {}
        for h in sorted(ratio):
            if len(ratio[h]) < 5: continue
            xs = ratio[h]; m = sum(xs) / len(xs); se = (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5 / len(xs) ** 0.5
            out[str(h)] = round(1 / m, 2); ses[str(h)] = round(se / m, 3); print(f"| {h:02d}:00 | {len(xs)} | {m:.2f} | {se:.3f} | {1 / m:.2f} |")
        if out:
            spread = max(out.values()) - min(out.values()); mse = max(ses.values())
            ok = spread >= 0.2 and spread > 2 * mse
            print(f"\n능률 배수 범위 {min(out.values()):.2f}~{max(out.values()):.2f} (폭 {spread:.2f}, 최대 SE {mse:.3f}) →", "hourly_factor 반영(폭 ≥0.20 이고 폭 > 2×SE)" if ok else "생략 가능(CV 흡수 — 폭이 작거나 잡음 수준)")
            print("제외: 가공 길이 >300분 단계(재단·건조 등 배치 단위)는 집계하지 않는다.")
            if a.out: pathlib.Path(a.out).write_text(json.dumps({"hourly_factor": out, "basis": "cycle_length"}, ensure_ascii=False, indent=1), encoding="utf-8")
        return
    if a.src.endswith(".jsonl"):
        for line in open(a.src, encoding="utf-8"):
            e = json.loads(line)
            if e["type"] != "proc_end" or (a.station and e["station"] != a.station): continue
            h = int((e["t"] % 1440) // 60); counts[h] = counts.get(h, 0) + 1; days.add(int(e["t"] // 1440))
    else:
        for r in csv.DictReader(open(a.src, encoding="utf-8")):
            if a.station and r.get("station") and r["station"] != a.station: continue
            ts = r["timestamp"]
            try: t = dt.datetime.fromisoformat(ts); h = t.hour; d = t.date()
            except ValueError: m = float(ts); h = int((m % 1440) // 60); d = int(m // 1440)
            counts[h] = counts.get(h, 0) + float(r.get("count") or 1); days.add(d)
    # 근무 시각만: factory 가 있으면 교대·휴게로 각 시각의 근무 분을 계산
    work_min = {h: 60 for h in range(24)}
    if a.factory:
        sh = json.loads(pathlib.Path(a.factory).read_text(encoding="utf-8"))["meta"]["shift"]
        hm = lambda s: int(s[:2]) * 60 + int(s[3:5])
        st, en = hm(sh["start"]), hm(sh["end"]); brk = [(hm(b[0]), hm(b[1])) for b in sh.get("breaks", [])]
        for h in range(24):
            lo, hi = h * 60, h * 60 + 60; m = max(0, min(hi, en) - max(lo, st))
            for b0, b1 in brk: m -= max(0, min(hi, b1) - max(lo, b0))
            work_min[h] = max(0, m)
    nd = max(1, len(days))
    rate = {h: counts.get(h, 0) / nd / (work_min[h] / 60) for h in range(24) if work_min[h] >= a.min_work_min}
    if not rate: print("근무 시각 데이터 없음"); return
    avg = sum(rate[h] * work_min[h] for h in rate) / sum(work_min[h] for h in rate)
    factor = {str(h): round(rate[h] / avg, 2) for h in rate}  # 완료 건수 프로파일 — 시간대 능률이 아니다(상류 기아·휴게 직후 몰림 포함). hourly_factor 로 쓰지 말 것
    print("| 시각 | 근무 분 | 시간당 처리(일 평균) | 배수 |"); print("|---|---|---|---|")
    for h in sorted(rate): print(f"| {h:02d}:00 | {work_min[h]} | {rate[h]:.1f} | {factor[str(h)]:.2f} |")
    spread = max(factor.values()) - min(factor.values())
    print(f"\n일수 {nd}, 교대 평균 {avg:.1f}/시간, 배수 범위 {min(factor.values()):.2f}~{max(factor.values()):.2f} (폭 {spread:.2f})")
    print("판정: 이것은 **완료 건수 프로파일**(교차검증·시간별 출력 검증용)이며 능률 배수가 아니다 — 리듬 없는 시뮬에서도 폭 0.4 가 나온다. 능률 배수는 --cycle 로 만든다.")
    print("주의: 카운터는 '완료 건수'라 상류 기아(starvation)도 낮은 배수로 잡힌다 — CT 로그의 '가동 중 사이클 길이'와 교차 확인. 같은 시각이 매일 낮으면 리듬, 특정 날만 낮으면 고장·결품.")
    if a.out: pathlib.Path(a.out).write_text(json.dumps({"count_profile": factor, "days": nd, "avg_per_hour": round(avg, 2), "note": "hourly_factor 아님 — --cycle 결과를 쓸 것"}, ensure_ascii=False, indent=1), encoding="utf-8"); print("wrote", a.out)


if __name__ == "__main__":
    main()
