#!/bin/bash
# EC2 서버에 PostgreSQL이 설치되어 있는지 확인

SERVER="ubuntu@3.39.124.0"
SSH_KEY="/root/.ssh/signalcraft-new.pem"

echo "🔍 EC2 서버의 PostgreSQL 설치 여부 확인 중..."
echo "📡 서버: $SERVER"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  PostgreSQL 설치 확인"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER" "
    echo 'PostgreSQL 버전 확인:'
    if command -v psql &> /dev/null; then
        psql --version
        echo '✅ PostgreSQL이 설치되어 있습니다!'
    else
        echo '❌ PostgreSQL이 설치되어 있지 않습니다.'
    fi
    echo ''
"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  PostgreSQL 서비스 상태 확인"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER" "
    if systemctl list-units --type=service | grep -q postgresql; then
        echo 'PostgreSQL 서비스 상태:'
        sudo systemctl status postgresql --no-pager | head -10
    elif systemctl list-units --type=service | grep -q postgres; then
        echo 'PostgreSQL 서비스 상태:'
        sudo systemctl status postgres --no-pager | head -10
    else
        echo '⚠️  PostgreSQL 서비스를 찾을 수 없습니다.'
    fi
    echo ''
"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  포트 5432 사용 확인"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER" "
    echo '포트 5432 사용 여부:'
    sudo netstat -tlnp | grep 5432 || sudo ss -tlnp | grep 5432 || echo '포트 5432를 사용하는 프로세스가 없습니다.'
    echo ''
"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  Docker 컨테이너 확인"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER" "
    if command -v docker &> /dev/null; then
        echo 'PostgreSQL Docker 컨테이너:'
        docker ps | grep -i postgres || echo 'PostgreSQL Docker 컨테이너가 실행 중이지 않습니다.'
    else
        echo 'Docker가 설치되어 있지 않습니다.'
    fi
    echo ''
"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💡 다음 단계"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. 위에서 PostgreSQL이 설치되어 있다면:"
echo "   → localhost를 사용하는 .env 파일로 수정"
echo ""
echo "2. PostgreSQL이 없다면:"
echo "   → RDS를 새로 만들거나"
echo "   → EC2에 PostgreSQL 설치"
echo ""

