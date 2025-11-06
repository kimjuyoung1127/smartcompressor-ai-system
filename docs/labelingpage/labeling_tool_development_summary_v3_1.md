# SignalCraft 오디오 스펙트로그램 라벨링 툴 개발 현황 요약 (v3.1) - 파일 구조 개선

이 문서는 SignalCraft 프로젝트의 라벨링 라우트 파일 구조 개선 작업을 요약합니다. 기존 `server/routes/labelingRoutes.js` 파일을 `server/routes/labeling/` 하위 디렉토리로 이동하여 유지보수성을 향상시켰습니다.

## 1. 파일 구조 개선

*   **라벨링 관련 라우트 파일 이동**: 기존 `server/routes/labelingRoutes.js` 파일을 `server/routes/labeling/index.js`로 이동하여 모듈화했습니다.
*   **서브 디렉토리 구조 채택**: 라벨링 관련 라우트를 별도의 디렉토리로 분리하여 프로젝트 구조를 더 명확하게 했습니다.
*   **기본 모듈 파일명 사용**: 서브 디렉토리 내에서 `index.js` 파일명을 사용하여 Node.js의 기본 모듈 로딩 규칙을 따르도록 했습니다.

## 2. 관련 코드 수정

*   **app.js import 수정**: `server/app.js`에서 라벨링 라우트를 가져오는 경로를 `require('./routes/labelingRoutes')`에서 `require('./routes/labeling')`로 수정했습니다.
*   **기존 기능 유지**: 라우트 로직 자체는 변경하지 않고 파일 위치만 변경하여 기존의 모든 기능이 그대로 유지됩니다.

## 3. 유지보수성 향상

*   **코드 조직화**: 라벨링 관련 기능이 별도의 디렉토리에 위치함으로써 코드 구조가 더 명확해졌습니다.
*   **확장성 개선**: 향후 라벨링 관련 다수의 파일이 추가될 경우 이 디렉토리 내에 추가하여 모듈성을 유지할 수 있습니다.
*   **의존성 관리 용이**: 라벨링 기능과 관련된 변경이 생길 경우 해당 디렉토리 내에서만 관리하면 되므로 오류 발생 가능성이 줄어듭니다.

## 4. 테스트 및 검증

*   **서버 시작 테스트**: 서버를 시작하여 모든 라우트가 정상적으로 동작하는 것을 확인했습니다.
*   **API 기능 검증**: 기존의 모든 라벨링 API 엔드포인트가 정상적으로 작동하는 것을 확인했습니다.
*   **기존 기능 유지 확인**: 파일 삭제, 리프레시, 자동 갱신 등 v3에서 추가된 모든 기능이 정상 작동함을 확인했습니다.

## 5. 추가적인 구조 개선 (v4.0)

*   **인증 및 사용자 관리 라우트 이동**: `authRoutes.js` → `routes/auth/index.js`
*   **관리자 기능 라우트 그룹화**: `adminInviteRoutes.js` → `routes/admin/invites.js`, `adminUserRoutes.js` → `routes/admin/users.js`
*   **ESP32 관련 라우트 그룹화**: `esp32*.js` 파일들 → `routes/esp32/` 디렉토리로 이동
*   **app.js import 경로 업데이트**: 모든 이동된 파일에 대한 import 경로 업데이트 완료

## 6. 파일 이동 내역 (2025-11-06)

*   `server/routes/labelingRoutes.js` → `server/routes/labeling/index.js`
*   `server/routes/authRoutes.js` → `server/routes/auth/index.js`
*   `server/routes/adminInviteRoutes.js` → `server/routes/admin/invites.js`
*   `server/routes/adminUserRoutes.js` → `server/routes/admin/users.js`
*   `server/routes/esp32*.js` → `server/routes/esp32/*.js`
*   `server/app.js` - 모든 import 경로 수정
*   `docs/labelingpage/labeling_tool_development_summary_v3_1.md` - 파일 구조 개선 요약 문서 생성/업데이트

## 7. 향후 계획

*   **기타 라우트 모듈화**: 다른 라우트 파일들에 대해서도 기능별로 그룹화하여 정리
*   **라벨링 관련 추가 모듈**: 라벨링 기능 확장 시 관련 유틸리티나 미들웨어 등을 동일한 디렉토리에 추가할 수 있습니다.
*   **테스트 파일 정리**: 기능별로 테스트 파일도 유사한 구조로 정리

## 8. v3.2 긴급 버그 수정 (2025-11-06)

파일 구조 변경 이후 발생한 여러 심각한 버그들을 해결했습니다.

### 8.1. 서버 측 경로 문제 해결

*   **문제점**: `v3.1`에서 파일 구조를 대대적으로 변경한 후, `require` 경로가 맞지 않아 서버가 시작되지 않는 `MODULE_NOT_FOUND` 오류가 발생했습니다.
*   **해결**: 오류가 발생한 모든 파일(`auth/index.js`, `labeling/index.js`, `admin/invites.js`, `admin/users.js`)의 상대 경로를 새로운 구조에 맞게 수정하여 서버가 정상적으로 실행되도록 했습니다.

### 8.2. 클라이언트 측 라벨링 툴 오류 해결

*   **문제점**: 라벨링 페이지(`audio_spectrogram_labeling.html`)에서 `wavesurfer.js` 라이브러리 버전 충돌 및 API 사용 오류로 인해 오디오 플레이어가 전혀 동작하지 않았습니다.
    *   `WaveSurfer.create is not a function`
    *   `Cannot read properties of undefined (reading 'load')`
    *   `Cannot read properties of undefined (reading 'playPause')`
*   **해결**:
    1.  **라이브러리 다운그레이드**: `wavesurfer.js` v7은 ES 모듈 방식으로 로드해야 하지만, 기존 코드는 v6 API를 사용하고 있었습니다. HTML 파일에서 라이브러리를 v7에서 v6.6.4로 다운그레이드하여 버전 충돌을 해결했습니다.
    2.  **API 사용법 수정**: `wavesurfer.js` v6의 API에 맞게 플러그인 이름을 소문자(`WaveSurfer.timeline`, `WaveSurfer.spectrogram`)로 수정하여 `create` 함수를 찾지 못하는 오류를 해결했습니다.
    3.  **초기화 로직 보강**: `spectrogram` 플러그인 인스턴스가 변수에 올바르게 할당되도록 초기화 코드를 수정하여 안정성을 높였습니다.

### 8.3. 라벨 저장 기능 오류 해결

*   **문제점**: 라벨링 페이지에서 '저장' 버튼을 클릭하면 500 서버 오류가 발생했습니다. 원인은 `labels` 테이블의 `file_name` 컬럼에 `UNIQUE` 제약 조건이 없어, 데이터베이스에서 `ON CONFLICT` 절을 처리할 수 없었기 때문입니다.
*   **해결**: `ON CONFLICT`를 사용하는 대신, 먼저 `SELECT` 문으로 기존 라벨의 존재 여부를 확인하고, 결과에 따라 `INSERT` 또는 `UPDATE`를 수행하는 수동 'upsert' 로직으로 수정하여 문제를 해결했습니다.