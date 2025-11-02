# ⚙️ SignalCraft - 산업용 압축기 오디오 분석 시스템

[![License](https://img.shields.io/badge/license-MIT-blue)](https://github.com/SEONBEOM-Kim/smartcompressor-ai-system/blob/main/LICENSE)
[![Project Status](https://img.shields.io/badge/status-active-brightgreen)](https://github.com/SEONBEOM-Kim/smartcompressor-ai-system)

## 개요

**SignalCraft**는 산업용 압축기의 **오디오 신호**를 분석해 **이상 징후, 고장, 유지보수 필요성**을 탐지하는 **AI 기반 시스템**입니다. 이 시스템은 엣지 컴퓨팅과 IoT 센서(ESP32), 머신러닝 모델, 그리고 실시간 모니터링과 분석을 위한 종합 대시보드를 결합합니다.

## 🚀 기능

- **실시간 오디오 모니터링**: 압축기 오디오 신호를 지속적으로 분석
- **고급 이상 탐지**: 머신러닝 기반의 비정상 패턴 식별
- **ESP32 연동**: 전용 센서 하드웨어를 통한 엣지 컴퓨팅
- **종합 대시보드**: 운영자를 위한 시각적 모니터링 인터페이스
- **전문가 지식 통합**: 엔지니어의 도메인 지식을 AI에 반영
- **멀티 채널 지원**: 여러 압축기를 동시에 모니터링
- **확장 가능한 아키텍처**: 여러 사이트와 설비로 확장 가능

## 🏗️ 프로젝트 구조

```
signalcraft/
├── .git/                       # Git 버전 제어 메타데이터
├── .github/                    # GitHub 설정 및 워크플로
│   └── workflows/              # CI/CD 파이프라인 (auto-deploy.yml, deploy.yml 등)
├── admin/                      # 관리자 인터페이스와 관리
├── ai/                         # AI 및 머신러닝 구성요소
├── assets/                     # 프론트엔드 정적 자산
├── backend_files/              # 컴파일된 백엔드 자산
├── config/                     # 설정 파일
├── data/                       # 데이터 파일과 데이터셋
├── database/                   # 데이터베이스 파일
├── docs/                       # 문서
├── examples/                   # 예제 파일과 사용 방법
├── hardware/                   # 하드웨어 관련 파일
├── ino/                        # Arduino/ESP32 펌웨어
├── models/                     # 데이터 및 ML 모델
├── node_modules/               # Node.js 의존성
├── routes/                     # API 라우트 정의
├── scripts/                    # 유틸리티/배포 스크립트
├── security/                   # 보안 관련 구성요소
├── server/                     # 서버 사이드 애플리케이션
├── services/                   # 비즈니스 로직 서비스
├── src/                        # 소스 코드 파일
├── static/                     # 정적 웹 자산
├── system/                     # 시스템 및 서비스 구성 파일
├── templates/                  # 서버 사이드 HTML 템플릿
├── tests/                      # 테스트 파일
├── uploads/                    # 파일 업로드 저장소
├── web/                        # 웹 관련 파일(HTML 등)
├── app.js                      # 메인 Node.js 애플리케이션 진입점
├── app.py                      # 메인 Python/Flask 애플리케이션 진입점
├── ecosystem.config.js         # PM2 프로세스 구성
├── package.json                # Node.js 프로젝트 메타데이터 및 의존성
├── package-lock.json           # Node.js 락 파일
├── README.md                   # 이 파일
├── requirements.txt            # Python 의존성
├── run_server.bat              # Windows 서버 시작 스크립트
├── server.js                   # 메인 서버 구현(실행을 위해 루트에 유지)
├── production-server.js        # 프로덕션 서버 구현(실행을 위해 루트에 유지)
└── smartcompressor.db          # SQLite 데이터베이스 파일
```

## 🧱 핵심 아키텍처

### 백엔드 구성요소
- **`app.js`** - 메인 Node.js 애플리케이션 진입점
- **`app.py`** - 메인 Python/Flask 애플리케이션 진입점
- **`server.js`** - 주요 서버 구현
- **`production-server.js`** - 프로덕션 서버 구성

### AI/ML 파이프라인
- **`ai/ai_model_trainer.py`** - 핵심 모델 학습
- **`ai/anomaly_detection_ai.py`** - 이상 탐지 알고리즘
- **`ai/train_ai.py`** - AI 학습 스크립트
- **`ai/run_diagnosis.py`** - 실시간 진단 스크립트

### IoT 통합
- **`ino/board_diagnosis.ino`** - 보드 하드웨어 진단
- **`routes/esp32Routes.js`** - ESP32 통신 API

### 프론트엔드 구성요소
- **`web/`** - 웹 인터페이스 HTML 파일
- **`static/`** - 정적 웹 자산(CSS, JS, 이미지)
- **`templates/`** - 서버 사이드 HTML 템플릿

## 🔄 시스템 흐름

```
[물리적 압축기] → [ESP32 센서] → [SignalCraft 서버] → [AI 분석] → [대시보드]
         ↓               ↓                 ↓               ↓            ↓
    오디오 신호     →   I2S 전송   →   네트워크 → 저장소   →  ML 모델  →  결과
```

### 데이터 처리 단계:
1. **데이터 수집**: ESP32 센서가 산업용 압축기의 오디오 데이터를 수집
2. **데이터 전송**: 오디오 데이터가 HTTP API를 통해 SignalCraft 서버로 전송
3. **데이터 저장**: 원본/가공 데이터를 데이터베이스/파일시스템에 저장
4. **AI 처리**: 이상 탐지 모델이 오디오 패턴을 분석
5. **결과 생성**: 분류 결과와 신뢰도(Confidence) 점수 산출
6. **대시보드 표시**: 시스템 상태와 이상 징후를 시각화
7. **알림**: 감지 결과에 따라 알림 전송

## 🛠️ 기술 스택

- **백엔드**: Python(Flask), Node.js(Express)
- **데이터베이스**: SQLite(기본), 향후 PostgreSQL로 마이그레이션 예정
- **AI/ML**: TensorFlow, scikit-learn, librosa(오디오 처리)
- **프론트엔드**: HTML/CSS/JavaScript, Bootstrap
- **IoT**: ESP32 마이크로컨트롤러(I2S 오디오 인터페이스)
- **배포**: Docker, PM2, Nginx, EC2

## 📋 핵심 파일 요약

| 디렉토리 | 주요 파일 | 목적 |
|-----------|-----------|---------|
| `ai/` | `ai_model_trainer.py`, `anomaly_detection_ai.py` | AI 모델 학습 및 추론 |
| `services/` | `dashboard_service.py`, `ai_service.py` | 비즈니스 로직 구현 |
| `routes/` | `dashboard_routes.py`, `ai_routes.py` | API 엔드포인트 정의 |
| `ino/` | `board_diagnosis.ino`, `ice_cream_sensor_final.ino` | ESP32 센서 펌웨어 |
| `src/` | 서버 및 애플리케이션 소스 파일 | 핵심 애플리케이션 로직 |
| `data/` | 다양한 하위 디렉토리 | 데이터 저장 및 처리 |
| `system/` | 서비스 구성 파일 | 시스템 및 배포 구성 |
| `web/` | HTML 파일 | 웹 인터페이스 파일 |

## 🚀 시작하기

### 사전 준비물
- Python 3.8 이상
- Node.js 14 이상
- ESP32 개발 보드
- 필요한 Python 패키지(`requirements.txt` 참고)
- 필요한 Node.js 패키지(`package.json` 참고)

### 설치
1. 저장소 클론
2. Python 의존성 설치: `pip install -r requirements.txt`
3. Node.js 의존성 설치: `npm install`
4. 환경 변수 설정: `.env` 템플릿 참고
5. 데이터베이스 초기화: `python -c "from models.database import init_db; init_db()"`
6. 애플리케이션 실행: `npm start` 또는 `node server.js`

### 서버 실행
- 개발용: `node server.js`
- PM2 사용: `pm2 start ecosystem.config.js`
- Windows용: `run_server.bat`

## 🛠️ 프로젝트 구성

프로젝트는 다음과 같은 원칙으로 구성되었습니다:
- 핵심 실행 파일과 주요 진입점은 루트 디렉토리에 유지
- 구성 파일은 `config/` 디렉토리에 위치
- 서비스 관련 파일은 `services/` 디렉토리에 위치
- API 라우트 정의는 `routes/` 디렉토리에 위치
- 웹 파일은 `web/` 디렉토리에 위치
- 시스템/서비스 구성 파일은 `system/` 디렉토리에 위치
- 테스트 파일은 `tests/` 디렉토리에 위치
- 모든 소스 코드 파일은 `src/` 디렉토리에 위치
- AI 관련 파일은 `ai/` 디렉토리에 위치
- 프론트엔드 자산은 `static/` 및 `assets/` 디렉토리에 위치

## 🤝 기여하기

SignalCraft 프로젝트에 대한 기여를 환영합니다! 자세한 내용은 [CONTRIBUTING.md](docs/contributing.md)를 참조하세요.

## 📄 라이선스

이 프로젝트는 **MIT License**를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 지원

지원이 필요하시면 GitHub 저장소에 이슈를 생성하시거나 메인테이너에게 연락해 주세요.

---

**SignalCraft** — AI 기반 오디오 분석으로 산업 유지보수를 강화합니다. 🔊🏭