#!/usr/bin/env python3
"""
SpectralAnomalyScorer 모듈 단위 테스트
"""

import pytest
import sys
import os

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.anomaly_detection_modules import SpectralAnomalyScorer


class TestSpectralAnomalyScorer:
    """SpectralAnomalyScorer 테스트 클래스"""
    
    def test_init(self):
        """초기화 테스트"""
        scorer = SpectralAnomalyScorer()
        assert scorer.anomaly_threshold == 0.7
    
    def test_calculate_no_baseline(self):
        """기준선이 없는 경우 테스트"""
        scorer = SpectralAnomalyScorer()
        features = {'rms_energy': 0.1, 'spectral_centroid': 2000.0}
        baseline = {}
        
        result = scorer.calculate(features, baseline)
        
        assert result['total_score'] == 0.0
        assert result['confidence'] == 0.0
    
    def test_calculate_normal(self):
        """정상 데이터 테스트"""
        scorer = SpectralAnomalyScorer()
        features = {
            'rms_energy': 0.1,
            'spectral_centroid': 2000.0,
            'high_freq_energy_ratio': 0.15,
            'low_freq_energy_ratio': 0.5,
            'zcr': 0.05
        }
        baseline = {
            'rms_energy_mean': 0.1,
            'rms_energy_std': 0.02,
            'spectral_centroid_mean': 2000.0,
            'spectral_centroid_std': 200.0,
            'high_freq_energy_ratio_mean': 0.15,
            'high_freq_energy_ratio_std': 0.05,
            'low_freq_energy_ratio_mean': 0.5,
            'low_freq_energy_ratio_std': 0.1,
            'zcr_mean': 0.05,
            'zcr_std': 0.02
        }
        
        result = scorer.calculate(features, baseline)
        
        assert result['total_score'] < 0.3  # 정상은 낮은 점수
        assert result['is_anomaly'] == False
    
    def test_calculate_anomaly(self):
        """이상 데이터 테스트"""
        scorer = SpectralAnomalyScorer()
        features = {
            'rms_energy': 0.5,  # 정상보다 5배 높음
            'spectral_centroid': 5000.0,  # 정상보다 2.5배 높음
            'high_freq_energy_ratio': 0.5,  # 정상보다 3배 높음
            'low_freq_energy_ratio': 0.2,
            'zcr': 0.2
        }
        baseline = {
            'rms_energy_mean': 0.1,
            'rms_energy_std': 0.02,
            'spectral_centroid_mean': 2000.0,
            'spectral_centroid_std': 200.0,
            'high_freq_energy_ratio_mean': 0.15,
            'high_freq_energy_ratio_std': 0.05,
            'low_freq_energy_ratio_mean': 0.5,
            'low_freq_energy_ratio_std': 0.1,
            'zcr_mean': 0.05,
            'zcr_std': 0.02
        }
        
        result = scorer.calculate(features, baseline)
        
        assert result['total_score'] > 0.7  # 이상은 높은 점수
        assert result['is_anomaly'] == True

