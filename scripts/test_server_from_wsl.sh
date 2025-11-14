#!/bin/bash
# WSL 내부에서 서버 접속 테스트

echo "=========================================="
echo "WSL 내부 서버 접속 테스트"
echo "=========================================="
echo ""

# 1. localhost 테스트
echo "1. localhost:5000 테스트:"
curl -s http://localhost:5000/api/esp32/realtime/statistics || echo "❌ localhost 접속 실패"
echo ""

# 2. 127.0.0.1 테스트
echo "2. 127.0.0.1:5000 테스트:"
curl -s http://127.0.0.1:5000/api/esp32/realtime/statistics || echo "❌ 127.0.0.1 접속 실패"
echo ""

# 3. WSL IP 테스트
WSL_IP=$(ip addr show eth0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)
echo "3. WSL IP ($WSL_IP):5000 테스트:"
curl -s http://$WSL_IP:5000/api/esp32/realtime/statistics || echo "❌ WSL IP 접속 실패"
echo ""

# 4. 서버 프로세스 확인
echo "4. 서버 프로세스 확인:"
if pgrep -f "start_server" > /dev/null || pgrep -f "app.py" > /dev/null; then
    echo "✅ 서버 프로세스 실행 중"
    ps aux | grep -E "python.*start_server|python.*app.py" | grep -v grep
else
    echo "❌ 서버 프로세스 없음"
fi
echo ""

echo "=========================================="

