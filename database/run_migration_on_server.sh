#!/bin/bash
# 서버에서 마이그레이션 실행 스크립트

cd /var/www/smartcompressor

# .env 파일에서 환경 변수 로드
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# 마이그레이션 실행
echo "🚀 마이그레이션 실행 중..."
node database/migrate.js

if [ $? -eq 0 ]; then
    echo "✅ 마이그레이션 완료!"
    
    # 마이그레이션 상태 확인
    echo ""
    echo "📊 마이그레이션 상태:"
    node database/migrate.js --status
else
    echo "❌ 마이그레이션 실패!"
    exit 1
fi

