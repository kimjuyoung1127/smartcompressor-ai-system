# WSL 서버 접속 문제 해결 가이드

## 🔍 문제 진단

서버는 정상적으로 실행 중이지만, Windows 브라우저에서 접속이 안 되는 경우는 **방화벽 또는 포트 포워딩 문제**입니다.

## ✅ 빠른 해결 방법

### 방법 1: Windows PowerShell 스크립트 실행 (권장)

**Windows PowerShell을 관리자 권한으로 실행**한 후:

```powershell
# 스크립트 실행
cd \\wsl.localhost\Ubuntu\root\smartcompressor-ai-system
.\scripts\fix_wsl_firewall.ps1
```

또는 직접 명령어 실행:

```powershell
# 1. 포트 포워딩 설정
netsh interface portproxy add v4tov4 listenport=5000 listenaddress=0.0.0.0 connectport=5000 connectaddress=172.27.98.13

# 2. 방화벽 규칙 추가
New-NetFirewallRule -DisplayName "WSL Flask Server" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

### 방법 2: WSL IP 주소 직접 사용

포트 포워딩 없이 **WSL IP 주소를 직접 사용**:

```
http://172.27.98.13:5000/static/dashboard-components/esp32-realtime-monitor.html
```

## 🧪 서버 연결 테스트

### WSL 터미널에서 테스트

```bash
# 서버 응답 확인
curl http://localhost:5000/api/esp32/realtime/statistics

# 또는 Python 스크립트 사용
python scripts/test_server_connection.py
```

### Windows PowerShell에서 테스트

```powershell
# 서버 응답 확인
Invoke-WebRequest -Uri "http://localhost:5000/api/esp32/realtime/statistics" -Method GET

# 또는 WSL IP 직접 테스트
Invoke-WebRequest -Uri "http://172.27.98.13:5000/api/esp32/realtime/statistics" -Method GET
```

## 📋 단계별 해결 방법

### 1단계: WSL 내부에서 서버 응답 확인

**WSL 터미널에서:**

```bash
# 서버가 실행 중인지 확인
curl http://localhost:5000/api/esp32/realtime/statistics
```

**응답이 오면**: 서버는 정상 작동 중입니다. → 2단계로 진행

**응답이 안 오면**: 서버 재시작 필요

```bash
# 서버 재시작
Ctrl+C  # 현재 서버 종료
python scripts/start_server_minimal.py
```

### 2단계: Windows 방화벽 설정

**Windows PowerShell (관리자 권한):**

```powershell
# 방화벽 규칙 추가
New-NetFirewallRule -DisplayName "WSL Flask Server" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

### 3단계: 포트 포워딩 설정 (선택사항)

**Windows PowerShell (관리자 권한):**

```powershell
# 포트 포워딩 추가
netsh interface portproxy add v4tov4 listenport=5000 listenaddress=0.0.0.0 connectport=5000 connectaddress=172.27.98.13

# 설정 확인
netsh interface portproxy show all
```

### 4단계: 브라우저에서 접속

포트 포워딩을 설정했다면:
```
http://localhost:5000/static/dashboard-components/esp32-realtime-monitor.html
```

포트 포워딩 없이 WSL IP 직접 사용:
```
http://172.27.98.13:5000/static/dashboard-components/esp32-realtime-monitor.html
```

## 🔧 문제 해결 체크리스트

- [ ] 서버가 WSL에서 실행 중인지 확인
- [ ] WSL 내부에서 `curl http://localhost:5000/api/esp32/realtime/statistics` 응답 확인
- [ ] Windows 방화벽 규칙 추가
- [ ] 포트 포워딩 설정 (또는 WSL IP 직접 사용)
- [ ] 브라우저에서 접속 시도

## ⚠️ 주의사항

1. **관리자 권한**: 방화벽 및 포트 포워딩 설정은 관리자 권한이 필요합니다.
2. **WSL IP 주소 변경**: WSL을 재시작하면 IP 주소가 변경될 수 있습니다. 그때마다 포트 포워딩을 다시 설정해야 합니다.
3. **방화벽 소프트웨어**: 서드파티 방화벽 소프트웨어가 설치되어 있다면 추가 설정이 필요할 수 있습니다.

## 🎯 권장 접속 방법

### 가장 확실한 방법: WSL IP 직접 사용

포트 포워딩 설정 없이도 접속 가능:

```
http://172.27.98.13:5000/static/dashboard-components/esp32-realtime-monitor.html
```

### 가장 편한 방법: localhost 사용

포트 포워딩 설정 후:

```
http://localhost:5000/static/dashboard-components/esp32-realtime-monitor.html
```

## 📞 추가 도움

문제가 계속되면:

1. WSL IP 주소 확인:
   ```bash
   wsl hostname -I
   ```

2. 포트 포워딩 확인:
   ```powershell
   netsh interface portproxy show all
   ```

3. 방화벽 규칙 확인:
   ```powershell
   Get-NetFirewallRule -DisplayName "WSL Flask Server"
   ```

