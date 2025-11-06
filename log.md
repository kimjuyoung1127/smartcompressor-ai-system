pwa와관련된 파일들을 나열해줘
Fast
View as codemap
Answer
귀하의 프로젝트에서 PWA(Progressive Web App)와 관련된 파일들은 다음과 같습니다:

핵심 PWA 파일
1. Manifest 파일
static/manifest.json - PWA 설정 파일로, 앱 이름, 아이콘, 테마 색상, 시작 URL 등을 정의합니다 manifest.json:1-10
2. Service Worker
static/js/sw.js - PWA의 핵심 기능인 오프라인 캐싱, 백그라운드 동기화, 푸시 알림을 처리하는 Service Worker입니다 sw.js:1-6
3. 모바일 앱 JavaScript
static/js/mobile_app.js - PWA 초기화, Service Worker 등록, 푸시 알림 권한 요청 등을 처리합니다 mobile_app.js:89-112
4. HTML 템플릿
templates/mobile_app.html - PWA 메타 태그, manifest 링크, Service Worker 등록 스크립트가 포함된 메인 HTML 파일입니다 mobile_app.html:8-17
백엔드 API 라우트
5. 모바일 앱 라우트
routes/mobile_app_routes.py - PWA 설치, 오프라인 동기화 등의 API 엔드포인트를 제공합니다 mobile_app_routes.py:23-49
테스트 파일
6. 모바일 앱 시스템 테스트
test_mobile_app_system.py - PWA 설치, 오프라인 동기화 등의 기능을 테스트합니다 test_mobile_app_system.py:37-64
관리자 대시보드
7. 관리자 대시보드 HTML
admin/templates/admin_dashboard.html - PWA 설치 버튼과 모바일 앱 링크가 포함되어 있습니다 admin_dashboard.html:529-551
아이콘 파일 (manifest.json에서 참조)
/static/icons/icon-72x72.png ~ /static/icons/icon-512x512.png - 다양한 크기의 PWA 아이콘들 manifest.json:14-62
Notes
이 프로젝트의 PWA는 Tesla App과 Starbucks App을 벤치마킹하여 구현되었습니다 sw.js:1 . Service Worker는 캐시 우선(cache-first), 네트워크 우선(network-first) 등의 전략을 사용하여 오프라인 기능을 제공하며 sw.js:8-13 , 백그라운드 동기화와 푸시 알림도 지원합니다 mobile_app.js:96-99 .