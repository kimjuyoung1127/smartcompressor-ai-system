#!/usr/bin/env python3
"""
안전한 서버 실행 스크립트 (.env 오류 무시)
"""

import sys
import os
from pathlib import Path
import warnings

# .env 파일 오류 무시를 위한 설정
warnings.filterwarnings('ignore', category=UserWarning)

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# .env 파일 문제 해결 시도
try:
    env_path = project_root / ".env"
    if env_path.exists():
        # null 바이트 제거 시도
        try:
            with open(env_path, 'rb') as f:
                content = f.read()
            if b'\x00' in content:
                print("⚠️ .env 파일에 null 바이트 발견. 수정 중...")
                with open(env_path, 'wb') as f:
                    f.write(content.replace(b'\x00', b''))
                print("✅ .env 파일 수정 완료")
        except Exception as e:
            print(f"⚠️ .env 파일 수정 실패 (무시): {e}")
except Exception:
    pass

if __name__ == "__main__":
    # dotenv 로드 오류를 무시하기 위해 모듈 레벨에서 패치
    import dotenv
    
    # dotenv.load_dotenv을 안전한 버전으로 교체
    original_load_dotenv = dotenv.load_dotenv
    
    def safe_load_dotenv(*args, **kwargs):
        """null 바이트 오류를 무시하는 안전한 load_dotenv"""
        try:
            return original_load_dotenv(*args, **kwargs)
        except ValueError as e:
            if "embedded null byte" in str(e):
                print("⚠️ .env 파일에 null 바이트가 있습니다. .env 파일을 건너뜁니다.")
                # .env 파일 없이 진행
                return False
            raise
    
    # dotenv 모듈의 load_dotenv 함수 교체
    dotenv.load_dotenv = safe_load_dotenv
    
    # routes 모듈에서도 안전하게 로드되도록
    import sys
    if 'routes.auth_routes' in sys.modules:
        # 이미 로드된 경우 재로드
        import importlib
        importlib.reload(sys.modules['routes.auth_routes'])
    
    from app import create_app
    
    app = create_app()
    
    print("\n" + "="*80)
    print("ESP32 실시간 모니터링 서버 시작 (안전 모드)")
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

