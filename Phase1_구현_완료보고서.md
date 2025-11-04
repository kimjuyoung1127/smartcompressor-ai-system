# 🚀 SignalCraft 개발 현황 종합 보고서: Phase 1 (인증 시스템 개편) 완료

| **문서 목적** | **Phase 1 (인증 시스템 개편)의 디버깅, 해결, 구현 전 과정을 기록하고, Phase 2 계획을 수립합니다.** |
| --- | --- |
| **작업 기간** | 2025-11-04 (기준) |
| **작성자** | 김주영 (개발 담당) |
| **상태** | ✅ **Phase 1 완료 (배포 및 테스트 필요)** |

## 1. 🎯 최종 요약 (Executive Summary)

**Phase 1: 인증 시스템 개편** 작업을 **100% 완료**했습니다.

이 작업으로 프로젝트의 가장 큰 문제점이었던 **SQLite 의존성**을 **PostgreSQL로 완전히 전환**했으며, **Node.js와 Flask에 중복 구현**되었던 인증 시스템을 **Node.js 기반의 '단일 인증 시스템'**으로 통합했습니다.

또한, **'역할 기반 접근 제어(RBAC)'** 미들웨어를 신규 구현하여, "관리자", "라벨러" 등 사용자 등급에 따른 보안 접근 제어의 기반을 완성했습니다.

| **Before (Phase 1 이전)** | **After (Phase 1 완료)** |
| --- | --- |
| ❌ SQLite 세션 저장소 (느리고 확장 불가) | ✅ **PostgreSQL 통합 세션 관리** (표준 테이블) |
| ❌ Flask와 Node.js 인증 기능 중복 | ✅ **Node.js 단일 인증 시스템** |
| ❌ RBAC (역할 기반) 미구현 | ✅ **RBAC 미들웨어 구현** (`requireRole`) |
| ❌ 라벨링 툴 접근 제어 없음 | ✅ **역할 기반 라벨링 API** (`labelingRoutes.js`) |
| ❌ `experts` / `users` 테이블 분리 | ✅ **`users` 테이블로 통합** (`labels.labeler_user_id` 적용) |

## 2. 🐛 디버깅 및 문제 해결 과정 (The Debugging Journey)

Phase 1을 구현하기 전, 로컬 개발 환경을 EC2 서버의 PostgreSQL에 연결하는 과정에서 3가지 치명적인 장애물에 부딪혔으며, 이를 모두 해결했습니다.

### 문제 1: 로컬 PC → EC2 DB 연결 실패 (`Connection Timed Out`)

- **원인:** 로컬 PC(`node server.js`)에서 EC2의 공인 IP(`3.39.124.0`)로 직접 접속을 시도했으나, AWS 보안 그룹 방화벽과 PostgreSQL 설정(`pg_hba.conf`)이 외부 접속을 차단함.
- **해결:** **SSH 터널링(Port Forwarding)** 방식을 도입하여, EC2의 DB 포트를 인터넷에 노출하지 않고 안전하게 로컬 PC와 연결했습니다.
    
    ```
    # [터미널 1] SSH 터널 개방 (가장 안전한 방법)
    ssh -i "signalcraft.pem" -N -L 5433:localhost:5432 ubuntu@3.39.124.0
    
    # [로컬 .env] .env 파일을 터널에 맞게 수정
    DB_HOST=localhost
    DB_PORT=5433
    
    ```
    

### 문제 2: DB 초기화 오류 1 (`relation "users" does not exist`)

- **원인:** 연결 성공 후, `database_service.js`의 `createTables()` 함수가 테이블 생성 순서를 무시하고 `labels` 테이블을 `users` 테이블보다 먼저 생성하려 시도함.
- **해결:** `database_service.js`의 `createTables()` 함수 내 코드 순서를 **의존성(Foreign Key)에 맞게** 재배치했습니다. (`users` → `stores` → `devices` → `labels` 순)

### 문제 3: DB 초기화 오류 2 (`relation "users" already exists`)

- **원인:** `createTables()` 함수가 EC2 DB에 **이미 존재하는 테이블**을 중복 생성하려 시도함.
- **해결:** `init()` 함수 로직을 **"스마트 초기화"** 방식으로 변경했습니다. 서버 시작 시, `users` 테이블이 존재하는지 **먼저 확인(`SELECT COUNT(*)`)**하고, **테이블이 이미 존재하면 `createTables()` 함수를 건너뛰도록** 수정하여 에러 로그를 완벽하게 제거했습니다.

## 3. 🛠️ Phase 1: 구현 완료 상세 내역

`db_migration_report.md`의 계획에 따라, 인증 시스템 개편을 위해 다음과 같은 코드를 신규 생성 및 수정했습니다.

### 1. RBAC(역할 기반 접근 제어) 미들웨어

- **신규 생성:** `server/middleware/rbac.js`
- **기능:** `requireRole(['labeler', 'admin'])`, `requireAdmin()` 등 특정 역할을 가진 사용자만 API에 접근할 수 있도록 강제하는 보안 검문소를 구현했습니다.

### 2. PostgreSQL 완전 전환 (SQLite 제거)

- **수정:** `server/routes/authRoutes.js`, `server/app.js`
- **내용:** 기존 `SQLiteDatabaseService` 의존성을 **완전히 제거**하고, `database_service.js` (PostgreSQL Pool)을 사용하도록 모든 인증 로직(회원가입, 로그인)을 수정했습니다.

### 3. PostgreSQL 기반 세션 관리

- **수정:** `services/database_service.js`
- **내용:** `connect-pg-simple` 라이브러리와 100% 호환되는 **표준 세션 테이블(`sessions`)** 스키마를 적용했습니다. `createSession`, `getSession` 등 세션 관리 메서드를 추가하여 Node.js가 세션을 PostgreSQL에 저장하도록 변경했습니다.

### 4. Flask 인증 기능 비활성화

- **수정:** `app.py` (Python 서버)
- **내용:** `enhanced_auth_bp` (Flask 인증 라우트)를 주석 처리하여, **인증 창구를 Node.js로 단일화**했습니다.

### 5. RBAC 기반 라벨링 API

- **신규 생성:** `server/routes/labelingRoutes.js`
- **내용:** 라벨링 툴(`labeling/interface`)에 접근할 때 `requireLabeler()` 미들웨어를 통과하도록 하여 **보안을 적용**했습니다.
- **핵심 개선:** `save-label` API가 하드코딩된 `'default_expert'` 대신, **로그인한 사용자의 ID(`req.session.user.id`)**를 `labeler_user_id`에 저장하도록 수정하여 라벨 작업자 추적이 가능해졌습니다.

## 4. 📁 생성/수정된 파일 목록

| **파일 경로** | **상태** | **목적** |
| --- | --- | --- |
| `server/middleware/rbac.js` | **신규** | 역할 기반 접근 제어(RBAC) 미들웨어 |
| `server/routes/labelingRoutes.js` | **신규** | 보안이 적용된 라벨링 시스템 API |
| `server/routes/authRoutes.js` | **수정** | SQLite → PostgreSQL 인증 로직 완전 전환 |
| `server/app.js` | **수정** | SQLite 의존성 제거, `labelingRoutes` 등록 |
| `services/database_service.js` | **수정** | "스마트 초기화" 로직 적용, 세션 관리 메서드 추가 |
| `app.py` | **수정** | Flask 인증 기능 비활성화 (주석 처리) |

## 5. 🚀 다음 단계: Phase 2 (스펙트로그램 통합)

Phase 1이 성공적으로 완료됨에 따라, AI 모델 성능 향상을 위한 **Phase 2** 개발에 즉시 착수합니다.

1. **스펙트로그램 UI 개발:**
    - `static/audio_spectrogram_labeling.html` 파일을 신규 생성합니다.
    - 기존 라벨링 툴(`high_quality_labeling_tool.html`)을 기반으로, **오디오 플레이어**와 **스펙트로그램 이미지/캔버스**를 한 화면에서 동시에 볼 수 있도록 UI를 통합합니다.
2. **스펙트로그램 생성 API (Flask):**
    - Python 서버(`routes/ai_routes.py` 등)에 `/api/generate-spectrogram` 엔드포인트를 추가합니다.
    - `librosa` 라이브러리를 사용하여, 업로드된 오디오 파일로부터 스펙트로그램 이미지를 생성하고 저장한 뒤, 이미지 URL을 반환합니다.
3. **프론트엔드 연동:**
    - `static/js/audio_spectrogram_labeling.js` 파일을 신규 생성합니다.
    - 사용자가 오디오 파일을 선택하면, 이 API를 호출하여 스펙트로그램 이미지를 받아와 화면에 표시하는 로직을 구현합니다.

## 6. (부록) SignalCraft 로컬 개발 환경 설정 가이드

앞으로 모든 개발자는 EC2 DB에 직접 접속하는 대신, **반드시 SSH 터널링을 사용**하여 안전하게 로컬 개발을 진행합니다.

**1. SSH 터널 실행 (터미널 1)**

- 새 PowerShell(CMD) 창을 열고, EC2 서버와 '비밀 통로'를 개방합니다. (이 창은 끄지 않습니다)
    
    ```
    ssh -i "C:\Users\gmdqn\pem\signalcraft.pem" -N -L 5433:localhost:5432 ubuntu@3.39.124.0
    
    ```
    

**2. `.env` 파일 설정 (프로젝트 폴더)**

- 프로젝트 루트의 `.env` 파일이 아래와 같이 **로컬 터널**을 바라보는지 확인합니다.
    
    ```
    DB_HOST=localhost
    DB_PORT=5433
    DB_NAME=smartcompressor_ai
    DB_USER=postgres
    DB_PASSWORD=signalcraft6898
    
    ```
    

**3. 서버 실행 (터미널 2)**

- **새로운** 프로젝트 터미널 창을 열고, Node.js 서버를 실행합니다.
    
    ```
    cd C:\Users\gmdqn\signalcraft
    node server.js
    
    ```
    
- **예상 결과:** `Connection Timeout`이나 `duplicate key` 오류 없이, `🗄️ 데이터베이스 테이블이 이미 존재합니다` 메시지와 함께 서버가 깨끗하게 실행됩니다.