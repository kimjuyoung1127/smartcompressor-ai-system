#!/usr/bin/env python3
"""
ESP32 통합 이상 감지 서비스
ESP32 데이터를 받아서 모듈화된 이상 감지 시스템으로 처리

[기능]
1. ESP32 오디오 데이터 수신 및 전처리
2. 모듈화된 이상 감지 시스템으로 처리
3. 데이터 품질 검증
4. 결과 저장 및 알림
"""

import numpy as np
import logging
import time
from typing import Dict, Optional, List
from datetime import datetime
import librosa

from services.universal_anomaly_detector_v2 import UniversalAnomalyDetectorV2
from services.anomaly_detection_modules.decibel_filter import DecibelFilter

logger = logging.getLogger(__name__)


class ESP32IntegratedDetectionService:
    """
    ESP32 통합 이상 감지 서비스
    
    [역할]
    - ESP32에서 수신한 오디오 데이터를 모듈화된 이상 감지 시스템으로 처리
    - 데이터 품질 검증
    - 결과 저장 및 알림
    """
    
    def __init__(self,
                 sample_rate: int = 16000,
                 window_size: float = 5.0,
                 anomaly_threshold: float = 0.7):
        """
        초기화
        
        Args:
            sample_rate: 샘플링 레이트 (기본 16000Hz)
            window_size: 분석 윈도우 크기 (초)
            anomaly_threshold: 이상 점수 임계값
        """
        self.sample_rate = sample_rate
        self.window_size = window_size
        
        # 모듈화된 이상 감지 시스템 초기화
        self.detector = UniversalAnomalyDetectorV2(
            sample_rate=sample_rate,
            window_size=window_size,
            anomaly_threshold=anomaly_threshold
        )
        
        # 데시벨 필터 (데시벨 레벨 계산용)
        self.decibel_filter = DecibelFilter()
        
        # 통계
        self.stats = {
            'total_processed': 0,
            'anomalies_detected': 0,
            'quality_issues': 0,
            'processing_times': []
        }
        
        logger.info("✅ ESP32 통합 이상 감지 서비스 초기화 완료")
    
    def process_esp32_audio(self,
                           audio_data: bytes,
                           device_id: str,
                           sample_rate: Optional[int] = None,
                           decibel_level: Optional[float] = None) -> Dict:
        """
        ESP32 오디오 데이터 처리
        
        [작동 방식]
        1. 바이트 데이터를 numpy 배열로 변환
        2. 데이터 품질 검증
        3. 샘플링 레이트 조정 (필요시)
        4. 데시벨 레벨 계산 (제공되지 않은 경우)
        5. 모듈화된 이상 감지 시스템으로 처리
        6. 결과 반환
        
        Args:
            audio_data: ESP32에서 수신한 오디오 바이트 데이터
            device_id: 디바이스 ID
            sample_rate: 샘플링 레이트 (None이면 기본값 사용)
            decibel_level: 데시벨 레벨 (None이면 자동 계산)
        
        Returns:
            {
                'success': bool,
                'device_id': str,
                'timestamp': str,
                'detection_result': Dict,  # 이상 감지 결과
                'data_quality': Dict,      # 데이터 품질 정보
                'processing_time_ms': float,
                'message': str
            }
        """
        start_time = time.time()
        
        try:
            # 1. 바이트 데이터를 numpy 배열로 변환
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            if len(audio_array) == 0:
                return {
                    'success': False,
                    'device_id': device_id,
                    'timestamp': datetime.now().isoformat(),
                    'message': '오디오 데이터가 비어있습니다.',
                    'data_quality': {'status': 'empty'}
                }
            
            # 2. 데이터 품질 검증
            quality_result = self._validate_data_quality(audio_array)
            if not quality_result['is_valid']:
                self.stats['quality_issues'] += 1
                logger.warning(f"데이터 품질 문제: {quality_result['issues']}")
                return {
                    'success': False,
                    'device_id': device_id,
                    'timestamp': datetime.now().isoformat(),
                    'message': f"데이터 품질 문제: {', '.join(quality_result['issues'])}",
                    'data_quality': quality_result
                }
            
            # 3. 샘플링 레이트 조정 (필요시)
            actual_sample_rate = sample_rate or self.sample_rate
            if actual_sample_rate != self.sample_rate:
                audio_array = librosa.resample(
                    audio_array.astype(np.float32) / 32768.0,
                    orig_sr=actual_sample_rate,
                    target_sr=self.sample_rate
                )
                audio_array = (audio_array * 32768.0).astype(np.int16)
            
            # 4. 데시벨 레벨 계산 (제공되지 않은 경우)
            if decibel_level is None:
                decibel_level = self._calculate_decibel_level(audio_array)
            
            # 5. 모듈화된 이상 감지 시스템으로 처리
            detection_result = self.detector.detect_anomaly(
                audio_data=audio_array.astype(np.float32) / 32768.0,
                decibel_level=decibel_level
            )
            
            # 6. 통계 업데이트
            processing_time = (time.time() - start_time) * 1000  # ms
            self.stats['total_processed'] += 1
            self.stats['processing_times'].append(processing_time)
            if len(self.stats['processing_times']) > 1000:
                self.stats['processing_times'] = self.stats['processing_times'][-1000:]
            
            if detection_result.get('is_anomaly', False):
                self.stats['anomalies_detected'] += 1
            
            # 7. 결과 반환
            return {
                'success': True,
                'device_id': device_id,
                'timestamp': datetime.now().isoformat(),
                'detection_result': detection_result,
                'data_quality': quality_result,
                'processing_time_ms': processing_time,
                'message': '처리 완료'
            }
            
        except Exception as e:
            logger.error(f"ESP32 오디오 처리 오류: {e}")
            return {
                'success': False,
                'device_id': device_id,
                'timestamp': datetime.now().isoformat(),
                'message': f'처리 오류: {str(e)}',
                'data_quality': {'status': 'error'}
            }
    
    def _validate_data_quality(self, audio_array: np.ndarray) -> Dict:
        """
        데이터 품질 검증
        
        [검증 항목]
        1. 데이터 길이 (너무 짧거나 길지 않은지)
        2. 신호 레벨 (너무 작거나 큰지)
        3. 클리핑 (신호가 잘렸는지)
        4. 무음 구간 (모두 0인지)
        
        Args:
            audio_array: 오디오 배열
        
        Returns:
            {
                'is_valid': bool,
                'issues': List[str],
                'metrics': Dict
            }
        """
        issues = []
        metrics = {}
        
        # 1. 데이터 길이 검증
        expected_length = int(self.sample_rate * self.window_size)
        actual_length = len(audio_array)
        
        if actual_length < expected_length * 0.5:
            issues.append(f'데이터 길이 부족 (예상: {expected_length}, 실제: {actual_length})')
        elif actual_length > expected_length * 2:
            issues.append(f'데이터 길이 초과 (예상: {expected_length}, 실제: {actual_length})')
        
        metrics['length'] = actual_length
        metrics['expected_length'] = expected_length
        
        # 2. 신호 레벨 검증
        max_amplitude = np.max(np.abs(audio_array))
        rms_level = np.sqrt(np.mean(audio_array.astype(np.float32) ** 2))
        
        if max_amplitude < 100:  # 너무 작은 신호
            issues.append(f'신호 레벨 너무 낮음 (max: {max_amplitude})')
        elif max_amplitude > 30000:  # 너무 큰 신호 (클리핑 가능성)
            issues.append(f'신호 레벨 너무 높음 (max: {max_amplitude}, 클리핑 가능성)')
        
        metrics['max_amplitude'] = int(max_amplitude)
        metrics['rms_level'] = float(rms_level)
        
        # 3. 클리핑 검증
        clipping_ratio = np.sum(np.abs(audio_array) > 30000) / len(audio_array)
        if clipping_ratio > 0.01:  # 1% 이상 클리핑
            issues.append(f'클리핑 감지 (비율: {clipping_ratio:.2%})')
        
        metrics['clipping_ratio'] = float(clipping_ratio)
        
        # 4. 무음 구간 검증
        silence_ratio = np.sum(audio_array == 0) / len(audio_array)
        if silence_ratio > 0.9:  # 90% 이상 무음
            issues.append(f'무음 구간 과다 (비율: {silence_ratio:.2%})')
        
        metrics['silence_ratio'] = float(silence_ratio)
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'metrics': metrics
        }
    
    def _calculate_decibel_level(self, audio_array: np.ndarray) -> float:
        """
        데시벨 레벨 계산
        
        Args:
            audio_array: 오디오 배열
        
        Returns:
            데시벨 레벨
        """
        # RMS 계산
        rms = np.sqrt(np.mean(audio_array.astype(np.float32) ** 2))
        
        # 데시벨 변환 (참조 레벨: 32768 = 최대값)
        if rms > 0:
            db = 20 * np.log10(rms / 32768.0)
            # 음수 값을 양수로 변환 (일반적인 데시벨 스케일)
            db = db + 96  # 96dB 오프셋 (일반적인 마이크 레벨)
        else:
            db = 0.0
        
        return float(db)
    
    def get_statistics(self) -> Dict:
        """
        통계 정보 반환
        
        Returns:
            통계 딕셔너리
        """
        processing_times = self.stats['processing_times']
        avg_processing_time = np.mean(processing_times) if processing_times else 0
        
        return {
            'total_processed': self.stats['total_processed'],
            'anomalies_detected': self.stats['anomalies_detected'],
            'quality_issues': self.stats['quality_issues'],
            'anomaly_rate': (
                self.stats['anomalies_detected'] / self.stats['total_processed']
                if self.stats['total_processed'] > 0 else 0
            ),
            'avg_processing_time_ms': float(avg_processing_time),
            'quality_issue_rate': (
                self.stats['quality_issues'] / self.stats['total_processed']
                if self.stats['total_processed'] > 0 else 0
            )
        }
    
    def establish_baseline(self, audio_samples: List[np.ndarray]) -> Dict:
        """
        기준선 설정 (위임)
        
        Args:
            audio_samples: 정상 상태 오디오 샘플 리스트
        
        Returns:
            기준선 딕셔너리
        """
        return self.detector.establish_baseline(audio_samples)


# 전역 인스턴스
esp32_integrated_service = ESP32IntegratedDetectionService()

