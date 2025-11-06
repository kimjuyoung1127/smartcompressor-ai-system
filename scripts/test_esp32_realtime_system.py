#!/usr/bin/env python3
"""
ESP32 실시간 모니터링 시스템 테스트
실제 시나리오를 시뮬레이션하여 작동 확인
"""

import sys
from pathlib import Path
import numpy as np
import time
import requests
import json
from datetime import datetime

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.esp32_realtime_detector import ESP32RealtimeDetector


class ESP32RealtimeTester:
    """ESP32 실시간 시스템 테스트"""
    
    def __init__(self, use_api=False, api_url="http://localhost:5000"):
        """
        Args:
            use_api: API를 통한 테스트 여부 (False면 직접 서비스 사용)
            api_url: API 서버 URL
        """
        self.use_api = use_api
        self.api_url = api_url
        self.detector = None
        
        if not use_api:
            self.detector = ESP32RealtimeDetector(
                no_input_threshold=(35, 40),
                detection_start_threshold=48.0,
                confidence_threshold=0.7
            )
        
        print("\n" + "="*80)
        print("ESP32 실시간 모니터링 시스템 테스트")
        print("="*80)
        print(f"\n테스트 모드: {'API 테스트' if use_api else '직접 서비스 테스트'}")
        if use_api:
            print(f"API URL: {api_url}")
        print()
    
    def generate_audio_sample(self, sample_type="normal", duration=2.0, sample_rate=16000):
        """테스트용 오디오 샘플 생성"""
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        if sample_type == "normal":
            # 정상 소리 (440Hz 사인파)
            audio = np.sin(2 * np.pi * 440 * t) * 0.3
        elif sample_type == "anomaly":
            # 이상 소리 (고주파 노이즈)
            audio = (
                np.sin(2 * np.pi * 2000 * t) * 0.5 +
                np.sin(2 * np.pi * 3000 * t) * 0.3 +
                np.random.randn(len(t)) * 0.2
            )
        elif sample_type == "low_confidence":
            # 낮은 신뢰도 소리 (노이즈가 많음)
            audio = (
                np.sin(2 * np.pi * 440 * t) * 0.2 +
                np.random.randn(len(t)) * 0.5
            )
        else:
            audio = np.random.randn(len(t)) * 0.1
        
        return audio
    
    def calculate_decibel(self, audio_data):
        """오디오 데이터에서 데시벨 계산 (시뮬레이션)"""
        rms = np.sqrt(np.mean(audio_data ** 2))
        if rms == 0:
            return 35.0  # 기본값
        
        # RMS를 데시벨로 변환 (시뮬레이션)
        db = 20 * np.log10(rms + 1e-10) + 50  # 0~80 dB 범위로 조정
        return max(30, min(80, db))  # 30~80 dB 범위로 제한
    
    def test_scenario(self, scenario_name, audio_type, decibel_override=None):
        """시나리오 테스트"""
        print(f"\n{'='*80}")
        print(f"시나리오: {scenario_name}")
        print(f"{'='*80}")
        
        # 오디오 샘플 생성
        audio_data = self.generate_audio_sample(audio_type)
        
        # 데시벨 계산 또는 오버라이드
        if decibel_override is not None:
            decibel = decibel_override
        else:
            decibel = self.calculate_decibel(audio_data)
        
        print(f"📊 데시벨 레벨: {decibel:.1f} dB")
        
        # 판단 수행
        if self.use_api:
            result = self.test_via_api(audio_data, decibel, f"ESP32_TEST_{scenario_name}")
        else:
            result = self.detector.process_esp32_data(
                audio_data=audio_data,
                decibel_level=decibel,
                device_id=f"ESP32_TEST_{scenario_name}",
                timestamp=datetime.now()
            )
        
        # 결과 출력
        self.print_result(result)
        
        return result
    
    def test_via_api(self, audio_data, decibel, device_id):
        """API를 통한 테스트"""
        try:
            url = f"{self.api_url}/api/esp32/realtime/detect"
            
            payload = {
                "audio_data": audio_data.tolist(),
                "decibel_level": float(decibel),
                "device_id": device_id,
                "sample_rate": 16000
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "status": "error",
                    "message": f"API 오류: {response.status_code}",
                    "decibel_level": decibel
                }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "status": "error",
                "message": "API 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.",
                "decibel_level": decibel
            }
        except Exception as e:
            return {
                "success": False,
                "status": "error",
                "message": f"API 요청 실패: {str(e)}",
                "decibel_level": decibel
            }
    
    def print_result(self, result):
        """결과 출력"""
        status = result.get('status', 'unknown')
        decibel = result.get('decibel_level', 0)
        message = result.get('message', '')
        
        # 상태별 아이콘 및 색상
        status_icons = {
            'no_input': '🔇',
            'below_threshold': '⏸️',
            'auto': '✅',
            'pending': '📋',
            'error': '❌'
        }
        
        icon = status_icons.get(status, '❓')
        
        print(f"\n{icon} 상태: {status.upper()}")
        print(f"   데시벨: {decibel:.1f} dB")
        print(f"   메시지: {message}")
        
        if result.get('result'):
            detection_result = result['result']
            if detection_result.get('decision') == 'auto':
                is_failure = detection_result.get('result', {}).get('is_failure', False)
                confidence = detection_result.get('confidence', 0)
                print(f"   판단: {'⚠️ 고장' if is_failure else '✅ 정상'}")
                print(f"   신뢰도: {confidence:.1%}")
            elif detection_result.get('decision') == 'pending':
                pending_id = detection_result.get('pending_item_id')
                confidence = detection_result.get('confidence', 0)
                print(f"   보류 항목 ID: {pending_id}")
                print(f"   신뢰도: {confidence:.1%}")
        
        print()
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("\n🚀 테스트 시작...\n")
        
        results = []
        
        # 시나리오 1: 소리 입력 없음 (35~40 dB)
        print("\n" + "="*80)
        print("시나리오 1: 소리 입력 없음 (35~40 dB)")
        print("="*80)
        print("예상: 소리 입력 없음으로 판단, 알고리즘 실행 안 함")
        
        result1 = self.test_scenario(
            "소리_없음",
            "normal",
            decibel_override=37.5  # 35~40 범위 내
        )
        results.append(("소리 입력 없음", result1))
        time.sleep(1)
        
        # 시나리오 2: 판단 임계값 미달 (40~48 dB)
        print("\n" + "="*80)
        print("시나리오 2: 판단 임계값 미달 (40~48 dB)")
        print("="*80)
        print("예상: 판단 임계값 미달로 판단, 알고리즘 실행 안 함")
        
        result2 = self.test_scenario(
            "임계값_미달",
            "normal",
            decibel_override=45.0  # 40~48 범위 내
        )
        results.append(("임계값 미달", result2))
        time.sleep(1)
        
        # 시나리오 3: 정상 소리 (48 dB 이상, 높은 신뢰도)
        print("\n" + "="*80)
        print("시나리오 3: 정상 소리 (48 dB 이상, 높은 신뢰도)")
        print("="*80)
        print("예상: 알고리즘 판단 시작 → 자동 판단 (정상)")
        
        result3 = self.test_scenario(
            "정상_소리",
            "normal",
            decibel_override=55.0  # 48 이상
        )
        results.append(("정상 소리", result3))
        time.sleep(1)
        
        # 시나리오 4: 이상 소리 (48 dB 이상, 높은 신뢰도)
        print("\n" + "="*80)
        print("시나리오 4: 이상 소리 (48 dB 이상, 높은 신뢰도)")
        print("="*80)
        print("예상: 알고리즘 판단 시작 → 자동 판단 (고장)")
        
        result4 = self.test_scenario(
            "이상_소리",
            "anomaly",
            decibel_override=60.0  # 48 이상
        )
        results.append(("이상 소리", result4))
        time.sleep(1)
        
        # 시나리오 5: 낮은 신뢰도 소리 (48 dB 이상, 낮은 신뢰도)
        print("\n" + "="*80)
        print("시나리오 5: 낮은 신뢰도 소리 (48 dB 이상, 낮은 신뢰도)")
        print("="*80)
        print("예상: 알고리즘 판단 시작 → 보류 큐 추가")
        
        result5 = self.test_scenario(
            "낮은_신뢰도",
            "low_confidence",
            decibel_override=50.0  # 48 이상
        )
        results.append(("낮은 신뢰도", result5))
        time.sleep(1)
        
        # 통계 조회
        print("\n" + "="*80)
        print("통계 조회")
        print("="*80)
        
        if self.use_api:
            try:
                stats_url = f"{self.api_url}/api/esp32/realtime/statistics"
                response = requests.get(stats_url, timeout=10)
                if response.status_code == 200:
                    stats = response.json().get('statistics', {})
                    print(f"\n📊 통계:")
                    print(f"   총 판단: {stats.get('total_detections', 0)}")
                    print(f"   자동 판단: {stats.get('auto_count', 0)}")
                    print(f"   보류 항목: {stats.get('pending_count', 0)}")
                    print(f"   고장 감지: {stats.get('failure_count', 0)}")
                    print(f"   자동 판단률: {stats.get('auto_rate', 0):.1%}")
            except Exception as e:
                print(f"   통계 조회 실패: {e}")
        else:
            stats = self.detector.get_statistics()
            print(f"\n📊 통계:")
            print(f"   총 판단: {stats.get('total_detections', 0)}")
            print(f"   자동 판단: {stats.get('auto_count', 0)}")
            print(f"   보류 항목: {stats.get('pending_count', 0)}")
            print(f"   고장 감지: {stats.get('failure_count', 0)}")
            print(f"   자동 판단률: {stats.get('auto_rate', 0):.1%}")
        
        # 결과 요약
        print("\n" + "="*80)
        print("테스트 결과 요약")
        print("="*80)
        
        for name, result in results:
            status = result.get('status', 'unknown')
            success_icon = '✅' if result.get('success', True) else '❌'
            print(f"{success_icon} {name}: {status}")
        
        print("\n" + "="*80)
        print("✅ 테스트 완료!")
        print("="*80)
        print("\n💡 대시보드에서 확인:")
        print("   http://localhost:5000/static/dashboard-components/esp32-realtime-monitor.html")
        print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='ESP32 실시간 모니터링 시스템 테스트')
    parser.add_argument('--api', action='store_true', help='API를 통한 테스트 (서버 실행 필요)')
    parser.add_argument('--url', default='http://localhost:5000', help='API 서버 URL')
    
    args = parser.parse_args()
    
    tester = ESP32RealtimeTester(use_api=args.api, api_url=args.url)
    tester.run_all_tests()

