#!/usr/bin/env python3
"""
보류 라벨링 서비스 (Pending Labeling Service)
실시간 판단 결과 중 신뢰도가 낮은 데이터를 보류하고, 대시보드에서 수동 라벨링할 수 있게 함
"""

import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class LabelingStatus(Enum):
    """라벨링 상태"""
    PENDING = "pending"  # 라벨링 대기
    IN_PROGRESS = "in_progress"  # 라벨링 진행 중
    COMPLETED = "completed"  # 라벨링 완료
    REJECTED = "rejected"  # 거부됨 (노이즈 등)


class PendingLabelingService:
    """보류 라벨링 서비스"""
    
    def __init__(self, 
                 confidence_threshold: float = 0.7,
                 db_path: str = "data/pending_labeling.db"):
        """
        Args:
            confidence_threshold: 신뢰도 임계값 (이하이면 보류)
            db_path: 데이터베이스 경로 (SQLite)
        """
        self.confidence_threshold = confidence_threshold
        self.db_path = db_path
        self.pending_dir = Path("data/pending_labeling")
        self.pending_dir.mkdir(parents=True, exist_ok=True)
        
        # 인메모리 저장소 (실제로는 DB 사용)
        self.pending_items = {}  # {item_id: item_data}
        self.next_id = 1
        
        logger.info(f"✅ 보류 라벨링 서비스 초기화 완료")
        logger.info(f"   - 신뢰도 임계값: {confidence_threshold:.2%}")
        logger.info(f"   - 보류 데이터 < {confidence_threshold:.2%} 신뢰도")
    
    def should_pend_labeling(self, detection_result: Dict) -> bool:
        """
        라벨링 보류 여부 판단
        
        Args:
            detection_result: 실시간 판단 결과
        
        Returns:
            bool: 보류 필요 여부
        """
        confidence = detection_result.get('confidence', 0.0)
        
        # 신뢰도가 임계값보다 낮으면 보류
        if confidence < self.confidence_threshold:
            return True
        
        # 점수가 중간값이면 보류 (0.3 ~ 0.7)
        score = detection_result.get('score', 0.0)
        if 0.3 <= score <= 0.7:
            return True
        
        return False
    
    def add_pending_item(self, 
                        audio_data: np.ndarray,
                        detection_result: Dict,
                        device_id: str,
                        timestamp: datetime = None,
                        metadata: Dict = None) -> str:
        """
        보류 항목 추가
        
        Args:
            audio_data: 오디오 데이터
            detection_result: 실시간 판단 결과
            device_id: 디바이스 ID
            timestamp: 타임스탬프
            metadata: 추가 메타데이터
        
        Returns:
            str: 보류 항목 ID
        """
        try:
            if timestamp is None:
                timestamp = datetime.now()
            
            item_id = f"pending_{self.next_id:06d}_{int(timestamp.timestamp())}"
            self.next_id += 1
            
            # 오디오 데이터 저장
            audio_path = self.pending_dir / f"{item_id}.wav"
            import soundfile as sf
            sf.write(str(audio_path), audio_data, 16000)
            
            # 보류 항목 데이터
            pending_item = {
                'item_id': item_id,
                'device_id': device_id,
                'timestamp': timestamp.isoformat(),
                'audio_path': str(audio_path),
                'detection_result': detection_result,
                'status': LabelingStatus.PENDING.value,
                'confidence': detection_result.get('confidence', 0.0),
                'score': detection_result.get('score', 0.0),
                'predicted_class': detection_result.get('predicted_class', 'unknown'),
                'method': detection_result.get('method', 'unknown'),
                'metadata': metadata or {},
                'created_at': datetime.now().isoformat(),
                'labeled_at': None,
                'labeled_by': None,
                'label': None,
                'expert_confidence': None
            }
            
            self.pending_items[item_id] = pending_item
            
            logger.info(f"📋 보류 항목 추가: {item_id} (신뢰도: {detection_result.get('confidence', 0):.2%})")
            
            return item_id
            
        except Exception as e:
            logger.error(f"보류 항목 추가 실패: {e}")
            return None
    
    def get_pending_items(self, 
                          device_id: Optional[str] = None,
                          status: Optional[str] = None,
                          limit: int = 100) -> List[Dict]:
        """
        보류 항목 조회
        
        Args:
            device_id: 디바이스 ID 필터 (선택적)
            status: 상태 필터 (선택적)
            limit: 최대 개수
        
        Returns:
            List[Dict]: 보류 항목 리스트
        """
        items = list(self.pending_items.values())
        
        # 필터링
        if device_id:
            items = [item for item in items if item['device_id'] == device_id]
        
        if status:
            items = [item for item in items if item['status'] == status]
        
        # 최신순 정렬
        items.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # 제한
        return items[:limit]
    
    def get_pending_item(self, item_id: str) -> Optional[Dict]:
        """보류 항목 단일 조회"""
        return self.pending_items.get(item_id)
    
    def update_labeling(self, 
                       item_id: str,
                       label: str,
                       labeled_by: str,
                       expert_confidence: float = None,
                       notes: str = None) -> bool:
        """
        라벨링 업데이트
        
        Args:
            item_id: 보류 항목 ID
            label: 라벨 (예: 'normal', 'abnormal_bearing', 'abnormal_overload' 등)
            labeled_by: 라벨링한 사용자 ID
            expert_confidence: 전문가 신뢰도 (선택적)
            notes: 메모 (선택적)
        
        Returns:
            bool: 성공 여부
        """
        try:
            if item_id not in self.pending_items:
                logger.error(f"보류 항목을 찾을 수 없습니다: {item_id}")
                return False
            
            item = self.pending_items[item_id]
            
            # 라벨링 정보 업데이트
            item['status'] = LabelingStatus.COMPLETED.value
            item['label'] = label
            item['labeled_by'] = labeled_by
            item['labeled_at'] = datetime.now().isoformat()
            item['expert_confidence'] = expert_confidence
            item['notes'] = notes
            
            logger.info(f"✅ 라벨링 완료: {item_id} -> {label} (전문가: {labeled_by})")
            
            return True
            
        except Exception as e:
            logger.error(f"라벨링 업데이트 실패: {e}")
            return False
    
    def reject_item(self, item_id: str, reason: str = None) -> bool:
        """항목 거부 (노이즈 등)"""
        try:
            if item_id not in self.pending_items:
                return False
            
            item = self.pending_items[item_id]
            item['status'] = LabelingStatus.REJECTED.value
            item['rejected_at'] = datetime.now().isoformat()
            item['rejection_reason'] = reason
            
            logger.info(f"❌ 항목 거부: {item_id} (이유: {reason})")
            
            return True
            
        except Exception as e:
            logger.error(f"항목 거부 실패: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """통계 정보"""
        total = len(self.pending_items)
        pending = sum(1 for item in self.pending_items.values() 
                     if item['status'] == LabelingStatus.PENDING.value)
        completed = sum(1 for item in self.pending_items.values() 
                       if item['status'] == LabelingStatus.COMPLETED.value)
        rejected = sum(1 for item in self.pending_items.values() 
                      if item['status'] == LabelingStatus.REJECTED.value)
        
        return {
            'total': total,
            'pending': pending,
            'completed': completed,
            'rejected': rejected,
            'pending_rate': pending / total if total > 0 else 0.0
        }
    
    def get_labeled_items_for_training(self, limit: int = 1000) -> List[Dict]:
        """재학습용 라벨링된 항목 조회"""
        completed_items = [
            item for item in self.pending_items.values()
            if item['status'] == LabelingStatus.COMPLETED.value
            and item['label'] is not None
        ]
        
        completed_items.sort(key=lambda x: x['labeled_at'], reverse=True)
        return completed_items[:limit]


if __name__ == "__main__":
    # 테스트 코드
    logging.basicConfig(level=logging.INFO)
    
    service = PendingLabelingService(confidence_threshold=0.7)
    
    # 테스트: 낮은 신뢰도 결과
    low_confidence_result = {
        'is_failure': False,
        'confidence': 0.5,  # 임계값 0.7 이하
        'score': 0.4,
        'method': 'fallback'
    }
    
    # 보류 여부 확인
    should_pend = service.should_pend_labeling(low_confidence_result)
    print(f"보류 필요: {should_pend}")
    
    if should_pend:
        # 보류 항목 추가
        test_audio = np.random.randn(32000)  # 2초 @ 16kHz
        item_id = service.add_pending_item(
            audio_data=test_audio,
            detection_result=low_confidence_result,
            device_id="test_device_001"
        )
        print(f"보류 항목 ID: {item_id}")
        
        # 보류 항목 조회
        pending = service.get_pending_items()
        print(f"보류 항목 개수: {len(pending)}")
        
        # 라벨링
        service.update_labeling(item_id, label='normal', labeled_by='expert_001')
        
        # 통계
        stats = service.get_statistics()
        print(f"통계: {stats}")

