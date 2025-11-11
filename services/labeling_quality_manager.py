#!/usr/bin/env python3
"""
라벨링 품질 관리 시스템
라벨링 품질을 검증하고 관리

[기능]
1. 라벨 일관성 검증
2. 라벨 완전성 검증
3. 전문가 간 일치도 측정 (Inter-annotator Agreement)
4. 라벨링 가이드라인 준수 여부 확인
5. 라벨링 품질 점수 계산
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from collections import Counter
import sqlite3
import json

logger = logging.getLogger(__name__)


class LabelingQualityManager:
    """
    라벨링 품질 관리 시스템
    
    [역할]
    - 라벨링 품질 검증
    - 전문가 간 일치도 측정
    - 라벨링 가이드라인 준수 여부 확인
    """
    
    def __init__(self, db_path: str = "data/labeling_quality.db"):
        """
        초기화
        
        Args:
            db_path: 데이터베이스 경로
        """
        self.db_path = db_path
        import os
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_database()
        
        logger.info("✅ 라벨링 품질 관리 시스템 초기화 완료")
    
    def _init_database(self):
        """데이터베이스 초기화"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 라벨링 기록 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS labeling_records (
                    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sample_id TEXT NOT NULL,
                    annotator_id TEXT NOT NULL,
                    label TEXT NOT NULL,
                    confidence REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata_json TEXT,
                    UNIQUE(sample_id, annotator_id)
                )
            ''')
            
            # 라벨링 품질 평가 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS labeling_quality_scores (
                    sample_id TEXT PRIMARY KEY,
                    consistency_score REAL,
                    completeness_score REAL,
                    agreement_score REAL,
                    overall_score REAL,
                    evaluated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    issues_json TEXT
                )
            ''')
            
            # 인덱스 생성
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_labeling_records_sample ON labeling_records(sample_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_labeling_records_annotator ON labeling_records(annotator_id)')
            
            conn.commit()
    
    def record_labeling(self,
                       sample_id: str,
                       annotator_id: str,
                       label: str,
                       confidence: float = 1.0,
                       metadata: Optional[Dict] = None):
        """
        라벨링 기록
        
        Args:
            sample_id: 샘플 ID
            annotator_id: 라벨링 담당자 ID
            label: 라벨
            confidence: 신뢰도 (0-1)
            metadata: 추가 메타데이터
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO labeling_records
                (sample_id, annotator_id, label, confidence, metadata_json)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                sample_id,
                annotator_id,
                label,
                confidence,
                json.dumps(metadata or {})
            ))
            conn.commit()
        
        logger.debug(f"라벨링 기록: {sample_id} → {label} (by {annotator_id})")
    
    def evaluate_labeling_quality(self, sample_id: str) -> Dict:
        """
        라벨링 품질 평가
        
        Args:
            sample_id: 샘플 ID
        
        Returns:
            품질 평가 결과
        """
        # 라벨링 기록 조회
        records = self._get_labeling_records(sample_id)
        
        if not records:
            return {
                'sample_id': sample_id,
                'overall_score': 0.0,
                'consistency_score': 0.0,
                'completeness_score': 0.0,
                'agreement_score': 0.0,
                'issues': ['라벨링 기록이 없습니다'],
                'recommendations': ['라벨링을 수행하세요']
            }
        
        # 1. 일관성 점수 (같은 샘플에 대한 라벨 일치도)
        consistency_score = self._calculate_consistency(records)
        
        # 2. 완전성 점수 (필수 필드 존재 여부)
        completeness_score = self._calculate_completeness(records)
        
        # 3. 전문가 간 일치도 (여러 전문가가 라벨링한 경우)
        agreement_score = self._calculate_agreement(records)
        
        # 전체 점수 (가중 평균)
        overall_score = (
            consistency_score * 0.4 +
            completeness_score * 0.3 +
            agreement_score * 0.3
        )
        
        # 문제점 및 개선 제안
        issues = []
        recommendations = []
        
        if consistency_score < 0.7:
            issues.append('라벨 일관성이 낮습니다')
            recommendations.append('라벨링 가이드라인을 확인하고 재라벨링을 고려하세요')
        
        if completeness_score < 0.8:
            issues.append('라벨 완전성이 부족합니다')
            recommendations.append('필수 필드를 모두 채워주세요')
        
        if agreement_score < 0.6 and len(records) > 1:
            issues.append('전문가 간 일치도가 낮습니다')
            recommendations.append('라벨링 가이드라인을 명확히 하고 전문가 간 논의를 진행하세요')
        
        # 결과 저장
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO labeling_quality_scores
                (sample_id, consistency_score, completeness_score, agreement_score, overall_score, issues_json)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                sample_id,
                consistency_score,
                completeness_score,
                agreement_score,
                overall_score,
                json.dumps(issues)
            ))
            conn.commit()
        
        return {
            'sample_id': sample_id,
            'overall_score': float(overall_score),
            'consistency_score': float(consistency_score),
            'completeness_score': float(completeness_score),
            'agreement_score': float(agreement_score),
            'issues': issues,
            'recommendations': recommendations,
            'record_count': len(records)
        }
    
    def _get_labeling_records(self, sample_id: str) -> List[Dict]:
        """라벨링 기록 조회"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM labeling_records
                WHERE sample_id = ?
            ''', (sample_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def _calculate_consistency(self, records: List[Dict]) -> float:
        """
        일관성 점수 계산
        
        같은 샘플에 대한 라벨이 일치하는지 확인
        """
        if len(records) == 0:
            return 0.0
        
        if len(records) == 1:
            return 1.0  # 라벨이 하나면 일관성 100%
        
        # 라벨 분포
        labels = [r['label'] for r in records]
        label_counts = Counter(labels)
        
        # 가장 많은 라벨의 비율
        most_common_count = label_counts.most_common(1)[0][1]
        consistency = most_common_count / len(records)
        
        return float(consistency)
    
    def _calculate_completeness(self, records: List[Dict]) -> float:
        """
        완전성 점수 계산
        
        필수 필드가 모두 채워져 있는지 확인
        """
        if len(records) == 0:
            return 0.0
        
        required_fields = ['label', 'annotator_id', 'confidence']
        complete_count = 0
        
        for record in records:
            if all(field in record and record[field] is not None for field in required_fields):
                complete_count += 1
        
        return float(complete_count / len(records))
    
    def _calculate_agreement(self, records: List[Dict]) -> float:
        """
        전문가 간 일치도 계산 (Cohen's Kappa 계수 간소화 버전)
        
        여러 전문가가 라벨링한 경우 일치도 측정
        """
        if len(records) <= 1:
            return 1.0  # 전문가가 한 명이면 일치도 100%
        
        labels = [r['label'] for r in records]
        label_counts = Counter(labels)
        
        # 모든 라벨이 같으면 일치도 100%
        if len(label_counts) == 1:
            return 1.0
        
        # 가장 많은 라벨의 비율 (간단한 일치도 측정)
        most_common_count = label_counts.most_common(1)[0][1]
        agreement = most_common_count / len(records)
        
        return float(agreement)
    
    def get_annotator_statistics(self, annotator_id: str) -> Dict:
        """
        라벨링 담당자 통계 조회
        
        Args:
            annotator_id: 라벨링 담당자 ID
        
        Returns:
            통계 정보
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 총 라벨링 수
            cursor.execute('''
                SELECT COUNT(*) FROM labeling_records
                WHERE annotator_id = ?
            ''', (annotator_id,))
            total_count = cursor.fetchone()[0]
            
            # 평균 신뢰도
            cursor.execute('''
                SELECT AVG(confidence) FROM labeling_records
                WHERE annotator_id = ?
            ''', (annotator_id,))
            avg_confidence = cursor.fetchone()[0] or 0.0
            
            # 라벨 분포
            cursor.execute('''
                SELECT label, COUNT(*) as count
                FROM labeling_records
                WHERE annotator_id = ?
                GROUP BY label
            ''', (annotator_id,))
            label_distribution = {row[0]: row[1] for row in cursor.fetchall()}
            
            return {
                'annotator_id': annotator_id,
                'total_labelings': total_count,
                'avg_confidence': float(avg_confidence),
                'label_distribution': label_distribution
            }


# 전역 인스턴스
labeling_quality_manager = LabelingQualityManager()

