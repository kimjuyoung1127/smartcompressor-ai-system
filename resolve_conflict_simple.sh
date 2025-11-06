#!/bin/bash
# PR #4 충돌 해결 - 간단 버전

set -e

echo "🔧 PR #4 충돌 해결 시작..."
echo ""

# 1. 원격 정보 가져오기
echo "📥 원격 브랜치 정보 가져오는 중..."
git fetch origin

# 2. PR 브랜치 이름 확인 (GitHub CLI 사용)
echo "🔍 PR #4 브랜치 정보 확인 중..."
PR_BRANCH=$(gh pr view 4 --json headRefName -q '.headRefName' 2>/dev/null || echo "")

if [ -z "$PR_BRANCH" ]; then
    echo "⚠️  GitHub CLI로 브랜치 정보를 가져올 수 없습니다."
    echo ""
    echo "원격 브랜치 목록:"
    git ls-remote --heads origin | head -10
    echo ""
    echo "PR 브랜치 이름을 직접 입력해주세요 (예: reorganize-structure):"
    read -p "> " PR_BRANCH
fi

echo "✅ PR 브랜치: $PR_BRANCH"
echo ""

# 3. 현재 브랜치 저장
CURRENT_BRANCH=$(git branch --show-current)
echo "현재 브랜치: $CURRENT_BRANCH"

# 4. 변경사항 있으면 stash
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  변경사항을 stash 합니다..."
    git stash
    STASHED=true
else
    STASHED=false
fi

# 5. PR 브랜치로 체크아웃 (로컬에 없으면 생성)
echo ""
echo "📂 PR 브랜치로 체크아웃 중..."
if git show-ref --verify --quiet refs/heads/pr4-resolve; then
    git checkout pr4-resolve
    git reset --hard origin/$PR_BRANCH 2>/dev/null || git reset --hard "origin/$PR_BRANCH"
else
    git checkout -b pr4-resolve "origin/$PR_BRANCH" 2>/dev/null || {
        echo "원격 브랜치를 찾을 수 없습니다. 직접 가져오는 중..."
        git fetch origin "$PR_BRANCH:pr4-resolve" || {
            echo "❌ PR 브랜치를 가져올 수 없습니다."
            exit 1
        }
        git checkout pr4-resolve
    }
fi

echo "✅ PR 브랜치로 체크아웃 완료"
echo ""

# 6. main 브랜치 merge
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔄 main 브랜치 merge 중..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
git fetch origin main

# merge 시도 (충돌 발생 가능)
if git merge origin/main --no-edit; then
    echo "✅ 충돌 없이 merge 완료!"
    CONFLICT=false
else
    echo "⚠️  충돌 발생!"
    CONFLICT=true
fi

# 7. 충돌 해결
if [ "$CONFLICT" = true ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔧 충돌 해결 중..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # 충돌 파일 확인
    echo "충돌 파일:"
    git status --short | grep "^UU\|^AA\|^DD" || echo "  (충돌 파일 없음?)"
    echo ""
    
    # nginx_signalcraft_config.conf 충돌 해결
    if git status | grep -q "nginx_signalcraft_config.conf"; then
        echo "📄 nginx_signalcraft_config.conf 충돌 해결 중..."
        
        # 파일 위치 확인
        if [ -f "system/nginx_signalcraft_config.conf" ]; then
            CONFLICT_FILE="system/nginx_signalcraft_config.conf"
            echo "  → 파일 위치: system/nginx_signalcraft_config.conf (PR 변경사항 유지)"
        elif [ -f "nginx_signalcraft_config.conf" ]; then
            CONFLICT_FILE="nginx_signalcraft_config.conf"
            echo "  → 파일 위치: nginx_signalcraft_config.conf"
        else
            echo "  ⚠️  파일을 찾을 수 없습니다."
            CONFLICT_FILE=""
        fi
        
        if [ -n "$CONFLICT_FILE" ] && [ -f "$CONFLICT_FILE" ]; then
            # 충돌 마커 확인
            if grep -q "^<<<<<<< " "$CONFLICT_FILE"; then
                echo ""
                echo "  충돌 마커 발견!"
                
                # PR의 변경사항 유지 (system/ 디렉토리로 이동한 것)
                # main의 변경사항은 버리고 PR 버전 사용
                echo ""
                echo "  해결 방법: PR 버전 유지 (system/ 디렉토리 이동)"
                echo ""
                
                # 간단한 자동 해결: ours 사용 (PR 버전)
                echo "  자동 해결: PR 버전 유지..."
                git checkout --ours "$CONFLICT_FILE"
                
                # 파일이 system/ 디렉토리에 있는지 확인
                if [[ "$CONFLICT_FILE" != system/* ]]; then
                    echo "  ⚠️  파일이 system/ 디렉토리에 없습니다. 이동 필요할 수 있습니다."
                fi
                
                git add "$CONFLICT_FILE"
                echo "  ✅ 충돌 해결 완료"
            else
                echo "  ✅ 충돌이 이미 해결되어 있습니다."
                git add "$CONFLICT_FILE"
            fi
        fi
    fi
    
    # 다른 충돌 파일도 확인
    OTHER_CONFLICTS=$(git status --short | grep "^UU\|^AA\|^DD" | grep -v "nginx_signalcraft_config.conf" || true)
    if [ -n "$OTHER_CONFLICTS" ]; then
        echo ""
        echo "⚠️  다른 충돌 파일이 있습니다:"
        echo "$OTHER_CONFLICTS"
        echo ""
        echo "수동으로 해결해주세요:"
        echo "  git add <파일>"
    fi
    
    # 커밋
    if [ -z "$(git status --short | grep '^UU\|^AA\|^DD')" ]; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "💾 충돌 해결 커밋 중..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        git commit -m "충돌 해결: main 브랜치와 병합"
        echo "✅ 커밋 완료!"
    else
        echo ""
        echo "⚠️  아직 해결되지 않은 충돌이 있습니다."
        echo "다음 명령어로 수동 해결 후:"
        echo "  git add <파일>"
        echo "  git commit -m '충돌 해결'"
        exit 1
    fi
fi

# 8. 원격에 푸시
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 원격 저장소에 푸시 중..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 원래 PR 브랜치에 푸시
echo "PR 브랜치로 푸시: $PR_BRANCH"
if git push origin pr4-resolve:"$PR_BRANCH" --force-with-lease; then
    echo "✅ 푸시 완료!"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ 충돌 해결 완료!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "PR #4 페이지에서 충돌이 해결된 것을 확인할 수 있습니다."
    echo ""
    echo "다음 단계:"
    echo "  1. GitHub에서 PR #4 확인"
    echo "  2. 'Merge pull request' 버튼 활성화 확인"
    echo "  3. 승인 후 머지"
else
    echo "❌ 푸시 실패"
    echo ""
    echo "수동으로 푸시하세요:"
    echo "  git push origin pr4-resolve:$PR_BRANCH --force-with-lease"
    exit 1
fi

# 9. 원래 브랜치로 돌아가기
if [ "$CURRENT_BRANCH" != "pr4-resolve" ]; then
    echo ""
    echo "원래 브랜치로 돌아가는 중: $CURRENT_BRANCH"
    git checkout "$CURRENT_BRANCH" 2>/dev/null || git checkout main
    
    # stash 되돌리기
    if [ "$STASHED" = true ]; then
        git stash pop 2>/dev/null || true
    fi
fi

echo ""
echo "🎉 모든 작업 완료!"

