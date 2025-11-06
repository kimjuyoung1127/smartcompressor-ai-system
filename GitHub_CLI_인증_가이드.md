# 🔐 GitHub CLI 인증 가이드

## 🚀 빠른 시작

### 방법 1: 토큰 인증 (권장 - WSL에서 가장 안정적)

1. **토큰 생성**
   - 브라우저 열기: https://github.com/settings/tokens
   - "Generate new token" → "Generate new token (classic)" 클릭
   - Note: `gh-cli` (원하는 이름)
   - Expiration: 90 days 또는 No expiration
   - **권한 체크**:
     - ✅ **repo** (전체) - 필수
     - ✅ **workflow** (GitHub Actions 사용시)
     - ✅ **read:org** (조직 접근시)
   - "Generate token" 클릭
   - **토큰 복사** (한 번만 보여집니다! `ghp_`로 시작)

2. **인증 실행**
   ```bash
   gh auth login
   ```
   
   선택사항:
   - `What account?` → `GitHub.com` (Enter)
   - `What is your preferred protocol?` → `HTTPS` (화살표로 이동 후 Enter)
   - `Authenticate Git with your GitHub credentials?` → `Yes` (Enter)
   - `How would you like to authenticate?` → `Paste an authentication token` (선택)
   - 토큰 붙여넣기 (WSL: `Ctrl+Shift+V`)

3. **인증 확인**
   ```bash
   gh auth status
   ```
   
   다음과 같이 나오면 성공:
   ```
   ✓ Logged in to github.com as USERNAME
   ✓ Git operations for github.com configured to use HTTPS
   ```

### 방법 2: 브라우저 인증 (간단하지만 WSL에서 브라우저 문제 가능)

1. **인증 시작**
   ```bash
   gh auth login
   ```

2. **선택사항**
   - `What account?` → `GitHub.com`
   - `Protocol?` → `HTTPS` (화살표로 이동)
   - `Authenticate Git?` → `Yes`
   - `How to authenticate?` → `Login with a web browser`

3. **코드 확인 및 입력**
   - 코드가 표시됨 (예: `D9D0-CD46`)
   - 브라우저에서: https://github.com/login/device 방문
   - 코드 입력
   - GitHub 로그인
   - "Authorize GitHub CLI" 클릭

4. **완료**
   - 터미널로 돌아가서 Enter 누르기

## 🚨 문제 해결

### "Failed opening a web browser"
WSL에서 브라우저가 자동으로 열리지 않습니다. 해결 방법:
- **토큰 방식 사용** (위의 방법 1)
- 또는 코드를 수동으로 입력: https://github.com/login/device

### "Too many requests"
- 잠시 기다린 후 다시 시도
- 토큰 방식으로 전환

### 토큰이 작동하지 않음
- 토큰에 `repo` 권한이 있는지 확인
- 토큰이 만료되지 않았는지 확인
- 새 토큰 생성 후 다시 시도

## ✅ 인증 확인

```bash
# 현재 로그인 상태 확인
gh auth status

# 사용자 정보 확인
gh api user

# 저장소 목록 확인
gh repo list
```

## 🔄 재인증

```bash
# 기존 인증 제거
gh auth logout

# 다시 인증
gh auth login
```

## 📝 빠른 명령어

```bash
# 인증 시작 (자동 안내)
gh auth login

# 인증 상태 확인
gh auth status

# 재인증
gh auth refresh

# 로그아웃
gh auth logout
```

---

**지금 실행: `gh auth login` 후 토큰 방식 선택하세요!**

