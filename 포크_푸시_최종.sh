#!/bin/bash
# 포크 저장소에 최종 푸시 (권한 확인 포함)

set -e

echo "🚀 포크 저장소에 푸시 시작..."
echo ""

# pr4-resolve 브랜치 확인
if ! git show-ref --verify --quiet refs/heads/pr4-resolve; then
    echo "❌ pr4-resolve 브랜치를 찾을 수 없습니다."
    exit 1
fi

git checkout pr4-resolve
echo "✅ pr4-resolve 브랜치로 체크아웃"
echo ""

# 포크 저장소 정보
FORK_OWNER="kimjuyoung1127"
FORK_URL="https://github.com/${FORK_OWNER}/smartcompressor-ai-system.git"
PR_BRANCH="customer-dashboard"

echo "포크 저장소: $FORK_URL"
echo "브랜치: $PR_BRANCH"
echo ""

# 원격 설정
echo "🔗 원격 저장소 설정 중..."
git remote remove pr4-fork 2>/dev/null || true
git remote add pr4-fork "$FORK_URL"
echo "✅ 원격 추가 완료"
echo ""

# 포크 저장소 정보 확인
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📤 포크 저장소에 푸시 시도..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

set +e
git push pr4-fork pr4-resolve:"$PR_BRANCH" --force-with-lease 2>&1 | tee /tmp/push_result.txt
PUSH_STATUS=$?
PUSH_OUTPUT=$(cat /tmp/push_result.txt)
rm -f /tmp/push_result.txt
set -e

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $PUSH_STATUS -eq 0 ]; then
    echo "✅ 푸시 성공!"
    echo ""
    echo "PR #4에서 충돌이 해결되었습니다!"
    echo "GitHub에서 확인해주세요."
else
    echo "⚠️  푸시 실패"
    echo ""
    
    # 권한 오류인지 확인
    if echo "$PUSH_OUTPUT" | grep -q "Permission denied\|denied\|403\|unauthorized"; then
        echo "❌ 권한이 없습니다 (예상됨)"
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "해결 방법: PR 작성자에게 직접 요청"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "충돌은 이미 해결되었지만, 포크 저장소에 푸시할 권한이 없습니다."
        echo ""
        echo "PR #4에 다음 코멘트를 남겨주세요:"
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        cat << 'COMMENT'
주영님, 충돌을 로컬에서 해결했습니다! ✅

다만 포크 저장소에 직접 푸시할 권한이 없어서, 
주영님이 직접 해결해주시면 감사하겠습니다.

**해결 방법:**

1. **GitHub 웹에서 (가장 쉬움):**
   - PR #4 페이지에서 **"Resolve conflicts"** 버튼 클릭
   - 웹 에디터에서 충돌 해결 후 **"Mark as resolved"** → **"Commit merge"**

2. **로컬에서 해결:**
```bash
git checkout customer-dashboard
git fetch origin main
git merge origin/main

# 충돌 해결 (nginx_signalcraft_config.conf)
# 파일은 system/ 디렉토리에 유지

git add system/nginx_signalcraft_config.conf  # 또는 nginx_signalcraft_config.conf
git commit -m "충돌 해결: main 브랜치와 병합"
git push
```

충돌 내용:
- `nginx_signalcraft_config.conf` 파일이 `system/` 디렉토리로 이동한 것은 유지
- main 브랜치의 최신 변경사항도 반영

감사합니다! 🙏
COMMENT
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    else
        echo "❌ 다른 오류 발생:"
        echo "$PUSH_OUTPUT"
    fi
fi

# 원래 브랜치로 돌아가기
git checkout main 2>/dev/null || true

