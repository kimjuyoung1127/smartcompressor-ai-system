#!/bin/bash
# 김주영님 SSH 키 추가 - 실행 스크립트
# Windows 경로를 WSL 경로로 자동 변환

WINDOWS_KEY_PATH="C:\\Signal_craft\\음원라벨링도구\\compressor-ai-diagnosis\\src\\signalcraft-new.pem"
WSL_KEY_PATH="/mnt/c/Signal_craft/음원라벨링도구/compressor-ai-diagnosis/src/signalcraft-new.pem"

echo "🔍 SSH 키 파일 확인 중..."
echo "   Windows 경로: $WINDOWS_KEY_PATH"
echo "   WSL 경로: $WSL_KEY_PATH"
echo ""

if [ ! -f "$WSL_KEY_PATH" ]; then
    echo "❌ 오류: SSH 키 파일을 찾을 수 없습니다: $WSL_KEY_PATH"
    echo ""
    echo "💡 확인 사항:"
    echo "   1. 파일 경로가 올바른지 확인"
    echo "   2. WSL에서 Windows 파일 접근 권한 확인"
    exit 1
fi

echo "✅ 키 파일 확인 완료!"
echo ""
echo "🚀 SSH 키 추가 스크립트 실행 중..."
echo ""

# 현재 디렉토리의 quick_add_ssh_key.sh 실행
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/quick_add_ssh_key.sh" "$WSL_KEY_PATH"

