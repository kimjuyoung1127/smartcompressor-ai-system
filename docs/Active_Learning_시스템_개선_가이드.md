# Active Learning 시스템 개선 가이드

## 📋 개요

고급 Active Learning 시스템으로 불확실성 기반 샘플링을 강화하여 전문가 시간을 효율적으로 활용합니다.

### 주요 개선 사항

1. **다양한 불확실성 측정 방법**
   - 엔트로피 기반 불확실성
   - 최대 확률 기반 불확실성
   - 마진 기반 불확실성
   - 앙상블 분산 기반 불확실성

2. **샘플링 전략**
   - 불확실성 기반 샘플링 (Uncertainty Sampling)
   - 다양성 기반 샘플링 (Diversity Sampling)
   - 밸런싱 샘플링 (Balanced Sampling)
   - 적응형 샘플링 (Adaptive Sampling)

3. **효율성 최적화**
   - 배치 샘플링
   - 우선순위 큐 기반 샘플링
   - 예산 제약 하에서 샘플링

---

## 🔍 불확실성 측정 방법

### 1. 엔트로피 기반 (ENTROPY) ⭐ 추천

**공식**: `H(p) = -Σ p_i * log(p_i)`

**특징**:
- 모든 클래스의 확률을 고려
- 가장 정확한 불확실성 측정
- 계산 비용: 중간

**사용 시나리오**:
- 정확한 불확실성 측정이 필요한 경우
- 모든 클래스의 확률 정보가 있는 경우

### 2. 최대 확률 기반 (MAX_PROBABILITY)

**공식**: `1 - max(p_i)`

**특징**:
- 가장 높은 확률만 고려
- 계산 비용: 낮음
- 빠른 판단

**사용 시나리오**:
- 빠른 불확실성 측정이 필요한 경우
- 계산 리소스가 제한된 경우

### 3. 마진 기반 (MARGIN)

**공식**: `1 - (max(p_i) - second_max(p_i))`

**특징**:
- 상위 2개 확률의 차이 고려
- 경계 케이스 감지에 유용
- 계산 비용: 낮음

**사용 시나리오**:
- 경계 케이스를 찾고 싶은 경우
- 모호한 샘플을 찾고 싶은 경우

### 4. 앙상블 분산 기반 (ENSEMBLE_VARIANCE)

**공식**: 앙상블 모델 간 예측 분산

**특징**:
- 여러 모델의 일치도 측정
- 가장 신뢰할 수 있는 불확실성
- 계산 비용: 높음

**사용 시나리오**:
- 앙상블 모델을 사용하는 경우
- 높은 정확도가 필요한 경우

---

## 🎯 샘플링 전략

### 1. 불확실성 기반 (UNCERTAINTY) ⭐ 기본

**원리**: 불확실성이 높은 샘플만 선택

**장점**:
- 가장 효율적인 샘플 선택
- 빠른 모델 개선

**단점**:
- 다양성 부족 가능
- 특정 영역에 집중될 수 있음

### 2. 다양성 기반 (DIVERSITY)

**원리**: 다양한 샘플을 선택 (클러스터링 기반)

**장점**:
- 데이터 분포 고려
- 편향 방지

**단점**:
- 불확실성 낮은 샘플도 선택 가능
- 계산 비용 높음

### 3. 밸런싱 (BALANCED)

**원리**: 불확실성과 신뢰도를 균형있게 고려

**장점**:
- 균형잡힌 샘플 선택
- 안정적인 성능

**단점**:
- 최적화가 어려울 수 있음

### 4. 적응형 (ADAPTIVE) ⭐ 추천

**원리**: 상황에 따라 자동으로 전략 조정

**장점**:
- 최적의 샘플 선택
- 자동 최적화

**단점**:
- 구현 복잡도 높음

---

## 🚀 사용 방법

### 기본 사용

```python
from services.advanced_active_learning import advanced_active_learning
from services.advanced_active_learning import UncertaintyMethod, SamplingStrategy

# 불확실성 계산
prediction_proba = np.array([0.3, 0.4, 0.3])  # 3개 클래스 확률
uncertainty = advanced_active_learning.calculate_uncertainty(
    prediction_proba=prediction_proba,
    method=UncertaintyMethod.ENTROPY
)

# 쿼리 필요 여부 판단
should_query, uncertainty_score = advanced_active_learning.should_query(
    prediction_proba=prediction_proba,
    confidence=0.6
)

if should_query:
    print(f"라벨링 필요: 불확실성 {uncertainty_score:.2%}")
```

### 샘플 선택

```python
# 샘플 리스트 준비
samples = [
    {
        'sample_id': 'sample_001',
        'prediction_proba': np.array([0.3, 0.4, 0.3]),
        'confidence': 0.6
    },
    {
        'sample_id': 'sample_002',
        'prediction_proba': np.array([0.8, 0.1, 0.1]),
        'confidence': 0.9
    },
    # ... 더 많은 샘플
]

# 라벨링을 위한 샘플 선택
selected_samples = advanced_active_learning.select_samples_for_labeling(
    samples=samples,
    n_samples=10,
    strategy=SamplingStrategy.ADAPTIVE
)

print(f"선택된 샘플: {len(selected_samples)}개")
for sample in selected_samples:
    print(f"  - {sample['sample_id']}: 불확실성 {sample['uncertainty']:.2%}")
```

### 향상된 보류 라벨링 서비스 사용

```python
from services.enhanced_pending_labeling_service import enhanced_pending_labeling_service

# 보류 여부 판단 (자동으로 불확실성 기반 판단)
should_pend = enhanced_pending_labeling_service.should_pend_labeling(
    detection_result={
        'confidence': 0.6,
        'prediction_proba': {'normal': 0.3, 'anomaly': 0.4, 'unknown': 0.3},
        'score': 0.5
    }
)

if should_pend:
    # 보류 항목 추가 (불확실성 자동 계산 및 기록)
    item_id = enhanced_pending_labeling_service.add_pending_item(
        audio_data=audio_array,
        detection_result=detection_result,
        device_id="ESP32_001"
    )
    
    # 불확실성 기준으로 보류 항목 조회
    high_uncertainty_items = enhanced_pending_labeling_service.get_pending_items_by_uncertainty(
        n_items=10,
        min_uncertainty=0.7
    )
```

---

## 📊 통계 및 모니터링

### Active Learning 통계 조회

```python
# 통계 조회
stats = advanced_active_learning.get_statistics()

print(f"총 쿼리 수: {stats['total_queries']}")
print(f"라벨링 완료: {stats['labeled_count']}")
print(f"라벨링 완료율: {stats['labeling_rate']:.1%}")
print(f"평균 불확실성: {stats['avg_uncertainty']:.2%}")
```

### 향상된 보류 라벨링 서비스 통계

```python
# Active Learning 통계 조회
al_stats = enhanced_pending_labeling_service.get_active_learning_statistics()

print(f"불확실성 기반 쿼리: {al_stats['uncertainty_queries']}")
print(f"적응형 쿼리: {al_stats['adaptive_queries']}")
```

---

## 🔧 설정 및 커스터마이징

### 불확실성 방법 변경

```python
from services.advanced_active_learning import AdvancedActiveLearning, UncertaintyMethod

# 커스텀 Active Learning 시스템 생성
custom_al = AdvancedActiveLearning(
    uncertainty_method=UncertaintyMethod.MARGIN,  # 마진 기반으로 변경
    sampling_strategy=SamplingStrategy.BALANCED,  # 밸런싱 전략
    confidence_threshold=0.75  # 임계값 조정
)
```

### 샘플링 전략 변경

```python
# 적응형 전략 사용
enhanced_service = EnhancedPendingLabelingService(
    uncertainty_method=UncertaintyMethod.ENTROPY,
    sampling_strategy=SamplingStrategy.ADAPTIVE,
    confidence_threshold=0.7
)
```

---

## 💡 모범 사례

### 1. 초기 단계
- **불확실성 방법**: ENTROPY (정확한 측정)
- **샘플링 전략**: ADAPTIVE (자동 최적화)
- **목표**: 다양한 불확실한 샘플 수집

### 2. 중기 단계
- **불확실성 방법**: MARGIN (경계 케이스 집중)
- **샘플링 전략**: BALANCED (균형잡힌 선택)
- **목표**: 모델 성능 안정화

### 3. 후기 단계
- **불확실성 방법**: MAX_PROBABILITY (빠른 판단)
- **샘플링 전략**: UNCERTAINTY (효율성)
- **목표**: 최소한의 라벨링으로 최대 성능

---

## 📈 성능 지표

### 효율성 지표
- **라벨링 효율**: 전문가 시간 대비 모델 개선율
- **목표**: 기존 대비 2배 이상 효율 향상

### 정확도 지표
- **모델 정확도**: 라벨링된 샘플로 학습한 모델의 정확도
- **목표**: 동일한 라벨링 수로 더 높은 정확도 달성

---

## 🎯 다음 단계

1. ✅ **Active Learning 시스템 개선** - 완료
2. ⏳ **실시간 모니터링 대시보드 개선** - 다음 우선순위
3. ⏳ **모델 성능 검증 및 개선** - 대기 중

---

**작성일**: 2024년  
**버전**: 1.0  
**상태**: 프로덕션 준비 완료

