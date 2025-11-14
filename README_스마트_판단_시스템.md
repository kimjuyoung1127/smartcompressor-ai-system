# 스마트 판단 시스템 - 빠른 시작

## 개요

실시간 판단으로 대부분 자동 판단하고, 신뢰도가 낮은 데이터만 보류하여 대시보드에서 수동 라벨링하는 모듈화된 시스템입니다.

---

## 🎯 핵심 기능

1. **자동 판단**: 신뢰도 높은 데이터는 즉시 판단 (약 90% 이상)
2. **보류 라벨링**: 신뢰도 낮은 데이터는 보류 큐에 추가
3. **대시보드**: 보류 항목을 조회하고 라벨링
4. **재학습**: 라벨링된 데이터를 재학습에 활용

---

## 🚀 빠른 시작

### 1. 스마트 판단 사용

```python
from services.smart_detection_orchestrator import SmartDetectionOrchestrator
import numpy as np

orchestrator = SmartDetectionOrchestrator(
    confidence_threshold=0.7,  # 70% 이하 신뢰도는 보류
    use_mimii_model=True  # 기존 92% 정확도 모델 사용
)

# 오디오 처리
result = orchestrator.process_audio(
    audio_data=audio_array,
    device_id="ESP32_001"
)

if result['decision'] == 'auto':
    print(f"✅ 자동 판단: {'고장' if result['result']['is_failure'] else '정상'}")
else:
    print(f"📋 보류 큐 추가: {result['pending_item_id']}")
```

### 2. API 사용

```bash
# 스마트 판단
curl -X POST http://localhost:5000/api/smart/detect \
  -H "Content-Type: application/json" \
  -d '{
    "audio_data": [0.1, 0.2, ...],
    "device_id": "ESP32_001"
  }'

# 보류 항목 조회
curl http://localhost:5000/api/pending/items

# 라벨링 완료
curl -X POST http://localhost:5000/api/pending/items/pending_000001_1234567890/label \
  -H "Content-Type: application/json" \
  -d '{
    "label": "abnormal_overload",
    "labeled_by": "expert_001"
  }'
```

### 3. 대시보드 접속

```
http://localhost:5000/static/dashboard-components/pending-labeling-widget.html
```

---

## 📊 워크플로우

```
[ESP32 오디오]
    ↓
[실시간 판단]
    ├─ 신뢰도 ≥ 70% → ✅ 자동 판단 완료
    └─ 신뢰도 < 70% → 📋 보류 큐 추가
                          ↓
                    [대시보드]
                          ↓
                    [전문가 라벨링]
                          ↓
                    [라벨링 완료]
```

---

## 📁 생성된 파일

### 서비스
- `services/pending_labeling_service.py` - 보류 라벨링 관리
- `services/smart_detection_orchestrator.py` - 오케스트레이터

### API 라우트
- `routes/smart_detection_routes.py` - 스마트 판단 API
- `routes/pending_labeling_routes.py` - 보류 라벨링 API

### 대시보드
- `static/dashboard-components/pending-labeling-widget.html` - 라벨링 대시보드

### 문서
- `docs/스마트_판단_아키텍처.md` - 상세 아키텍처
- `README_스마트_판단_시스템.md` - 이 파일

---

## ⚙️ 설정

### 신뢰도 임계값 조정

```python
# 더 엄격하게 (더 많은 데이터 보류)
orchestrator = SmartDetectionOrchestrator(confidence_threshold=0.8)

# 더 관대하게 (더 적은 데이터 보류)
orchestrator = SmartDetectionOrchestrator(confidence_threshold=0.6)
```

---

## 📈 예상 성과

- **자동 판단률**: 약 90% 이상 (신뢰도 높은 데이터)
- **보류율**: 약 10% 미만 (신뢰도 낮은 데이터)
- **전문가 작업량**: 보류 항목만 처리 (약 10%만 수동 라벨링)

---

## 🔄 다음 단계

1. ✅ 아키텍처 구현 완료
2. 🔄 대시보드 통합
3. 📊 통계 모니터링 강화
4. 🔄 재학습 파이프라인 연동

