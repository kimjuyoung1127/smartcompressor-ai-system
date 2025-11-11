#!/usr/bin/env python3
"""
실시간 대시보드 라우트 (Realtime Dashboard Routes)

WebSocket 및 REST API를 통한 실시간 대시보드 데이터 제공
"""

from flask import Blueprint, jsonify, request
from flask_cors import CORS
import logging
from typing import Optional
from services.realtime_dashboard_service import realtime_dashboard_service
from services.universal_monitoring_service import UniversalMonitoringService

logger = logging.getLogger(__name__)

realtime_dashboard_bp = Blueprint('realtime_dashboard', __name__)
CORS(realtime_dashboard_bp)

# 전역 모니터링 서비스 인스턴스 (실제로는 app.py에서 주입)
monitoring_service: Optional[UniversalMonitoringService] = None

def init_monitoring_service(service: UniversalMonitoringService):
    """모니터링 서비스 초기화"""
    global monitoring_service
    monitoring_service = service

@realtime_dashboard_bp.route('/api/realtime/data', methods=['GET'])
def get_realtime_data():
    """
    실시간 데이터 조회
    
    Query Parameters:
        device_id: 디바이스 ID (선택적)
    """
    try:
        device_id = request.args.get('device_id')
        data = realtime_dashboard_service.get_realtime_data(device_id)
        return jsonify(data), 200
    except Exception as e:
        logger.error(f"실시간 데이터 조회 오류: {e}")
        return jsonify({'error': str(e)}), 500

@realtime_dashboard_bp.route('/api/realtime/trend', methods=['GET'])
def get_trend_data():
    """
    트렌드 데이터 조회
    
    Query Parameters:
        device_id: 디바이스 ID (선택적)
        hours: 시간 범위 (기본 24시간)
    """
    try:
        device_id = request.args.get('device_id')
        hours = int(request.args.get('hours', 24))
        data = realtime_dashboard_service.get_trend_data(device_id, hours)
        return jsonify(data), 200
    except Exception as e:
        logger.error(f"트렌드 데이터 조회 오류: {e}")
        return jsonify({'error': str(e)}), 500

@realtime_dashboard_bp.route('/api/realtime/failure-stats', methods=['GET'])
def get_failure_stats():
    """
    고장 유형별 통계 조회
    
    Query Parameters:
        device_id: 디바이스 ID (선택적)
        days: 기간 (기본 7일)
    """
    try:
        device_id = request.args.get('device_id')
        days = int(request.args.get('days', 7))
        data = realtime_dashboard_service.get_failure_type_stats(device_id, days)
        return jsonify(data), 200
    except Exception as e:
        logger.error(f"고장 통계 조회 오류: {e}")
        return jsonify({'error': str(e)}), 500

@realtime_dashboard_bp.route('/api/realtime/performance-stats', methods=['GET'])
def get_performance_stats():
    """
    성능 통계 조회
    
    Returns:
        성능 최적화 통계
    """
    try:
        if monitoring_service is None:
            return jsonify({'error': '모니터링 서비스가 초기화되지 않았습니다.'}), 500
        
        stats = monitoring_service.get_performance_stats()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"성능 통계 조회 오류: {e}")
        return jsonify({'error': str(e)}), 500

@realtime_dashboard_bp.route('/api/realtime/performance-metrics', methods=['GET'])
def get_performance_metrics():
    """
    성능 지표 조회 (대시보드용)
    
    Query Parameters:
        device_id: 디바이스 ID (선택적)
    
    Returns:
        성능 지표 (처리 시간, 처리량, 품질 통과율, Active Learning 통계 등)
    """
    try:
        device_id = request.args.get('device_id')
        metrics = realtime_dashboard_service.get_performance_metrics(device_id)
        return jsonify(metrics), 200
    except Exception as e:
        logger.error(f"성능 지표 조회 오류: {e}")
        return jsonify({'error': str(e)}), 500

