#!/usr/bin/env python3
"""
데이터 버전 관리 시스템
수집된 데이터의 버전을 관리하고 추적

[기능]
1. 데이터셋 버전 관리
2. 데이터 변경 이력 추적
3. 데이터 롤백 지원
4. 데이터 비교 및 차이점 분석
"""

import json
import os
import hashlib
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import sqlite3

logger = logging.getLogger(__name__)


class DataVersionManager:
    """
    데이터 버전 관리 시스템
    
    [역할]
    - 데이터셋 버전 관리
    - 데이터 변경 이력 추적
    - 데이터 롤백 지원
    """
    
    def __init__(self, db_path: str = "data/data_versions.db"):
        """
        초기화
        
        Args:
            db_path: 데이터베이스 경로
        """
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_database()
        
        logger.info("✅ 데이터 버전 관리 시스템 초기화 완료")
    
    def _init_database(self):
        """데이터베이스 초기화"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 데이터셋 버전 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dataset_versions (
                    version_id TEXT PRIMARY KEY,
                    version_name TEXT NOT NULL,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_by TEXT,
                    metadata_json TEXT,
                    file_count INTEGER DEFAULT 0,
                    total_size_bytes INTEGER DEFAULT 0
                )
            ''')
            
            # 데이터 파일 버전 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_versions (
                    file_id TEXT PRIMARY KEY,
                    file_path TEXT NOT NULL,
                    version_id TEXT NOT NULL,
                    file_hash TEXT NOT NULL,
                    file_size_bytes INTEGER,
                    metadata_json TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (version_id) REFERENCES dataset_versions(version_id)
                )
            ''')
            
            # 변경 이력 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS change_history (
                    change_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version_id TEXT NOT NULL,
                    change_type TEXT NOT NULL,  -- 'add', 'modify', 'delete'
                    file_id TEXT,
                    description TEXT,
                    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    changed_by TEXT,
                    FOREIGN KEY (version_id) REFERENCES dataset_versions(version_id)
                )
            ''')
            
            # 인덱스 생성
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_versions_version ON file_versions(version_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_change_history_version ON change_history(version_id)')
            
            conn.commit()
    
    def create_version(self,
                      version_name: str,
                      description: str = "",
                      created_by: str = "system",
                      metadata: Optional[Dict] = None) -> str:
        """
        새 데이터셋 버전 생성
        
        Args:
            version_name: 버전 이름 (예: "v1.0.0", "baseline_2024_01")
            description: 버전 설명
            created_by: 생성자
            metadata: 추가 메타데이터
        
        Returns:
            version_id: 생성된 버전 ID
        """
        version_id = f"{version_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO dataset_versions 
                (version_id, version_name, description, created_by, metadata_json)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                version_id,
                version_name,
                description,
                created_by,
                json.dumps(metadata or {})
            ))
            conn.commit()
        
        logger.info(f"✅ 데이터셋 버전 생성: {version_id}")
        return version_id
    
    def add_file_to_version(self,
                           version_id: str,
                           file_path: str,
                           metadata: Optional[Dict] = None) -> str:
        """
        파일을 버전에 추가
        
        Args:
            version_id: 버전 ID
            file_path: 파일 경로
            metadata: 파일 메타데이터
        
        Returns:
            file_id: 파일 ID
        """
        # 파일 해시 계산
        file_hash = self._calculate_file_hash(file_path)
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        
        file_id = f"{version_id}_{file_hash[:8]}"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 파일 버전 추가
            cursor.execute('''
                INSERT OR REPLACE INTO file_versions
                (file_id, file_path, version_id, file_hash, file_size_bytes, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                file_id,
                file_path,
                version_id,
                file_hash,
                file_size,
                json.dumps(metadata or {})
            ))
            
            # 버전 파일 수 업데이트
            cursor.execute('''
                UPDATE dataset_versions
                SET file_count = (
                    SELECT COUNT(*) FROM file_versions WHERE version_id = ?
                ),
                total_size_bytes = (
                    SELECT SUM(file_size_bytes) FROM file_versions WHERE version_id = ?
                )
                WHERE version_id = ?
            ''', (version_id, version_id, version_id))
            
            # 변경 이력 추가
            cursor.execute('''
                INSERT INTO change_history
                (version_id, change_type, file_id, description, changed_by)
                VALUES (?, 'add', ?, '파일 추가', 'system')
            ''', (version_id, file_id))
            
            conn.commit()
        
        logger.debug(f"파일 추가: {file_path} → {version_id}")
        return file_id
    
    def get_version_info(self, version_id: str) -> Optional[Dict]:
        """
        버전 정보 조회
        
        Args:
            version_id: 버전 ID
        
        Returns:
            버전 정보 딕셔너리
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM dataset_versions WHERE version_id = ?
            ''', (version_id,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def list_versions(self) -> List[Dict]:
        """
        모든 버전 목록 조회
        
        Returns:
            버전 목록
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM dataset_versions
                ORDER BY created_at DESC
            ''')
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_version_files(self, version_id: str) -> List[Dict]:
        """
        버전에 포함된 파일 목록 조회
        
        Args:
            version_id: 버전 ID
        
        Returns:
            파일 목록
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM file_versions
                WHERE version_id = ?
                ORDER BY created_at
            ''', (version_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def compare_versions(self, version_id1: str, version_id2: str) -> Dict:
        """
        두 버전 비교
        
        Args:
            version_id1: 첫 번째 버전 ID
            version_id2: 두 번째 버전 ID
        
        Returns:
            비교 결과
        """
        files1 = {f['file_hash']: f for f in self.get_version_files(version_id1)}
        files2 = {f['file_hash']: f for f in self.get_version_files(version_id2)}
        
        common_files = set(files1.keys()) & set(files2.keys())
        only_in_v1 = set(files1.keys()) - set(files2.keys())
        only_in_v2 = set(files2.keys()) - set(files1.keys())
        
        return {
            'version1': version_id1,
            'version2': version_id2,
            'common_files_count': len(common_files),
            'only_in_v1_count': len(only_in_v1),
            'only_in_v2_count': len(only_in_v2),
            'common_files': list(common_files),
            'only_in_v1': list(only_in_v1),
            'only_in_v2': list(only_in_v2)
        }
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """
        파일 해시 계산 (SHA256)
        
        Args:
            file_path: 파일 경로
        
        Returns:
            파일 해시
        """
        if not os.path.exists(file_path):
            return ""
        
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        
        return sha256.hexdigest()


# 전역 인스턴스
data_version_manager = DataVersionManager()

