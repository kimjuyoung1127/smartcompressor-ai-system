#!/bin/bash
# 서버 상태 확인 스크립트

echo "🔍 Signalcraft 서버 상태 확인 시작..."

# 1. 서버 IP와 도메인 확인
echo "📋 서버 정보:"
echo "  - 도메인: signalcraft.kr"
echo "  - IP: 3.39.124.0"
echo "  - 포트: 3000 (Node.js), 80/443 (Nginx)"

# 2. 로컬 서버 상태 확인
echo ""
echo "🌐 로컬 서버 상태:"
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ 로컬 Node.js 서버 (포트 3000) - 정상"
else
    echo "❌ 로컬 Node.js 서버 (포트 3000) - 응답 없음"
fi

# 3. 외부 서버 상태 확인
echo ""
echo "🌍 외부 서버 상태:"
if curl -s -I https://signalcraft.kr > /dev/null; then
    echo "✅ HTTPS (signalcraft.kr) - 정상"
else
    echo "❌ HTTPS (signalcraft.kr) - 502 에러"
fi

if curl -s -I http://signalcraft.kr > /dev/null; then
    echo "✅ HTTP (signalcraft.kr) - 정상"
else
    echo "❌ HTTP (signalcraft.kr) - 응답 없음"
fi

# 4. 포트 확인
echo ""
echo "🔌 포트 사용 상태:"
netstat -tlnp | grep -E ":(3000|80|443)" 2>/dev/null || echo "포트 확인 권한 없음"

# 5. PM2 상태 확인 (로컬)
echo ""
echo "📊 PM2 상태:"
if command -v pm2 &> /dev/null; then
    pm2 status
else
    echo "PM2가 설치되어 있지 않습니다."
fi

# 6. Nginx 상태 확인 (로컬)
echo ""
echo "🔧 Nginx 상태:"
if command -v nginx &> /dev/null; then
    nginx -t 2>&1
    systemctl status nginx 2>/dev/null || echo "Nginx 상태 확인 권한 없음"
else
    echo "Nginx가 설치되어 있지 않습니다."
fi

echo ""
echo "✅ 서버 상태 확인 완료!"
