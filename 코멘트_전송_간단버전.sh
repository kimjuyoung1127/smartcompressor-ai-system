#!/bin/bash
# PR #4 코멘트 전송 - 간단 버전

echo "📝 PR #4에 코멘트 전송 중..."

gh pr comment 4 --body "주영님, 충돌을 로컬에서 해결했습니다! ✅

다만 포크 저장소에 직접 푸시할 권한이 없어서, 주영님이 직접 해결해주시면 감사하겠습니다.

**해결 방법 (가장 쉬움):**
1. PR #4 페이지에서 \"Resolve conflicts\" 버튼 클릭
2. 웹 에디터에서 충돌 해결 후 \"Mark as resolved\" → \"Commit merge\"

**충돌 내용:**
- \`nginx_signalcraft_config.conf\` 파일은 \`system/\` 디렉토리에 유지
- main 브랜치의 최신 변경사항도 반영

감사합니다! 🙏"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 코멘트 전송 완료!"
else
    echo ""
    echo "❌ 코멘트 전송 실패"
fi

