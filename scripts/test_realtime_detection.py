#!/usr/bin/env python3
"""
실시간 고장 판단 시스템 테스트 스크립트
"""

import sys
from pathlib import Path
import numpy as np
import time

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ai.realtime_anomaly_detector import RealtimeAnomalyDetector
from services.realtime_failure_detection_service import RealtimeFailureDetectionService
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_normal_sound():
    """정상 소리 테스트 (440Hz 사인파)"""
    print("\n" + "="*60)
    print("테스트 1: 정상 소리 (440Hz 사인파)")
    print("="*60)
    
    detector = RealtimeAnomalyDetector(use_pretrained_model=False)  # 빠른 테스트를 위해 모델 없이
    
    sample_rate = 16000
    duration = 2.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    normal_audio = np.sin(2 * np.pi * 440 * t)  # 440Hz 사인파
    
    result = detector.detect(normal_audio)
    
    print(f"고장 여부: {'⚠️ 고장' if result['is_failure'] else '✅ 정상'}")
    print(f"신뢰도: {result['confidence']:.2%}")
    print(f"이상 점수: {result['score']:.2f}")
    print(f"처리 시간: {result['processing_time_ms']:.2f}ms")
    print(f"사용 방법: {result['method']}")


def test_anomaly_sound():
    """이상 소리 테스트 (고주파 노이즈)"""
    print("\n" + "="*60)
    print("테스트 2: 이상 소리 (고주파 노이즈)")
    print("="*60)
    
    detector = RealtimeAnomalyDetector(use_pretrained_model=False)
    
    sample_rate = 16000
    duration = 2.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # 고주파 노이즈 + 불규칙 진동
    anomaly_audio = (
        np.sin(2 * np.pi * 2000 * t) * 0.5 +  # 2000Hz 고주파
        np.sin(2 * np.pi * 3000 * t) * 0.3 +  # 3000Hz 고주파
        np.random.randn(len(t)) * 0.2  # 노이즈
    )
    
    result = detector.detect(anomaly_audio)
    
    print(f"고장 여부: {'⚠️ 고장' if result['is_failure'] else '✅ 정상'}")
    print(f"신뢰도: {result['confidence']:.2%}")
    print(f"이상 점수: {result['score']:.2f}")
    print(f"처리 시간: {result['processing_time_ms']:.2f}ms")
    print(f"사용 방법: {result['method']}")
    
    if result.get('details', {}).get('feature_based', {}).get('flags'):
        print(f"이상 플래그: {result['details']['feature_based']['flags']}")


def test_service():
    """서비스 테스트"""
    print("\n" + "="*60)
    print("테스트 3: 실시간 판단 서비스")
    print("="*60)
    
    service = RealtimeFailureDetectionService(use_pretrained_model=False)
    
    sample_rate = 16000
    duration = 2.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # 여러 샘플 테스트
    test_cases = [
        ("정상 소리", np.sin(2 * np.pi * 440 * t)),
        ("이상 소리", np.sin(2 * np.pi * 2000 * t) + np.random.randn(len(t)) * 0.3),
    ]
    
    for name, audio in test_cases:
        result = service.process_audio(audio, device_id="test_device")
        
        print(f"\n{name}:")
        print(f"  고장 여부: {'⚠️ 고장' if result['is_failure'] else '✅ 정상'}")
        print(f"  신뢰도: {result['confidence']:.2%}")
        print(f"  알림 필요: {'🔔 예' if result['should_alert'] else '❌ 아니오'}")
    
    # 통계 조회
    stats = service.get_statistics()
    print(f"\n통계:")
    print(f"  총 샘플: {stats['total_samples']}")
    print(f"  고장 수: {stats['failure_count']}")
    print(f"  고장률: {stats['failure_rate']:.2%}")
    print(f"  평균 신뢰도: {stats['avg_confidence']:.2%}")


def test_performance():
    """성능 테스트"""
    print("\n" + "="*60)
    print("테스트 4: 성능 테스트 (10회 실행)")
    print("="*60)
    
    detector = RealtimeAnomalyDetector(use_pretrained_model=False)
    
    sample_rate = 16000
    duration = 2.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    test_audio = np.sin(2 * np.pi * 440 * t)
    
    times = []
    for i in range(10):
        start = time.time()
        result = detector.detect(test_audio)
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
    
    print(f"평균 처리 시간: {np.mean(times):.2f}ms")
    print(f"최소 처리 시간: {np.min(times):.2f}ms")
    print(f"최대 처리 시간: {np.max(times):.2f}ms")
    print(f"표준편차: {np.std(times):.2f}ms")


def main():
    """메인 테스트 실행"""
    print("="*60)
    print("실시간 고장 판단 시스템 테스트")
    print("="*60)
    
    try:
        test_normal_sound()
        test_anomaly_sound()
        test_service()
        test_performance()
        
        print("\n" + "="*60)
        print("✅ 모든 테스트 완료!")
        print("="*60)
        print("\n사용 방법:")
        print("  from ai.realtime_anomaly_detector import RealtimeAnomalyDetector")
        print("  detector = RealtimeAnomalyDetector()")
        print("  result = detector.detect(audio_data)")
        print("\nAPI 사용:")
        print("  POST /api/realtime/detect")
        print("  Body: {\"audio_data\": [...], \"device_id\": \"ESP32_001\"}")
        
    except Exception as e:
        logger.error(f"테스트 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

