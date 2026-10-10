"""공용 상수·헬퍼: 출처 폭(WIDTH), 요일/근무 판정, 상태 로그 기반 에너지 적분."""
import collections

# 파라미터 출처별 불확실성 폭 (명세서 §8-7 과 동일; calibrate/uncertainty 가 공유)
WIDTH = {"measured": None, "record": 0.10, "interview": 0.20, "estimated": 0.30}
BOUND = {"measured": 0.10, "record": 0.15, "interview": 0.25, "estimated": 0.40}  # 보정 탐색 경계


def hhmm(s):
    h, m = s.split(":"); return int(h) * 60 + int(m)


class Calendar:
    """근무 달력: Day 1 = 월요일(0). days_per_week(5/6), overtime {weekday_min, saturday:[a,b]}"""
    def __init__(self, shift):
        self.start, self.end = hhmm(shift["start"]), hhmm(shift["end"])
        self.breaks = [(hhmm(a), hhmm(b)) for a, b in shift.get("breaks", [])]
        self.days_per_week = int(shift.get("days_per_week", 5))
        ot = shift.get("overtime") or {}
        self.ot_weekday = ot.get("weekday_min", 0) or 0
        self.sat = tuple(hhmm(x) for x in ot["saturday"]) if ot.get("saturday") else None

    def is_workday(self, day):
        wd = day % 7
        return wd < 5 or (wd == 5 and (self.days_per_week >= 6 or self.sat is not None))

    def working(self, t):
        wd = int(t // 1440) % 7; m = t % 1440
        if wd >= 5:
            if wd == 5 and self.days_per_week >= 6:
                return self.start <= m < self.end and not any(a <= m < b for a, b in self.breaks)
            if wd == 5 and self.sat:
                return self.sat[0] <= m < self.sat[1]
            return False
        if not (self.start <= m < self.end + self.ot_weekday):
            return False
        return not any(a <= m < b for a, b in self.breaks)

    def workdays(self, d0, d1):
        return sum(1 for d in range(d0, d1) if self.is_workday(d))


def energy_from_events(factory, events, horizon, slot_min=15):
    """상태 로그 → 슬롯별 kW (기계: 가동/셋업 = 정격×부하율, 대기 = 근무시간 내 대기전력, 비근무 0;
    부대설비: when_any_on(연결 기계 가동 ∧ 근무) / shift / always; 기본부하: 근무 100%, 비근무 20%).
    반환: (per_slot dict asset->[kW], total list, slots)"""
    cal = Calendar(factory["meta"]["shift"]); spec = {s["id"]: s for s in factory["stations"]}
    slots = int(horizon // slot_min) + 1
    per = collections.defaultdict(lambda: [0.0] * slots); on_any = collections.defaultdict(lambda: [False] * slots)
    st_ev = collections.defaultdict(list)
    for e in events:
        if e["type"] == "state": st_ev[e["station"]].append((e["t"], e["state"]))
    def working_slot(k): return cal.working(k * slot_min + slot_min / 2)
    for sid, lst in st_ev.items():
        sp = spec.get(sid); lst.sort(); cur = "idle"; t_prev = 0.0
        if sp is None: continue
        for t, st in lst + [(horizon, "idle")]:
            a, b = int(t_prev // slot_min), int(t // slot_min)
            for k in range(a, min(b + 1, slots)):
                lo, hi = max(t_prev, k * slot_min), min(t, (k + 1) * slot_min)
                if hi > lo:
                    w = working_slot(k)
                    p = 0.0 if not w else (sp.get("rated_kw", 0) * sp.get("load_factor", 0.6) if cur in ("busy", "setup") else sp.get("idle_kw", 0))
                    per[sid][k] += p * (hi - lo) / slot_min
                    if w and cur in ("busy", "setup"):
                        for aid in sp.get("ancillary", []): on_any[aid][k] = True
            t_prev, cur = t, st
    for a in factory.get("ancillary", []):
        for k in range(slots):
            w = working_slot(k)
            on = (on_any[a["id"]][k] and w) if a["mode"] == "when_any_on" else (w if a["mode"] == "shift" else True)
            per[a["id"]][k] = a["rated_kw"] * a.get("load_factor", 0.7) if on else 0.0
    base = factory["meta"].get("energy", {}).get("base_load_kw", 0)
    for k in range(slots): per["BASE"][k] = base if working_slot(k) else base * 0.2
    total = [sum(v[k] for v in per.values()) for k in range(slots)]
    return per, total, slots
