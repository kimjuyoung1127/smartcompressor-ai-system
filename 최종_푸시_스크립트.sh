#!/bin/bash
# 포크 저장소에 최종 푸시

echo "🚀 포크 저장소에 푸시 시작..."
echo ""

# pr4-resolve 브랜치로 이동
git checkout pr4-resolve

# 포크 저장소 원격 추가
FORK_URL="https://github.com/kimjuyoung1127/smartcompressor-ai-system.git"
PR_BRANCH="customer-dashboard"

echo "포크 저장소: $FORK_URL"
echo "브랜치: $PR_BRANCH"
echo ""

# 원격 추가 (이미 있으면 업데이트)
git remote remove pr4-fork 2>/dev/null || true
git remote add pr4-fork "$FORK_URL"

echo "✅ 원격 추가 완료"
echo ""

# 푸시 시도
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📤 푸시 시도 중..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if git push pr4-fork pr4-resolve:"$PR_BRANCH" --force-with-lease 2>&1; then
    echo ""
    echo "✅ 푸시 성공!"
    echo ""
    echo "PR #4에서 충돌이 해결되었습니다!"
else
    echo ""
    echo "⚠️  푸시 실패 (권한 없음 - 정상)"
    echo ""
    echo "충돌은 이미 해결되었습니다."
    echo "PR 작성자에게 GitHub 웹에서 'Resolve conflicts' 버튼을 사용하도록 요청하세요."
    echo ""
    echo "또는 PR 코멘트로 안내:"
    echo "---"
    echo "주영님, 충돌을 로컬에서 해결했습니다."
    echo "GitHub 웹에서 'Resolve conflicts' 버튼을 클릭해주시거나,"
    echo "다음 명령어로 로컬에서 가져오실 수 있습니다:"
    echo ""
    echo "git fetch origin main"
    echo "git merge origin/main"
    echo "# 충돌 해결 후"
    echo "git push"
    echo "---"
fi

