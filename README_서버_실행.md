# 서버 실행 가이드

## 웹 대시보드 접속을 위해 서버 실행 필요

테스트는 성공했지만, 웹 대시보드를 보려면 Flask 서버를 실행해야 합니다.

---

## 서버 실행 방법

### 방법 1: 간단한 실행 (권장)

**WSL 터미널에서:**

```bash
cd /root/smartcompressor-ai-system
source venv/bin/activate
python scripts/start_server.py
```

또는:

```bash
bash scripts/start_server_simple.sh
```

### 방법 2: 직접 실행

```bash
cd /root/smartcompressor-ai-system
source venv/bin/activate
python app.py
```

---

## 접속 URL

서버 실행 후 브라우저에서 접속:

### 1. ESP32 실시간 모니터링 대시보드
```
http://localhost:5000/static/dashboard-components/esp32-realtime-monitor.html
```

### 2. 보류 라벨링 대시보드
```
http://localhost:5000/static/dashboard-components/pending-labeling-widget.html
```

### 3. API 엔드포인트
```
POST http://localhost:5000/api/esp32/realtime/detect
GET  http://localhost:5000/api/esp32/realtime/statistics
```

---

## 서버 실행 확인

서버가 정상 실행되면 다음과 같은 메시지가 표시됩니다:

```
================================================================================
ESP32 실시간 모니터링 서버 시작
================================================================================

🌐 서버 URL:
   http://localhost:5000

📊 대시보드:
   http://localhost:5000/static/dashboard-components/esp32-realtime-monitor.html

서버 실행 중... (Ctrl+C로 종료)
================================================================================

 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

---

## 문제 해결

### 문제: 포트 5000이 이미 사용 중
**해결:**
```bash
# 다른 포트 사용
FLASK_RUN_PORT=5001 python scripts/start_server.py
```

### 문제: 모듈을 찾을 수 없음
**해결:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

## 다음 단계

1. ✅ 서버 실행
2. 🌐 브라우저에서 대시보드 접속
3. 🔌 ESP32에서 데이터 전송
4. 📊 실시간 모니터링 확인

