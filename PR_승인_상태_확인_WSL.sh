#!/bin/bash
# PR 승인 상태 확인 (WSL용)

PR_NUMBER=4

echo "🔍 PR #$PR_NUMBER 승인 상태 확인 중..."
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PR 기본 정보"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
gh pr view $PR_NUMBER

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "리뷰 상태 (JSON)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
gh pr view $PR_NUMBER --json reviews,reviewDecision,state | jq '{
    state: .state,
    reviewDecision: .reviewDecision,
    reviews: [.reviews[] | {author: .author.login, state: .state, submittedAt: .submittedAt}]
}'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💡 해석"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "reviewDecision:"
echo "  - APPROVED: 승인됨 ✅"
echo "  - CHANGES_REQUESTED: 변경 요청됨"
echo "  - REVIEW_REQUIRED: 리뷰 필요"
echo "  - null: 아직 리뷰 없음"
echo ""
echo "reviews[].state:"
echo "  - APPROVED: 승인"
echo "  - CHANGES_REQUESTED: 변경 요청"
echo "  - COMMENTED: 코멘트만"
echo ""

