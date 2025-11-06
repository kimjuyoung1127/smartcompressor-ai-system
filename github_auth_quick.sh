#!/bin/bash
# GitHub CLI 빠른 인증 가이드

echo "🔐 GitHub CLI 인증 안내"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "방법 1: 브라우저 인증 (간단)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. 다음 명령어 실행:"
echo "   gh auth login"
echo ""
echo "2. 선택사항:"
echo "   - What account? → GitHub.com"
echo "   - Protocol? → HTTPS (화살표로 이동)"
echo "   - Authenticate Git? → Yes"
echo "   - How to authenticate? → Login with a web browser"
echo ""
echo "3. 코드가 표시되면:"
echo "   - https://github.com/login/device 방문"
echo "   - 코드 입력"
echo "   - GitHub 로그인 후 승인"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "방법 2: 토큰 인증 (권장, WSL 브라우저 문제 해결)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. 브라우저에서 토큰 생성:"
echo "   https://github.com/settings/tokens"
echo ""
echo "2. 'Generate new token' → 'Generate new token (classic)' 클릭"
echo ""
echo "3. 토큰 설정:"
echo "   - Note: gh-cli (원하는 이름)"
echo "   - Expiration: 90 days 또는 No expiration"
echo "   - 권한 체크:"
echo "     ✅ repo (전체)"
echo "     ✅ workflow (GitHub Actions 사용시)"
echo "     ✅ read:org (조직 접근시)"
echo ""
echo "4. 'Generate token' 클릭"
echo ""
echo "5. 생성된 토큰 복사 (한 번만 보여집니다!)"
echo ""
echo "6. 다음 명령어 실행:"
echo "   gh auth login"
echo "   → GitHub.com"
echo "   → HTTPS"
echo "   → Yes"
echo "   → 'Paste an authentication token' 선택"
echo "   → 토큰 붙여넣기 (Ctrl+Shift+V)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

read -p "지금 인증을 시작하시겠습니까? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 GitHub CLI 인증 시작..."
    gh auth login
else
    echo ""
    echo "나중에 실행: gh auth login"
fi

