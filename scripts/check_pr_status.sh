#!/bin/bash
# PR 상태 확인 스크립트

PR_NUMBER=6

echo "=========================================="
echo "PR #$PR_NUMBER 상태 확인"
echo "=========================================="
echo ""

# GitHub CLI가 설치되어 있는지 확인
if ! command -v gh &> /dev/null; then
    echo "⚠️  GitHub CLI가 설치되지 않았습니다."
    echo ""
    echo "웹 브라우저에서 확인하세요:"
    echo "https://github.com/SEONBEOM-Kim/smartcompressor-ai-system/pull/$PR_NUMBER"
    echo ""
    exit 0
fi

# PR 정보 조회
echo "PR 정보 조회 중..."
gh pr view $PR_NUMBER --json state,merged,title,author,baseRefName,headRefName,url

echo ""
echo "=========================================="
echo "상태 설명"
echo "=========================================="
echo ""
echo "state: OPEN = PR이 열려있음 (아직 머지 안 됨)"
echo "       MERGED = PR이 머지됨"
echo "       CLOSED = PR이 닫힘"
echo ""
echo "merged: true = 머지됨, false = 머지 안 됨"
echo ""

