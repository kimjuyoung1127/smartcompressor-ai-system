# 서버 빠른 시작 가이드

## 🚀 서버 실행 (가장 간단한 방법)

**WSL 터미널에서:**

```bash
cd /root/smartcompressor-ai-system
source venv/bin/activate
python scripts/start_server_minimal.py
```

이 스크립트는:
- ✅ .env 파일 null 바이트 자동 수정
- ✅ null 바이트 오류 무시
- ✅ 서버 정상 실행

---

## 접속 URL

서버 실행 후 브라우저에서:

### ESP32 실시간 모니터링
```
http://localhost:5000/static/dashboard-components/esp32-realtime-monitor.html
```

### 보류 라벨링 대시보드
```
http://localhost:5000/static/dashboard-components/pending-labeling-widget.html
```

---

## 문제 해결

### 만약 여전히 오류가 발생하면:

```bash
# .env 파일 임시로 이름 변경
mv .env .env.backup

# 서버 실행
python scripts/start_server_minimal.py
```

---

## 서버 실행 확인

서버가 정상 실행되면:

```
================================================================================
ESP32 실시간 모니터링 서버 시작
================================================================================

🌐 서버 URL:
   http://localhost:5000

 * Running on http://0.0.0.0:5000
```

이 메시지가 보이면 성공입니다!

