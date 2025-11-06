#!/bin/bash
# PostgreSQL postgres 사용자 비밀번호 설정 스크립트

NEW_PASSWORD="$1"

if [ -z "$NEW_PASSWORD" ]; then
    echo "❌ 사용법: $0 <새_비밀번호>"
    echo "예: $0 signalcraft6898"
    exit 1
fi

echo "🔧 PostgreSQL 비밀번호 설정 중..."
echo "비밀번호: $NEW_PASSWORD"

# psql 명령어를 사용하여 postgres 사용자의 비밀번호를 설정합니다.
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD '$NEW_PASSWORD';"

if [ $? -eq 0 ]; then
    echo "✅ 비밀번호 설정 완료"
else
    echo "❌ 비밀번호 설정 실패"
    exit 1
fi

echo ""
echo "🔍 데이터베이스 연결 테스트..."
export PGPASSWORD="$NEW_PASSWORD"
psql -h localhost -U postgres -d smartcompressor_ai -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';"

if [ $? -eq 0 ]; then
    echo "✅ 연결 테스트 성공!"
else
    echo "❌ 연결 테스트 실패"
    exit 1
fi

unset PGPASSWORD # 보안을 위해 환경 변수 제거

