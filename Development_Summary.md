# SignalCraft 개발 정리 문서

## 1. 인증 시스템 개선

### 1.1 사용자 역할 변경
- 데이터베이스에서 사용자 juyoungkim의 역할을 'user'에서 'admin'으로 성공적으로 변경
- 관리자 권한을 가진 사용자로 업데이트 완료

### 1.2 로그인/로그아웃 기능 개선
- 로그인 시 상세 콘솔 로깅 추가
- 로그아웃 기능 강화 및 UI 업데이트 개선
- 헤더에 로그인/로그아웃 상태 표시 기능 구현
  - 로그인 상태: "로그아웃" 링크 표시
  - 비로그인 상태: "로그인" 링크 표시

### 1.3 폼 제출 이벤트 리스너 구현
- register-modal.html에 회원가입 폼 제출 이벤트 리스너 추가
- login-modal.html에 로그인 폼 제출 이벤트 리스너 추가
- 입력값 검증 및 오류 처리 로직 구현

## 2. 관리자 기능 구현

### 2.1 관리자 전용 사용자 관리 API
- `/api/admin-users` 엔드포인트 구현
- 사용자 목록 조회 기능 (GET /users)
- 사용자 역할 변경 기능 (PATCH /users/:userId/role)
- 사용자 상태 변경 기능 (PATCH /users/:userId/status)
- 사용자 상세 정보 조회 기능 (GET /users/:userId)

### 2.2 보안 강화
- RBAC (역할 기반 접근 제어) 미들웨어 적용
- 관리자 전용 기능에 requireAdmin 미들웨어 적용
- 적절한 오류 처리 및 권한 검증 로직 구현

### 2.3 관리자 초대 시스템
- `/api/admin-invites` 엔드포인트 구현
- 관리자 초대 링크 생성 기능 (POST /invite-admin)
- 초대 기반 관리자 등록 기능 (POST /register-admin)
- 초대 링크 관리 및 추적 기능 (GET /invites)

### 2.4 관리자 전용 사용자 생성
- 즉시 계정 생성 기능 구현 (POST /create-user)
- 초대 없이도 관리자가 사용자 생성 가능

## 3. 세션 관리 개선

### 3.1 세션 데이터 동기화
- `getSession` 메서드 수정
- 세션 데이터를 사용자 데이터베이스와 실시간으로 동기화
- 사용자 역할 변경 시 기존 세션에도 최신 정보 반영

### 3.2 데이터베이스 스키마 수정
- `sessions` 테이블 생성 로직 추가
- 데이터베이스 초기화 시 세션 테이블 자동 생성
- 세션 만료 관리 및 인덱스 설정

## 4. 관리자 대시보드

### 4.1 대시보드 구현
- `/admin-panel` 경로에 관리자 대시보드 배포
- 사용자 관리 인터페이스 구현
- 대시보드 통계 표시 (총 사용자 수, 활성 사용자, 관리자 수 등)

### 4.2 기능 요약
- 사용자 목록 조회 및 검색
- 사용자 역할 변경 (admin, user, labeler, owner)
- 계정 활성/비활성화 기능
- 관리자 초대 생성 및 관리
- 실시간 통계 대시보드

## 5. 콘솔 로깅 개선

### 5.1 디버깅 로깅 추가
- 로그인/로그아웃 흐름에 상세 콘솔 로깅 추가
- 관리자 대시보드 API 호출에 상세 콘솔 로깅 추가
- 오류 발생 시 상세 정보 출력

### 5.2 오류 처리 개선
- 401 인증 오류 발생 시 적절한 리디렉션 처리
- 403 권한 오류에 대한 사용자 피드백 제공
- 네트워크 오류 및 예외 상황 처리

## 6. 라우팅 구조

### 6.1 관리자 경로
- `/admin-panel`: 관리자 대시보드 (admin 권한 필요)
- `/api/admin-users/*`: 관리자 사용자 관리 API (admin 권한 필요)
- `/api/admin-invites/*`: 관리자 초대 시스템 API (admin 권한 필요)

## 7. 보안 고려사항

### 7.1 권한 검증
- 모든 관리자 기능에 RBAC 미들웨어 적용
- 역할 기반 접근 제어 철저히 구현
- 세션 데이터의 무결성 보장

### 7.2 입력 검증
- 모든 API 엔드포인트에 입력값 검증 추가
- 비정상 요청에 대한 오류 처리
- 보안 취약점 방지

## 8. 기술 스택

### 8.1 백엔드
- Node.js / Express.js
- PostgreSQL 데이터베이스
- bcrypt 암호화
- RBAC 기반 권한 관리

### 8.2 프론트엔드
- HTML5 / CSS3 / JavaScript
- Bootstrap 5 UI 프레임워크
- 모듈 기반 JavaScript 아키텍처
- RESTful API 통신

## 9. 버그 수정

### 9.1 관리자 대시보드 401 오류 수정
- **문제:** 관리자 대시보드에서 사용자 목록 조회 API (`/api/admin-users/users`) 호출 시 401 Unauthorized 오류 발생
- **원인:** `adminUserRoutes.js` 에서 `requireAdmin` 미들웨어 이전에 `authenticateSession` 미들웨어가 없어 사용자 세션 정보(`req.user`)가 설정되지 않음
- **해결:**
    - `server/middleware/auth.js` 파일을 생성하여 `authenticateSession` 미들웨어를 분리하고 모듈화
    - `server/routes/authRoutes.js` 에서 `authenticateSession` 미들웨어를 새로 만든 모듈에서 가져오도록 수정
    - `server/routes/adminUserRoutes.js` 의 모든 라우트에 `authenticateSession` 미들웨어를 추가하여, `requireAdmin` 미들웨어가 실행되기 전에 사용자 세션이 먼저 검증되도록 수정

이 문서는 SignalCraft의 인증 시스템 및 관리자 기능 개선 작업을 정리한 것입니다. 모든 기능은 보안과 사용자 경험을 고려하여 설계 및 구현되었습니다.