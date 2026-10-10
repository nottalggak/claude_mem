"""전류(A, 1Hz) → 정지/공회전/가동 상태 구간 + 사이클 수 + 상태별 시간.
임계값은 첫날 라벨링(정지→공회전→1사이클)으로 기계별 학습: busy_on ≈ idle + 0.3~0.5×(busy−idle), 이력 10~20%, 최소 지속 2~3초.
사용: python3 states_from_current.py sense.db "kr/factory/sense/ct-edgebander-1/sensor/eb1_current/state" --off 0.3 --busy-on 4 --busy-off 3"""
import argparse, sqlite3, csv, sys

def segments(rows, off_on, busy_on, busy_off, min_dur):
    st = "off"; out = []
    for ts, a in rows:
        if st == "off" and a > off_on: st = "idle"
        elif st != "off" and a <= off_on * 0.8: st = "off"
        if st == "idle" and a >= busy_on: st = "busy"
        elif st == "busy" and a <= busy_off: st = "idle"
        if out and out[-1][0] == st: out[-1][2] = ts
        else: out.append([st, ts, ts])
    # 짧은 글리치 흡수
    merged = []
    for s in out:
        if merged and (s[2] - s[1]) < min_dur: merged[-1][2] = s[2]
        elif merged and merged[-1][0] == s[0]: merged[-1][2] = s[2]
        else: merged.append(s)
    return merged

ap = argparse.ArgumentParser(); ap.add_argument("db"); ap.add_argument("topic"); ap.add_argument("--off", type=float, default=0.3); ap.add_argument("--busy-on", type=float, default=4.0); ap.add_argument("--busy-off", type=float, default=3.0); ap.add_argument("--min-dur", type=float, default=3.0); ap.add_argument("--out", default="states.csv")
a = ap.parse_args()
rows = sqlite3.connect(a.db).execute("SELECT ts_utc, value FROM readings WHERE topic=? ORDER BY ts_utc", (a.topic,)).fetchall()
seg = segments(rows, a.off, a.busy_on, a.busy_off, a.min_dur)
with open(a.out, "w", newline="") as fp:
    w = csv.writer(fp); w.writerow(["state", "t0_utc", "t1_utc", "dur_s"]); [w.writerow([s, t0, t1, round(t1 - t0, 1)]) for s, t0, t1 in seg]
tot = {}
for s, t0, t1 in seg: tot[s] = tot.get(s, 0) + (t1 - t0)
print("cycles(busy segments):", sum(1 for s in seg if s[0] == "busy")); print({k: round(v / 3600, 2) for k, v in tot.items()}, "hours"); print("wrote", a.out)
