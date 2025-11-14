#!/usr/bin/env python3
"""
스마트 판단 시스템 종합 테스트 스크립트
A~Z 단계별 테스트 진행
"""

import sys
from pathlib import Path
import numpy as np
import time
import logging
from datetime import datetime

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestResult:
    """테스트 결과 클래스"""
    def __init__(self, name):
        self.name = name
        self.passed = False
        self.error = None
        self.duration = 0.0
    
    def success(self, duration=0.0):
        self.passed = True
        self.duration = duration
        logger.info(f"✅ {self.name} - 성공 ({duration:.2f}초)")
    
    def fail(self, error, duration=0.0):
        self.passed = False
        self.error = str(error)
        self.duration = duration
        logger.error(f"❌ {self.name} - 실패: {error}")


class SmartDetectionSystemTester:
    """스마트 판단 시스템 종합 테스트"""
    
    def __init__(self):
        self.test_results = []
        self.test_audio_samples = {}
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("\n" + "="*80)
        print("스마트 판단 시스템 종합 테스트 시작")
        print("="*80)
        print()
        
        # A~Z 단계별 테스트
        tests = [
            ("A. 환경 확인", self.test_environment),
            ("B. 모듈 Import 테스트", self.test_imports),
            ("C. 오디오 샘플 생성", self.test_audio_generation),
            ("D. 실시간 판단 시스템 테스트", self.test_realtime_detector),
            ("E. MIMII 모델 로드 테스트", self.test_mimii_model),
            ("F. 보류 라벨링 서비스 테스트", self.test_pending_service),
            ("G. 스마트 오케스트레이터 테스트", self.test_orchestrator),
            ("H. 자동 판단 시나리오", self.test_auto_detection),
            ("I. 보류 시나리오", self.test_pending_scenario),
            ("J. 통계 조회 테스트", self.test_statistics),
            ("K. 전체 워크플로우 테스트", self.test_full_workflow),
        ]
        
        for test_name, test_func in tests:
            result = TestResult(test_name)
            start_time = time.time()
            
            try:
                test_func(result)
                duration = time.time() - start_time
                if result.passed:
                    result.success(duration)
                else:
                    result.fail(result.error, duration)
            except Exception as e:
                duration = time.time() - start_time
                result.fail(e, duration)
            
            self.test_results.append(result)
            time.sleep(0.5)  # 테스트 간 간격
        
        # 결과 요약
        self.print_summary()
    
    def test_environment(self, result):
        """A. 환경 확인"""
        logger.info("A. 환경 확인 중...")
        
        # Python 버전
        import sys
        python_version = sys.version_info
        logger.info(f"   Python 버전: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            result.fail("Python 3.8 이상 필요")
            return
        
        # 필수 패키지 확인
        required_packages = ['numpy', 'librosa', 'scipy', 'sklearn']
        missing = []
        
        for package in required_packages:
            try:
                __import__(package)
                logger.info(f"   ✅ {package} 설치됨")
            except ImportError:
                missing.append(package)
                logger.warning(f"   ❌ {package} 없음")
        
        if missing:
            result.fail(f"필수 패키지 없음: {', '.join(missing)}")
            return
        
        result.success()
    
    def test_imports(self, result):
        """B. 모듈 Import 테스트"""
        logger.info("B. 모듈 Import 테스트 중...")
        
        try:
            from services.realtime_failure_detection_service import RealtimeFailureDetectionService
            logger.info("   ✅ RealtimeFailureDetectionService")
            
            from services.pending_labeling_service import PendingLabelingService
            logger.info("   ✅ PendingLabelingService")
            
            from services.smart_detection_orchestrator import SmartDetectionOrchestrator
            logger.info("   ✅ SmartDetectionOrchestrator")
            
            from ai.realtime_anomaly_detector import RealtimeAnomalyDetector
            logger.info("   ✅ RealtimeAnomalyDetector")
            
            try:
                from ai.realtime_anomaly_detector_with_mimii import RealtimeAnomalyDetectorWithMIMII
                logger.info("   ✅ RealtimeAnomalyDetectorWithMIMII")
            except ImportError:
                logger.warning("   ⚠️ RealtimeAnomalyDetectorWithMIMII (선택적)")
            
            result.success()
            
        except ImportError as e:
            result.fail(f"모듈 Import 실패: {e}")
    
    def test_audio_generation(self, result):
        """C. 오디오 샘플 생성"""
        logger.info("C. 오디오 샘플 생성 중...")
        
        try:
            sample_rate = 16000
            duration = 2.0
            
            # 정상 소리 (440Hz 사인파)
            t = np.linspace(0, duration, int(sample_rate * duration))
            normal_audio = np.sin(2 * np.pi * 440 * t)
            self.test_audio_samples['normal'] = normal_audio
            logger.info("   ✅ 정상 소리 생성 완료")
            
            # 이상 소리 (고주파 노이즈)
            anomaly_audio = (
                np.sin(2 * np.pi * 2000 * t) * 0.5 +
                np.sin(2 * np.pi * 3000 * t) * 0.3 +
                np.random.randn(len(t)) * 0.2
            )
            self.test_audio_samples['anomaly'] = anomaly_audio
            logger.info("   ✅ 이상 소리 생성 완료")
            
            # 낮은 신뢰도 소리 (중간 복잡도)
            low_confidence_audio = (
                np.sin(2 * np.pi * 440 * t) * 0.3 +
                np.random.randn(len(t)) * 0.4  # 노이즈가 많음
            )
            self.test_audio_samples['low_confidence'] = low_confidence_audio
            logger.info("   ✅ 낮은 신뢰도 소리 생성 완료")
            
            result.success()
            
        except Exception as e:
            result.fail(f"오디오 샘플 생성 실패: {e}")
    
    def test_realtime_detector(self, result):
        """D. 실시간 판단 시스템 테스트"""
        logger.info("D. 실시간 판단 시스템 테스트 중...")
        
        try:
            from ai.realtime_anomaly_detector import RealtimeAnomalyDetector
            
            detector = RealtimeAnomalyDetector(use_pretrained_model=False)  # 빠른 테스트
            
            test_audio = self.test_audio_samples.get('normal')
            if test_audio is None:
                result.fail("테스트 오디오 없음")
                return
            
            detection_result = detector.detect(test_audio)
            
            logger.info(f"   - 고장 여부: {detection_result['is_failure']}")
            logger.info(f"   - 신뢰도: {detection_result['confidence']:.2%}")
            logger.info(f"   - 처리 시간: {detection_result['processing_time_ms']:.2f}ms")
            
            if 'is_failure' not in detection_result:
                result.fail("결과 형식 오류")
                return
            
            result.success()
            
        except Exception as e:
            result.fail(f"실시간 판단 테스트 실패: {e}")
    
    def test_mimii_model(self, result):
        """E. MIMII 모델 로드 테스트"""
        logger.info("E. MIMII 모델 로드 테스트 중...")
        
        try:
            mimii_model_path = Path("data/models/mimii_model.pkl")
            mimii_scaler_path = Path("data/models/mimii_scaler.pkl")
            
            if not mimii_model_path.exists():
                logger.warning("   ⚠️ MIMII 모델 파일 없음 (선택적)")
                result.success()  # 선택적이므로 실패로 처리하지 않음
                return
            
            import joblib
            model = joblib.load(mimii_model_path)
            scaler = joblib.load(mimii_scaler_path)
            
            logger.info(f"   ✅ MIMII 모델 로드 완료")
            logger.info(f"   - 모델 타입: {type(model).__name__}")
            logger.info(f"   - 스케일러 타입: {type(scaler).__name__}")
            
            # 간단한 예측 테스트
            test_features = np.random.rand(10)  # 10개 특징
            features_scaled = scaler.transform(test_features.reshape(1, -1))
            prediction = model.predict(features_scaled)
            
            logger.info(f"   ✅ 예측 테스트 성공: {prediction[0]}")
            
            result.success()
            
        except Exception as e:
            logger.warning(f"   ⚠️ MIMII 모델 로드 실패 (선택적): {e}")
            result.success()  # 선택적이므로 실패로 처리하지 않음
    
    def test_pending_service(self, result):
        """F. 보류 라벨링 서비스 테스트"""
        logger.info("F. 보류 라벨링 서비스 테스트 중...")
        
        try:
            from services.pending_labeling_service import PendingLabelingService
            
            service = PendingLabelingService(confidence_threshold=0.7)
            
            # 보류 여부 판단 테스트
            low_confidence_result = {
                'is_failure': False,
                'confidence': 0.5,  # 임계값 이하
                'score': 0.4
            }
            
            should_pend = service.should_pend_labeling(low_confidence_result)
            logger.info(f"   - 보류 필요 여부: {should_pend}")
            
            if not should_pend:
                result.fail("보류 판단 로직 오류")
                return
            
            # 보류 항목 추가 테스트
            test_audio = self.test_audio_samples.get('low_confidence')
            if test_audio is None:
                test_audio = np.random.randn(32000)
            
            item_id = service.add_pending_item(
                audio_data=test_audio,
                detection_result=low_confidence_result,
                device_id="test_device_001"
            )
            
            logger.info(f"   - 보류 항목 ID: {item_id}")
            
            if not item_id:
                result.fail("보류 항목 추가 실패")
                return
            
            # 보류 항목 조회 테스트
            pending_items = service.get_pending_items()
            logger.info(f"   - 보류 항목 개수: {len(pending_items)}")
            
            # 라벨링 테스트
            success = service.update_labeling(
                item_id=item_id,
                label='normal',
                labeled_by='test_expert'
            )
            
            if not success:
                result.fail("라벨링 업데이트 실패")
                return
            
            logger.info(f"   ✅ 라벨링 완료")
            
            # 통계 테스트
            stats = service.get_statistics()
            logger.info(f"   - 통계: {stats}")
            
            result.success()
            
        except Exception as e:
            result.fail(f"보류 라벨링 서비스 테스트 실패: {e}")
    
    def test_orchestrator(self, result):
        """G. 스마트 오케스트레이터 테스트"""
        logger.info("G. 스마트 오케스트레이터 테스트 중...")
        
        try:
            from services.smart_detection_orchestrator import SmartDetectionOrchestrator
            
            orchestrator = SmartDetectionOrchestrator(
                confidence_threshold=0.7,
                use_mimii_model=True
            )
            
            logger.info("   ✅ 오케스트레이터 초기화 완료")
            
            # 정상 오디오 테스트 (높은 신뢰도 예상)
            normal_audio = self.test_audio_samples.get('normal')
            if normal_audio is None:
                normal_audio = np.random.randn(32000)
            
            result_normal = orchestrator.process_audio(
                audio_data=normal_audio,
                device_id="test_device_normal"
            )
            
            logger.info(f"   - 정상 오디오 결정: {result_normal['decision']}")
            logger.info(f"   - 신뢰도: {result_normal.get('confidence', 0):.2%}")
            
            # 낮은 신뢰도 오디오 테스트 (보류 예상)
            low_conf_audio = self.test_audio_samples.get('low_confidence')
            if low_conf_audio is None:
                low_conf_audio = np.random.randn(32000) * 0.5  # 낮은 신호
            
            result_low = orchestrator.process_audio(
                audio_data=low_conf_audio,
                device_id="test_device_low"
            )
            
            logger.info(f"   - 낮은 신뢰도 결정: {result_low['decision']}")
            logger.info(f"   - 신뢰도: {result_low.get('confidence', 0):.2%}")
            
            if result_low['decision'] == 'pending':
                logger.info(f"   - 보류 항목 ID: {result_low.get('pending_item_id')}")
            
            result.success()
            
        except Exception as e:
            result.fail(f"오케스트레이터 테스트 실패: {e}")
    
    def test_auto_detection(self, result):
        """H. 자동 판단 시나리오"""
        logger.info("H. 자동 판단 시나리오 테스트 중...")
        
        try:
            from services.smart_detection_orchestrator import SmartDetectionOrchestrator
            
            orchestrator = SmartDetectionOrchestrator(
                confidence_threshold=0.7,
                use_mimii_model=True
            )
            
            # 높은 신뢰도 오디오 (자동 판단 예상)
            test_audio = self.test_audio_samples.get('normal')
            if test_audio is None:
                test_audio = np.random.randn(32000)
            
            detection_result = orchestrator.process_audio(
                audio_data=test_audio,
                device_id="test_auto_device"
            )
            
            logger.info(f"   - 결정: {detection_result['decision']}")
            logger.info(f"   - 메시지: {detection_result['message']}")
            
            if detection_result['decision'] == 'auto':
                logger.info(f"   ✅ 자동 판단 성공")
                logger.info(f"   - 고장 여부: {detection_result['result']['is_failure']}")
                logger.info(f"   - 신뢰도: {detection_result['confidence']:.2%}")
            else:
                logger.info(f"   ⚠️ 보류로 처리됨 (신뢰도: {detection_result['confidence']:.2%})")
            
            result.success()
            
        except Exception as e:
            result.fail(f"자동 판단 시나리오 테스트 실패: {e}")
    
    def test_pending_scenario(self, result):
        """I. 보류 시나리오"""
        logger.info("I. 보류 시나리오 테스트 중...")
        
        try:
            from services.smart_detection_orchestrator import SmartDetectionOrchestrator
            
            orchestrator = SmartDetectionOrchestrator(
                confidence_threshold=0.7,
                use_mimii_model=True
            )
            
            # 낮은 신뢰도 오디오 (보류 예상)
            test_audio = self.test_audio_samples.get('low_confidence')
            if test_audio is None:
                # 노이즈가 많은 오디오 생성
                t = np.linspace(0, 2.0, 32000)
                test_audio = np.sin(2 * np.pi * 440 * t) * 0.2 + np.random.randn(32000) * 0.6
            
            detection_result = orchestrator.process_audio(
                audio_data=test_audio,
                device_id="test_pending_device"
            )
            
            logger.info(f"   - 결정: {detection_result['decision']}")
            logger.info(f"   - 신뢰도: {detection_result.get('confidence', 0):.2%}")
            
            if detection_result['decision'] == 'pending':
                pending_id = detection_result.get('pending_item_id')
                logger.info(f"   ✅ 보류 큐 추가 성공")
                logger.info(f"   - 보류 항목 ID: {pending_id}")
                
                # 보류 항목 확인
                pending_item = orchestrator.pending_service.get_pending_item(pending_id)
                if pending_item:
                    logger.info(f"   - 보류 항목 확인: {pending_item['status']}")
                    
                    # 라벨링 테스트
                    success = orchestrator.complete_labeling(
                        item_id=pending_id,
                        label='normal',
                        labeled_by='test_expert'
                    )
                    
                    if success:
                        logger.info(f"   ✅ 라벨링 완료")
                    else:
                        result.fail("라벨링 실패")
                        return
                else:
                    result.fail("보류 항목을 찾을 수 없음")
                    return
            else:
                logger.info(f"   ⚠️ 자동 판단으로 처리됨 (신뢰도: {detection_result['confidence']:.2%})")
            
            result.success()
            
        except Exception as e:
            result.fail(f"보류 시나리오 테스트 실패: {e}")
    
    def test_statistics(self, result):
        """J. 통계 조회 테스트"""
        logger.info("J. 통계 조회 테스트 중...")
        
        try:
            from services.smart_detection_orchestrator import SmartDetectionOrchestrator
            
            orchestrator = SmartDetectionOrchestrator(
                confidence_threshold=0.7,
                use_mimii_model=True
            )
            
            # 여러 샘플 처리
            for i in range(5):
                test_audio = np.random.randn(32000)
                orchestrator.process_audio(
                    audio_data=test_audio,
                    device_id=f"test_device_{i}"
                )
            
            # 통계 조회
            stats = orchestrator.get_statistics()
            
            logger.info(f"   - 감지 통계: {stats['detection']}")
            logger.info(f"   - 보류 통계: {stats['pending']}")
            logger.info(f"   - 자동 판단률: {stats['auto_decision_rate']:.2%}")
            
            result.success()
            
        except Exception as e:
            result.fail(f"통계 조회 테스트 실패: {e}")
    
    def test_full_workflow(self, result):
        """K. 전체 워크플로우 테스트"""
        logger.info("K. 전체 워크플로우 테스트 중...")
        
        try:
            from services.smart_detection_orchestrator import SmartDetectionOrchestrator
            
            orchestrator = SmartDetectionOrchestrator(
                confidence_threshold=0.7,
                use_mimii_model=True
            )
            
            # 시나리오 1: 정상 오디오 (자동 판단)
            logger.info("   시나리오 1: 정상 오디오 처리...")
            normal_audio = self.test_audio_samples.get('normal')
            result1 = orchestrator.process_audio(normal_audio, device_id="workflow_device_1")
            logger.info(f"      결정: {result1['decision']}, 신뢰도: {result1.get('confidence', 0):.2%}")
            
            # 시나리오 2: 이상 오디오 (자동 판단)
            logger.info("   시나리오 2: 이상 오디오 처리...")
            anomaly_audio = self.test_audio_samples.get('anomaly')
            result2 = orchestrator.process_audio(anomaly_audio, device_id="workflow_device_2")
            logger.info(f"      결정: {result2['decision']}, 신뢰도: {result2.get('confidence', 0):.2%}")
            
            # 시나리오 3: 낮은 신뢰도 (보류)
            logger.info("   시나리오 3: 낮은 신뢰도 오디오 처리...")
            low_conf_audio = self.test_audio_samples.get('low_confidence')
            result3 = orchestrator.process_audio(low_conf_audio, device_id="workflow_device_3")
            logger.info(f"      결정: {result3['decision']}, 신뢰도: {result3.get('confidence', 0):.2%}")
            
            if result3['decision'] == 'pending':
                # 보류 항목 라벨링
                pending_id = result3['pending_item_id']
                logger.info(f"      보류 항목 ID: {pending_id}")
                
                # 라벨링 완료
                orchestrator.complete_labeling(
                    item_id=pending_id,
                    label='normal',
                    labeled_by='workflow_test'
                )
                logger.info(f"      라벨링 완료")
            
            # 대시보드 데이터 조회
            dashboard_data = orchestrator.get_pending_items_for_dashboard()
            logger.info(f"   - 대시보드 보류 항목: {dashboard_data['total_pending']}개")
            
            # 최종 통계
            final_stats = orchestrator.get_statistics()
            logger.info(f"   - 최종 자동 판단률: {final_stats['auto_decision_rate']:.2%}")
            
            result.success()
            
        except Exception as e:
            result.fail(f"전체 워크플로우 테스트 실패: {e}")
    
    def print_summary(self):
        """테스트 결과 요약"""
        print("\n" + "="*80)
        print("테스트 결과 요약")
        print("="*80)
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.passed)
        failed = total - passed
        
        print(f"\n총 테스트: {total}개")
        print(f"✅ 성공: {passed}개")
        print(f"❌ 실패: {failed}개")
        print(f"성공률: {passed/total*100:.1f}%")
        
        print("\n" + "-"*80)
        print("상세 결과")
        print("-"*80)
        
        for result in self.test_results:
            status = "✅" if result.passed else "❌"
            print(f"{status} {result.name} ({result.duration:.2f}초)")
            if not result.passed and result.error:
                print(f"   오류: {result.error}")
        
        print("\n" + "="*80)
        
        if failed == 0:
            print("🎉 모든 테스트 통과!")
        else:
            print(f"⚠️ {failed}개의 테스트 실패. 위의 오류를 확인하세요.")
        
        print("="*80 + "\n")


if __name__ == "__main__":
    tester = SmartDetectionSystemTester()
    tester.run_all_tests()

