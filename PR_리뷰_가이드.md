# 🔍 GitHub PR 코드 리뷰 가이드

## 🚀 빠른 시작

### 방법 1: 자동 리뷰 스크립트 사용 (권장)

```bash
# GitHub CLI 설치 확인
gh --version

# GitHub 인증 (처음 한 번만)
gh auth login

# PR 리뷰 시작
./review_pr.sh <PR_NUMBER>
# 예: ./review_pr.sh 5

# 또는 PR URL 사용
./review_pr.sh https://github.com/user/repo/pull/5
```

### 방법 2: PR diff 수동 분석

```bash
# PR 번호로 diff 가져오기
gh pr diff <PR_NUMBER> > pr_diff.txt

# Python 스크립트로 분석
python3 analyze_pr_changes.py pr_diff.txt
```

### 방법 3: Git으로 직접 확인

```bash
# PR 브랜치 fetch
git fetch origin pull/<PR_NUMBER>/head:pr-<PR_NUMBER>

# PR 브랜치 체크아웃
git checkout pr-<PR_NUMBER>

# main과 비교
git diff main...pr-<PR_NUMBER>

# 특정 파일만 확인
git diff main...pr-<PR_NUMBER> -- path/to/file.js
```

## 📋 코드 리뷰 체크리스트

### 1. 기능 검증
- [ ] PR 설명과 실제 변경사항이 일치하는가?
- [ ] 기능이 올바르게 동작하는가?
- [ ] 엣지 케이스가 처리되었는가?

### 2. 코드 품질
- [ ] 코드 스타일이 프로젝트 컨벤션을 따르는가?
- [ ] 변수명이 명확하고 의미있는가?
- [ ] 함수가 적절한 크기로 분리되었는가?
- [ ] 중복 코드가 없는가?

### 3. 보안
- [ ] SQL Injection 취약점이 없는가?
- [ ] XSS 취약점이 없는가?
- [ ] 하드코딩된 비밀번호/API 키가 없는가?
- [ ] 입력값 검증이 적절한가?

### 4. 에러 처리
- [ ] 예외 처리가 적절한가?
- [ ] 에러 메시지가 명확한가?
- [ ] 리소스 누수 가능성이 없는가?

### 5. 성능
- [ ] 불필요한 반복문이나 쿼리가 없는가?
- [ ] 메모리 누수 가능성이 없는가?
- [ ] 비동기 처리가 적절한가?

### 6. 테스트
- [ ] 테스트 코드가 포함되었는가?
- [ ] 기존 테스트가 통과하는가?
- [ ] 테스트 커버리지가 적절한가?

### 7. 문서화
- [ ] 코드 주석이 충분한가?
- [ ] README가 업데이트되었는가?
- [ ] API 문서가 업데이트되었는가?

## 🔧 자동 분석 도구

### 제공된 스크립트

1. **`review_pr.sh`**: GitHub CLI를 사용하여 PR 정보 가져오기
2. **`analyze_pr_changes.py`**: PR diff 파일을 분석하여 문제점 찾기

### 실행 예시

```bash
# 1. PR 정보 가져오기
./review_pr.sh 5

# 2. 생성된 diff 파일 분석
python3 analyze_pr_changes.py /tmp/pr_5_diff.txt

# 3. 결과 확인 및 리뷰 작성
```

## 💡 리뷰 작성 팁

### 좋은 리뷰 코멘트 예시

```
✅ 좋은 예:
"이 부분에서 에러 처리를 추가하면 더 안전할 것 같습니다. 
try-catch 블록으로 감싸는 것을 제안합니다."

❌ 나쉬 예:
"이거 안 좋아"
```

### 리뷰 우선순위

1. **높음 (Blocking)**: 보안 취약점, 치명적 버그
2. **중간 (Important)**: 코드 품질, 성능 문제
3. **낮음 (Nice to have)**: 스타일, 문서화

## 🚨 일반적인 문제점

### 보안 관련
- 하드코딩된 비밀번호/토큰
- SQL Injection 가능성
- XSS 취약점
- eval(), exec() 사용

### 코드 품질
- console.log/print 남아있음
- TODO/FIXME 주석
- debugger 문
- 불필요한 주석 처리된 코드

### 에러 처리
- 일반적인 except/catch
- 에러 처리 누락
- 리소스 정리 누락

### 성능
- 반복문 내 DOM 조작
- N+1 쿼리 문제
- 불필요한 재렌더링

## 📞 도움이 필요하신가요?

PR을 공유해주시면 제가 직접 분석해드릴 수 있습니다:
1. PR 번호를 알려주세요
2. 또는 PR의 변경된 파일 목록을 공유해주세요
3. 또는 특정 파일의 diff를 붙여넣어주세요

