#!/bin/bash
# 마이그레이션을 직접 적용하는 스크립트 (환경 변수 로드 후 실행)

cd /var/www/smartcompressor

# .env 파일 로드
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# 데이터베이스 연결 정보 확인
echo "📋 데이터베이스 연결 정보:"
echo "  DB_HOST: ${DB_HOST:-localhost}"
echo "  DB_NAME: ${DB_NAME:-smartcompressor_ai}"
echo "  DB_USER: ${DB_USER:-postgres}"
echo "  DB_PORT: ${DB_PORT:-5432}"
echo ""

# 마이그레이션 파일 직접 실행
MIGRATION_FILE="database/migrations/20241104180000_add_core_tables_and_improvements.sql"

if [ ! -f "$MIGRATION_FILE" ]; then
    echo "❌ 마이그레이션 파일을 찾을 수 없습니다: $MIGRATION_FILE"
    exit 1
fi

echo "🚀 마이그레이션 실행: $MIGRATION_FILE"
echo ""

# PGPASSWORD 환경 변수 설정 후 psql 실행
if [ -n "$DB_PASSWORD" ]; then
    export PGPASSWORD="$DB_PASSWORD"
    psql -h "${DB_HOST:-localhost}" \
         -p "${DB_PORT:-5432}" \
         -U "${DB_USER:-postgres}" \
         -d "${DB_NAME:-smartcompressor_ai}" \
         -f "$MIGRATION_FILE"
    
    EXIT_CODE=$?
    unset PGPASSWORD
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo ""
        echo "✅ 마이그레이션 완료!"
        
        # 마이그레이션 상태 확인
        echo ""
        echo "📊 새로 생성된 테이블 확인:"
        psql -h "${DB_HOST:-localhost}" \
             -p "${DB_PORT:-5432}" \
             -U "${DB_USER:-postgres}" \
             -d "${DB_NAME:-smartcompressor_ai}" \
             -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('sessions', 'user_store_access', 'sensor_readings', 'anomalies', 'sensor_statistics') ORDER BY table_name;"
    else
        echo ""
        echo "❌ 마이그레이션 실패! (종료 코드: $EXIT_CODE)"
        exit 1
    fi
else
    echo "❌ DB_PASSWORD 환경 변수가 설정되지 않았습니다."
    echo "   .env 파일에 DB_PASSWORD가 있는지 확인하세요."
    exit 1
fi

