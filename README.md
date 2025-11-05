# ⚙️ SignalCraft - 산업용 압축기 오디오 분석 시스템 (v2 - 인증 개편 완료)

[![License](https://img.shields.io/badge/license-MIT-blue)](https://github.com/SEONBEOM-Kim/smartcompressor-ai-system/blob/main/LICENSE)
[![Project Status](https://img.shields.io/badge/status-active-brightgreen)](https://github.com/SEONBEOM-Kim/smartcompressor-ai-system)

## 개요

**SignalCraft**는 산업용 압축기의 **오디오 신호**를 분석해 **이상 징후, 고장, 유지보수 필요성**을 탐지하는 **AI 기반 시스템**입니다. 이 시스템은 엣지 컴퓨팅과 IoT 센서(ESP32), 머신러닝 모델, 그리고 실시간 모니터링과 분석을 위한 종합 대시보드를 결합합니다.

**최신 업데이트 (Phase 1):**
- **인증 시스템 개편 완료**: Node.js 기반의 단일 인증 시스템으로 통합하고, 역할 기반 접근 제어(RBAC)를 도입했습니다.
- **데이터베이스 마이그레이션**: 기존 SQLite에서 PostgreSQL로 전환하여 확장성과 성능을 개선했습니다.

## 🚀 기능

- **실시간 오디오 모니터링**: 압축기 오디오 신호를 지속적으로 분석
- **고급 이상 탐지**: 머신러닝 기반의 비정상 패턴 식별
- **ESP32 연동**: 전용 센서 하드웨어를 통한 엣지 컴퓨팅
- **종합 대시보드**: 운영자를 위한 시각적 모니터링 인터페이스
- **전문가 지식 통합**: 엔지니어의 도메인 지식을 AI에 반영
- **멀티 채널 지원**: 여러 압축기를 동시에 모니터링
- **확장 가능한 아키텍처**: 여러 사이트와 설비로 확장 가능

## 🏗️ 프로젝트 구조 (최신)

```
signalcraft/
├── .git/                       # Git 버전 제어 메타데이터
├── .github/                    # GitHub 설정 및 워크플로
│   └── workflows/              # CI/CD 파이프라인
├── admin/                      # 관리자 인터페이스와 관리
├── ai/                         # AI 및 머신러닝 구성요소
├── assets/                     # 프론트엔드 정적 자산
├── backend_files/              # 컴파일된 백엔드 자산
├── config/                     # 설정 파일
├── data/                       # 데이터 파일과 데이터셋
├── database/                   # 데이터베이스 관련 파일 (스키마, 마이그레이션 등)
├── docs/                       # 문서
├── examples/                   # 예제 파일과 사용 방법
├── hardware/                   # 하드웨어 관련 파일
├── ino/                        # Arduino/ESP32 펌웨어
├── mnt/                        # (신규) 외부 시스템 마운트 포인트 (용도 확인 필요)
├── models/                     # 데이터 및 ML 모델
├── node_modules/               # Node.js 의존성
├── routes/                     # API 라우트 정의
├── scripts/                    # 유틸리티/배포 스크립트
├── security/                   # 보안 관련 구성요소
├── server/                     # 서버 사이드 애플리케이션 (Node.js)
├── services/                   # 비즈니스 로직 서비스
├── src/                        # 소스 코드 파일
├── static/                     # 정적 웹 자산
├── system/                     # 시스템 및 서비스 구성 파일
├── templates/                  # 서버 사이드 HTML 템플릿
├── tests/                      # 테스트 파일
├── uploads/                    # 파일 업로드 저장소
├── web/                        # 웹 관련 파일(HTML 등)
├── .dockerignore               # Docker 빌드 시 제외할 파일 목록
├── .env                        # 환경 변수 설정 파일
├── .gitignore                  # Git이 추적하지 않을 파일 목록
├── admin_user_manager.js       # (신규) 관리자용 사용자 관리 스크립트
├── api_keys_template.env       # (신규) API 키 템플릿
├── app.js                      # 메인 Node.js 애플리케이션 진입점
├── app.py                      # 메인 Python/Flask 애플리케이션 진입점 (현재 인증 기능 비활성화)
├── Development_Summary.md      # (신규) 개발 요약 문서
├── ecosystem.config.js         # PM2 프로세스 구성
├── gunicorn.conf.py            # (신규) Gunicorn 서버 설정 파일
├── labeling,auth.md            # (신규) 라벨링 및 인증 시스템 개발 현황 문서
├── log.md                      # (신규) 로그 기록 문서
├── nginx_signalcraft_config.conf # (신규) Nginx 리버스 프록시 설정
├── package.json                # Node.js 프로젝트 메타데이터 및 의존성
├── package-lock.json           # Node.js 락 파일
├── production-server.js        # 프로덕션 서버 구현
├── README.md                   # 이 파일
├── realschema.md               # (신규) 실제 데이터베이스 스키마 문서
├── requirements.txt            # Python 의존성
├── run_server.bat              # Windows 서버 시작 스크립트
├── server.js                   # 메인 서버 구현
├── simple_server.py            # (신규) 간단한 테스트용 Python 서버
└── smartcompressor.db          # (구버전) SQLite 데이터베이스 파일 (현재 사용되지 않음)
```

## 🧱 핵심 아키텍처

### 백엔드 구성요소
- **`app.js`** - 메인 Node.js 애플리케이션 진입점 (인증 및 핵심 로직 담당)
- **`server.js`** - 주요 서버 구현
- **`routes/`** - `authRoutes.js`, `labelingRoutes.js` 등 API 엔드포인트 정의
- **`server/middleware/rbac.js`** - 역할 기반 접근 제어(RBAC) 미들웨어
- **`app.py`** - Python/Flask 애플리케이션 (AI 모델 서빙 등 보조 역할)

### AI/ML 파이프라인
- **`ai/`** - 핵심 모델 학습, 이상 탐지, 실시간 진단 스크립트 포함
- **다음 단계**: `wavesurfer.js`와 `Annotorious`를 활용한 프론트엔드 기반 라벨링 툴 고도화 예정

### IoT 통합
- **`ino/`** - ESP32 펌웨어 (데이터 수집 및 전송)
- **`routes/esp32Routes.js`** - ESP32 통신 API

## 🔄 시스템 흐름

```
[물리적 압축기] → [ESP32 센서] → [SignalCraft 서버 (Node.js)] → [AI 분석 (Python)] → [대시보드]
         ↓               ↓                 ↓                      ↓               ↓
    오디오 신호     →   I2S 전송   →   네트워크/DB (PostgreSQL) →  ML 모델  →  결과 시각화
```

## 🛠️ 기술 스택

- **백엔드**: **Node.js(Express)**, Python(Flask)
- **데이터베이스**: **PostgreSQL**
- **AI/ML**: TensorFlow, scikit-learn, librosa
- **프론트엔드**: HTML/CSS/JavaScript, Bootstrap, **(예정) wavesurfer.js**
- **IoT**: ESP32 마이크로컨트롤러
- **배포**: Docker, PM2, Nginx, EC2

## 🚀 시작하기 (로컬 개발 환경)

### 1️⃣ SSH 터널링 실행
EC2의 PostgreSQL 데이터베이스에 연결하기 위해 로컬에서 터널을 설정합니다.
```bash
ssh -i "C:\Users\gmdqn\pem\signalcraft.pem" -N -L 5433:localhost:5432 ubuntu@3.39.124.0
```

### 2️⃣ .env 파일 설정
프로젝트 루트에 `.env` 파일을 생성하고 아래와 같이 데이터베이스 연결 정보를 설정합니다.
```
DB_HOST=localhost
DB_PORT=5433
DB_NAME=smartcompressor_ai
DB_USER=postgres
DB_PASSWORD=signalcraft6898
```

### 3️⃣ 의존성 설치
```bash
# Node.js 의존성
npm install

# Python 의존성
pip install -r requirements.txt
```

### 4️⃣ 서버 실행
데이터베이스 초기화 로직이 포함된 메인 서버를 실행합니다.
```bash
node server.js
```
> ✅ **예상 결과**: "🗄️ 데이터베이스 테이블이 이미 존재합니다" 메시지와 함께 서버가 정상적으로 실행됩니다.

## 🤝 기여하기

SignalCraft 프로젝트에 대한 기여를 환영합니다! 자세한 내용은 [docs/contributing.md](docs/contributing.md)를 참조하세요.

## 📄 라이선스

이 프로젝트는 **MIT License**를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.
