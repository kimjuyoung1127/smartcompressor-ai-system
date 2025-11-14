#!/bin/bash
# 시스템 1 & 2 필수 패키지 설치 스크립트 (WSL/Linux용)

echo "=========================================="
echo "시스템 1 & 2 필수 패키지 설치"
echo "=========================================="
echo ""

# 가상환경 확인 및 생성
if [ ! -d "venv" ]; then
    echo "📦 가상환경 생성 중..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ 가상환경 생성 실패. python3-venv 패키지가 필요할 수 있습니다."
        echo "   설치: sudo apt install python3-venv python3-full"
        exit 1
    fi
    echo "✅ 가상환경 생성 완료"
else
    echo "✅ 기존 가상환경 사용"
fi

# 가상환경 활성화
echo ""
echo "🔧 가상환경 활성화 중..."
source venv/bin/activate

# pip 업그레이드
echo "📦 pip 업그레이드 중..."
pip install --upgrade pip

# 필수 패키지 설치
echo ""
echo "📦 필수 패키지 설치 중..."
pip install streamlit>=1.28.0 \
            Pillow>=10.0.0 \
            pandas>=2.0.0 \
            numpy>=1.24.0 \
            matplotlib>=3.7.0 \
            scipy>=1.11.0 \
            scikit-learn>=1.3.0

# 설치 확인
echo ""
echo "=========================================="
echo "설치 확인"
echo "=========================================="

python3 -c "import streamlit; print('✅ streamlit:', streamlit.__version__)" || echo "❌ streamlit 설치 실패"
python3 -c "import PIL; print('✅ Pillow:', PIL.__version__)" || echo "❌ Pillow 설치 실패"
python3 -c "import pandas; print('✅ pandas:', pandas.__version__)" || echo "❌ pandas 설치 실패"
python3 -c "import numpy; print('✅ numpy:', numpy.__version__)" || echo "❌ numpy 설치 실패"
python3 -c "import matplotlib; print('✅ matplotlib:', matplotlib.__version__)" || echo "❌ matplotlib 설치 실패"

echo ""
echo "=========================================="
echo "✅ 설치 완료!"
echo "=========================================="
echo ""
echo "⚠️  중요: 가상환경이 활성화된 상태에서 실행하세요!"
echo ""
echo "가상환경 활성화:"
echo "  source venv/bin/activate"
echo ""
echo "시스템 1 실행 방법:"
echo "  source venv/bin/activate"
echo "  streamlit run ai/advanced_labeling_tool.py"
echo ""
echo "시스템 2 데모 실행:"
echo "  source venv/bin/activate"
echo "  python scripts/run_system1_system2_demo.py"
echo ""
echo "가상환경 비활성화:"
echo "  deactivate"
echo ""

