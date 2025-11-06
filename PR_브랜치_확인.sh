#!/bin/bash
# PR #4 브랜치 정보 확인

echo "🔍 PR #4 브랜치 정보 확인..."
echo ""

# GitHub CLI로 확인
echo "GitHub CLI로 확인:"
gh pr view 4 --json headRefName,headRepository -q '
  "저장소: \(.headRepository.nameWithOwner)"
  + "\n브랜치: \(.headRefName)"
  + "\n전체: \(.headRepository.nameWithOwner):\(.headRefName)"
'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "원격 브랜치 목록:"
git ls-remote --heads origin | sed 's/.*refs\/heads\///' | sort

