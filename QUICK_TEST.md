# 빠른 테스트 가이드

## WSL 터미널에서 실행

```bash
cd /root/smartcompressor-ai-system
source venv/bin/activate
python scripts/quick_test_esp32.py
```

## 시각적 데모 (단계별 확인)

```bash
cd /root/smartcompressor-ai-system
source venv/bin/activate
python scripts/test_esp32_visual_demo.py
```

Enter를 눌러 각 단계를 진행합니다.

## 전체 테스트

```bash
cd /root/smartcompressor-ai-system
source venv/bin/activate
python scripts/test_esp32_realtime_system.py
```

## 대시보드 접속

테스트 후 브라우저에서:
```
http://localhost:5000/static/dashboard-components/esp32-realtime-monitor.html
```

