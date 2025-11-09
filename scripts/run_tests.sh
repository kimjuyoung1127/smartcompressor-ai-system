#!/bin/bash
# 테스트 실행 스크립트

echo "=========================================="
echo "테스트 실행"
echo "=========================================="
echo ""

# 가상 환경 활성화 (있는 경우)
if [ -d "venv" ]; then
    echo "가상 환경 활성화 중..."
    source venv/bin/activate
fi

# pytest 설치 확인
echo "pytest 설치 확인 중..."
python3 -m pip show pytest > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "pytest가 설치되지 않았습니다. 설치 중..."
    python3 -m pip install pytest pytest-cov pytest-asyncio
fi

echo ""
echo "테스트 실행 중..."
echo ""

# 테스트 실행
python3 -m pytest tests/ \
    --cov=services/anomaly_detection_modules \
    --cov=services/performance_optimizer \
    --cov=services/realtime_dashboard_service \
    --cov-report=html \
    --cov-report=term \
    -v

echo ""
echo "=========================================="
echo "테스트 완료"
echo "=========================================="
echo ""
echo "커버리지 리포트: htmlcov/index.html"

