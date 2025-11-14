#!/usr/bin/env python3
"""
기준선 관리 모듈 (BaselineManager)

[일반인/개발자를 위한 설명]

이 모듈은 "정상 상태의 기준"을 만들고 관리합니다.

📊 기준선(Baseline)이란?
- 정상 상태의 압축기 소리를 1-2일 동안 수집하여 만든 "정상 기준"
- 예: 정상 압축기의 RMS 에너지 평균 = 0.1, 표준편차 = 0.02
- 이 기준선과 비교하여 "이상한지" 판단합니다

🎯 기준선 설정 과정:
1. 정상 상태 오디오 샘플을 수집합니다 (1-2일)
2. 각 샘플에서 특징을 추출합니다
3. 모든 샘플의 특징을 모아서 통계를 계산합니다:
   - 평균 (mean): 대부분의 값이 모여있는 중심
   - 표준편차 (std): 값들이 얼마나 퍼져있는지
4. 기준선을 저장합니다

💡 왜 중요한가?
- 기준선이 없으면 "이상하다"고 판단할 수 없습니다
- 예: RMS 에너지가 0.2인데, 이것이 이상한지 정상인지 알 수 없음
- 기준선이 있으면: 정상 평균 = 0.1, 현재 = 0.2 → 2배 높음 → 이상!

🔧 개발자를 위한 설명:
- 입력: 정상 상태 오디오 샘플 리스트
- 출력: 기준선 딕셔너리 (평균, 표준편차 등)
- 연산 비용: 중간 (초기 1회만)
- 사용 시점: 모니터링 시작 전 (반드시 필요!)
- 저장 형식: JSON 파일
"""

import numpy as np
import json
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)


class BaselineManager:
    """
    기준선 관리 모듈
    
    [역할]
    "정상 상태의 기준"을 만들고 관리합니다.
    이 기준선이 있어야 "이상하다"고 판단할 수 있습니다.
    
    [왜 중요한가?]
    - 기준선이 없으면 "이상하다"고 판단할 수 없습니다
    - 예: RMS 에너지가 0.2인데, 이것이 이상한지 정상인지 알 수 없음
    - 기준선이 있으면: 정상 평균 = 0.1, 현재 = 0.2 → 2배 높음 → 이상!
    
    [작동 방식]
    1. 정상 상태 오디오 샘플을 수집합니다 (1-2일)
    2. 각 샘플에서 특징을 추출합니다 (FeatureExtractor 사용)
    3. 모든 샘플의 특징을 모아서 통계를 계산합니다:
       - 평균 (mean): 대부분의 값이 모여있는 중심
       - 표준편차 (std): 값들이 얼마나 퍼져있는지
    4. 기준선을 저장합니다 (JSON 파일)
    
    [실제 예시]
    정상 샘플 100개 수집:
    - RMS 에너지: [0.08, 0.12, 0.10, 0.11, ...]
    - 평균: 0.1
    - 표준편차: 0.02
    
    기준선:
    {
        'rms_energy_mean': 0.1,
        'rms_energy_std': 0.02,
        ...
    }
    
    이후 현재 소리와 비교:
    - 현재 RMS 에너지 = 0.2
    - Z-score = (0.2 - 0.1) / 0.02 = 5 (매우 이상!)
    """
    
    def __init__(self, baseline_history_size: int = 100):
        """
        초기화
        
        Args:
            baseline_history_size: 기준선 히스토리 크기
                - 최근 N개의 기준선을 저장 (변화 추적용)
        """
        self.baseline = None  # 현재 기준선
        self.baseline_history = deque(maxlen=baseline_history_size)  # 기준선 히스토리
        self.baseline_last_update = None  # 기준선 마지막 업데이트 시간
        
        logger.info("✅ 기준선 관리 모듈 초기화 완료")
    
    def establish(self, audio_samples: List[np.ndarray], feature_extractor) -> Dict:
        """
        기준선 설정
        
        [작동 방식]
        1. 정상 상태 오디오 샘플을 받습니다 (1-2일 수집)
        2. 각 샘플에서 특징을 추출합니다 (FeatureExtractor 사용)
        3. 모든 샘플의 특징을 모아서 통계를 계산합니다:
           - 평균 (mean): 대부분의 값이 모여있는 중심
           - 표준편차 (std): 값들이 얼마나 퍼져있는지
        4. 기준선을 저장합니다
        
        [통계 계산 예시]
        샘플 100개에서 RMS 에너지 추출:
        - 값: [0.08, 0.12, 0.10, 0.11, 0.09, ...]
        - 평균: 0.1 (대부분의 값이 0.1 근처)
        - 표준편차: 0.02 (값들이 0.1 ± 0.02 범위에 있음)
        
        이후 현재 소리와 비교:
        - 현재 RMS 에너지 = 0.2
        - Z-score = (0.2 - 0.1) / 0.02 = 5
        - 이상 점수 = min(1.0, 5 / 3.0) = 1.0 (100% 이상!)
        
        Args:
            audio_samples: 정상 상태 오디오 샘플 리스트
                - 예: [audio1, audio2, ..., audio100]
                - 1-2일 동안 수집한 정상 상태 샘플
            feature_extractor: 특징 추출기 인스턴스
                - FeatureExtractor 클래스의 인스턴스
                - 각 샘플에서 특징을 추출하는 데 사용
        
        Returns:
            기준선 딕셔너리:
            {
                'rms_energy_mean': float,      # RMS 에너지 평균
                'rms_energy_std': float,       # RMS 에너지 표준편차
                'spectral_centroid_mean': float,  # 스펙트럼 중심 평균
                'spectral_centroid_std': float,    # 스펙트럼 중심 표준편차
                ...
                'created_at': str,            # 기준선 생성 시간
                'sample_count': int           # 샘플 개수
            }
        
        [실제 예시]
        >>> manager = BaselineManager()
        >>> normal_samples = [audio1, audio2, ..., audio100]  # 1-2일 수집
        >>> extractor = FeatureExtractor()
        >>> baseline = manager.establish(normal_samples, extractor)
        >>> print(baseline['rms_energy_mean'])  # 0.1
        >>> print(baseline['rms_energy_std'])  # 0.02
        """
        logger.info(f"📊 기준선 설정 시작 ({len(audio_samples)}개 샘플)")
        
        # ===== 1. 각 샘플에서 특징 추출 =====
        # 모든 정상 샘플에서 특징을 추출하여 리스트에 저장
        all_features = []
        for audio in audio_samples:
            features = feature_extractor.extract(audio)
            if features:
                all_features.append(features)
        
        if not all_features:
            logger.warning("⚠️ 특징 추출 실패, 기본 기준선 사용")
            return self._get_default_baseline()
        
        # ===== 2. 통계 계산 =====
        # 모든 샘플의 특징을 모아서 평균과 표준편차를 계산
        # 평균 (mean): 대부분의 값이 모여있는 중심
        # 표준편차 (std): 값들이 얼마나 퍼져있는지
        
        # 스펙트럼 중심 통계
        # 예: [2000, 2100, 1900, 2050, ...] → 평균 = 2000, 표준편차 = 200
        baseline = {
            'spectral_centroid_mean': np.mean([f['spectral_centroid'] for f in all_features]),
            'spectral_centroid_std': np.std([f['spectral_centroid'] for f in all_features]),
            
            # RMS 에너지 통계
            # 예: [0.08, 0.12, 0.10, 0.11, ...] → 평균 = 0.1, 표준편차 = 0.02
            'rms_energy_mean': np.mean([f['rms_energy'] for f in all_features]),
            'rms_energy_std': np.std([f['rms_energy'] for f in all_features]),
            
            # 고주파 에너지 비율 통계
            # 예: [0.14, 0.16, 0.15, 0.15, ...] → 평균 = 0.15, 표준편차 = 0.05
            'high_freq_energy_ratio_mean': np.mean([f['high_freq_energy_ratio'] for f in all_features]),
            'high_freq_energy_ratio_std': np.std([f['high_freq_energy_ratio'] for f in all_features]),
            
            # 저주파 에너지 비율 통계
            # 예: [0.48, 0.52, 0.50, 0.51, ...] → 평균 = 0.5, 표준편차 = 0.1
            'low_freq_energy_ratio_mean': np.mean([f['low_freq_energy_ratio'] for f in all_features]),
            'low_freq_energy_ratio_std': np.std([f['low_freq_energy_ratio'] for f in all_features]),
            
            # Zero Crossing Rate 통계
            # 예: [0.04, 0.06, 0.05, 0.05, ...] → 평균 = 0.05, 표준편차 = 0.02
            'zcr_mean': np.mean([f['zcr'] for f in all_features]),
            'zcr_std': np.std([f['zcr'] for f in all_features]),
            
            # 패턴 안정성 통계
            # 예: [0.85, 0.90, 0.88, 0.87, ...] → 평균 = 0.8, 표준편차 = 0.1
            'pattern_regularity_mean': np.mean([f.get('pattern_regularity', 0.8) for f in all_features]),
            'pattern_regularity_std': np.std([f.get('pattern_regularity', 0.8) for f in all_features]),
            
            # 메타데이터
            'created_at': datetime.now().isoformat(),  # 기준선 생성 시간
            'sample_count': len(all_features)  # 샘플 개수
        }
        
        self.baseline = baseline
        self.baseline_last_update = datetime.now()
        self.baseline_history.append(baseline)
        
        logger.info("✅ 기준선 설정 완료")
        logger.info(f"   - 샘플 수: {len(all_features)}")
        logger.info(f"   - 스펙트럼 중심: {baseline['spectral_centroid_mean']:.2f} ± {baseline['spectral_centroid_std']:.2f}")
        logger.info(f"   - RMS 에너지: {baseline['rms_energy_mean']:.4f} ± {baseline['rms_energy_std']:.4f}")
        
        return baseline
    
    def get_baseline(self) -> Optional[Dict]:
        """
        현재 기준선 반환
        
        [용도]
        - SpectralAnomalyScorer에서 기준선을 가져올 때 사용
        - 기준선이 없으면 이상 점수를 계산할 수 없음
        
        Returns:
            기준선 딕셔너리 또는 None (기준선이 설정되지 않은 경우)
        """
        return self.baseline
    
    def save(self, filepath: str):
        """
        기준선 저장
        
        [용도]
        - 기준선을 JSON 파일로 저장하여 나중에 다시 사용
        - 서버 재시작 후에도 기준선을 유지
        
        [저장 형식]
        - JSON 파일
        - 예: data/baselines/ESP32_001_baseline.json
        
        Args:
            filepath: 저장할 파일 경로
                - 예: "data/baselines/ESP32_001_baseline.json"
        """
        if self.baseline:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(self.baseline, f, indent=2)
            logger.info(f"✅ 기준선 저장 완료: {filepath}")
    
    def load(self, filepath: str):
        """
        기준선 로드
        
        [용도]
        - 저장된 기준선을 파일에서 읽어옴
        - 서버 재시작 후 기준선을 복원
        
        Args:
            filepath: 로드할 파일 경로
                - 예: "data/baselines/ESP32_001_baseline.json"
        """
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                self.baseline = json.load(f)
            self.baseline_last_update = datetime.fromisoformat(
                self.baseline.get('created_at', datetime.now().isoformat())
            )
            logger.info(f"✅ 기준선 로드 완료: {filepath}")
        else:
            logger.warning(f"⚠️ 기준선 파일 없음: {filepath}")
    
    def _get_default_baseline(self) -> Dict:
        """기본 기준선 (임시)"""
        return {
            'spectral_centroid_mean': 2000.0,
            'spectral_centroid_std': 200.0,
            'rms_energy_mean': 0.1,
            'rms_energy_std': 0.02,
            'high_freq_energy_ratio_mean': 0.15,
            'high_freq_energy_ratio_std': 0.05,
            'low_freq_energy_ratio_mean': 0.5,
            'low_freq_energy_ratio_std': 0.1,
            'zcr_mean': 0.05,
            'zcr_std': 0.02,
            'pattern_regularity_mean': 0.8,
            'pattern_regularity_std': 0.1,
            'created_at': datetime.now().isoformat(),
            'sample_count': 0
        }

