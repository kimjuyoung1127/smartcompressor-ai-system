#!/usr/bin/env python3
"""
향상된 보류 라벨링 서비스
고급 Active Learning 시스템 통합

[개선 사항]
1. 불확실성 기반 샘플링 강화
2. 다양한 불확실성 측정 방법 지원
3. 적응형 샘플링 전략
4. 효율적인 전문가 시간 활용
"""

import logging
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import json

from services.pending_labeling_service import PendingLabelingService, LabelingStatus
from services.advanced_active_learning import (
    advanced_active_learning,
    UncertaintyMethod,
    SamplingStrategy
)

logger = logging.getLogger(__name__)


class EnhancedPendingLabelingService(PendingLabelingService):
    """
    향상된 보류 라벨링 서비스
    
    [개선 사항]
    - 고급 Active Learning 시스템 통합
    - 불확실성 기반 샘플링 강화
    - 적응형 샘플링 전략
    """
    
    def __init__(self,
                 confidence_threshold: float = 0.7,
                 uncertainty_method: UncertaintyMethod = UncertaintyMethod.ENTROPY,
                 sampling_strategy: SamplingStrategy = SamplingStrategy.ADAPTIVE,
                 db_path: str = "data/pending_labeling.db"):
        """
        초기화
        
        Args:
            confidence_threshold: 신뢰도 임계값
            uncertainty_method: 불확실성 측정 방법
            sampling_strategy: 샘플링 전략
            db_path: 데이터베이스 경로
        """
        super().__init__(confidence_threshold=confidence_threshold, db_path=db_path)
        
        self.uncertainty_method = uncertainty_method
        self.sampling_strategy = sampling_strategy
        
        logger.info("✅ 향상된 보류 라벨링 서비스 초기화 완료")
        logger.info(f"   - 불확실성 방법: {uncertainty_method.value}")
        logger.info(f"   - 샘플링 전략: {sampling_strategy.value}")
    
    def should_pend_labeling(self, detection_result: Dict) -> bool:
        """
        라벨링 보류 여부 판단 (향상된 버전)
        
        [개선 사항]
        - 불확실성 기반 판단 추가
        - 적응형 임계값 적용
        
        Args:
            detection_result: 실시간 판단 결과
        
        Returns:
            bool: 보류 필요 여부
        """
        confidence = detection_result.get('confidence', 0.0)
        
        # 1. 기본 신뢰도 체크
        if confidence < self.confidence_threshold:
            return True
        
        # 2. 불확실성 기반 판단 (예측 확률이 있는 경우)
        prediction_proba = detection_result.get('prediction_proba')
        if prediction_proba is not None:
            # 예측 확률 배열로 변환
            if isinstance(prediction_proba, dict):
                proba_array = np.array(list(prediction_proba.values()))
            elif isinstance(prediction_proba, list):
                proba_array = np.array(prediction_proba)
            else:
                proba_array = np.array(prediction_proba)
            
            # 불확실성 계산
            should_query, uncertainty = advanced_active_learning.should_query(
                prediction_proba=proba_array,
                confidence=confidence
            )
            
            if should_query:
                return True
        
        # 3. 점수 기반 판단 (기존 로직)
        score = detection_result.get('score', 0.0)
        if 0.3 <= score <= 0.7:
            return True
        
        return False
    
    def add_pending_item(self,
                        audio_data: np.ndarray,
                        detection_result: Dict,
                        device_id: str,
                        timestamp: datetime = None,
                        metadata: Dict = None) -> str:
        """
        보류 항목 추가 (향상된 버전)
        
        [개선 사항]
        - 불확실성 점수 기록
        - Active Learning 쿼리 기록
        
        Args:
            audio_data: 오디오 데이터
            detection_result: 실시간 판단 결과
            device_id: 디바이스 ID
            timestamp: 타임스탬프
            metadata: 추가 메타데이터
        
        Returns:
            str: 보류 항목 ID
        """
        # 기본 보류 항목 추가
        item_id = super().add_pending_item(
            audio_data=audio_data,
            detection_result=detection_result,
            device_id=device_id,
            timestamp=timestamp,
            metadata=metadata
        )
        
        # 불확실성 계산 및 기록
        prediction_proba = detection_result.get('prediction_proba')
        if prediction_proba is not None:
            # 예측 확률 배열로 변환
            if isinstance(prediction_proba, dict):
                proba_array = np.array(list(prediction_proba.values()))
            elif isinstance(prediction_proba, list):
                proba_array = np.array(prediction_proba)
            else:
                proba_array = np.array(prediction_proba)
            
            # 불확실성 계산
            uncertainty = advanced_active_learning.calculate_uncertainty(
                prediction_proba=proba_array,
                method=self.uncertainty_method
            )
            
            # Active Learning 쿼리 기록
            advanced_active_learning.record_query(
                sample_id=item_id,
                uncertainty_score=uncertainty,
                confidence=detection_result.get('confidence', 0.0),
                predicted_label=detection_result.get('predicted_class', 'unknown'),
                metadata={
                    'device_id': device_id,
                    'timestamp': timestamp.isoformat() if timestamp else datetime.now().isoformat(),
                    **(metadata or {})
                }
            )
            
            # 보류 항목에 불확실성 점수 추가
            if item_id in self.pending_items:
                self.pending_items[item_id]['uncertainty'] = uncertainty
                self.pending_items[item_id]['uncertainty_method'] = self.uncertainty_method.value
        
        logger.debug(f"향상된 보류 항목 추가: {item_id} (불확실성: {uncertainty if prediction_proba else 'N/A'})")
        
        return item_id
    
    def get_pending_items_by_uncertainty(self,
                                       n_items: int = 10,
                                       min_uncertainty: float = 0.0) -> List[Dict]:
        """
        불확실성 기준으로 보류 항목 조회
        
        Args:
            n_items: 조회할 항목 수
            min_uncertainty: 최소 불확실성
        
        Returns:
            보류 항목 리스트 (불확실성 높은 순)
        """
        # 불확실성이 있는 항목만 필터링
        items_with_uncertainty = [
            item for item in self.pending_items.values()
            if 'uncertainty' in item and item['uncertainty'] >= min_uncertainty
        ]
        
        # 불확실성 기준으로 정렬
        items_with_uncertainty.sort(key=lambda x: x.get('uncertainty', 0.0), reverse=True)
        
        return items_with_uncertainty[:n_items]
    
    def update_label(self,
                    item_id: str,
                    label: str,
                    labeled_by: str,
                    confidence: float = 1.0):
        """
        라벨 업데이트 (향상된 버전)
        
        [개선 사항]
        - Active Learning 라벨 업데이트
        
        Args:
            item_id: 보류 항목 ID
            label: 라벨
            labeled_by: 라벨링 담당자
            confidence: 신뢰도
        """
        # 기본 라벨 업데이트
        super().update_label(item_id, label, labeled_by, confidence)
        
        # Active Learning 라벨 업데이트
        advanced_active_learning.update_label(
            sample_id=item_id,
            ground_truth_label=label,
            labeled_by=labeled_by
        )
        
        logger.debug(f"라벨 업데이트: {item_id} → {label} (by {labeled_by})")
    
    def get_active_learning_statistics(self) -> Dict:
        """
        Active Learning 통계 조회
        
        Returns:
            통계 정보
        """
        return advanced_active_learning.get_statistics()


# 전역 인스턴스
enhanced_pending_labeling_service = EnhancedPendingLabelingService()

