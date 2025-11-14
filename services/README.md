
# 🧩 Services 디렉터리

이 디렉터리는 SignalCraft 애플리케이션의 서비스 계층 구현을 모두 포함하고 있습니다.

## 🧭 개요
Services 디렉터리는 SignalCraft 시스템의 핵심 기능과 비즈니스 로직을 구현한 Python 및 JavaScript 모듈을 포함합니다. 각 서비스는 애플리케이션의 다양한 부분에서 사용할 수 있는 특정 기능과 작업을 캡슐화합니다.

## 📄 파일 목록
- `__init__.py` - 패키지 초기화 파일  
- `__pycache__/` - Python 바이트코드 캐시 디렉터리  
- `ab_testing_service.py` - 기능 비교를 위한 A/B 테스트 구현  
- `adaptive_threshold_system.py` - 이상 탐지를 위한 적응형 임계값 시스템  
- `advanced_analytics_service.py` - 고급 분석 기능  
- `ai_model_training.py` - AI 모델 학습 서비스  
- `ai_service.py` - 일반적인 AI 서비스 기능  
- `analytics_service.py` - 분석 서비스 구현  
- `auth_service.py` - 인증 서비스  
- `automated_reporting_service.py` - 자동 보고 시스템  
- `contextual_failure_labeling.py` - 상황 기반 실패 라벨링 알고리즘  
- `customer_analytics_service.py` - 고객 분석 기능  
- `dashboard_service.py` - 대시보드 서비스 구현  
- `database_service.js` - JavaScript 기반 데이터베이스 서비스  
- `email_template_service.py` - 이메일 템플릿 관리  
- `esp32_optimizer.py` - ESP32 장치 최적화 서비스  
- `field_data_collection.py` - 현장 데이터 수집 서비스  
- `firmware_ota_service.py` - 펌웨어 OTA(Over-The-Air) 업데이트 서비스  
- `kakao_business_service.py` - 카카오 비즈니스 서비스 통합  
- `kakao_notification_service.py` - 카카오 알림 서비스  
- `mobile_payment_service.py` - 모바일 결제 처리  
- `mobile_push_service.py` - 모바일 푸시 알림 서비스  
- `model_management_service.py` - AI 모델 관리 서비스  
- `model_retraining.py` - 모델 재학습 서비스  
- `notification_management_service.py` - 알림 관리 서비스  
- `notification_service.py` - 일반 알림 서비스  
- `offline_sync_service.py` - 오프라인 동기화 서비스  
- `order_management_service.py` - 주문 관리 기능  
- `payment_service.py` - 결제 처리 서비스  
- `predictive_maintenance_service.py` - 예측 유지보수 알고리즘  
- `product_catalog_service.py` - 제품 카탈로그 관리  
- `real_time_monitoring_service.py` - 실시간 모니터링 기능  
- `realtime_monitoring.py` - 실시간 모니터링 서비스  
- `realtime_streaming_service.py` - 실시간 데이터 스트리밍  
- `remote_control_service.py` - 장치 원격 제어 기능  
- `sensor_data_service.py` - 센서 데이터 처리 서비스  
- `sensor_database_service.py` - 센서 데이터베이스 작업 서비스  
- `sensor_monitoring_service.py` - 센서 모니터링 기능  
- `smart_storage_service.py` - 스마트 저장소 관리  
- `sms_notification_service.py` - SMS 알림 서비스  
- `sqlite_database_service.js` - JavaScript 기반 SQLite 데이터베이스 서비스  
- `store_management_service.py` - 매장 관리 기능  
- `timeseries_learning_system.py` - 시계열 학습 알고리즘  
- `user_permission_service.py` - 사용자 권한 관리

## 🔄 서비스 아키텍처 흐름
```
클라이언트 요청 → API 계층 → 서비스 계층 → 데이터 계층 → 응답 생성 → 클라이언트 응답
```

## 🎯 목적
이 디렉터리는 다음을 위한 중심 저장소 역할을 합니다:
- 비즈니스 로직 구현
- API 서비스 메서드
- 외부 서비스 통합
- 데이터 처리 작업
- AI/ML 서비스 구성 요소
- 하드웨어 통신 서비스

## 🔁 핵심 서비스 흐름

### 🧠 AI 서비스 흐름
```
오디오 데이터 → 특징 추출 → 모델 추론 → 이상 탐지 → 결과 처리 → 응답
```

### 🔐 인증 흐름
```
사용자 자격 증명 → 인증 서비스 → 토큰 생성 → 세션 관리 → 접근 제어 → 응답
```

### 📡 IoT 데이터 흐름
```
ESP32 센서 → 데이터 수신 → 검증 → 저장 → 처리 → 분석 → 결과
```

### 📣 알림 흐름
```
이벤트 발생 → 알림 서비스 → 채널 선택 → 메시지 포맷팅 → 전달 → 상태 추적
```

## 📂 서비스 분류
- **AI/ML 서비스**: 모델 학습, 관리, 추론
- **IoT 서비스**: ESP32 통신 및 관리
- **알림 서비스**: 다채널 알림 시스템
- **분석 서비스**: 데이터 분석 및 보고
- **인증 서비스**: 사용자 인증 및 권한 관리
- **결제 서비스**: 결제 처리 기능
- **모니터링 서비스**: 실시간 시스템 모니터링
- **데이터베이스 서비스**: 데이터 저장 및 조회 작업

## 🔌 서비스 통합 지점
```
API 계층 ↔ 서비스 계층 ↔ 데이터 계층 ↔ 외부 서비스
```
