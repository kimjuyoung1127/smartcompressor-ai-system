#!/bin/bash
# PR #4 빠른 리뷰

echo "🔍 PR #4 리뷰 중..."
echo ""

# PR 정보
echo "📋 PR 정보:"
gh pr view 4 --json title,author,state,additions,deletions,changedFiles --jq '
  "  제목: \(.title)",
  "  작성자: \(.author.login)",
  "  상태: \(.state)",
  "  추가: +\(.additions)줄 / 삭제: -\(.deletions)줄",
  "  변경파일: \(.changedFiles)개"
'
echo ""

# 변경 파일
echo "📁 변경된 파일:"
gh pr view 4 --json files --jq '.files[] | "  \(.path) (+\(.additions) -\(.deletions))"'
echo ""

# Diff 저장
echo "💾 Diff 저장 중..."
gh pr diff 4 > pr_4_diff.txt
echo "✅ 저장 완료: pr_4_diff.txt"
echo ""

# 자동 분석
if [ -f "analyze_pr_changes.py" ]; then
    echo "🤖 자동 분석 실행..."
    python3 analyze_pr_changes.py pr_4_diff.txt
fi

echo ""
echo "📄 전체 diff 확인: gh pr diff 4"
echo "💬 리뷰 작성: gh pr comment 4 --body \"리뷰 내용\""

