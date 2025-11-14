#!/bin/bash
# EC2 서버 리전 및 데이터베이스 정보 확인 스크립트

SERVER="ubuntu@3.39.124.0"
SSH_KEY="/root/.ssh/signalcraft-new.pem"

echo "🔍 EC2 서버 정보 확인 중..."
echo "📡 서버: $SERVER"
echo ""

# EC2 서버의 리전 확인
echo "🌍 EC2 리전 확인 중..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER" "
    # EC2 메타데이터로 리전 확인
    echo '리전 정보:'
    REGION=\$(curl -s http://169.254.169.254/latest/meta-data/placement/region 2>/dev/null)
    if [ -n \"\$REGION\" ]; then
        echo \"  EC2 리전: \$REGION\"
    else
        echo \"  ⚠️  메타데이터 접근 불가\"
    fi
    
    echo ''
    echo '가용 영역 정보:'
    AZ=\$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone 2>/dev/null)
    if [ -n \"\$AZ\" ]; then
        echo \"  가용 영역: \$AZ\"
    fi
    
    echo ''
    echo '인스턴스 ID:'
    INSTANCE_ID=\$(curl -s http://169.254.169.254/latest/meta-data/instance-id 2>/dev/null)
    if [ -n \"\$INSTANCE_ID\" ]; then
        echo \"  인스턴스 ID: \$INSTANCE_ID\"
    fi
    
    echo ''
    echo 'VPC ID:'
    VPC_ID=\$(curl -s http://169.254.169.254/latest/meta-data/network/interfaces/macs/ 2>/dev/null | head -1 | xargs -I {} curl -s http://169.254.169.254/latest/meta-data/network/interfaces/macs/{}/vpc-id 2>/dev/null)
    if [ -n \"\$VPC_ID\" ]; then
        echo \"  VPC ID: \$VPC_ID\"
    fi
"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 현재 .env 파일 내용:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER" "
    if [ -f /home/ubuntu/smartcompressor-ai-system/.env ]; then
        cat /home/ubuntu/smartcompressor-ai-system/.env | grep -E '^DB_|^#'
    else
        echo '⚠️  .env 파일을 찾을 수 없습니다.'
    fi
"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💡 다음 단계:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. 위에서 확인한 EC2 리전과 .env 파일의 DB 리전을 비교하세요"
echo "2. EC2 리전이 us-east-1이면 DB도 us-east-1에 있어야 합니다"
echo "3. EC2 리전이 ap-northeast-2(서울)이면 현재 DB 설정이 맞을 수 있습니다"
echo ""

