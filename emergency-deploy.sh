#!/bin/bash

# 긴급 서버 복구 스크립트
# 실제 서버에 직접 실행해야 함

echo "🚨 긴급 서버 복구 시작..."

# 1. 프로젝트 디렉토리로 이동
cd /var/www/smartcompressor

# 2. 현재 상태 확인
echo "📊 현재 상태 확인..."
pwd
ls -la
pm2 status

# 3. 모든 프로세스 강제 종료
echo "🛑 모든 프로세스 강제 종료..."
pm2 kill
pkill -f "node"
pkill -f "npm"

# 4. 최신 코드 확인
echo "📥 최신 코드 확인..."
git status
git log --oneline -5

# 5. 의존성 재설치
echo "📦 의존성 재설치..."
rm -rf node_modules
npm install

# 6. PM2 재설치
echo "📦 PM2 재설치..."
npm install -g pm2

# 7. 서버 시작 (ecosystem.config.js 사용)
echo "🚀 서버 시작..."
pm2 start ecosystem.config.js --env production

# 8. 상태 확인
echo "📊 PM2 상태:"
pm2 status

# 9. 로그 확인
echo "📝 최근 로그:"
pm2 logs --lines 20

# 10. 포트 확인
echo "🌐 포트 사용 상태:"
netstat -tlnp | grep :3000 || echo "포트 3000 사용 안됨"

# 11. 서버 테스트
echo "🌐 서버 테스트..."
sleep 5
curl -s http://localhost:3000 && echo "✅ 메인 페이지 OK" || echo "❌ 메인 페이지 오류"
curl -s http://localhost:3000/api/esp32/features/recent?limit=1 && echo "✅ ESP32 API OK" || echo "❌ ESP32 API 오류"

# 12. Nginx 재시작
echo "🔄 Nginx 재시작..."
sudo systemctl restart nginx

echo "✅ 긴급 복구 완료!"
echo "🌐 서버 URL: https://signalcraft.kr"
echo "📊 PM2 모니터링: pm2 monit"
