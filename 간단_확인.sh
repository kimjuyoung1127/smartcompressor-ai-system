#!/bin/bash
# 간단한 PR 확인

echo "PR 목록 (간단):"
echo ""

gh pr list --limit 10 --json number,title,state,mergeable,mergeStateStatus --jq '.[] | "PR #\(.number) [\(.state)]: \(.title) | 머지가능: \(.mergeable // "?"), 상태: \(.mergeStateStatus // "?")"'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PWA 관련 PR:"
gh pr list --search "pwa" --json number,title,state,mergeable

