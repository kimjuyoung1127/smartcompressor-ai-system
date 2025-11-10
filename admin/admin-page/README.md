# SignalCraft 관리자 페이지

## 개요

SignalCraft 프로젝트의 관리자 대시보드입니다. 기존의 단일 페이지 애플리케이션을 모듈화하여 코드의 재사용성과 유지보수성을 향상시켰습니다.

## 프로젝트 구조

```
admin-page/
├── index.html                 # 메인 HTML 파일
├── css/
│   └── admin-page.css         # 관리자 페이지 전용 스타일
├── js/
│   ├── main.js                # 앱 초기화 및 전역 관리
│   ├── admin-sidebar.js       # 사이드바 및 섹션 로딩 처리
│   ├── admin-dashboard.js     # 대시보드 기능
│   ├── user-management.js     # 사용자 관리 기능
│   ├── invite-management.js   # 초대 관리 기능
│   └── system-settings.js     # 시스템 설정 기능
├── components/
│   ├── sidebar.html           # 사이드바 UI 컴포넌트
│   ├── dashboard.html         # 대시보드 UI 컴포넌트
│   ├── users.html             # 사용자 관리 UI 컴포넌트
│   ├── invites.html           # 초대 관리 UI 컴포넌트
│   ├── system.html            # 시스템 설정 UI 컴포넌트
│   └── modals.html            # 공용 모달 UI 컴포넌트
└── README.md                  # 본 문서
```

## 동작 방식

1.  **초기 로드**: 사용자가 `index.html`에 접속하면, `main.js`의 `AdminApp` 클래스가 앱을 초기화합니다.
2.  **세션 확인**: `AdminApp`은 `/api/auth/verify` API를 호출하여 사용자가 유효한 관리자인지 확인합니다. 인증 실패 시 로그인 페이지로 리디렉션됩니다.
3.  **컴포넌트 로딩**:
    *   `index.html`은 사이드바(`admin-sidebar`), 메인 콘텐츠(`admin-main-content`), 모달(`modals-container`)을 위한 컨테이너 역할만 합니다.
    *   `admin-sidebar.js`가 `components/sidebar.html`을 비동기적으로 로드하여 사이드바를 구성합니다.
    *   사이드바 메뉴 클릭 시, `admin-sidebar.js`의 `showSection` 함수가 호출되어 요청된 섹션에 맞는 HTML(`dashboard.html`, `users.html` 등)을 `admin-main-content` 영역에 동적으로 삽입합니다.
4.  **기능 실행**: 각 섹션에 맞는 `*.js` 파일(예: `user-management.js`)이 해당 UI와 상호작용하며 필요한 기능을 수행합니다.

## 기술 스택

-   **Frontend**: HTML5, CSS3, JavaScript (ES6+ Modules)
-   **UI Framework**: Bootstrap 5
-   **Icons**: Font Awesome 6
-   **API Communication**: Fetch API

## 사용 방법

1.  웹 브라우저에서 `index.html` 파일에 접근합니다.
2.  사이드바 메뉴를 통해 '대시보드', '사용자 관리' 등 원하는 기능으로 이동할 수 있습니다.
3.  모바일 환경에서는 햄버거 메뉴(`☰`)를 통해 사이드바를 열고 닫을 수 있습니다.

## 주요 기능

-   **대시보드**: 시스템의 주요 통계 정보를 시각적으로 제공합니다.
-   **사용자 관리**: 전체 사용자 목록을 조회하고, 역할을 변경하거나 계정을 관리합니다.
-   **초대 관리**: 신규 관리자를 초대하기 위한 초대 링크를 생성하고 관리합니다.
-   **시스템 설정**: 시스템의 주요 설정을 변경합니다. (일부 기능은 준비 중)