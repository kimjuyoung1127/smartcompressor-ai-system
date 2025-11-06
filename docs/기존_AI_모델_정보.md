# 기존 AI 모델 정보

## 발견된 모델 파일

### 위치
`data/models/`

### 파일 목록

1. **`mimii_model.pkl`** (94,433 bytes)
   - RandomForest 모델
   - 생성일: 2025-09-12
   
2. **`mimii_scaler.pkl`** (2,791 bytes)
   - 특징 스케일러 (정규화용)
   - 생성일: 2025-09-12

3. **`model_metadata.json`**
   - 모델 메타데이터
   - 성능 정보 포함

4. **`model_rules.json`**
   - 모델 규칙 정의
   - 7개 클래스 정의

---

## 모델 성능 (metadata.json 기준)

### MIMII RandomForest 모델
- **정확도 (Accuracy)**: 92%
- **정밀도 (Precision)**: 89%
- **재현율 (Recall)**: 91%

**매우 우수한 성능!**

---

## 분류 클래스 (7개)

### 정상 클래스 (3개)
1. **normal_compressor** (class_id: 0)
   - 정상 압축기
   
2. **normal_fan** (class_id: 1)
   - 정상 팬
   
3. **normal_motor** (class_id: 2)
   - 정상 모터

### 이상 클래스 (4개)
4. **abnormal_bearing** (class_id: 3)
   - 베어링 이상
   
5. **abnormal_unbalance** (class_id: 4)
   - 불균형 이상
   
6. **abnormal_friction** (class_id: 5)
   - 마찰 이상
   
7. **abnormal_overload** (class_id: 6)
   - 과부하 이상

---

## 모델 사용 방법

### 현재 코드에서 사용하는 곳

1. **`services/ai_service.py`**
   - `_analyze_with_mimii()` 메서드
   - 특징 추출 → 스케일링 → 예측

2. **`ai/intelligent_labeling_system.py`**
   - 모델 로드 경로: `data/models/mimii_model.pkl`

### 사용 예시

```python
import joblib
import numpy as np

# 모델 로드
model = joblib.load('data/models/mimii_model.pkl')
scaler = joblib.load('data/models/mimii_scaler.pkl')

# 특징 추출 (10개 특징)
features = np.array([...])  # 실제 특징 벡터

# 스케일링
features_scaled = scaler.transform(features.reshape(1, -1))

# 예측
prediction = model.predict(features_scaled)[0]
probability = model.predict_proba(features_scaled)[0].max()

# 클래스 이름
class_names = [
    'normal_compressor',
    'normal_fan',
    'normal_motor',
    'abnormal_bearing',
    'abnormal_unbalance',
    'abnormal_friction',
    'abnormal_overload'
]

predicted_class = class_names[prediction]
print(f"예측: {predicted_class} (신뢰도: {probability:.2%})")
```

---

## 특징 정보

모델은 **10개 특징**을 사용합니다 (model_rules.json 기준):
- feature_index: 0-9
- 각 특징은 min_value, max_value 범위로 정의됨

---

## 실시간 판단 시스템에 통합

이 기존 모델을 실시간 판단 시스템에 통합하면:
- **92% 정확도**의 고성능 모델 활용 가능
- 특징 추출 후 바로 예측 가능
- 고장/비고장 판단 + 이상 유형 분류까지 가능

### 통합 방안

1. **기존 모델 우선 사용**
   - 특징 추출 성공 시 → MIMII 모델 사용 (92% 정확도)
   - 특징 추출 실패 시 → 오픈소스 모델 + 특징 기반 알고리즘 사용 (80-90% 정확도)

2. **앙상블**
   - MIMII 모델: 70% 가중치
   - 실시간 판단 시스템: 30% 가중치

---

## 다음 단계

1. ✅ 기존 모델 확인 완료
2. 🔄 실시간 판단 시스템에 통합
3. 📊 성능 비교 및 최적화

