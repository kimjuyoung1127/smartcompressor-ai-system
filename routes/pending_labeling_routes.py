#!/usr/bin/env python3
"""
보류 라벨링 API 라우트
대시보드에서 보류 항목을 조회하고 라벨링할 수 있는 API
"""

from flask import Blueprint, request, jsonify, send_file
import logging
import os
from pathlib import Path
from services.smart_detection_orchestrator import SmartDetectionOrchestrator

logger = logging.getLogger(__name__)

# 전역 오케스트레이터 인스턴스
orchestrator = SmartDetectionOrchestrator(
    confidence_threshold=0.7,
    use_mimii_model=True
)

# 라우트 블루프린트
pending_bp = Blueprint('pending_labeling', __name__, url_prefix='/api/pending')

@pending_bp.route('/items', methods=['GET'])
def get_pending_items():
    """
    보류 항목 목록 조회 (대시보드용)
    
    Query Parameters:
    - device_id: 디바이스 ID 필터 (선택적)
    - limit: 최대 개수 (기본값: 50)
    
    Response:
    {
        "items": [...],
        "statistics": {...},
        "total_pending": 10
    }
    """
    try:
        device_id = request.args.get('device_id', None)
        limit = int(request.args.get('limit', 50))
        
        result = orchestrator.get_pending_items_for_dashboard(
            device_id=device_id,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            **result
        })
        
    except Exception as e:
        logger.error(f"보류 항목 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pending_bp.route('/items/<item_id>', methods=['GET'])
def get_pending_item(item_id: str):
    """보류 항목 단일 조회"""
    try:
        item = orchestrator.pending_service.get_pending_item(item_id)
        
        if not item:
            return jsonify({
                'success': False,
                'error': '항목을 찾을 수 없습니다.'
            }), 404
        
        return jsonify({
            'success': True,
            'item': item
        })
        
    except Exception as e:
        logger.error(f"보류 항목 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pending_bp.route('/items/<item_id>/audio', methods=['GET'])
def get_pending_audio(item_id: str):
    """보류 항목의 오디오 파일 다운로드"""
    try:
        item = orchestrator.pending_service.get_pending_item(item_id)
        
        if not item:
            return jsonify({
                'success': False,
                'error': '항목을 찾을 수 없습니다.'
            }), 404
        
        audio_path = Path(item['audio_path'])
        
        if not audio_path.exists():
            return jsonify({
                'success': False,
                'error': '오디오 파일을 찾을 수 없습니다.'
            }), 404
        
        return send_file(
            str(audio_path),
            mimetype='audio/wav',
            as_attachment=True,
            download_name=f"{item_id}.wav"
        )
        
    except Exception as e:
        logger.error(f"오디오 파일 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pending_bp.route('/items/<item_id>/label', methods=['POST'])
def label_item(item_id: str):
    """
    보류 항목 라벨링
    
    Request Body:
    {
        "label": "normal" | "abnormal_bearing" | "abnormal_overload" | ...,
        "labeled_by": "user_id",
        "expert_confidence": 0.95,  # 선택적
        "notes": "메모"  # 선택적
    }
    
    Response:
    {
        "success": true,
        "item_id": "...",
        "label": "...",
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
        
        label = data.get('label')
        labeled_by = data.get('labeled_by', 'unknown')
        expert_confidence = data.get('expert_confidence')
        notes = data.get('notes')
        
        if not label:
            return jsonify({
                'success': False,
                'error': 'label이 필요합니다.'
            }), 400
        
        # 라벨링 완료
        result = orchestrator.complete_labeling(
            item_id=item_id,
            label=label,
            labeled_by=labeled_by,
            expert_confidence=expert_confidence,
            notes=notes
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"라벨링 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pending_bp.route('/items/<item_id>/reject', methods=['POST'])
def reject_item(item_id: str):
    """
    보류 항목 거부 (노이즈 등)
    
    Request Body:
    {
        "reason": "노이즈가 너무 많음"  # 선택적
    }
    """
    try:
        data = request.get_json() or {}
        reason = data.get('reason', 'No reason provided')
        
        success = orchestrator.pending_service.reject_item(item_id, reason)
        
        if success:
            return jsonify({
                'success': True,
                'item_id': item_id,
                'message': '항목이 거부되었습니다.'
            })
        else:
            return jsonify({
                'success': False,
                'error': '항목을 찾을 수 없습니다.'
            }), 404
        
    except Exception as e:
        logger.error(f"항목 거부 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pending_bp.route('/statistics', methods=['GET'])
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

@pending_bp.route('/labeled', methods=['GET'])
def get_labeled_items():
    """
    라벨링 완료된 항목 조회 (재학습용)
    
    Query Parameters:
    - limit: 최대 개수 (기본값: 1000)
    """
    try:
        limit = int(request.args.get('limit', 1000))
        
        items = orchestrator.pending_service.get_labeled_items_for_training(limit=limit)
        
        return jsonify({
            'success': True,
            'items': items,
            'count': len(items)
        })
        
    except Exception as e:
        logger.error(f"라벨링 완료 항목 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

