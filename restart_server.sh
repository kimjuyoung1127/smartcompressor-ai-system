#!/bin/bash
# EC2 서버 재시작 스크립트

SERVER="ubuntu@3.39.124.0"
SSH_KEY="/root/.ssh/signalcraft-new.pem"

echo "🔄 EC2 서버 재시작 중..."
echo "📡 서버: $SERVER"
echo ""

# SSH 키 파일 확인
if [ ! -f "$SSH_KEY" ]; then
    echo "❌ SSH 키 파일을 찾을 수 없습니다: $SSH_KEY"
    echo ""
    echo "사용 가능한 키 파일 확인 중..."
    ls -la ~/.ssh/*.pem 2>/dev/null || echo "키 파일이 없습니다."
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  현재 실행 중인 프로세스 확인"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER" "
    echo 'PM2 프로세스:'
    pm2 list 2>/dev/null || echo 'PM2 프로세스 없음'
    echo ''
    echo 'Node.js 프로세스:'
    ps aux | grep -E 'node|server\.js' | grep -v grep | head -5
    echo ''
"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  서버 재시작"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER" "
    cd /home/ubuntu/smartcompressor-ai-system
    
    # PM2 사용 중인지 확인
    if command -v pm2 &> /dev/null; then
        PM2_PROCESSES=\$(pm2 list | grep -c 'online' || echo '0')
        
        if [ \"\$PM2_PROCESSES\" -gt 0 ]; then
            echo 'PM2로 서버 재시작 중...'
            pm2 restart all --update-env
            sleep 2
            pm2 status
        else
            echo '⚠️  PM2 프로세스가 없습니다. 새로 시작합니다...'
            
            # ecosystem.config.js 확인
            if [ -f ecosystem.config.js ]; then
                pm2 start ecosystem.config.js --update-env
            elif [ -f server.js ]; then
                pm2 start server.js --name 'smartcompressor' --update-env
            else
                echo '⚠️  서버 파일을 찾을 수 없습니다.'
            fi
            
            sleep 2
            pm2 status
        fi
    else
        echo '⚠️  PM2가 설치되어 있지 않습니다.'
        echo ''
        echo '대안: node server.js 직접 실행'
        if [ -f server.js ]; then
            echo '기존 프로세스 종료 중...'
            pkill -f 'node server.js' || true
            sleep 1
            echo '서버 시작 중...'
            nohup node server.js > server.log 2>&1 &
            sleep 2
            ps aux | grep 'node server.js' | grep -v grep
        fi
    fi
    echo ''
"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  서버 상태 확인"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER" "
    sleep 3
    echo 'PM2 상태:'
    pm2 status 2>/dev/null || echo 'PM2 없음'
    echo ''
    echo '포트 3000 사용 확인:'
    sudo netstat -tlnp | grep 3000 || sudo ss -tlnp | grep 3000 || echo '포트 3000 사용 안 함'
    echo ''
    echo 'API 테스트:'
    curl -s http://localhost:3000/api/auth/verify 2>/dev/null && echo '✅ API 응답 성공' || echo '⚠️  API 응답 없음'
    echo ''
"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 서버 재시작 완료!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 로그 확인:"
echo "   ssh -i $SSH_KEY $SERVER 'pm2 logs'"
echo "   또는"
echo "   ssh -i $SSH_KEY $SERVER 'tail -f /home/ubuntu/smartcompressor-ai-system/server.log'"
echo ""

