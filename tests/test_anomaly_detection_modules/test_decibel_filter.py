#!/usr/bin/env python3
"""
DecibelFilter 모듈 단위 테스트
"""

import pytest
import sys
import os

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.anomaly_detection_modules import DecibelFilter


class TestDecibelFilter:
    """DecibelFilter 테스트 클래스"""
    
    def test_init(self):
        """초기화 테스트"""
        filter = DecibelFilter()
        assert filter.no_input_threshold == 40.0
        assert filter.normal_low_threshold == 48.0
    
    def test_filter_no_input(self):
        """소리 없음 테스트"""
        filter = DecibelFilter()
        result = filter.filter(35.0)
        
        assert result['action'] == 'skip'
        assert result['reason'] == 'no_input'
        assert result['decibel_level'] == 35.0
    
    def test_filter_normal_low(self):
        """정상 (낮은 소리) 테스트"""
        filter = DecibelFilter()
        result = filter.filter(45.0)
        
        assert result['action'] == 'update_statistics_only'
        assert result['reason'] == 'normal_low'
        assert result['decibel_level'] == 45.0
    
    def test_filter_needs_analysis(self):
        """분석 필요 테스트"""
        filter = DecibelFilter()
        result = filter.filter(50.0)
        
        assert result['action'] == 'needs_analysis'
        assert result['reason'] == 'decibel_above_threshold'
        assert result['decibel_level'] == 50.0
    
    def test_filter_none(self):
        """데시벨 레벨이 None인 경우"""
        filter = DecibelFilter()
        result = filter.filter(None)
        
        assert result['action'] == 'needs_analysis'
        assert result['reason'] == 'decibel_not_provided'
        assert result['decibel_level'] is None
    
    def test_custom_thresholds(self):
        """커스텀 임계값 테스트"""
        filter = DecibelFilter(no_input_threshold=35.0, normal_low_threshold=45.0)
        
        result1 = filter.filter(30.0)
        assert result1['action'] == 'skip'
        
        result2 = filter.filter(40.0)
        assert result2['action'] == 'update_statistics_only'
        
        result3 = filter.filter(50.0)
        assert result3['action'] == 'needs_analysis'

