#!/usr/bin/env bash
# 통합 테스트: 샘플로 채운 템플릿 → factory.json → 시뮬레이션 → 검증 판정 (코드 경로 검증용)
set -e; cd "$(dirname "$0")/.."
python3 tools/fill_template_from_sample.py data/sample_filled_template.xlsx
python3 tools/templates_to_json.py data/sample_filled_template.xlsx data/sample_from_template.json
python3 tools/test_converter.py data/sample_from_template.json | tail -1   # 변환기 회귀 테스트(알려진 계수 되찾기)
python3 sim/factory_sim.py data/sample_from_template.json --name from_template
python3 sim/validate.py sim/out/from_template/kpis.json sim/out/from_template/factory.json || true
python3 tools/data_quality.py data/sample_from_template.json sim/out/sensitivity.md 2>/dev/null | sed -n '1,12p'
# 구조·규칙·리듬 도구 자체 검증 — 판정까지 (리뷰 22 P-7). 샘플 공장 40일 baseline(seed 1)을 기준으로 한다
python3 sim/factory_sim.py data/sample_factory.json --name baseline --seed 1 >/dev/null
python3 tools/events_to_worklog.py sim/out/baseline/events.jsonl sim/out/baseline/worklog.csv sim/out/baseline/releases.csv >/dev/null
python3 tools/trace_validate.py data/sample_factory.json sim/out/baseline/worklog.csv --releases sim/out/baseline/releases.csv --seeds 1 --level L0 --out sim/out/baseline/trace_validate_L0.md >/dev/null
PASS=$(grep -c "| 통과 |" sim/out/baseline/trace_validate_L0.md); echo "구조 검증 L0 통과 스테이션: $PASS / 16"; [ "$PASS" -ge 12 ] || { echo "FAIL: 올바른 구조의 L0 통과 수 < 12"; exit 1; }
python3 tools/rule_fit.py sim/out/baseline/worklog.csv --releases sim/out/baseline/releases.csv --factory data/sample_factory.json --out sim/out/baseline/rule_fit.md | grep "판정" | grep -q "FIFO" || { echo "FAIL: FIFO 공장에서 FIFO 판정 아님"; exit 1; }
echo "규칙 재현율(FIFO 공장): $(grep '전체\*\*' sim/out/baseline/rule_fit.md | cut -c1-80)"
python3 tools/hourly_profile.py sim/out/baseline/worklog.csv --cycle --factory data/sample_factory.json | grep "능률 배수 범위" | grep -q "생략 가능" || { echo "FAIL: 리듬 없는 시뮬에서 hourly_factor 반영 판정"; exit 1; }
echo "시간대 능률: 리듬 없음 → 생략 판정 OK"
echo "테스트 체인 전부 통과"
