#!/usr/bin/env python3
"""
하이브리드 저장 서비스
- 이상 감지 시: 오디오 파일 + 분석 결과 + 특징 데이터 저장
- 정상 데이터: 통계만 저장 (용량 절감)
- AI 학습에 최적화된 데이터 수집
"""

import os
import sqlite3
import json
import numpy as np
import soundfile as sf
import librosa
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import hashlib
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridStorageService:
    """하이브리드 저장 서비스 - AI 학습 최적화 + 비용 절감"""
    
    def __init__(self, 
                 db_path: str = "data/hybrid_storage.db",
                 audio_storage_path: str = "data/audio_samples",
                 compression_level: str = "medium"):
        """
        하이브리드 저장 서비스 초기화
        
        Args:
            db_path: 데이터베이스 파일 경로
            audio_storage_path: 오디오 파일 저장 경로
            compression_level: 압축 레벨 ('low', 'medium', 'high')
        """
        self.db_path = db_path
        self.audio_storage_path = audio_storage_path
        self.compression_level = compression_level
        
        # 디렉토리 생성
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        os.makedirs(self.audio_storage_path, exist_ok=True)
        
        # 압축 설정
        self.compression_settings = {
            'low': {'bitrate': '192k', 'quality': 5},      # 고품질
            'medium': {'bitrate': '128k', 'quality': 4},  # 균형
            'high': {'bitrate': '64k', 'quality': 3}       # 고압축
        }
        
        self._init_database()
        logger.info("하이브리드 저장 서비스 초기화 완료")
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 이상 데이터 테이블 (오디오 파일 + 분석 결과)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS anomaly_samples (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        device_id TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        audio_file_path TEXT NOT NULL,
                        audio_file_size INTEGER,
                        is_anomaly BOOLEAN NOT NULL,
                        anomaly_type TEXT,  -- 'critical', 'warning', 'low_confidence'
                        confidence REAL NOT NULL,
                        risk_level TEXT NOT NULL,
                        analysis_result_json TEXT NOT NULL,
                        features_json TEXT NOT NULL,
                        quality_metrics_json TEXT,
                        file_hash TEXT UNIQUE,  -- 중복 방지
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 정상 데이터 통계 테이블 (용량 절감)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS normal_statistics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        device_id TEXT NOT NULL,
                        date DATE NOT NULL,
                        total_samples INTEGER DEFAULT 0,
                        avg_confidence REAL,
                        avg_quality_score REAL,
                        peak_quality_score REAL,
                        min_confidence REAL,
                        max_confidence REAL,
                        sample_times TEXT,  -- JSON 배열: 샘플링 시간들
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(device_id, date)
                    )
                ''')
                
                # 특징 데이터 샘플 테이블 (AI 학습용)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS feature_samples (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        device_id TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        is_anomaly BOOLEAN NOT NULL,
                        features_json TEXT NOT NULL,  -- 압축된 특징 데이터
                        confidence REAL,
                        quality_score REAL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 저장 통계 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS storage_statistics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date DATE NOT NULL,
                        device_id TEXT NOT NULL,
                        total_samples INTEGER DEFAULT 0,
                        anomaly_samples INTEGER DEFAULT 0,
                        normal_samples INTEGER DEFAULT 0,
                        audio_files_stored INTEGER DEFAULT 0,
                        total_storage_bytes INTEGER DEFAULT 0,
                        storage_cost_estimate REAL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(date, device_id)
                    )
                ''')
                
                # 인덱스 생성
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_anomaly_device_time ON anomaly_samples(device_id, timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_anomaly_type ON anomaly_samples(anomaly_type, risk_level)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_normal_device_date ON normal_statistics(device_id, date)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_features_device_time ON feature_samples(device_id, timestamp)')
                
                conn.commit()
                logger.info("하이브리드 저장 데이터베이스 초기화 완료")
                
        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
            raise
    
    def should_store_audio(self, analysis_result: Dict) -> Tuple[bool, str]:
        """
        오디오 파일 저장 여부 판단
        
        Returns:
            (should_store, reason): 저장 여부와 이유
        """
        # 이상 감지
        if analysis_result.get('is_anomaly', False):
            confidence = analysis_result.get('confidence', 0)
            if confidence > 0.9:
                return True, 'critical_anomaly'
            elif confidence > 0.7:
                return True, 'warning_anomaly'
            else:
                return True, 'low_confidence_anomaly'
        
        # 신뢰도가 낮은 경우 (불확실한 데이터 - AI 학습에 중요)
        confidence = analysis_result.get('confidence', 0)
        if confidence < 0.6:
            return True, 'low_confidence'
        
        # 품질이 낮은 경우
        quality_metrics = analysis_result.get('quality_metrics', {})
        overall_quality = quality_metrics.get('overall_quality', 100)
        if overall_quality < 30:
            return True, 'low_quality'
        
        # 정상 데이터는 오디오 파일 저장하지 않음
        return False, 'normal'
    
    def store_sample(self, 
                    device_id: str,
                    audio_data: np.ndarray,
                    sample_rate: int,
                    analysis_result: Dict,
                    features: Dict) -> Optional[Dict]:
        """
        샘플 저장 (하이브리드 방식)
        
        Args:
            device_id: 디바이스 ID
            audio_data: 오디오 데이터 (numpy array)
            sample_rate: 샘플링 레이트
            analysis_result: AI 분석 결과
            features: 추출된 특징 데이터
            
        Returns:
            저장 결과 정보 또는 None
        """
        try:
            # 저장 여부 판단
            should_store, reason = self.should_store_audio(analysis_result)
            
            if should_store:
                # 이상 데이터: 오디오 파일 + 분석 결과 저장
                return self._store_anomaly_sample(
                    device_id, audio_data, sample_rate, 
                    analysis_result, features, reason
                )
            else:
                # 정상 데이터: 통계만 업데이트
                self._update_normal_statistics(
                    device_id, analysis_result, features
                )
                return {
                    'stored': False,
                    'reason': reason,
                    'message': '정상 데이터 - 통계만 업데이트'
                }
                
        except Exception as e:
            logger.error(f"샘플 저장 실패: {e}")
            return None
    
    def _store_anomaly_sample(self,
                              device_id: str,
                              audio_data: np.ndarray,
                              sample_rate: int,
                              analysis_result: Dict,
                              features: Dict,
                              reason: str) -> Dict:
        """이상 샘플 저장 (오디오 파일 + 분석 결과)"""
        try:
            # 파일명 생성
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{device_id}_{timestamp}_{reason}.mp3"
            file_path = os.path.join(self.audio_storage_path, filename)
            
            # 디렉토리 생성
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 오디오 파일 저장 (MP3 압축)
            # librosa를 사용하여 WAV로 먼저 저장 후 MP3 변환
            temp_wav = file_path.replace('.mp3', '.wav')
            sf.write(temp_wav, audio_data, sample_rate)
            
            # MP3 변환 (pydub 사용, 없으면 WAV 유지)
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_wav(temp_wav)
                bitrate = self.compression_settings[self.compression_level]['bitrate']
                audio.export(file_path, format="mp3", bitrate=bitrate)
                os.remove(temp_wav)  # 임시 WAV 파일 삭제
                file_format = 'mp3'
            except ImportError:
                # pydub가 없으면 WAV 유지
                file_path = temp_wav
                file_format = 'wav'
                logger.warning("pydub가 설치되지 않아 WAV 형식으로 저장합니다.")
            
            # 파일 크기
            file_size = os.path.getsize(file_path)
            
            # 파일 해시 (중복 방지)
            file_hash = self._calculate_file_hash(file_path)
            
            # 특징 데이터 압축
            compressed_features = self._compress_features(features)
            
            # 데이터베이스에 저장
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 이상 데이터 저장
                cursor.execute('''
                    INSERT INTO anomaly_samples 
                    (device_id, audio_file_path, audio_file_size, is_anomaly,
                     anomaly_type, confidence, risk_level, analysis_result_json,
                     features_json, quality_metrics_json, file_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    device_id,
                    file_path,
                    file_size,
                    analysis_result.get('is_anomaly', False),
                    reason,
                    analysis_result.get('confidence', 0),
                    self._calculate_risk_level(analysis_result),
                    json.dumps(analysis_result, ensure_ascii=False),
                    json.dumps(compressed_features, ensure_ascii=False),
                    json.dumps(analysis_result.get('quality_metrics', {}), ensure_ascii=False),
                    file_hash
                ))
                
                anomaly_id = cursor.lastrowid
                
                # 특징 데이터 샘플 저장 (AI 학습용)
                self._store_feature_sample(
                    cursor, device_id, compressed_features,
                    analysis_result.get('is_anomaly', False),
                    analysis_result.get('confidence', 0),
                    analysis_result.get('quality_metrics', {}).get('overall_quality', 0)
                )
                
                # 저장 통계 업데이트
                self._update_storage_statistics(cursor, device_id, file_size, True)
                
                conn.commit()
            
            logger.info(f"이상 샘플 저장 완료: {device_id} - {reason} ({file_size} bytes)")
            
            return {
                'stored': True,
                'reason': reason,
                'anomaly_id': anomaly_id,
                'file_path': file_path,
                'file_size': file_size,
                'file_format': file_format,
                'message': f'이상 데이터 저장 완료: {reason}'
            }
            
        except Exception as e:
            logger.error(f"이상 샘플 저장 실패: {e}")
            return None
    
    def _update_normal_statistics(self,
                                  device_id: str,
                                  analysis_result: Dict,
                                  features: Dict):
        """정상 데이터 통계 업데이트 (용량 절감)"""
        try:
            today = datetime.now().date()
            confidence = analysis_result.get('confidence', 0)
            quality_metrics = analysis_result.get('quality_metrics', {})
            overall_quality = quality_metrics.get('overall_quality', 0)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 오늘의 통계 조회
                cursor.execute('''
                    SELECT * FROM normal_statistics 
                    WHERE device_id = ? AND date = ?
                ''', (device_id, today))
                
                existing = cursor.fetchone()
                
                if existing:
                    # 기존 통계 업데이트
                    total = existing[2] + 1
                    avg_conf = (existing[3] * existing[2] + confidence) / total
                    avg_qual = (existing[4] * existing[2] + overall_quality) / total
                    peak_qual = max(existing[5], overall_quality)
                    min_conf = min(existing[6], confidence)
                    max_conf = max(existing[7], confidence)
                    
                    # 샘플 시간 추가
                    sample_times = json.loads(existing[8]) if existing[8] else []
                    sample_times.append(datetime.now().isoformat())
                    # 최근 100개만 유지
                    if len(sample_times) > 100:
                        sample_times = sample_times[-100:]
                    
                    cursor.execute('''
                        UPDATE normal_statistics 
                        SET total_samples = ?,
                            avg_confidence = ?,
                            avg_quality_score = ?,
                            peak_quality_score = ?,
                            min_confidence = ?,
                            max_confidence = ?,
                            sample_times = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE device_id = ? AND date = ?
                    ''', (
                        total, avg_conf, avg_qual, peak_qual,
                        min_conf, max_conf, json.dumps(sample_times),
                        device_id, today
                    ))
                else:
                    # 새로운 통계 생성
                    cursor.execute('''
                        INSERT INTO normal_statistics 
                        (device_id, date, total_samples, avg_confidence,
                         avg_quality_score, peak_quality_score,
                         min_confidence, max_confidence, sample_times)
                        VALUES (?, ?, 1, ?, ?, ?, ?, ?, ?)
                    ''', (
                        device_id, today, confidence, overall_quality,
                        overall_quality, confidence, confidence,
                        json.dumps([datetime.now().isoformat()])
                    ))
                
                # 특징 데이터 샘플 저장 (정상 데이터도 일부 저장 - AI 학습용)
                # 10% 확률로 저장 (용량 절감)
                import random
                if random.random() < 0.1:
                    compressed_features = self._compress_features(features)
                    self._store_feature_sample(
                        cursor, device_id, compressed_features,
                        False, confidence, overall_quality
                    )
                
                # 저장 통계 업데이트
                self._update_storage_statistics(cursor, device_id, 0, False)
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"정상 통계 업데이트 실패: {e}")
    
    def _store_feature_sample(self,
                              cursor,
                              device_id: str,
                              features: Dict,
                              is_anomaly: bool,
                              confidence: float,
                              quality_score: float):
        """특징 데이터 샘플 저장 (AI 학습용)"""
        try:
            cursor.execute('''
                INSERT INTO feature_samples 
                (device_id, is_anomaly, features_json, confidence, quality_score)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                device_id,
                is_anomaly,
                json.dumps(features, ensure_ascii=False),
                confidence,
                quality_score
            ))
        except Exception as e:
            logger.error(f"특징 데이터 샘플 저장 실패: {e}")
    
    def _update_storage_statistics(self,
                                   cursor,
                                   device_id: str,
                                   file_size: int,
                                   is_anomaly: bool):
        """저장 통계 업데이트"""
        try:
            today = datetime.now().date()
            
            cursor.execute('''
                SELECT * FROM storage_statistics 
                WHERE date = ? AND device_id = ?
            ''', (today, device_id))
            
            existing = cursor.fetchone()
            
            if existing:
                # 기존 통계 업데이트
                total = existing[2] + 1
                anomaly = existing[3] + (1 if is_anomaly else 0)
                normal = existing[4] + (0 if is_anomaly else 1)
                audio_files = existing[5] + (1 if is_anomaly and file_size > 0 else 0)
                total_bytes = existing[6] + file_size
                cost_estimate = total_bytes * 0.08 / (1024 ** 3)  # $0.08/GB/월
                
                cursor.execute('''
                    UPDATE storage_statistics 
                    SET total_samples = ?,
                        anomaly_samples = ?,
                        normal_samples = ?,
                        audio_files_stored = ?,
                        total_storage_bytes = ?,
                        storage_cost_estimate = ?
                    WHERE date = ? AND device_id = ?
                ''', (
                    total, anomaly, normal, audio_files,
                    total_bytes, cost_estimate, today, device_id
                ))
            else:
                # 새로운 통계 생성
                cost_estimate = file_size * 0.08 / (1024 ** 3)
                cursor.execute('''
                    INSERT INTO storage_statistics 
                    (date, device_id, total_samples, anomaly_samples,
                     normal_samples, audio_files_stored, total_storage_bytes,
                     storage_cost_estimate)
                    VALUES (?, ?, 1, ?, ?, ?, ?, ?)
                ''', (
                    today, device_id,
                    1 if is_anomaly else 0,
                    0 if is_anomaly else 1,
                    1 if is_anomaly and file_size > 0 else 0,
                    file_size, cost_estimate
                ))
                
        except Exception as e:
            logger.error(f"저장 통계 업데이트 실패: {e}")
    
    def _compress_features(self, features: Dict) -> Dict:
        """특징 데이터 압축"""
        compressed = {}
        
        for key, value in features.items():
            if isinstance(value, (list, np.ndarray)):
                if isinstance(value, list):
                    value = np.array(value)
                
                # float64 → float32 변환 (용량 절반)
                if value.dtype == np.float64:
                    value = value.astype(np.float32)
                
                compressed[key] = {
                    'data': value.tolist(),
                    'shape': list(value.shape),
                    'dtype': str(value.dtype)
                }
            else:
                compressed[key] = value
        
        return compressed
    
    def _calculate_risk_level(self, analysis_result: Dict) -> str:
        """위험도 계산"""
        confidence = analysis_result.get('confidence', 0)
        is_anomaly = analysis_result.get('is_anomaly', False)
        quality_metrics = analysis_result.get('quality_metrics', {})
        overall_quality = quality_metrics.get('overall_quality', 100)
        
        if is_anomaly and confidence > 0.9:
            return 'critical'
        elif is_anomaly or confidence < 0.6 or overall_quality < 20:
            return 'high'
        elif confidence < 0.8 or overall_quality < 40:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """파일 해시 계산 (중복 방지)"""
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            return file_hash
        except Exception as e:
            logger.error(f"파일 해시 계산 실패: {e}")
            return hashlib.md5(file_path.encode()).hexdigest()
    
    def get_storage_stats(self, device_id: str = None, days: int = 7) -> Dict:
        """저장 통계 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                start_date = datetime.now().date() - timedelta(days=days)
                
                if device_id:
                    cursor.execute('''
                        SELECT 
                            SUM(total_samples) as total,
                            SUM(anomaly_samples) as anomaly,
                            SUM(normal_samples) as normal,
                            SUM(audio_files_stored) as audio_files,
                            SUM(total_storage_bytes) as total_bytes,
                            AVG(storage_cost_estimate) as avg_cost
                        FROM storage_statistics
                        WHERE device_id = ? AND date >= ?
                    ''', (device_id, start_date))
                else:
                    cursor.execute('''
                        SELECT 
                            SUM(total_samples) as total,
                            SUM(anomaly_samples) as anomaly,
                            SUM(normal_samples) as normal,
                            SUM(audio_files_stored) as audio_files,
                            SUM(total_storage_bytes) as total_bytes,
                            AVG(storage_cost_estimate) as avg_cost
                        FROM storage_statistics
                        WHERE date >= ?
                    ''', (start_date,))
                
                row = cursor.fetchone()
                
                if row and row[0]:
                    total_bytes = row[4] or 0
                    return {
                        'total_samples': row[0] or 0,
                        'anomaly_samples': row[1] or 0,
                        'normal_samples': row[2] or 0,
                        'audio_files_stored': row[3] or 0,
                        'total_storage_bytes': total_bytes,
                        'total_storage_mb': total_bytes / (1024 ** 2),
                        'total_storage_gb': total_bytes / (1024 ** 3),
                        'estimated_monthly_cost': row[5] or 0,
                        'storage_efficiency': f"{(row[2] or 0) / max(row[0] or 1, 1) * 100:.1f}% 정상 데이터는 통계만 저장"
                    }
                else:
                    return {
                        'total_samples': 0,
                        'anomaly_samples': 0,
                        'normal_samples': 0,
                        'audio_files_stored': 0,
                        'total_storage_bytes': 0,
                        'total_storage_mb': 0,
                        'total_storage_gb': 0,
                        'estimated_monthly_cost': 0,
                        'storage_efficiency': '0%'
                    }
                    
        except Exception as e:
            logger.error(f"저장 통계 조회 실패: {e}")
            return {}
    
    def get_anomaly_samples(self, device_id: str = None, limit: int = 100) -> List[Dict]:
        """이상 샘플 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if device_id:
                    cursor.execute('''
                        SELECT * FROM anomaly_samples 
                        WHERE device_id = ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                    ''', (device_id, limit))
                else:
                    cursor.execute('''
                        SELECT * FROM anomaly_samples 
                        ORDER BY timestamp DESC
                        LIMIT ?
                    ''', (limit,))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'id': row[0],
                        'device_id': row[1],
                        'timestamp': row[2],
                        'audio_file_path': row[3],
                        'audio_file_size': row[4],
                        'is_anomaly': bool(row[5]),
                        'anomaly_type': row[6],
                        'confidence': row[7],
                        'risk_level': row[8],
                        'analysis_result': json.loads(row[9]) if row[9] else {},
                        'features': json.loads(row[10]) if row[10] else {},
                        'quality_metrics': json.loads(row[11]) if row[11] else {}
                    })
                
                return results
                
        except Exception as e:
            logger.error(f"이상 샘플 조회 실패: {e}")
            return []
    
    def get_feature_samples_for_training(self, 
                                        limit: int = 1000,
                                        anomaly_ratio: float = 0.3) -> List[Dict]:
        """AI 학습용 특징 데이터 샘플 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 이상 샘플 수 계산
                anomaly_limit = int(limit * anomaly_ratio)
                normal_limit = limit - anomaly_limit
                
                # 이상 샘플 조회
                cursor.execute('''
                    SELECT device_id, is_anomaly, features_json, confidence, quality_score, timestamp
                    FROM feature_samples
                    WHERE is_anomaly = 1
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (anomaly_limit,))
                
                anomaly_samples = []
                for row in cursor.fetchall():
                    anomaly_samples.append({
                        'device_id': row[0],
                        'is_anomaly': bool(row[1]),
                        'features': json.loads(row[2]) if row[2] else {},
                        'confidence': row[3],
                        'quality_score': row[4],
                        'timestamp': row[5]
                    })
                
                # 정상 샘플 조회
                cursor.execute('''
                    SELECT device_id, is_anomaly, features_json, confidence, quality_score, timestamp
                    FROM feature_samples
                    WHERE is_anomaly = 0
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (normal_limit,))
                
                normal_samples = []
                for row in cursor.fetchall():
                    normal_samples.append({
                        'device_id': row[0],
                        'is_anomaly': bool(row[1]),
                        'features': json.loads(row[2]) if row[2] else {},
                        'confidence': row[3],
                        'quality_score': row[4],
                        'timestamp': row[5]
                    })
                
                # 합치기
                return anomaly_samples + normal_samples
                
        except Exception as e:
            logger.error(f"학습용 특징 데이터 조회 실패: {e}")
            return []

# 전역 인스턴스
hybrid_storage_service = HybridStorageService()

