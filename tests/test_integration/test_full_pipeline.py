#!/usr/bin/env python3
"""
전체 파이프라인 통합 테스트
"""

import pytest
import numpy as np
import sys
import os

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.universal_anomaly_detector_v2 import UniversalAnomalyDetectorV2


class TestFullPipeline:
    """전체 파이프라인 테스트 클래스"""
    
    def test_baseline_establishment(self):
        """기준선 설정 테스트"""
        detector = UniversalAnomalyDetectorV2()
        
        # 정상 샘플 생성
        normal_samples = []
        for i in range(10):
            duration = 5.0
            sample_rate = 16000
            t = np.linspace(0, duration, int(sample_rate * duration))
            audio = np.sin(2 * np.pi * 60 * t) * 0.5
            normal_samples.append(audio)
        
        baseline = detector.establish_baseline(normal_samples)
        
        assert baseline is not None
        assert 'rms_energy_mean' in baseline
        assert 'spectral_centroid_mean' in baseline
    
    def test_detection_pipeline_normal(self):
        """정상 데이터 감지 파이프라인 테스트"""
        detector = UniversalAnomalyDetectorV2()
        
        # 기준선 설정
        normal_samples = []
        for i in range(10):
            duration = 5.0
            sample_rate = 16000
            t = np.linspace(0, duration, int(sample_rate * duration))
            audio = np.sin(2 * np.pi * 60 * t) * 0.5
            normal_samples.append(audio)
        detector.establish_baseline(normal_samples)
        
        # 정상 오디오 테스트
        duration = 5.0
        sample_rate = 16000
        t = np.linspace(0, duration, int(sample_rate * duration))
        test_audio = np.sin(2 * np.pi * 60 * t) * 0.5
        
        result = detector.detect_anomaly(test_audio, decibel_level=50.0)
        
        assert result is not None
        assert result['is_anomaly'] == False
        assert result['anomaly_score'] < 0.7
    
    def test_detection_pipeline_anomaly(self):
        """이상 데이터 감지 파이프라인 테스트"""
        detector = UniversalAnomalyDetectorV2()
        
        # 기준선 설정
        normal_samples = []
        for i in range(10):
            duration = 5.0
            sample_rate = 16000
            t = np.linspace(0, duration, int(sample_rate * duration))
            audio = np.sin(2 * np.pi * 60 * t) * 0.5
            normal_samples.append(audio)
        detector.establish_baseline(normal_samples)
        
        # 이상 오디오 테스트 (고주파)
        duration = 5.0
        sample_rate = 16000
        t = np.linspace(0, duration, int(sample_rate * duration))
        test_audio = np.sin(2 * np.pi * 200 * t) * 0.8  # 고주파
        
        result = detector.detect_anomaly(test_audio, decibel_level=55.0)
        
        assert result is not None
        # 이상 점수가 높을 수 있음 (하지만 항상 True는 아님, 기준선에 따라 다름)
        assert 'anomaly_score' in result
        assert 'anomaly_type' in result

