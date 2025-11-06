#!/bin/bash
# .env 파일 확인 및 환경 변수 로드 스크립트

cd /var/www/smartcompressor

echo "🔍 .env 파일 확인 중..."
echo ""

# 1. .env 파일 존재 확인
if [ ! -f .env ]; then
    echo "❌ .env 파일이 없습니다!"
    exit 1
fi

echo "✅ .env 파일 존재"
echo ""

# 2. .env 파일 첫 20줄 확인 (비밀번호 마스킹)
echo "📋 .env 파일 내용 (첫 20줄, 비밀번호 마스킹):"
cat .env | head -20 | sed 's/\(.*PASSWORD=\).*/\1***/'
echo ""

# 3. DB 관련 변수 확인
echo "📋 DB 관련 변수:"
grep -i "DB_" .env | sed 's/\(.*PASSWORD=\).*/\1***/'
echo ""

# 4. 변수명 패턴 확인 (대소문자, 공백 등)
echo "📋 변수명 패턴 확인:"
grep -E "^[A-Z_]+=" .env | head -10
echo ""

# 5. 파일 인코딩 확인
echo "📋 파일 인코딩:"
file .env
echo ""

# 6. 줄바꿈 확인
echo "📋 줄바꿈 형식:"
if file .env | grep -q "CRLF"; then
    echo "⚠️ Windows 줄바꿈(CRLF) 감지됨 - dos2unix로 변환 필요"
    echo "   실행: dos2unix .env"
else
    echo "✅ Unix 줄바꿈(LF)"
fi
echo ""

# 7. 환경 변수 로드 시도
echo "🚀 환경 변수 로드 시도..."
echo ""

# 방법 1: set -a 사용
set -a
source .env 2>&1
set +a

echo "방법 1 결과:"
echo "  DB_HOST: ${DB_HOST:-'(비어있음)'}"
echo "  DB_USER: ${DB_USER:-'(비어있음)'}"
echo "  DB_NAME: ${DB_NAME:-'(비어있음)'}"
echo ""

# 방법 2: 직접 추출
if [ -z "$DB_HOST" ]; then
    echo "방법 2: 직접 추출 시도..."
    DB_HOST=$(grep -i "^DB_HOST" .env | cut -d '=' -f2- | xargs)
    DB_USER=$(grep -i "^DB_USER" .env | cut -d '=' -f2- | xargs)
    DB_NAME=$(grep -i "^DB_NAME" .env | cut -d '=' -f2- | xargs)
    DB_PORT=$(grep -i "^DB_PORT" .env | cut -d '=' -f2- | xargs)
    DB_PASSWORD=$(grep -i "^DB_PASSWORD" .env | cut -d '=' -f2- | xargs)
    
    echo "  DB_HOST: ${DB_HOST:-'(비어있음)'}"
    echo "  DB_USER: ${DB_USER:-'(비어있음)'}"
    echo "  DB_NAME: ${DB_NAME:-'(비어있음)'}"
    echo ""
fi

# 8. 최종 권장 명령어 출력
echo "💡 권장 실행 명령어:"
echo ""
if [ -n "$DB_HOST" ] && [ -n "$DB_USER" ] && [ -n "$DB_NAME" ]; then
    echo "환경 변수가 로드되었습니다!"
    echo ""
    echo "export PGPASSWORD=\"\$DB_PASSWORD\""
    echo "psql -h \"\$DB_HOST\" -U \"\$DB_USER\" -d \"\$DB_NAME\" -f database/migrations/20241104180000_add_core_tables_and_improvements.sql"
else
    echo "환경 변수가 로드되지 않았습니다."
    echo ""
    echo ".env 파일을 직접 확인하고 수동으로 입력하세요:"
    echo ""
    echo "cat .env | grep -i DB_"
    echo ""
    echo "그 다음 수동으로:"
    echo "export DB_HOST=\"실제값\""
    echo "export DB_USER=\"실제값\""
    echo "export DB_NAME=\"실제값\""
    echo "export DB_PASSWORD=\"실제값\""
    echo "export PGPASSWORD=\"\$DB_PASSWORD\""
    echo "psql -h \"\$DB_HOST\" -U \"\$DB_USER\" -d \"\$DB_NAME\" -f database/migrations/20241104180000_add_core_tables_and_improvements.sql"
fi

