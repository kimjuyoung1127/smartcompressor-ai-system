#!/bin/bash
# EC2 서버 정보 확인 (대체 방법)

SERVER="ubuntu@3.39.124.0"
SSH_KEY="/root/.ssh/signalcraft-new.pem"

echo "🔍 EC2 서버 정보 확인 (대체 방법)"
echo "📡 서버: $SERVER"
echo ""

# IP 주소로 리전 추정 시도 (AWS IP 범위 확인)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  네트워크 정보 확인"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER" "
    echo '📍 공인 IP:'
    curl -s https://checkip.amazonaws.com 2>/dev/null || echo 'IP 확인 실패'
    echo ''
    echo '📍 로컬 IP (내부):'
    hostname -I 2>/dev/null || ip addr show | grep 'inet ' | grep -v '127.0.0.1' | awk '{print \$2}' | cut -d/ -f1 | head -1
    echo ''
"

# AWS CLI 설치 및 설정 확인
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  AWS 설정 확인"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER" "
    if [ -f ~/.aws/config ]; then
        echo '✅ AWS 설정 파일 존재'
        echo '기본 리전:'
        grep 'region' ~/.aws/config | head -1 || echo '리전 설정 없음'
    else
        echo '⚠️  AWS 설정 파일 없음'
    fi
    echo ''
"

# 현재 .env 파일 정보 요약
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  현재 .env 파일 정보 (요약)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER" "
    if [ -f /home/ubuntu/smartcompressor-ai-system/.env ]; then
        DB_HOST=\$(grep '^DB_HOST=' /home/ubuntu/smartcompressor-ai-system/.env | cut -d= -f2)
        echo \"현재 DB_HOST: \$DB_HOST\"
        
        # 리전 추출
        if echo \"\$DB_HOST\" | grep -q 'ap-northeast-2'; then
            echo \"📍 DB 리전: ap-northeast-2 (서울)\"
        elif echo \"\$DB_HOST\" | grep -q 'us-east-1'; then
            echo \"📍 DB 리전: us-east-1 (버지니아)\"
        elif echo \"\$DB_HOST\" | grep -q 'us-west-'; then
            echo \"📍 DB 리전: us-west (미국 서부)\"
        else
            echo \"📍 DB 리전: 확인 필요\"
        fi
        
        echo \"⚠️  이것은 김주영님 계정의 DB입니다 (jason 사용자)\"
    fi
    echo ''
"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💡 확인 방법"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1️⃣  AWS 콘솔에서 확인 (가장 확실함):"
echo "   - AWS 콘솔 → EC2 → 인스턴스"
echo "   - IP 3.39.124.0를 가진 인스턴스 찾기"
echo "   - 해당 인스턴스의 '리전' 확인"
echo ""
echo "2️⃣  현재 .env의 DB는 ap-northeast-2 (서울) 리전입니다"
echo "   - 이것이 김주영님 계정의 DB (jason 사용자)"
echo ""
echo "3️⃣  대표님 계정의 RDS를 확인하려면:"
echo "   - AWS 콘솔 → EC2에서 인스턴스 리전 확인"
echo "   - 해당 리전으로 이동"
echo "   - RDS → 데이터베이스에서 PostgreSQL 인스턴스 찾기"
echo ""
echo "4️⃣  가능한 리전:"
echo "   - us-east-1 (버지니아) - 가장 일반적"
echo "   - ap-northeast-2 (서울)"
echo "   - 다른 리전"
echo ""

