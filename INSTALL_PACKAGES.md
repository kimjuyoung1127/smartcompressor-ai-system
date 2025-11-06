# 누락된 패키지 설치 가이드

## 빠른 설치

**WSL 터미널에서:**

```bash
cd /root/smartcompressor-ai-system
source venv/bin/activate
pip install aiohttp schedule
```

또는:

```bash
bash scripts/install_missing_packages.sh
```

## 설치 확인

```bash
python -c "import aiohttp; import schedule; print('✅ 모든 패키지 설치됨')"
```

## 서버 실행

설치 후:

```bash
python scripts/start_server_minimal.py
```

