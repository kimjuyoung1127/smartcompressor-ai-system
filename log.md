24시간 자동 모니터링 AI 모듈 핵심 정리
📋 개요
24시간 무인 냉동고 모니터링 시스템은 실시간 소음 센서 데이터를 지속적으로 분석하여 이상 징후를 자동으로 감지하는 AI 기반 시스템입니다.

개발자: 주영님
목적: 24시간 무인 모니터링을 통한 사전 고장 예방
상태: 개발 완료 (현재 중단 요청)

🏗️ 시스템 아키텍처
┌─────────────────────────────────────────────────────────────┐
│                   24시간 모니터링 시스템                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │  센서 데이터 수집  │  ────>  │  오디오 전처리    │         │
│  │  (5초 간격)       │         │  (librosa)       │         │
│  └──────────────────┘         └──────────────────┘         │
│           │                              │                   │
│           │                              ▼                   │
│           │                    ┌──────────────────┐          │
│           │                    │  특징 추출        │          │
│           │                    │  (135개 특징)     │          │
│           │                    └──────────────────┘          │
│           │                              │                   │
│           │                              ▼                   │
│           │         ┌──────────────────────────────────┐    │
│           │         │     통합 AI 진단 시스템            │    │
│           │         │  ┌────────────────────────────┐  │    │
│           │         │  │ 1. 이상 탐지 AI             │  │    │
│           │         │  │    (Isolation Forest)       │  │    │
│           │         │  └────────────────────────────┘  │    │
│           │         │  ┌────────────────────────────┐  │    │
│           │         │  │ 2. 적응형 임계값 시스템     │  │    │
│           │         │  │    (동적 임계값 조정)        │  │    │
│           │         │  └────────────────────────────┘  │    │
│           │         │  ┌────────────────────────────┐  │    │
│           │         │  │ 3. 온라인 학습 시스템        │  │    │
│           │         │  │    (실시간 모델 업데이트)    │  │    │
│           │         │  └────────────────────────────┘  │    │
│           │         │         │ 가중 투표              │    │
│           │         │         ▼                        │    │
│           │         │  ┌────────────────────────────┐  │    │
│           │         │  │ 최종 이상 판정              │  │    │
│           │         │  │ (신뢰도 기반 통합)          │  │    │
│           │         │  └────────────────────────────┘  │    │
│           │         └──────────────────────────────────┘    │
│           │                              │                   │
│           │                              ▼                   │
│           │                    ┌──────────────────┐          │
│           │                    │  결과 저장        │          │
│           │                    │  (SQLite DB)     │          │
│           │                    └──────────────────┘          │
│           │                              │                   │
│           │                              ▼                   │
│           │                    ┌──────────────────┐          │
│           │                    │  알림 처리        │          │
│           │                    │  (CRITICAL/WARNING)│         │
│           │                    └──────────────────┘          │
│           │                                                   │
└───────────┴───────────────────────────────────────────────────┘
🔧 핵심 컴포넌트
1. RealtimeMonitoringService (메인 서비스)
파일: services/realtime_monitoring.py

역할: 24시간 모니터링의 핵심 서비스

주요 기능:

✅ 백그라운드 스레드로 지속적 모니터링
✅ 센서 데이터 수집 및 처리 (기본 60초 간격)
✅ AI 분석 결과를 SQLite 데이터베이스에 저장
✅ 이상 감지 시 알림 처리 (CRITICAL/WARNING/INFO)
✅ 모니터링 통계 및 알림 조회 API 제공
핵심 메서드:

# 모니터링 시작
def start_monitoring(self):
    """백그라운드 스레드로 24시간 모니터링 시작"""
    self.is_running = True
    self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
    self.monitoring_thread.daemon = True
    self.monitoring_thread.start()

# 모니터링 루프
def _monitoring_loop(self):
    """지속적으로 센서 데이터를 수집하고 분석"""
    while self.is_running:
        self._process_sensor_data()  # 센서 데이터 처리
        time.sleep(self.check_interval)  # 기본 60초 대기
설정:

check_interval: 모니터링 간격 (기본 60초)
alert_threshold: 이상 감지 임계값 (기본 0.7)
warning_threshold: 주의 감지 임계값 (기본 0.5)
2. IntegratedAISystem (통합 AI 시스템)
파일: ai/integrated_ai_system.py

역할: 3개의 AI 모듈을 통합하여 최종 이상 판정

주요 기능:

✅ 3개 AI 모듈의 예측 결과를 가중 투표로 통합
✅ 신뢰도 기반 최종 판정
✅ 실시간 모니터링 지원
✅ 성능 지표 추적
통합 방식:

# 가중 투표 방식
weights = {
    'anomaly_detector': 0.4,  # 가장 신뢰할 만한 모델
    'threshold_system': 0.3,
    'online_learner': 0.3
}

# 가중 평균 신뢰도 계산
weighted_confidence = (
    weights['anomaly_detector'] * anomaly_result['confidence'] +
    weights['threshold_system'] * threshold_score +
    weights['online_learner'] * online_result['confidence']
)

# 최종 이상 여부 판정
final_anomaly = majority_vote and weighted_confidence >= confidence_threshold
하위 시스템:

RefrigeratorAnomalyDetector (이상 탐지 AI)
AdaptiveThresholdSystem (적응형 임계값 시스템)
OnlineLearningSystem (온라인 학습 시스템)
3. RefrigeratorAnomalyDetector (이상 탐지 AI)
파일: ai/anomaly_detection_ai.py

역할: 정상 데이터 패턴을 학습하여 이상을 탐지

주요 기능:

✅ 정상 데이터로 Isolation Forest 모델 학습
✅ 135개 오디오 특징 추출
✅ 적응형 임계값 기반 이상 탐지
✅ 모니터링 히스토리 관리 (최근 24시간)
특징 추출:

# 추출되는 특징 (총 135개)
- 에너지 기반: RMS Energy, Energy Entropy
- 주파수 도메인: Spectral Centroid, Rolloff, Bandwidth
- Zero Crossing Rate (날카로운 소음 감지)
- MFCC (Mel-Frequency Cepstral Coefficients): 13개
- Chroma Features: 12개
- Spectral Contrast: 7개
- Tonnetz: 6개
- Tempo: 1개
학습 방법:

# 정상 데이터로만 학습 (Unsupervised Learning)
def train_on_normal_data(self, normal_audio_files: List[str]):
    """정상 오디오 파일로 이상 탐지 모델 학습"""
    # 1. 정상 데이터 특징 추출
    # 2. Isolation Forest 모델 학습
    # 3. 정상 데이터 통계 계산
    # 4. 적응형 임계값 설정
4. AdaptiveThresholdSystem (적응형 임계값 시스템)
파일: ai/adaptive_threshold_system.py

역할: 24시간 모니터링 데이터를 기반으로 임계값을 동적으로 조정

주요 기능:

✅ 정상 데이터 통계를 기반으로 임계값 자동 조정
✅ 6시간마다 임계값 업데이트
✅ 최근 7일 데이터를 히스토리로 관리
✅ 민감도 조절 가능 (0.0-1.0)
작동 원리:

# 1. 정상 데이터만 수집 (이상 데이터 제외)
# 2. 각 특징별 통계 계산 (평균, 표준편차, 백분위수)
# 3. 통계 기반 임계값 설정
#    - Lower bound: mean - (sensitivity * std)
#    - Upper bound: mean + (sensitivity * std)
# 4. 6시간마다 자동 업데이트
설정:

update_interval_hours: 임계값 업데이트 간격 (기본 6시간)
history_days: 통계 계산용 히스토리 기간 (기본 7일)
sensitivity: 민감도 (기본 0.1, 낮을수록 민감)
5. OnlineLearningSystem (온라인 학습 시스템)
파일: ai/online_learning_system.py

역할: 24시간 모니터링 데이터를 실시간으로 학습하여 모델 성능 지속 개선

주요 기능:

✅ 새로운 데이터를 실시간으로 학습
✅ 100개 샘플마다 모델 자동 업데이트
✅ 메모리 효율적 학습 (최대 10,000개 샘플 유지)
✅ 정상/이상 데이터 통계 추적
학습 방식:

# 1. 새로운 샘플 추가
def add_sample(self, features, is_anomaly, confidence):
    # 버퍼에 추가
    self.feature_buffer.append(feature_vector)
    self.label_buffer.append(is_anomaly)
    
    # 100개마다 모델 업데이트
    if self.total_samples % 100 == 0:
        self._update_model()
설정:

learning_rate: 학습률 (기본 0.01)
memory_size: 메모리에 유지할 샘플 수 (기본 10,000)
update_frequency: 모델 업데이트 주기 (기본 100샘플)
📊 데이터 흐름
1. 센서 데이터 수집
센서 → 오디오 데이터 (5초) → 전처리 → 특징 추출 (135개)
2. AI 분석
특징 벡터 → [이상 탐지 AI] → 예측 1 (가중치 0.4)
           → [적응형 임계값] → 예측 2 (가중치 0.3)
           → [온라인 학습]   → 예측 3 (가중치 0.3)
           → 가중 투표 → 최종 판정
3. 결과 저장 및 알림
최종 판정 → SQLite DB 저장 → 이상 감지 시 알림 처리
🔌 API 엔드포인트
모니터링 제어
파일: routes/monitoring_routes.py

1. 모니터링 시작
POST /api/monitoring/start
응답:

{
  "success": true,
  "message": "24시간 모니터링 서비스가 시작되었습니다."
}
2. 모니터링 중지
POST /api/monitoring/stop
응답:

{
  "success": true,
  "message": "24시간 모니터링 서비스가 중지되었습니다."
}
3. 모니터링 상태 조회
GET /api/monitoring/status
응답:

{
  "success": true,
  "is_running": true,
  "check_interval": 60,
  "alert_threshold": 0.7,
  "warning_threshold": 0.5
}
4. 모니터링 통계 조회
GET /api/monitoring/stats?hours=24
응답:

{
  "success": true,
  "stats": {
    "total_analyses": 1440,
    "anomaly_count": 12,
    "normal_count": 1428,
    "active_alerts": 3,
    "anomaly_rate": 0.83,
    "time_range_hours": 24
  }
}
5. 최근 알림 조회
GET /api/monitoring/alerts?limit=10
응답:

{
  "success": true,
  "alerts": [
    {
      "type": "CRITICAL",
      "message": "위험: 냉동고 이상 소음 감지 (확률: 85.3%)",
      "severity": "high",
      "timestamp": "2024-01-15 14:30:00",
      "resolved": false
    }
  ]
}
💾 데이터베이스 구조
파일: data/monitoring.db (SQLite)

1. monitoring_logs 테이블
CREATE TABLE monitoring_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    audio_file_path TEXT,
    prediction INTEGER,
    probability REAL,
    confidence TEXT,
    is_anomaly BOOLEAN,
    models_used TEXT,
    features_used INTEGER,
    status TEXT
)
2. alerts 테이블
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    alert_type TEXT,  -- CRITICAL, WARNING, INFO
    message TEXT,
    severity TEXT,     -- high, medium, low
    resolved BOOLEAN DEFAULT FALSE
)
⚙️ 설정 및 구성
환경 변수 (선택사항)
# 모니터링 간격 (초)
MONITORING_CHECK_INTERVAL=60

# 이상 감지 임계값
ALERT_THRESHOLD=0.7
WARNING_THRESHOLD=0.5

# 데이터베이스 경로
MONITORING_DB_PATH=data/monitoring.db
코드에서 설정
# RealtimeMonitoringService 초기화
monitoring_service = RealtimeMonitoringService(
    db_path='monitoring.db',
    check_interval=60  # 60초마다 체크
)

# IntegratedAISystem 초기화
ai_system = IntegratedAISystem(
    model_save_path="data/models/",
    monitoring_window_seconds=5,  # 5초 윈도우
    confidence_threshold=0.7      # 신뢰도 임계값
)
🚀 사용 방법
1. 서버 시작 시 자동 실행
파일: app.py (Line 200)

# 서버 시작 시 자동으로 모니터링 시작
sensor_monitoring_service.start_monitoring()
2. 수동으로 시작/중지
from services.realtime_monitoring import monitoring_service

# 모니터링 시작
monitoring_service.start_monitoring()

# 모니터링 중지
monitoring_service.stop_monitoring()

# 상태 확인
if monitoring_service.is_running:
    print("모니터링 실행 중")
3. API를 통한 제어
# 모니터링 시작
curl -X POST http://localhost:5000/api/monitoring/start

# 모니터링 중지
curl -X POST http://localhost:5000/api/monitoring/stop

# 상태 조회
curl http://localhost:5000/api/monitoring/status

# 통계 조회
curl http://localhost:5000/api/monitoring/stats?hours=24
📈 성능 지표
모니터링 통계
전체 분석 수: 24시간 동안 처리한 오디오 샘플 수
이상 감지 수: 이상으로 판정된 샘플 수
정상 감지 수: 정상으로 판정된 샘플 수
이상률: (이상 감지 수 / 전체 분석 수) × 100
활성 알림 수: 해결되지 않은 알림 수
AI 성능 지표
정확도 (Accuracy): 전체 예측 중 정확한 예측 비율
정밀도 (Precision): 이상으로 예측한 것 중 실제 이상 비율
재현율 (Recall): 실제 이상 중 올바르게 탐지한 비율
F1 Score: 정밀도와 재현율의 조화 평균
평균 처리 시간: 샘플당 평균 분석 시간
🔍 주요 특징
1. 3중 AI 시스템
이상 탐지 AI: 정상 패턴 학습 기반 이상 탐지
적응형 임계값: 동적 임계값 조정으로 환경 변화 대응
온라인 학습: 실시간 학습으로 성능 지속 개선
2. 가중 투표 방식
3개 AI 모델의 예측을 신뢰도 기반으로 통합
다수결 + 신뢰도 임계값으로 최종 판정
3. 자동화
백그라운드 스레드로 24시간 무인 모니터링
자동 임계값 업데이트 (6시간마다)
자동 모델 업데이트 (100샘플마다)
4. 데이터 관리
SQLite 데이터베이스로 모든 결과 저장
알림 히스토리 관리
통계 및 조회 API 제공
⚠️ 주의사항
1. 서버 시작 시 자동 실행
app.py에서 start_monitoring() 호출 시 서버 시작과 함께 모니터링 시작
중단하려면 해당 줄을 주석 처리
2. 리소스 사용
백그라운드 스레드로 지속 실행
메모리: 최대 10,000개 샘플 유지
CPU: 오디오 분석 및 AI 추론
3. 데이터베이스
SQLite 파일이 계속 증가
주기적 백업 및 정리 필요
4. 센서 데이터
현재는 시뮬레이션 데이터 사용
실제 센서 연동 시 _process_sensor_data() 수정 필요
📝 관련 파일 목록
핵심 파일
services/realtime_monitoring.py - 메인 24시간 모니터링 서비스
ai/integrated_ai_system.py - 통합 AI 시스템
routes/monitoring_routes.py - API 엔드포인트
AI 모듈
ai/anomaly_detection_ai.py - 이상 탐지 AI
ai/adaptive_threshold_system.py - 적응형 임계값 시스템
ai/online_learning_system.py - 온라인 학습 시스템
Phase 시스템
ai/phase1_basic_anomaly.py - 1단계 기본 이상 탐지
ai/phase2_adaptive_system.py - 2단계 적응형 시스템
ai/phase3_integrated_system.py - 3단계 통합 시스템
지원 모듈
ai/enhanced_feature_extractor.py - 특징 추출기
ai/preprocessor.py - 전처리 모듈
ai/basic_anomaly_detector.py - 기본 이상 탐지기
🔄 향후 개선 사항
실제 센서 연동: 시뮬레이션 데이터 대신 실제 센서 데이터 수신
알림 시스템 강화: 이메일, SMS, 푸시 알림 추가
대시보드 연동: 실시간 모니터링 대시보드 구축
성능 최적화: 처리 시간 단축 및 리소스 사용 최적화
다중 장비 지원: 여러 냉동고 동시 모니터링
📚 참고 문서
docs/24시간_모니터링_관련_파일_목록.md - 관련 파일 상세 목록
docs/24시간_모니터링_중단_가이드.md - 모니터링 중단 방법
작성일: 2024년
버전: 1.0
상태: 개발 완료 (현재 중단 요청)