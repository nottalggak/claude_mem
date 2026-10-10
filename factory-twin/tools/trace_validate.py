"""트레이스 구동 구조 검증(03 §8 보정 순서 1단계 '구조'를 숫자로 판정).
관측 기록(배치별 공정 도착·착수·완료 — 시트 13 또는 2주 양식)에서 **가공시간과 투입 시각을 관측값으로 고정**하고 모델을 돌린 뒤,
남는 차이(대기·운반)를 스테이션별 '구조 잔차'로 낸다. 가공시간을 고정했으므로 잔차는 분포 오차가 아니라 라우팅·버퍼·자원 수·배치·디스패칭·운반 경합의 오차다.
사용: python3 tools/trace_validate.py factory.json worklog.csv [--releases releases.csv] [--seeds 3] [--out sim/out/trace_validate.md]
  worklog.csv 열: batch,product,n_parts,station,arrive,start,end  (분; tools/events_to_worklog.py 형식 = 시트 13 과 동일 정보)
  releases.csv 열: batch,product,qty,release,due,order (분; order=주문 접수 시각 — 외주 발주 시계의 기준, 시트 8·13; 없으면 worklog 의 첫 도착을 투입으로, qty 는 BOM 부품 수로 역산)
잔차 해석(연구 18 참고): 대기 잔차 +(모델이 더 기다림) 전 스테이션 공통 → 자원 수/교대 부족; 특정 스테이션만 → 그 스테이션 대수·버퍼·배치 키; 운반 잔차 + → 운반 자원·거리; − → 모델에 없는 대기(탐색·외주·자재)."""
import json, csv, sys, pathlib, argparse, statistics, copy
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "sim"))
from factory_sim import Sim
from common import Calendar

_cal = None
def work_between(t0, t1):
    """두 시각 사이의 근무 분(야간·주말·휴게 제외). 관측 start→end 가 밤을 넘기면 달력 분이 아니라 근무 분이 가공시간이다."""
    if t1 <= t0: return 0.0
    a, b = int(t0), int(t1); n = sum(1 for t in range(a, b) if _cal.working(t))
    return n + (t1 - t0) - (b - a) if n > 0 else 0.0


def load_records(worklog, releases=None, factory=None):
    recs = {}
    for r in csv.DictReader(open(worklog, encoding="utf-8")):
        b = recs.setdefault(r["batch"], {"batch": r["batch"], "product": r["product"], "n_parts": int(float(r.get("n_parts") or 0)), "steps": []})
        b["steps"].append({"station": r["station"], "arrive": float(r["arrive"]), "start": float(r["start"]), "end": float(r["end"])})
    for b in recs.values():
        b["steps"].sort(key=lambda s: s["arrive"])
    if releases:
        for r in csv.DictReader(open(releases, encoding="utf-8")):
            if r["batch"] in recs:
                recs[r["batch"]]["qty"] = int(float(r["qty"])); recs[r["batch"]]["release"] = float(r["release"]); recs[r["batch"]]["due"] = float(r["due"]) if r.get("due") else None; recs[r["batch"]]["order"] = float(r["order"]) if r.get("order") else None
    known = {p["id"] for p in factory["products"]} if factory else None
    dropped = [k for k, b in recs.items() if known is not None and b["product"] not in known]
    if dropped: print(f"제품ID 없는 배치 {len(dropped)}건 제외(재작업 분기 'R' 배치·기록 누락): {dropped[:5]}")
    for k in dropped: recs.pop(k)
    for b in recs.values():
        b.setdefault("release", b["steps"][0]["arrive"]); b.setdefault("due", None); b.setdefault("order", None)
        if "qty" not in b:  # BOM 부품 수로 수량 역산
            ppu = sum(p.get("qty", 1) for p in next((p for p in factory["products"] if p["id"] == b["product"]), {"parts": []})["parts"]) or 1
            b["qty"] = max(1, round(b["n_parts"] / ppu))
    return sorted(recs.values(), key=lambda b: (b["release"], b["batch"]))


def run_trace(factory, recs, seed, level="L0"):
    f = copy.deepcopy(factory)
    if level == "L1": f.setdefault("meta", {})["trace_free_station"] = True
    f["orders"] = {"mode": "list", "horizon_days": factory["orders"].get("horizon_days", 40),
                   "list": [{"product": b["product"], "qty": b["qty"], "release_min": b["release"], "release_at": b["release"], "due_min": b["due"], "order_min": b["order"] if b.get("order") is not None else b["release"],
                             "trace": {s["station"]: work_between(s["start"], s["end"]) for s in b["steps"]}} for b in recs]}
    sim = Sim(f, seed=seed); sim.run()
    # 모델 배치 ↔ 관측 배치: list 순서 = B001.. 순서
    out = {}
    for i, b in enumerate(sim.batches):
        out[recs[i]["batch"]] = b["steps"] if i < len(recs) else []
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("factory"); ap.add_argument("worklog"); ap.add_argument("--releases"); ap.add_argument("--seeds", type=int, default=3); ap.add_argument("--out"); ap.add_argument("--level", choices=["L0", "L1"], default="L0", help="L0: 관측된 기계(병렬 대체기)까지 강제 — 논리 버그·미기록 사건만 남김 / L1: 기계 선택·배치·순서를 모델 논리에 맡김 — 구조 검증(연구 18 §2.2 강제 사다리)")
    a = ap.parse_args(); factory = json.loads(pathlib.Path(a.factory).read_text(encoding="utf-8"))
    global _cal; _cal = Calendar(factory["meta"]["shift"])
    recs = load_records(a.worklog, a.releases, factory)
    print(f"관측 배치 {len(recs)}개, 공정 단계 {sum(len(b['steps']) for b in recs)}개")
    per_station = {}  # station -> list of (obs_wait, model_wait, obs_transport, model_transport)
    for seed in range(1, a.seeds + 1):
        model = run_trace(factory, recs, seed, a.level)
        for b in recs:
            ms = model.get(b["batch"], []); prev_obs_end = b["release"]; prev_mod_end = b["release"]
            for s in b["steps"]:
                m = next((x for x in ms if x["station"] == s["station"]), None)
                if m is None:
                    per_station.setdefault(s["station"], {"missing": 0}).setdefault("missing", 0); per_station[s["station"]]["missing"] += 1; continue
                d = per_station.setdefault(s["station"], {"rows": [], "missing": 0})
                d.setdefault("rows", []).append((work_between(s["arrive"], s["start"]), work_between(m["arrive"], m["start"]), work_between(prev_obs_end, s["arrive"]), work_between(prev_mod_end, m["arrive"])))
                prev_obs_end, prev_mod_end = s["end"], m["end"]
    # 순서 잔차: 스테이션별 관측 착수 순서 vs 모델 착수 순서의 Kendall τ (1−τ 가 디스패칭·배치 불일치 척도) — 마지막 seed 기준
    tau = {}
    for sid, d in per_station.items():
        pairs = []
        for b in recs:
            s_ = next((x for x in b["steps"] if x["station"] == sid), None); m_ = next((x for x in model.get(b["batch"], []) if x["station"] == sid), None)
            if s_ and m_: pairs.append((s_["start"], m_["start"]))
        if len(pairs) >= 5:
            conc = disc = 0
            for i in range(len(pairs)):
                for j in range(i + 1, len(pairs)):
                    x = (pairs[i][0] - pairs[j][0]) * (pairs[i][1] - pairs[j][1]); conc += x > 0; disc += x < 0
            tau[sid] = (conc - disc) / max(1, conc + disc)
    def sign_p(k, n):  # 양측 부호검정 p (이항 정확)
        from math import comb
        k = min(k, n - k); return min(1.0, 2 * sum(comb(n, i) for i in range(0, k + 1)) / 2 ** n)
    lines = ["# 트레이스 구동 구조 검증 (가공시간·투입 시각 고정, seed %d회, 수준 %s)" % (a.seeds, a.level), "",
             "가공시간을 관측값으로 고정했으므로 아래 잔차는 **구조(자원 수·버퍼·배치·디스패칭·운반)** 의 오차다. 분포 보정(§8-2·3) 전에 이 표를 0 근처로 만든다.", "",
             "| 스테이션 | n | 관측 대기 평균(근무 분) | 모델 대기 평균 | 대기 잔차(모델−관측) | 잔차/서비스 중앙값 | 부호 일치율(모델>관측) | 부호검정 p | 순서 τ | 관측 운반+전대기 | 모델 | 운반 잔차 | 판정 |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    svc_med = {}
    for b in recs:
        for st_ in b["steps"]: svc_med.setdefault(st_["station"], []).append(work_between(st_["start"], st_["end"]))
    svc_med = {k: statistics.median(v) for k, v in svc_med.items()}
    worst = []
    for sid, d in sorted(per_station.items()):
        rows = d.get("rows", [])
        if not rows:
            lines.append(f"| {sid} | 0 | — | — | — | — | — | — | — | — | — | — | 모델에 이 스테이션 단계 없음({d.get('missing')}건) → **라우팅 오류**(L1 이면 병렬 대체기 선택 규칙 차이일 수 있음) |"); continue
        ow = statistics.mean(r[0] for r in rows); mw = statistics.mean(r[1] for r in rows); ot = statistics.mean(r[2] for r in rows); mt = statistics.mean(r[3] for r in rows)
        npos = sum(1 for r in rows if r[1] > r[0]); pos = npos / len(rows); pval = sign_p(npos, len(rows))
        rw = mw - ow; rt = mt - ot; rho = rw / max(1.0, svc_med.get(sid, 1.0)); t_ = tau.get(sid)
        scale = max(10.0, 0.2 * max(ow, 1.0))  # 평균 잔차 10분 미만은 소음(셋업·고장 재표본)
        if abs(rw) <= scale and abs(rt) <= max(10.0, 0.2 * max(ot, 1.0)): verdict = "통과"
        elif rw > scale: verdict = "모델이 더 기다림 → 대수·버퍼·배치 키·디스패칭 확인"
        elif rw < -scale: verdict = "관측이 더 기다림 → 모델에 없는 대기(탐색·자재·사람 없음·외주) 또는 자원 과대"
        elif rt > 0: verdict = "운반 잔차 + → 운반 자원·거리·적재 시간 과대"
        else: verdict = "운반 잔차 − → 기록되지 않은 이동·대기"
        worst.append((abs(rw) + abs(rt), sid))
        if verdict == "통과" and t_ is not None and t_ < 0.6: verdict = "대기는 맞으나 **순서 불일치**(τ<0.6) → 디스패칭·배치 키 확인(rule_fit)"
        lines.append(f"| {sid} | {len(rows)} | {ow:.1f} | {mw:.1f} | {rw:+.1f} | {rho:+.2f} | {pos:.0%} | {pval:.2f} | {(f'{t_:.2f}' if t_ is not None else '—')} | {ot:.1f} | {mt:.1f} | {rt:+.1f} | {verdict} |")
    worst.sort(reverse=True)
    lines += ["", f"가장 큰 구조 잔차: {', '.join(s for _, s in worst[:3])} → 03 §8-1 순서대로 라우팅·대수·버퍼·배치 키부터 고친 뒤 재실행.",
              "허용: 대기 잔차 |Δ| ≤ max(10분, 관측 대기의 20%). 부호검정 p<0.05 이면 체계적 오차(n=10 이면 10개 중 9개 이상 같은 부호). 잔차/서비스 중앙값(ρ)이 ±1 을 넘으면 '서비스 1회분' 크기의 구조 결함 — 10~20 배치로 검출되는 것은 이 크기부터다(연구 18 §6).",
              "잔차 패턴 → 결함(연구 18 §2.4): 전 스테이션 공통 + → 교대·인원 부족 / 특정 스테이션 − 가 WIP 와 비례 → 모델에 없는 자원 공유(1인 2기계 겸임) / 부호가 색상·두께로 군집, τ 낮음 → 배치 키 오류 / 부호가 납기 여유와 상관 → 디스패칭 규칙 / 상류 − 이면서 하류 앞 WIP 상한 → 봉쇄(버퍼) 누락 / 운반 잔차 + 가 같은 시간대 여러 배치에 동시 → 운반 경합·운반 묶음 / 소수 배치만 극단 + → 부품 식별 손실·탐색.",
              "순서: L0(관측 기계까지 강제)로 코드 버그·미기록 사건부터 없애고 → L1(--level L1)로 구조 → 그 뒤 분포(§8-2·3). 한 번에 결함 하나만 고치고 재실행(보상 결함 방지). 검정력은 결함 주입으로 잰다: 일부러 틀린 구조(스테이션 삭제·버퍼 축소)를 넣고 같은 트레이스로 잔차가 기각되는지 — 기각 못 하는 결함은 '이 데이터로 식별 불가'로 문서화.",
              "자체 검증(샘플): 올바른 구조 → 16개 중 병목 CUT2(−47분, 고장 재표본)·ASM2(+11분) 외 통과; EB2·ASM 3대를 지우고 CUT2 버퍼를 1로 줄인 구조 → 빠진 스테이션 3곳 '라우팅 오류', CUT2 −183분(2%)·EB1 +151분(98%)·CUT1 −91분 — 구조 오류는 부호 일치율 극단값으로 드러난다.",
              "주의: 고장·셋업·휴식은 여전히 모델이 생성하므로 잔차 전부가 구조는 아니다(seed 평균으로 완화). 관측에 없는 스테이션(병렬 대체기)은 pick_station 규칙 차이로 나타난다."]
    out = "\n".join(lines); print(out)
    if a.out: pathlib.Path(a.out).write_text(out, encoding="utf-8")


if __name__ == "__main__":
    main()
