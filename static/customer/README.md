# 🎯 Customer Dashboard

SignalCraft 고객 대시보드 - 프리미엄 사용자 전용 모니터링 및 관리 시스템

## 📋 개요

이 디렉토리는 **admin** 및 **premium_user** 역할을 가진 사용자만 접근할 수 있는 고급 대시보드를 포함합니다.

## 🔐 접근 권한

- ✅ **admin**: 전체 접근 가능
- ✅ **premium_user**: 전체 접근 가능 (예정)
- ❌ **user**: 접근 불가 → 업그레이드 안내 페이지로 리다이렉트

## 📂 디렉토리 구조

```
customer/
├── index.html                 # 메인 대시보드 페이지
├── upgrade-required.html      # 권한 없을 때 안내 페이지
├── README.md                  # 이 파일
│
├── js/                        # JavaScript 모듈
│   ├── auth.js               # 인증 및 권한 체크
│   ├── api.js                # API 통신 레이어
│   ├── main.js               # 앱 초기화
│   ├── config.js             # 설정
│   ├── router.js             # SPA 라우팅
│   └── utils.js              # 유틸리티 함수
│
├── css/                       # 스타일시트
│   ├── main.css              # 메인 스타일
│   ├── components.css        # 컴포넌트 스타일
│   ├── responsive.css        # 반응형
│   └── permission-denied.css # 권한 거부 스타일
│
└── components/                # UI 컴포넌트 (향후 추가)
```

## 🚀 접근 URL

- 메인 대시보드: `/customer/dashboard`
- 업그레이드 안내: `/customer/upgrade-required`
- 권한 확인: `/customer/check-access`

## 🔧 주요 기능

### 1. 대시보드
- 실시간 디바이스 모니터링
- 센서 데이터 시각화
- 이상 징후 알림

### 2. 디바이스 관리
- 디바이스 목록 조회
- 상세 정보 확인
- 센서 데이터 분석

### 3. 모니터링
- 실시간 센서 데이터
- 트렌드 분석
- 통계 요약

### 4. 이상 징후 관리
- 이상 징후 목록
- 심각도별 필터링
- 해결 처리

### 5. 오디오 분석
- 오디오 파일 업로드
- AI 분석 결과 확인
- 과부하 감지

## 📝 API 엔드포인트

### 페이지
- `GET /customer/dashboard` - 메인 대시보드
- `GET /customer/upgrade-required` - 업그레이드 안내
- `GET /customer/check-access` - 권한 확인

### API
- `GET /api/customer/dashboard/summary` - 대시보드 요약
- `GET /api/customer/devices` - 디바이스 목록
- `GET /api/customer/monitoring/realtime` - 실시간 모니터링
- `GET /api/customer/anomalies` - 이상 징후 목록
- `POST /api/customer/audio/upload` - 오디오 업로드
- `POST /api/customer/sample-data/generate` - 샘플 데이터 생성

## 🔗 관련 문서

- [전체 계획서](../docs/CUSTOMER_DASHBOARD_PLAN.md)
- [데이터베이스 스키마](../docs/Database/realschema.md)

---

**Last Updated**: 2025-11-10
**Version**: 1.0.0
