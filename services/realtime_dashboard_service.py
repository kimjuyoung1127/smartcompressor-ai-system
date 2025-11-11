#!/usr/bin/env python3
"""
실시간 대시보드 서비스 (Realtime Dashboard Service)

[일반인/개발자를 위한 설명]

이 서비스는 실시간으로 모니터링 데이터를 대시보드에 전송합니다.

🎯 주요 기능:

1. 실시간 데이터 스트리밍
   - WebSocket을 사용하여 실시간 데이터 전송
   - 비유: 라디오처럼 계속해서 데이터를 보내줌
   - 효과: 페이지 새로고침 없이 자동 업데이트

2. 고장 유형별 시각화
   - 각 고장 유형마다 다른 색상과 아이콘
   - 비유: 지도에서 장소마다 다른 마커
   - 효과: 한눈에 고장 유형 파악

3. 트렌드 분석
   - 시간에 따른 이상 점수 변화 그래프
   - 비유: 주식 차트처럼 시간에 따른 변화 표시
   - 효과: 고장 예측 가능

💡 왜 중요한가?
- 사용자가 실시간으로 상태를 확인할 수 있습니다
- 고장 유형을 한눈에 파악할 수 있습니다
- 트렌드를 통해 고장을 예측할 수 있습니다

🔧 개발자를 위한 설명:
- WebSocket: 양방향 실시간 통신
- Server-Sent Events (SSE): 서버에서 클라이언트로 단방향 스트리밍
- Chart.js: 실시간 차트 업데이트
"""

import asyncio
import json
import logging
import threading
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import deque

logger = logging.getLogger(__name__)


class RealtimeDashboardService:
    """
    실시간 대시보드 서비스
    
    [역할]
    실시간으로 모니터링 데이터를 대시보드에 전송
    
    [주요 기능]
    1. 실시간 데이터 스트리밍
    2. 고장 유형별 시각화 데이터 제공
    3. 트렌드 분석 데이터 제공
    """
    
    def __init__(self, max_history: int = 1000):
        """
        초기화
        
        Args:
            max_history: 최대 히스토리 크기
        """
        self.max_history = max_history
        self.clients = set()  # 연결된 클라이언트 (WebSocket 연결)
        self.data_history = deque(maxlen=max_history)  # 데이터 히스토리
        self.is_streaming = False
        self.streaming_thread = None
        
        logger.info("✅ 실시간 대시보드 서비스 초기화 완료")
    
    def add_client(self, client_id: str):
        """클라이언트 추가 (WebSocket 연결)"""
        self.clients.add(client_id)
        logger.info(f"클라이언트 연결: {client_id} (총 {len(self.clients)}개)")
    
    def remove_client(self, client_id: str):
        """클라이언트 제거 (WebSocket 연결 해제)"""
        self.clients.discard(client_id)
        logger.info(f"클라이언트 연결 해제: {client_id} (총 {len(self.clients)}개)")
    
    def broadcast_data(self, data: Dict):
        """
        모든 클라이언트에 데이터 브로드캐스트
        
        Args:
            data: 전송할 데이터
        """
        if not self.clients:
            return
        
        message = json.dumps(data)
        
        # 실제로는 WebSocket을 통해 전송
        # 여기서는 히스토리에 저장
        self.data_history.append({
            'timestamp': datetime.now().isoformat(),
            'data': data
        })
        
        logger.debug(f"데이터 브로드캐스트: {len(self.clients)}개 클라이언트")
    
    def get_realtime_data(self, device_id: Optional[str] = None) -> Dict:
        """
        실시간 데이터 조회
        
        Args:
            device_id: 디바이스 ID (선택적)
        
        Returns:
            실시간 데이터 딕셔너리
        """
        if not self.data_history:
            return {
                'timestamp': datetime.now().isoformat(),
                'device_id': device_id,
                'anomaly_score': 0.0,
                'decibel_level': 0.0,
                'is_anomaly': False,
                'anomaly_type': 'normal'
            }
        
        # 최신 데이터 반환
        latest = self.data_history[-1]
        return latest['data']
    
    def get_trend_data(self, device_id: Optional[str] = None, hours: int = 24) -> Dict:
        """
        트렌드 데이터 조회
        
        Args:
            device_id: 디바이스 ID (선택적)
            hours: 시간 범위 (시간)
        
        Returns:
            트렌드 데이터 딕셔너리
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # 시간 범위 내 데이터 필터링
        trend_data = []
        for item in self.data_history:
            item_time = datetime.fromisoformat(item['timestamp'])
            if item_time >= cutoff_time:
                data = item['data']
                if device_id is None or data.get('device_id') == device_id:
                    trend_data.append({
                        'timestamp': item['timestamp'],
                        'anomaly_score': data.get('anomaly_score', 0.0),
                        'decibel_level': data.get('decibel_level', 0.0),
                        'is_anomaly': data.get('is_anomaly', False),
                        'anomaly_type': data.get('anomaly_type', 'normal')
                    })
        
        return {
            'device_id': device_id,
            'hours': hours,
            'data_points': len(trend_data),
            'trend': trend_data
        }
    
    def get_failure_type_stats(self, device_id: Optional[str] = None, days: int = 7) -> Dict:
        """
        고장 유형별 통계 조회
        
        Args:
            device_id: 디바이스 ID (선택적)
            days: 기간 (일)
        
        Returns:
            고장 유형별 통계 딕셔너리
        """
        cutoff_time = datetime.now() - timedelta(days=days)
        
        failure_counts = {}
        total_anomalies = 0
        
        for item in self.data_history:
            item_time = datetime.fromisoformat(item['timestamp'])
            if item_time >= cutoff_time:
                data = item['data']
                if device_id is None or data.get('device_id') == device_id:
                    if data.get('is_anomaly', False):
                        anomaly_type = data.get('anomaly_type', 'general_anomaly')
                        failure_counts[anomaly_type] = failure_counts.get(anomaly_type, 0) + 1
                        total_anomalies += 1
        
        return {
            'device_id': device_id,
            'days': days,
            'total_anomalies': total_anomalies,
            'failure_types': failure_counts
        }

    def get_performance_metrics(self, device_id: Optional[str] = None) -> Dict:
        """
        성능 지표 조회
        
        Args:
            device_id: 디바이스 ID (선택적)
        
        Returns:
            성능 지표 딕셔너리
        """
        try:
            # ESP32 통합 서비스 통계
            from services.esp32_integrated_detection_service import esp32_integrated_service
            esp32_stats = esp32_integrated_service.get_statistics()
            
            # Active Learning 통계
            from services.advanced_active_learning import advanced_active_learning
            al_stats = advanced_active_learning.get_statistics()
            
            # 데이터 수집 통계
            from services.comprehensive_data_collection_service import comprehensive_data_collection_service
            collection_stats = comprehensive_data_collection_service.get_collection_statistics()
            
            # 시간별 처리량 계산
            recent_data = list(self.data_history)[-100:]  # 최근 100개
            if recent_data:
                time_span = (datetime.now() - datetime.fromisoformat(recent_data[0]['timestamp'])).total_seconds()
                throughput = len(recent_data) / time_span if time_span > 0 else 0
            else:
                throughput = 0
            
            return {
                'device_id': device_id,
                'timestamp': datetime.now().isoformat(),
                'processing': {
                    'total_processed': esp32_stats.get('total_processed', 0),
                    'avg_processing_time_ms': esp32_stats.get('avg_processing_time_ms', 0),
                    'throughput_per_second': float(throughput),
                    'anomaly_rate': esp32_stats.get('anomaly_rate', 0),
                    'quality_issue_rate': esp32_stats.get('quality_issue_rate', 0)
                },
                'active_learning': {
                    'total_queries': al_stats.get('total_queries', 0),
                    'labeled_count': al_stats.get('labeled_count', 0),
                    'labeling_rate': al_stats.get('labeling_rate', 0),
                    'avg_uncertainty': al_stats.get('avg_uncertainty', 0)
                },
                'data_collection': {
                    'total_collected': collection_stats.get('total_collected', 0),
                    'quality_pass_rate': collection_stats.get('quality_pass_rate', 0),
                    'labeling_rate': collection_stats.get('labeling_rate', 0)
                }
            }
        except Exception as e:
            logger.error(f"성능 지표 조회 오류: {e}")
            return {
                'device_id': device_id,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }

# 전역 인스턴스
realtime_dashboard_service = RealtimeDashboardService()

