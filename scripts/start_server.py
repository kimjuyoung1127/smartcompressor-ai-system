#!/usr/bin/env python3
"""
ESP32 실시간 모니터링 서버 실행 스크립트
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    from app import create_app
    
    app = create_app()
    
    print("\n" + "="*80)
    print("ESP32 실시간 모니터링 서버 시작")
    print("="*80)
    print("\n🌐 서버 URL:")
    print("   http://localhost:5000")
    print("\n📊 대시보드:")
    print("   http://localhost:5000/static/dashboard-components/esp32-realtime-monitor.html")
    print("\n📋 보류 라벨링 대시보드:")
    print("   http://localhost:5000/static/dashboard-components/pending-labeling-widget.html")
    print("\n🔌 API 엔드포인트:")
    print("   POST http://localhost:5000/api/esp32/realtime/detect")
    print("   GET  http://localhost:5000/api/esp32/realtime/statistics")
    print("\n" + "="*80)
    print("서버 실행 중... (Ctrl+C로 종료)")
    print("="*80 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

