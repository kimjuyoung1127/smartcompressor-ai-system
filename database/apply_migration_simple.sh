#!/bin/bash
# 간단한 마이그레이션 실행 스크립트

cd /var/www/smartcompressor

MIGRATION_FILE="database/migrations/20241104180000_add_core_tables_and_improvements.sql"

echo "🚀 마이그레이션 실행 중..."
echo "파일: $MIGRATION_FILE"
echo ""

# 여러 방법으로 시도
# 방법 1: .env 파일에서 환경 변수 로드 후 실행
if [ -f .env ]; then
    # .env 파일에서 변수 추출 (주석과 빈 줄 제외)
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
fi

# 환경 변수 확인
DB_HOST=${DB_HOST:-localhost}
DB_NAME=${DB_NAME:-smartcompressor_ai}
DB_USER=${DB_USER:-postgres}
DB_PORT=${DB_PORT:-5432}

echo "📋 연결 정보:"
echo "  Host: $DB_HOST"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo "  Port: $DB_PORT"
echo ""

# 방법 1: PGPASSWORD 사용
if [ -n "$DB_PASSWORD" ]; then
    echo "방법 1: PGPASSWORD 사용"
    export PGPASSWORD="$DB_PASSWORD"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$MIGRATION_FILE"
    EXIT_CODE=$?
    unset PGPASSWORD
elif [ "$DB_HOST" = "localhost" ] || [ "$DB_HOST" = "127.0.0.1" ]; then
    # 방법 2: 로컬 연결 (peer 인증 시도)
    echo "방법 2: 로컬 peer 인증 시도"
    sudo -u postgres psql -d "$DB_NAME" -f "$MIGRATION_FILE" 2>/dev/null
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -ne 0 ]; then
        # 방법 3: 기본값으로 시도
        echo "방법 3: 기본값으로 연결 시도"
        psql -h localhost -U postgres -d smartcompressor_ai -f "$MIGRATION_FILE" 2>&1 || {
            echo ""
            echo "⚠️ 자동 연결 실패"
            echo ""
            echo "다음 명령어를 수동으로 실행하세요:"
            echo "  cd /var/www/smartcompressor"
            echo "  psql -h <DB_HOST> -U <DB_USER> -d <DB_NAME> -f $MIGRATION_FILE"
            echo ""
            echo "또는 환경 변수를 설정한 후:"
            echo "  export PGPASSWORD='<DB_PASSWORD>'"
            echo "  psql -h \$DB_HOST -U \$DB_USER -d \$DB_NAME -f $MIGRATION_FILE"
            EXIT_CODE=1
        }
    fi
else
    echo "❌ DB_PASSWORD가 설정되지 않았고, 원격 호스트입니다."
    echo "   .env 파일에 DB_PASSWORD를 설정하거나 수동으로 실행하세요."
    EXIT_CODE=1
fi

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ 마이그레이션 완료!"
    echo ""
    echo "📊 생성된 테이블 확인:"
    if [ -n "$DB_PASSWORD" ]; then
        export PGPASSWORD="$DB_PASSWORD"
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "\dt sessions user_store_access sensor_readings anomalies sensor_statistics" 2>/dev/null
        unset PGPASSWORD
    fi
else
    echo ""
    echo "❌ 마이그레이션 실패!"
    echo ""
    echo "💡 해결 방법:"
    echo "1. .env 파일에 올바른 DB_PASSWORD 설정 확인"
    echo "2. 데이터베이스 연결 정보 확인"
    echo "3. 수동으로 마이그레이션 실행"
fi

exit $EXIT_CODE

