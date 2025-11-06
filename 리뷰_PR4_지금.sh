#!/bin/bash
# PR #4 코드 리뷰 실행 스크립트

echo "🔍 PR #4 코드 리뷰 시작..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 인증 확인
if ! gh auth status &>/dev/null; then
    echo "❌ GitHub CLI 인증이 필요합니다."
    echo "   gh auth login 실행 후 다시 시도하세요."
    exit 1
fi

echo "✅ GitHub CLI 인증 확인 완료"
echo ""

# PR 정보
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 PR #4 정보"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
gh pr view 4 --json title,author,state,additions,deletions,changedFiles,url --jq '
  "제목: \(.title)",
  "작성자: \(.author.login)",
  "상태: \(.state)",
  "추가: +\(.additions)줄",
  "삭제: -\(.deletions)줄",
  "변경파일: \(.changedFiles)개",
  "",
  "URL: \(.url)"
'
echo ""

# 변경된 파일 목록
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 변경된 파일 목록"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
gh pr view 4 --json files --jq '.files[] | "  \(.path) (+\(.additions) -\(.deletions))"'
echo ""

# Diff 저장
DIFF_FILE="pr_4_diff.txt"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💾 Diff 파일 저장 중: $DIFF_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
gh pr diff 4 > "$DIFF_FILE"

if [ $? -eq 0 ]; then
    LINES=$(wc -l < "$DIFF_FILE")
    echo "✅ 저장 완료 ($LINES 줄)"
    echo ""
    
    # 자동 분석 실행
    if [ -f "analyze_pr_changes.py" ]; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🤖 자동 코드 분석 실행 중..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        python3 analyze_pr_changes.py "$DIFF_FILE"
        echo ""
    fi
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📄 전체 diff 확인"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "   cat $DIFF_FILE | less"
    echo "   또는"
    echo "   gh pr diff 4"
    echo ""
else
    echo "❌ Diff 저장 실패"
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ PR #4 정보 수집 완료"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "다음 단계:"
echo "  1. $DIFF_FILE 파일 확인"
echo "  2. 코드 분석 결과 검토"
echo "  3. 리뷰 코멘트 작성:"
echo "     gh pr comment 4 --body \"리뷰 내용\""
echo "     또는"
echo "     gh pr review 4 --approve --body \"LGTM!\""
echo ""

