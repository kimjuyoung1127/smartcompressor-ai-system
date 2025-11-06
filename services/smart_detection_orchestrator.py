#!/usr/bin/env python3
"""
스마트 판단 오케스트레이터 (Smart Detection Orchestrator)
실시간 판단 + 보류 라벨링을 통합 관리하는 오케스트레이터
"""

import logging
import numpy as np
from datetime import datetime
from typing import Dict, Optional
from services.realtime_failure_detection_service import RealtimeFailureDetectionService
from services.pending_labeling_service import PendingLabelingService

logger = logging.getLogger(__name__)


class SmartDetectionOrchestrator:
    """
    스마트 판단 오케스트레이터
    
    워크플로우:
    1. 실시간 판단 수행
    2. 신뢰도가 높으면 → 즉시 판단 결과 반환
    3. 신뢰도가 낮으면 → 보류 큐에 추가, 대시보드에서 수동 라벨링 대기
    """
    
    def __init__(self,
                 confidence_threshold: float = 0.7,
                 use_mimii_model: bool = True,
                 auto_save_audio: bool = True):
        """
        Args:
            confidence_threshold: 신뢰도 임계값 (이하이면 보류)
            use_mimii_model: MIMII 모델 사용 여부
            auto_save_audio: 오디오 자동 저장 여부
        """
        # 실시간 판단 서비스
        self.detector = RealtimeFailureDetectionService(
            use_mimii_model=use_mimii_model
        )
        
        # 보류 라벨링 서비스
        self.pending_service = PendingLabelingService(
            confidence_threshold=confidence_threshold
        )
        
        self.auto_save_audio = auto_save_audio
        
        logger.info("✅ 스마트 판단 오케스트레이터 초기화 완료")
        logger.info(f"   - 신뢰도 임계값: {confidence_threshold:.2%}")
        logger.info(f"   - MIMII 모델: {'사용' if use_mimii_model else '미사용'}")
    
    def process_audio(self, 
                     audio_data: np.ndarray,
                     device_id: str,
                     metadata: Dict = None) -> Dict:
        """
        오디오 처리 및 판단
        
        Args:
            audio_data: 오디오 데이터
            device_id: 디바이스 ID
            metadata: 추가 메타데이터
        
        Returns:
            {
                'decision': 'auto' | 'pending',  # 자동 판단 or 보류
                'result': detection_result,  # 판단 결과
                'pending_item_id': str,  # 보류 항목 ID (보류인 경우)
                'message': str
            }
        """
        try:
            # 1. 실시간 판단 수행
            detection_result = self.detector.process_audio(audio_data, device_id=device_id)
            
            # 2. 보류 여부 판단
            should_pend = self.pending_service.should_pend_labeling(detection_result)
            
            if should_pend:
                # 3. 보류 큐에 추가
                pending_item_id = self.pending_service.add_pending_item(
                    audio_data=audio_data,
                    detection_result=detection_result,
                    device_id=device_id,
                    metadata=metadata
                )
                
                logger.info(f"📋 보류 큐 추가: {pending_item_id} (신뢰도: {detection_result['confidence']:.2%})")
                
                return {
                    'decision': 'pending',
                    'result': detection_result,
                    'pending_item_id': pending_item_id,
                    'message': f"신뢰도가 낮아 보류 큐에 추가되었습니다. 대시보드에서 수동 라벨링이 필요합니다.",
                    'confidence': detection_result['confidence'],
                    'threshold': self.pending_service.confidence_threshold
                }
            else:
                # 4. 자동 판단 완료
                logger.info(f"✅ 자동 판단 완료: {device_id} (신뢰도: {detection_result['confidence']:.2%})")
                
                return {
                    'decision': 'auto',
                    'result': detection_result,
                    'pending_item_id': None,
                    'message': f"자동 판단 완료: {'고장' if detection_result['is_failure'] else '정상'}",
                    'confidence': detection_result['confidence']
                }
                
        except Exception as e:
            logger.error(f"오디오 처리 실패: {e}")
            return {
                'decision': 'error',
                'result': None,
                'pending_item_id': None,
                'message': f"처리 오류: {str(e)}",
                'error': str(e)
            }
    
    def get_pending_items_for_dashboard(self, 
                                       device_id: Optional[str] = None,
                                       limit: int = 50) -> Dict:
        """
        대시보드용 보류 항목 조회
        
        Returns:
            {
                'items': [...],
                'statistics': {...}
            }
        """
        items = self.pending_service.get_pending_items(
            device_id=device_id,
            status='pending',
            limit=limit
        )
        
        # 대시보드용 포맷팅
        formatted_items = []
        for item in items:
            formatted_items.append({
                'id': item['item_id'],
                'device_id': item['device_id'],
                'timestamp': item['timestamp'],
                'audio_path': item['audio_path'],
                'confidence': item['confidence'],
                'score': item['score'],
                'predicted_class': item.get('predicted_class', 'unknown'),
                'method': item.get('method', 'unknown'),
                'detection_result': item['detection_result']
            })
        
        statistics = self.pending_service.get_statistics()
        
        return {
            'items': formatted_items,
            'statistics': statistics,
            'total_pending': len(formatted_items)
        }
    
    def complete_labeling(self,
                         item_id: str,
                         label: str,
                         labeled_by: str,
                         expert_confidence: float = None,
                         notes: str = None) -> Dict:
        """
        라벨링 완료 처리
        
        Returns:
            {
                'success': bool,
                'item_id': str,
                'label': str,
                'message': str
            }
        """
        success = self.pending_service.update_labeling(
            item_id=item_id,
            label=label,
            labeled_by=labeled_by,
            expert_confidence=expert_confidence,
            notes=notes
        )
        
        if success:
            logger.info(f"✅ 라벨링 완료: {item_id} -> {label}")
            return {
                'success': True,
                'item_id': item_id,
                'label': label,
                'message': '라벨링이 완료되었습니다.'
            }
        else:
            return {
                'success': False,
                'item_id': item_id,
                'message': '라벨링 업데이트 실패'
            }
    
    def get_statistics(self) -> Dict:
        """전체 통계"""
        detector_stats = {
            'total_detections': len(self.detector.detection_history),
            'recent_failures': sum(
                1 for h in self.detector.detection_history[-100:]
                if h.get('is_failure', False)
            )
        }
        
        pending_stats = self.pending_service.get_statistics()
        
        return {
            'detection': detector_stats,
            'pending': pending_stats,
            'auto_decision_rate': (
                1.0 - pending_stats['pending_rate']
                if pending_stats['total'] > 0 else 1.0
            )
        }


if __name__ == "__main__":
    # 테스트 코드
    logging.basicConfig(level=logging.INFO)
    
    orchestrator = SmartDetectionOrchestrator(
        confidence_threshold=0.7,
        use_mimii_model=True
    )
    
    # 테스트: 낮은 신뢰도 오디오
    test_audio = np.random.randn(32000)  # 2초 @ 16kHz
    
    result = orchestrator.process_audio(
        audio_data=test_audio,
        device_id="test_device_001"
    )
    
    print("\n" + "="*60)
    print("스마트 판단 결과")
    print("="*60)
    print(f"결정: {result['decision']}")
    print(f"메시지: {result['message']}")
    
    if result['decision'] == 'pending':
        print(f"보류 항목 ID: {result['pending_item_id']}")
        
        # 대시보드용 조회
        dashboard_data = orchestrator.get_pending_items_for_dashboard()
        print(f"보류 항목 개수: {dashboard_data['total_pending']}")
    
    # 통계
    stats = orchestrator.get_statistics()
    print(f"\n통계:")
    print(f"  자동 판단률: {stats['auto_decision_rate']:.2%}")

