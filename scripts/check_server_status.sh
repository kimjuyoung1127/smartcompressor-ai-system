#!/bin/bash
# 서버 상태 확인 스크립트

echo "=========================================="
echo "서버 상태 확인"
echo "=========================================="
echo ""

# 1. 포트 5000에서 실행 중인 프로세스 확인
echo "1. 포트 5000에서 실행 중인 프로세스:"
netstat -tuln | grep 5000 || echo "포트 5000에서 실행 중인 프로세스 없음"
echo ""

# 2. 서버 응답 확인
echo "2. 서버 응답 테스트:"
if command -v curl &> /dev/null; then
    curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:5000/api/esp32/realtime/statistics || echo "서버 응답 없음"
else
    echo "curl이 설치되지 않았습니다. wget으로 시도..."
    wget -q -O /dev/null -S http://localhost:5000/api/esp32/realtime/statistics 2>&1 | head -1 || echo "서버 응답 없음"
fi
echo ""

# 3. WSL IP 주소 확인
echo "3. WSL IP 주소:"
ip addr show eth0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1 || hostname -i || echo "IP 주소를 확인할 수 없습니다"
echo ""

# 4. Python 프로세스 확인
echo "4. Python 프로세스 확인:"
ps aux | grep -E "python.*start_server|python.*app.py|flask" | grep -v grep || echo "Python 서버 프로세스 없음"
echo ""

echo "=========================================="
echo "확인 완료"
echo "=========================================="
