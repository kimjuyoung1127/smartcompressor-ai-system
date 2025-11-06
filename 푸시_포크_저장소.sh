#!/bin/bash
# 포크 저장소에 충돌 해결된 코드 푸시

set -e

echo "🚀 포크 저장소에 푸시 시도..."
echo ""

# 현재 브랜치 확인
CURRENT_BRANCH=$(git branch --show-current)

if [ "$CURRENT_BRANCH" != "pr4-resolve" ]; then
    echo "PR 브랜치로 체크아웃 중..."
    git checkout pr4-resolve
fi

# 포크 저장소 원격 추가
FORK_REMOTE="pr4-fork"
FORK_OWNER="kimjuyoung1127"
FORK_URL="https://github.com/${FORK_OWNER}/smartcompressor-ai-system.git"
PR_BRANCH="customer-dashboard"

echo "포크 저장소: $FORK_URL"
echo "브랜치: $PR_BRANCH"
echo ""

# 원격 추가
if git remote get-url "$FORK_REMOTE" >/dev/null 2>&1; then
    echo "✅ 원격 이미 있음: $FORK_REMOTE"
    git remote set-url "$FORK_REMOTE" "$FORK_URL"
else
    git remote add "$FORK_REMOTE" "$FORK_URL"
    echo "✅ 원격 추가: $FORK_REMOTE"
fi

# 푸시 시도
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📤 포크 저장소에 푸시 중..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

set +e
git push "$FORK_REMOTE" pr4-resolve:"$PR_BRANCH" --force-with-lease
PUSH_STATUS=$?
set -e

if [ $PUSH_STATUS -eq 0 ]; then
    echo ""
    echo "✅ 푸시 성공!"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ 충돌 해결 완료!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "PR #4 페이지에서 충돌이 해결된 것을 확인할 수 있습니다."
    echo ""
    echo "다음 단계:"
    echo "  1. GitHub에서 PR #4 확인"
    echo "  2. 'Merge pull request' 버튼 활성화 확인"
    echo "  3. 승인 후 머지"
else
    echo ""
    echo "❌ 푸시 실패 (권한 없음)"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "대안 방법"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "충돌은 이미 해결되었지만, 포크 저장소에 푸시할 권한이 없습니다."
    echo ""
    echo "방법 1: PR 작성자에게 직접 안내"
    echo "  PR #4에 코멘트로 다음 메시지 전달:"
    echo ""
    echo "---"
    echo "주영님, 충돌을 로컬에서 해결했습니다."
    echo ""
    echo "다음 명령어로 해결된 코드를 가져오실 수 있습니다:"
    echo ""
    echo "git checkout customer-dashboard"
    echo "git fetch https://github.com/SEONBEOM-Kim/smartcompressor-ai-system.git pr4-resolve"
    echo "git merge FETCH_HEAD"
    echo "git push"
    echo ""
    echo "또는 GitHub 웹에서 'Resolve conflicts' 버튼을 사용해주세요."
    echo "---"
    echo ""
    echo "방법 2: GitHub 웹에서 해결"
    echo "  PR 작성자가 PR #4 페이지에서 'Resolve conflicts' 버튼 클릭"
    echo ""
    echo "현재 pr4-resolve 브랜치에 충돌 해결된 코드가 있습니다."
    echo "이 브랜치를 참고하여 PR 작성자가 직접 푸시하실 수 있습니다."
fi

