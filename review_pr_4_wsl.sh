#!/bin/bash
# PR #4 리뷰 - WSL에서 실행

echo "🔍 PR #4 코드 리뷰 시작..."
echo ""

# PR 브랜치 가져오기
echo "📥 PR #4 브랜치 가져오는 중..."
git fetch origin pull/4/head:pr-4-review

if [ $? -ne 0 ]; then
    echo "❌ PR 브랜치를 가져올 수 없습니다."
    echo ""
    echo "💡 대안: PR의 변경 파일 목록을 알려주시면 직접 분석해드릴 수 있습니다."
    exit 1
fi

echo "✅ PR 브랜치 가져오기 완료"
echo ""

# 변경된 파일 목록
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 변경된 파일 목록"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
git diff --name-status main...pr-4-review
echo ""

# 통계
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 변경 통계"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
git diff --stat main...pr-4-review
echo ""

# Diff 저장
DIFF_FILE="pr_4_diff.txt"
echo "💾 Diff 파일 저장 중: $DIFF_FILE"
git diff main...pr-4-review > "$DIFF_FILE"
echo "✅ 저장 완료"
echo ""

# 변경된 파일 목록 저장
CHANGED_FILES="pr_4_changed_files.txt"
git diff --name-only main...pr-4-review > "$CHANGED_FILES"
echo "📋 변경된 파일 목록 저장: $CHANGED_FILES"
echo ""

# Python 분석 스크립트 실행
if [ -f "analyze_pr_changes.py" ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🤖 자동 코드 분석 실행 중..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    python3 analyze_pr_changes.py "$DIFF_FILE"
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ PR #4 정보 수집 완료"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📄 다음 파일들을 확인하세요:"
echo "   - $DIFF_FILE (전체 변경사항)"
echo "   - $CHANGED_FILES (변경된 파일 목록)"
echo ""
echo "💡 전체 diff 확인: cat $DIFF_FILE | less"

