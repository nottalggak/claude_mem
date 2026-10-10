#!/usr/bin/env bash
# 통합 테스트: 샘플로 채운 템플릿 → factory.json → 시뮬레이션 → 검증 판정 (코드 경로 검증용)
set -e; cd "$(dirname "$0")/.."
python3 tools/fill_template_from_sample.py data/sample_filled_template.xlsx
python3 tools/templates_to_json.py data/sample_filled_template.xlsx data/sample_from_template.json
python3 tools/test_converter.py data/sample_from_template.json | tail -1   # 변환기 회귀 테스트(알려진 계수 되찾기)
python3 sim/factory_sim.py data/sample_from_template.json --name from_template
python3 sim/validate.py sim/out/from_template/kpis.json sim/out/from_template/factory.json || true
python3 tools/data_quality.py data/sample_from_template.json sim/out/sensitivity.md 2>/dev/null | sed -n '1,12p'
# 구조·규칙·리듬 도구 자체 검증(샘플 이벤트 → 작업일보 → 도구)
python3 tools/events_to_worklog.py sim/out/from_template/events.jsonl sim/out/from_template/worklog.csv sim/out/from_template/releases.csv >/dev/null
python3 tools/rule_fit.py sim/out/from_template/worklog.csv --releases sim/out/from_template/releases.csv --out sim/out/from_template/rule_fit.md | grep "전체\*\*"
python3 tools/trace_validate.py sim/out/from_template/factory.json sim/out/from_template/worklog.csv --releases sim/out/from_template/releases.csv --seeds 1 --out sim/out/from_template/trace_validate.md | grep -c "통과" | sed 's/^/구조 검증 통과 스테이션 수: /'
python3 tools/hourly_profile.py sim/out/from_template/worklog.csv --cycle --factory sim/out/from_template/factory.json | tail -1
