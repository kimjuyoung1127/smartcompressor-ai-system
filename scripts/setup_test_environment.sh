#!/bin/bash
# 테스트 환경 설정 스크립트

echo "=========================================="
echo "테스트 환경 설정"
echo "=========================================="
echo ""

# 프로젝트 루트로 이동
cd "$(dirname "$0")/.."
pwd

# 가상 환경 확인
if [ -d "venv" ]; then
    echo "✅ 가상 환경이 이미 존재합니다."
    echo "가상 환경 활성화 중..."
    source venv/bin/activate
else
    echo "⚠️ 가상 환경이 없습니다. 생성 중..."
    python3 -m venv venv
    echo "✅ 가상 환경 생성 완료"
    echo "가상 환경 활성화 중..."
    source venv/bin/activate
fi

echo ""
echo "Python 경로: $(which python)"
echo "pip 경로: $(which pip)"
echo ""

# pytest 설치
echo "pytest 설치 중..."
pip install --upgrade pip
pip install pytest pytest-cov pytest-asyncio

echo ""
echo "=========================================="
echo "설정 완료!"
echo "=========================================="
echo ""
echo "다음 명령어로 테스트를 실행하세요:"
echo "  pytest tests/"
echo ""

