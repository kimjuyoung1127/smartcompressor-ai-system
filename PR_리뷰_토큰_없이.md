# 🔍 PR 리뷰 - GitHub CLI 없이 하기

GitHub CLI 인증이 어려운 경우, 다른 방법으로 PR을 리뷰할 수 있습니다.

## 방법 1: PR 정보 직접 공유

다음 정보를 알려주시면 제가 분석해드립니다:

1. **PR 번호**
2. **변경된 파일 목록** (또는 PR URL)
3. **특정 파일의 변경 내용** (원하시는 경우)

예시:
```
PR #5
변경 파일:
- src/api/auth.js
- server/app.js
- package.json
```

## 방법 2: Git으로 PR diff 확인

```bash
# PR 브랜치 정보 확인
git fetch origin

# PR 번호를 알고 있다면
git fetch origin pull/5/head:pr-5
git checkout pr-5
git diff main

# 또는 특정 파일만
git diff main -- src/api/auth.js
```

## 방법 3: GitHub 웹에서 직접 확인

1. GitHub 웹사이트에서 PR 열기
2. "Files changed" 탭 확인
3. 변경된 코드 확인
4. 문제가 보이는 부분을 복사해서 제게 보여주시면 분석해드립니다

## 방법 4: 수동으로 diff 파일 만들기

```bash
# PR 브랜치 체크아웃
git fetch origin pull/<PR_NUMBER>/head:pr-<PR_NUMBER>
git checkout pr-<PR_NUMBER>

# diff 생성
git diff main > pr_diff.txt

# 분석 실행
python3 analyze_pr_changes.py pr_diff.txt
```

## 가장 쉬운 방법

**PR 번호만 알려주시면** 제가 변경된 파일을 찾아서 분석해드릴 수 있습니다!

또는 **PR의 변경 파일 목록**을 복사해서 보여주시면 해당 파일들을 직접 확인해서 리뷰해드리겠습니다.

