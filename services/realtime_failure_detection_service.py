#!/usr/bin/env python3
"""
실시간 고장 판단 서비스
ESP32에서 들어오는 오디오 데이터를 실시간으로 분석하여 고장/비고장 판단
"""

import logging
import numpy as np
from datetime import datetime
from typing import Dict, Optional
from ai.realtime_anomaly_detector import RealtimeAnomalyDetector
from ai.realtime_anomaly_detector_with_mimii import RealtimeAnomalyDetectorWithMIMII

logger = logging.getLogger(__name__)


class RealtimeFailureDetectionService:
    """실시간 고장 판단 서비스"""
    
    def __init__(self, 
                 sample_rate: int = 16000,
                 window_size: float = 2.0,
                 use_pretrained_model: bool = True,
                 use_mimii_model: bool = True):
        """
        Args:
            sample_rate: 샘플링 레이트
            window_size: 분석 윈도우 크기 (초)
            use_pretrained_model: 오픈소스 사전 훈련 모델 사용 여부
            use_mimii_model: 기존 MIMII 모델 사용 여부 (92% 정확도)
        """
        if use_mimii_model:
            # MIMII 모델 통합 버전 사용 (우선순위: MIMII 92% > 폴백 80-90%)
            self.detector = RealtimeAnomalyDetectorWithMIMII(
                sample_rate=sample_rate,
                window_size=window_size,
                use_pretrained_model=use_pretrained_model
            )
        else:
            # 기본 실시간 판단 시스템만 사용
            self.detector = RealtimeAnomalyDetector(
                sample_rate=sample_rate,
                window_size=window_size,
                use_pretrained_model=use_pretrained_model
            )
        
        # 알림 임계값
        self.alert_threshold = 0.7  # 신뢰도 70% 이상일 때 알림
        
        # 히스토리
        self.detection_history = []
        self.max_history = 1000
        
        logger.info("✅ 실시간 고장 판단 서비스 초기화 완료")
    
    def process_audio(self, audio_data: np.ndarray, device_id: str = None) -> Dict:
        """
        오디오 데이터 처리 및 고장 판단
        
        Args:
            audio_data: 오디오 데이터 (numpy array 또는 list)
            device_id: 디바이스 ID (선택적)
        
        Returns:
            {
                'is_failure': bool,
                'confidence': float,
                'should_alert': bool,  # 알림 필요 여부
                'device_id': str,
                'timestamp': str,
                'details': dict
            }
        """
        try:
            # numpy array 변환
            if isinstance(audio_data, list):
                audio_data = np.array(audio_data, dtype=np.float32)
            elif not isinstance(audio_data, np.ndarray):
                audio_data = np.array(audio_data, dtype=np.float32)
            
            # 오디오 정규화
            if len(audio_data) > 0:
                max_val = np.max(np.abs(audio_data))
                if max_val > 0:
                    audio_data = audio_data / max_val
            
            # 고장 판단
            result = self.detector.detect(audio_data)
            
            # 알림 필요 여부 판단
            should_alert = (
                result['is_failure'] and 
                result['confidence'] >= self.alert_threshold
            )
            
            # 결과 구성
            detection_result = {
                'is_failure': result['is_failure'],
                'confidence': result['confidence'],
                'score': result['score'],
                'should_alert': should_alert,
                'device_id': device_id,
                'timestamp': datetime.now().isoformat(),
                'processing_time_ms': result.get('processing_time_ms', 0),
                'details': result.get('details', {})
            }
            
            # 히스토리 저장
            self.detection_history.append(detection_result)
            if len(self.detection_history) > self.max_history:
                self.detection_history.pop(0)
            
            # 로깅
            if should_alert:
                logger.warning(f"⚠️ 고장 감지: device={device_id}, confidence={result['confidence']:.2%}")
            else:
                logger.debug(f"✅ 정상: device={device_id}, confidence={result['confidence']:.2%}")
            
            return detection_result
            
        except Exception as e:
            logger.error(f"오디오 처리 실패: {e}")
            return {
                'is_failure': False,
                'confidence': 0.0,
                'score': 0.0,
                'should_alert': False,
                'device_id': device_id,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def get_statistics(self, device_id: str = None, hours: int = 24) -> Dict:
        """통계 정보 조회"""
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # 필터링
        filtered = [
            h for h in self.detection_history
            if (device_id is None or h.get('device_id') == device_id) and
               datetime.fromisoformat(h['timestamp']) >= cutoff_time
        ]
        
        if not filtered:
            return {
                'total_samples': 0,
                'failure_count': 0,
                'failure_rate': 0.0,
                'avg_confidence': 0.0
            }
        
        failure_count = sum(1 for h in filtered if h['is_failure'])
        avg_confidence = np.mean([h['confidence'] for h in filtered])
        
        return {
            'total_samples': len(filtered),
            'failure_count': failure_count,
            'failure_rate': failure_count / len(filtered),
            'avg_confidence': float(avg_confidence),
            'hours': hours
        }


if __name__ == "__main__":
    # 테스트 코드
    logging.basicConfig(level=logging.INFO)
    
    service = RealtimeFailureDetectionService()
    
    # 테스트 오디오
    sample_rate = 16000
    duration = 2.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    test_audio = np.sin(2 * np.pi * 440 * t)
    
    result = service.process_audio(test_audio, device_id="test_device_001")
    
    print("\n" + "="*60)
    print("실시간 고장 판단 서비스 테스트")
    print("="*60)
    print(f"고장 여부: {'⚠️ 고장' if result['is_failure'] else '✅ 정상'}")
    print(f"신뢰도: {result['confidence']:.2%}")
    print(f"알림 필요: {'🔔 예' if result['should_alert'] else '❌ 아니오'}")
    print(f"처리 시간: {result['processing_time_ms']:.2f}ms")
    print("="*60)

