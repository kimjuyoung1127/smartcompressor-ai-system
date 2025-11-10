물론이죠! 아래는 SignalCraft Phase 2 개발 계획 보고서를 노션에 정리하기 적합한 형식으로 구성한 버전입니다:

---

# 🚀 SignalCraft Phase 2 개발 계획 보고서 (v2.0 - Hardened)

## 📌 문서 목적
"브라우저 다운" 및 "서버 다운"이라는 치명적 결함을 해결한, **서버 사이드 피크**와 **2D 어노테이션** 기반의 새로운 Phase 2 아키텍처를 정의하고 실행 계획을 수립합니다.

- **상태**: 🟢 계획 수립 완료 (Planning Complete)  
- **작성자**: 김주영 (개발 담당)  
- **선행 조건**: Phase 1 - 인증 시스템 개편 완료 (PostgreSQL 세션, RBAC 미들웨어 구현 완료)

---

## 1️⃣ 개요: 왜 계획을 변경해야 하는가?

기존 Phase 2는 Flask API가 librosa로 스펙트로그램 이미지를 생성해 반환하는 방식이었으나, 다음과 같은 치명적 결함이 발견되었습니다:

### ❌ 실패 1: 서버 다운 (Server Blocking)
- librosa는 CPU를 100% 사용하는 무거운 작업
- 동시 요청 2~3개만으로 Flask 서버 전체가 멈춤

### ❌ 실패 2: 브라우저 다운 (Browser Crash)
- wavesurfer.js의 decodeAudioData 방식은 70MB 오디오에 10GB 메모리를 사용
- 사용자의 브라우저가 다운됨

➡️ 따라서 기존 아키텍처를 폐기하고, 업계 표준인 **서버 사이드 피크 생성(Server-Side Peaks)** 방식으로 재설계합니다.

---

## 2️⃣ 새로운 Phase 2 아키텍처: Server-Side Peaks

### 🧠 핵심 아이디어
"시각화"와 "재생"을 분리하여 서버와 브라우저 다운 문제를 동시에 해결

### 🔧 Backend: 비동기 피크 생성
- 오디오 업로드 시, Flask 서버는 요청을 **비동기 작업 큐(Task Queue)**로 넘김
- Dramatiq 또는 Celery 작업자가 C++ 기반 **bbc/audiowaveform** 도구를 호출
- 수십 KB 크기의 **peaks.json** 파일 생성

### 🎨 Frontend: 경량 렌더링
- wavesurfer.js가 peaks.json만 로드하여 1초 이내 파형 렌더링
- 오디오 원본은 `<audio>` 태그로 스트리밍 재생

### 🧭 UI/UX: 2D 어노테이션
- Annotorious 또는 Konva.js를 통해 **시간-주파수 기반 2D 바운딩 박스** 라벨링 가능
- wavesurfer.js의 스펙트로그램 캔버스 위에 오버레이

---

## 3️⃣ Phase 2: 상세 작업 계획 (Task Breakdown)

### ✅ Task 1: 백엔드 - 비동기 작업 환경 구축 (Python/Flask)
**목표**: 무거운 오디오 처리 작업을 비동기 큐로 분리하여 API 서버 안정성 확보

- [신규 설치] Redis 및 Dramatiq
  ```bash
  pip install dramatiq[redis]
  sudo apt install redis-server
  ```
- [신규 설치] audiowaveform 도구
  ```bash
  sudo apt install audiowaveform
  ```
- [신규 생성] `tasks.py`에서 subprocess로 audiowaveform 호출
- [신규 생성] `/api/labeling/request-audio-processing` API
  - 오디오 파일 ID를 받아 작업 큐에 등록
  - 즉시 '처리 중' 상태 반환

---

### ✅ Task 2: 프론트엔드 - 2D 라벨링 툴 UI/UX 개발 (JS/HTML)
**목표**: Server-Side Peak 기반의 전문가용 2D 어노테이션 툴 개발

- [신규 생성] `static/labeling/audio_spectrogram_labeling.html`
- [라이브러리 도입]
  - wavesurfer.js + Spectrogram, Regions, Timeline 플러그인
  - Annotorious 또는 Konva.js
- [신규 생성] `static/js/labeling/audio_spectrogram_labeling.js`
- [핵심 로직]
  1. `peaks.json` fetch → `wavesurfer.loadPeaks()`로 렌더링
  2. `<audio>` 태그와 wavesurfer.js 연동
  3. Annotorious 오버레이로 2D 박스 라벨링
  4. `<audio>`의 `timeupdate` 이벤트와 Annotorious 이벤트 동기화

---

### ✅ Task 3: API 연동 및 DB 스키마 수정 (Node.js/PostgreSQL)
**목표**: 2D 어노테이션 데이터를 저장할 수 있도록 API 및 DB 수정

- [DB 스키마 수정]
  ```sql
  ALTER TABLE "labels"
      ADD COLUMN IF NOT EXISTS "start_time" FLOAT NOT NULL,
      ADD COLUMN IF NOT EXISTS "end_time" FLOAT NOT NULL,
      ADD COLUMN IF NOT EXISTS "min_freq" FLOAT,
      ADD COLUMN IF NOT EXISTS "max_freq" FLOAT;
  -- 기존 label, confidence 등은 유지
  ```

---
