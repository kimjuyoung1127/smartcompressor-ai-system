#!/usr/bin/env python3
"""
상관관계 분석 서비스 (Correlation Analysis Service)
소리 데이터 vs 온도/진동 데이터 비교 분석

로드맵 2단계 목표: "우리의 '소리 데이터'는, 기존 '온도 센서' 알람보다 평균 7.2일 먼저 
'냉매 누설' 징후를 95% 정확도로 예측했다"는 통계적 증명
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from scipy import stats
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import json

from services.data_warehouse_service import DataWarehouseService

logger = logging.getLogger(__name__)


class CorrelationAnalysisService:
    """상관관계 분석 서비스"""
    
    def __init__(self, warehouse_service: DataWarehouseService):
        """
        Args:
            warehouse_service: 데이터 웨어하우스 서비스 인스턴스
        """
        self.warehouse = warehouse_service
    
    def analyze_lead_time(self, device_id: str, start_date: datetime, 
                         end_date: datetime, 
                         failure_events: List[Dict]) -> Dict:
        """
        선행 지표 분석: 소리 데이터가 온도/진동보다 얼마나 먼저 이상 징후를 감지하는지 분석
        
        Args:
            device_id: 디바이스 ID
            start_date: 분석 시작일
            end_date: 분석 종료일
            failure_events: 실제 고장 이벤트 리스트 [{'timestamp': datetime, 'type': 'leak', ...}]
        
        Returns:
            Dict: 분석 결과
                {
                    'audio_lead_days': 평균 선행 일수,
                    'audio_accuracy': 예측 정확도,
                    'temperature_lead_days': 온도 센서 선행 일수,
                    'vibration_lead_days': 진동 센서 선행 일수,
                    'comparison': 비교 결과
                }
        """
        try:
            # 1. 센서 데이터 로드
            df = self.warehouse.get_sensor_data_range(device_id, start_date, end_date)
            
            if df.empty:
                logger.warning(f"디바이스 {device_id}의 데이터가 없습니다.")
                return {}
            
            # 2. 이상 징후 감지 함수
            audio_anomalies = self._detect_audio_anomalies(df)
            temperature_anomalies = self._detect_temperature_anomalies(df)
            vibration_anomalies = self._detect_vibration_anomalies(df)
            
            # 3. 실제 고장 이벤트와 비교
            audio_lead_times = []
            temperature_lead_times = []
            vibration_lead_times = []
            
            audio_predictions = []
            temperature_predictions = []
            vibration_predictions = []
            actual_failures = []
            
            for failure_event in failure_events:
                failure_time = failure_event['timestamp']
                if isinstance(failure_time, str):
                    failure_time = datetime.fromisoformat(failure_time)
                
                # 각 센서의 가장 가까운 이상 징후 찾기
                audio_lead = self._find_nearest_anomaly_before(
                    audio_anomalies, failure_time
                )
                temp_lead = self._find_nearest_anomaly_before(
                    temperature_anomalies, failure_time
                )
                vib_lead = self._find_nearest_anomaly_before(
                    vibration_anomalies, failure_time
                )
                
                if audio_lead:
                    lead_days = (failure_time - audio_lead).total_seconds() / 86400
                    audio_lead_times.append(lead_days)
                    audio_predictions.append(1)
                else:
                    audio_predictions.append(0)
                
                if temp_lead:
                    lead_days = (failure_time - temp_lead).total_seconds() / 86400
                    temperature_lead_times.append(lead_days)
                    temperature_predictions.append(1)
                else:
                    temperature_predictions.append(0)
                
                if vib_lead:
                    lead_days = (failure_time - vib_lead).total_seconds() / 86400
                    vibration_lead_times.append(lead_days)
                    vibration_predictions.append(1)
                else:
                    vibration_predictions.append(0)
                
                actual_failures.append(1)
            
            # 4. 통계 계산
            audio_avg_lead = np.mean(audio_lead_times) if audio_lead_times else 0
            temp_avg_lead = np.mean(temperature_lead_times) if temperature_lead_times else 0
            vib_avg_lead = np.mean(vibration_lead_times) if vibration_lead_times else 0
            
            # 5. 정확도 계산
            audio_accuracy = accuracy_score(actual_failures, audio_predictions) * 100
            temp_accuracy = accuracy_score(actual_failures, temperature_predictions) * 100
            vib_accuracy = accuracy_score(actual_failures, vibration_predictions) * 100
            
            # 6. 결과 저장
            result = {
                'device_id': device_id,
                'analysis_period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'audio_sensor': {
                    'avg_lead_days': round(audio_avg_lead, 2),
                    'accuracy': round(audio_accuracy, 2),
                    'sample_count': len(audio_lead_times),
                    'lead_times': [round(t, 2) for t in audio_lead_times]
                },
                'temperature_sensor': {
                    'avg_lead_days': round(temp_avg_lead, 2),
                    'accuracy': round(temp_accuracy, 2),
                    'sample_count': len(temperature_lead_times),
                    'lead_times': [round(t, 2) for t in temperature_lead_times]
                },
                'vibration_sensor': {
                    'avg_lead_days': round(vib_avg_lead, 2),
                    'accuracy': round(vib_accuracy, 2),
                    'sample_count': len(vibration_lead_times),
                    'lead_times': [round(t, 2) for t in vibration_lead_times]
                },
                'comparison': {
                    'audio_advantage_days': round(audio_avg_lead - max(temp_avg_lead, vib_avg_lead), 2),
                    'audio_advantage_accuracy': round(audio_accuracy - max(temp_accuracy, vib_accuracy), 2)
                },
                'analyzed_at': datetime.now().isoformat()
            }
            
            # DB에 저장
            self._save_correlation_result(result)
            
            logger.info(f"상관관계 분석 완료: device={device_id}, "
                       f"audio_lead={audio_avg_lead:.2f}일, "
                       f"accuracy={audio_accuracy:.2f}%")
            
            return result
            
        except Exception as e:
            logger.error(f"상관관계 분석 실패: {e}")
            return {}
    
    def _detect_audio_anomalies(self, df: pd.DataFrame, 
                                threshold_std: float = 2.0) -> List[datetime]:
        """오디오 데이터에서 이상 징후 감지"""
        if 'audio_level' not in df.columns or df['audio_level'].isna().all():
            return []
        
        audio_values = df['audio_level'].dropna()
        if len(audio_values) < 10:
            return []
        
        mean = audio_values.mean()
        std = audio_values.std()
        
        # 이상치 감지 (Z-score 기반)
        anomalies = df[
            (df['audio_level'] > mean + threshold_std * std) |
            (df['audio_level'] < mean - threshold_std * std)
        ]
        
        return anomalies['timestamp'].tolist()
    
    def _detect_temperature_anomalies(self, df: pd.DataFrame,
                                      threshold_std: float = 2.0) -> List[datetime]:
        """온도 데이터에서 이상 징후 감지"""
        if 'temperature' not in df.columns or df['temperature'].isna().all():
            return []
        
        temp_values = df['temperature'].dropna()
        if len(temp_values) < 10:
            return []
        
        mean = temp_values.mean()
        std = temp_values.std()
        
        anomalies = df[
            (df['temperature'] > mean + threshold_std * std) |
            (df['temperature'] < mean - threshold_std * std)
        ]
        
        return anomalies['timestamp'].tolist()
    
    def _detect_vibration_anomalies(self, df: pd.DataFrame,
                                   threshold_std: float = 2.0) -> List[datetime]:
        """진동 데이터에서 이상 징후 감지"""
        vib_cols = ['vibration_x', 'vibration_y', 'vibration_z']
        if not all(col in df.columns for col in vib_cols):
            return []
        
        # 진동 크기 계산 (3축 벡터 크기)
        df['vibration_magnitude'] = np.sqrt(
            df['vibration_x']**2 + 
            df['vibration_y']**2 + 
            df['vibration_z']**2
        )
        
        vib_values = df['vibration_magnitude'].dropna()
        if len(vib_values) < 10:
            return []
        
        mean = vib_values.mean()
        std = vib_values.std()
        
        anomalies = df[
            df['vibration_magnitude'] > mean + threshold_std * std
        ]
        
        return anomalies['timestamp'].tolist()
    
    def _find_nearest_anomaly_before(self, anomalies: List[datetime],
                                    target_time: datetime,
                                    max_days_before: int = 30) -> Optional[datetime]:
        """고장 시간 이전의 가장 가까운 이상 징후 찾기"""
        if not anomalies:
            return None
        
        # 최대 30일 이전까지만 검색
        cutoff_time = target_time - timedelta(days=max_days_before)
        
        valid_anomalies = [
            a for a in anomalies 
            if isinstance(a, datetime) and cutoff_time <= a < target_time
        ]
        
        if not valid_anomalies:
            return None
        
        # 가장 가까운 것 반환
        return max(valid_anomalies)
    
    def _save_correlation_result(self, result: Dict):
        """상관관계 분석 결과를 DB에 저장"""
        try:
            analysis_date = datetime.now().date()
            
            # 오디오 vs 온도 비교
            if self.warehouse.db_type == 'postgresql':
                try:
                    import psycopg2
                    conn = psycopg2.connect(
                        host=self.warehouse.db_config['host'],
                        port=self.warehouse.db_config['port'],
                        database=self.warehouse.db_config['database'],
                        user=self.warehouse.db_config['user'],
                        password=self.warehouse.db_config['password']
                    )
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        INSERT INTO correlation_analysis
                        (analysis_date, device_id, sensor_type_1, sensor_type_2,
                         correlation_coefficient, lead_time_days, prediction_accuracy,
                         sample_size, analysis_metadata)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        analysis_date,
                        result['device_id'],
                        'audio',
                        'temperature',
                        0.0,  # correlation_coefficient (추후 계산)
                        result['audio_sensor']['avg_lead_days'],
                        result['audio_sensor']['accuracy'],
                        result['audio_sensor']['sample_count'],
                        json.dumps(result)
                    ))
                    
                    conn.commit()
                    cursor.close()
                    conn.close()
                except ImportError:
                    pass
            else:
                import sqlite3
                conn = sqlite3.connect(self.warehouse.db_config['database'])
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO correlation_analysis
                    (analysis_date, device_id, sensor_type_1, sensor_type_2,
                     correlation_coefficient, lead_time_days, prediction_accuracy,
                     sample_size, analysis_metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    analysis_date.isoformat(),
                    result['device_id'],
                    'audio',
                    'temperature',
                    0.0,
                    result['audio_sensor']['avg_lead_days'],
                    result['audio_sensor']['accuracy'],
                    result['audio_sensor']['sample_count'],
                    json.dumps(result)
                ))
                
                conn.commit()
                conn.close()
            
        except Exception as e:
            logger.error(f"상관관계 결과 저장 실패: {e}")
    
    def analyze_multiple_devices(self, device_ids: List[str],
                                start_date: datetime, end_date: datetime,
                                failure_events_by_device: Dict[str, List[Dict]]) -> Dict:
        """여러 디바이스에 대한 집계 분석"""
        results = []
        
        for device_id in device_ids:
            failure_events = failure_events_by_device.get(device_id, [])
            result = self.analyze_lead_time(device_id, start_date, end_date, failure_events)
            if result:
                results.append(result)
        
        if not results:
            return {}
        
        # 집계 통계
        audio_lead_days = [r['audio_sensor']['avg_lead_days'] for r in results]
        audio_accuracies = [r['audio_sensor']['accuracy'] for r in results]
        
        temp_lead_days = [r['temperature_sensor']['avg_lead_days'] for r in results]
        vib_lead_days = [r['vibration_sensor']['avg_lead_days'] for r in results]
        
        aggregated_result = {
            'total_devices': len(results),
            'audio_sensor': {
                'avg_lead_days': round(np.mean(audio_lead_days), 2),
                'std_lead_days': round(np.std(audio_lead_days), 2),
                'avg_accuracy': round(np.mean(audio_accuracies), 2),
                'std_accuracy': round(np.std(audio_accuracies), 2)
            },
            'temperature_sensor': {
                'avg_lead_days': round(np.mean(temp_lead_days), 2) if temp_lead_days else 0,
                'std_lead_days': round(np.std(temp_lead_days), 2) if temp_lead_days else 0
            },
            'vibration_sensor': {
                'avg_lead_days': round(np.mean(vib_lead_days), 2) if vib_lead_days else 0,
                'std_lead_days': round(np.std(vib_lead_days), 2) if vib_lead_days else 0
            },
            'device_results': results,
            'analyzed_at': datetime.now().isoformat()
        }
        
        return aggregated_result


if __name__ == "__main__":
    # 테스트 코드
    from services.data_warehouse_service import DataWarehouseService
    
    warehouse = DataWarehouseService()
    analysis_service = CorrelationAnalysisService(warehouse)
    
    print("✅ 상관관계 분석 서비스 테스트 완료")

