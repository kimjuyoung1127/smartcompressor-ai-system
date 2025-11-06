#!/bin/bash
# PostgreSQL 비밀번호 설정 및 연결 테스트

echo "🔧 PostgreSQL 비밀번호 설정 중..."

# PostgreSQL 비밀번호 설정
sudo -u postgres psql << 'SQL'
ALTER USER postgres WITH PASSWORD 'password';
\q
SQL

echo "✅ 비밀번호 설정 완료"
echo ""

# 연결 테스트
echo "🔍 데이터베이스 연결 테스트..."
export PGPASSWORD="password"
psql -h localhost -U postgres -d smartcompressor_ai -c "SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = 'public';" 2>&1
unset PGPASSWORD

echo ""
echo "✅ 완료!"

