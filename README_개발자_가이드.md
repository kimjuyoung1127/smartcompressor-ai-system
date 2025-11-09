# SmartCompressor AI 시스템 - 개발자 가이드

## 📋 목차

1. [시스템 개요](#시스템-개요)
2. [최근 개발 완료 사항](#최근-개발-완료-사항)
3. [빠른 시작 (Docker)](#빠른-시작-docker)
4. [수동 설치 가이드](#수동-설치-가이드)
5. [핵심 모듈 설명](#핵심-모듈-설명)
6. [API 엔드포인트](#api-엔드포인트)
7. [테스트 가이드](#테스트-가이드)
8. [개발 워크플로우](#개발-워크플로우)

---

## 🎯 시스템 개요

**SmartCompressor AI 시스템**은 산업용 압축기의 오디오 신호를 분석하여 이상 상태를 실시간으로 진단하는 AI 기반 예방 정비 시스템입니다.

### 핵심 기능

- ✅ **실시간 이상 감지**: 모듈화된 이상 감지 시스템 (86.43% 테스트 커버리지)
- ✅ **ESP32 통합**: 실제 센서 데이터 처리 및 검증
- ✅ **데이터 품질 관리**: 자동 품질 검증 및 버전 관리
- ✅ **Active Learning**: 불확실성 기반 샘플링으로 전문가 시간 효율화
- ✅ **24시간 모니터링**: 하이브리드 저장 전략으로 비용 최적화

---

## 🚀 최근 개발 완료 사항

### 1. ESP32 통합 이상 감지 시스템 (완료 ✅)

**파일**: 
- `services/esp32_integrated_detection_service.py`
- `routes/esp32_integrated_routes.py`

**기능**:
- ESP32 오디오 데이터 수신 및 전처리
- 모듈화된 이상 감지 시스템 통합
- 데이터 품질 자동 검증

**API**:
```bash
POST /api/esp32/integrated/detect
GET /api/esp32/integrated/statistics
GET /api/esp32/integrated/health
```

**문서**: `docs/ESP32_통합_이상_감지_시스템_가이드.md`

---

### 2. 데이터 수집 및 검증 시스템 (완료 ✅)

**파일**:
- `services/data_quality_validator.py`
- `services/data_version_manager.py`
- `services/labeling_quality_manager.py`
- `services/comprehensive_data_collection_service.py`

**기능**:
- 종합적인 데이터 품질 검증 (기술적, 신호, 메타데이터)
- 데이터셋 버전 관리 및 추적
- 라벨링 품질 관리 및 전문가 간 일치도 측정

**품질 등급**: EXCELLENT (90-100점), GOOD (70-89점), ACCEPTABLE (50-69점), POOR (30-49점), REJECT (0-29점)

**문서**: `docs/데이터_수집_및_검증_시스템_가이드.md`

---

### 3. Active Learning 시스템 개선 (완료 ✅)

**파일**:
- `services/advanced_active_learning.py`
- `services/enhanced_pending_labeling_service.py`

**기능**:
- 4가지 불확실성 측정 방법 (엔트로피, 최대 확률, 마진, 앙상블 분산)
- 4가지 샘플링 전략 (불확실성, 다양성, 밸런싱, 적응형)
- 전문가 시간 효율 2배 이상 향상 예상

**문서**: `docs/Active_Learning_시스템_개선_가이드.md`

---

### 4. 모듈화된 이상 감지 시스템 (완료 ✅)

**파일**:
- `services/anomaly_detection_modules/decibel_filter.py`
- `services/anomaly_detection_modules/feature_extractor.py`
- `services/anomaly_detection_modules/spectral_anomaly_scorer.py`
- `services/anomaly_detection_modules/failure_type_classifier.py`
- `services/anomaly_detection_modules/baseline_manager.py`
- `services/universal_anomaly_detector_v2.py`

**테스트 커버리지**: 86.43% (목표 70% 초과 달성)

**문서**: 각 모듈 파일 내 상세 설명 포함

---

## 🐳 빠른 시작 (Docker)

### 사전 요구사항

- Docker 20.10 이상
- Docker Compose 2.0 이상

### 1. 저장소 클론

```bash
git clone https://github.com/SEONBEOM-Kim/smartcompressor-ai-system.git
cd smartcompressor-ai-system
```

### 2. 환경 변수 설정

```bash
cp env.example .env
# .env 파일을 편집하여 필요한 환경 변수 설정
```

### 3. Docker 컨테이너 빌드 및 실행

```bash
# 빌드 및 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 서비스 상태 확인
docker-compose ps
```

### 4. 서비스 접속

- **웹 대시보드**: http://localhost:5000
- **API 문서**: http://localhost:5000/api/docs
- **헬스 체크**: http://localhost:5000/api/health

### 5. 컨테이너 중지

```bash
docker-compose down
```

### 6. 컨테이너 재빌드 (코드 변경 후)

```bash
docker-compose up -d --build
```

---

## 💻 수동 설치 가이드

### 사전 요구사항

- Python 3.8 이상
- Node.js 14 이상
- SQLite 3 (또는 PostgreSQL)

### 1. Python 환경 설정

```bash
# 가상 환경 생성
python3 -m venv venv

# 가상 환경 활성화
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 의존성 설치
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Node.js 환경 설정

```bash
# 의존성 설치
npm install
```

### 3. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일 편집
```

### 4. 데이터베이스 초기화

```bash
python -c "from models.database import init_db; init_db()"
```

### 5. 서버 실행

```bash
# Python 서버 (Flask)
python app.py

# Node.js 서버 (Express)
npm start
# 또는
node server.js
```

---

## 🧩 핵심 모듈 설명

### 1. 모듈화된 이상 감지 시스템

**위치**: `services/anomaly_detection_modules/`

**모듈 구성**:
1. **DecibelFilter**: 데시벨 기반 1차 필터링 (35-40dB: 소리 없음, 48dB 이상: 분석 시작)
2. **FeatureExtractor**: 오디오 특징 추출 (RMS, 스펙트럼 중심, ZCR 등)
3. **SpectralAnomalyScorer**: 스펙트럼 이상 점수 계산 (Z-score 기반)
4. **FailureTypeClassifier**: 고장 유형 분류 (베어링 마모, 냉매 누출 등)
5. **BaselineManager**: 정상 상태 기준선 관리

**사용 예제**:
```python
from services.universal_anomaly_detector_v2 import UniversalAnomalyDetectorV2

detector = UniversalAnomalyDetectorV2()

# 기준선 설정 (1-2일 정상 데이터 수집)
baseline = detector.establish_baseline(normal_audio_samples)

# 이상 감지
result = detector.detect_anomaly(audio_data, decibel_level=50.0)
```

---

### 2. ESP32 통합 서비스

**위치**: `services/esp32_integrated_detection_service.py`

**기능**:
- ESP32 오디오 데이터 수신 및 전처리
- 자동 데이터 품질 검증
- 모듈화된 이상 감지 시스템 통합

**사용 예제**:
```python
from services.esp32_integrated_detection_service import esp32_integrated_service

result = esp32_integrated_service.process_esp32_audio(
    audio_data=audio_bytes,
    device_id="ESP32_001",
    sample_rate=16000
)
```

---

### 3. 데이터 품질 검증 시스템

**위치**: `services/data_quality_validator.py`

**검증 항목**:
- 기술적 품질 (40%): 샘플링 레이트, 데이터 길이, 신호 레벨, 클리핑, 무음 구간
- 신호 품질 (40%): SNR, 동적 범위, 신호 존재 여부
- 메타데이터 품질 (20%): 필수 필드, 타임스탬프, 디바이스 ID

**사용 예제**:
```python
from services.data_quality_validator import data_quality_validator

quality_result = data_quality_validator.validate_audio_data(
    audio_data=audio_array,
    sample_rate=16000,
    metadata={"device_id": "ESP32_001", "timestamp": "2024-01-01T12:00:00"}
)

print(f"품질 점수: {quality_result['overall_score']:.1f}점")
print(f"품질 등급: {quality_result['quality_level']}")
```

---

### 4. Active Learning 시스템

**위치**: `services/advanced_active_learning.py`

**불확실성 측정 방법**:
- **ENTROPY** (추천): 엔트로피 기반, 가장 정확
- **MAX_PROBABILITY**: 최대 확률 기반, 빠름
- **MARGIN**: 마진 기반, 경계 케이스 감지
- **ENSEMBLE_VARIANCE**: 앙상블 분산 기반, 높은 신뢰도

**샘플링 전략**:
- **ADAPTIVE** (추천): 상황에 따라 자동 조정
- **UNCERTAINTY**: 불확실성 기반
- **DIVERSITY**: 다양성 기반
- **BALANCED**: 밸런싱

**사용 예제**:
```python
from services.advanced_active_learning import advanced_active_learning
from services.advanced_active_learning import UncertaintyMethod, SamplingStrategy

# 불확실성 계산
uncertainty = advanced_active_learning.calculate_uncertainty(
    prediction_proba=np.array([0.3, 0.4, 0.3]),
    method=UncertaintyMethod.ENTROPY
)

# 샘플 선택
selected = advanced_active_learning.select_samples_for_labeling(
    samples=sample_list,
    n_samples=10,
    strategy=SamplingStrategy.ADAPTIVE
)
```

---

## 📡 API 엔드포인트

### ESP32 통합 이상 감지

```bash
# 이상 감지
POST /api/esp32/integrated/detect
Headers:
  - X-Device-ID: 디바이스 ID (필수)
  - X-Sample-Rate: 샘플링 레이트 (선택)
  - X-Decibel-Level: 데시벨 레벨 (선택)
Body: 오디오 바이트 데이터 (raw binary)

# 통계 조회
GET /api/esp32/integrated/statistics

# 헬스 체크
GET /api/esp32/integrated/health
```

### 데이터 수집 및 검증

```python
from services.comprehensive_data_collection_service import comprehensive_data_collection_service

# 데이터 수집 및 검증
result = comprehensive_data_collection_service.collect_and_validate(
    audio_data=audio_array,
    sample_rate=16000,
    device_id="ESP32_001",
    save_path="data/audio/sample.wav"
)

# 라벨링 추가
comprehensive_data_collection_service.add_labeling(
    sample_id=result['sample_id'],
    annotator_id="expert_001",
    label="normal",
    confidence=0.95
)
```

---

## 🧪 테스트 가이드

### 전체 테스트 실행

```bash
# 가상 환경 활성화
source venv/bin/activate

# 전체 테스트 실행
pytest tests/ -v

# 커버리지 포함
pytest tests/ --cov=services/anomaly_detection_modules --cov-report=html

# HTML 리포트 확인
# htmlcov/index.html 파일을 브라우저에서 열기
```

### 특정 모듈 테스트

```bash
# 이상 감지 모듈 테스트
pytest tests/test_anomaly_detection_modules/ -v

# ESP32 통합 테스트
pytest tests/test_integration/ -v
```

### 테스트 결과

- **통과**: 94개 테스트 ✅
- **커버리지**: 86.43% (목표 70% 초과 달성)
- **문서**: `docs/테스트_결과_요약.md`

---

## 🔄 개발 워크플로우

### 1. 기능 개발

```bash
# 새 기능 브랜치 생성
git checkout -b feature/new-feature

# 개발 및 테스트
# ... 코드 작성 ...
pytest tests/ -v

# 커밋 및 푸시
git add .
git commit -m "feat: 새 기능 추가"
git push origin feature/new-feature
```

### 2. 코드 리뷰

- GitHub에서 Pull Request 생성
- 코드 리뷰 요청
- 리뷰 후 머지

### 3. 배포

```bash
# Docker 이미지 빌드
docker-compose build

# 프로덕션 배포
docker-compose -f docker-compose.prod.yml up -d
```

---

## 📚 추가 문서

### 개발 워크플로우
- `docs/빠른_시작_가이드.md`: 5분 안에 시작하기
- `docs/개발_워크플로우_가이드.md`: 개인/팀 개발 워크플로우
- `docs/서비스_이식_체크리스트.md`: 기존 서비스에 이식하기

### 핵심 가이드
- `docs/ESP32_통합_이상_감지_시스템_가이드.md`: ESP32 통합 가이드
- `docs/데이터_수집_및_검증_시스템_가이드.md`: 데이터 품질 관리 가이드
- `docs/Active_Learning_시스템_개선_가이드.md`: Active Learning 가이드
- `docs/실시간_대시보드_성능_지표_가이드.md`: 대시보드 성능 지표 가이드

### 완료 요약
- `docs/다음_단계_완료_요약.md`: 최근 개발 완료 사항
- `docs/테스트_결과_요약.md`: 테스트 결과 요약

---

## 🛠️ 문제 해결

### 일반적인 문제

**문제**: Docker 컨테이너가 시작되지 않음
```bash
# 로그 확인
docker-compose logs

# 컨테이너 재빌드
docker-compose up -d --build
```

**문제**: Python 패키지 설치 오류
```bash
# pip 업그레이드
pip install --upgrade pip

# 가상 환경 재생성
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**문제**: 테스트 실패
```bash
# 테스트 환경 확인
pytest tests/ -v --tb=short

# 특정 테스트만 실행
pytest tests/test_anomaly_detection_modules/test_decibel_filter.py -v
```

---

## 🤝 기여하기

1. Fork 저장소
2. 기능 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'feat: Add amazing feature'`)
4. 브랜치에 푸시 (`git push origin feature/amazing-feature`)
5. Pull Request 생성

---

## 📞 지원

- **이슈 리포트**: GitHub Issues
- **문서**: `docs/` 디렉토리
- **코드 리뷰**: Pull Request

---

**작성일**: 2024년  
**버전**: 2.0  
**상태**: 프로덕션 준비 완료

