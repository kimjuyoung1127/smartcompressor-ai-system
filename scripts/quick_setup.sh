#!/bin/bash
# 빠른 설정 스크립트: 가상환경 생성 및 패키지 설치

echo "=========================================="
echo "시스템 1 & 2 빠른 설정"
echo "=========================================="
echo ""

# 현재 디렉토리 확인
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "📁 프로젝트 디렉토리: $PROJECT_ROOT"
echo ""

# 1. 가상환경 확인 및 생성
if [ ! -d "venv" ]; then
    echo "📦 가상환경 생성 중..."
    python3 -m venv venv
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "❌ 가상환경 생성 실패!"
        echo ""
        echo "다음 패키지를 설치하세요:"
        echo "  sudo apt update"
        echo "  sudo apt install python3-venv python3-full"
        echo ""
        exit 1
    fi
    
    echo "✅ 가상환경 생성 완료"
else
    echo "✅ 기존 가상환경 발견"
fi

# 2. 가상환경 활성화
echo ""
echo "🔧 가상환경 활성화 중..."
source venv/bin/activate

# 3. pip 업그레이드
echo ""
echo "📦 pip 업그레이드 중..."
pip install --upgrade pip --quiet

# 4. 필수 패키지 설치
echo ""
echo "📦 필수 패키지 설치 중..."
echo "   (이 작업은 몇 분 걸릴 수 있습니다...)"
echo ""

pip install streamlit>=1.28.0 \
            Pillow>=10.0.0 \
            pandas>=2.0.0 \
            numpy>=1.24.0 \
            matplotlib>=3.7.0 \
            scipy>=1.11.0 \
            scikit-learn>=1.3.0

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 패키지 설치 실패!"
    echo ""
    exit 1
fi

# 5. 설치 확인
echo ""
echo "=========================================="
echo "설치 확인"
echo "=========================================="

python3 -c "import streamlit; print('✅ streamlit:', streamlit.__version__)" 2>/dev/null || echo "❌ streamlit"
python3 -c "import PIL; print('✅ Pillow:', PIL.__version__)" 2>/dev/null || echo "❌ Pillow"
python3 -c "import pandas; print('✅ pandas:', pandas.__version__)" 2>/dev/null || echo "❌ pandas"
python3 -c "import numpy; print('✅ numpy:', numpy.__version__)" 2>/dev/null || echo "❌ numpy"

echo ""
echo "=========================================="
echo "✅ 설정 완료!"
echo "=========================================="
echo ""
echo "⚠️  중요: 매번 작업 전에 가상환경을 활성화하세요!"
echo ""
echo "가상환경 활성화:"
echo "  source venv/bin/activate"
echo ""
echo "시스템 1 실행:"
echo "  source venv/bin/activate"
echo "  streamlit run ai/advanced_labeling_tool.py"
echo ""
echo "가상환경 비활성화:"
echo "  deactivate"
echo ""

