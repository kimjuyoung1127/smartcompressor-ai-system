#!/usr/bin/env python3
"""
24시간 범용 모니터링 서비스 (Universal Monitoring Service)
지금까지 논의한 알고리즘을 통합한 24시간 모니터링 시스템

핵심 기능:
1. 데시벨 기반 1차 필터링
2. 스펙트럼 이상 점수 방식 (실시간 고장 신호 감지)
3. 범용 모델 (모든 압축기에 공통 적용)
4. 하이브리드 저장 (이상만 WAV 저장, 정상은 통계만)
5. 냉매 누출, 증발기 성에 등 다양한 고장 유형 감지
"""

import os
import time
import threading
import logging
import sqlite3
import json
import numpy as np
import soundfile as sf
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from services.universal_anomaly_detector_v2 import UniversalAnomalyDetectorV2 as UniversalAnomalyDetector
from services.hybrid_storage_service import HybridStorageService
from services.performance_optimizer import PerformanceOptimizer

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UniversalMonitoringService:
    """
    24시간 범용 모니터링 서비스
    
    특징:
    - 모든 압축기에 공통 적용 가능
    - 실시간 고장 신호 감지
    - 하이브리드 저장 (비용 절감)
    - 다양한 고장 유형 감지
    """
    
    def __init__(self,
                 db_path: str = "data/universal_monitoring.db",
                 check_interval: int = 300,  # 5분 간격
                 baseline_samples_required: int = 100,  # 기준선 설정에 필요한 샘플 수
                 enable_parallel: bool = True,  # 병렬 처리 활성화
                 max_workers: int = 4):  # 병렬 처리 최대 워커 수
        """
        Args:
            db_path: 데이터베이스 파일 경로
            check_interval: 체크 간격 (초)
            baseline_samples_required: 기준선 설정에 필요한 샘플 수
            enable_parallel: 병렬 처리 활성화 여부
            max_workers: 병렬 처리 최대 워커 수
        """
        self.db_path = db_path
        self.check_interval = check_interval
        self.baseline_samples_required = baseline_samples_required
        self.enable_parallel = enable_parallel
        
        self.is_running = False
        self.monitoring_thread = None
        self.device_id = "default"
        
        # 범용 이상 감지기
        self.detector = UniversalAnomalyDetector()
        
        # 하이브리드 저장 서비스
        self.storage_service = HybridStorageService()
        
        # 성능 최적화 모듈
        self.performance_optimizer = PerformanceOptimizer(max_workers=max_workers)
        
        # 기준선 설정 상태
        self.baseline_established = False
        self.baseline_samples = []
        
        # 데이터베이스 초기화
        self._init_database()
        
        logger.info("✅ 24시간 범용 모니터링 서비스 초기화 완료")
        logger.info(f"   - 병렬 처리: {'활성화' if enable_parallel else '비활성화'} (워커 수: {max_workers})")
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 모니터링 기록 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monitoring_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    device_id TEXT NOT NULL,
                    decibel_level REAL,
                    is_anomaly BOOLEAN,
                    anomaly_score REAL,
                    anomaly_type TEXT,
                    confidence REAL,
                    failure_type TEXT,
                    features_json TEXT,
                    audio_file_path TEXT,
                    stored_reason TEXT
                )
            ''')
            
            # 기준선 기록 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS baseline_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    device_id TEXT NOT NULL,
                    baseline_json TEXT,
                    sample_count INTEGER
                )
            ''')
            
            # 통계 요약 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS statistics_summary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    device_id TEXT NOT NULL,
                    total_samples INTEGER DEFAULT 0,
                    anomaly_samples INTEGER DEFAULT 0,
                    normal_samples INTEGER DEFAULT 0,
                    audio_files_stored INTEGER DEFAULT 0,
                    UNIQUE(date, device_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ 데이터베이스 초기화 오류: {e}")
    
    def establish_baseline(self, audio_samples: List[np.ndarray], device_id: str = "default") -> Dict:
        """
        기준선 설정 (초기 1-2일)
        
        Args:
            audio_samples: 정상 상태 오디오 샘플 리스트
            device_id: 디바이스 ID
        
        Returns:
            기준선 딕셔너리
        """
        logger.info(f"📊 기준선 설정 시작 ({len(audio_samples)}개 샘플)")
        
        baseline = self.detector.establish_baseline(audio_samples)
        self.baseline_established = True
        
        # 기준선 저장
        baseline_file = f"data/baselines/{device_id}_baseline.json"
        os.makedirs(os.path.dirname(baseline_file), exist_ok=True)
        self.detector.save_baseline(baseline_file)
        
        # 데이터베이스에 기록
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO baseline_history (device_id, baseline_json, sample_count)
                VALUES (?, ?, ?)
            ''', (device_id, json.dumps(baseline), len(audio_samples)))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"기준선 저장 오류: {e}")
        
        logger.info("✅ 기준선 설정 완료")
        return baseline
    
    def start_monitoring(self, device_id: str = "default"):
        """모니터링 시작"""
        if self.is_running:
            logger.warning("⚠️ 모니터링이 이미 실행 중입니다.")
            return
        
        if not self.baseline_established:
            logger.warning("⚠️ 기준선이 설정되지 않았습니다. 기준선 설정 후 모니터링을 시작하세요.")
            return
        
        self.is_running = True
        self.device_id = device_id
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        logger.info(f"🚀 24시간 모니터링 서비스 시작 (디바이스: {device_id})")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.is_running = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        
        # 성능 최적화 모듈 종료
        self.performance_optimizer.shutdown()
        
        logger.info("⏹️ 24시간 모니터링 서비스 중지")
    
    def get_performance_stats(self) -> Dict:
        """
        성능 통계 반환
        
        Returns:
            성능 통계 딕셔너리
        """
        return self.performance_optimizer.get_stats()
    
    def _monitoring_loop(self):
        """모니터링 루프"""
        while self.is_running:
            try:
                # 실제 환경에서는 ESP32 센서에서 데이터를 받아옴
                # 여기서는 시뮬레이션용으로 처리
                self._process_sensor_data()
                
                # 다음 체크까지 대기
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"❌ 모니터링 루프 오류: {e}")
                time.sleep(10)  # 오류 시 10초 대기
    
    def _process_sensor_data(self):
        """센서 데이터 처리 (단일 센서)"""
        try:
            # 실제 환경에서는 ESP32에서 오디오 데이터와 데시벨 레벨을 받아옴
            # 여기서는 시뮬레이션용으로 생성
            audio_data, decibel_level = self._simulate_sensor_data()
            
            # 성능 최적화: 캐싱을 사용한 특징 추출
            # (detect_anomaly 내부에서 처리되므로 여기서는 직접 호출)
            result = self._process_single_sensor(audio_data, decibel_level, self.device_id)
            
            if result:
                # 3단계: 하이브리드 저장
                storage_result = self._hybrid_storage(result, audio_data, decibel_level)
                
                # 4단계: 데이터베이스 저장
                self._save_monitoring_result(result, storage_result)
                
            # 5단계: 이상 감지 시 알림
            if result['is_anomaly']:
                self._handle_anomaly_alert(result)
            
            # 6단계: 실시간 대시보드에 데이터 브로드캐스트
            realtime_dashboard_service.broadcast_data(result)
            
        except Exception as e:
            logger.error(f"❌ 센서 데이터 처리 오류: {e}")
    
    def _process_single_sensor(self, audio_data: np.ndarray, decibel_level: float, device_id: str) -> Optional[Dict]:
        """
        단일 센서 데이터 처리 (캐싱 최적화 포함)
        
        Args:
            audio_data: 오디오 데이터
            decibel_level: 데시벨 레벨
            device_id: 디바이스 ID
        
        Returns:
            처리 결과 또는 None
        """
        # 1단계: 데시벨 기반 1차 필터링
        decibel_result = self.detector.decibel_filter.filter(decibel_level)
        
        if decibel_result['action'] == 'skip':
            # 소리 없음 → 저장하지 않음
            logger.debug(f"소리 없음 (데시벨: {decibel_level:.1f}dB)")
            return None
        
        if decibel_result['action'] == 'update_statistics_only':
            # 정상 (낮은 소리) → 통계만 업데이트
            self._update_statistics_only(decibel_level)
            return None
        
        # 2단계: 특징 추출 (캐싱 사용)
        features = self.performance_optimizer.extract_features_cached(
            audio_data,
            self.detector.feature_extractor
        )
        
        if not features:
            return None
        
        # 3단계: 스펙트럼 이상 점수 계산
        baseline = self.detector.baseline_manager.get_baseline()
        if not baseline:
            return None
        
        anomaly_score_result = self.detector.anomaly_scorer.calculate(features, baseline)
        
        # 4단계: 고장 유형 분류
        failure_type = self.detector.failure_classifier.classify(features, anomaly_score_result)
        
        result = {
            'is_anomaly': anomaly_score_result['is_anomaly'],
            'confidence': anomaly_score_result['confidence'],
            'message': '고장 신호 감지!' if anomaly_score_result['is_anomaly'] else '정상',
            'anomaly_type': failure_type,
            'anomaly_score': anomaly_score_result['total_score'],
            'individual_scores': anomaly_score_result['individual_scores'],
            'features': features,
            'decibel_level': decibel_level,
            'device_id': device_id,
            'timestamp': datetime.now().isoformat()
        }
        
        return result
    
    def process_multiple_sensors(self, sensor_data_list: List[Tuple[np.ndarray, float, str]]) -> List[Dict]:
        """
        여러 센서 데이터 병렬 처리
        
        [성능 최적화]
        - 병렬 처리: 여러 센서 동시 처리
        - 캐싱: 동일한 오디오 재계산 방지
        
        Args:
            sensor_data_list: 센서 데이터 리스트
                - 예: [(audio1, decibel1, device1), (audio2, decibel2, device2), ...]
        
        Returns:
            처리 결과 리스트
        """
        if not self.enable_parallel or len(sensor_data_list) == 1:
            # 병렬 처리 비활성화 또는 단일 센서: 순차 처리
            results = []
            for audio_data, decibel_level, device_id in sensor_data_list:
                result = self._process_single_sensor(audio_data, decibel_level, device_id)
                if result:
                    results.append(result)
            return results
        
        # 병렬 처리
        def detection_wrapper(audio_data, decibel_level):
            """병렬 처리를 위한 래퍼 함수"""
            return self._process_single_sensor(audio_data, decibel_level, "parallel")
        
        results = self.performance_optimizer.process_parallel(
            sensor_data_list,
            lambda audio, decibel, device: detection_wrapper(audio, decibel)
        )
        
        return results
    
    def _simulate_sensor_data(self) -> tuple:
        """
        센서 데이터 시뮬레이션 (실제 환경에서는 ESP32에서 받아옴)
        
        Returns:
            (audio_data, decibel_level)
        """
        duration = 5  # 5초
        sr = 16000
        t = np.linspace(0, duration, int(sr * duration))
        
        # 랜덤하게 정상/이상 생성
        if np.random.random() < 0.1:  # 10% 확률로 이상
            # 이상 소음 (고주파 + 불규칙)
            anomaly_freq = 120 + np.random.random() * 100
            audio_data = np.sin(2 * np.pi * anomaly_freq * t) * 0.8
            decibel_level = 55 + np.random.random() * 10  # 55-65dB
        else:
            # 정상 소음
            normal_freq = 60
            audio_data = np.sin(2 * np.pi * normal_freq * t) * 0.5
            decibel_level = 45 + np.random.random() * 5  # 45-50dB
        
        # 노이즈 추가
        noise = np.random.normal(0, 0.1, len(audio_data))
        audio_data = audio_data + noise
        
        return audio_data, decibel_level
    
    def _hybrid_storage(self, result: Dict, audio_data: np.ndarray, decibel_level: float) -> Dict:
        """
        하이브리드 저장
        
        - 이상 감지 시: WAV 파일 + 분석 결과 + 특징 데이터 저장
        - 정상 데이터: 통계만 저장
        """
        try:
            # 특징은 이미 result에 포함되어 있음 (캐싱 최적화)
            features = result.get('features', {})
            
            # 하이브리드 저장 서비스에 전달
            device_id = result.get('device_id', self.device_id)
            storage_result = self.storage_service.store_sample(
                device_id=device_id,
                audio_data=audio_data,
                sample_rate=self.detector.sample_rate,
                analysis_result=result,
                features=features
            )
            
            return storage_result
            
        except Exception as e:
            logger.error(f"하이브리드 저장 오류: {e}")
            return {'stored': False, 'reason': 'error'}
    
    def _update_statistics_only(self, decibel_level: float):
        """정상 데이터 통계만 업데이트"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = datetime.now().date()
            cursor.execute('''
                INSERT INTO statistics_summary 
                (date, device_id, total_samples, normal_samples)
                VALUES (?, ?, 1, 1)
                ON CONFLICT(date, device_id) DO UPDATE SET
                    total_samples = total_samples + 1,
                    normal_samples = normal_samples + 1
            ''', (today, self.device_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"통계 업데이트 오류: {e}")
    
    def _save_monitoring_result(self, result: Dict, storage_result: Dict):
        """모니터링 결과 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO monitoring_logs 
                (device_id, decibel_level, is_anomaly, anomaly_score, 
                 anomaly_type, confidence, failure_type, features_json, 
                 audio_file_path, stored_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.device_id,
                result.get('decibel_level'),
                result.get('is_anomaly', False),
                result.get('anomaly_score', 0.0),
                result.get('anomaly_type', 'unknown'),
                result.get('confidence', 0.0),
                result.get('anomaly_type', 'unknown'),
                json.dumps(result.get('features', {})),
                storage_result.get('file_path'),
                storage_result.get('reason', 'normal')
            ))
            
            # 통계 업데이트
            today = datetime.now().date()
            if result.get('is_anomaly', False):
                cursor.execute('''
                    INSERT INTO statistics_summary 
                    (date, device_id, total_samples, anomaly_samples, audio_files_stored)
                    VALUES (?, ?, 1, 1, 1)
                    ON CONFLICT(date, device_id) DO UPDATE SET
                        total_samples = total_samples + 1,
                        anomaly_samples = anomaly_samples + 1,
                        audio_files_stored = audio_files_stored + 1
                ''', (today, self.device_id))
            else:
                cursor.execute('''
                    INSERT INTO statistics_summary 
                    (date, device_id, total_samples, normal_samples)
                    VALUES (?, ?, 1, 1)
                    ON CONFLICT(date, device_id) DO UPDATE SET
                        total_samples = total_samples + 1,
                        normal_samples = normal_samples + 1
                ''', (today, self.device_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"모니터링 결과 저장 오류: {e}")
    
    def _handle_anomaly_alert(self, result: Dict):
        """이상 감지 시 알림 처리"""
        logger.warning(f"⚠️ 고장 신호 감지!")
        logger.warning(f"   - 고장 유형: {result.get('anomaly_type', 'unknown')}")
        logger.warning(f"   - 이상 점수: {result.get('anomaly_score', 0.0):.2%}")
        logger.warning(f"   - 신뢰도: {result.get('confidence', 0.0):.2%}")
        
        # 실제 환경에서는 여기서 알림 전송 (이메일, SMS, 푸시 등)
        # 예: send_alert(result)

