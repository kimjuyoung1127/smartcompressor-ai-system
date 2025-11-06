#!/usr/bin/env python3
"""
실시간 고장 판단 시스템 (오픈소스 AI + 간단한 알고리즘)
들어오는 소리를 즉시 고장/비고장으로 판단하는 경량 시스템

정확도 예상:
- 오픈소스 모델 (YAMNet): 약 70-80% (일반적인 사운드 분류)
- 특징 기반 알고리즘: 약 75-85% (도메인 특화)
- 앙상블: 약 80-90% (두 방법 결합)
"""

import numpy as np
import librosa
import time
from typing import Dict, Optional, Tuple
from scipy import signal
from scipy.signal import butter, filtfilt
import logging

logger = logging.getLogger(__name__)


class RealtimeAnomalyDetector:
    """
    실시간 고장 판단 시스템
    오픈소스 사전 훈련 모델 + 간단한 특징 기반 알고리즘
    """
    
    def __init__(self, 
                 sample_rate: int = 16000,
                 window_size: float = 2.0,  # 2초 윈도우
                 use_pretrained_model: bool = True):
        """
        Args:
            sample_rate: 샘플링 레이트
            window_size: 분석 윈도우 크기 (초)
            use_pretrained_model: 오픈소스 사전 훈련 모델 사용 여부
        """
        self.sample_rate = sample_rate
        self.window_size = window_size
        self.use_pretrained_model = use_pretrained_model
        
        # 오픈소스 사전 훈련 모델 (YAMNet)
        self.yamnet_model = None
        self.yamnet_class_names = None
        
        if use_pretrained_model:
            self._load_pretrained_model()
        
        # 특징 기반 알고리즘 임계값 (경험적 값)
        self.thresholds = {
            'energy_ratio': 2.0,  # 에너지 비율 임계값
            'spectral_centroid_std': 500.0,  # 스펙트럼 중심 표준편차
            'zcr_ratio': 1.5,  # Zero Crossing Rate 비율
            'high_freq_energy': 0.3,  # 고주파 에너지 비율
        }
        
        # 정상 기준값 (최근 데이터로 업데이트 가능)
        self.normal_baseline = {
            'energy_mean': 0.1,
            'spectral_centroid_mean': 2000.0,
            'zcr_mean': 0.05,
        }
        
        # 히스토리 (최근 N개 샘플)
        self.history = []
        self.max_history = 100
        
        logger.info("✅ 실시간 고장 판단 시스템 초기화 완료")
        logger.info(f"   - 윈도우 크기: {window_size}초")
        logger.info(f"   - 사전 훈련 모델: {'사용' if use_pretrained_model else '미사용'}")
    
    def _load_pretrained_model(self):
        """오픈소스 사전 훈련 모델 로드 (YAMNet)"""
        try:
            import tensorflow_hub as hub
            
            logger.info("📦 YAMNet 모델 로딩 중...")
            self.yamnet_model = hub.load('https://tfhub.dev/google/yamnet/1')
            logger.info("✅ YAMNet 모델 로드 완료")
            
            # YAMNet 클래스 이름 로드
            import csv
            import tempfile
            import urllib.request
            
            # 클래스 이름 다운로드
            csv_url = 'https://raw.githubusercontent.com/tensorflow/models/master/research/audioset/yamnet/yamnet_class_map.csv'
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.csv') as f:
                urllib.request.urlretrieve(csv_url, f.name)
                with open(f.name, 'r') as csvfile:
                    reader = csv.reader(csvfile)
                    self.yamnet_class_names = [row[2] for row in reader]
            
            logger.info(f"✅ YAMNet 클래스 이름 로드 완료 ({len(self.yamnet_class_names)}개 클래스)")
            
        except ImportError:
            logger.warning("⚠️ tensorflow_hub가 설치되지 않았습니다. 특징 기반 알고리즘만 사용합니다.")
            logger.warning("   설치: pip install tensorflow_hub")
            self.use_pretrained_model = False
        except Exception as e:
            logger.warning(f"⚠️ 사전 훈련 모델 로드 실패: {e}")
            logger.warning("   특징 기반 알고리즘만 사용합니다.")
            self.use_pretrained_model = False
    
    def extract_features(self, audio_data: np.ndarray) -> Dict[str, float]:
        """오디오에서 특징 추출"""
        try:
            # 샘플링 레이트 조정
            if len(audio_data) > 0:
                if hasattr(audio_data, 'shape') and len(audio_data.shape) > 1:
                    audio_data = audio_data.flatten()
                
                # 리샘플링 (필요시)
                if len(audio_data) < self.sample_rate * self.window_size:
                    # 패딩
                    target_length = int(self.sample_rate * self.window_size)
                    audio_data = np.pad(audio_data, (0, target_length - len(audio_data)))
                elif len(audio_data) > self.sample_rate * self.window_size:
                    # 자르기
                    target_length = int(self.sample_rate * self.window_size)
                    audio_data = audio_data[:target_length]
            
            # 노이즈 필터링
            nyquist = self.sample_rate / 2
            low_cutoff = 50 / nyquist
            high_cutoff = 4000 / nyquist
            b, a = butter(4, [low_cutoff, high_cutoff], btype='band')
            filtered_audio = filtfilt(b, a, audio_data)
            
            features = {}
            
            # 1. 에너지 특징
            rms_energy = np.sqrt(np.mean(filtered_audio ** 2))
            features['rms_energy'] = float(rms_energy)
            features['energy_ratio'] = float(rms_energy / (self.normal_baseline['energy_mean'] + 1e-6))
            
            # 2. 주파수 도메인 특징
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=filtered_audio, sr=self.sample_rate))
            features['spectral_centroid'] = float(spectral_centroid)
            features['spectral_centroid_std'] = float(np.std(librosa.feature.spectral_centroid(y=filtered_audio, sr=self.sample_rate)))
            
            spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=filtered_audio, sr=self.sample_rate))
            features['spectral_rolloff'] = float(spectral_rolloff)
            
            # 3. Zero Crossing Rate
            zcr = np.mean(librosa.feature.zero_crossing_rate(filtered_audio))
            features['zcr'] = float(zcr)
            features['zcr_ratio'] = float(zcr / (self.normal_baseline['zcr_mean'] + 1e-6))
            
            # 4. 고주파 에너지 비율
            stft = librosa.stft(filtered_audio, n_fft=1024, hop_length=512)
            magnitude = np.abs(stft)
            freq_bins = librosa.fft_frequencies(sr=self.sample_rate, n_fft=1024)
            
            # 고주파 (2000Hz 이상) 에너지
            high_freq_mask = freq_bins > 2000
            high_freq_energy = np.mean(magnitude[high_freq_mask, :])
            total_energy = np.mean(magnitude)
            features['high_freq_energy_ratio'] = float(high_freq_energy / (total_energy + 1e-6))
            
            # 5. MFCC 특징 (간단한 통계)
            mfccs = librosa.feature.mfcc(y=filtered_audio, sr=self.sample_rate, n_mfcc=13)
            features['mfcc_mean'] = float(np.mean(mfccs))
            features['mfcc_std'] = float(np.std(mfccs))
            
            return features
            
        except Exception as e:
            logger.error(f"특징 추출 실패: {e}")
            return {}
    
    def predict_with_pretrained_model(self, audio_data: np.ndarray) -> Dict:
        """오픈소스 사전 훈련 모델로 예측"""
        if not self.use_pretrained_model or self.yamnet_model is None:
            return {'score': 0.0, 'confidence': 0.0, 'method': 'not_available'}
        
        try:
            # YAMNet은 16kHz, 모노 입력 필요
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=0)
            
            # YAMNet 예측
            scores, embeddings, spectrogram = self.yamnet_model(audio_data)
            
            # 이상 소리 관련 클래스 찾기
            anomaly_keywords = ['noise', 'mechanical', 'machine', 'motor', 'vibration', 
                              'alarm', 'warning', 'siren', 'buzz', 'hum', 'rattle']
            
            anomaly_score = 0.0
            top_class_idx = np.argmax(scores[0])
            top_score = float(scores[0][top_class_idx])
            
            # 이상 소리 관련 클래스인지 확인
            if top_class_idx < len(self.yamnet_class_names):
                class_name = self.yamnet_class_names[top_class_idx].lower()
                for keyword in anomaly_keywords:
                    if keyword in class_name:
                        anomaly_score = top_score
                        break
            
            # 신뢰도 계산
            confidence = float(top_score)
            
            return {
                'score': anomaly_score,
                'confidence': confidence,
                'method': 'yamnet',
                'top_class': self.yamnet_class_names[top_class_idx] if top_class_idx < len(self.yamnet_class_names) else 'unknown'
            }
            
        except Exception as e:
            logger.error(f"사전 훈련 모델 예측 실패: {e}")
            return {'score': 0.0, 'confidence': 0.0, 'method': 'error'}
    
    def predict_with_features(self, features: Dict[str, float]) -> Dict:
        """특징 기반 알고리즘으로 예측"""
        anomaly_flags = []
        anomaly_scores = []
        
        # 1. 에너지 비율 검사
        if features.get('energy_ratio', 0) > self.thresholds['energy_ratio']:
            anomaly_flags.append('high_energy')
            anomaly_scores.append(0.7)
        elif features.get('energy_ratio', 0) < 0.3:
            anomaly_flags.append('low_energy')
            anomaly_scores.append(0.6)
        
        # 2. 스펙트럼 중심 변동 검사
        if features.get('spectral_centroid_std', 0) > self.thresholds['spectral_centroid_std']:
            anomaly_flags.append('unstable_frequency')
            anomaly_scores.append(0.8)
        
        # 3. Zero Crossing Rate 검사
        if features.get('zcr_ratio', 0) > self.thresholds['zcr_ratio']:
            anomaly_flags.append('high_zcr')
            anomaly_scores.append(0.7)
        
        # 4. 고주파 에너지 비율 검사 (냉매 누설 등)
        if features.get('high_freq_energy_ratio', 0) > self.thresholds['high_freq_energy']:
            anomaly_flags.append('high_freq_anomaly')
            anomaly_scores.append(0.75)
        
        # 최종 점수 계산
        if anomaly_scores:
            final_score = max(anomaly_scores)
            confidence = len(anomaly_flags) / 4.0  # 플래그 개수 기반 신뢰도
        else:
            final_score = 0.0
            confidence = 0.0
        
        return {
            'score': final_score,
            'confidence': confidence,
            'method': 'feature_based',
            'flags': anomaly_flags
        }
    
    def detect(self, audio_data: np.ndarray) -> Dict:
        """
        실시간 고장 판단
        
        Args:
            audio_data: 오디오 데이터 (numpy array)
        
        Returns:
            {
                'is_failure': bool,  # 고장 여부
                'confidence': float,  # 신뢰도 (0-1)
                'score': float,  # 이상 점수 (0-1)
                'method': str,  # 사용된 방법
                'details': dict  # 상세 정보
            }
        """
        start_time = time.time()
        
        try:
            # 1. 특징 추출
            features = self.extract_features(audio_data)
            
            if not features:
                return {
                    'is_failure': False,
                    'confidence': 0.0,
                    'score': 0.0,
                    'method': 'error',
                    'details': {'error': 'feature_extraction_failed'},
                    'processing_time_ms': 0
                }
            
            # 2. 오픈소스 모델 예측
            pretrained_result = self.predict_with_pretrained_model(audio_data)
            
            # 3. 특징 기반 알고리즘 예측
            feature_result = self.predict_with_features(features)
            
            # 4. 앙상블 (두 방법 결합)
            ensemble_score = (
                pretrained_result['score'] * 0.4 +  # 오픈소스 모델 가중치
                feature_result['score'] * 0.6      # 특징 기반 가중치
            )
            
            ensemble_confidence = (
                pretrained_result['confidence'] * 0.4 +
                feature_result['confidence'] * 0.6
            )
            
            # 5. 최종 판정 (임계값: 0.5)
            is_failure = ensemble_score > 0.5
            
            # 6. 히스토리 업데이트
            self.history.append({
                'timestamp': time.time(),
                'is_failure': is_failure,
                'score': ensemble_score,
                'features': features
            })
            
            if len(self.history) > self.max_history:
                self.history.pop(0)
            
            # 7. 정상 기준값 업데이트 (동적 조정)
            if not is_failure and len(self.history) > 10:
                recent_normal = [h for h in self.history[-10:] if not h['is_failure']]
                if recent_normal:
                    self.normal_baseline['energy_mean'] = np.mean([h['features'].get('rms_energy', 0) for h in recent_normal])
                    self.normal_baseline['zcr_mean'] = np.mean([h['features'].get('zcr', 0) for h in recent_normal])
            
            processing_time = (time.time() - start_time) * 1000
            
            return {
                'is_failure': is_failure,
                'confidence': float(ensemble_confidence),
                'score': float(ensemble_score),
                'method': 'ensemble',
                'details': {
                    'pretrained': pretrained_result,
                    'feature_based': feature_result,
                    'features': features
                },
                'processing_time_ms': processing_time
            }
            
        except Exception as e:
            logger.error(f"고장 판단 실패: {e}")
            return {
                'is_failure': False,
                'confidence': 0.0,
                'score': 0.0,
                'method': 'error',
                'details': {'error': str(e)},
                'processing_time_ms': 0
            }


if __name__ == "__main__":
    # 테스트 코드
    logging.basicConfig(level=logging.INFO)
    
    detector = RealtimeAnomalyDetector()
    
    # 테스트 오디오 생성 (간단한 사인파)
    duration = 2.0
    sample_rate = 16000
    t = np.linspace(0, duration, int(sample_rate * duration))
    test_audio = np.sin(2 * np.pi * 440 * t)  # 440Hz 사인파
    
    result = detector.detect(test_audio)
    print("\n" + "="*60)
    print("실시간 고장 판단 결과")
    print("="*60)
    print(f"고장 여부: {'⚠️ 고장' if result['is_failure'] else '✅ 정상'}")
    print(f"신뢰도: {result['confidence']:.2%}")
    print(f"이상 점수: {result['score']:.2f}")
    print(f"처리 시간: {result['processing_time_ms']:.2f}ms")
    print(f"사용 방법: {result['method']}")
    print("="*60)

