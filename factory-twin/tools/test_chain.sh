#!/usr/bin/env bash
# 통합 테스트: 샘플로 채운 템플릿 → factory.json → 시뮬레이션 → 검증 판정 (코드 경로 검증용)
set -e; cd "$(dirname "$0")/.."
python3 tools/fill_template_from_sample.py data/sample_filled_template.xlsx
python3 tools/templates_to_json.py data/sample_filled_template.xlsx data/sample_from_template.json
python3 sim/factory_sim.py data/sample_from_template.json --name from_template
python3 sim/validate.py sim/out/from_template/kpis.json sim/out/from_template/factory.json || true
python3 tools/data_quality.py data/sample_from_template.json sim/out/sensitivity.md 2>/dev/null | sed -n '1,12p'
