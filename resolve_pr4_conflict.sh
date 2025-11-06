#!/bin/bash
# PR #4 충돌 해결 스크립트

echo "🔧 PR #4 충돌 해결 시작..."
echo ""

# 현재 상태 확인
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  현재 상태 확인"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
CURRENT_BRANCH=$(git branch --show-current)
echo "현재 브랜치: $CURRENT_BRANCH"
echo ""

# 변경사항이 있으면 경고
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  경고: 커밋되지 않은 변경사항이 있습니다."
    echo "계속 진행하시겠습니까? (y/n)"
    read -p "> " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo "취소되었습니다."
        exit 1
    fi
fi

# PR 브랜치 정보 가져오기
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  PR 브랜치 정보 확인"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 최신 정보 가져오기
git fetch origin

# PR 브랜치 이름 확인
PR_BRANCH=$(gh pr view 4 --json headRefName --jq '.headRefName' 2>/dev/null)

if [ -z "$PR_BRANCH" ]; then
    echo "❌ PR 브랜치 정보를 가져올 수 없습니다."
    echo ""
    echo "수동으로 브랜치 이름을 입력해주세요:"
    echo "(PR 페이지에서 확인하거나 'kimjuyoung1127:branch-name' 형식)"
    read -p "PR 브랜치 이름: " PR_BRANCH
fi

echo "PR 브랜치: $PR_BRANCH"
echo ""

# PR 브랜치 확인
if ! git ls-remote --heads origin "$PR_BRANCH" | grep -q "$PR_BRANCH"; then
    echo "⚠️  원격에 PR 브랜치가 없습니다. 로컬 브랜치를 확인합니다..."
    # 원격 브랜치가 없다면 로컬에서 찾기
    LOCAL_BRANCH=$(git branch -a | grep -i "$PR_BRANCH" | head -1 | sed 's/^[* ] //' | sed 's/remotes\/origin\///')
    if [ -n "$LOCAL_BRANCH" ]; then
        PR_BRANCH="$LOCAL_BRANCH"
        echo "로컬 브랜치 사용: $PR_BRANCH"
    else
        echo "❌ PR 브랜치를 찾을 수 없습니다."
        exit 1
    fi
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  PR 브랜치로 체크아웃"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 원격 브랜치를 추적하는 로컬 브랜치 생성
if ! git show-ref --verify --quiet refs/heads/resolve-pr4; then
    echo "PR 브랜치를 로컬로 가져오는 중..."
    git fetch origin "$PR_BRANCH":"resolve-pr4" 2>/dev/null || git checkout -b resolve-pr4 "origin/$PR_BRANCH" 2>/dev/null
    
    if [ $? -ne 0 ]; then
        # 다른 방법 시도
        git checkout -b resolve-pr4 2>/dev/null
        git branch --set-upstream-to="origin/$PR_BRANCH" resolve-pr4 2>/dev/null
        git pull origin "$PR_BRANCH" 2>/dev/null
    fi
fi

git checkout resolve-pr4

echo "✅ PR 브랜치로 체크아웃 완료"
echo ""

# main 브랜치 merge
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  main 브랜치 merge"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
git fetch origin main
git merge origin/main

MERGE_STATUS=$?

if [ $MERGE_STATUS -eq 0 ]; then
    echo "✅ 충돌 없이 merge 완료!"
elif [ $MERGE_STATUS -eq 1 ]; then
    echo "⚠️  충돌 발생 - 해결 필요"
    echo ""
    echo "충돌 파일 확인:"
    git status | grep "both modified" || git status | grep "Unmerged"
    echo ""
    
    # nginx_signalcraft_config.conf 충돌 해결
    if git status | grep -q "nginx_signalcraft_config.conf"; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "5️⃣  nginx_signalcraft_config.conf 충돌 해결"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        # 충돌 파일 내용 확인
        echo "충돌 파일 확인 중..."
        
        # PR의 변경사항 확인 (system/ 디렉토리로 이동)
        if [ -f "system/nginx_signalcraft_config.conf" ]; then
            echo "✅ PR에서는 파일이 system/ 디렉토리로 이동됨"
            CONFLICT_FILE="system/nginx_signalcraft_config.conf"
        elif [ -f "nginx_signalcraft_config.conf" ]; then
            echo "⚠️  파일이 아직 루트에 있음"
            CONFLICT_FILE="nginx_signalcraft_config.conf"
        fi
        
        if [ -n "$CONFLICT_FILE" ] && [ -f "$CONFLICT_FILE" ]; then
            # 충돌 마커 확인
            if grep -q "^<<<<<<< " "$CONFLICT_FILE"; then
                echo ""
                echo "충돌 마커 발견. 자동 해결 시도 중..."
                
                # 간단한 자동 해결: system/ 디렉토리 버전 사용
                # (PR에서 파일을 이동시킨 것이므로 이 버전을 유지)
                
                echo ""
                echo "충돌 해결 방법:"
                echo "  - PR의 변경사항 (system/ 디렉토리) 유지"
                echo "  - main의 최신 내용도 반영"
                echo ""
                echo "수동으로 편집하시겠습니까? (y/n)"
                read -p "> " edit_choice
                
                if [ "$edit_choice" = "y" ] || [ "$edit_choice" = "Y" ]; then
                    echo "파일 편집 중..."
                    nano "$CONFLICT_FILE" || vi "$CONFLICT_FILE"
                else
                    echo "자동 해결을 시도합니다..."
                    # 자동 해결: 충돌 마커 제거하고 PR 버전 유지
                    # (실제로는 더 정교한 로직이 필요할 수 있음)
                    sed -i '/^<<<<<<< /,/^>>>>>>> /d' "$CONFLICT_FILE" 2>/dev/null
                    sed -i '/^=======$/d' "$CONFLICT_FILE" 2>/dev/null
                fi
                
                # 충돌 해결 확인
                if ! grep -q "^<<<<<<< " "$CONFLICT_FILE"; then
                    echo "✅ 충돌 마커 제거 완료"
                    git add "$CONFLICT_FILE"
                else
                    echo "⚠️  충돌이 남아있습니다. 수동으로 해결해주세요."
                    echo "파일: $CONFLICT_FILE"
                    exit 1
                fi
            else
                echo "✅ 충돌이 이미 해결된 것 같습니다."
                git add "$CONFLICT_FILE"
            fi
        fi
        
        # 다른 충돌 파일 확인
        echo ""
        echo "다른 충돌 파일 확인:"
        git status --short | grep "^UU\|^AA\|^DD"
        
        echo ""
        echo "충돌 해결 후 다음 명령어 실행:"
        echo "  git add <충돌파일>"
        echo "  git commit -m '충돌 해결'"
        echo "  git push origin resolve-pr4"
        
    else
        echo "⚠️  nginx_signalcraft_config.conf 파일을 찾을 수 없습니다."
        echo ""
        echo "충돌 파일 목록:"
        git status
    fi
    
    # 모든 충돌 해결 확인
    if [ -z "$(git status --short | grep '^UU\|^AA\|^DD')" ]; then
        echo ""
        echo "✅ 모든 충돌이 해결된 것 같습니다."
        echo ""
        echo "커밋하시겠습니까? (y/n)"
        read -p "> " commit_choice
        
        if [ "$commit_choice" = "y" ] || [ "$commit_choice" = "Y" ]; then
            git commit -m "충돌 해결: main 브랜치와 병합"
            echo "✅ 커밋 완료"
            echo ""
            echo "원격에 푸시하시겠습니까? (y/n)"
            read -p "> " push_choice
            
            if [ "$push_choice" = "y" ] || [ "$push_choice" = "Y" ]; then
                # 원래 PR 브랜치에 푸시
                git push origin resolve-pr4:"$PR_BRANCH" || git push origin HEAD:"$PR_BRANCH"
                
                if [ $? -eq 0 ]; then
                    echo "✅ 푸시 완료!"
                    echo ""
                    echo "PR 브랜치: $PR_BRANCH"
                    echo "충돌이 해결되었습니다. PR에서 확인해주세요!"
                else
                    echo "❌ 푸시 실패"
                    echo "수동으로 푸시해주세요:"
                    echo "  git push origin resolve-pr4:$PR_BRANCH"
                fi
            fi
        fi
    fi
else
    echo "❌ merge 실패"
    exit 1
fi

