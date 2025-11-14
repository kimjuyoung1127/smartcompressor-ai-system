#!/usr/bin/env python3
"""
고장 유형 분류 모듈 (FailureTypeClassifier)

[일반인/개발자를 위한 설명]

이 모듈은 "어떤 종류의 고장인지"를 판단합니다.

🔍 고장 유형이란?
- 단순히 "이상하다"고만 알려주는 것이 아니라
- "베어링 마모", "냉매 누출", "증발기 성에" 등 구체적인 고장 유형을 알려줍니다
- 각 고장 유형마다 다른 소리 패턴이 있습니다

🎯 고장 유형별 특징:

1. 베어링 마모 (bearing_wear)
   - 특징: 고주파 에너지 증가
   - 비유: 기계 부품이 마모되면 "삐걱삐걱" 소리 (고주파)
   - 예: 고주파 에너지 비율이 정상보다 70% 이상 높음

2. 파열음 (burst_sound)
   - 특징: RMS 에너지 급증
   - 비유: 폭발 소리처럼 갑자기 매우 시끄러움
   - 예: RMS 에너지가 정상보다 80% 이상 높음

3. 냉매 누출 (refrigerant_leak)
   - 특징: 저주파 에너지 증가 + 스펙트럼 중심 낮음
   - 비유: 압력이 떨어지면서 "우르르" 소리 (저주파)
   - 예: 저주파 에너지 비율이 정상보다 70% 이상 높고, 주파수 중심이 1000Hz 미만

4. 증발기 성에 (evaporator_frost)
   - 특징: 연속 작동 패턴 (RMS 에너지 지속적 높음 + 패턴 안정성 감소)
   - 비유: 시원해지지 않아서 압축기가 계속 돌음 (정상은 주기적으로 on/off)
   - 예: RMS 에너지가 정상보다 60% 이상 높고, 패턴 안정성이 70% 미만

5. 언밸런스 (unbalance)
   - 특징: 스펙트럼 중심 변화
   - 비유: 회전체가 불균형하면 주파수 패턴이 변함
   - 예: 스펙트럼 중심이 정상보다 70% 이상 다름

6. 마찰음 (friction)
   - 특징: Zero Crossing Rate 증가
   - 비유: 부품이 서로 마찰하며 "긁는" 소리
   - 예: ZCR이 정상보다 70% 이상 높음

💡 왜 중요한가?
- 고장 유형을 알면 정비 방법이 달라집니다
- 예: 베어링 마모 → 베어링 교체, 냉매 누출 → 누출 지점 찾기
- 사용자가 "무엇을 해야 하는지" 알 수 있습니다

🔧 개발자를 위한 설명:
- 입력: 특징 딕셔너리, 이상 점수 결과
- 출력: 고장 유형 문자열
- 연산 비용: 매우 낮음 (단순 조건문)
- 사용 시점: 이상 점수 계산 후
- 알고리즘: 규칙 기반 분류 (if-else)
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class FailureTypeClassifier:
    """
    고장 유형 분류 모듈
    
    [역할]
    이상 점수와 특징을 기반으로 "어떤 종류의 고장인지"를 판단합니다.
    단순히 "이상하다"고만 알려주는 것이 아니라 구체적인 고장 유형을 알려줍니다.
    
    [왜 중요한가?]
    - 고장 유형을 알면 정비 방법이 달라집니다
    - 예: 베어링 마모 → 베어링 교체, 냉매 누출 → 누출 지점 찾기
    - 사용자가 "무엇을 해야 하는지" 알 수 있습니다
    
    [작동 방식]
    1. 이상 점수 결과를 받습니다 (SpectralAnomalyScorer에서)
    2. 특징 딕셔너리를 받습니다 (FeatureExtractor에서)
    3. 각 고장 유형별 특징을 확인합니다 (if-else)
    4. 가장 일치하는 고장 유형을 반환합니다
    
    [고장 유형별 판단 기준]
    - 베어링 마모: 고주파 에너지 증가 (70% 이상)
    - 파열음: RMS 에너지 급증 (80% 이상)
    - 냉매 누출: 저주파 에너지 증가 (70% 이상) + 주파수 중심 낮음 (<1000Hz)
    - 증발기 성에: RMS 에너지 지속적 높음 (60% 이상) + 패턴 안정성 감소 (<70%)
    - 언밸런스: 스펙트럼 중심 변화 (70% 이상)
    - 마찰음: ZCR 증가 (70% 이상)
    """
    
    def __init__(self):
        logger.info("✅ 고장 유형 분류 모듈 초기화 완료")
    
    def classify(self, features: Dict, anomaly_score_result: Dict) -> str:
        """
        고장 유형 분류
        
        [작동 방식]
        1. 개별 특징별 이상 점수를 확인합니다
        2. 각 고장 유형별 특징을 확인합니다 (우선순위 순)
        3. 가장 일치하는 고장 유형을 반환합니다
        
        [우선순위]
        1. 베어링 마모 (고주파 에너지 증가)
        2. 파열음 (RMS 에너지 급증)
        3. 냉매 누출 (저주파 에너지 증가 + 주파수 중심 낮음)
        4. 증발기 성에 (RMS 에너지 지속적 높음 + 패턴 안정성 감소)
        5. 언밸런스 (스펙트럼 중심 변화)
        6. 마찰음 (ZCR 증가)
        7. 일반적인 이상 (이상 점수만 높음)
        8. 정상
        
        Args:
            features: 오디오 특징 (FeatureExtractor에서 받음)
                - 예: {'rms_energy': 0.2, 'spectral_centroid': 3000.0, ...}
            anomaly_score_result: 이상 점수 결과 (SpectralAnomalyScorer에서 받음)
                - 예: {'total_score': 0.85, 'individual_scores': {...}, ...}
        
        Returns:
            고장 유형 문자열:
            - 'bearing_wear': 베어링 마모
            - 'burst_sound': 파열음
            - 'refrigerant_leak': 냉매 누출
            - 'evaporator_frost': 증발기 성에
            - 'unbalance': 언밸런스
            - 'friction': 마찰음
            - 'general_anomaly': 일반적인 이상
            - 'normal': 정상
        
        [실제 예시]
        >>> classifier = FailureTypeClassifier()
        >>> features = {'high_freq_energy_ratio': 0.8, 'spectral_centroid': 5000.0, ...}
        >>> score_result = {'individual_scores': {'high_freq_energy': 0.85}, ...}
        >>> failure_type = classifier.classify(features, score_result)
        >>> print(failure_type)  # 'bearing_wear' (베어링 마모)
        """
        individual_scores = anomaly_score_result.get('individual_scores', {})
        total_score = anomaly_score_result.get('total_score', 0.0)
        
        # ===== 1. 베어링 마모 (Bearing Wear) =====
        # 특징: 고주파 에너지 증가
        # 비유: 기계 부품이 마모되면 "삐걱삐걱" 소리 (고주파)
        # 판단: 고주파 에너지 이상 점수 > 70%
        if individual_scores.get('high_freq_energy', 0) > 0.7:
            return 'bearing_wear'
        
        # ===== 2. 파열음 (Burst Sound) =====
        # 특징: RMS 에너지 급증
        # 비유: 폭발 소리처럼 갑자기 매우 시끄러움
        # 판단: RMS 에너지 이상 점수 > 80%
        if individual_scores.get('rms_energy', 0) > 0.8:
            return 'burst_sound'
        
        # ===== 3. 냉매 누출 (Refrigerant Leak) =====
        # 특징: 저주파 에너지 증가 + 스펙트럼 중심 낮음
        # 비유: 압력이 떨어지면서 "우르르" 소리 (저주파)
        # 판단: 저주파 에너지 이상 점수 > 70% AND 주파수 중심 < 1000Hz
        if (individual_scores.get('low_freq_energy', 0) > 0.7 and
            features.get('spectral_centroid', 0) < 1000):
            return 'refrigerant_leak'
        
        # ===== 4. 증발기 성에 (Evaporator Frost) =====
        # 특징: 연속 작동 패턴 (RMS 에너지 지속적 높음 + 패턴 안정성 감소)
        # 비유: 시원해지지 않아서 압축기가 계속 돌음 (정상은 주기적으로 on/off)
        # 판단: RMS 에너지 이상 점수 > 60% AND 패턴 안정성 < 70%
        if (individual_scores.get('rms_energy', 0) > 0.6 and
            features.get('pattern_regularity', 1.0) < 0.7):
            return 'evaporator_frost'
        
        # ===== 5. 언밸런스 (Unbalance) =====
        # 특징: 스펙트럼 중심 변화
        # 비유: 회전체가 불균형하면 주파수 패턴이 변함
        # 판단: 스펙트럼 중심 이상 점수 > 70%
        if individual_scores.get('spectral_centroid', 0) > 0.7:
            return 'unbalance'
        
        # ===== 6. 마찰음 (Friction) =====
        # 특징: Zero Crossing Rate 증가
        # 비유: 부품이 서로 마찰하며 "긁는" 소리
        # 판단: ZCR 이상 점수 > 70%
        if individual_scores.get('zcr', 0) > 0.7:
            return 'friction'
        
        # ===== 7. 일반적인 이상 (General Anomaly) =====
        # 특징: 이상 점수는 높지만 특정 패턴이 명확하지 않음
        # 판단: 종합 이상 점수 > 70%
        if total_score > 0.7:
            return 'general_anomaly'
        
        # ===== 8. 정상 (Normal) =====
        return 'normal'

