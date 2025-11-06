# SignalCraft 오디오 스펙트로그램 라벨링 툴 개발 현황 요약 (v2)

이 문서는 SignalCraft 프로젝트의 오디오 스펙트로그램 라벨링 툴에 대한 최근 개발 내용을 요약합니다. UI/UX 개선부터 백엔드 연동, 그리고 동적 인증 처리까지의 과정을 다룹니다.

## 1. UI/UX 개선 및 독립적인 스타일링

*   **새로운 UI 적용**: `log.md`에 포함된 현대적인 3단 레이아웃(대기열, 작업 영역, 도구 패널)의 UI가 `audio_spectrogram_labeling.html`에 적용되었습니다.
*   **독립적인 CSS**: 메인 대시보드의 CSS(`dashboard_v3.css`)로부터 라벨링 툴의 스타일을 분리하여 `static/css/labeling/labeling_tool.css` 파일을 생성했습니다. 이를 통해 라벨링 툴이 화면 전체 너비를 올바르게 사용하며, 다른 페이지의 레이아웃에 영향을 받지 않도록 했습니다.

## 2. 프론트엔드 기능 구현 (`static/js/labeling/audio_spectrogram_labeling.js`)

*   **Wavesurfer.js 및 플러그인 통합**: 오디오 파형, 스펙트로그램, 타임라인 시각화를 위해 `wavesurfer.js` (v7)와 `Spectrogram`, `Timeline`, `Regions` 플러그인이 통합되었습니다.
*   **Annotorious 통합**: 스펙트로그램 위에 2D 바운딩 박스를 그려 라벨링할 수 있는 `Annotorious` 라이브러리가 연동되었습니다.
*   **좌표 변환 로직**: 픽셀 기반의 라벨링 영역을 실제 오디오의 시간(초) 및 주파수(Hz) 범위로 변환하는 로직이 구현되었습니다.
*   **자동 저장 기능**: 작업 중인 라벨링 데이터를 `localStorage`에 임시 저장하여 데이터 손실을 방지합니다.
*   **UI 컨트롤 연동**: 재생/일시정지, 빨리 감기/되감기, 줌 인/아웃, 재생 속도 조절 등 모든 UI 컨트롤이 `wavesurfer.js` 인스턴스와 연동되었습니다.

## 3. Flask 백엔드 API 구축 (`ai/labeling/`)

라벨링 툴의 백엔드 로직은 Python/Flask를 사용하여 `ai/labeling/` 디렉터리 내에 모듈화되어 구현되었습니다.

*   **디렉터리 구조**: `ai/labeling/` 폴더가 생성되었으며, `__init__.py`, `api.py`, `services.py` 파일이 포함됩니다.
*   **Flask Blueprint**: `ai/labeling/api.py`에 `labeling_bp` Blueprint가 정의되었고, `app.py`에 `/api/labeling` URL 접두사로 등록되었습니다.
*   **인증 데코레이터**: `api.py`에 `@require_labeler` 데코레이터가 구현되어, `X-User-ID` 및 `X-User-Role` 헤더를 통해 'labeler' 또는 'admin' 역할의 사용자만 API에 접근할 수 있도록 보호합니다.
*   **API 엔드포인트 (더미 구현)**:
    *   `GET /api/labeling/queue`: 라벨링 대기열 목록을 반환합니다. (현재는 더미 데이터 사용)
    *   `GET /api/labeling/audio/<int:file_id>`: 지정된 ID의 오디오 파일을 제공합니다. (현재는 하드코딩된 파일 경로 사용)
    *   `GET /api/labeling/peaks/<int:file_id>`: 오디오 파일의 파형 데이터(`peaks.json`)를 생성(시뮬레이션)하거나 캐시된 파일을 반환합니다.
    *   `POST /api/labeling/save`: 프론트엔드에서 전송된 라벨링 데이터를 받아 처리합니다. (현재는 콘솔에 출력하는 시뮬레이션 로직)

## 4. 프론트엔드-백엔드 연동 및 동적 인증

*   **API 호출 연동**: `audio_spectrogram_labeling.js`의 `fetchQueue`, `loadAudio`, `saveAndNext` 함수들이 실제 Flask 백엔드 API 엔드포인트를 호출하도록 수정되었습니다.
*   **동적 인증 헤더**: `static/js/auth-manager.js`를 활용하여 로그인된 사용자의 `id`와 `role`을 동적으로 가져와 `X-User-ID` 및 `X-User-Role` HTTP 헤더에 포함하도록 구현되었습니다. 이를 통해 라벨링 툴은 프로젝트의 기존 인증 시스템과 통합되어 사용자 역할에 따른 접근 제어를 따르게 됩니다.

## 5. 다음 단계

*   `ai/labeling/services.py` 내의 더미 데이터 및 시뮬레이션 로직을 실제 PostgreSQL 데이터베이스 쿼리 및 `audiowaveform` 실행 로직으로 교체해야 합니다.
*   `audiowaveform` 도구의 서버 환경 설치 및 경로 설정이 필요합니다.

## 6. 진행 상황 업데이트 (2025-11-05)

*   `ai/labeling/services.py`의 더미 데이터 및 시뮬레이션 로직이 실제 PostgreSQL 데이터베이스 쿼리 및 `audiowaveform` 실행 로직으로 성공적으로 교체됨:
    *   PostgreSQL 데이터베이스 연결 구현 (psycopg2 사용)
    *   `get_audio_queue()` 함수가 `audio_files` 테이블에서 라벨링 대기열을 조회하도록 수정
    *   `get_audio_file_path()` 함수가 데이터베이스에서 오디오 파일 경로를 조회하도록 수정
    *   `generate_or_get_peaks()` 함수가 실제 `audiowaveform` 명령을 실행하도록 수정 (시뮬레이션 제거)
    *   `save_label_data()` 함수가 `labels` 테이블에 라벨링 데이터를 저장하도록 수정
    *   환경 변수 기반 데이터베이스 설정 로드 구현
*   `requirements.txt`에 psycopg2-binary 의존성 추가
*   라벨링 관련 테이블 스키마는 `realschema.md`에 명시된 대로 사용 (audio_files, labels 테이블)

## 7. 파일 업로드 기능 추가 (2025-11-05)

*   `static/labeling/audio_spectrogram_labeling.html` 파일에 오디오 업로드 버튼 추가:
    *   "파일 업로드" 버튼 및 파일 선택 입력 필드 추가
    *   `flex-wrap` CSS 속성 적용으로 버튼 항상 표시되도록 개선
    *   Font Awesome 아이콘 적용으로 시각적 일관성 유지

*   프론트엔드 JavaScript (`static/js/labeling/audio_spectrogram_labeling.js`) 기능 확장:
    *   파일 업로드 이벤트 리스너 및 처리 로직 추가
    *   WaveSurfer.js v7 호환성 개선 (colorMap 제거 및 플러그인 초기화 수정)
    *   Annotorious 라이브러리 초기화 문제 해결
    *   알림 시스템 구현 (업로드 성공/실패 메시지 표시)

*   Node.js 백엔드 (`server/routes/labelingRoutes.js`)에 라벨링 API 엔드포인트 추가:
    *   `/api/labeling/queue` - 라벨링 대기열 조회
    *   `/api/labeling/audio/:fileId` - 오디오 파일 제공
    *   `/api/labeling/peaks/:fileId` - 오디오 피크스 데이터 제공
    *   `/api/labeling/upload` - 오디오 파일 업로드 및 데이터베이스 등록
    *   `/api/labeling/save` - 라벨링 데이터 저장
    *   인증 및 권한 검사 미들웨어 통합

*   업로드된 파일 자동 처리:
    *   파일 업로드 시 자동으로 `data/labeling_ready` 디렉터리에 저장
    *   데이터베이스에 파일 정보 자동 등록 (`audio_files` 테이블)
    *   파일명 규칙 적용 (`labeling_unknown_YYYY-MM-DDTHH-MM-SS-MS.ext`)

*   오류 처리 및 안정성 개선:
    *   `audiowaveform` 미설치 시 대체 처리 로직 구현
    *   WaveSurfer.js 초기화 오류 해결
    *   UI 레이아웃 오류 수정
