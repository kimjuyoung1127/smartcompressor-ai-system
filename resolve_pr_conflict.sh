#!/bin/bash
# PR #4 충돌 해결 스크립트

echo "🔧 PR #4 충돌 해결 중..."
echo ""

# 현재 브랜치 확인
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 현재 브랜치: $CURRENT_BRANCH"
echo ""

# main 브랜치로 이동
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  최신 main 브랜치 가져오기"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
git fetch origin main

# PR 브랜치 정보 확인
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  PR 브랜치 정보 확인"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
PR_BRANCH=$(gh pr view 4 --json headRefName --jq '.headRefName' 2>/dev/null)

if [ -z "$PR_BRANCH" ]; then
    echo "⚠️  PR 브랜치 정보를 가져올 수 없습니다."
    echo "GitHub CLI를 WSL에서 실행하거나, PR 페이지에서 브랜치 이름을 확인하세요."
    exit 1
fi

echo "PR 브랜치: $PR_BRANCH"
echo ""

# 충돌 파일 확인
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  충돌 파일 확인"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "nginx_signalcraft_config.conf 파일 차이 확인:"
git diff origin/main...origin/$PR_BRANCH -- nginx_signalcraft_config.conf | head -50

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  충돌 해결 방법"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "방법 1: PR 작성자(kimjuyoung1127)에게 요청"
echo "  - PR 브랜치에 main을 merge하여 충돌 해결 요청"
echo ""
echo "방법 2: 직접 해결 (대표님이 해결하는 경우)"
echo "  - PR 브랜치를 체크아웃"
echo "  - main 브랜치를 merge"
echo "  - 충돌 해결"
echo "  - push"
echo ""

