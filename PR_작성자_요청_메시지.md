# PR 작성자에게 충돌 해결 요청 메시지

---

주영님, PR #4에 충돌이 발생했습니다.

`nginx_signalcraft_config.conf` 파일에서 충돌이 있습니다.
아래 방법으로 해결해주시면 감사하겠습니다!

## 해결 방법 (GitHub 웹)

1. **PR #4 페이지로 이동**
2. **"Resolve conflicts"** 버튼 클릭
3. 웹 에디터에서:
   - `nginx_signalcraft_config.conf` 파일의 충돌 마커를 찾아서
   - **PR의 변경사항 유지** (파일이 `system/` 디렉토리로 이동한 것)
   - main의 최신 변경사항도 확인하여 필요한 부분 반영
4. **"Mark as resolved"** 클릭
5. **"Commit merge"** 클릭

## 또는 로컬에서

```bash
git checkout customer-dashboard
git fetch origin main
git merge origin/main

# 충돌 해결
# nginx_signalcraft_config.conf 파일에서 충돌 마커 제거
# PR 버전 (system/ 디렉토리) 유지

git add nginx_signalcraft_config.conf  # 또는 system/nginx_signalcraft_config.conf
git commit -m "충돌 해결: main 브랜치와 병합"
git push
```

감사합니다!

---

