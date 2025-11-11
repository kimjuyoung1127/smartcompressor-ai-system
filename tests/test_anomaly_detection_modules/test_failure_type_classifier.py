#!/usr/bin/env python3
"""
FailureTypeClassifier 모듈 단위 테스트
"""

import pytest
import sys
import os

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.anomaly_detection_modules import FailureTypeClassifier


class TestFailureTypeClassifier:
    """FailureTypeClassifier 테스트 클래스"""
    
    def test_init(self):
        """초기화 테스트"""
        classifier = FailureTypeClassifier()
        assert classifier is not None
    
    def test_classify_bearing_wear(self):
        """베어링 마모 분류 테스트"""
        classifier = FailureTypeClassifier()
        features = {'spectral_centroid': 5000.0}
        anomaly_score_result = {
            'individual_scores': {'high_freq_energy': 0.85},
            'total_score': 0.8
        }
        
        result = classifier.classify(features, anomaly_score_result)
        assert result == 'bearing_wear'
    
    def test_classify_refrigerant_leak(self):
        """냉매 누출 분류 테스트"""
        classifier = FailureTypeClassifier()
        features = {'spectral_centroid': 800.0}
        anomaly_score_result = {
            'individual_scores': {'low_freq_energy': 0.85},
            'total_score': 0.8
        }
        
        result = classifier.classify(features, anomaly_score_result)
        assert result == 'refrigerant_leak'
    
    def test_classify_normal(self):
        """정상 분류 테스트"""
        classifier = FailureTypeClassifier()
        features = {'spectral_centroid': 2000.0}
        anomaly_score_result = {
            'individual_scores': {},
            'total_score': 0.3
        }
        
        result = classifier.classify(features, anomaly_score_result)
        assert result == 'normal'

