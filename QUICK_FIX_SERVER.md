# 서버 실행 오류 빠른 해결

## 문제: No module named 'aiohttp'

## 해결 방법

**WSL 터미널에서:**

```bash
cd /root/smartcompressor-ai-system
source venv/bin/activate
pip install aiohttp
```

또는:

```bash
bash scripts/install_missing_packages.sh
```

## 서버 실행

설치 후:

```bash
python scripts/start_server_minimal.py
```

## 접속 URL

```
http://localhost:5000/static/dashboard-components/esp32-realtime-monitor.html
```

