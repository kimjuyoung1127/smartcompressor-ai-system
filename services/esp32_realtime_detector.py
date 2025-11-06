#!/usr/bin/env python3
"""
ESP32 실시간 판단 서비스
데시벨 기반 입력 유무 판단 + 실시간 고장 판단
"""

import logging
import numpy as np
from typing import Dict, Optional
from datetime import datetime
from services.smart_detection_orchestrator import SmartDetectionOrchestrator

logger = logging.getLogger(__name__)


class ESP32RealtimeDetector:
    """
    ESP32 실시간 판단 서비스
    
    판단 로직:
    - 35~40dB: 소리 입력 없음 (No Input)
    - 48dB 이상: 알고리즘 판단 시작
    """
    
    def __init__(self,
                 no_input_threshold: tuple = (35, 40),  # (min, max) dB
                 detection_start_threshold: float = 48.0,  # dB
                 confidence_threshold: float = 0.7):
        """
        Args:
            no_input_threshold: 소리 입력 없음 범위 (dB)
            detection_start_threshold: 알고리즘 판단 시작 임계값 (dB)
            confidence_threshold: 보류 임계값 (신뢰도)
        """
        self.no_input_threshold = no_input_threshold
        self.detection_start_threshold = detection_start_threshold
        self.confidence_threshold = confidence_threshold
        
        # 스마트 판단 오케스트레이터
        self.orchestrator = SmartDetectionOrchestrator(
            confidence_threshold=confidence_threshold,
            use_mimii_model=True
        )
        
        # 상태 관리
        self.last_detection_time = {}
        self.detection_history = {}  # {device_id: [history]}
        
        logger.info("✅ ESP32 실시간 판단 서비스 초기화 완료")
        logger.info(f"   - 소리 없음 범위: {no_input_threshold[0]}~{no_input_threshold[1]} dB")
        logger.info(f"   - 판단 시작 임계값: {detection_start_threshold} dB 이상")
    
    def process_esp32_data(self,
                          audio_data: np.ndarray,
                          decibel_level: float,
                          device_id: str,
                          timestamp: datetime = None,
                          metadata: Dict = None) -> Dict:
        """
        ESP32 데이터 처리
        
        Args:
            audio_data: 오디오 데이터
            decibel_level: 데시벨 레벨
            device_id: 디바이스 ID
            timestamp: 타임스탬프
            metadata: 추가 메타데이터
        
        Returns:
            {
                'status': 'no_input' | 'processing' | 'auto' | 'pending',
                'decibel_level': float,
                'result': {...},  # 판단 결과 (processing 이상일 때)
                'message': str
            }
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # 1단계: 소리 입력 유무 확인
        if self.no_input_threshold[0] <= decibel_level <= self.no_input_threshold[1]:
            return {
                'status': 'no_input',
                'decibel_level': decibel_level,
                'result': None,
                'message': f'소리 입력 없음 ({decibel_level:.1f} dB)',
                'timestamp': timestamp.isoformat()
            }
        
        # 2단계: 판단 시작 임계값 확인
        if decibel_level < self.detection_start_threshold:
            return {
                'status': 'below_threshold',
                'decibel_level': decibel_level,
                'result': None,
                'message': f'판단 임계값 미달 ({decibel_level:.1f} dB < {self.detection_start_threshold} dB)',
                'timestamp': timestamp.isoformat()
            }
        
        # 3단계: 알고리즘 판단 수행
        try:
            detection_result = self.orchestrator.process_audio(
                audio_data=audio_data,
                device_id=device_id,
                metadata={
                    **(metadata or {}),
                    'decibel_level': decibel_level,
                    'timestamp': timestamp.isoformat()
                }
            )
            
            # 상태 결정
            if detection_result['decision'] == 'auto':
                status = 'auto'
                message = f"자동 판단: {'고장' if detection_result['result']['is_failure'] else '정상'} (신뢰도: {detection_result['confidence']:.1%})"
            else:
                status = 'pending'
                message = f"보류 큐 추가: 신뢰도 {detection_result['confidence']:.1%}"
            
            # 히스토리 저장
            if device_id not in self.detection_history:
                self.detection_history[device_id] = []
            
            self.detection_history[device_id].append({
                'timestamp': timestamp.isoformat(),
                'status': status,
                'decibel_level': decibel_level,
                'confidence': detection_result.get('confidence', 0.0),
                'is_failure': detection_result['result']['is_failure'] if detection_result.get('result') else False
            })
            
            # 최근 100개만 유지
            if len(self.detection_history[device_id]) > 100:
                self.detection_history[device_id] = self.detection_history[device_id][-100:]
            
            self.last_detection_time[device_id] = timestamp
            
            return {
                'status': status,
                'decibel_level': decibel_level,
                'result': detection_result,
                'message': message,
                'timestamp': timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"ESP32 데이터 처리 실패: {e}")
            return {
                'status': 'error',
                'decibel_level': decibel_level,
                'result': None,
                'message': f'처리 오류: {str(e)}',
                'timestamp': timestamp.isoformat(),
                'error': str(e)
            }
    
    def get_device_status(self, device_id: str) -> Dict:
        """디바이스 상태 조회"""
        history = self.detection_history.get(device_id, [])
        
        if not history:
            return {
                'device_id': device_id,
                'status': 'unknown',
                'last_detection': None,
                'total_detections': 0,
                'recent_status': None
            }
        
        recent = history[-1]
        
        return {
            'device_id': device_id,
            'status': recent['status'],
            'last_detection': recent['timestamp'],
            'total_detections': len(history),
            'recent_status': recent['status'],
            'recent_confidence': recent.get('confidence'),
            'recent_is_failure': recent.get('is_failure')
        }
    
    def get_statistics(self, device_id: Optional[str] = None) -> Dict:
        """통계 조회"""
        if device_id:
            history = self.detection_history.get(device_id, [])
        else:
            # 모든 디바이스 합산
            history = []
            for h in self.detection_history.values():
                history.extend(h)
        
        if not history:
            return {
                'total_detections': 0,
                'auto_count': 0,
                'pending_count': 0,
                'failure_count': 0,
                'no_input_count': 0
            }
        
        auto_count = sum(1 for h in history if h['status'] == 'auto')
        pending_count = sum(1 for h in history if h['status'] == 'pending')
        failure_count = sum(1 for h in history if h.get('is_failure', False))
        
        return {
            'total_detections': len(history),
            'auto_count': auto_count,
            'pending_count': pending_count,
            'failure_count': failure_count,
            'auto_rate': auto_count / len(history) if history else 0.0,
            'pending_rate': pending_count / len(history) if history else 0.0,
            'failure_rate': failure_count / len(history) if history else 0.0
        }

