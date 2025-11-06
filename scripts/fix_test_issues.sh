#!/bin/bash
# 테스트 문제 해결 스크립트

echo "=========================================="
echo "테스트 문제 해결"
echo "=========================================="
echo ""

# 가상환경 활성화
if [ -d "venv" ]; then
    echo "🔧 가상환경 활성화 중..."
    source venv/bin/activate
else
    echo "❌ 가상환경이 없습니다. 먼저 가상환경을 생성하세요."
    exit 1
fi

# seaborn 설치
echo ""
echo "📦 seaborn 설치 중..."
pip install seaborn

# 설치 확인
echo ""
echo "=========================================="
echo "설치 확인"
echo "=========================================="

python -c "import seaborn; print('✅ seaborn:', seaborn.__version__)" 2>/dev/null || echo "❌ seaborn 설치 실패"

echo ""
echo "=========================================="
echo "✅ 완료!"
echo "=========================================="
echo ""
echo "이제 테스트를 실행하세요:"
echo "  python scripts/test_smart_detection_system.py"
echo ""

