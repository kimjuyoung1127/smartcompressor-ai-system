#!/usr/bin/env python3
"""
실시간 고장 판단 API 라우트
ESP32에서 들어오는 오디오를 실시간으로 분석하여 고장/비고장 판단
"""

from flask import Blueprint, request, jsonify
import logging
import numpy as np
from services.realtime_failure_detection_service import RealtimeFailureDetectionService

logger = logging.getLogger(__name__)

# 실시간 판단 서비스 인스턴스
realtime_detector = RealtimeFailureDetectionService(
    sample_rate=16000,
    window_size=2.0,
    use_pretrained_model=True  # YAMNet 사용
)

# 라우트 블루프린트
realtime_bp = Blueprint('realtime_detection', __name__, url_prefix='/api/realtime')

@realtime_bp.route('/detect', methods=['POST'])
def detect_failure():
    """
    실시간 고장 판단 API
    
    Request Body:
    {
        "audio_data": [0.1, 0.2, ...],  # 오디오 샘플 배열
        "device_id": "ESP32_001",  # 선택적
        "sample_rate": 16000  # 선택적 (기본값: 16000)
    }
    
    Response:
    {
        "is_failure": true/false,
        "confidence": 0.85,
        "score": 0.75,
        "should_alert": true/false,
        "processing_time_ms": 15.2,
        "details": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body가 필요합니다.'
            }), 400
        
        audio_data = data.get('audio_data')
        device_id = data.get('device_id', 'unknown')
        sample_rate = data.get('sample_rate', 16000)
        
        if audio_data is None:
            return jsonify({
                'success': False,
                'error': 'audio_data가 필요합니다.'
            }), 400
        
        # numpy array 변환
        audio_array = np.array(audio_data, dtype=np.float32)
        
        # 샘플링 레이트 조정 (필요시)
        if sample_rate != 16000:
            import librosa
            audio_array = librosa.resample(audio_array, orig_sr=sample_rate, target_sr=16000)
        
        # 고장 판단
        result = realtime_detector.process_audio(audio_array, device_id=device_id)
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"실시간 고장 판단 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@realtime_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """
    통계 정보 조회 API
    
    Query Parameters:
    - device_id: 디바이스 ID (선택적)
    - hours: 조회 기간 (시간, 기본값: 24)
    
    Response:
    {
        "total_samples": 1000,
        "failure_count": 50,
        "failure_rate": 0.05,
        "avg_confidence": 0.82
    }
    """
    try:
        device_id = request.args.get('device_id', None)
        hours = int(request.args.get('hours', 24))
        
        stats = realtime_detector.get_statistics(device_id=device_id, hours=hours)
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        logger.error(f"통계 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@realtime_bp.route('/health', methods=['GET'])
def health_check():
    """헬스 체크"""
    return jsonify({
        'status': 'healthy',
        'service': 'realtime_failure_detection',
        'pretrained_model': realtime_detector.detector.use_pretrained_model
    })

