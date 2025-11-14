#!/usr/bin/env python3
"""
서버 연결 테스트 스크립트
WSL 내부와 Windows에서 서버 접속 가능 여부를 확인합니다.
"""

import requests
import sys
from datetime import datetime

def test_server(url, name):
    """서버 연결 테스트"""
    try:
        print(f"\n{'='*60}")
        print(f"테스트: {name}")
        print(f"URL: {url}")
        print(f"{'='*60}")
        
        response = requests.get(url, timeout=5)
        print(f"✅ 성공: HTTP {response.status_code}")
        print(f"응답 크기: {len(response.content)} bytes")
        return True
    except requests.exceptions.ConnectionError:
        print(f"❌ 실패: 연결할 수 없습니다 (서버가 실행 중이지 않거나 방화벽 문제)")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ 실패: 타임아웃 (서버가 응답하지 않음)")
        return False
    except Exception as e:
        print(f"❌ 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("\n" + "="*60)
    print("ESP32 서버 연결 테스트")
    print(f"테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 테스트할 URL 목록
    test_urls = [
        ("http://localhost:5000/api/esp32/realtime/statistics", "WSL 내부 - API"),
        ("http://127.0.0.1:5000/api/esp32/realtime/statistics", "WSL 내부 - 127.0.0.1"),
        ("http://172.27.98.13:5000/api/esp32/realtime/statistics", "WSL IP - 172.27.98.13"),
    ]
    
    results = []
    for url, name in test_urls:
        result = test_server(url, name)
        results.append((name, result))
    
    # 결과 요약
    print("\n" + "="*60)
    print("테스트 결과 요약")
    print("="*60)
    for name, result in results:
        status = "✅ 성공" if result else "❌ 실패"
        print(f"{status}: {name}")
    
    # 권장 사항
    print("\n" + "="*60)
    print("권장 사항")
    print("="*60)
    if all(r[1] for r in results[:2]):  # WSL 내부는 성공
        print("✅ WSL 내부에서 서버는 정상 작동 중입니다.")
        print("\n💡 Windows 브라우저에서 접속하려면:")
        print("   1. Windows PowerShell (관리자 권한)에서:")
        print("      netsh interface portproxy add v4tov4 listenport=5000 listenaddress=0.0.0.0 connectport=5000 connectaddress=172.27.98.13")
        print("\n   2. Windows 방화벽 규칙 추가:")
        print("      New-NetFirewallRule -DisplayName 'WSL Flask Server' -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow")
        print("\n   3. 브라우저에서 접속:")
        print("      http://localhost:5000/static/dashboard-components/esp32-realtime-monitor.html")
    else:
        print("❌ WSL 내부에서도 서버 접속이 안 됩니다.")
        print("   서버가 실행 중인지 확인하세요:")
        print("   python scripts/start_server_minimal.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n테스트 중단됨")
        sys.exit(0)
