"""변환기 회귀 테스트: 픽스처(알려진 계수로 채운 템플릿)를 변환해 되찾은 파라미터가 참값 근처인지 확인.
사용: python3 tools/test_converter.py data/sample_from_template.json   (test_chain.sh 가 호출)
픽스처 참값(tools/fill_template_from_sample.py): EB1 v_f=12, EB2 v_f=8, G=0.45, γ0=0.08, γ1=0.15; 보링 0.5+0.035·홀; 대차 6대."""
import json, sys, pathlib
f = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
st = {s["id"]: s for s in f["stations"]}
fails = []
def check(name, ok, detail):
    print(("PASS " if ok else "FAIL ") + name + " " + detail)
    if not ok: fails.append(name)
for sid, vf in (("EB1", 12), ("EB2", 8)):
    c = st[sid]["cycle"]; pu = c.get("per_unit", {})
    check(f"{sid} 엣지 물리항 분기", "edges_m" in pu and c.get("form", "").startswith("edge"), str(c))
    check(f"{sid} edges_m = 1/v_f", abs(pu.get("edges_m", 0) - 1 / vf) < 1e-3, f"{pu.get('edges_m')} vs {1/vf:.4f}")
    g1 = pu.get("n_edges", 0) - 0.45 / vf  # n_edges = G/v_f + γ1
    check(f"{sid} γ1 ≈ 0.15 (±0.08)", abs(g1 - 0.15) < 0.08, f"γ1={g1:.3f}")
    check(f"{sid} γ0 ≈ 0.08 (0~0.25)", 0 <= c["base_min"] <= 0.25, f"γ0={c['base_min']}")
    check(f"{sid} n ≥ 10 (첫 사이클 1개 버림)", c.get("n", 0) >= 10, f"n={c.get('n')}")
b = st["BOR1"]["cycle"]
check("BOR1 홀 수 회귀", abs(b.get("per_unit", {}).get("holes", 0) - 0.035) < 0.012 and abs(b["base_min"] - 0.5) < 0.15, str(b))
check("대차 수 → transport.carts", f["transport"].get("carts") == 6, str(f["transport"].get("carts")))
check("운반 인원 ≠ 대차 수", f["transport"].get("handlers") != 6, str(f["transport"].get("handlers")))
prov = f.get("provenance", {})
check("출처 자동 생성", len(prov) > 20 and prov.get("EB1.cycle") == "measured", f"{len(prov)}개, EB1.cycle={prov.get('EB1.cycle')}")
check("주문 이력 → orders_per_day·install_lead_days", f["orders"].get("history_list") and f["orders"].get("install_lead_days", {}).get("mode"), str({k: f["orders"].get(k) for k in ("orders_per_day", "install_lead_days")}))
check("외주 경로 적용 제품", all(o.get("products") for o in f.get("outsourced", [])), str([o.get("products") for o in f.get("outsourced", [])]))
check("규칙(시트 16) → 투입 D-n (픽스처 D-3)", f["orders"].get("install_lead_days", {}).get("start_before_days") == 3, str(f["orders"].get("install_lead_days")))
print(f"\n{len(fails)} 실패" if fails else "\n전부 통과"); sys.exit(1 if fails else 0)
