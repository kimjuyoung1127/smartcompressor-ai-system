#!/bin/bash
# PR #4 변경사항 확인 스크립트

echo "🔍 PR #4 변경사항 확인 중..."
echo ""

# Git 원격 저장소 확인
echo "📡 원격 저장소 확인..."
git remote -v
echo ""

# PR 브랜치 fetch 시도
echo "📥 PR 브랜치 가져오는 중..."
git fetch origin pull/4/head:pr-4-review 2>&1

if [ $? -eq 0 ]; then
    echo "✅ PR 브랜치 가져오기 성공"
    echo ""
    
    # 변경된 파일 목록 확인
    echo "📁 변경된 파일 목록:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    git diff --name-status main...pr-4-review
    echo ""
    
    # 통계
    echo "📊 변경 통계:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    git diff --stat main...pr-4-review
    echo ""
    
    # Diff 저장
    echo "💾 Diff 파일 저장 중..."
    git diff main...pr-4-review > pr_4_diff.txt
    echo "✅ 저장 완료: pr_4_diff.txt"
    echo ""
    
    # Python 분석 스크립트 실행
    if [ -f "analyze_pr_changes.py" ]; then
        echo "🔍 자동 분석 실행 중..."
        python3 analyze_pr_changes.py pr_4_diff.txt
    fi
    
else
    echo "⚠️  PR 브랜치를 가져올 수 없습니다."
    echo ""
    echo "다음 방법을 시도해보세요:"
    echo "1. Git 원격 저장소 확인: git remote -v"
    echo "2. 원격 업데이트: git fetch origin"
    echo "3. 또는 PR URL이나 변경 파일 목록을 직접 알려주세요"
fi

