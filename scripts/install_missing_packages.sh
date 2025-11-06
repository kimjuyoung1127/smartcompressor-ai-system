#!/bin/bash
# 누락된 패키지 설치 스크립트

cd /root/smartcompressor-ai-system
source venv/bin/activate

echo "=========================================="
echo "누락된 패키지 설치"
echo "=========================================="
echo ""

pip install aiohttp>=3.9.0 schedule>=1.2.0

echo ""
echo "=========================================="
echo "✅ 설치 완료!"
echo "=========================================="
echo ""
echo "이제 서버를 실행하세요:"
echo "  python scripts/start_server_minimal.py"
echo ""

