# WSL에서 실행한 서버 접속 가이드

## 서버 상태 확인

서버는 정상적으로 실행 중입니다:
- ✅ Flask 서버: `http://0.0.0.0:5000`
- ✅ WSL 내부 IP: `http://172.27.98.13:5000`
- ✅ 로컬 IP: `http://127.0.0.1:5000`

## 접속 방법

### 방법 1: WSL IP 주소 사용 (권장)

Windows 브라우저에서 다음 URL을 사용하세요:

```
http://172.27.98.13:5000/static/dashboard-components/esp32-realtime-monitor.html
```

### 방법 2: localhost 사용 (WSL2)

WSL2에서는 자동 포트 포워딩이 지원됩니다. 다음 URL을 시도하세요:

```
http://localhost:5000/static/dashboard-components/esp32-realtime-monitor.html
```

만약 접속이 안 되면:
1. Windows 방화벽 확인
2. WSL 포트 포워딩 확인

### 방법 3: WSL 내부에서 테스트

WSL 터미널에서:

```bash
# 서버 응답 확인
curl http://localhost:5000/api/esp32/realtime/statistics

# 또는 브라우저가 설치되어 있다면
# (WSL에서 브라우저 실행은 권장하지 않음)
```

## 문제 해결

### 1. 포트 포워딩 확인

Windows PowerShell (관리자 권한)에서:

```powershell
# WSL 포트 포워딩 확인
netsh interface portproxy show all

# 포트 포워딩 추가 (필요시)
netsh interface portproxy add v4tov4 listenport=5000 listenaddress=0.0.0.0 connectport=5000 connectaddress=172.27.98.13
```

### 2. Windows 방화벽 확인

Windows 방화벽에서 포트 5000이 허용되어 있는지 확인하세요.

### 3. 서버 재시작

서버가 응답하지 않으면:

```bash
# WSL 터미널에서
Ctrl+C  # 서버 종료
python scripts/start_server_minimal.py  # 재시작
```

## 접속 URL 목록

### ESP32 실시간 모니터링 대시보드
```
http://172.27.98.13:5000/static/dashboard-components/esp32-realtime-monitor.html
또는
http://localhost:5000/static/dashboard-components/esp32-realtime-monitor.html
```

### 보류 라벨링 대시보드
```
http://172.27.98.13:5000/static/dashboard-components/pending-labeling-widget.html
또는
http://localhost:5000/static/dashboard-components/pending-labeling-widget.html
```

### API 엔드포인트
```
POST http://172.27.98.13:5000/api/esp32/realtime/detect
GET  http://172.27.98.13:5000/api/esp32/realtime/statistics
```

## 참고

- WSL2에서는 `localhost` 자동 포워딩이 지원됩니다
- WSL1에서는 WSL IP 주소를 직접 사용해야 합니다
- 서버가 `0.0.0.0`에서 실행 중이므로 모든 네트워크 인터페이스에서 접속 가능합니다

