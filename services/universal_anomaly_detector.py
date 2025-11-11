#!/usr/bin/env python3
"""
범용 이상 감지 시스템 (Universal Anomaly Detector)
모든 압축기에 공통 적용 가능한 실시간 고장 신호 감지 알고리즘

핵심 알고리즘:
1. 스펙트럼 이상 점수 (Real-time Spectral Anomaly Score)
2. 데시벨 기반 1차 필터링
3. 범용 고장 패턴 감지 (파열음, 베어링 마모, 언밸런스, 증발기 성에 등)
"""

import numpy as np
import librosa
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from collections import deque
import json
import os

logger = logging.getLogger(__name__)


class UniversalAnomalyDetector:
    """
    범용 이상 감지 시스템
    
    특징:
    - 모든 압축기에 공통 적용 가능
    - 실시간 스펙트럼 이상 점수 계산
    - 데시벨 기반 1차 필터링
    - 범용 고장 패턴 감지
    """
    
    def __init__(self,
                 sample_rate: int = 16000,
                 window_size: float = 5.0,
                 baseline_update_interval_hours: int = 24):
        """
        Args:
            sample_rate: 샘플링 레이트
            window_size: 분석 윈도우 크기 (초)
            baseline_update_interval_hours: 기준선 업데이트 간격 (시간)
        """
        self.sample_rate = sample_rate
        self.window_size = window_size
        self.baseline_update_interval_hours = baseline_update_interval_hours
        
        # 기준선 (정상 상태)
        self.baseline = None
        self.baseline_history = deque(maxlen=100)  # 최근 100개 기준선
        self.baseline_last_update = None
        
        # 데시벨 임계값
        self.decibel_thresholds = {
            'no_input': 40,      # 35-40dB: 소리 없음
            'normal_low': 48,    # 40-48dB: 정상 (낮은 소리)
            'analysis_start': 48  # 48dB 이상: 분석 시작
        }
        
        # 히스토리 (최근 N개 샘플)
        self.history = deque(maxlen=1000)
        
        logger.info("✅ 범용 이상 감지 시스템 초기화 완료")
        logger.info(f"   - 윈도우 크기: {window_size}초")
        logger.info(f"   - 샘플링 레이트: {sample_rate}Hz")
    
    def establish_baseline(self, audio_samples: List[np.ndarray]) -> Dict:
        """
        정상 상태 기준선 설정
        
        Args:
            audio_samples: 정상 상태 오디오 샘플 리스트 (1-2일 수집)
        
        Returns:
            기준선 딕셔너리
        """
        logger.info(f"📊 기준선 설정 시작 ({len(audio_samples)}개 샘플)")
        
        all_features = []
        for audio in audio_samples:
            features = self._extract_features(audio)
            if features:
                all_features.append(features)
        
        if not all_features:
            logger.warning("⚠️ 특징 추출 실패, 기본 기준선 사용")
            return self._get_default_baseline()
        
        # 통계 계산
        baseline = {
            'spectral_centroid_mean': np.mean([f['spectral_centroid'] for f in all_features]),
            'spectral_centroid_std': np.std([f['spectral_centroid'] for f in all_features]),
            'rms_energy_mean': np.mean([f['rms_energy'] for f in all_features]),
            'rms_energy_std': np.std([f['rms_energy'] for f in all_features]),
            'high_freq_energy_ratio_mean': np.mean([f['high_freq_energy_ratio'] for f in all_features]),
            'high_freq_energy_ratio_std': np.std([f['high_freq_energy_ratio'] for f in all_features]),
            'low_freq_energy_ratio_mean': np.mean([f['low_freq_energy_ratio'] for f in all_features]),
            'low_freq_energy_ratio_std': np.std([f['low_freq_energy_ratio'] for f in all_features]),
            'zcr_mean': np.mean([f['zcr'] for f in all_features]),
            'zcr_std': np.std([f['zcr'] for f in all_features]),
            'pattern_regularity_mean': np.mean([f.get('pattern_regularity', 0.8) for f in all_features]),
            'pattern_regularity_std': np.std([f.get('pattern_regularity', 0.8) for f in all_features]),
            'created_at': datetime.now().isoformat(),
            'sample_count': len(all_features)
        }
        
        self.baseline = baseline
        self.baseline_last_update = datetime.now()
        self.baseline_history.append(baseline)
        
        logger.info("✅ 기준선 설정 완료")
        logger.info(f"   - 샘플 수: {len(all_features)}")
        logger.info(f"   - 스펙트럼 중심: {baseline['spectral_centroid_mean']:.2f} ± {baseline['spectral_centroid_std']:.2f}")
        logger.info(f"   - RMS 에너지: {baseline['rms_energy_mean']:.4f} ± {baseline['rms_energy_std']:.4f}")
        
        return baseline
    
    def detect_anomaly(self, 
                      audio_data: np.ndarray,
                      decibel_level: Optional[float] = None) -> Dict:
        """
        실시간 이상 감지
        
        Args:
            audio_data: 오디오 데이터
            decibel_level: 데시벨 레벨 (선택적)
        
        Returns:
            이상 감지 결과
        """
        if self.baseline is None:
            return {
                'is_anomaly': False,
                'confidence': 0.0,
                'message': '기준선이 설정되지 않았습니다.',
                'anomaly_type': 'unknown',
                'anomaly_score': 0.0
            }
        
        # 1단계: 데시벨 기반 1차 필터링
        decibel_result = self._first_stage_decibel_filter(decibel_level)
        if decibel_result['action'] == 'skip':
            return {
                'is_anomaly': False,
                'confidence': 1.0,
                'message': decibel_result['reason'],
                'anomaly_type': 'no_input',
                'anomaly_score': 0.0,
                'decibel_level': decibel_level
            }
        
        if decibel_result['action'] == 'update_statistics_only':
            return {
                'is_anomaly': False,
                'confidence': 1.0,
                'message': '정상 (낮은 소리)',
                'anomaly_type': 'normal_low',
                'anomaly_score': 0.0,
                'decibel_level': decibel_level
            }
        
        # 2단계: 특징 추출
        features = self._extract_features(audio_data)
        if not features:
            return {
                'is_anomaly': False,
                'confidence': 0.0,
                'message': '특징 추출 실패',
                'anomaly_type': 'unknown',
                'anomaly_score': 0.0
            }
        
        # 3단계: 스펙트럼 이상 점수 계산
        anomaly_score_result = self._calculate_anomaly_score(features)
        
        # 4단계: 고장 유형 분류
        failure_type = self._classify_failure_type(features, anomaly_score_result)
        
        # 5단계: 히스토리 업데이트
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'features': features,
            'anomaly_score': anomaly_score_result['total_score'],
            'failure_type': failure_type
        })
        
        result = {
            'is_anomaly': anomaly_score_result['total_score'] > 0.7,
            'confidence': anomaly_score_result['confidence'],
            'message': '고장 신호 감지!' if anomaly_score_result['total_score'] > 0.7 else '정상',
            'anomaly_type': failure_type,
            'anomaly_score': anomaly_score_result['total_score'],
            'individual_scores': anomaly_score_result['individual_scores'],
            'features': features,
            'decibel_level': decibel_level,
            'timestamp': datetime.now().isoformat()
        }
        
        return result
    
    def _first_stage_decibel_filter(self, decibel_level: Optional[float]) -> Dict:
        """
        데시벨 기반 1차 필터링
        
        Returns:
            필터링 결과
        """
        if decibel_level is None:
            return {'action': 'needs_analysis', 'reason': 'decibel_not_provided'}
        
        if decibel_level < self.decibel_thresholds['no_input']:
            return {'action': 'skip', 'reason': 'no_input'}
        
        if decibel_level < self.decibel_thresholds['normal_low']:
            return {'action': 'update_statistics_only', 'reason': 'normal_low'}
        
        return {'action': 'needs_analysis', 'reason': 'decibel_above_threshold'}
    
    def _extract_features(self, audio_data: np.ndarray) -> Optional[Dict]:
        """
        오디오에서 특징 추출
        """
        try:
            # 샘플링 레이트 조정
            if len(audio_data) > 0:
                if hasattr(audio_data, 'shape') and len(audio_data.shape) > 1:
                    audio_data = audio_data.flatten()
                
                # 리샘플링
                if len(audio_data) < self.sample_rate * self.window_size:
                    target_length = int(self.sample_rate * self.window_size)
                    audio_data = np.pad(audio_data, (0, target_length - len(audio_data)))
                elif len(audio_data) > self.sample_rate * self.window_size:
                    target_length = int(self.sample_rate * self.window_size)
                    audio_data = audio_data[:target_length]
            
            # 노이즈 필터링
            try:
                from scipy.signal import butter, filtfilt
                nyquist = self.sample_rate / 2
                low_cutoff = 50 / nyquist
                high_cutoff = 4000 / nyquist
                b, a = butter(4, [low_cutoff, high_cutoff], btype='band')
                filtered_audio = filtfilt(b, a, audio_data)
            except ImportError:
                # scipy가 없으면 필터링 없이 진행
                logger.warning("scipy가 설치되지 않아 필터링을 건너뜁니다.")
                filtered_audio = audio_data
            
            features = {}
            
            # 1. 에너지 특징
            rms_energy = np.sqrt(np.mean(filtered_audio ** 2))
            features['rms_energy'] = float(rms_energy)
            
            # 2. 주파수 도메인 특징
            stft = librosa.stft(filtered_audio, n_fft=1024, hop_length=512)
            magnitude = np.abs(stft)
            frequencies = librosa.fft_frequencies(sr=self.sample_rate, n_fft=1024)
            
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=filtered_audio, sr=self.sample_rate))
            features['spectral_centroid'] = float(spectral_centroid)
            features['spectral_centroid_std'] = float(np.std(librosa.feature.spectral_centroid(y=filtered_audio, sr=self.sample_rate)))
            
            spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=filtered_audio, sr=self.sample_rate))
            features['spectral_rolloff'] = float(spectral_rolloff)
            
            # 3. Zero Crossing Rate
            zcr = np.mean(librosa.feature.zero_crossing_rate(filtered_audio))
            features['zcr'] = float(zcr)
            
            # 4. 주파수 대역별 에너지 비율
            low_freq_energy = np.sum(magnitude[(frequencies >= 50) & (frequencies <= 500), :])
            mid_freq_energy = np.sum(magnitude[(frequencies >= 500) & (frequencies <= 2000), :])
            high_freq_energy = np.sum(magnitude[(frequencies >= 2000) & (frequencies <= 4000), :])
            total_energy = np.sum(magnitude)
            
            if total_energy > 0:
                features['low_freq_energy_ratio'] = float(low_freq_energy / total_energy)
                features['mid_freq_energy_ratio'] = float(mid_freq_energy / total_energy)
                features['high_freq_energy_ratio'] = float(high_freq_energy / total_energy)
            else:
                features['low_freq_energy_ratio'] = 0.0
                features['mid_freq_energy_ratio'] = 0.0
                features['high_freq_energy_ratio'] = 0.0
            
            # 5. 패턴 안정성 (간단한 버전)
            # 실제로는 시간적 패턴 분석이 필요하지만, 여기서는 스펙트럼 중심의 변동성으로 대체
            features['pattern_regularity'] = float(1.0 / (1.0 + features['spectral_centroid_std'] / (features['spectral_centroid'] + 1e-6)))
            
            return features
            
        except Exception as e:
            logger.error(f"특징 추출 실패: {e}")
            return None
    
    def _calculate_anomaly_score(self, features: Dict) -> Dict:
        """
        스펙트럼 이상 점수 계산
        """
        if not self.baseline:
            return {
                'total_score': 0.0,
                'confidence': 0.0,
                'individual_scores': {}
            }
        
        individual_scores = {}
        
        # 스펙트럼 중심 이상 점수
        centroid_z_score = abs(
            (features['spectral_centroid'] - self.baseline['spectral_centroid_mean'])
            / (self.baseline['spectral_centroid_std'] + 1e-6)
        )
        individual_scores['spectral_centroid'] = min(1.0, centroid_z_score / 3.0)
        
        # RMS 에너지 이상 점수
        energy_z_score = abs(
            (features['rms_energy'] - self.baseline['rms_energy_mean'])
            / (self.baseline['rms_energy_std'] + 1e-6)
        )
        individual_scores['rms_energy'] = min(1.0, energy_z_score / 3.0)
        
        # 고주파 에너지 비율 이상 점수
        high_freq_z_score = abs(
            (features['high_freq_energy_ratio'] - self.baseline['high_freq_energy_ratio_mean'])
            / (self.baseline['high_freq_energy_ratio_std'] + 1e-6)
        )
        individual_scores['high_freq_energy'] = min(1.0, high_freq_z_score / 3.0)
        
        # 저주파 에너지 비율 이상 점수 (냉매 누출 등)
        low_freq_z_score = abs(
            (features['low_freq_energy_ratio'] - self.baseline['low_freq_energy_ratio_mean'])
            / (self.baseline['low_freq_energy_ratio_std'] + 1e-6)
        )
        individual_scores['low_freq_energy'] = min(1.0, low_freq_z_score / 3.0)
        
        # Zero Crossing Rate 이상 점수
        zcr_z_score = abs(
            (features['zcr'] - self.baseline['zcr_mean'])
            / (self.baseline['zcr_std'] + 1e-6)
        )
        individual_scores['zcr'] = min(1.0, zcr_z_score / 3.0)
        
        # 종합 이상 점수 (가중 평균)
        total_score = (
            0.25 * individual_scores['spectral_centroid'] +
            0.25 * individual_scores['rms_energy'] +
            0.20 * individual_scores['high_freq_energy'] +
            0.15 * individual_scores['low_freq_energy'] +
            0.15 * individual_scores['zcr']
        )
        
        # 신뢰도 계산
        confidence = min(1.0, total_score * 1.2)
        
        return {
            'total_score': total_score,
            'confidence': confidence,
            'individual_scores': individual_scores
        }
    
    def _classify_failure_type(self, features: Dict, anomaly_score_result: Dict) -> str:
        """
        고장 유형 분류
        """
        individual_scores = anomaly_score_result['individual_scores']
        
        # 베어링 마모: 고주파 에너지 증가
        if individual_scores.get('high_freq_energy', 0) > 0.7:
            return 'bearing_wear'
        
        # 파열음: RMS 에너지 급증
        if individual_scores.get('rms_energy', 0) > 0.8:
            return 'burst_sound'
        
        # 냉매 누출: 저주파 에너지 증가
        if (individual_scores.get('low_freq_energy', 0) > 0.7 and
            features.get('spectral_centroid', 0) < 1000):
            return 'refrigerant_leak'
        
        # 증발기 성에: 연속 작동 패턴 (RMS 에너지 지속적 높음 + 패턴 안정성 감소)
        if (individual_scores.get('rms_energy', 0) > 0.6 and
            features.get('pattern_regularity', 1.0) < 0.7):
            return 'evaporator_frost'
        
        # 언밸런스: 스펙트럼 중심 변화
        if individual_scores.get('spectral_centroid', 0) > 0.7:
            return 'unbalance'
        
        # 마찰음: ZCR 증가
        if individual_scores.get('zcr', 0) > 0.7:
            return 'friction'
        
        # 일반적인 이상
        if anomaly_score_result['total_score'] > 0.7:
            return 'general_anomaly'
        
        return 'normal'
    
    def _get_default_baseline(self) -> Dict:
        """
        기본 기준선 (임시)
        """
        return {
            'spectral_centroid_mean': 2000.0,
            'spectral_centroid_std': 200.0,
            'rms_energy_mean': 0.1,
            'rms_energy_std': 0.02,
            'high_freq_energy_ratio_mean': 0.15,
            'high_freq_energy_ratio_std': 0.05,
            'low_freq_energy_ratio_mean': 0.5,
            'low_freq_energy_ratio_std': 0.1,
            'zcr_mean': 0.05,
            'zcr_std': 0.02,
            'pattern_regularity_mean': 0.8,
            'pattern_regularity_std': 0.1,
            'created_at': datetime.now().isoformat(),
            'sample_count': 0
        }
    
    def save_baseline(self, filepath: str):
        """기준선 저장"""
        if self.baseline:
            with open(filepath, 'w') as f:
                json.dump(self.baseline, f, indent=2)
            logger.info(f"✅ 기준선 저장 완료: {filepath}")
    
    def load_baseline(self, filepath: str):
        """기준선 로드"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                self.baseline = json.load(f)
            logger.info(f"✅ 기준선 로드 완료: {filepath}")
        else:
            logger.warning(f"⚠️ 기준선 파일 없음: {filepath}")

