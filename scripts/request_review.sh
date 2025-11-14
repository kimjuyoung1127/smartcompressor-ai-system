#!/bin/bash
# PR 리뷰 요청 스크립트

PR_NUMBER=6

echo "=========================================="
echo "PR #$PR_NUMBER 리뷰 요청"
echo "=========================================="
echo ""

# GitHub CLI 확인
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI가 설치되지 않았습니다."
    echo ""
    echo "설치 방법:"
    echo "  sudo apt install gh"
    echo "  gh auth login"
    echo ""
    echo "또는 웹 브라우저에서 직접:"
    echo "  https://github.com/SEONBEOM-Kim/smartcompressor-ai-system/pull/$PR_NUMBER"
    exit 1
fi

# 인증 확인
if ! gh auth status &> /dev/null; then
    echo "❌ GitHub 인증이 필요합니다."
    echo ""
    echo "인증 방법:"
    echo "  gh auth login"
    exit 1
fi

# 개발자 사용자명 입력
echo "개발자 GitHub 사용자명을 입력하세요:"
read -p "사용자명: " REVIEWER

if [ -z "$REVIEWER" ]; then
    echo "❌ 사용자명이 입력되지 않았습니다."
    exit 1
fi

# 리뷰어 추가
echo ""
echo "리뷰어 추가 중..."
gh pr edit $PR_NUMBER --add-reviewer "$REVIEWER"

if [ $? -eq 0 ]; then
    echo "✅ 리뷰 요청 완료!"
    echo ""
    echo "리뷰어: @$REVIEWER"
    echo "PR 링크: https://github.com/SEONBEOM-Kim/smartcompressor-ai-system/pull/$PR_NUMBER"
else
    echo "❌ 리뷰 요청 실패"
    exit 1
fi

# 코멘트 추가 여부 확인
echo ""
read -p "PR에 코멘트를 추가하시겠습니까? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    COMMENT="안녕하세요! @$REVIEWER 님

ESP32 실시간 모니터링 시스템 개발을 완료했습니다.
확인 부탁드립니다! 🙏

### 주요 구현 사항
- ✅ ESP32 실시간 판단 서비스
- ✅ 데시벨 기반 임계값 처리 (35-40dB: 소리 없음, 48dB 이상: 판단 시작)
- ✅ 디바이스 선택 기능
- ✅ 실시간 대시보드 구현
- ✅ MIMII 모델 통합 (92% 정확도)
- ✅ 보류 라벨링 시스템

### 테스트 방법
1. 서버 실행: \`python scripts/start_server_minimal.py\`
2. 대시보드 접속: \`http://172.27.98.13:5000/static/dashboard-components/esp32-realtime-monitor.html\`

### 참고사항
- 아직 main 브랜치에 머지하지 않았습니다 (검토 후 머지 예정)
- 서버 비용 발생 안 함 (다른 브랜치이므로 자동 배포 안 됨)

감사합니다!"
    
    echo "코멘트 추가 중..."
    gh pr comment $PR_NUMBER --body "$COMMENT"
    
    if [ $? -eq 0 ]; then
        echo "✅ 코멘트 추가 완료!"
    else
        echo "⚠️  코멘트 추가 실패 (리뷰 요청은 성공)"
    fi
fi

echo ""
echo "=========================================="
echo "완료!"
echo "=========================================="

