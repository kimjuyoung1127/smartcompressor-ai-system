#!/bin/bash
# PR 브랜치 정보 가져오기

echo "🔍 PR #4 브랜치 정보 확인 중..."
echo ""

# GitHub CLI로 PR 정보 가져오기
gh pr view 4 --json headRefName,headRepository -q '
  "PR 브랜치: \(.headRepository.nameWithOwner):\(.headRefName)"
  + "\n저장소: \(.headRepository.nameWithOwner)"
  + "\n브랜치: \(.headRefName)"
'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "원격 브랜치 목록:"
git ls-remote --heads origin | grep -i "reorganize\|structure\|pr" || echo "(관련 브랜치 없음)"

