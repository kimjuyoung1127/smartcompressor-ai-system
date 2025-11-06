#!/bin/bash
# SIGNALCRAFT EC2 완전 배포 스크립트

echo "🚀 SIGNALCRAFT EC2 완전 배포 시작..."

# 1. Node.js 설치 (없는 경우)
if ! command -v node &> /dev/null; then
    echo "📦 Node.js 설치 중..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
    echo "✅ Node.js 설치 완료"
else
    echo "✅ Node.js 이미 설치됨: $(node --version)"
fi

# 2. 프로젝트 디렉토리로 이동
cd /var/www/smartcompressor

# 3. 최신 코드 가져오기
echo "📥 최신 코드 가져오는 중..."
git pull origin main

# 4. Node.js 의존성 설치
echo "📦 Node.js 의존성 설치 중..."
npm install

# 5. 기존 프로세스 종료
echo "🛑 기존 서비스 종료 중..."
pkill -f "node server.js" || true
pkill -f "python.*integrated_web_server.py" || true

# 6. Node.js 서버 시작
echo "🚀 Node.js 서버 시작 중..."
nohup node server.js > node_server.log 2>&1 &

# 7. Python 서버 시작
echo "🐍 Python 서버 시작 중..."
source /home/ubuntu/smartcompressor_env/bin/activate
nohup python integrated_web_server.py > python_server.log 2>&1 &

# 8. 서비스 상태 확인
sleep 5
echo "🔍 서비스 상태 확인 중..."
ps aux | grep -E "(node server.js|python.*integrated_web_server.py)" | grep -v grep

# 9. 포트 확인
echo "🌐 포트 사용 상태:"
sudo netstat -tlnp | grep -E ":(3000|8001)" || echo "포트 확인 권한 없음"

# 10. API 테스트
echo "🧪 API 테스트:"
echo "Node.js 서버 (포트 3000):"
curl -s http://localhost:3000/api/auth/verify || echo "❌ Node.js API 응답 없음"

echo "Python 서버 (포트 8001):"
curl -s http://localhost:8001/ || echo "❌ Python API 응답 없음"

echo ""
echo "🎉 SIGNALCRAFT EC2 배포 완료!"
echo "🌐 Node.js 서버: http://3.39.124.0:3000"
echo "🐍 Python 서버: http://3.39.124.0:8001"
echo "📝 로그 확인: tail -f node_server.log python_server.log"
