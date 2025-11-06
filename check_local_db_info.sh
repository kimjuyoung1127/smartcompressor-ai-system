#!/bin/bash
# EC2 서버의 로컬 PostgreSQL 데이터베이스 정보 확인

SERVER="ubuntu@3.39.124.0"
SSH_KEY="/root/.ssh/signalcraft-new.pem"

echo "🔍 EC2 서버의 로컬 PostgreSQL 데이터베이스 정보 확인 중..."
echo "📡 서버: $SERVER"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  PostgreSQL 데이터베이스 목록"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER" "
    sudo -u postgres psql -l 2>/dev/null | grep -E 'Name|signalcraft|postgres|template' || echo '데이터베이스 목록 조회 실패'
    echo ''
"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  PostgreSQL 사용자 목록"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER" "
    sudo -u postgres psql -c '\du' 2>/dev/null | grep -E 'User|postgres|ubuntu|signalcraft' || echo '사용자 목록 조회 실패'
    echo ''
"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  signalcraft 데이터베이스 확인"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER" "
    if sudo -u postgres psql -lqt | cut -d \\| -f 1 | grep -qw signalcraft; then
        echo '✅ signalcraft 데이터베이스가 존재합니다'
        echo ''
        echo '테이블 목록:'
        sudo -u postgres psql -d signalcraft -c '\dt' 2>/dev/null | head -20
    else
        echo '⚠️  signalcraft 데이터베이스가 없습니다.'
        echo ''
        echo '생성하려면:'
        echo '  sudo -u postgres createdb signalcraft'
    fi
    echo ''
"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💡 권장 .env 설정"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "DB_HOST=localhost"
echo "DB_PORT=5432"
echo "DB_NAME=signalcraft (또는 확인된 데이터베이스명)"
echo "DB_USER=postgres (또는 확인된 사용자명)"
echo "DB_PASSWORD=설정하신_비밀번호"
echo ""

