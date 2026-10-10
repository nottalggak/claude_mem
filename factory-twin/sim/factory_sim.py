"""
가구공장 디지털 트윈 - 이산사건 시뮬레이션 (SimPy)
입력: factory.json (schema/factory.schema.json) [+ scenario patch]
출력: out/<scenario>/events.jsonl, kpis.json, paths.json

모델링 범위
- 주문 → 배치(제품 N개분 부품) → 라우팅 공정 순서대로 이동/대기/셋업/가공
- 공정별 기계 대수(capacity), 입력 버퍼 용량(초과 시 상류 블로킹), 셋업(제품 전환 시), 고장(MTBF/MTTR), 불량률
- 운반: 대차(운반 인원 자원) / 지게차, 격자 A* 경로, 거리 기반 이동 시간 → 동선(스파게티) 기록
- 근무시간/휴식: 휴식 중 가공/운반 중단
- 에너지: 기계 상태(가동/대기)별 kW + 부대설비(집진기/컴프레서) + 기본부하 → kWh, 전기요금
"""
import json, math, random, sys, pathlib, argparse, copy
import simpy
from pathfind import Grid
from common import Calendar, energy_from_events

BOARD_AREA = 2.44 * 1.22
YIELD = 0.78


def hhmm(s):
    h, m = s.split(":"); return int(h) * 60 + int(m)


class Shift(Calendar):
    def __init__(self, env, meta):
        super().__init__(meta["shift"]); self.env = env; self.day_min = 1440
        # 시간대 리듬: {"8": 0.85, "9": 1.0, ...} 시각별 능률 배수(1.0 = 측정 사이클 그대로). tools/hourly_profile.py 가 카운터·CT 로그에서 만든다
        self.hourly_factor = {int(k): float(v) for k, v in (meta["shift"].get("hourly_factor") or {}).items()}

    def factor(self, t):
        if not self.hourly_factor:
            return 1.0
        return max(0.2, self.hourly_factor.get(int((t % self.day_min) // 60), 1.0))

    def weekday(self, t):
        return int(t // self.day_min) % 7

    def next_open(self, t):
        if self.working(t):
            return t
        tt = int(t) + 1
        while tt < t + 8 * self.day_min:
            if self.working(tt):
                return tt
            tt += 1
        return tt

    def wait(self):
        t = self.env.now; n = self.next_open(t)
        return self.env.timeout(n - t) if n > t else self.env.timeout(0)

    def worked_minutes(self, horizon):
        return sum(1 for t in range(int(horizon)) if self.working(t))


class Station:
    def __init__(self, env, spec, sim):
        self.env, self.spec, self.sim = env, spec, sim
        self.id = spec["id"]; self.process = spec["process"]
        self.cap = spec.get("capacity", 1)
        self.res = simpy.PriorityResource(env, capacity=self.cap) if sim.f.get("rules", {}) and isinstance(sim.f.get("rules"), dict) and sim.f["rules"].get("dispatch") == "edd" else simpy.Resource(env, capacity=self.cap)
        self.edd = isinstance(self.res, simpy.PriorityResource)
        self.buffer = simpy.Resource(env, capacity=max(1, spec.get("buffer_batches", 4)) + self.cap)
        self.down = False
        self.last_product = None
        self.busy_min = 0.0; self.setup_min = 0.0; self.down_min = 0.0; self.blocked_min = 0.0
        self.n_batches = 0; self.n_parts = 0; self.wait_total = 0.0; self.waits = []
        self.queue_len = 0; self.queue_series = [(0.0, 0)]
        self.state = "idle"
        if spec.get("mtbf_min", 0) > 0 and self.process not in ("raw", "fg"):
            env.process(self.breakdowns())
        # 작업자 페이스 여부: 시간대 능률(hourly_factor)은 작업자 페이스 공정에만 적용(연구 20: 기계 페이스 공정은 시간대 효과가 사라진다)
        self.operator_paced = spec.get("paced", "operator" if self.process in ("assemble", "pack", "finish", "sand") else "machine") == "operator"
        absences = [a for a in (sim.f["meta"].get("absences") or []) if a.get("station") == self.id]
        if absences:
            env.process(self.absent_days(sorted(int(a["day"]) for a in absences)))

    def absent_days(self, days):
        """결근 트레이스(연구 20 §5: v0.5 는 실제 출근부를 그대로 입력). 그 날의 근무시간 동안 down — 1인 운전 스테이션 가정, 다인 벤치는 capacity 를 별도 스테이션으로 나눠 둔다."""
        for d in days:
            t0 = d * 1440 + self.sim.shift.start
            if t0 < self.env.now: continue
            yield self.env.timeout(t0 - self.env.now)
            self.down = True; self.log_state("down"); self.sim.ev({"type": "absent", "station": self.id, "day": d})
            yield self.env.timeout(self.sim.shift.end - self.sim.shift.start)
            self.down_min += self.sim.shift.end - self.sim.shift.start
            self.down = False; self.log_state("idle")

    def log_state(self, state):
        self.state = state
        self.sim.ev({"type": "state", "station": self.id, "state": state, "occ": self.res.count, "cap": self.cap})

    def breakdowns(self):
        while True:
            yield self.env.timeout(self.sim.rng.expovariate(1 / self.spec["mtbf_min"]))
            if not self.sim.shift.working(self.env.now):
                continue
            self.down = True
            d = self.sim.rng.expovariate(1 / self.spec["mttr_min"])
            self.log_state("down"); self.sim.ev({"type": "breakdown", "station": self.id, "duration": round(d, 1)})
            self.down_min += d
            yield self.env.timeout(d)
            self.down = False
            self.log_state("busy" if self.res.count else "idle")

    def part_time(self, part, product):
        c = self.spec.get("cycle")
        if not c:
            return 0.0
        t = c.get("base_min", 0.0)
        avail = self.spec.get("availability", 1.0) or 1.0  # 소정지·예열·청소 손실을 사이클 팽창으로 흡수
        for k, v in c.get("per_unit", {}).items():
            t += v * part.get(k, 0)
        if "per_product" in c:
            t += c["per_product"].get(product, 0)
        cv = c.get("cv", 0)
        if cv > 0 and t > 0:
            sigma = math.sqrt(math.log(1 + cv * cv)); mu = math.log(t) - sigma * sigma / 2
            t = self.sim.rng.lognormvariate(mu, sigma)
        return t / avail

    def set_queue(self, delta):
        self.queue_len += delta
        self.queue_series.append((self.env.now, self.queue_len))
        self.sim.ev({"type": "queue", "station": self.id, "len": self.queue_len})


class Sim:
    def __init__(self, factory, seed=1, horizon_days=None):
        if isinstance(factory.get("rules"), list):
            factory = dict(factory); factory["rules_list"] = factory["rules"]; factory["rules"] = {"dispatch": "edd" if any("납기" in str(r.get("그러면 (행동)", "")) for r in factory["rules_list"]) else "fifo"}
        self.rng_orders = random.Random(seed)       # 주문 스트림 (시나리오 간 동일)
        self.rng = random.Random(seed + 7919)        # 공정 변동/고장 스트림
        self.f = factory
        self.env = simpy.Environment()
        self.shift = Shift(self.env, factory["meta"])
        self.grid = Grid(factory)
        self.stations = {s["id"]: Station(self.env, s, self) for s in factory["stations"]}
        self.by_process = {}
        for s in self.stations.values():
            self.by_process.setdefault(s.process, []).append(s)
        tr = factory["transport"]
        self.handlers = simpy.Resource(self.env, capacity=max(1, tr.get("handlers", 1)))
        self.carts = simpy.Resource(self.env, capacity=tr["carts"]) if tr.get("carts") else None  # 대차 수 제약(옵션)
        self.cart_wait_total = 0.0
        self.forklifts = simpy.Resource(self.env, capacity=max(1, tr.get("forklifts", 1)))
        self.handler_speed = tr.get("handler_speed_mps", 1.2) * 60  # m/min
        self.forklift_speed = tr.get("forklift_speed_mps", 2.0) * 60
        self.load_min = tr.get("load_unload_min", 1.0)
        self.forklift_procs = set(tr.get("forklift_processes", ["raw", "fg"]))
        self.events = []
        self.moves = []  # (vehicle, t0, t1, path, length)
        self.batches = []
        self.handler_busy = 0.0; self.forklift_busy = 0.0
        self.handler_pos = {i: tuple(self.stations["RAW"].spec["out_pos"]) for i in range(self.handlers.capacity)}
        self.vehicle_ids = {}
        self.horizon_days = horizon_days or factory["orders"].get("horizon_days", 5)
        if factory["orders"].get("mode") == "history" and factory["orders"].get("history_list"):
            import datetime as _dt
            ds = [_dt.date.fromisoformat(str(h["order_date"])[:10]) for h in factory["orders"]["history_list"] if h.get("order_date")]
            dues = [_dt.date.fromisoformat(str(h["due_date"])[:10]) for h in factory["orders"]["history_list"] if h.get("due_date")]
            d0 = min(ds); last = max(ds + dues)
            self.horizon_days = (last - d0).days + d0.weekday() + 8
        self.horizon = self.horizon_days * 24 * 60
        self.products = {p["id"]: p for p in factory["products"]}
        self.scrap = 0; self.produced = 0
        self.cut_pool = {}; self.cut_timers = {}; self.n_cut_batches = 0; self.orders_in_cut_batches = 0; self.rework_parts = 0

    def ev(self, e):
        e["t"] = round(self.env.now, 2); self.events.append(e)

    # ---------- 주문 생성 ----------
    def gen_orders(self):
        o = self.f["orders"]
        oid = 0
        if o.get("mode") == "list":
            for od in o["list"]:  # order_min(주문 접수) 이 있으면 그 시각에 접수(외주 발주 시계 시작), release_at 에 투입
                yield self.env.timeout(max(0, od.get("order_min", od["release_min"]) - self.env.now))
                oid += 1; self.env.process(self.order_entry(oid, od["product"], od["qty"], od.get("due_min"), trace=od.get("trace"), release_at=od.get("release_at")))
            return
        if o.get("mode") == "history":
            # 실제 주문 이력 재생(검증·홀드아웃용). order_date 의 요일이 Day 1(월) 에 맞도록 가장 이른 날짜의 요일만큼 오프셋
            import datetime as _dt
            hist = [h for h in o.get("history_list", []) if h.get("order_date") and h.get("product") in self.products]
            dates = [_dt.date.fromisoformat(str(h["order_date"])[:10]) for h in hist]
            d0 = min(dates); off = d0.weekday()  # 월=0
            items = []
            for h, d in zip(hist, dates):
                day = (d - d0).days + off
                due = None
                if h.get("due_date"):
                    dd = _dt.date.fromisoformat(str(h["due_date"])[:10]); due = ((dd - d0).days + off) * 1440 + self.shift.end
                items.append((day * 1440 + self.shift.start + self.rng_orders.uniform(0, 240), h["product"], int(h.get("qty") or 1), due))
            items.sort()
            for t, pid, qty, due in items:
                yield self.env.timeout(max(0, t - self.env.now))
                oid += 1; self.env.process(self.order_entry(oid, pid, qty, due))
            return
        mix = o["mix"]; keys = list(mix); wts = [mix[k] for k in keys]
        il = o.get("install_lead_days")
        for day in range(self.horizon_days):
            if not self.shift.is_workday(day):  # 비근무일 주문 접수 없음
                continue
            n = o.get("orders_per_day", 6)
            n_today = max(1, int(self.rng_orders.gauss(n, n * 0.2)))
            base = day * 1440 + self.shift.start
            times = sorted(self.rng_orders.uniform(0, (self.shift.end - self.shift.start) * 0.6) for _ in range(n_today)) if o.get("release") != "shift_start" else [0] * n_today
            for tt in times:
                yield self.env.timeout(max(0, base + tt - self.env.now))
                pid = self.rng_orders.choices(keys, wts)[0]
                qty = o["batch_size"].get(pid, 5)
                oid += 1
                due = None
                if o.get("release") == "install_date" and il:
                    lead_days = self.rng_orders.triangular(il["min"], il["max"], il["mode"])  # 근무일 기준
                    due = self.add_workdays(day, lead_days) * 1440 + self.shift.end  # 시공일(평일) 종업 시각
                self.env.process(self.order_entry(oid, pid, qty, due))

    def add_workdays(self, day, n):
        """day(0=월) 에서 근무일 n일 뒤의 달력일 (비근무일 건너뜀)"""
        d = day; left = n
        while left > 0:
            d += 1
            if self.shift.is_workday(d):
                left -= 1
        return d

    def order_entry(self, oid, pid, qty, due=None, trace=None, release_at=None):
        """고객 주문 접수 → (시공일 역산) 투입 시점까지 대기 → 외주 발주 → 재단 배치 풀 또는 즉시 흐름
        trace: {스테이션ID: 관측 가공 분} — 트레이스 구동 검증(구조 오차 분리, 03 §8). 있으면 그 스테이션의 가공시간을 표본추출하지 않고 관측값으로 고정.
        release_at: 관측 투입 시각(분) — 있으면 D-n 역산 대신 그 시각에 투입."""
        o = self.f["orders"]
        prod = self.products[pid]
        parts = self.expand(pid, qty)
        batch = {"id": f"B{oid:03d}", "product": pid, "qty": qty, "n_parts": len(parts), "order_t": self.env.now, "due": due,
                 "transport_wait": 0.0, "transport_dist": 0.0, "queue_wait": 0.0, "proc_time": 0.0, "outsourced_wait": 0.0, "steps": [],
                 "color": prod.get("color", "-"), "thickness": prod.get("thickness", 18), "parts": parts, "trace": trace or None}
        self.batches.append(batch)
        batch["outsourced_ready"] = {}
        for ou in self.f.get("outsourced", []):
            if pid in ou["products"] and ou.get("order_at") == "order":
                batch["outsourced_ready"][ou["id"]] = self.env.now + self.outsourced_lead(ou)
        if release_at is not None:
            if release_at > self.env.now:
                yield self.env.timeout(release_at - self.env.now)
        elif due is not None and o.get("install_lead_days", {}).get("start_before_days"):
            due_day = int(due // 1440); n = o["install_lead_days"]["start_before_days"]; d = due_day
            while n > 0:  # 근무일 기준 D-n
                d -= 1
                if self.shift.is_workday(d):
                    n -= 1
            rel = d * 1440 + self.shift.start
            if rel > self.env.now:
                yield self.env.timeout(rel - self.env.now)
        batch["release"] = self.env.now
        self.ev({"type": "release", "batch": batch["id"], "product": pid, "qty": qty, "n_parts": len(parts), "due": due, "order_t": round(batch["order_t"], 2)})
        # 외주 발주 (발주 시점 = release)
        for ou in self.f.get("outsourced", []):
            if pid in ou["products"] and ou.get("order_at", "release") == "release":
                batch["outsourced_ready"][ou["id"]] = self.env.now + self.outsourced_lead(ou)
        bt = o.get("batching", {})
        if bt.get("cut_key") == "color_thickness" and "cut" in prod["routing"]:
            key = (batch["color"], batch["thickness"])
            self.cut_pool.setdefault(key, []).append(batch)
            if key not in self.cut_timers:
                self.cut_timers[key] = self.env.process(self.cut_collector(key, bt.get("cut_window_min", 60)))
        else:
            self.env.process(self.batch_flow(batch))

    def outsourced_lead(self, ou):
        ld = ou["lead_days"]; days = self.rng.triangular(ld["min"], ld["max"], ld["mode"])
        if self.rng.random() < ou.get("delay_prob", 0):
            days += ou.get("delay_days", 0)
        return days * 1440

    def cut_collector(self, key, window):
        """같은 색상×두께 주문을 창(window) 동안 모아 하나의 재단 배치로 투입"""
        yield self.env.timeout(window)
        group = self.cut_pool.pop(key, []); self.cut_timers.pop(key, None)
        if not group:
            return
        self.n_cut_batches += 1; self.orders_in_cut_batches += len(group)
        self.env.process(self.merged_cut_flow(key, group))

    def merged_cut_flow(self, key, group):
        parts = [p for b in group for p in b["parts"]]
        cb = {"id": "C" + "+".join(b["id"] for b in group), "product": f"{key[0]}/{key[1]}", "qty": sum(b["qty"] for b in group), "n_parts": len(parts),
              "transport_wait": 0.0, "transport_dist": 0.0, "queue_wait": 0.0, "proc_time": 0.0, "steps": [], "parts": parts, "outsourced_ready": {}}
        self.ev({"type": "cut_batch", "batch": cb["id"], "orders": [b["id"] for b in group], "n_parts": len(parts)})
        cur = self.stations["RAW"]; cur_pos = tuple(cur.spec["out_pos"])
        res = yield from self.run_steps(cb, ["cut"], cur, cur_pos, None, release_slot=False)
        st, pos, slot = res
        # 분류(현장별 소팅)
        sort_min = self.f["orders"].get("batching", {}).get("sort_min_per_part", 0.1) * len(parts)
        if sort_min > 0:
            yield from self.work_unit(st, sort_min); self.ev({"type": "sort", "batch": cb["id"], "station": st.id, "duration": round(sort_min, 1)})
        if slot is not None:
            slot[0].buffer.release(slot[1])
        for b in group:
            b["queue_wait"] += cb["queue_wait"] / len(group); b["transport_wait"] += cb["transport_wait"] / len(group)
            b["steps"].extend(cb["steps"])
            routing = list(self.products[b["product"]]["routing"])
            rest = routing[routing.index("cut") + 1:]
            self.env.process(self.batch_flow(b, rest, st, pos))

    # ---------- 배치 부품 전개 ----------
    def expand(self, pid, qty):
        prod = self.products[pid]
        parts = []
        for p in prod["parts"]:
            for _ in range(p["qty"] * qty):
                perim = 2 * (p["w"] + p["d"])
                edges_m = perim * (p.get("n_edges", 0) / 4.0)
                parts.append({"id": p["id"], "w": p["w"], "d": p["d"], "area_m2": p["w"] * p["d"], "edges_m": edges_m,
                              "n_edges": p.get("n_edges", 0), "holes": p.get("holes", 0), "finish": p.get("finish", False)})
        return parts

    def pick_station(self, process):
        cands = self.by_process.get(process)
        if not cands:
            return None
        return min(cands, key=lambda s: (len(s.res.queue) + s.res.count - s.cap + s.queue_len, self.rng.random()))

    # ---------- 운반 ----------
    def move(self, batch, frm, to, use_forklift):
        res = self.forklifts if use_forklift else self.handlers
        speed = self.forklift_speed if use_forklift else self.handler_speed
        with res.request() as rq:
            t_req = self.env.now
            yield rq
            wait = self.env.now - t_req  # 운반자 대기 (휴식/야간 제외)
            yield self.shift.wait()
            vid = f"{'F' if use_forklift else 'H'}{self.vehicle_slot(res, use_forklift)}"
            vpos = self.handler_pos.get(vid, frm)
            for leg_from, leg_to, loaded in ((vpos, frm, False), (frm, to, True)):
                path, length = self.grid.path(leg_from, leg_to)
                dur = length / speed
                if loaded:
                    yield self.env.timeout(self.load_min)
                t0 = self.env.now
                self.ev({"type": "move", "vehicle": vid, "batch": batch["id"] if loaded else None, "path": [[round(x, 2), round(y, 2)] for x, y in path],
                         "duration": round(dur, 2), "loaded": loaded, "parts": batch["n_parts"] if loaded else 0})
                self.moves.append((vid, t0, t0 + dur, path, length, loaded))
                yield self.env.timeout(dur)
                if loaded:
                    yield self.env.timeout(self.load_min)
                if use_forklift:
                    self.forklift_busy += dur + (self.load_min * 2 if loaded else 0)
                else:
                    self.handler_busy += dur + (self.load_min * 2 if loaded else 0)
            self.handler_pos[vid] = to
            batch["transport_wait"] += wait
            batch["transport_dist"] += length

    def vehicle_slot(self, res, fork):
        key = "F" if fork else "H"
        n = self.vehicle_ids.get(key, 0); self.vehicle_ids[key] = n + 1
        return (n % res.capacity) + 1

    # ---------- 배치 흐름 ----------
    def batch_flow(self, batch, routing=None, cur=None, cur_pos=None):
        prod = self.products[batch["product"]]
        routing = list(prod["routing"]) if routing is None else list(routing)
        cur = cur or self.stations["RAW"]; cur_pos = cur_pos or tuple(cur.spec["out_pos"])
        yield from self.run_steps(batch, routing + ["fg"], cur, cur_pos, None, release_slot=True)
        batch["done"] = self.env.now
        batch["lead_min"] = self.env.now - batch["release"]
        batch["lead_work_min"] = sum(1 for t in range(int(batch["release"]), int(self.env.now)) if self.shift.working(t))
        batch["late_min"] = max(0.0, self.env.now - batch["due"]) if batch.get("due") else 0.0
        batch["order_lead_days"] = round((self.env.now - batch["order_t"]) / 1440, 2)
        self.produced += batch["qty"]
        self.ev({"type": "done", "batch": batch["id"], "lead_min": round(batch["lead_min"], 1), "late_min": round(batch["late_min"], 1)})

    def rework_flow(self, rb, routing, cur):
        """재작업 묶음: 상류 공정부터 현재 공정까지 다시 거친 뒤 소멸(원 배치는 계속 진행 — 단순화: 재작업 부품은 후속 공정에서 별도 합류하지 않음)"""
        yield from self.run_steps(rb, routing, cur, tuple(cur.spec["out_pos"]), None, release_slot=True)
        self.ev({"type": "rework_done", "batch": rb["id"]})

    def run_steps(self, batch, routing, cur, cur_pos, prev_slot, release_slot=True):
        """routing 의 공정을 순서대로 수행. 반환: (마지막 스테이션, 출발 위치, 점유 중인 버퍼 슬롯)"""
        pid = batch["product"]; parts = batch["parts"]; qty = batch["qty"]
        for proc in routing:
            # 외주 합류 대기
            for ou in self.f.get("outsourced", []):
                if ou["join_process"] == proc and ou["id"] in batch.get("outsourced_ready", {}):
                    ready = batch["outsourced_ready"][ou["id"]]
                    if ready > self.env.now:
                        w = ready - self.env.now; batch["outsourced_wait"] += w
                        self.ev({"type": "wait_outsourced", "batch": batch["id"], "item": ou["id"], "station": cur.id, "duration": round(w, 1)})
                        yield self.env.timeout(w)
            st = self.pick_station(proc)
            if batch.get("trace") and not self.f["meta"].get("trace_free_station"):  # 트레이스 구동 L0: 관측된 스테이션(병렬 대체기 중 실제로 간 곳)을 강제. L1 은 모델이 고른다
                forced = next((self.stations[sid] for sid in batch["trace"] if sid in self.stations and self.stations[sid].process == proc), None)
                if forced is not None: st = forced
            if st is None:
                continue
            slot = st.buffer.request()
            t_block = self.env.now
            yield slot
            blocked = self.env.now - t_block
            if blocked > 0 and prev_slot is not None:
                prev_slot[0].blocked_min += blocked
                self.ev({"type": "blocked", "station": prev_slot[0].id, "batch": batch["id"], "duration": round(blocked, 1)})
            if prev_slot is not None:
                prev_slot[0].buffer.release(prev_slot[1])
            prev_slot = (st, slot)
            use_fork = proc in self.forklift_procs or cur.process in self.forklift_procs
            if self.carts is not None and not use_fork and batch.get("cart_req") is None:
                t_c = self.env.now; batch["cart_req"] = self.carts.request(); yield batch["cart_req"]
                self.cart_wait_total += self.env.now - t_c
                if self.env.now - t_c > 0: self.ev({"type": "wait_cart", "batch": batch["id"], "station": cur.id, "duration": round(self.env.now - t_c, 1)})
            yield self.env.process(self.move(batch, cur_pos, tuple(st.spec["in_pos"]), use_fork))
            self.ev({"type": "arrive", "batch": batch["id"], "station": st.id, "pos": st.spec["in_pos"]})
            if proc == "fg":
                if self.carts is not None and batch.get("cart_req") is not None:
                    self.carts.release(batch["cart_req"]); batch["cart_req"] = None
                break
            st.set_queue(+1)
            t_q = self.env.now
            prio = (batch.get("due") or 1e9) if st.edd else 0
            with (st.res.request(priority=prio) if st.edd else st.res.request()) as rq:
                yield rq
                st.set_queue(-1)
                w = self.env.now - t_q
                st.waits.append(w); st.wait_total += w; batch["queue_wait"] += w
                yield self.shift.wait()
                while st.down:
                    yield self.env.timeout(1)
                setup = 0.0
                if st.spec.get("setup_min", 0) > 0 and st.last_product != pid:
                    setup = st.spec["setup_min"]
                    st.log_state("setup"); st.setup_min += setup
                    self.ev({"type": "setup", "station": st.id, "batch": batch["id"], "duration": setup})
                    yield self.env.timeout(setup)
                st.last_product = pid
                if self.carts is not None and batch.get("cart_req") is not None:
                    self.carts.release(batch["cart_req"]); batch["cart_req"] = None
                st.log_state("busy")
                self.ev({"type": "proc_start", "station": st.id, "batch": batch["id"], "pos": st.spec["pos"]})
                t_start = self.env.now
                tr_key = st.id if (batch.get("trace") and st.id in batch["trace"]) else next((k for k in (batch.get("trace") or {}) if k in self.stations and self.stations[k].process == proc), None)
                if tr_key is not None:
                    yield from self.work_unit(st, float(batch["trace"][tr_key]))  # 트레이스 구동: 관측 가공시간 고정(L1 에서 다른 대체기를 골랐으면 같은 공정의 관측 시간)
                elif st.spec.get("batch_time_min"):
                    yield self.env.timeout(st.spec["batch_time_min"]); st.busy_min += st.spec["batch_time_min"]
                elif proc == "cut":
                    area = sum(p["area_m2"] for p in parts)
                    boards = math.ceil(area / (BOARD_AREA * YIELD))
                    for b in range(boards):
                        yield from self.work_unit(st, st.part_time({"board": 1}, pid))
                    for p in parts:
                        yield from self.work_unit(st, st.part_time({"board": 0, **p}, pid))
                elif proc in ("assemble", "pack"):
                    for i in range(qty):
                        yield from self.work_unit(st, st.part_time({}, pid))
                else:
                    sel = [p for p in parts if (p["finish"] if proc == "finish" else p.get("n_edges", 1) > 0 if proc == "edge" else p.get("holes", 1) > 0)]
                    for p in sel:
                        yield from self.work_unit(st, st.part_time(p, pid))
                sr = st.spec.get("scrap_rate", 0)
                if sr > 0:
                    lost = sum(1 for _ in parts if self.rng.random() < sr)
                    if lost:
                        self.scrap += lost
                        rew = lost * (st.part_time(parts[0], pid) + 0.5)
                        yield from self.work_unit(st, rew)
                        self.ev({"type": "scrap", "station": st.id, "batch": batch["id"], "parts": lost})
                # 상류 복귀 재작업 (예: 엣지 불량 → 재재단)
                rr = st.spec.get("rework_rate", 0); rto = st.spec.get("rework_to")
                if rr > 0 and rto and self.rng.random() < min(1.0, rr * len(parts)):
                    n_re = max(1, int(round(rr * len(parts)))); sub = parts[:n_re]
                    rb = {"id": batch["id"] + "R", "product": pid, "qty": 1, "n_parts": n_re, "release": self.env.now, "order_t": self.env.now, "due": batch.get("due"),
                          "transport_wait": 0.0, "transport_dist": 0.0, "queue_wait": 0.0, "proc_time": 0.0, "outsourced_wait": 0.0, "steps": [], "parts": sub, "outsourced_ready": {}, "is_rework": True}
                    self.rework_parts += n_re; self.ev({"type": "rework", "station": st.id, "batch": batch["id"], "parts": n_re, "to": rto})
                    routing_full = list(self.products[pid]["routing"]); idx = routing_full.index(rto) if rto in routing_full else 0
                    self.env.process(self.rework_flow(rb, routing_full[idx:routing_full.index(proc) + 1], st))
                dur = self.env.now - t_start
                st.n_batches += 1; st.n_parts += len(parts); batch["proc_time"] += dur
                batch["steps"].append({"station": st.id, "arrive": round(t_q, 1), "start": round(t_start, 1), "end": round(self.env.now, 1), "setup": setup})
                self.ev({"type": "proc_end", "station": st.id, "batch": batch["id"], "duration": round(dur, 1)})
                st.log_state("busy" if st.res.count > 1 else "idle")
                # 외주 발주 시점 after:<proc>
                for ou in self.f.get("outsourced", []):
                    if pid in ou["products"] and ou.get("order_at") == f"after:{proc}":
                        batch.setdefault("outsourced_ready", {})[ou["id"]] = self.env.now + self.outsourced_lead(ou)
            cur = st; cur_pos = tuple(st.spec["out_pos"])
        if release_slot and prev_slot is not None:
            prev_slot[0].buffer.release(prev_slot[1])
            prev_slot = None
        return cur, cur_pos, prev_slot

    def work_unit(self, st, minutes):
        """휴식/고장 시 중단되는 가공 단위"""
        if minutes <= 0:
            return
        yield self.shift.wait()
        while st.down:
            yield self.env.timeout(1)
        if st.operator_paced:
            minutes = minutes / self.shift.factor(self.env.now)  # 시간대 능률(아침 워밍업·점심 후 저하·종업 전 정리) — 작업자 페이스 공정만
        yield self.env.timeout(minutes)
        st.busy_min += minutes

    # ---------- 실행 ----------
    def run(self):
        self.env.process(self.gen_orders())
        self.env.run(until=self.horizon)
        return self.kpis()

    def kpis(self):
        avail = self.shift.worked_minutes(self.horizon)
        shift_hours = avail / 60
        stations = {}
        # 에너지: 상태 로그 15분 적분(단일 경로, power_profile 과 동일 함수)
        per_slot, total_kw, _ = energy_from_events(self.f, self.events, self.horizon)
        energy_kwh = sum(total_kw) * 0.25; energy_by = {k: round(sum(v) * 0.25, 1) for k, v in per_slot.items()}
        for st in self.stations.values():
            sp = st.spec
            if st.process in ("raw", "fg"):
                continue
            cap_avail = avail * st.cap
            util = (st.busy_min + st.setup_min) / cap_avail if cap_avail else 0
            kwh = energy_by.get(st.id, 0.0)
            qs = st.queue_series
            tw_q = sum((qs[i + 1][0] - qs[i][0]) * qs[i][1] for i in range(len(qs) - 1)) / max(1, self.horizon)
            stations[st.id] = {
                "name": sp["name"], "process": st.process, "capacity": st.cap,
                "utilization": round(util, 3), "busy_min": round(st.busy_min), "setup_min": round(st.setup_min),
                "down_min": round(st.down_min), "blocked_min": round(st.blocked_min),
                "batches": st.n_batches, "parts": st.n_parts,
                "avg_queue_wait_min": round(st.wait_total / max(1, len(st.waits)), 1),
                "max_queue_wait_min": round(max(st.waits) if st.waits else 0, 1),
                "avg_queue_len": round(tw_q, 2), "max_queue_len": max(q for _, q in qs),
                "energy_kwh": round(kwh, 1), "workers": sp.get("workers_required", 1),
            }
        tariff = self.f["meta"].get("energy", {}).get("tariff_krw_per_kwh", 160)
        done = [b for b in self.batches if "done" in b]
        released = [b for b in self.batches if "release" in b]
        warm = min(5, max(0, self.horizon_days // 3)) * 1440
        steady_days = self.shift.workdays(int(warm // 1440), self.horizon_days)  # 워밍업 이후 근무일 수
        tp_steady = sum(b["qty"] for b in done if b["done"] >= warm) / max(1e-9, steady_days)
        products_steady = sum(b["qty"] for b in done if b["done"] >= warm)
        n_setups = sum(1 for e in self.events if e["type"] == "setup")
        lead_work_sorted = sorted(b["lead_work_min"] for b in done)
        lead_work_p90 = lead_work_sorted[int(0.9 * (len(lead_work_sorted) - 1))] if lead_work_sorted else 0
        due_in = [b for b in self.batches if b.get("due") and b["due"] <= self.horizon]
        # 병목 점수: 가동률 + 평균 대기(정규화) + 블로킹 유발
        ranked = []
        maxw = max([s["avg_queue_wait_min"] for s in stations.values()] + [1])
        for sid, s in stations.items():
            score = 0.6 * s["utilization"] + 0.4 * s["avg_queue_wait_min"] / maxw
            ranked.append((round(score, 3), sid))
        ranked.sort(reverse=True)
        # 운반 거리 집계
        dist_loaded = sum(m[4] for m in self.moves if m[5]); dist_empty = sum(m[4] for m in self.moves if not m[5])
        wip_series = self.wip_series()
        return {
            "horizon_days": self.horizon_days, "shift_min_per_day": avail / self.horizon_days,
            "orders_received": len(self.batches), "orders_released": len(released), "orders_completed": len(done),
            "orders_due_in_horizon": len(due_in), "completed_of_due": round(sum(1 for b in due_in if "done" in b) / max(1, len(due_in)), 3) if due_in else None,
            "products_completed": self.produced, "products_completed_steady": products_steady, "steady_days": steady_days,
            "throughput_products_per_day": round(self.produced / self.horizon_days, 1),
            "setups_per_day": round(n_setups / max(1, self.shift.workdays(0, self.horizon_days)), 2),
            "lead_time_work_min_p90": round(lead_work_p90, 1),
            "throughput_steady_per_day": round(tp_steady, 1), "warmup_days": warm / 1440,
            "lead_time_work_min_avg": round(sum(b["lead_work_min"] for b in done) / max(1, len(done)), 1),
            "order_lead_days_avg": round(sum(b.get("order_lead_days", 0) for b in done) / max(1, len(done)), 2),
            "lead_time_min": {"avg": round(sum(b["lead_min"] for b in done) / max(1, len(done)), 1),
                              "p90": round(sorted(b["lead_min"] for b in done)[int(0.9 * (len(done) - 1))], 1) if done else 0,
                              "max": round(max([b["lead_min"] for b in done] + [0]), 1)},
            "avg_wip_batches": round(sum(w for _, w in wip_series) / max(1, len(wip_series)), 2),
            "scrap_parts": self.scrap, "rework_parts_upstream": self.rework_parts,
            "cart_wait_avg_min": round(self.cart_wait_total / max(1, len(done)), 1) if self.carts is not None else None,
            "outsourced_wait_avg_min": round(sum(b.get("outsourced_wait", 0) for b in done) / max(1, len(done)), 1),
            "on_time_ratio": round(sum(1 for b in done if b.get("late_min", 0) == 0) / max(1, len(done)), 3) if any(b.get("due") for b in done) else None,
            "cut_batching": {"cut_batches": self.n_cut_batches, "orders_per_cut_batch": round(self.orders_in_cut_batches / max(1, self.n_cut_batches), 2)} if self.n_cut_batches else None,
            "transport": {"handler_utilization": round(self.handler_busy / (avail * self.handlers.capacity), 3),
                          "forklift_utilization": round(self.forklift_busy / (avail * self.forklifts.capacity), 3),
                          "loaded_distance_m": round(dist_loaded), "empty_distance_m": round(dist_empty),
                          "distance_per_product_m": round((dist_loaded + dist_empty) / max(1, self.produced), 1),
                          "avg_transport_wait_per_batch_min": round(sum(b["transport_wait"] for b in self.batches) / max(1, len(self.batches)), 1)},
            "energy": {"total_kwh": round(energy_kwh), "kwh_per_product": round(energy_kwh / max(1, self.produced), 2),
                       "cost_krw": round(energy_kwh * tariff), "by_asset": energy_by, "tariff_krw_per_kwh": tariff},
            "bottleneck_ranking": [{"station": sid, "score": sc, "utilization": stations[sid]["utilization"],
                                    "avg_queue_wait_min": stations[sid]["avg_queue_wait_min"]} for sc, sid in ranked[:6]],
            "stations": stations,
            "batches": [{k: v for k, v in b.items() if k not in ("steps", "parts", "outsourced_ready", "cart_req")} for b in self.batches],
        }

    def wip_series(self):
        pts = []; wip = 0
        for e in self.events:
            if e["type"] == "release":
                wip += 1; pts.append((e["t"], wip))
            elif e["type"] == "done":
                wip -= 1; pts.append((e["t"], wip))
        return pts


def apply_scenario(factory, scn):
    """시나리오 패치: {"stations": {ID: {...덮어쓰기}}, "add_stations": [...], "remove_stations": [...],
    "transport": {...}, "orders": {...}, "meta": {...}}"""
    f = copy.deepcopy(factory)
    for sid, patch in scn.get("stations", {}).items():
        for s in f["stations"]:
            if s["id"] == sid:
                s.update(patch)
    rm = set(scn.get("remove_stations", []))
    f["stations"] = [s for s in f["stations"] if s["id"] not in rm] + scn.get("add_stations", [])
    for k in ("transport", "orders"):
        if k in scn:
            f[k].update(scn[k])
    if "rules" in scn:
        f["rules"] = {**(f.get("rules") if isinstance(f.get("rules"), dict) else {}), **scn["rules"]}
    if "meta" in scn:
        f["meta"].update(scn["meta"])
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("factory", nargs="?", default=str(pathlib.Path(__file__).parent.parent / "data/sample_factory.json"))
    ap.add_argument("--scenario", help="scenarios/*.json")
    ap.add_argument("--name", default=None)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--days", type=int, default=None)
    ap.add_argument("--out", default=str(pathlib.Path(__file__).parent / "out"))
    a = ap.parse_args()
    factory = json.loads(pathlib.Path(a.factory).read_text(encoding="utf-8"))
    name = a.name or "baseline"; desc = "현재 상태"
    if a.scenario:
        scn = json.loads(pathlib.Path(a.scenario).read_text(encoding="utf-8"))
        factory = apply_scenario(factory, scn)
        name = a.name or scn.get("id", pathlib.Path(a.scenario).stem); desc = scn.get("name", name)
    sim = Sim(factory, seed=a.seed, horizon_days=a.days)
    k = sim.run()
    k["scenario"] = {"id": name, "name": desc}
    outdir = pathlib.Path(a.out) / name; outdir.mkdir(parents=True, exist_ok=True)
    with open(outdir / "events.jsonl", "w", encoding="utf-8") as fp:
        for e in sim.events:
            fp.write(json.dumps(e, ensure_ascii=False) + "\n")
    (outdir / "kpis.json").write_text(json.dumps(k, ensure_ascii=False, indent=1), encoding="utf-8")
    (outdir / "factory.json").write_text(json.dumps(factory, ensure_ascii=False), encoding="utf-8")
    print(f"[{name}] 완료 {k['orders_completed']}/{k['orders_released']} 주문, {k['products_completed']}개 제품, "
          f"리드타임 평균 {k['lead_time_min']['avg']:.0f}분, 병목: {k['bottleneck_ranking'][0]['station']} "
          f"(util {k['bottleneck_ranking'][0]['utilization']:.0%}), 전력 {k['energy']['total_kwh']} kWh")
    return k


if __name__ == "__main__":
    main()
