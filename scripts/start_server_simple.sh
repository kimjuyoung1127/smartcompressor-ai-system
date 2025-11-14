#!/bin/bash
# 간단한 서버 실행 스크립트

cd /root/smartcompressor-ai-system
source venv/bin/activate

echo ""
echo "=========================================="
echo "ESP32 실시간 모니터링 서버 시작"
echo "=========================================="
echo ""
echo "🌐 서버 URL: http://localhost:5000"
echo "📊 대시보드: http://localhost:5000/static/dashboard-components/esp32-realtime-monitor.html"
echo ""
echo "서버 실행 중... (Ctrl+C로 종료)"
echo ""

python scripts/start_server.py

