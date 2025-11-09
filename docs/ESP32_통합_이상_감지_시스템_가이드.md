# ESP32 통합 이상 감지 시스템 가이드

## 📋 개요

ESP32 통합 이상 감지 시스템은 ESP32에서 수신한 오디오 데이터를 **모듈화된 이상 감지 시스템**으로 처리하는 통합 서비스입니다.

### 주요 기능

1. **ESP32 오디오 데이터 수신 및 전처리**
2. **데이터 품질 검증** (길이, 신호 레벨, 클리핑, 무음 구간)
3. **모듈화된 이상 감지 시스템으로 처리**
   - DecibelFilter: 데시벨 기반 1차 필터링
   - FeatureExtractor: 오디오 특징 추출
   - SpectralAnomalyScorer: 스펙트럼 이상 점수 계산
   - FailureTypeClassifier: 고장 유형 분류
4. **결과 저장 및 통계 수집**

---

## 🚀 빠른 시작

### 1. 서버 시작

```bash
# 가상 환경 활성화
source venv/bin/activate

# 서버 시작
python app.py
```

### 2. 테스트 실행

```bash
# 테스트 스크립트 실행
python scripts/test_esp32_integrated_detection.py
```

---

## 📡 API 엔드포인트

### 1. 이상 감지 (`POST /api/esp32/integrated/detect`)

ESP32 오디오 데이터를 받아서 이상 감지 수행

**요청 형식:**
```
POST /api/esp32/integrated/detect
Headers:
  - X-Device-ID: 디바이스 ID (필수)
  - X-Sample-Rate: 샘플링 레이트 (선택, 기본 16000)
  - X-Decibel-Level: 데시벨 레벨 (선택, 자동 계산)
Body: 오디오 바이트 데이터 (raw binary)
```

**응답 형식:**
```json
{
  "success": true,
  "device_id": "ESP32_001",
  "timestamp": "2024-01-01T12:00:00",
  "detection_result": {
    "is_anomaly": false,
    "confidence": 0.95,
    "anomaly_score": 0.15,
    "anomaly_type": "normal",
    "message": "정상",
    "individual_scores": {
      "spectral_centroid": 0.1,
      "rms_energy": 0.05,
      "high_freq_energy": 0.02
    }
  },
  "data_quality": {
    "is_valid": true,
    "issues": [],
    "metrics": {
      "length": 80000,
      "max_amplitude": 5000,
      "rms_level": 1500,
      "clipping_ratio": 0.0,
      "silence_ratio": 0.05
    }
  },
  "processing_time_ms": 45.2
}
```

**예제 (Python):**
```python
import requests

audio_bytes = b'...'  # 오디오 바이트 데이터

headers = {
    'X-Device-ID': 'ESP32_001',
    'X-Sample-Rate': '16000',
    'X-Decibel-Level': '50.0'
}

response = requests.post(
    'http://localhost:5000/api/esp32/integrated/detect',
    data=audio_bytes,
    headers=headers
)

result = response.json()
print(result)
```

---

### 2. 통계 조회 (`GET /api/esp32/integrated/statistics`)

처리 통계 정보 조회

**응답 형식:**
```json
{
  "total_processed": 1000,
  "anomalies_detected": 50,
  "quality_issues": 10,
  "anomaly_rate": 0.05,
  "avg_processing_time_ms": 45.2,
  "quality_issue_rate": 0.01
}
```

---

### 3. 헬스 체크 (`GET /api/esp32/integrated/health`)

서비스 상태 확인

**응답 형식:**
```json
{
  "status": "healthy",
  "service": "ESP32 Integrated Detection Service",
  "statistics": {
    "total_processed": 1000,
    "anomalies_detected": 50,
    ...
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

---

## 🔍 데이터 품질 검증

시스템은 다음 항목을 자동으로 검증합니다:

1. **데이터 길이**: 예상 길이의 50%~200% 범위 내
2. **신호 레벨**: 최대 진폭 100~30000 범위
3. **클리핑**: 클리핑 비율 1% 미만
4. **무음 구간**: 무음 비율 90% 미만

품질 검증 실패 시:
- `success: false` 반환
- `data_quality.issues`에 문제점 목록 포함

---

## 📊 모듈화된 이상 감지 시스템

### 처리 흐름

```
ESP32 오디오 데이터
    ↓
[데이터 품질 검증]
    ↓
[데시벨 레벨 계산]
    ↓
[DecibelFilter] → 소리 없음/정상(낮은 소리) → 스킵
    ↓
[FeatureExtractor] → 오디오 특징 추출
    ↓
[SpectralAnomalyScorer] → 이상 점수 계산
    ↓
[FailureTypeClassifier] → 고장 유형 분류
    ↓
결과 반환
```

### 고장 유형

- `normal`: 정상
- `bearing_wear`: 베어링 마모
- `burst_sound`: 파열음
- `refrigerant_leak`: 냉매 누출
- `evaporator_frost`: 증발기 성에
- `unbalance`: 언밸런스
- `friction`: 마찰음
- `general_anomaly`: 일반적인 이상

---

## 🧪 테스트

### 테스트 스크립트 실행

```bash
python scripts/test_esp32_integrated_detection.py
```

**테스트 항목:**
1. 헬스 체크
2. 정상 오디오 감지
3. 이상 오디오 감지
4. 소리 없음 감지
5. 통계 조회

---

## 📈 성능

### 처리 시간
- 평균: 45-50ms
- 최대: 100ms 이하

### 처리량
- 초당 약 20개 요청 처리 가능

---

## 🔧 설정

### 샘플링 레이트
- 기본: 16000Hz
- 지원 범위: 8000Hz ~ 48000Hz

### 분석 윈도우 크기
- 기본: 5초
- 권장: 3-10초

### 이상 점수 임계값
- 기본: 0.7 (70%)
- 조정 가능

---

## 📝 다음 단계

1. **기준선 설정**: 정상 상태 데이터로 기준선 설정
2. **실제 센서 데이터 수집**: 실제 ESP32 센서로 데이터 수집
3. **성능 모니터링**: 처리 시간 및 정확도 모니터링
4. **알림 연동**: 이상 감지 시 알림 설정

---

**작성일**: 2024년  
**버전**: 1.0  
**상태**: 프로덕션 준비 완료

