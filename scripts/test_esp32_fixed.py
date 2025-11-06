#!/usr/bin/env python3
"""
ESP32 실시간 모니터링 테스트 (수정 버전)
"""

import sys
from pathlib import Path
import numpy as np
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.esp32_realtime_detector import ESP32RealtimeDetector

print("\n" + "="*80)
print("ESP32 실시간 모니터링 테스트 (MIMII 모델 수정 버전)")
print("="*80 + "\n")

# 서비스 초기화
print("서비스 초기화 중...")
detector = ESP32RealtimeDetector()
print("✅ 초기화 완료\n")

# 테스트 1: 소리 없음
print("🔇 테스트 1: 소리 입력 없음 (37.5 dB)")
print("   예상: no_input 상태")
audio1 = np.random.randn(32000) * 0.01
result1 = detector.process_esp32_data(audio1, 37.5, "TEST_001")
print(f"   ✅ 상태: {result1['status']}")
print(f"   💬 메시지: {result1['message']}\n")

# 테스트 2: 정상 소리
print("✅ 테스트 2: 정상 소리 (55.0 dB)")
print("   예상: auto 상태 (정상 판단)")
audio2 = np.sin(2 * np.pi * 440 * np.linspace(0, 2, 32000)) * 0.3
result2 = detector.process_esp32_data(audio2, 55.0, "TEST_001")
print(f"   ✅ 상태: {result2['status']}")
print(f"   💬 메시지: {result2['message']}")

if result2.get('result') and result2['result'].get('decision') == 'auto':
    is_failure = result2['result']['result']['is_failure']
    confidence = result2['result']['confidence']
    method = result2['result'].get('method', 'unknown')
    print(f"   📊 판단: {'⚠️ 고장' if is_failure else '✅ 정상'}")
    print(f"   📈 신뢰도: {confidence:.1%}")
    print(f"   🔧 방법: {method}")
elif result2.get('result') and result2['result'].get('decision') == 'pending':
    confidence = result2['result']['confidence']
    pending_id = result2['result'].get('pending_item_id')
    print(f"   📋 보류 큐 추가 (신뢰도: {confidence:.1%})")
    print(f"   📝 보류 ID: {pending_id}")

print()

# 통계
stats = detector.get_statistics()
print("📊 최종 통계:")
print(f"   총 판단: {stats['total_detections']}")
print(f"   자동 판단: {stats['auto_count']}")
print(f"   보류 항목: {stats['pending_count']}")
print(f"   고장 감지: {stats['failure_count']}")
print(f"   자동 판단률: {stats['auto_rate']:.1%}")

print("\n" + "="*80)
print("✅ 테스트 완료!")
print("="*80)
print("\n💡 대시보드에서 확인:")
print("   http://localhost:5000/static/dashboard-components/esp32-realtime-monitor.html\n")

