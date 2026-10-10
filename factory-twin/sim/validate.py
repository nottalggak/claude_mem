"""복제 검증: kpis.json 을 factory.json 의 observations.validation 과 비교해 허용 오차 통과 여부를 표로 낸다.
허용 오차의 유일한 기준은 docs/03_공장복제_명세서.md §1.2 (v0.5 진단 / v1 복제). 시트 18 → tools/templates_to_json.py 가 아래 형식으로 내보낸다.
  {"metric": "products_completed", "actual": 1100, "tolerance_pct": 10, "source": "출하장 2주", "stage": "v0.5"}
  {"metric": "stations.EB2.utilization", "actual": 0.82, "tolerance_abs": 0.10, "source": "CT 2주"}
  {"metric": "lead_time_work_min_avg", "actual": 520, "tolerance_pct": 15, "source": "13_배치추적·2주 양식"}
  {"metric": "avg_wip_batches", "actual": 12, "tolerance_pct": 20, "source": "14_WIP센서스"}
  {"metric": "bottleneck_ranking.0.station", "actual": "EB2", "source": "센서스·카메라"}
입력에 쓴 데이터로 검증하지 말 것 (끼워맞춤 방지)."""
import json, sys, pathlib


def get(d, path):
    for k in path.split("."):
        d = d[int(k)] if isinstance(d, list) else d[k]
    return d


def validate(kpis, obs):
    rows = []; ok_all = True
    for o in obs:
        try:
            model = get(kpis, o["metric"])
        except (KeyError, IndexError, TypeError):
            rows.append((o["metric"], o.get("actual"), "없음", "-", "지표 없음", o.get("source", ""))); ok_all = False; continue
        actual = o.get("actual")
        if isinstance(actual, str):
            ok = (model == actual); diff = "-"
        else:
            diff = model - actual
            if "tolerance_abs" in o:
                ok = abs(diff) <= o["tolerance_abs"]
            else:
                ok = abs(diff) <= abs(actual) * o.get("tolerance_pct", 10) / 100 if actual else abs(diff) < 1e-9
            diff = f"{diff:+.2f} ({diff / actual * 100:+.0f}%)" if actual else f"{diff:+.2f}"
        ok_all &= ok
        rows.append((o["metric"], actual, model, diff, "통과" if ok else "실패", o.get("source", "")))
    return ok_all, rows


def main():
    kp = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).parent / "out/baseline/kpis.json"
    fp = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else kp.parent / "factory.json"
    kpis = json.loads(kp.read_text(encoding="utf-8")); factory = json.loads(fp.read_text(encoding="utf-8"))
    obs = factory.get("observations", {}).get("validation", [])
    if not obs:
        print("observations.validation 이 비어 있음 → 검증 불가. 배치추적·센서스·출하일지·고지서 값을 factory.json 에 넣으세요."); return 2
    ok, rows = validate(kpis, obs)
    print("| 지표 | 실제 | 모델 | 차이 | 판정 | 출처 |\n|---|---|---|---|---|---|")
    for r in rows:
        print("| " + " | ".join(str(x) for x in r) + " |")
    print("\n결과:", "복제 검증 통과" if ok else "검증 실패 → 03_공장복제_명세서 §8 보정 순서(구조→결정적 시간→변동→규칙)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
