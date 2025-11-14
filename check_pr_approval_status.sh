#!/bin/bash
# PR 승인 상태 확인 스크립트

PR_NUMBER=4

echo "🔍 PR #$PR_NUMBER 승인 상태 확인 중..."
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PR 정보"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
gh pr view $PR_NUMBER --json state,title,author,reviews,reviewDecision,isDraft

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "리뷰 목록"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
gh pr view $PR_NUMBER --json reviews | jq -r '.reviews[] | "\(.author.login): \(.state) - \(.body // "(코멘트 없음)")"'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💡 참고"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "승인 상태:"
echo "  - APPROVED: 승인됨"
echo "  - CHANGES_REQUESTED: 변경 요청됨"
echo "  - REVIEW_REQUIRED: 리뷰 필요"
echo "  - null: 아직 리뷰 없음"
echo ""

