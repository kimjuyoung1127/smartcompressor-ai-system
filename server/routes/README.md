# SignalCraft 서버 라우트 구조

이 디렉토리는 SignalCraft 애플리케이션의 API 엔드포인트와 웹 라우트를 정의하는 Express 라우터 파일들을 포함하고 있습니다.

## 디렉토리 구조

```
routes/
├── admin/                 # 관리자 기능 관련 라우트
│   ├── invites.js         # 관리자 초대 시스템
│   └── users.js           # 사용자 관리
├── auth/                  # 인증/회원가입 관련 라우트
│   └── index.js           # 로그인, 회원가입, 로그아웃 등
├── esp32/                 # ESP32 IoT 디바이스 통신 라우트
│   ├── dashboard.js       # ESP32 대시보드 API
│   ├── dataManager.js     # ESP32 데이터 관리
│   ├── features.js        # ESP32 기능별 API
│   ├── files.js           # ESP32 파일 관련 API
│   └── index.js           # ESP32 일반 라우트
├── labeling/              # 오디오 라벨링 툴 라우트
│   └── index.js           # 라벨링 큐, 저장, 업로드 등
├── aiRoutes.js            # AI 분석 기능
├── adminRoutes.js         # 관리자 대시보드
├── kakaoRoutes.js         # 카카오 OAuth 인증
├── monitoringRoutes.js    # 실시간 모니터링
├── notificationRoutes.js  # 알림 시스템
├── sensorDataApi.js       # 센서 데이터 API
├── weatherApi.js          # 날씨 API
└── ...
```

## 개별 라우트 설명

### admin/
- `/api/admin-invites`: 관리자 초대 링크 생성 및 관리
- `/api/admin-users`: 사용자 목록 조회 및 권한 관리

### auth/
- `/api/auth`: 회원가입, 로그인, 로그아웃, 세션 확인 등 인증 관련 기능

### esp32/
- `/api/esp32`: ESP32 디바이스와의 통신을 위한 다양한 API

### labeling/
- `/api/labeling`: 오디오 스펙트로그램 라벨링 툴 관련 API (큐, 저장, 업로드 등)

### 기타 주요 라우트
- `/api/ai`: AI 기반 이상 탐지 및 분석
- `/api/monitoring`: 실시간 장비 모니터링
- `/api/notifications`: 알림 및 이벤트 처리
- `/api/sensor`: 센서 데이터 수집
- `/api/weather`: 날씨 정보 API

## 공통 구조

모든 라우트 파일은 Express 라우터를 사용하여 정의되며, 대부분의 API는 인증 미들웨어를 사용합니다. 인증 관련된 미들웨어는 `server/middleware/` 디렉토리에 위치해 있습니다.

## 기술 스택
- Express.js: 웹 프레임워크
- Node.js: 런타임 환경
- PostgreSQL: 인증 및 세션 관리

## 확장성
이 구조는 새로운 기능별로 서브 디렉토리를 생성하여 확장할 수 있도록 설계되었습니다. 예를 들어, 새로운 기능이 필요할 경우 `routes/new-feature/` 디렉토리를 만들고 관련 라우트를 그룹화할 수 있습니다.