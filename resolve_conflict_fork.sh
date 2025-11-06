#!/bin/bash
# PR #4 충돌 해결 - 포크 저장소 대응

set -e

echo "🔧 PR #4 충돌 해결 시작 (포크 저장소 확인)..."
echo ""

# 1. 원격 정보 가져오기
echo "📥 원격 브랜치 정보 가져오는 중..."
git fetch origin

# 2. PR 정보 상세 확인
echo "🔍 PR #4 상세 정보 확인 중..."
PR_INFO=$(gh pr view 4 --json headRefName,headRepository,headRepositoryOwner 2>/dev/null)

PR_BRANCH=$(echo "$PR_INFO" | jq -r '.headRefName' 2>/dev/null || echo "customer-dashboard")
PR_REPO=$(echo "$PR_INFO" | jq -r '.headRepository.nameWithOwner' 2>/dev/null || echo "")
PR_OWNER=$(echo "$PR_INFO" | jq -r '.headRepositoryOwner.login' 2>/dev/null || echo "")

echo "PR 브랜치: $PR_BRANCH"
if [ -n "$PR_REPO" ] && [ "$PR_REPO" != "null" ]; then
    echo "PR 저장소: $PR_REPO"
    echo "PR 소유자: $PR_OWNER"
fi
echo ""

# 3. 포크 저장소 원격 추가 (필요한 경우)
if [ -n "$PR_OWNER" ] && [ "$PR_OWNER" != "null" ] && [ "$PR_OWNER" != "SEONBEOM-Kim" ]; then
    FORK_REMOTE="pr4-fork"
    FORK_URL="https://github.com/${PR_OWNER}/smartcompressor-ai-system.git"
    
    echo "🔗 포크 저장소 원격 추가 중..."
    if git remote get-url "$FORK_REMOTE" >/dev/null 2>&1; then
        echo "  이미 원격이 있습니다: $FORK_REMOTE"
        git remote set-url "$FORK_REMOTE" "$FORK_URL"
    else
        git remote add "$FORK_REMOTE" "$FORK_URL"
        echo "  ✅ 포크 원격 추가: $FORK_REMOTE"
    fi
    
    echo "  포크 저장소에서 브랜치 가져오는 중..."
    git fetch "$FORK_REMOTE" "$PR_BRANCH"
    PR_REMOTE="$FORK_REMOTE"
else
    # 같은 저장소에서 온 경우
    PR_REMOTE="origin"
    echo "  같은 저장소의 PR입니다."
    git fetch origin "$PR_BRANCH" 2>/dev/null || {
        echo "  ⚠️  원격 브랜치를 찾을 수 없습니다."
        if [ -n "$PR_OWNER" ] && [ "$PR_OWNER" != "null" ]; then
            echo "  포크 저장소에서 가져오는 중..."
            FORK_URL="https://github.com/${PR_OWNER}/smartcompressor-ai-system.git"
            git fetch "$FORK_URL" "$PR_BRANCH:$PR_BRANCH" 2>/dev/null || {
                echo "  ❌ 포크 저장소에서도 찾을 수 없습니다."
                echo ""
                echo "수동으로 PR을 가져오세요:"
                echo "  git fetch https://github.com/${PR_OWNER}/smartcompressor-ai-system.git $PR_BRANCH:$PR_BRANCH"
                exit 1
            }
        fi
    }
fi

# 4. 현재 상태 확인
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

# 5. PR 브랜치로 체크아웃
echo ""
echo "📂 PR 브랜치로 체크아웃 중..."

if git show-ref --verify --quiet refs/heads/pr4-resolve; then
    git checkout pr4-resolve
    # 포크에서 최신 가져오기
    if [ "$PR_REMOTE" != "origin" ]; then
        git fetch "$PR_REMOTE" "$PR_BRANCH"
        git reset --hard "$PR_REMOTE/$PR_BRANCH"
    else
        git reset --hard "$PR_BRANCH" 2>/dev/null || git reset --hard "origin/$PR_BRANCH"
    fi
else
    # 포크에서 브랜치 생성
    if [ "$PR_REMOTE" != "origin" ]; then
        git checkout -b pr4-resolve "$PR_REMOTE/$PR_BRANCH"
    else
        git checkout -b pr4-resolve "$PR_BRANCH" 2>/dev/null || git checkout -b pr4-resolve "origin/$PR_BRANCH"
    fi
fi

echo "✅ PR 브랜치로 체크아웃 완료"
echo ""

# 6. main 브랜치 merge
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

# 7. 충돌 해결
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

# 8. 원격에 푸시 (PR 브랜치로)
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 포크 저장소에 푸시 중..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$PR_REMOTE" != "origin" ]; then
    # 포크 저장소에 푸시
    echo "포크 저장소로 푸시: $PR_REMOTE/$PR_BRANCH"
    if git push "$PR_REMOTE" pr4-resolve:"$PR_BRANCH" --force-with-lease; then
        echo "✅ 푸시 완료!"
    else
        echo "⚠️  포크 저장소 푸시 실패 (권한 없을 수 있음)"
        echo ""
        echo "PR 작성자(kimjuyoung1127)에게 직접 해결을 요청하거나,"
        echo "GitHub 웹에서 'Resolve conflicts' 버튼을 사용하도록 안내해주세요."
        exit 1
    fi
else
    # 같은 저장소에 푸시
    if git push origin pr4-resolve:"$PR_BRANCH" --force-with-lease; then
        echo "✅ 푸시 완료!"
    else
        echo "❌ 푸시 실패"
        exit 1
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 충돌 해결 완료!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "PR #4 페이지에서 충돌이 해결된 것을 확인할 수 있습니다."

# 9. 원래 브랜치로 돌아가기
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

