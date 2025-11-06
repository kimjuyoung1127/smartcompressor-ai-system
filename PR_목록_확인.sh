#!/bin/bash
# 모든 PR 목록 확인

echo "🔍 모든 PR 목록 확인 중..."
echo ""

gh pr list --json number,title,headRefName,state,mergeable,mergeStateStatus,author --jq '.[] | "PR #\(.number): \(.title)\n   브랜치: \(.headRefName)\n   상태: \(.state)\n   머지 가능: \(.mergeable // "unknown")\n   머지 상태: \(.mergeStateStatus // "unknown")\n   작성자: \(.author.login)\n"' | head -50

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PR #4 상세 정보:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
gh pr view 4 --json number,title,state,mergeable,mergeStateStatus,isDraft

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "'pwa' 관련 PR 찾기:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
gh pr list --search "pwa" --json number,title,state,mergeable,mergeStateStatus

