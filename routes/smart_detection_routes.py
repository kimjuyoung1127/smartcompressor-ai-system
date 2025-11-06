#!/usr/bin/env python3
"""
스마트 판단 API 라우트
실시간 판단 + 보류 라벨링 통합 API
"""

from flask import Blueprint, request, jsonify
import logging
import numpy as np
from services.smart_detection_orchestrator import SmartDetectionOrchestrator

logger = logging.getLogger(__name__)

# 전역 오케스트레이터 인스턴스
orchestrator = SmartDetectionOrchestrator(
    confidence_threshold=0.7,
    use_mimii_model=True
)

# 라우트 블루프린트
smart_bp = Blueprint('smart_detection', __name__, url_prefix='/api/smart/detect')

@smart_bp.route('', methods=['POST'])
def smart_detect():
    """
    스마트 판단 API
    
    Request Body:
    {
        "audio_data": [0.1, 0.2, ...],  # 오디오 샘플 배열
        "device_id": "ESP32_001",
        "sample_rate": 16000,  # 선택적
        "metadata": {...}  # 선택적
    }
    
    Response:
    {
        "decision": "auto" | "pending",  # 자동 판단 or 보류
        "result": {...},  # 판단 결과
        "pending_item_id": "...",  # 보류 항목 ID (보류인 경우)
        "message": "...",
        "confidence": 0.85
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
        metadata = data.get('metadata')
        
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
        
        # 스마트 판단 수행
        result = orchestrator.process_audio(
            audio_data=audio_array,
            device_id=device_id,
            metadata=metadata
        )
        
        return jsonify({
            'success': True,
            **result
        })
        
    except Exception as e:
        logger.error(f"스마트 판단 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@smart_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """통계 정보 조회"""
    try:
        stats = orchestrator.get_statistics()
        
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

