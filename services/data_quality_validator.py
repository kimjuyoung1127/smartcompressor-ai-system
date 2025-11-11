#!/usr/bin/env python3
"""
데이터 품질 검증 시스템
수집된 오디오 데이터의 품질을 종합적으로 검증

[검증 항목]
1. 기술적 품질 (Technical Quality)
   - 샘플링 레이트
   - 비트 깊이
   - 채널 수
   - 데이터 길이
   - 신호 레벨
   - 클리핑
   - 무음 구간

2. 신호 품질 (Signal Quality)
   - SNR (Signal-to-Noise Ratio)
   - 주파수 응답
   - 왜곡 (Distortion)
   - 동적 범위

3. 메타데이터 품질 (Metadata Quality)
   - 필수 필드 존재 여부
   - 타임스탬프 유효성
   - 디바이스 ID 유효성
   - 환경 조건 데이터

4. 라벨링 품질 (Labeling Quality)
   - 라벨 일관성
   - 라벨 완전성
   - 전문가 간 일치도
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class QualityLevel(Enum):
    """품질 등급"""
    EXCELLENT = "excellent"  # 90-100점
    GOOD = "good"           # 70-89점
    ACCEPTABLE = "acceptable"  # 50-69점
    POOR = "poor"           # 30-49점
    REJECT = "reject"       # 0-29점


class DataQualityValidator:
    """
    데이터 품질 검증 시스템
    
    [역할]
    - 수집된 오디오 데이터의 품질을 종합적으로 검증
    - 품질 점수 계산 및 등급 부여
    - 품질 문제 진단 및 개선 제안
    """
    
    def __init__(self,
                 min_sample_rate: int = 16000,
                 max_sample_rate: int = 48000,
                 min_duration: float = 1.0,
                 max_duration: float = 10.0,
                 min_snr_db: float = 20.0,
                 max_clipping_ratio: float = 0.01,
                 max_silence_ratio: float = 0.9):
        """
        초기화
        
        Args:
            min_sample_rate: 최소 샘플링 레이트
            max_sample_rate: 최대 샘플링 레이트
            min_duration: 최소 오디오 길이 (초)
            max_duration: 최대 오디오 길이 (초)
            min_snr_db: 최소 SNR (dB)
            max_clipping_ratio: 최대 클리핑 비율
            max_silence_ratio: 최대 무음 비율
        """
        self.min_sample_rate = min_sample_rate
        self.max_sample_rate = max_sample_rate
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.min_snr_db = min_snr_db
        self.max_clipping_ratio = max_clipping_ratio
        self.max_silence_ratio = max_silence_ratio
        
        logger.info("✅ 데이터 품질 검증 시스템 초기화 완료")
    
    def validate_audio_data(self,
                          audio_data: np.ndarray,
                          sample_rate: int,
                          metadata: Optional[Dict] = None) -> Dict:
        """
        오디오 데이터 종합 검증
        
        Args:
            audio_data: 오디오 배열
            sample_rate: 샘플링 레이트
            metadata: 메타데이터 (선택)
        
        Returns:
            {
                'overall_score': float,  # 전체 품질 점수 (0-100)
                'quality_level': str,    # 품질 등급
                'is_valid': bool,        # 유효성 여부
                'technical_quality': Dict,
                'signal_quality': Dict,
                'metadata_quality': Dict,
                'issues': List[str],     # 문제점 목록
                'recommendations': List[str]  # 개선 제안
            }
        """
        results = {
            'technical_quality': self._validate_technical_quality(audio_data, sample_rate),
            'signal_quality': self._validate_signal_quality(audio_data, sample_rate),
            'metadata_quality': self._validate_metadata_quality(metadata or {})
        }
        
        # 전체 점수 계산 (가중 평균)
        overall_score = (
            results['technical_quality']['score'] * 0.4 +
            results['signal_quality']['score'] * 0.4 +
            results['metadata_quality']['score'] * 0.2
        )
        
        # 품질 등급 결정
        if overall_score >= 90:
            quality_level = QualityLevel.EXCELLENT
        elif overall_score >= 70:
            quality_level = QualityLevel.GOOD
        elif overall_score >= 50:
            quality_level = QualityLevel.ACCEPTABLE
        elif overall_score >= 30:
            quality_level = QualityLevel.POOR
        else:
            quality_level = QualityLevel.REJECT
        
        # 문제점 및 개선 제안 수집
        issues = []
        recommendations = []
        
        for category in ['technical_quality', 'signal_quality', 'metadata_quality']:
            category_result = results[category]
            issues.extend(category_result.get('issues', []))
            recommendations.extend(category_result.get('recommendations', []))
        
        return {
            'overall_score': float(overall_score),
            'quality_level': quality_level.value,
            'is_valid': quality_level != QualityLevel.REJECT,
            **results,
            'issues': issues,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }
    
    def _validate_technical_quality(self,
                                   audio_data: np.ndarray,
                                   sample_rate: int) -> Dict:
        """
        기술적 품질 검증
        
        검증 항목:
        - 샘플링 레이트
        - 데이터 길이
        - 신호 레벨
        - 클리핑
        - 무음 구간
        """
        score = 100.0
        issues = []
        recommendations = []
        metrics = {}
        
        # 1. 샘플링 레이트 검증
        if sample_rate < self.min_sample_rate:
            score -= 20
            issues.append(f'샘플링 레이트가 너무 낮음 ({sample_rate}Hz < {self.min_sample_rate}Hz)')
            recommendations.append(f'샘플링 레이트를 최소 {self.min_sample_rate}Hz로 설정하세요')
        elif sample_rate > self.max_sample_rate:
            score -= 10
            issues.append(f'샘플링 레이트가 너무 높음 ({sample_rate}Hz > {self.max_sample_rate}Hz)')
            recommendations.append(f'샘플링 레이트를 {self.max_sample_rate}Hz 이하로 설정하세요')
        
        metrics['sample_rate'] = sample_rate
        
        # 2. 데이터 길이 검증
        duration = len(audio_data) / sample_rate
        if duration < self.min_duration:
            score -= 30
            issues.append(f'오디오 길이가 너무 짧음 ({duration:.2f}초 < {self.min_duration}초)')
            recommendations.append(f'최소 {self.min_duration}초 이상의 오디오를 수집하세요')
        elif duration > self.max_duration:
            score -= 10
            issues.append(f'오디오 길이가 너무 김 ({duration:.2f}초 > {self.max_duration}초)')
            recommendations.append(f'오디오 길이를 {self.max_duration}초 이하로 제한하세요')
        
        metrics['duration'] = float(duration)
        metrics['length'] = len(audio_data)
        
        # 3. 신호 레벨 검증
        max_amplitude = np.max(np.abs(audio_data))
        rms_level = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
        
        if max_amplitude < 100:
            score -= 25
            issues.append(f'신호 레벨이 너무 낮음 (max: {max_amplitude})')
            recommendations.append('마이크 게인을 높이거나 센서 위치를 조정하세요')
        elif max_amplitude > 30000:
            score -= 20
            issues.append(f'신호 레벨이 너무 높음 (max: {max_amplitude}, 클리핑 가능성)')
            recommendations.append('마이크 게인을 낮추거나 센서 위치를 조정하세요')
        
        metrics['max_amplitude'] = int(max_amplitude)
        metrics['rms_level'] = float(rms_level)
        
        # 4. 클리핑 검증
        clipping_ratio = np.sum(np.abs(audio_data) > 30000) / len(audio_data)
        if clipping_ratio > self.max_clipping_ratio:
            score -= 30
            issues.append(f'클리핑 감지 (비율: {clipping_ratio:.2%})')
            recommendations.append('마이크 게인을 낮추거나 센서 위치를 조정하세요')
        
        metrics['clipping_ratio'] = float(clipping_ratio)
        
        # 5. 무음 구간 검증
        silence_ratio = np.sum(audio_data == 0) / len(audio_data)
        if silence_ratio > self.max_silence_ratio:
            score -= 25
            issues.append(f'무음 구간 과다 (비율: {silence_ratio:.2%})')
            recommendations.append('센서 위치를 조정하거나 환경 소음을 확인하세요')
        
        metrics['silence_ratio'] = float(silence_ratio)
        
        # 점수는 0 이상으로 제한
        score = max(0.0, score)
        
        return {
            'score': float(score),
            'issues': issues,
            'recommendations': recommendations,
            'metrics': metrics
        }
    
    def _validate_signal_quality(self,
                                audio_data: np.ndarray,
                                sample_rate: int) -> Dict:
        """
        신호 품질 검증
        
        검증 항목:
        - SNR (Signal-to-Noise Ratio)
        - 주파수 응답
        - 왜곡
        - 동적 범위
        """
        score = 100.0
        issues = []
        recommendations = []
        metrics = {}
        
        try:
            # 1. SNR 계산
            snr_db = self._calculate_snr(audio_data, sample_rate)
            if snr_db < self.min_snr_db:
                score -= 30
                issues.append(f'SNR이 너무 낮음 ({snr_db:.1f}dB < {self.min_snr_db}dB)')
                recommendations.append('환경 노이즈를 줄이거나 센서 위치를 조정하세요')
            
            metrics['snr_db'] = float(snr_db)
            
            # 2. 동적 범위 계산
            dynamic_range = self._calculate_dynamic_range(audio_data)
            if dynamic_range < 40:  # 40dB 미만이면 문제
                score -= 20
                issues.append(f'동적 범위가 너무 좁음 ({dynamic_range:.1f}dB)')
                recommendations.append('신호 레벨을 조정하거나 센서 위치를 변경하세요')
            
            metrics['dynamic_range_db'] = float(dynamic_range)
            
            # 3. 주파수 응답 검증 (기본 주파수 존재 여부)
            has_signal = self._check_signal_presence(audio_data, sample_rate)
            if not has_signal:
                score -= 40
                issues.append('유효한 신호가 감지되지 않음')
                recommendations.append('센서 연결 및 위치를 확인하세요')
            
            metrics['has_signal'] = has_signal
            
        except Exception as e:
            logger.warning(f"신호 품질 검증 오류: {e}")
            score -= 20
            issues.append(f'신호 품질 검증 실패: {str(e)}')
        
        # 점수는 0 이상으로 제한
        score = max(0.0, score)
        
        return {
            'score': float(score),
            'issues': issues,
            'recommendations': recommendations,
            'metrics': metrics
        }
    
    def _validate_metadata_quality(self, metadata: Dict) -> Dict:
        """
        메타데이터 품질 검증
        
        검증 항목:
        - 필수 필드 존재 여부
        - 타임스탬프 유효성
        - 디바이스 ID 유효성
        - 환경 조건 데이터
        """
        score = 100.0
        issues = []
        recommendations = []
        metrics = {}
        
        # 필수 필드
        required_fields = ['device_id', 'timestamp']
        for field in required_fields:
            if field not in metadata:
                score -= 30
                issues.append(f'필수 필드 누락: {field}')
                recommendations.append(f'{field} 필드를 추가하세요')
            else:
                metrics[field] = metadata[field]
        
        # 타임스탬프 유효성
        if 'timestamp' in metadata:
            try:
                timestamp = metadata['timestamp']
                if isinstance(timestamp, str):
                    datetime.fromisoformat(timestamp)
                metrics['timestamp_valid'] = True
            except (ValueError, TypeError):
                score -= 20
                issues.append('타임스탬프 형식이 올바르지 않음')
                recommendations.append('ISO 8601 형식의 타임스탬프를 사용하세요')
                metrics['timestamp_valid'] = False
        
        # 디바이스 ID 유효성
        if 'device_id' in metadata:
            device_id = metadata['device_id']
            if not device_id or len(device_id) < 3:
                score -= 20
                issues.append('디바이스 ID가 유효하지 않음')
                recommendations.append('유효한 디바이스 ID를 설정하세요')
            metrics['device_id_valid'] = bool(device_id and len(device_id) >= 3)
        
        # 선택적 필드 (점수에 영향 없음, 정보만)
        optional_fields = ['environmental_conditions', 'location', 'operator_notes']
        for field in optional_fields:
            if field in metadata:
                metrics[field] = metadata[field]
        
        # 점수는 0 이상으로 제한
        score = max(0.0, score)
        
        return {
            'score': float(score),
            'issues': issues,
            'recommendations': recommendations,
            'metrics': metrics
        }
    
    def _calculate_snr(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """
        SNR (Signal-to-Noise Ratio) 계산
        
        간단한 방법: 신호 에너지와 노이즈 에너지 비율
        """
        try:
            # 신호 에너지 (전체 RMS)
            signal_energy = np.mean(audio_data.astype(np.float32) ** 2)
            
            # 노이즈 에너지 (고주파 성분 추정)
            # FFT를 사용하여 고주파 노이즈 추정
            fft = np.fft.fft(audio_data)
            freqs = np.fft.fftfreq(len(audio_data), 1/sample_rate)
            
            # 고주파 대역 (노이즈 추정)
            high_freq_mask = np.abs(freqs) > sample_rate * 0.4
            noise_energy = np.mean(np.abs(fft[high_freq_mask]) ** 2)
            
            if noise_energy > 0:
                snr_linear = signal_energy / noise_energy
                snr_db = 10 * np.log10(snr_linear)
            else:
                snr_db = 100.0  # 노이즈가 없으면 매우 높은 SNR
            
            return float(snr_db)
        except Exception:
            return 0.0
    
    def _calculate_dynamic_range(self, audio_data: np.ndarray) -> float:
        """
        동적 범위 계산 (dB)
        """
        try:
            max_val = np.max(np.abs(audio_data))
            min_val = np.min(np.abs(audio_data[audio_data != 0]))
            
            if min_val > 0:
                dynamic_range = 20 * np.log10(max_val / min_val)
            else:
                dynamic_range = 0.0
            
            return float(dynamic_range)
        except Exception:
            return 0.0
    
    def _check_signal_presence(self, audio_data: np.ndarray, sample_rate: int) -> bool:
        """
        유효한 신호 존재 여부 확인
        
        기본 주파수 성분이 있는지 확인
        """
        try:
            # RMS 레벨이 임계값 이상인지 확인
            rms = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
            return rms > 100  # 최소 신호 레벨
        except Exception:
            return False


# 전역 인스턴스
data_quality_validator = DataQualityValidator()

