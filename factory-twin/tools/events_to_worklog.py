"""시뮬레이션 events.jsonl → 공장 작업일보 형태 CSV (batch, product, n_parts, station, arrive, start, end).
라운드트립 테스트용: 이 CSV를 log_to_model.py / trace_validate.py / rule_fit.py 에 넣어 원래 파라미터·구조·규칙이 복원되는지 본다.
세 번째 인자가 있으면 투입 기록(batch, product, qty, release, due)도 쓴다(시트 13 상단 정보에 해당)."""
import json, csv, sys
src, dst = sys.argv[1], sys.argv[2]; rel_dst = sys.argv[3] if len(sys.argv) > 3 else None
cur = {}; rows = []; meta = {}; rel = []
for line in open(src, encoding="utf-8"):
    e = json.loads(line)
    if e["type"] == "release":
        meta[e["batch"]] = (e["product"], e["n_parts"]); rel.append({"batch": e["batch"], "product": e["product"], "qty": e["qty"], "release": e["t"], "due": e.get("due") if e.get("due") is not None else "", "order": e.get("order_t", "")})
    elif e["type"] == "arrive":
        cur[(e["batch"], e["station"])] = {"arrive": e["t"]}
    elif e["type"] == "proc_start":
        cur.setdefault((e["batch"], e["station"]), {})["start"] = e["t"]
    elif e["type"] == "proc_end":
        k = (e["batch"], e["station"]); d = cur.get(k, {})
        p, n = meta.get(e["batch"], ("", ""))
        rows.append({"batch": e["batch"], "product": p, "n_parts": n, "station": e["station"], "arrive": d.get("arrive", ""), "start": d.get("start", ""), "end": e["t"]})
with open(dst, "w", newline="", encoding="utf-8") as fp:
    w = csv.DictWriter(fp, fieldnames=["batch", "product", "n_parts", "station", "arrive", "start", "end"]); w.writeheader(); w.writerows(rows)
print("wrote", dst, len(rows), "rows")
if rel_dst:
    with open(rel_dst, "w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=["batch", "product", "qty", "release", "due", "order"]); w.writeheader(); w.writerows(rel)
    print("wrote", rel_dst, len(rel), "releases")
