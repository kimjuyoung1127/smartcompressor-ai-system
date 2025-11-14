#!/bin/bash
# 커밋 준비 스크립트

set -e

echo "=========================================="
echo "Git 커밋 준비"
echo "=========================================="
echo ""

# .env 파일 확인
if git status --porcelain | grep -q "\.env$"; then
    echo "⚠️  .env 파일이 스테이징 영역에 있습니다!"
    echo "   .env 파일은 절대 커밋하지 마세요!"
    read -p "제거하시겠습니까? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git reset HEAD .env 2>/dev/null || true
        echo "✅ .env 파일 제거 완료"
    fi
fi

# 커밋할 주요 파일 그룹
echo "📦 커밋할 파일 그룹:"
echo ""

# 1. Docker 관련
echo "1. Docker 관련 파일"
git add Dockerfile docker-compose.yml docker-compose.dev.yml .dockerignore env.example 2>/dev/null || true

# 2. 문서 파일
echo "2. 문서 파일"
git add docs/*.md README*.md 2>/dev/null || true

# 3. 서비스 파일
echo "3. 서비스 파일"
git add services/*.py services/anomaly_detection_modules/ 2>/dev/null || true

# 4. 라우트 파일
echo "4. 라우트 파일"
git add routes/*.py 2>/dev/null || true

# 5. 테스트 파일
echo "5. 테스트 파일"
git add tests/ 2>/dev/null || true

# 6. 스크립트 파일
echo "6. 스크립트 파일"
git add scripts/*.sh scripts/*.py 2>/dev/null || true

# 7. UI 파일
echo "7. UI 파일"
git add static/pages/*.html 2>/dev/null || true

# 8. 설정 파일
echo "8. 설정 파일"
git add requirements.txt .gitignore 2>/dev/null || true

echo ""
echo "✅ 파일 스테이징 완료"
echo ""

# 스테이징된 파일 확인
echo "📋 스테이징된 파일:"
git status --short | head -20

echo ""
echo "=========================================="
echo "다음 단계:"
echo "=========================================="
echo ""
echo "1. 커밋 메시지 작성:"
echo "   git commit -m \"feat: 기능 설명\""
echo ""
echo "2. 또는 여러 커밋으로 나누기:"
echo "   git commit -m \"feat: Docker 설정 추가\""
echo "   git commit -m \"docs: 개발 가이드 추가\""
echo "   git commit -m \"feat: 실시간 대시보드 개선\""
echo ""
echo "3. 푸시:"
echo "   git push origin \$(git branch --show-current)"
echo ""

