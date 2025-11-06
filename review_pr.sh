#!/bin/bash
# GitHub PR 코드 리뷰 스크립트
# 사용법: ./review_pr.sh <PR_NUMBER> 또는 ./review_pr.sh <PR_URL>

PR_NUMBER=""
PR_URL=""

# PR 번호 또는 URL 파싱
if [ -z "$1" ]; then
    echo "❌ 오류: PR 번호 또는 URL을 제공해야 합니다."
    echo "사용법: $0 <PR_NUMBER>"
    echo "       $0 https://github.com/user/repo/pull/123"
    exit 1
fi

if [[ "$1" =~ ^https://github.com/.*/pull/([0-9]+)$ ]]; then
    PR_NUMBER="${BASH_REMATCH[1]}"
elif [[ "$1" =~ ^[0-9]+$ ]]; then
    PR_NUMBER="$1"
else
    echo "❌ 오류: 올바른 PR 번호 또는 URL 형식이 아닙니다."
    exit 1
fi

echo "🔍 GitHub PR #$PR_NUMBER 리뷰 시작..."
echo ""

# GitHub CLI가 설치되어 있는지 확인
if ! command -v gh &> /dev/null; then
    echo "⚠️  GitHub CLI가 설치되어 있지 않습니다."
    echo ""
    echo "설치 방법:"
    echo "  Ubuntu/Debian: sudo apt install gh"
    echo "  또는: curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg"
    echo ""
    echo "대안: PR의 변경 파일을 수동으로 확인하거나,"
    echo "다음 명령어로 PR diff를 확인하세요:"
    echo "  git fetch origin"
    echo "  git diff origin/main...origin/feature-branch"
    exit 1
fi

# PR 정보 가져오기
echo "📋 PR 정보 가져오는 중..."
PR_INFO=$(gh pr view $PR_NUMBER --json title,author,changedFiles,files,additions,deletions,body)

if [ $? -ne 0 ]; then
    echo "❌ PR을 찾을 수 없습니다. PR 번호를 확인하세요."
    exit 1
fi

PR_TITLE=$(echo "$PR_INFO" | jq -r '.title')
PR_AUTHOR=$(echo "$PR_INFO" | jq -r '.author.login')
PR_FILES=$(echo "$PR_INFO" | jq -r '.changedFiles')
PR_ADDITIONS=$(echo "$PR_INFO" | jq -r '.additions')
PR_DELETIONS=$(echo "$PR_INFO" | jq -r '.deletions')

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📌 PR 정보"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "제목: $PR_TITLE"
echo "작성자: $PR_AUTHOR"
echo "변경된 파일 수: $PR_FILES"
echo "추가된 줄: +$PR_ADDITIONS"
echo "삭제된 줄: -$PR_DELETIONS"
echo ""

# 변경된 파일 목록
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 변경된 파일 목록"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
gh pr view $PR_NUMBER --json files --jq '.files[] | "\(.path) (\(.additions) additions, \(.deletions) deletions)"'
echo ""

# PR diff 가져오기
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 변경사항 확인 중..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# PR diff를 파일로 저장
DIFF_FILE="/tmp/pr_${PR_NUMBER}_diff.txt"
gh pr diff $PR_NUMBER > "$DIFF_FILE"

if [ $? -eq 0 ]; then
    echo "✅ PR diff 저장 완료: $DIFF_FILE"
    echo ""
    echo "💡 다음 명령어로 전체 diff를 확인할 수 있습니다:"
    echo "   cat $DIFF_FILE"
    echo "   또는"
    echo "   less $DIFF_FILE"
else
    echo "⚠️  PR diff를 가져오는데 실패했습니다."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 코드 리뷰 체크리스트"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "다음 항목들을 확인하세요:"
echo ""
echo "1. ✅ 기능이 올바르게 동작하는가?"
echo "2. ✅ 코드 스타일이 프로젝트 컨벤션을 따르는가?"
echo "3. ✅ 에러 처리가 적절한가?"
echo "4. ✅ 보안 취약점이 없는가?"
echo "5. ✅ 성능 문제가 없는가?"
echo "6. ✅ 테스트 코드가 포함되어 있는가?"
echo "7. ✅ 주석과 문서화가 충분한가?"
echo "8. ✅ 불필요한 코드가 없는가?"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

