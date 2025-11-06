#!/bin/bash
# .env 파일 업데이트 스크립트

SERVER="ubuntu@3.39.124.0"
SSH_KEY="/root/.ssh/signalcraft-new.pem"
ENV_FILE="/home/ubuntu/smartcompressor-ai-system/.env"

echo "🔧 .env 파일 업데이트 스크립트"
echo "📡 서버: $SERVER"
echo ""

# 사용자 입력 받기
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "RDS 정보를 입력해주세요"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

read -p "DB_HOST (엔드포인트): " DB_HOST
read -p "DB_PORT (기본값 5432): " DB_PORT
read -p "DB_NAME (데이터베이스명): " DB_NAME
read -p "DB_USER (사용자명): " DB_USER
read -sp "DB_PASSWORD (비밀번호): " DB_PASSWORD
echo ""

# 기본값 설정
DB_PORT=${DB_PORT:-5432}

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "입력된 정보 확인"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "DB_HOST: $DB_HOST"
echo "DB_PORT: $DB_PORT"
echo "DB_NAME: $DB_NAME"
echo "DB_USER: $DB_USER"
echo "DB_PASSWORD: [비공개]"
echo ""

read -p "위 정보로 .env 파일을 업데이트하시겠습니까? (y/n): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "취소되었습니다."
    exit 0
fi

# .env 파일 업데이트
echo ""
echo "📝 .env 파일 업데이트 중..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER" "
    cd /home/ubuntu/smartcompressor-ai-system
    
    # 백업 생성
    BACKUP_FILE=\".env.backup_\$(date +%Y%m%d_%H%M%S)\"
    cp .env \$BACKUP_FILE
    echo \"✅ 백업 생성: \$BACKUP_FILE\"
    
    # 기존 DB 설정 제거
    grep -v '^DB_' .env > .env.tmp
    
    # 새 DB 설정 추가
    cat >> .env.tmp << EOF
# AWS RDS PostgreSQL Connection Settings
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD

# Connection Pool Settings
DB_POOL_SIZE=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
EOF
    
    mv .env.tmp .env
    echo \"✅ .env 파일 업데이트 완료\"
    
    # 확인
    echo \"\"
    echo \"📋 업데이트된 .env 파일 내용 (DB 관련):\"
    grep '^DB_' .env
"

if [ $? -eq 0 ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ .env 파일 업데이트 완료!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "💡 다음 단계:"
    echo "   1. 서버 재시작 (필요한 경우)"
    echo "   2. DB 연결 테스트"
    echo ""
else
    echo ""
    echo "❌ .env 파일 업데이트 실패"
    exit 1
fi

