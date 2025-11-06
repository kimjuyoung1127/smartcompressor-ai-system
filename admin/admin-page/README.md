# SignalCraft 관리자 페이지 모듈화

## 개요
기존 단일 HTML 파일인 `admin-dashboard.html`을 모듈화하여 유지보수성을 향상시켰습니다.

## 구조
```
admin-page/
├── index.html                 # 메인 HTML 파일
├── css/
│   └── admin-page.css         # 분리된 CSS 스타일
├── js/
│   ├── admin-sidebar.js       # 사이드바 관련 JS
│   ├── admin-dashboard.js     # 대시보드 기능 JS
│   ├── user-management.js     # 사용자 관리 JS
│   ├── invite-management.js   # 초대 관리 JS
│   ├── system-settings.js     # 시스템 설정 JS
│   └── main.js               # 메인 앱 초기화 및 공통 기능
├── components/
│   ├── sidebar.html          # 사이드바 컴포넌트
│   ├── dashboard.html        # 대시보드 섹션
│   ├── users.html            # 사용자 관리 섹션
│   ├── invites.html          # 초대 관리 섹션
│   ├── system.html           # 시스템 설정 섹션
│   └── modals.html           # 모든 모달 컴포넌트
└── assets/
    └── images/               # 관련 이미지 파일 (필요시)
```

## 경로 설정
- CSS: `./css/admin-page.css` (상대 경로)
- JS: `./js/*.js` (상대 경로)
- 컴포넌트: JavaScript로 동적 로드
- API 경로: 기존 `/api/*` 경로 그대로 유지
- 정적 파일: 기존 `/static/*` 경로 그대로 유지

## 사용 방법
1. 브라우저에서 `index.html` 파일 열기
2. 사이드바를 통해 다양한 관리 기능에 접근
3. 모바일에서는 햄버거 메뉴를 사용하여 사이드바 토글

## 주요 기능
- 대시보드: 시스템 통계 정보 표시
- 사용자 관리: 사용자 목록, 역할 및 상태 관리
- 초대 관리: 관리자 초대 링크 생성 및 관리
- 시스템 설정: 시스템 관련 설정 (준비 중)

## 기술 스택
- HTML5, CSS3, JavaScript (ES6+)
- Bootstrap 5
- Font Awesome 6
- Fetch API for AJAX requests
