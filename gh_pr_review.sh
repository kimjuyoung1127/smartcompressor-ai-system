#!/bin/bash
# GitHub CLI를 사용한 PR 리뷰 스크립트
# 사용법: ./gh_pr_review.sh [PR_NUMBER]

PR_NUMBER="${1:-4}"

# WSL에서 실행 확인
if [[ "$OSTYPE" == "msys" ]] || [[ -n "$WINDIR" ]]; then
    echo "⚠️  이 스크립트는 WSL 터미널에서 실행해야 합니다."
    echo "PowerShell이 아닌 WSL bash에서 실행하세요."
    echo ""
    echo "예: wsl bash -c './gh_pr_review.sh 4'"
    exit 1
fi

echo "🔍 GitHub CLI로 PR #$PR_NUMBER 리뷰 시작..."
echo ""

# GitHub CLI 인증 확인
if ! gh auth status &>/dev/null; then
    echo "❌ GitHub CLI 인증이 필요합니다."
    echo ""
    echo "인증 방법:"
    echo "  gh auth login"
    echo ""
    echo "토큰으로 인증:"
    echo "  1. https://github.com/settings/tokens 에서 토큰 생성"
    echo "  2. gh auth login"
    echo "     → GitHub.com 선택"
    echo "     → HTTPS 선택"
    echo "     → 'Paste an authentication token' 선택"
    echo "     → 토큰 붙여넣기"
    exit 1
fi

echo "✅ GitHub CLI 인증 확인 완료"
echo ""

# PR 정보 가져오기
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 PR #$PR_NUMBER 정보"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
gh pr view $PR_NUMBER --json title,author,state,additions,deletions,changedFiles,body,url --jq '
  "제목: \(.title)",
  "작성자: \(.author.login)",
  "상태: \(.state)",
  "추가된 줄: +\(.additions)",
  "삭제된 줄: -\(.deletions)",
  "변경된 파일: \(.changedFiles)",
  "",
  "URL: \(.url)",
  "",
  "설명:",
  (.body // "설명 없음")
'
echo ""

# 변경된 파일 목록
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 변경된 파일 목록"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
gh pr view $PR_NUMBER --json files --jq '.files[] | "\(.path) (+\(.additions) -\(.deletions))"'
echo ""

# Diff 저장
DIFF_FILE="pr_${PR_NUMBER}_diff.txt"
echo "💾 Diff 파일 저장 중: $DIFF_FILE"
gh pr diff $PR_NUMBER > "$DIFF_FILE"

if [ $? -eq 0 ]; then
    LINES=$(wc -l < "$DIFF_FILE")
    echo "✅ 저장 완료 ($LINES 줄)"
    echo ""
    
    # Python 분석 스크립트 실행
    if [ -f "analyze_pr_changes.py" ]; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🤖 자동 코드 분석"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        python3 analyze_pr_changes.py "$DIFF_FILE"
        echo ""
    fi
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📄 전체 diff 확인"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "   cat $DIFF_FILE | less"
    echo "   또는"
    echo "   gh pr diff $PR_NUMBER"
    echo ""
fi

# 리뷰 옵션
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💬 리뷰 코멘트 작성"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "리뷰를 작성하려면:"
echo "  gh pr review $PR_NUMBER --approve      # 승인"
echo "  gh pr review $PR_NUMBER --request-changes  # 변경 요청"
echo "  gh pr review $PR_NUMBER --comment     # 코멘트만"
echo ""
echo "특정 파일에 코멘트 추가:"
echo "  gh pr comment $PR_NUMBER --body '리뷰 코멘트 내용'"
echo ""
echo "특정 줄에 코멘트 (인라인 리뷰):"
echo "  gh pr review $PR_NUMBER --comment --body '코멘트'"
echo ""

