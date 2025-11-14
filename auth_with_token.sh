#!/bin/bash
# GitHub CLI 토큰으로 인증 (임시 스크립트)
# 사용법: ./auth_with_token.sh YOUR_TOKEN

if [ -z "$1" ]; then
    echo "❌ 오류: 토큰을 제공해야 합니다."
    echo ""
    echo "사용법: ./auth_with_token.sh YOUR_TOKEN"
    echo ""
    echo "또는 수동으로:"
    echo "  gh auth login"
    echo "  → GitHub.com"
    echo "  → HTTPS"
    echo "  → Yes"
    echo "  → Paste an authentication token"
    echo "  → 토큰 붙여넣기"
    exit 1
fi

TOKEN="$1"

echo "🔐 GitHub CLI 토큰으로 인증 중..."
echo ""

# 토큰으로 인증
echo "$TOKEN" | gh auth login --with-token

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 인증 성공!"
    echo ""
    echo "인증 상태 확인:"
    gh auth status
    echo ""
    echo "이제 PR 리뷰를 시작할 수 있습니다:"
    echo "  ./gh_pr_review.sh 4"
else
    echo ""
    echo "❌ 인증 실패"
    echo ""
    echo "수동으로 인증해보세요:"
    echo "  1. gh auth login"
    echo "  2. GitHub.com 선택"
    echo "  3. HTTPS 선택"
    echo "  4. Yes 선택"
    echo "  5. 'Paste an authentication token' 선택"
    echo "  6. 토큰 붙여넣기"
fi

