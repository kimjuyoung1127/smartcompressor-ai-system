#!/usr/bin/env python3
"""
종합 데이터 수집 및 검증 서비스
데이터 수집, 품질 검증, 버전 관리, 라벨링 품질 관리를 통합

[기능]
1. 데이터 수집 및 자동 품질 검증
2. 데이터 버전 관리
3. 라벨링 품질 관리
4. 데이터 통계 및 리포트 생성
"""

import numpy as np
import logging
from typing import Dict, List, Optional
from datetime import datetime
import os

from services.data_quality_validator import data_quality_validator
from services.data_version_manager import data_version_manager
from services.labeling_quality_manager import labeling_quality_manager

logger = logging.getLogger(__name__)


class ComprehensiveDataCollectionService:
    """
    종합 데이터 수집 및 검증 서비스
    
    [역할]
    - 데이터 수집 파이프라인 관리
    - 자동 품질 검증
    - 버전 관리
    - 라벨링 품질 관리
    """
    
    def __init__(self,
                 default_version: str = "v1.0.0",
                 auto_versioning: bool = True):
        """
        초기화
        
        Args:
            default_version: 기본 버전 이름
            auto_versioning: 자동 버전 관리 여부
        """
        self.default_version = default_version
        self.auto_versioning = auto_versioning
        self.current_version_id = None
        
        # 통계
        self.stats = {
            'total_collected': 0,
            'quality_passed': 0,
            'quality_failed': 0,
            'labeled': 0,
            'unlabeled': 0
        }
        
        logger.info("✅ 종합 데이터 수집 및 검증 서비스 초기화 완료")
    
    def collect_and_validate(self,
                            audio_data: np.ndarray,
                            sample_rate: int,
                            device_id: str,
                            metadata: Optional[Dict] = None,
                            save_path: Optional[str] = None) -> Dict:
        """
        데이터 수집 및 자동 품질 검증
        
        [작동 방식]
        1. 오디오 데이터 수집
        2. 자동 품질 검증
        3. 버전 관리 (선택)
        4. 결과 반환
        
        Args:
            audio_data: 오디오 배열
            sample_rate: 샘플링 레이트
            device_id: 디바이스 ID
            metadata: 메타데이터
            save_path: 저장 경로 (선택)
        
        Returns:
            {
                'success': bool,
                'sample_id': str,
                'quality_result': Dict,
                'version_id': str,
                'message': str
            }
        """
        try:
            # 메타데이터 준비
            full_metadata = {
                'device_id': device_id,
                'timestamp': datetime.now().isoformat(),
                'sample_rate': sample_rate,
                **(metadata or {})
            }
            
            # 1. 품질 검증
            quality_result = data_quality_validator.validate_audio_data(
                audio_data=audio_data,
                sample_rate=sample_rate,
                metadata=full_metadata
            )
            
            # 2. 샘플 ID 생성
            sample_id = self._generate_sample_id(device_id, full_metadata['timestamp'])
            
            # 3. 품질 통과 여부 확인
            is_valid = quality_result['is_valid']
            
            if is_valid:
                self.stats['quality_passed'] += 1
                
                # 4. 파일 저장 (선택)
                if save_path:
                    self._save_audio_file(audio_data, sample_rate, save_path)
                    
                    # 5. 버전 관리 (자동 버전 관리 활성화 시)
                    if self.auto_versioning:
                        version_id = self._ensure_version()
                        data_version_manager.add_file_to_version(
                            version_id=version_id,
                            file_path=save_path,
                            metadata=full_metadata
                        )
                else:
                    version_id = None
                
                self.stats['total_collected'] += 1
                self.stats['unlabeled'] += 1
                
                return {
                    'success': True,
                    'sample_id': sample_id,
                    'quality_result': quality_result,
                    'version_id': version_id,
                    'message': '데이터 수집 및 검증 완료'
                }
            else:
                self.stats['quality_failed'] += 1
                
                return {
                    'success': False,
                    'sample_id': sample_id,
                    'quality_result': quality_result,
                    'version_id': None,
                    'message': f"품질 검증 실패: {', '.join(quality_result['issues'])}"
                }
        
        except Exception as e:
            logger.error(f"데이터 수집 및 검증 오류: {e}")
            return {
                'success': False,
                'sample_id': None,
                'quality_result': None,
                'version_id': None,
                'message': f'오류: {str(e)}'
            }
    
    def add_labeling(self,
                    sample_id: str,
                    annotator_id: str,
                    label: str,
                    confidence: float = 1.0,
                    metadata: Optional[Dict] = None) -> Dict:
        """
        라벨링 추가
        
        Args:
            sample_id: 샘플 ID
            annotator_id: 라벨링 담당자 ID
            label: 라벨
            confidence: 신뢰도
            metadata: 추가 메타데이터
        
        Returns:
            라벨링 결과
        """
        try:
            # 라벨링 기록
            labeling_quality_manager.record_labeling(
                sample_id=sample_id,
                annotator_id=annotator_id,
                label=label,
                confidence=confidence,
                metadata=metadata
            )
            
            # 품질 평가
            quality_eval = labeling_quality_manager.evaluate_labeling_quality(sample_id)
            
            self.stats['labeled'] += 1
            if sample_id in [s for s in self.stats if s.startswith('unlabeled')]:
                self.stats['unlabeled'] = max(0, self.stats['unlabeled'] - 1)
            
            return {
                'success': True,
                'sample_id': sample_id,
                'quality_evaluation': quality_eval,
                'message': '라벨링 추가 완료'
            }
        
        except Exception as e:
            logger.error(f"라벨링 추가 오류: {e}")
            return {
                'success': False,
                'message': f'오류: {str(e)}'
            }
    
    def get_collection_statistics(self) -> Dict:
        """
        수집 통계 조회
        
        Returns:
            통계 정보
        """
        quality_pass_rate = (
            self.stats['quality_passed'] / self.stats['total_collected']
            if self.stats['total_collected'] > 0 else 0
        )
        
        labeling_rate = (
            self.stats['labeled'] / self.stats['total_collected']
            if self.stats['total_collected'] > 0 else 0
        )
        
        return {
            'total_collected': self.stats['total_collected'],
            'quality_passed': self.stats['quality_passed'],
            'quality_failed': self.stats['quality_failed'],
            'quality_pass_rate': float(quality_pass_rate),
            'labeled': self.stats['labeled'],
            'unlabeled': self.stats['unlabeled'],
            'labeling_rate': float(labeling_rate)
        }
    
    def _generate_sample_id(self, device_id: str, timestamp: str) -> str:
        """
        샘플 ID 생성
        
        Args:
            device_id: 디바이스 ID
            timestamp: 타임스탬프
        
        Returns:
            샘플 ID
        """
        # 타임스탬프에서 날짜/시간 추출
        date_str = timestamp.split('T')[0].replace('-', '')
        time_str = timestamp.split('T')[1].split('.')[0].replace(':', '')
        
        return f"{device_id}_{date_str}_{time_str}"
    
    def _ensure_version(self) -> str:
        """
        현재 버전 확인 및 생성
        
        Returns:
            버전 ID
        """
        if self.current_version_id:
            return self.current_version_id
        
        # 버전 생성
        version_id = data_version_manager.create_version(
            version_name=self.default_version,
            description=f"자동 생성된 버전: {self.default_version}",
            created_by="system"
        )
        
        self.current_version_id = version_id
        return version_id
    
    def _save_audio_file(self, audio_data: np.ndarray, sample_rate: int, file_path: str):
        """
        오디오 파일 저장
        
        Args:
            audio_data: 오디오 배열
            sample_rate: 샘플링 레이트
            file_path: 저장 경로
        """
        try:
            import soundfile as sf
            
            # 디렉토리 생성
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 파일 저장
            sf.write(file_path, audio_data, sample_rate, format='WAV')
            
            logger.debug(f"오디오 파일 저장: {file_path}")
        
        except Exception as e:
            logger.error(f"오디오 파일 저장 오류: {e}")
            raise


# 전역 인스턴스
comprehensive_data_collection_service = ComprehensiveDataCollectionService()

