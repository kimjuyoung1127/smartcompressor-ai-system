# 스마트 판단 시스템 테스트 가이드 (A~Z)

## 개요

스마트 판단 시스템을 단계별로 테스트하는 상세 가이드입니다.

---

## 테스트 준비

### 1. 가상환경 활성화

```bash
cd /root/smartcompressor-ai-system
source venv/bin/activate
```

### 2. 필수 패키지 확인

```bash
python -c "import numpy, librosa, scipy, sklearn; print('✅ 모든 패키지 설치됨')"
```

---

## 테스트 실행

### 자동 테스트 스크립트 실행

```bash
python scripts/test_smart_detection_system.py
```

---

## A~Z 단계별 테스트 상세 설명

### A. 환경 확인 (Environment Check)

**목적**: Python 환경과 필수 패키지가 제대로 설치되어 있는지 확인

**체크 항목**:
- Python 버전 (3.8 이상)
- 필수 패키지: numpy, librosa, scipy, sklearn

**예상 결과**:
```
✅ Python 버전: 3.12.x
✅ numpy 설치됨
✅ librosa 설치됨
✅ scipy 설치됨
✅ sklearn 설치됨
```

**실패 시 해결**:
```bash
pip install numpy librosa scipy scikit-learn
```

---

### B. 모듈 Import 테스트 (Module Import Test)

**목적**: 모든 모듈이 정상적으로 import되는지 확인

**테스트 모듈**:
- `RealtimeFailureDetectionService`
- `PendingLabelingService`
- `SmartDetectionOrchestrator`
- `RealtimeAnomalyDetector`
- `RealtimeAnomalyDetectorWithMIMII` (선택적)

**예상 결과**:
```
✅ RealtimeFailureDetectionService
✅ PendingLabelingService
✅ SmartDetectionOrchestrator
✅ RealtimeAnomalyDetector
```

**실패 시 해결**:
- 파일 경로 확인
- import 경로 확인

---

### C. 오디오 샘플 생성 (Audio Sample Generation)

**목적**: 테스트용 오디오 샘플 생성

**생성되는 샘플**:
1. **정상 소리** (440Hz 사인파)
   - 용도: 자동 판단 테스트
   - 예상: 높은 신뢰도, 정상 판단

2. **이상 소리** (고주파 노이즈)
   - 용도: 고장 감지 테스트
   - 예상: 높은 신뢰도, 고장 판단

3. **낮은 신뢰도 소리** (노이즈가 많은 혼합)
   - 용도: 보류 테스트
   - 예상: 낮은 신뢰도, 보류 처리

**예상 결과**:
```
✅ 정상 소리 생성 완료
✅ 이상 소리 생성 완료
✅ 낮은 신뢰도 소리 생성 완료
```

---

### D. 실시간 판단 시스템 테스트 (Realtime Detector Test)

**목적**: 기본 실시간 판단 시스템이 정상 작동하는지 확인

**테스트 내용**:
- 오디오 데이터 입력
- 특징 추출
- 판단 수행
- 결과 반환

**예상 결과**:
```
- 고장 여부: False
- 신뢰도: 0.XX%
- 처리 시간: XX.XXms
```

**확인 사항**:
- `is_failure` 필드 존재
- `confidence` 값이 0-1 사이
- 처리 시간이 100ms 이하

---

### E. MIMII 모델 로드 테스트 (MIMII Model Load Test)

**목적**: 기존 MIMII 모델 (92% 정확도)이 정상 로드되는지 확인

**테스트 내용**:
- 모델 파일 존재 확인
- 모델 로드
- 스케일러 로드
- 간단한 예측 테스트

**예상 결과**:
```
✅ MIMII 모델 로드 완료
- 모델 타입: RandomForestClassifier
- 스케일러 타입: StandardScaler
✅ 예측 테스트 성공: X
```

**파일 위치**:
- `data/models/mimii_model.pkl`
- `data/models/mimii_scaler.pkl`

**실패 시**: 모델 파일이 없어도 계속 진행 (선택적)

---

### F. 보류 라벨링 서비스 테스트 (Pending Labeling Service Test)

**목적**: 보류 라벨링 서비스가 정상 작동하는지 확인

**테스트 내용**:
1. **보류 판단 로직**
   - 신뢰도 0.5 → 보류 필요 여부 확인

2. **보류 항목 추가**
   - 오디오 데이터 저장
   - 보류 항목 생성
   - 항목 ID 반환

3. **보류 항목 조회**
   - 목록 조회
   - 필터링

4. **라벨링 업데이트**
   - 라벨 추가
   - 상태 변경

5. **통계 조회**

**예상 결과**:
```
- 보류 필요 여부: True
- 보류 항목 ID: pending_000001_XXXXXX
- 보류 항목 개수: 1
✅ 라벨링 완료
- 통계: {...}
```

**확인 사항**:
- 보류 항목이 `data/pending_labeling/`에 저장됨
- 라벨링 후 상태가 `completed`로 변경됨

---

### G. 스마트 오케스트레이터 테스트 (Smart Orchestrator Test)

**목적**: 오케스트레이터가 전체 워크플로우를 정상 관리하는지 확인

**테스트 내용**:
1. 오케스트레이터 초기화
2. 정상 오디오 처리 (자동 판단 예상)
3. 낮은 신뢰도 오디오 처리 (보류 예상)

**예상 결과**:
```
✅ 오케스트레이터 초기화 완료
- 정상 오디오 결정: auto
- 신뢰도: 0.XX%
- 낮은 신뢰도 결정: pending
- 신뢰도: 0.XX%
- 보류 항목 ID: pending_XXXXXX
```

**확인 사항**:
- 신뢰도 높으면 `decision: 'auto'`
- 신뢰도 낮으면 `decision: 'pending'`

---

### H. 자동 판단 시나리오 (Auto Detection Scenario)

**목적**: 높은 신뢰도 데이터가 자동으로 판단되는지 확인

**시나리오**:
- 정상 오디오 입력
- 신뢰도 ≥ 70% (임계값)
- 자동 판단 완료

**예상 결과**:
```
- 결정: auto
- 메시지: 자동 판단 완료: 정상
✅ 자동 판단 성공
- 고장 여부: False
- 신뢰도: 0.XX%
```

**확인 사항**:
- `decision`이 `'auto'`
- `pending_item_id`가 `None`
- 즉시 결과 반환

---

### I. 보류 시나리오 (Pending Scenario)

**목적**: 낮은 신뢰도 데이터가 보류 큐에 추가되고 라벨링되는지 확인

**시나리오**:
1. 낮은 신뢰도 오디오 입력
2. 신뢰도 < 70% → 보류 큐 추가
3. 보류 항목 확인
4. 라벨링 완료

**예상 결과**:
```
- 결정: pending
- 신뢰도: 0.XX%
✅ 보류 큐 추가 성공
- 보류 항목 ID: pending_XXXXXX
- 보류 항목 확인: pending
✅ 라벨링 완료
```

**확인 사항**:
- `decision`이 `'pending'`
- `pending_item_id`가 반환됨
- 오디오 파일이 저장됨
- 라벨링 후 상태가 `completed`로 변경

---

### J. 통계 조회 테스트 (Statistics Test)

**목적**: 통계 조회 기능이 정상 작동하는지 확인

**테스트 내용**:
- 여러 샘플 처리
- 통계 조회
- 자동 판단률 계산

**예상 결과**:
```
- 감지 통계: {...}
- 보류 통계: {...}
- 자동 판단률: 0.XX%
```

**확인 사항**:
- 감지 통계에 총 샘플 수 표시
- 보류 통계에 보류/완료/거부 개수 표시
- 자동 판단률이 계산됨

---

### K. 전체 워크플로우 테스트 (Full Workflow Test)

**목적**: 전체 시스템이 실제 시나리오에서 정상 작동하는지 확인

**시나리오**:
1. **시나리오 1**: 정상 오디오 → 자동 판단
2. **시나리오 2**: 이상 오디오 → 자동 판단
3. **시나리오 3**: 낮은 신뢰도 → 보류 → 라벨링

**예상 결과**:
```
시나리오 1: 정상 오디오 처리...
   결정: auto, 신뢰도: 0.XX%
시나리오 2: 이상 오디오 처리...
   결정: auto, 신뢰도: 0.XX%
시나리오 3: 낮은 신뢰도 오디오 처리...
   결정: pending, 신뢰도: 0.XX%
   보류 항목 ID: pending_XXXXXX
   라벨링 완료
- 대시보드 보류 항목: X개
- 최종 자동 판단률: 0.XX%
```

**확인 사항**:
- 모든 시나리오가 정상 처리됨
- 자동 판단과 보류가 적절히 분리됨
- 라벨링이 완료됨
- 통계가 정확함

---

## 수동 테스트 (선택적)

### API 테스트

```bash
# 1. 스마트 판단 API 테스트
curl -X POST http://localhost:5000/api/smart/detect \
  -H "Content-Type: application/json" \
  -d '{
    "audio_data": [0.1, 0.2, 0.3],
    "device_id": "test_device"
  }'

# 2. 보류 항목 조회
curl http://localhost:5000/api/pending/items

# 3. 통계 조회
curl http://localhost:5000/api/smart/detect/statistics
```

### 대시보드 테스트

```
http://localhost:5000/static/dashboard-components/pending-labeling-widget.html
```

---

## 예상 테스트 결과

### 성공적인 테스트

```
총 테스트: 11개
✅ 성공: 11개
❌ 실패: 0개
성공률: 100.0%

🎉 모든 테스트 통과!
```

### 실패 가능한 테스트

1. **MIMII 모델 없음** (선택적)
   - 모델 파일이 없어도 계속 진행
   - 폴백 시스템 사용

2. **패키지 없음**
   - `pip install`로 설치

3. **파일 경로 오류**
   - 프로젝트 루트에서 실행 확인

---

## 문제 해결

### 문제 1: ImportError

```bash
# 해결: 프로젝트 루트에서 실행
cd /root/smartcompressor-ai-system
python scripts/test_smart_detection_system.py
```

### 문제 2: 모델 파일 없음

```bash
# 해결: 모델 파일 확인
ls data/models/
# mimii_model.pkl이 없어도 계속 진행 가능 (폴백 사용)
```

### 문제 3: 오디오 파일 저장 실패

```bash
# 해결: 디렉토리 권한 확인
mkdir -p data/pending_labeling
chmod 755 data/pending_labeling
```

---

## 테스트 후 확인 사항

### 생성된 파일 확인

```bash
# 보류 오디오 파일
ls data/pending_labeling/*.wav

# 보류 항목이 정상 저장되었는지 확인
```

### 로그 확인

테스트 중 생성된 로그를 확인하여 각 단계의 상세 정보를 볼 수 있습니다.

---

## 다음 단계

테스트 완료 후:
1. ✅ 시스템 정상 작동 확인
2. 🔄 실제 ESP32 데이터로 테스트
3. 📊 대시보드 통합 확인
4. 🔄 재학습 파이프라인 연동

