#!/usr/bin/env python3
"""
ESP32 실시간 판단 API 라우트
"""

from flask import Blueprint, request, jsonify
import logging
import numpy as np
from datetime import datetime
from services.esp32_realtime_detector import ESP32RealtimeDetector

logger = logging.getLogger(__name__)

# 전역 ESP32 실시간 판단 서비스
esp32_detector = ESP32RealtimeDetector(
    no_input_threshold=(35, 40),
    detection_start_threshold=48.0,
    confidence_threshold=0.7
)

# 라우트 블루프린트
esp32_realtime_bp = Blueprint('esp32_realtime', __name__, url_prefix='/api/esp32/realtime')

@esp32_realtime_bp.route('/detect', methods=['POST'])
def detect():
    """
    ESP32 실시간 판단 API
    
    Request Body:
    {
        "audio_data": [0.1, 0.2, ...],  # 오디오 샘플 배열
        "decibel_level": 55.0,  # 데시벨 레벨
        "device_id": "ESP32_001",
        "sample_rate": 16000,  # 선택적
        "metadata": {...}  # 선택적
    }
    
    Response:
    {
        "success": true,
        "status": "no_input" | "processing" | "auto" | "pending",
        "decibel_level": 55.0,
        "result": {...},  # 판단 결과
        "message": "..."
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
        decibel_level = data.get('decibel_level')
        device_id = data.get('device_id', 'unknown')
        sample_rate = data.get('sample_rate', 16000)
        metadata = data.get('metadata')
        
        if audio_data is None:
            return jsonify({
                'success': False,
                'error': 'audio_data가 필요합니다.'
            }), 400
        
        if decibel_level is None:
            return jsonify({
                'success': False,
                'error': 'decibel_level이 필요합니다.'
            }), 400
        
        # numpy array 변환
        audio_array = np.array(audio_data, dtype=np.float32)
        
        # 샘플링 레이트 조정 (필요시)
        if sample_rate != 16000:
            import librosa
            audio_array = librosa.resample(audio_array, orig_sr=sample_rate, target_sr=16000)
        
        # ESP32 데이터 처리
        result = esp32_detector.process_esp32_data(
            audio_data=audio_array,
            decibel_level=float(decibel_level),
            device_id=device_id,
            timestamp=datetime.now(),
            metadata=metadata
        )
        
        return jsonify({
            'success': True,
            **result
        })
        
    except Exception as e:
        logger.error(f"ESP32 실시간 판단 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@esp32_realtime_bp.route('/status/<device_id>', methods=['GET'])
def get_device_status(device_id: str):
    """디바이스 상태 조회"""
    try:
        status = esp32_detector.get_device_status(device_id)
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        logger.error(f"디바이스 상태 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@esp32_realtime_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """통계 정보 조회"""
    try:
        device_id = request.args.get('device_id', None)
        stats = esp32_detector.get_statistics(device_id=device_id)
        
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

