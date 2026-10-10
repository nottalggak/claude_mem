#!/usr/bin/env bash
# 전체 파이프라인: 샘플 데이터 생성 → 시나리오 시뮬레이션 → 뷰어 서빙
set -e
cd "$(dirname "$0")"
pip install -q -r requirements.txt
python3 data/build_sample.py
python3 sim/compare.py --seeds 5
echo
echo "뷰어: http://localhost:8000/viewer/  (Ctrl+C 로 종료)"
python3 -m http.server 8000
