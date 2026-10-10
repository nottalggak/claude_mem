"""데이터 품질 스코어카드: factory.json 의 각 파라미터가 '측정/기록/추정' 중 무엇에서 왔는지 집계하고,
민감도 상위 파라미터가 추정에 머물러 있으면 경고한다.
provenance 는 factory.json 의 "provenance": {"CUT1.cycle": "measured", "EB2.setup_min": "record", ...} 로 기록한다.
값: measured(현장 측정) / record(공장 기록) / interview(인터뷰) / estimated(추정·기본값)"""
import json, sys, pathlib, re

WEIGHTS = {"measured": 1.0, "record": 0.8, "interview": 0.5, "estimated": 0.0}


def main(fp, sens_md=None):
    f = json.loads(pathlib.Path(fp).read_text(encoding="utf-8"))
    prov = f.get("provenance", {})
    keys = []
    for s in f["stations"]:
        if s["process"] in ("raw", "fg"):
            continue
        for k in ("cycle", "setup_min", "mtbf_min", "mttr_min", "buffer_batches", "rated_kw", "load_factor", "scrap_rate", "workers_required", "pos"):
            if k in s:
                keys.append(f"{s['id']}.{k}")
    keys += ["transport.handlers", "transport.handler_speed_mps", "transport.load_unload_min", "orders.batch_size", "orders.orders_per_day", "orders.mix", "meta.shift", "meta.energy.tariff_krw_per_kwh"]
    for a in f.get("ancillary", []):
        keys += [f"{a['id']}.rated_kw", f"{a['id']}.mode"]
    rows = [(k, prov.get(k, "estimated")) for k in keys]
    score = sum(WEIGHTS[p] for _, p in rows) / max(1, len(rows))
    top = []
    if sens_md and pathlib.Path(sens_md).exists():
        for line in pathlib.Path(sens_md).read_text(encoding="utf-8").splitlines():
            m = re.match(r"\| (\d+) \| ([^ |(]+)", line)
            if m and int(m.group(1)) <= 10:
                top.append(m.group(2))
    print(f"# 데이터 품질 스코어카드 — {f['meta'].get('name')}\n")
    print(f"전체 신뢰 점수: {score:.2f} / 1.00  (measured=1, record=0.8, interview=0.5, estimated=0)\n")
    cnt = {}
    for _, p in rows:
        cnt[p] = cnt.get(p, 0) + 1
    print("| 출처 | 파라미터 수 |\n|---|---|")
    for p, c in sorted(cnt.items(), key=lambda x: -x[1]):
        print(f"| {p} | {c} |")
    warn = [k for k, p in rows if p == "estimated" and any(k.startswith(t.split(".")[0] + "." + t.split(".")[1].split("(")[0]) for t in top)]
    if top:
        print("\n민감도 상위 10개 중 아직 '추정'인 파라미터 (→ 2주 로깅·2차 방문 재측정 1순위):")
        for k in warn or ["(없음)"]:
            print("-", k)
    print("\n'추정' 전체 목록:")
    for k, p in rows:
        if p == "estimated":
            print("-", k)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/home/user/claude_mem/factory-twin/data/sample_factory.json", sys.argv[2] if len(sys.argv) > 2 else "/home/user/claude_mem/factory-twin/sim/out/sensitivity.md")
