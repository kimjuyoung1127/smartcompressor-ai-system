# 🔍 GitHub CLI로 PR 리뷰 가이드

## 🚀 빠른 시작

### 1단계: WSL 터미널에서 실행

**PowerShell이 아닌 WSL 터미널**에서 다음을 실행하세요:

```bash
cd ~/smartcompressor-ai-system
```

### 2단계: GitHub CLI 인증 (아직 안 했다면)

```bash
# 인증 상태 확인
gh auth status

# 인증이 안 되어 있다면
gh auth login
```

인증 과정:
1. **What account?** → `GitHub.com` 선택
2. **Protocol?** → `HTTPS` 선택 (화살표로 이동 후 Enter)
3. **Authenticate Git?** → `Yes` 선택
4. **How to authenticate?** → `Login with a web browser` 또는 `Paste an authentication token`

**브라우저로 로그인** 선택 시:
- 코드가 표시됨 (예: `D9D0-CD46`)
- https://github.com/login/device 에서 코드 입력
- GitHub 로그인 후 "Authorize GitHub CLI" 클릭

**토큰으로 로그인** 선택 시:
1. https://github.com/settings/tokens 방문
2. "Generate new token (classic)" 클릭
3. `repo` 권한 체크
4. 토큰 생성 후 복사
5. 터미널에 붙여넣기

### 3단계: PR 리뷰 실행

#### 방법 1: 자동 리뷰 스크립트 (권장)

```bash
chmod +x gh_pr_review.sh
./gh_pr_review.sh 4
```

#### 방법 2: 인터랙티브 리뷰 도구

```bash
chmod +x gh_pr_review_interactive.sh
./gh_pr_review_interactive.sh 4
```

#### 방법 3: GitHub CLI 직접 사용

```bash
# PR 정보 보기
gh pr view 4

# PR diff 보기
gh pr diff 4

# 변경된 파일 목록
gh pr view 4 --json files --jq '.files[] | "\(.path) (+\(.additions) -\(.deletions))"'

# 특정 파일의 diff
gh pr diff 4 -- path/to/file.js

# 리뷰 코멘트 작성
gh pr comment 4 --body "좋은 변경입니다!"

# PR 승인
gh pr review 4 --approve

# 변경 요청
gh pr review 4 --request-changes --body "이 부분을 수정해주세요"

# 코멘트만 작성
gh pr review 4 --comment --body "리뷰 코멘트"
```

## 📋 PR #4 리뷰 명령어 모음

### 기본 정보 확인
```bash
# PR 전체 정보
gh pr view 4

# PR 설명
gh pr view 4 --json body --jq '.body'

# 변경 통계
gh pr view 4 --json additions,deletions,changedFiles --jq '
  "추가: +\(.additions)줄",
  "삭제: -\(.deletions)줄", 
  "파일: \(.changedFiles)개"
'
```

### 코드 변경 확인
```bash
# 전체 diff
gh pr diff 4

# 파일별 요약
gh pr view 4 --json files --jq '.files[] | "\(.path): +\(.additions)/-\(.deletions)"'

# Diff를 파일로 저장
gh pr diff 4 > pr_4_diff.txt
```

### 리뷰 작성
```bash
# 일반 코멘트
gh pr comment 4 --body "코멘트 내용"

# 승인
gh pr review 4 --approve --body "LGTM! 잘 작성되었습니다."

# 변경 요청
gh pr review 4 --request-changes --body "이 부분을 수정해주세요: 
- 보안 검증 추가 필요
- 에러 처리 개선 필요"

# 코멘트만 (승인/거부 없이)
gh pr review 4 --comment --body "좋은 방향입니다. 다만..."
```

## 🤖 자동 분석과 함께

```bash
# 1. Diff 저장
gh pr diff 4 > pr_4_diff.txt

# 2. 자동 분석
python3 analyze_pr_changes.py pr_4_diff.txt

# 3. 결과 확인 후 리뷰 작성
gh pr review 4 --comment --body "분석 결과: [분석 내용]"
```

## 💡 유용한 팁

### PR 비교
```bash
# PR 브랜치와 main 비교
gh pr checkout 4
git diff main
```

### 파일별 상세 확인
```bash
# 특정 파일만 확인
gh pr diff 4 -- static/js/dashboard.js | less
```

### 리뷰 히스토리
```bash
# PR의 리뷰 코멘트 보기
gh pr view 4 --json reviews --jq '.reviews[] | "\(.author.login): \(.state)"'
```

## 🎯 완전 자동화된 리뷰 플로우

```bash
# 1. 스크립트로 정보 수집
./gh_pr_review.sh 4

# 2. 자동 분석 실행 (스크립트 내부에서 자동 실행됨)

# 3. 분석 결과 확인
cat pr_4_diff.txt | less

# 4. 리뷰 작성
gh pr review 4 --comment --body "$(python3 analyze_pr_changes.py pr_4_diff.txt)"
```

## 🚨 문제 해결

### "gh: command not found"
```bash
# GitHub CLI 설치 확인
which gh

# 설치가 안 되어 있다면
sudo apt update
sudo apt install gh
```

### "not authenticated"
```bash
# 인증 상태 확인
gh auth status

# 재인증
gh auth login
```

### "Too many requests"
- 잠시 기다린 후 다시 시도
- 또는 토큰 방식으로 인증 시도

## 📝 리뷰 작성 예시

### 승인 예시
```bash
gh pr review 4 --approve --body "
✅ 코드 품질: 좋습니다
✅ 테스트: 테스트 코드 포함됨
✅ 문서화: 주석 충분함

LGTM! 좋은 작업입니다.
"
```

### 변경 요청 예시
```bash
gh pr review 4 --request-changes --body "
⚠️ 변경 요청 사항:

1. 보안 이슈:
   - 하드코딩된 API 키 제거 필요
   - 입력값 검증 추가 필요

2. 에러 처리:
   - try-catch 블록 추가 권장
   - 에러 메시지 개선 필요

3. 성능:
   - 반복문 최적화 가능

수정 후 다시 리뷰 요청 부탁드립니다.
"
```

---

**지금 WSL 터미널에서 `./gh_pr_review.sh 4` 실행해보세요!**

