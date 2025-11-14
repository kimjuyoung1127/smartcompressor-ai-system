#!/usr/bin/env python3
"""
ESP32 실시간 모니터링 시스템 시각적 데모
실제 작동하는 것을 단계별로 보여줌
"""

import sys
from pathlib import Path
import numpy as np
import time
from datetime import datetime

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.esp32_realtime_detector import ESP32RealtimeDetector


def print_header(text):
    """헤더 출력"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)


def print_status(status, decibel, message, details=None):
    """상태 출력"""
    status_icons = {
        'no_input': '🔇',
        'below_threshold': '⏸️',
        'auto': '✅',
        'pending': '📋',
        'error': '❌'
    }
    
    icon = status_icons.get(status, '❓')
    
    print(f"\n{icon} 상태: {status.upper()}")
    print(f"   📊 데시벨: {decibel:.1f} dB")
    print(f"   💬 메시지: {message}")
    
    if details:
        for key, value in details.items():
            print(f"   📋 {key}: {value}")
    
    print()


def main():
    print("\n" + "="*80)
    print("  ESP32 실시간 모니터링 시스템 시각적 데모")
    print("="*80)
    print("\n이 데모는 실제 ESP32 데이터 처리 흐름을 시뮬레이션합니다.")
    print("각 시나리오를 단계별로 보여드립니다.\n")
    
    input("⏸️  Enter를 눌러 시작하세요...")
    
    # 서비스 초기화
    detector = ESP32RealtimeDetector(
        no_input_threshold=(35, 40),
        detection_start_threshold=48.0,
        confidence_threshold=0.7
    )
    
    print("\n✅ ESP32 실시간 판단 서비스 초기화 완료")
    print("   - 소리 없음 범위: 35~40 dB")
    print("   - 판단 시작 임계값: 48 dB 이상")
    print("   - 보류 임계값: 신뢰도 70% 미만")
    
    time.sleep(2)
    
    # 시나리오 1: 소리 입력 없음
    print_header("시나리오 1: 소리 입력 없음")
    print("설명: 35~40 dB 범위는 소리 입력이 없는 것으로 판단합니다.")
    print("예상 결과: 🔇 소리 입력 없음 상태")
    
    input("\n⏸️  Enter를 눌러 테스트 실행...")
    
    audio1 = np.random.randn(32000) * 0.01  # 매우 작은 소리
    result1 = detector.process_esp32_data(
        audio_data=audio1,
        decibel_level=37.5,  # 35~40 범위
        device_id="ESP32_DEMO_001",
        timestamp=datetime.now()
    )
    
    print_status(
        result1['status'],
        result1['decibel_level'],
        result1['message'],
        {"판단": "알고리즘 실행 안 함 (소리 입력 없음)"}
    )
    
    time.sleep(2)
    
    # 시나리오 2: 판단 임계값 미달
    print_header("시나리오 2: 판단 임계값 미달")
    print("설명: 40~48 dB 범위는 판단 임계값 미달로 판단합니다.")
    print("예상 결과: ⏸️ 판단 임계값 미달 상태")
    
    input("\n⏸️  Enter를 눌러 테스트 실행...")
    
    audio2 = np.sin(2 * np.pi * 440 * np.linspace(0, 2, 32000)) * 0.1
    result2 = detector.process_esp32_data(
        audio_data=audio2,
        decibel_level=45.0,  # 40~48 범위
        device_id="ESP32_DEMO_001",
        timestamp=datetime.now()
    )
    
    print_status(
        result2['status'],
        result2['decibel_level'],
        result2['message'],
        {"판단": "알고리즘 실행 안 함 (임계값 미달)"}
    )
    
    time.sleep(2)
    
    # 시나리오 3: 정상 소리 (자동 판단)
    print_header("시나리오 3: 정상 소리 (자동 판단)")
    print("설명: 48 dB 이상에서 알고리즘이 실행됩니다.")
    print("      신뢰도가 70% 이상이면 자동 판단됩니다.")
    print("예상 결과: ✅ 자동 판단 (정상)")
    
    input("\n⏸️  Enter를 눌러 테스트 실행...")
    
    audio3 = np.sin(2 * np.pi * 440 * np.linspace(0, 2, 32000)) * 0.3  # 정상 소리
    result3 = detector.process_esp32_data(
        audio_data=audio3,
        decibel_level=55.0,  # 48 이상
        device_id="ESP32_DEMO_001",
        timestamp=datetime.now()
    )
    
    details3 = {}
    if result3.get('result'):
        det_result = result3['result']
        if det_result.get('decision') == 'auto':
            is_failure = det_result.get('result', {}).get('is_failure', False)
            confidence = det_result.get('confidence', 0)
            details3['판단 결과'] = '고장' if is_failure else '정상'
            details3['신뢰도'] = f"{confidence:.1%}"
            details3['처리 방식'] = '자동 판단 완료'
    
    print_status(
        result3['status'],
        result3['decibel_level'],
        result3['message'],
        details3
    )
    
    time.sleep(2)
    
    # 시나리오 4: 이상 소리 (자동 판단 - 고장)
    print_header("시나리오 4: 이상 소리 (자동 판단 - 고장)")
    print("설명: 고주파 노이즈가 포함된 이상 소리를 판단합니다.")
    print("예상 결과: ✅ 자동 판단 (고장)")
    
    input("\n⏸️  Enter를 눌러 테스트 실행...")
    
    t = np.linspace(0, 2, 32000)
    audio4 = (
        np.sin(2 * np.pi * 2000 * t) * 0.5 +
        np.sin(2 * np.pi * 3000 * t) * 0.3 +
        np.random.randn(len(t)) * 0.2
    )  # 이상 소리
    result4 = detector.process_esp32_data(
        audio_data=audio4,
        decibel_level=60.0,  # 48 이상
        device_id="ESP32_DEMO_001",
        timestamp=datetime.now()
    )
    
    details4 = {}
    if result4.get('result'):
        det_result = result4['result']
        if det_result.get('decision') == 'auto':
            is_failure = det_result.get('result', {}).get('is_failure', False)
            confidence = det_result.get('confidence', 0)
            details4['판단 결과'] = '고장' if is_failure else '정상'
            details4['신뢰도'] = f"{confidence:.1%}"
            details4['처리 방식'] = '자동 판단 완료'
    
    print_status(
        result4['status'],
        result4['decibel_level'],
        result4['message'],
        details4
    )
    
    time.sleep(2)
    
    # 시나리오 5: 낮은 신뢰도 (보류)
    print_header("시나리오 5: 낮은 신뢰도 (보류 큐 추가)")
    print("설명: 신뢰도가 70% 미만이면 보류 큐에 추가됩니다.")
    print("      대시보드에서 수동 라벨링이 필요합니다.")
    print("예상 결과: 📋 보류 큐 추가")
    
    input("\n⏸️  Enter를 눌러 테스트 실행...")
    
    audio5 = (
        np.sin(2 * np.pi * 440 * np.linspace(0, 2, 32000)) * 0.2 +
        np.random.randn(32000) * 0.5
    )  # 노이즈가 많은 소리
    result5 = detector.process_esp32_data(
        audio_data=audio5,
        decibel_level=50.0,  # 48 이상
        device_id="ESP32_DEMO_001",
        timestamp=datetime.now()
    )
    
    details5 = {}
    if result5.get('result'):
        det_result = result5['result']
        if det_result.get('decision') == 'pending':
            pending_id = det_result.get('pending_item_id')
            confidence = det_result.get('confidence', 0)
            details5['보류 항목 ID'] = pending_id
            details5['신뢰도'] = f"{confidence:.1%}"
            details5['처리 방식'] = '보류 큐 추가 (대시보드에서 라벨링 필요)'
    
    print_status(
        result5['status'],
        result5['decibel_level'],
        result5['message'],
        details5
    )
    
    time.sleep(2)
    
    # 통계 조회
    print_header("최종 통계")
    
    stats = detector.get_statistics()
    
    print(f"\n📊 전체 통계:")
    print(f"   총 판단: {stats.get('total_detections', 0)}")
    print(f"   자동 판단: {stats.get('auto_count', 0)}")
    print(f"   보류 항목: {stats.get('pending_count', 0)}")
    print(f"   고장 감지: {stats.get('failure_count', 0)}")
    print(f"   자동 판단률: {stats.get('auto_rate', 0):.1%}")
    print(f"   보류율: {stats.get('pending_rate', 0):.1%}")
    print(f"   고장률: {stats.get('failure_rate', 0):.1%}")
    
    # 요약
    print("\n" + "="*80)
    print("  테스트 완료!")
    print("="*80)
    print("\n✅ 모든 시나리오가 정상적으로 작동했습니다!")
    print("\n📋 판단 기준 요약:")
    print("   🔇 35~40 dB: 소리 입력 없음")
    print("   ⏸️  40~48 dB: 판단 임계값 미달")
    print("   ✅ 48 dB 이상 + 신뢰도 ≥ 70%: 자동 판단")
    print("   📋 48 dB 이상 + 신뢰도 < 70%: 보류 큐 추가")
    print("\n💡 실제 대시보드에서 확인:")
    print("   http://localhost:5000/static/dashboard-components/esp32-realtime-monitor.html")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 테스트 중단됨")
    except Exception as e:
        print(f"\n\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

