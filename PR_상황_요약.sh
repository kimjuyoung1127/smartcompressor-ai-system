#!/bin/bash
# PR 상황 요약

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 모든 PR 목록"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
gh pr list --limit 20 --json number,title,state,mergeable,mergeStateStatus,headRefName --jq '.[] | "PR #\(.number) [\(.state)]: \(.title)\n   브랜치: \(.headRefName)\n   머지가능: \(.mergeable // "unknown"), 상태: \(.mergeStateStatus // "unknown")\n"'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PR #4 상세 (충돌 확인)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
gh pr view 4 --json number,title,state,mergeable,mergeStateStatus,mergeable --jq '
  "PR #\(.number): \(.title)\n" +
  "상태: \(.state)\n" +
  "머지 가능: \(.mergeable // "unknown")\n" +
  "머지 상태: \(.mergeStateStatus // "unknown")"
'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PWA 관련 PR 검색"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
gh pr list --search "pwa OR PWA" --json number,title,state,mergeable,mergeStateStatus --jq '.[] | "PR #\(.number): \(.title) | 상태: \(.state), 머지가능: \(.mergeable // "?")"'

