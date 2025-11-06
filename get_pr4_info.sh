#!/bin/bash
# PR #4 정보 가져오기 및 리뷰 준비

echo "🔍 PR #4 'PR요청' 정보 수집 중..."
echo ""

# PR 기본 정보
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 PR 정보"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
gh pr view 4 --json title,author,state,body,additions,deletions,changedFiles,url --jq '
  "제목: \(.title)",
  "작성자: \(.author.login)",
  "상태: \(.state)",
  "추가: +\(.additions)줄",
  "삭제: -\(.deletions)줄",
  "변경파일: \(.changedFiles)개",
  "",
  "URL: \(.url)",
  "",
  "설명:",
  (.body // "설명 없음" | split("\n") | .[0:10] | join("\n"))
'
echo ""

# 변경된 파일 목록
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 변경된 파일 목록"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
gh pr view 4 --json files --jq '.files[] | "  \(.path) (+\(.additions) -\(.deletions))"'
echo ""

# Diff 저장
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💾 Diff 저장 중..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
gh pr diff 4 > pr_4_diff.txt
if [ $? -eq 0 ]; then
    LINES=$(wc -l < pr_4_diff.txt 2>/dev/null || echo "0")
    echo "✅ Diff 저장 완료: pr_4_diff.txt ($LINES 줄)"
    echo ""
    
    # 변경 파일 목록 저장
    gh pr view 4 --json files --jq '.files[].path' > pr_4_files.txt
    echo "✅ 변경 파일 목록 저장: pr_4_files.txt"
    echo ""
    
    # 자동 분석
    if [ -f "analyze_pr_changes.py" ]; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🤖 자동 코드 분석 실행..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        python3 analyze_pr_changes.py pr_4_diff.txt
        echo ""
    fi
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ 정보 수집 완료!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "다음 파일들이 생성되었습니다:"
    echo "  - pr_4_diff.txt (전체 변경사항)"
    echo "  - pr_4_files.txt (변경된 파일 목록)"
    echo ""
    echo "📄 Diff 확인: cat pr_4_diff.txt | less"
    echo "📋 파일 목록: cat pr_4_files.txt"
    echo ""
else
    echo "❌ Diff 저장 실패"
    exit 1
fi

