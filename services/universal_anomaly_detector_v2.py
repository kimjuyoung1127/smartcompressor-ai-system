#!/usr/bin/env python3
"""
범용 이상 감지 시스템 v2 (모듈화 버전)
모든 압축기에 공통 적용 가능한 실시간 고장 신호 감지 알고리즘

모듈화 구조:
1. DecibelFilter: 데시벨 기반 1차 필터링
2. FeatureExtractor: 오디오 특징 추출
3. SpectralAnomalyScorer: 스펙트럼 이상 점수 계산
4. FailureTypeClassifier: 고장 유형 분류
5. BaselineManager: 기준선 관리

장점:
- 연산 능력 절약 (필요한 모듈만 사용)
- 모듈별 독립 테스트 가능
- 유지보수 및 확장 용이
"""

import numpy as np
import logging
from typing import Dict, Optional, List
from datetime import datetime
from collections import deque

from .anomaly_detection_modules import (
    DecibelFilter,
    FeatureExtractor,
    SpectralAnomalyScorer,
    FailureTypeClassifier,
    BaselineManager
)

logger = logging.getLogger(__name__)


class UniversalAnomalyDetectorV2:
    """
    범용 이상 감지 시스템 v2 (모듈화 버전)
    
    특징:
    - 모든 압축기에 공통 적용 가능
    - 모듈화 구조로 연산 능력 절약
    - 실시간 스펙트럼 이상 점수 계산
    - 데시벨 기반 1차 필터링
    - 범용 고장 패턴 감지
    """
    
    def __init__(self,
                 sample_rate: int = 16000,
                 window_size: float = 5.0,
                 anomaly_threshold: float = 0.7):
        """
        Args:
            sample_rate: 샘플링 레이트
            window_size: 분석 윈도우 크기 (초)
            anomaly_threshold: 이상 점수 임계값
        """
        self.sample_rate = sample_rate
        self.window_size = window_size
        
        # 모듈 초기화
        self.decibel_filter = DecibelFilter()
        self.feature_extractor = FeatureExtractor(
            sample_rate=sample_rate,
            window_size=window_size
        )
        self.anomaly_scorer = SpectralAnomalyScorer(
            anomaly_threshold=anomaly_threshold
        )
        self.failure_classifier = FailureTypeClassifier()
        self.baseline_manager = BaselineManager()
        
        # 히스토리
        self.history = deque(maxlen=1000)
        
        logger.info("✅ 범용 이상 감지 시스템 v2 초기화 완료 (모듈화)")
        logger.info(f"   - 윈도우 크기: {window_size}초")
        logger.info(f"   - 샘플링 레이트: {sample_rate}Hz")
        logger.info(f"   - 이상 점수 임계값: {anomaly_threshold:.0%}")
    
    def establish_baseline(self, audio_samples: List[np.ndarray]) -> Dict:
        """
        정상 상태 기준선 설정
        
        Args:
            audio_samples: 정상 상태 오디오 샘플 리스트 (1-2일 수집)
        
        Returns:
            기준선 딕셔너리
        """
        return self.baseline_manager.establish(audio_samples, self.feature_extractor)
    
    def detect_anomaly(self,
                      audio_data: np.ndarray,
                      decibel_level: Optional[float] = None) -> Dict:
        """
        실시간 이상 감지
        
        Args:
            audio_data: 오디오 데이터
            decibel_level: 데시벨 레벨 (선택적)
        
        Returns:
            이상 감지 결과
        """
        baseline = self.baseline_manager.get_baseline()
        if not baseline:
            return {
                'is_anomaly': False,
                'confidence': 0.0,
                'message': '기준선이 설정되지 않았습니다.',
                'anomaly_type': 'unknown',
                'anomaly_score': 0.0
            }
        
        # 1단계: 데시벨 기반 1차 필터링 (빠른 필터링)
        decibel_result = self.decibel_filter.filter(decibel_level)
        if decibel_result['action'] == 'skip':
            return {
                'is_anomaly': False,
                'confidence': 1.0,
                'message': decibel_result['reason'],
                'anomaly_type': 'no_input',
                'anomaly_score': 0.0,
                'decibel_level': decibel_level
            }
        
        if decibel_result['action'] == 'update_statistics_only':
            return {
                'is_anomaly': False,
                'confidence': 1.0,
                'message': '정상 (낮은 소리)',
                'anomaly_type': 'normal_low',
                'anomaly_score': 0.0,
                'decibel_level': decibel_level
            }
        
        # 2단계: 특징 추출 (필요한 경우만)
        features = self.feature_extractor.extract(audio_data)
        if not features:
            return {
                'is_anomaly': False,
                'confidence': 0.0,
                'message': '특징 추출 실패',
                'anomaly_type': 'unknown',
                'anomaly_score': 0.0
            }
        
        # 3단계: 스펙트럼 이상 점수 계산 (필요한 경우만)
        anomaly_score_result = self.anomaly_scorer.calculate(features, baseline)
        
        # 4단계: 고장 유형 분류 (필요한 경우만)
        failure_type = self.failure_classifier.classify(features, anomaly_score_result)
        
        # 5단계: 히스토리 업데이트
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'features': features,
            'anomaly_score': anomaly_score_result['total_score'],
            'failure_type': failure_type
        })
        
        result = {
            'is_anomaly': anomaly_score_result['is_anomaly'],
            'confidence': anomaly_score_result['confidence'],
            'message': '고장 신호 감지!' if anomaly_score_result['is_anomaly'] else '정상',
            'anomaly_type': failure_type,
            'anomaly_score': anomaly_score_result['total_score'],
            'individual_scores': anomaly_score_result['individual_scores'],
            'features': features,
            'decibel_level': decibel_level,
            'timestamp': datetime.now().isoformat()
        }
        
        return result
    
    def save_baseline(self, filepath: str):
        """기준선 저장"""
        self.baseline_manager.save(filepath)
    
    def load_baseline(self, filepath: str):
        """기준선 로드"""
        self.baseline_manager.load(filepath)

