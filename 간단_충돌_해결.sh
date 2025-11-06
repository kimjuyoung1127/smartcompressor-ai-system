#!/bin/bash
# PR #4 충돌 해결 - 더 간단한 버전

set -e

echo "🔧 PR #4 충돌 해결 시작..."
echo ""

# 1. 원격 정보 가져오기
echo "📥 원격 브랜치 정보 가져오는 중..."
git fetch origin

# 2. PR 브랜치 이름 확인
echo "🔍 PR 브랜치 확인 중..."
PR_BRANCH=$(gh pr view 4 --json headRefName -q '.headRefName' 2>/dev/null || echo "")

if [ -z "$PR_BRANCH" ]; then
    echo "⚠️  GitHub CLI로 브랜치를 찾을 수 없습니다."
    echo ""
    echo "가능한 브랜치 목록:"
    git ls-remote --heads origin | grep -v "main\|master" | sed 's/.*refs\/heads\///' | head -10
    echo ""
    read -p "PR 브랜치 이름 입력: " PR_BRANCH
fi

echo "✅ PR 브랜치: $PR_BRANCH"
echo ""

# 3. 현재 상태 확인
CURRENT_BRANCH=$(git branch --show-current)
echo "현재 브랜치: $CURRENT_BRANCH"

# 변경사항 있으면 stash
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  변경사항을 stash 합니다..."
    git stash
    STASHED=true
else
    STASHED=false
fi

# 4. PR 브랜치 가져오기
echo ""
echo "📂 PR 브랜치 가져오는 중..."
if git show-ref --verify --quiet refs/heads/pr4-resolve; then
    git checkout pr4-resolve
    git fetch origin "$PR_BRANCH"
    git reset --hard "origin/$PR_BRANCH"
else
    git fetch origin "$PR_BRANCH:pr4-resolve"
    git checkout pr4-resolve
fi

echo "✅ PR 브랜치로 체크아웃 완료"
echo ""

# 5. main 브랜치 merge
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔄 main 브랜치 merge 중..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
git fetch origin main

# merge 시도
set +e
git merge origin/main --no-edit
MERGE_STATUS=$?
set -e

if [ $MERGE_STATUS -eq 0 ]; then
    echo "✅ 충돌 없이 merge 완료!"
    HAS_CONFLICT=false
else
    echo "⚠️  충돌 발생!"
    HAS_CONFLICT=true
fi

# 6. 충돌 해결
if [ "$HAS_CONFLICT" = true ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔧 충돌 해결 중..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # 충돌 파일 확인
    echo "충돌 파일:"
    git status --short | grep "^UU\|^AA\|^DD" || echo "  (충돌 파일 확인 중...)"
    echo ""
    
    # nginx_signalcraft_config.conf 충돌 해결
    CONFLICT_FILE=""
    if [ -f "system/nginx_signalcraft_config.conf" ]; then
        CONFLICT_FILE="system/nginx_signalcraft_config.conf"
    elif [ -f "nginx_signalcraft_config.conf" ]; then
        CONFLICT_FILE="nginx_signalcraft_config.conf"
    fi
    
    if [ -n "$CONFLICT_FILE" ] && [ -f "$CONFLICT_FILE" ]; then
        echo "📄 $CONFLICT_FILE 충돌 해결 중..."
        
        if grep -q "^<<<<<<< " "$CONFLICT_FILE"; then
            echo "  → PR 버전 유지 (--ours 사용)"
            git checkout --ours "$CONFLICT_FILE"
            git add "$CONFLICT_FILE"
            echo "  ✅ 충돌 해결 완료"
        else
            echo "  ✅ 충돌이 이미 해결되어 있습니다."
            git add "$CONFLICT_FILE"
        fi
    fi
    
    # 다른 충돌 파일 확인
    REMAINING_CONFLICTS=$(git status --short | grep "^UU\|^AA\|^DD" || true)
    
    if [ -z "$REMAINING_CONFLICTS" ]; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "💾 충돌 해결 커밋 중..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        git commit -m "충돌 해결: main 브랜치와 병합" || echo "⚠️  커밋 실패 (이미 커밋되었을 수 있음)"
        echo "✅ 커밋 완료!"
    else
        echo ""
        echo "⚠️  아직 해결되지 않은 충돌이 있습니다:"
        echo "$REMAINING_CONFLICTS"
        echo ""
        echo "수동으로 해결해주세요."
        exit 1
    fi
fi

# 7. 원격에 푸시
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 원격 저장소에 푸시 중..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if git push origin pr4-resolve:"$PR_BRANCH" --force-with-lease; then
    echo "✅ 푸시 완료!"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ 충돌 해결 완료!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "PR #4 페이지에서 충돌이 해결된 것을 확인할 수 있습니다."
else
    echo "❌ 푸시 실패"
    echo ""
    echo "수동으로 푸시하세요:"
    echo "  git push origin pr4-resolve:$PR_BRANCH --force-with-lease"
    exit 1
fi

# 8. 원래 브랜치로 돌아가기
if [ "$CURRENT_BRANCH" != "pr4-resolve" ]; then
    echo ""
    echo "원래 브랜치로 돌아가는 중: $CURRENT_BRANCH"
    git checkout "$CURRENT_BRANCH" 2>/dev/null || git checkout main
    
    if [ "$STASHED" = true ]; then
        git stash pop 2>/dev/null || true
    fi
fi

echo ""
echo "🎉 모든 작업 완료!"

