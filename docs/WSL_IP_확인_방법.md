# WSL IP 주소 확인 방법

## 문제

WSL에서 `hostname -I` 명령어가 작동하지 않는 경우 (BusyBox 환경) 다른 방법을 사용해야 합니다.

## 해결 방법

### 방법 1: 간단한 명령어 실행 (권장)

**Windows PowerShell에서:**

```powershell
# 방화벽 규칙만 추가 (가장 간단)
New-NetFirewallRule -DisplayName "WSL Flask Server" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow

# 브라우저에서 WSL IP 직접 사용
# (서버 로그에서 확인한 IP: 172.27.98.13)
```

그 다음 브라우저에서:
```
http://172.27.98.13:5000/static/dashboard-components/esp32-realtime-monitor.html
```

### 방법 2: WSL IP 주소 확인

**WSL 터미널에서:**

```bash
# 방법 1: ip 명령어
ip addr show eth0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1

# 방법 2: hostname 명령어 (BusyBox)
hostname -i

# 방법 3: ifconfig
ifconfig eth0 | grep 'inet ' | awk '{print $2}'

# 방법 4: 서버 로그 확인
# 서버 시작 시 "Running on http://172.27.98.13:5000" 메시지 확인
```

### 방법 3: 포트 포워딩 없이 직접 접속

가장 간단한 방법은 포트 포워딩 없이 **WSL IP 주소로 직접 접속**하는 것입니다:

1. **방화벽 규칙만 추가:**
   ```powershell
   New-NetFirewallRule -DisplayName "WSL Flask Server" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
   ```

2. **브라우저에서 접속:**
   ```
   http://172.27.98.13:5000/static/dashboard-components/esp32-realtime-monitor.html
   ```

## 서버 로그에서 IP 확인

서버 시작 시 로그에 다음 메시지가 표시됩니다:

```
 * Running on http://127.0.0.1:5000
 * Running on http://172.27.98.13:5000
```

여기서 `172.27.98.13`이 WSL IP 주소입니다.

## 참고

- WSL IP 주소는 WSL 재시작 시 변경될 수 있습니다
- 포트 포워딩 없이도 WSL IP로 직접 접속 가능합니다
- 가장 간단한 방법은 방화벽 규칙만 추가하고 WSL IP로 직접 접속하는 것입니다

