#!/bin/bash
# ESP32 실시간 모니터링 시스템을 개발자에게 공유하기 위한 feature 브랜치 생성 스크립트

echo "=========================================="
echo "Feature 브랜치 생성 및 공유"
echo "=========================================="
echo ""

# 브랜치 이름
BRANCH_NAME="feature/esp32-realtime-detection-v1"

# 현재 브랜치 확인
CURRENT_BRANCH=$(git branch --show-current)
echo "현재 브랜치: $CURRENT_BRANCH"
echo ""

# main 브랜치인지 확인
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "⚠️  현재 브랜치가 main이 아닙니다."
    read -p "계속하시겠습니까? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 변경사항 확인
if [ -n "$(git status --porcelain)" ]; then
    echo "변경사항이 있습니다:"
    git status --short
    echo ""
    read -p "변경사항을 커밋하시겠습니까? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "변경사항 스테이징 중..."
        git add .
        
        echo "커밋 메시지 입력:"
        read -p "커밋 메시지 (기본값 사용하려면 Enter): " COMMIT_MSG
        
        if [ -z "$COMMIT_MSG" ]; then
            COMMIT_MSG="feat: ESP32 실시간 모니터링 시스템 구현

- ESP32 실시간 판단 서비스 추가
- 데시벨 기반 임계값 처리 (35-40dB: 소리 없음, 48dB 이상: 판단 시작)
- 디바이스 선택 기능 추가
- 실시간 대시보드 구현
- MIMII 모델 통합 (92% 정확도)
- 보류 라벨링 시스템 구현
- 스마트 판단 오케스트레이터 구현"
        fi
        
        git commit -m "$COMMIT_MSG"
        echo "✅ 커밋 완료"
    else
        echo "⚠️  변경사항을 커밋하지 않았습니다. 브랜치 생성 시 변경사항이 포함됩니다."
    fi
fi

# Feature 브랜치 생성
echo ""
echo "Feature 브랜치 생성 중: $BRANCH_NAME"
git checkout -b "$BRANCH_NAME"

if [ $? -eq 0 ]; then
    echo "✅ 브랜치 생성 완료: $BRANCH_NAME"
else
    echo "❌ 브랜치 생성 실패"
    exit 1
fi

# 원격 저장소에 푸시
echo ""
read -p "원격 저장소에 푸시하시겠습니까? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "원격 저장소에 푸시 중..."
    git push -u origin "$BRANCH_NAME"
    
    if [ $? -eq 0 ]; then
        echo "✅ 푸시 완료"
        echo ""
        echo "=========================================="
        echo "브랜치 공유 정보"
        echo "=========================================="
        echo "브랜치 이름: $BRANCH_NAME"
        echo "원격 저장소: $(git remote get-url origin)"
        echo ""
        echo "다음 단계:"
        echo "1. GitHub에서 Pull Request 생성"
        echo "2. 또는 개발자에게 브랜치 이름 공유: $BRANCH_NAME"
        echo ""
        echo "GitHub PR 링크:"
        echo "https://github.com/$(git remote get-url origin | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/compare/main...$BRANCH_NAME"
    else
        echo "❌ 푸시 실패"
        exit 1
    fi
else
    echo "⚠️  푸시하지 않았습니다. 나중에 다음 명령어로 푸시하세요:"
    echo "   git push -u origin $BRANCH_NAME"
fi

echo ""
echo "=========================================="
echo "완료!"
echo "=========================================="

