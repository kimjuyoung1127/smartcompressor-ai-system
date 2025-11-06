#!/bin/bash
# PR #4 충돌 해결 - 직접 방법 (포크 저장소)

set -e

echo "🔧 PR #4 충돌 해결 (포크 저장소 직접 가져오기)..."
echo ""

# 1. 원격 정보 가져오기
echo "📥 원격 브랜치 정보 가져오는 중..."
git fetch origin

# 2. 현재 상태 저장
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

# 3. 포크 저장소에서 직접 가져오기
echo ""
echo "🔗 포크 저장소에서 PR 브랜치 가져오는 중..."
PR_BRANCH="customer-dashboard"
FORK_OWNER="kimjuyoung1127"
FORK_URL="https://github.com/${FORK_OWNER}/smartcompressor-ai-system.git"

echo "포크 URL: $FORK_URL"
echo "브랜치: $PR_BRANCH"
echo ""

# 포크에서 브랜치 가져오기
git fetch "$FORK_URL" "$PR_BRANCH:pr4-resolve" || {
    echo "❌ 포크 저장소에서 브랜치를 가져올 수 없습니다."
    echo ""
    echo "다른 방법: GitHub 웹에서 PR 작성자에게 'Resolve conflicts' 버튼 사용 요청"
    exit 1
}

# 4. PR 브랜치로 체크아웃
echo "📂 PR 브랜치로 체크아웃 중..."
git checkout pr4-resolve
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
        echo "📄 $CONFLICT_FILE 충돌 해결 중..."
    elif [ -f "nginx_signalcraft_config.conf" ]; then
        CONFLICT_FILE="nginx_signalcraft_config.conf"
        echo "📄 $CONFLICT_FILE 충돌 해결 중..."
    fi
    
    if [ -n "$CONFLICT_FILE" ] && [ -f "$CONFLICT_FILE" ]; then
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
        git commit -m "충돌 해결: main 브랜치와 병합"
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

# 7. 포크 저장소에 푸시
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚠️  포크 저장소에 직접 푸시할 권한이 없을 수 있습니다."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "해결 방법:"
echo ""
echo "1. GitHub 웹에서 PR 작성자(kimjuyoung1127)에게 요청:"
echo "   - PR #4 페이지에서 'Resolve conflicts' 버튼 사용"
echo ""
echo "2. 또는 PR 작성자에게 로컬에서 해결 후 푸시 요청:"
echo ""
echo "   다음 명령어를 PR 작성자에게 전달:"
echo "   ---"
echo "   git checkout customer-dashboard"
echo "   git fetch origin main"
echo "   git merge origin/main"
echo "   # 충돌 해결 후"
echo "   git add nginx_signalcraft_config.conf"
echo "   git commit -m '충돌 해결'"
echo "   git push"
echo "   ---"
echo ""

# 원래 브랜치로 돌아가기
if [ "$CURRENT_BRANCH" != "pr4-resolve" ]; then
    echo "원래 브랜치로 돌아가는 중: $CURRENT_BRANCH"
    git checkout "$CURRENT_BRANCH" 2>/dev/null || git checkout main
    
    if [ "$STASHED" = true ]; then
        git stash pop 2>/dev/null || true
    fi
fi

echo ""
echo "📋 현재 pr4-resolve 브랜치에 충돌 해결된 코드가 있습니다."
echo "   하지만 포크 저장소에 직접 푸시할 권한이 없으므로,"
echo "   PR 작성자에게 GitHub 웹에서 해결하도록 요청하세요."

