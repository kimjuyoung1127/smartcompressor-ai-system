#!/usr/bin/env python3
"""
FeatureExtractor 모듈 단위 테스트
"""

import pytest
import numpy as np
import sys
import os

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.anomaly_detection_modules import FeatureExtractor


class TestFeatureExtractor:
    """FeatureExtractor 테스트 클래스"""
    
    def test_init(self):
        """초기화 테스트"""
        extractor = FeatureExtractor()
        assert extractor.sample_rate == 16000
        assert extractor.window_size == 5.0
    
    def test_extract_features(self):
        """특징 추출 테스트"""
        extractor = FeatureExtractor()
        
        # 테스트 오디오 데이터 생성 (5초, 60Hz 사인파)
        duration = 5.0
        sample_rate = 16000
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = np.sin(2 * np.pi * 60 * t) * 0.5
        
        features = extractor.extract(audio_data)
        
        assert features is not None
        assert 'rms_energy' in features
        assert 'spectral_centroid' in features
        assert 'zcr' in features
        assert 'high_freq_energy_ratio' in features
        assert 'low_freq_energy_ratio' in features
        assert 'pattern_regularity' in features
    
    def test_extract_features_empty(self):
        """빈 오디오 데이터 테스트"""
        extractor = FeatureExtractor()
        audio_data = np.array([])
        
        features = extractor.extract(audio_data)
        
        # 빈 데이터는 None을 반환하거나 기본값을 반환할 수 있음
        # 실제 구현에 따라 조정 필요
        assert features is None or isinstance(features, dict)
    
    def test_extract_features_short(self):
        """짧은 오디오 데이터 테스트 (패딩)"""
        extractor = FeatureExtractor()
        
        # 1초 분량의 오디오 (5초가 아님)
        sample_rate = 16000
        audio_data = np.sin(2 * np.pi * 60 * np.linspace(0, 1, sample_rate)) * 0.5
        
        features = extractor.extract(audio_data)
        
        assert features is not None
        assert 'rms_energy' in features

