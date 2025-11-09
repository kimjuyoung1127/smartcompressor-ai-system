#!/usr/bin/env python3
"""
성능 최적화 테스트 스크립트

[테스트 내용]
1. 병렬 처리 성능 테스트
2. 캐싱 효과 테스트
3. 배치 처리 성능 테스트
"""

import numpy as np
import time
import sys
import os

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.performance_optimizer import PerformanceOptimizer
from services.anomaly_detection_modules import FeatureExtractor

def generate_test_audio(duration=5.0, sample_rate=16000, frequency=60):
    """테스트용 오디오 데이터 생성"""
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.sin(2 * np.pi * frequency * t) * 0.5
    noise = np.random.normal(0, 0.05, len(audio))
    return audio + noise

def test_parallel_processing():
    """병렬 처리 성능 테스트"""
    print("=" * 60)
    print("1. 병렬 처리 성능 테스트")
    print("=" * 60)
    
    optimizer = PerformanceOptimizer(max_workers=4)
    feature_extractor = FeatureExtractor()
    
    # 테스트 데이터 생성 (4개 센서)
    sensor_data_list = [
        (generate_test_audio(frequency=60 + i * 10), 50.0, f"ESP32_00{i+1}")
        for i in range(4)
    ]
    
    # 순차 처리 시간 측정
    start_time = time.time()
    sequential_results = []
    for audio_data, decibel_level, device_id in sensor_data_list:
        features = feature_extractor.extract(audio_data)
        sequential_results.append(features)
    sequential_time = time.time() - start_time
    
    # 병렬 처리 시간 측정
    def detection_func(audio_data, decibel_level):
        return feature_extractor.extract(audio_data)
    
    start_time = time.time()
    parallel_results = optimizer.process_parallel(sensor_data_list, detection_func)
    parallel_time = time.time() - start_time
    
    print(f"순차 처리 시간: {sequential_time:.3f}초")
    print(f"병렬 처리 시간: {parallel_time:.3f}초")
    print(f"성능 향상: {sequential_time / parallel_time:.2f}배")
    print(f"시간 절약: {(sequential_time - parallel_time):.3f}초 ({(1 - parallel_time/sequential_time)*100:.1f}%)")
    print()

def test_caching():
    """캐싱 효과 테스트"""
    print("=" * 60)
    print("2. 캐싱 효과 테스트")
    print("=" * 60)
    
    optimizer = PerformanceOptimizer(max_workers=4, cache_size=100)
    feature_extractor = FeatureExtractor()
    
    # 동일한 오디오 데이터 생성
    audio_data = generate_test_audio(frequency=60)
    
    # 첫 번째 추출 (캐시 미스)
    start_time = time.time()
    features1 = optimizer.extract_features_cached(audio_data, feature_extractor)
    first_time = time.time() - start_time
    
    # 두 번째 추출 (캐시 히트)
    start_time = time.time()
    features2 = optimizer.extract_features_cached(audio_data, feature_extractor)
    second_time = time.time() - start_time
    
    print(f"첫 번째 추출 (캐시 미스): {first_time:.3f}초")
    print(f"두 번째 추출 (캐시 히트): {second_time:.3f}초")
    print(f"성능 향상: {first_time / second_time:.2f}배")
    print(f"시간 절약: {(first_time - second_time):.3f}초 ({(1 - second_time/first_time)*100:.1f}%)")
    
    # 통계 확인
    stats = optimizer.get_stats()
    print(f"\n캐시 통계:")
    print(f"  - 캐시 히트: {stats['cache_hits']}")
    print(f"  - 캐시 미스: {stats['cache_misses']}")
    print(f"  - 캐시 히트율: {stats['cache_hit_rate']:.1%}")
    print()

def test_batch_processing():
    """배치 처리 성능 테스트"""
    print("=" * 60)
    print("3. 배치 처리 성능 테스트")
    print("=" * 60)
    
    optimizer = PerformanceOptimizer()
    feature_extractor = FeatureExtractor()
    
    # 배치 데이터 생성 (10개 샘플)
    audio_batch = [generate_test_audio(frequency=60 + i * 5) for i in range(10)]
    
    # 배치 처리 시간 측정
    start_time = time.time()
    batch_results = optimizer.process_batch(audio_batch, feature_extractor)
    batch_time = time.time() - start_time
    
    # 순차 처리 시간 측정
    start_time = time.time()
    sequential_results = []
    for audio_data in audio_batch:
        features = feature_extractor.extract(audio_data)
        sequential_results.append(features)
    sequential_time = time.time() - start_time
    
    print(f"순차 처리 시간: {sequential_time:.3f}초")
    print(f"배치 처리 시간: {batch_time:.3f}초")
    print(f"성능 향상: {sequential_time / batch_time:.2f}배")
    print(f"시간 절약: {(sequential_time - batch_time):.3f}초 ({(1 - batch_time/sequential_time)*100:.1f}%)")
    print()

def main():
    """메인 테스트 함수"""
    print("\n" + "=" * 60)
    print("성능 최적화 테스트 시작")
    print("=" * 60 + "\n")
    
    try:
        # 1. 병렬 처리 테스트
        test_parallel_processing()
        
        # 2. 캐싱 테스트
        test_caching()
        
        # 3. 배치 처리 테스트
        test_batch_processing()
        
        print("=" * 60)
        print("✅ 모든 테스트 완료!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 테스트 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

