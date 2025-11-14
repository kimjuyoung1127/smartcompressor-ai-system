#!/usr/bin/env python3
"""
ESP32 통합 이상 감지 라우트
모듈화된 이상 감지 시스템과 ESP32 데이터를 통합
"""

from flask import Blueprint, request, jsonify
import logging
import time
from datetime import datetime

from services.esp32_integrated_detection_service import esp32_integrated_service

logger = logging.getLogger(__name__)

esp32_integrated_bp = Blueprint('esp32_integrated', __name__, url_prefix='/api/esp32/integrated')


@esp32_integrated_bp.route('/detect', methods=['POST'])
def detect_anomaly():
    """
    ESP32 오디오 데이터를 받아서 모듈화된 이상 감지 시스템으로 처리
    
    [요청 형식]
    - Headers:
        - X-Device-ID: 디바이스 ID (필수)
        - X-Sample-Rate: 샘플링 레이트 (선택, 기본 16000)
        - X-Decibel-Level: 데시벨 레벨 (선택, 자동 계산)
    - Body: 오디오 바이트 데이터 (raw binary)
    
    [응답 형식]
    {
        "success": true,
        "device_id": "ESP32_001",
        "timestamp": "2024-01-01T12:00:00",
        "detection_result": {
            "is_anomaly": false,
            "confidence": 0.95,
            "anomaly_score": 0.15,
            "anomaly_type": "normal",
            "message": "정상"
        },
        "data_quality": {
            "is_valid": true,
            "issues": [],
            "metrics": {
                "length": 80000,
                "max_amplitude": 5000,
                "rms_level": 1500
            }
        },
        "processing_time_ms": 45.2
    }
    """
    try:
        # 헤더에서 디바이스 정보 추출
        device_id = request.headers.get('X-Device-ID')
        if not device_id:
            return jsonify({
                'success': False,
                'message': 'X-Device-ID 헤더가 필요합니다.'
            }), 400
        
        sample_rate = request.headers.get('X-Sample-Rate')
        if sample_rate:
            try:
                sample_rate = int(sample_rate)
            except ValueError:
                sample_rate = None
        else:
            sample_rate = None
        
        decibel_level = request.headers.get('X-Decibel-Level')
        if decibel_level:
            try:
                decibel_level = float(decibel_level)
            except ValueError:
                decibel_level = None
        else:
            decibel_level = None
        
        # 오디오 데이터 수신
        audio_data = request.data
        
        if not audio_data:
            return jsonify({
                'success': False,
                'message': '오디오 데이터가 없습니다.'
            }), 400
        
        # 통합 서비스로 처리
        result = esp32_integrated_service.process_esp32_audio(
            audio_data=audio_data,
            device_id=device_id,
            sample_rate=sample_rate,
            decibel_level=decibel_level
        )
        
        # HTTP 상태 코드 결정
        status_code = 200 if result['success'] else 400
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"ESP32 통합 이상 감지 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'처리 오류: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@esp32_integrated_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """
    통계 정보 조회
    
    [응답 형식]
    {
        "total_processed": 1000,
        "anomalies_detected": 50,
        "quality_issues": 10,
        "anomaly_rate": 0.05,
        "avg_processing_time_ms": 45.2,
        "quality_issue_rate": 0.01
    }
    """
    try:
        stats = esp32_integrated_service.get_statistics()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"통계 조회 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'통계 조회 오류: {str(e)}'
        }), 500


@esp32_integrated_bp.route('/health', methods=['GET'])
def health_check():
    """
    서비스 상태 확인
    """
    try:
        stats = esp32_integrated_service.get_statistics()
        return jsonify({
            'status': 'healthy',
            'service': 'ESP32 Integrated Detection Service',
            'statistics': stats,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"헬스 체크 오류: {e}")
        return jsonify({
            'status': 'unhealthy',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

