#!/usr/bin/env python3
"""
데시벨 기반 1차 필터링 모듈 (DecibelFilter)

[일반인/개발자를 위한 설명]

이 모듈은 "소리의 크기"만 보고 빠르게 판단하는 문지기 역할을 합니다.

🔊 데시벨(dB)이란?
- 소리의 크기를 나타내는 단위입니다
- 예: 조용한 도서관 30dB, 대화 60dB, 비행기 120dB
- 우리는 압축기 소리를 측정합니다

🎯 이 모듈이 하는 일:
1. 소리가 너무 작으면 (35-40dB) → "소리 없음" 판단 → 아무것도 안 함 (연산 절약!)
2. 소리가 조금 있지만 작으면 (40-48dB) → "정상 (낮은 소리)" 판단 → 통계만 기록
3. 소리가 충분히 크면 (48dB 이상) → "분석 필요" 판단 → 다음 단계로 진행

💡 왜 중요한가?
- 비유: 도서관에 들어가기 전에 문지기가 "너무 조용하면 들어올 필요 없어요"라고 미리 알려주는 것
- 효과: 불필요한 복잡한 계산을 99% 줄일 수 있습니다
- 예시: 하루 576개 샘플 중 50%는 소리 없음 → 이 모듈이 막아서 288개는 계산 안 함!

🔧 개발자를 위한 설명:
- 이 모듈은 가장 먼저 실행되어야 합니다 (가장 빠르고 가벼움)
- 단순 비교 연산만 하므로 CPU 부담이 거의 없습니다
- 이 모듈에서 걸러지면 FeatureExtractor, SpectralAnomalyScorer 등 무거운 모듈은 실행되지 않습니다
- 연산 시간: 0.001초 (매우 빠름)
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class DecibelFilter:
    """
    데시벨 기반 1차 필터링 모듈
    
    [역할]
    소리의 크기(데시벨)만 보고 빠르게 판단하는 "문지기" 역할
    
    [왜 중요한가?]
    - 불필요한 연산을 99% 줄일 수 있습니다
    - 소리 없음/정상 데이터는 복잡한 분석이 필요 없습니다
    - 이 모듈에서 걸러지면 FeatureExtractor 등 무거운 모듈은 실행되지 않습니다
    
    [작동 방식]
    1. 데시벨 레벨을 받습니다
    2. 임계값과 비교합니다 (단순 비교, 매우 빠름)
    3. 결과를 반환합니다:
       - skip: 소리 없음 → 아무것도 안 함
       - update_statistics_only: 정상 (낮은 소리) → 통계만 기록
       - needs_analysis: 분석 필요 → 다음 모듈로 진행
    
    [실제 예시]
    - 35dB: 소리 없음 → skip (연산 절약!)
    - 45dB: 정상 (낮은 소리) → 통계만 기록 (연산 절약!)
    - 50dB: 분석 필요 → FeatureExtractor 실행
    """
    
    def __init__(self,
                 no_input_threshold: float = 40.0,
                 normal_low_threshold: float = 48.0):
        """
        초기화
        
        Args:
            no_input_threshold: 소리 없음 임계값 (35-40dB)
                - 이 값보다 작으면 소리가 없다고 판단
                - 예: 35dB = 조용한 도서관 수준
            normal_low_threshold: 정상 (낮은 소리) 임계값 (40-48dB)
                - 이 값보다 작으면 정상이지만 낮은 소리로 판단
                - 예: 45dB = 조용한 사무실 수준
        """
        self.no_input_threshold = no_input_threshold
        self.normal_low_threshold = normal_low_threshold
        
        logger.info("✅ 데시벨 필터 모듈 초기화 완료")
        logger.info(f"   - 소리 없음 임계값: {no_input_threshold}dB")
        logger.info(f"   - 정상 (낮은 소리) 임계값: {normal_low_threshold}dB")
    
    def filter(self, decibel_level: Optional[float]) -> Dict:
        """
        데시벨 기반 1차 필터링
        
        [작동 방식]
        1. 데시벨 레벨을 받습니다
        2. 임계값과 비교합니다 (단순 if문, 매우 빠름)
        3. 결과를 반환합니다
        
        [반환값]
        - action: 'skip' | 'update_statistics_only' | 'needs_analysis'
          - skip: 소리 없음 → 아무것도 안 함 (연산 절약!)
          - update_statistics_only: 정상 (낮은 소리) → 통계만 기록 (연산 절약!)
          - needs_analysis: 분석 필요 → 다음 모듈로 진행
        
        Args:
            decibel_level: 데시벨 레벨 (예: 35.0, 45.0, 50.0)
        
        Returns:
            {
                'action': 'skip' | 'update_statistics_only' | 'needs_analysis',
                'reason': str,  # 이유 설명
                'decibel_level': float  # 입력받은 데시벨 레벨
            }
        
        [실제 예시]
        >>> filter = DecibelFilter()
        >>> filter.filter(35.0)
        {'action': 'skip', 'reason': 'no_input', 'decibel_level': 35.0}
        >>> filter.filter(45.0)
        {'action': 'update_statistics_only', 'reason': 'normal_low', 'decibel_level': 45.0}
        >>> filter.filter(50.0)
        {'action': 'needs_analysis', 'reason': 'decibel_above_threshold', 'decibel_level': 50.0}
        """
        # 데시벨 레벨이 없으면 분석 필요로 판단
        if decibel_level is None:
            return {
                'action': 'needs_analysis',
                'reason': 'decibel_not_provided',
                'decibel_level': None
            }
        
        # 소리 없음 판단 (35-40dB)
        # 예: 조용한 도서관 수준 → 아무것도 안 함 (연산 절약!)
        if decibel_level < self.no_input_threshold:
            return {
                'action': 'skip',
                'reason': 'no_input',
                'decibel_level': decibel_level
            }
        
        # 정상 (낮은 소리) 판단 (40-48dB)
        # 예: 조용한 사무실 수준 → 통계만 기록 (연산 절약!)
        if decibel_level < self.normal_low_threshold:
            return {
                'action': 'update_statistics_only',
                'reason': 'normal_low',
                'decibel_level': decibel_level
            }
        
        # 분석 필요 (48dB 이상)
        # 예: 압축기 작동 소리 → 다음 모듈로 진행
        return {
            'action': 'needs_analysis',
            'reason': 'decibel_above_threshold',
            'decibel_level': decibel_level
        }

