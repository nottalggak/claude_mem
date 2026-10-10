#!/usr/bin/env bash
# 맥미니(로컬) 최초 셋업: 가상환경 → 의존성 → 전체 테스트 체인 → 뷰어 안내
# 사용: cd factory-twin && bash tools/setup_local.sh
set -e; cd "$(dirname "$0")/.."
python3 --version
[ -d .venv ] || python3 -m venv .venv
source .venv/bin/activate
pip install -q --upgrade pip && pip install -q -r requirements.txt
echo "== 샘플 공장 생성 + 1회 시뮬 (약 30초)"
python3 data/build_sample.py
python3 sim/factory_sim.py data/sample_factory.json --name baseline --seed 1
echo "== 템플릿 → JSON → 시뮬 → 검증 도구 체인 (약 2분)"
bash tools/test_chain.sh | tail -6
echo
echo "완료. 뷰어: python3 -m http.server 8000  →  http://localhost:8000/viewer/"
echo "전체 비교표(5 seed, 약 10분): python3 sim/compare.py --seeds 5"
echo "민감도/불확실성(각 10~30분): python3 sim/sensitivity.py --seeds 2 ; python3 sim/uncertainty.py --B 20 --R 2"
