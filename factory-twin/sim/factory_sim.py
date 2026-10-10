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

BOARD_AREA = 2.44 * 1.22
YIELD = 0.78


def hhmm(s):
    h, m = s.split(":"); return int(h) * 60 + int(m)


class Shift:
    def __init__(self, env, meta):
        self.env = env
        self.start, self.end = hhmm(meta["shift"]["start"]), hhmm(meta["shift"]["end"])
        self.breaks = [(hhmm(a), hhmm(b)) for a, b in meta["shift"].get("breaks", [])]
        self.day_min = 24 * 60

    def working(self, t):
        m = t % self.day_min
        if not (self.start <= m < self.end):
            return False
        return not any(a <= m < b for a, b in self.breaks)

    def next_open(self, t):
        if self.working(t):
            return t
        day = (t // self.day_min) * self.day_min; m = t - day
        if m < self.start:
            return day + self.start
        for a, b in self.breaks:
            if a <= m < b:
                return day + b
        return day + self.day_min + self.start

    def wait(self):
        t = self.env.now; n = self.next_open(t)
        if n > t:
            return self.env.timeout(n - t)
        return self.env.timeout(0)

    def worked_minutes(self, horizon):
        return sum(1 for t in range(int(horizon)) if self.working(t))


class Station:
    def __init__(self, env, spec, sim):
        self.env, self.spec, self.sim = env, spec, sim
        self.id = spec["id"]; self.process = spec["process"]
        self.cap = spec.get("capacity", 1)
        self.res = simpy.Resource(env, capacity=self.cap)
        self.buffer = simpy.Resource(env, capacity=max(1, spec.get("buffer_batches", 4)) + self.cap)
        self.down = False
        self.last_product = None
        self.busy_min = 0.0; self.setup_min = 0.0; self.down_min = 0.0; self.blocked_min = 0.0
        self.n_batches = 0; self.n_parts = 0; self.wait_total = 0.0; self.waits = []
        self.queue_len = 0; self.queue_series = [(0.0, 0)]
        self.state = "idle"
        if spec.get("mtbf_min", 0) > 0 and self.process not in ("raw", "fg"):
            env.process(self.breakdowns())

    def log_state(self, state):
        self.state = state
        self.sim.ev({"type": "state", "station": self.id, "state": state})

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
        for k, v in c.get("per_unit", {}).items():
            t += v * part.get(k, 0)
        if "per_product" in c:
            t += c["per_product"].get(product, 0)
        cv = c.get("cv", 0)
        if cv > 0 and t > 0:
            sigma = math.sqrt(math.log(1 + cv * cv)); mu = math.log(t) - sigma * sigma / 2
            t = self.sim.rng.lognormvariate(mu, sigma)
        return t

    def set_queue(self, delta):
        self.queue_len += delta
        self.queue_series.append((self.env.now, self.queue_len))
        self.sim.ev({"type": "queue", "station": self.id, "len": self.queue_len})


class Sim:
    def __init__(self, factory, seed=1, horizon_days=None):
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
        self.horizon = self.horizon_days * 24 * 60
        self.products = {p["id"]: p for p in factory["products"]}
        self.scrap = 0; self.produced = 0
        self.cut_pool = {}; self.cut_timers = {}; self.n_cut_batches = 0; self.orders_in_cut_batches = 0

    def ev(self, e):
        e["t"] = round(self.env.now, 2); self.events.append(e)

    # ---------- 주문 생성 ----------
    def gen_orders(self):
        o = self.f["orders"]
        oid = 0
        if o.get("mode") == "list":
            for od in o["list"]:
                yield self.env.timeout(max(0, od["release_min"] - self.env.now))
                oid += 1; self.env.process(self.order_entry(oid, od["product"], od["qty"], od.get("due_min")))
            return
        mix = o["mix"]; keys = list(mix); wts = [mix[k] for k in keys]
        il = o.get("install_lead_days")
        for day in range(self.horizon_days):
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
                    lead_days = self.rng_orders.triangular(il["min"], il["max"], il["mode"])
                    due = (day + lead_days) * 1440 + self.shift.end  # 시공일 종업 시각
                self.env.process(self.order_entry(oid, pid, qty, due))

    def order_entry(self, oid, pid, qty, due=None):
        """고객 주문 접수 → (시공일 역산) 투입 시점까지 대기 → 외주 발주 → 재단 배치 풀 또는 즉시 흐름"""
        o = self.f["orders"]
        prod = self.products[pid]
        parts = self.expand(pid, qty)
        batch = {"id": f"B{oid:03d}", "product": pid, "qty": qty, "n_parts": len(parts), "order_t": self.env.now, "due": due,
                 "transport_wait": 0.0, "transport_dist": 0.0, "queue_wait": 0.0, "proc_time": 0.0, "outsourced_wait": 0.0, "steps": [],
                 "color": prod.get("color", "-"), "thickness": prod.get("thickness", 18), "parts": parts}
        self.batches.append(batch)
        batch["outsourced_ready"] = {}
        for ou in self.f.get("outsourced", []):
            if pid in ou["products"] and ou.get("order_at") == "order":
                batch["outsourced_ready"][ou["id"]] = self.env.now + self.outsourced_lead(ou)
        if due is not None and o.get("install_lead_days", {}).get("start_before_days"):
            rel = due - o["install_lead_days"]["start_before_days"] * 1440
            if rel > self.env.now:
                yield self.env.timeout(rel - self.env.now)
        batch["release"] = self.env.now
        self.ev({"type": "release", "batch": batch["id"], "product": pid, "qty": qty, "n_parts": len(parts), "due": due})
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
        self.produced += batch["qty"]
        self.ev({"type": "done", "batch": batch["id"], "lead_min": round(batch["lead_min"], 1), "late_min": round(batch["late_min"], 1)})

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
            yield self.env.process(self.move(batch, cur_pos, tuple(st.spec["in_pos"]), use_fork))
            self.ev({"type": "arrive", "batch": batch["id"], "station": st.id, "pos": st.spec["in_pos"]})
            if proc == "fg":
                break
            st.set_queue(+1)
            t_q = self.env.now
            with st.res.request() as rq:
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
                st.log_state("busy")
                self.ev({"type": "proc_start", "station": st.id, "batch": batch["id"], "pos": st.spec["pos"]})
                t_start = self.env.now
                if st.spec.get("batch_time_min"):
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
        energy_kwh = 0.0; energy_by = {}
        anc_on = {a["id"]: 0.0 for a in self.f.get("ancillary", [])}
        for st in self.stations.values():
            sp = st.spec
            if st.process in ("raw", "fg"):
                continue
            cap_avail = avail * st.cap
            util = (st.busy_min + st.setup_min) / cap_avail if cap_avail else 0
            idle = max(0, cap_avail - st.busy_min - st.setup_min - st.down_min)
            kwh = sp.get("rated_kw", 0) * sp.get("load_factor", 0.6) * st.busy_min / 60 + sp.get("idle_kw", 0) * idle / 60
            energy_by[st.id] = round(kwh, 1); energy_kwh += kwh
            for aid in sp.get("ancillary", []):
                anc_on[aid] = max(anc_on.get(aid, 0), st.busy_min + st.setup_min)
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
        for a in self.f.get("ancillary", []):
            if a["mode"] == "when_any_on":
                # 연결된 기계 중 하나라도 돌면 가동 → 연결 기계 가동시간 합의 상한을 근사 (보수적으로 최대값*1.3, 교대시간 이하)
                on = min(avail, anc_on.get(a["id"], 0) * 1.3)
            elif a["mode"] == "shift":
                on = avail
            else:
                on = self.horizon
            kwh = a["rated_kw"] * a.get("load_factor", 0.7) * on / 60
            energy_by[a["id"]] = round(kwh, 1); energy_kwh += kwh
        base = self.f["meta"].get("energy", {}).get("base_load_kw", 0) * shift_hours
        energy_by["BASE"] = round(base, 1); energy_kwh += base
        tariff = self.f["meta"].get("energy", {}).get("tariff_krw_per_kwh", 160)
        done = [b for b in self.batches if "done" in b]
        released = [b for b in self.batches if "release" in b]
        warm = min(5, max(0, self.horizon_days // 3)) * 1440
        steady_days = (self.horizon - warm) / 1440
        tp_steady = sum(b["qty"] for b in done if b["done"] >= warm) / max(1e-9, steady_days)
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
            "products_completed": self.produced,
            "throughput_products_per_day": round(self.produced / self.horizon_days, 1),
            "throughput_steady_per_day": round(tp_steady, 1), "warmup_days": warm / 1440,
            "lead_time_work_min_avg": round(sum(b["lead_work_min"] for b in done) / max(1, len(done)), 1),
            "lead_time_min": {"avg": round(sum(b["lead_min"] for b in done) / max(1, len(done)), 1),
                              "p90": round(sorted(b["lead_min"] for b in done)[int(0.9 * (len(done) - 1))], 1) if done else 0,
                              "max": round(max([b["lead_min"] for b in done] + [0]), 1)},
            "avg_wip_batches": round(sum(w for _, w in wip_series) / max(1, len(wip_series)), 2),
            "scrap_parts": self.scrap,
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
            "batches": [{k: v for k, v in b.items() if k not in ("steps", "parts", "outsourced_ready")} for b in self.batches],
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
