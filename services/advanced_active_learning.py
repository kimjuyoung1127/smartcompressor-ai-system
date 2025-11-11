#!/usr/bin/env python3
"""
고급 Active Learning 시스템
불확실성 기반 샘플링 강화

[주요 기능]
1. 다양한 불확실성 측정 방법
   - 엔트로피 기반 불확실성
   - 최대 확률 기반 불확실성
   - 마진 기반 불확실성
   - 베이지안 불확실성 (앙상블 기반)

2. 샘플링 전략
   - 불확실성 기반 샘플링 (Uncertainty Sampling)
   - 다양성 기반 샘플링 (Diversity Sampling)
   - 밸런싱 샘플링 (Balanced Sampling)
   - 적응형 샘플링 (Adaptive Sampling)

3. 효율성 최적화
   - 배치 샘플링 (Batch Sampling)
   - 우선순위 큐 기반 샘플링
   - 예산 제약 하에서 샘플링
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Callable
from datetime import datetime
from collections import deque
from enum import Enum
import sqlite3
import json

logger = logging.getLogger(__name__)


class UncertaintyMethod(Enum):
    """불확실성 측정 방법"""
    ENTROPY = "entropy"  # 엔트로피 기반
    MAX_PROBABILITY = "max_probability"  # 최대 확률 기반
    MARGIN = "margin"  # 마진 기반
    ENSEMBLE_VARIANCE = "ensemble_variance"  # 앙상블 분산 기반


class SamplingStrategy(Enum):
    """샘플링 전략"""
    UNCERTAINTY = "uncertainty"  # 불확실성 기반
    DIVERSITY = "diversity"  # 다양성 기반
    BALANCED = "balanced"  # 밸런싱
    ADAPTIVE = "adaptive"  # 적응형


class AdvancedActiveLearning:
    """
    고급 Active Learning 시스템
    
    [역할]
    - 불확실성 기반 샘플링 강화
    - 다양한 샘플링 전략 제공
    - 효율적인 전문가 시간 활용
    """
    
    def __init__(self,
                 uncertainty_method: UncertaintyMethod = UncertaintyMethod.ENTROPY,
                 sampling_strategy: SamplingStrategy = SamplingStrategy.ADAPTIVE,
                 confidence_threshold: float = 0.7,
                 db_path: str = "data/active_learning.db"):
        """
        초기화
        
        Args:
            uncertainty_method: 불확실성 측정 방법
            sampling_strategy: 샘플링 전략
            confidence_threshold: 신뢰도 임계값
            db_path: 데이터베이스 경로
        """
        self.uncertainty_method = uncertainty_method
        self.sampling_strategy = sampling_strategy
        self.confidence_threshold = confidence_threshold
        self.db_path = db_path
        
        # 샘플 히스토리
        self.sample_history = deque(maxlen=10000)
        
        # 통계
        self.stats = {
            'total_queries': 0,
            'uncertainty_queries': 0,
            'diversity_queries': 0,
            'balanced_queries': 0,
            'adaptive_queries': 0
        }
        
        self._init_database()
        
        logger.info("✅ 고급 Active Learning 시스템 초기화 완료")
        logger.info(f"   - 불확실성 방법: {uncertainty_method.value}")
        logger.info(f"   - 샘플링 전략: {sampling_strategy.value}")
        logger.info(f"   - 신뢰도 임계값: {confidence_threshold:.2%}")
    
    def _init_database(self):
        """데이터베이스 초기화"""
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 쿼리 기록 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS query_history (
                    query_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sample_id TEXT NOT NULL,
                    uncertainty_score REAL NOT NULL,
                    uncertainty_method TEXT NOT NULL,
                    sampling_strategy TEXT NOT NULL,
                    confidence REAL,
                    predicted_label TEXT,
                    queried_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    labeled_at DATETIME,
                    ground_truth_label TEXT,
                    labeled_by TEXT
                )
            ''')
            
            # 인덱스 생성
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_query_history_sample ON query_history(sample_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_query_history_uncertainty ON query_history(uncertainty_score)')
            
            conn.commit()
    
    def calculate_uncertainty(self,
                             prediction_proba: np.ndarray,
                             method: Optional[UncertaintyMethod] = None) -> float:
        """
        불확실성 계산
        
        Args:
            prediction_proba: 예측 확률 배열 (shape: [n_classes])
            method: 불확실성 측정 방법 (None이면 기본값 사용)
        
        Returns:
            불확실성 점수 (0-1, 높을수록 불확실)
        """
        if method is None:
            method = self.uncertainty_method
        
        if method == UncertaintyMethod.ENTROPY:
            # 엔트로피 기반 불확실성
            # H(p) = -Σ p_i * log(p_i)
            entropy = -np.sum(prediction_proba * np.log(prediction_proba + 1e-10))
            # 정규화 (최대 엔트로피 = log(n_classes))
            max_entropy = np.log(len(prediction_proba))
            uncertainty = entropy / max_entropy if max_entropy > 0 else 0.0
        
        elif method == UncertaintyMethod.MAX_PROBABILITY:
            # 최대 확률 기반 불확실성
            # 1 - max(p_i)
            uncertainty = 1.0 - np.max(prediction_proba)
        
        elif method == UncertaintyMethod.MARGIN:
            # 마진 기반 불확실성
            # 1 - (max(p_i) - second_max(p_i))
            sorted_proba = np.sort(prediction_proba)[::-1]
            if len(sorted_proba) >= 2:
                margin = sorted_proba[0] - sorted_proba[1]
                uncertainty = 1.0 - margin
            else:
                uncertainty = 1.0
        
        elif method == UncertaintyMethod.ENSEMBLE_VARIANCE:
            # 앙상블 분산 기반 불확실성 (앙상블 모델이 있는 경우)
            # 현재는 단일 모델이므로 최대 확률 기반으로 대체
            uncertainty = 1.0 - np.max(prediction_proba)
        
        else:
            uncertainty = 1.0 - np.max(prediction_proba)
        
        return float(np.clip(uncertainty, 0.0, 1.0))
    
    def should_query(self,
                    prediction_proba: np.ndarray,
                    confidence: float,
                    sample_id: Optional[str] = None) -> Tuple[bool, float]:
        """
        쿼리 필요 여부 판단
        
        Args:
            prediction_proba: 예측 확률 배열
            confidence: 신뢰도
            sample_id: 샘플 ID (선택)
        
        Returns:
            (should_query, uncertainty_score)
        """
        # 불확실성 계산
        uncertainty = self.calculate_uncertainty(prediction_proba)
        
        # 적응형 샘플링 전략
        if self.sampling_strategy == SamplingStrategy.ADAPTIVE:
            # 신뢰도와 불확실성을 모두 고려
            should_query = (
                confidence < self.confidence_threshold or
                uncertainty > (1.0 - self.confidence_threshold)
            )
        
        elif self.sampling_strategy == SamplingStrategy.UNCERTAINTY:
            # 불확실성만 고려
            should_query = uncertainty > (1.0 - self.confidence_threshold)
        
        elif self.sampling_strategy == SamplingStrategy.DIVERSITY:
            # 다양성 고려 (현재는 불확실성 기반)
            should_query = uncertainty > 0.5
        
        elif self.sampling_strategy == SamplingStrategy.BALANCED:
            # 밸런싱 (신뢰도와 불확실성 균형)
            combined_score = (uncertainty + (1.0 - confidence)) / 2.0
            should_query = combined_score > 0.5
        
        else:
            should_query = confidence < self.confidence_threshold
        
        return should_query, uncertainty
    
    def select_samples_for_labeling(self,
                                   samples: List[Dict],
                                   n_samples: int = 10,
                                   strategy: Optional[SamplingStrategy] = None) -> List[Dict]:
        """
        라벨링을 위한 샘플 선택
        
        Args:
            samples: 샘플 리스트 (각 샘플은 prediction_proba, confidence 등을 포함)
            n_samples: 선택할 샘플 수
            strategy: 샘플링 전략 (None이면 기본값 사용)
        
        Returns:
            선택된 샘플 리스트
        """
        if strategy is None:
            strategy = self.sampling_strategy
        
        # 각 샘플의 불확실성 계산
        sample_scores = []
        for sample in samples:
            prediction_proba = sample.get('prediction_proba')
            confidence = sample.get('confidence', 0.0)
            
            if prediction_proba is not None:
                uncertainty = self.calculate_uncertainty(prediction_proba)
                sample['uncertainty'] = uncertainty
                
                # 샘플링 전략에 따른 점수 계산
                if strategy == SamplingStrategy.UNCERTAINTY:
                    score = uncertainty
                elif strategy == SamplingStrategy.BALANCED:
                    score = (uncertainty + (1.0 - confidence)) / 2.0
                elif strategy == SamplingStrategy.ADAPTIVE:
                    # 적응형: 불확실성과 신뢰도를 모두 고려
                    score = uncertainty * (1.0 - confidence)
                else:
                    score = uncertainty
                
                sample_scores.append((score, sample))
        
        # 점수 기준으로 정렬 (높은 점수부터)
        sample_scores.sort(key=lambda x: x[0], reverse=True)
        
        # 상위 N개 선택
        selected = [sample for _, sample in sample_scores[:n_samples]]
        
        # 통계 업데이트
        self.stats['total_queries'] += len(selected)
        if strategy == SamplingStrategy.UNCERTAINTY:
            self.stats['uncertainty_queries'] += len(selected)
        elif strategy == SamplingStrategy.DIVERSITY:
            self.stats['diversity_queries'] += len(selected)
        elif strategy == SamplingStrategy.BALANCED:
            self.stats['balanced_queries'] += len(selected)
        elif strategy == SamplingStrategy.ADAPTIVE:
            self.stats['adaptive_queries'] += len(selected)
        
        logger.info(f"📋 {len(selected)}개 샘플 선택 (전략: {strategy.value})")
        
        return selected
    
    def record_query(self,
                    sample_id: str,
                    uncertainty_score: float,
                    confidence: float,
                    predicted_label: str,
                    metadata: Optional[Dict] = None):
        """
        쿼리 기록
        
        Args:
            sample_id: 샘플 ID
            uncertainty_score: 불확실성 점수
            confidence: 신뢰도
            predicted_label: 예측 라벨
            metadata: 추가 메타데이터
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO query_history
                (sample_id, uncertainty_score, uncertainty_method, sampling_strategy,
                 confidence, predicted_label, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                sample_id,
                uncertainty_score,
                self.uncertainty_method.value,
                self.sampling_strategy.value,
                confidence,
                predicted_label,
                json.dumps(metadata or {})
            ))
            conn.commit()
        
        # 히스토리 업데이트
        self.sample_history.append({
            'sample_id': sample_id,
            'uncertainty': uncertainty_score,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        })
    
    def update_label(self,
                    sample_id: str,
                    ground_truth_label: str,
                    labeled_by: str):
        """
        라벨 업데이트
        
        Args:
            sample_id: 샘플 ID
            ground_truth_label: 실제 라벨
            labeled_by: 라벨링 담당자
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE query_history
                SET ground_truth_label = ?,
                    labeled_by = ?,
                    labeled_at = CURRENT_TIMESTAMP
                WHERE sample_id = ? AND labeled_at IS NULL
            ''', (ground_truth_label, labeled_by, sample_id))
            conn.commit()
    
    def get_statistics(self) -> Dict:
        """
        통계 조회
        
        Returns:
            통계 정보
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 총 쿼리 수
            cursor.execute('SELECT COUNT(*) FROM query_history')
            total_queries = cursor.fetchone()[0]
            
            # 라벨링 완료 수
            cursor.execute('SELECT COUNT(*) FROM query_history WHERE labeled_at IS NOT NULL')
            labeled_count = cursor.fetchone()[0]
            
            # 평균 불확실성
            cursor.execute('SELECT AVG(uncertainty_score) FROM query_history')
            avg_uncertainty = cursor.fetchone()[0] or 0.0
            
            # 라벨링 완료율
            labeling_rate = labeled_count / total_queries if total_queries > 0 else 0.0
        
        return {
            'total_queries': total_queries,
            'labeled_count': labeled_count,
            'unlabeled_count': total_queries - labeled_count,
            'labeling_rate': float(labeling_rate),
            'avg_uncertainty': float(avg_uncertainty),
            'uncertainty_queries': self.stats['uncertainty_queries'],
            'diversity_queries': self.stats['diversity_queries'],
            'balanced_queries': self.stats['balanced_queries'],
            'adaptive_queries': self.stats['adaptive_queries']
        }


# 전역 인스턴스
advanced_active_learning = AdvancedActiveLearning()

