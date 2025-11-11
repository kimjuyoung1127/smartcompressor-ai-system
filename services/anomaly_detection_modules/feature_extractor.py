#!/usr/bin/env python3
"""
오디오 특징 추출 모듈 (FeatureExtractor)

[일반인/개발자를 위한 설명]

이 모듈은 "소리의 특성"을 숫자로 변환하는 역할을 합니다.

🎵 소리를 숫자로 변환한다는 것은?
- 사람이 "이 소리가 이상하다"고 느끼는 것처럼, 컴퓨터도 숫자로 표현해야 합니다
- 예: "이 소리는 고주파가 많네" → 숫자로 표현: high_freq_energy_ratio = 0.8

🔍 추출하는 특징들:

1. RMS 에너지 (rms_energy)
   - 의미: 소리의 "평균적인 크기"
   - 비유: 음악의 볼륨 크기
   - 예: 정상 압축기 = 0.1, 고장 압축기 = 0.5 (더 시끄러움)

2. 스펙트럼 중심 (spectral_centroid)
   - 의미: 소리의 "주파수 중심점"
   - 비유: 음악의 음높이 (저음/고음)
   - 예: 정상 압축기 = 2000Hz (중간), 베어링 마모 = 5000Hz (고음)

3. 주파수 대역별 에너지 비율
   - 의미: 저주파/중주파/고주파가 각각 얼마나 차지하는지
   - 비유: 음악의 베이스/미드/트레블 밸런스
   - 예: 냉매 누출 = 저주파 증가, 베어링 마모 = 고주파 증가

4. Zero Crossing Rate (zcr)
   - 의미: 소리가 얼마나 "날카로운지"
   - 비유: 부드러운 소리 vs 긁는 소리
   - 예: 정상 = 0.05 (부드러움), 마찰음 = 0.3 (날카로움)

5. 패턴 안정성 (pattern_regularity)
   - 의미: 소리가 얼마나 "일정한지"
   - 비유: 규칙적인 심장박동 vs 불규칙한 심장박동
   - 예: 정상 = 0.9 (안정적), 고장 = 0.3 (불안정)

💡 왜 중요한가?
- 이 특징들이 있어야 "이상 점수"를 계산할 수 있습니다
- 사람이 "이상하다"고 느끼는 것을 숫자로 표현합니다
- 이 숫자들을 기준선과 비교하여 고장을 감지합니다

🔧 개발자를 위한 설명:
- 입력: 오디오 데이터 (numpy array)
- 출력: 특징 딕셔너리 (숫자들의 모음)
- 연산 비용: 중간 (FFT 계산 필요)
- 사용 시점: 데시벨 필터 통과 후 (48dB 이상)
"""

import numpy as np
import librosa
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """
    오디오 특징 추출 모듈
    
    [역할]
    오디오 데이터를 받아서 "소리의 특성"을 숫자로 변환합니다.
    사람이 "이상하다"고 느끼는 것을 숫자로 표현하는 것이 목적입니다.
    
    [왜 중요한가?]
    - 컴퓨터는 소리를 직접 이해할 수 없습니다
    - 소리를 숫자(특징)로 변환해야 비교하고 판단할 수 있습니다
    - 이 특징들이 있어야 "이상 점수"를 계산할 수 있습니다
    
    [작동 방식]
    1. 오디오 데이터를 받습니다 (예: 5초 분량의 소리)
    2. 주파수 분석을 수행합니다 (FFT 사용)
    3. 여러 특징을 추출합니다:
       - RMS 에너지: 소리의 평균적인 크기
       - 스펙트럼 중심: 소리의 주파수 중심점
       - 주파수 대역별 에너지: 저주파/중주파/고주파 비율
       - Zero Crossing Rate: 소리의 날카로움
       - 패턴 안정성: 소리의 일정함
    4. 특징 딕셔너리를 반환합니다
    
    [실제 예시]
    입력: 5초 분량의 압축기 소리
    출력: {
        'rms_energy': 0.15,           # 평균적인 크기
        'spectral_centroid': 2500.0,  # 주파수 중심점
        'high_freq_energy_ratio': 0.2, # 고주파 비율
        'zcr': 0.08,                  # 날카로움
        'pattern_regularity': 0.85    # 안정성
    }
    """
    
    def __init__(self,
                 sample_rate: int = 16000,
                 window_size: float = 5.0,
                 n_fft: int = 1024,
                 hop_length: int = 512):
        """
        초기화
        
        Args:
            sample_rate: 샘플링 레이트 (초당 샘플 수)
                - 예: 16000 = 1초에 16,000개 샘플
                - 사람이 들을 수 있는 범위를 충분히 커버
            window_size: 분석 윈도우 크기 (초)
                - 예: 5.0 = 5초 분량의 소리를 분석
                - 너무 짧으면 정보 부족, 너무 길면 느림
            n_fft: FFT 윈도우 크기
                - 주파수 분석에 사용
                - 1024 = 적절한 해상도와 속도의 균형
            hop_length: 홉 길이
                - FFT를 수행하는 간격
                - 512 = 적절한 해상도
        """
        self.sample_rate = sample_rate
        self.window_size = window_size
        self.n_fft = n_fft
        self.hop_length = hop_length
        
        logger.info("✅ 특징 추출 모듈 초기화 완료")
        logger.info(f"   - 샘플링 레이트: {sample_rate}Hz")
        logger.info(f"   - 윈도우 크기: {window_size}초")
    
    def extract(self, audio_data: np.ndarray) -> Optional[Dict]:
        """
        오디오에서 특징 추출
        
        [작동 방식]
        1. 오디오 전처리 (길이 조정)
        2. 노이즈 필터링 (불필요한 주파수 제거)
        3. 특징 추출:
           - RMS 에너지: 소리의 평균적인 크기
           - 스펙트럼 중심: 소리의 주파수 중심점
           - 주파수 대역별 에너지: 저주파/중주파/고주파 비율
           - Zero Crossing Rate: 소리의 날카로움
           - 패턴 안정성: 소리의 일정함
        
        [반환값]
        특징 딕셔너리:
        {
            'rms_energy': float,              # 평균적인 크기 (0~1)
            'spectral_centroid': float,     # 주파수 중심점 (Hz)
            'spectral_centroid_std': float, # 주파수 중심점 변동성
            'high_freq_energy_ratio': float, # 고주파 비율 (0~1)
            'low_freq_energy_ratio': float,  # 저주파 비율 (0~1)
            'zcr': float,                   # 날카로움 (0~1)
            'pattern_regularity': float      # 안정성 (0~1)
        }
        
        Args:
            audio_data: 오디오 데이터 (numpy array)
                - 예: 5초 분량 = 80,000개 샘플 (16000Hz × 5초)
        
        Returns:
            특징 딕셔너리 또는 None (실패 시)
        
        [실제 예시]
        >>> extractor = FeatureExtractor()
        >>> audio = np.array([...])  # 5초 분량의 오디오
        >>> features = extractor.extract(audio)
        >>> print(features['rms_energy'])  # 0.15
        >>> print(features['spectral_centroid'])  # 2500.0
        """
        try:
            # 샘플링 레이트 조정
            audio_data = self._preprocess_audio(audio_data)
            
            # 노이즈 필터링
            filtered_audio = self._filter_noise(audio_data)
            
            # 특징 추출
            features = {}
            
            # ===== 1. 에너지 특징 (RMS Energy) =====
            # 의미: 소리의 "평균적인 크기"
            # 비유: 음악의 볼륨 크기
            # 예: 정상 압축기 = 0.1, 고장 압축기 = 0.5 (더 시끄러움)
            rms_energy = np.sqrt(np.mean(filtered_audio ** 2))
            features['rms_energy'] = float(rms_energy)
            
            # ===== 2. 주파수 도메인 특징 =====
            # STFT: 소리를 시간-주파수로 변환 (음악 앱의 스펙트럼 그래프처럼)
            stft = librosa.stft(filtered_audio, n_fft=self.n_fft, hop_length=self.hop_length)
            magnitude = np.abs(stft)  # 주파수별 강도
            frequencies = librosa.fft_frequencies(sr=self.sample_rate, n_fft=self.n_fft)
            
            # 스펙트럼 중심 (Spectral Centroid)
            # 의미: 소리의 "주파수 중심점"
            # 비유: 음악의 음높이 (저음/고음)
            # 예: 정상 압축기 = 2000Hz (중간), 베어링 마모 = 5000Hz (고음)
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=filtered_audio, sr=self.sample_rate))
            features['spectral_centroid'] = float(spectral_centroid)
            # 스펙트럼 중심의 변동성 (안정성 측정에 사용)
            features['spectral_centroid_std'] = float(np.std(librosa.feature.spectral_centroid(y=filtered_audio, sr=self.sample_rate)))
            
            # 스펙트럼 롤오프 (Spectral Rolloff)
            # 의미: 주파수 에너지의 85%가 모여있는 지점
            # 비유: 음악의 고음 영역 경계
            spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=filtered_audio, sr=self.sample_rate))
            features['spectral_rolloff'] = float(spectral_rolloff)
            
            # ===== 3. Zero Crossing Rate (ZCR) =====
            # 의미: 소리가 얼마나 "날카로운지"
            # 비유: 부드러운 소리 vs 긁는 소리
            # 예: 정상 = 0.05 (부드러움), 마찰음 = 0.3 (날카로움)
            # 계산: 소리가 0을 지나가는 횟수 (날카로운 소리일수록 많음)
            zcr = np.mean(librosa.feature.zero_crossing_rate(filtered_audio))
            features['zcr'] = float(zcr)
            
            # ===== 4. 주파수 대역별 에너지 비율 =====
            # 의미: 저주파/중주파/고주파가 각각 얼마나 차지하는지
            # 비유: 음악의 베이스/미드/트레블 밸런스
            # 예: 냉매 누출 = 저주파 증가, 베어링 마모 = 고주파 증가
            
            # 저주파 에너지 (50-500Hz): 냉매 누출, 언밸런스 등
            low_freq_energy = np.sum(magnitude[(frequencies >= 50) & (frequencies <= 500), :])
            # 중주파 에너지 (500-2000Hz): 정상 압축기 소리
            mid_freq_energy = np.sum(magnitude[(frequencies >= 500) & (frequencies <= 2000), :])
            # 고주파 에너지 (2000-4000Hz): 베어링 마모, 마찰음 등
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
            
            # ===== 5. 패턴 안정성 (Pattern Regularity) =====
            # 의미: 소리가 얼마나 "일정한지"
            # 비유: 규칙적인 심장박동 vs 불규칙한 심장박동
            # 예: 정상 = 0.9 (안정적), 고장 = 0.3 (불안정)
            # 계산: 스펙트럼 중심의 변동성이 낮을수록 안정적
            features['pattern_regularity'] = float(
                1.0 / (1.0 + features['spectral_centroid_std'] / (features['spectral_centroid'] + 1e-6))
            )
            
            return features
            
        except Exception as e:
            logger.error(f"특징 추출 실패: {e}")
            return None
    
    def _preprocess_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """오디오 전처리"""
        if len(audio_data) > 0:
            if hasattr(audio_data, 'shape') and len(audio_data.shape) > 1:
                audio_data = audio_data.flatten()
            
            # 리샘플링
            target_length = int(self.sample_rate * self.window_size)
            if len(audio_data) < target_length:
                audio_data = np.pad(audio_data, (0, target_length - len(audio_data)))
            elif len(audio_data) > target_length:
                audio_data = audio_data[:target_length]
        
        return audio_data
    
    def _filter_noise(self, audio_data: np.ndarray) -> np.ndarray:
        """노이즈 필터링"""
        try:
            from scipy.signal import butter, filtfilt
            nyquist = self.sample_rate / 2
            low_cutoff = 50 / nyquist
            high_cutoff = 4000 / nyquist
            b, a = butter(4, [low_cutoff, high_cutoff], btype='band')
            return filtfilt(b, a, audio_data)
        except ImportError:
            logger.warning("scipy가 설치되지 않아 필터링을 건너뜁니다.")
            return audio_data

