# src/ 디렉토리

이 디렉토리는 프로젝트의 모든 소스 코드 파일을 포함합니다. 프로젝트 구조를 더 명확하게 하기 위해 루트 디렉토리에 있던 다양한 JS 소스 파일을 이곳으로 이동했습니다.

## 포함된 파일

- `aiRoutes.js` - AI 관련 라우트 정의
- `esp32FeaturesApi.js`, `esp32FilesApi.js`, `esp32Routes.js`, `esp32Routes_fixed.js` - ESP32 통신 API 및 기능
- `server_app.js`, `server_app_fixed.js` - 서버 애플리케이션 모듈
- `simple_dashboard_server.js`, `simple_labeling_server.js` - 간단한 서버 구현
- `simple_server.js` - 간단한 서버 구현 (루트 디렉토리의 것과 다름)
- `https-server.js`, `https-server-simple.js` - HTTPS 서버 구현
- `integrated_server.js` - 통합 서버
- `data_upload_server.js`, `data_upload_server_fixed.js` - 데이터 업로드 서버
- `create_admin_sqlite.js` - SQLite 관리자 생성 스크립트
- 그 외 여러 서버 및 애플리케이션 소스 파일

## 목적

이 디렉토리는 서버 실행에 직접적으로 필요한 핵심 파일들(app.js, server.js 등)을 제외한 모든 소스 코드를 모아, 프로젝트의 루트 디렉토리를 더 깔끔하게 유지하기 위함입니다.