#!/bin/bash
# PostgreSQL 설정 및 연결 테스트

SERVER="ubuntu@3.39.124.0"
SSH_KEY="/root/.ssh/signalcraft-new.pem"
DB_NAME="signalcraft"
DB_USER="postgres"
DB_PASSWORD="signalcraft6898"

echo "🔧 PostgreSQL 설정 및 연결 테스트"
echo "📡 서버: $SERVER"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  postgres 사용자 비밀번호 설정"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER" "
    echo 'postgres 사용자 비밀번호 설정 중...'
    sudo -u postgres psql << EOF
ALTER USER postgres WITH PASSWORD '$DB_PASSWORD';
\q
EOF
    
    if [ \$? -eq 0 ]; then
        echo '✅ 비밀번호 설정 완료'
    else
        echo '⚠️  비밀번호 설정 중 오류 발생 (이미 설정되어 있을 수 있음)'
    fi
    echo ''
"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  signalcraft 데이터베이스 확인 및 생성"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER" "
    # 데이터베이스 존재 확인
    DB_EXISTS=\$(sudo -u postgres psql -lqt | cut -d \\| -f 1 | grep -qw $DB_NAME && echo 'yes' || echo 'no')
    
    if [ \"\$DB_EXISTS\" = 'yes' ]; then
        echo '✅ signalcraft 데이터베이스가 이미 존재합니다'
        echo ''
        echo '테이블 목록:'
        sudo -u postgres psql -d $DB_NAME -c '\dt' 2>/dev/null | head -10
    else
        echo '⚠️  signalcraft 데이터베이스가 없습니다. 생성 중...'
        sudo -u postgres createdb $DB_NAME
        if [ \$? -eq 0 ]; then
            echo '✅ signalcraft 데이터베이스 생성 완료'
        else
            echo '❌ 데이터베이스 생성 실패'
        fi
    fi
    echo ''
"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  PostgreSQL 인증 설정 확인"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER" "
    echo 'pg_hba.conf 설정 확인:'
    sudo grep -E '^local|^host' /etc/postgresql/*/main/pg_hba.conf | head -5
    echo ''
    echo '⚠️  만약 연결이 안 되면 pg_hba.conf를 수정해야 할 수 있습니다'
    echo ''
"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  연결 테스트 (psql)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER" "
    echo '비밀번호를 사용한 연결 테스트:'
    PGPASSWORD='$DB_PASSWORD' psql -h localhost -U $DB_USER -d $DB_NAME -c 'SELECT version();' 2>&1
    
    if [ \$? -eq 0 ]; then
        echo ''
        echo '✅ 연결 성공!'
    else
        echo ''
        echo '⚠️  연결 실패 - 인증 방식 확인 필요'
        echo ''
        echo '대안: sudo -u postgres로 접속 (비밀번호 없이)'
        sudo -u postgres psql -d $DB_NAME -c 'SELECT version();' 2>&1 | head -3
    fi
    echo ''
"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  Node.js로 연결 테스트"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER" "
    cd /home/ubuntu/smartcompressor-ai-system
    
    if [ -f package.json ]; then
        echo 'Node.js 연결 테스트 중...'
        node << 'NODE_EOF'
const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT || '5432'),
    database: process.env.DB_NAME || 'signalcraft',
    user: process.env.DB_USER || 'postgres',
    password: process.env.DB_PASSWORD || 'signalcraft6898',
});

pool.query('SELECT NOW() as current_time, version() as pg_version', (err, res) => {
    if (err) {
        console.error('❌ 연결 실패:', err.message);
        process.exit(1);
    } else {
        console.log('✅ 연결 성공!');
        console.log('현재 시간:', res.rows[0].current_time);
        console.log('PostgreSQL 버전:', res.rows[0].pg_version.split(',')[0]);
        pool.end();
        process.exit(0);
    }
});
NODE_EOF
        
        if [ \$? -eq 0 ]; then
            echo ''
            echo '✅ Node.js 연결 테스트 성공!'
        else
            echo ''
            echo '❌ Node.js 연결 테스트 실패'
        fi
    else
        echo '⚠️  package.json이 없습니다. Node.js 테스트 건너뜀'
    fi
    echo ''
"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 설정 및 테스트 완료!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 연결이 실패하면:"
echo "   1. pg_hba.conf 파일 수정이 필요할 수 있습니다"
echo "   2. 또는 sudo -u postgres로 접속하는 방식 사용"
echo ""

