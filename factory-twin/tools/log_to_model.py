"""
작업 기록(작업일보/작업실적/바코드 로그) → 모델 파라미터 복원.

입력 CSV 열(최소): batch, station, start, end   (분 단위 숫자 또는 'YYYY-MM-DD HH:MM')
선택 열: product, qty, n_parts, worker, arrive(도착 시각), from_station(직전 공정)
출력: JSON (스테이션별 서비스시간 통계·셋업 추정·대기, 라우팅 변형, from-to 행렬, Little's law 점검)

원리
- 서비스시간 = end - start. 부품 수/수량이 있으면 단위당 시간으로 정규화.
- 셋업 추정: 같은 스테이션에서 직전 배치와 product가 다를 때 (start - 직전 end) 간격의 중앙값 vs 같을 때 간격의 중앙값 차이.
- 대기 = start - arrive (arrive 없으면 직전 공정 end 로 대체 → 운반 포함 대기).
- 라우팅 변형 = batch별 station 순서 문자열의 빈도.
- from-to = (직전 station → station) 횟수.
"""
import csv, json, sys, statistics, math, pathlib, datetime
from collections import defaultdict, Counter


def parse_t(v):
    if v in (None, ""):
        return None
    try:
        return float(v)
    except ValueError:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
            try:
                return datetime.datetime.strptime(v, fmt).timestamp() / 60
            except ValueError:
                pass
    raise ValueError(f"시간 형식 불명: {v}")


def stats(xs):
    if not xs:
        return None
    xs = sorted(xs); n = len(xs); m = statistics.mean(xs)
    sd = statistics.pstdev(xs) if n > 1 else 0
    return {"n": n, "mean": round(m, 2), "sd": round(sd, 2), "cv": round(sd / m, 2) if m else 0,
            "min": round(xs[0], 2), "p50": round(xs[n // 2], 2), "p90": round(xs[int(0.9 * (n - 1))], 2), "max": round(xs[-1], 2)}


def sufficiency(rows):
    """기록의 열 구성으로 어떤 파라미터가 복원 가능한지 진단"""
    has = lambda k: any(r.get(k) is not None for r in rows)
    d = {}
    d["라우팅·변형·from-to"] = "복원 가능" if has("batch") and has("station") else "불가"
    d["가공(서비스) 시간"] = "복원 가능" if has("start") and has("end") else "불가: 완료 시각만 있으면 대기+운반이 섞임 → 착수 시각 기록(바코드 2회 스캔) 또는 시간연구 필요"
    d["대기 시간(순수)"] = "복원 가능" if has("arrive") else "근사: 직전 공정 완료→착수 간격(운반 포함). 도착 시각(대차 도착 스캔)이 있어야 분리"
    d["부품당 시간(믹스 보정)"] = "복원 가능" if has("n_parts") else "불가: 부품 수/수량 열 필요"
    d["셋업 시간"] = "간접 추정(표본 ≥10/10 필요)" if has("product") else "불가: 제품 열 없음 → 직접 기록"
    d["작업자별 가동"] = "복원 가능" if has("worker") else "불가"
    d["고장·결품"] = "불가: 작업 기록엔 보통 없음 → 설비이력·CT 로그"
    return d


def analyze(rows):
    suff = sufficiency(rows)
    rows = sorted(rows, key=lambda r: (r["batch"], r["start"]))
    by_batch = defaultdict(list)
    for r in rows:
        by_batch[r["batch"]].append(r)
    # 라우팅 변형, from-to, 대기
    variants = Counter(); from_to = Counter(); waits = defaultdict(list); lead = {}
    for b, rs in by_batch.items():
        rs.sort(key=lambda r: r["start"])
        variants[">".join(r["station"] for r in rs)] += 1
        for i, r in enumerate(rs):
            prev = rs[i - 1] if i else None
            if prev:
                from_to[(prev["station"], r["station"])] += 1
            arrive = r.get("arrive") if r.get("arrive") is not None else (prev["end"] if prev else r["start"])
            waits[r["station"]].append(max(0, r["start"] - arrive))
        lead[b] = rs[-1]["end"] - rs[0]["start"]
    # 서비스 시간 / 셋업
    by_station = defaultdict(list)
    for r in rows:
        by_station[r["station"]].append(r)
    stations = {}
    for s, rs in by_station.items():
        rs.sort(key=lambda r: r["start"])
        svc = [r["end"] - r["start"] for r in rs]
        per_unit = [(r["end"] - r["start"]) / r["n_parts"] for r in rs if r.get("n_parts")]
        same, diff = [], []
        for i in range(1, len(rs)):
            gap = rs[i]["start"] - rs[i - 1]["end"]
            if gap < 0 or gap > 60:  # 겹침(병렬 기계) 또는 야간/휴식 포함 간격은 제외
                continue
            (same if rs[i].get("product") == rs[i - 1].get("product") else diff).append(gap)
        setup_est = None; setup_conf = "없음"
        if same and diff:
            setup_est = round(max(0.0, statistics.median(diff) - statistics.median(same)), 1)
            setup_conf = "신뢰" if (len(same) >= 10 and len(diff) >= 10) else "낮음(표본 부족: 셋업은 직접 기록 권장)"
        busy = sum(svc); span = rs[-1]["end"] - rs[0]["start"] if len(rs) > 1 else 0
        stations[s] = {"batches": len(rs), "service_min": stats(svc), "service_min_per_part": stats(per_unit) if per_unit else None,
                       "wait_min": stats(waits[s]), "setup_est_min": setup_est, "setup_confidence": setup_conf, "n_same": len(same), "n_product_changes": len(diff),
                       "busy_min": round(busy), "span_min": round(span)}
    n_done = len(lead); horizon = max(r["end"] for r in rows) - min(r["start"] for r in rows)
    tp_per_min = n_done / horizon if horizon else 0
    avg_lead = statistics.mean(lead.values()) if lead else 0
    return {"n_rows": len(rows), "n_batches": len(by_batch), "horizon_min": round(horizon), "data_sufficiency": suff,
            "routing_variants": [{"route": k, "count": v} for k, v in variants.most_common()],
            "from_to": [{"from": a, "to": b, "count": c} for (a, b), c in from_to.most_common()],
            "stations": stations,
            "lead_time_min": stats(list(lead.values())),
            "littles_law": {"throughput_per_min": round(tp_per_min, 4), "avg_lead_min": round(avg_lead, 1),
                            "implied_avg_wip_batches": round(tp_per_min * avg_lead, 2),
                            "note": "현장 WIP 센서스 평균과 비교 → 크게 다르면 기록 누락/리드타임 정의 불일치"}}


def read_csv(path):
    out = []
    with open(path, encoding="utf-8-sig") as fp:
        for r in csv.DictReader(fp):
            out.append({"batch": r["batch"], "station": r["station"], "start": parse_t(r["start"]), "end": parse_t(r["end"]),
                        "product": r.get("product") or None, "n_parts": float(r["n_parts"]) if r.get("n_parts") else None,
                        "arrive": parse_t(r.get("arrive")) if r.get("arrive") else None, "worker": r.get("worker")})
    return out


if __name__ == "__main__":
    src = sys.argv[1]; dst = sys.argv[2] if len(sys.argv) > 2 else None
    res = analyze(read_csv(src))
    txt = json.dumps(res, ensure_ascii=False, indent=1)
    if dst:
        pathlib.Path(dst).write_text(txt, encoding="utf-8"); print("wrote", dst)
    else:
        print(txt)
