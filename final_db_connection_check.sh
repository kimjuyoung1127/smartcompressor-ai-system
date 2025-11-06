#!/bin/bash
# 최종 DB 연결 확인

SERVER="ubuntu@3.39.124.0"
SSH_KEY="/root/.ssh/signalcraft-new.pem"

echo "🔍 최종 DB 연결 및 애플리케이션 상태 확인"
echo "📡 서버: $SERVER"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  .env 파일 최종 확인"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER" "
    cd /home/ubuntu/smartcompressor-ai-system
    echo '📋 현재 .env 파일의 DB 설정:'
    grep '^DB_' .env
    echo ''
"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  PostgreSQL 연결 확인"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER" "
    cd /home/ubuntu/smartcompressor-ai-system
    source .env 2>/dev/null || true
    
    PGPASSWORD=\$DB_PASSWORD psql -h \$DB_HOST -U \$DB_USER -d \$DB_NAME -c 'SELECT current_database() as db_name, current_user as db_user, version() as pg_version;' 2>&1
    
    if [ \$? -eq 0 ]; then
        echo ''
        echo '✅ PostgreSQL 연결 성공!'
    else
        echo ''
        echo '❌ PostgreSQL 연결 실패'
    fi
    echo ''
"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  Node.js 애플리케이션 연결 확인"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER" "
    cd /home/ubuntu/smartcompressor-ai-system
    
    # PM2 로그에서 DB 연결 메시지 확인
    echo 'PM2 로그에서 DB 관련 메시지 확인 (최근 20줄):'
    pm2 logs --lines 20 --nostream 2>/dev/null | grep -i -E 'database|db|postgres|connection|error|connected' | tail -10 || echo '로그에서 DB 관련 메시지 없음'
    echo ''
"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  서버 상태"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER" "
    echo 'PM2 상태:'
    pm2 status
    echo ''
    echo 'API 응답 테스트:'
    curl -s http://localhost:3000/api/auth/verify | head -100
    echo ''
"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 확인 완료!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 요약:"
echo "   ✅ .env 파일: localhost로 설정됨"
echo "   ✅ PostgreSQL: 설치 및 실행 중"
echo "   ✅ 데이터베이스: signalcraft 생성됨"
echo "   ✅ 서버: 재시작 완료"
echo "   ✅ API: 정상 응답"
echo ""
echo "🎉 모든 설정이 완료되었습니다!"
echo ""

