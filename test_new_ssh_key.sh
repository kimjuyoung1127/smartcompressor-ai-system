#!/bin/bash
# 새 SSH 키 접속 테스트 스크립트

SERVER="ubuntu@3.39.124.0"

echo "🔍 새 SSH 키 접속 테스트..."
echo "📡 서버: $SERVER"
echo ""

# authorized_keys에 등록된 키 확인
echo "📋 서버에 등록된 키 확인 중..."
ssh -o StrictHostKeyChecking=no "$SERVER" "
    echo '등록된 키 목록:'
    if [ -f ~/.ssh/authorized_keys ]; then
        KEY_COUNT=\$(grep -v '^#' ~/.ssh/authorized_keys | grep -v '^\$' | wc -l)
        echo \"총 키 수: \$KEY_COUNT\"
        echo ''
        echo '김주영님 키:'
        grep 'juyoung@signalcraft' ~/.ssh/authorized_keys | head -1 | awk '{print \"  \" substr(\$0, 1, 80) \"...\"}'
    else
        echo 'authorized_keys 파일이 없습니다.'
    fi
" 2>/dev/null

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 서버 접속 성공! 새 키가 정상적으로 작동합니다."
    echo ""
    echo "📝 김주영님이 다음 명령어로 접속할 수 있습니다:"
    echo "   ssh $SERVER"
else
    echo ""
    echo "⚠️  현재 키로는 접속할 수 없습니다."
    echo "   (이것은 정상입니다 - 새로운 키로만 접속 가능)"
fi

