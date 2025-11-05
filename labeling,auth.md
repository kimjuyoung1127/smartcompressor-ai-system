물론입니다! 아래는 요청하신 내용을 바탕으로 정리한 **SignalCraft 개발 현황 종합 보고서 (Phase 1 완료)**의 노션용 보고서입니다. 노션에 바로 복사해도 깔끔하게 보이도록 구성했습니다.

---

# 🚀 SignalCraft 개발 현황 종합 보고서  
**Phase 1: 인증 시스템 개편 완료**

**📅 작업 기간**: 2025-11-04 기준  
**👨‍💻 작성자**: 김주영 (개발 담당)  
**📌 상태**: ✅ Phase 1 완료

---

## 1. 🎯 최종 요약 (Executive Summary)

**Phase 1: 인증 시스템 개편 작업을 100% 완료했습니다.**

- **SQLite → PostgreSQL 전환**  
- **Flask + Node.js 중복 인증 → Node.js 단일화**  
- **RBAC(역할 기반 접근 제어) 미들웨어 신규 구현**

| Before (Phase 1 이전) | After (Phase 1 완료) |
|-----------------------|----------------------|
| ❌ SQLite 세션 저장소 (느리고 확장 불가) | ✅ PostgreSQL 통합 세션 관리 (표준 테이블) |
| ❌ Flask와 Node.js 인증 기능 중복 | ✅ Node.js 단일 인증 시스템 |
| ❌ RBAC 미구현 | ✅ RBAC 미들웨어 구현 (`requireRole`) |
| ❌ experts / users 테이블 분리 | ✅ users 테이블로 통합 (`labels.labeler_user_id`) |
| ❌ 라벨링 툴 접근 제어 없음 | ✅ 역할 기반 라벨링 API (`labelingRoutes.js`) |

---

## 2. 🐛 디버깅 및 문제 해결 과정

### 🔧 문제 1: 로컬 → EC2 DB 연결 실패 (Connection Timed Out)
- **원인**: AWS 보안 그룹 + `pg_hba.conf` 외부 접속 차단  
- **해결**: SSH 터널링(Port Forwarding) 방식 도입

### 🔧 문제 2: DB 초기화 오류 1 (`relation "users" does not exist`)
- **원인**: FK 의존성 무시한 테이블 생성 순서  
- **해결**: `createTables()` 순서 재정렬 (users → stores → devices → labels)

### 🔧 문제 3: DB 초기화 오류 2 (`relation "users" already exists`)
- **원인**: 이미 존재하는 테이블 중복 생성 시도  
- **해결**: `init()` 함수에 스마트 초기화 로직 적용 (`SELECT COUNT(*)` 선 확인)

---

## 3. 🛠️ Phase 1: 구현 완료 상세 내역

### ✅ RBAC 미들웨어
- **신규 생성**: `server/middleware/rbac.js`  
- **기능**: `requireRole(['labeler', 'admin'])`, `requireAdmin()`, `requireLabeler()`

### ✅ PostgreSQL 완전 전환
- **수정**: `authRoutes.js`, `app.js`  
- **내용**: SQLite 의존성 제거, PostgreSQL Pool 기반 인증 로직 적용

### ✅ 세션 관리 개선
- **수정**: `database_service.js`  
- **내용**: `connect-pg-simple` 호환 세션 테이블 및 메서드 구현

### ✅ Flask 인증 기능 비활성화
- **수정**: `app.py`  
- **내용**: `enhanced_auth_bp` 주석 처리 → Node.js 단일 인증 창구

### ✅ 라벨링 API 보안 강화
- **신규 생성**: `labelingRoutes.js`  
- **핵심**: `requireLabeler()` 미들웨어 적용, `labeler_user_id`에 로그인 사용자 ID 저장

### ✅ 관리자 기능 및 프론트엔드 연동
- **신규 생성**: `adminUserRoutes.js`  
- **수정**: `auth-manager.js`  
- **내용**: 로그인 후 `user.role`에 따라 자동 리디렉션

---

## 4. 🚀 다음 단계: Phase 2 (AI 라벨링 툴 UI/UX 고도화)

### 🎯 목표
- **단순 뷰어 → 전문가용 생산성 도구로 진화**
- **라벨링 정확도, 속도, 피로도 개선**

---

### 4.1. 기술 스택 재정의

- **wavesurfer.js**: 브라우저에서 스펙트로그램 직접 생성 (서버 부하 0, 완전 동기화)  
- **Annotorious**: 스펙트로그램 위 2D 바운딩 박스 라벨링 구현

---

### 4.2. UI/UX 개선 (우선순위: 최우선)

- ⌨️ **키보드 단축키 도입**  
  - `Space`: 재생/일시정지  
  - `← / →`: 0.1초 단위 탐색  
  - `1, 2, 3`: 라벨(Normal, Warning, Critical) 선택  
  - `L`: 선택 영역 반복 재생

- 💾 **자동 저장 & 낙관적 UI**  
  - 3초마다 `localStorage`에 임시 저장  
  - 저장 버튼 클릭 시 즉시 "저장 완료" 표시 후 API 호출

- ⚡ **성능 최적화 (프리페치)**  
  - 다음 오디오 파일 및 `peaks.json` 미리 로드

- 🎯 **정확도 향상 (Snapping & Guides)**  
  - 시간축 그리드에 스냅  
  - 마우스 위치 기준 십자선 표시

---

### 4.3. 백엔드 지원 (Flask)

| API | 상태 | 설명 |
|-----|------|------|
| `/api/generate-spectrogram` | ❌ 폐기 | 프론트엔드에서 직접 생성 |
| `/api/generate-peaks` | ✅ 신규 | `audiowaveform` 기반 `peaks.json` 생성 |
| `/api/labeling/save-label` | 🔄 수정 | `metadata`에 2D 박스 및 시간 영역 저장 지원 |

---

## 5. 📎 부록: 로컬 개발 환경 설정 가이드

### 1️⃣ SSH 터널 실행 (터미널 1)
```bash
ssh -i "C:\Users\gmdqn\pem\signalcraft.pem" -N -L 5433:localhost:5432 ubuntu@3.39.124.0
```

### 2️⃣ .env 파일 설정
```
DB_HOST=localhost
DB_PORT=5433
DB_NAME=smartcompressor_ai
DB_USER=postgres
DB_PASSWORD=signalcraft6898
```

### 3️⃣ 서버 실행 (터미널 2)
```bash
cd C:\Users\gmdqn\signalcraft
node server.js
```

> ✅ 예상 결과: `🗄️ 데이터베이스 테이블이 이미 존재합니다` 메시지와 함께 서버 정상 실행

---

필요하시면 Phase 2용 상세 개발 계획서나 UI 프로토타입 문서도 함께 정리해드릴 수 있어요. 계속 이어서 도와드릴까요?
