#!/bin/bash
# EC2 서버에서 현재 사용 중인 데이터베이스 정보 확인 스크립트

SERVER="ubuntu@3.39.124.0"
SSH_KEY="/root/.ssh/signalcraft-new.pem"

echo "🔍 EC2 서버의 현재 데이터베이스 연결 정보 확인 중..."
echo "📡 서버: $SERVER"
echo ""

# EC2 서버 리전 확인
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  EC2 서버 리전 확인"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER" "
    REGION=\$(curl -s http://169.254.169.254/latest/meta-data/placement/region 2>/dev/null)
    AZ=\$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone 2>/dev/null)
    INSTANCE_ID=\$(curl -s http://169.254.169.254/latest/meta-data/instance-id 2>/dev/null)
    
    echo \"📍 리전: \$REGION\"
    echo \"📍 가용 영역: \$AZ\"
    echo \"🆔 인스턴스 ID: \$INSTANCE_ID\"
    echo \"\"
"

# 현재 .env 파일 내용
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  현재 .env 파일의 DB 설정"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER" "
    if [ -f /home/ubuntu/smartcompressor-ai-system/.env ]; then
        echo \"📄 .env 파일 위치: /home/ubuntu/smartcompressor-ai-system/.env\"
        echo \"\"
        grep -E '^DB_' /home/ubuntu/smartcompressor-ai-system/.env
    else
        echo \"⚠️  .env 파일을 찾을 수 없습니다.\"
    fi
    echo \"\"
"

# AWS CLI로 RDS 목록 확인 (만약 AWS CLI가 설치되어 있다면)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  AWS CLI로 RDS 인스턴스 확인 (가능한 경우)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER" "
    if command -v aws &> /dev/null; then
        REGION=\$(curl -s http://169.254.169.254/latest/meta-data/placement/region 2>/dev/null)
        echo \"📍 현재 리전: \$REGION\"
        echo \"\"
        echo \"🔍 해당 리전의 RDS 인스턴스:\"
        aws rds describe-db-instances --region \$REGION --query 'DBInstances[*].[DBInstanceIdentifier,Endpoint.Address,DBInstanceStatus,Engine]' --output table 2>/dev/null || echo \"⚠️  AWS CLI 설정 또는 권한 문제로 조회 실패\"
    else
        echo \"⚠️  AWS CLI가 설치되어 있지 않습니다.\"
    fi
    echo \"\"
"

# 실행 중인 프로세스에서 DB 연결 정보 추출 시도
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  실행 중인 애플리케이션의 DB 연결 정보 (환경 변수)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER" "
    if command -v pm2 &> /dev/null; then
        echo \"PM2 프로세스 환경 변수 확인:\"
        pm2 env 0 | grep -E 'DB_|DATABASE' | head -10 || echo \"PM2 프로세스가 없거나 DB 관련 환경 변수가 없습니다.\"
    fi
    echo \"\"
"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💡 다음 단계"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. 위에서 확인한 EC2 리전을 확인하세요"
echo "2. AWS 콘솔에서 해당 리전으로 이동"
echo "3. RDS 서비스 → 데이터베이스 목록에서 확인"
echo "4. 올바른 RDS 엔드포인트, 사용자명, 비밀번호 확인"
echo ""

