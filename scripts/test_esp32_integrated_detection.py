#!/usr/bin/env python3
"""
ESP32 통합 이상 감지 시스템 테스트
실제 ESP32 데이터 시뮬레이션 및 테스트
"""

import numpy as np
import requests
import time
import json
from typing import Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 테스트 서버 URL (로컬 개발 환경)
BASE_URL = "http://localhost:5000/api/esp32/integrated"


def generate_test_audio(duration: float = 5.0,
                       sample_rate: int = 16000,
                       audio_type: str = "normal") -> bytes:
    """
    테스트 오디오 데이터 생성
    
    Args:
        duration: 오디오 길이 (초)
        sample_rate: 샘플링 레이트
        audio_type: 오디오 타입 ("normal", "anomaly", "no_input")
    
    Returns:
        오디오 바이트 데이터
    """
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    if audio_type == "normal":
        # 정상 압축기 소리 (60Hz 기본 주파수)
        audio = np.sin(2 * np.pi * 60 * t) * 0.3
        audio += np.sin(2 * np.pi * 120 * t) * 0.1  # 하모닉
        noise = np.random.normal(0, 0.05, len(audio))
        audio = audio + noise
    
    elif audio_type == "anomaly":
        # 이상 소리 (고주파 + 불규칙 패턴)
        audio = np.sin(2 * np.pi * 200 * t) * 0.5  # 고주파
        audio += np.sin(2 * np.pi * 400 * t) * 0.3
        # 불규칙 패턴 추가
        irregular = np.random.random(len(audio)) * 0.2
        audio = audio + irregular
        noise = np.random.normal(0, 0.1, len(audio))
        audio = audio + noise
    
    elif audio_type == "no_input":
        # 소리 없음 (노이즈만)
        audio = np.random.normal(0, 0.01, len(audio))
    
    else:
        raise ValueError(f"알 수 없는 오디오 타입: {audio_type}")
    
    # 정규화 및 int16 변환
    audio = np.clip(audio, -1.0, 1.0)
    audio_int16 = (audio * 32768.0).astype(np.int16)
    
    return audio_int16.tobytes()


def calculate_decibel_level(audio_bytes: bytes) -> float:
    """
    데시벨 레벨 계산
    """
    audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
    rms = np.sqrt(np.mean(audio_array.astype(np.float32) ** 2))
    
    if rms > 0:
        db = 20 * np.log10(rms / 32768.0) + 96
    else:
        db = 0.0
    
    return float(db)


def test_detection(audio_type: str, device_id: str = "ESP32_TEST_001") -> Dict:
    """
    이상 감지 테스트
    
    Args:
        audio_type: 오디오 타입 ("normal", "anomaly", "no_input")
        device_id: 디바이스 ID
    
    Returns:
        테스트 결과
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"테스트: {audio_type} 오디오 감지")
    logger.info(f"{'='*60}")
    
    # 테스트 오디오 생성
    audio_bytes = generate_test_audio(audio_type=audio_type)
    decibel_level = calculate_decibel_level(audio_bytes)
    
    logger.info(f"오디오 생성 완료:")
    logger.info(f"  - 길이: {len(audio_bytes)} bytes")
    logger.info(f"  - 데시벨 레벨: {decibel_level:.2f} dB")
    
    # API 호출
    headers = {
        'X-Device-ID': device_id,
        'X-Sample-Rate': '16000',
        'X-Decibel-Level': str(decibel_level)
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/detect",
            data=audio_bytes,
            headers=headers,
            timeout=10
        )
        elapsed_time = (time.time() - start_time) * 1000
        
        logger.info(f"\n응답 시간: {elapsed_time:.2f} ms")
        logger.info(f"HTTP 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            logger.info(f"\n✅ 처리 성공:")
            logger.info(f"  - 디바이스 ID: {result.get('device_id')}")
            logger.info(f"  - 타임스탬프: {result.get('timestamp')}")
            
            detection = result.get('detection_result', {})
            logger.info(f"\n📊 이상 감지 결과:")
            logger.info(f"  - 이상 여부: {detection.get('is_anomaly', False)}")
            logger.info(f"  - 신뢰도: {detection.get('confidence', 0):.2%}")
            logger.info(f"  - 이상 점수: {detection.get('anomaly_score', 0):.2%}")
            logger.info(f"  - 고장 유형: {detection.get('anomaly_type', 'unknown')}")
            logger.info(f"  - 메시지: {detection.get('message', 'N/A')}")
            
            quality = result.get('data_quality', {})
            logger.info(f"\n🔍 데이터 품질:")
            logger.info(f"  - 유효성: {quality.get('is_valid', False)}")
            if quality.get('issues'):
                logger.warning(f"  - 문제점: {', '.join(quality['issues'])}")
            else:
                logger.info(f"  - 문제점: 없음")
            
            metrics = quality.get('metrics', {})
            logger.info(f"  - 데이터 길이: {metrics.get('length', 0)}")
            logger.info(f"  - 최대 진폭: {metrics.get('max_amplitude', 0)}")
            logger.info(f"  - RMS 레벨: {metrics.get('rms_level', 0):.2f}")
            
            logger.info(f"\n⏱️  처리 시간: {result.get('processing_time_ms', 0):.2f} ms")
            
            return {
                'success': True,
                'result': result,
                'elapsed_time_ms': elapsed_time
            }
        else:
            logger.error(f"❌ 처리 실패: {response.status_code}")
            logger.error(f"응답: {response.text}")
            return {
                'success': False,
                'status_code': response.status_code,
                'response': response.text
            }
    
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ 요청 오류: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def test_statistics():
    """
    통계 정보 조회 테스트
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"통계 정보 조회 테스트")
    logger.info(f"{'='*60}")
    
    try:
        response = requests.get(f"{BASE_URL}/statistics", timeout=5)
        
        if response.status_code == 200:
            stats = response.json()
            logger.info(f"\n📊 통계 정보:")
            logger.info(f"  - 총 처리: {stats.get('total_processed', 0)}개")
            logger.info(f"  - 이상 감지: {stats.get('anomalies_detected', 0)}개")
            logger.info(f"  - 품질 문제: {stats.get('quality_issues', 0)}개")
            logger.info(f"  - 이상 비율: {stats.get('anomaly_rate', 0):.2%}")
            logger.info(f"  - 평균 처리 시간: {stats.get('avg_processing_time_ms', 0):.2f} ms")
            logger.info(f"  - 품질 문제 비율: {stats.get('quality_issue_rate', 0):.2%}")
            return stats
        else:
            logger.error(f"❌ 통계 조회 실패: {response.status_code}")
            return None
    
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ 요청 오류: {e}")
        return None


def test_health_check():
    """
    헬스 체크 테스트
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"헬스 체크 테스트")
    logger.info(f"{'='*60}")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        
        if response.status_code == 200:
            health = response.json()
            logger.info(f"\n💚 서비스 상태: {health.get('status', 'unknown')}")
            logger.info(f"  - 서비스: {health.get('service', 'N/A')}")
            logger.info(f"  - 타임스탬프: {health.get('timestamp', 'N/A')}")
            return health
        else:
            logger.error(f"❌ 헬스 체크 실패: {response.status_code}")
            return None
    
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ 요청 오류: {e}")
        return None


def main():
    """
    메인 테스트 함수
    """
    logger.info("🚀 ESP32 통합 이상 감지 시스템 테스트 시작")
    logger.info(f"서버 URL: {BASE_URL}")
    
    # 1. 헬스 체크
    test_health_check()
    
    # 2. 정상 오디오 테스트
    test_detection("normal", "ESP32_TEST_001")
    time.sleep(1)
    
    # 3. 이상 오디오 테스트
    test_detection("anomaly", "ESP32_TEST_001")
    time.sleep(1)
    
    # 4. 소리 없음 테스트
    test_detection("no_input", "ESP32_TEST_001")
    time.sleep(1)
    
    # 5. 통계 조회
    test_statistics()
    
    logger.info(f"\n{'='*60}")
    logger.info("✅ 테스트 완료")
    logger.info(f"{'='*60}")


if __name__ == "__main__":
    main()

