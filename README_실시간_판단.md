# 실시간 고장 판단 시스템

## 🎯 개요

들어오는 소리를 **오픈소스 AI + 간단한 알고리즘**으로 즉시 고장/비고장 판단하는 시스템입니다.

**데이터 축적 없이 바로 사용 가능**하며, 나중에 데이터가 쌓이면 점진적으로 정확도를 개선할 수 있습니다.

---

## 📊 예상 정확도

| 방법 | 정확도 |
|------|--------|
| 오픈소스 모델 (YAMNet) | 70-80% |
| 특징 기반 알고리즘 | 75-85% |
| **앙상블 (결합)** | **80-90%** |

---

## 🚀 빠른 시작

### 1. 테스트 실행

```bash
# 가상환경 활성화
source venv/bin/activate

# 테스트 실행
python scripts/test_realtime_detection.py
```

### 2. Python에서 사용

```python
from ai.realtime_anomaly_detector import RealtimeAnomalyDetector
import numpy as np

# 초기화
detector = RealtimeAnomalyDetector(
    sample_rate=16000,
    window_size=2.0,  # 2초 윈도우
    use_pretrained_model=True  # YAMNet 사용
)

# 오디오 데이터
audio_data = np.array([...])  # 실제 오디오 샘플

# 고장 판단
result = detector.detect(audio_data)

if result['is_failure']:
    print(f"⚠️ 고장 감지! (신뢰도: {result['confidence']:.2%})")
else:
    print(f"✅ 정상 (신뢰도: {result['confidence']:.2%})")
```

### 3. API 사용 (ESP32에서)

```bash
curl -X POST http://localhost:5000/api/realtime/detect \
  -H "Content-Type: application/json" \
  -d '{
    "audio_data": [0.1, 0.2, 0.3, ...],
    "device_id": "ESP32_001",
    "sample_rate": 16000
  }'
```

---

## 📦 설치

```bash
# 필수 패키지 (이미 requirements.txt에 포함됨)
pip install tensorflow-hub  # YAMNet 사용 시
```

---

## ⚙️ 특징

### 1. 오픈소스 사전 훈련 모델 (YAMNet)
- Google의 오픈소스 오디오 분류 모델
- 521개 클래스 분류
- 사전 훈련됨 (추가 학습 불필요)

### 2. 특징 기반 알고리즘
- 에너지 (RMS, 에너지 비율)
- 주파수 도메인 (스펙트럼 중심, 롤오프)
- Zero Crossing Rate (ZCR)
- 고주파 에너지 비율
- MFCC

### 3. 앙상블
- 오픈소스 모델: 40% 가중치
- 특징 기반: 60% 가중치

### 4. 동적 조정
- 최근 10개 정상 샘플로 정상 기준값 자동 업데이트
- 환경 변화에 자동 적응

---

## 📈 성능

- **처리 시간**: 약 10-50ms (2초 오디오 기준)
- **메모리**: 약 50-100MB (YAMNet 로드 시)
- **CPU 사용**: 중간

---

## 🔧 설정

### 임계값 조정

```python
detector = RealtimeAnomalyDetector()

# 임계값 수정
detector.thresholds['energy_ratio'] = 2.5  # 더 민감하게
detector.thresholds['high_freq_energy'] = 0.25  # 덜 민감하게
```

### YAMNet 비활성화 (더 빠른 처리)

```python
detector = RealtimeAnomalyDetector(use_pretrained_model=False)
# 특징 기반 알고리즘만 사용 (더 빠름, 약간 낮은 정확도)
```

---

## 📝 API 엔드포인트

### POST /api/realtime/detect
실시간 고장 판단

**Request:**
```json
{
  "audio_data": [0.1, 0.2, 0.3, ...],
  "device_id": "ESP32_001",
  "sample_rate": 16000
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "is_failure": false,
    "confidence": 0.85,
    "score": 0.25,
    "should_alert": false,
    "processing_time_ms": 15.2
  }
}
```

### GET /api/realtime/statistics
통계 정보 조회

**Query Parameters:**
- `device_id`: 디바이스 ID (선택적)
- `hours`: 조회 기간 (시간, 기본값: 24)

---

## 🎓 사용 예시

### ESP32에서 실시간 모니터링

```cpp
// ESP32 코드 (간단 예시)
void sendAudioForDetection(float* audio_buffer, int length) {
    // HTTP POST 요청으로 오디오 데이터 전송
    // 서버에서 자동으로 고장/비고장 판단
}
```

### Python 서비스에서 사용

```python
from services.realtime_failure_detection_service import RealtimeFailureDetectionService

service = RealtimeFailureDetectionService()

# 오디오 수신
result = service.process_audio(audio_data, device_id="ESP32_001")

if result['should_alert']:
    # 알림 발송
    send_notification("고장 감지!", device_id="ESP32_001")
```

---

## 🔮 향후 개선

1. **데이터 축적 후**
   - 실제 고장 데이터로 임계값 조정
   - 커스텀 모델 학습 (선택적)

2. **정확도 향상**
   - 더 많은 특징 추가
   - 앙상블 가중치 최적화

3. **최적화**
   - 처리 시간 단축
   - 메모리 사용량 감소

---

## 📚 참고 문서

- `docs/실시간_고장_판단_시스템_가이드.md` - 상세 가이드
- `ai/realtime_anomaly_detector.py` - 핵심 알고리즘
- `services/realtime_failure_detection_service.py` - 서비스 레이어

