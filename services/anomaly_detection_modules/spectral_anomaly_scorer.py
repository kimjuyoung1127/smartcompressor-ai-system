#!/usr/bin/env python3
"""
스펙트럼 이상 점수 계산 모듈 (SpectralAnomalyScorer)

[일반인/개발자를 위한 설명]

이 모듈은 "정상 기준선"과 "현재 소리"를 비교하여 "이상 점수"를 계산합니다.

📊 기준선(Baseline)이란?
- 정상 상태의 압축기 소리를 1-2일 동안 수집하여 만든 "정상 기준"
- 예: 정상 압축기의 RMS 에너지 평균 = 0.1, 표준편차 = 0.02
- 이 기준선과 비교하여 "이상한지" 판단합니다

🎯 이상 점수 계산 방식:
1. 현재 소리의 특징을 추출합니다 (FeatureExtractor에서 받음)
2. 기준선의 평균과 표준편차를 사용합니다
3. Z-score를 계산합니다 (통계학의 표준 점수)
   - Z-score = (현재값 - 평균) / 표준편차
   - 예: Z-score = 3 → 평균에서 3 표준편차만큼 벗어남 (매우 이상!)
4. 각 특징별 이상 점수를 계산합니다 (0-100%)
5. 종합 이상 점수를 계산합니다 (가중 평균)

💡 왜 중요한가?
- 사람이 "이상하다"고 느끼는 것을 숫자로 표현합니다
- 기준선과 비교하여 객관적으로 판단합니다
- 이상 점수가 70% 이상이면 "고장 신호 감지!"

🔧 개발자를 위한 설명:
- 입력: 특징 딕셔너리, 기준선 딕셔너리
- 출력: 이상 점수 결과 (0-1)
- 연산 비용: 낮음 (단순 통계 계산)
- 사용 시점: FeatureExtractor 실행 후
- 알고리즘: Z-score 기반 통계적 이상 탐지
"""

import numpy as np
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class SpectralAnomalyScorer:
    """
    스펙트럼 이상 점수 계산 모듈
    
    [역할]
    "정상 기준선"과 "현재 소리"를 비교하여 "이상 점수"를 계산합니다.
    사람이 "이상하다"고 느끼는 것을 숫자(0-100%)로 표현하는 것이 목적입니다.
    
    [왜 중요한가?]
    - 컴퓨터는 "이상하다"는 것을 직접 느낄 수 없습니다
    - 정상 기준선과 비교하여 객관적으로 판단해야 합니다
    - 이상 점수가 70% 이상이면 "고장 신호 감지!"로 판단합니다
    
    [작동 방식]
    1. 현재 소리의 특징을 받습니다 (FeatureExtractor에서)
    2. 기준선의 평균과 표준편차를 사용합니다
    3. Z-score를 계산합니다 (통계학의 표준 점수)
       - Z-score = (현재값 - 평균) / 표준편차
       - 예: Z-score = 3 → 평균에서 3 표준편차만큼 벗어남 (매우 이상!)
    4. 각 특징별 이상 점수를 계산합니다 (0-100%)
    5. 종합 이상 점수를 계산합니다 (가중 평균)
    
    [실제 예시]
    기준선: RMS 에너지 평균 = 0.1, 표준편차 = 0.02
    현재 소리: RMS 에너지 = 0.2
    Z-score = (0.2 - 0.1) / 0.02 = 5 (매우 이상!)
    이상 점수 = min(1.0, 5 / 3.0) = 1.0 (100%)
    """
    
    def __init__(self, anomaly_threshold: float = 0.7):
        """
        초기화
        
        Args:
            anomaly_threshold: 이상 점수 임계값 (기본 70%)
                - 이 값 이상이면 "고장 신호 감지!"로 판단
                - 예: 0.7 = 70% 이상이면 고장
        """
        self.anomaly_threshold = anomaly_threshold
        
        logger.info("✅ 스펙트럼 이상 점수 계산 모듈 초기화 완료")
        logger.info(f"   - 이상 점수 임계값: {anomaly_threshold:.0%}")
    
    def calculate(self, features: Dict, baseline: Dict) -> Dict:
        """
        스펙트럼 이상 점수 계산
        
        [작동 방식]
        1. 각 특징별로 Z-score를 계산합니다
        2. Z-score를 이상 점수로 변환합니다 (0-1)
        3. 가중 평균으로 종합 이상 점수를 계산합니다
        4. 신뢰도를 계산합니다
        
        [Z-score 설명]
        - 통계학의 표준 점수
        - Z-score = (현재값 - 평균) / 표준편차
        - 예: Z-score = 0 → 평균과 동일 (정상)
        - 예: Z-score = 3 → 평균에서 3 표준편차만큼 벗어남 (매우 이상!)
        
        [가중치 설명]
        - 스펙트럼 중심: 25% (주파수 패턴 변화 중요)
        - RMS 에너지: 25% (소리 크기 변화 중요)
        - 고주파 에너지: 20% (베어링 마모 등 중요)
        - 저주파 에너지: 15% (냉매 누출 등 중요)
        - ZCR: 15% (마찰음 등 중요)
        
        Args:
            features: 현재 오디오 특징 (FeatureExtractor에서 받음)
            baseline: 기준선 딕셔너리 (BaselineManager에서 받음)
                - 예: {'rms_energy_mean': 0.1, 'rms_energy_std': 0.02, ...}
        
        Returns:
            {
                'total_score': float,  # 종합 이상 점수 (0-1)
                    # 0.0 = 정상, 1.0 = 매우 이상
                'confidence': float,    # 신뢰도 (0-1)
                    # 이상 점수가 높을수록 신뢰도도 높음
                'individual_scores': Dict  # 개별 특징별 이상 점수
                    # 예: {'rms_energy': 0.8, 'spectral_centroid': 0.6, ...}
                'is_anomaly': bool     # 이상 여부 (total_score > threshold)
            }
        
        [실제 예시]
        >>> scorer = SpectralAnomalyScorer()
        >>> features = {'rms_energy': 0.2, 'spectral_centroid': 3000.0, ...}
        >>> baseline = {'rms_energy_mean': 0.1, 'rms_energy_std': 0.02, ...}
        >>> result = scorer.calculate(features, baseline)
        >>> print(result['total_score'])  # 0.85 (85% 이상)
        >>> print(result['is_anomaly'])   # True (고장 신호 감지!)
        """
        if not baseline:
            return {
                'total_score': 0.0,
                'confidence': 0.0,
                'individual_scores': {}
            }
        
        individual_scores = {}
        
        # ===== 스펙트럼 중심 이상 점수 =====
        # 의미: 주파수 패턴이 정상과 얼마나 다른지
        # 예: 정상 = 2000Hz, 현재 = 5000Hz → 매우 이상!
        if 'spectral_centroid_mean' in baseline and 'spectral_centroid_std' in baseline:
            # Z-score 계산: (현재값 - 평균) / 표준편차
            centroid_z_score = abs(
                (features.get('spectral_centroid', 0) - baseline['spectral_centroid_mean'])
                / (baseline['spectral_centroid_std'] + 1e-6)  # 1e-6은 0으로 나누기 방지
            )
            # Z-score를 이상 점수로 변환 (0-1)
            # Z-score = 3이면 이상 점수 = 1.0 (100%)
            individual_scores['spectral_centroid'] = min(1.0, centroid_z_score / 3.0)
        
        # ===== RMS 에너지 이상 점수 =====
        # 의미: 소리 크기가 정상과 얼마나 다른지
        # 예: 정상 = 0.1, 현재 = 0.5 → 매우 시끄러움 (이상!)
        if 'rms_energy_mean' in baseline and 'rms_energy_std' in baseline:
            energy_z_score = abs(
                (features.get('rms_energy', 0) - baseline['rms_energy_mean'])
                / (baseline['rms_energy_std'] + 1e-6)
            )
            individual_scores['rms_energy'] = min(1.0, energy_z_score / 3.0)
        
        # ===== 고주파 에너지 비율 이상 점수 =====
        # 의미: 고주파가 정상보다 얼마나 많은지
        # 예: 베어링 마모 시 고주파 증가
        if 'high_freq_energy_ratio_mean' in baseline and 'high_freq_energy_ratio_std' in baseline:
            high_freq_z_score = abs(
                (features.get('high_freq_energy_ratio', 0) - baseline['high_freq_energy_ratio_mean'])
                / (baseline['high_freq_energy_ratio_std'] + 1e-6)
            )
            individual_scores['high_freq_energy'] = min(1.0, high_freq_z_score / 3.0)
        
        # ===== 저주파 에너지 비율 이상 점수 =====
        # 의미: 저주파가 정상보다 얼마나 많은지
        # 예: 냉매 누출 시 저주파 증가
        if 'low_freq_energy_ratio_mean' in baseline and 'low_freq_energy_ratio_std' in baseline:
            low_freq_z_score = abs(
                (features.get('low_freq_energy_ratio', 0) - baseline['low_freq_energy_ratio_mean'])
                / (baseline['low_freq_energy_ratio_std'] + 1e-6)
            )
            individual_scores['low_freq_energy'] = min(1.0, low_freq_z_score / 3.0)
        
        # ===== Zero Crossing Rate 이상 점수 =====
        # 의미: 소리가 정상보다 얼마나 날카로운지
        # 예: 마찰음 시 ZCR 증가
        if 'zcr_mean' in baseline and 'zcr_std' in baseline:
            zcr_z_score = abs(
                (features.get('zcr', 0) - baseline['zcr_mean'])
                / (baseline['zcr_std'] + 1e-6)
            )
            individual_scores['zcr'] = min(1.0, zcr_z_score / 3.0)
        
        # ===== 종합 이상 점수 계산 (가중 평균) =====
        # 각 특징별 이상 점수를 가중 평균하여 종합 점수 계산
        # 가중치: 스펙트럼 중심 25%, RMS 에너지 25%, 고주파 20%, 저주파 15%, ZCR 15%
        if individual_scores:
            total_score = (
                0.25 * individual_scores.get('spectral_centroid', 0) +  # 주파수 패턴 변화 중요
                0.25 * individual_scores.get('rms_energy', 0) +         # 소리 크기 변화 중요
                0.20 * individual_scores.get('high_freq_energy', 0) +    # 베어링 마모 등 중요
                0.15 * individual_scores.get('low_freq_energy', 0) +     # 냉매 누출 등 중요
                0.15 * individual_scores.get('zcr', 0)                   # 마찰음 등 중요
            )
        else:
            total_score = 0.0
        
        # ===== 신뢰도 계산 =====
        # 이상 점수가 높을수록 신뢰도도 높음
        # 예: 이상 점수 0.7 → 신뢰도 0.84 (84%)
        confidence = min(1.0, total_score * 1.2)
        
        return {
            'total_score': total_score,
            'confidence': confidence,
            'individual_scores': individual_scores,
            'is_anomaly': total_score > self.anomaly_threshold
        }

